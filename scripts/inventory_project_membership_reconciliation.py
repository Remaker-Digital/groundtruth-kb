#!/usr/bin/env python3
"""Read-only inventory for project membership reconciliation.

The CLI fresh-reads MemBase current-state views and classifies every
non-terminal work item exactly once. It intentionally has no apply or mutate
mode; output is a dry-run inventory for later governed disposition slices.
"""

from __future__ import annotations

import argparse
import json
import sqlite3
import sys
import tomllib
from collections import Counter, defaultdict
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from urllib.parse import quote

PROJECT_ROOT = Path(__file__).resolve().parent.parent

TERMINAL_WORK_ITEM_STATUSES = {
    "verified",
    "resolved",
    "retired",
    "wont_fix",
    "not_a_defect",
}
PROJECT_TERMINAL_STATUSES = {
    "completed",
    "retired",
    "cancelled",
}
PRIMARY_CLASSIFICATIONS = (
    "already_active_project_member",
    "dangling_or_terminal_project_membership",
    "existing_project_candidate_exact",
    "existing_project_candidate_weak",
    "new_project_candidate_cluster",
    "single_wi_project_candidate",
    "obsolete_or_duplicate_candidate",
    "dependency_blocked_candidate",
    "needs_manual_triage",
)


class InventoryValidationError(ValueError):
    """Raised when the inventory fails exactly-once invariants."""


def utc_now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _row_to_dict(row: sqlite3.Row) -> dict[str, Any]:
    return dict(row)


def _normalize_token_text(value: Any) -> str:
    raw = str(value or "").strip().lower()
    normalized = []
    previous_dash = False
    for char in raw:
        if char.isalnum():
            normalized.append(char)
            previous_dash = False
        elif not previous_dash:
            normalized.append("-")
            previous_dash = True
    return "".join(normalized).strip("-")


def _token_set(*values: Any) -> set[str]:
    tokens: set[str] = set()
    for value in values:
        normalized = _normalize_token_text(value)
        if not normalized:
            continue
        tokens.update(part for part in normalized.split("-") if len(part) >= 3)
    return tokens


def _parse_json_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item) for item in value]
    text = str(value).strip()
    if not text:
        return []
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError:
        return [text]
    if isinstance(parsed, list):
        return [str(item) for item in parsed]
    if isinstance(parsed, str):
        return [parsed]
    return [str(parsed)]


def db_path_from_project_root(project_root: Path) -> Path:
    config = project_root / "groundtruth.toml"
    if not config.is_file():
        return project_root / "groundtruth.db"
    data = tomllib.loads(config.read_text(encoding="utf-8"))
    db_value = data.get("groundtruth", {}).get("db_path", "groundtruth.db")
    db_path = Path(str(db_value))
    return db_path if db_path.is_absolute() else project_root / db_path


def open_readonly_connection(db_path: Path) -> sqlite3.Connection:
    resolved = db_path.resolve()
    uri_path = quote(str(resolved).replace("\\", "/"), safe="/:")
    conn = sqlite3.connect(f"file:{uri_path}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    return conn


def _fetch_all(conn: sqlite3.Connection, table: str, *, order_by: str = "id") -> list[dict[str, Any]]:
    rows = conn.execute(f"SELECT * FROM {table} ORDER BY {order_by}").fetchall()  # noqa: S608 - table names are constants
    return [_row_to_dict(row) for row in rows]


def _is_non_terminal_work_item(row: dict[str, Any]) -> bool:
    status = str(row.get("resolution_status") or "").strip().lower()
    return status not in TERMINAL_WORK_ITEM_STATUSES


def _is_active_project(row: dict[str, Any] | None) -> bool:
    if row is None:
        return False
    status = str(row.get("status") or "").strip().lower()
    return status not in PROJECT_TERMINAL_STATUSES


def _is_active_membership(row: dict[str, Any]) -> bool:
    return str(row.get("status") or "").strip().lower() == "active"


def _is_active_dependency(row: dict[str, Any]) -> bool:
    status = str(row.get("status") or "").strip().lower()
    blocking = str(row.get("blocking_status") or "").strip().lower()
    return status == "active" and blocking in {"", "open", "blocked", "active"}


def _project_aliases(project: dict[str, Any]) -> set[str]:
    aliases = {
        _normalize_token_text(project.get("id")),
        _normalize_token_text(str(project.get("id") or "").removeprefix("PROJECT-")),
        _normalize_token_text(project.get("name")),
        _normalize_token_text(project.get("source_project_name")),
    }
    source_project = _normalize_token_text(project.get("source_project_name"))
    source_subproject = _normalize_token_text(project.get("source_subproject_name"))
    if source_project and source_subproject:
        aliases.add(f"{source_project}-{source_subproject}")
    return {alias for alias in aliases if alias}


def _exact_project_candidates(item: dict[str, Any], active_projects: list[dict[str, Any]]) -> list[str]:
    compatibility = {
        _normalize_token_text(item.get("project_name")),
        _normalize_token_text(item.get("subproject_name")),
    }
    project = _normalize_token_text(item.get("project_name"))
    subproject = _normalize_token_text(item.get("subproject_name"))
    if project and subproject:
        compatibility.add(f"{project}-{subproject}")
    compatibility = {value for value in compatibility if value}
    if not compatibility:
        return []
    candidates: list[str] = []
    for active_project in active_projects:
        if compatibility & _project_aliases(active_project):
            candidates.append(str(active_project["id"]))
    return sorted(set(candidates))


def _weak_project_candidates(item: dict[str, Any], active_projects: list[dict[str, Any]]) -> list[str]:
    item_tokens = _token_set(
        item.get("id"),
        item.get("title"),
        item.get("project_name"),
        item.get("subproject_name"),
        item.get("component"),
    )
    if not item_tokens:
        return []
    candidates: list[str] = []
    for project in active_projects:
        project_tokens = _token_set(
            project.get("id"),
            project.get("name"),
            project.get("source_project_name"),
            project.get("source_subproject_name"),
        )
        if len(item_tokens & project_tokens) >= 2:
            candidates.append(str(project["id"]))
    return sorted(set(candidates))


def _cluster_key(item: dict[str, Any]) -> str | None:
    for field in ("project_name", "subproject_name", "component"):
        normalized = _normalize_token_text(item.get(field))
        if normalized:
            return f"{field}:{normalized}"
    return None


def _has_obsolete_signal(item: dict[str, Any]) -> bool:
    if item.get("superseded_by") or item.get("supersedes"):
        return True
    text = " ".join(
        str(item.get(field) or "")
        for field in (
            "id",
            "title",
            "description",
            "status_detail",
            "acceptance_summary",
            "failure_description",
        )
    ).lower()
    return any(token in text for token in ("obsolete", "duplicate", "superseded", "supersedes", "retire"))


def _related_signals(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "source_spec_id": item.get("source_spec_id"),
        "source_test_id": item.get("source_test_id"),
        "source_owner_directive": item.get("source_owner_directive"),
        "source_deliberation_query": item.get("source_deliberation_query"),
        "related_deliberation_ids": _parse_json_list(item.get("related_deliberation_ids")),
        "related_spec_ids_at_creation": _parse_json_list(item.get("related_spec_ids_at_creation")),
        "related_bridge_threads": _parse_json_list(item.get("related_bridge_threads")),
        "supersedes": _parse_json_list(item.get("supersedes")),
        "superseded_by": _parse_json_list(item.get("superseded_by")),
    }


def _classify_item(
    item: dict[str, Any],
    *,
    memberships_by_wi: dict[str, list[dict[str, Any]]],
    active_projects_by_id: dict[str, dict[str, Any]],
    projects_by_id: dict[str, dict[str, Any]],
    active_projects: list[dict[str, Any]],
    dependency_blockers_by_project: dict[str, list[dict[str, Any]]],
    cluster_counts: Counter[str],
) -> dict[str, Any]:
    work_item_id = str(item["id"])
    memberships = memberships_by_wi.get(work_item_id, [])
    active_memberships = [
        membership
        for membership in memberships
        if _is_active_membership(membership) and membership.get("project_id") in active_projects_by_id
    ]
    active_project_ids = sorted({str(membership["project_id"]) for membership in active_memberships})
    exact_candidates = _exact_project_candidates(item, active_projects)
    weak_candidates = [
        candidate for candidate in _weak_project_candidates(item, active_projects) if candidate not in exact_candidates
    ]
    inferred_candidate_project_ids = [] if active_project_ids else sorted(set(exact_candidates + weak_candidates))
    dependency_project_ids = sorted(set(active_project_ids + inferred_candidate_project_ids))
    dependency_blockers: list[dict[str, Any]] = []
    for project_id in dependency_project_ids:
        dependency_blockers.extend(dependency_blockers_by_project.get(project_id, []))

    classification: str
    reason: str
    if dependency_blockers:
        classification = "dependency_blocked_candidate"
        reason = "associated or candidate project has active/open dependency"
    elif active_memberships:
        classification = "already_active_project_member"
        reason = "work item already has an active membership in a non-terminal project"
    elif memberships:
        classification = "dangling_or_terminal_project_membership"
        reason = "membership exists but is inactive, missing, or points to a terminal project"
    elif _has_obsolete_signal(item):
        classification = "obsolete_or_duplicate_candidate"
        reason = "work item carries obsolete, duplicate, superseded, or retirement signal"
    elif exact_candidates:
        classification = "existing_project_candidate_exact"
        reason = "compatibility project fields exactly match an active project alias"
    elif weak_candidates:
        classification = "existing_project_candidate_weak"
        reason = "title/id/component tokens weakly match an active project"
    else:
        cluster_key = _cluster_key(item)
        if cluster_key and cluster_counts[cluster_key] > 1:
            classification = "new_project_candidate_cluster"
            reason = f"unmatched compatibility cluster has {cluster_counts[cluster_key]} non-terminal work items"
        elif item.get("project_name") or item.get("subproject_name"):
            classification = "single_wi_project_candidate"
            reason = "unmatched compatibility project signal appears on one non-terminal work item"
        else:
            classification = "needs_manual_triage"
            reason = "no active membership, project candidate, duplicate signal, or cluster signal found"

    all_project_ids = sorted(
        {str(membership.get("project_id") or "") for membership in memberships if membership.get("project_id")}
    )
    dangling_project_ids = [
        project_id
        for project_id in all_project_ids
        if project_id not in active_projects_by_id or not _is_active_project(projects_by_id.get(project_id))
    ]

    return {
        "id": work_item_id,
        "title": item.get("title"),
        "classification": classification,
        "decision_reason": reason,
        "resolution_status": item.get("resolution_status"),
        "stage": item.get("stage"),
        "priority": item.get("priority"),
        "component": item.get("component"),
        "origin": item.get("origin"),
        "implementation_order": item.get("implementation_order"),
        "active_membership_ids": sorted(str(membership["id"]) for membership in active_memberships),
        "all_membership_ids": sorted(str(membership["id"]) for membership in memberships),
        "active_project_ids": active_project_ids,
        "candidate_project_ids": inferred_candidate_project_ids,
        "dependency_project_ids": dependency_project_ids,
        "dangling_or_terminal_project_ids": sorted(set(dangling_project_ids)),
        "dependency_blockers": [
            {
                "dependency_id": blocker.get("id"),
                "from_project_id": blocker.get("from_project_id"),
                "to_project_id": blocker.get("to_project_id"),
                "blocking_status": blocker.get("blocking_status"),
                "related_work_item_id": blocker.get("related_work_item_id"),
            }
            for blocker in dependency_blockers
        ],
        "evidence": {
            "compatibility_project_name": item.get("project_name"),
            "compatibility_subproject_name": item.get("subproject_name"),
            "exact_candidate_project_ids": exact_candidates,
            "weak_candidate_project_ids": weak_candidates,
            "cluster_key": _cluster_key(item),
            "related_signals": _related_signals(item),
        },
    }


def validate_exactly_once(expected_work_item_ids: list[str], items: list[dict[str, Any]]) -> None:
    expected = set(expected_work_item_ids)
    seen = [str(item.get("id") or "") for item in items]
    counts = Counter(seen)
    duplicates = sorted(item_id for item_id, count in counts.items() if item_id and count > 1)
    omitted = sorted(expected - set(seen))
    extra = sorted(set(seen) - expected)
    if duplicates or omitted or extra:
        details = []
        if duplicates:
            details.append("duplicate=" + ",".join(duplicates))
        if omitted:
            details.append("omitted=" + ",".join(omitted))
        if extra:
            details.append("extra=" + ",".join(extra))
        raise InventoryValidationError("Inventory is not exactly-once: " + "; ".join(details))


def build_inventory_from_connection(conn: sqlite3.Connection, *, generated_at: str | None = None) -> dict[str, Any]:
    work_items = [item for item in _fetch_all(conn, "current_work_items") if _is_non_terminal_work_item(item)]
    projects = _fetch_all(conn, "current_projects")
    memberships = _fetch_all(conn, "current_project_work_item_memberships")
    dependencies = _fetch_all(conn, "current_project_dependencies")

    projects_by_id = {str(project["id"]): project for project in projects}
    active_projects = [project for project in projects if _is_active_project(project)]
    active_projects_by_id = {str(project["id"]): project for project in active_projects}

    memberships_by_wi: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for membership in memberships:
        memberships_by_wi[str(membership.get("work_item_id") or "")].append(membership)

    dependency_blockers_by_project: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for dependency in dependencies:
        if _is_active_dependency(dependency):
            dependency_blockers_by_project[str(dependency.get("from_project_id") or "")].append(dependency)

    cluster_counts = Counter(key for item in work_items if (key := _cluster_key(item)))
    inventory_items = [
        _classify_item(
            item,
            memberships_by_wi=memberships_by_wi,
            active_projects_by_id=active_projects_by_id,
            projects_by_id=projects_by_id,
            active_projects=active_projects,
            dependency_blockers_by_project=dependency_blockers_by_project,
            cluster_counts=cluster_counts,
        )
        for item in work_items
    ]
    validate_exactly_once([str(item["id"]) for item in work_items], inventory_items)

    classification_counts = Counter(item["classification"] for item in inventory_items)
    return {
        "generated_at": generated_at or utc_now_iso(),
        "source_authority": {
            "work_items": "fresh read: current_work_items",
            "projects": "fresh read: current_projects",
            "memberships": "fresh read: current_project_work_item_memberships",
            "dependencies": "fresh read: current_project_dependencies",
            "read_only": True,
        },
        "classification_taxonomy": list(PRIMARY_CLASSIFICATIONS),
        "summary": {
            "total_non_terminal_work_items": len(work_items),
            "classification_counts": {
                classification: classification_counts.get(classification, 0)
                for classification in PRIMARY_CLASSIFICATIONS
            },
            "omitted_non_terminal_work_items": 0,
            "duplicate_inventory_rows": 0,
        },
        "items": sorted(
            inventory_items,
            key=lambda item: (
                PRIMARY_CLASSIFICATIONS.index(str(item["classification"])),
                str(item.get("priority") or "ZZ"),
                str(item["id"]),
            ),
        ),
    }


def build_inventory(db_path: Path) -> dict[str, Any]:
    with open_readonly_connection(db_path) as conn:
        return build_inventory_from_connection(conn)


def render_json(inventory: dict[str, Any]) -> str:
    return json.dumps(inventory, indent=2, sort_keys=True) + "\n"


def _markdown_cell(value: Any) -> str:
    text = "" if value is None else str(value)
    return text.replace("|", "\\|").replace("\n", " ")


def render_markdown(inventory: dict[str, Any]) -> str:
    lines: list[str] = [
        "# Project Membership Reconciliation Inventory",
        "",
        f"Generated: `{inventory['generated_at']}`",
        "",
        "## Summary",
        "",
        f"- Total non-terminal work items: {inventory['summary']['total_non_terminal_work_items']}",
        "- Source authority: fresh MemBase current-state views.",
        "- Mode: read-only dry-run; no project, membership, work-item, bridge, or owner-decision mutation is performed.",
        "",
        "| Classification | Count |",
        "|---|---:|",
    ]
    counts = inventory["summary"]["classification_counts"]
    for classification in PRIMARY_CLASSIFICATIONS:
        lines.append(f"| `{classification}` | {counts.get(classification, 0)} |")
    lines.append("")

    grouped: dict[str, list[dict[str, Any]]] = {classification: [] for classification in PRIMARY_CLASSIFICATIONS}
    for item in inventory["items"]:
        grouped[str(item["classification"])].append(item)

    for classification in PRIMARY_CLASSIFICATIONS:
        rows = grouped[classification]
        lines.extend([f"## {classification}", ""])
        if not rows:
            lines.extend(["_No rows._", ""])
            continue
        lines.extend(
            [
                "| Work Item | Priority | Status | Candidate Projects | Reason |",
                "|---|---|---|---|---|",
            ]
        )
        for item in rows:
            candidates = ", ".join(item.get("active_project_ids") or item.get("candidate_project_ids") or [])
            lines.append(
                "| "
                f"`{_markdown_cell(item['id'])}` | "
                f"`{_markdown_cell(item.get('priority') or '')}` | "
                f"`{_markdown_cell(item.get('resolution_status') or '')}` | "
                f"{_markdown_cell(candidates)} | "
                f"{_markdown_cell(item.get('decision_reason'))} |"
            )
        lines.append("")
    return "\n".join(lines)


def write_outputs(inventory: dict[str, Any], *, output_json: Path | None, output_markdown: Path | None) -> None:
    if output_json is not None:
        output_json.parent.mkdir(parents=True, exist_ok=True)
        output_json.write_text(render_json(inventory), encoding="utf-8")
    if output_markdown is not None:
        output_markdown.parent.mkdir(parents=True, exist_ok=True)
        output_markdown.write_text(render_markdown(inventory), encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", type=Path, default=PROJECT_ROOT)
    parser.add_argument("--db-path", type=Path, default=None)
    parser.add_argument("--format", choices=("json", "markdown"), default="json")
    parser.add_argument("--output-json", type=Path, default=None)
    parser.add_argument("--output-markdown", type=Path, default=None)
    args = parser.parse_args(argv)

    project_root = args.project_root.resolve()
    db_path = args.db_path.resolve() if args.db_path else db_path_from_project_root(project_root).resolve()
    inventory = build_inventory(db_path)
    write_outputs(inventory, output_json=args.output_json, output_markdown=args.output_markdown)
    if args.format == "json":
        sys.stdout.write(render_json(inventory))
    else:
        sys.stdout.write(render_markdown(inventory))
        sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
