# 方案与取舍
采用 Python 标准库 CLI + SQLite；无第三方框架。任务规模小，显式循环方便评审动态行为、预算与边界；SQLite 事务和主键比单纯 JSON 文件更适合防重复与并发写入。

LiveModel 每一步接收用户任务和已有工具观察，自行选择 read_material、check_rules、query_slots、save_draft 或 finish。控制器校验参数后执行，再将观察返回模型。因此模型可根据风险、缺失、冲突选择下一动作，执行骨架并不固定工具序列。MockModel 是确定性测试替身，不证明真实 ReAct 能力。

read_material 读取合成元数据；check_rules 记录审核结果；query_slots 合并已有排期与数据库草稿；save_draft 强制检查审核及查询前置条件，并在 BEGIN IMMEDIATE 事务中再次检查冲突。模型不能直接修改确认状态、保存成功状态或 published 字段。没有 publish 工具。

幂等标识 = SHA256(material_id + requested_slot + campaign)。同一标识的完全相同草稿返回 duplicate；时段或确认变化时更新同一行。保存异常回滚并返回 save_failed。一次运行可处理多素材，之前保存的提案会影响后续素材查询。

预算覆盖每轮模型动作，包括错误工具调用。默认 12 步，达到上限返回 incomplete/limit_reached。模型异常返回 incomplete/model_error，不自动降级。提前 finish 时检查未处理素材，避免虚报完整成功。

真实接口依据智谱官方文档：https://docs.bigmodel.cn/cn/api/introduction 以及 https://docs.bigmodel.cn/cn/guide/models/text/glm-4 （2026-11-09 查阅）。使用普通 API 的 Bearer 认证和 JSON 输出，默认 glm-4-flash-250414。没有使用 Coding Plan 或 OpenRouter。真实网络集成仍待用户终端验证；协议单元测试验证了目标地址、认证头及错误脱敏，不能代替真实调用。

本轮改进：保存失败仍保留建议时段与待确认项；规则检查发现风险或资料缺失时，将已有草稿设为 inactive 并释放槽位。一次运行在永久保存失败后不重复保存，已保存后禁止同一运行改写；跨运行通过稳定主键更新。响应缺失、截断或 JSON 无效时不执行工具；HTTP 错误显示脱敏状态码和提示；拒绝接口重定向，避免凭证发送到其他地址。

交付版新增两道业务检查：原始/已确认的优先时段空闲时拒绝任意改选；有未完成审核/保存任务时拒绝提前 finish 并反馈未完成素材。两者只拒绝无效动作，不替模型选择下一工具或宣告成功；步数上限仍然生效。
