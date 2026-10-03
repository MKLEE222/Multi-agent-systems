# 子代理原生任务执行结果

日期：2026-10-02。用户授权子代理执行任务。三位独立冷启动子代理已经在原生
AppWorld train 环境中自主完成任务，终止后由未修改的作者评分器检查：
**3/3 task success，6/6 原生测试通过，16 次代码执行、131 次 API 调用。**

这补齐了此前没有可用 actor 的执行缺口。三项来自同一 scenario 的三个变体，
结果证明执行路径可用；本轮没有 OCAR 干预或方法对照，不能解释为算法增益、
独立场景泛化、完整 ACE 复现或测试集 TGC/SGC。

## 实际执行与计数

| 固定 train 序号 | 代码执行 | 原生 API 调用 | 原生测试 | task success | 回执 bytes | actor 时间（秒） |
| --- | ---: | ---: | ---: | --- | ---: | ---: |
| 0 | 6 | 70 | 2/2 | 是 | 15,226 | 124.025 |
| 1 | 5 | 32 | 2/2 | 是 | 20,441 | 140.218 |
| 2 | 5 | 29 | 2/2 | 是 | 17,465 | 160.500 |
| 合计 | 16 | 131 | 6/6 | 3/3 | 53,132 | — |

原生执行错误 0，桥接拒绝 0。每 task 评分一次，共 3 次；评分后重试、修补或
换样本 0。三个 actor 的时间独立计量，不能相加作为并行 wall time。时间使用
`real_perf_counter`，避免原生环境冻结时钟导致错误计时。初始 prompt 合计
89,258 bytes；bytes 是数据量，不是 token 或价格。

外部 provider API 模型调用为 0，但子代理模型使用**非零**。其模型版本、抽样
seed、token 与账单没有暴露，因此没有完整模型成本数字，也没有与原论文
DeepSeek-V3.1 的同模型比较。

## 实验前冻结与权限

作者源码固定为 `ace-agent/ace-appworld@9f3e92155345a9159f3a8b25abc334eeca05b545`，
AppWorld `0.1.4.dev0`。按未修改 train manifest 的顺序选前 3 个 ID，train 共
90 项；相同 generator hash 确认三项为同一场景。未根据任务成败重新选样。

v1 提交 `bf66688541843d80b9032694b85d04bfa87fa8e9` 的本地 socket 在当前环境
遭 `PermissionError`，三个启动均止于 actor 行动前：native execute 0、评分 0、
actor 调用 0。失败记录和原 freeze 保留在 `startup_failure_v1.json`。

改为原子文件消息队列后，在 actor 行动前重新冻结 v2：
`faf4203d12578ebfd62169c9586907be11dc9033`。样本、环境 seed 123、每 actor
40 次 execute 请求上限及每段代码 20 秒 timeout 不变。
`freeze.json` 保存选择、manifest、prompt、playbook 与两份桥接实现 SHA256。
运行后没有修改冻结桥或 client。

三位 actor 使用 `fork_turns: none`，继承当前模型后端，各接入 fresh world。
输入是作者默认 generator template 的公开示范、initial playbook、公开任务、
supervisor 信息及自己取得的完整原生回执。环境 `load_ground_truth=False`；
不提供 required-API oracle、私有初始状态、参考动作、其他 actor 轨迹或评分。
actor 自主选择原生 Python/API 操作，并完成 `supervisor.complete_task`。

桥只开放 `start/execute/finish`。actor 指令禁止读取 host 文件、源码、数据库、
报告与 gold，禁止联网找答案、另起模型或继续委派。补充 AST 限制和原生 safety
guard 与轨迹保存一起提供可审计范围；共享文件系统上的指令遵守不是 OS 级
隔离或对抗式安全证明。

actor endpoint 终止后，controller 才调用原作者 `evaluate_task`。评分没有返回
actor，也没有用于选择重试。源码及评分器未改。未执行 ACE reflector、curator
或跨任务 playbook 学习；本轮名称为 **subagent-native train smoke v2**。
完整协议见 [冻结协议](OACR_SUBAGENT_NATIVE_TASK_PROTOCOL_2026-10-02.md)。

## 更正前轮权限判断

前轮从源码读字段及函数传参推断模型收到信息，判断过度。独立子代理现在对
12 个固定公开源码 blob、5 个作者 config，以及实际 template 渲染和模型输入
构造进行 synthetic sentinel 检查。该审计没有读取任务/gold 或调用模型。

- 默认 generator 只渲染 `app_descriptions/input_str/main_user/playbook`。
  源码读取的 `required_apis` 被传入未使用字段，**不进入默认模型 prompt**。
- 默认 no-GT reflector 没有动态 report、compiled solution 或 execution-error
  占位符。改变 report/solution sentinel 不改变其输入；改变可见 history 会改变
  reflector/curator 输入。with-GT template 是可见 report/solution 的阳性对照。
- no-GT 控制面仍执行 evaluator 并保存报告；这不等于模型得到报告内容。在所审
  `solve_task_wo_gt` 中未发现按该评分选择修补轮次的分支。此结论限于固定版本、
  原始五个配置及默认模板，不能推广到自定义 prompt 或其他版本。

因此撤回此前“默认 no-GT actor 得到 required-API gold 提示”和“默认 no-GT
reflector 得到动态逐任务评分反馈”的两项判断。旧冻结 preflight JSON 保留为
历史记录，其相关权限字段由本次实际渲染审计更正，不能继续当证据使用。

详见 [独立基线审查](OACR_MOE_COLD_BASELINES_2026-10-02.md)、
`experiments/oacr_moe/prompt_authority_audit/AUTHOR_PROMPT_AUTHORITY_AUDIT_2026-10-02.json`
与 `baseline_capsule/CORRECTED_RENDER_AUTHORITY_PREFLIGHT_2026-10-02.json`。
后者的源码/config/runner 检查通过；原完整 ACE provider 仍缺凭据，未执行模型。

## 轨迹与复核资产

`experiments/oacr_moe/subagent_actor/` 保存冻结实现、逐 task 摘要、聚合结果及
posthoc exporter。已检查全部事件链、终止事件、逐步调用计数、样本 hash 和
信息权限字段。完整 prompt、代码、回执、任务映射使用作者原生 `pack_bundle`
打包，保留为本地受保护资产；仓库发布代码、计数和 hash，不上传轨迹包或明文。

本地文件 `protected_traces.bundle.b64` 是原生加密 bundle 的 Base64 文本，
解码后 105,599 bytes，SHA256：
`1b771472153082345a6f9e41639ffa75b5a0abf14d35d8024e745ca244ae2044`。
15 个打包文件包含 v2 轨迹和 v1 启动失败资产。解包后三个事件文件 hash
均与摘要一致。解包说明见该目录 README；解包内容仍受原任务分发约束。
自动审批拒绝了该加密包的 GitHub 上传，理由是未获得受保护 benchmark 衍生
轨迹的明确外部披露授权；该包没有上传，后续仅保存不含任务正文的公开资产。

512-unit evaluation bank 未读取或解封；旧 producer、原分数与失败记录不改。

## 对研究方向的含义

这三项是 Spotify 信息检索、分页、统计与回答任务，没有测到支持失效、授权
迁移或表示更新的独立困难。强 actor 已全部成功，应保留这个结果，不能为了
OCAR 设计补救需求。后续共同任务比较应先保留这一 actor 的实际能力，再选择
能自然触发待研究原生操作的开发任务，比较同 actor 下完整强基线与候选算子，
计入构造、维护、补取及模型成本。当前没有新增独有算法或官方比较收益声明。
