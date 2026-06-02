"""Tests for scripts/bridge_claim_cli.py work-intent claim surface."""

from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = PROJECT_ROOT / "scripts" / "bridge_claim_cli.py"


def _load_cli():
    spec = importlib.util.spec_from_file_location("bridge_claim_cli", SCRIPT_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    try:
        spec.loader.exec_module(module)
        return module
    finally:
        sys.modules.pop(spec.name, None)


def _run_cli(tmp_path: Path, *args: str, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    run_env = os.environ.copy()
    for key in (
        "CLAUDE_SESSION_ID",
        "GTKB_INHERITED_SESSION_ID",
        "CODEX_SESSION_ID",
        "CODEX_THREAD_ID",
        "ANTIGRAVITY_SESSION_ID",
        "GTKB_SESSION_ID",
    ):
        run_env.pop(key, None)
    if env:
        run_env.update(env)
    return subprocess.run(
        [sys.executable, str(SCRIPT_PATH), *args, "--project-root", str(tmp_path)],
        capture_output=True,
        env=run_env,
        text=True,
        timeout=30,
    )


def test_resolve_session_id_uses_harness_neutral_fallbacks(monkeypatch) -> None:
    cli = _load_cli()
    monkeypatch.delenv("CLAUDE_SESSION_ID", raising=False)
    monkeypatch.setenv("CODEX_THREAD_ID", "codex-thread-123")

    assert cli._resolve_session_id(None) == "codex-thread-123"
    assert cli._resolve_session_id("explicit-session") == "explicit-session"


def test_claim_release_status_round_trip_with_codex_env(tmp_path: Path) -> None:
    claim = _run_cli(
        tmp_path,
        "claim",
        "gtkb-demo-thread",
        env={"CODEX_THREAD_ID": "codex-thread-123"},
    )
    assert claim.returncode == 0, claim.stderr
    holder = json.loads(claim.stdout)
    assert holder["session_id"] == "codex-thread-123"

    status = _run_cli(tmp_path, "status", "gtkb-demo-thread")
    assert status.returncode == 0, status.stderr
    assert json.loads(status.stdout)["session_id"] == "codex-thread-123"

    release = _run_cli(
        tmp_path,
        "release",
        "gtkb-demo-thread",
        env={"CODEX_THREAD_ID": "codex-thread-123"},
    )
    assert release.returncode == 0, release.stderr

    cleared = _run_cli(tmp_path, "status", "gtkb-demo-thread")
    assert cleared.returncode == 0, cleared.stderr
    assert cleared.stdout.strip() == "null"


def test_claim_refused_when_other_session_holds_slug(tmp_path: Path) -> None:
    first = _run_cli(tmp_path, "claim", "gtkb-demo-thread", env={"CLAUDE_SESSION_ID": "session-a"})
    assert first.returncode == 0, first.stderr

    second = _run_cli(tmp_path, "claim", "gtkb-demo-thread", env={"GTKB_INHERITED_SESSION_ID": "session-b"})
    assert second.returncode == 2
    holder = json.loads(second.stdout)
    assert holder["session_id"] == "session-a"
