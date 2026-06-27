#!/usr/bin/env python3
"""Headless Cursor Agent harness shim for GT-KB bridge dispatch."""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_TIMEOUT_SECONDS = 600.0
LOYAL_OPPOSITION_BRIDGE_SKILLS = frozenset({"bridge-review", "verification"})
# WI-4872: the harness-registry Cursor invocation surfaces pass the canonical
# Loyal Opposition route keys ('bridge-review', 'verification'), but no SKILL.md
# exists under those names; resolve them to the real skill directories so headless
# LO dispatch loads a contract instead of failing closed.
_SKILL_ROUTE_ALIASES = {
    "bridge-review": "proposal-review",
    "verification": "verify",
}


class CursorHarnessError(RuntimeError):
    """Raised for fail-closed Cursor harness errors."""


def _resolve_agent_executable() -> str:
    for candidate in (
        os.environ.get("CURSOR_AGENT_BIN"),
        shutil.which("agent"),
        shutil.which("cursor"),
    ):
        if not candidate:
            continue
        return candidate
    raise CursorHarnessError(
        "Cursor Agent CLI not found. Install Cursor CLI and ensure `agent` is on PATH, or set CURSOR_AGENT_BIN."
    )


def _skill_system_prompt(skill: str | None) -> str | None:
    if not skill:
        return None
    skill = _SKILL_ROUTE_ALIASES.get(skill, skill)
    skill_path = PROJECT_ROOT / ".cursor" / "skills" / skill / "SKILL.md"
    if not skill_path.is_file():
        skill_path = PROJECT_ROOT / ".codex" / "skills" / skill / "SKILL.md"
    if not skill_path.is_file():
        skill_path = PROJECT_ROOT / ".claude" / "skills" / skill / "SKILL.md"
    if not skill_path.is_file():
        raise CursorHarnessError(f"unknown skill route {skill!r}; no SKILL.md found")
    return skill_path.read_text(encoding="utf-8")


def _build_prompt(user_prompt: str, skill: str | None) -> str:
    system_prompt = _skill_system_prompt(skill)
    if not system_prompt:
        return user_prompt
    return (
        f"Follow the GT-KB skill contract below, then execute the user task.\n\n{system_prompt}\n\n---\n\n{user_prompt}"
    )


def _build_command(prompt: str, project_root: Path, *, output_format: str) -> list[str]:
    agent = _resolve_agent_executable()
    command = [agent]
    if Path(agent).name.lower() in {"cursor", "cursor.cmd", "cursor.exe"}:
        command.append("agent")
    command.extend(
        [
            "-p",
            "--trust",
            "--workspace",
            str(project_root),
            "--output-format",
            output_format,
            prompt,
        ]
    )
    return command


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the GT-KB Cursor Agent harness shim.")
    parser.add_argument("-p", "--prompt", required=True, help="Prompt to send to Cursor Agent.")
    parser.add_argument(
        "--skill",
        help="Optional skill route key (for example bridge-review or verification).",
    )
    parser.add_argument(
        "--output-format",
        default="text",
        choices=["text", "json", "stream-json"],
        help="Cursor Agent print-mode output format.",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=DEFAULT_TIMEOUT_SECONDS,
        help="Subprocess timeout in seconds.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_arg_parser()
    args = parser.parse_args(argv)
    project_root = PROJECT_ROOT
    try:
        prompt = _build_prompt(args.prompt, args.skill)
        command = _build_command(prompt, project_root, output_format=args.output_format)
        env = os.environ.copy()
        env.setdefault("GTKB_HARNESS_NAME", "cursor")
        env.setdefault("GTKB_HARNESS_ID", "E")
        completed = subprocess.run(
            command,
            cwd=str(project_root),
            env=env,
            capture_output=True,
            text=True,
            timeout=args.timeout,
            check=False,
        )
    except CursorHarnessError as exc:
        print(f"cursor_harness: {exc}", file=sys.stderr)
        return 1
    except subprocess.TimeoutExpired:
        print("cursor_harness: timed out waiting for Cursor Agent", file=sys.stderr)
        return 1
    if completed.stderr:
        sys.stderr.write(completed.stderr)
    if completed.returncode != 0:
        if completed.stdout:
            sys.stdout.write(completed.stdout)
        return completed.returncode
    sys.stdout.write(completed.stdout)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
