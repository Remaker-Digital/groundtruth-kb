# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Helper for the /gtkb-bridge-propose skill.

Writes a bridge proposal file ``bridge/<topic>-001.md`` and inserts
its ``Document:`` / ``NEW:`` entry at the top of ``bridge/INDEX.md``
under governance-safe credential-scan and concurrency controls.

Design contract:

- Credential-only pre-flight scan (``CREDENTIAL_PATTERNS +
  BASH_EXTRAS``; PII explicitly excluded, same policy as the
  ``scanner-safe-writer`` hook). Callers never get a silent write
  when credential-shaped text is present.
- Two options on hit: **abort** or **redact**. Redact normalizes
  overlapping intervals before replacement, applies in reverse
  order, and re-scans the result. A non-empty second scan raises
  :class:`RedactionResidualError` (this is a bug, not a recoverable
  user state). **No Force option.**
- File-first write: the bridge file is persisted before the INDEX
  update. If the target file already exists,
  :class:`BridgeFileAlreadyExistsError` is raised before any INDEX
  touch.
- INDEX update is atomic (``os.replace``) and retry-safe. Total
  retry budget is **2 total attempts** (1 initial + 1 retry). On
  the second failure, :class:`BridgeIndexConflictError` surfaces
  with an actionable message.
- Idempotency detection uses an **exact-line match** against the
  stripped ``Document: <topic>`` line — substring matching would
  false-positive on slug prefixes.
"""

from __future__ import annotations

import contextlib
import os
import re
from pathlib import Path
from typing import Any, Literal

from groundtruth_kb.governance.credential_patterns import (
    BASH_EXTRAS,
    CREDENTIAL_PATTERNS,
)


class BridgeFileAlreadyExistsError(RuntimeError):
    """Raised when ``bridge/<topic>-001.md`` exists on disk before phase 3.

    The skill never silently overwrites. Callers should pick a fresh
    slug (or a versioned suffix like ``-002`` for REVISED) and retry.
    """


class BridgeIndexConflictError(RuntimeError):
    """Raised when INDEX.md cannot be updated safely.

    Two conditions trigger this error:

    - Another writer inserted a ``Document: <topic>`` line between
      the skill's read and its rename step.
    - The INDEX content changed between the read and the rename
      (non-topic concurrent modification), and the retry budget is
      exhausted.

    In both cases the bridge file is still on disk; the caller must
    either manually add an INDEX entry or retry the skill.
    """


class RedactionResidualError(RuntimeError):
    """Raised when the post-redaction re-scan still finds hits.

    This indicates a catalog/redactor bug (for example, a newly
    added pattern that the redactor doesn't cover). It is not a
    recoverable user state — the caller cannot fix it by editing
    the body. The fix is in the redactor/catalog code.
    """


class CredentialHitsFoundError(RuntimeError):
    """Raised by ``handle_hits_abort_or_redact`` when ``mode='abort'``.

    The body contained credential-shaped text and the caller chose
    to abort rather than redact.
    """


# Credential-only catalog. Iterates ``CREDENTIAL_PATTERNS + BASH_EXTRAS``
# directly — matching the scanner-safe-writer policy of excluding
# ``PII_PATTERNS`` (phone, email, ipv4) so operators can reference
# redacted samples without tripping a false-positive deny.
_SCAN_CATALOG: list[tuple[re.Pattern[str], str, str]] = [
    (spec.pattern, spec.name, spec.description) for spec in list(CREDENTIAL_PATTERNS) + list(BASH_EXTRAS)
]


def scan_credential_hits(content: str) -> list[dict[str, Any]]:
    """Return every credential-class hit in ``content``.

    Iterates :data:`_SCAN_CATALOG` (``CREDENTIAL_PATTERNS +
    BASH_EXTRAS``) and collects every non-overlapping regex match
    via ``finditer``. The list may contain overlapping hits when
    multiple specs match the same span (e.g., ``aws_key`` and
    ``bash_aws_key`` both match the same ``AKIA...`` literal). The
    overlap is resolved downstream by
    :func:`_normalize_hit_intervals`.

    Args:
        content: Text to scan.

    Returns:
        List of hit dictionaries, each with keys:

        - ``pattern_name`` (str) — the canonical PatternSpec name
        - ``pattern_description`` (str) — human-readable description
        - ``span`` (tuple[int, int]) — ``(start, end)`` offsets
    """
    hits: list[dict[str, Any]] = []
    for pattern, name, description in _SCAN_CATALOG:
        for match in pattern.finditer(content):
            hits.append(
                {
                    "pattern_name": name,
                    "pattern_description": description,
                    "span": (match.start(), match.end()),
                }
            )
    return hits


def _normalize_hit_intervals(hits: list[dict[str, Any]]) -> list[tuple[int, int, str]]:
    """Merge overlapping hits into non-overlapping ``(start, end, label)`` tuples.

    Sort order is ``(start, -end)`` so longer spans come first at
    the same start offset. Overlapping intervals are merged; the
    merged interval's label is the outermost (earliest-start) spec's
    ``pattern_name``. Duplicate spans (same start, same end) collapse
    to a single interval using the first spec's name as the label.

    Args:
        hits: Output of :func:`scan_credential_hits`.

    Returns:
        Non-overlapping ``(start, end, label)`` tuples, sorted by
        start ascending. Empty if ``hits`` is empty.
    """
    if not hits:
        return []
    # Sort by start ascending, then by -end (longer span first at the same start).
    sorted_hits = sorted(hits, key=lambda h: (h["span"][0], -h["span"][1]))
    merged: list[tuple[int, int, str]] = []
    for hit in sorted_hits:
        start, end = hit["span"]
        name = hit["pattern_name"]
        if merged and start < merged[-1][1]:
            # Overlaps with previous merged interval — extend end, keep outer label.
            prev_start, prev_end, prev_name = merged[-1]
            merged[-1] = (prev_start, max(prev_end, end), prev_name)
        else:
            merged.append((start, end, name))
    return merged


def redact_credential_hits(content: str, hits: list[dict[str, Any]]) -> str:
    """Replace credential hits with ``[REDACTED:<label>]`` placeholders.

    Handles overlapping canonical matches by normalizing hits into
    non-overlapping intervals first (outer-span-wins label), then
    applying replacements in reverse-start order so earlier offsets
    remain stable against later replacements.

    Args:
        content: Original text.
        hits: Output of :func:`scan_credential_hits`. May contain
            overlaps — they are resolved internally.

    Returns:
        Redacted text. Every character in ``content`` is replaced at
        most once.
    """
    intervals = _normalize_hit_intervals(hits)
    if not intervals:
        return content
    result = content
    # Apply in reverse-start order so indices before the replacement remain valid.
    for start, end, label in sorted(intervals, key=lambda iv: iv[0], reverse=True):
        result = result[:start] + f"[REDACTED:{label}]" + result[end:]
    return result


def handle_hits_abort_or_redact(
    body: str,
    hits: list[dict[str, Any]],
    *,
    mode: Literal["abort", "redact"],
) -> str:
    """Resolve credential hits per ``mode`` or raise.

    Args:
        body: Original body text.
        hits: Output of :func:`scan_credential_hits`.
        mode: ``"abort"`` raises :class:`CredentialHitsFoundError`;
            ``"redact"`` applies :func:`redact_credential_hits` then
            re-scans and raises :class:`RedactionResidualError` if
            the second scan is non-empty.

    Returns:
        The body to write. Either the original (when ``hits`` is
        empty) or the redacted version (when ``mode='redact'`` and
        the second scan is clean).
    """
    if not hits:
        return body
    if mode == "abort":
        first = hits[0]
        raise CredentialHitsFoundError(
            f"Credential-shaped content detected: "
            f"{first['pattern_name']} ({first['pattern_description']}). "
            f"Re-invoke with mode='redact' or edit the body."
        )
    if mode == "redact":
        redacted = redact_credential_hits(body, hits)
        residual = scan_credential_hits(redacted)
        if residual:
            first = residual[0]
            raise RedactionResidualError(
                f"Post-redaction re-scan still finds credential hits: "
                f"{first['pattern_name']} ({first['pattern_description']}). "
                f"This is a catalog/redactor bug, not a recoverable user state."
            )
        return redacted
    raise ValueError(f"Unknown mode {mode!r}; expected 'abort' or 'redact'.")


def _compute_new_index_content(existing_lines: list[str], new_entry: str) -> str:
    """Insert ``new_entry`` at the top of the INDEX body, after header comments.

    Header comment region is the contiguous prefix of lines that are
    blank, markdown headers (``#``), or HTML comments
    (``<!--``). Everything after that region is considered body.

    Args:
        existing_lines: Lines of the current INDEX.md (as returned by
            ``splitlines(keepends=True)``).
        new_entry: The full entry string to insert. Should end with a
            trailing newline.

    Returns:
        The new INDEX content as a single string.
    """
    # Find the boundary between the header/comment prefix and the body.
    insert_idx = 0
    in_comment = False
    for idx, line in enumerate(existing_lines):
        stripped = line.strip()
        # Track a multi-line HTML comment block.
        if in_comment:
            if "-->" in stripped:
                in_comment = False
            insert_idx = idx + 1
            continue
        if stripped.startswith("<!--"):
            # Single-line or start of a multi-line HTML comment.
            if "-->" not in stripped[4:]:
                in_comment = True
            insert_idx = idx + 1
            continue
        if not stripped or stripped.startswith("#") or stripped.startswith("|"):
            # Blank line, markdown header, or markdown table row (status legend) —
            # treat as header region.
            insert_idx = idx + 1
            continue
        # First real content line — stop. ``insert_idx`` points at it.
        break
    # Ensure the new_entry ends with a newline.
    entry = new_entry if new_entry.endswith("\n") else new_entry + "\n"
    # Ensure separation between the inserted entry and the existing line that follows.
    if insert_idx < len(existing_lines):
        following = existing_lines[insert_idx]
        if not entry.endswith("\n\n") and following.strip():
            entry = entry + "\n"
    head = "".join(existing_lines[:insert_idx])
    tail = "".join(existing_lines[insert_idx:])
    return head + entry + tail


def _update_bridge_index(
    index_path: Path,
    new_entry: str,
    *,
    topic_slug: str,
) -> None:
    """Insert ``new_entry`` at the top of ``index_path`` atomically.

    Steps:

    1. Read the current bytes.
    2. Idempotency check using **exact line match**: if any line,
       once stripped, equals ``"Document: <topic_slug>"`` exactly
       (NOT substring match), raise :class:`BridgeIndexConflictError`
       with a concurrent-same-topic message.
    3. Compute the new content via
       :func:`_compute_new_index_content`.
    4. Write the new content to a same-directory temp file.
    5. Re-read the INDEX bytes; if they differ from step 1, unlink
       the temp file and raise :class:`BridgeIndexConflictError`
       with an "INDEX changed during update" message.
    6. Atomically rename the temp file onto the index via
       :func:`os.replace`.

    Args:
        index_path: Path to ``bridge/INDEX.md``.
        new_entry: The entry block to insert at the top.
        topic_slug: The topic slug (for idempotency detection).

    Raises:
        BridgeIndexConflictError: On concurrent same-topic insertion
            or non-topic concurrent modification.
    """
    # Step 1: Read.
    original_bytes = index_path.read_bytes()
    lines = original_bytes.decode("utf-8").splitlines(keepends=True)

    # Step 2: Idempotency check — EXACT LINE MATCH per the skill contract.
    # Substring matching would false-positive if a Document line shares a
    # slug prefix (e.g., ``Document: foo-bar`` vs ``Document: foo``).
    expected = f"Document: {topic_slug}"
    for line in lines:
        if line.strip() == expected:
            raise BridgeIndexConflictError(
                f"INDEX.md already has an entry for {expected!r}. "
                f"Another writer inserted it concurrently. The bridge file "
                f"at bridge/{topic_slug}-001.md is on disk; inspect and "
                f"reconcile manually."
            )

    # Step 3: Compute new content.
    new_content = _compute_new_index_content(lines, new_entry)

    # Step 4: Write to a same-directory temp file so the rename is atomic.
    temp_path = index_path.with_name(f"{index_path.name}.tmp.{os.getpid()}")
    temp_path.write_bytes(new_content.encode("utf-8"))

    try:
        # Step 5: Pre-rename check — INDEX must not have changed since step 1.
        current_bytes = index_path.read_bytes()
        if current_bytes != original_bytes:
            temp_path.unlink()
            raise BridgeIndexConflictError(
                "INDEX.md changed during update — concurrent modification detected. Retry required."
            )

        # Step 6: Atomic rename.
        os.replace(temp_path, index_path)
    except BridgeIndexConflictError:
        raise
    except Exception:
        # Best-effort cleanup of temp file on any unexpected error.
        if temp_path.exists():
            with contextlib.suppress(OSError):
                temp_path.unlink()
        raise


def propose_bridge(
    topic_slug: str,
    body: str,
    *,
    mode: Literal["abort", "redact"] = "abort",
    bridge_dir: Path | None = None,
) -> Path:
    """Create ``bridge/<topic_slug>-001.md`` and insert an INDEX entry.

    Phase 1 — Pre-flight scan: iterate ``CREDENTIAL_PATTERNS +
    BASH_EXTRAS`` over ``body``. If hits are found, resolve per
    ``mode`` via :func:`handle_hits_abort_or_redact`.

    Phase 2 — File-first write: write ``bridge/<topic_slug>-001.md``
    atomically. If the file already exists,
    :class:`BridgeFileAlreadyExistsError` is raised before any INDEX
    touch.

    Phase 3 — INDEX insertion with retry: call
    :func:`_update_bridge_index`. On
    :class:`BridgeIndexConflictError`, retry once. **Total attempts:
    2 total** (1 initial + 1 retry). On the second failure, re-raise
    with an actionable message that mentions the bridge file on disk.

    Args:
        topic_slug: Kebab-case slug for the bridge document. The
            file becomes ``bridge/<topic_slug>-001.md`` and the
            INDEX entry begins with ``Document: <topic_slug>``.
        body: Proposal body text.
        mode: ``"abort"`` (default) or ``"redact"``. Controls the
            hit-resolution policy.
        bridge_dir: Parent bridge directory. Defaults to
            ``Path("bridge")``.

    Returns:
        Absolute path to the created bridge file.

    Raises:
        CredentialHitsFoundError: ``mode='abort'`` and hits found.
        RedactionResidualError: Redaction failed the re-scan gate.
        BridgeFileAlreadyExistsError: Target file already on disk.
        BridgeIndexConflictError: INDEX could not be updated after
            2 total attempts.
    """
    bridge_root = bridge_dir if bridge_dir is not None else Path("bridge")
    bridge_file = bridge_root / f"{topic_slug}-001.md"
    index_path = bridge_root / "INDEX.md"

    # Phase 1: Pre-flight scan.
    hits = scan_credential_hits(body)
    body_to_write = handle_hits_abort_or_redact(body, hits, mode=mode)

    # Phase 2: File-first write (fail-fast on existing file; no silent overwrite).
    if bridge_file.exists():
        raise BridgeFileAlreadyExistsError(
            f"{bridge_file} already exists — pick a fresh slug or bump to "
            f"-002 for a REVISED version. The skill never silently overwrites."
        )
    bridge_file.parent.mkdir(parents=True, exist_ok=True)
    bridge_file.write_bytes(body_to_write.encode("utf-8"))

    # Phase 3: INDEX insertion with retry.
    # Retry budget: 2 total attempts (1 initial + 1 retry). Both the comment,
    # the final exception message, and the test coverage use the "2 total"
    # phrasing — keep them in sync.
    new_entry = f"Document: {topic_slug}\nNEW: bridge/{topic_slug}-001.md\n"
    last_error: BridgeIndexConflictError | None = None
    max_attempts = 2  # 2 total attempts — 1 initial + 1 retry.
    for attempt in range(1, max_attempts + 1):
        try:
            _update_bridge_index(index_path, new_entry, topic_slug=topic_slug)
            return bridge_file
        except BridgeIndexConflictError as exc:
            last_error = exc
            if attempt >= max_attempts:
                break
            # else: loop and retry the INDEX-layer update only.
    # Exhausted 2 total attempts — re-raise with an actionable message.
    raise BridgeIndexConflictError(
        f"Bridge file {bridge_file} was written but INDEX.md could not be "
        f"updated after 2 total attempts. The file exists on disk; manually "
        f"add an entry to bridge/INDEX.md or retry the skill. "
        f"Last error: {last_error}"
    )


__all__ = [
    "BridgeFileAlreadyExistsError",
    "BridgeIndexConflictError",
    "CredentialHitsFoundError",
    "RedactionResidualError",
    "handle_hits_abort_or_redact",
    "propose_bridge",
    "redact_credential_hits",
    "scan_credential_hits",
]
