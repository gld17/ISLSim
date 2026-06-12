# ISLSim — Inter-Satellite Laser Link Simulation

## Overview

ISLSim is a lightweight FSO simulator for estimating distance, SNR, feasible modulation, bandwidth, and latency for inter-satellite laser links.

ISLSim 是一个轻量级自由空间光通信星间链路仿真器，用于估计不同距离下的接收功率、SNR、可用调制格式、带宽和传播时延。

## Physical Model

### 物理模型

本模型关注波特率与调制阶数之间的“等速率异构”问题：同样的比特速率可以由不同技术组合实现。例如，高波特率加低调制阶数，或低波特率加高调制阶数，都可能达到相近吞吐量。但这两类方案在相同距离下对应的 SNR、BER 和可支持距离区间并不相同。

模型不判断哪种方案“更优”，而是回答：在给定发射功率、孔径、波长、EDFA 噪声、链路余量、FEC 开销和调制池的条件下，各距离档位能支持多少带宽。

建模流程：

```text
d(t) -> Pr(t) -> SNR(t) -> max M(t) -> BW(t)
```

核心物理过程：

- Friis free-space path loss：根据距离、波长和收发孔径计算自由空间链路预算。
- EDFA SNR：使用 EDFA 前置放大器噪声模型估算信号 ASE 主导条件下的 SNR。
- M-QAM BER selection：对调制池中的 M-QAM 格式计算近似 BER，并选择满足 BER 门限的最高阶调制。

References:

- Friis, H.T. Proc. IRE, 1946. (Friis transmission equation)
- Agrawal G.P. Fiber-Optic Communication Systems, 5th ed., Wiley, 2021. (ASE noise)
- Proakis J.G. Digital Communications, 5th ed., McGraw-Hill, 2008. (M-QAM BER)
- MPBC Space-Qualified Amplifiers [mpbcommunications.com/space]
- PhotoniCore 5W EYDFA for SPACE [photonicore.com.tw]
- SDA OISL Standard v2.1.2 [sda.mil]
- Beijing S&T Commission: 400 Gbps in-orbit demo [kw.beijing.gov.cn, 2025.03]

## Installation

项目需要 Python 3，无需额外依赖。默认配置文件位于 `configs/google_constellation.json`。

```bash
python --version
```

## Usage

运行默认距离扫描：

```bash
python link_model.py
```

运行 sweep CLI：

```bash
python sweep.py
```

运行单距离测试：

```bash
python point_test.py --distance-km 1000
```

也可以指定配置文件和输出 CSV：

```bash
python sweep.py --config configs/google_constellation.json --output results/google.csv
```

## Configuration

配置文件使用 JSON，顶层包含 `tx`、`rx` 和 `channel` 三个对象，分别对应 `config.py` 中的 `TXConfig`、`RXConfig` 和 `ChannelConfig`。

`TXConfig` — 发射端硬件与波形参数：

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

`RXConfig` — 接收端硬件参数：

| Field | Description |
| --- | --- |
| `rx_aperture_m` | Receive aperture [m] |
| `preamp_gain_db` | EDFA gain [dB] |
| `preamp_nf_db` | EDFA noise figure [dB] |
| `ber_threshold` | BER threshold |
| `terminal_cap_gbps` | Terminal bandwidth cap [Gbps]; set to `null` to disable |

`ChannelConfig` — 信道参数：

| Field | Description |
| --- | --- |
| `link_margin_db` | Link margin [dB] |
| `optical_efficiency` | Optical efficiency |

`FSOConfig` 将三个配置段组合为一个链路配置对象，并暴露 `cfg.tx_power_w`、`cfg.rx_aperture_m`、`cfg.link_margin_db` 等扁平属性，供现有计算代码使用。

## Project Layout

```text
├── config.py              # Configuration dataclasses
├── link_model.py          # Core link-budget physics
├── sweep.py               # Distance-sweep CLI
├── point_test.py          # Single-distance CLI
├── validator.py           # Config validation and pre-check
├── configs/               # JSON configuration files
└── README.md              # This file
```
