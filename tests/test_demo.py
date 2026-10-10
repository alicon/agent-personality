from pathlib import Path
import json
import tempfile
import unittest

from personality_lab.demo import load_cases
from personality_lab.lab import CONDITIONS
from personality_lab.recorded_demo import read_demo, save_review


class DemoTests(unittest.TestCase):
    def test_feedback_preserves_condition_identity_without_approving_training(self):
        record = {"model_id": "test-only", "adapter_sha256": "test-digest"}
        index = {"case": {condition: {"reply": condition, "stop_reason": "length"} for condition in CONDITIONS}}
        with tempfile.TemporaryDirectory() as directory:
            review = save_review(record, index, "case", "hybrid", "prompt-only", "Neither works", "Too much certainty", directory)
            self.assertEqual(review["left_condition"], "hybrid")
            self.assertEqual(review["replies"]["prompt-only"]["stop_reason"], "length")
            self.assertFalse(review["training_approved"])
            self.assertEqual(len(list(Path(directory).glob("*.json"))), 1)
            for left, right, choice in (("hybrid", "hybrid", "Left"), ("unknown", "prompt-only", "Left"), ("hybrid", "prompt-only", None)):
                with self.assertRaises(ValueError):
                    save_review(record, index, "case", left, right, choice, "", directory)

    def test_saved_viewer_rejects_missing_or_mislabeled_conditions(self):
        record = {"status": "completed", "data_origin": "wholly_invented", "cases": [{"id": "case", "user": "invented"}],
                  "replies": [{"case_id": "case", "condition": condition, "reply": condition, "stop_reason": "eos"}
                              for condition in CONDITIONS]}
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "demo.json"
            path.write_text(json.dumps(record))
            _, index = read_demo(path)
            self.assertEqual(index["case"]["adapter-only"]["reply"], "adapter-only")
            for replies in (record["replies"][:-1], record["replies"] + record["replies"][:1],
                            [dict(record["replies"][0], case_id="wrong")] + record["replies"][1:]):
                path.write_text(json.dumps(dict(record, replies=replies)))
                with self.assertRaises(ValueError):
                    read_demo(path)

    def test_cases_are_development_only_and_outside_training_and_final_probes(self):
        cases = load_cases()
        self.assertEqual(len(cases), 4)
        training = [json.loads(line) for line in Path("data/development.jsonl").read_text().splitlines()]
        probes = json.loads(Path("evaluation/probes.json").read_text())["probes"]
        excluded = {message["content"] for row in training for message in row["messages"]}
        excluded.update(turn for probe in probes for turn in probe["user_turns"])
        self.assertFalse(excluded & {case["user"] for case in cases})

    def test_unbounded_or_noninvented_demo_input_is_rejected(self):
        source = json.loads(Path("data/demo-prompts.json").read_text())
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "cases.json"
            for content in (dict(source, origin="customer_transcript"), dict(source, cases=[]),
                            dict(source, cases=source["cases"] * 2)):
                path.write_text(json.dumps(content))
                with self.assertRaises(ValueError):
                    load_cases(path)
