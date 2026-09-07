"""Generated harness projection roots stay out of version control (WI-6691).

The projection roots are derived output: ``scripts/harness_projection/project_harness.py``
regenerates each one from ``.harness-baseline-configuration``. Tracking them made every
baseline edit spawn up to six protected projection diffs, each separately demanding a live
GO authorization packet, which nobody mints for generated output. This module is the
mechanical enforcement of the boundary that removes.

The roster is read from ``scripts/harness_projection/profiles.toml`` rather than hard-coded,
so a seventh harness added later is covered without editing this file.

Authority: ``GOV-HARNESS-NEUTRAL-BASELINE-001`` v2 obligation 2; ``SPEC-INTAKE-c878d9``;
``GOV-SOT-SINGLETON-001``. Bridge thread ``gtkb-wi6691-untrack-projection-roots``.
"""

from __future__ import annotations

import subprocess
import tomllib
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
PROFILES = REPO_ROOT / "scripts" / "harness_projection" / "profiles.toml"
BASELINE = REPO_ROOT / ".harness-baseline-configuration"


def _git(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
        timeout=60,
    )


def _projection_roots() -> list[str]:
    """Distinct ``config_dir`` values from the canonical roster.

    Several harnesses deliberately share one directory (ollama, openrouter and
    alibaba-cloud-studio all project into ``.api-harness``), so the roster is
    de-duplicated before use.
    """
    data = tomllib.loads(PROFILES.read_text(encoding="utf-8"))
    dirs = {cfg["config_dir"] for cfg in data.get("harnesses", {}).values() if cfg.get("config_dir")}
    return sorted(dirs)


ROOTS = _projection_roots()


def test_roster_is_readable_and_non_empty() -> None:
    """A silently empty roster would make every other assertion vacuously pass."""
    assert ROOTS, f"no config_dir entries found in {PROFILES}"
    assert all(r.startswith(".") for r in ROOTS), ROOTS


@pytest.mark.parametrize("root", ROOTS)
def test_projection_root_has_no_tracked_files(root: str) -> None:
    """Primary assertion: the derived copy is not in the index."""
    result = _git("ls-files", "--", root)
    assert result.returncode == 0, result.stderr
    tracked = [line for line in result.stdout.splitlines() if line.strip()]
    assert tracked == [], (
        f"{root} has {len(tracked)} tracked file(s); projection roots are generated "
        f"output and must not be tracked. First few: {tracked[:5]}"
    )


@pytest.mark.parametrize("root", ROOTS)
def test_projection_root_is_ignored(root: str) -> None:
    """The root is covered by a .gitignore entry, so regeneration stays clean."""
    result = _git("check-ignore", "-q", "--", f"{root}/")
    assert result.returncode == 0, (
        f"{root}/ is not covered by .gitignore; regenerated projections would "
        f"reappear as untracked noise and re-enter the protected-commit population"
    )


@pytest.mark.parametrize("root", ROOTS)
def test_untracking_did_not_delete_the_projection(root: str) -> None:
    """Non-destructiveness: untracking removed index entries, not files."""
    path = REPO_ROOT / root
    assert path.is_dir(), f"{root} does not exist on disk; untracking must not delete"
    assert any(path.rglob("*")), f"{root} exists but is empty"


def test_no_negation_reincludes_a_projection_root() -> None:
    """Regression floor for the S294 negation block this work item removed.

    The S294 lesson -- if it is essential, it must be tracked -- is satisfied at
    the baseline, which stays tracked. Re-adding negations here would re-enter
    every projected file into the protected-commit population, which is the exact
    defect WI-6691 removed.
    """
    gitignore = (REPO_ROOT / ".gitignore").read_text(encoding="utf-8")
    offenders = [
        line.strip()
        for line in gitignore.splitlines()
        if line.strip().startswith("!") and any(line.strip()[1:].startswith(root) for root in ROOTS)
    ]
    assert offenders == [], (
        "found negation entries re-including projected paths: "
        f"{offenders}. Projection roots are generated output; if content must be "
        "tracked, track it in .harness-baseline-configuration instead."
    )


def test_baseline_remains_tracked_and_non_empty() -> None:
    """GOV-SOT-SINGLETON-001: this removes the duplicate, not the source."""
    result = _git("ls-files", "--", ".harness-baseline-configuration")
    assert result.returncode == 0, result.stderr
    tracked = [line for line in result.stdout.splitlines() if line.strip()]
    assert len(tracked) > 100, (
        f"baseline has only {len(tracked)} tracked files; the projection roots are "
        f"derived from it, so it must remain the tracked source of truth"
    )
    assert BASELINE.is_dir()


def test_bridge_essential_rule_survives_at_the_baseline() -> None:
    """The specific file S294 was installed to protect is still under version control."""
    result = _git("ls-files", "--", ".harness-baseline-configuration/rules/bridge-essential.md")
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip(), (
        "bridge-essential.md is not tracked at the baseline; the S294 safety property "
        "depends on it being tracked at the source now that the projected copy is not"
    )
