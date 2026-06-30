"""Load canonical terminology for the startup disclosure surface."""

from __future__ import annotations

import re
import tomllib
from pathlib import Path
from typing import Any

GLOSSARY_RELATIVE_PATH = ".claude/rules/canonical-terminology.md"
GLOSSARY_CONFIG_RELATIVE_PATH = ".claude/rules/canonical-terminology.toml"
CORE_PROFILE_KEY = "dual-agent"

_TERM_HEADING_RE = re.compile(r"^###\s+(?P<name>.+?)\s*$", re.MULTILINE)
_FIELD_RE = re.compile(r"^\*\*(?P<field>Definition|Source|Implementation pointer):\*\*\s*(?P<value>.*)$")
_CACHE: dict[Path, dict[str, Any]] = {}


def clear_glossary_cache() -> None:
    """Clear the in-process glossary cache for tests and explicit refreshes."""
    _CACHE.clear()


def _collapse_lines(lines: list[str]) -> str:
    return " ".join(line.strip() for line in lines if line.strip()).strip()


def _extract_fields(block: str) -> dict[str, str]:
    fields: dict[str, str] = {}
    current_field: str | None = None
    current_lines: list[str] = []

    def flush() -> None:
        nonlocal current_field, current_lines
        if current_field:
            fields[current_field] = _collapse_lines(current_lines)
        current_field = None
        current_lines = []

    for raw_line in block.splitlines():
        line = raw_line.rstrip()
        match = _FIELD_RE.match(line)
        if match:
            flush()
            current_field = match.group("field").lower().replace(" ", "_")
            current_lines = [match.group("value")]
            continue
        if current_field:
            if line.startswith("**") or line.startswith("### "):
                flush()
                continue
            current_lines.append(line)
    flush()
    return fields


def _parse_glossary(text: str) -> tuple[dict[str, dict[str, str]], list[str]]:
    headings = list(_TERM_HEADING_RE.finditer(text))
    terms: dict[str, dict[str, str]] = {}
    order: list[str] = []
    for index, match in enumerate(headings):
        name = match.group("name").strip()
        start = match.end()
        end = headings[index + 1].start() if index + 1 < len(headings) else len(text)
        fields = _extract_fields(text[start:end])
        if not fields.get("definition"):
            continue
        terms[name] = {
            "definition": fields.get("definition", ""),
            "source": fields.get("source", ""),
            "implementation_pointer": fields.get("implementation_pointer", ""),
        }
        order.append(name)
    return terms, order


def _normalize_term_label(value: str) -> str:
    return " ".join(value.lower().split())


def _match_glossary_heading(term_label: str, terms: dict[str, dict[str, str]]) -> str | None:
    """Map a profile or primer label to a glossary heading when possible."""
    needle = _normalize_term_label(term_label)
    for name in terms:
        if _normalize_term_label(name) == needle:
            return name
    for name in terms:
        norm = _normalize_term_label(name)
        parts = [part.strip() for part in norm.replace("/", " ").split()]
        if needle in parts or needle == norm:
            return name
    return None


def _load_core_startup_term_names(project_root: Path) -> list[str]:
    """Return the bounded core primer term labels for base startup (S327 / ADR-0001)."""
    config_path = project_root / GLOSSARY_CONFIG_RELATIVE_PATH
    if config_path.is_file():
        try:
            raw = tomllib.loads(config_path.read_text(encoding="utf-8"))
            profiles = raw.get("config", {}).get("profiles", {})
            profile = profiles.get(CORE_PROFILE_KEY, {})
            primer = profile.get("required_primer_terms")
            if isinstance(primer, list) and all(isinstance(item, str) for item in primer):
                return list(primer)
        except (OSError, tomllib.TOMLDecodeError):
            pass
    return [
        "MemBase",
        "Deliberation Archive",
        "MEMORY.md",
        "Prime Builder",
        "Loyal Opposition",
        "GT-KB",
        "GroundTruth-KB",
        "GTKB",
        "platform",
        "application",
        "hosted application",
        "Agent Red",
        "adopter",
        "project",
        "work item",
        "backlog",
        "specification",
        "requirement",
        "implementation proposal",
        "implementation report",
        "verification",
        "dashboard",
        "bridge",
    ]


def _filter_terms_for_labels(
    terms: dict[str, dict[str, str]],
    labels: list[str],
) -> tuple[dict[str, dict[str, str]], list[str]]:
    filtered: dict[str, dict[str, str]] = {}
    order: list[str] = []
    for label in labels:
        heading = _match_glossary_heading(label, terms)
        if heading is None or heading in filtered:
            continue
        filtered[heading] = terms[heading]
        order.append(heading)
    return filtered, order


def _load_parsed_glossary(project_root: Path) -> dict[str, Any]:
    """Return the full parsed glossary structure (cached per project root)."""
    root = project_root.resolve()
    cached = _CACHE.get(root)
    if cached is not None:
        return cached

    source = root / GLOSSARY_RELATIVE_PATH
    result: dict[str, Any] = {
        "status": "missing",
        "source": GLOSSARY_RELATIVE_PATH,
        "path": str(source),
        "terms": {},
        "term_order": [],
        "error": None,
        "full_term_count": 0,
    }
    if not source.is_file():
        _CACHE[root] = result
        return result
    try:
        text = source.read_text(encoding="utf-8")
    except OSError as exc:
        result["status"] = "error"
        result["error"] = str(exc)
        _CACHE[root] = result
        return result

    terms, order = _parse_glossary(text)
    result.update(
        {
            "status": "loaded",
            "terms": terms,
            "term_order": order,
            "term_count": len(order),
            "full_term_count": len(order),
        }
    )
    _CACHE[root] = result
    return result


def load_glossary_for_startup(project_root: Path) -> dict[str, Any]:
    """Return the bounded core terminology subset for base session startup.

    Base startup loads only the core GT-KB primer subset (``required_primer_terms``
    from ``canonical-terminology.toml``). Activity-specific terms are resolved on
    ``::open <activity>`` via :func:`resolve_glossary_terms`.
    """
    parsed = _load_parsed_glossary(project_root)
    core_labels = _load_core_startup_term_names(project_root)
    terms = parsed.get("terms") if isinstance(parsed.get("terms"), dict) else {}
    filtered_terms, filtered_order = _filter_terms_for_labels(terms, core_labels)
    full_count = int(parsed.get("full_term_count") or len(parsed.get("term_order") or []))
    return {
        **parsed,
        "scope": "core_startup",
        "core_term_labels": core_labels,
        "terms": filtered_terms,
        "term_order": filtered_order,
        "term_count": len(filtered_order),
        "full_term_count": full_count,
        "progressive_disclosure": "activity_envelope",
    }


def resolve_glossary_terms(project_root: Path, term_labels: list[str]) -> dict[str, dict[str, str]]:
    """Resolve activity-profile terminology labels to glossary definitions."""
    parsed = _load_parsed_glossary(project_root)
    terms = parsed.get("terms") if isinstance(parsed.get("terms"), dict) else {}
    resolved: dict[str, dict[str, str]] = {}
    for label in term_labels:
        heading = _match_glossary_heading(label, terms)
        if heading is None:
            continue
        resolved[label] = terms[heading]
    return resolved
