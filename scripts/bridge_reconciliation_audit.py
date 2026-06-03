#!/usr/bin/env python3
"""Read-only bridge/backlog reconciliation audit.

Compares fresh ``bridge/INDEX.md``, on-disk bridge files, and MemBase
``current_work_items`` rows. The audit emits deterministic review findings and
does not mutate bridge, backlog, project, or deliberation state.
"""

from __future__ import annotations

# ruff: noqa: E402,I001

import argparse
import json
import re
import sys
from collections import Counter
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent
GROUNDTRUTH_SRC = PROJECT_ROOT / "groundtruth-kb" / "src"
if str(GROUNDTRUTH_SRC) not in sys.path:
    sys.path.insert(0, str(GROUNDTRUTH_SRC))

from groundtruth_kb.db import KnowledgeDB, WORK_ITEM_TERMINAL_RESOLUTION_STATUSES

STATUS_TOKENS = ("NEW", "REVISED", "GO", "NO-GO", "VERIFIED", "ADVISORY", "DEFERRED", "WITHDRAWN")
STATUS_LINE_RE = re.compile(r"^(NEW|REVISED|GO|NO-GO|VERIFIED|ADVISORY|DEFERRED|WITHDRAWN):\s+(bridge/\S+\.md)\s*$")
VERSIONED_BRIDGE_FILE_RE = re.compile(r"^(.+)-(\d{3})\.md$")
BRIDGE_PATH_RE = re.compile(r"(?:^|\b)bridge/([A-Za-z0-9_.-]+?)-\d{3}\.md(?:\b|$)")
WI_ID_RE = re.compile(r"(?<![A-Za-z0-9_.-])WI-\d+(?![A-Za-z0-9_.-])")
TOKEN_SPLIT_RE = re.compile(r"[,;\r\n]+")


@dataclass(frozen=True)
class BridgeEntry:
    document: str
    status: str
    path: str
    line: int


def _posix(path: Path) -> str:
    return path.as_posix()


def _rel(root: Path, path: Path) -> str:
    return _posix(path.resolve().relative_to(root.resolve()))


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
            entries[current_document].append(
                BridgeEntry(
                    document=current_document,
                    status=match.group(1),
                    path=match.group(2),
                    line=line_number,
                )
            )
    return entries


def latest_bridge_statuses(entries: dict[str, list[BridgeEntry]]) -> dict[str, BridgeEntry]:
    return {document: rows[0] for document, rows in entries.items() if rows}


def _first_status_token(path: Path) -> str | None:
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        text = path.read_text(encoding="utf-8", errors="replace")
    for line in text.splitlines():
        stripped = line.strip()
        if stripped:
            return stripped.split(maxsplit=1)[0]
    return None


def _extract_wi_ids(path: Path) -> list[str]:
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        text = path.read_text(encoding="utf-8", errors="replace")
    return sorted(set(WI_ID_RE.findall(text)))


def _bridge_thread_files(root: Path, slug: str) -> list[Path]:
    return sorted((root / "bridge").glob(f"{slug}-*.md"))


def _flatten_related_value(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        stripped = value.strip()
        if not stripped:
            return []
        try:
            decoded = json.loads(stripped)
        except json.JSONDecodeError:
            decoded = None
        if isinstance(decoded, (list, tuple)):
            return _flatten_related_value(decoded)
        if isinstance(decoded, str) and decoded != value:
            return _flatten_related_value(decoded)
        paths = [match.group(0).strip() for match in BRIDGE_PATH_RE.finditer(stripped)]
        if paths:
            remainder = BRIDGE_PATH_RE.sub(" ", stripped)
            return paths + [token for token in TOKEN_SPLIT_RE.split(remainder) if token]
        return [token for token in TOKEN_SPLIT_RE.split(stripped) if token]
    if isinstance(value, (list, tuple, set)):
        tokens: list[str] = []
        for item in value:
            tokens.extend(_flatten_related_value(item))
        return tokens
    return []


def normalize_bridge_reference(token: str) -> str | None:
    cleaned = token.strip().strip("`'\"")
    if not cleaned:
        return None
    path_match = BRIDGE_PATH_RE.search(cleaned)
    if path_match:
        return path_match.group(1)
    if cleaned.startswith("bridge/"):
        cleaned = cleaned.removeprefix("bridge/")
    versioned_match = VERSIONED_BRIDGE_FILE_RE.match(cleaned)
    if versioned_match:
        return versioned_match.group(1)
    if cleaned.endswith(".md"):
        return None
    if "/" in cleaned or "\\" in cleaned:
        return None
    if re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]*", cleaned):
        return cleaned
    return None


def parse_related_bridge_threads(value: Any) -> list[str]:
    slugs: list[str] = []
    seen: set[str] = set()
    for token in _flatten_related_value(value):
        slug = normalize_bridge_reference(token)
        if slug and slug not in seen:
            slugs.append(slug)
            seen.add(slug)
    return slugs


def _thread_mentions_work_item(root: Path, slug: str, work_item_id: str) -> bool:
    pattern = re.compile(rf"(?<![A-Za-z0-9_.-]){re.escape(work_item_id)}(?![A-Za-z0-9_.-])")
    for path in _bridge_thread_files(root, slug):
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            text = path.read_text(encoding="utf-8", errors="replace")
        if pattern.search(text):
            return True
    return False


def _thread_wi_ids(root: Path, slug: str) -> list[str]:
    ids: set[str] = set()
    for path in _bridge_thread_files(root, slug):
        ids.update(_extract_wi_ids(path))
    return sorted(ids)


def _issue(
    issue_class: str,
    issue_type: str,
    subject: str,
    *,
    evidence: dict[str, Any],
    severity: str = "P2",
    recommended_action: str,
) -> dict[str, Any]:
    return {
        "class": issue_class,
        "type": issue_type,
        "subject": subject,
        "severity": severity,
        "evidence": evidence,
        "recommended_action": recommended_action,
    }


def _bridge_index_drift_issues(root: Path, entries: dict[str, list[BridgeEntry]]) -> list[dict[str, Any]]:
    issues: list[dict[str, Any]] = []
    referenced_paths = {entry.path for rows in entries.values() for entry in rows}
    for rows in entries.values():
        for entry in rows:
            absolute = root / entry.path
            if not absolute.exists():
                issues.append(
                    _issue(
                        "bridge_index_drift",
                        "index_references_missing_file",
                        entry.document,
                        evidence={"index_line": entry.line, "path": entry.path, "status": entry.status},
                        recommended_action="Add the missing bridge file or file a governed INDEX correction.",
                    )
                )
                continue
            token = _first_status_token(absolute)
            if token and token in STATUS_TOKENS and token != entry.status:
                issues.append(
                    _issue(
                        "bridge_index_drift",
                        "index_status_body_mismatch",
                        entry.document,
                        evidence={
                            "index_line": entry.line,
                            "path": entry.path,
                            "index_status": entry.status,
                            "body_status": token,
                        },
                        recommended_action="Review the version chain and file a governed INDEX correction.",
                    )
                )
    bridge_dir = root / "bridge"
    if bridge_dir.exists():
        for path in sorted(bridge_dir.glob("*.md")):
            rel_path = _rel(root, path)
            if rel_path == "bridge/INDEX.md" or rel_path in referenced_paths:
                continue
            if VERSIONED_BRIDGE_FILE_RE.match(path.name):
                issues.append(
                    _issue(
                        "bridge_index_drift",
                        "versioned_bridge_file_unindexed",
                        path.stem,
                        evidence={"path": rel_path},
                        severity="P3",
                        recommended_action="Decide whether this is a parked draft or needs a governed INDEX entry.",
                    )
                )
    return issues


def _work_item_linkage_issues(
    root: Path,
    work_items: list[dict[str, Any]],
    latest: dict[str, BridgeEntry],
) -> list[dict[str, Any]]:
    issues: list[dict[str, Any]] = []
    for item in sorted(work_items, key=lambda row: str(row.get("id") or "")):
        item_id = str(item.get("id") or "")
        links = parse_related_bridge_threads(
            item.get("related_bridge_threads_parsed", item.get("related_bridge_threads"))
        )
        if not links:
            continue
        missing = [slug for slug in links if slug not in latest]
        if missing:
            issues.append(
                _issue(
                    "missing_or_incorrect_related_bridge_threads",
                    "related_bridge_thread_missing_from_index",
                    item_id,
                    evidence={
                        "priority": item.get("priority"),
                        "missing_bridge_threads": missing,
                        "related_bridge_threads": links,
                    },
                    recommended_action="Correct related_bridge_threads or file a bridge INDEX repair packet.",
                )
            )
        incorrect = [
            slug
            for slug in links
            if slug in latest
            and latest[slug].status == "VERIFIED"
            and not _thread_mentions_work_item(root, slug, item_id)
        ]
        if incorrect:
            issues.append(
                _issue(
                    "missing_or_incorrect_related_bridge_threads",
                    "verified_related_bridge_lacks_work_item_evidence",
                    item_id,
                    evidence={
                        "priority": item.get("priority"),
                        "incorrect_bridge_threads": incorrect,
                        "related_bridge_threads": links,
                    },
                    recommended_action="Repair the linkage or leave the work item active until explicit evidence exists.",
                )
            )
    return issues


def _stale_backlog_issues(
    root: Path,
    work_items: list[dict[str, Any]],
    latest: dict[str, BridgeEntry],
) -> list[dict[str, Any]]:
    issues: list[dict[str, Any]] = []
    terminal = set(WORK_ITEM_TERMINAL_RESOLUTION_STATUSES)
    for item in sorted(work_items, key=lambda row: str(row.get("id") or "")):
        item_id = str(item.get("id") or "")
        if item.get("resolution_status") in terminal:
            continue
        links = parse_related_bridge_threads(
            item.get("related_bridge_threads_parsed", item.get("related_bridge_threads"))
        )
        if not links or any(slug not in latest for slug in links):
            continue
        statuses = {slug: latest[slug].status for slug in links}
        if all(status == "VERIFIED" for status in statuses.values()) and all(
            _thread_mentions_work_item(root, slug, item_id) for slug in links
        ):
            issues.append(
                _issue(
                    "stale_backlog_status",
                    "nonterminal_work_item_all_related_threads_verified",
                    item_id,
                    evidence={
                        "priority": item.get("priority"),
                        "resolution_status": item.get("resolution_status"),
                        "stage": item.get("stage"),
                        "related_bridge_threads": links,
                        "related_bridge_statuses": statuses,
                    },
                    recommended_action="Review for terminal backlog update through the governed correction flow.",
                )
            )
    return issues


def _terminal_without_evidence_issues(
    root: Path,
    work_items: list[dict[str, Any]],
    latest: dict[str, BridgeEntry],
) -> list[dict[str, Any]]:
    issues: list[dict[str, Any]] = []
    terminal = set(WORK_ITEM_TERMINAL_RESOLUTION_STATUSES)
    for item in sorted(work_items, key=lambda row: str(row.get("id") or "")):
        item_id = str(item.get("id") or "")
        if item.get("resolution_status") not in terminal:
            continue
        links = parse_related_bridge_threads(
            item.get("related_bridge_threads_parsed", item.get("related_bridge_threads"))
        )
        completion_evidence = str(item.get("completion_evidence") or "").strip()
        verified_links_with_parent = [
            slug
            for slug in links
            if slug in latest and latest[slug].status == "VERIFIED" and _thread_mentions_work_item(root, slug, item_id)
        ]
        if not completion_evidence or (links and not verified_links_with_parent):
            issues.append(
                _issue(
                    "terminal_backlog_without_evidence",
                    "terminal_work_item_lacks_verifiable_bridge_evidence",
                    item_id,
                    evidence={
                        "priority": item.get("priority"),
                        "resolution_status": item.get("resolution_status"),
                        "stage": item.get("stage"),
                        "has_completion_evidence": bool(completion_evidence),
                        "related_bridge_threads": links,
                        "verified_links_with_parent_evidence": verified_links_with_parent,
                    },
                    recommended_action="Reopen or attach governed completion evidence through a correction packet.",
                )
            )
    return issues


def _verified_bridge_backlog_issues(
    root: Path,
    work_items: list[dict[str, Any]],
    latest: dict[str, BridgeEntry],
) -> list[dict[str, Any]]:
    issues: list[dict[str, Any]] = []
    terminal = set(WORK_ITEM_TERMINAL_RESOLUTION_STATUSES)
    work_by_id = {str(item.get("id")): item for item in work_items}
    for slug, entry in sorted(latest.items()):
        if entry.status != "VERIFIED":
            continue
        wi_ids = _thread_wi_ids(root, slug)
        if not wi_ids:
            issues.append(
                _issue(
                    "verified_bridge_without_backlog_match",
                    "verified_bridge_thread_has_no_work_item_evidence",
                    slug,
                    evidence={"bridge_thread": slug, "latest_path": entry.path},
                    severity="P3",
                    recommended_action="Classify as intentionally unlinked or file a backlog linkage packet.",
                )
            )
            continue
        unmatched = [wi_id for wi_id in wi_ids if wi_id not in work_by_id]
        if unmatched:
            issues.append(
                _issue(
                    "verified_bridge_without_backlog_match",
                    "verified_bridge_work_item_id_missing_from_membase",
                    slug,
                    evidence={"bridge_thread": slug, "work_item_ids": unmatched, "latest_path": entry.path},
                    recommended_action="Create or correct the MemBase backlog linkage through governed intake.",
                )
            )
        for wi_id in wi_ids:
            item = work_by_id.get(wi_id)
            if item is None:
                continue
            if item.get("resolution_status") not in terminal:
                issues.append(
                    _issue(
                        "verified_bridge_missing_terminal_backlog_state",
                        "verified_bridge_points_to_nonterminal_work_item",
                        slug,
                        evidence={
                            "bridge_thread": slug,
                            "work_item_id": wi_id,
                            "priority": item.get("priority"),
                            "resolution_status": item.get("resolution_status"),
                            "stage": item.get("stage"),
                        },
                        recommended_action="Review for terminal backlog update through the governed correction flow.",
                    )
                )
    return issues


def run_audit(
    *,
    project_root: Path = PROJECT_ROOT,
    db_path: Path | None = None,
    bridge_index: Path | None = None,
) -> dict[str, Any]:
    root = project_root.resolve()
    index_path = (bridge_index or root / "bridge" / "INDEX.md").resolve()
    database_path = (db_path or root / "groundtruth.db").resolve()
    index_text = index_path.read_text(encoding="utf-8")
    entries = parse_bridge_index(index_text)
    latest = latest_bridge_statuses(entries)
    db = KnowledgeDB(database_path)
    try:
        work_items = db.list_work_items()
    finally:
        db.close()

    issues: list[dict[str, Any]] = []
    issues.extend(_bridge_index_drift_issues(root, entries))
    issues.extend(_work_item_linkage_issues(root, work_items, latest))
    issues.extend(_stale_backlog_issues(root, work_items, latest))
    issues.extend(_terminal_without_evidence_issues(root, work_items, latest))
    issues.extend(_verified_bridge_backlog_issues(root, work_items, latest))
    issues.sort(key=lambda row: (row["class"], row["subject"], row["type"]))
    counts = Counter(row["class"] for row in issues)
    return {
        "schema_version": 1,
        "generated_at": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        "project_root": str(root),
        "db_path": str(database_path),
        "bridge_index": str(index_path),
        "source_authority": {
            "bridge": "fresh bridge/INDEX.md plus on-disk bridge files",
            "backlog": "fresh MemBase current_work_items",
            "mutation": "none; read-only audit",
        },
        "bridge_document_count": len(latest),
        "work_item_count": len(work_items),
        "issue_count": len(issues),
        "counts_by_class": dict(sorted(counts.items())),
        "issues": issues,
    }


def render_markdown_summary(result: dict[str, Any]) -> str:
    counts = result["counts_by_class"]
    lines = [
        "# Bridge Reconciliation Audit",
        "",
        f"- generated_at: `{result['generated_at']}`",
        f"- bridge_index: `{result['bridge_index']}`",
        f"- db_path: `{result['db_path']}`",
        "- source_authority: fresh `bridge/INDEX.md`, on-disk bridge files, and MemBase `current_work_items`",
        "- mutation: none",
        f"- bridge_documents: {result['bridge_document_count']}",
        f"- work_items: {result['work_item_count']}",
        f"- issues: {result['issue_count']}",
        "",
        "## Counts By Class",
    ]
    if counts:
        lines.extend(f"- {key}: {value}" for key, value in counts.items())
    else:
        lines.append("- none: 0")
    lines.append("")
    lines.append("## Top Issues")
    for issue in result["issues"][:20]:
        lines.append(f"- [{issue['severity']}] {issue['class']} / {issue['type']}: {issue['subject']}")
    if not result["issues"]:
        lines.append("- none")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", type=Path, default=PROJECT_ROOT)
    parser.add_argument("--db-path", type=Path)
    parser.add_argument("--bridge-index", type=Path)
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")
    args = parser.parse_args(argv)
    result = run_audit(project_root=args.project_root, db_path=args.db_path, bridge_index=args.bridge_index)
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(render_markdown_summary(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
