from __future__ import annotations

import json
import tomllib
from pathlib import Path

import pytest

from scripts import ollama_harness as oh

FULL_MODEL_ID = "fixture-full:current"
READ_ONLY_MODEL_ID = "fixture-review:current"
FULL_TOOL_SET = ("Read", "Write", "Edit", "Grep", "Glob", "Bash")


def make_root(tmp_path: Path, routing_text: str) -> Path:
    root = tmp_path / "repo"
    root.mkdir()
    (root / "groundtruth.toml").write_text("[project]\nname='test'\n", encoding="utf-8")
    (root / oh.ROUTING_CONFIG_PATH).parent.mkdir(parents=True)
    (root / oh.ROUTING_CONFIG_PATH).write_text(routing_text.strip() + "\n", encoding="utf-8")
    return root


def routing_text(extra_routing: str = "") -> str:
    return f"""
schema_version = 1

[models.full-route]
model_id = "{FULL_MODEL_ID}"
tool_calling_supported = true
allowed_tools = ["Read", "Write", "Edit", "Grep", "Glob", "Bash"]

[models.read-only-route]
model_id = "{READ_ONLY_MODEL_ID}"
tool_calling_supported = true
allowed_tools = ["Read", "Grep", "Glob"]

[routing.ollama]
default_model = "full-route"
{extra_routing}
"""


# c123 (batch design WP2 2.1): a role skill no longer selects D's model. A registration names its route with --model,
# and the loader refuses a [routing.ollama.skills] table in either form, whatever route it names.
RETIRED_SKILL_TABLE = r"routing\.ollama\.skills: routing skill tables are retired; registrations name --model"


def test_named_model_route_selects_full_tool_review_model(tmp_path: Path) -> None:
    root = make_root(tmp_path, routing_text())
    config = oh.load_routing_config(root, advertised_model_ids=[FULL_MODEL_ID, READ_ONLY_MODEL_ID])

    selected = oh.resolve_model(config, "full-route")

    assert selected.key == "full-route"
    assert selected.model_version == oh.infer_model_version(FULL_MODEL_ID)
    assert selected.allowed_tools == ("Read", "Write", "Edit", "Grep", "Glob", "Bash")


def test_explicit_model_overrides_default_route(tmp_path: Path) -> None:
    root = make_root(tmp_path, routing_text())
    config = oh.load_routing_config(root)

    selected = oh.resolve_model(config, "read-only-route")

    assert config.default_model == "full-route"
    assert selected.key == "read-only-route"
    assert selected.allowed_tools == ("Read", "Grep", "Glob")


def test_unrequested_model_uses_default_route_and_unknown_model_fails_closed(tmp_path: Path) -> None:
    root = make_root(tmp_path, routing_text())
    config = oh.load_routing_config(root)

    selected = oh.resolve_model(config, None)

    assert selected.key == "full-route"
    with pytest.raises(oh.OllamaHarnessError, match="unknown model route: unmapped-route"):
        oh.resolve_model(config, "unmapped-route")


@pytest.mark.parametrize("route_key", ["missing-route", "full-route"])
def test_retired_skill_table_is_refused_whatever_route_it_names(tmp_path: Path, route_key: str) -> None:
    root = make_root(
        tmp_path,
        routing_text(
            f"""
[routing.ollama.skills]
bridge-review = "{route_key}"
"""
        ),
    )

    with pytest.raises(oh.OllamaHarnessError, match=RETIRED_SKILL_TABLE):
        oh.load_routing_config(root)


def test_retired_table_form_skill_route_is_refused(tmp_path: Path) -> None:
    root = make_root(
        tmp_path,
        routing_text(
            """
[routing.ollama.skills.bridge-review]
model = "read-only-route"
"""
        ),
    )

    with pytest.raises(oh.OllamaHarnessError, match=RETIRED_SKILL_TABLE):
        oh.load_routing_config(root)


def test_advertised_model_validation_rejects_missing_local_model(tmp_path: Path) -> None:
    root = make_root(tmp_path, routing_text())

    with pytest.raises(oh.OllamaHarnessError, match="not advertised locally"):
        oh.load_routing_config(root, advertised_model_ids=["other:model"])


def test_advertised_model_validation_accepts_duplicate_route_model_id(tmp_path: Path) -> None:
    root = make_root(tmp_path, routing_text())

    config = oh.load_routing_config(root, advertised_model_ids=[FULL_MODEL_ID, READ_ONLY_MODEL_ID])

    assert sorted(config.models) == ["full-route", "read-only-route"]


def test_call_ollama_tags_extracts_advertised_model_names(monkeypatch: pytest.MonkeyPatch) -> None:
    requests: list[str] = []

    class Response:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, traceback):
            return False

        def read(self) -> bytes:
            return json.dumps({"models": [{"name": FULL_MODEL_ID}, {"model": "fallback:id"}]}).encode("utf-8")

    def fake_urlopen(request, timeout: float):
        requests.append(request.full_url)
        return Response()

    monkeypatch.setattr(oh.urllib.request, "urlopen", fake_urlopen)

    assert oh.call_ollama_tags("http://ollama.test/") == (FULL_MODEL_ID, "fallback:id")
    assert requests == ["http://ollama.test/api/tags"]


@pytest.mark.timeout(300)
def test_generated_routing_config_preserves_baseline_routes_without_skill_tables(generated_harness_root: Path) -> None:
    """Derivation/selection only; configured IDs are not a live model inventory."""
    repo_root = generated_harness_root
    baseline = tomllib.loads((repo_root / ".harness-baseline-configuration/routing.toml").read_text(encoding="utf-8"))
    config = oh.load_routing_config(repo_root)

    assert config.default_model == baseline["routing"]["ollama"]["default_model"]
    # c123 (batch design WP2 2.1): the baseline has no skill table, and every model row is selectable by its key.
    assert "skills" not in baseline["routing"]["ollama"]
    expected = {key: row for key, row in baseline["models"].items() if row.get("provider") == "ollama"}
    assert set(config.models) == set(expected)
    assert {key: row.model_id for key, row in config.models.items()} == {
        key: row["model_id"] for key, row in expected.items()
    }
    for key in config.models:
        assert oh.resolve_model(config, key).key == key
    # D's corrected registration names --model deepseek-v4-flash-cloud (batch design WP2 2.1, step 3): the review
    # route it names, like the default, carries the full tool set.
    for selected in (oh.resolve_model(config, None), oh.resolve_model(config, "deepseek-v4-flash-cloud")):
        assert selected.allowed_tools == FULL_TOOL_SET
        assert selected.model_version == oh.infer_model_version(selected.model_id)
    assert "model_version" not in (repo_root / oh.ROUTING_CONFIG_PATH).read_text(encoding="utf-8")
