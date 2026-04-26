"""Tests for Wave 2 Slice 1 validation rules in scripts/rehearse/_common.py.

Per ``bridge/gtkb-isolation-016-phase8-wave2-slice1-001.md`` §3 (NEW)
and ``-002`` (Codex GO).
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from rehearse._common import (  # noqa: E402
    LEGACY_ROOT,
    ManifestError,
    ManifestValidationError,
    load_manifest,
)


_VALID_FILTER_TEMPLATE = (
    "git filter-repo --path <agent-red-paths-from-_path_rewrite> "
    "--path-rename <each-source>:applications/Agent_Red/<each-target>"
)


def _write_manifest(tmp_path: Path, **overrides) -> Path:
    """Write a minimal valid Wave 2 manifest TOML; overrides replace fields."""
    base: dict = {
        "target_root": str((LEGACY_ROOT / "applications" / "Agent_Red").as_posix()),
        "legacy_root": str(LEGACY_ROOT.as_posix()),
        "applications_namespace": str((LEGACY_ROOT / "applications").as_posix()),
        "output_dir": "C:/temp/agent-red-rehearsal",
        "git_strategy": "clone_with_history_filter",
        "git_filter_command_template": _VALID_FILTER_TEMPLATE,
        "db_reconciliation_strategy": "OWNER_DECISION_REQUIRED",
        "phase_1_authority_matrix_path": (
            "independent-progress-assessments/CODEX-INSIGHT-DROPBOX/"
            "GTKB-ISOLATION-001-PHASE1-AUTHORITY-MATRIX-PLAN-2026-04-22.md"
        ),
    }
    base.update(overrides)
    lines: list[str] = []
    for key, value in base.items():
        if value is None:
            continue
        lines.append(f'{key} = "{value}"')
    if "surface_treatments" not in overrides or overrides["surface_treatments"] is _empty_table_marker:
        lines.append("[surface_treatments]")
    manifest_path = tmp_path / "manifest.toml"
    manifest_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return manifest_path


_empty_table_marker = object()


# ----- Rule M1 — placeholder rejection -----

def test_m1_owner_decision_required_in_blocking_field_rejected_for_wave2(tmp_path: Path) -> None:
    """M1: output_dir = OWNER_DECISION_REQUIRED rejected when wave=2."""
    manifest_path = _write_manifest(tmp_path, output_dir="OWNER_DECISION_REQUIRED")
    with pytest.raises(ManifestValidationError, match="M1.*output_dir.*OWNER_DECISION_REQUIRED"):
        load_manifest(manifest_path, wave=2)


def test_m1_owner_decision_required_in_db_reconciliation_accepted_for_wave2(tmp_path: Path) -> None:
    """M1: db_reconciliation_strategy = OWNER_DECISION_REQUIRED accepted at wave=2 (surfaces at wave=3)."""
    manifest_path = _write_manifest(tmp_path)  # default has the placeholder
    data = load_manifest(manifest_path, wave=2)
    assert data["db_reconciliation_strategy"] == "OWNER_DECISION_REQUIRED"


def test_m1_owner_decision_required_in_db_reconciliation_rejected_for_wave3(tmp_path: Path) -> None:
    """M1: db_reconciliation_strategy = OWNER_DECISION_REQUIRED rejected at wave=3."""
    manifest_path = _write_manifest(tmp_path)
    with pytest.raises(ManifestValidationError, match="M1.*db_reconciliation_strategy.*Wave 3"):
        load_manifest(manifest_path, wave=3)


# ----- Rule M2 — output_dir safety -----

def test_m2_output_dir_under_legacy_root_rejected(tmp_path: Path) -> None:
    """M2: output_dir under LEGACY_ROOT rejected."""
    manifest_path = _write_manifest(tmp_path, output_dir=(LEGACY_ROOT / "foo").as_posix())
    with pytest.raises(ManifestValidationError, match="M2.*cannot be under LEGACY_ROOT"):
        load_manifest(manifest_path, wave=2)


def test_m2_output_dir_under_target_root_rejected(tmp_path: Path) -> None:
    """M2: output_dir under TARGET_ROOT_DEFAULT (applications/Agent_Red) rejected."""
    manifest_path = _write_manifest(
        tmp_path, output_dir=(LEGACY_ROOT / "applications" / "Agent_Red" / "foo").as_posix()
    )
    with pytest.raises(ManifestValidationError, match="M2.*cannot be under .*TARGET_ROOT_DEFAULT"):
        load_manifest(manifest_path, wave=2)


def test_m2_output_dir_drive_synced_pattern_rejected(tmp_path: Path) -> None:
    """M2: output_dir under known cloud-sync paths (e.g. OneDrive) rejected via allowlist mismatch."""
    manifest_path = _write_manifest(tmp_path, output_dir="C:/Users/micha/OneDrive/foo")
    with pytest.raises(ManifestValidationError, match="M2.*does not match the sandbox allowlist"):
        load_manifest(manifest_path, wave=2)


def test_m2_output_dir_c_temp_accepted(tmp_path: Path) -> None:
    """M2: output_dir = C:/temp/agent-red-rehearsal* accepted."""
    manifest_path = _write_manifest(tmp_path, output_dir="C:/temp/agent-red-rehearsal-20260426")
    data = load_manifest(manifest_path, wave=2)
    assert data["output_dir"] == "C:/temp/agent-red-rehearsal-20260426"


# ----- Rule M3 — git_strategy + filter template -----

def test_m3_git_strategy_unknown_rejected(tmp_path: Path) -> None:
    """M3: unknown git_strategy rejected."""
    manifest_path = _write_manifest(tmp_path, git_strategy="monorepo_split")
    with pytest.raises(ManifestValidationError, match="M3.*git_strategy.*not in"):
        load_manifest(manifest_path, wave=2)


def test_m3_clone_with_history_filter_requires_command_template(tmp_path: Path) -> None:
    """M3: clone_with_history_filter without required placeholders in template rejected."""
    manifest_path = _write_manifest(
        tmp_path, git_filter_command_template="git filter-repo --foo bar"
    )
    with pytest.raises(ManifestValidationError, match="M3.*missing required placeholder"):
        load_manifest(manifest_path, wave=2)


# ----- Rule M4 — authority matrix path existence -----

def test_m4_authority_matrix_path_missing_rejected(tmp_path: Path) -> None:
    """M4: phase_1_authority_matrix_path pointing at non-existent file rejected."""
    manifest_path = _write_manifest(
        tmp_path, phase_1_authority_matrix_path="independent-progress-assessments/does-not-exist.md"
    )
    with pytest.raises(ManifestValidationError, match="M4.*does not exist on disk"):
        load_manifest(manifest_path, wave=2)


def test_m4_authority_matrix_path_correct_accepted(tmp_path: Path) -> None:
    """M4: real production authority matrix path accepted."""
    # Use the actual production manifest — should pass wave=2 validation.
    production_manifest = (
        LEGACY_ROOT
        / "independent-progress-assessments"
        / "CODEX-INSIGHT-DROPBOX"
        / "rehearsal"
        / "manifest.toml"
    )
    if not production_manifest.exists():
        pytest.skip("production manifest not available in this checkout")
    data = load_manifest(production_manifest, wave=2)
    assert "phase_1_authority_matrix_path" in data


# ----- Rule M5 — surface_treatments shape -----

def test_m5_empty_surface_treatments_accepted_for_source_manifest(tmp_path: Path) -> None:
    """M5: empty [surface_treatments] table accepted for Wave 2 source manifest."""
    manifest_path = _write_manifest(tmp_path)  # default has empty [surface_treatments]
    data = load_manifest(manifest_path, wave=2)
    assert data.get("surface_treatments") == {}


def test_m5_non_dict_surface_treatments_rejected(tmp_path: Path) -> None:
    """M5: surface_treatments as non-table value rejected.

    Note: TOML syntax does not allow a top-level `surface_treatments = "string"`
    coexisting with `[surface_treatments]`. We test the non-dict path by
    injecting via a manifest TOML that uses a string assignment instead of a
    table header.
    """
    manifest_path = tmp_path / "manifest.toml"
    legacy_posix = LEGACY_ROOT.as_posix()
    manifest_path.write_text(
        f'target_root = "{legacy_posix}/applications/Agent_Red"\n'
        f'legacy_root = "{legacy_posix}"\n'
        f'applications_namespace = "{legacy_posix}/applications"\n'
        f'output_dir = "C:/temp/agent-red-rehearsal"\n'
        f'git_strategy = "fresh_repo"\n'
        f'phase_1_authority_matrix_path = "independent-progress-assessments/'
        f'CODEX-INSIGHT-DROPBOX/GTKB-ISOLATION-001-PHASE1-AUTHORITY-MATRIX-PLAN-2026-04-22.md"\n'
        f'surface_treatments = "not-a-table"\n',
        encoding="utf-8",
    )
    with pytest.raises(ManifestValidationError, match="M5.*must be a TOML table"):
        load_manifest(manifest_path, wave=2)


# ----- Backward-compat regression -----

def test_wave1_default_preserves_existing_behavior(tmp_path: Path) -> None:
    """Wave 1 default (load_manifest(path)) preserves existing behavior:
    no M1-M5 enforcement; Wave 1 callers continue to pass."""
    # A manifest that would FAIL all of M1-M5 except ADR fields:
    legacy_posix = LEGACY_ROOT.as_posix()
    manifest_path = tmp_path / "manifest.toml"
    manifest_path.write_text(
        f'target_root = "{legacy_posix}/applications/Agent_Red"\n'
        f'legacy_root = "{legacy_posix}"\n'
        f'applications_namespace = "{legacy_posix}/applications"\n'
        f'output_dir = "OWNER_DECISION_REQUIRED"\n'
        f'git_strategy = "OWNER_DECISION_REQUIRED"\n'
        # No phase_1_authority_matrix_path; no surface_treatments
        ,
        encoding="utf-8",
    )
    # Wave 1 default — no exception raised.
    data = load_manifest(manifest_path)
    assert data["target_root"].endswith("/applications/Agent_Red")
    # The same manifest at wave=2 SHOULD raise (regression armor that the
    # wave parameter actually gates the new rules).
    with pytest.raises(ManifestValidationError):
        load_manifest(manifest_path, wave=2)
