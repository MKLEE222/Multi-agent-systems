# OACR support kill：主动取证、替代证书与合法测试

日期：2026-10-03。审查对象：future native action 的 Boolean obligation `Psi`、部分失效的已有支持、每个合法付费 query 仅填一个 hole、以全部相容世界的安全性决定是否 commit；保留与维护也计成本。

**结论：多 alternative evidence sets、依据当前支持只补必要 hole、付费查询后以 `forall compatible worlds` 停止，并不是独立新核心。** 在静态、无噪、可自由测试的片段，它直接落入 priced Boolean function evaluation / SBFE / certificate finding；一般有限相容世界可落入 equivalence class determination。测试先决顺序也已有直接近邻。未知查询结果时，正确的优化对象通常是 policy，而非一份静态最小 `Q`。加入权限、失效和保留收费可能使具体结构定理不再适用，但这本身没有证明算法新颖：有限 stateful 版本仍有标准 belief-state 控制基线。

本轮仅检索原始论文并阅读公开仓库文档。没有读取 benchmark gold、私有状态或外部模型，没有调用评测模型，没有修改冻结 producer。本报告附带的纯 Python 小例是**经典控制能力见证**，不属于 OCAR 收益、官方任务实验或新算法贡献。

## 1. 必须先固定哪种安全目标

令 `b in {0,1,*}^h` 是当前有效的部分观察，`W(b)` 是合同允许、与 `b` 相容的世界。过期证据应恢复为 `*`；已可靠观测的否定值是 `0`，两者不能混用。若查询不改变世界、只揭示当前 hole，那么经典的正停止条件正是

\[
W(b)\subseteq\Psi^{-1}(1).
\]

即 `b` 是 1-certificate。若允许安全拒绝或延期，负停止条件是 `W(b) subseteq Psi^{-1}(0)`，即 0-certificate。SBFE 以发现其中任一证书结束；每次选取下一测试可依赖已见答案。[R2, §2–4]

以下三个目标必须分开：

| 目标 | 正确对象 | 可解性 / 证书要求 |
|---|---|---|
| 最终正确判定能否 commit | 自适应决策树，允许 true/false 终止 | 所有不同标签世界须能被合法测试区分；true 才执行动作 |
| 所有世界最终都能正向 commit | 只允许 1-certificate 终止 | 若查询只揭示、不修复世界，而 `W(b)` 含 `Psi=0` 世界，则不可行；查询全体也不能把 false 变成 true |
| 给定实际世界的最便宜支持 | `min` certificate contained in actual input | 是事后 oracle 下界；没有看到答案的策略一般无法预先选中它 |

若合同已承诺 `Psi=1` 且纯粹只要求语义蕴含，`W(b)` 可以已全为正，零查询即可安全判定。若 native 接口还要求提交一份显式 receipt、指定来源或某个 DNF 项，即使世界逻辑保证真也必须取得见证，则目标是**带见证的证明要求**，不能把它悄悄等同为 Boolean evaluation。[R2, §2] 已明确比较过 evaluation 与 explanation：恒真的公式在前者可以零测试，在后者可能仍要求测试并交付一项。此区别不是新的现象。

## 2. 原始文献覆盖与适用边界

| 原始工作 | 对本候选直接覆盖什么 | 本轮不能越过的条件 |
|---|---|---|
| Charikar et al., *Query Strategies for Priced Information*, 2002 [R1] | 已知函数、未知输入、逐次付费取值；与实际输入内最便宜证明比较。AND/OR tree 的 `Balance` 达到该成本向量下最优 deterministic competitive ratio | competitive ratio 相对事后最便宜证明，不等于最小 expected cost；树结构与其成本模型不能免费推广为任意原生状态 |
| Deshpande–Hellerstein–Kletenik, 2014 [R2] | SBFE 的 paid bit query、unknown answers、自适应下一测试、0/1-certificate；CDNF/decision tree 的 `O(log(kd))` 近似与到 SSSC 的归约 | 正确性是全支持输入，优化是已知 product distribution 的期望成本；`goal value Q` 的可构造性与大小不是自动成立 |
| Allen et al., *Evaluation of DNF Formulas*, 2013 preprint [R3] | DNF 中任一成立项提供正证书；否定证书须击破所有项；共享变量的 sibling classes 与最优策略 DP | 一般 DNF 并非自动易解。其结构结果和复杂度必须按 formula class 使用 |
| Golovin–Krause, 2011，2017 修订 [R4] | adaptive policies、adaptive submodularity、adaptive coverage；对一般相关结果必须验证条件 | 2017 版本纠正了原 average-cover logarithmic proof，Theorem 13 改为 squared-log bound，带 strong 条件；不能照抄旧概括 |
| Hellerstein–Kletenik–Parthasarathy, 2021 [R5] | 随机子模覆盖 Adaptive Greedy 的 `alpha*(ln(Q/eta)+1)` 紧界，整数效用可用 `alpha*H(Q)` | 独立 item states、pointwise polymatroid、sufficiency、每个 realization 全体测试都达到 `Q`；该证明明确依赖独立性 |
| Golovin–Krause–Ray, EC2, 2010 [R6] | 有限 hypotheses 按决策标签分 equivalence classes；直到剩余版本空间落入一类，按 expected cross-class edge cutting / cost 选测试 | 成本和先验已知，测试结果由固定 hypothesis/noise realization 决定；其 noisy decision 目标也可为与全测试相同的 Bayes decision，不自动等于零风险 native commit |
| Hellerstein et al., *Adaptivity Gaps for SBFE*, 2022 preprint [R7] | 固定顺序与自适应策略是不同基线；read-once DNF 已有非平凡甚至很大的 adaptivity gaps，策略表示成本也被讨论 | 不可把固定顺序的损失记为新“支持感知”效果；要允许经典基线按结果改下一测试 |
| Blanc–Koch–Lange–Tan, STOC 2022 [R8] | certificate complexity 与找证书已是独立成熟问题；monotone 函数有 `O(k^8 log n)` queries 的高概率小证书算法 | 它查询的是未知黑盒函数 `f(y)`，而 `x*` 已给定；不是免费可调用的原生 hole query。不能直接拿该 bound 当 SBFE 执行成本 |
| Blanc et al., ITCS 2023 [R9] | circuit 表示下 certificate 验证的 computational difficulty；VerifyCert 为 coNP-complete | 语义证书检查不是免费 oracle；需要给表示、求解器和计费。原问题有 NP oracle，原生系统未必有 |
| Gupta–Nagarajan, IPCO 2013 [R10] | stochastic probing 已区分 probe 的 outer feasibility 与成功选择的 inner feasibility，并要求每个 realization 遵守 | 这是 packing maximization，成功 probe 需 irrevocable accept；不是任意 safe-commit cover，但排除“合法 probe 约束从未被考虑”的泛称 |
| Szyfelbein–Dereniowski, 2026 preprint v4 [R11] | predecessor test 必须先执行；precedence-constrained decision trees 同时研究 worst-case 与 average-case，给一般及 inforest/outforest 近似 | 文中每测试单位成本，平均目标为 uniform hypotheses 下总路径长，终点是识别 hypothesis；权限是固定 poset，不是 outcome-dependent/revocable authorization |
| Smallwood–Sondik, 1973 [R12] | 有限隐藏 Markov 状态、状态转移、观察与行动、有限 horizon 的最优 belief-state policy；具体示例就是维护 | 提供通用建模与最优控制基线，不提供本候选特殊图上的高效参数界；扩展 state 不能当新定理 |

`Psi` 只是 Boolean 公式，并不保证 `gain = newly satisfied obligations` 是 submodular。最小反例 `Psi=x1 AND x2`：把已证实 true 的坐标集合记为 `S`，效用 `g(S)=1` 当且仅当 `{1,2} subseteq S`。则 `x2` 在空集的边际是 0，在 `{x1}` 的边际是 1，违反 diminishing returns。SSSC 的成熟路径是构造适当 assignment-feasible utility，而不是直接把 Boolean commit indicator 当子模效用。[R2, §4–5] 这里的反例是本报告推导。

## 3. 两个严格替代支持例与三个不同成本

### 3.1 保留部分有效支持之后，仍是经典残余函数

设

\[
\Psi=(a\land b)\lor(c\land d),\qquad b_0:a=c=1,
\]

已保留 `a,c` 的有效 receipt，`b,d` 是过期 hole。每次合法 query 只读取一个 hole；`c_b=1,c_d=2`，剩余位独立且 `p_b=p_d=1/2`。残余函数就是 `b OR d`。先测 `b`，true 即可使用 `{a,b}` commit；false 再测 `d`，true 使用 `{c,d}`，false 安全拒绝。

此策略期望取证成本 `1+(1/2)*2=2`；反序成本 `2+(1/2)*1=5/2`。这是 OR 的经典 `c_i/p_i` 排序规则。[R2, §2] 若 retain / maintenance `a,c` 收费合计 `rho`，相同保留选择的完整成本就是 `rho+2`；不得把 `rho` 藏在候选之外。若保留选择本身可优化，所有基线必须拥有相同 retain/drop/replace 能力并支付同样收费，见 §5。

因此，“支持 A 失效后换 B”“不刷新无关支持”“发现一条替代支持即可结束”本身已可由 formula restriction、DNF certificates 和 adaptive testing 表达。这个例子没有使用全刷新作为性能基线。

### 3.2 四位穷举：oracle certificate 不等于可执行查询计划

现在四个位都是 hole：

\[
\Psi=(x_1\land x_2)\lor(x_3\land x_4),
\quad c_i=1,\quad p_i=1/2\text{ independently}.
\]

正证书是任一项的两个 true；负证书是每项各一个 false。每个实际世界都有成本恰为 2 的最小证书，但找出该证书需要按未知答案取证。

| 最优化对象 / 可执行权限 | 精确成本 | 为什么 |
|---|---:|---|
| 实际输入预知后的 offline 最小 0/1-certificate | 每世界都是 2，期望也是 2 | true 选一条成立项；false 每项选一个零 |
| 最佳固定顺序，遇到语义证书立即停止 | `25/8` | 穷举全部 24 顺序与 16 世界；本例全部顺序相同 |
| 最佳自适应 hole-only 策略 | `21/8` | 答案改变后续测试；81 个 partial observations 的精确 Bellman DP |
| 最佳 minimax 策略 | 4 | 对抗答案可要求读全体；DP 取 branch maximum |
| 一次固定 batch，所有 batch 答案都须确定 `Psi` | 4 | 任何少测一位的 batch 都留下异标签世界对 |
| 所有相容世界最终都正向 commit，禁止 false/abort | 不可行 | 16 世界中 9 个 `Psi=0`，揭示答案不能改变世界 |

一个最优自适应策略：先测 `x1`。若为 0，跳过 `x2`，只评估 `x3 AND x4`；若为 1，先测 `x2`，它为 1 则停止，为 0 再评估后一项。期望成本为

\[
1+\tfrac12\cdot\tfrac32+\tfrac12\cdot\tfrac74=\tfrac{21}{8}.
\]

这里固定顺序允许证书一出现就停止；它不是“无条件刷新所有 hole”弱基线。固定顺序若允许根据答案跳过无关测试，就已经获得自适应决策能力，必须按其实际能力归类。`25/21` 是这个经典小例的 adaptivity ratio，**不是 OCAR 相对经典算法的收益**。

### 3.3 expected 与 worst-case 的最优策略也可不同

本报告另作解析例：`Psi=(s AND a) OR ((NOT s) AND b)`，独立 fair bits，`c_s=100,c_a=c_b=1`。按 expected cost 最优的是先测 `a,b`：相同则无需 `s`，不同才测 `s`，故 `E=2+(1/2)*100=52`、worst=102。按 worst cost 最优的是先测 `s` 再测对应位，worst=101、E=101。offline 最小证书的期望为 `(1/2)*2+(1/2)*101=103/2`。

这不是额外算法贡献，只说明“min cost”若不指定 expected、worst、realized 或 competitive ratio，连要选哪个首测都不确定。该解析例另以临时内存中的 Fraction 穷举核对；持久检查器只针对 §3.2 的四位固定控制例。

## 4. 未知结果下静态 `min Q` 的三种含义

设原始表达式是“找最便宜 `Q`，补齐它之后对全部相容世界安全 commit”。必须说明 `Q` 的答案如何量化：

1. **存在一组有利答案**使 `Q` 为正证书：这会挑中根本没有实现的支持；不能保证合法执行。
2. **给定实际答案**选最便宜 `Q`：这是 offline certificate oracle，不是部署前可实现策略；§3.2 得 2。
3. **全部可能答案**都必须正向 commit：只揭示信息时，有 false 世界即无解。若改为全部答案都能正确判定，问题是 valid fixed batch；§3.2 得 4，但优化目标不再是自适应最优期望成本。

静态问题并非一律无意义：在查询结果预知、确定性源、固定 batch 要求或事后证书选择中，它完全有定义。病态的是混淆这些对象，或让候选预知实际 receipt 再与不知道答案的基线比较。

## 5. 可计算的强基线：同信息、同权限、同总收费

### 5.1 精确 classical DP（小合同的金标准）

对无状态静态测试，令 `T(b)` 是合法未测 hole。若允许正确 true/false 判定：

\[
V_{\rm exp}(b)=
\begin{cases}
0,&\Psi\text{ 在 }W(b)\text{ 上恒定};\\
\min_{i\in T(b)}\{c_i+\sum_o P(o\mid b,i)V_{\rm exp}(b\cup\{i=o\})\},&\text{否则}.
\end{cases}
\]

将 branch expectation 换成 maximum 即 `V_worst`；未终止且无合法测试的状态置 `+infinity`。纯 SBFE 独立位用 `p_i`；有限相关 scenario 用公开先验与相容世界算 conditional probability，不能把 posterior 当额外私有信息。一个大小为 `h` 的全 Cartesian hole 模型最多 `3^h` 部分赋值；做 truth-table consistency 检查的枚举成本另计。近邻 [R2, §2] 已给 truth-table 版本的精确 DP，而 [R3] 进一步按 DNF 结构压缩。

与候选比较时至少保留：exact DP、最优固定顺序提前停止、matched legality 的 classical adaptive heuristic。不得只给 full refresh 或将经典基线禁止保留多条支持。

### 5.2 certificate / batch 的 exact ILP（区分 oracle 下界）

有限世界下，实际世界 `x` 已知时，令 `z_i` 选是否购买该位。对所有 `y in W(b)` 且 `Psi(y) != Psi(x)`，加入

\[
\sum_{i:x_i\ne y_i}z_i\ge1,\quad z_i\in\{0,1\},\qquad
\min\sum_i c_i z_i.
\]

它是 weighted hitting-set certificate optimum，只能作为 offline 下界；若要一个**对全部答案都判定**的 batch，则对所有异标签对 `(x,y)` 加同类约束。权限先决可加 closure 约束，但结果依赖、可撤销权限仍需 policy state。该可计算 ILP 是本报告的直接编码，未声称为新方法。

### 5.3 成熟 polynomial / approximation 对照

- OR/AND 用经典最优比例顺序；read-once / CDNF 使用与具体 formula class 匹配的 published strategy。[R1–R3]
- 若能公开构造 assignment-feasible utility `g` 并给出适当 `Q`，使用 SSSC Adaptive Greedy / Adaptive Dual Greedy；只在相应 theorem conditions 下报告 bound。计入 `g` 构造、期望边际查询、证书检查和保存成本。[R2, R5]
- 对显式有限 correlated scenarios，将世界按 `Psi` 标签分两类，EC2 按 expected cross-class edge removal / cost 取证，到剩余世界全落一类即停。此 baseline 无需猜一个支持集合；但不能免费枚举指数多 worlds，且有原生权限时要给同合法动作。[R6]
- 对固定测试先决 poset，使用 precedence-respecting decision-tree DP；如果完全匹配单位成本、uniform hypothesis identification 的结构，也应纳入 [R11] 的算法。只需要动作标签时不能故意要求基线完整识别世界，否则会人为抬高成本。

### 5.4 retain / drop / expiry / stateful query：统一收费的有限状态基线

扩充状态为 `z=(belief/support state, retained witnesses, permission state, version/time, budget)`。公开合同给每合法动作的 observation/transition 与收费 `kappa(z,u)`，把 retain、drop、replace、query、局部重算及证书维护都作为动作或状态收费。终止时校验实际 retained witnesses 是否满足 native receipt / version / binding 要求；不得用免费完整历史复原被删 receipt。

有限 horizon 时 exact baseline 是

\[
V_t(z)=\min_{u\in L(z)}\{\kappa(z,u)+\sum_o P(o\mid z,u)V_{t+1}(U(z,u,o))\},
\]

并给安全 commit / safe failure terminal、deadline 和不终止罚值；robust worst-case 用 max 代替 expectation。若 zero-cost retain/drop 会成环，不能假设递归天然 acyclic，须用有限 horizon 或标准 stochastic-shortest-path 条件。这是把候选公开合同接入标准部分可观察控制的推导。[R12] 不是 SBFE 原 theorem 已包含任意维护收费的宣称，也不是新的控制原理。

该 exact baseline 可能昂贵，但它让“最优”“局部”“联合维护”变为可检验对象。比较应计入 offline compilation、policy lookup、online update、stored policy / support bytes 与 legal tool cost；若双方可摊销同一次编译，则相同摊销。经典 DP 拥有候选相同有效支持与合法来源，不需要 full refresh。

## 6. 什么仍未被这些具体结构定理直接覆盖

| 合同特性 | 缺的是哪个条件 | 本轮判定 |
|---|---|---|
| 查询结果未知，但世界和合法测试固定 | 不缺新模型条件 | SBFE / ECD 已覆盖。新命题不能只重述 alternatives 与 residual query |
| tests 之间相关 | 独立 product state | 不直接套 [R5] 紧界；finite scenario ECD 与 exact conditional DP 仍是基线 |
| 任意 `Psi` circuit / support formula | efficient certificate verification、small goal value 或可解 formula class | 不是“Boolean 就可高效优化”；[R9] 给 computational 难度近邻 |
| 静态 predecessor tests | unrestricted query；但是固定 poset | [R11] 是直接权限近邻，应按其真实单位成本/uniform/identification范围比较 |
| 根据查询答案授予/撤销权限、查询消耗资格或产生写效应 | fixed realization、history-independent item state、poset closure | 要进 stateful policy；不能只给 query set。一般控制建模已成熟，尚无本合同的特殊高效定理 |
| 时间流逝或别的 query 使已知证据失效 | information/utility monotonicity；一次性稳定测试 | 子模覆盖边际与终止保持性须重证；exact augmented-state baseline 仍成立于公开有限合同 |
| retain/drop 改变可用 witness、未来费用 | 原 SBFE 固定 per-test additive cost；免费记忆 | 要显式收费和受控遗忘；先建立同状态同成本 baseline，再谈表示优势 |
| 来源绑定、scope、receipt format 是 commit 条件 | 仅由 Boolean truth label 决定的终止 | 要写 native verifier 的可观察可判定 predicate；不能把“语义真”替换成“持有所需原生见证” |

这些是**未满足近邻具体 theorem hypotheses 的位置**，不是独立新颖性证明。本轮没有确定可成立的新残差定理。若要继续，须限定真实出现的结构，例如局部 outcome-transition、有限 churn、有限 horizon 与可观测 permission state，再提出以下可验证目标之一：

1. 一个精确/FPT/approximation 算法，在公开 support/permission/transition 的明确参数下优于同结构 classical state DP，给对所有合法历史的正确性和完整费用界。
2. 一个表示充分性或因子分解定理，证明哪些 retained information 足以继续最优或近优控制，同时保留 native 见证、权限与失效语义。

两者都必须解释新参数与标准 decision-tree / belief-state / decision-diagram 结构参数的关系，并给分离族或既有方法不能达到的界。仅说“SBFE+maintenance+permission 的组合”不能过优先权门。若某个 test legality / transition / retention 条件被省略，须把适用片段写在命题中，不得泛称覆盖全部 native action。

## 7. 可执行控制见证与结果

检查器：[active_acquisition_classical_witness.py](../experiments/oacr_support_kill/active_acquisition_classical_witness.py)。结果：[CLASSICAL_WITNESS_2026-10-03.json](../experiments/oacr_support_kill/CLASSICAL_WITNESS_2026-10-03.json)。

```bash
python experiments/oacr_support_kill/active_acquisition_classical_witness.py --out experiments/oacr_support_kill/CLASSICAL_WITNESS_2026-10-03.json
```

结果：`all assertions passed`。仅使用 Python 标准库；所有概率与期望成本使用 `Fraction`。穷举 16 worlds、81 partial observations、24 fixed orders、16 batch subsets。truth-table 的 universal-world certificate 与独立编写的 DNF 0/1 规则在全部 81 状态一致：25 个 0-certificate、17 个 1-certificate、39 个 ambiguous。随后分别运行 expected DP、minimax DP，逐世界执行求出的策略、检查终止证书和真实标签，再枚举每世界全部 coordinate subsets 检查 offline minimum。精确结果为：

```json
{
  "optimal_adaptive_expected_cost": "21/8",
  "optimal_fixed_order_expected_cost": "25/8",
  "optimal_minimax_cost": 4,
  "minimum_determining_batch_cost": 4,
  "offline_certificate_cost_all_worlds": [2],
  "expected_offline_certificate_cost": "2",
  "fixed_order_to_adaptive_ratio": "25/21",
  "all_world_positive_commit_feasible": false
}
```

该见证不读取 benchmark 或 candidate 输出，没有 hidden-world peek。offline certificate 是显式标注的 oracle 下界，部署策略不访问 oracle。脚本不改变 producer、冻结合同、模型或 official denominator；它展示经典算法已具备的替代支持、按结果选 query 和安全停止能力。

## 8. 原始来源（2026-10-03 核对）

- **R1.** Moses Charikar, Ronald Fagin, Venkatesan Guruswami, Jon Kleinberg, Prabhakar Raghavan, Amit Sahai. *Query Strategies for Priced Information*. JCSS 64(4), 2002. [作者托管全文](https://web.cs.ucla.edu/~sahai/work/web/2002%20Publications/J.CompSysSci2002.pdf)。§1.1、§2.2 / Theorem 2.8；不是以检索摘要替代原文。
- **R2.** Amol Deshpande, Lisa Hellerstein, Devorah Kletenik. *Approximation Algorithms for Stochastic Boolean Function Evaluation and Stochastic Submodular Set Cover*. SODA 2014；[作者预印本](https://arxiv.org/abs/1303.0726)，[全文](https://arxiv.org/pdf/1303.0726)。§2、§3 certificate 定义、§4 CDNF、§5 goal-value 限制。
- **R3.** Sarah R. Allen, Lisa Hellerstein, Devorah Kletenik, Tonguç Ünlüyurt. *Evaluation of DNF Formulas*. [2013 作者预印本](https://arxiv.org/abs/1310.3673)，[全文](https://arxiv.org/pdf/1310.3673)。§6 / Theorem 4 sibling classes 与 DP，§7 certificate-cost / strategy-cost gap。
- **R4.** Daniel Golovin, Andreas Krause. *Adaptive Submodularity: Theory and Applications in Active Learning and Stochastic Optimization*. JAIR 42, 2011；[2017 修订版本](https://arxiv.org/abs/1003.3967)，[全文](https://arxiv.org/pdf/1003.3967)。§5.2、Theorems 13–14、Historical Note。
- **R5.** Lisa Hellerstein, Devorah Kletenik, Srinivasan Parthasarathy. *A Tight Bound for Stochastic Submodular Cover*. JAIR 71, 2021. [作者预印本](https://arxiv.org/abs/2102.01149)，[全文](https://arxiv.org/pdf/2102.01149)。§1.1 Assumptions 1–4、Theorem 1；§1 说明独立性边界。
- **R6.** Daniel Golovin, Andreas Krause, Debajyoti Ray. *Near-Optimal Bayesian Active Learning with Noisy Observations*. NeurIPS 2010. [会议原文](https://proceedings.neurips.cc/paper/2010/file/1e6e0a04d20f50967c64dac2d639a577-Paper.pdf)。§3 ECD 定义与 EC2、Theorems 3–4、§4 noisy decision equivalence classes。
- **R7.** Lisa Hellerstein, Devorah Kletenik, Naifeng Liu, R. Teal Witter. *Adaptivity Gaps for the Stochastic Boolean Function Evaluation Problem*. [作者预印本 2022](https://arxiv.org/abs/2208.03810)，[可检索全文](https://arxiv.org/html/2208.03810v1)。§1、§2 Theorems 2.1–2.5。只采用具体 theorem 陈述，没有把摘要中的渐近范围当任意公式的保证。
- **R8.** Guy Blanc, Caleb Koch, Jane Lange, Li-Yang Tan. *The Query Complexity of Certification*. STOC 2022. [作者预印本](https://arxiv.org/abs/2201.07736)，[全文](https://arxiv.org/pdf/2201.07736)。Definition 1、Theorem 1、Claims 1.1–1.2；特别核对 query access 是 `f` 的求值。
- **R9.** Guy Blanc, Caleb Koch, Jane Lange, Carmen Strassle, Li-Yang Tan. *Certification with an NP Oracle*. ITCS 2023. [会议原文页面](https://drops.dagstuhl.de/entities/document/10.4230/LIPIcs.ITCS.2023.18)，[作者全文](https://arxiv.org/pdf/2211.02257)。Definition 4、Lemma 4.1 / VerifyCert。
- **R10.** Anupam Gupta, Viswanath Nagarajan. *A Stochastic Probing Problem with Applications*. IPCO 2013. [作者预印本](https://arxiv.org/abs/1302.5913)，[全文](https://arxiv.org/pdf/1302.5913)。§1 模型的 outer / inner constraints 与 irrevocable successful probe。
- **R11.** Michał Szyfelbein, Dariusz Dereniowski. *Precedence-Constrained Decision Trees and Coverings*. [2026 预印本，v4 修订于 2026-07-12](https://arxiv.org/abs/2602.21312)，[全文](https://arxiv.org/pdf/2602.21312)。§2 Problems 2.1–2.2、unit path-length costs；§3 approximation；§7.1 明确 uniform-distribution 限制。是当前日期之前的直接近邻，尚按 preprint 身份使用。
- **R12.** Richard D. Smallwood, Edward J. Sondik. *The Optimal Control of Partially Observable Markov Processes over a Finite Horizon*. Operations Research 21(5):1071–1088, 1973. [出版方原文与摘要](https://pubsonline.informs.org/doi/abs/10.1287/opre.21.5.1071)。本文只用其 finite-state partial-observation control / finite-horizon policy 的建模结论，不声称复现其数值实验。
