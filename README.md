# Agent-Plan

**English** | [中文](README.zh-CN.md)

Agent-Plan is a Codex/Claude skill for building strict AI-readable planning trees before implementation.

It is designed for users who work with multiple AI agents such as Claude, Codex, OpenCode, CCB, and Codex App automations, but it also supports a single AI CLI window.

## Purpose

Agent-Plan prevents AI agents from drifting away from the user's real intent during long-running work.

It does this by generating:

- append-only user-word records
- AI-readable requirements
- architecture and design documents
- total task documents
- Claude, Codex, Reviewer, and OpenCode task documents
- Claude/Codex `/goal` prompts
- CCB dispatch prompts
- Codex App recurring audit prompts
- git checkpoint rules

## Why This Exists

Human speech is often clear to humans but ambiguous to AI agents. If agents start coding before the requirements, boundaries, and task ownership are fixed, they may reinterpret the work halfway through.

Agent-Plan moves interpretation into the planning phase and makes implementation agents follow approved documents.

## Install

Clone this directory into your skills directory:

```bash
mkdir -p "$CODEX_HOME/skills"
git clone https://github.com/YOUR_NAME/agent-plan.git "$CODEX_HOME/skills/agent-plan"
```

For Claude Code, install it in the equivalent Claude skills location or copy the skill directory to the provider-specific skills folder.

## Use

Ask your AI agent to use Agent-Plan:

```text
$agent-plan Create a planning tree for this project. Preserve my original words, split tasks for Claude/Codex/Reviewer, generate /goal prompts, and create a Codex App 30-minute audit prompt.
```

## Default Agent Roles

| Agent | Role |
|---|---|
| Claude | requirements, architecture, task decomposition, source-of-truth maintenance |
| Codex | scoped code implementation, tests, compatibility, bug fixes |
| Reviewer (Claude) | document review, requirement alignment, task conflict checks |
| OpenCode | code risk review, hardcoding checks, test gaps, interface drift |
| CCB | multi-agent routing and shared context |
| Codex App | recurring audit automation |

## Output Tree

Agent-Plan creates `docs/agent-plan/` in the target project.

See `templates/` for the document formats used by the skill.

