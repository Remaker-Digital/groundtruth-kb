#!/usr/bin/env python3
"""Work-subject state, commands, and root-classification guardrails for Agent Red / GT-KB sessions.

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

# ---- Work-subject identity ----------------------------------------------
FOCUS_APPLICATION = "application"
FOCUS_GTKB_INFRASTRUCTURE = "gtkb_infrastructure"
DEFAULT_FOCUS = FOCUS_APPLICATION

SUBJECT_APPLICATION = FOCUS_APPLICATION
SUBJECT_GTKB = FOCUS_GTKB_INFRASTRUCTURE
DEFAULT_SUBJECT = SUBJECT_APPLICATION

SCHEMA_VERSION = 1
ROLE_SLOT_DEFAULT = "shared"
DEFAULT_APPLICATION_LABEL = "Agent Red"

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

OPERATING_ROLE_RELATIVE_PATH = Path(".claude") / "rules" / "operating-role.md"
LIFECYCLE_GUARD_RELATIVE_PATH = Path(".claude") / "hooks" / ".session-lifecycle-guard.json"
STARTUP_REPORT_RELATIVE_PATH = Path("docs") / "gtkb-dashboard" / "session-startup-report.md"
DEFAULT_DASHBOARD_PREFERENCES_PATH = (
    Path.home() / ".codex" / "agent-red-hooks" / "session-startup-preferences.json"
)
HARNESS_ROLE_RECORDS = {
    "codex": Path.home() / ".codex" / "agent-red-hooks" / "operating-role.md",
    "claude": Path.home() / ".claude" / "agent-red-hooks" / "operating-role.md",
}
HARNESS_LIFECYCLE_GUARDS = {
    "codex": Path.home() / ".codex" / "agent-red-hooks" / "session-lifecycle-guard.json",
    "claude": Path.home() / ".claude" / "agent-red-hooks" / "session-lifecycle-guard.json",
}

# ---- Role profiles (unchanged from prior module) -----------------------
ROLE_PRIME_BUILDER = "prime-builder"
ROLE_LOYAL_OPPOSITION = "loyal-opposition"
ROLE_ACTING_PRIME_BUILDER = "acting-prime-builder"
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


def _project_root_from_env() -> Path:
    return Path(os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()).resolve()


def _normalize_harness_name(value: str | None) -> str | None:
    normalized = str(value or "").strip().lower().replace("_", "-")
    if normalized in HARNESS_ROLE_RECORDS:
        return normalized
    return None


def _resolved_harness_name() -> str | None:
    return _normalize_harness_name(os.environ.get("GTKB_HARNESS_NAME"))


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
    override = os.environ.get("GTKB_OPERATING_ROLE_PATH")
    if override:
        return Path(override).expanduser().resolve()
    harness_name = _resolved_harness_name()
    if harness_name:
        return HARNESS_ROLE_RECORDS[harness_name].expanduser().resolve()
    root = (project_root or _project_root_from_env()).resolve()
    return root / OPERATING_ROLE_RELATIVE_PATH


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
    2. Sibling ``../groundtruth-kb`` checkout when it contains ``src/groundtruth_kb``.
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
    candidate = project.parent / "groundtruth-kb"
    try:
        if candidate.is_dir() and (candidate / "src" / "groundtruth_kb").is_dir():
            return candidate.resolve()
    except OSError:
        return None
    return None


def _read_lifecycle_guard(project_root: Path | None = None) -> dict[str, Any]:
    path = lifecycle_guard_path(project_root)
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
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
) -> dict[str, Any]:
    """Persist the canonical work-subject state under ``.claude/session/work-subject.json``."""

    if focus not in FOCUS_LABELS:
        raise ValueError(f"Unknown work subject: {focus}")

    state = _canonical_default(project_root)
    state.update(
        {
            "current_subject": focus,
            "updated_at": _now_iso(),
            "updated_by": updated_by,
            "source": source or _infer_source(updated_by),
        }
    )
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
    path = operating_role_path(project_root)
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        fallback_path = ((project_root or _project_root_from_env()).resolve()) / OPERATING_ROLE_RELATIVE_PATH
        if path != fallback_path:
            try:
                text = fallback_path.read_text(encoding="utf-8")
            except OSError:
                return ROLE_PRIME_BUILDER
        else:
            return ROLE_PRIME_BUILDER
    match = re.search(r"(?im)^\s*active_role\s*:\s*`?([a-z][a-z0-9-]*)`?\s*$", text)
    if not match:
        return ROLE_PRIME_BUILDER
    role = match.group(1).lower()
    return role if role in TOGGLEABLE_ROLE_PROFILES else ROLE_PRIME_BUILDER


def _next_toggled_role(current_role: str) -> str:
    return ROLE_PRIME_BUILDER if current_role == ROLE_LOYAL_OPPOSITION else ROLE_LOYAL_OPPOSITION


def set_next_session_role(role: str, project_root: Path | None = None) -> str:
    if role not in {ROLE_PRIME_BUILDER, ROLE_LOYAL_OPPOSITION}:
        raise ValueError(f"Unsupported next-session role: {role}")

    path = operating_role_path(project_root)
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        fallback_path = ((project_root or _project_root_from_env()).resolve()) / OPERATING_ROLE_RELATIVE_PATH
        try:
            text = fallback_path.read_text(encoding="utf-8")
        except OSError:
            text = "# Durable Operating Role Assignment\n\nactive_role: prime-builder\n"

    if re.search(r"(?im)^\s*active_role\s*:", text):
        text = re.sub(r"(?im)^(\s*active_role\s*:\s*)`?[a-z][a-z0-9-]*`?(\s*)$", rf"\1{role}\2", text)
    else:
        text = text.rstrip() + f"\n\nactive_role: {role}\n"

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
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
            f"This updates `{role_path_display}`; the current session role is unchanged."
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


def render_startup_focus_lines(snapshot: dict[str, str | None] | None = None) -> str:
    """Render the Active Work Subject block with Phase-7 ``work subject`` language."""

    snapshot = snapshot or startup_focus_snapshot()
    app_label = snapshot["application_label"] or DEFAULT_APPLICATION_LABEL
    role_slot = snapshot.get("role_slot") or ROLE_SLOT_DEFAULT
    topology_mode = snapshot.get("topology_mode") or TOPOLOGY_MODE_DEFAULT
    return "\n".join(
        [
            f"- Default work subject: {snapshot['default_label']}",
            f"- Current work subject: {snapshot['current_label']}",
            f"- Application label: {app_label}",
            f"- Bridge role slot: `{role_slot}` (shared, prime-builder, or loyal-opposition).",
            f"- Harness topology: `{topology_mode}` (single_harness or multi_harness).",
            "- Application work subject means owner direction is interpreted as work on the unique application being built with GroundTruth-KB.",
            "- GT-KB Infrastructure work subject is active only when explicitly declared.",
            "- Application work subject commands: `work subject application`, `application mode`, `app mode`, `agent red mode`.",
            "- GT-KB work subject commands: `work subject GT-KB`, `GT-KB mode`, `GT-KB infrastructure mode`, `GroundTruth-KB mode`.",
            "- Canonical state file: `.claude/session/work-subject.json` (legacy `.claude/hooks/.workstream-focus-state.json` migrated on next owner command).",
            "- First owner message in a fresh session is a session-start stimulus only; do not map it to a task, focus, approval, or answer.",
            "- Live bridge authority: `bridge/INDEX.md` is the canonical handoff/review record; poller status, scan-freshness files, and startup snapshots are non-canonical.",
        ]
    )


def render_active_work_subject(
    project_root: Path | None = None,
    *,
    snapshot: dict[str, str | None] | None = None,
    overlay_status: dict[str, Any] | None = None,
    include_counterpart: bool = True,
) -> str:
    """Render the enriched Active Work Subject block (Slice 1 §A).

    Composes ``render_startup_focus_lines`` with an overlay status line (§C)
    and, when ``include_counterpart`` is True, a counterpart-state warning
    summary (§E). Overlay and counterpart outputs are always informational —
    the startup report never treats them as canonical.
    """

    lines = [render_startup_focus_lines(snapshot or startup_focus_snapshot(project_root))]
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
            "WARNING: session overlay work subject differs from the active subject; "
            "overlay is informational only."
        )
    if status.get("projection_diff"):
        warnings.append(
            "WARNING: session overlay projection differs from live state; rely on live "
            "files for readiness and bridge decisions."
        )
    if warnings:
        warnings.append(
            "Session overlays are never canonical for Deliberation Archive, MemBase, "
            "bridge, or readiness decisions."
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


def _read_active_role_from_file(path: Path) -> str | None:
    try:
        text = path.read_text(encoding="utf-8")
    except (FileNotFoundError, OSError):
        return None
    match = re.search(r"^active_role:\s*([a-z0-9_\-]+)\s*$", text, re.MULTILINE | re.IGNORECASE)
    if not match:
        return None
    value = match.group(1).strip().lower()
    return value or None


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


def detect_counterpart_state(project_root: Path | None = None) -> dict[str, Any]:
    """Detect role-slot and subject conflicts with the counterpart harness (§E).

    Returns ``{"counterpart_present", "same_role_slot", "subject_mismatch",
    "warnings"}``. Warnings are only emitted when counterpart state files are
    present; missing files yield no warnings and no crash.
    """

    current_harness = _resolved_harness_name()
    per_harness_roles: dict[str, str] = {}
    for harness, record_path in HARNESS_ROLE_RECORDS.items():
        role = _read_active_role_from_file(record_path)
        if role:
            per_harness_roles[harness] = role

    counterpart_present = any(
        harness != current_harness and harness in per_harness_roles
        for harness in HARNESS_ROLE_RECORDS
    )

    warnings: list[str] = []
    same_role_slot = False
    if current_harness and current_harness in per_harness_roles:
        our_role = per_harness_roles[current_harness]
        for harness, role in per_harness_roles.items():
            if harness == current_harness:
                continue
            if role == our_role and role in TOGGLEABLE_ROLE_PROFILES:
                same_role_slot = True
                warnings.append(
                    f"both `{current_harness}` and `{harness}` have active_role=`{role}` "
                    "— counterpart bridge roles may collide; verify operating-role.md per harness."
                )
            elif role != our_role and role in TOGGLEABLE_ROLE_PROFILES and our_role in TOGGLEABLE_ROLE_PROFILES:
                warnings.append(
                    f"`{current_harness}` is `{our_role}`; counterpart `{harness}` is `{role}`. "
                    "Treat bridge message authority per operating-role.md."
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
    our_guard_path = HARNESS_LIFECYCLE_GUARDS.get(current_harness) if current_harness else None
    if our_guard_path is not None:
        our_subject = _read_counterpart_subject(our_guard_path)
    if our_subject is None:
        try:
            our_subject = str(load_state(project_root).get("current_subject") or "") or None
        except Exception:
            our_subject = None
    for harness, guard_path in HARNESS_LIFECYCLE_GUARDS.items():
        if harness == current_harness:
            continue
        counterpart_subject = _read_counterpart_subject(guard_path)
        if (
            counterpart_subject is not None
            and our_subject is not None
            and counterpart_subject != our_subject
        ):
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


def _startup_gate_message() -> str:
    report_path = STARTUP_REPORT_RELATIVE_PATH.as_posix()
    return (
        "GTKB STARTUP INPUT GATE: The first owner message of a fresh session is never actionable. "
        "Discard the current prompt completely; do not interpret it as a task, resume request, focus choice, "
        "approval, answer, or command, even if it says `resume`, `continue`, or names a focus option. "
        "Your next response must be the role-appropriate startup disclosure already generated for this session. "
        f"If the SessionStart payload is unavailable, read `{report_path}` from the project root and relay that startup disclosure. "
        "After presenting the startup disclosure, stop and wait for Mike's next message. "
        "Do not use tools, change files, or map session focus on this discarded-input turn."
    )


def _startup_gate_response() -> dict[str, Any]:
    message = _startup_gate_message()
    return {
        "systemMessage": message,
        "hookSpecificOutput": {
            "hookEventName": "UserPromptSubmit",
            "additionalContext": message,
        },
    }


def _consume_discard_first_prompt_gate(prompt: str, project_root: Path | None = None) -> dict[str, Any] | None:
    state = _read_lifecycle_guard(project_root)
    if state.get("discard_next_user_prompt") is not True:
        return None

    trimmed_prompt = " ".join(prompt.strip().split())
    state.update(
        {
            "discard_next_user_prompt": False,
            "startup_prompt_discarded": True,
            "startup_prompt_discarded_at": _now_iso(),
            "startup_prompt_preview": trimmed_prompt[:160],
            "startup_response_pending": True,
        }
    )
    _write_lifecycle_guard(state, project_root)
    return _startup_gate_response()


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
    return state.get("startup_response_pending") is True


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
                "BLOCKED (GTKB-STARTUP-INPUT-GATE): the first owner message of this fresh session was discarded "
                "as startup stimulus. Do not use tools on this turn. Present the startup disclosure and wait for "
                "Mike's next message."
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
    if isinstance(prompt, str):
        return handle_user_prompt(prompt, project_root)
    return guard_tool_use(payload, project_root)
