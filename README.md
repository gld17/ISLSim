# ISLSim 星间激光链路仿真

ISLSim 是一个用于估算星间自由空间光通信链路距离和带宽关系的轻量级仿真项目。模型根据发射功率、孔径、波长、链路余量、EDFA 噪声、调制格式和 FEC 开销，计算指定距离下的接收功率、SNR、可用调制格式、吞吐量和传播时延。

## 安装说明

项目运行依赖 Python 3。早期版本使用 numpy 做几何距离采样；当前入口脚本已内置等价采样函数，不强制依赖 numpy。若你的扩展脚本仍使用 numpy，可按需安装：

```bash
python -m pip install numpy
```

不需要额外的数据文件。默认配置位于 `configs/google_constellation.json`。

## 使用示例

运行默认链路计算：

```bash
python link_model.py
```

运行距离扫描，并使用默认 Google 星座通信场景配置：

```bash
python sweep.py
```

指定配置文件和输出 CSV：

```bash
python sweep.py --config configs/google_constellation.json --output results/google.csv
```

调整距离范围：

```bash
python sweep.py --distance-min-km 100 --distance-max-km 5000 --distance-points 20
```

## 配置说明

配置文件采用 JSON 格式，顶层包含 `tx`、`rx` 和 `channel` 三个对象，对应 `config.py` 中的三个配置类。

`TXConfig` 表示发射端硬件和波形参数：

| 字段 | 含义 |
| --- | --- |
| `tx_power_w` | 发射功率，单位 W |
| `tx_aperture_m` | 发射孔径，单位 m |
| `wavelength_m` | 工作波长，单位 m，默认 1.55e-6 |
| `baud_rate_ghz` | 波特率，单位 GHz |
| `wdm_channels` | WDM 通道数 |
| `fec_overhead` | FEC 开销比例 |
| `dual_polarization` | 是否启用双极化 |
| `wdm_power_mode` | WDM 功率模式，例如 `total_power_fixed` |
| `modulation_pool` | 调制阶数和标签列表，例如 `[[16, "DP-16QAM"], [8, "DP-8QAM"], [4, "DP-QPSK"]]` |

`RXConfig` 表示接收端硬件参数：

| 字段 | 含义 |
| --- | --- |
| `rx_aperture_m` | 接收孔径，单位 m |
| `preamp_gain_db` | EDFA 增益，单位 dB |
| `preamp_nf_db` | EDFA 噪声系数，单位 dB |
| `ber_threshold` | BER 门限 |
| `terminal_cap_gbps` | 终端带宽上限，单位 Gbps；设为 `null` 可关闭上限 |

`ChannelConfig` 表示信道参数：

| 字段 | 含义 |
| --- | --- |
| `link_margin_db` | 链路余量，单位 dB |
| `optical_efficiency` | 光效率 |

`FSOConfig` 将上述三类配置组合为一个链路配置对象，同时保留 `cfg.tx_power_w`、`cfg.rx_aperture_m`、`cfg.link_margin_db` 这类扁平属性访问方式，便于现有计算函数继续使用。

## 项目结构

```text
.
├── config.py                         # 配置 dataclass、JSON 加载和导出
├── configs/
│   └── google_constellation.json     # Google 星座通信场景示例配置
├── link_model.py                     # 核心链路物理计算
├── sweep.py                          # 距离扫描入口
├── results/                          # sweep.py 默认输出目录，运行后生成
└── README.md                         # 项目说明
```
