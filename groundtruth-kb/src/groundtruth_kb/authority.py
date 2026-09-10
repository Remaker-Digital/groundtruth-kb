"""Resolve current canonical terminology without a file-backed authority map."""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Iterable
from difflib import get_close_matches
from typing import Any


class AuthorityResolutionError(ValueError):
    """Current terminology cannot be interpreted without guessing."""


def _normalize(value: str) -> str:
    return " ".join(value.split()).casefold()


def _match_keys(record: dict[str, Any]) -> set[str]:
    aliases = record.get("accepted_synonyms")
    if aliases is None:
        aliases = []
    if not isinstance(aliases, list):
        raise AuthorityResolutionError(f"{record['id']}: accepted_synonyms must be a string list")
    values = [record.get("id"), record.get("canonical_term"), *aliases]
    if any(not isinstance(value, str) or not _normalize(value) for value in values):
        raise AuthorityResolutionError(f"{record['id']}: names and accepted synonyms must be nonempty strings")
    return {_normalize(value) for value in values}


def _active(records: Iterable[dict[str, Any]], scope: str | None) -> list[dict[str, Any]]:
    return sorted(
        (row for row in records if row["lifecycle_status"] == "active" and (scope is None or row["scope"] == scope)),
        key=lambda row: row["id"],
    )


def resolve_term(term: str, *, records: Iterable[dict[str, Any]], scope: str | None = None) -> dict[str, Any]:
    """Match current IDs, names or accepted synonyms; never select an ambiguous match."""
    if not _normalize(term):
        raise AuthorityResolutionError("A nonempty term is required")
    active = _active(records, scope)
    keys = {}
    query = _normalize(term)
    for row in active:
        try:
            keys[row["id"]] = _match_keys(row)
        except AuthorityResolutionError:
            # Refuse a malformed entry's recognizable names without disabling
            # unrelated subjects during reconciliation.
            aliases = row.get("accepted_synonyms")
            values = [row.get("id"), row.get("canonical_term")]
            if isinstance(aliases, list):
                values.extend(aliases)
            if any(isinstance(value, str) and _normalize(value) == query for value in values):
                raise
    matches = [row for row in active if query in keys.get(row["id"], set())]
    if not matches:
        known = sorted({key for values in keys.values() for key in values})
        return {
            "status": "not_found",
            "term": term,
            "message": "No current canonical term matched.",
            "candidates": get_close_matches(_normalize(term), known, n=5, cutoff=0.55),
        }
    if len(matches) != 1:
        return {
            "status": "ambiguous",
            "term": term,
            "message": "Multiple current terms matched; select a scope or read an exact record ID.",
            "candidates": [{key: row[key] for key in ("id", "canonical_term", "scope")} for row in matches],
        }
    return {"status": "resolved", "term": term, "message": "Current canonical term resolved.", "record": matches[0]}


def compact_status(*, records: Iterable[dict[str, Any]], scope: str | None = None) -> dict[str, Any]:
    """Report interpretation conflicts in the current corpus, independent of installed files."""
    selected = [row for row in records if scope is None or row["scope"] == scope]
    active = _active(selected, scope)
    owners: dict[tuple[str, str], set[str]] = defaultdict(set)
    issues = []
    for row in active:
        try:
            keys = _match_keys(row)
        except AuthorityResolutionError as error:
            issues.append({"id": row["id"], "message": str(error)})
            continue
        for key in keys:
            owners[row["scope"], key].add(row["id"])
    ambiguous = [
        {"scope": key[0], "term": key[1], "ids": sorted(ids)} for key, ids in sorted(owners.items()) if len(ids) > 1
    ]
    return {
        "status": "pass" if active and not ambiguous and not issues else "fail",
        "source": "canonical_terms",
        "records": len(selected),
        "active_records": len(active),
        "inactive_records": len(selected) - len(active),
        "ambiguities": ambiguous,
        "validation_issues": issues,
    }


def format_resolution(result: dict[str, Any]) -> str:
    """Render canonical definitions and actionable ambiguity or failure diagnostics."""
    lines = [f"{result.get('status')}: {result.get('message', '')}".rstrip()]
    row = result.get("record")
    if row:
        lines.extend([f"{row['id']} v{row['version']}: {row['canonical_term']}", row["definition"]])
        lines.append(f"Source: {row['source_authority']}")
        lines.extend(f"Service: {value}" for value in row.get("linked_services") or [])
    for candidate in result.get("candidates", []):
        lines.append(
            f"Candidate: {candidate['id']} ({candidate['scope']})"
            if isinstance(candidate, dict)
            else f"Candidate: {candidate}"
        )
    if "active_records" in result:
        lines.append(f"{result['active_records']} active / {result['records']} current records")
    for ambiguity in result.get("ambiguities", []):
        lines.append(f"Ambiguous: {ambiguity['term']} ({ambiguity['scope']}): {', '.join(ambiguity['ids'])}")
    for issue in result.get("source_issues", []):
        lines.append(f"Source requires correction: {issue['id']} -> {issue['source_authority']} ({issue['status']})")
    for issue in result.get("validation_issues", []):
        lines.append(f"Term requires correction: {issue['id']}: {issue['message']}")
    return "\n".join(lines)
