# 模型用量：预算代码可测，真实 actor 入口尚未接通

本轮按用户同意继续落实用量检查，保持单主代理、子代理暂停、DEV24-B 未启动。已有 `actor_client.py` 仅处理文件 mailbox；当前 collaboration 工具不返回模型 usage 或 checkpoint，旧 native summary 的 model calls/tokens/cost 均为未知。未从环境中探查凭证，也未创建 API key、联系模型 provider、发送任务内容或推断账单。

## 实现与验证

[model_budget.py](../experiments/oacr_residual_dev24b/model_budget.py)为未来可计量 actor adapter 提供 controller-side admission：

- 单任务和整批分别限制调用数与 total tokens，每次调用先预留经过验证的完整 input bound 加最大 output cap，然后才允许一次 callback。
- 实际 input/output usage 返回后结账并释放未使用额度；重复上下文的全部 input tokens 每次重新计入。cached/reasoning 是各自 parent token count 的细分，不二次相加；缺少细分保留 `null`。
- 首次调用之前持久化 claim；同一 call ID 禁止重放。timeout、缺少 usage、身份不符、超过 bound 或 crash 后的遗留 claim 均 fail closed，保留已占额度并阻断后续调用。
- 同一 ledger 的 callback 串行；改变配置不能重置该 ledger。仅保存模型元数据/用量，不保存 prompt 或输出正文，不虚构美元成本。

`selection_prepare.py` 的 prepare 和 verify 都在任何 task metadata/manifest/world 操作之前检查真实 `MODEL_BUDGET_REGISTRATION.json`。模型身份、数值预算和实际 adapter 的 usage/input-bound/output-cap 审计未注册，禁止生成 B freeze 或启动 native bridge。未来 freeze 固定注册文件和预算模块哈希，模型字段来自注册的 snapshot。

只提供[未就绪模板](../experiments/oacr_residual_dev24b/MODEL_BUDGET_REGISTRATION.template.json)，未创建可运行注册。模板不能通过启动检查。注册字段属于受信 controller 的研究记录，不能把自填 hashes 当成 provider attestation。

[预算 stub 结果](../experiments/oacr_residual_dev24b/MODEL_BUDGET_STUB_RESULT_2026-10-05.json)记录 **17/17 通过**：边界外请求零 callback、单项/整批限制、完整重复 input 计费、细分不重复计数、timeout/usage 丢失、稳定 ID 重放、真正子进程退出后 claim 不补跑、配置变化拒绝、8 个并发调用最多 1 个在执行且整批只准入 3 个，以及 B prepare/verify 在未读 metadata 前停止。已有 4 项 controller audit 再验通过。所有 fixture 为 synthetic；provider/model/native task/API/evaluator 调用均为 0。这是工程门槛，不是算法收益或科学 residual。

## 不能由 stub 证明的部分

预算的真实 token 上限**依赖可信且实际接通的 adapter**：调用前验证完整输入的上界，provider 必须执行包含不可见 reasoning 的 output cap，SDK 自动重试关闭，返回实际 usage。此模块不取消远端已开始的推理，不约束绕过它的其他客户端，不把本对话的主代理模型消耗包括进 ledger。单独写一个计数器不能证明真实模型已受控。

OpenAI 的公开 token-counting 文档说明，usage 的输出计数包含不可见生成 token，`max_output_tokens` 覆盖它们，并提供 input-token counting 接口：[官方文档](https://developers.openai.com/api/docs/guides/token-counting)。这说明一种可接通的技术路径，不证明当前账户可用、不指定模型、不授权换 provider 或产生费用；本轮未实现或调用 API-backed actor。

## 后续所需配置

下一步需要明确 actor 调用入口及模型用量上限。若继续当前 Work collaboration 入口，现有工具只能限制并发、native 次数与墙钟，无法验证这里要求的实际 token ledger；不能悄悄把科学协议中的真实用量 gate 降为时间估计。若使用返回 usage 的独立入口，需要另行固定模型 snapshot、推理设置、真实 adapter、输入计数、输出限制、零重试、usage probe 和数值预算，再验证其完整 native 调用路径。与旧未知模型的差异须单列，不能解释为 OACR 收益。

目前 **B freeze 不存在，真实模型注册不存在，B prompts/worlds/actors 均为 0**。quote A/B 原预冻结 runner、文档、结果与原 DEV24 数据不改；Support-Lifecycle 继续退出，512-unit bank 保持封存。异常模型用量的历史原因仍未知。
