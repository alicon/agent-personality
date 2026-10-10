# How much buys a useful prototype?

October 10, 2026. These are planning ranges, not spending authorization or measured runtimes. No paid model training has run.

A $1,000–$2,000 campaign can support meaningful adapter experiments on an existing 14B model. We are adapting a model whose language and reasoning capabilities were already trained, rather than paying to pretrain those capabilities ourselves. That makes this budget materially different from the cost of building a foundation model.

The current Hugging Face rate is $2.50/hour for an 80 GB A100: forty GPU hours cost $100 and two hundred cost $500. Actual completed work per hour still needs measurement. Setup, downloads, uploads, failed attempts, evaluation, and serving all consume resources. [Official pricing](https://huggingface.co/docs/hub/jobs-pricing).

| Cumulative planning budget | Realistic objective | What it cannot establish by itself |
| --- | --- | --- |
| Below $100 | Validate the pipeline and try a small development adapter on the actual target model | Durable personality or an advantage over prompting |
| Roughly $300–$700 | A first meaningful 14B prototype, curated examples, iterations, and a fair development comparison with a tuned prompt | General effectiveness, publication quality, or commercial demand |
| $1,000–$2,000 | A focused comparative study with repeated training seeds, unseen cases, long histories, and some independent review | Journal acceptance or a production-ready product |

These ranges assume we supply substantial engineering and curation labor ourselves. They exclude the value of that labor. Dataset size alone is not a quality target; a few thousand well-chosen episodes can be more informative than a large set of repetitive stylistic rewrites. The first fifty episodes are intentionally tiny, unreviewed fixtures.

There is research showing that fine-tuning and preference optimization can influence measured personality more effectively than prompting in their tested settings. BIG5-CHAT still used trait instructions in evaluations and did not establish our desired reduction in correction effort during scientific work. It supports trying the experiment, not assuming its result. [BIG5-CHAT](https://arxiv.org/abs/2410.16491).

Personality training is narrower than learning difficult scientific reasoning from scratch, but audience awareness and sound disagreement depend on understanding the task. A charming response that drops a caveat is a failure. Warmth training has increased sycophancy in published experiments, so judge accuracy and independence separately from friendliness. [Oxford warmth-training research](https://syntheticsociety.oii.ox.ac.uk/research/warm-llm/).

Start by checking that the untuned 14B model can handle our invented scientific tasks. Then compare prompt-only, adapter-only, and hybrid conditions on that same base. A stronger model can be a separate product reference, but it does not isolate what the adapter contributed. If 14B fails because of analytical capability, a measured larger-model comparison is more useful than buying more epochs on an incapable base. If a strong prompt wins, that is a useful result for the harness and paper too.

Before expanding the prototype budget, inspect actual throughput, held-out replies, recurring corrections, and whether uncertainty and warranted revisions survive training. More GPU time cannot repair an unclear target or a biased comparison.

Serving is a separate financial question. At the same hourly rate, leaving one A100 rented continuously for thirty days would cost about $1,800 in GPU time. Training a reusable adapter can be cheap while an always-on demo is expensive. Use bounded sessions for this hobby phase; customer-hosted serving needs its own sizing and cost model.

**Next decision:** None for spending now. Next action: finish the preparation checks and measure real GPU throughput before proposing a larger prototype envelope.
