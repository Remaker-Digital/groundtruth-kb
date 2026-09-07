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


def test_goose_routes_to_gtkb_v4f_preset() -> None:
    r = _routing()
    models = r["models"]
    g = r["routing"]["goose"]
    for key in [g["default_model"], *g["skills"].values()]:
        assert key == "gtkb-v4f-goose"
        assert models[key]["model_id"] == "@preset/gtkb-v4f"
        assert models[key]["provider"] == "goose"


def test_openrouter_routes_to_gtkb_preset() -> None:
    r = _routing()
    models = r["models"]
    o = r["routing"]["openrouter"]
    for key in [o["default_model"], *o["skills"].values()]:
        assert key == "gtkb-v4f-openrouter"
        assert models[key]["model_id"] == "@preset/gtkb-openrouter-deepseek-v4-flash"
        assert models[key]["provider"] == "openrouter"


def test_openrouter_preset_inertness_guard() -> None:
    r = _routing()
    for entry in r["models"].values():
        if entry.get("provider") == "openrouter" and str(entry.get("model_id", "")).startswith("@preset/"):
            # Sending the preset identifier as the model field is what selects the
            # preset; omit_payload_model must be false for @preset/ OpenRouter routes.
            assert entry.get("omit_payload_model", False) is False


def test_headless_argv_names_preset_routing_keys_and_preserves_non_model() -> None:
    reg = _registry()
    harnesses = {h["id"]: h for h in reg["harnesses"]}

    g_argv = harnesses["G"]["invocation_surfaces"]["headless"]["argv"]
    assert g_argv == [
        "groundtruth-kb/.venv/Scripts/python.exe",
        "scripts/goose_harness.py",
        "-p",
        "{{PROMPT}}",
        "--skill",
        "bridge-review",
        "--model",
        "gtkb-v4f-goose",
    ]

    f_argv = harnesses["F"]["invocation_surfaces"]["headless"]["argv"]
    assert f_argv == [
        "groundtruth-kb/.venv/Scripts/python.exe",
        "scripts/openrouter_harness.py",
        "-p",
        "{{PROMPT}}",
        "--model",
        "gtkb-v4f-openrouter",
        "--skill",
        "bridge-review",
        "--max-turns",
        "200",
        "--timeout",
        "60",
        "--session-timeout",
        "5400",
    ]


def test_allowed_tools_preserved() -> None:
    r = _routing()
    models = r["models"]
    for key in ("gtkb-v4f-goose", "gtkb-v4f-openrouter"):
        assert models[key]["allowed_tools"] == ["Read", "Write", "Edit", "Grep", "Glob", "Bash"]


def test_deleted_openrouter_preset_identifier_is_unreferenced() -> None:
    stale_identifier = "gt-kb-openrouter-harness-deepdeek-v4-flash"
    routing_text = (_ROOT / ".api-harness/routing.toml").read_text(encoding="utf-8")
    registry_text = (_ROOT / "harness-state/harness-registry.json").read_text(encoding="utf-8")

    assert stale_identifier not in routing_text
    assert stale_identifier not in registry_text
