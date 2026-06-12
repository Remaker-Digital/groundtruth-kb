# (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Tests for WI-4476: OpenRouter routing re-pointed to cost-optimized DeepSeek models.

Spec-derived from ``bridge/gtkb-openrouter-routing-deepseek-cost-optimization-001.md``
(GO at -002). The ``provider="openrouter"`` rows in ``.api-harness/routing.toml`` must
point at account-eligible providers (deepseek/qwen/moonshotai) rather than the
account-ineligible ``google/`` / ``openai/`` slugs that returned HTTP 404
"No allowed providers". Structural loader behavior is exercised against a fixture; the
live-config invariant guards against a regression back to ineligible slugs.
"""

from __future__ import annotations

from pathlib import Path

from scripts import ollama_harness as oh_o
from scripts import openrouter_harness as oh_r

REPO_ROOT = Path(__file__).resolve().parents[2]
ELIGIBLE_PROVIDER_PREFIXES = ("deepseek/", "qwen/", "moonshotai/")
INELIGIBLE_PROVIDER_PREFIXES = ("google/", "openai/", "azure/", "anthropic/")

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


def _fixture_root(tmp_path: Path, routing_text: str) -> Path:
    root = tmp_path / "repo"
    root.mkdir()
    (root / "groundtruth.toml").write_text("[project]\nname='test'\n", encoding="utf-8")
    (root / ".api-harness").mkdir()
    (root / oh_r.ROUTING_CONFIG_PATH).write_text(routing_text.strip() + "\n", encoding="utf-8")
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
    config = oh_o.load_routing_config(_fixture_root(tmp_path, DEEPSEEK_ROUTING))
    assert set(config.models.keys()) == {"ollama-keep"}


# --- live-config invariant (WI-4476 regression guard) ---


def test_live_openrouter_models_are_account_eligible() -> None:
    config = oh_r.load_routing_config(REPO_ROOT)
    assert config.models, "expected at least one openrouter model in the live routing.toml"
    for route in config.models.values():
        mid = route.model_id
        assert not mid.startswith(INELIGIBLE_PROVIDER_PREFIXES), (
            f"openrouter model {mid!r} uses an account-ineligible provider (the 404 root cause)"
        )
        assert mid.startswith(ELIGIBLE_PROVIDER_PREFIXES), (
            f"openrouter model {mid!r} should use an account-eligible provider"
        )


def test_live_openrouter_default_resolves() -> None:
    config = oh_r.load_routing_config(REPO_ROOT)
    route = oh_r.resolve_model(config, None)
    assert route.model_id.startswith(ELIGIBLE_PROVIDER_PREFIXES)
    assert route.tool_calling_supported is True
