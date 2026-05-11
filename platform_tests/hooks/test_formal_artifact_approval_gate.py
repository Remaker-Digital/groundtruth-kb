"""Tests for the formal artifact approval PreToolUse hook."""

from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
HOOK = REPO_ROOT / ".claude" / "hooks" / "formal-artifact-approval-gate.py"


def _run_hook(command: str) -> dict:
    payload = {"tool_name": "Bash", "tool_input": {"command": command}}
    result = subprocess.run(
        ["python", str(HOOK)],
        cwd=REPO_ROOT,
        input=json.dumps(payload),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
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

    response = _run_hook(
        f'GTKB_FORMAL_APPROVAL_PACKET="{packet_path}" python -m groundtruth_kb deliberations upsert'
    )

    assert response == {}


def test_formal_write_allows_scoped_auto_approval_packet(tmp_path: Path) -> None:
    packet_path = _packet(tmp_path, approval_mode="auto")

    response = _run_hook(
        f'GTKB_FORMAL_APPROVAL_PACKET="{packet_path}" python -m groundtruth_kb deliberations upsert'
    )

    assert response == {}


def test_auto_approval_requires_transcript_capture(tmp_path: Path) -> None:
    packet_path = _packet(tmp_path, approval_mode="auto", transcript_captured=False)

    response = _run_hook(
        f'GTKB_FORMAL_APPROVAL_PACKET="{packet_path}" python -m groundtruth_kb deliberations upsert'
    )

    assert response["decision"] == "block"
    assert "transcript_captured=true" in response["reason"]


def test_python_membase_mutation_blocks_without_packet() -> None:
    response = _run_hook('python -c "db.insert_spec(\'GOV-1\', \'T\', \'specified\', \'me\', \'reason\')"')

    assert response["decision"] == "block"
    assert "formal artifact mutation" in response["reason"]
