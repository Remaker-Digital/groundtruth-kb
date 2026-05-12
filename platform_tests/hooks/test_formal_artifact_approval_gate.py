"""Tests for the formal artifact approval PreToolUse hook."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
HOOK = REPO_ROOT / ".claude" / "hooks" / "formal-artifact-approval-gate.py"
sys.path.insert(0, str(REPO_ROOT / "groundtruth-kb" / "src"))

from groundtruth_kb.governance.approval_packet import validate_packet  # noqa: E402


def _run_hook(command: str) -> dict:
    payload = {"tool_name": "Bash", "tool_input": {"command": command}}
    result = subprocess.run(
        ["python", str(HOOK)],
        cwd=REPO_ROOT,
        input=json.dumps(payload),
        text=True,
        capture_output=True,
        check=True,
    )
    return json.loads(result.stdout)


def _packet(tmp_path: Path, *, approval_mode: str = "approve", transcript_captured: bool = True) -> Path:
    content = "artifact_type: governance\nid: GOV-EXAMPLE-001\nbody: Full native proposal\n"
    packet = {
        "artifact_type": "governance",
        "artifact_id": "GOV-EXAMPLE-001",
        "action": "insert",
        "source_ref": "conversation:test",
        "full_content": content,
        "full_content_sha256": hashlib.sha256(content.encode("utf-8")).hexdigest(),
        "approval_mode": approval_mode,
        "presented_to_user": True,
        "transcript_captured": transcript_captured,
        "explicit_change_request": "Create GOV-EXAMPLE-001 from owner-approved packet.",
        "changed_by": "test",
        "change_reason": "test approval packet",
    }
    if approval_mode == "auto":
        packet["auto_approval_scope"] = "governance"
        packet["auto_approval_activated_by"] = "owner"
    else:
        packet["approved_by"] = "Mike"

    path = tmp_path / "approval.json"
    path.write_text(json.dumps(packet), encoding="utf-8")
    return path


def test_non_formal_command_passes_without_packet() -> None:
    assert _run_hook("python -m pytest tests/scripts/test_groundtruth_governance_adoption.py") == {}


def test_formal_deliberation_write_blocks_without_packet() -> None:
    response = _run_hook("python -m groundtruth_kb deliberations upsert --source-type owner_conversation")

    assert response["decision"] == "block"
    assert "GOV-ARTIFACT-APPROVAL-001" in response["reason"]
    assert "does not reference" in response["reason"]


def test_formal_write_allows_manual_approval_packet(tmp_path: Path) -> None:
    packet_path = _packet(tmp_path)

    response = _run_hook(f'GTKB_FORMAL_APPROVAL_PACKET="{packet_path}" python -m groundtruth_kb deliberations upsert')

    assert response == {}


def test_formal_write_allows_scoped_auto_approval_packet(tmp_path: Path) -> None:
    packet_path = _packet(tmp_path, approval_mode="auto")

    response = _run_hook(f'GTKB_FORMAL_APPROVAL_PACKET="{packet_path}" python -m groundtruth_kb deliberations upsert')

    assert response == {}


def test_auto_approval_requires_transcript_capture(tmp_path: Path) -> None:
    packet_path = _packet(tmp_path, approval_mode="auto", transcript_captured=False)

    response = _run_hook(f'GTKB_FORMAL_APPROVAL_PACKET="{packet_path}" python -m groundtruth_kb deliberations upsert')

    assert response["decision"] == "block"
    assert "transcript_captured=true" in response["reason"]


def test_python_membase_mutation_blocks_without_packet() -> None:
    response = _run_hook("python -c \"db.insert_spec('GOV-1', 'T', 'specified', 'me', 'reason')\"")

    assert response["decision"] == "block"
    assert "formal artifact mutation" in response["reason"]


def test_high_level_spec_record_command_is_not_hook_matched() -> None:
    response = _run_hook("python -m groundtruth_kb spec record --id GOV-EXAMPLE-001")

    assert response == {}


def test_hook_and_shared_validator_agree_on_packet_fixtures(tmp_path: Path) -> None:
    valid_path = _packet(tmp_path)
    valid_packet = json.loads(valid_path.read_text(encoding="utf-8"))
    assert validate_packet(valid_packet).is_valid is True
    assert _run_hook(f'GTKB_FORMAL_APPROVAL_PACKET="{valid_path}" python -m groundtruth_kb deliberations upsert') == {}

    invalid_packet = dict(valid_packet)
    invalid_packet["full_content_sha256"] = "bad"
    invalid_path = tmp_path / "bad-approval.json"
    invalid_path.write_text(json.dumps(invalid_packet), encoding="utf-8")
    assert validate_packet(invalid_packet).is_valid is False
    response = _run_hook(f'GTKB_FORMAL_APPROVAL_PACKET="{invalid_path}" python -m groundtruth_kb deliberations upsert')
    assert response["decision"] == "block"
    assert "sha256" in response["reason"]
