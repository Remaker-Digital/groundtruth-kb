"""WI-5668: spec-derived tests for the skill-rename reference-sweep doctor check.

Verifies ``_check_skill_rename_reference_sweep``:
- WARNs (with count + offending path) while a bare pre-rename skill reference remains,
- PASSes at zero remaining references,
- honors the exclusion set (bridge/, archive/, .gtkb-state/ do not count),
- derives the bare-name set from current ``gtkb-`` skill dirs (self-maintaining).

The seeded references are built from constructed strings (``f"...{bare}..."``) so this
test file's own tracked source never literally carries a matchable ``skills/<bare>/``
segment and cannot inflate a real-repo doctor run.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

from groundtruth_kb.project.doctor import _check_skill_rename_reference_sweep


def _git(tmp: Path, *args: str) -> None:
    subprocess.run(["git", "-C", str(tmp), *args], capture_output=True, text=True, check=True)


def _init_repo(tmp: Path) -> None:
    _git(tmp, "init", "-q")
    _git(tmp, "config", "user.email", "test@example.com")
    _git(tmp, "config", "user.name", "test")


def _make_gtkb_skill(tmp: Path, name: str) -> None:
    d = tmp / ".agents" / "skills" / f"gtkb-{name}" / "helpers"
    d.mkdir(parents=True, exist_ok=True)
    (d / "helper.py").write_text("# renamed skill helper\n", encoding="utf-8")


def _write_tracked(tmp: Path, rel: str, content: str) -> None:
    p = tmp / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")


def test_warns_while_bare_reference_remains(tmp_path: Path) -> None:
    _init_repo(tmp_path)
    _make_gtkb_skill(tmp_path, "verify")
    bare = "verify"
    _write_tracked(tmp_path, "scripts/user.py", f'HELPER = ".agents/skills/{bare}/helpers/w.py"\n')
    _git(tmp_path, "add", "-A")

    result = _check_skill_rename_reference_sweep(tmp_path)

    assert result.status == "warning"
    assert result.required is False
    assert "scripts/user.py" in result.message


def test_passes_when_no_bare_reference(tmp_path: Path) -> None:
    _init_repo(tmp_path)
    _make_gtkb_skill(tmp_path, "verify")
    _write_tracked(tmp_path, "scripts/user.py", 'HELPER = "ok"\n')
    _git(tmp_path, "add", "-A")

    result = _check_skill_rename_reference_sweep(tmp_path)

    assert result.status == "pass"


def test_excluded_trees_do_not_count(tmp_path: Path) -> None:
    _init_repo(tmp_path)
    _make_gtkb_skill(tmp_path, "verify")
    bare = "verify"
    for rel in ("bridge/audit.md", "archive/old.py", ".gtkb-state/scratch.json"):
        _write_tracked(tmp_path, rel, f'REF = ".agents/skills/{bare}/helpers"\n')
    _git(tmp_path, "add", "-A")

    result = _check_skill_rename_reference_sweep(tmp_path)

    assert result.status == "pass"


def test_self_maintaining_derivation_no_gtkb_dirs(tmp_path: Path) -> None:
    _init_repo(tmp_path)
    (tmp_path / ".agents" / "skills").mkdir(parents=True, exist_ok=True)
    _write_tracked(tmp_path, "scripts/user.py", 'HELPER = "ok"\n')
    _git(tmp_path, "add", "-A")

    result = _check_skill_rename_reference_sweep(tmp_path)

    # No gtkb- dirs → no bare-name set to sweep → info (nothing to enforce yet).
    assert result.status == "info"


def test_sweep_unicode_output_preserves_warning(tmp_path: Path) -> None:
    _init_repo(tmp_path)
    _make_gtkb_skill(tmp_path, "verify")
    bare = "verify"
    _write_tracked(
        tmp_path,
        "scripts/unicode.py",
        f'# UTF-8 left arrow: ←; HELPER = ".agents/skills/{bare}/helpers/w.py"\n',
    )
    _git(tmp_path, "add", "-A")

    result = _check_skill_rename_reference_sweep(tmp_path)

    assert result.status == "warning"
    assert "1 pre-rename bare skill-dir reference(s) remain" in result.message
    assert "scripts/unicode.py" in result.message


def test_sweep_exit0_without_usable_output_is_not_pass(tmp_path: Path, monkeypatch) -> None:
    _make_gtkb_skill(tmp_path, "verify")

    def _missing_output(*args, **kwargs):
        return subprocess.CompletedProcess(args=args[0], returncode=0, stdout=None)

    monkeypatch.setattr(subprocess, "run", _missing_output)

    result = _check_skill_rename_reference_sweep(tmp_path)

    assert result.status == "warning"
    assert "scan unavailable" in result.message
    assert "sweep complete" not in result.message


def test_sweep_pass_only_at_zero(tmp_path: Path, monkeypatch) -> None:
    _make_gtkb_skill(tmp_path, "verify")

    def _no_matches(*args, **kwargs):
        return subprocess.CompletedProcess(args=args[0], returncode=1, stdout=b"")

    monkeypatch.setattr(subprocess, "run", _no_matches)

    result = _check_skill_rename_reference_sweep(tmp_path)

    assert result.status == "pass"
    assert "sweep complete" in result.message
