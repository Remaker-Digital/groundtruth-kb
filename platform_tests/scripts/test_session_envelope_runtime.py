"""Focused tests for the WI-4301 session-envelope runtime."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from groundtruth_kb.session.envelope import (
    EnvelopeError,
    archive_dir,
    close_topic,
    current_envelope_path,
    open_session,
    open_topic,
)
from groundtruth_kb.session.topic_router import parse_topic_command
from groundtruth_kb.session.wrap import is_canonical_wrap_trigger, run_wrap


def _seed_harness(root: Path) -> None:
    state = root / "harness-state"
    state.mkdir(parents=True)
    (state / "harness-identities.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "harnesses": {"codex": {"id": "A"}},
            }
        ),
        encoding="utf-8",
    )
    (state / "harness-registry.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "harnesses": [{"id": "A", "harness_name": "codex", "role": ["loyal-opposition"]}],
            }
        ),
        encoding="utf-8",
    )


def test_open_session_writes_current_per_harness_envelope(tmp_path: Path) -> None:
    _seed_harness(tmp_path)

    envelope = open_session(
        tmp_path,
        harness_name="codex",
        init_keyword="::init gtkb lo",
        active_work_item_id="WI-4301",
    )

    current = current_envelope_path(tmp_path, "codex")
    assert current.is_file()
    saved = json.loads(current.read_text(encoding="utf-8"))
    assert saved["session_id"] == envelope["session_id"]
    assert saved["harness_id"] == "A"
    assert saved["role_resolved"] == "loyal-opposition"
    assert saved["active_work_item_id"] == "WI-4301"


def test_topic_open_close_is_strict_and_one_per_type(tmp_path: Path) -> None:
    _seed_harness(tmp_path)
    open_session(tmp_path, harness_name="codex")

    topic = open_topic(tmp_path, "spec", harness_name="codex")
    assert topic["route_target"] == "spec-governance-service"
    assert topic["preload_state"]["sources"]
    with pytest.raises(EnvelopeError, match="already open"):
        open_topic(tmp_path, "spec", harness_name="codex")

    closed = close_topic(tmp_path, "spec", harness_name="codex")
    assert closed["closed_at"]
    assert closed["close_outcome"] == "closed"


def test_run_wrap_archives_envelope_with_mandatory_step_results(tmp_path: Path) -> None:
    _seed_harness(tmp_path)
    open_session(tmp_path, harness_name="codex")
    open_topic(tmp_path, "test", harness_name="codex")

    result = run_wrap(tmp_path, harness_name="codex", wrap_outcome="canonical_wrap")

    archive_path = result["archive_path"]
    assert archive_path.parent == archive_dir(tmp_path, "codex")
    assert archive_path.is_file()
    assert not current_envelope_path(tmp_path, "codex").exists()
    archived = json.loads(archive_path.read_text(encoding="utf-8"))
    assert archived["status"] == "closed"
    assert archived["wrap_outcome"] == "canonical_wrap"
    assert {item["step"] for item in archived["wrap_step_results"]} >= {1, 4, 8, 11, 12}
    step_11 = next(item for item in archived["wrap_step_results"] if item["step"] == 11)
    assert step_11["closed_topic_count"] == 1
    assert archived["topics"][0]["close_outcome"] == "auto_closed_by_session_wrap"


def test_wrap_and_topic_command_parsers_are_strict() -> None:
    assert is_canonical_wrap_trigger("::wrap")
    assert is_canonical_wrap_trigger("\n::wrap\nlater text")
    assert not is_canonical_wrap_trigger("::wrap ")
    assert not is_canonical_wrap_trigger("::WRAP")

    assert parse_topic_command("::open spec").topic_type == "spec"  # type: ignore[union-attr]
    assert parse_topic_command("\n::close project\nnotes").action == "close"  # type: ignore[union-attr]
    assert parse_topic_command("::open") is None
    assert parse_topic_command("::open  spec") is None
    assert parse_topic_command("::close unknown") is None
