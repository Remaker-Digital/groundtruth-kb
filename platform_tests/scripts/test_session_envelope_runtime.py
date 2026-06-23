"""Focused tests for the WI-4301 session-envelope runtime."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from groundtruth_kb.session import topic_router
from groundtruth_kb.session.envelope import (
    TOPIC_TYPES,
    EnvelopeError,
    archive_dir,
    close_topic,
    current_envelope_path,
    open_session,
    open_topic,
)
from groundtruth_kb.session.topic_router import (
    handle_topic_command,
    parse_topic_command,
    render_topic_context,
)
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
        init_keyword="::init gtkb pb",
        role="prime-builder",
        active_work_item_id="WI-4301",
    )

    current = current_envelope_path(tmp_path, "codex")
    assert current.is_file()
    saved = json.loads(current.read_text(encoding="utf-8"))
    assert saved["session_id"] == envelope["session_id"]
    assert saved["harness_id"] == "A"
    assert saved["role_resolved"] == "prime-builder"
    assert saved["role_resolution"]["interactive_resolved_role"] == "prime-builder"
    assert saved["role_resolution"]["interactive_role_source"] == "transcript_init_keyword"
    assert saved["role_resolution"]["durable_registry_role"] == "loyal-opposition"
    assert saved["role_resolution"]["authority_mode"] == "interactive_transcript"
    assert "non-overriding" in saved["role_resolution"]["durable_registry_authority"]
    assert saved["active_work_item_id"] == "WI-4301"


def test_open_session_without_role_uses_durable_registry_fallback(tmp_path: Path) -> None:
    _seed_harness(tmp_path)

    open_session(tmp_path, harness_name="codex")

    saved = json.loads(current_envelope_path(tmp_path, "codex").read_text(encoding="utf-8"))
    assert saved["role_resolved"] == "loyal-opposition"
    assert saved["role_resolution"]["interactive_role_source"] is None
    assert saved["role_resolution"]["durable_registry_role"] == "loyal-opposition"
    assert saved["role_resolution"]["authority_mode"] == "durable_registry_fallback"


def test_topic_open_close_is_strict_and_one_per_type(tmp_path: Path) -> None:
    _seed_harness(tmp_path)
    open_session(tmp_path, harness_name="codex")

    assert set(TOPIC_TYPES) == {"ops", "deliberation", "build", "test", "spec", "project"}

    topic = open_topic(tmp_path, "spec", harness_name="codex")
    assert topic["route_target"] == "spec-governance-service"
    assert topic["preload_state"]["sources"]
    with pytest.raises(EnvelopeError, match="already open"):
        open_topic(tmp_path, "spec", harness_name="codex")

    closed = close_topic(tmp_path, "spec", harness_name="codex")
    assert closed["closed_at"]
    assert closed["close_outcome"] == "closed"


def test_ops_topic_route_and_preload_are_available(tmp_path: Path) -> None:
    _seed_harness(tmp_path)
    open_session(tmp_path, harness_name="codex")

    topic = open_topic(tmp_path, "ops", harness_name="codex")

    assert topic["route_target"] == "operations-status-decision-service"
    assert topic["preload_state"]["sources"] == [
        "operations_status",
        "support_user_activity",
        "ops_feedback_inputs",
    ]
    with pytest.raises(EnvelopeError, match="already open"):
        open_topic(tmp_path, "ops", harness_name="codex")


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
    assert parse_topic_command("::open ops").topic_type == "ops"  # type: ignore[union-attr]
    assert parse_topic_command("::close ops").action == "close"  # type: ignore[union-attr]
    assert parse_topic_command("\n::close project\nnotes").action == "close"  # type: ignore[union-attr]
    assert parse_topic_command("::open") is None
    assert parse_topic_command("::open  spec") is None
    assert parse_topic_command("::close unknown") is None


def test_render_topic_context_injects_activity_profile_for_open(tmp_path: Path) -> None:
    _seed_harness(tmp_path)
    open_session(tmp_path, harness_name="codex")
    command = parse_topic_command("::open build")
    assert command is not None

    result = handle_topic_command(tmp_path, command, harness_name="codex")
    assert result["project_root"] == str(tmp_path)
    context = render_topic_context(result)

    assert "## Activity Disposition Profile" in context
    assert "- name: build" in context
    assert "- headless_eligibility: headless_eligible" in context
    assert "- skills: bridge, bridge-propose, verify, kb-work-item, kb-spec" in context
    assert "- terminology: implementation proposal, implementation report, work item" in context
    assert "- history_state.sources: GO'd bridge proposals, active PAUTH authorizations" in context
    assert "- direction.stance: implement-within-scope" in context
    assert "- direction.guardrails: no implementation without a GO'd bridge proposal" in context
    assert "- direction.manipulates: source files, test files" in context
    assert "## Open Activity Operator Context" in context


def test_render_topic_context_does_not_inject_profile_for_close(tmp_path: Path) -> None:
    _seed_harness(tmp_path)
    open_session(tmp_path, harness_name="codex")
    open_topic(tmp_path, "build", harness_name="codex")
    command = parse_topic_command("::close build")
    assert command is not None

    result = handle_topic_command(tmp_path, command, harness_name="codex")
    context = render_topic_context(result)

    assert "`::close build` accepted." in context
    assert "## Activity Disposition Profile" not in context
    assert "## Open Activity Operator Context" not in context


def test_render_topic_context_injects_operator_context_for_open(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    class FakeStartup:
        GRAFANA_DASHBOARD_URL = "http://localhost:3000/d/gtkb/groundtruth-kb-dashboard"

        @staticmethod
        def build_startup_model(project_root: Path, *, role_profile: str, fast_hook: bool) -> dict:
            assert project_root == tmp_path.resolve()
            assert role_profile == "prime-builder"
            assert fast_hook is True
            return {
                "workstream_focus": {"current_label": "GT-KB Infrastructure Focus"},
                "session_overlay": {},
            }

        @staticmethod
        def render_active_work_subject(*args, **kwargs) -> str:
            return "- Current work subject is GT-KB Infrastructure Focus."

        @staticmethod
        def _render_session_startup_briefing(model: dict) -> str:
            return "- Operator briefing: compact."

        @staticmethod
        def _render_top_priority_actions_section(model: dict) -> str:
            return "### Top Priority Actions\n\n1. **WI-1**: Synthetic priority (priority: P1)"

    monkeypatch.setattr(topic_router, "_load_startup_module", lambda _root: FakeStartup)
    context = render_topic_context(
        {
            "action": "open",
            "topic_type": "build",
            "project_root": str(tmp_path),
            "topic": {"route_target": "build-package-scaffold-service"},
        }
    )

    assert "## Open Activity Operator Context" in context
    assert (
        "- Dashboard: GroundTruth-KB Project Dashboard: http://localhost:3000/d/gtkb/groundtruth-kb-dashboard"
        in context
    )
    assert "### Active Work Subject" in context
    assert "- Current work subject is GT-KB Infrastructure Focus." in context
    assert "### Session Startup Briefing" in context
    assert "- Operator briefing: compact." in context
    assert "### Top Priority Actions" in context
    assert "**WI-1**" in context


def test_render_topic_context_profile_loader_failure_is_non_blocking(monkeypatch: pytest.MonkeyPatch) -> None:
    def fail_loader():
        raise topic_router.ActivityProfileError("profile config unavailable")

    monkeypatch.setattr(topic_router, "load_activity_profiles", fail_loader)
    context = render_topic_context(
        {
            "action": "open",
            "topic_type": "build",
            "topic": {"route_target": "build-package-scaffold-service"},
        }
    )

    assert "`::open build` accepted." in context
    assert "## Activity Disposition Profile" in context
    assert "- status: unavailable" in context
    assert "- reason: profile config unavailable" in context
