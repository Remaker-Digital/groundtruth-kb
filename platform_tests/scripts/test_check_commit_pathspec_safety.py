"""Tests for scripts/check_commit_pathspec_safety.py (WI-4464 Slice A).

Each test maps to an acceptance criterion in the implementation proposal
``bridge/gtkb-wi4464-commit-pathspec-safety-detector-001.md`` (Verification
Plan). The detector is split into a pure ``classify_staged`` function and a
thin ``_staged_names`` git shim so these tests bypass git entirely via
monkeypatch.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = PROJECT_ROOT / "scripts" / "check_commit_pathspec_safety.py"


def _load_checker():
    spec = importlib.util.spec_from_file_location("check_commit_pathspec_safety", SCRIPT_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    try:
        spec.loader.exec_module(module)
        return module
    finally:
        sys.modules.pop(spec.name, None)


checker = _load_checker()


# --- classify_staged: contamination signature detection ---------------------


def test_mixed_bridge_and_source_is_flagged() -> None:
    """Contamination signature (WI-4464; bridge-essential "Scoped commits only")."""
    result = checker.classify_staged(["bridge/foo-001.md", "scripts/x.py"])
    assert result["mixed"] is True
    assert result["bridge_queue"] == ["bridge/foo-001.md"]
    assert result["other"] == ["scripts/x.py"]


def test_bridge_only_not_mixed() -> None:
    """No false positive on a legit bridge-only commit (GOV-FILE-BRIDGE-AUTHORITY-001)."""
    result = checker.classify_staged(["bridge/foo-001.md", "bridge/bar-002.md"])
    assert result["mixed"] is False
    assert result["bridge_queue"] == ["bridge/bar-002.md", "bridge/foo-001.md"]
    assert result["other"] == []


def test_source_only_not_mixed() -> None:
    """No false positive on a source-only commit."""
    result = checker.classify_staged(["scripts/x.py", "a/b.py"])
    assert result["mixed"] is False
    assert result["bridge_queue"] == []
    assert result["other"] == ["a/b.py", "scripts/x.py"]


def test_empty_not_mixed() -> None:
    """Empty staged set is not flagged."""
    result = checker.classify_staged([])
    assert result["mixed"] is False
    assert result["bridge_queue"] == []
    assert result["other"] == []


def test_nested_bridge_path_is_other() -> None:
    """Conservative matcher: nested bridge/ paths are NOT queue surface."""
    result = checker.classify_staged(["bridge/sub/foo.md", "bridge/bar-001.md"])
    assert result["mixed"] is True
    assert result["bridge_queue"] == ["bridge/bar-001.md"]
    assert result["other"] == ["bridge/sub/foo.md"]


def test_non_md_bridge_path_is_other() -> None:
    """Conservative matcher: non-.md bridge/ paths are NOT queue surface."""
    result = checker.classify_staged(["bridge/notes.txt", "bridge/foo-001.md"])
    assert result["mixed"] is True
    assert result["bridge_queue"] == ["bridge/foo-001.md"]
    assert result["other"] == ["bridge/notes.txt"]


def test_backslash_paths_normalized() -> None:
    """Windows-style backslash paths normalize to forward slashes."""
    result = checker.classify_staged(["bridge\\bar-001.md", "scripts\\x.py"])
    assert result["mixed"] is True
    assert result["bridge_queue"] == ["bridge/bar-001.md"]
    assert result["other"] == ["scripts/x.py"]


# --- main(): CLI advisory / strict / json behavior --------------------------


def test_advisory_exit_zero_on_mixed(monkeypatch, capsys) -> None:
    """Advisory mode never blocks a commit (fail-open; protects swarm + sweep-commit)."""
    monkeypatch.setattr(checker, "_staged_names", lambda: ["bridge/foo-001.md", "scripts/x.py"])
    rc = checker.main(["--staged"])
    captured = capsys.readouterr()
    assert rc == 0
    assert "WARNING" in captured.err
    assert "bridge/foo-001.md" in captured.err
    assert "scripts/x.py" in captured.err
    assert captured.out == ""


def test_strict_exit_nonzero_on_mixed(monkeypatch, capsys) -> None:
    """Strict mode blocks on contamination with a distinct exit code."""
    monkeypatch.setattr(checker, "_staged_names", lambda: ["bridge/foo-001.md", "scripts/x.py"])
    rc = checker.main(["--staged", "--strict"])
    captured = capsys.readouterr()
    assert rc == checker.STRICT_CONTAMINATION_EXIT
    assert rc == 3
    assert "WARNING" in captured.err


def test_strict_exit_zero_on_clean(monkeypatch, capsys) -> None:
    """Strict mode passes a clean (bridge-only) staged set."""
    monkeypatch.setattr(checker, "_staged_names", lambda: ["bridge/foo-001.md", "bridge/bar-002.md"])
    rc = checker.main(["--staged", "--strict"])
    captured = capsys.readouterr()
    assert rc == 0
    assert captured.err == ""


def test_json_output(monkeypatch, capsys) -> None:
    """JSON output shape: parseable with mixed/bridge_queue/other keys."""
    monkeypatch.setattr(checker, "_staged_names", lambda: ["bridge/foo-001.md", "scripts/x.py"])
    rc = checker.main(["--staged", "--json"])
    captured = capsys.readouterr()
    assert rc == 0
    payload = json.loads(captured.out)
    assert payload == {
        "mixed": True,
        "bridge_queue": ["bridge/foo-001.md"],
        "other": ["scripts/x.py"],
        "foreign_verdicts": [],
        "foreign_blocked": False,
    }


def test_json_exit_zero_even_when_mixed(monkeypatch, capsys) -> None:
    """--json always exits 0 regardless of contamination (machine-read mode)."""
    monkeypatch.setattr(checker, "_staged_names", lambda: ["bridge/INDEX.md", "scripts/x.py"])
    rc = checker.main(["--staged", "--json", "--strict"])
    capsys.readouterr()
    assert rc == 0


def test_no_staged_fail_open(monkeypatch, capsys) -> None:
    """No-git / no-staged fail-open: exit 0, no warning."""
    monkeypatch.setattr(checker, "_staged_names", lambda: [])
    rc = checker.main(["--staged", "--strict"])
    captured = capsys.readouterr()
    assert rc == 0
    assert captured.err == ""
    assert captured.out == ""


def test_default_no_staged_flag_is_clean(capsys) -> None:
    """Without --staged, no git read occurs; clean exit 0."""
    rc = checker.main([])
    captured = capsys.readouterr()
    assert rc == 0
    assert captured.err == ""


# --- _staged_names(): git shim fail-open ------------------------------------


def test_staged_names_fail_open_on_oserror(monkeypatch) -> None:
    """_staged_names returns [] when git is unavailable (OSError)."""

    def _raise(*_args, **_kwargs):
        raise OSError("git not found")

    monkeypatch.setattr(checker.subprocess, "run", _raise)
    assert checker._staged_names() == []


def test_staged_names_fail_open_on_called_process_error(monkeypatch) -> None:
    """_staged_names returns [] when git exits non-zero (not a repo)."""

    def _raise(*_args, **_kwargs):
        raise checker.subprocess.CalledProcessError(128, ["git"])

    monkeypatch.setattr(checker.subprocess, "run", _raise)
    assert checker._staged_names() == []
