from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

import pytest
from groundtruth_kb.session.packet import (
    SESSION_ENVELOPE_TOKEN_CAP,
    PacketError,
    compose_packet,
)


def _project(tmp_path: Path) -> Path:
    root = tmp_path / "project"
    root.mkdir()
    startup_dir = root / "config" / "agent-control"
    startup_dir.mkdir(parents=True)
    (startup_dir / "SESSION-STARTUP-INDEX.md").write_text("startup index\n", encoding="utf-8")
    (startup_dir / "PRIME-BUILDER-STARTUP-OVERLAY.md").write_text("prime overlay\n", encoding="utf-8")
    (startup_dir / "LOYAL-OPPOSITION-STARTUP-OVERLAY.md").write_text("lo overlay\n", encoding="utf-8")
    return root


def test_session_envelope_packet_is_budgeted_and_live_state_pointer_only(tmp_path: Path) -> None:
    root = _project(tmp_path)

    packet = compose_packet(
        project_root=root,
        packet_kind="session-envelope",
        cache_dir=tmp_path / "cache",
        generated_at=datetime(2026, 7, 17, 12, 0, tzinfo=UTC),
    )

    assert packet["packet_kind"] == "session-envelope"
    assert packet["status"] == "ready"
    assert packet["budget"]["cap_estimated_tokens"] == SESSION_ENVELOPE_TOKEN_CAP
    assert packet["budget"]["estimated_tokens"] <= SESSION_ENVELOPE_TOKEN_CAP
    # WI-7318: the packet has no TTL or cache-validity concept. It declares the
    # composition policy instead, and every call composes from live sources.
    assert packet["composition"] == {"policy": "real_time_per_invocation", "cached": False}
    assert "session-startup-index" in packet["source_hashes"]
    assert packet["source_hashes"]["session-startup-index"].startswith("sha256:")
    assert {descriptor["cache_policy"] for descriptor in packet["live_query_descriptors"]} == {"live_query_only"}
    assert "bridge-thread-state" in {descriptor["source_id"] for descriptor in packet["live_query_descriptors"]}


def test_pointer_only_packet_is_returned_when_budget_would_be_exceeded(tmp_path: Path) -> None:
    root = _project(tmp_path)

    packet = compose_packet(
        project_root=root,
        packet_kind="activity-packet",
        activity="build",
        cache_dir=tmp_path / "cache",
        budget_cap_tokens=100,
        generated_at=datetime(2026, 7, 17, 12, 0, tzinfo=UTC),
    )

    assert packet["status"] == "over_budget_pointer_only"
    assert packet["diagnostic"]["pointer_only"] is True
    assert packet["budget"]["candidate_estimated_tokens"] > 100
    assert packet["budget"]["estimated_tokens"] <= 100
    assert "payload" not in packet


def test_activity_packet_requires_activity(tmp_path: Path) -> None:
    with pytest.raises(PacketError, match="activity is required"):
        compose_packet(project_root=_project(tmp_path), packet_kind="activity-packet")
