# Durable agent personality: evidence and recommendation

Reviewed October 10, 2026.

The practical target is less repeated correction during useful work. A stable persona can still be exhausting, flattering, rigid, or incapable of adapting to an engineering colleague versus an executive.

The evidence supports testing learned disposition, but does not establish that putting personality into weights solves long-session drift. Diagnosing the current system remains useful; the [accepted training-first direction](decisions/0001-training-first.md) lets the hobby build proceed alongside it.

## What the research establishes

| Source | Demonstrated finding | Limit for this project |
| --- | --- | --- |
| [Measuring and Controlling Persona Drift](https://arxiv.org/html/2402.10962v1) | In experiments involving older chat models, adherence to an unchanged persona prompt degraded during conversation. The authors examined attention decay and tested inference interventions. | This establishes that file mutation is unnecessary for drift. The models, artificial personas, and self-dialogue benchmark do not diagnose Abel's present system. Attention decay remains an explanatory hypothesis here. |
| [BIG5-CHAT](https://arxiv.org/html/2410.16491v3) | SFT and DPO, using LoRA, induced Big Five traits in Llama models more strongly than the tested prompting baselines on personality questionnaires. | Trait names and levels still appeared in instructions for trained models. Questionnaire performance does not establish prompt-free disposition, sustained working relationships, or reduced corrective effort. The dialogue data are generated with human-grounded trait generators, rather than simply a corpus of human conversations. |
| [Oxford warmth training](https://syntheticsociety.oii.ox.ac.uk/research/warm-llm/) | The researchers report that training five models toward warmer behavior increased errors and reinforcement of incorrect user beliefs, despite largely preserved standard benchmark performance. | This is a risk demonstrated under their training and evaluation conditions, not proof that warmth necessarily causes sycophancy. Evaluate warmth and judgment separately. The lab's primary research summary was accessible; the linked Nature article and PMC copy could not be retrieved in this session. |
| [Persona Vectors](https://arxiv.org/html/2507.21509v3) | Activation directions tracked selected traits and predicted or mitigated changes induced by fine-tuning. Strong inference steering could reduce general capability. | Activation steering changes runtime hidden states; an adapter changes learned parameters. Neither should be presented as a proven durable personality layer for this use case. The work also shows why factual or task training can unintentionally affect disposition. |
| [Multi-turn persona RL](https://arxiv.org/html/2511.00222v1) | Multi-turn RL improved persona consistency in simulated human users. | The authors explicitly acknowledge that their consistency objective may penalize justified changes of tone or perspective. A simulator of a fixed human persona is a different target from a colleague who should learn and reconsider. |

## Two causes to distinguish

**Instruction mutation:** a core file changes, another file replaces it, a loader omits it, or a summarizer changes its representation. A source file can be stable while the instruction supplied to the model changes.

**Behavioral drift with stable instructions:** an unchanged disposition is expressed differently as task history, tool output, prior assistant answers, or surrounding instructions accumulate.

These can coexist. Changing provider/model versions, generation settings, retrieval, tools, or personality modes introduces additional explanations. A fresh conversation recovering the desired behavior is suggestive of context effects, but a reset usually changes several variables at once.

Official OpenAI documentation describes global and project instruction discovery, precedence, and a size limit. It also describes instruction loading at session startup. This makes instruction provenance worth recording, but says nothing by itself about the cause of Abel's drift. [Custom instructions with AGENTS.md](https://learn.chatgpt.com/docs/agent-configuration/agents-md).

The [local inspection](local-observations.md) found writable communication files and layered instruction sources. It did not find a historical change that explains personality drift.

## Mitigations worth testing

1. **Protect the core.** Pin a version and hash, and have a launcher outside the task agent's write authority verify and load it. Allow proposed amendments. Git history makes changes recoverable; it does not prevent an agent from changing a file.
2. **Separate memory.** Facts and task lessons use a different store and retrieval path. A lesson about one ticket or recipient should not silently become a universal social rule.
3. **Observe assembly.** Record source bytes, roles, order, truncation, retrieval, surrounding instructions, model/settings, and compaction events at the closest observable boundary to inference.
4. **Evaluate during work.** Probe after technical work and context compression. Measure how often Abel must interrupt to correct presentation, and whether the same correction returns.
5. **Train judgment alongside style.** Include both socially pressured disagreement and warranted revision. Do not reward agreement, rigid stance retention, or minimum word count as substitutes for collaboration.

Each item is a proposed mitigation. None has been validated in this repository.

## Recommendation

Build the adapter and chat lab under the [training plan](training-plan.md). Establish a protected prompt baseline and compare on the same base model before treating a smaller social model plus specialists as an architecture choice. The [small diagnostic experiment](experiment.md) remains a separate investigation into the existing system.

The architecture is plausible. Its value remains a hypothesis: it might reduce corrective effort, or merely relocate the errors to routing and the presentation of specialist findings. The [comparison plan](architecture.md) makes those failure modes observable.

**Next decision:** None for the investigation package. Next action: prepare the training build and calibrate the scoring examples.
