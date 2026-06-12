# -*- coding: utf-8 -*-
"""Core FSO link-budget physics.

Physical engine for inter-satellite laser link simulation.
"""

from dataclasses import dataclass
from typing import List, Tuple
import math
import csv
import os

from config import FSOConfig, load_config_from_json

# ============================================================================
# Physical constants
# ============================================================================
C = 299_792_458.0          # speed of light [m/s]
H = 6.62607015e-34         # Planck constant [J*s]
PI = math.pi

# Photon energy at 1550 nm
NU_1550 = C / 1.55e-6      # ~193.4 THz
HNU = H * NU_1550           # ~1.28e-19 J


# ============================================================================
# Q-function approximation
# ============================================================================
def _qfunc(x: float) -> float:
    """Q(x) = 0.5 * erfc(x / sqrt(2))"""
    return 0.5 * math.erfc(x / math.sqrt(2.0))


# ============================================================================
# M-QAM BER formula (Gray mapping approximation)
# ============================================================================
def ber_mqam(M: int, snr_linear: float) -> float:
    """Approximate BER for M-QAM with Gray mapping.

    BER = 2*(sqrt(M)-1)/(sqrt(M)*log2(M)) * Q(sqrt(3*snr/(M-1)))

    Reference: Proakis J.G. Digital Communications, 5th ed., McGraw-Hill, 2008.
    """
    if M < 4:
        return 1.0
    sqrt_m = math.sqrt(M)
    coeff = 2.0 * (sqrt_m - 1.0) / (sqrt_m * math.log2(M))
    arg = math.sqrt(3.0 * snr_linear / (M - 1.0))
    return coeff * _qfunc(arg)


# ============================================================================
# Link budget result
# ============================================================================
@dataclass
class LinkResult:
    """Output of a single FSO link budget computation."""
    distance_km: float = 0.0
    received_power_dbm: float = 0.0
    path_loss_db: float = 0.0
    tx_antenna_gain_db: float = 0.0
    rx_antenna_gain_db: float = 0.0
    snr_db: float = 0.0
    snr_linear: float = 0.0
    modulation_order: int = 0
    modulation_label: str = ""
    feasible: bool = True
    per_channel_bw_gbps: float = 0.0
    total_bw_gbps: float = 0.0
    raw_total_bw_gbps: float = 0.0
    latency_ms: float = 0.0
    limiting_reason: str = ""


# ============================================================================
# Core physics functions (FIXED - do not modify)
# ============================================================================

def _antenna_gain_db(diameter_m: float, wavelength_m: float) -> float:
    """Diffraction-limited circular aperture gain.
    G = (pi * D / lambda)^2
    """
    if diameter_m <= 0 or wavelength_m <= 0:
        return 0.0
    g_linear = (PI * diameter_m / wavelength_m) ** 2
    return 10.0 * math.log10(g_linear)


def _path_loss_db(distance_m: float, wavelength_m: float) -> float:
    """Friis free-space path loss.
    L = (lambda / (4 * pi * d))^2
    Valid for far-field: d >> 2*D^2/lambda
    """
    if distance_m <= 0:
        raise ValueError(f"distance must be > 0, got {distance_m} m")
    l_linear = (wavelength_m / (4.0 * PI * distance_m)) ** 2
    return 10.0 * math.log10(l_linear)


def _edfa_snr(
    pr_linear_w: float,
    preamp_nf_db: float,
    baud_rate_hz: float,
) -> float:
    """Compute SNR after EDFA pre-amplifier (signal-ASE beat noise dominant).

    SNR = Pr / (2 * n_sp * h * nu * B_e)

    where n_sp = NF_linear / 2 (high-gain approximation).

    Reference: Agrawal G.P. Fiber-Optic Communication Systems, 5th ed., 2021, Sec 6.3-6.5.
    Formula only - EDFA parameter values from space-qualified sources (MPBC).

    This noise mechanism is identical whether the signal arrived via fiber or
    free-space propagation, once coupled into single-mode fiber before the EDFA.
    """
    if pr_linear_w <= 0:
        return 0.0
    nf_linear = 10.0 ** (preamp_nf_db / 10.0)
    n_sp = nf_linear / 2.0
    n_ase_per_hz = n_sp * HNU  # ASE power spectral density [W/Hz]
    snr = pr_linear_w / (2.0 * n_ase_per_hz * baud_rate_hz)
    return snr


def _select_modulation(
    snr_linear: float,
    ber_threshold: float,
    modulation_pool: List[Tuple[int, str]],
) -> Tuple[int, str, bool]:
    """Select highest modulation order satisfying BER threshold.

    Traverses pool from high to low M, returns first feasible format.
    Returns (M, label, feasible).
    When no format meets the threshold: (0, "infeasible", False).
    """
    for M, label in modulation_pool:
        if ber_mqam(M, snr_linear) <= ber_threshold:
            return M, label, True
    return 0, "infeasible", False


# ============================================================================
# Main computation
# ============================================================================

def compute_link(config: FSOConfig, distance_km: float) -> LinkResult:
    """Compute FSO link budget for a given distance and configuration.

    Flow: d -> Pr -> SNR -> select max M -> BW
    """
    if distance_km <= 0:
        raise ValueError(f"distance_km must be > 0, got {distance_km}")
    if config.tx_power_w <= 0:
        raise ValueError(f"tx_power_w must be > 0, got {config.tx_power_w}")

    distance_m = distance_km * 1e3

    # ---- Per-channel transmit power ----------------------------------------
    if config.wdm_power_mode == "per_channel_power_fixed":
        tx_per_ch_w = config.tx_power_w
    else:
        tx_per_ch_w = config.tx_power_w / config.wdm_channels
    tx_per_ch_dbm = 10.0 * math.log10(tx_per_ch_w * 1e3)

    # ---- Friis -> received power -------------------------------------------
    g_tx_db = _antenna_gain_db(config.tx_aperture_m, config.wavelength_m)
    g_rx_db = _antenna_gain_db(config.rx_aperture_m, config.wavelength_m)
    l_fs_db = _path_loss_db(distance_m, config.wavelength_m)
    eta_db = (10.0 * math.log10(config.optical_efficiency)
              if config.optical_efficiency > 0 else -99.0)

    pr_dbm = tx_per_ch_dbm + g_tx_db + g_rx_db + l_fs_db + eta_db - config.link_margin_db
    pr_w = 1e-3 * (10.0 ** (pr_dbm / 10.0))

    # ---- SNR after EDFA pre-amp --------------------------------------------
    baud_rate_hz = config.baud_rate_ghz * 1e9
    snr_linear = _edfa_snr(
        pr_linear_w=pr_w,
        preamp_nf_db=config.preamp_nf_db,
        baud_rate_hz=baud_rate_hz,
    )
    snr_db = 10.0 * math.log10(snr_linear) if snr_linear > 0 else -99.0

    # DP penalty: SNR per polarization is halved
    if config.dual_polarization:
        snr_pol_linear = snr_linear / 2.0
        snr_pol_db = snr_db - 3.0
    else:
        snr_pol_linear = snr_linear
        snr_pol_db = snr_db

    # ---- Select modulation -------------------------------------------------
    M, label, feasible = _select_modulation(
        snr_pol_linear,
        ber_threshold=config.ber_threshold,
        modulation_pool=config.modulation_pool,
    )

    # ---- Bandwidth ---------------------------------------------------------
    if feasible and M > 0:
        fec_eff = 1.0 - config.fec_overhead
        dp_factor = 2.0 if config.dual_polarization else 1.0
        per_ch_bw = config.baud_rate_ghz * math.log2(M) * dp_factor * fec_eff
    else:
        per_ch_bw = 0.0

    total_bw = per_ch_bw * config.wdm_channels
    raw_total = total_bw

    # Apply terminal hardware cap
    if config.terminal_cap_gbps is not None:
        per_ch_bw = min(per_ch_bw, config.terminal_cap_gbps)
        total_bw = min(total_bw, config.terminal_cap_gbps)

    # ---- Latency -----------------------------------------------------------
    latency_ms = (distance_m / C) * 1e3

    # ---- Limiting reason ---------------------------------------------------
    limiting_reason = ""
    if not feasible:
        limiting_reason = (
            f"SNR {snr_pol_db:.1f} dB insufficient for any modulation "
            f"at BER={config.ber_threshold:.0e}"
        )
    elif total_bw <= 0:
        limiting_reason = "Total bandwidth zero"

    return LinkResult(
        distance_km=distance_km,
        received_power_dbm=pr_dbm,
        path_loss_db=l_fs_db,
        tx_antenna_gain_db=g_tx_db,
        rx_antenna_gain_db=g_rx_db,
        snr_db=snr_pol_db,
        snr_linear=snr_pol_linear,
        modulation_order=M,
        modulation_label=label,
        feasible=feasible,
        per_channel_bw_gbps=per_ch_bw,
        total_bw_gbps=total_bw,
        raw_total_bw_gbps=raw_total,
        latency_ms=latency_ms,
        limiting_reason=limiting_reason,
    )


# ============================================================================
# Sweep utilities
# ============================================================================

def sweep_distances(
    config: FSOConfig,
    distances_km: List[float],
) -> List[LinkResult]:
    """Run link budget for a list of distances."""
    return [compute_link(config, d) for d in distances_km]


def geomspace(start: float, end: float, points: int) -> List[float]:
    """Return geometric-spaced values without requiring external packages."""
    if start <= 0 or end <= 0:
        raise ValueError("geometric distance bounds must be > 0")
    if points <= 0:
        raise ValueError("points must be > 0")
    if points == 1:
        return [start]

    log_start = math.log(start)
    log_end = math.log(end)
    return [
        math.exp(log_start + (log_end - log_start) * i / (points - 1))
        for i in range(points)
    ]


def sweep_range(
    config: FSOConfig,
    start_km: float = 100.0,
    end_km: float = 5000.0,
    points: int = 20,
) -> List[LinkResult]:
    """Run link budget over a geometric-spaced range of distances."""
    return sweep_distances(config, geomspace(start_km, end_km, points))


def print_table(results: List[LinkResult]) -> None:
    """Print results as formatted table.

    Shows raw (physics-only) and capped (hardware-limited) bandwidth
    side by side when a terminal cap is active.
    """
    has_cap = any(r.raw_total_bw_gbps != r.total_bw_gbps for r in results)
    if has_cap:
        header = (
            f"{'Dist(km)':>10s}  {'Lat(ms)':>8s}  {'SNR(dB)':>8s}  "
            f"{'Modulation':>14s}  {'Raw BW':>10s}  {'Capped':>10s}  {'OK':>5s}"
        )
    else:
        header = (
            f"{'Dist(km)':>10s}  {'Lat(ms)':>8s}  {'SNR(dB)':>8s}  "
            f"{'Modulation':>14s}  {'BW(Gbps)':>10s}  {'OK':>5s}"
        )
    sep = "-" * len(header)
    print(sep)
    print(header)
    print(sep)
    for r in results:
        if has_cap and r.feasible:
            print(
                f"{r.distance_km:10.1f}  {r.latency_ms:8.2f}  {r.snr_db:8.2f}  "
                f"{r.modulation_label:>14s}  {r.raw_total_bw_gbps:10.1f}  {r.total_bw_gbps:10.1f}  "
                f"{'YES' if r.feasible else 'NO':>5s}"
            )
        else:
            bw_str = f"{r.total_bw_gbps:10.1f}" if r.feasible else ""
            print(
                f"{r.distance_km:10.1f}  {r.latency_ms:8.2f}  {r.snr_db:8.2f}  "
                f"{r.modulation_label:>14s}  {'':>10s}  {bw_str:>10s}  "
                f"{'YES' if r.feasible else 'NO':>5s}"
            )
    print(sep)

def save_csv(results: List[LinkResult], filepath: str) -> None:
    """Save results to CSV."""
    os.makedirs(os.path.dirname(filepath) or ".", exist_ok=True)
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow([
            "distance_km", "latency_ms", "received_power_dbm",
            "path_loss_db", "snr_db", "modulation_label",
            "modulation_order", "per_channel_bw_gbps",
            "total_bw_gbps", "feasible", "limiting_reason",
        ])
        for r in results:
            w.writerow([
                f"{r.distance_km:.1f}",
                f"{r.latency_ms:.3f}",
                f"{r.received_power_dbm:.2f}",
                f"{r.path_loss_db:.2f}",
                f"{r.snr_db:.2f}",
                r.modulation_label,
                r.modulation_order,
                f"{r.per_channel_bw_gbps:.2f}",
                f"{r.total_bw_gbps:.2f}",
                "True" if r.feasible else "False",
                r.limiting_reason,
            ])
    print(f"Saved {len(results)} rows to {filepath}")


# ============================================================================
# Quick-run entry point
# ============================================================================
if __name__ == "__main__":
    cfg_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "configs",
        "google_constellation.json",
    )
    cfg = load_config_from_json(cfg_path)
    from validator import validate_config, pre_check_link_feasibility, ValidationError

    try:
        validate_config(cfg)
        pre_check_link_feasibility(cfg)
    except ValidationError as e:
        import sys
        print(f"Config validation failed: {e.message}", file=sys.stderr)
        sys.exit(1)

    results = sweep_range(cfg, 100, 5000, 15)

    print()
    print(f"Config: {cfg_path}")
    print(f"Waveform: {cfg.baud_rate_ghz} Gbaud, WDM={cfg.wdm_channels}, "
          f"Pool={[m[1] for m in cfg.modulation_pool]}")
    print(f"EDFA: {cfg.tx_power_w}W booster, "
          f"G={cfg.preamp_gain_db}dB / NF={cfg.preamp_nf_db}dB")
    print(f"Aperture: {cfg.tx_aperture_m*100:.0f}cm | Margin: {cfg.link_margin_db}dB "
          f"| Cap: {cfg.terminal_cap_gbps}Gbps")
    print()

    print_table(results)
