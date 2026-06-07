#!/usr/bin/env python3
"""Install, verify, or remove Agent-Plan guardrails in a target project.

The installer is intentionally conservative:
- it copies only Agent-Plan-owned hook files;
- it merges Claude settings instead of replacing them;
- it does not take over an existing non-.githooks core.hooksPath unless asked.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shutil
import stat
import subprocess
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
TEMPLATES = ROOT / "templates" / "guards"
AGENT_PLAN_DIR = Path("docs") / "agent-plan"
CURRENT_TASK_REL = AGENT_PLAN_DIR / "04-execution" / "current-task.json"
GUARDS_DOC_REL = AGENT_PLAN_DIR / "10-guards" / "护栏说明.md"


class GuardError(Exception):
    pass


def run_git(project: Path, args: list[str]) -> tuple[int, str, str]:
    result = subprocess.run(
        ["git", "-C", str(project), *args],
        capture_output=True,
        text=True,
    )
    return result.returncode, result.stdout.strip(), result.stderr.strip()


def is_git_repo(project: Path) -> bool:
    code, _, _ = run_git(project, ["rev-parse", "--show-toplevel"])
    return code == 0


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise GuardError(f"Invalid JSON: {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise GuardError(f"Expected JSON object: {path}")
    return data


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def backup(path: Path) -> Path:
    backup_path = path.with_suffix(path.suffix + ".agent-plan.bak")
    i = 1
    while backup_path.exists():
        backup_path = path.with_suffix(path.suffix + f".agent-plan.bak.{i}")
        i += 1
    shutil.copy2(path, backup_path)
    return backup_path


def same_file_content(src: Path, dest: Path) -> bool:
    return dest.exists() and src.read_bytes() == dest.read_bytes()


def looks_agent_plan_owned(path: Path) -> bool:
    text = path.read_text(encoding="utf-8", errors="ignore")
    return "Agent-Plan" in text or "agent-plan" in text


def copy_owned(src: Path, dest: Path, *, force: bool) -> str:
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists():
        if same_file_content(src, dest):
            return "unchanged"
        if not force or not looks_agent_plan_owned(dest):
            raise GuardError(
                f"Refusing to overwrite existing file: {dest}. "
                "Use --force to replace Agent-Plan hook files."
            )
    shutil.copy2(src, dest)
    mode = dest.stat().st_mode
    dest.chmod(mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    return "written"


def preflight_copy(destinations: list[tuple[Path, Path]], *, force: bool) -> None:
    conflicts: list[str] = []
    for src, dest in destinations:
        if not src.exists():
            conflicts.append(f"missing template: {src}")
            continue
        if not dest.exists() or same_file_content(src, dest):
            continue
        if force and looks_agent_plan_owned(dest):
            continue
        conflicts.append(
            f"would overwrite existing non-matching file: {dest}"
            + (" (not Agent-Plan-owned)" if force else "")
        )
    if conflicts:
        raise GuardError(
            "Guardrail install preflight failed; no files were copied:\n"
            + "\n".join(f"- {item}" for item in conflicts)
        )


def canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


def merge_claude_settings(project: Path) -> tuple[bool, Path | None]:
    incoming_path = TEMPLATES / "settings.hooks.json"
    incoming = load_json(incoming_path)
    settings_path = project / ".claude" / "settings.json"
    existing = load_json(settings_path)
    changed = False

    hooks = existing.setdefault("hooks", {})
    if not isinstance(hooks, dict):
        raise GuardError(f"Expected .claude/settings.json hooks to be an object: {settings_path}")

    for event, entries in (incoming.get("hooks") or {}).items():
        if not isinstance(entries, list):
            raise GuardError(f"Expected hook entries to be a list for {event}: {incoming_path}")
        current = hooks.setdefault(event, [])
        if not isinstance(current, list):
            raise GuardError(f"Expected .claude/settings.json hooks.{event} to be a list")
        seen = {canonical(entry) for entry in current}
        for entry in entries:
            key = canonical(entry)
            if key not in seen:
                current.append(entry)
                seen.add(key)
                changed = True

    if changed or not settings_path.exists():
        backup_path = backup(settings_path) if settings_path.exists() else None
        write_json(settings_path, existing)
        return True, backup_path
    return False, None


def remove_claude_settings(project: Path) -> bool:
    incoming = load_json(TEMPLATES / "settings.hooks.json")
    settings_path = project / ".claude" / "settings.json"
    if not settings_path.exists():
        return False
    existing = load_json(settings_path)
    hooks = existing.get("hooks")
    if not isinstance(hooks, dict):
        return False

    changed = False
    for event, entries in (incoming.get("hooks") or {}).items():
        current = hooks.get(event)
        if not isinstance(current, list):
            continue
        remove_keys = {canonical(entry) for entry in entries}
        kept = [entry for entry in current if canonical(entry) not in remove_keys]
        if len(kept) != len(current):
            hooks[event] = kept
            changed = True
        if hooks.get(event) == []:
            hooks.pop(event, None)
    if hooks == {}:
        existing.pop("hooks", None)

    if changed:
        backup(settings_path)
        write_json(settings_path, existing)
    return changed


def install(project: Path, *, force: bool, force_hooks_path: bool) -> int:
    project = project.resolve()
    if not TEMPLATES.exists():
        raise GuardError(f"Guard templates not found: {TEMPLATES}")

    print(f"[agent-plan] project: {project}")

    copy_plan = [
        (
            TEMPLATES / "hooks" / "scope-guard.py",
            project / ".claude" / "hooks" / "scope-guard.py",
        ),
        (
            TEMPLATES / "hooks" / "feedback-stop-check.py",
            project / ".claude" / "hooks" / "feedback-stop-check.py",
        ),
        (
            TEMPLATES / "githooks" / "pre-commit",
            project / ".githooks" / "pre-commit",
        ),
        (
            TEMPLATES / "githooks" / "commit-msg",
            project / ".githooks" / "commit-msg",
        ),
        (
            TEMPLATES / "githooks" / "pre-push",
            project / ".githooks" / "pre-push",
        ),
    ]
    preflight_copy(copy_plan, force=force)

    for name in ("scope-guard.py", "feedback-stop-check.py"):
        status = copy_owned(
            TEMPLATES / "hooks" / name,
            project / ".claude" / "hooks" / name,
            force=force,
        )
        print(f"[agent-plan] {status}: .claude/hooks/{name}")

    changed, backup_path = merge_claude_settings(project)
    if changed:
        msg = "merged: .claude/settings.json"
        if backup_path:
            msg += f" (backup: {backup_path.name})"
        print(f"[agent-plan] {msg}")
    else:
        print("[agent-plan] unchanged: .claude/settings.json")

    for name in ("pre-commit", "commit-msg", "pre-push"):
        status = copy_owned(
            TEMPLATES / "githooks" / name,
            project / ".githooks" / name,
            force=force,
        )
        print(f"[agent-plan] {status}: .githooks/{name}")

    current_task = project / CURRENT_TASK_REL
    if current_task.exists():
        print(f"[agent-plan] unchanged: {CURRENT_TASK_REL}")
    else:
        current_task.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(TEMPLATES / "current-task.json", current_task)
        print(f"[agent-plan] written: {CURRENT_TASK_REL}")

    guards_doc = project / GUARDS_DOC_REL
    if not guards_doc.exists():
        guards_doc.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(TEMPLATES / "护栏说明.md", guards_doc)
        print(f"[agent-plan] written: {GUARDS_DOC_REL}")

    if not is_git_repo(project):
        print("[agent-plan] warning: not a git repo; git hooks were copied but not enabled.")
        return 0

    code, current_hooks_path, _ = run_git(project, ["config", "--get", "core.hooksPath"])
    if code != 0 or not current_hooks_path:
        code, _, err = run_git(project, ["config", "core.hooksPath", ".githooks"])
        if code != 0:
            raise GuardError(f"Failed to set core.hooksPath: {err}")
        print("[agent-plan] enabled: git config core.hooksPath .githooks")
    elif current_hooks_path == ".githooks":
        print("[agent-plan] unchanged: core.hooksPath=.githooks")
    elif force_hooks_path:
        code, _, err = run_git(project, ["config", "core.hooksPath", ".githooks"])
        if code != 0:
            raise GuardError(f"Failed to replace core.hooksPath: {err}")
        print(f"[agent-plan] replaced: core.hooksPath {current_hooks_path!r} -> '.githooks'")
    else:
        print(
            "[agent-plan] warning: existing core.hooksPath is "
            f"{current_hooks_path!r}; Agent-Plan did not replace it."
        )
        print(
            "[agent-plan] integrate manually by chaining .githooks/pre-commit, "
            ".githooks/commit-msg, and .githooks/pre-push from the existing hook system, "
            "or rerun with --force-hooks-path after user approval."
        )
    return 0


def verify(project: Path, *, allow_existing_hooks_path: bool) -> int:
    project = project.resolve()
    errors: list[str] = []
    warnings: list[str] = []

    required = [
        project / ".claude" / "hooks" / "scope-guard.py",
        project / ".claude" / "hooks" / "feedback-stop-check.py",
        project / ".githooks" / "pre-commit",
        project / ".githooks" / "commit-msg",
        project / ".githooks" / "pre-push",
        project / CURRENT_TASK_REL,
    ]
    for path in required:
        if not path.exists():
            errors.append(f"missing: {path.relative_to(project)}")

    for path in required[2:5]:
        if path.exists() and not os.access(path, os.X_OK):
            errors.append(f"not executable: {path.relative_to(project)}")

    try:
        settings = load_json(project / ".claude" / "settings.json")
        incoming = load_json(TEMPLATES / "settings.hooks.json")
        hooks = settings.get("hooks") if isinstance(settings, dict) else None
        if not isinstance(hooks, dict):
            errors.append("missing Claude hooks in .claude/settings.json")
        else:
            for event, entries in (incoming.get("hooks") or {}).items():
                current = hooks.get(event, [])
                current_keys = {canonical(entry) for entry in current if isinstance(current, list)}
                for entry in entries:
                    if canonical(entry) not in current_keys:
                        errors.append(f"missing Claude {event} Agent-Plan hook")
    except GuardError as exc:
        errors.append(str(exc))

    current_task_path = project / CURRENT_TASK_REL
    if current_task_path.exists():
        try:
            ct = load_json(current_task_path)
            for key in ("task_id", "phase", "allow", "forbid", "protected", "acceptance_cmd", "test_cmd"):
                if key not in ct:
                    errors.append(f"current-task.json missing key: {key}")
            for key in ("allow", "forbid", "protected"):
                if key in ct and not isinstance(ct[key], list):
                    errors.append(f"current-task.json {key} must be a list")
            if not (ct.get("task_id") or "").strip():
                warnings.append("current-task.json task_id is empty; scope guard is passive in planning mode")
        except GuardError as exc:
            errors.append(str(exc))

    if is_git_repo(project):
        code, current_hooks_path, _ = run_git(project, ["config", "--get", "core.hooksPath"])
        if code != 0 or not current_hooks_path:
            errors.append("core.hooksPath is not set")
        elif current_hooks_path != ".githooks":
            msg = f"core.hooksPath is {current_hooks_path!r}, not '.githooks'"
            if allow_existing_hooks_path:
                warnings.append(
                    msg
                    + "; assuming Agent-Plan hooks are chained from the existing hook manager"
                )
            else:
                errors.append(msg)
    else:
        warnings.append("not a git repo; git hooks cannot be active")

    if errors:
        print("[agent-plan] guard verification: FAILED")
        for item in errors:
            print(f"  error: {item}")
        for item in warnings:
            print(f"  warning: {item}")
        return 1

    print("[agent-plan] guard verification: OK")
    for item in warnings:
        print(f"  warning: {item}")
    return 0


def uninstall(project: Path, *, unset_hooks_path: bool) -> int:
    project = project.resolve()
    removed = False

    for path in [
        project / ".claude" / "hooks" / "scope-guard.py",
        project / ".claude" / "hooks" / "feedback-stop-check.py",
        project / ".githooks" / "pre-commit",
        project / ".githooks" / "commit-msg",
        project / ".githooks" / "pre-push",
    ]:
        if path.exists():
            text = path.read_text(encoding="utf-8", errors="ignore")
            if "Agent-Plan" in text or "agent-plan" in text:
                path.unlink()
                print(f"[agent-plan] removed: {path.relative_to(project)}")
                removed = True
            else:
                print(f"[agent-plan] skipped non-Agent-Plan file: {path.relative_to(project)}")

    if remove_claude_settings(project):
        print("[agent-plan] removed Agent-Plan entries from .claude/settings.json")
        removed = True

    if unset_hooks_path and is_git_repo(project):
        code, current_hooks_path, _ = run_git(project, ["config", "--get", "core.hooksPath"])
        if code == 0 and current_hooks_path == ".githooks":
            code, _, err = run_git(project, ["config", "--unset", "core.hooksPath"])
            if code != 0:
                raise GuardError(f"Failed to unset core.hooksPath: {err}")
            print("[agent-plan] unset: core.hooksPath")
            removed = True

    if not removed:
        print("[agent-plan] no Agent-Plan guard files found")
    return 0


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "command",
        choices=("install", "verify", "uninstall"),
        help="Guardrail lifecycle command.",
    )
    parser.add_argument(
        "--project",
        default=".",
        help="Target project root. Defaults to current directory.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Replace existing Agent-Plan hook files when their content differs.",
    )
    parser.add_argument(
        "--force-hooks-path",
        action="store_true",
        help="Install only: replace an existing non-.githooks core.hooksPath.",
    )
    parser.add_argument(
        "--unset-hooks-path",
        action="store_true",
        help="Uninstall only: unset core.hooksPath when it is .githooks.",
    )
    parser.add_argument(
        "--allow-existing-hooks-path",
        action="store_true",
        help=(
            "Verify only: accept an existing non-.githooks hook manager after "
            "Agent-Plan hooks have been explicitly chained from it."
        ),
    )
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    project = Path(args.project)
    try:
        if args.command == "install":
            return install(project, force=args.force, force_hooks_path=args.force_hooks_path)
        if args.command == "verify":
            return verify(project, allow_existing_hooks_path=args.allow_existing_hooks_path)
        if args.command == "uninstall":
            return uninstall(project, unset_hooks_path=args.unset_hooks_path)
        raise GuardError(f"Unknown command: {args.command}")
    except GuardError as exc:
        print(f"[agent-plan] error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
