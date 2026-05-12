"""Tests for shared formal-artifact approval packet validation."""

from __future__ import annotations

import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / "groundtruth-kb" / "src"))

from groundtruth_kb.governance.approval_packet import (  # noqa: E402
    construct_approval_packet,
    validate_packet,
)


def _packet() -> dict[str, object]:
    return construct_approval_packet(
        artifact_type="deliberation",
        artifact_id="DELIB-9001",
        action="create",
        source_ref="conversation:test",
        full_content="Owner-approved deliberation content.",
        approval_mode="approve",
        presented_to_user=True,
        transcript_captured=True,
        explicit_change_request="AUQ S999: approve recording this deliberation.",
        approved_by="owner",
        changed_by="test",
        change_reason="test approval packet",
    )


def test_valid_manual_approval_packet_passes() -> None:
    assert validate_packet(_packet()).is_valid is True


def test_manual_packet_requires_approved_or_acknowledged_by() -> None:
    packet = _packet()
    packet.pop("approved_by")
    result = validate_packet(packet)
    assert result.is_valid is False
    assert "approved_by or acknowledged_by" in result.errors[0]


def test_hash_mismatch_fails() -> None:
    packet = _packet()
    packet["full_content_sha256"] = "bad"
    result = validate_packet(packet)
    assert result.is_valid is False
    assert "sha256" in result.errors[0]


def test_presented_to_user_false_fails() -> None:
    packet = _packet()
    packet["presented_to_user"] = False
    result = validate_packet(packet)
    assert result.is_valid is False
    assert "presented_to_user=true" in result.errors[0]


def test_transcript_captured_false_fails() -> None:
    packet = _packet()
    packet["transcript_captured"] = False
    result = validate_packet(packet)
    assert result.is_valid is False
    assert "transcript_captured=true" in result.errors[0]


def test_auto_mode_requires_owner_activated_scope() -> None:
    packet = _packet()
    packet["approval_mode"] = "auto"
    packet.pop("approved_by")
    result = validate_packet(packet)
    assert result.is_valid is False
    assert "auto_approval_scope" in result.errors[0]

    packet["auto_approval_scope"] = "governance"
    result = validate_packet(packet)
    assert result.is_valid is False
    assert "auto_approval_activated_by='owner'" in result.errors[0]

    packet["auto_approval_activated_by"] = "owner"
    assert validate_packet(packet).is_valid is True


def test_expired_packet_fails() -> None:
    packet = _packet()
    packet["expires_at"] = (datetime.now(UTC) - timedelta(days=1)).isoformat()
    result = validate_packet(packet)
    assert result.is_valid is False
    assert "expired" in result.errors[0]
