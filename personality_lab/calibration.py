"""Persist explicit human judgments; never automatically train from a selected reply."""
import json
from pathlib import Path
import time
import uuid

from personality_lab.data import digest


def save_choice(card, choice, reason, directory="artifacts/calibration"):
    if choice not in ("A", "B", "Both work", "Neither works"):
        raise ValueError("Select a reply or reject both")
    if card["kind"] not in ("taste", "judgment"):
        raise ValueError("Unknown calibration kind")
    result = {"card_id": card["id"], "card_sha256": digest(card), "kind": card["kind"],
              "choice": choice, "reason": reason, "recorded_at_unix": time.time(),
              "training_approved": False, "requires_review_of_factual_validity": card["kind"] == "judgment"}
    path = Path(directory) / (uuid.uuid4().hex + ".json")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result, indent=2))
    return result


def add_calibration_ui():
    import gradio as gr
    cards = json.loads(Path("data/calibration.json").read_text())["cards"]
    lookup = {card["title"]: card for card in cards}
    with gr.Accordion("Personality calibration: pick what feels right", open=False):
        gr.Markdown("These are authored examples, not model outputs. Taste questions can have several good answers; judgment questions also need factual review. Choices are saved locally and do not start training.")
        title = gr.Dropdown(list(lookup), label="Situation")
        scene = gr.Markdown()
        replies = gr.Markdown()
        choice = gr.Radio(["A", "B", "Both work", "Neither works"], label="Your preference")
        reason = gr.Textbox(label="What works, what bothers you, or your rewrite")
        save = gr.Button("Save judgment")
        status = gr.Textbox(label="Calibration status", interactive=False)
        def display(selected):
            card = lookup[selected]
            return card["scene"], f"**A**\n\n{card['A']}\n\n**B**\n\n{card['B']}"
        def record(selected, selected_choice, text):
            if not selected or not selected_choice:
                raise gr.Error("Choose a situation and a preference first")
            save_choice(lookup[selected], selected_choice, text or "")
            return "Saved locally for review. No training started."
        title.change(display, title, [scene, replies], api_name="calibration_card")
        save.click(record, [title, choice, reason], status, api_name="calibration_save")
