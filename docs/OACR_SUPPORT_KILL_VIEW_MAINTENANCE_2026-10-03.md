# Support-Lifecycle kill test：materialized view maintenance

日期：2026-10-03。只审公开一手论文；没有 benchmark 任务、额外模型 API 或原生任务执行。
结论：**“依赖部分破坏后保留其它支持、利用替代推导避免全刷新”不能认领。**
现代强控制也不应被限制为单 dependency 的 stale 标记。

## 直接覆盖与可计算结构

1. Blakeley–Coburn–Larson，VLDB 1986，*Updating Derived Relations: Detecting
   Irrelevant and Autonomously Computable Updates*，公开全文 §4–5、结尾。
   研究 update 对 view/constraint 是否无关，以及仅凭旧 view 与公开 update
   能否维护。对所审 relational fragment 给充要条件；条件的可判定效率依赖
   satisfiability fragment。结尾已经明确提出最小额外 base-data 获取问题。
   这不是当前已有完整最优补查算法的证明，也不能用四十年前的 open question
   宣称今天仍未解决。[一手全文](https://www.vldb.org/conf/1986/P457.PDF)

2. Gupta–Mumick–Subrahmanian，SIGMOD 1993，*Maintaining Views Incrementally*，
   原文摘要与 counting/DRed 算法。每个 tuple 可有多个 alternative derivations；
   非递归含 aggregation/negation 的 counting 与一般递归的 DRed 分开。
   某推导失效不意味着结论失效：仍有其它推导即可保留。递归下不能用简单计数
   的循环自支持冒充正确控制。
   [一手全文](https://www.cs.columbia.edu/~gravano/Qual/Papers/13%20-%20Maintaining%20Views%20Incrementally.pdf)

3. Mistry–Roy–Sudarshan–Ramamritham，SIGMOD 2001（2000 preprint），
   *Materialized View Selection and Maintenance Using Multi-Query Optimization*，
   §1、§3、§4–6。共同选择 transient/permanent 中间结果、共享子表达式，以及
   incremental/recompute 计划。维护计算和保留中间结果的权衡已有明确算法。
   原文的 optimal plan 有固定候选物化集合等条件；物化集合搜索用 heuristic，
   不能说所有存储约束下都有全局多项式最优。
   [作者全文](https://www.cse.iitb.ac.in/~sudarsha/Pubs-dir/viewmaint-sigmod01.pdf)

4. Koch et al.，*DBToaster: Higher-order Delta Processing for Dynamic,
   Frequently Fresh Views*，2012 preprint，§1、§4–5。维护 query 的 delta views
   与更高阶 delta，用多层辅助物化减少重复计算，公开实现亦存在。不能将
   “support views 支持彼此维护”或“编译成更新触发器”视为新对象。
   [一手全文](https://arxiv.org/pdf/1207.0137)
   [作者实现](https://github.com/dbtoaster/dbtoaster-backend)

## 面向 action 的精确映射与边界

这是本次审查的 reduction，不是上述论文原任务：固定参数的动作可定义
`Ready(a)` 派生关系；已合法观察并仍有效的 receipts、版本、作用域和资源是
base evidence，guard/authorization rules 是 view definition。多套充分证据是
多套 derivations；公开失效事件是相应 evidence 删除/更新。完整证明依赖可
由 provenance/ATMS 保留。action commitment 交给真实 guard/monitor，不由
view 的名称赋予环境权限。

因此“action obligation 使用逻辑而非逐项依赖”在表达层并不逃离经典控制。
复杂 guard、API refinement 和精确 effect relation 仍需正确建模；不是每个
Python API 自动属于这些 relational fragments。

静态 view maintenance 通常得到 update delta；如果允许未观察外部写入，不能
把不知道的 update 当成免费已知 delta。查询未知结果、状态依赖合法性及负分支
需要主动取证/部分可观测规划；并不由 counting 自行解决。把这些能力接入经典
组合控制是必要公平对照，也不是现成论文已经完成同一个系统的断言。

## Kill 决定

撤回对 partial invalidation、alternative derivation 与 retain/maintain/recompute
组合概念的核心新颖性预期。未确认任何同保证下不可消去的经典额外成本或适用
范围差额。若继续研究，只能先列真实 API fragment、已知/未知 update 语义、
合法 acquisition 动作与成本，再对实现保留经典能力的控制提出明确算法命题。
本报告没有证明整个研究领域已封闭，也没有为当前候选提供独立核心豁免。
