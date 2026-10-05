# DEV24-B：两次 kill 后的最后一次 AppWorld broad discovery

日期：2026-10-04。用户授权顺序：transport 修复与纯 stub stress → index-2 独立 paired classical diagnostic → DEV24-B。没有新 OACR 方法或干预，原 DEV24 producer、轨迹、结果与分母不变；Support-Lifecycle 不复活，512-unit 评估库保持封存。

## 前置门槛

1. 新 transport 必须在 native 前原子 claim，并持久化 claimed/executed/responded UUID 状态及完成响应。重复 UUID 只能重发相同缓存，不能重新执行；同 UUID 改 payload、遗留 claimed 无结果或有冲突 response 均 fail closed。执行后发布或清理失败不授权重新执行。crash 后不能声称普遍 exactly-once；未能证明结果的 claimed 请求不补跑。
2. 纯 transport stub stress 必须覆盖重复 pending UUID、unlink 失败/无效、既有 response、延迟清理、duplicate delivery、publication failure。每个被接受的 UUID 的 stub callback 调用数恰为 1；AppWorld world、task/API、evaluator、model 调用均为 0。还需验证 host 文件操作不受 native global monkeypatch 改变。失败则不启动 native 诊断或 B。
3. 独立 index-2 diagnostic/control 必须在打开 fresh world 前冻结实现、私有合法代码 payload hashes、paired invariants、native评分和四分支处置。它不属于原 producer 重跑，也不产生新独立任务。只更改 CSV data-field quoting，合法 source set、记录顺序、destination、其它序列化条件与 mutation sequence 保持相同。独立 parser 与公开 read-back 对齐后才做删除；不读取 gold、私有 DB 或 evaluator report，评分仅在 endpoint 关闭后各一次。

## 机械选择（metadata-only）

使用未修改的作者 train manifest 和原 DEV24 recovery freeze。按原冻结的 24 个 family hashes 顺序，对每个 family 从 manifest 中选原选中 variant 之后的第一条未使用 variant。排除旧三项暴露实例及原 DEV24 所有 24 个冻结身份（包括启动失败或中断任务），不读取 prompt、难度、gold 或评分，不依据 index 2 选相似任务。

若某 family 无下一合法 variant，则保留该固定任务位与 family hash，记 `not_started_no_unused_variant`，不换 family、不回绕、不按结果补选。只有 metadata 确认全部 24 个 family 均有下一实例时，才形成 24 个 actor 的执行 freeze。现实 manifest 若不满足，此协议停止并报告容量，不能自行改变规则。

机械选择脚本和所有 implementation hashes、task/family hashes、manifest hash、顺序及预算在打开任何 B prompt 前提交 GitHub 预冻结。diagnostic 对原实例的重复暴露不改变 B variant 选择。没有任务替换、评分后重试或第二次 B batch。

## 原生 actor 与资源

作者源固定 `9f3e92155345a9159f3a8b25abc334eeca05b545`，AppWorld `0.1.4.dev0`；所有 12 个共享基库在启动前与 canonical 作者包哈希一致，作者 API、环境语义和 evaluator 不修改。共享资产损坏则保留固定位置的基础设施状态，不按结果重试。

每项独立 fresh world，cold subagent，作者公开 generator prompt 与固定初始 playbook；只看自己的公开 prompt/合法 receipts，ground truth disabled，禁止其他 actor 轨迹、源状态、评分反馈、外部模型或网络。并发隔离以每个 actor 的独立进程/world/mailbox为界。未运行完整 ACE 学习闭环或原始 DeepSeek backbone。

与原 DEV24 相同：40 次 execute（拒绝/解析错误计数）、每段 native 20 秒、actor 自首次 start 起 1200 秒、终止后 grader 120 秒且仅一次、environment seed 123、2000 Unicode chars 每页。所有 prompt 页交付后才执行；分页仅获取已有文本。重复 transport UUID 不产生新的 execute 预算消耗；重复 delivery、缓存发布与失败清理独立计成本。通信 timeout 不授权重发 mutating execute 或重启 world。

高成本筛查保持每项 API requester records ≥100、execute ≥20、生成 native receipt bytes ≥100000、actor 墙钟 ≥600 秒；筛查仅用于事后归因。API/execute、生成文本、发布文本、模型实际消费分别记账。模型使用非零；checkpoint、sampling、calls、tokens 与费用未知，不从 API 次数推断。

## 最终发现与停止规则

本轮不比较新算法。只判断是否存在同一机制 residual 在至少 3 个独立开发任务、至少 2 个 generator family 中复发，并且确实影响原生完成/正确性或注册成本。原任务在 paired diagnostic 中的两条控制臂不算新的独立任务；故障、中断、transport污染、未定因和普通实现错误不能凑复发。

| B 的结果 | 处置 |
| --- | --- |
| 没有达到 R1 的机制复发 | **停止 AppWorld core search 和 broad fishing。** 报告“在这两次固定开发横截面中，没有观测到足以诱导新核心的 recurrent residual”，不主张全域不存在。不得再开 DEV48/DEV72 来延续搜索。 |
| 出现达到 R1、具有 R2 证据的明确机制 | 先独立预注册最强可实现经典控制：index/cache、完整合法历史 replay、state machine、constraint checking、alternative enumeration 等，保持相同信息和完成保证，初始化/存储/查询/维护/补取及已知模型成本全部计入。 |
| 经典控制消除该机制或追平收益 | 归入经典适配/工程能力，候选退出；不救。 |
| R1、R2、R3 有确证 | 才允许提出明确 R4 算法对象与构造前 R5 falsifier；任何新的候选/baseline/口径未冻前，封存库不打开。 |

若执行因基础设施不足无法完成，保留所有固定位置和缺失成本，不将未执行部分解释为能力成功或失败。这也不授权开启第三轮 broad discovery。允许后续完成本次已冻结位置的尚未启动尝试、审计与定向经典控制；已执行/已评分任务不补跑。

## 公开与权限

公开仓库只保存通用执行代码、协议、hashes、计数、非敏感归因与范围化结果。原始 task identities、prompt、完整 actor code/receipts、凭证、DB/gold/评分报告留在本地私有目录。不得上传、读入 actor 上下文或用私有 truth 选择候选。结束时审查所有固定行、UUID at-most-once 记录、事件链、评分顺序与资源未知项后更新 PR #89。
