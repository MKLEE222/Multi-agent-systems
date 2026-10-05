# Index-2 paired quote diagnostic：经典控制消除失败候选

本次诊断在 2026-10-05 完成。原实例的两条 fresh-world 控制臂只更改 data-field quoting；A 保留原 quote-all，B 使用 minimal quoting。独立 parser、公开 read-back 及跨臂不变量全部通过，原生 producer 返回 A 未成功、B 成功。因此按事前注册的 `01` 分支，归因于 **quote-policy acceptance sensitivity**，index 2 退出独有核心候选。这里没有产生新算法、跨任务复发或 OACR 收益。

## 预冻结和运行范围

- 执行前提交：[8af3081f54a325a545b6abec099b6df04589f0eb](https://github.com/MKLEE222/Multi-agent-systems/commit/8af3081f54a325a545b6abec099b6df04589f0eb)。16 项公开代码/协议/哈希文件经 GitHub tree 回读校验，私有合法 payload 不外披。
- [诊断 freeze](../experiments/oacr_residual_dev24b/diagnostic/freeze.json) 的 SHA-256 为 `890ea6405bafe6608b49a018a5a8faa740514a1aa4e26069ed014695e09804c0`；[协议](OACR_DEV24B_QUOTE_DIAGNOSTIC_PROTOCOL_2026-10-04.md)与 runner 保持预冻结字节。
- 只有原 DEV24 index 2 的一个 train task、一个 family、两个新环境。两臂不算新的独立开发任务，未重启原 producer，也未修改原评分或固定分母。
- 每臂执行原来的 9 条合法 native snippets，加一条相同的独立 parser 检查。parser 不发业务 API；两个原 AST 拒绝不在此 native diagnostic 中重放。
- 两臂都通过删除前检查才授权删除；两臂都关闭后才授权各评分一次。没有重试、替换、读取 gold/private DB/evaluator report 或打开 512-unit 评估库。

## 结果与成本

[原生聚合结果](../experiments/oacr_residual_dev24b/diagnostic/RESULT_2026-10-04.json)沿用预冻结 runner 的文件名；实际执行日期为 2026-10-05。

| 指标 | A：原 quote-all | B：minimal quote |
| --- | ---: | ---: |
| producer success bit | 0 | 1 |
| parser 与公开 read-back | 通过 | 通过 |
| 行数 / distinct pairs | 72 / 72 | 72 / 72 |
| native executions | 10 | 10 |
| API requester records | 88 | 88 |
| 独立 parser 的业务 API | 0 | 0 |
| 删除尝试 / 评分尝试 | 1 / 1 | 1 / 1 |
| generated receipt bytes | 34,007 | 33,715 |
| native execution elapsed seconds 小计 | 1.094714 | 1.056879 |

两臂相同的合法 source components、source union、record order、headers、row order、row set、公开回读后的解析顺序和 API counts 均通过冻结检查；输出字节按各自 quoting policy 独立重建匹配。parent 墙钟为 **10.199182 秒**，共 **20 次 native executions、176 条 API records、67,722 个 receipt bytes、2 次原生评分**。这是这两个固定控制臂的实际本地运行成本，不包含此前工程开发、模型思考或对话消耗。

本次没有新增子代理；两个本地 Python 环境进程不调用 actor 模型。固定诊断 actor model calls 为 **0**，主代理编写、审查与执行调度的模型使用非零，tokens 和费用未暴露。此前异常用量的账单成因仍未查明，不能从这次 native 墙钟或 API 次数推出模型费用已恢复正常。

[执行后审计](../experiments/oacr_residual_dev24b/diagnostic/AUDIT_2026-10-05.json)重新核对全部步骤、payload/receipt 哈希、parser/read-back、授权文件与执行 ledger 顺序、评分次数和成本小计。每个固定步骤每臂恰执行一次，A 的 9 条原生 receipt 哈希全部与旧合法记录一致；原 producer、freeze、合法来源证据与 source 哈希重验通过。审计仅检查本次文件和冻结代码，不是第三条原生复验臂，也不是执行的密码学证明。

## 两次 kill 的解释

1. **Transport kill 已通过纯 stub 测试。** 新模块的 26/26 检查中，154 个进入 callback 的 UUID 对应 154 次 callback；一个 callback 前遗留 claim 和一个冲突响应均不执行。测试覆盖重复 delivery、清理失败、既有 response、发布失败、重启和 native monkeypatch 边界，AppWorld task/world/API/evaluator/model 调用均为 0。另 4 项 controller audit 检查通过。保证是 at-most-once admission；未知执行结果 fail closed，不能声称 crash 下普遍 exactly-once。新 UUID bridge 的完整 cold-actor 集成尚未在 DEV24-B 验证。
2. **Index-2 的窄科学假设已有判别结果。** 相同合法数据与 mutation 下，quoting 改动足以改变本次 producer 接受结果。它归入经典序列化/验收适配，不支持新的表示、支持生命周期或算法对象。quote-all 在独立普通 CSV parser 下有效；未读 evaluator report，因此不进一步认领内部验收机制、malformed CSV 或 evaluator bug。

index 1 继续因重复执行干扰排除在科学 R1/R3 外。index 2 现在按预注册经典控制归档。原 DEV24 与 recovery 的所有历史行和评分保持不变；本次不把 A/B 成功拼入原 DEV24 actor 成功率。当前没有通过 R1/R3 的机制残差，独有核心仍未发现，Support-Lifecycle 继续退休。

## 环境与下一步

启动前再次发现共享 `simple_note.db` 与 canonical 作者资产不符，成因未知。先保存坏文件，再恢复已有 canonical 原始字节；准备、parent、各 worker 启动前和执行后，12 个共享资产全部哈希匹配。该事件见[资产 preflight](../experiments/oacr_residual_dev24b/SHARED_ASSET_PREFLIGHT_2026-10-05.json)，不能归为自然任务残差。作者 tracked Git source 未改；所用 installed native app source 以哈希固定，但不在 ACE Git revision 中，来源证明的这一限制保留。

DEV24-B 的两项实验前置条件已经满足，但 **B 尚未冻结、没有读取 B prompt、没有创建 B world 或调用 B actor**。接下来只完善[可计量用量的执行准备](OACR_DEV24B_BOUNDED_EXECUTION_PLAN_2026-10-05.md)。24 个 family 的 next variant 仍由原规则机械选择，任何运行都须保持最后一次 broad discovery 及无 R1 则停止 AppWorld core search 的规则。
