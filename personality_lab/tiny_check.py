"""Two-process GPU checkpoint smoke; not a personality quality evaluation."""
import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import time

from personality_lab.training import Recipe, environment_manifest, persist_folder


def phase_commands(recipe_path, run_id, repo):
    recipe = Recipe.load(recipe_path)
    if recipe.model_id != "Qwen/Qwen3-0.6B" or recipe.max_steps != 2:
        raise ValueError("Tiny check requires the two-step small-model recipe")
    common = [sys.executable, "-m", "personality_lab.training", "--recipe", str(recipe_path),
              "--verify-frozen-base", "--persist-repo", repo]
    first_id, second_id = run_id + "-first", run_id + "-resume"
    checkpoint = str(Path(recipe.output) / first_id / "checkpoint-1")
    return (common + ["--run-id", first_id, "--stop-after-step", "1"],
            common + ["--run-id", second_id, "--resume", checkpoint])


def check_phase_reports(first, second, first_metrics, second_metrics):
    if (first["status"] != "stopped_early" or second["status"] != "completed"
            or first_metrics["steps"] != 1 or second_metrics["steps"] != 2
            or first_metrics.get("optimizer_step_values") != [1]
            or second_metrics.get("optimizer_step_values") != [2]
            or second.get("resume_start_step") != 1):
        raise ValueError("Expected an interrupted first step and a resumed second step")
    for manifest, metrics in ((first, first_metrics), (second, second_metrics)):
        if not all(manifest.get(key) is True for key in
                   ("adapter_changed", "reload_checked", "frozen_parameters_unchanged")):
            raise ValueError("Training, reload and frozen-parameter checks must pass")
        if not math.isfinite(metrics["validation"]["eval_loss"]):
            raise ValueError("Validation loss must be finite")
        if not math.isfinite(manifest["adapter_on_off_max_abs_delta"]) or manifest["adapter_on_off_max_abs_delta"] <= 0:
            raise ValueError("Adapter on/off must differ")
    if any(first[key] != second[key] for key in ("recipe", "data_sha256", "chat_template_sha256", "source")):
        raise ValueError("Training phases must have identical provenance")


def adapter_changed(first_path, second_path):
    import torch
    from safetensors.torch import load_file
    first, second = load_file(str(first_path)), load_file(str(second_path))
    if set(first) != set(second) or any(first[key].shape != second[key].shape for key in first):
        raise ValueError("Resumed adapter layout changed")
    if not all(torch.isfinite(tensor).all() for tensor in list(first.values()) + list(second.values())):
        raise ValueError("Adapter tensors must be finite")
    return any(not torch.equal(first[key], second[key]) for key in first)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--persist-repo", required=True)
    args = parser.parse_args()
    if not re.fullmatch(r"[a-zA-Z0-9_-]{1,60}", args.run_id):
        parser.error("Simple run ID required")
    recipe_path = "configs/tiny-check.json"
    recipe = Recipe.load(recipe_path)
    commands = phase_commands(recipe_path, args.run_id, args.persist_repo)
    root = Path(recipe.output)
    output = root / args.run_id
    output.mkdir(parents=True, exist_ok=False)
    report = {"status": "started", "run_id": args.run_id, "model_training": True, "behavior_evaluation": False,
              "data_review": "agent-authored unreviewed software fixtures; not calibrated to Abel",
              "environment": environment_manifest(),
              "source_bundle_sha256": os.environ.get("PERSONALITY_SOURCE_SHA256"),
              "source_git_commit": os.environ.get("PERSONALITY_SOURCE_COMMIT")}
    started = time.monotonic()
    try:
        # These are two planned phases, never a retry of a failed phase.
        subprocess.run(commands[0], check=True, timeout=900)
        subprocess.run(commands[1], check=True, timeout=600)
        first_dir, second_dir = root / (args.run_id + "-first"), root / (args.run_id + "-resume")
        first, second = [json.loads((path / "manifest.json").read_text()) for path in (first_dir, second_dir)]
        first_metrics, second_metrics = [json.loads((path / "metrics.json").read_text()) for path in (first_dir, second_dir)]
        check_phase_reports(first, second, first_metrics, second_metrics)
        adapter_path = second_dir / "adapter/adapter_model.safetensors"
        if not adapter_changed(first_dir / "adapter/adapter_model.safetensors", adapter_path):
            raise RuntimeError("Resumed optimizer step did not change adapter tensors")
        # Retrieve exact uploaded adapter bytes through the Hub into a fresh directory.
        from huggingface_hub import HfApi, hf_hub_download
        revision = HfApi().model_info(args.persist_repo).sha
        remote_path = f"preparation/runs/{args.run_id}-resume/adapter/adapter_model.safetensors"
        expected_sha = hashlib.sha256(adapter_path.read_bytes()).hexdigest()
        with tempfile.TemporaryDirectory() as directory:
            recovered = hf_hub_download(args.persist_repo, remote_path, revision=revision, local_dir=directory)
            if hashlib.sha256(Path(recovered).read_bytes()).hexdigest() != expected_sha:
                raise RuntimeError("Persisted adapter bytes differ from saved adapter")
        report.update(status="completed", first=first, resumed=second,
                      first_metrics=first_metrics, resumed_metrics=second_metrics,
                      adapter_changed_after_resume=True, uploaded_adapter_retrieved=True,
                      adapter_sha256=expected_sha, artifact_revision=revision, artifact_path=remote_path)
    except BaseException:
        report["status"] = "failed"
        raise
    finally:
        report["elapsed_seconds"] = time.monotonic() - started
        (output / "tiny-check.json").write_text(json.dumps(report, indent=2))
        persist_folder(output, args.run_id, args.persist_repo)
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
