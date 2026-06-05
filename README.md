# Agent-Plan

[![release](https://img.shields.io/badge/release-v1.0.0-2F9E44.svg)](https://github.com/2270525352/Agent-Plan) [![for](https://img.shields.io/badge/for-Claude%20%7C%20Codex-lightgrey.svg)]()

**English** | [中文](README.zh-CN.md)

Agent-Plan is a Codex/Claude skill for building strict AI-readable planning trees that a **single AI** (one Claude window or one Codex window) executes autonomously via `/goal` — without drifting from the user's real intent.

## Purpose

Long autonomous runs drift: the AI starts reinterpreting the requirements while it codes. Agent-Plan moves interpretation into the planning phase, freezes it into a source of truth, and keeps the executing AI honest with two layers of drift defense.

It generates:

- append-only user-word records
- AI-readable requirements
- architecture and design documents
- a granular total task document
- a task spec + an execution-feedback log
- Claude/Codex `/goal` prompts for autonomous execution
- a scheduled-testing plan + trigger prompts (Claude Code cron or Codex App)
- git checkpoint rules

## Two Layers Against Drift

There is no second AI to catch mistakes, so drift is caught two ways:

- **Inner — self-check.** After each task, each large change, and whenever it nears a forbidden boundary, the executing AI re-reads the source of truth, runs acceptance/tests, and writes execution feedback.
- **Outer — scheduled testing.** On a timer, a routine runs the test suite, runs acceptance commands, re-reads the source of truth, compares the execution-feedback log against the real diff, and reports GREEN / YELLOW / RED. It only audits — it never fixes business code on its own.

The trigger matches the AI: **Claude Code `/schedule` (cron)** when you run Claude, **Codex App automation** when you run Codex.

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
```

## Output Tree

Agent-Plan creates `docs/agent-plan/` in the target project:

```text
docs/agent-plan/
  00-source/        用户原话文档.md  用户强调事项.md  禁止偏离事项.md
  01-requirements/  总需求文档.md  AI可读需求文档.md  需求对齐检查表.md  开放问题.md
  02-architecture/  总架构文档.md  架构图.md  总设计文档.md  接口契约文档.md
  03-tasks/         总任务文档.md  任务依赖图.md  阶段交付计划.md
  04-execution/     任务说明.md  执行反馈日志.md
  05-reviews/       需求对齐审查.md  架构一致性审查.md  偏离用户原话报告.md  自动模式门禁.md
  06-goals/         Claude-goal.md  Codex-goal.md
  07-testing/       定时测试方案.md  ClaudeCode定时任务提示词.md  CodexApp定时测试提示词.md
  08-runtime/       单AI执行模式.md
  09-git/           Git提交纪律.md  提交检查表.md
```

See `templates/` for the document formats, and `examples/` for a **filled** sample tree (a small `local-todo-cli` project) showing what good output looks like.
