# OACR support lifecycle 冷启动审查：partial-observation monitoring / runtime assurance / shielding

日期：2026-10-03。性质：定向近邻与表达能力审查；没有运行实验，没有改动冻结协议、实现或结果。只读取允许的仓库说明和公开 primary papers / official documentation；没有调用额外模型 API、benchmark gold 或私有数据库。

**判定：把“合法证据下所有兼容世界都满足动作义务、证据失效后局部更新、存在替代支持则继续、否则合法取证、每次提交前检查”作为统一对象，本身不足以排除成熟 belief monitoring + permissive shielding + costed observation 的解释。** 在明确的有限原生模型内，完整生命周期可以编译成带证据状态和成本的 belief game。这个覆盖是表达与基线构造结论，不是已经有现成工具自动提取任意 native API 的语义，也不是高效最小查询算法已被证明存在。下面列出具体编译及成立边界；不据此宣称全球无创新。

## 1. 被审对象与必须保留的语义

目标不是事后检查一条完整 trace。维护器面对尚未执行的原生动作 `a`，可见信息为 `I`，合法、当前有效的支持为 `Γ`，必须保证：

\[
 B(I)=\operatorname{Compat}(I)\ne\varnothing,
 \qquad \forall w\in B(I):\ \Psi_a(w).
\]

 `Ψ_a` 至少含 binding、guard、authorization 和 effect obligation。证书只引用 I 中合法有效的证据及可靠推理规则；它自身不能额外排除兼容世界。绑定到错误实体、过期版本或错误权限主体不是普通布尔 guard 缺失。若 effect 含不确定回执、失败或部分写入，义务须对规定的全部原生后继成立；不能用一次成功回执代替事前保证。下文把这些内容及剩余契约纳入模型，不把证书正确等同于世界事实不变。

事件可以使部分支持失效；另一份支持或符号相关性可能仍证明 `Ψ_a`。查询必须合法，返回证据后才缩小兼容世界。每次实际 commit 应有与当时状态/来源版本一致的有效证书。选择目标包含 retain、maintain、reacquire 及证明/索引/计算的成本，不限于来源请求数。

与仓库现有边界一致：[联合底层算子问题](OACR_JOINT_OPERATOR_QUESTIONS_2026-10-02.md) 已区分事实、行为义务、物理支持及证明变化；[联合证书维护](OACR_JOINT_CERTIFICATE_MAINTENANCE_2026-10-02.md) 的通用 dependency-DAG 控制须继续保留。本审查不把其冻结图模型扩张为已执行的来源/版本/权限模型。

## 2. primary sources 与实际阅读范围

“全文可读取”只表示检索器返回了完整 PDF/正文载体；下表另外声明本次实际精读范围。没有声称逐页通读所有正文、附录、证明与实验，也没有运行这些作者的软件。搜索命中的综述、ResearchGate/二次摘要及 2026 年新文献未用来支撑本文结论。

| 编号 | primary paper / official documentation | 本次实际全文范围 | 与目标的直接关系及限制 |
|---|---|---|---|
| P1 | Atkinson & Carbin, *Programming and Reasoning with Partial Observability*, OOPSLA 2020, DOI [10.1145/3428268](https://doi.org/10.1145/3428268)；[作者 arXiv 全文，43 页](https://arxiv.org/pdf/2101.04742.pdf) | 精读 §3.1、Fig. 9、§3.4 和 §4 开头；核对 `choose / observe / infer`、belief execution 和 epistemic Hoare judgment。未审全部附录。 | 运行时维护可能世界并对 belief 作模态判断已有直接编程语义；环境模型仍需开发者提供，不自动产生成本最优来源策略。 |
| P2 | Graf, Peled & Quinton, *Monitoring Distributed Systems using Knowledge*, FMOODS/FORTE 2011, DOI [10.1007/978-3-642-21461-5_12](https://doi.org/10.1007/978-3-642-21461-5_12)；[作者全文，15 页](https://www-verimag.imag.fr/~graf/PAPERS/2011-GrafPeledQuinton-Forte-11.pdf) | 精读 §1、§2 的 state-equivalence / Def. 9，以及 §3 开头 Def. 10。未逐页审后续案例与算法。 | `Kφ` 对观察等价的可达世界作全称量化；临时同步补足知识并减少通信已有先例。其主任务是保证违例可被知晓，不等同于每次动作必须安全。 |
| P3 | Carr, Jansen, Junges & Topcu, *Safe Reinforcement Learning via Shielding under Partial Observability*, AAAI 2023, DOI [10.1609/aaai.v37i12.26723](https://doi.org/10.1609/aaai.v37i12.26723)；[会议全文，9 页](https://ojs.aaai.org/index.php/AAAI/article/download/26723/26495) | 精读 §2–3.3，belief-support update、Def. 2、Theorems 1–4 及公平性/partial-model 限制。未审全部实验。 | support-based estimator 与 permissive action sets 已在 partial observation 下联合；安全支持不依赖精确概率。reach-avoid 的进展结论有公平性前提，不能偷换成所有世界、所有无限历史必达。 |
| P4 | Cimatti, Tian & Tonetta, *Assumption-based Runtime Verification*, DOI [10.1007/s10703-023-00416-z](https://doi.org/10.1007/s10703-023-00416-z)；[NuRV official documentation](https://es-static.fbk.eu/tools/nurv/documentation.html)；[NuRV 2.0.0 manual，42 页](https://es-static.fbk.eu/tools/nurv/manuals/nurv-manual_200.pdf) | 论文只读出版社摘要/元信息；PDF 链接重定向到摘要页，没有据此声称读到论文全文。手册精读 Ch. 1、Ch. 2 在线 heartbeat 例、§4.2 状态编码/API 与 §4.5/4.6 reset 接口的有关段落。 | 官方实现支持模型假设、在线输入、dynamic partial observability 中 `unknown / true / false` 以及 out-of-model verdict。reset 是其特定监控语义，不是任意证据依赖的免费精准失效算子；手册列明工具本身不做 instrumentation / active reaction。 |
| P5 | Mitsch & Platzer, *Verified Runtime Validation for Partially Observable Hybrid Systems*；[作者全文，26 页](https://arxiv.org/pdf/1811.06502) | 精读 §4–5 中控制/模型违例、sensor uncertainty 及相关 Theorems 1–4 的声明；核对 §6 monitor synthesis / quantifier elimination 段落。未独立核验 Appendix A/E 的完整证明。 | 有证明的模型监控、动作生效前的 fallback、部分可观测传感器误差已有 runtime assurance 路径。其存在性解释必须结合已证明不变量/误差条件；不能把“存在一个解释”直接当成本文所需全称动作安全。 |
| P6 | Cano Córdoba et al., *Safety Shielding under Delayed Observation*, ICAPS 2023；[作者全文，6 页](https://arxiv.org/pdf/2307.02164)；[作者 artifact](https://github.com/filipcano/safety-shields-delayed) | 精读 “Shielding under Delayed Inputs” 的 Steps 1–4、maximally-permissive 定义、延迟内存/复杂度段落；未运行 artifact。 | 有界延迟下仍按兼容潜在历史判断动作；须给定最坏延迟。预先允许动作集合与选择一个替换动作是不同阶段；干预启发式不证明支持生命周期总成本最优。 |
| P7 | Chen & Roşu, *Parametric Trace Slicing and Monitoring*, TACAS 2009, DOI [10.1007/978-3-642-00768-2_23](https://doi.org/10.1007/978-3-642-00768-2_23)；[出版社全文，16 页](https://link.springer.com/content/pdf/10.1007/978-3-642-00768-2_23.pdf) | 精读 §2 的 parametric event / slice、Algorithm A 的有关论证/Theorem 1 及 §3 的 monitor 定义和 online algorithm 引入。未逐项核验优化算法与实验。 | 带实体参数的事件分派与 instance-indexed monitor state 已有基础，基线不能假定每个事件必然重置全部实体。trace slicing 并不自动证明遗漏事件、权限或替代支持的原生语义。 |
| P8 | Cassez & Tripakis, *Fault Diagnosis with Dynamic Observers*；[作者全文，8 页](https://arxiv.org/pdf/1004.2810)；其引用的 Cassez, Tripakis & Altisen, *Synthesis of Optimal-Cost Dynamic Observers…*, TASE 2007, DOI [10.1109/TASE.2007.51](https://doi.org/10.1109/TASE.2007.51) | 精读 §II observer/diagnoser、§III Theorems 2–4、§IV 成本定义、Theorems 5–8。TASE 原文未取得全文，不单独以该原文作更强结论。 | 动态打开/关闭观察、最宽许可 observer 和 optimal-cost synthesis 已有明确结果；此文成本是最坏运行的长期平均观察代价，可使用一般 observer-state 权重。不是本文 retain+reacquire 的现成同目标复现。 |
| P9 | Grigore & Kiefer, *Selective Monitoring*, CONCUR 2018, DOI [10.4230/LIPIcs.CONCUR.2018.20](https://doi.org/10.4230/LIPIcs.CONCUR.2018.20)；[会议全文，16 页](https://drops.dagstuhl.de/storage/00lipics/lipics-vol118-concur2018/LIPIcs.CONCUR.2018.20/LIPIcs.CONCUR.2018.20.pdf)；[作者扩展全文，41 页](https://arxiv.org/pdf/1806.06143)；期刊版 DOI [10.1016/j.jcss.2020.09.003](https://doi.org/10.1016/j.jcss.2020.09.003) | 精读会议 §3–5 的 feasible policy、confusion、Theorems 14–15，以及扩展稿 §5 的 Theorems 27–28。未通读不可判定归约附录，也未读期刊版全文。 | 保持诊断能力的 selective observation 有真正优化结果；一般 hidden labelled MC 的期望成本阈值问题不可判定，non-hidden MC 可多项式计算 infimum，procrastination family（几乎）最优。不能将 infimum 无条件写成有限策略取得的最小值。 |

以上覆盖不是单篇论文已包含 OACR 全接口的主张。下面的组合编码是本审查的推导，不把它归给某个作者，也不把它当成新的理论。

## 3. 一个能覆盖完整生命周期的有限编码

### 3.1 原生状态、证据状态及允许信息

先固定公开、允许读取的有限关系模型 `M`。真实世界变量至少包括实体/alias mapping、native value、版本、权限、契约、原生读写关系及异常状态。维护器变量包含物理表示 `r`、缓存证据/派生摘要、`Γ`、依赖索引、来源 token 和历史压缩状态。事件、source query、`Retain / Drop / Rebind / Reprove / Materialize / Commit_a` 都是有前提、回执与转移关系的标签。

维护器不取得实际隐藏世界，只得到该标签规定的合法 observation。有限世界空间是从允许的模型枚举/符号化，不是通过私有数据库、gold 或 verifier 得到完整未来行为表。若模型尚不能从原生实现/允许说明构造，本编码仍只是规格级基线；模型提取、验证、编译、索引与储存一律计成本。

令 `T_ℓ(w,w')` 为标签的原生转移、`O_ℓ(w',o)` 为回执/事件的观察关系，则标准 belief 更新为

\[
 \widehat B=\{w':\exists w\in B\ T_\ell(w,w')\},\qquad
 B'=\{w'\in\widehat B:O_\ell(w',o)\}.
\]

未观测外部变更须用模型允许的 unobserved closure/prediction 纳入 `T`，不能令旧 fact 永久冻结。明确“不影响 x”的可靠 frame condition 才能运输旧 x。普通 TTL 不足以证明期间无权限撤销。若 `B'=∅`，输出 inconsistency/out-of-model 并阻止依赖该模型的 commit；不能借空集全称量化生成有效证书。

P1 的 `choose / observe / infer`、P2 的知识语义及 P4 的动态部分观察为这一构造提供直接近邻。用 BDD/SMT 表示 `B` 可保存世界间相关性；把各 fact 独立标 `?` 会丢掉这类信息，不能充当唯一最强基线。真正的 `Forget` 要把 epistemic state 抽象/放宽到仍保留的合法信息所支持的世界；若保留旧约束、proof node 或可重放历史以维持原来的 `B`，它们必须作为 retained representation 计费，重放也要计计算成本。

### 3.2 查询合法性与补 missing

每个来源请求 `q` 有 `Legal_q(w)`、明确身份/版本和可能结果 `y`。若发起未经授权的查询本身非法，应要求 `B ⊆ Legal_q` 后才能 dispatch。若接口允许合法发起且返回拒绝，则把拒绝作为独立结果；不得把拒绝当作免费取得被禁止内容。

对不改变世界的合法查询，`B_{q,y}=B∩O_q^{-1}(y)`；若有费用扣除、审计或其他副作用，使用完整 `T_q`。新证据绑定本次回执与来源 token，只在其规定有效范围中使用。查询也可以先确认 auth，再让下一查询成为合法，因此可行策略是自适应决策树，不必是静态“missing facts 的并集”。

`B ⊄ Ψ_a` 不推出一定存在修复查询。若两个兼容世界需要不同的合法动作/绑定，却在所有允许观测策略下不可区分，则当前信息权限下无可行 commit 保证。未找到某种证明语言的证书则只是搜索/表达失败，不能直接写成这种信息不可能性。

### 3.3 证书与 shield 的提交门

令

\[
 \Psi_a(w)=Binding_a(w)\land Guard_a(w)\land Auth_a(w)
 \land\forall w'\,[T_a(w,w')\Rightarrow Effect_a(w,w')].
\]

还要单独编码动作 enabledness、规定回执及任务要求，避免没有后继时的 vacuity。检查器接受 `Γ` 的条件是：证据均合法/有效、证明规则 sound、来源/实体/契约 token 与当前提交对象匹配，并证明 `B⇒Ψ_a`。符号检查等价于排除 `B∧¬Ψ_a` 的反例；产出可检查 proof object 的后端是另一个实现义务，不由一个 RV verdict 免费提供。

将 `commit_a ∧ ¬ValidCert_a` 和任何非法取证编码为 bad state，pre-action shield 只允许保持安全的动作。未来义务用 product monitor + winning-region fixpoint；只检查本次动作时可用上述 entailment 直接 gate。形式上的 `G(commit_a→ValidCert_a)` 只有在 shield 拦截点位于原生副作用之前时才是执行保证，事后 RV 报警不能撤回已发生的写入。

P3/P6 已覆盖 belief 下的动作许可；P5 覆盖有证明监控与 fallback 的链条。论文的模型与误差假设、概率零/公平性条件不能被省略。一般 API 的并发撤权或版本竞争，还需要 commit token/CAS/事务式快照等原生机制；没有相应机制时，一次事前检查不保证检查后仍有效。

### 3.4 替代证明与事件局部失效

义务可以表示为共享 AND/OR formula 或 proof DAG。保留所有允许替代，而不是只保存当前一条 justification。事件按 `(source,entity,version,permission,contract)` 键失效已受影响的 leaves；先验证仍有效的 branch，再对缺口求 entailment/reproof。当前 branch 的依赖闭包只是充分的局部检查范围；不是所有可能证明的最小语义影响范围。

甚至 `K(p∨q)` 可能成立而 `Kp∨Kq` 不成立：两个兼容世界分别满足 p、q 即可。P2 明确区分这两种知识要求。强基线应保留符号析取/相关性；若原生义务确实要求指出具体 witness，则另加 witness extraction 义务，不能混为一谈。

P7 支持将实体事件派给有关 monitor instances；P4 支持本次观察为 unknown，而不强迫全 trace 失忆。来源变更的精确 frame / invalidation adapter、proof-DAG 的局部 check 与缓存策略仍需实现及付费；这些文献没有自动给出任意 API 的依赖索引。

## 4. 最强 baseline 必须允许哪些动作

建议强对照为 **symbolic belief monitor + permissive certificate shield + adaptive costed sensing + dependency/proof reuse**。这是组合基线的描述，不是假称已经复现某一作者软件。它必须共享候选的合法输入、模型/证书语言、替代证明、索引、来源接口及全部成本，至少允许：

1. 运输未受影响证据与证明；事件仅影响单实体时保持其他 instance 状态。
2. 放弃当前 justification 后换用仍有效支持，或直接从当前符号 belief 重新证明；不先要求恢复原事实。
3. 保留额外物理支持或备用证书，并承担存储/维护费用；不得强迫 baseline 进行 canonical 删除。
4. 根据实际结果选择下一合法查询；auth/binding query 和内容 query 分开建模。
5. 对无法排除的坏世界阻止 native commit；保留规定的等待/abort/recovery 语义。
6. 将安全与进展分开验收；永远阻断所有动作不能以零查询“赢得”任务。

**可杀掉全刷新对照的小例。** 固定同一 binding/auth/effect 证据仍有效，guard 为 `u∨v`。初始同时有 u、v 的合法证据，当前证书选择 u。事件仅使 u 失效，可靠 frame 保证 v 未变。局部 alternative-aware baseline 用 v 换证即可提交，来源查询为 0；其检查/索引/证明改写成本仍计入。只追踪当前 Γ 然后刷新全部证据的对照会误报查询必要性。若 v 已真正遗忘，补查 v 才成为某些策略的选项。

“遗忘”不能仅删除原记录却免费保留 `B⇒v`、proof node 或 summary：任何仍能用于证书的记忆和生命周期元数据都属于 retain 成本。若摘要足以继续证明行为，baseline 也有权保留并计费。这个例子只是逻辑辨析，无新实验、自然现象或性能结果。

## 5. 能表达最小化与能高效求最小查询必须分开

### 5.1 有限合同中的精确规格级对照

设允许的 world model、证据/表示编码、查询结果字母表、生命周期 token 与策略记忆空间均有限；固定有界操作合同/阶段，令完整维护状态为 `z=(B,r,Γ,index,tokens,progress)`。可控动作包括 retain/drop、rebind/reprove、合法 query、native commit；不可控结果为模型允许的事件、回执和隐藏分支。每个 `u` 都有明确成本 `c(z,u)` 和 observation successors `Succ(z,u,o)`。

对有界最坏情况任务，可用有限 AND/OR backward dynamic programming：

\[
 V_k(z)=\min_{u\in U_{safe}(z)}\left[
 c(z,u)+\max_{o\in Out(z,u)}V_{k-1}(Succ(z,u,o))\right].
\]

边界只对已完成合法任务赋有限终值；超限但未完成、invalid certificate 或非法请求为 `+∞`。阶段计数/查询上限应明确包含内部操作，否则必须另解阶段内 shortest-path game，不能用零成本循环假装完成。若任务并非所有结果都能完成，报告 infeasible；不能以停止代替必须完成的 commit。

权重可固定为 `c_retain + c_maintain + c_reacquire + c_proof + c_compute`，或事先指定词典序/Pareto 目标；计量单位/权重未经规定时不存在唯一“最小总成本”。有公开、合法的概率先验时才用期望替代 `max`；POMDP belief support 足以讨论某些安全性质，不足以决定期望成本。上述程序可得有限域内精确强基线，但其状态可能包含 `2^{|W|}` 个 beliefs、全部证据子集/共享证书与策略记忆；“有限可解”绝不等于相对 native input 的多项式算法。

### 5.2 最小查询的局部规格也有独立难点

对冻结世界、固定动作且只计合法查询的单次 episode，正确 query strategy 的每个 commit leaf 都要满足 `B_leaf⊆Ψ_a`。静态最少 query set、实际结果分支上的最少次查询、事前最坏查询数及期望查询数是不同问题；retain/版本事件又改变下一 episode 的状态。把它写成 `missing=deps(current Γ)` 既遗漏替代证明，也忽视查询结果之间的相关性与合法性前提。

P8 已有 dynamic observers 和成本最优化，故“观察集合可动态选且有费用”不能单独成为新方法。P9 更直接提醒：一般 hidden MC 中，保持诊断能力并把期望观测成本压到阈值以下甚至不可判定；其 non-hidden 多项式结果只适用于每个观测标签识别状态的特定模型。这个不可判定结论不直接适用于 OACR 的有界、有限结果、最坏情况 API 合同，也不能当作本项目的下界证明。反过来，shield 的 minimum intervention / maximally permissive 也不是最小查询、最小 proof bytes 或最小 reacquire 总成本。

## 6. 本审查关闭什么、仍不能关闭什么

| 候选主张 | 当前审查判定 | 若要保留独立增量，需要的可审对象 |
|---|---|---|
| 所有 Compat 世界下保证未来动作 | epistemic / belief semantics 与 partial-observation shielding 有直接覆盖 | native relation/contract 的新结构，或在规定来源接口下严格更强的可证明保证 |
| 事件只失效一部分支持，换证明继续 | 强对照可用 AND/OR、符号相关性、参数化事件和现有 DAG 复用表达；全刷新只是弱控制 | 比相同 proof language + indexed reuse 更强的局部化构造/界；明确 source semantics |
| missing 时付费合法 sensing | 可编译为动态 observer / belief-game 动作；不能只比较固定刷新计划 | 同目标、同权限、同成本下的结构化查询算法、近似界或下界 |
| 每次 commit 均有 valid certificate | proof-checking gate + pre-action shield 可表达，但接口提取与 atomicity 仍需落实 | 一条可执行的原生保证链；不能仅保存一个 verdict 字段 |
| 联合 min retain + maintain + reacquire | 有限状态扩展可表达并作规格级精确规划；未发现本文阅读范围中现成同目标高效算法 | 成本耦合的可计算结构、可比强基线及相对输入规模的复杂度/实际代价 |

因此，**可先否定的是“该生命周期对象天然超出 monitoring/shielding”与“较全刷新省查询即独有算法”两种论证。** 不能仅凭有限状态可编码否定原生语义提取、特定结构算法、joint support/certificate optimization 或真实任务中的新现象。也不能把尚未取得的全文或未运行的软件算成已排除的强对照。

本轮只完成定向文献与规格级 encoding；未新增 benchmark、未读取 hidden evaluator 信息、未调用额外模型 API，未改变冻结文件或既有账本。下一轮若执行，应先冻结 native world/observation/permission/effect adapter 与完整成本，保留上述强基线及仓库通用 dependency-DAG 控制，再检验结构增量。当前没有全球无创新证明，也没有 T2/T5 或自然证据验收结论。
