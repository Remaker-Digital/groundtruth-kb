#!/usr/bin/env python3
"""Bridge scanner: role-filtered actionable list.

Reads status-bearing versioned bridge files and emits a structured summary of
which threads need attention from the calling harness based on its durable
operating role.

Filter rules (per ``.claude/rules/file-bridge-protocol.md``):

- ``prime-builder`` acts on latest ``NO-GO`` (revise) and latest ``GO``
  (implement) — EXCEPT a latest ``GO`` whose operative Prime proposal carries a
  terminal-kind ``bridge_kind`` (``governance_review``, ``scoping``,
  ``closure``, ...). Such a ``GO`` is the deliverable and has no Prime
  implementation follow-up, so it is excluded from the Prime actionable list.
  A latest ``NO-GO`` always stays Prime-actionable regardless of kind (Prime
  must revise).
- ``loyal-opposition`` acts on latest ``NEW`` and latest ``REVISED`` (review),
  unaffected by terminal-kind classification.
- ``ADVISORY`` is actionable for ``prime-builder`` only (advisory disposition
  requires Prime owner-deliberation/UAQ work); it is non-actionable for
  ``loyal-opposition`` and is non-dispatchable for headless dispatch (see the
  ``_derive_dispatchable`` invariant in ``groundtruth_kb.bridge.notify``).
- ``VERIFIED`` is terminal for both roles. ``DEFERRED`` and ``WITHDRAWN`` are
  non-actionable for both roles. VERIFIED threads are surfaced in
  ``terminal_verified`` for context, not in ``actionable``.

The terminal-kind classification mirrors the canonical dispatchability model in
``groundtruth_kb.bridge.notify`` (``_KIND_TERMINAL_TOKENS`` +
``_derive_dispatchable``: a ``GO`` is dispatchable only when its kind is not
terminal). Parity with the canonical token set is asserted by
``platform_tests/scripts/test_scan_bridge.py``.

The helper performs no mutations and is idempotent. It implements the manual
Scan procedure documented in ``.claude/skills/bridge/SKILL.md``.

CLI usage:

  python .claude/skills/bridge/helpers/scan_bridge.py --role prime-builder [--format json|markdown]

Public API:

  from scan_bridge import scan
  result = scan(role="prime-builder")
"""

from __future__ import annotations

import argparse
import datetime as _dt
import json
import re
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

PROJECT_ROOT = Path(__file__).resolve().parents[4]
DEFAULT_BRIDGE_DIR = PROJECT_ROOT / "bridge"

Role = Literal["prime-builder", "loyal-opposition"]

PRIME_ACTIONABLE_STATUSES = frozenset({"NO-GO", "GO", "ADVISORY"})
LO_ACTIONABLE_STATUSES = frozenset({"NEW", "REVISED"})
TERMINAL_STATUSES = frozenset({"VERIFIED"})

# Prime-authored proposal statuses. ``bridge_kind`` metadata lives on the
# operative Prime proposal (latest NEW/REVISED), NOT on the Codex GO verdict.
_PRIME_VERSION_STATUSES = frozenset({"NEW", "REVISED"})

# Terminal-kind ``bridge_kind`` substring tokens. MIRROR of
# ``groundtruth_kb.bridge.notify._KIND_TERMINAL_TOKENS``. A latest-``GO`` whose
# operative Prime proposal carries one of these tokens is dispatch-terminal: the
# ``GO`` is the deliverable, with no Prime implementation follow-up, so it must
# NOT appear in the Prime actionable list. Kept in sync with the canonical set
# by a parity test in ``platform_tests/scripts/test_scan_bridge.py``.
_KIND_TERMINAL_TOKENS = (
    "scoping",
    "closure",
    "parking",
    "index_reconciliation",
    "thread_reconciliation",
    "operational_state_change",
    "candidate_spec_intake",
    "governance_review",
    "spec_intake",
    "loyal_opposition_advisory",
    "governance_advisory",
    "post_implementation",
    "post_impl",
    "implementation_report",
)

# Header read budget (bytes). ``bridge_kind`` is always in the header section.
_HEADER_READ_BUDGET_BYTES = 4096

_STATUS_LINE_RE = re.compile(
    r"^(NEW|REVISED|GO|NO-GO|NO-ACTION|VERIFIED|WITHDRAWN|ADVISORY|DEFERRED|ACCEPTED|BLOCKED):\s*(bridge/.+\.md)\s*$"
)
_DOCUMENT_LINE_RE = re.compile(r"^Document:\s*(\S+)\s*$")
_BRIDGE_KIND_RE = re.compile(r"^bridge_kind:\s*(\S+)", re.MULTILINE)
_VERSION_FILE_RE = re.compile(r"^(.+)-(\d{3})\.md$")
_WORK_ITEM_VERSION_FILE_RE = re.compile(r"^(?P<slug>.+)-(?P<version>\d{3})\.md$")
_WORK_ITEM_METADATA_LINE_RE = re.compile(
    r"^\s*(?:[-*]\s*)?(?:Work Items?|work_item_ids?|work_item_id)\s*:\s*(?P<value>.+)$",
    re.IGNORECASE,
)
_WORK_ITEM_ID_RE = re.compile(r"\bWI-\d+\b", re.IGNORECASE)
_FILE_STATUS_RE = re.compile(
    r"^[#>*\-\s`]*(NEW|REVISED|GO|NO-GO|NO-ACTION|VERIFIED|WITHDRAWN|ADVISORY|DEFERRED|ACCEPTED|BLOCKED)\b",
    re.IGNORECASE,
)
_TERMINAL_WORK_ITEM_RESOLUTION_STATUSES = frozenset({"verified", "resolved", "retired", "wont_fix", "not_a_defect"})
_WORK_ITEM_HEADER_READ_BUDGET_BYTES = 16_384


@dataclass(frozen=True)
class VersionEntry:
    status: str
    path: str

    def to_dict(self) -> dict[str, str]:
        return {"status": self.status, "path": self.path}


@dataclass(frozen=True)
class ThreadEntry:
    document: str
    latest_status: str
    latest_path: str
    version_chain: tuple[VersionEntry, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "document": self.document,
            "latest_status": self.latest_status,
            "latest_path": self.latest_path,
            "version_chain": [v.to_dict() for v in self.version_chain],
        }


def _parse_index(index_text: str) -> list[ThreadEntry]:
    """Parse INDEX text into ThreadEntry list.

    The INDEX format is:

        Document: <slug>
        <STATUS>: bridge/<file>.md
        <STATUS>: bridge/<file>.md
        ...
        (blank line)
        Document: <next-slug>
        ...

    Latest status is the FIRST status line within a Document block (top of
    the version list). Comment lines starting with ``<!--`` are skipped.
    """
    threads: list[ThreadEntry] = []
    current_doc: str | None = None
    current_versions: list[VersionEntry] = []

    def flush() -> None:
        nonlocal current_doc, current_versions
        if current_doc and current_versions:
            threads.append(
                ThreadEntry(
                    document=current_doc,
                    latest_status=current_versions[0].status,
                    latest_path=current_versions[0].path,
                    version_chain=tuple(current_versions),
                )
            )
        current_doc = None
        current_versions = []

    for raw_line in index_text.splitlines():
        line = raw_line.rstrip()
        if not line:
            flush()
            continue
        stripped = line.strip()
        if stripped.startswith("<!--") or stripped.startswith("#"):
            continue
        m_doc = _DOCUMENT_LINE_RE.match(line)
        if m_doc:
            flush()
            current_doc = m_doc.group(1)
            continue
        m_status = _STATUS_LINE_RE.match(line)
        if m_status and current_doc is not None:
            current_versions.append(VersionEntry(status=m_status.group(1), path=m_status.group(2)))
    flush()
    return threads


def _status_from_bridge_file(path: Path) -> str | None:
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        match = _FILE_STATUS_RE.match(stripped)
        return match.group(1).upper() if match else None
    return None


def _thread_from_rows(slug: str, rows: list[tuple[int, str, str]]) -> ThreadEntry | None:
    ordered = sorted(rows, key=lambda row: row[0], reverse=True)
    versions = tuple(VersionEntry(status=status, path=rel_path) for _version, status, rel_path in ordered)
    if not versions:
        return None
    return ThreadEntry(
        document=slug,
        latest_status=versions[0].status,
        latest_path=versions[0].path,
        version_chain=versions,
    )


def _inventory_version_files(project_root: Path) -> dict[str, list[tuple[int, Path, str]]]:
    """Group numbered files by slug without reading bridge content."""
    bridge_dir = project_root / "bridge"
    grouped: dict[str, list[tuple[int, Path, str]]] = {}
    for path in bridge_dir.glob("*.md"):
        match = _VERSION_FILE_RE.match(path.name)
        if not match:
            continue
        slug = match.group(1)
        version = int(match.group(2))
        try:
            rel_path = path.resolve().relative_to(project_root.resolve()).as_posix()
        except ValueError:
            rel_path = path.as_posix()
        grouped.setdefault(slug, []).append((version, path, rel_path))
    for rows in grouped.values():
        rows.sort(key=lambda row: row[0], reverse=True)
    return grouped


def _scan_rows_from_version_files(project_root: Path) -> dict[str, list[tuple[int, str, str]]]:
    grouped: dict[str, list[tuple[int, str, str]]] = {}
    for slug, version_files in _inventory_version_files(project_root).items():
        for version, path, rel_path in version_files:
            status = _status_from_bridge_file(path)
            if status is not None:
                grouped.setdefault(slug, []).append((version, status, rel_path))
    return grouped


def _compact_thread_from_version_files(
    slug: str,
    version_files: list[tuple[int, Path, str]],
    role: Role,
) -> ThreadEntry | None:
    """Load current status and only ancestry needed for compact classification."""
    versions: list[VersionEntry] = []
    need_prime_ancestry = False
    for _version, path, rel_path in version_files:
        status = _status_from_bridge_file(path)
        if status is None:
            continue
        versions.append(VersionEntry(status=status, path=rel_path))
        if len(versions) == 1:
            need_prime_ancestry = role == "prime-builder" and status == "GO"
            if not need_prime_ancestry:
                break
        elif status in _PRIME_VERSION_STATUSES:
            break
    if not versions:
        return None
    return ThreadEntry(
        document=slug,
        latest_status=versions[0].status,
        latest_path=versions[0].path,
        version_chain=tuple(versions),
    )


def _compact_threads_from_version_files(project_root: Path, role: Role) -> list[ThreadEntry]:
    threads: list[ThreadEntry] = []
    for slug, version_files in _inventory_version_files(project_root).items():
        thread = _compact_thread_from_version_files(slug, version_files, role)
        if thread is not None:
            threads.append(thread)
    return sorted(threads, key=lambda thread: thread.document)


def _render_state_from_version_files(project_root: Path) -> str:
    grouped = _scan_rows_from_version_files(project_root)

    lines: list[str] = []
    for slug in sorted(grouped):
        lines.append(f"Document: {slug}")
        for _version, status, rel_path in sorted(grouped[slug], key=lambda row: row[0], reverse=True):
            lines.append(f"{status}: {rel_path}")
        lines.append("")
    return "\n".join(lines)


def _operative_prime_path(thread: ThreadEntry) -> str | None:
    """Return the path of the operative Prime proposal (latest NEW/REVISED).

    ``version_chain`` is ordered latest-first, so the first NEW/REVISED entry is
    the operative Prime version that carries ``bridge_kind:`` metadata. Returns
    None if the thread has no Prime-authored version (rare).
    """
    for version in thread.version_chain:
        if version.status in _PRIME_VERSION_STATUSES:
            return version.path
    return None


def _is_terminal_kind_go(thread: ThreadEntry, project_root: Path) -> bool:
    """Return True if the thread's latest GO is dispatch-terminal.

    Reads ``bridge_kind:`` from the operative Prime proposal version and matches
    it against ``_KIND_TERMINAL_TOKENS``. Unreadable file, absent operative
    version, or missing ``bridge_kind`` → False (fail-open: keep the GO
    actionable), mirroring the canonical ``ambiguous -> dispatchable`` GO rule in
    ``groundtruth_kb.bridge.notify._derive_dispatchable``.
    """
    rel_path = _operative_prime_path(thread)
    if rel_path is None:
        return False
    full_path = project_root / rel_path
    try:
        with full_path.open("r", encoding="utf-8") as fh:
            head = fh.read(_HEADER_READ_BUDGET_BYTES)
    except (OSError, UnicodeDecodeError):
        return False
    match = _BRIDGE_KIND_RE.search(head)
    if not match:
        return False
    bk_normalized = match.group(1).strip().lower().replace("-", "_")
    return any(token in bk_normalized for token in _KIND_TERMINAL_TOKENS)


def _bridge_version_files_for_thread(project_root: Path, bridge_id: str) -> list[Path]:
    bridge_dir = project_root / "bridge"
    if not bridge_dir.is_dir():
        return []
    versioned: list[tuple[int, Path]] = []
    for path in bridge_dir.glob("*.md"):
        match = _WORK_ITEM_VERSION_FILE_RE.match(path.name)
        if match is None or match.group("slug") != bridge_id:
            continue
        versioned.append((int(match.group("version")), path))
    return [path for _version, path in sorted(versioned, key=lambda row: row[0], reverse=True)]


def _work_item_ids_for_bridge_thread(project_root: Path, bridge_id: str) -> list[str]:
    work_item_ids: list[str] = []
    for path in _bridge_version_files_for_thread(project_root, bridge_id):
        try:
            head = path.read_text(encoding="utf-8", errors="replace")[:_WORK_ITEM_HEADER_READ_BUDGET_BYTES]
        except OSError:
            continue
        for line in head.splitlines():
            match = _WORK_ITEM_METADATA_LINE_RE.match(line)
            if match is None:
                continue
            for raw_work_item_id in _WORK_ITEM_ID_RE.findall(match.group("value")):
                work_item_id = raw_work_item_id.upper()
                if work_item_id not in work_item_ids:
                    work_item_ids.append(work_item_id)
        if work_item_ids:
            return work_item_ids
    return work_item_ids


def _work_item_resolution_status(project_root: Path, work_item_id: str) -> str | None:
    db_path = project_root / "groundtruth.db"
    if not db_path.is_file():
        return None
    try:
        with sqlite3.connect(db_path) as con:
            row = con.execute(
                "SELECT resolution_status FROM current_work_items WHERE id = ? LIMIT 1",
                (work_item_id,),
            ).fetchone()
    except sqlite3.Error:
        return None
    if row is None or row[0] is None:
        return None
    return str(row[0]).strip()


def _terminal_work_item_reason_for_thread(project_root: Path, bridge_id: str) -> str | None:
    work_item_ids = _work_item_ids_for_bridge_thread(project_root, bridge_id)
    if not work_item_ids:
        return None
    terminal: list[tuple[str, str]] = []
    for work_item_id in work_item_ids:
        resolution_status = _work_item_resolution_status(project_root, work_item_id)
        if resolution_status is None:
            return None
        normalized = resolution_status.lower()
        if normalized not in _TERMINAL_WORK_ITEM_RESOLUTION_STATUSES:
            return None
        terminal.append((work_item_id, normalized))
    rendered = ", ".join(f"{work_item_id}={status}" for work_item_id, status in terminal)
    return f"referenced work item terminal ({rendered})"


def _role_filter(
    threads: list[ThreadEntry], role: Role, project_root: Path
) -> tuple[list[ThreadEntry], list[ThreadEntry], list[dict[str, Any]]]:
    """Return (actionable, terminal_verified) for the given role.

    For ``prime-builder``, a latest ``GO`` whose operative Prime proposal carries
    a terminal-kind ``bridge_kind`` is excluded — the GO is the deliverable with
    no Prime implementation follow-up. A latest ``NO-GO`` is never excluded
    (Prime must revise regardless of kind). ``loyal-opposition`` is unaffected.
    """
    if role == "prime-builder":
        actionable_statuses = PRIME_ACTIONABLE_STATUSES
    elif role == "loyal-opposition":
        actionable_statuses = LO_ACTIONABLE_STATUSES
    else:
        raise ValueError(f"Unknown role {role!r}; expected 'prime-builder' or 'loyal-opposition'")

    actionable: list[ThreadEntry] = []
    blocked_non_activatable: list[dict[str, Any]] = []
    for t in threads:
        if t.latest_status not in actionable_statuses:
            continue
        if role == "prime-builder" and t.latest_status == "GO" and _is_terminal_kind_go(t, project_root):
            continue
        if role == "prime-builder" and t.latest_status in {"GO", "NO-GO"}:
            terminal_work_item_reason = _terminal_work_item_reason_for_thread(project_root, t.document)
            if terminal_work_item_reason is not None:
                blocked = t.to_dict()
                blocked["go_file"] = t.latest_path
                blocked["reasons"] = [terminal_work_item_reason]
                blocked_non_activatable.append(blocked)
                continue
        actionable.append(t)
    terminal_verified = [t for t in threads if t.latest_status in TERMINAL_STATUSES]
    return actionable, terminal_verified, blocked_non_activatable


def _summary_counts(threads: list[ThreadEntry]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for t in threads:
        counts[t.latest_status] = counts.get(t.latest_status, 0) + 1
    return counts


def _compact_thread_dict(thread: dict[str, Any]) -> dict[str, Any]:
    """Return current/actionable thread summary without archival version chains."""
    return {key: value for key, value in thread.items() if key != "version_chain"}


def _compact_scan_result(result: dict[str, Any]) -> dict[str, Any]:
    """Suppress terminal VERIFIED payloads; keep current summaries only."""
    compact = dict(result)
    compact["compact"] = True
    compact["actionable"] = [_compact_thread_dict(thread) for thread in result.get("actionable", [])]
    compact["blocked_non_activatable"] = [
        _compact_thread_dict(thread) for thread in result.get("blocked_non_activatable", [])
    ]
    compact["terminal_verified_count"] = len(result.get("terminal_verified", []))
    compact.pop("terminal_verified", None)
    return compact


def scan(
    role: Role,
    index_path: Path | None = None,
    *,
    index_text: str | None = None,
    compact: bool = False,
) -> dict[str, Any]:
    """Scan versioned bridge state and return role-filtered actionable list.

    Args:
        role: ``"prime-builder"`` or ``"loyal-opposition"``.
        index_path: Optional compatibility-text locator used only to infer a
            project root for old test fixtures; live scans do not read it.
        index_text: Inline compatibility-shaped text. Useful for tests.

    Returns:
        Dict with keys:
          - ``role``: the role filter applied.
          - ``actionable``: list of thread dicts the role should act on.
          - ``terminal_verified``: list of VERIFIED thread dicts (context only).
          - ``summary``: counts by latest-status across all threads.
          - ``generated_at``: ISO-8601 UTC timestamp.
    """
    threads: list[ThreadEntry] | None = None
    if index_text is None:
        project_root = index_path.resolve().parent.parent if index_path is not None else PROJECT_ROOT
        if compact:
            threads = _compact_threads_from_version_files(project_root, role)
        else:
            index_text = _render_state_from_version_files(project_root)
    elif index_path is not None:
        # Inline text but an explicit index path: resolve operative bridge files
        # relative to that path's project root (used by terminal-kind tests).
        project_root = index_path.resolve().parent.parent
    else:
        # Inline text with no path: operative files (if any) resolve under the
        # real project root; absent fixture files fail-open to actionable.
        project_root = PROJECT_ROOT

    if threads is None:
        threads = _parse_index(index_text)
    actionable, terminal_verified, blocked_non_activatable = _role_filter(threads, role, project_root)

    result = {
        "role": role,
        "actionable": [t.to_dict() for t in actionable],
        "blocked_non_activatable": blocked_non_activatable,
        "terminal_verified": [t.to_dict() for t in terminal_verified],
        "summary": _summary_counts(threads),
        "generated_at": _dt.datetime.now(_dt.UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    if compact:
        return _compact_scan_result(result)
    return result


def _format_markdown(result: dict[str, Any]) -> str:
    lines: list[str] = []
    lines.append(f"# Bridge Scan ({result['role']})")
    lines.append("")
    lines.append(f"Generated: {result['generated_at']}")
    lines.append("")
    lines.append("## Summary (latest-status counts across all threads)")
    lines.append("")
    if result["summary"]:
        for status, count in sorted(result["summary"].items()):
            lines.append(f"- {status}: {count}")
    else:
        lines.append("- (empty)")
    lines.append("")
    lines.append(f"## Actionable for {result['role']} ({len(result['actionable'])})")
    lines.append("")
    if result["actionable"]:
        for thread in result["actionable"]:
            lines.append(f"- **{thread['document']}** -- {thread['latest_status']} at `{thread['latest_path']}`")
    else:
        lines.append("- (none)")
    lines.append("")
    lines.append(f"## Blocked (non-activatable GO/NO-GO) ({len(result.get('blocked_non_activatable', []))})")
    lines.append("")
    if result.get("blocked_non_activatable"):
        for thread in result["blocked_non_activatable"]:
            lines.append(f"- **{thread['document']}** -- {thread['latest_status']} at `{thread['latest_path']}`")
            for reason in thread.get("reasons", []):
                lines.append(f"  - {reason}")
    else:
        lines.append("- (none)")
    lines.append("")
    if result.get("compact"):
        lines.append(f"## Terminal VERIFIED (count only, {result.get('terminal_verified_count', 0)})")
        lines.append("")
        lines.append("- Full VERIFIED payloads omitted in compact mode; rerun without `--compact` for archival detail.")
    else:
        lines.append(f"## Terminal VERIFIED (context, {len(result['terminal_verified'])})")
        lines.append("")
        if result["terminal_verified"]:
            for thread in result["terminal_verified"]:
                lines.append(f"- {thread['document']} -- VERIFIED at `{thread['latest_path']}`")
        else:
            lines.append("- (none)")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--role", required=True, choices=["prime-builder", "loyal-opposition"])
    parser.add_argument(
        "--index-path", default=None, help="Optional compatibility-state locator used to infer project root"
    )
    parser.add_argument("--format", default="json", choices=["json", "markdown"], help="Output format (default: json)")
    parser.add_argument(
        "--compact",
        action="store_true",
        help="Omit terminal VERIFIED payloads; return current/actionable summaries only",
    )
    args = parser.parse_args(argv)

    index_path = Path(args.index_path) if args.index_path else None
    result = scan(role=args.role, index_path=index_path, compact=args.compact)

    if args.format == "json":
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(_format_markdown(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
