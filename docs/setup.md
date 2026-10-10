# Hugging Face setup

Checked October 10, 2026. Local setup is complete; model training is still planned.

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

## Remaining work

Implement and test the trainer, dataset preparation, and chat lab under the [preparation phase below $100](preparation-phase.md). Then propose a bounded GPU smoke run with an explicit timeout, persistence destination, expected cost, and cumulative spend allowance. Funding can wait until that run is ready. The $1,000–$2,000 campaign range remains a planning budget.

Billing balance and successful GPU scheduling have not been established by repository creation. Account setup does not establish training eligibility or capacity.

**Next decision:** None for account setup. Next action: implement the trainer and invented-data tooling; present the first paid run when it is concrete and reviewable.
