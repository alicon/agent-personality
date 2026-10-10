# Capture personality through choices

We need to learn how the agent should behave before asking an adapter to reproduce that behavior. Trait words such as warm, independent, or concise describe the intention but leave important choices unresolved.

Use short invented situations with contrasting replies. Which reply fits the relationship? Does a joke help? How much initiative is welcome? When should the agent stop talking? Let Abel choose both or neither and write a correction. The [twelve initial cards](../data/calibration.json) are available in the local lab. They are authored examples, not outputs of a trained model or a validated psychological instrument.

Keep three questions separate:

1. **Taste:** two accurate replies can differ in warmth, directness, playfulness, or initiative. We want to learn which feels natural to work alongside.
2. **Judgment:** evidence, audience, and task constraints determine whether a reply is appropriate. User preference does not make an unsupported scientific statement true.
3. **Continuity:** the same priorities should survive topic changes and long technical work. Later examples must test persistence of judgment, while allowing warranted changes of mind.

Fiction is useful as an inspiration for recognizable priorities and habits across situations. A character can be appealing because of what they notice, what they care about, how they respond under pressure, and the limits of their patience. Those are lenses for designing original scenes; a fictional character's disposition is not automatically suitable for scientific work.

Books that explicitly explain social conventions could also inform the rubric. The working hypothesis is that they help name hidden expectations and exceptions. Reading such books alone does not demonstrate contextual social judgment, and we have not evaluated a specific book or trained on one. Broad social guidance must be checked against the actual audience and situation.

The first calibration set is deliberately small. Use it to discover disagreements and language that feels wrong, then collect roughly thirty anchors across varied situations. Add nearby counterexamples: a short engineering request versus an explanation for a newcomer; pressure without new evidence versus a real change in constraints; casual acknowledgement versus a request for practical help.

Convert reviewed anchors into training candidates only after checking factual validity and recording their provenance. Keep the final evaluation set separate. A preference record stays a record; it does not silently rewrite the live agent's instructions or automatically launch training.

Success is not reproducing Abel's favorite phrases. It is less repeated correction across new scientific and computational tasks, while retaining useful judgment.

**Next decision:** Abel can try the cards during build review. The next action is to use those judgments to revise the development examples before meaningful personality training.
