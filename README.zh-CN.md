<div align="center">

# Agent-Plan — 单 AI 自主执行的前置规划 Skill

<p>
  <img src="https://img.shields.io/badge/skill-agent--plan-0B7285?style=for-the-badge" alt="agent-plan skill">
  <img src="https://img.shields.io/badge/for-Claude%20%7C%20Codex-2F9E44?style=for-the-badge" alt="for Claude and Codex">
  <img src="https://img.shields.io/badge/output-AI%20readable%20plan%20tree-CF1322?style=for-the-badge" alt="AI readable plan tree">
</p>

[![Provider](https://img.shields.io/badge/provider-Claude%20%7C%20Codex-lightgrey.svg)]()
[![Mode](https://img.shields.io/badge/mode-single--AI%20autonomous-blue.svg)]()
[![Anti-drift](https://img.shields.io/badge/anti--drift-self--check%20%2B%20scheduled%20tests-orange.svg)]()
[![Docs](https://img.shields.io/badge/docs-Chinese%20plan%20tree-orange.svg)]()

**中文** | [English](README.md)

[为什么需要前置规划](#为什么需要前置规划) · [它解决什么](#它解决什么) · [核心原则](#核心原则) · [两层防跑偏](#两层防跑偏) · [快速开始](#快速开始) · [输出目录](#输出目录) · [自动模式门禁](#自动模式门禁) · [安装](#安装)

</div>

---

## 为什么需要前置规划

单个 AI 处理小任务足够了。但当它要长时间自主执行——拆需求、定架构、实现、跑测试、提交——AI 在写代码的过程中很容易**重新理解需求**，于是越做越偏。没有第二个 AI 帮它兜底，跑偏只会越积越多。

人话对人类清晰，对 AI 模糊。Agent-Plan 把"理解需求"这件事提前固化到规划阶段，冻结成真相源，再用两层机制盯着这一个 AI 别跑偏。

| 价值 | 通俗说明 |
| :--- | :--- |
| 需求不漂移 | 用户原话只追加、不改写，永远可追溯到最初表达。 |
| 细节够颗粒 | 每个任务步骤可勾选、允许/禁止范围具体到文件，验收可命令化。 |
| 执行有反馈 | 每次执行都回写真实改动、验收/测试结果、对照真相源的结论。 |
| 跑偏能抓住 | AI 自检 + 定时测试两层兜底，红了就停。 |

<details>
<summary><b>为什么"边写边想"会出问题</b></summary>

- AI 在编码时遇到模糊点，会按自己的猜测补全，而不是回头问。
- 长任务没有冻结的接口契约，后写的代码改了前面的约定。
- 没有验收标准，"完成"全凭感觉，没法复核。
- 用户的原始表达被一次次"润色总结"后，最初的意图被稀释甚至改写。
- 自主跑得越久，偏差越积越大，等人发现时已经偏很远。

</details>

## 它解决什么

Agent-Plan 是一个用于**单 AI 自主执行**前置规划的 Codex / Claude skill。目标不是写一份好看的计划，而是生成一整套 **AI 可读、可执行、可反馈、可定时审查** 的项目文档，让一个 Claude 或一个 Codex 窗口照着自主干，且不跑偏。

使用后，项目应先拥有下面这些内容，再进入实现：

- **用户原话文档** — 原封不动，只追加，不改写、不润色、不翻译、不总结替代。
- **AI 可读需求文档** — 把大白话转成带 id、约束、禁止项、验收标准的可执行需求。
- **总需求、总架构、架构图、总设计、接口契约** — 冻结边界与对外约定。
- **总任务文档** — 每个任务带来源需求、允许/禁止范围、颗粒化步骤、依赖、验收命令、测试命令、停止条件。
- **任务说明 + 执行反馈日志** — 这一个 AI 的任务、范围、自检节奏，以及每次执行的真实回写。
- **Claude / Codex `/goal` 提示词** — 让单个 AI 自主跑完整循环。
- **定时测试方案 + 两套触发提示词** — 跑测试 + 对照真相源，按所用 AI 选 Claude Code 定时任务或 Codex App。
- **Git 提交纪律与提交检查表**。

## 核心原则

> 不要让 AI 在写代码的时候重新理解需求。

需求理解、架构判断、任务拆分、边界确认，都应该在实现前完成并冻结。执行阶段只按已审查通过的任务文档做事，并把每一步都反馈出来。

四条不可妥协的规则：

| 规则 | 含义 |
| :--- | :--- |
| 保真用户原话 | `00-source/用户原话文档.md` 只追加。需要清洗版时，另写 AI 可读需求文档，绝不在原话里改。 |
| 文档要 AI 可读且颗粒 | 用稳定字段：允许范围、禁止范围、依赖、验收标准、验证命令、停止条件；步骤可逐条勾选。 |
| 执行必须有反馈 | 每个任务、每次自检都写入执行反馈日志：真实改动、验收/测试结果、对照真相源结论。没写反馈视为未完成。 |
| 两层防跑偏 | AI 自检是内部第一道防线，定时测试是外部兜底，两者都要。 |

## 两层防跑偏

只有一个 AI 在跑，没有第二个 AI 复核，所以靠两层机制盯住它：

| 层 | 机制 | 触发时机 | 做什么 |
| :--- | :--- | :--- | :--- |
| 内层 | AI 自检 | 每完成一个任务、每改一大块、每接近禁止范围 | 重读真相源 + 跑验收/测试 + 写执行反馈 |
| 外层 | 定时测试 | 每 30 分钟（或每完成 N 个任务） | 跑测试套件 + 跑验收命令 + 重读真相源 + 对照执行反馈与真实 diff + 查 git，输出 GREEN/YELLOW/RED |

> 触发器跟着所用 AI 走：跑 **Claude** 就用 **Claude Code 的 `/schedule`（cron 定时任务）**；跑 **Codex** 就用 **Codex App 自动化**。两套提示词内容一致，用哪个 AI 就用哪套。定时测试只审查、只报告，不擅自改业务代码；发现 RED 就停下并写入偏离报告。

## 快速开始

让你的 AI 代理调用 Agent-Plan：

```text
$agent-plan 为这个项目建立规划文档树。保留我的原话，写一份颗粒化、带执行反馈的总任务文档，
生成 Claude 和 Codex 的 /goal 提示词，并创建一个定时测试（跑 Claude 用 Claude Code 定时任务，
跑 Codex 用 Codex App），定时跑测试并对照真相源审查是否跑偏。
```

典型流程：

1. 记录用户原话。
2. 生成 AI 可读需求。
3. 生成总需求、架构、设计、接口契约。
4. 生成颗粒化总任务文档（含验收命令、测试命令、执行反馈字段）。
5. 生成任务说明与执行反馈日志。
6. 审查文档是否对齐原话、是否漏项、是否缺验收。
7. 审查通过后生成 Claude / Codex `/goal`。
8. 生成定时测试方案与对应触发提示词（Claude Code 定时任务 / Codex App）。
9. 进入实现：单 AI 自主跑循环，自检 + 定时测试兜底，按 Git 检查点提交。

## 输出目录

默认在目标项目生成 `docs/agent-plan/`：

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

每一层对应的模板见 [`templates/`](templates/);一份**填好的样板**(小项目 `local-todo-cli`)见 [`examples/`](examples/),直接看「填好长啥样」。

<details>
<summary><b>各层目录职责</b></summary>

| 目录 | 职责 |
| :--- | :--- |
| `00-source/` | 保留用户原始意图与硬边界，最高真相源。 |
| `01-requirements/` | 把大白话转成可执行需求，逐条可追溯到原话。 |
| `02-architecture/` | 定义架构、设计、图、冻结的接口契约。 |
| `03-tasks/` | 定义阶段、依赖、颗粒化任务与验收。 |
| `04-execution/` | 单 AI 的范围、任务列表、自检节奏与执行反馈日志。 |
| `05-reviews/` | 自动化前的审查与偏离跟踪。 |
| `06-goals/` | Claude / Codex 的 `/goal` 提示词。 |
| `07-testing/` | 定时测试方案与触发提示词（Claude Code / Codex App）。 |
| `08-runtime/` | 单 AI 执行循环与停止条件。 |
| `09-git/` | Git 检查点与提交纪律。 |

</details>

## 自动模式门禁

只有当下列条件**全部**满足时，计划才被认为可以进入单 AI 自主自动化执行：

- 用户原话已记录且只追加。
- AI 可读需求可追溯到用户原话记录。
- 架构与设计覆盖了当前阶段 / P0 需求。
- 接口契约明确且冻结。
- 总任务可追溯到需求，且颗粒度足够。
- 任务说明的允许/禁止范围清楚。
- 每个任务都有验收命令和验收标准。
- 执行反馈日志机制已建立。
- Claude / Codex `/goal` 已生成。
- 单 AI 执行模式已生成。
- 定时测试方案已生成。
- 按所用 AI 的触发提示词已生成（Claude Code 定时任务 或 Codex App 定时测试）。
- Git 提交纪律已定义。
- 审查文档显示没有阻塞性偏离、缺失验收标准或缺失验证。

任一条件不满足时，skill 会输出阻塞项并停在自动化之前，写入 `05-reviews/自动模式门禁.md`。

## 安装

把本目录克隆到你的 skills 目录：

```bash
mkdir -p "$CODEX_HOME/skills"
git clone https://github.com/YOUR_NAME/agent-plan.git "$CODEX_HOME/skills/agent-plan"
```

Claude Code 用户：把整个 skill 目录复制到对应的 Claude skills 位置即可。

## License

见 [LICENSE](LICENSE)。
