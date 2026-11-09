# 项目一：素材审核与发布排期 Agent

帮助内容团队读取素材、检查规则、查询时段并保存排期草稿。**不接发布接口，永远不声称已发布。**

当前状态：可运行 CLI；21 项离线测试通过，9 组自动验收全部通过。智谱真实模型适配器及脱敏错误诊断已实现，尚待用户终端运行验证；没有两条真实模型 Trace，不能视为完整达标提交。

## 环境与安装
Python 3.9+，仅标准库；本次实际验证 Python 3.14。无需 pip 安装、框架或部署。

```bash
cd agent-content-scheduler
python3 -m unittest discover -s tests -v
python3 -m examples.generate
python3 -m src.agent --mode mock --input examples/conflict/input.json --db demo.sqlite --output examples/manual-mock.json
```

上面冲突案例：要求 18:00，已占用，建议 19:00；保存待确认草稿。重复执行同一命令只保留一份草稿。所有时间都包含日期与 +08:00 时区。

## 真实模型运行：智谱开放平台普通 API

使用智谱标准 API，固定端点 `https://open.bigmodel.cn/api/paas/v4/chat/completions`。默认 `glm-4-flash-250414`；可通过 `ZHIPU_MODEL` 选择账户可用模型。不使用 Coding Plan 或 OpenRouter 地址。

最简单的方式：

```bash
zsh scripts/run_live.zsh
```

脚本会隐式输入密钥（不显示、不保存）；若你之前误把智谱密钥设置为 `OPENROUTER_API_KEY`，只在该脚本内沿用为 `ZHIPU_API_KEY`。Python 接口只读取 `ZHIPU_API_KEY`。所有请求仅发送至智谱。

该命令自动运行 9 组场景，包含全部 6 个验收点、重复请求、更换占用时段及确认流程；保存实际输入、输出、Trace、草稿快照、断言和报告到独立的 `examples/live-时间戳/` 目录。每个场景最多 12 次模型调用、每次超时 30 秒；遇到模型接口错误即停止整个验证，避免连续无效请求。不会伪造通过结果。

手动配置方式（Mac zsh）：

```zsh
read -r -s 'ZHIPU_API_KEY?粘贴智谱普通 API Key 后按回车：'
echo
export ZHIPU_API_KEY
export ZHIPU_MODEL=glm-4-flash-250414
python3 scripts/evaluate.py --mode live --output examples/live-manual
```

密钥仅存在当前终端进程环境；不用写入 `.env`。真实调用可能消耗账户额度。认证或余额问题将显示 HTTP 状态码、平台错误码和脱敏错误说明，无须反复更换密钥。

单次运行和失败注入：

```bash
python3 -m src.agent --mode live --input examples/conflict/input.json --db demo-live.sqlite --output examples/live-single.json
python3 -m src.agent --mode mock --input examples/save_failure/input.json --fail-save --db failure.sqlite --output examples/failure-manual.json
```

确认替代时段：用户在输入 JSON 加入 `"confirmed_slot":"2026-11-10T19:00:00+08:00"` 后重跑；模型不能生成用户确认。所有时间都包含日期与时区。仅支持用户控制的本地 CLI 输入，未实现在线身份认证。

## 评审入口
1. [业务与验收点](docs/01-requirements.md)
2. [设计和取舍](docs/02-solution.md)
3. [测试与证据](docs/03-evaluation.md)
4. [AI 使用说明](docs/04-ai-usage.md)
5. [复盘和用时](docs/05-retrospective.md)

每份 `examples/*/output.json` 包含各项审核状态、风险原因、建议时段、待确认项、保存状态及完整 Trace。`completed` 仅表示审核/草稿处理结束，可能包含被阻断素材；不表示所有素材通过、用户确认或已发布。

## 提交前尚需完成
配置真实模型并运行全部业务验收，至少保留两条不同动态决策路径；更新评估文档；填写本人真实修改及学习收获；仓库：https://github.com/sijiameng107/agent-content-scheduler 。提交真实验证结果后记录最终完整 SHA，向指定评审账号开放读取。当前版本仍待真实模型验证，不能作为最终达标声明。
