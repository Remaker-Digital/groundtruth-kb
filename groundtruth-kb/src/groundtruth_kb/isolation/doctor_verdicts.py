"""Read-only application diagnostics, not formal bridge verdicts or authorization."""

from pathlib import Path
from typing import Any

from .app_root_minimization import REGISTRY_FILENAME, validate_app_root_minimization
from .occupancy_detector import detect_occupancy
from .registry_check import ApplicationRegistryError, application_slot_path, load_application_catalog
from .validation import check_slot_markers


def evaluate_isolation_state(project_root: Path) -> dict[str, Any]:
    """Check every catalog entry and actual slot without inferring an application limit."""
    verdicts: list[dict[str, str]] = []
    slots_status: dict[str, dict[str, Any]] = {}
    occupied_slots: list[str] = []
    result: dict[str, Any] = {
        "verdicts": verdicts,
        "slots_status": slots_status,
        "occupied_slots": occupied_slots,
    }

    def finding(title: str, details: str, *, severity: str = "P1") -> None:
        verdicts.append(
            {
                "severity": severity,
                "verdict": title,
                "details": details,
                "remediation": "Reconcile application boundary and registry facts; preserve existing content.",
            }
        )

    try:
        catalog = load_application_catalog(project_root)
        apps_dir = Path(project_root).resolve() / "applications"
        candidates = set(catalog)
        if apps_dir.exists():
            if not apps_dir.is_dir():
                raise ApplicationRegistryError("applications path is not a directory")
            candidates.update(p.name for p in apps_dir.iterdir() if p.is_dir())
    except (ApplicationRegistryError, OSError) as exc:
        finding("Application catalog invalid", str(exc))
        return result
    for name in sorted(candidates):
        try:
            app_dir = application_slot_path(project_root, name)
            status = detect_occupancy(project_root, name)
        except (ApplicationRegistryError, OSError) as exc:
            finding("Application slot invalid", f"{name}: {exc}")
            continue
        markers = check_slot_markers(project_root, name)
        slot = {
            "name": name,
            "occupied": status["occupied"],
            "trigger": status["trigger"],
            "details": status["details"],
            "marker_check": markers,
            "dir_exists": app_dir.is_dir(),
            "registry_exists": name in catalog,
        }
        slots_status[name] = slot
        if status["occupied"]:
            occupied_slots.append(name)
        if markers["mismatched"]:
            issue = markers["mismatched"][0]
            finding("Mismatched markers", f"applications/{name}/{issue['path']} names {issue['found_name']}")
        elif markers["malformed"]:
            issue = markers["malformed"][0]
            finding("Malformed markers", f"applications/{name}/{issue['path']}: {issue['error']}")
        elif name in catalog and not app_dir.is_dir():
            finding(
                "Registry drift", f"Registered application directory applications/{name}/ is missing", severity="P2"
            )
        elif name not in catalog:
            title = "Unregistered application content" if status["occupied"] else "Empty unregistered slot"
            finding(title, f"applications/{name}/ has no application catalog entry", severity="P2")
        elif not markers["app_toml_present"] or not (app_dir / REGISTRY_FILENAME).is_file():
            finding(
                "Partial slot registration", f"applications/{name}/ lacks application.toml or its artifact registry"
            )
        else:
            boundary = validate_app_root_minimization(app_dir, project_root=project_root)
            if not boundary.ok:
                finding("Application registry boundary", f"applications/{name}/: {boundary.first_error_message()}")
    return result
