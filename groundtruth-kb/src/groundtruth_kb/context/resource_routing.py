"""Deterministic routing for the canonical backlog and bridge-queue resources."""

from __future__ import annotations

import copy
import re
from typing import Any

RESOURCE_CONTRACT_SCHEMA_VERSION = 1
RESOURCE_SELECTION_SCHEMA_VERSION = 1
RESOURCE_PRECEDENCE = (
    "current_owner_literal > dispatch_provenance > activity_or_startup_default > prior_context_or_notes > conjecture"
)
RESOURCE_ORDER = ("backlog", "bridge_queue")
_WORK_ITEM_PATTERN = re.compile(r"(?<![A-Za-z0-9])WI-\d+(?![A-Za-z0-9])", re.IGNORECASE)

_CANONICAL_RESOURCE_CONTRACT: dict[str, Any] = {
    "schema_version": RESOURCE_CONTRACT_SCHEMA_VERSION,
    "precedence": RESOURCE_PRECEDENCE,
    "no_inference": True,
    "topic_qualifiers": [
        "bridge",
        "bridge work",
        "bridge-related",
        "TAFE",
        "harness",
        "harness-related",
    ],
    "resources": {
        "backlog": {
            "canonical_term": "backlog",
            "accepted_terms": [
                "backlog",
                "standing backlog",
                "active backlog",
                "current backlog",
                "work list",
                "known work",
            ],
            "authority": "MemBase current_work_items",
            "read_route": "gt backlog list",
            "non_alias": "bridge_queue",
        },
        "bridge_queue": {
            "canonical_term": "bridge queue",
            "accepted_terms": ["bridge queue", "review queue"],
            "authority": "TAFE/dispatcher bridge state plus status-bearing numbered files under bridge/",
            "read_route": "gt bridge state-report",
            "non_alias": "backlog",
        },
    },
}


class ResourceRoutingError(ValueError):
    """Raised when a resource contract or selection is not canonical."""


def canonical_resource_contract() -> dict[str, Any]:
    """Return an isolated copy of the exact two-resource contract."""

    return copy.deepcopy(_CANONICAL_RESOURCE_CONTRACT)


def validate_resource_contract(contract: object) -> dict[str, Any]:
    """Reject non-semantic, aliased, or swapped resource descriptors."""

    if not isinstance(contract, dict):
        raise ResourceRoutingError("resource_contract must be a table")
    expected = canonical_resource_contract()
    if contract != expected:
        raise ResourceRoutingError(
            "resource_contract must exactly preserve backlog and bridge_queue terms, authorities, read routes, "
            "non-alias semantics, and literal-owner precedence"
        )
    return copy.deepcopy(contract)


def _term_pattern(term: str) -> re.Pattern[str]:
    pieces = [re.escape(piece) for piece in re.split(r"[\s-]+", term) if piece]
    phrase = r"(?:\s+|-)".join(pieces)
    return re.compile(rf"(?<![A-Za-z0-9]){phrase}(?![A-Za-z0-9])", re.IGNORECASE)


def _resource_matches(prompt: str, resource: str) -> list[dict[str, Any]]:
    descriptor = _CANONICAL_RESOURCE_CONTRACT["resources"][resource]
    terms = sorted(descriptor["accepted_terms"], key=lambda value: (-len(value), value))
    candidates: list[tuple[int, int, str]] = []
    for term in terms:
        candidates.extend((match.start(), match.end(), term) for match in _term_pattern(term).finditer(prompt))
    candidates.sort(key=lambda match: (match[0], -(match[1] - match[0]), match[2]))

    accepted: list[dict[str, Any]] = []
    occupied: list[tuple[int, int]] = []
    for start, end, term in candidates:
        if any(start < used_end and end > used_start for used_start, used_end in occupied):
            continue
        occupied.append((start, end))
        accepted.append({"resource": resource, "term": term, "start": start, "end": end})
    return accepted


def _work_item_ids(prompt: str) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for match in _WORK_ITEM_PATTERN.finditer(prompt):
        work_item_id = match.group(0).upper()
        if work_item_id not in seen:
            seen.add(work_item_id)
            result.append(work_item_id)
    return result


def _selection(
    selected_resources: list[str],
    *,
    matched_terms: list[dict[str, Any]],
    selection_source: str,
    selection_authority: str,
    work_item_ids: list[str] | None = None,
    dispatch_run_id: str | None = None,
) -> dict[str, Any]:
    resources = _CANONICAL_RESOURCE_CONTRACT["resources"]
    return {
        "schema_version": RESOURCE_SELECTION_SCHEMA_VERSION,
        "selected_resources": selected_resources,
        "primary_resource": selected_resources[0] if len(selected_resources) == 1 else None,
        "matched_terms": [{"resource": item["resource"], "term": item["term"]} for item in matched_terms],
        "explicit_resource_terms": bool(matched_terms),
        "selection_source": selection_source,
        "selection_authority": selection_authority,
        "precedence": RESOURCE_PRECEDENCE,
        "authoritative_sources": {resource: resources[resource]["authority"] for resource in selected_resources},
        "read_routes": {resource: resources[resource]["read_route"] for resource in selected_resources},
        "work_item_ids": list(work_item_ids or []),
        "dispatch_run_id": dispatch_run_id,
    }


def resolve_resource_selection(
    prompt: str,
    *,
    selection_source: str = "current_owner_prompt",
) -> dict[str, Any]:
    """Resolve only explicit approved resource nouns in the current prompt."""

    prompt = prompt if isinstance(prompt, str) else ""
    matches: list[dict[str, Any]] = []
    for resource in RESOURCE_ORDER:
        matches.extend(_resource_matches(prompt, resource))
    matches.sort(key=lambda item: (item["start"], item["end"], RESOURCE_ORDER.index(item["resource"])))
    selected = [resource for resource in RESOURCE_ORDER if any(m["resource"] == resource for m in matches)]
    return _selection(
        selected,
        matched_terms=matches,
        selection_source=selection_source,
        selection_authority="current_owner_literal" if selected else "none",
        work_item_ids=_work_item_ids(prompt),
    )


def dispatch_resource_selection(dispatch_run_id: str | None) -> dict[str, Any]:
    """Select bridge_queue only when a worker carries nonblank dispatch provenance."""

    normalized = dispatch_run_id.strip() if isinstance(dispatch_run_id, str) else ""
    if not normalized:
        return resolve_resource_selection("", selection_source="no_dispatch_provenance")
    return _selection(
        ["bridge_queue"],
        matched_terms=[],
        selection_source="dispatcher_composition",
        selection_authority="dispatch_provenance",
        dispatch_run_id=normalized,
    )


def render_resource_context(selection: dict[str, Any]) -> str:
    """Render a compact prompt reminder for an explicit resource selection."""

    resources = selection.get("selected_resources") or []
    if not selection.get("explicit_resource_terms") or not resources:
        return ""
    labels = ", ".join(f"`{resource}`" for resource in resources)
    routes = "; ".join(f"`{resource}` via `{selection['read_routes'][resource]}`" for resource in resources)
    return (
        "# GT-KB Resource Selection\n\n"
        f"The current owner prompt explicitly selects {labels}. Read {routes}. "
        "`backlog` and `bridge_queue` are distinct, non-alias resources. Current explicit owner terms "
        "outrank activity defaults, startup ordering, prior context, notes, and conjecture. The file bridge "
        "remains a governance gate for protected changes; it does not replace the selected work resource."
    )


__all__ = [
    "RESOURCE_ORDER",
    "RESOURCE_PRECEDENCE",
    "ResourceRoutingError",
    "canonical_resource_contract",
    "dispatch_resource_selection",
    "render_resource_context",
    "resolve_resource_selection",
    "validate_resource_contract",
]
