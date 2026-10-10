"""Atomic local reservations. Unknown submission/billing retains the liability."""
from contextlib import contextmanager
from decimal import Decimal
import json
from pathlib import Path
import sqlite3

from scripts.preparation_cost import amount, estimate


class Ledger:
    def __init__(self, path):
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        self.path = str(path)
        with self.connect() as db:
            db.execute('''CREATE TABLE IF NOT EXISTS jobs (
                reservation TEXT PRIMARY KEY, plan_sha TEXT NOT NULL,
                maximum TEXT NOT NULL, state TEXT NOT NULL,
                job_id TEXT, actual TEXT, terminal_status TEXT)''')

    @contextmanager
    def connect(self):
        db = sqlite3.connect(self.path, timeout=5, isolation_level=None)
        try:
            db.execute("BEGIN IMMEDIATE")
            yield db
            db.execute("COMMIT")
        except BaseException:
            db.execute("ROLLBACK")
            raise
        finally:
            db.close()

    def summary(self):
        with self.connect() as db:
            rows = db.execute("SELECT maximum,state,actual FROM jobs").fetchall()
        return {"spent": str(sum((amount(a) for _, s, a in rows if s == "reconciled"), Decimal(0))),
                "reserved": str(sum((amount(m) for m, s, _ in rows if s != "reconciled"), Decimal(0))),
                "unresolved_jobs": sum(s != "reconciled" for _, s, _ in rows)}

    def reserve(self, reservation, plan_sha, rate, minutes, extras):
        with self.connect() as db:
            rows = db.execute("SELECT maximum,state,actual FROM jobs").fetchall()
            if any(s != "reconciled" for _, s, _ in rows):
                raise ValueError("Resolve the previous liability before another paid job")
            spent = sum((amount(a) for _, _, a in rows), Decimal(0))
            quote = estimate(rate, minutes, spent, 0, extras)
            if not quote["within_preparation_policy"]:
                raise ValueError("Preparation budget would be exceeded")
            db.execute("INSERT INTO jobs VALUES (?,?,?,'reserved',NULL,NULL,NULL)",
                       (reservation, plan_sha, quote["job_max_with_extras_usd"]))
        return quote

    def submitted(self, reservation, job_id):
        with self.connect() as db:
            changed = db.execute("UPDATE jobs SET state='submitted',job_id=? WHERE reservation=? AND state='reserved'",
                                 (job_id, reservation)).rowcount
            if changed != 1:
                raise ValueError("Reservation is not awaiting submission")

    def reconcile(self, reservation, actual, terminal_status):
        if terminal_status not in ("COMPLETED", "CANCELED", "ERROR", "DELETED", "CONFIRMED_NOT_SUBMITTED"):
            raise ValueError("Only a confirmed terminal job can be reconciled")
        cost = amount(actual)
        with self.connect() as db:
            row = db.execute("SELECT state FROM jobs WHERE reservation=?", (reservation,)).fetchone()
            if not row or row[0] == "reconciled":
                raise ValueError("Unknown or already reconciled reservation")
            db.execute("UPDATE jobs SET state='reconciled',actual=?,terminal_status=? WHERE reservation=?",
                       (str(cost), terminal_status, reservation))


def main():
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ledger", default="artifacts/budget.sqlite")
    parser.add_argument("--reconcile")
    parser.add_argument("--actual")
    parser.add_argument("--terminal-status")
    args = parser.parse_args()
    ledger = Ledger(args.ledger)
    if args.reconcile:
        if args.actual is None or args.terminal_status is None:
            parser.error("Actual invoice charge and confirmed terminal status required")
        ledger.reconcile(args.reconcile, args.actual, args.terminal_status)
    print(json.dumps(ledger.summary(), indent=2))


if __name__ == "__main__":
    main()
