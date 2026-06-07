#!/usr/bin/env python3
# Agent-Plan scope guard — Claude Code PreToolUse hook (Edit|MultiEdit|Write|NotebookEdit).
#
# Blocks a write when, for the CURRENT task, the target file:
#   - matches a `protected` glob (verbatim source of truth), or
#   - matches a `forbid` glob, or
#   - falls outside a non-empty `allow` list.
# The guard is PASSIVE until a task is active (current-task.json has a non-empty
# task_id) so planning/intake is never blocked. Append-only protection of the
# user-words doc during planning is enforced deterministically by the pre-commit hook.
#
# Fails OPEN (exit 0) on any internal error: a buggy guard must never brick the agent.
import sys
import os
import json
import re

CT_REL = "docs/agent-plan/04-execution/current-task.json"


def to_regex(pat):
    # glob: ** => any (incl /), * => any except /, ? => one non-/, trailing / => whole dir
    if pat.endswith("/"):
        pat = pat + "**"
    out, i, n = [], 0, len(pat)
    while i < n:
        c = pat[i]
        if c == "*":
            if i + 1 < n and pat[i + 1] == "*":
                out.append(".*")
                i += 2
                continue
            out.append("[^/]*")
            i += 1
            continue
        if c == "?":
            out.append("[^/]")
            i += 1
            continue
        out.append(re.escape(c))
        i += 1
    return re.compile("^" + "".join(out) + "$")


def matches_any(path, patterns):
    for p in patterns or []:
        if p and to_regex(p).match(path):
            return p
    return None


def main():
    data = json.loads(sys.stdin.read())
    tin = data.get("tool_input") or {}
    fp = tin.get("file_path") or tin.get("notebook_path") or ""
    if not fp:
        return 0

    proj = os.path.abspath(os.environ.get("CLAUDE_PROJECT_DIR") or data.get("cwd") or os.getcwd())
    rel = os.path.relpath(os.path.abspath(fp), proj).replace(os.sep, "/")

    ct = {}
    ct_path = os.path.join(proj, CT_REL)
    if os.path.exists(ct_path):
        try:
            with open(ct_path, encoding="utf-8") as f:
                ct = json.load(f)
        except Exception:
            ct = {}

    task_id = (ct.get("task_id") or "").strip()
    if not task_id:
        return 0  # planning phase: guard passive

    hit = matches_any(rel, ct.get("protected"))
    if hit:
        sys.stderr.write(
            f"[agent-plan] 拒绝:{rel} 命中受保护真相源({hit})。\n"
            f"用户原话 / 强调 / 禁止事项在执行期不改动;要追加新原话走 intake,要清洗版写进 01-requirements。\n"
        )
        return 2

    hit = matches_any(rel, ct.get("forbid"))
    if hit:
        sys.stderr.write(f"[agent-plan] 拒绝:任务 {task_id} 的禁止范围命中 {rel}({hit})。\n")
        return 2

    allow = ct.get("allow") or []
    if allow and not matches_any(rel, allow):
        sys.stderr.write(
            f"[agent-plan] 拒绝:{rel} 不在任务 {task_id} 的允许范围内。\n"
            f"允许范围:{', '.join(allow)}\n"
            f"如确需改它,先更新 03-tasks/总任务文档 与 current-task.json,不要擅自扩范围。\n"
        )
        return 2

    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:  # fail open
        sys.stderr.write(f"[agent-plan] scope-guard 跳过(内部错误,放行):{e}\n")
        sys.exit(0)
