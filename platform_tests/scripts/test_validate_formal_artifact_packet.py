"""Paired tests for scripts/validate_formal_artifact_packet.py.

Each test exercises one branch of the live gate's ``_validate_packet`` so the
helper is verified to track gate semantics by construction. Tests use the
gate module's actual constants via ``importlib`` so a rename/refactor in the
gate surfaces here as ``AttributeError`` rather than silently passing.

Authority: WI-3266 + bridge/gtkb-formal-artifact-packet-validator-cli-001.md.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import subprocess
import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
HELPER = PROJECT_ROOT / "scripts" / "validate_formal_artifact_packet.py"
GATE = PROJECT_ROOT / ".claude" / "hooks" / "formal-artifact-approval-gate.py"


def _load_gate() -> Any:
    spec = importlib.util.spec_from_file_location("gate_under_test", GATE)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)  # type: ignore[union-attr]
    return module


def _sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _valid_packet() -> dict[str, Any]:
    content = "Test content for formal artifact validation."
    return {
        "artifact_type": "design_constraint",
        "artifact_id": "DCL-TEST-WI-3266-PACKET",
        "action": "insert",
        "source_ref": "bridge/gtkb-formal-artifact-packet-validator-cli-001.md",
        "full_content": content,
        "full_content_sha256": _sha256(content),
        "approval_mode": "approve",
        "presented_to_user": True,
        "transcript_captured": True,
        "explicit_change_request": "owner directive: please proceed with WI-3266",
        "changed_by": "prime-builder/claude",
        "change_reason": "WI-3266 Slice 1 test fixture",
        "approved_by": "owner",
    }


def _run_helper(packet_path: Path) -> tuple[int, str, str]:
    """Run the helper as a subprocess and return (exit_code, stdout, stderr)."""
    result = subprocess.run(
        [sys.executable, str(HELPER), str(packet_path)],
        cwd=str(PROJECT_ROOT),
        capture_output=True,
        text=True,
        check=False,
    )
    return result.returncode, result.stdout, result.stderr


@pytest.fixture
def packet_dir(tmp_path: Path) -> Path:
    return tmp_path


def _write_packet(packet_dir: Path, name: str, packet: dict[str, Any]) -> Path:
    path = packet_dir / f"{name}.json"
    path.write_text(json.dumps(packet, indent=2), encoding="utf-8")
    return path


def test_happy_path_exits_zero_and_prints_canonical_line(packet_dir: Path) -> None:
    """Valid packet -> exit 0 + 'packet_valid: <path>' stdout line."""
    path = _write_packet(packet_dir, "valid", _valid_packet())
    exit_code, stdout, stderr = _run_helper(path)
    assert exit_code == 0, f"expected 0, got {exit_code}; stderr={stderr}"
    assert f"packet_valid: {path}" in stdout
    assert stderr == ""


def test_missing_required_field_exits_one_with_gate_message(packet_dir: Path) -> None:
    """Removing a REQUIRED_PACKET_FIELDS entry -> exit 1 + gate's missing-fields message."""
    packet = _valid_packet()
    del packet["transcript_captured"]
    path = _write_packet(packet_dir, "missing_field", packet)
    exit_code, _, stderr = _run_helper(path)
    assert exit_code == 1
    # _validate_packet returns the missing-fields message FIRST when a required
    # field is absent. The transcript_captured-specific message only fires
    # when the field is present but not literally True.
    assert "approval packet missing required fields" in stderr
    assert "transcript_captured" in stderr


def test_invalid_artifact_type_exits_one_with_gate_message(packet_dir: Path) -> None:
    """artifact_type outside VALID_ARTIFACT_TYPES -> exit 1 + gate's specific error."""
    packet = _valid_packet()
    packet["artifact_type"] = "not_a_real_type"
    path = _write_packet(packet_dir, "bad_type", packet)
    exit_code, _, stderr = _run_helper(path)
    assert exit_code == 1
    assert "artifact_type must be one of" in stderr
    assert "not_a_real_type" in stderr


def test_invalid_approval_mode_exits_one_with_gate_message(packet_dir: Path) -> None:
    """approval_mode outside VALID_APPROVAL_MODES -> exit 1 + gate's specific error."""
    packet = _valid_packet()
    packet["approval_mode"] = "rubber-stamp"
    path = _write_packet(packet_dir, "bad_mode", packet)
    exit_code, _, stderr = _run_helper(path)
    assert exit_code == 1
    assert "approval_mode must be one of" in stderr
    assert "rubber-stamp" in stderr


def test_full_content_sha256_mismatch_exits_one_with_gate_message(packet_dir: Path) -> None:
    """full_content_sha256 not matching full_content -> exit 1 + gate's hash-mismatch error."""
    packet = _valid_packet()
    packet["full_content_sha256"] = "0" * 64
    path = _write_packet(packet_dir, "bad_hash", packet)
    exit_code, _, stderr = _run_helper(path)
    assert exit_code == 1
    assert "full_content_sha256 does not match" in stderr


def test_presented_to_user_false_exits_one_with_gate_message(packet_dir: Path) -> None:
    """presented_to_user must be exactly True -> exit 1 + gate's per-flag error."""
    packet = _valid_packet()
    packet["presented_to_user"] = False
    path = _write_packet(packet_dir, "not_presented", packet)
    exit_code, _, stderr = _run_helper(path)
    assert exit_code == 1
    assert "requires presented_to_user=true" in stderr


def test_auto_mode_without_scope_exits_one_with_gate_message(packet_dir: Path) -> None:
    """approval_mode='auto' requires auto_approval_scope -> exit 1 + gate's specific error."""
    packet = _valid_packet()
    packet["approval_mode"] = "auto"
    # Remove approved_by to force the gate down the auto path rather than the manual fallback.
    del packet["approved_by"]
    path = _write_packet(packet_dir, "auto_no_scope", packet)
    exit_code, _, stderr = _run_helper(path)
    assert exit_code == 1
    assert "auto approval requires auto_approval_scope" in stderr


def test_expired_packet_exits_one_with_gate_message(packet_dir: Path) -> None:
    """expires_at in the past -> exit 1 + gate's expiry error."""
    packet = _valid_packet()
    past = (datetime.now(UTC) - timedelta(days=1)).isoformat().replace("+00:00", "Z")
    packet["expires_at"] = past
    path = _write_packet(packet_dir, "expired", packet)
    exit_code, _, stderr = _run_helper(path)
    assert exit_code == 1
    assert "approval packet is expired" in stderr


def test_missing_argument_exits_two_with_usage_hint() -> None:
    """No packet path argument -> exit 2 + usage hint on stderr."""
    result = subprocess.run(
        [sys.executable, str(HELPER)],
        cwd=str(PROJECT_ROOT),
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 2
    assert "usage:" in result.stderr.lower()


def test_helper_constants_track_live_gate() -> None:
    """Regression guard: gate's REQUIRED_PACKET_FIELDS / VALID_ARTIFACT_TYPES.

    This test imports the gate module the same way the helper does and asserts
    the public constants exist with non-empty contents. If the gate is later
    refactored to rename or remove these, the helper would silently lose
    coverage; this assertion catches that.
    """
    gate = _load_gate()
    assert isinstance(gate.REQUIRED_PACKET_FIELDS, set)
    assert gate.REQUIRED_PACKET_FIELDS, "REQUIRED_PACKET_FIELDS must be non-empty"
    assert isinstance(gate.VALID_ARTIFACT_TYPES, set)
    assert gate.VALID_ARTIFACT_TYPES, "VALID_ARTIFACT_TYPES must be non-empty"
    assert isinstance(gate.VALID_APPROVAL_MODES, set)
    assert "approve" in gate.VALID_APPROVAL_MODES
    # Validate the helper functions exist
    assert callable(gate._load_packet)
    assert callable(gate._validate_packet)
