# (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Structural tests for Slice C — role-neutral startup index + role overlays.

GTKB-STARTUP-REFRACTOR-001 Slice C (WI-4271), advisory findings F4 (duplicated
startup content) and F7 (no compact role-neutral startup load list). Slice C
creates a role-neutral ``SESSION-STARTUP-INDEX.md`` plus compact Prime Builder
and Loyal Opposition overlays under ``config/agent-control/``, and repoints the
protected narrative (``CLAUDE.md``, ``AGENTS.md``) to reference the index.

These tests pin the load-bearing contract: the index exists and declares the
canonical load order, both role overlays exist, the index references the
overlays + the Slice A control-map, and both protected narrative files reference
the index.

Authority: ``bridge/gtkb-startup-refractor-slice-c-startup-index-overlays-002.md``
(GO); ``GOV-SESSION-SELF-INITIALIZATION-001``; ``DCL-SESSION-STARTUP-TOKEN-BUDGET-001``.
"""

from __future__ import annotations

from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
_AGENT_CONTROL = _ROOT / "config" / "agent-control"
_INDEX = _AGENT_CONTROL / "SESSION-STARTUP-INDEX.md"
_PB_OVERLAY = _AGENT_CONTROL / "PRIME-BUILDER-STARTUP-OVERLAY.md"
_LO_OVERLAY = _AGENT_CONTROL / "LOYAL-OPPOSITION-STARTUP-OVERLAY.md"
_CONTROL_MAP = _AGENT_CONTROL / "SESSION-STARTUP-CONTROL-MAP.md"
_CLAUDE_MD = _ROOT / "CLAUDE.md"
_AGENTS_MD = _ROOT / "AGENTS.md"

# The canonical load-order steps the index must declare, IN ORDER (advisory F7).
_LOAD_ORDER_TOKENS = (
    "Role record",
    "Role overlay",
    "Canonical terminology",
    "File bridge",
    "Dashboard / backlog summary",
    "Selected task",
)


def _read(path: Path) -> str:
    assert path.is_file(), f"required Slice C artifact missing: {path}"
    return path.read_text(encoding="utf-8")


def test_index_exists_and_declares_load_order() -> None:
    text = _read(_INDEX)
    assert "Canonical Startup Load Order" in text
    missing = [t for t in _LOAD_ORDER_TOKENS if t not in text]
    assert not missing, f"SESSION-STARTUP-INDEX.md omits load-order steps: {missing}"
    # The steps must appear in the canonical order, not merely be present (F3).
    positions = [text.index(t) for t in _LOAD_ORDER_TOKENS]
    assert positions == sorted(positions), f"load-order steps out of canonical order: {_LOAD_ORDER_TOKENS}"


def test_role_overlays_exist_with_headers() -> None:
    pb = _read(_PB_OVERLAY)
    lo = _read(_LO_OVERLAY)
    assert "Prime Builder Startup Overlay" in pb
    assert "Loyal Opposition Startup Overlay" in lo


def test_index_references_overlays_and_control_map() -> None:
    text = _read(_INDEX)
    assert "PRIME-BUILDER-STARTUP-OVERLAY.md" in text
    assert "LOYAL-OPPOSITION-STARTUP-OVERLAY.md" in text
    assert "SESSION-STARTUP-CONTROL-MAP.md" in text
    # Slice A control-map exists (the index points at a real surface).
    assert _CONTROL_MAP.is_file(), "Slice A control-map must exist for the index to reference"


def test_protected_narrative_references_index() -> None:
    assert "SESSION-STARTUP-INDEX.md" in _read(_CLAUDE_MD), "CLAUDE.md must reference the startup index"
    assert "SESSION-STARTUP-INDEX.md" in _read(_AGENTS_MD), "AGENTS.md must reference the startup index"
