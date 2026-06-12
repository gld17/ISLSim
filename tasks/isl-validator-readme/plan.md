# ISLSim 引入参数校验模块与 README 结构化梳理

## Goal Description

对 ISLSim 星间链路仿真项目进行两项迭代：

1. **引入 `validator.py` 参数校验与错误处理模块**：在执行仿真流程之前，先对仿真配置 `config` 进行校验。覆盖统一错误码、配置参数范围校验、链路可行性预检三个维度。校验模块需被 `sweep.py` 和 `point_test.py` 在入口显式调用，确保非法配置在仿真开始前即被拒绝。

2. **结构化梳理 `README.md`**：将 `link_model.py` 中冗长的物理模型说明（等速率异构问题、建模流程 d->Pr->SNR->M->BW）迁移到 README 的独立章节；精简各脚本的文件说明，只保留用途描述，不再展开内部仿真逻辑；README 整体保持中文或中英双语，结构清晰。

## Acceptance Criteria

- AC-1: validator.py 模块结构与错误码
  - 项目根目录存在 `validator.py`，包含一个统一错误码枚举（或常量字典），覆盖至少以下类别：`INVALID_VALUE`（非法数值）、`OUT_OF_RANGE`（越界）、`MISSING_FIELD`（缺失字段）、`LINK_INFEASIBLE`（链路不可行）、`UNKNOWN`（未知错误）；
  - 错误码定义可被外部调用方通过 `from validator import ValidationError, ErrorCode` 等方式导入；
  - Positive Tests：`python -c "from validator import ValidationError, ErrorCode; print(ErrorCode.INVALID_VALUE)"` 无报错；
  - Negative Tests：不存在未定义的错误码被引用。

- AC-2: 配置参数范围校验
  - `validator.py` 提供 `validate_config(config: FSOConfig)` 函数，对以下参数执行范围/合法性检查：
    - `tx_power_w > 0`
    - `tx_aperture_m > 0`
    - `wavelength_m > 0` 且在合理光通信波段（如 0.4e-6 ~ 10e-6 m）
    - `baud_rate_ghz > 0`
    - `wdm_channels >= 1`（整数）
    - `fec_overhead` 在 `[0, 1)` 区间
    - `modulation_pool` 非空，每项为 `[order, label]`，其中 `order` 为 2 的幂次且 `>= 4`
    - `rx_aperture_m > 0`
    - `preamp_gain_db >= 0`
    - `preamp_nf_db >= 1`（噪声系数物理下限）
    - `ber_threshold` 在 `(0, 1)` 区间
    - `terminal_cap_gbps` 为 `None` 或 `> 0`
    - `link_margin_db >= 0`
    - `optical_efficiency` 在 `(0, 1]` 区间
  - 任何校验失败均抛出 `ValidationError`，携带错误码和 human-readable 消息；
  - Positive Tests：`validate_config(load_config_from_json("configs/google_constellation.json"))` 通过且不抛异常；
  - Negative Tests：构造越界参数（如 `tx_power_w = -1`）时，`validate_config` 抛出 `ValidationError` 且错误码为 `INVALID_VALUE` 或 `OUT_OF_RANGE`。

- AC-3: 链路可行性预检
  - `validator.py` 提供 `pre_check_link_feasibility(config: FSOConfig)` 函数，在典型距离（如 100 km 和 5000 km）下分别调用 `compute_link`，检查是否至少有一种调制格式在短距离下 `feasible=True`；
  - 若短距离下仍不可行（说明配置本身物理上不可能建立任何链路），抛出 `ValidationError(ErrorCode.LINK_INFEASIBLE)`；
  - 若仅长距离不可行但短距离可行，视为通过（属于正常衰减行为）；
  - Positive Tests：使用 `google_constellation.json` 预检通过；
  - Negative Tests：构造极端不可行配置（如 `tx_power_w = 1e-12`， aperture 极小），预检抛出 `LINK_INFEASIBLE`。

- AC-4: 入口脚本集成校验
  - `sweep.py` 在 `load_config_from_json` 之后、`sweep_distances` 之前，显式调用 `validate_config` 和 `pre_check_link_feasibility`；
  - `point_test.py` 在 `load_config_from_json` 之后、`compute_link` 之前，显式调用 `validate_config` 和 `pre_check_link_feasibility`；
  - `link_model.py` 的 `__main__` 快速运行入口同样增加校验调用；
  - Positive Tests：`python sweep.py` 使用默认配置正常输出结果；
  - Negative Tests：修改 `google_constellation.json` 使 `tx_power_w = -5`，运行 `python sweep.py` 时在校验阶段即报错退出，不进入物理计算。

- AC-5: README.md 结构化梳理
  - README 新增"物理模型"独立章节，包含：
    - 波特率与调制阶数的"等速率异构"问题说明；
    - 物理建模流程 `d(t) -> Pr(t) -> SNR(t) -> max M(t) -> BW(t)`；
    - 核心公式简要说明（Friis 自由空间损耗、EDFA 预放大器 SNR、M-QAM BER 近似）。
  - 以上内容的详细程度与当前 `link_model.py` 开头的 docstring 等价或更精炼；
  - "项目布局"章节中，各脚本说明精简为单行用途描述（如 `link_model.py` 仅写"核心链路预算物理计算"，不再展开内部公式）；
  - README 整体为中英双语或中文为主；
  - Positive Tests：`README.md` 存在且包含"物理模型"、"等速率异构"字样；
  - Negative Tests：`README.md` 中各脚本说明不超过两行。

- AC-6: link_model.py 精简
  - `link_model.py` 开头过长的中文 docstring（等速率异构问题说明、建模流程说明）被移除或大幅精简，仅保留模块用途（如 `"Core FSO link-budget physics."`）；
  - 各物理函数的 docstring 保留（Friis 公式、EDFA SNR、M-QAM BER 等），不删除；
  - Positive Tests：`link_model.py` 仍能通过 `python -m py_compile`；
  - Negative Tests：`link_model.py` 开头 30 行内不再包含"等速率异构"大段说明。

- AC-7: 无回归
  - 所有现有 `.py` 文件通过 `python -m py_compile`；
  - `python link_model.py`、`python sweep.py`、`python point_test.py --distance-km 1000` 使用默认配置输出结果与重构前一致；
  - 不修改核心物理公式、不修改 `config.py` 的 dataclass 定义、不修改 JSON 配置内容。

## Implementation Notes
- 代码中禁止出现 AC-、Milestone、Step、Phase 等 plan 标记
- `validator.py` 的错误码设计应便于未来扩展，建议用 `Enum` 或 `dataclass` 封装
- 校验失败时打印清晰的错误消息到 stderr 并返回非零退出码
- README 中物理模型章节的内容可直接从当前 `link_model.py` 的 docstring 迁移，不必重新撰写
- 保持 `link_model.py` 中各函数的核心 docstring（含参考文献），只移除模块级的大段中文说明

## Path Boundaries
- 可接受的实现范围：新增 `validator.py`、修改 `sweep.py`/`point_test.py`/`link_model.py` 的入口调用、重构 `README.md`、精简 `link_model.py` 模块级注释
- 不可接受的方向：修改核心物理公式、修改 `config.py` dataclass 定义、修改 `configs/google_constellation.json` 内容、引入新的依赖包
