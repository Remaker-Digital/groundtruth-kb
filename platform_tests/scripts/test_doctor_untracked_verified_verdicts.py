"""WI-4871: doctor guard for untracked terminal-VERIFIED bridge verdict files.

Bridge thread: bridge/gtkb-wi4871-untracked-verified-verdict-guard-001.md
(Cursor-LO GO at -002).

Covers ``doctor._check_untracked_terminal_verified_verdicts``:
- untracked terminal-VERIFIED verdict -> WARN (the finalization-bypass gap).
- tracked terminal-VERIFIED verdict -> no WARN (not in --others output).
- non-VERIFIED untracked bridge file -> no WARN (only terminal VERIFIED is scope).
- fail-soft: severity is WARN, never FAIL.

``_run_cmd`` is monkeypatched to simulate ``git ls-files --others`` output.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
_PACKAGE_SRC = REPO_ROOT / "groundtruth-kb" / "src"
for _p in (str(REPO_ROOT), str(_PACKAGE_SRC)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from groundtruth_kb.project import doctor  # noqa: E402


def _make_bridge_file(target: Path, rel: str, first_line: str) -> None:
    path = target / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"{first_line}\n\n# body\n", encoding="utf-8")


def _fake_run_cmd(others: list[str]):
    def runner(cmd: list[str], *, timeout: int = 10) -> tuple[bool, str]:
        if "--others" in cmd:
            return (True, "\n".join(others))
        return (False, "")

    return runner


def test_untracked_verified_verdict_warns(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _make_bridge_file(tmp_path, "bridge/foo-002.md", "VERIFIED")
    monkeypatch.setattr(doctor, "_run_cmd", _fake_run_cmd(["bridge/foo-002.md"]))

    result = doctor._check_untracked_terminal_verified_verdicts(tmp_path)

    assert result.status == "warning"
    assert "foo-002.md" in result.message
    assert "git add" in result.message


def test_tracked_verified_verdict_no_warn(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    # A tracked VERIFIED file does not appear in `ls-files --others`.
    (tmp_path / "bridge").mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(doctor, "_run_cmd", _fake_run_cmd([]))

    result = doctor._check_untracked_terminal_verified_verdicts(tmp_path)

    assert result.status == "pass"


def test_non_verified_untracked_no_warn(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _make_bridge_file(tmp_path, "bridge/bar-001.md", "NEW")
    monkeypatch.setattr(doctor, "_run_cmd", _fake_run_cmd(["bridge/bar-001.md"]))

    result = doctor._check_untracked_terminal_verified_verdicts(tmp_path)

    assert result.status == "pass"


def test_failsoft_severity_never_fail(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _make_bridge_file(tmp_path, "bridge/foo-002.md", "VERIFIED")
    monkeypatch.setattr(doctor, "_run_cmd", _fake_run_cmd(["bridge/foo-002.md"]))

    result = doctor._check_untracked_terminal_verified_verdicts(tmp_path)

    assert result.status != "fail"
    assert result.required is False


def test_missing_bridge_dir_is_info(tmp_path: Path) -> None:
    result = doctor._check_untracked_terminal_verified_verdicts(tmp_path)

    assert result.status == "info"
