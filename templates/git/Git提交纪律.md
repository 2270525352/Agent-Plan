# Git 提交纪律

## 基本规则

- 开始前必须运行 `git status`。
- 不覆盖用户已有改动。
- 不把无关改动混进提交。
- 不提交密钥、临时文件、失败产物、大型无关生成物。
- 每次提交前必须查看 diff。
- 每个提交必须对应一个稳定文档基线或一个独立任务。

## 提交门槛（必须全部满足才允许提交）

1. **自己审查 3 次**:每次都对照真相源(用户原话 / 需求 / 接口契约)看完整 diff,确认没超范围、没偏离、没硬编码。
2. **测试 / 验收通过**:任务的验收命令和测试必须跑过;跑不了要写明原因,不许假装通过。
3. **提交信息带名字 + 任务编号**:必须写清是哪个 AI 提交的、对应哪个任务,方便事后排查。

### 提交信息格式

```text
<任务编号> (<AI 名字>): <一句话简述>
```

示例:

```text
T-P0-0001 (Codex): 实现接口兼容层
REV-0001 (Claude): 修复需求对齐审查指出的边界问题
```

## 建议 checkpoint

| 时机 | 提交类型 | 示例提交信息 |
|---|---|---|
| Agent-Plan 文档树初始完成 | docs baseline | `BASELINE (Claude): add planning baseline` |
| 规划确认、可进入执行 | planning checkpoint | `PLAN (Claude): freeze 总任务文档` |
| 一个独立任务完成并验收 | task checkpoint | `T-P0-0001 (Codex): implement interface compatibility` |
| 审查修复完成 | review checkpoint | `REV-0001 (Claude): address alignment review` |

## 提交前检查

```bash
git status
git diff --stat
git diff
```

## 禁止提交

- 用户未授权的大范围格式化。
- 未通过审查的任务文档。
- 未解释的失败测试。
- 临时 debug 输出。
- `.env`、API key、token、密钥。
- 与当前任务无关的改动。
