#!/usr/bin/env python3
"""Generate the GroundTruth-KB fresh-session startup report and dashboard."""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import os
import re
import shutil
import sqlite3
import subprocess
import sys
import tomllib
import urllib.error
import urllib.request
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

# UTF-8 stdout/stderr reconfigure per bridge/gtkb-startup-evidence-restoration-002.md GO.
# Prevents UnicodeEncodeError when SessionStart hook emits non-ASCII via
# json.dumps(..., ensure_ascii=False) at the two _emit hook-context paths
# (~line 4900 and ~line 5103). Without this, Windows fresh-session hook
# execution fails on cp1252 default stdout when PYTHONIOENCODING is unset.
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass
if hasattr(sys.stderr, "reconfigure"):
    try:
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

# Ensure E:\GT-KB project root is on sys.path so `from scripts.<sibling>` imports
# resolve when this script is invoked as `python scripts/session_self_initialization.py`
# (where sys.path[0] is the scripts/ directory, not the project root).
# Per gtkb-claude-session-start-parity-001 GO Change 3 — repairs the
# `No module named 'scripts.check_harness_parity'` error that surfaced in the
# `Harness parity` field of every startup payload.
_PROJECT_ROOT_FOR_IMPORTS = Path(__file__).resolve().parent.parent
if str(_PROJECT_ROOT_FOR_IMPORTS) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT_FOR_IMPORTS))

try:
    from scripts.workstream_focus import (
        CANONICAL_STATE_RELATIVE_PATH as _WORK_SUBJECT_CANONICAL_PATH,
    )
    from scripts.workstream_focus import (
        FOCUS_APPLICATION,
        FOCUS_GTKB_INFRASTRUCTURE,
        SubjectScopeError,  # noqa: F401  # intentional re-export for module.SubjectScopeError test access
        assert_readiness_subject_scope,
        render_active_work_subject,
        startup_focus_snapshot,
    )
    from scripts.workstream_focus import (
        load_state as _workstream_load_state,
    )
except ModuleNotFoundError:  # pragma: no cover - direct script execution path
    from workstream_focus import (  # type: ignore[no-redef]
        CANONICAL_STATE_RELATIVE_PATH as _WORK_SUBJECT_CANONICAL_PATH,
    )
    from workstream_focus import (  # type: ignore[no-redef]
        FOCUS_APPLICATION,
        FOCUS_GTKB_INFRASTRUCTURE,
        SubjectScopeError,  # noqa: F401  # intentional re-export for module.SubjectScopeError test access
        assert_readiness_subject_scope,
        render_active_work_subject,
        startup_focus_snapshot,
    )
    from workstream_focus import (
        load_state as _workstream_load_state,
    )

try:
    from scripts.harness_roles import (
        DEFAULT_HARNESS_IDS,
        ROLE_ASSIGNMENTS_RELATIVE_PATH,
        load_role_assignments,
        role_assignments_path,
        role_for_harness,
    )
    from scripts.harness_roles import (
        normalize_harness_name as _normalize_harness_name_from_roles,
    )
    from scripts.harness_roles import (
        resolved_harness_id as _resolved_harness_id_from_roles,
    )
except ImportError:  # pragma: no cover - direct script execution path
    from harness_roles import (  # type: ignore[no-redef]
        DEFAULT_HARNESS_IDS,
        ROLE_ASSIGNMENTS_RELATIVE_PATH,
        load_role_assignments,
        role_assignments_path,
        role_for_harness,
    )
    from harness_roles import (  # type: ignore[no-redef]
        normalize_harness_name as _normalize_harness_name_from_roles,
    )
    from harness_roles import (  # type: ignore[no-redef]
        resolved_harness_id as _resolved_harness_id_from_roles,
    )

try:
    from scripts import gtkb_overlay as _gtkb_overlay
except ImportError:  # pragma: no cover - direct script execution path
    # Broader than ModuleNotFoundError: direct `python scripts/session_self_initialization.py`
    # can raise ImportError("cannot import name 'gtkb_overlay' from 'scripts'") even when
    # a 'scripts' namespace package is importable without this submodule bound. Catching
    # ImportError covers both the "package missing" and "name missing" cases.
    import gtkb_overlay as _gtkb_overlay  # type: ignore[no-redef]

try:
    from scripts.gtkb_scoped_client import (
        DASHBOARD_SUMMARY_READ,
        GtkbScopedClient,
        ScopedOperationError,
        ScopedServiceConfigError,
    )
except ImportError:  # pragma: no cover - direct script execution path
    from gtkb_scoped_client import (  # type: ignore[no-redef]
        DASHBOARD_SUMMARY_READ,
        GtkbScopedClient,
        ScopedOperationError,
        ScopedServiceConfigError,
    )

PROJECT_ROOT = Path(__file__).resolve().parent.parent
HARNESS_REGISTRY_RELATIVE_PATH = Path("harness-state") / "harness-registry.json"
# Harness-local role, lifecycle guard, and startup preference records belong to
# GT-KB itself. Agent Red is an adopter/demo and must not own active harness
# state unless Mike explicitly switches the session to Agent Red work.
GTKB_HARNESS_STATE_ROOT = PROJECT_ROOT / "harness-state"
# DEFAULT_DASHBOARD_DIR / DEFAULT_HISTORY_PATH removed per
# bridge/generator-hardening-001-003.md Â§4.6: argparse defaults to None;
# main() derives both from resolved --project-root post-parse.
# Codex GO -004 implementation constraint (i): PROJECT_ROOT only as CLI
# fallback for --project-root, never as internal output/read-path fallback.
DEFAULT_USER_STARTUP_PREFERENCES_PATH = GTKB_HARNESS_STATE_ROOT / "codex" / "session-startup-preferences.json"
GRAFANA_DASHBOARD_URL = "http://localhost:3000/d/gtkb/groundtruth-kb-dashboard"
GRAFANA_HEALTH_URL = "http://localhost:3000/api/health"
DASHBOARD_OPEN_MODE_HARNESS = "harness_browser"
DASHBOARD_OPEN_MODE_SYSTEM = "system_default_browser"
PDF_EXPORT_FILENAME = "groundtruth-kb-project-dashboard.pdf"
MAX_HISTORY = 200
DASHBOARD_SCOPE_VERSION = "gtkb_v1"
DASHBOARD_SCOPE_NOTE = "GroundTruth-KB project dashboard."
DEFAULT_RELEASE_BRANCH = "main"
STARTUP_SERVICE_CONTRACT_VERSION = "gtkb-startup-service-v2"
STARTUP_FRESHNESS_CONTRACT_VERSION = "gtkb-startup-freshness-v1"
STARTUP_PAYLOAD_PROFILE_CONTRACT_VERSION = "gtkb-startup-payload-profile-v1"
STARTUP_PAYLOAD_PROFILE_DIR = Path(".gtkb-state") / "startup-payload-profiles"
OPERATING_ROLE_RELATIVE_PATH = ROLE_ASSIGNMENTS_RELATIVE_PATH
HARNESS_LIFECYCLE_GUARDS = {
    "codex": GTKB_HARNESS_STATE_ROOT / "codex" / "session-lifecycle-guard.json",
    "claude": GTKB_HARNESS_STATE_ROOT / "claude" / "session-lifecycle-guard.json",
}
BRIDGE_DISPATCH_ROLE_TEXT = (
    "cross-harness event-driven trigger registered as PostToolUse and Stop hooks "
    "(.claude/settings.json, .codex/hooks.json); fires on tool-use and Stop "
    "rather than on a fixed interval; manual bridge/INDEX.md scans available "
    "as fallback; retired smart poller and OS poller remain archived"
)
BRIDGE_OPERATION_INSTRUCTIONS_TEXT = (
    "Bridge automation has two complementary axes. "
    "AXIS 1 (DISPATCHABLE WORK): the cross-harness event-driven trigger "
    "(`scripts/cross_harness_bridge_trigger.py`) is the canonical mechanism for "
    "self-contained work — reviews, verdicts, tests, work that a freshly-spawned "
    "counterpart harness can complete without further owner input. Registered as "
    "PostToolUse and Stop hooks. "
    "AXIS 2 (NON-DISPATCHABLE WORK): a thread automation pattern wakes the "
    "interactive chat session periodically to scan `bridge/INDEX.md` and surface "
    "work that requires interactive owner input mid-stream — owner-AUQ-required "
    "decisions, multi-turn review with accumulating context, cross-thread "
    "coordination, AUQ-heavy implementation. "
    "Both axes are required; their roles do not overlap. "
    "Use the `gtkb-bridge` skill (`.claude/skills/bridge/SKILL.md`; Codex adapter "
    "`.codex/skills/bridge/SKILL.md`) for proposal/review/verification mechanics. "
    "Manual `bridge/INDEX.md` scans remain available as fallback. "
    "Do NOT create new bridge automations (Codex-app-side, Claude-side, or otherwise) "
    "without owner approval; any new automation must be classified by axis "
    "(dispatchable vs non-dispatchable) and inventoried in "
    "`config/agent-control/system-interface-map.toml`."
)
ROLE_PROFILES: dict[str, dict[str, str]] = {
    "prime-builder": {
        "assumed_role": "Prime Builder",
        "role_assignment": "active AI harness assigned by owner through the single role assignment map",
        "bridge": "always available through bridge/INDEX.md and checked at session startup",
        "bridge_dispatch": BRIDGE_DISPATCH_ROLE_TEXT,
        "bridge_operation_instructions": BRIDGE_OPERATION_INSTRUCTIONS_TEXT,
        "role_mapping_source": "harness-state/harness-registry.json",
    },
    "acting-prime-builder": {
        "assumed_role": "Acting Prime Builder (compatibility/provenance)",
        "role_assignment": (
            "legacy/compatibility profile per bridge gtkb-role-session-lifecycle-simplification-003 "
            "Acting-Prime Compatibility Contract: this harness was previously assigned "
            "acting-prime-builder before the two-role canonical set (prime-builder, loyal-opposition) "
            "was finalized. Compatibility/provenance label, NOT a new role-switch target."
        ),
        "bridge": "always available through bridge/INDEX.md and checked at session startup",
        "bridge_dispatch": BRIDGE_DISPATCH_ROLE_TEXT,
        "bridge_operation_instructions": BRIDGE_OPERATION_INSTRUCTIONS_TEXT,
        "role_mapping_source": ".claude/rules/acting-prime-builder.md",
    },
    "loyal-opposition": {
        "assumed_role": "Loyal Opposition",
        "role_assignment": "active AI harness assigned by owner through the single role assignment map",
        "bridge": "always available through bridge/INDEX.md and checked at session startup",
        "bridge_dispatch": BRIDGE_DISPATCH_ROLE_TEXT,
        "bridge_operation_instructions": BRIDGE_OPERATION_INSTRUCTIONS_TEXT,
        "role_mapping_source": "harness-state/harness-registry.json",
    },
}
LIFECYCLE_GUARD_RELATIVE_PATH = Path(".claude") / "hooks" / ".session-lifecycle-guard.json"
DEV_ENV_INVENTORY_PUBLIC_JSON_RELATIVE_PATH = Path("docs") / "release" / "dev-environment-inventory.json"
DEV_ENV_INVENTORY_PUBLIC_MARKDOWN_RELATIVE_PATH = Path("docs") / "release" / "dev-environment-inventory.md"
DEV_ENV_INVENTORY_MAX_AGE_HOURS = 336
DEV_ENV_INVENTORY_REQUIRED_SECTIONS = (
    "project",
    "collector",
    "host",
    "shell",
    "toolchain",
    "harnesses",
    "repo_configured_surfaces",
    "runtime_provided_capabilities",
    "role_by_harness_compatibility",
    "redaction",
    "verification",
)


def _normalized_path(path: Path) -> Path:
    return path.expanduser().resolve()


def _normalize_harness_name(value: str | None) -> str | None:
    normalized = _normalize_harness_name_from_roles(value)
    if normalized in DEFAULT_HARNESS_IDS:
        return normalized
    return None


def _resolved_harness_name(explicit: str | None = None) -> str | None:
    return _normalize_harness_name(explicit) or _normalize_harness_name(os.environ.get("GTKB_HARNESS_NAME"))


def _resolved_harness_id(
    explicit: str | None = None,
    *,
    harness_name: str | None = None,
    project_root: Path | None = None,
) -> str | None:
    return _resolved_harness_id_from_roles(project_root, harness_id=explicit, harness_name=harness_name)


def _repo_operating_role_path(project_root: Path) -> Path:
    return role_assignments_path(project_root)


def harness_registry_path(project_root: Path) -> Path:
    return project_root.resolve() / HARNESS_REGISTRY_RELATIVE_PATH


def operating_role_path(
    project_root: Path,
    *,
    harness_name: str | None = None,
    harness_id: str | None = None,
    role_record_path: Path | None = None,
    prefer_local: bool = True,
) -> Path:
    if role_record_path is not None:
        return _normalized_path(role_record_path)
    if os.environ.get("GTKB_ROLE_ASSIGNMENTS_PATH"):
        return role_assignments_path(project_root)
    _ = harness_name, harness_id, prefer_local
    registry_path = harness_registry_path(project_root)
    if registry_path.is_file():
        return registry_path
    return role_assignments_path(project_root)


def _display_role_mapping_source(
    project_root: Path,
    *,
    harness_name: str | None = None,
    harness_id: str | None = None,
    role_record_path: Path | None = None,
) -> str:
    path = operating_role_path(
        project_root,
        harness_name=harness_name,
        harness_id=harness_id,
        role_record_path=role_record_path,
        prefer_local=False,
    )
    if role_record_path is not None or os.environ.get("GTKB_ROLE_ASSIGNMENTS_PATH"):
        return str(path)
    try:
        return path.relative_to(project_root).as_posix()
    except ValueError:
        return str(path)


def _role_metadata(
    role_profile: str,
    project_root: Path,
    *,
    harness_name: str | None = None,
    harness_id: str | None = None,
    role_record_path: Path | None = None,
) -> dict[str, str]:
    metadata = dict(ROLE_PROFILES[role_profile])
    resolved_name = _resolved_harness_name(harness_name)
    if resolved_name:
        metadata["harness_name"] = resolved_name
    mapping_source = _display_role_mapping_source(
        project_root,
        harness_name=harness_name,
        harness_id=harness_id,
        role_record_path=role_record_path,
    )
    metadata["role_mapping_source"] = mapping_source
    resolved_id = _resolved_harness_id(harness_id, harness_name=harness_name, project_root=project_root)
    if resolved_id:
        metadata["harness_id"] = resolved_id
        metadata["harness_identity_source"] = "harness-state/harness-identities.json"
        metadata["role_assignment"] = (
            f"active AI harness assigned by owner through single role map entry for harness `{resolved_id}`"
        )
    return metadata


def _truthy_preference(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "on", "enabled"}
    return False


def _user_startup_preferences_path() -> Path:
    override = os.environ.get("GTKB_STARTUP_PREFERENCES_PATH")
    return Path(override).expanduser() if override else DEFAULT_USER_STARTUP_PREFERENCES_PATH


def _read_user_startup_preferences(path: Path | None = None) -> dict[str, Any]:
    preference_path = path or _user_startup_preferences_path()
    try:
        if not preference_path.is_file():
            return {}
        data = json.loads(preference_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return data if isinstance(data, dict) else {}


def _should_open_dashboard_on_session_start(path: Path | None = None) -> bool:
    env_override = os.environ.get("GTKB_OPEN_DASHBOARD_ON_SESSION_START")
    if env_override is not None:
        return _truthy_preference(env_override)
    preferences = _read_user_startup_preferences(path)
    return _truthy_preference(preferences.get("open_dashboard_on_session_start"))


def _normalize_dashboard_open_mode(value: Any) -> str:
    if not isinstance(value, str):
        return DASHBOARD_OPEN_MODE_HARNESS
    normalized = value.strip().lower().replace("-", "_")
    if normalized in {"system", "system_browser", "system_default", "system_default_browser", "os", "os_default"}:
        return DASHBOARD_OPEN_MODE_SYSTEM
    return DASHBOARD_OPEN_MODE_HARNESS


def _dashboard_open_mode(path: Path | None = None) -> str:
    env_override = os.environ.get("GTKB_DASHBOARD_OPEN_MODE")
    if env_override:
        return _normalize_dashboard_open_mode(env_override)
    preferences = _read_user_startup_preferences(path)
    return _normalize_dashboard_open_mode(preferences.get("dashboard_open_mode"))


def _dashboard_opening_state(path: Path | None = None) -> dict[str, Any]:
    mode = _dashboard_open_mode(path)
    mechanism = (
        "operating system default browser"
        if mode == DASHBOARD_OPEN_MODE_SYSTEM
        else "harness-controlled browser connector"
    )
    return {
        "startup_open_requested": _should_open_dashboard_on_session_start(path),
        "mode": mode,
        "mechanism": mechanism,
        "system_browser_opt_in_required": True,
    }


def _probe_http_url(source: str, url: str, *, timeout: float = 3.0) -> dict[str, Any]:
    queried_at = _now_iso()
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "gtkb-startup-reachability-probe/1.0"},
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:  # noqa: S310 - local operator-configured URL.
            status_code = int(getattr(response, "status", response.getcode()))
    except (OSError, urllib.error.URLError, TimeoutError) as exc:
        return {
            "source": source,
            "kind": "live_probe",
            "required": False,
            "status": "unavailable",
            "queried_at": queried_at,
            "detail": url,
            "timeout_seconds": timeout,
            "error": str(exc),
        }
    return {
        "source": source,
        "kind": "live_probe",
        "required": False,
        "status": "queried" if status_code == 200 else "unavailable",
        "queried_at": queried_at,
        "detail": url,
        "timeout_seconds": timeout,
        "http_status": status_code,
    }


def _dashboard_reachability_probes() -> list[dict[str, Any]]:
    return [
        _probe_http_url("Grafana health endpoint", GRAFANA_HEALTH_URL),
        _probe_http_url("GT-KB dashboard URL", GRAFANA_DASHBOARD_URL),
    ]


def _open_dashboard_url_in_system_browser(url: str) -> bool:
    try:
        if sys.platform.startswith("win") and hasattr(os, "startfile"):
            os.startfile(url)  # type: ignore[attr-defined]
            return True
        opener = shutil.which("xdg-open") or shutil.which("open")
        if not opener:
            return False
        subprocess.Popen([opener, url], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except Exception:
        return False


def _maybe_open_dashboard_on_session_start(url: str) -> bool:
    if not _should_open_dashboard_on_session_start():
        return False
    if _dashboard_open_mode() == DASHBOARD_OPEN_MODE_SYSTEM:
        return _open_dashboard_url_in_system_browser(url)
    return True


NON_TERMINAL_WORK_ITEM_STATUSES = {
    "blocked",
    "created",
    "deferred",
    "in_progress",
    "new",
    "open",
    "specified",
    "unresolved",
}
ACTIONABLE_BRIDGE_STATUSES = {"NEW", "REVISED", "GO", "NO-GO"}
REVIEW_QUEUE_BRIDGE_STATUSES = {"NEW", "REVISED"}
PRIME_RESPONSE_BRIDGE_STATUSES = {"GO", "NO-GO"}
ADVISORY_BRIDGE_STATUSES = {"ADVISORY"}
PRIORITY_SORT_ORDER = {
    "P0": 0,
    "P1": 1,
    "P2": 2,
    "P3": 3,
    "P4": 4,
    "HIGH": 5,
    "MEDIUM": 6,
    "LOW": 7,
}
AGENT_RED_SCOPE_INCLUDED = {
    "agent_red_product",
    "agent_red_release",
    "agent_red_operations",
    "agent_red_governance_adoption",
}
AGENT_RED_PRIMARY_SCOPE_INCLUDED = {
    "agent_red_product",
    "agent_red_release",
    "agent_red_operations",
}
GTKB_SCOPE_EXCLUDED = {"gtkb_framework", "gtkb_upstream"}

GTKB_EXCLUDE_TERMS = (
    "gtkb",
    "gt-kb",
    "groundtruth",
    "groundtruth-kb",
    "managed-artifact",
    "managed artifact",
    "managed-skill",
    "managed skill",
    "doctor",
    "scaffold",
    "deliberation archive",
    "formal artifact",
    "session self-initialization",
    "session startup",
    "session lifecycle",
    "wrap-up",
    "codex hook",
    "hook parity",
    "loyal opposition",
    "file bridge",
    "bridge dispatcher",
    "bridge automation",
    "poller",
    "standing backlog",
    "artifact approval",
    "knowledge database",
    "knowledge db",
    "membase",
)

AGENT_RED_RELEASE_TERMS = (
    "agent red",
    "release",
    "production",
    "commercial readiness",
    "commercial-readiness",
    "shopify",
    "stripe",
    "credential",
    "security",
    "sonarcloud",
    "python 3.12",
    "provenance",
    "deploy",
    "container app",
    "azure",
)

AGENT_RED_PRODUCT_TERMS = (
    "widget",
    "tenant",
    "admin",
    "customer",
    "storefront",
    "billing",
    "sms",
    "otp",
    "mfa",
    "magic link",
    "inbox",
    "conversation",
    "pipeline",
    "cosmos",
    "standalone",
    "provider",
    "superadmin",
    "api key",
    "trial",
    "usage",
)

AGENT_RED_PATH_PREFIXES = (
    "src/",
    "admin/",
    "widget/",
    "extensions/",
    "evaluation/",
    "config/",
    "tests/multi_tenant/",
    "tests/unit/",
    "tests/widget/",
    "tests/security/",
    "tests/e2e",
    "tests/rag-documents-upload/",
    "scripts/deploy/",
    "docs/shopify/",
    "docs/architecture/",
    "docs/plans/",
    "docs/research/",
)

GTKB_PATH_PREFIXES = (
    ".claude/",
    ".codex/",
    ".groundtruth/",
    "docs/gtkb-dashboard/",
    "independent-progress-assessments/",
    "scripts/session_self_initialization.py",
    "scripts/check_codex_hook_parity.py",
    "scripts/audit_standing_backlog_sources.py",
    "tests/scripts/",
    "tests/hooks/",
    "memory/gtkb-dashboard-history.json",
)

STARTUP_PRUNING_RELATIVE_FILES = (
    "AGENTS.md",
    "CLAUDE.md",
    "bridge/INDEX.md",
    "independent-progress-assessments/CODEX-SESSION-BOOTSTRAP.md",
    "independent-progress-assessments/CODEX-STANDING-PRIORITIES.md",
    "independent-progress-assessments/GROUNDTRUTH-KB-VISION.md",
    "independent-progress-assessments/CODEX-WAY-OF-WORKING.md",
    "independent-progress-assessments/CODEX-REVIEW-OPERATING-CONTRACT.md",
    "independent-progress-assessments/CODEX-LOYAL-OPPOSITION-RUNBOOK.md",
    "independent-progress-assessments/CODEX-KNOWLEDGE-BASE-INDEX.md",
    "independent-progress-assessments/CODEX-REVIEW-CHECKLISTS.md",
    "independent-progress-assessments/LOYAL-OPPOSITION-LOG.md",
    ".claude/rules/deliberation-protocol.md",
    ".claude/settings.json",
    "memory/gtkb-dashboard-history.json",
)
STARTUP_PRUNING_LARGE_FILE_BYTES = 50_000
STARTUP_PRUNING_TOTAL_WARN_BYTES = 250_000
WRAPUP_TRIGGER_COMMANDS = (
    "wrap up",
    "wrap up this session",
    "session wrap-up",
    "run session wrap-up",
    "close this session",
    "end this session",
    "new session",
    "fresh session",
    "start a new session",
    "start a fresh session",
    "begin a new session",
    "begin a fresh session",
    "open a new session",
    "prepare a new session",
    "initialize a new session",
    "start fresh",
    "begin fresh",
)


def _run_verified_bridge_startup_maintenance(project_root: Path) -> dict[str, Any]:
    """Archive VERIFIED bridge threads and prune them from the startup index."""
    try:
        from retroactive_harvest_bridge_threads import archive_verified_threads_and_prune_index

        return archive_verified_threads_and_prune_index(
            index_path=project_root / "bridge" / "INDEX.md",
            bridge_dir=project_root / "bridge",
            kb_path=str(project_root / "groundtruth.db"),
        )
    except Exception as exc:  # noqa: BLE001 - startup report should still render
        return {
            "verified_threads_seen": 0,
            "already_archived": 0,
            "inserted": 0,
            "pruned_from_index": 0,
            "failed_count": 1,
            "failed": [str(exc)],
            "kept_unarchived": 0,
        }


def _file_size_profile(project_root: Path, relative_path: str) -> dict[str, Any] | None:
    path = project_root / relative_path
    if not path.is_file():
        return None
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
        stat = path.stat()
    except OSError as exc:
        return {"path": relative_path, "available": False, "error": str(exc)}
    return {
        "path": relative_path,
        "available": True,
        "bytes": stat.st_size,
        "lines": text.count("\n") + (1 if text else 0),
    }


def _latest_insight_profile(project_root: Path) -> dict[str, Any] | None:
    insight_dir = project_root / "independent-progress-assessments" / "CODEX-INSIGHT-DROPBOX"
    try:
        latest = max((p for p in insight_dir.iterdir() if p.is_file()), key=lambda p: p.stat().st_mtime)
    except (FileNotFoundError, ValueError):
        return None
    return _file_size_profile(project_root, str(latest.relative_to(project_root)).replace("\\", "/"))


def _startup_pruning_scan(
    project_root: Path,
    bridge_maintenance: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Measure startup-loaded file bloat and identify safe pruning candidates."""
    profiles = [
        profile
        for profile in (_file_size_profile(project_root, rel) for rel in STARTUP_PRUNING_RELATIVE_FILES)
        if profile is not None
    ]
    latest_insight = _latest_insight_profile(project_root)
    if latest_insight is not None:
        profiles.append(latest_insight)

    available_profiles = [p for p in profiles if p.get("available")]
    total_bytes = sum(int(p.get("bytes", 0)) for p in available_profiles)
    largest = sorted(available_profiles, key=lambda p: int(p.get("bytes", 0)), reverse=True)[:8]

    candidates: list[dict[str, Any]] = []
    if bridge_maintenance and (
        bridge_maintenance.get("inserted")
        or bridge_maintenance.get("already_archived")
        or bridge_maintenance.get("pruned_from_index")
        or (bridge_maintenance.get("comment_compaction") or {}).get("removed_comment_lines")
    ):
        candidates.append(
            {
                "type": "completed",
                "target": "bridge/INDEX.md",
                "action": (
                    "Archived terminal bridge state and compacted oversized historical "
                    "comment blocks from the active startup index."
                ),
                "evidence": bridge_maintenance,
            }
        )

    for profile in largest:
        if int(profile.get("bytes", 0)) >= STARTUP_PRUNING_LARGE_FILE_BYTES:
            candidates.append(
                {
                    "type": "candidate",
                    "target": profile["path"],
                    "action": "Review for summarization, archival split, or index-first loading.",
                    "evidence": {
                        "bytes": profile["bytes"],
                        "lines": profile["lines"],
                    },
                }
            )

    if total_bytes >= STARTUP_PRUNING_TOTAL_WARN_BYTES:
        candidates.append(
            {
                "type": "candidate",
                "target": "session startup corpus",
                "action": "Reduce default startup reads to compact indices plus targeted detail files.",
                "evidence": {"total_bytes": total_bytes, "file_count": len(available_profiles)},
            }
        )

    return {
        "scope": "startup_loaded_files_and_coordination_state",
        "total_bytes": total_bytes,
        "file_count": len(available_profiles),
        "largest_files": largest,
        "candidate_count": len([c for c in candidates if c["type"] == "candidate"]),
        "completed_count": len([c for c in candidates if c["type"] == "completed"]),
        "candidates": candidates,
    }


def _now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _parse_iso8601(value: str | None) -> datetime | None:
    text = str(value or "").strip()
    if not text:
        return None
    normalized = text[:-1] + "+00:00" if text.endswith("Z") else text
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError:
        return None
    return parsed.astimezone(UTC) if parsed.tzinfo is not None else parsed.replace(tzinfo=UTC)


def _iso_is_ordered(earlier: str | None, later: str | None) -> bool:
    earlier_dt = _parse_iso8601(earlier)
    later_dt = _parse_iso8601(later)
    if earlier_dt is None or later_dt is None:
        return False
    return earlier_dt <= later_dt


def _iso_elapsed_ms(start: str | None, end: str | None) -> int | None:
    start_dt = _parse_iso8601(start)
    end_dt = _parse_iso8601(end)
    if start_dt is None or end_dt is None:
        return None
    return int((end_dt - start_dt).total_seconds() * 1000)


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return ""


# Per bridge/generator-hardening-001-003.md Â§4.7 + Codex -004 GO:
# _LOCAL_ENV_CACHE dropped. With project_root threaded, the cache would
# need a per-root key; the .env.local parse is trivial work and
# eliminates the multi-root cache-correctness question.


def _local_env_values(project_root: Path) -> dict[str, str]:
    """Read non-secret routing values from local env files without logging them.

    Per bridge/generator-hardening-001-003.md Â§4.7: project_root is now
    a required parameter (was: bound to module-level PROJECT_ROOT).
    """

    values: dict[str, str] = {}
    for path in (project_root / ".env.local", project_root / "env.local"):
        if not path.is_file():
            continue
        for raw_line in _read_text(path).splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            values[key.strip()] = value.strip().strip('"').strip("'")
    return values


def _local_env_value(project_root: Path, name: str, default: str = "") -> str:
    """Read one local-env value with environment-variable override.

    Per bridge/generator-hardening-001-003.md Â§4.7 + Codex -002 Finding 2:
    project_root is now a required parameter (was: parameterless wrapper).
    """
    return os.environ.get(name) or _local_env_values(project_root).get(name, default)


def _github_repo_slug(value: str) -> str:
    repo = value.strip()
    if repo.startswith("git@github.com:"):
        repo = repo.split(":", 1)[1]
    if repo.startswith("https://github.com/"):
        repo = repo.removeprefix("https://github.com/")
    if repo.endswith(".git"):
        repo = repo[:-4]
    return repo.strip("/")


def _github_repo_url(repo_slug: str) -> str:
    return f"https://github.com/{repo_slug}.git"


def _active_work_subject(project_root: Path) -> str:
    """Return the canonical active work subject for repo-selection branching.

    Reads ``.claude/session/work-subject.json`` via ``scripts.workstream_focus.load_state``.
    Returns one of ``FOCUS_GTKB_INFRASTRUCTURE`` (``"gtkb_infrastructure"``) or
    ``FOCUS_APPLICATION`` (``"application"``).

    Fail-soft default: returns ``FOCUS_GTKB_INFRASTRUCTURE`` on any error,
    missing canonical-state file, malformed JSON, or unrecognized value. This
    matches the convention that a clean GT-KB checkout defaults to the GT-KB
    platform work subject.

    Per WI-3409 / ``bridge/gtkb-work-subject-aware-testing-integration-probe-003.md``
    GO at ``-004``: the testing/tool integration probe must respect the active
    work subject when selecting the GitHub repository query target so the
    rollup label and underlying data agree.
    """
    try:
        state = _workstream_load_state(project_root)
        subject = state.get("current_subject")
        if subject in (FOCUS_APPLICATION, FOCUS_GTKB_INFRASTRUCTURE):
            return subject
    except Exception:  # noqa: BLE001 - fail-soft per proposal Risks/Rollback contract
        pass
    return FOCUS_GTKB_INFRASTRUCTURE


def _normalize_path(value: str) -> str:
    return value.replace("\\", "/").strip().lstrip("./").lower()


def _extract_paths(value: Any) -> list[str]:
    if not value:
        return []
    if isinstance(value, list):
        return [_normalize_path(str(item)) for item in value if str(item).strip()]
    text = str(value).strip()
    if not text:
        return []
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError:
        return [_normalize_path(part) for part in re.split(r"[,;\n]", text) if part.strip()]
    if isinstance(parsed, list):
        return [_normalize_path(str(item)) for item in parsed if str(item).strip()]
    return [_normalize_path(text)]


def _path_matches(path: str, prefixes: tuple[str, ...]) -> bool:
    normalized = _normalize_path(path)
    return any(normalized.startswith(prefix) for prefix in prefixes)


def _combined_text(row: dict[str, Any] | sqlite3.Row) -> str:
    values = dict(row).values() if isinstance(row, sqlite3.Row) else row.values()
    values = [str(value or "") for value in values]
    return " ".join(values).lower()


def classify_dashboard_scope(row: dict[str, Any] | sqlite3.Row) -> str:
    """Classify whether a record belongs in Agent Red project dashboard KPIs."""

    text = _combined_text(row)
    row_data = dict(row) if isinstance(row, sqlite3.Row) else row
    identifier = str(row_data.get("id", "")).upper()
    title = str(row_data.get("title", ""))
    source_paths = _extract_paths(row_data.get("source_paths"))
    test_file = str(row_data.get("test_file", "") or "")
    path_values = [*source_paths, _normalize_path(test_file)]

    if identifier.startswith("AR-") or "agent red project dashboard" in text:
        return "agent_red_operations"
    if "top for the next prime builder session" in text and "agent red" in text:
        return "agent_red_operations"
    if identifier.startswith("GTKB-") and any(
        term in text
        for term in (
            "upstream gt-kb",
            "managed skill",
            "managed-skill",
            "managed artifact",
            "managed-artifact",
            "doctor/readiness",
            "future adopters",
            "reusable release-candidate gate",
        )
    ):
        return "gtkb_upstream"
    if identifier.startswith("GTKB-") and any(
        term in text
        for term in (
            "agent red release",
            "release-readiness",
            "release readiness",
            "commercial readiness",
            "commercial-readiness",
            "spec-1831",
            "spec-1832",
            "spec-1833",
        )
    ):
        return "agent_red_release"
    if any(_path_matches(path, GTKB_PATH_PREFIXES) for path in path_values):
        return "gtkb_framework"
    if "gtkb" in identifier or identifier.startswith(("GOV-", "PB-", "ADR-", "DCL-")):
        return "gtkb_framework"
    if any(term in text for term in GTKB_EXCLUDE_TERMS):
        if any(term in text for term in ("agent red release", "release readiness", "release-readiness")):
            return "agent_red_governance_adoption"
        return "gtkb_framework"
    if any(_path_matches(path, AGENT_RED_PATH_PREFIXES) for path in path_values):
        return "agent_red_product"
    if any(term in text for term in AGENT_RED_RELEASE_TERMS):
        return "agent_red_release"
    if any(term in text for term in AGENT_RED_PRODUCT_TERMS):
        return "agent_red_product"
    if title.startswith("Test:"):
        return "agent_red_product"
    return "unknown"


def _scope_counts(rows: list[dict[str, Any] | sqlite3.Row]) -> dict[str, int]:
    return dict(sorted(Counter(classify_dashboard_scope(row) for row in rows).items()))


def _is_agent_red_scope(row: dict[str, Any] | sqlite3.Row, *, primary_only: bool = False) -> bool:
    included = AGENT_RED_PRIMARY_SCOPE_INCLUDED if primary_only else AGENT_RED_SCOPE_INCLUDED
    if isinstance(row, dict):
        if "_cached_scope" not in row:
            row["_cached_scope"] = classify_dashboard_scope(row)
        scope = row["_cached_scope"]
    else:
        scope = classify_dashboard_scope(row)
    return scope in included


def _work_item_priority_rank(row: dict[str, Any]) -> int:
    raw_priority = str(row.get("priority") or "").strip().upper()
    return PRIORITY_SORT_ORDER.get(raw_priority, len(PRIORITY_SORT_ORDER) + 1)


def _work_item_order_value(row: dict[str, Any]) -> int:
    raw_order = row.get("implementation_order")
    if isinstance(raw_order, int):
        return raw_order
    try:
        return int(str(raw_order))
    except (TypeError, ValueError):
        return 1_000_000


def _project_state_rollup(work_items: list[dict[str, Any]]) -> dict[str, Any]:
    grouped: dict[str, list[dict[str, Any]]] = {}
    ungrouped_non_terminal: list[dict[str, Any]] = []
    status_counts = Counter(str(row.get("resolution_status") or "none") for row in work_items)

    for row in work_items:
        status = str(row.get("resolution_status") or "")
        if status not in NON_TERMINAL_WORK_ITEM_STATUSES:
            continue
        project_name = str(row.get("project_name") or "").strip()
        if not project_name:
            ungrouped_non_terminal.append(row)
            continue
        grouped.setdefault(project_name, []).append(row)

    projects: list[dict[str, Any]] = []
    for project_name, rows in grouped.items():
        sorted_rows = sorted(
            rows,
            key=lambda row: (
                _work_item_order_value(row),
                _work_item_priority_rank(row),
                str(row.get("id") or ""),
            ),
        )
        top = sorted_rows[0]
        projects.append(
            {
                "project": project_name,
                "non_terminal_count": len(rows),
                "status_counts": dict(
                    sorted(Counter(str(row.get("resolution_status") or "none") for row in rows).items())
                ),
                "top_id": str(top.get("id") or ""),
                "top_title": str(top.get("title") or ""),
                "top_status": str(top.get("resolution_status") or "none"),
                "top_priority": str(top.get("priority") or ""),
                "top_order": top.get("implementation_order"),
            }
        )

    projects.sort(key=lambda project: (-int(project["non_terminal_count"]), str(project["project"])))
    return {
        "available": True,
        "source": "MemBase table: current_work_items",
        "project_group_field": "project_name",
        "total_current_work_items": len(work_items),
        "status_counts": dict(sorted(status_counts.items())),
        "non_terminal_work_items": sum(int(project["non_terminal_count"]) for project in projects)
        + len(ungrouped_non_terminal),
        "active_project_count": len(projects),
        "ungrouped_non_terminal_count": len(ungrouped_non_terminal),
        "projects": projects,
    }


def _database_metrics(project_root: Path) -> dict[str, Any]:
    # GTKB-ISOLATION-012 Phase 4 baseline: the Agent Red startup summary path
    # reads groundtruth.db only through the scoped-service client. The
    # `check_scoped_service_boundary.py` guard fails the release gate if a
    # direct sqlite3.connect(...groundtruth.db...) call reappears in this
    # function body.
    try:
        client = GtkbScopedClient.from_project_root(project_root)
        envelope = client.invoke(DASHBOARD_SUMMARY_READ, project_root=project_root)
    except (ScopedServiceConfigError, ScopedOperationError) as exc:
        return {"available": False, "error": f"scoped-client error: {exc}"}

    source_metadata = {
        "source": envelope.get("source"),
        "source_path": envelope.get("source_path"),
        "freshness": envelope.get("freshness"),
        "subject": envelope.get("subject"),
        "operation": envelope.get("operation"),
        "application_id": envelope.get("application_id"),
    }

    if not envelope.get("available"):
        return {
            "available": False,
            "error": envelope.get("error", "scoped-client unavailable"),
            "source_metadata": source_metadata,
        }

    payload = envelope.get("payload") or {}
    specifications = list(payload.get("specifications", []))
    work_items = list(payload.get("work_items", []))
    tests = list(payload.get("tests", []))
    deliberations = list(payload.get("deliberations", []))
    test_procedures_count = int(payload.get("test_procedures_count", 0))

    agent_red_specs = [row for row in specifications if _is_agent_red_scope(row)]
    agent_red_work_items = [row for row in work_items if _is_agent_red_scope(row)]
    agent_red_tests = [row for row in tests if _is_agent_red_scope(row)]
    agent_red_deliberations = [row for row in deliberations if _is_agent_red_scope(row)]
    open_work_items = [
        row
        for row in agent_red_work_items
        if str(row.get("resolution_status") or "") in NON_TERMINAL_WORK_ITEM_STATUSES
    ]
    return {
        "available": True,
        "source_metadata": source_metadata,
        "specifications": {
            "current_total": len(agent_red_specs),
            "raw_current_total": len(specifications),
            "status_counts": dict(sorted(Counter(str(row.get("status") or "none") for row in agent_red_specs).items())),
            "type_counts": dict(sorted(Counter(str(row.get("type") or "none") for row in agent_red_specs).items())),
            "scope_counts": _scope_counts(specifications),
            "scope_confidence": "gtkb_current_heuristic",
        },
        "membase": {
            "work_item_status_counts": dict(
                sorted(Counter(str(row.get("resolution_status") or "none") for row in agent_red_work_items).items())
            ),
            "open_work_items": len(open_work_items),
            "raw_open_work_items": sum(
                1 for row in work_items if str(row.get("resolution_status") or "") in NON_TERMINAL_WORK_ITEM_STATUSES
            ),
            "test_records": len(agent_red_tests),
            "test_procedure_records": test_procedures_count,
            "scope_counts": _scope_counts(work_items),
            "scope_confidence": "gtkb_current_heuristic",
            "project_state_rollup": _project_state_rollup(work_items),
        },
        "deliberation_archive": {
            "current_total": len(agent_red_deliberations),
            "raw_current_total": len(deliberations),
            "outcome_counts": dict(
                sorted(Counter(str(row.get("outcome") or "none") for row in agent_red_deliberations).items())
            ),
            "scope_counts": _scope_counts(deliberations),
            "scope_confidence": "gtkb_current_heuristic",
        },
        "scope": {
            "version": DASHBOARD_SCOPE_VERSION,
            "note": DASHBOARD_SCOPE_NOTE,
            "excluded_scopes": sorted(GTKB_SCOPE_EXCLUDED),
        },
    }


def _backlog_items_from_membase(project_root: Path) -> list[dict[str, Any]]:
    """Query MemBase work_items via ``gt backlog list --json`` (canonical backlog surface).

    Returns a list of dicts with ``id``, ``title``, ``body``, ``approval_state``,
    ``resolution_status``, and ``priority`` keys. The approval_state /
    resolution_status / priority fields are required by the top-3 priority
    selection in ``_backlog_metrics`` per SPEC-ENVELOPE-DISCLOSURE-UI-001.

    Per DELIB-S337-WORK-LIST-MD-DELETION-AT-MIGRATION-CONCLUSION, the canonical
    backlog is MemBase ``work_items``; the legacy markdown backlog view is retired.
    """
    try:
        result = subprocess.run(
            [sys.executable, "-m", "groundtruth_kb", "backlog", "list", "--json"],
            capture_output=True,
            text=True,
            timeout=30,
            cwd=str(project_root),
        )
        if result.returncode != 0:
            return []
        raw_items: list[dict[str, Any]] = json.loads(result.stdout)
    except Exception:
        return []
    items: list[dict[str, Any]] = []
    for row in raw_items:
        items.append(
            {
                "id": str(row.get("id", "")),
                "title": str(row.get("title", "")),
                "body": str(row.get("description") or row.get("status_detail") or ""),
                "approval_state": str(row.get("approval_state") or ""),
                "resolution_status": str(row.get("resolution_status") or ""),
                "priority": row.get("priority"),
            }
        )
    return items


_RESIDUAL_OVERRIDE_RE = re.compile(r"\*\*Status:\*\*\s+VERIFIED\s*\(residual:", re.IGNORECASE)
_STALE_PRIORITY_RE = re.compile(r"\*\*Priority:\*\*\s+Stale\b", re.IGNORECASE)


def _work_item_id_to_bridge_document(wi_id: str) -> str:
    return wi_id.lower()


def _bridge_index_latest_status(project_root: Path) -> dict[str, str]:
    index_path = project_root / "bridge" / "INDEX.md"
    if not index_path.exists():
        return {}
    text = _read_text(index_path)
    result: dict[str, str] = {}
    current: str | None = None
    for line in text.splitlines():
        if line.startswith("Document: "):
            current = line.split(": ", 1)[1].strip()
            continue
        if not current:
            continue
        match = re.match(r"^(NEW|REVISED|GO|NO-GO|VERIFIED|ADVISORY|DEFERRED):\s+bridge/", line)
        if match:
            result[current] = match.group(1)
            current = None
    return result


def _residual_override_present(body: str) -> bool:
    return bool(_RESIDUAL_OVERRIDE_RE.search(body or ""))


_PRIORITY_RANK = {"P0": 0, "P1": 1, "P2": 2, "P3": 3, "P4": 4}


def _top_priority_sort_key(item: dict[str, Any]) -> tuple[int, str]:
    """Order top-3 by priority (P0 highest, none lowest) then by stable WI id.

    Per SPEC-ENVELOPE-DISCLOSURE-UI-001: highest-priority (P0 > P1 > P2 > P3 >
    P4 > none); within same priority, lowest WI id (stable order).
    """

    priority = str(item.get("priority") or "").upper().strip()
    return (_PRIORITY_RANK.get(priority, 5), str(item.get("id") or ""))


def _backlog_metrics(project_root: Path) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    items = _backlog_items_from_membase(project_root)
    bridge_status = _bridge_index_latest_status(project_root)
    classified = []
    for item in items:
        row = {"id": item["id"], "title": item["title"], "description": item.get("body", "")}
        classified.append({**item, "scope": classify_dashboard_scope(row)})
    primary_items = [item for item in classified if item["scope"] in AGENT_RED_PRIMARY_SCOPE_INCLUDED]
    visible_items = primary_items or [item for item in classified if item["scope"] in AGENT_RED_SCOPE_INCLUDED]

    filtered_verified_ids: list[str] = []
    filtered_stale_ids: list[str] = []
    eligible: list[dict[str, Any]] = []
    for item in visible_items:
        wi_id = item.get("id", "")
        body = item.get("body", "")
        mapped = _work_item_id_to_bridge_document(wi_id)
        latest_status = bridge_status.get(mapped)
        if latest_status == "VERIFIED" and not _residual_override_present(body):
            filtered_verified_ids.append(wi_id)
            continue
        if _STALE_PRIORITY_RE.search(body):
            filtered_stale_ids.append(wi_id)
            continue
        eligible.append(item)

    # Top-3 selection per SPEC-ENVELOPE-DISCLOSURE-UI-001:
    # Operates on ALL classified items (bypasses the agent_red scope filter so
    # GT-KB infrastructure WIs appear in the session-startup priority surface).
    # Applies: VERIFIED bridge filter, stale priority filter,
    # approval_state='implementation_authorized', resolution_status open/in_progress/blocked.
    # Computed once; reused at both consumption sites (dict field and tuple return).
    top_eligible: list[dict[str, Any]] = []
    for _item in classified:
        _wi_id = _item.get("id", "")
        _body = _item.get("body", "")
        _mapped = _work_item_id_to_bridge_document(_wi_id)
        _latest = bridge_status.get(_mapped)
        if _latest == "VERIFIED" and not _residual_override_present(_body):
            continue
        if _STALE_PRIORITY_RE.search(_body):
            continue
        if _item.get("approval_state") == "implementation_authorized" and _item.get("resolution_status") in (
            "open",
            "in_progress",
            "blocked",
        ):
            top_eligible.append(_item)
    top_eligible.sort(key=_top_priority_sort_key)
    top_priority = top_eligible[:3]
    return {
        "active_item_count": len(eligible),
        "raw_active_item_count": len(items),
        "top_priority_actions": top_priority,
        "source": "MemBase work_items",
        "scope_counts": dict(sorted(Counter(item["scope"] for item in classified).items())),
        "scope_confidence": "gtkb_current_heuristic",
        "filtered_verified_ids": filtered_verified_ids,
        "filtered_stale_ids": filtered_stale_ids,
    }, top_priority


def _bridge_metrics(project_root: Path) -> dict[str, Any]:
    index_path = project_root / "bridge" / "INDEX.md"
    index_text = _read_text(index_path)
    entries: list[dict[str, str]] = []
    current_document: str | None = None
    for line in index_text.splitlines():
        if line.startswith("Document: "):
            current_document = line.split(": ", 1)[1].strip()
            continue
        if not current_document:
            continue
        match = re.match(r"^(NEW|REVISED|GO|NO-GO|VERIFIED|ADVISORY|DEFERRED):\s+(bridge/[^\s]+)", line)
        if not match:
            continue
        entries.append({"document": current_document, "status": match.group(1), "path": match.group(2)})
        current_document = None

    classified = []
    for entry in entries:
        content = _read_text(project_root / entry["path"])
        row = {
            "id": entry["document"],
            "title": entry["document"].replace("-", " "),
            "description": content[:4000],
            "source_paths": [entry["path"]],
        }
        classified.append({**entry, "scope": classify_dashboard_scope(row)})

    visible_entries = [entry for entry in classified if entry["scope"] in AGENT_RED_PRIMARY_SCOPE_INCLUDED]
    counts = Counter(entry["status"] for entry in visible_entries)
    actionable = [entry for entry in visible_entries if entry["status"] in ACTIONABLE_BRIDGE_STATUSES]
    raw_review_queue = [entry for entry in entries if entry["status"] in REVIEW_QUEUE_BRIDGE_STATUSES]
    raw_prime_response_queue = [entry for entry in entries if entry["status"] in PRIME_RESPONSE_BRIDGE_STATUSES]
    raw_advisory_entries = [entry for entry in entries if entry["status"] in ADVISORY_BRIDGE_STATUSES]
    return {
        "latest_status_counts": dict(sorted(counts.items())),
        "actionable_count": len(actionable),
        "actionable_by_status": dict(sorted(Counter(entry["status"] for entry in actionable).items())),
        "oldest_actionable": actionable[:5],
        "raw_latest_status_counts": dict(sorted(Counter(entry["status"] for entry in entries).items())),
        "raw_actionable_count": sum(1 for entry in entries if entry["status"] in ACTIONABLE_BRIDGE_STATUSES),
        "raw_review_queue_count": len(raw_review_queue),
        "raw_review_queue_by_status": dict(sorted(Counter(entry["status"] for entry in raw_review_queue).items())),
        "raw_prime_response_queue_count": len(raw_prime_response_queue),
        "raw_prime_response_queue_by_status": dict(
            sorted(Counter(entry["status"] for entry in raw_prime_response_queue).items())
        ),
        "raw_advisory_count": len(raw_advisory_entries),
        "raw_advisory_documents": [entry["document"] for entry in raw_advisory_entries],
        "raw_advisory_response_paths": ["proposal", "rebuttal", "defer", "candidate-artifact"],
        "scope_counts": dict(sorted(Counter(entry["scope"] for entry in classified).items())),
        "scope_confidence": "gtkb_current_heuristic",
        "source": "bridge/INDEX.md",
        "source_read_mode": "direct_file_read",
        "source_authority": "live bridge/INDEX.md is the sole authoritative bridge queue source",
        "derived_artifacts_authoritative": False,
        "live_index_available": index_path.is_file(),
    }


def _dev_environment_inventory_status(project_root: Path) -> dict[str, Any]:
    public_json = project_root / DEV_ENV_INVENTORY_PUBLIC_JSON_RELATIVE_PATH
    public_markdown = project_root / DEV_ENV_INVENTORY_PUBLIC_MARKDOWN_RELATIVE_PATH
    base = {
        "public_json": DEV_ENV_INVENTORY_PUBLIC_JSON_RELATIVE_PATH.as_posix(),
        "public_markdown": DEV_ENV_INVENTORY_PUBLIC_MARKDOWN_RELATIVE_PATH.as_posix(),
        "present": public_json.is_file(),
        "markdown_present": public_markdown.is_file(),
        "authoritative": False,
        "full_inventory_loaded": False,
        "max_age_hours": DEV_ENV_INVENTORY_MAX_AGE_HOURS,
    }
    if not public_json.is_file():
        return {
            **base,
            "state": "missing",
            "health": "red",
            "generated_at": None,
            "age_hours": None,
            "redaction_status": "unknown",
            "collector_version": "unknown",
            "collector_hash": None,
            "missing_sections": list(DEV_ENV_INVENTORY_REQUIRED_SECTIONS),
            "latest_verification_command": (
                "python scripts/collect_dev_environment_inventory.py "
                "--public-json docs/release/dev-environment-inventory.json "
                "--public-markdown docs/release/dev-environment-inventory.md "
                "--local-json .gtkb-state/dev-environment-inventory/local.json"
            ),
        }
    try:
        payload = json.loads(public_json.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return {
            **base,
            "state": "malformed",
            "health": "red",
            "generated_at": None,
            "age_hours": None,
            "redaction_status": "unknown",
            "collector_version": "unknown",
            "collector_hash": None,
            "missing_sections": list(DEV_ENV_INVENTORY_REQUIRED_SECTIONS),
            "error": str(exc),
            "latest_verification_command": "python scripts/collect_dev_environment_inventory.py --check-only",
        }
    if not isinstance(payload, dict):
        payload = {}
    generated_at = str(payload.get("generated_at") or "")
    generated_dt = _parse_iso8601(generated_at)
    age_hours = (
        round((datetime.now(UTC) - generated_dt).total_seconds() / 3600, 1) if generated_dt is not None else None
    )
    missing_sections = [section for section in DEV_ENV_INVENTORY_REQUIRED_SECTIONS if section not in payload]
    redaction_status = str((payload.get("redaction") or {}).get("status") or "unknown")
    collector = payload.get("collector") or {}
    verification = payload.get("verification") or {}
    stale = age_hours is None or age_hours > DEV_ENV_INVENTORY_MAX_AGE_HOURS
    if missing_sections or redaction_status != "pass":
        health = "red"
        state = "invalid"
    elif stale:
        health = "yellow"
        state = "stale"
    else:
        health = "green"
        state = "present"
    return {
        **base,
        "state": state,
        "health": health,
        "generated_at": generated_at or None,
        "age_hours": age_hours,
        "redaction_status": redaction_status,
        "collector_version": str(collector.get("version") or "unknown"),
        "collector_hash": collector.get("script_hash"),
        "missing_sections": missing_sections,
        "latest_verification_command": str(
            verification.get("latest_command") or "python scripts/collect_dev_environment_inventory.py --check-only"
        ),
    }


def _harness_parity_status(project_root: Path, *, harness_name: str | None, role_profile: str) -> dict[str, Any]:
    harness_scope = _normalize_harness_name(harness_name) or "all"
    if harness_scope not in {"claude", "codex"}:
        harness_scope = "all"
    try:
        from scripts.check_harness_parity import check_harness_parity  # noqa: PLC0415

        report = check_harness_parity(
            project_root,
            harness=harness_scope,
            role=role_profile,
            include_all=False,
        )
    except Exception as exc:  # noqa: BLE001 - startup must continue with visible diagnostic
        return {
            "status": "unavailable",
            "harness_scope": harness_scope,
            "role_scope": role_profile,
            "counts": {},
            "verification_command": "python scripts/check_harness_parity.py --all --markdown",
            "error": str(exc),
        }
    return {
        "status": report.overall_status.lower(),
        "harness_scope": harness_scope,
        "role_scope": role_profile,
        "counts": report.counts,
        "verification_command": (
            f"python scripts/check_harness_parity.py --harness {harness_scope} --role {role_profile} --markdown"
            if harness_scope != "all"
            else "python scripts/check_harness_parity.py --all --markdown"
        ),
    }


def _harness_parity_compact_text(status: dict[str, Any]) -> str:
    counts = status.get("counts") if isinstance(status.get("counts"), dict) else {}
    count_text = ", ".join(f"{key}={value}" for key, value in sorted(counts.items())) or "no counts"
    text = (
        f"{status.get('status', 'unknown')} "
        f"(harness={status.get('harness_scope', 'unknown')}, "
        f"role={status.get('role_scope', 'unknown')}, {count_text})"
    )
    if status.get("error"):
        text += f"; error={status['error']}"
    return text


def _release_blockers(project_root: Path) -> list[str]:
    text = _read_text(project_root / "memory" / "release-readiness.md")
    blockers: list[str] = []
    in_section = False
    for line in text.splitlines():
        if line.startswith("## Remaining Release Blockers"):
            in_section = True
            continue
        if in_section and line.startswith("## "):
            break
        if in_section and line.startswith("- "):
            blockers.append(line[2:].strip())
    return blockers


def _git_drift(project_root: Path) -> dict[str, Any]:
    try:
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=project_root,
            text=True,
            capture_output=True,
            encoding="utf-8",
            errors="replace",
            timeout=30,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {"available": False, "error": str(exc)}

    if result.returncode != 0:
        return {"available": False, "error": result.stderr.strip()}

    lines = [line for line in result.stdout.splitlines() if line.strip()]
    agent_red_lines = [
        line
        for line in lines
        if _path_matches(line[3:] if len(line) > 3 else line, AGENT_RED_PATH_PREFIXES)
        and not _path_matches(line[3:] if len(line) > 3 else line, GTKB_PATH_PREFIXES)
    ]
    return {
        "available": True,
        "changed_path_count": len(agent_red_lines),
        "raw_changed_path_count": len(lines),
        "untracked_path_count": sum(1 for line in agent_red_lines if line.startswith("??")),
        "deleted_path_count": sum(1 for line in agent_red_lines if "D" in line[:2]),
        "scope_confidence": "gtkb_current_heuristic",
    }


def _user_extension_discovery_opt_in() -> bool:
    """Per bridge/gh-002-skills-plugin-cache-closure-scoping-2026-04-28-004.md (GO):
    Home-directory user-extension discovery for skills + plugin-cache is OFF
    by default (root-contained per .claude/rules/project-root-boundary.md).
    Owner can set GTKB_DISCOVER_USER_EXTENSIONS=1 to enable opt-in scanning.
    Strict "1" only; no other truthy values. SessionStart hooks must NOT
    set this env var.
    """
    return os.environ.get("GTKB_DISCOVER_USER_EXTENSIONS") == "1"


def _discover_skill_files(project_root: Path) -> list[Path]:
    roots = [project_root / ".claude" / "skills"]
    if _user_extension_discovery_opt_in():
        roots.extend(
            [
                Path.home() / ".codex" / "skills",
                Path.home() / ".agents" / "skills",
            ]
        )
    skill_files: list[Path] = []
    for root in roots:
        if not root.is_dir():
            continue
        for path in root.rglob("SKILL.md"):
            try:
                path.relative_to(root)
            except ValueError:
                continue
            skill_files.append(path)
    return sorted(set(skill_files), key=lambda path: str(path).lower())


def _skill_name(path: Path) -> str:
    return path.parent.name


def _plugin_inventory() -> list[str]:
    plugins: set[str] = set()
    if not _user_extension_discovery_opt_in():
        return sorted(plugins)
    plugin_cache = Path.home() / ".codex" / "plugins" / "cache"
    if plugin_cache.is_dir():
        for path in plugin_cache.glob("*/*"):
            if path.is_dir():
                plugins.add(path.name)
    return sorted(plugins)


def _command_available(command: str) -> bool:
    return shutil.which(command) is not None


def _git_remote_origin(project_root: Path) -> dict[str, Any]:
    configured_repo = _github_repo_slug(_local_env_value(project_root, "AGENT_RED_GITHUB_REPO"))
    if configured_repo:
        return {
            "present": True,
            "host": "github.com",
            "repository": configured_repo,
            "source": "AGENT_RED_GITHUB_REPO",
            "remote_url": _github_repo_url(configured_repo),
        }

    try:
        result = subprocess.run(
            ["git", "remote", "get-url", "origin"],
            cwd=project_root,
            text=True,
            capture_output=True,
            encoding="utf-8",
            errors="replace",
            timeout=10,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {"present": False, "host": None, "repository": None, "error": str(exc)}

    if result.returncode != 0:
        return {"present": False, "host": None, "repository": None, "error": result.stderr.strip()}

    remote_url = result.stdout.strip()
    host = "github.com" if "github.com" in remote_url.lower() else "unknown"
    repository = remote_url.rstrip("/").removesuffix(".git").split(":")[-1].split("github.com/")[-1]
    return {
        "present": bool(remote_url),
        "host": host,
        "repository": repository if "/" in repository else None,
        "source": "git remote origin",
        "remote_url": remote_url,
    }


def _command_output(command: list[str], cwd: Path, timeout: int = 10) -> dict[str, Any]:
    try:
        result = subprocess.run(
            command,
            cwd=cwd,
            text=True,
            capture_output=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {"ok": False, "stdout": "", "stderr": str(exc), "returncode": None}
    return {
        "ok": result.returncode == 0,
        "stdout": result.stdout.strip(),
        "stderr": result.stderr.strip(),
        "returncode": result.returncode,
    }


def _read_toml(path: Path) -> dict[str, Any]:
    try:
        with path.open("rb") as handle:
            return tomllib.load(handle)
    except (FileNotFoundError, tomllib.TOMLDecodeError):
        return {}


def _version_tuple(value: str | None) -> tuple[int, ...]:
    if not value:
        return ()
    match = re.search(r"(\d+(?:\.\d+){0,3})", value)
    if not match:
        return ()
    return tuple(int(part) for part in match.group(1).split("."))


def _compare_versions(left: str | None, right: str | None) -> int:
    left_tuple = _version_tuple(left)
    right_tuple = _version_tuple(right)
    width = max(len(left_tuple), len(right_tuple), 1)
    padded_left = left_tuple + (0,) * (width - len(left_tuple))
    padded_right = right_tuple + (0,) * (width - len(right_tuple))
    return (padded_left > padded_right) - (padded_left < padded_right)


def _repo_web_url(remote_url: str | None) -> str | None:
    if not remote_url:
        return None
    value = remote_url.strip()
    if value.startswith("git@github.com:"):
        value = "https://github.com/" + value.split(":", 1)[1]
    if value.endswith(".git"):
        value = value[:-4]
    return value


def _latest_remote_semver_tag(project_root: Path, remote_url: str) -> dict[str, Any]:
    result = _command_output(["git", "ls-remote", "--tags", "--sort=-v:refname", remote_url], project_root, timeout=12)
    if not result["ok"]:
        return {"available": False, "tag": None, "sha": None, "error": result["stderr"]}
    tags: dict[str, str] = {}
    for line in result["stdout"].splitlines():
        parts = line.split()
        if len(parts) != 2:
            continue
        sha, ref = parts
        if ref.endswith("^{}"):
            ref = ref[:-3]
        tag = ref.removeprefix("refs/tags/")
        if _version_tuple(tag):
            tags[tag] = sha
    if not tags:
        return {"available": False, "tag": None, "sha": None, "error": "no semver tags found"}
    tag = sorted(tags, key=_version_tuple, reverse=True)[0]
    return {"available": True, "tag": tag, "sha": tags[tag], "error": None}


def _remote_branch_sha(project_root: Path, remote_url: str, branch: str = "main") -> dict[str, Any]:
    result = _command_output(["git", "ls-remote", remote_url, f"refs/heads/{branch}"], project_root, timeout=12)
    if not result["ok"]:
        return {"available": False, "branch": branch, "sha": None, "error": result["stderr"]}
    first_line = result["stdout"].splitlines()[0] if result["stdout"] else ""
    sha = first_line.split()[0] if first_line else None
    return {"available": bool(sha), "branch": branch, "sha": sha, "error": None if sha else "branch not found"}


def _gtkb_package_info() -> dict[str, Any]:
    try:
        module = __import__("groundtruth_kb")
    except Exception as exc:  # pragma: no cover - defensive in partially installed environments.
        return {"available": False, "version": None, "file": None, "error": str(exc)}
    return {
        "available": True,
        "version": getattr(module, "__version__", None),
        "file": str(getattr(module, "__file__", "")),
        "error": None,
    }


def _git_checkout_info(path: Path, project_root: Path) -> dict[str, Any]:
    if not path.is_dir():
        return {"available": False, "path": str(path), "error": "checkout not found"}
    # Owner-directive scope check per .claude/rules/project-root-boundary.md:
    # checkouts outside project_root must not trigger live git subprocesses.
    # See bridge/generator-hardening-cross-repo-005.md GO. Live cross-repo
    # upgrade-posture inspection is removed by design; the dashboard renders
    # the degraded record gracefully via the "available: false" branch.
    resolved_path = path.resolve()
    resolved_root = project_root.resolve()
    try:
        resolved_path.relative_to(resolved_root)
    except ValueError:
        return {
            "available": False,
            "path": str(path),
            "error": "checkout_outside_project_root",
            "scope_diagnostic": (
                "checkout outside --project-root; live cross-repo inspection "
                "removed per owner directive (all live GT-KB artifacts must be "
                "within project root)."
            ),
        }
    branch = _command_output(["git", "branch", "--show-current"], path)
    sha = _command_output(["git", "rev-parse", "HEAD"], path)
    short_sha = _command_output(["git", "rev-parse", "--short", "HEAD"], path)
    remote = _command_output(["git", "remote", "get-url", "origin"], path)
    status = _command_output(["git", "status", "--porcelain"], path)
    if not sha["ok"]:
        return {"available": False, "path": str(path), "error": sha["stderr"]}
    return {
        "available": True,
        "path": str(path),
        "branch": branch["stdout"] if branch["ok"] else None,
        "sha": sha["stdout"],
        "short_sha": short_sha["stdout"] if short_sha["ok"] else None,
        "remote_url": remote["stdout"] if remote["ok"] else None,
        "dirty_path_count": len([line for line in status["stdout"].splitlines() if line.strip()])
        if status["ok"]
        else None,
        "error": None,
    }


def _gtkb_upgrade_plan(project_root: Path) -> dict[str, Any]:
    try:
        from groundtruth_kb.project.upgrade import plan_upgrade
    except Exception as exc:  # pragma: no cover - defensive in partially installed environments.
        return {"available": False, "error": str(exc), "action_count": None, "action_counts": {}, "sample_actions": []}

    try:
        actions = plan_upgrade(project_root)
    except Exception as exc:
        return {"available": False, "error": str(exc), "action_count": None, "action_counts": {}, "sample_actions": []}

    action_counts = dict(sorted(Counter(action.action for action in actions).items()))
    mutating_actions = [action for action in actions if action.action not in {"warning", "informational"}]
    sample_actions = [
        {"action": action.action, "file": action.file, "reason": action.reason} for action in mutating_actions[:12]
    ]
    return {
        "available": True,
        "error": None,
        "action_count": len(actions),
        "mutating_action_count": len(mutating_actions),
        "action_counts": action_counts,
        "sample_actions": sample_actions,
    }


def _gtkb_upgrade_posture(project_root: Path, *, fast_hook: bool = False) -> dict[str, Any]:
    config = _read_toml(project_root / "groundtruth.toml")
    scaffold_version = config.get("project", {}).get("scaffold_version")
    package = _gtkb_package_info()
    inferred_checkout = None
    if package.get("file"):
        package_path = Path(str(package["file"]))
        if len(package_path.parents) >= 3 and (package_path.parents[2] / "pyproject.toml").is_file():
            inferred_checkout = package_path.parents[2]
    adjacent_checkout = project_root.parent / "groundtruth-kb"
    checkout_path = inferred_checkout or adjacent_checkout
    checkout = _git_checkout_info(checkout_path, project_root)
    configured_gtkb_repo = _github_repo_slug(_local_env_value(project_root, "GROUND_TRUTH_GITHUB_REPO"))
    remote_url = (
        _github_repo_url(configured_gtkb_repo)
        if configured_gtkb_repo
        else checkout.get("remote_url") or "https://github.com/Remaker-Digital/groundtruth-kb.git"
    )
    if fast_hook:
        latest_release = {
            "available": False,
            "tag": None,
            "sha": None,
            "error": "skipped_fast_hook",
        }
        latest_main = {
            "available": False,
            "branch": "main",
            "sha": None,
            "error": "skipped_fast_hook",
        }
    else:
        latest_release = _latest_remote_semver_tag(project_root, str(remote_url))
        latest_main = _remote_branch_sha(project_root, str(remote_url), "main")
    upgrade_plan = _gtkb_upgrade_plan(project_root)

    package_version = package.get("version")
    latest_release_version = latest_release.get("tag")
    release_upgrade_available = (
        latest_release.get("available")
        and package_version is not None
        and _compare_versions(str(package_version), str(latest_release_version)) < 0
    )
    scaffold_upgrade_available = bool(upgrade_plan.get("mutating_action_count"))
    local_main_sha = checkout.get("sha")
    unreleased_upstream_changes = bool(
        latest_main.get("sha") and local_main_sha and latest_main.get("sha") != local_main_sha
    )
    if (
        latest_main.get("sha")
        and local_main_sha
        and latest_main.get("sha") == local_main_sha
        and latest_release.get("tag")
    ):
        count_result = _command_output(
            ["git", "rev-list", "--count", f"{latest_release['tag']}..HEAD"],
            Path(str(checkout_path)),
            timeout=8,
        )
        unreleased_commit_count = (
            int(count_result["stdout"]) if count_result["ok"] and count_result["stdout"].isdigit() else None
        )
    else:
        unreleased_commit_count = None

    if release_upgrade_available:
        status = "release_upgrade_available"
    elif scaffold_upgrade_available:
        status = "scaffold_upgrade_plan_available"
    elif unreleased_upstream_changes or (unreleased_commit_count or 0) > 0:
        status = "unreleased_upstream_changes_available"
    else:
        status = "current_release"

    plan_command = "gt project upgrade --dry-run --dir ."
    apply_command = "gt project upgrade --apply --dir ."
    fallback_prefix = 'python -c "from groundtruth_kb.cli import main; main()"'
    return {
        "status": status,
        "scope": "implementation_infrastructure",
        "package_version": package_version,
        "package_file": package.get("file"),
        "package_import_available": package.get("available"),
        "scaffold_version": scaffold_version,
        "repo_url": _repo_web_url(str(remote_url)),
        "remote_url": remote_url,
        "latest_release_tag": latest_release.get("tag"),
        "latest_release_sha": latest_release.get("sha"),
        "latest_main_branch": latest_main.get("branch"),
        "latest_main_sha": latest_main.get("sha"),
        "local_checkout": checkout,
        "release_upgrade_available": release_upgrade_available,
        "scaffold_upgrade_available": scaffold_upgrade_available,
        "unreleased_upstream_changes_available": unreleased_upstream_changes or (unreleased_commit_count or 0) > 0,
        "unreleased_commit_count": unreleased_commit_count,
        "gt_cli_available": _command_available("gt"),
        "plan_command": plan_command
        if _command_available("gt")
        else f"{fallback_prefix} project upgrade --dry-run --dir .",
        "apply_command": apply_command
        if _command_available("gt")
        else f"{fallback_prefix} project upgrade --apply --dir .",
        "apply_enabled": False,
        "apply_gate": "Static dashboard cannot execute local shell. Apply requires owner approval, clean/acknowledged git state, dry-run review, and post-upgrade tests.",
        "upgrade_plan": upgrade_plan,
        "latest_release_probe_error": latest_release.get("error"),
        "latest_main_probe_error": latest_main.get("error"),
    }


def _gh_auth_status(project_root: Path) -> str:
    if not _command_available("gh"):
        return "gh_cli_missing"
    try:
        result = subprocess.run(
            ["gh", "auth", "status"],
            cwd=project_root,
            text=True,
            capture_output=True,
            encoding="utf-8",
            errors="replace",
            timeout=10,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return "unknown"
    return "authenticated" if result.returncode == 0 else "not_authenticated_or_unavailable"


def _workflow_name(path: Path) -> str:
    text = _read_text(path)
    match = re.search(r"(?m)^name:\s*['\"]?([^'\"]+?)['\"]?\s*$", text)
    return match.group(1).strip() if match else path.stem.replace("-", " ").title()


def _workflow_inventory(project_root: Path) -> dict[str, dict[str, Any]]:
    workflows_dir = project_root / ".github" / "workflows"
    if not workflows_dir.is_dir():
        return {}
    inventory = {}
    for path in sorted([*workflows_dir.glob("*.yml"), *workflows_dir.glob("*.yaml")]):
        inventory[path.name] = {
            "file": path.name,
            "name": _workflow_name(path),
            "text": _read_text(path),
        }
    return inventory


def _latest_github_workflow_runs(project_root: Path, gh_auth_status: str) -> dict[str, Any]:
    # Per WI-3409 / bridge/gtkb-work-subject-aware-testing-integration-probe-003.md
    # GO at -004: branch GitHub query repo on active work subject. The previous
    # implementation unconditionally queried AGENT_RED_GITHUB_REPO; GT-KB sessions
    # then saw Agent Red CI labeled as "GT-KB Testing/tool rollup", a coupling
    # defect. The fix reads the canonical work subject from
    # scripts.workstream_focus.load_state and selects:
    #   - FOCUS_GTKB_INFRASTRUCTURE -> GROUND_TRUTH_GITHUB_REPO (or git remote fallback)
    #   - FOCUS_APPLICATION         -> AGENT_RED_GITHUB_REPO
    work_subject = _active_work_subject(project_root)
    if work_subject == FOCUS_APPLICATION:
        env_var_name = "AGENT_RED_GITHUB_REPO"
    else:
        # FOCUS_GTKB_INFRASTRUCTURE branch (or unknown via fail-soft default)
        env_var_name = "GROUND_TRUTH_GITHUB_REPO"
    if gh_auth_status != "authenticated":
        return {
            "available": False,
            "reason": gh_auth_status,
            "runs_by_workflow": {},
            "queried_work_subject": work_subject,
            "queried_repo": None,
            "queried_env_var": env_var_name,
        }
    repo = _github_repo_slug(_local_env_value(project_root, env_var_name))
    # Per WI-3409 proposal -003 IP-2 (LO -006 NO-GO finding P1-001): the
    # FOCUS_APPLICATION branch must explicitly fall back to the `agent-red`
    # named git remote when AGENT_RED_GITHUB_REPO is empty, and return
    # no-recent-run rather than silently querying the current `origin`
    # remote (which on a GT-KB checkout is Remaker-Digital/groundtruth-kb
    # and would re-introduce the cross-subject coupling defect this fix
    # is supposed to eliminate, just in the opposite direction).
    if not repo and work_subject == FOCUS_APPLICATION:
        try:
            agent_red_remote = subprocess.run(
                ["git", "remote", "get-url", "agent-red"],
                cwd=project_root,
                text=True,
                capture_output=True,
                encoding="utf-8",
                errors="replace",
                timeout=5,
                check=False,
            )
        except (OSError, subprocess.TimeoutExpired):
            agent_red_remote = None
        if agent_red_remote is not None and agent_red_remote.returncode == 0 and agent_red_remote.stdout.strip():
            repo = _github_repo_slug(agent_red_remote.stdout.strip())
        if not repo:
            # No env var, no agent-red git remote: return a no-recent-run
            # result rather than invoking `gh run list` against the current
            # origin remote.
            return {
                "available": False,
                "reason": "application_session_missing_agent_red_target",
                "runs_by_workflow": {},
                "queried_work_subject": work_subject,
                "queried_repo": None,
                "queried_env_var": env_var_name,
            }
    command = [
        "gh",
        "run",
        "list",
        "--limit",
        "100",
        "--json",
        "databaseId,name,workflowName,status,conclusion,headBranch,headSha,createdAt,updatedAt,event,url",
    ]
    if repo:
        command.extend(["--repo", repo])
    try:
        result = subprocess.run(
            command,
            cwd=project_root,
            text=True,
            capture_output=True,
            encoding="utf-8",
            errors="replace",
            timeout=8,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {
            "available": False,
            "reason": str(exc),
            "runs_by_workflow": {},
            "queried_work_subject": work_subject,
            "queried_repo": repo or None,
            "queried_env_var": env_var_name,
        }

    if result.returncode != 0:
        return {
            "available": False,
            "reason": result.stderr.strip(),
            "runs_by_workflow": {},
            "queried_work_subject": work_subject,
            "queried_repo": repo or None,
            "queried_env_var": env_var_name,
        }

    try:
        runs = json.loads(result.stdout or "[]")
    except json.JSONDecodeError as exc:
        return {
            "available": False,
            "reason": f"invalid gh json: {exc}",
            "runs_by_workflow": {},
            "queried_work_subject": work_subject,
            "queried_repo": repo or None,
            "queried_env_var": env_var_name,
        }

    latest: dict[str, dict[str, Any]] = {}
    for run in runs:
        workflow_name = str(run.get("workflowName") or run.get("name") or "")
        if workflow_name and workflow_name not in latest:
            latest[workflow_name] = run
    return {
        "available": True,
        "queried_at": _now_iso(),
        "repository": repo or "current git remote",
        "runs": runs,
        "runs_by_workflow": latest,
        "queried_work_subject": work_subject,
        "queried_repo": repo or "current git remote",
        "queried_env_var": env_var_name,
    }


def _workflow_run_health(run: dict[str, Any] | None) -> str:
    if not run:
        return "no_recent_run"
    status = run.get("status")
    conclusion = run.get("conclusion")
    if status and status != "completed":
        return str(status)
    if conclusion == "success":
        return "passing"
    if conclusion in {"failure", "timed_out", "cancelled", "action_required"}:
        return "failing"
    return str(conclusion or "unknown")


def _workflow_run_summary(run: dict[str, Any] | None) -> str:
    if not run:
        return "No recent run returned by gh."
    sha = str(run.get("headSha") or "")
    short_sha = sha[:7] if sha else "unknown"
    conclusion = run.get("conclusion") or run.get("status") or "unknown"
    branch = run.get("headBranch") or "unknown"
    updated_at = run.get("updatedAt") or run.get("createdAt") or "unknown time"
    return f"{conclusion} on {branch}@{short_sha}, updated {updated_at}"


def _status_from_requirements(requirements: list[bool], manual: bool = False) -> str:
    if requirements and all(requirements):
        return "manual" if manual else "ready"
    if any(requirements):
        return "partial"
    return "not_wired"


def _package_json(project_root: Path, relative_path: str) -> dict[str, Any]:
    candidates = (
        project_root / relative_path,
        project_root / "applications" / "Agent_Red" / relative_path,
    )
    for path in candidates:
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except (FileNotFoundError, json.JSONDecodeError):
            continue
    return {}


def _package_has_script(package_data: dict[str, Any], script_name: str) -> bool:
    return script_name in package_data.get("scripts", {})


def _package_has_dependency(package_data: dict[str, Any], dependency_name: str) -> bool:
    return dependency_name in package_data.get("dependencies", {}) or dependency_name in package_data.get(
        "devDependencies", {}
    )


def _dependency_declared(project_root: Path, dependency_name: str) -> bool:
    text = "\n".join(
        _read_text(project_root / path)
        for path in ["requirements.txt", "requirements-test.txt", "requirements-local.txt"]
    )
    return bool(re.search(rf"(?im)^\s*{re.escape(dependency_name)}(?:[<>=~!].*)?$", text))


def _workflow_text(workflows: dict[str, dict[str, Any]], filename: str) -> str:
    return str(workflows.get(filename, {}).get("text") or "")


def _workflow_run(
    runs: dict[str, Any],
    workflows: dict[str, dict[str, Any]],
    filename: str,
    fallback_name: str | None = None,
    branch: str | None = None,
) -> dict[str, Any] | None:
    workflow_name = str(workflows.get(filename, {}).get("name") or fallback_name or "")
    if branch:
        for run in runs.get("runs", []):
            run_workflow_name = str(run.get("workflowName") or run.get("name") or "")
            if run_workflow_name == workflow_name and run.get("headBranch") == branch:
                return run
        return None
    return runs.get("runs_by_workflow", {}).get(workflow_name)


def _workflow_default_tag(workflow_text: str) -> str | None:
    match = re.search(r"(?im)^\s*default:\s*['\"]?(v\d+\.\d+\.\d+(?:[-.\w]*)?)", workflow_text)
    return match.group(1) if match else None


def _version_from_text(*values: Any) -> str | None:
    text = " ".join(str(value or "") for value in values)
    match = re.search(r"\bv\d+\.\d+\.\d+(?:[-.\w]*)?\b", text)
    return match.group(0) if match else None


def _current_version_manifest(project_root: Path) -> dict[str, Any]:
    versions: dict[str, Any] = {}
    pyproject = _read_toml(project_root / "pyproject.toml")
    if pyproject.get("project", {}).get("version"):
        versions["python_package"] = pyproject["project"]["version"]
    api_version_text = _read_text(project_root / "src" / "api_versioning.py")
    api_match = re.search(r'API_VERSION\s*=\s*["\']([^"\']+)["\']', api_version_text)
    if api_match:
        versions["api_version"] = api_match.group(1)
    for label, relative_path in {
        "root_package": "package.json",
        "widget": "widget/package.json",
        "admin": "admin/package.json",
        "docs_site": "docs-site/package.json",
    }.items():
        package = _package_json(project_root, relative_path)
        if package.get("version"):
            versions[label] = package["version"]
    return {
        "versions": versions,
        "display": ", ".join(f"{key}: {value}" for key, value in versions.items()) or "No package version files found.",
    }


def _recent_git_commits(project_root: Path, limit: int = 12) -> list[dict[str, Any]]:
    result = _command_output(
        ["git", "log", "--date=iso-strict", "--pretty=format:%H%x1f%h%x1f%cI%x1f%an%x1f%s", "-n", str(limit)],
        project_root,
        timeout=10,
    )
    if not result["ok"]:
        return []
    commits = []
    for line in result["stdout"].splitlines():
        parts = line.split("\x1f")
        if len(parts) != 5:
            continue
        sha, short_sha, committed_at, author, subject = parts
        described = _command_output(
            ["git", "describe", "--tags", "--always", "--abbrev=8", sha], project_root, timeout=4
        )
        commits.append(
            {
                "sha": sha,
                "short_sha": short_sha,
                "committed_at": committed_at,
                "author": author,
                "subject": subject,
                "version": described["stdout"] if described["ok"] else short_sha,
            }
        )
    return commits


def _image_refs_from_file(path: Path) -> list[dict[str, str]]:
    text = _read_text(path)
    refs = []
    for match in re.finditer(r"(acragentredeastus\.azurecr\.io/([\w.-]+):([\w.-]+))", text):
        refs.append({"image": match.group(1), "component": match.group(2), "version": match.group(3)})
    return refs


def _workflow_stage(workflow_name: str, run_name: str = "") -> str:
    text = f"{workflow_name} {run_name}".lower()
    if "production" in text or re.search(r"\bprod\b", text):
        return (
            "production_deployment" if "deploy" in text or "release" in text or "upgrade" in text else "production_test"
        )
    if "staging" in text:
        return "staging_deployment" if "deploy" in text or "release" in text or "upgrade" in text else "staging_test"
    if "build" in text or "container" in text or "docker" in text:
        return "build"
    if any(
        term in text
        for term in ("test", "lint", "security", "sonar", "coverage", "accessibility", "chromatic", "quality")
    ):
        return "test"
    if "deploy" in text or "release" in text or "upgrade" in text:
        return "deployment"
    return "workflow"


def _stage_label(stage: str) -> str:
    return {
        "commit": "Commit",
        "build": "Build",
        "test": "Test Run",
        "deployment": "Deployment",
        "staging_deployment": "Staging Deployment",
        "staging_test": "Staging Test",
        "production_deployment": "Production Deployment",
        "production_test": "Production Test",
        "workflow": "Workflow",
    }.get(stage, stage.replace("_", " ").title())


def _result_color(result: str) -> str:
    value = str(result or "").lower()
    if value in {"success", "passing", "pass", "recorded", "configured"}:
        return "green"
    if value in {"failure", "failed", "failing", "timed_out", "cancelled", "action_required"}:
        return "red"
    return "yellow"


def _delivery_timeline(
    project_root: Path, infrastructure: dict[str, Any], *, fast_hook: bool = False
) -> dict[str, Any]:
    workflows = _workflow_inventory(project_root)
    workflow_name_to_file = {str(details.get("name")): filename for filename, details in workflows.items()}
    github = infrastructure.get("testing_service_integrations", {}).get("github", {})
    runs = list(github.get("workflow_runs") or [])
    version_manifest = _current_version_manifest(project_root)
    rows: list[dict[str, Any]] = []

    if not fast_hook:
        for commit in _recent_git_commits(project_root):
            rows.append(
                {
                    "timestamp": commit["committed_at"],
                    "stage": "commit",
                    "stage_label": _stage_label("commit"),
                    "event": commit["subject"],
                    "version": commit["version"],
                    "commit": commit["short_sha"],
                    "branch": "",
                    "result": "recorded",
                    "result_color": "green",
                    "test_results": "Correlate with workflow rows sharing this commit.",
                    "source": "git log",
                    "url": "",
                    "notes": commit["author"],
                }
            )

    for run in runs[:80]:
        workflow_name = str(run.get("workflowName") or run.get("name") or "Workflow")
        workflow_file = workflow_name_to_file.get(workflow_name)
        workflow_text = _workflow_text(workflows, workflow_file) if workflow_file else ""
        stage = _workflow_stage(workflow_name, str(run.get("name") or ""))
        result = str(run.get("conclusion") or run.get("status") or "unknown")
        version = _version_from_text(run.get("name"), workflow_name) or _workflow_default_tag(workflow_text)
        if not version:
            version = str(run.get("headSha") or "")[:8] or "not recorded"
        rows.append(
            {
                "timestamp": run.get("updatedAt") or run.get("createdAt") or "",
                "stage": stage,
                "stage_label": _stage_label(stage),
                "event": workflow_name,
                "version": version,
                "commit": str(run.get("headSha") or "")[:8],
                "branch": run.get("headBranch") or "",
                "result": result,
                "result_color": _result_color(result),
                "test_results": "Workflow conclusion/status is the available test/build result.",
                "source": workflow_file or "GitHub Actions",
                "url": run.get("url") or "",
                "notes": f"event={run.get('event') or 'unknown'}; run={run.get('databaseId') or 'unknown'}",
            }
        )

    for filename, details in sorted(workflows.items()):
        if not filename.startswith("build-"):
            continue
        default_tag = _workflow_default_tag(str(details.get("text") or "")) or "input tag required"
        workflow_path = project_root / ".github" / "workflows" / filename
        workflow_timestamp = (
            datetime.fromtimestamp(workflow_path.stat().st_mtime, UTC).isoformat().replace("+00:00", "Z")
            if workflow_path.is_file()
            else ""
        )
        rows.append(
            {
                "timestamp": workflow_timestamp,
                "stage": "build",
                "stage_label": _stage_label("build"),
                "event": str(details.get("name") or filename),
                "version": default_tag,
                "commit": "",
                "branch": "workflow_dispatch",
                "result": "configured",
                "result_color": "green",
                "test_results": "Build workflow is configured; latest run evidence appears above when GitHub returns it.",
                "source": f".github/workflows/{filename}",
                "url": "",
                "notes": "Manual build workflow.",
            }
        )

    deployment_files = [
        ("staging_deployment", project_root / "scripts" / "agent-container-template.yaml"),
        ("staging_deployment", project_root / "scripts" / "deploy" / "build-and-deploy-staging.ps1"),
        ("production_deployment", project_root / "scripts" / "deploy" / "api-gateway-restore.yaml"),
        ("production_deployment", project_root / "scripts" / "deploy" / "upgrade.ps1"),
        ("production_deployment", project_root / "scripts" / "deploy" / "rollback.ps1"),
    ]
    for stage, path in deployment_files:
        if not path.is_file():
            continue
        refs = _image_refs_from_file(path)
        version = (
            ", ".join(sorted({ref["version"] for ref in refs}))
            or _version_from_text(_read_text(path))
            or "parameterized"
        )
        rows.append(
            {
                "timestamp": datetime.fromtimestamp(path.stat().st_mtime, UTC).isoformat().replace("+00:00", "Z"),
                "stage": stage,
                "stage_label": _stage_label(stage),
                "event": path.name,
                "version": version,
                "commit": "",
                "branch": "",
                "result": "configured",
                "result_color": "yellow",
                "test_results": "Deployment script/manifest evidence only; live environment revision was not queried.",
                "source": path.relative_to(project_root).as_posix(),
                "url": "",
                "notes": "; ".join(ref["image"] for ref in refs[:3]) or "No pinned image found.",
            }
        )

    rows = sorted(rows, key=lambda row: str(row.get("timestamp") or "0000"), reverse=True)
    summary = []
    for stage in ["commit", "build", "test", "staging_deployment", "production_deployment"]:
        stage_rows = [row for row in rows if row.get("stage") == stage]
        latest = stage_rows[0] if stage_rows else {}
        summary.append(
            {
                "stage": stage,
                "label": _stage_label(stage),
                "count": len(stage_rows),
                "latest_result": latest.get("result") or "not detected",
                "latest_version": latest.get("version") or "not recorded",
                "status": _result_color(str(latest.get("result") or "unknown")) if latest else "yellow",
            }
        )
    return {
        "version_manifest": version_manifest,
        "stage_summary": summary,
        "timeline": rows[:160],
    }


def _integration(
    *,
    order: int,
    display_name: str,
    status: str,
    gate_role: str,
    evidence: list[str],
    remediation: str,
    artifacts: list[str] | None = None,
    gaps: list[str] | None = None,
    workflow_file: str | None = None,
    latest_run: dict[str, Any] | None = None,
) -> dict[str, Any]:
    health = _workflow_run_health(latest_run)
    latest_run_summary = _workflow_run_summary(latest_run)
    if latest_run is None and workflow_file is None:
        if status == "manual":
            health = "manual"
            latest_run_summary = "Manual/local capability; no GitHub Actions run expected."
        else:
            health = "configured"
            latest_run_summary = "Configuration detected; no single workflow run is associated."
    return {
        "order": order,
        "display_name": display_name,
        "status": status,
        "scope": "implementation_infrastructure",
        "health": health,
        "latest_run": latest_run,
        "latest_run_summary": latest_run_summary,
        "workflow_file": workflow_file,
        "gate_role": gate_role,
        "remediation": remediation,
        "evidence": evidence,
        "artifacts": artifacts or [],
        "gaps": gaps or [],
    }


def _testing_service_integrations(project_root: Path, plugins: list[str], *, fast_hook: bool = False) -> dict[str, Any]:
    workflows = _workflow_inventory(project_root)
    workflow_names = sorted(workflows)
    workflow_set = set(workflow_names)
    remote = _git_remote_origin(project_root)
    if fast_hook:
        gh_auth_status = "skipped_fast_hook"
        gh_runs = {"available": False, "reason": "skipped_fast_hook", "runs_by_workflow": {}}
    else:
        gh_auth_status = _gh_auth_status(project_root)
        gh_runs = _latest_github_workflow_runs(project_root, gh_auth_status)
    github_plugin_detected = any(plugin.lower() == "github" for plugin in plugins)
    pyproject_text = _read_text(project_root / "pyproject.toml")
    sonar_text = _read_text(project_root / "sonar-project.properties")
    dependabot_text = _read_text(project_root / ".github" / "dependabot.yml")
    python_tests_text = _workflow_text(workflows, "python-tests.yml")
    lint_text = _workflow_text(workflows, "lint.yml")
    security_text = _workflow_text(workflows, "security-scan.yml")
    widget_package = _package_json(project_root, "widget/package.json")
    docs_package = _package_json(project_root, "docs-site/package.json")
    admin_package = _package_json(project_root, "admin/package.json")
    dependabot_ecosystems = sorted(set(re.findall(r'package-ecosystem:\s*["\']?([^"\'\n]+)', dependabot_text)))
    required_workflow_files = [
        "python-tests.yml",
        "release-candidate-gate.yml",
        "lint.yml",
        "security-scan.yml",
        "sonarcloud.yml",
        "docs-quality.yml",
        "accessibility.yml",
    ]
    required_runs = [
        _workflow_run(gh_runs, workflows, filename, branch=DEFAULT_RELEASE_BRANCH)
        for filename in required_workflow_files
        if filename in workflow_set
    ]
    required_health = [_workflow_run_health(run) for run in required_runs]
    parent_health = (
        "failing"
        if "failing" in required_health
        else "running"
        if any(health not in {"passing", "no_recent_run"} for health in required_health)
        else "passing"
        if required_runs and all(health == "passing" for health in required_health)
        else "partial_history"
    )
    ready = (
        remote.get("host") == "github.com"
        and bool(workflow_names)
        and "python-tests.yml" in workflow_set
        and "release-candidate-gate.yml" in workflow_set
        and gh_auth_status == "authenticated"
    )
    partially_configured = (
        remote.get("present") or bool(workflow_names) or github_plugin_detected or _command_available("gh")
    )
    integrations = {
        "github": {
            "order": 10,
            "display_name": "GitHub Actions",
            "status": "ready" if ready else "partial" if partially_configured else "not_configured",
            "scope": "implementation_infrastructure",
            "health": parent_health if gh_runs.get("available") else "live_state_unavailable",
            "queried_at": gh_runs.get("queried_at"),
            "workflow_runs_available": bool(gh_runs.get("available")),
            "latest_run_summary": (
                f"{len(required_runs)} required {DEFAULT_RELEASE_BRANCH} workflow runs checked; health={parent_health}"
                if gh_runs.get("available")
                else "Latest workflow run state unavailable."
            ),
            "remote_present": remote.get("present", False),
            "remote_host": remote.get("host"),
            "repository": remote.get("repository"),
            "workflow_count": len(workflow_names),
            "workflow_names": workflow_names,
            "python_tests_workflow": "python-tests.yml" in workflow_set,
            "release_candidate_gate_workflow": "release-candidate-gate.yml" in workflow_set,
            "security_scan_workflow": "security-scan.yml" in workflow_set,
            "docs_quality_workflow": "docs-quality.yml" in workflow_set,
            "github_plugin_detected": github_plugin_detected,
            "gh_cli_available": _command_available("gh"),
            "gh_auth_status": gh_auth_status,
            "release_branch": DEFAULT_RELEASE_BRANCH,
            "latest_run_source": "gh run list" if gh_runs.get("available") else gh_runs.get("reason"),
            "latest_run_repository": gh_runs.get("repository"),
            "workflow_runs": gh_runs.get("runs", [])[:100],
            # Per WI-3409: surface work-subject-aware probe metadata so the
            # rollup label, dashboard intelligence, and consumers downstream
            # can reflect the actual repository queried for this session.
            "queried_work_subject": gh_runs.get("queried_work_subject"),
            "queried_repo": gh_runs.get("queried_repo"),
            "queried_env_var": gh_runs.get("queried_env_var"),
            "gate_role": "Parent CI runner and repository service for automated release evidence.",
            "remediation": "Open the latest failing required workflow runs, fix the child gate rows they identify, then rerun the failed workflows from GitHub Actions.",
            "evidence": [
                f"remote: {remote.get('host') or 'none'}",
                f"repo: {remote.get('repository') or 'unknown'}",
                f"workflows: {len(workflow_names)}",
                f"gh CLI: {gh_auth_status}",
                f"plugin: {'yes' if github_plugin_detected else 'no'}",
                f"release gate: {'yes' if 'release-candidate-gate.yml' in workflow_set else 'no'}",
                f"queried repo: {gh_runs.get('queried_repo') or 'unknown'} (work subject: {gh_runs.get('queried_work_subject') or 'unknown'})",
            ],
            "artifacts": ["GitHub Actions runs", "uploaded CI artifacts", "PR checks"],
            "gaps": []
            if gh_runs.get("available")
            else ["Latest workflow run state was not available during generation."],
            "state_source": "GROUND_TRUTH_GITHUB_REPO or AGENT_RED_GITHUB_REPO per active work subject, plus local git remote, .github/workflows, local harness plugin cache, gh CLI status, and gh run list when available",
        }
    }
    integrations["pytest_coverage"] = _integration(
        order=20,
        display_name="Pytest Coverage",
        status=_status_from_requirements(
            [
                "python-tests.yml" in workflow_set,
                "--cov=src" in python_tests_text,
                "coverage-merged.json" in python_tests_text,
                "fail_under = 75" in pyproject_text,
            ]
        ),
        workflow_file="python-tests.yml",
        latest_run=_workflow_run(gh_runs, workflows, "python-tests.yml"),
        gate_role="Primary regression test and line-coverage gate.",
        remediation="Inspect the pytest shard and merged coverage artifacts, reproduce the failing shard locally, then restore the configured coverage threshold before rerunning Python Tests.",
        evidence=["pytest shards configured", "merged coverage artifact configured", "coverage fail_under=75"],
        artifacts=["test-results-*.xml", "coverage-*.xml", "coverage-merged.json"],
    )
    integrations["release_candidate_gate"] = _integration(
        order=30,
        display_name="Release Candidate Gate",
        status=_status_from_requirements(["release-candidate-gate.yml" in workflow_set]),
        workflow_file="release-candidate-gate.yml",
        latest_run=_workflow_run(gh_runs, workflows, "release-candidate-gate.yml"),
        gate_role="Top-level release readiness command for Python and frontend gates.",
        remediation="Run the release candidate gate locally, fix the first failing release blocker or frontend gate, then rerun the Release Candidate Gate workflow.",
        evidence=["release-candidate-gate workflow present", "scripts/release_candidate_gate.py referenced"],
    )
    integrations["ruff_lint_format"] = _integration(
        order=40,
        display_name="Ruff Lint / Format",
        status=_status_from_requirements(
            ["lint.yml" in workflow_set, "ruff check" in lint_text, "ruff format" in lint_text]
        ),
        workflow_file="lint.yml",
        latest_run=_workflow_run(gh_runs, workflows, "lint.yml"),
        gate_role="Static Python correctness and formatting gate.",
        remediation="Run the Ruff blocking and format checks locally, fix E/F/import/format findings in `src/` and `tests/`, then rerun the Lint workflow.",
        evidence=["ruff blocking E/F check", "ruff advisory all-rules check", "ruff format check"],
    )
    integrations["sonarcloud"] = _integration(
        order=50,
        display_name="SonarCloud",
        status=_status_from_requirements(["sonarcloud.yml" in workflow_set, "sonar.projectKey=" in sonar_text]),
        workflow_file="sonarcloud.yml",
        latest_run=_workflow_run(gh_runs, workflows, "sonarcloud.yml"),
        gate_role="External code quality and coverage ingestion service.",
        remediation="Verify the `SONAR_TOKEN` secret, Sonar project key, and organization, then inspect the SonarCloud run log or quality gate and rerun after configuration is repaired.",
        evidence=["sonar-project.properties present", "SonarCloud workflow present"],
        artifacts=["coverage.xml"],
        gaps=["SONAR_TOKEN presence cannot be verified from local files."],
    )
    integrations["semgrep_sast"] = _integration(
        order=60,
        display_name="Semgrep SAST",
        status=_status_from_requirements(["security-scan.yml" in workflow_set, "semgrep" in security_text]),
        workflow_file="security-scan.yml",
        latest_run=_workflow_run(gh_runs, workflows, "security-scan.yml"),
        gate_role="Static application security scan.",
        remediation="Open the Semgrep artifact and workflow log, remediate reported SAST or secret findings, and rerun Security Scan.",
        evidence=["Semgrep Python/security/secrets rules configured"],
        artifacts=["semgrep-results"],
    )
    integrations["bandit"] = _integration(
        order=70,
        display_name="Bandit",
        status=_status_from_requirements(
            ["security-scan.yml" in workflow_set, "bandit" in security_text, "[tool.bandit]" in pyproject_text]
        ),
        workflow_file="security-scan.yml",
        latest_run=_workflow_run(gh_runs, workflows, "security-scan.yml"),
        gate_role="Python security linting.",
        remediation="Open the Bandit artifact, review high-confidence findings against `pyproject.toml` skips, fix real issues or document justified suppressions, then rerun Security Scan.",
        evidence=["Bandit configured in pyproject.toml", "Bandit workflow job present"],
        artifacts=["bandit-results"],
    )
    integrations["pip_audit"] = _integration(
        order=80,
        display_name="pip-audit",
        status=_status_from_requirements(["pip-audit" in security_text or "pip-audit" in lint_text]),
        workflow_file="security-scan.yml",
        latest_run=_workflow_run(gh_runs, workflows, "security-scan.yml"),
        gate_role="Python dependency vulnerability scan.",
        remediation="Run `pip-audit` against the project requirements, upgrade vulnerable packages or add an explicit justified advisory disposition, then rerun Security Scan.",
        evidence=["pip-audit configured in security/lint workflows"],
        artifacts=["pip-audit JSON output"],
    )
    integrations["docker_scout"] = _integration(
        order=90,
        display_name="Docker Scout",
        status=_status_from_requirements(["security-scan.yml" in workflow_set, "docker/scout-action" in security_text]),
        workflow_file="security-scan.yml",
        latest_run=_workflow_run(gh_runs, workflows, "security-scan.yml"),
        gate_role="Container CVE gate for high and critical findings.",
        remediation="Verify ACR/Docker credentials, rebuild the scan image, review Docker Scout high/critical CVEs, update the base image or dependencies, then rerun Security Scan.",
        evidence=["Docker Scout action configured", "Dockerfile build scan configured"],
        gaps=["ACR credentials cannot be verified from local files."],
    )
    integrations["accessibility_axe"] = _integration(
        order=100,
        display_name="axe-core Accessibility",
        status=_status_from_requirements(
            [
                "accessibility.yml" in workflow_set,
                (project_root / "applications" / "Agent_Red" / "tests" / "accessibility").is_dir()
                or (project_root / "platform_tests" / "accessibility").is_dir()
                or (project_root / "tests" / "accessibility").is_dir(),
            ]
        ),
        workflow_file="accessibility.yml",
        latest_run=_workflow_run(gh_runs, workflows, "accessibility.yml"),
        gate_role="WCAG 2.1 AA accessibility enforcement.",
        remediation="Open `a11y-results.xml`, reproduce the affected Playwright/axe test locally, fix critical or serious WCAG violations, then rerun Accessibility.",
        evidence=["tests/accessibility present", "Playwright Chromium install configured"],
        artifacts=["a11y-results.xml"],
    )
    integrations["chromatic"] = _integration(
        order=110,
        display_name="Chromatic",
        status=_status_from_requirements(
            ["chromatic.yml" in workflow_set, _package_has_script(widget_package, "chromatic")]
        ),
        workflow_file="chromatic.yml",
        latest_run=_workflow_run(gh_runs, workflows, "chromatic.yml"),
        gate_role="Storybook/widget visual review baseline service.",
        remediation="Verify `CHROMATIC_PROJECT_TOKEN`, inspect the Chromatic build for visual diffs or build errors, accept intentional baselines or fix regressions, then rerun Chromatic.",
        evidence=["widget chromatic script present", "Chromatic workflow present"],
        gaps=["CHROMATIC_PROJECT_TOKEN presence cannot be verified from local files."],
    )
    integrations["visual_regression"] = _integration(
        order=120,
        display_name="Playwright Visual Regression",
        status=_status_from_requirements(
            ["visual-regression.yml" in workflow_set, (project_root / "tests" / "provider_visual").is_dir()]
        ),
        workflow_file="visual-regression.yml",
        latest_run=_workflow_run(gh_runs, workflows, "visual-regression.yml"),
        gate_role="Provider/admin screenshot baseline generation.",
        remediation="Review generated screenshot artifacts, compare unexpected diffs against intended UI behavior, update baselines only after review, then rerun Visual Regression.",
        evidence=["provider visual tests present", "Playwright browser install configured"],
        artifacts=["screenshot-baselines", "visual-results.xml"],
        gaps=["Workflow is dispatch-only until baseline enforcement phase."],
    )
    integrations["docs_quality"] = _integration(
        order=130,
        display_name="Docs Quality",
        status=_status_from_requirements(
            [
                "docs-quality.yml" in workflow_set,
                _package_has_script(docs_package, "build"),
                _package_has_script(docs_package, "audit:coverage"),
            ]
        ),
        workflow_file="docs-quality.yml",
        latest_run=_workflow_run(gh_runs, workflows, "docs-quality.yml"),
        gate_role="Documentation build, lint, link, and coverage checks.",
        remediation="Run the docs build, prose lint, markdown lint, link check, and coverage audit locally; fix broken links or missing coverage before rerunning Docs Quality.",
        evidence=["Docusaurus build", "docs coverage audit", "markdown/link checks configured"],
    )
    integrations["openapi_compatibility"] = _integration(
        order=140,
        display_name="OpenAPI Compatibility",
        status=_status_from_requirements(
            ["openapi-compat" in python_tests_text, "@comparest/cli" in python_tests_text]
        ),
        workflow_file="python-tests.yml",
        latest_run=_workflow_run(gh_runs, workflows, "python-tests.yml"),
        gate_role="API schema compatibility regression check.",
        remediation="Inspect the OpenAPI compatibility job output, confirm whether schema changes are intentional, then either restore compatibility or document/version the breaking API change.",
        evidence=["OpenAPI schema diff job present", "@comparest/cli configured"],
    )
    integrations["dependabot"] = _integration(
        order=150,
        display_name="Dependabot",
        status=_status_from_requirements([bool(dependabot_ecosystems)]),
        gate_role="Dependency freshness automation across package ecosystems.",
        remediation="Inspect failing Dependabot update PR checks, update constraints or lockfiles as needed, and close superseded dependency PRs once a clean update lands.",
        evidence=[f"ecosystems: {', '.join(dependabot_ecosystems) or 'none'}"],
        artifacts=["Dependabot pull requests"],
    )
    integrations["container_builds"] = _integration(
        order=160,
        display_name="Container Build Workflows",
        status=_status_from_requirements(
            [
                "build-api-gateway.yml" in workflow_set,
                "build-slim-gateway.yml" in workflow_set,
                "build-agent-containers.yml" in workflow_set,
                "build-test-host.yml" in workflow_set,
            ]
        ),
        gate_role="Build and publish deployable/test container images.",
        remediation="Inspect the failed container build log, verify ACR credentials and Dockerfile paths, rebuild the target image locally, then rerun the affected build workflow.",
        evidence=["API gateway, slim gateway, agent container, and test-host workflows present"],
        gaps=["ACR credential state cannot be verified from local files."],
    )
    integrations["locust_performance"] = _integration(
        order=170,
        display_name="Locust Performance",
        status=_status_from_requirements(
            [
                (project_root / "tests" / "performance" / "locustfile.py").is_file()
                or (project_root / "applications" / "Agent_Red" / "tests" / "performance" / "locustfile.py").is_file()
                or (project_root / "platform_tests" / "performance" / "locustfile.py").is_file(),
                _dependency_declared(project_root, "locust"),
            ],
            manual=True,
        ),
        gate_role="Manual/local load and latency testing capability.",
        remediation="If performance evidence is required, run the Locust profile against the intended environment and publish the latency/error summary into release evidence.",
        evidence=["tests/performance/locustfile.py present", "locust dependency declared"],
        gaps=["No GitHub Actions workflow currently wires this as an automated gate."],
    )
    integrations["mutation_testing"] = _integration(
        order=180,
        display_name="Mutation Testing",
        status=_status_from_requirements(
            ["[tool.mutmut]" in pyproject_text, _dependency_declared(project_root, "mutmut")], manual=True
        ),
        gate_role="Session-scoped test oracle quality check.",
        remediation="Run mutation testing on changed modules, strengthen assertions for surviving mutants, and record the mutation score in session or release evidence.",
        evidence=["mutmut configured in pyproject.toml", "mutmut dependency declared"],
        gaps=["No GitHub Actions workflow currently publishes mutation score."],
    )
    integrations["contract_testing"] = _integration(
        order=190,
        display_name="Pact / Contract Testing",
        status=_status_from_requirements(
            [_package_has_dependency(widget_package, "@pact-foundation/pact")], manual=True
        ),
        gate_role="Consumer/provider contract testing capability.",
        remediation="Add or run Pact contract verification for widget/provider boundaries and publish pact results or broker status before treating this as an automated gate.",
        evidence=["@pact-foundation/pact dependency present in widget package"],
        gaps=["No Pact workflow or broker/report integration found."],
    )
    integrations["property_testing"] = _integration(
        order=200,
        display_name="Hypothesis Property Tests",
        status=_status_from_requirements(
            [_dependency_declared(project_root, "hypothesis"), "property:" in pyproject_text], manual=True
        ),
        gate_role="Property-based test capability through pytest.",
        remediation="Use Hypothesis for changed logic with broad input space, then run the relevant property-marked pytest target and capture failures as regression tests.",
        evidence=["hypothesis dependency declared", "pytest property marker configured"],
    )
    integrations["schemathesis_api"] = _integration(
        order=210,
        display_name="Schemathesis API Testing",
        status=_status_from_requirements([_dependency_declared(project_root, "schemathesis")], manual=True),
        gate_role="API schema fuzzing capability.",
        remediation="Run Schemathesis against the current OpenAPI schema and target service, triage generated failures, then decide whether to promote it into CI.",
        evidence=["schemathesis dependency declared"],
        gaps=["No GitHub Actions workflow currently wires Schemathesis as an automated gate."],
    )
    integrations["admin_eslint"] = _integration(
        order=220,
        display_name="Admin ESLint",
        status=_status_from_requirements([_package_has_script(admin_package, "lint")], manual=True),
        gate_role="Admin TypeScript/React linting capability.",
        remediation="Run the admin ESLint script locally, fix TypeScript/React/a11y lint findings, and consider wiring it into CI if it gates release readiness.",
        evidence=["admin lint script present"],
        gaps=["No GitHub Actions workflow currently wires admin ESLint as an automated gate."],
    )
    return integrations


def _hook_inventory(project_root: Path) -> dict[str, list[str]]:
    inventory: dict[str, list[str]] = {}
    for label, path in {
        "claude": project_root / ".claude" / "settings.json",
        "codex": project_root / ".codex" / "hooks.json",
    }.items():
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (FileNotFoundError, json.JSONDecodeError):
            inventory[label] = []
            continue
        hooks = []
        for event_name, groups in data.get("hooks", {}).items():
            for group in groups:
                for hook in group.get("hooks", []):
                    command = hook.get("command")
                    if isinstance(command, str):
                        hooks.append(f"{event_name}: {command}")
        inventory[label] = hooks
    return inventory


def _token_metric() -> dict[str, Any]:
    raw = os.environ.get("GTKB_STARTUP_TOKENS_CONSUMED") or os.environ.get("CODEX_STARTUP_TOKENS_CONSUMED")
    if raw:
        try:
            return {
                "tokens_consumed_before_user_input": int(raw),
                "measurement_status": "measured_from_environment",
            }
        except ValueError:
            return {
                "tokens_consumed_before_user_input": None,
                "measurement_status": f"invalid_environment_value:{raw}",
            }
    return {
        "tokens_consumed_before_user_input": None,
        "measurement_status": "not_exposed_by_current_harness",
    }


def _repo_state(project_root: Path) -> dict[str, Any]:
    branch = _command_output(["git", "branch", "--show-current"], project_root)
    sha = _command_output(["git", "rev-parse", "HEAD"], project_root)
    short_sha = _command_output(["git", "rev-parse", "--short", "HEAD"], project_root)
    last_commit = _command_output(["git", "log", "-1", "--format=%cd%n%s", "--date=iso-strict"], project_root)
    return {
        "branch": branch["stdout"] if branch["ok"] else None,
        "sha": sha["stdout"] if sha["ok"] else None,
        "short_sha": short_sha["stdout"] if short_sha["ok"] else None,
        "last_commit": last_commit["stdout"] if last_commit["ok"] else None,
    }


def _dashboard_status_color(status: str) -> str:
    if status in {"red", "yellow", "green"}:
        return status
    if status in {"failing", "blocked", "not_wired", "needs_attention"}:
        return "red"
    if status in {"warning", "manual", "partial", "unknown", "no_recent_run", "watch"}:
        return "yellow"
    return "green"


def _health_pill(label: str, status: str, value: str, tooltip: str) -> dict[str, str]:
    return {"label": label, "status": _dashboard_status_color(status), "value": value, "tooltip": tooltip}


def _shortcut(label: str, target: str, kind: str = "file") -> dict[str, str]:
    return {"label": label, "target": target, "kind": kind}


def _dashboard_intelligence(
    *,
    project_root: Path,
    generated_at: str,
    metrics: dict[str, Any],
    top_actions: list[dict[str, Any]],
    blockers: list[str],
    infrastructure: dict[str, Any],
) -> dict[str, Any]:
    integrations = infrastructure["testing_service_integrations"]
    failing_integrations = [item for item in integrations.values() if item.get("health") == "failing"]
    manual_integrations = [item for item in integrations.values() if item.get("status") == "manual"]
    unknown_integrations = [
        item
        for item in integrations.values()
        if item.get("health") in {"no_recent_run", "live_state_unavailable", "partial_history"}
    ]
    release_blockers = metrics["regression"].get("release_blocker_count") or 0
    bridge_actions = metrics["contention"].get("actionable_count") or 0
    drift_count = metrics["drift"].get("changed_path_count") or 0
    upgrade_posture = infrastructure["gtkb_upgrade_posture"]
    dev_environment_inventory = infrastructure.get("dev_environment_inventory", {})
    scaffold_actions = upgrade_posture.get("upgrade_plan", {}).get("mutating_action_count") or 0
    repo_state = _repo_state(project_root)
    database_path = project_root / "groundtruth.db"
    db_mtime = (
        datetime.fromtimestamp(database_path.stat().st_mtime, UTC).isoformat().replace("+00:00", "Z")
        if database_path.is_file()
        else None
    )
    release_status = "red" if release_blockers else "green"
    ci_status = "red" if failing_integrations else "yellow" if unknown_integrations else "green"
    governance_status = "red" if bridge_actions else "yellow" if scaffold_actions else "green"
    drift_status = "red" if drift_count > 25 else "yellow" if drift_count else "green"
    gtkb_status = (
        "yellow" if scaffold_actions or upgrade_posture.get("unreleased_upstream_changes_available") else "green"
    )
    data_status = "yellow" if unknown_integrations else "green"
    health = [
        _health_pill(
            "Project Health",
            "red" if release_blockers or failing_integrations else drift_status,
            f"{release_blockers + len(failing_integrations)} issues",
            "Release blockers plus failing integrations.",
        ),
        _health_pill(
            "Release Readiness",
            release_status,
            f"{release_blockers} blockers",
            "Open release-readiness blockers from the governed evidence file.",
        ),
        _health_pill(
            "CI / Testing",
            ci_status,
            f"{len(failing_integrations)} failing",
            "Live GitHub Actions health where available.",
        ),
        _health_pill(
            "Security",
            "red"
            if any(
                item.get("display_name") in {"Semgrep SAST", "Bandit", "pip-audit", "Docker Scout"}
                and item.get("health") == "failing"
                for item in integrations.values()
            )
            else "green",
            "scan posture",
            "Security and supply-chain workflow state.",
        ),
        _health_pill(
            "Governance",
            governance_status,
            f"{bridge_actions} bridge items",
            "Actionable bridge entries and GT-KB scaffold drift.",
        ),
        _health_pill(
            "GT-KB",
            gtkb_status,
            str(upgrade_posture.get("status")),
            "Installed GT-KB package/scaffold and upstream posture.",
        ),
        _health_pill(
            "Dev Env Inventory",
            str(dev_environment_inventory.get("health") or "red"),
            str(dev_environment_inventory.get("state") or "missing"),
            "Release-safe harness and development environment inventory status.",
        ),
        _health_pill(
            "Data Freshness",
            data_status,
            "live probes",
            "Whether network-backed and local probes returned current evidence.",
        ),
    ]

    action_center: list[dict[str, Any]] = []
    for item in failing_integrations[:8]:
        action_center.append(
            {
                "severity": "red",
                "owner_lane": "Prime Builder",
                "action": f"Repair {item.get('display_name')}",
                "why": item.get("latest_run_summary") or "Integration is failing.",
                "remediation": item.get("remediation"),
                "shortcut": _shortcut(
                    "Open GitHub Actions",
                    "https://github.com/Remaker-Digital/agent-red-customer-engagement/actions",
                    "web",
                ),
                "source": "Testing Service / Tool Integrations",
            }
        )
    for blocker in blockers[:5]:
        action_center.append(
            {
                "severity": "red",
                "owner_lane": "Owner / Prime Builder",
                "action": blocker,
                "why": "Listed as a release-readiness blocker.",
                "remediation": "Resolve, explicitly defer with owner approval, or supersede with newer governed evidence.",
                "shortcut": _shortcut("Open release readiness", "memory/release-readiness.md"),
                "source": "Release Readiness",
            }
        )
    if scaffold_actions:
        action_center.append(
            {
                "severity": "yellow",
                "owner_lane": "Prime Builder",
                "action": "Review GT-KB scaffold upgrade plan",
                "why": f"{scaffold_actions} mutating dry-run action(s) are available.",
                "remediation": "Run the dry-run command, review the diff, and apply only with owner approval.",
                "shortcut": _shortcut("Copy dry-run command", str(upgrade_posture.get("plan_command")), "command"),
                "source": "GT-KB Upgrade Posture",
            }
        )
    advisory_documents = metrics["contention"].get("raw_advisory_documents", [])
    if advisory_documents:
        action_center.append(
            {
                "severity": "yellow",
                "owner_lane": "Prime Builder",
                "action": "Disposition LO advisory bridge report",
                "why": "Latest ADVISORY bridge thread(s): " + ", ".join(advisory_documents[:5]),
                "remediation": "Respond through one permitted path: proposal, rebuttal, defer, or candidate-artifact.",
                "shortcut": _shortcut("Open bridge index", "bridge/INDEX.md"),
                "source": "Bridge ADVISORY",
            }
        )
    if dev_environment_inventory.get("health") != "green":
        action_center.append(
            {
                "severity": str(dev_environment_inventory.get("health") or "red"),
                "owner_lane": "Prime Builder",
                "action": "Refresh GT-KB dev environment inventory",
                "why": _dev_inventory_compact_text(dev_environment_inventory),
                "remediation": "Run the collector and then rerun the release-gate inventory check.",
                "shortcut": _shortcut(
                    "Copy collector command",
                    str(dev_environment_inventory.get("latest_verification_command")),
                    "command",
                ),
                "source": "Dev Environment Inventory",
            }
        )
    for item in top_actions[:3]:
        action_center.append(
            {
                "severity": "yellow",
                "owner_lane": "Prime Builder",
                "action": f"{item['id']}: {item['title']}",
                "why": "Standing backlog top priority.",
                "remediation": "Execute or disposition through the governed backlog/bridge process.",
                "shortcut": _shortcut("Query MemBase backlog", "gt backlog list", "command"),
                "source": "Standing Backlog",
            }
        )

    risks = []
    if release_blockers:
        risks.append(
            {
                "severity": "red",
                "risk": "Production GO is blocked",
                "evidence": f"{release_blockers} release blocker(s) remain.",
                "impact": "Stakeholder-ready release posture cannot be claimed.",
                "remediation": "Close, defer, or supersede every blocker with governed evidence.",
                "owner": "Owner / Prime Builder",
            }
        )
    if failing_integrations:
        risks.append(
            {
                "severity": "red",
                "risk": "Automated quality gates are failing",
                "evidence": f"{len(failing_integrations)} failing testing/service integration(s).",
                "impact": "Release evidence is incomplete or stale.",
                "remediation": "Work through the failing integration remediation list.",
                "owner": "Prime Builder",
            }
        )
    if scaffold_actions:
        risks.append(
            {
                "severity": "yellow",
                "risk": "GT-KB scaffold drift",
                "evidence": f"{scaffold_actions} mutating upgrade action(s) are planned.",
                "impact": "Project governance runtime may lag the installed GT-KB package.",
                "remediation": "Review `gt project upgrade --dry-run` and apply only after owner approval.",
                "owner": "Prime Builder / Owner",
            }
        )
    if drift_count:
        risks.append(
            {
                "severity": drift_status,
                "risk": "Working tree drift",
                "evidence": f"{drift_count} GT-KB changed path(s).",
                "impact": "Dashboard evidence may include uncommitted local state.",
                "remediation": "Review drift and stage/commit or explicitly defer it.",
                "owner": "Prime Builder",
            }
        )
    if dev_environment_inventory.get("health") != "green":
        risks.append(
            {
                "severity": str(dev_environment_inventory.get("health") or "red"),
                "risk": "Development environment inventory is not release-ready",
                "evidence": _dev_inventory_compact_text(dev_environment_inventory),
                "impact": "Release/package evidence cannot prove the current harness and tool baseline.",
                "remediation": "Regenerate and validate the public inventory before packaging.",
                "owner": "Prime Builder",
            }
        )

    return {
        "health": health,
        "action_center": action_center[:12],
        "risk_register": risks,
        "release_readiness": {
            "status": release_status,
            "blocker_count": release_blockers,
            "blockers": blockers,
            "release_gate_script": metrics["regression"].get("release_gate_script"),
            "shortcut": _shortcut("Open release-readiness evidence", "memory/release-readiness.md"),
        },
        "quality_rollup": {
            "total": len(integrations),
            "failing": len(failing_integrations),
            "manual": len(manual_integrations),
            "unknown": len(unknown_integrations),
            "ready_or_passing": sum(
                1
                for item in integrations.values()
                if item.get("health") in {"passing", "configured"} or item.get("status") == "ready"
            ),
            # Per WI-3409: surface the work-subject-aware queried repo so the
            # rollup label can reflect the actual GitHub repository whose CI
            # this rollup summarizes (avoids the GT-KB-session-but-Agent-Red-data
            # coupling defect).
            "queried_repo": integrations.get("github", {}).get("queried_repo"),
            "queried_work_subject": integrations.get("github", {}).get("queried_work_subject"),
        },
        "data_freshness": {
            "generated_at": generated_at,
            "groundtruth_db_modified_at": db_mtime,
            "repo_branch": repo_state.get("branch"),
            "repo_sha": repo_state.get("sha"),
            "repo_short_sha": repo_state.get("short_sha"),
            "last_commit": repo_state.get("last_commit"),
            "scope_version": DASHBOARD_SCOPE_VERSION,
            "sources": [
                "groundtruth.db",
                "memory/release-readiness.md",
                "bridge/INDEX.md",
                ".github/workflows",
                "docs/release/dev-environment-inventory.json",
                "GitHub Actions via gh when authenticated",
                "GT-KB package and upstream repository probes",
            ],
        },
        "shortcuts": [
            _shortcut("Open dashboard data", "docs/gtkb-dashboard/dashboard-data.json"),
            _shortcut("Open release readiness", "memory/release-readiness.md"),
            _shortcut("Query MemBase backlog", "gt backlog list", "command"),
            _shortcut("Open bridge index", "bridge/INDEX.md"),
            _shortcut("Open dev environment inventory", "docs/release/dev-environment-inventory.md"),
            _shortcut(
                "Open GitHub Actions", "https://github.com/Remaker-Digital/agent-red-customer-engagement/actions", "web"
            ),
            _shortcut("Open GT-KB upstream", "https://github.com/Remaker-Digital/groundtruth-kb", "web"),
        ],
    }


def discover_role_profile(
    project_root: Path,
    *,
    harness_name: str | None = None,
    harness_id: str | None = None,
    role_record_path: Path | None = None,
) -> str:
    """Read the durable role assignment from the single harness role map."""

    role_profile, _document, _path = role_for_harness(
        project_root,
        harness_id=harness_id,
        harness_name=harness_name,
        assignment_path=role_record_path,
        ensure_prime_on_startup=True,
    )
    return role_profile if role_profile in ROLE_PROFILES else "prime-builder"


def _role_profile_or_discovered(
    project_root: Path,
    role_profile: str | None = None,
    *,
    harness_name: str | None = None,
    harness_id: str | None = None,
    role_record_path: Path | None = None,
) -> str:
    if role_profile:
        return role_profile if role_profile in ROLE_PROFILES else "prime-builder"
    return discover_role_profile(
        project_root,
        harness_name=harness_name,
        harness_id=harness_id,
        role_record_path=role_record_path,
    )


def build_startup_model(
    project_root: Path,
    role_profile: str | None = None,
    *,
    harness_name: str | None = None,
    harness_id: str | None = None,
    role_record_path: Path | None = None,
    fast_hook: bool = False,
) -> dict[str, Any]:
    """Collect the complete startup disclosure model without writing files."""

    resolved_role_profile = _role_profile_or_discovered(
        project_root,
        role_profile,
        harness_name=harness_name,
        harness_id=harness_id,
        role_record_path=role_record_path,
    )
    generated_at = _now_iso()
    database = _database_metrics(project_root)
    backlog, top_actions = _backlog_metrics(project_root)
    blockers = _release_blockers(project_root)
    skill_files = _discover_skill_files(project_root)
    rule_files = sorted((project_root / ".claude" / "rules").glob("*.md"))
    hook_files = sorted((project_root / ".claude" / "hooks").glob("*.py"))
    test_files = sorted((project_root / "tests").rglob("test_*.py"))
    plugins = _plugin_inventory()
    dev_environment_inventory = _dev_environment_inventory_status(project_root)
    harness_parity = _harness_parity_status(
        project_root,
        harness_name=harness_name,
        role_profile=resolved_role_profile,
    )
    agent_red_test_files = [
        path for path in test_files if _path_matches(path.relative_to(project_root).as_posix(), AGENT_RED_PATH_PREFIXES)
    ]
    metrics = {
        "backlog": backlog,
        "membase": database.get("membase", {}),
        "deliberation_archive": database.get("deliberation_archive", {}),
        "tests": {
            "pytest_file_count": len(agent_red_test_files),
            "raw_pytest_file_count": len(test_files),
            "test_records": database.get("membase", {}).get("test_records"),
            "test_procedure_records": database.get("membase", {}).get("test_procedure_records"),
            "scope_confidence": "gtkb_current_heuristic",
        },
        "templates": {
            "skill_template_count": len(skill_files),
            "rule_template_count": len(rule_files),
            "hook_template_count": len(hook_files),
            "scope": "implementation_infrastructure",
        },
        "specifications": database.get("specifications", {}),
        "drift": _git_drift(project_root),
        "regression": {
            "release_blocker_count": len(blockers),
            "blockers": blockers,
            "release_gate_script": "scripts/release_candidate_gate.py",
            "startup_self_initialization_test": "tests/scripts/test_session_self_initialization.py",
        },
        "contention": _bridge_metrics(project_root),
        "tokens": _token_metric(),
        "work_subject": _collect_work_subject(project_root),
        "dev_environment_inventory": dev_environment_inventory,
        "harness_parity": harness_parity,
    }
    infrastructure = {
        "instrumentation": "GT-KB",
        "scope_note": "GT-KB infrastructure is the primary dashboard scope; adopter-application KPIs are explicit secondary context.",
        "skill_template_count": len(skill_files),
        "rule_template_count": len(rule_files),
        "hook_template_count": len(hook_files),
        "hook_registrations": _hook_inventory(project_root),
        "dashboard_history_path": "memory/gtkb-dashboard-history.json",
        "dev_environment_inventory": dev_environment_inventory,
        "harness_parity": harness_parity,
        "gtkb_upgrade_posture": _gtkb_upgrade_posture(project_root, fast_hook=fast_hook),
        "testing_service_integrations": _testing_service_integrations(project_root, plugins, fast_hook=fast_hook),
        "dashboard_reachability": _dashboard_reachability_probes(),
    }
    infrastructure["delivery_timeline"] = _delivery_timeline(project_root, infrastructure, fast_hook=fast_hook)
    dashboard_intelligence = _dashboard_intelligence(
        project_root=project_root,
        generated_at=generated_at,
        metrics=metrics,
        top_actions=top_actions,
        blockers=blockers,
        infrastructure=infrastructure,
    )

    return {
        "generated_at": generated_at,
        "role": _role_metadata(
            resolved_role_profile,
            project_root,
            harness_name=harness_name,
            harness_id=harness_id,
            role_record_path=role_record_path,
        ),
        "role_profile": resolved_role_profile,
        "dashboard_opening": _dashboard_opening_state(),
        "governance_stance": [
            "Strict GOV enforcement where mechanically available",
            "Formal artifact approval required for DA, GOV, SPEC, PB, ADR, and DCL mutations",
            "Standing backlog is the governed cross-session work authority",
            "Strategic self-improvement directive: Prime Builder and Loyal Opposition capture noticed fix-worthy issues and useful workflow enhancements as review/consideration backlog items in MemBase, not MEMORY.md; backlog capture is not implementation approval; implementation-approved backlog items require AskUserQuestion evidence; executing a consideration item means presenting insight/options and obtaining AskUserQuestion approval before implementation proposal work",
            "GT-KB adoption and release-readiness evidence remain release-gate visible",
            "Harness hook limitations require parity checks and explicit fallback disclosure",
        ],
        "skills": {
            "count": len(skill_files),
            "items": [_skill_name(path) for path in skill_files[:80]],
            "source": (
                "project .claude/skills plus opt-in local harness skill directories"
                if _user_extension_discovery_opt_in()
                else "project .claude/skills (root-contained default per project-root-boundary)"
            ),
        },
        "plugins": {
            "items": plugins,
            "source": (
                "opt-in local harness plugin cache via GTKB_DISCOVER_USER_EXTENSIONS=1"
                if _user_extension_discovery_opt_in()
                else "default root-contained (no plugin cache scan; opt-in via GTKB_DISCOVER_USER_EXTENSIONS=1)"
            ),
        },
        "user_extension_discovery": (
            "opt_in_active" if _user_extension_discovery_opt_in() else "default_root_contained"
        ),
        "directives": {
            "rule_files": [path.name for path in rule_files],
            "hook_files": [path.name for path in hook_files],
            "hook_registrations": _hook_inventory(project_root),
        },
        "workstream_focus": startup_focus_snapshot(project_root),
        "session_overlay": _safe_overlay_status(project_root),
        "dashboard_requirements": {
            "spec_id": "SPEC-PROJECT-DASHBOARD-KPI-LINK-001",
            "scope_version": DASHBOARD_SCOPE_VERSION,
            "scope_note": DASHBOARD_SCOPE_NOTE,
            "subsystems": [
                "backlog",
                "MemBase",
                "Deliberation Archive",
                "tests",
                "templates",
                "specifications",
                "drift",
                "regression",
                "contention",
                "dev environment inventory",
                "tokens consumed before user input",
            ],
        },
        "metrics": metrics,
        "infrastructure": infrastructure,
        "dashboard_intelligence": dashboard_intelligence,
        "top_priority_actions": top_actions,
        "token_reduction_options": [
            "Use the dashboard link before loading large artifacts into context.",
            "Read indices and summaries first; open full artifacts only when needed.",
            "Load only the specific skill body required for the current turn.",
            "Use cached startup snapshots for stable KPI instead of re-scanning everything.",
            "Propose explicit governance relaxation only when the audit trail can preserve the tradeoff.",
        ],
        "current_work_subject": metrics["work_subject"].get("current_subject"),
    }


def _collect_work_subject(project_root: Path) -> dict[str, Any]:
    """Collect the active work-subject for the dashboard.

    Distinguishes "no canonical state file" from "explicitly set to application"
    by checking the canonical file's existence rather than relying on
    ``load_state()`` which normalizes a missing file to the default subject.
    Slice 2.1 of GTKB-DASHBOARD-002 (Implementation Condition #2).
    """
    canonical_path = project_root / _WORK_SUBJECT_CANONICAL_PATH
    present = canonical_path.is_file()
    if not present:
        return {
            "current_subject": None,
            "source_path": str(_WORK_SUBJECT_CANONICAL_PATH).replace("\\", "/"),
            "present": False,
        }
    try:
        state = _workstream_load_state(project_root)
    except Exception:
        return {
            "current_subject": None,
            "source_path": str(_WORK_SUBJECT_CANONICAL_PATH).replace("\\", "/"),
            "present": True,
        }
    return {
        "current_subject": state.get("current_subject"),
        "source_path": str(_WORK_SUBJECT_CANONICAL_PATH).replace("\\", "/"),
        "present": True,
    }


def _snapshot_from_model(model: dict[str, Any]) -> dict[str, Any]:
    metrics = model["metrics"]
    return {
        "scope_version": DASHBOARD_SCOPE_VERSION,
        "scope_confidence": "gtkb_current_heuristic",
        "scope_source": "current dashboard model",
        "generated_at": model["generated_at"],
        "backlog_active_items": metrics["backlog"].get("active_item_count"),
        "membase_open_work_items": metrics["membase"].get("open_work_items"),
        "deliberation_archive_current_total": metrics["deliberation_archive"].get("current_total"),
        "pytest_file_count": metrics["tests"].get("pytest_file_count"),
        "skill_template_count": metrics["templates"].get("skill_template_count"),
        "specification_current_total": metrics["specifications"].get("current_total"),
        "drift_changed_path_count": metrics["drift"].get("changed_path_count"),
        "regression_release_blocker_count": metrics["regression"].get("release_blocker_count"),
        "contention_actionable_bridge_count": metrics["contention"].get("actionable_count"),
        "tokens_consumed_before_user_input": metrics["tokens"].get("tokens_consumed_before_user_input"),
        "token_measurement_status": metrics["tokens"].get("measurement_status"),
        "current_work_subject": (metrics.get("work_subject") or {}).get("current_subject"),
    }


def _load_history(history_path: Path) -> list[dict[str, Any]]:
    try:
        data = json.loads(history_path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return []
    if not isinstance(data, list):
        return []
    return [row for row in data if isinstance(row, dict) and row.get("scope_version") == DASHBOARD_SCOPE_VERSION]


def _write_history(
    history_path: Path,
    snapshot: dict[str, Any],
    *,
    seed_history: list[dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    history = seed_history or []
    snapshot_day = str(snapshot.get("generated_at", ""))[:10]
    existing = [
        row
        for row in _load_history(history_path)
        if not (
            str(row.get("generated_at", ""))[:10] >= snapshot_day and row.get("scope_confidence") == "gtkb_inferred"
        )
    ]
    seen = {row.get("generated_at") for row in history}
    history.extend(row for row in existing if row.get("generated_at") not in seen)
    history = sorted(history, key=lambda row: str(row.get("generated_at") or ""))
    if not history or history[-1] != snapshot:
        history.append(snapshot)
    deduped: dict[str, dict[str, Any]] = {}
    for row in history:
        generated_at = str(row.get("generated_at") or "")
        if generated_at:
            deduped[generated_at] = row
    history = [deduped[key] for key in sorted(deduped)]
    history = history[-MAX_HISTORY:]
    _atomic_write_text(history_path, json.dumps(history, indent=2, sort_keys=True) + "\n")
    return history


def _version_rows(connection: sqlite3.Connection, table: str) -> list[dict[str, Any]]:
    return [
        dict(row)
        for row in connection.execute(
            f"SELECT * FROM {table} WHERE changed_at IS NOT NULL AND changed_at != '' ORDER BY changed_at, id, version"
        )
    ]


def _historical_agent_red_backfill(project_root: Path) -> list[dict[str, Any]]:
    db_path = project_root / "groundtruth.db"
    if not db_path.is_file():
        return []

    connection = sqlite3.connect(db_path)
    connection.row_factory = sqlite3.Row
    try:
        table_rows = {
            "specifications": _version_rows(connection, "specifications"),
            "work_items": _version_rows(connection, "work_items"),
            "tests": _version_rows(connection, "tests"),
            "deliberations": _version_rows(connection, "deliberations"),
        }
    finally:
        connection.close()

    dates = sorted(
        {
            str(row.get("changed_at", ""))[:10]
            for rows in table_rows.values()
            for row in rows
            if str(row.get("changed_at", ""))[:10]
        }
    )
    states: dict[str, dict[str, dict[str, Any]]] = {name: {} for name in table_rows}
    indexes = {name: 0 for name in table_rows}
    snapshots: list[dict[str, Any]] = []

    for day in dates:
        for table, rows in table_rows.items():
            index = indexes[table]
            while index < len(rows) and str(rows[index].get("changed_at", ""))[:10] <= day:
                states[table][str(rows[index].get("id"))] = rows[index]
                index += 1
            indexes[table] = index

        specs = [row for row in states["specifications"].values() if _is_agent_red_scope(row)]
        work_items = [row for row in states["work_items"].values() if _is_agent_red_scope(row)]
        tests = [row for row in states["tests"].values() if _is_agent_red_scope(row)]
        deliberations = [row for row in states["deliberations"].values() if _is_agent_red_scope(row)]
        open_work_items = [
            row for row in work_items if str(row.get("resolution_status") or "") in NON_TERMINAL_WORK_ITEM_STATUSES
        ]
        pytest_files = {
            _normalize_path(str(row.get("test_file") or "")) for row in tests if str(row.get("test_file") or "").strip()
        }

        snapshots.append(
            {
                "scope_version": DASHBOARD_SCOPE_VERSION,
                "scope_confidence": "gtkb_inferred",
                "scope_source": "groundtruth.db version history by changed_at",
                "generated_at": f"{day}T23:59:59Z",
                "backlog_active_items": None,
                "membase_open_work_items": len(open_work_items),
                "deliberation_archive_current_total": len(deliberations),
                "pytest_file_count": len(pytest_files),
                "skill_template_count": None,
                "specification_current_total": len(specs),
                "drift_changed_path_count": None,
                "regression_release_blocker_count": None,
                "contention_actionable_bridge_count": None,
                "tokens_consumed_before_user_input": None,
                "token_measurement_status": "not_exposed_by_current_harness",
            }
        )
    return snapshots


def _markdown_list(items: list[str], *, limit: int = 20) -> str:
    visible = items[:limit]
    lines = [f"- {item}" for item in visible]
    if len(items) > limit:
        lines.append(f"- ... {len(items) - limit} more")
    return "\n".join(lines) if lines else "- none detected"


def _first_text(items: list[Any], default: str) -> str:
    return str(items[0]) if items else default


def _sentence_fragment(value: Any, default: str) -> str:
    text = str(value or default).strip()
    return text.rstrip(".")


def _protocol_review_queue_count(contention: dict[str, Any]) -> int:
    """Count latest NEW/REVISED bridge entries without dashboard scope filtering."""

    if "raw_review_queue_count" in contention:
        return int(contention.get("raw_review_queue_count") or 0)
    raw_status_counts = contention.get("raw_latest_status_counts", {})
    return sum(int(raw_status_counts.get(status, 0) or 0) for status in REVIEW_QUEUE_BRIDGE_STATUSES)


def _protocol_prime_response_queue_count(contention: dict[str, Any]) -> int:
    """Count latest GO/NO-GO bridge entries without dashboard scope filtering."""

    if "raw_prime_response_queue_count" in contention:
        return int(contention.get("raw_prime_response_queue_count") or 0)
    raw_status_counts = contention.get("raw_latest_status_counts", {})
    return sum(int(raw_status_counts.get(status, 0) or 0) for status in PRIME_RESPONSE_BRIDGE_STATUSES)


def _session_focus_options(model: dict[str, Any]) -> list[dict[str, str]]:
    metrics = model["metrics"]
    intelligence = model.get("dashboard_intelligence", {})
    startup_pruning = model.get("startup_pruning", {})
    token_reduction_options = model.get("token_reduction_options", [])
    integrations = model["infrastructure"]["testing_service_integrations"]
    failing_integrations = [item for item in integrations.values() if item.get("health") == "failing"]
    unknown_integrations = [
        item
        for item in integrations.values()
        if item.get("health") in {"no_recent_run", "live_state_unavailable", "partial_history"}
    ]
    blockers = metrics["regression"].get("blockers") or []
    risks = intelligence.get("risk_register", [])
    action_center = intelligence.get("action_center", [])
    top_actions = model["top_priority_actions"]
    release_blocker_count = metrics["regression"].get("release_blocker_count") or 0
    drift_count = metrics["drift"].get("changed_path_count") or 0
    raw_status_counts = metrics["contention"].get("raw_latest_status_counts", {})
    continuation_go_count = int(raw_status_counts.get("GO", 0) or 0)
    continuation_no_go_count = int(raw_status_counts.get("NO-GO", 0) or 0)
    continuation_response_count = continuation_go_count + continuation_no_go_count
    prime_response_count = _protocol_prime_response_queue_count(metrics["contention"])
    first_blocker = _sentence_fragment(
        _first_text(blockers, "run the release gate and confirm no blocker evidence is stale"),
        "run the release gate and confirm no blocker evidence is stale",
    )
    first_integration = (
        failing_integrations[0] if failing_integrations else unknown_integrations[0] if unknown_integrations else {}
    )
    first_integration_name = _sentence_fragment(
        first_integration.get("display_name"),
        "the highest-risk testing integration",
    )
    first_integration_remediation = _sentence_fragment(
        first_integration.get("remediation"),
        "refresh live evidence and confirm the integration still gates the release path",
    )
    first_risk = risks[0] if risks else {}
    first_action = action_center[0] if action_center else {}
    first_backlog = top_actions[0] if top_actions else {}
    startup_candidate_count = int(startup_pruning.get("candidate_count", 0) or 0)
    backlog_label = (
        f"{first_backlog.get('id')}: {first_backlog.get('title')}"
        if first_backlog
        else "the first active standing-backlog item"
    )
    token_option_summary = "; ".join(item.rstrip(".") for item in token_reduction_options) or (
        "prefer dashboard and index-first reads before loading full artifacts"
    )
    action_summary = (
        "; ".join(
            f"{item.get('id')}: {_sentence_fragment(item.get('title'), 'standing backlog priority')}"
            for item in top_actions[:3]
        )
        or "No active standing-backlog items found"
    )
    file_bridge_summary = (
        f"file bridge scan shows {prime_response_count} latest GO/NO-GO bridge response"
        f"{'s' if prime_response_count != 1 else ''}"
    )

    return [
        {
            "label": "Optimize Startup Token Consumption",
            "reason": (
                f"{startup_candidate_count} startup reduction candidate(s) are currently visible."
                if startup_candidate_count
                else "Startup context can be reduced by preferring dashboard and index-first reads."
            ),
            "prompt": (
                "Focus this session on reducing startup token consumption. Review the startup-loaded artifacts, "
                "prefer dashboard and index-first reads, and trim default startup context to the minimum evidence needed. "
                f"Use this reduction set: {token_option_summary}."
            ),
        },
        {
            "label": "Top Priority Actions",
            "reason": (
                f"The standing backlog already identifies the visible highest-priority governed actions for this session, and the "
                f"{file_bridge_summary}."
            ),
            "prompt": (
                "Focus this session on the established top priority actions. Current priorities: "
                f"{action_summary}. Start with {backlog_label}; explain the current evidence, immediate next command, "
                "and expected verification."
            ),
        },
        {
            "label": "Resolve Release Blockers",
            "reason": f"{release_blocker_count} release blocker(s) are visible in the dashboard.",
            "prompt": (
                "Focus this session on clearing release blockers. Start with "
                f"{first_blocker}. Verify the result with scripts/release_candidate_gate.py and update governed evidence."
            ),
        },
        {
            "label": "Repair Testing/Tool Integrations",
            "reason": f"{len(failing_integrations)} failing and {len(unknown_integrations)} unknown integration(s) are visible.",
            "prompt": (
                "Focus this session on restoring testing service/tool integration health. Start with "
                f"{first_integration_name}: {first_integration_remediation}. Preserve GT-KB as infrastructure evidence."
            ),
        },
        {
            "label": "Remediate Known Risks",
            "reason": f"{len(risks)} active risk(s) are summarized from release, integration, GT-KB, and drift signals.",
            "prompt": (
                "Focus this session on the dashboard risk register. Start with "
                f"{_sentence_fragment(first_risk.get('risk'), 'the highest-severity current risk')}; recommended action: "
                f"{_sentence_fragment(first_risk.get('remediation'), 'turn the risk into a concrete owner-approved action and verify the evidence')}."
            ),
        },
        {
            "label": "Clear Stage/Test Release Path",
            "reason": "Release readiness, regression, integration, and staging evidence should converge before stakeholder release.",
            "prompt": (
                "Prepare for release by clearing the path to stage and test. Confirm release blockers, required checks, "
                "tool integrations, staging readiness, and evidence freshness before recommending a release decision."
            ),
        },
        {
            "label": "Clean For Internal Review",
            "reason": f"{drift_count} changed path(s) are visible in dashboard drift.",
            "prompt": (
                "Clean and tidy for internal review. Inventory changed paths, separate unrelated work, run focused checks, "
                "and prepare a concise review handoff without modifying formal artifacts unless explicitly approved."
            ),
        },
        {
            "label": "Pick From Standing Backlog",
            "reason": "Standing backlog remains the governed cross-session work authority.",
            "prompt": (
                "Choose work from the standing backlog. Start with "
                f"{backlog_label}; restate the governing evidence, required approvals, implementation scope, and verification plan."
            ),
        },
        {
            "label": "Commit and push to GitHub",
            "reason": "Local changes can be packaged into an evidence-backed GitHub update when the working tree is ready.",
            "prompt": (
                "Prepare a scoped commit and push it to GitHub. Inventory changed paths, separate unrelated work, run focused "
                "verification, commit only the intended scope, push the branch, and report the resulting GitHub evidence."
            ),
        },
        {
            "label": "Merge to main, build and push to the staging environment",
            "reason": "A reviewed GitHub branch can advance into the staging release lane after required checks and approvals are green.",
            "prompt": (
                "Merge the reviewed branch to main, build the release artifact, and push it to the staging environment. Confirm "
                "required GitHub checks, release-gate evidence, branch provenance, build output, and staging deployment status."
            ),
        },
        {
            "label": "Execute end-to-end tests in the staging environment",
            "reason": "Staging must prove the candidate through live end-to-end coverage before production promotion.",
            "prompt": (
                "Execute the staging end-to-end test plan. Verify environment health, run the governed E2E suites against staging, "
                "capture failures with evidence, and update release-readiness records with the staging result."
            ),
        },
        {
            "label": "Push staged-and-tested build to production, then smoke test",
            "reason": "Production promotion is only available after the staged build has passed required gates and owner approval is recorded.",
            "prompt": (
                "Promote the staged-and-tested build to production, then run production smoke tests. Confirm explicit production "
                "approval, artifact provenance, deployment status, smoke-test evidence, rollback readiness, and release records."
            ),
        },
        {
            "label": "Continue Last Session",
            "reason": (
                f"The action center and {continuation_response_count} latest GO/NO-GO bridge response"
                f"{'s' if continuation_response_count != 1 else ''} define the current-session continuation scope."
            ),
            "prompt": (
                "Continue from the last session using the dashboard action center and any latest GO/NO-GO bridge "
                "responses, including responses produced by a prior Loyal Opposition session. Start by inventorying "
                f"the latest GO/NO-GO bridge entries, then continue with {first_action.get('action', backlog_label)}; "
                "explain current evidence, next command, and expected verification."
            ),
        },
    ]


def _render_session_focus_options(options: list[dict[str, str]], model: dict[str, Any] | None = None) -> str:
    recommendations = _rank_session_focus_options(model, options) if model else []
    return _render_ranked_session_focus_options(options, recommendations)


def _first_sentence(text: str, fallback: str) -> str:
    clean = " ".join(str(text or "").split()).strip()
    if not clean:
        return fallback
    for delimiter in (". ", "? ", "! "):
        if delimiter in clean:
            head = clean.split(delimiter, 1)[0].strip()
            return f"{head}{delimiter.strip()}"
    return clean if clean.endswith((".", "?", "!")) else f"{clean}."


def _focus_option_by_label(options: list[dict[str, str]]) -> dict[str, dict[str, str]]:
    return {str(option.get("label") or ""): option for option in options}


def _add_focus_signal(
    scores: dict[str, int],
    evidence: dict[str, tuple[int, str]],
    options_by_label: dict[str, dict[str, str]],
    label: str,
    points: int,
    reason: str,
) -> None:
    if label not in options_by_label or points <= 0:
        return
    scores[label] = scores.get(label, 0) + points
    current = evidence.get(label)
    if current is None or points > current[0]:
        evidence[label] = (points, reason)


def _rank_session_focus_options(model: dict[str, Any], options: list[dict[str, str]]) -> list[dict[str, str]]:
    options_by_label = _focus_option_by_label(options)
    option_order = {option["label"]: index for index, option in enumerate(options)}
    metrics = model.get("metrics", {})
    contention = metrics.get("contention", {})
    raw_status_counts = contention.get("raw_latest_status_counts", {})
    infrastructure = model.get("infrastructure", {})
    integrations = infrastructure.get("testing_service_integrations", {})
    failing_integrations = [item for item in integrations.values() if item.get("health") == "failing"]
    unknown_integrations = [
        item
        for item in integrations.values()
        if item.get("health") in {"no_recent_run", "live_state_unavailable", "partial_history"}
    ]
    release_blocker_count = int(metrics.get("regression", {}).get("release_blocker_count") or 0)
    blockers = metrics.get("regression", {}).get("blockers") or []
    drift_count = int(metrics.get("drift", {}).get("changed_path_count") or 0)
    startup_candidate_count = int(model.get("startup_pruning", {}).get("candidate_count", 0) or 0)
    prime_response_count = _protocol_prime_response_queue_count(contention)
    advisory_count = int(raw_status_counts.get("ADVISORY", 0) or 0)
    top_actions = model.get("top_priority_actions") or []
    action_center = model.get("dashboard_intelligence", {}).get("action_center") or []
    project_rollup = metrics.get("membase", {}).get("project_state_rollup") or {}
    active_project_count = int(project_rollup.get("active_project_count") or 0)
    non_terminal_work_items = int(project_rollup.get("non_terminal_work_items") or 0)
    dev_inventory = infrastructure.get("dev_environment_inventory", {})
    harness_parity = infrastructure.get("harness_parity", {})

    scores: dict[str, int] = {}
    evidence: dict[str, tuple[int, str]] = {}

    first_blocker = _sentence_fragment(
        _first_text(blockers, "release-readiness blocker evidence needs disposition"),
        "release-readiness blocker evidence needs disposition",
    )
    if release_blocker_count:
        _add_focus_signal(
            scores,
            evidence,
            options_by_label,
            "Resolve Release Blockers",
            120 + (release_blocker_count * 10),
            f"Release readiness reports {release_blocker_count} blocker(s); first signal: {first_blocker}.",
        )
        _add_focus_signal(
            scores,
            evidence,
            options_by_label,
            "Clear Stage/Test Release Path",
            35 + (release_blocker_count * 5),
            "Release blocker evidence is present; stage/test readiness should converge after blocker disposition.",
        )

    integration_points = (len(failing_integrations) * 45) + (len(unknown_integrations) * 18)
    if integration_points:
        integration_name = _sentence_fragment(
            (failing_integrations[0] if failing_integrations else unknown_integrations[0]).get("display_name"),
            "the highest-risk testing integration",
        )
        _add_focus_signal(
            scores,
            evidence,
            options_by_label,
            "Repair Testing/Tool Integrations",
            95 + integration_points,
            (
                f"Testing/tool state reports {len(failing_integrations)} failing and "
                f"{len(unknown_integrations)} unknown integration(s); first signal: {integration_name}."
            ),
        )

    if prime_response_count:
        _add_focus_signal(
            scores,
            evidence,
            options_by_label,
            "Continue Last Session",
            110 + (prime_response_count * 8),
            (
                f"Live bridge metrics show {prime_response_count} latest GO/NO-GO response"
                f"{'s' if prime_response_count != 1 else ''} for Prime continuation."
            ),
        )
        _add_focus_signal(
            scores,
            evidence,
            options_by_label,
            "Top Priority Actions",
            35 + (prime_response_count * 3),
            "Prime-actionable bridge responses should be considered alongside standing priorities.",
        )

    if advisory_count:
        _add_focus_signal(
            scores,
            evidence,
            options_by_label,
            "Remediate Known Risks",
            70 + (advisory_count * 10),
            f"Bridge state includes {advisory_count} ADVISORY thread(s) requiring Prime disposition.",
        )

    if top_actions:
        first_action = top_actions[0]
        _add_focus_signal(
            scores,
            evidence,
            options_by_label,
            "Top Priority Actions",
            80 + (len(top_actions) * 5),
            f"Standing backlog top signal: {first_action.get('id')}: {first_action.get('title')}.",
        )
        _add_focus_signal(
            scores,
            evidence,
            options_by_label,
            "Pick From Standing Backlog",
            45 + (len(top_actions) * 4),
            "Standing backlog remains the governed cross-session work authority.",
        )

    if active_project_count or non_terminal_work_items:
        _add_focus_signal(
            scores,
            evidence,
            options_by_label,
            "Pick From Standing Backlog",
            30 + active_project_count + min(non_terminal_work_items, 25),
            (
                f"MemBase project rollup shows {active_project_count} active project group(s) "
                f"and {non_terminal_work_items} non-terminal work item(s)."
            ),
        )

    if drift_count:
        _add_focus_signal(
            scores,
            evidence,
            options_by_label,
            "Clean For Internal Review",
            35 + min(drift_count, 60),
            f"Dashboard drift reports {drift_count} changed path(s).",
        )

    if startup_candidate_count:
        _add_focus_signal(
            scores,
            evidence,
            options_by_label,
            "Optimize Startup Token Consumption",
            40 + min(startup_candidate_count * 8, 60),
            f"Startup pruning found {startup_candidate_count} token-reduction candidate(s).",
        )

    if dev_inventory.get("health") not in {None, "", "green"}:
        _add_focus_signal(
            scores,
            evidence,
            options_by_label,
            "Repair Testing/Tool Integrations",
            30,
            f"Dev environment inventory health is {dev_inventory.get('health')}; release-safe tooling needs attention.",
        )
    if harness_parity.get("health") not in {None, "", "green"}:
        _add_focus_signal(
            scores,
            evidence,
            options_by_label,
            "Remediate Known Risks",
            25,
            f"Harness parity health is {harness_parity.get('health')}; startup/hook drift risk is visible.",
        )

    if action_center:
        _add_focus_signal(
            scores,
            evidence,
            options_by_label,
            "Remediate Known Risks",
            20 + min(len(action_center) * 3, 30),
            f"Dashboard action center has {len(action_center)} current action signal(s).",
        )

    fallback_labels = [
        "Top Priority Actions",
        "Continue Last Session",
        "Pick From Standing Backlog",
        "Optimize Startup Token Consumption",
    ]
    ranked_labels = sorted(
        options_by_label,
        key=lambda label: (-(scores.get(label, 0)), option_order.get(label, 1_000_000)),
    )
    selected: list[str] = []
    for label in ranked_labels:
        if scores.get(label, 0) > 0:
            selected.append(label)
        if len(selected) == 3:
            break
    for label in fallback_labels:
        if label in options_by_label and label not in selected:
            selected.append(label)
        if len(selected) == 3:
            break
    for label in options_by_label:
        if label not in selected:
            selected.append(label)
        if len(selected) == 3:
            break

    recommendations: list[dict[str, str]] = []
    for label in selected[:3]:
        option = options_by_label[label]
        recommendations.append(
            {
                "label": label,
                "reason": evidence.get(label, (0, option["reason"]))[1],
                "expected_work": _first_sentence(option.get("prompt", ""), option["reason"]),
                "score": str(scores.get(label, 0)),
            }
        )
    return recommendations


def _render_ranked_session_focus_options(options: list[dict[str, str]], recommendations: list[dict[str, str]]) -> str:
    if not recommendations:
        recommendations = [
            {
                "label": option["label"],
                "reason": option["reason"],
                "expected_work": _first_sentence(option.get("prompt", ""), option["reason"]),
            }
            for option in options[:3]
        ]
    blocks: list[str] = []
    for marker, option in zip(("A", "B", "C"), recommendations, strict=False):
        blocks.extend(
            [
                f"{marker}. **{option['label']}**",
                f"   Evidence: {option['reason']}",
                f"   Expected work: {option['expected_work']}",
                "",
            ]
        )
    blocks.extend(
        [
            "D. **Full Focus List**",
            "   Choose any label below; the active role will expand it using the stored prompt details.",
        ]
    )
    for option in options:
        blocks.append(f"   - {option['label']}")
    return "\n".join(blocks).rstrip()


def _compact_top_action_summary(actions: list[dict[str, Any]]) -> str:
    if not actions:
        return "none visible"
    return "; ".join(f"{item.get('id')}: {item.get('title')}" for item in actions[:3])


def _render_top_priority_actions_section(model: dict[str, Any]) -> str:
    """Render the canonical top-3 priorities surface for the open disclosure.

    Per SPEC-ENVELOPE-DISCLOSURE-UI-001 the open disclosure must keep a
    top-3 priorities surface; the actions are already filtered + ordered
    deterministically by `_backlog_metrics`. Universal: shown in both Prime
    and Loyal Opposition open disclosures.
    """

    actions = model.get("top_priority_actions") or []
    lines = ["### Top Priority Actions", ""]
    if not actions:
        lines.append("- No implementation-authorized work items currently surface as top-3 priorities.")
        return "\n".join(lines)
    for index, action in enumerate(actions, start=1):
        title = action.get("title") or "(no title)"
        identifier = action.get("id") or "(no id)"
        priority = str(action.get("priority") or "none").strip() or "none"
        lines.append(f"{index}. **{identifier}**: {title} (priority: {priority})")
    return "\n".join(lines)


def _render_session_startup_briefing(model: dict[str, Any]) -> str:
    role = model.get("role", {})
    metrics = model.get("metrics", {})
    infrastructure = model.get("infrastructure", {})
    intelligence = model.get("dashboard_intelligence", {})
    workstream = model.get("workstream_focus") or {}
    dashboard_opening = model.get("dashboard_opening", {})
    release = intelligence.get("release_readiness", {})
    quality = intelligence.get("quality_rollup", {})
    dev_inventory = infrastructure.get("dev_environment_inventory", {})
    harness_parity = infrastructure.get("harness_parity", {})
    upgrade_posture = infrastructure.get("gtkb_upgrade_posture", {})
    dashboard_open_requested = "enabled" if dashboard_opening.get("startup_open_requested") else "disabled"
    dashboard_open_mode = dashboard_opening.get("mode") or DASHBOARD_OPEN_MODE_HARNESS
    active_subject = _active_subject_label(model)

    return "\n".join(
        [
            "### Configuration",
            f"- Work subject: {active_subject}; startup focus: {workstream.get('current_label', 'unknown')}.",
            f"- Role assignment: {role.get('assumed_role')} from {role.get('role_mapping_source')}.",
            (
                f"- Harness: id {role.get('harness_id', 'unidentified')} from "
                f"{role.get('harness_identity_source', 'unidentified')}; topology "
                f"`{workstream.get('topology_mode', 'unknown')}`."
            ),
            (
                f"- Dashboard opening: {dashboard_open_requested}; mode `{dashboard_open_mode}`; "
                f"package {upgrade_posture.get('package_version', 'unknown')}."
            ),
            "",
            "### Operating State",
            f"- Release blockers: {release.get('blocker_count', metrics.get('regression', {}).get('release_blocker_count'))}.",
            (
                # Per WI-3409: append queried_repo as parenthetical SUFFIX so the
                # pre-existing label-format contract "Testing/tools: ..." is
                # preserved (downstream consumers parse on the colon position).
                # The queried_repo is also exposed structurally via
                # quality_rollup["queried_repo"] for non-string consumers.
                f"- Testing/tools: "
                f"{quality.get('failing', 'unknown')} failing, "
                f"{quality.get('manual', 'unknown')} manual, "
                f"{quality.get('ready_or_passing', 'unknown')} ready/passing "
                f"(queried repo: {quality.get('queried_repo') or 'unknown'})."
            ),
            f"- Dev environment inventory: {_dev_inventory_compact_text(dev_inventory)}",
            f"- Harness parity: {_harness_parity_compact_text(harness_parity)}",
            f"- Data freshness: {intelligence.get('data_freshness', {}).get('generated_at', model.get('generated_at'))}.",
        ]
    )


def _is_loyal_opposition_model(model: dict[str, Any]) -> bool:
    return model.get("role", {}).get("assumed_role") == "Loyal Opposition"


def _render_dashboard_reachability_lines(model: dict[str, Any]) -> list[str]:
    probes = model.get("infrastructure", {}).get("dashboard_reachability") or []
    if not probes:
        return []
    lines: list[str] = []
    unavailable: list[str] = []
    for probe in probes:
        source = str(probe.get("source") or "dashboard probe")
        status = str(probe.get("status") or "unknown")
        detail = str(probe.get("detail") or "")
        status_detail = status
        if probe.get("http_status") is not None:
            status_detail = f"{status} (HTTP {probe['http_status']})"
        lines.append(f"- Dashboard reachability: {source}: {status_detail}; target: {detail}")
        if status != "queried":
            unavailable.append(source)
    if unavailable:
        lines.append(
            "- Dashboard recovery hint: Grafana is optional for startup; start or restart the local Grafana service "
            "and re-open the dashboard link when reachability is unavailable."
        )
    return lines


def _render_loyal_opposition_startup_task(model: dict[str, Any]) -> str:
    return "\n".join(
        [
            "- Startup mode: Loyal Opposition review and verification.",
            "- Default session purpose: process Prime Builder reviews and verifications on the file bridge.",
            "- Session-focus menu: not presented in Loyal Opposition mode; numbered focus choices are Prime Builder startup controls.",
            "- Bridge/dispatch distinction: the file bridge is the durable role handoff and review mechanism; the cross-harness event-driven trigger is the dispatch automation registered as PostToolUse and Stop hooks (retired smart poller and OS poller archived per Slice 4).",
            "- Bridge startup rule: check the file bridge in both Prime Builder and Loyal Opposition startup.",
            "- Live bridge authority: current bridge state must be determined only from a fresh read of live `bridge/INDEX.md`; this generated report is not authoritative after generation.",
            "- Mandatory direct-read rule: before reporting the live bridge scan count, read `bridge/INDEX.md` directly; do not derive bridge state from startup reports, dashboard JSON, cached documents, copied excerpts, summary counts, or hook-generated summaries.",
            "- Project-state startup rule: include a compact current-state report for every active MemBase project group using `current_work_items.project_name`; distinguish bridge queue state, git drift, release blockers, and Prime-actionable bridge responses.",
            "- Startup execution rule: execute live bridge verification before using this section in owner-facing chat; do not display this checklist as a substitute for performing the verification.",
            "- Bridge dispatch startup rule: rely on the cross-harness event-driven trigger registered as PostToolUse and Stop hooks; do not restore the retired smart poller or OS poller. Manual bridge/INDEX.md scans remain available as fallback when separate-harness or asynchronous monitoring is needed.",
            f"- Bridge operation instructions: {BRIDGE_OPERATION_INSTRUCTIONS_TEXT}.",
            "- First task: verify that the Prime Builder / Loyal Opposition file bridge is functioning.",
            _render_file_bridge_scan(model),
            "- If the live bridge verification succeeds, report the live scan result and auto-process actionable NEW/REVISED bridge entries oldest-to-newest by default (per ADR-LOYAL-OPPOSITION-STARTUP-AUTO-PROCESS-DEFAULT-001).",
            "- Advisory mode opt-in: when the session was opened with `init gtkb advisory`, report the scan and ask Mike whether to switch to auto-process; do not write verdict files in advisory mode.",
            "- If the bridge is not functioning, diagnose and repair the bridge before ordinary review work.",
            "- Bridge authority: Loyal Opposition has permanent owner permission to diagnose and repair bridge function/use and downstream bridge-dependent artifacts needed to sustain the bridge.",
        ]
    )


def _render_fresh_session_input_semantics(model: dict[str, Any]) -> str:
    lines = [
        "- The harness's UserPromptSubmit hook routes the first owner message through the init-keyword matcher (per ADR-SESSION-START-INIT-KEYWORD-CONTRACT-001 and DCL-SESSION-START-INIT-KEYWORD-MATCHING-001): on match (e.g., `init gtkb`, `init gtkb advisory`), render the harness-specific startup disclosure and wait for the next owner message before tool use; on no-match, process the prompt as normal task content.",
    ]
    if _is_loyal_opposition_model(model):
        lines.append(
            "- After presenting this startup disclosure, execute the harness-only Loyal Opposition startup action before ordinary task work."
        )
    else:
        lines.append(
            "- After presenting this startup disclosure and the session-focus choices, wait for Mike's next message before choosing or mapping session work."
        )
    return "\n".join(lines)


def _render_startup_pruning(model: dict[str, Any]) -> str:
    pruning = model.get("startup_pruning")
    if not pruning:
        return "Startup pruning scan not run for this command."

    largest = pruning.get("largest_files", [])[:5]
    candidates = pruning.get("candidates", [])[:8]
    lines = [
        f"- Startup corpus measured: {pruning.get('file_count')} files, {pruning.get('total_bytes')} bytes.",
        f"- Completed pruning actions: {pruning.get('completed_count')}",
        f"- Candidate reductions: {pruning.get('candidate_count')}",
    ]
    if largest:
        lines.append("- Largest startup inputs:")
        for item in largest:
            lines.append(f"  - `{item.get('path')}`: {item.get('bytes')} bytes / {item.get('lines')} lines")
    if candidates:
        lines.append("- Pruning queue:")
        for item in candidates:
            lines.append(f"  - `{item.get('target')}`: {item.get('action')}")
    return "\n".join(lines)


def _active_subject_label(model: dict[str, Any]) -> str:
    """Return a human subject label for readiness/test/drift section headers."""

    focus = model.get("workstream_focus") or {}
    current = str(focus.get("current_focus") or "").strip()
    if current == "gtkb_infrastructure":
        return "GT-KB"
    return "Application"


def _dev_inventory_compact_text(status: dict[str, Any]) -> str:
    state = str(status.get("state") or "unknown")
    generated_at = status.get("generated_at") or "unknown"
    redaction = status.get("redaction_status") or "unknown"
    if not status.get("present"):
        return f"{state}; generate with `{status.get('latest_verification_command')}`"
    return f"{state}; generated {generated_at}; redaction {redaction}"


def _render_current_project_state(model: dict[str, Any]) -> str:
    metrics = model["metrics"]
    intelligence = model.get("dashboard_intelligence", {})
    release = intelligence.get("release_readiness", {})
    quality = intelligence.get("quality_rollup", {})
    upgrade_posture = model.get("infrastructure", {}).get("gtkb_upgrade_posture", {})
    dev_inventory = model.get("infrastructure", {}).get("dev_environment_inventory", {})
    harness_parity = model.get("infrastructure", {}).get("harness_parity", {})
    subject_label = _active_subject_label(model)

    # Â§A hard-rejection: a combined application + GT-KB green claim may not be
    # emitted without an explicit dual-scope declaration at the readiness/report
    # layer. This is defense-in-depth against future code paths that might
    # assemble dual-subject readiness outputs without the guard.
    dual_scope_declared = bool(intelligence.get("dual_scope_declared"))
    subject_readiness = intelligence.get("subject_readiness") or {}
    app_green = bool(subject_readiness.get("application_green"))
    gtkb_green = bool(subject_readiness.get("gtkb_green"))
    if app_green or gtkb_green:
        assert_readiness_subject_scope(
            application_green=app_green,
            gtkb_green=gtkb_green,
            dual_scope_declared=dual_scope_declared,
            context=f"{subject_label} release readiness",
        )

    # Render-time canonical derivation per gtkb-startup-payload-canonical-state-drift -006 F1.
    # Always pass through canonical helpers (including for missing or malformed role-map state)
    # so fail-closed semantics (multi_harness / shared) survive every failure mode. The earlier
    # implementation's literal single_harness/shared defaults were the bug F1 of -006 cited.
    role_slot = "shared"
    topology_mode = "multi_harness"
    role_map: dict[str, Any] = {}
    try:
        from groundtruth_kb.mode_switch.derive import (
            role_slot_from_active_harness,
            topology_from_role_map,
        )

        # WI-3342 IP-4: role map resolves from the harness registry projection
        # via the IP-3 foundational loader (load_role_assignments now reads the
        # projection). load_role_assignments is fail-soft — a missing or
        # malformed projection yields an empty document, preserving the
        # canonical-helper fail-closed path below.
        role_map = load_role_assignments(_PROJECT_ROOT_FOR_IMPORTS)
        topology_mode = topology_from_role_map(role_map)
        active_harness_id = model.get("role", {}).get("harness_id")
        role_slot = role_slot_from_active_harness(role_map, active_harness_id)
    except Exception:  # noqa: BLE001 - ImportError or other unexpected; defaults already set
        pass
    return "\n".join(
        [
            f"- {subject_label} release blockers: {release.get('blocker_count', metrics['regression'].get('release_blocker_count'))}",
            f"- {subject_label} active backlog items: {metrics['backlog'].get('active_item_count')}",
            f"- {subject_label} open MemBase work items: {metrics['membase'].get('open_work_items')}",
            f"- {subject_label} dashboard-scoped bridge/contention entries, non-authoritative for queue state: {metrics['contention'].get('actionable_count')}",
            f"- {subject_label} drift changed paths: {metrics['drift'].get('changed_path_count')}",
            (
                # Per WI-3409: append queried_repo as parenthetical SUFFIX so the
                # pre-existing label-format contract "Testing/tool rollup: ..." is
                # preserved (downstream consumers + the test
                # platform_tests/scripts/test_session_self_initialization.py
                # test_dashboard_and_report_are_written_with_time_series_kpi
                # parse on the colon position).
                f"- {subject_label} Testing/tool rollup: "
                f"{quality.get('failing', 'unknown')} failing, "
                f"{quality.get('manual', 'unknown')} manual, "
                f"{quality.get('ready_or_passing', 'unknown')} ready/passing "
                f"(queried repo: {quality.get('queried_repo') or 'unknown'})"
            ),
            f"- Bridge role slot: `{role_slot}` (prime-builder, loyal-opposition, or shared)",
            f"- Harness topology: `{topology_mode}` (single_harness or multi_harness)",
            (
                "- GT-KB infrastructure posture: "
                f"package {upgrade_posture.get('package_version', 'unknown')}; "
                f"dry-run upgrade plan available: {upgrade_posture.get('upgrade_plan', {}).get('available', False)}"
            ),
            f"- GT-KB dev environment inventory: {_dev_inventory_compact_text(dev_inventory)}",
            f"- Harness parity: {_harness_parity_compact_text(harness_parity)}",
        ]
    )


def _compact_counts(counts: dict[str, Any]) -> str:
    if not counts:
        return "none"
    return ", ".join(f"{key}={value}" for key, value in counts.items())


def _format_project_top_item(project: dict[str, Any]) -> str:
    title = _sentence_fragment(project.get("top_title"), "top item")
    priority = str(project.get("top_priority") or "").strip()
    priority_text = f", {priority}" if priority else ""
    order = project.get("top_order")
    order_text = f", order {order}" if order not in (None, "") else ""
    return f"`{project.get('top_id')}` - {title} [{project.get('top_status')}{priority_text}{order_text}]"


def _render_project_state_rollup(model: dict[str, Any]) -> str:
    rollup = model.get("metrics", {}).get("membase", {}).get("project_state_rollup")
    if not rollup:
        return "- Project-state rollup unavailable; MemBase project grouping was not loaded."
    if not rollup.get("available", True):
        return f"- Project-state rollup unavailable: {rollup.get('error', 'unknown error')}"

    projects = list(rollup.get("projects") or [])
    lines = [
        f"- Source: {rollup.get('source')} grouped by `{rollup.get('project_group_field')}`.",
        (
            f"- Current work items: {rollup.get('total_current_work_items')}; "
            f"non-terminal: {rollup.get('non_terminal_work_items')}; "
            f"active projects: {rollup.get('active_project_count')}; "
            f"ungrouped non-terminal: {rollup.get('ungrouped_non_terminal_count')}."
        ),
        f"- Status counts: {_compact_counts(rollup.get('status_counts') or {})}.",
    ]
    if not projects:
        lines.append("- No active project groups found in MemBase.")
        return "\n".join(lines)

    lines.append("- Active project states:")
    for project in projects:
        lines.append(
            "  - "
            f"`{project.get('project')}`: {project.get('non_terminal_count')} non-terminal "
            f"({_compact_counts(project.get('status_counts') or {})}); "
            f"top: {_format_project_top_item(project)}."
        )
    return "\n".join(lines)


def _safe_overlay_status(project_root: Path) -> dict[str, Any]:
    """Return session overlay snapshot, never raising into the startup model."""

    try:
        return _gtkb_overlay.current_overlay_status(project_root)
    except Exception as exc:  # pragma: no cover - defensive against startup-time errors
        return {
            "authoritative": False,
            "overlay_root": _gtkb_overlay.OVERLAY_ROOT_RELATIVE.as_posix(),
            "overlay_present": False,
            "overlay_id": None,
            "expired": False,
            "entries_stale": 0,
            "entries_total": 0,
            "is_stale": False,
            "notes": [f"overlay status unavailable; treating as absent: {exc}"],
        }


def _render_session_overlay_status(status: dict[str, Any]) -> str:
    lines = [
        f"- Overlay root: `{status.get('overlay_root', _gtkb_overlay.OVERLAY_ROOT_RELATIVE.as_posix())}` (ignored by git, non-authoritative by construction).",
        "- Overlays are copy-only context; canonical state lives in the KB, MemBase, Deliberation Archive, and source files.",
    ]
    if not status.get("overlay_present"):
        lines.append("- Current overlay: none active; startup context read directly from live files.")
    else:
        lines.append(
            "- Current overlay: "
            f"`{status.get('overlay_id')}` "
            f"(authoritative={status.get('authoritative', False)}, "
            f"expired={status.get('expired', False)}, "
            f"stale_entries={status.get('entries_stale', 0)}/{status.get('entries_total', 0)})."
        )
    notes = status.get("notes") or []
    for note in notes:
        lines.append(f"- {note}")
    return "\n".join(lines)


def _render_file_bridge_scan(model: dict[str, Any]) -> str:
    contention = model["metrics"]["contention"]
    actionable_review_count = _protocol_review_queue_count(contention)
    if actionable_review_count:
        return (
            f"- Generated-time file bridge scan, non-authoritative after report generation: "
            f"{actionable_review_count} latest NEW/REVISED entr"
            f"{'y' if actionable_review_count == 1 else 'ies'} identified."
        )
    return "- Generated-time file bridge scan, non-authoritative after report generation: 0 latest NEW/REVISED entries identified."


def _render_wrapup_trigger_commands() -> str:
    examples = ", ".join(f"`{command}`" for command in WRAPUP_TRIGGER_COMMANDS)
    return "\n".join(
        [
            "- Wrap-up trigger: use one of the documented commands as a standalone message.",
            f"- Accepted wrap-up commands: {examples}.",
            "- Optional leading or trailing `please` and final punctuation are accepted.",
        ]
    )


def _markdown_file_link(path: Path) -> str:
    """Return a visible absolute file path with a desktop-openable link target."""
    resolved = path.resolve()
    return f"[{resolved}](<{resolved.as_posix()}>)"


def _markdown_url_link(url: str) -> str:
    return f"[{url}]({url})"


# _atomic_write_text relocated to scripts/_wrap_io.py per
# bridge/gtkb-wrapup-enhancements-slice1-005.md Â§2.4 (REVISED-2 binding,
# GO at -006). Re-imported here as a module-level alias so the four
# existing call sites at lines ~2744, ~4886, ~4891, ~4892 continue to
# resolve to the same function object without behavior change.
#
# sys.path conditional insert per bridge/gtkb-startup-evidence-restoration-002.md
# GO (S313): the test loader (importlib.util.spec_from_file_location) does
# not add scripts/ to sys.path, so the bare `from _wrap_io` import fails
# with ModuleNotFoundError. Conditional-insert avoids duplicating the path
# on repeated test loads. Reuses top-level `sys` and `Path` imports.
_scripts_dir = str(Path(__file__).resolve().parent)
if _scripts_dir not in sys.path:
    sys.path.insert(0, _scripts_dir)
from _wrap_io import _atomic_write_text  # noqa: E402,F401,I001


# Pending owner-decisions surfacing
# ---------------------------------
# The .claude/hooks/owner-decision-tracker.py hook is the canonical
# writer of memory/pending-owner-decisions.md. This renderer reads the
# same file and surfaces any `## Pending` entries in the startup
# disclosure so owner decisions don't drown in inline message flow.
# Authority: bridge/gtkb-gov-owner-decision-surfacing-slice1-003.md Â§2.6;
# Codex GO at -004 with condition "keep visibility through this script,
# do not reintroduce a separate SessionStart hook as primary surface."

_PENDING_DECISIONS_REL_PATH = "memory/pending-owner-decisions.md"


def _load_pending_owner_decisions(project_root: Path) -> list[dict[str, str]]:
    """Read pending-owner-decisions.md `## Pending` section.

    Returns a list of decision dicts (id, question, options, thread_ref,
    asked_at, asked_in_session). Empty list when the file is missing,
    malformed, or `## Pending` is empty. All exceptions are caught and
    logged to stderr to preserve startup-disclosure rendering -- a
    broken pending-decisions surfacing must never break the rest of the
    startup report.
    """
    path = project_root / _PENDING_DECISIONS_REL_PATH
    if not path.exists():
        return []
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:  # pragma: no cover - defensive
        sys.stderr.write(f"_load_pending_owner_decisions read failed: {exc}\n")
        return []

    try:
        return _parse_pending_block(text)
    except Exception as exc:  # pragma: no cover - defensive
        sys.stderr.write(f"_load_pending_owner_decisions parse failed: {exc}\n")
        return []


def _parse_pending_block(text: str) -> list[dict[str, str]]:
    """Parse the `## Pending` section into a list of decision dicts.

    Format matches the YAML-frontmatter list shape that
    .claude/hooks/owner-decision-tracker.py writes:

      - id: DECISION-NNNN
        asked_at: 2026-04-25T07:30:00Z
        question: "<text>"
        options:
          - "<label-1>"
          - "<label-2>"
        ...
    """
    entries: list[dict[str, str | list[str]]] = []
    in_pending = False
    current: dict[str, str | list[str]] | None = None
    in_options = False

    for raw_line in text.splitlines():
        stripped = raw_line.strip()
        if stripped.startswith("## "):
            heading = stripped[3:].strip().lower()
            if heading == "pending":
                in_pending = True
                continue
            if in_pending:
                # Hit the next section heading; flush and stop.
                if current is not None:
                    entries.append(current)
                    current = None
                break
        if not in_pending:
            continue
        if stripped.startswith("- id: "):
            if current is not None:
                entries.append(current)
            current = {"id": stripped[len("- id: ") :].strip(), "options": []}
            in_options = False
            continue
        if current is None:
            continue
        if raw_line.startswith("  options:"):
            in_options = True
            continue
        if in_options and raw_line.startswith("    - "):
            opt = _unquote_pending_value(raw_line[len("    - ") :])
            opts_field = current.get("options")
            if isinstance(opts_field, list):
                opts_field.append(opt)
            continue
        if raw_line.startswith("  ") and ":" in stripped:
            in_options = False
            key, _, val = stripped.partition(":")
            current[key.strip()] = _unquote_pending_value(val.strip())

    if current is not None:
        entries.append(current)

    # Coerce option lists to list[str] for downstream consumers.
    out: list[dict[str, str]] = []
    for entry in entries:
        flat: dict[str, str] = {}
        for k, v in entry.items():
            if isinstance(v, list):
                flat[k] = "; ".join(v)
            else:
                flat[k] = v
        out.append(flat)
    return out


def _unquote_pending_value(value: str) -> str:
    if value.startswith('"') and value.endswith('"') and len(value) >= 2:
        return value[1:-1].replace('\\"', '"').replace("\\\\", "\\")
    return value


def _render_smart_poller_section(project_root: Path, role: dict[str, Any]) -> list[str]:
    """Retired stub — smart-poller startup-orient surface removed in Slice 4.

    The smart-poller mechanism was retired on 2026-05-09 in favor of the
    cross-harness event-driven trigger (see Slice 4 of
    ``bridge/gtkb-bridge-poller-event-driven-replacement-slice-4-smart-poller-retirement-001-*``).
    The cross-harness trigger does not surface a startup-orient section
    — actionable bridge work is dispatched via PostToolUse + Stop hooks
    rather than read from notification artifacts at session start.

    The function is preserved as a stub returning ``[]`` so that the
    call site in ``render_report`` continues to compose cleanly without
    a structural edit. Call sites and tests that previously exercised
    this surface have been updated to reflect the empty result.
    """
    return []


def _render_diagnostic_section(health: Any) -> list[str]:
    """Render a single-section diagnostic for an unhealthy smart poller.

    Per ``bridge/smart-poller-orient-verification-2026-04-29-005.md`` (carry
    forward of ``-003 §3-§4``) + GO at ``-006``: when the doctor reports
    ``warning`` or ``fail``, the diagnostic supersedes notification rendering
    because notifications cannot be trusted when the poller itself is
    unhealthy. The doctor message is reused verbatim — it already contains
    specific remediation hints (file paths, command strings).
    """
    icon = "⚠️" if health.status == "warning" else "❌"
    return [
        f"### Smart-poller diagnostic — {health.status.upper()}",
        "",
        f"{icon} {health.message}",
        "",
    ]


def _render_pending_decisions_block(decisions: list[dict[str, str]]) -> str:
    """Format the pending-decisions list for the startup disclosure.

    Matches the visual style of other startup sections (markdown bullets
    with bold IDs). The decision id and suffix metadata render on the bullet
    line; the question renders as a column-0 blockquote so a verbatim relay
    of this section is classified as documentation rather than a fresh
    owner-decision-ask by the owner-decision-tracker Stop hook (WI-3332). An
    optional indented option list follows.
    """
    if not decisions:
        return ""
    lines: list[str] = [
        f"{len(decisions)} owner decision(s) await a response. "
        "Address one by quoting its DECISION-NNNN ID, type "
        "`resolve DECISION-NNNN: <answer>` to record an answer, "
        "`defer all` to acknowledge without resolving, or "
        "`clear pending` to dismiss intentionally.",
        "",
    ]
    for entry in decisions:
        decision_id = entry.get("id", "")
        question = entry.get("question", "")
        opts = entry.get("options", "")
        thread_ref = entry.get("thread_ref", "")
        asked_at = entry.get("asked_at", "")
        suffix_parts: list[str] = []
        if asked_at:
            suffix_parts.append(f"asked {asked_at}")
        if thread_ref:
            suffix_parts.append(f"thread: `{thread_ref}`")
        suffix = f" ({'; '.join(suffix_parts)})" if suffix_parts else ""
        # WI-3332: render the stored question as a column-0 blockquote line so
        # a verbatim relay of this section is classified as documentation, not
        # a fresh owner-decision-ask, by the owner-decision-tracker Stop hook's
        # structural-context check (a line starting with "> " is treated as a
        # relay). The decision id, question, and options stay fully visible.
        lines.append(f"- **{decision_id}**{suffix}")
        if question:
            lines.append(f"> {question}")
        if opts:
            lines.append(f"  - Options: {opts}")
    return "\n".join(lines)


def _load_startup_glossary(project_root: Path) -> dict[str, Any]:
    try:
        from scripts.startup_glossary_load import load_glossary_for_startup
    except Exception as exc:  # noqa: BLE001 - startup must render fail-soft.
        return {
            "status": "error",
            "source": ".claude/rules/canonical-terminology.md",
            "terms": {},
            "term_order": [],
            "error": f"loader import failed: {exc}",
        }
    try:
        return load_glossary_for_startup(project_root)
    except Exception as exc:  # noqa: BLE001 - startup must render fail-soft.
        return {
            "status": "error",
            "source": ".claude/rules/canonical-terminology.md",
            "terms": {},
            "term_order": [],
            "error": str(exc),
        }


def _truncate_startup_glossary_definition(value: str, limit: int = 180) -> str:
    normalized = " ".join(value.split())
    if len(normalized) <= limit:
        return normalized
    return f"{normalized[: limit - 3].rstrip()}..."


def _render_startup_glossary_section(project_root: Path, *, max_terms: int = 8) -> str:
    glossary = _load_startup_glossary(project_root)
    source = str(glossary.get("source") or ".claude/rules/canonical-terminology.md")
    status = str(glossary.get("status") or "missing")
    terms = glossary.get("terms") if isinstance(glossary.get("terms"), dict) else {}
    term_order = glossary.get("term_order") if isinstance(glossary.get("term_order"), list) else []

    lines = ["### Glossary", ""]
    if status != "loaded" or not terms:
        detail = f" ({glossary.get('error')})" if glossary.get("error") else ""
        lines.append(
            f"- Canonical terminology source unavailable: `{source}`; startup continues without term summaries{detail}."
        )
        return "\n".join(lines)

    lines.append(f"- Source: `{source}`")
    for name in [str(item) for item in term_order[:max_terms]]:
        entry = terms.get(name)
        if not isinstance(entry, dict):
            continue
        definition = _truncate_startup_glossary_definition(str(entry.get("definition") or ""))
        if not definition:
            continue
        lines.append(f"- **{name}**: {definition}")
    omitted = max(0, len(term_order) - max_terms)
    if omitted:
        lines.append(f"- ... {omitted} additional canonical term(s) omitted from startup summary.")
    return "\n".join(lines)


def render_report(model: dict[str, Any], dashboard_link: str, project_root: Path) -> str:
    """Render the startup report markdown.

    Per bridge/generator-hardening-001-003.md Â§4.5 + Codex -004 GO:
    project_root is now a required parameter (was: model lacked
    project_root, so the function read PROJECT_ROOT global directly).
    """
    role = model["role"]
    metrics = model["metrics"]
    dashboard_opening = model.get("dashboard_opening", {})
    dashboard_open_requested = "enabled" if dashboard_opening.get("startup_open_requested") else "disabled"
    dashboard_open_mode = dashboard_opening.get("mode") or DASHBOARD_OPEN_MODE_HARNESS
    token_count = metrics["tokens"]["tokens_consumed_before_user_input"]
    token_count_text = "unavailable" if token_count is None else str(token_count)
    pending_decisions = _load_pending_owner_decisions(project_root)
    if pending_decisions:
        pending_decisions_section = [
            "### Pending Owner Decisions",
            "",
            _render_pending_decisions_block(pending_decisions),
            "",
        ]
    else:
        pending_decisions_section = []

    if _is_loyal_opposition_model(model):
        startup_task_section = []
        project_state_rollup_section = [
            "### Project State Rollup",
            "",
            _render_project_state_rollup(model),
            "",
        ]
    else:
        startup_task_section = [
            "## Session Startup",
            "",
            _render_session_startup_briefing(model),
            "",
        ]
        project_state_rollup_section = []

    return "\n".join(
        [
            "# GroundTruth-KB Fresh Session Startup",
            "",
            f"Generated: {model['generated_at']}",
            f"Dashboard: GroundTruth-KB Project Dashboard: {dashboard_link}",
            "",
            "## Startup Disclosure",
            "",
            "### Role And Governance Stance",
            "",
            f"- Role being assumed: {role['assumed_role']}",
            f"- Role assignment: {role['role_assignment']}",
            f"- Bridge: {role['bridge']}",
            f"- Bridge dispatch: {role['bridge_dispatch']}",
            f"- Bridge operation instructions: {role['bridge_operation_instructions']}",
            f"- Role mapping source: {role['role_mapping_source']}",
            f"- Harness self-identification: {role.get('harness_id', 'unidentified')}",
            f"- Harness identity source: {role.get('harness_identity_source', 'unidentified')}",
            "",
            _markdown_list(model["governance_stance"]),
            "",
            "### Live Project Dashboard",
            "",
            f"- Dashboard: GroundTruth-KB Project Dashboard: {dashboard_link}",
            *_render_dashboard_reachability_lines(model),
            f"- Browser opening: use the harness-controlled browser for live dashboard inspection; startup open request: {dashboard_open_requested}; current mode: `{dashboard_open_mode}`. Startup hooks must not launch the operating system default browser unless explicitly configured with `dashboard_open_mode: system_default_browser`.",
            "- KPI coverage: GT-KB backlog, MemBase work items, Deliberation Archive records, tests, specifications, drift, regression, contention, and tokens consumed at session start before user input.",
            f"- Dashboard scope: {model['dashboard_requirements']['scope_note']}",
            f"- Token measurement status: {metrics['tokens']['measurement_status']}",
            f"- Tokens consumed before user input: {token_count_text}",
            "",
            "### Current Project State",
            "",
            _render_current_project_state(model),
            "",
            *project_state_rollup_section,
            "### Active Work Subject",
            "",
            render_active_work_subject(
                project_root,
                snapshot=model.get("workstream_focus"),
                overlay_status=model.get("session_overlay") or {},
                include_counterpart=True,
                include_overlay_note=False,
                include_operational_instructions=False,
            ),
            "",
            *_render_smart_poller_section(project_root, role),
            *pending_decisions_section,
            _render_top_priority_actions_section(model),
            "",
            *startup_task_section,
        ]
    )


def render_wrapup_notice(model: dict[str, Any], dashboard_link: str) -> str:
    metrics = model["metrics"]
    actions = model["top_priority_actions"]
    action_lines = [f"{index}. {item['id']}: {item['title']}" for index, item in enumerate(actions, start=1)] or [
        "1. No active standing-backlog items found."
    ]

    return "\n".join(
        [
            "# GroundTruth-KB Proactive Session Wrap-Up",
            "",
            f"Generated: {model['generated_at']}",
            "",
            "## Governance Principle",
            "",
            "- The user should not have to explicitly instruct GT-KB to perform session wrap-up procedures.",
            "- Each session should actively inform and engage the user across project priorities.",
            "- Suggested actions should simplify user input by presenting clear next choices.",
            "",
            "## Wrap-Up Procedure Entry Point",
            "",
            "- Procedure skill: `.claude/skills/kb-session-wrap/SKILL.md`",
            f"- Dashboard: GroundTruth-KB Project Dashboard: {dashboard_link}",
            "- Safe automatic action: this report is generated without mutating MemBase, git history, or external infrastructure.",
            "- Mutating wrap-up actions still require the applicable approval, acknowledgement, or owner-authorized automation scope.",
            "",
            "## Current Priority Signals",
            "",
            f"- Active backlog items: {metrics['backlog'].get('active_item_count')}",
            f"- Open MemBase work items: {metrics['membase'].get('open_work_items')}",
            f"- Release blockers: {metrics['regression'].get('release_blocker_count')}",
            f"- Actionable bridge/contention entries: {metrics['contention'].get('actionable_count')}",
            f"- Drift changed paths: {metrics['drift'].get('changed_path_count')}",
            "",
            "## Suggested Next User Actions",
            "",
            "\n".join(action_lines),
            "",
            "## Suggested Wrap-Up Actions",
            "",
            "1. Review the dashboard and startup/wrap-up reports before opening large artifacts.",
            "2. Confirm whether to run the full `kb-session-wrap` procedure for this session.",
            "3. Confirm whether any formal artifacts, backlog entries, or release blockers need owner disposition before the next session.",
            "",
        ]
    )


def _render_metric_table(snapshot: dict[str, Any]) -> str:
    rows = []
    for key, value in snapshot.items():
        rows.append(f"<tr><th>{html.escape(key.replace('_', ' ').title())}</th><td>{html.escape(str(value))}</td></tr>")
    return "\n".join(rows)


def _link_for_shortcut(shortcut: dict[str, str]) -> str:
    label = html.escape(str(shortcut.get("label") or "Open"))
    target = str(shortcut.get("target") or "")
    kind = shortcut.get("kind") or "file"
    if kind == "web":
        return f'<a href="{html.escape(target, quote=True)}">{label}</a>'
    if kind == "command":
        return f"<code>{html.escape(target)}</code>"
    return f'<a href="../../{html.escape(target, quote=True)}">{label}</a>'


def _render_health_strip(health: list[dict[str, str]]) -> str:
    return "\n".join(
        "<section "
        f'class="health-card {html.escape(item["status"])}" '
        f'title="{html.escape(item["tooltip"], quote=True)}">'
        f'<span class="health-label">{html.escape(item["label"])}</span>'
        f"<strong>{html.escape(item['value'])}</strong>"
        "</section>"
        for item in health
    )


def _render_action_center(actions: list[dict[str, Any]]) -> str:
    rows = []
    for action in actions:
        shortcut = action.get("shortcut") or {}
        rows.append(
            "<tr>"
            f'<th><span class="severity-dot {html.escape(str(action.get("severity")))}"></span>{html.escape(str(action.get("action")))}</th>'
            f"<td>{html.escape(str(action.get('owner_lane')))}</td>"
            f"<td>{html.escape(str(action.get('why')))}</td>"
            f"<td>{html.escape(str(action.get('remediation')))}</td>"
            f"<td>{_link_for_shortcut(shortcut)}</td>"
            f"<td>{html.escape(str(action.get('source')))}</td>"
            "</tr>"
        )
    return "\n".join(rows) or '<tr><td colspan="6">No corrective actions detected.</td></tr>'


def _render_risk_register(risks: list[dict[str, Any]]) -> str:
    rows = []
    for risk in risks:
        rows.append(
            "<tr>"
            f'<th><span class="severity-dot {html.escape(str(risk.get("severity")))}"></span>{html.escape(str(risk.get("risk")))}</th>'
            f"<td>{html.escape(str(risk.get('evidence')))}</td>"
            f"<td>{html.escape(str(risk.get('impact')))}</td>"
            f"<td>{html.escape(str(risk.get('remediation')))}</td>"
            f"<td>{html.escape(str(risk.get('owner')))}</td>"
            "</tr>"
        )
    return "\n".join(rows) or '<tr><td colspan="5">No active risks detected by current dashboard probes.</td></tr>'


def _render_release_readiness(release: dict[str, Any]) -> str:
    blockers = release.get("blockers") or []
    blocker_rows = "\n".join(
        f"<tr><th>Blocker {index}</th><td>{html.escape(str(blocker))}</td></tr>"
        for index, blocker in enumerate(blockers, start=1)
    )
    if not blocker_rows:
        blocker_rows = '<tr><td colspan="2">No release blockers detected.</td></tr>'
    return f"""
  <section class="split-panel">
    <div class="panel-visual {html.escape(str(release.get("status")))}">
      <span>Release Readiness</span>
      <strong>{html.escape(str(release.get("blocker_count")))} blockers</strong>
      <small>{html.escape(str(release.get("release_gate_script")))}</small>
    </div>
    <div>
      <table>
        <tbody>{blocker_rows}</tbody>
      </table>
      <p class="shortcut-row">{_link_for_shortcut(release.get("shortcut", {}))}</p>
    </div>
  </section>
"""


def _render_quality_rollup(rollup: dict[str, Any]) -> str:
    cards = [
        ("Total", rollup.get("total"), "green"),
        ("Failing", rollup.get("failing"), "red"),
        ("Manual", rollup.get("manual"), "yellow"),
        ("No Recent / Unknown", rollup.get("unknown"), "yellow"),
        ("Ready / Passing", rollup.get("ready_or_passing"), "green"),
    ]
    return "\n".join(
        f'<section class="mini-card {color}"><span>{html.escape(label)}</span><strong>{html.escape(str(value))}</strong></section>'
        for label, value, color in cards
    )


def _render_data_freshness(freshness: dict[str, Any]) -> str:
    sources = ", ".join(str(source) for source in freshness.get("sources", []))
    rows = {
        "Generated At": freshness.get("generated_at"),
        "GroundTruth DB Modified": freshness.get("groundtruth_db_modified_at"),
        "Repo Branch": freshness.get("repo_branch"),
        "Repo SHA": freshness.get("repo_short_sha"),
        "Scope Version": freshness.get("scope_version"),
        "Sources": sources,
    }
    return "\n".join(
        f"<tr><th>{html.escape(label)}</th><td>{html.escape(str(value))}</td></tr>" for label, value in rows.items()
    )


def _render_shortcuts(shortcuts: list[dict[str, str]]) -> str:
    return "\n".join(f'<span class="shortcut-chip">{_link_for_shortcut(shortcut)}</span>' for shortcut in shortcuts)


def _render_delivery_timeline_summary(summary: list[dict[str, Any]]) -> str:
    return "\n".join(
        "<section "
        f'class="timeline-stage {html.escape(str(item.get("status")))}">'
        f"<span>{html.escape(str(item.get('label')))}</span>"
        f"<strong>{html.escape(str(item.get('count')))}</strong>"
        f"<small>{html.escape(str(item.get('latest_result')))} / {html.escape(str(item.get('latest_version')))}</small>"
        "</section>"
        for item in summary
    )


def _timeline_link(row: dict[str, Any]) -> str:
    url = str(row.get("url") or "")
    source = html.escape(str(row.get("source") or ""))
    if url:
        return f'<a href="{html.escape(url, quote=True)}">{source or "Open"}</a>'
    return source


def _timeline_ordered_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted(rows, key=lambda row: str(row.get("timestamp") or "9999"))


def _timeline_date_label(timestamp: Any) -> str:
    text = str(timestamp or "").strip()
    if re.match(r"^\d{4}-\d{2}-\d{2}", text):
        return text[:10]
    return "Configuration"


def _render_delivery_timeline_rail(rows: list[dict[str, Any]]) -> str:
    grouped: dict[str, list[tuple[int, dict[str, Any]]]] = {}
    for index, row in enumerate(_timeline_ordered_rows(rows), start=1):
        grouped.setdefault(_timeline_date_label(row.get("timestamp")), []).append((index, row))
    rendered = []
    for date_label, events in grouped.items():
        event_cards = []
        for index, row in events:
            event_cards.append(
                '<section class="timeline-event">'
                f'<span class="timeline-node {html.escape(str(row.get("result_color")))}">{index}</span>'
                f'<span class="timeline-date-inline">{html.escape(date_label)}</span>'
                f'<span class="timeline-stage-label">{html.escape(str(row.get("stage_label")))}</span>'
                f"<strong>{html.escape(str(row.get('event') or 'Event'))}</strong>"
                f"<small>{html.escape(str(row.get('version') or 'not recorded'))}</small>"
                "</section>"
            )
        rendered.append(
            '<section class="timeline-day-group">'
            f'<div class="timeline-date-badge">{html.escape(date_label)}<span>{len(events)} event{"s" if len(events) != 1 else ""}</span></div>'
            f'<div class="timeline-day-events">{"".join(event_cards)}</div>'
            "</section>"
        )
    return "\n".join(rendered) or '<p class="note">No delivery timeline evidence detected.</p>'


def _render_delivery_timeline_details(rows: list[dict[str, Any]]) -> str:
    cards = []
    for index, row in enumerate(_timeline_ordered_rows(rows), start=1):
        cards.append(
            f"""
      <section class="timeline-detail" id="timeline-event-{index}">
        <div class="timeline-detail-heading"><span class="result-pill {html.escape(str(row.get("result_color")))}">{index}. {html.escape(str(row.get("stage_label")))}</span> <strong>{html.escape(str(row.get("event") or "Event"))}</strong> <span>{html.escape(_timeline_date_label(row.get("timestamp")))} / {html.escape(str(row.get("version") or "not recorded"))}</span></div>
        <table>
          <tbody>
            <tr><th>Calendar Date</th><td>{html.escape(_timeline_date_label(row.get("timestamp")))}</td></tr>
            <tr><th>Time</th><td>{html.escape(str(row.get("timestamp") or "configuration"))}</td></tr>
            <tr><th>Version / Build</th><td>{html.escape(str(row.get("version") or "not recorded"))}</td></tr>
            <tr><th>Commit</th><td>{html.escape(str(row.get("commit") or ""))}</td></tr>
            <tr><th>Branch</th><td>{html.escape(str(row.get("branch") or ""))}</td></tr>
            <tr><th>Result</th><td>{html.escape(str(row.get("result") or "unknown"))}</td></tr>
            <tr><th>Test Results</th><td>{html.escape(str(row.get("test_results") or ""))}</td></tr>
            <tr><th>Source</th><td>{_timeline_link(row)}</td></tr>
            <tr><th>Notes</th><td>{html.escape(str(row.get("notes") or ""))}</td></tr>
          </tbody>
        </table>
      </section>"""
        )
    content = "\n".join(cards) or '<p class="note">No delivery timeline details detected.</p>'
    return f"""
  <details class="drilldown print-page" id="deliveryTimelineDetails">
    <summary>Delivery Timeline Details <span>Open for delivery event source details.</span></summary>
    <div class="timeline-detail-list">
      {content}
    </div>
  </details>
"""


def _render_delivery_timeline(timeline: dict[str, Any]) -> str:
    return f"""
  <details class="drilldown print-page" id="deliveryTimeline" open>
    <summary>Delivery Timeline <span>Commits, builds, staging/production deployment evidence, versions, and test results.</span></summary>
    <div class="timeline-wrap">
      <div class="timeline-strip">
        {_render_delivery_timeline_summary(timeline.get("stage_summary", []))}
      </div>
      <div class="timeline-rail" aria-label="Delivery events from oldest to latest">
        <div class="timeline-track">
          {_render_delivery_timeline_rail(timeline.get("timeline", []))}
        </div>
      </div>
    </div>
  </details>
"""


def _render_action_center_section(actions: list[dict[str, Any]]) -> str:
    return f"""
  <details class="drilldown" id="actionCenter">
    <summary>Action Center <span>Open for prioritized remediation actions.</span></summary>
    <table>
      <thead>
        <tr><th>Action</th><th>Lane</th><th>Why</th><th>Remediation</th><th>Shortcut</th><th>Source</th></tr>
      </thead>
      <tbody>
        {_render_action_center(actions)}
      </tbody>
    </table>
  </details>
"""


def _short_sha(value: Any) -> str:
    text = str(value or "")
    return text[:7] if text else "unknown"


def _render_gtkb_upgrade_posture(posture: dict[str, Any]) -> str:
    checkout = posture.get("local_checkout") or {}
    upgrade_plan = posture.get("upgrade_plan") or {}
    repo_url = posture.get("repo_url")
    repo_cell = (
        f'<a href="{html.escape(str(repo_url), quote=True)}">{html.escape(str(repo_url))}</a>'
        if repo_url
        else "unknown"
    )
    action_counts = upgrade_plan.get("action_counts") or {}
    action_summary = ", ".join(f"{key}: {value}" for key, value in action_counts.items()) or "none"
    sample_actions = upgrade_plan.get("sample_actions") or []
    sample_rows = "\n".join(
        "<tr>"
        f"<td>{html.escape(str(action.get('action')))}</td>"
        f"<td>{html.escape(str(action.get('file')))}</td>"
        f"<td>{html.escape(str(action.get('reason')))}</td>"
        "</tr>"
        for action in sample_actions
    )
    if not sample_rows:
        sample_rows = '<tr><td colspan="3">No mutating dry-run actions detected.</td></tr>'
    apply_state = "Disabled in static dashboard; owner-approved execution required."
    return f"""
  <h3>GT-KB Version / Upgrade Posture</h3>
  <table>
    <tbody>
      <tr><th>Status</th><td>{html.escape(str(posture.get("status")))}</td></tr>
      <tr><th>Package Version</th><td>{html.escape(str(posture.get("package_version")))}</td></tr>
      <tr><th>Scaffold Version</th><td>{html.escape(str(posture.get("scaffold_version")))}</td></tr>
      <tr><th>Package Source</th><td>{html.escape(str(posture.get("package_file")))}</td></tr>
      <tr><th>Upstream Repository</th><td>{repo_cell}</td></tr>
      <tr><th>Latest Release</th><td>{html.escape(str(posture.get("latest_release_tag")))} @ {_short_sha(posture.get("latest_release_sha"))}</td></tr>
      <tr><th>Upstream Main</th><td>{html.escape(str(posture.get("latest_main_branch")))} @ {_short_sha(posture.get("latest_main_sha"))}</td></tr>
      <tr><th>Local Checkout</th><td>{html.escape(str(checkout.get("path")))} @ {_short_sha(checkout.get("sha"))} ({html.escape(str(checkout.get("branch") or "unknown"))})</td></tr>
      <tr><th>Unreleased Commits After Latest Release</th><td>{html.escape(str(posture.get("unreleased_commit_count")))}</td></tr>
      <tr><th>Release Upgrade Available</th><td>{html.escape(str(posture.get("release_upgrade_available")))}</td></tr>
      <tr><th>Scaffold Upgrade Plan Available</th><td>{html.escape(str(posture.get("scaffold_upgrade_available")))}</td></tr>
      <tr><th>GT CLI Available</th><td>{html.escape(str(posture.get("gt_cli_available")))}</td></tr>
      <tr><th>Dry-Run Plan Command</th><td><code>{html.escape(str(posture.get("plan_command")))}</code></td></tr>
      <tr><th>Apply Command</th><td><code>{html.escape(str(posture.get("apply_command")))}</code><br>{html.escape(apply_state)}</td></tr>
      <tr><th>Apply Gate</th><td>{html.escape(str(posture.get("apply_gate")))}</td></tr>
      <tr><th>Dry-Run Action Counts</th><td>{html.escape(action_summary)}</td></tr>
    </tbody>
  </table>
  <details class="drilldown" id="gtkbUpgradePlan">
    <summary>GT-KB Upgrade Plan Sample <span>Open for representative mutating dry-run actions.</span></summary>
    <table>
      <thead>
        <tr><th>Action</th><th>File</th><th>Reason</th></tr>
      </thead>
      <tbody>
        {sample_rows}
      </tbody>
    </table>
  </details>
"""


def _integration_status_dot(details: dict[str, Any]) -> tuple[str, str]:
    health = str(details.get("health") or "")
    status = str(details.get("status") or "")
    if health == "failing" or status == "not_wired":
        return "red", "Needs attention"
    if health in {"passing", "configured"} and status == "ready":
        return "green", "Ready"
    if status == "manual" or health == "manual":
        return "yellow", "Manual"
    if status == "partial" or health in {"no_recent_run", "partial_history", "live_state_unavailable", "running"}:
        return "yellow", "Needs review"
    if status == "ready":
        return "green", "Ready"
    return "yellow", "Needs review"


def _html_id_fragment(value: str) -> str:
    fragment = re.sub(r"[^a-zA-Z0-9_-]+", "-", value.strip()).strip("-")
    return fragment or "integration"


def _render_testing_service_integrations(integrations: dict[str, Any]) -> str:
    sections = []
    ordered = sorted(integrations.items(), key=lambda item: (item[1].get("order", 999), item[0]))
    for name, details in ordered:
        display_name = details.get("display_name") or {"github": "GitHub"}.get(name, name.title())
        evidence = details.get("evidence") or []
        artifacts = details.get("artifacts") or []
        gaps = details.get("gaps") or []
        evidence_text = "; ".join(str(item) for item in evidence[:6]) or "No local evidence found."
        artifact_text = "; ".join(str(item) for item in artifacts[:4]) or "None declared."
        if gaps:
            artifact_text = f"{artifact_text} Gaps: {'; '.join(str(item) for item in gaps[:3])}"
        remediation_text = str(details.get("remediation") or "No remediation recorded.")
        dot_class, dot_label = _integration_status_dot(details)
        section_id = f"integration-{_html_id_fragment(name)}"
        fact_rows = [
            ("Integration", display_name),
            ("Config", str(details.get("status"))),
            ("Health", str(details.get("health"))),
            ("Latest Run", str(details.get("latest_run_summary"))),
            ("Gate Role", str(details.get("gate_role") or "Unclassified testing support.")),
            ("Suggested Remediation", remediation_text),
            ("Local Evidence", evidence_text),
            ("Artifacts / Gaps", artifact_text),
        ]
        rows = "\n".join(
            f"<tr><th>{html.escape(label)}</th><td>{html.escape(value)}</td></tr>" for label, value in fact_rows
        )
        sections.append(
            f"""
    <details class="integration-drilldown" id="{html.escape(section_id, quote=True)}">
      <summary><span class="status-dot {dot_class}" aria-label="{html.escape(dot_label, quote=True)}"></span>{html.escape(display_name)} <span>{html.escape(str(details.get("health")))} / {html.escape(str(details.get("status")))}</span></summary>
      <table>
        <tbody>
          {rows}
        </tbody>
      </table>
    </details>"""
        )
    return f"""
  <details class="drilldown" id="testingServiceIntegrations">
    <summary>Testing Service / Tool Integrations <span>Open for per-service health, remediation, evidence, and artifacts.</span></summary>
    <div class="integration-list">
      {"".join(sections)}
    </div>
  </details>
"""


def _json_for_script(data: dict[str, Any]) -> str:
    return json.dumps(data, sort_keys=True).replace("&", "\\u0026").replace("<", "\\u003c").replace(">", "\\u003e")


def render_dashboard(model: dict[str, Any], history: list[dict[str, Any]]) -> str:
    current = _snapshot_from_model(model)
    intelligence = model.get("dashboard_intelligence", {})
    history_rows = "\n".join(
        "<tr>"
        f"<td>{html.escape(str(row.get('generated_at')))}</td>"
        f"<td>{html.escape(str(row.get('backlog_active_items')))}</td>"
        f"<td>{html.escape(str(row.get('membase_open_work_items')))}</td>"
        f"<td>{html.escape(str(row.get('deliberation_archive_current_total')))}</td>"
        f"<td>{html.escape(str(row.get('pytest_file_count')))}</td>"
        f"<td>{html.escape(str(row.get('specification_current_total')))}</td>"
        f"<td>{html.escape(str(row.get('drift_changed_path_count')))}</td>"
        f"<td>{html.escape(str(row.get('regression_release_blocker_count')))}</td>"
        f"<td>{html.escape(str(row.get('contention_actionable_bridge_count')))}</td>"
        f"<td>{html.escape(str(row.get('tokens_consumed_before_user_input')))}</td>"
        f"<td>{html.escape(str(row.get('scope_confidence')))}</td>"
        "</tr>"
        for row in history[-40:]
    )
    dashboard_json = html.escape(json.dumps(model["dashboard_requirements"]["subsystems"]))
    dashboard_payload = _json_for_script({"model": model, "history": history})
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>GroundTruth-KB Project Dashboard</title>
  <style>
    :root {{
      --bg: #f6f7f9;
      --panel: #ffffff;
      --ink: #202124;
      --muted: #5f6368;
      --line: #d8dde3;
      --soft: #eef1f4;
      --red: #b42318;
      --amber: #b45309;
      --green: #2f6b2f;
      --teal: #0f766e;
      --indigo: #4338ca;
    }}
    body {{
      font-family: Arial, sans-serif;
      margin: 28px;
      color: var(--ink);
      background: var(--bg);
      line-height: 1.45;
    }}
    main {{ max-width: 1280px; margin: 0 auto; }}
    h1, h2, h3 {{ color: #1d252c; letter-spacing: 0; }}
    h1 {{ font-size: 28px; margin-bottom: 6px; }}
    h2 {{ margin-top: 30px; }}
    a {{ color: #0f766e; }}
    table {{ width: 100%; border-collapse: collapse; background: var(--panel); margin: 16px 0 28px; }}
    th, td {{ border: 1px solid var(--line); padding: 8px 10px; text-align: left; vertical-align: top; }}
    th {{ background: var(--soft); }}
    code {{ background: var(--soft); padding: 1px 4px; }}
    .note {{ background: var(--panel); border: 1px solid var(--line); padding: 12px; }}
    .dashboard-hero {{
      background: linear-gradient(135deg, #12343b 0%, #1f5f5b 52%, #6b5b2a 100%);
      color: #ffffff !important;
      border-radius: 8px;
      padding: 22px;
      margin-bottom: 18px;
      position: relative;
      overflow: hidden;
    }}
    .dashboard-hero h1 {{ color: #ffffff; margin-top: 0; }}
    .hero-grid {{
      display: grid;
      grid-template-columns: minmax(260px, 1.2fr) minmax(220px, 0.8fr);
      gap: 18px;
      align-items: end;
    }}
    .hero-meta {{ color: #e8f3f1; margin: 5px 0; }}
    .export-button {{
      background: #ffffff;
      border: 1px solid #ffffff;
      border-radius: 8px;
      color: #12343b;
      cursor: pointer;
      display: inline-block;
      font-weight: 700;
      margin: 0 0 8px 8px;
      padding: 10px 14px;
      text-decoration: none;
      width: fit-content;
    }}
    .health-strip {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
      gap: 10px;
      margin: 18px 0;
    }}
    .health-card, .mini-card {{
      background: var(--panel);
      border: 1px solid var(--line);
      border-left: 7px solid var(--green);
      border-radius: 8px;
      padding: 12px;
    }}
    .health-card.red, .mini-card.red {{ border-left-color: var(--red); }}
    .health-card.yellow, .mini-card.yellow {{ border-left-color: var(--amber); }}
    .health-card.green, .mini-card.green {{ border-left-color: var(--green); }}
    .health-label, .mini-card span {{
      color: var(--muted);
      display: block;
      font-size: 12px;
      text-transform: uppercase;
    }}
    .health-card strong, .mini-card strong {{ display: block; font-size: 20px; margin-top: 4px; }}
    .section-band {{
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 14px;
      margin: 16px 0 24px;
    }}
    .section-band h2 {{ margin-top: 0; }}
    .severity-dot {{
      border-radius: 50%;
      display: inline-block;
      height: 10px;
      margin-right: 7px;
      width: 10px;
    }}
    .severity-dot.red {{ background: var(--red); }}
    .severity-dot.yellow {{ background: var(--amber); }}
    .severity-dot.green {{ background: var(--green); }}
    .split-panel {{
      display: grid;
      grid-template-columns: minmax(220px, 0.45fr) minmax(320px, 1fr);
      gap: 14px;
      align-items: stretch;
    }}
    .panel-visual {{
      border-radius: 8px;
      color: #ffffff;
      display: grid;
      place-content: center;
      min-height: 180px;
      padding: 18px;
      text-align: center;
    }}
    .panel-visual.red {{ background: #8b1e3f; }}
    .panel-visual.yellow {{ background: #8b5a0a; }}
    .panel-visual.green {{ background: #2f6b2f; }}
    .panel-visual, .panel-visual * {{ color: #ffffff !important; }}
    .panel-visual strong {{ display: block; font-size: 34px; margin: 8px 0; }}
    .quality-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
      gap: 10px;
      margin-bottom: 14px;
    }}
    .shortcut-row {{
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      margin: 10px 0 0;
    }}
    .shortcut-chip {{
      background: #eef7f5;
      border: 1px solid #bdd8d3;
      border-radius: 8px;
      display: inline-block;
      padding: 6px 9px;
    }}
    .timeline-wrap {{
      padding: 0 12px 12px;
    }}
    .timeline-strip {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(170px, 1fr));
      gap: 10px;
      margin: 12px 0;
    }}
    .timeline-stage {{
      background: #fbfcfd;
      border: 1px solid var(--line);
      border-left: 7px solid var(--amber);
      border-radius: 8px;
      padding: 12px;
    }}
    .timeline-stage.green {{ border-left-color: var(--green); }}
    .timeline-stage.red {{ border-left-color: var(--red); }}
    .timeline-stage.yellow {{ border-left-color: var(--amber); }}
    .timeline-stage span, .timeline-stage small {{ color: var(--muted); display: block; }}
    .timeline-stage strong {{ display: block; font-size: 24px; margin: 4px 0; }}
    .result-pill {{
      border-radius: 8px;
      color: #ffffff;
      display: inline-block;
      font-size: 12px;
      font-weight: 700;
      margin-bottom: 4px;
      padding: 3px 7px;
    }}
    .result-pill.green {{ background: var(--green); }}
    .result-pill.red {{ background: var(--red); }}
    .result-pill.yellow {{ background: #8b5a0a; }}
    .result-pill, .result-pill * {{ color: #ffffff !important; }}
    .timeline-rail {{
      margin: 18px 0;
      overflow-x: auto;
      padding: 10px 0 18px;
    }}
    .timeline-track {{
      align-items: stretch;
      display: flex;
      gap: 16px;
      min-width: 100%;
      position: relative;
      width: max-content;
    }}
    .timeline-track::before {{
      background: var(--line);
      content: "";
      height: 3px;
      left: 0;
      position: absolute;
      right: 0;
      top: 32px;
    }}
    .timeline-day-group {{
      display: grid;
      flex: 0 0 auto;
      gap: 8px;
      min-width: 210px;
      position: relative;
      z-index: 1;
    }}
    .timeline-date-badge {{
      align-self: start;
      background: #173f3b;
      border-radius: 8px;
      color: #ffffff;
      font-weight: 700;
      padding: 7px 9px;
      width: fit-content;
    }}
    .timeline-date-badge span {{
      color: #d8ebe7;
      display: block;
      font-size: 12px;
      font-weight: 400;
      margin-top: 2px;
    }}
    .timeline-day-events {{
      display: flex;
      gap: 10px;
    }}
    .timeline-event {{
      background: #fbfcfd;
      border: 1px solid var(--line);
      border-radius: 8px;
      flex: 0 0 185px;
      min-height: 126px;
      padding: 8px;
      position: relative;
      z-index: 1;
    }}
    .timeline-node {{
      align-items: center;
      border: 3px solid #ffffff;
      border-radius: 50%;
      color: #ffffff;
      display: flex;
      font-size: 12px;
      font-weight: 700;
      height: 31px;
      justify-content: center;
      margin-bottom: 8px;
      width: 31px;
    }}
    .timeline-node.green {{ background: var(--green); }}
    .timeline-node.red {{ background: var(--red); }}
    .timeline-node.yellow {{ background: var(--amber); }}
    .timeline-date-inline {{
      color: #173f3b;
      display: block;
      font-size: 12px;
      font-weight: 700;
      margin-bottom: 3px;
    }}
    .timeline-stage-label {{
      color: var(--muted);
      display: block;
      font-size: 12px;
      text-transform: uppercase;
    }}
    .timeline-event strong {{
      display: block;
      margin: 3px 0;
      overflow-wrap: anywhere;
    }}
    .timeline-event small {{
      color: var(--muted);
      display: block;
      overflow-wrap: anywhere;
    }}
    .timeline-detail-list {{
      display: grid;
      gap: 8px;
    }}
    .timeline-detail {{
      background: #fbfcfd;
      border: 1px solid var(--line);
      border-radius: 8px;
    }}
    .timeline-detail-heading {{
      align-items: center;
      display: flex;
      gap: 8px;
      padding: 10px 12px;
    }}
    .timeline-detail-heading span:last-child {{
      color: var(--muted);
      margin-left: auto;
    }}
    .timeline-detail table {{
      margin: 0;
    }}
    .dashboard-meta {{ color: var(--muted); margin-top: 0; }}
    .metric-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(210px, 1fr));
      gap: 12px;
      margin: 18px 0 10px;
    }}
    .metric-tile {{
      background: var(--panel);
      border: 1px solid var(--line);
      border-left: 6px solid var(--teal);
      border-radius: 8px;
      padding: 12px;
      min-height: 108px;
    }}
    .metric-tile.watch {{ border-left-color: var(--red); }}
    .metric-tile.steady {{ border-left-color: var(--amber); }}
    .metric-tile.growth {{ border-left-color: var(--green); }}
    .tile-label {{ color: var(--muted); font-size: 13px; }}
    .tile-value {{ font-size: 30px; font-weight: 700; margin: 5px 0; }}
    .tile-delta {{ font-size: 13px; color: var(--muted); }}
    .visual-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
      gap: 14px;
      margin: 16px 0 8px;
    }}
    .chart-panel {{
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 14px;
      min-height: 238px;
    }}
    .chart-panel h3 {{ margin: 0 0 6px; font-size: 16px; }}
    .chart-subtitle {{ color: var(--muted); font-size: 13px; margin: 0 0 10px; }}
    .sparkline {{
      width: 100%;
      height: 118px;
      display: block;
      border: 1px solid var(--line);
      background: #fbfcfd;
    }}
    .chart-legend {{
      display: flex;
      flex-wrap: wrap;
      gap: 8px 14px;
      margin-top: 10px;
      color: var(--muted);
      font-size: 12px;
    }}
    .legend-swatch {{
      display: inline-block;
      width: 18px;
      height: 3px;
      margin-right: 5px;
      vertical-align: middle;
    }}
    .signal-list {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
      gap: 10px;
      margin: 14px 0;
      padding: 0;
      list-style: none;
    }}
    .signal-list li {{
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 10px 12px;
    }}
    .signal-kicker {{
      display: block;
      color: var(--muted);
      font-size: 12px;
      text-transform: uppercase;
    }}
    .signal-text {{ display: block; margin-top: 3px; }}
    .controls {{
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      gap: 10px;
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 10px 12px;
      margin: 16px 0 4px;
    }}
    .controls label {{ font-weight: 700; }}
    .controls select {{
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 7px 9px;
      background: #ffffff;
      color: var(--ink);
      font: inherit;
    }}
    .controls span {{ color: var(--muted); font-size: 13px; }}
    .heatmap {{
      display: grid;
      grid-template-columns: minmax(110px, 1fr) repeat(var(--cols), minmax(18px, 1fr));
      gap: 3px;
      align-items: center;
      overflow-x: auto;
    }}
    .heatmap-label {{ color: var(--muted); font-size: 12px; white-space: nowrap; }}
    .heatmap-cell {{
      height: 18px;
      border: 1px solid #ffffff;
      background: var(--soft);
    }}
    details.drilldown {{
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
      margin: 16px 0 28px;
    }}
    details.drilldown summary {{
      cursor: pointer;
      font-weight: 700;
      padding: 12px 14px;
      color: #1d252c;
      list-style-position: inside;
    }}
    details.drilldown summary span {{
      color: var(--muted);
      display: inline-block;
      font-size: 13px;
      font-weight: 400;
      margin-left: 8px;
    }}
    details.drilldown table {{ margin: 0; }}
    details.drilldown .history-wrap {{ margin: 0; }}
    .integration-list {{
      display: grid;
      gap: 10px;
      padding: 0 12px 12px;
    }}
    details.integration-drilldown {{
      border: 1px solid var(--line);
      border-radius: 8px;
      background: #fbfcfd;
    }}
    details.integration-drilldown summary {{
      align-items: center;
      display: flex;
      gap: 8px;
      padding: 10px 12px;
    }}
    details.integration-drilldown summary span:last-child {{
      margin-left: auto;
    }}
    .status-dot {{
      border-radius: 50%;
      display: inline-block;
      height: 11px;
      min-width: 11px;
      width: 11px;
    }}
    .status-dot.red {{ background: var(--red); }}
    .status-dot.yellow {{ background: var(--amber); }}
    .status-dot.green {{ background: var(--green); }}
    .history-wrap {{ overflow-x: auto; }}
    @media print {{
      body {{ margin: 0; background: #ffffff; }}
      main {{ max-width: none; }}
      .export-button, .controls {{ display: none; }}
      .section-band, details.drilldown, .dashboard-hero {{ break-inside: avoid; }}
      details.drilldown, details.integration-drilldown {{ display: block; }}
      details.drilldown > summary, details.integration-drilldown > summary {{ break-after: avoid; }}
      h2 {{ break-after: avoid; }}
      tr {{ break-inside: avoid; }}
      .print-page {{ break-before: page; }}
    }}
  </style>
</head>
<body>
<main>
  <section class="dashboard-hero">
    <div class="hero-grid">
      <div>
        <h1>GroundTruth-KB Project Dashboard</h1>
        <p class="hero-meta">Generated: {html.escape(model["generated_at"])}</p>
        <p class="hero-meta">Branch: {html.escape(str(intelligence.get("data_freshness", {}).get("repo_branch")))} @ {html.escape(str(intelligence.get("data_freshness", {}).get("repo_short_sha")))}</p>
        <p>{html.escape(model["dashboard_requirements"]["scope_note"])}</p>
      </div>
      <div>
        <button id="exportDashboard" class="export-button" title="Open the generated PDF export. If blocked, use browser Print to PDF.">Export PDF</button>
        <p class="hero-meta">Stakeholder export: {PDF_EXPORT_FILENAME}</p>
      </div>
    </div>
  </section>

  <section class="health-strip" aria-label="Executive health status">
    {_render_health_strip(intelligence.get("health", []))}
  </section>

  {_render_delivery_timeline(model["infrastructure"].get("delivery_timeline", {}))}

  {_render_delivery_timeline_details(model["infrastructure"].get("delivery_timeline", {}).get("timeline", []))}

  {_render_action_center_section(intelligence.get("action_center", []))}

  <section class="section-band">
    <h2>Shortcuts</h2>
    <p class="shortcut-row">{_render_shortcuts(intelligence.get("shortcuts", []))}</p>
  </section>

  <p class="note">Time-series KPI coverage: <code>{dashboard_json}</code></p>

  <h2>Executive Signals</h2>
  <div class="controls">
    <label for="timeIncrement">Change increment</label>
    <select id="timeIncrement">
      <option value="sessions">Sessions</option>
      <option value="calendar-days">Calendar days</option>
    </select>
    <span id="incrementSummary">Showing one point per dashboard snapshot.</span>
  </div>
  <div id="metricTiles" class="metric-grid" aria-live="polite"></div>

  <h2>Trend Signals</h2>
  <ul id="signalList" class="signal-list"></ul>

  <section id="kpiMovementSection">
    <h2>KPI Movement</h2>
    <div id="chartGrid" class="visual-grid"></div>
  </section>

  <h2>Divergence And Convergence</h2>
  <div class="visual-grid">
    <section class="chart-panel">
      <h3>Work Pressure vs Knowledge Surface</h3>
      <p class="chart-subtitle">Normalized movement shows whether backlog, blockers, bridge contention, and drift are converging with or diverging from MemBase, DA, specs, and tests.</p>
      <svg id="pressureKnowledgeChart" class="sparkline" viewBox="0 0 640 180" role="img" aria-label="Normalized work pressure and knowledge surface trend"></svg>
      <div class="chart-legend">
        <span><span class="legend-swatch" style="background: var(--red);"></span>Work pressure</span>
        <span><span class="legend-swatch" style="background: var(--green);"></span>Knowledge surface</span>
      </div>
    </section>
    <section class="chart-panel">
      <h3>Change Heatmap</h3>
      <p class="chart-subtitle">Darker cells mark where each metric moved relative to its observed range. Pale rows are stable.</p>
      <div id="changeHeatmap" class="heatmap"></div>
    </section>
  </div>

  <section class="section-band print-page">
    <h2>Release Readiness</h2>
    {_render_release_readiness(intelligence.get("release_readiness", {}))}
  </section>

  <section class="section-band">
    <h2>Quality / Security / Testing Rollup</h2>
    <div class="quality-grid">
      {_render_quality_rollup(intelligence.get("quality_rollup", {}))}
    </div>
    <p class="note">Open the integration drilldowns below for per-service health, remediation, artifacts, and gaps.</p>
  </section>

  <section class="section-band">
    <h2>Risk Register</h2>
    <table>
      <thead>
        <tr><th>Risk</th><th>Evidence</th><th>Impact</th><th>Remediation</th><th>Owner</th></tr>
      </thead>
      <tbody>
        {_render_risk_register(intelligence.get("risk_register", []))}
      </tbody>
    </table>
  </section>

  <details class="drilldown" id="currentSnapshot">
    <summary>Current Snapshot <span>Open for the full current metric table.</span></summary>
    <table>
      <tbody>
        {_render_metric_table(current)}
      </tbody>
    </table>
  </details>

  <details class="drilldown" id="timeSeriesHistory">
    <summary>Time-Series KPI History <span>Open for the latest 40 scoped history rows.</span></summary>
    <div class="history-wrap">
      <table>
        <thead>
          <tr>
            <th>Generated At</th>
            <th>Backlog</th>
            <th>MemBase Open WI</th>
            <th>DA Total</th>
            <th>Tests</th>
            <th>Specs</th>
            <th>Drift</th>
            <th>Regression</th>
            <th>Contention</th>
            <th>Tokens</th>
            <th>Scope</th>
          </tr>
        </thead>
        <tbody>
          {history_rows}
        </tbody>
      </table>
    </div>
  </details>

  <h2>Implementation Infrastructure</h2>
  <p class="note">GT-KB is reported here only as project instrumentation, not as the product represented by the primary KPIs.</p>
  <table>
    <tbody>
      <tr><th>Instrumentation</th><td>{html.escape(str(model["infrastructure"].get("instrumentation")))}</td></tr>
      <tr><th>Skill Templates</th><td>{html.escape(str(model["infrastructure"].get("skill_template_count")))}</td></tr>
      <tr><th>Rule Templates</th><td>{html.escape(str(model["infrastructure"].get("rule_template_count")))}</td></tr>
      <tr><th>Hook Templates</th><td>{html.escape(str(model["infrastructure"].get("hook_template_count")))}</td></tr>
      <tr><th>Dev Environment Inventory</th><td>{html.escape(_dev_inventory_compact_text(model["infrastructure"].get("dev_environment_inventory", {})))}</td></tr>
      <tr><th>Dashboard History</th><td>{html.escape(str(model["infrastructure"].get("dashboard_history_path")))}</td></tr>
    </tbody>
  </table>
  {_render_gtkb_upgrade_posture(model["infrastructure"].get("gtkb_upgrade_posture", {}))}
  {_render_testing_service_integrations(model["infrastructure"].get("testing_service_integrations", {}))}

  <details class="drilldown print-page" id="dataFreshness">
    <summary>Data Freshness / Provenance <span>Open for source and evidence timing.</span></summary>
    <table>
      <tbody>
        {_render_data_freshness(intelligence.get("data_freshness", {}))}
      </tbody>
    </table>
  </details>
  <script id="dashboardData" type="application/json">{dashboard_payload}</script>
  <script>
    const dashboard = JSON.parse(document.getElementById("dashboardData").textContent);
    const history = dashboard.history || [];
    let selectedIncrement = "sessions";
    const metrics = [
      {{ key: "backlog_active_items", label: "Backlog", group: "pressure", lowerIsBetter: true, color: "#b42318" }},
      {{ key: "membase_open_work_items", label: "MemBase Open WI", group: "knowledge", lowerIsBetter: true, color: "#0f766e" }},
      {{ key: "deliberation_archive_current_total", label: "Deliberation Archive", group: "knowledge", lowerIsBetter: false, color: "#4338ca" }},
      {{ key: "pytest_file_count", label: "Pytest Files", group: "knowledge", lowerIsBetter: false, color: "#2f6b2f" }},
      {{ key: "specification_current_total", label: "Specifications", group: "knowledge", lowerIsBetter: false, color: "#6d4c41" }},
      {{ key: "drift_changed_path_count", label: "Drift Changed Paths", group: "pressure", lowerIsBetter: true, color: "#b45309" }},
      {{ key: "regression_release_blocker_count", label: "Release Blockers", group: "pressure", lowerIsBetter: true, color: "#8b1e3f" }},
      {{ key: "contention_actionable_bridge_count", label: "Bridge Contention", group: "pressure", lowerIsBetter: true, color: "#5b5f97" }}
    ];

    function dateKey(row) {{
      return String(row.generated_at || "").slice(0, 10) || "unknown";
    }}

    function aggregateByCalendarDay(rows) {{
      const byDay = new Map();
      rows.forEach((row) => byDay.set(dateKey(row), row));
      return Array.from(byDay.entries()).map(([day, row]) => ({{
        ...row,
        generated_at: day,
        source_sample_count: rows.filter((candidate) => dateKey(candidate) === day).length
      }}));
    }}

    function activeHistory() {{
      return selectedIncrement === "calendar-days" ? aggregateByCalendarDay(history) : history;
    }}

    function incrementLabel() {{
      return selectedIncrement === "calendar-days" ? "calendar day" : "session";
    }}

    function numericSeries(key) {{
      return activeHistory().map((row) => Number(row[key])).filter((value) => Number.isFinite(value));
    }}

    function deltaFor(def) {{
      const values = numericSeries(def.key);
      const first = values[0];
      const last = values[values.length - 1];
      const delta = Number.isFinite(first) && Number.isFinite(last) ? last - first : 0;
      return {{ values, first, last, delta }};
    }}

    function statusFor(def, delta) {{
      if (delta === 0) return "steady";
      const improving = def.lowerIsBetter ? delta < 0 : delta > 0;
      return improving ? "growth" : "watch";
    }}

    function formatDelta(delta) {{
      if (delta === 0) return "no movement";
      return `${{delta > 0 ? "+" : ""}}${{delta}} since first ${{incrementLabel()}}`;
    }}

    function pointsFor(values, width, height, pad) {{
      const min = Math.min(...values);
      const max = Math.max(...values);
      const span = max - min || 1;
      return values.map((value, index) => {{
        const x = pad + (index * (width - pad * 2)) / Math.max(values.length - 1, 1);
        const y = height - pad - ((value - min) / span) * (height - pad * 2);
        return `${{x.toFixed(1)}},${{y.toFixed(1)}}`;
      }}).join(" ");
    }}

    function renderMetricTiles() {{
      const selected = metrics.filter((def) => [
        "backlog_active_items",
        "drift_changed_path_count",
        "regression_release_blocker_count",
        "contention_actionable_bridge_count",
        "deliberation_archive_current_total",
        "specification_current_total"
      ].includes(def.key));
      document.getElementById("metricTiles").innerHTML = selected.map((def) => {{
        const trend = deltaFor(def);
        const status = statusFor(def, trend.delta);
        return `
          <section class="metric-tile ${{status}}">
            <span class="tile-label">${{def.label}}</span>
            <div class="tile-value">${{trend.last ?? "n/a"}}</div>
            <div class="tile-delta">${{formatDelta(trend.delta)}}</div>
          </section>
        `;
      }}).join("");
    }}

    function renderSignals() {{
      const changed = metrics
        .map((def) => ({{ def, ...deltaFor(def) }}))
        .filter((item) => item.values.length && item.delta !== 0)
        .sort((a, b) => Math.abs(b.delta) - Math.abs(a.delta));
      const flatPressure = metrics
        .map((def) => ({{ def, ...deltaFor(def) }}))
        .filter((item) => item.values.length && item.delta === 0 && item.def.group === "pressure");
      const signals = [];
      changed.slice(0, 4).forEach((item) => {{
        const status = statusFor(item.def, item.delta) === "watch" ? "Watch" : "Movement";
        signals.push(`<li><span class="signal-kicker">${{status}}</span><span class="signal-text">${{item.def.label}} moved from ${{item.first}} to ${{item.last}} (${{formatDelta(item.delta)}}).</span></li>`);
      }});
      flatPressure.forEach((item) => {{
        signals.push(`<li><span class="signal-kicker">Plateau</span><span class="signal-text">${{item.def.label}} stayed at ${{item.last}} across the sampled window.</span></li>`);
      }});
      if (!signals.length) {{
        signals.push(`<li><span class="signal-kicker">Stable</span><span class="signal-text">No numeric KPI movement was detected in the sampled window.</span></li>`);
      }}
      document.getElementById("signalList").innerHTML = signals.join("");
    }}

    function renderSparklines() {{
      const movementSection = document.getElementById("kpiMovementSection");
      const chartGrid = document.getElementById("chartGrid");
      const movingMetrics = metrics
        .map((def) => ({{ def, ...deltaFor(def) }}))
        .filter((item) => item.values.length > 1 && item.delta !== 0);
      movementSection.hidden = movingMetrics.length === 0;
      if (!movingMetrics.length) {{
        chartGrid.innerHTML = "";
        return;
      }}
      chartGrid.innerHTML = movingMetrics.map((item) => {{
        const def = item.def;
        const trend = deltaFor(def);
        const values = trend.values.length ? trend.values : [0];
        const points = pointsFor(values, 280, 110, 12);
        const status = statusFor(def, trend.delta);
        return `
          <section class="chart-panel">
            <h3>${{def.label}}</h3>
            <p class="chart-subtitle">${{formatDelta(trend.delta)}}. Latest value: ${{trend.last ?? "n/a"}}.</p>
            <svg class="sparkline" viewBox="0 0 280 110" role="img" aria-label="${{def.label}} trend">
              <line x1="12" y1="88" x2="268" y2="88" stroke="#d8dde3" stroke-width="1"></line>
              <polyline fill="none" stroke="${{def.color}}" stroke-width="3" points="${{points}}"></polyline>
              <circle cx="${{points.split(" ").at(-1).split(",")[0]}}" cy="${{points.split(" ").at(-1).split(",")[1]}}" r="4" fill="${{def.color}}"></circle>
            </svg>
            <div class="chart-legend"><span>${{status === "watch" ? "Needs attention" : status === "growth" ? "Improving/growing" : "Flat"}}</span></div>
          </section>
        `;
      }}).join("");
    }}

    function normalizedComposite(group) {{
      const defs = metrics.filter((def) => def.group === group);
      const rows = activeHistory();
      return rows.map((_, index) => {{
        const values = defs.map((def) => {{
          const series = numericSeries(def.key);
          const min = Math.min(...series);
          const max = Math.max(...series);
          const span = max - min || 1;
          const value = Number(rows[index][def.key]);
          if (!Number.isFinite(value)) return 0;
          return (value - min) / span;
        }});
        return values.reduce((sum, value) => sum + value, 0) / Math.max(values.length, 1);
      }});
    }}

    function renderCompositeChart() {{
      const svg = document.getElementById("pressureKnowledgeChart");
      const pressure = normalizedComposite("pressure");
      const knowledge = normalizedComposite("knowledge");
      const pressurePoints = pointsFor(pressure, 640, 180, 18);
      const knowledgePoints = pointsFor(knowledge, 640, 180, 18);
      svg.innerHTML = `
        <line x1="18" y1="144" x2="622" y2="144" stroke="#d8dde3" stroke-width="1"></line>
        <polyline fill="none" stroke="#b42318" stroke-width="4" points="${{pressurePoints}}"></polyline>
        <polyline fill="none" stroke="#2f6b2f" stroke-width="4" points="${{knowledgePoints}}"></polyline>
      `;
    }}

    function renderHeatmap() {{
      const heatmap = document.getElementById("changeHeatmap");
      const activeRows = activeHistory();
      const visibleRows = activeRows.slice(-20);
      heatmap.style.setProperty("--cols", visibleRows.length || 1);
      const heatmapRows = metrics.map((def) => {{
        const series = numericSeries(def.key);
        const min = Math.min(...series);
        const max = Math.max(...series);
        const span = max - min || 1;
        const cells = visibleRows.map((row) => {{
          const value = Number(row[def.key]);
          const scaled = Number.isFinite(value) ? (value - min) / span : 0;
          const alpha = 0.15 + scaled * 0.7;
          return `<span class="heatmap-cell" title="${{def.label}} on ${{row.generated_at}}: ${{value}}" style="background: rgba(180, 83, 9, ${{alpha.toFixed(2)}});"></span>`;
        }}).join("");
        return `<span class="heatmap-label">${{def.label}}</span>${{cells}}`;
      }}).join("");
      heatmap.innerHTML = heatmapRows;
    }}

    function updateIncrementSummary() {{
      const rows = activeHistory();
      const modeText = selectedIncrement === "calendar-days"
        ? "Showing the latest dashboard snapshot for each calendar day."
        : "Showing one point per dashboard snapshot.";
      document.getElementById("incrementSummary").textContent = `${{modeText}} Points: ${{rows.length}}.`;
    }}

    function renderAll() {{
      updateIncrementSummary();
      renderMetricTiles();
      renderSignals();
      renderSparklines();
      renderCompositeChart();
      renderHeatmap();
    }}

    document.getElementById("timeIncrement").addEventListener("change", (event) => {{
      selectedIncrement = event.target.value;
      renderAll();
    }});

    document.getElementById("exportDashboard").addEventListener("click", () => {{
      window.open("{PDF_EXPORT_FILENAME}", "_blank");
    }});

    renderAll();
  </script>
</main>
</body>
</html>
"""


def _write_dashboard_pdf(dashboard_path: Path, pdf_path: Path) -> dict[str, Any]:
    try:
        from playwright.sync_api import sync_playwright
    except Exception as exc:  # pragma: no cover - depends on local optional runtime.
        return {"available": False, "path": str(pdf_path), "error": str(exc)}
    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            page = browser.new_page(viewport={"width": 1440, "height": 1600})
            page.goto(dashboard_path.resolve().as_uri(), wait_until="networkidle")
            page.emulate_media(media="print")
            pdf_path.parent.mkdir(parents=True, exist_ok=True)
            page.pdf(
                path=str(pdf_path),
                format="Letter",
                print_background=True,
                margin={"top": "0.45in", "right": "0.35in", "bottom": "0.45in", "left": "0.35in"},
            )
            browser.close()
    except Exception as exc:
        return {"available": False, "path": str(pdf_path), "error": str(exc)}
    return {"available": True, "path": str(pdf_path), "error": None}


def write_dashboard_and_report(
    project_root: Path,
    dashboard_dir: Path,
    history_path: Path,
    generate_pdf: bool = True,
    seed_historical_backfill: bool = True,
    startup_bridge_maintenance: dict[str, Any] | None = None,
    startup_pruning: dict[str, Any] | None = None,
    role_profile: str | None = None,
    harness_name: str | None = None,
    harness_id: str | None = None,
    role_record_path: Path | None = None,
    fast_hook: bool = False,
) -> dict[str, Any]:
    model = build_startup_model(
        project_root,
        role_profile=role_profile,
        harness_name=harness_name,
        harness_id=harness_id,
        role_record_path=role_record_path,
        fast_hook=fast_hook,
    )
    if startup_bridge_maintenance is not None:
        model["startup_bridge_maintenance"] = startup_bridge_maintenance
    if startup_pruning is not None:
        model["startup_pruning"] = startup_pruning
    dashboard_dir.mkdir(parents=True, exist_ok=True)

    snapshot = _snapshot_from_model(model)
    snapshot_day = str(snapshot.get("generated_at", ""))[:10]
    backfill_history = (
        [
            row
            for row in _historical_agent_red_backfill(project_root)
            if str(row.get("generated_at", ""))[:10] < snapshot_day
        ]
        if seed_historical_backfill
        else []
    )
    history = _write_history(history_path, snapshot, seed_history=backfill_history)

    data_path = dashboard_dir / "dashboard-data.json"
    dashboard_path = project_root / "docs" / "gtkb-dashboard" / "grafana" / "dashboards" / "gtkb-dashboard.json"
    pdf_path = dashboard_dir / PDF_EXPORT_FILENAME
    report_path = dashboard_dir / "session-startup-report.md"
    wrapup_path = dashboard_dir / "session-wrapup-report.md"
    data = {"model": model, "history": history}
    _atomic_write_text(data_path, json.dumps(data, indent=2, sort_keys=True) + "\n")

    dashboard_link = _markdown_url_link(GRAFANA_DASHBOARD_URL)
    report_text = render_report(model, dashboard_link, project_root)
    wrapup_text = render_wrapup_notice(model, dashboard_link)
    _atomic_write_text(report_path, report_text)
    _atomic_write_text(wrapup_path, wrapup_text)
    pdf_export = {"available": False, "path": str(pdf_path), "error": "Static dashboard PDF export is disabled."}

    return {
        "project_root": project_root,
        "model": model,
        "history": history,
        "dashboard_path": dashboard_path,
        "dashboard_url": GRAFANA_DASHBOARD_URL,
        "pdf_path": pdf_path,
        "pdf_export": pdf_export,
        "data_path": data_path,
        "report_path": report_path,
        "report_text": report_text,
        "wrapup_path": wrapup_path,
        "wrapup_text": wrapup_text,
    }


def _emit_hook_context(text: str) -> None:
    print(json.dumps({"additionalContext": text}, ensure_ascii=False))


def _source_file_observation(project_root: Path, relative_path: str, *, required: bool = True) -> dict[str, Any]:
    path = project_root / Path(relative_path)
    if path.is_file():
        modified_at = datetime.fromtimestamp(path.stat().st_mtime, UTC).isoformat().replace("+00:00", "Z")
        status = "present"
    else:
        modified_at = None
        status = "missing"
    return {
        "source": relative_path.replace("\\", "/"),
        "kind": "local_file",
        "required": required,
        "status": status,
        "path": str(path),
        "modified_at": modified_at,
    }


def _source_file_signature(path: Path, *, source: str, required: bool = True) -> dict[str, Any]:
    if not path.is_file():
        return {
            "source": source.replace("\\", "/"),
            "kind": "local_file",
            "required": required,
            "status": "missing",
            "path": str(path),
            "modified_at": None,
            "modified_ns": None,
            "sha256": None,
        }
    stat = path.stat()
    try:
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
    except OSError:
        digest = None
    return {
        "source": source.replace("\\", "/"),
        "kind": "local_file",
        "required": required,
        "status": "present",
        "path": str(path),
        "modified_at": datetime.fromtimestamp(stat.st_mtime, UTC).isoformat().replace("+00:00", "Z"),
        "modified_ns": stat.st_mtime_ns,
        "sha256": digest,
    }


def _startup_freshness_input_signatures(project_root: Path) -> dict[str, Any]:
    role_path = operating_role_path(project_root, prefer_local=False)
    role_source = (
        str(role_path.relative_to(project_root)).replace("\\", "/")
        if role_path.is_relative_to(project_root)
        else str(role_path)
    )
    return {
        "role_assignments": _source_file_signature(role_path, source=role_source),
        "bridge_index": _source_file_signature(project_root / "bridge" / "INDEX.md", source="bridge/INDEX.md"),
    }


def _workflow_inventory_observation(project_root: Path, *, required: bool = True) -> dict[str, Any]:
    workflows_dir = project_root / ".github" / "workflows"
    workflow_files = (
        sorted([*workflows_dir.glob("*.yml"), *workflows_dir.glob("*.yaml")]) if workflows_dir.is_dir() else []
    )
    latest_modified_at = None
    if workflow_files:
        latest_mtime = max(path.stat().st_mtime for path in workflow_files)
        latest_modified_at = datetime.fromtimestamp(latest_mtime, UTC).isoformat().replace("+00:00", "Z")
    return {
        "source": ".github/workflows",
        "kind": "local_directory",
        "required": required,
        "status": "present" if workflow_files else "missing",
        "path": str(workflows_dir),
        "file_count": len(workflow_files),
        "latest_modified_at": latest_modified_at,
    }


def _startup_freshness_metadata(
    *,
    project_root: Path,
    model: dict[str, Any],
    request_started_at: str,
    payload_emitted_at: str,
    report_origin: str,
) -> dict[str, Any]:
    dashboard_intelligence = model.get("dashboard_intelligence", {})
    data_freshness = dashboard_intelligence.get("data_freshness", {})
    infrastructure = model.get("infrastructure", {})
    github = infrastructure.get("testing_service_integrations", {}).get("github", {})
    upgrade_posture = infrastructure.get("gtkb_upgrade_posture", {})
    generated_at = str(model.get("generated_at") or "")
    local_sources = [
        _source_file_observation(project_root, "groundtruth.db"),
        _source_file_observation(project_root, "memory/release-readiness.md"),
        _source_file_observation(project_root, "bridge/INDEX.md"),
        _workflow_inventory_observation(project_root),
    ]
    live_probes = [
        *infrastructure.get("dashboard_reachability", []),
        {
            "source": "GitHub Actions via gh",
            "kind": "live_probe",
            "required": False,
            "status": "queried" if github.get("workflow_runs_available") else "unavailable",
            "queried_at": github.get("queried_at"),
            "detail": github.get("latest_run_source"),
        },
        {
            "source": "GT-KB latest release probe",
            "kind": "live_probe",
            "required": False,
            "status": "queried" if not upgrade_posture.get("latest_release_probe_error") else "unavailable",
            "queried_at": generated_at,
            "detail": upgrade_posture.get("latest_release_tag"),
            "error": upgrade_posture.get("latest_release_probe_error"),
        },
        {
            "source": "GT-KB latest main probe",
            "kind": "live_probe",
            "required": False,
            "status": "queried" if not upgrade_posture.get("latest_main_probe_error") else "unavailable",
            "queried_at": generated_at,
            "detail": upgrade_posture.get("latest_main_sha"),
            "error": upgrade_posture.get("latest_main_probe_error"),
        },
    ]
    required_local_sources_ok = all(
        source.get("status") == "present" for source in local_sources if source.get("required") is True
    )
    generated_after_request = _iso_is_ordered(request_started_at, generated_at)
    emitted_after_generation = _iso_is_ordered(generated_at, payload_emitted_at)
    emitted_after_request = _iso_is_ordered(request_started_at, payload_emitted_at)
    startup_payload_fresh = (
        generated_after_request
        and emitted_after_generation
        and emitted_after_request
        and required_local_sources_ok
        and report_origin == "in_memory_model_render"
    )
    live_probe_gaps = [probe["source"] for probe in live_probes if probe.get("status") != "queried"]
    validation_status = "invalid" if not startup_payload_fresh else "fresh_with_gaps" if live_probe_gaps else "fresh"
    checks = [
        {
            "name": "generated_at_is_not_older_than_request",
            "passed": generated_after_request,
            "detail": f"request_started_at={request_started_at}; generated_at={generated_at}",
        },
        {
            "name": "payload_emitted_after_generation",
            "passed": emitted_after_generation and emitted_after_request,
            "detail": f"generated_at={generated_at}; payload_emitted_at={payload_emitted_at}",
        },
        {
            "name": "required_local_sources_present",
            "passed": required_local_sources_ok,
            "detail": "groundtruth.db, memory/release-readiness.md, bridge/INDEX.md, and .github/workflows must exist for a fresh startup payload.",
        },
        {
            "name": "payload_render_origin_is_in_memory",
            "passed": report_origin == "in_memory_model_render",
            "detail": f"render_origin={report_origin}",
        },
    ]
    return {
        "contract_version": STARTUP_FRESHNESS_CONTRACT_VERSION,
        "request_started_at": request_started_at,
        "generated_at": generated_at,
        "payload_emitted_at": payload_emitted_at,
        "report_origin": report_origin,
        "generation_latency_ms": _iso_elapsed_ms(request_started_at, generated_at),
        "emit_latency_ms": _iso_elapsed_ms(request_started_at, payload_emitted_at),
        "repo": {
            "branch": data_freshness.get("repo_branch"),
            "sha": data_freshness.get("repo_sha"),
            "short_sha": data_freshness.get("repo_short_sha"),
        },
        "freshness_inputs": _startup_freshness_input_signatures(project_root),
        "validation": {
            "status": validation_status,
            "startup_payload_fresh": startup_payload_fresh,
            "live_probe_gap_count": len(live_probe_gaps),
            "live_probe_gaps": live_probe_gaps,
            "checks": checks,
        },
        "required_local_sources": local_sources,
        "live_probes": live_probes,
    }


def _startup_service_context(result: dict[str, Any]) -> str:
    model = result["model"]
    project_root = Path(result["project_root"])
    profile_path = _startup_payload_profile_path(result)
    profile_rel = _display_path(project_root, profile_path)
    report_path = _display_path(project_root, Path(result["report_path"]))
    wrapup_path = _display_path(project_root, Path(result["wrapup_path"]))
    data_path = _display_path(project_root, Path(result["data_path"]))
    dashboard_path = _display_path(project_root, Path(result["dashboard_path"]))
    role = model.get("role") or {}
    tokens = (model.get("metrics") or {}).get("tokens") or {}
    focus_option_count = len(_session_focus_options(model))
    relay_cache_lines = _startup_relay_cache_lines(project_root, _harness_name_for_payload(result))
    top_priority_lines = _compact_top_priority_lines(model)
    startup_instruction_context = [
        "",
        "## Session Startup Instructions",
        "",
        "- Do not relay this section to Mike as user-visible startup content.",
        "- These instructions describe startup handling and operational context; they are not disclosure text.",
        "",
        "### Session Overlay Status (Non-Authoritative)",
        "",
        _render_session_overlay_status(model.get("session_overlay") or {}),
        "",
        "### Fresh-Session Input Semantics",
        "",
        _render_fresh_session_input_semantics(model),
        "",
        "### Codex Operating Resource Map",
        "",
        "- Resource authority: live project files under `E:\\GT-KB` are canonical; session overlays and generated startup/dashboard summaries are routing context only.",
        "- Role authority: resolve `harness-state/harness-identities.json` first, then `harness-state/harness-registry.json` (canonical role registry per Slice 1 retirement; legacy `harness-state/role-assignments.json` mirror is orphan/compat); role records may be list-valued role sets.",
        "- Bridge authority: read `bridge/INDEX.md` directly before bridge queue claims; generated bridge counts are non-authoritative after startup generation.",
        "- Work subject authority: `.claude/session/work-subject.json`; GT-KB infrastructure is default unless owner direction names an application/adopter.",
        "- Knowledge surfaces: use `groundtruth.db` (MemBase), `memory/release-readiness.md`, `.claude/rules/`, `.codex/skills/`, and `docs/gtkb-dashboard/session-startup-report.md` as targeted context sources. Backlog is queried via `gt backlog list`.",
        "- Hook handling: Codex hook `systemMessage` and `additionalContext` are operational instructions; if a hook blocks, read the cited guard/state file and clear stale lifecycle state only through the governed hook path.",
        "- Token consumption: prefer dashboard and index-first reads, then load detailed artifacts only when needed for the selected task.",
        "- Verification defaults: use repository-native commands such as `python -m pytest <target> -q --tb=short`, `python -m ruff check .`, and targeted parity checks before claiming startup/hook changes are fixed.",
    ]
    loyal_opposition_context: list[str] = []
    if _is_loyal_opposition_model(model):
        startup_relay_instruction = (
            "- SessionStart caches the generated Loyal Opposition startup disclosure for later init-keyword rendering. "
            "Do not render it directly from this SessionStart payload; execute bridge review work only when an "
            "init-keyword match or explicit bridge dispatch task makes it applicable."
        )
        loyal_opposition_context = [
            "",
            "## Harness-Only Loyal Opposition Startup Action",
            "",
            "- Do not relay this section to Mike as user-visible startup content.",
            "- Execute these instructions before ordinary task work; they are operational startup requirements, not disclosure text.",
            "",
            _render_loyal_opposition_startup_task(model),
        ]
    else:
        startup_relay_instruction = (
            "- SessionStart caches the generated Prime Builder startup disclosure for later init-keyword rendering. "
            "Do not render it directly from this SessionStart payload or wait for a focus selection unless the "
            "UserPromptSubmit init-keyword matcher returns a match."
        )
    return "\n".join(
        [
            "# GroundTruth-KB Programmatic Startup Payload",
            "",
            f"- Contract: {STARTUP_SERVICE_CONTRACT_VERSION}",
            f"- Payload profile contract: {STARTUP_PAYLOAD_PROFILE_CONTRACT_VERSION}",
            "- Source: `scripts/session_self_initialization.py`",
            f"- Generated: {model['generated_at']}",
            "- Context mode: compact SessionStart routing summary.",
            "- User-visible startup disclosure is generated in `hookSpecificOutput.startupDisclosure`; it is intentionally not embedded in `additionalContext`.",
            startup_relay_instruction,
            "- Do not summarize, paraphrase, shorten, reorder, or omit cached startup-disclosure content when an init-keyword path relays it.",
            "- Preserve every generated heading, bullet, A/B/C/D option, `Evidence`, `Expected work`, and compact full-list label exactly as written in `startupDisclosure`.",
            (
                f"- Prime Builder focus-menu preservation rule: when the startup message contains a session-focus menu, "
                f"the A/B/C recommendations and D full focus list must remain present; the full focus list must include all {focus_option_count} labels in order."
            ),
            "- After SessionStart, the harness's UserPromptSubmit hook routes the first owner message through the init-keyword matcher (per ADR-SESSION-START-INIT-KEYWORD-CONTRACT-001): on match (e.g., `init gtkb`, `init gtkb advisory`), render the startup disclosure and wait for the next message; on no-match, process the prompt as normal task content. The startup disclosure is generated at SessionStart time and cached for lazy injection by the matcher; it is not unconditionally relayed.",
            "- Only an init-keyword match relays startup disclosure; a non-matching first owner message is ordinary task input and may be mapped normally.",
            "- When the init-keyword path renders cached startup content, do not replace the startup message with a shorter final answer after rendering it.",
            "- The AI harness is not responsible for composing role, mode, bridge, process, or focus content during startup.",
            "",
            "## Compact Startup Routing Facts",
            "",
            f"- Role being assumed: {role.get('assumed_role', 'unidentified')}",
            f"- Role mapping source: {role.get('role_mapping_source', 'unidentified')}; legacy compatibility surface: harness-state/role-assignments.json.",
            f"- Harness self-identification: {role.get('harness_id', 'unidentified')}",
            f"- Harness identity source: {role.get('harness_identity_source', 'unidentified')}",
            f"- Work subject: {model.get('current_work_subject') or 'gtkb_infrastructure/default'}",
            f"- Dashboard URL: {result['dashboard_url']}",
            f"- Dashboard data: `{data_path}`",
            f"- Dashboard JSON: `{dashboard_path}`",
            f"- Startup report path: `{report_path}`",
            f"- Wrap-up report path: `{wrapup_path}`",
            f"- Payload profile path: `{profile_rel}`",
            f"- Token measurement status: {tokens.get('measurement_status', 'unknown')}; reducing startup token consumption now uses compact `additionalContext` plus demand-loaded expansion paths.",
            "",
            "### Top Priority Actions",
            "",
            *top_priority_lines,
            "",
            "### Startup Disclosure Cache Paths",
            "",
            *relay_cache_lines,
            *startup_instruction_context,
            *loyal_opposition_context,
        ]
    )


def _startup_disclosure(result: dict[str, Any]) -> str:
    return str(result["report_text"])


def _display_path(project_root: Path, path: Path) -> str:
    try:
        return path.relative_to(project_root).as_posix()
    except ValueError:
        return str(path)


def _harness_name_for_payload(result: dict[str, Any]) -> str:
    role = (result.get("model") or {}).get("role") or {}
    harness_name = _normalize_harness_name(str(role.get("harness_name") or ""))
    if harness_name:
        return harness_name
    harness_id = str(role.get("harness_id") or "").strip()
    for name, expected_id in DEFAULT_HARNESS_IDS.items():
        if harness_id == expected_id:
            return name
    return _resolved_harness_name(None) or "claude"


def _startup_payload_profile_path(result: dict[str, Any]) -> Path:
    project_root = Path(result["project_root"])
    harness = re.sub(r"[^a-z0-9_-]+", "-", _harness_name_for_payload(result).lower()).strip("-") or "unknown"
    return project_root / STARTUP_PAYLOAD_PROFILE_DIR / f"last-{harness}.json"


def _startup_relay_cache_lines(project_root: Path, harness_name: str) -> list[str]:
    if harness_name == "codex":
        out_dir = project_root / ".codex" / "gtkb-hooks"
    elif harness_name == "claude":
        out_dir = project_root / ".claude" / "hooks"
    else:
        out_dir = project_root / "harness-state" / harness_name
    return [
        f"- Default cache: `{_display_path(project_root, out_dir / 'last-user-visible-startup.md')}`",
        f"- Prime Builder cache: `{_display_path(project_root, out_dir / 'last-user-visible-startup-pb.md')}`",
        f"- Loyal Opposition cache: `{_display_path(project_root, out_dir / 'last-user-visible-startup-lo.md')}`",
    ]


def _compact_top_priority_lines(model: dict[str, Any]) -> list[str]:
    actions = model.get("top_priority_actions") or []
    if not actions:
        return ["- None surfaced by the current startup model."]
    lines: list[str] = []
    for action in actions[:3]:
        identifier = str(action.get("id") or "unknown")
        title = str(action.get("title") or "untitled")
        priority = str(action.get("priority") or "none")
        lines.append(f"- {identifier}: {title} (priority: {priority})")
    return lines


def _text_payload_metrics(text: str) -> dict[str, Any]:
    encoded = text.encode("utf-8")
    return {
        "utf8_bytes": len(encoded),
        "line_count": 0 if text == "" else text.count("\n") + 1,
        "character_count": len(text),
        "rough_token_estimate": 0 if text == "" else (len(text) + 3) // 4,
        "sha256": hashlib.sha256(encoded).hexdigest(),
    }


def _startup_payload_profile(
    result: dict[str, Any],
    *,
    payload_emitted_at: str,
    additional_context: str,
    startup_disclosure: str,
) -> dict[str, Any]:
    project_root = Path(result["project_root"])
    profile_path = _startup_payload_profile_path(result)
    model = result["model"]
    role = model.get("role") or {}
    return {
        "contract_version": STARTUP_PAYLOAD_PROFILE_CONTRACT_VERSION,
        "generated_at": model.get("generated_at"),
        "payload_emitted_at": payload_emitted_at,
        "harness_name": _harness_name_for_payload(result),
        "harness_id": role.get("harness_id"),
        "role_profile": model.get("role_profile"),
        "profile_path": _display_path(project_root, profile_path),
        "sections": {
            "additionalContext": _text_payload_metrics(additional_context),
            "startupDisclosure": _text_payload_metrics(startup_disclosure),
        },
    }


def _write_startup_payload_profile(result: dict[str, Any], profile: dict[str, Any]) -> None:
    path = _startup_payload_profile_path(result)
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        _atomic_write_text(path, json.dumps(profile, ensure_ascii=True, indent=2, sort_keys=True) + "\n")
    except OSError:
        pass


def _emit_startup_service_payload(
    result: dict[str, Any],
    *,
    request_started_at: str,
) -> None:
    payload_emitted_at = _utc_now_iso()
    startup_freshness = _startup_freshness_metadata(
        project_root=result["project_root"],
        model=result["model"],
        request_started_at=request_started_at,
        payload_emitted_at=payload_emitted_at,
        report_origin="in_memory_model_render",
    )
    # Per Slice A of GTKB-MEMBASE-EFFECTIVE-USE-RECOVERY (bridge -006 GO):
    # write the per-session timestamp lower bound that the spec-event-surfacer
    # hook reads. Without this file the surfacer falls back to now() - 1 hour
    # which is correct but emits a stderr warning.
    _write_session_start_json(
        project_root=Path(result["project_root"]),
        request_started_at=request_started_at,
        harness=_harness_name_for_payload(result),
    )
    additional_context = _startup_service_context(result)
    startup_disclosure = _startup_disclosure(result)
    payload_profile = _startup_payload_profile(
        result,
        payload_emitted_at=payload_emitted_at,
        additional_context=additional_context,
        startup_disclosure=startup_disclosure,
    )
    # Fail-soft profile write (writer swallows OSError); on-disk profile is the
    # generated runtime evidence, the in-payload profile is the authoritative copy.
    _write_startup_payload_profile(result, payload_profile)
    payload = {
        "hookSpecificOutput": {
            "hookEventName": "SessionStart",
            "additionalContext": additional_context,
            "startupDisclosure": startup_disclosure,
            "startupFreshness": startup_freshness,
            "startupPayloadProfile": payload_profile,
        }
    }
    payload_text = json.dumps(payload, ensure_ascii=False)
    print(payload_text)


def _write_session_start_json(
    *,
    project_root: Path,
    request_started_at: str,
    harness: str,
) -> None:
    """Write ``.claude/session/session-start.json`` for the spec-event-surfacer.

    Per bridge ``gtkb-membase-effective-use-recovery-slice-a-event-surfacer-
    2026-04-29-005`` REVISED-2 §1.3 + Codex GO at -006: the surfacer hook
    reads ``session_started_at`` from this file as the lower bound for
    "in-session" spec rows. Atomic-rename pattern; graceful degradation on
    filesystem errors (the surfacer's fallback to ``now() - 1 hour`` is the
    safety net per F2 fix).
    """
    target = project_root / ".claude" / "session" / "session-start.json"
    payload = {
        "session_started_at": request_started_at,
        "session_id": os.environ.get("GTKB_STARTUP_GUARD_ID", request_started_at),
        "harness": harness,
    }
    try:
        target.parent.mkdir(parents=True, exist_ok=True)
        tmp = target.with_name(f"{target.name}.tmp.{os.getpid()}")
        tmp.write_text(json.dumps(payload), encoding="utf-8")
        os.replace(tmp, target)
    except OSError:
        # Graceful degradation: surfacer's fallback handles missing file.
        pass


def _emit_no_hook_context() -> None:
    print("{}")


def _utc_now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _default_lifecycle_guard_path(project_root: Path, *, harness_name: str | None = None) -> Path:
    override = os.environ.get("GTKB_LIFECYCLE_GUARD_PATH")
    if override:
        return _normalized_path(Path(override))
    resolved_harness_name = _resolved_harness_name(harness_name)
    if resolved_harness_name:
        return _normalized_path(HARNESS_LIFECYCLE_GUARDS[resolved_harness_name])
    return project_root / LIFECYCLE_GUARD_RELATIVE_PATH


def _read_lifecycle_guard(path: Path) -> dict[str, Any]:
    try:
        raw = json.loads(path.read_text(encoding="utf-8-sig"))
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return {}
    return raw if isinstance(raw, dict) else {}


def _write_lifecycle_guard(path: Path, state: dict[str, Any]) -> None:
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    except OSError:
        pass


def _startup_guard_id() -> str:
    return os.environ.get("GTKB_STARTUP_GUARD_ID") or _utc_now_iso()


def _arm_startup_interaction_guard(
    path: Path,
    guard_id: str,
    *,
    suppress_next_wrapup: bool,
    current_subject: str | None = None,
) -> None:
    state = _read_lifecycle_guard(path)
    if (
        state.get("startup_guard_id") == guard_id
        and state.get("discard_next_user_prompt") is True
        and state.get("startup_response_pending") is False
        and state.get("suppress_next_wrapup") is suppress_next_wrapup
        and (current_subject is None or state.get("current_subject") == current_subject)
    ):
        return

    update: dict[str, Any] = {
        "armed_at": _utc_now_iso(),
        "armed_reason": "startup_first_owner_prompt_must_be_discarded",
        "discard_next_user_prompt": True,
        "startup_prompt_discarded": False,
        "startup_response_pending": False,
        "first_wrapup_suppressed": False,
        "startup_guard_id": guard_id,
        "suppress_next_wrapup": suppress_next_wrapup,
    }
    # Persist the active harness's current work subject so the counterpart
    # harness's detect_counterpart_state() can detect divergence against a
    # live-populated durable source (Phase 7 Â§E live-wiring, per bridge -012).
    if current_subject is not None:
        update["current_subject"] = current_subject
    state.update(update)
    _write_lifecycle_guard(path, state)


def _consume_startup_wrapup_guard(path: Path) -> bool:
    state = _read_lifecycle_guard(path)
    if state.get("suppress_next_wrapup") is not True:
        return False

    state.update(
        {
            "first_wrapup_suppressed": True,
            "last_suppressed_at": _utc_now_iso(),
            "last_suppressed_reason": "startup_focus_input_pending",
            "suppress_next_wrapup": False,
            "suppressed_count": int(state.get("suppressed_count", 0) or 0) + 1,
        }
    )
    _write_lifecycle_guard(path, state)
    return True


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", type=Path, default=PROJECT_ROOT)
    # Per bridge/generator-hardening-001-003.md Â§4.6: dashboard-dir and
    # history-path default to None; main() derives them from the resolved
    # --project-root post-parse. This means a caller passing only
    # --project-root <child-root> gets all output under <child-root>, not
    # under the canonical PROJECT_ROOT.
    parser.add_argument(
        "--dashboard-dir",
        type=Path,
        default=None,
        help="Default: <project-root>/docs/gtkb-dashboard",
    )
    parser.add_argument(
        "--history-path",
        type=Path,
        default=None,
        help="Default: <project-root>/memory/gtkb-dashboard-history.json",
    )
    parser.add_argument("--emit-report", action="store_true", help="Print the startup report after writing it.")
    parser.add_argument(
        "--emit-startup-service-payload",
        action="store_true",
        help="Print the full Codex SessionStart payload generated by the startup service.",
    )
    parser.add_argument(
        "--emit-wrapup", action="store_true", help="Print the proactive wrap-up report after writing it."
    )
    parser.add_argument(
        "--force-wrapup",
        action="store_true",
        help="Bypass the startup focus guard and emit the wrap-up report immediately.",
    )
    parser.add_argument(
        "--lifecycle-guard-path",
        type=Path,
        default=None,
        help="Override the lifecycle guard state path for tests or alternate harnesses.",
    )
    parser.add_argument(
        "--role-record-path",
        type=Path,
        default=None,
        help="Deprecated alias: override the single durable role-assignment map path.",
    )
    parser.add_argument(
        "--role-assignment-path",
        type=Path,
        default=None,
        help="Override the single durable role-assignment map path.",
    )
    parser.add_argument(
        "--user-preferences-path",
        type=Path,
        default=None,
        help=(
            "Override the user startup preferences JSON path. Mirrors "
            "--role-record-path / --lifecycle-guard-path. Used by the Slice 11 "
            "audit-hook lane to thread a sandbox-relative preferences path so "
            "the legacy generator does not read the canonical "
            "harness-state/codex/session-startup-"
            "preferences.json from outside its sandbox. Per "
            "bridge/harness-state-preferences-path-cli-2026-04-28-002.md "
            "Codex GO. Implemented as a setdefault env-var bridge so the "
            "existing GTKB_STARTUP_PREFERENCES_PATH override remains "
            "highest-precedence."
        ),
    )
    parser.add_argument(
        "--harness-name",
        choices=sorted(DEFAULT_HARNESS_IDS),
        default=None,
        help="Select harness-local lifecycle state paths and default harness ID.",
    )
    parser.add_argument(
        "--harness-id",
        default=None,
        help="Assert the durable installation ID for this harness; persistent identity is loaded from harness-state/harness-identities.json.",
    )
    parser.add_argument("--json", action="store_true", help="Print machine-readable output paths and current model.")
    parser.add_argument(
        "--role-profile",
        choices=sorted(ROLE_PROFILES),
        default=None,
        help=(
            "Diagnostic role mapping override for non-startup output. "
            "--emit-report always discovers the startup role from the resolved durable operating-role record."
        ),
    )
    parser.add_argument(
        "--fast-hook",
        action="store_true",
        help=(
            "Use the lifecycle-hook budget path: skip historical backfill, PDF export, and startup bridge maintenance."
        ),
    )
    parser.add_argument(
        "--skip-bridge-maintenance",
        action="store_true",
        help="Skip startup archival/pruning of VERIFIED bridge index entries.",
    )
    args = parser.parse_args(argv)
    if not args.project_root.is_absolute():
        # Per bridge/session-self-init-project-root-path-doubling-fix-2026-04-27-004.md (GO):
        # drive-relative inputs like 'E:GT-KB' (no slash) silently combine with
        # the drive's current directory via Path.resolve(), producing doubled
        # paths (e.g., E:\GT-KB\GT-KB). Reject them up front.
        raise SystemExit(
            f"--project-root must be an absolute path; got {args.project_root!r}. "
            f"On Windows, drive-relative paths like 'E:GT-KB' (no slash after the "
            f"colon) are silently combined with the drive's current directory by "
            f"Path.resolve(), which can produce a doubled path (e.g., "
            f"E:\\GT-KB\\GT-KB). Pass an absolute path: "
            f"e.g., 'E:\\\\GT-KB' (escaped backslash) or 'E:/GT-KB' (forward slashes)."
        )
    project_root = args.project_root.resolve()
    # Slice 1 of gtkb-operating-mode-transaction-001: drain any pending
    # mode-switch transactions BEFORE topology derivation so a deferred
    # role/topology change takes effect for this session's reported state.
    # Fail-soft per design: failures do not abort startup.
    try:
        from groundtruth_kb.mode_switch.pending import apply_pending as _apply_pending

        _apply_pending(project_root)
    except Exception:  # noqa: BLE001 - fail-soft per spec acceptance criterion #6
        pass
    if args.user_preferences_path is not None:
        # Per bridge/harness-state-preferences-path-cli-2026-04-28-002.md Codex
        # GO Candidate B: bridge the CLI arg into the existing
        # GTKB_STARTUP_PREFERENCES_PATH env-var override channel so downstream
        # readers (_user_startup_preferences_path) honor it without signature
        # changes. setdefault preserves the precedence order required by GO
        # condition 2: existing env var > CLI arg > canonical default.
        os.environ.setdefault(
            "GTKB_STARTUP_PREFERENCES_PATH",
            str(args.user_preferences_path.resolve()),
        )
    startup_emit_requested = args.emit_report or args.emit_startup_service_payload
    startup_requested_at = os.environ.get("GTKB_STARTUP_REQUESTED_AT") if args.emit_startup_service_payload else None
    if _parse_iso8601(startup_requested_at) is None:
        startup_requested_at = _utc_now_iso()
    role_record_path = (
        args.role_assignment_path.resolve()
        if args.role_assignment_path is not None
        else (args.role_record_path.resolve() if args.role_record_path is not None else None)
    )
    role_profile = (
        discover_role_profile(
            project_root,
            harness_name=args.harness_name,
            harness_id=args.harness_id,
            role_record_path=role_record_path,
        )
        if startup_emit_requested
        else _role_profile_or_discovered(
            project_root,
            args.role_profile,
            harness_name=args.harness_name,
            harness_id=args.harness_id,
            role_record_path=role_record_path,
        )
    )
    lifecycle_guard_path = (
        args.lifecycle_guard_path.resolve()
        if args.lifecycle_guard_path is not None
        else _default_lifecycle_guard_path(project_root, harness_name=args.harness_name)
    )

    if startup_emit_requested:
        try:
            current_subject_for_guard: str | None = (
                str(startup_focus_snapshot(project_root).get("current_focus") or "") or None
            )
        except Exception:
            current_subject_for_guard = None
        _arm_startup_interaction_guard(
            lifecycle_guard_path,
            _startup_guard_id(),
            suppress_next_wrapup=role_profile != "loyal-opposition",
            current_subject=current_subject_for_guard,
        )

    if args.emit_wrapup and not args.force_wrapup and _consume_startup_wrapup_guard(lifecycle_guard_path):
        _emit_no_hook_context()
        return 0

    # Per bridge/generator-hardening-001-003.md Â§4.6: derive output paths
    # from resolved project_root when CLI args are omitted, so a caller
    # passing only --project-root <child> gets all output under <child>.
    dashboard_dir = (
        args.dashboard_dir.resolve() if args.dashboard_dir is not None else project_root / "docs" / "gtkb-dashboard"
    )
    history_path = (
        args.history_path.resolve()
        if args.history_path is not None
        else project_root / "memory" / "gtkb-dashboard-history.json"
    )
    bridge_maintenance = None
    if startup_emit_requested and not args.skip_bridge_maintenance and not args.fast_hook:
        bridge_maintenance = _run_verified_bridge_startup_maintenance(project_root)
    startup_pruning = _startup_pruning_scan(project_root, bridge_maintenance) if startup_emit_requested else None

    # Per bridge/generator-hardening-001-003.md Â§4.6: derive output paths
    # from resolved project_root when CLI args are omitted, so a caller
    # passing only --project-root <child> gets all output under <child>.
    dashboard_dir = (
        args.dashboard_dir.resolve() if args.dashboard_dir is not None else project_root / "docs" / "gtkb-dashboard"
    )
    history_path = (
        args.history_path.resolve()
        if args.history_path is not None
        else project_root / "memory" / "gtkb-dashboard-history.json"
    )
    result = write_dashboard_and_report(
        project_root=project_root,
        dashboard_dir=dashboard_dir,
        history_path=history_path,
        generate_pdf=not args.fast_hook,
        seed_historical_backfill=not args.fast_hook,
        startup_bridge_maintenance=bridge_maintenance,
        startup_pruning=startup_pruning,
        role_profile=role_profile,
        harness_name=args.harness_name,
        harness_id=args.harness_id,
        role_record_path=role_record_path,
        fast_hook=args.fast_hook,
    )
    if startup_emit_requested:
        _maybe_open_dashboard_on_session_start(result["dashboard_url"])
    if args.json:
        printable = {
            "dashboard_path": str(result["dashboard_path"]),
            "dashboard_url": result["dashboard_url"],
            "data_path": str(result["data_path"]),
            "pdf_path": str(result["pdf_path"]),
            "pdf_export": result["pdf_export"],
            "report_path": str(result["report_path"]),
            "wrapup_path": str(result["wrapup_path"]),
            "model": result["model"],
        }
        print(json.dumps(printable, indent=2, sort_keys=True))
    elif args.emit_startup_service_payload:
        _emit_startup_service_payload(
            result,
            request_started_at=startup_requested_at,
        )
    elif args.emit_report:
        _emit_hook_context(str(result["report_text"]))
    elif args.emit_wrapup:
        _emit_hook_context(str(result["wrapup_text"]))
    else:
        print(f"Dashboard: {result['dashboard_url']}")
        print(
            f"PDF export: {result['pdf_path']} ({'available' if result['pdf_export']['available'] else 'not generated'})"
        )
        print(f"Startup report: {result['report_path']}")
        print(f"Wrap-up report: {result['wrapup_path']}")
        print("Session focus options:")
        for index, option in enumerate(_session_focus_options(result["model"]), start=1):
            print(f"{index}. {option['label']}: {option['prompt']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
