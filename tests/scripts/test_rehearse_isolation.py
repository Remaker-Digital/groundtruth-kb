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
import rehearse_isolation as driver  # noqa: E402
from rehearse._common import (  # noqa: E402
    LEGACY_CONFLATED_SURFACES,
    TargetRootError,
    hash_set_walk,
    validate_target_root,
)

# ============================================================================
# T-DRIVER-1: refusal logic (parametric over conflated surfaces)
# ============================================================================


@pytest.mark.parametrize("surface", sorted(LEGACY_CONFLATED_SURFACES))
def test_target_root_refused_in_each_conflated_surface(
    tmp_path: Path, surface: str, monkeypatch: pytest.MonkeyPatch
) -> None:
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
        "inventory",
        "rewrite",
        "ci",
        "membase",
        "chromadb",
        "dashboard",
        "bridge-split",
        "backlog-split",
        "release-readiness-split",
        "production",
        "rollback",
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


# =============================================================================
# Slice 3 driver wire-up tests (per
# bridge/gtkb-isolation-016-phase8-wave2-slice3-003.md REVISED-1 + -004 GO).
# All fixture-based; no live-root walks.
# =============================================================================

import json as _json  # noqa: E402

import rehearse_isolation as _driver  # noqa: E402
from rehearse._common import LEGACY_ROOT, ManifestValidationError  # noqa: E402

_PRODUCTION_MANIFEST_PATH = (
    LEGACY_ROOT / "independent-progress-assessments" / "CODEX-INSIGHT-DROPBOX" / "rehearsal" / "manifest.toml"
)


def _slice3_skip_if_no_production_manifest():
    if not _PRODUCTION_MANIFEST_PATH.exists():
        pytest.skip("production manifest unavailable in this checkout")


# ----- F1: --execute opt-in semantics -----


def test_main_loads_manifest_at_wave2(monkeypatch: pytest.MonkeyPatch) -> None:
    """main() calls load_manifest with wave=2."""
    _slice3_skip_if_no_production_manifest()
    captured: dict = {}

    def _spy_load(path, *, wave=1, is_runtime_manifest=False):
        captured["wave"] = wave
        captured["is_runtime_manifest"] = is_runtime_manifest
        return {
            "target_root": str((LEGACY_ROOT / "applications" / "Agent_Red").as_posix()),
            "legacy_root": str(LEGACY_ROOT.as_posix()),
            "applications_namespace": str((LEGACY_ROOT / "applications").as_posix()),
            "output_dir": "C:/temp/agent-red-rehearsal",
        }

    monkeypatch.setattr(_driver, "load_manifest", _spy_load)
    rc = _driver.main(["--phase", "verify"])
    assert rc == _driver.EXIT_OK
    assert captured["wave"] == 2


def test_execute_flag_enables_real_run() -> None:
    """--execute does NOT trigger v1 hard refusal."""
    _slice3_skip_if_no_production_manifest()
    rc = _driver.main(["--phase", "verify", "--execute"])
    assert rc == _driver.EXIT_OK


def test_no_dry_run_still_refused_even_with_execute() -> None:
    """--no-dry-run continues to be refused even when --execute is also passed."""
    rc = _driver.main(["--phase", "verify", "--execute", "--no-dry-run"])
    assert rc == _driver.EXIT_REFUSE


# ----- output_dir construction + F2: override safety -----


def test_resolve_output_dir_default_appends_iso_timestamp() -> None:
    manifest = {"output_dir": "C:/temp/agent-red-rehearsal"}
    result = _driver._resolve_output_dir(manifest, override=None)
    s = str(result)
    assert "agent-red-rehearsal-" in s
    suffix = s.split("agent-red-rehearsal-", 1)[1]
    assert len(suffix) == 16 and suffix.endswith("Z") and "T" in suffix


def test_output_dir_override_in_sandbox_accepted() -> None:
    manifest = {"output_dir": "C:/temp/agent-red-rehearsal"}
    override = Path("C:/temp/agent-red-rehearsal-custom")
    result = _driver._resolve_output_dir(manifest, override=override)
    assert result == override


def test_output_dir_override_under_legacy_root_rejected() -> None:
    manifest = {"output_dir": "C:/temp/agent-red-rehearsal"}
    override = LEGACY_ROOT / "foo"
    with pytest.raises(ManifestValidationError, match="M2.*LEGACY_ROOT"):
        _driver._resolve_output_dir(manifest, override=override)


def test_output_dir_override_under_target_root_rejected() -> None:
    manifest = {"output_dir": "C:/temp/agent-red-rehearsal"}
    override = LEGACY_ROOT / "applications" / "Agent_Red" / "foo"
    with pytest.raises(ManifestValidationError, match="M2.*TARGET_ROOT_DEFAULT"):
        _driver._resolve_output_dir(manifest, override=override)


def test_output_dir_override_non_allowlisted_rejected() -> None:
    manifest = {"output_dir": "C:/temp/agent-red-rehearsal"}
    override = Path("C:/Users/micha/OneDrive/foo")
    with pytest.raises(ManifestValidationError, match="M2.*sandbox allowlist"):
        _driver._resolve_output_dir(manifest, override=override)


# ----- F3: dispatch exception narrowing -----


def test_dispatch_lane_module_missing_returns_skipped() -> None:
    """A lane whose module file does not exist returns status='skipped'.

    Per Slice 11 (dashboard lane landed at S314), this test now uses
    ``rollback`` as the still-missing lane fixture. (Slice 10 ``chromadb``
    module landed WIP at commit ``c4acfc13`` in S313; ``rollback`` is the
    last still-missing leaf in the Phase 8 dispatch table.) When the
    rollback lane lands, this test should be updated to assert the
    dispatcher correctly handles "all lanes implemented" via a different
    mechanism (e.g., a deliberately-missing fixture path). The test's
    intent — that the dispatcher correctly distinguishes "module not on
    disk" from runtime defects — is unchanged.
    """
    result = _driver._dispatch("rollback", manifest={}, output_dir=Path("ignored"), dry_run=True)
    assert result["status"] == "skipped"
    assert any("not yet implemented" in w for w in result["warnings"])


def test_dispatch_lane_module_broken_dependency_returns_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A lane whose module imports a missing dependency returns status='error'."""
    real_import = _driver.importlib.import_module

    def _broken_import(name, *args, **kwargs):
        if name == "rehearse._path_rewrite":
            raise ModuleNotFoundError(
                "No module named 'some_missing_dependency'",
                name="some_missing_dependency",
            )
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(_driver.importlib, "import_module", _broken_import)
    result = _driver._dispatch("rewrite", manifest={}, output_dir=Path("ignored"), dry_run=True)
    assert result["status"] == "error"
    assert any("missing dependency" in w and "some_missing_dependency" in w for w in result["warnings"])


def test_dispatch_lane_module_missing_run_function_returns_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A lane module that exists but lacks run() returns status='error'."""
    real_import = _driver.importlib.import_module

    class _ModWithoutRun:
        pass

    def _import_module_without_run(name, *args, **kwargs):
        if name == "rehearse._path_rewrite":
            return _ModWithoutRun()
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(_driver.importlib, "import_module", _import_module_without_run)
    result = _driver._dispatch("rewrite", manifest={}, output_dir=Path("ignored"), dry_run=True)
    assert result["status"] == "error"
    assert any("module exists but has no" in w for w in result["warnings"])


def test_dispatch_unknown_phase_raises_valueerror() -> None:
    with pytest.raises(ValueError, match="unknown phase"):
        _driver._dispatch(
            "nonexistent-phase",
            manifest={},
            output_dir=Path("ignored"),
            dry_run=True,
        )


# ----- run-summary.json emission (per GO -004 implementation note) -----


def test_run_summary_written_when_lane_returns_ok(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """Summary file appears when at least one lane returns ok."""
    _slice3_skip_if_no_production_manifest()
    output_dir = tmp_path / "run-output"

    def _spy_dispatch(phase_name, manifest, output_dir, *, dry_run):
        return {"status": "ok", "output_files": [], "metrics": {}, "warnings": []}

    monkeypatch.setattr(_driver, "_dispatch", _spy_dispatch)
    monkeypatch.setattr(_driver, "_resolve_output_dir", lambda m, override=None: output_dir)
    rc = _driver.main(["--phase", "inventory", "--execute"])
    assert rc == _driver.EXIT_OK
    summary_path = output_dir / "run-summary.json"
    assert summary_path.exists(), "run-summary.json should be emitted on ok"
    summary = _json.loads(summary_path.read_text(encoding="utf-8"))
    assert summary["dry_run"] is False
    assert "inventory" in summary["results"]


def test_run_summary_not_written_when_all_lanes_skipped(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """Summary file does NOT appear if every lane returned skipped."""
    _slice3_skip_if_no_production_manifest()
    output_dir = tmp_path / "run-output-skipped"

    def _all_skipped_dispatch(phase_name, manifest, output_dir, *, dry_run):
        return {
            "status": "skipped",
            "output_files": [],
            "metrics": {},
            "warnings": ["test stub: not implemented"],
        }

    monkeypatch.setattr(_driver, "_dispatch", _all_skipped_dispatch)
    monkeypatch.setattr(_driver, "_resolve_output_dir", lambda m, override=None: output_dir)
    rc = _driver.main(["--phase", "rewrite"])
    assert rc == _driver.EXIT_OK
    summary_path = output_dir / "run-summary.json"
    assert not summary_path.exists(), "run-summary.json should NOT be emitted when every lane was skipped"


# ----- Slice 4: rewrite lane is now implemented (driver integration) -----


def test_driver_dispatches_path_rewrite_lane_with_module_now_present(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """Per Slice 4 -003 §3 driver integration: _dispatch('rewrite', ...) now
    returns non-skipped status because _path_rewrite.py is on disk.

    Verifies Slice 3 -005 §7 sequencing claim that "Stage B-D lanes become
    independently implementable in any order; each is its own bridge" —
    Slice 4 lights up the rewrite lane via module addition only, no driver
    changes. classify-tree subprocess mocked per Codex GO -004 condition 3
    (do not run live classify-tree against LEGACY_ROOT in unit tests).
    """
    import subprocess as _subprocess

    def _fake_run(cmd, *args, **kwargs):
        if "--output" in cmd:
            output_idx = cmd.index("--output") + 1
            output_path = Path(cmd[output_idx])
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(
                _json.dumps(
                    {
                        "generated": "test",
                        "gt_kb_version": "test",
                        "gt_kb_head": "test",
                        "target_tree": str(tmp_path),
                        "target_head": "test",
                        "total_paths_classified": 0,
                        "owner_decision_pending_rows": 0,
                        "rows": [],
                    }
                ),
                encoding="utf-8",
            )
        return _subprocess.CompletedProcess(args=cmd, returncode=0, stdout="", stderr="")

    monkeypatch.setattr(_subprocess, "run", _fake_run)

    output_dir = tmp_path / "rewrite-driver-test"
    output_dir.mkdir()
    manifest = {
        "target_root": str((tmp_path / "applications" / "Agent_Red").as_posix()),
        "legacy_root": str(tmp_path.as_posix()),
        "applications_namespace": str((tmp_path / "applications").as_posix()),
        "output_dir": "C:/temp/agent-red-rehearsal",
        "git_strategy": "clone_with_history_filter",
        "excluded_paths": [],
    }

    result = _driver._dispatch("rewrite", manifest, output_dir, dry_run=False)

    # Pre-Slice-4 expectation: would have been "skipped" because the module
    # didn't exist on disk. Post-Slice-4: must be "ok" — the rewrite lane is
    # implemented and the synthetic empty classification produces a valid
    # (zero-rewrite) result.
    assert result["status"] == "ok", f"rewrite lane should be implemented post-Slice-4, got {result}"
    assert result["status"] != "skipped"
