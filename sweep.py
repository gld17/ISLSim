# -*- coding: utf-8 -*-
"""
FSO distance-bandwidth sweep script (v3.0)
===========================================
Usage:
  python sweep.py
  python sweep.py --config configs/google_constellation.json

Physical engine is in link_model.py.
"""

import argparse
import os

from config import FSOConfig, load_config_from_json
from link_model import geomspace, sweep_distances, print_table, save_csv
from validator import validate_config, pre_check_link_feasibility, ValidationError


if __name__ == "__main__":
    default_config = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "configs",
        "google_constellation.json",
    )
    parser = argparse.ArgumentParser(description="FSO distance-bandwidth sweep")
    parser.add_argument("--config", default=default_config,
                        help="JSON config path")
    parser.add_argument("--distance-min-km", type=float, default=100.0)
    parser.add_argument("--distance-max-km", type=float, default=5000.0)
    parser.add_argument("--distance-points", type=int, default=15)
    parser.add_argument("--output", type=str, default=None,
                        help="CSV output path")
    args = parser.parse_args()

    cfg: FSOConfig = load_config_from_json(args.config)
    try:
        validate_config(cfg)
        pre_check_link_feasibility(cfg)
    except ValidationError as e:
        import sys
        print(f"Config validation failed: {e.message}", file=sys.stderr)
        sys.exit(1)

    distances = geomspace(
        args.distance_min_km, args.distance_max_km, args.distance_points
    )
    results = sweep_distances(cfg, distances)

    print()
    print(f"Config: {args.config}")
    print(f"  Bs={cfg.baud_rate_ghz} Gbaud | WDM={cfg.wdm_channels} | "
          f"Pool={[m[1] for m in cfg.modulation_pool]}")
    print(f"  EDFA: {cfg.tx_power_w}W booster, "
          f"G={cfg.preamp_gain_db}dB / NF={cfg.preamp_nf_db}dB")
    print(f"  Aperture: {cfg.tx_aperture_m*100:.0f}cm | Margin: {cfg.link_margin_db}dB "
          f"| Cap: {cfg.terminal_cap_gbps}Gbps")
    print()

    print_table(results)

    # CSV output
    if args.output:
        out_path = args.output
    else:
        out_dir = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "results",
        )
        os.makedirs(out_dir, exist_ok=True)
        config_name = os.path.splitext(os.path.basename(args.config))[0]
        out_path = os.path.join(out_dir, f"distance_bw_{config_name}.csv")

    save_csv(results, out_path)
