# Codex App 定时审查提示词(单窗口 · 外层兜底)

跑 Codex 时用这套。Codex **没有内置定时器**(只能 `sleep` 阻塞硬撑),所以这个心跳交给 **Codex App 的 RRULE 调度**——它独立于主 goal 会话,会话挂了也照跑,是真·独立的外层闹钟。

## 铁律:只检测、只记录,绝不擅自修改

审查代理**只做检测**。发现问题就【只追加】记录到问题文档 `docs/agent-plan/05-reviews/偏离用户原话报告.md`,**绝不自己改任何代码或文档**,更不许碰用户原话。修不修、怎么修,由主执行 / 用户决定。

## 它只看得到已提交状态(重要)

Codex App 任务跑在**独立会话 / 环境**,以**已提交 / 已 push 的状态**为准——主执行工作区里没提交的改动它看不见。所以:

- 审查输入是**已提交的分支 diff**:先 `git fetch -q origin`,再比 `git diff <基线分支>...<任务分支>`。
- 这要求主循环每个任务都提交 + push(goal 已写死)。没提交的改动审不到,是设计如此。

## 启动顺序(重要)

**先挂这个定时任务,再开 goal。** 先有人盯着,再开始干,才能从第一分钟就抓跑偏。

## 调度(RRULE)

```text
每 30 分钟、每天:  RRULE:FREQ=HOURLY;INTERVAL=1;BYMINUTE=0,30;BYDAY=SU,MO,TU,WE,TH,FR,SA
每小时一次:        RRULE:FREQ=HOURLY;INTERVAL=1;BYMINUTE=0;BYDAY=SU,MO,TU,WE,TH,FR,SA
```

- 这是**心跳兜底**;真正的审查单元是「每个任务提交」。
- 定时任务必须跑在**项目目录 / 任务分支**里(能读到 `docs/agent-plan` 和提交历史)。
- 有些调度对 `FREQ=MINUTELY;INTERVAL=30` 支持不稳,推荐用上面 `BYMINUTE=0,30` 那条。

## 提示词

```text
你是独立审查代理,每次运行只检测、只记录,绝不改任何代码或文档。

先取最新已提交状态(你看不到未提交的工作区改动):
  git fetch -q origin
  git diff <基线分支>...<任务分支>      # 例如 git diff origin/main...HEAD
  git log --oneline <基线分支>..<任务分支>

只读:docs/agent-plan/00-source/用户原话文档.md、用户强调事项.md、禁止偏离事项.md;
docs/agent-plan/03-tasks/总任务文档.md;docs/agent-plan/04-execution/执行反馈日志.md、current-task.json;
以及上面的已提交 diff 与提交历史。

检测以下几项:
1. 实现有没有偏离用户原话。
2. 改动有没有超出任务允许范围(对照 current-task.json 的 allow / forbid)。
3. 有没有硬编码事实 / 价格 / 链接 / 话术 / 临时数据。
4. 进度跟文档(总任务、阶段)对不对得上。
5. 执行反馈日志跟已提交 diff 对不对得上(有没有漏写、谎报)。
6. 有没有大量改动迟迟不按任务粒度提交(会让审查变瞎)。
7. current-task.json 的 task_id 是否跟最近提交 / 反馈对得上。

输出:状态 GREEN / YELLOW / RED + 具体问题清单 + 涉及文件。

处置(只检测、只记录):
- 发现问题(YELLOW / RED)就【只追加】写进 docs/agent-plan/05-reviews/偏离用户原话报告.md。
- RED:在报告里标 RED,让主执行停下等用户确认。
- 绝不自己修复、绝不改业务代码、绝不动用户原话。修复交给主执行 / 用户。
```
