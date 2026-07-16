from __future__ import annotations

import json
import sys
import tomllib
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "groundtruth-kb" / "src"))

from groundtruth_kb.bridge_dispatch_config import (  # noqa: E402
    apply_dispatch_config_to_record,
    collect_bridge_dispatch_status,
    load_bridge_dispatch_config,
)
from groundtruth_kb.bridge_dispatch_report import build_bridge_dispatch_report  # noqa: E402
from groundtruth_kb.bridge_dispatch_transactions import add_harness, set_caps  # noqa: E402


def _write_dispatch_config(root: Path, *, override: bool = False) -> None:
    path = root / "config" / "dispatcher" / "rules.toml"
    path.parent.mkdir(parents=True, exist_ok=True)
    override_line = "max_items_override = true\n" if override else ""
    path.write_text(
        (
            'schema_version = 1\nselection_order = ["harness_id"]\nrules = []\n\n'
            "[harnesses.A]\n"
            "max_items = 4\n"
            f"{override_line}"
        ),
        encoding="utf-8",
    )


def _write_registry(root: Path, *, max_items: object = 1) -> None:
    dispatch = {
        "can_receive_dispatch": True,
        "can_fire_events": False,
        "dispatch_cost": 60,
        "dispatch_quality": 90,
        "dispatch_availability": 90,
    }
    if max_items is not None:
        dispatch["dispatch_max_items"] = max_items
    path = root / "harness-state" / "harness-registry.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "source_of_truth": "test",
                "harnesses": [
                    {
                        "id": "A",
                        "harness_name": "codex",
                        "harness_type": "codex",
                        "status": "active",
                        "role": ["prime-builder"],
                        "reviewer_precedence": 20,
                        **dispatch,
                    }
                ],
            }
        ),
        encoding="utf-8",
    )


@pytest.mark.parametrize(
    ("canonical", "override", "expected_cap", "expected_source"),
    [
        (1, False, 1, "harness_registry"),
        (None, False, 4, "dispatcher_config_fallback"),
        ("malformed", False, 4, "dispatcher_config_fallback"),
        (0, False, 4, "dispatcher_config_fallback"),
        (1, True, 4, "dispatcher_config_override"),
    ],
)
def test_cap_precedence_is_explicit_and_idempotent(
    tmp_path: Path,
    canonical: object,
    override: bool,
    expected_cap: int,
    expected_source: str,
) -> None:
    _write_dispatch_config(tmp_path, override=override)
    config = load_bridge_dispatch_config(tmp_path)
    record = {"id": "A"}
    if canonical is not None:
        record["dispatch_max_items"] = canonical

    first = apply_dispatch_config_to_record(record, config)
    second = apply_dispatch_config_to_record(first, config)

    assert first["dispatch_max_items"] == expected_cap
    assert first["dispatch_max_items_source"] == expected_source
    assert second == first


def test_cap_transactions_write_and_round_trip_explicit_override_marker(tmp_path: Path) -> None:
    _write_dispatch_config(tmp_path)

    set_result = set_caps(tmp_path, "A", max_items=3)
    add_result = add_harness(tmp_path, "F", description="OpenRouter", max_items=2)

    assert set_result.status == "applied"
    assert add_result.status == "applied"
    raw = tomllib.loads((tmp_path / "config" / "dispatcher" / "rules.toml").read_text(encoding="utf-8"))
    assert raw["harnesses"]["A"]["max_items"] == 3
    assert raw["harnesses"]["A"]["max_items_override"] is True
    assert raw["harnesses"]["F"]["max_items"] == 2
    assert raw["harnesses"]["F"]["max_items_override"] is True

    config = load_bridge_dispatch_config(tmp_path)
    assert config.harnesses["A"].max_items_override is True
    assert config.harnesses["F"].max_items_override is True
    audit_path = tmp_path / ".gtkb-state" / "bridge-dispatch-config-transactions" / "audit.jsonl"
    audit = [json.loads(line) for line in audit_path.read_text(encoding="utf-8").splitlines()]
    assert [row["transaction"] for row in audit] == ["set-caps", "add-harness"]


def test_status_and_report_use_the_same_canonical_cap_and_source(tmp_path: Path) -> None:
    _write_dispatch_config(tmp_path)
    _write_registry(tmp_path, max_items=1)

    status = collect_bridge_dispatch_status(tmp_path).to_json_dict()
    selected = status["selected_by_role"]["prime-builder"]

    assert len(selected) == 1
    assert selected[0]["dispatch_max_items"] == 1
    assert selected[0]["dispatch_max_items_source"] == "harness_registry"

    report = build_bridge_dispatch_report(tmp_path)
    report_selected = report["topology"]["selected_by_role"]["prime-builder"]
    assert report_selected[0]["dispatch_max_items"] == 1
    assert report_selected[0]["dispatch_max_items_source"] == "harness_registry"
    assert report["summary"]["effective_per_cycle_ceiling"]["prime-builder"] == 1
