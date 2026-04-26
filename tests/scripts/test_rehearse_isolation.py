"""Tests for GTKB-ISOLATION-016 Phase 8 rehearsal driver (Wave 1 skeleton).

Per `bridge/gtkb-isolation-016-phase8-rehearsal-implementation-013.md`
(REVISED-6) and `-014` (Codex GO). Covers:

  T-DRIVER-1: parametric over LEGACY_CONFLATED_SURFACES (refusal)
  T-DRIVER-1-ALLOW: applications/<name>/ passes refusal check
  T-DRIVER-2: --no-dry-run refusal
  T-DRIFT-CHECK: hash_set_walk drift detection
  T-LANE-COVERAGE: dispatch table contains all 11 lanes
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
from rehearse._common import (  # noqa: E402
    LEGACY_CONFLATED_SURFACES,
    TargetRootError,
    hash_set_walk,
    validate_target_root,
)
import rehearse_isolation as driver  # noqa: E402


# ============================================================================
# T-DRIVER-1: refusal logic (parametric over conflated surfaces)
# ============================================================================


@pytest.mark.parametrize("surface", sorted(LEGACY_CONFLATED_SURFACES))
def test_target_root_refused_in_each_conflated_surface(tmp_path: Path, surface: str, monkeypatch: pytest.MonkeyPatch) -> None:
    """T-DRIVER-1: every entry in LEGACY_CONFLATED_SURFACES must refuse.

    The check uses the live LEGACY_ROOT constant (E:/GT-KB), so we test
    against real top-level directories. The function should raise for each.
    """
    from rehearse import _common
    legacy = _common.LEGACY_ROOT
    bad = legacy / surface / "deeper" / "child"
    with pytest.raises(TargetRootError):
        validate_target_root(bad)


def test_target_root_refused_at_legacy_root_itself() -> None:
    from rehearse import _common
    with pytest.raises(TargetRootError):
        validate_target_root(_common.LEGACY_ROOT)


def test_target_root_refused_at_applications_parent() -> None:
    from rehearse import _common
    with pytest.raises(TargetRootError):
        validate_target_root(_common.APPLICATIONS_NAMESPACE)


def test_target_root_refused_with_invalid_name() -> None:
    from rehearse import _common
    bad = _common.APPLICATIONS_NAMESPACE / "1invalid-starts-with-digit"
    with pytest.raises(TargetRootError, match="identifier pattern"):
        validate_target_root(bad)


# ============================================================================
# T-DRIVER-1-ALLOW: positive allow rule
# ============================================================================


def test_target_root_allowed_at_applications_named_child() -> None:
    """T-DRIVER-1-ALLOW: applications/<name>/ passes refusal check."""
    from rehearse import _common
    good = _common.APPLICATIONS_NAMESPACE / "Agent_Red"
    validate_target_root(good)  # must not raise


@pytest.mark.parametrize("name", ["A", "Agent_Red", "my-app", "App1", "App_2-final"])
def test_target_root_allowed_for_valid_names(name: str) -> None:
    from rehearse import _common
    good = _common.APPLICATIONS_NAMESPACE / name
    validate_target_root(good)


def test_target_root_allowed_outside_legacy_root(tmp_path: Path) -> None:
    """A path entirely outside <gt-kb-root>/ is allowed (e.g., test sandbox).

    The ADR binds adopters under GT-KB; rehearsal can run against any path
    that doesn't conflict with the conflated legacy surfaces. Tests live
    outside <gt-kb-root>/ in a tmp_path fixture.
    """
    validate_target_root(tmp_path / "sandbox" / "anywhere")


# ============================================================================
# T-DRIVER-2: --no-dry-run refusal
# ============================================================================


def test_no_dry_run_refused() -> None:
    """T-DRIVER-2: --no-dry-run must trigger refusal exit (v1 forbidden)."""
    rc = driver.main(["--no-dry-run", "--phase", "all"])
    assert rc == driver.EXIT_REFUSE


# ============================================================================
# T-DRIFT-CHECK: hash_set_walk drift detection
# ============================================================================


def test_hash_set_walk_returns_per_file_hashes(tmp_path: Path) -> None:
    """T-DRIFT-CHECK: hash_set_walk emits sha256 per file."""
    (tmp_path / "a.txt").write_text("alpha")
    (tmp_path / "sub").mkdir()
    (tmp_path / "sub" / "b.txt").write_text("beta")

    hashes = hash_set_walk(tmp_path)
    assert "a.txt" in hashes
    assert "sub/b.txt" in hashes
    assert all(len(h) == 64 for h in hashes.values())


def test_hash_set_walk_detects_content_drift(tmp_path: Path) -> None:
    """T-DRIFT-CHECK: changing file content changes the hash."""
    (tmp_path / "drift.txt").write_text("v1")
    h1 = hash_set_walk(tmp_path)["drift.txt"]
    (tmp_path / "drift.txt").write_text("v2")
    h2 = hash_set_walk(tmp_path)["drift.txt"]
    assert h1 != h2


def test_hash_set_walk_skips_ignored_top_level(tmp_path: Path) -> None:
    """T-DRIFT-CHECK: ignored top-level dirs not walked."""
    (tmp_path / ".git").mkdir()
    (tmp_path / ".git" / "head").write_text("xxx")
    (tmp_path / "real.py").write_text("ok")
    hashes = hash_set_walk(tmp_path)
    assert "real.py" in hashes
    assert not any(p.startswith(".git/") for p in hashes)


# ============================================================================
# T-LANE-COVERAGE: dispatch table maps 11 lanes (Phase 8 plan Exit Criterion 1)
# ============================================================================


def test_dispatch_table_has_eleven_lanes() -> None:
    """T-LANE-COVERAGE: 11 sub-script lanes per `-013` §2.2."""
    assert len(driver.DISPATCH_TABLE) == 11


def test_dispatch_table_all_lanes_unique() -> None:
    cli_names = [entry[0] for entry in driver.DISPATCH_TABLE]
    assert len(cli_names) == len(set(cli_names))


def test_dispatch_table_contains_required_lanes() -> None:
    """Each Phase 8 plan lane must be represented in the dispatch table."""
    required = {
        "inventory", "rewrite", "ci", "membase", "chromadb", "dashboard",
        "bridge-split", "backlog-split", "release-readiness-split",
        "production", "rollback",
    }
    actual = {entry[0] for entry in driver.DISPATCH_TABLE}
    assert actual == required, f"Lane mismatch. Missing: {required - actual}; Extra: {actual - required}"


def test_phase_choices_includes_all_dispatch_plus_aggregates() -> None:
    """argparse --phase must accept every dispatch lane plus 'all' and 'verify'."""
    choices = set(driver.PHASE_CHOICES)
    expected_dispatch = {entry[0] for entry in driver.DISPATCH_TABLE}
    assert expected_dispatch.issubset(choices)
    assert "all" in choices
    assert "verify" in choices


# ============================================================================
# Manifest validation tests
# ============================================================================


def test_manifest_validation_rejects_wrong_namespace(tmp_path: Path) -> None:
    """ADR enforcement: applications_namespace must equal <legacy_root>/applications."""
    from rehearse._common import ManifestError, load_manifest
    bad_manifest = tmp_path / "manifest.toml"
    bad_manifest.write_text(
        f'target_root = "{(tmp_path / "wrong" / "Agent_Red").as_posix()}"\n'
        f'legacy_root = "{tmp_path.as_posix()}"\n'
        f'applications_namespace = "{(tmp_path / "wrong").as_posix()}"\n'
    )
    with pytest.raises(ManifestError, match="applications_namespace"):
        load_manifest(bad_manifest)


def test_manifest_validation_accepts_canonical_paths(tmp_path: Path) -> None:
    from rehearse._common import load_manifest
    namespace = tmp_path / "applications"
    target = namespace / "Agent_Red"
    good_manifest = tmp_path / "manifest.toml"
    good_manifest.write_text(
        f'target_root = "{target.as_posix()}"\n'
        f'legacy_root = "{tmp_path.as_posix()}"\n'
        f'applications_namespace = "{namespace.as_posix()}"\n'
    )
    data = load_manifest(good_manifest)
    assert data["target_root"] == target.as_posix()
