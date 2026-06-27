"""WI-4457: doctor check that registered governance hook scripts are git-tracked.

Bridge thread: bridge/gtkb-wi4457-registered-hook-tracked-doctor-check-001.md
(Cursor-LO GO at -002).

Covers ``doctor._check_registered_hooks_tracked``:
- registered-but-untracked hook script -> WARN (the WI-4449 surface).
- all registered hooks tracked -> PASS (no false positive).
- untracked sibling .claude/hooks/*.py -> WARN with git-add guidance.
- fail-soft: severity is WARN, never FAIL.
- missing .claude/settings.json -> INFO (nothing to verify).

``_run_cmd`` is monkeypatched to simulate git tracking state so the test does
not require a real git fixture.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
_PACKAGE_SRC = REPO_ROOT / "groundtruth-kb" / "src"
for _p in (str(REPO_ROOT), str(_PACKAGE_SRC)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from groundtruth_kb.project import doctor  # noqa: E402


def _write_settings(target: Path, hook_commands: list[str]) -> None:
    """Write a .claude/settings.json registering the given hook commands under PreToolUse."""
    settings = {
        "hooks": {
            "PreToolUse": [{"matcher": "Write", "hooks": [{"type": "command", "command": c} for c in hook_commands]}]
        }
    }
    settings_path = target / ".claude" / "settings.json"
    settings_path.parent.mkdir(parents=True, exist_ok=True)
    settings_path.write_text(json.dumps(settings), encoding="utf-8")


def _make_hooks_dir(target: Path, files: list[str]) -> None:
    hooks_dir = target / ".claude" / "hooks"
    hooks_dir.mkdir(parents=True, exist_ok=True)
    for f in files:
        (hooks_dir / f).write_text("# fixture hook\n", encoding="utf-8")


def _fake_run_cmd(*, tracked: set[str], others: list[str]):
    """Build a _run_cmd replacement keyed on git subcommand.

    ``--error-unmatch <rel>`` -> (rel in tracked, "").
    ``--others`` -> (True, newline-joined others).
    """

    def runner(cmd: list[str], *, timeout: int = 10) -> tuple[bool, str]:
        if "--error-unmatch" in cmd:
            rel = cmd[-1].replace("\\", "/")
            return (rel in tracked, "")
        if "--others" in cmd:
            return (True, "\n".join(others))
        return (False, "")

    return runner


def test_untracked_registered_hook_warns(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _write_settings(tmp_path, ["python .claude/hooks/foo.py"])
    _make_hooks_dir(tmp_path, ["foo.py"])
    monkeypatch.setattr(doctor, "_run_cmd", _fake_run_cmd(tracked=set(), others=[]))

    result = doctor._check_registered_hooks_tracked(tmp_path)

    assert result.status == "warning"
    assert "foo.py" in result.message
    assert "git add" in result.message


def test_all_registered_hooks_tracked_passes(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _write_settings(tmp_path, ["python .claude/hooks/foo.py"])
    _make_hooks_dir(tmp_path, ["foo.py"])
    monkeypatch.setattr(doctor, "_run_cmd", _fake_run_cmd(tracked={".claude/hooks/foo.py"}, others=[]))

    result = doctor._check_registered_hooks_tracked(tmp_path)

    assert result.status == "pass"


def test_untracked_sibling_hook_warns(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    # No registered hooks; only an untracked sibling .py under .claude/hooks/.
    _write_settings(tmp_path, [])
    _make_hooks_dir(tmp_path, ["bar.py"])
    monkeypatch.setattr(doctor, "_run_cmd", _fake_run_cmd(tracked=set(), others=[".claude/hooks/bar.py"]))

    result = doctor._check_registered_hooks_tracked(tmp_path)

    assert result.status == "warning"
    assert "bar.py" in result.message


def test_failsoft_severity_never_fail(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _write_settings(tmp_path, ["python .claude/hooks/foo.py"])
    _make_hooks_dir(tmp_path, ["foo.py"])
    monkeypatch.setattr(doctor, "_run_cmd", _fake_run_cmd(tracked=set(), others=[]))

    result = doctor._check_registered_hooks_tracked(tmp_path)

    assert result.status != "fail"
    assert result.required is False


def test_missing_settings_is_info(tmp_path: Path) -> None:
    result = doctor._check_registered_hooks_tracked(tmp_path)

    assert result.status == "info"
