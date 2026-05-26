# CCB 多 AI 执行模式

## 适用条件

- 项目安装并启动 CCB。
- 至少有 Claude 和 Codex。
- 可选 OpenCode。
- 用户希望多代理并行讨论、审查、执行。

## 执行顺序

1. Claude 维护用户原话、需求、架构、总设计、总任务。
2. Claude 和 Codex 在 CCB 里讨论任务边界。
3. Reviewer-Claude 审查文档。
4. 多个 Codex App 代理或 Reviewer 代理审查文档是否对齐需求。
5. 审查通过后，在 Claude 和 Codex pane 设置 `/goal`。
6. 用 CCB `/ask` 或 `ccb ask` 分发任务。
7. Codex 执行代码任务。
8. OpenCode 或 Reviewer 审查实现。
9. 通过验收后更新状态并按 Git 提交纪律提交。

## 禁止

- 未通过自动模式门禁就进入自动执行。
- 让 Codex 自由拆需求。
- 让 OpenCode 定义需求。
- 把 `/goal` 当作 OpenCode 默认能力。

