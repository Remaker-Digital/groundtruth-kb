"""The projection-drift gate refuses a baseline commit whose renders are stale.

Owner direction, 2026-09-08. The unreviewed checkpoint ``2f688c4ca`` removed the
mandatory VERIFIED commit-finalization deny from the baseline compliance gate and
the gap reached all six harness projections with nothing at commit time
objecting. This module pins the gate that closes that loop.

The tests drive the module functions against synthetic roots rather than the live
repository, so they neither read the real index nor run the real projector.
"""

from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = REPO_ROOT / "scripts" / "check_projection_drift.py"

PROFILES_TOML = """
[harnesses.claude]
config_dir = ".claude"

[harnesses.goose]
config_dir = ".goose"

[harnesses.ollama]
config_dir = ".ollama"
status = "profile_pending"
"""


def _load():
    spec = importlib.util.spec_from_file_location("check_projection_drift_under_test", SCRIPT_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


GATE = _load()


@pytest.fixture
def project(tmp_path: Path) -> Path:
    profiles = tmp_path / "scripts" / "harness_projection"
    profiles.mkdir(parents=True)
    (profiles / "profiles.toml").write_text(PROFILES_TOML, encoding="utf-8")
    return tmp_path


def test_pending_profiles_are_not_asked_to_self_check(project: Path) -> None:
    """A harness without its own projector slice cannot be rendered, so gating on
    it would fail every commit for a reason the committer cannot fix."""
    assert GATE.renderable_harnesses(project) == ["claude", "goose"]


def test_no_baseline_path_staged_passes_without_running_the_projector(monkeypatch, project: Path) -> None:
    """The expensive pass is cheap-gated: an ordinary commit never pays for it."""
    monkeypatch.setattr(GATE, "staged_baseline_paths", lambda root: [])

    def _fail(*args, **kwargs):  # pragma: no cover - must not be reached
        raise AssertionError("the projector must not run when no baseline path is staged")

    monkeypatch.setattr(GATE, "check_harness", _fail)
    assert GATE.main(["--staged", "--project-root", str(project)]) == 0


def test_baseline_staged_and_every_harness_in_sync_passes(monkeypatch, project: Path) -> None:
    monkeypatch.setattr(
        GATE,
        "staged_baseline_paths",
        lambda root: [".harness-baseline-configuration/hooks/bridge-compliance-gate.py"],
    )
    monkeypatch.setattr(GATE, "check_harness", lambda root, harness: (0, f"CHECK {harness}: 0 drifted"))
    assert GATE.main(["--staged", "--project-root", str(project)]) == 0


def test_baseline_staged_with_a_drifted_harness_is_refused(monkeypatch, project: Path, capsys) -> None:
    """The checkpoint regression: baseline edited, projections left behind."""
    monkeypatch.setattr(
        GATE,
        "staged_baseline_paths",
        lambda root: [".harness-baseline-configuration/hooks/bridge-compliance-gate.py"],
    )

    def _check(root: Path, harness: str) -> tuple[int, str]:
        if harness == "goose":
            return 1, "CHECK goose: 1 drifted of 127 managed"
        return 0, f"CHECK {harness}: 0 drifted"

    monkeypatch.setattr(GATE, "check_harness", _check)
    assert GATE.main(["--staged", "--project-root", str(project)]) == 1
    assert "goose" in capsys.readouterr().err


def test_missing_profiles_fails_closed(monkeypatch, tmp_path: Path, capsys) -> None:
    """A gate that cannot find the harness roster refuses rather than passing."""
    monkeypatch.setattr(
        GATE,
        "staged_baseline_paths",
        lambda root: [".harness-baseline-configuration/rules/file-bridge-protocol.md"],
    )
    assert GATE.main(["--staged", "--project-root", str(tmp_path)]) == 1
    assert "no renderable harness profiles" in capsys.readouterr().err


def test_staged_baseline_paths_reads_the_index(tmp_path: Path) -> None:
    """The staged-path reader is real git behaviour, not a parsed string."""
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    subprocess.run(["git", "config", "user.email", "t@example.com"], cwd=tmp_path, check=True)
    subprocess.run(["git", "config", "user.name", "Test"], cwd=tmp_path, check=True)
    baseline = tmp_path / ".harness-baseline-configuration" / "hooks"
    baseline.mkdir(parents=True)
    (baseline / "gate.py").write_text("x = 1\n", encoding="utf-8")
    (tmp_path / "unrelated.py").write_text("y = 2\n", encoding="utf-8")

    subprocess.run(["git", "add", "unrelated.py"], cwd=tmp_path, check=True)
    assert GATE.staged_baseline_paths(tmp_path) == []

    subprocess.run(["git", "add", "-f", ".harness-baseline-configuration/hooks/gate.py"], cwd=tmp_path, check=True)
    assert GATE.staged_baseline_paths(tmp_path) == [".harness-baseline-configuration/hooks/gate.py"]
