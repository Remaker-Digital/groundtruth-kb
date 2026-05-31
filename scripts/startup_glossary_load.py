"""Load canonical terminology for the startup disclosure surface."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

GLOSSARY_RELATIVE_PATH = ".claude/rules/canonical-terminology.md"

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


def load_glossary_for_startup(project_root: Path) -> dict[str, Any]:
    """Return structured canonical terminology for startup rendering.

    The result is cached for the current process. Missing or unreadable glossary
    files return a degraded structure instead of raising, so SessionStart can
    always emit a payload.
    """
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
        }
    )
    _CACHE[root] = result
    return result
