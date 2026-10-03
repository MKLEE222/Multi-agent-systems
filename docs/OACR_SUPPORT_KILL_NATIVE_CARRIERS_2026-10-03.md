# OACR support lifecycle：公开原生载体核查

日期：2026-10-03。性质：公开源码与政策审查；没有执行 benchmark、AppWorld 环境、额外模型 API、评分或新任务，没有改动冻结 producer。这里只回答原生机制是否存在，以及合法观察能证明什么。**源码允许某历史，不等于已有官方任务实际发生该历史。**

## 1. 来源、权限与结论

| 载体 | 固定来源 | 本次观察边界 |
| --- | --- | --- |
| BFCL | `ShishirPatil/gorilla@6ea57973c7a6097fd7c5915698c54c17c5b1b6c8`；本地公开 `bfcl_eval/eval_checker/multi_turn_eval/func_source_code/gorilla_file_system.py` | 只读公开工具源码和既有协议文档；没有读取任务初始状态、gold 来建立当前事实 |
| τ² | `sierra-research/tau2-bench@5bfa7e37b36656b37dc6d022156be6563c1007f3` | 通过公共 GitHub 读取 retail/telecom 工具、数据类型、environment、toolkit、agent/orchestrator 和公开政策；没有读 DB、tasks、轨迹或评分 |
| ACE/AppWorld | `/workspace/scratch/7e7b92172dda/ocar_moe_runtime/ace_appworld`，`ace-agent/ace-appworld@9f3e92155345a9159f3a8b25abc334eeca05b545` | 只读公开 `src`。`src/appworld/.source/apps.bundle` 依公开安装器的解码方式在内存读出指定 app 源文件，未安装、解包写盘或导入运行 AppWorld；没有读取 `data/tasks`、outputs、DB、gold、private traces |

AppWorld 来源核实：author checkout 的 git origin 为 [ace-agent/ace-appworld](https://github.com/ace-agent/ace-appworld.git)。README 保留旧 `Alex-q-z/ace-appworld` 克隆链接；[旧仓库 API](https://api.github.com/repos/Alex-q-z/ace-appworld) 返回永久迁移至 repository ID `1096756401`，[现仓库 API](https://api.github.com/repos/ace-agent/ace-appworld) 返回同 ID、canonical `ace-agent/ace-appworld`、public；同 pin 可从 canonical 仓库取得。因此是同一 repository 的迁移，非另选 mirror。primary 源为[固定 pin 的公开源码安装器](https://raw.githubusercontent.com/ace-agent/ace-appworld/9f3e92155345a9159f3a8b25abc334eeca05b545/src/appworld/install.py)，本次不改旧冻结 manifest。

核查结论：

1. **BFCL 有真实的观察抽象缺口**：`sort` 在非退化序列化范围给出全部排序行的多重集，却通常不能证明 `tail` 的原始顺序。不是版本失效，也不需要假设外部写入。
2. **τ² 有原生动作资格消耗**：retail 修改 items 将 strict pending 状态改掉；可保持为真的产品事实和历史确认不能恢复资格。但原生没有 confirmation token/consumed ledger；已有 capsule 的 ledger/epochs 是适配层协议。
3. **τ² telecom 有合法、对 assistant 不可见的 user-tool 写入及同步效应**：付款与设备设置是确证的双角色机制。半双工调度限制了干扰区间，不能宣称任意时刻都可能外写。
4. **AppWorld 有真实 alternative guards、对象消耗和跨应用效应；本固定公开实现中没有查得独立自然后台写者。** 共享模型能被另一授权调用修改，不足以证明原 benchmark 正在发生未观察 external update。
5. 三者均未暴露可直接给 producer 使用的 generic exact readset/guard-dependency/effect extraction API。源码可支持少量函数的审计适配；schema 或 WRITE 标签不是精确依赖。

必须分开三类问题：

| 问题类别 | read 的作用 | read 不会自动完成的事 |
| --- | --- | --- |
| stale/不足的 observation | 取得当前被许可的状态投影，或补缺失的顺序/范围 | 给没有返回的字段、未来状态或未经观察的确认作证 |
| 当前 native eligibility 为 false/已 consumed | 证实当前不可用，必要时定位原因 | 恢复资格；恢复必须另有真实允许的世界动作或新 grant，原生一次性状态也可能没有恢复接口 |
| 文档/summary 不覆盖，或接口没有原子版本屏障 | 部分工具读可补数据 | 补齐缺少的语义模型或建立不存在的 CAS/no-interference；须降低保证或明确合同 |

## 2. BFCL：行多重集活着，顺序 support 不存在

[公开工具源码](https://github.com/ShishirPatil/gorilla/blob/6ea57973c7a6097fd7c5915698c54c17c5b1b6c8/berkeley-function-call-leaderboard/bfcl_eval/eval_checker/multi_turn_eval/func_source_code/gorilla_file_system.py) 的 `GorillaFileSystem.sort`，L483–502，读 `file._read()` 后返回 `"\n".join(sorted(content.splitlines()))`，**没有调用 `_write`**。内部排序保留重复行，不只是去重集合；输出丢失原行排列、原换行表示及末尾换行。精确地说，序列化也有退化边界：空文件的 `[]` 与单空行的 `[""]` 都返回空字符串，故不能无条件声称每个 sort receipt 唯一确定全部行多重集。

`tail`，L563–585，从原内容 `splitlines()` 取 `content[-lines:]` 后连接；`cat`，L388–408，返回原始字符串。因此，在已有观察只有同路径同内容版本的 `sort` 回执时，两个不同排列可有相同观察、不同 `tail` 回执。这是源码支持的不可辨识构造，不是声称某条官方任务已出现该失败。

适配也须保留源码的参数边界：这里 `tail(lines=0)` 因 `[-0:]` 返回全部行，negative lines 没有单独拒绝。不能把常见 shell tail 语义或数学 suffix 定义当作原码。

| 当前需求 | 旧 support | 可以合法修补的 read | 限制 |
| --- | --- | --- | --- |
| 再次 `sort` | 完整排序回执，在内容与文件绑定未受未知效应影响时足够 | `sort` 本身 | 不应为求尾顺序误把 sort 当作改写文件 |
| `tail(file, k)` | 通常只有排序回执不足；历史确证的原序 `cat` 或同参数 `tail` 可构成 alternative support | `tail(file, k)` 最直接；`cat` 可修完整原序 hole | `grep` 一般只有子序列，`wc` 只有计数；均不能一般修完整尾顺序 |
| 原始 `cat` 字节 | sort/grep/tail 的规格不同 | `cat` | 即使 tail 覆盖所有行，也没有证明原换行编码和末尾换行 |

“alternative” 在这里是**可替代的观察证据**，不是工具内的 OR guard。已完整观察的内容、已知 `echo` 写入内容、经审计 copy/move 传递的内容都可独立支持读预测；不能只固定一组 witness、丢掉它就宣布 query 不可答。无写入时，事实没有过期，但它的抽象粒度不够回答另一种需求。

`File._last_modified`，L25/35/54，是实际内部时间戳；本文件没有 public `stat`/version endpoint，cat/sort/tail 也不回传它。它不提供 producer 可用的版本通知、CAS 或 snapshot barrier。cp/mv 的内容及目录对象行为仍须按原码审计，不能将系统内部对象直接发给 producer。源码 SHA256：`84173750930b09aaa31b90547c9bd79ce75714682608b35e78a9c1ea259faf2b`。

## 3. τ² retail：原生资格与政策确认是两种 support

[工具源码](https://github.com/sierra-research/tau2-bench/blob/5bfa7e37b36656b37dc6d022156be6563c1007f3/src/tau2/domains/retail/tools.py) 中 `modify_pending_order_items`，L455–542：

- L481–483 严格要求 `order.status == "pending"`。
- L486–511 要求旧 item 多重性足够、列表等长、old/new 不同、同 product 的新 variant 可用，并计算价差。
- L514–518 要求所选 payment method 存在；gift card 才查余额覆盖价差。
- L521–530 追加 payment/refund 并更新 gift balance；L533–540 修改 items，设 `order.status = "pending (item modified)"`。

成功写的原生返回就是更新后的 `Order`。同一个订单下一次调用会被 strict status guard 拒绝，即使商品价格、可用性等其他已观察事实没有改变。`get_order_details`，L333–346，可合法查现在的 status；它能证明资格已失，**不能恢复资格**。重新取得用户 yes 也不把订单改回 pending。

[公开 retail policy](https://github.com/sierra-research/tau2-bench/blob/5bfa7e37b36656b37dc6d022156be6563c1007f3/data/tau2/domains/retail/policy.md)：L10–16 要求身份认证、单用户范围、写前列细节并取得明确 yes；L84/108–114 要求一次性 items 修改，收齐全部修改并确认。确认是会话中的授权依据，**不是工具参数中的一次性对象**。源码没有 confirmation ID、consume API 或 ready/spent 字段；不得把我们的 affine ledger 当成 τ² native feature。

政策与实现并非完全相等：policy L110 说修改后不能再 modify/cancel；`cancel_pending_order` 使用 strict pending，而 `modify_pending_order_address/payment` 使用 `_is_pending_order` 的子串检查（L132–140、L440–441、L568–569）。因此“原生所有修改接口都统一消费一次性资格”过强；政策层仍须独立检查。只读 DB 不会补齐用户确认语义或消除这类政策/代码差别。

### 真正含 alternative support 的 guards

| 目标 | 原生接受条件中的 alternative | 来源 | 合法 read 能取得什么 |
| --- | --- | --- | --- |
| 修改/交换 items 的支付资格 | `not GiftCard OR balance >= diff_price`，另有 method 存在等共同条件 | retail tools L514–518；exchange L265–276 | `get_user_details` 给 payment methods；`get_order_details` 给 items/user；`get_product_details` 或 `get_item_details` 给 variant 信息 |
| delivered return 的退款方法 | `GiftCard OR payment_method_id == original_payment_id`，共同要求 method 存在、delivered 和 items 多重性 | retail tools L689–707；policy L118–126 | user/order reads；当原付款本身为 gift card，两条 branch 可同时成立，丢其中一条 support 不应整体拒绝 |
| resume line 的原生状态资格 | `Suspended OR Pending Activation`，共同要求 customer owns line | telecom tools L298–330 | `get_details_by_id(line_id)` 和 customer 查询；**政策另要求无未付 overdue bill、合同未过期**，不得以 native status OR 取代政策 |

这些是公开源码中的实际析取。它们没有证明在固定官方任务上已有 support-kill 后 survivor 获益，也没有证明比正确的经典条件维护新颖。payment type/owner 稳定性应由可写字段分析证明；不能任意造一个不允许的 type 改写。

### exact dependency 的实际边界

固定 action 的必要字段可从源码总结：order existence/status/owner、items 的 ID 多重性和 product/price/options、product variants 的 membership/availability/price/options、payment-method membership/type/条件余额、写后 effect。已有 capsule `experiments/oacr_moe/authority_transport/native_retail.py` 是这一片段的公开 source-body 副本；manifest 已声明省 decorators/constructor，而非完整 native runner。

但 exactness 不可从几条字段名称自动推出：源码先计算价差，后修改循环仍使用前循环最后的 `variant`；重复 IDs 和 sequential substitution 都有作用。通用 AST 扫属性名会过粗，简单理想化配对会不正确。精确 guard 依赖、效果依赖、返回值依赖是三个不同集合；只有通过全路径/helper/别名/控制流审计后才可称这一受限片段 exact。

`ToolSignature` 只给 name/doc/params/returns（`environment/toolkit.py` L247–275）；`ToolType` 和 `mutates_state` 是粗标签/重放提示（L43–88）。没有 support alternatives、per-field read/write set、版本 receipt 或 certificate API。`get_db_hash` 是 environment/toolkit 后端接口，不能因为公开源码中可调用就给部署 producer 读取保护状态。

原生版本方面：[retail data model](https://github.com/sierra-research/tau2-bench/blob/5bfa7e37b36656b37dc6d022156be6563c1007f3/src/tau2/domains/retail/data_model.py) 的 Order/User/Product 片段无用于并发检查的 per-object version/confirmation epoch。现有 `authority_transport/README.md` 已明确：成功/无写入/不确定 completion ledger 输入是合成边界审计，`window_certified` 是明确协议前提，不能从未看见写入推断。

## 4. τ² telecom：hidden user updates 确实原生，区间也确实受限

以下链路全由公开原生代码支持：

1. [user_tools.py](https://github.com/sierra-research/tau2-bench/blob/5bfa7e37b36656b37dc6d022156be6563c1007f3/src/tau2/domains/telecom/user_tools.py) L1072–1090：用户 `make_payment()` 将 `PaymentRequest.paid = True`。
2. [telecom/environment.py](https://github.com/sierra-research/tau2-bench/blob/5bfa7e37b36656b37dc6d022156be6563c1007f3/src/tau2/domains/telecom/environment.py) L75–80：`sync_tools()` 发现 paid，就 `_set_bill_to_paid`，并清掉用户 payment_request；工具侧 L406–411 将 Bill.status 改为 Paid。
3. [agent/base_agent.py](https://github.com/sierra-research/tau2-bench/blob/5bfa7e37b36656b37dc6d022156be6563c1007f3/src/tau2/agent/base_agent.py) L38–44：agent 合法历史保留 assistant 消息、用户文字、assistant 请求的 ToolMessage；排除 user tool-call 及其工具结果。
4. [orchestrator.py](https://github.com/sierra-research/tau2-bench/blob/5bfa7e37b36656b37dc6d022156be6563c1007f3/src/tau2/orchestrator/orchestrator.py) L819–888：user tool call→ENV→USER，工具结果回送 requestor；用户发文字后才轮到 assistant。不是给 assistant 免费广播完整 user-tool ledger。

[main_policy.md](https://github.com/sierra-research/tau2-bench/blob/5bfa7e37b36656b37dc6d022156be6563c1007f3/data/tau2/domains/telecom/main_policy.md) L102–117 要求发送付款请求、用户付款后再次核实 Bill Paid；L125–128 要求付清 overdue 且合同未过期才可恢复线路。这给出明确的合法 repair：assistant 的 `get_bills_for_customer`（tools L335–358）/`get_details_by_id(bill_id)`（L233–259）重新观察 carrier 状态，而非读取 user DB。

但 `get_bills_for_customer` 默认 `limit=12`，是排序后截断的列表；不能凭默认前 12 条已 paid 推断所有 overdue 已清。要证明 policy 的全称条件，须封闭 customer.bill_ids 的相关范围并查对应账单，或取得覆盖全范围的合法查询结果。`get_details_by_id` 只修指定对象的 hole，不自动证明列表 completeness。

用户设备设置也是真原生 write：`toggle_data`、`toggle_roaming`、`toggle_airplane_mode`、`reboot_device` 等改变用户模型。carrier roaming 与手机 roaming 是不同字段；`sync_tools` L52–73 将 carrier line/plan 状态映到用户 surroundings。手机 `check_network_status`（user tools L142–177）、`check_sim_status`、`check_apn_settings`、`check_data_restriction_status`、`run_speed_test` 是 **user-side 合法 tools**；普通 assistant 只能按公开政策引导用户执行并报告，不能跨角色直接调用。solo mode 明确另外开放 user tools，因此应单独写观察合同。

这些 reads 是不同抽象：`run_speed_test` 的描述或随机 speed 不是全字段 snapshot，`check_network_status` 不含完整 surroundings。`_get_mobile_data_working` L214–244 依赖多项设备和环境条件，其中 abroad 时同时要求 phone roaming 和 carrier roaming；不能把一个“roaming enabled”事实笼统当成所有连通性的 support。[tech_support_manual.md](https://github.com/sierra-research/tau2-bench/blob/5bfa7e37b36656b37dc6d022156be6563c1007f3/data/tau2/domains/telecom/tech_support_manual.md) 给出这些合法诊断流程。

**限制**：半双工中，assistant 发起工具调用后回执回到 assistant，若它继续调用另一个工具，不会在两者之间插入 user turn。用户侧隐藏改变可以发生在交给用户期间；不能用此来源声称连续 assistant `read→write` 区间也有任意后台干扰。`set_data_usage`、`set_user_location`、断网/锁 SIM helpers 等未注册的 initialization/assertion 接口也不能当作角色可合法调用的外写。

还有一个适配细节：[通用 Environment.get_response](https://github.com/sierra-research/tau2-bench/blob/5bfa7e37b36656b37dc6d022156be6563c1007f3/src/tau2/environment/environment.py) 调用工具后会 `sync_tools`。工具方法的 READ 标签不足以证明整个 dispatch 对所有角色状态纯读；应总结同步读写效应，不能直接用标签建立 frame guarantee。

## 5. AppWorld：真 guards/consumption 可查；自然外写未成立

公共安装器 `src/appworld/install.py` L9–32 说明 app 实现位于 `src/appworld/.source/apps.bundle`。本次仅在内存读取其 app source members；以下行号是**bundle 内解码源文件**，不是任务数据。可复核公开 [安装器](https://github.com/ace-agent/ace-appworld/blob/9f3e92155345a9159f3a8b25abc334eeca05b545/src/appworld/install.py) 及同 pin 的 source bundle。bundle SHA256：`ed68e817a989a6dc23d9c010f21d874b8cd0420aa9321d9f18a6252da0a7d388`。

| 原生机制 | 精确源码位置 | 可见性/repair |
| --- | --- | --- |
| Venmo transaction 的 alternative authorization | `apps/venmo/apis.py` L997–1008：拒绝条件是 `private AND sender != self AND receiver != self`；接受该 guard 即 `public OR sender=self OR receiver=self`，另需未点赞 | `show_transaction` L648–687 返回 private、sender/receiver 名字和 email、updated_at；合法查询可修这些可见 hole。不能先读取无权访问的 private transaction 来证明授权 |
| 原生合法 privacy 写入 | Venmo `update_transaction` L752–776 只准 sender 修改 private/description | sender 把 public 改 private 仍有 sender branch。它是可审计的 branch-survival 载体；未声称某固定任务里自然发生此序列，也不改 task 来强行要求它 |
| 一次付款请求的资格 consumed | Venmo `approve_payment_request` L1601–1654：要求 receiver=self、approved_at/denied_at 均空；成功设置 approved_at 并转款/建交易/通知 | `show_received_payment_requests` L1406–1458 返回这些字段，按 status 分页；合法完整翻页可确认当前对象，单页缺席不能证明全局不存在。重新 read 能识别 consumed，不能重新开放它 |
| 草稿对象消耗 | Gmail `send_email_from_draft` L1886–1957，在权限、收件人、内容等检查后发送并 `draft.delete()` | `show_drafts`/`show_draft` 可查当前存在性；原内容事实或旧 draft receipt 不再支持执行相同 draft ID |
| 跨应用/跨用户模型效应 | Phone `send_text_message` L618–659 同步创建 sender 与 receiver 的 UserTextMessage；Venmo receipt 下载 L965–979 调 file_system 写文件并增加下载计数 | 这是 agent 已调用 write 的更广 effect；不是未观察 external actor。receipt 对某字段缺失，也不等于该字段没改 |

Venmo 源 member SHA256：`14894a0bc4fa3cb5ccaf52cd927c3484752d367075ef6f194a41cf17e0456c1d`；Gmail APIs：`064472ab4ab40328d054b44a7c6ec88975955bd18d8b881e8b289bc5fdd9c0d0`；Phone APIs：`b32c231f29515f0c77175e6cb3bd3cd91254237545f2230eb5166a102e250338`。

### 版本、时间与 observation API

- `environment.py` L375–381 将时间冻结为 task datetime；L85–108 默认 `allow_datetime_change=False`，注释明确测试参数不得改给实际模型。不能通过放开时间/补 external writer 制造原生失败。
- Venmo `show_transaction` 可见 updated_at，`update_transaction` 设 `DateTime.now()`。冻结时间下多次不同写可有同一 updated_at；**不是每写单调 version**，不能替代未观察写入通知或 CAS。
- `apps/model_lib.py` L182–225 的 DBChangesTracker 记录 SQL 写，L1101–1111 的 ModelHash/record_hash 用于后端比较、评估；它们是 native 内部维护机制，**不是 agent 的合法 freshness feed**。`DB_VERSION` 是代码/数据兼容版本，也不是对象 epoch。
- bundle `apps/api_docs/apis.py` L90–148 的 `show_api_doc` 返回 path/method/description/parameters/response_schemas；公开 `src/appworld/api_docs.py` L173–354 从 OpenAPI 建这些文档，`collections/api_docs.py` L42–60 排除 private APIs。没有 exact guard formula、conditional readset、write effect、alternative proofs 或 snapshot/version certificate。
- 扫描公开非 admin/non-supervisor app API 的函数参数，未找到 expected_version/etag/revision/epoch/if_match 等乐观并发条件；这只是本 source pin 范围的阴性核查，不是对所有未来 AppWorld 版本的断言。
- `apps/__init__.py` L121–128 明确 No-API-Docs/Private-API 为行政用途，agent 不应直接访问。公开源可供离线审计，不能因此将 `models`、DBChangesTracker、admin 数据或全 state 作为在线 producer 的合法观察。

`environment.py` 的本地执行由代码/API 调用推进，时间固定；对 runtime、requester、API library 与非 admin/non-supervisor app source 的后台 task/thread/scheduler 候选扫描没有找到独立自动写者。Gmail 有 scheduled_send_at 数据与草稿 API，不能从字段名字推断当前代码存在自动发送线程。因而本固定实现最多支持“另一个经授权的调用可以修改共享状态”的条件推演；**不能写成 AppWorld 原任务天然有未观察 external writes**。远程服务器若另接 writer，则须明示新增执行合同，不再冒充原固定 benchmark。

## 6. 强 certificate 何时不能成立

这里的 strong certificate 指：不取得新的相应观察，仍保证当前 query/guard/effect 在执行点正确。它不等于“最终工具会再次检查并拒绝坏状态”。

**信息不足反例条件**：存在两个合法 native histories，producer 可见 prefix 完全相同，当前 query/guard/effect 不同。则只靠此 prefix 的算法不能对两者都给正确确定结果；与它是检索、证据图还是经典维护无关。

| 场景 | 是否支持上述反例 | 合法解决边界 |
| --- | --- | --- |
| BFCL 只有 sort，需求变为 tail | 是：无需写入，两个原排列即可 | 当前 tail/cat read 修所需抽象；不能把“sort 输出仍真”升级成 tail 证据 |
| τ² retail 成功修改后的产品事实仍真 | 资格已实际改变，成功回执本身可见 | 原生 status/已知 effect 能准确拒绝；缺 completion 才需要合法 order read。不能把确认历史重用当再授权 |
| telecom 用户 turn 可执行付款/设置，而未向 assistant 文字报告 | 是：不同 user-tool 历史可有相同 assistant 可见 prefix | assistant carrier read、用户诊断并报告；转回 assistant 后，半双工连续 read→action 可利用实际调度保障 |
| AppWorld 默认本地 runtime 凭“可能其他用户变更” | 本次源码不能证明自然历史存在 | 不得制造 external actor/时间前进来声称原生反例；先取得真实允许的执行合同 |
| 任意系统明确允许相关 hidden writes，且没有锁/版本条件/快照屏障 | 若写可改变目标且没有剩余不受影响的 alternative，则是 | read 只保证 read 时点。读后还能外写时，重复 read 也不能保证未来 exact effect；须原子 native guard/CAS/锁/已声明 no-interference，或降低保证 |

没有看见 external write，**不等于**没有 external write。反过来，允许外写也**不等于**所有 certificate 都不可能：不可变字段、已证明 writer 不触及的依赖、各可能状态中不变的答案、存活的 alternative support 都可保留保证。需对目标相关的可写域和调度做证明，不能全局一律 invalidate 或全局一律 trust。

单次合法 read 能修 observation hole；无法恢复 native consumed resource，无法取得缺少的用户授权，无法自动封闭 TOCTOU 窗口。访问保护 DB 或 verifier 的全状态可以让审计器看见答案，但不构成部署 producer 的修补。

## 7. 是否值得最低实现

**本轮不建议进入新的候选实现或扩跑。当前没有发现正确强经典控制不能覆盖的独立结构残差。** 已查源码可作为现有适配的审计清单；如果以后另有独立可区分保证/成本构造，再按以下边界另立实现，不能由本次载体存在本身推出新核心：

1. BFCL 分开 `RawContent`、`OrderedLines`、`LineMultiset`、`Suffix(k)` 的 support，不从 sort 升格出顺序；内容/路径绑定效应沿已有合法写回执维护。
2. τ² 分开状态资格、政策身份/用户确认、历史事实；原生成功状态消耗可由 source effect 维护，未知 completion 保持 unknown；不要新增 native confirmation/version 幻觉。
3. 只把上表少量 actual OR guards 登记为 alternatives；source/policy/receipt 程度、共同条件、branch dependencies 和修补 endpoint 一并记载。survivor 仍须完整满足共同 guard 与政策。
4. 把 telecom 的用户 turn 作为实际调度边界，carrier 与 phone scopes 分开；共享 source summary 包括 sync effect。AppWorld 先限已观察动作/固定时间，external writer 若没有真实合法来源就不加入。
5. 输出 unresolved hole 及可用合法 read；不修改 task/user、工具前置条件、评分或官方分母来强造击杀。新实现另建新 freeze；本次冻结 producer 不变。

还需先把目标合同写完整：若 min cost **只要求每次 commit 安全，没有必须完成的任务、目标进度或最低 commit 约束**，零 commit、零取证可平凡达到成本 0，不能据此要求 query repair 或声称最优有效操作算法。世界中 guard 为 false 时，read 只能知道 false；不能把所有 hole 都写成一定可由 query 修成可提交。

上述机制足以检查“支持的种类、资格生命周期与可观察区间”是否被错误混为普通事实缓存。它仍是标准抽象解释、依赖/条件维护和 typestate 的适配义务。若正确经典对照实现同样机制后追平，就应结束独有内核主张；现有公开源码核查没有给出它们无法追平的结果或成本分离。
