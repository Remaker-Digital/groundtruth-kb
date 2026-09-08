"""Hook registration retirement lock for the mechanical implementation-start gate.

Owner ruling 2026-09-07 (canon v8.92) retired the gate. These tests lock its
absence from every projected hook-registration surface and from the Codex
batch catalog, so a stale render or residue file cannot re-arm it silently.
"""
# ruff: noqa: I001

from __future__ import annotations

import importlib.util
import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
WRAPPER_PATH = REPO_ROOT / ".codex" / "gtkb-hooks" / "run_py_no_window.py"
RETIRED_GATE_TOKEN = "implementation-start-gate"
REGISTRATION_SURFACES = (
    Path(".claude") / "settings.json",
    Path(".cursor") / "hooks.json",
    Path(".goose") / "plugins" / "gtkb" / "hooks" / "hooks.json",
    Path(".codex") / "hooks.json",
)


def _load_codex_hook_wrapper():
    spec = importlib.util.spec_from_file_location("codex_run_py_no_window_parity", WRAPPER_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _hook_commands(payload: object) -> list[str]:
    commands: list[str] = []
    if isinstance(payload, dict):
        command = payload.get("command")
        if isinstance(command, str):
            commands.append(command)
        for value in payload.values():
            commands.extend(_hook_commands(value))
    elif isinstance(payload, list):
        for value in payload:
            commands.extend(_hook_commands(value))
    return commands


def test_no_registration_surface_names_implementation_start_gate() -> None:
    for relative in REGISTRATION_SURFACES:
        surface = REPO_ROOT / relative
        assert surface.is_file(), relative
        commands = _hook_commands(json.loads(surface.read_text(encoding="utf-8")).get("hooks", {}))
        assert commands, relative
        offenders = [command for command in commands if RETIRED_GATE_TOKEN in command]
        assert not offenders, f"{relative} still registers the retired gate: {offenders}"


def test_codex_batch_catalog_does_not_run_implementation_start_gate() -> None:
    hooks = json.loads((REPO_ROOT / ".codex" / "hooks.json").read_text(encoding="utf-8"))
    assert RETIRED_GATE_TOKEN not in json.dumps(hooks, sort_keys=True)

    wrapper = _load_codex_hook_wrapper()
    for batch_name, entries in wrapper.BATCHES.items():
        assert not any(RETIRED_GATE_TOKEN in " ".join(entry) for entry in entries), batch_name

    assert not (REPO_ROOT / ".codex" / "gtkb-hooks" / "implementation-start-gate.cmd").exists()
