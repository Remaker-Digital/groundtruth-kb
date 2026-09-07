"""Spec-derived tests for implementation-start authorization gate."""

from __future__ import annotations

import io
import json
import shutil
import sqlite3
import subprocess
import sys
from pathlib import Path

import pytest
from groundtruth_kb.db import KnowledgeDB
from groundtruth_kb.git_lifecycle.models import OperationDenied
from groundtruth_kb.git_lifecycle.service import GitLifecycleService
from groundtruth_kb.project.registry_control_plane import (
    apply_registry_transaction,
    serialize_registry,
)
from groundtruth_kb.project.sot_registry import SoTArtifact, sync_projection

ROOT = Path(__file__).resolve().parents[2]
TAXONOMY_PATH = ROOT / "config" / "governance" / "project-authorization-operation-taxonomy.toml"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts import implementation_authorization as auth  # noqa: E402
from scripts import implementation_start_gate as gate  # noqa: E402
from scripts import registry_observation_hook as observer  # noqa: E402


@pytest.fixture(autouse=True)
def _clear_ambient_work_intent_env(monkeypatch: pytest.MonkeyPatch) -> None:
    for name in auth.gtkb_session_id.BRIDGE_WORK_INTENT_ORDER:
        monkeypatch.delenv(name, raising=False)
    monkeypatch.setenv("GTKB_HARNESS_NAME", "fixture")


def _proposal(
    *,
    bridge_id: str = "sample-implementation",
    target_paths: list[str] | None = None,
    requirement_sufficiency: str = "Existing requirements sufficient - linked rules cover this implementation.",
) -> str:
    targets = target_paths or [
        "scripts/sample.py",
        "platform_tests/scripts/test_sample.py",
    ]
    return "\n".join(
        [
            "NEW",
            "",
            f"author_identity: prime-builder/fixture-{bridge_id}",
            f"author_session_context_id: fixture-proposal-session-{bridge_id}",
            "bridge_kind: implementation_proposal",
            f"Document: {bridge_id}",
            "Version: 001",
            "",
            "# Implementation Proposal",
            "",
            f"target_paths: {json.dumps(targets)}",
            "",
            "## Specification Links",
            "",
            "- `GOV-FILE-BRIDGE-AUTHORITY-001`",
            "- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`",
            "- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`",
            "",
            "## Requirement Sufficiency",
            "",
            requirement_sufficiency,
            "",
            "## Specification-Derived Verification Plan",
            "",
            "| Test ID | Requirement | Verification |",
            "|---|---|---|",
            "| T-gate | GOV-FILE-BRIDGE-AUTHORITY-001 | pytest |",
            "",
        ]
    )


def _pauth_proposal(*, work_item: str = "WI-AUTH-001", **kwargs: object) -> str:
    """Proposal carrying full authorization metadata.

    WI-6856: ``work_item`` is parameterized because the work-intent registry
    rejects claiming one work item on two threads concurrently. Fixtures that
    stand up two simultaneously-claimed threads must give each a distinct work
    item; the default preserves every single-thread call site unchanged.
    """
    return (
        _proposal(**kwargs)
        + f"\nProject Authorization: `PAUTH-AUTH`\nProject: `PROJECT-AUTH`\nWork Item: `{work_item}`\n"
    )


def _work_item_proposal(*, work_item: str = "WI-AUTH-001", **kwargs: object) -> str:
    """Proposal carrying Work Item metadata but deliberately NO Project Authorization.

    WI-6856: an implementation-bearing claim must carry work-item metadata, so a
    proposal with none cannot be claimed at all and its test body never runs.
    Tests that specify PAUTH-absence behaviour need the work item present and the
    Project Authorization absent, which is what this builder expresses.
    """
    return _proposal(**kwargs) + f"\nWork Item: `{work_item}`\n"


def _go_verdict_body(bridge_id: str = "sample-implementation") -> str:
    return "\n".join(
        [
            "GO",
            "::init gtkb pb",
            "::open build",
            "",
            f"author_identity: loyal-opposition/fixture-{bridge_id}",
            f"author_session_context_id: fixture-go-session-{bridge_id}",
            "bridge_kind: lo_verdict",
            f"Document: {bridge_id}",
            "Version: 002",
            f"Responds to: bridge/{bridge_id}-001.md",
            "",
            "# Review",
            "",
        ]
    )


def _write_implementation_report(root: Path, bridge_id: str, paths: list[str]) -> None:
    (root / "bridge" / f"{bridge_id}-003.md").write_text(
        "\n".join(
            [
                "NEW",
                "",
                f"author_identity: prime-builder/fixture-{bridge_id}",
                f"author_session_context_id: fixture-report-session-{bridge_id}",
                "bridge_kind: implementation_report",
                f"Document: {bridge_id}",
                "Version: 003",
                f"Responds to: bridge/{bridge_id}-002.md",
                "",
                "## Files Changed",
                "",
                *(f"- `{path}`" for path in paths),
                "",
            ]
        ),
        encoding="utf-8",
    )


def _write_thread(
    root: Path,
    *,
    bridge_id: str = "sample-implementation",
    latest_status: str = "GO",
    proposal: str | None = None,
) -> None:
    bridge = root / "bridge"
    bridge.mkdir(exist_ok=True)
    proposal_name = f"{bridge_id}-001.md"
    go_name = f"{bridge_id}-002.md"
    proposal_body = proposal or _proposal(bridge_id=bridge_id)
    (bridge / proposal_name).write_text(proposal_body, encoding="utf-8")
    if latest_status == "GO":
        (bridge / go_name).write_text(_go_verdict_body(bridge_id), encoding="utf-8")
        lines = [
            f"Document: {bridge_id}",
            f"GO: bridge/{go_name}",
            f"NEW: bridge/{proposal_name}",
        ]
    elif latest_status == "REVISED":
        no_go_name = f"{bridge_id}-002.md"
        revised_name = f"{bridge_id}-003.md"
        no_go = _go_verdict_body(bridge_id).replace("GO", "NO-GO", 1)
        revised = proposal_body.replace("NEW", "REVISED", 1)
        revised = revised.replace("Version: 001", "Version: 003", 1)
        revised = revised.replace(
            f"author_session_context_id: fixture-proposal-session-{bridge_id}",
            f"author_session_context_id: fixture-revised-session-{bridge_id}",
            1,
        )
        revised = revised.replace(
            "bridge_kind: implementation_proposal",
            f"Responds to: bridge/{no_go_name}\nbridge_kind: implementation_proposal",
            1,
        )
        (bridge / no_go_name).write_text(no_go, encoding="utf-8")
        (bridge / revised_name).write_text(revised, encoding="utf-8")
        lines = [f"Document: {bridge_id}", f"REVISED: bridge/{revised_name}"]
    else:
        lines = [f"Document: {bridge_id}", f"NEW: bridge/{proposal_name}"]
    (bridge / "INDEX.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def _seed_project_authorization(
    root: Path,
    *,
    link_work_item: bool = True,
    status: str = "active",
    forbidden_operations: list[str] | None = None,
    allowed_mutation_classes: list[str] | None = None,
) -> None:
    taxonomy_target = root / "config" / "governance" / TAXONOMY_PATH.name
    taxonomy_target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(TAXONOMY_PATH, taxonomy_target)
    db = KnowledgeDB(root / "groundtruth.db")
    try:
        db.insert_deliberation(
            "DELIB-PROJECT-AUTH",
            "owner_conversation",
            "Owner approved project authorization",
            "Owner approved project implementation scope.",
            "{}",
            "test",
            "seed project authorization decision",
            outcome="owner_decision",
        )
        db.insert_project(
            "Authorized Project",
            "test",
            "seed project",
            id="PROJECT-AUTH",
            status="active",
        )
        db.insert_work_item(
            "WI-AUTH-001",
            "Authorized work item",
            "new",
            "platform",
            "open",
            "test",
            "seed work item",
            stage="backlogged",
        )
        # WI-6856: a second member so fixtures that stand up two concurrently
        # claimed threads can give each a distinct work item. The work-intent
        # registry refuses to claim one work item on two threads at once, and
        # packet creation refuses a work item that is not a project member, so
        # both records are required. Single-thread fixtures are unaffected;
        # nothing asserts on membership composition.
        db.insert_work_item(
            "WI-AUTH-002",
            "Second authorized work item",
            "new",
            "platform",
            "open",
            "test",
            "seed second work item for concurrent-thread fixtures",
            stage="backlogged",
        )
        if link_work_item:
            db.link_project_work_item(
                "PROJECT-AUTH",
                "WI-AUTH-001",
                "test",
                "seed work item membership",
            )
            db.link_project_work_item(
                "PROJECT-AUTH",
                "WI-AUTH-002",
                "test",
                "seed second work item membership",
            )
        # WI-3312 spec-linkage gate: an active project authorization must cite
        # an approved specification. Seed one so this fixture stays compliant.
        db.insert_spec(
            id="SPEC-AUTH-SEED",
            title="Authorized seed specification",
            status="verified",
            changed_by="test",
            change_reason="seed spec for project authorization fixture",
        )
    finally:
        db.close()


def _seed_owner_sufficiency_deliberation(root: Path) -> str:
    deliberation_id = "DELIB-OWNER-SUFFICIENCY"
    db = KnowledgeDB(root / "groundtruth.db")
    try:
        db.insert_deliberation(
            deliberation_id,
            "owner_conversation",
            "Owner clarified requirement sufficiency",
            "Existing requirements are sufficient.",
            (
                "Mike stated: Existing requirements are sufficient. "
                "This clarification applies to bridge sample-implementation."
            ),
            "test",
            "seed owner sufficiency decision",
            outcome="owner_decision",
        )
    finally:
        db.close()
    return deliberation_id


def _bind_prime_session(root: Path, session_id: str) -> None:
    from groundtruth_kb.session.attestation.service import (
        RoleAttestationError,
        bind_exact_init,
        binding_for_context,
    )

    try:
        binding_for_context(root / "groundtruth.db", session_id)
    except RoleAttestationError as exc:
        if exc.code != "no_session_binding":
            raise
        bind_exact_init(
            root / "groundtruth.db",
            invoking_context=session_id,
            init_command="::init gtkb pb",
            issuer="test/exact-init",
        )


def _claim_bridge(root: Path, bridge_id: str = "sample-implementation", session_id: str | None = None) -> None:
    holder = session_id or "session-1"
    _bind_prime_session(root, holder)
    assert auth.bridge_work_intent_registry.acquire(bridge_id, holder, project_root=root)


def _write_bootstrap_thread(root: Path, bridge_id: str = "bootstrap-implementation") -> None:
    proposal = (
        _proposal(bridge_id=bridge_id, target_paths=["groundtruth.db"])
        + "\nProject: PROJECT-AUTH\n"
        + "Work Item: WI-AUTH-001\n"
        + "Project Authorization: PAUTH-BOOTSTRAP\n"
        + "Owner Decision: DELIB-BOOTSTRAP\n\n"
        + "## Project Authorization Bootstrap\n\n"
        + "project_authorization_bootstrap binds DELIB-BOOTSTRAP to PAUTH-BOOTSTRAP.\n"
    )
    _write_thread(root, bridge_id=bridge_id, proposal=proposal)


def _claim_bootstrap_bridge(
    root: Path,
    bridge_id: str = "bootstrap-implementation",
    session_id: str = "session-bootstrap",
) -> None:
    _bind_prime_session(root, session_id)
    assert auth.bridge_work_intent_registry.acquire(
        bridge_id,
        session_id,
        project_root=root,
        claim_kind=auth.bridge_work_intent_registry.CLAIM_KIND_PROJECT_AUTHORIZATION_BOOTSTRAP,
        bootstrap_authority={
            "owner_decision_id": "DELIB-BOOTSTRAP",
            "project_id": "PROJECT-AUTH",
            "work_item_id": "WI-AUTH-001",
            "authorization_id": "PAUTH-BOOTSTRAP",
            "carrier_targets": ["groundtruth.db"],
        },
    )


def _apply_patch_payload(
    root: Path, target: str = "scripts/sample.py", session_id: str = "session-1"
) -> dict[str, object]:
    return {
        "cwd": str(root),
        "session_id": session_id,
        "tool_name": "apply_patch",
        "tool_input": {"patch": f"*** Begin Patch\n*** Update File: {target}\n@@\n+pass\n*** End Patch\n"},
    }


def _seed_registered_target(root: Path, target: str = "scripts/sample.py") -> None:
    member = root / target
    member.parent.mkdir(parents=True, exist_ok=True)
    member.write_text("before\n", encoding="utf-8")
    record = SoTArtifact(
        id="fixture-registered-target",
        domain="control_surface",
        lifecycle="active",
        storage_path=target,
        authority_spec_id="GOV-PLATFORM-SOT-REGISTRY-001",
        mutation_api="governed implementation edit",
        versioning_policy="git_tracked",
        backup_policy="git_tracked",
        health_check_function="",
        owner_role="shared",
        restore_action="git_restore",
        coverage_mode="exact",
    )
    registry = root / "config" / "registry" / "sot-artifacts.toml"
    packaged = (
        root
        / "groundtruth-kb"
        / "src"
        / "groundtruth_kb"
        / "context"
        / "registries"
        / "v1"
        / "config"
        / "registry"
        / "sot-artifacts.toml"
    )
    registry.parent.mkdir(parents=True, exist_ok=True)
    packaged.parent.mkdir(parents=True, exist_ok=True)
    payload = serialize_registry([record])
    registry.write_bytes(payload)
    packaged.write_bytes(payload)
    db_path = root / "groundtruth.db"
    KnowledgeDB(db_path=db_path)
    sync_projection([record], db_path, changed_by="test", change_reason="registry fixture")
    apply_registry_transaction(
        [record],
        operation="legacy_bootstrap",
        actor_session="fixture-registry",
        changed_by="test",
        change_reason="seed current registry fixture",
        start_packet_hash="sha256:fixture",
        pauth_id="PAUTH-AUTH",
        bridge_id="sample-implementation",
        project_root=root,
        registry_path=registry,
        packaged_registry_path=packaged,
        db_path=db_path,
    )


def _authorize_registered_target(root: Path, target: str = "scripts/sample.py") -> None:
    _seed_project_authorization(root)
    _write_thread(root, proposal=_pauth_proposal(target_paths=[target]))
    packet = auth.create_authorization_packet(root, "sample-implementation")
    auth.write_packet(root, packet)
    _claim_bridge(root)
    _seed_registered_target(root, target)


def _registered_payload(root: Path, target: str = "scripts/sample.py") -> dict[str, object]:
    payload = _apply_patch_payload(root, target=target)
    payload["tool_use_id"] = "fixture-tool-event"
    return payload


def test_go_authorization_packet_without_pauth_blocks_in_scope_apply_patch(
    tmp_path: Path,
) -> None:
    taxonomy_target = tmp_path / "config" / "governance" / TAXONOMY_PATH.name
    taxonomy_target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(TAXONOMY_PATH, taxonomy_target)
    # WI-6856: work item present, Project Authorization absent -- the exact state
    # this test specifies. Without the work item the claim is refused during
    # setup and the assertion below never runs.
    _write_thread(tmp_path, proposal=_work_item_proposal())
    packet = auth.create_authorization_packet(tmp_path, "sample-implementation")
    auth.write_packet(tmp_path, packet)
    _claim_bridge(tmp_path)

    result = gate.gate_decision(_apply_patch_payload(tmp_path))

    assert result["decision"] == "block"
    assert "Project Authorization is required" in result["reason"]


def test_bootstrap_packet_blocks_unrelated_source_apply_patch(tmp_path: Path) -> None:
    bridge_id = "bootstrap-implementation"
    session_id = "session-bootstrap"
    _write_bootstrap_thread(tmp_path, bridge_id=bridge_id)
    _claim_bootstrap_bridge(tmp_path, bridge_id=bridge_id, session_id=session_id)
    packet = auth.create_authorization_packet(tmp_path, bridge_id, session_id=session_id)
    finalized = auth.finalize_implementation_start_packet(tmp_path, packet, session_id=session_id)
    auth.write_started_packets(tmp_path, [finalized])

    result = gate.gate_decision(_apply_patch_payload(tmp_path, target="scripts/sample.py", session_id=session_id))

    assert result["decision"] == "block"
    assert "Target path outside implementation authorization scope" in result["reason"]


def test_pauth_backed_go_authorization_allows_in_scope_apply_patch(
    tmp_path: Path,
) -> None:
    _seed_project_authorization(tmp_path)
    proposal = (
        _proposal() + "\nProject Authorization: `PAUTH-AUTH`\nProject: `PROJECT-AUTH`\nWork Item: `WI-AUTH-001`\n"
    )
    _write_thread(tmp_path, proposal=proposal)
    packet = auth.create_authorization_packet(tmp_path, "sample-implementation")
    auth.write_packet(tmp_path, packet)
    _claim_bridge(tmp_path)

    assert gate.gate_decision(_apply_patch_payload(tmp_path)) == {}


def test_gate_blocks_dirty_path_claimed_by_nonterminal_peer_report(tmp_path: Path, monkeypatch) -> None:
    """WI-5105: protected mutation rechecks a released peer report before edit."""
    peer = "peer-thread"
    current = "current-thread"
    _seed_project_authorization(tmp_path)
    _write_thread(tmp_path, bridge_id=peer)
    peer_packet = auth.create_authorization_packet(tmp_path, peer)
    auth.write_named_packet(tmp_path, peer_packet, peer)
    _write_thread(tmp_path, bridge_id=current, proposal=_pauth_proposal(bridge_id=current))
    current_packet = auth.create_authorization_packet(tmp_path, current)
    auth.write_packet(tmp_path, current_packet)
    _claim_bridge(tmp_path, current, "session-1")
    _write_implementation_report(tmp_path, peer, ["scripts/sample.py"])
    monkeypatch.setattr(auth, "_dirty_worktree_paths", lambda _root: ["scripts/sample.py"])

    result = gate.gate_decision(_apply_patch_payload(tmp_path, session_id="session-1"))

    assert result["decision"] == "block"
    assert "Peer implementation report conflict" in result["reason"]
    assert "peer-thread" in result["reason"]
    assert "scripts/sample.py" in result["reason"]


def test_dispatcher_rules_toml_direct_apply_patch_blocked_even_with_go(
    tmp_path: Path,
) -> None:
    target = "config/dispatcher/rules.toml"
    # WI-6856: work item present so the claim succeeds; the dispatcher-config
    # block under test is unrelated to authorization metadata.
    _write_thread(tmp_path, proposal=_work_item_proposal(target_paths=[target]))
    packet = auth.create_authorization_packet(tmp_path, "sample-implementation")
    auth.write_packet(tmp_path, packet)
    _claim_bridge(tmp_path)

    result = gate.gate_decision(_apply_patch_payload(tmp_path, target=target))

    assert result["decision"] == "block"
    assert result["reason_code"] == "dispatcher_config_cli_only"
    assert "DCL-DISPATCHER-CONFIG-CLI-ONLY-001" in result["reason"]
    assert "gt bridge dispatch config" in result["reason"]


def test_dispatcher_rules_toml_direct_shell_write_blocked(tmp_path: Path) -> None:
    payload = {
        "cwd": str(tmp_path),
        "session_id": "session-1",
        "tool_name": "Bash",
        "tool_input": {"command": "Set-Content -Path config/dispatcher/rules.toml -Value 'schema_version = 1'"},
    }

    result = gate.gate_decision(payload)

    assert result["decision"] == "block"
    assert result["reason_code"] == "dispatcher_config_cli_only"


def test_dispatcher_config_cli_command_not_treated_as_direct_file_edit(
    tmp_path: Path,
) -> None:
    payload = {
        "cwd": str(tmp_path),
        "session_id": "session-1",
        "tool_name": "Bash",
        "tool_input": {
            "command": (
                "python -m groundtruth_kb.cli bridge dispatch config set-eligibility F --no-can-receive-dispatch"
            )
        },
    }

    assert gate.gate_decision(payload) == {}


def test_blocks_when_work_intent_claim_missing(tmp_path: Path) -> None:
    """WI-7751: the work-intent claim is a RETAINED readiness control.

    v5 retires the implementation-start packet but keeps "a matching live
    work-intent claim" in the readiness set, so a protected mutation with no claim
    is still refused. The refusal now names the claim rather than the packet.
    """
    _seed_project_authorization(tmp_path)
    _write_thread(tmp_path, proposal=_pauth_proposal())

    result = gate.gate_decision(_apply_patch_payload(tmp_path))

    assert result["decision"] == "block"
    assert "work-intent claim" in result["reason"]


def test_valid_packet_blocks_when_claim_held_by_other_session(tmp_path: Path) -> None:
    _seed_project_authorization(tmp_path)
    _write_thread(tmp_path, proposal=_pauth_proposal())
    packet = auth.create_authorization_packet(tmp_path, "sample-implementation")
    auth.write_packet(tmp_path, packet)
    _claim_bridge(tmp_path, "sample-implementation", "other-session")

    result = gate.gate_decision(_apply_patch_payload(tmp_path, session_id="session-1"))

    assert result["decision"] == "block"
    assert "claimed by session 'other-session'" in result["reason"]


def test_lapsed_claim_blocks_mutation(tmp_path: Path) -> None:
    _seed_project_authorization(tmp_path)
    _write_thread(tmp_path, proposal=_pauth_proposal())
    packet = auth.create_authorization_packet(tmp_path, "sample-implementation")
    auth.write_packet(tmp_path, packet)
    _claim_bridge(tmp_path, "sample-implementation", "session-1")
    conn = auth.bridge_work_intent_registry._get_conn(tmp_path)
    try:
        with conn:
            conn.execute(
                "UPDATE work_intent_claims SET ttl_expires_at = ?, implementation_grace_expires_at = ? "
                "WHERE thread_slug = ?",
                (
                    "2026-01-01T00:00:00Z",
                    "2026-01-01T00:00:00Z",
                    "sample-implementation",
                ),
            )
    finally:
        conn.close()

    result = gate.gate_decision(_apply_patch_payload(tmp_path))

    assert result["decision"] == "block"
    assert "No active work-intent claim" in result["reason"]


def test_gate_allows_concurrent_authorized_implementers(tmp_path: Path) -> None:
    """WI-4443 + WI-4471: concurrent Prime Builders with overlapping scope.

    bridge-a and bridge-b both authorize ``scripts/shared.py``; bridge-b also
    authorizes ``scripts/b_only.py``. The ambient session claims bridge-a;
    session-B claims bridge-b; bridge-b's ``begin`` clobbers current.json.

    WI-4443 fix: session-aware packet lookup ensures current.json clobbering
    does not wrongly route the ambient session to bridge-b's packet.

    WI-4471 change: the cross-claim collision check now BLOCKS the ambient
    session from mutating ``scripts/shared.py`` when session-B's active
    claim+packet (bridge-b) also reserves that path.  This is the intentional
    tightening -- concurrent implementers must not edit the same file.

    (a) ambient session mutating ``scripts/shared.py`` -> BLOCKED (WI-4471:
        bridge-b / session-B collision).
    (c) ambient session mutating ``scripts/b_only.py`` (bridge-b's exclusive
        scope) -> BLOCKED by packet authorization (bridge-a doesn't cover it).
    """
    _seed_project_authorization(tmp_path)
    bridge = tmp_path / "bridge"
    bridge.mkdir()
    (bridge / "bridge-a-001.md").write_text(
        _pauth_proposal(bridge_id="bridge-a", target_paths=["scripts/shared.py"]),
        encoding="utf-8",
    )
    (bridge / "bridge-a-002.md").write_text(_go_verdict_body("bridge-a"), encoding="utf-8")
    (bridge / "bridge-b-001.md").write_text(
        _pauth_proposal(
            bridge_id="bridge-b",
            target_paths=["scripts/shared.py", "scripts/b_only.py"],
            work_item="WI-AUTH-002",
        ),
        encoding="utf-8",
    )
    (bridge / "bridge-b-002.md").write_text(_go_verdict_body("bridge-b"), encoding="utf-8")
    (bridge / "INDEX.md").write_text(
        "Document: bridge-a\nGO: bridge/bridge-a-002.md\nNEW: bridge/bridge-a-001.md\n\n"
        "Document: bridge-b\nGO: bridge/bridge-b-002.md\nNEW: bridge/bridge-b-001.md\n",
        encoding="utf-8",
    )

    # Both begin; bridge-b's begin clobbers current.json to bridge-b.
    packet_a = auth.create_authorization_packet(tmp_path, "bridge-a")
    auth.write_packet(tmp_path, packet_a)
    auth.write_named_packet(tmp_path, packet_a, "bridge-a")
    packet_b = auth.create_authorization_packet(tmp_path, "bridge-b")
    auth.write_packet(tmp_path, packet_b)
    auth.write_named_packet(tmp_path, packet_b, "bridge-b")
    assert json.loads(auth.packet_path(tmp_path).read_text(encoding="utf-8"))["bridge_id"] == "bridge-b"

    # Two concurrent implementers: ambient session claims bridge-a; session-B claims bridge-b.
    _claim_bridge(tmp_path, "bridge-a")
    _claim_bridge(tmp_path, "bridge-b", "session-B")

    # (a) WI-4471: ambient session's mutation of the overlapping target is now BLOCKED
    # because session-B's active bridge-b claim+packet also reserves scripts/shared.py.
    collision = gate.gate_decision(_apply_patch_payload(tmp_path, target="scripts/shared.py"))
    assert collision["decision"] == "block"
    assert "bridge-b" in collision["reason"]
    assert "session-B" in collision["reason"]

    # (c) ambient session mutating bridge-b's exclusive target is blocked (no claim on bridge-b).
    cross = gate.gate_decision(_apply_patch_payload(tmp_path, target="scripts/b_only.py"))
    assert cross["decision"] == "block"


def test_gate_allows_when_holder_is_dispatch_id(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _seed_project_authorization(tmp_path)
    _write_thread(tmp_path, proposal=_pauth_proposal())
    packet = auth.create_authorization_packet(tmp_path, "sample-implementation")
    auth.write_packet(tmp_path, packet)
    _claim_bridge(tmp_path, "sample-implementation", "dispatch-1")
    monkeypatch.setenv("GTKB_BRIDGE_POLLER_RUN_ID", "dispatch-1")

    assert gate.gate_decision(_apply_patch_payload(tmp_path, session_id="ambient-session")) == {}


def test_gate_blocks_on_work_intent_registry_error(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _seed_project_authorization(tmp_path)
    _write_thread(tmp_path, proposal=_pauth_proposal())
    packet = auth.create_authorization_packet(tmp_path, "sample-implementation")
    auth.write_packet(tmp_path, packet)
    _claim_bridge(tmp_path, "sample-implementation", "session-1")

    def raise_registry_error(*_args, **_kwargs):
        raise auth.bridge_work_intent_registry.WorkIntentRegistryError("registry unavailable")

    monkeypatch.setattr(auth.bridge_work_intent_registry, "current_holder", raise_registry_error)

    result = gate.gate_decision(_apply_patch_payload(tmp_path))

    assert result["decision"] == "block"
    assert "Could not verify bridge work-intent claim" in result["reason"]


def test_bootstrap_bridge_id_does_not_exempt_the_claim_check(tmp_path: Path) -> None:
    """WI-7751: the bootstrap exemption is narrow, and this is its boundary test.

    The retired predicate this test used to assert -- that a bootstrap id does not
    exempt a missing project authorization -- has no subject under v5, which states
    no authorization instrument exists. The surviving invariant is that bootstrap
    narrows exactly one thing: scope derivation, which cannot apply to a thread whose
    purpose is to bring the gate's own authority surface into being. It does NOT
    exempt the claim check. Without this, the bootstrap branch added by WI-7751 could
    silently widen into a general bypass and no test would notice.
    """
    bridge_id = "gtkb-implementation-start-authorization-gate"
    _seed_project_authorization(tmp_path)
    _write_thread(
        tmp_path,
        bridge_id=bridge_id,
        proposal=_proposal(bridge_id=bridge_id, target_paths=["scripts/sample.py"]),
    )

    result = gate.gate_decision(_apply_patch_payload(tmp_path, session_id=""))

    assert result["decision"] == "block"
    assert "work-intent claim" in result["reason"]


def test_existing_packet_blocks_when_bridge_becomes_latest_deferred(
    tmp_path: Path,
) -> None:
    (tmp_path / "groundtruth.toml").write_text('[groundtruth]\ndb_path = "groundtruth.db"\n', encoding="utf-8")
    _write_thread(tmp_path)
    packet = auth.create_authorization_packet(tmp_path, "sample-implementation")
    auth.write_packet(tmp_path, packet)
    bridge = tmp_path / "bridge"
    (bridge / "sample-implementation-003.md").write_text(
        "\n".join(
            [
                "DEFERRED",
                "",
                "author_identity: prime-builder/fixture-sample-implementation",
                "author_session_context_id: fixture-deferred-session-sample-implementation",
                "bridge_kind: prime_proposal",
                "Document: sample-implementation",
                "Version: 003",
                "Responds to: bridge/sample-implementation-002.md",
                "",
                "# Owner deferral",
                "",
            ]
        ),
        encoding="utf-8",
    )
    (bridge / "INDEX.md").write_text(
        "\n".join(
            [
                "Document: sample-implementation",
                "DEFERRED: bridge/sample-implementation-003.md",
                "GO: bridge/sample-implementation-002.md",
                "NEW: bridge/sample-implementation-001.md",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    target = "scripts/" + "sample.py"
    payload = {
        "cwd": str(tmp_path),
        "tool_name": "apply_patch",
        "tool_input": {"patch": f"*** Begin Patch\n*** Update File: {target}\n@@\n+pass\n*** End Patch\n"},
    }

    result = gate.gate_decision(payload)

    # WI-7751: an obsolete-status file confers nothing, including no block.
    # DEFERRED is an obsolete bridge status: it "confers no routing, lifecycle,
    # claim, lease, or implementation state". This mutation is still refused, but
    # the refusal must come from a RETAINED control rather than from the presence
    # of an obsolete token in the chain. Asserting DEFERRED as the reason would
    # re-grant the obsolete status exactly the lifecycle meaning canon removes.
    assert result["decision"] == "block"
    assert "DEFERRED" not in result["reason"]
    assert "work-intent claim" in result["reason"]


def test_no_auth_blocks_protected_source_edit(tmp_path: Path) -> None:
    _write_thread(tmp_path)
    payload = {
        "cwd": str(tmp_path),
        "tool_name": "apply_patch",
        "tool_input": {"patch": "*** Begin Patch\n*** Update File: scripts/sample.py\n@@\n+pass\n*** End Patch\n"},
    }

    result = gate.gate_decision(payload)

    assert result["decision"] == "block"
    assert "authorization packet" in result["reason"]


def test_emergency_bridge_repair_allows_bridge_function_edit_without_packet(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    audit_path = tmp_path / "gate-events.jsonl"
    monkeypatch.setenv(gate.EMERGENCY_BRIDGE_REPAIR_ENV_VAR, "1")
    monkeypatch.setenv("GTKB_GATE_DENIALS_PATH", str(audit_path))

    result = gate.gate_decision(_apply_patch_payload(tmp_path, target="scripts/dispatcher_runtime.py"))

    assert result == {}
    [record] = [json.loads(line) for line in audit_path.read_text(encoding="utf-8").splitlines()]
    assert record["event"] == "exemption"
    assert record["pattern_id"] == "emergency-bridge-repair"
    assert record["paths"] == ["scripts/dispatcher_runtime.py"]


def test_emergency_env_does_not_exempt_registry_control_plane_edit(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv(gate.EMERGENCY_BRIDGE_REPAIR_ENV_VAR, "1")

    result = gate.gate_decision(
        _apply_patch_payload(
            tmp_path,
            target="groundtruth-kb/src/groundtruth_kb/project/registry_control_plane.py",
        )
    )

    assert result["decision"] == "block"
    assert "authorization packet" in result["reason"]


def test_no_emergency_env_blocks_bridge_function_edit(tmp_path: Path) -> None:
    result = gate.gate_decision(_apply_patch_payload(tmp_path, target="scripts/dispatcher_runtime.py"))

    assert result["decision"] == "block"
    assert "authorization packet" in result["reason"]


def test_emergency_env_does_not_exempt_unknown_mutating_target(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(gate.EMERGENCY_BRIDGE_REPAIR_ENV_VAR, "1")
    payload = {
        "cwd": str(tmp_path),
        "tool_name": "Bash",
        "tool_input": {"command": "python -c \"open('scripts/dispatcher_runtime.py', 'w').write('x')\""},
    }

    result = gate.gate_decision(payload)

    assert result["decision"] == "block"
    assert "<unknown-mutating-target>" in result["reason"]


PROTECTED_COMMIT_CHECKER = "scripts/check_protected_commit_authorization.py"


def test_bridge_function_exact_includes_protected_commit_checker() -> None:
    """WI-6036: the checker must be reachable by the emergency-bootstrap exception.

    Repairing the checker requires committing it; committing it runs the
    protected-commit gate, which is the code under repair. Membership here is
    what gives that repair a landable path.
    """
    assert PROTECTED_COMMIT_CHECKER in gate.BRIDGE_FUNCTION_EXACT


def test_bridge_function_exact_membership_is_exactly_the_expected_set() -> None:
    """WI-6036 acceptance 5: no other entry is added or removed."""
    expected = {
        ".claude/settings.json",
        ".codex/hooks.json",
        "scripts/bridge_claim_cli.py",
        PROTECTED_COMMIT_CHECKER,
        "scripts/dispatcher_runtime.py",
        "scripts/gtkb_bridge_writer.py",
        "scripts/implementation_authorization.py",
        "scripts/implementation_start_gate.py",
    }
    assert expected == gate.BRIDGE_FUNCTION_EXACT


def test_bridge_function_prefixes_are_unchanged() -> None:
    """WI-6036 acceptance 5: BRIDGE_FUNCTION_PREFIXES is unchanged."""
    assert gate.BRIDGE_FUNCTION_PREFIXES == (
        ".claude/hooks/",
        ".codex/gtkb-hooks/",
        "groundtruth-kb/src/groundtruth_kb/bridge/",
    )


def test_emergency_bridge_repair_allows_protected_commit_checker_edit(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """WI-6036 acceptance 1: the checker edit is exempt under the opt-in."""
    audit_path = tmp_path / "gate-events.jsonl"
    monkeypatch.setenv(gate.EMERGENCY_BRIDGE_REPAIR_ENV_VAR, "1")
    monkeypatch.setenv("GTKB_GATE_DENIALS_PATH", str(audit_path))

    result = gate.gate_decision(_apply_patch_payload(tmp_path, target=PROTECTED_COMMIT_CHECKER))

    assert result == {}
    [record] = [json.loads(line) for line in audit_path.read_text(encoding="utf-8").splitlines()]
    assert record["event"] == "exemption"
    assert record["pattern_id"] == "emergency-bridge-repair"
    assert record["paths"] == [PROTECTED_COMMIT_CHECKER]


def test_no_emergency_env_blocks_protected_commit_checker_edit(tmp_path: Path) -> None:
    """WI-6036 acceptance 2: the opt-in remains mandatory; no new standing authority."""
    result = gate.gate_decision(_apply_patch_payload(tmp_path, target=PROTECTED_COMMIT_CHECKER))

    assert result["decision"] == "block"
    assert "authorization packet" in result["reason"]


def test_emergency_env_refuses_checker_mixed_with_non_bridge_function_path(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """WI-6036 acceptance 3: the all-paths rule is unchanged.

    One non-bridge-function protected path in the operation still defeats the
    exception, so the checker's membership cannot be used to smuggle unrelated
    protected edits through the bootstrap escape.
    """
    monkeypatch.setenv(gate.EMERGENCY_BRIDGE_REPAIR_ENV_VAR, "1")
    patch = (
        "*** Begin Patch\n"
        f"*** Update File: {PROTECTED_COMMIT_CHECKER}\n@@\n+pass\n"
        "*** Update File: groundtruth-kb/src/groundtruth_kb/project/registry_control_plane.py\n@@\n+pass\n"
        "*** End Patch\n"
    )
    payload = {
        "cwd": str(tmp_path),
        "session_id": "session-1",
        "tool_name": "apply_patch",
        "tool_input": {"patch": patch},
    }

    result = gate.gate_decision(payload)

    assert result["decision"] == "block"
    assert "authorization packet" in result["reason"]


def test_emergency_env_does_not_exempt_unknown_mutating_checker_target(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """WI-6036 acceptance 4: the <unknown-mutating-target> refusal is unchanged."""
    monkeypatch.setenv(gate.EMERGENCY_BRIDGE_REPAIR_ENV_VAR, "1")
    payload = {
        "cwd": str(tmp_path),
        "tool_name": "Bash",
        "tool_input": {"command": f"python -c \"open('{PROTECTED_COMMIT_CHECKER}', 'w').write('x')\""},
    }

    result = gate.gate_decision(payload)

    assert result["decision"] == "block"
    assert "<unknown-mutating-target>" in result["reason"]


def test_non_go_bridge_entry_cannot_create_authorization(tmp_path: Path) -> None:
    _write_thread(tmp_path, latest_status="REVISED")

    with pytest.raises(auth.AuthorizationError, match="requires a GO in the bridge chain"):
        auth.create_authorization_packet(tmp_path, "sample-implementation")


def test_authorization_accepts_bold_target_paths_metadata(tmp_path: Path) -> None:
    _write_thread(tmp_path, proposal=_proposal().replace("target_paths:", "**target_paths:**"))

    packet = auth.create_authorization_packet(tmp_path, "sample-implementation")

    assert packet["target_path_globs"] == [
        "scripts/sample.py",
        "platform_tests/scripts/test_sample.py",
    ]


def test_exact_file_target_path_authorizes_exact_protected_file(tmp_path: Path) -> None:
    exact_target = "config/governance/hygiene-baseline-registry.toml"
    _seed_project_authorization(tmp_path)
    _write_thread(tmp_path, proposal=_pauth_proposal(target_paths=[exact_target]))
    packet = auth.create_authorization_packet(tmp_path, "sample-implementation")
    auth.write_packet(tmp_path, packet)
    _claim_bridge(tmp_path)
    sample_patch = f"*** Begin Patch\n*** Update File: {exact_target}\n@@\n+enabled = true\n*** End Patch\n"

    payload = {
        "cwd": str(tmp_path),
        "session_id": "session-1",
        "tool_name": "apply_patch",
        "tool_input": {"patch": sample_patch},
    }

    assert packet["target_path_globs"] == [exact_target]
    assert gate.gate_decision(payload) == {}


@pytest.mark.parametrize(
    ("path", "classification"),
    [
        (".claude/hooks/h.py", ".claude/hooks/"),
        ("./.claude/hooks/h.py", ".claude/hooks/"),
        (".claude/rules/x.md", ".claude/rules/"),
        (".codex/gtkb-hooks/a.py", ".codex/gtkb-hooks/"),
        (".github/workflows/ci.yml", ".github/"),
        (".claude/settings.json", "registry:wi5441-claude-settings-json"),
        (".codex/hooks.json", "registry:wi5441-member-codex-hooks-json-82c735c2c8"),
        (".env", ".env"),
        ("./.env.local", "registry:owner-local-env"),
        ("env.local", "env.local"),
        ("env.staging", "env.staging"),
        ("bridge/example-001.md", "bridge/<slug>-NNN.md"),
        ("bridge/INDEX.md", "bridge/INDEX.md"),
        ("groundtruth.db", "groundtruth.db"),
        (
            ".gtkb-state/implementation-authorizations/current.json",
            ".gtkb-state/implementation-authorizations/",
        ),
    ],
)
def test_is_protected_path_preserves_dot_prefixed_protected_paths(path: str, classification: str) -> None:
    assert gate.is_protected_path(path) is True
    assert gate._protected_path_classification(path) == classification


def test_protected_path_classification_preserves_dot_prefixed_prefixes() -> None:
    assert gate.is_protected_path("./bridge/proposal.md") is False
    assert gate.is_protected_path("./.gtkb-state/diagnostic.json") is False
    assert gate.is_protected_path("./scripts/tool.py") is True


def test_requirement_gap_blocks_authorization(tmp_path: Path) -> None:
    _write_thread(
        tmp_path,
        proposal=_proposal(
            requirement_sufficiency="New or revised requirement required before implementation - capture it first."
        ),
    )

    with pytest.raises(auth.AuthorizationError, match="new or revised requirements"):
        auth.create_authorization_packet(tmp_path, "sample-implementation")


def test_requirement_sufficiency_are_sufficient_allows_gate_authorization(
    tmp_path: Path,
) -> None:
    """WI-3410: natural sufficient-state wording authorizes protected edits."""
    _seed_project_authorization(tmp_path)
    _write_thread(
        tmp_path,
        proposal=_pauth_proposal(requirement_sufficiency="Existing requirements are sufficient for this scoped fix."),
    )
    packet = auth.create_authorization_packet(tmp_path, "sample-implementation")
    auth.write_packet(tmp_path, packet)
    _claim_bridge(tmp_path)
    sample_patch = "*** Begin Patch\n*** Update File: scripts/sample.py\n@@\n+pass\n*** End Patch\n"

    payload = {
        "cwd": str(tmp_path),
        "session_id": "session-1",
        "tool_name": "apply_patch",
        "tool_input": {"patch": sample_patch},
    }

    assert packet["requirement_sufficiency"] == "sufficient"
    assert gate.gate_decision(payload) == {}


def test_owner_sufficiency_deliberation_packet_allows_gate_authorization(
    tmp_path: Path,
) -> None:
    """WI-4241: owner-decision fallback packets authorize protected edits."""
    _seed_project_authorization(tmp_path)
    _write_thread(
        tmp_path,
        proposal=_pauth_proposal(requirement_sufficiency="Complete coverage exists without the bounded phrase."),
    )
    delib_id = _seed_owner_sufficiency_deliberation(tmp_path)
    packet = auth.create_authorization_packet(
        tmp_path,
        "sample-implementation",
        owner_sufficiency_deliberation_id=delib_id,
    )
    auth.write_packet(tmp_path, packet)
    _claim_bridge(tmp_path)
    sample_patch = (
        "*** Begin Patch\n" + "*** " + "Update File: scripts/sample.py\n" + "@@\n" + "+pass\n" + "*** End Patch\n"
    )

    payload = {
        "cwd": str(tmp_path),
        "session_id": "session-1",
        "tool_name": "apply_patch",
        "tool_input": {"patch": sample_patch},
    }

    assert packet["requirement_sufficiency"] == "owner_deliberation"
    assert packet["requirement_sufficiency_evidence"]["deliberation_id"] == delib_id
    assert gate.gate_decision(payload) == {}


def test_project_authorization_metadata_is_carried_in_packet(tmp_path: Path) -> None:
    _seed_project_authorization(tmp_path)
    proposal = (
        _proposal() + "\nProject Authorization: `PAUTH-AUTH`\nProject: `PROJECT-AUTH`\nWork Item: `WI-AUTH-001`\n"
    )
    _write_thread(tmp_path, proposal=proposal)

    packet = auth.create_authorization_packet(tmp_path, "sample-implementation")
    auth.write_packet(tmp_path, packet)

    assert packet["project_authorization"]["id"] == "PAUTH-AUTH"
    assert packet["project_authorization"]["project_id"] == "PROJECT-AUTH"
    assert packet["project_authorization"]["work_item_id"] == "WI-AUTH-001"
    assert auth.load_packet(tmp_path)["project_authorization"]["id"] == "PAUTH-AUTH"


def test_start_finalizer_emits_schema3_without_packet_role_or_envelope_authority(
    tmp_path: Path,
) -> None:
    _seed_project_authorization(tmp_path)
    proposal = (
        _proposal() + "\nProject Authorization: `PAUTH-AUTH`\nProject: `PROJECT-AUTH`\nWork Item: `WI-AUTH-001`\n"
    )
    _write_thread(tmp_path, proposal=proposal)
    packet = auth.create_authorization_packet(tmp_path, "sample-implementation")
    pre_start_hash = packet["packet_hash"]
    _claim_bridge(tmp_path)

    finalized = auth.finalize_implementation_start_packet(tmp_path, packet, session_id="session-1")
    auth.write_started_packets(tmp_path, [finalized])

    evidence = finalized["implementation_start"]
    assert finalized["schema_version"] == 3
    assert evidence["pre_start_packet_hash"] == pre_start_hash
    assert evidence["session_id"] == "session-1"
    assert evidence["work_intent_claim"]["claim_kind"] == "go_implementation"
    assert evidence["schema_version"] == 3
    serialized_evidence = json.dumps(evidence, sort_keys=True)
    assert "role_attestation" not in serialized_evidence
    assert "worker_role_provenance" not in serialized_evidence
    assert "session_envelope_id" not in serialized_evidence
    assert "acting_role" not in serialized_evidence
    assert evidence["project_authorization_decision"]["normalized_operation"] == "implementation_start"
    assert evidence["project_authorization_decision"]["allowed"] is True
    assert auth.packet_hash(finalized) == finalized["packet_hash"]
    assert auth.load_packet(tmp_path) == finalized
    assert auth.load_named_packet(tmp_path, "sample-implementation") == finalized


@pytest.mark.parametrize("replacement", ["", "::init gtkb lo"])
def test_start_finalizer_denies_missing_or_wrong_authored_go_init_role(
    tmp_path: Path,
    replacement: str,
) -> None:
    _seed_project_authorization(tmp_path)
    _write_thread(tmp_path, proposal=_pauth_proposal())
    packet = auth.create_authorization_packet(tmp_path, "sample-implementation")
    _claim_bridge(tmp_path)
    go_path = tmp_path / "bridge" / "sample-implementation-002.md"
    go_path.write_text(
        go_path.read_text(encoding="utf-8").replace("::init gtkb pb", replacement, 1),
        encoding="utf-8",
    )

    with pytest.raises(auth.AuthorizationError, match="DENY_NO_INIT_ROLE"):
        auth.finalize_implementation_start_packet(tmp_path, packet, session_id="session-1")

    assert not auth.packet_path(tmp_path).exists()
    assert not auth.packet_path_for_bridge(tmp_path, "sample-implementation").exists()


def _git_lifecycle_service_with_schema3_authority(tmp_path: Path) -> GitLifecycleService:
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    _seed_project_authorization(tmp_path)
    proposal = _proposal() + "\nProject Authorization: PAUTH-AUTH\nProject: PROJECT-AUTH\nWork Item: WI-AUTH-001\n"
    _write_thread(tmp_path, proposal=proposal)
    packet = auth.create_authorization_packet(tmp_path, "sample-implementation")
    _claim_bridge(tmp_path)
    finalized = auth.finalize_implementation_start_packet(tmp_path, packet, session_id="session-1")
    auth.write_started_packets(tmp_path, [finalized])
    return GitLifecycleService(tmp_path)


def test_git_lifecycle_service_accepts_schema3_from_authored_go_without_session_store(
    tmp_path: Path,
) -> None:
    service = _git_lifecycle_service_with_schema3_authority(tmp_path)

    authority = service._current_authority(
        bridge_id="sample-implementation",
        work_item_id="WI-AUTH-001",
        required_paths=("scripts/sample.py",),
    )

    assert authority["authored_role_source"]["init_line"] == "::init gtkb pb"
    assert authority["authored_role_source"]["path"] == "bridge/sample-implementation-002.md"
    source = (ROOT / "groundtruth-kb/src/groundtruth_kb/git_lifecycle/service.py").read_text(encoding="utf-8")
    assert "resolve_worker_role_provenance" not in source
    assert "groundtruth_kb.session.envelope" not in source
    assert "session-envelopes" not in source


def test_git_lifecycle_service_denies_when_authored_go_init_role_disappears(
    tmp_path: Path,
) -> None:
    service = _git_lifecycle_service_with_schema3_authority(tmp_path)
    go_path = tmp_path / "bridge" / "sample-implementation-002.md"
    go_path.write_text(
        go_path.read_text(encoding="utf-8").replace("::init gtkb pb\n", "", 1),
        encoding="utf-8",
    )

    with pytest.raises(OperationDenied) as caught:
        service._current_authority(
            bridge_id="sample-implementation",
            work_item_id="WI-AUTH-001",
            required_paths=("scripts/sample.py",),
        )

    assert caught.value.code == "DENY_NO_INIT_ROLE"


def test_git_lifecycle_service_builds_receipts_only_from_verified_message_fields() -> None:
    fields = {
        "Author-Session": "prime-session",
        "Author-Role": "prime-builder",
        "Verifier-Session": "lo-session",
        "Verifier-Role": "loyal-opposition",
    }

    assert GitLifecycleService._verdict_session_receipt(
        fields,
        session_field="Author-Session",
        role_field="Author-Role",
        expected_role="prime-builder",
    ) == {
        "session_id": "prime-session",
        "role": "prime-builder",
        "provenance_source": "verified_message_header",
    }
    with pytest.raises(OperationDenied) as caught:
        GitLifecycleService._verdict_session_receipt(
            {},
            session_field="Verifier-Session",
            role_field="Verifier-Role",
            expected_role="loyal-opposition",
        )
    assert caught.value.code == "verification_session_invalid"


def test_start_finalizer_rejects_missing_pauth_for_protected_targets(
    tmp_path: Path,
) -> None:
    taxonomy_target = tmp_path / "config" / "governance" / TAXONOMY_PATH.name
    taxonomy_target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(TAXONOMY_PATH, taxonomy_target)
    # WI-6856: work item present, Project Authorization absent -- the state this
    # test specifies. The claim must succeed for the finalizer to be reached.
    _write_thread(tmp_path, proposal=_work_item_proposal())
    packet = auth.create_authorization_packet(tmp_path, "sample-implementation")
    _claim_bridge(tmp_path)

    with pytest.raises(auth.AuthorizationError, match="Project Authorization is required"):
        auth.finalize_implementation_start_packet(tmp_path, packet, session_id="session-1")


def test_start_finalizer_denial_writes_no_packet(tmp_path: Path) -> None:
    _seed_project_authorization(tmp_path, forbidden_operations=["implementation_start"])
    proposal = (
        _proposal() + "\nProject Authorization: `PAUTH-AUTH`\nProject: `PROJECT-AUTH`\nWork Item: `WI-AUTH-001`\n"
    )
    _write_thread(tmp_path, proposal=proposal)
    packet = auth.create_authorization_packet(tmp_path, "sample-implementation")
    _claim_bridge(tmp_path)

    with pytest.raises(
        auth.AuthorizationError,
        match=r"forbidden_operation: Operation 'implementation_start' is forbidden\.",
    ):
        auth.finalize_implementation_start_packet(tmp_path, packet, session_id="session-1")

    assert not auth.packet_path(tmp_path).exists()
    assert not auth.packet_path_for_bridge(tmp_path, "sample-implementation").exists()


@pytest.mark.parametrize("forbidden_operation", ["implementation_start", "protected_mutation"])
def test_gate_rechecks_live_project_authorization_before_protected_effect(
    tmp_path: Path,
    forbidden_operation: str,
) -> None:
    _seed_project_authorization(tmp_path, forbidden_operations=[forbidden_operation])
    proposal = (
        _proposal() + "\nProject Authorization: `PAUTH-AUTH`\nProject: `PROJECT-AUTH`\nWork Item: `WI-AUTH-001`\n"
    )
    _write_thread(tmp_path, proposal=proposal)
    packet = auth.create_authorization_packet(tmp_path, "sample-implementation")
    auth.write_packet(tmp_path, packet)
    _claim_bridge(tmp_path)

    result = gate.gate_decision(_apply_patch_payload(tmp_path))

    assert result["decision"] == "block"
    assert f"Operation '{forbidden_operation}' is forbidden." in result["reason"]
    assert "forbidden_operation" in result["reason"]


def test_work_intent_acquire_denial_creates_no_claim(tmp_path: Path) -> None:
    _seed_project_authorization(tmp_path, forbidden_operations=["work_intent_acquire"])
    proposal = (
        _proposal() + "\nProject Authorization: `PAUTH-AUTH`\nProject: `PROJECT-AUTH`\nWork Item: `WI-AUTH-001`\n"
    )
    _write_thread(tmp_path, proposal=proposal)
    _bind_prime_session(tmp_path, "session-1")

    with pytest.raises(
        auth.bridge_work_intent_registry.WorkIntentRegistryError,
        match="work_intent_acquire",
    ):
        auth.bridge_work_intent_registry.acquire("sample-implementation", "session-1", project_root=tmp_path)

    conn = sqlite3.connect(tmp_path / "groundtruth.db")
    try:
        count = conn.execute(
            "SELECT COUNT(*) FROM work_intent_claims WHERE thread_slug = ?",
            ("sample-implementation",),
        ).fetchone()[0]
    finally:
        conn.close()
    assert count == 0


def test_work_intent_extension_denial_leaves_claim_unchanged(tmp_path: Path) -> None:
    _seed_project_authorization(tmp_path, forbidden_operations=["work_intent_extend"])
    proposal = (
        _proposal() + "\nProject Authorization: `PAUTH-AUTH`\nProject: `PROJECT-AUTH`\nWork Item: `WI-AUTH-001`\n"
    )
    _write_thread(tmp_path, proposal=proposal)
    _claim_bridge(tmp_path)
    before = auth.bridge_work_intent_registry.current_holder("sample-implementation", project_root=tmp_path)

    with pytest.raises(
        auth.bridge_work_intent_registry.WorkIntentRegistryError,
        match="work_intent_extend",
    ):
        auth.bridge_work_intent_registry.extend("sample-implementation", "session-1", project_root=tmp_path)

    after = auth.bridge_work_intent_registry.current_holder("sample-implementation", project_root=tmp_path)
    assert after == before


def test_work_intent_renew_denial_leaves_go_claim_unchanged(tmp_path: Path) -> None:
    _seed_project_authorization(tmp_path, forbidden_operations=["work_intent_renew"])
    proposal = (
        _proposal() + "\nProject Authorization: `PAUTH-AUTH`\nProject: `PROJECT-AUTH`\nWork Item: `WI-AUTH-001`\n"
    )
    _write_thread(tmp_path, proposal=proposal)
    _claim_bridge(tmp_path)
    before = auth.bridge_work_intent_registry.current_holder("sample-implementation", project_root=tmp_path)

    with pytest.raises(
        auth.bridge_work_intent_registry.WorkIntentAuthorizationError,
        match="work_intent_renew",
    ):
        auth.bridge_work_intent_registry.acquire("sample-implementation", "session-1", project_root=tmp_path)

    after = auth.bridge_work_intent_registry.current_holder("sample-implementation", project_root=tmp_path)
    assert after == before


def test_work_intent_reclassify_denial_leaves_draft_claim_unchanged(
    tmp_path: Path,
) -> None:
    _seed_project_authorization(tmp_path, forbidden_operations=["work_intent_reclassify"])
    proposal = (
        _proposal() + "\nProject Authorization: `PAUTH-AUTH`\nProject: `PROJECT-AUTH`\nWork Item: `WI-AUTH-001`\n"
    )
    _write_thread(tmp_path, proposal=proposal, latest_status="NEW")
    _bind_prime_session(tmp_path, "session-1")
    assert auth.bridge_work_intent_registry.acquire("sample-implementation", "session-1", project_root=tmp_path)
    before = auth.bridge_work_intent_registry.current_holder("sample-implementation", project_root=tmp_path)
    (tmp_path / "bridge" / "sample-implementation-002.md").write_text(
        _go_verdict_body(),
        encoding="utf-8",
    )

    with pytest.raises(
        auth.bridge_work_intent_registry.WorkIntentAuthorizationError,
        match="work_intent_reclassify",
    ):
        auth.bridge_work_intent_registry.acquire("sample-implementation", "session-1", project_root=tmp_path)

    after = auth.bridge_work_intent_registry.current_holder("sample-implementation", project_root=tmp_path)
    assert after == before


def _write_amendment_packet(tmp_path: Path, filename: str, content: str) -> str:
    """Write a valid owner-approved formal-artifact-approval packet under the
    test project root and return the cited relative path. Required so a
    project-authorization spec amendment satisfies the WI-3313 amendment gate
    (DCL-PROJECT-SPECIFICATION-AMENDMENT-APPROVAL-REQUIRED-001)."""
    import json

    from groundtruth_kb.governance.approval_packet import content_hash

    packet_dir = tmp_path / ".groundtruth" / "formal-artifact-approvals"
    packet_dir.mkdir(parents=True, exist_ok=True)
    packet = {
        "artifact_type": "design_constraint",
        "artifact_id": "PAUTH-AUTH",
        "action": "amend",
        "source_ref": "owner conversation",
        "full_content": content,
        "full_content_sha256": content_hash(content),
        "approval_mode": "approve",
        "presented_to_user": True,
        "transcript_captured": True,
        "explicit_change_request": "owner authorizes the project-authorization spec amendment",
        "changed_by": "owner",
        "change_reason": "owner-approved amendment",
        "approved_by": "owner",
    }
    (packet_dir / filename).write_text(json.dumps(packet), encoding="utf-8")
    return f".groundtruth/formal-artifact-approvals/{filename}"


def test_project_authorization_load_revalidates_current_spec_exclusions(
    tmp_path: Path,
) -> None:
    _seed_project_authorization(tmp_path)
    proposal = (
        _proposal() + "\nProject Authorization: `PAUTH-AUTH`\nProject: `PROJECT-AUTH`\nWork Item: `WI-AUTH-001`\n"
    )
    _write_thread(tmp_path, proposal=proposal)
    packet = auth.create_authorization_packet(tmp_path, "sample-implementation")
    auth.write_packet(tmp_path, packet)

    db = KnowledgeDB(tmp_path / "groundtruth.db")
    try:
        # WI-3313 amendment gate: a spec-set amendment must cite an
        # owner-approved covering packet in change_reason. Fixture setup only;
        # the assertion below is unchanged.
        amendment_packet = _write_amendment_packet(
            tmp_path,
            "exclude-gov-spec.json",
            "Owner-approved amendment of project PROJECT-AUTH authorization "
            "PAUTH-AUTH excluding spec GOV-FILE-BRIDGE-AUTHORITY-001.",
        )
        db.update_project_authorization(
            "PAUTH-AUTH",
            "test",
            f"exclude linked governing spec per {amendment_packet}",
            excluded_spec_ids=["GOV-FILE-BRIDGE-AUTHORITY-001"],
        )
    finally:
        db.close()

    with pytest.raises(auth.AuthorizationError, match="Spec link\\(s\\) excluded"):
        auth.load_packet(tmp_path)


def test_project_authorization_does_not_broaden_target_scope(tmp_path: Path) -> None:
    _seed_project_authorization(tmp_path)
    proposal = (
        _proposal() + "\nProject Authorization: `PAUTH-AUTH`\nProject: `PROJECT-AUTH`\nWork Item: `WI-AUTH-001`\n"
    )
    _write_thread(tmp_path, proposal=proposal)
    packet = auth.create_authorization_packet(tmp_path, "sample-implementation")
    auth.write_packet(tmp_path, packet)

    with pytest.raises(auth.AuthorizationError, match="outside implementation authorization scope"):
        auth.validate_targets(tmp_path, ["groundtruth-kb/src/groundtruth_kb/db.py"])


def test_project_authorization_requires_work_item_membership_or_inclusion(
    tmp_path: Path,
) -> None:
    _seed_project_authorization(tmp_path, link_work_item=False)
    proposal = (
        _proposal() + "\nProject Authorization: `PAUTH-AUTH`\nProject: `PROJECT-AUTH`\nWork Item: `WI-AUTH-001`\n"
    )
    _write_thread(tmp_path, proposal=proposal)

    with pytest.raises(auth.AuthorizationError, match="not an active member of project"):
        auth.create_authorization_packet(tmp_path, "sample-implementation")


def test_target_outside_approved_proposal_paths_is_blocked(tmp_path: Path) -> None:
    """WI-7751: change scope is RETAINED and is now sourced from the proposal.

    v5 keeps change scope -- "change scope is the implementation proposal's declared
    target_paths" -- while retiring the packet that used to carry it. The scope is
    derived from the GO-approved proposal in the live chain instead, so an
    out-of-scope protected path is still refused, and the refusal names the
    approved set rather than a packet.
    """
    _write_thread(tmp_path)
    payload = {
        "cwd": str(tmp_path),
        "tool_name": "apply_patch",
        "tool_input": {
            "patch": "*** Begin Patch\n*** Update File: config/out-of-scope.toml\n@@\n+x=1\n*** End Patch\n"
        },
    }

    result = gate.gate_decision(payload)

    assert result["decision"] == "block"
    assert "target_paths" in result["reason"] or "work-intent claim" in result["reason"]


def test_bridge_status_file_write_blocks_without_governed_helper(
    tmp_path: Path,
) -> None:
    payload = {
        "cwd": str(tmp_path),
        "tool_name": "apply_patch",
        "tool_input": {"patch": "*** Begin Patch\n*** Add File: bridge/example-001.md\n+NEW\n*** End Patch\n"},
    }

    result = gate.gate_decision(payload)

    assert result["decision"] == "block"
    assert result["reason_code"] == "bridge_status_file_direct_mutation"
    assert "governed bridge" in result["reason"]


@pytest.mark.parametrize("path_key", ["path", "file_path"])
def test_raw_write_bridge_status_path_aliases_remain_direct_mutation_denials(tmp_path: Path, path_key: str) -> None:
    payload = {
        "cwd": str(tmp_path),
        "tool_name": "Write",
        "tool_input": {path_key: "bridge/provider-verdict-002.md", "content": "GO\n"},
    }

    result = gate.gate_decision(payload)

    assert result["decision"] == "block"
    assert result["reason_code"] == "bridge_status_file_direct_mutation"


def test_non_status_bridge_note_write_remains_open_without_authorization(
    tmp_path: Path,
) -> None:
    payload = {
        "cwd": str(tmp_path),
        "tool_name": "apply_patch",
        "tool_input": {"patch": "*** Begin Patch\n*** Add File: bridge/example-note.md\n+note\n*** End Patch\n"},
    }

    assert gate.gate_decision(payload) == {}


def test_raw_patch_bridge_status_and_index_write_blocks_without_authorization(
    tmp_path: Path,
) -> None:
    payload = {
        "cwd": str(tmp_path),
        "tool_name": "apply_patch",
        "tool_input": (
            "*** Begin Patch\n"
            "*** Add File: bridge/example-001.md\n"
            "+NEW\n"
            "*** Update File: bridge/INDEX.md\n"
            "@@\n"
            "+NEW: bridge/example-001.md\n"
            "*** End Patch\n"
        ),
    }

    assert gate.changed_paths(payload) == (
        ["bridge/example-001.md", "bridge/INDEX.md"],
        True,
    )
    result = gate.gate_decision(payload)
    assert result["decision"] == "block"
    assert result["reason_code"] == "controlled_artifact_direct_mutation"
    assert "bridge/<slug>-NNN.md" in result["reason"]
    assert "bridge/INDEX.md" in result["reason"]


def test_raw_patch_protected_write_blocks_without_authorization(tmp_path: Path) -> None:
    payload = {
        "cwd": str(tmp_path),
        "tool_name": "functions.apply_patch",
        "input": "*** Begin Patch\n*** Update File: scripts/sample.py\n@@\n+pass\n*** End Patch\n",
    }

    result = gate.gate_decision(payload)

    assert result["decision"] == "block"
    assert "authorization packet" in result["reason"]


def test_nested_patch_payload_without_tool_name_blocks_bridge_status_write(
    tmp_path: Path,
) -> None:
    payload = {
        "cwd": str(tmp_path),
        "event": "PreToolUse",
        "tool": "freeform",
        "tool_input": {
            "arguments": {"payload": ("*** Begin Patch\n*** Add File: bridge/example-002.md\n+NEW\n*** End Patch\n")}
        },
    }

    assert gate.changed_paths(payload) == (["bridge/example-002.md"], True)
    result = gate.gate_decision(payload)
    assert result["decision"] == "block"
    assert result["reason_code"] == "bridge_status_file_direct_mutation"


def test_shell_payload_with_escaped_patch_newlines_blocks_bridge_status_write(
    tmp_path: Path,
) -> None:
    payload = {
        "cwd": str(tmp_path),
        "tool_name": "Bash",
        "tool_input": {
            "command": ('$payload = "*** Begin Patch`n*** Add File: bridge/example-003.md`n+NEW`n*** End Patch`n"')
        },
    }

    assert gate.changed_paths(payload) == (["bridge/example-003.md"], True)
    result = gate.gate_decision(payload)
    assert result["decision"] == "block"
    assert result["reason_code"] == "bridge_status_file_direct_mutation"


def test_shell_mutation_classification_blocks_protected_write(tmp_path: Path) -> None:
    payload = {
        "cwd": str(tmp_path),
        "tool_name": "Bash",
        "tool_input": {"command": "Set-Content -Path scripts/sample.py -Value 'x'"},
    }

    result = gate.gate_decision(payload)

    assert result["decision"] == "block"
    assert "authorization packet" in result["reason"]


@pytest.mark.parametrize(
    ("path", "reason_code"),
    [
        ("groundtruth.db", "membase_direct_mutation"),
        (
            ".gtkb-state/implementation-authorizations/current.json",
            "runtime_authority_state_direct_mutation",
        ),
        (
            ".gtkb-state/work-intent/thread.json",
            "runtime_authority_state_direct_mutation",
        ),
        (
            ".gtkb-state/bridge-poller/dispatch-state.json",
            "runtime_authority_state_direct_mutation",
        ),
        (
            ".gtkb-state/dispatcher-daemon/status.json",
            "runtime_authority_state_direct_mutation",
        ),
    ],
)
def test_shell_mutation_blocks_controlled_authority_state(path: str, reason_code: str, tmp_path: Path) -> None:
    payload = {
        "cwd": str(tmp_path),
        "tool_name": "Bash",
        "tool_input": {"command": f"Set-Content -Path {path} -Value 'x'"},
    }

    result = gate.gate_decision(payload)

    assert result["decision"] == "block"
    assert result["reason_code"] == reason_code
    assert "controlled artifact" in result["reason"]


def test_registered_memory_mutation_requires_authorization(tmp_path: Path) -> None:
    payload = {
        "cwd": str(tmp_path),
        "tool_name": "Bash",
        "tool_input": {"command": "Set-Content -Path memory/pending-owner-decisions.md -Value 'x'"},
    }

    assert gate.changed_paths(payload) == (["memory/pending-owner-decisions.md"], True)
    result = gate.gate_decision(payload)
    assert result["decision"] == "block"
    assert "registry:pending-owner-decisions" in result["reason"]


def test_deliberation_search_query_with_patch_word_is_allowed_without_authorization(
    tmp_path: Path,
) -> None:
    payload = {
        "cwd": str(tmp_path),
        "tool_name": "Bash",
        "tool_input": {
            "command": (
                "$env:PYTHONPATH='groundtruth-kb/src'; "
                "python -m groundtruth_kb deliberations search "
                '"implementation start authorization gate apply_patch bridge only" --limit 8 --json'
            )
        },
    }

    assert gate.gate_decision(payload) == {}


def test_read_only_shell_command_is_allowed_without_authorization(
    tmp_path: Path,
) -> None:
    payload = {
        "cwd": str(tmp_path),
        "tool_name": "Bash",
        "tool_input": {"command": 'rg -n "hello" scripts/sample.py'},
    }

    assert gate.gate_decision(payload) == {}


@pytest.mark.parametrize(
    "command",
    [
        "python -m pytest platform_tests/scripts/test_sample.py -q",
        "git status --short",
        'rg -n "hello" scripts/sample.py',
    ],
)
def test_structurally_single_read_only_commands_remain_allowed(command: str, tmp_path: Path) -> None:
    payload = {
        "cwd": str(tmp_path),
        "tool_name": "Bash",
        "tool_input": {"command": command},
    }

    assert gate._is_safe_command(command) is True
    assert gate.gate_decision(payload) == {}


@pytest.mark.parametrize(
    ("command", "reason_code"),
    [
        (
            "python -m pytest -q; Set-Content -Path scripts/bypass.py -Value x",
            "authorization",
        ),
        (
            "git status; git add scripts/bypass.py",
            "direct_git_effect_requires_lifecycle",
        ),
    ],
)
def test_safe_prefix_does_not_exempt_appended_mutating_stage(command: str, reason_code: str, tmp_path: Path) -> None:
    payload = {
        "cwd": str(tmp_path),
        "tool_name": "Bash",
        "tool_input": {"command": command},
    }

    assert gate._is_safe_command(command) is False
    paths, mutating = gate.changed_paths(payload)
    assert mutating is True
    assert "scripts/bypass.py" in paths
    result = gate.gate_decision(payload)
    assert result["decision"] == "block"
    if reason_code == "authorization":
        assert "authorization packet" in result["reason"]
    else:
        assert result["reason_code"] == reason_code


@pytest.mark.parametrize(
    "subcommand",
    ["create", "attach", "preserve", "promote", "close", "resume", "recover", "drain"],
)
def test_git_lifecycle_mutating_subcommands_are_mutation_signals(
    subcommand: str,
) -> None:
    command = f"python -m groundtruth_kb.git_lifecycle --repo . {subcommand} --fixture-argument x"

    assert gate._has_mutating_git_lifecycle_signal(command) is True
    assert gate._is_mutating_command(command) is True


def test_git_lifecycle_preserve_requires_implementation_authority(
    tmp_path: Path,
) -> None:
    command = (
        'python -m groundtruth_kb.git_lifecycle --repo . preserve --work-item-id WI-TEST --message "preserve test"'
    )
    payload = {
        "cwd": str(tmp_path),
        "tool_name": "Bash",
        "tool_input": {"command": command},
    }

    assert gate.changed_paths(payload) == ([], True)
    result = gate.gate_decision(payload)
    assert result["decision"] == "block"
    assert "authorization packet" in result["reason"]


@pytest.mark.parametrize("hook_input", ["", "{}", "[]", "{malformed-json"])
def test_hook_denies_empty_or_malformed_json_payload(
    hook_input: str,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.setattr(sys, "stdin", io.StringIO(hook_input))
    monkeypatch.setattr(gate, "_record_gate_denial", lambda *_args, **_kwargs: None)

    assert gate.main() == 0
    output = json.loads(capsys.readouterr().out)
    hook_output = output["hookSpecificOutput"]
    assert hook_output["permissionDecision"] == "deny"
    assert "payload" in hook_output["permissionDecisionReason"].lower()


@pytest.mark.parametrize(
    ("command", "subcommand"),
    [
        ('git commit -m "feat(gtkb): finalize verified bridge work"', "commit"),
        ('git commit -m "literal ; | && message punctuation"', "commit"),
        ("git commit --amend --no-edit", "commit"),
        ('git -C . commit -m "scoped change"', "commit"),
        ('git -c user.name="GT-KB" commit -m "scoped change"', "commit"),
        ("git push origin develop", "push"),
        ("git.exe push --porcelain origin HEAD", "push"),
        ("git --git-dir=.git push --force-with-lease origin HEAD", "push"),
        ("git switch -c bypass", "switch"),
        ("git branch bypass", "branch"),
        ("git cherry-pick HEAD~1", "cherry-pick"),
        ("git revert HEAD", "revert"),
        ("git update-ref refs/heads/main HEAD", "update-ref"),
        ("git clean -fd", "clean"),
        ("git worktree add ../bypass", "worktree"),
        ("git checkout -b bypass", "checkout"),
        ("git config user.name bypass", "config"),
        ("git fetch origin", "fetch"),
    ],
)
def test_direct_git_effects_require_lifecycle_command(
    tmp_path: Path,
    command: str,
    subcommand: str,
) -> None:
    payload = {
        "cwd": str(tmp_path),
        "tool_name": "Bash",
        "tool_input": {"command": command},
    }

    assert gate.changed_paths(payload) == ([], True)
    result = gate.gate_decision(payload)

    assert result["decision"] == "block"
    assert result["reason_code"] == "direct_git_effect_requires_lifecycle"
    assert f"git {subcommand}" in result["reason"]
    assert "python -m groundtruth_kb.git_lifecycle" in result["reason"]


@pytest.mark.parametrize(
    ("command", "subcommand"),
    [
        ('cmd /c "git.exe commit -m nested"', "commit"),
        ('cmd.exe /s /c "git.exe push origin HEAD"', "push"),
        ('powershell.exe -NoProfile -Command "git.exe commit -m nested"', "commit"),
        ('pwsh -c "& git.exe push origin HEAD"', "push"),
        ('bash -c "git commit -m nested"', "commit"),
        ("Write-Output inspected\ngit.exe commit -m nested", "commit"),
    ],
)
def test_shell_wrapped_direct_git_effects_require_lifecycle(
    tmp_path: Path,
    command: str,
    subcommand: str,
) -> None:
    payload = {
        "cwd": str(tmp_path),
        "tool_name": "Shell",
        "tool_input": {"command": command},
    }

    result = gate.gate_decision(payload)

    assert result["decision"] == "block"
    assert result["reason_code"] == "direct_git_effect_requires_lifecycle"
    assert f"git {subcommand}" in result["reason"]


@pytest.mark.parametrize(
    "command",
    [
        "powershell.exe -EncodedCommand ZgBvAG8A",
        "pwsh -Command",
        "cmd.exe /c",
        "bash -c",
    ],
)
def test_uninspectable_nested_shell_commands_fail_closed(tmp_path: Path, command: str) -> None:
    payload = {
        "cwd": str(tmp_path),
        "tool_name": "Shell",
        "tool_input": {"command": command},
    }

    result = gate.gate_decision(payload)

    assert result["decision"] == "block"
    assert result["reason_code"] == "direct_git_effect_requires_lifecycle"


@pytest.mark.parametrize(
    "command",
    [
        "cmd /c git.exe status --short",
        'powershell.exe -Command "git.exe diff --stat"',
        'bash -c "git log -1"',
    ],
)
def test_shell_wrapped_read_only_git_commands_remain_allowed(tmp_path: Path, command: str) -> None:
    payload = {
        "cwd": str(tmp_path),
        "tool_name": "Shell",
        "tool_input": {"command": command},
    }

    assert gate.gate_decision(payload) == {}


@pytest.mark.parametrize(
    ("tool_name", "tool_input", "subcommand"),
    [
        ("Shell", {"command": ["git", "commit", "--amend", "--no-edit"]}, "commit"),
        ("git", {"argv": ["push", "origin", "HEAD"]}, "push"),
        ("git.exe", {"args": ["-C", ".", "commit", "-m", "shell-free"]}, "commit"),
    ],
)
def test_shell_free_direct_git_effect_payloads_fail_closed(
    tmp_path: Path,
    tool_name: str,
    tool_input: dict[str, object],
    subcommand: str,
) -> None:
    payload = {"cwd": str(tmp_path), "tool_name": tool_name, "tool_input": tool_input}

    result = gate.gate_decision(payload)

    assert result["decision"] == "block"
    assert result["reason_code"] == "direct_git_effect_requires_lifecycle"
    assert f"git {subcommand}" in result["reason"]


@pytest.mark.parametrize(
    "tool_input",
    [
        {"argv": ["status", "--short"]},
        {"args": ["-C", ".", "diff", "--stat"]},
    ],
)
def test_shell_free_read_only_git_commands_remain_allowed(
    tmp_path: Path,
    tool_input: dict[str, object],
) -> None:
    payload = {"cwd": str(tmp_path), "tool_name": "git", "tool_input": tool_input}

    assert gate.gate_decision(payload) == {}


def test_direct_git_effect_cannot_be_enabled_by_implementation_packet(
    tmp_path: Path,
) -> None:
    _seed_project_authorization(tmp_path)
    _write_thread(tmp_path, proposal=_pauth_proposal())
    packet = auth.create_authorization_packet(tmp_path, "sample-implementation")
    auth.write_packet(tmp_path, packet)
    _claim_bridge(tmp_path)
    payload = {
        "cwd": str(tmp_path),
        "session_id": "session-1",
        "tool_name": "Bash",
        "tool_input": {"command": 'git commit -m "must use lifecycle"'},
    }

    result = gate.gate_decision(payload)

    assert result["decision"] == "block"
    assert result["reason_code"] == "direct_git_effect_requires_lifecycle"


def test_canonical_git_lifecycle_command_reaches_authorization_boundary(
    tmp_path: Path,
) -> None:
    command = 'python -m groundtruth_kb.git_lifecycle preserve --work-item-id WI-TEST --message "preserve test"'
    payload = {
        "cwd": str(tmp_path),
        "tool_name": "Bash",
        "tool_input": {"command": command},
    }

    assert gate._direct_git_effect_from_payload(payload) is None
    result = gate.gate_decision(payload)

    assert result["decision"] == "block"
    assert result.get("reason_code") != "direct_git_effect_requires_lifecycle"
    assert "authorization packet" in result["reason"]


def test_chained_git_commit_with_protected_write_still_blocks(tmp_path: Path) -> None:
    payload = {
        "cwd": str(tmp_path),
        "tool_name": "Bash",
        "tool_input": {"command": 'git commit -m "x"; Set-Content -Path scripts/sample.py -Value "x"'},
    }

    result = gate.gate_decision(payload)

    assert result["decision"] == "block"
    assert result["reason_code"] == "direct_git_effect_requires_lifecycle"


def test_gate_uses_unique_named_packet_when_current_json_absent(tmp_path: Path) -> None:
    """WI-4452: a unique valid named packet can authorize the protected target."""
    _seed_project_authorization(tmp_path)
    _write_thread(tmp_path, proposal=_pauth_proposal())
    packet = auth.create_authorization_packet(tmp_path, "sample-implementation")

    named_path = auth.write_named_packet(tmp_path, packet, "sample-implementation")
    _claim_bridge(tmp_path)
    assert named_path.is_file(), "test setup: named packet must be on disk"
    assert not auth.packet_path(tmp_path).is_file(), (
        "test setup: current.json must be absent so any positive gate decision comes from the unique by-bridge packet"
    )

    payload = {
        "cwd": str(tmp_path),
        "session_id": "session-1",
        "tool_name": "apply_patch",
        "tool_input": {"patch": ("*** Begin Patch\n*** Update File: scripts/sample.py\n@@\n+pass\n*** End Patch\n")},
    }

    assert gate.gate_decision(payload) == {}


def test_gate_blocks_ambiguous_named_packet_fallback(tmp_path: Path) -> None:
    """WI-4452: overlapping named packets fail closed instead of guessing."""
    shared_target = "scripts/sample.py"
    _write_thread(
        tmp_path,
        bridge_id="bridge-a",
        proposal=_proposal(bridge_id="bridge-a", target_paths=[shared_target]),
    )
    bridge = tmp_path / "bridge"
    (bridge / "bridge-b-001.md").write_text(
        _proposal(bridge_id="bridge-b", target_paths=[shared_target]),
        encoding="utf-8",
    )
    (bridge / "bridge-b-002.md").write_text(_go_verdict_body("bridge-b"), encoding="utf-8")
    (bridge / "INDEX.md").write_text(
        "\n".join(
            [
                "Document: bridge-a",
                "GO: bridge/bridge-a-002.md",
                "NEW: bridge/bridge-a-001.md",
                "",
                "Document: bridge-b",
                "GO: bridge/bridge-b-002.md",
                "NEW: bridge/bridge-b-001.md",
                "",
            ]
        ),
        encoding="utf-8",
    )
    packet_a = auth.create_authorization_packet(tmp_path, "bridge-a")
    packet_b = auth.create_authorization_packet(tmp_path, "bridge-b")
    auth.write_named_packet(tmp_path, packet_a, "bridge-a")
    auth.write_named_packet(tmp_path, packet_b, "bridge-b")
    assert not auth.packet_path(tmp_path).is_file()

    payload = {
        "cwd": str(tmp_path),
        "tool_name": "apply_patch",
        "tool_input": {"patch": ("*** Begin Patch\n*** Update File: scripts/sample.py\n@@\n+pass\n*** End Patch\n")},
    }

    result = gate.gate_decision(payload)

    # WI-7751: the WI-4452 invariant survives, its mechanism does not.
    # Two threads declaring the same target used to collide in the named-packet
    # fallback, which resolved authority by guessing among packets. That fallback is
    # retired with the packet. The invariant -- overlapping scope fails closed rather
    # than being resolved by guesswork -- is now carried by the RETAINED controls:
    # no session holds a claim here, so the gate refuses before any scope question
    # arises. The two bridge ids are no longer named in the reason because the gate
    # never disambiguates between them; refusing to choose IS the fixed behaviour.
    assert result.get("decision") == "block"
    assert "work-intent claim" in result.get("reason", "")


# IP-A: Null-sink redirect classifier tests (F1 closures)


def test_gate_allows_stderr_redirect_to_dev_null() -> None:
    assert gate._is_mutating_command("python script.py 2>/dev/null") is False


def test_gate_allows_stderr_redirect_to_powershell_null() -> None:
    assert gate._is_mutating_command("python script.py 2>$null") is False


def test_gate_allows_stderr_redirect_to_windows_nul() -> None:
    assert gate._is_mutating_command("python script.py 2>NUL") is False


def test_gate_blocks_unnumbered_redirect_to_file() -> None:
    assert gate._is_mutating_command("cmd > out.txt") is True


def test_gate_blocks_stderr_numbered_redirect_to_real_file() -> None:
    assert gate._is_mutating_command("cmd 2> err.txt") is True


def test_gate_blocks_stdout_numbered_redirect_to_file() -> None:
    assert gate._is_mutating_command("cmd 1> out.txt") is True


def test_gate_blocks_combined_redirect_to_file() -> None:
    assert gate._is_mutating_command("cmd &> out.txt") is True


# WI-3317: MUTATING_COMMAND_RE format-spec false-positive fix.
# The redirect alternation (?<![:>-])>{1,2}(?![&]) must NOT flag Python
# format-spec right-alignment (:>) or arrow tokens (->), while still
# flagging every real shell redirect form.


def test_gate_allows_python_format_spec_right_align() -> None:
    # `:>` is Python format-spec right alignment, not a shell redirect.
    assert gate._is_mutating_command("python -c \"print(f'{n:>2}')\"") is False


def test_gate_allows_python_arrow_token() -> None:
    # `->` is a Python return-annotation arrow, not a shell redirect.
    assert gate._is_mutating_command('python -c "def f() -> int: return 1"') is False


def test_gate_blocks_append_redirect_to_file() -> None:
    assert gate._is_mutating_command("cmd >> out.txt") is True


def test_gate_blocks_no_space_redirect_to_file() -> None:
    # A redirect with no space before `>` is still a real file write.
    assert gate._is_mutating_command("cmd>out.txt") is True


# WI-3356: MUTATING_COMMAND_RE comparison-operator false-positive fix.
# The redirect alternation's trailing lookahead (?![>&=]) must NOT flag a
# Python `>=` comparison or `>>=` augmented-assignment operator, while still
# flagging every real shell redirect form.


def test_gate_allows_python_ge_comparison() -> None:
    # `>=` is a Python comparison operator, not a shell redirect.
    assert gate._is_mutating_command('python -c "print(1 if i>=0 else 2)"') is False


def test_gate_allows_python_ge_comparison_with_spaces() -> None:
    # A spaced `>=` comparison is still not a shell redirect.
    assert gate._is_mutating_command('python -c "assert x >= 0"') is False


def test_gate_allows_python_rshift_augmented_assignment() -> None:
    # `>>=` is the Python augmented right-shift assignment operator.
    assert gate._is_mutating_command('python -c "x=8; x>>=2; print(x)"') is False


# IP-B/F3: sqlite safe-read tests


def test_gate_allows_python_sqlite_select_read() -> None:
    cmd = "python -c \"import sqlite3; sqlite3.connect('a.db').execute('SELECT COUNT(*) FROM t').fetchone()\""
    assert gate._is_mutating_command(cmd) is False


def test_gate_allows_python_sqlite_with_read() -> None:
    cmd = (
        'python -c "import sqlite3; '
        "sqlite3.connect('a.db').execute('WITH cte AS (SELECT id FROM t) SELECT * FROM cte')\""
    )
    assert gate._is_mutating_command(cmd) is False


def test_gate_blocks_python_sqlite_pragma_function_call_form() -> None:
    cmd = "python -c \"import sqlite3; sqlite3.connect('a.db').execute('PRAGMA table_info(t)')\""
    assert gate._is_mutating_command(cmd) is True


def test_gate_blocks_python_sqlite_pragma_assignment() -> None:
    cmd = "python -c \"import sqlite3; sqlite3.connect('a.db').execute('PRAGMA journal_mode = WAL')\""
    assert gate._is_mutating_command(cmd) is True


def test_gate_blocks_python_sqlite_user_version_assignment() -> None:
    cmd = "python -c \"import sqlite3; sqlite3.connect('a.db').execute('PRAGMA user_version = 7')\""
    assert gate._is_mutating_command(cmd) is True


def test_gate_blocks_python_sqlite_literal_insert() -> None:
    cmd = "python -c \"import sqlite3; sqlite3.connect('a.db').execute('INSERT INTO t VALUES (1)')\""
    assert gate._is_mutating_command(cmd) is True


def test_gate_blocks_python_sqlite_commit_after_select() -> None:
    cmd = "python -c \"import sqlite3; c=sqlite3.connect('a.db'); c.execute('SELECT * FROM t'); c.commit()\""
    assert gate._is_mutating_command(cmd) is True


# WI-3358: quoted-argument Python mutation text is data, not shell intent.


@pytest.mark.parametrize(
    "cmd",
    [
        "python -c 'msg = \"sqlite3.connect(a.db).execute(INSERT INTO t VALUES (1))\"; print(msg)'",
        "python -c 'msg = \"Path(x).write_text(y)\"; print(msg)'",
        'python -c \'msg = """open(x, "w")"""; print(msg)\'',
    ],
)
def test_gate_allows_quoted_python_mutation_literals(cmd: str, tmp_path: Path) -> None:
    payload = {
        "cwd": str(tmp_path),
        "tool_name": "Bash",
        "tool_input": {"command": cmd},
    }

    assert gate._is_mutating_command(cmd) is False
    assert gate.gate_decision(payload) == {}


# WI-4471: cross-claim path-collision check — gate blocks when a different session's
# active work-intent claim+packet reserves the same target path.


def test_gate_blocks_when_other_session_claim_packet_reserves_target(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """WI-4471: gate blocks when another session's active claim+packet reserves the target."""
    monkeypatch.setenv("GTKB_BRIDGE_POLLER_RUN_ID", "session-A")
    shared_target = "scripts/shared.py"
    _seed_project_authorization(tmp_path)
    bridge = tmp_path / "bridge"
    bridge.mkdir()
    (bridge / "bridge-a-001.md").write_text(
        _pauth_proposal(bridge_id="bridge-a", target_paths=[shared_target]),
        encoding="utf-8",
    )
    (bridge / "bridge-a-002.md").write_text(_go_verdict_body("bridge-a"), encoding="utf-8")
    (bridge / "bridge-b-001.md").write_text(
        _pauth_proposal(bridge_id="bridge-b", target_paths=[shared_target], work_item="WI-AUTH-002"),
        encoding="utf-8",
    )
    (bridge / "bridge-b-002.md").write_text(_go_verdict_body("bridge-b"), encoding="utf-8")
    (bridge / "INDEX.md").write_text(
        "Document: bridge-a\nGO: bridge/bridge-a-002.md\nNEW: bridge/bridge-a-001.md\n\n"
        "Document: bridge-b\nGO: bridge/bridge-b-002.md\nNEW: bridge/bridge-b-001.md\n",
        encoding="utf-8",
    )
    packet_a = auth.create_authorization_packet(tmp_path, "bridge-a")
    auth.write_packet(tmp_path, packet_a)
    auth.write_named_packet(tmp_path, packet_a, "bridge-a")
    packet_b = auth.create_authorization_packet(tmp_path, "bridge-b")
    auth.write_packet(tmp_path, packet_b)
    auth.write_named_packet(tmp_path, packet_b, "bridge-b")
    _claim_bridge(tmp_path, "bridge-a", "session-A")
    _claim_bridge(tmp_path, "bridge-b", "session-B")

    result = gate.gate_decision(_apply_patch_payload(tmp_path, target=shared_target, session_id="session-A"))

    assert result["decision"] == "block"
    assert "bridge-b" in result["reason"]
    assert "session-B" in result["reason"]


def test_gate_allows_when_no_other_session_reserves_target(tmp_path: Path) -> None:
    """WI-4471: no cross-claim collision when no other active named packet overlaps the target."""
    _seed_project_authorization(tmp_path)
    _write_thread(tmp_path, proposal=_pauth_proposal())
    packet = auth.create_authorization_packet(tmp_path, "sample-implementation")
    auth.write_packet(tmp_path, packet)
    auth.write_named_packet(tmp_path, packet, "sample-implementation")
    _claim_bridge(tmp_path)

    assert gate.gate_decision(_apply_patch_payload(tmp_path)) == {}


def test_collision_ignores_expired_claim_for_overlapping_packet(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """WI-4471: expired/lapsed claim does not trigger a cross-claim collision."""
    monkeypatch.setenv("GTKB_BRIDGE_POLLER_RUN_ID", "session-A")
    shared_target = "scripts/shared.py"
    _seed_project_authorization(tmp_path)
    bridge = tmp_path / "bridge"
    bridge.mkdir()
    (bridge / "bridge-a-001.md").write_text(
        _pauth_proposal(bridge_id="bridge-a", target_paths=[shared_target]),
        encoding="utf-8",
    )
    (bridge / "bridge-a-002.md").write_text(_go_verdict_body("bridge-a"), encoding="utf-8")
    (bridge / "bridge-b-001.md").write_text(
        _pauth_proposal(bridge_id="bridge-b", target_paths=[shared_target], work_item="WI-AUTH-002"),
        encoding="utf-8",
    )
    (bridge / "bridge-b-002.md").write_text(_go_verdict_body("bridge-b"), encoding="utf-8")
    (bridge / "INDEX.md").write_text(
        "Document: bridge-a\nGO: bridge/bridge-a-002.md\nNEW: bridge/bridge-a-001.md\n\n"
        "Document: bridge-b\nGO: bridge/bridge-b-002.md\nNEW: bridge/bridge-b-001.md\n",
        encoding="utf-8",
    )
    packet_a = auth.create_authorization_packet(tmp_path, "bridge-a")
    auth.write_packet(tmp_path, packet_a)
    auth.write_named_packet(tmp_path, packet_a, "bridge-a")
    packet_b = auth.create_authorization_packet(tmp_path, "bridge-b")
    auth.write_packet(tmp_path, packet_b)
    auth.write_named_packet(tmp_path, packet_b, "bridge-b")
    _claim_bridge(tmp_path, "bridge-a", "session-A")
    _claim_bridge(tmp_path, "bridge-b", "session-B")
    # Expire bridge-b's claim so current_holder returns None.
    conn = auth.bridge_work_intent_registry._get_conn(tmp_path)
    try:
        with conn:
            conn.execute(
                "UPDATE work_intent_claims"
                " SET ttl_expires_at = ?, implementation_grace_expires_at = ?"
                " WHERE thread_slug = ?",
                ("2026-01-01T00:00:00Z", "2026-01-01T00:00:00Z", "bridge-b"),
            )
    finally:
        conn.close()

    assert gate.gate_decision(_apply_patch_payload(tmp_path, target=shared_target, session_id="session-A")) == {}


def test_collision_ignores_same_session_overlapping_claim(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """WI-4471: same-session overlapping claim is not a collision (legitimate multi-thread)."""
    monkeypatch.setenv("GTKB_BRIDGE_POLLER_RUN_ID", "session-A")
    shared_target = "scripts/shared.py"
    _seed_project_authorization(tmp_path)
    bridge = tmp_path / "bridge"
    bridge.mkdir()
    (bridge / "bridge-a-001.md").write_text(
        _pauth_proposal(bridge_id="bridge-a", target_paths=[shared_target]),
        encoding="utf-8",
    )
    (bridge / "bridge-a-002.md").write_text(_go_verdict_body("bridge-a"), encoding="utf-8")
    (bridge / "bridge-b-001.md").write_text(
        _pauth_proposal(bridge_id="bridge-b", target_paths=[shared_target], work_item="WI-AUTH-002"),
        encoding="utf-8",
    )
    (bridge / "bridge-b-002.md").write_text(_go_verdict_body("bridge-b"), encoding="utf-8")
    (bridge / "INDEX.md").write_text(
        "Document: bridge-a\nGO: bridge/bridge-a-002.md\nNEW: bridge/bridge-a-001.md\n\n"
        "Document: bridge-b\nGO: bridge/bridge-b-002.md\nNEW: bridge/bridge-b-001.md\n",
        encoding="utf-8",
    )
    packet_a = auth.create_authorization_packet(tmp_path, "bridge-a")
    auth.write_packet(tmp_path, packet_a)
    auth.write_named_packet(tmp_path, packet_a, "bridge-a")
    packet_b = auth.create_authorization_packet(tmp_path, "bridge-b")
    auth.write_packet(tmp_path, packet_b)
    auth.write_named_packet(tmp_path, packet_b, "bridge-b")
    # Same session holds both claims.
    _claim_bridge(tmp_path, "bridge-a", "session-A")
    _claim_bridge(tmp_path, "bridge-b", "session-A")

    assert gate.gate_decision(_apply_patch_payload(tmp_path, target=shared_target, session_id="session-A")) == {}


def test_gate_blocks_when_other_session_glob_packet_reserves_target(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """WI-4996: a peer packet glob reserves matching concrete protected edits."""
    monkeypatch.setenv("GTKB_BRIDGE_POLLER_RUN_ID", "session-A")
    concrete_target = "scripts/dispatcher_runtime.py"
    _seed_project_authorization(tmp_path)
    bridge = tmp_path / "bridge"
    bridge.mkdir()
    (bridge / "bridge-a-001.md").write_text(
        _pauth_proposal(bridge_id="bridge-a", target_paths=[concrete_target]),
        encoding="utf-8",
    )
    (bridge / "bridge-a-002.md").write_text(_go_verdict_body("bridge-a"), encoding="utf-8")
    (bridge / "bridge-b-001.md").write_text(
        _pauth_proposal(bridge_id="bridge-b", target_paths=["scripts/*.py"], work_item="WI-AUTH-002"),
        encoding="utf-8",
    )
    (bridge / "bridge-b-002.md").write_text(_go_verdict_body("bridge-b"), encoding="utf-8")
    (bridge / "INDEX.md").write_text(
        "Document: bridge-a\nGO: bridge/bridge-a-002.md\nNEW: bridge/bridge-a-001.md\n\n"
        "Document: bridge-b\nGO: bridge/bridge-b-002.md\nNEW: bridge/bridge-b-001.md\n",
        encoding="utf-8",
    )
    packet_a = auth.create_authorization_packet(tmp_path, "bridge-a")
    auth.write_packet(tmp_path, packet_a)
    auth.write_named_packet(tmp_path, packet_a, "bridge-a")
    packet_b = auth.create_authorization_packet(tmp_path, "bridge-b")
    auth.write_packet(tmp_path, packet_b)
    auth.write_named_packet(tmp_path, packet_b, "bridge-b")
    _claim_bridge(tmp_path, "bridge-a", "session-A")
    _claim_bridge(tmp_path, "bridge-b", "session-B")

    result = gate.gate_decision(_apply_patch_payload(tmp_path, target=concrete_target, session_id="session-A"))

    assert result["decision"] == "block"
    assert "bridge-b" in result["reason"]
    assert concrete_target in result["reason"]


@pytest.mark.parametrize(
    "cmd",
    [
        "python -c \"from pathlib import Path; Path('scripts/foo.py').write_text('x')\"",
        "python -c \"open('scripts/foo.py', 'w').write('x')\"",
        "python -c \"import sqlite3; sqlite3.connect('a.db').execute('INSERT INTO t VALUES (1)')\"",
        "python -c \"db.insert_work_item('WI-1')\"",
    ],
)
def test_gate_preserves_python_mutation_true_positives(cmd: str, tmp_path: Path) -> None:
    payload = {
        "cwd": str(tmp_path),
        "tool_name": "Bash",
        "tool_input": {"command": cmd},
    }

    assert gate._is_mutating_command(cmd) is True
    result = gate.gate_decision(payload)
    assert result["decision"] == "block"
    assert "authorization packet" in result["reason"]


def test_gate_allows_bridge_write_with_quoted_protected_path_mention(
    tmp_path: Path,
) -> None:
    cmd = 'Set-Content -Path bridge/note.md -Value "reminder: update scripts/secret.py"'
    payload = {
        "cwd": str(tmp_path),
        "tool_name": "Bash",
        "tool_input": {"command": cmd},
    }

    assert gate.changed_paths(payload) == (["bridge/note.md"], True)
    assert gate.gate_decision(payload) == {}


# WI-3353 IP-3: worktree-aware canonical-root resolution closes Bug 2 (the
# silent enforcement escape) for a worktree session editing a canonical file.


def _build_worktree_project(tmp_path: Path) -> tuple[Path, Path]:
    """Build a synthetic GT-KB canonical checkout with a linked worktree under
    .claude/worktrees/test-wt. Returns (canonical_root, worktree_root). The
    worktree carries its own committed groundtruth.toml. Requires git.
    """
    ident = [
        "-c",
        "user.email=test@example.com",
        "-c",
        "user.name=test",
        "-c",
        "commit.gpgsign=false",
    ]
    canonical = tmp_path / "canonical"
    canonical.mkdir()
    (canonical / "groundtruth.toml").write_text("# synthetic GT-KB root\n", encoding="utf-8")
    subprocess.run(["git", "init"], cwd=canonical, check=True, capture_output=True)
    subprocess.run(
        ["git", *ident, "add", "groundtruth.toml"],
        cwd=canonical,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", *ident, "commit", "-m", "init"],
        cwd=canonical,
        check=True,
        capture_output=True,
    )
    worktree = canonical / ".claude" / "worktrees" / "test-wt"
    worktree.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        ["git", *ident, "worktree", "add", "--detach", str(worktree)],
        cwd=canonical,
        check=True,
        capture_output=True,
    )
    return canonical, worktree


def test_start_gate_enforces_canonical_edit_from_worktree(tmp_path: Path) -> None:
    """WI-3353 IP-3 (Bug 2 closure): a worktree session editing a canonical file
    by absolute path is classified as a protected-path edit and gated. Before
    the fix the gate trusted payload['cwd'] (the worktree), normalize_relative_path
    raised 'Path escapes project root', is_protected_path silently returned
    False, and the gate emitted no decision -- a silent enforcement escape."""
    if shutil.which("git") is None:
        pytest.skip("git not available on this system")
    canonical, worktree = _build_worktree_project(tmp_path)
    payload = {
        "cwd": str(worktree),
        "tool_name": "Write",
        "tool_input": {"file_path": str(canonical / "scripts" / "sample.py")},
    }
    result = gate.gate_decision(payload)
    assert result.get("decision") == "block", (
        "the implementation-start gate must enforce against a canonical-by-"
        "absolute-path edit from a worktree session, not silently escape"
    )
    assert "authorization packet" in result.get("reason", "")


# WI-3357 regression corpus for quote-aware command parsing. Cases derive from
# the Specification-Derived Verification
# Plan in bridge/gtkb-impl-start-gate-finalization-quoting-fix-007.md, plus the
# -008 review's non-blocking observations (multi-cat / CRLF / unquoted shapes).
# In a command string, \n is a literal newline; HEREDOC commands span lines.


_WI3357_GATE_CASES = [
    # Direct commit/push effects always block, regardless of message syntax.
    (
        "01-chaining-markers-block",
        'git commit -m "fix X; tidy | done && wrap"',
        "block",
    ),
    ("03-heredoc-block", "git commit -m \"$(cat <<'EOF'\nmsg body\nEOF\n)\"", "block"),
    (
        "05-cmdsub-protected-write-blocks",
        'git commit -m "$(Set-Content -Path scripts/sample.py -Value z)"',
        "block",
    ),
    (
        "06-backtick-protected-write-blocks",
        'git commit -m "`Set-Content -Path scripts/sample.py -Value z`"',
        "block",
    ),
    ("07-cmdsub-non-heredoc-blocks", 'git commit -m "$(cat msg.txt)"', "block"),
    (
        "08-heredoc-unquoted-delim-blocks",
        'git commit -m "$(cat <<EOF\nmsg\nEOF\n)"',
        "block",
    ),
    (
        "09-heredoc-non-cat-blocks",
        "git commit -m \"$(rm scripts/sample.py <<'EOF'\nx\nEOF\n)\"",
        "block",
    ),
    (
        "12-chained-protected-write-blocks",
        'git commit -m "fix; tidy"; Set-Content -Path scripts/sample.py -Value "z"',
        "block",
    ),
    (
        "13-chained-after-heredoc-blocks",
        "git commit -m \"$(cat <<'EOF'\nmsg\nEOF\n)\" && Set-Content -Path scripts/sample.py -Value z",
        "block",
    ),
    ("14-plain-push-block", "git push origin develop", "block"),
    (
        "16-early-delimiter-blocks",
        "git commit -m \"$(cat <<'EOF'\nmsg\nEOF\nSet-Content -Path scripts/sample.py -Value z\nEOF\n)\"",
        "block",
    ),
    (
        "17-early-delimiter-separator-blocks",
        "git commit -m \"$(cat <<'EOF'\nmsg\nEOF\n; Set-Content -Path scripts/sample.py -Value z\nEOF\n)\"",
        "block",
    ),
    (
        "18-opener-redirect-tail-blocks",
        "git commit -m \"$(cat <<'EOF' > scripts/sample.py\nmsg\nEOF\n)\"",
        "block",
    ),
    (
        "19-opener-separator-tail-blocks",
        "git commit -m \"$(cat <<'EOF'; Set-Content -Path scripts/sample.py -Value z\nmsg\nEOF\n)\"",
        "block",
    ),
    (
        "20-opener-pipeline-tail-blocks",
        "git commit -m \"$(cat <<'EOF' | tee scripts/sample.py\nmsg\nEOF\n)\"",
        "block",
    ),
]


@pytest.mark.parametrize(("case_id", "command", "expected"), _WI3357_GATE_CASES)
def test_wi3357_gate_decision_classification(tmp_path: Path, case_id: str, command: str, expected: str) -> None:
    """All historical direct-finalization forms now require the lifecycle CLI."""
    payload = {
        "cwd": str(tmp_path),
        "tool_name": "Bash",
        "tool_input": {"command": command},
    }
    result = gate.gate_decision(payload)
    assert expected == "block", case_id
    assert result.get("decision") == "block", case_id
    if result.get("reason_code") is not None:
        assert result["reason_code"] == "direct_git_effect_requires_lifecycle", case_id
    else:
        assert "authorization packet" in result.get("reason", ""), case_id


_WI3357_PARSER_CASES = [
    # (case_id, command, expected_span_count)
    (
        "documented-single-heredoc",
        "git commit -m \"$(cat <<'EOF'\nmsg body\nEOF\n)\"",
        1,
    ),
    ("unquoted-delimiter", 'git commit -m "$(cat <<EOF\nmsg\nEOF\n)"', 0),
    (
        "non-cat-opener",
        "git commit -m \"$(rm scripts/sample.py <<'EOF'\nx\nEOF\n)\"",
        0,
    ),
    (
        "early-delimiter-then-command",
        "git commit -m \"$(cat <<'EOF'\nmsg\nEOF\nSet-Content -Path scripts/sample.py -Value z\nEOF\n)\"",
        0,
    ),
    (
        "early-delimiter-then-separator",
        "git commit -m \"$(cat <<'EOF'\nmsg\nEOF\n; rm -rf x\nEOF\n)\"",
        0,
    ),
    (
        "opener-redirect-tail",
        "git commit -m \"$(cat <<'EOF' > scripts/sample.py\nmsg\nEOF\n)\"",
        0,
    ),
    (
        "opener-separator-tail",
        "git commit -m \"$(cat <<'EOF'; rm -rf x\nmsg\nEOF\n)\"",
        0,
    ),
    (
        "opener-pipeline-tail",
        "git commit -m \"$(cat <<'EOF' | tee scripts/sample.py\nmsg\nEOF\n)\"",
        0,
    ),
    ("no-delimiter-line", "git commit -m \"$(cat <<'EOF'\njust body text\n)\"", 0),
    ("multi-cat-heredoc", "git commit -m \"$(cat <<'A' <<'B'\nbody\nA\nB\n)\"", 0),
    ("crlf-heredoc", "git commit -m \"$(cat <<'EOF'\r\nmsg\r\nEOF\r\n)\"", 0),
    (
        "two-independent-heredocs",
        "git commit -m \"$(cat <<'A'\nfirst\nA\n)$(cat <<'B'\nsecond\nB\n)\"",
        2,
    ),
]


@pytest.mark.parametrize(("case_id", "command", "expected_spans"), _WI3357_PARSER_CASES)
def test_wi3357_heredoc_parser_recognizes_only_safe_spans(case_id: str, command: str, expected_spans: int) -> None:
    """WI-3357: _find_heredoc_message_substitution_spans recognizes a span only
    when every boundary -- opener, opener-line tail, first delimiter line, and
    post-delimiter close paren -- is validated; every other shape fails closed
    (no span), so the $( stays visible to the control-marker scan."""
    spans = gate._find_heredoc_message_substitution_spans(command)
    assert len(spans) == expected_spans, case_id


# W4 IP-4 (gtkb-s358-w4-enforcement-calibration, WI-3368): MUTATING_COMMAND_RE
# redirect detection replaced by a punctuation-aware shlex token scan. A `>`
# inside a quoted argument or embedded Python expression is no longer misread
# as a shell redirect, while a standalone redirect operator token and the
# named-command mutations still flag.


def test_impl_start_gate_python_operator_not_mutating() -> None:
    """W4 IP-4 (false-positive removed): a quoted Python comparison or shift
    operator is not misread as a shell redirect, so the command is not flagged
    mutating."""
    assert gate._is_mutating_command('python -c "print(1 if a>b else 0)"') is False
    assert gate._is_mutating_command('python -c "x = value >> 2"') is False
    assert gate._is_mutating_command("python -c 'assert score >= 0'") is False


def test_impl_start_gate_genuine_redirect_still_mutating() -> None:
    """W4 IP-4 (genuine-positive preserved): a standalone shell redirect
    operator token is still flagged mutating, and named-command mutations are
    unaffected by the shlex-based redirect detection."""
    assert gate._is_mutating_command("echo data > out.txt") is True
    assert gate._is_mutating_command("echo data>>out.txt") is True
    assert gate._is_mutating_command("Set-Content -Path scripts/sample.py -Value x") is True


# ---------------------------------------------------------------------------
# WI-4837: post-VERIFIED finalization staging clearance (automatic parity per
# DELIB-WI4837-AUTOMATIC-PARITY-20260707). A `git add` of a terminal-VERIFIED
# thread's own approved target_paths is cleared; ordinary mutation stays blocked.
# ---------------------------------------------------------------------------


def _write_verified_thread(
    root: Path,
    *,
    bridge_id: str = "verified-impl",
    target_paths: list[str] | None = None,
) -> None:
    """Build a terminal-VERIFIED chain: NEW at -001, GO at -002, VERIFIED at -003."""
    bridge = root / "bridge"
    bridge.mkdir(exist_ok=True)
    (bridge / f"{bridge_id}-001.md").write_text(
        _proposal(bridge_id=bridge_id, target_paths=target_paths), encoding="utf-8"
    )
    (bridge / f"{bridge_id}-002.md").write_text(_go_verdict_body(bridge_id), encoding="utf-8")
    (bridge / f"{bridge_id}-003.md").write_text(
        "VERIFIED\n\nauthor_session_context_id: fixture-verified-session\n\n# Verdict\n",
        encoding="utf-8",
    )


def _git_add_payload(root: Path, command: str, session_id: str = "session-1") -> dict[str, object]:
    return {
        "cwd": str(root),
        "session_id": session_id,
        "tool_name": "bash",
        "tool_input": {"command": command},
    }


def test_post_verified_finalization_git_add_approved_path_requires_lifecycle(
    tmp_path: Path,
) -> None:
    """Terminal verification does not bypass the canonical Git lifecycle."""
    _write_verified_thread(tmp_path, bridge_id="verified-impl")
    _claim_bridge(tmp_path, "verified-impl", "session-1")

    result = gate.gate_decision(_git_add_payload(tmp_path, "git add scripts/sample.py"))

    assert result["decision"] == "block"
    assert result["reason_code"] == "direct_git_effect_requires_lifecycle"


def test_post_verified_finalization_git_add_multiple_approved_paths_requires_lifecycle(
    tmp_path: Path,
) -> None:
    """Multiple approved targets still require the canonical Git lifecycle."""
    _write_verified_thread(tmp_path, bridge_id="verified-impl")
    _claim_bridge(tmp_path, "verified-impl", "session-1")

    result = gate.gate_decision(
        _git_add_payload(tmp_path, "git add scripts/sample.py platform_tests/scripts/test_sample.py")
    )

    assert result["decision"] == "block"
    assert result["reason_code"] == "direct_git_effect_requires_lifecycle"


def test_post_verified_finalization_git_add_outside_target_paths_blocked(
    tmp_path: Path,
) -> None:
    """GOV-WORK-TREE-HYGIENE-001: a staged path outside the approved target_paths
    is not cleared; it falls through to the fail-closed authorization gate."""
    _write_verified_thread(tmp_path, bridge_id="verified-impl")
    _claim_bridge(tmp_path, "verified-impl", "session-1")

    result = gate.gate_decision(_git_add_payload(tmp_path, "git add scripts/other.py"))

    assert result["decision"] == "block"


def test_post_verified_finalization_mixed_targets_blocked(tmp_path: Path) -> None:
    """A single out-of-scope target disqualifies the whole staging command."""
    _write_verified_thread(tmp_path, bridge_id="verified-impl")
    _claim_bridge(tmp_path, "verified-impl", "session-1")

    result = gate.gate_decision(_git_add_payload(tmp_path, "git add scripts/sample.py scripts/other.py"))

    assert result["decision"] == "block"


def test_post_verified_finalization_broad_git_add_blocked(tmp_path: Path) -> None:
    """A broad/whole-tree `git add -A` is not clearable (targets not enumerable)."""
    _write_verified_thread(tmp_path, bridge_id="verified-impl")
    _claim_bridge(tmp_path, "verified-impl", "session-1")

    result = gate.gate_decision(_git_add_payload(tmp_path, "git add -A"))

    assert result["decision"] == "block"


def test_post_verified_finalization_chained_command_not_cleared(tmp_path: Path) -> None:
    """GOV-WORK-TREE-HYGIENE-001: a chained command disqualifies the fast
    finalization clearance so the protected staging falls through and is blocked."""
    _write_verified_thread(tmp_path, bridge_id="verified-impl")
    _claim_bridge(tmp_path, "verified-impl", "session-1")

    result = gate.gate_decision(_git_add_payload(tmp_path, "git add scripts/sample.py; rm -rf scripts"))

    assert result["decision"] == "block"


def test_post_verified_finalization_without_work_intent_claim_blocked(
    tmp_path: Path,
) -> None:
    """PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001: with no work-intent claim
    identifying the thread, the clearance cannot resolve a bridge and the staging
    is blocked."""
    _write_verified_thread(tmp_path, bridge_id="verified-impl")

    result = gate.gate_decision(_git_add_payload(tmp_path, "git add scripts/sample.py"))

    assert result["decision"] == "block"


def test_post_verified_ordinary_mutation_still_blocked(tmp_path: Path) -> None:
    """_validate_packet is unchanged: an ordinary (non-`git add`) mutation of an
    approved path after terminal VERIFIED still fails closed -- the clearance
    covers only finalization staging, not resumed implementation."""
    _write_verified_thread(tmp_path, bridge_id="verified-impl")
    _claim_bridge(tmp_path, "verified-impl", "session-1")

    result = gate.gate_decision(_apply_patch_payload(tmp_path, target="scripts/sample.py"))

    assert result["decision"] == "block"


def test_finalization_git_add_targets_parses_and_rejects() -> None:
    """The staging-command parser accepts a pure `git add` of explicit paths and
    rejects chaining, flags, whole-tree, pathspec magic, and globs."""
    assert gate._finalization_git_add_targets("git add scripts/a.py scripts/b.py") == [
        "scripts/a.py",
        "scripts/b.py",
    ]
    assert gate._finalization_git_add_targets("git add -- scripts/a.py") == ["scripts/a.py"]
    assert gate._finalization_git_add_targets("git add -A") is None
    assert gate._finalization_git_add_targets("git add .") is None
    assert gate._finalization_git_add_targets("git add scripts/*.py") is None
    assert gate._finalization_git_add_targets("git add :/") is None
    assert gate._finalization_git_add_targets("git add a.py && rm b") is None
    assert gate._finalization_git_add_targets("git commit -m x") is None
    assert gate._finalization_git_add_targets("git rm scripts/a.py") is None


def test_registered_content_edit_can_refresh_stale_registry_observation(
    tmp_path: Path,
) -> None:
    _authorize_registered_target(tmp_path)
    (tmp_path / "scripts" / "sample.py").write_text("stale\n", encoding="utf-8")

    result = gate.gate_decision(_registered_payload(tmp_path))

    assert "decision" not in result
    assert "capability_hash" in result["registryObservationIntent"]
    assert observer.intent_path(tmp_path, "session-1", "fixture-tool-event").exists()


def test_incomplete_registry_journal_records_nonblocking_audit_gap(
    tmp_path: Path,
) -> None:
    _authorize_registered_target(tmp_path)
    with sqlite3.connect(tmp_path / "groundtruth.db") as conn:
        conn.execute(
            """
            INSERT INTO sot_registry_transaction_journal (
                journal_id, operation, intent_recorded_at, journal_state,
                actor_session, changed_by, changed_at, change_reason
            ) VALUES ('fixture-incomplete', 'amend', '2026-07-25T00:00:00Z',
                      'prepared', 'fixture', 'test', '2026-07-25T00:00:00Z', 'fixture')
            """
        )
        conn.commit()

    result = gate.gate_decision(_registered_payload(tmp_path))

    assert "decision" not in result
    gap = result["registryObservationIntent"]["audit_gap"]
    assert gap["code"] == "registry_observation_unavailable"
    assert "fixture-incomplete" in gap["detail"]


def test_registered_identity_change_requires_transition(tmp_path: Path) -> None:
    _authorize_registered_target(tmp_path)
    payload = _registered_payload(tmp_path)
    payload["tool_input"] = {"patch": "*** Begin Patch\n*** Delete File: scripts/sample.py\n*** End Patch\n"}

    result = gate.gate_decision(payload)

    assert result["decision"] == "block"
    assert "separately reviewed transition authority" in result["reason"]
    assert not observer.intent_path(tmp_path, "session-1", "fixture-tool-event").exists()


def test_authorized_write_mints_observation_intent(tmp_path: Path) -> None:
    _authorize_registered_target(tmp_path)

    result = gate.gate_decision(_registered_payload(tmp_path))

    assert "registryObservationIntent" in result
    intent = observer.intent_path(tmp_path, "session-1", "fixture-tool-event")
    assert intent.exists()
    intent_payload = json.loads(intent.read_text(encoding="utf-8"))
    assert intent_payload["target_paths"] == ["scripts/sample.py"]
    assert intent_payload["session_id"] == "session-1"
    assert intent_payload["tool_event_id"] == "fixture-tool-event"
    with sqlite3.connect(tmp_path / "groundtruth.db") as conn:
        row = conn.execute("SELECT capability_state FROM sot_registry_observation_capabilities").fetchone()
    assert row == ("minted",)


def test_unauthorized_write_mints_no_observation_intent(tmp_path: Path) -> None:
    _seed_registered_target(tmp_path)

    result = gate.gate_decision(_registered_payload(tmp_path))

    assert result["decision"] == "block"
    assert not observer.intent_path(tmp_path, "session-1", "fixture-tool-event").exists()
    with sqlite3.connect(tmp_path / "groundtruth.db") as conn:
        count = conn.execute("SELECT COUNT(*) FROM sot_registry_observation_capabilities").fetchone()[0]
    assert count == 0


@pytest.mark.parametrize(
    ("command", "expected", "rationale"),
    [
        ("python -m groundtruth_kb.git_lifecycle create --help", True, "help on a governed CLI"),
        ("gt bridge dispatch report --help", True, "help on the gt CLI"),
        ("sometool --usage", True, "usage flag"),
        ("sometool --help > out.txt", False, "redirection writes a file"),
        ("sometool --help >> out.txt", False, "append redirection writes a file"),
        ("git commit --help && mkdir newdir", False, "chaining is disqualifying"),
        ("chown -h user file", False, "-h is a real operation modifier, not help"),
        ("mkdir /tmp/newdir", False, "plain mutation with no help flag"),
        ("git push origin main", False, "mutation with no help flag"),
    ],
)
def test_help_output_is_classified_read_only(command: str, expected: bool, rationale: str) -> None:
    """WI-6674: a --help/--usage request prints usage text and mutates nothing.

    The WI-3291 prefix allowlist enumerates command verbs, so it cannot express
    help output on an arbitrary governed CLI; such invocations previously fell
    through to ``<unknown-mutating-target>`` and were denied. Redirection and
    chaining must still deny, and ``-h`` must not be admitted as help because it
    is a real operation modifier for some verbs.
    """
    assert gate._is_safe_command(command) is expected, rationale


# WI-6821 Change 7: command-position anchoring for bare POSIX write verbs.
#
# The verbs added by F10 were originally matched anywhere in the command text,
# so ordinary prose in an argument tripped a fail-closed gate. Change 7 anchors
# them to command position. Both directions need coverage: a narrowing that
# silently drops a real detection is a worse defect than the false positives it
# fixes, because it reopens the enforcement hole F10 closed.
PROTECTED_GATE_PATH = "scripts/implementation_start_gate" + ".py"


@pytest.mark.parametrize(
    ("template", "rationale"),
    [
        ("rm -rf {p}", "bare verb at start of command"),
        ("cat payload | tee {p}", "tee reached through a pipe; the pipe alternative must cover it"),
        ("cp a.py {p}", "copy onto a protected path"),
        ("mv a.py {p}", "move onto a protected path"),
        ("true && rm {p}", "verb after an && chain"),
        ("echo hi; touch {p}", "verb after a semicolon"),
        ("(cd scripts && rm {p})", "verb inside a subshell, after an opening paren"),
    ],
)
def test_change7_preserves_command_position_mutation_detection(template: str, rationale: str) -> None:
    """WI-6821: every real mutation sits at command position and must still fire.

    This is the anti-regression half of Change 7. The narrowing is acceptable
    only if it drops argument-position prose WITHOUT dropping any of these; a
    miss here means the F10 enforcement hole has been reopened.
    """
    assert gate._has_mutating_signal(template.format(p=PROTECTED_GATE_PATH)), rationale


@pytest.mark.parametrize(
    ("command", "rationale"),
    [
        ("git log --grep=rm", "write verb inside a --grep value is prose, not a command"),
        ("git log --grep=cp --oneline", "same, with a trailing flag"),
        ("git log --format=%h --grep=install", "write verb inside a --grep value"),
        ("grep -rn dd scripts/", "a write verb used as a search pattern operand"),
        ("git for-each-ref --format=%(refname)", "read-only ref enumeration (F3)"),
    ],
)
def test_change7_drops_argument_position_false_positives(command: str, rationale: str) -> None:
    """WI-6821: a write verb in argument position is prose and must not fire.

    These are the materialized false positives that motivated Change 7: the
    unanchored form blocked read-only inspection commands whose only offense
    was carrying a write verb inside a flag value.
    """
    assert not gate._has_mutating_signal(command), rationale
