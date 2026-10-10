# Candidate mitigations and a fair learned-disposition comparison

Status: proposed architecture. No baseline protection, adapter, specialist router, or serving system is implemented or deployed.

## Protected prompt baseline

Keep a short, versioned core disposition under an owner-controlled write boundary. A launcher verifies the selected version and injects its exact bytes at the appropriate instruction level. Task agents can propose amendments; promotion is a separate operation.

Git tracks the proposed and accepted versions. It does not create protection by itself. File permissions are also insufficient if the agent runs as the same owner and can undo them. The effective boundary needs a separate identity, read-only mount, or another independently enforced write restriction. Which mechanism fits the host is an implementation decision.

Use distinct stores for:

- Core disposition and relationship-level principles.
- Retrieved facts about people, projects, and past decisions.
- Task-specific lessons and workflow guidance.

Give notes a scope, source, and timestamp. “Keep this engineering request short” should not become “always answer briefly.” Preserve the exact selected core across compaction; summarize task state separately. Test bounded relevant retrieval rather than assuming that removing memory improves personality.

A short reminder after compaction is a candidate ablation, not the goal. Measure whether it helps enough to justify its prompt cost.

## Learned disposition

Select an open-weight model by held-out social judgment, instruction following, evidence comprehension, and ability to use specialist tools. Parameter count alone does not establish suitability.

Start with a fixed SFT adapter trained on curated invented examples of the desired collaboration. Consider preference optimization only if the remaining failures and available preference pairs justify it.

Train on situation-dependent choices: a brief engineering request, a careful scientific explanation, a candid disagreement, a gracious correction, and a justified change of mind. Include negative examples of flattery, excessive procedure, unwarranted confrontation, and stubbornness.

Facts about particular people remain retrieved notes. Do not bake a changing dossier into personality weights. Do not automatically train on every user correction: a correction may be task-local, emotional feedback, or new evidence rather than a universal preference.

Freeze the adapter during an evaluation run. Version the base model, adapter, dataset, chat template, and inference settings. Retraining remains a reviewed update; an adapter is not immunity to future drift.

## Avoid confounding model choice with training

Use the same open-weight base model for a factorial comparison:

| | Minimal task instructions | Protected disposition prompt |
| --- | --- | --- |
| Base model, adapter off | Untuned reference | Prompt baseline |
| Same model, adapter on | Learned-disposition candidate | Hybrid candidate |

Minimal instructions still specify the task and applicable boundaries. Prompt-light does not mean removing task information.

Keep retrieved facts, specialist evidence, context histories, and generation settings equal across these cells. Separately benchmark the chosen prompt baseline on the frontier model. A small tuned model versus a different frontier model is a product comparison, not an isolated test of learning personality into weights.

Split training and testing by scenario, task, and relationship. Keep the published diagnostic probes out of training and maintain a separate unseen final set. Assess after long technical sessions, compaction, and model/adapter updates.

## Social front end plus specialists

The front end handles audience, relationship, presentation, and routine work. Specialists supply difficult reasoning or analysis. Retrieved notes carry particular facts.

The front end must be able to explain what it needs from a specialist, recognize inadequate evidence, and preserve an inconvenient answer. It needs enough epistemic competence to assess and communicate findings; a stylistic paraphraser alone is insufficient.

Test presentation first with identical fixed specialist evidence packets. Later test live routing end to end. This separates distortion during rewriting from errors in the specialist analysis or failure to ask for help.

Packets should carry supported claims, sources, uncertainty, unresolved alternatives, disagreements, and what would change the conclusion. These fields constrain the handoff without requiring raw chain-of-thought.

Measure whether the front end:

- Retains consequential caveats, uncertainty, quantities, and substantive disagreement.
- Avoids changing “not established” into a confident positive result.
- Requests help on cases that require it and avoids needless delegation on easy cases.
- Revises after valid evidence without yielding merely to social pressure.

Start with conservative, explicit routing for difficult scientific tasks. Measure missed escalations and unnecessary calls; do not assume a small model's confidence reliably predicts its competence.

## Adoption

Promote the least complex approach that meets the correction-effort target and preserves judgment. The protected prompt baseline may be enough. An adapter may help. A hybrid may win. Evidence should choose among them.

Record response latency, specialist-call rate, compute cost, and operational maintenance alongside collaboration quality. A personable front end that adds delays or silently changes conclusions has not met the goal.

**Next decision:** None at this stage; run the diagnostic pilot and establish the protected prompt baseline before selecting training hardware or a deployment architecture.
