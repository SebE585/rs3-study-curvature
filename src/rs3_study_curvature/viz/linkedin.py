"""
Compat pour: python -m rs3_study_curvature.viz.linkedin carte|distrib
"""

import argparse
from rs3_study_curvature.workflows import linkedin as wf


def carte():
    p = argparse.ArgumentParser()
    p.add_argument("--out-dir", required=True)
    p.add_argument("--bbox", nargs=4, required=True, type=float)
    p.add_argument("--street", default=None)
    p.add_argument("--street-buffer-m", type=float, default=40)
    p.add_argument("--plot-centroids", action="store_true")
    p.add_argument("--fit-clothoid", action="store_true")
    p.add_argument("--clothoid-step-m", type=float, default=8.0)
    p.add_argument("--clothoid-window-m", type=float, default=60.0)
    p.add_argument("--clothoid-r2-min", type=float, default=0.7)
    args = p.parse_args()
    wf.run_map(
        out_dir=args.out_dir,
        bbox=tuple(args.bbox),
        street=args.street,
        street_buffer_m=args.street_buffer_m,
        plot_centroids=args.plot_centroids,
        fit_clothoid=args.fit_clothoid,
        clothoid_step_m=args.clothoid_step_m,
        clothoid_window_m=args.clothoid_window_m,
        clothoid_r2_min=args.clothoid_r2_min,
    )


def distrib():
    p = argparse.ArgumentParser()
    p.add_argument("--out-dir", required=True)
    p.add_argument("--bbox", nargs=4, required=True, type=float)
    args = p.parse_args()
    wf.run_distrib(out_dir=args.out_dir, bbox=tuple(args.bbox))


if __name__ == "__main__":
    import sys

    cmd = (sys.argv[1] if len(sys.argv) > 1 else "").lower()
    sys.argv = [sys.argv[0]] + sys.argv[2:]
    if cmd == "carte":
        carte()
    elif cmd == "distrib":
        distrib()
    else:
        print("Utilisation: python -m rs3_study_curvature.viz.linkedin [carte|distrib] <options>")
