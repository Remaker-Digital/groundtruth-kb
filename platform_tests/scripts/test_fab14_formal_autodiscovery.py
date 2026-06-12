"""FAB-14 HYG-047: formal-artifact gate packet auto-discovery."""

from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
_HOOK = _ROOT / ".claude" / "hooks" / "formal-artifact-approval-gate.py"
_spec = importlib.util.spec_from_file_location("_fab14_formal_gate", _HOOK)
gate = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(gate)


def _write_packet(approvals: Path, name: str, artifact_id: str, content: str) -> None:
    approvals.mkdir(parents=True, exist_ok=True)
    packet = {
        "artifact_type": "design_constraint",
        "artifact_id": artifact_id,
        "action": "update",
        "source_ref": "fab-14 test",
        "full_content": content,
        "full_content_sha256": hashlib.sha256(content.encode("utf-8")).hexdigest(),
        "approval_mode": "approve",
        "presented_to_user": True,
        "transcript_captured": True,
        "explicit_change_request": "test",
        "changed_by": "test",
        "change_reason": "fab14",
        "approved_by": "owner",
    }
    (approvals / name).write_text(json.dumps(packet), encoding="utf-8")


def test_formal_autodiscover_finds_matching_artifact_and_content(tmp_path: Path) -> None:
    content = "# DCL-TEST\n\nBody.\n"
    content_file = tmp_path / "candidate.md"
    content_file.write_text(content, encoding="utf-8")
    _write_packet(
        tmp_path / ".groundtruth" / "formal-artifact-approvals",
        "packet.json",
        "DCL-TEST",
        content,
    )

    command = f"gt spec update --id DCL-TEST --content-file {content_file}"

    assert gate._autodiscover_packet(tmp_path, command) is not None


def test_formal_autodiscover_rejects_artifact_mismatch(tmp_path: Path) -> None:
    content = "# DCL-TEST\n\nBody.\n"
    content_file = tmp_path / "candidate.md"
    content_file.write_text(content, encoding="utf-8")
    _write_packet(
        tmp_path / ".groundtruth" / "formal-artifact-approvals",
        "packet.json",
        "DCL-OTHER",
        content,
    )

    command = f"gt spec update --id DCL-TEST --content-file {content_file}"

    assert gate._autodiscover_packet(tmp_path, command) is None


def test_formal_autodiscover_rejects_content_mismatch(tmp_path: Path) -> None:
    content_file = tmp_path / "candidate.md"
    content_file.write_text("# DCL-TEST\n\nNew body.\n", encoding="utf-8")
    _write_packet(
        tmp_path / ".groundtruth" / "formal-artifact-approvals",
        "packet.json",
        "DCL-TEST",
        "# DCL-TEST\n\nOld body.\n",
    )

    command = f"gt spec update --id DCL-TEST --content-file {content_file}"

    assert gate._autodiscover_packet(tmp_path, command) is None
