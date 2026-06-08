# Round 0 Summary

## 1. 本轮实现内容

- 新增 `config.py`，定义 `TXConfig`、`RXConfig`、`ChannelConfig` 和组合型 `FSOConfig`，并提供 `load_config_from_json(filepath)` 与 `config_to_dict(config)`。
- 新增 `configs/google_constellation.json`，使用嵌套的 `tx`、`rx`、`channel` 结构表达 Google 星座通信场景参数。
- 修改 `link_model.py`：移除内嵌 `FSOConfig`，改为从 `config.py` 导入；清理缺失外部文档引用；保留 Friis、EDFA SNR、M-QAM BER 等核心公式注释；入口改为加载默认 JSON 配置。
- 修改 `sweep.py`：移除 `sys.path.insert` 和旧 `presets.py` 依赖；将 `--preset` 改为 `--config`；默认读取 `configs/google_constellation.json`。
- 删除 `presets.py`，不再保留任何预设常量或预设注册表。
- 新增中文 `README.md`，覆盖项目简介、安装说明、使用示例、配置字段说明和项目结构。
- 为避免当前环境缺少 numpy 导致入口脚本失败，新增标准库 `geomspace` 实现，保持距离扫描行为等价且不改变核心链路公式。

## 2. AC 推进情况

- AC-1: Implemented
  - 证据：`config.py` 包含 `TXConfig`、`RXConfig`、`ChannelConfig` 和组合型 `FSOConfig`。
  - 证据：`configs/google_constellation.json` 存在且可由 `load_config_from_json` 加载为三个配置对象。
  - 证据：执行 `python3 -c "from config import TXConfig, RXConfig, ChannelConfig; print('OK')"` 输出 `OK`。
  - 证据：删除 JSON 中 `tx_power_w` 后加载会抛出 `ValueError missing required field(s) in 'tx': tx_power_w`。

- AC-2: Implemented
  - 证据：`sweep.py` 和 `link_model.py` 使用项目根目录绝对导入，不再包含 `sys.path.insert`。
  - 证据：执行 `python3 sweep.py --help` 正常输出帮助信息。
  - 证据：执行 `python3 link_model.py` 正常输出链路计算表格。
  - 证据：运行入口未出现 `ModuleNotFoundError` 或 `ImportError`。

- AC-3: Implemented
  - 证据：运行 `rg` 未找到 `parameter_audit.md`、`docs/loops` 等缺失文档引用残留。
  - 证据：`_antenna_gain_db`、`_path_loss_db`、`_edfa_snr` 和 `ber_mqam` 仍保留公式说明 docstring。

- AC-4: Implemented
  - 证据：项目根目录已新增 `README.md`。
  - 证据：README 前 20 行包含中文字符。
  - 证据：README 覆盖项目简介、安装说明、`sweep.py` 与 `link_model.py` 使用示例、三个配置类字段说明和项目结构。

- AC-5: Implemented
  - 证据：`presets.py` 已删除。
  - 证据：运行 `rg` 未找到 `DEVICE_PRESETS`、`BS32`、`BS60` 等旧预设常量残留。
  - 证据：`configs/google_constellation.json` 是唯一配置示例，且 `python3 -c "import json; json.load(open('configs/google_constellation.json')); print('JSON OK')"` 输出 `JSON OK`。

- AC-6: Implemented
  - 证据：核心物理计算函数未改变公式逻辑，仅迁移配置来源。
  - 证据：执行 `find . -name '*.py' -not -path './tasks/*' -print0 | xargs -0 python3 -m py_compile` 通过。
  - 证据：执行 `python3 sweep.py --distance-points 3 --output /tmp/isl_sweep_check.csv` 成功生成 3 行扫描结果。

## 3. 遗留问题

- 当前环境没有 `python` 命令，验证时使用的是 `python3`。
- 当前环境未安装 numpy；入口脚本已改为不强制依赖 numpy，README 中说明 numpy 仅作为扩展脚本的可选安装项。

## 4. Goal Tracker 更新请求

- 请将本轮目标状态更新为 Round 0 implemented。
- 请记录配置层拆分、JSON 配置入口、旧 presets 删除、中文 README 和基础验证均已完成。

## 5. Lesson Delta

- 扁平脚本项目中不要使用包路径假设和运行时 `sys.path.insert`，项目根目录绝对导入更适合当前结构。
- 命令行入口的 `--help` 不应被非必要第三方依赖阻断；轻量采样逻辑可用标准库实现，减少运行环境摩擦。
- 配置迁移时保留 `FSOConfig` 扁平属性访问，可以降低对核心物理计算函数的影响范围。
