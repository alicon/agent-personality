# Agent personality

Reduce the repeated work of correcting an agent's tone, social judgment, verbosity, and interaction style during collaboration. Abel calls that burden “brain carpal tunnel.”

The target is a warm, socially aware colleague with reasoned independence: able to disagree, reconsider when evidence changes, and adapt to the audience without constant coaching. Some quirks and persistence are welcome. Prompt-light is enough.

## Current state

This repository contains a research review, a training and paper plan, a commercial hypothesis, a proposed diagnostic experiment, and eight invented behavioral probes. No drift experiment or personality training has run. The cause of drift in Abel's system remains undiagnosed.

The current direction is to build a Hugging Face personality adapter and a chat lab first, then compare it fairly with prompting. The commercial target is a customer-hosted harness that organizations tune themselves. Molecular-diagnostics assay-development and bioinformatics teams are the proposed first market.

- [Training build, accounts, budget, and paper](docs/training-plan.md)
- [Commercial north star](docs/product-north-star.md)
- [Competitors and molecular-diagnostics first market](docs/market-landscape.md)
- [Research and its limits](docs/research.md)
- [Local observations from October 10, 2026](docs/local-observations.md)
- [Small diagnostic experiment and scoring](docs/experiment.md)
- [Protected baseline and learned-disposition comparison](docs/architecture.md)
- [Behavioral probes](evaluation/probes.json)

## Work order

Use [GitHub Issues](https://github.com/alicon/agent-personality/issues) as the work queue. Priority P0 comes first, followed by P1 and P2. Milestones separate the first build, fair comparison, paper and product work, and the historical drift investigation. Each issue names its dependencies.

Build and play with a learned adapter first, following the [accepted sequencing decision](docs/decisions/0001-training-first.md). Include provenance in the new harness. The separate investigation into Abel's existing system does not block training. Choose a commercial architecture only after measuring collaboration burden and independent judgment.

| Order | Ticket | Depends on |
| --- | --- | --- |
| P0 | [Prepare the Hugging Face trainer and bounded cloud run](https://github.com/alicon/agent-personality/issues/8) | Code can start; paid run needs account and bounded approval |
| P0 | [Curate training examples and reserve unseen scenarios](https://github.com/alicon/agent-personality/issues/9) | Invented examples can start |
| P0 | [Train the first adapter](https://github.com/alicon/agent-personality/issues/5) | #8, #9 |
| P0 | [Build the adapter-switching chat lab](https://github.com/alicon/agent-personality/issues/10) | Interface can start; trained checkpoint from #5 |
| P0 | [Measure repeated personality correction](https://github.com/alicon/agent-personality/issues/2) | Ready |
| P1 | [Establish the protected prompt baseline](https://github.com/alicon/agent-personality/issues/4) | Ready for design; execution uses #8 |
| P1 | [Prepare the comparative paper](https://github.com/alicon/agent-personality/issues/11) | #2, #4, #5, #10 |
| P1 | [Validate the molecular-diagnostics first market](https://github.com/alicon/agent-personality/issues/13) | Research can start; outreach needs an explicit instruction |
| P1 | [Capture the existing system's instruction provenance](https://github.com/alicon/agent-personality/issues/1) | Ready |
| P1 | [Run the historical fresh-versus-long diagnostic](https://github.com/alicon/agent-personality/issues/3) | #1, #2 |
| P2 | [Package the customer-hosted harness](https://github.com/alicon/agent-personality/issues/12) | #5, #10, #13 |
| P2 | [Test specialist handoffs and escalation](https://github.com/alicon/agent-personality/issues/6) | #2 |
| P2 | [Choose by correction burden and judgment](https://github.com/alicon/agent-personality/issues/7) | #11; #6 if evaluating specialists |

GitHub Projects can add a board later. The currently configured CLI credential lacks read:project; Issues, labels, and milestones work.

## Repository checks

Run:

    python3 -m unittest discover -s tests -v

These checks validate the research package's links and probe structure. They do not test model behavior or establish that a mitigation works.

Agent guidance is in [CLAUDE.md](CLAUDE.md). This repository does not install or modify a live personality.
