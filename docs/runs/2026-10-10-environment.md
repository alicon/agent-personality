# First rented-GPU environment check

October 10, 2026. The approved one-attempt L4 check passed and the provider confirmed completion. CUDA, NF4 operations, tokenizer rendering and private artifact persistence worked. No model weights were downloaded, no model was trained, and no personality evaluation ran.

Hugging Face billing displayed **$0.03 for Jobs**, representing two billed minutes on l4x1. This is current-period reported usage, not a final invoice. The same page displayed $99.99 remaining credits, which does not agree with subtracting $0.03 from the $100 deposit. The reason for that discrepancy is unconfirmed. A later read-only billing check still showed the same itemized $0.03 Jobs charge and no other usage charges. The ledger is now reconciled against **$0.03 reported usage**, releasing the $1.40 reservation. This is the provider's current-period charge, not a final monthly invoice; the unexplained balance discrepancy remains recorded. Abel separately approved the next tiny training check.

## Observed checks

- Pinned Linux image and resolved dependencies started on NVIDIA L4.
- A bfloat16 CUDA matrix operation returned finite values.
- A bitsandbytes NF4 linear operation returned finite values.
- All fifty invented fixtures rendered with the pinned Qwen3-14B tokenizer, at most 200 tokens per episode.
- The private report uploaded successfully and was retrieved through the Hub API after the job completed.

These observations validate the environment and remote persistence. They do not establish GPU training, optimizer recovery, target-model VRAM or throughput, or improved personality. The next software validation is a separately reviewed tiny pretrained-model training/save/reload/resume check; the actual 14B path follows that.

## Run record

| Field | Observed value |
| --- | --- |
| Job | [6aca6acbfee2c9007018a183](https://huggingface.co/jobs/abelcable/6aca6acbfee2c9007018a183) |
| Run/reservation | env-1664e546f5eb |
| Status | COMPLETED; no active account Jobs found after completion |
| Created, UTC | 2026-10-10 16:41:47.680 |
| Started, UTC | 2026-10-10 16:41:50.147 |
| Finished, UTC | 2026-10-10 16:42:15.343 |
| Provider running interval | Approximately 25 seconds; billing reports two minutes |
| Approved limits | One L4, 30-minute timeout, no retries; $0.40 GPU, $1.40 total reserved |
| Source commit | dfc50c71fbba8ecb9a39c6c64a13b9a252e7a782 |
| Source bundle SHA-256 | 147c3d0ea394b17be0c25edfc684d405dd26e92bade974356374d9b1541a87e9 |
| Approval SHA-256 | 9d46207bf0790423930f33b58544fadbb366f7fd08c2150745d16e986c67dc6c |
| Private artifact commit | db3e4a177470f8313509f04eee141c99573f81ce |
| Private artifact path | preparation/runs/env-1664e546f5eb/environment.json |

[Recorded environment report](2026-10-10-environment.json) contains the installed versions. It contains only software and invented-fixture metadata. Local receipt and ledger remain in ignored artifacts/.

Launch, logs, status and artifact retrieval used CLI/Hub APIs. Billing was checked read-only in the browser after no billing command/method was found in the installed CLI/SDK and an authenticated HTTP attempt redirected to login. That observation does not establish that Hugging Face has no billing API.

**Next decision:** None; follow the separately approved tiny training check and record its results. The environment job's reservation is reconciled against reported usage.
