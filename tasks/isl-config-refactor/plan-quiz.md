# Plan Quiz

请回答以下两个问题：

## Q1

重构后的配置层中，以下哪个类**不属于**配置模块的分类？

A. TXConfig（发射端硬件配置）
B. RXConfig（接收端硬件配置）
C. ChannelConfig（信道配置）
D. LinkConfig（链路整体配置）

## Q2

本项目重构后，预设参数应该如何提供？

A. 在 `link_model.py` 中硬编码多个预设
B. 在 `presets.py` 中定义 `BS32_WDM1` 等常量
C. 仅在 `configs/` 目录下通过 JSON 文件提供，代码中不引入任何预设常量
D. 在 `config.py` 中定义 `DEVICE_PRESETS` 字典
