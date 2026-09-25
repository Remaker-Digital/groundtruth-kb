"""GT-KB's OpenRouter harness authenticates with GT-KB's named credential (host F; owner direction 2026-09-24).

``.env.local`` defines GTKB_OPENROUTER_API_KEY (GOV-ENV-LOCAL-AUTHORITY-001); the launcher read only the conventional
OPENROUTER_API_KEY and so could never authenticate on the owner's installation. It now prefers the GT-KB name and keeps
the conventional name as a fallback. Values here are fixtures.
"""

from __future__ import annotations

import os
from pathlib import Path

import pytest

from platform_tests.scripts.openrouter_fixtures import make_root
from scripts import _env as env_loader
from scripts import openrouter_harness as orh


def _dispatch(monkeypatch, tmp_path: Path, env_file: dict[str, str], process: dict[str, str]):
    root = make_root(tmp_path)
    config = orh.load_routing_config(root)
    monkeypatch.chdir(root)
    for name in ("GTKB_OPENROUTER_API_KEY", "OPENROUTER_API_KEY"):
        monkeypatch.delenv(name, raising=False)
    for name, value in process.items():
        monkeypatch.setenv(name, value)

    def fake_load_env_local() -> dict[str, str]:
        for name, value in env_file.items():  # the loader never overrides a process value
            if name not in os.environ:
                monkeypatch.setenv(name, value)
        return dict(env_file)

    seen: dict[str, str] = {}

    def fake_run_tool_loop(prompt, model_route, endpoint, api_key, max_turns, project_root, **kwargs) -> str:
        seen["api_key"] = api_key
        return "done"

    monkeypatch.setattr(env_loader, "load_env_local", fake_load_env_local)
    monkeypatch.setattr(orh, "load_routing_config", lambda _project_root: config)
    monkeypatch.setattr(orh, "run_tool_loop", fake_run_tool_loop)
    return orh.main(["-p", "hello", "--skill", "bridge-review"]), seen


def test_the_gtkb_named_credential_from_env_local_authenticates(monkeypatch, tmp_path):
    code, seen = _dispatch(monkeypatch, tmp_path, {"GTKB_OPENROUTER_API_KEY": "gtkb-fixture"}, {})
    assert code == 0 and seen["api_key"] == "gtkb-fixture"


def test_the_gtkb_name_wins_over_the_conventional_name(monkeypatch, tmp_path):
    code, seen = _dispatch(
        monkeypatch, tmp_path, {"GTKB_OPENROUTER_API_KEY": "gtkb-fixture"}, {"OPENROUTER_API_KEY": "generic"}
    )
    assert code == 0 and seen["api_key"] == "gtkb-fixture"


def test_the_conventional_name_still_works_alone(monkeypatch, tmp_path):
    code, seen = _dispatch(monkeypatch, tmp_path, {}, {"OPENROUTER_API_KEY": "generic"})
    assert code == 0 and seen["api_key"] == "generic"


def test_without_either_name_the_failure_names_both(monkeypatch, tmp_path, capsys: pytest.CaptureFixture[str]):
    code, seen = _dispatch(monkeypatch, tmp_path, {}, {})
    assert code == 1 and not seen
    err = capsys.readouterr().err
    assert "GTKB_OPENROUTER_API_KEY is not set" in err and "OPENROUTER_API_KEY environment variable is not set" in err


def test_the_adopter_profile_names_the_gtkb_credential():
    assert orh._OPENROUTER_PROFILE.auth_env_key == "GTKB_OPENROUTER_API_KEY"
