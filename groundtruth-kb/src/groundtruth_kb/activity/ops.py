"""Deterministic ops activity context renderer for ``::open ops``."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

OPS_OPTIONS: tuple[str, ...] = (
    "apply patch",
    "increase scale threshold",
    "approve operational change",
    "triage support",
    "evaluate feedback",
)

_STATUS_RANK = {
    "attention": 3,
    "watch": 2,
    "nominal": 1,
    "observed": 1,
    "unavailable": 0,
}


@dataclass(frozen=True)
class SourceObservation:
    """Availability and summary for one optional in-root ops source."""

    label: str
    relative_path: str
    status: str
    summary: str


@dataclass(frozen=True)
class OpsSignal:
    """Normalized deployed-application status signal."""

    name: str
    status: str
    evidence: str
    sources: tuple[SourceObservation, ...]


@dataclass(frozen=True)
class OpsOption:
    """Report-only AUQ option and deterministic rationale."""

    text: str
    priority: str
    reason: str


@dataclass(frozen=True)
class OpsSnapshot:
    """Full report model rendered for the ops activity."""

    signals: tuple[OpsSignal, ...]
    options: tuple[OpsOption, ...]


def _safe_json_load(path: Path) -> tuple[dict[str, Any] | None, str | None]:
    try:
        data = json.loads(path.read_text(encoding="utf-8-sig"))
    except FileNotFoundError:
        return None, "missing"
    except json.JSONDecodeError as exc:
        return None, f"invalid JSON: {exc.msg}"
    except OSError as exc:
        return None, f"unreadable: {exc}"
    if not isinstance(data, dict):
        return None, "invalid JSON: top-level value is not an object"
    return data, None


def _status_from_value(value: object) -> str:
    text = str(value or "").strip().lower()
    if not text:
        return "observed"
    if text in {"red", "failed", "failure", "fail", "failing", "blocked", "critical", "unhealthy", "down"}:
        return "attention"
    if text in {"amber", "warn", "warning", "degraded", "partial", "unknown", "pending"}:
        return "watch"
    if text in {"green", "pass", "passed", "success", "successful", "healthy", "ok", "nominal"}:
        return "nominal"
    if text == "unavailable":
        return "unavailable"
    return "observed"


def _max_status(*statuses: str) -> str:
    return max(
        (status for status in statuses if status), key=lambda item: _STATUS_RANK.get(item, 0), default="observed"
    )


def _compact_value(value: object) -> str:
    if isinstance(value, float):
        return f"{value:g}"
    if isinstance(value, (str, int, bool)) or value is None:
        return str(value)
    return json.dumps(value, ensure_ascii=True, sort_keys=True)


def _available_summary(label: str, data: dict[str, Any]) -> str:
    preferred_keys = (
        "status",
        "summary",
        "release_gate_status",
        "open_cases",
        "urgent_cases",
        "active_users",
        "pending_feedback",
        "negative_feedback",
        "usage_pct",
        "current_load",
        "scale_threshold",
    )
    parts = [f"{key}={_compact_value(data[key])}" for key in preferred_keys if key in data]
    if not parts:
        parts = [f"keys={', '.join(sorted(str(key) for key in data)[:6]) or 'none'}"]
    return f"{label}: " + "; ".join(parts)


def _observe_json(
    project_root: Path, label: str, relative_path: str
) -> tuple[SourceObservation, dict[str, Any] | None]:
    path = project_root / relative_path
    data, error = _safe_json_load(path)
    if data is None:
        return SourceObservation(
            label=label, relative_path=relative_path, status="unavailable", summary=error or "missing"
        ), None
    return SourceObservation(
        label=label, relative_path=relative_path, status="available", summary=_available_summary(label, data)
    ), data


def _dashboard_health(data: dict[str, Any]) -> tuple[str, list[str]]:
    headlines = data.get("headlines") if isinstance(data.get("headlines"), dict) else {}
    operations = data.get("operations") if isinstance(data.get("operations"), dict) else {}
    verification = (
        operations.get("latest_verification_run") if isinstance(operations.get("latest_verification_run"), dict) else {}
    )
    runtime = operations.get("runtime_live_metrics") if isinstance(operations.get("runtime_live_metrics"), dict) else {}

    statuses = [
        _status_from_value(headlines.get("release_gate_status")),
        _status_from_value(verification.get("status")),
        _status_from_value(runtime.get("status")),
    ]
    failing_tests = data.get("quality", {}).get("failing_tests") if isinstance(data.get("quality"), dict) else None
    if isinstance(failing_tests, int) and failing_tests > 0:
        statuses.append("attention")
    open_p0_p1 = headlines.get("open_p0_p1")
    if isinstance(open_p0_p1, int) and open_p0_p1 > 0:
        statuses.append("attention")

    details: list[str] = []
    for key in ("release_gate_status", "open_p0_p1"):
        if key in headlines:
            details.append(f"{key}={_compact_value(headlines[key])}")
    if verification:
        details.append(f"latest_verification_run.status={_compact_value(verification.get('status'))}")
    if runtime:
        details.append(f"runtime_live_metrics.status={_compact_value(runtime.get('status'))}")
    if failing_tests is not None:
        details.append(f"failing_tests={_compact_value(failing_tests)}")
    return _max_status(*statuses), details


def _dashboard_scale(data: dict[str, Any]) -> tuple[str, list[str]]:
    operations = data.get("operations") if isinstance(data.get("operations"), dict) else {}
    statuses: list[str] = []
    details: list[str] = []

    success_rate = operations.get("deployment_success_rate_30d")
    if isinstance(success_rate, int | float):
        details.append(f"deployment_success_rate_30d={success_rate:g}")
        if success_rate < 80:
            statuses.append("attention")
        elif success_rate < 95:
            statuses.append("watch")
        else:
            statuses.append("nominal")

    deployments = operations.get("real_deployments_30d")
    if isinstance(deployments, int | float):
        details.append(f"real_deployments_30d={deployments:g}")
        statuses.append("observed")

    runtime = operations.get("runtime_live_metrics") if isinstance(operations.get("runtime_live_metrics"), dict) else {}
    if runtime:
        details.append(f"runtime_live_metrics.status={_compact_value(runtime.get('status'))}")
        statuses.append(_status_from_value(runtime.get("status")))
    return _max_status(*statuses), details


def _generic_signal_from_data(data: dict[str, Any], *, signal: str) -> tuple[str, list[str]]:
    statuses: list[str] = []
    details: list[str] = []
    for key in ("status", f"{signal}_status", "summary"):
        if key in data:
            details.append(f"{key}={_compact_value(data[key])}")
            statuses.append(_status_from_value(data[key]))

    numeric_rules = {
        "scale": ("usage_pct", "current_load", "scale_threshold"),
        "support": ("open_cases", "urgent_cases"),
        "user_activity": ("active_users", "activity_threshold"),
        "feedback": ("pending_feedback", "negative_feedback"),
    }
    for key in numeric_rules.get(signal, ()):
        if key in data:
            details.append(f"{key}={_compact_value(data[key])}")

    if signal == "scale":
        usage = data.get("usage_pct")
        current_load = data.get("current_load")
        scale_threshold = data.get("scale_threshold")
        if isinstance(usage, int | float):
            statuses.append("attention" if usage >= 90 else "watch" if usage >= 75 else "nominal")
        if isinstance(current_load, int | float) and isinstance(scale_threshold, int | float):
            statuses.append("attention" if current_load >= scale_threshold else "nominal")
    elif signal == "support":
        urgent = data.get("urgent_cases")
        open_cases = data.get("open_cases")
        if isinstance(urgent, int) and urgent > 0:
            statuses.append("attention")
        elif isinstance(open_cases, int):
            statuses.append("watch" if open_cases > 0 else "nominal")
    elif signal == "user_activity":
        active = data.get("active_users")
        threshold = data.get("activity_threshold")
        if isinstance(active, int | float) and isinstance(threshold, int | float):
            statuses.append("watch" if active >= threshold else "nominal")
    elif signal == "feedback":
        negative = data.get("negative_feedback")
        pending = data.get("pending_feedback")
        if isinstance(negative, int) and negative > 0:
            statuses.append("attention")
        elif isinstance(pending, int):
            statuses.append("watch" if pending > 0 else "nominal")

    return _max_status(*statuses), details


def _merge_signal(name: str, sources: tuple[SourceObservation, ...], details: list[tuple[str, list[str]]]) -> OpsSignal:
    available_details = [(status, values) for status, values in details if values]
    if not available_details:
        missing = ", ".join(source.relative_path for source in sources)
        return OpsSignal(
            name=name, status="unavailable", evidence=f"missing optional source(s): {missing}", sources=sources
        )
    status = _max_status(*(item[0] for item in available_details))
    evidence_parts = ["; ".join(values) for _, values in available_details if values]
    return OpsSignal(name=name, status=status, evidence="; ".join(evidence_parts), sources=sources)


def _collect_health(project_root: Path) -> OpsSignal:
    primary, primary_data = _observe_json(project_root, "ops health", ".gtkb-state/ops/health.json")
    dashboard, dashboard_data = _observe_json(
        project_root,
        "project progress snapshot",
        "independent-progress-assessments/artifacts/project-progress/latest.json",
    )
    details: list[tuple[str, list[str]]] = []
    if primary_data is not None:
        details.append(_generic_signal_from_data(primary_data, signal="health"))
    if dashboard_data is not None:
        details.append(_dashboard_health(dashboard_data))
    return _merge_signal("health", (primary, dashboard), details)


def _collect_scale(project_root: Path) -> OpsSignal:
    primary, primary_data = _observe_json(project_root, "ops scale", ".gtkb-state/ops/scale.json")
    dashboard, dashboard_data = _observe_json(
        project_root,
        "project progress snapshot",
        "independent-progress-assessments/artifacts/project-progress/latest.json",
    )
    details: list[tuple[str, list[str]]] = []
    if primary_data is not None:
        details.append(_generic_signal_from_data(primary_data, signal="scale"))
    if dashboard_data is not None:
        details.append(_dashboard_scale(dashboard_data))
    return _merge_signal("scale", (primary, dashboard), details)


def _collect_named_signal(project_root: Path, name: str, label: str, relative_path: str, signal: str) -> OpsSignal:
    source, data = _observe_json(project_root, label, relative_path)
    details = [_generic_signal_from_data(data, signal=signal)] if data is not None else []
    return _merge_signal(name, (source,), details)


def collect_ops_snapshot(project_root: Path) -> OpsSnapshot:
    """Collect deterministic in-root ops signals without external calls."""
    root = project_root.expanduser().resolve()
    signals = (
        _collect_health(root),
        _collect_scale(root),
        _collect_named_signal(
            root, "support cases", "ops support cases", ".gtkb-state/ops/support-cases.json", "support"
        ),
        _collect_named_signal(
            root, "user activity", "ops user activity", ".gtkb-state/ops/user-activity.json", "user_activity"
        ),
        _collect_named_signal(root, "ops feedback", "ops feedback", ".gtkb-state/ops/feedback.json", "feedback"),
    )
    by_name = {signal.name: signal for signal in signals}
    options = (
        _option("apply patch", by_name["health"], "patch when health, release, or verification signals need attention"),
        _option(
            "increase scale threshold", by_name["scale"], "adjust scale only when local scale evidence supports it"
        ),
        _option(
            "approve operational change",
            _combined_signal("operational change", by_name["health"], by_name["scale"]),
            "owner approval remains separate; this report only surfaces readiness context",
        ),
        _option("triage support", by_name["support cases"], "prioritize support when case evidence is present"),
        _option("evaluate feedback", by_name["ops feedback"], "review ops feedback before changing behavior"),
    )
    return OpsSnapshot(signals=signals, options=options)


def _combined_signal(name: str, *signals: OpsSignal) -> OpsSignal:
    status = _max_status(*(signal.status for signal in signals))
    evidence = "; ".join(f"{signal.name}: {signal.status}" for signal in signals)
    sources = tuple(source for signal in signals for source in signal.sources)
    return OpsSignal(name=name, status=status, evidence=evidence, sources=sources)


def _option(text: str, signal: OpsSignal, reason: str) -> OpsOption:
    priority = {
        "attention": "P1",
        "watch": "P2",
        "nominal": "P3",
        "observed": "P3",
        "unavailable": "P4",
    }.get(signal.status, "P3")
    return OpsOption(text=text, priority=priority, reason=f"{reason}; signal={signal.name}:{signal.status}")


def _source_line(source: SourceObservation) -> str:
    if source.status == "available":
        return f"- {source.label}: available at `{source.relative_path}` ({source.summary})"
    return f"- {source.label}: unavailable at `{source.relative_path}` ({source.summary})"


def render_ops_activity_context(project_root: Path) -> str:
    """Render the report-only ops status and AUQ option surface."""
    snapshot = collect_ops_snapshot(project_root)
    lines = [
        "## Ops Activity Status And AUQ Options",
        "",
        "- status: report-only",
        "- source_scope: in-root optional operational surfaces",
        "- external_actions: none",
        "- owner_decisions: none requested by this renderer",
        "",
        "### Operations Snapshot",
        "",
        "| Signal | Status | Evidence |",
        "| --- | --- | --- |",
    ]
    for signal in snapshot.signals:
        lines.append(f"| {signal.name} | {signal.status} | {signal.evidence} |")
    lines.extend(["", "### Source Availability", ""])
    for signal in snapshot.signals:
        lines.append(f"- {signal.name}:")
        lines.extend(f"  {line}" for line in (_source_line(source) for source in signal.sources))
    lines.extend(["", "### Prioritized AUQ Options", ""])
    for index, option in enumerate(snapshot.options, start=1):
        lines.append(f"{index}. {option.text} (priority: {option.priority}) - {option.reason}")
    return "\n".join(lines)
