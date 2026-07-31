"""Governed backlog/project query filters for CLI surfaces.

Agents must filter and sort backlog rows through ``gt backlog list`` (and
project rows through ``gt projects list``) rather than post-processing raw
MemBase output or opening SQLite directly.
"""

from __future__ import annotations

import fnmatch
import re
from dataclasses import dataclass
from typing import Any

from groundtruth_kb.backlog.approval_state import ALLOWED_STATES

# Fields exposed on ``current_work_items`` that ``gt backlog list`` may filter.
WORK_ITEM_EXACT_FILTER_FIELDS = frozenset(
    {
        "id",
        "title",
        "description",
        "origin",
        "component",
        "source_spec_id",
        "source_test_id",
        "failure_description",
        "resolution_status",
        "priority",
        "stage",
        "approval_state",
        "project_name",
        "subproject_name",
        "implementation_order",
        "status_detail",
        "source_owner_directive",
        "source_deliberation_query",
        "related_deliberation_ids",
        "related_spec_ids_at_creation",
        "related_bridge_threads",
        "depends_on_work_items",
        "blocks_work_items",
        "acceptance_summary",
        "regression_visibility",
        "completion_evidence",
        "supersedes",
        "superseded_by",
        "version",
        "changed_by",
        "changed_at",
        "change_reason",
    }
)

WORK_ITEM_PATTERN_FILTER_FIELDS = frozenset(WORK_ITEM_EXACT_FILTER_FIELDS)

WORK_ITEM_RANGE_FILTER_FIELDS = frozenset(
    {
        "id",
        "title",
        "origin",
        "component",
        "source_spec_id",
        "resolution_status",
        "priority",
        "stage",
        "approval_state",
        "project_name",
        "subproject_name",
        "implementation_order",
        "status_detail",
        "version",
        "changed_at",
    }
)

WORK_ITEM_SORT_FIELDS = frozenset(WORK_ITEM_EXACT_FILTER_FIELDS | {"implementation_order"})

PROJECT_EXACT_FILTER_FIELDS = frozenset(
    {
        "id",
        "name",
        "status",
        "parent_project_id",
        "source_project_name",
        "source_subproject_name",
        "purpose",
        "scope_note",
        "target_outcome",
        "notes",
        "rank",
        "start_date",
        "target_date",
        "completed_at",
        "version",
        "changed_by",
        "changed_at",
        "change_reason",
    }
)

PROJECT_SORT_FIELDS = frozenset(PROJECT_EXACT_FILTER_FIELDS)

PROJECT_PATTERN_FILTER_FIELDS = frozenset(PROJECT_EXACT_FILTER_FIELDS)

_PRIORITY_ORDER = {"P0": 0, "P1": 1, "P2": 2, "P3": 3, "P4": 4}

_FIELD_SPEC_RE = re.compile(r"^(?P<field>[a-z_]+):(?P<value>.*)$", re.IGNORECASE)
_MATCH_SPEC_RE = re.compile(r"^(?P<field>[a-z_]+):(?P<pattern>.+)$", re.IGNORECASE)
_RANGE_SPEC_RE = re.compile(
    r"^(?P<field>[a-z_]+):(?:(?P<lower>[^.]+)?\.\.(?P<upper>.+)?)$",
    re.IGNORECASE,
)


class BacklogQueryError(ValueError):
    """Raised when a query specification is invalid."""


@dataclass(frozen=True)
class SortKey:
    field: str
    descending: bool = False


@dataclass
class BacklogListQuery:
    """In-memory filter/sort specification for ``gt backlog list``."""

    include_terminal: bool = False
    work_item_ids: tuple[str, ...] = ()
    project_name: str | None = None
    subproject_name: str | None = None
    priorities: tuple[str, ...] = ()
    resolution_statuses: tuple[str, ...] = ()
    stages: tuple[str, ...] = ()
    origins: tuple[str, ...] = ()
    components: tuple[str, ...] = ()
    approval_states: tuple[str, ...] = ()
    contains_terms: tuple[str, ...] = ()
    exact_specs: tuple[str, ...] = ()
    match_specs: tuple[str, ...] = ()
    range_specs: tuple[str, ...] = ()
    member_of_project_ids: tuple[str, ...] = ()
    sort_keys: tuple[SortKey, ...] = ()
    limit: int | None = None


def parse_field_spec(spec: str, *, allowed_fields: frozenset[str]) -> tuple[str, str]:
    match = _FIELD_SPEC_RE.match(str(spec or "").strip())
    if match is None:
        raise BacklogQueryError(f"invalid --field value {spec!r}; expected field:value")
    field_name = match.group("field").lower()
    if field_name not in allowed_fields:
        raise BacklogQueryError(f"unsupported --field field {field_name!r}; allowed: {sorted(allowed_fields)}")
    return field_name, match.group("value")


def parse_match_spec(spec: str, *, allowed_fields: frozenset[str]) -> tuple[str, str]:
    match = _MATCH_SPEC_RE.match(str(spec or "").strip())
    if match is None:
        raise BacklogQueryError(f"invalid --match value {spec!r}; expected field:pattern")
    field_name = match.group("field").lower()
    if field_name not in allowed_fields:
        raise BacklogQueryError(f"unsupported --match field {field_name!r}; allowed: {sorted(allowed_fields)}")
    return field_name, match.group("pattern")


def parse_range_spec(spec: str, *, allowed_fields: frozenset[str]) -> tuple[str, str | None, str | None]:
    match = _RANGE_SPEC_RE.match(str(spec or "").strip())
    if match is None:
        raise BacklogQueryError(f"invalid --range value {spec!r}; expected field:min..max")
    field_name = match.group("field").lower()
    if field_name not in allowed_fields:
        raise BacklogQueryError(f"unsupported --range field {field_name!r}; allowed: {sorted(allowed_fields)}")
    lower = (match.group("lower") or "").strip() or None
    upper = (match.group("upper") or "").strip() or None
    if lower is None and upper is None:
        raise BacklogQueryError(f"invalid --range value {spec!r}; at least one bound is required")
    return field_name, lower, upper


def _normalize_approval_state(value: object) -> str:
    text = str(value or "").strip().lower()
    return text or "unapproved"


def _field_text(row: dict[str, Any], field_name: str) -> str:
    value = row.get(field_name)
    if value is None:
        return ""
    return str(value)


def _compare_values(field_name: str, left: object, right: object) -> int:
    if field_name == "priority":
        left_rank = _PRIORITY_ORDER.get(str(left or "").upper(), 99)
        right_rank = _PRIORITY_ORDER.get(str(right or "").upper(), 99)
        return (left_rank > right_rank) - (left_rank < right_rank)
    if field_name in {"implementation_order", "version"}:
        left_num = left if isinstance(left, int) else int(left) if str(left or "").isdigit() else None
        right_num = right if isinstance(right, int) else int(right) if str(right or "").isdigit() else None
        if left_num is None and right_num is None:
            return 0
        if left_num is None:
            return 1
        if right_num is None:
            return -1
        return (left_num > right_num) - (left_num < right_num)
    left_text = _field_text({"value": left}, "value")
    right_text = _field_text({"value": right}, "value")
    return (left_text > right_text) - (left_text < right_text)


def _matches_pattern(row: dict[str, Any], field_name: str, pattern: str) -> bool:
    haystack = _field_text(row, field_name).casefold()
    return fnmatch.fnmatchcase(haystack, pattern.casefold())


def _matches_range(row: dict[str, Any], field_name: str, lower: str | None, upper: str | None) -> bool:
    value = row.get(field_name)
    if value is None and field_name not in {"implementation_order", "version"}:
        return False
    if lower is not None and _compare_values(field_name, value, lower) < 0:
        return False
    return not (upper is not None and _compare_values(field_name, value, upper) > 0)


def _matches_any_exact(row: dict[str, Any], key: str, accepted: tuple[str, ...]) -> bool:
    if not accepted:
        return True
    if key == "approval_state":
        return _normalize_approval_state(row.get(key)) in {_normalize_approval_state(item) for item in accepted}
    value = row.get(key)
    return value is not None and str(value) in set(accepted)


def _matches_exact(row: dict[str, Any], key: str, expected: str | None) -> bool:
    if expected is None:
        return True
    if key == "approval_state":
        return _normalize_approval_state(row.get(key)) == _normalize_approval_state(expected)
    value = row.get(key)
    return value is not None and str(value) == expected


def _matches_contains(row: dict[str, Any], fields: tuple[str, ...], terms: tuple[str, ...]) -> bool:
    normalized_terms = tuple(term.casefold() for term in terms if term.strip())
    if not normalized_terms:
        return True
    haystack = " ".join(_field_text(row, field_name) for field_name in fields).casefold()
    return all(term in haystack for term in normalized_terms)


def validate_approval_states(states: tuple[str, ...]) -> None:
    for state in states:
        normalized = _normalize_approval_state(state)
        if normalized not in ALLOWED_STATES:
            raise BacklogQueryError(f"unknown approval_state {state!r}; allowed: {sorted(ALLOWED_STATES)}")


def filter_work_items(
    items: list[dict[str, Any]],
    query: BacklogListQuery,
    *,
    contains_fields: tuple[str, ...],
    project_membership_ids: dict[str, set[str]] | None = None,
) -> list[dict[str, Any]]:
    """Apply governed in-memory filters to work-item rows."""

    validate_approval_states(query.approval_states)
    parsed_exact = [parse_field_spec(spec, allowed_fields=WORK_ITEM_EXACT_FILTER_FIELDS) for spec in query.exact_specs]
    parsed_matches = [
        parse_match_spec(spec, allowed_fields=WORK_ITEM_PATTERN_FILTER_FIELDS) for spec in query.match_specs
    ]
    parsed_ranges = [parse_range_spec(spec, allowed_fields=WORK_ITEM_RANGE_FILTER_FIELDS) for spec in query.range_specs]
    membership_map = project_membership_ids or {}

    filtered: list[dict[str, Any]] = []
    for item in items:
        if not _matches_any_exact(item, "id", query.work_item_ids):
            continue
        if not _matches_exact(item, "project_name", query.project_name):
            continue
        if not _matches_exact(item, "subproject_name", query.subproject_name):
            continue
        if not _matches_any_exact(item, "priority", query.priorities):
            continue
        if not _matches_any_exact(item, "resolution_status", query.resolution_statuses):
            continue
        if not _matches_any_exact(item, "stage", query.stages):
            continue
        if not _matches_any_exact(item, "origin", query.origins):
            continue
        if not _matches_any_exact(item, "component", query.components):
            continue
        if not _matches_any_exact(item, "approval_state", query.approval_states):
            continue
        if not _matches_contains(item, contains_fields, query.contains_terms):
            continue
        if not all(_matches_exact(item, field_name, expected) for field_name, expected in parsed_exact):
            continue
        if not all(_matches_pattern(item, field_name, pattern) for field_name, pattern in parsed_matches):
            continue
        if not all(_matches_range(item, field_name, lower, upper) for field_name, lower, upper in parsed_ranges):
            continue
        if query.member_of_project_ids:
            work_item_id = str(item.get("id") or "")
            if not any(
                work_item_id in membership_map.get(project_id, set()) for project_id in query.member_of_project_ids
            ):
                continue
        filtered.append(item)

    sorted_items = sort_rows(filtered, query.sort_keys, allowed_fields=WORK_ITEM_SORT_FIELDS)
    if query.limit is not None:
        return sorted_items[: query.limit]
    return sorted_items


def sort_rows(
    rows: list[dict[str, Any]],
    sort_keys: tuple[SortKey, ...],
    *,
    allowed_fields: frozenset[str],
) -> list[dict[str, Any]]:
    if not sort_keys:
        return rows

    def sort_component(field_name: str, value: object, descending: bool) -> tuple[int, Any]:
        if value is None:
            return (1, "")
        if field_name in {"implementation_order", "rank", "version"}:
            normalized = value if isinstance(value, int) else int(value) if str(value).isdigit() else 10**9
            return (0, -normalized if descending else normalized)
        if field_name == "priority":
            normalized = _PRIORITY_ORDER.get(str(value or "").upper(), 99)
            return (0, -normalized if descending else normalized)
        text = str(value)
        return (0, tuple(-ord(ch) for ch in text) if descending else text)

    def sort_key(row: dict[str, Any]) -> tuple[Any, ...]:
        values: list[Any] = []
        for key in sort_keys:
            if key.field not in allowed_fields:
                raise BacklogQueryError(f"unsupported sort field {key.field!r}; allowed: {sorted(allowed_fields)}")
            values.append(sort_component(key.field, row.get(key.field), key.descending))
        return tuple(values)

    return sorted(rows, key=sort_key)


@dataclass
class ProjectListQuery:
    include_terminal: bool = False
    project_ids: tuple[str, ...] = ()
    status: str | None = None
    contains_terms: tuple[str, ...] = ()
    exact_specs: tuple[str, ...] = ()
    match_specs: tuple[str, ...] = ()
    sort_keys: tuple[SortKey, ...] = ()
    limit: int | None = None


def filter_projects(
    projects: list[dict[str, Any]],
    query: ProjectListQuery,
    *,
    contains_fields: tuple[str, ...],
) -> list[dict[str, Any]]:
    parsed_exact = [parse_field_spec(spec, allowed_fields=PROJECT_EXACT_FILTER_FIELDS) for spec in query.exact_specs]
    parsed_matches = [
        parse_match_spec(spec, allowed_fields=PROJECT_PATTERN_FILTER_FIELDS) for spec in query.match_specs
    ]
    filtered: list[dict[str, Any]] = []
    for project in projects:
        if query.project_ids and str(project.get("id") or "") not in set(query.project_ids):
            continue
        if query.status is not None and str(project.get("status") or "") != query.status:
            continue
        if not _matches_contains(project, contains_fields, query.contains_terms):
            continue
        if not all(_matches_exact(project, field_name, expected) for field_name, expected in parsed_exact):
            continue
        if not all(_matches_pattern(project, field_name, pattern) for field_name, pattern in parsed_matches):
            continue
        filtered.append(project)
    sorted_projects = sort_rows(filtered, query.sort_keys, allowed_fields=PROJECT_SORT_FIELDS)
    if query.limit is not None:
        return sorted_projects[: query.limit]
    return sorted_projects
