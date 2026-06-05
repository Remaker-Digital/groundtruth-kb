"""Regression checks for the Phase-1 rule-files role-assignment cleanup."""

from __future__ import annotations

import json
import re
import subprocess
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


def test_rule_files_have_no_live_role_assignments_mirror_authority() -> None:
    """Only enumerated operating-role provenance may still cite the retired mirror."""
    for relpath in PROTECTED_TARGETS:
        if relpath == ".claude/rules/operating-role.md":
            continue
        assert MIRROR not in _read(relpath), f"{relpath} still cites retired {MIRROR}"

    operating_role = _read(".claude/rules/operating-role.md")
    assert operating_role.count(MIRROR) == len(OPERATING_ROLE_ALLOWED_MIRROR_SNIPPETS)
    for snippet in OPERATING_ROLE_ALLOWED_MIRROR_SNIPPETS:
        assert snippet in operating_role


def test_rule_files_cite_canonical_role_reader_entrypoint() -> None:
    """Each protected role surface points live role reads at the canonical reader."""
    for relpath in PROTECTED_TARGETS:
        text = _read(relpath)
        assert CANONICAL_READER in text, f"{relpath} does not cite {CANONICAL_READER}"
        assert CANONICAL_READER_CLI_GROUP in text, f"{relpath} does not cite {CANONICAL_READER_CLI_GROUP}"
        assert CANONICAL_READER_CLI_SUBCOMMAND in text, f"{relpath} does not cite {CANONICAL_READER_CLI_SUBCOMMAND}"


def test_rule_files_do_not_cite_singular_harness_role_command() -> None:
    """The deprecated singular CLI spelling must not remain in live guidance."""
    for relpath in PROTECTED_TARGETS:
        assert SINGULAR_READER_COMMAND.search(_read(relpath)) is None, (
            f"{relpath} still cites singular harness-role reader command"
        )


def test_canonical_reader_cli_subcommand_is_live() -> None:
    """The documented CLI reader subcommand should execute and emit the projection."""
    result = subprocess.run(
        [_gt_command(), "harness", CANONICAL_READER_CLI_SUBCOMMAND],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(result.stdout)
    assert "harnesses" in payload


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


def test_canonical_reader_entrypoint_glossary_entry_present() -> None:
    """The new first-contact concept is present in canonical terminology."""
    text = _read(".claude/rules/canonical-terminology.md")
    assert "### canonical reader entrypoint" in text
    assert "DCL-HARNESS-STATE-SOT-READER-CONTRACT-001" in text
    assert "groundtruth_kb.harness_projection.{read_roles, read_identity, read_capabilities}" in text
