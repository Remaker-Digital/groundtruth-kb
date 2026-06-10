#!/usr/bin/env python3
"""Validate the directive registry schema, path sanity, and dependency registration."""

import json
import sys
from pathlib import Path

from pydantic import BaseModel


class PatternModel(BaseModel):
    allowed_root: str | None = None
    blocked_absolute: list[str] | None = None
    governed_paths: list[str] | None = None


class DirectiveModel(BaseModel):
    id: str
    name: str
    description: str
    non_negotiable: bool
    enforcement_modes: list[str]
    patterns: PatternModel


class RegistryModel(BaseModel):
    schema_version: str
    directives: list[DirectiveModel]


def validate_registry() -> None:
    project_root = Path(__file__).resolve().parent.parent
    registry_file = project_root / ".gtkb" / "directive-registry.json"
    if not registry_file.is_file():
        print(f"Error: {registry_file} not found.")
        sys.exit(1)

    try:
        content = registry_file.read_text(encoding="utf-8")
        data = json.loads(content)
        # 1. Pydantic validation
        registry = RegistryModel(**data)

        # 2. Path sanity checks
        boundary = next((d for d in registry.directives if d.id == "DIR-ROOT-BOUNDARY-001"), None)
        if not boundary:
            print("Error: DIR-ROOT-BOUNDARY-001 directive is missing.")
            sys.exit(1)

        allowed_root = boundary.patterns.allowed_root
        if not allowed_root:
            print("Error: allowed_root is missing under DIR-ROOT-BOUNDARY-001.")
            sys.exit(1)

        allowed_path = Path(allowed_root)
        if not allowed_path.is_absolute():
            print(f"Error: allowed_root '{allowed_root}' must be an absolute path.")
            sys.exit(1)

        if not allowed_path.exists():
            print(f"Error: allowed_root '{allowed_root}' does not exist on disk.")
            sys.exit(1)

        # 3. Dependency verification
        # Ensure that the Claude adapter is registered or exists
        adapter_path = project_root / ".claude" / "hooks" / "directive-enforcement-claude-adapter.py"
        if not adapter_path.is_file():
            print(f"Error: Claude adapter hook not found at {adapter_path}.")
            sys.exit(1)

        print("Directive registry validation PASSED successfully.")
        sys.exit(0)
    except Exception as exc:
        print(f"Validation FAILED: {exc}")
        sys.exit(1)


if __name__ == "__main__":
    validate_registry()
