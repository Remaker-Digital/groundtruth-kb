"""Remediation script for POR Step 16.E exit verification."""

import argparse
import datetime
import hashlib
import json
import shutil
import sqlite3
import sys
from pathlib import Path

EXPECTED_HASH = "c12dff39354a3b4eb117bada2e3237b968b8c946b1879d94fbd7a0293aeffbda"
DEFAULT_DB_PATH = Path("groundtruth.db")


def calculate_sha256(filepath: Path) -> str:
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(8192):
            h.update(chunk)
    return h.hexdigest()


def load_manifest(manifest_path: Path) -> dict:
    if not manifest_path.is_file():
        raise FileNotFoundError(f"Manifest file not found: {manifest_path}")

    # Hash check
    actual_hash = calculate_sha256(manifest_path)
    if actual_hash.lower() != EXPECTED_HASH.lower():
        raise ValueError(f"Manifest SHA-256 mismatch!\nExpected: {EXPECTED_HASH}\nActual:   {actual_hash}")

    try:
        with open(manifest_path, encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Malformed manifest JSON: {exc}") from exc

    for key in ["adopt", "retire", "waived_specs", "covered_specs"]:
        if key not in data:
            raise ValueError(f"Manifest missing required key: {key}")

    return data


def verify_boundary(conn: sqlite3.Connection, manifest: dict) -> None:
    # Query database for all orphan tests
    cursor = conn.execute(
        """
        SELECT id FROM current_tests
        WHERE spec_id IS NULL OR TRIM(spec_id) = ''
        """
    )
    db_orphans = {row["id"] for row in cursor}

    # Manifest orphans
    manifest_adopt = {item["test_id"] for item in manifest["adopt"]}
    manifest_retire = {item["test_id"] for item in manifest["retire"]}
    manifest_orphans = manifest_adopt.union(manifest_retire)

    # Check for exact set match
    extra_in_db = db_orphans - manifest_orphans
    extra_in_manifest = manifest_orphans - db_orphans

    if extra_in_db or extra_in_manifest:
        msg = ["Database orphans and manifest orphans do not match!"]
        if extra_in_db:
            msg.append(f"Orphan tests in database but not in manifest: {sorted(list(extra_in_db))}")
        if extra_in_manifest:
            msg.append(f"Orphan tests in manifest but not in database: {sorted(list(extra_in_manifest))}")
        raise ValueError("\n".join(msg))


def execute_remediation(db_path: Path, manifest: dict, dry_run: bool) -> None:
    # Set up DB connection
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row

    try:
        # Check boundary first
        verify_boundary(conn, manifest)

        adopt_list = manifest["adopt"]
        retire_list = manifest["retire"]
        covered_specs = manifest["covered_specs"]
        waived_specs = manifest["waived_specs"]

        print("Verified boundary safety successfully.")
        print("Planned changes:")
        print(f"- Adopt {len(adopt_list)} orphan tests by incrementing version and setting spec_id.")
        print(f"- Retire {len(retire_list)} legacy tests by deleting all versions from the database.")
        print(f"- Map {len(covered_specs)} covered specifications to platform tests.")
        print(f"- Exclude {len(waived_specs)} waived specifications from untested count.")

        if dry_run:
            print("Running in DRY-RUN mode. No changes were written to the database.")
            return

        # Perform backup
        backup_path = db_path.with_name(db_path.name + ".pre-remediate.bak")
        shutil.copy2(db_path, backup_path)
        print(f"Captured pre-mutation backup: {backup_path}")

        # Start transaction
        conn.execute("BEGIN TRANSACTION")

        # 1. Retire tests
        retire_count = 0
        for item in retire_list:
            test_id = item["test_id"]
            c = conn.execute("DELETE FROM tests WHERE id = ?", (test_id,))
            retire_count += c.rowcount

        # 2. Adopt tests
        adopt_count = 0
        changed_at = datetime.datetime.utcnow().isoformat() + "Z"
        for item in adopt_list:
            test_id = item["test_id"]
            spec_id = item["spec_id"]

            row = conn.execute("SELECT * FROM current_tests WHERE id = ?", (test_id,)).fetchone()
            if not row:
                raise ValueError(f"Orphan test {test_id} not found in database current_tests view during adoption.")

            test_data = dict(row)
            new_version = int(test_data["version"]) + 1

            conn.execute(
                """
                INSERT INTO tests (
                    id, version, title, spec_id, test_type, test_file, test_class,
                    test_function, description, expected_outcome, last_result,
                    last_executed_at, changed_by, changed_at, change_reason
                ) VALUES (
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
                )
                """,
                (
                    test_id,
                    new_version,
                    test_data["title"],
                    spec_id,
                    test_data["test_type"],
                    test_data["test_file"],
                    test_data["test_class"],
                    test_data["test_function"],
                    test_data["description"],
                    test_data["expected_outcome"],
                    test_data["last_result"],
                    test_data["last_executed_at"],
                    "Prime Builder (Antigravity)",
                    changed_at,
                    "Adopt orphan test under POR Step 16.E",
                ),
            )
            adopt_count += 1

        # 3. Link covered specs (TEST-11185 through TEST-11220)
        link_count = 0
        sorted_specs = sorted(list(covered_specs.keys()))
        for idx, spec_id in enumerate(sorted_specs):
            test_id = f"TEST-{11185 + idx}"
            mapping = covered_specs[spec_id]

            conn.execute(
                """
                INSERT INTO tests (
                    id, version, title, spec_id, test_type, test_file, test_class,
                    test_function, description, expected_outcome, last_result,
                    last_executed_at, changed_by, changed_at, change_reason
                ) VALUES (
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
                )
                """,
                (
                    test_id,
                    1,
                    f"Spec-derived test for {spec_id}",
                    spec_id,
                    "unit",
                    mapping["test_file"],
                    mapping["test_class"],
                    mapping["test_function"],
                    f"Automatically mapped spec-derived test for {spec_id} under POR Step 16.E exit verification",
                    "pass",
                    None,
                    None,
                    "Prime Builder (Antigravity)",
                    changed_at,
                    f"Link spec {spec_id} to platform test under POR Step 16.E",
                ),
            )
            link_count += 1

        conn.commit()
        print("Atomically committed all changes to database.")
        print(f"Successfully retired {retire_count} test version rows.")
        print(f"Successfully adopted {adopt_count} tests.")
        print(f"Successfully created {link_count} spec-derived tests linking specifications.")

    except Exception as exc:
        if "conn" in locals():
            try:
                conn.execute("ROLLBACK")
            except sqlite3.OperationalError:
                pass
        print(f"ERROR during database remediation: {exc}", file=sys.stderr)
        raise exc
    finally:
        if "conn" in locals():
            conn.close()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", type=Path, default=Path.cwd())
    parser.add_argument("--db", type=Path, default=None)
    parser.add_argument("--manifest", type=Path, default=None)
    parser.add_argument("--apply", action="store_true", help="Apply modifications to database")
    args = parser.parse_args(argv)

    db_path = args.db or DEFAULT_DB_PATH
    if not db_path.is_absolute():
        db_path = args.project_root / db_path
    db_path = db_path.resolve()

    manifest_path = args.manifest
    if manifest_path is None:
        manifest_path = args.project_root / "bridge" / "gtkb-por-step-16-e-exit-verification-manifest-011.json"
    else:
        manifest_path = manifest_path.resolve()

    try:
        manifest = load_manifest(manifest_path)
        execute_remediation(db_path, manifest, dry_run=not args.apply)
    except Exception as exc:
        print(f"Remediation failed: {exc}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
