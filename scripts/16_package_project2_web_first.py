from __future__ import annotations

import argparse
import csv
import hashlib
import json
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PORTFOLIO_ROOT = ROOT.parent
PACKAGE_NAME = "Project2_CreditPortfolioMonitoring_WEB_FIRST_RELEASE_v1_0.zip"
PACKAGE_ROOT = "02_CreditPortfolioMonitoring"
MANIFEST = ROOT / "validation" / "web_first_release_manifest.csv"
VERIFICATION = ROOT / "validation" / "web_first_release_manifest_verification.json"
PREFLIGHT = ROOT / "validation" / "web_first_release_preflight.json"

EXCLUDED_PREFIXES = (
    "tools/",
    "powerbi/",
    "archive/superseded/",
    "archive/deferred_powerbi/",
)
DEFERRED_POWERBI_PREFIXES = (
    "scripts/11_generate_powerbi_",
    "scripts/12_validate_powerbi_",
    "scripts/13_validate_tmdl_",
    "scripts/14_run_powerbi_",
    "scripts/14_stage_provider_",
    "testing/dax_",
    "testing/pbix_",
    "testing/provider_",
    "validation/powerbi_",
    "validation/tmdl_",
)
EXCLUDED_NAMES = {"Thumbs.db", ".DS_Store"}
EXCLUDED_SUFFIXES = {".pyc", ".pyo", ".tmp"}
MANIFEST_EXCLUSIONS = {
    "validation/web_first_release_manifest.csv",
    "validation/web_first_release_manifest_verification.json",
}
AUTHOR_PATH_TOKENS = (
    "D:" + r"\data\FinancialRiskPortfolioProjects",
    "D:" + r"\Po BI",
    "C:" + r"\Users\sangk",
)
TEXT_SUFFIXES = {".md", ".html", ".json", ".csv", ".txt", ".py", ".ps1", ".sql"}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def relative(path: Path, root: Path = ROOT) -> str:
    return path.relative_to(root).as_posix()


def is_included(path: Path) -> bool:
    if not path.is_file() or "__pycache__" in path.parts:
        return False
    rel = relative(path)
    if any(rel.startswith(prefix) for prefix in EXCLUDED_PREFIXES):
        return False
    if any(rel.startswith(prefix) for prefix in DEFERRED_POWERBI_PREFIXES):
        return False
    if path.name in EXCLUDED_NAMES or path.suffix.lower() in EXCLUDED_SUFFIXES:
        return False
    return True


def included_files(include_governance: bool = True) -> list[Path]:
    files = [path for path in ROOT.rglob("*") if is_included(path)]
    if not include_governance:
        files = [path for path in files if relative(path) not in MANIFEST_EXCLUSIONS]
    return sorted(files, key=relative)


def run_check(cwd: Path, command: list[str]) -> dict[str, object]:
    result = subprocess.run(command, cwd=cwd, capture_output=True, text=True, check=False)
    return {
        "command": " ".join([Path(command[0]).name, *command[1:]]),
        "status": "PASS" if result.returncode == 0 else "FAIL",
        "return_code": result.returncode,
        "output": (result.stdout + result.stderr).strip(),
    }


def count_pass_rows(path: Path) -> tuple[int, int]:
    rows = list(csv.DictReader(path.open(encoding="utf-8-sig", newline="")))
    passed = sum(str(row.get("status", "")).strip().upper() == "PASS" for row in rows)
    return passed, len(rows)


def find_author_paths(files: list[Path]) -> list[dict[str, str]]:
    findings: list[dict[str, str]] = []
    for path in files:
        if path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        text = path.read_text(encoding="utf-8-sig", errors="replace")
        for token in AUTHOR_PATH_TOKENS:
            if token.lower() in text.lower():
                findings.append({"path": relative(path), "token": token})
    return findings


def write_manifest(files: list[Path]) -> None:
    rows = [
        {"relative_path": relative(path), "size_bytes": path.stat().st_size, "sha256": sha256(path)}
        for path in files
    ]
    with MANIFEST.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["relative_path", "size_bytes", "sha256"])
        writer.writeheader()
        writer.writerows(rows)


def verify_manifest(root: Path) -> dict[str, object]:
    manifest_path = root / "validation" / "web_first_release_manifest.csv"
    rows = list(csv.DictReader(manifest_path.open(encoding="utf-8", newline="")))
    expected = {row["relative_path"] for row in rows}
    missing: list[str] = []
    mismatched: list[str] = []
    for row in rows:
        path = root / row["relative_path"]
        if not path.exists():
            missing.append(row["relative_path"])
        elif int(row["size_bytes"]) != path.stat().st_size or row["sha256"] != sha256(path):
            mismatched.append(row["relative_path"])

    if root.resolve() == ROOT.resolve():
        actual = {relative(path) for path in included_files(include_governance=False)}
    else:
        actual = {
            path.relative_to(root).as_posix()
            for path in root.rglob("*")
            if path.is_file() and path.relative_to(root).as_posix() not in MANIFEST_EXCLUSIONS
        }
    unlisted = sorted(actual - expected)
    return {
        "manifest_rows": len(rows),
        "missing_manifest_files": sorted(missing),
        "hash_mismatches": sorted(mismatched),
        "unlisted_files": unlisted,
        "status": "PASS" if not missing and not mismatched and not unlisted else "FAIL",
    }


def required_artifacts(root: Path) -> list[str]:
    required = [
        "OPEN_THIS_FIRST.html",
        "README.md",
        "PACKAGE_INDEX.md",
        "PACKAGE_README_WEB_FIRST.md",
        "dashboard/index.html",
        "excel/Project2_CreditPortfolioMonitoring_Gold_v2_1_4.xlsx",
        "reports/risk_committee_monitoring_memo.md",
        "validation/web_first_release_validation_report.md",
        "validation/web_first_release_manifest.csv",
        "validation/web_first_release_manifest_verification.json",
    ]
    return [item for item in required if not (root / item).exists()]


def validate_extracted_package(root: Path) -> dict[str, object]:
    manifest_result = verify_manifest(root)
    missing_required = required_artifacts(root)
    deferred_leaks = [
        path.relative_to(root).as_posix()
        for path in root.rglob("*")
        if path.is_file()
        and (
            path.relative_to(root).as_posix().startswith("powerbi/")
            or path.relative_to(root).as_posix().startswith("archive/deferred_powerbi/")
            or any(path.relative_to(root).as_posix().startswith(prefix) for prefix in DEFERRED_POWERBI_PREFIXES)
        )
    ]
    public_files = [path for path in root.rglob("*") if path.is_file()]
    author_paths = []
    for path in public_files:
        if path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        text = path.read_text(encoding="utf-8-sig", errors="replace")
        for token in AUTHOR_PATH_TOKENS:
            if token.lower() in text.lower():
                author_paths.append({"path": path.relative_to(root).as_posix(), "token": token})
    web_check = run_check(root, [sys.executable, "scripts/15_validate_web_dashboard.py"])
    status = (
        manifest_result["status"] == "PASS"
        and not missing_required
        and not deferred_leaks
        and not author_paths
        and web_check["status"] == "PASS"
    )
    return {
        "status": "PASS" if status else "FAIL",
        "manifest": manifest_result,
        "missing_required_files": missing_required,
        "deferred_powerbi_leaks": deferred_leaks,
        "author_local_path_findings": author_paths,
        "web_validator": web_check,
    }


def write_zip(output: Path) -> tuple[list[str], str | None]:
    files = included_files(include_governance=True)
    if output.exists():
        output.unlink()
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in files:
            archive_name = (Path(PACKAGE_ROOT) / path.relative_to(ROOT)).as_posix()
            archive.write(path, archive_name)
    with zipfile.ZipFile(output) as archive:
        names = archive.namelist()
        bad_member = archive.testzip()
    return names, bad_member


def clean_extract_check(output: Path) -> dict[str, object]:
    with tempfile.TemporaryDirectory(prefix="project2_web_release_") as temp_dir:
        temp_root = Path(temp_dir)
        with zipfile.ZipFile(output) as archive:
            archive.extractall(temp_root)
        return validate_extracted_package(temp_root / PACKAGE_ROOT)


def main() -> int:
    parser = argparse.ArgumentParser(description="Build the portable Project 2 Web-First Release v1.0 ZIP.")
    parser.add_argument("--output", type=Path, default=PORTFOLIO_ROOT / "_final_deliverables" / PACKAGE_NAME)
    args = parser.parse_args()
    output = args.output.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)

    web_check = run_check(ROOT, [sys.executable, "scripts/15_validate_web_dashboard.py"])
    row_checks = {}
    for label, path in {
        "analytical": ROOT / "validation/validation_checks.csv",
        "uat": ROOT / "testing/uat_test_cases.csv",
        "sit": ROOT / "testing/sit_test_cases.csv",
        "negative": ROOT / "testing/negative_test_cases.csv",
        "excel_reconciliation": ROOT / "validation/excel_formula_reconciliation.csv",
        "web": ROOT / "validation/web_dashboard_validation.csv",
    }.items():
        passed, total = count_pass_rows(path)
        row_checks[label] = {"passed": passed, "total": total, "status": "PASS" if passed == total else "FAIL"}

    public_files = included_files(include_governance=False)
    author_paths = find_author_paths(public_files)
    preflight_status = web_check["status"] == "PASS" and all(
        item["status"] == "PASS" for item in row_checks.values()
    ) and not author_paths
    PREFLIGHT.write_text(
        json.dumps(
            {
                "status": "PASS" if preflight_status else "FAIL",
                "release": "Project 2 Web-First Release v1.0",
                "analytical_baseline": "v2.1.4 reviewer-mode reproducibility checked",
                "web_validator": web_check,
                "control_counts": row_checks,
                "author_local_path_findings": author_paths,
                "excluded_prefixes": list(EXCLUDED_PREFIXES),
                "claim_boundary": "Power BI is intentionally excluded from the public Web-First release.",
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    if not preflight_status:
        raise SystemExit("Project 2 release preflight failed")

    write_manifest(included_files(include_governance=False))
    source_manifest = verify_manifest(ROOT)
    verification = {
        "status": source_manifest["status"],
        "release": "Project 2 Web-First Release v1.0",
        "manifest": "validation/web_first_release_manifest.csv",
        "manifest_sha256": sha256(MANIFEST),
        "manifest_scope_exclusions": sorted(MANIFEST_EXCLUSIONS),
        "source_tree_verification": source_manifest,
        "clean_extract_verification": "PENDING_PACKAGE_SERIALIZATION",
        "author_local_path_findings": author_paths,
    }
    VERIFICATION.write_text(json.dumps(verification, indent=2) + "\n", encoding="utf-8")

    names, bad_member = write_zip(output)
    first_clean = clean_extract_check(output)
    verification["clean_extract_verification"] = first_clean
    verification["status"] = "PASS" if source_manifest["status"] == "PASS" and first_clean["status"] == "PASS" else "FAIL"
    VERIFICATION.write_text(json.dumps(verification, indent=2) + "\n", encoding="utf-8")

    names, bad_member = write_zip(output)
    final_clean = clean_extract_check(output)
    backslash_entries = sum("\\" in name for name in names)
    status = verification["status"] == "PASS" and final_clean["status"] == "PASS" and bad_member is None and backslash_entries == 0
    result = {
        "status": "PASS" if status else "FAIL",
        "package_name": output.name,
        "size_bytes": output.stat().st_size,
        "sha256": sha256(output),
        "zip_entries": len(names),
        "backslash_entries": backslash_entries,
        "crc_bad_member": bad_member,
        "final_clean_extract": final_clean,
    }
    print(json.dumps(result, indent=2))
    return 0 if status else 1


if __name__ == "__main__":
    raise SystemExit(main())
