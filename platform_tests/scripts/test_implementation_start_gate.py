"""Spec-derived tests for implementation-start authorization gate."""

from __future__ import annotations

import json
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
        db.insert_project_authorization(
            "PROJECT-AUTH",
            "Authorized implementation project",
            "DELIB-PROJECT-AUTH",
            "Bounded project implementation scope.",
            "test",
            "seed project authorization",
            id="PAUTH-AUTH",
            status=status,
        )
    finally:
        db.close()


def test_go_authorization_packet_allows_in_scope_apply_patch(tmp_path: Path) -> None:
    _write_thread(tmp_path)
    packet = auth.create_authorization_packet(tmp_path, "sample-implementation")
    auth.write_packet(tmp_path, packet)

    payload = {
        "cwd": str(tmp_path),
        "tool_name": "apply_patch",
        "tool_input": {"patch": "*** Begin Patch\n*** Update File: scripts/sample.py\n@@\n+pass\n*** End Patch\n"},
    }

    assert gate.gate_decision(payload) == {}


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


def test_requirement_gap_blocks_authorization(tmp_path: Path) -> None:
    _write_thread(
        tmp_path,
        proposal=_proposal(
            requirement_sufficiency="New or revised requirement required before implementation - capture it first."
        ),
    )

    with pytest.raises(auth.AuthorizationError, match="new or revised requirements"):
        auth.create_authorization_packet(tmp_path, "sample-implementation")


def test_project_authorization_metadata_is_carried_in_packet(tmp_path: Path) -> None:
    _seed_project_authorization(tmp_path)
    proposal = _proposal() + "\nProject Authorization: `PAUTH-AUTH`\nProject: `PROJECT-AUTH`\nWork Item: `WI-AUTH-001`\n"
    _write_thread(tmp_path, proposal=proposal)

    packet = auth.create_authorization_packet(tmp_path, "sample-implementation")
    auth.write_packet(tmp_path, packet)

    assert packet["project_authorization"]["id"] == "PAUTH-AUTH"
    assert packet["project_authorization"]["project_id"] == "PROJECT-AUTH"
    assert packet["project_authorization"]["work_item_id"] == "WI-AUTH-001"
    assert auth.load_packet(tmp_path)["project_authorization"]["id"] == "PAUTH-AUTH"


def test_project_authorization_load_revalidates_current_spec_exclusions(tmp_path: Path) -> None:
    _seed_project_authorization(tmp_path)
    proposal = _proposal() + "\nProject Authorization: `PAUTH-AUTH`\nProject: `PROJECT-AUTH`\nWork Item: `WI-AUTH-001`\n"
    _write_thread(tmp_path, proposal=proposal)
    packet = auth.create_authorization_packet(tmp_path, "sample-implementation")
    auth.write_packet(tmp_path, packet)

    db = KnowledgeDB(tmp_path / "groundtruth.db")
    try:
        db.update_project_authorization(
            "PAUTH-AUTH",
            "test",
            "exclude linked governing spec",
            excluded_spec_ids=["GOV-FILE-BRIDGE-AUTHORITY-001"],
        )
    finally:
        db.close()

    with pytest.raises(auth.AuthorizationError, match="Spec link\\(s\\) excluded"):
        auth.load_packet(tmp_path)


def test_project_authorization_does_not_broaden_target_scope(tmp_path: Path) -> None:
    _seed_project_authorization(tmp_path)
    proposal = _proposal() + "\nProject Authorization: `PAUTH-AUTH`\nProject: `PROJECT-AUTH`\nWork Item: `WI-AUTH-001`\n"
    _write_thread(tmp_path, proposal=proposal)
    packet = auth.create_authorization_packet(tmp_path, "sample-implementation")
    auth.write_packet(tmp_path, packet)

    with pytest.raises(auth.AuthorizationError, match="outside implementation authorization scope"):
        auth.validate_targets(tmp_path, ["groundtruth-kb/src/groundtruth_kb/db.py"])


def test_project_authorization_requires_work_item_membership_or_inclusion(tmp_path: Path) -> None:
    _seed_project_authorization(tmp_path, link_work_item=False)
    proposal = _proposal() + "\nProject Authorization: `PAUTH-AUTH`\nProject: `PROJECT-AUTH`\nWork Item: `WI-AUTH-001`\n"
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
