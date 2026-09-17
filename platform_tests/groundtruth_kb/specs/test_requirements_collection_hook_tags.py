"""GOV-REQUIREMENTS-COLLECTION-HOOK-001 carries only its live tags (WI-3381 regression guard, native form)."""

from __future__ import annotations

SPEC_ID = "GOV-REQUIREMENTS-COLLECTION-HOOK-001"
EXPECTED_TAGS = ["governance", "requirements-collection", "user-prompt-submit-hook", "3-option-clarification"]
STALE_V4_TAGS = {"llm-classification", "retrieval-augmented"}


def test_requirements_collection_hook_carries_only_live_tags(formal_record):
    record = formal_record(SPEC_ID)
    assert record["type"] == "governance"
    assert record["tags"] == EXPECTED_TAGS
    assert STALE_V4_TAGS.isdisjoint(record["tags"])
