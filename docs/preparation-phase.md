# Prepare and debug before a full training run

Date: October 10, 2026. Abel subsequently authorized continued preparation under $100, without approval for each individual bounded check. Retain the $90 working limit and $9 reserve; the larger research campaign still needs a separate decision.

Status: local harness implemented and tested; first approved environment job passed. Jobs billing reports $0.03; the first reservation is reconciled against repeat-verified itemized reported usage. [Run record](runs/2026-10-10-environment.md). This document narrows the first build; the larger research campaign remains a planning budget.

Abel wants the enjoyment of building without an open-ended GPU debugging bill. Keep the preparation phase below $100 cumulatively. Use a $90 working limit across all paid services, with $9 reserved for billing rounding or unexpected ancillary charges. The resulting $99 ceiling includes failed runs and retries, not just successful training. Target $20–$40, and spend only what resolves a concrete uncertainty.

Abel deposited $100, approved the first checks and then authorized continued preparation within the cumulative cap. Funding an account does not itself verify or enforce this project's spending limit. Do not enable automatic credit refills or create a recurring paid endpoint for preparation.

## Local work first: no rented compute

Build and test:

- Invented dialogue schema, provenance, scenario-family splits, leakage checks, and a small curated development fixture. Preserve separate final evaluation cases.
- Training configuration validation, assistant-response loss masks, token-length checks, and explicit step limits.
- A chat interface using a simulated backend to verify adapter/prompt controls, blind comparisons, and correction recording. Simulation verifies wiring, not learned behavior.
- Run manifests recording exact source, model, data, environment, settings, and artifact destinations. Keep credentials out of records.
- Cost estimates, cumulative spending records, explicit provider timeouts, cancellation, and checkpoint persistence paths.
- Automated tests for bad input, missing configuration, incorrect account/destination, and interruption/reload behavior wherever these can be simulated.

Wholly invented examples and local manual review are enough for this phase. Do not pay for synthetic-data generation or model judges by default. Existing account subscriptions and human time are not new charges against the preparation allowance.

Local tests cannot prove GPU availability, CUDA/bitsandbytes compatibility, actual VRAM use, download speed, remote permissions, or recovery of a real adapter. Those require short remote smoke runs. A tiny model can prove a training path works; it cannot validate the 14B model's resource requirements or personality quality.

## Remote stages, each answering one question

| Stage | Purpose | Initial timeout and hardware proposal | Evidence required |
| --- | --- | --- | --- |
| Environment smoke | Verify pinned image, CUDA, libraries, secrets, and artifact writes | Up to 30 minutes on one L4 | Import checks, GPU detected, persistent artifact recovered |
| Tiny adapter smoke | Exercise real training, save, reload, adapter-off/on, and resume | Up to 60 minutes on one L4, using a compatible small Qwen3 model | Finite loss, assistant masks correct, trainable parameters change, checkpoint reload and resumed step work |
| Target model smoke | Verify the actual 14B QLoRA path and measure throughput/VRAM | Up to 90 minutes on one 80 GB A100, 10–30 optimizer steps and short examples | No memory error, measured timing/VRAM, adapter saved and reloaded |
| Short end-to-end demo | Produce a development adapter from about 50–200 reviewed invented episodes and try it in the lab | At most two hours on one A100, if measured throughput supports it | Comparable responses, repair recording, resume and stop work; useful behavior remains exploratory |

These are proposals, not queued jobs or guaranteed runtimes. If a stage needs more time, recalculate it within the same allowance before launch. Downloads, environment setup during billable Starting/Running, and artifact uploads consume time too. Give the job's useful work a shorter deadline than the provider timeout so it has time to save.

Current published rates are L4 $0.80/hour and A100 80 GB $2.50/hour. The proposed timeouts above sum to $9.95 in GPU time for one attempt at each stage. That arithmetic is not a quote or a promise that one attempt will succeed; the $20–$40 target permits some deliberate debugging. Recheck actual rates before launch. [Official Jobs pricing](https://huggingface.co/docs/hub/jobs-pricing).

## Spending and debugging controls

1. Run one paid job at a time. Before launching, record actual spend so far, unresolved maximum liabilities from prior jobs, and the proposed job's maximum cost. Count unknown prior costs conservatively until reconciled.
2. Use the current provider rate and round the timeout up to billable minutes. Include ancillary services and storage. Reserve the maximum cost before submitting so a second launch cannot spend the same remaining allowance.
3. Use a provider-enforced timeout and one attempt. No automatic retry policy, recurring schedule, paid inference endpoint, or paid Space is part of this phase.
4. Limit any proposed preparation job to two hours and $5 of GPU time at launch. Different rates or hardware require recalculation. The first proposed job still must be concrete and reviewable before spending.
5. After a failure, stop the job and inspect the evidence. Repair locally where possible. Relaunch only after a specific change that addresses the failure. After two remote failures on the same issue, stop that issue and reassess; do not keep renting while guessing.
6. Save logs with non-sensitive diagnostics and record run IDs, status, duration, artifacts, and costs. A terminal disconnect or closing a log view does not cancel a job. Confirm terminal job status and reconcile billing after each run.
7. Stop before a launch would exceed the $90 working limit. The $9 reserve is not another debugging allowance. A full corpus, long-context study, repeated training seeds, or larger research campaign requires a new decision after the preparation results are reviewable.

The local environment launcher now implements source-bound approval, account/destination checks, one-attempt provider timeouts, and atomic cumulative reservations. Tests simulate provider submission and billing failures; the first live environment check passed; the first reported charge is reconciled; any running job retains its own maximum reservation. Unknown submission outcomes retain their reservation. The calculator remains a separate estimate. The launcher supports the environment stage and the separately reviewed [tiny training check](tiny-training-review.md), and cannot enforce an account-wide cap or prevent manually started jobs. See the [review package](build-review.md) for evidence and the $1.40 maximum-reservation proposal.

## What success buys us

The preparation phase should produce a working end-to-end development adapter and comparison interface, reproducible artifacts, a tested recovery path, actual GPU timing, and a credible estimate for the next run. It does not establish durable personality or publication-ready results.

Before a full run, review the development responses and verify that every required check passed. Spending the remaining preparation allowance is not itself a goal.

**Next decision:** None; repair and validate the tiny training path within the authorized preparation cap. Reassess after a second remote failure on the same issue.
