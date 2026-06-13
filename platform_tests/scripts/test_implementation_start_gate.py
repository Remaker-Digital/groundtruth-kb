"""Spec-derived tests for implementation-start authorization gate."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest
from groundtruth_kb.db import KnowledgeDB

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts import implementation_authorization as auth  # noqa: E402
from scripts import implementation_start_gate as gate  # noqa: E402


def _proposal(
    *,
    bridge_id: str = "sample-implementation",
    target_paths: list[str] | None = None,
    requirement_sufficiency: str = "Existing requirements sufficient - linked rules cover this implementation.",
) -> str:
    targets = target_paths or ["scripts/sample.py", "platform_tests/scripts/test_sample.py"]
    return "\n".join(
        [
            "NEW",
            "",
            "# Implementation Proposal",
            "",
            f"Document: {bridge_id}",
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


def _write_thread(
    root: Path,
    *,
    bridge_id: str = "sample-implementation",
    latest_status: str = "GO",
    proposal: str | None = None,
) -> None:
    bridge = root / "bridge"
    bridge.mkdir()
    proposal_name = f"{bridge_id}-001.md"
    go_name = f"{bridge_id}-002.md"
    (bridge / proposal_name).write_text(proposal or _proposal(bridge_id=bridge_id), encoding="utf-8")
    (bridge / go_name).write_text("GO\n\n# Review\n", encoding="utf-8")
    if latest_status == "GO":
        lines = [
            f"Document: {bridge_id}",
            f"GO: bridge/{go_name}",
            f"NEW: bridge/{proposal_name}",
        ]
    else:
        lines = [
            f"Document: {bridge_id}",
            f"{latest_status}: bridge/{proposal_name}",
        ]
    (bridge / "INDEX.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def _seed_project_authorization(root: Path, *, link_work_item: bool = True, status: str = "active") -> None:
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
        if link_work_item:
            db.link_project_work_item(
                "PROJECT-AUTH",
                "WI-AUTH-001",
                "test",
                "seed work item membership",
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
        db.insert_project_authorization(
            "PROJECT-AUTH",
            "Authorized implementation project",
            "DELIB-PROJECT-AUTH",
            "Bounded project implementation scope.",
            "test",
            "seed project authorization",
            id="PAUTH-AUTH",
            status=status,
            included_spec_ids=["SPEC-AUTH-SEED"],
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


def _claim_bridge(root: Path, bridge_id: str = "sample-implementation", session_id: str | None = None) -> None:
    holder = session_id or auth.resolve_work_intent_session_id() or "session-1"
    assert auth.bridge_work_intent_registry.acquire(bridge_id, holder, project_root=root)


def _apply_patch_payload(
    root: Path, target: str = "scripts/sample.py", session_id: str = "session-1"
) -> dict[str, object]:
    return {
        "cwd": str(root),
        "session_id": session_id,
        "tool_name": "apply_patch",
        "tool_input": {"patch": f"*** Begin Patch\n*** Update File: {target}\n@@\n+pass\n*** End Patch\n"},
    }


def test_go_authorization_packet_allows_in_scope_apply_patch(tmp_path: Path) -> None:
    _write_thread(tmp_path)
    packet = auth.create_authorization_packet(tmp_path, "sample-implementation")
    auth.write_packet(tmp_path, packet)
    _claim_bridge(tmp_path)

    assert gate.gate_decision(_apply_patch_payload(tmp_path)) == {}


def test_valid_packet_blocks_when_work_intent_claim_missing(tmp_path: Path) -> None:
    _write_thread(tmp_path)
    packet = auth.create_authorization_packet(tmp_path, "sample-implementation")
    auth.write_packet(tmp_path, packet)

    result = gate.gate_decision(_apply_patch_payload(tmp_path))

    assert result["decision"] == "block"
    assert "No active work-intent claim" in result["reason"]


def test_valid_packet_blocks_when_claim_held_by_other_session(tmp_path: Path) -> None:
    _write_thread(tmp_path)
    packet = auth.create_authorization_packet(tmp_path, "sample-implementation")
    auth.write_packet(tmp_path, packet)
    _claim_bridge(tmp_path, "sample-implementation", "other-session")

    result = gate.gate_decision(_apply_patch_payload(tmp_path, session_id="session-1"))

    assert result["decision"] == "block"
    assert "claimed by session 'other-session'" in result["reason"]


def test_lapsed_claim_blocks_mutation(tmp_path: Path) -> None:
    _write_thread(tmp_path)
    packet = auth.create_authorization_packet(tmp_path, "sample-implementation")
    auth.write_packet(tmp_path, packet)
    _claim_bridge(tmp_path, "sample-implementation", "session-1")
    conn = auth.bridge_work_intent_registry._get_conn(tmp_path)
    try:
        with conn:
            conn.execute(
                "UPDATE work_intent_claims SET ttl_expires_at = ?, implementation_grace_expires_at = ? "
                "WHERE thread_slug = ?",
                ("2026-01-01T00:00:00Z", "2026-01-01T00:00:00Z", "sample-implementation"),
            )
    finally:
        conn.close()

    result = gate.gate_decision(_apply_patch_payload(tmp_path))

    assert result["decision"] == "block"
    assert "No active work-intent claim" in result["reason"]


def test_gate_allows_when_holder_is_dispatch_id(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _write_thread(tmp_path)
    packet = auth.create_authorization_packet(tmp_path, "sample-implementation")
    auth.write_packet(tmp_path, packet)
    _claim_bridge(tmp_path, "sample-implementation", "dispatch-1")
    monkeypatch.setenv("GTKB_BRIDGE_POLLER_RUN_ID", "dispatch-1")

    assert gate.gate_decision(_apply_patch_payload(tmp_path, session_id="ambient-session")) == {}


def test_gate_blocks_on_work_intent_registry_error(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _write_thread(tmp_path)
    packet = auth.create_authorization_packet(tmp_path, "sample-implementation")
    auth.write_packet(tmp_path, packet)
    _claim_bridge(tmp_path, "sample-implementation", "session-1")

    def raise_registry_error(*_args, **_kwargs):
        raise auth.bridge_work_intent_registry.WorkIntentRegistryError("registry unavailable")

    monkeypatch.setattr(auth.bridge_work_intent_registry, "current_holder", raise_registry_error)

    result = gate.gate_decision(_apply_patch_payload(tmp_path))

    assert result["decision"] == "block"
    assert "Could not verify bridge work-intent claim" in result["reason"]


def test_bootstrap_bridge_id_exempt_from_claim_check(tmp_path: Path) -> None:
    bridge_id = "gtkb-implementation-start-authorization-gate"
    _write_thread(
        tmp_path,
        bridge_id=bridge_id,
        proposal=_proposal(bridge_id=bridge_id, target_paths=["scripts/sample.py"]),
    )
    packet = auth.create_authorization_packet(tmp_path, bridge_id)
    auth.write_packet(tmp_path, packet)

    assert gate.gate_decision(_apply_patch_payload(tmp_path, session_id="")) == {}


def test_existing_packet_blocks_when_bridge_becomes_latest_deferred(tmp_path: Path) -> None:
    (tmp_path / "groundtruth.toml").write_text('[groundtruth]\ndb_path = "groundtruth.db"\n', encoding="utf-8")
    _write_thread(tmp_path)
    packet = auth.create_authorization_packet(tmp_path, "sample-implementation")
    auth.write_packet(tmp_path, packet)
    bridge = tmp_path / "bridge"
    (bridge / "sample-implementation-003.md").write_text("DEFERRED\n\n# Owner deferral\n", encoding="utf-8")
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

    assert result["decision"] == "block"
    assert "DEFERRED" in result["reason"]


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


def test_non_go_bridge_entry_cannot_create_authorization(tmp_path: Path) -> None:
    _write_thread(tmp_path, latest_status="REVISED")

    with pytest.raises(auth.AuthorizationError, match="latest GO"):
        auth.create_authorization_packet(tmp_path, "sample-implementation")


def test_authorization_accepts_bold_target_paths_metadata(tmp_path: Path) -> None:
    _write_thread(tmp_path, proposal=_proposal().replace("target_paths:", "**target_paths:**"))

    packet = auth.create_authorization_packet(tmp_path, "sample-implementation")

    assert packet["target_path_globs"] == ["scripts/sample.py", "platform_tests/scripts/test_sample.py"]


def test_exact_file_target_path_authorizes_exact_protected_file(tmp_path: Path) -> None:
    exact_target = "config/governance/hygiene-baseline-registry.toml"
    _write_thread(tmp_path, proposal=_proposal(target_paths=[exact_target]))
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


def test_requirement_gap_blocks_authorization(tmp_path: Path) -> None:
    _write_thread(
        tmp_path,
        proposal=_proposal(
            requirement_sufficiency="New or revised requirement required before implementation - capture it first."
        ),
    )

    with pytest.raises(auth.AuthorizationError, match="new or revised requirements"):
        auth.create_authorization_packet(tmp_path, "sample-implementation")


def test_requirement_sufficiency_are_sufficient_allows_gate_authorization(tmp_path: Path) -> None:
    """WI-3410: natural sufficient-state wording authorizes protected edits."""
    _write_thread(
        tmp_path,
        proposal=_proposal(requirement_sufficiency="Existing requirements are sufficient for this scoped fix."),
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


def test_owner_sufficiency_deliberation_packet_allows_gate_authorization(tmp_path: Path) -> None:
    """WI-4241: owner-decision fallback packets authorize protected edits."""
    _write_thread(
        tmp_path,
        proposal=_proposal(requirement_sufficiency="Complete coverage exists without the bounded phrase."),
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


def test_project_authorization_load_revalidates_current_spec_exclusions(tmp_path: Path) -> None:
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


def test_project_authorization_requires_work_item_membership_or_inclusion(tmp_path: Path) -> None:
    _seed_project_authorization(tmp_path, link_work_item=False)
    proposal = (
        _proposal() + "\nProject Authorization: `PAUTH-AUTH`\nProject: `PROJECT-AUTH`\nWork Item: `WI-AUTH-001`\n"
    )
    _write_thread(tmp_path, proposal=proposal)

    with pytest.raises(auth.AuthorizationError, match="neither included in nor an active member"):
        auth.create_authorization_packet(tmp_path, "sample-implementation")


def test_target_mismatch_blocks_even_with_valid_packet(tmp_path: Path) -> None:
    _write_thread(tmp_path)
    packet = auth.create_authorization_packet(tmp_path, "sample-implementation")
    auth.write_packet(tmp_path, packet)
    payload = {
        "cwd": str(tmp_path),
        "tool_name": "apply_patch",
        "tool_input": {
            "patch": "*** Begin Patch\n*** Update File: config/out-of-scope.toml\n@@\n+x=1\n*** End Patch\n"
        },
    }

    result = gate.gate_decision(payload)

    assert result["decision"] == "block"
    assert "outside implementation authorization scope" in result["reason"]


def test_bridge_report_write_remains_open_without_authorization(tmp_path: Path) -> None:
    payload = {
        "cwd": str(tmp_path),
        "tool_name": "apply_patch",
        "tool_input": {"patch": "*** Begin Patch\n*** Add File: bridge/example-001.md\n+NEW\n*** End Patch\n"},
    }

    assert gate.gate_decision(payload) == {}


def test_raw_patch_bridge_only_write_remains_open_without_authorization(tmp_path: Path) -> None:
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

    assert gate.changed_paths(payload) == (["bridge/example-001.md", "bridge/INDEX.md"], True)
    assert gate.gate_decision(payload) == {}


def test_raw_patch_protected_write_blocks_without_authorization(tmp_path: Path) -> None:
    payload = {
        "cwd": str(tmp_path),
        "tool_name": "functions.apply_patch",
        "input": "*** Begin Patch\n*** Update File: scripts/sample.py\n@@\n+pass\n*** End Patch\n",
    }

    result = gate.gate_decision(payload)

    assert result["decision"] == "block"
    assert "authorization packet" in result["reason"]


def test_nested_patch_payload_without_tool_name_allows_bridge_only_write(tmp_path: Path) -> None:
    payload = {
        "cwd": str(tmp_path),
        "event": "PreToolUse",
        "tool": "freeform",
        "tool_input": {
            "arguments": {"payload": ("*** Begin Patch\n*** Add File: bridge/example-002.md\n+NEW\n*** End Patch\n")}
        },
    }

    assert gate.changed_paths(payload) == (["bridge/example-002.md"], True)
    assert gate.gate_decision(payload) == {}


def test_shell_payload_with_escaped_patch_newlines_allows_bridge_only_write(tmp_path: Path) -> None:
    payload = {
        "cwd": str(tmp_path),
        "tool_name": "Bash",
        "tool_input": {
            "command": ('$payload = "*** Begin Patch`n*** Add File: bridge/example-003.md`n+NEW`n*** End Patch`n"')
        },
    }

    assert gate.changed_paths(payload) == (["bridge/example-003.md"], True)
    assert gate.gate_decision(payload) == {}


def test_shell_mutation_classification_blocks_protected_write(tmp_path: Path) -> None:
    payload = {
        "cwd": str(tmp_path),
        "tool_name": "Bash",
        "tool_input": {"command": "Set-Content -Path scripts/sample.py -Value 'x'"},
    }

    result = gate.gate_decision(payload)

    assert result["decision"] == "block"
    assert "authorization packet" in result["reason"]


def test_memory_only_mutating_shell_payload_allowed_without_authorization(tmp_path: Path) -> None:
    payload = {
        "cwd": str(tmp_path),
        "tool_name": "Bash",
        "tool_input": {"command": "Set-Content -Path memory/pending-owner-decisions.md -Value 'x'"},
    }

    assert gate.changed_paths(payload) == (["memory/pending-owner-decisions.md"], True)
    assert gate.gate_decision(payload) == {}


def test_deliberation_search_query_with_patch_word_is_allowed_without_authorization(tmp_path: Path) -> None:
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


def test_read_only_shell_command_is_allowed_without_authorization(tmp_path: Path) -> None:
    payload = {
        "cwd": str(tmp_path),
        "tool_name": "Bash",
        "tool_input": {"command": 'rg -n "hello" scripts/sample.py'},
    }

    assert gate.gate_decision(payload) == {}


def test_git_commit_finalization_command_is_allowed_without_authorization(tmp_path: Path) -> None:
    payload = {
        "cwd": str(tmp_path),
        "tool_name": "Bash",
        "tool_input": {"command": 'git commit -m "feat(gtkb): finalize verified bridge work"'},
    }

    assert gate.gate_decision(payload) == {}


def test_git_push_finalization_command_is_allowed_without_authorization(tmp_path: Path) -> None:
    payload = {
        "cwd": str(tmp_path),
        "tool_name": "Bash",
        "tool_input": {"command": "git push origin develop"},
    }

    assert gate.gate_decision(payload) == {}


def test_chained_git_commit_with_protected_write_still_blocks(tmp_path: Path) -> None:
    payload = {
        "cwd": str(tmp_path),
        "tool_name": "Bash",
        "tool_input": {"command": 'git commit -m "x"; Set-Content -Path scripts/sample.py -Value "x"'},
    }

    result = gate.gate_decision(payload)

    assert result["decision"] == "block"
    assert "authorization packet" in result["reason"]


def test_gate_uses_unique_named_packet_when_current_json_absent(tmp_path: Path) -> None:
    """WI-4452: a unique valid named packet can authorize the protected target."""
    _write_thread(tmp_path)
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
    (bridge / "bridge-b-002.md").write_text("GO\n\n# Review\n", encoding="utf-8")
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

    assert result.get("decision") == "block"
    assert "Ambiguous implementation authorization" in result.get("reason", "")
    assert "bridge-a" in result.get("reason", "")
    assert "bridge-b" in result.get("reason", "")


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
    cmd = "python -c \"import sqlite3; sqlite3.connect('a.db').execute('WITH cte AS (SELECT id FROM t) SELECT * FROM cte')\""
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
    subprocess.run(["git", *ident, "add", "groundtruth.toml"], cwd=canonical, check=True, capture_output=True)
    subprocess.run(["git", *ident, "commit", "-m", "init"], cwd=canonical, check=True, capture_output=True)
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


# WI-3357: implementation_start_gate finalization-exemption quote-aware
# control-marker fix. Cases derive from the Specification-Derived Verification
# Plan in bridge/gtkb-impl-start-gate-finalization-quoting-fix-007.md, plus the
# -008 review's non-blocking observations (multi-cat / CRLF / unquoted shapes).
# In a command string, \n is a literal newline; HEREDOC commands span lines.


_WI3357_SIMPLE_CASES = [
    # (case_id, command, expected_is_simple)
    ("01-chaining-markers-double-quoted", 'git commit -m "fix X; tidy | done && wrap"', True),
    ("02-chaining-marker-single-quoted", "git commit -m 'fix X; tidy Y'", True),
    ("03-heredoc-single-quoted-delim", "git commit -m \"$(cat <<'EOF'\nmsg body\nEOF\n)\"", True),
    ("04-heredoc-double-quoted-delim", 'git commit -m "$(cat <<"EOF"\nmsg\nEOF\n)"', True),
    ("05-cmdsub-protected-write", 'git commit -m "$(Set-Content -Path scripts/sample.py -Value z)"', False),
    ("06-backtick-protected-write", 'git commit -m "`Set-Content -Path scripts/sample.py -Value z`"', False),
    ("07-cmdsub-non-heredoc", 'git commit -m "$(cat msg.txt)"', False),
    ("08-heredoc-unquoted-delim", 'git commit -m "$(cat <<EOF\nmsg\nEOF\n)"', False),
    ("09-heredoc-non-cat-command", "git commit -m \"$(rm scripts/sample.py <<'EOF'\nx\nEOF\n)\"", False),
    ("10-cmdsub-literal-single-quoted", "git commit -m '$(whoami)'", True),
    ("11-chained-after-git-finalization", 'git commit -m "x"; rm -rf y', False),
    (
        "12-chained-protected-write-punctuated",
        'git commit -m "fix; tidy"; Set-Content -Path scripts/sample.py -Value "z"',
        False,
    ),
    (
        "13-chained-after-complete-heredoc",
        "git commit -m \"$(cat <<'EOF'\nmsg\nEOF\n)\" && Set-Content -Path scripts/sample.py -Value z",
        False,
    ),
    ("14-plain-push", "git push origin develop", True),
    ("15-denied-push-flag", "git push --force origin main", False),
    (
        "16-early-delimiter-then-command",
        "git commit -m \"$(cat <<'EOF'\nmsg\nEOF\nSet-Content -Path scripts/sample.py -Value z\nEOF\n)\"",
        False,
    ),
    (
        "17-early-delimiter-then-separator",
        "git commit -m \"$(cat <<'EOF'\nmsg\nEOF\n; Set-Content -Path scripts/sample.py -Value z\nEOF\n)\"",
        False,
    ),
    (
        "18-opener-redirect-tail",
        "git commit -m \"$(cat <<'EOF' > scripts/sample.py\nmsg\nEOF\n)\"",
        False,
    ),
    (
        "19-opener-separator-tail",
        "git commit -m \"$(cat <<'EOF'; Set-Content -Path scripts/sample.py -Value z\nmsg\nEOF\n)\"",
        False,
    ),
    (
        "20-opener-pipeline-tail",
        "git commit -m \"$(cat <<'EOF' | tee scripts/sample.py\nmsg\nEOF\n)\"",
        False,
    ),
    ("21-multi-cat-heredoc", "git commit -m \"$(cat <<'A' <<'B'\nbody\nA\nB\n)\"", False),
    ("22-crlf-heredoc", "git commit -m \"$(cat <<'EOF'\r\nmsg\r\nEOF\r\n)\"", False),
    ("23-unquoted-heredoc-substitution", "git commit -m $(cat <<'EOF'\nmsg\nEOF\n)", True),
]


@pytest.mark.parametrize(("case_id", "command", "expected"), _WI3357_SIMPLE_CASES)
def test_wi3357_simple_git_finalization_classification(case_id: str, command: str, expected: bool) -> None:
    """WI-3357: _is_simple_git_finalization_command classifies each verification
    case correctly. Literal punctuation and the documented HEREDOC commit
    pattern are exempt; executable command substitution, chaining, and any
    heredoc whose substitution would run a further command are not."""
    assert gate._is_simple_git_finalization_command(command) is expected, case_id


_WI3357_GATE_CASES = [
    # (case_id, command, expected) -- expected is "exempt" ({}) or "block"
    ("01-chaining-markers-exempt", 'git commit -m "fix X; tidy | done && wrap"', "exempt"),
    ("03-heredoc-exempt", "git commit -m \"$(cat <<'EOF'\nmsg body\nEOF\n)\"", "exempt"),
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
    ("08-heredoc-unquoted-delim-blocks", 'git commit -m "$(cat <<EOF\nmsg\nEOF\n)"', "block"),
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
    ("14-plain-push-exempt", "git push origin develop", "exempt"),
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
    """WI-3357: gate_decision exempts a punctuated/HEREDOC git finalization
    command (returns {}) and blocks a command whose substitution or chaining
    would run a protected mutation, with no authorization packet seeded."""
    payload = {
        "cwd": str(tmp_path),
        "tool_name": "Bash",
        "tool_input": {"command": command},
    }
    result = gate.gate_decision(payload)
    if expected == "exempt":
        assert result == {}, case_id
    else:
        assert result.get("decision") == "block", case_id
        assert "authorization packet" in result.get("reason", ""), case_id


_WI3357_PARSER_CASES = [
    # (case_id, command, expected_span_count)
    ("documented-single-heredoc", "git commit -m \"$(cat <<'EOF'\nmsg body\nEOF\n)\"", 1),
    ("unquoted-delimiter", 'git commit -m "$(cat <<EOF\nmsg\nEOF\n)"', 0),
    ("non-cat-opener", "git commit -m \"$(rm scripts/sample.py <<'EOF'\nx\nEOF\n)\"", 0),
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
    ("opener-separator-tail", "git commit -m \"$(cat <<'EOF'; rm -rf x\nmsg\nEOF\n)\"", 0),
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
