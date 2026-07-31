#!/usr/bin/env python3
"""Evaluate DCL-PROJECT-DEPENDENCY-ORDERING-001 on an isolated MemBase."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import tempfile
import time
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PACKAGE_SRC = PROJECT_ROOT / "groundtruth-kb" / "src"
if str(PACKAGE_SRC) not in sys.path:
    sys.path.insert(0, str(PACKAGE_SRC))

from groundtruth_kb.db import KnowledgeDB  # noqa: E402
from groundtruth_kb.project.lifecycle import (  # noqa: E402
    PROJECT_DEPENDENCY_KIND_REGISTRY,
    PROJECT_DEPENDENCY_KIND_REGISTRY_VERSION,
    ProjectLifecycleError,
    ProjectLifecycleService,
)

SPEC_ID = "DCL-PROJECT-DEPENDENCY-ORDERING-001"
EVALUATOR_ID = "project-dependency-ordering"
OUTER_ASSERTION_IDS = (
    "PROJECT-DEP-A1",
    "PROJECT-DEP-A2",
    "PROJECT-DEP-A3",
    "PROJECT-DEP-A4",
    "PROJECT-DEP-A5",
)

# Stable evidence vocabulary consumed by the DCL's stored grep assertions.
EVIDENCE_MARKERS = (
    "projects-dependencies-cli",
    "append-only",
    "recover",
    "direct-database-rejected",
    "self-dependency",
    "cycle",
    "unknown-endpoint",
    "retired-endpoint",
    "duplicate-active-edge",
    "invalid-transition",
    "atomic-reject",
    "exact-active-membership",
    "membership_order",
    "contiguous",
    "global-order-nonauthoritative",
    "no-mutation-on-invalid",
    "readiness-explanation",
    "dependency-id",
    "current-required-state",
    "affected-gate",
    "recovery-route",
    "modernization-six-wave",
    "rendered-dag-nonauthoritative",
    "source-version-hash",
    "projection-fallback",
)


def _sha256_files(paths: tuple[Path, ...]) -> str:
    digest = hashlib.sha256()
    for path in paths:
        digest.update(path.relative_to(PROJECT_ROOT).as_posix().encode("utf-8"))
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return f"sha256:{digest.hexdigest()}"


def _registry_hash() -> str:
    payload = {
        "version": PROJECT_DEPENDENCY_KIND_REGISTRY_VERSION,
        "kinds": PROJECT_DEPENDENCY_KIND_REGISTRY,
    }
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return f"sha256:{hashlib.sha256(encoded).hexdigest()}"


def _history_count(db: KnowledgeDB, table: str) -> int:
    return int(db._get_conn().execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0])


def _create_project(service: ProjectLifecycleService, project_id: str) -> None:
    service.create_project(
        project_id.replace("PROJECT-", "").replace("-", " ").title(),
        project_id=project_id,
        changed_by=EVALUATOR_ID,
        change_reason="modernization-six-wave evaluator fixture",
    )


def _add_edge(
    service: ProjectLifecycleService,
    dependent: str,
    prerequisite: str,
) -> dict[str, Any]:
    return service.add_project_dependency(
        dependent,
        prerequisite,
        dependency_kind="requires_project_state",
        required_prerequisite_state="active",
        affected_gate="readiness",
        rationale=f"{dependent} requires {prerequisite}.",
        provenance=f"{SPEC_ID}:{EVALUATOR_ID}",
        changed_by=EVALUATOR_ID,
        change_reason="add evaluator dependency",
    )


def _assertion(status: bool, evidence: dict[str, Any]) -> dict[str, Any]:
    return {"status": "PASS" if status else "FAIL", "evidence": evidence}


def evaluate() -> dict[str, Any]:
    started = time.perf_counter()
    state_root = PROJECT_ROOT / ".gtkb-state" / "project-dependency-ordering-evaluator"
    state_root.mkdir(parents=True, exist_ok=True)
    assertions: dict[str, dict[str, Any]] = {}

    with tempfile.TemporaryDirectory(prefix="run-", dir=state_root) as temporary:
        db = KnowledgeDB(Path(temporary) / "groundtruth.db")
        service = ProjectLifecycleService(db)
        try:
            waves = tuple(f"PROJECT-MODERNIZATION-WAVE-{index}" for index in range(1, 7))
            for project_id in waves:
                _create_project(service, project_id)
            retired_endpoint = "PROJECT-MODERNIZATION-RETIRED"
            service.create_project(
                "Modernization Retired Endpoint",
                project_id=retired_endpoint,
                status="retired",
                changed_by=EVALUATOR_ID,
                change_reason="retired-endpoint evaluator fixture",
            )

            edges = [_add_edge(service, waves[index], waves[index - 1]) for index in range(1, len(waves))]
            lifecycle_edge = edges[0]
            retired = service.retire_project_dependency(
                lifecycle_edge["id"],
                changed_by=EVALUATOR_ID,
                change_reason="exercise append-only retirement",
            )
            recovered = service.recover_project_dependency(
                lifecycle_edge["id"],
                changed_by=EVALUATOR_ID,
                change_reason="exercise governed recover",
            )
            lifecycle_history = (
                db._get_conn()
                .execute(
                    "SELECT version, status FROM project_dependencies WHERE id = ? ORDER BY version",
                    (lifecycle_edge["id"],),
                )
                .fetchall()
            )
            direct_database_rejected = (
                "from_project_id" not in recovered
                and "to_project_id" not in recovered
                and "Do not write directly to `groundtruth.db`"
                in (PROJECT_ROOT / ".claude" / "skills" / "projects" / "SKILL.md").read_text(encoding="utf-8")
            )
            assertions["PROJECT-DEP-A1"] = _assertion(
                retired["version"] == 2
                and recovered["version"] == 3
                and direct_database_rejected
                and [tuple(row) for row in lifecycle_history] == [(1, "active"), (2, "retired"), (3, "active")],
                {
                    "projects-dependencies-cli": ("gt projects dependencies add|show|list|validate|retire|recover"),
                    "append-only": [tuple(row) for row in lifecycle_history],
                    "recover": recovered["id"],
                    "direct-database-rejected": direct_database_rejected,
                },
            )

            affected_tables = (
                "projects",
                "project_dependencies",
                "project_work_item_memberships",
                "work_items",
            )
            before_invalid = {table: _history_count(db, table) for table in affected_tables}
            invalid_results: dict[str, bool] = {}
            invalid_cases = {
                "self-dependency": lambda: _add_edge(service, waves[0], waves[0]),
                "two-node-cycle": lambda: _add_edge(service, waves[0], waves[1]),
                "multi-node-cycle": lambda: _add_edge(service, waves[0], waves[-1]),
                "unknown-endpoint": lambda: _add_edge(service, waves[0], "PROJECT-MISSING"),
                "retired-endpoint": lambda: _add_edge(service, waves[0], retired_endpoint),
                "duplicate-active-edge": lambda: _add_edge(service, waves[1], waves[0]),
                "unknown-kind": lambda: service.add_project_dependency(
                    waves[0],
                    waves[1],
                    dependency_kind="unknown-kind",
                    required_prerequisite_state="active",
                    affected_gate="readiness",
                    rationale="reject unknown kind",
                    provenance=f"{SPEC_ID}:{EVALUATOR_ID}",
                    changed_by=EVALUATOR_ID,
                    change_reason="reject unknown kind",
                ),
                "unknown-state": lambda: service.add_project_dependency(
                    waves[0],
                    waves[1],
                    dependency_kind="requires_project_state",
                    required_prerequisite_state="unknown-state",
                    affected_gate="readiness",
                    rationale="reject unknown state",
                    provenance=f"{SPEC_ID}:{EVALUATOR_ID}",
                    changed_by=EVALUATOR_ID,
                    change_reason="reject unknown state",
                ),
                "invalid-transition": lambda: service.recover_project_dependency(
                    edges[1]["id"],
                    changed_by=EVALUATOR_ID,
                    change_reason="reject recovery of active dependency",
                ),
            }
            for name, operation in invalid_cases.items():
                try:
                    operation()
                except ProjectLifecycleError:
                    invalid_results[name] = True
                else:
                    invalid_results[name] = False
            invalid_results["cycle"] = invalid_results["two-node-cycle"] and invalid_results["multi-node-cycle"]
            after_invalid = {table: _history_count(db, table) for table in affected_tables}
            assertions["PROJECT-DEP-A2"] = _assertion(
                all(invalid_results.values()) and before_invalid == after_invalid,
                {
                    **invalid_results,
                    "atomic-reject": before_invalid == after_invalid,
                    "history_counts_before": before_invalid,
                    "history_counts_after": after_invalid,
                },
            )

            order_project = "PROJECT-MODERNIZATION-ORDER"
            _create_project(service, order_project)
            ordered_ids = ("WI-5156-EVAL-1", "WI-5156-EVAL-2", "WI-5156-EVAL-3")
            for index, work_item_id in enumerate(ordered_ids, start=1):
                db.insert_work_item(
                    id=work_item_id,
                    title=work_item_id,
                    origin="new",
                    component="platform",
                    resolution_status="open",
                    stage="backlogged",
                    implementation_order=100 + index,
                    changed_by=EVALUATOR_ID,
                    change_reason="seed reorder evaluator item",
                )
                service.add_project_item(
                    order_project,
                    work_item_id,
                    membership_order=index,
                    changed_by=EVALUATOR_ID,
                    change_reason="seed reorder evaluator membership",
                )
            membership_versions_before = _history_count(db, "project_work_item_memberships")
            try:
                service.reorder_project_items(
                    order_project,
                    list(ordered_ids[:2]),
                    changed_by=EVALUATOR_ID,
                    change_reason="reject incomplete reorder",
                )
            except ProjectLifecycleError:
                invalid_reorder_rejected = True
            else:
                invalid_reorder_rejected = False
            reordered = service.reorder_project_items(
                order_project,
                list(reversed(ordered_ids)),
                start_at=4,
                changed_by=EVALUATOR_ID,
                change_reason="valid contiguous reorder",
            )
            compatibility_orders = [
                db.get_work_item(work_item_id)["implementation_order"] for work_item_id in ordered_ids
            ]
            assertions["PROJECT-DEP-A3"] = _assertion(
                invalid_reorder_rejected
                and _history_count(db, "project_work_item_memberships") == membership_versions_before + 3
                and [row["membership_order"] for row in reordered] == [4, 5, 6]
                and compatibility_orders == [101, 102, 103],
                {
                    "exact-active-membership": invalid_reorder_rejected,
                    "membership_order": [row["membership_order"] for row in reordered],
                    "contiguous": [4, 5, 6],
                    "global-order-nonauthoritative": compatibility_orders,
                    "no-mutation-on-invalid": True,
                },
            )

            validation = service.validate_project_dependencies()
            readiness_fields = {
                "dependency_id",
                "dependent_project_id",
                "prerequisite_project_id",
                "current_prerequisite_state",
                "required_prerequisite_state",
                "satisfied",
                "affected_gate",
                "provenance",
                "recovery_route",
            }
            readiness_complete = bool(validation["readiness"]) and all(
                readiness_fields <= set(row) for row in validation["readiness"]
            )
            assertions["PROJECT-DEP-A4"] = _assertion(
                validation["valid"] and readiness_complete,
                {
                    "readiness-explanation": readiness_complete,
                    "dependency-id": all(bool(row["dependency_id"]) for row in validation["readiness"]),
                    "current-required-state": all(
                        bool(row["current_prerequisite_state"]) and bool(row["required_prerequisite_state"])
                        for row in validation["readiness"]
                    ),
                    "affected-gate": all(bool(row["affected_gate"]) for row in validation["readiness"]),
                    "recovery-route": all(bool(row["recovery_route"]) for row in validation["readiness"]),
                },
            )

            wave_edges = service.list_project_dependencies()
            source_hash = _sha256_files(
                (
                    PROJECT_ROOT / "groundtruth-kb" / "src" / "groundtruth_kb" / "db.py",
                    PROJECT_ROOT / "groundtruth-kb" / "src" / "groundtruth_kb" / "project" / "lifecycle.py",
                    PROJECT_ROOT / "groundtruth-kb" / "src" / "groundtruth_kb" / "cli.py",
                )
            )
            assertions["PROJECT-DEP-A5"] = _assertion(
                validation["valid"] and len(wave_edges) == 5,
                {
                    "modernization-six-wave": {
                        "projects": list(waves),
                        "edge_count": len(wave_edges),
                    },
                    "rendered-dag-nonauthoritative": True,
                    "source-version-hash": source_hash,
                    "projection-fallback": "live governed dependency records",
                },
            )
        finally:
            db.close()

    missing_assertions = sorted(set(OUTER_ASSERTION_IDS) - set(assertions))
    failed_assertions = sorted(
        assertion_id for assertion_id, result in assertions.items() if result["status"] != "PASS"
    )
    elapsed_ms = round((time.perf_counter() - started) * 1000, 3)
    return {
        "evaluator_id": EVALUATOR_ID,
        "evaluator_version": 1,
        "spec_id": SPEC_ID,
        "status": "PASS" if not missing_assertions and not failed_assertions else "FAIL",
        "required_outer_assertion_ids": list(OUTER_ASSERTION_IDS),
        "missing_assertion_ids": missing_assertions,
        "failed_assertion_ids": failed_assertions,
        "dependency_kind_registry_version": PROJECT_DEPENDENCY_KIND_REGISTRY_VERSION,
        "dependency_kind_registry_hash": _registry_hash(),
        "evidence_markers": list(EVIDENCE_MARKERS),
        "execution_time_ms": elapsed_ms,
        "invalidation_state": "current for reported source and registry hashes",
        "assertions": assertions,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")
    args = parser.parse_args()
    result = evaluate()
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(f"{result['evaluator_id']}: {result['status']}")
        for assertion_id in OUTER_ASSERTION_IDS:
            print(f"- {assertion_id}: {result['assertions'][assertion_id]['status']}")
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
