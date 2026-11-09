# 评估结果

实际运行 21 项离线测试，全通过；见 [测试输出](../examples/test-results.txt)。本结论仅验证流程与工程边界，不证明真实模型决策效果。

| 验收点 | 场景 | 实际结果 | 证据 |
|---|---|---|---|
| A1 | normal | approved; saved; confirmed | [输入](../examples/normal/input.json)、[实际输出及 Trace](../examples/normal/output.json)、[资料](../examples/normal/fixture.json) |
| A2 | missing | missing_information; not_attempted; — | [输入](../examples/missing/input.json)、[实际输出及 Trace](../examples/missing/output.json)、[资料](../examples/missing/fixture.json) |
| A3 | risk | blocked; not_attempted; — | [输入](../examples/risk/input.json)、[实际输出及 Trace](../examples/risk/output.json)、[资料](../examples/risk/fixture.json) |
| A4 | conflict | approved; saved; pending_confirmation | [输入](../examples/conflict/input.json)、[实际输出及 Trace](../examples/conflict/output.json)、[资料](../examples/conflict/fixture.json) |
| A5 | duplicate_first | approved; saved; pending_confirmation | [输入](../examples/duplicate_first/input.json)、[实际输出及 Trace](../examples/duplicate_first/output.json)、[资料](../examples/duplicate_first/fixture.json) |
| A5 | duplicate_repeat | approved; duplicate; pending_confirmation | [输入](../examples/duplicate_repeat/input.json)、[实际输出及 Trace](../examples/duplicate_repeat/output.json)、[资料](../examples/duplicate_repeat/fixture.json) |
| A4/A5 | changed_occupancy | approved; updated; pending_confirmation | [输入](../examples/changed_occupancy/input.json)、[实际输出及 Trace](../examples/changed_occupancy/output.json)、[资料](../examples/changed_occupancy/fixture.json) |
| A6 | save_failure | approved; failed; — | [输入](../examples/save_failure/input.json)、[实际输出及 Trace](../examples/save_failure/output.json)、[资料](../examples/save_failure/fixture.json) |

额外测试包括用户确认、步数上限、跳过审核、非法发布工具、提前结束、无空闲槽位及批量防冲突。重复和更换占用时段测试断言数据库行数保持 1。

真实模型状态：未运行，无 API Key 配置与可用网络验证。必须补充至少两条 live 路径，证明工具观察改变了模型下一步选择；当前 mock 路径不可替代该要求。

已知限制：关键词风险检查不理解完整语义；只支持离散时段；没有多渠道容量、跨批事务、认证确认或真实发布；模型 JSON 解析失败会中止，不自动修复；保存失败可能发生在更新已有草稿时，此时旧草稿仍保留，失败表示本次修改未保存。查询和写入间占用变化会再次检查，真实模型须选择重查。

## 智谱迁移后的自动验收
[9 组场景报告](../examples/mock-validation/REPORT.md) 和 [结构化汇总](../examples/mock-validation/summary.json) 均来自实际离线运行。每项包含独立 input.json、fixture.json、output.json（含 Trace）、draft_snapshot.json 和 assertions.json。全部通过。

新增测试验证智谱目标地址和认证头、HTTP 错误脱敏、缺 Key 时不使用其他平台凭证、无效响应拒绝、旧风险草稿失效、保存失败保留建议、工具观察回传模型及异常动作安全结束。协议测试使用网络替身，明确不算 live 证据。

运行 `zsh scripts/run_live.zsh` 后，引用新生成的 live 报告，并人工核对至少两条不同结果引导的路径。模型返回完整工具调用链、冲突时选择替代、风险时阻断，均须用真实 Trace 证明。运行脚本不会自动声称满足真实 ReAct。
