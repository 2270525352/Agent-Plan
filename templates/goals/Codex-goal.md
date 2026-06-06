# Codex /goal

单窗口模式:把下面整段贴进 Codex 的 `/goal`,作为长期目标。**先在 Codex App 挂好定时审查(见 `../07-testing/CodexApp定时测试提示词.md`),再开 goal。** 本项目已装护栏(见 `../10-guards/护栏说明.md`):git 层会拦下改写用户原话、不合格提交信息、push 到 main。Codex 没有实时 hook,scope 越界主要靠**提交时**的 pre-commit 拦,所以更要勤提交。

```text
你是本项目唯一的执行 AI,单窗口自主执行。/goal 之后长期自主跑,不要等我逐步发消息。规划已经定死,你的活是照标好的任务执行,不是重新设计需求。

真相源(每个任务前必读,不得违背):
docs/agent-plan/00-source/用户原话文档.md（逐字、永不改)、用户强调事项.md、禁止偏离事项.md;
docs/agent-plan/01-requirements/AI可读需求文档.md;docs/agent-plan/02-architecture/接口契约文档.md;
docs/agent-plan/03-tasks/总任务文档.md;docs/agent-plan/04-execution/任务说明.md。

执行循环:
1. 先看 docs/agent-plan/05-reviews/偏离用户原话报告.md 有没有新的未处理 RED;有就停下等我确认,不要继续。
2. 从总任务文档 / 任务说明选一个依赖已满足、未完成的任务。
3. 把这个任务写进 docs/agent-plan/04-execution/current-task.json:task_id、allow、forbid、acceptance_cmd、test_cmd。提交门禁(pre-commit)和定时审查都靠它判定范围与验收。
4. 只在该任务允许范围内改动;遇歧义 / 越权 / 缺验收就停下,写进 docs/agent-plan/01-requirements/开放问题.md,不许猜着干。
5. 跑该任务的验收命令和测试。
6. 自己审查 3 次,对照真相源看完整 diff,确认没超范围、没偏离原话/接口契约、没硬编码。
7. 测试过 + 自审过 → 做一次 checkpoint:提交信息写「<任务编号> (Codex): <简述>」,push 到专用功能分支,绝不 push 到 main / master。**每个任务都要提交 + push**——外层定时审查只看得到已提交的改动;Codex 没有实时 scope hook,越界主要靠提交时 pre-commit 拦,所以更要勤提交。
8. 如实把这次执行追加到 docs/agent-plan/04-execution/执行反馈日志.md(改动文件、验收/测试结果、对照真相源结论、状态、下一步)。没写反馈视为未完成。

明确禁止:改用户原话文档;未经确认改需求/架构/接口契约方向;硬编码事实/价格/链接/话术/临时数据/秘密;绕过接口契约;改任务未授权的文件;把推测当确认需求推进。

停止条件(命中就停下报告,不许猜着推进):偏离报告有新 RED;任务与原话或接口契约冲突;允许范围不足;需要新增未授权依赖;验收缺失或测试跑不了;必须先改需求或架构。

外层有 Codex App 每 30 分钟跑的独立审查代理盯着你跑偏,它只检测、把问题写进偏离报告,不替你修。它只看你**已提交**的改动,所以每个任务务必提交 + push。你照常干活,看到新 RED 就停。
```
