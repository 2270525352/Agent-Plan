#!/usr/bin/env python3
"""Bootstrap root Agent-Plan coordination files in a target project.

This helper is conservative by design:
- AGENTS.md is merged through the AGENT_PLAN_START/END marked block.
- Existing non-Agent-Plan AGENTS.md content is preserved.
- CURRENT_STATE.md is created if missing and left untouched by default if present.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path
import re
import shutil
import sys


ROOT = Path(__file__).resolve().parents[1]
TEMPLATES = ROOT / "templates" / "bootstrap"
AGENTS_START = "<!-- AGENT_PLAN_START -->"
AGENTS_END = "<!-- AGENT_PLAN_END -->"
AGENTS_BLOCK_RE = re.compile(
    rf"{re.escape(AGENTS_START)}.*?{re.escape(AGENTS_END)}",
    re.DOTALL,
)


class BootstrapError(Exception):
    pass


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def backup(path: Path) -> Path:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    backup_path = path.with_name(f"{path.name}.agent-plan.{stamp}.bak")
    i = 1
    while backup_path.exists():
        backup_path = path.with_name(f"{path.name}.agent-plan.{stamp}.{i}.bak")
        i += 1
    shutil.copy2(path, backup_path)
    return backup_path


def extract_agents_block(template: str) -> str:
    match = AGENTS_BLOCK_RE.search(template)
    if not match:
        raise BootstrapError("AGENTS template is missing Agent-Plan markers")
    return match.group(0).rstrip() + "\n"


def merge_agents(project: Path, *, force: bool) -> str:
    template_path = TEMPLATES / "AGENTS.md"
    dest = project / "AGENTS.md"
    block = extract_agents_block(read_text(template_path))

    if not dest.exists():
        write_text(dest, read_text(template_path))
        return "created AGENTS.md"

    existing = read_text(dest)
    if AGENTS_BLOCK_RE.search(existing):
        merged = AGENTS_BLOCK_RE.sub(block.rstrip(), existing).rstrip() + "\n"
        if merged == existing:
            return "AGENTS.md unchanged"
        backup_path = backup(dest)
        write_text(dest, merged)
        return f"updated Agent-Plan block in AGENTS.md (backup: {backup_path.name})"

    if not force:
        backup_path = backup(dest)
        prefix = existing.rstrip()
        merged = f"{prefix}\n\n{block}" if prefix else block
        write_text(dest, merged)
        return f"appended Agent-Plan block to existing AGENTS.md (backup: {backup_path.name})"

    backup_path = backup(dest)
    write_text(dest, read_text(template_path))
    return f"replaced AGENTS.md from template (backup: {backup_path.name})"


def create_current_state(project: Path, *, force: bool, append_log: bool) -> str:
    template_path = TEMPLATES / "CURRENT_STATE.md"
    dest = project / "CURRENT_STATE.md"
    template = read_text(template_path)

    if not dest.exists():
        write_text(dest, template)
        return "created CURRENT_STATE.md"

    if force:
        backup_path = backup(dest)
        write_text(dest, template)
        return f"replaced CURRENT_STATE.md from template (backup: {backup_path.name})"

    if append_log:
        existing = read_text(dest)
        stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        record = (
            "\n\n### STATE-agent-plan-bootstrap\n\n"
            f"Time: {stamp}\n\n"
            "Actor: Agent-Plan bootstrap\n\n"
            "Event Type: bootstrap\n\n"
            "Summary: Agent-Plan bootstrap ran. Existing CURRENT_STATE.md was preserved; update the current snapshot before execution.\n\n"
            "Files touched: AGENTS.md, CURRENT_STATE.md\n\n"
            "Verification: manual review required\n\n"
            "Blockers:\n\n"
            "Next step: refresh Current Snapshot fields before starting /goal or implementation.\n"
        )
        backup_path = backup(dest)
        write_text(dest, existing.rstrip() + record)
        return f"appended bootstrap log to CURRENT_STATE.md (backup: {backup_path.name})"

    return "CURRENT_STATE.md exists; preserved (update it manually before execution)"


def install(project: Path, *, force_agents: bool, force_current_state: bool, append_state_log: bool) -> int:
    project = project.resolve()
    if not TEMPLATES.exists():
        raise BootstrapError(f"bootstrap templates not found: {TEMPLATES}")
    if not project.exists():
        raise BootstrapError(f"project not found: {project}")

    print(f"[agent-plan] project: {project}")
    print(f"[agent-plan] {merge_agents(project, force=force_agents)}")
    print(
        "[agent-plan] "
        + create_current_state(
            project,
            force=force_current_state,
            append_log=append_state_log,
        )
    )
    return 0


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Bootstrap Agent-Plan root coordination files.")
    sub = parser.add_subparsers(dest="command", required=True)

    install_parser = sub.add_parser("install", help="create or merge AGENTS.md and CURRENT_STATE.md")
    install_parser.add_argument("--project", required=True, help="target project directory")
    install_parser.add_argument(
        "--force-agents",
        action="store_true",
        help="replace AGENTS.md instead of merging/appending the Agent-Plan block",
    )
    install_parser.add_argument(
        "--force-current-state",
        action="store_true",
        help="replace CURRENT_STATE.md from the template",
    )
    install_parser.add_argument(
        "--append-state-log",
        action="store_true",
        help="append a bootstrap record when CURRENT_STATE.md already exists",
    )
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    try:
        if args.command == "install":
            return install(
                Path(args.project),
                force_agents=args.force_agents,
                force_current_state=args.force_current_state,
                append_state_log=args.append_state_log,
            )
    except BootstrapError as exc:
        print(f"[agent-plan] ERROR: {exc}", file=sys.stderr)
        return 1
    return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
