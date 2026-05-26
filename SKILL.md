---
name: agent-plan
description: Build an AI-readable planning tree for multi-agent or single-agent software work. Use when the user needs requirements alignment, source-of-truth preservation, Claude/Codex/OpenCode task splitting, CCB dispatch prompts, /goal prompts, Codex App automation prompts, review gates, or strict git checkpoint discipline before implementation.
---

# Agent-Plan

Agent-Plan turns user intent, rough notes, chats, and draft documents into a strict AI-executable planning tree. Its purpose is to prevent AI agents from reinterpreting the project during implementation.

The skill must produce documents that AI agents can read and act on directly. Narrative, user-friendly explanations may exist as secondary summaries, but every document used by an agent must have explicit fields, scope, boundaries, acceptance criteria, and stop conditions.

## Core Principle

Do not let implementation agents rediscover the requirements while they are coding.

Planning is where ambiguity is resolved. Execution is where approved tasks are followed.

## When To Use

Use this skill when any of these are true:

- The user wants to plan a project before implementation.
- The user needs multiple AI agents to work together.
- The user uses CCB, Claude, Codex, OpenCode, or Codex App automations.
- The user wants `/goal` prompts for Claude or Codex.
- The user is worried that AI agents will drift from the original request.
- The user provides rough speech, long notes, chat transcripts, or draft docs that need to become execution documents.
- The user asks for task splitting, reviewer tasks, automation prompts, or a strict implementation plan.

## Non-Negotiable Rules

1. Preserve user words exactly.
   - The user-words document is append-only.
   - Never rewrite, polish, summarize, translate, delete, or replace original user words inside that document.
   - If a cleaned version is needed, create a separate AI-readable requirements document.

2. Make agent-facing documents AI-readable.
   - Use stable fields.
   - Include allowed scope, forbidden scope, dependencies, acceptance criteria, verification commands, and stop conditions.
   - Do not rely on prose-only descriptions for tasks that an AI agent must execute.

3. Ask for role division before final task assignment.
   - Ask how Claude, Codex, Reviewer, OpenCode, CCB, and any other agents should be divided.
   - If the user does not specify, use the default role model in this skill.

4. Separate thinking from doing.
   - Claude may own requirements, architecture, task decomposition, and alignment review.
   - Codex may own clearly scoped code implementation, tests, compatibility work, and bug fixes.
   - Reviewer (Claude) reviews documents and task boundaries without implementing.
   - OpenCode, when available, reviews code risks, hardcoding, interface drift, and test gaps.

5. Do not assume CCB exists.
   - Generate CCB dispatch prompts when CCB exists.
   - Also generate a single-agent CLI mode so one Claude or Codex window can execute the same plan safely.

6. Treat git checkpoints as part of the workflow.
   - Check git status before work.
   - Protect user changes.
   - Commit after stable planning baselines and after independent verified tasks when the user wants commits or the project workflow allows commits.
   - Never mix unrelated changes in a commit.

## Default Role Model

Use these defaults unless the user overrides them.

| Role | Agent | Owns | Must Not Own |
|---|---|---|---|
| Planner | Claude | user intent, requirements, architecture, design docs, task decomposition, ambiguity resolution | unapproved implementation drift |
| Implementer | Codex | explicit code tasks, tests, interface compatibility, bug fixes, mechanical refactors | user words, product direction, AI strategy, prompts, broad architecture changes without authorization |
| Reviewer | Claude | document review, requirement alignment, task conflict review, auto-mode gate | implementation |
| Technical reviewer | OpenCode | hardcoding checks, diff review, tests, interface drift, implementation risk | goal state, product requirements |
| Coordinator | CCB | routing, asks, shared context, multi-agent dispatch | interpreting requirements without documents |
| Automation | Codex App | recurring progress and drift audits | replacing human approval on blocked decisions |

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

  04-agents/
    分工总说明.md
    Claude任务文档.md
    Codex任务文档.md
    Reviewer-Claude任务文档.md
    OpenCode审查任务文档.md

  05-reviews/
    需求对齐审查.md
    架构一致性审查.md
    任务冲突审查.md
    偏离用户原话报告.md
    自动模式门禁.md

  06-goals/
    Claude-goal.md
    Codex-goal.md

  07-dispatch/
    CCB分发提示词.md
    CodexApp定时审查提示词.md

  08-runtime/
    CCB多AI执行模式.md
    单AI执行模式.md
    CodexApp自动化模式.md

  09-git/
    Git提交纪律.md
    提交检查表.md
```

## Workflow

### 1. Intake

Collect:

- user raw words
- draft requirements
- draft architecture docs
- existing codebase constraints
- existing interface contracts
- agent environment: CCB or no CCB
- available agents: Claude, Codex, OpenCode, other reviewers
- git policy: whether commits should be made now, proposed only, or disabled

If files are provided, read them before generating final docs.

### 2. Append User Words

Write the user's original wording into `00-source/用户原话文档.md`.

Rules:

- Preserve exact wording.
- Use a timestamp and source label.
- Do not correct typos.
- Do not translate.
- Do not compress.
- Add new entries under a new record.

### 3. Translate To AI-Readable Requirements

Create `01-requirements/AI可读需求文档.md`.

Every requirement must include:

- requirement id
- source user-word record id
- intent
- hard constraints
- forbidden behavior
- assumptions
- open questions
- acceptance criteria
- downstream task references

### 4. Build Architecture And Design Docs

Create architecture documents that identify:

- system boundary
- components
- data flow
- interface contracts
- frozen fields
- source-of-truth data
- extension points
- forbidden shortcuts
- observability requirements
- migration and rollback requirements when relevant

Use Mermaid diagrams for architecture and task dependency diagrams when useful.

### 5. Build Total Task Document

Create `03-tasks/总任务文档.md`.

Each task must include:

- task id
- phase
- owner role
- source requirement ids
- input docs
- allowed files or areas
- forbidden files or areas
- dependencies
- execution steps
- acceptance criteria
- verification commands
- handoff output
- stop conditions
- git checkpoint expectation

### 6. Split Agent Tasks

Generate separate task documents:

- `Claude任务文档.md`
- `Codex任务文档.md`
- `Reviewer-Claude任务文档.md`
- `OpenCode审查任务文档.md`

Claude and Codex task documents must not overlap in ownership unless the overlap is explicitly described as a handoff.

### 7. Review Before Execution

Before generating final `/goal` and automation prompts, require review against:

- user words
- AI-readable requirements
- total requirements
- architecture
- design
- total task document
- agent task documents
- forbidden behavior
- git discipline

If anything fails, write blockers to `05-reviews/自动模式门禁.md` and do not mark the plan ready for automation.

### 8. Generate Goals And Dispatch Prompts

Generate `/goal` prompts only for agents that support them:

- Claude supports `/goal`.
- Codex supports `/goal`.
- OpenCode is treated as not supporting `/goal` unless the user proves otherwise.

Generate CCB prompts using `/ask` or `ccb ask` format when CCB is available. Also generate manual single-agent instructions for users without CCB.

### 9. Generate Codex App Automation Prompt

Create a recurring audit prompt for Codex App. Default interval: every 30 minutes.

The prompt must audit:

- drift from user words
- mismatch between total tasks and split tasks
- Claude/Codex task conflict
- unauthorized file changes
- hardcoding
- interface drift
- missing tests
- failed verification
- missing document status updates
- uncommitted or mixed git changes

The automation prompt must tell the agent to report blockers and avoid implementing unrelated fixes unless explicitly assigned.

### 10. Git Checkpoints

When working in a git repository:

- Run `git status` before edits.
- Do not overwrite user changes.
- Commit stable document baselines when appropriate.
- Commit independent task completions after verification when appropriate.
- Use task ids in commit messages.
- Do not commit secrets, temporary files, failed outputs, or unrelated formatting.

When the current directory is not a git repository:

- Still generate `09-git/Git提交纪律.md`.
- Ask whether the user wants a repo initialized before making commits.

## Auto-Mode Gate

The plan is ready for automated multi-agent execution only when all are true:

- user words are recorded append-only
- AI-readable requirements trace back to user-word records
- architecture and design docs cover all P0 or current-phase requirements
- total tasks trace to requirements
- Claude, Codex, and Reviewer task documents have non-overlapping boundaries
- Codex tasks have strict allowed and forbidden scope
- `/goal` prompts exist for Claude and Codex
- CCB and single-agent dispatch instructions exist
- Codex App audit prompt exists
- review docs show no blocking drift, conflict, missing acceptance criteria, or missing verification
- git discipline is defined

If any condition is false, output the blockers and stop before automation.

## Output Style

When reporting to the user:

- Be concise.
- Explain what documents were produced and what is still blocked.
- Do not paste every generated document unless asked.
- Point to the generated paths.

