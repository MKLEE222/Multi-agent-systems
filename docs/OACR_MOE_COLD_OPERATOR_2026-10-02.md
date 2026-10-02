# OACR 冷启动：从原生对象提出三个算子候选

日期：2026-10-02。独立冷启动审查；没有读旧 512 个封存单元，没有改 producer 或 gate，没有运行模型系统或大规模任务实验。

**推荐先实施候选 A 的最小原生接口与正确经典对照；候选 C 是更远的独立方向；候选 B 是可立即验证的语义/构造方向。三个均未取得独有优势或定理优先权。** 这里遵守用户的原创校准：可用已有逻辑、切片、类型和维护组件；贡献可以在对象、可算构造、结构范围或同保证完整成本，不要求零件从零开始，也不要求现象、理论、方法各自独立首创。

已读指定的四份 foundation/adaptation/audit/baseline 文档及 `real_bfcl_views_v1.py`。基线事实是：图内 query/flow/proof-DAG 已被强控制匹配；官方 BFCL base 文件系统 50 案例的参考前缀上，IndexedViews 与 DemandViews 各 known 19/73、原生不一致 0、官方省调用 0。故不继续给旧 Need 另加索引，也不从这 19 个命中推断新收益。完整 AMA/ACE/AgeMem 系统尚未跑，这一缺口没有被本报告补齐。

## 1. 候选的差异和优先级

| 候选 | 真正研究的对象 | 与旧缓存/Need 的区别 | 最强必须比较的近邻 | 首个可证伪问题 |
| --- | --- | --- | --- | --- |
| A：效应绑定的一次性当前授权 | 可见会话中的具体意图、当前实体绑定、原生效应与一次性资格之间的可检查关系 | 准备一个不可重复的真实写入，保持授权与效应一致；不是回答同一读取 | LPCFS/linear authorization + source WP/typestate + PAuth operand slice + 正确增量 guard 维护 | 同输入下，标准 intent key、版本、affine guard 与 source summary 是否已经得到同保证、同成本？ |
| B：观察可得的别名/定位运输 | 公共操作产生的共享内容对象、目录 entry map、父指针及观察见证 | 绑定沿调用词改变，且两个不同路径能写同一对象；不把重绑定统一成删边 | 精确 symbolic heap / points-to / separation logic + 增量值维护 | 是否存在既无需 backend identity、又比同等 lazy symbolic heap 更省完整存储/维护的构造？ |
| C：经许可的区分消除程序 | 在隐藏状态下，通过原生写入建立义务，而非恢复过去被省略的事实 | 补取可以被合法状态建立代替；改变环境和改变知识有不同合同 | conformant/contingent planning、reset words、factored belief tracking、框架/授权条件 | 计入用户角色、副作用与全部 action/receipt 后，是否仍有可实现的取证/存储节省？ |

三者可以共享基础类型，但不能在实现后把它们合并为一个没有分离预测的万能模块。A 的关键是**授权效应运输**，B 是**位置和对象的别名语义**，C 是**用许可动作消除区分**。

## 2. 候选 A：效应绑定的一次性当前授权

### 原生事实与任务需要

τ² retail 固定修订 `5bfa7e37b36656b37dc6d022156be6563c1007f3` 的 `modify_pending_order_items` 是直接载体：

- 原生入口精确要求 `order.status == "pending"`，成功置为 `pending (item modified)`；同一原语的成功重试不可行。
- `item_ids` 与 `new_item_ids` 是按位置配对的列表；原商品多重性、同产品、可用性、价格差、付款归属/余额共同决定是否合法。
- 用户明确确认是工具文档中的政策义务，函数没有 `confirmation` 参数或独立会话授权检查。工具成功不能证明政策授权正确。
- 该函数写订单、payment history 和可能的 gift-card balance。授权某个操作名或某组 item ID，并不自动授权任意价格/支付/目标效应。

这是真实任务中不可逆的决策瓶颈。只保留最后的订单内容可能忘掉已消费的资格；只找回旧的“yes”可能让新意图复用旧授权。后续用户会话可以修改商品、支付或范围，actor 必须在一次性调用前收齐并确认当前计划。不能预测用户未来不再改意，也不能把“all items collected”从 benchmark 私有目标注入。

### 对象、许可输入与原生操作

对象不是新的 capability 名称，而是三联关系

`(intent specification, native effect relation, current authority witness)`。

允许输入为：公开 API/schema/已核源程序语义，当前角色可见用户消息与 actor 提出的调用，合法取得的 order/product/user/payment 回执，以及本次已观察动作。不得使用 backend object、私有目标、未来轮或 evaluator 标签。文档/源程序的用途是静态接口审查；实际 actor 可见文档权限须单列并让对照相同。

原生动作仍为原来的 READ/WRITE 和会话请求。OCAR 内核只准备、验证、运输或阻断依据；不修改工具的 guard、状态转移或官方评分。

### 可算构造

先限定一个能够独立验算的源程序片段：有限控制、公开参数绑定、字段读写、列表计数/配对、有限聚合与显式异常。拒绝未知外部调用、未知 Python 别名或未审查异常路径；不要用 LLM 抽取置信度充当 soundness。

1. 从原生函数提取 branch-sensitive guard/effect summary，而非只列 READ/WRITE 字段。列表必须保留 multiplicity 与 pairing，不能各自排序后假定同义。
2. 为 actor 候选写入生成一个具体 obligation bundle：绑定身份、当前原生 guard、要承担的效果边界、用户确认范围、一次性资格状态。自然语言到 intent 的 soundness 单独声明；第一步用清晰显式确认语法，只覆盖该片段，其他消息返回“检查未完成/需解释”，不称为不可解。
3. 在新回执或意图变更后，检查旧授权能否运输至新 bundle：需证明新效果仍满足原来已确认的谓词，并且资格未被消费。只因值相等、semantic similarity 或相同 method name 不够。
4. 成功回执消费资格并更新效应；异常需走已经验证的异常路径。是否发生写入不明时保留可能已消费状态，先用允许操作消歧，不能自动重试。

关键构造输出应是“这个当前调用的效应符合这段当前授权”的证据，而不是一个全局 success label。经典对照必须得到相同 summary、角色输入、确认解析片段及增量优化能力。

### 最近主源和真正可能增加的结论

[A1] 的 linear authorization 已有主体 affirmation、知识与可消费资源；[A2] LPCFS 已经实现一次性/撤销凭证、离线验证及在线消费检查；[A3] PCP 已有资源逻辑、frame rule 与可执行计划的 soundness。因此“有证书且不能重复消费”不是新定理。

[A4] PAuth v2 进一步是直接 agent 邻居：源自用户任务的 operand-level slice 与带 provenance 的 envelope，而非只授权工具名。其 §III-A/§VI 明确把无事务保证、状态在读写之间改变以及 session isolation 排除在其机制保证之外。这个边界不是其实际失败的证据；它已有 proxy 部署选项，不能靠“无需改服务器”单独区分。

**候选命题 A-P（待证而非已成立）：** 在已声明的无隐藏干预区间，或原生操作本身拥有可核对的 live guard/效应见证的 API 类中，可从 effect summary 与当前可见 intent 构造一个授权运输检查器。它 sound 地接受恰当的“效果仍在原确认范围内”变更；资格消费、作用域变更或授权效果之外的变化返回拒绝/补取。若 summary 的关系约束结构满足指定宽度条件，运输与最小需再确认/再取证集合可在该宽度的参数成本内计算，且持久结构随活跃 effect/authority supports 而非整段对话增长。

这里的新增量不能只是写出 WP 或新的 width 字母。需要给一个源程序到 bundle/运输器的有效构造、说明参数与 factored belief/constraint width 的关系，并证明完整成本；若标准 WP + 参数化 CSP + affine ledger 完整推出，则理论部分归入继承。仍可能保留经检验的新接口/构造贡献，但必须相对同等经典实现有新保证或完整成本点。

没有事务或观察窗口时，“最后一次观察后没有看见更新”不等于当前值有效。对可能影响承诺效果的隐藏干预，要么证明动作对所有相容后继都安全，要么补取/回退；若干预可在补取与写入之间再发生，单纯反复读无法保证。该不可行边界先行冻结，不用未来给 API 加锁制造优势。

### Kill test 与可马上实施的第一步

**首个 kill test：** 相同 AST summary、相同清晰确认输入，在原生 retail 小规模 mutation suite 中比较 A 与“当前实体记录 + exact intent key + field versions + affine guard ledger + WP/guard checker”。覆盖一次成功后的重试、参数变更、无关事件、同 ID 多次商品、相同 ID 不同作用域、付款/价格依赖，以及异常路径。要求两者逐条 sound；对照允许局部更新和证据复用。若候选没有额外可检查保证且初始化、全部字节、解析/验证/维护和重新确认/来源调用不优，则停止其新内核主张。仅胜过没有 ledger 的记忆检索不通过。

**立即第一步：** 交付固定函数的原生语义表、一个 typed intent/obligation 数据接口、清晰确认 parser 的已声明范围，以及以上经典 guard 对照；再接 candidate transport。先独立 native audit，不跑 LLM、不取官方 task labels、不更改 third-party API。官方全任务闭环与 AMA/ACE/训练 actor 对照另立冻结版本，不能拿 fixture 的护栏通过率作任务收益。

额外源码校准：该函数后段用循环末次绑定的 `variant` 写每个 item 的价格/options，且按当前 `item_id` 查找后逐项变更。候选不得把理想的“配对同时替换”当作固定源码的实际效应，也不能把修第三方实现算为 OCAR 优势。第一步应保留这个实际语义并将其与政策意图分列；是否为合法任务可触发、官方检查如何处理，本报告未知，未读逐例标签。

## 3. 候选 B：观察可得的别名/定位运输

### 原生事实与短小可行性检查

BFCL 固定文件系统源码 `6ea57973c7a6097fd7c5915698c54c17c5b1b6c8` 中，directory `cp` 新建目录 wrapper 后用 `item.contents.copy()`；directory `mv` 赋值同一 `contents`。子对象及其 `parent` 并没有递归重建。故 API 不是普通 OS 的目录深拷贝/移动语义。

本报告只做了一个 21-call 的自建原生检查：从空 root 经公开 `mkdir/cd/touch/echo` 建 `a/f` 和 `a/kid/g`，`cp(a,b)`，在 `b` 写 `f="v2"` 后到 `a` 执行 `cat(f)`，回执为 `v2`；进入 `b/kid` 执行 `pwd` 回执 `///a/kid`，再 `cd(..)` / `pwd` 回执 `///a`。未读取 native object identity 或 backend 字段作预测输入，未用官方任务数据。这只验证语义障碍与接口可行性，不是自然发生率或科学优势。

最新两个 view 内核在 unknown/directory transfer 后全局 invalidation 与 fresh navigation namespace，正是为了避免错误的路径/版本假设。简单放松 barrier 会制造 false known；没有证明的多记几个 paths 不是改进。

### 对象、许可输入、原生操作和构造

对象包含三种不能混同的东西：directory entry map、child object 的共享关系、`parent` 导航关系。一个路径字符串不是稳定对象；symbolic object ID 只能由合法观察和公开操作创建的约束引入，不能冒充免费 inode。

许可输入为过去可见 calls/receipts、当前 proposed action、已核初始化/操作语义；不含未知初始树的内容或对象 identity。`cp/mv/cd/echo/cat/ls/pwd/rm` 用固定 native interpreter 执行。

可算构造是一个 role-observable symbolic heap：分别表示 entry-map copy snapshot、共享 child 和旧 parent，不枚举未知子树。对观察过的字段附支持；未知 contents 保留 unknown，copy 只运输它所保证的关系，不创造内容。遇到成员赋值、子对象 mutation 和 parent navigation，沿不同关系更新。路径渲染根据实际 parent 链，而非人类认为的 clone 路径；需要判断导航位置的多个相容 heap 时不能输出确定绑定。

最近的强经典控制是 lazy symbolic heap / points-to analysis，配合同样 receipt semantics 与增量 query materialization。Separation logic 的 locality/frame 和 bi-abduction 的 frame/anti-frame 是直接基础；后者主源 PDF 本轮未取得正文，只有原作者索引摘要，不能据摘要作具体定理排除。不能用 OS inode cache 作唯一 classical baseline。

**候选命题 B-P（待证）：** 在公开初始化不会制造未知 alias、后续共享仅由已审查复制/移动原语产生的 API 类中，构造一个仅依赖可见 prefix 的 symbolic heap，sound 且在指定正向观察片段内 complete 地运输已知值、相等/别名关系与导航见证。其 representation 和在线维护由已观察 entry/object/parent 的增量数及实际修改的 alias classes 控制，无需因 unknown directory transfer 丢失整个已知区。

soundness、symbolic heap 与局部更新各自已有传统；可贡献点只能是这个可算的观察受限复制/导航构造，或精确运输相对于保守 shape analysis 的结构范围，或相对于同保证 lazy heap 的完整成本。若强 classical 同样以 O(1) snapshot、共享 object records 和正确 parent 边做到相同，一般算法优势就被杀死；仍可把原生 adapter 收为基础。不能拿 eager 展开整树作唯一对照，也不能假定 unknown subtree 必须全恢复。

### Kill test、任务需要与第一步

固定一组不超过几十调用的 native fixtures，改变 copy 时机、overwrite、共享 child、entry-map divergence、parent navigation、rename/move 与失败路径。candidate 与 lazy heap 对照都只看可见 prefix，预测绑定/值与“未知”分开；原生执行独立验证。native semantics 不一致一次即先修构造；完全匹配而无额外保证/成本优势即退为适配基础。

真实任务允许这些原语，所以完整支持声称必须承担它们；但在 50-case dev 的自然发生率、本机制是否暴露于官方有收益任务，**未知**。立即第一步是把上述三个 heap relations 做成共享 source summary 和正确 classical reducer，再看 candidate 能否省 proof/状态运输成本。这不许可声称 directory coverage 自动转化为官方省调用：BFCL 累计 response checker 仍须真实产生需要的回执。

## 4. 候选 C：经许可的区分消除程序

### 对象与真实需要

τ² telecom 的角色工具使“取回缺失事实”不总是必要动作。`toggle_airplane_mode` 依旧状态翻转，同时改变 Wi-Fi/VPN/网络搜索；在未知 bit 上任意固定次数 toggle 无法保证目标 OFF。相反，已装饰并暴露的 `disconnect_vpn` 可以建立 VPN disconnected；`reset_apn_settings` 只置 `reset_at_reboot`，实际 APN replacement 要等 `reboot_device`。这是不同的算子家族：改变真实世界使若干初始区分对已授权后续义务失去影响。

双控任务要求维护器知道哪些东西是 agent 当前合法可见的。用户侧工具回执不因此成为 agent 私有工具；agent 只能收到协议给它的消息，向用户发指令后也不能免费假定动作已经完成。工具类 `device` property 和未装饰的 `turn_airplane_mode_off` 不属于本候选可用的免费状态/原语。

### 许可输入、原生操作与可算构造

输入是两个角色公开 API/转移摘要、agent 可见 prefix、当前授权的任务/保护条件与固定 horizon；私有 device/surroundings 和用户回执不直接输入 agent 维护器。

输出是带角色的原生 action/communication 程序以及 proof obligation：某段允许写入在所有相容初始状态和所声明的外部干预中建立目标谓词，且不破坏被保护的效应/授权。它不是保存一个“reset happened”词条：需核对延迟效应、失败、保护框架与用户实际可见执行证据。

可计算先限定 finite compositional API summaries，用静态分析识别可建立的 predicates、scope 和 delayed triggers；编译 `query-first` 与 `establish-first` 两类程序，在相同原生成本下比较。把无法按角色观察确认 completion 的分支返回未完成，而不是为用户工具代执行。强控制可以用同样 summaries、symbolic beliefs 和 compiled policies。

最近主源：conformant/contingent planning 已联合处理 actuation/sensing；reset words 已研究将多个状态送入同一状态；Bonet–Geffner factored belief tracking 已对相关上下文及 width 建界，且讨论可不经某些 actions 达到目标的 effective width。**“不必恢复世界也能完成任务”不是新的现象定理。**

**候选命题 C-P（待证）：** 对由公开效应摘要定义的 reset/establish modules，加入角色完成观察、授权与 frame 条件后，可编译一个局部区分消除程序；其正确性覆盖所有相容状态，而必要持久信息/取证只与不可安全覆盖的边界条件有关。如果这些 modules 的接口宽度有可计算界，完整编译与在线成本可按该界计算，而无需恢复每个被覆盖字段的原值。

真正可能新的内容是原生角色/延迟效应条件下的有效构造或同保证资源点，不是重命名 synchronizing word。需展示参数与 factored belief/causal/effective width 的关系；如果通用 symbolic contingent planner 得到同样程序与资源，候选的算法增量失败。单一 `disconnect_vpn` 的常值赋值不是分离实例。

### Kill test 与第一步

第一步只从已公开的两个用户工具 `disconnect_vpn` 和 `reset_apn_settings/reboot_device` 提取 effect + delayed effect + role observation 表；检查官方 protocol 是否让 agent 合法取得 completion 的充分见证。不能取得时先杀掉“agent 当前确定建立”主张，再研究用户角色局部表示，而非增加权限。

最小 kill suite 对同一允许任务义务比较：read/restore、establish、成熟 contingent planner。必须同时记动作与用户交互、全部回执/上下文、actor 调用、frame 副作用和初始化。加入不允许 reset、外部再次干预、pending trigger 没执行、用户未完成等负例。没有合法的非平凡 establish 程序，或对照同保证追平全成本，就终止。闭环才可能支持实际收益；冻结 reference trace 不允许替换世界行动来冒充分数。

## 5. 实施顺序与判据

1. **A 先做一个最小 source/native/authority 共用接口。** 它最直接承接 BRFP 的实体、效应、当前授权，并迫使核心决定“是否有资格做这次真实写入”；不再绕回读取缓存命中。先用 native audit 和正确经典控制争取构造/保证，再做官方闭环。
2. B 的 21-call 发现可以马上成为共享适配器的语义需求；只有越过 lazy symbolic heap 后才值得成为新核心。
3. C 保留为独立探索，其潜力在于改变表示维护原语，而角色协议最可能先把候选杀死。不要在没有 completion 证据前实现 agent 自动 reset。

所有候选通过 native correctness 都只完成第一关。原创贡献的具体定位必须随后写清，再核主源、同资源 strong controls、原方法完整系统与官方全分母。任何失败都按保证、结构范围、实际成本具体说明；不说“经典能做”便直接否决，也不把未验证的组合复杂性算为胜利。

## 6. 本轮主源核对与未知边界

- **[A1]** Garg, Bauer, Bowers, Pfenning, Reiter, *A Linear Logic of Authorization and Knowledge*；已打开全文，§1–5、cut elimination/主体知识与一次性 affirmation：[作者 PDF](https://www.cs.cmu.edu/~fp/papers/affknow06.pdf)。
- **[A2]** Morgenstern, Garg, Pfenning, *A Proof-Carrying File System with Revocable and Use-Once Certificates*；已打开全文，§1–4，原子消费/撤销、离线验证能力：[作者 PDF](https://people.mpi-sws.org/~dg/papers/stm11-lpcfs.pdf)。
- **[A3]** Hill, Komendantskaya, Petrick, *Proof-Carrying Plans: a Resource Logic for AI Planning*, arXiv `2008.04165v2`；已打开全文，资源逻辑与 executable functions 的 soundness：[PDF](https://arxiv.org/pdf/2008.04165)。没有将其确定性 planning theorem 泛化到隐藏角色通信。
- **[A4]** Sharma, Jiang, Chen, Lin, *Beyond OAuth: Task-Scoped Authorization for AI Agents via Natural Language Slices*, arXiv `2603.17170v2`（2026-08-25）；已读 §III–IV 和 §VI 关键边界，尚未运行实现：[全文](https://arxiv.org/html/2603.17170v2)。需与 CaMeL/FIDES/Progent/Cedar 当前版本继续对齐；本轮未做它们完整优先权审查。
- **[B1]** O'Hearn, Reynolds, Yang, *Local Reasoning about Programs that Alter Data Structures*：[作者 PDF 索引](https://www0.cs.ucl.ac.uk/staff/p.ohearn/papers/localreasoning.pdf)。**本轮正文打开失败**；基础 locality 不作为独有点，具体 theorem/最优成本未知。
- **[B2]** Calcagno 等，*Compositional Shape Analysis by Means of Bi-Abduction*：[作者 PDF 索引](https://www0.cs.ucl.ac.uk/staff/p.ohearn/papers/popl09.pdf)。**本轮正文打开失败**；作者摘要描述 frame/anti-frame joint inference，不据此声称已覆盖本候选全部保证与成本。
- **[B3]** Tzevelekos, *Fresh-Register Automata*；已打开全文 §1–2，names/registers/freshness 的 symbolic model：[作者 PDF](https://www.cs.ox.ac.uk/people/nikos.tzevelekos/FRA_11.pdf)。无免费 freshness oracle 的实际 API 不可直接套用，不能用 unbounded IDs 自称新结构。
- **[C1]** Bonet, Geffner, *Belief Tracking for Planning with Sensing: Width, Complexity and Approximations*, JAIR 2014；本轮复核 Definitions 12–14、Theorem 15、causal tracking 和 §10.3/12 的 encoding/effective-width 边界：[期刊 PDF](https://www.jair.org/index.php/jair/article/download/10901/25996/20340)。
- **[C2]** Yalciner 等，*Hybrid Conditional Planning Using Answer Set Programming*；已打开原文，sensing/actuation 共同序列建模：[PDF](https://arxiv.org/pdf/1707.05904.pdf)。未运行 ASP 系统。
- **[C3]** Szykuła, Zyzik, *An Improved Algorithm for Finding the Shortest Synchronizing Words*；已打开原文，exact reset-word algorithms：[PDF](https://arxiv.org/pdf/2207.05495)。未将 automaton 全状态 reset 与 protected-effect role-specific establish 偷换成相同保证。
- τ² retail/user tools/toolkit 已通过 GitHub connector 直接取得固定修订源码，只核函数与工具暴露边界，未抓 task labels：[retail tools](https://github.com/sierra-research/tau2-bench/blob/5bfa7e37b36656b37dc6d022156be6563c1007f3/src/tau2/domains/retail/tools.py)、[telecom user tools](https://github.com/sierra-research/tau2-bench/blob/5bfa7e37b36656b37dc6d022156be6563c1007f3/src/tau2/domains/telecom/user_tools.py)、[toolkit](https://github.com/sierra-research/tau2-bench/blob/5bfa7e37b36656b37dc6d022156be6563c1007f3/src/tau2/environment/toolkit.py)。
- BFCL 用已保存固定 source 的 function code 做 21 次独立 fixture feasibility check；没有 official task rerun、模型实验或 savings claim：[固定文件系统源码](https://github.com/ShishirPatil/gorilla/blob/6ea57973c7a6097fd7c5915698c54c17c5b1b6c8/berkeley-function-call-leaderboard/bfcl_eval/eval_checker/multi_turn_eval/func_source_code/gorilla_file_system.py)。

这里的主源核对是定向查邻近构造，不是全球优先权结论。MSS 完整系统与 MESA continuous-update 延伸、具体 automated source-verification 能力、三个候选相对成熟实现的完整成本均未知；报告没有将这些未知解释成对手不会做。

## 7. 候选 A 第一片段已实施及退出

本轮继续完成了 `experiments/oacr_moe/authority_transport/`：typed scope/action/结构化 confirmation/obligation、可见回执和 version/epoch、affine ready/spent/uncertain ledger、exact-intent cache，以及 effect-bound transport 与正确 classical semantic fallback。原生 target/helper body 自固定 τ² 源码逐字摘取并哈希，独立 verifier 不向维护器提供 backend 状态。该固定 summary 是人工按源语义实现的适配，不声称自动 Python 语义提取。

冻结后首次且唯一一次 suite 执行通过：31 自建 fixtures、每方法 8 admit / 23 deny，62 native write probes 加 194 public READs，共 256 native 顶层调用（内部 helper 次数不在此数）；每方法 20 个具体 guard/effect predictions 独立 audited，native 不一致 0、unsound fixture admission 0。runner wall 0.043890370 秒。没有失败 attempts、预冻结 suite runs、模型调用、官方任务或跨系统评分。完整入口、固定结果、源码归属与许可、执行摘要见该目录的 `README.md`、`result.json`、`execution_record.json`；当前 freeze 与最终代码匹配。

**结束这个已实现精确效应相等片段的独有内核主张。** 两个 class 的运输/授权条件都是同一 compiled effect equality，且共享维护框架；因此 deterministic counters 和序列化表示追平源于构造定义。native suite 的意义是审计 summary/adapter，不是独立两算法性能实验、CPU 相等或完整成本最优证明。保留可用 adapter 为基础，不推断更一般授权运输或限定宽度构造没有价值。

保证边界为明确结构化确认、已声明 effect projection 和 fixture 串行无干预区间；window 默认不可信，由 harness 协议显式声明，hidden interference 会使 epoch 失效。成功/无写入/消费不明是这批 fixture 明确提供的合成 ledger 输入事件，不冒称完整合法原生对话历史。未知角色通信、自然语言解析、隐藏更新下政策/效应、官方全任务收益都尚未验证。没有为堆数量追加实验，未把本片段强套到 AppWorld。
