# Agent-Plan

[![release](https://img.shields.io/badge/release-v1.1.0-2F9E44.svg)](https://github.com/2270525352/Agent-Plan) [![for](https://img.shields.io/badge/for-Claude%20%7C%20Codex-lightgrey.svg)]()

**English** | [中文](README.zh-CN.md)

> **v1.1.0** — now with deterministic guardrails (Claude Code hooks + git hooks), project-size profiles, and a committed-state scheduled auditor. See [CHANGELOG](CHANGELOG.md).

Agent-Plan is a Codex/Claude skill for building strict AI-readable planning trees that one **mainline AI window** (Claude, Codex, or a CLI conversation) executes autonomously via `/goal`, optionally with bounded helper agents — without drifting from the user's real intent.

## Purpose

Long autonomous runs drift: the AI starts reinterpreting the requirements while it codes. Agent-Plan moves interpretation into the planning phase, freezes it into a source of truth, and keeps the mainline AI honest with self-checks, side-agent merge gates, scheduled audits, and hard guardrails.

It generates:

- root `AGENTS.md` repository rules, merged through an Agent-Plan marker block
- root `CURRENT_STATE.md` live handoff state for multi-window continuity
- append-only user-word records
- AI-readable requirements
- architecture and design documents
- a granular total task document
- a task spec + execution-feedback and side-task logs
- Claude/Codex `/goal` prompts for autonomous execution
- a scheduled-testing plan + trigger prompts (Claude Code cron or Codex App)
- git checkpoint rules
- a guardrail layer (Claude Code hooks + git hooks) that enforces task scope, user-words append-only, commit format, and no-push-to-main

## Mainline And Helper Agents

There is one mainline decision authority. The mainline window owns requirements interpretation, task state, merge decisions, git checkpoints, and stop/go decisions.

Helper agents are optional side workers. They only receive bounded contracts: parent task, source requirements, allowed files, forbidden files, expected output, acceptance criteria, verification command, and stop conditions. Their output is advisory until the mainline classifies it:

- **GREEN** — complete, in scope, traceable, verified, no new assumptions.
- **YELLOW** — useful but incomplete, assumed something, lacks tests, or needs mainline follow-up.
- **RED** — changes requirements, exceeds scope, conflicts with source of truth, breaks contracts, or cannot be verified.

A parent task is not complete until every side task is merged, rejected, or explicitly blocked in `04-execution/支线任务记录.md`.

## Three Layers Against Drift

Drift is caught three ways:

- **Inner — self-check.** After each task, each large change, and whenever it nears a forbidden boundary, the mainline AI re-reads the source of truth, runs acceptance/tests, and writes execution feedback.
- **Merge gate — side-agent review.** Helper output is checked for completeness, source traceability, allowed scope, conflicts, verification, and drift before it enters the mainline.
- **Outer — scheduled testing.** On a timer, a routine runs the test suite, runs acceptance commands, re-reads the source of truth, compares the execution-feedback log against the committed branch diff, and reports GREEN / YELLOW / RED. It only audits — it never fixes business code on its own.

The trigger matches the AI: **Claude Code `/schedule` (cron)** when you run Claude, **Codex App automation** when you run Codex. The auditor sees COMMITTED state only, so the main loop commits every task; the audit unit is per-task-commit and the 30-min timer is a heartbeat backstop.

**Plus a hard layer — guardrails.** The layers above *detect* drift; a generated guardrail layer *enforces* what tooling can enforce. Claude Code hooks block out-of-scope / forbidden / source-of-truth writes in real time and check feedback on stop; git hooks keep the user-words doc append-only, gate commits on an active task + a feedback entry + passing acceptance/tests, enforce the commit format, and block pushes to main/master. Claude gets hooks + git; Codex relies on the git hooks. See `10-guards/`.

Guardrails are installed with `scripts/agent-plan-guards.py install|verify|uninstall`. The installer merges Claude settings and refuses to silently replace an existing hook manager such as Husky, lefthook, or pre-commit; chain Agent-Plan hooks from that manager, or use `--force-hooks-path` only after explicit approval.

## Guardrail Lifecycle

Install and verify guardrails in a target project:

```bash
python3 scripts/agent-plan-guards.py install --project /path/to/project
python3 scripts/agent-plan-guards.py verify --project /path/to/project
```

If the project already uses a hook manager, the installer copies Agent-Plan hooks but keeps the existing `core.hooksPath`. Chain `.githooks/pre-commit`, `.githooks/commit-msg`, and `.githooks/pre-push` from that manager, then verify with:

```bash
python3 scripts/agent-plan-guards.py verify --project /path/to/project --allow-existing-hooks-path
```

Uninstall only Agent-Plan hook files and Claude hook entries:

```bash
python3 scripts/agent-plan-guards.py uninstall --project /path/to/project
```

Add `--unset-hooks-path` only when `.githooks` is Agent-Plan-owned for that project.

## Bootstrap Lifecycle

Before generating the planning tree, bootstrap root coordination files in the target project:

```bash
python3 scripts/agent-plan-bootstrap.py install --project /path/to/project
```

This preserves an existing `AGENTS.md` and inserts or updates only the `<!-- AGENT_PLAN_START --> ... <!-- AGENT_PLAN_END -->` block. `CURRENT_STATE.md` is created if missing and preserved by default if it already exists. Use `--append-state-log` to record a bootstrap run in an existing state file; use force flags only after explicit approval.

## Install

Clone this directory into your skills directory:

```bash
mkdir -p "$CODEX_HOME/skills"
git clone https://github.com/2270525352/Agent-Plan.git "$CODEX_HOME/skills/agent-plan"
```

For Claude Code, copy the skill directory to the provider-specific skills folder.

## Use

Ask your AI agent to use Agent-Plan:

```text
$agent-plan Build a planning tree for this project. Preserve my original words, write a granular
task document with execution feedback, generate Claude and Codex /goal prompts, and create a
scheduled drift test (Claude Code cron, or Codex App) that runs the tests and re-checks the source of truth.
Start by creating or merging AGENTS.md and CURRENT_STATE.md at the project root.
```

## Profiles

Scale to the project — don't emit ~30 files for a todo CLI. Pick a profile; the enforcement **core** (root `AGENTS.md`, root `CURRENT_STATE.md`, source of truth, AI-readable requirements, total tasks, task spec + feedback + side-task records, goals, scheduled audit, runtime, git, guardrails) ships in every profile, and profiles only add planning depth.

- **lite** — small / single-component / clear requirements. ~16 files incl. root bootstrap, core only (no separate architecture docs unless there are real interfaces).
- **standard** (default) — a typical multi-part project. lite + emphasis doc, alignment checklist, architecture overview (diagram inline) + interface contracts, phase plan, alignment review, commit checklist. ~22 files.
- **full** — large / handoff / regulated. Every template, including the expanded prose docs. ~30 files.

lite/standard skip the prose docs that restate machine-readable content (`总需求文档`, `总设计文档`, `架构图`); full keeps them. See SKILL.md → Profiles for the exact matrix.

## Output Tree

Agent-Plan creates root coordination files plus `docs/agent-plan/` in the target project (the full tree below; lite/standard emit a subset — see Profiles):

```text
AGENTS.md              root repository rules; existing content is preserved via marker merge
CURRENT_STATE.md       live state, write locks, active task, blockers, next step
docs/agent-plan/
  00-source/        用户原话文档.md  用户强调事项.md  禁止偏离事项.md
  01-requirements/  总需求文档.md  AI可读需求文档.md  需求对齐检查表.md  开放问题.md
  02-architecture/  总架构文档.md  架构图.md  总设计文档.md  接口契约文档.md
  03-tasks/         总任务文档.md  任务依赖图.md  阶段交付计划.md
  04-execution/     任务说明.md  执行反馈日志.md  支线任务记录.md  current-task.json
  05-reviews/       需求对齐审查.md  架构一致性审查.md  偏离用户原话报告.md  自动模式门禁.md
  06-goals/         Claude-goal.md  Codex-goal.md
  07-testing/       定时测试方案.md  ClaudeCode定时任务提示词.md  CodexApp定时测试提示词.md
  08-runtime/       主线执行模式.md
  09-git/           Git提交纪律.md  提交检查表.md
  10-guards/        护栏说明.md  (+ installed to .claude/ and .githooks/)
```

See `templates/` for the document formats, and `examples/` for a **filled** sample tree (a small `local-todo-cli` project) showing what good output looks like.
