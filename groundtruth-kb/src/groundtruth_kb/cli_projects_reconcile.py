"""Implementation for ``gt projects reconcile-doubled-prefix``.

Authority: bridge/gtkb-phantom-project-prefix-reconciliation-003.md (REVISED-1),
Codex GO at bridge/gtkb-phantom-project-prefix-reconciliation-004.md. Source
work item: WI-3355 (member of PROJECT-GTKB-RELIABILITY-FIXES under
PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING).

The reconciliation is the one-shot cleanup that closes WI-3355: the source
defect (the doubled-prefix backfill in ``_project_id_from_names``) was fixed
in commit ``281fa28f`` via ``bridge/gtkb-project-id-prefix-idempotent-fix-005.md``
VERIFIED, but the historical phantoms it produced still exist in the canonical
store. This module deterministically:

1. Enumerates all phantom ``PROJECT-PROJECT-*`` projects.
2. For each phantom, derives the canonical id by stripping one leading
   ``PROJECT-`` prefix.
3. For each phantom's active memberships:
   a. If the canonical project lacks an equivalent active membership for
      the same work_item_id, inserts one. Per
      ``DELIB-2506`` the disposition for the 7 retired-canonical cases is
      "Re-link to retired canonical" — active-on-retired memberships are
      intentional historical fact, not a defect.
   b. Inserts a new version of the phantom membership with
      ``status='superseded'`` (the membership id is the same; only the
      version + status + change_reason change).
4. Retires the phantom project (inserts new project version with
   ``status='retired'``) unless it's already retired.

Per ``DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE`` this is the deterministic
service form: the algorithm is idempotent on rerun (zero writes the second
time) so a future phantom recurrence — if the source defect ever regressed,
which the regression tests forbid — would be cleanly mopped up by a CLI rerun
rather than requiring per-row AI-mediated work.

Mutation contract:

* ``--dry-run`` (default): NO ``groundtruth.db`` writes. Builds and returns
  the reconciliation plan only.
* ``--apply``: Inserts new MemBase rows per the algorithm. Append-only — the
  prior versions of every superseded row and the prior version of every
  retired project are preserved.

Copyright (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
Licensed under AGPL-3.0-or-later.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from groundtruth_kb.config import GTConfig
from groundtruth_kb.db import KnowledgeDB
from groundtruth_kb.project.lifecycle import ProjectLifecycleService

# The original literal phantom doubled-prefix pattern. Kept as a public
# compatibility constant for the WI-3355 tests and for operator language, but
# detection is now structural so project-specific doubled segments such as
# ``PROJECT-X-PROJECT-X-*`` are also reconciled.
PHANTOM_PREFIX = "PROJECT-PROJECT-"

# Standard MemBase attribution for rows this CLI inserts. Both the
# ``source`` (which appears in the membership row) and the ``changed_by``
# (which appears in the history row) point back to this CLI so a future
# audit can trace every mutation to this reconciliation thread.
RECONCILE_SOURCE = "gt projects reconcile-doubled-prefix"
RECONCILE_CHANGED_BY = "gt-projects-reconcile"


@dataclass(frozen=True)
class ReconcileRequest:
    """Validated request for one ``gt projects reconcile-doubled-prefix`` invocation.

    Frozen so the CLI wrapper and the service share a pure value object.
    The default ``apply=False`` enforces the contract that omitting the flag
    means "preview only, no writes" — operators must explicitly opt in to
    canonical mutation by passing ``--apply``.
    """

    apply: bool = False
    project_id: str | None = None


def _repeated_leading_segment(project_id: str) -> str | None:
    """Return the longest repeated leading ``*-`` segment, if any.

    ``PROJECT-PROJECT-X`` returns ``PROJECT-``. A TAFE sub-project phantom
    such as ``PROJECT-GTKB-...-ENGINE-PROJECT-GTKB-...-ENGINE-PHASE-1``
    returns the full ``PROJECT-GTKB-...-ENGINE-`` segment. The longest match
    matters because it prefers the project parent segment over shorter
    incidental repeated prefixes.
    """
    matches = []
    for index, char in enumerate(project_id):
        if char != "-":
            continue
        segment = project_id[: index + 1]
        if project_id.startswith(segment + segment):
            matches.append(segment)
    if not matches:
        return None
    return max(matches, key=len)


def _canonical_id_from_phantom(phantom_id: str) -> str:
    """Strip one detected repeated leading segment from a phantom id."""
    repeated_segment = _repeated_leading_segment(phantom_id)
    if repeated_segment is None:
        raise ValueError(f"Not a phantom doubled-prefix id: {phantom_id!r}")
    return phantom_id[len(repeated_segment) :]


def _project_scope_matches(canonical_id: str, project_id: str | None) -> bool:
    """Return whether a canonical project id is inside an optional scope."""
    if not project_id:
        return True
    return canonical_id == project_id or canonical_id.startswith(f"{project_id}-")


def _list_doubled_prefix_projects(db: KnowledgeDB, project_id: str | None = None) -> list[dict[str, Any]]:
    """Return all current projects whose id matches the phantom pattern.

    Includes terminal-status projects so an already-retired phantom (e.g.
    from a prior partial reconciliation attempt) is visible in the plan and
    can be detected as a no-op.
    """
    phantoms: list[dict[str, Any]] = []
    for project in db.list_projects(include_terminal=True):
        current_id = str(project["id"])
        try:
            canonical_id = _canonical_id_from_phantom(current_id)
        except ValueError:
            continue
        if _project_scope_matches(canonical_id, project_id):
            phantoms.append(project)
    return phantoms


def _canonical_has_active_membership(db: KnowledgeDB, canonical_id: str, work_item_id: str) -> bool:
    """Return True iff the canonical project has an active membership for the WI."""
    memberships = db.list_project_work_items(canonical_id, include_inactive=False)
    return any(str(m.get("work_item_id")) == work_item_id for m in memberships)


def _plan_one_phantom(db: KnowledgeDB, phantom: dict[str, Any]) -> dict[str, Any]:
    """Build the per-phantom reconciliation plan; no MemBase mutation.

    The plan is a serializable dict suitable for both ``--dry-run`` output
    and ``--apply`` execution. Every action the apply phase will take is
    enumerated here so the plan and the execution stay tightly coupled.
    """
    phantom_id = str(phantom["id"])
    phantom_status = str(phantom.get("status") or "")
    canonical_id = _canonical_id_from_phantom(phantom_id)
    canonical = db.get_project(canonical_id)

    plan: dict[str, Any] = {
        "phantom_id": phantom_id,
        "phantom_status": phantom_status,
        "canonical_id": canonical_id,
        "canonical_present": canonical is not None,
        "canonical_status": str(canonical.get("status")) if canonical else None,
        "phantom_active_memberships": [],
        "canonical_links_to_create": [],
        "phantom_memberships_to_supersede": [],
        "retire_phantom": False,
        "skipped": False,
        "skip_reason": None,
    }

    if canonical is None:
        # Safety branch: a phantom whose canonical counterpart never existed.
        # The live inventory at proposal time had zero such cases, but the
        # code path exists so a future stray phantom doesn't silently fail.
        plan["skipped"] = True
        plan["skip_reason"] = "canonical_missing"
        return plan

    phantom_memberships = db.list_project_work_items(phantom_id, include_inactive=False)

    for member in phantom_memberships:
        membership_id = str(member.get("membership_id") or "")
        wi_id = str(member.get("work_item_id") or "")
        if not membership_id or not wi_id:
            continue

        plan["phantom_active_memberships"].append({"membership_id": membership_id, "work_item_id": wi_id})
        # Always supersede the phantom membership row.
        plan["phantom_memberships_to_supersede"].append({"membership_id": membership_id, "work_item_id": wi_id})
        # Only create a new canonical link if the canonical lacks one for
        # this WI. The 42 redundant cases from the proposal inventory take
        # this no-op branch (canonical already has the membership via the
        # operator-applied add-item workaround).
        if not _canonical_has_active_membership(db, canonical_id, wi_id):
            plan["canonical_links_to_create"].append(wi_id)

    # Only retire phantoms that are currently active. A phantom already in
    # terminal state (e.g. ``retired``) does NOT trigger a new retire-version
    # insertion; the rerun-idempotence contract requires the second-pass
    # apply to make zero writes.
    if phantom_status == "active":
        plan["retire_phantom"] = True

    return plan


def _apply_one_phantom(
    db: KnowledgeDB,
    service: ProjectLifecycleService,
    plan: dict[str, Any],
) -> dict[str, Any]:
    """Execute one phantom's plan against MemBase.

    Returns the actual mutation results so the report can show ``apply``
    vs ``planned`` separately. The mutation order matches the algorithm
    spec: (1) create canonical links, (2) supersede phantom memberships,
    (3) retire phantom project. Per-phantom commits are implicit in each
    underlying ``conn.commit()`` call; partial completion across phantoms
    is acceptable because phantoms are independent of each other.
    """
    results: dict[str, Any] = {
        "canonical_links_created": [],
        "phantom_memberships_superseded": [],
        "phantom_retired": False,
    }

    if plan["skipped"]:
        return results

    phantom_id = plan["phantom_id"]
    canonical_id = plan["canonical_id"]

    # (1) New active memberships on the canonical for WIs that need them.
    # ``link_project_work_item`` with no explicit ``id`` uses the stable
    # PWM-<project>-<wi> derivation, producing the same id for the same
    # (canonical, wi) pair regardless of when called. Re-run safety
    # comes from the canonical_has_active_membership check above.
    for wi_id in plan["canonical_links_to_create"]:
        db.link_project_work_item(
            project_id=canonical_id,
            work_item_id=wi_id,
            changed_by=RECONCILE_CHANGED_BY,
            change_reason=(
                f"Reconcile phantom {phantom_id} -> {canonical_id}: "
                "re-link work item to canonical project per WI-3355 "
                "(DELIB-2505, DELIB-2506)"
            ),
            source=RECONCILE_SOURCE,
            status="active",
        )
        results["canonical_links_created"].append(wi_id)

    # (2) Supersede phantom memberships. Passing the existing membership
    # ``id`` makes the link helper insert a NEW VERSION of that same row
    # rather than a freshly-id'd row. The supersession is the contract.
    for member_info in plan["phantom_memberships_to_supersede"]:
        membership_id = member_info["membership_id"]
        wi_id = member_info["work_item_id"]
        db.link_project_work_item(
            id=membership_id,
            project_id=phantom_id,
            work_item_id=wi_id,
            changed_by=RECONCILE_CHANGED_BY,
            change_reason=(
                f"Supersede phantom membership; canonical "
                f"{canonical_id} now holds equivalent (WI-3355; "
                f"DELIB-2505, DELIB-2506)"
            ),
            source=RECONCILE_SOURCE,
            status="superseded",
        )
        results["phantom_memberships_superseded"].append(membership_id)

    # (3) Retire phantom project.
    if plan["retire_phantom"]:
        service.retire_project(
            phantom_id,
            changed_by=RECONCILE_CHANGED_BY,
            change_reason=(
                f"Retire phantom project; reconciled to canonical {canonical_id} per WI-3355 (DELIB-2505, DELIB-2506)"
            ),
        )
        results["phantom_retired"] = True

    return results


def build_reconcile_plan(config: GTConfig, request: ReconcileRequest) -> dict[str, Any]:
    """Build (and optionally execute) the phantom reconciliation plan.

    Returns a single structured report covering every phantom found. The
    ``apply`` field of the request governs whether the plan is executed or
    merely previewed. Dry-run (default) opens the DB read-only-style — the
    underlying KnowledgeDB connection still uses the same write mode, but
    no SQL INSERTs are issued, so the byte-content of ``groundtruth.db``
    is unchanged (proposal test T2 asserts this via sha256).
    """
    db = KnowledgeDB(config.db_path)
    service = ProjectLifecycleService(db)
    try:
        phantoms = _list_doubled_prefix_projects(db, request.project_id)
        report: dict[str, Any] = {
            "apply": request.apply,
            "project_id": request.project_id,
            "phantoms": [],
        }
        totals = {
            "phantom_count": 0,
            "skipped_count": 0,
            "canonical_links_created": 0,
            "phantom_memberships_superseded": 0,
            "phantom_projects_retired": 0,
        }

        for phantom in phantoms:
            totals["phantom_count"] += 1
            plan = _plan_one_phantom(db, phantom)
            if plan["skipped"]:
                totals["skipped_count"] += 1

            entry: dict[str, Any] = {"plan": plan}
            if request.apply:
                results = _apply_one_phantom(db, service, plan)
                entry["results"] = results
                totals["canonical_links_created"] += len(results["canonical_links_created"])
                totals["phantom_memberships_superseded"] += len(results["phantom_memberships_superseded"])
                if results["phantom_retired"]:
                    totals["phantom_projects_retired"] += 1

            report["phantoms"].append(entry)

        report["totals"] = totals
    finally:
        db.close()

    return report
