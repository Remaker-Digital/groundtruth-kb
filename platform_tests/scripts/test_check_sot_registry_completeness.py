# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Tests for ``_check_sot_registry_completeness`` doctor check.

Verifies GOV-PLATFORM-SOT-REGISTRY-001 acceptance — the doctor check runs at
WARN severity (``status="warning"``) when drift is observed; ``"info"`` when
the registry file is absent (adopter without Slice 7 rollout); ``"fail"`` only
on structural parse failure of the TOML; ``"pass"`` when parity holds and all
active storage_paths resolve.

Bridge:
``bridge/gtkb-platform-sot-consolidation-slice-1-governance-foundation-005.md``
(GO).
"""

from __future__ import annotations

import sqlite3
import textwrap
from pathlib import Path

import pytest
from groundtruth_kb.project.doctor import _check_sot_registry_completeness


def _write_registry(target: Path, body: str) -> Path:
    """Write ``config/registry/sot-artifacts.toml`` under ``target`` with body."""
    registry_path = target / "config" / "registry" / "sot-artifacts.toml"
    registry_path.parent.mkdir(parents=True, exist_ok=True)
    registry_path.write_text(textwrap.dedent(body), encoding="utf-8")
    return registry_path


def _minimal_valid_record(record_id: str, storage_path: str) -> str:
    return textwrap.dedent(
        f"""
        [[artifacts]]
        id = "{record_id}"
        domain = "control_surface"
        lifecycle = "active"
        storage_path = "{storage_path}"
        authority_spec_id = "GOV-X"
        mutation_api = "n/a"
        versioning_policy = "git_tracked"
        backup_policy = "git_tracked"
        health_check_function = ""
        owner_role = "shared"
        """
    )


def _init_sot_artifacts_table(db_path: Path) -> None:
    """Create the minimum sot_artifacts table + view needed by load_projection."""
    conn = sqlite3.connect(str(db_path))
    try:
        conn.executescript(
            """
            CREATE TABLE sot_artifacts (
                rowid INTEGER PRIMARY KEY AUTOINCREMENT,
                id TEXT NOT NULL,
                version INTEGER NOT NULL,
                domain TEXT NOT NULL,
                lifecycle TEXT NOT NULL,
                storage_path TEXT NOT NULL,
                authority_spec_id TEXT NOT NULL,
                mutation_api TEXT NOT NULL,
                versioning_policy TEXT NOT NULL,
                backup_policy TEXT NOT NULL,
                health_check_function TEXT,
                owner_role TEXT NOT NULL,
                depends_on TEXT,
                forbidden_substitutes TEXT,
                notes TEXT,
                changed_by TEXT NOT NULL,
                changed_at TEXT NOT NULL,
                change_reason TEXT NOT NULL,
                UNIQUE(id, version)
            );
            CREATE VIEW current_sot_artifacts AS
            SELECT s.* FROM sot_artifacts s
            INNER JOIN (
                SELECT id, MAX(version) AS max_version FROM sot_artifacts GROUP BY id
            ) latest ON s.id = latest.id AND s.version = latest.max_version;
            """
        )
        conn.commit()
    finally:
        conn.close()


def _insert_projection_row(db_path: Path, record_id: str, storage_path: str, lifecycle: str = "active") -> None:
    """Insert one current-version projection row."""
    conn = sqlite3.connect(str(db_path))
    try:
        conn.execute(
            """
            INSERT INTO sot_artifacts (
                id, version, domain, lifecycle, storage_path, authority_spec_id,
                mutation_api, versioning_policy, backup_policy, health_check_function,
                owner_role, depends_on, forbidden_substitutes, notes,
                changed_by, changed_at, change_reason
            ) VALUES (?, 1, ?, ?, ?, ?, ?, ?, ?, ?, ?, NULL, NULL, NULL, ?, ?, ?)
            """,
            (
                record_id,
                "control_surface",
                lifecycle,
                storage_path,
                "GOV-X",
                "n/a",
                "git_tracked",
                "git_tracked",
                "",
                "shared",
                "test",
                "2026-06-04T00:00:00Z",
                "fixture",
            ),
        )
        conn.commit()
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# GOV-PLATFORM-SOT-REGISTRY-001 acceptance: doctor check runs at WARN severity
# ---------------------------------------------------------------------------


def test_registry_missing_returns_info_skip(tmp_path: Path) -> None:
    """An adopter project before Slice 7 rollout has no registry; skip (info)."""
    result = _check_sot_registry_completeness(tmp_path)
    assert result.status == "info"
    assert "not present" in result.message


def test_check_runs_at_warn_severity_on_empty_projection(tmp_path: Path) -> None:
    """When the registry exists but MemBase projection is empty, status is warning.

    This is the WARN severity acceptance for GOV-PLATFORM-SOT-REGISTRY-001:
    drift is reported, never fail.
    """
    _write_registry(tmp_path, _minimal_valid_record("rec-1", "x"))
    db_path = tmp_path / "groundtruth.db"
    _init_sot_artifacts_table(db_path)
    result = _check_sot_registry_completeness(tmp_path)
    assert result.status == "warning"
    assert "projection empty" in result.message or "parity drift" in result.message
    assert result.required is False


def test_check_passes_when_toml_and_projection_match(tmp_path: Path) -> None:
    """When TOML records match the MemBase projection exactly, status is pass."""
    target_file = tmp_path / "x"
    target_file.write_text("present", encoding="utf-8")
    _write_registry(tmp_path, _minimal_valid_record("rec-1", "x"))
    db_path = tmp_path / "groundtruth.db"
    _init_sot_artifacts_table(db_path)
    _insert_projection_row(db_path, "rec-1", "x")
    result = _check_sot_registry_completeness(tmp_path)
    assert result.status == "pass", f"expected pass, got {result.status}: {result.message}"


def test_check_warns_on_unresolved_active_storage_path(tmp_path: Path) -> None:
    """When an active record's storage_path doesn't resolve, status is warning."""
    _write_registry(tmp_path, _minimal_valid_record("rec-1", "missing-path"))
    db_path = tmp_path / "groundtruth.db"
    _init_sot_artifacts_table(db_path)
    _insert_projection_row(db_path, "rec-1", "missing-path")
    result = _check_sot_registry_completeness(tmp_path)
    assert result.status == "warning"
    assert "unresolved" in result.message


def test_check_skips_membase_prefix_storage_paths(tmp_path: Path) -> None:
    """Storage paths prefixed ``membase:`` are not point-resolvable; skip them."""
    _write_registry(tmp_path, _minimal_valid_record("rec-1", "membase:some_table"))
    db_path = tmp_path / "groundtruth.db"
    _init_sot_artifacts_table(db_path)
    _insert_projection_row(db_path, "rec-1", "membase:some_table")
    result = _check_sot_registry_completeness(tmp_path)
    assert result.status == "pass", f"expected pass, got {result.status}: {result.message}"


def test_check_warns_on_field_divergence(tmp_path: Path) -> None:
    """Field-level drift between TOML and projection raises warning."""
    target_file = tmp_path / "x"
    target_file.write_text("present", encoding="utf-8")
    _write_registry(tmp_path, _minimal_valid_record("rec-1", "x"))
    db_path = tmp_path / "groundtruth.db"
    _init_sot_artifacts_table(db_path)
    # Insert a projection row with mismatched lifecycle.
    _insert_projection_row(db_path, "rec-1", "x", lifecycle="deprecated")
    result = _check_sot_registry_completeness(tmp_path)
    assert result.status == "warning"
    assert "parity drift" in result.message or "field drift" in result.message


def test_check_fails_on_unparseable_toml(tmp_path: Path) -> None:
    """A registry file that fails to load returns fail (structural defect)."""
    body = textwrap.dedent(
        """
        [[artifacts]]
        id = "bad"
        domain = "not-a-real-domain"
        lifecycle = "active"
        storage_path = "x"
        authority_spec_id = "GOV-X"
        mutation_api = "n/a"
        versioning_policy = "git_tracked"
        backup_policy = "git_tracked"
        health_check_function = ""
        owner_role = "shared"
        """
    )
    _write_registry(tmp_path, body)
    db_path = tmp_path / "groundtruth.db"
    _init_sot_artifacts_table(db_path)
    result = _check_sot_registry_completeness(tmp_path)
    assert result.status == "fail"
    assert "failed to load" in result.message


def test_check_skips_glob_storage_paths(tmp_path: Path) -> None:
    """Glob-pattern storage paths (containing * ? [ ]) are not point-resolvable."""
    _write_registry(tmp_path, _minimal_valid_record("rec-1", "config/governance/*.toml"))
    db_path = tmp_path / "groundtruth.db"
    _init_sot_artifacts_table(db_path)
    _insert_projection_row(db_path, "rec-1", "config/governance/*.toml")
    result = _check_sot_registry_completeness(tmp_path)
    assert result.status == "pass", f"expected pass, got {result.status}: {result.message}"


def test_check_skips_deprecated_lifecycle_records(tmp_path: Path) -> None:
    """Deprecated records are not asserted to resolve on disk."""
    body = _minimal_valid_record("rec-1", "missing-path").replace('lifecycle = "active"', 'lifecycle = "deprecated"')
    _write_registry(tmp_path, body)
    db_path = tmp_path / "groundtruth.db"
    _init_sot_artifacts_table(db_path)
    _insert_projection_row(db_path, "rec-1", "missing-path", lifecycle="deprecated")
    result = _check_sot_registry_completeness(tmp_path)
    # Should pass: lifecycle=deprecated records are skipped in the on-disk check.
    assert result.status == "pass", f"expected pass, got {result.status}: {result.message}"


def test_check_warning_message_includes_record_count(tmp_path: Path) -> None:
    """Warning message should report the number of SoT records loaded."""
    _write_registry(tmp_path, _minimal_valid_record("rec-1", "x"))
    db_path = tmp_path / "groundtruth.db"
    _init_sot_artifacts_table(db_path)
    result = _check_sot_registry_completeness(tmp_path)
    assert result.status == "warning"
    assert "1 SoT records" in result.message


@pytest.mark.parametrize(
    "lifecycle,storage_path",
    [
        ("active", "membase:foo"),
        ("archive", "anywhere"),
    ],
)
def test_check_does_not_assert_storage_path_for_non_concrete(tmp_path: Path, lifecycle: str, storage_path: str) -> None:
    """Archive lifecycle + membase: storage paths are not asserted on disk."""
    body = _minimal_valid_record("rec-1", storage_path).replace('lifecycle = "active"', f'lifecycle = "{lifecycle}"')
    _write_registry(tmp_path, body)
    db_path = tmp_path / "groundtruth.db"
    _init_sot_artifacts_table(db_path)
    _insert_projection_row(db_path, "rec-1", storage_path, lifecycle=lifecycle)
    result = _check_sot_registry_completeness(tmp_path)
    assert result.status == "pass", f"expected pass, got {result.status}: {result.message}"
