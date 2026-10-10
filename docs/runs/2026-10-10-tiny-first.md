# First tiny GPU training check: reload failure

October 10, 2026. The first Qwen3-0.6B check completed one QLoRA optimizer step, then failed its saved-adapter reload comparison. The job stopped; the planned resumed phase never started and no automatic retry occurred. This is a failed software validation, not evidence of personality quality.

The first step produced finite training loss (2.5437) and validation loss (4.0664). The frozen base parameter-byte check passed, and adapter-on/off outputs differed. The training/evaluation interval lasted about four seconds, with 1,418,351,616 bytes peak allocated CUDA memory. This figure covers this tiny run, not the 14B model or all GPU memory use.

The saved adapter, checkpoint and optimizer state survived job termination. Local recovery verified 392 finite adapter tensors containing 5,046,272 parameters, identical checkpoint/final adapter tensors, and optimizer step one. The adapter remains unsuitable for the lab because reload validation failed. No scientific or personality behavior evaluation ran.

## Diagnosis and repair

The confirmed error was `Saved adapter reload mismatch`. The failed run did not record its maximum reload difference, so that magnitude remains unknown. Inspection found that Trainer/Accelerate decorates the trained model's forward method with bfloat16 autocast and an output conversion; a newly reloaded PeftModel does not automatically inherit that wrapper.

A local CPU mixed-precision reproduction failed the same absolute/relative 0.02 comparison, with maximum difference 0.0391283. Giving both calls identical bfloat16 autocast yielded zero difference. This demonstrates the precision-confounding mechanism locally; it does not establish that it was the sole cause of the GPU failure.

The repair removes the training wrapper before inference checks, applies the same explicit bfloat16 compute settings to both models, and compares outputs in float32. The tolerance is unchanged. It also records the maximum reload difference before testing it and checks frozen parameter bytes after reload. A second bounded GPU attempt will test the hypothesis. Stop this issue and reassess if that repair fails again.

## Run and spending record

- [Job 6aca728a095c578089314c80](https://huggingface.co/jobs/abelcable/6aca728a095c578089314c80): ERROR; run tiny-3a1d2b1ec4b7.
- Created 17:14:50.576 UTC; started 17:15:57.760; finished 17:16:48.995 on October 10.
- Source commit 50b98dced1d49a2a78a48e8eb1ecb3e79227c6c0; bundle SHA-256 944630403e936050908de633ea9b6478ae7ead9906e0cbc70db3498ad106f96d.
- Private artifact revision 4a759d9adba70ec7f878bd12ad201000c63523e3 in abelcable/agent-personality-qwen3-14b.
- The $1.80 reservation was released against the reported Jobs subtotal increasing from $0.03 to **$0.05 cumulative**. The $0.02 increment includes aggregate rounding and is not a separate per-job invoice. No other usage charge was displayed. Credits displayed $99.97; the balance/subtotal discrepancy remains unexplained.
- No active Jobs remain. No endpoints, paid Spaces or automatic refills were created.

[Machine-readable run record](2026-10-10-tiny-first.json). Checkpoint binaries and scrubbed logs remain in ignored local artifacts; private Hub artifacts are unchanged.

Abel subsequently authorized continued preparation under $100. This covers bounded further checks within the existing $90 working limit and $9 reserve; it does not authorize the larger research campaign.

**Next decision:** None; finish the local regression test and run the repaired tiny check under the preparation budget.
