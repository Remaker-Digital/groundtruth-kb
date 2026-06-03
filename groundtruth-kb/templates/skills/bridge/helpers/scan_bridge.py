#!/usr/bin/env python3
"""Bridge INDEX scanner: role-filtered actionable list.

Reads ``bridge/INDEX.md`` and emits a structured summary of which threads need
attention from the calling harness based on its durable operating role.

Filter rules (per ``.claude/rules/file-bridge-protocol.md``):

- ``prime-builder`` acts on latest ``NO-GO`` (revise) and latest ``GO``
  (implement).
- ``loyal-opposition`` acts on latest ``NEW`` and latest ``REVISED`` (review).
- ``VERIFIED`` is terminal for both roles. VERIFIED threads are surfaced in
  ``terminal_verified`` for context, not in ``actionable``.

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

_STATUS_LINE_RE = re.compile(r"^(NEW|REVISED|GO|NO-GO|VERIFIED|WITHDRAWN|ADVISORY|DEFERRED):\s*(bridge/.+\.md)\s*$")
_DOCUMENT_LINE_RE = re.compile(r"^Document:\s*(\S+)\s*$")


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


def _role_filter(threads: list[ThreadEntry], role: Role) -> tuple[list[ThreadEntry], list[ThreadEntry]]:
    """Return (actionable, terminal_verified) for the given role."""
    if role == "prime-builder":
        actionable_statuses = PRIME_ACTIONABLE_STATUSES
    elif role == "loyal-opposition":
        actionable_statuses = LO_ACTIONABLE_STATUSES
    else:
        raise ValueError(f"Unknown role {role!r}; expected 'prime-builder' or 'loyal-opposition'")

    actionable = [t for t in threads if t.latest_status in actionable_statuses]
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

    threads = _parse_index(index_text)
    actionable, terminal_verified = _role_filter(threads, role)

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
