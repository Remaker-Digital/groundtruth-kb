from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = REPO_ROOT / "scripts" / "codex_shell_no_window_wrapper.py"


def _load_module():
    if str(REPO_ROOT) not in sys.path:
        sys.path.insert(0, str(REPO_ROOT))
    spec = importlib.util.spec_from_file_location("codex_shell_no_window_wrapper", SCRIPT_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_run_wrapped_uses_no_window_subprocess_kwargs(monkeypatch) -> None:
    module = _load_module()
    captured: dict[str, object] = {}

    def fake_run(command, **kwargs):
        captured["command"] = command
        captured["kwargs"] = kwargs
        return subprocess.CompletedProcess(command, 7)

    monkeypatch.setattr(module, "no_window_subprocess_kwargs", lambda: {"creationflags": 0x08000000})
    monkeypatch.setattr(module.subprocess, "run", fake_run)

    result = module.run_wrapped(["pwsh", "-NoProfile", "-Command", "echo ok"])

    assert result == 7
    assert captured["command"] == ["pwsh", "-NoProfile", "-Command", "echo ok"]
    assert captured["kwargs"]["creationflags"] == 0x08000000
    assert captured["kwargs"]["check"] is False


def test_main_accepts_separator(monkeypatch) -> None:
    module = _load_module()
    monkeypatch.setattr(module, "run_wrapped", lambda command: 0 if command == ["echo", "ok"] else 9)

    assert module.main(["--", "echo", "ok"]) == 0
