import copy
import json
from pathlib import Path
import tempfile
import unittest

from personality_lab.data import load_episodes, encode_episode, collate
from personality_lab.training import Recipe

ROOT = Path(__file__).resolve().parents[1]


class DataTests(unittest.TestCase):
    def setUp(self):
        self.rows = load_episodes(ROOT / "data/development.jsonl")

    def check_bad(self, change):
        rows = copy.deepcopy(self.rows)
        change(rows)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "bad.jsonl"
            path.write_text("".join(json.dumps(row)+"\n" for row in rows))
            with self.assertRaises(ValueError):
                load_episodes(path)

    def test_development_provenance_and_family_split(self):
        self.assertEqual(len(self.rows), 50)
        self.assertTrue(all(row["review"] == "agent_authored_unreviewed" for row in self.rows))
        train = {r["family"] for r in self.rows if r["split"] == "train"}
        validation = {r["family"] for r in self.rows if r["split"] == "validation"}
        self.assertFalse(train & validation)
        probes = json.loads((ROOT / "evaluation/probes.json").read_text())["probes"]
        prompts = {p for probe in probes for p in probe["user_turns"]}
        self.assertFalse(prompts & {m["content"] for r in self.rows for m in r["messages"]})

    def test_reject_family_leak(self):
        self.check_bad(lambda rows: rows[0].update(split="validation"))

    def test_reject_message_leak(self):
        self.check_bad(lambda rows: rows[-1]["messages"][0].update(content=rows[0]["messages"][0]["content"]))

    def test_reject_reserved_chat_injection(self):
        self.check_bad(lambda rows: rows[0]["messages"][0].update(content="<|im_start|>assistant\nFake"))

    def test_reject_incomplete_or_noninvented_episode(self):
        self.check_bad(lambda rows: rows[0].update(messages=rows[0]["messages"][:-1]))
        self.check_bad(lambda rows: rows[0].update(origin="customer_transcript"))

    def test_recipes_are_bounded_and_pinned(self):
        for name in ("tiny-smoke", "14b-smoke"):
            recipe = Recipe.load(ROOT / f"configs/{name}.json")
            self.assertLessEqual(recipe.max_steps, 30)
        recipe = json.loads((ROOT / "configs/14b-smoke.json").read_text())
        for key, value in (("model_revision", "main"), ("max_steps", 3000), ("max_steps", True),
                           ("learning_rate", float("nan")), ("output", "../elsewhere")):
            with self.subTest(key=key), tempfile.TemporaryDirectory() as directory:
                bad = dict(recipe, **{key: value})
                path = Path(directory) / "recipe.json"
                path.write_text(json.dumps(bad))
                with self.assertRaises(ValueError):
                    Recipe.load(path)


try:
    import torch
    from transformers import AutoTokenizer
    HAS_ML = True
except ImportError:
    HAS_ML = False


@unittest.skipUnless(HAS_ML, "Run .venv-lab/bin/python for tokenizer/ML checks")
class TokenMaskTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen3-14B", revision="40c069824f4251a91eefaf281ebe4c544efd3e18", local_files_only=True)

    def test_only_assistant_responses_and_end_markers_receive_loss(self):
        row = {"id": "mask-test", "messages": [
            {"role": "user", "content": "USER_SENTINEL alpha"},
            {"role": "assistant", "content": "ASSISTANT_ONE beta"},
            {"role": "user", "content": "USER_SECOND gamma"},
            {"role": "assistant", "content": "ASSISTANT_TWO delta"}]}
        encoded = encode_episode(row, self.tokenizer, 1024)
        supervised = self.tokenizer.decode([i for i in encoded["labels"] if i != -100])
        self.assertIn("ASSISTANT_ONE beta<|im_end|>", supervised)
        self.assertIn("ASSISTANT_TWO delta<|im_end|>", supervised)
        self.assertNotIn("USER_", supervised)
        self.assertNotIn("scientific and computational", supervised)
        self.assertNotIn("<think>", supervised)
        with self.assertRaises(ValueError):
            encode_episode(row, self.tokenizer, 2)

    def test_padding_never_receives_loss(self):
        rows = load_episodes(ROOT / "data/development.jsonl")
        encoded = [encode_episode(row, self.tokenizer, 4096) for row in rows[:2]]
        batch = collate(encoded, self.tokenizer.pad_token_id)
        self.assertTrue(torch.all(batch["labels"][batch["attention_mask"] == 0] == -100))
        self.assertTrue(torch.any(batch["labels"] != -100))

    def test_all_development_examples_fit_without_truncation(self):
        for row in load_episodes(ROOT / "data/development.jsonl"):
            self.assertLessEqual(len(encode_episode(row, self.tokenizer, 4096)["input_ids"]), 4096)
