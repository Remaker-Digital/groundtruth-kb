"""Specification-derived tests for WI-5266 resource identity and closure."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

import pytest

from groundtruth_kb.context.resource_routing import (
    dispatch_resource_selection,
    render_resource_context,
    resolve_resource_selection,
)

FIXED_TIME = datetime(2026, 7, 15, tzinfo=UTC)
REPO_ROOT = Path(__file__).resolve().parents[2]
PACKAGE_SRC = REPO_ROOT / "groundtruth-kb" / "src"


@pytest.mark.parametrize(
    ("prompt", "expected"),
    [
        ("Auto-process the Top Backlog items", ["backlog"]),
        (
            "Process P0/P1 backlog, beginning with all bridge/TAFE/harness-related items",
            ["backlog"],
        ),
        ("Process the bridge queue", ["bridge_queue"]),
        ("Review the review queue", ["bridge_queue"]),
        ("Continue bridge work for the TAFE harness", []),
        ("Investigate bridge-related harness behavior", []),
        ("A bridgeless build and backlogless fixture", []),
    ],
)
def test_literal_resource_terms_are_boundary_aware(prompt: str, expected: list[str]) -> None:
    selection = resolve_resource_selection(prompt)

    assert selection["selected_resources"] == expected
    assert selection["primary_resource"] == (expected[0] if len(expected) == 1 else None)


def test_explicit_multi_resource_request_has_no_silent_winner() -> None:
    selection = resolve_resource_selection("Compare the current backlog with the bridge queue")

    assert selection["selected_resources"] == ["backlog", "bridge_queue"]
    assert selection["primary_resource"] is None
    assert selection["read_routes"] == {
        "backlog": "gt backlog list",
        "bridge_queue": "gt bridge state-report",
    }


@pytest.mark.parametrize("dispatch_run_id", [None, "", "   "])
def test_blank_dispatch_provenance_cannot_default_the_bridge_queue(dispatch_run_id: str | None) -> None:
    assert dispatch_resource_selection(dispatch_run_id)["selected_resources"] == []


def test_work_item_ids_and_compact_context_follow_current_literal_selection() -> None:
    selection = resolve_resource_selection("Process backlog item wi-5266 before WI-5267")
    context = render_resource_context(selection)

    assert selection["work_item_ids"] == ["WI-5266", "WI-5267"]
    assert selection["selection_authority"] == "current_owner_literal"
    assert "`backlog` via `gt backlog list`" in context
    assert "distinct, non-alias resources" in context
