# 缓存与零阶编辑：候选预检契约

日期：2026-10-01。状态：P0 的固定输入 / 单 token 注入组件检查已执行；完整编辑管线和全成本门槛未执行，不是方法验收。结果与路线判决见 [已执行的机制探索](OACR_CACHE_RESPONSE_MECHANISM_EXPLORATION_2026-10-01.md)。

## 研究对象与继承边界

本候选是共同母问题的一个载体。先从缓存块、编辑注入、前向调用、来源获取与重算算子定义需求和成本；公共接口与上层数学见 [算子出发的基础规格](OACR_OPERATOR_FIRST_FOUNDATION_2026-10-01.md)。下列近邻提供可检验的机制与强基线，不决定我们的维护器定义。

考察优化过程中的实际损失差，而非当前回答的等价类。允许控制器查询训练输入的 fresh/cached 损失，但查询、刷新和任何额外存储必须全部计入成本。任务评估答案不参与刷新策略设计。

[MobiEdit，ICLR 2026](https://proceedings.iclr.cc/paper_files/paper/2026/file/2b35d186908df6fa14a51ba1cae9dc4e-Paper-Conference.pdf) §2.4/§3.3 是具体问题入口。[CacheReforge](https://arxiv.org/html/2609.30884v1) 已研究演化适配器的自适应推理缓存修复，不独占自适应刷新。[Certified Multi-Fidelity Zeroth-Order Optimization](https://arxiv.org/abs/2308.00978) 已研究不同成本/精度的函数评估与认证；一般多保真优化不属于本候选的新贡献。[QZO](https://arxiv.org/html/2505.13430v2)、[AGZO](https://openreview.net/forum?id=zfVxpXEZti)、[ZO-Act](https://arxiv.org/html/2607.01125v1)、[AIM-ZO](https://arxiv.org/html/2609.35257) 是优化侧必须追查的近邻，适用的计算算子和更新参数要分别核对。

## 已完成的源代码定位

官方库：[UbiquitousLearning/MobiEdit](https://github.com/UbiquitousLearning/MobiEdit)，读取提交 `5a07b7906baa5457c15bd86cc012b1993ef6d3c6`（2026-03-01）。以下文件下载后按 git blob 算法核对一致：

| 相对 models 目录的路径 | git blob SHA |
|---|---|
| `rome/rome_main.py` | `77abe4fdd333bae0832776da34e8489f5102d455` |
| `rome/compute_v.py` | `9892b4799bc499c36cb25de9ac74c81b9a9f8961` |
| `rome/zo.py` | `986f6c63f88f1a7fc22f5f6f8fa1b22f9411297c` |
| `rome/rome_hparams.py` | `294f32eede644530689867440585a7ad246c34d9` |
| `quantization/quantizer.py` | `3887a0c69e53831eb590fff17ded4f47761aa098` |

`rome/modeling_qwen2.py` 已通过 git 获取完整原始文件，blob 与上游 `defdad8cd04a5366016b5b6185b014af24d1784f` 一致。早先检索文本字节不完整的问题已解决；原生组件已在匹配的 Transformers 4.44.2 下运行。

静态读取发现：

- `rome_main.py` 根据 `use_zo` 选择 `compute_v_zo`；不能把另一条实验函数当作默认实现。
- `ZOTrainer.zero_order_loss` 在 `lookup_idxs` 指定的 MLP 输出位置注入编辑向量，不是每个扰动都改变全部模型权重。
- 缓存启用分支传入 `prefix=10`。刷新条件读取两条 loss 记录；原文描述与仓库代码应分别标注，不能混成同一冻结实现。
- `compute_v_zo` 构造重写提示和 `"{} is a"` 的 KL 提示。不同 batch 行的编辑位置可能不同，必须逐行核对缓存边界。
- 所读量化器包含校准后固定的量化参数路径。量化本身不自动打破因果前缀的不变性；需检查实际 hook 顺序、校准状态、clipping 和执行内核。
- calculate_jvp 依次调用 center、minus、plus 的损失。zero_order_loss 可初始化 target/KL 状态并调用缓存刷新分支。配对评估需记录这些可变状态，不能把每次调用默认为同一个静态函数。这是定位事实，不是已测得顺序偏差。

以上静态检查与本轮运行结果分别标注。已导入未修改的官方模型组件、测量诊断损失；尚未建立默认 AutoModelForCausalLM 编辑入口如何加载该组件，未运行官方完整训练器或复现原论文数值，不能据此宣布论文 bug。

## P0：最便宜的可推翻检查

运行环境已建于独立依赖环境：Python 3.12、Torch 2.5.1+cpu、Transformers 4.44.2、NumPy 1.26.4。官方模型源文件、预训练权重和 tokenizer 的固定版本及哈希已记录；量化路径尚未运行。下列完整 P0 义务不能因局部组件检查完成而全部标为通过。

对相同训练输入、编辑向量、方向、扰动尺度和 RNG 状态比较：

1. 完整 fresh 执行。
2. 仅复用经依赖检查证明不受该 token 注入影响的前缀/层。
3. 官方启用缓存的执行。

逐 batch 行记录 token、attention mask、编辑位置、实际缓存边界、缓存生成状态、量化参数与刷新分支。覆盖编辑位置在缓存之前、之内、之后，以及模板变化、batch 行序变化和连续编辑；这些是预先声明的机制条件，不是独立自然任务样本。

先控制初始化/量化/随机性导致的差异，确认差异能由缓存的特定受影响状态解释。fresh 对照不能更新后续原生运行的缓存、target/KL 初始状态、锚点或 RNG。比较固定锚点的配对执行、完整原生 center/minus/plus 顺序，以及交换 minus/plus 的执行；统一扰动方向与尺度，分别记录实际状态变更，不能在原生分支中静默改掉状态行为。

本轮先建立独立于新修复方法的现象与机制预测，再测方法收益；观察协议及贡献边界见 [现象与机制协议](OACR_PHENOMENON_AND_MECHANISM_PROTOCOL_2026-10-01.md)。精确因果不受影响区是现象消失的对照，不保证会出现新现象。

**P0 的判决：**

- 若完整执行与精确因果复用一致，而且后者已满足成本目标，停止“需要学习刷新”的假设。
- 若只由错用 token 边界、mask、batch 身份或遗漏失效处理解释，先归为实现修复；不自动成为新方法论文。
- 若正确的精确复用仍留下显著成本障碍，再进入 P1 的多保真控制候选。
- 若官方实现不能完整运行，标记工程阻塞，不把不可复现当作科学负结果。

**本轮执行后的局部判决：** 96 个小模型配置中，缓存内早层的 32 个配置全部出现 fresh 非零、固定缓存为零的损失差分；其余条件符合因果边界和最后层对照。一个预训练模型的 12 个手工探针也支持该结构，其中缓存内早层的 4 个探针全部失去响应。精确因果复用消除结构性问题；预训练的数值差异由完全 fresh 的相同矩阵分块逐值复现。因此暂停此固定输入、定权重、单 token 场景的学习型刷新方法主张。没有测得精确复用后的全成本障碍，暂不进入 P1。

固定同一锚点的 288 个小模型执行变体没有配对顺序差异。真实训练器的 target/KL 状态、刷新、逐行位置差异、mask/模板/batch 身份变化、连续编辑、量化及硬件成本仍未覆盖。接口异常单独报告，不替代这些检查。

## P1：需要控制什么误差

此节保留为条件性候选，不是本轮已启动的方法实验。[On Adaptivity in Zeroth-Order Optimization](https://arxiv.org/html/2605.03869v1) §4.2 / Appendix F 已使用安全上游激活复用。[Wall-Clock Complexity for Zeroth-Order Optimization with Tunable Oracle Fidelity](https://arxiv.org/html/2605.31346v1) §7 明确未计精度切换成本；缓存重建的历史成本可以作为待筛查问题，尚未建立新颖性。

固定某一缓存状态 C 和当前训练点 v，用相同方向 u、尺度 epsilon 比较

`D_fresh = [L_fresh(v+epsilon*u)-L_fresh(v-epsilon*u)]/(2*epsilon)`

`D_cached = [L_C(v+epsilon*u)-L_C(v-epsilon*u)]/(2*epsilon)`。

令两侧 loss 误差分别为 e+、e-，则差值为 `(e+ - e-)/(2*epsilon)`。这是代数恒等式，不是新定理。低的单次 loss 误差不必意味着扰动差可靠；公共误差也可能抵消。直接测量配对差，而不是只看激活余弦或缓存年龄。量化路径可能不光滑，此处比较有限差分，不假定存在普通梯度。

待筛查的控制器用冻结频率的 fresh 配对探测估计差分误差，决定复用或刷新，并与普通多保真校正比较。阈值、频率、可见输入和候选刷新区域必须在相应独立结果暴露前冻结。实际探测预算可由独立成本开发集确定，不能事后挑最好的成本点。

## P2：什么结果才值得写成论文

在同一墙钟/完整前向预算、同一存储预算与同一输入下，比较完整 fresh、精确因果复用、官方刷新、固定频率、随机成本匹配和适用的多保真/CacheReforge 基线。不能只胜过永不刷新的旧缓存。

主要任务指标是编辑有效性、泛化及对无关知识的损伤；缓存 loss、方向符号和误差用于解释机制。全成本包括探测、校准、重新生成激活、锚点和 peak memory。若没有真实端侧硬件测量，就不报告手机能耗或 NPU 延迟优势。

开发阶段先估计成本与成对差异，再冻结至少两个模型及独立任务/来源簇的确认性方案。有限机制条件、随机种子、重复调用不能充当独立任务数量。旧 GRACE 开发结果和 512 单位封存评估不迁移为本问题的证据。

若普通因果缓存、固定频率或已有多保真办法达到同样收益，停止新方法主张。只有需要新机制、独立任务有实际收益、全成本优势成立且近邻边界清楚，才提升为主线。
