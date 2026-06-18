"""Hook registration working-directory robustness (WI-4623).

Asserts that every `python` hook command in ``.claude/settings.json`` that
references ``.claude/hooks/<name>.py`` resolves through the project-root-
absolute ``$CLAUDE_PROJECT_DIR`` form rather than the working-directory-
relative ``python .claude/hooks/<name>.py`` form.

The relative form is fragile: if the harness launches a hook from a
working directory other than the repo root (e.g. after a directory change
during a subagent or worktree task), the interpreter cannot locate the
script, exits with code 2, and the harness treats that as a PreToolUse
hard-block — denying every subsequent tool call until the next turn
boundary.

The fix bridge thread is
``bridge/gtkb-harness-hook-path-cwd-robustness-001.md`` (Codex GO at
``-002``); this test is the mechanical-enforcement layer per
``GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001``.
"""
# ruff: noqa: I001

from __future__ import annotations

import json
import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SETTINGS_PATH = REPO_ROOT / ".claude" / "settings.json"

# A command string is "working-directory fragile" when it starts with
# ``python `` followed directly by ``.claude/hooks/`` — i.e., the path is
# resolved relative to the harness's current working directory rather than
# the project root.
RELATIVE_HOOK_COMMAND_RE = re.compile(r"^\s*python\s+\.claude/hooks/")


def _iter_hook_commands(settings: dict) -> list[tuple[str, str, str]]:
    """Yield (event, matcher, command) triples for every registered hook."""
    rows: list[tuple[str, str, str]] = []
    for event, groups in (settings.get("hooks") or {}).items():
        if not isinstance(groups, list):
            continue
        for group in groups:
            matcher = group.get("matcher") or ""
            for hook in group.get("hooks") or []:
                command = hook.get("command") or ""
                rows.append((event, matcher, command))
    return rows


def test_no_relative_python_hook_commands_in_claude_settings() -> None:
    settings = json.loads(SETTINGS_PATH.read_text(encoding="utf-8"))
    offenders = [
        (event, matcher, command)
        for event, matcher, command in _iter_hook_commands(settings)
        if RELATIVE_HOOK_COMMAND_RE.match(command)
    ]
    assert not offenders, (
        "Found working-directory-fragile python hook registrations in "
        f"{SETTINGS_PATH.relative_to(REPO_ROOT)}. Convert each "
        "`python .claude/hooks/<name>.py` to "
        '`python "$CLAUDE_PROJECT_DIR/.claude/hooks/<name>.py"`. '
        f"Offenders: {offenders}"
    )


def test_every_claude_hook_path_resolves_through_project_root() -> None:
    """Positive assertion: every `.claude/hooks/<name>.py` reference uses
    ``$CLAUDE_PROJECT_DIR``. This catches future regressions where a new
    hook is added in the fragile form even if the offender count is small.
    """
    settings = json.loads(SETTINGS_PATH.read_text(encoding="utf-8"))
    hook_path_commands = [
        (event, matcher, command)
        for event, matcher, command in _iter_hook_commands(settings)
        if ".claude/hooks/" in command and command.lstrip().startswith("python")
    ]
    assert hook_path_commands, "No python .claude/hooks/ registrations found; test fixture stale."
    missing_project_dir = [
        (event, matcher, command)
        for event, matcher, command in hook_path_commands
        if "$CLAUDE_PROJECT_DIR" not in command
    ]
    assert not missing_project_dir, (
        "Found python `.claude/hooks/` registrations that do not anchor through "
        "$CLAUDE_PROJECT_DIR. These will fail when the harness launches hooks "
        "from any working directory other than the repo root. Offenders: "
        f"{missing_project_dir}"
    )
