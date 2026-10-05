# DEV24-B：Work 串行限额执行登记

用户在入口选择问题后说“你看着来”。本轮选择已有 Work actor，保持 tokens、model calls、snapshot、sampling 与费用未知，不新增付费 API。此前多路研究/审计子代理继续暂停；任务执行仅临时启用一个 `fork_turns=none` 的 cold actor，禁止递归委派，结束或到时立即停止，再启动下一个。本轮最多准入固定顺序位置 0、1 两个 actor。

这是对上一轮强制真实 token-meter 启动门槛的明确修订，**不声称真实 token gate 已通过**。token-budget 模块与 17 项原 stub 证据保留；B 采用单独公开的 Work proxy-limit schema，不能伪填 usage、预算或 provider 审计。

每项 300 秒 effective endpoint wall time、120 次 mailbox deliveries（含 prompt/receipt 分页及重复 delivery）、最多 40 execute、每段 native 20 秒、评分 120 秒且一次、seed 123、页宽 2000 chars。监督 actor 生命周期并在终止时关闭 actor。300 秒是额外资源截断，与旧 DEV24 1200 秒预算不同；不能直接拼成同预算成功率。时间超过 600 秒的原高成本 screen 在本配置被截断，不报告“没有高成本”作为发现。

冻结原 24 family 的下一未使用 variant，完整 24 位分母不变，在任何 B prompt 前提交并远端回读。前两项为正式 B 位置，不是额外 pilot tasks；不根据 index-2 内容挑任务。其余 22 项本阶段不准入、不换任务、不补跑前两项；后续仅依据资源与基础设施审核安排新的有限执行阶段，不依据前两项评分选择是否继续或选择任务。

资源上限导致停止时保存原生前缀并评分一次，明确标记 `resource_limited_prefix`；不能解释为完成 actor 的失败或科学 R1 复发。初始化/transport 故障不构成 residual。完整终态结果的归因仍遵循 native residual → correct classical kill → algorithm only if R1/R2/R3。Support-Lifecycle 继续退出，512-unit bank 封存。B 仍是最后一次 broad discovery，无 R1 则结束 AppWorld broad core search；不增加 DEV48/DEV72。

Work 工具未提供真实 tokens/费用；300 秒与 mailbox 请求上限不等于模型费用上限。模型消耗异常的历史原因仍未知，主控自己的对话消耗也不纳入 actor proxy counts。本配置只缩小单次自动执行的暴露范围。
