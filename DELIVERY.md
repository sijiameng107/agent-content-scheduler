# 项目一交付说明

## 最短运行
Python 3.9+，无第三方依赖。解压后进入 agent-content-scheduler：

```bash
python3 -m src.agent --mode mock --input examples/conflict/input.json --output result.json
python3 -m unittest discover -s tests -v
```

真实模型批量运行（可选，不影响查看交付物）：`zsh scripts/run_live.zsh`。密钥仅在本地输入。

## 实际状态
- 25 项离线单元/边界测试通过，9/9 离线场景通过。
- 第一次真实模型验收 2/9，第二次 7/9；两个目录保留原始输入、输出、Trace、断言、草稿快照和报告。
- 第二轮 conflict 第 3 步观察 18:00 冲突，第 4 步建议并保存 19:00 待确认草稿；changed_occupancy 改用 20:00；risk 阻断；save_failure 如实失败并结束。可用于核对动态决策路径。
- 第二轮 normal 未优先原定空闲时间；confirmed_alternative 提前结束。这两项已修正控制边界并通过离线测试，在第三轮通过。
- 无真实发布、无重复草稿、无真实密钥。全部材料均在本包。

## 正式提交限制
原考核要求题号、GitHub URL、最终 commit SHA 和指定评审账号读取权限。

## 文档与证据
- docs/01-requirements.md：用户、范围和验收标准
- docs/02-solution.md：模型循环、工具、幂等与确认边界
- docs/03-evaluation.md：证据链接与失败分析
- docs/04-ai-usage.md：AI 辅助及用户实际操作
- docs/05-retrospective.md：问题、改进及时间口径
- examples/live-20261109-211901/：第一轮真实运行
- examples/live-20261109-212930/：第二轮真实运行
- examples/mock-validation/：当前离线验收

2026-11-10 真实智谱运行 9/9 通过。[完整报告](examples/live-20261110-144836/REPORT.md)。
