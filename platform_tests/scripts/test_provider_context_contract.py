"""Provider-context contract across the launch routes (M07.3 provider-context closure).

API-driven launchers (OpenRouter, Alibaba Cloud Studio, Ollama) host their own
model run: each run mints one fresh native context, exports it as
``GTKB_NATIVE_CONTEXT_ID`` equal to the hook payload ``session_id``, drops an
inherited ``GTKB_AUTHOR_SESSION_CONTEXT_ID`` and exports no role. External-host
launchers (Goose, Cursor) hand the run to a host that owns its native session id
(``GOOSE_SESSION_ID`` / ``CURSOR_SESSION_ID`` in the projection profiles): they
export no GT-KB context identity of their own, drop an inherited one and export
no role. In every route the role comes only from the immutable binding
(DCL-INIT-BOUND-SESSION-IDENTITY-001); a harness name or id never implies it.
Actual-host hook delivery and dispatcher activation are qualified separately.
"""

from __future__ import annotations

import os
import re
import subprocess
import sys
from pathlib import Path

import pytest
from groundtruth_kb import cursor_harness

from scripts import alibaba_cloud_studio_harness as alibaba
from scripts import cloud_harness_base as base
from scripts import ollama_harness as ollama
from scripts import openrouter_harness as openrouter

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS_DIR = ROOT / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import goose_execution_guard  # noqa: E402
import goose_harness  # noqa: E402

# A role token standing alone (not inside a longer word such as "ollama"): the launchers export none.
ROLE_TOKEN = re.compile(r"(?<![A-Za-z0-9])(prime-builder|loyal-opposition|pb|lo)(?![A-Za-z0-9])")
INHERITED = {
    "GTKB_AUTHOR_SESSION_CONTEXT_ID": "SENV-inherited-binding",
    "GTKB_NATIVE_CONTEXT_ID": "inherited-native-context",
    "GTKB_AUTHOR_IDENTITY": "prime-builder/parent/X",
    "GTKB_SESSION_ID": "legacy-session-marker",
}


def _assert_no_role(env: dict[str, str]) -> None:
    for name, value in env.items():
        if name.startswith("GTKB_"):
            assert not ROLE_TOKEN.search(value), (name, value)


def _inherit(monkeypatch) -> None:
    for name, value in INHERITED.items():
        monkeypatch.setenv(name, value)


@pytest.mark.parametrize(
    "provider,profile",
    [(openrouter, openrouter._OPENROUTER_PROFILE), (alibaba, alibaba._ALIBABA_PROFILE)],
    ids=["openrouter", "alibaba-cloud-studio"],
)
def test_cloud_launchers_export_one_fresh_native_context_and_no_role(provider, profile, tmp_path, monkeypatch):
    _inherit(monkeypatch)
    runs = []
    for _ in range(2):
        metadata = base.ModelMetadata("requested-model", "v1", "https://fixture.invalid", "fixture")
        env = base._native_hook_env(metadata, tmp_path, profile)
        payload = base._native_hook_payload("PreToolUse", metadata, tmp_path, profile, tool_name="Bash")
        assert env["GTKB_NATIVE_CONTEXT_ID"] == metadata.native_context_id == payload["session_id"]
        assert env["GTKB_NATIVE_CONTEXT_ID"] != INHERITED["GTKB_NATIVE_CONTEXT_ID"]
        assert "GTKB_AUTHOR_SESSION_CONTEXT_ID" not in env
        assert env["GTKB_AUTHOR_IDENTITY"] == provider.AUTHOR_IDENTITY == profile.author_identity
        assert env["GTKB_AUTHOR_HARNESS_ID"] == provider.AUTHOR_HARNESS_ID
        _assert_no_role(env)
        assert payload["profile"]["author_identity"] == profile.author_identity
        assert "role" not in payload and "role" not in payload["profile"]
        runs.append(metadata.native_context_id)
        # The provider's own wrapper reaches the same base contract.
        wrapped = provider.set_author_metadata_env(os.environ, "m", "v", native_context_id="ctx-1")
        assert wrapped["GTKB_NATIVE_CONTEXT_ID"] == "ctx-1" and "GTKB_AUTHOR_SESSION_CONTEXT_ID" not in wrapped
    assert len(set(runs)) == 2
    assert os.environ["GTKB_NATIVE_CONTEXT_ID"] == INHERITED["GTKB_NATIVE_CONTEXT_ID"]


def test_ollama_launcher_exports_one_fresh_native_context_and_no_role(monkeypatch):
    _inherit(monkeypatch)
    metadata = ollama.ModelMetadata("requested-model", "v1", "http://127.0.0.1:11434", "fixture")
    env = ollama.set_author_metadata_env(os.environ, "m", "v", native_context_id=metadata.native_context_id)
    assert env["GTKB_NATIVE_CONTEXT_ID"] == metadata.native_context_id != INHERITED["GTKB_NATIVE_CONTEXT_ID"]
    assert "GTKB_AUTHOR_SESSION_CONTEXT_ID" not in env
    assert env["GTKB_AUTHOR_IDENTITY"] == ollama.AUTHOR_IDENTITY == "Ollama D"
    _assert_no_role(env)
    assert ollama.ModelMetadata("m", "v", "e", "r").native_context_id != metadata.native_context_id


def test_goose_launcher_exports_harness_identity_without_role_or_inherited_context(monkeypatch, tmp_path):
    _inherit(monkeypatch)
    for name in (
        "GTKB_AUTHOR_MODEL",
        "GTKB_AUTHOR_MODEL_VERSION",
        "GTKB_AUTHOR_HARNESS_NAME",
        "GTKB_AUTHOR_HARNESS_ID",
    ):
        monkeypatch.delenv(name, raising=False)
    monkeypatch.delenv("GTKB_AUTHOR_IDENTITY", raising=False)
    goose_execution_guard.export_model_configuration("deepseek-v4-pro")
    assert os.environ["GTKB_AUTHOR_HARNESS_NAME"] == "goose" and os.environ["GTKB_AUTHOR_HARNESS_ID"] == "G"
    assert "GTKB_AUTHOR_IDENTITY" not in os.environ
    child = goose_harness.child_environment()
    assert "GTKB_AUTHOR_SESSION_CONTEXT_ID" not in child and "GTKB_NATIVE_CONTEXT_ID" not in child
    assert child["GTKB_AUTHOR_MODEL"] == "deepseek-v4-pro"
    _assert_no_role(child)
    # An explicit parent mapping is filtered the same way and is not mutated.
    parent = {"GTKB_NATIVE_CONTEXT_ID": "x", "GTKB_AUTHOR_SESSION_CONTEXT_ID": "y", "GOOSE_SESSION_ID": "host-owned"}
    assert goose_harness.child_environment(parent) == {"GOOSE_SESSION_ID": "host-owned"}
    assert parent["GTKB_NATIVE_CONTEXT_ID"] == "x"

    # The launcher passes exactly that environment to the Goose child.
    (tmp_path / "groundtruth.toml").write_text("[groundtruth]\n", encoding="utf-8")
    # The execution-floor contract is resolved before the spawn (c96); the test root carries the checkout's copy.
    floor = tmp_path / goose_harness.FLOOR_CONFIG_RELATIVE_PATH
    floor.parent.mkdir(parents=True)
    floor.write_bytes((ROOT / goose_harness.FLOOR_CONFIG_RELATIVE_PATH).read_bytes())
    launches = []

    def launch(command, **kwargs):
        launches.append((command, kwargs))
        return subprocess.CompletedProcess(command, 1, stdout="", stderr="controlled failure")

    monkeypatch.setattr(goose_harness.subprocess, "run", launch)
    monkeypatch.setattr(goose_harness, "_find_goose_cli", lambda: "goose-fixture")
    assert goose_harness.main(["--prompt", "owner prompt", "--project-root", str(tmp_path)]) == 1
    assert len(launches) == 1
    env = launches[0][1]["env"]
    assert "GTKB_AUTHOR_SESSION_CONTEXT_ID" not in env and "GTKB_NATIVE_CONTEXT_ID" not in env
    assert "GTKB_AUTHOR_IDENTITY" not in env
    assert env["GTKB_AUTHOR_HARNESS_ID"] == "G"
    _assert_no_role(env)
    assert launches[0][0][:2] == ["goose-fixture", "run"] and "owner prompt" in launches[0][0]


def test_cursor_launcher_passes_no_inherited_context_or_role(monkeypatch, tmp_path):
    _inherit(monkeypatch)
    monkeypatch.setattr(cursor_harness, "load_env_local", lambda **_kwargs: {})
    env = cursor_harness._cursor_agent_env(project_root=tmp_path)
    assert "GTKB_AUTHOR_SESSION_CONTEXT_ID" not in env and "GTKB_NATIVE_CONTEXT_ID" not in env
    assert env["GTKB_HARNESS_NAME"] == "cursor" and env["GTKB_HARNESS_ID"] == "E"
    assert "GTKB_AUTHOR_IDENTITY" not in env or env["GTKB_AUTHOR_IDENTITY"] == INHERITED["GTKB_AUTHOR_IDENTITY"]
    assert not any(
        env.get(name, "").startswith(("prime-builder", "loyal-opposition"))
        for name in ("GTKB_HARNESS_NAME", "GTKB_HARNESS_ID", "GTKB_AUTHOR_MODEL")
    )
    assert os.environ["GTKB_NATIVE_CONTEXT_ID"] == INHERITED["GTKB_NATIVE_CONTEXT_ID"]

    # The launcher passes exactly that environment to the Cursor Agent child.
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(cursor_harness, "_load_project_env_local", lambda **_kwargs: None)
    monkeypatch.setattr(cursor_harness, "_resolve_agent_command", lambda: ["C:/Tools/agent.exe"])
    monkeypatch.setattr(cursor_harness, "_skill_system_prompt", lambda skill, **_kwargs: None)
    launches = []

    def launch(command, **kwargs):
        launches.append((command, kwargs))
        return subprocess.CompletedProcess(command, 0, stdout="agent stdout\n", stderr="")

    monkeypatch.setattr(cursor_harness.subprocess, "run", launch)
    assert cursor_harness.main(["--prompt", "owner prompt", "--timeout", "5"]) == 0
    assert len(launches) == 1
    child = launches[0][1]["env"]
    assert "GTKB_AUTHOR_SESSION_CONTEXT_ID" not in child and "GTKB_NATIVE_CONTEXT_ID" not in child
    assert child["GTKB_HARNESS_ID"] == "E"


def test_no_launcher_source_assigns_a_role_bearing_identity() -> None:
    """A recurrence guard, not behavioral evidence: no launch route writes a role into a GTKB_* value."""
    sources = [
        SCRIPTS_DIR / "goose_execution_guard.py",
        SCRIPTS_DIR / "goose_harness.py",
        SCRIPTS_DIR / "cloud_harness_base.py",
        SCRIPTS_DIR / "ollama_harness.py",
        SCRIPTS_DIR / "openrouter_harness.py",
        SCRIPTS_DIR / "alibaba_cloud_studio_harness.py",
        ROOT / "groundtruth-kb/src/groundtruth_kb/cursor_harness.py",
    ]
    for source in sources:
        for line in source.read_text(encoding="utf-8").splitlines():
            if "GTKB_" in line and ("setdefault(" in line or "environ[" in line or '"GTKB_AUTHOR_IDENTITY":' in line):
                assert not any(token in line for token in ("prime-builder", "loyal-opposition")), (source.name, line)
