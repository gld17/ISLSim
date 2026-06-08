# -*- coding: utf-8 -*-
"""
FSO distance-bandwidth sweep script (v3.0)
===========================================
Usage:
  python -m src.fso_link_model.sweep                        # default (bs32_wdm1)
  python -m src.fso_link_model.sweep --preset bs60_wdm1
  python -m src.fso_link_model.sweep --preset low_baud_high_qam

Available presets:
  bs32_wdm1         32 Gbaud, WDM=1, 16/8/QPSK  (classic staircase)
  bs60_wdm1         60 Gbaud, WDM=1, 16/8/QPSK  (near-field hits 400 cap)
  bs60_wdm2         60 Gbaud, WDM=2, 16/8/QPSK  (SDA dual-lambda)
  bs32_wdm2         32 Gbaud, WDM=2, 16/8/QPSK
  high_baud_qpsk_only  60 Gbaud, QPSK only (most conservative)
  low_baud_high_qam    32 Gbaud, up to 64QAM (exploratory)

Physical engine is in link_model.py.
"""

import argparse
import os
import sys
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.fso_link_model.link_model import (
    FSOConfig, sweep_distances, print_table, save_csv,
)
from src.fso_link_model.presets import DEVICE_PRESETS


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="FSO distance-bandwidth sweep")
    parser.add_argument("--preset", default="bs32_wdm1",
                        choices=list(DEVICE_PRESETS.keys()),
                        help="Device preset")
    parser.add_argument("--distance-min-km", type=float, default=100.0)
    parser.add_argument("--distance-max-km", type=float, default=5000.0)
    parser.add_argument("--distance-points", type=int, default=15)
    parser.add_argument("--output", type=str, default=None,
                        help="CSV output path")
    args = parser.parse_args()

    cfg = DEVICE_PRESETS[args.preset]

    distances = np.geomspace(
        args.distance_min_km, args.distance_max_km, args.distance_points
    )
    results = sweep_distances(cfg, list(distances))

    print()
    print(f"Preset: {args.preset}")
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
            os.path.dirname(os.path.abspath(__file__)), "..", "..",
            "docs", "loops", "2026-05-31-fso-distance-bandwidth-model", "results",
        )
        os.makedirs(out_dir, exist_ok=True)
        out_path = os.path.join(out_dir, f"distance_bw_{args.preset}.csv")

    save_csv(results, out_path)
