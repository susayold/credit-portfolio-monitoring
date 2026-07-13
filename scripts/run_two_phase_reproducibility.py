from __future__ import annotations

import csv
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import zipfile
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PORTFOLIO_ROOT = ROOT.parent
DELIVERABLES = PORTFOLIO_ROOT / "_final_deliverables"
VERSION_STEM = "Project2_CreditPortfolioMonitoring_GoldCandidate_v2_1_4_REVIEWER_VERIFIED"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def checked_remove_tree(path: Path, allowed_parent: Path) -> None:
    resolved = path.resolve()
    parent = allowed_parent.resolve()
    if resolved == parent or parent not in resolved.parents:
        raise RuntimeError(f"Refusing to remove path outside controlled build workspace: {resolved}")
    if resolved.exists():
        shutil.rmtree(resolved)


def run_pipeline(project_root: Path, env: dict[str, str], capture: bool = False) -> subprocess.CompletedProcess[str]:
    completed = subprocess.run(
        [sys.executable, str(project_root / "scripts/run_full_pipeline.py")],
        cwd=project_root,
        env=env,
        check=True,
        text=True,
        capture_output=capture,
    )
    if capture:
        if completed.stdout:
            print(completed.stdout, end="")
        if completed.stderr:
            print(completed.stderr, end="", file=sys.stderr)
    return completed


def main() -> None:
    DELIVERABLES.mkdir(parents=True, exist_ok=True)
    build_parent = PORTFOLIO_ROOT / "_build_evidence" / "project2"
    build_parent.mkdir(parents=True, exist_ok=True)
    run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    workspace = build_parent / f"two_phase_{run_id}"
    author_root = workspace / "AUTHOR_BUILD" / ROOT.name
    clean_extract_root = workspace / "CLEAN_EXTRACT"
    workspace.mkdir(parents=True, exist_ok=False)

    try:
        print(f"[Two phase] Creating isolated author workspace: {author_root}", flush=True)
        shutil.copytree(
            ROOT,
            author_root,
            ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "author_reference"),
        )
        for relative in [
            "validation/deterministic_reference_hashes.json",
            "validation/deterministic_rebuild_comparison.csv",
            "validation/reference_temporal_validation.json",
        ]:
            candidate = author_root / relative
            if candidate.exists():
                candidate.unlink()

        author_env = os.environ.copy()
        author_env.update(
            {
                "P2_RUN_MODE": "author_reference",
                "P2_ALLOW_AUTHOR_REFERENCE_CAPTURE": "1",
                "P2_SKIP_PACKAGE": "1",
                "P2_REFRESH_REFERENCE_HASHES": "0",
                "P2_PIPELINE_TEMP_LOG": str(workspace / "author_pipeline_temp.json"),
            }
        )
        print("[Two phase] Running isolated author-reference build", flush=True)
        run_pipeline(author_root, author_env)

        author_reference_path = author_root / "validation/deterministic_reference_hashes.json"
        reference = json.loads(author_reference_path.read_text(encoding="utf-8"))
        reference_id = str(reference["reference_build_id"])
        author_bundle_dir = author_root / "validation/author_reference" / reference_id
        if not author_bundle_dir.exists():
            raise RuntimeError("Isolated author build did not create the governed reference bundle")

        main_author_root = ROOT / "validation/author_reference"
        if main_author_root.exists():
            checked_remove_tree(main_author_root, ROOT / "validation")
        main_author_root.mkdir(parents=True, exist_ok=True)
        shutil.copytree(author_bundle_dir, main_author_root / reference_id)
        shutil.copy2(author_reference_path, ROOT / "validation/deterministic_reference_hashes.json")

        reviewer_env = os.environ.copy()
        reviewer_env.update(
            {
                "P2_RUN_MODE": "reviewer",
                "P2_SKIP_PACKAGE": "0",
                "P2_REFRESH_REFERENCE_HASHES": "0",
                "P2_ALLOW_AUTHOR_REFERENCE_CAPTURE": "0",
                "P2_PIPELINE_TEMP_LOG": str(workspace / "reviewer_pipeline_temp.json"),
            }
        )
        print(f"[Two phase] Frozen author reference copied before reviewer start: {reference_id}", flush=True)
        print("[Two phase] Running later reviewer rebuild", flush=True)
        run_pipeline(ROOT, reviewer_env)

        full_zip = DELIVERABLES / f"{VERSION_STEM}.zip"
        if not full_zip.exists():
            raise RuntimeError(f"Final package was not created: {full_zip}")
        with zipfile.ZipFile(full_zip) as archive:
            backslash_paths = [name for name in archive.namelist() if "\\" in name]
            if backslash_paths:
                raise RuntimeError(f"Non-portable ZIP paths detected: {backslash_paths[:3]}")
            archive.extractall(clean_extract_root)
            zip_entry_count = len(archive.namelist())

        extracted_project = clean_extract_root / ROOT.name
        quick_env = os.environ.copy()
        quick_env["P2_RUN_MODE"] = "quick"
        print("[Two phase] Running final clean-extract quick validation", flush=True)
        quick = run_pipeline(extracted_project, quick_env, capture=True)
        sidecar = {
            "package_name": full_zip.name,
            "package_sha256": sha256(full_zip),
            "package_size_bytes": full_zip.stat().st_size,
            "zip_entry_count": zip_entry_count,
            "zip_forward_slash_paths": True,
            "clean_extract_path_used": "<TEMP_CLEAN_EXTRACT_WORKSPACE>",
            "quick_validation_return_code": quick.returncode,
            "quick_validation_result": "PASS_FINAL_CLEAN_EXTRACT",
            "quick_validation_output": quick.stdout.strip(),
            "author_reference_build_id": reference_id,
            "author_reference_generated_at": reference.get("generated_at"),
            "verified_at": datetime.now().isoformat(timespec="seconds"),
        }
        sidecar_path = DELIVERABLES / f"{VERSION_STEM}_CLEAN_EXTRACT_VERIFICATION.json"
        sidecar_path.write_text(json.dumps(sidecar, indent=2), encoding="utf-8")

        package_index = DELIVERABLES / f"{VERSION_STEM}_PACKAGE_INDEX.csv"
        rows = []
        if package_index.exists():
            with package_index.open("r", encoding="utf-8-sig", newline="") as handle:
                rows = list(csv.DictReader(handle))
        rows = [row for row in rows if row.get("package") != sidecar_path.name]
        rows.append(
            {
                "package": sidecar_path.name,
                "size_bytes": sidecar_path.stat().st_size,
                "purpose": "Detached SHA-256 and final clean-extract quick-validation evidence for the immutable ZIP",
            }
        )
        with package_index.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=["package", "size_bytes", "purpose"])
            writer.writeheader()
            writer.writerows(rows)

        print(f"[Two phase] PASS_AUTHOR_REVIEWER_RECONCILIATION: {full_zip}", flush=True)
        print(f"[Two phase] PASS_FINAL_CLEAN_EXTRACT: {sidecar_path}", flush=True)
    finally:
        if workspace.exists():
            checked_remove_tree(workspace, build_parent)


if __name__ == "__main__":
    main()
