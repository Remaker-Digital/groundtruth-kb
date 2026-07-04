"""Tests for shared controlled-artifact path classification."""

from __future__ import annotations

import pytest

from scripts.controlled_artifact_paths import (
    classify_controlled_artifact,
    direct_write_block_reason_code,
    is_bridge_status_artifact_path,
    is_protected_path,
    is_runtime_authority_state_path,
    is_versioned_bridge_status_file,
)


@pytest.mark.parametrize(
    ("path", "reason_code", "classification"),
    [
        ("bridge/example-001.md", "bridge_status_file_direct_mutation", "bridge/<slug>-NNN.md"),
        ("./bridge/example-123.md", "bridge_status_file_direct_mutation", "bridge/<slug>-NNN.md"),
        ("bridge/INDEX.md", "bridge_index_direct_mutation", "bridge/INDEX.md"),
        ("groundtruth.db", "membase_direct_mutation", "groundtruth.db"),
        (
            ".gtkb-state/implementation-authorizations/current.json",
            "runtime_authority_state_direct_mutation",
            ".gtkb-state/implementation-authorizations/",
        ),
        (
            ".gtkb-state/work-intent/thread.json",
            "runtime_authority_state_direct_mutation",
            ".gtkb-state/work-intent/",
        ),
        (
            ".gtkb-state/bridge-poller/dispatch-state.json",
            "runtime_authority_state_direct_mutation",
            ".gtkb-state/bridge-poller/",
        ),
        (
            ".gtkb-state/dispatcher-daemon/status.json",
            "runtime_authority_state_direct_mutation",
            ".gtkb-state/dispatcher-daemon/",
        ),
    ],
)
def test_direct_controlled_artifacts_are_block_classified(path: str, reason_code: str, classification: str) -> None:
    result = classify_controlled_artifact(path)

    assert result.is_controlled is True
    assert result.direct_write_blocked is True
    assert result.reason_code == reason_code
    assert result.classification == classification


@pytest.mark.parametrize(
    "path",
    [
        "bridge/design-note.md",
        "bridge/example.md",
        ".gtkb-state/bridge-impl-reports/drafts/report.md",
        ".gtkb-state/bridge-revisions/drafts/revision.md",
        ".gtkb-state/state.json",
        "independent-progress-assessments/report.md",
    ],
)
def test_diagnostic_and_non_status_bridge_paths_remain_open(path: str) -> None:
    result = classify_controlled_artifact(path)

    assert result.is_controlled is False
    assert result.direct_write_blocked is False
    assert is_protected_path(path) is False


def test_bridge_status_helpers_are_specific() -> None:
    assert is_versioned_bridge_status_file("bridge/example-001.md") is True
    assert is_versioned_bridge_status_file("bridge/example.md") is False
    assert is_bridge_status_artifact_path("bridge/INDEX.md") is True
    assert is_bridge_status_artifact_path("bridge/example-001.md") is True
    assert is_bridge_status_artifact_path("bridge/example.md") is False


def test_runtime_authority_state_helper_is_specific() -> None:
    assert is_runtime_authority_state_path("groundtruth.db") is True
    assert is_runtime_authority_state_path(".gtkb-state/implementation-authorizations/current.json") is True
    assert is_runtime_authority_state_path(".gtkb-state/bridge-impl-reports/drafts/report.md") is False


def test_multi_surface_reason_collapses_to_generic_direct_mutation() -> None:
    assert (
        direct_write_block_reason_code(["bridge/example-001.md", "groundtruth.db"])
        == "controlled_artifact_direct_mutation"
    )
