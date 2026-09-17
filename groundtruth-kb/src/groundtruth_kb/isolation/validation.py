"""One structured-marker reader shared by preflight and diagnostics."""

import json
import tomllib
from pathlib import Path
from typing import Any

from .app_root_minimization import REGISTRY_FILENAME, AppRootFinding, _normalize_registry_entries, _unique_object
from .registry_check import ApplicationRegistryError, application_slot_path


class ValidationError(ValueError):
    """Application marker preflight failed without changing application state."""


def check_slot_markers(project_root: Path, slot_name: str) -> dict[str, Any]:
    """Inspect marker identity and schema only; inventory/lifecycle checks are separate."""
    malformed: list[dict[str, str]] = []
    mismatched: list[dict[str, str]] = []
    result = {"malformed": malformed, "mismatched": mismatched, "consistent": False, "app_toml_present": False}
    try:
        app_dir = application_slot_path(project_root, slot_name)
    except ApplicationRegistryError as exc:
        malformed.append({"path": "slot", "error": str(exc)})
        return result
    for name in ("application.toml", REGISTRY_FILENAME):
        path = app_dir / name
        try:
            if path.resolve() != path:
                raise ValueError("marker must be a direct file in the application slot")
            if not path.exists():
                continue
            if not path.is_file():
                raise ValueError("marker must be a file")
            if name == "application.toml":
                result["app_toml_present"] = True
                payload = tomllib.loads(path.read_text(encoding="utf-8"))
                nested = payload.get("application", {})
                if not isinstance(nested, dict):
                    raise ValueError("application marker table must be an object")
                names = [value for value in (payload.get("name"), nested.get("name")) if value is not None]
                if not names or any(not isinstance(value, str) or not value for value in names):
                    raise ValueError("application marker requires a non-empty name")
                if len(set(names)) != 1:
                    raise ValueError("application marker contains conflicting names")
                found_name = names[0]
            else:
                payload = json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=_unique_object)
                if not isinstance(payload, dict):
                    raise ValueError("application registry marker must be an object")
                found_name = payload.get("application")
                findings: list[AppRootFinding] = []
                _normalize_registry_entries(payload, Path(project_root), path, findings)
                malformed.extend(
                    {"path": name, "error": f"{finding.code}: {finding.message}"}
                    for finding in findings
                    if finding.code != "application_mismatch"
                )
            if isinstance(found_name, str) and found_name and found_name != slot_name:
                mismatched.append({"path": name, "found_name": found_name})
        except (OSError, UnicodeError, ValueError, RuntimeError) as exc:
            malformed.append({"path": name, "error": str(exc)})
    result["consistent"] = not malformed and not mismatched
    return result


def validate_self_completion_preflight(project_root: Path, slot_name: str) -> None:
    """Refuse invalid existing markers; success is not registration or write authority."""
    result = check_slot_markers(project_root, slot_name)
    if result["mismatched"]:
        issue = result["mismatched"][0]
        raise ValidationError(
            f"Application slot-name mismatch: {issue['path']} names {issue['found_name']} instead of {slot_name}. "
            "Reconcile the selected slot and marker identity before retrying."
        )
    if result["malformed"]:
        issue = result["malformed"][0]
        raise ValidationError(
            f"Invalid application marker {issue['path']}: {issue['error']}. "
            "Reconcile the marker with the current application registry contract before retrying."
        )
