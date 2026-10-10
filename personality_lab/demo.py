"""Bounded illustrative model replies; not a personality effectiveness evaluation."""
from contextlib import nullcontext
from dataclasses import asdict
import hashlib
import json
from pathlib import Path
import time

from personality_lab.data import MARKERS, digest
from personality_lab.lab import CONDITIONS, Generation, assemble


def load_cases(path="data/demo-prompts.json"):
    content = json.loads(Path(path).read_text())
    if content.get("origin") != "wholly_invented" or content.get("status") != "development_demo_not_final_evaluation":
        raise ValueError("Only invented development demo cases are supported")
    cases = content["cases"]
    if not 1 <= len(cases) <= 4 or len({case["id"] for case in cases}) != len(cases):
        raise ValueError("One to four unique cases required")
    for case in cases:
        if set(case) != {"id", "user"} or not isinstance(case["user"], str) or not case["user"].strip():
            raise ValueError("Demo case schema mismatch")
        if any(marker in case["user"] for marker in MARKERS):
            raise ValueError("Reserved chat markers in demo")
    return cases


def generate_demo(model, tokenizer, recipe, output, manifest):
    import torch
    cases = load_cases()
    settings = Generation(max_new_tokens=192)
    disposition = Path("configs/disposition.txt").read_text()
    records = []
    model.eval()
    model.config.use_cache = True
    for case in cases:
        for condition in CONDITIONS:
            messages, use_adapter = assemble([], case["user"], condition, disposition, "")
            encoded = tokenizer.apply_chat_template(messages, tokenize=True, add_generation_prompt=True,
                enable_thinking=False, return_tensors="pt", return_dict=True)
            if encoded["input_ids"].shape[-1] + settings.max_new_tokens > 4096:
                raise ValueError("Demo exceeded the reviewed sequence bound")
            inputs = {key: value.to(model.device) for key, value in encoded.items()}
            started = time.monotonic()
            with torch.no_grad(), torch.autocast("cuda", dtype=torch.bfloat16), (
                    nullcontext() if use_adapter else model.disable_adapter()):
                generated = model.generate(**inputs, do_sample=False, max_new_tokens=settings.max_new_tokens,
                                           use_cache=True, pad_token_id=tokenizer.pad_token_id)
            reply_tokens = generated[0, encoded["input_ids"].shape[-1]:].tolist()
            ended = bool(reply_tokens and reply_tokens[-1] == tokenizer.eos_token_id)
            records.append({"case_id": case["id"], "condition": condition, "messages": messages,
                "model_inputs": {key: value.tolist() for key, value in encoded.items()}, "use_adapter": use_adapter,
                "request_sha256": digest({"messages": messages, "adapter": use_adapter, "settings": asdict(settings)}),
                "reply": tokenizer.decode(reply_tokens, skip_special_tokens=True), "reply_token_ids": reply_tokens,
                "stop_reason": "eos" if ended else "length", "elapsed_seconds": time.monotonic() - started})
    result = {"status": "completed", "purpose": "unrated development illustrations, not efficacy or drift evidence",
              "data_origin": "wholly_invented", "model_id": recipe.model_id, "model_revision": recipe.model_revision,
              "adapter_sha256": hashlib.sha256((output / "adapter/adapter_model.safetensors").read_bytes()).hexdigest(),
              "settings": asdict(settings), "compute_autocast": "bfloat16", "source": manifest["source"],
              "chat_template_sha256": manifest["chat_template_sha256"],
              "disposition_sha256": hashlib.sha256(disposition.encode()).hexdigest(), "cases": cases, "replies": records}
    (output / "demo.json").write_text(json.dumps(result, indent=2))
    return {"cases": len(cases), "replies": len(records),
            "length_limited_replies": sum(row["stop_reason"] == "length" for row in records)}
