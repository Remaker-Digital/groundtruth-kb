"""Slice 6: MemBase attribution follows the resolved interactive session role.

bridge/gtkb-interactive-session-role-override-slice-6-attribution-role-awareness-001.md
(Codex GO at -002).

Covers:
- A declared interactive session role overrides the durable role for the
  ``changed_by`` LABEL (ADR-INTERACTIVE-SESSION-ROLE-OVERRIDE-001 Decision 1).
- The override is layered on the fail-closed durable resolution: no durable role
  -> RuntimeError BEFORE any marker can affect the result (the
  gtkb-kb-attribution-harness-aware mis-attribution invariant is preserved).
- The override is interactive-only (headless dispatch keeps durable attribution).
- The override layer is fail-soft (resolver error -> keep durable label), and it
  never masks a durable-attribution failure.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import scripts._kb_attribution as kb  # noqa: E402

_LO = "loyal-opposition"
_PB = "prime-builder"


# ---------------------------------------------------------------------------
# resolve_changed_by composition: durable (fail-closed) + marker label override.
# ---------------------------------------------------------------------------


@pytest.fixture
def stub_harness(monkeypatch: pytest.MonkeyPatch) -> None:
    """Stub the harness-id lookup so resolve_changed_by reaches the role step.

    Tests set _role_for_harness_id and _session_role_override per case.
    """
    monkeypatch.setattr(kb, "_harness_id_for_name", lambda name: "B")


def test_attribution_lo_marker_overrides_durable_pb(monkeypatch: pytest.MonkeyPatch, stub_harness: None) -> None:
    monkeypatch.setattr(kb, "_role_for_harness_id", lambda hid: _PB)  # durable PB
    monkeypatch.setattr(kb, "_session_role_override", lambda name: _LO)  # declared LO
    assert kb.resolve_changed_by(harness_name="claude") == "loyal-opposition/claude"


def test_attribution_pb_marker_overrides_durable_lo(monkeypatch: pytest.MonkeyPatch, stub_harness: None) -> None:
    monkeypatch.setattr(kb, "_role_for_harness_id", lambda hid: _LO)  # durable LO
    monkeypatch.setattr(kb, "_session_role_override", lambda name: _PB)  # declared PB
    assert kb.resolve_changed_by(harness_name="codex") == "prime-builder/codex"


def test_attribution_no_marker_uses_durable(monkeypatch: pytest.MonkeyPatch, stub_harness: None) -> None:
    monkeypatch.setattr(kb, "_role_for_harness_id", lambda hid: _PB)
    monkeypatch.setattr(kb, "_session_role_override", lambda name: None)  # no marker
    assert kb.resolve_changed_by(harness_name="claude") == "prime-builder/claude"


def test_attribution_failclosed_when_no_durable_role(monkeypatch: pytest.MonkeyPatch, stub_harness: None) -> None:
    """No durable role -> RuntimeError BEFORE any marker override can apply."""
    monkeypatch.setattr(kb, "_role_for_harness_id", lambda hid: None)  # no durable role

    called = {"override": False}

    def _tracking_override(name: str) -> str | None:
        called["override"] = True
        return _LO

    monkeypatch.setattr(kb, "_session_role_override", _tracking_override)
    with pytest.raises(RuntimeError):
        kb.resolve_changed_by(harness_name="claude")
    assert called["override"] is False, "override ran before the fail-closed durable check"


# ---------------------------------------------------------------------------
# _session_role_override behavior (resolver + headless guard + fail-soft).
# ---------------------------------------------------------------------------


def _patch_resolver(monkeypatch: pytest.MonkeyPatch, result: object) -> None:
    import scripts.session_role_resolution as srr

    if isinstance(result, Exception):

        def _boom(*a: object, **k: object) -> tuple[str, str]:
            raise result

        monkeypatch.setattr(srr, "resolve_interactive_session_role", _boom)
    else:
        monkeypatch.setattr(srr, "resolve_interactive_session_role", lambda *a, **k: result)


@pytest.mark.parametrize("source", ["marker", "marker_session_id_unverified"])
def test_override_returns_role_for_marker_sources(monkeypatch: pytest.MonkeyPatch, source: str) -> None:
    monkeypatch.delenv("GTKB_BRIDGE_POLLER_RUN_ID", raising=False)
    _patch_resolver(monkeypatch, (_LO, source))
    assert kb._session_role_override("claude") == _LO


@pytest.mark.parametrize(
    "source",
    ["durable_marker_absent", "durable_marker_invalid_role", "durable_marker_stale_session"],
)
def test_override_returns_none_for_durable_sources(monkeypatch: pytest.MonkeyPatch, source: str) -> None:
    monkeypatch.delenv("GTKB_BRIDGE_POLLER_RUN_ID", raising=False)
    _patch_resolver(monkeypatch, (_PB, source))
    assert kb._session_role_override("claude") is None


def test_override_none_under_headless_dispatch(monkeypatch: pytest.MonkeyPatch) -> None:
    """Headless dispatch (env-var present) -> no override even with a marker."""
    monkeypatch.setenv("GTKB_BRIDGE_POLLER_RUN_ID", "run-123")
    # Resolver would return a marker role, but the headless guard returns first.
    called = {"resolver": False}

    import scripts.session_role_resolution as srr

    def _should_not_run(*a: object, **k: object) -> tuple[str, str]:
        called["resolver"] = True
        return (_LO, "marker")

    monkeypatch.setattr(srr, "resolve_interactive_session_role", _should_not_run)
    assert kb._session_role_override("claude") is None
    assert called["resolver"] is False, "resolver consulted under headless dispatch"


def test_override_fail_soft_on_resolver_error(monkeypatch: pytest.MonkeyPatch) -> None:
    """A resolver error returns None (keep durable label), never raises."""
    monkeypatch.delenv("GTKB_BRIDGE_POLLER_RUN_ID", raising=False)
    _patch_resolver(monkeypatch, RuntimeError("resolver unavailable"))
    assert kb._session_role_override("claude") is None


def test_headless_attribution_keeps_durable(monkeypatch: pytest.MonkeyPatch, stub_harness: None) -> None:
    """End-to-end: under headless dispatch, resolve_changed_by keeps the durable role."""
    monkeypatch.setenv("GTKB_BRIDGE_POLLER_RUN_ID", "run-123")
    monkeypatch.setattr(kb, "_role_for_harness_id", lambda hid: _PB)  # durable PB

    import scripts.session_role_resolution as srr

    # Even if a marker would say LO, the headless guard inside _session_role_override
    # suppresses it, so attribution stays durable PB.
    monkeypatch.setattr(srr, "resolve_interactive_session_role", lambda *a, **k: (_LO, "marker"))
    assert kb.resolve_changed_by(harness_name="claude") == "prime-builder/claude"
