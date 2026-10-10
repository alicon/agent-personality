# Continue from another machine

Code, plans, decisions and run reports are in the private [GitHub repository](https://github.com/alicon/agent-personality). Large adapters, optimizer checkpoints and complete generation records are in the private Hugging Face model repository. A new agent can recover the work without this conversation or rerunning training. This is documented recovery, not yet a tested installation on a second physical machine.

## Current checkpoint

As of October 10, 2026, environment validation, tiny GPU save/reload/resume and a twenty-step Qwen3-14B development run passed. The 14B artifact produced sixteen saved replies. They are unreviewed development illustrations; no formal personality-effectiveness or drift study ran. Live pretrained-model chat is unfinished. [Result and measurements](runs/2026-10-10-14b-smoke.md).

Reported spending is $0.46, with no unresolved reservation or active job at this handoff. Abel authorized continued bounded preparation below $100. Keep the $90 working limit and $9 reserve, one paid job at a time, provider timeouts and no automatic retries, refills or recurring endpoints. The $1,000–$2,000 research campaign remains a planning range. [Budget rules](preparation-phase.md).

Planning is in GitHub Issues, with priority/status labels, dependencies and four milestones. A GitHub Projects board has not been created by this work. The current CLI credential lacks read:project; accessing or maintaining a board requires appropriate Projects authorization. This credential limitation does not affect the issue queue.

Next work: finish bounded interactive model chat (#10), collect preferences and curate invented examples (#9), then build the optimized prompt baseline and fair comparison (#4, #2, #11). The fixture adapter is not the finished personality build (#5).

## What travels and what does not

| State | Recovery source |
| --- | --- |
| Code, configs, invented fixtures, plans, decisions, run measurements | GitHub main branch |
| Priorities, dependencies, milestone and completion state | GitHub Issues |
| 14B adapter, saved replies and optimizer checkpoint | Private Hugging Face artifact revision below |
| Current cumulative budget | Local artifacts/budget.sqlite; also a dated, non-secret [ledger snapshot](preparation-ledger.json) in GitHub |
| Human preferences and chat records | Local artifacts/calibration/, artifacts/demo-reviews/ and artifacts/chat/; not automatically backed up |
| GitHub/Hugging Face credentials | Authenticate on the new machine; do not put credentials in Git |
| Python environments and running Gradio process | Recreate locally; environments and localhost processes do not migrate |
| Personal agent skills and global instructions | Machine-specific installation; not bundled with this research repository |

No calibration or model-reply preference files existed at this handoff. Two local mock-chat records existed. Future human feedback must be copied separately if it should survive a move. Do not upload local session records wholesale: they are not constrained to invented text merely because the interface requests it.

## Recover the app without renting a GPU

Clone the private repository, authenticate GitHub and Hugging Face as the accounts with access, then follow [setup](setup.md). The tested Mac lab uses Python 3.13 and requirements-local-resolved.txt. Linux/CUDA has a separate pinned container and requirements-gpu-resolved.txt; do not reuse the Mac lock as a Linux training environment. Installation on other OS/Python combinations remains untested.

Download only the saved reply record to browse it. The following authenticated CLI command performs no training or inference:

    .venv/bin/hf download abelcable/agent-personality-qwen3-14b preparation/runs/q14-60fc11a776c4/demo.json --revision 034df8c0881b1c8398db86822c945ef10d5c7397 --local-dir artifacts/recovered/q14-60fc11a776c4
    .venv-lab/bin/python -m personality_lab.lab --demo-path artifacts/recovered/q14-60fc11a776c4/preparation/runs/q14-60fc11a776c4/demo.json

Open http://127.0.0.1:7860. The saved replies are actual model outputs. Conversation controls still default to simulated replies.

For training artifacts, retrieve adapter/, manifest.json, metrics.json or checkpoint-20/ under the same pinned run path. The base model is Qwen/Qwen3-14B at revision 40c069824f4251a91eefaf281ebe4c544efd3e18. The recovered adapter SHA-256 is 40fdbcd0f6545ff7c11be2f1c60c433bc893b4d4f65601d5c604c86bdc0563d9. Verify bytes before using it. Saved optimizer files exist remotely; actual fresh-process 14B optimizer resume has not been tested. Tiny-model optimizer resume has.

## Preserve the budget before another paid launch

Prefer copying the current artifacts/budget.sqlite from the machine that last submitted a job. Use one submitting machine at a time: separate local SQLite ledgers do not share a lock, even if both machines have the same checkout. A fresh empty ledger would incorrectly show zero prior spending.

If the original ledger is unavailable, reconstruct a new ledger from the GitHub snapshot only after checking that it is still current: inspect remote Jobs, read the latest run reports and compare itemized billing. Any new or unresolved job requires preserving its full liability; do not use an older completed snapshot to erase it. The reported $0.46 is current-period usage, not a final invoice.

The following reconstruction refuses to overwrite an existing ledger. Run it from the repository root, after establishing the snapshot remains current:

    .venv/bin/python - <<'PY'
    import json
    from decimal import Decimal
    from pathlib import Path
    from personality_lab.budget import Ledger
    state = json.loads(Path('docs/preparation-ledger.json').read_text())
    target = Path('artifacts/budget.sqlite')
    if target.exists():
        raise SystemExit('Existing ledger found; preserve it instead of overwriting')
    assert state['version'] == 1 and state['account'] == 'abelcable'
    assert all(row['state'] == 'reconciled' for row in state['rows'])
    assert sum(Decimal(row['actual']) for row in state['rows']) == Decimal(state['reported_spent_usd'])
    ledger = Ledger(target)
    columns = ('reservation', 'plan_sha', 'maximum', 'state', 'job_id', 'actual', 'terminal_status')
    with ledger.connect() as db:
        for row in state['rows']:
            db.execute('INSERT INTO jobs VALUES (?,?,?,?,?,?,?)', tuple(row[key] for key in columns))
    print(ledger.summary())
    PY

Prepared paid-job plans also live locally. Generate a fresh source-bound plan on the new checkout; do not reuse a prior job's digest after source changes. Inspect only selected job metadata, never full specifications containing secrets.

Before handing off changes, run python3 -m unittest discover -s tests -v. The separate lab environment runs optional ML checks. Do not confuse software checks with model personality evaluation.

**Next decision:** None to recover the saved app. Before paid work, the continuing agent must verify the latest budget and remote job state; a machine change does not reset the $100 allowance.
