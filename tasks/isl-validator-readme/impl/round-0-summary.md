# Round 0 Summary — ISLSim 参数校验模块与 README 结构化梳理

## 任务
- 引入 `validator.py` 参数校验与错误处理模块
- 结构化梳理 `README.md`

## 变更文件
1. **新增** `validator.py` — 统一错误码枚举 + 配置参数范围校验 + 链路可行性预检
2. **修改** `sweep.py` — 入口增加 `validate_config` + `pre_check_link_feasibility` 调用
3. **修改** `point_test.py` — 入口增加校验调用
4. **修改** `link_model.py` — `__main__` 块增加校验调用；模块级 docstring 精简（函数级 docstring 保留）
5. **修改** `README.md` — 新增"物理模型"章节（含等速率异构说明），精简"项目布局"脚本描述为一行

## 未变更文件
- `config.py`（dataclass 定义未动）
- `configs/google_constellation.json`（配置示例未动）

## AC 状态
| AC | 描述 | 状态 |
|---|---|---|
| AC-1 | validator.py 模块结构与错误码 | **Verified** |
| AC-2 | 配置参数范围校验 | **Verified** |
| AC-3 | 链路可行性预检 | **Verified** |
| AC-4 | 入口脚本集成校验 | **Verified** |
| AC-5 | README.md 结构化梳理 | **Verified** |
| AC-6 | link_model.py 精简 | **Verified** |
| AC-7 | 无回归 | **Verified** |

## 测试结果
- `py_compile` 全部通过
- `sweep.py` / `point_test.py` / `link_model.py` 默认配置运行输出与重构前一致
- 非法配置（`tx_power_w = -1`）在校验阶段即被拒绝
- 极端不可行配置触发 `LINK_INFEASIBLE`

## 结论
Round 0 一次性通过，无需修复迭代。
