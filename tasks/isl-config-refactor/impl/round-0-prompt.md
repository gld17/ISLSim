# Round 0 任务

## 强制执行规则
你必须遵守 pbr-codex-builder skill。若未加载该 skill，也必须遵守：
1. 你是唯一 Builder，只写代码。
2. 不做 review 判断。
3. 不执行任何 git 命令。
4. 完成后必须写入指定 summary 文件。

## 重要限制
- **不要执行 git 命令**：如果你需要重命名文件，请直接创建新文件并写入内容，然后删除旧文件。不要尝试 `git mv`（你会被拒绝）。Kimi 会在后续 commit 阶段处理 git 历史追溯性。
- 所有文件操作（创建、修改、删除）通过 Hermes 工具完成，不直接输出代码到对话中。
- 每次修改文件后，检查是否有 include 路径、import 路径或其他引用需要同步更新。
- 修改前先在相关文件中搜索所有引用，确认修改的安全性。
- 本项目不使用 `sys.path.insert` 等运行时路径修改，导入方式统一为相对导入或项目根目录绝对导入。

## 项目当前结构

```
/share/guolidong-nfs/SeeSpace/ISLSim/
├── link_model.py    # 包含 FSOConfig dataclass 和核心物理计算
├── presets.py       # 包含 BS32_WDM1 等预设配置（需要删除/清空）
├── sweep.py         # 扫描脚本，引用 presets.py
└── tasks/           # PBR 任务目录（不要修改）
```

## 本轮需完成的工作

根据 plan.md 的 AC-1 到 AC-6，完成以下全部工作：

### 1. 创建 config.py
- 定义三个 dataclass：
  - `TXConfig`：发射端硬件参数
    - tx_power_w (float)：发射功率 [W]
    - tx_aperture_m (float)：发射孔径 [m]
    - wavelength_m (float)：波长 [m]，默认 1.55e-6
    - baud_rate_ghz (float)：波特率 [GHz]
    - wdm_channels (int)：WDM 通道数
    - fec_overhead (float)：FEC 开销比例
    - dual_polarization (bool)：是否双极化
    - wdm_power_mode (str)：WDM 功率模式，如 "total_power_fixed"
    - modulation_pool (List[Tuple[int, str]])：调制阶数与标签列表，如 [(16, "DP-16QAM"), (8, "DP-8QAM"), (4, "DP-QPSK")]
  - `RXConfig`：接收端硬件参数
    - rx_aperture_m (float)：接收孔径 [m]
    - preamp_gain_db (float)：EDFA 增益 [dB]
    - preamp_nf_db (float)：EDFA 噪声系数 [dB]
    - ber_threshold (float)：BER 门限
    - terminal_cap_gbps (Optional[float])：终端带宽上限 [Gbps]
  - `ChannelConfig`：信道配置
    - link_margin_db (float)：链路余量 [dB]
    - optical_efficiency (float)：光效率
- 定义一个 `FSOConfig` 类（可用 dataclass），将上述三个配置组合在一起，提供向后兼容的属性访问方式（如通过 property 或直接字段）。保持 `link_model.py` 中 `compute_link` 函数接口尽量不变。
- 提供从 JSON 文件加载配置的函数 `load_config_from_json(filepath) -> FSOConfig`。
- 提供将 `FSOConfig` 导出为字典的函数 `config_to_dict(config) -> dict`。

### 2. 创建 configs/ 目录和 google_constellation.json
- 在项目根目录创建 `configs/` 目录。
- 创建 `configs/google_constellation.json`，包含完整的 Google 星座通信场景参数。
- 参数值基于 Starlink / Project Kuiper 等星座通信的公开技术文献合理设定：
  - 发射功率：~5W（类似 MPBC 空间级 EDFA）
  - 孔径：~10cm（类似 Mynaric CONDOR）
  - 波长：1550nm（C 波段标准）
  - 波特率：60 Gbaud（高速相干通信）
  - WDM：2 通道（双波长标准）
  - EDFA 增益：40 dB，噪声系数 7.5 dB
  - BER 门限：1e-3（HD-FEC）
  - 终端带宽上限：400 Gbps
  - 链路余量：7 dB
  - 光效率：0.7

### 3. 修改 link_model.py
- 从 `link_model.py` 中移除 `FSOConfig` dataclass 定义，改为从 `config.py` 导入。
- 清理所有引用缺失外部文档的注释（如 `parameter_audit.md`、`docs/loops/...` 等）。
- 保留核心物理公式的必要注释（Friis、EDFA SNR、M-QAM BER 等）。
- `__main__` 块中的示例代码需要调整，不再引用 `presets.py`，改为从 `configs/google_constellation.json` 加载配置或创建默认配置。

### 4. 修改 sweep.py
- 移除 `sys.path.insert` 运行时路径修改。
- 移除对 `presets.py` 的导入。
- 改为从 `config.py` 导入 `FSOConfig` 和配置加载函数。
- `--preset` 参数改为 `--config`，接受 JSON 配置文件路径，默认使用 `configs/google_constellation.json`。
- 如果用户指定了 `--config`，则从该 JSON 文件加载配置；否则使用默认配置。

### 5. 处理 presets.py
- 删除 `presets.py` 中的所有预设配置常量（BS32_WDM1 等）。
- 如果文件变为空，可以删除该文件，或在文件中只保留一个注释说明该文件已被弃用。
- 优先选择**删除文件**的方案（更干净）。

### 6. 创建 README.md
- 使用中文编写。
- 包含：项目简介、安装说明（numpy 依赖）、使用示例（sweep.py 和 link_model.py）、配置说明（三个配置类的字段说明）、项目结构说明。
- 不要引用未定义的文件路径。

## 完成后写入 Summary
将 summary 写入：/share/guolidong-nfs/SeeSpace/ISLSim/tasks/isl-config-refactor/impl/round-0-summary.md

Summary 必须包含以下部分：
1. 本轮实现内容
2. AC 推进情况（逐个 AC 说明：Implemented / Not Met / Partial，并列出证据）
3. 遗留问题
4. Goal Tracker 更新请求
5. Lesson Delta

## plan.md 全文

# ISLSim 配置层重构与项目规范化

## Goal Description

对 ISLSim 星间链路仿真项目进行配置层重构和规范化改造：
1. 将现有 `link_model.py` 中内嵌的 `FSOConfig` 参数配置提取为独立的 `config.py` 模块，并建立 `configs/` 目录结构，支持发射端硬件、接收端硬件和信道配置的三层分类管理；
2. 调整所有脚本间的引用路径，确保导入方式统一、清晰；
3. 清理代码中引用缺失外部文档的注释，保留必要的物理公式说明；
4. 添加完整的中文 `README.md` 文档；
5. 不在代码中引入任何预设配置常量，仅在 `configs/` 目录下提供一个 Google 星座通信场景的 JSON 配置文件示例。

## Acceptance Criteria

- AC-1: 配置层正确提取
  - `config.py` 中存在独立的 `TXConfig`（发射端硬件）、`RXConfig`（接收端硬件）和 `ChannelConfig`（信道配置）三个 dataclass，字段覆盖需求中列出的全部参数；
  - `configs/` 目录存在且包含一个 `google_constellation.json` 文件，该文件包含完整的 Google 星座通信参数配置，可被 `config.py` 的加载函数正确解析为上述三个配置对象；
  - 原有的 `FSOConfig` 被重构为组合上述三个子配置的新类或方式，现有 `compute_link` 等函数的接口需向后兼容或正确迁移；
  - Positive Tests：运行 `python -c "from config import TXConfig, RXConfig, ChannelConfig; print('OK')"` 无报错；
  - Positive Tests：`json.load(open('configs/google_constellation.json'))` 后能通过配置加载函数转换为有效配置对象；
  - Negative Tests：若 `configs/google_constellation.json` 缺失必填字段，加载函数应抛出 `ValueError` 或 `KeyError`。

- AC-2: 引用路径统一
  - 所有 `.py` 文件之间的相对/绝对导入方式统一，不存在 `sys.path.insert` 等运行时路径修改；
  - `sweep.py` 能正确引用重构后的配置模块；
  - `link_model.py` 能正确引用重构后的配置模块；
  - Positive Tests：在项目根目录执行 `python sweep.py --help` 正常输出帮助信息；
  - Positive Tests：在项目根目录执行 `python link_model.py` 正常输出计算结果；
  - Negative Tests：不存在任何 `ModuleNotFoundError` 或 `ImportError`。

- AC-3: 代码注释清理
  - 删除所有引用缺失外部文档（如 `parameter_audit.md`、`docs/loops/...` 等不存在文件）的注释；
  - 保留 Friis 公式、EDFA SNR 公式、M-QAM BER 公式等核心物理原理的必要注释；
  - Positive Tests：代码中不包含 `parameter_audit.md`、`docs/loops` 等字符串；
  - Negative Tests：核心物理公式（如 `_antenna_gain_db`、`_path_loss_db`、`_edfa_snr`）上方仍保留 docstring 或必要注释。

- AC-4: 中文 README 文档
  - 项目根目录存在 `README.md`，语言为中文；
  - README 包含项目简介、安装说明、使用示例（sweep 和 link_model 两种入口）、配置说明（三个配置类的字段说明）和项目结构说明；
  - Positive Tests：`README.md` 文件存在且前 20 行包含中文字符；
  - Negative Tests：`README.md` 不包含未定义的文件路径引用。

- AC-5: 不引入预设参数配置
  - `presets.py` 文件被删除或清空，不再包含任何预设常量（`BS32_WDM1`、`BS60_WDM1` 等）；
  - 不存在任何硬编码的预设配置字典；
  - 唯一提供的配置示例是 `configs/google_constellation.json`；
  - Positive Tests：项目中不存在 `DEVICE_PRESETS` 常量；
  - Positive Tests：`configs/google_constellation.json` 存在且为合法 JSON；
  - Negative Tests：`presets.py` 若保留，其内容应为空或仅含占位注释，不得含有任何 `FSOConfig(...)` 实例化。

- AC-6: 无回归
  - Positive Tests：现有文件和功能不被破坏，核心物理计算逻辑（Friis 公式、EDFA SNR、调制选择、带宽计算）保持原样；
  - Negative Tests：不引入语法错误或破坏性改动，所有 `.py` 文件能通过 `python -m py_compile` 检查。

## Implementation Notes
- 代码中禁止出现 AC-、Milestone、Step、Phase 等 plan 标记
- 配置层重构时保持向后兼容：`link_model.py` 的计算函数签名应尽量保持稳定
- `configs/google_constellation.json` 中的参数值需基于 Google Starlink/Project Kuiper 等星座通信的公开技术文献合理设定
- 导入方式统一使用相对导入（`from .config import ...`）或项目根目录的绝对导入，避免运行时 `sys.path` 修改

## Path Boundaries
- 可接受的实现范围：配置提取、路径调整、注释清理、README 编写、JSON 配置示例
- 不可接受的方向：修改核心物理公式、添加新的可视化功能、引入额外的依赖包
