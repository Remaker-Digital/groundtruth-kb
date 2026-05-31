"""Read-only MemBase effective-use audit helpers.

This module implements the audit slice approved by
``bridge/gtkb-membase-effective-use-recovery-next-slice-004.md``. It exposes a
programmatic API only; CLI registration is intentionally out of scope for this
bridge thread.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

SPEC_ID_RE = re.compile(r"\b(?:ADR|DCL|GOV|PB|SPEC)-[A-Z0-9][A-Z0-9_-]*\d+\b")
STATUS_LINE_RE = re.compile(r"^(NEW|REVISED|GO|NO-GO|VERIFIED|WITHDRAWN|ADVISORY):\s*(bridge/.+?\.md)\s*$")
DOCUMENT_LINE_RE = re.compile(r"^Document:\s*(\S+)\s*$")
SENTENCE_RE = re.compile(r"(?<=[.!?])\s+")
DELIB_DRAFT_RE = re.compile(r"(?im)^\s*(?:draft\s+delib|delib\s+draft|source_type\s*=\s*owner_conversation)\b")


@dataclass(frozen=True)
class BridgeEntry:
    """Latest bridge state plus the referenced files for one document entry."""

    document: str
    latest_status: str
    latest_path: str
    version_paths: tuple[str, ...]


@dataclass(frozen=True)
class AuditFinding:
    """One audit finding from a MemBase effective-use lens."""

    lens: str
    severity: str
    subject: str
    message: str
    references: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return {
            "lens": self.lens,
            "severity": self.severity,
            "subject": self.subject,
            "message": self.message,
            "references": list(self.references),
        }


@dataclass(frozen=True)
class AuditResult:
    """Aggregate read-only audit result."""

    generated_at: str
    project_root: str
    bridge_entries_scanned: int
    specs_scanned: int
    memory_files_scanned: int
    findings: tuple[AuditFinding, ...] = field(default_factory=tuple)

    @property
    def summary_by_lens(self) -> dict[str, int]:
        summary: dict[str, int] = {}
        for finding in self.findings:
            summary[finding.lens] = summary.get(finding.lens, 0) + 1
        return dict(sorted(summary.items()))

    def to_dict(self) -> dict[str, Any]:
        return {
            "generated_at": self.generated_at,
            "project_root": self.project_root,
            "bridge_entries_scanned": self.bridge_entries_scanned,
            "specs_scanned": self.specs_scanned,
            "memory_files_scanned": self.memory_files_scanned,
            "summary_by_lens": self.summary_by_lens,
            "finding_count": len(self.findings),
            "findings": [finding.to_dict() for finding in self.findings],
        }

    def to_markdown(self) -> str:
        lines = [
            "# MemBase Effective Use Audit",
            "",
            f"Generated: {self.generated_at}",
            f"Project root: `{self.project_root}`",
            "",
            "## Summary",
            "",
            f"- Bridge entries scanned: {self.bridge_entries_scanned}",
            f"- Specs scanned: {self.specs_scanned}",
            f"- Memory files scanned: {self.memory_files_scanned}",
            f"- Findings: {len(self.findings)}",
        ]
        if self.summary_by_lens:
            for lens, count in self.summary_by_lens.items():
                lines.append(f"- {lens}: {count}")
        else:
            lines.append("- No findings.")
        lines.extend(["", "## Findings", ""])
        if not self.findings:
            lines.append("No MemBase effective-use findings were detected by this snapshot.")
            return "\n".join(lines) + "\n"
        for finding in self.findings:
            lines.extend(
                [
                    f"### {finding.lens}: {finding.subject}",
                    "",
                    f"- Severity: `{finding.severity}`",
                    f"- Message: {finding.message}",
                ]
            )
            if finding.references:
                lines.append("- References:")
                lines.extend(f"  - `{ref}`" for ref in finding.references)
            lines.append("")
        return "\n".join(lines)


def parse_bridge_index(index_path: Path) -> list[BridgeEntry]:
    """Parse ``bridge/INDEX.md`` into latest-state entries."""

    if not index_path.is_file():
        return []
    entries: list[BridgeEntry] = []
    current_document: str | None = None
    current_statuses: list[tuple[str, str]] = []

    def flush() -> None:
        nonlocal current_document, current_statuses
        if current_document and current_statuses:
            latest_status, latest_path = current_statuses[0]
            entries.append(
                BridgeEntry(
                    document=current_document,
                    latest_status=latest_status,
                    latest_path=latest_path,
                    version_paths=tuple(path for _, path in current_statuses),
                )
            )
        current_document = None
        current_statuses = []

    for raw_line in index_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        doc_match = DOCUMENT_LINE_RE.match(line)
        if doc_match:
            flush()
            current_document = doc_match.group(1)
            continue
        if not line:
            flush()
            continue
        status_match = STATUS_LINE_RE.match(line)
        if current_document and status_match:
            current_statuses.append((status_match.group(1), status_match.group(2)))
    flush()
    return entries


def run_audit(
    project_root: str | Path = ".",
    *,
    db: Any | None = None,
    age_threshold_days: int | None = 183,
    now: datetime | None = None,
) -> AuditResult:
    """Run all read-only MemBase effective-use audit lenses."""

    root = Path(project_root).resolve()
    generated_at = (now or datetime.now(UTC)).astimezone(UTC).isoformat()
    active_db = db if db is not None else _open_default_db(root)
    specs = _current_specs(active_db)
    filtered_specs = _filter_specs_by_age(specs, age_threshold_days=age_threshold_days, now=now)
    spec_by_id = {str(spec.get("id")): spec for spec in filtered_specs if spec.get("id")}
    bridge_entries = parse_bridge_index(root / "bridge" / "INDEX.md")
    memory_files = sorted((root / "memory").glob("*.md")) if (root / "memory").is_dir() else []

    findings: list[AuditFinding] = []
    findings.extend(_verified_state_mismatches(root, bridge_entries, spec_by_id, active_db))
    findings.extend(_duplicated_canonical_content(memory_files, filtered_specs))
    findings.extend(_delib_draft_candidates(memory_files))

    return AuditResult(
        generated_at=generated_at,
        project_root=str(root),
        bridge_entries_scanned=len(bridge_entries),
        specs_scanned=len(filtered_specs),
        memory_files_scanned=len(memory_files),
        findings=tuple(findings),
    )


def write_audit_report(result: AuditResult, out_path: str | Path) -> Path:
    """Write a markdown audit report and return the written path."""

    path = Path(out_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(result.to_markdown(), encoding="utf-8", newline="\n")
    return path


def _open_default_db(project_root: Path) -> Any | None:
    db_path = project_root / "groundtruth.db"
    if not db_path.exists():
        return None
    from groundtruth_kb.db import KnowledgeDB

    return KnowledgeDB(str(db_path))


def _current_specs(db: Any | None) -> list[dict[str, Any]]:
    if db is None or not hasattr(db, "list_specs"):
        return []
    rows = db.list_specs()
    return [dict(row) for row in rows]


def _filter_specs_by_age(
    specs: list[dict[str, Any]],
    *,
    age_threshold_days: int | None,
    now: datetime | None,
) -> list[dict[str, Any]]:
    if age_threshold_days is None:
        return specs
    cutoff = (now or datetime.now(UTC)).astimezone(UTC) - timedelta(days=age_threshold_days)
    filtered: list[dict[str, Any]] = []
    for spec in specs:
        changed_at = _parse_datetime(spec.get("changed_at") or spec.get("created_at"))
        if changed_at is None or changed_at >= cutoff:
            filtered.append(spec)
    return filtered


def _parse_datetime(value: object) -> datetime | None:
    if not value:
        return None
    text = str(value).strip()
    if not text:
        return None
    try:
        return datetime.fromisoformat(text.replace("Z", "+00:00")).astimezone(UTC)
    except ValueError:
        return None


def _verified_state_mismatches(
    project_root: Path,
    bridge_entries: list[BridgeEntry],
    spec_by_id: dict[str, dict[str, Any]],
    db: Any | None,
) -> list[AuditFinding]:
    findings: list[AuditFinding] = []
    for entry in bridge_entries:
        if entry.latest_status != "VERIFIED":
            continue
        text = _read_entry_text(project_root, entry)
        for spec_id in sorted(extract_spec_ids(text)):
            spec = spec_by_id.get(spec_id)
            if spec is None and db is not None and hasattr(db, "get_spec"):
                fetched = db.get_spec(spec_id)
                spec = dict(fetched) if fetched else None
            if not spec:
                continue
            status = str(spec.get("status", "")).strip()
            if status and status != "verified":
                findings.append(
                    AuditFinding(
                        lens="verified_state_mismatch",
                        severity="warning",
                        subject=spec_id,
                        message=(
                            f"Bridge thread `{entry.document}` is latest VERIFIED and cites `{spec_id}`, "
                            f"but MemBase status is `{status}`."
                        ),
                        references=(entry.latest_path,),
                    )
                )
    return findings


def _read_entry_text(project_root: Path, entry: BridgeEntry) -> str:
    chunks: list[str] = []
    for rel_path in entry.version_paths:
        path = project_root / rel_path
        if path.is_file():
            chunks.append(path.read_text(encoding="utf-8", errors="replace"))
    return "\n\n".join(chunks)


def extract_spec_ids(text: str) -> set[str]:
    """Extract likely MemBase specification IDs from text."""

    return {match.group(0).rstrip(".,);:") for match in SPEC_ID_RE.finditer(text)}


def _duplicated_canonical_content(memory_files: list[Path], specs: list[dict[str, Any]]) -> list[AuditFinding]:
    findings: list[AuditFinding] = []
    memory_texts = {path: _normalize_text(path.read_text(encoding="utf-8", errors="replace")) for path in memory_files}
    for spec in specs:
        spec_id = str(spec.get("id") or "")
        description = str(spec.get("description") or "")
        triples = _sentence_triples(description)
        if not spec_id or not triples:
            continue
        for path, normalized_text in memory_texts.items():
            for triple in triples:
                if all(sentence in normalized_text for sentence in triple):
                    findings.append(
                        AuditFinding(
                            lens="duplicated_canonical_content",
                            severity="info",
                            subject=spec_id,
                            message=(
                                f"`{path.as_posix()}` repeats at least three consecutive sentences from "
                                f"MemBase spec `{spec_id}`."
                            ),
                            references=(path.as_posix(),),
                        )
                    )
                    break
    return findings


def _sentence_triples(text: str) -> list[tuple[str, str, str]]:
    sentences = [_normalize_text(part) for part in SENTENCE_RE.split(text) if _normalize_text(part)]
    if len(sentences) < 3:
        return []
    return [tuple(sentences[index : index + 3]) for index in range(len(sentences) - 2)]


def _normalize_text(text: str) -> str:
    return " ".join(text.lower().split())


def _delib_draft_candidates(memory_files: list[Path]) -> list[AuditFinding]:
    findings: list[AuditFinding] = []
    for path in memory_files:
        text = path.read_text(encoding="utf-8", errors="replace")
        if DELIB_DRAFT_RE.search(text):
            findings.append(
                AuditFinding(
                    lens="delib_draft_candidate",
                    severity="info",
                    subject=path.name,
                    message=f"`{path.as_posix()}` contains deliberation-draft-shaped text.",
                    references=(path.as_posix(),),
                )
            )
    return findings
