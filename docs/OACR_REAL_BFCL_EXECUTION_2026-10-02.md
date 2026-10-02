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
  --freeze-commit FREEZE_COMMIT \
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
