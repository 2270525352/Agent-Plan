# AGENTS.md

<!-- AGENT_PLAN_START -->
## Agent-Plan Repository Rules

### Repository Profile

Repository type:

Work mode: mainline AI / mainline plus helper agents / CCB / single CLI

Mainline AI:

Agent-Plan profile: lite / standard / full

Primary planning tree: `docs/agent-plan/`

Dynamic state file: `CURRENT_STATE.md`

### Startup Read Order

Every AI window must read these files before doing project work:

1. `AGENTS.md`
2. `CURRENT_STATE.md`
3. `docs/agent-plan/00-source/用户原话文档.md`
4. `docs/agent-plan/00-source/禁止偏离事项.md`
5. `docs/agent-plan/01-requirements/AI可读需求文档.md`
6. `docs/agent-plan/03-tasks/总任务文档.md`
7. `docs/agent-plan/04-execution/任务说明.md`
8. `docs/agent-plan/04-execution/执行反馈日志.md`
9. `docs/agent-plan/04-execution/支线任务记录.md`

If a referenced file does not exist yet, create it through Agent-Plan planning before implementation starts.

### Source-Of-Truth Rules

- `docs/agent-plan/00-source/用户原话文档.md` is append-only.
- Never rewrite, polish, translate, delete, or summarize over user words in the user-words document.
- Cleaned requirements belong in `docs/agent-plan/01-requirements/AI可读需求文档.md`.
- Any requirement, task, design decision, or code change must trace back to user words or a user-confirmed source.

### Mainline Authority

- Exactly one mainline AI/window owns final decisions, task state, git commits, and merge decisions.
- Helper agents may research, draft, review, test, or implement bounded subtasks only through explicit side-task contracts.
- Helper output is advisory until the mainline records a GREEN / YELLOW / RED merge decision in `docs/agent-plan/04-execution/支线任务记录.md`.
- No helper may redefine requirements, product direction, architecture direction, source-of-truth text, or task boundaries.

### Multi-Window Mutex

- Only one window may write the same final artifact at the same time.
- Before writing any final artifact, the active writer must update `CURRENT_STATE.md` with the locked artifact and active task.
- Other windows may research, draft, review, or propose changes, but must not write the locked artifact.
- Before saving, the active writer must re-read `CURRENT_STATE.md` and the latest target file on disk.
- After saving, the active writer must update `CURRENT_STATE.md` with the written range, changed files, verification result, and next step.

### Modification Authorization

- Discussion, direction approval, preview review, or "looks good" does not by itself authorize writing final artifacts.
- Write only when the user explicitly asks to modify, execute, save, or apply changes, or when the active Agent-Plan task contract already grants that write.
- If authorization is ambiguous, ask before writing.

### Target-File Reread Rule

Before modifying any final artifact, read the current target file from disk with enough surrounding context to preserve structure and wording continuity. Do not rely only on conversation memory, summaries, or `CURRENT_STATE.md`.

### State Update Rule

Update `CURRENT_STATE.md` after:

- important edits
- task completion
- blocker discovery
- user decisions or new rules
- helper-agent dispatch or return
- merge-gate decisions
- checkpoint commits
- findings that are researched but not yet written into final docs

State updates must be concise and factual: what changed, what remains blocked, what cannot be touched, and what the next AI window should read first.

### Response Completeness

When the user is reviewing a range that contains multiple items, fields, sections, or numbered points, responses must show the complete affected range or complete proposed replacement. Do not show only the one changed item if that hides how it fits with neighboring content.

### Git Discipline

- Run `git status` before edits.
- Protect user changes.
- Commit stable planning baselines and verified task checkpoints when the workflow allows commits.
- Do not mix unrelated changes.
- Do not commit secrets, temp files, failed outputs, or unexplained generated artifacts.
- Use task IDs or checkpoint labels in commit messages.

<!-- AGENT_PLAN_END -->

