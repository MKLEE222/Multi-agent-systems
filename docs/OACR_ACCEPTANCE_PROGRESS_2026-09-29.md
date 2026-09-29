# OACR 当前验收进度 — 2026-09-29

**快照时间：2026-09-29 18:19（Asia/Shanghai）。** 本记录核对了 GitHub 当前提交、Actions 作业状态、作业日志和产物元数据；运行中的作业以本快照为准。前轮 R3/G5/L1 的验收见 [2026-09-28 记录](OACR_ACCEPTANCE_PROGRESS_2026-09-28.md)。

## 一、已核对的当前状态

| 线 | GitHub 证据 | 当前验收决定 |
| --- | --- | --- |
| L2b fold0 targeted native replay | [Clean run 36540298285](https://github.com/MKLEE222/Multi-agent-systems/actions/runs/36540298285) 的 replay 作业成功，产物 `oacr-l2b-fold0-targeted-replay`（ID 11021905711）已上传；日志返回 `PASS_POSITIVE_REPLAY` | **单个 learned positive witness 的 targeted replay 通过**。两次 fresh reconstruction 一致，H0 task equality 成立，注册 H1 actions `51/29/73` 均分离。结论限于 fold0 及该冻结契约。 |
| WACT-R 原始 prospective run | [Run 36526302297](https://github.com/MKLEE222/Multi-agent-systems/actions/runs/36526302297) 中 profession、software、musical instrument、sport、academic discipline 五个 INCLUDED 作业成功并有产物；programming language 完成且属于结构性排除；food、disease 仍在运行 | 已完成五个 INCLUDED roots 的原 verifier 结果为 **80/80 prospective witnesses PASS**；超过[预注册主门槛](OACR_WACT_R_WRITE_ACTIVATION_FLIP_PROTOCOL_V1.md)所需的 3 roots、32 witnesses。八个 frozen roots 的最终汇总仍待全部结束。 |
| WACT-R strict verification-only recheck | [Run 36552116448](https://github.com/MKLEE222/Multi-agent-systems/actions/runs/36552116448) 下载原 run 的 frozen artifacts；profession、software、musical instrument 的作业日志各返回 `PASS_STRICT`，每个 16 witnesses、0 native causal failures、16 exact representation flips；programming language 返回 `PASS_STRUCTURAL_EXCLUSION`；sport 与 academic discipline 仍在运行 | **3 个 INCLUDED roots、48/48 witnesses 已通过加强后的 artifact-level 独立复验**；另 1 个结构性排除通过复核。原 run 的 80/80 目前不能表述为 80/80 strict pass。 |
| WACT-G v1 preflight | [Clean run 36541670322](https://github.com/MKLEE222/Multi-agent-systems/actions/runs/36541670322) 五仓库作业均成功且上传产物；[独立复验记录](OACR_WACT_G_V1_VERIFIED_UNDERPOWER_2026-09-29.md)给出相同 underpower 结论 | **preflight underpower 已复验通过**。cpython/numpy/systemd eligible=0，openssl eligible=6，curl 在结构门槛处退出；原 run 与 clean rerun 均执行了 **0 个 native merge outcome**。这不构成 WACT-G 的 WRITE-activation 阴性结果。 |

## 二、验收依据与边界

### L2b：修复后 clean replay

- Artifact-path 修复已落在 [workflow 提交 39161d4](https://github.com/MKLEE222/Multi-agent-systems/commit/39161d452066f0affbb3706deb5abe08aacac699) 和 [脚本提交 6a3a5e4](https://github.com/MKLEE222/Multi-agent-systems/commit/6a3a5e4e502282daf76a76dff90605aa22936764)。脚本在切换工作目录前解析输出绝对路径。
- Clean rerun 的日志直接给出 `deterministic_two_reconstructions_equal=true`、`h0_task_equal=true`、`separating_actions=[51,29,73]`；三个 action 的 branch task diff counts 分别为 3、11、5。产物 ZIP SHA256 为 `fb936b90fd51cfa3c1be5d9e249c333e1ab349ecbd449cd3d6091f6a9692a95a`。
- 这支持一个已复验的 learned 正例。单个 fold0 witness 尚不足以支持跨 seed、跨机制的发生率或稳定性结论。

### WACT-R：主门槛已过，严格复验仍在收尾

- 原始 run 的五个 INCLUDED roots 各有 16 个 prospective witnesses，合计 80；sport 与 academic discipline 的原作业日志分别报告 `PASS`、16 witnesses、0 native causal failures，前者 eligible distinctions=20，后者为 82。
- [Strict verifier 提交 1b768d5](https://github.com/MKLEE222/Multi-agent-systems/commit/1b768d53d833c1b2f445148e6fa5eb8ee70d497b) 改为独立重建页内容、图、SCC、closure、候选与 action 选择，并核对页 SHA、combined JSON、activation matrix、witness selection、native replay、`U/E` 和 activation spectrum。[Verification-only workflow](https://github.com/MKLEE222/Multi-agent-systems/commit/7077a4e6bc299f94a468c876cce0af26f301d856) 使用原冻结产物，不重访 WDQS，也不重跑 producer。
- 截至本快照，profession、software、musical instrument 的严格复验分别得到 16/16 exact representation flips、0 native causal failures；programming language 因 `redundant_candidates_lt_64` 按协议排除。
- [Interim acceptance](OACR_WACT_R_INTERIM_ACCEPTANCE_2026-09-29.md) 所述 relational-family 有限主 claim 保留。该实验的 activation certificate 由图 reachability 结构预测；跨 state substrate 的 WRITE-activation claim 尚未验收。Activation concentration 仍为次要观察。

### WACT-G：只验收 preflight 诊断

- [v1 独立复验记录](OACR_WACT_G_V1_VERIFIED_UNDERPOWER_2026-09-29.md)说明 global second-parent target pool 无法在足够多的 natural same-tree pairs 上同时找到 inert 与 activating target；即使 numpy/systemd 有大量 same-tree pairs，eligible 仍为 0。
- 五个冻结仓库和 head 已明确。允许的 v2 后继是在任何 merge outcome 前，改变 outcome-blind target construction；需保留原仓库和 head，不按结果替换 carrier。
- Git v2 native merge 尚未启动。不能把 v1 写成负实证或跨 substrate 失败。

## 三、当前 claim 台账

1. **已验收：** 前轮 R3/G5 的有限 shared-contract 双向失配；L2b fold0 的 targeted learned native replay；WACT-R relational family 至少 3 个 roots、48 个 witnesses 的 strict artifact-level verification；WACT-G v1 的 preflight underpower 诊断。
2. **已达预注册主门槛，等待全量严格收口：** WACT-R 原始五个 INCLUDED roots 的 80/80。严格复验目前确认其中 48/48；sport、academic discipline 仍在 strict run，food、disease 仍在原 producer。
3. **尚未验收：** WACT-R 八 root 最终汇总；Git native WRITE-activation；跨 substrate 的通用 WRITE-activation claim；learned positive 的跨 fold/seed/机制稳定性；OACR-guided representation redesign 的广泛适用性。

## 四、下一道验收门槛

- 等 [strict run 36552116448](https://github.com/MKLEE222/Multi-agent-systems/actions/runs/36552116448) 的 sport 与 academic discipline 出结果。逐项核对 `PASS_STRICT`、witness 数、0 native causal failures、representation flips 和产物上传；失败则先定位并修复代码或验证逻辑，再作 clean rerun。
- 等 [原始 WACT-R run 36526302297](https://github.com/MKLEE222/Multi-agent-systems/actions/runs/36526302297) 的 food 与 disease 结束，按预注册 inclusion/exclusion 规则汇总全部八个 roots；不替换不利结果。
- 严格复验收口后，再注册 WACT-G v2 的 outcome-blind target selection，先复验 eligibility，再执行 native merge。保持五个 frozen repos/head 不变。
- 把 learned 侧从 fold0 单例扩至独立 fold/seed 或第二种 persistent-state WRITE 机制，并预先定义 collision、action 与成功门槛。

**验收纪律：** 当前不将 WACT-R 80/80 写成全量 strict pass，也不将 WACT-G v1 preflight underpower 写成 native WRITE 阴性。新科学协议以严格复验收口后的冻结版本为起点。
