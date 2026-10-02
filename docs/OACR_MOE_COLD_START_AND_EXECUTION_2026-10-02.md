# OCAR：MOE 冷启动汇合与已经开始的执行

日期：2026-10-02。只读审查起点：PR #89 head
`dde1d4da9471ed0e2485c6b8ae549c1dbbb7d282`。

**解困方向是先定位完整强方法留下的具体缺口，再争取一项独立增量。**
已有 BRFP/OACR 成果保留；零件可以继承成熟理论。三层各自首创是上限目标，
不是所有局部结果的联合准入门槛。仍然需要对应主张的近邻、正确经典对照、
原生验证与实际价值；当前没有已确认的独有核心算法。

本轮不是仅给建议：四位专家独立冷审，完成旧真实实验的原因诊断，展开此前
遗漏的作者原生 runner、安装并实际启动其 train 环境，同时构造并运行了第一版
效应绑定授权接口。该版一经形式化就归约为经典检查，立即停止其独有内核主张。

## 1. 四路冷审的合流

| 冷审 | 具体发现 | 对推进顺序的影响 |
| --- | --- | --- |
| [科学目标](OACR_MOE_COLD_SCIENCE_2026-10-02.md) | 经典匹配、信息不足、实现漏覆盖、评分契约和载体负荷是不同障碍；旧 gate 将完整升级与所有局部贡献混用 | 唯一验收登记已按主张绑定义务；不追溯给负结果盖章，不增加三层原创的强制门槛 |
| [强系统](OACR_MOE_COLD_BASELINES_2026-10-02.md) | ACE 的实际 AppWorld runner 在固定 gitlink 内；no-GT 仍有相关 API 先验和训练评分反馈；公开子模块与论文 v3 的增强存在版本边界 | 修正“未见 runner”；原系统能力和权限逐项保留，环境就绪与完整模型成绩分开 |
| [真实 arena](OACR_MOE_COLD_ARENA_2026-10-02.md) | 54 个 unknown 中，50 有执行不可辨见证，1 有源码见证，3 是可由经典维护补齐的实现缺口 | 不再将全部 unknown 解释为信息下界，也不拿补三条覆盖当新算法 |
| [底层算子](OACR_MOE_COLD_OPERATOR_2026-10-02.md) | 提出效应绑定授权、可见别名运输、许可动作建立义务三条候选；每条都有直接经典近邻 | 先做可证伪的接口/原生边界；一次性 ledger、symbolic heap、belief/reset 各自已有基础，不以换名升格 |

BFCL 见证条件化于旧 producer 可见 calls/receipts 与拟议 read，**不针对完整
agent 的用户消息、经验与合法补查权限**。50 执行见证与 1 源码见证不提供新
全球定理；3 项缺口也没有回写冻结 producer。19 原预测加 3 个可确定结果是
逐前缀证书诊断，不是新方法 22/73 得分。原官方省调用仍为 0。

## 2. 原作者强系统入口已从“找不到”推进到原生环境可运行

固定父库 `ace-agent/ace@82709de050e1db6e6ef2f07bcb0393560b94992a` 的
gitlink 指向 `ace-agent/ace-appworld@9f3e92155345a9159f3a8b25abc334eeca05b545`。
这是定制 AppWorld `0.1.4.dev0`；此前核过的官方 `0.2.0.dev0` 不用于冒充该复现。

已实际完成：

- 完整 checkout、4 个 LFS bundles、作者 editable package 与 `experiments[simplified]`
  安装、指定 `data-0.1.0.bundle` 下载与原生安装。作者 tracked source 的 diff 为空。
- 42 个公开源文件精确 Git blob 匹配、20 个 AST、5 个 Jsonnet 编译；作者 runner
  3 分支与 deterministic merge 接口核验。后两项使用边界替身，不称原生任务。
- train manifest 有 90 项，选择其第一项，与输出无关。`load_ground_truth=false`
  创建 AppWorld，执行公开 API metadata/current-task-status 两次调用，非空成功回执，
  正常关闭；耗时约 1.885 秒，模型/评分调用 0，test 任务加载 0。
- 原 no-GT 三角色 train 配置已写出；生成经验放在隔离 scratch，不用 online test
  学习的现成 playbook 作开发起点。公开 PR 只保存哈希/元数据，不再分发解包 task/DB。

初始 CLI 失败也保留：`typer==0.12.5` 与解析出的 `click==8.5.0` 报
`Secondary flag is not valid for non-boolean flag`。将 Click 固定为 `8.1.8` 后
原 CLI 安装/下载成功，没有修改作者 Python。119 个环境依赖版本已登记。

实际入口与证据：

```bash
python experiments/oacr_moe/baseline_capsule/native_appworld_smoke_v1.py \
  --source-root /absolute/pinned/ace_appworld \
  --output /absolute/output/native_smoke.json
```

使用上述隔离安装的 Python。结果在
`experiments/oacr_moe/baseline_capsule/NATIVE_APPWORLD_SMOKE_2026-10-02.json`；
完整 checkout 的独立预检在 `FULL_CHECKOUT_PREFLIGHT_2026-10-02.json`。
后者 `--require-model` 实际退出码 **2**：SambaNova/OpenAI/Together 凭据均不存在，
虽依赖模块齐全，授权模型仍缺。没有调用源码中的凭据字面量或下载模型。

**环境可运行不等于 ACE actor 完成任务。** 未执行 Generator/Reflector/Curator
闭环，未生成有效训练经验，未得官方 TGC/SGC。no-GT 的 `required_apis` 先验与
任务后 `test_report` 反馈必须分别记录；若做公开输入的三臂移植，共同移除该先验
并明确命名，不能偷偷改变作者原系统然后声称复现其成绩。

## 3. 第一版算子已经构造并接受原生核验

第一对象是 τ² retail 的当前效应、具体确认范围与一次性资格之间的可检查关系，
承接 BRFP 的实体/效应/当前授权。固定公开源码 SHA
`5bfa7e37b36656b37dc6d022156be6563c1007f3`，实现位于
`experiments/oacr_moe/authority_transport/`。

已交付 typed scope/action/confirmation/obligation，角色可见 READ 记录、guard/effect
summary、支持版本缓存、ready/spent/uncertain ledger、缺证据/干预窗口失效分支。
观察窗口默认不可信；自建串行协议明确认证后才准备调用。明确结构化确认
不是自然语言解析，summary 是人工审查后的有效片段实现，不是通用源程序编译器。

独立 verifier 保留目标函数及 8 个 helpers 的原始 body；仅去注册 decorator/工具
基类初始化，保留 upstream 顺序写入、末次 variant 等实际语义，逐 body 哈希登记。
它不是完整 τ² runner，未加载官方任务或私有目标。

唯一一次冻结开发运行包含 31 个自建 fixtures、每臂 97 次公开 READ、总共 62 次
source-body 写入调用 probe。每臂 8 admit/23 deny；20 个可检验 guard/effect
预测均匹配原生，admit 分支无不合确认效应。耗时约 0.044 秒。成功重复消费、
作用域/参数变化、缺来源、价格/付款、未明完成与干预窗口等边界均保留。
completion ledger 事件是明确的自建输入；这些 fixtures 不冒称完整合法原生对话历史。

**这一片段退为适配基础。** 候选只把 effect 精确相等作为 transport 条件，
而强经典 control 被允许相同语义 fallback。因此两者的规则就是同一个 predicate，
逐行相同的计数/状态是定义关系；native suite 审计的是源语义适配和有限 fixtures，
不是独立算法性能实验、完整成本相等定理或新颖性排除全部授权运输对象。
CPU 分别记录，未断言相等；native probe 与 READ 分开收费。一次性/可撤销证书
已有 LPCFS，任务 operand/provenance 授权已有 PAuth，不能单凭这两个形式升格。

## 4. 现在还缺什么，以及下一次构造要回答什么

保留已经打通的原生接口，但退出旧 read-view 与 exact-effect equality 的独有
核心主张。下一次投入必须先回答：**在强 actor 的实际合法轨迹里，哪些当前依据
或操作资格不能由现有完整经验/回查/正确维护以同样保证和成本获得？**
只有真实剩余缺口，才能决定研究新关系结构、可算 source-to-obligation 构造、
局部重取/再确认，或完整成本界；不预先给组合起新名字。

完整作者 actor 资源齐备后，先原方法，再同 actor/权限/预算加经典维护与候选；
保留全部角色、历史 fallback、反馈、缓存，官方结果/操作正确性/全成本分账。
24 个固定开发任务 × 3 seeds × 3 arms 是冷 arena 的候选预算，不是已冻结或已执行
的 216 episodes；seed 配置实际是否送给 provider 也须审计。原生权限与自然发生率
不支持目标时退出或换对象，不改评分造优势。

τ² 授权构造和 ACE/AppWorld 环境是两项独立资产；尚未找到同一机制的跨系统
实例，不把它们相加为跨系统证据。上述执行没有新独立确认、全球优先权或官方
收益。旧 512-unit bank 未读、未解封，旧结果与失败全部保留。
