# OACR MOE：冷启动强系统入口与可执行准备

日期：2026-10-02。审查起点：PR #89 head `dde1d4da9471ed0e2485c6b8ae549c1dbbb7d282`。
独立冷基线审查；不读取旧 512 封存单元，不使用任务 gold 驱动 producer。

**权限勘误（同日后续审计）：此前从“源码读取字段”直接推断“actor 收到 API 先验、
no-GT reflector 收到 evaluator 报告”，判断过头。** 5 份原配配置都不把
`required_apis` 渲染进 generator 输入；两份 no-GT adaptation 配置的 reflector/curator
也不接收动态 `test_report` 内容。第 3 节以实际公开模板渲染和原方法合成 sentinel
审计更正。旧冻结预检结果保持原样；其中的权限推断不能再当作有效证据。

**今天能实际开始的是 ACE 作者发布的原生 AppWorld 训练入口及其配置/接口准备。**
此前“ACE 固定树未见 AppWorld runner”的判断遗漏了 Git submodule，需要更正：
`ace-agent/ace@82709de050e1db6e6ef2f07bcb0393560b94992a` 的 `ace-appworld`
gitlink 指向 `9f3e92155345a9159f3a8b25abc334eeca05b545`，子模块确实有原生
ReAct、反思、增量 playbook 合并、offline/online 与 GT/no-GT 配置。

本轮执行了 42 个作者源文件的精确 Git blob 校验、20 个 Python 文件语法检查、
5 个 Jsonnet 配置编译、原作者 runner 的 3 个分支接口及原作者 playbook 增量合并。
模型调用 **0**，原生任务 **0**，没有复现论文成绩。模型缺口被保留为可检测阻断，
不是用 BM25、边界替身或参考答案回放补成“完整强系统已跑通”。

## 1. 原方法为什么强，以及怎样保留其能力

ACE 的强度是 actor 在真实 API/代码环境中执行，从当前和既往任务的成功/错误学到
可复用策略；独立 reflector 提取细节，curator 产生条目增量，以程序合并保存旧经验。
这不同于只按相似度找几条历史。原文 v3 还讨论 grow-and-refine、语义去重、弱/噪声
反思和缓存复用；不能删除这些能力再宣称候选胜过“ACE”。论文用相同 backbone
配置 Generator/Reflector/Curator；这里也必须保留三个角色及它们的全部成本。

原生对照入口的完整性有一个版本界限：本次固定子模块有完整 native rollout +
reflection + curation，但其 `playbook.py` 实际只实现 `ADD`，其他编辑操作标为 TODO；
计数已移除，未见其实现语义 embedding 去重。论文 v3、主 ACE 库和这个发布的
AppWorld runner 不能混成一个已经验证的版本。准确命名是“作者公开 AppWorld runner
复现”；论文 v3 全部增强尚未完成一一对齐。这是源码边界，不是 ACE 能力否定。

| 对照 | 保留的真实能力 | 完整运行仍需的资源 |
| --- | --- | --- |
| ACE 作者原生 AppWorld runner | 真实 ReAct 代码/回执循环、完整 prompt 示范、初始/学习 playbook、任务后 reflector/curator、原生评价及缓存 | 定制 AppWorld 源和 LFS bundles、数据 `data-0.1.0.bundle`、实验包、授权的三个角色模型、实际 token/成本日志 |
| AMA-Agent 完整 QA 系统 | LLM state extraction、可选 causal graph、embedding 初取、LLM sufficiency、自选图/范围/代码补查、原始完整轨迹、回答及独立 judge | 模型接口或 checkpoint、embedding 服务/模型、作者数据与独立拆分说明、完整 construct/retrieve/answer/judge runner |
| AgeMem 训练版 | RL 学到的 LTM/STM 存取/更新/删减策略；不能用无 RL demo 代替训练 actor | Qwen2.5-7B-Instruct、真正训练 LoRA checkpoint、HotpotQA fullwiki、Ray/Trinity/verl/vLLM、训练/评价资源和 DashScope judge/干扰生成接口 |

AMA 的 BM25/accessor 是诊断组件；已有 BFCL 73 reads 的数字不代表这张表的完整方法。
AgeMem 的 AgentScope demo 也不代表训练后的论文系统。

## 2. 已核准的 ACE 原生入口和版本

作者子模块的 `pyproject.toml` 明示 **AppWorld `0.1.4.dev0`**、Python >=3.11。
它是作者定制 source tree；README 明示不要用 `pip install appworld` 替代。
此前另核对的官方 `StonyBrookNLP/appworld@42b5bcf3cd334fee33f0c37c02070a9f5807add5`
是 `0.2.0.dev0`，因此在该新版启动环境或移植 ACE，不等于复现这个作者版本。
两版必须各自固定 evaluator、数据、API 和配置，不混用成绩。

作者安装路径如下；没有 GPU 也可运行环境及远端模型调用。本子任务没有安装大套环境。

```bash
git lfs install
git clone https://github.com/ace-agent/ace-appworld.git /tmp/ocar_ace_appworld
git -C /tmp/ocar_ace_appworld checkout 9f3e92155345a9159f3a8b25abc334eeca05b545
git -C /tmp/ocar_ace_appworld lfs pull
cd /tmp/ocar_ace_appworld
export APPWORLD_PROJECT_PATH=/tmp/ocar_ace_appworld
python -m pip install -e .
appworld install --repo
python -m pip install -e './experiments[simplified]'
appworld download data
```

README 用 bare `pip install -e .` 安装 experiments；源码 `experiments/setup.py` 则把
`joblib/jinja2` 放在 simplified extra。上面明确安装该 extra，避免 native ReAct 缺依赖。
`src/appworld/download.py` 精确指向 `data-0.1.0.bundle`，不是任意最新版数据。
GitHub 的 `.source/*.bundle` 是 LFS 指针；仅下载小文本树不能使环境可运行。

合法开发入口是：

```bash
appworld run ACE_offline_no_GT_adaptation
```

它由 `experiments/code/ace/run.py:run_experiment` 分派到 `StarAgent`，再按注册类型
选择 `ace_adaptation_react`。代码真正创建 `AppWorld`、把模型生成的 Python 送入
`world.execute`、取得原生回执、反思并更新 playbook。此“offline adaptation”是在
**train 上逐任务闭环执行，然后跨任务积累经验**，不是一份监督 QA 文件的离线回放。
主 ACE 库 `ace/ace.py` 的通用离线监督接口是另一入口，不能拿它冒充原生 AppWorld。

| 原始配置 | 数据 | 行为 | 发布树输入是否齐全 |
| --- | --- | --- | --- |
| `ACE_offline_no_GT_adaptation` | train | native ReAct + 任务后反思/curation，1 epoch，40 steps，`use_gt_code=false` | prompt/初始 playbook 齐全；待环境/模型 |
| `ACE_offline_with_GT_adaptation` | train | native ReAct + compiled solution 辅助，GT 分支至多 5 retries | prompt/初始 playbook 齐全；不得和无解法输入条件混计 |
| `ACE_offline_no_GT_evaluation` | test_normal | 固定训练 playbook 的 native ReAct | 引用 `appworld_offline_trained_no_gt_playbook_deepseek_3_1.txt`，发布树不存在；须先训练生成 |
| `ACE_offline_with_GT_evaluation` | test_normal | 固定训练 playbook 的 native ReAct | 指向发布树 0 字节 playbook；没有可用的已训练内容 |
| `ACE_online_no_GT` | test_normal | 每例预测后再更新 playbook | 初始输入齐全，但属于作者 online 测试协议，本轮不做开发/逐例分析 |

原配三个角色均 `DeepSeek-V3.1` / SambaNova / temperature 0 / cache true。
配置写 seed 100，但有效 API 实现把 seed 等部分字段注释掉；不能声称实际下发了 seed。
运行预算原配整体 1000、每任务 10 的费用单位，必须结合实际 provider/model 价格校准。
不能把 unknown-model 的费用追踪警告当作真实零成本。

## 3. 实际模板渲染权限：修正源码字段推断

`adaptation_react.initialize` 和 `evaluation_react.initialize` 确实读取
`world.task.ground_truth.required_apis`，并把其字符串放进 `template_params`
的 `relevant_apis`。**这不证明模型接收该字段。** 5 份默认配置都选择同一
`appworld_react_generator_prompt.txt`；该模板没有 `relevant_apis` 引用，Jinja 实际
undeclared variables 仅为 `app_descriptions/input_str/main_user/playbook`。
替换两种合成 required-API sentinel 后，原 `initialize` 的 actor messages 和原
`trimmed_messages` 所准备的首次 generator 输入均完全相同，sentinel 均未出现。

no-GT 的任务结束分支也确实调用 `evaluate_task` 并保存 `self.test_report`，随后
调用 curator。但默认 `appworld_react_reflector_no_gt_prompt.txt` 没有
`{{test_report}}` 或 `{{ground_truth_code}}` 占位符，原 `reflector_call` 的这些
`str.replace` 没有把字段插入 prompt。原 curator 模板也没有 report/gt 占位符。
在原 reflector/curator 方法中改变合成 report 内容，两个实际待发送输入均不变、
sentinel 均未出现；改变可见执行历史则两个输入都变化，作为正对照。

| 默认配置 | required-API 字段读取 | required-API 内容进入 generator | 动态 evaluator 报告进入 reflector | compiled solution 进入 reflector |
| --- | --- | --- | --- | --- |
| `ACE_offline_no_GT_adaptation` | 是 | 否 | 否 | 否 |
| `ACE_offline_no_GT_evaluation` | 是 | 否 | 无该模型角色 | 无该模型角色 |
| `ACE_offline_with_GT_adaptation` | 是 | 否 | 是 | 是 |
| `ACE_offline_with_GT_evaluation` | 是 | 否 | 无该模型角色 | 无该模型角色 |
| `ACE_online_no_GT` | 是 | 否 | 否 | 否 |

with-GT reflector 是有效的正对照：它确有 report/solution 占位符，分别改变两种
sentinel 会改变 reflector 输入。curator 可经真实 reflector 的输出间接接收 GT
推导；本审计使用固定合成 reflector 回复，所以不据 curator 的不变断言该间接
路径不存在。上表仅说明当前默认模板与对应字段的动态传播，不声称静态示范、
作者初始 playbook 或训练经验不包含任务知识。

no-GT 的 evaluator 调用仍存在于控制平面：源码是在
`world.task_completed() or cost_tracker.exceeded()` 成立后赋值报告，才调用 curator；
`solve_task_wo_gt` 后续没有读取 `test_tracker.failures` 或 `self.test_report` 控制
重试/结束。若仅耗尽 max_steps 而未触发该条件，也不会自动进入这个 curator 分支。
reflector/curator 的有效默认反馈是模型可见的 `trimmed_messages` 执行历史和反思，
不是 evaluator 报告内容。我们没有运行 evaluator 或 native 循环。

修正后的共同权限条件因此是：默认 no-GT 对照没有动态 API oracle 或 grader report
输入，不需要凭旧推断给 OCAR 免费增加它们。共享经典/候选维护仍只接受角色合法
可见的历史回执。若改模板引用这些字段，应重新审计并准确命名输入条件；评价标签
不能实时生成候选调用或“证据”。

审计代码和实际结果位于 `experiments/oacr_moe/prompt_authority_audit/`，共核对
12 个公开源文件的精确 Git blob、5 份 Jsonnet 配置和 Jinja 变量；直接执行原公开
`initialize/reflector_call/curator_call` 方法的渲染段，0 模型请求、0 benchmark
任务/答案/DB 读取。替身 transport 截获 curator 的待发送输入并抛出明确的停止信号，
在 JSON 解析/merge/写 playbook 之前停止；只保存布尔差异、哈希和变量名，不保存
原模板/渲染消息内容。该渲染审计不证明模型会如何使用输入，也不覆盖另换模板、
初始化外手动插入标签或完整 native 异常/终止路径。

```bash
python -m pip install --target /tmp/ocar_prompt_audit_deps \
  -r experiments/oacr_moe/prompt_authority_audit/requirements.txt
PYTHONPATH=/tmp/ocar_prompt_audit_deps \
python experiments/oacr_moe/prompt_authority_audit/audit_author_prompt_authority_v1.py \
  --source-root /path/to/pinned/ace-appworld \
  --output /tmp/ocar_author_prompt_authority_audit.json
```

实际结果：[公开模板权限渲染审计](../experiments/oacr_moe/prompt_authority_audit/AUTHOR_PROMPT_AUTHORITY_AUDIT_2026-10-02.json)。
旧 `AUTHOR_ACE_PREFLIGHT`、manifest 和 train 配置生成器里相应推断性字段/日志保留为
冻结历史，本轮不改写；它们不能覆盖本次实际渲染证据。

强对照的三臂应是同一 native actor、同一学习过的 ACE playbook/反思预算，分别：
作者 task-local 上下文、加入共享经典维护、加入候选维护。维护器只消费该角色过去
实际可见的调用/回执；由同一 actor 生成 native 调用。不能把标准绑定/失效/依赖
规则只免费给候选，也不能把官方检查器输出作为在线 producer 输入。
这三臂的维护 hook 尚未在作者 runner 实现；本胶囊没有声称已经形成闭环增益。

`lite_llm_generator.py` 另含一个作者公开源码里的凭据字面量。本轮没有使用或复制到
报告或作为资源；预检只报告存在且 redact。有效调用分支按 provider 创建环境凭据
客户端。当前没有相应 API 环境凭据；配置 `provider=openai` 可沿该实现的
`OPENAI_BASE_URL` 路线连接已授权的兼容端点，但本轮没有端点或调用。

## 4. 今天已直接执行的可复用胶囊

目录：`experiments/oacr_moe/baseline_capsule/`。

| 文件 | 可执行内容 |
| --- | --- |
| `author_ace_manifest_v1.json` | 父库/gitlink/ref、定制版本、42 个文件的 Git blob SHA/大小、模型与权限条件 |
| `prepare_author_ace_v1.py` | 下载并逐文件校验小型公开作者源子集；不下载模型或任务数据；完整 native 安装仍需作者完整 LFS checkout |
| `preflight_author_ace_v1.py` | 源哈希、Python AST、Jsonnet 编译、配置路径、权限和环境布尔检查；原作者 runner/merge 接口执行；从不请求模型或加载真实任务 |
| `write_author_ace_train_config_v1.py` | 编译作者 no-GT native train 配置，限制公开 train 前缀，保持三个角色同模型，把学习产物写到隔离 scratch；不改作者 Python |
| `preflight.requirements.txt` | 唯一新增轻依赖 `jsonnet==0.21.0`，本轮实际下载 wheel 为 6.5 MB |
| `AUTHOR_ACE_PREFLIGHT_2026-10-02.json` | 实际结果和配置输入 readiness；不能称任务成绩 |

在本任务独立 scratch `/tmp/oacr_moe_cold_sources/` 实际准备了作者源；连接器返回
文本附加的换行已去掉，并逐文件对齐原 Git blob，未修改作者实现。
之后又在全新目录实际执行下载器：42 个文件从固定 raw URL 下载、42 个 blob 校验
通过、复用 0 个文件、模型下载 0 bytes、任务数据读取 false；下载器不只通过复用检查。

```bash
# 以下从 OCAR 仓库根目录执行。只有轻预检依赖，无模型安装。
python -m pip install --target /tmp/ocar_ace_preflight_deps \
  -r experiments/oacr_moe/baseline_capsule/preflight.requirements.txt
python experiments/oacr_moe/baseline_capsule/prepare_author_ace_v1.py \
  --dest /tmp/ocar_ace_preflight_source
PYTHONPATH=/tmp/ocar_ace_preflight_deps \
python experiments/oacr_moe/baseline_capsule/preflight_author_ace_v1.py \
  --source-root /tmp/ocar_ace_preflight_source \
  --output /tmp/ocar_ace_preflight_result.json --require-model
```

`--require-model` 在本环境实际返回 **2**，明确表示原配模型凭据缺失。
普通预检返回 0 只表示源码/配置编译/接口核验成功；配置 readiness 矩阵仍明确标记
两条 evaluation 的训练产物缺失/为空，runtime 也不伪称完整 environment ready。
模型凭据布尔存在也不等于 endpoint 可用；本预检不探测或调用 endpoint。

已执行的原 `run_experiment` 接口覆盖 adaptation/evaluation/non-ACE 三个分支、
sample_size 和 epoch 参数；其 loader/agent 边界替身是惯性接口测试，加载真实任务 0。
原 merge 函数保留初始 8 条 bullet 并添加 1 条通用 sentinel；它仅验证确定性合并，
不验证 reflector 学习质量，也不把 sentinel 保存为实际策略经验。

在完整安装的作者 checkout 上，下一步可直接写出并运行单个 train 开发任务：

```bash
PYTHONPATH=/tmp/ocar_ace_preflight_deps \
python experiments/oacr_moe/baseline_capsule/write_author_ace_train_config_v1.py \
  --source-root /tmp/ocar_ace_appworld \
  --dest /tmp/ocar_ace_appworld/experiments/configs/OACR_ACE_train_smoke.jsonnet \
  --artifact-root /tmp/ocar_ace_train_artifacts --sample-size 1
cd /tmp/ocar_ace_appworld
APPWORLD_PROJECT_PATH=/tmp/ocar_ace_appworld appworld run OACR_ACE_train_smoke
```

配置写出已实际执行并重新编译。`--model/--provider/--openai-base-url` 可使用已有授权
模型；换 backbone 必须命名为作者方法复现变体、对各臂一致配置。没有凭据时停止在
明确资源阻断，不建账号、不取 key、不下载大模型、不发生付费调用。

## 5. 数据、许可与已发布轨迹能否用来冷启动

AppWorld 官方规则允许 train 用于学习/示范/手动分析，dev 用于调参/分析；两类 test
只用于最终 aggregate，不看逐例报告、不做调参。禁止在 agent 逻辑硬编码领域 API
调用；可以给通用 prompt 提示。因此共享适配器可维护证据/提出需求，但不能替 actor
写固定登录/取证脚本，再把其成绩称符合原规则。

作者 ACE 代码公开部分是 Apache-2.0。AppWorld 的 app/task/API 文档/DB/答案等
protected bundle 部分是 Apache-2.0 加“公开再分发或派生品须加密”要求；可以本地运行
公开开发资产，但不要把解包 task/DB 原文或派生完整轨迹明文加入公开 PR。这里只保存
公开源引用、哈希、权限和聚合，不保存 protected 任务内容。

| 已发布资产 | 本轮核到什么 | 可用范围/实际取得情况 |
| --- | --- | --- |
| ACE 子模块初始 playbook | 1469 bytes、8 个解析 bullet、Git blob `099f914ec56dcbf7ea227161ee8c78eaaf13d4f0` | 作者初始经验已下载并做接口核验，可固定为所有臂的起点 |
| ACE 子模块 online trained playbook | 130120 bytes | 文件已发布，配置是 test_normal 的 online adaptation；本轮不审查逐条学习内容，不当开发初始化，不冒称原始执行轨迹 |
| ACE offline trained no-GT 文件 | 另有 1723 bytes 文件，但名字不匹配默认 evaluation 配置 | 没有运行来源/预算说明；不能直接假定默认论文训练产物已齐全 |
| ACE/AppWorld experiment outputs | 作者 download.py 有 `experiment-outputs-0.1.2.bundle` 地址；ACE repo releases 为空 | 这是继承的 AppWorld baseline 输出入口，尚未证明包含 ACE 作者实验；本轮没有下载或审查逐例 test 输出 |
| AMA 数据 | 作者 README 明示只有 test；HF card 为 MIT | 可作公开暴露开发数据须另声明按 episode 的开发/验证切分，不能仍称官方未见 test；本轮未读数据/gold |
| AMA 全运行日志 | 固定 README 链接公开 Drive folder，宣称含模型输出、judge 输出及 pipeline trace | 网页检索打开返回 Internal Error，实际可读/下载内容未核实；无现成可审查轨迹已落地的结论 |
| AgeMem checkpoints | pin 树 441 项、发布 releases 空，eval yaml 指向本地 `dummy_lora` | 未找到作者已发布训练权重/可直接运行轨迹。不能把 base model 或 standalone demo 当训练 checkpoint |

开发原生环境可以先独立启动/执行合法 train 调用，验证环境和 evaluator；这与 actor
完成任务是两件事。在作者模型真正取得以前，现有作者公开经验或 QA frozen trajectory
最多帮助设计可观察失效分析，不能用 gold 选择 producer 下一步动作。

## 6. AMA 与 AgeMem 的精确阻断，及不降格的备选路线

AMA 固定 `AMA-Bench/AMA-Bench@ddfd319e0be33424288c13806f1eafc63e625b59`
提供 `src/run.py --method ama_agent --method-config configs/ama_agent.yaml` 和
`scripts/run_api.sh`。当前配置 default actor Qwen3-32B，embedding 是
Qwen3-Embedding-4B、auto-launch vLLM/tensor-parallel=2，另有回答和 judge 模型。
可把服务换为已有授权 API，但不能删除 embedding、自评和补查来方便我们获胜。

两个 config 细节须先冻结：YAML 写的是 `casual:false`，实现读取的是 `causal`，默认
false；要测试论文因果图能力须显式 `causal:true`。该类也不消费 YAML 中
`retrieval_mode/enable_tools`；只改这些键不证明切换了完整方法。原始轨迹回查一直
存在。这个 pin 公开的 TextWorld 路径是 synthetic trajectory/QA 生成代码；尚未核到
v4 论文 TextWorld/Spider2 端到端比较的对应 native runner，不能由 paper 宣称直接推定
今天已有可跑的 native capsule。

AgeMem 固定 `y1y5/AgeMem@98f563f907d67b2f2436e3ae7b7ceff32e482814`
是真实 Trinity-RFT 训练代码，不是简单 prompt。eval config 要 4 GPUs、Qwen2.5-7B
及 LoRA rank32 checkpoint，Ray/verl/vLLM 和 DashScope；当前无模型、训练 checkpoint
或 API 能力。其根 pyproject 声明 Apache 软件许可分类；本轮未在该树找到完整根
LICENSE 文本，若再分发其实现须单独核授权。最先可做的是公开 HotpotQA train 与
训练接口准备，但这不如已找到的 ACE 原生 train 入口直接回答 OCAR 的操作问题。

因此本轮选择 **ACE 作者原生 train + 原生评价 + 共同 actor 三臂接口**，先把可跑的
source/config/version/permissions 做实。完整 actor 资源补齐后才记录真正失败，
再据失败构造经典/候选维护。冷启动准备、原生启动、作者模型任务成绩、候选独有
增量四项分开验收；目前仅第一项已在本子任务完成。

## 7. 可复查主源

- [ACE 父库精确树与 gitlink](https://github.com/ace-agent/ace/tree/82709de050e1db6e6ef2f07bcb0393560b94992a)。
- [ACE AppWorld 固定 README](https://github.com/ace-agent/ace-appworld/blob/9f3e92155345a9159f3a8b25abc334eeca05b545/README.md)、[定制版本](https://github.com/ace-agent/ace-appworld/blob/9f3e92155345a9159f3a8b25abc334eeca05b545/pyproject.toml)。
- [原生 runner](https://github.com/ace-agent/ace-appworld/blob/9f3e92155345a9159f3a8b25abc334eeca05b545/experiments/code/ace/run.py)、[no-GT train 配置](https://github.com/ace-agent/ace-appworld/blob/9f3e92155345a9159f3a8b25abc334eeca05b545/experiments/configs/ACE_offline_no_GT_adaptation.jsonnet)。
- [native adaptation 权限/反馈](https://github.com/ace-agent/ace-appworld/blob/9f3e92155345a9159f3a8b25abc334eeca05b545/experiments/code/ace/adaptation_agent.py)、[actor 初始化](https://github.com/ace-agent/ace-appworld/blob/9f3e92155345a9159f3a8b25abc334eeca05b545/experiments/code/ace/adaptation_react.py)、[playbook 实际算子](https://github.com/ace-agent/ace-appworld/blob/9f3e92155345a9159f3a8b25abc334eeca05b545/experiments/code/ace/playbook.py)。
- [ACE 原文 v3](https://arxiv.org/html/2510.04618v3)，§3/4.1–4.2；本报告只借此定位完整能力，不复述论文全部结果。
- [AppWorld 公开/保护许可和开发规则](https://github.com/StonyBrookNLP/appworld/blob/42b5bcf3cd334fee33f0c37c02070a9f5807add5/README.md)。
- [AMA 固定 README/数据与日志说明](https://github.com/AMA-Bench/AMA-Bench/blob/ddfd319e0be33424288c13806f1eafc63e625b59/README.md)、[方法读取字段](https://github.com/AMA-Bench/AMA-Bench/blob/ddfd319e0be33424288c13806f1eafc63e625b59/src/method/ama_agent.py)、[数据 card](https://huggingface.co/datasets/AMA-bench/AMA-bench)。
- [AgeMem 固定 README](https://github.com/y1y5/AgeMem/blob/98f563f907d67b2f2436e3ae7b7ceff32e482814/README.md)、[训练版评价资源](https://github.com/y1y5/AgeMem/blob/98f563f907d67b2f2436e3ae7b7ceff32e482814/examples/agemem_hotpotqa/agemem_eval.yaml)。

前序：[强基线拆解](OACR_STRONG_BASELINE_DECOMPOSITION_2026-10-02.md)、
[真实 BFCL 执行](OACR_REAL_BFCL_EXECUTION_2026-10-02.md)、
[真实领域适配](OACR_REAL_DOMAIN_OPERATOR_ADAPTATION_2026-10-02.md)。
