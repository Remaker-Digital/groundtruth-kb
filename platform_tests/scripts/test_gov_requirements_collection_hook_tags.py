"""Regression guard for WI-3381 GOV tag-only supersession."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest
from groundtruth_kb.db import KnowledgeDB

DB_PATH = Path(__file__).resolve().parents[2] / "groundtruth.db"
SPEC_ID = "GOV-REQUIREMENTS-COLLECTION-HOOK-001"
EXPECTED_TITLE = (
    "A UserPromptSubmit hook MUST classify each owner message and force "
    "3-option clarification when a requirement candidate is detected"
)
EXPECTED_V5_TAGS = [
    "governance",
    "requirements-collection",
    "user-prompt-submit-hook",
    "3-option-clarification",
]
STALE_V4_TAGS = {"llm-classification", "retrieval-augmented"}
CONTENT_FIELDS = (
    "title",
    "description",
    "priority",
    "scope",
    "section",
    "handle",
    "status",
    "assertions",
    "type",
    "authority",
    "provisional_until",
    "constraints",
    "affected_by",
    "testability",
    "source_paths",
    "implementation_verified_at",
    "retired_at",
    "parent",
)


def _parse_json_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        value = json.loads(value)
    assert isinstance(value, list)
    return value


@pytest.fixture(scope="module")
def spec_history() -> list[dict[str, Any]]:
    if not DB_PATH.is_file():
        pytest.skip(f"MemBase not present at {DB_PATH}; GOV tag regression not checkable.")

    db = KnowledgeDB(DB_PATH)
    try:
        history = db.get_spec_history(SPEC_ID)
    finally:
        db.close()

    assert history, f"{SPEC_ID} missing from MemBase."
    return history


def test_requirements_collection_hook_gov_v5_has_only_live_tags(
    spec_history: list[dict[str, Any]],
) -> None:
    current = spec_history[0]

    assert current["version"] == 5
    assert current["title"] == EXPECTED_TITLE
    assert current["status"] == "verified"
    assert current["type"] == "governance"

    tags = _parse_json_list(current.get("tags"))
    assert tags == EXPECTED_V5_TAGS
    assert STALE_V4_TAGS.isdisjoint(tags)


def test_requirements_collection_hook_gov_v5_is_tag_only_supersession(
    spec_history: list[dict[str, Any]],
) -> None:
    current = spec_history[0]
    v4 = next((row for row in spec_history if row.get("version") == 4), None)
    assert v4 is not None, f"{SPEC_ID} v4 history row missing."

    v4_tags = set(_parse_json_list(v4.get("tags")))
    assert STALE_V4_TAGS.issubset(v4_tags)

    for field in CONTENT_FIELDS:
        assert current.get(field) == v4.get(field), f"{field} drifted in v5 tag-only supersession."
