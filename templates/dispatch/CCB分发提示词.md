# CCB 分发提示词

## 使用说明

CCB 负责分发和协作。`/goal` 不是 CCB 通用命令，而是 Claude 和 Codex pane 的 provider 命令。

OpenCode 默认不使用 `/goal`。

## 手动设置 goal

在 Claude pane 输入 `/goal`，粘贴：

```text
docs/agent-plan/06-goals/Claude-goal.md
```

在 Codex pane 输入 `/goal`，粘贴：

```text
docs/agent-plan/06-goals/Codex-goal.md
```

## CCB ask 分发模板

### 给 Claude

```text
/ask claude 请读取 docs/agent-plan/04-agents/Claude任务文档.md，并按其中任务执行。执行前必须检查用户原话、AI可读需求、总需求、总架构、接口契约、总任务和自动模式门禁。不得让 Codex 执行未审查通过的任务。
```

### 给 Codex

```text
/ask codex 请读取 docs/agent-plan/04-agents/Codex任务文档.md，并只执行其中已授权的代码任务。不得修改用户原话、需求方向、架构方向、prompt 或 AI 策略。发现歧义或越权需求时停止并报告。
```

### 给 Reviewer-Claude

```text
/ask reviewer 请读取 docs/agent-plan/04-agents/Reviewer-Claude任务文档.md，对 Agent-Plan 文档树做需求对齐、架构一致性、任务冲突和自动模式门禁审查。只输出审查报告，不实现代码。
```

### 给 OpenCode

```text
/ask opencode 请读取 docs/agent-plan/04-agents/OpenCode审查任务文档.md，对当前实现或任务计划检查硬编码、接口偏离、测试缺口、未授权改动和实现风险。只输出技术审查报告。
```

## Shell 形式

```bash
ccb ask claude <<'EOF'
请读取 docs/agent-plan/04-agents/Claude任务文档.md，并按其中任务执行。执行前必须检查用户原话、AI可读需求、总需求、总架构、接口契约、总任务和自动模式门禁。不得让 Codex 执行未审查通过的任务。
EOF
```

