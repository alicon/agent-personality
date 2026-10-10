"""Local preparation cost estimate; never submits jobs or changes billing."""

import argparse
from decimal import Decimal, InvalidOperation, ROUND_CEILING
import json


WORKING_LIMIT = Decimal("90")
MAX_GPU_QUOTE = Decimal("5")


def amount(value):
    try:
        result = Decimal(str(value))
    except InvalidOperation as exc:
        raise ValueError("Amounts must be finite nonnegative numbers") from exc
    if not result.is_finite() or result < 0:
        raise ValueError("Amounts must be finite nonnegative numbers")
    return result


def estimate(hourly_rate, timeout_minutes, spent, reserved, extras):
    rate, minutes, used, pending, extra = map(
        amount, (hourly_rate, timeout_minutes, spent, reserved, extras)
    )
    if rate == 0 or minutes == 0 or minutes > 120:
        raise ValueError("Use a positive rate and a timeout of at most 120 minutes")
    billed_minutes = minutes.to_integral_value(rounding=ROUND_CEILING)
    gpu = (rate * billed_minutes / 60).quantize(Decimal("0.01"), rounding=ROUND_CEILING)
    total = gpu + extra
    projected = used + pending + total
    return {
        "gpu_max_usd": str(gpu),
        "job_max_with_extras_usd": str(total),
        "projected_phase_liability_usd": str(projected),
        "within_preparation_policy": gpu <= MAX_GPU_QUOTE and projected <= WORKING_LIMIT,
        "attempts": 1,
        "billable_minutes": int(billed_minutes),
        "submitted": False,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("hourly-rate", "timeout-minutes", "spent", "reserved", "extras"):
        parser.add_argument(f"--{name}", required=True)
    args = parser.parse_args()
    try:
        result = estimate(args.hourly_rate, args.timeout_minutes, args.spent, args.reserved, args.extras)
    except ValueError as exc:
        parser.error(str(exc))
    print(json.dumps(result, indent=2))
    return 0 if result["within_preparation_policy"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
