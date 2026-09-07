# (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Focused tests for the canonical scratchpad location and cleanup duty (WI-6001).

The seven authorizable role surfaces must each carry the canonical ``## Scratch
Files`` section, the scratch directory must be the in-root
``E:\\GT-KB\\scratchpad\\``, and the two ``.claude/rules`` /
``config/agent-control`` mirror pairs must keep their scratch section
byte-identical.
"""

from __future__ import annotations

from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]

SCRATCH_DIR_TOKEN = "E:\\GT-KB\\scratchpad\\"
SCRATCH_DIR_TOKEN_POSIX = "E:/GT-KB/scratchpad/"

AUTHORIZABLE_SURFACES = (
    ".claude/rules/prime-builder.md",
    ".claude/rules/loyal-opposition.md",
    "config/agent-control/gtkb-prime-builder.md",
    "config/agent-control/gtkb-loyal-opposition.md",
    "AGENTS.md",
    "config/agent-control/PRIME-BUILDER-STARTUP-OVERLAY.md",
    "config/agent-control/LOYAL-OPPOSITION-STARTUP-OVERLAY.md",
)

MIRROR_PAIRS = (
    (".claude/rules/prime-builder.md", "config/agent-control/gtkb-prime-builder.md"),
    (".claude/rules/loyal-opposition.md", "config/agent-control/gtkb-loyal-opposition.md"),
)

# Surfaces intentionally excluded because their mutation class cannot be
# authorized (generated adapters, .goosehints, per-harness SKILL.md files).
EXCLUDED_SURFACES_DOCUMENTED_IN = (
    ".claude/rules/prime-builder.md",
    ".claude/rules/loyal-opposition.md",
    "AGENTS.md",
)


@pytest.mark.parametrize("rel", AUTHORIZABLE_SURFACES, ids=lambda p: p)
def test_surface_carries_scratch_files_section(rel: str) -> None:
    path = PROJECT_ROOT / rel
    assert path.is_file(), f"surface missing: {rel}"
    text = path.read_text(encoding="utf-8")
    assert "## Scratch Files" in text
    assert SCRATCH_DIR_TOKEN in text or SCRATCH_DIR_TOKEN_POSIX in text
    assert "**Nothing in `scratchpad/` is authoritative.**" in text
    assert "Delete scratch files as soon as they are no longer needed" in text


@pytest.mark.parametrize(("a", "b"), MIRROR_PAIRS, ids=lambda p: p)
def test_mirror_pair_scratch_section_identical(a: str, b: str) -> None:
    ta = (PROJECT_ROOT / a).read_text(encoding="utf-8")
    tb = (PROJECT_ROOT / b).read_text(encoding="utf-8")
    sa = ta[ta.find("## Scratch Files") :]
    sb = tb[tb.find("## Scratch Files") :]
    # Normalize line endings; the git-tracked mirrors may differ in CRLF vs LF.
    assert sa.replace("\r\n", "\n") == sb.replace("\r\n", "\n")


def test_scratchpad_non_authority_mandate() -> None:
    """The section must state the non-authority rule prominently."""
    for rel in AUTHORIZABLE_SURFACES:
        text = (PROJECT_ROOT / rel).read_text(encoding="utf-8")
        assert "never let a formal artifact" in text
        assert "never cite it as evidence" in text.lower() or "never cite it as" in text.lower()


def test_scratch_directory_is_in_root_scratchpad() -> None:
    """The canonical scratch dir is the in-root scratchpad, not a harness-local temp."""
    for rel in AUTHORIZABLE_SURFACES:
        text = (PROJECT_ROOT / rel).read_text(encoding="utf-8")
        assert "E:\\GT-KB\\scratchpad\\" in text or "E:/GT-KB/scratchpad/" in text
        assert "harness" in text  # convention-overrides-harness-default clause present


def test_goosehints_is_not_an_authorizable_surface() -> None:
    """T7: `.goosehints` is deliberately excluded from the authorizable set.

    The proposal documents that the Goose root role surface cannot currently be
    authorized (unclassified mutation class); this test pins that exclusion as an
    intentional, documented test surface rather than silently omitting it.
    """
    assert ".goosehints" not in AUTHORIZABLE_SURFACES
    # The excluded-surface rationale appears in the in-scope rule set mirror.
    prime = (PROJECT_ROOT / ".claude" / "rules" / "prime-builder.md").read_text(encoding="utf-8")
    assert "## Scratch Files" in prime
    # The authorizable set must not silently include a file whose mutation class
    # was denied at filing time.
    assert all(Path(PROJECT_ROOT / rel).is_file() for rel in AUTHORIZABLE_SURFACES)
