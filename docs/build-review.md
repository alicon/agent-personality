# Review before the first paid run

October 10, 2026. The first approved GPU environment check passed. Jobs billing reports **$0.03**; the **$1.40 reservation remains held** pending settled billing. [Run record](runs/2026-10-10-environment.md). This package does not establish learned personality.

## What you can try now

From this repository, start the local lab:

    .venv-lab/bin/python -m personality_lab.lab

Open http://127.0.0.1:7860. The interface includes twelve [personality calibration situations](../data/calibration.json), a simulated comparison, hidden condition labels, and correction recording. It binds to this computer only; it creates no public sharing link. All default replies explicitly say they are simulated.

Pick A, B, both, or neither on the calibration cards, and explain what feels right or offer your own rewrite. Choices stay in ignored local artifacts and never trigger training. Taste and factual judgment are marked separately: a preferred response that misstates evidence is not automatically a good training target. [How calibration works](personality-calibration.md).

The comparison supports untuned, prompt-only, adapter-only, and hybrid conditions. It records the assembled messages, disposition and factual notes separately, generation settings, condition mapping, and marked corrections. Real-model mode additionally records token inputs and the pinned model, template, and adapter identity. Mock mode records only assembly and controls. Neither a mock nor a file hash establishes observed model behavior.

The correction timer measures wall time between marking a reply and the follow-up, including model latency. It does not measure active human effort. Shared corrective follow-ups affect both conditions, so this interface is suitable for exploratory comparisons; the paper's condition-specific effort study needs separate conversations and a calibrated measurement protocol.

## What was checked locally

- Fifty invented development episodes, forty for training and ten for validation, split across disjoint scenario families. All are agent-authored and **none are human-reviewed**. Repeated variants make these pipeline fixtures, not a representative research corpus.
- All fifty episodes rendered with the actual pinned Qwen3-14B tokenizer. They contain 6,781 tokens, with a maximum of 200 per episode and 2,783 assistant loss tokens. System and user text do not receive loss; padding is ignored and overlong examples fail rather than being truncated.
- A miniature random Qwen model trained a real LoRA adapter on CPU. Tests checked changed adapter weights, unchanged frozen weights, adapter-off/on differences, save/reload equivalence, and interruption followed by a resumed optimizer update. This is a software test, not a useful personality model.
- Local Gradio requests exercised session creation, paired replies, correction recording, and follow-up. Session records survive restart; interrupted timing remains missing rather than being reconstructed.
- Atomic spending reservations prevent concurrent launches through the local launcher. A lost submission response retains the maximum liability and blocks another launch. Wrong account, public artifact destination, an active provider job, changed source/specification, higher live rate, and excess budget fail before submission. Provider submission is mocked in tests.

Verification: 35 tests pass in the lab environment, including the four ML/tokenizer tests. The required system-Python suite also passes, with those four optional tests skipped. Dependency checks and Python static checks pass. No pretrained-model behavior evaluations have run. The first remote check now verifies CUDA/NF4 execution, provider scheduling and private report persistence. GPU model training and the actual 14B memory/throughput path remain untested.

## First paid proposal

The first job checks the GPU environment and artifact persistence. It **does not download model weights or train a model**. If it fails, we inspect and repair before proposing another attempt.

| Item | Proposed setting |
| --- | --- |
| Provider | Hugging Face Jobs, abelcable |
| GPU | One L4, flavor l4x1, 24 GB VRAM |
| Provider timeout | 30 minutes, one attempt, no automatic retries |
| GPU rate | At most $0.80/hour, checked again before submission |
| GPU maximum | $0.40 at the timeout |
| Ancillary reservation | $1.00; a conservative allowance, not a quoted storage charge |
| Maximum reservation for this job | $1.40 against the $90 preparation working limit |
| Persistent output | Private abelcable/agent-personality-qwen3-14b, preparation/runs/<run-id>/environment.json |
| Container | pytorch/pytorch@sha256:417bd75df6365104c283ea4c1651fb3530d9eb5a4c2fafa51943cff2a94e6385 |
| Software | Linux/Python 3.11 dependency resolution in requirements-gpu-resolved.txt; installed versions recorded at runtime |

The public registry confirms the image's amd64 digest. The Linux lock ran successfully in the first environment check. Image setup and package installation use part of the provider timeout. Package installation has its own 15-minute deadline, followed by at most ten minutes for the environment script. The provider's 30-minute timeout covers the whole job.

The launcher uploads only the enumerated repository source, configs, invented data, requirements, and tests as a deterministic bundle. It checks the exact bundle digest before extraction. The Hub token goes through provider secrets, not command arguments or saved manifests. Private-repository writes and a local retrieval of the uploaded result must succeed to establish persistence. A timeout before upload is a failed stage, not evidence that artifacts survived.

Prepare the exact source-bound proposal after reviewing the code:

    .venv/bin/python -m personality_lab.cloud prepare

This writes ignored artifacts/first-run.json and initializes the local ledger without submitting. The eventual submit command requires that proposal's approval digest; the agent will use it only after Abel approves spending. The launcher currently supports this environment stage only. Tiny-model and 14B runs need their own reviewed proposals after the environment result.

A local ledger cannot enforce an account-wide spending cap or prevent manually launched jobs. Confirm final provider status and invoice cost before reconciling the reservation. Use the status/cancel commands in [setup](setup.md); disconnecting a terminal does not cancel a job. Abel deposited $100 and approved this single check. Scheduling succeeded; the billing discrepancy and retained reservation are documented in the run record. The deposit does not authorize further jobs.

**Next decision:** None; prepare a separate tiny-model training proposal locally, and settle the first reservation before another launch.
