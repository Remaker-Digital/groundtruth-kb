"""
GroundTruth KB deterministic handoff-prompt service.

Implements ``SPEC-HANDOFF-PROMPT-DETERMINISTIC-SERVICE-001`` (MemBase rowid
8562). The service generates a bounded, action-oriented handoff prompt that
the next GroundTruth-KB session reads to inherit the closing session's open
state. Output is byte-stable for identical canonical inputs and contains no
AI-mediated content.

Inputs (per spec § Inputs):

1. The latest archived session-envelope JSON at
   ``harness-state/<harness_name>/session-envelope-archive/<closed_at-ISO>-session-envelope.json``.
2. Open bridge state filtered for the active role: the latest NEW / REVISED /
   GO / NO-GO line per Document in ``bridge/INDEX.md``.

Outputs (per spec § Output Surfaces):

1. A new MemBase ``session_prompts`` row keyed by ``session_id`` plus a
   deterministic idempotency key carried in the row's ``context`` JSON field.
2. A markdown file at ``.claude/session/handoff-<session-id>.md``.
3. Terminal echo (performed by the CLI wrapper, not this module).

Copyright (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
Licensed under AGPL-3.0-or-later.
"""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any

from groundtruth_kb.db import KnowledgeDB
from groundtruth_kb.harness_projection import HarnessStateError, read_identity

# Canonical status tokens we surface in the handoff prompt. Latest-only per
# Document; matches the bridge file-bridge protocol § Statuses.
_BRIDGE_STATUSES_OF_INTEREST = ("NEW", "REVISED", "GO", "NO-GO")

# Roles for which a bridge entry is considered "open" / actionable.
_ROLE_ACTIONABLE_STATUSES = {
    "prime-builder": ("GO", "NO-GO"),
    "loyal-opposition": ("NEW", "REVISED"),
}


class HandoffError(Exception):
    """Raised when the handoff service cannot produce a deterministic prompt.

    The CLI maps this to a non-zero exit code.
    """


def generate(
    session_id: str | None = None,
    *,
    project_root: Path | None = None,
    db: KnowledgeDB | None = None,
) -> dict[str, Any]:
    """Generate the deterministic handoff prompt for a session.

    Args:
        session_id: Operator-supplied identifier used to key MemBase rows and
            name the markdown output file. When ``None``, the service derives
            an identifier from the latest archived envelope's ``harness_id``
            plus its ``closed_at`` field.
        project_root: Repository root. Defaults to the GT-KB project root
            (resolved relative to this module).
        db: Optional pre-bound ``KnowledgeDB``. Tests inject this; production
            opens the default database resolved from ``project_root``.

    Returns:
        A dict with keys ``session_id``, ``prompt_markdown``, ``output_files``,
        and ``session_prompts_id``.

    Raises:
        HandoffError: When the archive directory or a usable envelope file is
            missing, or when the bridge index cannot be read.
    """
    root = (project_root or _default_project_root()).resolve()
    harness_name = _resolve_active_harness_name(root)
    archive_dir = root / "harness-state" / harness_name / "session-envelope-archive"
    if not archive_dir.exists():
        raise HandoffError(
            f"Session-envelope archive directory missing: {archive_dir}. "
            "WI-4293 (session-envelope durability) must land before the handoff "
            "service can read archived envelopes for harness '{harness_name}'.".format(
                harness_name=harness_name,
            )
        )

    envelope_path = _select_envelope_for_session_id(archive_dir, session_id)
    if envelope_path is None:
        raise HandoffError(
            f"No archived session envelope found in {archive_dir}. "
            "Run ::wrap on a session before invoking the handoff service.",
        )

    envelope_bytes = envelope_path.read_bytes()
    envelope = json.loads(envelope_bytes.decode("utf-8"))

    resolved_session_id = session_id or _derive_session_id(envelope, envelope_path)

    bridge_index_path = root / "bridge" / "INDEX.md"
    if not bridge_index_path.exists():
        raise HandoffError(f"Bridge INDEX missing: {bridge_index_path}")
    bridge_bytes = bridge_index_path.read_bytes()
    role = _role_from_envelope(envelope)
    bridge_state = _parse_bridge_state_for_role(bridge_bytes.decode("utf-8"), role)

    idempotency_key = _compute_idempotency_key(
        resolved_session_id,
        envelope_bytes,
        bridge_bytes,
    )

    owned_db = db is None
    db_instance = db if db is not None else KnowledgeDB(db_path=root / "groundtruth.db")
    try:
        existing = db_instance.get_session_prompt_by_idempotency_key(
            resolved_session_id,
            idempotency_key,
        )
        if existing is not None:
            prompt_markdown = existing["prompt_text"]
            handoff_md_path = _write_handoff_markdown(
                root,
                resolved_session_id,
                prompt_markdown,
            )
            return {
                "session_id": resolved_session_id,
                "prompt_markdown": prompt_markdown,
                "output_files": [str(handoff_md_path.relative_to(root))],
                "session_prompts_id": _row_identifier(existing),
            }

        prompt_markdown = _assemble_prompt(
            session_id=resolved_session_id,
            envelope=envelope,
            envelope_path=envelope_path,
            bridge_state=bridge_state,
            role=role,
        )
        context = {
            "idempotency_key": idempotency_key,
            "envelope_path": str(envelope_path.relative_to(root)),
            "role": role,
        }
        row = db_instance.insert_session_prompt(
            resolved_session_id,
            prompt_markdown,
            context=context,
        )
        if row is None:
            raise HandoffError(
                f"MemBase insert_session_prompt returned no row for session_id={resolved_session_id!r}",
            )
        handoff_md_path = _write_handoff_markdown(
            root,
            resolved_session_id,
            prompt_markdown,
        )
        return {
            "session_id": resolved_session_id,
            "prompt_markdown": prompt_markdown,
            "output_files": [str(handoff_md_path.relative_to(root))],
            "session_prompts_id": _row_identifier(row),
        }
    finally:
        if owned_db:
            with _suppress():
                db_instance.close()


# ---------------------------------------------------------------------------
# Pure helpers (deterministic)
# ---------------------------------------------------------------------------


def _default_project_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _resolve_active_harness_name(project_root: Path) -> str:
    """Resolve the active host-local harness name via deterministic disambiguation.

    Selection rule (per FINDING-P1-002 of
    ``bridge/gtkb-handoff-prompt-deterministic-service-impl-007.md``):

    1. Read ``harness-state/harness-identities.json``.
    2. If any record carries ``status == "active"`` (legacy/test schema),
       restrict the pool to those names; otherwise use every enumerated
       harness as the pool. The live identities file omits ``status`` per
       its current schema, so the directory-presence filter below is the
       deterministic disambiguator on production checkouts.
    3. Filter the pool to names whose
       ``harness-state/<name>/session-envelope-archive`` directory exists.
    4. If exactly one candidate remains, return it.
    5. Otherwise raise ``HandoffError`` — alphabetic fallback would select a
       registered-but-non-present harness (e.g., ``antigravity`` sorting
       before ``claude`` / ``codex``).
    """
    identities_path = project_root / "harness-state" / "harness-identities.json"
    try:
        data = read_identity(project_root)
    except HarnessStateError as exc:
        raise HandoffError(f"Harness identities missing or unreadable: {identities_path}") from exc
    harnesses = data.get("harnesses", {}) or data.get("identities", {}) or {}
    if not harnesses:
        raise HandoffError(
            f"No harnesses recorded in {identities_path}; cannot resolve active harness.",
        )
    explicit_active = [
        name for name, record in harnesses.items() if isinstance(record, dict) and record.get("status") == "active"
    ]
    pool = explicit_active or list(harnesses.keys())
    candidates = sorted(
        name for name in pool if (project_root / "harness-state" / name / "session-envelope-archive").is_dir()
    )
    if not candidates:
        raise HandoffError(
            "No registered harness has a session-envelope archive directory under "
            f"{project_root / 'harness-state'}. WI-4293 (session-envelope durability) "
            "must land before the handoff service can read archived envelopes.",
        )
    if len(candidates) == 1:
        return candidates[0]
    raise HandoffError(
        "Cannot deterministically resolve active harness: multiple harnesses have "
        f"session-envelope archives ({candidates}); supply the active harness explicitly.",
    )


def _latest_archived_envelope(archive_dir: Path) -> Path | None:
    """Return the lexicographically largest envelope file, or None.

    Archive filenames are ``<closed_at-ISO>-session-envelope.json`` per
    WI-4293's invariant; lexicographic ordering matches chronological order
    for ISO-8601 UTC timestamps.
    """
    candidates = sorted(p for p in archive_dir.glob("*-session-envelope.json") if p.is_file())
    return candidates[-1] if candidates else None


def _select_envelope_for_session_id(
    archive_dir: Path,
    session_id: str | None,
) -> Path | None:
    """Select the archived envelope identified by ``session_id``.

    Per ``SPEC-HANDOFF-PROMPT-DETERMINISTIC-SERVICE-001`` § Inputs (line 278):
    ``<harness_name>`` and ``<closed_at-ISO>`` are resolved "from the
    ``session_id`` + directory contents at service invocation time." That
    contract requires the explicit ``session_id`` to participate in archive
    selection — not be applied as a label after a latest-envelope pick.

    Selection rules:

    1. If ``session_id is None``: fall back to ``_latest_archived_envelope``
       so callers that omit the argument receive the most-recently-archived
       envelope (canonical case for fresh-wrap handoff).
    2. If ``session_id`` is supplied: scan candidate envelope files. For
       each, look up the canonical session identifier:

       a. Prefer the envelope's explicit ``session_id`` JSON field when
          present.
       b. Otherwise fall back to ``_derive_session_id(envelope, path)``
          (``{harness_id}-{closed_at}``), which is the legacy derivation
          used by callers that pre-date the explicit-field schema.

       Match the supplied ``session_id`` against the canonical identifier.
       On exactly one match: return it. On zero matches: raise
       ``HandoffError`` ("no archived envelope matches session_id"). On
       multiple matches: raise ``HandoffError`` ("ambiguous").

    This closes FINDING-P1-001 of
    ``bridge/gtkb-handoff-prompt-deterministic-service-impl-009.md``.
    """
    candidates = sorted(p for p in archive_dir.glob("*-session-envelope.json") if p.is_file())
    if not candidates:
        return None
    if session_id is None:
        return candidates[-1]

    matches: list[Path] = []
    for candidate in candidates:
        try:
            env = json.loads(candidate.read_bytes().decode("utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError):
            continue
        explicit = env.get("session_id") if isinstance(env, dict) else None
        if explicit is not None:
            canonical_id = explicit
        else:
            canonical_id = _derive_session_id(env if isinstance(env, dict) else {}, candidate)
        if canonical_id == session_id:
            matches.append(candidate)

    if len(matches) == 1:
        return matches[0]
    if not matches:
        raise HandoffError(
            f"No archived envelope matches session_id={session_id!r} in {archive_dir}. "
            f"Found {len(candidates)} envelope(s); the explicit session_id must match an "
            "envelope's `session_id` field or its derived `<harness_id>-<closed_at>` form."
        )
    raise HandoffError(
        f"Ambiguous archive selection: multiple envelopes match session_id={session_id!r} "
        f"in {archive_dir} ({[m.name for m in matches]}). Archive envelopes must have "
        "distinct session_id values."
    )


def _derive_session_id(envelope: dict[str, Any], envelope_path: Path) -> str:
    """Deterministically derive a session_id from envelope metadata."""
    harness_id = envelope.get("harness_id") or envelope.get("harness_name") or "unknown"
    closed_at = envelope.get("closed_at") or envelope_path.stem
    return f"{harness_id}-{closed_at}"


def _role_from_envelope(envelope: dict[str, Any]) -> str:
    """Extract the canonical operating role from the envelope."""
    role = envelope.get("role_resolved") or envelope.get("role")
    if role in _ROLE_ACTIONABLE_STATUSES:
        return role
    return "prime-builder"


_DOCUMENT_LINE = re.compile(r"^Document:\s*(?P<name>\S+)\s*$")
_STATUS_LINE = re.compile(r"^(?P<status>[A-Z-]+):\s*(?P<path>\S+)\s*$")


def _parse_bridge_state_for_role(index_text: str, role: str) -> list[dict[str, str]]:
    """Parse ``bridge/INDEX.md`` into role-filtered latest-status entries.

    Returns a list of ``{document, status, path}`` dicts whose ``status`` is
    actionable for ``role``. Entries are ordered by their first appearance in
    the index (newest-first, per the protocol).
    """
    actionable = _ROLE_ACTIONABLE_STATUSES.get(role, _ROLE_ACTIONABLE_STATUSES["prime-builder"])
    entries: list[dict[str, str]] = []
    current_doc: str | None = None
    latest_seen: bool = False
    for raw in index_text.splitlines():
        line = raw.rstrip()
        doc_match = _DOCUMENT_LINE.match(line)
        if doc_match:
            current_doc = doc_match.group("name")
            latest_seen = False
            continue
        if current_doc is None:
            continue
        status_match = _STATUS_LINE.match(line)
        if not status_match:
            continue
        if latest_seen:
            continue
        latest_seen = True
        status = status_match.group("status")
        if status not in _BRIDGE_STATUSES_OF_INTEREST:
            continue
        if status not in actionable:
            continue
        entries.append(
            {
                "document": current_doc,
                "status": status,
                "path": status_match.group("path"),
            },
        )
    return entries


def _compute_idempotency_key(
    session_id: str,
    envelope_bytes: bytes,
    bridge_bytes: bytes,
) -> str:
    """Compute the deterministic idempotency key for these inputs."""
    digest = hashlib.sha256()
    digest.update(session_id.encode("utf-8"))
    digest.update(b"\x00")
    digest.update(envelope_bytes)
    digest.update(b"\x00")
    digest.update(bridge_bytes)
    return f"sha256:{digest.hexdigest()}"


def _assemble_prompt(
    *,
    session_id: str,
    envelope: dict[str, Any],
    envelope_path: Path,
    bridge_state: list[dict[str, str]],
    role: str,
) -> str:
    """Assemble the deterministic handoff-prompt markdown body."""
    harness_id = envelope.get("harness_id", "unknown")
    harness_name = envelope.get("harness_name", "unknown")
    project_id = envelope.get("project_id") or "unset"
    active_wi = envelope.get("active_work_item_id") or "unset"
    work_item_ids = envelope.get("work_item_ids") or []
    closed_at = envelope.get("closed_at") or "unset"
    wrap_outcome = envelope.get("wrap_outcome") or "unset"
    topics = envelope.get("topics") or []

    lines: list[str] = []
    lines.append(f"# Handoff Prompt - session {session_id}")
    lines.append("")
    lines.append(
        "Generated deterministically per "
        "SPEC-HANDOFF-PROMPT-DETERMINISTIC-SERVICE-001 from the archived "
        "session envelope plus the live bridge index.",
    )
    lines.append("")
    lines.append("## Closed Session Envelope")
    lines.append("")
    lines.append(f"- envelope_file: {envelope_path.name}")
    lines.append(f"- harness_id: {harness_id}")
    lines.append(f"- harness_name: {harness_name}")
    lines.append(f"- role: {role}")
    lines.append(f"- project_id: {project_id}")
    lines.append(f"- active_work_item_id: {active_wi}")
    lines.append(f"- work_item_ids: {', '.join(work_item_ids) if work_item_ids else 'none'}")
    lines.append(f"- closed_at: {closed_at}")
    lines.append(f"- wrap_outcome: {wrap_outcome}")
    lines.append("")
    lines.append("## Topics Recorded in Envelope")
    lines.append("")
    if topics:
        for topic in topics:
            ttype = topic.get("type", "unknown")
            outcome = topic.get("close_outcome", "unset")
            opened = topic.get("opened_at", "unset")
            closed = topic.get("closed_at", "unset")
            lines.append(
                f"- {ttype}: close_outcome={outcome} opened_at={opened} closed_at={closed}",
            )
    else:
        lines.append("- (no topics recorded)")
    lines.append("")
    lines.append(f"## Open Bridge Entries Actionable for {role}")
    lines.append("")
    if bridge_state:
        for entry in bridge_state:
            lines.append(
                f"- {entry['status']}: {entry['document']} -> {entry['path']}",
            )
    else:
        lines.append("- (no actionable bridge entries for this role)")
    lines.append("")
    lines.append("## Next-Session Direction")
    lines.append("")
    lines.append(
        "Read this handoff prompt before reading bridge/INDEX.md. Then read "
        "the live bridge state directly and act on the role-actionable "
        "entries above in oldest-first order.",
    )
    lines.append("")
    return "\n".join(lines)


def _write_handoff_markdown(
    project_root: Path,
    session_id: str,
    prompt_markdown: str,
) -> Path:
    """Write the handoff-prompt markdown to .claude/session/handoff-<id>.md."""
    out_dir = project_root / ".claude" / "session"
    out_dir.mkdir(parents=True, exist_ok=True)
    safe_session_id = re.sub(r"[^A-Za-z0-9._-]", "_", session_id)
    out_path = out_dir / f"handoff-{safe_session_id}.md"
    out_path.write_text(prompt_markdown, encoding="utf-8")
    return out_path


def _row_identifier(row: dict[str, Any]) -> str:
    """Return a stable identifier for a session_prompts row."""
    rowid = row.get("rowid")
    if rowid is None:
        return f"session_prompts:{row.get('session_id')}:{row.get('version')}"
    return f"session_prompts:{rowid}"


class _suppress:
    """Tiny context manager that swallows AttributeError on db.close()."""

    def __enter__(self) -> _suppress:
        return self

    def __exit__(self, exc_type, exc, tb) -> bool:
        return exc_type is None or issubclass(exc_type, AttributeError)
