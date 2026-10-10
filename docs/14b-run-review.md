# Bounded 14B training and example run

October 10, 2026. Prepared under Abel's authorization to continue below $100. The [tiny training/reload/resume check passed](runs/2026-10-10-tiny-success.md); reported cumulative usage is $0.08. This job exercises the actual 14B model and saves illustrative replies to inspect.

One Hugging Face a100-large (80 GB) runs once with a 90-minute provider timeout and no automatic retries. The rate ceiling is $2.51/hour, slightly above the published $2.50 to accommodate the provider's rounded minute quote. GPU liability rounds up to **$3.77**, plus $1 ancillary allowance: **$4.77 maximum reservation**. Preflight checks the actual A100 rate, account, private repository, active jobs and cumulative ledger again. This job does not create a serving endpoint or recurring schedule.

Use Qwen/Qwen3-14B at revision 40c069824f4251a91eefaf281ebe4c544efd3e18, whose public safetensors total 29,536,665,640 bytes. The immutable container and pinned Linux dependencies are unchanged. Package installation is limited to fifteen minutes; the training/demo script to seventy minutes, within the ninety-minute job timeout. Downloads and uploads consume that time too.

The [recipe](../configs/14b-smoke.json) runs twenty optimizer steps with rank-32 NF4/bfloat16 QLoRA, gradient accumulation four, and assistant-only loss. The fifty invented examples are agent-authored and unreviewed. Their maximum length is 200 tokens despite a 4,096-token recipe ceiling. Measured memory and throughput therefore describe short examples, not full-length context performance or a full corpus.

Require finite metrics, changed adapter parameters, adapter-on/off differences, saved-adapter reload agreement at identical inference precision, versioned manifests and private checkpoints. After completion, retrieve the adapter locally and verify its bytes. Record timing and peak allocated VRAM; do not substitute those values for total device memory or projected long-context capacity.

The job then generates sixteen saved replies: four new invented development scenarios under untuned, prompt-only, adapter-only and combined conditions. All use the same pinned base, factual inputs, non-thinking mode and deterministic decoding. Each reply is capped at 192 new tokens and records whether it hit that limit. The prompt-only arm receives the versioned experimental disposition. Cases are outside the training examples and the existing final diagnostic probes.

These are **unrated development illustrations**, not a fair final study or evidence that traits endure. Record complete assembled messages, actual token inputs, adapter and disposition identities, settings and raw replies. A truncation must stay visible; a short truncated response is not evidence of good brevity. The eventual paper still requires a calibrated corpus, optimized prompt baseline, unseen scenario families, independent conversations, repeated runs and human correction-effort measures.

Prepare without submission:

    .venv/bin/python -m personality_lab.cloud prepare --stage 14b-smoke --plan artifacts/14b-plan.json

Submit only that prepared source/configuration digest after local checks and budget verification. Any changed source needs a fresh plan. Abel's cumulative preparation authorization covers this bounded job; spending outside that scope needs a separate decision.

**Next decision:** None; complete the local checks, run this bounded job, retrieve its artifacts and assess the illustrative replies.
