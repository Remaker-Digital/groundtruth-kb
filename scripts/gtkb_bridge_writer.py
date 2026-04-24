"""Live-state writer and validator for bridge/INDEX.md and bridge/*.md files.

Enforces the Phase 7 bridge contract: fresh-read live state on every call,
reject stale or cached state, validate role/status transitions with correct
writer authority, compute the next bridge file number from live index plus
disk, write the response file before inserting the status line, and verify
post-write live state.

Contract reference: `.claude/rules/file-bridge-protocol.md`.
Phase 7 planning reference:
`independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-ISOLATION-007-PHASE7-WORK-SUBJECT-ROOT-ENFORCEMENT-PLAN-2026-04-23.md`.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

VALID_STATUSES: frozenset[str] = frozenset({"NEW", "REVISED", "GO", "NO-GO", "VERIFIED"})
PRIME_STATUSES: frozenset[str] = frozenset({"NEW", "REVISED"})
LOYAL_OPPOSITION_STATUSES: frozenset[str] = frozenset({"GO", "NO-GO", "VERIFIED"})

PRIME_ROLE_SLOT = "prime-builder"
LOYAL_OPPOSITION_ROLE_SLOT = "loyal-opposition"

_STATUS_LINE_RE = re.compile(
    r"^(?P<status>NEW|REVISED|GO|NO-GO|VERIFIED):\s+bridge/(?P<filename>[A-Za-z0-9._\-]+)-(?P<version>\d{3,})\.md\s*$"
)
_DOCUMENT_LINE_RE = re.compile(r"^Document:\s+(?P<name>[A-Za-z0-9._\-]+)\s*$")


class BridgeError(Exception):
    """Base class for bridge writer errors."""


class BridgeConflictError(BridgeError):
    """Live index or disk state conflicts with the proposed write."""


class BridgeTransitionError(BridgeError):
    """Proposed status transition is illegal for the given writer role."""


@dataclass(frozen=True)
class BridgeEntry:
    status: str
    filename: str
    version: int


@dataclass(frozen=True)
class DocumentBlock:
    name: str
    entries: tuple[BridgeEntry, ...]

    @property
    def latest_status(self) -> str | None:
        return self.entries[0].status if self.entries else None

    @property
    def latest_version(self) -> int | None:
        return self.entries[0].version if self.entries else None


def _index_path(project_root: Path) -> Path:
    return project_root / "bridge" / "INDEX.md"


def _bridge_dir(project_root: Path) -> Path:
    return project_root / "bridge"


def read_index(project_root: Path) -> tuple[str, tuple[DocumentBlock, ...]]:
    """Read bridge/INDEX.md fresh from disk and parse document blocks.

    Never caches. Every call reads the current on-disk content.
    Returns (raw_text, parsed_blocks).
    """
    raw = _index_path(project_root).read_text(encoding="utf-8")
    return raw, parse_index(raw)


def parse_index(raw: str) -> tuple[DocumentBlock, ...]:
    """Parse INDEX.md content into ordered document blocks.

    A block starts at a `Document: <name>` line and continues through
    consecutive `STATUS: bridge/<name>-NNN.md` lines until the next
    Document line or end of file. Comment and blank lines are skipped.
    """
    blocks: list[DocumentBlock] = []
    current_name: str | None = None
    current_entries: list[BridgeEntry] = []
    for line in raw.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("<!--") or stripped.startswith("#"):
            continue
        doc_match = _DOCUMENT_LINE_RE.match(stripped)
        if doc_match:
            if current_name is not None:
                blocks.append(DocumentBlock(current_name, tuple(current_entries)))
            current_name = doc_match.group("name")
            current_entries = []
            continue
        status_match = _STATUS_LINE_RE.match(stripped)
        if status_match and current_name is not None:
            current_entries.append(
                BridgeEntry(
                    status=status_match.group("status"),
                    filename=f"{status_match.group('filename')}-{status_match.group('version')}.md",
                    version=int(status_match.group("version")),
                )
            )
    if current_name is not None:
        blocks.append(DocumentBlock(current_name, tuple(current_entries)))
    return tuple(blocks)


def get_block(blocks: tuple[DocumentBlock, ...], document_name: str) -> DocumentBlock | None:
    for block in blocks:
        if block.name == document_name:
            return block
    return None


def next_file_number(document_name: str, project_root: Path) -> int:
    """Compute the next bridge file number from live index plus on-disk files.

    Never uses a cached count. Combines the maximum version seen in the live
    INDEX with the maximum version seen on disk under bridge/ for the given
    document slug. Returns that max plus one, or 1 if the document has no
    prior entries anywhere.
    """
    _, blocks = read_index(project_root)
    block = get_block(blocks, document_name)
    max_version = 0
    if block is not None:
        for entry in block.entries:
            if entry.version > max_version:
                max_version = entry.version
    for path in _bridge_dir(project_root).glob(f"{document_name}-*.md"):
        match = re.match(rf"^{re.escape(document_name)}-(\d{{3,}})\.md$", path.name)
        if match:
            version = int(match.group(1))
            if version > max_version:
                max_version = version
    return max_version + 1


def validate_transition(
    document_name: str,
    proposed_status: str,
    role_slot: str,
    project_root: Path,
) -> None:
    """Enforce writer authority and legal status transitions.

    Raises BridgeTransitionError describing which rule was violated.
    """
    if proposed_status not in VALID_STATUSES:
        raise BridgeTransitionError(
            f"invalid status {proposed_status!r}; must be one of {sorted(VALID_STATUSES)}"
        )
    if role_slot == PRIME_ROLE_SLOT and proposed_status not in PRIME_STATUSES:
        raise BridgeTransitionError(
            f"prime-builder may not write {proposed_status!r}; allowed: {sorted(PRIME_STATUSES)}"
        )
    if role_slot == LOYAL_OPPOSITION_ROLE_SLOT and proposed_status not in LOYAL_OPPOSITION_STATUSES:
        raise BridgeTransitionError(
            f"loyal-opposition may not write {proposed_status!r}; allowed: {sorted(LOYAL_OPPOSITION_STATUSES)}"
        )
    if role_slot not in (PRIME_ROLE_SLOT, LOYAL_OPPOSITION_ROLE_SLOT):
        raise BridgeTransitionError(
            f"unknown role_slot {role_slot!r}; expected 'prime-builder' or 'loyal-opposition'"
        )

    _, blocks = read_index(project_root)
    block = get_block(blocks, document_name)
    latest = block.latest_status if block is not None else None

    if latest == "VERIFIED":
        raise BridgeTransitionError(
            f"{document_name}: thread is VERIFIED; no further transitions permitted"
        )

    if proposed_status == "NEW":
        if latest is None:
            return
        if latest == "GO":
            return
        raise BridgeTransitionError(
            f"{document_name}: prime-builder NEW only permitted on new document or after GO (post-impl report); current latest={latest}"
        )

    if proposed_status == "REVISED":
        if latest == "NO-GO":
            return
        raise BridgeTransitionError(
            f"{document_name}: prime-builder REVISED only permitted after NO-GO; current latest={latest}"
        )

    if proposed_status == "GO":
        if latest in ("NEW", "REVISED"):
            return
        raise BridgeTransitionError(
            f"{document_name}: GO only permitted after NEW or REVISED; current latest={latest}"
        )

    if proposed_status == "NO-GO":
        if latest in ("NEW", "REVISED"):
            return
        raise BridgeTransitionError(
            f"{document_name}: NO-GO only permitted after NEW or REVISED; current latest={latest}"
        )

    if proposed_status == "VERIFIED":
        if latest == "NEW":
            return
        raise BridgeTransitionError(
            f"{document_name}: VERIFIED only permitted after post-impl NEW; current latest={latest}"
        )


def write_bridge_file(
    document_name: str,
    version: int,
    content: str,
    project_root: Path,
) -> Path:
    """Write bridge/<document>-<NNN>.md and re-read to verify.

    Raises BridgeConflictError if the file already exists on disk.
    """
    padded = f"{version:03d}"
    target = _bridge_dir(project_root) / f"{document_name}-{padded}.md"
    if target.exists():
        raise BridgeConflictError(f"{target} already exists; refusing to overwrite")
    target.write_text(content, encoding="utf-8")
    written = target.read_text(encoding="utf-8")
    if written != content:
        raise BridgeConflictError(
            f"post-write verification failed for {target}: content on disk differs"
        )
    return target


def insert_index_status(
    document_name: str,
    version: int,
    status: str,
    project_root: Path,
    expected_index_raw: str | None = None,
) -> None:
    """Fresh-read INDEX, insert status line at top of document block, verify.

    If expected_index_raw is supplied and does not match the current on-disk
    INDEX content, raises BridgeConflictError (snapshot is stale).
    """
    if status not in VALID_STATUSES:
        raise BridgeTransitionError(
            f"invalid status {status!r}; must be one of {sorted(VALID_STATUSES)}"
        )
    index_path = _index_path(project_root)
    raw_current = index_path.read_text(encoding="utf-8")
    if expected_index_raw is not None and expected_index_raw != raw_current:
        raise BridgeConflictError(
            "INDEX.md changed between snapshot and write; refusing stale insert"
        )
    new_line = f"{status}: bridge/{document_name}-{version:03d}.md"
    lines = raw_current.splitlines(keepends=True)
    updated: list[str] = []
    inserted = False
    i = 0
    while i < len(lines):
        line = lines[i]
        if not inserted:
            stripped = line.rstrip("\r\n").strip()
            doc_match = _DOCUMENT_LINE_RE.match(stripped)
            if doc_match and doc_match.group("name") == document_name:
                updated.append(line)
                newline_suffix = "\n" if not line.endswith("\r\n") else "\r\n"
                updated.append(new_line + newline_suffix)
                inserted = True
                i += 1
                continue
        updated.append(line)
        i += 1
    if not inserted:
        raise BridgeConflictError(
            f"Document: {document_name} block not found in INDEX.md; cannot insert status"
        )
    new_content = "".join(updated)
    index_path.write_text(new_content, encoding="utf-8")
    verified = index_path.read_text(encoding="utf-8")
    if verified != new_content:
        raise BridgeConflictError("post-write verification failed for INDEX.md")
    _, blocks = read_index(project_root)
    block = get_block(blocks, document_name)
    if block is None or block.latest_status != status or block.latest_version != version:
        raise BridgeConflictError(
            f"post-write live-state verification failed: expected top entry "
            f"{status}:{version:03d} for {document_name}, got "
            f"{block.latest_status if block else None}:{block.latest_version if block else None}"
        )
