"""Serialized bridge INDEX mutation helpers.

This module is the package API behind ``gt bridge index``. It validates bridge
document names, status tokens, and versioned bridge paths, then performs the
live ``bridge/INDEX.md`` mutation through the existing standalone
``scripts/bridge_index_writer.py`` lock/atomic-write primitive.
"""

from __future__ import annotations

import importlib.util
import sys
from collections import Counter
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from re import IGNORECASE
from re import compile as re_compile
from types import ModuleType
from typing import Any, cast

from groundtruth_kb.bridge.detector import BridgeStatus, parse_index

_SLUG_RE = re_compile(r"^[a-z0-9][a-z0-9-]*[a-z0-9]$")
_BRIDGE_PATH_RE = re_compile(r"^bridge/(?P<slug>[a-z0-9][a-z0-9-]*[a-z0-9])-(?P<version>\d{3})\.md$")
_OWNER_DECISIONS_HEADING_RE = re_compile(r"^#{1,6}\s*Owner Decisions(?:\s*/\s*Input)?\s*$", IGNORECASE)
_DEFERRED_REASON_RE = re_compile(r"\bdeferr(?:al|ed)\s+reason\b|\breason\s*:", IGNORECASE)
_DEFERRED_CLEAR_CONDITION_RE = re_compile(
    r"\bclear\s+condition\b|\bresume\s+condition\b|\bunblock(?:ing)?\s+condition\b|\breactivat(?:e|ion)\b",
    IGNORECASE,
)
_DEFERRED_CLEAR_EVIDENCE_RE = re_compile(
    r"\b(?:clear(?:s|ed|ing)?|reactivat(?:es|ed|ing|ion)?|resum(?:es|ed|ing|e)?)\b.{0,80}\b(?:DEFERRED|deferr(?:al|ed))\b"
    r"|\b(?:DEFERRED|deferr(?:al|ed))\b.{0,80}\b(?:clear(?:s|ed|ing)?|reactivat(?:es|ed|ing|ion)?|resum(?:es|ed|ing|e)?)\b",
    IGNORECASE,
)
_OWNER_EVIDENCE_RE = re_compile(
    r"\b(?:DELIB-[A-Z0-9_.-]+|AUQ|AskUserQuestion|owner\s+(?:decision|directive|input|approval))\b",
    IGNORECASE,
)
_PLACEHOLDER_LINE_RE = re_compile(
    r"^[\s>*`_\-:]*(?:tbd|todo|none|n/a|not applicable|no relevant(?: owner decisions?)?)[\s.`_\-:]*$",
    IGNORECASE,
)
_ALLOWED_MUTATION_STATUSES = frozenset(
    {
        BridgeStatus.NEW,
        BridgeStatus.REVISED,
        BridgeStatus.GO,
        BridgeStatus.NO_GO,
        BridgeStatus.VERIFIED,
        BridgeStatus.WITHDRAWN,
        BridgeStatus.ADVISORY,
        BridgeStatus.DEFERRED,
    }
)


class BridgeIndexMutationError(ValueError):
    """Raised when a bridge INDEX mutation is invalid or cannot be serialized."""


@dataclass(frozen=True)
class BridgeIndexMutationResult:
    """Result returned by successful serialized bridge INDEX mutations."""

    document: str
    status: str
    path: str
    index_path: Path
    written_text: str

    def to_json_dict(self) -> dict[str, str]:
        """Return a stable JSON-safe payload for CLI callers."""
        return {
            "document": self.document,
            "status": self.status,
            "path": self.path,
            "index_path": str(self.index_path),
        }


def validate_document_slug(slug: str) -> str:
    """Validate and return a bridge document slug."""
    if not _SLUG_RE.fullmatch(slug):
        raise BridgeIndexMutationError("document slug must be lowercase kebab-case using only a-z, 0-9, and hyphens")
    return slug


def validate_status(status: str) -> BridgeStatus:
    """Validate and return a mutable bridge INDEX status."""
    try:
        parsed = BridgeStatus(status)
    except ValueError as exc:
        raise BridgeIndexMutationError(f"unknown bridge status: {status}") from exc
    if parsed not in _ALLOWED_MUTATION_STATUSES:
        raise BridgeIndexMutationError(f"bridge status is not accepted for INDEX mutation: {status}")
    return parsed


def validate_bridge_path(document_slug: str, bridge_path: str) -> str:
    """Validate and return ``bridge/<document-slug>-NNN.md``."""
    validate_document_slug(document_slug)
    path = Path(bridge_path)
    if path.is_absolute():
        raise BridgeIndexMutationError("bridge path must be relative")
    if "\\" in bridge_path:
        raise BridgeIndexMutationError("bridge path must use forward slashes")
    if ".." in Path(bridge_path).parts:
        raise BridgeIndexMutationError("bridge path must not contain '..'")
    match = _BRIDGE_PATH_RE.fullmatch(bridge_path)
    if not match:
        raise BridgeIndexMutationError("bridge path must match bridge/<document-slug>-NNN.md")
    if match.group("slug") != document_slug:
        raise BridgeIndexMutationError("bridge path slug does not match document slug")
    return bridge_path


def validate_deferred_status_content(content: str) -> None:
    """Validate owner evidence required for a DEFERRED bridge status file."""
    first_line = next((line.strip().lstrip("\ufeff") for line in content.splitlines() if line.strip()), "")
    if first_line != BridgeStatus.DEFERRED.value:
        raise BridgeIndexMutationError(
            "DEFERRED INDEX status requires a bridge file whose first non-blank line is DEFERRED"
        )
    if not _DEFERRED_REASON_RE.search(content):
        raise BridgeIndexMutationError("DEFERRED bridge file must state a deferral reason")
    if not _DEFERRED_CLEAR_CONDITION_RE.search(content):
        raise BridgeIndexMutationError("DEFERRED bridge file must state a clear/resume condition")

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
    concrete_lines = [line.strip() for line in section if line.strip()]
    if not concrete_lines or not any(not _PLACEHOLDER_LINE_RE.match(line) for line in concrete_lines):
        raise BridgeIndexMutationError("DEFERRED bridge file must include a concrete Owner Decisions / Input section")
    if not _OWNER_EVIDENCE_RE.search("\n".join(concrete_lines)):
        raise BridgeIndexMutationError("DEFERRED bridge file must cite owner-decision evidence")


def validate_deferred_clear_content(content: str) -> None:
    """Validate owner evidence required to clear a latest DEFERRED status."""
    first_line = next((line.strip().lstrip("\ufeff") for line in content.splitlines() if line.strip()), "")
    if first_line == BridgeStatus.DEFERRED.value:
        raise BridgeIndexMutationError("clearing DEFERRED requires a non-DEFERRED bridge status file")

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
    concrete_lines = [line.strip() for line in section if line.strip()]
    section_text = "\n".join(concrete_lines)
    if not concrete_lines or not any(not _PLACEHOLDER_LINE_RE.match(line) for line in concrete_lines):
        raise BridgeIndexMutationError("clearing DEFERRED requires a concrete Owner Decisions / Input section")
    if not _OWNER_EVIDENCE_RE.search(section_text):
        raise BridgeIndexMutationError("clearing DEFERRED requires owner-decision evidence")
    if not _DEFERRED_CLEAR_EVIDENCE_RE.search(section_text):
        raise BridgeIndexMutationError("clearing DEFERRED requires explicit clear/reactivation evidence")


def validate_deferred_status_file(project_root: Path, bridge_path: str) -> None:
    """Validate the owner-only evidence carried by a DEFERRED bridge file."""
    target = project_root / bridge_path
    if not target.is_file():
        raise BridgeIndexMutationError(f"DEFERRED bridge file does not exist: {bridge_path}")
    try:
        content = target.read_text(encoding="utf-8")
    except OSError as exc:
        raise BridgeIndexMutationError(f"cannot read DEFERRED bridge file {bridge_path}: {exc}") from exc
    validate_deferred_status_content(content)


def validate_deferred_clear_file(project_root: Path, bridge_path: str) -> None:
    """Validate the owner-only evidence carried by a file that clears DEFERRED."""
    target = project_root / bridge_path
    if not target.is_file():
        raise BridgeIndexMutationError(f"DEFERRED clear bridge file does not exist: {bridge_path}")
    try:
        content = target.read_text(encoding="utf-8")
    except OSError as exc:
        raise BridgeIndexMutationError(f"cannot read DEFERRED clear bridge file {bridge_path}: {exc}") from exc
    validate_deferred_clear_content(content)


def add_document_to_index_text(index_text: str, document_slug: str, status: str, bridge_path: str) -> str:
    """Return INDEX text with a new document block inserted at the top."""
    document_slug = validate_document_slug(document_slug)
    parsed_status = validate_status(status)
    bridge_path = validate_bridge_path(document_slug, bridge_path)
    _require_index_text(index_text)
    documents = _parse_documents_or_raise(index_text)
    _raise_on_duplicate_documents(documents)
    if any(document.name == document_slug for document in documents):
        raise BridgeIndexMutationError(f"document already exists in bridge INDEX: {document_slug}")
    if any(version.file_path == bridge_path for document in documents for version in document.versions):
        raise BridgeIndexMutationError(f"bridge path already exists in bridge INDEX: {bridge_path}")

    lines, newline = _split_index_text(index_text)
    insert_at = _first_document_line_index(lines)
    status_line = f"{parsed_status.value}: {bridge_path}"
    block = [f"Document: {document_slug}", status_line, ""]
    if insert_at is None:
        prefix = list(lines)
        if prefix and prefix[-1] != "":
            prefix.append("")
        return _join_index_lines(prefix + block, newline)
    prefix = list(lines[:insert_at])
    if prefix and prefix[-1] != "":
        prefix.append("")
    return _join_index_lines(prefix + block + lines[insert_at:], newline)


def set_status_in_index_text(index_text: str, document_slug: str, status: str, bridge_path: str) -> str:
    """Return INDEX text with a status line prepended to an existing document."""
    document_slug = validate_document_slug(document_slug)
    parsed_status = validate_status(status)
    bridge_path = validate_bridge_path(document_slug, bridge_path)
    _require_index_text(index_text)
    documents = _parse_documents_or_raise(index_text)
    _raise_on_duplicate_documents(documents)
    matching = [document for document in documents if document.name == document_slug]
    if not matching:
        raise BridgeIndexMutationError(f"document does not exist in bridge INDEX: {document_slug}")
    document = matching[0]
    if any(version.file_path == bridge_path for version in document.versions):
        raise BridgeIndexMutationError(f"bridge path already exists for document {document_slug}: {bridge_path}")

    lines, newline = _split_index_text(index_text)
    status_line = f"{parsed_status.value}: {bridge_path}"
    insert_at = document.line_number
    return _join_index_lines(lines[:insert_at] + [status_line] + lines[insert_at:], newline)


def add_document(
    project_root: str | Path,
    document_slug: str,
    *,
    status: str = "NEW",
    bridge_path: str,
    timeout_seconds: float = 10.0,
) -> BridgeIndexMutationResult:
    """Serialize adding a new document block to ``bridge/INDEX.md``."""
    project_root = Path(project_root)
    index_path = _require_index_path(project_root)
    writer = _load_index_writer(project_root)
    parsed_status = validate_status(status)
    if parsed_status is BridgeStatus.DEFERRED:
        validate_deferred_status_file(project_root, bridge_path)

    def mutate(current_text: str) -> str:
        return add_document_to_index_text(current_text, document_slug, status, bridge_path)

    written = _atomic_index_update(writer, index_path, project_root, mutate, timeout_seconds)
    return BridgeIndexMutationResult(document_slug, parsed_status.value, bridge_path, index_path, written)


def set_status(
    project_root: str | Path,
    document_slug: str,
    status: str,
    *,
    bridge_path: str,
    timeout_seconds: float = 10.0,
) -> BridgeIndexMutationResult:
    """Serialize prepending a status line to a document in ``bridge/INDEX.md``."""
    project_root = Path(project_root)
    index_path = _require_index_path(project_root)
    writer = _load_index_writer(project_root)
    parsed_status = validate_status(status)
    if parsed_status is BridgeStatus.DEFERRED:
        validate_deferred_status_file(project_root, bridge_path)

    def mutate(current_text: str) -> str:
        documents = _parse_documents_or_raise(current_text)
        matching = [document for document in documents if document.name == document_slug]
        if (
            matching
            and matching[0].current_top is not None
            and matching[0].current_top.status is BridgeStatus.DEFERRED
            and parsed_status is not BridgeStatus.DEFERRED
        ):
            validate_deferred_clear_file(project_root, bridge_path)
        return set_status_in_index_text(current_text, document_slug, status, bridge_path)

    written = _atomic_index_update(writer, index_path, project_root, mutate, timeout_seconds)
    return BridgeIndexMutationResult(document_slug, parsed_status.value, bridge_path, index_path, written)


def _require_index_text(index_text: str) -> None:
    if not index_text.strip():
        raise BridgeIndexMutationError("bridge INDEX is empty or missing")


def _parse_documents_or_raise(index_text: str) -> list[Any]:
    result = parse_index(index_text)
    if result.errors:
        first = result.errors[0]
        raise BridgeIndexMutationError(
            f"bridge INDEX parse error at line {first.line_number}: expected {first.expected_state}"
        )
    return list(result.documents)


def _raise_on_duplicate_documents(documents: list[Any]) -> None:
    counts = Counter(document.name for document in documents)
    duplicates = sorted(name for name, count in counts.items() if count > 1)
    if duplicates:
        raise BridgeIndexMutationError(f"duplicate bridge document block(s): {', '.join(duplicates)}")


def _split_index_text(index_text: str) -> tuple[list[str], str]:
    newline = "\r\n" if "\r\n" in index_text else "\n"
    normalized = index_text.replace("\r\n", "\n")
    lines = normalized.split("\n")
    if lines and lines[-1] == "":
        lines.pop()
    return lines, newline


def _join_index_lines(lines: list[str], newline: str) -> str:
    return newline.join(lines).rstrip() + newline


def _first_document_line_index(lines: list[str]) -> int | None:
    for idx, line in enumerate(lines):
        if line.startswith("Document: "):
            return idx
    return None


def _require_index_path(project_root: Path) -> Path:
    index_path = project_root / "bridge" / "INDEX.md"
    if not index_path.is_file():
        raise BridgeIndexMutationError(f"bridge INDEX does not exist: {index_path}")
    return index_path


def _load_index_writer(project_root: Path) -> ModuleType:
    script_path = project_root / "scripts" / "bridge_index_writer.py"
    if not script_path.is_file():
        raise BridgeIndexMutationError(f"serialized bridge INDEX writer not found: {script_path}")
    module_name = f"_gtkb_bridge_index_writer_{abs(hash(script_path.resolve()))}"
    spec = importlib.util.spec_from_file_location(module_name, script_path)
    if spec is None or spec.loader is None:
        raise BridgeIndexMutationError(f"cannot load serialized bridge INDEX writer: {script_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    try:
        spec.loader.exec_module(module)
    except Exception as exc:  # noqa: BLE001 - surface load failure as CLI-safe error  # intentional-catch: quality gate waiver
        sys.modules.pop(module_name, None)
        raise BridgeIndexMutationError(f"cannot load serialized bridge INDEX writer: {exc}") from exc
    return module


def _atomic_index_update(
    writer: ModuleType,
    index_path: Path,
    project_root: Path,
    mutate: Callable[[str], str],
    timeout_seconds: float,
) -> str:
    state_dir = project_root / ".gtkb-state" / "bridge-index-writer"
    try:
        return cast(
            str,
            writer.atomic_index_update(
                index_path,
                mutate,
                state_dir=state_dir,
                timeout_seconds=timeout_seconds,
            ),
        )
    except BridgeIndexMutationError:
        raise
    except Exception as exc:  # noqa: BLE001 - normalize writer failures for CLI callers  # intentional-catch: quality gate waiver
        raise BridgeIndexMutationError(str(exc)) from exc
