# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Tests for groundtruth_kb.bridge.routing.

Bridge imports are lazy per tests/test_bridge_import_hygiene.py rule.
"""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace


def _routing() -> SimpleNamespace:
    """Lazy-import bridge.routing and bridge.checkpoint."""
    from groundtruth_kb.bridge.checkpoint import Transition
    from groundtruth_kb.bridge.routing import (
        BridgeAgent,
        TransitionOutcome,
        route_transitions,
        synthesize_bootstrap_outcomes,
    )

    return SimpleNamespace(
        BridgeAgent=BridgeAgent,
        Transition=Transition,
        TransitionOutcome=TransitionOutcome,
        route_transitions=route_transitions,
        synthesize_bootstrap_outcomes=synthesize_bootstrap_outcomes,
    )


def _make_bridge_file(project_root: Path, name: str, version: int) -> str:
    bridge_dir = project_root / "bridge"
    bridge_dir.mkdir(exist_ok=True)
    rel_path = f"bridge/{name}-{version:03d}.md"
    (project_root / rel_path).write_text("# stub\n", encoding="utf-8")
    return rel_path


def test_routing_emits_routable_for_prime_authored_status_with_existing_file(
    tmp_path: Path,
) -> None:
    r = _routing()
    rel = _make_bridge_file(tmp_path, "foo", 1)
    transition = r.Transition(
        document_name="foo",
        from_status=None,
        from_file=None,
        to_status="NEW",
        to_file=rel,
    )
    [routed] = r.route_transitions((transition,), project_root=tmp_path)
    assert routed.outcome == r.TransitionOutcome.ROUTABLE
    assert routed.authored_by == r.BridgeAgent.PRIME
    assert routed.recipient == r.BridgeAgent.CODEX


def test_routing_emits_routable_for_codex_authored_status_with_existing_file(
    tmp_path: Path,
) -> None:
    r = _routing()
    rel = _make_bridge_file(tmp_path, "foo", 2)
    transition = r.Transition(
        document_name="foo",
        from_status="NEW",
        from_file="bridge/foo-001.md",
        to_status="GO",
        to_file=rel,
    )
    [routed] = r.route_transitions((transition,), project_root=tmp_path)
    assert routed.outcome == r.TransitionOutcome.ROUTABLE
    assert routed.authored_by == r.BridgeAgent.CODEX
    assert routed.recipient == r.BridgeAgent.PRIME


def test_routing_emits_unroutable_file_missing_when_top_file_absent(
    tmp_path: Path,
) -> None:
    r = _routing()
    transition = r.Transition(
        document_name="foo",
        from_status=None,
        from_file=None,
        to_status="NEW",
        to_file="bridge/foo-001.md",
    )
    [routed] = r.route_transitions((transition,), project_root=tmp_path)
    assert routed.outcome == r.TransitionOutcome.UNROUTABLE_FILE_MISSING
    assert routed.recipient is None
    assert "missing" in routed.detail.lower()


def test_routing_skips_routing_for_unknown_status(tmp_path: Path) -> None:
    r = _routing()
    rel = _make_bridge_file(tmp_path, "foo", 1)
    transition = r.Transition(
        document_name="foo",
        from_status=None,
        from_file=None,
        to_status="UNKNOWN_STATUS",
        to_file=rel,
    )
    [routed] = r.route_transitions((transition,), project_root=tmp_path)
    assert routed.outcome == r.TransitionOutcome.UNROUTABLE_FILE_MISSING
    assert routed.recipient is None
    assert "Unknown status" in routed.detail


def test_routing_handles_mixed_outcomes_in_one_call(tmp_path: Path) -> None:
    r = _routing()
    rel_existing = _make_bridge_file(tmp_path, "foo", 1)
    transitions = (
        r.Transition(
            document_name="foo",
            from_status=None,
            from_file=None,
            to_status="NEW",
            to_file=rel_existing,
        ),
        r.Transition(
            document_name="bar",
            from_status=None,
            from_file=None,
            to_status="REVISED",
            to_file="bridge/bar-001.md",
        ),
    )
    routed = r.route_transitions(transitions, project_root=tmp_path)
    assert len(routed) == 2
    assert routed[0].outcome == r.TransitionOutcome.ROUTABLE
    assert routed[1].outcome == r.TransitionOutcome.UNROUTABLE_FILE_MISSING


def test_synthesize_bootstrap_outcomes_returns_empty() -> None:
    r = _routing()
    assert r.synthesize_bootstrap_outcomes(document_count=42) == ()
