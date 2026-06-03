"""Slice 3 windowed-keyword test — root + startup surfaces post-mirror-retirement.

Asserts that no live root/startup surface treats `harness-state/role-assignments.json`
as authoritative SOT (closing Codex NO-GO `-006 F1` on
`gtkb-role-rule-orthogonality-cleanup-claude-pb-switch`).

The 5 surfaces:

- `CLAUDE.md`
- `AGENTS.md`
- `scripts/session_self_initialization.py`
- `scripts/check_index_role_intent_sentinel.py`
- `scripts/single_harness_bridge_dispatcher.py`

Carve-outs (allowed mentions):

- Citations that frame `role-assignments.json` as `orphan`, `compat`,
  `compatibility`, `legacy`, or `not authoritative` are permitted — they are
  the orphan-marking the retirement requires.
- The string `harness-registry.json` MUST appear in each surface as the
  canonical role authority cite.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]

TARGETS = [
    "CLAUDE.md",
    "AGENTS.md",
    "scripts/session_self_initialization.py",
    "scripts/check_index_role_intent_sentinel.py",
    "scripts/single_harness_bridge_dispatcher.py",
]

MIRROR = "role-assignments.json"
REGISTRY = "harness-registry.json"

# Tokens that, when present in the same context window as a `MIRROR` mention,
# mark the mention as an orphan/compat citation (permitted).
COMPAT_TOKENS = [
    "orphan",
    "compat",
    "compatibility",
    "legacy",
    "not authoritative",
    "not the canonical",
    "superseded",
    "retired",
]

# Number of characters around a MIRROR hit to scan for COMPAT_TOKENS.
WINDOW = 400


def _read(relpath: str) -> str:
    path = ROOT / relpath
    return path.read_text(encoding="utf-8")


def _mirror_hits(content: str) -> list[tuple[int, str]]:
    """Return list of (offset, window_text) for each MIRROR mention."""
    hits: list[tuple[int, str]] = []
    for match in re.finditer(re.escape(MIRROR), content):
        start = max(0, match.start() - WINDOW)
        end = min(len(content), match.end() + WINDOW)
        hits.append((match.start(), content[start:end]))
    return hits


def _is_compat_marked(window_text: str) -> bool:
    lower = window_text.lower()
    return any(token in lower for token in COMPAT_TOKENS)


@pytest.mark.parametrize("relpath", TARGETS)
def test_target_cites_registry_as_role_authority(relpath: str) -> None:
    """Each of the 5 surfaces names `harness-registry.json` as role authority."""
    content = _read(relpath)
    assert REGISTRY in content, (
        f"{relpath} does not cite {REGISTRY!r} as the canonical role authority. "
        "Slice 3 requires every retained surface to name the registry."
    )


@pytest.mark.parametrize("relpath", TARGETS)
def test_target_no_unguarded_mirror_authority_cite(relpath: str) -> None:
    """No `role-assignments.json` mention may appear without an orphan/compat marker
    in its surrounding ±400-char window."""
    content = _read(relpath)
    hits = _mirror_hits(content)
    unguarded: list[int] = []
    for offset, window_text in hits:
        if not _is_compat_marked(window_text):
            unguarded.append(offset)
    assert not unguarded, (
        f"{relpath} has {len(unguarded)} unguarded {MIRROR!r} mention(s) at offsets "
        f"{unguarded}. Each mention must be accompanied by an orphan/compat marker "
        f"({', '.join(COMPAT_TOKENS)}) within ±{WINDOW} chars."
    )


def test_all_targets_present() -> None:
    """Sanity: all 5 target files exist at expected paths."""
    for relpath in TARGETS:
        assert (ROOT / relpath).is_file(), f"target missing: {relpath}"
