# OACR：真实领域、算子适配与数学增量

日期：2026-10-02。源码审查基线：PR #89，`d5ebb7ab698cf7549b87546d2fdf6b91decf03aa`。
原始审查状态：真实任务、近邻原文及公开算子/评价器已核对；当时适配器未实现，没有新任务实验或新定理。后续执行按各自冻结版本单独登记。

2026-10-02 MOE 冷启动补记：ACE 父库的 AppWorld gitlink 已展开，准确作者版本为
`ace-agent/ace-appworld@9f3e92155345a9159f3a8b25abc334eeca05b545`，AppWorld
`0.1.4.dev0`，与下面只读审查的官方 `0.2.0.dev0` 不混用。作者环境已经安装、
指定数据已取得，train 首个环境执行 2 次公开 API 调用并关闭，ground truth 未载入、
模型/评分调用为 0。完整作者 actor 仍缺授权模型；环境就绪不等于官方任务收益。
τ² 的效应绑定授权另作独立原生构造开发，不因 AppWorld 可启动而获得跨系统验证。
具体冷审、入口与范围见 [冷基线](OACR_MOE_COLD_BASELINES_2026-10-02.md)、
[冷算子](OACR_MOE_COLD_OPERATOR_2026-10-02.md)。

同日子代理 actor 变体已实际完成首 3 个 train IDs（同一 scenario），原生任务
3/3 通过；它使用作者公开初始 prompt/playbook，没有执行完整 ACE 学习角色或
OCAR 维护增量。默认模板的 API 先验/no-GT 动态评分报告推断也已通过实际渲染
审计纠正。结果与界限见 [子代理执行](OACR_SUBAGENT_NATIVE_TASK_EXECUTION_2026-10-02.md)。

用户最新修正：完整有限合同不足以充当论文锚点。近邻和强基线有自己的真实任务载体，OCAR 应在这些原生任务上完成领域适配、算子适配和数学表达的实质增量，再证明独有优势。

这取代上一轮“先以完整有限合同为对象、再找领域”的推进顺序。完整有限合同保留为条件化语义规格与验证工具；研究对象从实际领域中的表示、原生动作、可见信息、约束与任务目标中提取。BRFP → OACR 的直接谱系、已成立结果、反循环要求和唯一验收门均保留。

## 1. 真实任务及其原生合同不能统一改写成图任务

| 任务载体 | 本轮核对的实际目标/接口 | 表示及算子适配必须处理的对象 | 共同竞技位置 |
| --- | --- | --- | --- |
| BFCL multi-turn | 逐轮 public backend state 与执行 response 检查；response 使用累计执行记录，不能省成最终答案相同 | agent 历史/工具回执、对象定位、原生状态读写、跨轮依赖；保留官方 checker | BRFP 的直接工具线；先做原生算子适配，新结果与旧 BRFP 任务版本分开 |
| τ² retail / airline | 工具操作加域政策；评价按任务 reward_basis 选择 DB、环境断言、动作/通信等检查，不是统一的单一 DB 指标 | 订单/用户/支付对象、状态相关 guard、确认与一次性写入；来源只能经允许工具/交互取得 | 独立域语义与后续更新检查；旧 τ 结果不混入新版本 |
| τ² telecom | 用户与 agent 都能改变环境，拥有不同工具与观察 | 用户侧不可见更新、当前证据的有效性、信息补取与实际状态变更的区分 | 用于检验“维护器知道全部写入”的假设何时失效；不能免费提供用户私有状态 |
| AppWorld | 任务 evaluation 程序检查实际数据库前后状态与答案；聚合 TGC / SGC | 跨 app 实体、API 输出、代码变量与凭据、任务内状态和跨任务经验；按实际运行状态计费 | ACE / DC / GEPA 在此有原生比较，适合直接检验领域适配；尚未执行 OACR |
| AMA-Bench 与其执行载体 | 主协议从冻结轨迹构建记忆并独立答 QA；v4 另有 TextWorld 与 Spider2 执行实验 | 机器生成对象/状态/因果信息；相同轨迹的记忆构造和工具检索；真实执行另记分母 | AMA-Agent 是直接近邻；可在其原任务比较，但 QA 与持续原生维护证据不能混用 |

以上是现实领域的可执行基准或真实 agent 轨迹，不把模拟基准等同生产部署。此区分不会削弱共同任务的意义。关键是承担原有任务与操作语义，而不是给真实任务套上我们更容易获胜的自定目标。

### 已固定的公开源码修订

- BFCL：`ShishirPatil/gorilla@6ea57973c7a6097fd7c5915698c54c17c5b1b6c8`。
- τ²：`sierra-research/tau2-bench@5bfa7e37b36656b37dc6d022156be6563c1007f3`。
- AppWorld：`StonyBrookNLP/appworld@42b5bcf3cd334fee33f0c37c02070a9f5807add5`。

这些是本轮只读源码审查的复现点，不是已经冻结的实验任务版本、拆分或构造器。本轮未读各基准的任务标签、测试逐例报告或封存单元。

## 2. 比此前更直接的强近邻

| 方法 | 本轮核对的实际机制和任务 | 对 OACR 的设计约束 |
| --- | --- | --- |
| ACE，arXiv 2510.04618v3 | AppWorld 的官方 ReAct 框架上比较；条目化 playbook、增量更新与去重；有不同监督/适配设置 | 增量条目、局部更新、避免整体摘要遗失不能单独当首创；逐项对齐训练与可见反馈 |
| Dynamic Cheatsheet / GEPA | ACE 原文中作为实际 AppWorld 对照；DC 累积经验，GEPA 用反馈优化 prompt | 不把原对照替换为仅随机删记忆；task-local 状态与跨任务策略经验应分层比较 |
| AMA-Agent，arXiv 2602.22769v4 | 用相邻观察/动作提取对象状态与因果关系；图/关键词工具检索；新增原生执行比较 | 因果记忆、前置条件、状态更新、工具补查已是正面对手；不能说它只做静态 QA 或不懂操作依赖 |
| AgeMem，ACL 2026 | 把 LTM/STM 存取、更新、摘要/丢弃纳入策略；在 ALFWorld、SciWorld、PDDL、BabyAI、HotpotQA 比较 | 将保留、补取、删减工具化这一形式已有覆盖；训练后的策略与未训练基线不能当同 backbone 的模块对照 |
| 完整历史、标准实体/版本/依赖维护 | 应在选定原生任务实际实现；可保留全部历史或按有语义的变化刷新 | 长上下文强对照和正确的结构维护都进入比较；不能只与无版本的相似度检索竞争 |

本轮没有复现上述论文的分数，也没有断言它们在 OACR 拟定的所有实时规则上缺少能力。论文结果是选对共同竞技对象的依据，不是 OACR 已经领先的证据。

后续拆解纳入 AdaMEM 的 episode 内策略刷新、MESA 的互补结构选择及
MSS-Complement 的状态条件化充分证据恢复。MESA 全文已读；MSS 只核作者摘要，
不推断其证书或维护能力缺失。AMA 实现保留原始轨迹及回查；ACE 缓存、AgeMem
训练与现 GEPA 的组件优化能力须保留并计费。构建与局限证据见
[强基线拆解](OACR_STRONG_BASELINE_DECOMPOSITION_2026-10-02.md)。这些近邻收紧
宽泛现象/方法的新颖性范围，尚不构成候选核心的最终优先权判决。

## 3. 算子适配应从真实代码提取

### 3.1 文件定位与重绑定：BFCL

核对 `gorilla_file_system.py` 的 `cd`、`cat`、`mv`：`cat(file_name)` 只读取当前目录内的名称；`cd` 改变目录上下文；`mv` 在当前目录重命名或移入目录。原生 `mv` 还可能重建 File/Directory 对象，不能假定 Python 对象 identity 就是稳定领域身份。

适配器应显式表示“定位上下文 + 名称 + 从允许回执获知的对象/内容”关系。只保存名字会丢定位依据；只保存旧内容不提供当前可用位置。此处不要虚构 benchmark 已提供的全局 inode 或免费 namespace 版本。目录、名称、内容及其见证分别保留或更新，并按原生调用的实际结果处理失败。

这些是源码导出的操作义务，不是新的文件系统现象。下一步检验的是同一个需求/维护规则能否由这种语义自动产生正确决定，成本是否优于成熟路径/版本维护。

### 3.2 一次性写入与政策见证：τ² retail

核对 `modify_pending_order_items`：入口要求订单状态精确为 `pending`；成功后变为 `pending (item modified)`，同一修改原语不能简单重试。该函数还检查配对商品、可用性、价格差、支付方式及余额，并写入订单/付款记录。文档要求先解释并得到明确确认，但函数本体没有把会话确认作为独立运行时输入检查。

因此，适配不能把“当前内容”与“仍可执行的动作”当同一对象，也不能把工具 guard 和政策授权当同一谓词。维护器必须更新已消费的动作资格、关联商品/支付事实与可见确认见证；确认的语义解析本身有范围，不能假定自然语言分类器总正确。

此例不是新 typestate 定理。本轮只读代码，没有运行任务、修补第三方实现，或把工具实现问题算为 OACR 新机制。

### 3.3 部分可见的外部更新：τ² telecom

核对用户工具 `toggle_airplane_mode` 及其内部实现：它可同时影响连接、Wi-Fi/VPN 与网络搜索。agent 不因此获得用户侧全部字段。维护器只接收其角色合法可见的消息/回执；未见更新必须进入不确定状态或允许的重新询问流程。

这意味着来源查询不总是“冻结世界上只改变知识”的 membership 问题。具体工具调用或用户行为可以改变环境，适配层要逐项说明。上述动态与部分观察已有 Dec-POMDP 近邻，不能以新增一个变量宣称数学首创。

## 4. 数学表达必须适配真实 agent 接口

图载体中的 `Dec(r)` 可生成一个能原生执行的图；工具 agent 的压缩记忆一般不能生成完整订单库、设备或 AppWorld 环境。因此，原有解码等式只在确有该接口的结构类使用。真实 agent 主线区分：

- x_t：环境实际状态，不默认对维护器可见；
- h_t：角色允许见到的用户输入、工具调用与实际回执历史；
- r_t：部署实际保存的表示，外存、索引、证明和元数据均计费；
- pi：调用 agent/model 的策略；
- T_d、O_d：原生领域的转移与角色观察；
- Phi_d：未经修改的官方任务评分，目标标签/私有断言只在评价端。

一个执行周期可以写为：

\[
 a_t\sim\pi(\cdot\mid u_t,\operatorname{Render}_d(r_t)),
 \qquad (x_{t+1},y_t)\sim(T_d,O_d)(x_t,a_t,w_t),
\]
\[
 r_{t+1}=\mathsf M_d(r_t,u_t,a_t,y_t).
\]

这里 w_t 表示允许的其他参与者/环境事件；隐藏 w_t 不直接传给 M_d。允许的查询本身也是原生动作，必须通过该周期并计费。实际实现可有查询、决策、写入多个子步，此式只是边界规格，不是新算法。

### 4.1 从操作后义务反推当前需求，再正向维护

需要研究的算子接口是：

\[
 \mathfrak D^{\leftarrow}_{d,a}:\mathcal R^{+}\mapsto\mathcal R^{-},
 \qquad
 \mathfrak U^{\rightarrow}_{d,a}:(r,y)\mapsto r'.
\]

R^+ 是后续任务/操作所需的义务，R^- 是当前执行所需的实体绑定、前置条件、值及支持；U 按真实回执更新可用依据。它们须面对绑定替换、状态改变、动作资格消费与不可见更新，不能只把所有调用统一命名为删边。

设 I 为实际可见信息，Compat_d(I) 为相容领域状态/历史。证书 Gamma 的目标至少是：

\[
 \operatorname{Check}_d(I,\Gamma,a)=1
 \Longrightarrow
 \forall(x,h)\in\operatorname{Compat}_d(I):
 \Psi_d(h,x,a,T_d(x,a)) .
\]

Psi_d 明确指定该次操作应保持的绑定、允许性与效应义务；不等于 LLM 一定解好整个任务。若 x 不足以表示会话授权，需要把 h 的相应可见见证纳入 Psi。对随机/双控领域，量化允许后继并使用角色观察；不能默认为确定性、全可见。

这种表达与 weakest precondition、typestate、frame reasoning、抽象细化及信息状态相关。**写下它不是超越。** 数学增量要来自新结构条件、可计算需求变换及其资源界，并在上述真实操作语义下证明；必须与上一轮审查中的结构宽度、符号策略和经典维护直接核对。

### 4.2 新命题应由真实障碍决定

实际候选问题是：能否在有限可见依据下，用绑定与支持交互结构计算一段真实工具操作所需的保留/补取/重写，给出可检查的正确性与成本界，并经适配迁移到不同 API？

下一条定理必须明确多出的结论：是比成熟参数覆盖更广的可处理结构，还是更强可执行保证，还是有证明的计算/完整成本增量。若只是前置条件的回推、版本失效、普通依赖闭包或标准策略合成，归入基础。完整有限合同用于声明证明范围，不能代替这些结果，也不能把任务私有目标提供给构造器。

## 5. 对比设计：适配本身也要接受检验

比较不只问核心选择器是否更优，还要区分三个实际增量：

1. **领域适配**：同一表示维护规则能否支持原任务与原评分，覆盖合法工具和角色可见信息？
2. **算子适配**：是否从原生 API/允许文档及回执推导需求与更新，而不是人工为每个任务补一条成功路径？
3. **数学与算法**：适配后的结构究竟让什么保证或成本界成立，强基线是否已有等价构造？

公平性首先要求相同公开文档、历史、工具权限与反馈。竞争方法可用相同合法结构、预处理、缓存和成熟优化。还应做“共享适配器 + 不同维护方法”的定位比较，以识别收益来自适配还是核心算法。共享一个经检验的新模块并不自动否定该模块的贡献；但不能把共同模块的收益只记给自己的选择器，或遗漏成熟等价适配。

对 ACE 类方法区分跨任务经验 playbook 和本次任务的状态记忆；固定前者时才把差异归给 task-local 维护。训练/reflector 的模型与调用、嵌入/检索、字节、tokens、来源访问、时间、初始化摊销全部报告。端到端原方法与移植变体分别命名；AgeMem 训练策略不能悄悄计为免费同模型能力，EC² 只比较其适用的共同取证子问题。

**AppWorld 的实际开发规则影响适配形态。** 本轮 README 明确禁止在 agent 逻辑中硬编码领域 API 调用，test 集只用于最终聚合评价。不能用固定脚本自动登录/补查，再作为遵守原规则的 AppWorld 分数。优先实现通用回执/上下文维护与向 agent 提供需求说明；由 agent 在允许接口选择调用。若要让构造器直接生成调用，先证明该实现符合其一般 agent 规则，不能通过改规则维持优势。这是具体任务的适配条件，不是要求用户再次批准工作。

## 6. 现在的研究顺序

第一步对象固定为 BFCL 文件操作的定位/重绑定，以及 τ² retail 的一次性订单修改；两者均直接承接 BRFP 的实体、效应与授权。产出其原生接口到需求/更新表示的映射、允许信息与独立验算方式。不是先跑语言模型或先人为寻找成功例。

同时把 ACE/AppWorld 与 AMA-Agent 的真实任务协议纳入共同竞技设计，核对可用实现与资源配置。第二载体检验同一核心算子规则是否成立；不把改写一个领域专用规则当跨系统迁移。

随后只为这批真实算子暴露的结构障碍提出候选定理；优先检查近邻是否已有同等条件和结论。适配正确、独立数学增量、官方任务收益分别验收。没有可独立检验的增量，仍按既定退出规则收为基线；不能以适配工作量、更多图枚举或新符号替代优势。

本轮完成的是源码与原文审查、对象选择和设计修订。适配器、独立证明、新官方任务运行与跨系统收益仍待完成。旧 512 个单元保持封存。

## 7. 原文和源码定位

- BFCL 官方 multi-turn 评价说明：[官方文档](https://gorilla.cs.berkeley.edu/blogs/13_bfcl_v3_multi_turn.html)。
- BFCL 状态/累计 response checker：[固定源码](https://github.com/ShishirPatil/gorilla/blob/6ea57973c7a6097fd7c5915698c54c17c5b1b6c8/berkeley-function-call-leaderboard/bfcl_eval/eval_checker/multi_turn_eval/multi_turn_checker.py)。
- BFCL 文件操作：[固定源码](https://github.com/ShishirPatil/gorilla/blob/6ea57973c7a6097fd7c5915698c54c17c5b1b6c8/berkeley-function-call-leaderboard/bfcl_eval/eval_checker/multi_turn_eval/func_source_code/gorilla_file_system.py)。
- BFCL travel：同一修订的 `func_source_code/travel_booking.py`，只读核对认证与 booking/cancel，不推断未实现的 token 消费机制。
- τ² retail 工具：[固定源码](https://github.com/sierra-research/tau2-bench/blob/5bfa7e37b36656b37dc6d022156be6563c1007f3/src/tau2/domains/retail/tools.py)。
- τ² 用户侧工具：[固定源码](https://github.com/sierra-research/tau2-bench/blob/5bfa7e37b36656b37dc6d022156be6563c1007f3/src/tau2/domains/telecom/user_tools.py)。
- τ² 实际评价入口/环境评价器：同一修订的 `src/tau2/evaluator/evaluator.py`、`evaluator_env.py`、`evaluator_action.py`；[论文 v1](https://arxiv.org/html/2506.07982v1)。论文原实验与现在代码的新模式不能混用。
- AppWorld 评价与开发约束：[评价器](https://github.com/StonyBrookNLP/appworld/blob/42b5bcf3cd334fee33f0c37c02070a9f5807add5/src/appworld/evaluator.py)、[README](https://github.com/StonyBrookNLP/appworld/blob/42b5bcf3cd334fee33f0c37c02070a9f5807add5/README.md)。本轮未取得/执行具体 app bundle。
- ACE：[原文 v3](https://arxiv.org/html/2510.04618v3)，§3、AppWorld 实验与反馈条件；此前 v1 也已读，本文用 v3 修订核对。
- AMA-Agent：[原文 v4](https://arxiv.org/html/2602.22769v4)，§3.1、§5、§6.1、§6.3；不能沿用 v2 的范围描述忽略新增 TextWorld / Spider2 原生执行。
- AgeMem：[ACL 原文](https://aclanthology.org/2026.acl-long.981.pdf)，§3–4.1；本轮核对机制及实际五类任务，不声称已移植到 BFCL/AppWorld。

内部衔接：`OACR_BRFP_CORE_UPGRADE_EXECUTION_2026-10-01.md`、`OACR_COMMON_ARENA_AND_PAPER_DIRECTION_2026-10-01.md`、`OACR_COMPLETE_FINITE_CONTRACT_PRIORITY_AUDIT_2026-10-02.md`、`OACR_OPERATOR_FIRST_FOUNDATION_2026-10-01.md`。唯一门槛仍为 `OACR_FINAL_UPGRADE_ACCEPTANCE_GATE_2026-09-30.md`。
