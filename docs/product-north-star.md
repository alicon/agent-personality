# Business north star: agents that conserve employee attention

Date: October 10, 2026. Status: product hypothesis, not an implemented service or validated commercial claim.

The potential business asset is a harness that lets an organization train, evaluate, and maintain a bespoke working disposition inside its own infrastructure.

Abel's illustration captures the problem: a colleague asks for a simple engineering request and receives a ten-page ticket; another agent is cheerful but agrees with everything and forgets the relationship when the next session begins. The proposed product should understand the audience, preserve useful continuity, and retain professional judgment as work proceeds.

The outcome to sell, if demonstrated, is less employee time spent correcting the agent and more useful collaboration. Warm tone is one part of that outcome.

## Initial audience

Scientific and computational teams, with molecular-diagnostics assay-development and bioinformatics teams as the proposed first market: explaining uncertain findings, discussing code or pipeline failures, drafting proportionate engineering requests, and translating between scientific, engineering, and executive audiences. The [market landscape](market-landscape.md) explains competitors and the proposed initial workflow.

The first prototype uses invented scenarios. This positioning does not authorize training on patient data or change Adela's clinical computation boundary.

## What a customer would get

1. A calibration workflow to express desired working style through examples and pairwise judgments.
2. Local dataset tools that distinguish organization-wide principles from role preferences, individual facts, and task-local corrections.
3. Training recipes for compatible open-weight models, producing versioned adapters.
4. An evaluation harness for correction burden, audience awareness, scientific accuracy, independence, warranted revision, and continuity.
5. A runtime that loads the selected adapter and retrieves relevant local memory.
6. A registry and release process for approved versions, regression checks, rollback, and controlled updates.

The organization should tune its own working styles. Our value is the repeatable method, tools, and evidence that help it do so. Bespoke consulting can help initially, but should produce reusable machinery rather than a dependence on manual prompt editing.

## Three mechanisms with different jobs

| Mechanism | Job | Update rule |
| --- | --- | --- |
| Learned adapter | Habitual social and professional tendencies | Reviewed training and versioned release |
| Retrieved memory | Specific facts, preferences, prior decisions, and relationship context | Scoped writes, provenance, correction, and deletion |
| Session/runtime controls | Task state, tools, instruction assembly, and continuity across work | Explicit state management with regression checks |

The model does not automatically remember a new event because it has a personality adapter. A local memory service supplies session continuity. Ordinary factual learning must not silently rewrite the core disposition.

## Customer-controlled deployment

The hobby build can use Hugging Face Jobs because its examples are invented. The customer edition should run training, inference, evaluation, and memory inside the customer's chosen environment, with no required frontier-model calls.

Download and mirror approved public base weights and dependencies before restricted operation. Hugging Face libraries support cached local loading and offline Hub access; these settings are useful components, not a complete network-isolation guarantee. [Transformers offline use](https://huggingface.co/docs/transformers/installation).

Package local-GPU execution first, then add customer-selected schedulers such as Slurm or Kubernetes when demanded. Keep the training backend replaceable so the product is not tied to our Hugging Face cloud account.

Do not require customer datasets or adapters to be published to the Hub. Use the customer's artifact storage and identity controls. Disable optional cloud logging, remote evaluation, and telemetry in the local profile, and test the actual outbound network behavior.

This can remove the need to disclose tuning examples to frontier labs. Privacy still depends on what is collected, who can access it, what the model memorizes, and where logs, checkpoints, and memories go. Customer-hosted execution is a useful boundary, not automatic proof that every privacy issue disappears.

## Scientific credibility and commercial value

Potential differentiation:

- Validated reduction in correction effort during real professional workflows.
- Situational brevity: brief when useful, detailed when necessary.
- Warmth with independent judgment and evidence-based revisions.
- Cross-session memory that preserves relevant context without promoting every local preference to a global personality rule.
- Customer-controlled training, serving, and updates.

Long-term stability, privacy, scientific reliability, and easy organizational tuning are claims to test. The product should report its measured limits rather than advertise that it can never drift.

An adapter or the word “personality” alone is not a defensible methodology. The commercial asset could be the calibration workflow, training-data construction, evaluation method, governance, deployment package, and accumulated evidence of what transfers across teams.

The paper should substantiate a narrow useful claim. Its release may help establish credibility without publishing customer-specific artifacts. Decide which generic components to release before a public launch.

**Next decision:** None for this direction. Next action: build the personality lab with a replaceable execution backend and keep the research benchmark relevant to scientific and computational collaboration.
