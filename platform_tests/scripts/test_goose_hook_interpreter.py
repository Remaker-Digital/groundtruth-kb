"""Goose's hook interpreter is a named, verified prerequisite of Goose enforcement (observer B74; finding F9).

Goose 1.45.0 runs every GT-KB hook command through ``sh``. Without it on PATH every hook fails at spawn and Goose lets
each tool call run, before any GT-KB code could answer, and ``on_failure: block`` does not catch it. The Goose profile
declares the interpreter; GT-KB's Goose launcher resolves it on the child's PATH and refuses to start a session whose
hooks could not run, before any model call. The doctor side is tested in groundtruth-kb/tests.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tomllib
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS_DIR = ROOT / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import goose_harness  # noqa: E402


def _project(tmp_path: Path) -> Path:
    root = tmp_path / "project"
    root.mkdir()
    (root / "groundtruth.toml").write_text("[groundtruth]\n", encoding="utf-8")
    for relative in (goose_harness.FLOOR_CONFIG_RELATIVE_PATH, goose_harness.PROFILES_RELATIVE_PATH):
        target = root / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes((ROOT / relative).read_bytes())
    return root


def _interpreter(directory: Path) -> Path:
    directory.mkdir(parents=True, exist_ok=True)
    fake = directory / ("sh.exe" if os.name == "nt" else "sh")
    fake.write_bytes(b"")
    fake.chmod(0o755)
    return fake


def test_the_goose_profile_declares_sh_as_its_hook_interpreter() -> None:
    profiles = tomllib.loads((ROOT / goose_harness.PROFILES_RELATIVE_PATH).read_text(encoding="utf-8"))
    assert profiles["harnesses"]["goose"]["hook_interpreter"] == "sh"


def test_the_interpreter_is_resolved_on_the_childs_path(tmp_path: Path) -> None:
    root = _project(tmp_path)
    fake = _interpreter(tmp_path / "bin")
    resolved = goose_harness.require_hook_interpreter(root, {"PATH": str(fake.parent)})
    assert Path(resolved).resolve() == fake.resolve()


def test_the_launcher_refuses_before_any_spawn_when_the_interpreter_is_missing(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    root = _project(tmp_path)
    empty = tmp_path / "empty"
    empty.mkdir()
    monkeypatch.setenv("PATH", str(empty))
    monkeypatch.chdir(empty)

    def refuse_spawn(*args: object, **kwargs: object) -> None:
        raise AssertionError("Goose must not be spawned without its hook interpreter")

    monkeypatch.setattr(goose_harness.subprocess, "run", refuse_spawn)
    assert goose_harness.main(["-p", "hello", "--project-root", str(root)]) == 1
    err = capsys.readouterr().err
    assert "'sh', which is not on PATH" in err and "unenforced" in err


def test_a_profile_without_a_declared_interpreter_is_refused(tmp_path: Path) -> None:
    root = _project(tmp_path)
    profiles = root / goose_harness.PROFILES_RELATIVE_PATH
    text = profiles.read_text(encoding="utf-8")
    assert text.count('hook_interpreter = "sh"\n') == 1
    profiles.write_text(text.replace('hook_interpreter = "sh"\n', ""), encoding="utf-8")
    with pytest.raises(goose_harness.GooseHarnessError, match="declares no hook interpreter"):
        goose_harness.require_hook_interpreter(root, {"PATH": ""})


def test_a_real_launch_with_sh_removed_from_path_refuses_visibly(tmp_path: Path) -> None:
    """B74's sufficient validation: the launcher run as a process with ``sh`` absent from PATH refuses to operate."""
    root = _project(tmp_path)
    env = {key: value for key, value in os.environ.items() if key.upper() != "PATH"}
    env["PATH"] = str(Path(sys.executable).parent)  # the interpreter's own folder: no Git for Windows usr\bin
    env["PYTHONIOENCODING"] = "utf-8"
    assert shutil.which("sh", path=env["PATH"]) is None
    done = subprocess.run(
        [sys.executable, "-B", str(SCRIPTS_DIR / "goose_harness.py"), "-p", "probe", "--project-root", str(root)],
        cwd=tmp_path,
        env=env,
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=120,
        check=False,
    )
    assert done.returncode == 1
    assert done.stdout == ""
    assert "which is not on PATH" in done.stderr and "unenforced" in done.stderr
