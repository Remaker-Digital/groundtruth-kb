# (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Regression tests for Antigravity active role startup overlay integration.

Cites Specifications:
- GOV-SESSION-SELF-INITIALIZATION-001: startup instructions load from live authoritative sources.
- DCL-SESSION-STARTUP-TOKEN-BUDGET-001: Antigravity optimized low-overhead startup path.
- GOV-FILE-BRIDGE-AUTHORITY-001: bridge state is canonical and status writes require role checks.
- DCL-SESSION-ROLE-RESOLUTION-001: durable-dispatch versus transcript-interactive role-authority separation.
- GOV-SESSION-ROLE-AUTHORITY-001: durable role assignment is distinct from session-stated role authority.
- ADR-INTERACTIVE-SESSION-ROLE-OVERRIDE-001: interactive role override constraints.
- ADR-ROLE-AUTHORITY-INTERACTIVE-PERSISTENCE-001: transcript-defined interactive role persistence.
- DCL-INTERACTIVE-SESSION-ROLE-PERSISTENCE-001: transcript role resolution rules.
"""

from __future__ import annotations

from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
_AGENTS_MD = _ROOT / "AGENTS.md"
_STARTUP_INDEX = _ROOT / "config" / "agent-control" / "SESSION-STARTUP-INDEX.md"


def _read(path: Path) -> str:
    assert path.is_file(), f"Required file missing: {path}"
    return path.read_text(encoding="utf-8")


def test_antigravity_startup_overlay_directive_in_agents_md() -> None:
    text = _read(_AGENTS_MD)
    # Verify Antigravity optimized startup directive exists
    assert "Antigravity harness (ID C)" in text
    assert "Startup Optimization Directive" in text

    # Assert active role overlay loading requirement
    assert "load the active role overlay file" in text
    assert "PRIME-BUILDER-STARTUP-OVERLAY.md" in text
    assert "LOYAL-OPPOSITION-STARTUP-OVERLAY.md" in text


def test_antigravity_startup_overrides_in_index() -> None:
    text = _read(_STARTUP_INDEX)
    assert "Antigravity (Harness ID C) Overrides" in text

    # Assert role overlay selection is preserved while skipping rules/logs reads
    assert "Load Role Overlay" in text
    assert "Skip Rules/Logs Reads" in text
    assert "Omit Heavy Subprocesses" in text


def test_bridge_status_role_boundary_check_in_agents_md() -> None:
    text = _read(_AGENTS_MD)

    # Assert first-line eligibility check is declared
    assert "First-Line Role Eligibility Check" in text
    assert "Prime Builder is strictly prohibited from authoring Loyal Opposition status tokens" in text
    assert "Loyal Opposition is strictly prohibited from authoring Prime Builder status tokens" in text


def test_specification_citations_in_changed_surfaces() -> None:
    agents_text = _read(_AGENTS_MD)
    index_text = _read(_STARTUP_INDEX)

    # Check that key specifications are cited
    assert "GOV-SESSION-SELF-INITIALIZATION-001" in index_text
    assert "DCL-SESSION-STARTUP-TOKEN-BUDGET-001" in index_text
    assert "GOV-FILE-BRIDGE-AUTHORITY-001" in agents_text
