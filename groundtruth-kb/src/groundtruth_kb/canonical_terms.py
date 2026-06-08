"""Canonical Terminology System backing registry (Phase 1).

Per `bridge/gtkb-canonical-terminology-system-context-model-001-005.md`
(Codex GO at `-006`):

- Markdown/TOML at ``.claude/rules/canonical-terminology.md`` and
  ``.claude/rules/canonical-terminology.toml`` remain the startup-readable
  authority for fresh agents and scaffold templates. Phase 1 does NOT change
  what fresh agents read at startup.
- This module provides a structured backing registry over MemBase's
  ``canonical_terms`` table. Tools (collision detection, parity checks,
  future retrieval surfaces) query the table; the markdown stays canonical.
- Collision detection uses a unified text-surface key model (per Codex
  ``-004`` F1 + ``-005`` revision): all lexical surfaces (canonical_term,
  accepted_synonyms, discouraged_synonyms, forbidden_uses) share a single
  ``("text", normalized_value)`` key namespace so cross-field text reuse
  is detected. Field-of-origin metadata is preserved separately for the
  classifier.
- Phase 2/3/4 (Agent Operating Context, Bounded Knowledge Principle,
  junior-developer documentation) are out-of-scope for this module.

Copyright (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC.
All rights reserved.
"""

from __future__ import annotations

import hashlib
import json
import re
import sqlite3
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from groundtruth_kb.db import KnowledgeDB

# ---------------------------------------------------------------------------
# Schema
# ---------------------------------------------------------------------------

SCHEMA_DDL = """\
CREATE TABLE IF NOT EXISTS canonical_terms (
    rowid INTEGER PRIMARY KEY AUTOINCREMENT,
    id TEXT NOT NULL,
    version INTEGER NOT NULL,
    canonical_term TEXT NOT NULL,
    definition TEXT NOT NULL,
    authority_level TEXT NOT NULL CHECK (authority_level IN ('platform_core', 'adopter_extension', 'project_local')),
    scope TEXT NOT NULL,
    accepted_synonyms TEXT,
    discouraged_synonyms TEXT,
    linked_artifacts TEXT,
    linked_services TEXT,
    usage_examples TEXT,
    forbidden_uses TEXT,
    lifecycle_status TEXT NOT NULL CHECK (lifecycle_status IN ('candidate', 'active', 'deprecated', 'retired')),
    source_authority TEXT NOT NULL,
    changed_by TEXT NOT NULL,
    changed_at TEXT NOT NULL,
    change_reason TEXT NOT NULL,
    UNIQUE(id, version)
)\
"""

VALID_AUTHORITY_LEVELS = ("platform_core", "adopter_extension", "project_local")
VALID_LIFECYCLE_STATUSES = ("candidate", "active", "deprecated", "retired")
LEXICAL_FIELDS = ("canonical_term", "accepted_synonym", "discouraged_synonym", "forbidden_use")
JSON_LIST_COLUMNS = (
    "accepted_synonyms",
    "discouraged_synonyms",
    "linked_artifacts",
    "linked_services",
    "usage_examples",
    "forbidden_uses",
)


# ---------------------------------------------------------------------------
# Errors
# ---------------------------------------------------------------------------


class CanonicalTermError(Exception):
    """Base error for canonical_terms operations."""


class CanonicalTermValidationError(CanonicalTermError, ValueError):
    """Raised when input fails validation before insertion."""


# ---------------------------------------------------------------------------
# Helpers: connection, time, JSON encoding
# ---------------------------------------------------------------------------


def _conn(db_or_conn: KnowledgeDB | sqlite3.Connection) -> sqlite3.Connection:
    """Resolve a sqlite3.Connection from either a KnowledgeDB or raw connection."""
    if isinstance(db_or_conn, sqlite3.Connection):
        return db_or_conn
    # KnowledgeDB exposes a private _get_conn(); we use it because the public
    # surface is itself implemented on top of the same connection. Any future
    # KnowledgeDB-public accessor can be substituted without changing callers
    # of this module.
    return db_or_conn._get_conn()


def _now_iso() -> str:
    return datetime.now(UTC).isoformat(timespec="seconds")


def _encode_list(value: list[str] | None) -> str | None:
    if value is None:
        return None
    return json.dumps(list(value), ensure_ascii=False)


def _decode_list(value: str | None) -> list[str]:
    if value is None or value == "":
        return []
    try:
        decoded = json.loads(value)
    except (json.JSONDecodeError, TypeError):
        return []
    return [str(x) for x in decoded] if isinstance(decoded, list) else []


def _row_to_term(row: sqlite3.Row | tuple[Any, ...] | None) -> dict[str, Any] | None:
    if row is None:
        return None
    if isinstance(row, sqlite3.Row):
        d = dict(row)
    else:
        # Caller passed a raw tuple; we cannot decode without column info.
        # All public APIs in this module use sqlite3.Row, so this path is a
        # safety fallback.
        return None
    for col in JSON_LIST_COLUMNS:
        if col in d:
            d[col] = _decode_list(d[col])
    return d


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------


def _validate_authority_level(value: str) -> None:
    if value not in VALID_AUTHORITY_LEVELS:
        raise CanonicalTermValidationError(f"authority_level must be one of {VALID_AUTHORITY_LEVELS}, got {value!r}")


def _validate_lifecycle_status(value: str) -> None:
    if value not in VALID_LIFECYCLE_STATUSES:
        raise CanonicalTermValidationError(f"lifecycle_status must be one of {VALID_LIFECYCLE_STATUSES}, got {value!r}")


def _validate_required_str(name: str, value: Any) -> None:
    if not isinstance(value, str) or not value.strip():
        raise CanonicalTermValidationError(f"{name} is required and must be a non-empty string")


# ---------------------------------------------------------------------------
# Insert / get / list
# ---------------------------------------------------------------------------


def insert_term(
    db_or_conn: KnowledgeDB | sqlite3.Connection,
    *,
    id: str,
    canonical_term: str,
    definition: str,
    authority_level: str,
    scope: str,
    source_authority: str,
    changed_by: str,
    change_reason: str,
    accepted_synonyms: list[str] | None = None,
    discouraged_synonyms: list[str] | None = None,
    linked_artifacts: list[str] | None = None,
    linked_services: list[str] | None = None,
    usage_examples: list[str] | None = None,
    forbidden_uses: list[str] | None = None,
    lifecycle_status: str = "active",
    changed_at: str | None = None,
) -> dict[str, Any]:
    """Append a new version of a canonical term.

    Versioning is monotonic per ``id``; the first insert is version 1, and
    each subsequent ``insert_term`` for the same ``id`` appends a new version
    one greater than the current maximum. Schema constraints enforce
    ``UNIQUE(id, version)`` so two callers cannot append the same version
    concurrently.
    """
    _validate_required_str("id", id)
    _validate_required_str("canonical_term", canonical_term)
    _validate_required_str("definition", definition)
    _validate_required_str("scope", scope)
    _validate_required_str("source_authority", source_authority)
    _validate_required_str("changed_by", changed_by)
    _validate_required_str("change_reason", change_reason)
    _validate_authority_level(authority_level)
    _validate_lifecycle_status(lifecycle_status)

    conn = _conn(db_or_conn)
    cur = conn.execute("SELECT COALESCE(MAX(version), 0) FROM canonical_terms WHERE id = ?", (id,))
    current_max = cur.fetchone()[0]
    next_version = int(current_max) + 1

    conn.execute(
        """
        INSERT INTO canonical_terms (
            id, version, canonical_term, definition, authority_level, scope,
            accepted_synonyms, discouraged_synonyms, linked_artifacts,
            linked_services, usage_examples, forbidden_uses,
            lifecycle_status, source_authority,
            changed_by, changed_at, change_reason
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            id,
            next_version,
            canonical_term,
            definition,
            authority_level,
            scope,
            _encode_list(accepted_synonyms),
            _encode_list(discouraged_synonyms),
            _encode_list(linked_artifacts),
            _encode_list(linked_services),
            _encode_list(usage_examples),
            _encode_list(forbidden_uses),
            lifecycle_status,
            source_authority,
            changed_by,
            changed_at or _now_iso(),
            change_reason,
        ),
    )
    conn.commit()
    return _get_by_id_and_version(conn, id, next_version)  # type: ignore[return-value]


def _get_by_id_and_version(conn: sqlite3.Connection, id: str, version: int) -> dict[str, Any] | None:
    conn.row_factory = sqlite3.Row
    row = conn.execute("SELECT * FROM canonical_terms WHERE id = ? AND version = ?", (id, version)).fetchone()
    return _row_to_term(row)


def get_term(db_or_conn: KnowledgeDB | sqlite3.Connection, id: str) -> dict[str, Any] | None:
    """Return the latest version of the term with the given id, or None."""
    conn = _conn(db_or_conn)
    conn.row_factory = sqlite3.Row
    row = conn.execute("SELECT * FROM current_canonical_terms WHERE id = ?", (id,)).fetchone()
    return _row_to_term(row)


def list_versions(db_or_conn: KnowledgeDB | sqlite3.Connection, id: str) -> list[dict[str, Any]]:
    """Return all versions of the term with the given id, oldest first."""
    conn = _conn(db_or_conn)
    conn.row_factory = sqlite3.Row
    rows = conn.execute("SELECT * FROM canonical_terms WHERE id = ? ORDER BY version ASC", (id,)).fetchall()
    return [t for r in rows if (t := _row_to_term(r)) is not None]


def list_terms(
    db_or_conn: KnowledgeDB | sqlite3.Connection,
    *,
    authority_level: str | None = None,
    scope: str | None = None,
    include_retired: bool = False,
) -> list[dict[str, Any]]:
    """Return current-state terms (latest version per id), optionally filtered."""
    conn = _conn(db_or_conn)
    conn.row_factory = sqlite3.Row
    sql = "SELECT * FROM current_canonical_terms WHERE 1=1"
    params: list[Any] = []
    if authority_level is not None:
        _validate_authority_level(authority_level)
        sql += " AND authority_level = ?"
        params.append(authority_level)
    if scope is not None:
        sql += " AND scope = ?"
        params.append(scope)
    if not include_retired:
        sql += " AND lifecycle_status != 'retired'"
    sql += " ORDER BY id ASC"
    rows = conn.execute(sql, params).fetchall()
    return [t for r in rows if (t := _row_to_term(r)) is not None]


# ---------------------------------------------------------------------------
# Collision detection (unified text-surface key model)
# ---------------------------------------------------------------------------


def _normalize(value: str) -> str:
    return value.strip().lower()


def _normalized_text_keys(term: dict[str, Any]) -> set[tuple[str, str]]:
    """Return the set of (kind, normalized_text) keys for the term.

    Structural identifier (``id``) stays in its own namespace because it
    identifies the term as a row, not its surface text.

    Lexical surfaces (``canonical_term``, ``accepted_synonyms``,
    ``discouraged_synonyms``, ``forbidden_uses``) all share the
    ``("text", value)`` namespace so cross-field text reuse is detected.
    Field-of-origin metadata is exposed via ``_text_surface_origin`` so
    classifiers can label collisions after detection.
    """
    keys: set[tuple[str, str]] = set()
    term_id = term.get("id")
    if isinstance(term_id, str) and term_id.strip():
        keys.add(("id", _normalize(term_id)))
    term_display = term.get("canonical_term")
    if isinstance(term_display, str) and term_display.strip():
        keys.add(("text", _normalize(term_display)))
    for syn in term.get("accepted_synonyms") or []:
        if isinstance(syn, str) and syn.strip():
            keys.add(("text", _normalize(syn)))
    for dsyn in term.get("discouraged_synonyms") or []:
        if isinstance(dsyn, str) and dsyn.strip():
            keys.add(("text", _normalize(dsyn)))
    for fuse in term.get("forbidden_uses") or []:
        if isinstance(fuse, str) and fuse.strip():
            keys.add(("text", _normalize(fuse)))
    return keys


def _text_surface_origin(term: dict[str, Any]) -> dict[str, list[tuple[str, str]]]:
    """Return {normalized_text: [(field, raw_value), ...]} for the term's
    lexical surfaces. Used by the collision classifier to label cross-field
    text reuse.
    """
    origins: dict[str, list[tuple[str, str]]] = defaultdict(list)
    term_display = term.get("canonical_term")
    if isinstance(term_display, str) and term_display.strip():
        origins[_normalize(term_display)].append(("canonical_term", term_display))
    for syn in term.get("accepted_synonyms") or []:
        if isinstance(syn, str) and syn.strip():
            origins[_normalize(syn)].append(("accepted_synonym", syn))
    for dsyn in term.get("discouraged_synonyms") or []:
        if isinstance(dsyn, str) and dsyn.strip():
            origins[_normalize(dsyn)].append(("discouraged_synonym", dsyn))
    for fuse in term.get("forbidden_uses") or []:
        if isinstance(fuse, str) and fuse.strip():
            origins[_normalize(fuse)].append(("forbidden_use", fuse))
    return dict(origins)


@dataclass
class CollisionFinding:
    """A single collision between two or more terms.

    ``key`` is the normalized lookup key the detector grouped on.
    ``classification`` is one of:

    - ``platform_core_redefinition`` — at least one ``platform_core`` term
      and at least one non-``platform_core`` term share a key. ERROR.
    - ``cross_scope_overlap`` — terms in different scopes share a key
      (excludes the platform_core_redefinition case which is reported
      separately as ERROR). WARN.
    - ``cross_field_text_reuse`` — same-scope lexical surfaces in different
      fields share text (e.g., A.accepted_synonym matches B.discouraged_synonym).
      WARN.

    ``instances`` carries the colliding terms; ``origin_pairs`` carries
    per-instance ``[(field, raw_value), ...]`` metadata (only populated for
    ``("text", ...)`` keys).
    """

    key: tuple[str, str]
    classification: str
    instances: list[dict[str, Any]]
    origin_pairs: list[tuple[str, list[tuple[str, str]]]] = field(default_factory=list)


def find_collisions(
    terms: list[dict[str, Any]],
) -> tuple[list[CollisionFinding], list[CollisionFinding]]:
    """Detect collisions across ``terms`` using the unified text-surface key.

    Returns ``(errors, warnings)``. Errors are platform_core redefinitions;
    warnings cover cross-scope overlap and cross-field text reuse.
    """
    by_key: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    origins_by_term: dict[str, dict[str, list[tuple[str, str]]]] = {}
    for term in terms:
        term_id = term.get("id")
        if isinstance(term_id, str):
            origins_by_term[term_id] = _text_surface_origin(term)
        for key in _normalized_text_keys(term):
            by_key[key].append(term)

    errors: list[CollisionFinding] = []
    warnings: list[CollisionFinding] = []

    for key, instances in by_key.items():
        if len(instances) < 2:
            continue
        kind, value = key
        levels = {t.get("authority_level") for t in instances}
        scopes = {t.get("scope") for t in instances}

        if kind == "text":
            origin_pairs = [
                (str(t.get("id")), origins_by_term.get(str(t.get("id")), {}).get(value, [])) for t in instances
            ]
        else:
            origin_pairs = [(str(t.get("id")), [("id", str(t.get("id")))]) for t in instances]

        if "platform_core" in levels and len(levels) > 1:
            errors.append(
                CollisionFinding(
                    key=key,
                    classification="platform_core_redefinition",
                    instances=instances,
                    origin_pairs=origin_pairs,
                )
            )
            continue
        if len(scopes) > 1:
            warnings.append(
                CollisionFinding(
                    key=key,
                    classification="cross_scope_overlap",
                    instances=instances,
                    origin_pairs=origin_pairs,
                )
            )
            continue
        if kind == "text":
            field_kinds_per_instance = [{f for (f, _) in pair[1]} for pair in origin_pairs]
            if field_kinds_per_instance and len(set().union(*field_kinds_per_instance)) > 1:
                warnings.append(
                    CollisionFinding(
                        key=key,
                        classification="cross_field_text_reuse",
                        instances=instances,
                        origin_pairs=origin_pairs,
                    )
                )

    return errors, warnings


# ---------------------------------------------------------------------------
# Markdown parsing + parity check
# ---------------------------------------------------------------------------

# Match `### TermName` headings. The term name is the rest of the line.
_HEADING_RE = re.compile(r"^###\s+(.+?)\s*$", re.MULTILINE)


def parse_markdown_glossary(markdown_text: str) -> list[dict[str, str]]:
    """Parse ``.claude/rules/canonical-terminology.md`` into a list of term
    dicts. Each dict has ``id`` (slug-form, uppercase), ``canonical_term``
    (display form), and ``definition`` (the prose immediately following the
    heading until the next ``### `` heading or the end of the section).

    Only headings under ``## Canonical Terms`` and ``## GT-KB Platform &
    Lifecycle Terms`` sections are included; sub-headings under a different
    ``##`` section (e.g., ``## Alias / Canonical Disposition``) are ignored.
    """
    # Locate the relevant ## sections by scanning the structure.
    lines = markdown_text.splitlines()
    relevant_section_re = re.compile(
        r"^##\s+(Canonical Terms|GT-KB Platform & Lifecycle Terms|Project-specific Terminology)",
        re.IGNORECASE,
    )
    in_relevant = False
    block_lines: list[str] = []
    for ln in lines:
        if ln.startswith("## "):
            in_relevant = bool(relevant_section_re.match(ln))
            continue
        if in_relevant:
            block_lines.append(ln)
    block_text = "\n".join(block_lines)

    terms: list[dict[str, str]] = []
    seen_slugs: dict[str, int] = {}
    matches = list(_HEADING_RE.finditer(block_text))
    for i, m in enumerate(matches):
        display = m.group(1).strip()
        # Skip subheading-only items like "Artifact Types" / "Concepts (not tables)".
        # Heuristic: a real term heading is followed by a "**Definition:**"
        # (or "**Definition" word boundary) within the next ~30 lines.
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(block_text)
        body = block_text[start:end]
        definition = _extract_definition(body)
        if not definition:
            # No definition prose found — likely a sub-heading or marker.
            continue
        base_slug = _slugify(display)
        if not base_slug:
            continue
        # Stable de-duplication: when two distinct headings slugify to the
        # same id (e.g., "GroundTruth KB" and "GroundTruth-KB"), suffix
        # later occurrences with `_2`, `_3`, ... so each markdown entry
        # has a stable unique id across runs.
        seen_slugs[base_slug] = seen_slugs.get(base_slug, 0) + 1
        slug = base_slug if seen_slugs[base_slug] == 1 else f"{base_slug}_{seen_slugs[base_slug]}"
        terms.append({"id": slug, "canonical_term": display, "definition": definition})
    return terms


def _slugify(display: str) -> str:
    """Convert a display name to a stable slug ID.

    Rules:
    - Replace whitespace, ``/``, and ``-`` with ``_`` (so "GT-KB" and "GTKB"
      do not collide).
    - Drop non-alphanumeric/underscore characters.
    - Uppercase.
    - Collapse repeated underscores.
    """
    s = re.sub(r"[\s/\-]+", "_", display.strip())
    s = re.sub(r"[^A-Za-z0-9_]+", "", s)
    s = re.sub(r"_+", "_", s).strip("_")
    return s.upper()


_DEFINITION_RE = re.compile(
    r"\*\*Definition[:.]?\*\*\s*(.*?)(?=\n\*\*[A-Za-z][^*]*?:?\*\*|\Z)",
    re.DOTALL | re.IGNORECASE,
)


def _extract_definition(body: str) -> str:
    m = _DEFINITION_RE.search(body)
    if not m:
        return ""
    text = m.group(1).strip()
    # Collapse consecutive whitespace within a paragraph but preserve
    # paragraph breaks marked by blank lines.
    paragraphs = [re.sub(r"\s+", " ", p).strip() for p in re.split(r"\n\s*\n", text)]
    return "\n\n".join(p for p in paragraphs if p)


def _markdown_hash(markdown_text: str) -> str:
    return "sha256:" + hashlib.sha256(markdown_text.encode("utf-8")).hexdigest()


# ---------------------------------------------------------------------------
# Seed
# ---------------------------------------------------------------------------


@dataclass
class SeedOperation:
    """A single seed-time operation: insert, update, retire, or unchanged."""

    op: str  # "insert" | "update" | "retire" | "unchanged"
    id: str
    canonical_term: str
    reason: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "op": self.op,
            "id": self.id,
            "canonical_term": self.canonical_term,
            "reason": self.reason,
        }


@dataclass
class SeedPlan:
    """Plan of seed operations for a given markdown source."""

    source_path: str
    source_hash: str
    operations: list[SeedOperation] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "source_path": self.source_path,
            "source_hash": self.source_hash,
            "operations": [o.to_dict() for o in self.operations],
            "summary": self.summary(),
        }

    def summary(self) -> dict[str, int]:
        s: dict[str, int] = defaultdict(int)
        for o in self.operations:
            s[o.op] += 1
        return dict(s)


def seed_from_markdown(
    db_or_conn: KnowledgeDB | sqlite3.Connection,
    markdown_path: Path,
    *,
    dry_run: bool = True,
    changed_by: str = "canonical-terms-seed",
) -> SeedPlan:
    """Seed (or plan to seed) ``canonical_terms`` from a markdown glossary.

    The markdown is treated as the canonical source. Each ``### TermName``
    heading under ``## Canonical Terms`` or ``## GT-KB Platform & Lifecycle
    Terms`` becomes a ``platform_core`` term at scope ``platform``.

    Operations:
    - ``insert``: term is in markdown but not in the table.
    - ``update``: term is in both, but the table's current version differs
      (by canonical_term or definition). Append a new version.
    - ``unchanged``: term is in both with matching content.
    - ``retire``: term is in the table at ``platform_core`` scope but no
      longer in the markdown. Append a new version with
      ``lifecycle_status='retired'``.

    Idempotent: a second run against an unchanged markdown produces all
    ``unchanged`` operations.
    """
    text = markdown_path.read_text(encoding="utf-8")
    src_hash = _markdown_hash(text)
    source_authority = f"{markdown_path.as_posix()}+{src_hash}"
    parsed = parse_markdown_glossary(text)
    parsed_by_id = {t["id"]: t for t in parsed}

    conn = _conn(db_or_conn)
    # Include retired rows so revivals are detected as updates rather than
    # silent re-inserts (which would fail the UNIQUE(id, version) ratchet
    # because list_versions still grows monotonically).
    existing_platform = list_terms(conn, authority_level="platform_core", scope="platform", include_retired=True)
    existing_by_id = {t["id"]: t for t in existing_platform}

    plan = SeedPlan(source_path=markdown_path.as_posix(), source_hash=src_hash)

    for term in parsed:
        existing = existing_by_id.get(term["id"])
        if existing is None:
            plan.operations.append(
                SeedOperation(
                    op="insert",
                    id=term["id"],
                    canonical_term=term["canonical_term"],
                    reason=f"new platform_core term from {markdown_path.name}",
                )
            )
        elif (
            existing.get("canonical_term") != term["canonical_term"]
            or existing.get("definition") != term["definition"]
            or existing.get("lifecycle_status") == "retired"
        ):
            plan.operations.append(
                SeedOperation(
                    op="update",
                    id=term["id"],
                    canonical_term=term["canonical_term"],
                    reason=f"content changed from {markdown_path.name} (or revival from retired)",
                )
            )
        else:
            plan.operations.append(
                SeedOperation(
                    op="unchanged",
                    id=term["id"],
                    canonical_term=term["canonical_term"],
                    reason="matches markdown source",
                )
            )

    for term_id, existing in existing_by_id.items():
        if term_id in parsed_by_id:
            continue
        if existing.get("lifecycle_status") == "retired":
            continue  # already retired; no double-retire op
        plan.operations.append(
            SeedOperation(
                op="retire",
                id=term_id,
                canonical_term=existing.get("canonical_term", ""),
                reason=f"no longer in {markdown_path.name}",
            )
        )

    if dry_run:
        return plan

    # Apply mutations.
    for op in plan.operations:
        if op.op == "insert":
            term = parsed_by_id[op.id]
            insert_term(
                conn,
                id=op.id,
                canonical_term=term["canonical_term"],
                definition=term["definition"],
                authority_level="platform_core",
                scope="platform",
                source_authority=source_authority,
                changed_by=changed_by,
                change_reason=f"seed from {src_hash}",
                lifecycle_status="active",
            )
        elif op.op == "update":
            term = parsed_by_id[op.id]
            insert_term(
                conn,
                id=op.id,
                canonical_term=term["canonical_term"],
                definition=term["definition"],
                authority_level="platform_core",
                scope="platform",
                source_authority=source_authority,
                changed_by=changed_by,
                change_reason=f"update from {src_hash}",
                lifecycle_status="active",
            )
        elif op.op == "retire":
            existing = existing_by_id[op.id]
            insert_term(
                conn,
                id=op.id,
                canonical_term=existing.get("canonical_term", ""),
                definition=existing.get("definition", ""),
                authority_level="platform_core",
                scope="platform",
                source_authority=source_authority,
                changed_by=changed_by,
                change_reason=f"retired: not in {markdown_path.name} at {src_hash}",
                lifecycle_status="retired",
            )
        # "unchanged" is a no-op.

    return plan


# ---------------------------------------------------------------------------
# Parity check (markdown ↔ table)
# ---------------------------------------------------------------------------


@dataclass
class ParityFinding:
    """Markdown ↔ table parity gap."""

    severity: str  # "error" | "warning"
    kind: str  # "missing_in_table" | "missing_in_markdown" | "content_drift"
    id: str
    detail: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "severity": self.severity,
            "kind": self.kind,
            "id": self.id,
            "detail": self.detail,
        }


def parity_check(
    db_or_conn: KnowledgeDB | sqlite3.Connection,
    markdown_path: Path,
) -> list[ParityFinding]:
    """Compare ``platform_core`` rows in the table to ``markdown_path``.

    Returns a list of findings:

    - ERROR ``missing_in_markdown``: a ``platform_core`` term exists in the
      table but is not in the markdown. (Suggests the seed was applied at
      a different markdown content; or the markdown was edited and the
      seed has not been re-run yet.)
    - WARNING ``missing_in_table``: a markdown term has not been seeded
      yet. Run ``seed_from_markdown(..., dry_run=False)``.
    - WARNING ``content_drift``: term exists in both but display or
      definition differs.

    A passing parity check has no findings.
    """
    text = markdown_path.read_text(encoding="utf-8")
    parsed_by_id = {t["id"]: t for t in parse_markdown_glossary(text)}
    existing = list_terms(db_or_conn, authority_level="platform_core", scope="platform")
    existing_by_id = {t["id"]: t for t in existing}

    findings: list[ParityFinding] = []
    for term_id, term in parsed_by_id.items():
        existing_term = existing_by_id.get(term_id)
        if existing_term is None:
            findings.append(
                ParityFinding(
                    severity="warning",
                    kind="missing_in_table",
                    id=term_id,
                    detail=f"markdown term {term['canonical_term']!r} not yet seeded",
                )
            )
        else:
            if existing_term.get("canonical_term") != term["canonical_term"]:
                findings.append(
                    ParityFinding(
                        severity="warning",
                        kind="content_drift",
                        id=term_id,
                        detail=(
                            f"display drift: markdown={term['canonical_term']!r} "
                            f"table={existing_term.get('canonical_term')!r}"
                        ),
                    )
                )
            if existing_term.get("definition") != term["definition"]:
                findings.append(
                    ParityFinding(
                        severity="warning",
                        kind="content_drift",
                        id=term_id,
                        detail="definition drift between markdown and table",
                    )
                )

    for term_id in existing_by_id:
        if term_id not in parsed_by_id:
            existing_term = existing_by_id[term_id]
            if existing_term.get("lifecycle_status") == "retired":
                continue
            findings.append(
                ParityFinding(
                    severity="error",
                    kind="missing_in_markdown",
                    id=term_id,
                    detail=(
                        f"platform_core term {existing_term.get('canonical_term')!r} "
                        f"in table but not in {markdown_path.name}"
                    ),
                )
            )

    return findings
