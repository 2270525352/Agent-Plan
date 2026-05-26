# Git 提交纪律

## 基本规则

- 开始前必须运行 `git status`。
- 不覆盖用户已有改动。
- 不把无关改动混进提交。
- 不提交密钥、临时文件、失败产物、大型无关生成物。
- 每次提交前必须查看 diff。
- 每个提交必须对应一个稳定文档基线或一个独立任务。

## 建议 checkpoint

| 时机 | 提交类型 | 示例提交信息 |
|---|---|---|
| Agent-Plan 文档树初始完成 | docs baseline | `agent-plan: add planning baseline` |
| 总任务和分任务确认 | planning checkpoint | `agent-plan: split Claude and Codex tasks` |
| 一个独立代码任务完成并验收 | task checkpoint | `T-P0-0001: implement interface compatibility` |
| 审查修复完成 | review checkpoint | `REV-0001: address task boundary review` |

## 提交前检查

```bash
git status
git diff --stat
git diff
```

## 禁止提交

- 用户未授权的大范围格式化。
- 未审查通过的任务文档。
- 未解释的失败测试。
- 临时 debug 输出。
- `.env`、API key、token、密钥。
- 与当前任务无关的改动。

