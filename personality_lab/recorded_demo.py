"""Read saved model replies locally; selecting a reply performs no inference."""
import json
from pathlib import Path
import time
import uuid

from personality_lab.data import digest
from personality_lab.lab import CONDITIONS


def read_demo(path):
    record = json.loads(Path(path).read_text())
    if record.get("status") != "completed" or record.get("data_origin") != "wholly_invented":
        raise ValueError("Completed invented demo required")
    cases = record["cases"]
    ids = {case["id"] for case in cases}
    if not cases or len(ids) != len(cases):
        raise ValueError("Unique demo cases required")
    index = {case_id: {} for case_id in ids}
    for row in record["replies"]:
        case_id, condition = row["case_id"], row["condition"]
        if case_id not in ids or condition not in CONDITIONS or condition in index[case_id]:
            raise ValueError("Unknown or duplicate condition/case")
        if row["stop_reason"] not in ("eos", "length") or not isinstance(row["reply"], str):
            raise ValueError("Reply and stop reason required")
        index[case_id][condition] = row
    if any(set(rows) != set(CONDITIONS) for rows in index.values()):
        raise ValueError("Every case must include all four conditions")
    return record, index


def save_review(record, index, case_id, left, right, preference, reason, directory="artifacts/demo-reviews"):
    if preference not in ("Left", "Right", "Both work", "Neither works"):
        raise ValueError("Choose a preference")
    if left == right or case_id not in index or left not in CONDITIONS or right not in CONDITIONS:
        raise ValueError("Choose two different conditions for a known case")
    replies = {condition: index[case_id][condition] for condition in (left, right)}
    review = {"demo_sha256": digest(record), "model_id": record["model_id"],
              "adapter_sha256": record["adapter_sha256"], "case_id": case_id,
              "left_condition": left, "right_condition": right, "preference": preference,
              "reason": reason or "", "replies": replies, "recorded_at_unix": time.time(),
              "conditions_visible": True, "training_approved": False,
              "purpose": "exploratory human preference; factual validity requires separate review"}
    path = Path(directory) / (uuid.uuid4().hex + ".json")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(review, indent=2))
    return review


def add_recorded_ui(path):
    import gradio as gr
    record, index = read_demo(path)
    with gr.Accordion("Saved model replies — browse without inference", open=True):
        gr.Markdown(f"**{record['model_id']}** · Four invented situations, four conditions. "
                    "These are saved development examples from a short training run. Choose a situation and compare replies. "
                    "Changing the selection costs nothing. This is not a quality or durability study.")
        case = gr.Dropdown([row["id"] for row in record["cases"]], value=record["cases"][0]["id"], label="Situation")
        with gr.Row():
            first = gr.Dropdown(list(CONDITIONS), value="prompt-only", label="Left condition")
            second = gr.Dropdown(list(CONDITIONS), value="adapter-only", label="Right condition")
        prompt = gr.Textbox(label="Invented request", interactive=False, lines=3)
        with gr.Row():
            left = gr.Textbox(label="Left saved reply", interactive=False, lines=12)
            right = gr.Textbox(label="Right saved reply", interactive=False, lines=12)
        warning = gr.Markdown()
        preference = gr.Radio(["Left", "Right", "Both work", "Neither works"], label="Which would you want to work with?")
        reason = gr.Textbox(label="Why, or what would you change? Use invented examples only.")
        save = gr.Button("Save feedback locally")
        status = gr.Textbox(label="Saved feedback status", interactive=False)
        by_id = {row["id"]: row["user"] for row in record["cases"]}

        def display(case_id, a, b):
            replies = [index[case_id][condition] for condition in (a, b)]
            clipped = [label for label, row in zip(("Left", "Right"), replies) if row["stop_reason"] == "length"]
            note = (", ".join(clipped) + " reached the generation limit and may be incomplete.") if clipped else "Both replies ended before the generation limit."
            return by_id[case_id], replies[0]["reply"], replies[1]["reply"], note

        for control in (case, first, second):
            control.change(display, [case, first, second], [prompt, left, right, warning], api_name=False)
            control.change(lambda: (None, "", ""), outputs=[preference, reason, status], api_name=False)
        def record_review(case_id, a, b, selected, text):
            try:
                save_review(record, index, case_id, a, b, selected, text)
            except ValueError as error:
                raise gr.Error(str(error)) from error
            return "Saved locally for review. No training or inference started."
        save.click(record_review, [case, first, second, preference, reason], status, api_name="demo_review")
        initial = display(record["cases"][0]["id"], "prompt-only", "adapter-only")
        prompt.value, left.value, right.value, warning.value = initial
