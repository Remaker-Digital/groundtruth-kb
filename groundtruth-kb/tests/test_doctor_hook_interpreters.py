"""The doctor fails loudly when an installed projection's hook interpreter is missing (observers B74, B76; finding F9).

Goose 1.45.0 runs every GT-KB hook through ``sh``; without it every hook fails at spawn and each tool call runs
unenforced. The check reads the projection profiles' declared ``hook_interpreter`` and fails as a required check, so
the whole doctor verdict fails rather than the host degrading to allow. Unreadable profiles and an installed
plugin-hook projection without a declared interpreter are required failures too (B76): neither may leave the
prerequisite unverified while the doctor passes. A projection that is not installed is not checked, and a target
without projection profiles has nothing to check.
"""

from __future__ import annotations

import tomllib
from pathlib import Path

import pytest

from groundtruth_kb.project import doctor

REPO = Path(__file__).resolve().parents[2]
PROFILES = (
    '[harnesses.goose]\nconfig_dir = ".goose"\nhooks_projection = "plugin_hooks_json"\nhook_interpreter = "sh"\n\n'
    '[harnesses.claude]\nconfig_dir = ".claude"\n'
)


def _target(tmp_path: Path, *, installed: bool = True, profiles: str = PROFILES) -> Path:
    path = tmp_path / "scripts" / "harness_projection" / "profiles.toml"
    path.parent.mkdir(parents=True)
    path.write_text(profiles, encoding="utf-8")
    if installed:
        (tmp_path / ".goose").mkdir()
        (tmp_path / ".goose" / ".projection-manifest.json").write_text("{}", encoding="utf-8")
    return tmp_path


def test_a_missing_interpreter_is_a_required_failure(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(doctor.shutil, "which", lambda name, *args, **kwargs: None)
    check = doctor._check_hook_interpreters(_target(tmp_path))
    assert check.status == "fail" and check.required is True
    assert "goose runs its GT-KB hooks through 'sh', which is not on PATH" in check.message
    assert "unenforced" in check.message
    assert doctor.DoctorReport(checks=[check]).overall == "fail"


def test_a_resolving_interpreter_passes(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(doctor.shutil, "which", lambda name, *args, **kwargs: f"C:/fixture/{name}.exe")
    check = doctor._check_hook_interpreters(_target(tmp_path))
    assert check.status == "pass" and check.required is False
    assert check.message == "Harness hook interpreters resolve: goose (sh)"


def test_an_uninstalled_projection_is_not_checked(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(doctor.shutil, "which", lambda name, *args, **kwargs: None)
    check = doctor._check_hook_interpreters(_target(tmp_path, installed=False))
    assert check.status == "info" and check.required is False


def test_a_target_without_projection_profiles_has_nothing_to_check(tmp_path: Path) -> None:
    check = doctor._check_hook_interpreters(tmp_path)
    assert check.status == "info" and check.found is False and check.required is False


@pytest.mark.parametrize("corrupt", ["[harnesses.goose\n", "harnesses = 3\n", "[other]\nx = 1\n"])
def test_unreadable_profiles_are_a_required_failure(tmp_path: Path, corrupt: str) -> None:
    """B76: a present but unreadable declaration leaves the prerequisite unverified, so the doctor fails."""
    check = doctor._check_hook_interpreters(_target(tmp_path, profiles=corrupt))
    assert check.status == "fail" and check.required is True
    assert "cannot be verified" in check.message
    assert doctor.DoctorReport(checks=[check]).overall == "fail"


def test_an_installed_plugin_hook_projection_without_a_declared_interpreter_fails(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """B76: Goose's plugin hooks always run through a shell; a profile that stops declaring it must not pass."""
    monkeypatch.setattr(doctor.shutil, "which", lambda name, *args, **kwargs: f"C:/fixture/{name}.exe")
    undeclared = PROFILES.replace('hook_interpreter = "sh"\n', "")
    check = doctor._check_hook_interpreters(_target(tmp_path, profiles=undeclared))
    assert check.status == "fail" and check.required is True
    assert "goose runs its GT-KB hooks through a shell but its profile declares no hook_interpreter" in check.message


def test_every_plugin_hook_profile_in_this_repository_declares_its_interpreter() -> None:
    profiles = tomllib.loads((REPO / "scripts/harness_projection/profiles.toml").read_text(encoding="utf-8"))
    shell_run = {
        name: row
        for name, row in profiles["harnesses"].items()
        if row.get("hooks_projection") in doctor._SHELL_RUN_HOOK_PROJECTIONS
    }
    assert shell_run and all(row.get("hook_interpreter") for row in shell_run.values()), shell_run
