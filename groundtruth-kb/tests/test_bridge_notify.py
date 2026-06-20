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
    from groundtruth_kb.bridge.disposition import (
        LOYAL_OPPOSITION_ACTIONABLE_STATUSES,
        LOYAL_OPPOSITION_ROLE,
        PRIME_ACTIONABLE_STATUSES,
        PRIME_BUILDER_ROLE,
        BridgeDisposition,
        dispatchable_for_status,
        disposition_for_status,
    )
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
        BridgeDisposition=BridgeDisposition,
        LOYAL_OPPOSITION_ACTIONABLE_STATUSES=LOYAL_OPPOSITION_ACTIONABLE_STATUSES,
        LOYAL_OPPOSITION_ROLE=LOYAL_OPPOSITION_ROLE,
        NOTIFY_SCHEMA_VERSION=NOTIFY_SCHEMA_VERSION,
        PRIME_ACTIONABLE_STATUSES=PRIME_ACTIONABLE_STATUSES,
        PRIME_BUILDER_ROLE=PRIME_BUILDER_ROLE,
        ActionablePending=ActionablePending,
        BridgeAgent=BridgeAgent,
        NotificationArtifact=NotificationArtifact,
        clear_notification=clear_notification,
        compute_actionable_pending=compute_actionable_pending,
        dispatchable_for_status=dispatchable_for_status,
        disposition_for_status=disposition_for_status,
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


def test_shared_disposition_matrix_routes_statuses_by_role() -> None:
    n = _notify()

    assert n.disposition_for_status("NEW", n.LOYAL_OPPOSITION_ROLE).actionable is True
    assert n.disposition_for_status("REVISED", n.LOYAL_OPPOSITION_ROLE).next_action == "review"
    assert n.disposition_for_status("GO", n.PRIME_BUILDER_ROLE).actionable is True
    assert n.disposition_for_status("NO-GO", n.PRIME_BUILDER_ROLE).next_action == "revise"


def test_shared_disposition_matrix_advisory_is_manual_prime_only() -> None:
    n = _notify()

    prime = n.disposition_for_status("ADVISORY", n.PRIME_BUILDER_ROLE)
    loyal_opposition = n.disposition_for_status("ADVISORY", n.LOYAL_OPPOSITION_ROLE)

    assert prime.actionable is True
    assert prime.dispatchable is False
    assert prime.owner_visible is True
    assert prime.reason_code == "prime_advisory_disposition"
    assert loyal_opposition.actionable is False
    assert loyal_opposition.reason_code == "wrong_role_prime_advisory"


def test_shared_disposition_matrix_wrong_role_reason_codes() -> None:
    n = _notify()

    assert n.disposition_for_status("NEW", n.PRIME_BUILDER_ROLE).reason_code == "wrong_role_lo_review"
    assert n.disposition_for_status("GO", n.LOYAL_OPPOSITION_ROLE).reason_code == "wrong_role_prime_continuation"


def test_notify_actionable_status_sets_follow_shared_disposition_matrix() -> None:
    n = _notify()

    assert n.ACTIONABLE_STATUSES_FOR_PRIME == n.PRIME_ACTIONABLE_STATUSES
    assert n.ACTIONABLE_STATUSES_FOR_CODEX == n.LOYAL_OPPOSITION_ACTIONABLE_STATUSES


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


def test_compute_pending_excludes_withdrawn_for_both_recipients(tmp_path: Path) -> None:
    """WITHDRAWN, like VERIFIED, is closure for both Prime and Codex. Per
    WI-3276 / Layer-0 fix at gtkb-canonical-bridge-parser-withdrawn-status-handling.
    """
    n = _notify()
    text, root = _make_index_with_top_file(tmp_path, "foo", "WITHDRAWN")
    parsed = n.parse_index(text)
    prime, codex = n.compute_actionable_pending(parsed, project_root=root)
    assert len(prime) == 0, f"WITHDRAWN must not be actionable for Prime; got {prime}"
    assert len(codex) == 0, f"WITHDRAWN must not be actionable for Codex; got {codex}"


def test_deferred_top_status_not_actionable_for_either_role(tmp_path: Path) -> None:
    """DEFERRED is a deliberate bridge parking state, not role-actionable work."""
    n = _notify()
    text, root = _make_index_with_top_file(tmp_path, "foo", "DEFERRED")
    parsed = n.parse_index(text)
    prime, codex = n.compute_actionable_pending(parsed, project_root=root)
    assert len(prime) == 0, f"DEFERRED must not be actionable for Prime; got {prime}"
    assert len(codex) == 0, f"DEFERRED must not be actionable for Codex; got {codex}"


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


# --- WI-3442: scoping-terminal-with-successor classifier fix ----------------
# Per bridge/gtkb-axis-2-scoping-terminal-classifier-fix-002 (GO).


def test_scoping_terminal_with_successor_is_excluded(tmp_path: Path) -> None:
    """A scoping thread at GO is excluded when its successor (slug without
    `-scoping` suffix) exists in INDEX, regardless of the successor's status."""
    n = _notify()
    bridge_dir = tmp_path / "bridge"
    bridge_dir.mkdir()
    (bridge_dir / "gtkb-example-scoping-002.md").write_text("# stub\n", encoding="utf-8")
    (bridge_dir / "gtkb-example-scoping-001.md").write_text("# stub\n", encoding="utf-8")
    (bridge_dir / "gtkb-example-002.md").write_text("# stub\n", encoding="utf-8")
    (bridge_dir / "gtkb-example-001.md").write_text("# stub\n", encoding="utf-8")
    text = (
        "Document: gtkb-example-scoping\n"
        "GO: bridge/gtkb-example-scoping-002.md\n"
        "NEW: bridge/gtkb-example-scoping-001.md\n\n"
        "Document: gtkb-example\n"
        "VERIFIED: bridge/gtkb-example-002.md\n"
        "NEW: bridge/gtkb-example-001.md\n"
    )
    parsed = n.parse_index(text)
    prime, codex = n.compute_actionable_pending(parsed, project_root=tmp_path)
    prime_names = {item.document_name for item in prime}
    codex_names = {item.document_name for item in codex}
    assert "gtkb-example-scoping" not in prime_names, (
        f"scoping-terminal must be suppressed from Prime when successor exists; got {prime_names}"
    )
    assert "gtkb-example-scoping" not in codex_names, (
        f"scoping-terminal must be suppressed from Codex when successor exists; got {codex_names}"
    )


def test_scoping_terminal_without_successor_is_included(tmp_path: Path) -> None:
    """A scoping thread at GO is NOT suppressed when no successor exists; the
    classifier remains conservative (false-negative) when the bridge protocol's
    scoping → successor pattern is not yet complete."""
    n = _notify()
    text, root = _make_index_with_top_file(tmp_path, "gtkb-example-scoping", "GO")
    parsed = n.parse_index(text)
    prime, codex = n.compute_actionable_pending(parsed, project_root=root)
    prime_names = {item.document_name for item in prime}
    assert "gtkb-example-scoping" in prime_names, (
        f"scoping thread without successor must remain Prime-actionable; got {prime_names}"
    )
    assert len(codex) == 0


def test_scoping_helper_classification_safety(tmp_path: Path) -> None:
    """Unit test of `_scoping_terminal_with_successor` edge cases.

    Per WI-3442 design: only true scoping-with-successor combinations should
    be suppressed. Empty-successor slugs (`-scoping` alone) and non-scoping
    slugs are pass-through.
    """
    from groundtruth_kb.bridge.notify import _scoping_terminal_with_successor

    n = _notify()

    def parse_with_docs(*names: str) -> object:
        bridge_dir = tmp_path / "bridge"
        if not bridge_dir.exists():
            bridge_dir.mkdir()
        parts = []
        for nm in names:
            top = bridge_dir / f"{nm}-001.md"
            if not top.exists():
                top.write_text("# stub\n", encoding="utf-8")
            parts.append(f"Document: {nm}\nNEW: bridge/{nm}-001.md\n")
        return n.parse_index("\n".join(parts))

    pr_with_both = parse_with_docs("foo-scoping", "foo")
    pr_scoping_only = parse_with_docs("foo-scoping")
    pr_non_scoping = parse_with_docs("foo")
    pr_empty_successor = parse_with_docs("-scoping")
    pr_unrelated = parse_with_docs("foo-scoping", "bar")

    assert _scoping_terminal_with_successor("foo-scoping", pr_with_both) is True
    assert _scoping_terminal_with_successor("foo-scoping", pr_scoping_only) is False
    assert _scoping_terminal_with_successor("foo", pr_non_scoping) is False
    assert _scoping_terminal_with_successor("-scoping", pr_empty_successor) is False
    assert _scoping_terminal_with_successor("foo-scoping", pr_unrelated) is False


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
    # Schema v3 per smart-poller-kind-aware-routing-2026-04-30-009 REVISED-4.
    assert payload["schema_version"] == 3
    assert "pending_actions" in payload
    assert "pending_transitions" not in payload
    assert payload["pending_actions"][0]["top_status"] == "REVISED"
    assert payload["pending_actions"][0]["top_file"] == "bridge/foo-002.md"
    assert payload["pending_actions"][0]["index_line_number"] == 8
    # Schema-v3 fields are present and serialized.
    assert "dispatchable" in payload["pending_actions"][0]
    assert "classification" in payload["pending_actions"][0]
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
    # Schema v3 per smart-poller-kind-aware-routing-2026-04-30-009 REVISED-4.
    assert artifact.schema_version == 3
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


# ===========================================================================
# Smart-poller kind-aware routing (per smart-poller-kind-aware-routing-2026-04-30
# bridge thread; GO at -010). Tests below cover:
# - _derive_dispatchable decision tree (status-aware)
# - _extract_bridge_kind frontmatter parser
# - find_operative_prime_version version traversal
# - classify_document_dispatchability (kind tokens)
# - compute_actionable_pending end-to-end with real bridge chains
# - schema v3 markdown rendering ((terminal) prefix scoped to GO+terminal)
# - GTKB_NOTIFY_KIND_AWARE_ROUTING feature flag
# ===========================================================================


def _kind_aware() -> SimpleNamespace:
    """Lazy-import kind-aware routing helpers."""
    from groundtruth_kb.bridge.detector import BridgeDocument, BridgeStatus, BridgeVersion
    from groundtruth_kb.bridge.notify import (
        KIND_AWARE_ROUTING_ENV_VAR,
        _derive_dispatchable,
        _extract_bridge_kind,
        _kind_aware_routing_enabled,
        classify_document_dispatchability,
        find_operative_prime_version,
    )

    return SimpleNamespace(
        BridgeDocument=BridgeDocument,
        BridgeStatus=BridgeStatus,
        BridgeVersion=BridgeVersion,
        KIND_AWARE_ROUTING_ENV_VAR=KIND_AWARE_ROUTING_ENV_VAR,
        _derive_dispatchable=_derive_dispatchable,
        _extract_bridge_kind=_extract_bridge_kind,
        _kind_aware_routing_enabled=_kind_aware_routing_enabled,
        classify_document_dispatchability=classify_document_dispatchability,
        find_operative_prime_version=find_operative_prime_version,
    )


def _make_doc(name: str, status_file_pairs: list[tuple[str, str]]) -> object:
    """Build a BridgeDocument with versions in most-recent-first order.

    status_file_pairs: list of (status_str, file_path) — order is the order
    they appear in INDEX (most-recent first).
    """
    k = _kind_aware()
    versions = tuple(
        k.BridgeVersion(
            status=k.BridgeStatus(status),
            file_path=path,
            line_number=10 + i,
        )
        for i, (status, path) in enumerate(status_file_pairs)
    )
    return k.BridgeDocument(name=name, versions=versions, line_number=9)


def _seed_bridge_file(project_root: Path, file_path: str, content: str) -> None:
    """Write a bridge file under project_root with the given content."""
    full = project_root / file_path
    full.parent.mkdir(parents=True, exist_ok=True)
    full.write_text(content, encoding="utf-8")


# --- _derive_dispatchable decision tree ----------------------------------


def test_derive_dispatchable_NEW_returns_True_for_terminal_kind() -> None:
    k = _kind_aware()
    assert k._derive_dispatchable("NEW", "terminal") is True


def test_derive_dispatchable_REVISED_returns_True_for_terminal_kind() -> None:
    k = _kind_aware()
    assert k._derive_dispatchable("REVISED", "terminal") is True


def test_derive_dispatchable_NO_GO_returns_True_for_terminal_kind() -> None:
    k = _kind_aware()
    assert k._derive_dispatchable("NO-GO", "terminal") is True


def test_derive_dispatchable_NO_GO_returns_True_for_dispatchable_kind() -> None:
    k = _kind_aware()
    assert k._derive_dispatchable("NO-GO", "dispatchable") is True


def test_derive_dispatchable_GO_returns_False_for_terminal_kind() -> None:
    k = _kind_aware()
    assert k._derive_dispatchable("GO", "terminal") is False


def test_derive_dispatchable_GO_returns_True_for_dispatchable_kind() -> None:
    k = _kind_aware()
    assert k._derive_dispatchable("GO", "dispatchable") is True


def test_derive_dispatchable_GO_returns_True_for_ambiguous_kind() -> None:
    k = _kind_aware()
    assert k._derive_dispatchable("GO", "ambiguous") is True


def test_derive_dispatchable_VERIFIED_returns_False() -> None:
    k = _kind_aware()
    assert k._derive_dispatchable("VERIFIED", "dispatchable") is False
    assert k._derive_dispatchable("VERIFIED", "terminal") is False


def test_derive_dispatchable_unknown_status_returns_False() -> None:
    k = _kind_aware()
    assert k._derive_dispatchable("UNKNOWN", "dispatchable") is False


# --- _extract_bridge_kind frontmatter parser -------------------------------


def test_extract_bridge_kind_extracts_value() -> None:
    k = _kind_aware()
    header = "Some preamble\nbridge_kind: implementation_proposal\nMore text"
    assert k._extract_bridge_kind(header) == "implementation_proposal"


def test_extract_bridge_kind_returns_None_when_missing() -> None:
    k = _kind_aware()
    assert k._extract_bridge_kind("# Header\n\nNo bridge_kind line here") is None


def test_extract_bridge_kind_extracts_kebab_variant() -> None:
    k = _kind_aware()
    assert k._extract_bridge_kind("bridge_kind: post-implementation-report") == "post-implementation-report"


# --- find_operative_prime_version version traversal -----------------------


def test_find_operative_prime_version_returns_latest_REVISED() -> None:
    k = _kind_aware()
    doc = _make_doc(
        "foo",
        [
            ("GO", "bridge/foo-004.md"),
            ("REVISED", "bridge/foo-003.md"),
            ("NO-GO", "bridge/foo-002.md"),
            ("NEW", "bridge/foo-001.md"),
        ],
    )
    operative = k.find_operative_prime_version(doc)
    assert operative is not None
    assert operative.file_path == "bridge/foo-003.md"
    assert operative.status == k.BridgeStatus.REVISED


def test_find_operative_prime_version_returns_latest_NEW_when_no_REVISED() -> None:
    k = _kind_aware()
    doc = _make_doc(
        "foo",
        [
            ("GO", "bridge/foo-002.md"),
            ("NEW", "bridge/foo-001.md"),
        ],
    )
    operative = k.find_operative_prime_version(doc)
    assert operative is not None
    assert operative.file_path == "bridge/foo-001.md"


def test_find_operative_prime_version_returns_None_when_no_NEW_or_REVISED() -> None:
    k = _kind_aware()
    # All Codex-authored versions (rare; a thread initialized by Codex).
    doc = _make_doc(
        "foo",
        [
            ("VERIFIED", "bridge/foo-002.md"),
            ("GO", "bridge/foo-001.md"),
        ],
    )
    assert k.find_operative_prime_version(doc) is None


def test_find_operative_prime_version_skips_codex_authored_GO_NO_GO_VERIFIED() -> None:
    k = _kind_aware()
    # Mixed: GO/NO-GO/VERIFIED interleaved with REVISED → REVISED is operative.
    doc = _make_doc(
        "foo",
        [
            ("VERIFIED", "bridge/foo-005.md"),
            ("GO", "bridge/foo-004.md"),
            ("REVISED", "bridge/foo-003.md"),
            ("NO-GO", "bridge/foo-002.md"),
            ("NEW", "bridge/foo-001.md"),
        ],
    )
    operative = k.find_operative_prime_version(doc)
    assert operative is not None
    assert operative.status == k.BridgeStatus.REVISED


# --- classify_document_dispatchability (kind tokens) ----------------------


def _classify_with_kind(tmp_path: Path, bridge_kind_value: str | None) -> str:
    """Helper: build a doc + bridge file with the given bridge_kind, classify."""
    k = _kind_aware()
    doc_name = "synth"
    file_path = f"bridge/{doc_name}-001.md"
    if bridge_kind_value is None:
        content = "# Synthetic\nNo bridge_kind here.\n"
    else:
        content = f"# Synthetic\nbridge_kind: {bridge_kind_value}\nMore text.\n"
    _seed_bridge_file(tmp_path, file_path, content)
    doc = _make_doc(doc_name, [("NEW", file_path)])
    return k.classify_document_dispatchability(tmp_path, doc)


def test_classify_terminal_scoping_kind(tmp_path: Path) -> None:
    assert _classify_with_kind(tmp_path, "implementation_scoping") == "terminal"
    assert _classify_with_kind(tmp_path, "scoping_proposal") == "terminal"
    assert _classify_with_kind(tmp_path, "governance_scoping_proposal") == "terminal"


def test_classify_terminal_candidate_spec_intake_kind(tmp_path: Path) -> None:
    assert _classify_with_kind(tmp_path, "candidate_spec_intake") == "terminal"


def test_classify_terminal_closure_kind(tmp_path: Path) -> None:
    assert _classify_with_kind(tmp_path, "closure") == "terminal"
    assert _classify_with_kind(tmp_path, "parking_acknowledgement") == "terminal"
    assert _classify_with_kind(tmp_path, "index_reconciliation") == "terminal"


def test_classify_terminal_compliance_exempt_kinds(tmp_path: Path) -> None:
    """Compliance-exempt non-implementation kinds (mirror of
    bridge-compliance-gate.py BRIDGE_KIND_METADATA_EXEMPT) are dispatch-terminal,
    so a GO does not auto-dispatch headless Prime (forgery-prevention alignment).
    """
    assert _classify_with_kind(tmp_path, "governance_review") == "terminal"
    assert _classify_with_kind(tmp_path, "spec_intake") == "terminal"
    assert _classify_with_kind(tmp_path, "loyal_opposition_advisory") == "terminal"


def test_compliance_exempt_kinds_GO_not_dispatchable(tmp_path: Path) -> None:
    """A GO on a compliance-exempt non-implementation kind is not Prime-dispatchable."""
    k = _kind_aware()
    for kind in ("governance_review", "spec_intake", "loyal_opposition_advisory"):
        classification = _classify_with_kind(tmp_path, kind)
        assert classification == "terminal"
        assert k._derive_dispatchable("GO", classification) is False


def test_compliance_exempt_kinds_review_paths_still_dispatchable(tmp_path: Path) -> None:
    """Terminal means 'no Prime follow-up after GO', not 'no Codex review':
    NEW/REVISED for these kinds still dispatch to Codex; NO-GO still to Prime.
    """
    k = _kind_aware()
    for kind in ("governance_review", "spec_intake", "loyal_opposition_advisory"):
        classification = _classify_with_kind(tmp_path, kind)
        assert k._derive_dispatchable("NEW", classification) is True
        assert k._derive_dispatchable("REVISED", classification) is True
        assert k._derive_dispatchable("NO-GO", classification) is True


def test_classify_dispatchable_implementation_proposal_kind(tmp_path: Path) -> None:
    assert _classify_with_kind(tmp_path, "implementation_proposal") == "dispatchable"
    assert _classify_with_kind(tmp_path, "implementation_slice") == "dispatchable"


def test_classify_terminal_post_implementation_kind(tmp_path: Path) -> None:
    assert _classify_with_kind(tmp_path, "post_implementation_report") == "terminal"
    assert _classify_with_kind(tmp_path, "post_implementation_report_revision") == "terminal"
    assert _classify_with_kind(tmp_path, "post_impl_report") == "terminal"
    assert _classify_with_kind(tmp_path, "implementation_report") == "terminal"


def test_classify_terminal_post_implementation_kebab_variant_kind(tmp_path: Path) -> None:
    """Kebab-norm: post-implementation-report → post_implementation_report match."""
    assert _classify_with_kind(tmp_path, "post-implementation-report") == "terminal"


def test_classify_ambiguous_bare_proposal_kind(tmp_path: Path) -> None:
    assert _classify_with_kind(tmp_path, "proposal") == "ambiguous"


def test_classify_ambiguous_review_kind(tmp_path: Path) -> None:
    """`review` is ambiguous in REVISED-2 — dropped from terminal tokens for safety."""
    assert _classify_with_kind(tmp_path, "review") == "ambiguous"


def test_classify_ambiguous_verification_kind(tmp_path: Path) -> None:
    """`verification` is ambiguous in REVISED-2 — dropped from terminal tokens for safety."""
    assert _classify_with_kind(tmp_path, "verification") == "ambiguous"


def test_classify_ambiguous_when_bridge_kind_field_missing(tmp_path: Path) -> None:
    assert _classify_with_kind(tmp_path, None) == "ambiguous"


def test_classify_ambiguous_when_no_operative_prime_version(tmp_path: Path) -> None:
    """Document with only Codex-authored versions classifies as ambiguous."""
    k = _kind_aware()
    # Note: BridgeStatus uses NO_GO with underscore — but the value is "NO-GO".
    doc = _make_doc("foo", [("VERIFIED", "bridge/foo-002.md"), ("GO", "bridge/foo-001.md")])
    assert k.classify_document_dispatchability(tmp_path, doc) == "ambiguous"


def test_classify_ambiguous_when_file_missing(tmp_path: Path) -> None:
    """Operative version exists in BridgeDocument but the file is not on disk."""
    k = _kind_aware()
    doc = _make_doc("foo", [("REVISED", "bridge/foo-001.md")])
    # Don't write the file
    assert k.classify_document_dispatchability(tmp_path, doc) == "ambiguous"


# --- compute_actionable_pending end-to-end with real bridge chains -------


def _make_index_with_kind(
    tmp_path: Path,
    doc_name: str,
    top_status: str,
    operative_kind: str | None,
    operative_status: str = "REVISED",
    operative_version: int = 3,
    top_version: int = 4,
) -> tuple[str, Path]:
    """Build a real INDEX text + on-disk verdict file + on-disk operative-Prime
    file with the given bridge_kind. Returns (text, project_root).
    """
    project_root = tmp_path
    bridge_dir = project_root / "bridge"
    bridge_dir.mkdir(exist_ok=True)
    # Top file (Codex verdict) — no bridge_kind.
    top_path = bridge_dir / f"{doc_name}-{top_version:03d}.md"
    top_path.write_text(f"# {top_status} verdict on -{operative_version:03d}\n", encoding="utf-8")
    # Operative Prime file — has bridge_kind.
    op_path = bridge_dir / f"{doc_name}-{operative_version:03d}.md"
    op_content = f"# {operative_status}\n"
    if operative_kind is not None:
        op_content += f"bridge_kind: {operative_kind}\n"
    op_path.write_text(op_content, encoding="utf-8")
    # Build INDEX text — top first (most recent), then operative.
    text = (
        f"Document: {doc_name}\n"
        f"{top_status}: bridge/{doc_name}-{top_version:03d}.md\n"
        f"{operative_status}: bridge/{doc_name}-{operative_version:03d}.md\n"
    )
    return text, project_root


def test_compute_pending_codex_NEW_scoping_proposal_is_dispatchable(tmp_path: Path) -> None:
    n = _notify()
    text, root = _make_index_with_kind(
        tmp_path, "foo", "NEW", "scoping_proposal", "NEW", operative_version=4, top_version=4
    )
    parsed = n.parse_index(text)
    prime, codex = n.compute_actionable_pending(parsed, project_root=root)
    assert len(codex) == 1
    assert codex[0].dispatchable is True
    assert codex[0].classification == "terminal"
    assert codex[0].top_status == "NEW"


def test_compute_pending_codex_NEW_candidate_spec_intake_is_dispatchable(tmp_path: Path) -> None:
    n = _notify()
    text, root = _make_index_with_kind(
        tmp_path, "foo", "NEW", "candidate_spec_intake", "NEW", operative_version=4, top_version=4
    )
    parsed = n.parse_index(text)
    _, codex = n.compute_actionable_pending(parsed, project_root=root)
    assert codex[0].dispatchable is True
    assert codex[0].classification == "terminal"


def test_compute_pending_codex_REVISED_terminal_kind_is_dispatchable(tmp_path: Path) -> None:
    n = _notify()
    text, root = _make_index_with_kind(
        tmp_path, "foo", "REVISED", "scoping_proposal", "REVISED", operative_version=3, top_version=3
    )
    parsed = n.parse_index(text)
    _, codex = n.compute_actionable_pending(parsed, project_root=root)
    assert codex[0].dispatchable is True


def test_compute_pending_prime_NO_GO_terminal_kind_is_dispatchable(tmp_path: Path) -> None:
    """F1 fix from -008 NO-GO: terminal-kind NO-GO requires Prime revision."""
    n = _notify()
    text, root = _make_index_with_kind(tmp_path, "foo", "NO-GO", "scoping_proposal")
    parsed = n.parse_index(text)
    prime, _ = n.compute_actionable_pending(parsed, project_root=root)
    assert len(prime) == 1
    assert prime[0].dispatchable is True
    assert prime[0].classification == "terminal"
    assert prime[0].top_status == "NO-GO"


def test_compute_pending_prime_NO_GO_scoping_proposal_is_dispatchable(tmp_path: Path) -> None:
    n = _notify()
    text, root = _make_index_with_kind(tmp_path, "foo", "NO-GO", "scoping_proposal")
    parsed = n.parse_index(text)
    prime, _ = n.compute_actionable_pending(parsed, project_root=root)
    assert prime[0].dispatchable is True


def test_compute_pending_prime_NO_GO_candidate_spec_intake_is_dispatchable(tmp_path: Path) -> None:
    """The exact case Codex cited: candidate-spec-intake NO-GO needs Prime revision."""
    n = _notify()
    text, root = _make_index_with_kind(tmp_path, "foo", "NO-GO", "candidate_spec_intake")
    parsed = n.parse_index(text)
    prime, _ = n.compute_actionable_pending(parsed, project_root=root)
    assert prime[0].dispatchable is True


def test_compute_pending_prime_GO_terminal_kind_is_NOT_dispatchable(tmp_path: Path) -> None:
    """The core token-cost-reduction case: terminal-kind GO is suppressed."""
    n = _notify()
    text, root = _make_index_with_kind(tmp_path, "foo", "GO", "scoping_proposal")
    parsed = n.parse_index(text)
    prime, _ = n.compute_actionable_pending(parsed, project_root=root)
    assert len(prime) == 1
    assert prime[0].dispatchable is False
    assert prime[0].classification == "terminal"
    assert prime[0].top_status == "GO"


def test_compute_pending_prime_GO_candidate_spec_intake_is_NOT_dispatchable(tmp_path: Path) -> None:
    n = _notify()
    text, root = _make_index_with_kind(tmp_path, "foo", "GO", "candidate_spec_intake")
    parsed = n.parse_index(text)
    prime, _ = n.compute_actionable_pending(parsed, project_root=root)
    assert prime[0].dispatchable is False


def test_compute_pending_prime_GO_implementation_proposal_is_dispatchable(tmp_path: Path) -> None:
    n = _notify()
    text, root = _make_index_with_kind(tmp_path, "foo", "GO", "implementation_proposal")
    parsed = n.parse_index(text)
    prime, _ = n.compute_actionable_pending(parsed, project_root=root)
    assert prime[0].dispatchable is True
    assert prime[0].classification == "dispatchable"


def test_compute_pending_prime_GO_implementation_report_is_not_dispatchable(tmp_path: Path) -> None:
    n = _notify()
    text, root = _make_index_with_kind(tmp_path, "foo", "GO", "implementation_report")
    parsed = n.parse_index(text)
    prime, _ = n.compute_actionable_pending(parsed, project_root=root)
    assert len(prime) == 1
    assert prime[0].dispatchable is False
    assert prime[0].classification == "terminal"
    assert prime[0].top_status == "GO"


def test_compute_pending_prime_NO_GO_implementation_report_is_dispatchable(tmp_path: Path) -> None:
    n = _notify()
    text, root = _make_index_with_kind(tmp_path, "foo", "NO-GO", "implementation_report")
    parsed = n.parse_index(text)
    prime, _ = n.compute_actionable_pending(parsed, project_root=root)
    assert len(prime) == 1
    assert prime[0].dispatchable is True
    assert prime[0].classification == "terminal"
    assert prime[0].top_status == "NO-GO"


def test_compute_pending_prime_GO_bare_proposal_is_dispatchable_via_ambiguous(tmp_path: Path) -> None:
    """Legacy bare `bridge_kind: proposal` falls through to ambiguous → dispatchable."""
    n = _notify()
    text, root = _make_index_with_kind(tmp_path, "foo", "GO", "proposal")
    parsed = n.parse_index(text)
    prime, _ = n.compute_actionable_pending(parsed, project_root=root)
    assert prime[0].dispatchable is True
    assert prime[0].classification == "ambiguous"


def test_compute_pending_prime_GO_no_bridge_kind_is_dispatchable_via_ambiguous(tmp_path: Path) -> None:
    """Legacy bridge with no bridge_kind: at all falls through to ambiguous → dispatchable."""
    n = _notify()
    text, root = _make_index_with_kind(tmp_path, "foo", "GO", None)
    parsed = n.parse_index(text)
    prime, _ = n.compute_actionable_pending(parsed, project_root=root)
    assert prime[0].dispatchable is True
    assert prime[0].classification == "ambiguous"


# --- Schema v3 markdown rendering ----------------------------------------


def test_markdown_renders_dispatchable_and_classification_columns(tmp_path: Path) -> None:
    """v3 columns are rendered."""
    n = _notify()
    state_dir = tmp_path / "state"
    items = [
        n.ActionablePending(
            document_name="foo",
            top_status="GO",
            top_file="bridge/foo-002.md",
            index_line_number=8,
            dispatchable=True,
            classification="dispatchable",
        )
    ]
    n.update_notification(state_dir, n.BridgeAgent.PRIME, items)
    md_path = state_dir / "notifications" / "pending-bridge-action-prime.md"
    md_text = md_path.read_text(encoding="utf-8")
    assert "Dispatchable" in md_text
    assert "Classification" in md_text
    assert "yes" in md_text  # dispatchable=True marker


def test_markdown_renders_terminal_prefix_only_when_GO_and_terminal(tmp_path: Path) -> None:
    """`(terminal)` prefix on GO+terminal rows; absent on NO-GO+terminal rows."""
    n = _notify()
    state_dir = tmp_path / "state"
    # GO + terminal → prefix shown
    go_terminal = n.ActionablePending(
        document_name="scoping_thread",
        top_status="GO",
        top_file="bridge/scoping_thread-002.md",
        index_line_number=5,
        dispatchable=False,
        classification="terminal",
    )
    # NO-GO + terminal → prefix NOT shown
    no_go_terminal = n.ActionablePending(
        document_name="intake_thread",
        top_status="NO-GO",
        top_file="bridge/intake_thread-002.md",
        index_line_number=10,
        dispatchable=True,
        classification="terminal",
    )
    n.update_notification(state_dir, n.BridgeAgent.PRIME, [go_terminal, no_go_terminal])
    md_path = state_dir / "notifications" / "pending-bridge-action-prime.md"
    md_text = md_path.read_text(encoding="utf-8")
    # GO row has prefix:
    assert "(terminal) scoping_thread" in md_text
    # NO-GO row does NOT have prefix:
    assert "(terminal) intake_thread" not in md_text
    assert "intake_thread" in md_text  # but the row is still there


# --- Feature flag --------------------------------------------------------


def test_kind_aware_routing_enabled_by_default_when_env_var_unset(monkeypatch) -> None:
    k = _kind_aware()
    monkeypatch.delenv(k.KIND_AWARE_ROUTING_ENV_VAR, raising=False)
    assert k._kind_aware_routing_enabled() is True


def test_kind_aware_routing_disabled_when_env_var_zero(monkeypatch) -> None:
    k = _kind_aware()
    monkeypatch.setenv(k.KIND_AWARE_ROUTING_ENV_VAR, "0")
    assert k._kind_aware_routing_enabled() is False


def test_kind_aware_routing_enabled_when_env_var_one(monkeypatch) -> None:
    k = _kind_aware()
    monkeypatch.setenv(k.KIND_AWARE_ROUTING_ENV_VAR, "1")
    assert k._kind_aware_routing_enabled() is True


def test_compute_pending_prime_ADVISORY_is_actionable_but_not_dispatchable(tmp_path: Path) -> None:
    """ADVISORY status entries appear in actionable_for_prime so manual scans /
    interactive surfaces can present them for owner-deliberation/UAQ disposition,
    but ``dispatchable`` MUST be False so they never spawn a headless Prime
    session. Per gtkb-advisory-prime-actionability-surfacing-002 (Codex GO
    2026-06-14) Conditions 1 + 3: the dispatchability invariant in
    ``_derive_dispatchable`` already forces False for any status other than
    NEW/REVISED/NO-GO and conditionally GO. We intentionally do NOT assert any
    specific ``classification`` token (per Codex Condition 2: do not conflate
    ADVISORY with the VERIFIED-terminal label).
    """
    n = _notify()
    # ADVISORY entries have no NEW/REVISED operative version in this thread shape;
    # construct an INDEX that only has the ADVISORY line + on-disk file.
    bridge_dir = tmp_path / "bridge"
    bridge_dir.mkdir()
    (bridge_dir / "foo-001.md").write_text("ADVISORY\nbridge_kind: loyal_opposition_advisory\n", encoding="utf-8")
    text = "Document: foo\nADVISORY: bridge/foo-001.md\n"
    parsed = n.parse_index(text)
    prime, codex = n.compute_actionable_pending(parsed, project_root=tmp_path)
    assert len(prime) == 1
    assert prime[0].top_status == "ADVISORY"
    assert prime[0].dispatchable is False
    assert codex == []
