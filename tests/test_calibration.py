import json
from pathlib import Path
import tempfile
import unittest

from personality_lab.calibration import save_choice


class CalibrationTests(unittest.TestCase):
    def test_choices_record_preferences_without_training_or_overriding_facts(self):
        cards = json.loads(Path("data/calibration.json").read_text())["cards"]
        self.assertEqual(len({c["id"] for c in cards}), 12)
        self.assertEqual({c["kind"] for c in cards}, {"taste", "judgment"})
        with tempfile.TemporaryDirectory() as directory:
            for card in cards:
                result = save_choice(card, "Neither works", "Rewrite needed", directory)
                self.assertFalse(result["training_approved"])
                self.assertEqual(result["requires_review_of_factual_validity"], card["kind"] == "judgment")
                self.assertTrue(result["card_sha256"])
            self.assertEqual(len(list(Path(directory).glob("*.json"))), 12)
            with self.assertRaises(ValueError):
                save_choice(cards[0], "automatically choose", "", directory)
