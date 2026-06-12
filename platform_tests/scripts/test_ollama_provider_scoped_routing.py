# (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Tests for WI-4473: provider-scoped model loading in the Ollama harness.

Spec-derived from ``bridge/gtkb-ollama-harness-provider-scoped-model-validation-001.md``
(GO at -002). The Ollama harness's ``load_routing_config`` must load/validate only
``provider == "ollama"`` rows from the shared ``.api-harness/routing.toml`` so that
``provider == "openrouter"`` rows do not get checked against the local Ollama
``/api/tags`` inventory (the 508-failure root cause). An absent ``provider`` defaults
to ``"ollama"`` for backward compatibility.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from scripts import ollama_harness as oh

OLLAMA_MODEL_ID = "ollama-model:current"
OLLAMA_LEGACY_MODEL_ID = "ollama-legacy:current"
OPENROUTER_MODEL_ID = "deepseek/deepseek-v4-pro"


def make_root(tmp_path: Path, routing_text: str) -> Path:
    root = tmp_path / "repo"
    root.mkdir()
    (root / "groundtruth.toml").write_text("[project]\nname='test'\n", encoding="utf-8")
    (root / ".api-harness").mkdir()
    (root / oh.ROUTING_CONFIG_PATH).write_text(routing_text.strip() + "\n", encoding="utf-8")
    return root


def mixed_provider_routing() -> str:
    """A routing.toml with ollama, ollama (absent provider), and openrouter rows."""
    return f"""
schema_version = 1

[models.ollama-default]
model_id = "{OLLAMA_MODEL_ID}"
provider = "ollama"
tool_calling_supported = true
allowed_tools = ["Read", "Write", "Edit", "Grep", "Glob", "Bash"]

[models.ollama-no-provider]
model_id = "{OLLAMA_LEGACY_MODEL_ID}"
tool_calling_supported = true
allowed_tools = ["Read", "Grep", "Glob"]

[models.openrouter-one]
model_id = "{OPENROUTER_MODEL_ID}"
provider = "openrouter"
tool_calling_supported = true
allowed_tools = ["Read", "Write", "Edit", "Grep", "Glob", "Bash"]

[routing.ollama]
default_model = "ollama-default"

[routing.ollama.skills]
bridge-review = "ollama-default"
"""


def _advertised() -> list[str]:
    # Simulates the local Ollama /api/tags inventory: only ollama-provider models.
    return [OLLAMA_MODEL_ID, OLLAMA_LEGACY_MODEL_ID]


def test_load_routing_config_loads_only_ollama_models(tmp_path: Path) -> None:
    root = make_root(tmp_path, mixed_provider_routing())
    config = oh.load_routing_config(root, advertised_model_ids=_advertised())
    assert set(config.models.keys()) == {"ollama-default", "ollama-no-provider"}
    assert "openrouter-one" not in config.models


def test_absent_provider_row_defaults_to_ollama(tmp_path: Path) -> None:
    root = make_root(tmp_path, mixed_provider_routing())
    config = oh.load_routing_config(root, advertised_model_ids=_advertised())
    # The row with no `provider` key is treated as ollama (backward compatibility).
    assert "ollama-no-provider" in config.models
    assert config.models["ollama-no-provider"].model_id == OLLAMA_LEGACY_MODEL_ID


def test_validate_advertised_models_passes_after_provider_filter(tmp_path: Path) -> None:
    root = make_root(tmp_path, mixed_provider_routing())
    # The openrouter model id is NOT in the advertised set. Pre-fix this raised
    # "configured model_id values are not advertised locally"; post-fix the
    # openrouter row is never loaded, so validation passes.
    config = oh.load_routing_config(root, advertised_model_ids=_advertised())
    assert config is not None  # no OllamaHarnessError raised


def test_openrouter_model_id_not_in_validated_set(tmp_path: Path) -> None:
    root = make_root(tmp_path, mixed_provider_routing())
    config = oh.load_routing_config(root, advertised_model_ids=_advertised())
    configured_ids = {route.model_id for route in config.models.values()}
    assert OPENROUTER_MODEL_ID not in configured_ids
    assert OLLAMA_MODEL_ID in configured_ids
    assert OLLAMA_LEGACY_MODEL_ID in configured_ids


def test_default_and_skill_routes_still_resolve(tmp_path: Path) -> None:
    root = make_root(tmp_path, mixed_provider_routing())
    config = oh.load_routing_config(root, advertised_model_ids=_advertised())
    assert oh.resolve_model(config, None).key == "ollama-default"
    assert oh.resolve_model(config, None, skill="bridge-review").key == "ollama-default"


def test_unadvertised_ollama_model_still_raises(tmp_path: Path) -> None:
    # The filter must NOT suppress a genuine "ollama model not advertised" error:
    # if an ollama-provider model is configured but absent from /api/tags, the
    # harness should still fail closed.
    root = make_root(tmp_path, mixed_provider_routing())
    with pytest.raises(oh.OllamaHarnessError):
        oh.load_routing_config(root, advertised_model_ids=[OLLAMA_MODEL_ID])  # missing ollama-legacy
