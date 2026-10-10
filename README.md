# Agent personality

Reduce the repeated work of correcting an agent's tone, social judgment, verbosity, and interaction style during collaboration. Abel calls that burden “brain carpal tunnel.”

The target is a warm, socially aware colleague with reasoned independence: able to disagree, reconsider when evidence changes, and adapt to the audience without constant coaching. Some quirks and persistence are welcome. Prompt-light is enough.

## Current state

This repository contains a research review, a proposed diagnostic experiment, and eight invented behavioral probes. No drift experiment or personality training has run. The cause of drift in Abel's system remains undiagnosed.

- [Research and its limits](docs/research.md)
- [Local observations from October 10, 2026](docs/local-observations.md)
- [Small diagnostic experiment and scoring](docs/experiment.md)
- [Protected baseline and learned-disposition comparison](docs/architecture.md)
- [Behavioral probes](evaluation/probes.json)

## Work order

Use [GitHub Issues](https://github.com/alicon/agent-personality/issues) as the work queue. Priority P0 comes first, followed by P1 and P2. Milestones separate diagnosis, the protected prompt baseline, and the learned-disposition comparison. Each issue names its dependencies.

Start with instruction provenance and the correction-effort scorecard. Diagnose before redesigning. Choose an architecture only after measuring collaboration burden and independent judgment.

| Order | Ticket | Depends on |
| --- | --- | --- |
| P0 | [Capture the instructions that actually reach the model](https://github.com/alicon/agent-personality/issues/1) | Ready |
| P0 | [Measure repeated personality correction](https://github.com/alicon/agent-personality/issues/2) | Ready |
| P0 | [Run the fresh-versus-long experiment](https://github.com/alicon/agent-personality/issues/3) | #1, #2 |
| P1 | [Establish the protected prompt baseline](https://github.com/alicon/agent-personality/issues/4) | #3 |
| P2 | [Compare a learned adapter on the same base model](https://github.com/alicon/agent-personality/issues/5) | #2, #4 |
| P2 | [Test specialist handoffs and escalation](https://github.com/alicon/agent-personality/issues/6) | #2 |
| P2 | [Choose by correction burden and judgment](https://github.com/alicon/agent-personality/issues/7) | #4, #5, #6 |

GitHub Projects can add a board later. The currently configured CLI credential lacks read:project; Issues, labels, and milestones work.

## Repository checks

Run:

    python3 -m unittest discover -s tests -v

These checks validate the research package's links and probe structure. They do not test model behavior or establish that a mitigation works.

Agent guidance is in [CLAUDE.md](CLAUDE.md). This repository does not install or modify a live personality.
