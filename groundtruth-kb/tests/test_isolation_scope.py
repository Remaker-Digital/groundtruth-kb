"""Application-scope selection shared by scope-aware readers (groundtruth_kb.isolation.scope)."""

from __future__ import annotations

from pathlib import Path

import pytest

from groundtruth_kb.isolation.scope import (
    APPLICATION_MARKER,
    PLATFORM_SCOPE,
    ApplicationScopeError,
    default_application_scope,
    explicit_application_scope,
    marker_application_scope,
    select_application_scope,
)


@pytest.mark.parametrize("scope", ["gtkb_platform", "application:Alpha", "application:agent-red_2"])
def test_explicit_scope_forms_pass_through(scope: str) -> None:
    assert explicit_application_scope(scope) == scope
    assert select_application_scope(Path("nowhere"), scope) == scope


@pytest.mark.parametrize("scope", ["", "platform", "agent_red_application", "application:", "Application:Alpha"])
def test_explicit_scope_of_another_form_is_refused(scope: str) -> None:
    with pytest.raises(ApplicationScopeError) as refused:
        explicit_application_scope(scope)
    assert refused.value.code == "invalid_application_scope"
    assert isinstance(refused.value, ValueError)


def test_root_without_a_marker_selects_the_platform_scope(tmp_path: Path) -> None:
    assert marker_application_scope(tmp_path) is None
    assert default_application_scope(tmp_path) == PLATFORM_SCOPE == "gtkb_platform"
    assert select_application_scope(tmp_path, None) == PLATFORM_SCOPE
    assert default_application_scope(tmp_path / "absent") == PLATFORM_SCOPE


def test_marker_names_the_application_scope(tmp_path: Path) -> None:
    (tmp_path / APPLICATION_MARKER).write_text('[application]\nname = "Alpha"\n', encoding="utf-8")
    assert marker_application_scope(tmp_path) == "application:Alpha"
    assert default_application_scope(tmp_path) == "application:Alpha"
    assert select_application_scope(tmp_path, None) == "application:Alpha"
    assert select_application_scope(tmp_path, "gtkb_platform") == "gtkb_platform"


@pytest.mark.parametrize(
    ("marker", "message"),
    [
        ("[application]\n", "must name the registered application"),
        ('[application]\nname = ""\n', "must name the registered application"),
        ('name = "Alpha"\n', "must name the registered application"),
        ('[application\nname = "Alpha"\n', "cannot be read"),
    ],
)
def test_a_marker_that_names_no_application_is_refused(tmp_path: Path, marker: str, message: str) -> None:
    (tmp_path / APPLICATION_MARKER).write_text(marker, encoding="utf-8")
    with pytest.raises(ApplicationScopeError, match=message):
        default_application_scope(tmp_path)
    # An explicit selection never reads the marker.
    assert select_application_scope(tmp_path, "application:Beta") == "application:Beta"


def test_a_marker_directory_is_not_a_marker(tmp_path: Path) -> None:
    (tmp_path / APPLICATION_MARKER).mkdir()
    assert default_application_scope(tmp_path) == PLATFORM_SCOPE
