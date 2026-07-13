from __future__ import annotations

from project2_gold_validation import compare_deterministic_rebuild_outputs


def main() -> None:
    comparison = compare_deterministic_rebuild_outputs()
    failed = comparison[comparison["status"].eq("FAIL")]
    print(f"Deterministic rebuild comparison: {len(comparison) - len(failed)}/{len(comparison)} PASS")
    if not failed.empty:
        raise SystemExit("Deterministic rebuild comparison failed")


if __name__ == "__main__":
    main()
