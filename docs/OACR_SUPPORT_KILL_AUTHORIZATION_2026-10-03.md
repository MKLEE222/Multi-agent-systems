# Support-Lifecycle 冷启动近邻审查：授权、能力与线性资源

日期：2026-10-03。审查对象由当前任务给定，不改写冻结候选或既有结果。
本次只读取仓库文档和公开一手论文/官方标准；没有访问 benchmark gold、私有数据库，
没有额外模型 API 调用、跑新实验、改候选代码或冻结协议。

**判定：授权侧的宽泛概念主张基本被覆盖。** 证明携带授权、相关凭证发现、替代证明、
状态/时间条件、撤销、一次性凭证、证明依赖与补证均有直接近邻。
尤其 LPCFS (2011) 已把这些机制放进同一个可执行文件系统。
“部分状态兼容的全部世界中，动作产生满足后置条件的世界”亦有 Proof-Carrying Plans
(2020) 的明确语义与定理。不能将 PCA 单篇只保证准许访问的范围，误当成强组合基线
无法验证效果的证据。

这不证明任何 Support-Lifecycle 增量算法都无创新。当前可保留的是尚须精确陈述与
证明的窄问题：在相同合法观察/获取权限下，面向具体原生接口和生命周期变化，联合
选择保留证据、换证明、重查事实、重新授权的增量算法是否有新的正确性或完整成本
结果。组合词、字段更多、能表达对象、比冷重建省调用均不足以单独成立该结论。

## 1. 必须分开的三种对象

| 对象 | 支持内容 | 部分破坏后的含义 | 不能混同的结论 |
|---|---|---|---|
| 事实及其证据 | 路径目前指向实体 e；版本为 v；目标具备某属性；某时发生过确认 | 世界可能变了，也可能仅缓存证据丢失。丢失证据不推出事实为假；合法重查可能重建证据 | 签名认证“谁作了断言”，不会自动使断言成为当前客观事实 |
| 授权资源及其状态 | 谁可对何对象执行何请求；作用域、nonce、期限、可用次数；撤销 epoch | 撤销或消费可以消灭使用权，而历史确认记录仍为真。复制旧凭证字节不能复活资源 | 重新读取旧确认不能替代重新取得有效授权；逻辑中的可重复假设也不表示现实永不变化 |
| 动作效果契约 | 原生动作 a 的前置条件、绑定、成功/失败转换与承诺后置关系 | 授权有效但动作可能失败、部分写入、返回未知结果；须由动作模型或执行回执处理 | “获准执行”不推出“已经执行”“恰好一次成功”或“产生唯一精确结果” |

Garg et al. (2006) 明确区分 `A true` 与 `K affirms A`，并指出后一项不推出前一项。
它也分别设 unrestricted 与 linear 假设 [R1, §2]。因而上述区分不是本候选的新概念。
LPCFS 进一步明确分开线性使用、发行者撤销与时间过期 [R3, §2]。

例如，`Confirmed(user, request_hash, t0)` 可以一直是历史事实；
`Available(confirmation_id, request_hash, epoch, 1)` 是现时授权资源。
执行后前者保留，后者消费。这个例子是本审查的说明，不是论文实验。

线性逻辑通常要求选入线性上下文的资源恰用一次；affine 允许丢弃但禁止复制。
对“最多一次确认”，可以选用 affine 规则，或像 LPCFS 一样选择实际使用的线性
子上下文 Δ0，而不是要求库存全部消费。证明搜索中的一次使用限制还必须连接到
执行处的可靠消费机制；只有语法上的资源计数不能防止复制 proof 后重复执行。

## 2. 一手近邻的覆盖范围

以下表格是有边界的文献映射，不是声称已经复现各论文系统。

| 一手来源 | 已覆盖的最强相关能力 | 对当前候选不能免费补上的部分 |
|---|---|---|
| [R1] Linear Authorization and Knowledge, 2006 | truth/affirmation 分离、可消费与可重复凭证、资源敏感证明、cut elimination | 某个原生 API 的观察可信度、实体绑定和执行故障语义须另外建模 |
| [R2] PCFS, 2010 | 证明提前验证后发出条件能力；时间/系统状态条件留到访问时检查；自动 proof search；验证程序正确性定理 | 论文明确把 relevant credential finding 列为非目标；既有 filesystem 名称表示不自动解决任何 API 的稳定实体绑定 |
| [R3] LPCFS, 2011 | 同一系统内处理 use-once、revocable、persistent 凭证；linearity-aware backchaining；procap 携带依赖凭证 ID；访问处检查条件及原子消费 | 不声称最优补证/最优联合存储算法；其消费事务与底层 I/O 成功仍有崩溃窗口 |
| [R4] Consumable Credentials, 2007 | 分布式 ratifier 跟踪可消费凭证；请求绑定 nonce；bounded use 与消费原子性要求 | 不直接提供一般的原生动作 exact-effect/跨服务事务提交定理 |
| [R5] Distributed Credential Chain Discovery, 2003 | RT0 credential graph；目标驱动、按需分布式检索；在相应 traversability/storage typing 条件下给出 soundness/completeness | 不能将证明相对已取回图成立升级为无条件拥有全部隐藏凭证；不提供当前四类义务的最优联合维护 |
| [R6] Abductive Credential Gathering, 2009 | constrained Datalog 的 tabled abduction；本地计算完整 missing-credential specification；随后合法获取 | hypothetical missing credential 不是现成凭证；须真的从 provider 得到。没有据此断言一般最小成本生命周期策略 |
| [R7] Weighted Credentials, 2012 | weighted Datalog/RT 与 soft-constraint deduction/abduction；权重可表示 cost；公开原文片段使用 min-plus weighted semiring | 全文抓取未成功，仅据原文摘要及可检索片段判断；不借此声称共享证据、消费资源、在线观测策略的完整最优定理 |
| [R8] Quantitative Proofs of Authorization, 2010 | 明确定义 inclusion-minimal proofs 与 relevant credentials；多替代证明、proof overlap/short-chain robustness 和组合评分 | robustness score 不等于概率校准、不等于最坏情况全世界保证，也不等于补取成本最小 |
| [R9] Proof-Carrying Plans, 2020 | 部分状态对应一组兼容 worlds；资源/前后置逻辑；对任意兼容 world 和 well-formed handler 的 evaluation soundness | 标准符号动作模型不自动是真实 API 的实现精化；证明后置关系也不自动是完整输出/全部状态的唯一精确值 |
| [R10] OAuth 官方 RFC | 当前 active-state introspection、细粒度请求范围、proof-of-possession/request binding/replay 机制 | 生命周期检查、请求绑定与执行效果保证仍是不同机制；标准自身给出缓存撤销滞后窗口和 DPoP 的消息覆盖范围 |

最直接的单系统 baseline 是 **LPCFS**，不是只有静态 ACL 或证书签名校验的弱版本。
其 §4 的实际路径是 `policy → proof → procap → file access`：检查证明和签名后，
procap 记录 principal/file/permission、time/state 条件及 persistent/linear 依赖列表。
reference monitor 对撤销与未消费条件做事务检查，然后标记 linear 凭证已使用。
其前端允许外部 heuristics/provers，不能把它限成每一步从头搜索。
同一节也坦承，标记消费之后、访问之前崩溃可能导致“已消费而未访问”，靠日志和
管理员恢复 [R3, §4]。所以这里有强生命周期实现，但不能读成 exactly-once I/O。

PCFS 的 Theorem V.1 证明“两阶段检查”等同于直接证明授权的相应逻辑保证。
其 Theorem III.1 已有 proof substitution [R2]。替代证明和证书代换须与这些机制
直接比较，不能因为论文没有使用 Support-Lifecycle 的名称就宣布概念空白。

## 3. 具体 reduction：强组合基线如何覆盖候选对象

本节是本审查构造的组合基线与条件归约，不冒充某一论文已给出的端到端系统。

令合法观察历史为 I，`Compat(I)` 包含全部满足公开动作模型、合法观察和明确
环境变化契约的世界。对具体请求 a，固定：

- `G_a(w)`：guard；`B_a(w, β)`：参数/名称绑定到目标 β 及其版本。
- `A_a(w, D)`：在现时 ledger/epoch 中，凭证集合 D 足以授权此请求。
- `T_a(w, o, w')`：原生动作的完整转换关系，含允许的失败结果 o。
- `R_a(w, o, w')`：所承诺的效果关系。

要求证书成立的语义可以写成

\[
\forall w\in Compat(I):\quad
G_a(w)\land B_a(w,\beta)\land A_a(w,D)
\land\forall o,w'\,[T_a(w,o,w')\Rightarrow R_a(w,o,w')].
\]

这里量化全部允许转换，不能只量化成功返回；若需要必成功、终止或恰好一次，
须再写出相应 liveness/termination/commit 条件。没有允许转换时不能凭 vacuity
把“可执行且成功”当作已证。

**映射。** 用 φI 表示这些合法观察所定义的可能世界集合；未观察的属性仍自由，
不采用“未出现即假”。将 `G_a ∧ B_a ∧ WP_R(a)` 作为事实/动作层的证明目标；
将 `Authorized(principal, request_hash, β, epoch)` 作为线性授权层的目标。
证书是一对可检查 proof 加它们的依赖 DAG，而非一个布尔 allow 位。

| Support-Lifecycle 项 | 强组合 baseline 中的具体对象/操作 |
|---|---|
| support certificate | φI 蕴涵 guard/binding/效果弱前置条件的证明，加 Γ;Δ 下的资源敏感授权证明 |
| alternative supports | 同一证明目标的多 derivations；共享 persistent 子证明的 DAG；linear 叶的 occurrence/resource ID 保持计数 |
| legal observation | 带 provenance、版本与可得性条件的输入规则；不把 provider 有凭证当成已经观察到凭证 |
| expired/stale fact | 删除或弱化相应现时假设，沿依赖索引重检；未受影响子证明可复用 |
| consumed/revoked confirmation | ledger transition 删除现时可用资源或改变 revocation epoch；历史事实可留；旧 proof/capability 若依赖该资源则不可直接重放 |
| proof switch | 在同一当前 φI、ledger、request scope 下选择另一 derivation；检查资源分配，而不是复活旧资源 |
| minimum legal reacquire | 以获取/renew/reconfirm 操作为 abducibles，加入其合法前置和资源转换，求使整个目标可证明的最小成本方案 |

**条件归约命题。** 若 (i) φI 精确表示 Compat(I)，(ii) 观察规则在这组世界上可靠，
(iii) 公开动作转换模型 T 精确表示原生实现，(iv) 授权
证明系统对当前 ledger 的资源语义 sound，(v) 所需证明 fragment 完备且获取动作
模型/成本相同，则上述组合 baseline 对同一请求的接受与所定义 support validity
等价。证明只是各层 soundness/completeness 与合取：事实层排除 guard/binding/WP
反例；资源层给出 scope 正确的授权及 resource accounting；动作层使用其契约。
若只满足 soundness，只有“接受 ⇒ support valid”，不能声称拒绝即不存在证书。
特别地，若 T 只是原生实现的 sound over-approximation，对其全部转换验证 R 可给
上述安全方向，但可能因额外伪转换拒绝本来可行的动作，不能据此声称接受等价。

这个命题明确了归约条件，不声称任意原生系统都已有精确 φI、可判定完整逻辑或
免费译码。Proof-Carrying Plans §3.1–3.2，Definitions 5–6 与 Theorems 11–12，
已有“部分状态兼容多个世界 + 对所有 well-formed worlds 的 postcondition”基础
[R9]。因此单单加入 `∀w∈Compat(I)` 不会绕过这一类近邻。

若支持的“effect”仅为 `w' satisfies permitted_write_scope`、不破坏 invariant，
它是 **safety relation**；若支持的是“返回某唯一 JSON、恰好删除这一个实体，
没有其他写入”，则需足够细的 T/R 与 frame/error/observability 契约。
后者可能比前者严格，但这属于承诺精度和实现精化问题，不是凭授权证书自然得到的
知识；也不是换一个 effect 字段便能建立的新定理。

## 4. 最小 legal reacquire 的严格边界

在有限正向规则、明确可获取凭证、已知非负获取成本下，令 E 为仍可用证据，
P_a 为同一当前上下文下所有有效 proof 的支持集合族。把 consumed/revoked 叶排除
后，一个静态版本的补证问题是

\[
\min_{X\subseteq Q}\ c(X)\quad
\text{s.t.}\ \exists S\in P_a:\ S\subseteq E\cup Obs(X),\quad Legal_I(X).
\]

这是 constrained/weighted abduction 与 evidence selection 的直接表述 [R6–R7]。
R8 的 minimal 是“没有正确的真子集”，不是该式的 globally minimum cost。
称为“最小补证”必须声明 cardinality、钱/调用数、最坏情况/期望还是完整维护成本。

该式固定一个必须支持/完成的目标请求 a；它不能替换任务的 completion obligation。
若优化仅要求“每次 commit 有有效证书”，而允许永不 commit，则零 commit、成本 0
是退化可行解。端到端比较须同时固定 official success/任务目标、允许 blocked 的
条件，以及在合法可完成环境下的进展或完成要求。安全证书维持正确不能代替完成
用户任务；授权确已丧失且无法重获时，安全拒绝可以正确但仍不等于任务成功。

同样，纯查询至多取得 `revoked/consumed` 的当前证据；它不能填回已经消失的
entitlement。恢复只能来自允许的 renew/reconfirm/new-grant 等改变世界或资源状态
的动作。若只允许 read，这类 hole 的最小“查询补齐”成本不是有限值，而应判定
没有可行恢复路径；不能把确认 receipt 的回查当成新 authorization。

强 baseline 允许记录替代 proofs、memoization、provider 索引、请求合并、缓存、
局部失效和合法 provider 接口。有限候选空间可用精确约束优化作 oracle/control，
不需要贬低成逐世界枚举或每次全重建；复杂性较高不等于原则上不能构建对照。
R6 本来就利用 tabled abduction/memoization，R5 本来就目标驱动按需获取。

有四个不能被一句 min-plus 自动解决的细节：

1. **共享成本。** 同一 persistent evidence 被多条目标引用，获取与保留只计实际
   一次；按 proof tree 每个叶收费会重复计算。已消费 linear resource 不能因 DAG
   共享而多用。可为来源动作与 proof occurrence 分别引入变量/约束。
2. **合法获取不等于补齐字面值。** 对 revoked grant，旧字节的重新下载不是 renew；
   需 issuer 允许并实际发行新 ID/epoch。可能根本不存在合法 reacquire；输出
   blocked/need-authorization 是正确结果，不能假设 provider 必答 yes。
3. **获取有状态和结果。** provider 查询可能拒绝、返回部分信息；confirmation
   可能产生新资源，查状态可能只缩小 Compat(I)。此时 X 是有序合法动作或适应性
   策略，不是无序 missing-atom 集。其精确最优对照应使用相同观测分支与信念/资源
   状态，不能提前知道未来回答。
4. **完整成本。** 应包括 retained raw evidence、proof DAG、dependency index、
   ledger/version metadata、checker/search work、source/renew 交互与冷初始化。
   不仅比较补取次数。压缩 physical representation 和保持更多现成 supports 可能
   有不同的全成本最优解。

这些是对已有对象的精化条件与有待测量的算法问题，不在本审查中宣布为新结果。
静态 weighted abduction 不能直接据此获得一般在线最优策略；反过来，“动态”也
不能直接否定可用状态化、增量化的经典组合对照。

## 5. Future、撤销与执行边界

“future action 有证书”有两种不同的有效性：现在已知道一个当时可授权的请求，
或在未来真正执行时仍保证有效。如果 Compat(I) 允许未观测的任意撤销/外部写入，
旧观察无法保证后一种结论。应明确采用 lease/版本锁/原子 validation-and-use、
受控变化契约，或到执行边界重建证据；这是所有方法共同的信息限制。

能力不是永久事实。PCFS/LPCFS 的条件能力正是把变化条件留到使用时检查 [R2–R3]。
RFC 7662 §4 也明确 token introspection 缓存会造成撤销后的继续使用窗口；短缓存与
负载存在权衡 [R10a]。缓存 freshness 只能在声明的时间/环境边界内有保证。

请求绑定也应精确。RFC 9396 §2 的 authorization_details 可表达 action/resource 与
参数范围 [R10b]。RFC 9449 §4.2–4.3 的 DPoP 包含 method、target URI、时间、jti，
并明确基础设计只覆盖 method 与 URI；不能将其自动读成整个 body、query 和预期
effect 都已经签入 [R10c]。作用域差额需要明确加绑定规则，而非笼统声称 capability
没有绑定能力。

LPCFS 的消费事务不是“消费 + 底层动作 effect”完整事务。若候选把可用凭证与
外部 side effect 绑在 exactly-once promise 上，必须证明 commit/crash/retry 语义；
仅有合法 proof search 与最后一刻 revocation check 仍不能完成这一证明。

## 6. 仍可能成立的贡献：严格 remaining condition

当前证据支持把 **concept priority claim** 收窄；不支持宣判全部算法可能性为空。
至少以下一种条件实际成立，才能继续以独立贡献推进：

**理论差额。** 给出固定原生 semantics、可用 source/acquisition interface、允许生命周期
变化及 proof language。在相同信息条件下，证明一个不是直接 soundness/cut/Hoare
composition/weighted abduction 改名的结果，例如联合表示—proof—资源—reacquire
优化的可分解条件、不可分解反例、复杂度/下界，或可检查的局部更新充分必要条件。
需明确哪些现有定理被使用、哪一步超出它们，而不是只列四类 obligation。

**算法差额。** 实现一个具体增量算子，对合法变化更新 φI、资源 ledger、binding 与
proof DAG，在 checker 保持同一承诺后置关系的条件下，有新的维护工作/查询/全成本
界，或者共同任务上的可靠改进。归约能表达对象并不否定这种增量贡献；但必须与
下面的强组合控制竞争：

> 完整合法观察日志与 scope/version provenance + conditional-capability/reference
> monitor + linear/affine resource ledger + alternative proof DAG/dependency index +
> constrained weighted abduction + 原生 action-contract checker。

这是本审查建议构建的 control，不称其为已经运行的 LPCFS/PCP 外部复现。允许与
候选相同的预处理、缓存、局部更新、原始证据回查和获取动作；全部计费。

**原生语义差额。** 如果贡献在 binding、失败转换、未观测外部变化或 exact effect，
先证明 source observations 与 action handler 对真实接口的 sound refinement，给出
无法保证时的 blocked/recheck 行为。模型声明中的 effect 应与 evaluator 承诺同精度。
如果最终只验证安全关系，不能写成精确效果保证；若精确输出需额外观察，要计费。

**自然现象差额。** 在独立自然任务中，固定日志/证据/版本/权限/确认来源，实际出现
“事实依旧成立而使用权已消失”“支持消失但另一个合法 proof 仍成立”或“重获事实与
重新授权成本不同”等可重复干预效应。它们作为一般概念早有先例；新现象须是具体
领域的可信识别、边界与后果，不能由人工确认 token fixture 单独提升为首创。

只有“单篇没有所有词”不是 remaining condition；只有“公知组件组合后可表达”也
不是 algorithm impossibility proof。没有达到上述条件时，本候选宜定位为成熟语义
维护思想在具体原生接口上的整合/适配成果，保留已完成工作但不申报独有总机制。

## 7. 引用、已核查范围与访问限制

页码均为 PDF 从 1 起的物理页码；仅引用列明范围，未声称文献穷尽。
各条的内容概要限于此次实际核查，正文归约/反例/控制方案明确为本审查推导。

- **R1.** Deepak Garg, Lujo Bauer, Kevin D. Bowers, Frank Pfenning, Michael K. Reiter,
  *A Linear Logic of Authorization and Knowledge*, ESORICS 2006。
  [作者 PDF](https://www.cs.cmu.edu/~fp/papers/esorics06.pdf)。核查：摘要、§2 pp.2–3
  的 truth/affirmation、linear/unrestricted judgments；不据其逻辑表达能力声称现成
  原生 action refinement 或最优维护算法。
- **R2.** Deepak Garg, Frank Pfenning, *A Proof-Carrying File System*, IEEE S&P 2010。
  [作者 PDF](https://people.mpi-sws.org/~dg/papers/oakland10.pdf)。核查：§I pp.1–2
  的 dynamic authorization/non-goals；§II–III pp.3–7；Theorem III.1；§V 的
  proof search/conditional verification 及 Theorem V.1 pp.9–11。
- **R3.** Jamie Morgenstern, Deepak Garg, Frank Pfenning, *A Proof-Carrying File
  System with Revocable and Use-Once Certificates*, STM 2011。
  [作者 PDF](https://people.mpi-sws.org/~dg/papers/stm11-lpcfs.pdf)。核查：§1–2
  pp.1–6；§3 的 Γ/Δ、tensor split、cut pp.7–9；§4 pp.10–12 的搜索、procap
  dependencies、exclusive transaction、消费后访问前的 failure/recovery 说明。
- **R4.** Kevin D. Bowers et al., *Consumable Credentials in Logic-Based
  Access-Control Systems*, NDSS 2007。
  [作者 PDF](https://www.cs.cmu.edu/~fp/papers/ndss07.pdf)。核查：pp.2–5 的 ratifier、
  `action(action,parameters,nonce)`、Bounded Use 与 Atomicity 定义；不把分布式凭证
  消费协议等同一般外部 effect commit。
- **R5.** Ninghui Li, William H. Winsborough, John C. Mitchell, *Distributed Credential
  Chain Discovery in Trust Management*, JCS 11(1):35–86, 2003。
  [作者论文页](https://crypto.stanford.edu/~ninghui/abstracts/discovery_jcs03.html)，
  [作者 PDF](https://crypto.stanford.edu/~ninghui/papers/discovery_jcs03.pdf)。核查论文页
  的具体 sound/complete/traversability 条件与 PDF 元信息；本审查未全文逐证明复核。
- **R6.** Moritz Y. Becker, Jason F. Mackay, Blair Dillaway, *Abductive Authorization
  Credential Gathering*, POLICY 2009。
  [微软研究院原文](https://www.microsoft.com/en-us/research/wp-content/uploads/2009/07/becker2009ieee-policy-submission.pdf)。
  核查：摘要、§1 pp.1–2 的 pull/push 成本与可得性；§3 pp.2–3 的 constrained
  tabled abduction、missing-assertion sets。全文相应扩展：
  [MSR–TR–2009–19](https://www.microsoft.com/en-us/research/wp-content/uploads/2009/02/becker2009credentialTR.pdf)。
- **R7.** Stefano Bistarelli, Fabio Martinelli, Francesco Santini, *A semiring-based
  framework for the deduction/abduction reasoning in access control with weighted
  credentials*, Computers & Mathematics with Applications 64(4):447–462, 2012。
  [原期刊页面](https://www.sciencedirect.com/science/article/pii/S0898122111010728)，
  DOI [10.1016/j.camwa.2011.12.017](https://doi.org/10.1016/j.camwa.2011.12.017)，
  [作者存档版本](https://inria.hal.science/hal-00662587/file/rtmljournal.pdf)。
  本次全文 open 被阻；实际核查仅原期刊摘要/检索到的原文片段（weighted semiring、
  monetary credential cost、abduction），不提供未读取的 theorem/section 优先权结论。
- **R8.** Adam J. Lee, Ting Yu, *Towards Quantitative Analysis of Proofs of
  Authorization: Applications, Framework, and Techniques*, CSF 2010。
  [作者 PDF](https://people.cs.pitt.edu/~adamlee/pubs/2010/lee2010csf.pdf)。核查：
  Definitions 4–5 p.5；pp.8–9 的 minimal-proof family、ωlen/ωind、Eq.6–9。
  一次直接 HTTPS open 报错，随后经 HTTP 地址成功读到相同 HTTPS PDF；未据此
  声称该评分是 cost-minimization。
- **R9.** Alasdair Hill, Ekaterina Komendantskaya, Ronald P. A. Petrick,
  *Proof-Carrying Plans: a Resource Logic for AI Planning*, PPDP 2020。
  [作者 arXiv v2 PDF](https://arxiv.org/pdf/2008.04165)，
  DOI [10.1145/3414080.3414094](https://doi.org/10.1145/3414080.3414094)。核查：
  摘要；§3.1–3.2 pp.7–8 的 compatible well-formed worlds、Definitions 5–6、
  Theorems 9/11/12。此 soundness 以 well-formed handler 为条件。
- **R10a.** [RFC 7662](https://datatracker.ietf.org/doc/html/rfc7662)，§2 的 active-state
  introspection，§4 的 security tradeoff/撤销后缓存有效窗口。
  **R10b.** [RFC 9396](https://datatracker.ietf.org/doc/html/rfc9396)，§2 的
  authorization_details/action/resource fields。
  **R10c.** [RFC 9449](https://datatracker.ietf.org/doc/html/rfc9449)，§4.2–4.3 的
  htm/htu/iat/jti/ath、基本 DPoP 所覆盖的请求部分及 replay 校验。

最终状态：概念组合 kill 很强；对具体增量算法的全面 kill 尚无证据。严格的下一步
是固定上述 remaining condition 的一个窄对象及可执行强控制，不能直接重跑旧开发
例子后把经典 capability/proof/resource maintenance 包装成独有 Support-Lifecycle。
