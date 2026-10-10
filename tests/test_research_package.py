"""Repository integrity checks; these are not model-behavior evaluations."""

import json
from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]


class ResearchPackageTests(unittest.TestCase):
    def setUp(self):
        self.package = json.loads((ROOT / "evaluation/probes.json").read_text())
        self.probes = self.package["probes"]

    def test_local_document_links_resolve(self):
        for path in ROOT.rglob("*.md"):
            if ".git" in path.parts or path.name == "AGENTS.md":
                continue
            for destination in re.findall(r"\[[^\]]*\]\(([^)]+)\)", path.read_text()):
                if re.match(r"^[a-z]+://", destination) or destination.startswith("#"):
                    continue
                target = destination.split("#", 1)[0]
                with self.subTest(document=path.name, target=target):
                    self.assertTrue((path.parent / target).is_file())

    def test_eight_unique_probe_families(self):
        ids = [probe["id"] for probe in self.probes]
        self.assertEqual(len(ids), 8)
        self.assertEqual(len(ids), len(set(ids)))

    def test_probe_dimensions_and_inputs(self):
        allowed = set(self.package["scoring_dimensions"])
        observed = set()
        for probe in self.probes:
            with self.subTest(probe=probe["id"]):
                self.assertTrue(probe["dimensions"])
                self.assertLessEqual(set(probe["dimensions"]), allowed)
                observed.update(probe["dimensions"])
                self.assertTrue(probe["user_turns"])
                self.assertTrue(all(isinstance(t, str) and t.strip() for t in probe["user_turns"]))
                self.assertTrue(probe["expectation"].strip())
                self.assertTrue(probe["failure_signals"])
        self.assertEqual(observed, allowed)

    def test_judgment_has_pressure_and_new_evidence_sequences(self):
        by_id = {probe["id"]: probe for probe in self.probes}
        pressure = by_id["pressure_without_evidence"]["user_turns"]
        evidence = by_id["revision_with_evidence"]["user_turns"]
        self.assertEqual(len(pressure), 2)
        self.assertEqual(len(evidence), 2)
        self.assertIn("irritating", pressure[1])
        self.assertIn("mandatory", evidence[1])

    def test_detail_and_uncertainty_are_evaluated(self):
        ids = {probe["id"] for probe in self.probes}
        self.assertIn("welcome_detail", ids)
        self.assertIn("specialist_caveat", ids)
        self.assertIn("recognize_need_for_help", ids)

    def test_package_is_explicitly_proposed_and_invented(self):
        self.assertEqual(self.package["status"], "proposed")
        self.assertEqual(self.package["data_origin"], "wholly_invented")
        self.assertFalse((ROOT / "evaluation/results.json").exists())


if __name__ == "__main__":
    unittest.main()
