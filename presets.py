# -*- coding: utf-8 -*-
"""FSO distance-bandwidth model presets (v3.0)

Design principle:
  Lock modulation pool to [DP-16QAM, DP-8QAM, DP-QPSK] (matching industry
  consensus: fix modulation at 8-16QAM, scale baud rate for throughput).
  Vary baud rate (32 / 60 Gbaud) and WDM channels (1 / 2).

Parameter sources: see parameter_audit.md
"""

from .link_model import FSOConfig

# Shared base parameters (space-qualified EDFA, 10cm aperture, 7dB margin)
_BASE = dict(
    tx_power_w=5.0,
    preamp_gain_db=40.0,
    preamp_nf_db=7.5,
    tx_aperture_m=0.10,
    rx_aperture_m=0.10,
    optical_efficiency=0.7,
    link_margin_db=7.0,
    terminal_cap_gbps=400.0,
)

# --- Core presets ---

# A: 32 Gbaud, WDM=1 -- classic discrete staircase
BS32_WDM1 = FSOConfig(
    baud_rate_ghz=32.0,
    modulation_pool=[(16, "DP-16QAM"), (8, "DP-8QAM"), (4, "DP-QPSK")],
    wdm_channels=1,
    **_BASE,
)

# B: 60 Gbaud, WDM=1 -- near-field hits 400 Gbps cap
BS60_WDM1 = FSOConfig(
    baud_rate_ghz=60.0,
    modulation_pool=[(16, "DP-16QAM"), (8, "DP-8QAM"), (4, "DP-QPSK")],
    wdm_channels=1,
    **_BASE,
)

# C: 60 Gbaud, WDM=2 -- dual-wavelength (SDA OISL standard)
BS60_WDM2 = FSOConfig(
    baud_rate_ghz=60.0,
    modulation_pool=[(16, "DP-16QAM"), (8, "DP-8QAM"), (4, "DP-QPSK")],
    wdm_channels=2,
    **_BASE,
)

# D: 32 Gbaud, WDM=2 -- dual-wavelength at conservative baud
BS32_WDM2 = FSOConfig(
    baud_rate_ghz=32.0,
    modulation_pool=[(16, "DP-16QAM"), (8, "DP-8QAM"), (4, "DP-QPSK")],
    wdm_channels=2,
    **_BASE,
)

# --- Exploratory presets ---

# E: High baud + QPSK only (most conservative, best verified)
HIGH_BAUD_QPSK_ONLY = FSOConfig(
    baud_rate_ghz=60.0,
    modulation_pool=[(4, "DP-QPSK")],
    wdm_channels=1,
    **_BASE,
)

# F: Low baud + high QAM (exploratory, physics-allowed, not space-verified)
LOW_BAUD_HIGH_QAM = FSOConfig(
    baud_rate_ghz=32.0,
    modulation_pool=[
        (64, "DP-64QAM"), (32, "DP-32QAM"),
        (16, "DP-16QAM"), (8, "DP-8QAM"), (4, "DP-QPSK"),
    ],
    wdm_channels=1,
    **_BASE,
)

# --- Registry ---
DEVICE_PRESETS = {
    "bs32_wdm1": BS32_WDM1,
    "bs60_wdm1": BS60_WDM1,
    "bs60_wdm2": BS60_WDM2,
    "bs32_wdm2": BS32_WDM2,
    "high_baud_qpsk_only": HIGH_BAUD_QPSK_ONLY,
    "low_baud_high_qam": LOW_BAUD_HIGH_QAM,
}
