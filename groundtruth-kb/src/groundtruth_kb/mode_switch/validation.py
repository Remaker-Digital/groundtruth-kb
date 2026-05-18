"""Validators for the authoritative role, bridge, and session-state artifacts.

Per ``SPEC-BRIDGE-MODE-CONFIG-TRANSACTIONS-001`` acceptance criterion #2:
"The component validates the requested switch against the authoritative
role, bridge, and session-state artifacts before writing durable state."

The bridge-artifact validator mirrors the canonical bridge parser's status
vocabulary from ``scripts/bridge_applicability_preflight.py:32`` —
``{NEW, REVISED, GO, NO-GO, VERIFIED, WITHDRAWN, ADVISORY}`` — and does NOT
require referenced-file existence on disk (historical INDEX entries may
legitimately reference moved or removed files; that is bridge hygiene, not
mode-switch safety, per Codex NO-GO at bridge ``-007`` F1 closed by
REVISED-3 at ``-008``).

(c) 2026 Remaker Digital, a DBA of VanDusen and Palmeter, LLC. All rights
reserved.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path

BRIDGE_STATUS_TOKENS = frozenset(
    {"NEW", "REVISED", "GO", "NO-GO", "VERIFIED", "WITHDRAWN", "ADVISORY"}
)

_BRIDGE_STATUS_LINE_RE = re.compile(
    r"^(NEW|REVISED|GO|NO-GO|VERIFIED|WITHDRAWN|ADVISORY):\s+(bridge/\S+\.md)\s*$"
)
_BRIDGE_STATUS_SHAPED_LINE_RE = re.compile(r"^([A-Z][A-Z\-]+):\s+bridge/\S+\.md\s*$")
_DOCUMENT_LINE_RE = re.compile(r"^Document:\s+\S")


@dataclass(frozen=True)
class ValidationResult:
    """Result of validating a single authoritative artifact."""

    is_valid: bool
    axis: str
    errors: tuple[str, ...] = ()


def _ok(axis: str) -> ValidationResult:
    return ValidationResult(is_valid=True, axis=axis)


def _fail(axis: str, *errors: str) -> ValidationResult:
    return ValidationResult(is_valid=False, axis=axis, errors=tuple(errors))


def validate_role_artifact(project_root: Path) -> ValidationResult:
    """Validate the harness registry projection (WI-3342 IP-5).

    Confirms ``harness-state/harness-registry.json`` exists, is readable,
    parses as JSON, and structurally matches the projection schema (top-level
    ``"harnesses"`` LIST; each harness record carries a ``"role"`` field as
    either a list of tokens or a legacy scalar; tokens are from
    ``{prime-builder, loyal-opposition, acting-prime-builder}`` per
    ``ADR-SINGLE-HARNESS-OPERATING-MODE-001`` and
    ``GOV-ACTING-PRIME-BUILDER-001``). Migrated from the retired
    ``harness-state/role-assignments.json`` role artifact.
    """
    axis = "role"
    from groundtruth_kb.harness_projection import harness_registry_path

    path = harness_registry_path(project_root)
    if not path.exists():
        return _fail(axis, f"role artifact missing: {path}")
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        return _fail(axis, f"role artifact unreadable: {exc}")
    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        return _fail(axis, f"role artifact JSON parse failed: {exc}")
    if not isinstance(data, dict):
        return _fail(axis, "role artifact top-level must be a JSON object")
    harnesses = data.get("harnesses")
    if not isinstance(harnesses, list):
        return _fail(axis, "role artifact missing 'harnesses' list")
    valid_tokens = {"prime-builder", "loyal-opposition", "acting-prime-builder"}
    for record in harnesses:
        if not isinstance(record, dict):
            return _fail(axis, "harness registry record is not a JSON object")
        harness_id = record.get("id")
        role = record.get("role")
        if isinstance(role, list):
            tokens = [str(item).strip() for item in role]
        elif isinstance(role, str):
            tokens = [role.strip()]
        else:
            return _fail(
                axis,
                f"harness {harness_id!r} role field must be a list or string",
            )
        for token in tokens:
            if token and token not in valid_tokens:
                return _fail(
                    axis,
                    f"harness {harness_id!r} has unknown role token {token!r}",
                )
    return _ok(axis)


def validate_bridge_artifact(project_root: Path) -> ValidationResult:
    """Validate ``bridge/INDEX.md``.

    Parse-clean rule:
    1. ``bridge/INDEX.md`` exists and is readable.
    2. The file contains at least one ``Document: <name>`` entry (signal that
       the bridge protocol is alive).
    3. Every status line that matches the bridge-status pattern uses a token
       from ``BRIDGE_STATUS_TOKENS``.
    4. Lines that do NOT match the bridge-status shape are ignored (commentary,
       HTML comments, blank lines, headings). Same forgiveness pattern as the
       canonical preflight script.

    Does NOT validate file-existence of referenced bridge files; historical
    INDEX entries may reference relocated or removed files, and that is a
    separate hygiene concern out of scope for mode-switch safety.
    """
    axis = "bridge"
    path = project_root / "bridge" / "INDEX.md"
    if not path.exists():
        return _fail(axis, f"bridge artifact missing: {path}")
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        return _fail(axis, f"bridge artifact unreadable: {exc}")
    has_document_entry = False
    bad_status_tokens: list[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if _DOCUMENT_LINE_RE.match(stripped):
            has_document_entry = True
            continue
        if _BRIDGE_STATUS_LINE_RE.match(stripped):
            continue
        shaped = _BRIDGE_STATUS_SHAPED_LINE_RE.match(stripped)
        if shaped:
            token = shaped.group(1)
            if token not in BRIDGE_STATUS_TOKENS:
                bad_status_tokens.append(token)
    if not has_document_entry:
        return _fail(axis, "bridge artifact contains no 'Document:' entry")
    if bad_status_tokens:
        unique_bad = sorted(set(bad_status_tokens))
        return _fail(
            axis,
            f"bridge artifact contains unknown status tokens: {unique_bad}",
        )
    return _ok(axis)


def validate_session_state_artifact(project_root: Path) -> ValidationResult:
    """Validate ``.claude/session/work-subject.json``.

    Optional artifact: missing file is OK (single-harness installs may
    legitimately lack one). If present, must be readable JSON.
    """
    axis = "session-state"
    path = project_root / ".claude" / "session" / "work-subject.json"
    if not path.exists():
        return _ok(axis)
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        return _fail(axis, f"session-state artifact unreadable: {exc}")
    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        return _fail(axis, f"session-state JSON parse failed: {exc}")
    if not isinstance(data, dict):
        return _fail(axis, "session-state top-level must be a JSON object")
    return _ok(axis)
