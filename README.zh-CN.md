<div align="center">

# Agent-Plan — 主线 AI 自主执行的前置规划 Skill

<p>
  <img src="https://img.shields.io/badge/skill-agent--plan-0B7285?style=for-the-badge" alt="agent-plan skill">
  <img src="https://img.shields.io/badge/for-Claude%20%7C%20Codex-2F9E44?style=for-the-badge" alt="for Claude and Codex">
  <img src="https://img.shields.io/badge/output-AI%20readable%20plan%20tree-CF1322?style=for-the-badge" alt="AI readable plan tree">
  <img src="https://img.shields.io/badge/release-v1.1.0-2F9E44?style=for-the-badge" alt="release v1.1.0">
</p>

[![Provider](https://img.shields.io/badge/provider-Claude%20%7C%20Codex-lightgrey.svg)]()
[![Mode](https://img.shields.io/badge/mode-mainline%20AI%20autonomous-blue.svg)]()
[![Anti-drift](https://img.shields.io/badge/anti--drift-self--check%20%2B%20merge--gate%20%2B%20audit%20%2B%20guards-orange.svg)]()
[![Docs](https://img.shields.io/badge/docs-Chinese%20plan%20tree-orange.svg)]()

**中文** | [English](README.md)

[为什么需要前置规划](#为什么需要前置规划) · [它解决什么](#它解决什么) · [核心原则](#核心原则) · [防跑偏](#防跑偏) · [快速开始](#快速开始) · [分档](#分档) · [输出目录](#输出目录) · [自动模式门禁](#自动模式门禁) · [安装](#安装)

📋 当前 main：主线窗口 + 支线合流门禁；**v1.1.0**：护栏（hooks + git）+ 分档 + 已提交状态审查 —— 见 [更新日志](CHANGELOG.md)

</div>

---

## 为什么需要前置规划

一个主线 AI 窗口处理小任务足够了。但当它要长时间自主执行——拆需求、定架构、实现、跑测试、提交——AI 在写代码的过程中很容易**重新理解需求**，于是越做越偏。如果它再调用多个智能体协助，主线和支线不分清楚，偏移会更隐蔽：支线可能做得很努力，但方向已经不属于原任务。

人话对人类清晰，对 AI 模糊。Agent-Plan 把"理解需求"这件事提前固化到规划阶段，冻结成真相源，再让一个主线窗口负责到底；支线智能体只能拿合同做局部协助，返回后必须由主线做合流门禁。

| 价值 | 通俗说明 |
| :--- | :--- |
| 需求不漂移 | 用户原话只追加、不改写，永远可追溯到最初表达。 |
| 细节够颗粒 | 每个任务步骤可勾选、允许/禁止范围具体到文件，验收可命令化。 |
| 执行有反馈 | 每次执行、每次支线派发、每次合流都回写真实改动、验收/测试结果、对照真相源的结论。 |
| 跑偏能抓住 | 主线自检 + 支线合流门禁 + 定时测试三层兜底，红了就停。 |

<details>
<summary><b>为什么"边写边想"会出问题</b></summary>

- AI 在编码时遇到模糊点，会按自己的猜测补全，而不是回头问。
- 长任务没有冻结的接口契约，后写的代码改了前面的约定。
- 没有验收标准，"完成"全凭感觉，没法复核。
- 用户的原始表达被一次次"润色总结"后，最初的意图被稀释甚至改写。
- 多个智能体并行时，如果没有父任务、允许范围、验收和合流记录，支线结果很容易把主线带偏。
- 自主跑得越久，偏差越积越大，等人发现时已经偏很远。

</details>

## 它解决什么

Agent-Plan 是一个用于**主线 AI 自主执行**前置规划的 Codex / Claude skill。目标不是写一份好看的计划，而是生成一整套 **AI 可读、可执行、可反馈、可定时审查** 的项目文档，让一个 Claude、Codex 或 CLI 对话窗口照着自主干；需要多个智能体协助时，也能分清主线和支线，保证任务完整性与偏移度可控。

使用后，项目应先拥有下面这些内容，再进入实现：

- **用户原话文档** — 原封不动，只追加，不改写、不润色、不翻译、不总结替代。
- **AI 可读需求文档** — 把大白话转成带 id、约束、禁止项、验收标准的可执行需求。
- **总需求、总架构、架构图、总设计、接口契约** — 冻结边界与对外约定。
- **总任务文档** — 每个任务带来源需求、允许/禁止范围、颗粒化步骤、依赖、验收命令、测试命令、停止条件。
- **任务说明 + 执行反馈日志 + 支线任务记录** — 主线任务、范围、自检节奏、每次执行回写，以及支线合同与合流决策。
- **Claude / Codex `/goal` 提示词** — 让主线 AI 自主跑完整循环。
- **定时测试方案 + 两套触发提示词** — 跑测试 + 对照真相源，按所用 AI 选 Claude Code 定时任务或 Codex App。
- **Git 提交纪律与提交检查表**。
- **护栏（hooks + git）** — 把「改错文件、动用户原话、提交格式、push main」从「提示词请求」变成「工具强制」:Claude 用实时 hook + git hook,Codex 用 git hook。

## 核心原则

> 不要让 AI 在写代码的时候重新理解需求。

需求理解、架构判断、任务拆分、边界确认，都应该在实现前完成并冻结。执行阶段只按已审查通过的任务文档做事，并把每一步都反馈出来。

五条不可妥协的规则：

| 规则 | 含义 |
| :--- | :--- |
| 保真用户原话 | `00-source/用户原话文档.md` 只追加。需要清洗版时，另写 AI 可读需求文档，绝不在原话里改。 |
| 文档要 AI 可读且颗粒 | 用稳定字段：允许范围、禁止范围、依赖、验收标准、验证命令、停止条件；步骤可逐条勾选。 |
| 执行必须有反馈 | 每个任务、每次自检都写入执行反馈日志；每次支线派发、返回、合流或拒绝都写入支线任务记录。没写反馈视为未完成。 |
| 主线权威唯一 | 主线窗口负责解释真相源、推进任务状态、判断合流、提交代码和决定停止；支线不能改需求方向、架构方向或任务边界。 |
| 三层防跑偏 | 主线自检是内部第一道防线，支线合流门禁防止协作偏移，定时测试是外部兜底。 |
| 能强制就强制 | 能脚本判定的纪律交给护栏（Claude Code hooks + git hooks）硬执行，不只靠提示词。 |

## 防跑偏

主线窗口可以调用支线智能体，但只有主线能解释真相源和推进状态。防跑偏靠三层检测盯住它：

| 层 | 机制 | 触发时机 | 做什么 |
| :--- | :--- | :--- | :--- |
| 内层 | 主线自检 | 每完成一个任务、每改一大块、每接近禁止范围 | 重读真相源 + 跑验收/测试 + 写执行反馈 |
| 合流层 | 支线合流门禁 | 每次支线返回后、父任务完成前 | 查完整性、允许范围、真相源追溯、冲突、验收/测试、偏移度，输出 GREEN/YELLOW/RED |
| 外层 | 定时测试 | 每完成一个任务提交（30 分钟为心跳兜底） | 跑测试套件 + 跑验收命令 + 重读真相源 + 对照执行反馈与已提交分支 diff + 查 git，输出 GREEN/YELLOW/RED |

> 触发器跟着所用 AI 走：跑 **Claude** 就用 **Claude Code 的 `/schedule`（cron 定时任务）**；跑 **Codex** 就用 **Codex App 自动化**。两套提示词内容一致，用哪个 AI 就用哪套。定时测试只审查、只报告，不擅自改业务代码；发现 RED 就停下并写入偏离报告。
>
> **只看已提交状态**：远程定时代理看不到未提交的工作区改动，所以审查输入是已提交的分支 diff（`git diff 基线...任务分支`），主循环每个任务都要提交 + push。审查单元是「每个任务提交」，30 分钟是心跳兜底。

**护栏（硬执行底座）：** 上面几层是「提示词 + 审查」，都还可能被无视。skill 另生成一层 hooks + git 护栏，把能机器判定的规则直接拦死：改越界文件、改用户原话、提交格式不对、push 到 main 当场失败。跑 Claude 有实时 hook + git 双层，跑 Codex 靠 git hook（提交时）。详见 `10-guards/`。

护栏用 `scripts/agent-plan-guards.py install|verify|uninstall` 安装、校验和卸载。安装器会合并 Claude settings,并且遇到 Husky / lefthook / pre-commit / 自定义 `core.hooksPath` 时默认不接管;先把 Agent-Plan hooks 串到已有 hook 系统里,只有用户明确同意时才用 `--force-hooks-path`。

## 护栏生命周期

在目标项目安装并校验护栏:

```bash
python3 scripts/agent-plan-guards.py install --project /path/to/project
python3 scripts/agent-plan-guards.py verify --project /path/to/project
```

如果项目已有 hook manager,安装器会复制 Agent-Plan hooks,但保留原来的 `core.hooksPath`。请从已有 hook 系统里串联 `.githooks/pre-commit`、`.githooks/commit-msg`、`.githooks/pre-push`,然后这样校验:

```bash
python3 scripts/agent-plan-guards.py verify --project /path/to/project --allow-existing-hooks-path
```

只卸载 Agent-Plan 自己的 hook 文件和 Claude hook 条目:

```bash
python3 scripts/agent-plan-guards.py uninstall --project /path/to/project
```

只有确认 `.githooks` 是该项目专门给 Agent-Plan 用的,才加 `--unset-hooks-path`。

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
5. 生成任务说明、执行反馈日志与支线任务记录。
6. 审查文档是否对齐原话、是否漏项、是否缺验收。
7. 审查通过后生成 Claude / Codex `/goal`。
8. 生成定时测试方案与对应触发提示词（Claude Code 定时任务 / Codex App）。
9. 进入实现：主线 AI 自主跑循环；必要时按合同派发支线，合流门禁通过后再纳入主线；按 Git 检查点提交。

## 分档

别给一个 todo CLI 生成 28 个文件。选一档，决定生成哪些文档；**防跑偏核心（真相源、AI 可读需求、总任务、任务说明+反馈+支线记录、goal、定时审查、运行时、git、护栏）每档都有**，分档只加规划深度。

| 档 | 适用 | 大致 |
| :--- | :--- | :--- |
| **lite** | 小 / 单组件 / 一次性，需求基本清楚 | ~14 个文件，只有核心。不单出架构文档（有真接口才加 `接口契约文档`）。 |
| **standard**（默认） | 一般的多模块项目 | lite + `用户强调事项`、`需求对齐检查表`、`总架构文档`（图内嵌）+ `接口契约文档`、`阶段交付计划`、`需求对齐审查`、`提交检查表`。~20 个。 |
| **full** | 大 / 多组件 / 团队交接 / 合规 | 全部模板，含展开的散文档 `总需求`、`总设计`、`架构图`、`任务依赖图`、`架构一致性审查`。~28 个。 |

> 合并冗余：lite/standard 不出「把可读结构再用大白话重写一遍」的散文档——`总需求文档`（用 `AI可读需求文档`）、`总设计 / 架构图`（mermaid 内嵌进 `总架构文档`）。full 保留展开版，给大项目和交接用。

## 输出目录

默认在目标项目生成 `docs/agent-plan/`（下面是 **full** 全量树，lite/standard 取子集，见上「分档」）：

```text
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
  10-guards/        护栏说明.md（可执行部分装到 .claude/ 与 .githooks/）
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
| `04-execution/` | 主线任务范围、任务列表、自检节奏、执行反馈日志、支线合同与合流记录。 |
| `05-reviews/` | 自动化前的审查与偏离跟踪。 |
| `06-goals/` | Claude / Codex 的 `/goal` 提示词。 |
| `07-testing/` | 定时测试方案与触发提示词（Claude Code / Codex App）。 |
| `08-runtime/` | 主线执行循环、支线协作规则与停止条件。 |
| `09-git/` | Git 检查点与提交纪律。 |
| `10-guards/` | 把纪律变成 hooks + git 硬约束：实时拦越界写入、保护用户原话、提交门禁、禁 push main。 |

</details>

## 自动模式门禁

只有当下列条件**全部**满足时，计划才被认为可以进入主线 AI 自主自动化执行：

- 用户原话已记录且只追加。
- AI 可读需求可追溯到用户原话记录。
- 架构与设计覆盖了当前阶段 / P0 需求。
- 接口契约明确且冻结。
- 总任务可追溯到需求，且颗粒度足够。
- 任务说明的允许/禁止范围清楚。
- 支线策略已明确：禁用支线，或已生成支线合同与合流门禁模板。
- 每个任务都有验收命令和验收标准。
- 执行反馈日志机制已建立。
- Claude / Codex `/goal` 已生成。
- 主线执行模式已生成。
- 定时测试方案已生成。
- 按所用 AI 的触发提示词已生成（Claude Code 定时任务 或 Codex App 定时测试）。
- Git 提交纪律已定义。
- 护栏已用 `agent-plan-guards.py verify` 校验（Claude Code hooks + git hooks 生效，或已有 hook manager 已明确串联 Agent-Plan hooks，`current-task.json` 存在）。
- 审查文档显示没有阻塞性偏离、缺失验收标准或缺失验证。

任一条件不满足时，skill 会输出阻塞项并停在自动化之前，写入 `05-reviews/自动模式门禁.md`。

## 安装

把本目录克隆到你的 skills 目录：

```bash
mkdir -p "$CODEX_HOME/skills"
git clone https://github.com/2270525352/Agent-Plan.git "$CODEX_HOME/skills/agent-plan"
```

Claude Code 用户：把整个 skill 目录复制到对应的 Claude skills 位置即可。

## License

见 [LICENSE](LICENSE)。
