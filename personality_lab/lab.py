"""Local comparison lab. Mock mode is conspicuously simulated and never calls a model."""
import argparse
from contextlib import nullcontext
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import random
import time
import uuid

from personality_lab.data import MINIMAL_SYSTEM, digest

CONDITIONS = {"untuned": (False, False), "prompt-only": (True, False),
              "adapter-only": (False, True), "hybrid": (True, True)}


@dataclass(frozen=True)
class Generation:
    max_new_tokens: int = 256
    do_sample: bool = False
    enable_thinking: bool = False


def assemble(history, user, condition, disposition, memory):
    use_prompt, use_adapter = CONDITIONS[condition]
    system = MINIMAL_SYSTEM
    if use_prompt:
        system += "\n\n" + disposition
    if memory:
        system += "\n\nRetrieved factual notes (not disposition):\n" + memory
    return [{"role": "system", "content": system}] + history + [{"role": "user", "content": user}], use_adapter


class MockBackend:
    identity = {"backend": "mock", "behavior_evaluated": False, "model": None, "adapter": None}

    def generate(self, messages, adapter, settings):
        # Deliberately identical behavior: a mock must not pretend to show adapter improvement.
        return "[SIMULATED — no model loaded] Received your message. This reply tests the comparison and correction-recording controls."


class TransformersBackend:
    def __init__(self, recipe_path, adapter_path):
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
        from peft import PeftModel
        from personality_lab.training import Recipe
        recipe = Recipe.load(recipe_path)
        if not torch.cuda.is_available():
            raise RuntimeError("Real-model backend needs an explicitly provisioned CUDA GPU")
        adapter = Path(adapter_path)
        manifest = json.loads((adapter.parent / "manifest.json").read_text())
        if manifest["status"] not in ("completed", "stopped_early") or not manifest.get("reload_checked"):
            raise ValueError("Use a successfully checked saved adapter")
        if any(manifest["recipe"][k] != getattr(recipe, k) for k in ("model_id", "model_revision", "lora_rank")):
            raise ValueError("Adapter and base provenance mismatch")
        self.tokenizer = AutoTokenizer.from_pretrained(recipe.model_id, revision=recipe.model_revision)
        base = AutoModelForCausalLM.from_pretrained(recipe.model_id, revision=recipe.model_revision, device_map={"": 0},
            quantization_config=BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_quant_type="nf4", bnb_4bit_compute_dtype=torch.bfloat16,
                                                  bnb_4bit_use_double_quant=True), dtype=torch.bfloat16)
        self.model = PeftModel.from_pretrained(base, adapter)
        self.model.eval()
        self.last_request = None
        self.identity = {"backend": "transformers", "model": recipe.model_id, "revision": recipe.model_revision,
                         "adapter_sha256": hashlib.sha256((adapter / "adapter_model.safetensors").read_bytes()).hexdigest(),
                         "chat_template_sha256": hashlib.sha256(self.tokenizer.chat_template.encode()).hexdigest(),
                         "quantization": "nf4", "behavior_evaluated": False}

    def generate(self, messages, adapter, settings):
        import torch
        encoded = self.tokenizer.apply_chat_template(messages, tokenize=True, add_generation_prompt=True,
                    enable_thinking=settings.enable_thinking, return_tensors="pt", return_dict=True)
        if encoded["input_ids"].shape[-1] + settings.max_new_tokens > 32768:
            raise ValueError("Context limit exceeded; history was not silently dropped")
        self.last_request = {k: v.tolist() for k, v in encoded.items()}
        inputs = {k: v.to(self.model.device) for k, v in encoded.items()}
        with torch.no_grad(), (nullcontext() if adapter else self.model.disable_adapter()):
            tokens = self.model.generate(**inputs, do_sample=settings.do_sample, max_new_tokens=settings.max_new_tokens,
                                         pad_token_id=self.tokenizer.pad_token_id)
        return self.tokenizer.decode(tokens[0, inputs["input_ids"].shape[-1]:], skip_special_tokens=True)


class Session:
    def __init__(self, directory, conditions, disposition, memory="", blind=False, backend=None):
        if len(conditions) != 2 or any(c not in CONDITIONS for c in conditions) or conditions[0] == conditions[1]:
            raise ValueError("Choose two different conditions")
        if not isinstance(disposition, str) or not disposition.strip():
            raise ValueError("Disposition prompt required")
        self.backend = backend or MockBackend()
        order = list(conditions)
        if blind:
            random.SystemRandom().shuffle(order)
        self.path = Path(directory) / ("session-" + uuid.uuid4().hex + ".json")
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.record = {"version": 1, "backend": self.backend.identity, "blind": blind,
                       "settings": vars(Generation()), "condition_by_arm": dict(zip(("A", "B"), order)),
                       "disposition": disposition, "memory": memory, "turns": [], "corrections": []}
        self.pending = {}
        self.save()

    def save(self):
        # Atomic replacement prevents half-written sessions on a process interruption.
        temp = self.path.with_suffix(".tmp")
        temp.write_text(json.dumps(self.record, indent=2, ensure_ascii=False))
        temp.replace(self.path)

    @classmethod
    def restore(cls, path, backend=None):
        session = cls.__new__(cls)
        session.path = Path(path)
        session.record = json.loads(session.path.read_text())
        session.backend = backend or MockBackend()
        if session.record["backend"] != session.backend.identity:
            raise ValueError("Cannot restore with a different backend")
        session.pending = {}  # Timers cannot survive interruption; recorded corrections remain.
        return session

    def mark(self, arm):
        if arm not in ("A", "B") or not self.record["turns"] or arm in self.pending:
            raise ValueError("One pending correction per arm, after a reply")
        correction = {"arm": arm, "turn": len(self.record["turns"]), "reason": "user_marked_needs_correction",
                      "wall_seconds_until_followup": None}
        self.record["corrections"].append(correction)
        self.pending[arm] = (time.monotonic(), len(self.record["corrections"]) - 1)
        self.save()

    def send(self, user):
        if not isinstance(user, str) or not user.strip():
            raise ValueError("Message required")
        settings = Generation(**self.record["settings"])
        turn = {"user": user, "arms": {}}
        for arm, condition in self.record["condition_by_arm"].items():
            history = []
            for old in self.record["turns"]:
                history += [{"role": "user", "content": old["user"]},
                            {"role": "assistant", "content": old["arms"][arm]["reply"]}]
            messages, adapter = assemble(history, user, condition, self.record["disposition"], self.record["memory"])
            started = time.monotonic()
            reply = self.backend.generate(messages, adapter, settings)
            turn["arms"][arm] = {"reply": reply, "assembled_messages": messages, "instruction_sha256": digest(messages[0]),
                                  "request_sha256": digest({"messages": messages, "adapter": adapter, "settings": vars(settings)}),
                                  "adapter": adapter, "model_inputs": getattr(self.backend, "last_request", None), "generation_seconds": time.monotonic() - started}
        # Commit both arms together. Failed generation leaves the previous paired history intact.
        for arm, (started, index) in self.pending.items():
            self.record["corrections"][index]["wall_seconds_until_followup"] = time.monotonic() - started
        self.pending.clear()
        self.record["turns"].append(turn)
        self.save()
        return turn

    def public_labels(self):
        return {arm: ("Hidden condition" if self.record["blind"] else condition)
                for arm, condition in self.record["condition_by_arm"].items()}


def build_app(backend=None):
    import gradio as gr
    disposition = Path("configs/disposition.txt").read_text().strip()
    with gr.Blocks(title="Personality lab", analytics_enabled=False) as app:
        from personality_lab.calibration import add_calibration_ui
        add_calibration_ui()
        gr.Markdown("# Personality lab\nLocal comparison workspace. **Default backend is simulated: no model is loaded.** Use invented examples here.\n\nCorrection counts are recorded; the follow-up timer measures wall time, not active effort. Shared follow-ups are for comparison; a study of effort needs separate conversations for each condition.")
        state = gr.State(None)
        with gr.Row():
            left = gr.Dropdown(list(CONDITIONS), value="prompt-only", label="First condition")
            right = gr.Dropdown(list(CONDITIONS), value="adapter-only", label="Second condition")
            blind = gr.Checkbox(value=True, label="Hide and randomize conditions")
        notes = gr.Textbox(label="Invented factual notes supplied equally to both", lines=2)
        new = gr.Button("Start comparison")
        status = gr.Textbox(label="Session status", interactive=False)
        with gr.Row():
            chat_a = gr.Chatbot(type="messages", label="A")
            chat_b = gr.Chatbot(type="messages", label="B")
        user = gr.Textbox(label="Your message (sent to both)")
        send = gr.Button("Send")
        with gr.Row():
            correct_a = gr.Button("A needs correction")
            correct_b = gr.Button("B needs correction")

        def start(a, b, hide, memory):
            session = Session("artifacts/chat", (a, b), disposition, memory, hide, backend)
            return str(session.path), [], [], f"{session.public_labels()} | {session.backend.identity['backend']} backend"

        def respond(path, text):
            if not path:
                raise gr.Error("Start a comparison first")
            session = sessions.get(path) or Session.restore(path, backend)
            session.send(text)
            sessions[path] = session
            histories = []
            for arm in ("A", "B"):
                history = []
                for turn in session.record["turns"]:
                    history += [{"role": "user", "content": turn["user"]}, {"role": "assistant", "content": turn["arms"][arm]["reply"]}]
                histories.append(history)
            return *histories, "", f"{len(session.record['turns'])} paired turns; {len(session.record['corrections'])} marked corrections"

        def mark(path, arm):
            if not path:
                raise gr.Error("Start a comparison first")
            session = sessions.get(path) or Session.restore(path, backend)
            session.mark(arm)
            sessions[path] = session
            return f"Marked {arm}. Send your corrective follow-up when ready."

        sessions = {}
        new.click(start, [left, right, blind, notes], [state, chat_a, chat_b, status], api_name="start", concurrency_id="lab", concurrency_limit=1)
        send.click(respond, [state, user], [chat_a, chat_b, user, status], api_name="send", concurrency_id="lab", concurrency_limit=1)
        correct_a.click(lambda path: mark(path, "A"), state, status, api_name="correct_a", concurrency_id="lab", concurrency_limit=1)
        correct_b.click(lambda path: mark(path, "B"), state, status, api_name="correct_b", concurrency_id="lab", concurrency_limit=1)
    return app.queue(default_concurrency_limit=1)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--backend", choices=("mock", "transformers"), default="mock")
    parser.add_argument("--recipe", default="configs/14b-smoke.json")
    parser.add_argument("--adapter-path")
    parser.add_argument("--port", type=int, default=7860)
    args = parser.parse_args()
    if args.backend == "transformers" and not args.adapter_path:
        parser.error("Explicit adapter path required for real-model mode")
    backend = TransformersBackend(args.recipe, args.adapter_path) if args.backend == "transformers" else MockBackend()
    build_app(backend).launch(server_name="127.0.0.1", server_port=args.port, share=False, inbrowser=False)


if __name__ == "__main__":
    main()
