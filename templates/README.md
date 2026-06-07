# Agent-Plan Templates

These templates are copied or adapted into a target project's `docs/agent-plan/` tree.

Agent-facing documents stay AI-readable: stable fields, explicit scope, forbidden scope, acceptance criteria, stop conditions, and status fields. The skill targets a single executing AI (one Claude or one Codex), with self-check plus scheduled testing as drift defense.

## Template Map

| Target directory | Templates | Purpose |
|---|---|---|
| `00-source/` | `用户原话文档.md`, `用户强调事项.md`, `禁止偏离事项.md` | Preserve original user intent and hard boundaries |
| `01-requirements/` | `总需求文档.md`, `AI可读需求文档.md`, `需求对齐检查表.md`, `开放问题.md` | Convert raw words into executable requirements |
| `02-architecture/` | `总架构文档.md`, `架构图.md`, `总设计文档.md`, `接口契约文档.md` | Define architecture, design, diagrams, and frozen interfaces |
| `03-tasks/` | `总任务文档.md`, `任务依赖图.md`, `阶段交付计划.md` | Define phases, dependencies, and granular task acceptance |
| `04-execution/` | `任务说明.md`, `执行反馈日志.md`, `current-task.json` | The single AI's scope, task list, self-check cadence, append-only execution feedback, and the per-task guard state |
| `05-reviews/` | `需求对齐审查.md`, `架构一致性审查.md`, `偏离用户原话报告.md`, `自动模式门禁.md` | Review before automation and track drift |
| `06-goals/` | `Claude-goal.md`, `Codex-goal.md` | Provider `/goal` prompts for autonomous single-AI execution |
| `07-testing/` | `定时测试方案.md`, `ClaudeCode定时任务提示词.md`, `CodexApp定时测试提示词.md` | Scheduled drift testing: run tests + re-check source of truth |
| `08-runtime/` | `单AI执行模式.md` | The single-AI execution loop and stop conditions |
| `09-git/` | `Git提交纪律.md`, `提交检查表.md` | Git checkpoint and commit discipline |
| `10-guards/` | `护栏说明.md`, `settings.hooks.json`, `current-task.json`, `hooks/*.py`, `githooks/*` | Deterministic enforcement: Claude Code hooks + git hooks (installed to `.claude/` and `.githooks/`) |

## Maintenance Rules

- Keep Chinese filenames because the intended workflow uses Chinese planning documents.
- Keep task and review templates field-based and granular.
- The executing AI may be Claude or Codex; keep both `/goal` prompts in sync.
- Drift defense is two-layer: AI self-check (inner) + scheduled testing (outer). Keep both wired.
- Match the scheduled-testing trigger to the AI: Claude Code `/schedule` (cron) for Claude, Codex App automation for Codex.
- The scheduled auditor sees COMMITTED state only — keep its input the committed branch diff, and keep the per-task commit cadence in the goal prompts.
- Guardrails (`templates/guards/`) are the hard-enforcement layer: keep the hook scripts and `settings.hooks.json` in sync, and keep `current-task.json` the single source the guards read. The JSON-parsing hooks need `python3`; the git append-only / main-branch / message checks degrade gracefully without it.
