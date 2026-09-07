"""Deterministic bridge, registry-publication, and harness state report.

Worker-facing only: this report intentionally carries no TAFE dispatcher
configuration. Workers must not be asked to know about the dispatcher or its
configuration, so the report does not surface dispatcher state or
dispatch-derived columns (WI-6186).
"""

from __future__ import annotations

import importlib.util
import sqlite3
import sys
from collections import Counter
from pathlib import Path
from types import ModuleType
from typing import Any

from groundtruth_kb.bridge.disposition import LOYAL_OPPOSITION_ACTIONABLE_STATUSES, PRIME_ACTIONABLE_STATUSES
from groundtruth_kb.bridge.notify import resolve_thread_actionability_annotations
from groundtruth_kb.harness_projection import read_roles
from groundtruth_kb.project.registry_control_plane import (
    RegistryPaths,
    load_registry_snapshot,
    registry_currentness,
)

BRIDGE_THREAD_HELPER = Path("scripts") / "bridge_thread_files.py"
BRIDGE_AGGREGATE_ID = "bridge-versioned-files"


def build_state_report(project_root: Path) -> dict[str, Any]:
    """Build a read-only worker-facing state report from live bridge files.

    The report exposes bridge and registry-publication state plus a worker-facing
    harness summary. It deliberately excludes TAFE dispatcher configuration so no
    worker is asked to know about the dispatcher (WI-6186).
    """

    root = project_root.resolve()
    return {
        "bridge": _bridge_section(root),
        "registry_publication": _registry_publication_section(root),
        "harnesses": _harness_section(root),
        "source_authority": {
            "bridge": "status-bearing numbered bridge files via scripts/bridge_thread_files.py",
            "work_item_annotations": "current_work_items in groundtruth.db (advisory; never suppressive)",
            "git_terminality": "exact singleton Work-Item metadata in commits reachable from HEAD",
            "registry_publication": "registry_currentness scoped to bridge-versioned-files",
            "harnesses": "harness-state/harness-registry.json via groundtruth_kb.harness_projection.read_roles",
        },
    }


def render_markdown(report: dict[str, Any]) -> str:
    """Render the report as the owner-standard Markdown tables."""

    bridge = report["bridge"]
    registry_publication = report["registry_publication"]
    harnesses = report["harnesses"]["rows"]

    bridge_rows = [
        ("TOTAL_THREADS", str(bridge["total_thread_count"])),
    ]
    bridge_rows.extend((row["status"], str(row["count"])) for row in bridge["status_mix"])
    bridge_rows.append(
        (
            "PRIME_ACTIONABLE_LATEST_GO_NO_GO",
            _actionable_summary(bridge["prime_actionable"]),
        )
    )
    bridge_rows.append(
        (
            "LO_ACTIONABLE_LATEST_NEW_REVISED_NO_ACTION",
            _actionable_summary(bridge["lo_actionable"]),
        )
    )

    lines = ["## BRIDGE", "| Status | Count |", "| --- | --- |"]
    lines.extend(f"| {_md_cell(status)} | {_md_cell(count)} |" for status, count in bridge_rows)

    aggregate_current = registry_publication["aggregate_current"]
    lines.extend(
        [
            "",
            "## REGISTRY PUBLICATION",
            "| Aspect | Value |",
            "| --- | --- |",
            f"| Enabled | {_md_cell(_yes_no(registry_publication['enabled']))} |",
            f"| Aggregate current | {_md_cell(_yes_no(aggregate_current) if aggregate_current is not None else '(unavailable)')} |",
            f"| Stale count | {_md_cell(registry_publication['stale_count'])} |",
            f"| Stale record IDs | {_md_cell(', '.join(registry_publication['stale_record_ids']) or '(none)')} |",
        ]
    )
    if registry_publication["enabled"] and aggregate_current is False:
        lines.extend(
            [
                "",
                "WARNING: The bridge publication aggregate is stale audit state. Governed "
                "publication self-observes the aggregate under its serialized control-plane "
                "transaction; this diagnostic does not mean publications are refused.",
            ]
        )

    lines.extend(
        [
            "",
            "## HARNESSES",
            "| ID | Harness | Model / Config | Active | Events |",
            "| --- | --- | --- | --- | --- |",
        ]
    )
    for row in harnesses:
        lines.append(
            "| {id} | {harness} | {model_config} | {active} | {events} |".format(
                id=_md_cell(row["id"]),
                harness=_md_cell(row["harness"]),
                model_config=_md_cell(row["model_config"]),
                active=_md_cell(row["active"]),
                events=_md_cell(row["events"]),
            )
        )
    return "\n".join(lines) + "\n"


def _registry_publication_section(root: Path) -> dict[str, Any]:
    disabled = {
        "enabled": False,
        "aggregate_current": None,
        "stale_count": 0,
        "stale_record_ids": [],
    }
    paths = RegistryPaths.resolve(project_root=root)
    if not all(path.is_file() for path in (paths.registry_path, paths.packaged_registry_path, paths.db_path)):
        return disabled

    try:
        snapshot = load_registry_snapshot(
            project_root=paths.project_root,
            registry_path=paths.registry_path,
            packaged_registry_path=paths.packaged_registry_path,
            db_path=paths.db_path,
        )
        if not any(record.id == BRIDGE_AGGREGATE_ID for record in snapshot.records):
            return disabled
        currentness = registry_currentness(
            snapshot,
            project_root=paths.project_root,
            db_path=paths.db_path,
            record_ids={BRIDGE_AGGREGATE_ID},
        )
    except (OSError, RuntimeError, sqlite3.Error, ValueError):
        return disabled

    stale_record_ids = sorted(
        {
            *(str(record_id) for record_id in currentness.get("missing_revisions", [])),
            *(str(row["id"]) for row in currentness.get("stale", []) if row.get("id")),
        }
    )
    return {
        "enabled": True,
        "aggregate_current": bool(currentness.get("current")),
        "stale_count": len(stale_record_ids),
        "stale_record_ids": stale_record_ids,
    }


def _bridge_section(root: Path) -> dict[str, Any]:
    helper = _load_bridge_thread_helper(root)
    index = helper.index_bridge_thread_files_archive_aware(root)
    annotations = resolve_thread_actionability_annotations(
        root,
        {slug: tuple(item.path for item in reversed(files)) for slug, files in index.items() if files},
    )
    status_counts: Counter[str] = Counter()
    threads: list[dict[str, Any]] = []

    for slug, files in sorted(index.items()):
        if not files:
            continue
        latest = files[-1]
        status = helper.status_from_bridge_file(latest.path) or "UNKNOWN"
        annotation = annotations[slug]
        status_counts[status] += 1
        threads.append(
            {
                "slug": slug,
                "latest_status": status,
                "latest_path": _relative_path(latest.path, root),
                "latest_version": latest.version,
                "version_count": len(files),
                "work_item_id": annotation.work_item_id,
                "work_item_stage": annotation.stage,
                "work_item_resolution_status": annotation.resolution_status,
                "work_item_status_detail": annotation.status_detail,
                "git_terminality": annotation.git_terminality,
                "terminal_commit": annotation.terminal_commit,
                "terminality_diagnostic": annotation.terminality_diagnostic,
                "suppressed_by_git_terminality": annotation.git_terminality == "confirmed",
            }
        )

    prime_actionable = [
        row
        for row in threads
        if row["latest_status"] in PRIME_ACTIONABLE_STATUSES and not row["suppressed_by_git_terminality"]
    ]
    lo_actionable = [
        row
        for row in threads
        if row["latest_status"] in LOYAL_OPPOSITION_ACTIONABLE_STATUSES and not row["suppressed_by_git_terminality"]
    ]
    return {
        "total_thread_count": len(threads),
        "status_mix": _status_mix(status_counts),
        "prime_actionable": prime_actionable,
        "lo_actionable": lo_actionable,
        "threads": threads,
    }


def _harness_section(root: Path) -> dict[str, Any]:
    """Build the worker-facing harness summary from the non-dispatch projection.

    Uses ``read_roles`` directly (never the dispatcher's view) and drops the
    dispatch-derived ``Role`` and ``Dispatchable`` columns (WI-6186). No worker
    sees dispatcher configuration.
    """
    projection = read_roles(root)
    harnesses = projection.get("harnesses", [])
    if not isinstance(harnesses, list):
        harnesses = []
    rows: list[dict[str, str]] = []
    for raw in sorted(harnesses, key=lambda item: str(item.get("id") or "") if isinstance(item, dict) else ""):
        if not isinstance(raw, dict):
            continue
        rows.append(
            {
                "id": str(raw.get("id") or ""),
                "harness": str(raw.get("harness_name") or ""),
                "model_config": _model_config(raw),
                "active": _yes_no(str(raw.get("status")) == "active"),
                "events": _yes_no(raw.get("can_fire_events") is True or raw.get("event_driven_hooks") is True),
            }
        )
    return {"rows": rows}


def _load_bridge_thread_helper(root: Path) -> ModuleType:
    candidates = [
        root / BRIDGE_THREAD_HELPER,
        Path(__file__).resolve().parents[4] / BRIDGE_THREAD_HELPER,
    ]
    for path in candidates:
        if not path.is_file():
            continue
        spec = importlib.util.spec_from_file_location("gtkb_bridge_thread_files_state_report", path)
        if spec is None or spec.loader is None:
            continue
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)
        return module
    raise RuntimeError(f"Unable to locate {BRIDGE_THREAD_HELPER.as_posix()}")


def _model_config(raw_record: dict[str, Any]) -> str:
    argv = _headless_argv(raw_record)
    argv_model = _argv_value(argv, "--model")
    model = argv_model or "(unspecified)"
    parts = [str(model)]

    assignments = _argv_config_assignments(argv)
    reasoning = assignments.get("model_reasoning_effort") or assignments.get("reasoning")
    if reasoning:
        parts.append(f"reasoning={reasoning}")
    effort = _argv_value(argv, "--effort")
    if effort:
        parts.append(f"effort={effort}")
    approval = assignments.get("approval_policy")
    if approval:
        parts.append(f"approval_policy={approval}")
    skill = _argv_value(argv, "--skill")
    if skill:
        parts.append(f"skill={skill}")
    route = _argv_value(argv, "--route")
    if route:
        parts.append(f"route={route}")
    return "; ".join(parts)


def _headless_argv(raw_record: dict[str, Any]) -> list[str]:
    surfaces = raw_record.get("invocation_surfaces")
    if not isinstance(surfaces, dict):
        return []
    headless = surfaces.get("headless")
    if not isinstance(headless, dict):
        return []
    argv = headless.get("argv")
    if not isinstance(argv, list):
        return []
    return [str(item) for item in argv]


def _argv_value(argv: list[str], flag: str) -> str | None:
    for index, item in enumerate(argv):
        if item == flag and index + 1 < len(argv):
            return argv[index + 1]
        prefix = f"{flag}="
        if item.startswith(prefix):
            return item[len(prefix) :]
    return None


def _argv_config_assignments(argv: list[str]) -> dict[str, str]:
    assignments: dict[str, str] = {}
    for index, item in enumerate(argv):
        if item not in {"-c", "--config"} or index + 1 >= len(argv):
            continue
        key, sep, value = argv[index + 1].partition("=")
        if sep:
            assignments[key.strip()] = value.strip().strip("\"'")
    return assignments


def _status_mix(status_counts: Counter[str]) -> list[dict[str, Any]]:
    preferred_order = (
        "NEW",
        "REVISED",
        "NO-ACTION",
        "GO",
        "NO-GO",
        "VERIFIED",
        "ADVISORY",
        "DEFERRED",
        "WITHDRAWN",
    )
    rows = []
    seen: set[str] = set()
    for status in preferred_order:
        if status in status_counts:
            rows.append({"status": status, "count": status_counts[status]})
            seen.add(status)
    for status in sorted(set(status_counts) - seen):
        rows.append({"status": status, "count": status_counts[status]})
    return rows


def _actionable_summary(rows: list[dict[str, Any]]) -> str:
    if not rows:
        return "0: (none)"
    entries = [
        f"{row['slug']} ({row['latest_status']} at {row['latest_path']}; "
        f"work_item={row.get('work_item_id') or '(unresolved)'}; "
        f"state={row.get('work_item_stage') or '(unknown)'}/"
        f"{row.get('work_item_resolution_status') or '(unknown)'}; "
        f"git_terminality={row.get('git_terminality') or 'ambiguous'})"
        for row in sorted(rows, key=lambda item: str(item["slug"]))
    ]
    return f"{len(entries)}: " + "; ".join(entries)


def _relative_path(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def _md_cell(value: object) -> str:
    text = str(value)
    return text.replace("|", "\\|").replace("\r", " ").replace("\n", "<br>")


def _yes_no(value: bool) -> str:
    return "yes" if value else "no"
