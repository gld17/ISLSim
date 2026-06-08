NO_ISSUES

## REVIEW Review - Round 0

### Diff 统计
- `link_model.py`: -229 lines, 移除内嵌 FSOConfig，导入 config.py，清理旧注释
- `presets.py`: 删除（-89 lines）
- `sweep.py`: -50 lines，移除 sys.path.insert 和 presets 依赖，改为 --config 参数
- 新增 `config.py`: 配置 dataclass 和 JSON 加载/导出
- 新增 `README.md`: 中文项目说明
- 新增 `configs/google_constellation.json`: Google 星座通信配置示例

### 审查结果

- [P0] 无：功能错误、安全风险、数据风险 — 未发现
- [P1] 无：逻辑缺陷、测试缺失、接口不一致 — 未发现
- [P2-P9] 无：代码风格、可读性、低优化项 — 未发现

### 备注
- 核心物理公式（Friis、EDFA SNR、M-QAM BER）未修改，仅迁移配置来源
- 配置层拆分后 `FSOConfig` 通过 `__getattr__`/`__setattr__` 保留扁平属性访问，向后兼容良好
- `geomspace` 标准库实现等价于 numpy.geomspace
- `__pycache__/` 目录出现在未跟踪文件中，建议在 Final Gate 时添加到 `.gitignore`
