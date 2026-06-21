from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "groundtruth-kb" / "src"))

from groundtruth_kb.bridge_dispatch_config import (  # noqa: E402
    BridgeDispatchConfig,
    HarnessDispatchConfig,
    collect_bridge_dispatch_status,
    select_dispatch_candidates,
)
from groundtruth_kb.bridge_dispatch_rules import DispatchContext  # noqa: E402


def _dispatch_config(
    *,
    selection_order: tuple[str, ...] = ("cost", "quality", "harness_id"),
    harnesses: dict[str, HarnessDispatchConfig] | None = None,
) -> BridgeDispatchConfig:
    return BridgeDispatchConfig(
        path=Path("config/dispatcher/rules.toml"),
        exists=True,
        schema_version=1,
        selection_order=selection_order,
        harnesses=harnesses or {},
    )


def _record(
    harness_id: str,
    *,
    role: str = "loyal-opposition",
    cost: float = 50.0,
    quality: float | None = None,
) -> dict:
    record = {
        "id": harness_id,
        "harness_name": harness_id.lower(),
        "harness_type": "test",
        "status": "active",
        "role": [role],
        "can_receive_dispatch": True,
        "can_fire_events": role == "prime-builder",
        "dispatch_cost": cost,
        "reviewer_precedence": 10,
    }
    if quality is not None:
        record["dispatch_quality"] = quality
    return record


def _write_project(root: Path, *, harnesses: list[dict]) -> None:
    (root / "config" / "dispatcher").mkdir(parents=True)
    (root / "config" / "dispatcher" / "rules.toml").write_text(
        """
schema_version = 1
selection_order = ["cost", "quality", "harness_id"]
rules = []
""".lstrip(),
        encoding="utf-8",
    )
    (root / "harness-state").mkdir()
    (root / "harness-state" / "harness-registry.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "source_of_truth": "test",
                "harnesses": harnesses,
            }
        ),
        encoding="utf-8",
    )


def test_lo_quality_floor_excludes_explicit_subfloor_candidates_before_cost_ranking() -> None:
    records = [
        _record("F", cost=20.0, quality=72.0),
        _record("A", cost=35.0, quality=88.0),
    ]

    selected = select_dispatch_candidates(
        records,
        _dispatch_config(),
        DispatchContext(required_role="loyal-opposition"),
    )

    assert [row["id"] for row in selected] == ["A"]


def test_lo_quality_floor_uses_overlayed_dispatch_quality() -> None:
    records = [_record("F", cost=20.0, quality=72.0)]
    config = _dispatch_config(
        harnesses={
            "F": HarnessDispatchConfig(
                harness_id="F",
                dispatch_quality=85.0,
            )
        }
    )

    selected = select_dispatch_candidates(
        records,
        config,
        DispatchContext(required_role="loyal-opposition"),
    )

    assert [row["id"] for row in selected] == ["F"]
    assert selected[0]["dispatch_quality"] == 85.0


def test_prime_builder_selection_is_not_affected_by_lo_floor() -> None:
    records = [
        _record("B", role="prime-builder", cost=10.0, quality=10.0),
        _record("A", role="prime-builder", cost=20.0, quality=95.0),
    ]

    selected = select_dispatch_candidates(
        records,
        _dispatch_config(),
        DispatchContext(required_role="prime-builder"),
    )

    assert [row["id"] for row in selected] == ["B", "A"]


def test_missing_dispatch_quality_uses_ranker_default_and_fails_lo_floor() -> None:
    records = [
        _record("D", cost=20.0),
        _record("F", cost=35.0),
    ]

    selected = select_dispatch_candidates(
        records,
        _dispatch_config(),
        DispatchContext(required_role="loyal-opposition"),
    )

    assert selected == []


def test_malformed_dispatch_quality_uses_ranker_default_and_fails_lo_floor() -> None:
    records = [_record("F", cost=20.0, quality=95.0)]
    records[0]["dispatch_quality"] = "not-a-number"

    selected = select_dispatch_candidates(
        records,
        _dispatch_config(),
        DispatchContext(required_role="loyal-opposition"),
    )

    assert selected == []


def test_lo_quality_floor_fails_closed_when_no_explicit_candidate_qualifies(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _write_project(
        tmp_path,
        harnesses=[
            _record("B", role="prime-builder", cost=70.0, quality=95.0),
            _record("C", cost=35.0, quality=78.0),
            _record("D", cost=20.0, quality=62.0),
            _record("F", cost=20.0, quality=72.0),
        ],
    )
    monkeypatch.setenv("GTKB_HARNESS_REGISTRY_PATH", str(tmp_path / "harness-state" / "harness-registry.json"))

    status = collect_bridge_dispatch_status(tmp_path)

    assert status.selected_by_role["loyal-opposition"] == []
    assert status.health_status == "FAIL"
    assert any("loyal-opposition" in finding for finding in status.health_findings)
