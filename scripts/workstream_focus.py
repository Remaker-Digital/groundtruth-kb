#!/usr/bin/env python3
"""Work-subject state, commands, and root-classification guardrails for GroundTruth-KB sessions.

Phase 7 foundation slice (DELIB-0876 / GTKB-ISOLATION-010): the module stores
canonical runtime state at ``.claude/session/work-subject.json`` with a typed
schema, migrates one legacy window from ``.claude/hooks/.workstream-focus-state.json``,
recognizes ``work subject application`` / ``work subject GT-KB`` commands
alongside the pre-existing aliases, classifies candidate write targets as
``application_product`` / ``current_repo_bridge_or_governance`` / ``gtkb_product``
/ ``neutral``, and renders startup text using ``work subject`` language.
"""

from __future__ import annotations

import hashlib
import json
import os
import queue
import re
import threading
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

try:
    from scripts._session_init_keyword import InitKeywordMatch, match_init_keyword
    from scripts.harness_roles import (
        DEFAULT_HARNESS_IDS,
        ROLE_ACTING_PRIME_BUILDER,
        ROLE_ASSIGNMENTS_RELATIVE_PATH,
        ROLE_LOYAL_OPPOSITION,
        ROLE_PRIME_BUILDER,
        _normalize_role_field,
        current_prime_ids,
        load_role_assignments,
        role_assignments_path,
        role_for_harness,
        set_harness_role,
    )
    from scripts.harness_roles import (
        normalize_harness_name as _normalize_harness_name_from_roles,
    )
    from scripts.harness_roles import (
        resolved_harness_id as _resolved_harness_id_from_roles,
    )
except ImportError:  # pragma: no cover - direct script execution path
    from _session_init_keyword import InitKeywordMatch, match_init_keyword  # type: ignore[no-redef]
    from harness_roles import (  # type: ignore[no-redef]
        DEFAULT_HARNESS_IDS,
        ROLE_ACTING_PRIME_BUILDER,
        ROLE_ASSIGNMENTS_RELATIVE_PATH,
        ROLE_LOYAL_OPPOSITION,
        ROLE_PRIME_BUILDER,
        _normalize_role_field,
        current_prime_ids,
        load_role_assignments,
        role_assignments_path,
        role_for_harness,
        set_harness_role,
    )
    from harness_roles import (  # type: ignore[no-redef]
        normalize_harness_name as _normalize_harness_name_from_roles,
    )
    from harness_roles import (  # type: ignore[no-redef]
        resolved_harness_id as _resolved_harness_id_from_roles,
    )

PROJECT_ROOT = Path(__file__).resolve().parent.parent
GTKB_HARNESS_STATE_ROOT = PROJECT_ROOT / "harness-state"

# ---- Work-subject identity ----------------------------------------------
FOCUS_APPLICATION = "application"
FOCUS_GTKB_INFRASTRUCTURE = "gtkb_infrastructure"
DEFAULT_FOCUS = FOCUS_GTKB_INFRASTRUCTURE

SUBJECT_APPLICATION = FOCUS_APPLICATION
SUBJECT_GTKB = FOCUS_GTKB_INFRASTRUCTURE
DEFAULT_SUBJECT = SUBJECT_GTKB

SCHEMA_VERSION = 1
ROLE_SLOT_DEFAULT = "shared"
DEFAULT_APPLICATION_LABEL = "Agent Red demo adopter"

# Topology mode — whether GT-KB Prime Builder and Loyal Opposition run in one
# harness (single) or split across two harnesses (multi). Drives counterpart
# detection in ``detect_counterpart_state`` and the Active Work Subject block.
TOPOLOGY_MODE_SINGLE = "single_harness"
TOPOLOGY_MODE_MULTI = "multi_harness"
TOPOLOGY_MODE_DEFAULT = TOPOLOGY_MODE_SINGLE
_TOPOLOGY_MODES = {TOPOLOGY_MODE_SINGLE, TOPOLOGY_MODE_MULTI}

# ---- State-file paths ---------------------------------------------------
LEGACY_STATE_RELATIVE_PATH = Path(".claude") / "hooks" / ".workstream-focus-state.json"
CANONICAL_STATE_RELATIVE_PATH = Path(".claude") / "session" / "work-subject.json"
STATE_RELATIVE_PATH = CANONICAL_STATE_RELATIVE_PATH  # Back-compat alias (now canonical)

OPERATING_ROLE_RELATIVE_PATH = ROLE_ASSIGNMENTS_RELATIVE_PATH
LIFECYCLE_GUARD_RELATIVE_PATH = Path(".claude") / "hooks" / ".session-lifecycle-guard.json"
STARTUP_REPORT_RELATIVE_PATH = Path("docs") / "gtkb-dashboard" / "session-startup-report.md"
DEFAULT_DASHBOARD_PREFERENCES_PATH = GTKB_HARNESS_STATE_ROOT / "codex" / "session-startup-preferences.json"
STARTUP_RESPONSE_PENDING_EXPIRY_SECONDS = 30 * 60
STARTUP_RELAY_CACHE_MAX_AGE_SECONDS = STARTUP_RESPONSE_PENDING_EXPIRY_SECONDS
STARTUP_RELAY_CACHE_FUTURE_SKEW_SECONDS = 5 * 60
STARTUP_RELAY_REFRESH_TIMEOUT_SECONDS = 2.0
HARNESS_LIFECYCLE_GUARDS = {
    "codex": GTKB_HARNESS_STATE_ROOT / "codex" / "session-lifecycle-guard.json",
    "claude": GTKB_HARNESS_STATE_ROOT / "claude" / "session-lifecycle-guard.json",
}

# ---- Role profiles (unchanged from prior module) -----------------------
TOGGLEABLE_ROLE_PROFILES = {ROLE_PRIME_BUILDER, ROLE_LOYAL_OPPOSITION, ROLE_ACTING_PRIME_BUILDER}

# Labels preserved (asserted by test_session_self_initialization.py:93-95).
FOCUS_LABELS = {
    FOCUS_APPLICATION: "Application Focus",
    FOCUS_GTKB_INFRASTRUCTURE: "GT-KB Infrastructure Focus",
}

# ---- Command vocabularies ----------------------------------------------
# Phase 7 canonical commands for setting the work subject directly.
WORK_SUBJECT_APPLICATION_COMMANDS = {
    "work subject application",
    "work subject app",
    "work subject agent red",
}

WORK_SUBJECT_GTKB_COMMANDS = {
    "work subject gt-kb",
    "work subject gtkb",
    "work subject groundtruth-kb",
    "work subject groundtruth kb",
    "work subject gt-kb infrastructure",
    "work subject gtkb infrastructure",
}

# Legacy aliases preserved for one migration window.
APPLICATION_FOCUS_COMMANDS = {
    "application mode",
    "application focus",
    "app mode",
    "app focus",
    "agent red mode",
    "agent red focus",
}

GTKB_FOCUS_COMMANDS = {
    "gt-kb mode",
    "gt-kb focus",
    "gtkb mode",
    "gtkb focus",
    "groundtruth-kb mode",
    "groundtruth-kb focus",
    "groundtruth kb mode",
    "groundtruth kb focus",
    "gt-kb infrastructure mode",
    "gt-kb infrastructure focus",
    "gtkb infrastructure mode",
    "gtkb infrastructure focus",
    "groundtruth-kb infrastructure mode",
    "groundtruth-kb infrastructure focus",
    "groundtruth kb infrastructure mode",
    "groundtruth kb infrastructure focus",
}

ROLE_TOGGLE_NEXT_SESSION_COMMANDS = {
    "switch mode next session",
    "change mode next session",
    "switch role next session",
    "change role next session",
    "switch roles next session",
    "change roles next session",
}

PRIME_BUILDER_NEXT_SESSION_COMMANDS = {
    "prime builder next session",
    "prime builder mode next session",
    "switch to prime builder next session",
    "change to prime builder next session",
}

LOYAL_OPPOSITION_NEXT_SESSION_COMMANDS = {
    "loyal opposition next session",
    "loyal opposition mode next session",
    "switch to loyal opposition next session",
    "change to loyal opposition next session",
}

DASHBOARD_ENABLE_COMMANDS = {
    "enable dashboard",
    "enable dashboard next session",
    "open dashboard next session",
}

DASHBOARD_DISABLE_COMMANDS = {
    "disable dashboard",
    "disable dashboard next session",
    "do not open dashboard next session",
}

# ---- Root classification taxonomy --------------------------------------
ROOT_APPLICATION_PRODUCT = "application_product"
ROOT_CURRENT_REPO_BRIDGE_OR_GOVERNANCE = "current_repo_bridge_or_governance"
ROOT_GTKB_PRODUCT = "gtkb_product"
ROOT_NEUTRAL = "neutral"

# Application product surfaces in the current repo.
APPLICATION_PREFIXES = (
    "admin/",
    "assets/",
    "config/",
    "docs-site/",
    "extensions/",
    "infrastructure/",
    "src/",
    "test_host/",
    "website/",
    "widget/",
)

# Current-repo bridge/governance surfaces.
CURRENT_REPO_BRIDGE_OR_GOVERNANCE_PREFIXES = (
    ".claude/hooks/",
    ".claude/rules/",
    ".claude/skills/",
    ".claude/session/",
    ".codex/",
    ".groundtruth/",
    "bridge/",
    "docs/gtkb-dashboard/",
    "scripts/gtkb_dashboard/",
    "independent-progress-assessments/",
    "memory/",
)

CURRENT_REPO_BRIDGE_OR_GOVERNANCE_FILES = {
    "AGENTS.md",
    "CLAUDE.md",
    "groundtruth.db",
    "groundtruth.toml",
    "scripts/check_codex_hook_parity.py",
    "scripts/session_self_initialization.py",
    "scripts/workstream_focus.py",
}

VERSIONED_BRIDGE_PATH_RE = re.compile(r"^bridge/[^/]+-\d{3}\.md$")
ADVISORY_BRIDGE_KIND_RE = re.compile(r"^bridge_kind:\s*[\w-]*advisory\b", re.IGNORECASE | re.MULTILINE)
SHELL_TOOL_NAMES = {"Bash", "shell_command", "functions.shell_command"}

# Back-compat aliases (legacy classify_path still consumed by third-party callers).
GTKB_INFRASTRUCTURE_PREFIXES = CURRENT_REPO_BRIDGE_OR_GOVERNANCE_PREFIXES
GTKB_INFRASTRUCTURE_FILES = CURRENT_REPO_BRIDGE_OR_GOVERNANCE_FILES

MUTATING_COMMAND_PATTERNS = (
    re.compile(r"\b(?:Set-Content|Add-Content|Out-File|New-Item|Remove-Item|Move-Item|Copy-Item)\b", re.I),
    re.compile(r"(?:^|\s)(?:>|>>)\s*"),
    re.compile(r"\b(?:cat|type)\b.*(?:>|>>)", re.I),
)


def _now_iso() -> str:
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")


def _parse_iso8601(value: Any) -> datetime | None:
    text = str(value or "").strip()
    if not text:
        return None
    normalized = text[:-1] + "+00:00" if text.endswith("Z") else text
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError:
        return None
    return parsed.astimezone(UTC) if parsed.tzinfo is not None else parsed.replace(tzinfo=UTC)


def _project_root_from_env() -> Path:
    return Path(os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()).resolve()


def _normalize_harness_name(value: str | None) -> str | None:
    normalized = _normalize_harness_name_from_roles(value)
    if normalized in DEFAULT_HARNESS_IDS:
        return normalized
    return None


def _resolved_harness_name() -> str | None:
    return _normalize_harness_name(os.environ.get("GTKB_HARNESS_NAME"))


def _resolved_harness_id(project_root: Path | None = None) -> str | None:
    return _resolved_harness_id_from_roles(
        (project_root or _project_root_from_env()).resolve(),
        harness_name=_resolved_harness_name(),
    )


def state_path(project_root: Path | None = None) -> Path:
    """Return the canonical work-subject state file path (new Phase 7 location)."""

    override = os.environ.get("GTKB_WORKSTREAM_FOCUS_STATE")
    if override:
        return Path(override).expanduser().resolve()
    root = (project_root or _project_root_from_env()).resolve()
    return root / CANONICAL_STATE_RELATIVE_PATH


def legacy_state_path(project_root: Path | None = None) -> Path:
    """Return the pre-Phase-7 state file path (for one-window migration reads)."""

    override = os.environ.get("GTKB_WORKSTREAM_FOCUS_LEGACY_STATE")
    if override:
        return Path(override).expanduser().resolve()
    root = (project_root or _project_root_from_env()).resolve()
    return root / LEGACY_STATE_RELATIVE_PATH


def operating_role_path(project_root: Path | None = None) -> Path:
    root = (project_root or _project_root_from_env()).resolve()
    return role_assignments_path(root)


def dashboard_preferences_path() -> Path:
    override = os.environ.get("GTKB_STARTUP_PREFERENCES_PATH")
    if override:
        return Path(override).expanduser().resolve()
    return DEFAULT_DASHBOARD_PREFERENCES_PATH


def lifecycle_guard_path(project_root: Path | None = None) -> Path:
    override = os.environ.get("GTKB_LIFECYCLE_GUARD_PATH")
    if override:
        return Path(override).expanduser().resolve()
    harness_name = _resolved_harness_name()
    if harness_name:
        return HARNESS_LIFECYCLE_GUARDS[harness_name].expanduser().resolve()
    root = (project_root or _project_root_from_env()).resolve()
    return root / LIFECYCLE_GUARD_RELATIVE_PATH


def application_label() -> str:
    return os.environ.get("GTKB_APPLICATION_LABEL") or DEFAULT_APPLICATION_LABEL


def gtkb_product_root() -> Path | None:
    """Return the resolved GT-KB product checkout root, or None if unresolvable.

    Resolution order:

    1. Explicit env override ``GTKB_PRODUCT_ROOT``.
    2. The current project root when it contains ``src/groundtruth_kb``.
    3. Otherwise, ``None`` (unknown/external paths stay ``neutral``).
    """

    override = os.environ.get("GTKB_PRODUCT_ROOT")
    if override:
        resolved = Path(override).expanduser()
        try:
            return resolved.resolve() if resolved.exists() else None
        except OSError:
            return None
    project = _project_root_from_env()
    candidate = project
    try:
        if candidate.is_dir() and (candidate / "src" / "groundtruth_kb").is_dir():
            return candidate.resolve()
    except OSError:
        return None
    return None


def _read_lifecycle_guard(project_root: Path | None = None) -> dict[str, Any]:
    path = lifecycle_guard_path(project_root)
    try:
        data = json.loads(path.read_text(encoding="utf-8-sig"))
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return {}
    return data if isinstance(data, dict) else {}


def _write_lifecycle_guard(state: dict[str, Any], project_root: Path | None = None) -> None:
    path = lifecycle_guard_path(project_root)
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    except OSError:
        pass


# ---- Canonical + legacy state read/write --------------------------------
def _canonical_default(project_root: Path | None = None) -> dict[str, Any]:
    root = (project_root or _project_root_from_env()).resolve()
    gtkb_root = gtkb_product_root()
    return {
        "schema_version": SCHEMA_VERSION,
        "current_subject": DEFAULT_SUBJECT,
        "application_id": None,
        "updated_at": None,
        "updated_by": "default",
        "source": "startup default",
        "project_root": str(root),
        "gtkb_root": str(gtkb_root) if gtkb_root else None,
        "role_slot": ROLE_SLOT_DEFAULT,
        "topology_mode": TOPOLOGY_MODE_DEFAULT,
    }


def _read_canonical_file(project_root: Path | None = None) -> dict[str, Any] | None:
    try:
        data = json.loads(state_path(project_root).read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return None
    return data if isinstance(data, dict) else None


def _read_legacy_file(project_root: Path | None = None) -> dict[str, Any] | None:
    try:
        data = json.loads(legacy_state_path(project_root).read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return None
    return data if isinstance(data, dict) else None


def _normalize_subject(value: Any) -> str:
    if isinstance(value, str) and value in FOCUS_LABELS:
        return value
    return DEFAULT_SUBJECT


def _with_compat_keys(canonical: dict[str, Any]) -> dict[str, Any]:
    """Attach legacy-shape keys to a canonical state dict for back-compat callers."""

    subject = _normalize_subject(canonical.get("current_subject"))
    merged = dict(canonical)
    merged.update(
        {
            "default_focus": DEFAULT_FOCUS,
            "current_focus": subject,
            "application_label": application_label(),
        }
    )
    return merged


def load_state(project_root: Path | None = None) -> dict[str, Any]:
    """Load work-subject state, preferring canonical file, else migrating legacy shape.

    Returned dict carries BOTH the canonical schema keys (``current_subject``,
    ``schema_version``, ``project_root``, ``gtkb_root``, ``role_slot``,
    ``source``, ``updated_at``, ``updated_by``) and legacy-compat keys
    (``current_focus``, ``default_focus``, ``application_label``) so existing
    callers continue to work.
    """

    canonical_raw = _read_canonical_file(project_root)
    if canonical_raw is not None:
        state = _canonical_default(project_root)
        for key in (
            "schema_version",
            "current_subject",
            "application_id",
            "updated_at",
            "updated_by",
            "source",
            "project_root",
            "gtkb_root",
            "role_slot",
            "topology_mode",
        ):
            if key in canonical_raw:
                state[key] = canonical_raw[key]
        state["current_subject"] = _normalize_subject(state.get("current_subject"))
        if state.get("topology_mode") not in _TOPOLOGY_MODES:
            state["topology_mode"] = TOPOLOGY_MODE_DEFAULT
        return _with_compat_keys(state)

    legacy_raw = _read_legacy_file(project_root)
    state = _canonical_default(project_root)
    if legacy_raw is not None:
        legacy_subject = _normalize_subject(legacy_raw.get("current_focus"))
        state.update(
            {
                "current_subject": legacy_subject,
                "updated_at": legacy_raw.get("updated_at"),
                "updated_by": legacy_raw.get("updated_by") or "legacy_migration",
                "source": "legacy workstream alias",
            }
        )
    return _with_compat_keys(state)


def save_state(
    focus: str,
    project_root: Path | None = None,
    *,
    updated_by: str = "owner_prompt",
    source: str | None = None,
    application_id: str | None = None,
) -> dict[str, Any]:
    """Persist the canonical work-subject state under ``.claude/session/work-subject.json``."""

    if focus not in FOCUS_LABELS:
        raise ValueError(f"Unknown work subject: {focus}")

    state = _canonical_default(project_root)
    state.update(
        {
            "current_subject": focus,
            "application_id": application_id if focus == FOCUS_APPLICATION else None,
            "updated_at": _now_iso(),
            "updated_by": updated_by,
            "source": source or _infer_source(updated_by),
        }
    )
    # Slice 1 of gtkb-operating-mode-transaction-001: derive topology_mode
    # from the live role-map rather than relying on the canonical default.
    # When derivation fails (missing/unreadable role map), keep the canonical
    # default so legacy behavior is preserved.
    try:
        from groundtruth_kb.mode_switch.derive import topology_from_role_map

        root = project_root if project_root is not None else _project_root_from_env()
        # WI-3342 IP-4: topology resolves from the harness registry projection
        # via the IP-3 foundational loader (load_role_assignments now reads the
        # projection); the retired role mirror is no longer read here.
        role_map = load_role_assignments(root)
        if role_map.get("harnesses"):
            state["topology_mode"] = topology_from_role_map(role_map)
    except Exception:  # noqa: BLE001 - fail-soft to canonical default
        pass
    path = state_path(project_root)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return _with_compat_keys(state)


def _infer_source(updated_by: str) -> str:
    if updated_by == "owner_prompt":
        return "standalone owner command"
    if updated_by == "legacy_migration":
        return "legacy workstream alias"
    if updated_by == "reset":
        return "reset"
    return "startup default"


def reset_state(project_root: Path | None = None) -> dict[str, Any]:
    return save_state(DEFAULT_FOCUS, project_root, updated_by="reset")


def focus_label(focus: str) -> str:
    return FOCUS_LABELS.get(focus, FOCUS_LABELS[DEFAULT_FOCUS])


def normalize_focus_command(prompt: str) -> str:
    text = prompt.strip().lower()
    text = re.sub(r"^[\s,.;:!?]*(please[\s,.;:!?]+)?", "", text)
    text = re.sub(r"[\s,.;:!?]*(please)?[\s,.;:!?]*$", "", text)
    text = re.sub(r"\s+", " ", text)
    return text


def focus_from_prompt(prompt: str) -> str | None:
    """Recognize a standalone work-subject command (new + legacy aliases)."""

    normalized = normalize_focus_command(prompt)
    if normalized in WORK_SUBJECT_APPLICATION_COMMANDS or normalized in APPLICATION_FOCUS_COMMANDS:
        return FOCUS_APPLICATION
    if normalized in WORK_SUBJECT_GTKB_COMMANDS or normalized in GTKB_FOCUS_COMMANDS:
        return FOCUS_GTKB_INFRASTRUCTURE
    return None


# Alias for clarity in new callers; identical behavior.
def work_subject_from_prompt(prompt: str) -> str | None:
    return focus_from_prompt(prompt)


def role_command_from_prompt(prompt: str) -> str | None:
    normalized = normalize_focus_command(prompt)
    if normalized in ROLE_TOGGLE_NEXT_SESSION_COMMANDS:
        return "toggle"
    if normalized in PRIME_BUILDER_NEXT_SESSION_COMMANDS:
        return ROLE_PRIME_BUILDER
    if normalized in LOYAL_OPPOSITION_NEXT_SESSION_COMMANDS:
        return ROLE_LOYAL_OPPOSITION
    return None


def dashboard_command_from_prompt(prompt: str) -> bool | None:
    normalized = normalize_focus_command(prompt)
    if normalized in DASHBOARD_ENABLE_COMMANDS:
        return True
    if normalized in DASHBOARD_DISABLE_COMMANDS:
        return False
    return None


def _role_label(role: str) -> str:
    return {
        ROLE_PRIME_BUILDER: "Prime Builder",
        ROLE_LOYAL_OPPOSITION: "Loyal Opposition",
        ROLE_ACTING_PRIME_BUILDER: "Acting Prime Builder",
    }.get(role, role)


def _read_active_role(project_root: Path | None = None) -> str:
    role, _document, _path = role_for_harness(
        (project_root or _project_root_from_env()).resolve(),
        harness_id=_resolved_harness_id(project_root),
        harness_name=_resolved_harness_name(),
        ensure_prime_on_startup=False,
    )
    return role if role in TOGGLEABLE_ROLE_PROFILES else ROLE_PRIME_BUILDER


def _next_toggled_role(current_role: str) -> str:
    return ROLE_PRIME_BUILDER if current_role == ROLE_LOYAL_OPPOSITION else ROLE_LOYAL_OPPOSITION


def _role_change_parity_message(role: str, project_root: Path | None = None) -> str:
    root = (project_root or _project_root_from_env()).resolve()
    harness_name = _resolved_harness_name()
    harness_scope = _normalize_harness_name_from_roles(harness_name) or "all"
    if harness_scope not in {"claude", "codex"}:
        harness_scope = "all"
    try:
        from scripts.check_harness_parity import check_harness_parity  # noqa: PLC0415

        report = check_harness_parity(root, harness=harness_scope, role=role)
    except Exception as exc:  # noqa: BLE001 - role command must still complete with visible diagnostic
        return f" Harness parity check unavailable: {exc}."
    counts = ", ".join(f"{key}={value}" for key, value in sorted(report.counts.items())) or "no counts"
    return f" Harness parity after role change: {report.overall_status} ({counts})."


def set_next_session_role(role: str, project_root: Path | None = None) -> str:
    if role not in {ROLE_PRIME_BUILDER, ROLE_LOYAL_OPPOSITION}:
        raise ValueError(f"Unsupported next-session role: {role}")
    set_harness_role(
        (project_root or _project_root_from_env()).resolve(),
        role,
        harness_id=_resolved_harness_id(project_root),
        harness_name=_resolved_harness_name(),
    )
    return role


def handle_role_command(prompt: str, project_root: Path | None = None) -> dict[str, str] | None:
    requested = role_command_from_prompt(prompt)
    if requested is None:
        return None
    current_role = _read_active_role(project_root)
    next_role = _next_toggled_role(current_role) if requested == "toggle" else requested
    set_next_session_role(next_role, project_root)
    role_path = operating_role_path(project_root)
    try:
        role_path_display = role_path.relative_to((project_root or _project_root_from_env()).resolve()).as_posix()
    except ValueError:
        role_path_display = str(role_path)
    return {
        "systemMessage": (
            f"Next fresh-session operating mode set to {_role_label(next_role)}. "
            f"This updates `{role_path_display}` for harness `{_resolved_harness_id(project_root) or 'unidentified'}`; "
            "the current session role is unchanged."
            f"{_role_change_parity_message(next_role, project_root)}"
        )
    }


def set_dashboard_auto_launch(enabled: bool) -> dict[str, Any]:
    path = dashboard_preferences_path()
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        data = {}
    if not isinstance(data, dict):
        data = {}
    data["open_dashboard_on_session_start"] = enabled
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return data


def handle_dashboard_command(prompt: str) -> dict[str, str] | None:
    enabled = dashboard_command_from_prompt(prompt)
    if enabled is None:
        return None
    set_dashboard_auto_launch(enabled)
    state = "enabled" if enabled else "disabled"
    return {
        "systemMessage": (
            f"Dashboard auto-launch is {state} for future sessions. "
            "This updates the user-local Codex startup preferences file."
        )
    }


def startup_focus_snapshot(project_root: Path | None = None) -> dict[str, str | None]:
    state = load_state(project_root)
    current = str(state["current_focus"])
    return {
        "default_focus": DEFAULT_FOCUS,
        "default_label": focus_label(DEFAULT_FOCUS),
        "current_focus": current,
        "current_label": focus_label(current),
        "application_label": str(state["application_label"]),
        "updated_at": state.get("updated_at"),
        "role_slot": str(state.get("role_slot") or ROLE_SLOT_DEFAULT),
        "topology_mode": str(state.get("topology_mode") or TOPOLOGY_MODE_DEFAULT),
    }


def render_startup_focus_lines(
    snapshot: dict[str, str | None] | None = None,
    *,
    include_operational_instructions: bool = True,
) -> str:
    """Render the Active Work Subject block with Phase-7 ``work subject`` language."""

    snapshot = snapshot or startup_focus_snapshot()
    app_label = snapshot["application_label"] or DEFAULT_APPLICATION_LABEL
    role_slot = snapshot.get("role_slot") or ROLE_SLOT_DEFAULT
    topology_mode = snapshot.get("topology_mode") or TOPOLOGY_MODE_DEFAULT
    lines = [
        f"- Default work subject: {snapshot['default_label']}",
        f"- Current work subject: {snapshot['current_label']}",
        f"- Application label: {app_label}",
        f"- Work-subject bridge role slot: `{role_slot}` (shared, prime-builder, or loyal-opposition).",
        f"- Harness topology: `{topology_mode}` (single_harness or multi_harness).",
        "- GT-KB is the default work subject; owner direction is interpreted as GroundTruth-KB work unless Mike explicitly names an adopter application.",
        "- Application work subject means owner direction is interpreted as work on a named adopter/demo application such as Agent Red.",
        "- Application work subject commands: `work subject application`, `application mode`, `app mode`, `agent red mode`.",
        "- GT-KB work subject commands: `work subject GT-KB`, `GT-KB mode`, `GT-KB infrastructure mode`, `GroundTruth-KB mode`.",
        "- Canonical state file: `.claude/session/work-subject.json` (legacy `.claude/hooks/.workstream-focus-state.json` migrated on next owner command).",
    ]
    if include_operational_instructions:
        lines.extend(
            [
                "- First owner message in a fresh session is routed through the init-keyword matcher: matches relay startup disclosure; non-matches pass through as ordinary task input.",
                "- Live bridge authority: dispatcher/TAFE state plus status-bearing numbered bridge files; poller status, scan-freshness files, and startup snapshots are non-canonical.",
            ]
        )
    return "\n".join(lines)


def render_active_work_subject(
    project_root: Path | None = None,
    *,
    snapshot: dict[str, str | None] | None = None,
    overlay_status: dict[str, Any] | None = None,
    include_counterpart: bool = True,
    include_overlay_note: bool = True,
    include_operational_instructions: bool = True,
) -> str:
    """Render the enriched Active Work Subject block (Slice 1 §A).

    Composes ``render_startup_focus_lines`` with an overlay status line (§C)
    and, when ``include_counterpart`` is True, a counterpart-state warning
    summary (§E). Overlay and counterpart outputs are always informational —
    the startup report never treats them as canonical.
    """

    lines = [
        render_startup_focus_lines(
            snapshot or startup_focus_snapshot(project_root),
            include_operational_instructions=include_operational_instructions,
        )
    ]
    if include_overlay_note:
        overlay_note = overlay_startup_note(overlay_status or {})
        lines.extend(f"- {line}" for line in overlay_note["lines"])
    if include_counterpart:
        counterpart = detect_counterpart_state(project_root)
        for warning in counterpart["warnings"]:
            lines.append(f"- WARNING: counterpart harness — {warning}")
        if not counterpart["warnings"] and counterpart["counterpart_present"]:
            lines.append("- Counterpart harness detected; no role or subject conflicts.")
    return "\n".join(lines)


# ---- §C Overlay-aware startup -------------------------------------------


def overlay_startup_note(status: dict[str, Any]) -> dict[str, Any]:
    """Map a session overlay status dict to a startup-block level + lines.

    - Absent → informational note. No warning.
    - Stale / root_mismatch / subject_mismatch / projection_diff → WARNING.
    - Overlays are never canonical for DA/MemBase/bridge/readiness decisions.
    """

    if not status.get("overlay_present"):
        return {
            "level": "info",
            "lines": ["No session overlay active; startup context from live files."],
        }

    warnings: list[str] = []
    if status.get("is_stale"):
        warnings.append(
            "WARNING: session overlay is stale (source hash mismatch or expired entries); "
            "treat overlay contents as non-canonical."
        )
    if status.get("root_mismatch"):
        warnings.append(
            "WARNING: session overlay references a different project root than the active "
            "session; ignore overlay for routing decisions."
        )
    if status.get("subject_mismatch"):
        warnings.append(
            "WARNING: session overlay work subject differs from the active subject; overlay is informational only."
        )
    if status.get("projection_diff"):
        warnings.append(
            "WARNING: session overlay projection differs from live state; rely on live "
            "files for readiness and bridge decisions."
        )
    if warnings:
        warnings.append(
            "Session overlays are never canonical for Deliberation Archive, MemBase, bridge, or readiness decisions."
        )
        return {"level": "warning", "lines": warnings}

    return {
        "level": "info",
        "lines": [
            "Session overlay present and fresh; overlay is informational only, "
            "canonical state lives in KB/MemBase/Deliberation Archive/source files.",
        ],
    }


# ---- §E Counterpart state detection -------------------------------------


def _read_counterpart_subject(path: Path) -> str | None:
    """Read a harness's lifecycle-guard JSON and return its recorded subject.

    Returns ``None`` when the file is missing, unreadable, malformed, or does
    not record a current_subject.
    """

    try:
        data = json.loads(path.expanduser().read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return None
    if not isinstance(data, dict):
        return None
    subject = data.get("current_subject")
    return subject if isinstance(subject, str) and subject else None


def _harness_state_records_for_project(
    project_root: Path,
) -> tuple[Path, dict[str, Path]]:
    """Build harness role-map and lifecycle-guard paths rooted at project_root.

    Mirrors the module-level ``HARNESS_LIFECYCLE_GUARDS`` constants but builds them from a passed
    ``project_root`` rather than from this module's ``PROJECT_ROOT`` (which
    is computed from ``__file__`` at import time and resolves to the legacy
    root when this module is imported from there — e.g., during the Slice 11
    rehearsal lane subprocess).

    Per bridge/harness-state-preferences-path-cli-2026-04-28-004.md Codex
    NO-GO Required Revision Option 1 (preferred): fix at the class boundary
    so ``detect_counterpart_state`` does not iterate canonical-bound
    module-level dictionaries when called with a sandbox project_root.
    """
    state_root = project_root / "harness-state"
    lifecycle_guards: dict[str, Path] = {
        "codex": state_root / "codex" / "session-lifecycle-guard.json",
        "claude": state_root / "claude" / "session-lifecycle-guard.json",
    }
    return state_root / "harness-registry.json", lifecycle_guards


def detect_counterpart_state(project_root: Path | None = None) -> dict[str, Any]:
    """Detect role-slot and subject conflicts with the counterpart harness (§E).

    Returns ``{"counterpart_present", "same_role_slot", "subject_mismatch",
    "warnings"}``. Warnings are only emitted when counterpart state files are
    present; missing files yield no warnings and no crash.

    When ``project_root`` is provided, harness-state role-map/guard paths are
    resolved relative to that root (sandbox-aware execution). When omitted,
    falls back to the canonical module-level constants (production default
    where this module is imported from the canonical project root).
    """

    if project_root is not None:
        assignment_path, lifecycle_guards = _harness_state_records_for_project(project_root)
        root = project_root.resolve()
    else:
        root = _project_root_from_env()
        assignment_path = role_assignments_path(root)
        lifecycle_guards = HARNESS_LIFECYCLE_GUARDS

    current_harness = _resolved_harness_name()
    current_harness_id = _resolved_harness_id(root)
    role_document = load_role_assignments(root, assignment_path)
    # Per IP-8 of gtkb-single-harness-bridge-dispatcher-001 (Codex GO at -014),
    # role records carry a role-set (list-of-strings wire form). Build a
    # per-harness map of role-set values rather than scalar role values so
    # downstream set-membership comparisons work for both singleton sets
    # (multi-harness topology) and multi-element sets (single-harness mode).
    per_harness_role_sets: dict[str, frozenset[str]] = {}
    harnesses = role_document.get("harnesses", {})
    if isinstance(harnesses, dict):
        for harness_id, record in harnesses.items():
            if not isinstance(record, dict):
                continue
            role_set = _normalize_role_field(record.get("role"))
            # Keep records whose role-set has any toggleable role; the legacy
            # check considered acting-prime-builder a valid toggle role too.
            if not (role_set & TOGGLEABLE_ROLE_PROFILES):
                continue
            harness_type = str(record.get("harness_type") or harness_id).strip().lower()
            per_harness_role_sets[harness_type] = role_set

    counterpart_present = any(
        harness != current_harness and harness in per_harness_role_sets for harness in DEFAULT_HARNESS_IDS
    )

    def _role_set_display_label(role_set: frozenset[str]) -> str:
        """Render a role-set for warning text.

        Singleton sets display as the bare token (preserves the legacy scalar
        log shape that tests pin on). Multi-element sets display as
        ``+`` -separated sorted tokens so single-harness mode warnings remain
        unambiguous.
        """
        tokens = sorted(role_set & TOGGLEABLE_ROLE_PROFILES)
        if not tokens:
            return ""
        if len(tokens) == 1:
            return tokens[0]
        return "+".join(tokens)

    warnings: list[str] = []
    same_role_slot = False
    if current_harness and current_harness in per_harness_role_sets:
        our_role_set = per_harness_role_sets[current_harness]
        our_label = _role_set_display_label(our_role_set)
        for harness, role_set in per_harness_role_sets.items():
            if harness == current_harness:
                continue
            # Two distinct harnesses sharing any toggleable role token =
            # same-role-slot conflict (the existing semantic). Set-membership
            # generalizes the prior scalar equality cleanly; the warning text
            # lists the overlapping role tokens explicitly.
            overlap = (role_set & our_role_set) & TOGGLEABLE_ROLE_PROFILES
            their_label = _role_set_display_label(role_set)
            if overlap:
                same_role_slot = True
                overlap_label = "+".join(sorted(overlap))
                warnings.append(
                    f"both `{current_harness}` and `{harness}` have role=`{overlap_label}` "
                    "— counterpart bridge roles may collide; verify harness-state/harness-registry.json (canonical role registry)."
                )
            elif role_set & TOGGLEABLE_ROLE_PROFILES and our_role_set & TOGGLEABLE_ROLE_PROFILES and not overlap:
                warnings.append(
                    f"`{current_harness}` is `{our_label}`; counterpart `{harness}` is `{their_label}`. "
                    "Treat bridge message authority per harness-state/harness-registry.json (canonical role registry)."
                )

    # Read OUR subject from our own per-harness lifecycle-guard so divergence
    # detection is symmetric across harnesses (per bridge -014 P1). The shared
    # canonical work-subject file cannot represent multi-harness divergence;
    # reading it for the active-harness side of the comparison would let one
    # harness silently miss a split that the other harness correctly warns on.
    # Falls back to the canonical state only when the local guard has no
    # current_subject recorded (e.g., pre-upgrade session where the writer
    # hadn't yet been extended).
    subject_mismatch = False
    our_subject: str | None = None
    our_guard_path = lifecycle_guards.get(current_harness) if current_harness else None
    if our_guard_path is not None:
        our_subject = _read_counterpart_subject(our_guard_path)
    if our_subject is None:
        try:
            our_subject = str(load_state(project_root).get("current_subject") or "") or None
        except Exception:
            our_subject = None
    for harness, guard_path in lifecycle_guards.items():
        if harness == current_harness:
            continue
        counterpart_subject = _read_counterpart_subject(guard_path)
        if counterpart_subject is not None and our_subject is not None and counterpart_subject != our_subject:
            subject_mismatch = True
            warnings.append(
                f"counterpart `{harness}` records work subject=`{counterpart_subject}` "
                f"while `{current_harness or 'local'}` is on `{our_subject}` — "
                "verify both harnesses intend this split."
            )

    return {
        "counterpart_present": counterpart_present,
        "same_role_slot": same_role_slot,
        "subject_mismatch": subject_mismatch,
        "current_harness_id": current_harness_id,
        "prime_harness_ids": current_prime_ids(role_document),
        "warnings": warnings,
    }


# ---- §A Readiness hard-rejection ----------------------------------------


class SubjectScopeError(RuntimeError):
    """Raised when a readiness/report output would emit a combined application + GT-KB

    green claim without an explicit dual-scope declaration (§A hard rejection).
    """


def assert_readiness_subject_scope(
    *,
    application_green: bool,
    gtkb_green: bool,
    dual_scope_declared: bool,
    context: str = "release readiness",
) -> None:
    """Hard-reject unlabeled combined application + GT-KB green claims.

    Raises ``SubjectScopeError`` when both ``application_green`` and
    ``gtkb_green`` are True but ``dual_scope_declared`` is False. Callers must
    provide an explicit dual-scope declaration before emitting combined green
    claims at the readiness/report layer (not just at the startup model layer).
    """

    if application_green and gtkb_green and not dual_scope_declared:
        raise SubjectScopeError(
            f"{context}: combined application + GT-KB green claim rejected — "
            "caller must pass an explicit dual-scope declaration identifying "
            "both subjects (application and GT-KB) before emitting a combined "
            "green claim. Use `work subject application` or `work subject GT-KB` "
            "to scope the claim, or provide a dual-scope justification."
        )


def system_message_for_state(state: dict[str, Any], *, changed: bool = False) -> str:
    subject = str(state.get("current_subject") or state.get("current_focus") or DEFAULT_SUBJECT)
    label = focus_label(subject)
    app_label = str(state.get("application_label") or DEFAULT_APPLICATION_LABEL)
    verb = "set to" if changed else "is"
    if subject == FOCUS_GTKB_INFRASTRUCTURE:
        return (
            f"Current work subject {verb} {label}. "
            "Interpret owner direction as GroundTruth-KB infrastructure work. "
            f"Application ({app_label}) source mutations require standalone `work subject application` or a verification need."
        )
    return (
        f"Current work subject {verb} {label}. "
        f"Interpret owner direction as work on the application ({app_label}) by default. "
        "GT-KB baseline infrastructure changes require standalone `work subject GT-KB` or the existing formal approval path."
    )


_CANONICAL_DISPATCH_INIT_RE = re.compile(r"^::init\s+gtkb\s+(?P<role_mode>pb|lo)\s*$", re.IGNORECASE)

_PROMPT_EXPLICIT_ROLE_HINTS = (
    (
        "pb",
        re.compile(
            r"\byou\s+are\s+authorized\s+to\s+operate\s+as\s+(?:an?\s+)?(?:autonomous\s+)?prime\s+builder\b",
            re.IGNORECASE,
        ),
    ),
    (
        "pb",
        re.compile(
            r"\byou\s+are\s+(?:now\s+)?(?:operating|acting|running)\s+as\s+(?:an?\s+)?prime\s+builder\b",
            re.IGNORECASE,
        ),
    ),
    (
        "lo",
        re.compile(
            r"\byou\s+are\s+authorized\s+to\s+operate\s+as\s+(?:an?\s+)?loyal\s+opposition\b",
            re.IGNORECASE,
        ),
    ),
    (
        "lo",
        re.compile(
            r"\byou\s+are\s+(?:now\s+)?(?:operating|acting|running)\s+as\s+(?:an?\s+)?loyal\s+opposition\b",
            re.IGNORECASE,
        ),
    ),
)


def _match_startup_init_keyword(prompt: str) -> InitKeywordMatch | None:
    match = match_init_keyword(prompt)
    if match is not None:
        return match
    if _CANONICAL_DISPATCH_INIT_RE.match(prompt.strip()):
        return InitKeywordMatch(app_scope="gtkb", mode="default")
    return None


def _startup_role_mode_from_prompt(prompt: str) -> str | None:
    match = _CANONICAL_DISPATCH_INIT_RE.match(prompt.strip())
    if match is None:
        return None
    return match.group("role_mode").lower()


def _explicit_role_hint_mode_from_prompt(prompt: str) -> str | None:
    """Return a role mode when the prompt explicitly declares this agent's role.

    This is the ordinary-prompt counterpart to ``::init gtkb pb|lo``. The
    prompt declaration is authoritative for the receiving agent; the durable
    registry remains a fallback when no valid prompt/session hint exists.
    Ambiguous prompts that explicitly match both roles are ignored fail-soft.
    """

    matches = {mode for mode, pattern in _PROMPT_EXPLICIT_ROLE_HINTS if pattern.search(prompt)}
    if len(matches) == 1:
        return next(iter(matches))
    return None


# Slice 2 of PROJECT-GTKB-INTERACTIVE-SESSION-ROLE-OVERRIDE
# (bridge/gtkb-interactive-session-role-override-slice-2-session-role-marker-003.md,
# Codex GO at -004). Per ADR-INTERACTIVE-SESSION-ROLE-OVERRIDE-001 Decision 4
# and DCL-SESSION-ROLE-RESOLUTION-001 assertions 2/6/7: when the owner declares
# a session role via ``::init gtkb (pb|lo)`` in an interactive context, write
# marker state carrying the role and a non-null session id. The legacy
# single-file marker may be invalidated by SessionStart, but the WI-4540
# per-session marker/envelope authority persists across compaction/resume and is
# read by the shared resolver.
_MODE_TO_ROLE_PROFILE = {
    "pb": "prime-builder",
    "lo": "loyal-opposition",
}
_SESSION_ROLE_MARKER_NAME = "active-session-role.json"
# Marker-continuity env order is owned by scripts/gtkb_session_id.py (WI-4270
# shared resolver unification; bridge/gtkb-session-id-shared-resolver-
# unification-003 GO at -004). Delegate to the shared MARKER_CONTINUITY_ORDER
# (GTKB_SESSION_ID-first); behavior is identical to the prior local tuple. The
# dual import mirrors this module's top-level import style (scripts.* package
# path; bare name under direct script execution). The marker parity test
# (platform_tests/hooks/test_workstream_focus_session_role_marker.py) locks
# this to the canonical order.
try:
    from scripts.gtkb_session_id import MARKER_CONTINUITY_ORDER as _SESSION_ID_ENV_FALLBACKS
    from scripts.gtkb_session_id import per_session_role_marker_path as _per_session_role_marker_path
except ImportError:  # pragma: no cover - direct script execution path
    from gtkb_session_id import MARKER_CONTINUITY_ORDER as _SESSION_ID_ENV_FALLBACKS  # type: ignore[no-redef]
    from gtkb_session_id import per_session_role_marker_path as _per_session_role_marker_path  # type: ignore[no-redef]
_BRIDGE_DISPATCH_RUN_ID_ENV = "GTKB_BRIDGE_POLLER_RUN_ID"


def _session_role_marker_path(project_root: Path | None = None) -> Path:
    root = (project_root or _project_root_from_env()).resolve()
    return root / ".claude" / "session" / _SESSION_ROLE_MARKER_NAME


def _resolve_session_id(payload_session_id: Any) -> tuple[str | None, str | None]:
    """Resolve a non-null session id per the Slice 2 F1 fallback chain.

    Returns ``(session_id, source_label)``. Source label is ``"payload"`` when
    the id came from the hook payload, ``"env:<NAME>"`` when from an env var, or
    ``(None, None)`` when no non-null id is available (the fail-soft branch).
    Per DCL-SESSION-ROLE-RESOLUTION-001 assertion 6, callers MUST NOT persist a
    marker when this returns ``(None, None)``.
    """
    if isinstance(payload_session_id, str) and payload_session_id.strip():
        return payload_session_id.strip(), "payload"
    for env_name in _SESSION_ID_ENV_FALLBACKS:
        value = os.environ.get(env_name)
        if isinstance(value, str) and value.strip():
            return value.strip(), f"env:{env_name}"
    return None, None


def _write_session_role_marker(
    role_profile: str,
    session_id: str,
    session_id_source: str,
    project_root: Path | None = None,
    *,
    source: str = "init_keyword",
) -> bool:
    """Write the ephemeral session-state role marker; fail soft on OSError.

    Returns True on successful write, False if the directory or file could not
    be written. The caller decides whether to record a fail-soft event in the
    lifecycle guard.
    """
    import time

    marker_path = _session_role_marker_path(project_root)
    lock_path = marker_path.with_suffix(".lock")

    # Ensure parent directory exists before attempting lock creation
    try:
        marker_path.parent.mkdir(parents=True, exist_ok=True)
    except OSError:
        return False

    acquired = False
    for _attempt in range(5):
        try:
            with open(lock_path, "x") as f:
                f.write(str(os.getpid()))
            acquired = True
            break
        except FileExistsError:
            time.sleep(0.1)
        except OSError:
            try:
                marker_path.parent.mkdir(parents=True, exist_ok=True)
            except OSError:
                pass
            time.sleep(0.1)

    if not acquired:
        return False

    try:
        if marker_path.is_file():
            try:
                existing_data = json.loads(marker_path.read_text(encoding="utf-8"))
                if isinstance(existing_data, dict):
                    existing_session_id = existing_data.get("session_id")
                    existing_written_at = existing_data.get("written_at")
                    if existing_session_id and existing_written_at:
                        if existing_session_id != session_id:
                            parsed_dt = _parse_iso8601(existing_written_at)
                            if parsed_dt:
                                age = (datetime.now(UTC) - parsed_dt).total_seconds()
                                if age <= 1800:
                                    return False
            except (json.JSONDecodeError, OSError):
                pass

        body = {
            "role": role_profile,
            "session_id": session_id,
            "session_id_source": session_id_source,
            "written_at": _now_iso(),
            "source": source,
        }
        marker_path.write_text(
            json.dumps(body, ensure_ascii=True, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
            newline="\n",
        )
    except OSError:
        return False
    finally:
        try:
            if lock_path.is_file():
                lock_path.unlink()
        except OSError:
            pass
    return True


def _candidate_marker_session_ids(payload_session_id: Any) -> list[tuple[str, str]]:
    """Return ``(session_id, source_label)`` pairs to key per-session markers under.

    WI-4540 R-B1 (bridge -004): the per-session marker is written under the
    resolved payload/transcript id AND, defensively, under each currently-set
    session-id env candidate, so BOTH the resolver (which queries the raw
    payload/transcript id) and the WI-4534 guard (which resolves
    ``CLAUDE_CODE_SESSION_ID`` via the bridge work-intent order) find a marker
    keyed to the id they look up during the additive transition. The list is
    de-duplicated and order-stable: payload first, then ``MARKER_CONTINUITY_ORDER``.
    """
    pairs: list[tuple[str, str]] = []
    seen: set[str] = set()
    if isinstance(payload_session_id, str) and payload_session_id.strip():
        pid = payload_session_id.strip()
        pairs.append((pid, "payload"))
        seen.add(pid)
    for env_name in _SESSION_ID_ENV_FALLBACKS:
        value = os.environ.get(env_name)
        if isinstance(value, str) and value.strip():
            candidate = value.strip()
            if candidate not in seen:
                pairs.append((candidate, f"env:{env_name}"))
                seen.add(candidate)
    return pairs


def _write_per_session_role_marker(
    role_profile: str,
    session_id: str,
    session_id_source: str,
    project_root: Path | None = None,
    *,
    source: str = "init_keyword",
) -> bool:
    """Write a per-session role marker keyed to ``session_id``; fail soft.

    WI-4540: ``.claude/session/role-<sanitized_session_id>.json``. Per-session
    keying means no cross-session contention, so there is NO clobber-rejection
    heuristic (unlike the legacy shared single-file writer): the marker is the
    property of exactly one session id and is freely (re-)written by that
    session. Returns True on success, False on OSError.
    """
    root = project_root or _project_root_from_env()
    marker_path = _per_session_role_marker_path(root, session_id)
    try:
        marker_path.parent.mkdir(parents=True, exist_ok=True)
        body = {
            "role": role_profile,
            "session_id": session_id,
            "session_id_source": session_id_source,
            "written_at": _now_iso(),
            "source": source,
        }
        marker_path.write_text(
            json.dumps(body, ensure_ascii=True, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
            newline="\n",
        )
    except OSError:
        return False
    return True


def _write_per_session_role_markers(
    role_profile: str,
    candidates: list[tuple[str, str]],
    project_root: Path | None = None,
    *,
    source: str = "init_keyword",
) -> int:
    """Write a per-session marker for each candidate id (R-B1 multi-key).

    Returns the count of markers successfully written. Each write is
    independent and fail-soft, so a single unwritable id never aborts the rest.
    """
    written = 0
    for session_id, source_label in candidates:
        if _write_per_session_role_marker(role_profile, session_id, source_label, project_root, source=source):
            written += 1
    return written


def _record_explicit_role_hint_from_prompt(
    prompt: str,
    state: dict[str, Any],
    project_root: Path | None = None,
    *,
    session_id: str | None = None,
) -> bool:
    role_mode = _explicit_role_hint_mode_from_prompt(prompt)
    role_profile = _MODE_TO_ROLE_PROFILE.get(role_mode or "")
    if not role_profile:
        return False
    resolved_id, source_label = _resolve_session_id(session_id)
    if resolved_id is None:
        state["prompt_role_hint_marker_failsoft_at"] = _now_iso()
        state["prompt_role_hint_marker_failsoft_reason"] = "session_id_unresolved"
        state["prompt_role_hint_role"] = role_profile
        return True
    wrote = _write_session_role_marker(
        role_profile,
        resolved_id,
        source_label or "",
        project_root,
        source="prompt_explicit_role_hint",
    )
    if wrote:
        state["prompt_role_hint_marker_written_at"] = _now_iso()
        state["prompt_role_hint_role"] = role_profile
        state["prompt_role_hint_session_id_source"] = source_label
    else:
        state["prompt_role_hint_marker_failsoft_at"] = _now_iso()
        state["prompt_role_hint_marker_failsoft_reason"] = "marker_write_oserror"
        state["prompt_role_hint_role"] = role_profile
    # WI-4540: additively write the per-session marker(s) (R-B1 multi-key). The
    # per-session marker is the new authority for the guard/resolver; it is NOT
    # gated on the legacy single-file write result (per-session keying has no
    # cross-session contention, so a legacy clobber-rejection must not suppress
    # this session's own marker).
    per_session_written = _write_per_session_role_markers(
        role_profile,
        _candidate_marker_session_ids(session_id),
        project_root,
        source="prompt_explicit_role_hint",
    )
    if per_session_written:
        state["prompt_role_hint_per_session_markers_written"] = per_session_written
    return True


def _set_work_subject_from_init_match(
    init_match: InitKeywordMatch,
    project_root: Path | None = None,
) -> str | None:
    if init_match.app_scope == "gtkb":
        save_state(
            FOCUS_GTKB_INFRASTRUCTURE,
            project_root,
            updated_by="startup_init_keyword",
            source="startup init keyword",
        )
        return FOCUS_GTKB_INFRASTRUCTURE
    if init_match.app_scope == "agent_red":
        save_state(
            FOCUS_APPLICATION,
            project_root,
            updated_by="startup_init_keyword",
            source="startup init keyword",
            application_id="agent_red",
        )
        return FOCUS_APPLICATION
    return None


def _startup_diagnostic_dir(project_root: Path | None = None) -> Path:
    root = (project_root or _project_root_from_env()).resolve()
    harness_name = _resolved_harness_name()
    if harness_name == "codex":
        return root / ".codex" / "gtkb-hooks"
    if harness_name == "claude":
        return root / ".claude" / "hooks"
    return root / ".codex" / "gtkb-hooks"


STARTUP_RELAY_CACHE_NAME = "last-user-visible-startup.md"
STARTUP_RELAY_META_NAME = "last-user-visible-startup.meta.json"
_STARTUP_CACHE_READ_COMMAND_RE = re.compile(
    r"^\s*Get-Content\s+"
    r"(?:(?:-Raw\s+)?-LiteralPath\s+(?P<path_a>'[^']+'|\"[^\"]+\"|[^\s]+)(?:\s+-Raw)?"
    r"|-LiteralPath\s+(?P<path_b>'[^']+'|\"[^\"]+\"|[^\s]+)\s+-Raw"
    r"|-Raw\s+(?P<path_c>'[^']+'|\"[^\"]+\"|[^\s]+))"
    r"\s*$",
    re.IGNORECASE,
)
_STARTUP_CACHE_READ_FORBIDDEN_TOKENS = (";", "|", "&", ">", "<", "`", "$(")


def _startup_relay_cache_paths(root: Path, role_mode: str | None = None) -> tuple[Path, Path]:
    """Harness-scoped startup-disclosure relay cache file and metadata sidecar.

    The cache is harness-scoped (under the active harness's hooks directory),
    so a Loyal Opposition session never reads a Prime Builder disclosure and
    vice versa.
    """
    diag = _startup_diagnostic_dir(root)
    if role_mode in {"pb", "lo"}:
        return (
            diag / f"last-user-visible-startup-{role_mode}.md",
            diag / f"last-user-visible-startup-{role_mode}.meta.json",
        )
    return (diag / STARTUP_RELAY_CACHE_NAME, diag / STARTUP_RELAY_META_NAME)


def _startup_relay_cache_fresh(meta: dict[str, Any], project_root: Path) -> bool:
    """Return true when relay cache metadata belongs to the active startup gate."""

    generated_at = _parse_iso8601(meta.get("generated_at"))
    if generated_at is None:
        return False
    state = _read_lifecycle_guard(project_root)
    reference_at = _parse_iso8601(state.get("startup_prompt_discarded_at") or state.get("armed_at"))
    if reference_at is None:
        reference_at = datetime.now(UTC)
    age_seconds = (reference_at - generated_at).total_seconds()
    if age_seconds > STARTUP_RELAY_CACHE_MAX_AGE_SECONDS:
        return False
    return -age_seconds <= STARTUP_RELAY_CACHE_FUTURE_SKEW_SECONDS


def _startup_relay_refresh_timeout_seconds() -> float:
    raw_value = os.environ.get("GTKB_STARTUP_RELAY_REFRESH_TIMEOUT_SECONDS")
    if raw_value is None:
        return STARTUP_RELAY_REFRESH_TIMEOUT_SECONDS
    try:
        value = float(raw_value)
    except ValueError:
        return STARTUP_RELAY_REFRESH_TIMEOUT_SECONDS
    return max(0.01, min(value, STARTUP_RELAY_REFRESH_TIMEOUT_SECONDS))


def _refresh_startup_relay_cache_bounded(root: Path, *, role_mode: str | None, meta: dict[str, Any]) -> bool:
    """Best-effort stale relay-cache refresh, bounded for UserPromptSubmit hooks."""

    result_queue: queue.Queue[bool] = queue.Queue(maxsize=1)
    cancel = threading.Event()

    def _refresh() -> None:
        try:
            try:
                from scripts import session_start_dispatch_core as _core
            except ImportError:
                import session_start_dispatch_core as _core
            _core.HARNESS_NAME = _resolved_harness_name() or "codex"
            _core.OUT_DIR = _startup_diagnostic_dir(root)
            role_mode_to_use = role_mode or meta.get("role_mode") or "pb"
            role_profile = _core._MODE_TO_ROLE_PROFILE.get(role_mode_to_use)
            if not role_profile:
                result_queue.put(False)
                return
            report = _core._render_role_startup_report(role_profile)
            if not report or cancel.is_set():
                result_queue.put(False)
                return
            _core._write_startup_relay_cache(report, role_mode=role_mode)
            result_queue.put(True)
        except Exception:
            try:
                result_queue.put(False)
            except queue.Full:
                pass

    worker = threading.Thread(target=_refresh, name="gtkb-startup-relay-refresh", daemon=True)
    worker.start()
    worker.join(_startup_relay_refresh_timeout_seconds())
    if worker.is_alive():
        cancel.set()
        return False
    try:
        return result_queue.get_nowait()
    except queue.Empty:
        return False


def _allowed_startup_relay_cache_reads(root: Path) -> set[Path]:
    allowed: set[Path] = set()
    for role_mode in (None, "pb", "lo"):
        cache_path, _meta_path = _startup_relay_cache_paths(root, role_mode)
        allowed.add(cache_path.resolve())
    return allowed


def _candidate_startup_cache_read_path(raw_path: str, root: Path) -> Path | None:
    path_text = raw_path.strip().strip("'\"")
    if not path_text:
        return None
    candidate = Path(path_text)
    if not candidate.is_absolute():
        candidate = root / candidate
    return candidate.resolve()


def _is_startup_relay_cache_read(payload: dict[str, Any], project_root: Path | None = None) -> bool:
    """Allow the one read needed to relay an init-keyword startup disclosure."""

    tool_name = str(payload.get("tool_name") or "")
    if tool_name not in {"Bash", "shell_command"}:
        return False
    tool_input = payload.get("tool_input") or {}
    if not isinstance(tool_input, dict):
        return False
    command = str(tool_input.get("command") or "")
    if not command.strip():
        return False
    if any(token in command for token in _STARTUP_CACHE_READ_FORBIDDEN_TOKENS):
        return False
    match = _STARTUP_CACHE_READ_COMMAND_RE.match(command)
    if match is None:
        return False
    raw_path = match.group("path_a") or match.group("path_b") or match.group("path_c")
    if raw_path is None:
        return False
    root = (project_root or _project_root_from_env()).resolve()
    candidate = _candidate_startup_cache_read_path(raw_path, root)
    return candidate in _allowed_startup_relay_cache_reads(root)


def _startup_relay_pointer(project_root: Path | None = None, *, role_mode: str | None = None) -> dict[str, Any] | None:
    """Read the harness-scoped startup-disclosure relay cache and metadata.

    Returns a bounded pointer dict, or None when the cache file or its
    metadata sidecar is missing, empty, or malformed. The relay path consults
    only this harness-scoped cache: bridge auto-dispatch SessionStart payloads
    never populate it, and the shared dashboard report is not a fallback.
    """
    root = (project_root or _project_root_from_env()).resolve()
    cache_path, meta_path = _startup_relay_cache_paths(root, role_mode)
    try:
        body = cache_path.read_text(encoding="utf-8")
    except OSError:
        return None
    if not body.strip():
        return None
    try:
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    if not isinstance(meta, dict):
        return None
    actual_bytes = body.encode("utf-8")
    actual_sha = hashlib.sha256(actual_bytes).hexdigest()
    harness_ok = meta.get("harness_name") in (None, _resolved_harness_name())
    harness_id = _resolved_harness_id(root)
    harness_id_ok = meta.get("harness_id") in (None, harness_id)
    role_ok = role_mode is None or meta.get("role_mode") == role_mode
    disclosure_ok = "# GroundTruth-KB Fresh Session Startup" in body and "## Startup Disclosure" in body
    relay_identity_ok = harness_ok and harness_id_ok and role_ok and disclosure_ok
    content_matches_meta = meta.get("sha256") == actual_sha and meta.get("byte_length") == len(actual_bytes)
    consistent_except_freshness = relay_identity_ok and content_matches_meta
    freshness_ok = _startup_relay_cache_fresh(meta, root)
    headless_dispatch = bool(os.environ.get("GTKB_BRIDGE_POLLER_RUN_ID"))
    recoverable_content_drift = relay_identity_ok and not content_matches_meta

    if relay_identity_ok and (not freshness_ok or recoverable_content_drift) and not headless_dispatch:
        refreshed = _refresh_startup_relay_cache_bounded(root, role_mode=role_mode, meta=meta)
        if refreshed:
            try:
                body = cache_path.read_text(encoding="utf-8")
                meta = json.loads(meta_path.read_text(encoding="utf-8"))
                actual_bytes = body.encode("utf-8")
                actual_sha = hashlib.sha256(actual_bytes).hexdigest()
                harness_ok = meta.get("harness_name") in (None, _resolved_harness_name())
                harness_id_ok = meta.get("harness_id") in (None, harness_id)
                role_ok = role_mode is None or meta.get("role_mode") == role_mode
                disclosure_ok = "# GroundTruth-KB Fresh Session Startup" in body and "## Startup Disclosure" in body
                relay_identity_ok = harness_ok and harness_id_ok and role_ok and disclosure_ok
                content_matches_meta = meta.get("sha256") == actual_sha and meta.get("byte_length") == len(actual_bytes)
                consistent_except_freshness = relay_identity_ok and content_matches_meta
                freshness_ok = _startup_relay_cache_fresh(meta, root)
            except (OSError, json.JSONDecodeError):
                pass

    consistent = consistent_except_freshness and freshness_ok
    try:
        rel_path = cache_path.relative_to(root).as_posix()
    except ValueError:
        rel_path = cache_path.as_posix()
    return {
        "cache_path": rel_path,
        "byte_length": len(actual_bytes),
        "sha256": actual_sha,
        "harness_id": meta.get("harness_id"),
        "role_mode": meta.get("role_mode"),
        "generated_at": meta.get("generated_at"),
        "fresh": freshness_ok,
        "consistent": consistent,
    }


def _startup_role_mode_from_registry(project_root: Path | None = None) -> str | None:
    root = (project_root or _project_root_from_env()).resolve()
    if not (root / ROLE_ASSIGNMENTS_RELATIVE_PATH).is_file():
        return None
    try:
        role, _document, _path = role_for_harness(
            root,
            harness_id=_resolved_harness_id(root),
            harness_name=_resolved_harness_name(),
            ensure_prime_on_startup=False,
        )
    except Exception:  # noqa: BLE001 - init-keyword relay must fail soft.
        return None
    if role == ROLE_LOYAL_OPPOSITION:
        return "lo"
    if role in {ROLE_PRIME_BUILDER, ROLE_ACTING_PRIME_BUILDER}:
        return "pb"
    return None


def _startup_effective_role_mode(prompt: str, project_root: Path | None = None) -> str | None:
    return _startup_role_mode_from_prompt(prompt) or _startup_role_mode_from_registry(project_root)


def _startup_gate_action_guard(role_mode: str | None) -> str:
    if role_mode == "lo":
        return (
            "Do not perform ordinary task work, map session focus, or run broad exploration before relaying "
            "the disclosure. The harness-only Loyal Opposition startup action described below is the permitted "
            "continuation after the disclosure relay."
        )
    return (
        "Do not perform ordinary task work, mutate files, map session focus, or run broad exploration on this "
        "disclosure-relay turn."
    )


def _startup_gate_followup_instruction(role_mode: str | None, init_mode: str | None) -> str:
    if role_mode == "lo" and init_mode == "advisory":
        return (
            "After relaying the cached disclosure, continue only with the harness-only Loyal Opposition "
            "advisory startup action: read current TAFE/dispatcher bridge state and status-bearing versioned "
            "files under `bridge/`, report the live scan result, and ask Mike whether to switch to "
            "auto-process. Do not write verdict files or auto-process bridge entries in advisory mode."
        )
    if role_mode == "lo":
        return (
            "After relaying the cached disclosure, continue with the harness-only Loyal Opposition startup "
            "action: read current TAFE/dispatcher bridge state and status-bearing versioned files under "
            "`bridge/`, report the live scan result, and process actionable latest `NEW` / `REVISED` bridge "
            "entries oldest-to-newest by default. Do not stop after disclosure relay when the bridge startup "
            "action is still pending."
        )
    return (
        "After relaying the cached disclosure, stop and wait for the next owner message. Prime Builder startup "
        "must not choose, map, or begin session work until Mike supplies focus or an unambiguous concrete task."
    )


def _startup_gate_message(role_mode: str | None = None, *, init_mode: str | None = None) -> str:
    return (
        "GTKB STARTUP INPUT GATE (init-keyword match): the prompt matched the "
        "GroundTruth-KB init keyword, so the startup-disclosure relay path is active. "
        f"{_startup_gate_action_guard(role_mode)} "
        "The owner-visible startup disclosure is NOT inlined in this payload; it is held in a harness-scoped "
        "cache file so this payload stays bounded. If the startup disclosure is not already fully present in "
        "model context, perform exactly one read-only filesystem read of the cache file named below, then relay "
        "its content verbatim as the owner-visible startup disclosure. "
        f"{_startup_gate_followup_instruction(role_mode, init_mode)} "
        "Do not replace the disclosure with a short acknowledgement."
    )


def _startup_relay_failure_context(reason: str) -> str:
    return (
        "GTKB STARTUP RELAY FAILURE (init-keyword match): the startup-disclosure "
        f"relay path is active but its harness-scoped cache is unusable -- {reason}. "
        "Do NOT treat startup as satisfied, do NOT mark the startup response "
        "complete, and do NOT claim the disclosure was presented. Report this "
        "startup-relay failure to the owner with this diagnostic and ask how to "
        "proceed. Do not perform ordinary task work on this turn."
    )


def _startup_gate_response(
    project_root: Path | None = None,
    *,
    role_mode: str | None = None,
    init_mode: str | None = None,
) -> dict[str, Any]:
    pointer = _startup_relay_pointer(project_root, role_mode=role_mode)
    if pointer is None and role_mode is not None:
        pointer = _startup_relay_pointer(project_root, role_mode=None)
    if pointer is None:
        diagnostic = _startup_relay_failure_context(
            "the cache file or its metadata sidecar is missing, empty, or malformed"
        )
        return {
            "systemMessage": diagnostic,
            "hookSpecificOutput": {
                "hookEventName": "UserPromptSubmit",
                "additionalContext": diagnostic,
            },
        }
    message = _startup_gate_message(role_mode or pointer.get("role_mode"), init_mode=init_mode)
    if not pointer["consistent"]:
        diagnostic = _startup_relay_failure_context(
            f"cache file {pointer['cache_path']} does not match its metadata sidecar "
            "(sha256, byte-length, harness id, role, freshness, or startup-disclosure shape mismatch); "
            "it may be stale, wrong-role, or displaced by a non-disclosure payload"
        )
        return {
            "systemMessage": diagnostic,
            "hookSpecificOutput": {
                "hookEventName": "UserPromptSubmit",
                "additionalContext": diagnostic,
            },
        }
    pointer_block = (
        "\n\n## Startup Disclosure Relay Source\n\n"
        f"- cache file: {pointer['cache_path']}\n"
        f"- byte length: {pointer['byte_length']}\n"
        f"- sha256: {pointer['sha256']}\n\n"
        "Read that cache file once (a single read-only filesystem read), then "
        "relay its full content verbatim as the owner-visible startup disclosure."
    )
    return {
        "systemMessage": message,
        "hookSpecificOutput": {
            "hookEventName": "UserPromptSubmit",
            "additionalContext": f"{message}{pointer_block}",
        },
    }


def _consume_discard_first_prompt_gate(
    prompt: str,
    project_root: Path | None = None,
    *,
    session_id: str | None = None,
) -> dict[str, Any] | None:
    state = _read_lifecycle_guard(project_root)
    if state.get("discard_next_user_prompt") is not True:
        return None

    trimmed_prompt = " ".join(prompt.strip().split())
    init_match = _match_startup_init_keyword(prompt)
    if state.get("first_wrapup_suppressed") is True and state.get("startup_response_pending") is not True:
        state.update(
            {
                "discard_next_user_prompt": False,
                "stale_startup_gate_cleared": True,
                "stale_startup_gate_cleared_at": _now_iso(),
                "stale_startup_gate_reason": "startup_stop_already_suppressed",
                "startup_prompt_preview": trimmed_prompt[:160],
            }
        )
        _write_lifecycle_guard(state, project_root)
        return None

    if init_match is None:
        state.update(
            {
                "discard_next_user_prompt": False,
                "startup_prompt_discarded": False,
                "startup_response_pending": False,
                "startup_gate_no_match_passed_through": True,
                "startup_gate_no_match_at": _now_iso(),
                "startup_prompt_preview": trimmed_prompt[:160],
            }
        )
        _write_lifecycle_guard(state, project_root)
        return None

    current_subject = _set_work_subject_from_init_match(init_match, project_root)
    state.update(
        {
            "discard_next_user_prompt": False,
            "startup_prompt_discarded": True,
            "startup_prompt_discarded_at": _now_iso(),
            "startup_prompt_preview": trimmed_prompt[:160],
            "startup_response_pending": True,
            "startup_init_app_scope": init_match.app_scope,
            "startup_init_mode": init_match.mode,
        }
    )
    if current_subject is not None:
        state["current_subject"] = current_subject
    # Slice 2: write the ephemeral session-state role marker on the interactive
    # init-keyword path. Per DCL-SESSION-ROLE-RESOLUTION-001:
    #   - assertion 2: marker is written on the keyword code path;
    #   - assertion 6: persisted marker MUST carry a non-null session id (the
    #     fail-soft branch writes NO marker when no id can be resolved);
    #   - assertion 7: marker role is in {prime-builder, loyal-opposition}.
    # The headless dispatch path (GTKB_BRIDGE_POLLER_RUN_ID present) is excluded
    # so only interactive owner-typed declarations produce a marker, per
    # DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001's INTERACTIVE_OVERRIDE_AUTHORIZED
    # receiver decision.
    explicit_role_mode = _startup_role_mode_from_prompt(prompt)
    role_mode = _startup_effective_role_mode(prompt, project_root)
    role_profile = _MODE_TO_ROLE_PROFILE.get(explicit_role_mode or "")
    headless_dispatch = bool(os.environ.get(_BRIDGE_DISPATCH_RUN_ID_ENV))
    if role_profile and not headless_dispatch:
        resolved_id, source_label = _resolve_session_id(session_id)
        if resolved_id is None:
            state["startup_session_role_marker_failsoft_at"] = _now_iso()
            state["startup_session_role_marker_failsoft_reason"] = "session_id_unresolved"
        else:
            wrote = _write_session_role_marker(
                role_profile,
                resolved_id,
                source_label or "",
                project_root,
            )
            if wrote:
                state["startup_session_role_marker_written_at"] = _now_iso()
                state["startup_session_role_marker_role"] = role_profile
                state["startup_session_role_marker_session_id_source"] = source_label
            else:
                state["startup_session_role_marker_failsoft_at"] = _now_iso()
                state["startup_session_role_marker_failsoft_reason"] = "marker_write_oserror"
            # WI-4540: additively write the per-session marker(s) (R-B1
            # multi-key) — the new authority for the guard/resolver, written
            # independently of the legacy single-file clobber result.
            per_session_written = _write_per_session_role_markers(
                role_profile,
                _candidate_marker_session_ids(session_id),
                project_root,
            )
            if per_session_written:
                state["startup_session_role_per_session_markers_written"] = per_session_written
    if role_mode:
        state["startup_init_role_mode"] = role_mode
    _write_lifecycle_guard(state, project_root)
    return _startup_gate_response(project_root, role_mode=role_mode, init_mode=init_match.mode)


def _clear_startup_response_pending_for_followup(project_root: Path | None = None) -> None:
    state = _read_lifecycle_guard(project_root)
    if state.get("startup_response_pending") is not True:
        return
    state.update(
        {
            "startup_response_pending": False,
            "startup_input_gate_cleared_at": _now_iso(),
        }
    )
    _write_lifecycle_guard(state, project_root)


def _startup_response_pending(project_root: Path | None = None) -> bool:
    state = _read_lifecycle_guard(project_root)
    if state.get("startup_response_pending") is not True:
        return False
    started_at = _parse_iso8601(state.get("startup_prompt_discarded_at") or state.get("armed_at"))
    if started_at is None:
        return True
    age_seconds = (datetime.now(UTC) - started_at).total_seconds()
    if age_seconds <= STARTUP_RESPONSE_PENDING_EXPIRY_SECONDS:
        return True
    state.update(
        {
            "startup_response_pending": False,
            "stale_startup_response_pending_cleared": True,
            "stale_startup_response_pending_cleared_at": _now_iso(),
        }
    )
    _write_lifecycle_guard(state, project_root)
    return False


def _normalize_relative_path(path_text: str, project_root: Path | None = None) -> str:
    raw = Path(path_text.replace("\\", "/"))
    root = (project_root or _project_root_from_env()).resolve()
    try:
        path = raw if raw.is_absolute() else root / raw
        relative = path.resolve().relative_to(root)
        return relative.as_posix()
    except (OSError, ValueError):
        return path_text.replace("\\", "/").lstrip("./")


def _absolute_candidate(path_text: str, project_root: Path | None = None) -> Path | None:
    root = (project_root or _project_root_from_env()).resolve()
    raw = Path(path_text.replace("\\", "/"))
    try:
        absolute = raw if raw.is_absolute() else root / raw
        return absolute.resolve(strict=False)
    except (OSError, ValueError):
        return None


def classify_root(path_text: str, project_root: Path | None = None) -> str:
    """Classify a candidate write target under the Phase 7 4-category taxonomy.

    Returns one of ``application_product``, ``current_repo_bridge_or_governance``,
    ``gtkb_product``, or ``neutral``.
    """

    gtkb_root = gtkb_product_root()
    absolute = _absolute_candidate(path_text, project_root)
    if gtkb_root is not None and absolute is not None:
        try:
            absolute.relative_to(gtkb_root)
            return ROOT_GTKB_PRODUCT
        except ValueError:
            pass

    relative = _normalize_relative_path(path_text, project_root)
    if relative in CURRENT_REPO_BRIDGE_OR_GOVERNANCE_FILES:
        return ROOT_CURRENT_REPO_BRIDGE_OR_GOVERNANCE
    for prefix in CURRENT_REPO_BRIDGE_OR_GOVERNANCE_PREFIXES:
        if relative == prefix.rstrip("/") or relative.startswith(prefix):
            return ROOT_CURRENT_REPO_BRIDGE_OR_GOVERNANCE
    for prefix in APPLICATION_PREFIXES:
        if relative == prefix.rstrip("/") or relative.startswith(prefix):
            return ROOT_APPLICATION_PRODUCT
    return ROOT_NEUTRAL


def classify_path(path_text: str, project_root: Path | None = None) -> str:
    """Legacy 3-value classifier kept for callers that rely on ``FOCUS_*`` strings.

    Maps the new 4-category classifier back to the pre-Phase-7 vocabulary:
    ``gtkb_product`` or ``current_repo_bridge_or_governance`` → ``FOCUS_GTKB_INFRASTRUCTURE``;
    ``application_product`` → ``FOCUS_APPLICATION``; ``neutral`` → ``"neutral"``.
    """

    category = classify_root(path_text, project_root)
    if category == ROOT_APPLICATION_PRODUCT:
        return FOCUS_APPLICATION
    if category in (ROOT_GTKB_PRODUCT, ROOT_CURRENT_REPO_BRIDGE_OR_GOVERNANCE):
        return FOCUS_GTKB_INFRASTRUCTURE
    return "neutral"


def _path_mentions_from_command(command: str) -> list[str]:
    """Extract path-like mentions from a mutating shell command.

    Finds both known-prefix substring matches (``bridge/``, ``src/``, …) and
    whitespace-separated tokens that look like filesystem paths (contain a
    slash or carry a drive-letter prefix). Token scanning is how absolute
    paths under ``GTKB_PRODUCT_ROOT`` (outside the current-repo prefix table)
    get surfaced for classification.
    """

    mentions: list[str] = []
    known_paths = sorted(
        set(CURRENT_REPO_BRIDGE_OR_GOVERNANCE_FILES)
        | set(CURRENT_REPO_BRIDGE_OR_GOVERNANCE_PREFIXES)
        | set(APPLICATION_PREFIXES),
        key=len,
        reverse=True,
    )
    normalized_command = command.replace("\\", "/")
    for path in known_paths:
        if path.rstrip("/") in normalized_command:
            mentions.append(path)
    for raw_token in re.split(r"\s+", normalized_command):
        token = raw_token.strip(" '\"`;,")
        if not token:
            continue
        if "/" in token or re.match(r"^[A-Za-z]:/", token):
            mentions.append(token)
    return mentions


def _command_looks_mutating(command: str) -> bool:
    return any(pattern.search(command) for pattern in MUTATING_COMMAND_PATTERNS)


def paths_from_tool_input(tool_name: str, tool_input: dict[str, Any]) -> list[str]:
    paths: list[str] = []
    for key in ("file_path", "path", "notebook_path"):
        value = tool_input.get(key)
        if isinstance(value, str) and value.strip():
            paths.append(value)

    if tool_name in SHELL_TOOL_NAMES:
        command = str(tool_input.get("command") or "")
        if _command_looks_mutating(command):
            paths.extend(_path_mentions_from_command(command))
    return paths


def _first_non_blank_line(text: str) -> str:
    for line in text.splitlines():
        stripped = line.strip()
        if stripped:
            return stripped
    return ""


def _application_allows_current_repo_write(
    *,
    path_text: str,
    tool_name: str,
    tool_input: dict[str, Any],
    project_root: Path | None = None,
) -> bool:
    relative = _normalize_relative_path(path_text, project_root)
    if not VERSIONED_BRIDGE_PATH_RE.match(relative):
        return False
    if tool_name != "Write":
        return False
    content = tool_input.get("content")
    if not isinstance(content, str):
        return False
    return _first_non_blank_line(content) == "ADVISORY" and ADVISORY_BRIDGE_KIND_RE.search(content) is not None


def guard_tool_use(
    payload: dict[str, Any],
    project_root: Path | None = None,
) -> dict[str, Any]:
    """Phase 7 root-aware guard.

    Blocks cross-subject writes:

    * ``application`` subject blocks ``gtkb_product`` targets.
    * ``application`` subject blocks current-repo bridge/governance targets
      except full-content writes of numbered bridge ``ADVISORY`` entries.
    * ``gtkb_infrastructure`` subject blocks ``application_product`` targets.
    """

    if _startup_response_pending(project_root) and not _is_startup_relay_cache_read(payload, project_root):
        return {
            "decision": "block",
            "reason": (
                "BLOCKED (GTKB-STARTUP-INPUT-GATE): startup disclosure has been emitted; awaiting owner's next message before tool use. "
                "The init-keyword contract relays the disclosure on match (init gtkb / init gtkb advisory / etc.) and passes through on no-match "
                "(per DCL-INIT-KEYWORD-STARTUP-DISCLOSURE-RELAY-001)."
            ),
        }

    tool_name = str(payload.get("tool_name") or "")
    tool_input = payload.get("tool_input") or {}
    if not isinstance(tool_input, dict):
        return {}

    state = load_state(project_root)
    active_subject = str(state["current_subject"])
    for path_text in paths_from_tool_input(tool_name, tool_input):
        root_class = classify_root(path_text, project_root)
        if active_subject == FOCUS_APPLICATION and root_class == ROOT_GTKB_PRODUCT:
            return {
                "decision": "block",
                "reason": (
                    "BLOCKED (GTKB-WORK-SUBJECT): Current work subject is application. "
                    f"This change targets GT-KB product artifacts (`{path_text}`). "
                    "Switch with standalone `work subject GT-KB` before proceeding."
                ),
            }
        if active_subject == FOCUS_APPLICATION and root_class == ROOT_CURRENT_REPO_BRIDGE_OR_GOVERNANCE:
            if _application_allows_current_repo_write(
                path_text=path_text,
                tool_name=tool_name,
                tool_input=tool_input,
                project_root=project_root,
            ):
                continue
            return {
                "decision": "block",
                "reason": (
                    "BLOCKED (GTKB-WORK-SUBJECT): Current work subject is application. "
                    f"This change targets GT-KB bridge/governance artifacts (`{path_text}`). "
                    "Application work may only write GT-KB-directed output as a numbered bridge ADVISORY entry; "
                    "switch with standalone `work subject GT-KB` before ordinary GT-KB artifact changes."
                ),
            }
        if active_subject == FOCUS_GTKB_INFRASTRUCTURE and root_class == ROOT_APPLICATION_PRODUCT:
            return {
                "decision": "block",
                "reason": (
                    "BLOCKED (GTKB-WORK-SUBJECT): Current work subject is GT-KB. "
                    f"This change targets application product artifacts (`{path_text}`). "
                    "Switch with standalone `work subject application` before proceeding."
                ),
            }
    return {}


def handle_user_prompt(
    prompt: str,
    project_root: Path | None = None,
    *,
    session_id: str | None = None,
) -> dict[str, Any]:
    startup_gate_response = _consume_discard_first_prompt_gate(prompt, project_root, session_id=session_id)
    if startup_gate_response is not None:
        return startup_gate_response

    state = _read_lifecycle_guard(project_root)
    if _record_explicit_role_hint_from_prompt(prompt, state, project_root, session_id=session_id):
        _write_lifecycle_guard(state, project_root)

    _clear_startup_response_pending_for_followup(project_root)

    role_response = handle_role_command(prompt, project_root)
    if role_response is not None:
        return role_response

    dashboard_response = handle_dashboard_command(prompt)
    if dashboard_response is not None:
        return dashboard_response

    requested_focus = focus_from_prompt(prompt)
    if requested_focus:
        state = save_state(requested_focus, project_root)
        return {"systemMessage": system_message_for_state(state, changed=True)}
    return {"systemMessage": system_message_for_state(load_state(project_root))}


def handle_hook_payload(payload: dict[str, Any], project_root: Path | None = None) -> dict[str, Any]:
    prompt = payload.get("user_prompt")
    if not isinstance(prompt, str):
        prompt = payload.get("prompt")
    if isinstance(prompt, str):
        # Slice 2: thread the Claude Code UserPromptSubmit ``session_id`` field
        # (if present) into the prompt-handling path so the init-keyword marker
        # write can satisfy DCL-SESSION-ROLE-RESOLUTION-001 assertion 6
        # (non-null session id) without falling through to the env fallback
        # chain when the canonical payload field is available.
        payload_session_id = payload.get("session_id")
        return handle_user_prompt(
            prompt,
            project_root,
            session_id=payload_session_id if isinstance(payload_session_id, str) else None,
        )
    return guard_tool_use(payload, project_root)
