# ISLSim — Inter-Satellite Laser Link Simulation

ISLSim is a lightweight simulator for estimating the relationship between distance and bandwidth in free-space optical (FSO) inter-satellite links. Given transmit power, aperture, wavelength, link margin, EDFA noise, modulation format, and FEC overhead, the model computes received power, SNR, feasible modulation format, throughput, and propagation latency at a specified distance.

## Installation

The project requires Python 3. Earlier versions used NumPy for geometric distance sampling; the current entry scripts include an equivalent built-in sampler, so NumPy is not required. Install it only if your own extensions still depend on it:

```bash
python -m pip install numpy
```

No additional data files are required. The default configuration is at `configs/google_constellation.json`.

## Usage

Run the default single-link calculation:

```bash
python link_model.py
```

Run a distance sweep with the default Google constellation scenario:

```bash
python sweep.py
```

Specify a config file and output CSV:

```bash
python sweep.py --config configs/google_constellation.json --output results/google.csv
```

Adjust the distance range:

```bash
python sweep.py --distance-min-km 100 --distance-max-km 5000 --distance-points 20
```

## Configuration

Configuration files use JSON. The top level has three objects — `tx`, `rx`, and `channel` — corresponding to the three config classes in `config.py`.

`TXConfig` — transmit-side hardware and waveform parameters:

| Field | Description |
| --- | --- |
| `tx_power_w` | Transmit power [W] |
| `tx_aperture_m` | Transmit aperture [m] |
| `wavelength_m` | Operating wavelength [m]; default `1.55e-6` |
| `baud_rate_ghz` | Symbol rate [GHz] |
| `wdm_channels` | Number of WDM channels |
| `fec_overhead` | FEC overhead fraction |
| `dual_polarization` | Enable dual polarization |
| `wdm_power_mode` | WDM power mode, e.g. `total_power_fixed` |
| `modulation_pool` | List of `[order, label]` pairs, e.g. `[[16, "DP-16QAM"], [8, "DP-8QAM"], [4, "DP-QPSK"]]` |

`RXConfig` — receive-side hardware parameters:

| Field | Description |
| --- | --- |
| `rx_aperture_m` | Receive aperture [m] |
| `preamp_gain_db` | EDFA gain [dB] |
| `preamp_nf_db` | EDFA noise figure [dB] |
| `ber_threshold` | BER threshold |
| `terminal_cap_gbps` | Terminal bandwidth cap [Gbps]; set to `null` to disable |

`ChannelConfig` — channel parameters:

| Field | Description |
| --- | --- |
| `link_margin_db` | Link margin [dB] |
| `optical_efficiency` | Optical efficiency |

`FSOConfig` combines the three sections into one link configuration object. It also exposes flat attributes such as `cfg.tx_power_w`, `cfg.rx_aperture_m`, and `cfg.link_margin_db` so existing computation code can keep using the same access pattern.

## Project layout

```text
.
├── config.py                         # Config dataclasses, JSON load/export
├── configs/
│   └── google_constellation.json     # Example Google constellation scenario
├── link_model.py                     # Core link-budget physics
├── sweep.py                          # Distance-sweep CLI entry point
├── results/                          # Default sweep output directory (created on run)
└── README.md                         # This file
```
