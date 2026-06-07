# Changelog

All notable changes to Agent-Plan.

## v1.1.0 — 2026-06-07

Optimization pass: turn prompt-only discipline into **enforced** discipline, fix the scheduled-auditor blind spot, and scale output to project size.

### Added
- **Guardrails (`10-guards/`)** — a hard-enforcement layer the skill installs into the target project:
  - **Claude Code hooks**: `scope-guard.py` (PreToolUse) blocks writes outside the current task's allowed scope / into forbidden / source-of-truth paths; `feedback-stop-check.py` (Stop) requires an execution-feedback entry before the agent ends.
  - **git hooks** (Claude & Codex): `pre-commit` (user-words append-only; a business commit needs an active task + a feedback entry; runs acceptance/tests), `pre-push` (blocks main/master), `commit-msg` (enforces `<task> (Claude|Codex): …`).
  - Driven by `04-execution/current-task.json`, which the main loop rewrites at the start of every task. Claude gets real-time hooks + git hooks; Codex relies on the git hooks. JSON-parsing hooks need `python3`; git checks degrade gracefully without it.
- **Profiles** — `lite` (~14 files), `standard` (~20, default), `full` (~28). Scale planning depth to project size; the enforcement core ships in every profile.

### Changed
- **Scheduled auditor reads committed state.** Remote `/schedule` and Codex App auditors run in a clean checkout and only see committed work, so the audit input is now the committed branch diff (`git diff <base>...<task-branch>`); the audit unit is per-task-commit, with the 30-min timer as a heartbeat. Goals commit + push every task and update `current-task.json`.
- **Dedup.** lite/standard no longer emit prose docs that restate machine-readable content (`总需求文档`, `总设计文档`, `架构图`); full keeps them.
- SKILL.md, both READMEs, templates README, runtime doc, and the auto-mode gate updated for all of the above.

### Fixed
- macOS `/bin/sh` (bash 3.2) corrupts an unbraced `$var` immediately followed by CJK text; all shell hooks now brace `${var}`.

## v1.0.0

Initial release: AI-readable planning tree, verbatim source of truth, granular tasks with execution feedback, Claude/Codex `/goal` prompts, scheduled drift testing, review gates, git checkpoint discipline.
