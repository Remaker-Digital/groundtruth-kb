#!/usr/bin/env python3
"""Read-only bridge INDEX/file-chain deviation detector.

Detects bridge artifact drift between fresh ``bridge/INDEX.md`` and on-disk
``bridge/*.md`` files. The detector emits correction-packet-ready findings and
does not mutate bridge files or ``bridge/INDEX.md``.
"""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent

STATUS_TOKENS = ("NEW", "REVISED", "GO", "NO-GO", "VERIFIED", "ADVISORY", "WITHDRAWN")
STATUS_LINE_RE = re.compile(r"^(NEW|REVISED|GO|NO-GO|VERIFIED|ADVISORY|WITHDRAWN):\s+(bridge/\S+\.md)\s*$")
VERSIONED_BRIDGE_FILE_RE = re.compile(r"^(.+)-(\d{3})\.md$")
BRIDGE_FILE_REF_RE = re.compile(r"bridge/[A-Za-z0-9_.-]+-\d{3}\.md")


@dataclass(frozen=True)
class BridgeEntry:
    document: str
    status: str
    path: str
    line: int
    version: int | None


@dataclass(frozen=True)
class BridgeFile:
    slug: str
    version: int
    path: Path
    rel_path: str
    first_status: str | None
    document_header: str | None
    responds_to: str | None


def _posix(path: Path) -> str:
    return path.as_posix()


def _rel(root: Path, path: Path) -> str:
    return _posix(path.resolve().relative_to(root.resolve()))


def _version_from_bridge_path(path: str) -> int | None:
    match = VERSIONED_BRIDGE_FILE_RE.match(Path(path).name)
    if not match:
        return None
    return int(match.group(2))


def parse_bridge_index(index_text: str) -> dict[str, list[BridgeEntry]]:
    entries: dict[str, list[BridgeEntry]] = {}
    current_document: str | None = None
    for line_number, raw_line in enumerate(index_text.splitlines(), start=1):
        line = raw_line.strip()
        if line.startswith("Document: "):
            current_document = line.split(": ", 1)[1].strip()
            entries.setdefault(current_document, [])
            continue
        if current_document is None:
            continue
        match = STATUS_LINE_RE.match(line)
        if match:
            path = match.group(2)
            entries[current_document].append(
                BridgeEntry(
                    document=current_document,
                    status=match.group(1),
                    path=path,
                    line=line_number,
                    version=_version_from_bridge_path(path),
                )
            )
    return entries


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(encoding="utf-8", errors="replace")


def _first_status_token(text: str) -> str | None:
    for line in text.splitlines():
        stripped = line.strip()
        if stripped:
            token = stripped.split(maxsplit=1)[0]
            return token if token in STATUS_TOKENS else token
    return None


def _field_value(text: str, field: str) -> str | None:
    prefix = f"{field}:"
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if line.startswith(prefix):
            return line.split(":", 1)[1].strip()
    return None


def _responds_to_path(text: str) -> str | None:
    value = _field_value(text, "Responds to")
    if value is None:
        return None
    match = BRIDGE_FILE_REF_RE.search(value)
    return match.group(0) if match else value


def _scan_bridge_files(root: Path) -> dict[str, dict[int, BridgeFile]]:
    bridge_dir = root / "bridge"
    files: dict[str, dict[int, BridgeFile]] = {}
    if not bridge_dir.exists():
        return files
    for path in sorted(bridge_dir.glob("*.md")):
        if path.name == "INDEX.md":
            continue
        match = VERSIONED_BRIDGE_FILE_RE.match(path.name)
        if not match:
            continue
        text = _read_text(path)
        slug = match.group(1)
        version = int(match.group(2))
        files.setdefault(slug, {})[version] = BridgeFile(
            slug=slug,
            version=version,
            path=path,
            rel_path=_rel(root, path),
            first_status=_first_status_token(text),
            document_header=_field_value(text, "Document"),
            responds_to=_responds_to_path(text),
        )
    return files


def _issue(
    issue_type: str,
    subject: str,
    *,
    evidence: dict[str, Any],
    candidate_repair_actions: list[dict[str, Any]],
    severity: str = "P2",
    risk_notes: list[str] | None = None,
    recommended_action: str,
) -> dict[str, Any]:
    return {
        "class": "bridge_index_chain_deviation",
        "type": issue_type,
        "subject": subject,
        "severity": severity,
        "evidence": evidence,
        "candidate_repair_actions": candidate_repair_actions,
        "risk_notes": risk_notes or [],
        "recommended_action": recommended_action,
    }


def _missing_range(versions: set[int]) -> list[int]:
    if not versions:
        return []
    lower = min(versions)
    upper = max(versions)
    return [version for version in range(lower, upper + 1) if version not in versions]


def _document_chain_issues(
    root: Path,
    document: str,
    rows: list[BridgeEntry],
    files_by_version: dict[int, BridgeFile],
) -> list[dict[str, Any]]:
    issues: list[dict[str, Any]] = []
    seen_versions: dict[int, list[BridgeEntry]] = {}
    seen_paths: dict[str, list[BridgeEntry]] = {}
    for row in rows:
        seen_paths.setdefault(row.path, []).append(row)
        if row.version is not None:
            seen_versions.setdefault(row.version, []).append(row)
        absolute = root / row.path
        if not absolute.exists():
            issues.append(
                _issue(
                    "index_references_missing_file",
                    document,
                    evidence={"index_line": row.line, "path": row.path, "status": row.status},
                    candidate_repair_actions=[
                        {
                            "action": "create_missing_bridge_file_or_remove_index_line",
                            "target_path": row.path,
                            "index_line": row.line,
                        }
                    ],
                    recommended_action="Review whether to restore the file or file a governed INDEX correction.",
                )
            )
            continue
        bridge_file = files_by_version.get(row.version or -1)
        if bridge_file and bridge_file.first_status in STATUS_TOKENS and bridge_file.first_status != row.status:
            issues.append(
                _issue(
                    "index_status_body_mismatch",
                    document,
                    evidence={
                        "index_line": row.line,
                        "path": row.path,
                        "index_status": row.status,
                        "body_status": bridge_file.first_status,
                    },
                    candidate_repair_actions=[
                        {
                            "action": "align_index_status_with_file_or_file_body",
                            "target_path": row.path,
                            "index_line": row.line,
                        }
                    ],
                    recommended_action="File a correction packet that reconciles the INDEX status and file body status.",
                )
            )
        if bridge_file and bridge_file.document_header and bridge_file.document_header != document:
            issues.append(
                _issue(
                    "document_header_mismatch",
                    document,
                    evidence={
                        "index_line": row.line,
                        "path": row.path,
                        "index_document": document,
                        "file_document": bridge_file.document_header,
                    },
                    candidate_repair_actions=[
                        {
                            "action": "correct_document_header_or_index_document",
                            "target_path": row.path,
                            "index_line": row.line,
                        }
                    ],
                    recommended_action="Review the version chain and correct the mismatched document identity.",
                )
            )
    for version, duplicate_rows in sorted(seen_versions.items()):
        if len(duplicate_rows) > 1:
            issues.append(
                _issue(
                    "duplicate_index_version",
                    document,
                    evidence={
                        "version": version,
                        "index_lines": [row.line for row in duplicate_rows],
                        "paths": [row.path for row in duplicate_rows],
                    },
                    candidate_repair_actions=[
                        {
                            "action": "deduplicate_index_version_rows",
                            "version": f"{version:03d}",
                            "index_lines": [row.line for row in duplicate_rows[1:]],
                        }
                    ],
                    recommended_action="File a governed INDEX correction that keeps the valid version row only.",
                )
            )
    for path, duplicate_rows in sorted(seen_paths.items()):
        if len(duplicate_rows) > 1:
            issues.append(
                _issue(
                    "duplicate_index_path",
                    document,
                    evidence={"path": path, "index_lines": [row.line for row in duplicate_rows]},
                    candidate_repair_actions=[
                        {
                            "action": "deduplicate_index_path_rows",
                            "path": path,
                            "index_lines": [row.line for row in duplicate_rows[1:]],
                        }
                    ],
                    recommended_action="File a governed INDEX correction that removes duplicated path rows.",
                )
            )
    indexed_versions = {row.version for row in rows if row.version is not None}
    disk_versions = set(files_by_version)
    missing_versions = _missing_range(indexed_versions | disk_versions)
    if missing_versions:
        issues.append(
            _issue(
                "missing_intermediate_versions",
                document,
                evidence={
                    "indexed_versions": [f"{version:03d}" for version in sorted(indexed_versions)],
                    "disk_versions": [f"{version:03d}" for version in sorted(disk_versions)],
                    "missing_versions": [f"{version:03d}" for version in missing_versions],
                },
                candidate_repair_actions=[
                    {
                        "action": "classify_missing_intermediate_versions",
                        "versions": [f"{version:03d}" for version in missing_versions],
                    }
                ],
                recommended_action="Classify whether each missing version is a real gap, historical pruning, or an INDEX-only defect.",
            )
        )
    index_latest = rows[0] if rows else None
    if index_latest and indexed_versions and index_latest.version != max(indexed_versions):
        issues.append(
            _issue(
                "latest_index_not_highest_indexed_version",
                document,
                evidence={
                    "latest_index_line": index_latest.line,
                    "latest_index_version": f"{index_latest.version:03d}" if index_latest.version else None,
                    "highest_indexed_version": f"{max(indexed_versions):03d}",
                },
                candidate_repair_actions=[
                    {
                        "action": "reorder_document_entry_latest_first",
                        "document": document,
                        "highest_indexed_version": f"{max(indexed_versions):03d}",
                    }
                ],
                recommended_action="Reorder the document entry so the latest version is first.",
            )
        )
    if index_latest and disk_versions and index_latest.version is not None:
        highest_disk_version = max(disk_versions)
        highest_disk_file = files_by_version[highest_disk_version]
        if highest_disk_version > index_latest.version:
            issues.append(
                _issue(
                    "latest_index_omits_highest_file",
                    document,
                    evidence={
                        "latest_index_path": index_latest.path,
                        "latest_index_status": index_latest.status,
                        "highest_disk_path": highest_disk_file.rel_path,
                        "highest_disk_status": highest_disk_file.first_status,
                    },
                    candidate_repair_actions=[
                        {
                            "action": "classify_or_insert_highest_version_index_row",
                            "target_path": highest_disk_file.rel_path,
                            "status": highest_disk_file.first_status,
                        }
                    ],
                    risk_notes=["The highest on-disk file may be a parked draft; do not auto-insert without review."],
                    recommended_action="Classify the highest version file before preparing an INDEX correction packet.",
                )
            )
    for row in rows:
        if row.version is None:
            continue
        bridge_file = files_by_version.get(row.version)
        if bridge_file is None or bridge_file.responds_to is None:
            continue
        expected = f"bridge/{document}-{row.version - 1:03d}.md"
        if row.version > 1 and bridge_file.responds_to != expected:
            issues.append(
                _issue(
                    "responds_to_mismatch",
                    document,
                    evidence={
                        "path": row.path,
                        "index_line": row.line,
                        "responds_to": bridge_file.responds_to,
                        "expected_previous_version": expected,
                    },
                    candidate_repair_actions=[
                        {
                            "action": "review_responds_to_reference",
                            "target_path": row.path,
                            "expected_previous_version": expected,
                        }
                    ],
                    recommended_action="Review the thread chain and correct the verdict/report response reference if needed.",
                )
            )
    return issues


def run_audit(
    *,
    project_root: Path = PROJECT_ROOT,
    bridge_index: Path | None = None,
) -> dict[str, Any]:
    root = project_root.resolve()
    index_path = (bridge_index or root / "bridge" / "INDEX.md").resolve()
    index_text = index_path.read_text(encoding="utf-8")
    entries = parse_bridge_index(index_text)
    bridge_files = _scan_bridge_files(root)
    issues: list[dict[str, Any]] = []
    for document in sorted(entries):
        issues.extend(_document_chain_issues(root, document, entries[document], bridge_files.get(document, {})))
    referenced_paths = {entry.path for rows in entries.values() for entry in rows}
    for slug, versions in sorted(bridge_files.items()):
        for bridge_file in sorted(versions.values(), key=lambda item: item.version):
            if bridge_file.rel_path in referenced_paths:
                continue
            issues.append(
                _issue(
                    "versioned_bridge_file_unindexed",
                    slug,
                    evidence={
                        "path": bridge_file.rel_path,
                        "version": f"{bridge_file.version:03d}",
                        "body_status": bridge_file.first_status,
                    },
                    candidate_repair_actions=[
                        {
                            "action": "classify_unindexed_bridge_file",
                            "target_path": bridge_file.rel_path,
                            "status": bridge_file.first_status,
                        }
                    ],
                    severity="P3",
                    risk_notes=[
                        "Unindexed files may be historical pruned files or parked drafts; classification is required before repair."
                    ],
                    recommended_action="Classify as historical, parked draft, or live INDEX drift before correction.",
                )
            )
    issues.sort(key=lambda row: (row["type"], row["subject"], json.dumps(row["evidence"], sort_keys=True)))
    counts = Counter(row["type"] for row in issues)
    return {
        "schema_version": 1,
        "generated_at": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        "project_root": str(root),
        "bridge_index": str(index_path),
        "source_authority": {
            "bridge": "fresh bridge/INDEX.md plus on-disk bridge files",
            "mutation": "none; read-only audit",
        },
        "bridge_document_count": len(entries),
        "bridge_file_count": sum(len(versions) for versions in bridge_files.values()),
        "issue_count": len(issues),
        "counts_by_type": dict(sorted(counts.items())),
        "issues": issues,
    }


def render_markdown_summary(result: dict[str, Any]) -> str:
    counts = result["counts_by_type"]
    lines = [
        "# Bridge INDEX Chain Audit",
        "",
        f"- generated_at: `{result['generated_at']}`",
        f"- bridge_index: `{result['bridge_index']}`",
        "- source_authority: fresh `bridge/INDEX.md` plus on-disk bridge files",
        "- mutation: none",
        f"- bridge_documents: {result['bridge_document_count']}",
        f"- bridge_files: {result['bridge_file_count']}",
        f"- issues: {result['issue_count']}",
        "",
        "## Counts By Type",
    ]
    if counts:
        lines.extend(f"- {key}: {value}" for key, value in counts.items())
    else:
        lines.append("- none: 0")
    lines.append("")
    lines.append("## Top Issues")
    for issue in result["issues"][:20]:
        lines.append(f"- [{issue['severity']}] {issue['type']}: {issue['subject']}")
    if not result["issues"]:
        lines.append("- none")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", type=Path, default=PROJECT_ROOT)
    parser.add_argument("--bridge-index", type=Path)
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")
    args = parser.parse_args(argv)
    result = run_audit(project_root=args.project_root, bridge_index=args.bridge_index)
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(render_markdown_summary(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
