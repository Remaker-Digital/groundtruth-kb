"""Spec-derived tests for ``scripts/check_ruff_format.py`` (WI-3473).

Bridge thread ``gtkb-ruff-format-pre-file-gate`` (GO at -008). Covers the
spec-to-test mapping:

- staged-Python detection filters to ``*.py``;
- ``ruff format --check`` PASS on formatted / FAIL on unformatted staged Python;
- no staged Python -> PASS no-op;
- F2 regression: ``resolve_ruff`` is deterministic and venv-first (it must not
  depend on the launching ``python`` having ruff), so the gate cannot fail open
  in this checkout;
- the WARN-pass boundary is gated on project-venv presence.

Tests run under the project venv (pytest interpreter has ruff), so subprocess
invocations use ``sys.executable`` as a ruff-capable interpreter.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = REPO_ROOT / "scripts" / "check_ruff_format.py"

_spec = importlib.util.spec_from_file_location("check_ruff_format", SCRIPT_PATH)
assert _spec and _spec.loader
guardrail = importlib.util.module_from_spec(_spec)
sys.modules["check_ruff_format"] = guardrail
_spec.loader.exec_module(guardrail)


_FORMATTED = "x = [1, 2, 3]\n"
_UNFORMATTED = "x = [1,2,3]\n"  # missing spaces after commas; ruff format rewrites this


def _init_repo(path: Path) -> None:
    subprocess.run(["git", "init", "-q"], cwd=path, check=True)
    subprocess.run(["git", "config", "user.email", "t@example.com"], cwd=path, check=True)
    subprocess.run(["git", "config", "user.name", "t"], cwd=path, check=True)


def _stage(path: Path, name: str, content: str) -> None:
    (path / name).write_text(content, encoding="utf-8")
    subprocess.run(["git", "add", name], cwd=path, check=True)


def _run_guardrail(repo: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT_PATH), "--staged"],
        cwd=str(repo),
        capture_output=True,
        text=True,
    )


# --- component: staged-file detection ---------------------------------------- #


def test_staged_python_files_filters_to_py(tmp_path):
    _init_repo(tmp_path)
    _stage(tmp_path, "a.py", _FORMATTED)
    _stage(tmp_path, "b.txt", "not python\n")
    staged = guardrail.staged_python_files(tmp_path)
    assert staged == ["a.py"]


# --- component: format check ------------------------------------------------- #


def test_check_files_passes_on_formatted(tmp_path):
    ruff = guardrail.resolve_ruff(REPO_ROOT)
    assert ruff is not None, "project venv ruff must resolve in this checkout"
    (tmp_path / "f.py").write_text(_FORMATTED, encoding="utf-8")
    ok, _ = guardrail.check_files(ruff, ["f.py"], tmp_path)
    assert ok is True


def test_check_files_fails_on_unformatted(tmp_path):
    ruff = guardrail.resolve_ruff(REPO_ROOT)
    assert ruff is not None
    (tmp_path / "f.py").write_text(_UNFORMATTED, encoding="utf-8")
    ok, _ = guardrail.check_files(ruff, ["f.py"], tmp_path)
    assert ok is False


# --- F2 regression: deterministic venv-first resolution ---------------------- #


def test_resolve_ruff_prefers_venv(tmp_path):
    """The load-bearing F2 fix: resolution is venv-first, so the gate works even
    when the launching ``python`` lacks ruff. In this checkout the project venv
    exists, so ``resolve_ruff`` must return a command pointing into it."""
    ruff = guardrail.resolve_ruff(REPO_ROOT)
    assert ruff is not None
    interp = ruff[0].replace("\\", "/")
    assert "groundtruth-kb/.venv" in interp, f"expected venv-first resolution; got {ruff!r}"


def test_venv_python_presence_boundary(tmp_path):
    """WARN/FAIL boundary is gated on project-venv presence: present in the real
    checkout, absent for an unrelated tmp root."""
    assert guardrail._venv_python(REPO_ROOT) is not None
    assert guardrail._venv_python(tmp_path) is None


# --- end-to-end: main() via the active-hook invocation shape ----------------- #


def test_main_passes_when_no_python_staged(tmp_path):
    _init_repo(tmp_path)
    _stage(tmp_path, "notes.txt", "hello\n")
    result = _run_guardrail(tmp_path)
    assert result.returncode == 0, result.stdout + result.stderr
    assert "no staged Python" in result.stdout


def test_main_passes_on_formatted(tmp_path):
    _init_repo(tmp_path)
    _stage(tmp_path, "good.py", _FORMATTED)
    result = _run_guardrail(tmp_path)
    assert result.returncode == 0, result.stdout + result.stderr
    assert "[PASS]" in result.stdout


def test_main_blocks_unformatted(tmp_path):
    _init_repo(tmp_path)
    _stage(tmp_path, "bad.py", _UNFORMATTED)
    result = _run_guardrail(tmp_path)
    assert result.returncode == 1, result.stdout + result.stderr
    assert "[FAIL]" in result.stdout
    assert "bad.py" in result.stdout


def test_main_ignores_non_python(tmp_path):
    _init_repo(tmp_path)
    _stage(tmp_path, "good.py", _FORMATTED)
    _stage(tmp_path, "doc.md", "# title with trailing space \n")
    result = _run_guardrail(tmp_path)
    # The .md is ignored; only the formatted .py is checked -> PASS.
    assert result.returncode == 0, result.stdout + result.stderr
