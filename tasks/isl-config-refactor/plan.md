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
