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

import os
import re
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path

try:
    from scripts.bridge_author_metadata import ensure_author_metadata
    from scripts.bridge_index_writer import atomic_index_update
except ModuleNotFoundError:  # pragma: no cover - direct script execution fallback
    from bridge_author_metadata import ensure_author_metadata
    from bridge_index_writer import atomic_index_update

VALID_STATUSES: frozenset[str] = frozenset({"NEW", "REVISED", "GO", "NO-GO", "VERIFIED", "ADVISORY", "DEFERRED"})
PRIME_STATUSES: frozenset[str] = frozenset({"NEW", "REVISED"})
LOYAL_OPPOSITION_STATUSES: frozenset[str] = frozenset({"GO", "NO-GO", "VERIFIED", "ADVISORY"})

PRIME_ROLE_SLOT = "prime-builder"
LOYAL_OPPOSITION_ROLE_SLOT = "loyal-opposition"

_STATUS_LINE_RE = re.compile(
    r"^(?P<status>NEW|REVISED|GO|NO-GO|VERIFIED|ADVISORY|DEFERRED|WITHDRAWN|ACCEPTED|BLOCKED):\s+"
    r"bridge/(?P<filename>[A-Za-z0-9._\-]+)-(?P<version>\d{3,})\.md\s*$"
)
_DOCUMENT_LINE_RE = re.compile(r"^Document:\s+(?P<name>[A-Za-z0-9._\-]+)\s*$")
_SESSION_METADATA_RE = re.compile(
    r"^(?:author_)?session(?:_context)?_id:\s*(?P<id>\S+)\s*$",
    re.IGNORECASE | re.MULTILINE,
)
_OWNER_DECISIONS_HEADING_RE = re.compile(r"^#{1,6}\s*Owner Decisions(?:\s*/\s*Input)?\s*$", re.IGNORECASE)
_DEFERRED_REASON_RE = re.compile(r"\bdeferr(?:al|ed)\s+reason\b|\breason\s*:", re.IGNORECASE)
_DEFERRED_CLEAR_CONDITION_RE = re.compile(
    r"\bclear\s+condition\b|\bresume\s+condition\b|\bunblock(?:ing)?\s+condition\b|\breactivat(?:e|ion)\b",
    re.IGNORECASE,
)
_DEFERRED_CLEAR_EVIDENCE_RE = re.compile(
    r"\b(?:clear(?:s|ed|ing)?|reactivat(?:es|ed|ing|ion)?|resum(?:es|ed|ing|e)?)\b.{0,80}\b(?:DEFERRED|deferr(?:al|ed))\b"
    r"|\b(?:DEFERRED|deferr(?:al|ed))\b.{0,80}\b(?:clear(?:s|ed|ing)?|reactivat(?:es|ed|ing|ion)?|resum(?:es|ed|ing|e)?)\b",
    re.IGNORECASE,
)
_OWNER_EVIDENCE_RE = re.compile(
    r"\b(?:DELIB-[A-Z0-9_.-]+|AUQ|AskUserQuestion|owner\s+(?:decision|directive|input|approval))\b",
    re.IGNORECASE,
)
_PLACEHOLDER_LINE_RE = re.compile(
    r"^[\s>*`_\-:]*(?:tbd|todo|none|n/a|not applicable|no relevant(?: owner decisions?)?)[\s.`_\-:]*$",
    re.IGNORECASE,
)


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


def _current_session_id(session_id: str | None = None) -> str | None:
    if session_id and session_id.strip():
        return session_id.strip()
    for name in ("GTKB_SESSION_ID", "CLAUDE_SESSION_ID", "CODEX_SESSION_ID"):
        value = os.environ.get(name)
        if value and value.strip():
            return value.strip()
    return None


def _bridge_file_session_id(project_root: Path, entry: BridgeEntry | None) -> str | None:
    if entry is None:
        return None
    path = _bridge_dir(project_root) / entry.filename
    try:
        text = path.read_text(encoding="utf-8")
    except (FileNotFoundError, OSError):
        return None
    match = _SESSION_METADATA_RE.search(text)
    return match.group("id") if match else None


def _reject_same_session_review(
    *,
    proposed_status: str,
    latest_entry: BridgeEntry | None,
    project_root: Path,
    session_id: str | None,
) -> None:
    """Reject LO review writes when author metadata names this same session."""
    if proposed_status not in LOYAL_OPPOSITION_STATUSES or latest_entry is None:
        return
    current_session = _current_session_id(session_id)
    if not current_session:
        return
    author_session = _bridge_file_session_id(project_root, latest_entry)
    if author_session and author_session == current_session:
        raise BridgeTransitionError(
            f"same-session review is forbidden: the latest bridge file was authored by session {author_session!r}"
        )


def _first_nonblank_line(content: str) -> str:
    for line in content.splitlines():
        stripped = line.strip().lstrip("\ufeff")
        if stripped:
            return stripped
    return ""


def _owner_decisions_section_lines(content: str) -> list[str]:
    lines = content.splitlines()
    section: list[str] = []
    in_section = False
    for line in lines:
        stripped = line.strip()
        if _OWNER_DECISIONS_HEADING_RE.match(stripped):
            in_section = True
            continue
        if in_section and stripped.startswith("#"):
            break
        if in_section:
            section.append(line)
    return section


def _validate_deferred_status_content(content: str) -> None:
    if _first_nonblank_line(content) != "DEFERRED":
        raise BridgeTransitionError(
            "DEFERRED INDEX status requires a bridge file whose first non-blank line is DEFERRED"
        )
    if not _DEFERRED_REASON_RE.search(content):
        raise BridgeTransitionError("DEFERRED bridge file must state a deferral reason")
    if not _DEFERRED_CLEAR_CONDITION_RE.search(content):
        raise BridgeTransitionError("DEFERRED bridge file must state a clear/resume condition")

    concrete_lines = [line.strip() for line in _owner_decisions_section_lines(content) if line.strip()]
    if not concrete_lines or not any(not _PLACEHOLDER_LINE_RE.match(line) for line in concrete_lines):
        raise BridgeTransitionError("DEFERRED bridge file must include a concrete Owner Decisions / Input section")
    if not _OWNER_EVIDENCE_RE.search("\n".join(concrete_lines)):
        raise BridgeTransitionError("DEFERRED bridge file must cite owner-decision evidence")


def _validate_deferred_clear_content(content: str) -> None:
    if _first_nonblank_line(content) == "DEFERRED":
        raise BridgeTransitionError("clearing DEFERRED requires a non-DEFERRED bridge status file")

    concrete_lines = [line.strip() for line in _owner_decisions_section_lines(content) if line.strip()]
    section_text = "\n".join(concrete_lines)
    if not concrete_lines or not any(not _PLACEHOLDER_LINE_RE.match(line) for line in concrete_lines):
        raise BridgeTransitionError("clearing DEFERRED requires a concrete Owner Decisions / Input section")
    if not _OWNER_EVIDENCE_RE.search(section_text):
        raise BridgeTransitionError("clearing DEFERRED requires owner-decision evidence")
    if not _DEFERRED_CLEAR_EVIDENCE_RE.search(section_text):
        raise BridgeTransitionError("clearing DEFERRED requires explicit clear/reactivation evidence")


def _validate_deferred_status_file(document_name: str, version: int, project_root: Path) -> None:
    target = _bridge_dir(project_root) / f"{document_name}-{version:03d}.md"
    if not target.is_file():
        raise BridgeTransitionError(f"DEFERRED bridge file does not exist: {target}")
    _validate_deferred_status_content(target.read_text(encoding="utf-8"))


def _validate_deferred_clear_file(document_name: str, version: int, project_root: Path) -> None:
    target = _bridge_dir(project_root) / f"{document_name}-{version:03d}.md"
    if not target.is_file():
        raise BridgeTransitionError(f"DEFERRED clear bridge file does not exist: {target}")
    _validate_deferred_clear_content(target.read_text(encoding="utf-8"))


def validate_transition(
    document_name: str,
    proposed_status: str,
    role_slot: str,
    project_root: Path,
    *,
    session_id: str | None = None,
) -> None:
    """Enforce writer authority and legal status transitions.

    Raises BridgeTransitionError describing which rule was violated.
    """
    if proposed_status not in VALID_STATUSES:
        raise BridgeTransitionError(f"invalid status {proposed_status!r}; must be one of {sorted(VALID_STATUSES)}")
    if role_slot == PRIME_ROLE_SLOT and proposed_status not in PRIME_STATUSES:
        raise BridgeTransitionError(
            f"prime-builder may not write {proposed_status!r}; allowed: {sorted(PRIME_STATUSES)}"
        )
    if role_slot == LOYAL_OPPOSITION_ROLE_SLOT and proposed_status not in LOYAL_OPPOSITION_STATUSES:
        raise BridgeTransitionError(
            f"loyal-opposition may not write {proposed_status!r}; allowed: {sorted(LOYAL_OPPOSITION_STATUSES)}"
        )
    if role_slot not in (PRIME_ROLE_SLOT, LOYAL_OPPOSITION_ROLE_SLOT):
        raise BridgeTransitionError(f"unknown role_slot {role_slot!r}; expected 'prime-builder' or 'loyal-opposition'")

    _, blocks = read_index(project_root)
    block = get_block(blocks, document_name)
    latest = block.latest_status if block is not None else None
    latest_entry = block.entries[0] if block is not None and block.entries else None
    _reject_same_session_review(
        proposed_status=proposed_status,
        latest_entry=latest_entry,
        project_root=project_root,
        session_id=session_id,
    )

    if latest == "VERIFIED":
        raise BridgeTransitionError(f"{document_name}: thread is VERIFIED; no further transitions permitted")

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
        raise BridgeTransitionError(f"{document_name}: GO only permitted after NEW or REVISED; current latest={latest}")

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

    if proposed_status == "ADVISORY":
        if latest is None:
            return
        raise BridgeTransitionError(
            f"{document_name}: ADVISORY only permitted on a new advisory document; current latest={latest}"
        )

    if proposed_status == "DEFERRED":
        raise BridgeTransitionError(
            f"{document_name}: DEFERRED is owner-only and cannot be written by the {role_slot} role transition path"
        )


def write_bridge_file(
    document_name: str,
    version: int,
    content: str,
    project_root: Path,
    *,
    author_metadata: Mapping[str, object] | None = None,
    require_author_metadata: bool = True,
) -> Path:
    """Write bridge/<document>-<NNN>.md and re-read to verify.

    Raises BridgeConflictError if the file already exists on disk.
    """
    padded = f"{version:03d}"
    target = _bridge_dir(project_root) / f"{document_name}-{padded}.md"
    if target.exists():
        raise BridgeConflictError(f"{target} already exists; refusing to overwrite")
    content_to_write = (
        ensure_author_metadata(content, project_root=project_root, explicit=author_metadata)
        if require_author_metadata
        else content
    )
    target.write_text(content_to_write, encoding="utf-8")
    written = target.read_text(encoding="utf-8")
    if written != content_to_write:
        raise BridgeConflictError(f"post-write verification failed for {target}: content on disk differs")
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
        raise BridgeTransitionError(f"invalid status {status!r}; must be one of {sorted(VALID_STATUSES)}")
    if status == "DEFERRED":
        _validate_deferred_status_file(document_name, version, project_root)
    index_path = _index_path(project_root)
    new_line = f"{status}: bridge/{document_name}-{version:03d}.md"

    def latest_tuple(block: DocumentBlock | None) -> tuple[str | None, int | None]:
        return (block.latest_status, block.latest_version) if block is not None else (None, None)

    def mutate(raw_current: str) -> str:
        current_blocks = parse_index(raw_current)
        block = get_block(current_blocks, document_name)
        if expected_index_raw is not None:
            expected_block = get_block(parse_index(expected_index_raw), document_name)
            if latest_tuple(expected_block) != latest_tuple(block):
                raise BridgeConflictError(
                    "INDEX.md target document changed between snapshot and write; refusing stale insert"
                )
        if block is None:
            raise BridgeConflictError(f"Document: {document_name} block not found in INDEX.md; cannot insert status")
        if any(
            entry.filename == f"{document_name}-{version:03d}.md"
            for existing in current_blocks
            for entry in existing.entries
        ):
            raise BridgeConflictError(f"bridge/{document_name}-{version:03d}.md already exists in INDEX.md")
        if block.latest_status == "DEFERRED" and status != "DEFERRED":
            _validate_deferred_clear_file(document_name, version, project_root)

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
            raise BridgeConflictError(f"Document: {document_name} block not found in INDEX.md; cannot insert status")
        return "".join(updated)

    new_content = atomic_index_update(
        index_path,
        mutate,
        state_dir=project_root / ".gtkb-state" / "bridge-index-writer",
    )
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
    # WI-3364: best-effort event-driven bridge/INDEX.md archival trim.
    try:
        import sys as _sys

        _trim_scripts = str(project_root / "scripts")
        if _trim_scripts not in _sys.path:
            _sys.path.insert(0, _trim_scripts)
        from bridge_index_archival import maybe_archive_and_prune_index as _trim

        _trim(project_root, current_thread=document_name)
    except Exception:  # noqa: BLE001 - archival must never fail a bridge write
        pass


def _phantom_backing_files(document_name: str, project_root: Path) -> list[str]:
    """Return the versioned bridge file names that back ``document_name``.

    Only ``bridge/<document_name>-NNN.md`` files (digits immediately after the
    slug) count as backing files. This deliberately excludes longer-named
    siblings that merely share a prefix (e.g. ``foo-bar-001.md`` is not a
    backing file for ``foo``), matching the version-pattern discipline used by
    ``next_file_number``.
    """
    backing: list[str] = []
    for path in _bridge_dir(project_root).glob(f"{document_name}-*.md"):
        if re.match(rf"^{re.escape(document_name)}-\d{{3,}}\.md$", path.name):
            backing.append(path.name)
    return sorted(backing)


def remove_document(document_name: str, project_root: Path) -> None:
    """Remove a phantom ``Document: <name>`` block from bridge/INDEX.md.

    A *phantom* block is an INDEX document entry with NO backing
    ``bridge/<name>-NNN.md`` file on disk. Removal is restricted to phantoms
    to preserve the never-delete-a-real-thread audit invariant: a thread that
    still has versioned files on disk can never be removed from the INDEX by
    this primitive.

    The whole operation runs through the same serialized-writer lock and
    atomic read-modify-write path as ``insert_index_status`` so concurrent
    INDEX mutations can never interleave. The phantom-only guardrail and the
    block removal are evaluated together inside the lock against live disk and
    INDEX state.

    Raises:
        BridgeConflictError: if any ``bridge/<name>-NNN.md`` backing file
            exists (phantom-only guardrail), or if ``document_name`` is absent
            from INDEX.md (explicit not-found; consistent with
            ``insert_index_status``'s block-not-found discipline).
    """
    index_path = _index_path(project_root)

    def mutate(raw_current: str) -> str:
        backing = _phantom_backing_files(document_name, project_root)
        if backing:
            raise BridgeConflictError(
                f"refusing to remove {document_name!r}: backing bridge file(s) exist "
                f"({', '.join(backing)}); only phantom (no-backing-file) entries are removable"
            )
        if get_block(parse_index(raw_current), document_name) is None:
            raise BridgeConflictError(f"Document: {document_name} block not found in INDEX.md; nothing to remove")
        lines = raw_current.splitlines(keepends=True)
        out: list[str] = []
        removed = False
        i = 0
        n = len(lines)
        while i < n:
            stripped = lines[i].rstrip("\r\n").strip()
            doc_match = _DOCUMENT_LINE_RE.match(stripped)
            if not removed and doc_match and doc_match.group("name") == document_name:
                i += 1
                # Drop the block's contiguous status/comment lines.
                while i < n:
                    nxt = lines[i].rstrip("\r\n").strip()
                    if _STATUS_LINE_RE.match(nxt) or nxt.startswith("<!--"):
                        i += 1
                    else:
                        break
                # Drop a single trailing blank separator so blocks do not
                # accumulate double blank lines after removal.
                if i < n and lines[i].strip() == "":
                    i += 1
                removed = True
                continue
            out.append(lines[i])
            i += 1
        if not removed:
            raise BridgeConflictError(f"Document: {document_name} block not found in INDEX.md; nothing to remove")
        return "".join(out)

    new_content = atomic_index_update(
        index_path,
        mutate,
        state_dir=project_root / ".gtkb-state" / "bridge-index-writer",
    )
    verified = index_path.read_text(encoding="utf-8")
    if verified != new_content:
        raise BridgeConflictError("post-write verification failed for INDEX.md")
    _, blocks = read_index(project_root)
    if get_block(blocks, document_name) is not None:
        raise BridgeConflictError(
            f"post-write live-state verification failed: {document_name} still present in INDEX.md"
        )
