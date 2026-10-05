# 24-task infrastructure abort and separately frozen recovery

2026-10-04。首批 pre-run commit：`13b794c7d9ddf1c56999189ac27ba9315701a4b5`；
freeze SHA256：`cf9530a3fe8e5d9c87a17113d3f15356e77d97c66fd848e48434ab3845b15648`。

## 原始尝试永久保留

索引0–5的六次 world initialization 均在作者 `get_db_args()` 的 SQLite backup
阶段报 `DatabaseError: database disk image is malformed`。没有成功创建 world，
没有 actor start、prompt 交付、原生 actor API 调用或 evaluator 调用。Task.load
已经开始，不能写作“零任务载入”。其余18项在统一基础设施故障后停止启动，
记录 `not_started_due_infrastructure_abort`。原批保留24项分母；不是 actor 0/24
能力测量，也不将启动错误改写成 native evaluator false。

首六项 summaries、私有日志/锁、首批 freeze 和未启动状态不删不覆盖。
保护内容不上传。首批不调用通用 exporter 将 actor 模型使用假记为 nonzero；
该批实际 actor invocations 为0，工程/controller模型使用不属于 actor实验成本。

## 资产诊断与原样恢复

仅做共享 base DB 的字节、100-byte header及只读 structural integrity 检查，
不查询数据行、task正文、gold、参考动作或 evaluator labels。损坏 Gmail 文件
57,392,640 bytes；作者原包的 Gmail 文件62,545,920 bytes。重新下载 pinned
作者 `download.py` 指定的 `data-0.1.0.bundle`：
`https://s3.us-west-2.amazonaws.com/appworld.dev/data-0.1.0.bundle`，
34,280,074 bytes，SHA256
`fd9f9608c2ec71ed0ac25c3633a738b9129a318a129e31230425b9188e508250`。

只解出共享12个 base DB，不按例读取 test/gold。原包12个 DB 全部通过 quick_check；
11个与当前安装完全一致，仅 Gmail 不同。旧损坏文件留本地；恢复原包字节后全部
12个 SHA 与 canonical一致。没有 REINDEX/VACUUM、SQL修复、任务择修或造数据。
资产对照公开于 `CANONICAL_ASSET_RECOVERY_2026-10-04.json`，仅 hash/size/status。
损坏发生原因尚未确定，不归因自然外部 writer 或任何研究现象。

作者 task loader 在 backup 后才应用 task delta，且为每 task加载全部 apps；一个
坏共享库足以解释六项同位置初始化失败。隔离 venv 与 controller 的 SQLite版本
均为3.53.1。作者源码 tracked diff 仍为空，API/evaluator未改。

## 恢复批次的独立注册

恢复属于**明确披露的 infrastructure retry**，不能声称总体“无 retry”。
没有 actor内容/成绩暴露，没有score-conditioned retry，也没有task replacement。
同24个 task/family hashes、原顺序和manifest保持不变；不按成功率重选样本。
新的 private run root、freeze、结果目录和run ID与首批分开。首批六个 native
output目录均不存在：故未改 producer，可沿用作者 experiment name，创建其
首次实际 native outputs；这不是覆盖既有 world。逻辑与字节级producer均不变。

恢复 freeze 在actor前增加 canonical bundle/12asset SHA、abort batch关联、实际
retry范围、newrun ID；其它冻结40/20s/1200s/grade120s/2000chars/seed123、
公开context、禁止gold和OACR、成本阈值均保持。恢复完成后仍完整报告24项，
不得用它替换原批结果。它是开发恢复实验，不能当作独立测试泛化证据。

执行恢复前提交新freeze；全部actor结束后按原注册归因与R1–R5审查。
