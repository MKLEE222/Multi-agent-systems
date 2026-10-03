# Support-Lifecycle cold kill：epistemic / contingent / partially observable planning

日期：2026-10-03。范围：只审当前候选的 planning 邻域；不运行额外模型 API、benchmark、私有任务、gold 或新的开发检查，不改冻结协议、代码或结果。仓库依据为已有 operator-first、joint-certificate 和 joint-operator-question 文档。

**判定：候选的宽泛机制主张被成熟 planning 框架覆盖；具体高效算法的新颖性仍须单独审。** “合法取得的信息足以确认动作前提，缺口通过有代价的 observation 补齐，按 observation 分支，之后才能 commit”不是新框架。“失效后切换证据组，而非全量刷新”也不能避开最强 planning 对照。另一方面，没有读到一篇论文已经在真实工具接口上，完整实现并最优求解实体绑定、证书负载、权限撤销、一次性确认、时效、retain/maintain/reacquire 全成本；不能将一个有限状态 reduction 冒充该完整实证结果。

最强可构建基线是：**原生合法事件模型 + 实际保留状态 + 同信息策略约束 + strong bounded-reachability 合成 + 成本预算约束**。工程规模基线再加增量证明/依赖维护、结构化 belief tracking、按需 sensing 与局部 replanning。全量 refresh 只能保留为成本上界控制，不能代表经典方法。

## 1. 一手来源与实际阅读边界

以下都是作者、会议、出版社或官方服务来源。没有使用综述、博客或二手文献作为关键技术证据。PDF 可得不等于全文逐页读完；本轮阅读程度如下。

| 编号 | 一手来源与定位 | 本轮实际核读 | 精确覆盖与限制 |
|---|---|---|---|
| P1 | Bonet & Geffner, *Planning with Incomplete Information as Heuristic Search in Belief Space*, AIPS 2000, pp.52–61。[AAAI PDF](https://cdn.aaai.org/AIPS/2000/AIPS00-006.pdf) | 数学模型、contingent/probabilistic 模型、Bellman/RTDP 部分及结论限制；未逐项复核全部实验 | Eq.1–5 的 belief progression/filtering、Eq.2 的全世界 action applicability、Eq.6–7 的最坏成本优化；不同 action costs 与 epistemic goals。RTDP 的最优性是有限 belief space 的渐近性质，不能据此声称有限运行已最优。 |
| P2 | Petrick & Bacchus, *A Knowledge-Based Approach to Planning with Incomplete Information and Sensing*, AIPS 2002。[作者 PDF](https://www.cs.toronto.edu/~fbacchus/Papers/PBAIPS2002.pdf) | knowledge semantics、四数据库、更新、Table 2 PlanPKS 与 plan correctness；未逐项复核全部实验 | K 的全世界语义，知识前提，Kw/Kv 与 runtime sensing 分支。数据库 inference 是 sound but incomplete；不能当一般完整或成本最优解法。 |
| P3 | Petrick & Bacchus, *Extending the Knowledge-Based Approach to Planning with Incomplete Information and Sensing*, ICAPS 2004。[作者 PDF](https://www.cs.toronto.edu/~fbacchus/Papers/PetrickBacchusICAPS2004.pdf) | PKS 回顾、postdiction 假设、numeric evaluation、UNIX Table 3–4 与结论；未逐项复核全部例子 | 已实现 numeric resources、temporal restore 和 permission-sensing 的 UNIX 模型。数值表达式需 plan time 可求值；inference 不完整；postdiction 的 world-change 假设须检查并发。 |
| P4 | Pandey & Rintanen, *Planning for Partial Observability by SAT and Graph Constraints*, ICAPS 2018, pp.190–198。[会议 PDF](https://cdn.aaai.org/ojs/13896/13896-40-17414-1-2-20201228.pdf) | plan-class 定义、Def.1–4、SAT/graph encoding、实验范围、future work；未逐页重做所有证明与实验 | 任意有限 transition system、bounded-memory policy、execution graph、strong bounded reachability 与公平 strong-cyclic 类。其论文不提供本文所需全部成本优化；MILP/SMT numeric reward optimization 出现在 future work，不能写成已完成能力。 |
| P5 | Bonet & Geffner, *Causal Belief Decomposition for Planning with Sensing: Completeness Results and Practical Approximation*, IJCAI 2013, pp.2275–2281。[作者 PDF](https://bonetblai.github.io/reports/IJCAI13-tracking.pdf) | relevance/projection、Theorem 8/16/18、CBT 与 beam tracking；未读完整长版证明或重跑实验 | 非全量 belief tracking 的成熟结构化基线。CBT 始终 sound、在 causally decomposable 条件下 complete；beam tracking sound but incomplete。不是通用局部复杂度保证。 |
| P6 | Muise, Belle & McIlraith, *Computing Contingent Plans via Fully Observable Non-Deterministic Planning*, AAAI 2014。[会议全文](https://ojs.aaai.org/index.php/AAAI/article/view/9049/8908) | introduction、simple PPOS 定义、K' compilation、sensing 选择与 policy/DAG 部分；未逐项复核全部实验 | PO-PRP 允许按需选择 sensing，并以 partial-state policy/DAG 降冗余；原文假设 uncertainty monotonically decreases，不能直接覆盖失效后再次 unknown。 |
| P7 | Levesque, *What Is Planning in the Presence of Sensing?*, AAAI 1996, pp.1139–1146。[会议 PDF](https://cdn.aaai.org/AAAI/1996/AAAI96-169.pdf) | 合法动作、sensing 规格、机器人程序及机场 knowledge-precondition 例；未逐项重做全证明 | 计划须在运行时知道怎样执行；知识前提与 sensing 不是当前候选新提出的约束。此来源不是成本最优 maintenance 系统。 |
| P8 | Bertoli et al., *Strong Planning under Partial Observability*, Artificial Intelligence 170, 2006, pp.337–384。[出版社条目](https://www.sciencedirect.com/science/article/pii/S0004370206000075)；DOI 10.1016/j.artint.2006.01.004 | **仅出版社摘要；全文本轮未成功取得** | 摘要明确 AND/OR belief-space search、termination/correctness/completeness 与 symbolic BDD。本文不凭摘要归因其全部具体算法、成本功能或生命周期支持。 |

P3 是重要的“不是仅靠通用可表达性”近邻：其 Table 4 实际把 cp 的 permission 前提写成 K(exec(d))，以 ls 获取 permission 信息，再按结果 copy 或 chmod/copy/restore；另有 cp+ 回执用于 postdiction。它是作者实现中的模型化 UNIX 任务，**不是本轮执行真实 shell，也不证明完整 UNIX 权限语义或现实并发已覆盖**。

## 2. 先统一 guarantee，避免把弱解与候选强保证比较

候选为 native action a 维护合法证书 Γ，要求

\[
I,\Gamma\ \Longrightarrow\
\forall x\in\operatorname{Compat}(I):\Psi(x,a).
\]

令 Ψ 分别指明 binding、guard、authorization 与 effect。若 effect 有 nondeterministic outcome，还须明确量化所有合法后继，不能只量化前态。知识表达 KΨ 的语义正是 Ψ 在所有可行世界成立；P1 的 Eq.2 已将安全动作定义为

\[
A(b)=\bigcap_{x\in b} A(x).
\]

这覆盖“动作前提在所有 compatible states 都满足”的语义骨架。[P1,P2]

| 解的类型 | 保证 | 在本候选对照中的用途 |
|---|---|---|
| Weak / optimistic | 某条可行结果路径成功，或在假设世界上成功 | 可比较效率与恢复，但不能独自承接逐动作全称保证；须加共同 commit gate。 |
| Strong | 所有允许初态与所有允许结果分支都合法，并在有界步骤内达到目标 | 与有限 horizon 的候选任务完成保证直接对齐。[P4] |
| Strong cyclic | 所有分支留在可达目标区域，最终达标依赖 outcome fairness；步骤数无统一界 | 只有候选也接受同一 fairness 时才公平；若 sensing 可永久拒绝/过期，不能假定迟早成功。[P4] |
| Probabilistic expected-cost / almost-sure | 优化期望成本或概率 1 到达 | 与对所有世界/轨迹的保证不同；不通过高平均成功率替换 permission/guard 硬约束。[P1,P4] |
| 每次 commit 的安全性 | 提交前证据合法且保证动作不会发生被禁止的效果 | 本身不保证任务完成；永远拒绝提交可满足安全性，故成功率/覆盖率必须另报。 |

还需区分：API 原子 guard 可以保证“若版本不匹配则拒绝、不会错误写入”，不等于保证“这次写入一定成功”。两方法若都可能遭遇合法 concurrent change，就应共同允许正确拒绝/重试，或共同满足同样的稳定性/租约假设。

## 3. 生命周期义务怎样编进一个 planning 模型

下面是本轮提出的具体适配 reduction，不声称 P1–P8 任一论文已原样实现全部字段。

先固定有限 native model。实际世界 x 与实际 retained controller state z 分开：

\[
z=(r,\Gamma,\operatorname{index},\operatorname{tokens},
\operatorname{budget},\operatorname{phase},a_{\rm pending}).
\]

记录 r 的每条 evidence 至少保存原生实体绑定、source、作用域、版本/epoch、取得途径、适用权限、时效，以及仍可使用的次数；只包含该任务接口实际提供的字段。没有公开 stable ID 时不发明一个。证书/索引/版本标签/预算计数器都是真实存储，均计费用。

| 义务 | Native/model 状态 | Observation / maintenance / commit 编码 |
|---|---|---|
| Binding | 实体 ID 或合法路径解释、对象版本、作用域 | 记录必须绑定当前动作参数；rename/rebind 按实际事件模型更新，不以字符串等于对象身份。 |
| Permission | 当前 rights/capability 与 provenance | Acquire_q 自己也有权限前提；感知成功不能自行产生写权限。revocation 是状态转移，旧证据可能失效。 |
| Resource | quota、remaining budget、实际可使用资源 | Acquire/maintain/native commit 消耗对应资源；补取可因预算/权限失败，拒绝是一个合法 observation 分支。 |
| Consumed confirmation | 与动作/参数/版本绑定的未消费 token | 成功使用后 token→consumed；复制证明或重新读取旧确认文本不使其复活。是否失败调用也消费须由 native contract 决定。 |
| Freshness | 记录版本、expiry、当前合法时钟/epoch | expires/change 事件使 validity 变 false 或当前值变 unknown；是否发生变化不得由隐藏真相免费告知。 |
| Predicted effect | 原生 transition relation 与结果类型 | Guarded commit 的前提必须同时保证所有允许后继的承诺效果，或明确只保证拒绝时无非法效果。 |
| Alternative supports | 可检查的 Γ₁,…,Γ_k 及其记录 dependencies | commit 可选择任一当前有效证据组；reprove/rebind 是带费用的动作，不强制取回失效的原记录。 |

每个 Acquire_q 都是一个有前提、费用和 observation partition 的 native action：可能返回 true/false/unknown/denied/version-change。Retain、Drop、Reprove、Materialize、Commit 也有各自读写与费用。把外部变化合入原生 transition relation，不把“只有维护器动作会改变世界”偷偷当成真实 API 属性。

须分别建模 canAttempt(q) 与实际 source read permission：有些接口允许提出请求但返回 denied；有些任务政策直接禁止无权尝试。前者把 denied 作为结果分支，后者要求 canAttempt 在全部 compatible worlds 成立。不能为了保证而删除实际存在的拒绝分支。若公开模型允许自上次回执后发生未观察的版本/撤权变化，记录的 current-validity 必须为 unknown，不能让 stored-valid bit 免费读取隐藏事件。

逻辑真值和可使用证据是不同 fluent：K(auth) 不等于 possession(valid-capability)；K(approved) 不等于拥有未消费且适用于当前参数的确认。Γ 是可核验的推导或可使用 token 组合，不是免费添加“正确”标签。若行为替代不足以满足 provenance 义务，planner 同样不得用替代证明冒充原证据。

Alternative support 的两种语义亦须区分：

\[
K(P\lor Q)\not\equiv KP\lor KQ.
\]

通用 belief inference 可能直接确认 Ψ，但特定证书语言可能要求显式选择一个 support group。公平基线应提供同样的证书语言/构造器；“planner 知道 Ψ”不能免费代替真实 Γ 生产、保存和检查。相反，只测试单份旧 Γ 的 dependencies 会削弱经典基线，因为它必须允许其他已有合法支持重新证明 Ψ。

## 4. 一个处理保留与遗忘的严格 reduction

**不能让经典 planner 免费使用已经 Drop 的 observations。** 普通 perfect-recall belief 状态 b(history) 保留全部历史的逻辑信息，若候选只保留 z，直接以普通 belief planner 比成本可能比较不同的信息接口。

采用 P4 的有限 partially observable transition-system 形式，构造：

\[
S=X\times Z_{\rm legal}\times B,\qquad
\operatorname{Obs}(x,z,b)=\operatorname{Visible}(z).
\]

B 为用于成本约束的剩余预算计数；只有真实维护器保留了预算 tracker，才把相应值给 Obs。原生模型中的合法 hidden world 只在 X，绝不直接给 actor 或策略。pending source reply 在 observation phase 可见；离开该 phase 后，只有实际保留的部分进入 z，其余不可回查。

动作集合包含以上真实可行 maintenance/native actions，转移

\[
(x,z,b)\xrightarrow{u}(x',z',b-c)
\]

必须由原生读写/回执语义与已声明 memory mutation 得到。Reprove 只能读取 z 中合法支持，不能修改 memory state 来凭空“恢复”已忘的信息。缓存旧推导可保留，但其语义/来源/元数据与字节仍收费。

先令 P4 的额外 controller memory M 只有一个节点：全部真实 controller memory 已编码在 z，因此 policy π 只能依赖 Visible(z)。若再允许额外 M，必须把该 controller state 和代码表全部计费，并约束其更新不绕过 z。P4 原版的 k 个抽象 memory states **不直接等于 k 字节**；本文的物理记录与合法变更约束是必要适配。

对每个 commit，强制当前 Checker(z,a) 成功，而且用公开 native model 与合法 retained evidence 验证

\[
D_{\rm public}\land \operatorname{Facts}_{\rm valid}(z)
\land \neg\Psi_a
\quad\text{不可满足}.
\]

若 Ψ_a 包含后继性质，把 transition relation 及 negated successor obligation 一并放入公式。检查器应有可检查 witness；native provenance/consumable-token 义务另作显式检查。这样 gate 针对整个 Compat(I)，不会因选定 policy 历史恰好只到达部分世界而缩小候选的知识义务。

还必须满足 uniformity：

\[
\operatorname{Visible}(z_h)=\operatorname{Visible}(z_{h'})
\Longrightarrow \pi(h)=\pi(h').
\]

这禁止在两条已合并/遗忘的历史上用不同动作暗中编码事实。Native actor 自己保留的上下文、事件日志和控制阶段也是信息载体；候选若可使用，基线同样可使用并共同计费。

在有限对象、有限版本/时域、有限记录/证书语言、完整公开转移模型与同一允许动作类内，候选策略逐步映射为这个 observation-uniform policy；每次 sensing 对应同一个合法回执分支，cost 和 commit check 可逐步对应。反向映射亦须依上述 memory-mutation 约束。因而**在此限定类中 lifecycle 可行性与成本选择被 reduction 到成熟 planning；增加四类 token 不创造新的规划语义**。

这不是 compactness 或 efficiency 定理。X×Z 可能指数甚至更大；无限对象/版本、未建模工具效果、真实并发、黑盒证书构造及未知实际成本，都不由此 reduction 自动解决。有限编码能表达所有内容，不能证明一个具体高效算法早已存在。

## 5. 最强 reference algorithm：预算约束的 strong 策略合成

这是能直接实现的经典组合基线设计，**本轮未实现/运行，不称为 P4 原软件的复现**。P4 给出 policy/execution graph/SAT/acyclicity 结构；费用 counter、真实证书检查和 memory-mutation restriction 是上述适配。

输入是公开 native model、相同初始合法 observations、相同 z 格式/证书语言、实际 source action 集，以及预先确定的 integer cost model、内存限制和 horizon/终止规格。绝不用隐藏真实初态替代初始世界集合。

~~~text
for cost budget C from a valid lower bound to a known feasible upper bound:
    create policy variables choose[o,u] with exactly one legal choice per o
    build transitions from public native effects, legal observations,
        actual memory writes, and cumulative cost <= C
    seed reachability for every allowed initial hidden state
    for every reachable (x,z,b):
        require the common choice for Visible(z) to be executable
        forbid illegal sensing, stale/consumed evidence use, and failed commit gate
    require every reachable non-goal node to have a successor
    require rank(successor) < rank(node) on every non-goal execution edge
    solve SAT/SMT plus graph constraints; validate the resulting policy
    if satisfiable: return policy and checked support witnesses
return "no strong policy in the stated finite model/action/representation class"
~~~

rank/acyclicity 保证所有 outcome 分支有限终止；目标须包含 native requested action 的接受/任务成功，不能只写“有证书”或允许永远 abstain。已知可行预算上界下可二分；内存峰值可独立加上限，或枚举 Pareto budgets。integer 化加权成本的最优性只对应该已声明模型；实际 wall time、通信、内存与 source 调用仍分项报告。不能把 planner 的巨大 compile/search 开销从成本表隐藏。

纯 sensing 只区分世界，不能把 false permission、已经 consumed 的 confirmation 或不足 resource 变成 true/unused/enough。初始集合包含这种世界且动作集没有合法恢复/新授权/补充资源步骤时，不能构造对所有初态完成目标的 strong policy；再多查询也不改变这个结论。允许正确报告 blocked，但 blocked 不作为 native task 成功。

这个算法允许任意便宜的 retain、替代支持、局部 observation 或 reprove 序列，**没有 full refresh 指令作为唯一恢复动作**。对同一 native action，它能发现“旧 Γ₁ 坏了、Γ₂ 仍可用”、只补取一个足以改变其他 obligation 的证据，以及消耗确认导致之后需重新获取的先后次序。优化 over all finite policies 可能非常昂贵，但昂贵不等于方法原则上缺少这些能力。

若改为 strong cyclic，则去掉所有非目标循环的禁止而加入对应 goal-reachability/fairness 约束，结果保证必须同步降级。若无强解，reference 不会用 hopeful outcome 替代证明；timeout/unknown 与 proved infeasible 分开记录。

## 6. 可扩展工程基线：不是全量 refresh

reference 较贵时仍要保留一个成熟、允许复用的工程控制。建议组合如下，不冒充某一论文完整复现：

1. 原生绑定、scope、version、expiry 和 consumed-token 跟踪；完整可见事件日志按共同政策保留与计费。
2. 依赖索引 + 多组 justification；收到真实合法事件后只标记其影响的当前支持，尝试已有 alternative proof，再判定是否 sensing。
3. Incremental SAT/SMT entailment 或适用的知识数据库；允许缓存、assumptions、proof/core 复用。Checker 收到的全部 facts 均来自当时合法 retained input。
4. 以当前 actor 的 a_pending 的未满足 obligations 为目标，做 costed AND/OR repair planning；分支必须使用合法 source returns。已获得事实通过 invariant/correlation 可能使其他 queries 不再必要。
5. 结构成立时启用 P5 的 factored/causal belief tracking；不成立时保守 overapproximation 或局部扩大/精确回退。只看 old-proof dependencies 不等于完整 semantic relevance。
6. 找到完整证书才 gate commit；commit 后按原生结果更新资源、确认消费、版本和支持。局部求解失败不能自动宣布信息论不可修复。

P1 给出 minimax / expected Bellman 与 RTDP 的成本决策近邻；P5 给出结构化 tracking，故不能用“全世界显式枚举、每步所有来源全读、全证明全重建”代表 planning 家族。它们的理论条件与代价须照实记录；sound but incomplete 的控制可保持 commit 安全，但未必完成所有候选能完成的任务。

P6/PO-PRP 可以作为其适用子域的外部实现控制，不能承接全部 lifecycle：作者的 uncertainty monotonic 假设直接排除了“已知后因未知改变再次 unknown”的一般情形。公开实现入口已核对：

- [QuMuLab PRP repository](https://github.com/QuMuLab/planner-for-relevant-policies)：README 给出 src/build_all 与 prp domain/problem 接口及 policy/local recovery 选项；本轮未 build、读全源码或运行。
- [Guy Shani ContingentPlanning repository](https://github.com/shanigu/ContingentPlanning)：作者 README 列出 SDR、CPOR、WriteKPlanner translation 与 POPRP scripts；本轮只核读 README，未检查完整项目/compatibility 或宣称成本最优。

## 7. Same actor、same legal information、same guarantee 的实际比较接口

不能让 symbolic baseline 另选一个更聪明 actor，也不能把一个固定 open-loop 参考动作序列当成真实 agent 的全部能力。固定同一 actor/checkpoint、prompts、task initialization、available tools 与 source permissions；替换的是支持维护/repair 层。每个 actor 提出的 a_pending 输入候选和基线，双方从各自合法保留状态规划合法 sensing/repair，然后把相同格式的证据、拒绝原因或回执交给同一 actor。相同 actor 对不同合法 observations 产生不同后续决策是正常结果，应计其后续模型/工具成本。

oracle 隐藏真相仅可交给独立 auditor 评估结果，不交给 baseline compiler。公开 native transition model 可共享；若为黑盒接口学模型、探测效果或生成 domain，则双方同权、训练/探测/初始化费用都计。没有条件构建精确完整模型时，报告 reference 不可得或模型边界，不把它写成已经跑过的强最优分数。

至少并行报告 task success/coverage、每次 commit 的 provenance/permission/version 正确性、source calls、native calls、certificate compute、preprocessing/search time、实际 retained bytes/索引/策略表/日志，以及拒绝与 timeout。必须让 baseline 使用 retain-all、local-cache、alternative-proof、on-demand sensing 等成熟选择；full refresh 另列，不是唯一经典 baseline。

## 8. 真实原生任务应从哪里开始

下表是来自官方接口语义的真实 task family，尚未执行。它们不是自己生成 support-loss 小图，也不是任何 benchmark 新成绩。测试环境须由 owner 授权，且状态变化用真实 API/native events 提供；本轮只查公开 docs。

| 原生任务 | 官方已存在的生命周期语义 | 适配中的具体比较 |
|---|---|---|
| 合并一个满足 repository rules 的 GitHub PR | Merge REST API 要求 Contents(write)，sha 可以固定 expected head，不匹配返回 409；protected branch 配置可在 diff/new push/merge-base 变化后 dismiss stale reviews | 同 actor 保存 head/approvals/check evidence；新 push 后正确失效相关证据，查当前合法支持，使用同一 sha guard，比较最少 native reads 与实际成功/正确拒绝。不得把旧 approval 当新版本授权。 |
| 更新 Kubernetes ConfigMap 等资源 | 条件更新使用 resourceVersion；过期版本返回 409。watch 历史不可得可返回 410，官方恢复为 cache clear、new get/list、从新版本续 watch | 允许双方 retain cache + watch 增量；按实际 scope 复取，不能强制每步 full list。410 时尊重 native 恢复语义，不能凭旧 snapshot 保证当前写入成功。 |
| OAuth authorization-code exchange | RFC 6749 明定 code short-lived、single-use；该 code 不能经保存旧文本重新变成未消费 code | 检验 source possession、client/scope binding、expiry 与 consumption。它不是一般用户“确认”文本的等价物，也不证明所有服务实现相同。 |

一手任务依据（只阅读相关条目，不声称完整规范已审）：

- [GitHub REST pull requests：Merge a pull request](https://docs.github.com/en/rest/pulls/pulls)，Permissions / sha / status codes。
- [GitHub protected branches](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches)，stale approval / most recent reviewable push / merge-base。
- [Kubernetes API Concepts](https://kubernetes.io/docs/reference/using-api/api-concepts/)，Updates to existing resources / Efficient detection of changes / Resource versions。
- [RFC 6749](https://www.rfc-editor.org/rfc/rfc6749.html)，§4.1.2、§10.5。这里只使用 code 生命周期事实，未设计或实施 OAuth 安全流程。

这些任务首先要固定可观察事件模型：没有 reliable watch/lease/atomic API guard 时，最近读过的状态不自动足以保证 commit 时仍成立。任意 silent concurrent change 可产生相同合法信息、不同应执行结果的两个世界；此时 candidate 与 baseline 都不能获得无条件“必成功”证书。原子 native guard 的 safety 与 return-success guarantee 应分别验收。

## 9. 哪些主张被杀，哪些严格剩余

| 候选主张 | 本轮 verdict | 理由 / 剩余义务 |
|---|---|---|
| 提交前要求合法信息保证所有 compatible worlds 的 action obligations | **宽泛新框架主张不成立** | K-preconditions 与 belief applicability 已直接存在；native provenance 需 adapter，不能以 adapter 名称申报一般语义创新。[P1,P2,P7] |
| sensing 有前提/成本，取得结果后修复/选择分支 | **宽泛新机制主张不成立** | 直接对应 contingent planning 与 costed belief-space control。[P1–P3] |
| 换已有 support set、局部补取，不全量刷新 | **不能作为避开经典对照的理由** | exact inference/AND-OR policies 已可选择 alternative plans；P5/P6 提供具体结构化/按需基线，但适用条件须检查。 |
| permissions/resources/confirmation/freshness 不能纳入同一成熟框架 | **在上述有限模型下不成立** | 已给出具体 native-state + legal-memory + observation-uniform reduction；P3 甚至有实现的 permission/resource 近邻。 |
| 一篇成熟工具已解决本候选全部真实接口与完整物理成本 | **本轮未证成** | 原软件/论文各有模型限制；尚无该完整复现。必须保留此边界。 |
| 一个新结构算法能更便宜维护 Γ、推导 repair 区域与替代支持 | **仍可能成立，但当前严格证据为空** | 需独立 soundness/适用条件/复杂度或相同真实任务上的优势；generic reduction 不杀掉未出现的新算法。 |
| 面向 support lifecycle 的新现象 | **未关闭** | 要真实原生任务与方法无关干预支持；本轮只有文献与 adapter 设计，没有自然现象测量。 |
| 联合 retain+maintain+reacquire 的新定理 | **目前是规格，不是新理论** | 需相对明确表示/证书/来源语言的结构结果或下界；P1 成本优化与 P4 有限记忆合成不是它的新定理。 |

可以继续的最窄 research target 是：**在明确 native operator 和证书语言中，从读写/来源结构构造可核验且低于通用 semantic synthesis 成本的 alternative-support 与 repair-region 算法，并证明其边界。** 这条路线尚未被本轮杀掉，也尚未成立。不能用“同一 mature framework 里有 reduction”宣告所有可能算法无创新；同样，不能用“通用 solver 不够快”自动宣告当前候选已有新算法。

本轮只关闭了宽泛优先权主张，提供可构建的强对照与真实接口候选。未跑新实验、未使用 hidden/gold/model、未改冻结内容，未关闭 T2/T5 或全部 scientific gate。
