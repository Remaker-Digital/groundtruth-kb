# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Tests for groundtruth_kb.bridge.notify.

Per ``bridge/gtkb-bridge-poller-p3-notify-2026-04-29-008.md`` GO conditions
+ -005/-007 LC1-LC15 lifecycle test contract:

- LC1, LC2: actionable top status persists across unchanged scans
- LC3: REVISED → GO transition moves notification Codex → Prime
- LC4: NEW/REVISED → VERIFIED clears Codex, no Prime notification written
- LC5: VERIFIED excluded for both recipients
- LC6: missing top file excluded
- LC9, LC10: deterministic; checkpoint-independent
- LC11-LC13: schema v2 (pending_actions[], top_status/top_file/index_line_number; no v1 from_*)
- Plus VERIFIED-suppression and routing tests from -003

Bridge imports are lazy per tests/test_bridge_import_hygiene rule.
"""

from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace


def _notify() -> SimpleNamespace:
    """Lazy-import bridge.notify + dependencies per test_bridge_import_hygiene rule."""
    from groundtruth_kb.bridge.detector import parse_index
    from groundtruth_kb.bridge.notify import (
        ACTIONABLE_STATUSES_FOR_CODEX,
        ACTIONABLE_STATUSES_FOR_PRIME,
        NOTIFY_SCHEMA_VERSION,
        ActionablePending,
        NotificationArtifact,
        clear_notification,
        compute_actionable_pending,
        read_notification,
        update_notification,
    )
    from groundtruth_kb.bridge.routing import BridgeAgent

    return SimpleNamespace(
        ACTIONABLE_STATUSES_FOR_CODEX=ACTIONABLE_STATUSES_FOR_CODEX,
        ACTIONABLE_STATUSES_FOR_PRIME=ACTIONABLE_STATUSES_FOR_PRIME,
        NOTIFY_SCHEMA_VERSION=NOTIFY_SCHEMA_VERSION,
        ActionablePending=ActionablePending,
        BridgeAgent=BridgeAgent,
        NotificationArtifact=NotificationArtifact,
        clear_notification=clear_notification,
        compute_actionable_pending=compute_actionable_pending,
        parse_index=parse_index,
        read_notification=read_notification,
        update_notification=update_notification,
    )


def _make_index_with_top_file(tmp_path: Path, doc_name: str, top_status: str, top_version: int = 2) -> tuple[str, Path]:
    """Build a minimal INDEX text + create the on-disk top file. Returns (text, project_root)."""
    project_root = tmp_path
    bridge_dir = project_root / "bridge"
    bridge_dir.mkdir(exist_ok=True)
    top_path = bridge_dir / f"{doc_name}-{top_version:03d}.md"
    top_path.write_text("# stub\n", encoding="utf-8")
    text = (
        f"Document: {doc_name}\n{top_status}: bridge/{doc_name}-{top_version:03d}.md\nNEW: bridge/{doc_name}-001.md\n"
    )
    if top_version != 1:
        # Also create the older NEW file for completeness.
        (bridge_dir / f"{doc_name}-001.md").write_text("# stub\n", encoding="utf-8")
    return text, project_root


# --- Tests for compute_actionable_pending ----------------------------------


def test_compute_pending_routes_new_revised_to_codex(tmp_path: Path) -> None:
    n = _notify()
    text, root = _make_index_with_top_file(tmp_path, "foo", "REVISED")
    parsed = n.parse_index(text)
    prime, codex = n.compute_actionable_pending(parsed, project_root=root)
    assert len(prime) == 0
    assert len(codex) == 1
    assert codex[0].top_status == "REVISED"
    assert codex[0].document_name == "foo"


def test_compute_pending_routes_go_no_go_to_prime(tmp_path: Path) -> None:
    n = _notify()
    text, root = _make_index_with_top_file(tmp_path, "foo", "GO")
    parsed = n.parse_index(text)
    prime, codex = n.compute_actionable_pending(parsed, project_root=root)
    assert len(prime) == 1
    assert prime[0].top_status == "GO"
    assert len(codex) == 0


def test_compute_pending_excludes_verified_for_both_recipients(tmp_path: Path) -> None:
    """LC5: VERIFIED is closure for both Prime and Codex."""
    n = _notify()
    text, root = _make_index_with_top_file(tmp_path, "foo", "VERIFIED")
    parsed = n.parse_index(text)
    prime, codex = n.compute_actionable_pending(parsed, project_root=root)
    assert len(prime) == 0
    assert len(codex) == 0


def test_compute_pending_excludes_documents_with_missing_top_file(
    tmp_path: Path,
) -> None:
    """LC6: missing top file → exclude from notifications."""
    n = _notify()
    project_root = tmp_path
    (project_root / "bridge").mkdir()
    # NOTE: we do NOT create foo-002.md
    text = "Document: foo\nGO: bridge/foo-002.md\nNEW: bridge/foo-001.md\n"
    parsed = n.parse_index(text)
    prime, codex = n.compute_actionable_pending(parsed, project_root=project_root)
    assert len(prime) == 0
    assert len(codex) == 0


def test_compute_pending_is_deterministic_across_repeated_calls(tmp_path: Path) -> None:
    """LC9: same parse_result + same on-disk → same output."""
    n = _notify()
    text, root = _make_index_with_top_file(tmp_path, "foo", "REVISED")
    parsed = n.parse_index(text)
    out1 = n.compute_actionable_pending(parsed, project_root=root)
    out2 = n.compute_actionable_pending(parsed, project_root=root)
    assert out1 == out2


def test_compute_pending_does_not_consult_checkpoint(tmp_path: Path) -> None:
    """LC10: function takes only parse_result + project_root; no checkpoint dep."""
    n = _notify()
    text, root = _make_index_with_top_file(tmp_path, "foo", "REVISED")
    parsed = n.parse_index(text)
    # Inject a fake checkpoint to prove it's ignored
    state_dir = tmp_path / ".gtkb-state" / "bridge-poller"
    state_dir.mkdir(parents=True)
    (state_dir / "checkpoint.json").write_text(
        '{"schema_version": 1, "captured_at": "2020", "documents": []}',
        encoding="utf-8",
    )
    prime, codex = n.compute_actionable_pending(parsed, project_root=root)
    assert len(codex) == 1


def test_compute_pending_preserves_index_order(tmp_path: Path) -> None:
    """Order in returned lists matches parse_result.documents order."""
    n = _notify()
    bridge_dir = tmp_path / "bridge"
    bridge_dir.mkdir()
    for name in ("alpha", "beta", "gamma"):
        (bridge_dir / f"{name}-002.md").write_text("# stub\n", encoding="utf-8")
        (bridge_dir / f"{name}-001.md").write_text("# stub\n", encoding="utf-8")
    text = (
        "Document: gamma\nGO: bridge/gamma-002.md\nNEW: bridge/gamma-001.md\n\n"
        "Document: alpha\nGO: bridge/alpha-002.md\nNEW: bridge/alpha-001.md\n\n"
        "Document: beta\nGO: bridge/beta-002.md\nNEW: bridge/beta-001.md\n"
    )
    parsed = n.parse_index(text)
    prime, _ = n.compute_actionable_pending(parsed, project_root=tmp_path)
    assert [item.document_name for item in prime] == ["gamma", "alpha", "beta"]


# --- Tests for update_notification + read_notification -----------------------


def test_update_notification_writes_v2_schema(tmp_path: Path) -> None:
    """LC11, LC12, LC13: v2 schema with pending_actions[]."""
    n = _notify()
    state_dir = tmp_path / "state"
    items = [
        n.ActionablePending(
            document_name="foo",
            top_status="REVISED",
            top_file="bridge/foo-002.md",
            index_line_number=8,
        )
    ]
    artifact = n.update_notification(state_dir, n.BridgeAgent.CODEX, items)
    assert artifact is not None
    json_path = state_dir / "notifications" / "pending-bridge-action-codex.json"
    payload = json.loads(json_path.read_text(encoding="utf-8"))
    assert payload["schema_version"] == 2
    assert "pending_actions" in payload
    assert "pending_transitions" not in payload
    assert payload["pending_actions"][0]["top_status"] == "REVISED"
    assert payload["pending_actions"][0]["top_file"] == "bridge/foo-002.md"
    assert payload["pending_actions"][0]["index_line_number"] == 8
    # No v1 fields:
    assert "from_status" not in payload["pending_actions"][0]
    assert "from_file" not in payload["pending_actions"][0]


def test_update_notification_removes_files_when_items_empty(tmp_path: Path) -> None:
    """File-absent represents no pending action."""
    n = _notify()
    state_dir = tmp_path / "state"
    items = [
        n.ActionablePending(
            document_name="foo",
            top_status="GO",
            top_file="bridge/foo-002.md",
            index_line_number=5,
        )
    ]
    n.update_notification(state_dir, n.BridgeAgent.PRIME, items)
    json_path = state_dir / "notifications" / "pending-bridge-action-prime.json"
    md_path = state_dir / "notifications" / "pending-bridge-action-prime.md"
    assert json_path.is_file()
    assert md_path.is_file()
    # Now clear:
    result = n.update_notification(state_dir, n.BridgeAgent.PRIME, [])
    assert result is None
    assert not json_path.is_file()
    assert not md_path.is_file()


def test_read_notification_round_trip(tmp_path: Path) -> None:
    n = _notify()
    state_dir = tmp_path / "state"
    items = [
        n.ActionablePending(
            document_name="foo",
            top_status="REVISED",
            top_file="bridge/foo-002.md",
            index_line_number=8,
        )
    ]
    n.update_notification(state_dir, n.BridgeAgent.CODEX, items, poller_run_id="test-run-001")
    artifact = n.read_notification(state_dir, n.BridgeAgent.CODEX)
    assert artifact is not None
    assert artifact.schema_version == 2
    assert artifact.recipient == "codex"
    assert artifact.poller_run_id == "test-run-001"
    assert len(artifact.pending_actions) == 1
    assert artifact.pending_actions[0].document_name == "foo"
    assert artifact.pending_actions[0].top_status == "REVISED"


def test_read_notification_returns_none_when_absent(tmp_path: Path) -> None:
    n = _notify()
    state_dir = tmp_path / "state"
    state_dir.mkdir()
    assert n.read_notification(state_dir, n.BridgeAgent.PRIME) is None


def test_clear_notification_removes_files(tmp_path: Path) -> None:
    n = _notify()
    state_dir = tmp_path / "state"
    items = [
        n.ActionablePending(
            document_name="foo",
            top_status="GO",
            top_file="bridge/foo-002.md",
            index_line_number=5,
        )
    ]
    n.update_notification(state_dir, n.BridgeAgent.PRIME, items)
    n.clear_notification(state_dir, n.BridgeAgent.PRIME)
    assert n.read_notification(state_dir, n.BridgeAgent.PRIME) is None


# --- LC1, LC2: persistence across unchanged scans ---------------------------


def test_revised_remains_in_codex_notification_across_unchanged_scans(
    tmp_path: Path,
) -> None:
    """LC1: REVISED entry persists across N unchanged scans."""
    n = _notify()
    text, root = _make_index_with_top_file(tmp_path, "foo", "REVISED")
    parsed = n.parse_index(text)

    state_dir = tmp_path / "state"
    # Scan 1
    _, codex_1 = n.compute_actionable_pending(parsed, project_root=root)
    n.update_notification(state_dir, n.BridgeAgent.CODEX, codex_1)
    artifact_1 = n.read_notification(state_dir, n.BridgeAgent.CODEX)
    assert artifact_1 is not None
    assert artifact_1.pending_actions[0].top_status == "REVISED"

    # Scan 2 (unchanged INDEX)
    _, codex_2 = n.compute_actionable_pending(parsed, project_root=root)
    n.update_notification(state_dir, n.BridgeAgent.CODEX, codex_2)
    artifact_2 = n.read_notification(state_dir, n.BridgeAgent.CODEX)
    assert artifact_2 is not None
    assert artifact_2.pending_actions[0].top_status == "REVISED"

    # Scan 3 (unchanged INDEX)
    _, codex_3 = n.compute_actionable_pending(parsed, project_root=root)
    n.update_notification(state_dir, n.BridgeAgent.CODEX, codex_3)
    artifact_3 = n.read_notification(state_dir, n.BridgeAgent.CODEX)
    assert artifact_3 is not None
    assert artifact_3.pending_actions[0].top_status == "REVISED"


def test_go_remains_in_prime_notification_across_unchanged_scans(tmp_path: Path) -> None:
    """LC2: GO entry persists across N unchanged scans."""
    n = _notify()
    text, root = _make_index_with_top_file(tmp_path, "foo", "GO")
    parsed = n.parse_index(text)

    state_dir = tmp_path / "state"
    for _ in range(3):
        prime, _ = n.compute_actionable_pending(parsed, project_root=root)
        n.update_notification(state_dir, n.BridgeAgent.PRIME, prime)
        artifact = n.read_notification(state_dir, n.BridgeAgent.PRIME)
        assert artifact is not None
        assert artifact.pending_actions[0].top_status == "GO"


# --- LC3, LC4: transition handling ----------------------------------------


def test_revised_to_go_transition_moves_notification_codex_to_prime(
    tmp_path: Path,
) -> None:
    """LC3: REVISED → GO transition removes Codex notif, writes Prime notif."""
    n = _notify()
    state_dir = tmp_path / "state"

    # Scan 1: top is REVISED
    text_1, root = _make_index_with_top_file(tmp_path, "foo", "REVISED", top_version=2)
    parsed_1 = n.parse_index(text_1)
    prime_1, codex_1 = n.compute_actionable_pending(parsed_1, project_root=root)
    n.update_notification(state_dir, n.BridgeAgent.PRIME, prime_1)
    n.update_notification(state_dir, n.BridgeAgent.CODEX, codex_1)
    assert n.read_notification(state_dir, n.BridgeAgent.CODEX) is not None
    assert n.read_notification(state_dir, n.BridgeAgent.PRIME) is None

    # Scan 2: a new GO was added; top is now GO at -003
    (root / "bridge" / "foo-003.md").write_text("# stub\n", encoding="utf-8")
    text_2 = "Document: foo\nGO: bridge/foo-003.md\nREVISED: bridge/foo-002.md\nNEW: bridge/foo-001.md\n"
    parsed_2 = n.parse_index(text_2)
    prime_2, codex_2 = n.compute_actionable_pending(parsed_2, project_root=root)
    n.update_notification(state_dir, n.BridgeAgent.PRIME, prime_2)
    n.update_notification(state_dir, n.BridgeAgent.CODEX, codex_2)
    assert n.read_notification(state_dir, n.BridgeAgent.CODEX) is None
    artifact_prime = n.read_notification(state_dir, n.BridgeAgent.PRIME)
    assert artifact_prime is not None
    assert artifact_prime.pending_actions[0].top_status == "GO"


def test_new_or_revised_to_verified_clears_codex_notification(tmp_path: Path) -> None:
    """LC4: NEW/REVISED → VERIFIED clears Codex; no Prime notification."""
    n = _notify()
    state_dir = tmp_path / "state"

    # Scan 1: top is REVISED
    text_1, root = _make_index_with_top_file(tmp_path, "foo", "REVISED", top_version=2)
    parsed_1 = n.parse_index(text_1)
    prime_1, codex_1 = n.compute_actionable_pending(parsed_1, project_root=root)
    n.update_notification(state_dir, n.BridgeAgent.CODEX, codex_1)
    assert n.read_notification(state_dir, n.BridgeAgent.CODEX) is not None

    # Scan 2: top transitions to VERIFIED
    (root / "bridge" / "foo-004.md").write_text("# stub\n", encoding="utf-8")
    text_2 = "Document: foo\nVERIFIED: bridge/foo-004.md\nREVISED: bridge/foo-002.md\nNEW: bridge/foo-001.md\n"
    parsed_2 = n.parse_index(text_2)
    prime_2, codex_2 = n.compute_actionable_pending(parsed_2, project_root=root)
    n.update_notification(state_dir, n.BridgeAgent.PRIME, prime_2)
    n.update_notification(state_dir, n.BridgeAgent.CODEX, codex_2)
    # VERIFIED → no notification for either:
    assert n.read_notification(state_dir, n.BridgeAgent.CODEX) is None
    assert n.read_notification(state_dir, n.BridgeAgent.PRIME) is None


# --- VERIFIED-suppression specific tests (from -003) -----------------------


def test_verified_top_status_does_not_appear_in_prime_notification(
    tmp_path: Path,
) -> None:
    n = _notify()
    text, root = _make_index_with_top_file(tmp_path, "foo", "VERIFIED")
    parsed = n.parse_index(text)
    state_dir = tmp_path / "state"
    prime, _ = n.compute_actionable_pending(parsed, project_root=root)
    n.update_notification(state_dir, n.BridgeAgent.PRIME, prime)
    assert n.read_notification(state_dir, n.BridgeAgent.PRIME) is None


def test_verified_top_status_does_not_appear_in_codex_notification(
    tmp_path: Path,
) -> None:
    n = _notify()
    text, root = _make_index_with_top_file(tmp_path, "foo", "VERIFIED")
    parsed = n.parse_index(text)
    state_dir = tmp_path / "state"
    _, codex = n.compute_actionable_pending(parsed, project_root=root)
    n.update_notification(state_dir, n.BridgeAgent.CODEX, codex)
    assert n.read_notification(state_dir, n.BridgeAgent.CODEX) is None


def test_only_go_no_go_appear_in_prime_notification(tmp_path: Path) -> None:
    n = _notify()
    bridge_dir = tmp_path / "bridge"
    bridge_dir.mkdir()
    for name in ("a", "b", "c", "d", "e"):
        for v in (1, 2):
            (bridge_dir / f"{name}-{v:03d}.md").write_text("# stub\n", encoding="utf-8")
    text = (
        "Document: a\nNEW: bridge/a-001.md\n\n"
        "Document: b\nREVISED: bridge/b-002.md\nNEW: bridge/b-001.md\n\n"
        "Document: c\nGO: bridge/c-002.md\nNEW: bridge/c-001.md\n\n"
        "Document: d\nNO-GO: bridge/d-002.md\nNEW: bridge/d-001.md\n\n"
        "Document: e\nVERIFIED: bridge/e-002.md\nNEW: bridge/e-001.md\n"
    )
    parsed = n.parse_index(text)
    prime, _ = n.compute_actionable_pending(parsed, project_root=tmp_path)
    statuses = {item.top_status for item in prime}
    assert statuses == {"GO", "NO-GO"}


def test_only_new_revised_appear_in_codex_notification(tmp_path: Path) -> None:
    n = _notify()
    bridge_dir = tmp_path / "bridge"
    bridge_dir.mkdir()
    for name in ("a", "b", "c", "d", "e"):
        for v in (1, 2):
            (bridge_dir / f"{name}-{v:03d}.md").write_text("# stub\n", encoding="utf-8")
    text = (
        "Document: a\nNEW: bridge/a-001.md\n\n"
        "Document: b\nREVISED: bridge/b-002.md\nNEW: bridge/b-001.md\n\n"
        "Document: c\nGO: bridge/c-002.md\nNEW: bridge/c-001.md\n\n"
        "Document: d\nNO-GO: bridge/d-002.md\nNEW: bridge/d-001.md\n\n"
        "Document: e\nVERIFIED: bridge/e-002.md\nNEW: bridge/e-001.md\n"
    )
    parsed = n.parse_index(text)
    _, codex = n.compute_actionable_pending(parsed, project_root=tmp_path)
    statuses = {item.top_status for item in codex}
    assert statuses == {"NEW", "REVISED"}


def test_no_actionable_documents_means_files_absent(tmp_path: Path) -> None:
    """LC8: zero actionable for a recipient → file absent."""
    n = _notify()
    state_dir = tmp_path / "state"
    n.update_notification(state_dir, n.BridgeAgent.PRIME, [])
    n.update_notification(state_dir, n.BridgeAgent.CODEX, [])
    assert n.read_notification(state_dir, n.BridgeAgent.PRIME) is None
    assert n.read_notification(state_dir, n.BridgeAgent.CODEX) is None
