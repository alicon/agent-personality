import unittest

from scripts.preparation_cost import estimate


class PreparationCostTests(unittest.TestCase):
    def test_prior_pending_jobs_cannot_be_spent_twice(self):
        result = estimate("2.50", 120, 85, 1, 0)
        self.assertFalse(result["within_preparation_policy"])
        self.assertEqual(result["projected_phase_liability_usd"], "91.00")

    def test_ancillary_costs_count_against_phase(self):
        self.assertFalse(estimate("2.50", 120, 85, 0, "0.01")["within_preparation_policy"])

    def test_minute_and_cent_rounding_is_conservative(self):
        result = estimate("0.80", "30.01", 0, 0, 0)
        self.assertEqual(result["billable_minutes"], 31)
        self.assertEqual(result["gpu_max_usd"], "0.42")

    def test_invalid_costs_fail_before_quote(self):
        for bad in ("NaN", "Infinity", "-1", "unknown"):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                estimate(bad, 30, 0, 0, 0)

    def test_expensive_hardware_fails_even_with_phase_headroom(self):
        self.assertFalse(estimate(10, 60, 0, 0, 0)["within_preparation_policy"])

    def test_zero_or_long_timeout_is_rejected(self):
        for minutes in (0, 121):
            with self.subTest(minutes=minutes), self.assertRaises(ValueError):
                estimate("2.50", minutes, 0, 0, 0)

    def test_quote_does_not_submit_or_auto_retry(self):
        result = estimate("2.50", 90, 0, 0, 0)
        self.assertEqual(result["gpu_max_usd"], "3.75")
        self.assertTrue(result["within_preparation_policy"])
        self.assertFalse(result["submitted"])
        self.assertEqual(result["attempts"], 1)
