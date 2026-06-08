# Round 0 Summary

## 1. 本轮实现内容

- 在项目根目录新增 `point_test.py`。
- 脚本使用 argparse 接收必需参数 `--distance-km` 和可选参数 `--config`。
- `--config` 默认值为 `configs/google_constellation.json`。
- 脚本通过 `load_config_from_json()` 加载配置，通过 `compute_link()` 执行单点链路计算。
- 标准输出仅打印一个浮点带宽数值：链路可行时输出 `LinkResult.total_bw_gbps`，不可行时输出 `0.0`。
- 未修改 `sweep.py`、`config.py`、`link_model.py` 或配置文件。

## 2. AC 推进情况

- AC-1: Implemented
  - 证据：项目根目录存在 `point_test.py`。
  - 证据：`python3 point_test.py --distance-km 1000 --config configs/google_constellation.json` 输出 `400.0`，退出码为 0。
  - 证据：`python3 point_test.py --distance-km 1000` 使用默认配置输出 `400.0`，退出码为 0。
  - 证据：`python3 point_test.py` 输出 usage，并因缺少 `--distance-km` 以退出码 2 失败。
  - 说明：本轮任务明确要求 `--config` 为可选参数，因此未将缺少 `--config` 作为错误处理。

- AC-2: Implemented
  - 证据：`python3 point_test.py --distance-km 1000 --config configs/google_constellation.json | wc -l` 输出 `1`。
  - 证据：`python3 point_test.py --distance-km 1000 --config configs/google_constellation.json | python3 -c "import sys; print(float(sys.stdin.read().strip()))"` 输出 `400.0`。
  - 证据：脚本 stdout 仅包含带宽数值，不输出 `Config:`、`Waveform:` 或其他说明文字。

- AC-3: Implemented
  - 证据：`point_test.py` 使用 `from config import load_config_from_json` 和 `from link_model import compute_link`。
  - 证据：`python3 point_test.py --distance-km 1000 --config configs/does_not_exist.json` 抛出 `FileNotFoundError`，退出码为 1。
  - 证据：配置加载异常未被吞掉，符合非零退出要求。

- AC-4: Implemented
  - 证据：本轮未修改 `sweep.py`。
  - 证据：`python3 sweep.py --help` 正常输出原有 argparse help，退出码为 0。
  - 证据：`sweep.py` 中没有新增导入或代码路径。

- AC-5: Implemented
  - 证据：`python3 -m py_compile point_test.py` 通过。
  - 证据：`python3 -m py_compile $(rg --files -g '*.py' -g '!tasks/**')` 通过。
  - 证据：`python3 link_model.py` 正常运行并输出距离-带宽表，退出码为 0。
  - 证据：未修改 `config.py`、`link_model.py`、`configs/google_constellation.json`。

## 3. 遗留问题

- 无。

## 4. Goal Tracker 更新请求

- 请求将 Round 0 标记为完成。
- AC-1 至 AC-5 均已按本轮任务约束实现并验证。

## 5. Lesson Delta

- 新增单点测试入口时，保持 stdout 仅输出机器可解析数值，避免复用会打印说明文字的 sweep 输出路径。
- 本轮任务中 `--config` 的要求以 Round 0 明确说明为准：可选并提供默认配置路径。
