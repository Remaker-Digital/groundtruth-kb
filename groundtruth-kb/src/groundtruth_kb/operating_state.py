"""Deterministic local operating-state collection for GroundTruth KB."""

from __future__ import annotations

import json
import sqlite3
import time
import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from groundtruth_kb import __version__
from groundtruth_kb import db as _db_module
from groundtruth_kb.bridge.status_driver import collect_bridge_status
from groundtruth_kb.config import GTConfig

STATUS_ORDER = {"PASS": 0, "UNKNOWN": 1, "WARN": 2, "FAIL": 3}
COMPONENTS = (
    "project",
    "db",
    "chroma",
    "bridge",
    "bridge-dispatch",
    "dashboard",
    "hooks",
    "resource-registry",
    "system-interface-map",
    "startup",
)


@dataclass(frozen=True)
class OperatingStateComponent:
    """A single deterministic operating-state probe result."""

    name: str
    status: str
    detail: str
    source: str
    duration_ms: float
    evidence: dict[str, Any]

    def to_json_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "status": self.status,
            "detail": self.detail,
            "source": self.source,
            "duration_ms": round(self.duration_ms, 3),
            "evidence": self.evidence,
        }


@dataclass(frozen=True)
class OperatingState:
    """Stable JSON envelope for local operating-state output."""

    schema_version: int
    package_version: str
    captured_at: str
    project_root: Path
    startup: bool
    overall_status: str
    components: tuple[OperatingStateComponent, ...]

    def to_json_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "package_version": self.package_version,
            "captured_at": self.captured_at,
            "project_root": str(self.project_root),
            "startup": self.startup,
            "overall_status": self.overall_status,
            "components": [component.to_json_dict() for component in self.components],
        }


def collect_operating_state(
    project_root: Path | None = None,
    *,
    config: GTConfig | None = None,
    startup: bool = False,
    components: tuple[str, ...] | None = None,
) -> OperatingState:
    """Collect deterministic status for a local GT-KB project."""
    if config is None:
        config = GTConfig.load(None)
    root = (project_root or config.project_root).resolve()
    _reject_archive_path(root)

    selected = components or COMPONENTS
    unknown = sorted(set(selected) - set(COMPONENTS))
    if unknown:
        allowed = ", ".join(COMPONENTS)
        raise ValueError(f"unknown status component(s): {unknown}; expected one of: {allowed}")

    probe_map = {
        "project": lambda: _probe_project(root, config),
        "db": lambda: _probe_db(root, config, quick=startup),
        "chroma": lambda: _probe_chroma(root, config),
        "bridge": lambda: _probe_bridge(root),
        "bridge-dispatch": lambda: _probe_bridge_dispatch(root),
        "dashboard": lambda: _probe_dashboard(root),
        "hooks": lambda: _probe_hooks(root),
        "resource-registry": lambda: _probe_resource_registry(root),
        "system-interface-map": lambda: _probe_system_interface_map(root),
        "startup": lambda: _probe_startup(root),
    }
    collected = tuple(_timed_probe(name, probe_map[name]) for name in selected)
    overall = _overall_status(collected)
    return OperatingState(
        schema_version=1,
        package_version=__version__,
        captured_at=_now(),
        project_root=root,
        startup=startup,
        overall_status=overall,
        components=collected,
    )


def format_operating_state_text(state: OperatingState) -> str:
    """Render a compact text status report."""
    lines = [
        f"GroundTruth KB operating state: {state.overall_status}",
        f"Project root: {state.project_root}",
        f"Captured at: {state.captured_at}",
        "",
        "Components:",
    ]
    for component in state.components:
        lines.append(f"- {component.status} {component.name}: {component.detail}")
    return "\n".join(lines)


def format_startup_operating_state(state: OperatingState) -> str:
    """Render startup-safe text from the same collector payload."""
    lines = [
        "Operating State",
        f"- Overall: {state.overall_status}",
        f"- Project root: {state.project_root}",
    ]
    for component in state.components:
        lines.append(f"- {component.name}: {component.status} - {component.detail}")
    return "\n".join(lines)


def _timed_probe(name: str, probe: Any) -> OperatingStateComponent:
    start = time.perf_counter()
    try:
        status, detail, source, evidence = probe()
    except Exception as exc:  # intentional-catch: status must degrade instead of crashing startup
        status, detail, source, evidence = "FAIL", f"{type(exc).__name__}: {exc}", "", {}
    duration_ms = (time.perf_counter() - start) * 1000
    return OperatingStateComponent(
        name=name,
        status=status,
        detail=detail,
        source=source,
        duration_ms=duration_ms,
        evidence=evidence,
    )


def _overall_status(components: tuple[OperatingStateComponent, ...]) -> str:
    if not components:
        return "UNKNOWN"
    return max((component.status for component in components), key=lambda status: STATUS_ORDER[status])


def _reject_archive_path(path: Path) -> None:
    normalized = str(path).replace("/", "\\").lower()
    if "\\claude-playground" in normalized or normalized.endswith("\\claude-playground"):
        raise ValueError(f"{path} is an archive path and must not be treated as live GT-KB state")


def _probe_project(root: Path, config: GTConfig) -> tuple[str, str, str, dict[str, Any]]:
    config_path = root / "groundtruth.toml"
    if not root.exists():
        return "FAIL", "project root does not exist", str(root), {}
    if not config_path.exists():
        return "WARN", "groundtruth.toml not found at project root", str(config_path), {}
    return (
        "PASS",
        "project root and groundtruth.toml found",
        str(config_path),
        {"app_title": config.app_title, "project_root": str(root)},
    )


def _probe_db(root: Path, config: GTConfig, *, quick: bool = False) -> tuple[str, str, str, dict[str, Any]]:
    db_path = config.db_path.resolve()
    if not _is_relative_to(db_path, root):
        return "FAIL", "configured database path is outside project root", str(db_path), {}
    if not db_path.exists():
        return "WARN", "groundtruth.db is missing", str(db_path), {}
    try:
        with sqlite3.connect(f"file:{db_path}?mode=ro", uri=True, timeout=2.0) as conn:
            if quick:
                conn.execute("SELECT 1").fetchone()
                return (
                    "PASS",
                    "SQLite database readable (startup quick check)",
                    str(db_path),
                    {"quick_check": True},
                )
            integrity = conn.execute("PRAGMA integrity_check").fetchone()[0]
    except sqlite3.Error as exc:
        return "FAIL", f"SQLite unavailable: {exc}", str(db_path), {}
    if integrity != "ok":
        return "FAIL", f"SQLite integrity_check={integrity}", str(db_path), {"integrity_check": integrity}
    return "PASS", "SQLite database readable and integrity_check ok", str(db_path), {"integrity_check": integrity}


def _probe_chroma(root: Path, config: GTConfig) -> tuple[str, str, str, dict[str, Any]]:
    chroma_path = (config.chroma_path or root / ".groundtruth-chroma").resolve()
    if not _is_relative_to(chroma_path, root):
        return "FAIL", "configured ChromaDB path is outside project root", str(chroma_path), {}
    if not _db_module.HAS_CHROMADB:
        return "UNKNOWN", "ChromaDB optional dependency is not installed", str(chroma_path), {}
    if not chroma_path.exists():
        return "UNKNOWN", "ChromaDB cache is absent and can be regenerated when needed", str(chroma_path), {}
    sqlite_file = chroma_path / "chroma.sqlite3"
    if sqlite_file.exists():
        return "PASS", "ChromaDB cache directory exists", str(chroma_path), {"sqlite": str(sqlite_file)}
    return "WARN", "ChromaDB cache directory exists without chroma.sqlite3", str(chroma_path), {}


def _probe_bridge(root: Path) -> tuple[str, str, str, dict[str, Any]]:
    bridge_dir = root / "bridge"
    if not bridge_dir.exists():
        return "UNKNOWN", "bridge directory not found", str(bridge_dir), {}
    snapshot = collect_bridge_status(root)
    queue = snapshot.queue
    status = "WARN" if queue.parse_error_count else "PASS"
    return (
        status,
        (
            f"{queue.threads} bridge thread(s); Prime actionable={len(queue.prime_actionable)}; "
            f"Loyal Opposition actionable={len(queue.loyal_opposition_actionable)}"
        ),
        str(bridge_dir),
        queue.to_json_dict(top_n=10),
    )


def _probe_bridge_dispatch(root: Path) -> tuple[str, str, str, dict[str, Any]]:
    """Cross-harness event-driven trigger dispatch-state probe.

    Replaces the retired smart-poller probe (Slice 4, 2026-05-09). Reads
    ``.gtkb-state/bridge-poller/dispatch-state.json`` written by
    ``scripts/cross_harness_bridge_trigger.py`` on each trigger fire.
    """
    trigger_script = root / "scripts" / "cross_harness_bridge_trigger.py"

    if not trigger_script.exists():
        return "UNKNOWN", "cross-harness-trigger script not found", str(trigger_script), {}
    snapshot = collect_bridge_status(root).automation
    dispatch_state = snapshot.dispatch_state
    default_dispatch_state_path = str(root / ".gtkb-state" / "bridge-poller" / "dispatch-state.json")
    dispatch_state_path = dispatch_state.get("path", default_dispatch_state_path)
    if not dispatch_state.get("exists"):
        return (
            "UNKNOWN",
            "dispatch-state.json not yet written by the trigger",
            dispatch_state_path,
            snapshot.to_json_dict(),
        )
    if not dispatch_state.get("parseable"):
        return "FAIL", "dispatch-state.json unreadable", dispatch_state_path, snapshot.to_json_dict()

    hook_values = snapshot.hook_registrations.values()
    hooks_registered = all(
        hook.get("cross_harness_trigger_registered") and hook.get("active_session_heartbeat_registered")
        for hook in hook_values
        if hook.get("exists")
    )
    status = "PASS" if hooks_registered else "WARN"
    retired_count = len(snapshot.system_inventory.get("retired_systems", []))
    external_count = len(snapshot.system_inventory.get("external_thread_automations", []))
    detail = (
        f"{dispatch_state.get('recipient_count', 0)} dispatch recipient(s) tracked; "
        f"cross-harness trigger registered; retired systems={retired_count}; "
        f"external thread automations={external_count}"
    )
    if not hooks_registered:
        detail += "; hook registration incomplete"
    return status, detail, dispatch_state_path, snapshot.to_json_dict()


def _probe_dashboard(root: Path) -> tuple[str, str, str, dict[str, Any]]:
    dashboard_db = root / ".groundtruth" / "dashboard" / "gtkb-dashboard.sqlite"
    if not dashboard_db.exists():
        return "UNKNOWN", "dashboard SQLite database not generated", str(dashboard_db), {}
    try:
        with sqlite3.connect(f"file:{dashboard_db}?mode=ro", uri=True, timeout=2.0) as conn:
            table_count = conn.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table'").fetchone()[0]
    except sqlite3.Error as exc:
        return "FAIL", f"dashboard SQLite unavailable: {exc}", str(dashboard_db), {}
    return "PASS", "dashboard SQLite database readable", str(dashboard_db), {"tables": table_count}


def _probe_hooks(root: Path) -> tuple[str, str, str, dict[str, Any]]:
    settings = root / ".claude" / "settings.json"
    rules = root / ".claude" / "rules"
    if not settings.exists() and not rules.exists():
        return "UNKNOWN", "Claude hook/rule files not found", str(root / ".claude"), {}
    if settings.exists():
        try:
            json.loads(settings.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            return "FAIL", f".claude/settings.json is invalid JSON: {exc}", str(settings), {}
    return "PASS", "hook/rule surface is readable", str(root / ".claude"), {"settings_exists": settings.exists()}


def _probe_resource_registry(root: Path) -> tuple[str, str, str, dict[str, Any]]:
    registry_path = root / "config" / "agent-control" / "project-resource-aliases.toml"
    pointer_path = root / ".claude" / "rules" / "project-resource-aliases.toml"
    if not registry_path.exists():
        return "UNKNOWN", "project resource alias registry not found", str(registry_path), {}
    try:
        with registry_path.open("rb") as handle:
            registry = tomllib.load(handle)
    except (OSError, tomllib.TOMLDecodeError) as exc:
        return "FAIL", f"resource registry is unreadable: {exc}", str(registry_path), {}

    resources = registry.get("resources", [])
    if not isinstance(resources, list) or not resources:
        return "FAIL", "resource registry has no resources", str(registry_path), {}
    unverified = [
        str(row.get("id"))
        for row in resources
        if isinstance(row, dict) and str(row.get("status") or "") == "canonical_unverified_url"
    ]
    separate = [
        str(row.get("id"))
        for row in resources
        if isinstance(row, dict) and str(row.get("status") or "").startswith("separate_project")
    ]
    pointer_status = "missing"
    if pointer_path.exists():
        try:
            with pointer_path.open("rb") as handle:
                pointer = tomllib.load(handle)
            pointer_status = (
                "delegated"
                if pointer.get("registry_path") == "config/agent-control/project-resource-aliases.toml"
                and "resources" not in pointer
                else "invalid"
            )
        except (OSError, tomllib.TOMLDecodeError):
            pointer_status = "invalid"

    status = "FAIL" if pointer_status == "invalid" else "WARN" if unverified else "PASS"
    detail = (
        f"{len(resources)} resource(s); unverified canonical={len(unverified)}; "
        f"separate-project={len(separate)}; pointer={pointer_status}"
    )
    return (
        status,
        detail,
        str(registry_path),
        {
            "resources": len(resources),
            "unverified_canonical": unverified,
            "separate_project": len(separate),
            "pointer_status": pointer_status,
        },
    )


def _probe_system_interface_map(root: Path) -> tuple[str, str, str, dict[str, Any]]:
    map_path = root / "config" / "agent-control" / "system-interface-map.toml"
    if not map_path.exists():
        return "UNKNOWN", "system interface map not found", str(map_path), {}
    try:
        with map_path.open("rb") as handle:
            system_map = tomllib.load(handle)
    except (OSError, tomllib.TOMLDecodeError) as exc:
        return "FAIL", f"system interface map is unreadable: {exc}", str(map_path), {}
    systems = system_map.get("systems", [])
    if not isinstance(systems, list) or not systems:
        return "FAIL", "system interface map has no systems", str(map_path), {}
    companion = root / str(system_map.get("human_companion") or "")
    backlog = next((row for row in systems if isinstance(row, dict) and row.get("id") == "backlog"), None)
    backlog_text = (
        " ".join(str(backlog.get(field) or "") for field in ("authoritative_source", "read_method", "harness_caveats"))
        if backlog
        else ""
    )
    backlog_ok = backlog is not None and all(
        token in backlog_text for token in ("current_work_items", "work_items", "versioned bridge")
    )
    status = "PASS" if companion.exists() and backlog_ok else "WARN"
    companion_state = "present" if companion.exists() else "missing"
    backlog_state = "ok" if backlog_ok else "incomplete"
    detail = f"{len(systems)} system(s); companion={companion_state}; backlog_case={backlog_state}"
    return (
        status,
        detail,
        str(map_path),
        {
            "systems": len(systems),
            "human_companion": str(companion),
            "human_companion_exists": companion.exists(),
            "first_reconciliation_case": "backlog",
            "backlog_case": "ok" if backlog_ok else "incomplete",
        },
    )


def _probe_startup(root: Path) -> tuple[str, str, str, dict[str, Any]]:
    report = root / "docs" / "gtkb-dashboard" / "session-startup-report.md"
    if not report.exists():
        return "UNKNOWN", "session startup report not generated", str(report), {}
    size = report.stat().st_size
    if size == 0:
        return "WARN", "session startup report is empty", str(report), {"bytes": size}
    return "PASS", "session startup report exists", str(report), {"bytes": size}


def _latest_bridge_statuses(index: Path) -> dict[str, str]:
    statuses: dict[str, str] = {}
    current: str | None = None
    for raw_line in index.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if line.startswith("Document: "):
            current = line.removeprefix("Document: ").strip()
            continue
        if current is None or current in statuses:
            continue
        for status in ("NEW", "REVISED", "GO", "NO-GO", "VERIFIED", "ADVISORY"):
            if line.startswith(f"{status}:"):
                statuses[current] = status
                break
    return statuses


def _is_relative_to(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
    except ValueError:
        return False
    return True


def _now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
