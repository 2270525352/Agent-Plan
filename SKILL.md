---
name: agent-plan
description: Plan a new project end-to-end into an AI-readable tree so a main CLI/conversation window can execute by following marked tasks instead of re-deciding what to build, optionally delegating bounded side tasks to helper agents while preserving one mainline decision authority. Use when the user wants requirements aligned and frozen before coding, the user's exact words preserved verbatim as the alignment anchor, granular tasks with execution feedback, helper-agent task contracts, merge gates for completeness and drift, Claude/Codex /goal automation prompts, scheduled drift testing (Claude Code cron or Codex App), strict git checkpoint discipline, or deterministic guardrails (Claude Code hooks + git hooks) that enforce task scope and commit discipline.
---

# Agent-Plan

Agent-Plan turns user intent, rough notes, chats, and draft documents into a strict AI-executable planning tree, then drives one main CLI/conversation window (Claude or Codex) to execute it without reinterpreting the project halfway through.

The premise: humans and AI have a communication gap. Say it in plain words and the AI's understanding can land far from what you meant. So a new project is planned end to end BEFORE any coding — requirements, architecture, tasks all frozen — and the user's exact words are kept verbatim as the anchor everything is checked against. Plan it thoroughly and execution turns mechanical: the AI just follows the marked tasks instead of re-deciding what to build — fast, and basically no drift. Leave gaps or ambiguity and the AI improvises, and its ideas diverge from yours fast.

Scope is ONE MAINLINE window. The mainline window owns planning, task selection, final decisions, state, git checkpoints, and merge approval. It may call helper/side agents for bounded work, but helpers never become a second source of truth and never redefine requirements. Drift is caught by self-checks, side-agent merge gates, and scheduled testing that re-runs tests + re-reads the source of truth on a timer.

Every document the AI reads must be AI-readable — explicit fields, scope, boundaries, acceptance criteria, verification commands, stop conditions (structured metadata the AI parses cleanly, not human prose). Narrative summaries are secondary only.

## Core Principle

Do not let the AI rediscover the requirements while it is coding. Resolve every ambiguity in planning; during execution the AI follows approved tasks and feeds back every step — it does not invent new direction.

If the plan is unclear or ambiguous, the AI's thinking diverges (Codex/GPT especially). The fix is always upstream: make the plan detailed enough that there is nothing left to improvise. A well-planned project runs fast with almost no bugs because the AI is executing, not deciding.

## When To Use

Use this skill when any of these are true:

- The user wants one Claude/Codex CLI or conversation window to run a project autonomously via `/goal`.
- The user wants that main window to call helper agents safely without losing the mainline.
- The user wants requirements aligned and frozen before implementation.
- The user is worried the AI will drift from the original request during long runs.
- The user wants granular tasks with explicit execution feedback / status write-back.
- The user wants scheduled testing (Claude Code cron or Codex App) that runs tests and audits drift.
- The user provides rough speech, long notes, chat transcripts, or draft docs that must become execution documents.
- The user asks for `/goal` prompts, a strict implementation plan, or git checkpoint discipline.

## Non-Negotiable Rules

1. Preserve user words exactly.
   - The user-words document is append-only.
   - Never rewrite, polish, summarize, translate, delete, or replace original user words inside that document.
   - If a cleaned version is needed, create a separate AI-readable requirements document.

2. Make agent-facing documents AI-readable.
   - Use stable fields: allowed scope, forbidden scope, dependencies, acceptance criteria, verification commands, stop conditions.
   - Do not rely on prose-only descriptions for tasks the AI must execute.
   - Tasks must be granular: step-by-step, checkable, with allowed/forbidden scope down to files or directories.

3. Require execution feedback.
   - Every task and every self-check writes a record to the execution-feedback log.
   - Every helper-agent dispatch and merge decision writes a side-agent record.
   - The log states actual files changed, acceptance and test results, the source-of-truth comparison, any drift, status, and next step.
   - An execution with no feedback record counts as not done.

4. Keep one mainline, even with helper agents.
   - The mainline window is the only coordinator. It owns source-of-truth interpretation, task state, merge decisions, git commits, and stop/go decisions.
   - A helper agent may only receive a bounded side-task contract: task id, source requirements, allowed scope, forbidden scope, acceptance criteria, expected output, and stop conditions.
   - Helper output is advisory until the mainline checks completeness, drift, conflicts, tests, and scope. No helper may change product direction, user words, architecture direction, or task boundaries.

5. Prevent drift with three layers.
   - Inner: the mainline AI self-checks (re-read source of truth + run acceptance/tests + write feedback) after each task, each large change, and whenever it nears a forbidden boundary.
   - Merge gate: helper-agent outputs are classified GREEN / YELLOW / RED before they enter the mainline.
   - Outer: an independent scheduled auditor on an external timer (Claude Code `/schedule` cron, or Codex App RRULE, every 30 min) re-reads the source of truth and the diff and reports drift.
   - The auditor is DETECTION-ONLY: it records problems to `05-reviews/偏离用户原话报告.md` and never fixes or modifies anything (least of all the user words). Fixing is the mainline / user's call. On RED the mainline stops. Set the auditor up BEFORE starting the goal.

6. The timer must be external, the auditor independent.
   - The mainline AI has no reliable internal timer (Codex can only block on `sleep`; it cannot self-wake), so the 30-min cycle comes from an EXTERNAL scheduler.
   - Claude window → Claude Code `/schedule` (cron `*/30 * * * *`). Codex window → Codex App task (`RRULE:FREQ=HOURLY;INTERVAL=1;BYMINUTE=0,30;BYDAY=SU,MO,TU,WE,TH,FR,SA`).
   - The auditor must be INDEPENDENT — a clean agent that reads only the source of truth + diff, not the main agent's execution context, so it cannot rationalize the same drift.
   - The auditor sees COMMITTED state only (it runs in a separate checkout / remote routine), so its input is the committed branch diff (`git diff <base>...<task-branch>`) and the mainline must checkpoint-commit every task — uncommitted work is invisible to it by design. The audit unit is per-task-commit; the 30-min timer is a heartbeat backstop.
   - Generate both prompt files; the user picks the one matching the AI they run.

7. Treat git checkpoints as part of the workflow.
   - Check git status before work.
   - Protect user changes.
   - Commit stable planning baselines and verified tasks when the user wants commits or the project workflow allows them.
   - Never mix unrelated changes in a commit.

8. Enforce what can be enforced — with tooling, not just prose.
   - The skill generates a guardrail layer (`10-guards/`): Claude Code hooks (scope-guard blocks out-of-scope / forbidden / source-of-truth writes in real time; a Stop hook checks execution feedback) plus git hooks (pre-commit enforces user-words append-only, requires a feedback entry before committing business code, and runs acceptance/tests; commit-msg enforces the commit format; pre-push blocks main/master).
   - These are the hard enforcement backstop for append-only source of truth, task scope, feedback, acceptance/tests, commit format, and no main/master push. Claude gets real-time hooks + git hooks; Codex relies on the git hooks (commit time). See `10-guards/护栏说明.md`.

## Mainline + Side-Agent Model

The project has ONE mainline window — one Claude window, one Codex window, or one CLI conversation. That window may ask helper/side agents for bounded work, but the mainline remains the only coordinator and the only place where requirements are interpreted and state is advanced.

| Concern | Owner | Notes |
|---|---|---|
| Planning (requirements, architecture, task decomposition, ambiguity resolution) | Mainline window, before execution starts | Resolved up front and frozen into the source of truth. |
| Execution (implementation, tests, interface compatibility, bug fixes, scoped refactors) | Mainline window, optionally with helper agents | Helpers receive bounded contracts; mainline owns final merge. |
| Helper / side work | Helper agents | Review, risk checks, focused implementation, tests, or analysis only inside an explicit side-task contract. |
| Merge decision | Mainline window | Checks completeness, drift score, conflicts, tests, and allowed scope before accepting helper output. |
| Inner drift defense | Mainline self-check | Re-read source of truth + run acceptance/tests + write feedback. |
| Side-agent drift defense | Merge gate | GREEN / YELLOW / RED classification before any helper output is accepted. |
| Outer drift defense | Scheduled testing | Claude Code cron when running Claude; Codex App automation when running Codex. Audits COMMITTED state, so commit every task. |
| Hard enforcement | Guardrails (`10-guards/`) | Claude Code hooks (real-time) + git hooks (commit/push), keyed off `current-task.json`. |

The mainline may be Claude or Codex; the `/goal` prompts cover both so the user pastes whichever they run. Helper use is optional. If no helper agent is available, execute the same plan in the mainline only.

## Helper-Agent Rules

Only dispatch helper agents when the task is large enough or risky enough to benefit from review, focused implementation, or test generation. Before dispatch, write a side-task contract in `04-execution/支线任务记录.md`.

Each helper contract must include:

- side-task id
- parent task id
- helper role
- source requirement ids / user-word ids
- input docs
- allowed files or areas
- forbidden files or areas
- expected output
- acceptance criteria
- verification command
- stop conditions
- merge gate checklist

Helper output must be classified:

- GREEN: complete, in scope, traceable to source requirements, tests/acceptance pass, no new assumptions.
- YELLOW: useful but incomplete, has assumptions, lacks tests, or needs mainline edits before merge.
- RED: changes requirements, exceeds scope, conflicts with source of truth, breaks contracts, or cannot be verified.

GREEN may be merged by the mainline after self-review. YELLOW requires mainline follow-up and explicit feedback. RED stops the parent task and records a drift report or open question.

## Profiles

Scale to the project — don't emit ~28 files for a todo CLI. Pick a profile; it decides which documents are generated. The enforcement CORE (source of truth, AI-readable requirements, total tasks, task spec + feedback + side-task records, goals, scheduled audit, runtime, git, guardrails) ships in EVERY profile — profiles only add planning depth.

| Profile | When | Roughly |
|---|---|---|
| **lite** | small / single-component / throwaway; requirements basically clear | ~14 files: core only. No separate architecture docs (add `接口契约文档.md` only if real interfaces exist). |
| **standard** (default) | a typical multi-part project | lite + `用户强调事项`, `需求对齐检查表`, `总架构文档` (diagram inline) + `接口契约文档`, `阶段交付计划`, `需求对齐审查`, `提交检查表`. ~20 files. |
| **full** | large / multi-component / team handoff / regulated | every template, incl. the expanded prose docs `总需求文档`, `总设计文档`, `架构图`, `任务依赖图`, `架构一致性审查`. ~28 files. |

Dedup: lite/standard do NOT emit the human-prose docs that restate machine-readable content — `总需求文档` (use `AI可读需求文档`), `总设计文档` / `架构图` (fold the mermaid diagram inline into `总架构文档`). Full keeps the expanded set, where prose versions earn their keep for big projects and handoffs.

Selecting: infer from scope (one component & clear → lite; typical → standard; large / regulated / handoff → full) and state which you picked; ask only if genuinely ambiguous. The user can name a profile or add/drop individual docs. Whatever the profile, the Auto-Mode Gate still requires every CORE item.

## Required Output Tree

Create this tree in the target project unless the user asks for another path. This is the FULL tree, tagged so you can see what each profile emits — `lite`/`standard` emit a subset (see Profiles). Tags: (untagged) = all profiles incl. lite · `[S]` = standard + full · `[F]` = full only.

```text
# tags: (none) = all profiles incl. lite · [S] = standard + full · [F] = full only
docs/agent-plan/
  00-source/
    用户原话文档.md
    禁止偏离事项.md
    用户强调事项.md            [S]

  01-requirements/
    AI可读需求文档.md
    开放问题.md
    需求对齐检查表.md          [S]
    总需求文档.md              [F]

  02-architecture/            [S]  (lite: skip dir; add 接口契约文档.md only if real interfaces exist)
    总架构文档.md              [S]  (embed the mermaid diagram inline)
    接口契约文档.md            [S]
    架构图.md                  [F]
    总设计文档.md              [F]

  03-tasks/
    总任务文档.md
    阶段交付计划.md            [S]
    任务依赖图.md              [F]

  04-execution/
    任务说明.md
    执行反馈日志.md
    支线任务记录.md
    current-task.json

  05-reviews/
    偏离用户原话报告.md
    自动模式门禁.md
    需求对齐审查.md            [S]
    架构一致性审查.md          [F]

  06-goals/
    Claude-goal.md
    Codex-goal.md

  07-testing/                 (generate the trigger prompt for the AI you run)
    定时测试方案.md
    ClaudeCode定时任务提示词.md
    CodexApp定时测试提示词.md

  08-runtime/
    主线执行模式.md

  09-git/
    Git提交纪律.md
    提交检查表.md              [S]

  10-guards/
    护栏说明.md
```

The guardrails' executable parts live OUTSIDE this tree (hooks only work in fixed locations): `.claude/hooks/`, `.claude/settings.json`, and `.githooks/`. `10-guards/护栏说明.md` documents them; the per-task state file the guards read is `04-execution/current-task.json`. Side-agent state is tracked in `04-execution/支线任务记录.md` and checked before parent task completion.

## Workflow

### 1. Intake

Collect:

- user raw words
- draft requirements, architecture docs, interface contracts
- existing codebase constraints
- which mainline AI will execute: Claude (Claude Code) or Codex
- whether helper/side agents may be used, and by what tool (CLI subagent, ask, CCB, manual second window, reviewer, etc.)
- profile: lite / standard / full (see Profiles — infer from project size, confirm only if unsure)
- git policy: commit now, propose only, or disabled

If files are provided, read them before generating final docs.

### 2. Append User Words

Write the user's original wording into `00-source/用户原话文档.md`. Preserve exact wording, timestamp, and source label. Do not correct typos, translate, or compress. Append new entries as new records.

### 3. Translate To AI-Readable Requirements

Create `01-requirements/AI可读需求文档.md`. Every requirement includes: requirement id, source user-word record id, intent, hard constraints, forbidden behavior, assumptions, open questions, acceptance criteria, downstream task references.

### 4. Build Architecture And Design Docs

Identify system boundary, components, data flow, interface contracts, frozen fields, source-of-truth data, extension points, forbidden shortcuts, observability, and migration/rollback when relevant. Use Mermaid diagrams when useful.

### 5. Build Total Task Document

Create `03-tasks/总任务文档.md`. Each task includes: task id, phase, source requirement ids, input docs, allowed files/areas, forbidden files/areas, dependencies, granular step-by-step execution, acceptance criteria, verification command, test command, deliverable, execution-feedback record id, status write-back, stop conditions, git checkpoint expectation.

### 6. Build Task Spec

Create `04-execution/任务说明.md` (the mainline window identity, allowed/forbidden scope, granular task list, self-check cadence, stop conditions, mandatory execution feedback), `04-execution/执行反馈日志.md` (append-only feedback log), and `04-execution/支线任务记录.md` (helper dispatch contracts and merge decisions). Tasks here trace back to the total task document. There is one mainline task spec; helper tasks are bounded side records under it.

### 6.5. Dispatch Helpers Only By Contract

If helper agents are allowed, dispatch them only from an active parent task and only after writing a side-task contract. Helper output must return to the mainline with evidence. The mainline then runs the merge gate:

- completeness: did the helper cover the requested subtask?
- traceability: which requirement/user-word ids justify the output?
- scope: are all touched files inside allowed scope?
- conflict: does it conflict with other side work, architecture, or interface contracts?
- verification: did tests/acceptance pass, or what remains?
- drift score: GREEN / YELLOW / RED

Do not mark the parent task complete until every side task is merged, rejected, or explicitly blocked.

### 7. Review Before Execution

Before generating `/goal` and testing prompts, review against: user words, AI-readable requirements, total requirements, architecture, design, total task document, the task spec (任务说明), forbidden behavior, git discipline. If anything fails, write blockers to `05-reviews/自动模式门禁.md` and do not mark the plan ready.

### 8. Generate Goals

Generate `/goal` prompts for both Claude and Codex (`06-goals/`). Each makes the mainline AI run the full loop: read source of truth → pick task → optionally dispatch bounded helper work → merge-gate helper output → implement within allowed scope → run acceptance and tests → write execution feedback → self-check against source of truth → git checkpoint. The user pastes whichever AI they run.

### 9. Generate Guardrails

Generate the `10-guards/` enforcement layer (templates in `templates/guards/`) and install it so discipline is enforced by tooling, not just prompts:

- Prefer the bundled lifecycle script instead of manual copying:
  `python3 <skill-dir>/scripts/agent-plan-guards.py install --project <target-project>`.
- The script copies `.claude/hooks/scope-guard.py` (PreToolUse) and `.claude/hooks/feedback-stop-check.py` (Stop), then merges `settings.hooks.json` into `.claude/settings.json` without replacing existing hooks.
- The script copies `.githooks/pre-commit` (user-words append-only; business commit needs an active task + a feedback entry; runs the task's acceptance/test commands), `pre-push` (no main/master), and `commit-msg` (`<task> (Claude|Codex): …`).
- Safety rule: if the target repo already has a non-`.githooks` `core.hooksPath` (Husky, lefthook, pre-commit, custom hooks), do not overwrite it silently. Report the conflict and either document how to chain Agent-Plan hooks from the existing hook system or rerun only after user approval with `--force-hooks-path`.
- Run `python3 <skill-dir>/scripts/agent-plan-guards.py verify --project <target-project>` after installation. If Agent-Plan hooks are chained from an existing hook manager, verify with `--allow-existing-hooks-path` and record that integration in `10-guards/护栏说明.md`. To remove only Agent-Plan hook entries/files, use `uninstall`; add `--unset-hooks-path` only when `.githooks` is Agent-Plan-owned for that project.
- `04-execution/current-task.json` — the main loop rewrites it at the START of every task (task_id / allow / forbid / acceptance_cmd / test_cmd); the guards key off it. Empty task_id = guard passive (planning phase).
- Claude gets real-time hooks + git hooks; Codex has no equivalent live hook, so its hard enforcement is the git hooks at commit time. Requires `python3` for the JSON-parsing hooks; the git append-only / main-branch / message checks degrade gracefully without it.

### 10. Generate Scheduled Audit

Create `07-testing/` — an independent, external-timer auditor (the mainline AI has no reliable internal timer):

- `定时测试方案.md` — the detection-only audit plan: re-read the source of truth, compare the feedback log against the committed branch diff (`git diff <base>...<task-branch>`), optionally run tests/acceptance, classify GREEN / YELLOW / RED, plus the startup order.
- `ClaudeCode定时任务提示词.md` — the audit prompt for Claude Code `/schedule` (cron `*/30 * * * *`), for a Claude window.
- `CodexApp定时测试提示词.md` — the same audit for a Codex App task (`RRULE ... BYMINUTE=0,30 ...`), for a Codex window.

Default interval: every 30 minutes — a heartbeat backstop; the real audit unit is per-task-commit, so the main loop must commit every task. The auditor sees COMMITTED state only and is DETECTION-ONLY — it records problems to `05-reviews/偏离用户原话报告.md` and never fixes or modifies anything. On RED the mainline stops. Tell the user to set up the auditor BEFORE starting the goal.

### 11. Git Checkpoints

In a git repository: run `git status` before edits, do not overwrite user changes, self-review the diff 3 times against the source of truth, commit only after tests/acceptance pass, put the AI name + task number in the commit message, never commit secrets/temp/failed output/unrelated formatting. When not a git repository: still generate `09-git/Git提交纪律.md` and ask whether to initialize a repo before committing.

## Auto-Mode Gate

The plan is ready for autonomous mainline execution only when all are true (profile-specific docs are required only when the chosen profile emits them; CORE items are always required):

- user words are recorded append-only
- AI-readable requirements trace back to user-word records
- architecture and design cover all P0 / current-phase requirements (standard / full; lite may skip)
- interface contracts are explicit and frozen (when the project has interfaces)
- total tasks trace to requirements and are granular enough
- the task spec (任务说明) has clear allowed and forbidden scope
- side-agent policy exists: helpers disabled, or helper contract + merge gate are defined
- every task has an acceptance command and acceptance criteria
- the execution-feedback log mechanism exists
- `/goal` prompts exist for Claude and Codex
- the mainline execution mode exists
- the scheduled-testing plan exists
- the trigger prompt for the AI in use exists (Claude Code cron or Codex App)
- git discipline is defined
- guardrails are installed and verified with `agent-plan-guards.py verify` (or, when an existing hook manager is present, Agent-Plan hooks are explicitly chained and that integration is documented), and `current-task.json` is present
- review docs show no blocking drift, missing acceptance criteria, or missing verification

If any condition is false, output the blockers and stop before automation.

## Output Style

When reporting to the user:

- Be concise.
- Explain what documents were produced and what is still blocked.
- Do not paste every generated document unless asked.
- Point to the generated paths.
