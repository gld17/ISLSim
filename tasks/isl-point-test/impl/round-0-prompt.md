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
- **sweep.py 必须保持原样，不得修改任何内容。**

## 项目当前结构

```
/share/guolidong-nfs/SeeSpace/ISLSim/
├── config.py              # 配置 dataclass：TXConfig, RXConfig, ChannelConfig, FSOConfig, load_config_from_json(), config_to_dict()
├── link_model.py          # 核心物理计算：compute_link(config, distance_km) -> LinkResult, sweep_distances(), geomspace(), print_table(), save_csv()
├── sweep.py               # 距离扫描入口（必须保持原样）
├── configs/
│   └── google_constellation.json
├── README.md
└── tasks/                 # PBR 任务目录（不要修改）
```

## 本轮需完成的工作

根据 plan.md 的 AC-1 到 AC-5，完成以下工作：

### 新增 point_test.py

在项目根目录（`/share/guolidong-nfs/SeeSpace/ISLSim/`）新增 `point_test.py`，要求如下：

1. **命令行参数**：
   - `--distance-km`（必需）：指定星间距离，单位 km，类型 float
   - `--config`（可选）：JSON 配置文件路径，默认值为 `configs/google_constellation.json`

2. **功能逻辑**：
   - 使用 `config.py` 的 `load_config_from_json()` 加载 JSON 配置文件
   - 调用 `link_model.py` 的 `compute_link(config, distance_km)` 计算链路结果
   - 从 `LinkResult` 对象中提取 `total_bw_gbps` 字段
   - 如果 `feasible=False`，输出 `0.0`
   - 如果 `feasible=True`，输出 `total_bw_gbps` 的浮点数值

3. **输出格式**：
   - **标准输出仅包含一个带宽数值**，无表头、无说明文字、无装饰
   - 数值应能被 `float()` 直接解析
   - 不要输出 "Config:"、"Waveform:" 等描述性文字
   - 建议格式：`print(f"{result.total_bw_gbps:.2f}")` 或 `print(result.total_bw_gbps)`

4. **导入方式**：
   - 使用项目根目录绝对导入：
     ```python
     from config import load_config_from_json
     from link_model import compute_link
     ```
   - 不要使用 `sys.path.insert`

5. **错误处理**：
   - 缺少 `--distance-km` 参数时，argparse 应自动报错并输出 usage
   - 配置文件不存在或格式错误时，应抛出异常并以非零退出码退出

### 验证要求

完成代码后，执行以下验证：
1. `python3 point_test.py --distance-km 1000 --config configs/google_constellation.json` — 应输出一个数值（如 `400.0`）
2. `python3 point_test.py --distance-km 1000 --config configs/google_constellation.json | wc -l` — 应输出 `1`
3. `python3 point_test.py --distance-km 1000 --config configs/google_constellation.json | python3 -c "import sys; print(float(sys.stdin.read().strip()))"` — 应成功解析为 float
4. `python3 point_test.py` — 缺少 `--distance-km`，应以非零退出码报错
5. `python3 sweep.py --help` — 输出应与之前完全一致（sweep.py 未被修改）
6. `python3 -m py_compile point_test.py` — 语法检查通过
7. 所有 `.py` 文件通过 `python3 -m py_compile` 检查

## 完成后写入 Summary
将 summary 写入：/share/guolidong-nfs/SeeSpace/ISLSim/tasks/isl-point-test/impl/round-0-summary.md

Summary 必须包含以下部分：
1. 本轮实现内容
2. AC 推进情况（逐个 AC 说明：Implemented / Not Met / Partial，并列出证据）
3. 遗留问题
4. Goal Tracker 更新请求
5. Lesson Delta

## plan.md 全文

# ISLSim 新增单点测试脚本

## Goal Description

在 ISLSim 项目中新增一个单点测试脚本 `point_test.py`，功能如下：
1. 接受两个命令行参数：距离（km）和配置文件路径（JSON）；
2. 从 JSON 配置文件加载 FSO 配置；
3. 调用 `link_model.py` 的 `compute_link` 函数计算指定距离下的链路结果；
4. 仅输出该距离下的带宽数值（total_bw_gbps），格式简洁，便于脚本化调用和管道处理；
5. 保持 `sweep.py` 脚本不变。

## Acceptance Criteria

- AC-1: 脚本存在且可运行
  - 项目根目录存在 `point_test.py`；
  - 脚本可通过命令行接收 `--distance-km` 和 `--config` 参数；
  - Positive Tests：`python point_test.py --distance-km 1000 --config configs/google_constellation.json` 输出一个数值（如 `400.0`）；
  - Negative Tests：缺少 `--distance-km` 或 `--config` 参数时，脚本以非零退出码报错并输出 usage。

- AC-2: 输出格式简洁
  - 脚本标准输出仅包含带宽数值（`total_bw_gbps`），无额外表头、说明文字或装饰；
  - 数值格式为浮点数，保留适当精度；
  - Positive Tests：`python point_test.py --distance-km 1000 --config configs/google_constellation.json | wc -l` 输出 `1`；
  - Positive Tests：输出内容可被 `float()` 直接解析；
  - Negative Tests：输出中不包含 "Config:"、"Waveform:" 等描述性文字。

- AC-3: 配置加载正确
  - 脚本使用 `config.py` 的 `load_config_from_json()` 加载配置；
  - 能正确解析 JSON 配置文件并传递给 `compute_link()`；
  - Positive Tests：使用不同的 JSON 配置文件（如自定义测试配置）能得到不同的带宽结果；
  - Negative Tests：配置文件不存在或格式错误时，脚本抛出异常并以非零退出码退出。

- AC-4: sweep.py 不受影响
  - `sweep.py` 文件内容保持不变；
  - Positive Tests：`python sweep.py --help` 输出与之前完全一致；
  - Negative Tests：`sweep.py` 中无新增导入或修改。

- AC-5: 无回归
  - Positive Tests：现有文件（`config.py`、`link_model.py`、`configs/google_constellation.json`）不被破坏；
  - Positive Tests：`python link_model.py` 仍能正常运行；
  - Negative Tests：不引入语法错误，所有 `.py` 文件通过 `python -m py_compile` 检查。

## Implementation Notes
- 代码中禁止出现 AC-、Milestone、Step、Phase 等 plan 标记
- 输出到 stdout 的带宽数值应直接来自 `LinkResult.total_bw_gbps`
- 如果链路不可行（feasible=False），输出 `0.0`
- 脚本应使用 `argparse` 处理命令行参数
- 导入方式与现有脚本保持一致（项目根目录绝对导入）

## Path Boundaries
- 可接受的实现范围：新增 `point_test.py` 脚本，不修改其他文件
- 不可接受的方向：修改 `sweep.py`、修改核心物理公式、修改配置文件格式
