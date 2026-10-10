import tempfile
import unittest

from personality_lab.lab import CONDITIONS, Generation, MockBackend, Session, assemble


class SpyBackend(MockBackend):
    def __init__(self):
        self.calls = []
        self.fail = False
    def generate(self, messages, adapter, settings):
        self.calls.append((messages, adapter, settings))
        if self.fail:
            raise RuntimeError("Simulated backend failure")
        return super().generate(messages, adapter, settings)


class LabTests(unittest.TestCase):
    def test_condition_controls_preserve_facts_and_settings(self):
        for condition, (prompt, adapter) in CONDITIONS.items():
            messages, actual_adapter = assemble([], "USER", condition, "DISPOSITION", "FACTS")
            self.assertEqual(actual_adapter, adapter)
            self.assertEqual("DISPOSITION" in messages[0]["content"], prompt)
            self.assertIn("FACTS", messages[0]["content"])
            self.assertEqual(messages[-1]["content"], "USER")

    def test_blind_session_record_and_correction_restore(self):
        with tempfile.TemporaryDirectory() as directory:
            backend = SpyBackend()
            session = Session(directory, ("prompt-only", "adapter-only"), "DISPOSITION", "FACTS", True, backend)
            session.send("hello")
            self.assertEqual(session.public_labels(), {"A": "Hidden condition", "B": "Hidden condition"})
            self.assertEqual({call[1] for call in backend.calls}, {False, True})
            self.assertTrue(all(call[2] == Generation() for call in backend.calls))
            session.mark("A")
            session.send("make this shorter")
            restored = Session.restore(session.path, backend)
            self.assertEqual(len(restored.record["turns"]), 2)
            self.assertGreaterEqual(restored.record["corrections"][0]["wall_seconds_until_followup"], 0)
            self.assertIn("assembled_messages", restored.record["turns"][0]["arms"]["A"])
            self.assertNotEqual(restored.record["turns"][0]["arms"]["A"]["request_sha256"],
                                restored.record["turns"][0]["arms"]["B"]["request_sha256"])
            self.assertFalse(restored.record["backend"]["behavior_evaluated"])

    def test_failed_pair_does_not_commit_partial_history(self):
        with tempfile.TemporaryDirectory() as directory:
            backend = SpyBackend()
            session = Session(directory, ("prompt-only", "adapter-only"), "DISPOSITION", backend=backend)
            backend.fail = True
            with self.assertRaises(RuntimeError):
                session.send("hello")
            self.assertEqual(session.record["turns"], [])
            self.assertEqual(Session.restore(session.path, backend).record["turns"], [])

    def test_invalid_controls_and_double_mark_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(ValueError):
                Session(directory, ("prompt-only", "prompt-only"), "DISPOSITION")
            session = Session(directory, ("untuned", "hybrid"), "DISPOSITION")
            with self.assertRaises(ValueError):
                session.mark("A")
            session.send("hello")
            session.mark("B")
            with self.assertRaises(ValueError):
                session.mark("B")
