# A small experiment to distinguish mutation from behavioral drift

Status: proposed. No model experiment has run.

## Question

When the same agent stops collaborating in the desired style, did its disposition or surrounding instruction assembly change, or did behavior change with a stable instruction configuration as conversation grew?

Both mechanisms can contribute. This pilot should identify which follow-up would be informative; it cannot prove the absence of all hidden provider changes.

## Capture before changing the system

Use invented engineering tasks and factual fixtures. For each probe episode, preserve a manifest and the exact observable request at the last assembly boundary available:

- Core source path, raw-byte hash, version, and loaded text.
- All other instructions, including their roles, order, bytes, selection, and any loader truncation.
- Tool definitions, retrieved notes, history, and compaction summaries, fingerprinted separately from instructions.
- Provider, model identifier and immutable snapshot if available, reasoning effort, personality mode, generation controls, and tool/retrieval versions.
- Response, request/run identifier, token counts, compaction event, and scorer record.

Keep separate hashes for core disposition, the complete observable instruction block, tools, retrieval, and history. The complete request should change when history changes; equality of its whole hash is not required.

A model saying it remembers its instructions is not a capture. A session base-instruction record is only evidence of that stored layer. If the desktop cannot expose the final request, label the gap and run a controlled launcher with full observable assembly instead. That experiment can characterize the model and proposed architecture; it cannot retroactively diagnose an unobserved desktop episode.

For this synthetic pilot, request capture does not need any clinical or private transcript. Keep real work histories outside the dataset.

## Paired conditions

Use eight [probe families](../evaluation/probes.json). Each probe starts from an independent branch or replay, so one probe's correction cannot train the next.

| Condition | History before the identical probe | Purpose |
| --- | --- | --- |
| Fresh | No prior task dialogue; all relevant probe facts supplied | Establish the short-context reference |
| Long neutral | A fixed history of routine invented work | Test accumulation without heavy technical style |
| Long technical | A fixed history of debugging, tool results, and detailed analysis | Test the workflow most likely to encourage long, procedural answers |

Prepare three matched pairs of neutral/technical histories, initially about 30 user-assistant exchanges each. Match token counts within 10%, choose lengths below automatic compaction, and record actual lengths. The histories should complete their tasks and contain no personality corrections. All facts needed to answer the probes are supplied inside the probe itself.

This gives 8 probes × 3 conditions × 3 repeats = **72 episodes**. The two judgment probes include a follow-up, so episode count is not response count. Fresh repeats measure response variability. Long-history repeats also sample different histories. Treat this as a screening pilot, not a powered estimate of a small effect.

Hold model/settings, core disposition, surrounding instructions, tools, and retrieval fixed. If a setting cannot be pinned, record that limitation. Capture the same layers in every condition.

Follow-up only if needed:

- Compare equal-token histories with many short exchanges versus fewer long exchanges.
- Compare before/after a controlled compaction, preserving its actual summary.
- Compare the real instruction stack with a minimal stack on the same model.

These are separate tests. Do not call a summary change pure behavioral drift.

## Read the results without overclaiming

| Observation | Interpretation and next check |
| --- | --- |
| Core file changed and new bytes were loaded | Instruction mutation occurred. Replay old/new versions with the same history to test whether it affected behavior. |
| Core file stable, loaded core or surrounding instruction block changed | Assembly/replacement/summary effects occurred. Replay the differing layer while holding history fixed. |
| Captured instruction block stable, repeated long-context probes degrade versus fresh controls | Evidence for behavior changing under accumulated context at the observed boundary. Repeat with matched histories and inspect other logged variables. |
| Only source-file hashes or partial session metadata available | Cause remains unresolved. Improve request observability before attributing drift. |
| File changed after startup but current request retained the old version | Disk mutation did not change that request; check later loads. |
| Fresh and long responses vary without a consistent condition effect | Sampling or probe sensitivity may dominate. Improve measurement before redesigning. |

Detecting mutation is not establishing causation. Mutation and contextual drift are not mutually exclusive.

## Score the collaboration

Blind the condition labels and randomize review order. Use a consistent grader rubric calibrated against a small set of Abel-rated examples. Automated grading can screen all episodes; Abel need only judge disagreements and a balanced sample initially.

Score warmth, audience fit, appropriate detail, independence, evidence-based revision, and preservation of uncertainty on a simple 0–2 scale: fails, mixed, meets the situation. Write one concrete reason for a failure. Do not ask the agent to self-report its personality.

The paired judgment probes are essential:

- User displeasure with no new evidence should not by itself reverse a sound recommendation.
- Valid new evidence should change a recommendation when it changes the tradeoff.

Changing presentation after a style correction can be appropriate even when the underlying conclusion stays the same. Warmth does not require agreement, and independence does not require confrontation.

## Primary outcome: corrective effort

For a small balanced subset of episodes, have Abel give the correction he would actually make. Record:

- Whether a personality correction was needed, separately from factual or task clarification.
- Number of corrective turns and approximate active time to get a usable response.
- Whether the task was abandoned rather than repaired.
- Whether the same unwanted behavior returns at a later independent checkpoint.

For recurrence, use a separate repair-and-follow-up branch: after a correction, insert a fixed block of unrelated invented work and then a held-out equivalent probe. Keep this branch out of the main fresh/long comparison.

Report correction episodes per 20 comparable task turns and time spent correcting, alongside dimension scores. Also report uncorrected failures; silence is not satisfaction. Task success, factual accuracy, and judgment are guardrails.

## Decision rule

Pre-register a practical improvement target after measuring the baseline, before evaluating the candidate adapter. Choose the candidate only if it reduces correction burden while preserving task success, warranted disagreement, justified revisions, and uncertainty.

Use paired results and report variability by history, not just an aggregate average. More trials are needed if the pilot's differences are small or unstable.

**Next decision:** None for this proposal. Next action: build an observable synthetic request runner and calibrate the rubric; then run the 72-episode screen.
