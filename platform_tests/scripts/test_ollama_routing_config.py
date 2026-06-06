from __future__ import annotations

import json
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
    (root / ".ollama").mkdir()
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

[routing]
default_model = "full-route"
{extra_routing}
"""


def test_skill_route_selects_full_tool_review_model(tmp_path: Path) -> None:
    root = make_root(
        tmp_path,
        routing_text(
            """
[routing.skills]
bridge-review = "full-route"
"""
        ),
    )
    config = oh.load_routing_config(root, advertised_model_ids=[FULL_MODEL_ID, READ_ONLY_MODEL_ID])

    selected = oh.resolve_model(config, None, skill="bridge-review")

    assert selected.key == "full-route"
    assert selected.model_version == oh.infer_model_version(FULL_MODEL_ID)
    assert selected.allowed_tools == ("Read", "Write", "Edit", "Grep", "Glob", "Bash")


def test_explicit_model_overrides_skill_route(tmp_path: Path) -> None:
    root = make_root(
        tmp_path,
        routing_text(
            """
[routing.skills]
bridge-review = "read-only-route"
"""
        ),
    )
    config = oh.load_routing_config(root)

    selected = oh.resolve_model(config, "full-route", skill="bridge-review")

    assert selected.key == "full-route"
    assert selected.allowed_tools == ("Read", "Write", "Edit", "Grep", "Glob", "Bash")


def test_unknown_skill_uses_default_route(tmp_path: Path) -> None:
    root = make_root(
        tmp_path,
        routing_text(
            """
[routing.skills]
bridge-review = "read-only-route"
"""
        ),
    )
    config = oh.load_routing_config(root)

    selected = oh.resolve_model(config, None, skill="unmapped-skill")

    assert selected.key == "full-route"


def test_invalid_skill_route_reference_fails_closed(tmp_path: Path) -> None:
    root = make_root(
        tmp_path,
        routing_text(
            """
[routing.skills]
bridge-review = "missing-route"
"""
        ),
    )

    with pytest.raises(oh.OllamaHarnessError, match=r"routing\.skills\.bridge-review"):
        oh.load_routing_config(root)


def test_table_form_skill_route_reference_is_supported(tmp_path: Path) -> None:
    root = make_root(
        tmp_path,
        routing_text(
            """
[routing.skills.bridge-review]
model = "read-only-route"
"""
        ),
    )
    config = oh.load_routing_config(root)

    assert oh.resolve_model(config, None, skill="bridge-review").key == "read-only-route"


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


def test_repository_routing_config_has_skill_overrides() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    raw_config = oh.load_routing_config(repo_root)
    advertised = [route.model_id for route in raw_config.models.values()]
    config = oh.load_routing_config(repo_root, advertised_model_ids=advertised)

    assert config.default_model in config.models
    for skill in ("bridge-review", "verification", "implementation"):
        assert config.skill_routes[skill] in config.models
    assert config.skill_routes["verification"] == config.skill_routes["bridge-review"]
    selected = oh.resolve_model(config, None, skill="bridge-review")
    assert selected.key == config.skill_routes["bridge-review"]
    assert selected.allowed_tools == FULL_TOOL_SET
    assert selected.model_version == oh.infer_model_version(selected.model_id)
    assert "model_version" not in (repo_root / ".ollama" / "routing.toml").read_text(encoding="utf-8")
