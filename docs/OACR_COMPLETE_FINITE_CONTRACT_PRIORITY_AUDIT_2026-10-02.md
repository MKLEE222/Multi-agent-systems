# OACR 完整有限合同：定理优先权与独有优势审查

日期：2026-10-02。审查基线：PR #89，`bff89d104645d42012c05a5ed1db0c66136b60f8`。

本记录执行用户最新要求：理论对象是完整有限合同；具体定理的全球文献优先权与跨系统验证仍待推进；被成熟方法完整追平的候选不能作为主贡献。现象、理论、方法分别争取独立首创的目标保留。BRFP、原 OACR 的已成立结果保留，不能把升级失败倒写为基础工作失败。

## 1. 本轮决定

当前 DAG Need / joint Release，以及此前的查询选择、闭包单点证书和通用证明 DAG 维护，**退出独立主贡献候选**。正确性、实现、账本与反例仍可作为基础和共同任务对照。最近一轮通用 indexed classical-flow / proof-composition 对照匹配候选全部状态和计费工作；不是只匹配答案。候选增加初始化和存储成本，也没有完整成本优势。

本轮没有确定一个已经具有独立优先权的新核心定理，也没有新增跨系统算法收益。下面是有具体先行定理支持的排除结论与待解决对象，不是“全球文献已查完”或“整个研究问题已被覆盖”的声明。此次只核对已存记录与文献，没有新实验、模型调用或评测解封。

## 2. 理论对象：完整有限合同

沿用 `OACR_OPERATOR_FIRST_FOUNDATION_2026-10-01.md`。合同 C 给出有限、前缀闭合的允许原生操作词集合 L(C)，包含空词；规定各节点的观察、动作合法性与剩余预算。系统状态域对所登记操作闭合。状态相关的非法动作须使用统一索引与显式拒绝行为，不能按实际状态删掉测试项。

令 T_alpha 为实际原生执行，O_alpha 为合同在该节点要求的观察：

    B_C(x) = (O_alpha(T_alpha(x)))_[alpha in L(C)]
    L(C/a) = { beta : a beta in L(C) }

“完整”要求覆盖所承诺的每条合法历史及其观察，包括残余更新；不等于无限未来，也不允许每步重置有限视界。DAG 中的完整可达性与有限删除预算只是一个实例。缩小观察、改动作语义、增加权限或版本假设，必须形成另一个明确合同。

两个直接的继承事实用于约束后续命题，不申报新理论：

1. 对相同合同上下文，行为等价可按空词观察与各允许首动作的残余行为递归刻画。证明只需将允许词分成空词与 a beta。把有限合同上下文并入状态，就得到标准有限转移系统上的行为保持问题。
2. 已保存信息 I 能确定目标行为 Q，当且仅当 ker(I) 包含的每个纤维都落在 Q 的一个纤维中，即 ker(I) subseteq ker(Q)。这只是函数因子分解。它不提供物理表示、合法写入程序、来源恢复或计算成本界。

因此，完整语义不能由“一次修补正确”替代；但写下完整语义本身也不能取得定理优先权。

## 3. 按具体命题审查优先权

| 拟升格内容 | 已核对的先行结果 | 对 OACR 的结论 | 仍可能需要独立解决的部分 |
| --- | --- | --- | --- |
| 为所有合同内后续行为寻找最粗充分抽象 | Ranzato–Tapparo，Theorem 6.7 / Corollary 6.8：在其语言闭合条件下，以 forward complete shell 刻画最抽象强保持域 [P1] | 不能把完整行为商、最粗充分区分或算子族保持作为一般首创 | 指定物理表示与修补语言之后的构造和资源界；该先行定理没有替我们完成它们 |
| 对既有表示同时补充区分、删除多余区分 | Giacobazzi–Ranzato–Scozzari，Theorem 5.10：连续操作族下 complete shell/core 的构造性固定点刻画 [P2] | “双向修补”和一般存在性不能单独承担新理论 | 原生可执行语言中的可达性、实际取得信息与成本；不能只列新约束宣称已得到新定理 |
| 不完全信息下按观察取证并选择后续动作 | Bonet–Geffner 2000：belief-space contingent planning、感知结果分支及带动作成本的策略 [P3] | “查询与行动联合决策”这一一般形式已有先行工作 | 新结构是否让同样信息、同样动作集合下的精确维护获得更强界或更低完整成本 |
| 只靠合法可见信息维持所有允许执行正确 | Chatterjee 等 2007，Theorem 3.4：observation-based sure winning 与 knowledge-based subset game 等价；Theorem 3.9 给出 antichain 符号求解 [P4] | 一般可执行策略的存在性与按知识状态求解不能默认是新结果；强对照不止逐世界穷举 | 需要具体编码与资源一致的比较，不能将隐藏全状态或策略内存免费交给一方 |
| 按因果/感知依赖局部计算需求，并给出结构宽度复杂度 | Bonet–Geffner 2014，Theorems 15 / 22：sound and complete factored belief tracking，时间空间对其 width 指数 [P5] | “只查局部依赖”和泛称结构参数可解并未越过近邻 | 新参数必须定义、证明并与该 width 建立关系；全局枚举基线慢不是新下界 |
| 抽象正确后还能经接口原生执行 | Reissig–Weber–Rungger，Theorems V.4 / V.5 / VI.3：特定静态接口架构的反馈细化充分/必要条件及控制器转移 [P6] | “抽象能指导原生执行”一般保证也已有具体理论 | OACR 的表示写入、来源和证明存储是否引出不同可证明条件；先行接口定理不等于 OACR 全成本最优 |
| 完整任务保留条件下最小化系统 | Gleizer–Madnani–Mazo，finite-system ASE minimization [P7] | 保持控制器存在性下的最小化已有算法；不可泛称最小任务充分系统首创 | ASE 保留策略存在性，与逐原生词精确行为相同不是同一要求，不能偷换比较目标 |
| 证书很小，因此能以同样成本自适应找到它 | Kothari 等，Theorem 2：subcube partition 与决策树查询复杂度的分离 [P8] | 不能从逐状态证书大小直接推出一个统一策略的查询最优性 | 与 OACR 特定命题建立严格归约后才能用其上下界；这里只排除无证明推理 |
| 表示大小、可回答查询与可维护变换的联合权衡 | Darwiche–Marquis 的 knowledge compilation map [P9] | 联合讨论紧凑性、查询和变换并非新框架发现 | 必须落到不同的定理、有效构造及共同任务可验证收益 |

当前闭包单点证书还受此前冷审查中的 unique generation / interval fiber 先行结果约束；本轮不重复更名升格。上述先行定理各有假设，不能把任何一篇夸大为已经解决所有 OACR 物理修补。反过来，尚未完全相同也不能证明 OACR 首创。

### 有限合同为何不能绕开策略合成近邻

这是本轮的建模归约说明，不作为新定理：如果状态域、合法物理表示、可见元数据、来源版本/权限、修补原语、控制器内存与资源界均有限，可把它们和合同上下文组成有限状态。环境负责初始隐藏状态、合法原生请求及来源响应；维护方仅按实际可见信息选择查询或表示写入。发生原生观察错误、非法访问或资源越界即进入失败状态。合同结束成为安全终止节点。

这给出有限不完全信息安全博弈；允许任意观察历史内存时，精确维护策略的存在性可对接 [P4]。感知、写入和动作成本也可进入 [P3] 的控制模型。这不等于一个现实高效解：显式展开可能巨大，合成策略内存、具体序列化字节与在线计算不能免费。若另有控制器内存上限，必须限制策略实现并核对有界合成条件；不能直接拿 [P4] 的自由历史策略宣称资源一致的充要条件。[P10] 提供输出反馈与 bounded synthesis 的另一个直接近邻，但也不是 OACR 完整成本定理。若维护方可以暂停不响应，还必须编码终止期限，不能把永远查询当作成功。只声明“可归约、可合成”不能是新核心。

真正仍待追问的对象是：**对明确的原生表示/修补语言，能否从合同与已合法取得的结构信息，构造有独立资源界的精确维护程序，而非重新命名行为商或信念策略。** 当前尚无已证明并通过优先权审查的答案。

## 4. 跨系统证据：保留什么，尚缺什么

| 载体 | 既有证据及实际合同 | 可以支持 | 没有支持 |
| --- | --- | --- | --- |
| R4 building | 272 状态、64 删除动作、17,408 原生回放；22 个保留增量对应 23 行为类；fresh acceptance 有独立验证记录 | 图载体的物理补充/删减与该动作银行的精确行为保持 | 完整有限合同的新一般算子已在其他系统复制；组织/地理 producer 结果不能代替尚缺的独立验收 |
| SQEC v2 | 12 受控变体、4 个原生事件；深度至 2 的 20 个非空词，加当前观察；shared repair 用 1 条相关 guard，full restore 用 2 条，等成本 sham 失败 | 冻结有限合同内的因果修补和共享物理修补优势，结果保留 | 自动发现该结构、普适构造或相对成熟 CEGAR / synthesis 的独有优势 |
| 原生 Git | 相同 tree 分组、冻结 target panel 与实际 merge 观察；后续 H2 工程记录为 producer 暴露与验收区分 | 操作合同能区别当前内容相同的状态；自然载体的审计接口 | 新 Need / Release 规则在 Git 上执行并胜过共同对照；H2 自然机制阳性 |
| GRACE / 既有 FT | GRACE 66 dev 查询各方法相同；已有组合审计中 GRACE 为 H2 阴性，FT 一个可用折为 H1 区分、无新增 H2 | 已测作用与适用范围，包括真实阴性结果 | learned 表示的后续维护新收益或新增统一算子验证 |
| cache 探针 | 96 tiny 配置与 12 人工 pretrained 探针；测得精确因果复用 | 被测故障的执行修复 | 自然发生率、完整编辑器重复、未被近邻覆盖的算法优势 |
| 本轮升级 DAG | 744 来源世界、7,068 有序历史、6,324 更新；候选与通用对照全部状态和计费匹配 | 完整局部合同下正确维护、反例和成本账本 | 独有方法收益；多个图例不是异构跨系统验证 |

证据依据为本库的原验收与工程记录，不是本轮重新运行。尤其不能把“不同载体分别做过行为审计”改写为“同一个新增定理和构造已跨系统验证”。R4、SQEC、Git、learned 分支的历史结果不因本次升级门槛变更被删除。

## 5. 下一轮必须产出的具体对象

下一轮先交付一条**可被近邻直接检验的候选命题及分离实例**，再决定是否开发构造器。对象固定为完整有限合同；不得通过任意缩小观察/动作、增加不可得来源或给对照禁用相同支持来制造优势。

候选命题必须一次写清：输入表示和合同的描述长度、实际可见来源、物理修补原语、合法性/终止、所保证的精确行为、资源目标、结构条件，以及其相对最近定理究竟多出的结论。一般维持正确、存在策略、有限可解、最小行为商不再作为候选的新结论。

优先追问“支持交互使联合维护可计算”是否有独立内容：其结构参数是否确实比已有 factored belief width / symbolic abstraction 更有力；其证书是否产生可实现的查询与写入顺序；其成本界是否仍成立于全部合同内历史。当前这些都是问题，不是已成立定理。对新参数须给与最近参数的包含关系或分离族；对新算法须给强基线也允许同样结构与预编译的比较。

具体升级依据分三层记录：

1. **现象**：冻结前提出可干预预测；原生操作/支持干预与同成本 sham 区分机制；已有受控造例与自然发生率分开。
2. **理论**：逐条命题核对先行原文的假设和结论；新资源界、结构刻画或语义能力必须有证明。没有完全同名论文不构成全球优先权。
3. **方法**：共同输入、共同原生任务和公平权限下，相对成熟强对照得到可重复的独立收益；计入初始化、来源、物理表示、元数据/证明、维护与执行。跨系统应复用同一核心规则，只更换原生接口，并检验同一预测。

“独有优势”可以是新的可证明保证、真正不同的可处理结构范围，或明确的完整成本收益；不要求每个指标、每个系统都占优。但不能只改目标名称、给对照遗漏一个经典技巧，或用手调载体专用规则拼成跨系统算法。在上述三类中没有可独立检验的增量，就不继续把候选当作主贡献。这里保留三层独立首创的研究目标，并不声称目前已实现。

本轮不启动新的 DAG 枚举，不实施未冻结的公共任务实验，不读取 512 个封存评测单元。下一阶段的失败退出条件明确：候选命题被先行定理推出，或共同任务被资源一致的成熟方法完整追平，且没有剩余独立保证，则归入对照并终止该候选的主线投入。

## 6. 原文与证据索引

这是定向审查，不是全领域的穷尽式系统综述。下列原文已打开；所用具体定理/章节列出。2026 年相关控制架构论文的检索命中未能取得正文，本轮没有以该摘要作定理排除依据；近期后继工作和引用链仍须随具体候选继续检查。

- [P1] Ranzato, Tapparo. *Generalized Strong Preservation by Abstract Interpretation*. JLC 2007；原文 Theorem 6.7、Corollary 6.8：[PDF](https://arxiv.org/pdf/cs/0401016)。语言闭合假设不可省略；有限合同可借上下文扩展对接相应语义，不能直接宣称原文输出原生修补。
- [P2] Giacobazzi, Ranzato, Scozzari. *Making Abstract Interpretations Complete*. JACM 2000；Theorem 5.10 与 complete core/shell 章节：[作者 PDF](https://www.sci.unich.it/~scozzari/paper/JACM00.pdf)。连续性假设与 abstract-domain 格必须注明。
- [P3] Bonet, Geffner. *Planning with Incomplete Information as Heuristic Search in Belief Space*. AIPS 2000；belief-space contingent control 与成本策略章节：[AAAI PDF](https://cdn.aaai.org/AIPS/2000/AIPS00-006.pdf)。最坏情形与期望成本不能互换。
- [P4] Chatterjee, Doyen, Henzinger, Raskin. *Algorithms for ω-Regular Games with Imperfect Information*. LMCS 2007；Theorems 3.4、3.9：[期刊 PDF](https://lmcs.episciences.org/1094/pdf)。观察策略与隐藏真实状态策略必须区分。
- [P5] Bonet, Geffner. *Belief Tracking for Planning with Sensing: Width, Complexity and Approximations*. JAIR 2014；Definitions 10–14、Theorems 15、22：[期刊 PDF](https://www.jair.org/index.php/jair/article/download/10901/25996/20340)。其 width 依因果和 evidential relevance 定义，不能换名字后当新参数。
- [P6] Reissig, Weber, Rungger. *Feedback Refinement Relations for the Synthesis of Symbolic Controllers*. 2017；Theorems V.4、V.5、VI.3：[PDF](https://arxiv.org/pdf/1503.03715)。必要性针对其控制器/接口架构，不是任意 OACR 程序必要性。
- [P7] Gleizer, Madnani, Mazo. *A Simpler Alternative: Minimizing Transition Systems Modulo Alternating Simulation Equivalence*. 2022：[PDF](https://arxiv.org/pdf/2203.01672)。核对摘要及定义/引言；本轮不借其最小化结果推导 OACR 字节成本最优性。
- [P8] Kothari, Racicot-Desloges, Santha. *Separating Decision Tree Complexity from Subcube Partition Complexity*. APPROX/RANDOM 2015；Theorem 2：[Dagstuhl PDF](https://drops.dagstuhl.de/storage/00lipics/lipics-vol040-approx-random2015/LIPIcs.APPROX-RANDOM.2015.915/LIPIcs.APPROX-RANDOM.2015.915.pdf)。不是未经归约的 OACR 查询下界。
- [P9] Darwiche, Marquis. *A Knowledge Compilation Map*. JAIR 2002；引言与目标语言/查询/变换比较：[PDF](https://arxiv.org/pdf/1106.1819)。全文描述长度、预编译和在线成本须分开。
- [P10] Schmuck, Zareian. *Abstraction-Based Output-Feedback Control with State-Based Specifications*. 2021；Theorem 1、输出反馈合成与 bounded synthesis 章节：[PDF](https://arxiv.org/pdf/2104.10974)。可见输出与不可见状态谓词区分；本轮不把其算法声称为已经实现 OACR 的字节/来源/计算联合最优。

内部证据：

- `OACR_OPERATOR_FIRST_FOUNDATION_2026-10-01.md`
- `OACR_NOVELTY_INHERITANCE_LOCK_V1_2026-09-30.md`
- `OACR_SAME_INPUT_NEIGHBOR_COMPARISON_2026-10-01.md`
- `OACR_OPERATOR_COLD_REVIEW_2026-10-02.md`
- `OACR_INCREMENTAL_NEED_RELEASE_2026-10-02.md`
- `OACR_INCREMENTAL_NEED_RELEASE_RESULT_2026-10-02.json`
- `OACR_PHENOMENON_AND_MECHANISM_PROTOCOL_2026-10-01.md`
- `OACR_R4_BUILDING_FRESH_ACCEPTANCE_2026-09-29.md`
- `OACR_AUDIT_TO_REPAIR_ACCEPTANCE_RECORD_2026-09-30.md`
- `OACR_G5_SAME_CONTRACT_GIT_PROTOCOL_V1.md`
- `OACR_COMPOSE_G_H2_ENGINEERING_RECORD_2026-09-29.md`
- `OACR_COMPOSE_LEARNED_EXISTING_ASSET_AUDIT_2026-09-29.md`
- `OACR_R4_ORGANIZATION_SPLIT_STAGE_RERUN_RECORD_2026-09-29.md`
- `OACR_R4_GEOGRAPHICAL_SPLIT_STAGE_RERUN_RECORD_2026-09-29.md`

唯一总验收门仍为 `OACR_FINAL_UPGRADE_ACCEPTANCE_GATE_2026-09-30.md`。本记录改变主贡献候选的优先级，不改变封存评测、已取得结果或原门槛。
