from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            value.update(block)
    return value.hexdigest().upper()


def main() -> None:
    required = [
        "README.md",
        "dashboard/index.html",
        "excel/Project2_CreditPortfolioMonitoring_Gold_v2_1_4.xlsx",
        "validation/web_first_release_validation_report.md",
        "validation/web_first_release_manifest.csv",
        "validation/web_first_release_manifest_verification.json",
        "testing/uat_test_cases.csv",
        "testing/sit_test_cases.csv",
        "testing/negative_test_cases.csv",
    ]
    missing = [relative for relative in required if not (ROOT / relative).exists()]
    if missing:
        raise SystemExit(f"QUICK VALIDATION FAIL - missing: {missing}")
    manifest = pd.read_csv(ROOT / "validation/web_first_release_manifest.csv")
    failures = []
    for row in manifest.itertuples():
        path = ROOT / row.relative_path
        if not path.exists() or digest(path) != row.sha256:
            failures.append(row.relative_path)
    for suite in ["uat_test_cases.csv", "sit_test_cases.csv", "negative_test_cases.csv"]:
        frame = pd.read_csv(ROOT / "testing" / suite)
        if not frame["status"].eq("PASS").all():
            failures.append(f"testing/{suite}")
    if failures:
        raise SystemExit(f"QUICK VALIDATION FAIL - {failures[:10]}")
    verification = json.loads((ROOT / "validation/web_first_release_manifest_verification.json").read_text(encoding="utf-8"))
    if verification.get("status") != "PASS":
        raise SystemExit("QUICK VALIDATION FAIL - release manifest verification is not PASS")
    print(f"QUICK VALIDATION PASS - {len(manifest)} Web-First release artifacts and executable test suites verified")


if __name__ == "__main__":
    main()
