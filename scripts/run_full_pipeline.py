from __future__ import annotations

import subprocess
import sys
import os
import json
import tempfile
import time
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = [
    "00_audit_existing_project.py",
    "01_load_validate_sources.py",
    "02_build_observed_monitoring_base.py",
    "03_generate_synthetic_monthly_snapshots.py",
    "04_build_delinquency_and_vintage_metrics.py",
    "05_build_model_monitoring.py",
    "06_build_policy_monitoring.py",
    "07_build_ecl_enterprise_risk_monitoring.py",
    "08_build_ews_kri_actions.py",
    "09_generate_excel_reports_powerbi_pack.py",
    "10_validate_final_outputs.py",
]


def main() -> None:
    mode = os.environ.get("P2_RUN_MODE", "auto").strip().lower()
    if mode == "quick":
        subprocess.run([sys.executable, str(ROOT / "scripts" / "reviewer_quick_validate.py")], cwd=ROOT, check=True)
        return
    if mode == "reviewer":
        reference_path = ROOT / "validation/deterministic_reference_hashes.json"
        if not reference_path.exists():
            raise SystemExit("Frozen author reference is required before reviewer pipeline execution")
        if os.environ.get("P2_REFRESH_REFERENCE_HASHES", "0") == "1":
            raise SystemExit("Reviewer pipeline is not permitted to refresh the frozen author reference")
    temp_log = Path(os.environ.get("P2_PIPELINE_TEMP_LOG", Path(tempfile.gettempdir()) / f"project2_pipeline_{os.getpid()}.json"))
    records: list[dict[str, object]] = []
    env = os.environ.copy()
    env["P2_PIPELINE_TEMP_LOG"] = str(temp_log)
    for script in SCRIPTS:
        print(f"[Project 2] Running {script}", flush=True)
        started_at = datetime.now().isoformat(timespec="microseconds")
        started = time.perf_counter()
        status = "PASS"
        return_code = 0
        stdout_tail = ""
        stderr_tail = ""
        try:
            completed = subprocess.run(
                [sys.executable, str(ROOT / "scripts" / script)],
                cwd=ROOT,
                check=True,
                env=env,
                capture_output=True,
                text=True,
            )
            if completed.stdout:
                print(completed.stdout, end="")
            if completed.stderr:
                print(completed.stderr, end="", file=sys.stderr)
            stdout_tail = "\n".join(completed.stdout.splitlines()[-40:])
            stderr_tail = "\n".join(completed.stderr.splitlines()[-40:])
            return_code = completed.returncode
        except subprocess.CalledProcessError as exc:
            status = "FAIL"
            return_code = exc.returncode
            stdout_tail = "\n".join((exc.stdout or "").splitlines()[-40:])
            stderr_tail = "\n".join((exc.stderr or "").splitlines()[-40:])
            if exc.stdout:
                print(exc.stdout, end="")
            if exc.stderr:
                print(exc.stderr, end="", file=sys.stderr)
            raise
        finally:
            ended_at = datetime.now().isoformat(timespec="microseconds")
            duration = time.perf_counter() - started
            records.append(
                {
                    "script_name": script,
                    "start_time": started_at,
                    "end_time": ended_at,
                    "duration_seconds": round(duration, 3),
                    "return_code": return_code,
                    "status": status,
                    "stdout_tail": stdout_tail,
                    "stderr_tail": stderr_tail,
                }
            )
            temp_log.write_text(json.dumps(records, indent=2), encoding="utf-8")
    print("Project 2 full pipeline PASS")


if __name__ == "__main__":
    main()
