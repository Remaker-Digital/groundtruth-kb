"""Current guidance must not point to retired role-assignment overlays."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LIVE_GUIDANCE_TARGETS = (
    "AGENTS.md",
    "CLAUDE.md",
    *tuple(path.as_posix() for path in sorted((ROOT / ".harness-baseline-configuration" / "rules").glob("*.md"))),
)
OVERLAY_POINTERS = (
    "harness-state/claude/operating-role.md",
    "harness-state/codex/operating-role.md",
)


def _read(relpath: str) -> str:
    return (ROOT / relpath).read_text(encoding="utf-8")


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
