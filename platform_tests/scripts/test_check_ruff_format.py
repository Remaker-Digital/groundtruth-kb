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

import pytest

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
    _init_repo(tmp_path)
    _stage(tmp_path, "f.py", _FORMATTED)
    ok, _ = guardrail.check_files(ruff, ["f.py"], tmp_path)
    assert ok is True


def test_check_files_fails_on_unformatted(tmp_path):
    ruff = guardrail.resolve_ruff(REPO_ROOT)
    assert ruff is not None
    _init_repo(tmp_path)
    _stage(tmp_path, "f.py", _UNFORMATTED)
    ok, _ = guardrail.check_files(ruff, ["f.py"], tmp_path)
    assert ok is False


def test_check_files_fails_closed_when_staged_blob_is_unreadable(tmp_path, monkeypatch):
    ruff = guardrail.resolve_ruff(REPO_ROOT)
    assert ruff is not None
    monkeypatch.setattr(guardrail, "_staged_blob", lambda _root, _path: None)

    ok, output = guardrail.check_files(ruff, ["missing.py"], tmp_path)

    assert ok is False
    assert "Unable to read staged blob: missing.py" in output


# --- F2 regression: deterministic venv-first resolution ---------------------- #


def _require_project_venv() -> None:
    if guardrail._venv_python(REPO_ROOT) is None:
        pytest.skip("project venv missing in this checkout; venv-first resolution is measured on the production layout")


def test_resolve_ruff_prefers_venv(tmp_path):
    """The load-bearing F2 fix: resolution is venv-first, so the gate works even
    when the launching ``python`` lacks ruff. Where the project venv exists,
    ``resolve_ruff`` must return a command pointing into it."""
    _require_project_venv()
    ruff = guardrail.resolve_ruff(REPO_ROOT)
    assert ruff is not None
    interp = ruff[0].replace("\\", "/")
    assert "groundtruth-kb/.venv" in interp, f"expected venv-first resolution; got {ruff!r}"


def test_venv_python_presence_boundary(tmp_path):
    """WARN/FAIL boundary is gated on project-venv presence: absent for an
    unrelated tmp root, present where the production layout exists."""
    assert guardrail._venv_python(tmp_path) is None
    _require_project_venv()
    assert guardrail._venv_python(REPO_ROOT) is not None


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
    assert "then re-stage (git add)" in result.stdout


def test_main_ignores_non_python(tmp_path):
    _init_repo(tmp_path)
    _stage(tmp_path, "good.py", _FORMATTED)
    _stage(tmp_path, "doc.md", "# title with trailing space \n")
    result = _run_guardrail(tmp_path)
    # The .md is ignored; only the formatted .py is checked -> PASS.
    assert result.returncode == 0, result.stdout + result.stderr


def test_main_checks_staged_lf_blob_not_mixed_eol_worktree(tmp_path):
    _init_repo(tmp_path)
    _stage(tmp_path, "mixed.py", "x = [1, 2, 3]\ny = 4\n")
    (tmp_path / "mixed.py").write_bytes(b"x = [1, 2, 3]\r\ny = 4\n")
    ruff = guardrail.resolve_ruff(REPO_ROOT)
    assert ruff is not None
    path_check = subprocess.run(
        ruff + ["format", "--check", "mixed.py"],
        cwd=tmp_path,
        capture_output=True,
    )
    assert path_check.returncode != 0, "fixture must reproduce the old path-based false failure"

    result = _run_guardrail(tmp_path)

    assert result.returncode == 0, result.stdout + result.stderr


def test_main_pins_index_vs_worktree_divergence_both_directions(tmp_path):
    _init_repo(tmp_path)
    _stage(tmp_path, "clean_index.py", _FORMATTED)
    (tmp_path / "clean_index.py").write_text(_UNFORMATTED, encoding="utf-8")

    clean_index = _run_guardrail(tmp_path)

    assert clean_index.returncode == 0, clean_index.stdout + clean_index.stderr

    _stage(tmp_path, "dirty_index.py", _UNFORMATTED)
    (tmp_path / "dirty_index.py").write_text(_FORMATTED, encoding="utf-8")

    dirty_index = _run_guardrail(tmp_path)

    assert dirty_index.returncode == 1, dirty_index.stdout + dirty_index.stderr
    assert "dirty_index.py" in dirty_index.stdout


def test_main_autocrlf_staged_blob_still_blocks_real_format_error(tmp_path):
    _init_repo(tmp_path)
    subprocess.run(["git", "config", "core.autocrlf", "true"], cwd=tmp_path, check=True)
    (tmp_path / "bad_crlf.py").write_bytes(b"x = [1,2,3]\r\n")
    subprocess.run(["git", "add", "bad_crlf.py"], cwd=tmp_path, check=True)
    staged = subprocess.run(
        ["git", "show", ":0:bad_crlf.py"],
        cwd=tmp_path,
        check=True,
        capture_output=True,
    ).stdout
    assert b"\r\n" not in staged

    result = _run_guardrail(tmp_path)

    assert result.returncode == 1, result.stdout + result.stderr
    assert "bad_crlf.py" in result.stdout
