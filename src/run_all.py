"""Reproduce the complete published analytical pipeline."""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

from common import ROOT


def run(*args: str) -> None:
    print("\n>", " ".join(args), flush=True)
    subprocess.run(args, cwd=ROOT, check=True)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--use-snapshot",
        action="store_true",
        help="Use the dated, checksummed snapshot that produced the published results.",
    )
    args = parser.parse_args()
    python = sys.executable
    snapshot = Path("data/raw/clinical_trials_2026-07-31.json")

    if not args.use_snapshot:
        run(python, "src/extract_clinical_trials.py")
    run(python, "src/build_foundation.py", "--snapshot", str(snapshot))
    run(python, "src/build_country_reference.py")
    run(python, "src/create_audit_sample.py")
    run(python, "src/build_decision_model.py")
    run(python, "src/create_group2_figures.py")
    run(python, "src/run_portfolio_optimisation.py")
    run(python, "src/run_robustness_analysis.py")
    run(python, "src/create_group3_figures.py")
    run(python, "-m", "unittest", "discover", "-s", "tests", "-v")


if __name__ == "__main__":
    main()
