# Review the tiny-model training check

October 10, 2026. Abel approved this one check; **submitted** as [6aca728a095c578089314c80](https://huggingface.co/jobs/abelcable/6aca728a095c578089314c80). It failed after the first optimizer step at the reload comparison. [Result and local repair](runs/2026-10-10-tiny-first.md). The [repaired attempt passed](runs/2026-10-10-tiny-success.md) under Abel's subsequent authorization to continue below $100. The first GPU environment check passed. This next job tests whether a real pretrained Qwen3-0.6B model can train, persist and resume a QLoRA adapter on rented hardware. Two optimizer steps are a software check, not a personality prototype or a comparison with prompting.

## Proposed job

| Item | Setting |
| --- | --- |
| Provider | Hugging Face Jobs, abelcable; one L4 with 24 GB VRAM |
| Limits | One job, 60-minute provider timeout, one attempt, no automatic retries |
| Rate ceiling | $0.80/hour; live minute rate checked again before launch |
| Maximum reservation | $0.80 GPU + $1.00 ancillary allowance = **$1.80** |
| Base | Qwen/Qwen3-0.6B, revision c1899de289a04d12100db370d81485cdf75e47ca |
| Download | Public, ungated; model safetensors total 1,503,300,328 bytes |
| Learning | NF4/bfloat16, rank-8 LoRA, assistant-only loss, two optimizer steps total |
| Data | Fifty wholly invented, agent-authored unreviewed fixtures; forty train, ten validation |
| Private destination | abelcable/agent-personality-qwen3-14b, preparation/runs/<run-id> and phase subfolders |
| Recipe | [tiny-check.json](../configs/tiny-check.json) |

The pinned container and Linux dependencies are the ones that passed the environment check. Package installation has a 15-minute deadline. The training/check module has a 30-minute deadline: its first subprocess has 15 minutes, its resumed subprocess ten minutes, leaving time for checks and artifact upload. Each trainer has a five-minute soft training deadline. These are limits, not expected runtimes or promises of successful artifact persistence after a hard timeout.

## What it must establish

1. Stop deliberately after optimizer step one and save adapter, optimizer, scheduler and RNG state. Check finite training/validation values, unchanged frozen base parameter bytes, detectable adapter-on/off logit differences, and saved-adapter reload agreement.
2. Start a fresh subprocess. Validate the old checkpoint's model, data, tokenizer template and learning configuration before writing a new manifest. Resume the full checkpoint and finish step two; confirm the optimizer step counter reaches two and adapter tensors change again.
3. Retrieve the uploaded final adapter into a fresh directory and compare its bytes with the saved adapter. Upload a summary containing phase manifests and metrics. After provider completion, retrieve the report and adapter locally again; only that establishes persistence beyond job termination.

The reload check uses the trainer's explicit numerical tolerance (absolute and relative 0.02), and records the measured maximum difference. Frozen-parameter hashing checks parameter bytes, not every buffer or quantization-state object. It is restricted to this tiny model to avoid hashing the entire 14B base.

A failed first phase prevents the resumed phase from starting. A failed resumed phase does not retry. Preserve the spending reservation after unknown submission, execution or billing outcomes.

## Local evidence and remaining uncertainty

All **42 tests pass** in the lab environment. The required system-Python suite passes with six optional ML checks skipped. A random miniature CPU model proves that deliberate stop followed by reconstruction and full optimizer resume matches uninterrupted training to the tested tolerance. Tests reject changed resume provenance, missing checkpoint state, failed reload/base checks, stale optimizer counters, and mutated job approvals. Static checks pass.

The actual Qwen3-0.6B tokenizer rendered all fifty fixtures locally, with at most 200 tokens per episode. These checks download tokenizer files only. No pretrained base weights were downloaded locally. The first GPU attempt trained one step; its saved adapter and optimizer checkpoint were recovered locally. No personality behavior evaluation ran.

The first environment job validates CUDA/NF4 operations, but The first GPU attempt established one training step and its measured memory use; adapter reload failed and GPU optimizer recovery remains untested. This is what the proposed job resolves. It does not answer whether learned personality is useful, durable or better than prompts. The actual 14B model requires its own later check.

## Approval and billing boundary

The $100 deposit funds the account; it does not authorize this run. Abel separately approved the completed environment check and this one tiny check. The first reservation is reconciled against repeat-verified itemized usage of $0.03; the unexplained credit-balance discrepancy remains in its run record. The failed job is reconciled; reported cumulative Jobs usage is $0.05. A repaired attempt reserves $1.80. Preparing a proposal performs no billing reconciliation or paid submission.

Prepare the exact source-bound plan without spending:

    .venv/bin/python -m personality_lab.cloud prepare --stage tiny-check --plan artifacts/tiny-training-plan.json

For the repaired attempt, Abel's authorization to continue preparation under $100 supplies spending permission. Prepare a fresh exact source-bound plan, verify local tests and the resolved prior reservation, then submit with its digest:

    .venv/bin/python -m personality_lab.cloud submit --plan artifacts/tiny-training-plan.json --approve-plan REVIEWED_DIGEST

Any source, configuration, rate or Git revision change requires a fresh plan and verification. Another human approval is needed if spending leaves the authorized preparation scope. The launcher checks the expected account, private destination, active jobs, actual rate and cumulative budget again. Its ledger retains unknown liabilities. The local ledger cannot prevent manually launched jobs outside the harness.

**Next decision:** None; proceed to the 14B preparation check within the authorized cumulative cap.
