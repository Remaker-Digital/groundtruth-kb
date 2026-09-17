"""Compact read-only operating status from current native facts (O-7 R25).

Every component is a fresh read at the moment of the call: the configured authority, the host and its application
catalog, the bridge state report, the declared registry, the formal authority status, on request one native context
binding, and the project dashboard link as configuration states it (the derived view is described from local files
and never contacted). Nothing here reads a cached startup report, a local database or an inherited session, and
nothing certifies a context: an unavailable or unknown fact is reported as such with its cause.
"""

from __future__ import annotations

import json
import time
import tomllib
from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from groundtruth_kb import __version__
from groundtruth_kb.authority_client import AuthorityClient, AuthorityClientError
from groundtruth_kb.config import GTConfig
from groundtruth_kb.dashboard_link import default_dashboard_runtime_root, grafana_dashboard_url, refresh_service_url

COMPONENTS: tuple[str, ...] = ("authority", "project", "bridge", "registry", "formal", "session", "dashboard")


@dataclass(frozen=True)
class StatusComponent:
    """One fresh read: PASS (fact observed and healthy), FAIL (fact observed and unhealthy) or UNKNOWN (unavailable)."""

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
class OperatingStatus:
    schema_version: int
    package_version: str
    captured_at: str
    project_root: Path
    startup: bool
    overall_status: str
    components: tuple[StatusComponent, ...]

    def to_json_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "package_version": self.package_version,
            "captured_at": self.captured_at,
            "project_root": str(self.project_root),
            "startup": self.startup,
            "overall_status": self.overall_status,
            "certifies_context": False,
            "components": [component.to_json_dict() for component in self.components],
        }


Probe = Callable[[], tuple[str, str, str, dict[str, Any]]]


def _timed(name: str, probe: Probe) -> StatusComponent:
    started = time.perf_counter()
    try:
        status, detail, source, evidence = probe()
    except AuthorityClientError as error:
        status, detail, source, evidence = (
            "UNKNOWN",
            f"authority unavailable: {error} ({error.code})",
            "native authority",
            {"code": error.code, "details": error.details},
        )
    except (OSError, ValueError) as error:
        status, detail, source, evidence = (
            "UNKNOWN",
            f"unavailable: {error}",
            "local read",
            {"error": type(error).__name__},
        )
    return StatusComponent(name, status, detail, source, (time.perf_counter() - started) * 1000.0, evidence)


def _authority(client: AuthorityClient) -> tuple[str, str, str, dict[str, Any]]:
    payload = client.request("GET", "/v1/status")
    ready = bool(payload.get("ready")) and bool(payload.get("reachable", True))
    return (
        "PASS" if ready else "FAIL",
        ("ready" if ready else "not ready") + f" ({client.url})",
        "GET /v1/status",
        {
            key: payload.get(key)
            for key in ("ready", "reachable", "schema_catalog_matches", "schema_version")
            if key in payload
        },
    )


def _project(root: Path, config: GTConfig) -> tuple[str, str, str, dict[str, Any]]:
    catalog = root / "applications" / "registry.toml"
    applications: list[str] = []
    if catalog.is_file():
        applications = sorted(tomllib.loads(catalog.read_text(encoding="utf-8")).get("applications", {}))
    return (
        "PASS" if root.is_dir() else "FAIL",
        f"{root} ({len(applications)} registered application(s))",
        "configuration and application catalog",
        {
            "config_file": str(root / "groundtruth.toml") if (root / "groundtruth.toml").is_file() else None,
            "applications": applications,
            "catalog_present": catalog.is_file(),
        },
    )


def _bridge(client: AuthorityClient) -> tuple[str, str, str, dict[str, Any]]:
    report = client.request("GET", "/v1/bridge/state-report")
    counts = {key: value for key, value in report.items() if isinstance(value, int | float)}
    lists = {key: len(value) for key, value in report.items() if isinstance(value, list)}
    summary = ", ".join(f"{key} {value}" for key, value in sorted({**counts, **lists}.items())) or "no counts reported"
    return "PASS", summary, "GET /v1/bridge/state-report", {"counts": counts, "list_sizes": lists}


def _registry(root: Path) -> tuple[str, str, str, dict[str, Any]]:
    declaration = root / "config" / "registry" / "sot-artifacts.toml"
    if not declaration.is_file():
        return (
            "UNKNOWN",
            "no declared registry at config/registry/sot-artifacts.toml",
            "declared registry",
            {"present": False},
        )
    rows = tomllib.loads(declaration.read_text(encoding="utf-8")).get("artifacts", [])
    active = sum(1 for row in rows if row.get("lifecycle") == "active")
    return (
        "PASS",
        f"{len(rows)} declarations ({active} active)",
        "declared registry",
        {"declarations": len(rows), "active": active},
    )


FORMAL_FINDING_LISTS = ("ambiguities", "source_issues", "validation_issues")


def _formal(client: AuthorityClient) -> tuple[str, str, str, dict[str, Any]]:
    """The native authority-status contract: `status` pass/fail plus three finding lists; anything else is UNKNOWN."""
    payload = client.request("GET", "/v1/authority/status")
    route = "GET /v1/authority/status"
    if (
        not isinstance(payload, dict)
        or payload.get("status") not in ("pass", "fail")
        or any(not isinstance(payload.get(name), list) for name in FORMAL_FINDING_LISTS)
    ):
        return (
            "UNKNOWN",
            "authority status response is not the native contract (status, ambiguities, source_issues, "
            "validation_issues); nothing is inferred from it",
            route,
            {"response_keys": sorted(payload) if isinstance(payload, dict) else type(payload).__name__},
        )
    counts = {name: len(payload[name]) for name in FORMAL_FINDING_LISTS}
    healthy = payload["status"] == "pass" and not any(counts.values())
    findings = ", ".join(f"{count} {name.replace('_', ' ')}" for name, count in counts.items() if count)
    return (
        "PASS" if healthy else "FAIL",
        "pass: no ambiguities, source issues or validation issues"
        if healthy
        else f"{payload['status']}: " + (findings or "the service reports fail without listed findings"),
        route,
        {key: payload[key] for key in payload if key != "records"},
    )


def _session(client: AuthorityClient, native_context_id: str | None) -> tuple[str, str, str, dict[str, Any]]:
    if not native_context_id:
        return (
            "UNKNOWN",
            "no native context id supplied; nothing is inferred from the environment",
            "GET /v1/sessions/binding",
            {"requested": False},
        )
    binding = client.request("GET", "/v1/sessions/binding", query={"native_context_id": native_context_id})
    row = binding.get("binding", binding)
    return (
        "PASS",
        f"bound as {row.get('role')} ({row.get('session_context_id')})",
        "GET /v1/sessions/binding",
        {"binding": row},
    )


DASHBOARD_PAGE_JSON = "dashboard-data.json"


def _last_dashboard_refresh(page_json: Path) -> tuple[str | None, str]:
    """The `generated_at` the refresh path published to the page JSON, or why none is stated; never inferred."""
    if not page_json.is_file():
        return None, f"no {DASHBOARD_PAGE_JSON} under the runtime root"
    try:
        payload = json.loads(page_json.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None, f"{DASHBOARD_PAGE_JSON} is unreadable or malformed; nothing is inferred from it"
    generated_at = payload.get("generated_at") if isinstance(payload, dict) else None
    if not isinstance(generated_at, str):
        return None, f"{DASHBOARD_PAGE_JSON} records no refresh timestamp"
    try:
        datetime.fromisoformat(generated_at)
    except ValueError:
        return None, f"{DASHBOARD_PAGE_JSON} records a malformed refresh timestamp; nothing is inferred from it"
    return generated_at, f"{DASHBOARD_PAGE_JSON} generated_at"


def _dashboard(root: Path) -> tuple[str, str, str, dict[str, Any]]:
    """The project dashboard link as configuration states it; the derived view is described, never contacted.

    A dashboard is configured for a project root when its selected configuration `groundtruth.toml` is there: the
    launch (`gt dashboard start`) and the refresh service read that file. The link is the derivation the launch
    reports; the ports are the package defaults because a launch persists no other choice locally. Nothing is
    requested from Grafana, the refresh service or the authority, so reading this component binds no session,
    infers no role and selects no work.
    """
    source = "dashboard configuration and derived view"
    selected_configuration = root / "groundtruth.toml"
    if not selected_configuration.is_file():
        return (
            "UNKNOWN",
            f"no dashboard is configured for {root}: groundtruth.toml is absent there (the dashboard launch and its "
            "refresh service read that selected configuration), so no link is stated",
            source,
            {"configured": False, "selected_configuration": str(selected_configuration), "contacted": False},
        )
    runtime_root = default_dashboard_runtime_root(root)
    link = grafana_dashboard_url()
    last_refresh, basis = _last_dashboard_refresh(runtime_root / DASHBOARD_PAGE_JSON)
    return (
        "PASS",
        f"{link} (not contacted)",
        source,
        {
            "configured": True,
            "grafana_url": link,
            "refresh_url": refresh_service_url(),
            "runtime_root": str(runtime_root),
            "runtime_root_present": runtime_root.is_dir(),
            "landing_page_present": (runtime_root / "index.html").is_file(),
            "grafana_dashboard_present": (runtime_root / "grafana" / "dashboards" / "gtkb-dashboard.json").is_file(),
            "last_refresh": last_refresh,
            "last_refresh_basis": basis,
            "contacted": False,
        },
    )


def collect_operating_status(
    config: GTConfig,
    *,
    startup: bool = False,
    native_context_id: str | None = None,
    components: tuple[str, ...] | None = None,
) -> OperatingStatus:
    """Collect current facts through the native readers; every component is a fresh read."""
    selected = components or COMPONENTS
    unknown = sorted(set(selected) - set(COMPONENTS))
    if unknown:
        raise ValueError(f"unknown status component(s): {unknown}; expected one of: {', '.join(COMPONENTS)}")
    root = config.project_root.resolve()
    client = AuthorityClient(config.authority_url, timeout=10) if config.authority_url else None

    def needs_authority(probe: Callable[[AuthorityClient], tuple[str, str, str, dict[str, Any]]]) -> Probe:
        def run() -> tuple[str, str, str, dict[str, Any]]:
            if client is None:
                return "UNKNOWN", "no authority_url is configured", "native authority", {"configured": False}
            return probe(client)

        return run

    probes: dict[str, Probe] = {
        "authority": needs_authority(_authority),
        "project": lambda: _project(root, config),
        "bridge": needs_authority(_bridge),
        "registry": lambda: _registry(root),
        "formal": needs_authority(_formal),
        "session": needs_authority(lambda c: _session(c, native_context_id)),
        "dashboard": lambda: _dashboard(root),
    }
    collected = tuple(_timed(name, probes[name]) for name in selected)
    statuses = {component.status for component in collected}
    overall = "FAIL" if "FAIL" in statuses else ("UNKNOWN" if "UNKNOWN" in statuses else "PASS")
    return OperatingStatus(
        schema_version=1,
        package_version=__version__,
        captured_at=datetime.now(UTC).isoformat(timespec="seconds"),
        project_root=root,
        startup=startup,
        overall_status=overall,
        components=collected,
    )


def format_operating_status_text(status: OperatingStatus) -> str:
    lines = [
        f"GroundTruth KB operating status: {status.overall_status}",
        f"Project root: {status.project_root}",
        f"Captured at: {status.captured_at}",
        "",
        "Components (fresh reads; nothing here certifies a context):",
    ]
    lines.extend(f"- {component.status} {component.name}: {component.detail}" for component in status.components)
    return "\n".join(lines)


def format_startup_operating_status(status: OperatingStatus) -> str:
    lines = ["Operating State", f"- Overall: {status.overall_status}", f"- Project root: {status.project_root}"]
    lines.extend(f"- {component.name}: {component.status} - {component.detail}" for component in status.components)
    lines.append("- Context: not certified by this report; bind and read the current native context")
    return "\n".join(lines)
