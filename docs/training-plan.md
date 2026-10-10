# Build a personality lab, then a paper

Date: October 10, 2026. Status: build and study plan; [local implementation and first run review](build-review.md) ready. [Local login and private Hub repositories](setup.md) are ready under abelcable; no GPU jobs, model training, or billing changes have been performed by the agent.

Abel wants the enjoyment of training a real model now, with a publication and potential business asset as longer-term goals. The planning budget is $1,000–$2,000 using rented GPUs. That range is not authorization to spend.

The current execution phase is [local preparation and short smoke tests below $100](preparation-phase.md), with a $90 working limit and $9 billing reserve across the whole phase. Build locally before funding compute. This preparation phase precedes the full corpus and research campaign described below.

## The first thing to build

A private personality lab: train an adapter for Qwen3-14B, save it as a versioned artifact, and chat with the same model with the adapter off or on. Add prompt-only and combined conditions, plus a blind comparison mode.

The first milestone is a working learned checkpoint and an enjoyable chat interface. It does not wait for a complete diagnosis of past Codex drift. Capture model, instructions, dataset, and generation settings in the lab so the experiment is useful from its first run.

The lab should expose training loss, checkpoint selection, response comparisons, and a simple way to mark “this needs correcting.” A loss curve is evidence that optimization ran; held-out behavior establishes whether the adapter learned something useful.

## What numerical memory means here

LoRA learns additional numerical matrices applied inside the model. The original model can remain frozen while the adapter learns tendencies from examples. QLoRA loads the frozen base in 4-bit precision to reduce training memory. This is different from sending the model a longer personality script. [Hugging Face PEFT integration](https://huggingface.co/docs/trl/peft_integration).

The useful analogy is procedural disposition: how to speak to a colleague, decide how much detail a situation needs, and preserve a sound disagreement. It is not a dependable diary or lookup table. Particular facts and session continuity belong in a separate local memory service.

Training changes the probabilities of behavior; it does not guarantee that a trait is permanently fixed. Test generalization to unseen contexts and long work sessions.

## Recommended setup

| Component | Recommendation | Reason |
| --- | --- | --- |
| Model | Qwen/Qwen3-14B, the post-trained chat model | A substantial, accessible starting point with a compatible Hugging Face stack |
| First training GPU | One A100 with 80 GB on Hugging Face Jobs | Headroom for debugging and longer examples without beginning with multi-GPU orchestration |
| Learning | Supervised fine-tuning with a QLoRA adapter; preference optimization as a second experiment | First teach good examples, then test whether preference pairs improve the remaining failures |
| Libraries | PyTorch, Transformers, Datasets, PEFT, TRL, bitsandbytes, Accelerate | Standard tools that organizations can run themselves |
| Interface | Gradio with adapter and checkpoint controls | Immediate interaction and blind comparisons |
| Artifacts | Private Hugging Face model/dataset repositories and persistent checkpoints | Versioned, reusable outputs from the hobby build |
| Customer execution | The same training/evaluation package inside customer infrastructure | The commercial method should not depend on uploading customer examples to our lab |

The model card lists Apache-2.0, 14.8 billion parameters, a native 32,768-token context, and a non-thinking mode. Pin the model revision and use the same thinking mode across evaluation conditions. This is a pragmatic starting model, not a claim that it is the newest or best. [Model card](https://huggingface.co/Qwen/Qwen3-14B).

Public Hub metadata checked in this session reported revision 40c069824f4251a91eefaf281ebe4c544efd3e18 for 14B and b968826d9c46dd6066d109eabc6255188de91218 for the optional Qwen3-8B replication. Both were public and ungated. Reconfirm the selected revision before the first run.

The current implementation pins the image and resolves Linux dependencies before the first environment smoke. It uses Transformers Trainer with tested assistant masks; TRL and preference optimization remain later work. Confirm runtime compatibility and preserve the working environment after a successful smoke test. Do not use moving package or model branches for the paper runs.

## Accounts and setup Abel needs

1. Completed: Abel supplied the [abelcable account](https://huggingface.co/abelcable) and authorized local browser/device login. [Setup record](setup.md).
2. Wait to fund compute until the first smoke run is concrete and reviewable. Choose the smallest practical initial credit purchase then; account funding and actual job spending are distinct. Do not enable automatic refills.
3. Completed: local CLI authentication and private model/dataset repository creation. Check Jobs authorization separately before the first run. Keep credentials in local login or job secrets, outside chat. [Token documentation](https://huggingface.co/docs/hub/security-tokens).
4. Approve a concrete first run after the trainer, dataset, expected runtime, and cost cap are reviewable.

GitHub is already available. No second GPU-cloud account is required for the recommended path. Hugging Face PRO is optional: current Jobs documentation allows any account with a positive compute-credit balance. Jobs eligibility and GPU availability still need an authenticated check for the new account. [Jobs pricing and billing](https://huggingface.co/docs/hub/jobs-pricing).

I can prepare the code, dataset tools, recipes, and interface before account setup finishes. Account creation, payment details, and granting account access belong to Abel.

## Training data: teach judgment, not a catchphrase

Begin with about 3,000 curated synthetic dialogue episodes. Expand toward 5,000–10,000 only if coverage and held-out failures justify it. These are proposed corpus sizes, not estimates of the minimum necessary data.

Include invented molecular-diagnostics assay-development and bioinformatics collaboration cases as the proposed commercial focus. The [market landscape](market-landscape.md) defines the first workflow: preserve the scientific meaning of an investigation while adapting an engineering handoff and a leadership update to their audiences. Keep broader scientific cases to assess whether improvements transfer.

Cover engineering requests, executive updates, scientific uncertainty, computational debugging, disagreement under social pressure, valid revisions, casual warmth, and switching between brief and detailed work. Include multi-turn examples in which the same undesirable behavior must not recur after unrelated technical work.

Use the [commercial north star](product-north-star.md) to choose situations: the agent should understand professional context and conserve employee attention.

Start with roughly 30 anchor examples or judgments from Abel in one calibration session. Generate candidate examples from that rubric, then have Abel review a sampled set and ambiguous cases. This bounds the human curation burden; it does not assume automatically generated examples are all good.

Each episode needs a scenario group, audience/relationship context, provenance, and a target response. For preference training, add genuinely comparable preferred/rejected responses. Split by scenario family before generating variations. Keep the existing diagnostic probes and a new unseen final set out of training.

Train on assistant responses, with audience and task facts in the input. Use a minimal constant system instruction for the primary adapter experiment; do not feed the desired personality paragraph to every training example and then claim the adapter no longer needs it. Hugging Face TRL supports assistant-only training, with chat-template support that must be checked in the pinned environment. [SFT Trainer](https://huggingface.co/docs/trl/sft_trainer).

Keep all pilot examples invented. Customer editions can use the organization's permitted examples locally; that does not authorize training on protected clinical values under Adela's existing policy.

## First training recipe

Provisional settings: rank-32 LoRA, 4-bit NF4 base loading, bfloat16 adapter computation, assistant-only loss, gradient checkpointing, sequence length initially 4,096, and a modest learning-rate search around 1e-4. Start with one epoch and select further training using validation behavior rather than training loss alone.

These settings are a starting recipe, not a validated configuration. Check masks, trainable-parameter counts, finite loss, VRAM, and saved-adapter reload on a short smoke run. Then time representative batches before estimating the full run.

Save checkpoints outside the Job's ephemeral disk. Hugging Face documents that Job disk disappears at termination; mounted buckets or Hub uploads preserve artifacts. Use timeouts and explicit job cancellation. [Training on Jobs](https://huggingface.co/docs/hub/jobs-training).

The first full run should produce an adapter, a model card, a dataset manifest, a software/environment manifest, and saved answers to held-out probes. The base model stays separate so adapter-off remains a real control.

## Budget

Current published Jobs rates include an 80 GB A100 at $2.50/hour and a 48 GB L40S at $1.80/hour. Thus 20 A100 hours cost $50 in GPU charges; 100 hours cost $250. Storage, inference services, and any additional subscriptions are separate. Rates and availability should be rechecked at launch. [Official rates](https://huggingface.co/docs/hub/jobs-pricing).

Suggested allocation for a $1,500 campaign:

| Purpose | Planning allowance |
| --- | ---: |
| Training, debugging, and repeated seeds | $350 |
| Evaluation inference and long-context runs | $350 |
| Optional synthetic generation and independent model grading | $150 |
| Independent human ratings / interaction pilot | $300 |
| Artifact storage and occasional demo serving | $50 |
| Contingency and reviewer-requested experiments | $300 |
| Total | $1,500 |

These are envelopes, not service quotes or a promise of publication-quality results at that cost. Runtime depends on tokens, hardware throughput, and experiment scope. Use the $1,000 end for one primary model and a narrower study; use up to $2,000 for replication and extra human validation. Do not run an always-on GPU endpoint by default.

For the current preparation phase, use the [staged budget and stop rules](preparation-phase.md). Target $20–$40 cumulatively, enforce the $90 working limit with a $9 reserve, and limit any proposed individual GPU job to two hours and $5 of GPU charges. A provider timeout limits one job, not the whole campaign; record and reconcile cumulative costs. The local launcher now reserves cumulative liability atomically and requires the reviewed source/specification digest. Its provider interactions are tested with mocks; the first approved live environment check passed. GPU model training remains untested; see the [run record](runs/2026-10-10-environment.md).

A [cost feasibility note](cost-feasibility.md) separates a useful prototype from a convincing comparative study. [Personality calibration](personality-calibration.md) captures Abel’s preferences before expanding the corpus.

## From the toy to a paper

Working question: **Does learned disposition reduce the human cost of maintaining an agent's working style during extended scientific and computational collaboration?**

The main experiment uses the same base model:

| Condition | Disposition prompt | Learned adapter |
| --- | --- | --- |
| Untuned reference | Minimal task instructions | Off |
| Prompt-only | Tuned personality instructions | Off |
| Adapter-only | Minimal task instructions | On |
| Hybrid | Same tuned personality instructions | On |

Use identical model revisions, quantization, task facts, memory retrieval, tools, chat templates, output limits, and generation settings. Give the prompt-only baseline a fair validation-time tuning budget and a few-shot baseline drawn from the same training corpus. Do not compare a polished adapter with one careless prompt.

Keep SFT and SFT-plus-preference-training as separate results. Start with 14B, then replicate selected findings at 8B if budget permits. Target three independent adapter-training seeds for the main learned conditions.

Develop approximately 120 held-out scenario groups across the professional situations above. Use fresh, moderate, and long histories, with defined token lengths rather than turn counts alone. Branch probes independently. Freeze the final test set and analysis plan after the development pilot and before the main run.

Primary outcome: corrections and active correction time needed to achieve a usable result. Secondary outcomes: recurrence, audience fit, appropriate detail, warmth, sycophancy, justified revisions, uncertainty preservation, task accuracy, and latency.

Abel's evaluations establish personal fit. Add independent blinded ratings, and an interaction study with other adults if we want to claim a broader reduction in employee effort. Ratings of fixed outputs alone do not measure actual correction burden. Determine the sample size from pilot variability and the effect worth detecting; a provisional 12–20-person pilot is not an adequately powered universal study.

Treat scenario, participant, conversation, and training seed as sources of variation. Use paired contrasts with uncertainty estimates; do not count every token or follow-up turn as an independent observation. Report negative results and tradeoffs.

Cross-session continuity is a separate memory-system experiment. Hold retrieval equal in the disposition comparison, then test memory on/off independently. [LongMemEval](https://arxiv.org/abs/2410.10813) provides relevant precedent for evaluating knowledge updates, temporal reasoning, and abstention. Do not attribute retrieved facts to adapter memory.

The potential contribution is a reproducible method and benchmark for the cost of repeated social correction, with scientific-work scenarios and explicit independence/revision tests. This must be differentiated from existing personality-training and persona-consistency work. “We fine-tuned a friendly model” by itself is not the intended contribution.

## Publication path and commercial boundary

Write methods while building, then results after the frozen experiment. Preserve a reproducibility bundle with configs, scripts, data provenance, checkpoints, evaluation traces, and analysis code.

TMLR is a plausible journal to consider because its stated criteria emphasize evidence-supported claims and findings of interest, including robust reproducibility studies, rather than requiring a new state-of-the-art method. Fit depends on the actual contribution; acceptance is not assured. [Acceptance criteria](https://www.jmlr.org/tmlr/acceptance-criteria.html).

Later setup: an OpenReview profile, an ORCID if useful, and a preprint account when the manuscript is ready. TMLR requires anonymized submissions, research reporting, and human-subjects information. Establish consent and the applicable ethics-review/reporting route before recruiting participants. This does not hold up invented-data training. [Author guide](https://www.jmlr.org/tmlr/author-guide.html).

Abel owns the scientific claims, reviews sources and results, and makes the publication decisions. Disclose AI assistance according to venue policy. [TMLR FAQ](https://www.jmlr.org/tmlr/faq.html).

Keep the repository private during development. Decide the public research release separately from the commercial package and any customer-specific assets. A generic dataset and adapter may be releasable; customer documents, examples, memories, and adapters remain customer-controlled.

**Next decision:** None; prepare the next tiny-model training check for separate review after the successful environment stage.
