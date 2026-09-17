"""Initialization never overwrites an existing application or targets a path outside the registered slot."""

from __future__ import annotations

from pathlib import Path

import pytest

from groundtruth_kb.project.scaffold import application_files, scaffold_project


def test_second_scaffold_against_existing_adopter_raises(clean_adopter, native_application) -> None:
    adopter, _host = clean_adopter
    before = {path: (adopter / path).read_bytes() for path in application_files(adopter)}
    with pytest.raises(ValueError, match="gt project upgrade"):
        scaffold_project(native_application.options("Alpha", profile="dual-agent"))
    assert {path: (adopter / path).read_bytes() for path in application_files(adopter)} == before


def test_scaffold_refuses_target_outside_applications_dir(native_application, tmp_path: Path) -> None:
    outside = tmp_path / "not-an-application"
    outside.mkdir()
    with pytest.raises(ValueError, match="registered application root"):
        scaffold_project(native_application.options("Alpha", target_dir=outside))
    assert list(outside.iterdir()) == []
