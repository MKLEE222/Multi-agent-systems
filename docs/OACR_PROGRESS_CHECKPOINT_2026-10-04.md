# OACR 研究进度记录（2026-10-04）

记录位置：[PR #89](https://github.com/MKLEE222/Multi-agent-systems/pull/89) 的 `work/ocar-takeover-20261001` 分支。本文是证据状态索引，不替代各实验协议、结果文件或最终验收 gate。原 10 月 4 日记录纳入 24 个冻结任务位、三项中断前缀处置及两项冷审；下文新增 10 月 5 日单代理工程与 paired diagnostic 结果，历史实验行和评分不覆盖。

## 当前判定

**独立核心增量仍未成立。** 当前版本的 operation-specific Support-Lifecycle 退出独有核心候选。研究保留已验证的有限契约、原生构造与载体内结果；这些结果各自按原协议和分母解释。完整升级的理论、识别与自然证据门槛仍开放，冻结的 512-unit 评估库继续封存。

| 研究项 | 当前状态 | 证据与边界 |
| --- | --- | --- |
| Support-Lifecycle 抽象 | **退出独有核心** | [kill test](OACR_SUPPORT_LIFECYCLE_KILL_TEST_2026-10-03.md) 的七条理论线和原生载体审查发现 ATMS、SBFE、LPCFS、规划、溯源、物化视图维护、运行时监测等直接近邻。此判定针对当前抽象主张；具体结构算法仍须逐项比较。 |
| 经典主动取证控制 | **实跑、归类为经典能力** | [精确结果](../experiments/oacr_support_kill/CLASSICAL_WITNESS_2026-10-03.json)：16 worlds、81 partial observations、24 fixed orders；固定顺序期望查询成本 `25/8`，最优自适应决策树 `21/8`，最坏情形均为 4。该四位自构见证不是官方任务收益。 |
| ACE/AppWorld 原生入口 | **执行路径可用** | [三项原生 train 变体](OACR_SUBAGENT_NATIVE_TASK_EXECUTION_2026-10-02.md) 在同一场景 family 上 3/3 成功，证明接口可执行；完整 ACE 学习闭环和跨 family 收益未验证。 |
| 多场景原生残差发现 | **24 个任务位已记录，无合格残差** | [DEV24 结果](OACR_RESIDUAL_DEV24_RESULTS_2026-10-04.md)：20 项原 producer 终态评分中 18 成功；另 3 项额度中断前缀、1 项基库启动失败单列。index 1 有确证接口干扰；[10 月 5 日独立控制](OACR_DEV24B_QUOTE_DIAGNOSTIC_RESULTS_2026-10-05.md)得到 quote-all 未通过、minimal quote 通过，index 2 归档为经典序列化/验收敏感性。控制臂不拼入原成功率。 |
| BFCL 与效应授权 | **经典适配/控制** | [BFCL 开发回放](OACR_REAL_BFCL_EXECUTION_2026-10-02.md) 的 54 个 unknown 已分解为信息边界和可补工程缺口；同场强经典维护没有留下独有调用收益。[效应授权报告](OACR_MOE_COLD_START_AND_EXECUTION_2026-10-02.md) 的 31 项构造检查通过，effect equality 条件归入经典检查。 |
| 既有 R4、SQEC、BRFP 证据 | **保留原范围** | 见[唯一升级验收 gate](OACR_FINAL_UPGRADE_ACCEPTANCE_GATE_2026-09-30.md)。已有精确或控制实验不承担这轮独有核心的新颖性证明。 |

## 本轮理论修正

1. **可执行修复需说明信息来源。** 若粗表示已合并行为不同的两个状态，单靠该粗表示和共同契约无法恢复其差别。加性修复必须列明仍可用的原始断言、日志、外部证据或合法重取机制，并计入保存和重取成本。
2. **分区正确与执行正确分别验收。** `U=E=0` 或 `ker(Enc)=ker(B_C)` 只说明类别对应；decoder 的原生回放及后续更新仍需独立检查。
3. **冻结与算法贡献分别验收。** 禁止读取评估结果是信息权限条件。即使规则预先冻结，若构造器利用合法输入完整模拟所有未来结果，仍须报告 native/oracle 调用与计算成本。
4. **任务准确率与表示商分开。** N1 当前的 future-query accuracy 不直接测量共同 state bank 的表示核、operational quotient 或 `U/E`。N1 保持分支结果身份。

上述要求已在[唯一升级验收 gate](OACR_FINAL_UPGRADE_ACCEPTANCE_GATE_2026-09-30.md)中列为额外 R1–R5 义务。进度按已通过的具体主张判断，不按工作量或完成百分比判断。

## 10 月 4 日开发批次状态

[Residual-discovery 协议](OACR_RESIDUAL_DISCOVERY_PROTOCOL_2026-10-04.md)冻结 24 个 train tasks、24 个不同 family 的开发样本，先观察原生剩余问题，再给出同输入、同完成约束的可实现强经典控制。新核心晋级须满足复现、原生相关性、经典控制下仍存、可归因算法对象与事前反证标准 R1–R5。

[原批结果](../experiments/oacr_residual_discovery/RESULT_2026-10-04.json)的 24 行完整保留：前 6 项在 world initialization 的 SQLite backup 阶段报 `DatabaseError`，其余 18 项因共同基础设施故障未启动。原批成功初始化、actor 调用、prompt 交付和 evaluator 调用均为 0；`task_success_score` 为 `null`。这次中止不产生 actor 能力分数，也不构成自然任务的科学 residual。

[基础设施恢复记录](OACR_RESIDUAL_DEV24_INFRA_RECOVERY_2026-10-04.md)显示：损坏的共享 Gmail DB 已用作者固定数据包的原始字节恢复，12 个共享 DB 的哈希与 canonical 包对齐；没有读取任务正文、gold 或评分标签。恢复臂在 `a862d4754072294cd6a8b4d9465a349a99a68a26` 独立预冻结，沿用相同 24 个 task/family hashes、顺序、producer 与预算；原批中止记录完整保留。

**恢复臂的 24 个任务位现已全部记录。** [范围化结果报告](OACR_RESIDUAL_DEV24_RESULTS_2026-10-04.md)与[完整归因账本](../experiments/oacr_residual_discovery/recovery/ATTRIBUTION_LEDGER_2026-10-04.json)区分：20 项原 producer 终态评分（18 成功、2 未成功），3 项额度中断保存前缀（1 成功、2 未成功），以及 1 项基库初始化失败未评分。固定分母仍为 24；23 次原生评分的 19 次观测成功包含一条中断前缀，不是 24 条完整 actor 轨迹的成功率。已知原生测试小计为 120/137。

索引 10–12 的 controller 在额度中断中消失；先于评分提交的[中断处置](OACR_RESIDUAL_DEV24_RUNTIME_INTERRUPTION_2026-10-04.md)仅对已保存前缀评分一次，没有重启 actor 或重放 native actions。原始 exporter 的三项异常与 `all_fixed_rows_audited: false` 保留；[限定审计](../experiments/oacr_residual_discovery/recovery/QUALIFIED_AUDIT_2026-10-04.json)检查单独处置记录，不将其伪装成原 producer 正常终态。索引 13 的共享 Amazon 基库字节再次损坏，成因未知；保留启动失败，恢复 canonical 字节后继续其余固定任务，不重试索引 13。

20 项终态均未触发预注册高成本阈值。已知成本小计为 165 次 execute、159 次原生执行、947 条 API requester records；中断项的完整墙钟和成本未知，模型使用非零但 checkpoint、tokens、调用与费用均未知。没有 OACR 干预、方法比较或封存评估库使用。

[接口冷审](OACR_DEV24_TRANSPORT_AUDIT_2026-10-04.md)确证索引 1 同一个 execute UUID 执行三次，76 条 API records 中 40 条来自额外重复执行；终止出错发生于 response publication。保留原评分与成本，该项不支持科学 R1/R3，精确请求保留原因未定。[任务冷审](OACR_DEV24_TASK_FAILURE_AUDIT_2026-10-04.md)对索引 2 未建立因果解释；序列化/验收差异仅是低置信假设，不能宣称 evaluator bug。窄经典诊断控制已说明、尚未执行。

因此只有一项原因未决的原生失败，没有同机制跨任务复发，也没有经典控制下存活证据。**R1、R3、R4 未达到，不准新核心晋级。** Support-Lifecycle 继续退出；这轮不产生独有算法结论，也不证明未来没有可成立的结构增量。

## 10 月 5 日：两次 kill 已执行，B 保持未启动

用户因异常用量暂停子代理，本轮只使用单主代理。新 transport 和桥接实现单独保存，没有修改旧 producer。[纯 stub stress](../experiments/oacr_residual_dev24b/TRANSPORT_STRESS_RESULT_2026-10-04.json) 26/26 通过，154 个 callback-admitted UUID 对应 154 次 callback；无 native task/API/evaluator/model 调用。4 项 controller audit 通过，覆盖重复执行、缓存篡改和发布后清理失败的实际成本。保证为 at-most-once，未知结果 fail closed；不是任意 crash 下的 exactly-once，新 bridge 的完整 cold-actor 集成尚未运行。

paired quote diagnostic 在 `8af3081f54a325a545b6abec099b6df04589f0eb` 预冻结并回读后执行。两条独立 fresh-world 臂只改变 quoting，解析和公开 read-back 的 72 行及来源/顺序/操作不变量通过；producer 成功位 A=0、B=1。按预注册 `01` 分支，index 2 退出独有核心候选，归入经典 acceptance/serialization sensitivity。quote-all 在独立 CSV parser 下有效；未读取 evaluator report，不声称 malformed CSV 或 evaluator bug。原实例失败记录保留，控制不增加独立开发任务数。

本次实际 diagnostic 成本为 20 次 native execute、176 条 API requester records、67,722 receipt bytes、2 次评分，parent 墙钟 10.199182 秒；固定 actor model calls 为 0。主代理工程/审查模型消耗非零且 tokens/费用未知，异常账单原因没有因此查明。执行后审计通过，原 A 的 9 个 native receipt hashes 与旧合法记录一致；12 个共享基库及原冻结来源哈希重验通过。启动前 `simple_note.db` 的再次损坏先备份再恢复 canonical 原始字节，成因未知，按环境问题记录。

详见[完整诊断报告](OACR_DEV24B_QUOTE_DIAGNOSTIC_RESULTS_2026-10-05.md)及[控制用量的 B 执行准备](OACR_DEV24B_BOUNDED_EXECUTION_PLAN_2026-10-05.md)。两项实验前置门槛已通过，**DEV24-B 尚未冻结、B prompt 未读、B world/actor 均为 0**；子代理暂停持续有效。没有新的 R1/R3 机制残差，Support-Lifecycle 不复活，独有核心仍未发现。

同日继续完成[模型预算 admission 与启动检查](OACR_DEV24B_MODEL_METER_READINESS_2026-10-05.md)：17/17 synthetic controller 测试通过，已有 4 项 controller audit 再验通过。每次模型 callback 前持久化额度预留，缺失 usage/timeout/未知 claim 阻断后续调用；B prepare/verify 在未读取任务 metadata 前要求已验证的模型身份、预算与真实 adapter 注册。实际 actor 入口仍未接通，数值预算未选择，tokens/费用不可见；没有新增真实模型或 native 调用。仅保存未就绪模板，B 继续未启动。

## 下一次可晋级的条件

- 原批与恢复臂的各 24 行已保留；后续不得覆盖原记录或按结果换任务。新 transport 的纯 stub gate 已通过，完整 B 运行仍需核验桥接 ledger 与真实成本。
- 窄诊断已独立预冻结并执行，index 2 不再作为经典控制存活候选。B 须先登记 actor 身份、可执行模型用量上限与计量，保持原 24 family 的 outcome-independent next variants；没有 R1 则停止 AppWorld broad core search。
- 若出现跨独立开发任务的同类原生剩余问题，先执行同合法信息、同原生评分、同完成约束的强经典控制；记录完整资源成本与模型成本中的未知项。
- 只有 R1–R5 都有证据，才构造新的核心候选。若强经典控制消除剩余问题，归档为适配或工程结论。
- 冻结的 512-unit 评估库保持封存，直到原[升级 gate](OACR_FINAL_UPGRADE_ACCEPTANCE_GATE_2026-09-30.md)的科学 estimand、实现、对手与最终构造通过审查。

## 证据权限

受保护原生轨迹加密包的 GitHub 外披曾被自动审批拒绝，原因是缺少明确外披授权；该包仅保留本地。本 PR 的公开材料限于代码、哈希、聚合计数及公开来源审查。此记录不重新上传受保护内容，也不把未公开轨迹当作可由外部读者直接复验的材料。
