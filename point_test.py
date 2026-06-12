# -*- coding: utf-8 -*-
"""Single-distance FSO link bandwidth test."""

import argparse

from config import load_config_from_json
from link_model import compute_link
from validator import validate_config, pre_check_link_feasibility, ValidationError


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Compute FSO bandwidth at a single distance"
    )
    parser.add_argument(
        "--distance-km",
        type=float,
        required=True,
        help="Inter-satellite distance in km",
    )
    parser.add_argument(
        "--config",
        default="configs/google_constellation.json",
        help="JSON config path",
    )
    args = parser.parse_args()

    config = load_config_from_json(args.config)
    try:
        validate_config(config)
        pre_check_link_feasibility(config)
    except ValidationError as e:
        import sys
        print(f"Config validation failed: {e.message}", file=sys.stderr)
        sys.exit(1)

    result = compute_link(config, args.distance_km)

    if result.feasible:
        print(result.total_bw_gbps)
    else:
        print(0.0)


if __name__ == "__main__":
    main()
