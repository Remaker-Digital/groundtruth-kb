"""Tests for directive registry schema and validation."""

from __future__ import annotations

import json
from pathlib import Path
import pytest
from pydantic import ValidationError
from scripts.validate_directive_registry import RegistryModel


def test_schema_load() -> None:
    valid_data = {
        "schema_version": "1.0",
        "directives": [
            {
                "id": "DIR-TEST-001",
                "name": "Test Directive",
                "description": "Just a test",
                "non_negotiable": True,
                "enforcement_modes": ["tool-call"],
                "patterns": {"allowed_root": "E:\\GT-KB", "blocked_absolute": ["C:\\Users\\"]},
            }
        ],
    }
    registry = RegistryModel(**valid_data)
    assert registry.schema_version == "1.0"
    assert len(registry.directives) == 1
    assert registry.directives[0].id == "DIR-TEST-001"
    assert registry.directives[0].patterns.allowed_root == "E:\\GT-KB"


def test_schema_invalid_pattern() -> None:
    # id is missing, which is a required field
    invalid_data = {
        "schema_version": "1.0",
        "directives": [
            {
                "name": "Test Directive",
                "description": "Just a test",
                "non_negotiable": True,
                "enforcement_modes": ["tool-call"],
                "patterns": {},
            }
        ],
    }
    with pytest.raises(ValidationError):
        RegistryModel(**invalid_data)
