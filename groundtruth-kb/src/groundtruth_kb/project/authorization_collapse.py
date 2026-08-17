# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""WI-6618: collapse to one current project authorization per project.

Union of granted scope, supersede rather than delete. C1/C2 fail-closed after
the pass lives in ``insert_project_authorization``; this module is the
append-only writer for the supersession event.
"""

from __future__ import annotations

from collections import defaultdict
from datetime import datetime
from typing import Any

from groundtruth_kb.db import KnowledgeDB
from groundtruth_kb.project.authorization import (
    ACTIVE_PROJECT_AUTHORIZATION_STATUS,
    parse_expires_at,
    work_item_scoped_authorization_identity,
)

COLLAPSE_OWNER_DECISION = "DELIB-20260816201237"
COLLAPSE_STATUS_SUPERSEDED = "superseded"
APPROVED_SPEC_STATUSES = frozenset({"specified", "implemented", "verified", "active"})
CHANGE_REASON = (
    "WI-6618 one current authorization per project "
    "(GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001 v3 / "
    "DCL-PROJECT-AUTHORIZATION-EVENT-TRANSACTION-001 C1/C2)"
)


class AuthorizationCollapseError(ValueError):
    """A single project's collapse could not be written."""


def _json_list(row: dict[str, Any], key: str) -> list[str]:
    parsed = row.get(f"{key}_parsed")
    if isinstance(parsed, list):
        return [str(item).strip() for item in parsed if str(item).strip()]
    raw = row.get(key)
    if isinstance(raw, list):
        return [str(item).strip() for item in raw if str(item).strip()]
    return []


def census_active_authorizations(db: KnowledgeDB) -> dict[str, Any]:
    """Read-only current-authorization census (C1/C2 shape)."""
    rows = db.list_project_authorizations(include_terminal=False)
    by_project: dict[str, list[str]] = defaultdict(list)
    wi_scoped: list[str] = []
    for row in rows:
        if str(row.get("status") or "").strip().lower() != ACTIVE_PROJECT_AUTHORIZATION_STATUS:
            continue
        project_id = str(row.get("project_id") or "")
        auth_id = str(row.get("id") or "")
        if not project_id or not auth_id:
            continue
        by_project[project_id].append(auth_id)
        if work_item_scoped_authorization_identity(auth_id, row.get("scope_summary")):
            wi_scoped.append(auth_id)
    multi = {pid: ids for pid, ids in by_project.items() if len(ids) > 1}
    return {
        "active_current_rows": sum(len(ids) for ids in by_project.values()),
        "projects_with_active": len(by_project),
        "wi_scoped_current_ids": len(wi_scoped),
        "projects_with_multiple_current_ids": len(multi),
        "max_per_project": max((len(ids) for ids in by_project.values()), default=0),
        "c1_violations": sorted(multi),
        "c2_violations": sorted(set(wi_scoped)),
        "by_project": {pid: list(ids) for pid, ids in sorted(by_project.items())},
    }


def union_granted_envelope(rows: list[dict[str, Any]], *, db: KnowledgeDB) -> dict[str, Any]:
    """Union of grants: allow-lists union, deny-lists intersection, longest expiry."""
    allowed: list[str] = []
    seen_allowed: set[str] = set()
    forbidden_sets: list[set[str]] = []
    included_specs: list[str] = []
    seen_specs: set[str] = set()
    excluded_sets: list[set[str]] = []
    expiries: list[datetime] = []
    unbounded_expiry = False
    names: list[str] = []
    for row in rows:
        name = str(row.get("authorization_name") or "").strip()
        if name:
            names.append(name)
        for item in _json_list(row, "allowed_mutation_classes"):
            if item not in seen_allowed:
                seen_allowed.add(item)
                allowed.append(item)
        forbidden_sets.append(set(_json_list(row, "forbidden_operations")))
        for item in _json_list(row, "included_spec_ids"):
            if item not in seen_specs:
                seen_specs.add(item)
                included_specs.append(item)
        excluded_sets.append(set(_json_list(row, "excluded_spec_ids")))
        raw_expiry = row.get("expires_at")
        if not raw_expiry:
            unbounded_expiry = True
        else:
            parsed = parse_expires_at(str(raw_expiry))
            if parsed is None:
                unbounded_expiry = True
            else:
                expiries.append(parsed)
    forbidden: list[str] = []
    if forbidden_sets and all(forbidden_sets):
        shared = set.intersection(*forbidden_sets)
        forbidden = sorted(shared)
    excluded: list[str] = []
    if excluded_sets and all(excluded_sets):
        shared_ex = set.intersection(*excluded_sets)
        excluded = sorted(shared_ex)
    approved_specs: list[str] = []
    for spec_id in included_specs:
        spec = db.get_spec(spec_id)
        if spec is None:
            continue
        if spec.get("status") in APPROVED_SPEC_STATUSES:
            approved_specs.append(spec_id)
    expires_at = None if unbounded_expiry or not expiries else max(expiries).strftime("%Y-%m-%dT%H:%M:%SZ")
    source_ids = [str(row.get("id") or "") for row in rows if row.get("id")]
    scope = "One current project authorization (WI-6618). Union of grants from " + ", ".join(source_ids) + "."
    return {
        "authorization_name": names[0] if len(names) == 1 else "Current project authorization",
        "scope_summary": scope[:2000],
        "allowed_mutation_classes": allowed or None,
        "forbidden_operations": forbidden or None,
        "included_spec_ids": approved_specs,
        "excluded_spec_ids": excluded or None,
        "expires_at": expires_at,
        "supersedes": source_ids,
    }


def choose_current_authorization_id(project_id: str, db: KnowledgeDB) -> str:
    """Pick a project-scoped identity that is not WI-scoped and is unused, if possible."""
    candidates = [
        f"PAUTH-{project_id}",
        f"PAUTH-{project_id}-ONE-CURRENT",
    ]
    for candidate in candidates:
        if work_item_scoped_authorization_identity(candidate):
            continue
        existing = db.get_project_authorization(candidate)
        if existing is None:
            return candidate
        if str(existing.get("project_id") or "") == project_id:
            # Reuse only when it is already this project's and we will supersede
            # every live identity first, then insert a new version. Prefer a
            # fresh unused id so the active insert is version 1 (no spec-amendment
            # packet). Fall through.
            continue
    suffix = 1
    while True:
        candidate = f"PAUTH-{project_id}-ONE-CURRENT-{suffix}"
        if db.get_project_authorization(candidate) is None and not work_item_scoped_authorization_identity(candidate):
            return candidate
        suffix += 1


def _copy_historical_fields(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "authorization_name": str(row.get("authorization_name") or "superseded authorization"),
        "owner_decision": str(row.get("owner_decision_deliberation_id") or COLLAPSE_OWNER_DECISION),
        "scope_summary": str(row.get("scope_summary") or "Superseded by WI-6618."),
        "allowed_mutation_classes": _json_list(row, "allowed_mutation_classes") or None,
        "forbidden_operations": _json_list(row, "forbidden_operations") or None,
        "included_spec_ids": _json_list(row, "included_spec_ids") or None,
        "excluded_spec_ids": _json_list(row, "excluded_spec_ids") or None,
        "expires_at": row.get("expires_at"),
    }


def collapse_project(
    db: KnowledgeDB,
    project_id: str,
    *,
    changed_by: str,
    change_reason: str = CHANGE_REASON,
    dry_run: bool = True,
) -> dict[str, Any]:
    """Supersede every live identity for ``project_id`` and insert one current row."""
    live = [
        row
        for row in db.list_project_authorizations(project_id)
        if str(row.get("status") or "").strip().lower() == ACTIVE_PROJECT_AUTHORIZATION_STATUS
    ]
    if not live:
        return {"project_id": project_id, "skipped": True, "reason": "no_active_authorization"}
    envelope = union_granted_envelope(live, db=db)
    left_unauthorized = not envelope["included_spec_ids"]
    new_id = None if left_unauthorized else choose_current_authorization_id(project_id, db)
    plan = {
        "project_id": project_id,
        "skipped": False,
        "new_id": new_id,
        "left_unauthorized": left_unauthorized,
        "supersede_ids": [str(row.get("id") or "") for row in live],
        "envelope": envelope,
        "dry_run": dry_run,
    }
    if dry_run:
        return plan
    conn = db._get_conn()
    try:
        successor = [new_id] if new_id else None
        for row in live:
            hist = _copy_historical_fields(row)
            owner = hist["owner_decision"]
            if db.get_deliberation(owner) is None:
                owner = COLLAPSE_OWNER_DECISION
            inserted = db.insert_project_authorization(
                project_id,
                hist["authorization_name"],
                owner,
                hist["scope_summary"],
                changed_by,
                change_reason,
                id=str(row["id"]),
                status=COLLAPSE_STATUS_SUPERSEDED,
                allowed_mutation_classes=hist["allowed_mutation_classes"],
                forbidden_operations=hist["forbidden_operations"],
                included_spec_ids=hist["included_spec_ids"],
                excluded_spec_ids=hist["excluded_spec_ids"],
                expires_at=hist["expires_at"],
                superseded_by=successor,
                commit=False,
            )
            if inserted is None:
                raise AuthorizationCollapseError(f"{project_id}: supersede insert returned None for {row.get('id')}")
        current = None
        if not left_unauthorized:
            current = db.insert_project_authorization(
                project_id,
                envelope["authorization_name"],
                COLLAPSE_OWNER_DECISION,
                envelope["scope_summary"],
                changed_by,
                change_reason,
                id=new_id,
                status=ACTIVE_PROJECT_AUTHORIZATION_STATUS,
                allowed_mutation_classes=envelope["allowed_mutation_classes"],
                forbidden_operations=envelope["forbidden_operations"],
                included_spec_ids=envelope["included_spec_ids"],
                excluded_spec_ids=envelope["excluded_spec_ids"],
                expires_at=envelope["expires_at"],
                supersedes=envelope["supersedes"],
                commit=False,
            )
            if current is None:
                raise AuthorizationCollapseError(f"{project_id}: current insert returned None")
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    if current is not None:
        plan["written_current"] = {"id": current.get("id"), "version": current.get("version")}
    return plan


def collapse_all(
    db: KnowledgeDB,
    *,
    changed_by: str,
    change_reason: str = CHANGE_REASON,
    dry_run: bool = True,
) -> dict[str, Any]:
    before = census_active_authorizations(db)
    results: list[dict[str, Any]] = []
    errors: list[str] = []
    for project_id in sorted(before["by_project"]):
        try:
            results.append(
                collapse_project(
                    db,
                    project_id,
                    changed_by=changed_by,
                    change_reason=change_reason,
                    dry_run=dry_run,
                )
            )
        except Exception as exc:  # noqa: BLE001 - per-project isolation
            errors.append(f"{project_id}: {exc}")
    after = census_active_authorizations(db) if not dry_run else before
    left_unauthorized = [str(item.get("project_id")) for item in results if item.get("left_unauthorized")]
    return {
        "before": {k: v for k, v in before.items() if k != "by_project"},
        "after": {k: v for k, v in after.items() if k != "by_project"},
        "projects": results,
        "errors": errors,
        "dry_run": dry_run,
        "left_unauthorized": left_unauthorized,
        "c1_fail_closed": (not dry_run) and after["projects_with_multiple_current_ids"] == 0,
        "c2_fail_closed": (not dry_run) and after["wi_scoped_current_ids"] == 0,
    }
