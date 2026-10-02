"""Run the ten saved-evidence checks without network or model calls."""
from pathlib import Path
import json, subprocess, sys, time
ROOT = Path(__file__).resolve().parent
CHECKS = [
    "reproduction_core/reproduce.py", "review_reproduction/reproduce.py",
    "baseline_reproduction/reproduce.py", "synthesis_reproduction/reproduce.py",
    "confirmation_reproduction/reproduce.py", "selection_reproduction/reproduce.py",
    "confirmation_reproduction/audit_traces.py", "executor_check_reproduction/reproduce.py",
    "walkthrough_reproduction/reproduce.py", "state_opportunity_reproduction/reproduce.py",
]
def main():
    out = ROOT / "outputs"
    out.mkdir(exist_ok=True)
    rows = []
    for i, name in enumerate(CHECKS, 1):
        start = time.monotonic()
        logfile = out / f"{i:02d}_{Path(name).parent.name}_{Path(name).stem}.txt"
        with logfile.open("w") as log:
            run = subprocess.run([sys.executable, str(ROOT / name)], cwd=ROOT, stdout=log, stderr=subprocess.STDOUT)
        rows.append({"command": name, "exit_code": run.returncode, "seconds": round(time.monotonic()-start, 3), "log": str(logfile.relative_to(ROOT))})
        (out / "RESULTS.json").write_text(json.dumps({"status": "PASS" if len(rows)==len(CHECKS) and all(r["exit_code"]==0 for r in rows) else "INCOMPLETE_OR_FAILED", "checks": rows}, indent=2)+"\n")
        print(f"{i}/{len(CHECKS)} {name}: {'PASS' if run.returncode == 0 else 'FAIL'}", flush=True)
        if run.returncode:
            raise SystemExit(run.returncode)
if __name__ == "__main__":
    main()
