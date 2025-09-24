from __future__ import annotations
import argparse
from pathlib import Path
from rs3_study_curvature.etl.compute_curvature import build_from_config


def main():
    ap = argparse.ArgumentParser("build-curvature")
    ap.add_argument("--config", required=True)
    args = ap.parse_args()
    build_from_config(Path(args.config))


if __name__ == "__main__":
    main()
