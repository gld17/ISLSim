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
