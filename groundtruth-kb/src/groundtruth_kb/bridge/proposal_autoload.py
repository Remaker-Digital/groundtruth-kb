"""Deterministic context loading for ``gt bridge propose`` drafts."""

from __future__ import annotations

import fnmatch
import json
import tomllib
from pathlib import Path
from typing import Any

from groundtruth_kb.db import KnowledgeDB

DEFAULT_BRIDGE_PROPOSAL_SPECS: tuple[str, ...] = (
    "GOV-FILE-BRIDGE-AUTHORITY-001",
    "GOV-ARTIFACT-ORIENTED-GOVERNANCE-001",
    "DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001",
    "DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001",
    "DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001",
    "SPEC-AUQ-POLICY-ENGINE-001",
    "ADR-ISOLATION-APPLICATION-PLACEMENT-001",
    "GOV-STANDING-BACKLOG-001",
    "ADR-CODEX-HOOK-PARITY-FALLBACK-001",
    "ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001",
    "DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001",
)


def _dedupe(values: list[str] | tuple[str, ...]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        item = str(value).strip()
        if item and item not in seen:
            seen.add(item)
            result.append(item)
    return result


def _parsed_list(row: dict[str, Any], field: str) -> list[str]:
    parsed = row.get(f"{field}_parsed") or row.get(f"_{field}_parsed") or row.get(field)
    if parsed is None:
        return []
    if isinstance(parsed, list):
        return [str(item) for item in parsed if str(item).strip()]
    if isinstance(parsed, str):
        try:
            decoded = json.loads(parsed)
        except json.JSONDecodeError:
            return [parsed] if parsed.strip() else []
        if isinstance(decoded, list):
            return [str(item) for item in decoded if str(item).strip()]
        if isinstance(decoded, str) and decoded.strip():
            return [decoded]
    return []


def _normalize_rel_path(path: str) -> str:
    return path.replace("\\", "/").strip("/")


def _path_matches(path: str, patterns: list[str]) -> bool:
    normalized = _normalize_rel_path(path)
    return any(fnmatch.fnmatch(normalized, pattern) for pattern in patterns)


def _load_applicability_rules(project_root: Path) -> list[dict[str, Any]]:
    config_path = project_root / "config" / "governance" / "spec-applicability.toml"
    if not config_path.is_file():
        return []
    with config_path.open("rb") as handle:
        data = tomllib.load(handle)
    rules = data.get("rules", [])
    return [rule for rule in rules if isinstance(rule, dict)]


def get_work_item_or_raise(db: KnowledgeDB, wi_id: str) -> dict[str, Any]:
    work_item = db.get_work_item(wi_id)
    if work_item is None:
        raise ValueError(f"Work item not found: {wi_id}")
    return work_item


def auto_spec_links(
    db: KnowledgeDB,
    project_root: Path,
    wi_id: str,
    kind: str,
    target_paths: tuple[str, ...],
    extra_specs: tuple[str, ...] = (),
) -> list[str]:
    """Return deterministic candidate spec links for a bridge proposal draft."""
    work_item = get_work_item_or_raise(db, wi_id)
    candidates: list[str] = []
    source_spec_id = str(work_item.get("source_spec_id") or "").strip()
    if source_spec_id:
        candidates.append(source_spec_id)
    candidates.extend(_parsed_list(work_item, "related_spec_ids_at_creation"))
    candidates.extend(DEFAULT_BRIDGE_PROPOSAL_SPECS)

    content_probe = " ".join(
        str(part)
        for part in (
            kind,
            "implementation proposal bridge proposal Specification Links verification",
            work_item.get("title"),
            work_item.get("description"),
            work_item.get("component"),
        )
        if part
    ).casefold()
    for rule in _load_applicability_rules(project_root):
        spec_id = str(rule.get("spec_id") or "").strip()
        if not spec_id:
            continue
        doc_patterns = [str(item) for item in rule.get("applies_when_doc_matches", [])]
        path_patterns = [str(item) for item in rule.get("applies_when_paths_match", [])]
        content_patterns = [str(item).casefold() for item in rule.get("applies_when_content_matches", [])]
        if "*" in doc_patterns:
            candidates.append(spec_id)
            continue
        if path_patterns and any(_path_matches(path, path_patterns) for path in target_paths):
            candidates.append(spec_id)
            continue
        if content_patterns and any(pattern in content_probe for pattern in content_patterns):
            candidates.append(spec_id)

    candidates.extend(extra_specs)
    return _dedupe(tuple(candidates))


def auto_prior_delibs(db: KnowledgeDB, wi_id: str, slug: str, *, limit: int = 5) -> list[str]:
    """Return prior-deliberation candidates, falling back to an empty list."""
    work_item = db.get_work_item(wi_id)
    query_parts = [wi_id, slug]
    if work_item:
        query_parts.extend(
            str(work_item.get(key) or "")
            for key in ("title", "description", "source_deliberation_query")
            if work_item.get(key)
        )
    try:
        rows = db.search_deliberations(" ".join(query_parts), limit=limit)
    except Exception:
        return []
    candidates: list[str] = []
    for row in rows:
        delib_id = str(row.get("id") or "").strip()
        if not delib_id:
            continue
        title = str(row.get("title") or row.get("summary") or "").strip()
        candidates.append(f"`{delib_id}` - {title}" if title else f"`{delib_id}`")
    return _dedupe(tuple(candidates))


def auto_owner_decisions(project_root: Path, wi_id: str) -> list[str]:
    """Return owner-decision tracker lines that mention the work item."""
    decision_path = project_root / "memory" / "pending-owner-decisions.md"
    if not decision_path.is_file():
        return []
    try:
        lines = decision_path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return []
    matches = [line.strip() for line in lines if wi_id in line and line.strip()]
    return _dedupe(tuple(matches))


def auto_target_paths_in_root_evidence(project_root: Path, target_paths: tuple[str, ...]) -> str:
    root = project_root.resolve()
    if not target_paths:
        return "No target paths were supplied; fill target_paths before filing the bridge proposal."
    normalized: list[str] = []
    for raw_path in target_paths:
        if not raw_path.strip():
            continue
        candidate = (root / raw_path).resolve()
        if not candidate.is_relative_to(root):
            raise ValueError(f"Target path is outside the project root: {raw_path}")
        normalized.append(_normalize_rel_path(raw_path))
    if not normalized:
        return "No target paths were supplied; fill target_paths before filing the bridge proposal."
    paths = ", ".join(f"`{path}`" for path in normalized)
    return f"All target paths are inside `{root}`: {paths}."


def auto_project_metadata(db: KnowledgeDB, wi_id: str) -> dict[str, str]:
    """Resolve active project metadata for a work item."""
    work_item = get_work_item_or_raise(db, wi_id)
    project: dict[str, Any] | None = None
    membership: dict[str, Any] | None = None
    for candidate_project in db.list_projects(include_terminal=True):
        for candidate_membership in db.list_project_work_items(
            candidate_project["id"],
            include_inactive=True,
        ):
            if candidate_membership.get("work_item_id") == wi_id:
                project = candidate_project
                membership = candidate_membership
                break
        if project:
            break

    project_id = str(project.get("id")) if project else str(work_item.get("project_name") or "")
    project_name = str(project.get("name")) if project else str(work_item.get("project_name") or "")
    authorization: dict[str, Any] | None = None
    if project:
        active_authorizations = db.list_project_authorizations(project["id"], status="active")
        for candidate_authorization in active_authorizations:
            included = _parsed_list(candidate_authorization, "included_work_item_ids")
            excluded = _parsed_list(candidate_authorization, "excluded_work_item_ids")
            if wi_id in excluded:
                continue
            if not included or wi_id in included:
                authorization = candidate_authorization
                break
        if authorization is None and active_authorizations:
            authorization = active_authorizations[0]

    return {
        "project_authorization_id": str(authorization.get("id"))
        if authorization
        else "<fill active project authorization>",
        "project_authorization_name": str(authorization.get("authorization_name")) if authorization else "",
        "project_id": project_id or "<fill project id>",
        "project_name": project_name,
        "work_item_id": wi_id,
        "work_item_title": str(work_item.get("title") or wi_id),
        "work_item_description": str(work_item.get("description") or ""),
        "membership_id": str(membership.get("membership_id")) if membership else "",
    }
