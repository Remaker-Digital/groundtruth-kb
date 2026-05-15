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

import json
import os
import re
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

# Current-repo bridge/governance surfaces (allowed under BOTH work subjects).
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
        role_map_path = root / "harness-state" / "role-assignments.json"
        if role_map_path.exists():
            role_map = json.loads(role_map_path.read_text(encoding="utf-8"))
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
        f"- Bridge role slot: `{role_slot}` (shared, prime-builder, or loyal-opposition).",
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
                "- Live bridge authority: `bridge/INDEX.md` is the canonical handoff/review record; poller status, scan-freshness files, and startup snapshots are non-canonical.",
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
    return state_root / "role-assignments.json", lifecycle_guards


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
                    "— counterpart bridge roles may collide; verify harness-state/role-assignments.json."
                )
            elif role_set & TOGGLEABLE_ROLE_PROFILES and our_role_set & TOGGLEABLE_ROLE_PROFILES and not overlap:
                warnings.append(
                    f"`{current_harness}` is `{our_label}`; counterpart `{harness}` is `{their_label}`. "
                    "Treat bridge message authority per harness-state/role-assignments.json."
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


_CANONICAL_DISPATCH_INIT_RE = re.compile(r"^::init\s+gtkb\s+(?:pb|lo)\s*$", re.IGNORECASE)


def _match_startup_init_keyword(prompt: str) -> InitKeywordMatch | None:
    match = match_init_keyword(prompt)
    if match is not None:
        return match
    if _CANONICAL_DISPATCH_INIT_RE.match(prompt.strip()):
        return InitKeywordMatch(app_scope="gtkb", mode="default")
    return None


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


def _extract_user_visible_startup(context: str) -> str:
    marker = "## User-Visible Startup Message"
    if marker in context:
        return context.split(marker, 1)[1].strip()
    return context.strip()


def _cached_startup_disclosure(project_root: Path | None = None) -> str | None:
    root = (project_root or _project_root_from_env()).resolve()
    candidates = [
        _startup_diagnostic_dir(root) / "last-session-start.json",
        root / "docs" / "gtkb-dashboard" / "session-startup-report.md",
    ]
    for path in candidates:
        try:
            text = path.read_text(encoding="utf-8-sig")
        except OSError:
            continue
        if path.suffix.lower() == ".json":
            try:
                payload = json.loads(text)
            except json.JSONDecodeError:
                continue
            hook_output = payload.get("hookSpecificOutput") if isinstance(payload, dict) else None
            context = hook_output.get("additionalContext") if isinstance(hook_output, dict) else None
            if isinstance(context, str) and context.strip():
                return _extract_user_visible_startup(context)
            continue
        if text.strip():
            return text.strip()
    return None


def _startup_gate_message() -> str:
    report_path = STARTUP_REPORT_RELATIVE_PATH.as_posix()
    return (
        "GTKB STARTUP INPUT GATE (init-keyword match): the prompt matched the init keyword "
        "(per ADR-SESSION-START-INIT-KEYWORD-CONTRACT-001 and DCL-SESSION-START-INIT-KEYWORD-MATCHING-001) "
        "so the startup disclosure relay path is active. "
        "Render the cached role-appropriate startup disclosure included in this additionalContext when present and wait for the next owner message. "
        f"If the SessionStart payload is unavailable, read `{report_path}` from the project root and relay that startup disclosure. "
        "After presenting the disclosure, stop and wait for Mike's next message. "
        "Do not use tools, change files, or map session focus on this disclosure-relay turn."
    )


def _startup_gate_response(project_root: Path | None = None) -> dict[str, Any]:
    message = _startup_gate_message()
    cached_disclosure = _cached_startup_disclosure(project_root)
    additional_context = message
    if cached_disclosure:
        additional_context = f"{message}\n\n## Cached User-Visible Startup Message\n\n{cached_disclosure}"
    return {
        "systemMessage": message,
        "hookSpecificOutput": {
            "hookEventName": "UserPromptSubmit",
            "additionalContext": additional_context,
        },
    }


def _consume_discard_first_prompt_gate(prompt: str, project_root: Path | None = None) -> dict[str, Any] | None:
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
    _write_lifecycle_guard(state, project_root)
    return _startup_gate_response(project_root)


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

    if tool_name == "Bash":
        command = str(tool_input.get("command") or "")
        if _command_looks_mutating(command):
            paths.extend(_path_mentions_from_command(command))
    return paths


def guard_tool_use(
    payload: dict[str, Any],
    project_root: Path | None = None,
) -> dict[str, Any]:
    """Phase 7 root-aware guard.

    Blocks only cross-product writes:

    * ``application`` subject blocks ``gtkb_product`` targets.
    * ``gtkb_infrastructure`` subject blocks ``application_product`` targets.

    Current-repo bridge/governance surfaces (``current_repo_bridge_or_governance``)
    are NOT blocked in either subject — they are workspace infrastructure, not
    GT-KB product paths.
    """

    if _startup_response_pending(project_root):
        return {
            "decision": "block",
            "reason": (
                "BLOCKED (GTKB-STARTUP-INPUT-GATE): startup disclosure has been emitted; awaiting owner's next message before tool use. "
                "The init-keyword contract relays the disclosure on match (init gtkb / init gtkb advisory / etc.) and passes through on no-match "
                "(per ADR-SESSION-START-INIT-KEYWORD-CONTRACT-001)."
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


def handle_user_prompt(prompt: str, project_root: Path | None = None) -> dict[str, Any]:
    startup_gate_response = _consume_discard_first_prompt_gate(prompt, project_root)
    if startup_gate_response is not None:
        return startup_gate_response

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
        return handle_user_prompt(prompt, project_root)
    return guard_tool_use(payload, project_root)
