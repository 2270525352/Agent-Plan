---
name: agent-plan
description: Plan a new project end-to-end into an AI-readable tree so a single AI window (one Claude or one Codex window) executes by following marked tasks instead of re-deciding what to build. Use when the user wants requirements aligned and frozen before coding, the user's exact words preserved verbatim as the alignment anchor, granular tasks with execution feedback, Claude/Codex /goal automation prompts, scheduled drift testing (Claude Code cron or Codex App) that runs tests and re-checks the source of truth, review gates, or strict git checkpoint discipline.
---

# Agent-Plan

Agent-Plan turns user intent, rough notes, chats, and draft documents into a strict AI-executable planning tree, then drives a single AI window (one Claude window or one Codex window) to execute it without reinterpreting the project halfway through.

The premise: humans and AI have a communication gap. Say it in plain words and the AI's understanding can land far from what you meant. So a new project is planned end to end BEFORE any coding — requirements, architecture, tasks all frozen — and the user's exact words are kept verbatim as the anchor everything is checked against. Plan it thoroughly and execution turns mechanical: the AI just follows the marked tasks instead of re-deciding what to build — fast, and basically no drift. Leave gaps or ambiguity and the AI improvises, and its ideas diverge from yours fast.

Scope is ONE AI window. No CC/CX role split, no second reviewer AI — a single window cannot be two AIs. Drift is caught by two layers: the AI self-checks against the source of truth, and scheduled testing re-runs tests + re-reads the source of truth on a timer.

Every document the AI reads must be AI-readable — explicit fields, scope, boundaries, acceptance criteria, verification commands, stop conditions (structured metadata the AI parses cleanly, not human prose). Narrative summaries are secondary only.

## Core Principle

Do not let the AI rediscover the requirements while it is coding. Resolve every ambiguity in planning; during execution the AI follows approved tasks and feeds back every step — it does not invent new direction.

If the plan is unclear or ambiguous, the AI's thinking diverges (Codex/GPT especially). The fix is always upstream: make the plan detailed enough that there is nothing left to improvise. A well-planned project runs fast with almost no bugs because the AI is executing, not deciding.

## When To Use

Use this skill when any of these are true:

- The user wants a single Claude or single Codex to run a project autonomously via `/goal`.
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
   - The log states actual files changed, acceptance and test results, the source-of-truth comparison, any drift, status, and next step.
   - An execution with no feedback record counts as not done.

4. Prevent drift with two layers.
   - Inner: the executing AI self-checks (re-read source of truth + run acceptance/tests + write feedback) after each task, each large change, and whenever it nears a forbidden boundary.
   - Outer: an independent scheduled auditor on an external timer (Claude Code `/schedule` cron, or Codex App RRULE, every 30 min) re-reads the source of truth and the diff and reports drift.
   - The auditor is DETECTION-ONLY: it records problems to `05-reviews/偏离用户原话报告.md` and never fixes or modifies anything (least of all the user words). Fixing is the main execution's / user's call. On RED the main execution stops. Set the auditor up BEFORE starting the goal.

5. The timer must be external, the auditor independent.
   - The executing AI has no reliable internal timer (Codex can only block on `sleep`; it cannot self-wake), so the 30-min cycle comes from an EXTERNAL scheduler.
   - Claude window → Claude Code `/schedule` (cron `*/30 * * * *`). Codex window → Codex App task (`RRULE:FREQ=HOURLY;INTERVAL=1;BYMINUTE=0,30;BYDAY=SU,MO,TU,WE,TH,FR,SA`).
   - The auditor must be INDEPENDENT — a clean agent that reads only the source of truth + diff, not the main agent's execution context, so it cannot rationalize the same drift.
   - Generate both prompt files; the user picks the one matching the AI they run.

6. Treat git checkpoints as part of the workflow.
   - Check git status before work.
   - Protect user changes.
   - Commit stable planning baselines and verified tasks when the user wants commits or the project workflow allows them.
   - Never mix unrelated changes in a commit.

## Single-Window Model

The whole project runs in ONE AI window — one Claude window or one Codex window. There is no CC/CX division of labor and no separate reviewer AI; a single window is a single AI. That one AI resolves all planning up front, then executes the frozen plan.

| Concern | Owner | Notes |
|---|---|---|
| Planning (requirements, architecture, task decomposition, ambiguity resolution) | The single window AI, before execution starts | Resolved up front and frozen into the source of truth. |
| Execution (implementation, tests, interface compatibility, bug fixes, scoped refactors) | The same window AI | Follows the task spec; stays inside each task's allowed scope; writes execution feedback. |
| Inner drift defense | The AI's self-check | Re-read source of truth + run acceptance/tests + write feedback. |
| Outer drift defense | Scheduled testing | Claude Code cron when running Claude; Codex App automation when running Codex. |

The window may be Claude or Codex; the `/goal` prompts cover both so the user pastes whichever they run.

## Required Output Tree

Create this tree in the target project unless the user asks for another path:

```text
docs/agent-plan/
  00-source/
    用户原话文档.md
    用户强调事项.md
    禁止偏离事项.md

  01-requirements/
    总需求文档.md
    AI可读需求文档.md
    需求对齐检查表.md
    开放问题.md

  02-architecture/
    总架构文档.md
    架构图.md
    总设计文档.md
    接口契约文档.md

  03-tasks/
    总任务文档.md
    任务依赖图.md
    阶段交付计划.md

  04-execution/
    任务说明.md
    执行反馈日志.md

  05-reviews/
    需求对齐审查.md
    架构一致性审查.md
    偏离用户原话报告.md
    自动模式门禁.md

  06-goals/
    Claude-goal.md
    Codex-goal.md

  07-testing/
    定时测试方案.md
    ClaudeCode定时任务提示词.md
    CodexApp定时测试提示词.md

  08-runtime/
    单AI执行模式.md

  09-git/
    Git提交纪律.md
    提交检查表.md
```

## Workflow

### 1. Intake

Collect:

- user raw words
- draft requirements, architecture docs, interface contracts
- existing codebase constraints
- which AI will execute: Claude (Claude Code) or Codex
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

Create `04-execution/任务说明.md` (the single window AI's identity, allowed/forbidden scope, granular task list, self-check cadence, stop conditions, mandatory execution feedback) and `04-execution/执行反馈日志.md` (the append-only feedback log). Tasks here trace back to the total task document. There is no CC/CX split — one window, one task spec.

### 7. Review Before Execution

Before generating `/goal` and testing prompts, review against: user words, AI-readable requirements, total requirements, architecture, design, total task document, the task spec (任务说明), forbidden behavior, git discipline. If anything fails, write blockers to `05-reviews/自动模式门禁.md` and do not mark the plan ready.

### 8. Generate Goals

Generate `/goal` prompts for both Claude and Codex (`06-goals/`). Each makes the single AI run the full loop: read source of truth → pick task → implement within allowed scope → run acceptance and tests → write execution feedback → self-check against source of truth → git checkpoint. The user pastes whichever AI they run.

### 9. Generate Scheduled Audit

Create `07-testing/` — an independent, external-timer auditor (the executing AI has no reliable internal timer):

- `定时测试方案.md` — the detection-only audit plan: re-read the source of truth, compare the feedback log against the real diff, optionally run tests/acceptance, classify GREEN / YELLOW / RED, plus the startup order.
- `ClaudeCode定时任务提示词.md` — the audit prompt for Claude Code `/schedule` (cron `*/30 * * * *`), for a Claude window.
- `CodexApp定时测试提示词.md` — the same audit for a Codex App task (`RRULE ... BYMINUTE=0,30 ...`), for a Codex window.

Default interval: every 30 minutes. The auditor is DETECTION-ONLY — it records problems to `05-reviews/偏离用户原话报告.md` and never fixes or modifies anything. On RED the main execution stops. Tell the user to set up the auditor BEFORE starting the goal.

### 10. Git Checkpoints

In a git repository: run `git status` before edits, do not overwrite user changes, self-review the diff 3 times against the source of truth, commit only after tests/acceptance pass, put the AI name + task number in the commit message, never commit secrets/temp/failed output/unrelated formatting. When not a git repository: still generate `09-git/Git提交纪律.md` and ask whether to initialize a repo before committing.

## Auto-Mode Gate

The plan is ready for autonomous single-AI execution only when all are true:

- user words are recorded append-only
- AI-readable requirements trace back to user-word records
- architecture and design cover all P0 / current-phase requirements
- interface contracts are explicit and frozen
- total tasks trace to requirements and are granular enough
- the task spec (任务说明) has clear allowed and forbidden scope
- every task has an acceptance command and acceptance criteria
- the execution-feedback log mechanism exists
- `/goal` prompts exist for Claude and Codex
- the single-AI execution mode exists
- the scheduled-testing plan exists
- the trigger prompt for the AI in use exists (Claude Code cron or Codex App)
- git discipline is defined
- review docs show no blocking drift, missing acceptance criteria, or missing verification

If any condition is false, output the blockers and stop before automation.

## Output Style

When reporting to the user:

- Be concise.
- Explain what documents were produced and what is still blocked.
- Do not paste every generated document unless asked.
- Point to the generated paths.
