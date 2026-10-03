# Authority transport: fixed exact-effect fragment

这是候选 A 的第一步可运行适配资产，**不是独立两算法性能实验**。ClassicalAuthority 与 EffectBoundTransport 共享事实、版本、affine ledger、exact-intent cache 与原生 guard/effect summary；在本冻结片段，两者的授权谓词都是已确认 effect 的精确相等。正确强经典控制必须拥有相同 semantic fallback，不能只比较 anchor 参数后拒绝语义等价调用。

因此，本实现的独有内核主张已结束：候选条件与强经典条件相同，这个关系来自构造定义。native mutation suite 的用途是独立审计手写 source-derived summary、角色/授权接口和拒绝边界；它没有证明所有授权运输、限定宽度构造或其他效果合同都无价值。

## Run

需要 Python 3.10+ 与 Pydantic 2；本轮环境为 Python 3.12 / Pydantic 2.13.5。无需 tau2、模型、密钥、网络或 benchmark data。原生 data-model 类来自固定公开源码；fixture DB 只是承载这些真实 model 对象的字典容器。

从仓库根目录运行：

```bash
python experiments/oacr_moe/authority_transport/run_mutation_suite.py \
  --freeze experiments/oacr_moe/authority_transport/freeze.json \
  --output /tmp/authority_transport_replay.json
```

也可在任意目录传三个绝对路径。入口先检查冻结实现 SHA256、再检查每个 copied method body 的 AST hash。当前 `freeze.json` 与已交付 code/source manifest 完全匹配。README/LICENSE/执行补记不改变冻结代码。不要把新的修改继续写到本冻结 `result.json` 后当作同版本结果；修改需另立 freeze 和 result。

## Input and guarantee scope

- `Scope` 明确 session/user；`Action` 保留 item/new-item 的顺序配对与多重性；`Confirmation` 是明确结构化输入，要求本次当前修改范围已确认。没有自然语言 parser 或 NL correctness 声称。
- 授权的语义是本次原生调用的完整声明 effect projection：目标 order/user、最终 items/status、新 payment event 与 gift-card delta。原生源程序里的 terminal-variant 与 sequential substitution 保留，未改为理想的同时配对替换。
- 两维护器只接收 deep-copied public READ 回执；构造 fixture、原生 state clone 与 before/after 只在独立 auditor。确认 payload 由公开 fixture 明确给定，不从 native verifier 的答案产生。
- `window_certified` 默认 False。runner 显式声明无其他 actor 的串行 fixture 区间并调用 certify；这是一项执行协议前提，不从“没有看见更新”推断。`open_interference` 使 epoch 失效；仅重新声明窗口而不重新观察仍拒绝。没有对隐藏更新下当前政策/效应的保证。
- `ready/spent/uncertain` 阻止旧确认、重复确认或未知 write completion 恢复已经消费的资格。suite 中成功/无写入/不确定 completion 是明确的合成 ledger 输入事件，用于接口边界审计；**这些 case 不宣称是一段完整合法原生执行历史**。原生 source probes 在独立 fresh clone 上发生，不能代替未来端到端闭环。
- 无规则/无观察/范围未封闭/消费不明是检查拒绝或未完成，不是信息论不可解。

目标/helper 方法 body 逐字复制自 Sierra τ² commit `5bfa7e37b36656b37dc6d022156be6563c1007f3`，见 `source_manifest.json` 的 source SHA、位置、segment hash 和 body hash。只省略工具注册 decorators、ToolKitBase 及其注册初始化；`NativeRetailTools.__init__` 只赋 db。没有修改目标/helper body。它是 source-body native verifier，不是完整 tau2 environment / tool dispatch / policy parser / official evaluator。公开源码副本遵守随附 Sierra MIT LICENSE；不包含任何 benchmark database 或任务标签。

## First execution record

冻结代码后，首次且唯一一次 diagnostic suite execution 成功。没有失败 attempts 或预冻结 suite runs；之前的 BFCL 21-call feasibility check 属于另一个已单列检查，未用于这份 result。第一次 result 保存于 `result.json`，独立执行记录及文件摘要保存于 `execution_record.json`。

| 项目 | 实际结果 |
| --- | ---: |
| 公开自建 fixtures | 31 |
| 每方法 admit / deny | 8 / 23 |
| Source-body native write probes | 62 |
| Public native READs（两方法合计） | 194 |
| 总 native 顶层调用（READ + write probe；不含内部 helper 次数） | 256 |
| 每方法具体 native guard/effect predictions audited | 20 |
| Guard/effect native mismatches | 0 |
| Unsound fixture admissions | 0 |
| 每方法已取得 public receipt payload bytes | 44,880 |
| 每 case retained state bytes 范围 | 1,624–2,842 |
| Runner wall time | 0.043890370 s |
| Exec 命令总 wall time | 约 0.092 s |
| 模型调用/官方任务执行 | 0 / 0 |

Mutation cases 包含：exact/version cache、等效和不等效的配对次序、terminal-variant 影响、sequential collision、重复 ID、支付与作用域变更、可用性/余额/strict pending guards、无关观察变化、关联价格变化、unknown interference、stale epoch、重新观察、范围未封闭、已消费和消费不明、缺观察以及空列表的实际源码边界。

## Cost interpretation

`result.json` 中 `all_counted_resources_matched` 只表示记录的序列化状态/同输入 hash、共享代码/capsule 字节、回执字节、native READ/probe 数及确定性工作计数相同。由于两个类共享维护框架和同一 predicate，这些相等不是两个独立算法的性能胜负。CPU 与 wall time 分别实测，未断言它们相等；冻结 result 不提供计时显著性或完整成本最优性证明。

每方法计数：97 read receipts、31 confirmation writes（含重新确认）、32 prepares、12 cache writes、322 guard/lookup visits、13 effect comparisons、4 completion writes。state 字节包含 facts/versions/epochs、confirmation payload、ledger 与 cache；公共源 capsule 18,475 字节与所有实现文件字节另列。审计器自己的全状态和 62 write probes 属于 verification 成本，不免费提供给 producer。无 LLM tokens、训练/反思、工具调用省额或官方 reward 声称；所记录 serialization 是字节代理，不是 Python heap RSS。

可用的 source adapter 和强经典接口保留为基础。下一步若改变授权合同、结构范围或隐藏干预条件，必须提出具体新构造/保证/成本点并重新冻结；本次不继续扩大 fixtures 或贴到 AppWorld 来声称跨系统。
