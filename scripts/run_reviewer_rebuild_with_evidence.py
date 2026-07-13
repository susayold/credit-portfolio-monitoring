from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    env = os.environ.copy()
    env["P2_RUN_MODE"] = "reviewer"
    env.setdefault("P2_REFRESH_REFERENCE_HASHES", "0")
    subprocess.run([sys.executable, str(ROOT / "scripts" / "run_full_pipeline.py")], cwd=ROOT, check=True, env=env)


if __name__ == "__main__":
    main()
