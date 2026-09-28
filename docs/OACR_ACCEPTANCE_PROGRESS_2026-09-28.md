# OACR 验收进度 — 2026-09-28

## 验收依据

- 冻结结果：[V2 checkpoint](https://github.com/MKLEE222/Multi-agent-systems/blob/5cc8baf1db8b66061032da6c99723a2956f98121/docs/OACR_CHECKPOINT_2026-09-28_V2.md)，提交 [5cc8baf](https://github.com/MKLEE222/Multi-agent-systems/commit/5cc8baf1db8b66061032da6c99723a2956f98121)。
- 本次已在 GitHub 核对 checkpoint 提交、R3/G5/L1 的 Actions 作业结论、产物 ID 和产物摘要。以下实验数值取自冻结 checkpoint，并核对了分区数量与所报 pair/gap 数值的内部一致性。本记录没有重新计算 ZIP 内的原始结果。
- “验收通过”均限于所列 state bank、操作契约、观测规则和实验版本。

## 已验收进度

| 项目 | GitHub 证据 | 验收状态 |
| --- | --- | --- |
| R3 shared-contract relational | [Run 36385544527](https://github.com/MKLEE222/Multi-agent-systems/actions/runs/36385544527)：`oacr-r3` 成功；产物 `oacr-r3-v1`（ID 10954033797，ZIP SHA256 `0d631fd0436331d4aa02fa05c510efbb3e3fced140990f2932898741ba9ff29d`） | 272 个同 closure 状态面对统一 64 项 deletion contract，形成 101 个 H=1 operational classes；通过有限 exact carrier 的 same-contract 验收 |
| G5 Git discovery / held-out validation | [Run 36385706858](https://github.com/MKLEE222/Multi-agent-systems/actions/runs/36385706858)：discovery 和 validation 两个作业均成功；产物 ID 分别为 10954224696、10954788549 | 两组互不重叠的 48 对 natural same-tree pairs 使用统一 12-target contract；held-out validation 结果进入有限自然 carrier 的验收 |
| L1 GRACE H=2 | [Run 36383356207](https://github.com/MKLEE222/Multi-agent-systems/actions/runs/36383356207)：5 个 seed 作业均成功，5 个产物均存在 | negative diagnostic 已完成；未取得 horizon-induced separation witness |
| M1 directional U/E | [实现](https://github.com/MKLEE222/Multi-agent-systems/commit/d0371e7cd28380cf8684e59cb9e56d0a4ad6457d)与[self-test](https://github.com/MKLEE222/Multi-agent-systems/commit/fd3ffd8974b09d912f32917a5366408d2a0ab0c3)已提交 | 测量工具的自测阶段通过；本记录未独立重跑 |

### R3：同一契约下的双向失配

Operational partition 为 1 个 172-state class 加 100 个 singleton，故 `1 < |O_1| = 101 < 272`。

- Closure-only：`U=3.391442481659308, E=0`；22,150 个 under-refinement pairs。
- Full asserted-edge identity：`U=0, E=4.69602035959104`；14,706 个 over-refinement pairs。
- 64 个 action endpoints 的 path-count profile：`U=3.391442481659308, E=0`，未恢复所需 distinction。

算术核对：`C(272,2)=36,856`，`C(172,2)=14,706`，二者之差为 22,150；272 个状态等权时，所报条件熵与 101-class 分区一致。

### G5：独立状态集上的有限契约匹配

Discovery 与 held-out validation 各有 48 对，其中各为 2 required separations、46 behaviorally equivalent。Validation 中：

- Current tree：`U=0.04166666666666696, E=0`。
- Full commit identity：`U=0, E=0.958333333333333`。
- Tree + 12-target ancestry vector：`U=E=0`，50 个 representation classes 与 50 个 operational classes 精确匹配。
- Tree + merge-base vector：`U=0, E=0.8124999999999991`，39 个 over-refinement pairs。

`0.04167=2/48`、`0.95833=46/48`、`0.8125=39/48`，与 checkpoint 所述 pair 结构一致。Ancestry vector 的结论限于该 frozen target panel 和 held-out bank；validation positives 只有 2 对，且 `already-up-to-date` 输出与 target ancestry 有直接结构关系。

### L1：结果已完成，正向目标未通过

Seeds 73、137、211、307、401 各只有 2 个有效状态、1 个 H=0 collision pair；5 对在 H=1/H=2 均无 separation，`N_0=N_1=N_2=1`。F2/F3 在 H=2 对 5/5 pairs 过度区分。该结果作为小规模 learned negative diagnostic 保留。

## Claim 验收结论

1. **有限 shared-contract 双向失配：通过。** R3 在同一 state bank 和 deletion contract 上给出 `U>0,E=0` 与 `U=0,E>0`；G5 held-out natural bank 在统一 merge contract 上给出同向结构。
2. **Operational partition 严格位于当前观测与完整内部身份之间：通过。** R3 有 `1<101<272`；G5 validation 的 target-ancestry vector 在注册有限 contract 上达到 `U=E=0`。
3. **Nested-contract 的跨 carrier 经验轨迹：待验收。** 对固定 representation 的理论单调方向已有定义；尚需同一 state bank、固定权重和真正嵌套的 contract 序列产生曲线。
4. **R3 紧致 sufficient representation / OACR-guided redesign：待验收。** 当前 support profile 失败，尚无经过独立验证的构造。
5. **Learned H=2 operational necessity：待验收。** L1 的五对状态没有出现 H1/H2 separation，规模不足以支持最终 learned block。

## 下一轮验收门槛

- 用 R3/G5 的固定状态集、固定权重和嵌套 action panels 输出每一级的 `|O|, U, E`，并检查分区细化关系。
- 从 R3 的 101-class target 构造紧致表示，明确开发/验证边界，在未用于特征选择的状态或操作上评估 `U/E`。
- 将 G5 扩展到额外仓库和更广的 shared merge panels，保持 prospective action selection 与 held-out validation。
- 扩大 learned 有效状态集并加入第二种 writable mechanism；先报告状态构造成功率与 H=0 collision 覆盖，再判定 horizon refinement。

当前可对外使用的结论是**上述两个有限 contract 核心 claim**。Git 普适最小性、R3 最小结构编码、learned horizon 正向结果、跨系统经验规律及 representation-design 方法尚未验收。
