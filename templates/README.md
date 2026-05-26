# Agent-Plan Templates

These templates are copied or adapted into a target project's `docs/agent-plan/` tree.

Agent-facing documents should stay AI-readable: stable fields, explicit scope, forbidden scope, acceptance criteria, stop conditions, and status fields.

## Template Map

| Target directory | Templates | Purpose |
|---|---|---|
| `00-source/` | `用户原话文档.md`, `用户强调事项.md`, `禁止偏离事项.md` | Preserve original user intent and hard boundaries |
| `01-requirements/` | `总需求文档.md`, `AI可读需求文档.md`, `需求对齐检查表.md`, `开放问题.md` | Convert raw words into executable requirements |
| `02-architecture/` | `总架构文档.md`, `架构图.md`, `总设计文档.md`, `接口契约文档.md` | Define architecture, design, diagrams, and frozen interfaces |
| `03-tasks/` | `总任务文档.md`, `任务依赖图.md`, `阶段交付计划.md` | Define phases, dependencies, and task acceptance |
| `04-agents/` | `分工总说明.md`, `Claude任务文档.md`, `Codex任务文档.md`, `Reviewer-Claude任务文档.md`, `OpenCode审查任务文档.md` | Split work by agent capability and forbidden scope |
| `05-reviews/` | `需求对齐审查.md`, `架构一致性审查.md`, `任务冲突审查.md`, `偏离用户原话报告.md`, `自动模式门禁.md` | Review before automation and track drift |
| `06-goals/` | `Claude-goal.md`, `Codex-goal.md` | Provider `/goal` prompts for Claude and Codex |
| `07-dispatch/` | `CCB分发提示词.md`, `CodexApp定时审查提示词.md` | CCB asks and Codex App automation prompt |
| `08-runtime/` | `CCB多AI执行模式.md`, `单AI执行模式.md`, `CodexApp自动化模式.md` | Execution modes with or without CCB |
| `09-git/` | `Git提交纪律.md`, `提交检查表.md` | Git checkpoint and commit discipline |

## Maintenance Rules

- Keep Chinese filenames because the intended workflow uses Chinese planning documents.
- Keep task and review templates field-based.
- Do not rename `Claude任务文档.md`, `Codex任务文档.md`, or `Reviewer-Claude任务文档.md` back to CC/CX names.
- Treat OpenCode as review-only and no-`/goal` by default.
- Keep single-agent mode available for users without CCB.

