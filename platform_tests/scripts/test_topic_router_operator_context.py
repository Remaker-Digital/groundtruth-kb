"""Activity rendering points assigned work at the canonical context reader."""

from pathlib import Path

from groundtruth_kb.session import topic_router


def render(activity: str, root: Path) -> str:
    return topic_router.render_topic_context(
        {"action": "open", "topic_type": activity, "project_root": str(root), "topic": {"route_target": "assigned"}}
    )


def test_deliberation_does_not_select_implementation_work(tmp_path: Path) -> None:
    context = render("deliberation", tmp_path)
    assert "- activity: deliberation" in context
    assert "- direction.stance: capture-and-clarify" in context
    assert "### Current Task Context" not in context
    assert "### Top Priority Actions" not in context
    assert list(tmp_path.iterdir()) == []


def test_build_routes_assigned_work_to_current_requirements_without_claiming_loaded_context(tmp_path: Path) -> None:
    context = render("build", tmp_path)
    assert "### Current Task Context" in context
    assert "gt context work-item <work-item-id>" in context
    assert "assigned by the owner or dispatcher" in context
    assert "test instructions and prerequisites" in context
    assert "unavailable" in context and "recovery route" in context
    assert "session envelope packet" not in context
    assert "### Top Priority Actions" not in context
    assert "status=ready" not in context
    assert list(tmp_path.iterdir()) == []


def test_missing_activity_profile_reports_missing_context_without_fabricated_bootstrap(
    tmp_path: Path, monkeypatch
) -> None:
    monkeypatch.setattr(topic_router, "load_activity_profiles", lambda: {})
    context = render("build", tmp_path)
    assert "activity disposition profile unavailable" in context
    assert "### Current Task Context" not in context
    assert "### Top Priority Actions" not in context
    assert list(tmp_path.iterdir()) == []
