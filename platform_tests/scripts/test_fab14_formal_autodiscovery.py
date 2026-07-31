"""FAB-14 HYG-047: formal-artifact gate packet auto-discovery."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
from pathlib import Path

from click.testing import CliRunner

_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_ROOT / "groundtruth-kb" / "src"))

from groundtruth_kb.cli import main  # noqa: E402

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


def test_cli_structured_packet_is_autodiscovered_and_tampering_is_rejected(tmp_path: Path) -> None:
    config = tmp_path / "groundtruth.toml"
    config.write_text(
        '[groundtruth]\ndb_path = "./groundtruth.db"\nproject_root = "."\n',
        encoding="utf-8",
    )
    seed_content = tmp_path / "seed.md"
    seed_content.write_text("## Constraint\nThe seed invariant must hold.\n", encoding="utf-8")
    updated_content = tmp_path / "updated.md"
    updated_content.write_text("## Constraint\nThe updated invariant must hold.\n", encoding="utf-8")
    runner = CliRunner()
    seed = runner.invoke(
        main,
        [
            "--config",
            str(config),
            "spec",
            "record",
            "--id",
            "DCL-FAB14-001",
            "--title",
            "FAB-14 seed",
            "--status",
            "specified",
            "--content-file",
            str(seed_content),
            "--change-reason",
            "seed FAB-14 integration test",
            "--auq-id",
            "S999-AUQ-FAB14-SEED",
            "--auq-answer",
            "Approved",
            "--owner-presented",
        ],
    )
    assert seed.exit_code == 0, seed.output

    updated = runner.invoke(
        main,
        [
            "--config",
            str(config),
            "spec",
            "update",
            "--id",
            "DCL-FAB14-001",
            "--content-file",
            str(updated_content),
            "--change-reason",
            "update FAB-14 structured packet",
            "--auq-id",
            "S999-AUQ-FAB14-UPDATE",
            "--auq-answer",
            "Approved",
            "--owner-presented",
            "--tags-json",
            '["fab-14"]',
            "--constraints-json",
            '{"mode": "strict"}',
            "--source-paths-json",
            '["groundtruth-kb/src/**/*.py"]',
            "--json",
        ],
    )
    assert updated.exit_code == 0, updated.output
    payload = json.loads(updated.output)
    packet_path = Path(payload["approval_packet_path"])
    assert packet_path.is_file()

    command = f"gt spec update --id DCL-FAB14-001 --content-file {updated_content}"
    assert gate._autodiscover_packet(tmp_path, command) == str(packet_path)

    packet = json.loads(packet_path.read_text(encoding="utf-8"))
    assert packet["postimage_fields"]["constraints"] == {"mode": "strict"}
    assert gate._shared_validate_packet is not None
    assert gate._validate_packet(packet) is None

    packet["postimage_sha256"] = "0" * 64
    validation_error = gate._validate_packet(packet)
    assert validation_error is not None
    assert "postimage_sha256" in validation_error
