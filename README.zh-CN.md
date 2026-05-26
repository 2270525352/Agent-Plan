<div align="center">

# Agent-Plan — 多 AI 协作的前置规划 Skill

<p>
  <img src="https://img.shields.io/badge/skill-agent--plan-0B7285?style=for-the-badge" alt="agent-plan skill">
  <img src="https://img.shields.io/badge/for-Claude%20%7C%20Codex-2F9E44?style=for-the-badge" alt="for Claude and Codex">
  <img src="https://img.shields.io/badge/output-AI%20readable%20plan%20tree-CF1322?style=for-the-badge" alt="AI readable plan tree">
</p>

[![Provider](https://img.shields.io/badge/provider-Claude%20%7C%20Codex%20%7C%20OpenCode-lightgrey.svg)]()
[![Mode](https://img.shields.io/badge/mode-multi--agent%20%7C%20single--agent-blue.svg)]()
[![Pairs with](https://img.shields.io/badge/pairs%20with-CCB-orange.svg)](https://github.com/SeemSeam/claude_codex_bridge)
[![Docs](https://img.shields.io/badge/docs-Chinese%20plan%20tree-orange.svg)]()

**中文** | [English](README.md)

[为什么需要前置规划](#为什么需要前置规划) · [它解决什么](#它解决什么) · [核心原则](#核心原则) · [快速开始](#快速开始) · [输出目录](#输出目录) · [默认分工](#默认分工) · [自动模式门禁](#自动模式门禁) · [与-ccb-配合](#与-ccb-配合) · [安装](#安装)

</div>

---

## 为什么需要前置规划

单个 AI 处理小任务足够了。但当工作需要拆需求、定架构、分工、并行实现、审查、提交时，AI 在写代码的过程中很容易**重新理解需求**，于是越做越偏。

人话对人类清晰，对 AI 模糊。Agent-Plan 把"理解需求"这件事提前固化到规划阶段，让实现代理只按已审查通过的文档做事。

| 价值 | 通俗说明 |
| :--- | :--- |
| 需求不漂移 | 用户原话只追加、不改写，永远可追溯到最初表达。 |
| 边界不打架 | Claude 负责规划，Codex 负责实现，互不越界。 |
| 进度可自动审查 | Codex App 定时巡检偏离、冲突、漏项、git 脏状态。 |
| 多 AI / 单 AI 通吃 | 有 CCB 就分发，没 CCB 就用单窗口顺序执行同一份计划。 |

<details>
<summary><b>为什么"边写边想"会出问题</b></summary>

- 实现代理在编码时遇到模糊点，会按自己的猜测补全，而不是回头问。
- 多个代理各自补全，补出来的方向互相冲突。
- 长任务没有冻结的接口契约，后写的代码改了前面的约定。
- 没有验收标准，"完成"全凭感觉，审查无从下手。
- 用户的原始表达被一次次"润色总结"后，最初的意图被稀释甚至改写。

</details>

## 它解决什么

Agent-Plan 是一个用于多 AI 协作前置规划的 Codex / Claude skill。它的目的不是写一份好看的计划，而是生成一整套 **AI 可读、可执行、可审查、可分工、可自动化跟踪** 的项目文档。

使用 Agent-Plan 后，项目应该先拥有下面这些内容，再进入实现：

- **用户原话文档** — 原封不动，只追加，不改写、不润色、不翻译、不总结替代。
- **AI 可读需求文档** — 把大白话转成带 id、约束、禁止项、验收标准的可执行需求。
- **总需求文档**。
- **总架构文档、架构图、总设计文档、接口契约** — 冻结边界与对外约定。
- **总任务文档** — 每个任务带 owner、来源需求、允许/禁止范围、依赖、验收命令、停止条件。
- **分代理任务文档** — Claude / Codex / Reviewer(Claude) / OpenCode 各一份，边界不重叠。
- **`/goal` 提示词** — 供 Claude 和 Codex 直接粘贴。
- **CCB 分发提示词** — `/ask` 与 `ccb ask` 两种形式。
- **单 AI 执行说明** — 没有 CCB 也能跑同一份计划。
- **Codex App 定时审查提示词** — 默认每 30 分钟巡检一次。
- **Git 提交纪律与提交检查表**。

## 核心原则

> 不要让 AI 在写代码的时候重新理解需求。

需求理解、架构判断、任务拆分、边界确认，都应该在实现前完成。执行代理只按已经审查通过的任务文档做事。

四条不可妥协的规则：

| 规则 | 含义 |
| :--- | :--- |
| 保真用户原话 | `00-source/用户原话文档.md` 只追加。需要清洗版时，另写 AI 可读需求文档，绝不在原话里改。 |
| 面向 AI 的文档要 AI 可读 | 用稳定字段：允许范围、禁止范围、依赖、验收标准、验证命令、停止条件，不靠纯散文。 |
| 先定分工再分配任务 | 先问 Claude / Codex / Reviewer / OpenCode / CCB 如何分工；用户不指定就用默认分工。 |
| 思考与执行分离 | Claude 管需求/架构/拆分/对齐审查；Codex 只做边界清晰的代码任务；Reviewer 只审不写；OpenCode 只查技术风险。 |

## 快速开始

让你的 AI 代理调用 Agent-Plan：

```text
$agent-plan 为这个项目建立规划文档树。保留我的原话，拆出 Claude / Codex / Reviewer 任务，
生成 /goal 提示词，并创建一个 Codex App 每 30 分钟的定时审查提示词。
```

典型流程：

1. 记录用户原话。
2. 生成 AI 可读需求。
3. 生成总需求、架构、设计、接口契约。
4. 生成总任务文档。
5. 在 CCB 或当前对话里讨论 Claude / Codex / Reviewer 分工。
6. 拆出分代理任务文档（Claude / Codex / Reviewer-Claude / OpenCode）。
7. 用多个代理审查文档是否对齐原话、是否漏项、是否任务打架。
8. 审查通过后生成 Claude / Codex `/goal`。
9. 输出 CCB 分发提示词。
10. 输出 Codex App 定时审查自动化提示词。
11. 进入实现，并按 Git 检查点提交。

## 输出目录

默认在目标项目生成 `docs/agent-plan/`：

```text
docs/agent-plan/
  00-source/        用户原话文档.md  用户强调事项.md  禁止偏离事项.md
  01-requirements/  总需求文档.md  AI可读需求文档.md  需求对齐检查表.md  开放问题.md
  02-architecture/  总架构文档.md  架构图.md  总设计文档.md  接口契约文档.md
  03-tasks/         总任务文档.md  任务依赖图.md  阶段交付计划.md
  04-agents/        分工总说明.md  Claude任务文档.md  Codex任务文档.md  Reviewer-Claude任务文档.md  OpenCode审查任务文档.md
  05-reviews/       需求对齐审查.md  架构一致性审查.md  任务冲突审查.md  偏离用户原话报告.md  自动模式门禁.md
  06-goals/         Claude-goal.md  Codex-goal.md
  07-dispatch/      CCB分发提示词.md  CodexApp定时审查提示词.md
  08-runtime/       CCB多AI执行模式.md  单AI执行模式.md  CodexApp自动化模式.md
  09-git/           Git提交纪律.md  提交检查表.md
```

每一层对应的模板见 [`templates/`](templates/)。

<details>
<summary><b>各层目录职责</b></summary>

| 目录 | 职责 |
| :--- | :--- |
| `00-source/` | 保留用户原始意图与硬边界，最高真相源。 |
| `01-requirements/` | 把大白话转成可执行需求，逐条可追溯到原话。 |
| `02-architecture/` | 定义架构、设计、图、冻结的接口契约。 |
| `03-tasks/` | 定义阶段、依赖、任务验收。 |
| `04-agents/` | 按代理能力与禁止范围拆分工作。 |
| `05-reviews/` | 自动化前的审查与偏离跟踪。 |
| `06-goals/` | Claude / Codex 的 `/goal` 提示词。 |
| `07-dispatch/` | CCB 分发与 Codex App 自动化提示词。 |
| `08-runtime/` | 有无 CCB 的执行模式。 |
| `09-git/` | Git 检查点与提交纪律。 |

</details>

## 默认分工

未被用户覆盖时采用下列默认分工：

| 角色 | 默认代理 | 负责 | 禁止 |
| :--- | :--- | :--- | :--- |
| 规划 | Claude | 需求沟通、用户原话保真、总需求、总架构、总设计、任务拆分 | 未确认就让实现代理开干 |
| 实现 | Codex | 明确代码任务、接口兼容、测试、修 bug | 改原话、改需求方向、自由改 AI 策略、碰 prompt、硬编码事实 |
| 审查 | Reviewer(Claude) | 文档审查、需求对齐、任务冲突审查、自动模式门禁 | 实现代码 |
| 技术审查 | OpenCode | 查硬编码、查测试缺口、查接口偏离、查代码风险 | 定义需求或产品方向 |
| 调度 | CCB | 分发任务、跨代理沟通、共享上下文 | 代替文档重新解释需求 |
| 自动审查 | Codex App | 每 30 分钟检查偏离、冲突、漏项、git 状态 | 擅自推进未授权实现 |

> `/goal` 是 Claude 和 Codex pane 的 provider 命令，不是 CCB 通用命令。OpenCode 默认按"不支持 `/goal`、只做审查"处理。

## 自动模式门禁

只有当下列条件**全部**满足时，计划才被认为可以进入多 AI 自动执行或 Codex App 自动化推进：

- 用户原话已记录且只追加。
- AI 可读需求可追溯到用户原话记录。
- 架构与设计覆盖了当前阶段 / P0 需求。
- 总任务可追溯到需求。
- Claude / Codex / Reviewer 任务边界不重叠。
- Codex 任务有明确的允许与禁止范围。
- Claude / Codex `/goal` 已生成。
- CCB 与单 AI 分发说明都已存在。
- Codex App 审查提示词已生成。
- 审查文档显示没有阻塞性偏离、冲突、缺失验收标准或缺失验证。
- Git 提交纪律已定义。

任一条件不满足时，skill 会输出阻塞项并停在自动化之前，写入 `05-reviews/自动模式门禁.md`。

## 与 CCB 配合

Agent-Plan 负责**规划**，[CCB（Claude Codex Bridge）](https://github.com/SeemSeam/claude_codex_bridge) 负责**让多个真实 CLI 代理在一个可见、可控的终端工作区里协作执行**。两者天然互补：

- Agent-Plan 在 `07-dispatch/CCB分发提示词.md` 里直接生成 CCB 可用的 `/ask` 与 `ccb ask` 分发提示词。
- 在 CCB 的 Claude / Codex pane 里用 `/goal` 粘贴 `06-goals/` 下对应的目标文件，长期目标即固定下来。
- CCB 的角色分离（main 规划 / worker 实现 / reviewer 审查）与 Agent-Plan 的默认分工一一对应。

典型组合：用 Agent-Plan 把需求固化成文档树并通过自动模式门禁，再用 CCB 把任务分发到各个 CLI 代理并行执行，OpenCode/Reviewer 审查，Codex App 定时巡检偏离。

```text
# 在 CCB 中，给各 pane 设置目标与任务
/goal              -> 粘贴 docs/agent-plan/06-goals/Claude-goal.md（Claude pane）
/goal              -> 粘贴 docs/agent-plan/06-goals/Codex-goal.md（Codex pane）
/ask claude        -> 读取并执行 docs/agent-plan/04-agents/Claude任务文档.md
/ask codex         -> 只执行 docs/agent-plan/04-agents/Codex任务文档.md 中已授权任务
/ask reviewer      -> 按 Reviewer-Claude任务文档.md 做对齐与冲突审查
```

没有 CCB 也没关系：`08-runtime/单AI执行模式.md` 给出在单个 Claude / Codex 窗口里顺序执行同一份计划的规则。

## 安装

把本目录克隆到你的 skills 目录：

```bash
mkdir -p "$CODEX_HOME/skills"
git clone https://github.com/YOUR_NAME/agent-plan.git "$CODEX_HOME/skills/agent-plan"
```

Claude Code 用户：把整个 skill 目录复制到对应的 Claude skills 位置即可。

## 相关项目

- [CCB — Claude Codex Bridge](https://github.com/SeemSeam/claude_codex_bridge)：可见、可控的多代理 CLI 终端工作区，用 tmux 把 Codex / Claude / Gemini / OpenCode 等真实 CLI 放进同一个项目里协作。Agent-Plan 生成的分发提示词与 `/goal` 可直接在 CCB 中使用。

## License

见 [LICENSE](LICENSE)。
