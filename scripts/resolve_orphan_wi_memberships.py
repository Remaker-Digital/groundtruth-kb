"""Orphan-WI membership backfill resolution driver (Slice 2; WI-3450).

Authority: bridge/gtkb-orphan-wi-membership-backfill-slice-2-implementation-003.md
(REVISED-1), Codex GO at -004. Owner-decision source: DELIB-2509. Project
authorization: PAUTH-WI-3450-ORPHAN-BACKFILL-DRIVER-001 (active; classes
``source`` + ``test_addition``; scope WI-3450 driver + tests).

The driver consumes the Slice 1 discovery scanner's output
(``scripts/discover_orphan_wi_memberships.py``, VERIFIED at
``bridge/gtkb-orphan-wi-membership-discovery-slice-1-012.md``) and builds a
per-orphan resolution plan. With ``--apply`` it executes assignment-only
mutations against MemBase through the deterministic
``ProjectLifecycleService.add_project_item`` service. Retire and exclude
decisions are deliberately NOT executed by this slice; they are written to a
deferred-actions artifact for a follow-on Slice 2b (WI-3464) to consume.

Two design properties are load-bearing:

1. **Re-runs discovery first.** ``build_inventory`` is called at the start of
   every invocation so the orphan set is fresh. The discovery report's
   per-orphan ``recoverability_class`` and ``candidate_project_id`` are the
   inputs to plan generation; consuming a stale report would silently apply
   to an out-of-date set.

2. **Fail-closed on owner decisions.** The driver does not embed any policy.
   An orphan with no entry in the decisions artifact is **skipped** (never
   mutated). A ``retire`` or ``exclude`` decision is **always** written to
   ``deferred_actions.json`` (never executed as a canonical mutation), since
   the per-WI retire service is out of scope this slice. A successful
   ``assign`` routes through ``add_project_item``.

The class threshold ``HIGH_CONFIDENCE_THRESHOLD = 0.80`` is set exactly at
``recoverable_via_id_match`` (Slice 1 confidence 0.80), so the three
structural-evidence classes (``source_spec`` 0.95, ``bridge_thread`` 0.85,
``id_match`` 0.80) auto-map to ``assign_candidate`` and the title-only guess
(``title_match`` 0.70) requires owner-pick. The threshold lives in the module
namespace, not buried in a helper, so test 9 can assert the boundary at the
exact published value.

Copyright (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC.
All rights reserved. Licensed under AGPL-3.0-or-later.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

# The Slice 1 scanner lives at ``scripts/discover_orphan_wi_memberships.py``.
# Add the repo root to ``sys.path`` so importing siblings under ``scripts``
# works regardless of invocation context (CLI, pytest, ad-hoc python -c).
_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

# Slice 1 reuse by import — single-sources the classification taxonomy and
# the ``build_inventory`` entry point. NEVER reimplement the recoverability
# heuristics here.
from groundtruth_kb.db import KnowledgeDB  # noqa: E402
from groundtruth_kb.project.lifecycle import ProjectLifecycleService  # noqa: E402

from scripts.discover_orphan_wi_memberships import (  # noqa: E402
    _open_db,
    build_inventory,
)

# Plan action vocabulary. Tests assert membership against this exact set.
RESOLUTION_ACTIONS = frozenset(
    {
        "assign_candidate",
        "owner_pick",
        "owner_decision",
        "already_member_noop",
    }
)

# Confidence threshold for the auto-assign branch. Slice 1 confidences:
#   recoverable_via_source_spec   0.95  -> assign_candidate (>= 0.80)
#   recoverable_via_bridge_thread 0.85  -> assign_candidate (>= 0.80)
#   recoverable_via_id_match      0.80  -> assign_candidate (>= 0.80; boundary)
#   recoverable_via_title_match   0.70  -> owner_pick       (< 0.80)
#   unrecoverable                 0.00  -> owner_decision
HIGH_CONFIDENCE_THRESHOLD = 0.80

# Driver-side attribution for membership writes; matches the precedent set by
# the phantom reconciliation driver (``gt projects reconcile-doubled-prefix``)
# so the audit trail is uniform across all reconciliation-class CLIs.
RESOLVE_SOURCE = "gt projects resolve-orphan-wi"
RESOLVE_CHANGED_BY = "gt-projects-resolve-orphan-wi"


def _plan_action_for_orphan(orphan: dict[str, Any], threshold: float) -> str:
    """Return the planned action for one orphan based on class + threshold.

    Pure function: no DB access. The mapping IS the policy this slice
    encodes; tests 2/3/4/9 assert each branch.
    """
    klass = str(orphan.get("recoverability_class") or "")
    confidence = float(orphan.get("confidence_score") or 0.0)
    candidate = orphan.get("candidate_project_id")

    if klass == "unrecoverable" or candidate is None:
        return "owner_decision"
    if confidence >= threshold:
        return "assign_candidate"
    return "owner_pick"


def build_resolution_plan(
    inventory: dict[str, Any],
    *,
    high_confidence_threshold: float = HIGH_CONFIDENCE_THRESHOLD,
) -> dict[str, Any]:
    """Build the per-orphan resolution plan from a discovery inventory.

    Pure function; no DB access; no mutation. Consuming a stale inventory is
    the caller's choice — ``build_and_run`` always re-runs discovery first.

    The output schema is deliberately flat and JSON-serializable so the plan
    can be saved as runtime evidence or piped to an owner-review tool.
    """
    plan_entries: list[dict[str, Any]] = []
    counts: dict[str, int] = {action: 0 for action in RESOLUTION_ACTIONS}

    for orphan in inventory.get("orphans", []):
        action = _plan_action_for_orphan(orphan, high_confidence_threshold)
        counts[action] = counts.get(action, 0) + 1
        plan_entries.append(
            {
                "work_item_id": str(orphan.get("id") or ""),
                "title": str(orphan.get("title") or ""),
                "recoverability_class": str(orphan.get("recoverability_class") or ""),
                "confidence_score": float(orphan.get("confidence_score") or 0.0),
                "candidate_project_id": orphan.get("candidate_project_id"),
                "planned_action": action,
            }
        )

    return {
        "run_id": str(inventory.get("run_id") or ""),
        "generated_at": str(inventory.get("generated_at") or ""),
        "orphan_count": int(inventory.get("orphan_count") or 0),
        "high_confidence_threshold": float(high_confidence_threshold),
        "planned_action_counts": counts,
        "entries": plan_entries,
    }


def _load_decisions(decisions_path: Path) -> dict[str, dict[str, Any]]:
    """Load decisions JSON into a ``{work_item_id: decision}`` mapping."""
    raw = json.loads(decisions_path.read_text(encoding="utf-8"))
    if isinstance(raw, list):
        # Tolerate a list-of-decisions form too; key by work_item_id.
        return {str(d["work_item_id"]): d for d in raw if "work_item_id" in d}
    return {str(k): dict(v) for k, v in raw.items()}


def _existing_active_membership(db: KnowledgeDB, project_id: str, work_item_id: str) -> bool:
    """Return True iff project already has an active membership for the WI."""
    memberships = db.list_project_work_items(project_id, include_inactive=False)
    return any(str(m.get("work_item_id")) == work_item_id for m in memberships)


def _append_deferred_action(
    deferred_actions_path: Path,
    record: dict[str, Any],
) -> None:
    """Append a record to the deferred-actions artifact (list form)."""
    if deferred_actions_path.exists():
        try:
            existing = json.loads(deferred_actions_path.read_text(encoding="utf-8"))
            if not isinstance(existing, list):
                existing = []
        except json.JSONDecodeError:
            existing = []
    else:
        existing = []
    existing.append(record)
    deferred_actions_path.parent.mkdir(parents=True, exist_ok=True)
    deferred_actions_path.write_text(json.dumps(existing, indent=2, sort_keys=True), encoding="utf-8")


def apply_resolution(
    plan: dict[str, Any],
    decisions: dict[str, dict[str, Any]],
    service: ProjectLifecycleService,
    *,
    db: KnowledgeDB,
    deferred_actions_path: Path,
) -> dict[str, Any]:
    """Apply the plan against MemBase per per-orphan owner decisions.

    Fail-closed semantics (per the GO's Implementation Constraints):

    * Orphan with no decision -> ``skipped_no_decision`` (NOT mutated).
    * Decision ``assign`` -> ``service.add_project_item(...)``. Already-active
      membership for the target project -> ``already_member_noop``.
    * Decision ``retire`` / ``exclude`` -> append a record to
      ``deferred_actions_path``; NEVER mutate canonical. Slice 2b
      (WI-3464) owns the per-WI retire service that consumes this artifact.
    * Any other decision action -> ``unrecognized_action`` (NOT mutated).

    The function returns a structured report listing each result by class so
    the post-implementation evidence is machine-checkable.
    """
    results: dict[str, list[Any]] = {
        "assigned": [],
        "already_member_noop": [],
        "deferred_actions_written": [],
        "skipped_no_decision": [],
        "unrecognized_action": [],
    }

    for entry in plan.get("entries", []):
        wi_id = str(entry.get("work_item_id") or "")
        if not wi_id:
            continue

        decision = decisions.get(wi_id)
        if decision is None:
            results["skipped_no_decision"].append(wi_id)
            continue

        action = str(decision.get("action") or "")

        if action == "assign":
            project_id = str(decision.get("project_id") or "")
            if not project_id:
                results["unrecognized_action"].append({"work_item_id": wi_id, "reason": "missing project_id"})
                continue
            if _existing_active_membership(db, project_id, wi_id):
                results["already_member_noop"].append({"work_item_id": wi_id, "project_id": project_id})
                continue
            service.add_project_item(
                project_id,
                wi_id,
                changed_by=RESOLVE_CHANGED_BY,
                change_reason=(
                    f"Assign orphan WI {wi_id} to {project_id} per owner decision (WI-3450 Slice 2; DELIB-2509)"
                ),
                source=RESOLVE_SOURCE,
            )
            results["assigned"].append({"work_item_id": wi_id, "project_id": project_id})

        elif action in ("retire", "exclude"):
            # Deferred-execution record. The follow-on Slice 2b (WI-3464)
            # owns the per-WI retire/exclude canonical execution. This slice
            # NEVER mutates canonical for retire/exclude decisions.
            record = {
                "work_item_id": wi_id,
                "action": action,
                "decision_evidence": decision.get("decision_evidence"),
                "deferred_at": plan.get("generated_at"),
                "follow_on_slice": ("Slice 2b (WI-3464): per-WI retire/exclude service"),
            }
            _append_deferred_action(deferred_actions_path, record)
            results["deferred_actions_written"].append(record)

        else:
            results["unrecognized_action"].append({"work_item_id": wi_id, "action": action})

    return results


def build_and_run(
    db_path: Path,
    *,
    apply: bool,
    decisions_path: Path | None,
    run_id: str | None,
    deferred_actions_path: Path | None,
) -> dict[str, Any]:
    """CLI entry: re-run discovery, build plan, optionally apply.

    Dry-run (default) returns the plan; ``apply`` additionally returns the
    application results. Re-running discovery on every invocation keeps the
    orphan set fresh (per the scoping GO's "re-run discovery first"
    requirement).
    """
    db = _open_db(db_path)
    try:
        inventory = build_inventory(db, run_id=run_id or "resolve-driver-run")
        plan = build_resolution_plan(inventory)

        report: dict[str, Any] = {"apply": apply, "plan": plan}
        if apply:
            if decisions_path is None:
                # CLI guard test 10 asserts this branch.
                raise ValueError("--apply requires --decisions <path> to a decisions JSON file")
            decisions = _load_decisions(decisions_path)
            service = ProjectLifecycleService(db)
            default_deferred = (
                _REPO_ROOT
                / ".gtkb-state"
                / "orphan-wi-discovery"
                / (run_id or "resolve-driver-run")
                / "deferred_actions.json"
            )
            results = apply_resolution(
                plan,
                decisions,
                service,
                db=db,
                deferred_actions_path=deferred_actions_path or default_deferred,
            )
            report["results"] = results
    finally:
        db.close()
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Resolve orphan-WI memberships (Slice 2; assign-only).")
    parser.add_argument(
        "--apply",
        action="store_true",
        help=("Execute the plan (assignment-only; retire/exclude write deferred records). Default is dry-run."),
    )
    parser.add_argument(
        "--decisions",
        default=None,
        type=Path,
        help="Path to a decisions JSON file. Required when --apply is set.",
    )
    parser.add_argument(
        "--db-path",
        default=Path("groundtruth.db"),
        type=Path,
        help="Path to groundtruth.db (default: ./groundtruth.db).",
    )
    parser.add_argument(
        "--run-id",
        default=None,
        help="Run ID for the discovery rerun (default: 'resolve-driver-run').",
    )
    parser.add_argument(
        "--deferred-actions",
        default=None,
        type=Path,
        help=(
            "Path to the deferred-actions artifact "
            "(default: .gtkb-state/orphan-wi-discovery/<run-id>/deferred_actions.json)."
        ),
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit the report as JSON to stdout.",
    )
    args = parser.parse_args(argv)

    report = build_and_run(
        args.db_path,
        apply=args.apply,
        decisions_path=args.decisions,
        run_id=args.run_id,
        deferred_actions_path=args.deferred_actions,
    )

    if args.json:
        sys.stdout.write(json.dumps(report, indent=2, sort_keys=True))
        sys.stdout.write("\n")
    else:
        plan = report["plan"]
        mode = "APPLY" if report["apply"] else "DRY-RUN"
        sys.stdout.write(f"Orphan resolution [{mode}]\n")
        sys.stdout.write(f"  run_id={plan['run_id']} orphan_count={plan['orphan_count']}\n")
        sys.stdout.write(f"  planned action counts: {plan['planned_action_counts']}\n")
        if report["apply"]:
            results = report.get("results", {})
            sys.stdout.write(f"  assigned:                 {len(results.get('assigned', []))}\n")
            sys.stdout.write(f"  already-member no-op:     {len(results.get('already_member_noop', []))}\n")
            sys.stdout.write(f"  deferred-actions written: {len(results.get('deferred_actions_written', []))}\n")
            sys.stdout.write(f"  skipped (no decision):    {len(results.get('skipped_no_decision', []))}\n")
            sys.stdout.write(f"  unrecognized action:      {len(results.get('unrecognized_action', []))}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
