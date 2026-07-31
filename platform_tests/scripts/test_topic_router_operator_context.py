"""Regression tests for topic-router open-activity operator context."""

from __future__ import annotations

from pathlib import Path

from groundtruth_kb.session import topic_router
from groundtruth_kb.session.topic_router import render_topic_context


def _open_result(activity: str, project_root: Path) -> dict[str, object]:
    return {
        "action": "open",
        "topic_type": activity,
        "project_root": str(project_root),
        "topic": {"route_target": f"{activity}-route"},
    }


class _FakeStartup:
    GRAFANA_DASHBOARD_URL = "http://localhost:3000/d/gtkb/groundtruth-kb-dashboard"

    @staticmethod
    def build_startup_model(project_root: Path, *, role_profile: str, fast_hook: bool) -> dict[str, object]:
        assert role_profile == "prime-builder"
        assert fast_hook is True
        return {
            "workstream_focus": {"current_label": f"Synthetic focus at {project_root.name}"},
            "session_overlay": {},
        }

    @staticmethod
    def render_active_work_subject(*args, **kwargs) -> str:
        return "- Current work subject is synthetic implementation work."

    @staticmethod
    def _render_session_startup_briefing(model: dict[str, object]) -> str:
        return "- Operator briefing: compact."

    @staticmethod
    def _render_top_priority_actions_section(model: dict[str, object]) -> str:
        return "### Top Priority Actions\n\n1. **WI-1**: Synthetic priority (priority: P1)"


def test_deliberation_operator_context_uses_stance_without_prime_briefing(tmp_path: Path, monkeypatch) -> None:
    def fail_startup_load(_project_root: Path):
        raise AssertionError("deliberation activity must not load the Prime startup briefing")

    monkeypatch.setattr(topic_router, "_load_startup_module", fail_startup_load)

    context = render_topic_context(_open_result("deliberation", tmp_path))

    assert "## Open Activity Operator Context" in context
    assert "- context_source: activity_disposition_profile" in context
    assert "- direction.stance: capture-and-clarify" in context
    assert "- history_state.sources: prior deliberations on the topic, pending owner decisions" in context
    assert "- direction.guardrails: do not implement during a deliberation session" in context
    assert "### Session Startup Briefing" not in context
    assert "### Top Priority Actions" not in context
    assert "### Active Work Subject" not in context
    assert "Operator briefing: compact" not in context


def test_build_operator_context_keeps_prime_implementation_briefing(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(topic_router, "_load_startup_module", lambda _project_root: _FakeStartup)

    context = render_topic_context(_open_result("build", tmp_path))

    assert "- direction.stance: implement-within-scope" in context
    assert "### Active Work Subject" in context
    assert "### Session Startup Briefing" in context
    assert "- Operator briefing: compact." in context
    assert "### Top Priority Actions" in context


def test_missing_activity_profile_falls_back_to_existing_startup_briefing(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(topic_router, "load_activity_profiles", lambda: {})
    monkeypatch.setattr(topic_router, "_load_startup_module", lambda _project_root: _FakeStartup)

    context = render_topic_context(_open_result("build", tmp_path))

    assert "- reason: no profile configured for activity 'build'" in context
    assert "### Session Startup Briefing" in context
    assert "- Operator briefing: compact." in context
