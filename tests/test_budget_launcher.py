from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from types import SimpleNamespace
import tempfile
import unittest
from unittest.mock import patch

from personality_lab.budget import Ledger
from personality_lab.cloud import plan, submit


class FakeApi:
    def __init__(self):
        self.account, self.private, self.active, self.price = "abelcable", True, False, .013333
        self.submissions, self.uploads = [], []
        self.lose_response = False
        self.a100_price = .041667
    def whoami(self):
        return {"name": self.account}
    def model_info(self, repo):
        return SimpleNamespace(private=self.private)
    def list_jobs(self, **kwargs):
        return [SimpleNamespace(status=SimpleNamespace(stage="RUNNING"))] if self.active else []
    def list_jobs_hardware(self):
        return [SimpleNamespace(name="l4x1", unit_label="minute", unit_cost_usd=self.price),
                SimpleNamespace(name="a100-large", unit_label="minute", unit_cost_usd=self.a100_price)]
    def upload_file(self, **kwargs):
        self.uploads.append(kwargs)
    def run_job(self, **kwargs):
        self.submissions.append(kwargs)
        if self.lose_response:
            raise ConnectionError("Lost response after possible submission")
        return SimpleNamespace(id="fake-job", url="https://example.invalid/fake-job")


class BudgetTests(unittest.TestCase):
    def test_atomic_reservation_only_one_concurrent_launch(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "budget.sqlite"
            Ledger(path)
            def reserve(i):
                try:
                    Ledger(path).reserve(str(i), "sha", ".80", 30, 1)
                    return True
                except ValueError:
                    return False
            with ThreadPoolExecutor(max_workers=2) as pool:
                self.assertEqual(sum(pool.map(reserve, range(2))), 1)
            self.assertEqual(Ledger(path).summary()["unresolved_jobs"], 1)

    def test_unknown_bill_blocks_relaunch_and_reconciliation_counts_actual(self):
        with tempfile.TemporaryDirectory() as directory:
            ledger = Ledger(Path(directory) / "budget.sqlite")
            ledger.reserve("one", "sha", "2.50", 120, 0)
            ledger.submitted("one", "job")
            with self.assertRaises(ValueError):
                ledger.reconcile("one", 1, "RUNNING")
            with self.assertRaises(ValueError):
                ledger.reserve("two", "sha", "2.50", 120, 0)
            ledger.reconcile("one", "88", "ERROR")
            self.assertEqual(ledger.summary()["spent"], "88")
            with self.assertRaises(ValueError):
                ledger.reserve("two", "sha", "2.50", 120, 0)

    def test_failure_never_releases_the_reservation_or_retries(self):
        with tempfile.TemporaryDirectory() as directory:
            api = FakeApi()
            api.lose_response = True
            reviewed = plan()
            ledger = Ledger(Path(directory) / "budget.sqlite")
            with self.assertRaises(ConnectionError):
                submit(api, ledger, reviewed, reviewed["approval_sha256"], "fake-test-token")
            self.assertEqual(len(api.submissions), 1)
            self.assertEqual(ledger.summary()["reserved"], "1.40")
            with self.assertRaises(ValueError):
                submit(api, ledger, reviewed, reviewed["approval_sha256"], "fake-test-token")
            self.assertEqual(len(api.submissions), 1)

    def test_success_has_provider_timeout_one_attempt_and_private_destination(self):
        with tempfile.TemporaryDirectory() as directory:
            api = FakeApi()
            reviewed = plan()
            result = submit(api, Ledger(Path(directory) / "budget.sqlite"), reviewed, reviewed["approval_sha256"], "fake-test-token")
            spec = api.submissions[0]
            self.assertEqual(spec["timeout"], 1800)
            self.assertEqual(spec["attempts"], 1)
            self.assertEqual(spec["flavor"], "l4x1")
            self.assertNotIn("fake-test-token", repr(spec["command"]))
            self.assertEqual(spec["secrets"], {"HF_TOKEN": "fake-test-token"})
            self.assertEqual(result["ledger"]["unresolved_jobs"], 1)

    def test_tiny_check_requires_its_own_approval_and_reserves_one_bounded_job(self):
        with tempfile.TemporaryDirectory() as directory:
            api = FakeApi()
            reviewed = plan(stage="tiny-check")
            ledger = Ledger(Path(directory) / "budget.sqlite")
            with self.assertRaises(ValueError):
                submit(api, ledger, reviewed, plan()["approval_sha256"], "fake-test-token")
            self.assertFalse(api.submissions)
            result = submit(api, ledger, reviewed, reviewed["approval_sha256"], "fake-test-token")
            spec = api.submissions[0]
            self.assertEqual((spec["timeout"], spec["attempts"], spec["flavor"]), (3600, 1, "l4x1"))
            self.assertIn("personality_lab.tiny_check", spec["command"][2])
            compile(spec["command"][2], "reviewed-bootstrap", "exec")
            self.assertEqual(reviewed["plan"]["recipe"]["max_steps"], 2)
            self.assertTrue(reviewed["plan"]["downloads_model_weights"])
            self.assertEqual(result["ledger"]["reserved"], "1.80")
            self.assertEqual(len(api.submissions), 1)

    def test_unsupported_stage_and_mutated_training_recipe_never_submit(self):
        with self.assertRaises(ValueError):
            plan(stage="14b-training")
        reviewed = plan(stage="tiny-check")
        reviewed["plan"]["recipe"]["max_steps"] = 300
        with tempfile.TemporaryDirectory() as directory:
            api = FakeApi()
            with self.assertRaises(ValueError):
                submit(api, Ledger(Path(directory) / "budget.sqlite"), reviewed, reviewed["approval_sha256"], "fake-test-token")
            self.assertFalse(api.uploads)

    def test_target_model_run_uses_live_a100_rate_and_bounded_demo(self):
        with tempfile.TemporaryDirectory() as directory:
            reviewed = plan(stage="14b-smoke")
            api = FakeApi()
            ledger = Ledger(Path(directory) / "budget.sqlite")
            submit(api, ledger, reviewed, reviewed["approval_sha256"], "fake-test-token")
            spec = api.submissions[0]
            self.assertEqual((spec["flavor"], spec["timeout"], spec["attempts"]), ("a100-large", 5400, 1))
            self.assertIn('"--recipe","configs/14b-smoke.json","--demo"', spec["command"][2])
            compile(spec["command"][2], "reviewed-bootstrap", "exec")
            self.assertEqual(ledger.summary()["reserved"], "4.77")
        with tempfile.TemporaryDirectory() as directory:
            api = FakeApi()
            api.a100_price = .05
            with self.assertRaises(ValueError):
                submit(api, Ledger(Path(directory) / "budget.sqlite"), reviewed, reviewed["approval_sha256"], "fake-test-token")
            self.assertFalse(api.uploads)

    def test_wrong_account_public_destination_active_job_price_or_approval_stops_before_upload(self):
        for attribute, bad in (("account", "someone_else"), ("private", False), ("active", True), ("price", 1)):
            with self.subTest(attribute=attribute), tempfile.TemporaryDirectory() as directory:
                api = FakeApi()
                setattr(api, attribute, bad)
                reviewed = plan()
                with self.assertRaises(ValueError):
                    submit(api, Ledger(Path(directory) / "budget.sqlite"), reviewed, reviewed["approval_sha256"], "fake-test-token")
                self.assertEqual(api.uploads, [])
                self.assertEqual(api.submissions, [])
        with tempfile.TemporaryDirectory() as directory:
            api = FakeApi()
            with self.assertRaises(ValueError):
                submit(api, Ledger(Path(directory) / "budget.sqlite"), plan(), "wrong-digest", "fake-test-token")
            self.assertFalse(api.submissions)

    def test_reviewed_spec_mutation_cannot_change_command_or_cost(self):
        reviewed = plan()
        reviewed["plan"]["attempts"] = 3
        with tempfile.TemporaryDirectory() as directory, self.assertRaises(ValueError):
            submit(FakeApi(), Ledger(Path(directory) / "budget.sqlite"), reviewed, reviewed["approval_sha256"], "fake-test-token")

    def test_source_change_during_api_preflight_stops_before_reservation(self):
        reviewed = plan()
        with tempfile.TemporaryDirectory() as directory:
            api = FakeApi()
            ledger = Ledger(Path(directory) / "budget.sqlite")
            original = api.list_jobs_hardware
            def price_then_source_change():
                # After the initial source-bound comparison, simulate a concurrent edit.
                source_patch.start()
                return original()
            api.list_jobs_hardware = price_then_source_change
            source_patch = patch("personality_lab.cloud.source_bundle", return_value=(b"changed", "different"))
            try:
                with self.assertRaises(ValueError):
                    submit(api, ledger, reviewed, reviewed["approval_sha256"], "fake-test-token")
            finally:
                source_patch.stop()
            self.assertEqual(ledger.summary()["unresolved_jobs"], 0)
            self.assertFalse(api.uploads)
