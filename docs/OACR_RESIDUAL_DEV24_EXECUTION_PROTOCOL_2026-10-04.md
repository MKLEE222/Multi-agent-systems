# AppWorld train 24-task residual discovery：执行前注册

日期：2026-10-04。上位协议：
[Residual Discovery](OACR_RESIDUAL_DISCOVERY_PROTOCOL_2026-10-04.md)，
用户提交 `9276445530198098e986f72b822843a7bb3bec9f`。本轮不添加 OACR intervention，
不挽救 Support-Lifecycle，不在出现符合 R1–R5 的残差前构造新核心。

## 选择与信息边界

作者 AppWorld 子模块 source `9f3e92155345a9159f3a8b25abc334eeca05b545`、
原环境 `0.1.4.dev0`、原 evaluator。只读 train manifest 元信息；90 tasks，
30 generator families。排除旧 smoke 的三个已暴露 task hash 后，按 manifest
顺序取每个 family 的第一个剩余 task，选前 24 个不同 family。选择不使用
任务内容、难度、答案、执行结果或期望残差类型。24项 indices 为
`3,6,9,12,15,18,21,24,27,30,33,36,39,42,45,48,51,54,57,60,63,66,69,72`。
没有足够不同 family 时中止准备，不看结果换样。

任务 hashes、family hashes、manifest SHA、旧暴露排除 hashes、实现/
prompt/playbook/evaluator SHA 与日志 schema 保存于新的 freeze。公开资产只有
代码、hash、计数和不含任务正文的审计/归因。保护 prompts、原生代码回执、
任务映射与完整轨迹留本地，不尝试上传被拒绝的保护轨迹包。

test/test_normal 不按例读取，既有 512-unit bank 不读不解封。此批是 manifest
顺序下的开发筛查，不能当作随机总体泛化或测试集成绩。

## Actor 与操作预算

每 task 一个 `fork_turns: none` 的独立冷启动子代理，一个 fresh world。
使用同一预注册调用方式、作者渲染的公开 generator context 与 initial playbook；
仅见自己的合法 receipts。初始 prompt 和原生回执按 2,000 characters 分页；
actor 开始行动前须读完初始 prompt，回执余页可按需读取，分页不调用原生 API。
角色只执行任务，不参加研究归因、不获知其他任务
结果。禁止 host 源码/文件/数据库/outputs/gold 访问、联网找答案、另起模型和
继续委派；只允许通过 actor_client 调用原生 `apis`。

子代理模型继承当前后端，版本、sampling seed、token 与账单未暴露；不声明
同原 DeepSeek backbone、版本同质性或完整模型成本公平性。子代理模型使用
非零；记录 actor invocations，外部 provider API 调用另列。角色为 native
actor 变体，未执行完整 ACE reflector、curator 或跨 task playbook 更新。

每 task 至多 40 execute requests（parse error、拒绝和原生错误均计）；
原生每段代码 timeout 20s，环境 seed 123。actor start 后 wall 上限 1200s，
使用真实 monotonic/performance clock；等待 actor 接入不算其执行时间。
client 通信 timeout 与 actor deadline 独立。并行只用于运行独立 worlds。

actor 认定完成/不可继续、预算耗尽或 wall deadline 后终止。controller 关闭
actor endpoint 再调用未改 evaluator 一次；评分不返 actor，不按 score 修补、
重跑或替换任务。启动/基础设施/评分异常保留，全部 24 项保留分母。

## 预注册高成本筛选

以下任一条件将 task 标为需要离线成本归因：

- 原生 actor API calls **≥100**；
- execute requests **≥20**；
- 原生生成的 native receipt bytes **≥100,000**；
- actor wall time **≥600s**。

四项分别报告，不混成美元/时间代理。这只是筛选 threshold，不证明费用
不可避免，也不满足 R2 或 R3 的方法优势。所有失败必须归因，即使没有
触发阈值；所有成功仍记录完整计数，不删去“没有问题”的样本。

## 记账、离线归因和经典控制

日志对每个 execute request 都保存 hash 链及 metrics。请求计数、实际 native
interactions、API calls、拒绝、parse/transport/执行错误与 grading 调用分开。
分别保存完整初始 prompt/原生生成 receipt bytes、mailbox 已交付文本 bytes、
分页请求数；保存并不等于模型已读取，工具或模型实际可见文本量未暴露时记 unknown。
保存 actor/native 时间、终止原因和原生
success/test counts；模型 token/费用未知字段显式为 unknown，不记零。

在线 actors 全部终止后，才基于合法任务输入、原生 code/receipts、公开 API
语义与 aggregate score 做离线诊断；不使用参考解、gold API list 或私有 DB
来给维护器补证。归因记录 task/family hash、事件/步骤号、类别、证据、置信
程度、可行控制及其 tested/pending 状态。允许多个标签，不把 memory failure
作为终点；unresolved 是待核状态，不是 surviving residual。

类别按上位协议：reasoning/planning、implementation/semantic coverage、classical
maintenance、observation insufficiency、consumed/revoked permission/false guard、
binding/rebinding、cross-app effect coupling、evaluator/API/task inconsistency、
unresolved。API 约束引起的多次 read 与本可避免的重复 read 分开。

重复机制先给可实现的正确经典控制。新控制必须单独冻结合法信息、完成保证
与全部成本后执行，是开发诊断 arm，不改此批 actor 首跑成绩。未实际比较的
控制只记 pending；源码解释或反思建议不算 R3 已通过/已失败。

本批严格执行 R1 的 **≥3 independent tasks 且 ≥2 families**，不使用上位
协议的 formal-counterexample 豁免。此处每 family 一 task，观察到三项复发
会自然跨三 family。R1–R5 缺一项不准提出新核心。安全 abstain 不代替原生
任务完成，generic optimum 很贵不等于 heuristic 新颖。

当前状态：执行前注册；freeze/首跑 commit 和实际结果将分别记录，不回填
成预注册事实。
