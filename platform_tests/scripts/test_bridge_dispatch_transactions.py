"""Regression tests for WI-5012 registry-backed dispatch metadata transactions.

``set_eligibility`` and ``set_weights`` no longer write the dispatch capability
or ranking authority fields into ``config/dispatcher/rules.toml``. They append a
new MemBase harness version under ``invocation_surfaces.dispatch`` and regenerate
the static ``harness-state/harness-registry.json`` projection, which is the
dispatcher trigger's hot-path source of truth.

Specs: GOV-SOURCE-OF-TRUTH-FRESHNESS-001 (fresh canonical read),
DCL-HARNESS-STATE-SOT-READER-CONTRACT-001 (projection consistency),
ADR-DISPATCHER-ARCHITECTURE-001 (trigger honors eligibility).

(c) 2026 Remaker Digital, a DBA of VanDusen and Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import json
import sys
import tomllib
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[2]
_PACKAGE_SRC = _REPO_ROOT / "groundtruth-kb" / "src"
if str(_PACKAGE_SRC) not in sys.path:
    sys.path.insert(0, str(_PACKAGE_SRC))

from groundtruth_kb.bridge_dispatch_transactions import (  # noqa: E402
    DispatchConfigTransactionError,
    add_harness,
    set_eligibility,
    set_rule,
    set_weights,
)
from groundtruth_kb.db import KnowledgeDB  # noqa: E402
from groundtruth_kb.harness_projection import generate_harness_projection, harness_registry_path  # noqa: E402

_AUTHORITATIVE_FIELDS = {
    "can_receive_dispatch",
    "can_fire_events",
    "dispatch_cost",
    "dispatch_quality",
    "dispatch_availability",
    "reviewer_precedence",
}

_RULES_TOML = """\
schema_version = 1
selection_order = ["quality", "cost", "availability", "harness_id"]

[budget]
enabled = false
per_session_usd = 0.0
per_user_daily_usd = 0.0
soft_session_usd = 0.0
unknown_model_policy = "fail_closed"
unpriced_model_policy = "fail_open"

[budget.harnesses.D]
model = "kimi-k2-7-code-cloud"
pricing = "priced"
estimated_usd_per_dispatch = 0.0

[harnesses.D]
description = "LO"
max_items = 2
tags = ["loyal-opposition"]

[[rules]]
id = "bridge-loyal-opposition-default"
required_roles = ["loyal-opposition"]
statuses = ["NEW", "REVISED"]
prefer = ["quality", "cost", "availability", "harness_id"]
"""


def _seed(root: Path) -> None:
    """Seed a real groundtruth.db registry + policy-only rules.toml + projection."""
    root.mkdir(parents=True, exist_ok=True)
    (root / "groundtruth.toml").write_text(
        '[groundtruth]\ndb_path = "./groundtruth.db"\nproject_root = "."\n', encoding="utf-8"
    )
    (root / "config" / "dispatcher").mkdir(parents=True)
    (root / "config" / "dispatcher" / "rules.toml").write_text(_RULES_TOML, encoding="utf-8")
    db = KnowledgeDB(db_path=root / "groundtruth.db")
    db.insert_harness(
        id="D",
        harness_name="ollama",
        harness_type="ollama",
        role=["loyal-opposition"],
        changed_by="test",
        change_reason="WI-5012 dispatch metadata fixture",
        status="active",
        invocation_surfaces={
            "dispatch": {
                "can_receive_dispatch": False,
                "can_fire_events": False,
                "event_driven_hooks": False,
                "dispatch_cost": 30,
                "dispatch_quality": 80,
                "dispatch_availability": 95,
                "dispatch_max_items": 2,
                "dispatch_tags": ["loyal-opposition"],
            }
        },
    )
    generate_harness_projection(db, root)


def _projection_record(root: Path, harness_id: str) -> dict[str, object]:
    data = json.loads(harness_registry_path(root).read_text(encoding="utf-8"))
    for record in data.get("harnesses", []):
        if record.get("id") == harness_id:
            return record
    raise AssertionError(f"harness {harness_id!r} not present in projection")


def _rules_harness(root: Path, harness_id: str) -> dict[str, object]:
    rules = tomllib.loads((root / "config" / "dispatcher" / "rules.toml").read_text(encoding="utf-8"))
    return rules.get("harnesses", {}).get(harness_id, {})


def _budget_harness(root: Path, harness_id: str) -> dict[str, object]:
    rules = tomllib.loads((root / "config" / "dispatcher" / "rules.toml").read_text(encoding="utf-8"))
    return rules.get("budget", {}).get("harnesses", {}).get(harness_id, {})


def _db_dispatch_surface(root: Path, harness_id: str) -> dict[str, object]:
    row = KnowledgeDB(db_path=root / "groundtruth.db").get_harness(harness_id)
    assert row is not None
    surfaces = json.loads(row["invocation_surfaces"])
    return surfaces["dispatch"]


def _rule_statuses(root: Path, rule_id: str) -> list[str]:
    rules = tomllib.loads((root / "config" / "dispatcher" / "rules.toml").read_text(encoding="utf-8"))
    for rule in rules.get("rules", []):
        if rule.get("id") == rule_id:
            return list(rule.get("statuses", []))
    raise AssertionError(f"rule {rule_id!r} not present")


def _assert_rules_policy_only(root: Path, harness_id: str) -> None:
    assert not (_AUTHORITATIVE_FIELDS & set(_rules_harness(root, harness_id)))


def test_set_eligibility_updates_registry_projection_without_rules_authority(tmp_path: Path) -> None:
    root = tmp_path / "project"
    _seed(root)
    expected_budget = _budget_harness(root, "D")
    assert _projection_record(root, "D")["can_receive_dispatch"] is False
    _assert_rules_policy_only(root, "D")

    result = set_eligibility(root, "D", can_receive_dispatch=True, can_fire_events=None)

    assert result.status == "applied"
    assert result.mutated is True
    assert "harness registry/MemBase" in result.message
    assert "projection regenerated" in result.message
    assert _projection_record(root, "D")["can_receive_dispatch"] is True
    assert _db_dispatch_surface(root, "D")["can_receive_dispatch"] is True
    _assert_rules_policy_only(root, "D")
    assert _budget_harness(root, "D") == expected_budget


def test_set_eligibility_disable_flips_projection_back(tmp_path: Path) -> None:
    root = tmp_path / "project"
    _seed(root)
    expected_budget = _budget_harness(root, "D")
    set_eligibility(root, "D", can_receive_dispatch=True, can_fire_events=None)
    assert _projection_record(root, "D")["can_receive_dispatch"] is True

    result = set_eligibility(root, "D", can_receive_dispatch=False, can_fire_events=None)

    assert result.status == "applied"
    assert _projection_record(root, "D")["can_receive_dispatch"] is False
    assert _db_dispatch_surface(root, "D")["can_receive_dispatch"] is False
    _assert_rules_policy_only(root, "D")
    assert _budget_harness(root, "D") == expected_budget


def test_set_weights_updates_registry_projection_without_rules_authority(tmp_path: Path) -> None:
    root = tmp_path / "project"
    _seed(root)

    result = set_weights(
        root,
        "D",
        dispatch_quality=88,
        dispatch_cost=24,
        dispatch_availability=91,
        reviewer_precedence=12,
    )

    assert result.status == "applied"
    projection = _projection_record(root, "D")
    assert projection["dispatch_quality"] == 88.0
    assert projection["dispatch_cost"] == 24.0
    assert projection["dispatch_availability"] == 91.0
    assert projection["reviewer_precedence"] == 12
    dispatch = _db_dispatch_surface(root, "D")
    assert dispatch["dispatch_quality"] == 88
    assert dispatch["dispatch_cost"] == 24
    assert dispatch["dispatch_availability"] == 91
    _assert_rules_policy_only(root, "D")


def test_set_weights_can_update_reviewer_precedence_without_rewriting_dispatch_surface(tmp_path: Path) -> None:
    root = tmp_path / "project"
    _seed(root)
    before_dispatch = _db_dispatch_surface(root, "D")

    result = set_weights(
        root,
        "D",
        dispatch_quality=None,
        dispatch_cost=None,
        dispatch_availability=None,
        reviewer_precedence=20,
    )

    assert result.status == "applied"
    assert _projection_record(root, "D")["reviewer_precedence"] == 20
    assert _db_dispatch_surface(root, "D") == before_dispatch
    _assert_rules_policy_only(root, "D")


def test_dry_run_does_not_regenerate_projection(tmp_path: Path) -> None:
    root = tmp_path / "project"
    _seed(root)
    expected_budget = _budget_harness(root, "D")
    assert _projection_record(root, "D")["can_receive_dispatch"] is False

    result = set_eligibility(root, "D", can_receive_dispatch=True, can_fire_events=None, dry_run=True)

    assert result.status == "dry_run"
    assert result.mutated is False
    assert result.config is None
    assert "projection regenerated" not in result.message
    assert _projection_record(root, "D")["can_receive_dispatch"] is False
    assert _budget_harness(root, "D") == expected_budget


def test_add_harness_rejects_registry_authority_fields(tmp_path: Path) -> None:
    root = tmp_path / "project"
    _seed(root)

    with pytest.raises(DispatchConfigTransactionError, match="harness registry/MemBase"):
        add_harness(root, "G", can_receive_dispatch=True)


def test_set_rule_accepts_no_action_status_for_lo_routing(tmp_path: Path) -> None:
    root = tmp_path / "project"
    _seed(root)

    result = set_rule(
        root,
        "bridge-loyal-opposition-default",
        statuses=("NEW", "REVISED", "NO-ACTION"),
        dry_run=True,
    )

    assert result.status == "dry_run"
    assert result.config is not None
    rule = next(row for row in result.config["rules"] if row["id"] == "bridge-loyal-opposition-default")
    assert rule["statuses"] == ["NEW", "REVISED", "NO-ACTION"]
    assert _rule_statuses(root, "bridge-loyal-opposition-default") == ["NEW", "REVISED"]
