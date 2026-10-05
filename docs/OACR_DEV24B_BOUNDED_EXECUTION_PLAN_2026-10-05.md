# DEV24-B：控制用量后的执行准备

状态：**未启动，未形成 B execution freeze**。用户暂停子代理的指令持续有效。本轮仅单主代理完成工程检查和固定 quote A/B，两个实验前置门槛已通过。没有运行额外 actor、打开 B prompt 或创建 B world。

后续同日推进：[模型计量就绪记录](OACR_DEV24B_MODEL_METER_READINESS_2026-10-05.md)。预算 admission 的 17 项纯 stub 检查与 4 项原 controller 审计通过，B prepare/verify 已加入强制注册检查。真实 actor adapter、usage、数值预算尚未连接；没有生成 B freeze，不能把 stub 成功写成实际模型计量已完成。

## 当前缺口

原 DEV24 recovery 的 actor 模型 checkpoint、sampling、calls、tokens 和费用未知；本对话的主代理模型消耗也未暴露。transport 防止 native 重复执行，不能阻止或计量模型的长时间推理。API records 与 tokens/费用不能互相替代。因此不能宣称异常用量已经修复，也不能把原 40 execute / 1200 秒的 native 预算当成模型费用上限。

B 的任务侧规则已有代码：保持原 24 family 顺序，选下一未使用 variant；metadata 检查显示每个 family 都有候选，没有按 index-2 内容选任务。selection prepare 尚未生成 B freeze。原经典 quote 控制的两臂不增加独立任务数。

## 启动前登记

| 项目 | 启动要求 | 目前状态 |
| --- | --- | --- |
| actor 身份 | 固定可复验模型 checkpoint、推理/采样配置、prompt/playbook 与信息权限；强度不能为节省成本而暗中降低 | 尚未登记 |
| 模型计量 | 每次调用保存实际 usage；区分 input/output、cached/reasoning tokens（若提供），保留缺失项；费用由真实计费信息取得 | 尚未接入 |
| 硬预算 | 事前固定单项和整批模型调用、tokens/费用或服务可执行的等价用量上限；达到上限直接终止，禁止自动续跑 | 尚未登记数值与可执行限制 |
| 隔离与并发 | 独立 cold actor context；同一时刻最多一个 actor；禁止自动派生子代理或递归委派 | 用户暂停子代理，当前 actor 数为 0 |
| 原生限制 | 每项 40 execute（含拒绝）、单段 20 秒、actor 1200 秒、评分 120 秒且一次、seed 123、页宽 2000 chars | 沿用原协议 |
| 运行前冻结 | 24 固定位置、manifest/hash、完整 implementation、身份/用量设置和停止规则在任何 B prompt 前提交并回读 | 尚未执行 |

新的可计量 actor 如与旧未知模型无法证明相同，必须明确作为第二个有身份的 development actor 配置报告；不把跨模型差异解释为算法收益。持有已有研究上下文的主代理不能伪装成 cold actor。

## 建议的串行执行形态

整批 24 个位置一次冻结。先串行运行固定顺序的前两个位置，只核查用量计量、硬上限执行、UUID ledger、初始化与清理是否可信；它们就是 B 的正式位置，不增加 pilot tasks、不重跑。开启剩余 22 项的门槛只依赖预注册资源与基础设施条件，不能依赖前两项的任务成功或残差内容。若资源门槛失败，保留 24 行及未启动位置，不换任务、不换模型后拼接为同批完整结果。

这只是执行方案，不授权在本轮恢复子代理或开启 B。继续推进时先补齐上述计量与身份条件，再依照用户的执行范围决定是否运行。现有 native 限制保留；额外模型硬上限若使轨迹中断，须单列中断前缀，不伪装成完整 actor 成功/失败。

## 科学停止规则

B 仍是最后一次 outcome-independent broad discovery。若未出现同一机制在至少 3 个独立任务、至少 2 个 family 中复发，停止 AppWorld core search，不开 DEV48/DEV72。若达到 R1/R2，先上同输入、同保证的正确强经典控制；R3 未成立，不构造新核心。Support-Lifecycle 不救，512-unit bank 保持封存。
