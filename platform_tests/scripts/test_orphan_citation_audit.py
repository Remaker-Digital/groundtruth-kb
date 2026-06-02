# (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Tests for the orphan citation audit and doctor integration."""

from __future__ import annotations

import importlib.util
import json
import sqlite3
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = REPO_ROOT / "scripts" / "orphan_citation_audit.py"
SRC_ROOT = REPO_ROOT / "groundtruth-kb" / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))


def _load_audit_module():
    spec = importlib.util.spec_from_file_location("orphan_citation_audit_under_test", SCRIPT_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules["orphan_citation_audit_under_test"] = module
    spec.loader.exec_module(module)
    return module


def _seed_minimal_db(db_path: Path, *, specs: list[str] | None = None) -> None:
    conn = sqlite3.connect(str(db_path))
    try:
        conn.execute("CREATE TABLE specifications (id TEXT)")
        conn.execute("CREATE TABLE deliberations (id TEXT)")
        conn.execute("CREATE TABLE work_items (id TEXT)")
        for spec_id in specs or []:
            conn.execute("INSERT INTO specifications (id) VALUES (?)", (spec_id,))
        conn.commit()
    finally:
        conn.close()


def test_audit_detects_orphan_citation(tmp_path: Path) -> None:
    audit = _load_audit_module()
    src = tmp_path / "src"
    src.mkdir()
    (src / "sample.py").write_text("# See SPEC-MISSING-001\n", encoding="utf-8")
    _seed_minimal_db(tmp_path / "groundtruth.db")

    result = audit.audit_root(tmp_path, tmp_path / "groundtruth.db", [src])

    assert result.scanned_files == 1
    assert [orphan.anchor for orphan in result.orphans] == ["SPEC-MISSING-001"]
    assert result.orphans[0].kind == "spec"


def test_audit_resolves_known_good_spec(tmp_path: Path) -> None:
    audit = _load_audit_module()
    src = tmp_path / "src"
    src.mkdir()
    (src / "sample.md").write_text("See SPEC-OK-001 for context.\n", encoding="utf-8")
    _seed_minimal_db(tmp_path / "groundtruth.db", specs=["SPEC-OK-001"])

    result = audit.audit_root(tmp_path, tmp_path / "groundtruth.db", [src])

    assert result.orphans == []
    assert result.resolved["spec"] == 1


def test_audit_json_output_shape_is_stable(tmp_path: Path) -> None:
    audit = _load_audit_module()
    src = tmp_path / "src"
    src.mkdir()
    (src / "sample.py").write_text("# See SPEC-MISSING-001\n", encoding="utf-8")
    _seed_minimal_db(tmp_path / "groundtruth.db")

    payload = audit.audit_root(tmp_path, tmp_path / "groundtruth.db", [src]).to_jsonable()

    assert set(payload) == {"root", "db_path", "scanned_files", "resolved", "orphans"}
    assert set(payload["resolved"]) == {"spec", "deliberation", "work_item", "bridge"}
    assert set(payload["orphans"][0]) == {"anchor", "kind", "path", "line"}


def test_cli_exit_code_reflects_orphan_presence(tmp_path: Path) -> None:
    src = tmp_path / "src"
    src.mkdir()
    db_path = tmp_path / "groundtruth.db"
    _seed_minimal_db(db_path, specs=["SPEC-OK-001"])
    sample = src / "sample.py"

    sample.write_text("# See SPEC-MISSING-001\n", encoding="utf-8")
    orphan_result = subprocess.run(
        [sys.executable, str(SCRIPT_PATH), "--root", str(tmp_path), "--db", str(db_path), "--scan-dir", "src"],
        text=True,
        capture_output=True,
        check=False,
    )
    assert orphan_result.returncode == 1
    assert json.loads(orphan_result.stdout)["orphans"][0]["anchor"] == "SPEC-MISSING-001"

    sample.write_text("# See SPEC-OK-001\n", encoding="utf-8")
    clean_result = subprocess.run(
        [sys.executable, str(SCRIPT_PATH), "--root", str(tmp_path), "--db", str(db_path), "--scan-dir", "src"],
        text=True,
        capture_output=True,
        check=False,
    )
    assert clean_result.returncode == 0
    assert json.loads(clean_result.stdout)["orphans"] == []


def test_doctor_check_invokes_audit_and_surfaces_orphans(tmp_path: Path) -> None:
    from groundtruth_kb.project import doctor

    src = tmp_path / "src"
    src.mkdir()
    (src / "sample.py").write_text("# See SPEC-MISSING-001\n", encoding="utf-8")
    _seed_minimal_db(tmp_path / "groundtruth.db")

    check = doctor._check_orphan_citations(tmp_path)

    assert check.name == "Orphan citations"
    assert check.status == "warning"
    assert "1 orphan citation" in check.message
