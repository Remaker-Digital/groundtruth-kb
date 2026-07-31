"""Tests for shared formal-artifact approval packet validation."""

from __future__ import annotations

import sys
from collections.abc import Mapping
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / "groundtruth-kb" / "src"))

from groundtruth_kb.governance.approval_packet import (  # noqa: E402
    construct_approval_packet,
    validate_packet,
)


def _packet(postimage_fields: Mapping[str, object] | None = None) -> dict[str, object]:
    kwargs: dict[str, object] = {}
    if postimage_fields is not None:
        kwargs["postimage_fields"] = postimage_fields
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
        **kwargs,
    )


def test_valid_manual_approval_packet_passes() -> None:
    packet = _packet()
    assert not {"postimage_schema_version", "postimage_fields", "postimage_sha256"} & set(packet)
    assert validate_packet(packet).is_valid is True


def test_postimage_hash_is_deterministic_for_reordered_nested_unicode() -> None:
    left = {
        "title": "Café Δ",
        "nested": {"β": [1, True, None, {"雪": "☃"}]},
        "empty": [],
    }
    right = {
        "empty": [],
        "nested": {"β": [1, True, None, {"雪": "☃"}]},
        "title": "Café Δ",
    }

    left_packet = _packet(left)
    right_packet = _packet(right)

    assert left_packet["postimage_sha256"] == right_packet["postimage_sha256"]
    assert left_packet["postimage_sha256"] == "d25a83a700e6748ad746fb01c1650313d5491efad87985a11559b0f97baf2a5b"
    assert validate_packet(left_packet).is_valid is True


@pytest.mark.parametrize(
    "field_name",
    ["postimage_schema_version", "postimage_fields", "postimage_sha256"],
)
def test_postimage_extension_requires_atomic_trio(field_name: str) -> None:
    packet = _packet({"title": "Bound title"})
    packet.pop(field_name)

    result = validate_packet(packet)

    assert result.is_valid is False
    assert "postimage extension missing required fields" in result.errors[0]


@pytest.mark.parametrize("schema_version", [True, 1.0, 2])
def test_postimage_schema_version_must_be_exact_integer_one(schema_version: object) -> None:
    packet = _packet({"title": "Bound title"})
    packet["postimage_schema_version"] = schema_version

    result = validate_packet(packet)

    assert result.is_valid is False
    assert "postimage_schema_version must be integer 1" in result.errors[0]


@pytest.mark.parametrize(
    "fields",
    [
        {},
        {"nested": {1: "non-string key"}},
        {"value": ("tuple",)},
        {"value": {"set"}},
        {"value": b"bytes"},
        {"value": float("nan")},
        {"value": float("inf")},
        {"value": float("-inf")},
    ],
)
def test_postimage_rejects_non_json_native_or_empty_fields(fields: dict[object, object]) -> None:
    packet = _packet({"title": "Bound title"})
    packet["postimage_fields"] = fields

    result = validate_packet(packet)

    assert result.is_valid is False
    assert "postimage_fields" in result.errors[0]


def test_postimage_rejects_wrong_hash() -> None:
    packet = _packet({"title": "Bound title"})
    packet["postimage_sha256"] = "0" * 64

    result = validate_packet(packet)

    assert result.is_valid is False
    assert "postimage_sha256" in result.errors[0]


def test_postimage_hash_binds_existing_packet_identity_fields() -> None:
    packet = _packet({"title": "Bound title"})
    packet["action"] = "update"

    result = validate_packet(packet)

    assert result.is_valid is False
    assert "postimage_sha256" in result.errors[0]


def test_postimage_rejects_reference_cycles_without_raising() -> None:
    cyclic: list[object] = []
    cyclic.append(cyclic)
    packet = _packet({"title": "Bound title"})
    packet["postimage_fields"] = {"cyclic": cyclic}

    result = validate_packet(packet)

    assert result.is_valid is False
    assert "reference cycles" in result.errors[0]


def test_postimage_preserves_explicit_empty_values_and_detaches_input() -> None:
    tags: list[str] = []
    constraints: dict[str, object] = {}
    nested = {"values": ["original"]}
    fields: dict[str, object] = {
        "tags": tags,
        "constraints": constraints,
        "priority": None,
        "nested": nested,
    }
    packet = _packet(fields)

    tags.append("late")
    constraints["late"] = True
    nested["values"].append("late")

    assert packet["postimage_fields"] == {
        "tags": [],
        "constraints": {},
        "priority": None,
        "nested": {"values": ["original"]},
    }
    assert validate_packet(packet).is_valid is True


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


def test_gap_state_capture_requires_context_and_intended_operation() -> None:
    packet = construct_approval_packet(
        artifact_type="deliberation",
        artifact_id="DELIB-9002",
        action="create",
        source_ref="bridge:gap-state",
        full_content="Owner-approved gap-state deliberation content.",
        approval_mode="approve",
        presented_to_user=True,
        transcript_captured=True,
        explicit_change_request="AUQ S999: approve gap-state capture.",
        approved_by="owner",
        changed_by="test",
        change_reason="gap-state formal artifact capture",
        capture_context="gap_state",
        gap_state_bridge_id="gtkb-gap-state-example",
        gap_state_reason="requirement sufficiency gap-state proposal needs formal artifact capture",
        intended_db_operation={"method": "insert_deliberation", "source_ref": "bridge:gap-state"},
    )

    assert validate_packet(packet).is_valid is True

    packet.pop("intended_db_operation")
    result = validate_packet(packet)
    assert result.is_valid is False
    assert "intended_db_operation" in result.errors[0]


def test_expired_packet_fails() -> None:
    packet = _packet()
    packet["expires_at"] = (datetime.now(UTC) - timedelta(days=1)).isoformat()
    result = validate_packet(packet)
    assert result.is_valid is False
    assert "expired" in result.errors[0]
