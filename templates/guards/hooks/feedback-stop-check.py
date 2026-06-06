#!/usr/bin/env python3
# Agent-Plan feedback gate — Claude Code Stop hook.
#
# When the agent tries to end with uncommitted changes to BUSINESS files (outside
# docs/agent-plan/) but no execution-feedback entry for the current task, block ONCE
# and tell it to record feedback (and/or checkpoint) first. Relies on stop_hook_active
# to never loop: the agent gets exactly one nudge.
#
# Fails OPEN (exit 0) on any internal error.
import sys
import os
import json
import subprocess

CT_REL = "docs/agent-plan/04-execution/current-task.json"
FB_REL = "docs/agent-plan/04-execution/执行反馈日志.md"


def main():
    data = json.loads(sys.stdin.read())
    if data.get("stop_hook_active"):
        return 0  # already nudged once this stop — don't loop

    proj = os.path.abspath(os.environ.get("CLAUDE_PROJECT_DIR") or data.get("cwd") or os.getcwd())

    ct_path = os.path.join(proj, CT_REL)
    if not os.path.exists(ct_path):
        return 0
    with open(ct_path, encoding="utf-8") as f:
        ct = json.load(f)
    task_id = (ct.get("task_id") or "").strip()
    if not task_id:
        return 0  # planning phase

    r = subprocess.run(
        ["git", "-c", "core.quotePath=false", "-C", proj, "status", "--porcelain", "-uall"],
        capture_output=True, text=True,
    )
    if r.returncode != 0:
        return 0
    business = []
    for line in r.stdout.splitlines():
        p = line[3:].strip()
        if " -> " in p:  # rename: take destination
            p = p.split(" -> ", 1)[1]
        p = p.strip('"')
        if p and not p.startswith("docs/agent-plan/"):
            business.append(p)
    if not business:
        return 0

    fb_path = os.path.join(proj, FB_REL)
    fb = ""
    if os.path.exists(fb_path):
        with open(fb_path, encoding="utf-8") as f:
            fb = f.read()
    if task_id in fb:
        return 0  # feedback already recorded

    sys.stderr.write(
        f"[agent-plan] 先别结束:任务 {task_id} 有未提交的业务改动,但执行反馈日志里没有它的记录。\n"
        f"请按格式往 {FB_REL} 追加一条(实际改动文件 / 验收 / 测试 / 对照真相源 / 状态 / 下一步),"
        f"需要的话做一次 task checkpoint 提交,然后再结束。\n"
        f"如果你是命中停止条件要停下问用户,请把原因写进 01-requirements/开放问题.md "
        f"或 05-reviews/偏离用户原话报告.md 之后再停。\n"
    )
    return 2


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:  # fail open
        sys.stderr.write(f"[agent-plan] feedback-stop-check 跳过(内部错误,放行):{e}\n")
        sys.exit(0)
