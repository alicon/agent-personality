"""Bounded environment/tiny checks; submission requires the reviewed plan's exact digest."""
import argparse
from decimal import Decimal
import gzip
import hashlib
import io
import json
from pathlib import Path
import subprocess
import tarfile
import uuid

from personality_lab.budget import Ledger
from personality_lab.data import digest, load_episodes
from personality_lab.training import Recipe

ROOT = Path(__file__).resolve().parents[1]
IMAGE = "pytorch/pytorch@sha256:417bd75df6365104c283ea4c1651fb3530d9eb5a4c2fafa51943cff2a94e6385"
ACCOUNT = "abelcable"
REPO = "abelcable/agent-personality-qwen3-14b"
TERMINAL = {"COMPLETED", "CANCELED", "ERROR", "DELETED"}
STAGES = {
    "environment": ("l4x1", 1800, "0.80", "environment", 600, None),
    "tiny-check": ("l4x1", 3600, "0.80", "tiny_check", 1800, "configs/tiny-check.json"),
    "14b-smoke": ("a100-large", 5400, "2.51", "training", 4200, "configs/14b-smoke.json"),
}


def source_bundle():
    files = [p for folder in ("personality_lab", "scripts", "configs", "data", "tests")
             for p in (ROOT / folder).rglob("*") if p.is_file() and p.suffix in (".py", ".json", ".jsonl")]
    files += [ROOT / name for name in ("requirements-lab.txt", "requirements-gpu.txt", "requirements-gpu-resolved.txt",
                                      "configs/disposition.txt")]
    raw = io.BytesIO()
    with gzip.GzipFile(fileobj=raw, mode="wb", mtime=0) as compressed:
        with tarfile.open(fileobj=compressed, mode="w") as archive:
            for path in sorted(files):
                content = path.read_bytes()
                member = tarfile.TarInfo(str(path.relative_to(ROOT)))
                member.size, member.mode, member.mtime = len(content), 0o644, 0
                archive.addfile(member, io.BytesIO(content))
    content = raw.getvalue()
    return content, hashlib.sha256(content).hexdigest()


def verify_account(api):
    if api.whoami()["name"] != ACCOUNT or not api.model_info(REPO).private:
        raise ValueError("Expected account and private artifact repository required")
    active = [j for j in api.list_jobs(namespace=ACCOUNT) if j.status.stage not in TERMINAL]
    if active:
        raise ValueError("An unresolved provider job is present; do not submit another")


def current_rate(api, flavor="l4x1"):
    hardware = api.list_jobs_hardware()
    item = next(h for h in hardware if h.name == flavor)
    # Prices are provider USD per hour; use minute rate too where supplied.
    if item.unit_label != "minute":
        raise ValueError("Unknown provider billing unit")
    floor = Decimal("0.80" if flavor == "l4x1" else "2.50")
    return str(max(floor, Decimal(str(item.unit_cost_usd)) * 60))


def plan(rate=None, stage="environment"):
    if stage not in STAGES:
        raise ValueError("Unknown bounded preparation stage")
    flavor, timeout, default_rate, _, _, recipe_path = STAGES[stage]
    rate = default_rate if rate is None else rate
    load_episodes(ROOT / "data/development.jsonl")
    _, source_sha = source_bundle()
    source_commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    content = {"schema": 1, "stage": stage, "account": ACCOUNT, "repo": REPO,
               "image": IMAGE, "flavor": flavor, "timeout_seconds": timeout, "attempts": 1,
               "hourly_rate_usd": rate, "extras_max_usd": "1.00", "source_bundle_sha256": source_sha,
               "git_commit": source_commit, "downloads_model_weights": stage != "environment"}
    if recipe_path:
        from dataclasses import asdict
        recipe = Recipe.load(ROOT / recipe_path)
        expected_model, expected_steps = ("Qwen/Qwen3-0.6B", 2) if stage == "tiny-check" else ("Qwen/Qwen3-14B", 20)
        if recipe.model_id != expected_model or recipe.max_steps != expected_steps:
            raise ValueError("Expected bounded model recipe")
        content["recipe"] = asdict(recipe)
    if stage == "14b-smoke":
        content["demo"] = {"cases": "data/demo-prompts.json", "max_new_tokens": 192,
                           "do_sample": False, "enable_thinking": False, "conditions": 4}
    return {"plan": content, "approval_sha256": digest(content)}


def bootstrap(source_sha, run_id, stage="environment"):
    if stage not in STAGES:
        raise ValueError("Unknown stage")
    _, _, _, module, deadline, recipe_path = STAGES[stage]
    extra = ',"--recipe","configs/14b-smoke.json","--demo"' if stage == "14b-smoke" else ""
    # No secret values in command/spec/records; token is passed only through provider secrets.
    return f'''import hashlib,io,os,pathlib,subprocess,tarfile,urllib.request
url="https://huggingface.co/{REPO}/resolve/main/preparation/source/{source_sha}.tar.gz"
request=urllib.request.Request(url,headers={{"Authorization":"Bearer "+os.environ["HF_TOKEN"]}})
content=urllib.request.urlopen(request,timeout=90).read()
assert hashlib.sha256(content).hexdigest()=="{source_sha}","Source digest mismatch"
root=pathlib.Path("/tmp/personality-source");root.mkdir(exist_ok=False)
with tarfile.open(fileobj=io.BytesIO(content),mode="r:gz") as archive:
 for member in archive.getmembers():
  assert member.isfile() and not pathlib.Path(member.name).is_absolute() and ".." not in pathlib.Path(member.name).parts,"Unsafe archive"
 archive.extractall(root,filter="data")
subprocess.run(["python","-m","pip","install","--disable-pip-version-check","-r","requirements-gpu-resolved.txt"],cwd=root,check=True,timeout=900)
subprocess.run(["python","-m","personality_lab.{module}","--run-id","{run_id}","--persist-repo","{REPO}"{extra}],cwd=root,check=True,timeout={deadline})
'''


def submit(api, ledger, reviewed, approval, token):
    expected = plan(reviewed["plan"]["hourly_rate_usd"], reviewed["plan"]["stage"])
    if reviewed != expected or approval != expected["approval_sha256"]:
        raise ValueError("Reviewed source or plan changed; prepare and review again")
    verify_account(api)
    if Decimal(current_rate(api, expected["plan"]["flavor"])) > Decimal(expected["plan"]["hourly_rate_usd"]):
        raise ValueError("Live hardware price exceeds reviewed rate")
    prefix = {"environment": "env-", "tiny-check": "tiny-", "14b-smoke": "q14-"}[expected["plan"]["stage"]]
    run_id = prefix + uuid.uuid4().hex[:12]
    spec = expected["plan"]
    content, source_sha = source_bundle()
    if source_sha != spec["source_bundle_sha256"]:
        raise ValueError("Reviewed source changed during preflight")
    ledger.reserve(run_id, approval, spec["hourly_rate_usd"], spec["timeout_seconds"] / 60, spec["extras_max_usd"])
    # Failure anywhere after reservation retains liability, including a lost response.
    api.upload_file(path_or_fileobj=content, path_in_repo=f"preparation/source/{source_sha}.tar.gz", repo_id=REPO,
                    commit_message=f"Pinned source for bounded {spec['stage']} smoke")
    job = api.run_job(image=IMAGE, command=["python", "-c", bootstrap(source_sha, run_id, spec["stage"])], flavor=spec["flavor"],
                      timeout=spec["timeout_seconds"], attempts=1, namespace=ACCOUNT, name=run_id,
                      labels={"project": "agent-personality", "reservation": run_id},
                      env={"PERSONALITY_SOURCE_SHA256": source_sha, "PERSONALITY_SOURCE_COMMIT": spec["git_commit"]},
                      secrets={"HF_TOKEN": token})
    ledger.submitted(run_id, job.id)
    return {"job_id": job.id, "reservation": run_id, "url": job.url, "ledger": ledger.summary()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("prepare", "submit", "status", "cancel"))
    parser.add_argument("--plan", default="artifacts/first-run.json")
    parser.add_argument("--ledger", default="artifacts/budget.sqlite")
    parser.add_argument("--approve-plan")
    parser.add_argument("--job-id")
    parser.add_argument("--stage", choices=tuple(STAGES), default="environment")
    args = parser.parse_args()
    ledger = Ledger(args.ledger)
    if args.action == "prepare":
        result = plan(stage=args.stage)
        Path(args.plan).parent.mkdir(parents=True, exist_ok=True)
        Path(args.plan).write_text(json.dumps(result, indent=2))
        result["ledger"] = ledger.summary()
    else:
        from huggingface_hub import HfApi, get_token
        api = HfApi()
        if args.action == "submit":
            if not args.approve_plan:
                parser.error("An explicitly reviewed plan digest is required")
            token = get_token()
            if not token:
                parser.error("Local Hugging Face login required")
            result = submit(api, ledger, json.loads(Path(args.plan).read_text()), args.approve_plan, token)
        else:
            if not args.job_id:
                parser.error("Job ID required")
            if args.action == "cancel":
                api.cancel_job(job_id=args.job_id, namespace=ACCOUNT)
            job = api.inspect_job(job_id=args.job_id, namespace=ACCOUNT)
            result = {"job_id": job.id, "status": job.status.stage, "ledger": ledger.summary()}
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
