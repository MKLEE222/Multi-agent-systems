# OACR support lifecycle：ATMS / provenance 冷启动反证

日期：2026-10-03。范围：只审查分配的抽象及公开一手文献；未读 benchmark gold、私有 DB 或受保护任务正文，未调用额外模型 API，未改 producer。下文的 reduction / 数值反例是本次推导，明确区别于论文已有结果。

## 判定

**“动作专属证书有多组支持，事件后保留未坏部分、改走另一组支持，必要时补证”的对象与基本维护机制已经被成熟框架覆盖。** ATMS 不是单依赖 invalidation；provenance 也不是只有一条 proof 的缓存。把 binding / guard / authorization / effect 合成动作索引的目标节点，本身不能构成对象新颖性。[1–5]

**尚不能从所查文献确认：一套现成算法直接最优求解合法、结果未知的查询策略，加上选择性保留、跨期维护和再获取的总成本。** 这不等于该目标是新问题，也不否定具体算法仍可能有增量；必须先固定成本、查询结果语义、事件过程与契约编译，再比较同条件的强 baseline。

## 1. 对象的严格对齐

固定动作实例 `a`，令其安全条件为 `φ_a = B_a ∧ G_a ∧ U_a ∧ E_a`。假定背景理论 `T` 精确编码合法世界和动作转移契约，合法可见证据是带来源、版本及有效条件的 literals。则：

`∀w ∈ Compat(I): w ⊨ φ_a` 等价于 `T ∧ I ⊨ φ_a`，也等价于 `T ∧ I ∧ ¬φ_a` 不可满足。

某组证据 `Γ ⊆ I` 是充分证书，当且仅当 `T ∧ Γ` 可满足且 `T ∧ Γ ⊨ φ_a`。可满足性用于排除矛盾证书的真空保证。

在有限 propositional / Horn 实例中，把四个义务及其合取引入为 ATMS nodes；证据激活条件作为 assumptions，契约推理作为 justifications。目标节点的 label 正是所有一致、包含意义上最小的充分 environments 的 antichain。规则完备时，合法当前 environment `A_I` 下可执行，当且仅当存在 `Γ ∈ label(safe_a)` 满足 `Γ ⊆ A_I`。[1] 对任意有限命题子句，CMS 的 minimal supports / prime implicants 给出同类模型论对象；可用辅助原子表达合取目标。[2,3]

这是条件 reduction：TMS 不会自动发现正确的原生 effect、授权语义或遗漏的兼容世界。仅有 sound、未必 complete 的 justifications 时，label 对已提交推理完备，未必包含语义上所有充分证书。[2,4] 不能把来源可信、信息合法可见和事件映射完备性当作 ATMS 自带保证。

## 2. 成熟算法已经做到什么

| 分配对象 | 已核查的成熟机制 | 不能偷换的边界 |
|---|---|---|
| 多组 alternative support sets | ATMS label 同时保持一致、sound、complete、inclusion-minimal；union / conjunction 产生并化简 environments。[1 §4.2, §4.7] | inclusion-minimal 不等于 minimum-cost。 |
| 部分事件破坏后保留和切换 | 新 justification 的 label delta 沿 consequents 传播；nogood 清除含坏环境的支持，其他 alternatives 留存；当前 context 用 subset test。[1 §1.1, §4.7] | 不能把任一前提变化等同全量刷新。 |
| 撤销推导 | 为 justification 加额外 defeasability assumption，撤销时将其置为 nogood；论文也提供正确但昂贵的直接 retraction。[1 §4.9] | 永久 nogood 不应随后“复活”；补证应使用新版本 token 或更新 context。 |
| alternative derivations / joint use | `N[X]` 的加法表示替代推导，乘法表示联合使用；`PosBool(X)` / minimal witness why-provenance 保留最小支持集合。[5 §§3–4; 6 slides 17–21] | `x=0` 可以表示证据不可用于证明，不表示未知世界事实 `¬x`。 |
| 插入 / 删除后的增量 provenance | ORCHESTRA 有 delta rules 和 `PropagateDelete`；受影响 tuple 若仍能由 trusted base facts 推导则保留，含环时检查 grounded derivability；有 DB2 实现。[7 §4.2, Fig.3, §5] | 简单计数不能可靠处理无 base grounding 的支持环；强 baseline 应保留该检查。 |
| 不一次枚举全部解释 | AAAI 2024 用 SAT 逐个构建 Datalog why-provenance explanations。[8] | 这里的 incremental 是解释枚举，不能据此声称已有事件维护或全生命周期最优算法。 |

版本化证据失效可映射为旧激活 token 不再可选；补回合法查询结果后加入新 token 和相应规则。这是上述框架的普通输入更新，不需要引入新支持对象。是否正确覆盖原生事件依然取决于共同的事件/契约编译器。

## 3. minimum-cost witnesses / repair：已有覆盖与计费陷阱

**静态已知支持。** 若完整 antichain `L_a` 已给出、所有候选证据合法且有效、成本是非负的每 token 一次计费，则 `min_{Γ∈L_a} Σ_{x∈Γ} c(x)` 精确求得单次最便宜证书。保留项及已知可成功取得的缺失项可以并入 `c(x)`。这是在已有 supports 上的直接精确选择；无需全刷新，也不意味着计算或存储 `L_a` 廉价。

**现成优化文献。** Hu–Sintos 的 smallest-witness problem 最小化保留的 sub-database，并在无 self-join CQ、固定 query 的 data complexity 下给出 head-cluster 的多项式精确算法和困难性的 dichotomy；也讨论单个结果的 witness primitive 与多结果共享。[9 §1.3, §3, Algorithm 1] Xu 等给出非递归 Datalog 带 negation 的 and-or repair tree，覆盖所有 minimal repairs，及 tropical 成本示例；作者明确使用 active-domain CWA。[10 §§3,5] Comer–Tannen 2026 给出 minimum-cardinality missing-answer repair 的具体复杂性与算法上界；其 semi-positive Datalog 在 data complexity 下可多项式求解，projection+join 的 combined setting 则 NP-hard。[11 §§3–5]

**repair 不自动等于 reacquire。** [10,11] 中 repair 是实际插入/删除数据库 facts 使答案出现。付费读一个未知事实改变的是信息状态，不能预设世界会返回所需事实。二者只有在查询输出及其合法性已确定、获取事实不会改变世界等额外假设下才能直接对齐。

**tropical 计费反例（本次推导）。** 对 provenance `P=x²+yz`，取 `c(x)=3,c(y)=c(z)=2`。按 leaf occurrence 的 tropical evaluation 得 `min(6,4)=4`，选 `{y,z}`；若真实成本是保留唯一证据一次，`{x}` 成本为 3，应选 `{x}`。四个动作义务共用证据也会造成同样差异。`PosBool` 有 `x∧x=x`，而正成本 tropical multiplication 有 `c+c≠c`，故不能从最小 Boolean supports 无条件保真地映射到该计费。应与 unique-set / shared-query 成本的 witness 优化比较，而不是只给 token 填 tropical 权重。[5 的 semiring 定义；6 的 hierarchy；反例不是论文结论]

## 4. 严格复杂性与成本反例

**Set Cover reduction（本次推导）。** 给集合覆盖实例 `U={e_1,…,e_m}`、集合 `S_j` 和非负权重 `w_j`，为每个集合建可合法保留的证据 `x_j`；对每个 `e_i∈S_j` 加 Horn 规则 `x_j→g_i`，再加 `g_1∧…∧g_m→safe_a`。可令 binding、authorization、effect 恒真，guard 包含这些检查义务。背景无 nogood，所有证据当前有效，maintenance / reacquire 成本为 0。

选中 `Γ` 能推出 `safe_a`，当且仅当对应集合覆盖 `U`；保留成本恰为 `Σ_{x_j∈Γ}w_j`。未覆盖时，令未选 `x_j` 为假并取 Horn least model 就给出一个不满足安全目标的兼容世界。因此最小保留成本恰为 weighted Set Cover 的最优值；unit-cost bounded decision 在这个有限 Horn 子类中 NP-complete（可猜 `Γ` 后多项式 forward-chain 检验）。该下界属于不受限义务/证明图的 combined input，不可套到固定无 self-join CQ 的单结果 witness。

**显式 antichain 的输出下界（本次推导）。** `∧_{i=1}^m(x_i∨y_i)` 有 `2^m` 个最小 supports，却有线性大小的 AND/OR DAG。声称“维护所有最小支持总能多项式”不成立；也不能由此推出 compact symbolic provenance 或按需枚举无效。CMS 原论文明确讨论 prime implicants 的指数数量及编译/检索取舍。[2 §4.2]

**静态便宜不等于跨期便宜（本次推导）。** supports 是 `{x}` 与 `{y,z}`；初始保留成本分别 1 与 2。已知下一事件一定使 x 失效，合法补回 x 的费用 100，而 y,z 均继续有效。只按初始最低 witness 选择产生总成本 101，选 `{y,z}` 为 2。ATMS 可表示和维护两条路径，但单次最小成本评价没有优化该事件过程。这只否定把静态选择直接当 lifecycle optimum；它不是新算法或新问题声明。

## 5. 审查落点

已覆盖的抽象不可再作为主要贡献：operation-indexed 目标、多条最小充分支持、局部失效后的剩余支持、alternative 切换、插入新支持以及静态 witness 选择。合格 baseline 至少应允许 ATMS antichains 或 compact provenance、剩余推导检查、增量 insertion/deletion；成本实验必须给它相同合法候选证据和真实计费。ATMS 与 ORCHESTRA 是分别已有的算法，不声称这里拼装出一套已发表的全目标最优算法。

尚须严格证明的差异：未知结果的合法自适应查询；查询批量产出/共享计费；长期选择性保留和维护预算；事件模型及最优性准则（known trace、expectation、worst case 或 competitive）；原生动作 contract 的可靠编译。它们可能落入既有 abduction / information gathering / planning / view selection 工作，本报告未完成那些领域的穷尽检索。因此：**kill 抽象新颖性，不据“可表达” kill 所有具体算法；未确认覆盖也不授予新颖性。**

## 一手来源与实际查验范围

所有检索与页面查验均于 2026-10-03 完成；只记录实际读到的正文/摘要范围，不声称复现实现。

1. Johan de Kleer (1986), *An Assumption-Based TMS*, AI 28:127–162. [作者 PDF](https://dekleer.org/Publications/An%20Assumption-Based%20TMS.pdf)。查验 §1.1, §4.2, §4.7–4.9；重点：label invariants、delta propagation、retraction。
2. Raymond Reiter & Johan de Kleer (1987), *Foundations of Assumption-Based Truth Maintenance Systems: Preliminary Report*, AAAI:183–188. [会议 PDF](https://cdn.aaai.org/AAAI/1987/AAAI87-033.pdf)。查验 §§1–2, §4.2, §§5–6；minimal supports、entailment、prime implicants、指数编译成本。论文自称 preliminary；合取 query 不可直接宣称是其原始接口。
3. Johan de Kleer (1986), *Extending the ATMS*, AI 28:163–196. [作者 PDF](https://www.dekleer.org/Publications/AIJ%20Version%20Light%20Copy.pdf)。查验 §6 propositional encoding、§8 interpretation construction；不据此宣称通用高效计算。
4. Johan de Kleer (1986), *Problem Solving with the ATMS*, AI 28:197–224. [作者 PDF](https://www.dekleer.org/Publications/Problem%20Solving%20with%20the%20ATMS.pdf)。查验 §2.1 正确 justifications 与 reasoner/TMS 边界；未核其全部 problem-solver 实现。
5. Todd J. Green, Grigoris Karvounarakis & Val Tannen (2007), *Provenance Semirings*, PODS:31–40. [作者 PDF](https://www.cs.ucdavis.edu/~green/papers/pods07.pdf)。查验 §§3–5, §8；`N[X]`、`PosBool`、homomorphism、tropical、递归求值；原 RA+ 不包括一般 negation。
6. Val Tannen (2017), *The Semiring Framework for Database Provenance*, PODS invited tutorial. [作者 slides](https://www.cis.upenn.edu/~val/15MayPODS.pdf)。查验 slides 15–21；witness/minimal witness、计数与集合语义 hierarchy。官方作者教程，非独立算法性能证据。
7. Green, Karvounarakis, Zachary G. Ives & Tannen (2007), *Update Exchange with Mappings and Provenance*, MS-CIS-07-26（修订 VLDB 2007 版本）. [作者 PDF](https://www.cs.ucdavis.edu/~green/papers/TechReport07.pdf)。查验 §4.1.3, §4.2 Fig.3, §5, §6.3；增量删除、trusted grounding、DB2 实现。Tukwila deletion 当时未完整实现，不夸大为所有 backend 都有。
8. Marco Calautti, Ester Livshits, Andreas Pieris & Markus Schneider (2024), *Computing the Why-Provenance for Datalog Queries via SAT Solvers*, AAAI:10459–10466. [会议页面](https://ojs.aaai.org/index.php/AAAI/article/view/28914)；[会议 PDF](https://ojs.aaai.org/index.php/AAAI/article/view/28914/29739)。核摘要与作者公开 PDF，逐解释 SAT 枚举；未核事件更新/最优成本实现。
9. Xiao Hu & Stavros Sintos (2024 version), *Finding Smallest Witnesses for Conjunctive Queries*. [作者 arXiv v3 正文](https://arxiv.org/html/2311.18157v3)。查验 §1.3, §3, Algorithm 1，及 approximation 摘要；本文引用这一明确版本，未套用后续 TODS 版本可能变化的表述。
10. Jane Xu, Waley Zhang, Abdussalam Alawini & Tannen (2018), *Provenance Analysis for Missing Answers and Integrity Repairs*, IEEE DE Bulletin 41(1):39–50. [出版社 PDF](https://sites.computer.org/debull/A18mar/p39.pdf)在本次 open 中失败；改核[作者 Alawini 上传的完整正文](https://www.researchgate.net/publication/325090722_Provenance_Analysis_for_Missing_Answers_and_Integrity_Repairs)，非引用第三方综述。查验 §§1,3,5；CWA、repair tree、成本定义，未验证代码。
11. Jesse Comer & Val Tannen (2026), *The Complexity of Finding Missing Answer Repairs*, ICDT, LIPIcs 365:12. [会议正文](https://drops.dagstuhl.de/storage/00lipics/lipics-vol365-icdt2026/html/LIPIcs.ICDT.2026.12/LIPIcs.ICDT.2026.12.html)。查验摘要、Definition 3.1–3.2、Tables 1–2、§4 的最小 repair 上界；其 cardinality objective 不是任意 weighted lifecycle objective。
