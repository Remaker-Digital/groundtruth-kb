# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Helper for the /gtkb-bridge-propose skill.

Writes a bridge proposal file ``bridge/<topic>-001.md`` and inserts
its ``Document:`` / ``NEW:`` entry at the top of ``bridge/INDEX.md``
under governance-safe credential-scan and concurrency controls.

Design contract:

- Credential-only pre-flight scan (``CREDENTIAL_PATTERNS +
  BASH_EXTRAS``; PII explicitly excluded, same policy as the
  ``scanner-safe-writer`` hook). Callers never get a silent write
  when credential-shaped text is present.
- Two options on hit: **abort** or **redact**. Redact normalizes
  overlapping intervals before replacement, applies in reverse
  order, and re-scans the result. A non-empty second scan raises
  :class:`RedactionResidualError` (this is a bug, not a recoverable
  user state). **No Force option.**
- File-first write: the bridge file is persisted before the INDEX
  update. If the target file already exists,
  :class:`BridgeFileAlreadyExistsError` is raised before any INDEX
  touch.
- INDEX update is serialized through the bridge index lock and retry-safe. Total
  retry budget is **2 total attempts** (1 initial + 1 retry). On
  the second failure, :class:`BridgeIndexConflictError` surfaces
  with an actionable message.
- Idempotency detection uses an **exact-line match** against the
  stripped ``Document: <topic>`` line — substring matching would
  false-positive on slug prefixes.
"""

from __future__ import annotations

import importlib
import json
import os
import re
import sys
from collections.abc import Mapping
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Literal


def _discover_project_root() -> Path:
    for parent in Path(__file__).resolve().parents:
        if (parent / "scripts" / "bridge_author_metadata.py").is_file():
            return parent
    return Path(__file__).resolve().parents[4]


PROJECT_ROOT = _discover_project_root()
_GROUNDTRUTH_SRC = PROJECT_ROOT / "groundtruth-kb" / "src"
if _GROUNDTRUTH_SRC.is_dir() and str(_GROUNDTRUTH_SRC) not in sys.path:
    sys.path.insert(0, str(_GROUNDTRUTH_SRC))
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

_credential_patterns = importlib.import_module("groundtruth_kb.governance.credential_patterns")
BASH_EXTRAS = _credential_patterns.BASH_EXTRAS
CREDENTIAL_PATTERNS = _credential_patterns.CREDENTIAL_PATTERNS
ensure_author_metadata = importlib.import_module("scripts.bridge_author_metadata").ensure_author_metadata
atomic_index_update = importlib.import_module("scripts.bridge_index_writer").atomic_index_update


class BridgeFileAlreadyExistsError(RuntimeError):
    """Raised when ``bridge/<topic>-001.md`` exists on disk before phase 3.

    The skill never silently overwrites. Callers should pick a fresh
    slug (or a versioned suffix like ``-002`` for REVISED) and retry.
    """


class BridgeIndexConflictError(RuntimeError):
    """Raised when INDEX.md cannot be updated safely.

    Two conditions trigger this error:

    - Another writer inserted a ``Document: <topic>`` line between
      the skill's read and its rename step.
    - The INDEX content changed between the read and the rename
      (non-topic concurrent modification), and the retry budget is
      exhausted.

    In both cases the bridge file is still on disk; the caller must
    either manually add an INDEX entry or retry the skill.
    """


class RedactionResidualError(RuntimeError):
    """Raised when the post-redaction re-scan still finds hits.

    This indicates a catalog/redactor bug (for example, a newly
    added pattern that the redactor doesn't cover). It is not a
    recoverable user state — the caller cannot fix it by editing
    the body. The fix is in the redactor/catalog code.
    """


class CredentialHitsFoundError(RuntimeError):
    """Raised by ``handle_hits_abort_or_redact`` when ``mode='abort'``.

    The body contained credential-shaped text and the caller chose
    to abort rather than redact.
    """


class SpecificationLinksMissingError(RuntimeError):
    """Raised when a bridge proposal omits mandatory specification linkage."""


class BridgeWorkIntentError(RuntimeError):
    """Raised when bridge work-intent acquisition blocks a helper write."""


# Credential-only catalog. Iterates ``CREDENTIAL_PATTERNS + BASH_EXTRAS``
# directly — matching the scanner-safe-writer policy of excluding
# ``PII_PATTERNS`` (phone, email, ipv4) so operators can reference
# redacted samples without tripping a false-positive deny.
_SCAN_CATALOG: list[tuple[re.Pattern[str], str, str]] = [
    (spec.pattern, spec.name, spec.description) for spec in list(CREDENTIAL_PATTERNS) + list(BASH_EXTRAS)
]

WORK_INTENT_TTL_SECONDS = 300
# Session-id env-var membership is owned by scripts/gtkb_session_id.py
# (WI-4270 shared resolver unification; bridge/gtkb-session-id-shared-resolver-
# unification-003 GO at -004). Import the canonical bridge work-intent order;
# fail soft to a verbatim local copy so the helper never throws on a partial
# install. The drift-lock test platform_tests/scripts/test_gtkb_session_id.py +
# the bridge-propose work-intent test lock this fallback to the canonical
# BRIDGE_WORK_INTENT_ORDER.
try:
    from scripts.gtkb_session_id import BRIDGE_WORK_INTENT_ORDER as WORK_INTENT_SESSION_ENV_VARS
except Exception:  # pragma: no cover - helper fail-soft fallback for partial installs
    WORK_INTENT_SESSION_ENV_VARS = (
        "GTKB_BRIDGE_POLLER_RUN_ID",
        "CLAUDE_CODE_SESSION_ID",
        "CLAUDE_SESSION_ID",
        "GTKB_INHERITED_SESSION_ID",
        "CODEX_SESSION_ID",
        "CODEX_THREAD_ID",
        "ANTIGRAVITY_SESSION_ID",
        "GTKB_SESSION_ID",
    )


def resolve_work_intent_session_id(environ: Mapping[str, str] | None = None) -> str:
    """Resolve the current helper session id from supported env vars."""
    active_env = os.environ if environ is None else environ
    for name in WORK_INTENT_SESSION_ENV_VARS:
        value = active_env.get(name)
        if value and value.strip():
            return value.strip()
    expected = ", ".join(WORK_INTENT_SESSION_ENV_VARS)
    raise BridgeWorkIntentError(
        f"Bridge work-intent session id required before writing a bridge file. Set one of: {expected}."
    )


def _load_work_intent_registry(project_root: Path) -> Any:
    for scripts_dir in (project_root / "scripts", PROJECT_ROOT / "scripts"):
        if scripts_dir.is_dir() and str(scripts_dir) not in sys.path:
            sys.path.insert(0, str(scripts_dir))
    try:
        return importlib.import_module("bridge_work_intent_registry")
    except Exception as exc:  # noqa: BLE001 - raise helper-specific guidance
        raise BridgeWorkIntentError(
            "Bridge work-intent registry unavailable; expected scripts/bridge_work_intent_registry.py to be importable."
        ) from exc


def _acquire_bridge_work_intent(thread_slug: str, session_id: str, *, project_root: Path) -> Any:
    registry = _load_work_intent_registry(project_root)
    holder = registry.current_holder(thread_slug, project_root=project_root)
    holder_session = holder.get("session_id") if holder else None
    if holder_session and holder_session != session_id:
        expires = holder.get("ttl_expires_at", "unknown expiration")
        raise BridgeWorkIntentError(
            f"Bridge work-intent for thread {thread_slug!r} is held by session "
            f"{holder_session!r} until {expires}; current session {session_id!r} "
            "cannot write. Claim another thread or wait for the holder to release/expire."
        )
    if registry.acquire(
        thread_slug,
        session_id,
        ttl_seconds=WORK_INTENT_TTL_SECONDS,
        project_root=project_root,
    ):
        return registry
    holder = registry.current_holder(thread_slug, project_root=project_root)
    holder_session = holder.get("session_id") if holder else "unknown"
    expires = holder.get("ttl_expires_at", "unknown expiration") if holder else "unknown expiration"
    raise BridgeWorkIntentError(
        f"Bridge work-intent acquire failed for thread {thread_slug!r}; "
        f"current holder is {holder_session!r} until {expires}."
    )


def _release_bridge_work_intent(registry: Any, thread_slug: str, session_id: str, *, project_root: Path) -> None:
    registry.release(thread_slug, session_id, project_root=project_root)


# ---------------------------------------------------------------------------
# Phase 2 of GTKB-DA-READ-SURFACE-CORRECTION (template pre-population).
#
# `pre_populate_prior_deliberations` implements the placement-pattern target
# from `ADR-DA-READ-SURFACE-PLACEMENT-001` Path D for the bridge-template
# surface: when a bridge proposal is authored through this helper, the
# `## Prior Deliberations` section is pre-populated with relevant DA records
# so the cognitive operation flips from "remember to populate" (failure-prone)
# to "review and prune" (more reliable).
#
# Two-stage retrieval (per F2 resolution of phase-2 -004 NO-GO):
#
#   1. Glossary-source seeding (DETERMINISTIC). The canonical-terminology
#      glossary at `.claude/rules/canonical-terminology.md` is the
#      authoritative read surface for prior decisions per
#      `GOV-GLOSSARY-AS-DA-READ-SURFACE-001`. When the topic slug matches a
#      `### <heading>` in the glossary, the helper reads that heading's
#      `**Source:**` block and extracts DELIB/MemBase-spec IDs as seeds.
#
#   2. Semantic search (BROAD COVERAGE; OPTIONAL). When a KnowledgeDB
#      instance is provided, the helper queries
#      `search_deliberations(query, limit=...)` for additional candidates.
#      Failures are swallowed (graceful degradation).
# ---------------------------------------------------------------------------

_GLOSSARY_HEADING_RE = re.compile(r"^###\s+(.+?)\s*$")
_GLOSSARY_ID_RE = re.compile(r"\b(?:DELIB-[A-Z0-9-]+|(?:SPEC|GOV|ADR|DCL|PB|REQ)-[A-Z0-9-]+)\b")
_PRIOR_DELIBS_HEADING = "## Prior Deliberations"

DEFAULT_GLOSSARY_PATH = Path(".claude/rules/canonical-terminology.md")
DEFAULT_PREPOPULATION_LOG = Path(".gtkb-state/bridge-propose-helper/last-prepopulation.json")
DEFAULT_PRE_POPULATION_LIMIT = 5
DEFAULT_DB_PATH = "groundtruth.db"

NO_PRIOR_DELIBS_PLACEHOLDER = "_No prior deliberations: <fill in reason before filing>._"


def _try_open_default_db() -> Any | None:
    """Attempt to open the default ``KnowledgeDB`` for semantic search."""
    try:
        from groundtruth_kb.db import KnowledgeDB  # noqa: PLC0415

        return KnowledgeDB(DEFAULT_DB_PATH)
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
            # Matching heading found; locate Source: within 30 lines.
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

    # Also parse detail glossary if present in the workspace
    try:
        project_root = _discover_project_root()
        detail_path = project_root / "groundtruth-kb" / "docs" / "reference" / "canonical-terminology-detail.md"
        if detail_path.exists():
            detail_content = detail_path.read_text(encoding="utf-8")
            detail_seeds = extract_from_content(detail_content)
            for tok in detail_seeds:
                if tok not in seed_ids:
                    seed_ids.append(tok)
    except Exception:
        pass

    return seed_ids


def _find_prior_deliberations_section(body_lines: list[str]) -> tuple[int, int] | None:
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
    """Pre-populate the ``## Prior Deliberations`` section of a proposal body.

    Two-stage retrieval — glossary-source seeding (deterministic) then
    semantic search (broad coverage; default-on, auto-opens default
    ``KnowledgeDB``).

    Args:
        db: ``KnowledgeDB`` instance, ``None`` (default — auto-open the
            default ``KnowledgeDB("groundtruth.db")`` for semantic search;
            silent fallback to glossary-only if open fails), or ``False``
            (explicitly disable semantic search).

    When neither stage produces candidates, an
    ``_No prior deliberations: <fill in reason before filing>._``
    placeholder is inserted so the proposal does not fail the LO
    review-side check.
    """
    if glossary_path is None:
        glossary_path = DEFAULT_GLOSSARY_PATH

    glossary_content = ""
    if isinstance(glossary_path, Path) and glossary_path.exists():
        try:
            glossary_content = glossary_path.read_text(encoding="utf-8")
        except OSError:
            glossary_content = ""
    seed_ids = _glossary_seed_ids_for_topic(topic_slug, glossary_content)

    if db is False:
        active_db: Any | None = None
    elif db is None:
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
        # F2 fix: novel/no-match topics get the empty-justification placeholder
        # so the proposal does not fail the LO review-side check.
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


_SPEC_LINK_HEADING_RE = re.compile(
    r"^#{1,6}\s*(?:relevant\s+|linked\s+|governing\s+)?specification(?:\s+links?|\s+references?|\s*)$",
    re.IGNORECASE,
)
_SPEC_LINK_TOKEN_RE = re.compile(
    r"\b(?:SPEC|GOV|ADR|DCL|PB|REQ)-[A-Z0-9][A-Z0-9_.-]*\b"
    r"|(?:^|[`(\s])(?:\.claude/rules|groundtruth-kb/docs|docs|bridge)/[^\s`)]+",
    re.IGNORECASE | re.MULTILINE,
)
_SPEC_PLACEHOLDER_RE = re.compile(r"\b(?:tbd|todo|none|n/a|not applicable|no relevant)\b", re.IGNORECASE)


def _specification_links_section(body: str) -> str | None:
    """Return the body of the mandatory specification-link section, if present."""
    lines = body.splitlines()
    start: int | None = None
    for idx, line in enumerate(lines):
        if _SPEC_LINK_HEADING_RE.match(line.strip()):
            start = idx + 1
            break
    if start is None:
        return None

    section: list[str] = []
    for line in lines[start:]:
        stripped = line.strip()
        if stripped.startswith("#"):
            break
        section.append(line)
    return "\n".join(section).strip()


def validate_specification_links(body: str) -> None:
    """Require explicit links to the relevant governing specifications."""
    section = _specification_links_section(body)
    if section is None:
        raise SpecificationLinksMissingError(
            "Bridge implementation proposals must include a 'Specification Links' "
            "section citing every relevant governing specification."
        )
    if _SPEC_PLACEHOLDER_RE.search(section) or not _SPEC_LINK_TOKEN_RE.search(section):
        raise SpecificationLinksMissingError(
            "The 'Specification Links' section must contain concrete spec IDs "
            "or specification/rule file paths, not placeholders."
        )


def scan_credential_hits(content: str) -> list[dict[str, Any]]:
    """Return every credential-class hit in ``content``.

    Iterates :data:`_SCAN_CATALOG` (``CREDENTIAL_PATTERNS +
    BASH_EXTRAS``) and collects every non-overlapping regex match
    via ``finditer``. The list may contain overlapping hits when
    multiple specs match the same span (e.g., ``aws_key`` and
    ``bash_aws_key`` both match the same ``AKIA...`` literal). The
    overlap is resolved downstream by
    :func:`_normalize_hit_intervals`.

    Args:
        content: Text to scan.

    Returns:
        List of hit dictionaries, each with keys:

        - ``pattern_name`` (str) — the canonical PatternSpec name
        - ``pattern_description`` (str) — human-readable description
        - ``span`` (tuple[int, int]) — ``(start, end)`` offsets
    """
    hits: list[dict[str, Any]] = []
    for pattern, name, description in _SCAN_CATALOG:
        for match in pattern.finditer(content):
            hits.append(
                {
                    "pattern_name": name,
                    "pattern_description": description,
                    "span": (match.start(), match.end()),
                }
            )
    return hits


def _normalize_hit_intervals(hits: list[dict[str, Any]]) -> list[tuple[int, int, str]]:
    """Merge overlapping hits into non-overlapping ``(start, end, label)`` tuples.

    Sort order is ``(start, -end)`` so longer spans come first at
    the same start offset. Overlapping intervals are merged; the
    merged interval's label is the outermost (earliest-start) spec's
    ``pattern_name``. Duplicate spans (same start, same end) collapse
    to a single interval using the first spec's name as the label.

    Args:
        hits: Output of :func:`scan_credential_hits`.

    Returns:
        Non-overlapping ``(start, end, label)`` tuples, sorted by
        start ascending. Empty if ``hits`` is empty.
    """
    if not hits:
        return []
    # Sort by start ascending, then by -end (longer span first at the same start).
    sorted_hits = sorted(hits, key=lambda h: (h["span"][0], -h["span"][1]))
    merged: list[tuple[int, int, str]] = []
    for hit in sorted_hits:
        start, end = hit["span"]
        name = hit["pattern_name"]
        if merged and start < merged[-1][1]:
            # Overlaps with previous merged interval — extend end, keep outer label.
            prev_start, prev_end, prev_name = merged[-1]
            merged[-1] = (prev_start, max(prev_end, end), prev_name)
        else:
            merged.append((start, end, name))
    return merged


def redact_credential_hits(content: str, hits: list[dict[str, Any]]) -> str:
    """Replace credential hits with ``[REDACTED:<label>]`` placeholders.

    Handles overlapping canonical matches by normalizing hits into
    non-overlapping intervals first (outer-span-wins label), then
    applying replacements in reverse-start order so earlier offsets
    remain stable against later replacements.

    Args:
        content: Original text.
        hits: Output of :func:`scan_credential_hits`. May contain
            overlaps — they are resolved internally.

    Returns:
        Redacted text. Every character in ``content`` is replaced at
        most once.
    """
    intervals = _normalize_hit_intervals(hits)
    if not intervals:
        return content
    result = content
    # Apply in reverse-start order so indices before the replacement remain valid.
    for start, end, label in sorted(intervals, key=lambda iv: iv[0], reverse=True):
        result = result[:start] + f"[REDACTED:{label}]" + result[end:]
    return result


def handle_hits_abort_or_redact(
    body: str,
    hits: list[dict[str, Any]],
    *,
    mode: Literal["abort", "redact"],
) -> str:
    """Resolve credential hits per ``mode`` or raise.

    Args:
        body: Original body text.
        hits: Output of :func:`scan_credential_hits`.
        mode: ``"abort"`` raises :class:`CredentialHitsFoundError`;
            ``"redact"`` applies :func:`redact_credential_hits` then
            re-scans and raises :class:`RedactionResidualError` if
            the second scan is non-empty.

    Returns:
        The body to write. Either the original (when ``hits`` is
        empty) or the redacted version (when ``mode='redact'`` and
        the second scan is clean).
    """
    if not hits:
        return body
    if mode == "abort":
        first = hits[0]
        raise CredentialHitsFoundError(
            f"Credential-shaped content detected: "
            f"{first['pattern_name']} ({first['pattern_description']}). "
            f"Re-invoke with mode='redact' or edit the body."
        )
    if mode == "redact":
        redacted = redact_credential_hits(body, hits)
        residual = scan_credential_hits(redacted)
        if residual:
            first = residual[0]
            raise RedactionResidualError(
                f"Post-redaction re-scan still finds credential hits: "
                f"{first['pattern_name']} ({first['pattern_description']}). "
                f"This is a catalog/redactor bug, not a recoverable user state."
            )
        return redacted
    raise ValueError(f"Unknown mode {mode!r}; expected 'abort' or 'redact'.")


def _compute_new_index_content(existing_lines: list[str], new_entry: str) -> str:
    """Insert ``new_entry`` at the top of the INDEX body, after header comments.

    Header comment region is the contiguous prefix of lines that are
    blank, markdown headers (``#``), or HTML comments
    (``<!--``). Everything after that region is considered body.

    Args:
        existing_lines: Lines of the current INDEX.md (as returned by
            ``splitlines(keepends=True)``).
        new_entry: The full entry string to insert. Should end with a
            trailing newline.

    Returns:
        The new INDEX content as a single string.
    """
    # Find the boundary between the header/comment prefix and the body.
    insert_idx = 0
    in_comment = False
    for idx, line in enumerate(existing_lines):
        stripped = line.strip()
        # Track a multi-line HTML comment block.
        if in_comment:
            if "-->" in stripped:
                in_comment = False
            insert_idx = idx + 1
            continue
        if stripped.startswith("<!--"):
            # Single-line or start of a multi-line HTML comment.
            if "-->" not in stripped[4:]:
                in_comment = True
            insert_idx = idx + 1
            continue
        if not stripped or stripped.startswith("#") or stripped.startswith("|"):
            # Blank line, markdown header, or markdown table row (status legend) —
            # treat as header region.
            insert_idx = idx + 1
            continue
        # First real content line — stop. ``insert_idx`` points at it.
        break
    # Ensure the new_entry ends with a newline.
    entry = new_entry if new_entry.endswith("\n") else new_entry + "\n"
    # Ensure separation between the inserted entry and the existing line that follows.
    if insert_idx < len(existing_lines):
        following = existing_lines[insert_idx]
        if not entry.endswith("\n\n") and following.strip():
            entry = entry + "\n"
    head = "".join(existing_lines[:insert_idx])
    tail = "".join(existing_lines[insert_idx:])
    return head + entry + tail


def _index_writer_state_dir(index_path: Path) -> Path:
    return index_path.parent.parent / ".gtkb-state" / "bridge-index-writer"


def _update_bridge_index(
    index_path: Path,
    new_entry: str,
    *,
    topic_slug: str,
) -> None:
    """Insert ``new_entry`` at the top of ``index_path`` through the serialized writer.

    Steps:

    1. Acquire the bridge-index writer lock.
    2. Read the current text inside the lock.
    3. Idempotency check using **exact line match**: if any line,
       once stripped, equals ``"Document: <topic_slug>"`` exactly
       (NOT substring match), raise :class:`BridgeIndexConflictError`
       with a concurrent-same-topic message.
    4. Compute the new content via
       :func:`_compute_new_index_content`.
    5. Atomically replace the index through
       :func:`scripts.bridge_index_writer.atomic_index_update`.

    Args:
        index_path: Path to ``bridge/INDEX.md``.
        new_entry: The entry block to insert at the top.
        topic_slug: The topic slug (for idempotency detection).

    Raises:
        BridgeIndexConflictError: On concurrent same-topic insertion.
    """

    def mutate(current_text: str) -> str:
        lines = current_text.splitlines(keepends=True)
        expected = f"Document: {topic_slug}"
        for line in lines:
            if line.strip() == expected:
                raise BridgeIndexConflictError(
                    f"INDEX.md already has an entry for {expected!r}. "
                    f"Another writer inserted it concurrently. The bridge file "
                    f"at bridge/{topic_slug}-001.md is on disk; inspect and "
                    f"reconcile manually."
                )
        return _compute_new_index_content(lines, new_entry)

    atomic_index_update(index_path, mutate, state_dir=_index_writer_state_dir(index_path))


def propose_bridge(
    topic_slug: str,
    body: str,
    *,
    mode: Literal["abort", "redact"] = "abort",
    bridge_dir: Path | None = None,
    pre_populate_prior_deliberations: bool = True,
    db: Any | None = None,
    glossary_path: Path | None = None,
    pre_populate_log_path: Path | bool | None = None,
) -> Path:
    """Create ``bridge/<topic_slug>-001.md`` and insert an INDEX entry.

    Phase 0a — Prior Deliberations pre-population (default-on; Phase 2 of
    GTKB-DA-READ-SURFACE-CORRECTION): when
    ``pre_populate_prior_deliberations=True`` (default), call
    :func:`pre_populate_prior_deliberations` on ``body`` before scanning.
    Glossary-source seeding from ``.claude/rules/canonical-terminology.md``
    plus optional semantic search (when ``db`` is provided) populates the
    proposal's ``## Prior Deliberations`` section. Authors review and
    prune. Set ``pre_populate_prior_deliberations=False`` to opt out;
    opt-out callers must include a justification in the section
    (``_No prior deliberations: <reason>._``).

    Phase 0b - Specification linkage gate: require a ``Specification Links``
    section with concrete spec/rule links before any bridge file or INDEX
    mutation.

    Phase 1 — Pre-flight scan: iterate ``CREDENTIAL_PATTERNS +
    BASH_EXTRAS`` over ``body``. If hits are found, resolve per
    ``mode`` via :func:`handle_hits_abort_or_redact`.

    Phase 2 — File-first write: write ``bridge/<topic_slug>-001.md``
    atomically. If the file already exists,
    :class:`BridgeFileAlreadyExistsError` is raised before any INDEX
    touch.

    Phase 3 — INDEX insertion with retry: call
    :func:`_update_bridge_index`. On
    :class:`BridgeIndexConflictError`, retry once. **Total attempts:
    2 total** (1 initial + 1 retry). On the second failure, re-raise
    with an actionable message that mentions the bridge file on disk.

    Args:
        topic_slug: Kebab-case slug for the bridge document. The
            file becomes ``bridge/<topic_slug>-001.md`` and the
            INDEX entry begins with ``Document: <topic_slug>``.
        body: Proposal body text.
        mode: ``"abort"`` (default) or ``"redact"``. Controls the
            hit-resolution policy.
        bridge_dir: Parent bridge directory. Defaults to
            ``Path("bridge")``.
        pre_populate_prior_deliberations: Phase-0a pre-population flag
            (default ``True``). Set ``False`` to opt out.
        db: Optional ``KnowledgeDB`` instance for the semantic-search
            stage of pre-population.
        glossary_path: Override the glossary path used for seeding.
        pre_populate_log_path: Override the audit-log path. ``None``
            (default) writes to the default location; ``False`` disables
            logging.

    Returns:
        Absolute path to the created bridge file.

    Raises:
        SpecificationLinksMissingError: Mandatory specification linkage missing.
        CredentialHitsFoundError: ``mode='abort'`` and hits found.
        RedactionResidualError: Redaction failed the re-scan gate.
        BridgeFileAlreadyExistsError: Target file already on disk.
        BridgeIndexConflictError: INDEX could not be updated after
            2 total attempts.
    """
    bridge_root = bridge_dir if bridge_dir is not None else Path("bridge")
    project_root = bridge_root.parent.resolve()
    bridge_file = bridge_root / f"{topic_slug}-001.md"
    index_path = bridge_root / "INDEX.md"

    # Phase 0a: Prior Deliberations pre-population (default-on).
    if pre_populate_prior_deliberations:
        body = globals()["pre_populate_prior_deliberations"](
            topic_slug,
            body,
            db=db,
            glossary_path=glossary_path,
            log_path=pre_populate_log_path,
        )

    # Phase 0b: Implementation proposals must link relevant specifications.
    validate_specification_links(body)

    # Phase 1: Pre-flight scan.
    hits = scan_credential_hits(body)
    body_to_write = handle_hits_abort_or_redact(body, hits, mode=mode)
    body_to_write = ensure_author_metadata(body_to_write, project_root=bridge_root.parent)

    # Phase 2: File-first write (fail-fast on existing file; no silent overwrite).
    if bridge_file.exists():
        raise BridgeFileAlreadyExistsError(
            f"{bridge_file} already exists — pick a fresh slug or bump to "
            f"-002 for a REVISED version. The skill never silently overwrites."
        )
    session_id = resolve_work_intent_session_id()
    work_intent_registry = _acquire_bridge_work_intent(topic_slug, session_id, project_root=project_root)
    bridge_file.parent.mkdir(parents=True, exist_ok=True)
    bridge_file.write_bytes(body_to_write.encode("utf-8"))

    # Phase 3: INDEX insertion with retry.
    # Retry budget: 2 total attempts (1 initial + 1 retry). Both the comment,
    # the final exception message, and the test coverage use the "2 total"
    # phrasing — keep them in sync.
    new_entry = f"Document: {topic_slug}\nNEW: bridge/{topic_slug}-001.md\n"
    last_error: BridgeIndexConflictError | None = None
    max_attempts = 2  # 2 total attempts — 1 initial + 1 retry.
    for attempt in range(1, max_attempts + 1):
        try:
            _update_bridge_index(index_path, new_entry, topic_slug=topic_slug)
            _release_bridge_work_intent(work_intent_registry, topic_slug, session_id, project_root=project_root)
            return bridge_file
        except BridgeIndexConflictError as exc:
            last_error = exc
            if attempt >= max_attempts:
                break
            # else: loop and retry the INDEX-layer update only.
    # Exhausted 2 total attempts — re-raise with an actionable message.
    raise BridgeIndexConflictError(
        f"Bridge file {bridge_file} was written but INDEX.md could not be "
        f"updated after 2 total attempts. The file exists on disk; manually "
        f"add an entry to bridge/INDEX.md or retry the skill. "
        f"Last error: {last_error}"
    )


__all__ = [
    "BridgeFileAlreadyExistsError",
    "BridgeIndexConflictError",
    "BridgeWorkIntentError",
    "CredentialHitsFoundError",
    "DEFAULT_GLOSSARY_PATH",
    "DEFAULT_PREPOPULATION_LOG",
    "DEFAULT_PRE_POPULATION_LIMIT",
    "RedactionResidualError",
    "SpecificationLinksMissingError",
    "WORK_INTENT_SESSION_ENV_VARS",
    "WORK_INTENT_TTL_SECONDS",
    "handle_hits_abort_or_redact",
    "pre_populate_prior_deliberations",
    "propose_bridge",
    "redact_credential_hits",
    "resolve_work_intent_session_id",
    "scan_credential_hits",
    "validate_specification_links",
]
