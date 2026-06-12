#!/usr/bin/env python3
"""Bridge INDEX scanner: role-filtered actionable list.

Reads ``bridge/INDEX.md`` and emits a structured summary of which threads need
attention from the calling harness based on its durable operating role.

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
- ``VERIFIED`` is terminal for both roles. ``ADVISORY``, ``DEFERRED``, and
  ``WITHDRAWN`` are non-actionable for both roles. VERIFIED threads are surfaced in
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
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

PROJECT_ROOT = Path(__file__).resolve().parents[4]
DEFAULT_INDEX_PATH = PROJECT_ROOT / "bridge" / "INDEX.md"

Role = Literal["prime-builder", "loyal-opposition"]

PRIME_ACTIONABLE_STATUSES = frozenset({"NO-GO", "GO"})
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
)

# Header read budget (bytes). ``bridge_kind`` is always in the header section.
_HEADER_READ_BUDGET_BYTES = 4096

_STATUS_LINE_RE = re.compile(
    r"^(NEW|REVISED|GO|NO-GO|VERIFIED|WITHDRAWN|ADVISORY|DEFERRED|ACCEPTED|BLOCKED):\s*(bridge/.+\.md)\s*$"
)
_DOCUMENT_LINE_RE = re.compile(r"^Document:\s*(\S+)\s*$")
_BRIDGE_KIND_RE = re.compile(r"^bridge_kind:\s*(\S+)", re.MULTILINE)


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


def _role_filter(
    threads: list[ThreadEntry], role: Role, project_root: Path
) -> tuple[list[ThreadEntry], list[ThreadEntry]]:
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
    for t in threads:
        if t.latest_status not in actionable_statuses:
            continue
        if role == "prime-builder" and t.latest_status == "GO" and _is_terminal_kind_go(t, project_root):
            continue
        actionable.append(t)
    terminal_verified = [t for t in threads if t.latest_status in TERMINAL_STATUSES]
    return actionable, terminal_verified


def _summary_counts(threads: list[ThreadEntry]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for t in threads:
        counts[t.latest_status] = counts.get(t.latest_status, 0) + 1
    return counts


def scan(
    role: Role,
    index_path: Path | None = None,
    *,
    index_text: str | None = None,
) -> dict[str, Any]:
    """Scan bridge/INDEX.md and return role-filtered actionable list.

    Args:
        role: ``"prime-builder"`` or ``"loyal-opposition"``.
        index_path: Path to INDEX.md. Defaults to ``<project-root>/bridge/INDEX.md``.
        index_text: Inline INDEX text (overrides ``index_path``). Useful for tests.

    Returns:
        Dict with keys:
          - ``role``: the role filter applied.
          - ``actionable``: list of thread dicts the role should act on.
          - ``terminal_verified``: list of VERIFIED thread dicts (context only).
          - ``summary``: counts by latest-status across all threads.
          - ``generated_at``: ISO-8601 UTC timestamp.
    """
    if index_text is None:
        path = index_path if index_path is not None else DEFAULT_INDEX_PATH
        index_text = path.read_text(encoding="utf-8")
        project_root = path.resolve().parent.parent
    elif index_path is not None:
        # Inline text but an explicit index path: resolve operative bridge files
        # relative to that path's project root (used by terminal-kind tests).
        project_root = index_path.resolve().parent.parent
    else:
        # Inline text with no path: operative files (if any) resolve under the
        # real project root; absent fixture files fail-open to actionable.
        project_root = PROJECT_ROOT

    threads = _parse_index(index_text)
    actionable, terminal_verified = _role_filter(threads, role, project_root)

    return {
        "role": role,
        "actionable": [t.to_dict() for t in actionable],
        "terminal_verified": [t.to_dict() for t in terminal_verified],
        "summary": _summary_counts(threads),
        "generated_at": _dt.datetime.now(_dt.UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }


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
        "--index-path", default=None, help="Path to bridge/INDEX.md (defaults to project bridge/INDEX.md)"
    )
    parser.add_argument("--format", default="json", choices=["json", "markdown"], help="Output format (default: json)")
    args = parser.parse_args(argv)

    index_path = Path(args.index_path) if args.index_path else None
    result = scan(role=args.role, index_path=index_path)

    if args.format == "json":
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(_format_markdown(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
