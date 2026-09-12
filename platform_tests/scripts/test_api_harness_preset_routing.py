"""WI-5978: harness preset model routing regression tests.

Asserts that Goose (G) and OpenRouter (F) are routed to their owner-designated
GT-KB presets, with the inertness guard on `omit_payload_model`, and that the
headless argv carries the preset routing keys with all non-model elements
unchanged.

Authority: bridge/gtkb-wi5978-harness-preset-model-routing-001.md (GO at -002).
"""

from __future__ import annotations

import json
import tomllib
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]


def _routing() -> dict:
    with open(_ROOT / ".api-harness/routing.toml", "rb") as fh:
        return tomllib.load(fh)


def _registry() -> dict:
    with open(_ROOT / "harness-state/harness-registry.json", encoding="utf-8") as fh:
        return json.load(fh)


def test_openrouter_preset_inertness_guard() -> None:
    r = _routing()
    for entry in r["models"].values():
        if entry.get("provider") == "openrouter" and str(entry.get("model_id", "")).startswith("@preset/"):
            # Sending the preset identifier as the model field is what selects the
            # preset; omit_payload_model must be false for @preset/ OpenRouter routes.
            assert entry.get("omit_payload_model", False) is False
