# (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Provider routing isolation and complete baseline-derived configuration.

Synthetic inputs cover loader selection. The supported projector supplies the
baseline integration fixture. Neither model-name prefixes nor configured IDs
establish current account eligibility; that requires a separate provider check.
"""

from __future__ import annotations

import tomllib
from pathlib import Path

import pytest

from scripts import ollama_harness as oh_o
from scripts import openrouter_harness as oh_r

DEEPSEEK_ROUTING = """
schema_version = 1

[models.ollama-keep]
model_id = "ollama-thing:cloud"
provider = "ollama"
tool_calling_supported = true
allowed_tools = ["Read", "Grep", "Glob"]

[models.deepseek-v4-pro]
model_id = "deepseek/deepseek-v4-pro"
provider = "openrouter"
tool_calling_supported = true
allowed_tools = ["Read", "Write", "Edit", "Grep", "Glob", "Bash"]

[models.deepseek-v4-flash]
model_id = "deepseek/deepseek-v4-flash"
provider = "openrouter"
tool_calling_supported = true
allowed_tools = ["Read", "Write", "Edit", "Grep", "Glob", "Bash"]

[routing.ollama]
default_model = "ollama-keep"

[routing.openrouter]
default_model = "deepseek-v4-pro"

[routing.openrouter.skills]
bridge-review = "deepseek-v4-pro"
"""


def _fixture_root(tmp_path: Path, routing_text: str, config_path: Path = oh_r.ROUTING_CONFIG_PATH) -> Path:
    root = tmp_path / "repo"
    root.mkdir()
    (root / "groundtruth.toml").write_text("[project]\nname='test'\n", encoding="utf-8")
    (root / config_path).parent.mkdir(parents=True)
    (root / config_path).write_text(routing_text.strip() + "\n", encoding="utf-8")
    return root


# --- fixture-based loader behavior ---


def test_openrouter_loads_only_openrouter_models(tmp_path: Path) -> None:
    config = oh_r.load_routing_config(_fixture_root(tmp_path, DEEPSEEK_ROUTING))
    assert set(config.models.keys()) == {"deepseek-v4-pro", "deepseek-v4-flash"}
    assert "ollama-keep" not in config.models


def test_openrouter_default_resolves_to_deepseek(tmp_path: Path) -> None:
    config = oh_r.load_routing_config(_fixture_root(tmp_path, DEEPSEEK_ROUTING))
    route = oh_r.resolve_model(config, None)
    assert route.key == "deepseek-v4-pro"
    assert route.model_id == "deepseek/deepseek-v4-pro"
    assert route.tool_calling_supported is True


def test_openrouter_skill_route_resolves(tmp_path: Path) -> None:
    config = oh_r.load_routing_config(_fixture_root(tmp_path, DEEPSEEK_ROUTING))
    assert oh_r.resolve_model(config, None, skill="bridge-review").key == "deepseek-v4-pro"


def test_ollama_loader_ignores_openrouter_rows(tmp_path: Path) -> None:
    # Cross-provider isolation: the ollama loader (WI-4473 filter) loads only its own rows.
    config = oh_o.load_routing_config(_fixture_root(tmp_path, DEEPSEEK_ROUTING, oh_o.ROUTING_CONFIG_PATH))
    assert set(config.models.keys()) == {"ollama-keep"}


# --- complete generated-configuration invariants ---


@pytest.mark.timeout(300)
def test_generated_openrouter_models_preserve_only_the_provider_baseline(generated_harness_root: Path) -> None:
    config = oh_r.load_routing_config(generated_harness_root)
    baseline = tomllib.loads(
        (generated_harness_root / ".harness-baseline-configuration/routing.toml").read_text(encoding="utf-8")
    )
    expected = {key: row for key, row in baseline["models"].items() if row.get("provider") == "openrouter"}
    assert expected and set(config.models) == set(expected)
    for key, route in config.models.items():
        assert route.model_id == expected[key]["model_id"]
        assert route.allowed_tools == tuple(expected[key]["allowed_tools"])
        assert route.omit_payload_model == expected[key].get("omit_payload_model", False)


@pytest.mark.timeout(300)
def test_generated_openrouter_default_and_skill_routes_resolve(generated_harness_root: Path) -> None:
    config = oh_r.load_routing_config(generated_harness_root)
    baseline = tomllib.loads(
        (generated_harness_root / ".harness-baseline-configuration/routing.toml").read_text(encoding="utf-8")
    )
    expected = baseline["routing"]["openrouter"]
    assert config.default_model == expected["default_model"]
    assert config.skill_routes == expected["skills"]
    route = oh_r.resolve_model(config, None)
    assert route.key == expected["default_model"]
    assert route.tool_calling_supported is True
    for skill, key in expected["skills"].items():
        assert oh_r.resolve_model(config, None, skill=skill).key == key
