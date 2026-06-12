import json
import os
import tomllib
from pathlib import Path

from .occupancy_detector import detect_occupancy
from .registry_check import has_registry_entry


def check_slot_markers(project_root: Path, slot_name: str) -> dict[str, any]:
    """Parse structured markers in applications/<slot_name>/ and validate consistency.

    Returns a dict with:
        malformed: list[dict] -> list of {path: str, error: str}
        mismatched: list[dict] -> list of {path: str, found_name: str}
        consistent: bool
        app_toml_present: bool
    """
    app_dir = project_root / "applications" / slot_name
    malformed = []
    mismatched = []

    # 1. Parse application.toml
    app_toml_path = app_dir / "application.toml"
    app_toml_name = None
    if app_toml_path.is_file():
        try:
            with open(app_toml_path, "rb") as f:
                data = tomllib.load(f)
            app_toml_name = data.get("name")
            if not app_toml_name:
                app_toml_name = data.get("application", {}).get("name")
            if app_toml_name and app_toml_name != slot_name:
                mismatched.append({"path": "application.toml", "found_name": app_toml_name})
        except Exception as e:
            malformed.append({"path": "application.toml", "error": str(e)})

    # 2. Parse .gtkb-app-isolation.json
    isolation_json_path = app_dir / ".gtkb-app-isolation.json"
    isolation_json_name = None
    if isolation_json_path.is_file():
        try:
            with open(isolation_json_path, encoding="utf-8") as f:
                data = json.load(f)
            isolation_json_name = data.get("application")
            if isolation_json_name and isolation_json_name != slot_name:
                mismatched.append({"path": ".gtkb-app-isolation.json", "found_name": isolation_json_name})
        except Exception as e:
            malformed.append({"path": ".gtkb-app-isolation.json", "error": str(e)})

    consistent = len(malformed) == 0 and len(mismatched) == 0
    return {
        "malformed": malformed,
        "mismatched": mismatched,
        "consistent": consistent,
        "app_toml_present": app_toml_path.is_file(),
    }


def evaluate_isolation_state(project_root: Path) -> dict[str, any]:
    """Scan all application slots and registry entries to compute the doctor diagnostic verdicts."""
    candidates = set()
    apps_dir = project_root / "applications"
    if apps_dir.is_dir():
        for name in os.listdir(apps_dir):
            if (apps_dir / name).is_dir():
                candidates.add(name)

    registry_path = apps_dir / "registry.toml"
    if registry_path.is_file():
        try:
            with open(registry_path, "rb") as f:
                data = tomllib.load(f)
            apps = data.get("applications", {})
            if isinstance(apps, dict):
                candidates.update(apps.keys())
        except Exception:
            pass

    candidates = {name for name in candidates if name not in {"registry.toml", "__pycache__"}}

    slots_status = {}
    occupied_slots = []

    for name in sorted(candidates):
        status = detect_occupancy(project_root, name)
        marker_check = check_slot_markers(project_root, name)

        slot_info = {
            "name": name,
            "occupied": status["occupied"],
            "trigger": status["trigger"],
            "details": status["details"],
            "marker_check": marker_check,
            "dir_exists": (apps_dir / name).is_dir(),
            "registry_exists": has_registry_entry(project_root, name),
        }
        slots_status[name] = slot_info
        if status["occupied"]:
            occupied_slots.append(name)

    verdicts = []

    # 1. Multi-slot occupancy (P0)
    if len(occupied_slots) >= 2:
        verdicts.append(
            {
                "severity": "P0",
                "verdict": "Multi-slot occupancy",
                "remediation": (
                    "Platform supports only one developed application at a time. "
                    "Run `gt application unregister <name>` to remove an application."
                ),
                "details": f"Multiple occupied slots detected: {', '.join(sorted(occupied_slots))}",
            }
        )

    for name in sorted(candidates):
        slot = slots_status[name]

        # 2. Malformed structured markers (P1)
        if slot["dir_exists"] and slot["marker_check"]["malformed"]:
            path = slot["marker_check"]["malformed"][0]["path"]
            err = slot["marker_check"]["malformed"][0]["error"]
            verdicts.append(
                {
                    "severity": "P1",
                    "verdict": "Malformed markers",
                    "remediation": (
                        f"Malformed marker at `applications/{name}/{path}`. "
                        "Manual repair required before registration can proceed."
                    ),
                    "details": f"Parse error in {path}: {err}",
                }
            )
            continue

        # 3. Mismatched marker name (P1)
        if slot["dir_exists"] and slot["marker_check"]["mismatched"]:
            path = slot["marker_check"]["mismatched"][0]["path"]
            found = slot["marker_check"]["mismatched"][0]["found_name"]
            verdicts.append(
                {
                    "severity": "P1",
                    "verdict": "Mismatched markers",
                    "remediation": (
                        f"Slot at `applications/{name}/` contains markers naming `{found}`. "
                        f"Run `gt application register {found}` (if `{found}` is the "
                        "intended occupant) or archive the slot."
                    ),
                    "details": f"Marker {path} names {found} instead of slot {name}",
                }
            )
            continue

        # 4. Registry drift (P2)
        if slot["registry_exists"] and not slot["dir_exists"]:
            verdicts.append(
                {
                    "severity": "P2",
                    "verdict": "Registry drift",
                    "remediation": (
                        f"Registry drift: registry references `{name}` but no slot directory "
                        f"exists. Run `gt application unregister {name}` to clean registry."
                    ),
                    "details": f"applications/{name}/ directory is missing but entry exists in registry.toml",
                }
            )
            continue

        # 5. Empty leftover subdirectories (P2)
        if slot["dir_exists"] and not slot["occupied"] and not slot["registry_exists"]:
            verdicts.append(
                {
                    "severity": "P2",
                    "verdict": "Empty leftover slot",
                    "remediation": (
                        f"Empty leftover slot detected at `applications/{name}/`. "
                        f"Run `rm -r applications/{name}` to clean up."
                    ),
                    "details": f"leftover slot at applications/{name}/",
                }
            )
            continue

        # 6. Partial slot registration (P1)
        if slot["occupied"] and slot["dir_exists"] and not slot["marker_check"]["app_toml_present"]:
            verdicts.append(
                {
                    "severity": "P1",
                    "verdict": "Partial slot registration",
                    "remediation": f"Run `gt application register {name}` to complete registration.",
                    "details": f"Consistent markers but missing application.toml in applications/{name}/",
                }
            )
            continue

    return {"verdicts": verdicts, "slots_status": slots_status, "occupied_slots": occupied_slots}
