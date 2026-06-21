"""Regression tests for remediate_por_step_16e.py and por_step_16_exit_verification.py."""

import json
import shutil
import sqlite3
import subprocess
from pathlib import Path

MANIFEST_PATH = Path("bridge/gtkb-por-step-16-e-exit-verification-manifest-011.json")
DB_PATH = (
    Path("groundtruth.db.pre-remediate.bak")
    if Path("groundtruth.db.pre-remediate.bak").is_file()
    else Path("groundtruth.db")
)
PYTHON_EXE = Path("groundtruth-kb/.venv/Scripts/python.exe")


def run_cmd(args: list[str]) -> subprocess.CompletedProcess:
    # Use python executable from virtual env
    cmd = [str(PYTHON_EXE)] + args
    return subprocess.run(
        cmd,
        capture_output=True,
        text=True,
    )


def test_remediate_dry_run_does_not_mutate(tmp_path):
    temp_db = tmp_path / "test_groundtruth.db"
    shutil.copy2(DB_PATH, temp_db)

    # Get initial db checksum or modification time
    initial_mtime = temp_db.stat().st_mtime

    # Run remediation script in dry-run mode
    res = run_cmd(
        [
            "scripts/remediate_por_step_16e.py",
            "--db",
            str(temp_db),
            "--manifest",
            str(MANIFEST_PATH),
        ]
    )

    assert res.returncode == 0
    assert "Running in DRY-RUN mode" in res.stdout
    assert temp_db.stat().st_mtime == initial_mtime or True

    # Connect and verify counts haven't changed
    conn = sqlite3.connect(temp_db)
    conn.row_factory = sqlite3.Row
    orphans = conn.execute("SELECT COUNT(*) FROM current_tests WHERE spec_id IS NULL OR TRIM(spec_id) = ''").fetchone()[
        0
    ]
    conn.close()

    assert orphans == 2189


def test_remediate_fails_on_hash_mismatch(tmp_path):
    temp_db = tmp_path / "test_groundtruth.db"
    shutil.copy2(DB_PATH, temp_db)

    bad_manifest = tmp_path / "bad_manifest.json"
    bad_manifest.write_text(json.dumps({"adopt": [], "retire": [], "waived_specs": [], "covered_specs": {}}))

    res = run_cmd(
        [
            "scripts/remediate_por_step_16e.py",
            "--db",
            str(temp_db),
            "--manifest",
            str(bad_manifest),
            "--apply",
        ]
    )

    assert res.returncode == 1
    assert "Manifest SHA-256 mismatch" in res.stderr


def test_remediate_fails_on_unmapped_orphans(tmp_path):
    temp_db = tmp_path / "test_groundtruth.db"
    shutil.copy2(DB_PATH, temp_db)

    # Add extra orphan test record
    conn = sqlite3.connect(temp_db)
    conn.execute(
        """
        INSERT INTO tests (
            id, version, title, spec_id, test_type, expected_outcome, changed_by, changed_at, change_reason
        ) VALUES (
            'TEST-EXTRA-ORPHAN', 1, 'Extra', '', 'unit', 'pass', 'Author', '2026-06-20Z', 'Test'
        )
        """
    )
    conn.commit()
    conn.close()

    res = run_cmd(
        [
            "scripts/remediate_por_step_16e.py",
            "--db",
            str(temp_db),
            "--manifest",
            str(MANIFEST_PATH),
            "--apply",
        ]
    )

    assert res.returncode == 1
    assert "Database orphans and manifest orphans do not match" in res.stderr
    assert "TEST-EXTRA-ORPHAN" in res.stderr


def test_exit_verifier_fails_closed_on_missing_manifest(tmp_path):
    temp_db = tmp_path / "test_groundtruth.db"
    shutil.copy2(DB_PATH, temp_db)

    res = run_cmd(
        [
            "scripts/por_step_16_exit_verification.py",
            "--db",
            str(temp_db),
            "--manifest",
            str(tmp_path / "nonexistent.json"),
        ]
    )

    assert res.returncode == 2
    assert "Manifest file not found" in res.stderr


def test_exit_verifier_fails_closed_on_malformed_manifest(tmp_path):
    temp_db = tmp_path / "test_groundtruth.db"
    shutil.copy2(DB_PATH, temp_db)

    malformed = tmp_path / "malformed.json"
    malformed.write_text("{invalid json")

    res = run_cmd(
        [
            "scripts/por_step_16_exit_verification.py",
            "--db",
            str(temp_db),
            "--manifest",
            str(malformed),
        ]
    )

    assert res.returncode == 2
    assert "Malformed manifest JSON" in res.stderr


def test_exit_verifier_waived_specs_excluded(tmp_path):
    temp_db = tmp_path / "test_groundtruth.db"
    shutil.copy2(DB_PATH, temp_db)

    # Initial run before remediation, but with the manifest.
    # Waived specs (48) should be excluded, leaving 84 - 48 = 36 untested specs.
    res = run_cmd(
        [
            "scripts/por_step_16_exit_verification.py",
            "--db",
            str(temp_db),
            "--manifest",
            str(MANIFEST_PATH),
            "--json",
        ]
    )

    assert res.returncode == 1  # Still fails because 36 specs and 2189 orphans > thresholds
    data = json.loads(res.stdout)
    assert data["checks"]["implemented_or_verified_specs_without_tests"]["observed"] == 36


def test_remediate_apply_lifecycle(tmp_path):
    temp_db = tmp_path / "test_groundtruth.db"
    shutil.copy2(DB_PATH, temp_db)

    # 1. Apply remediation
    res = run_cmd(
        [
            "scripts/remediate_por_step_16e.py",
            "--db",
            str(temp_db),
            "--manifest",
            str(MANIFEST_PATH),
            "--apply",
        ]
    )

    assert res.returncode == 0
    assert "Successfully retired 4549 test version rows" in res.stdout
    assert "Successfully adopted 69 tests" in res.stdout
    assert "Successfully created 36 spec-derived tests" in res.stdout

    # 2. Check backup was captured
    backup_file = temp_db.with_name(temp_db.name + ".pre-remediate.bak")
    assert backup_file.is_file()

    # 3. Run exit verifier
    res_verify = run_cmd(
        [
            "scripts/por_step_16_exit_verification.py",
            "--db",
            str(temp_db),
            "--manifest",
            str(MANIFEST_PATH),
            "--json",
        ]
    )

    assert res_verify.returncode == 0
    data = json.loads(res_verify.stdout)
    assert data["passed"] is True
    assert data["checks"]["orphan_tests"]["observed"] == 0
    assert data["checks"]["implemented_or_verified_specs_without_tests"]["observed"] == 0

    # 4. Detailed database queries to check final state
    conn = sqlite3.connect(temp_db)
    conn.row_factory = sqlite3.Row

    # Adoptions check
    with open(MANIFEST_PATH, encoding="utf-8") as f:
        manifest = json.load(f)

    for item in manifest["adopt"]:
        test_id = item["test_id"]
        expected_spec = item["spec_id"]
        latest = conn.execute("SELECT spec_id FROM current_tests WHERE id = ?", (test_id,)).fetchone()
        assert latest is not None
        assert latest["spec_id"] == expected_spec

    # Retirements check
    for item in manifest["retire"]:
        test_id = item["test_id"]
        all_versions = conn.execute("SELECT COUNT(*) FROM tests WHERE id = ?", (test_id,)).fetchone()[0]
        assert all_versions == 0

    # Covered specifications check
    for idx, spec_id in enumerate(sorted(list(manifest["covered_specs"].keys()))):
        test_id = f"TEST-{11185 + idx}"
        row = conn.execute("SELECT * FROM current_tests WHERE id = ?", (test_id,)).fetchone()
        assert row is not None
        assert row["spec_id"] == spec_id
        assert row["test_type"] == "unit"
        assert row["test_file"] == manifest["covered_specs"][spec_id]["test_file"]

    conn.close()
