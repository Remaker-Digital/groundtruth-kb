from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

import pytest
from groundtruth_kb.session.packet import (
    ACTIVITY_PACKET_TOKEN_CAP,
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
    assert packet["ttl"]["seconds"] == 300
    assert packet["cache"]["hit"] is False
    assert "session-startup-index" in packet["source_hashes"]
    assert packet["source_hashes"]["session-startup-index"].startswith("sha256:")
    assert {descriptor["cache_policy"] for descriptor in packet["live_query_descriptors"]} == {"live_query_only"}
    assert "bridge-thread-state" in {descriptor["source_id"] for descriptor in packet["live_query_descriptors"]}


def test_activity_packet_uses_ttl_cache_when_sources_and_ttl_match(tmp_path: Path) -> None:
    root = _project(tmp_path)
    cache_dir = root / ".cache"
    generated_at = datetime(2026, 7, 17, 12, 0, tzinfo=UTC)

    first = compose_packet(
        project_root=root,
        packet_kind="activity-packet",
        activity="build",
        role="prime-builder",
        cache_dir=cache_dir,
        generated_at=generated_at,
    )
    second = compose_packet(
        project_root=root,
        packet_kind="activity-packet",
        activity="build",
        role="prime-builder",
        cache_dir=cache_dir,
        generated_at=generated_at,
    )

    assert first["packet_kind"] == "activity-packet"
    assert first["activity"] == "build"
    assert first["status"] == "ready"
    assert first["budget"]["cap_estimated_tokens"] == ACTIVITY_PACKET_TOKEN_CAP
    assert first["budget"]["estimated_tokens"] <= ACTIVITY_PACKET_TOKEN_CAP
    assert second["cache"]["status"] == "hit"
    assert second["budget"]["estimated_tokens"] <= ACTIVITY_PACKET_TOKEN_CAP

    unrelated_startup_source = root / "config" / "agent-control" / "SESSION-STARTUP-INDEX.md"
    unrelated_startup_source.write_text("startup index changed\n", encoding="utf-8")
    third = compose_packet(
        project_root=root,
        packet_kind="activity-packet",
        activity="build",
        role="prime-builder",
        cache_dir=cache_dir,
        generated_at=generated_at,
    )

    assert third["cache"]["status"] == "hit"


def test_session_packet_cache_misses_when_tracked_source_hash_changes(tmp_path: Path) -> None:
    root = _project(tmp_path)
    cache_dir = root / ".cache"
    generated_at = datetime(2026, 7, 17, 12, 0, tzinfo=UTC)

    first = compose_packet(
        project_root=root,
        packet_kind="session-envelope",
        cache_dir=cache_dir,
        generated_at=generated_at,
    )
    (root / "config" / "agent-control" / "SESSION-STARTUP-INDEX.md").write_text(
        "startup index changed\n",
        encoding="utf-8",
    )
    second = compose_packet(
        project_root=root,
        packet_kind="session-envelope",
        cache_dir=cache_dir,
        generated_at=generated_at,
    )

    assert first["source_hashes"]["session-startup-index"] != second["source_hashes"]["session-startup-index"]
    assert first["cache"]["cache_key"] != second["cache"]["cache_key"]
    assert second["cache"]["status"] == "miss"


def test_packet_cache_misses_when_ttl_expires(tmp_path: Path) -> None:
    root = _project(tmp_path)
    cache_dir = root / ".cache"

    first = compose_packet(
        project_root=root,
        packet_kind="session-envelope",
        cache_dir=cache_dir,
        ttl_seconds=60,
        generated_at=datetime(2026, 7, 17, 12, 0, tzinfo=UTC),
    )
    second = compose_packet(
        project_root=root,
        packet_kind="session-envelope",
        cache_dir=cache_dir,
        ttl_seconds=60,
        generated_at=datetime(2026, 7, 17, 12, 1, 1, tzinfo=UTC),
    )

    assert first["cache"]["cache_key"] == second["cache"]["cache_key"]
    assert second["cache"]["status"] == "miss"


def test_packet_cache_misses_on_non_object_json_entry(tmp_path: Path) -> None:
    root = _project(tmp_path)
    cache_dir = root / ".cache"
    generated_at = datetime(2026, 7, 17, 12, 0, tzinfo=UTC)

    first = compose_packet(
        project_root=root,
        packet_kind="session-envelope",
        cache_dir=cache_dir,
        generated_at=generated_at,
    )
    cache_path = root / first["cache"]["cache_path"]
    cache_path.write_text("[]\n", encoding="utf-8")
    second = compose_packet(
        project_root=root,
        packet_kind="session-envelope",
        cache_dir=cache_dir,
        generated_at=generated_at,
    )

    assert second["cache"]["cache_key"] == first["cache"]["cache_key"]
    assert second["cache"]["status"] == "miss"


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
