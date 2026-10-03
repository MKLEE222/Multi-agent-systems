# OCAR：表示与支持证书的联合维护

日期：2026-10-02。起点：`e214458f4649a4281514b5c1ffb166e4af0bb331`。
协议、候选与对照代码在新运行前提交为
`34c4df3e532a8f75a08da27f1a317a14410a59eb`。

判定：**支持删减后的联合正确性缺口已在限定模型中补上；候选与通用证明 DAG
复用对照完全相同，尚无独有方法优势。物理边数最小不等于完整维护状态的字节最小。**
这是同一助手实现与证明调试，未关闭独立审查、T2/T5 或自然维护证据。

## 1. 研究目标与继承成果

本轮承接 BRFP → OCAR，保留既有修补、识别、原生图构造、来源接口、组件交互和
预算更新成果。用户明确将“现象、理论、方法每层各自具有独立创新”定为尽量达到的
研究目标；原 gate 的最低验收要求不充当研究上限。JCR Q1 是选刊条件，不能降低
科学目标，也不自动要求某一层先被判定为首创。

问题仍由自己的组件、算子和合法来源定义，同时在共同任务、相同信息权限和完整
成本下与现有方法竞争。不能把组成性的证明复用或少于全重建的调用数直接升格为
新算法，也不能因新候选被成熟解释覆盖而抹掉已有成果。

本轮只解决上一轮的具体执行缺口：合法消耗预算后，canonical 表示可删掉支持边，
旧路径证书却仍引用该边。原生输出正确与证书仍有效须分别检查。

## 2. 对象、输入与维护程序

继承的模型为公开潜在 DAG、完整可达性观察、只允许删除 base edges 的动作集 A、
剩余预算 h、持久 additions、冻结独立来源和 singleton 查询。每次合法删除消费
一单位预算，不能重置 h。来源/权限/实体版本变动及契约扩张不在本轮范围内。

实际状态含公开图 G、A、h、物理 additions r、候选身份、已确认否定事实、支持
节点 Γ、固定拓扑次序和来源 epoch。依赖索引按实际证明路径构造并计字节与遍历
成本。更新函数不接收真实 additions、来源接口或未来结果。

初始化来自已有 `compile_from_source`，所有方法共享相同可见初态。更新有三步：

1. 删除 arrived action，消费预算；检查 epoch 与前态 contract token。
2. 要求 canonical 的方法用同一个 bounded-flow 程序扫描旧 r；输出新 r 及每条
   新删支持边的路径证明。保留旧支持的对照另列，不要求 canonical。
3. 更新省略证明，独立检查新表示上的全部证明 DAG，记录完整维护状态字节。

候选允许证明节点引用别的证明节点：`b=0→2` 物理删掉后，旧 `e=0→3` 证明中的
`0→2→3` 可以引用 b 的新证明 `0→1→2`。b 的身份和证明均收费；解释器不把 b
当作仍存在的物理边。

## 3. 组成性工作引理及更新不变量

记 `G\F ∪ r` 为实际残余图，F⊆A 且 |F|≤h。每个证明节点 e 存有 h+1 条从
e 起点到终点的抽象路径。实际可删边在同一节点的不同路径中至多出现一次；
其他边必须是当前物理保护边、物理持久边或具有有效证明的虚拟边。证明依赖无环。

**引理。** 若每个虚拟边都针对同一 A、h 成立，则每个节点在实际图上对全部
F⊆A、|F|≤h 都成立。

证明：按证明依赖的拓扑次序归纳。固定任意 F。在一个节点内，最多 h 条抽象路径
包含 F 中的实际可删边，因此至少一条路径幸存。该路径的每条虚拟边由更早节点的
归纳结论提供实际可达路径；逐段连接便得到实际可达性。不同节点可共享可删边，
不要求全部展开后的路径仍两两边不交；统一的全称失败集合保证组成性。

这是普通全称性质、可达性传递与证明代换的实例，不以此申报新理论。

一次合法删除 f 后，各节点移去含 f 的唯一抽象路径；无路径含 f 时移去一条。
剩余 h 条路径适配 h−1 预算。新删支持边的证明来自新的 canonical prefix，
旧依赖沿严格较短拓扑跨度，所以不会出现依赖循环。重复执行仍有相同不变量。

原生行为维护分别由两项继承性质成立：旧 r 在删除 `{f}∪F` 下保留原行为；新的
canonical r 在新 G、A、h 上与旧 r 等价。组合证明不会从来源中恢复任何遗失真值。

这一工作论证建立的是本模型中的联合安全性；不是形式证明助手证书或独立作者
审查。实际代码另有完整 failure/BFS 回放。

## 4. 共同对照与冻结开发范围

协议：[joint_certificate_maintenance_v1.json](../experiments/oacr_theory/joint_certificate_maintenance_v1.json)。
算子：[joint_certificate_maintenance_v1.py](../experiments/oacr_theory/joint_certificate_maintenance_v1.py)。
审计：[audit_joint_certificate_maintenance_v1.py](../experiments/oacr_theory/audit_joint_certificate_maintenance_v1.py)。
结果：[OACR_JOINT_CERTIFICATE_MAINTENANCE_RESULT_2026-10-02.json](OACR_JOINT_CERTIFICATE_MAINTENANCE_RESULT_2026-10-02.json)。

四种 canonical 方法共享完整输入、表示目标和 canonicalization 原语：

- `cold_flat`：每次重算全部省略组件的 literal-path 证明。
- `dependency_flat`：运输 literal paths，仅对物理支持消失的证明重新求 flow。
- `substitution_dag`：候选；把新删支持边绑定到新证明节点。
- `generic_dependency_dag`：另写的 bottom-up justification substitution，对照允许
  使用相同证明语言。这是本轮实现的通用组成性控制，**不是 Doyle TMS、UpProver
  或 ICALP 动态图算法的外部软件复现**。

第五种 `persistent_flat` 保留旧 r 并运输证明；其原生行为与证书必须正确，
物理最小性不作为目标，多保留的 additions 和全部字节仍计费。

开发银行严格复用上轮种子与生成次序：60 个公开图配置、744 个完整来源状态。
每个来源枚举所有合法有序删除前缀，初始 h≤2、至多五条允许动作。
共 7,068 个历史状态、6,324 次更新，不把重复来源、顺序或方法视为独立样本。
另有八个事先固定的链式压力例，均为工程构造，不是自然现象或独立确认。

## 5. 结果：正确性成立，通用对照追平

| 方法 | 更新 flow 请求 | 增广次数 | BFS 弧检查 | 7,068 状态的 bundle 字节之和 |
|---|---:|---:|---:|---:|
| 全部 literal 证明重算 | 38,654 | 24,473 | 718,328 | 4,096,495 |
| 依赖失效后局部 literal 重算 | 18,444 | 3,249 | 315,779 | 4,090,323 |
| 候选证明代换 DAG | 17,769 | 2,572 | 302,098 | 4,091,953 |
| 通用 dependency-DAG 对照 | 17,769 | 2,572 | 302,098 | 4,091,953 |
| 保留旧物理支持 | 0 | 0 | 0 | 4,000,589 |

所有方法均执行 6,324 次更新、零更新来源查询。所有 canonical 方法返回同一
物理表示；候选和通用 DAG 对照在全部 7,068 个状态返回相同证明节点与字节。
候选比 dependency-flat 少 675 次 flow（其总 flow 的约 3.66%），这个实现差异
被通用证明复用解释，不能成为独有方法优势。

这张字节表是相同观察状态权重下的序列化快照之和，不是部署的总存储、RSS、
独立样本效应或最优编码界。单次时间只保留在 JSON 作为诊断。共同初始化另外计：
752 次（744 开发世界+8 压力例），5,076 次 flow、1,668 次来源查询；每个方法
部署时都应承担一次对应初始成本，不能把它们免费掉。

审计累计：77,120 组实际图/参考图的 failure 结果对；239,155 个虚拟边原生检查；
35,380 个方法状态证明检查（含压力例）；71,128 个保留边原生必要性见证。
5,032 个计费 flow 结果与原 producer 相同。非法动作、耗尽预算、过期 epoch、
错误前态、缺失依赖、自引用、循环引用、共享可删边与不足路径均被拒绝。
这些是有限开发检查，不能替代一般证明或独立作者审查。

代码/协议哈希保存在结果中，运行期间未更改。无结果后修正或选优。
ledger SHA-256：`af0a388eeb3648ae4e20631a9a49818343c5bfaa1ab5cbd39b2ae276bfdc1015`。

## 6. 一个必须带到下一轮的成本边界

继承的六节点反例，现在可输出物理空 additions 与有效两节点证明 DAG：b 由 base
chain 证明，e 引用 b。它补上了执行缺口，却不意味着总成本最优。

在预先固定的 12 节点主链压力例中，消费断开的无关删除边后：

| 方法 | 存储 additions | 更新 flow | 完整 bundle 字节 |
|---|---:|---:|---:|
| canonical literal 重算 | 0 | 11 | 1,272 |
| canonical 证明 DAG | 0 | 1 | 1,208 |
| 保留旧支持 | 1 | 0 | 1,163 |

最后一行有一条冗余物理边，但其完整维护状态更小，所有允许后续行为仍正确。
两种 unknown 真值分支给出相同结果，因为该未知边无需取证。
这只是本序列化格式与工程压力例的具体边界；不能称为自然发现或独立新现象。
一般结论应收窄为：**只最小化实际 additions 数，没有优化证明、索引、元数据和
更新工作的总目标。** 不能通过删去证书成本保住 canonical 优势。

## 7. 直接近邻与贡献权限

- Jon Doyle, *A Truth Maintenance System*, Artificial Intelligence 12(3), 1979,
  DOI `10.1016/0004-3702(79)90008-0`，出版社摘要明确覆盖记录/维护理由和依赖。
  https://www.sciencedirect.com/science/article/pii/0004370279900080 。本轮可读取摘要，
  全文抓取被拒；不据此声称全文已覆盖我们的故障预算模型。
- Albert, Arenas, Puebla, *Some Issues on Incremental Abstraction-Carrying Code*,
  arXiv:cs/0701111，2007，全文 §5–6 覆盖增量证书与增量检查，
  https://arxiv.org/pdf/cs/0701111 。更新后的程序和安全证书联合维护已有基础。
- Asadi et al., *SMT-based verification of program changes through summary repair*,
  DOI `10.1007/s10703-023-00423-0`，全文 §3–4 覆盖摘要复用、弱化、修复及正确性。
  https://link.springer.com/article/10.1007/s10703-023-00423-0 。不把其 SMT 的程序
  修订接口等同于本轮来源受限图契约；也不声称已运行 UpProver。
- Goranci et al., *Fully Dynamic Algorithms for Transitive Reduction*, ICALP 2025,
  DOI `10.4230/LIPIcs.ICALP.2025.92`，全文 Theorem 1.1、§5：已知 DAG 的传递
  约简已有 O(m) amortized 动态维护；
  https://doi.org/10.4230/LIPIcs.ICALP.2025.92 。正式全文同时可从
  https://drops.dagstuhl.de/storage/00lipics/lipics-vol334-icalp2025/LIPIcs.ICALP.2025.92/LIPIcs.ICALP.2025.92.pdf
  读取。本轮既未实现其算法，也未证明其结果直接适用于未知来源/全未来故障契约。

本次只完成定向近邻检查，不是文献穷尽。组成性证书复用不晋升为独有主算法。

## 8. 下一步的具体研究对象

用户随后明确要求下一步追问底层算子。具体的读写、前提、失败语义、结构需求
构造与待证明问题见 [底层算子追问](OACR_JOINT_OPERATOR_QUESTIONS_2026-10-02.md)。
该补充不改变本轮冻结协议或执行结果。

现在有可执行的 `(r,C,snapshot,Γ,index)` 基线，可以检验更高的目标：

1. **现象目标**：真实原生任务中，表示压缩何时把负担转移到证书、来源或重算？
   哪些支持干预预测这种转移，哪些无关干预不产生它？先固定自然组件与成本，
   不通过人为放大记录大小制造优势。
2. **理论目标**：对可得来源和允许表示/证明语言联合刻画可维护性与完整成本，
   特别是何时能把表示选择、证明选择和补取分开优化，何时这种分解损失可证明。
   这一目标尚未求解，需与知识编译、证明压缩、ECD/SBFE、动态维护直接比较。
3. **方法目标**：根据上述耦合决定保留支持、换证明、补取或局部重算；不能只做
   canonical 边删减。固定完整成本后，与成熟证明复用、来源策略、完整保留和
   重建同台。当前通用 DAG 对照必须保留为强基线。

回到 BRFP 的 BFCL 原生工具接口前，先固定真实表示、来源生命周期、实体版本、
权限与 evaluator adapter，验证这里的证明/成本对象确实存在。尚未执行这一自然
接口或外部任务，不能把图开发检查转成 BFCL 新成绩。旧 512 单位继续封存。

唯一验收仍为 [原 gate](OACR_FINAL_UPGRADE_ACCEPTANCE_GATE_2026-09-30.md)。

```bash
PYTHONDONTWRITEBYTECODE=1 python experiments/oacr_theory/audit_joint_certificate_maintenance_v1.py --out /tmp/oacr_joint_certificate.json
```
