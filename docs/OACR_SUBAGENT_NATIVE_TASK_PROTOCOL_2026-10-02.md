# 子代理原生任务尝试：冻结协议

日期：2026-10-02。用户明确授权子代理执行任务。使用已安装的作者 AppWorld
`0.1.4.dev0` / source `9f3e92155345a9159f3a8b25abc334eeca05b545`。

## 本轮要回答的问题

子代理能否凭公开任务、动态 API 文档与原生回执，在真实 train 环境中选择行动、
完成任务，并通过未修改的作者评分器？这补齐此前“原生环境可启动、没有 actor”
的工程缺口。它不是原 DeepSeek-V3.1 的成绩复现，也没有执行完整 ACE 反思、
curation 或跨任务经验更新；不据此宣称 OCAR 算法优势。

## 冻结样本与输入

按原 train manifest 的先后取前 3 个 ID，不看任务输出、难度或 gold 后选样。
三项是 **同一 scenario 的三个 task variants**，不得当三个独立场景。选择哈希、
manifest 哈希与实现 SHA 已写入 `experiments/oacr_moe/subagent_actor/freeze.json`。
3 位 cold subagents 分别接入 fresh world；fork none，仅收到桥接使用说明。

actor 输入使用作者默认 generator template 的公开示范、原 initial playbook、
当前任务与 supervisor 公开资料，以及自己实际取得的全部回执。不载入 ground
truth、不提供 required API oracle、私有状态、参考动作、评分结果或其他 actor
轨迹。不注入 OCAR/近邻失败结论。actor 自己选择 Python 原生调用，变量保留于
环境 REPL；不使用固定领域脚本替它做任务。

执行窗口为每 actor 至多 40 次 execute requests（错误亦计请求），native 单段
timeout 20s，环境 seed 123。子代理模型继承当前系统；其版本、抽样 seed、token
和账单未暴露，不能声称同原 DeepSeek backbone 或完整公平的成本比较。

## 接口与评分分离

原 v1 Unix socket 创建被当前环境拒绝（PermissionError），3 个启动均止于
actor 行动前；没有模型、native execute 或评分。失败保留并重新冻结 v2，样本/
预算不变，使用原子文件消息队列。桥仅公开 `start/execute/finish`；host actor 指令仅允许调用该 client，
禁止读文件/源码/后端/任务 labels、联网找答案、另起模型或继续委派。桥有补充 AST
禁读项及原生 safety guard。共享 workspace 的 prompt 合规不是 OS 级隔离证明，
因此保存全部经桥输入/回执供审计，不称对抗式安全保证。

actor 完成原生 `supervisor.complete_task` 后或主动认定无法继续时，发送 finish；
先关闭 actor endpoint，后由 controller 单次调用原作者 `evaluate_task`。评分不
返回 actor，不进行按评分修补/重跑/删失败。环境错误、失败、预算耗尽都保留。
若 actor 未能终止，controller 终止它并按未完成计入，不换任务。

Native interaction/API 调用、输出 bytes、桥拒绝、原生错误、时间和轨迹 hash
分别记账。子代理确实用了模型；只有 external provider API calls 是 0。token/
美元未知不能写成零。指标是三个 train variants 的原生逐 task success 与测试
通过计数；不是完整测试集 TGC/SGC 或泛化估计。

## 可复现资产与信息边界

桥和 client 位于 `experiments/oacr_moe/subagent_actor/`。保护任务、prompt、完整
回执和轨迹放在私有 scratch；公开仓库仅保存 metadata/hash/聚合或合规加密
bundle。旧冻结 producer、旧结果和 512-unit bank 不改、不读、不解封。

实际子代理完成轨迹后，才据可见行动分析依据维护的候选机会；评价结果是此后
的开发诊断，不能回称独立确认。若三项都成功，保留强 actor 能力这一事实，
不编造需要 OCAR 修复的失败。
