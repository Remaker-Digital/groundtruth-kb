"""Regression tests for the WI-4820 dispatch-eligibility write-through.

``bridge_dispatch_transactions._apply_transaction`` regenerates the static
``harness-state/harness-registry.json`` projection after an applied rules.toml
mutation, so the cross-harness trigger (which resolves dispatchability from the
static projection, NOT from ``config/dispatcher/rules.toml``) honors
``set_eligibility`` immediately. Pre-fix the projection stayed stale while
``gt bridge dispatch status`` merged the overlay live, producing the WI-4820
false-green: status reported the harness enabled and selected while the trigger
returned ``no_active_target_for_role``.

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

_REPO_ROOT = Path(__file__).resolve().parents[2]
_PACKAGE_SRC = _REPO_ROOT / "groundtruth-kb" / "src"
if str(_PACKAGE_SRC) not in sys.path:
    sys.path.insert(0, str(_PACKAGE_SRC))

from groundtruth_kb.bridge_dispatch_transactions import set_eligibility  # noqa: E402
from groundtruth_kb.db import KnowledgeDB  # noqa: E402
from groundtruth_kb.harness_projection import generate_harness_projection, harness_registry_path  # noqa: E402

# rules.toml overlay starts harness D DISABLED so the seeded projection (which
# applies the overlay) reads can_receive_dispatch=false — the baseline the
# trigger would see.
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
can_receive_dispatch = false
can_fire_events = false
dispatch_cost = 30
dispatch_quality = 80
dispatch_availability = 95
max_items = 2
tags = ["loyal-opposition"]

[[rules]]
id = "bridge-loyal-opposition-default"
required_roles = ["loyal-opposition"]
statuses = ["NEW", "REVISED"]
prefer = ["quality", "cost", "availability", "harness_id"]
"""


def _seed(root: Path) -> None:
    """Seed a real groundtruth.db registry + rules.toml + generated projection."""
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
        change_reason="WI-4820 dispatch-eligibility write-through fixture",
        status="active",
    )
    generate_harness_projection(db, root)


def _projection_can_receive(root: Path, harness_id: str) -> bool | None:
    """Return the projection ``can_receive_dispatch`` — the exact field the
    trigger's ``_record_can_receive_dispatch`` gate reads from the static
    ``harness-registry.json``. Resolved via ``harness_registry_path`` so the test
    honors the ``GTKB_HARNESS_REGISTRY_PATH`` override the scripts/ conftest sets."""
    data = json.loads(harness_registry_path(root).read_text(encoding="utf-8"))
    for record in data.get("harnesses", []):
        if record.get("id") == harness_id:
            return record.get("can_receive_dispatch")
    raise AssertionError(f"harness {harness_id!r} not present in projection")


def _rules_can_receive(root: Path, harness_id: str) -> bool | None:
    rules = tomllib.loads((root / "config" / "dispatcher" / "rules.toml").read_text(encoding="utf-8"))
    return rules.get("harnesses", {}).get(harness_id, {}).get("can_receive_dispatch")


def _budget_harness(root: Path, harness_id: str) -> dict[str, object]:
    rules = tomllib.loads((root / "config" / "dispatcher" / "rules.toml").read_text(encoding="utf-8"))
    return rules.get("budget", {}).get("harnesses", {}).get(harness_id, {})


def test_set_eligibility_regenerates_projection(tmp_path: Path) -> None:
    root = tmp_path / "project"
    _seed(root)
    expected_budget = _budget_harness(root, "D")
    # Baseline: the rules.toml overlay disables D, so the static projection the
    # trigger reads is False.
    assert _projection_can_receive(root, "D") is False

    result = set_eligibility(root, "D", can_receive_dispatch=True, can_fire_events=None)

    assert result.status == "applied"
    assert result.mutated is True
    assert "projection regenerated" in result.message
    # The fix: the static projection now reflects the enable, so the trigger's
    # dispatchability gate sees D as a target instead of a false-green.
    assert _projection_can_receive(root, "D") is True
    # rules.toml and the projection now agree — no drift, no false-green.
    assert _rules_can_receive(root, "D") is True
    assert _projection_can_receive(root, "D") == _rules_can_receive(root, "D")
    assert _budget_harness(root, "D") == expected_budget


def test_set_eligibility_disable_flips_projection_back(tmp_path: Path) -> None:
    root = tmp_path / "project"
    _seed(root)
    expected_budget = _budget_harness(root, "D")
    set_eligibility(root, "D", can_receive_dispatch=True, can_fire_events=None)
    assert _projection_can_receive(root, "D") is True

    result = set_eligibility(root, "D", can_receive_dispatch=False, can_fire_events=None)

    assert result.status == "applied"
    assert _projection_can_receive(root, "D") is False
    assert _projection_can_receive(root, "D") == _rules_can_receive(root, "D")
    assert _budget_harness(root, "D") == expected_budget


def test_dry_run_does_not_regenerate_projection(tmp_path: Path) -> None:
    # Cursor GO review note #2: the regen must run only on the applied path,
    # never on dry_run.
    root = tmp_path / "project"
    _seed(root)
    expected_budget = _budget_harness(root, "D")
    assert _projection_can_receive(root, "D") is False

    result = set_eligibility(root, "D", can_receive_dispatch=True, can_fire_events=None, dry_run=True)

    assert result.status == "dry_run"
    assert result.mutated is False
    assert result.config is not None
    assert result.config.get("budget", {}).get("harnesses", {}).get("D") == expected_budget
    assert "projection regenerated" not in result.message
    # The static projection is untouched by a dry run.
    assert _projection_can_receive(root, "D") is False
    assert _budget_harness(root, "D") == expected_budget
