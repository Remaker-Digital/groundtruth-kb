import json
import sys
import tomllib
from pathlib import Path


class ValidationError(Exception):
    """Exception raised when slot preflight validation fails."""

    pass


def validate_self_completion_preflight(project_root: Path, slot_name: str) -> None:
    """Validate name consistency and structured marker compatibility.

    Raises ValidationError on abort conditions.
    """
    app_dir = project_root / "applications" / slot_name

    # 1. Parse application.toml
    app_toml_path = app_dir / "application.toml"
    if app_toml_path.is_file():
        try:
            with open(app_toml_path, "rb") as f:
                data = tomllib.load(f)
        except Exception as e:
            raise ValidationError(
                f"Malformed marker at `applications/{slot_name}/application.toml`: {e}. "
                "Manually inspect or restore from backup."
            )

        app_name = data.get("name")
        if not app_name:
            app_name = data.get("application", {}).get("name")
        if app_name and app_name != slot_name:
            raise ValidationError(
                f"Slot `applications/{slot_name}/` contains marker `application.toml` naming application `{app_name}`. "
                f"This is a slot-name mismatch. Run `gt application register {app_name}` to claim it for `{app_name}`, "
                f"or manually archive the slot if it should be removed."
            )

    # 2. Parse .gtkb-app-isolation.json
    isolation_json_path = app_dir / ".gtkb-app-isolation.json"
    if isolation_json_path.is_file():
        try:
            with open(isolation_json_path, encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            raise ValidationError(
                f"Malformed marker at `applications/{slot_name}/.gtkb-app-isolation.json`: {e}. "
                "Manually inspect or restore from backup."
            )

        app_name = data.get("application")
        if app_name and app_name != slot_name:
            raise ValidationError(
                f"Slot `applications/{slot_name}/` contains marker `.gtkb-app-isolation.json` naming application `{app_name}`. "
                f"This is a slot-name mismatch. Run `gt application register {app_name}` to claim it for `{app_name}`, "
                f"or manually archive the slot if it should be removed."
            )

        schema_version = data.get("schema_version")
        if schema_version is not None:
            if not isinstance(schema_version, (str, int, float)):
                raise ValidationError(
                    f"Marker at `applications/{slot_name}/.gtkb-app-isolation.json` is schema-incompatible: "
                    f"schema_version = {schema_version}. Run `gt application repair {slot_name}` or manually edit and retry."
                )
            try:
                version_val = float(schema_version)
            except ValueError:
                version_val = 1.0
            if version_val > 1.0:
                print(
                    f"Warning: schema version {schema_version} newer than supported 1.0; "
                    "proceeding under best-effort interpretation",
                    file=sys.stderr,
                )

        if "application" not in data:
            raise ValidationError(
                f"Marker at `applications/{slot_name}/.gtkb-app-isolation.json` is schema-incompatible: "
                f"application = None. Run `gt application repair {slot_name}` or manually edit and retry."
            )
