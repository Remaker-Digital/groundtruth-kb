# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Drift-repair regression tests for gtkb-settings-merge (C4).

Covers binding conditions from bridge/gtkb-settings-merge-004.md GO:

- §3.1 (10 tests): each of the 10 C4-promoted settings-hook-registrations
  triggers a ``merge-event-hooks`` action when missing, and execute_upgrade
  restores it to the canonical event list.
- §3.2 (3 tests): each of the 3 C4-promoted gitignore-pattern rows triggers
  an ``append-gitignore`` action when missing, and execute_upgrade restores
  it to ``.gitignore``.

Copyright (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
Licensed under AGPL-3.0-or-later.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

from groundtruth_kb.project.upgrade import execute_upgrade, plan_upgrade

# ---------------------------------------------------------------------------
# Fixtures + helpers
# ---------------------------------------------------------------------------


def _write_minimal_toml(target: Path, profile: str = "dual-agent", version: str | None = None) -> None:
    """Write a minimal groundtruth.toml at the target's scaffold_version.

    If ``version`` is None, uses the current package version (same-version
    drift scenario).
    """
    from groundtruth_kb import __version__

    effective_version = version or __version__
    toml_path = target / "groundtruth.toml"
    toml_path.write_text(
        f"""[groundtruth]
db_path = "groundtruth.db"

[project]
project_name = "Test"
owner = "Test Owner"
profile = "{profile}"
copyright_notice = ""
cloud_provider = "none"
scaffold_version = "{effective_version}"
created_at = "2026-01-01T00:00:00Z"
""",
        encoding="utf-8",
    )


def _setup_git_for_upgrade(target: Path) -> None:
    """Init git + clean initial commit so execute_upgrade preconditions pass.

    Per bridge gtkb-rollback-receipts-014, execute_upgrade requires a clean
    git work tree to anchor the rollback receipt. Mirrors the helper in
    tests/test_upgrade.py.
    """
    subprocess.run(["git", "init", "--initial-branch=main"], cwd=target, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=target, check=True)
    subprocess.run(["git", "config", "user.name", "Test"], cwd=target, check=True)
    subprocess.run(["git", "config", "commit.gpgsign", "false"], cwd=target, check=True)
    subprocess.run(["git", "config", "core.autocrlf", "false"], cwd=target, check=True)
    subprocess.run(["git", "add", "-A"], cwd=target, check=True)
    subprocess.run(
        ["git", "commit", "-m", "pre-upgrade snapshot", "--allow-empty"],
        cwd=target,
        check=True,
        capture_output=True,
    )


# Full canonical settings.json shape for dual-agent profile post-C4. Used as
# the baseline; each §3.1 test deletes exactly one registration by hook_filename.
_FULL_SETTINGS_BY_EVENT: dict[str, list[str]] = {
    "SessionStart": ["session-start-governance.py", "assertion-check.py"],
    "UserPromptSubmit": [
        "turn-marker.py",
        "delib-preflight-gate.py",
        "gov09-capture.py",
        "delib-search-gate.py",
        "intake-classifier.py",
    ],
    "PostToolUse": ["owner-decision-capture.py", "delib-search-tracker.py"],
    "PreToolUse": [
        "scanner-safe-writer.py",
        "spec-before-code.py",
        "bridge-compliance-gate.py",
        "kb-not-markdown.py",
        "destructive-gate.py",
        "credential-scan.py",
    ],
}


def _settings_dict(omit_hook: str | None = None) -> dict[str, object]:
    """Build a canonical dual-agent settings.json dict.

    ``omit_hook`` is a hook filename; if set, the matching entry is dropped
    from its event class. Event classes themselves remain present.
    """
    hooks: dict[str, list[dict[str, object]]] = {}
    for event, filenames in _FULL_SETTINGS_BY_EVENT.items():
        event_entries: list[dict[str, object]] = []
        for fn in filenames:
            if fn == omit_hook:
                continue
            event_entries.append({"hooks": [{"type": "command", "command": f"python .claude/hooks/{fn}"}]})
        hooks[event] = event_entries
    return {"hooks": hooks}


def _write_settings_json(target: Path, omit_hook: str | None = None) -> None:
    settings_dir = target / ".claude"
    settings_dir.mkdir(parents=True, exist_ok=True)
    data = _settings_dict(omit_hook=omit_hook)
    (settings_dir / "settings.json").write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def _read_event_commands(settings_path: Path, event: str) -> list[str]:
    """Return the list of ``command`` strings for ``event`` in settings.json."""
    data = json.loads(settings_path.read_text(encoding="utf-8"))
    entries = data.get("hooks", {}).get(event, [])
    commands: list[str] = []
    for entry in entries:
        for h in entry.get("hooks", []):
            cmd = h.get("command", "")
            if isinstance(cmd, str):
                commands.append(cmd)
    return commands


# ---------------------------------------------------------------------------
# §3.1 — Settings-hook drift repair (one test per C4-promoted registration)
# ---------------------------------------------------------------------------

# (hook_filename, expected_event) for each of the 10 promoted registrations.
_PROMOTED_SETTINGS_REGISTRATIONS: list[tuple[str, str]] = [
    ("session-start-governance.py", "SessionStart"),
    ("assertion-check.py", "SessionStart"),
    ("delib-search-gate.py", "UserPromptSubmit"),
    ("intake-classifier.py", "UserPromptSubmit"),
    ("delib-search-tracker.py", "PostToolUse"),
    ("spec-before-code.py", "PreToolUse"),
    ("bridge-compliance-gate.py", "PreToolUse"),
    ("kb-not-markdown.py", "PreToolUse"),
    ("destructive-gate.py", "PreToolUse"),
    ("credential-scan.py", "PreToolUse"),
]


@pytest.mark.parametrize(("hook_filename", "expected_event"), _PROMOTED_SETTINGS_REGISTRATIONS)
def test_c4_settings_drift_repair(tmp_path: Path, hook_filename: str, expected_event: str) -> None:
    """C4 §3.1: removing a promoted registration triggers merge-event-hooks
    and execute_upgrade restores it in canonical event list.
    """
    _write_minimal_toml(tmp_path, profile="dual-agent")
    _write_settings_json(tmp_path, omit_hook=hook_filename)
    # Minimal gitignore with ALL 4 managed patterns so only settings drift is seen.
    (tmp_path / ".gitignore").write_text(
        ".claude/hooks/*.log\ngroundtruth.db\n.groundtruth/\n.claude/settings.local.json\n",
        encoding="utf-8",
    )

    # 1. plan surfaces the right merge action.
    actions = plan_upgrade(tmp_path)
    merge_actions = [a for a in actions if a.action == "merge-event-hooks" and a.event == expected_event]
    assert merge_actions, (
        f"expected merge-event-hooks for {expected_event} when {hook_filename} missing; "
        f"got: {[(a.action, a.event, a.file) for a in actions]}"
    )

    # 2. execute restores the entry.
    _setup_git_for_upgrade(tmp_path)
    execute_upgrade(tmp_path, actions, force=False)

    settings_path = tmp_path / ".claude" / "settings.json"
    restored_commands = _read_event_commands(settings_path, expected_event)
    expected_marker = f"python .claude/hooks/{hook_filename}"
    assert any(expected_marker in cmd for cmd in restored_commands), (
        f"expected {expected_marker!r} restored in {expected_event} after execute_upgrade; "
        f"got commands: {restored_commands}"
    )


# ---------------------------------------------------------------------------
# §3.2 — Gitignore drift repair (one test per C4-promoted pattern)
# ---------------------------------------------------------------------------

# Patterns promoted to upgrade-managed in C4.
_PROMOTED_GITIGNORE_PATTERNS: list[str] = [
    "groundtruth.db",
    ".groundtruth/",
    ".claude/settings.local.json",
]


@pytest.mark.parametrize("pattern", _PROMOTED_GITIGNORE_PATTERNS)
def test_c4_gitignore_drift_repair(tmp_path: Path, pattern: str) -> None:
    """C4 §3.2: removing a promoted gitignore pattern triggers append-gitignore
    and execute_upgrade restores it to .gitignore.
    """
    _write_minimal_toml(tmp_path, profile="dual-agent")
    # Full canonical settings.json so only gitignore drift is seen.
    _write_settings_json(tmp_path, omit_hook=None)
    # Gitignore has all managed patterns EXCEPT the one under test.
    all_patterns = [".claude/hooks/*.log", "groundtruth.db", ".groundtruth/", ".claude/settings.local.json"]
    kept = [p for p in all_patterns if p != pattern]
    (tmp_path / ".gitignore").write_text("\n".join(kept) + "\n", encoding="utf-8")

    # 1. plan surfaces the append action.
    actions = plan_upgrade(tmp_path)
    append_actions = [a for a in actions if a.action == "append-gitignore" and a.payload == pattern]
    assert append_actions, (
        f"expected append-gitignore for {pattern!r}; "
        f"got: {[(a.action, a.payload) for a in actions if a.action == 'append-gitignore']}"
    )

    # 2. execute restores the pattern.
    _setup_git_for_upgrade(tmp_path)
    execute_upgrade(tmp_path, actions, force=False)

    gitignore_text = (tmp_path / ".gitignore").read_text(encoding="utf-8")
    gitignore_lines = {line.strip() for line in gitignore_text.splitlines()}
    assert pattern in gitignore_lines, (
        f"expected {pattern!r} restored in .gitignore after execute_upgrade; got lines: {sorted(gitignore_lines)}"
    )
    # The kept patterns are still present — no data loss.
    for kept_pattern in kept:
        assert kept_pattern in gitignore_lines, f"{kept_pattern!r} disappeared after restore"
