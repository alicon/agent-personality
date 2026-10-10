"""Bounded assistant-only QLoRA training; CPU fixtures test mechanics, not behavior."""
import argparse
from dataclasses import asdict, dataclass
from functools import partial
import hashlib
import importlib.metadata
import json
import math
import os
from pathlib import Path
import re
import signal
import time

from personality_lab.data import collate, digest, encode_episode, load_episodes


@dataclass(frozen=True)
class Recipe:
    model_id: str
    model_revision: str
    data: str
    max_length: int
    max_steps: int
    gradient_accumulation_steps: int
    learning_rate: float
    lora_rank: int
    seed: int
    soft_timeout_seconds: int
    output: str
    quantization: str

    @classmethod
    def load(cls, path):
        recipe = cls(**json.loads(Path(path).read_text()))
        if recipe.model_id not in ("Qwen/Qwen3-14B", "Qwen/Qwen3-0.6B") or not re.fullmatch(r"[0-9a-f]{40}", recipe.model_revision):
            raise ValueError("Supported model and immutable revision required")
        for name, limit in (("max_length", 4096), ("max_steps", 30), ("gradient_accumulation_steps", 16),
                            ("lora_rank", 64), ("soft_timeout_seconds", 6000)):
            value = getattr(recipe, name)
            if type(value) is not int or not 0 < value <= limit:
                raise ValueError(f"Invalid bounded {name}")
        if type(recipe.seed) is not int or not 0 <= recipe.seed < 2**32:
            raise ValueError("Invalid seed")
        if not isinstance(recipe.learning_rate, (int, float)) or not math.isfinite(recipe.learning_rate) or not 0 < recipe.learning_rate <= .001:
            raise ValueError("Invalid learning rate")
        if recipe.quantization != "nf4":
            raise ValueError("GPU smoke recipes require NF4")
        output = Path(recipe.output)
        if output.is_absolute() or ".." in output.parts or output.parts[0] != "artifacts":
            raise ValueError("Output must be inside artifacts/")
        return recipe


def add_adapter(model, rank):
    from peft import LoraConfig, get_peft_model
    return get_peft_model(model, LoraConfig(r=rank, lora_alpha=2*rank, lora_dropout=0,
                           target_modules=["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
                           bias="none", task_type="CAUSAL_LM"))


def environment_manifest():
    import platform
    packages = {}
    for name in ("torch", "transformers", "peft", "accelerate", "bitsandbytes", "huggingface_hub", "tokenizers", "safetensors"):
        try:
            packages[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            packages[name] = None
    return {"python": platform.python_version(), "platform": platform.system(), "packages": packages}


def persist_folder(output, run_id, repo):
    if repo is None:
        return None
    from huggingface_hub import HfApi
    api = HfApi()
    if api.whoami()["name"] != "abelcable" or repo != "abelcable/agent-personality-qwen3-14b" or not api.model_info(repo).private:
        raise ValueError("Expected account and private model destination required")
    commit = api.upload_folder(repo_id=repo, folder_path=str(output), path_in_repo=f"preparation/runs/{run_id}",
                               commit_message=f"Preparation artifact {run_id}")
    return commit.oid


def validate_resume(checkpoint, manifest):
    """Check the old provenance before any output manifest can overwrite it."""
    checkpoint = Path(checkpoint)
    prior = json.loads((checkpoint.parent / "manifest.json").read_text())
    state = json.loads((checkpoint / "trainer_state.json").read_text())
    keys = ("model_id", "model_revision", "lora_rank", "seed", "quantization", "max_length",
            "gradient_accumulation_steps", "learning_rate")
    if type(state["global_step"]) is not int or not 0 < state["global_step"] < manifest["recipe"]["max_steps"]:
        raise ValueError("Checkpoint must precede the requested step limit")
    if (prior["data_sha256"] != manifest["data_sha256"]
            or prior["chat_template_sha256"] != manifest["chat_template_sha256"]
            or prior.get("source") != manifest.get("source")
            or any(prior["recipe"][k] != manifest["recipe"][k] for k in keys)):
        raise ValueError("Resume checkpoint provenance mismatch")
    for name in ("optimizer.pt", "scheduler.pt", "rng_state.pth", "adapter_model.safetensors"):
        if not (checkpoint / name).is_file():
            raise ValueError("Complete optimizer, scheduler, RNG and adapter checkpoint required")
    return state["global_step"]


def frozen_parameter_digest(model):
    """Byte-level parameter check for small smoke models; not a full-state hash."""
    import torch
    result = hashlib.sha256()
    for name, parameter in model.named_parameters():
        if not parameter.requires_grad and "lora_" not in name:
            result.update(name.encode())
            result.update(str((tuple(parameter.shape), parameter.dtype)).encode())
            result.update(parameter.detach().cpu().contiguous().reshape(-1).view(torch.uint8).numpy().tobytes())
    return result.hexdigest()


def inference_logits(model, sample, *, device_type="cuda"):
    """Use identical compute and comparison precision before and after reload."""
    import torch
    model.eval()
    with torch.no_grad(), torch.autocast(device_type=device_type, dtype=torch.bfloat16):
        return model(**sample).logits.detach().float().cpu()


def fit(model, train_rows, validation_rows, tokenizer, recipe, output, *, cpu=False, resume=None,
        upload=None, stop_after_step=None):
    import torch
    from transformers import Trainer, TrainerCallback, TrainingArguments
    started, stop = time.monotonic(), {"requested": False}

    class Checks(TrainerCallback):
        def on_step_end(self, args, state, control, **kwargs):
            if (stop["requested"] or time.monotonic() - started >= recipe.soft_timeout_seconds
                    or (stop_after_step is not None and state.global_step >= stop_after_step)):
                control.should_training_stop = True
                control.should_save = True
            return control

        def on_log(self, args, state, control, logs=None, **kwargs):
            for key in ("loss", "eval_loss", "grad_norm"):
                if logs and key in logs and not math.isfinite(float(logs[key])):
                    raise RuntimeError("Nonfinite training metric")

        def on_save(self, args, state, control, **kwargs):
            if upload:
                upload()

    arguments = TrainingArguments(output_dir=str(output), max_steps=recipe.max_steps, learning_rate=recipe.learning_rate,
        per_device_train_batch_size=1, per_device_eval_batch_size=1,
        gradient_accumulation_steps=recipe.gradient_accumulation_steps, logging_steps=1, save_steps=min(5, recipe.max_steps),
        save_total_limit=2, eval_strategy="no", report_to=[], seed=recipe.seed, data_seed=recipe.seed,
        bf16=not cpu, use_cpu=cpu, gradient_checkpointing=not cpu,
        gradient_checkpointing_kwargs={"use_reentrant": False}, optim="adamw_torch",
        remove_unused_columns=False, dataloader_pin_memory=not cpu, disable_tqdm=True,
        logging_nan_inf_filter=False)
    trainer = Trainer(model=model, args=arguments, train_dataset=train_rows, eval_dataset=validation_rows,
                      data_collator=partial(collate, pad_token_id=tokenizer.pad_token_id), callbacks=[Checks()])
    old_handlers = {}
    for sig in (signal.SIGTERM, signal.SIGINT):
        try:
            old_handlers[sig] = signal.signal(sig, lambda *_: stop.update(requested=True))
        except ValueError:  # Running in a thread, e.g. a local test.
            pass
    try:
        train_result = trainer.train(resume_from_checkpoint=resume)
        trainer.save_model(str(output / "adapter"))
        tokenizer.save_pretrained(output / "adapter")
        evaluation = trainer.evaluate()
        if not math.isfinite(evaluation["eval_loss"]):
            raise RuntimeError("Nonfinite validation loss")
        # Trainer/Accelerate adds a mixed-precision forward wrapper. A newly loaded
        # PeftModel does not have it, so remove it before controlled inference.
        trainer.accelerator.unwrap_model(model, keep_fp32_wrapper=False)
        metrics = {"training": train_result.metrics, "validation": evaluation, "steps": trainer.state.global_step,
                   "optimizer_step_values": sorted({int(state["step"]) for state in trainer.optimizer.state.values()
                                                     if "step" in state}),
                   "elapsed_seconds": time.monotonic() - started, "stopped_early": trainer.state.global_step < recipe.max_steps,
                   "peak_vram_bytes": torch.cuda.max_memory_allocated() if not cpu else 0}
        (output / "metrics.json").write_text(json.dumps(metrics, indent=2))
        return metrics
    finally:
        for sig, handler in old_handlers.items():
            signal.signal(sig, handler)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--recipe", required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--persist-repo")
    parser.add_argument("--resume")
    parser.add_argument("--stop-after-step", type=int)
    parser.add_argument("--verify-frozen-base", action="store_true")
    args = parser.parse_args()
    if not re.fullmatch(r"[a-zA-Z0-9_-]{1,80}", args.run_id):
        parser.error("Simple run ID required")
    recipe = Recipe.load(args.recipe)
    if args.stop_after_step is not None and not 0 < args.stop_after_step < recipe.max_steps:
        parser.error("Stop step must precede the recipe's final step")
    if args.verify_frozen_base and recipe.model_id != "Qwen/Qwen3-0.6B":
        parser.error("Full frozen-parameter hashing is restricted to the tiny model")
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig, set_seed
    from peft import prepare_model_for_kbit_training, PeftModel
    if not torch.cuda.is_available() or not torch.cuda.is_bf16_supported():
        raise RuntimeError("CUDA GPU with bfloat16 support required; do not silently fall back")
    set_seed(recipe.seed)
    rows = load_episodes(recipe.data)
    tokenizer = AutoTokenizer.from_pretrained(recipe.model_id, revision=recipe.model_revision)
    encoded = [(row["split"], encode_episode(row, tokenizer, recipe.max_length)) for row in rows]
    output = Path(recipe.output) / args.run_id
    if output.exists() and not args.resume:
        raise ValueError("Refusing to overwrite an existing run")
    output.mkdir(parents=True, exist_ok=True)
    manifest = {"status": "started", "recipe": asdict(recipe), "data_sha256": digest(rows),
                "chat_template_sha256": hashlib.sha256(tokenizer.chat_template.encode()).hexdigest(),
                "environment": environment_manifest(), "boundary": "local Transformers inputs, not a frontier API",
                "data_review": "agent-authored development fixtures; not calibrated to Abel", "run_id": args.run_id,
                "source": {"bundle_sha256": os.environ.get("PERSONALITY_SOURCE_SHA256"),
                           "git_commit": os.environ.get("PERSONALITY_SOURCE_COMMIT"),
                           "trainer_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}}
    if args.resume:
        manifest["resume_start_step"] = validate_resume(args.resume, manifest)
        manifest["resumed_from"] = str(args.resume)
    (output / "manifest.json").write_text(json.dumps(manifest, indent=2))
    quant = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_quant_type="nf4", bnb_4bit_compute_dtype=torch.bfloat16,
                              bnb_4bit_use_double_quant=True)
    model = AutoModelForCausalLM.from_pretrained(recipe.model_id, revision=recipe.model_revision,
                                               quantization_config=quant, device_map={"": 0}, dtype=torch.bfloat16)
    model.config.use_cache = False
    model = add_adapter(prepare_model_for_kbit_training(model), recipe.lora_rank)
    before = {name: value.detach().cpu().clone() for name, value in model.named_parameters() if value.requires_grad}
    frozen_before = frozen_parameter_digest(model) if args.verify_frozen_base else None
    manifest["trainable_parameters"] = sum(p.numel() for p in model.parameters() if p.requires_grad)
    try:
        metrics = fit(model, [r for s, r in encoded if s == "train"], [r for s, r in encoded if s == "validation"],
                      tokenizer, recipe, output, resume=args.resume,
                      upload=lambda: persist_folder(output, args.run_id, args.persist_repo),
                      stop_after_step=args.stop_after_step)
        if not any(not torch.equal(before[n], p.detach().cpu()) for n, p in model.named_parameters() if n in before):
            raise RuntimeError("Adapter weights did not change")
        manifest["adapter_changed"] = True
        if frozen_before is not None:
            if frozen_before != frozen_parameter_digest(model):
                raise RuntimeError("Frozen base parameters changed")
            manifest["frozen_parameters_unchanged"] = True
        # Reload against the identical frozen base without allocating a second 14B model.
        sample = collate([encoded[0][1]], tokenizer.pad_token_id)
        sample = {k: v.to(model.device) for k, v in sample.items()}
        manifest["inference_check"] = {"autocast": "bfloat16", "comparison_dtype": "float32",
                                       "training_forward_wrapper_removed": not hasattr(model, "_original_forward")}
        trained_logits = inference_logits(model, sample)
        with model.disable_adapter():
            base_logits = inference_logits(model, sample)
        if torch.allclose(trained_logits, base_logits):
            raise RuntimeError("Adapter-on/off produces no detectable difference")
        manifest["adapter_on_off_max_abs_delta"] = float((trained_logits - base_logits).abs().max())
        base = model.unload()
        del base.peft_config
        restored = PeftModel.from_pretrained(base, output / "adapter")
        reloaded_logits = inference_logits(restored, sample)
        manifest["reload_max_abs_delta"] = float((trained_logits - reloaded_logits).abs().max())
        if frozen_before is not None:
            if frozen_before != frozen_parameter_digest(restored):
                raise RuntimeError("Frozen base parameters changed during reload")
            manifest["reload_frozen_parameters_unchanged"] = True
        if not torch.allclose(trained_logits, reloaded_logits, atol=.02, rtol=.02):
            raise RuntimeError("Saved adapter reload mismatch")
        manifest.update(status="completed" if not metrics["stopped_early"] else "stopped_early",
                        adapter_changed=True, reload_checked=True, behavior_evaluated=False)
    except BaseException:
        manifest["status"] = "failed"
        raise
    finally:
        (output / "manifest.json").write_text(json.dumps(manifest, indent=2))
        persist_folder(output, args.run_id, args.persist_repo)


if __name__ == "__main__":
    main()
