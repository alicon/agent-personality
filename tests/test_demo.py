from pathlib import Path
import json
import tempfile
import unittest

from personality_lab.demo import load_cases


class DemoTests(unittest.TestCase):
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
