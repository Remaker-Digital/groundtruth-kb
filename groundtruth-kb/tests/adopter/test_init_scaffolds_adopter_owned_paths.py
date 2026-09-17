"""A fresh application contains every minimum profile file and only application-owned or derived paths."""

from __future__ import annotations

import pytest

from groundtruth_kb.project.scaffold import application_files, enumerate_scaffold_outputs

RETIRED_LOCAL_ARTIFACTS = (
    "groundtruth.db",
    "MEMORY.md",
    "CLAUDE.md",
    "memory/release-readiness.md",
    "BRIDGE-INVENTORY.md",
    ".claude/session/work-subject.json",
)


def test_clean_adopter_contains_every_minimum_file(clean_adopter) -> None:
    adopter, _host = clean_adopter
    observed = application_files(adopter)
    missing = [path for path in enumerate_scaffold_outputs("dual-agent") if path not in observed]
    assert not missing, missing


def test_clean_adopter_scaffold_count_is_nonzero(clean_adopter) -> None:
    adopter, _host = clean_adopter
    assert len(application_files(adopter) - {"application.toml"}) >= 5


@pytest.mark.parametrize("rel_path", ["README.md", "groundtruth.toml", ".githooks/reference-transaction"])
def test_clean_adopter_owned_entry_points_present(clean_adopter, rel_path: str) -> None:
    adopter, _host = clean_adopter
    assert (adopter / rel_path).is_file()


@pytest.mark.parametrize("rel_path", RETIRED_LOCAL_ARTIFACTS)
def test_retired_local_state_artifacts_are_not_created(clean_adopter, rel_path: str) -> None:
    """Local authority stores, prompt notes and banners were retired with the SQLite-era scaffold."""
    adopter, _host = clean_adopter
    assert not (adopter / rel_path).exists()
