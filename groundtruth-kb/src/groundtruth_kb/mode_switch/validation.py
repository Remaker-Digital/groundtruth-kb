"""Validators for the authoritative role, bridge, and session-state artifacts.

Per ``SPEC-BRIDGE-MODE-CONFIG-TRANSACTIONS-001`` acceptance criterion #2:
"The component validates the requested switch against the authoritative
role, bridge, and session-state artifacts before writing durable state."

The bridge-artifact validator mirrors the canonical bridge status vocabulary
and checks status-bearing numbered files directly.

(c) 2026 Remaker Digital, a DBA of VanDusen and Palmeter, LLC. All rights
reserved.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path

BRIDGE_STATUS_TOKENS = frozenset(
    {"NEW", "REVISED", "GO", "NO-GO", "VERIFIED", "WITHDRAWN", "ADVISORY", "DEFERRED", "ACCEPTED", "BLOCKED"}
)

_BRIDGE_FILE_RE = re.compile(r"^.+-\d{3}\.md$")
_BRIDGE_STATUS_TOKEN_RE = re.compile(r"^[#>*\-\s`]*([A-Z][A-Z\-]*)\b")


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
    ``GOV-ACTING-PRIME-BUILDER-001``). Migrated from the retired role
    artifact.
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
    """Validate the status-bearing numbered bridge-file chain."""
    axis = "bridge"
    bridge_dir = project_root / "bridge"
    if not bridge_dir.is_dir():
        return _fail(axis, f"bridge directory missing: {bridge_dir}")
    checked_files = 0
    bad_status_tokens: list[str] = []
    unreadable: list[str] = []
    missing_status: list[str] = []
    for path in sorted(bridge_dir.glob("*.md")):
        if not _BRIDGE_FILE_RE.match(path.name):
            continue
        checked_files += 1
        try:
            lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
        except OSError as exc:
            unreadable.append(f"{path.name}: {exc}")
            continue
        token: str | None = None
        for line in lines:
            stripped = line.strip()
            if not stripped:
                continue
            match = _BRIDGE_STATUS_TOKEN_RE.match(stripped)
            token = match.group(1) if match else None
            break
        if token is None:
            missing_status.append(path.name)
        elif token not in BRIDGE_STATUS_TOKENS:
            bad_status_tokens.append(token)
    if checked_files == 0:
        return _fail(axis, "bridge directory contains no numbered bridge files")
    if unreadable:
        return _fail(axis, f"bridge files unreadable: {sorted(unreadable)}")
    if missing_status:
        return _fail(axis, f"bridge files missing status tokens: {sorted(missing_status)}")
    if bad_status_tokens:
        unique_bad = sorted(set(bad_status_tokens))
        return _fail(
            axis,
            f"bridge files contain unknown status tokens: {unique_bad}",
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


def validate_bridge_substrate(project_root: Path, new_substrate: str, topology: str) -> ValidationResult:
    """Validate bridge substrate configuration against topology and registrations.

    Substrates: 'cross_harness_trigger', 'single_harness_dispatcher', 'none'.
    Rules:
    1. 'single_harness_dispatcher' is valid ONLY if topology is 'single_harness'.
    2. 'cross_harness_trigger' requires 'cross_harness_bridge_trigger.py' substring
       registered in either .claude/settings.json or .codex/hooks.json (if those files exist and contain hooks).
    3. 'single_harness_dispatcher' when on Windows probes GTKB-SingleHarnessBridgeDispatcher scheduled task.
    """
    axis = "bridge_substrate"
    allowed = {"cross_harness_trigger", "single_harness_dispatcher", "none"}
    if new_substrate not in allowed:
        return _fail(axis, f"unknown bridge substrate {new_substrate!r}")

    if new_substrate == "single_harness_dispatcher" and topology != "single_harness":
        return _fail(
            axis,
            f"bridge substrate {new_substrate!r} requires single_harness topology (current topology: {topology})",
        )

    # If new_substrate is 'cross_harness_trigger', probe registration.
    if new_substrate == "cross_harness_trigger":
        registered = False
        settings_path = project_root / ".claude" / "settings.json"
        codex_hooks_path = project_root / ".codex" / "hooks.json"

        def _contains_bridge_trigger(value: object) -> bool:
            if isinstance(value, dict):
                command = value.get("command")
                if isinstance(command, str) and "cross_harness_bridge_trigger.py" in command:
                    return True
                return any(_contains_bridge_trigger(child) for key, child in value.items() if key not in {"command"})
            if isinstance(value, list):
                return any(_contains_bridge_trigger(item) for item in value)
            return False

        # Check settings.json
        if settings_path.is_file():
            try:
                data = json.loads(settings_path.read_text(encoding="utf-8"))
                registered = _contains_bridge_trigger(data.get("hooks", {}))
            except Exception:  # intentional-catch: quality gate waiver
                pass

        # Check codex hooks.json
        if not registered and codex_hooks_path.is_file():
            try:
                data = json.loads(codex_hooks_path.read_text(encoding="utf-8"))
                registered = _contains_bridge_trigger(data.get("hooks", {}))
            except Exception:  # intentional-catch: quality gate waiver
                pass

        if not registered:
            return _fail(
                axis,
                "cross_harness_trigger is not registered in .claude/settings.json or .codex/hooks.json",
            )

    # If new_substrate is 'single_harness_dispatcher', probe Windows Scheduled Task if on Windows.
    if new_substrate == "single_harness_dispatcher":
        import sys

        if sys.platform == "win32":
            import subprocess

            try:
                res = subprocess.run(
                    ["powershell", "-Command", "Get-ScheduledTask -TaskName GTKB-SingleHarnessBridgeDispatcher"],
                    capture_output=True,
                    text=True,
                    check=False,
                )
                if res.returncode != 0:
                    return _fail(
                        axis,
                        "GTKB-SingleHarnessBridgeDispatcher scheduled task is not registered in Windows",
                    )
            except Exception as exc:  # intentional-catch: quality gate waiver
                return _fail(
                    axis,
                    f"Failed to check GTKB-SingleHarnessBridgeDispatcher scheduled task: {exc}",
                )

    return _ok(axis)
