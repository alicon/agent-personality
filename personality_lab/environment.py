"""First paid smoke: CUDA compatibility and persistence; no model weights downloaded."""
import argparse
import json
import os
from pathlib import Path
import time

from personality_lab.data import encode_episode, load_episodes
from personality_lab.training import environment_manifest, persist_folder


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--persist-repo", required=True)
    args = parser.parse_args()
    import torch
    import bitsandbytes as bnb
    from transformers import AutoTokenizer
    output = Path("artifacts/environment") / args.run_id
    output.mkdir(parents=True, exist_ok=True)
    started = time.monotonic()
    report = {"status": "started", "environment": environment_manifest(), "model_training": False,
              "behavior_evaluation": False, "run_id": args.run_id,
              "source_bundle_sha256": os.environ.get("PERSONALITY_SOURCE_SHA256"),
              "source_git_commit": os.environ.get("PERSONALITY_SOURCE_COMMIT")}
    try:
        if not torch.cuda.is_available() or not torch.cuda.is_bf16_supported():
            raise RuntimeError("Expected CUDA/bfloat16 GPU unavailable")
        x = torch.ones((16, 16), device="cuda", dtype=torch.bfloat16)
        if not torch.isfinite(x @ x).all():
            raise RuntimeError("CUDA matrix multiply failed")
        layer = bnb.nn.Linear4bit(16, 16, bias=False, compute_dtype=torch.bfloat16, quant_type="nf4").cuda()
        if not torch.isfinite(layer(x)).all():
            raise RuntimeError("NF4 operation failed")
        tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen3-14B", revision="40c069824f4251a91eefaf281ebe4c544efd3e18")
        rows = load_episodes("data/development.jsonl")
        encoded = [encode_episode(row, tokenizer, 4096) for row in rows]
        report.update(status="completed", gpu=torch.cuda.get_device_name(),
                      tokenizer_episodes=len(encoded), max_tokens=max(len(row["input_ids"]) for row in encoded))
    except BaseException:
        report["status"] = "failed"
        raise
    finally:
        report["elapsed_seconds"] = time.monotonic() - started
        (output / "environment.json").write_text(json.dumps(report, indent=2))
        persist_folder(output, args.run_id, args.persist_repo)
    # Retrieval is required separately on the local host to establish persistence.
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
