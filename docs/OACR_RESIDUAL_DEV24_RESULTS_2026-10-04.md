# OACR 多场景原生残差发现：24 项开发批次结果

日期：2026-10-04。范围：AppWorld train 开发批次；不使用封存的 512-unit 评估库。

**24 个冻结任务位已全部记录，但没有发现达到 R1–R5 的独有算法残差。** 20 项原 producer 终态评分中，18 项成功、2 项未成功；其中一项未成功受到确证的接口重复执行干扰，另一项原生失败仍未定因。另有 3 项额度中断前缀和 1 项共享基库启动失败，单列保留。没有终态记录触发预注册高成本阈值；中断项的完整墙钟和成本未知。正确经典诊断控制尚未实跑，因此不主张任何残差已通过 R3。

## 冻结与执行范围

[用户协议](OACR_RESIDUAL_DISCOVERY_PROTOCOL_2026-10-04.md)在 `9276445530198098e986f72b822843a7bb3bec9f` 固定 residual-first 顺序。选择只扫描未改动 train manifest：排除先前暴露的 3 项后，按原顺序选每个 family 首个剩余实例，取前 24 个 family。这是 24 个任务、24 个不同 generator family 的固定开发样本，既不随机抽样，也不估计总体泛化率。

原批在 `13b794c7d9ddf1c56999189ac27ba9315701a4b5` 预先冻结。前 6 项均在共享 Gmail 基库加载阶段失败，另外 18 项因共同故障没有启动；actor 与 evaluator 调用均为 0。[原批 24 行结果](../experiments/oacr_residual_discovery/RESULT_2026-10-04.json)及 `task_success_score: null` 保留，不能记作 actor 的 0/24 能力分数。

[恢复臂](OACR_RESIDUAL_DEV24_INFRA_RECOVERY_2026-10-04.md)在 `a862d4754072294cd6a8b4d9465a349a99a68a26` 独立冻结，freeze SHA256 为 `7d2cb3c3ef337b2f0a7186db3e75e421045a871de6f4077a11c8a9f75ede3bb9`。相同 24 个 task/family hashes、顺序、producer、预算及原生评分规则保持不变；基础设施再尝试明确披露，没有按结果换任务或重跑 actor。恢复原始作者包的共享 DB 字节时只做结构与哈希检查，没有读取任务、gold 或评分行。

固定源为 ACE AppWorld `9f3e92155345a9159f3a8b25abc334eeca05b545`、AppWorld `0.1.4.dev0`。actor 是独立冷启动子代理，接收作者公开 generator 上下文、固定初始 playbook 和自己的合法 receipts。它们未接收 gold、评分反馈、其他 actor 的历史或 OACR 干预。本轮没有运行原始 DeepSeek backbone 或完整 ACE 学习闭环，也没有方法比较。

每个任务最多 40 次 execute 请求（拒绝、解析失败也计数）、每段原生代码 20 秒、actor 窗口 1200 秒、终止后独立评分最多 120 秒且仅 1 次。分页传输要求在执行前交付完整 prompt，但不能证明模型实际读取。原生安全机制及补充 AST 限制保持冻结；本接口不构成 OS 级隔离。

## 分母与原生评分

下表使用恢复臂固定位置索引。所有 24 项都保留，不以成功、故障或中断为由移除。

| 记录范围 | 项数 | 原生成功 | 原生未成功 | 未评分 | 解释 |
| --- | ---: | ---: | ---: | ---: | --- |
| 原 producer 终态，索引 0–9、14–23 | 20 | 18 | 2 | 0 | 包含索引 1 的 controller error；不是 20 条正常完成的 actor 轨迹 |
| 额度中断的保存前缀，索引 10–12 | 3 | 1 | 2 | 0 | 单独、事后 controller adjudication；不能并入完整 actor 能力分数 |
| 基库初始化失败，索引 13 | 1 | 0 | 0 | 1 | actor 与 evaluator 均未启动 |
| 固定任务位合计 | 24 | 19 | 4 | 1 | 23 项有原生评分；19 次观测成功的范围如上 |

已知评分测试小计为 120/137。它混合终态和中断前缀测试，不能替代完整轨迹成功率。23 个 actor 启动，23 次 evaluator 尝试；没有向 actor 返回评分，也没有评分后的 actor 重启或动作重放。

额度中断使索引 10–12 的旧 controller 消失。[中断处置](OACR_RESIDUAL_DEV24_RUNTIME_INTERRUPTION_2026-10-04.md)及 finalizer 在 `5ed064382fdf1383f6d65eb09d348f1db90c761f` 先于这三项评分登记：关闭死亡 mailbox，仅对 SDK 已保存前缀调用未修改的 evaluator 一次，没有重建 actor 或重执行 native actions。索引 10 前缀成功（2/2）；索引 11 为 2/5，索引 12 为 2/8，且索引 12 初始 prompt 尚未交付完整。它们不构成自然失败机制复发。

恢复继续时，索引 13 又在共享 Amazon 基库初始化失败。该文件与 canonical 字节不符，成因未知；保留失败记录和原坏文件，恢复作者原始字节后继续剩余固定位置，没有重试索引 13。恢复前后记录见 [asset metadata](../experiments/oacr_residual_discovery/recovery/ASSET_RESUME_RESTORATION_2026-10-04.json)。所有评分完成后，12 个共享基库与 canonical 哈希一致，作者 tracked source 无修改。

## 成本口径

[原始聚合结果](../experiments/oacr_residual_discovery/recovery/RESULT_2026-10-04.json)报告以下已知小计。索引 10–12 的完整成本未知；原生 requester records 是观察到的 API 记录，不是账单或未观测服务器工作量。

| 计量项 | 已知小计 |
| --- | ---: |
| execute 请求 / 原生执行 | 165 / 159 |
| 原生环境交互 / requester API 记录 | 159 / 947 |
| bridge 拒绝 / 解析失败 / 原生执行错误 | 5 / 1 / 0 |
| 生成的原生 receipt bytes | 436,551 |
| 生成的 bridge receipt bytes | 371 |
| 传输的 prompt / receipt 文本 bytes | 682,491 / 412,313 |
| prompt / receipt 分页请求 | 345 / 133 |
| mailbox 响应 bytes | 1,231,634 |
| actor 墙钟秒，已知小计 | 4,388.445 |

生成 receipt、mailbox 发布和模型实际消费分别计量；模型可见字节未知。模型调用非零，但 checkpoint、sampling、调用数、tokens 与费用均不对 controller 暴露。`external_provider_model_calls: 0` 不代表模型使用或模型费用为零。不能据此主张完整系统成本优势。

预注册高成本筛查为每项 API records ≥100、execute ≥20、原生生成 receipt bytes ≥100,000 或 actor 墙钟 ≥600 秒。20 项终态未触发；3 项中断前缀的墙钟 flag 为 `null`。筛查未触发仅表示没有该阈值的观测证据，不证明没有任何可优化成本。

## 冷审与归因

完整 [24 行归因账本](../experiments/oacr_residual_discovery/recovery/ATTRIBUTION_LEDGER_2026-10-04.json)保留每项 hash、原分数、成本、证据链与归因状态。归因是评分后诊断，不回写 producer 结果。

**索引 1：确证的 transport 干扰。** [独立接口冷审](OACR_DEV24_TRANSPORT_AUDIT_2026-10-04.md)确认只有 4 个不同 execute UUID，但实际有 6 次原生执行；同一个 UUID 被处理三次。76 次 API records 中有 40 次发生在两次重复调用，原数完整保留。终止异常在 response publication，不能当作原生动作执行异常。请求文件保留或重现的精确原因未定；bridge 缺少执行前 UUID claim/deduplication 则由代码与链式事件共同确证。不能将 36 次描述性 first-per-UUID 小计冒充修正运行成本，不能假定一次执行的反事实任务会成功。本项不支持科学 R1/R3。

**索引 2：原生未成功，原因未决。** [独立任务冷审](OACR_DEV24_TASK_FAILURE_AUDIT_2026-10-04.md)只查看该 actor 的原始公开指令、代码、receipts 和公共 API 实现，未读 gold、私有状态或 evaluator report。可见证据包括分页、去重集合、导出写入与精确读回、删除与完成 acknowledgment。两次常规实现被 AST 拒绝后，actor 使用显式调用与手工 CSV；quote-all 形式通常是有效 CSV，不能据此宣布格式错误或 evaluator bug。自生成字符串相等只能验证保存与内部一致性，不能独立证明完整接受条件。

序列化/验收差异只是低置信假设，尚无因果确证；持久化、删除条件或其他原生差异也未排除。冷审登记了保持合法数据、动作顺序及评分不变的 paired quote-policy 诊断控制与独立解析/覆盖检查，**尚未执行**。它不是已通过的经典控制，更不是已存活的 OCAR 残差。原冻结任务不在本批重跑；任何后来控制须另行预冻结并披露身份。

其余 18 个成功终态没有自然失败或预注册高成本触发，不人为制造“需要修复”的问题。3 个中断前缀和 1 个初始化错误分别归为基础设施记录，不能凑成重复科学机制。

## R1–R5 处置

| 门槛 | 本轮证据 | 处置 |
| --- | --- | --- |
| R1：至少 3 个独立任务、2 个 family 的同机制复发 | 仅 1 个待核原生失败，且机制未定 | 未达到 |
| R2：真实原生成败或登记成本 | 原生失败已观测；高成本筛查没有终态触发 | 任务相关性存在，机制因果未建立 |
| R3：正确可实现强经典控制仍不能消除 | 仅登记诊断控制；没有执行 | 未达到，不能把 unresolved 算作 survival |
| R4：更广结构、新构造、同保证成本界或新能力 | 没有独立增量 | 未达到 |
| R5：构造前精确反证标准 | 登记了窄诊断假设的 falsifier；没有新核心构造 | 诊断待检验，不记作核心准入通过 |

因此没有新核心 producer，没有算法晋级，也没有官方比较收益主张。Support-Lifecycle 保持退出；既有 BRFP、R4/SQEC、图构造与残余更新证据保留原范围。本轮不证明所有未来算法方向都没有价值。

## 审计范围与后续顺序

冻结 producer hashes、task/family 顺序、链式事件与计数已核对。原始 exporter 的 `all_fixed_rows_audited: false` 保留：10–12 缺少原 producer stop/grade 事件，12 还缺完整 prompt 交付。[独立限定审计](../experiments/oacr_residual_discovery/recovery/QUALIFIED_AUDIT_2026-10-04.json)核对 21 个原 producer 终态记录（含 1 初始化失败）及 3 个单独前缀处置，确认原前缀未改、处置 hash 与独立评分匹配、endpoint 先关闭、没有重放，未知成本保留。它不把 3 个例外改造成原 producer 正常终态，也不修正原聚合 audit flag。

后续先处理 future harness 的 at-most-once request admission 与 host/native 文件操作边界，使用 transport-only stub 诊断后再冻结新版本；现有 producer 不改。该修复目前只是已审查建议，未实现或测试。随后才按独立预注册执行窄经典诊断，并用与结果无关的新任务选择继续寻找复发。未达 R1/R3 前不构造新方法，不因未决失败扩大原创主张。

公开内容仅含代码、哈希、计数、范围化结果和公共来源审查；任务身份、完整 prompt/code/receipt 轨迹、凭证、gold 与数据库内容未上传。外部读者可核对公开账本与声明一致性，完整私有轨迹的独立重验仍需合法访问授权。
