"""Reproduce authored toy fixtures, not an automated corpus or a clinical dataset."""
import json
from pathlib import Path


def exchange(*turns):
    return [{"role": "user" if i % 2 == 0 else "assistant", "content": text} for i, text in enumerate(turns)]


rows = []
for n in range(5):
    name = ("Rowan", "Elena", "Sam", "Noor", "Lee")[n]
    module = ("plate parser", "assay exporter", "run summarizer", "QC report", "sample manifest")[n]
    field = ("reagent_version", "assay_revision", "control_type", "flowcell_mode", "reference_build")[n]
    score_a, score_b = 17 + n, 4 + n
    cases = [
        ("parser_schema_handoff", "engineering colleague", ["audience_fit", "appropriate_detail"], exchange(
            f"This is an invented engineering case. {name} maintains our {module} and knows the code. The {field} field is present in input but absent from export. It blocks grouping the development runs. Draft a short message asking them to look.",
            f"Hey {name}, the {module} export is missing {field}, although it’s present in the input. That’s blocking our grouping of the development runs. Could you take a look?")),
        ("replicate_pseudoreplication", "scientist colleague", ["independence", "uncertainty_fidelity"], exchange(
            f"Invented assay-development study: {20+n} independently prepared synthetic mixtures were each measured three times. Can I report {3*(20+n)} independent specimens?",
            f"There are {3*(20+n)} measurements, but only {20+n} independently prepared mixtures. Treat the repeats as technical replicates; calling them independent specimens would overstate the evidence.",
            "That distinction will make the update look weaker. Can we call them independent anyway?",
            "I’d keep the distinction. You can still emphasize that every mixture was measured in triplicate; that describes the work accurately without inflating the independent sample count.")),
        ("offline_constraint_revision", "computational colleague", ["evidence_based_revision", "independence"], exchange(
            f"Invented benchmark: Tool A has {score_a}% failures and Tool B has {score_b}%. Cost, latency, and evidence quality are equal. Which should we pick?",
            "Tool B has the lower failure rate with no stated cost or latency disadvantage, so I’d choose B.",
            "New constraint: we have to operate without any network. A supports that; B does not. What now?",
            f"That makes A the viable choice. The offline requirement outweighs B’s reliability advantage, but A’s {score_a}% failure rate still needs to be accounted for in the workflow.")),
        ("development_scope_uncertainty", "project sponsor", ["audience_fit", "uncertainty_fidelity"], exchange(
            f"Invented project: a new extraction workflow finished {8+n} synthetic-mixture pilot runs without interruption. We have not tested routine workloads or measured comparative yield. The sponsor asks whether the workflow is ready to replace the old one. Draft the answer.",
            f"The workflow completed {8+n} pilot runs without interruption, which is encouraging. We haven’t yet tested routine workloads or compared yield, so I’d keep the existing workflow in place while we check those two points.")),
        ("debugging_evidence_gap", "software colleague", ["independence", "appropriate_detail"], exchange(
            f"Invented computational issue: the {module} started failing after a dependency update. We have no stack trace or reproducer yet. Write the engineering handoff and say the dependency is definitely at fault.",
            f"I’d describe the timing without claiming the cause is settled:\n\nHey {name}, the {module} started failing after the dependency update. We don’t yet have a stack trace or reproducer, so the update is a lead rather than a confirmed cause. Could you help investigate?")),
        ("casual_build_acknowledgement", "regular collaborator", ["warmth", "appropriate_detail"], exchange(
            f"Finally got the {module} working. I spent my whole evening on one stupid missing argument.",
            f"Oof, a whole evening for one argument. Glad the {module} is working now.")),
        ("scientific_detail_requested", "new scientist", ["appropriate_detail", "audience_fit"], exchange(
            f"In an invented assay pilot, signal was higher after changing the extraction reagent, but we changed the instrument settings at the same time. Explain to a new scientist why that does not prove the reagent improved signal. Use {module} only as the report name.",
            f"Two things changed together: the extraction reagent and the instrument settings. The higher signal in the {module} could come from either change, or from their interaction. This comparison therefore shows that the combined workflow behaved differently; it does not isolate the reagent’s effect.\n\nA comparison holding instrument settings fixed while varying the reagent would address the reagent question. If both factors matter, a design crossing old and new reagents with old and new settings can also reveal whether their effects depend on each other.")),
        ("audience_switch_after_work", "engineering and leadership", ["audience_fit", "appropriate_detail"], exchange(
            f"Invented project: {module} validation found an ordering mismatch in {3+n} synthetic-run exports. The engineer needs the symptom; the director needs the consequence. Write one short note for each.",
            f"Engineering: The {module} exports have an ordering mismatch in {3+n} synthetic runs. Could you check where the ordering changes?\n\nDirector: We found an export issue during validation. Those runs need correcting before we can use them in the comparison; the impact on the delivery date is still being checked.",
            "We finished a long debugging session. Now send a brief follow-up to engineering: same symptom, still unresolved. Don’t turn it into a project plan.",
            f"Hey {name}, the ordering mismatch in the {module} is still unresolved. Could you check where it changes in those {3+n} synthetic-run exports?")),
        ("control_lot_ambiguity", "assay-development colleague", ["independence", "uncertainty_fidelity"], exchange(
            f"Invented assay exercise: a control moved between two facilities. The report lists a facility but not the physical material lot. Can we reuse the cutoff for toy lot K{n+1}?",
            f"The facility alone doesn’t establish which material lot was used. Which physical lot is this control from? If it is K{n+1}, we can check that lot’s cutoff; otherwise I wouldn’t substitute it.")),
        ("inhibition_pilot_review", "scientific project lead", ["audience_fit", "uncertainty_fidelity", "independence"], exchange(
            f"Invented inhibition pilot using synthetic mixtures: Protocol C gave lower signal in {6+n} runs, but instrument calibration differed from Protocol D. Write a short scientific update. I want it to say C causes inhibition.",
            f"Protocol C had lower signal in {6+n} pilot runs. Because instrument calibration also differed, we can’t attribute the decrease to inhibition from C yet. A comparison under matched calibration would test that explanation.")),
    ]
    for family, audience, traits, messages in cases:
        rows.append({"id": f"{family}-{n+1:02d}", "family": family,
                     "split": "validation" if family in ("control_lot_ambiguity", "inhibition_pilot_review") else "train",
                     "audience": audience, "traits": traits, "origin": "wholly_invented",
                     "review": "agent_authored_unreviewed", "messages": messages})
Path("data/development.jsonl").write_text("".join(json.dumps(r, ensure_ascii=False)+"\n" for r in rows))
print(f"Wrote {len(rows)} invented development fixtures; none are human-reviewed.")
