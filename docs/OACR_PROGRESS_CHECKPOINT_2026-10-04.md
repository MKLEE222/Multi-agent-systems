# OACR 研究进度记录（2026-10-04）

记录位置：[PR #89](https://github.com/MKLEE222/Multi-agent-systems/pull/89) 的 `work/ocar-takeover-20261001` 分支。本文是证据状态索引，不替代各实验协议、结果文件或最终验收 gate。核对范围为截至本次读取时该 PR 的公开文件；本记录没有重新运行原生实验。

## 当前判定

**独立核心增量仍未成立。** 当前版本的 operation-specific Support-Lifecycle 退出独有核心候选。研究保留已验证的有限契约、原生构造与载体内结果；这些结果各自按原协议和分母解释。完整升级的理论、识别与自然证据门槛仍开放，冻结的 512-unit 评估库继续封存。

| 研究项 | 当前状态 | 证据与边界 |
| --- | --- | --- |
| Support-Lifecycle 抽象 | **退出独有核心** | [kill test](OACR_SUPPORT_LIFECYCLE_KILL_TEST_2026-10-03.md) 的七条理论线和原生载体审查发现 ATMS、SBFE、LPCFS、规划、溯源、物化视图维护、运行时监测等直接近邻。此判定针对当前抽象主张；具体结构算法仍须逐项比较。 |
| 经典主动取证控制 | **实跑、归类为经典能力** | [精确结果](../experiments/oacr_support_kill/CLASSICAL_WITNESS_2026-10-03.json)：16 worlds、81 partial observations、24 fixed orders；固定顺序期望查询成本 `25/8`，最优自适应决策树 `21/8`，最坏情形均为 4。该四位自构见证不是官方任务收益。 |
| ACE/AppWorld 原生入口 | **执行路径可用** | [三项原生 train 变体](OACR_SUBAGENT_NATIVE_TASK_EXECUTION_2026-10-02.md) 在同一场景 family 上 3/3 成功，证明接口可执行；完整 ACE 学习闭环和跨 family 收益未验证。 |
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

[基础设施恢复记录](OACR_RESIDUAL_DEV24_INFRA_RECOVERY_2026-10-04.md)显示：损坏的共享 Gmail DB 已用作者固定数据包的原始字节恢复，12 个共享 DB 的哈希与 canonical 包对齐；没有读取任务正文、gold 或评分标签。恢复臂需沿用相同 24 个 task/family hashes 与原顺序，使用独立 freeze、run ID 和结果目录；原批中止记录不得覆盖。**截至本记录核对的公开文件，恢复臂尚无 24 项 actor/评分结果。** [静态审查](OACR_RESIDUAL_DEV24_AUDIT_2026-10-04.md)通过启动代码门槛，仍待实际原生运行及失败归因。

## 下一次可晋级的条件

- 保留原批 24 行及独立恢复臂的完整 24 行；任何再次启动失败也单列，禁止按结果换任务。
- 若出现跨独立开发任务的同类原生剩余问题，先执行同合法信息、同原生评分、同完成约束的强经典控制；记录完整资源成本与模型成本中的未知项。
- 只有 R1–R5 都有证据，才构造新的核心候选。若强经典控制消除剩余问题，归档为适配或工程结论。
- 冻结的 512-unit 评估库保持封存，直到原[升级 gate](OACR_FINAL_UPGRADE_ACCEPTANCE_GATE_2026-09-30.md)的科学 estimand、实现、对手与最终构造通过审查。

## 证据权限

受保护原生轨迹加密包的 GitHub 外披曾被自动审批拒绝，原因是缺少明确外披授权；该包仅保留本地。本 PR 的公开材料限于代码、哈希、聚合计数及公开来源审查。此记录不重新上传受保护内容，也不把未公开轨迹当作可由外部读者直接复验的材料。
