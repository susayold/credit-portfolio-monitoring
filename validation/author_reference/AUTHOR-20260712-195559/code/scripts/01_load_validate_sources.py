from project2_gold_common import load_validate_sources, phase0_methodology_lock


if __name__ == "__main__":
    phase0_methodology_lock()
    load_validate_sources()
    print("Phase 0/1 source validation PASS")
