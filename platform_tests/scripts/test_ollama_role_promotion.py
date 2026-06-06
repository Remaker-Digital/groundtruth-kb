from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[2]
_PACKAGE_SRC = _REPO_ROOT / "groundtruth-kb" / "src"
if str(_PACKAGE_SRC) not in sys.path:
    sys.path.insert(0, str(_PACKAGE_SRC))

from groundtruth_kb.db import KnowledgeDB  # noqa: E402
from groundtruth_kb.harness_projection import generate_harness_projection  # noqa: E402

from scripts import harness_roles as roles  # noqa: E402

_VERIFIED_CHILDREN = {
    "gtkb-ollama-integration-phase-2-routing": "VERIFIED",
    "gtkb-ollama-integration-phase-2-adapters": "VERIFIED",
    "gtkb-ollama-integration-phase-2-dispatch": "VERIFIED",
}


def _write_index(root: Path, statuses: dict[str, str]) -> None:
    lines = ["# Bridge Index\n"]
    for bridge_id, status in statuses.items():
        lines.extend(
            [
                f"\nDocument: {bridge_id}\n",
                f"{status}: bridge/{bridge_id}-010.md\n",
            ]
        )
    (root / "bridge").mkdir(parents=True, exist_ok=True)
    (root / "bridge" / "INDEX.md").write_text("".join(lines), encoding="utf-8")


def _seed_registry(root: Path) -> KnowledgeDB:
    db = KnowledgeDB(db_path=root / "groundtruth.db")
    fixtures: list[tuple[str, str, list[str], str]] = [
        ("A", "codex", ["loyal-opposition"], "active"),
        ("B", "claude", [], "active"),
        ("C", "antigravity", ["prime-builder"], "active"),
        ("D", "ollama", [], "registered"),
    ]
    for harness_id, name, role, status in fixtures:
        db.insert_harness(
            id=harness_id,
            harness_name=name,
            harness_type=name,
            role=role,
            changed_by="test",
            change_reason="ollama role promotion fixture",
            status=status,
            invocation_surfaces={
                "headless": {
                    "argv": [
                        "groundtruth-kb/.venv/Scripts/python.exe",
                        "scripts/ollama_harness.py",
                        "-p",
                        "{{PROMPT}}",
                        "--skill",
                        "bridge-review",
                    ]
                }
            }
            if harness_id == "D"
            else None,
        )
    generate_harness_projection(db, root)
    return db


def _seed_phase2_project(root: Path, db: KnowledgeDB) -> None:
    db.insert_deliberation(
        id="DELIB-TEST-OLLAMA-PHASE2",
        source_type="owner_conversation",
        title="Fixture Ollama Phase 2+ authorization",
        summary="Fixture owner decision for Ollama Phase 2+ closure tests.",
        content="Fixture owner decision for Ollama Phase 2+ closure tests.",
        changed_by="test",
        change_reason="ollama phase2 closure fixture",
        outcome="owner_decision",
    )
    db.insert_project(
        "Ollama integration",
        "test",
        "ollama phase2 closure fixture",
        id=roles.OLLAMA_PHASE2_PROJECT_ID,
        status="active",
    )
    db.insert_spec(
        "ADR-OLLAMA-HARNESS-ADOPTION-001",
        "Fixture Ollama harness adoption",
        "specified",
        "test",
        "ollama phase2 closure fixture",
        description="Fixture spec that satisfies active project-authorization linkage.",
        type="architecture_decision",
    )
    for index, item_id in enumerate(roles.OLLAMA_PHASE2_CLOSURE_WORK_ITEMS, start=1):
        db.insert_work_item(
            id=item_id,
            title=f"Ollama Phase 2+ fixture {item_id}",
            origin="new",
            component="harness/ollama",
            resolution_status="open",
            changed_by="test",
            change_reason="ollama phase2 closure fixture",
            description=f"Fixture work item {item_id}",
            priority="P1",
            stage="backlogged",
            approval_state="approved",
            project_name=roles.OLLAMA_PHASE2_PROJECT_ID,
            subproject_name="Phase 2+",
            implementation_order=index,
            related_bridge_threads="gtkb-ollama-integration-phase-2-role-promotion",
        )
        db.link_project_work_item(
            roles.OLLAMA_PHASE2_PROJECT_ID,
            item_id,
            "test",
            "ollama phase2 closure fixture",
            membership_order=index,
        )
    db.insert_project_authorization(
        roles.OLLAMA_PHASE2_PROJECT_ID,
        "Ollama integration Phase 2+ completion",
        "DELIB-TEST-OLLAMA-PHASE2",
        "Fixture authorization for Ollama Phase 2+ closure tests.",
        "test",
        "ollama phase2 closure fixture",
        id=roles.OLLAMA_PHASE2_AUTHORIZATION_ID,
        status="active",
        included_work_item_ids=list(roles.OLLAMA_PHASE2_CLOSURE_WORK_ITEMS),
        included_spec_ids=["ADR-OLLAMA-HARNESS-ADOPTION-001"],
    )
    memory_dir = root / "memory"
    memory_dir.mkdir(parents=True)
    (memory_dir / "MEMORY.md").write_text(
        "# Agent Red Memory\n\n## Current Status\n\n- Existing fixture status.\n",
        encoding="utf-8",
    )


def _read_projection(root: Path) -> dict[str, dict[str, Any]]:
    data = json.loads((root / "harness-state" / "harness-registry.json").read_text(encoding="utf-8"))
    return {str(record["id"]): record for record in data["harnesses"]}


def _ready() -> dict[str, Any]:
    return {"ready": True, "checks": [{"name": "fixture readiness", "passed": True}]}


def _not_ready() -> dict[str, Any]:
    return {"ready": False, "checks": [{"name": "ollama /api/tags", "passed": False}]}


def test_ollama_promotion_refuses_when_child_bridge_not_verified(tmp_path: Path) -> None:
    _seed_registry(tmp_path)
    statuses = dict(_VERIFIED_CHILDREN)
    statuses["gtkb-ollama-integration-phase-2-dispatch"] = "GO"
    _write_index(tmp_path, statuses)

    result = roles.apply_ollama_role_promotion(tmp_path, readiness_result=_ready())

    assert result["applied"] is False
    assert result["would_apply"] is False
    assert "missing_verified_child_bridge" in result["evaluation"]["blocking_reasons"]
    assert result["evaluation"]["prerequisites"]["missing_verified"] == ["gtkb-ollama-integration-phase-2-dispatch"]


def test_ollama_promotion_refuses_when_dispatch_readiness_fails(tmp_path: Path) -> None:
    _seed_registry(tmp_path)
    _write_index(tmp_path, _VERIFIED_CHILDREN)

    result = roles.apply_ollama_role_promotion(tmp_path, readiness_result=_not_ready())

    assert result["applied"] is False
    assert result["would_apply"] is False
    assert "ollama_dispatch_not_ready" in result["evaluation"]["blocking_reasons"]


def test_ollama_promotion_dry_run_succeeds_when_all_gates_pass(tmp_path: Path) -> None:
    _seed_registry(tmp_path)
    _write_index(tmp_path, _VERIFIED_CHILDREN)

    result = roles.apply_ollama_role_promotion(tmp_path, readiness_result=_ready())
    projection = _read_projection(tmp_path)

    assert result["applied"] is False
    assert result["would_apply"] is True
    assert result["reason"] == "dry run"
    assert projection["D"]["status"] == "registered"
    assert projection["D"]["role"] == []


def test_ollama_promotion_validation_failure_does_not_activate_ollama(tmp_path: Path) -> None:
    from groundtruth_kb.mode_switch.transaction import TransactionValidationError

    _seed_registry(tmp_path)
    _write_index(tmp_path, _VERIFIED_CHILDREN)
    session_dir = tmp_path / ".claude" / "session"
    session_dir.mkdir(parents=True)
    (session_dir / "work-subject.json").write_text("{not valid json", encoding="utf-8")

    with pytest.raises(TransactionValidationError):
        roles.apply_ollama_role_promotion(
            tmp_path,
            dry_run=False,
            readiness_result=_ready(),
        )

    projection = _read_projection(tmp_path)
    assert projection["D"]["status"] == "registered"
    assert projection["D"]["role"] == []


def test_ollama_promotion_restores_ollama_if_role_switch_fails_after_activation(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import groundtruth_kb.mode_switch.transaction as transaction_module
    from groundtruth_kb.mode_switch.transaction import TransactionValidationError

    _seed_registry(tmp_path)
    _write_index(tmp_path, _VERIFIED_CHILDREN)

    def fail_role_switch(*args: Any, **kwargs: Any) -> None:
        _ = args, kwargs
        raise TransactionValidationError(
            "fixture role-switch validation failed",
            axis="session-state",
            errors=("fixture role-switch validation failed",),
        )

    monkeypatch.setattr(transaction_module, "apply_role_switch", fail_role_switch)

    with pytest.raises(TransactionValidationError):
        roles.apply_ollama_role_promotion(
            tmp_path,
            dry_run=False,
            readiness_result=_ready(),
        )

    projection = _read_projection(tmp_path)
    assert projection["D"]["status"] == "registered"
    assert projection["D"]["role"] == []


def test_ollama_promotion_apply_uses_canonical_role_partition(tmp_path: Path) -> None:
    _seed_registry(tmp_path)
    _write_index(tmp_path, _VERIFIED_CHILDREN)

    result = roles.apply_ollama_role_promotion(
        tmp_path,
        role=roles.ROLE_LOYAL_OPPOSITION,
        dry_run=False,
        readiness_result=_ready(),
    )
    projection = _read_projection(tmp_path)

    assert result["applied"] is True
    assert result["transaction"]["harness_id"] == "D"
    assert result["partition"]["prime_builder_id"] == "C"
    assert result["partition"]["loyal_opposition_id"] == "D"
    assert projection["C"]["status"] == "active"
    assert projection["C"]["role"] == ["prime-builder"]
    assert projection["D"]["status"] == "active"
    assert projection["D"]["role"] == ["loyal-opposition"]
    assert projection["A"]["status"] == "suspended"
    assert projection["B"]["status"] == "suspended"
    assert any("gt harness suspend --harness D" in command for command in result["rollback_commands"])


def test_ollama_phase2_closure_refuses_when_ollama_role_not_promoted(tmp_path: Path) -> None:
    db = _seed_registry(tmp_path)
    _seed_phase2_project(tmp_path, db)
    _write_index(tmp_path, _VERIFIED_CHILDREN)

    result = roles.apply_ollama_phase2_closure(tmp_path, dry_run=False)

    assert result["applied"] is False
    assert result["would_apply"] is False
    assert "ollama_role_not_promoted" in result["evaluation"]["blocking_reasons"]
    assert db.get_project_authorization(roles.OLLAMA_PHASE2_AUTHORIZATION_ID)["status"] == "active"
    assert db.get_project(roles.OLLAMA_PHASE2_PROJECT_ID)["status"] == "active"
    assert db.get_work_item("WI-4382")["resolution_status"] == "open"
    assert roles.OLLAMA_PHASE2_MEMORY_MARKER not in (tmp_path / "memory" / "MEMORY.md").read_text(encoding="utf-8")


def test_ollama_phase2_closure_dry_run_is_mutation_free_after_promotion(tmp_path: Path) -> None:
    db = _seed_registry(tmp_path)
    _seed_phase2_project(tmp_path, db)
    _write_index(tmp_path, _VERIFIED_CHILDREN)
    roles.apply_ollama_role_promotion(
        tmp_path,
        role=roles.ROLE_LOYAL_OPPOSITION,
        dry_run=False,
        readiness_result=_ready(),
    )

    result = roles.apply_ollama_phase2_closure(tmp_path)

    assert result["applied"] is False
    assert result["would_apply"] is True
    assert result["reason"] == "dry run"
    assert db.get_project_authorization(roles.OLLAMA_PHASE2_AUTHORIZATION_ID)["status"] == "active"
    assert db.get_project(roles.OLLAMA_PHASE2_PROJECT_ID)["status"] == "active"
    assert db.get_work_item("WI-4382")["resolution_status"] == "open"
    assert roles.OLLAMA_PHASE2_MEMORY_MARKER not in (tmp_path / "memory" / "MEMORY.md").read_text(encoding="utf-8")


def test_ollama_phase2_closure_resolves_project_work_items_and_memory_after_promotion(tmp_path: Path) -> None:
    db = _seed_registry(tmp_path)
    _seed_phase2_project(tmp_path, db)
    _write_index(tmp_path, _VERIFIED_CHILDREN)
    roles.apply_ollama_role_promotion(
        tmp_path,
        role=roles.ROLE_LOYAL_OPPOSITION,
        dry_run=False,
        readiness_result=_ready(),
    )

    result = roles.apply_ollama_phase2_closure(tmp_path, dry_run=False)

    assert result["applied"] is True
    assert result["authorization_completed"] is True
    assert result["project_completed"] is True
    assert result["memory_updated"] is True
    assert result["resolved_work_items"] == list(roles.OLLAMA_PHASE2_CLOSURE_WORK_ITEMS)
    for item_id in roles.OLLAMA_PHASE2_CLOSURE_WORK_ITEMS:
        row = db.get_work_item(item_id)
        assert row["resolution_status"] == "resolved"
        assert row["stage"] == "resolved"
        assert row["completion_evidence"] == roles.OLLAMA_PHASE2_COMPLETION_EVIDENCE
    assert db.get_project_authorization(roles.OLLAMA_PHASE2_AUTHORIZATION_ID)["status"] == "completed"
    assert db.get_project(roles.OLLAMA_PHASE2_PROJECT_ID)["status"] == "completed"
    memory_text = (tmp_path / "memory" / "MEMORY.md").read_text(encoding="utf-8")
    assert roles.OLLAMA_PHASE2_MEMORY_MARKER in memory_text
    assert "WI-4379, WI-4380, WI-4381, and WI-4382 resolved" in memory_text
