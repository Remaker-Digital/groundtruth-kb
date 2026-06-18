"""API harness stewardship monitor (report-only) - WI-4558 / Slice 1.

Read-only aggregation monitor for the Ollama (harness D) and OpenRouter
(harness F) API harnesses. On each run it fresh-reads the existing
heterogeneous state surfaces, detects MATERIAL status changes against a
persisted prior-state snapshot, scores stuck-work risk with cited evidence,
and emits a regenerable status report (JSON + markdown).

It is strictly REPORT-ONLY per PAUTH-WI4558-STEWARDSHIP-MONITOR-REPORT-ONLY:
no auto-remediation, no auto-dispatch/auto-kill, and no paid external
pricing-API / credential / live-network calls. The readiness probe is an
injected seam defaulting to ``mock_readiness_probe`` so tests and report-only
runs make NO live network call. The module writes only under
``.gtkb-state/api-harness-stewardship/``.

Bridge: gtkb-api-harness-stewardship-monitor (GO at -002).
Governing specs: GOV-HARNESS-ONBOARDING-CONTRACT-001, GOV-STANDING-BACKLOG-001,
GOV-SOURCE-OF-TRUTH-FRESHNESS-001, DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001.
"""

from __future__ import annotations

import json
import re
from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - tomllib is stdlib on 3.11+
    tomllib = None  # type: ignore[assignment]

# harness_id -> provider name (the two API harnesses this monitor stewards).
MONITORED_HARNESSES: dict[str, str] = {"D": "ollama", "F": "openrouter"}

_STATE_SUBPATH: tuple[str, ...] = (".gtkb-state", "api-harness-stewardship")

# dispatch-state ``last_result`` values that indicate a degraded/stuck recipient.
_FAILURE_RESULTS: frozenset[str] = frozenset(
    {
        "provider_failure_backoff_active",
        "previous_launch_failed",
        "spawn_rate_limited",
        "concurrency_cap_reached",
    }
)
# dispatch-failures ``reason`` values that indicate a genuine (not re-logged) failure.
_FATAL_FAILURE_REASONS: frozenset[str] = frozenset(
    {
        "max_turn_exhaustion",
        "subprocess_execution_failed",
        "provider_failure",
        "fatal_worker_output_marker",
    }
)
_FAILURE_COUNT_RISK_THRESHOLD = 3

_VERSION_RE = re.compile(r"^(.*)-(\d{3})\.md$")

ReadinessProbe = Callable[[str], dict[str, Any]]
DBFactory = Callable[[Path], Any]


def mock_readiness_probe(harness_id: str) -> dict[str, Any]:
    """Default readiness probe: report-only, makes NO network/credential call."""
    return {
        "harness_id": harness_id,
        "probed": False,
        "status": "not_probed",
        "note": "report-only default; inject a probe for live readiness",
    }


def _state_dir(project_root: Path) -> Path:
    return project_root.joinpath(*_STATE_SUBPATH)


def _read_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def _load_toml(path: Path) -> dict[str, Any] | None:
    if tomllib is None:
        return None
    try:
        return tomllib.loads(path.read_text(encoding="utf-8"))
    except (OSError, tomllib.TOMLDecodeError):
        return None


# --------------------------------------------------------------------------
# Surface readers (read-only, defensive: a missing/unreadable surface yields an
# "unknown" sub-status rather than raising).
# --------------------------------------------------------------------------


def read_dispatch_surface(project_root: Path) -> dict[str, Any]:
    """Surface (d): dispatch-poller state + failure JSONL family (incl. rotation)."""
    base = project_root / ".gtkb-state" / "bridge-poller"
    state = _read_json(base / "dispatch-state.json")
    recipients = state.get("recipients", {}) if isinstance(state, dict) else {}

    failures: dict[str, dict[str, int]] = {}
    for fp in sorted(base.glob("dispatch-failures.jsonl*")):
        try:
            text = fp.read_text(encoding="utf-8")
        except OSError:
            continue
        for line in text.splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue
            recip = str(rec.get("recipient", ""))
            reason = str(rec.get("reason", ""))
            bucket = failures.setdefault(recip, {})
            bucket[reason] = bucket.get(reason, 0) + 1

    per_harness: dict[str, Any] = {}
    for hid in MONITORED_HARNESSES:
        key = f"loyal-opposition:{hid}"
        rec = recipients.get(key, {}) if isinstance(recipients, dict) else {}
        per_harness[hid] = {
            "recipient_key": key,
            "present": bool(rec),
            "last_result": rec.get("last_result"),
            "circuit_breaker_tripped": bool(rec.get("circuit_breaker_tripped")),
            "failure_count": int(rec.get("failure_count") or 0),
            "updated_at": rec.get("updated_at"),
            "failure_reasons": failures.get(key, {}),
        }
    return {"status": "ok" if isinstance(state, dict) else "unknown", "per_harness": per_harness}


def read_harness_surface(project_root: Path) -> dict[str, Any]:
    """Surface (b): harness registry + identities."""
    base = project_root / "harness-state"
    registry = _read_json(base / "harness-registry.json")
    identities = _read_json(base / "harness-identities.json")

    entries: list[dict[str, Any]] = []
    if isinstance(registry, dict):
        raw = registry.get("harnesses") or registry.get("entries")
        if isinstance(raw, list):
            entries = [e for e in raw if isinstance(e, dict)]
        elif raw is None and all(isinstance(v, dict) for v in registry.values()):
            entries = [{"id": k, **v} for k, v in registry.items()]

    per_harness: dict[str, Any] = {}
    for hid in MONITORED_HARNESSES:
        match = next(
            (e for e in entries if str(e.get("id") or e.get("harness_id")) == hid),
            None,
        )
        per_harness[hid] = {
            "present": match is not None,
            "role": (match or {}).get("role"),
            "status": (match or {}).get("status") or (match or {}).get("lifecycle_status"),
        }
    return {
        "status": "ok" if entries else "unknown",
        "per_harness": per_harness,
        "identities_present": isinstance(identities, dict),
    }


def read_routing_surface(project_root: Path) -> dict[str, Any]:
    """Surface (c): API-harness routing config (.api-harness/routing.toml)."""
    data = _load_toml(project_root / ".api-harness" / "routing.toml")
    if not isinstance(data, dict):
        return {"status": "unknown", "per_provider": {}, "default_model": None}
    models = data.get("models", {})
    per_provider: dict[str, list[str]] = {}
    if isinstance(models, dict):
        for name, model in models.items():
            provider = str(model.get("provider", "")) if isinstance(model, dict) else ""
            per_provider.setdefault(provider, []).append(name)
    routing = data.get("routing", {})
    default_model = routing.get("default_model") if isinstance(routing, dict) else None
    return {
        "status": "ok" if models else "unknown",
        "per_provider": per_provider,
        "default_model": default_model,
    }


def read_cost_quality_surface(project_root: Path) -> dict[str, Any]:
    """Cost/quality rollup from EXISTING static dispatcher rules (no live pricing)."""
    data = _load_toml(project_root / "config" / "dispatcher" / "rules.toml")
    harnesses = data.get("harnesses", {}) if isinstance(data, dict) else {}
    per_harness: dict[str, Any] = {}
    for hid in MONITORED_HARNESSES:
        entry = harnesses.get(hid, {}) if isinstance(harnesses, dict) else {}
        per_harness[hid] = {
            "dispatch_cost": entry.get("dispatch_cost"),
            "dispatch_quality": entry.get("dispatch_quality"),
            "dispatch_availability": entry.get("dispatch_availability"),
            "can_receive_dispatch": entry.get("can_receive_dispatch"),
        }
    return {"status": "ok" if harnesses else "unknown", "per_harness": per_harness}


def _bridge_first_token(path: Path) -> str | None:
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None
    for line in text.splitlines():
        stripped = line.strip()
        if stripped:
            tokens = stripped.lstrip("#>*-` ").split()
            return tokens[0] if tokens else None
    return None


def read_bridge_surface(project_root: Path) -> dict[str, Any]:
    """Surface (a): bridge state (latest-version status of each thread)."""
    bdir = project_root / "bridge"
    if not bdir.is_dir():
        return {"status": "unknown", "threads": 0, "actionable_pending": 0}
    latest: dict[str, Path] = {}
    for path in bdir.glob("*.md"):
        match = _VERSION_RE.match(path.name)
        slug = match.group(1) if match else path.stem
        if slug not in latest or path.name > latest[slug].name:
            latest[slug] = path
    actionable = sum(1 for p in latest.values() if _bridge_first_token(p) in {"NEW", "REVISED"})
    return {"status": "ok", "threads": len(latest), "actionable_pending": actionable}


def read_readiness_surface(probe: ReadinessProbe | None = None) -> dict[str, Any]:
    """Surface (e): readiness via an injected probe (default: no-network mock)."""
    active = probe or mock_readiness_probe
    per_harness: dict[str, Any] = {}
    for hid in MONITORED_HARNESSES:
        try:
            per_harness[hid] = dict(active(hid))
        except Exception as exc:  # noqa: BLE001 - defensive: a probe must never crash the report
            per_harness[hid] = {"probed": False, "status": "probe_error", "error": type(exc).__name__}
    return {"status": "ok", "per_harness": per_harness}


def _default_db_factory(project_root: Path) -> Any:
    from groundtruth_kb.db import KnowledgeDB  # lazy import; read-only usage only

    return KnowledgeDB(str(project_root / "groundtruth.db"))


def read_membase_surface(project_root: Path, db_factory: DBFactory | None = None) -> dict[str, Any]:
    """Surface (f): MemBase work-item/project state for D and F (read-only)."""
    factory = db_factory or _default_db_factory
    try:
        db = factory(project_root)
    except Exception as exc:  # noqa: BLE001 - defensive: missing/unreadable DB is "unknown"
        return {"status": "unknown", "error": type(exc).__name__, "per_harness": {}}
    try:
        items = list(db.list_work_items()) if hasattr(db, "list_work_items") else []
    except Exception as exc:  # noqa: BLE001 - defensive read
        return {"status": "unknown", "error": type(exc).__name__, "per_harness": {}}

    terminal = {"done", "verified", "retired", "closed", "completed"}
    per_harness: dict[str, Any] = {}
    for hid, provider in MONITORED_HARNESSES.items():
        related = 0
        for item in items:
            blob = (str(item.get("title", "")) + " " + str(item.get("description", ""))).lower()
            if provider in blob and str(item.get("stage", "")) not in terminal:
                related += 1
        per_harness[hid] = {"provider": provider, "open_related_work_items": related}
    return {"status": "ok" if items else "unknown", "per_harness": per_harness}


# --------------------------------------------------------------------------
# Stuck-work risk scoring + material-change detection.
# --------------------------------------------------------------------------


def score_stuck_work_risk(
    harness_id: str,
    dispatch_surface: dict[str, Any],
    bridge_surface: dict[str, Any],
) -> dict[str, Any]:
    """Deterministic stuck-work risk heuristic with cited evidence."""
    state = dispatch_surface.get("per_harness", {}).get(harness_id, {})
    evidence: list[str] = []

    if state.get("circuit_breaker_tripped"):
        evidence.append(f"circuit_breaker_tripped for {state.get('recipient_key')}")
    if state.get("last_result") in _FAILURE_RESULTS:
        evidence.append(f"last_result={state.get('last_result')}")
    failure_count = int(state.get("failure_count") or 0)
    if failure_count >= _FAILURE_COUNT_RISK_THRESHOLD:
        evidence.append(f"failure_count={failure_count} (>= {_FAILURE_COUNT_RISK_THRESHOLD})")
    fatal = sum(
        count for reason, count in (state.get("failure_reasons") or {}).items() if reason in _FATAL_FAILURE_REASONS
    )
    if fatal:
        evidence.append(f"{fatal} fatal dispatch-failure record(s)")

    return {
        "risk": "elevated" if evidence else "none",
        "evidence": evidence,
        "context": {"bridge_actionable_pending": int(bridge_surface.get("actionable_pending") or 0)},
    }


def _snapshot_signature(report: dict[str, Any]) -> dict[str, Any]:
    signature: dict[str, Any] = {}
    for hid, harness in report.get("harnesses", {}).items():
        signature[hid] = {
            "dispatch_last_result": harness["dispatch"].get("last_result"),
            "circuit_breaker_tripped": harness["dispatch"].get("circuit_breaker_tripped"),
            "risk": harness["risk"]["risk"],
            "registry_status": harness["harness"].get("status"),
            "readiness_status": harness["readiness"].get("status"),
            "open_related_work_items": harness["membase"].get("open_related_work_items"),
        }
    return signature


def detect_material_changes(
    prior_signature: dict[str, Any] | None,
    current_signature: dict[str, Any],
) -> list[dict[str, Any]]:
    """Report only material per-harness changes versus the prior snapshot."""
    changes: list[dict[str, Any]] = []
    for hid, current in current_signature.items():
        prior = (prior_signature or {}).get(hid)
        if prior is None:
            changes.append({"harness": hid, "kind": "baseline", "fields": {}})
            continue
        diff = {key: {"from": prior.get(key), "to": value} for key, value in current.items() if prior.get(key) != value}
        if diff:
            changes.append({"harness": hid, "kind": "changed", "fields": diff})
    return changes


# --------------------------------------------------------------------------
# Report build + emit + run.
# --------------------------------------------------------------------------


def build_report(
    project_root: Path,
    *,
    readiness_probe: ReadinessProbe | None = None,
    db_factory: DBFactory | None = None,
    now: datetime | None = None,
    run_id: str | None = None,
) -> dict[str, Any]:
    """Aggregate all surfaces into a report structure (no file I/O)."""
    moment = now or datetime.now(UTC)
    resolved_run_id = run_id or moment.strftime("%Y%m%dT%H%M%SZ")

    dispatch = read_dispatch_surface(project_root)
    harness = read_harness_surface(project_root)
    routing = read_routing_surface(project_root)
    bridge = read_bridge_surface(project_root)
    readiness = read_readiness_surface(readiness_probe)
    membase = read_membase_surface(project_root, db_factory)
    cost_quality = read_cost_quality_surface(project_root)

    harnesses: dict[str, Any] = {}
    for hid, provider in MONITORED_HARNESSES.items():
        harnesses[hid] = {
            "provider": provider,
            "dispatch": dispatch["per_harness"].get(hid, {}),
            "harness": harness["per_harness"].get(hid, {}),
            "readiness": readiness["per_harness"].get(hid, {}),
            "membase": membase.get("per_harness", {}).get(hid, {}),
            "cost_quality": cost_quality.get("per_harness", {}).get(hid, {}),
            "risk": score_stuck_work_risk(hid, dispatch, bridge),
        }

    return {
        "schema_version": 1,
        "run_id": resolved_run_id,
        "generated_at": moment.astimezone(UTC).isoformat().replace("+00:00", "Z"),
        "report_only": True,
        "surfaces": {
            "dispatch": dispatch.get("status"),
            "harness": harness.get("status"),
            "routing": routing.get("status"),
            "bridge": bridge.get("status"),
            "readiness": readiness.get("status"),
            "membase": membase.get("status"),
        },
        "routing": routing,
        "bridge": bridge,
        "harnesses": harnesses,
    }


def _render_markdown(report: dict[str, Any], material_changes: list[dict[str, Any]]) -> str:
    lines = [
        f"# API Harness Stewardship Report - {report['run_id']}",
        "",
        f"Generated: {report['generated_at']} (report-only)",
        "",
        f"Surfaces: {report['surfaces']}",
        "",
    ]
    for hid, harness in report["harnesses"].items():
        lines.append(f"## Harness {hid} ({harness['provider']})")
        lines.append(f"- risk: **{harness['risk']['risk']}**")
        for item in harness["risk"]["evidence"]:
            lines.append(f"  - {item}")
        lines.append(f"- dispatch.last_result: {harness['dispatch'].get('last_result')}")
        lines.append(f"- readiness: {harness['readiness'].get('status')}")
        lines.append(f"- cost/quality: {harness['cost_quality']}")
        lines.append(f"- open related work items: {harness['membase'].get('open_related_work_items')}")
        lines.append("")
    lines.append("## Material changes since last snapshot")
    if material_changes:
        for change in material_changes:
            lines.append(f"- {change['harness']}: {change['kind']} {change.get('fields') or ''}")
    else:
        lines.append("- none")
    lines.append("")
    return "\n".join(lines)


def emit_report(
    project_root: Path,
    report: dict[str, Any],
    *,
    material_changes: list[dict[str, Any]],
) -> dict[str, Path]:
    """Write the JSON + markdown report under .gtkb-state/api-harness-stewardship/<run_id>/."""
    out_dir = _state_dir(project_root) / report["run_id"]
    out_dir.mkdir(parents=True, exist_ok=True)
    full = dict(report, material_changes=material_changes)
    json_path = out_dir / "report.json"
    md_path = out_dir / "report.md"
    json_path.write_text(json.dumps(full, indent=2, sort_keys=True), encoding="utf-8")
    md_path.write_text(_render_markdown(report, material_changes), encoding="utf-8")
    return {"json": json_path, "markdown": md_path}


def run(
    project_root: Path | str,
    *,
    readiness_probe: ReadinessProbe | None = None,
    db_factory: DBFactory | None = None,
    now: datetime | None = None,
    run_id: str | None = None,
) -> dict[str, Any]:
    """Full report-only run: build, detect material changes, emit, persist snapshot."""
    root = Path(project_root)
    report = build_report(
        root,
        readiness_probe=readiness_probe,
        db_factory=db_factory,
        now=now,
        run_id=run_id,
    )
    state_dir = _state_dir(root)
    prior = _read_json(state_dir / "last-snapshot.json")
    current_signature = _snapshot_signature(report)
    material_changes = detect_material_changes(prior if isinstance(prior, dict) else None, current_signature)
    report["material_changes"] = material_changes

    paths = emit_report(root, report, material_changes=material_changes)
    state_dir.mkdir(parents=True, exist_ok=True)
    (state_dir / "last-snapshot.json").write_text(
        json.dumps(current_signature, indent=2, sort_keys=True), encoding="utf-8"
    )
    report["report_paths"] = {name: str(path) for name, path in paths.items()}
    return report


def main(argv: list[str] | None = None) -> int:
    import argparse

    parser = argparse.ArgumentParser(description="API harness stewardship monitor (report-only).")
    parser.add_argument("--project-root", default=".")
    args = parser.parse_args(argv)
    report = run(Path(args.project_root))
    summary = {
        "run_id": report["run_id"],
        "surfaces": report["surfaces"],
        "risk": {hid: report["harnesses"][hid]["risk"]["risk"] for hid in report["harnesses"]},
        "material_changes": len(report.get("material_changes", [])),
        "report_paths": report.get("report_paths"),
    }
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
