# OACR：强基线的强度来源、构建与进一步突破

日期：2026-10-02。审查起点：PR #89，`62f2c8cf93e843839a4a3703407d1bf924d1cede`。
状态：原文、公开实现接口与构建条件已核对；论文完整系统、训练与新算子证明尚未完成。

后续子代理实际执行已打通：三位冷启动 actor 完成固定 train 前三项，3/3 原生
成功、6/6 检查通过、16 次代码执行和 131 次 API 调用。三项属于同一场景，未
运行 ACE 反思/curation 或 OCAR 方法对照。实际渲染审计同时撤回前轮默认
no-GT API gold 提示和动态评分反馈的过度推断。见
[子代理执行结果](OACR_SUBAGENT_NATIVE_TASK_EXECUTION_2026-10-02.md)。

后续最小执行已实现经典文件绑定参考，并经预运行冻结完成 7 个人工原生 fixture
的 50 次工具调用审计；65 个已知输出与原生执行一致，85 个需取证、2 个不支持。
这没有复现上表论文系统，也不是新算法或官方任务成绩。范围、候选及完整账本见
[发散探索与谨慎构造](OACR_DIVERGENT_EXPLORATION_AND_NATIVE_CONSTRUCTION_2026-10-02.md)。

后续已从人工 fixture 推进到全部 50 个官方 BFCL base 文件系统开发案例：159 轮、
276 次参考原生调用、73 次实际读取。经典依赖索引与需求回推候选各正确覆盖 19 次，
无原生不一致；各 54 次继续取证，官方规则下各省调用 0 次。作者 AMA 的原始历史/
entity/BM25 accessor 已原样执行，但未运行 AMA 完整模型系统。候选的适配正确性
未产生独有优势，不能升格。见 [真实案例执行](OACR_REAL_BFCL_EXECUTION_2026-10-02.md)。

本轮问题：强基线为什么强，如何保留其实际能力构建共同对照，哪些局限已经有证据，OCAR 可以在哪一层增加独立结果？

结论：保留近邻的经验学习、结构记忆、检索和训练能力，再研究原生操作下的可执行依据维护。新增记忆结构、动态检索或互补集合选择已经有直接近邻。没有维护定理不等于方法实际失败；必须与成熟语义维护和实际端到端任务共同检验。

## 1. 强度分成四层，得分不能直接分摊

| 层 | 实际能力 | 构建条件 |
| --- | --- | --- |
| 输入与反馈 | 原始历史、成功经验、工具文档、回执、标签、反思 | 固定数据/反馈权限与时机、初始化经验；实时任务只用当前可见前缀 |
| 表示与访问 | 详细 playbook、对象/因果图、多种索引、原始轨迹回查 | 记录原文、图、向量、索引、证书、缓存的实际保留与构建/访问成本 |
| 决策与维护算子 | 缺口判断、结构子集选择、存取/删除、原生工具策略 | 固定动作空间、预算、异常处理与适配；允许预处理、缓存和局部更新 |
| 训练与计算 | RL/微调、反思、优化搜索、辅助模型、上下文缓存 | 固定 actor/encoder/reflector/checkpoint；报告训练、冷启动及摊销 |

四层有交互。不能把原论文总增益拆成相加的四个数字，或把训练收益全归给存储结构。

## 2. 方法拆解：强度、构建、局限

| 方法 | 强度来源 | 我们怎样构建 | 局限证据与待检验边界 |
| --- | --- | --- | --- |
| ACE / DC | 从反馈积累详细策略经验；ACE 用条目、反思与增量合并 | 保留经验池、各模型角色、offline/online 与缓存；有标签和仅执行反馈分开 | ACE 作者指出反思须产生有效信息、丰富上下文非普遍需要；同时弱反思/噪声实验有正结果。具体对象状态与授权的维护是待测问题，不能断言一定失败 |
| GEPA | 用反馈反思搜索、选择与组合互补候选 | 使用作者 adapter，允许合理优化程序组件；完整优化预算计费 | 当前实现已有代码/系统组件优化，不能限成只改一句 prompt；平均验证收益不自动给出逐状态保证，这是我们的推断 |
| AMA-Agent | 对象/状态/因果关系与按需扩大检索 | 保留图、embedding、原始轨迹、范围/关键词/脚本回查；QA 与原生执行分开 | LLM 抽取和自评是否满足具体 API 义务待测。源码保留 raw turns，因此抽取遗漏不等于信息永久丢失 |
| AgeMem | 记忆工具与训练策略共同控制 LTM/STM | 真正训练 checkpoint/训练复现及 noRL 条件；固定训练 actor 再比较维护模块 | 作者指出固定工具、受控任务与 HotpotQA 训练范围；已有跨域迁移，不能推断新操作必失败 |
| AdaMEM | episode 内按当前状态检索并合成/刷新策略 | 保留成功训练轨迹索引、HIGH/LOW/MAX、策略模型调用；STEP-MFT 另计 | 作者仓库已覆盖动态刷新；本轮全文访问失败，不作完整优先权或能力否定 |
| MESA | 联合选择随 query 改变的互补结构记忆 | 保留多结构 builder/accessor/composer、固定 answer model 和策略搜索；加入 all-structure/route-to-one/固定子集 | 作者将连续更新及构建/检索/选择/融合联合优化留作扩展；已报告构建成本。实验范围不能解释成原则上做不到 |
| MSS-Complement | 状态条件化、集合级补齐当前决策缺失证据 | 取得完整原文后对齐源池、校准、调用预算、证书和执行范围 | 本轮仅作者摘要已核，全文/代码未取得；不推断证书或后续维护能力缺失 |

MESA 直接覆盖“组件贡献依任务及其他组件改变”的宽泛主张；MSS 摘要直接覆盖“已有支持改变补取需求”。二者必须进入优先权审查，不能将该层概念当 OCAR 独有结果。本轮未复现任何论文分数。

### 原始实现的重要资源条件

AMA 的固定 `construct.py` 保存 `trajectory_text`、解析轨迹、state memory 与可选 graph/embedding；`retrieve.py` 可取得原始 turns 并执行补充搜索。ACE v3 已讨论反思质量与缓存复用。AgeMem 官方 README 中的独立 AgentScope demo 不自动等于论文训练版。只算最终 prompt tokens，会漏掉这些能力的代价；也不能删除对手的回查或缓存来制造胜出。

### 必须主动构建的经典强对照

这是我们设计的组合控制，不冒充一篇已复现论文：完整可见事件日志、正确的实体/位置绑定、类型与动作状态、作用域内确认依据、版本失效、读写集、依赖索引、前置条件回推，以及适用的符号信息状态和增量维护。

允许预处理、缓存与局部更新，不强制逐步枚举世界或重扫全历史。没有公开稳定 ID 时不创造 inode；没有观察外部变化时不免费获取隐藏写入。未知与不存在分开，报错不统一解释成零写入，证据不够时补查或保守回退。若它匹配 OCAR 的保证和成本，新增字段与依赖规则归入基础。

## 3. 构建两组对照

### 原方法完整系统

建立版本胶囊：原文版本、代码 SHA、runner、task/version/split、模型角色与 checkpoint、经验池与反馈、上下文/工具预算、存储和成本。

| 方法 | 只读审查的代码修订 | 已核入口 / 尚未完成 |
| --- | --- | --- |
| ACE | `82709de050e1db6e6ef2f07bcb0393560b94992a`；gitlink `ace-appworld@9f3e92155345a9159f3a8b25abc334eeca05b545` | 主库通用 offline/online/test 与子模块原生 AppWorld runner 均存在。原子模块为 AppWorld `0.1.4.dev0`，已有 ReAct/reflector/curator；不得用当前官方新版冒充原作者复现 |
| AMA-Agent | `ddfd319e0be33424288c13806f1eafc63e625b59` | BaseMethod、ama_agent、construct/retrieve/tool；未执行 QA 或实时环境，native harness 覆盖待核 |
| AgeMem | `98f563f907d67b2f2436e3ae7b7ceff32e482814` | 官方 Trinity-RFT 训练/评价说明及独立 demo；未取得训练 checkpoint 或运行五类任务 |
| GEPA | `fb1ed589fd83372caef499cffc2c73173d3b096b` | `GEPAAdapter.evaluate` / `make_reflective_dataset` 及扩展接口；论文版与现扩展版须分别固定 |

这些不是实验前冻结。AdaMEM 已核作者仓库但尚未 pin；MESA/MSS 的可复用实现尚未核实，不用简化复刻冒充原方法。

AMA README 表明公开数据 test-only；新增开发/校准拆分独立声明，不把同条轨迹的不同 QA 当未见轨迹验证。AppWorld 禁止硬编码领域 API 调用，适配层不能靠固定脚本自动补查来宣称官方成绩。所有原生评分与角色输入不变。

### MOE 冷启动后的入口更正与实际状态

此前未展开 gitlink，因而遗漏了 ACE 的实际原生入口；“未见 runner”不再是当前
结论。子模块已实际固定、取得 LFS bundles，独立环境安装并下载其指定数据。
train 首个原生环境以 `load_ground_truth=false` 启动，执行 2 次公开 API 调用并
正常关闭；没有调用模型、任务评分或 test 实例。42 个作者公开源文件 SHA 对齐，
5 个配置编译、runner/merge 接口核验通过。完整 ACE 闭环仍缺授权模型资源，
`--require-model` 实际返回 2；环境就绪不能写成作者任务成绩已复现。

同日实际模板审计纠正前轮权限推断：源码虽读取 `required_apis/test_report`，
5 份默认 generator 模板均未引用 relevant_apis；默认 no-GT reflector/curator
也没有动态评分报告占位符。改变这些合成 sentinel 不改变实际模型输入；改变可见
历史会改变输入，with-GT 的报告/solution 正对照会改变输入。不得将源码读取直接
写成 actor/reflector 得到先验。作者原配能力与实际模型输入分开声明，详见
`experiments/oacr_moe/prompt_authority_audit/AUTHOR_PROMPT_AUTHORITY_AUDIT_2026-10-02.json`。
子模块实现的是 ADD 合并，不能直接代表论文 v3 的全部 grow/refine/dedup 增强。
offline evaluation 默认产物有缺失/空文件，先从合法 train 生成经验；online
test 学习的现成 playbook 不作我们的开发起点。

详见 [冷基线报告](OACR_MOE_COLD_BASELINES_2026-10-02.md) 与
`experiments/oacr_moe/baseline_capsule/NATIVE_APPWORLD_SMOKE_2026-10-02.json`。
AMA 完整图/embedding/actor 与 AgeMem 训练 actor 仍未运行，旧 accessor 结果不
替代它们。上述准备没有给当前候选补出独有优势。

### 共享适配后的维护模块

保留 ACE 的策略经验、AMA 的提取/检索、AgeMem 的训练 actor。比较原方法、加经典维护、加候选 OCAR 维护；再在共享合法适配器上比较经典与候选内核。原端到端方法与移植变体分别命名。

部署接口为：接收角色可见回执 → 构建/维护表示 → 准备候选操作所需上下文 → actor 选择允许的原生调用。私有任务状态/目标只在评价侧。适配语义不能只免费给自己。

共享新的经检验模块不自动否定模块贡献；收益归给实际改变的部分。若经典等价模块也同样改善，不能将收益归给新内核。总成本包含训练/优化、构建、全部模型调用与缓存命中、外存/索引/图/证书/缓存字节、检索/来源/工具访问、写入/重算与时间。跨任务评分不并成虚假的同分母胜率。

## 4. OCAR 的具体候选内核

继承 BRFP 的实体、效应与当前授权。表示保存合法取得的事实、作用域内绑定、当前动作资格、来源见证与支持关系；原始历史是否继续保留明确计费。

从原生代码审查与允许文档提取绑定、guard、读写效应、角色观察及异常义务。需求算子 D 对指定操作/声明的后续操作族回推所需依据；更新算子 U 按实际回执维护绑定、资格与支持。成功、失败、部分写入与未见事件分开处理。自然语言确认识别不假定总正确。

输出分三类，避免将技术失败包装成不可解：

1. 已验证依据：在已证明 sound 的语义片段内验证指定绑定/guard/效应义务。
2. 实质歧义：相容但义务判断不同的状态/历史见证；寻找允许查询，不能合法区分时才报告信息不足。
3. 检查未完成：规格不支持、超限或证书失败，不称为信息论不可解。

先在 BFCL 文件重绑定与 τ² 一次性订单修改适配同一规则。记忆不能解码隐藏环境，检查器标签不能驱动取证。完整有限合同只声明证明范围。

## 5. 更进一步必须多出的结果

候选性质是：明确操作/观察条件下，当前义务的合法依据经 U 更新为后继义务的合法依据，或明确暴露不能维持的部分。它只覆盖所列操作义务，不保证 LLM 完成整个任务。原生执行、政策及官方评分另验。

一般前置条件回推、typestate、frame reasoning、信息状态与增量依赖维护已是基础。理论突破须增加可计算的构造、区别于已有参数的可处理结构，或同保证下的计算/完整成本界，并在原任务产生收益。结构参数必须由合法输入计算，不能由答案定义。局部更新界须收费初始化、索引、证书变化和定位受影响区。

相容状态不可区分论证可作必要取证下界，但本身不是新定理。DAG 的旧逐状态最优/局部维护结果不直接迁移到别名、资格消费或双控更新。

最有希望的待检验问题是：能否联合编译所需依据、来源补取与后继维护，让有效支持的变化决定局部工作，并减少完整历史/信息状态恢复？MESA、MSS 与成熟符号/维护方法都参与分离。该问题尚未证明新颖、可解或更优。

## 6. 最小推进与退出

先实现正确的经典维护和两个原生适配，再实现候选 D/U/证书。冻结可见输入、适用片段、配置、成本与独立原生检查后执行；本轮无训练或基准运行。端到端方法产生不同未来轨迹时，不能用单一冻结轨迹重放冒充闭环收益。

第二领域检验同内核是否需要改规则。适用片段、回退、检查失败、真实信息不足与非法操作分开记账，始终保留全任务官方分母。若经典维护正确且全成本追平，归入基础；若只胜过记忆检索而与经典维护持平，只支持适配价值，不升格核心算法。旧 512 个单元保持封存，旧退出决定及 T/I/N 要求不变。

## 7. 原文与衔接

- [ACE v3](https://arxiv.org/html/2510.04618v3)：§3、§4.6–4.7、§5、App. A.4；[固定实现](https://github.com/ace-agent/ace/tree/82709de050e1db6e6ef2f07bcb0393560b94992a)。
- [DC 原文](https://aclanthology.org/2026.eacl-long.333/)；[GEPA ICLR 入口](https://proceedings.iclr.cc/paper_files/paper/2026/hash/0e9e708b6f48e14fd0ac29e167413f76-Abstract-Conference.html)、[固定实现](https://github.com/gepa-ai/gepa/tree/fb1ed589fd83372caef499cffc2c73173d3b096b)。
- [AMA v4](https://arxiv.org/html/2602.22769v4)：§5、§6.3；[固定 constructor](https://github.com/AMA-Bench/AMA-Bench/blob/ddfd319e0be33424288c13806f1eafc63e625b59/src/method/ama_agent_core/construct.py)、[retriever](https://github.com/AMA-Bench/AMA-Bench/blob/ddfd319e0be33424288c13806f1eafc63e625b59/src/method/ama_agent_core/retrieve.py)。
- [AgeMem](https://aclanthology.org/2026.acl-long.981.pdf)：§3–4、Limitations；[固定实现](https://github.com/y1y5/AgeMem/tree/98f563f907d67b2f2436e3ae7b7ceff32e482814)。
- [AdaMEM 作者仓库](https://github.com/yunx-z/AdaMEM)、[摘要](https://arxiv.org/abs/2606.05684)：全文未取得。
- [MESA v1](https://arxiv.org/pdf/2608.10108)：§3–4、App. G，全文已核，未复现。
- [MSS-Complement](https://arxiv.org/abs/2609.20050)：只核作者摘要，全文/代码待取得。

前序：[真实领域与算子适配](OACR_REAL_DOMAIN_OPERATOR_ADAPTATION_2026-10-02.md)、[机制协议](OACR_PHENOMENON_AND_MECHANISM_PROTOCOL_2026-10-01.md)、[优先权审查](OACR_COMPLETE_FINITE_CONTRACT_PRIORITY_AUDIT_2026-10-02.md)。唯一门槛：[Acceptance Gate](OACR_FINAL_UPGRADE_ACCEPTANCE_GATE_2026-09-30.md)。
