from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "groundtruth-kb" / "src"))

from groundtruth_kb.bridge_dispatch_config import (  # noqa: E402
    collect_bridge_dispatch_status,
    load_bridge_dispatch_config,
    select_dispatch_candidates,
)
from groundtruth_kb.bridge_dispatch_rules import DispatchContext, context_from_bridge_text  # noqa: E402


@pytest.fixture(autouse=True)
def _no_registry_env_override(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("GTKB_HARNESS_REGISTRY_PATH", raising=False)


def _write_project(root: Path, *, rules: str = "", harnesses: list[dict] | None = None) -> None:
    (root / "config" / "dispatcher").mkdir(parents=True)
    (root / "config" / "dispatcher" / "rules.toml").write_text(
        rules
        or """
schema_version = 1
selection_order = ["reviewer_precedence", "harness_id"]
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
                "harnesses": harnesses or _default_harnesses(),
            }
        ),
        encoding="utf-8",
    )


def _default_harnesses() -> list[dict]:
    return [
        {
            "id": "A",
            "harness_name": "codex",
            "harness_type": "codex",
            "status": "active",
            "role": ["prime-builder"],
            "can_fire_events": True,
            "can_receive_dispatch": True,
            "event_driven_hooks": True,
            "reviewer_precedence": 20,
        },
        {
            "id": "B",
            "harness_name": "claude",
            "harness_type": "claude",
            "status": "active",
            "role": ["prime-builder"],
            "can_fire_events": True,
            "can_receive_dispatch": False,
            "event_driven_hooks": False,
            "reviewer_precedence": 10,
        },
        {
            "id": "D",
            "harness_name": "ollama",
            "harness_type": "ollama",
            "status": "active",
            "role": ["loyal-opposition"],
            "can_fire_events": False,
            "can_receive_dispatch": True,
            "event_driven_hooks": False,
            "reviewer_precedence": 10,
        },
        {
            "id": "F",
            "harness_name": "openrouter",
            "harness_type": "openrouter",
            "status": "active",
            "role": ["loyal-opposition"],
            "can_fire_events": False,
            "can_receive_dispatch": True,
            "event_driven_hooks": False,
            "reviewer_precedence": 20,
        },
    ]


def test_collect_status_keeps_role_and_dispatchability_orthogonal(tmp_path: Path) -> None:
    _write_project(tmp_path)

    status = collect_bridge_dispatch_status(tmp_path)

    assert status.health_status == "PASS"
    assert [row["id"] for row in status.selected_by_role["prime-builder"]] == ["A"]
    assert [row["id"] for row in status.selected_by_role["loyal-opposition"]] == ["D", "F"]
    claude = next(row for row in status.harnesses if row["id"] == "B")
    assert claude["role"] == ["prime-builder"]
    assert claude["can_receive_dispatch"] is False
    assert claude["can_fire_events"] is True


def test_config_overlay_can_disable_dispatchability(tmp_path: Path) -> None:
    _write_project(
        tmp_path,
        rules="""
schema_version = 1
selection_order = ["reviewer_precedence", "harness_id"]

[harnesses.A]
can_receive_dispatch = false

rules = []
""".lstrip(),
    )

    status = collect_bridge_dispatch_status(tmp_path)

    assert status.health_status == "FAIL"
    assert status.selected_by_role["prime-builder"] == []
    assert any("prime-builder" in finding for finding in status.health_findings)


def test_context_from_bridge_text_extracts_rule_context() -> None:
    context = context_from_bridge_text(
        "loyal-opposition",
        "session_subject: Dispatch topology\n\n::open verify\n",
        status="NEW",
    )

    assert context == DispatchContext(
        required_role="loyal-opposition",
        status="NEW",
        session_subject="Dispatch topology",
        activity="verify",
    )


def test_rules_match_status_and_activity_without_role_only_fallback(tmp_path: Path) -> None:
    _write_project(
        tmp_path,
        rules="""
schema_version = 1

[[rules]]
id = "lo-verify-only"
required_roles = ["loyal-opposition"]
statuses = ["NEW"]
activities = ["verify"]
prefer = ["harness_id"]
""".lstrip(),
    )
    config = load_bridge_dispatch_config(tmp_path)
    records = _default_harnesses()

    matching = select_dispatch_candidates(
        records,
        config,
        DispatchContext(required_role="loyal-opposition", status="NEW", activity="verify"),
    )
    non_matching = select_dispatch_candidates(
        records,
        config,
        DispatchContext(required_role="loyal-opposition", status="GO", activity="verify"),
    )

    assert [row["id"] for row in matching] == ["D", "F"]
    assert non_matching == []
