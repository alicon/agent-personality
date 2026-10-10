# Tiny GPU training, reload and resume passed

October 10, 2026. The repaired Qwen3-0.6B check passed on one L4. It trained a QLoRA adapter, deliberately stopped after step one, reconstructed the model in a fresh subprocess and resumed the saved optimizer to step two. Both saved-adapter reload checks had **zero measured maximum logit difference**. Frozen base parameter bytes remained unchanged through training and reload.

The resumed step changed adapter tensors again. The GPU job retrieved the uploaded adapter and verified its bytes. After provider completion, the adapter was also retrieved locally and matched SHA-256 196a1108292278d8a2e356bc38d6c732e5d4db5773071e67d04467a9d3d5c75b (20,236,472 bytes). This establishes persistence after job termination. The recorded optimizer counters were one and two.

The first failed attempt exposed mismatched mixed-precision wrappers. Removing the training wrapper and controlling inference precision fixed the GPU check without relaxing its tolerance. These results support that diagnosis, but do not prove it was the sole possible contributor in the failed run.

This is a successful software test on fifty invented, unreviewed fixtures. Two optimizer steps are not a useful personality study. No personality-quality or durability evaluation ran, and the actual 14B path remains untested.

## Run record

- [Job 6aca74bc095c578089314eb0](https://huggingface.co/jobs/abelcable/6aca74bc095c578089314eb0): COMPLETED; reservation tiny-c4d4b38ee01e.
- Created 17:24:12.545 UTC; started 17:24:16.027; finished 17:25:15.315 on October 10.
- Source commit c8acfcf12e9c0ca3e53efa14fd82fcb373e2f5c8; bundle SHA-256 8ec0ffe335e788b11fdea9505696c40958dbe43479989fb29bfd2b5a7a419b3c.
- Private adapter artifact revision ab5f84d245690a4ca7ec0f0856373e32e91c6ef1. Summary report revision: 1679014cff51d9b7afc9ad44a022630b4192361b.
- Reported cumulative Jobs usage is **$0.08**, with no other usage charge shown. The ledger records the $0.03 increase over the prior $0.05 subtotal and releases the $1.80 reservation. These increments include aggregate rounding and are not separate per-job invoices. The credit balance displayed $99.96; its difference from the usage subtotal remains unexplained.

[Full machine-readable report](2026-10-10-tiny-success.json), including both phase metrics and exact artifact identities. Keep checkpoint binaries in ignored local storage and the private Hub repository.

**Next decision:** None; run the bounded 14B check under the authorized preparation cap.
