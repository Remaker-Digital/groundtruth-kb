# (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Tests for scripts/cursor_harness.py Loyal Opposition skill-route resolution (WI-4872).

The harness-registry Cursor invocation surfaces pass the canonical LO route keys
'bridge-review' / 'verification', which have no SKILL.md. These tests assert the
alias resolution maps them to the real skill contracts so headless LO dispatch
loads a contract instead of failing closed, while genuinely unknown routes still
fail closed.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[2]
_HARNESS_PATH = _REPO_ROOT / "scripts" / "cursor_harness.py"


def _load_harness():
    spec = importlib.util.spec_from_file_location("cursor_harness_test", _HARNESS_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_skill_route_alias_bridge_review_resolves() -> None:
    """WI-4872: 'bridge-review' aliases to the real proposal-review skill contract."""
    harness = _load_harness()
    content = harness._skill_system_prompt("bridge-review")
    assert content is not None
    assert "proposal-review" in content


def test_skill_route_alias_verification_resolves() -> None:
    """WI-4872: 'verification' aliases to the real verify skill contract."""
    harness = _load_harness()
    content = harness._skill_system_prompt("verification")
    assert content is not None
    assert "verify" in content.lower()


def test_skill_route_non_aliased_resolves() -> None:
    """A real skill name resolves directly (no alias needed)."""
    harness = _load_harness()
    content = harness._skill_system_prompt("proposal-review")
    assert content is not None


def test_skill_route_unknown_still_raises() -> None:
    """Genuinely unknown routes still fail closed (CursorHarnessError preserved)."""
    harness = _load_harness()
    with pytest.raises(harness.CursorHarnessError, match="unknown skill route"):
        harness._skill_system_prompt("definitely-not-a-skill")


def test_skill_route_none_returns_none() -> None:
    """No skill route yields no system prompt."""
    harness = _load_harness()
    assert harness._skill_system_prompt(None) is None
