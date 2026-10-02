# OACR：真实 BFCL 案例上的执行候选与经典强对照

日期：2026-10-02。起点：PR #89，`b05b4a9376c0b92d2d035a69798cad866dc4749a`。
预运行版本：本文件、producer、runner、下载器、依赖与 manifest 一起冻结后执行。
首个冻结 `d6d001c744ae25f4c9ed9f48c77b6ab6745b87cf` 的尝试在 base_0 的第 6 条
调用 `sort('final_report.pdf')` 因位置参数解析中止，此前执行 5 个公开事件、1 个
read 请求，0 个完整案例/官方分支检查，无完整结果。只修正 runner 的公共签名绑定，
增加全部调用的语法预检；producer 与 50 个 case IDs 不变。修正后重新冻结再执行。

用户要求：执行候选必须可做，必须比较真实基线与案例，解释对手为何强，再判断独有优势。
上轮 7 个人工 fixture 只作接口开发检查。本轮直接使用公开 BFCL 官方任务和未改动的
原生工具/检查器；仍区分参考动作回放、学习 agent 分数及独立算法增量。

## 1. 实际对象与输入权限

BFCL 固定 `ShishirPatil/gorilla@6ea57973c7a6097fd7c5915698c54c17c5b1b6c8`。
使用 `BFCL_v4_multi_turn_base.json` 中全部 50 个 `involved_classes` 含
`GorillaFileSystem` 的条目（base_0–49），不按成功或收益筛选。这些公开评价条目
明确作为暴露的开发案例，不能再称未见测试集。参考答案作为 verifier 的回放驱动，
逐次提供当前候选调用；不是学习出来的 actor，也不是独立闭环任务完成率。

producer 只收过去的可见调用/回执与当前 proposed read。初始配置、未来动作/回执
及评分只在 verifier；初始 cwd 为 root 是公开执行协议，不取得初始目录/文件内容。
原生执行不被记忆表示替代，官方检查器保持原代码。旧 512 单元不读取、不解封。

## 2. 三种能力的具体实现

| 对象 | 本轮实际执行 | 保留能力 / 不能推断 |
| --- | --- | --- |
| 经典依赖维护 | `IndexedViews`：可见内容事实、部分查询结果、路径前缀依赖索引、已确认文件的 copy/move 传递与写入失效 | 不强迫重扫全历史；包含初始化、索引和共同原始历史成本 |
| 当前执行候选 | `DemandViews`：从当前原生 read 向后回推值/查询证据，经过 copy/move 重绑定，遇未知效应明确回退 | 基于经典回推/程序切片的未升格候选；不是独立新算法或必要性定理 |
| 作者检索/回查组件 | 未改动 AMA `traj_get`、`traj_find` 和 `BM25Method(top_k=5)`，在真实可见前缀上执行 | 这是公开 accessor 的移植诊断；未运行 AMA 的 embedding/causal graph/LLM sufficiency/agent，不能用它冒充完整强基线 |

所有维护方法保留相同收费的可见原始历史。经典与候选共享经源码审查的语义适配，
各自维护并执行不同表示。查询原生语义覆盖 cat/grep/wc/sort/tail/diff，维护包括
touch/echo/mkdir/rm/rmdir/已确认文件的 cp/mv 及单层 cd。未知类型或目录复制/移动
触发全局失效与新导航命名空间，之后仍允许安全局部读依据；不谎称已掌握别名。
未见 writer 不在正面保证范围。未知只表示本算法不能从当前依据确定，不证明
所有方法都信息不足。错误预测不作静默修正。

原生目录 cp 是浅拷贝，mv 创建新对象且对子目录 parent 的处理不同于普通文件系统。
这些是适配义务，不能以实现怪异作为新现象的论文贡献。更强的经典 heap/alias
维护能否消除回退，需要在同一合法观察输入下进一步构造。

## 3. 两个不同的实际目标

1. 当前原生读的回执能否从可见前缀正确计算：在真实下一次 read 之前作预测，然后
   与未改动的 backend 回执比较。信息不足继续调用，不排除困难任务。
2. 官方检查器下能否真的省调用：只省候选已正确知道且同一分支已经实际取得足量
   同样序列化回执的纯读取。每轮请求计数公开在线计算，不看未来 gold。其余调用
   保留。完整参考与两条过滤轨迹分别送原官方 multi_turn_checker。

原检查器既检查最终原生状态，也要求参考回执在累计实际回执中出现。第一次由
本地内容推导出的新形式回执，不能直接算作官方认可的省调用。局部依据复用率、
实际省调用数、原生任务检查是三个不同数字。参考轨迹自己通过只作运行 sanity，
不是我们 agent 得分；过滤后通过也只验证此轨迹变换。

检索诊断报告选定 compiler 证据索引是否被 accessor 覆盖。证据不是全局最小集合，
包含保守保留的导航；没覆盖此证据不等于无法用其他证据作答，更不等于 AMA 失败。
作者 full-prefix 回查始终允许，不能关掉它制造强基线劣势。

## 4. 成本与预运行冻结

逐例记录共同可见历史加 producer 状态的序列化字节峰值、构建/更新访问、查询访问、
producer CPU 与原生调用。索引、namespace、证据及上下文一同计入；程序访问计数
不是普适成本下界，单次 CPU 不作稳定性能结论，序列化大小不冒充 RSS。下载和
依赖属于运行准备；本轮模型调用为 0，也不作 token/美元或端到端总成本胜出。

复现（在仓库根目录；source 和数据下载至独立目录）：

```bash
python experiments/oacr_native/prepare_real_bfcl_views_v1.py --dest /tmp/oacr_real_sources
python -m pip install --target /tmp/oacr_real_sources/native_deps -r experiments/oacr_native/real_bfcl_views_v1.requirements.txt
python experiments/oacr_native/run_real_bfcl_views_v1.py \
  --source-root /tmp/oacr_real_sources \
  --freeze-commit a01af92d19c28aa0f7d34fbe534552d380e3ac3d \
  --output docs/OACR_REAL_BFCL_VIEWS_RESULT_2026-10-02.json
```

manifest 固定全部 50 case IDs、14 个作者 source/data 哈希、三份实现哈希、输入权限、
回退与失败条件。官方 checker 任一分支失败或原生已知预测不一致均保留失败输出并
返回非零，不删案例。结果/逐读 ledger 在运行后追加，冻结代码不随结果修正。

## 5. 独有优势的判断

真实任务载体使问题可检验，但不自动制造理论增量。先判断经典维护为何能追平：
已经知道的事实可以跨操作保持，未知初始内容不能从检索中创造，依赖索引能避免
无关全扫。候选必须增加其不能匹配的构造、结构范围或同保证成本结果；只有
检索上下文更短、反向证据看起来漂亮，均不够。

完整 AMA-Agent/ACE/AgeMem 对照仍需要实际模型、各角色与经验/训练预算、对应
原生 runner。当前环境没有模型接口/本地模型，因此本轮不声称这些端到端复现。
已有可运行共同维护接口也不能替代这个未完成项目。

唯一门槛：[Acceptance Gate](OACR_FINAL_UPGRADE_ACCEPTANCE_GATE_2026-09-30.md)。
前序：[强基线拆解](OACR_STRONG_BASELINE_DECOMPOSITION_2026-10-02.md)、
[领域适配](OACR_REAL_DOMAIN_OPERATOR_ADAPTATION_2026-10-02.md)。

## 6. 冻结后的真实案例结果

修正后的预运行冻结为 `a01af92d19c28aa0f7d34fbe534552d380e3ac3d`，完整执行一次。
producer、runner、配置与依赖此后未改动。50 个案例、159 轮、276 个参考原生调用
均保留；73 个实际读取请求没有增造、删去或用已知任务替换。

| 检查 / 成本 | 经典索引维护 | 当前需求回推候选 |
| --- | ---: | ---: |
| 从过去可见依据正确计算本次回执 | 19 / 73 | 19 / 73 |
| 原生已知预测不一致 | 0 | 0 |
| 需要继续原生取证 | 54 | 54 |
| 可在原官方回执规则下省掉的调用 | 0 | 0 |
| 完整轨迹通过原官方检查器 | 50 / 50 | 50 / 50 |
| 查询事件 / lookup 访问 | 84 | 169 |
| 更新访问（含 namespace 与索引） | 939 | 466 |
| 各案例完整序列化 bundle 峰值之和，bytes | 87,837 | 92,837 |

覆盖逐请求完全一致。50/50 不是新 agent 成绩：动作来自作者 reference；本轮实际
没有省去任何调用，因此过滤分支保持同一原生调用列表。它确认了真实运行接口和
检查器可用，不能作闭环决策优势。候选序列化存储多 5,000 bytes（约 5.69%）；
查询与更新访问采用不同的程序原语，不把两列相加当普适成本界。单次 producer CPU
记录在 JSON 中，未做重复性能实验，不据它宣称稳定速度或端到端总成本胜出。
原生调用另分账：prefix 驱动为 276 次；原官方 checker 对三条完整分支各执行
proposed/reference，合计 1,656 次 verifier-only 回放，总计 1,932 次。
这 1,656 次未回流为 producer 的新证据，不算部署取证收益。

19 个成功需求覆盖 13 个案例：wc 10、cat 3、sort 3、grep 2、tail 1。14 个案例进入
未知/目录 transfer 的保守模式，仍在完整分母中。54 个未解决项是这个可见依据
算法的输出，不是查询必要性证明；检索不到不存在的初始内容和本实现主动保守
回退均可能影响覆盖。

真实实例 base_2：`TeamNotes.txt` 经 echo 写入、复制至 Archived、再重命名为
`IdeasArchive.txt`。最后 cat 的内容可由合法旧依据正确传递，经典与候选给出相同
内容和 `[0,2,4,5,6]` 证据索引；原生结果一致。这个真正的重绑定案例说明维护有用，
同时说明其本身不独有。base_36 的空文件 copy/rename 后 grep 也由两者同样处理。

### 为什么不能把检索对照变成独有优势

在 19 个选定 compiler witness 上，未改动作者 BM25 top-5 覆盖 17 个，固定 entity
search 覆盖 9 个，完整历史回查覆盖全部。全 73 个请求的输出上下文字节分别为
24,422、12,503、26,092。此批原始 prefix 很短；BM25 已接近返回全部上下文。
缺少选定 witness 不证明缺少任何可替代依据，也不对应模型答案错误。

AMA-Agent 的真正强度还包括语义状态/因果图、embedding 初取、自评缺口、图或
代码/关键词扩查、原始历史保留。本轮跑到的三个 accessor 不能代表完整系统。
其 v4 已用同一 actor 在 TextWorld 和 Spider2 检验端到端任务；这些领域和长链
规模尚未在本轮复现。ACE 的详细策略 playbook、反馈反思和增量合并，以及
AgeMem 的训练策略也不在这个 reference 回放中。比较它们时必须保留这些能力。

源码补查：BFCL `base_handler.py` 在本 source pin 下获取实例初始状态用于日志，
并把原生回执交给 actor；本轮没有把日志中的 state_info 提供给 producer。

### 本轮研究决定

“文件重绑定后回推并复用正确读依据”保留为实际适配基础，不能升格为独有核心。
它与正确经典维护的覆盖完全相同，并无官方省调用收益。我们目前未找到新核心
优势；真实执行不是新颖性的替代品。

下一个候选只有满足下列具体区分才值得构造：在合法可见输入上处理本轮回退的
部分观察/别名/效应结构，或在同保证下减少构建、更新、取证与存储的联合成本；
且必须同时让正确的经典 heap/alias、查询视图与依赖维护竞争。原生适配的代码怪异、
手工写得更多的规则、更漂亮的证据列表均不算这种区分。扩大到 τ² 的一次性动作
资格及双角色更新时，也不能仅靠标准 typestate/前置条件回推来宣称新内核。

在完整学习方法运行前，还须取得相同 actor 与各方法角色配置、作者实际 native
runner、经验/反馈预算和公开开发轨迹。先记录完整原方法的失败及经典适配能否
补齐，再决定算子，而不是根据我们自己造出的案例选新算子。缺少模型接口/本地
checkpoint 是本轮未执行完整系统的实际限制，不用 accessor 数字填补此项。

结果：[完整运行与逐案例成本](OACR_REAL_BFCL_VIEWS_RESULT_2026-10-02.json)、
[73 条真实读取账本](OACR_REAL_BFCL_VIEWS_RESULT_2026-10-02.ledger.jsonl)。
ledger SHA256：`c7ff9f2ace2e62763b0ca761e9e645b560b824c36630d3caf67ebf6dbe6fda88`。
原文：[AMA-Agent v4](https://arxiv.org/html/2602.22769v4)、
[ACE v3](https://arxiv.org/html/2510.04618v3)。输入/源码 pin 与下载 URL 见运行 manifest。
