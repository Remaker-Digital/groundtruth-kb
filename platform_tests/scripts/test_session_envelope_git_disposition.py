"""Regression guard for WI-5325 session-envelope Git disposition."""

from __future__ import annotations

import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

IGNORED_RUNTIME_ENVELOPE_PATHS = (
    "harness-state/codex/session-envelope.json",
    "harness-state/claude/session-envelopes/session-example.json",
    "harness-state/openrouter/session-envelope-archive/2026-07-17T04-00-00Z-session-envelope.json",
)

VISIBLE_HARNESS_CONTROL_PATHS = (
    "harness-state/harness-registry.json",
    "harness-state/harness-identities.json",
    "harness-state/codex/operating-role.md",
    "harness-state/codex/session-startup-preferences.json",
    "harness-state/codex/session-envelope-notes.json",
)


def _git(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def test_runtime_session_envelope_paths_are_gitignored() -> None:
    for test_path in IGNORED_RUNTIME_ENVELOPE_PATHS:
        result = _git("check-ignore", "--no-index", "-v", test_path)

        assert result.returncode == 0, (
            f"Expected {test_path!r} to be gitignored. stdout: {result.stdout!r} stderr: {result.stderr!r}"
        )


def test_durable_harness_controls_remain_visible_to_git() -> None:
    for test_path in VISIBLE_HARNESS_CONTROL_PATHS:
        result = _git("check-ignore", "--no-index", "-q", test_path)

        assert result.returncode == 1, (
            f"Expected {test_path!r} to remain visible to git. stdout: {result.stdout!r} stderr: {result.stderr!r}"
        )
