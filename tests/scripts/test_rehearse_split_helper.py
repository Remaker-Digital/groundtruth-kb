"""Tests for Wave 2 Slice 5 _split_helper.py.

Per ``bridge/gtkb-isolation-016-phase8-wave2-slice5-005.md`` (REVISED-2)
and ``-006`` (Codex GO).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from rehearse import _split_helper  # noqa: E402


def test_classify_by_id_prefix_gtkb_returns_framework() -> None:
    assert _split_helper.classify_by_id_prefix("GTKB-FOO-001") == "framework"


def test_classify_by_id_prefix_ar_returns_adopter() -> None:
    assert _split_helper.classify_by_id_prefix("AR-FOO-001") == "adopter"


def test_classify_by_id_prefix_unknown_returns_unknown() -> None:
    assert _split_helper.classify_by_id_prefix("MYPROJECT-001") == "unknown"
    assert _split_helper.classify_by_id_prefix("") == "unknown"


def test_partition_items_buckets_correctly() -> None:
    items = [
        {"id": "GTKB-1"},
        {"id": "AR-1"},
        {"id": "OTHER-1"},
        {"id": "GTKB-2"},
    ]

    def _classifier(item: dict) -> tuple[str, str]:
        prefix_class = _split_helper.classify_by_id_prefix(item["id"])
        if prefix_class == "framework":
            return ("framework", "gtkb_prefix")
        if prefix_class == "adopter":
            return ("adopter", "ar_prefix")
        return ("unclassified", "unknown_prefix")

    buckets = _split_helper.partition_items(items, _classifier)
    assert len(buckets["framework"]) == 2
    assert len(buckets["adopter"]) == 1
    assert len(buckets["unclassified"]) == 1
    # classification_signal appended to each item
    assert all("classification_signal" in r for r in buckets["framework"])
    assert all("classification_signal" in r for r in buckets["adopter"])
    assert all("classification_signal" in r for r in buckets["unclassified"])
    # Original input not mutated
    assert "classification_signal" not in items[0]


def test_build_split_summary_counts_per_bucket() -> None:
    buckets = {
        "framework": [{}, {}, {}],
        "adopter": [{}],
        "unclassified": [{}, {}],
    }
    summary = _split_helper.build_split_summary(buckets)
    assert summary == {
        "framework_count": 3,
        "adopter_count": 1,
        "unclassified_count": 2,
        "total": 6,
    }


def test_classify_with_content_override_routes_gtkb_prefix_conflict_to_unclassified() -> None:
    """Per Slice 5 -004 F1 + Slice 6 -002 F2: GTKB-* + adopter content
    conflict goes to unclassified, NOT silent adopter override."""
    classification, signal = _split_helper.classify_with_content_override(
        "GTKB-MIXED-001",
        "Some text mentioning Agent Red migration tooling.",
    )
    assert classification == "unclassified"
    assert signal == "gtkb_prefix_with_adopter_content"


def test_classify_with_content_override_keeps_clean_gtkb_as_framework() -> None:
    classification, signal = _split_helper.classify_with_content_override(
        "GTKB-CLEAN-001",
        "Pure framework spec with no adopter mentions.",
    )
    assert classification == "framework"
    assert signal == "gtkb_prefix"


def test_classify_with_content_override_ar_prefix_returns_adopter() -> None:
    classification, signal = _split_helper.classify_with_content_override("AR-DASH-001", "")
    assert classification == "adopter"
    assert signal == "ar_prefix"


def test_emit_result_writes_file_and_self_references(tmp_path: Path) -> None:
    """result.json is written and its path appears in output_files."""
    lane_dir = tmp_path / "lane"
    lane_dir.mkdir()
    initial_result = {
        "status": "ok",
        "output_files": [str(tmp_path / "lane" / "data.json")],
        "metrics": {"x": 1},
        "warnings": [],
    }
    returned = _split_helper.emit_result(lane_dir, initial_result)
    result_path = lane_dir / "result.json"
    assert result_path.exists()
    assert str(result_path) in returned["output_files"]
    on_disk = json.loads(result_path.read_text(encoding="utf-8"))
    assert on_disk == returned
