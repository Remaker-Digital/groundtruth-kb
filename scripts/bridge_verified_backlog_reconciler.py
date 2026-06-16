#!/usr/bin/env python3
"""Resolve active work items whose linked bridge threads are all VERIFIED."""

from __future__ import annotations

# ruff: noqa: E402,I001

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent
GROUNDTRUTH_SRC = PROJECT_ROOT / "groundtruth-kb" / "src"
if str(GROUNDTRUTH_SRC) not in sys.path:
    sys.path.insert(0, str(GROUNDTRUTH_SRC))

from groundtruth_kb.db import (  # noqa: E402
    KnowledgeDB,
    WORK_ITEM_BACKLOG_FIELDS,
    WORK_ITEM_TERMINAL_RESOLUTION_STATUSES,
)

BRIDGE_FILE_STATUS_RE = re.compile(r"^[#>*\-\s`]*(NEW|REVISED|GO|NO-GO|VERIFIED|ADVISORY|WITHDRAWN)\b")
BRIDGE_PATH_RE = re.compile(r"(?:^|\b)bridge/([A-Za-z0-9_.-]+?)-\d{3}\.md(?:\b|$)")
VERSIONED_MD_RE = re.compile(r"^([A-Za-z0-9_.-]+?)-\d{3}\.md$")
TOKEN_SPLIT_RE = re.compile(r"[,;\r\n]+")
# Canonical bridge-file metadata line declaring the thread's parent work item.
# Anchored and MULTILINE so only the metadata declaration matches, never a prose
# WI mention. The captured ID is upper-cased to key the reverse index against the
# canonical uppercase work_items.id form.
_WORK_ITEM_METADATA_RE = re.compile(r"^Work Item:\s*(WI-[A-Za-z0-9-]+)\s*$", re.MULTILINE | re.IGNORECASE)

CHANGED_BY = "bridge-verified-backlog-reconciler"
CHANGE_REASON = (
    "Resolved by bridge VERIFIED backlog reconciler per DELIB-S345-BRIDGE-VERIFICATION-RETIRES-PARENT-BACKLOG-ITEM."
)
REPAIR_CHANGED_BY = "bridge-verified-backlog-reconciler-repair"
REPAIR_CHANGE_REASON = (
    "Reopened by bridge VERIFIED backlog reconciler repair after "
    "bridge/gtkb-bridge-verified-backlog-retirement-006.md NO-GO identified "
    "an overbroad related_bridge_threads closure predicate."
)


def _status_from_bridge_file(path: Path) -> str | None:
    try:
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return None
    for raw in lines:
        stripped = raw.strip()
        if not stripped:
            continue
        match = BRIDGE_FILE_STATUS_RE.match(stripped)
        return match.group(1).upper() if match else None
    return None


def collect_latest_bridge_statuses(project_root: Path) -> dict[str, dict[str, str]]:
    """Return the latest status row for each numbered bridge-file thread."""

    latest: dict[str, tuple[int, str, str]] = {}
    bridge_dir = project_root / "bridge"
    if not bridge_dir.is_dir():
        return {}
    for path in bridge_dir.glob("*.md"):
        match = VERSIONED_MD_RE.match(path.name)
        if match is None:
            continue
        slug = match.group(1)
        version_match = re.search(r"-(\d{3})\.md$", path.name)
        if version_match is None:
            continue
        status = _status_from_bridge_file(path)
        if status is None:
            continue
        rel_path = path.relative_to(project_root).as_posix()
        version = int(version_match.group(1))
        prior = latest.get(slug)
        if prior is None or version > prior[0]:
            latest[slug] = (version, status, rel_path)
    return {slug: {"status": status, "path": rel_path} for slug, (_version, status, rel_path) in sorted(latest.items())}


def _flatten_related_value(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        stripped = value.strip()
        if not stripped:
            return []
        try:
            decoded = json.loads(stripped)
        except json.JSONDecodeError:
            decoded = None
        if isinstance(decoded, (list, tuple)):
            return _flatten_related_value(decoded)
        if isinstance(decoded, str) and decoded != value:
            return _flatten_related_value(decoded)
        paths = [match.group(0).strip() for match in BRIDGE_PATH_RE.finditer(stripped)]
        if paths:
            remainder = BRIDGE_PATH_RE.sub(" ", stripped)
            return paths + [token for token in TOKEN_SPLIT_RE.split(remainder) if token]
        return [token for token in TOKEN_SPLIT_RE.split(stripped) if token]
    if isinstance(value, (list, tuple, set)):
        tokens: list[str] = []
        for item in value:
            tokens.extend(_flatten_related_value(item))
        return tokens
    return []


def normalize_bridge_reference(token: str) -> str | None:
    """Normalize a related_bridge_threads token to a bridge document slug."""

    cleaned = token.strip().strip("`'\"")
    if not cleaned:
        return None
    path_match = BRIDGE_PATH_RE.search(cleaned)
    if path_match:
        return path_match.group(1)
    if cleaned.startswith("bridge/"):
        cleaned = cleaned.removeprefix("bridge/")
    versioned_match = VERSIONED_MD_RE.match(cleaned)
    if versioned_match:
        return versioned_match.group(1)
    if cleaned.endswith(".md"):
        return None
    if "/" in cleaned or "\\" in cleaned:
        return None
    if re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]*", cleaned):
        return cleaned
    return None


def parse_related_bridge_threads(value: Any) -> list[str]:
    """Parse related_bridge_threads values without inferring from prose."""

    slugs: list[str] = []
    seen: set[str] = set()
    for token in _flatten_related_value(value):
        slug = normalize_bridge_reference(token)
        if slug and slug not in seen:
            slugs.append(slug)
            seen.add(slug)
    return slugs


def _bridge_thread_files(project_root: Path, slug: str) -> list[Path]:
    return sorted((project_root / "bridge").glob(f"{slug}-*.md"))


def build_work_item_bridge_links(
    project_root: Path,
    bridge_statuses: dict[str, dict[str, str]],
) -> dict[str, list[str]]:
    """Derive the reverse work-item -> [bridge slug] index from bridge files.

    Bridge files carry a canonical ``Work Item: WI-XXXX`` metadata line that
    declares the thread's parent work item (file -> WI). MemBase work items do
    not always carry the inverse ``related_bridge_threads`` link, so a VERIFIED
    bridge can never reach an unlinked WI through ``related_bridge_threads``
    alone. This builds the inverse map by scanning each indexed slug's files for
    the metadata line only (never prose WI mentions), so the reconciler can
    supplement a WI's links with the slugs that explicitly declare it.
    """

    index: dict[str, set[str]] = {}
    for slug in bridge_statuses:
        for path in _bridge_thread_files(project_root, slug):
            try:
                text = path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                text = path.read_text(encoding="utf-8", errors="replace")
            for match in _WORK_ITEM_METADATA_RE.finditer(text):
                work_item_id = match.group(1).upper()
                index.setdefault(work_item_id, set()).add(slug)
    return {work_item_id: sorted(slugs) for work_item_id, slugs in index.items()}


def _contains_work_item_id(text: str, work_item_id: str) -> bool:
    escaped = re.escape(work_item_id)
    return bool(re.search(rf"(?<![A-Za-z0-9_.-]){escaped}(?![A-Za-z0-9_.-])", text))


def bridge_thread_has_parent_evidence(project_root: Path, slug: str, work_item_id: str) -> dict[str, Any]:
    """Return explicit evidence that a bridge thread covers the work item.

    related_bridge_threads is a broad linkage field. For mechanical closure we
    require the bridge thread chain itself to carry the exact work item ID.
    """

    files = _bridge_thread_files(project_root, slug)
    matched_files: list[str] = []
    for path in files:
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            text = path.read_text(encoding="utf-8", errors="replace")
        if _contains_work_item_id(text, work_item_id):
            matched_files.append(str(path.relative_to(project_root)).replace("\\", "/"))
    return {
        "has_parent_evidence": bool(matched_files),
        "files_checked": [str(path.relative_to(project_root)).replace("\\", "/") for path in files],
        "matched_files": matched_files,
    }


def _completion_evidence(current: dict[str, Any], slugs: list[str]) -> str:
    evidence = (
        "Bridge VERIFIED backlog reconciler resolved this work item because "
        "all recognized parent implementation bridge threads are latest VERIFIED "
        "and carry explicit work-item evidence: "
        f"{', '.join(slugs)}. Source: "
        "DELIB-S345-BRIDGE-VERIFICATION-RETIRES-PARENT-BACKLOG-ITEM."
    )
    existing = current.get("completion_evidence")
    if isinstance(existing, str) and existing.strip():
        return f"{existing.rstrip()}\n{evidence}"
    return evidence


def classify_work_item(
    item: dict[str, Any],
    bridge_statuses: dict[str, dict[str, str]],
    *,
    project_root: Path = PROJECT_ROOT,
    ignore_terminal: bool = False,
    derived_links: dict[str, list[str]] | None = None,
) -> dict[str, Any]:
    raw_links = item.get("related_bridge_threads_parsed", item.get("related_bridge_threads"))
    parsed_links = parse_related_bridge_threads(raw_links)
    if derived_links:
        for slug in derived_links.get(item["id"], []):
            if slug not in parsed_links:
                parsed_links.append(slug)
    recognized = [slug for slug in parsed_links if slug in bridge_statuses]
    missing = [slug for slug in parsed_links if slug not in bridge_statuses]
    statuses = {slug: bridge_statuses[slug]["status"] for slug in recognized}
    parent_evidence = {
        slug: bridge_thread_has_parent_evidence(project_root, slug, item["id"])
        for slug in recognized
        if statuses.get(slug) == "VERIFIED"
    }
    missing_parent_evidence = [
        slug
        for slug in recognized
        if statuses.get(slug) == "VERIFIED" and not parent_evidence[slug]["has_parent_evidence"]
    ]

    if not ignore_terminal and item.get("resolution_status") in WORK_ITEM_TERMINAL_RESOLUTION_STATUSES:
        action = "skip"
        reason = "terminal_work_item"
    elif not parsed_links:
        action = "skip"
        reason = "no_related_bridge_threads"
    elif missing:
        action = "skip"
        reason = "missing_bridge_document"
    elif not recognized:
        action = "skip"
        reason = "unrecognized_only"
    elif any(status != "VERIFIED" for status in statuses.values()):
        action = "skip"
        reason = "linked_bridge_not_verified"
    elif missing_parent_evidence:
        action = "skip"
        reason = "missing_parent_evidence"
    else:
        action = "resolve"
        reason = "all_parent_links_verified"

    return {
        "id": item["id"],
        "title": item.get("title"),
        "resolution_status": item.get("resolution_status"),
        "stage": item.get("stage"),
        "related_bridge_threads": parsed_links,
        "recognized_bridge_threads": recognized,
        "missing_bridge_threads": missing,
        "bridge_statuses": statuses,
        "parent_evidence": parent_evidence,
        "missing_parent_evidence": missing_parent_evidence,
        "action": action,
        "reason": reason,
    }


def classify_reconciler_resolution(
    item: dict[str, Any],
    bridge_statuses: dict[str, dict[str, str]],
    *,
    project_root: Path = PROJECT_ROOT,
    derived_links: dict[str, list[str]] | None = None,
) -> dict[str, Any]:
    strict = classify_work_item(
        item,
        bridge_statuses,
        project_root=project_root,
        ignore_terminal=True,
        derived_links=derived_links,
    )
    if strict["action"] == "resolve":
        action = "keep_resolved"
        reason = "strict_parent_evidence_satisfied"
    else:
        action = "reopen"
        reason = f"overbroad_resolution_{strict['reason']}"
    return {**strict, "action": action, "reason": reason}


def _copy_work_item_version(
    db: KnowledgeDB,
    source: dict[str, Any],
    *,
    changed_by: str,
    change_reason: str,
) -> dict[str, Any] | None:
    kwargs = {field: source.get(field) for field in WORK_ITEM_BACKLOG_FIELDS}
    return db.insert_work_item(
        source["id"],
        source["title"],
        source["origin"],
        source["component"],
        source["resolution_status"],
        changed_by,
        change_reason,
        description=source.get("description"),
        source_spec_id=source.get("source_spec_id"),
        source_test_id=source.get("source_test_id"),
        failure_description=source.get("failure_description"),
        priority=source.get("priority"),
        stage=source.get("stage", "backlogged"),
        **kwargs,
    )


def _previous_nonterminal_version(db: KnowledgeDB, item_id: str) -> dict[str, Any] | None:
    for row in db.get_work_item_history(item_id)[1:]:
        if row.get("resolution_status") not in WORK_ITEM_TERMINAL_RESOLUTION_STATUSES:
            return row
    return None


def reconcile(
    *,
    project_root: Path = PROJECT_ROOT,
    db_path: Path | None = None,
    apply: bool = False,
    repair_overbroad: bool = False,
) -> dict[str, Any]:
    root = project_root.resolve()
    database_path = db_path or root / "groundtruth.db"

    bridge_statuses = collect_latest_bridge_statuses(root)
    derived_links = build_work_item_bridge_links(root, bridge_statuses)
    db = KnowledgeDB(database_path)
    resolved_ids: list[str] = []
    reopened_ids: list[str] = []
    errors: list[dict[str, str]] = []
    repair_inventory: list[dict[str, Any]] = []
    try:
        candidates = [
            item
            for item in db.get_open_work_items()
            if item.get("related_bridge_threads")
            or item.get("related_bridge_threads_parsed")
            or derived_links.get(item["id"])
        ]
        inventory = [
            classify_work_item(item, bridge_statuses, project_root=root, derived_links=derived_links)
            for item in candidates
        ]
        items_by_id = {item["id"]: item for item in candidates}
        if apply:
            for row in inventory:
                if row["action"] != "resolve":
                    continue
                current = items_by_id[row["id"]]
                try:
                    db.update_work_item(
                        row["id"],
                        CHANGED_BY,
                        CHANGE_REASON,
                        owner_approved=True,
                        resolution_status="resolved",
                        stage="resolved",
                        completion_evidence=_completion_evidence(current, row["recognized_bridge_threads"]),
                    )
                    resolved_ids.append(row["id"])
                except Exception as exc:  # pragma: no cover - defensive runtime reporting
                    errors.append({"id": row["id"], "error": str(exc)})
        if repair_overbroad:
            reconciler_resolutions = [
                item
                for item in db.list_work_items(resolution_status="resolved")
                if item.get("changed_by") == CHANGED_BY
            ]
            repair_inventory = [
                classify_reconciler_resolution(item, bridge_statuses, project_root=root, derived_links=derived_links)
                for item in reconciler_resolutions
            ]
            if apply:
                for row in repair_inventory:
                    if row["action"] != "reopen":
                        continue
                    try:
                        previous = _previous_nonterminal_version(db, row["id"])
                        if previous is None:
                            errors.append({"id": row["id"], "error": "no_previous_nonterminal_version"})
                            continue
                        _copy_work_item_version(
                            db,
                            previous,
                            changed_by=REPAIR_CHANGED_BY,
                            change_reason=REPAIR_CHANGE_REASON,
                        )
                        reopened_ids.append(row["id"])
                    except Exception as exc:  # pragma: no cover - defensive runtime reporting
                        errors.append({"id": row["id"], "error": str(exc)})
    finally:
        db.close()

    mode = "apply" if apply else "dry-run"
    if repair_overbroad:
        mode = f"{mode}+repair-overbroad"
    return {
        "project_root": str(root),
        "db_path": str(database_path),
        "bridge_state": str(root / "bridge"),
        "mode": mode,
        "bridge_document_count": len(bridge_statuses),
        "candidate_count": len(inventory),
        "would_resolve_ids": [row["id"] for row in inventory if row["action"] == "resolve"],
        "resolved_ids": resolved_ids,
        "repair_candidate_count": len(repair_inventory),
        "would_reopen_ids": [row["id"] for row in repair_inventory if row["action"] == "reopen"],
        "reopened_ids": reopened_ids,
        "errors": errors,
        "candidates": inventory,
        "repair_candidates": repair_inventory,
    }


def render_text(summary: dict[str, Any]) -> str:
    lines = [
        "Bridge VERIFIED backlog reconciler",
        f"mode: {summary['mode']}",
        f"candidates: {summary['candidate_count']}",
        f"would_resolve_ids: {summary['would_resolve_ids']}",
        f"resolved_ids: {summary['resolved_ids']}",
        f"repair_candidates: {summary['repair_candidate_count']}",
        f"would_reopen_ids: {summary['would_reopen_ids']}",
        f"reopened_ids: {summary['reopened_ids']}",
    ]
    if summary["errors"]:
        lines.append(f"errors: {summary['errors']}")
    for row in summary["candidates"]:
        lines.append(
            "- {id}: {action} ({reason}); status={resolution_status}; "
            "stage={stage}; links={recognized_bridge_threads}; "
            "bridge_statuses={bridge_statuses}".format(**row)
        )
    for row in summary["repair_candidates"]:
        lines.append(
            "- repair {id}: {action} ({reason}); status={resolution_status}; "
            "stage={stage}; links={recognized_bridge_threads}; "
            "missing_parent_evidence={missing_parent_evidence}".format(**row)
        )
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--dry-run", action="store_true", help="Report candidates without mutating MemBase.")
    mode.add_argument("--apply", action="store_true", help="Resolve eligible work items.")
    parser.add_argument(
        "--repair-overbroad",
        action="store_true",
        help="Audit reconciler-resolved rows and reopen ones without strict parent evidence.",
    )
    parser.add_argument("--quiet", action="store_true", help="Suppress normal output unless errors occur.")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")
    parser.add_argument("--project-root", type=Path, default=PROJECT_ROOT)
    parser.add_argument("--db-path", type=Path)
    args = parser.parse_args(argv)

    summary = reconcile(
        project_root=args.project_root,
        db_path=args.db_path,
        apply=args.apply,
        repair_overbroad=args.repair_overbroad,
    )
    if not args.quiet or summary["errors"]:
        if args.json:
            print(json.dumps(summary, indent=2, sort_keys=True))
        else:
            print(render_text(summary))
    return 1 if summary["errors"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
