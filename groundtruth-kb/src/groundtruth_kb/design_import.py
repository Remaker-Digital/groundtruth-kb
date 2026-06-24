"""Local Claude Design handoff import / inspection for GroundTruth-KB.

Productizes the metadata-only handoff inspection, validation, content-formatting,
and Deliberation Archive archival pipeline that previously lived only in
``scripts/archive_claude_design_handoff.py`` (PROC-CD-DA-ARCHIVAL-001). The
reusable logic now lives here as a package module so it can back the
package-facing ``gt design import`` command, while the original script remains a
thin Agent Red-scoped compatibility wrapper.

Scope: local ``.zip`` or directory handoffs only. The pipeline inspects a handoff
(file list + sizes + an archive ``sha256``, never raw bytes), validates it
against ``SPEC-CD-HANDOFF-FORMAT-001``'s D1 structural assertions, formats a
deterministic inspection record, and (only with ``apply=True``) archives that
record as one content-hash-idempotent ``report`` Deliberation Archive row.

Out of scope for this slice and explicitly requiring a separate proposal: live
Claude Design API integration, production-code adoption, context-pack
generation, visual verification, dashboards, and adopter application UI changes.
Imported handoffs remain design intent and evidence (``GOV-CD-PRESERVATION``),
never production code or a bridge bypass: raw HTML/JSX/CSS/PNG bytes are never
inlined into Deliberation Archive content.

Design notes (carried forward from the original script's GO'd bridge binding
condition #5 — reuse existing DA harvest patterns):

* **Redaction**: delegates to ``KnowledgeDB.redact_content`` — identical to
  ``scripts/harvest_session_deliberations.py``.
* **Idempotence**: pre-checks ``current_deliberations`` for
  ``(source_ref, content_hash)`` before insert.
* **Binary safety**: handoff archive/dir is inspected for a file list + metadata
  + observations; raw bytes are never inlined.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import hashlib
import zipfile
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

__all__ = [
    "HandoffEntry",
    "HandoffInspection",
    "ArchiveResult",
    "inspect_handoff",
    "validate_handoff_format",
    "format_inspection_content",
    "archive",
]

# Default Deliberation Archive attribution for archived handoff inspection rows.
# The handoff intake pipeline originated as an Agent Red-specific path; these
# defaults preserve that provenance. Callers (the compatibility script, the
# package CLI) override ``changed_by`` to record the surface that performed the
# import.
_DEFAULT_ORIGIN_PROJECT = "agent-red"
_DEFAULT_ORIGIN_REPO = "Remaker-Digital/agent-red-customer-engagement"
_DEFAULT_CHANGED_BY = "groundtruth_kb.design_import"


# ---------------------------------------------------------------------------
# KB + redaction glue (identical pattern to harvest_session_deliberations.py)
# ---------------------------------------------------------------------------


def _load_kb() -> Any:
    """Open the package-native MemBase (root ``groundtruth.db``).

    This default is used only when no ``db`` is injected into :func:`archive`
    and ``apply=True`` is requested. Tests inject a temporary KnowledgeDB, and
    the Agent Red compatibility wrapper injects the AR-scoped KnowledgeDB, so
    neither path relies on this default.
    """
    from groundtruth_kb.db import KnowledgeDB

    return KnowledgeDB()


def _redact(content: str) -> tuple[str, str | None]:
    """Delegate to the KB's redaction classmethod (same as the harvest script)."""
    from groundtruth_kb.db import KnowledgeDB as _GT

    return _GT.redact_content(content)


# ---------------------------------------------------------------------------
# Handoff inspection — file-list + metadata only, no raw bytes
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class HandoffEntry:
    """One file inside the handoff — path + size only, never bytes."""

    path: str
    size_bytes: int


@dataclass(frozen=True)
class HandoffInspection:
    source_path: str
    source_kind: str  # "zip" or "directory"
    entries: tuple[HandoffEntry, ...]
    total_bytes: int
    sha256: str | None  # only for zips; None for directories


def _list_zip_entries(zip_path: Path) -> tuple[tuple[HandoffEntry, ...], int]:
    entries: list[HandoffEntry] = []
    total = 0
    with zipfile.ZipFile(zip_path, "r") as zf:
        for info in zf.infolist():
            if info.is_dir():
                continue
            entries.append(HandoffEntry(path=info.filename, size_bytes=info.file_size))
            total += info.file_size
    return tuple(entries), total


def _list_dir_entries(dir_path: Path) -> tuple[tuple[HandoffEntry, ...], int]:
    entries: list[HandoffEntry] = []
    total = 0
    for p in sorted(dir_path.rglob("*")):
        if p.is_file():
            rel = p.relative_to(dir_path).as_posix()
            size = p.stat().st_size
            entries.append(HandoffEntry(path=rel, size_bytes=size))
            total += size
    return tuple(entries), total


def _sha256_of_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def inspect_handoff(handoff_path: Path) -> HandoffInspection:
    """Return a metadata-only inspection of a handoff zip or directory."""
    if not handoff_path.exists():
        raise FileNotFoundError(f"Handoff path does not exist: {handoff_path}")

    if handoff_path.is_file() and handoff_path.suffix.lower() == ".zip":
        entries, total = _list_zip_entries(handoff_path)
        return HandoffInspection(
            source_path=str(handoff_path),
            source_kind="zip",
            entries=entries,
            total_bytes=total,
            sha256=_sha256_of_file(handoff_path),
        )
    if handoff_path.is_dir():
        entries, total = _list_dir_entries(handoff_path)
        return HandoffInspection(
            source_path=str(handoff_path),
            source_kind="directory",
            entries=entries,
            total_bytes=total,
            sha256=None,
        )
    raise ValueError(f"Handoff path must be a .zip file or a directory: {handoff_path}")


def validate_handoff_format(inspection: HandoffInspection) -> list[str]:
    """Check SPEC-CD-HANDOFF-FORMAT-001's structural assertion.

    Returns a list of human-readable warnings (empty if conformant).
    """
    warnings: list[str] = []
    paths = {entry.path.lower().replace("\\", "/") for entry in inspection.entries}

    def _contains(stem: str) -> bool:
        return any(p.endswith(stem) or f"/{stem}" in p for p in paths)

    if not any(p.endswith("readme.md") for p in paths):
        warnings.append("Missing README.md (D1 mandatory).")
    if not any("project/index.html" in p for p in paths):
        warnings.append("Missing project/index.html (D1 mandatory).")
    if not any(p.endswith(".css") and "project/" in p for p in paths):
        warnings.append("Missing project/*.css design-token source (D1 mandatory).")
    if not any((p.endswith(".jsx") or p.endswith(".tsx")) and "project/" in p for p in paths):
        warnings.append("Missing at least one project/*.{jsx,tsx} component file (D1 mandatory).")
    _ = _contains  # reserved for future optional checks
    return warnings


# ---------------------------------------------------------------------------
# Inspection → canonical content string (stable across re-runs)
# ---------------------------------------------------------------------------


def format_inspection_content(
    *,
    inspection: HandoffInspection,
    date: str,
    session_id: str,
    owner_decision: str | None,
    notes: str | None,
    warnings: Iterable[str],
) -> str:
    """Produce deterministic, redaction-safe inspection content.

    Content hashes are sensitive to this function's output — entries are
    pre-sorted in ``_list_zip_entries`` / ``_list_dir_entries`` so re-runs on
    the same handoff reproduce the same string.
    """
    lines: list[str] = []
    lines.append("# Claude Design Handoff Inspection")
    lines.append("")
    lines.append(f"Handoff date: {date}")
    lines.append(f"Session: {session_id}")
    lines.append(f"Source: {inspection.source_path}")
    lines.append(f"Source kind: {inspection.source_kind}")
    if inspection.sha256:
        lines.append(f"sha256: {inspection.sha256}")
    lines.append(f"Total bytes: {inspection.total_bytes}")
    lines.append(f"File count: {len(inspection.entries)}")
    lines.append("")

    lines.append("## File list")
    for entry in inspection.entries:
        lines.append(f"- {entry.path} ({entry.size_bytes} bytes)")
    lines.append("")

    lines.append("## Format conformance (SPEC-CD-HANDOFF-FORMAT-001)")
    warnings = list(warnings)
    if warnings:
        lines.append("WARNINGS:")
        for w in warnings:
            lines.append(f"- {w}")
    else:
        lines.append("OK — all D1 mandatory files present.")
    lines.append("")

    if owner_decision:
        lines.append("## Owner decision / triage outcome")
        lines.append(owner_decision.strip())
        lines.append("")

    if notes:
        lines.append("## Inspection notes")
        lines.append(notes.strip())
        lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# DA insertion (content-hash idempotent)
# ---------------------------------------------------------------------------


@dataclass
class ArchiveResult:
    action: str  # "created", "would_create", "skipped"
    source_ref: str
    content_hash: str
    delib_id: Any | None
    redaction_reason: str | None
    warnings: list[str]


def archive(
    *,
    handoff_path: Path,
    date: str,
    session_id: str,
    owner_decision: str | None = None,
    notes: str | None = None,
    source_ref: str | None = None,
    apply: bool = False,
    db: Any | None = None,
    origin_project: str = _DEFAULT_ORIGIN_PROJECT,
    origin_repo: str = _DEFAULT_ORIGIN_REPO,
    changed_by: str = _DEFAULT_CHANGED_BY,
) -> ArchiveResult:
    """Archive one handoff as one ``report`` DA row.

    The function is a pure pipeline: inspect → format → redact → hash →
    pre-check → insert. Every step returns metadata that the caller surfaces.
    With ``apply=False`` (the default) it computes the would-be record without
    any database access. ``db`` may be injected (tests, the Agent Red
    compatibility wrapper, the package CLI) to target a specific KnowledgeDB;
    when omitted and ``apply=True`` the package-native MemBase is opened.
    """
    inspection = inspect_handoff(handoff_path)
    warnings = validate_handoff_format(inspection)

    content = format_inspection_content(
        inspection=inspection,
        date=date,
        session_id=session_id,
        owner_decision=owner_decision,
        notes=notes,
        warnings=warnings,
    )
    redacted, redaction_reason = _redact(content)
    content_hash = hashlib.sha256(redacted.encode()).hexdigest()

    ref = source_ref or f"claude-design-handoff:{date}:{handoff_path.name}"
    title = f"Claude Design handoff inspection ({date})"
    summary = (
        f"Inspection of {inspection.source_kind} at "
        f"{handoff_path.name}; {len(inspection.entries)} files; "
        f"{inspection.total_bytes} bytes."
    )

    if not apply:
        return ArchiveResult(
            action="would_create",
            source_ref=ref,
            content_hash=content_hash,
            delib_id=None,
            redaction_reason=redaction_reason,
            warnings=warnings,
        )

    if db is None:
        db = _load_kb()

    conn = db._get_conn()
    exists = conn.execute(
        "SELECT id FROM current_deliberations WHERE source_ref = ? AND content_hash = ?",
        (ref, content_hash),
    ).fetchone()
    if exists:
        return ArchiveResult(
            action="skipped",
            source_ref=ref,
            content_hash=content_hash,
            delib_id=exists[0],
            redaction_reason=redaction_reason,
            warnings=warnings,
        )

    delib = db.upsert_deliberation_source(
        source_type="report",
        source_ref=ref,
        content=redacted,
        title=title,
        summary=summary,
        outcome="informational",
        session_id=session_id,
        origin_project=origin_project,
        origin_repo=origin_repo,
        changed_by=changed_by,
        change_reason=("PROC-CD-DA-ARCHIVAL-001 (gt design import) — Claude Design handoff inspection archive."),
    )
    return ArchiveResult(
        action="created",
        source_ref=ref,
        content_hash=content_hash,
        delib_id=delib["id"] if delib else None,
        redaction_reason=redaction_reason,
        warnings=warnings,
    )
