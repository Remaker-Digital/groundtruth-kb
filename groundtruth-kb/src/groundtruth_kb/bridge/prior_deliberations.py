# (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Prior-deliberation seeding helpers for bridge authoring surfaces."""

from __future__ import annotations

import json
import os
import re
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

_GLOSSARY_HEADING_RE = re.compile(r"^###\s+(.+?)\s*$")
_GLOSSARY_ID_RE = re.compile(r"\b(?:DELIB-[A-Z0-9-]+|(?:SPEC|GOV|ADR|DCL|PB|REQ)-[A-Z0-9-]+)\b")
_PRIOR_DELIBS_HEADING = "## Prior Deliberations"

DEFAULT_GLOSSARY_PATH = Path(".claude/rules/canonical-terminology.md")
DEFAULT_PREPOPULATION_LOG = Path(".gtkb-state/bridge-propose-helper/last-prepopulation.json")
DEFAULT_PRE_POPULATION_LIMIT = 5
DEFAULT_DB_PATH = "groundtruth.db"
# WI-4565: bound the default-store open so an opt-in (db=True) semantic search
# can never hang on ChromaDB client construction / embedding-model load. Tunable
# via GTKB_DA_OPEN_TIMEOUT_SECONDS; degrades to glossary-only seeding on timeout.
_OPEN_DB_TIMEOUT_SECONDS = float(os.environ.get("GTKB_DA_OPEN_TIMEOUT_SECONDS") or "10")

NO_PRIOR_DELIBS_PLACEHOLDER = "_No prior deliberations: <fill in reason before filing>._"


def _discover_project_root() -> Path:
    for parent in Path(__file__).resolve().parents:
        if (parent / "scripts" / "bridge_author_metadata.py").is_file():
            return parent
    return Path(__file__).resolve().parents[4]


def _try_open_default_db() -> Any | None:
    """Attempt to open the default ``KnowledgeDB`` for semantic search.

    WI-4565: the construction is bounded by ``_OPEN_DB_TIMEOUT_SECONDS`` (via the
    shared daemon-thread timeout) so a stalled ChromaDB client / embedding-model
    load degrades to glossary-only seeding instead of hanging the bridge-authoring
    hot path. This is the read-side analogue of the FAB-17/WI-4519 query timeout,
    which bounded the query but left the store-open default unguarded.
    """
    try:
        from groundtruth_kb.db import KnowledgeDB, _call_with_timeout  # noqa: PLC0415

        return _call_with_timeout(lambda: KnowledgeDB(DEFAULT_DB_PATH), _OPEN_DB_TIMEOUT_SECONDS)
    except Exception:  # noqa: BLE001 - graceful degradation
        return None


def _glossary_seed_ids_for_topic(
    topic_slug: str,
    glossary_content: str,
) -> list[str]:
    """Extract DELIB/spec IDs from the glossary entry matching the topic slug."""
    if not topic_slug or not glossary_content:
        return []
    candidate = topic_slug.replace("-", " ").strip().lower()
    if not candidate:
        return []

    def extract_from_content(content: str) -> list[str]:
        if not content:
            return []
        lines = content.splitlines()
        found_seeds: list[str] = []
        for i, line in enumerate(lines):
            m = _GLOSSARY_HEADING_RE.match(line)
            if not m:
                continue
            heading_text = m.group(1).strip().lower()
            if heading_text != candidate:
                continue
            for j in range(i + 1, min(i + 30, len(lines))):
                if lines[j].lstrip().startswith("**Source:**"):
                    source_block = [lines[j]]
                    for k in range(j + 1, min(j + 30, len(lines))):
                        nxt = lines[k]
                        if nxt.lstrip().startswith("**") or nxt.startswith("### ") or nxt.startswith("## "):
                            break
                        source_block.append(nxt)
                    for match in _GLOSSARY_ID_RE.finditer("\n".join(source_block)):
                        tok = match.group(0)
                        if tok not in found_seeds:
                            found_seeds.append(tok)
                    break
            break
        return found_seeds

    seed_ids = extract_from_content(glossary_content)

    try:
        detail_path = (
            _discover_project_root() / "groundtruth-kb" / "docs" / "reference" / "canonical-terminology-detail.md"
        )
        if detail_path.exists():
            detail_content = detail_path.read_text(encoding="utf-8")
            detail_seeds = extract_from_content(detail_content)
            for tok in detail_seeds:
                if tok not in seed_ids:
                    seed_ids.append(tok)
    except Exception:  # noqa: BLE001 - graceful degradation
        pass

    return seed_ids


def _find_prior_deliberations_section(body_lines: list[str]) -> tuple[int, int] | None:
    """Locate the existing ``## Prior Deliberations`` section line range."""
    section_start = None
    for i, line in enumerate(body_lines):
        if line.strip() == _PRIOR_DELIBS_HEADING:
            section_start = i
            break
    if section_start is None:
        return None
    section_end = len(body_lines)
    for j in range(section_start + 1, len(body_lines)):
        if body_lines[j].startswith("## ") and not body_lines[j].startswith("### "):
            section_end = j
            break
    return (section_start, section_end)


def _format_helper_entry(
    token: str,
    *,
    source: str,
    db_record: dict[str, Any] | None = None,
) -> str:
    """Format one Markdown bullet for a pre-populated DA candidate."""
    if db_record is not None:
        title = (db_record.get("title") or "").strip()
        source_type = db_record.get("source_type") or ""
        if title:
            return f"- DA: `{token}` — seed={source}; {source_type}; {title[:80]}"
        return f"- DA: `{token}` — seed={source}; {source_type}"
    return f"- DA: `{token}` — seed={source}."


def _insert_prior_deliberations_block(body: str, block_text: str) -> str:
    """Insert ``block_text`` into the body's ``## Prior Deliberations`` section."""
    body_lines = body.splitlines(keepends=True)
    stripped_lines = [ln.rstrip("\n") for ln in body_lines]
    range_ = _find_prior_deliberations_section(stripped_lines)

    if range_ is None:
        suffix = "" if body.endswith("\n") else "\n"
        return body + suffix + "\n## Prior Deliberations\n\n" + block_text

    section_start, section_end = range_
    section_body_text = "".join(body_lines[section_start + 1 : section_end]).strip()

    if not section_body_text:
        insertion = "\n" + block_text + "\n"
        new_lines = body_lines[: section_start + 1] + [insertion] + body_lines[section_end:]
        return "".join(new_lines)

    insertion = "\n### Helper-suggested candidates\n\n" + block_text + "\n"
    new_lines = body_lines[:section_end] + [insertion] + body_lines[section_end:]
    return "".join(new_lines)


def pre_populate_prior_deliberations(
    topic_slug: str,
    body: str,
    *,
    db: Any | bool | None = None,
    glossary_path: Path | None = None,
    limit: int = DEFAULT_PRE_POPULATION_LIMIT,
    threshold: float = 0.0,
    log_path: Path | bool | None = None,
) -> str:
    """Pre-populate the ``## Prior Deliberations`` section of a bridge body."""
    if glossary_path is None:
        glossary_path = DEFAULT_GLOSSARY_PATH

    glossary_content = ""
    if isinstance(glossary_path, Path) and glossary_path.exists():
        try:
            glossary_content = glossary_path.read_text(encoding="utf-8")
        except OSError:
            glossary_content = ""
    seed_ids = _glossary_seed_ids_for_topic(topic_slug, glossary_content)

    # WI-4565: semantic search is opt-in. db=None (default) and db=False both
    # skip the ChromaDB default-store open (glossary-source seeding still runs);
    # db=True opts in to a timeout-bounded default-store search; any other value
    # is treated as a live KnowledgeDB instance.
    if db is False or db is None:
        active_db: Any | None = None
    elif db is True:
        active_db = _try_open_default_db()
    else:
        active_db = db

    search_results: list[dict[str, Any]] = []
    if active_db is not None:
        try:
            query = topic_slug.replace("-", " ")
            raw = active_db.search_deliberations(query, limit=limit) or []
            search_results = [r for r in raw if isinstance(r, dict)]
        except Exception:  # noqa: BLE001 - graceful degradation
            search_results = []

    seen: set[str] = set(seed_ids)
    search_records_to_add: list[dict[str, Any]] = []
    for r in search_results:
        rid = r.get("id")
        if isinstance(rid, str) and rid and rid not in seen:
            search_records_to_add.append(r)
            seen.add(rid)

    if log_path is None:
        log_path = DEFAULT_PREPOPULATION_LOG
    if log_path is not False and isinstance(log_path, Path):
        try:
            log_path.parent.mkdir(parents=True, exist_ok=True)
            log_path.write_text(
                json.dumps(
                    {
                        "timestamp": datetime.now(UTC).isoformat(),
                        "topic_slug": topic_slug,
                        "query": topic_slug.replace("-", " "),
                        "glossary_path": str(glossary_path),
                        "glossary_seed_ids": seed_ids,
                        "search_result_ids": [r.get("id", "") for r in search_records_to_add],
                        "semantic_search_attempted": active_db is not None,
                        "limit": limit,
                        "threshold": threshold,
                        "candidate_count": len(seed_ids) + len(search_records_to_add),
                    },
                    indent=2,
                    ensure_ascii=False,
                )
                + "\n",
                encoding="utf-8",
            )
        except OSError:
            pass

    if not seed_ids and not search_records_to_add:
        placeholder_block = NO_PRIOR_DELIBS_PLACEHOLDER + "\n"
        return _insert_prior_deliberations_block(body, placeholder_block)

    entries: list[str] = []
    for sid in seed_ids:
        entries.append(_format_helper_entry(sid, source="glossary"))
    for r in search_records_to_add:
        rid = r.get("id", "")
        entries.append(_format_helper_entry(rid, source="search", db_record=r))

    marker = "<!-- Pre-populated by helper; review and prune. -->"
    block_text = marker + "\n" + "\n".join(entries) + "\n"

    return _insert_prior_deliberations_block(body, block_text)


__all__ = [
    "DEFAULT_DB_PATH",
    "DEFAULT_GLOSSARY_PATH",
    "DEFAULT_PREPOPULATION_LOG",
    "DEFAULT_PRE_POPULATION_LIMIT",
    "NO_PRIOR_DELIBS_PLACEHOLDER",
    "_find_prior_deliberations_section",
    "_format_helper_entry",
    "_glossary_seed_ids_for_topic",
    "_insert_prior_deliberations_block",
    "_try_open_default_db",
    "pre_populate_prior_deliberations",
]
