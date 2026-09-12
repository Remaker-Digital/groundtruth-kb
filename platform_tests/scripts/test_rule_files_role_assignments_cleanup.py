"""Regression checks for the Phase-1 rule-files role-assignment cleanup."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

PROTECTED_TARGETS = (
    ".claude/rules/operating-role.md",
    ".claude/rules/canonical-terminology.md",
    ".claude/rules/acting-prime-builder.md",
    ".claude/rules/bridge-essential.md",
    ".claude/rules/codex-session-bootstrap.md",
    ".claude/rules/prime-builder-role.md",
    "CLAUDE.md",
    "AGENTS.md",
)

LIVE_GUIDANCE_TARGETS = (
    "AGENTS.md",
    "CLAUDE.md",
    *tuple(path.as_posix() for path in sorted((ROOT / ".claude" / "rules").glob("*.md"))),
)

MIRROR = "role-assignments.json"
CANONICAL_READER = "groundtruth_kb.harness_projection.read_roles"
CANONICAL_READER_CLI_GROUP = "gt harness"
CANONICAL_READER_CLI_SUBCOMMAND = "roles"
SINGULAR_READER_COMMAND = re.compile(r"gt harness " + r"role(?!s)\b")
OVERLAY_POINTERS = (
    "harness-state/claude/operating-role.md",
    "harness-state/codex/operating-role.md",
)

OPERATING_ROLE_ALLOWED_MIRROR_SNIPPETS = (
    "legacy `harness-state/role-assignments.json` mirror is orphan per\nSlice 1 retirement",
    "Legacy `harness-state/role-assignments.json` mirror is orphan per\n  Slice 1 retirement",
    "legacy compat mirror `harness-state/role-assignments.json` (orphan per Slice 1 retirement; no live writer)",
    "legacy `harness-state/role-assignments.json` is an\norphan compat mirror",
    "Retire harness-state/role-assignments.json legacy mirror",
)


def _read(relpath: str) -> str:
    return (ROOT / relpath).read_text(encoding="utf-8")


def _gt_command() -> str:
    for candidate in (
        ROOT / "groundtruth-kb" / ".venv" / "Scripts" / "gt.exe",
        ROOT / "groundtruth-kb" / ".venv" / "bin" / "gt",
    ):
        if candidate.exists():
            return str(candidate)
    return "gt"


def test_legacy_overlay_pointer_files_are_deleted() -> None:
    """The per-harness operating-role pointer files are retired from live state."""
    for relpath in OVERLAY_POINTERS:
        assert not (ROOT / relpath).exists(), f"legacy overlay pointer still exists: {relpath}"


def test_live_guidance_has_no_overlay_pointer_references() -> None:
    """Live guidance should refer to the root operating-role rule, not deleted overlays."""
    for relpath in LIVE_GUIDANCE_TARGETS:
        text = _read(relpath)
        for pointer in OVERLAY_POINTERS:
            assert pointer not in text, f"{relpath} still references deleted overlay {pointer}"
