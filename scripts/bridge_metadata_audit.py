"""Read-only bridge author-metadata audit scanner (WI-4938).

Scans latest status-bearing bridge artifacts and classifies author metadata
compliance without mutating bridge files.
"""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

try:
    from scripts.gtkb_session_id import session_scratch_dirname
except ImportError:  # pragma: no cover - direct script execution path
    from gtkb_session_id import session_scratch_dirname

try:
    from bridge_author_metadata import (
        REQUIRED_AUTHOR_METADATA_FIELDS,
        author_metadata_gaps_for_content,
        bridge_artifact_status,
        extract_author_metadata,
        is_synthetic_session_context_id,
        metadata_value_is_valid,
    )
except ModuleNotFoundError:  # pragma: no cover
    from scripts.bridge_author_metadata import (
        REQUIRED_AUTHOR_METADATA_FIELDS,
        author_metadata_gaps_for_content,
        bridge_artifact_status,
        extract_author_metadata,
        is_synthetic_session_context_id,
        metadata_value_is_valid,
    )

VERSION_FILE_RE = re.compile(r"^(.+)-(\d{3})\.md$")
AUTOPROC_SESSION_RE = re.compile(r"-autoproc-", re.IGNORECASE)
STATUS_BEARING = frozenset({"NEW", "REVISED", "GO", "NO-GO", "VERIFIED"})

COMPLIANCE_COMPLIANT = "compliant"
COMPLIANCE_MISSING_FIELDS = "missing_fields"
COMPLIANCE_INVALID_VALUES = "invalid_values"
COMPLIANCE_SYNTHETIC_SESSION = "synthetic_session_id"
COMPLIANCE_NON_UNIQUE_SESSION = "non_unique_session_id"


@dataclass(frozen=True)
class ArtifactFinding:
    document: str
    path: str
    status: str
    author_harness_id: str
    missing_fields: tuple[str, ...]
    invalid_fields: tuple[str, ...]
    synthetic_session_id: bool
    non_unique_session_id: bool
    compliance: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class AuditReport:
    generated_at: str
    bridge_dir: str
    artifact_count: int
    findings: list[ArtifactFinding] = field(default_factory=list)
    summary: dict[str, int] = field(default_factory=dict)
    by_harness: dict[str, dict[str, int]] = field(default_factory=dict)
    by_status: dict[str, dict[str, int]] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "generated_at": self.generated_at,
            "bridge_dir": self.bridge_dir,
            "artifact_count": self.artifact_count,
            "summary": dict(sorted(self.summary.items())),
            "by_harness": {
                harness: dict(sorted(counts.items())) for harness, counts in sorted(self.by_harness.items())
            },
            "by_status": {status: dict(sorted(counts.items())) for status, counts in sorted(self.by_status.items())},
            "findings": [finding.to_dict() for finding in self.findings],
        }


def _is_synthetic_session_for_audit(value: object) -> bool:
    if not metadata_value_is_valid(value):
        return False
    text = str(value).strip().strip("`")
    if is_synthetic_session_context_id(text):
        return True
    return AUTOPROC_SESSION_RE.search(text) is not None


def _invalid_metadata_fields(metadata: dict[str, str]) -> list[str]:
    invalid: list[str] = []
    for field_name in REQUIRED_AUTHOR_METADATA_FIELDS:
        value = metadata.get(field_name)
        if value is None:
            continue
        if not metadata_value_is_valid(value):
            invalid.append(field_name)
    return sorted(invalid)


def _latest_bridge_files(bridge_dir: Path) -> dict[str, Path]:
    by_slug: dict[str, list[tuple[int, Path]]] = defaultdict(list)
    for path in sorted(bridge_dir.glob("*.md")):
        match = VERSION_FILE_RE.match(path.name)
        if not match:
            continue
        slug, version_text = match.group(1), match.group(2)
        by_slug[slug].append((int(version_text), path))
    latest: dict[str, Path] = {}
    for slug, entries in by_slug.items():
        _, path = sorted(entries, key=lambda item: item[0])[-1]
        latest[slug] = path
    return latest


def _classify_finding(
    *,
    document: str,
    path: str,
    status: str,
    metadata: dict[str, str],
    missing_fields: list[str],
    invalid_fields: list[str],
    synthetic_session_id: bool,
    non_unique_session_id: bool,
) -> ArtifactFinding:
    harness_id = metadata.get("author_harness_id", "")
    if missing_fields:
        compliance = COMPLIANCE_MISSING_FIELDS
    elif invalid_fields:
        compliance = COMPLIANCE_INVALID_VALUES
    elif synthetic_session_id:
        compliance = COMPLIANCE_SYNTHETIC_SESSION
    elif non_unique_session_id:
        compliance = COMPLIANCE_NON_UNIQUE_SESSION
    else:
        compliance = COMPLIANCE_COMPLIANT
    return ArtifactFinding(
        document=document,
        path=path,
        status=status,
        author_harness_id=harness_id,
        missing_fields=tuple(missing_fields),
        invalid_fields=tuple(invalid_fields),
        synthetic_session_id=synthetic_session_id,
        non_unique_session_id=non_unique_session_id,
        compliance=compliance,
    )


def audit_bridge_metadata(
    project_root: Path,
    *,
    bridge_dir: Path | None = None,
    generated_at: str | None = None,
) -> AuditReport:
    root = project_root.resolve()
    bridge_path = (bridge_dir or root / "bridge").resolve()
    generated_at = generated_at or datetime.now(tz=UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    latest_files = _latest_bridge_files(bridge_path)

    session_id_slugs: dict[str, list[str]] = defaultdict(list)
    raw_findings: list[tuple[ArtifactFinding, str | None]] = []

    for document in sorted(latest_files):
        path = latest_files[document]
        content = path.read_text(encoding="utf-8", errors="replace")
        status = bridge_artifact_status(content)
        if status not in STATUS_BEARING:
            continue
        metadata = extract_author_metadata(content)
        missing = author_metadata_gaps_for_content(content)
        invalid = _invalid_metadata_fields(metadata)
        session_id = metadata.get("author_session_context_id", "")
        synthetic = _is_synthetic_session_for_audit(session_id)
        if metadata_value_is_valid(session_id):
            session_id_slugs[str(session_id).strip()].append(document)
        finding = _classify_finding(
            document=document,
            path=str(path.relative_to(root)).replace("\\", "/"),
            status=status,
            metadata=metadata,
            missing_fields=missing,
            invalid_fields=invalid,
            synthetic_session_id=synthetic,
            non_unique_session_id=False,
        )
        raw_findings.append((finding, session_id if metadata_value_is_valid(session_id) else None))

    non_unique_ids = {
        session_id
        for session_id, slugs in session_id_slugs.items()
        if len(slugs) > 1 and (_is_synthetic_session_for_audit(session_id) or len(set(slugs)) > 1)
    }

    findings: list[ArtifactFinding] = []
    for finding, session_id in raw_findings:
        non_unique = bool(session_id and session_id in non_unique_ids and not finding.synthetic_session_id)
        if non_unique and finding.compliance == COMPLIANCE_COMPLIANT:
            findings.append(
                ArtifactFinding(
                    document=finding.document,
                    path=finding.path,
                    status=finding.status,
                    author_harness_id=finding.author_harness_id,
                    missing_fields=finding.missing_fields,
                    invalid_fields=finding.invalid_fields,
                    synthetic_session_id=finding.synthetic_session_id,
                    non_unique_session_id=True,
                    compliance=COMPLIANCE_NON_UNIQUE_SESSION,
                )
            )
        else:
            updated = finding
            if non_unique:
                updated = ArtifactFinding(
                    document=finding.document,
                    path=finding.path,
                    status=finding.status,
                    author_harness_id=finding.author_harness_id,
                    missing_fields=finding.missing_fields,
                    invalid_fields=finding.invalid_fields,
                    synthetic_session_id=finding.synthetic_session_id,
                    non_unique_session_id=True,
                    compliance=finding.compliance,
                )
            findings.append(updated)

    summary = Counter(finding.compliance for finding in findings)
    by_harness: dict[str, Counter[str]] = defaultdict(Counter)
    by_status: dict[str, Counter[str]] = defaultdict(Counter)
    for finding in findings:
        harness = finding.author_harness_id or "unknown"
        by_harness[harness][finding.compliance] += 1
        by_status[finding.status][finding.compliance] += 1

    return AuditReport(
        generated_at=generated_at,
        bridge_dir=str(bridge_path.relative_to(root)).replace("\\", "/"),
        artifact_count=len(findings),
        findings=findings,
        summary=dict(summary),
        by_harness={key: dict(value) for key, value in sorted(by_harness.items())},
        by_status={key: dict(value) for key, value in sorted(by_status.items())},
    )


def render_markdown_report(report: AuditReport) -> str:
    lines = [
        "# Bridge author-metadata audit",
        "",
        f"- generated_at: `{report.generated_at}`",
        f"- bridge_dir: `{report.bridge_dir}`",
        f"- artifact_count: {report.artifact_count}",
        "",
        "## Summary",
        "",
    ]
    for key in sorted(report.summary):
        lines.append(f"- {key}: {report.summary[key]}")
    lines.extend(["", "## Non-compliant artifacts", ""])
    non_compliant = [f for f in report.findings if f.compliance != COMPLIANCE_COMPLIANT]
    if not non_compliant:
        lines.append("_All audited artifacts compliant._")
    else:
        for finding in non_compliant:
            lines.append(
                f"- `{finding.document}` ({finding.path}) status={finding.status} "
                f"compliance={finding.compliance} harness={finding.author_harness_id or 'unknown'}"
            )
    lines.append("")
    return "\n".join(lines)


def write_grandfather_report(project_root: Path, report: AuditReport) -> Path:
    # Canon s17: audit output is session-scoped scratch, never `.gtkb-state`.
    out_dir = project_root / "scratchpad" / session_scratch_dirname() / "bridge-metadata-grandfather-audit"
    out_dir.mkdir(parents=True, exist_ok=True)
    date_stamp = report.generated_at[:10]
    out_path = out_dir / f"grandfather-audit-{date_stamp}.json"
    payload = report.to_dict()
    payload["report_kind"] = "grandfather_audit"
    out_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return out_path


def write_audit_reports(project_root: Path, report: AuditReport, out_dir: Path | None = None) -> tuple[Path, Path]:
    # Canon s17: `out_dir` still overrides; the default is session-scoped scratch.
    report_dir = out_dir or project_root / "scratchpad" / session_scratch_dirname() / "bridge-metadata-audit"
    report_dir.mkdir(parents=True, exist_ok=True)
    safe_stamp = report.generated_at.replace(":", "").replace("-", "").replace("T", "-").rstrip("Z")
    json_path = report_dir / f"bridge-metadata-audit-{safe_stamp}.json"
    markdown_path = report_dir / f"bridge-metadata-audit-{safe_stamp}.md"
    json_path.write_text(json.dumps(report.to_dict(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    markdown_path.write_text(render_markdown_report(report), encoding="utf-8")
    return json_path, markdown_path


def run_cli(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Read-only bridge author-metadata audit scanner.")
    parser.add_argument("--project-root", type=Path, default=Path.cwd())
    parser.add_argument("--bridge-dir", type=Path, default=None)
    parser.add_argument("--json", action="store_true", help="Emit JSON report on stdout.")
    parser.add_argument("--write-report", type=Path, default=None, help="Write markdown report to path.")
    parser.add_argument(
        "--write-state-report",
        action="store_true",
        help="Write JSON and markdown reports under scratchpad/<session>/bridge-metadata-audit/.",
    )
    parser.add_argument(
        "--grandfather-report",
        action="store_true",
        help="Write append-only grandfather audit JSON under scratchpad/<session>/.",
    )
    args = parser.parse_args(argv)

    report = audit_bridge_metadata(args.project_root, bridge_dir=args.bridge_dir)
    state_report_paths: tuple[Path, Path] | None = None
    if args.write_state_report:
        state_report_paths = write_audit_reports(args.project_root.resolve(), report)

    if args.grandfather_report:
        out_path = write_grandfather_report(args.project_root.resolve(), report)
        if args.json:
            payload = report.to_dict()
            payload["grandfather_report_path"] = str(out_path)
            if state_report_paths is not None:
                payload["state_report_paths"] = [str(path) for path in state_report_paths]
            print(json.dumps(payload, indent=2, sort_keys=True))
        else:
            print(out_path)
    elif args.json:
        payload = report.to_dict()
        if state_report_paths is not None:
            payload["state_report_paths"] = [str(path) for path in state_report_paths]
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(render_markdown_report(report))

    if args.write_report is not None:
        args.write_report.parent.mkdir(parents=True, exist_ok=True)
        args.write_report.write_text(render_markdown_report(report), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(run_cli())
