# Hugging Face setup

Checked October 10, 2026. Local harness is implemented; GPU execution and pretrained-model evaluation remain untested.

## Current resources

- Account: [abelcable](https://huggingface.co/abelcable).
- Private model repository: [agent-personality-qwen3-14b](https://huggingface.co/abelcable/agent-personality-qwen3-14b).
- Private dataset repository: [agent-personality-dialogues](https://huggingface.co/datasets/abelcable/agent-personality-dialogues).

Authentication was verified against the expected account. Both repositories were created through the Hub API and their private visibility was checked. They contain no uploaded training corpus or learned checkpoint yet. No GPU job, endpoint, or paid Space was started.

The local CLI is huggingface_hub 2.2.0, installed in this project's ignored .venv using Python 3.13.2. The [bootstrap requirements](../requirements-bootstrap.txt) pin the installed packages. This is Hub tooling, not the future Linux/CUDA training environment.

Abel completed the CLI's browser/device authorization. Credentials are kept in the Hugging Face local credential cache outside the repository. Never copy credentials into issue bodies, chat, source files, or command arguments.

## Reproduce the local tools

From the repository directory:

    python3 -m venv .venv
    .venv/bin/python -m pip install -r requirements-bootstrap.txt
    .venv/bin/hf auth login
    .venv/bin/hf auth whoami

The CLI supports browser/device login; the human reviews and authorizes access in their browser. It also supports locally entered access tokens. [Official CLI guide](https://huggingface.co/docs/huggingface_hub/guides/cli).

Before uploading any artifacts, verify that the authenticated account is abelcable and the destination is private. Passing private=True when reusing an existing repository does not change its existing visibility.

## Local lab and training checks

The lab uses a separate ignored .venv-lab so the working Hub 2.2.0 login/Jobs tools remain intact. On the Mac, create it with Python 3.13 and install requirements-local-resolved.txt. requirements-lab.txt records the main dependencies. For Linux/CUDA, use the pinned container and requirements-gpu-resolved.txt instead; the Mac lock is not a Linux lock.

    python3 -m venv .venv-lab
    .venv-lab/bin/python -m pip install -r requirements-local-resolved.txt
    .venv-lab/bin/python -m personality_lab.data --tokenizer-check
    .venv-lab/bin/python -m unittest discover -s tests -v
    .venv-lab/bin/python -m personality_lab.lab

The tokenizer check downloads public tokenizer files, not model weights or paid inference. The tests use the cached tokenizer and a random miniature CPU model; they do not download a pretrained model. Gradio binds only to 127.0.0.1 and starts with simulated replies. No public link or paid service is created.

Development data can be reproduced with python3 scripts/build_development_data.py. This writes fifty invented fixtures with explicit unreviewed status. Calibration choices and chat traces stay in ignored artifacts/. Never commit tokens or private work transcripts.

The GPU training entry point is personality_lab.training with --recipe configs/tiny-smoke.json or configs/14b-smoke.json, a unique --run-id, and optional --persist-repo. It refuses a CUDA-free fallback. Recipes are limited smoke configurations, not full campaign recipes. Standard Transformers Trainer is used with explicitly verified assistant masks; TRL/preference optimization is deferred.

## Reviewed cloud execution only

The [first proposal](build-review.md) is a thirty-minute environment check, with at most $0.40 in GPU time and $1.00 ancillary reservation. Funding and spending remain pending Abel's review. The larger research range remains a planning budget.

Prepare without submission:

    .venv/bin/python -m personality_lab.cloud prepare

After explicit human approval, submit using the exact approval_sha256 from artifacts/first-run.json:

    .venv/bin/python -m personality_lab.cloud submit --approve-plan REVIEWED_DIGEST

The local ledger is artifacts/budget.sqlite. Preserve it across sessions. An interrupted submit may have started a remote job: do not discard the reservation or rerun while uncertain. Find the job by its project/reservation labels using the read-only Jobs listing. Never print full job specs because they can include secrets.

Inspect or cancel explicitly:

    .venv/bin/python -m personality_lab.cloud status --job-id JOB_ID
    .venv/bin/python -m personality_lab.cloud cancel --job-id JOB_ID

Confirm a terminal status, retrieve the private environment.json artifact, and inspect billing. Reconcile only the actual charge, including ancillary charges, with the reservation returned at launch:

    .venv/bin/python -m personality_lab.budget --reconcile RESERVATION_ID --actual INVOICE_USD --terminal-status COMPLETED

If a submission response was lost, retain maximum liability until the job or confirmed non-submission is established. The CONFIRMED_NOT_SUBMITTED reconciliation status is for that established case, never an assumption from a network error. The provider timeout remains active if the terminal disconnects. Closing Gradio or a log view does not cancel a cloud job.

Billing balance and successful GPU scheduling have not been established by repository creation. Account setup does not establish training eligibility or capacity.

**Next decision:** Abel reviews the local build and decides whether to fund and approve the first environment job. The launcher will not submit without that decision.
