from dataclasses import asdict
import copy
import json
from pathlib import Path
import tempfile
import unittest

from personality_lab.training import Recipe, validate_resume
from personality_lab.tiny_check import check_phase_reports, phase_commands


class ResumeProtocolTests(unittest.TestCase):
    def test_resume_rejects_changed_provenance_and_incomplete_state_without_overwrite(self):
        recipe = asdict(Recipe.load("configs/tiny-check.json"))
        manifest = {"recipe": recipe, "data_sha256": "original-data", "chat_template_sha256": "template",
                    "source": {"trainer_sha256": "original"}}
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            checkpoint = root / "checkpoint-1"
            checkpoint.mkdir()
            old = json.dumps(manifest)
            (root / "manifest.json").write_text(old)
            (checkpoint / "trainer_state.json").write_text('{"global_step": 1}')
            files = ("optimizer.pt", "scheduler.pt", "rng_state.pth", "adapter_model.safetensors")
            for filename in files:
                (checkpoint / filename).touch()
            self.assertEqual(validate_resume(checkpoint, manifest), 1)
            for key in ("data_sha256", "chat_template_sha256"):
                altered = copy.deepcopy(manifest)
                altered[key] = "different"
                with self.assertRaises(ValueError):
                    validate_resume(checkpoint, altered)
            altered = copy.deepcopy(manifest)
            altered["recipe"]["learning_rate"] *= 2
            with self.assertRaises(ValueError):
                validate_resume(checkpoint, altered)
            altered = copy.deepcopy(manifest)
            altered["source"]["trainer_sha256"] = "changed"
            with self.assertRaises(ValueError):
                validate_resume(checkpoint, altered)
            for filename in files:
                (checkpoint / filename).unlink()
                with self.assertRaises(ValueError):
                    validate_resume(checkpoint, manifest)
                (checkpoint / filename).touch()
            (checkpoint / "trainer_state.json").write_text('{"global_step": 2}')
            with self.assertRaises(ValueError):
                validate_resume(checkpoint, manifest)
            self.assertEqual((root / "manifest.json").read_text(), old)

    def test_second_process_points_to_first_optimizer_checkpoint(self):
        first, resumed = phase_commands("configs/tiny-check.json", "tiny-test", "abelcable/agent-personality-qwen3-14b")
        self.assertEqual(first[first.index("--stop-after-step") + 1], "1")
        self.assertEqual(resumed[resumed.index("--resume") + 1], "artifacts/tiny-check/tiny-test-first/checkpoint-1")
        self.assertNotIn("--stop-after-step", resumed)
        self.assertIn("--verify-frozen-base", first)
        self.assertIn("--verify-frozen-base", resumed)

    def test_report_rejects_no_resume_failed_reload_changed_base_or_nonfinite_loss(self):
        common = {"adapter_changed": True, "reload_checked": True, "frozen_parameters_unchanged": True,
                  "reload_frozen_parameters_unchanged": True,
                  "adapter_on_off_max_abs_delta": .01, "recipe": {}, "data_sha256": "data",
                  "chat_template_sha256": "template", "source": {}}
        first = dict(common, status="stopped_early")
        second = dict(common, status="completed", resume_start_step=1)
        metrics1 = {"steps": 1, "optimizer_step_values": [1], "validation": {"eval_loss": 2.0}}
        metrics2 = {"steps": 2, "optimizer_step_values": [2], "validation": {"eval_loss": 1.9}}
        check_phase_reports(first, second, metrics1, metrics2)
        for key, value in (("resume_start_step", 0), ("reload_checked", False),
                           ("frozen_parameters_unchanged", False), ("adapter_on_off_max_abs_delta", 0),
                           ("reload_frozen_parameters_unchanged", False),
                           ("data_sha256", "changed")):
            with self.subTest(key=key), self.assertRaises(ValueError):
                check_phase_reports(first, dict(second, **{key: value}), metrics1, metrics2)
        with self.assertRaises(ValueError):
            check_phase_reports(first, second, metrics1, dict(metrics2, validation={"eval_loss": float("nan")}))
        with self.assertRaises(ValueError):
            check_phase_reports(first, second, metrics1, dict(metrics2, optimizer_step_values=[1]))
