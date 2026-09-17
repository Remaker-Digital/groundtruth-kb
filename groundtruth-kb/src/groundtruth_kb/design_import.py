"""Local Claude Design handoff inspection for GroundTruth-KB (O-7 R21).

``gt design inspect`` reads a local ``.zip`` archive or a directory handoff and reports its file list with sizes,
the archive ``sha256`` (zips only), the ``SPEC-CD-HANDOFF-FORMAT-001`` D1 format warnings and a deterministic,
redacted inspection record with its content hash. Raw HTML / JSX / CSS / PNG bytes are never read into the record.
The inspection publishes nothing: the former automatic publication of the record into the retired deliberation
archive is retired, no database is opened and no archive attribution exists. A missing path is a usage error; a path
that is neither a ``.zip`` file nor a directory is refused.

Imported handoffs remain design intent and evidence (``GOV-CD-PRESERVATION``), never production code or a bridge
bypass. Live Claude Design API integration, context-pack generation and visual verification remain out of scope.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import hashlib
import zipfile
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from groundtruth_kb.governance.credential_patterns import db_pattern_list

__all__ = [
    "HandoffEntry",
    "HandoffInspection",
    "InspectionReport",
    "build_inspection_report",
    "format_inspection_content",
    "inspect_handoff",
    "redact_inspection_content",
    "validate_handoff_format",
]


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
    files = sorted((p.relative_to(dir_path).as_posix(), p) for p in dir_path.rglob("*") if p.is_file())
    entries = tuple(HandoffEntry(path=rel, size_bytes=p.stat().st_size) for rel, p in files)
    return entries, sum(e.size_bytes for e in entries)


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

    if not any(p.endswith("readme.md") for p in paths):
        warnings.append("Missing README.md (D1 mandatory).")
    if not any("project/index.html" in p for p in paths):
        warnings.append("Missing project/index.html (D1 mandatory).")
    if not any(p.endswith(".css") and "project/" in p for p in paths):
        warnings.append("Missing project/*.css design-token source (D1 mandatory).")
    if not any((p.endswith(".jsx") or p.endswith(".tsx")) and "project/" in p for p in paths):
        warnings.append("Missing at least one project/*.{jsx,tsx} component file (D1 mandatory).")
    return warnings


# ---------------------------------------------------------------------------
# Inspection → canonical content string (stable across re-runs)
# ---------------------------------------------------------------------------


def format_inspection_content(
    *,
    inspection: HandoffInspection,
    date: str,
    session_id: str | None,
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
    if session_id:
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


def redact_inspection_content(content: str) -> tuple[str, str | None]:
    """Replace credential and PII matches from the canonical pattern catalog with ``[REDACTED:<name>]`` markers.

    Returns the redacted text and a note naming each matched pattern with its occurrence count, or ``None`` when
    nothing matched. The catalog is the shared cross-consumer source; no database is involved.
    """
    notes: list[str] = []
    result = content
    for name, pattern in db_pattern_list():
        count = len(pattern.findall(result))
        if count:
            result = pattern.sub(f"[REDACTED:{name}]", result)
            notes.append(f"{name}: {count} occurrence(s)")
    return result, "; ".join(notes) if notes else None


# ---------------------------------------------------------------------------
# The complete local report — computed, shown, never stored by the platform
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class InspectionReport:
    inspection: HandoffInspection
    warnings: tuple[str, ...]
    content: str
    content_hash: str
    redaction_notes: str | None

    def to_json_dict(self) -> dict[str, Any]:
        return {
            "source_path": self.inspection.source_path,
            "source_kind": self.inspection.source_kind,
            "sha256": self.inspection.sha256,
            "total_bytes": self.inspection.total_bytes,
            "file_count": len(self.inspection.entries),
            "entries": [{"path": e.path, "size_bytes": e.size_bytes} for e in self.inspection.entries],
            "warnings": list(self.warnings),
            "content": self.content,
            "content_hash": self.content_hash,
            "redaction_notes": self.redaction_notes,
        }


def build_inspection_report(
    handoff_path: Path,
    *,
    date: str,
    session_id: str | None = None,
    owner_decision: str | None = None,
    notes: str | None = None,
) -> InspectionReport:
    """Inspect, validate, format and redact one local handoff.

    A pure pipeline: it reads the handoff's metadata and writes nothing. Identical inputs reproduce the same
    ``content_hash``; the caller decides what, if anything, to do with the report.
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
    redacted, redaction_notes = redact_inspection_content(content)
    return InspectionReport(
        inspection=inspection,
        warnings=tuple(warnings),
        content=redacted,
        content_hash=hashlib.sha256(redacted.encode("utf-8")).hexdigest(),
        redaction_notes=redaction_notes,
    )
