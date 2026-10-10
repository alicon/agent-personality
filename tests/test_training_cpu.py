"""Real gradient/save/reload/resume tests on random tiny Qwen; no behavior claims."""
from dataclasses import replace
from pathlib import Path
import tempfile
import unittest

try:
    import torch
    from peft import PeftModel
    from transformers import Qwen3Config, Qwen3ForCausalLM
    HAS_ML = True
except ImportError:
    HAS_ML = False

from personality_lab.training import Recipe, add_adapter, fit, frozen_parameter_digest, inference_logits
from personality_lab.tiny_check import adapter_changed


class ToyTokenizer:
    pad_token_id = 0
    def save_pretrained(self, path):
        Path(path).mkdir(parents=True, exist_ok=True)


@unittest.skipUnless(HAS_ML, "Run .venv-lab/bin/python for real CPU adapter checks")
class CpuTrainingTests(unittest.TestCase):
    def test_reload_checks_control_training_autocast_wrapper_and_comparison_dtype(self):
        # Accelerate precision configuration is process-global; isolate it from
        # the other tests' full-precision CPU Trainers.
        import subprocess
        import sys
        script = ("import sys; sys.path.insert(0, 'tests'); "
                  "from test_training_cpu import CpuTrainingTests; "
                  "CpuTrainingTests()._check_precision_reload()")
        result = subprocess.run([sys.executable, "-c", script], capture_output=True, text=True, timeout=45)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def _check_precision_reload(self):
        from accelerate import Accelerator
        torch.set_num_threads(1)
        torch.manual_seed(41)
        config = Qwen3Config(vocab_size=32, hidden_size=16, intermediate_size=32, num_hidden_layers=1,
                             num_attention_heads=2, num_key_value_heads=1, head_dim=8,
                             bos_token_id=1, eos_token_id=2, pad_token_id=0)
        model = add_adapter(Qwen3ForCausalLM(config), 2)
        with torch.no_grad():
            model.base_model.model.lm_head.weight.mul_(50)
            for name, parameter in model.named_parameters():
                if "lora_B" in name:
                    parameter.normal_(0, .01)
        sample = {"input_ids": torch.tensor([[1, 3, 4, 5, 2]])}
        accelerator = Accelerator(cpu=True, mixed_precision="bf16")
        model = accelerator.prepare_model(model)
        model.eval()
        with torch.no_grad():
            uncontrolled_expected = model(**sample).logits.detach().float()
        before = frozen_parameter_digest(model)
        with tempfile.TemporaryDirectory() as directory:
            model.save_pretrained(directory)
            accelerator.unwrap_model(model, keep_fp32_wrapper=False)
            self.assertFalse(hasattr(model, "_original_forward"))
            controlled_expected = inference_logits(model, sample, device_type="cpu")
            base = model.unload()
            del base.peft_config
            restored = PeftModel.from_pretrained(base, directory)
            restored.eval()
            with torch.no_grad():
                uncontrolled_actual = restored(**sample).logits.detach().float()
            self.assertFalse(torch.allclose(uncontrolled_expected, uncontrolled_actual, atol=.02, rtol=.02))
            actual = inference_logits(restored, sample, device_type="cpu")
            self.assertEqual(actual.dtype, torch.float32)
            self.assertTrue(torch.equal(controlled_expected, actual))
            self.assertEqual(before, frozen_parameter_digest(restored))

    def test_adapter_changes_and_can_reload_switch_and_resume(self):
        torch.set_num_threads(1)
        torch.manual_seed(41)
        config = Qwen3Config(vocab_size=32, hidden_size=16, intermediate_size=32, num_hidden_layers=1,
                             num_attention_heads=2, num_key_value_heads=1, head_dim=8,
                             bos_token_id=1, eos_token_id=2, pad_token_id=0, attention_dropout=0)
        model = add_adapter(Qwen3ForCausalLM(config), 2)
        base_before = {n: p.detach().clone() for n, p in model.named_parameters() if not p.requires_grad}
        before = {n: p.detach().clone() for n, p in model.named_parameters() if p.requires_grad}
        frozen_sha = frozen_parameter_digest(model)
        rows = [{"input_ids": [1, 3, 4, 5, 2], "attention_mask": [1]*5, "labels": [-100, -100, 4, 5, 2]},
                {"input_ids": [1, 6, 7, 2], "attention_mask": [1]*4, "labels": [-100, -100, 7, 2]}]
        recipe = Recipe.load("configs/tiny-smoke.json")
        recipe = replace(recipe, max_steps=2, gradient_accumulation_steps=1, learning_rate=.001, lora_rank=2, soft_timeout_seconds=1e-9)
        from personality_lab.data import collate
        sample = collate([rows[0]], 0)
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            metrics = fit(model, rows, rows, ToyTokenizer(), recipe, output, cpu=True)
            self.assertEqual(metrics["steps"], 1)
            self.assertTrue(any(not torch.equal(before[n], p) for n, p in model.named_parameters() if n in before))
            self.assertTrue(all(torch.equal(base_before[n], p) for n, p in model.named_parameters() if n in base_before))
            self.assertEqual(frozen_sha, frozen_parameter_digest(model))
            model.eval()
            with torch.no_grad():
                expected = model(**sample).logits
                with model.disable_adapter():
                    original = model(**sample).logits
            self.assertFalse(torch.equal(expected, original))
            base = model.unload()
            del base.peft_config
            restored = PeftModel.from_pretrained(base, output / "adapter", is_trainable=True)
            restored.eval()
            with torch.no_grad():
                self.assertTrue(torch.allclose(restored(**sample).logits, expected, atol=1e-6))
            before_resume = {n: p.detach().clone() for n, p in restored.named_parameters() if p.requires_grad}
            resumed = fit(restored, rows, rows, ToyTokenizer(), replace(recipe, soft_timeout_seconds=600), output,
                          cpu=True, resume=str(output / "checkpoint-1"))
            self.assertEqual(resumed["steps"], 2)
            self.assertTrue(any(not torch.equal(before_resume[n], p) for n, p in restored.named_parameters() if n in before_resume))

    def test_deliberate_stop_and_fresh_process_style_resume_updates_saved_tensors(self):
        torch.set_num_threads(1)
        torch.manual_seed(41)
        config = Qwen3Config(vocab_size=32, hidden_size=16, intermediate_size=32, num_hidden_layers=1,
                             num_attention_heads=2, num_key_value_heads=1, head_dim=8,
                             bos_token_id=1, eos_token_id=2, pad_token_id=0, attention_dropout=0)
        recipe = replace(Recipe.load("configs/tiny-check.json"), learning_rate=.001, lora_rank=2)
        rows = [{"input_ids": [1, 3, 4, 5, 2], "attention_mask": [1]*5, "labels": [-100, -100, 4, 5, 2]}]
        with tempfile.TemporaryDirectory() as directory:
            first, resumed = Path(directory) / "first", Path(directory) / "resumed"
            model = add_adapter(Qwen3ForCausalLM(config), 2)
            metrics = fit(model, rows, rows, ToyTokenizer(), recipe, first, cpu=True, stop_after_step=1)
            self.assertEqual(metrics["steps"], 1)
            self.assertTrue(metrics["stopped_early"])
            # Reconstruct the model rather than continuing the first optimizer in memory.
            torch.manual_seed(41)
            fresh_model = add_adapter(Qwen3ForCausalLM(config), 2)
            continued = fit(fresh_model, rows, rows, ToyTokenizer(), recipe, resumed, cpu=True,
                            resume=str(first / "checkpoint-1"))
            self.assertEqual(continued["steps"], 2)
            self.assertEqual(continued["optimizer_step_values"], [2])
            self.assertTrue(adapter_changed(first / "adapter/adapter_model.safetensors",
                                            resumed / "adapter/adapter_model.safetensors"))
            self.assertFalse(adapter_changed(first / "adapter/adapter_model.safetensors",
                                             first / "adapter/adapter_model.safetensors"))
            torch.manual_seed(41)
            uninterrupted_model = add_adapter(Qwen3ForCausalLM(config), 2)
            uninterrupted = Path(directory) / "uninterrupted"
            fit(uninterrupted_model, rows, rows, ToyTokenizer(), recipe, uninterrupted, cpu=True)
            from safetensors.torch import load_file
            expected = load_file(str(uninterrupted / "adapter/adapter_model.safetensors"))
            actual = load_file(str(resumed / "adapter/adapter_model.safetensors"))
            for name in expected:
                self.assertTrue(torch.allclose(expected[name], actual[name], atol=1e-7, rtol=1e-6), name)
