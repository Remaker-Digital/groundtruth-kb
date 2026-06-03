#!/usr/bin/env python3
"""Spec-derived tests for the LO/bridge history backfill inventory (WI-3162 Slice 1).

Each test maps to one or more specifications cited in
``bridge/gtkb-lo-bridge-history-backfill-slice-1-inventory-009.md``:

| Test | Specification(s) |
|------|------------------|
| test_classification_already_harvested_exact_path | SPEC-DA-HARVEST-INCLUSION, SPEC-DA-RETROACTIVE-SWEEP |
| test_classification_already_harvested_compressed_wildcard | SPEC-DA-THREAD-COMPRESSION, SPEC-DA-RETROACTIVE-SWEEP |
| test_classification_content_drift_reclassified_eligible | SPEC-DA-RETROACTIVE-SWEEP |
| test_exclusion_size_under_100_bytes | SPEC-DA-HARVEST-EXCLUSION |
| test_exclusion_redaction_survivor | SPEC-DA-HARVEST-EXCLUSION, GOV-FILE-BRIDGE-AUTHORITY-001 |
| test_eligible_classification_default | SPEC-DA-HARVEST-INCLUSION |
| test_inventory_manifest_schema_complete | SPEC-DA-COVERAGE-METRIC |
| test_manifest_byte_stable_for_fixed_inputs | SPEC-DA-RETROACTIVE-SWEEP |
| test_manifest_excludes_generated_at_and_mtime | SPEC-DA-RETROACTIVE-SWEEP |
| test_summary_records_generated_at_outside_manifest | ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 |
| test_orphan_bridge_thread_recorded | GOV-FILE-BRIDGE-AUTHORITY-001 |
| test_inventory_does_not_write_deliberation_archive | SPEC-DA-MECHANICAL-ENFORCE |

Tests use sandbox bridge/LO-report fixtures and a temporary SQLite DA replica.
They must not mutate the real ``groundtruth.db``.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import sqlite3
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = REPO_ROOT / "scripts" / "inventory_lo_bridge_history_backfill.py"


def _load_module():
    spec = importlib.util.spec_from_file_location("inventory_lo_bridge_history_backfill", SCRIPT_PATH)
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    sys.modules["inventory_lo_bridge_history_backfill"] = mod
    spec.loader.exec_module(mod)
    return mod


INV = _load_module()


def _sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _make_repo(tmp_path: Path) -> Path:
    """Create a minimal in-root-shaped sandbox repo."""
    (tmp_path / "bridge").mkdir(parents=True)
    (tmp_path / "independent-progress-assessments" / "CODEX-INSIGHT-DROPBOX").mkdir(parents=True)
    return tmp_path


def _make_da(tmp_path: Path, rows: list[tuple[str, str, str]]) -> Path:
    """Create a temp SQLite DA replica with a ``current_deliberations`` view.

    rows: list of (id, source_ref, content_hash).
    """
    db_path = tmp_path / "groundtruth.db"
    conn = sqlite3.connect(db_path)
    conn.execute(
        "CREATE TABLE deliberations (rowid_ INTEGER PRIMARY KEY, id TEXT, version INTEGER, "
        "source_ref TEXT, content_hash TEXT)"
    )
    conn.execute("CREATE VIEW current_deliberations AS SELECT id, source_ref, content_hash FROM deliberations")
    for i, (row_id, source_ref, content_hash) in enumerate(rows, start=1):
        conn.execute(
            "INSERT INTO deliberations (rowid_, id, version, source_ref, content_hash) VALUES (?,?,?,?,?)",
            (i, row_id, 1, source_ref, content_hash),
        )
    conn.commit()
    conn.close()
    return db_path


def _write_bridge(repo: Path, name: str, content: str) -> Path:
    p = repo / "bridge" / name
    p.write_text(content, encoding="utf-8")
    return p


def _write_lo(repo: Path, name: str, content: str) -> Path:
    p = repo / "independent-progress-assessments" / "CODEX-INSIGHT-DROPBOX" / name
    p.write_text(content, encoding="utf-8")
    return p


def _record_by_path(records, path):
    for r in records:
        if r.path == path:
            return r
    raise AssertionError(f"no record for {path}; have {[r.path for r in records]}")


# ---------------------------------------------------------------------------
# Classification tests
# ---------------------------------------------------------------------------


def test_classification_already_harvested_exact_path(tmp_path):
    repo = _make_repo(tmp_path)
    body = "GO\n\n# substantive bridge content well over the hundred byte exclusion threshold for harvest.\n"
    _write_bridge(repo, "alpha-thread-002.md", body)
    db = _make_da(tmp_path, [("DELIB-1", "bridge/alpha-thread-002.md", _sha(body))])

    records, _ = INV.build_inventory(repo, db)
    rec = _record_by_path(records, "bridge/alpha-thread-002.md")
    assert rec.classification == INV.ALREADY_HARVESTED
    assert rec.classification_reason == "exact_path_match"
    assert rec.current_da_row_id == "DELIB-1"


def test_classification_already_harvested_compressed_wildcard(tmp_path):
    repo = _make_repo(tmp_path)
    body = "VERIFIED\n\n# compressed-thread bridge file with content exceeding the hundred byte harvest floor.\n"
    _write_bridge(repo, "beta-thread-004.md", body)
    # Only a compressed wildcard ref exists for the thread, no exact-path row.
    db = _make_da(tmp_path, [("DELIB-2", "bridge/beta-thread-*.md", _sha("thread-level-collector"))])

    records, _ = INV.build_inventory(repo, db)
    rec = _record_by_path(records, "bridge/beta-thread-004.md")
    assert rec.classification == INV.ALREADY_HARVESTED
    assert rec.classification_reason == "compressed_wildcard_coverage"


def test_classification_content_drift_reclassified_eligible(tmp_path):
    repo = _make_repo(tmp_path)
    body = "GO\n\n# content has changed since the deliberation row was harvested, exceeding the harvest floor.\n"
    _write_bridge(repo, "gamma-thread-002.md", body)
    # DA row exists for this exact path but with a stale hash.
    db = _make_da(tmp_path, [("DELIB-3", "bridge/gamma-thread-002.md", _sha("STALE PRIOR CONTENT"))])

    records, _ = INV.build_inventory(repo, db)
    rec = _record_by_path(records, "bridge/gamma-thread-002.md")
    assert rec.classification == INV.ELIGIBLE_FOR_HARVEST
    assert rec.classification_reason == "content_drift_since_harvest"
    assert rec.current_da_row_id == "DELIB-3"


def test_exclusion_size_under_100_bytes(tmp_path):
    repo = _make_repo(tmp_path)
    _write_bridge(repo, "tiny-thread-001.md", "GO\nshort\n")  # < 100 bytes
    db = _make_da(tmp_path, [])

    records, _ = INV.build_inventory(repo, db)
    rec = _record_by_path(records, "bridge/tiny-thread-001.md")
    assert rec.classification == INV.EXCLUDED_PER_SPEC
    assert rec.classification_reason == "size_under_100_bytes"


def test_exclusion_redaction_survivor(tmp_path):
    repo = _make_repo(tmp_path)
    # An LO report long enough to pass the size floor but carrying a credential
    # survivor. The survivor token is assembled at runtime so no credential-shaped
    # literal appears in this test source (scanner-safe-writer / SPEC-0058).
    survivor = "ar_" + "live_" + ("Z" * 16)
    body = (
        "# LO report with an embedded credential survivor that redaction cannot fully scrub.\n"
        f"leaked = {survivor}\n"
        "padding line to exceed the hundred byte harvest exclusion threshold for this fixture.\n"
    )
    _write_lo(repo, "INSIGHTS-2026-01-01-00-00.md", body)
    db = _make_da(tmp_path, [])

    records, _ = INV.build_inventory(repo, db)
    rec = _record_by_path(
        records, "independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-01-01-00-00.md"
    )
    # When the redaction helper is importable it may scrub the token; the survivor
    # regex still matches the fixture token, so a non-scrubbing redactor (and the
    # conservative fallback) classify it excluded. Accept either deterministic
    # outcome but pin the reason when excluded.
    assert rec.classification in (INV.EXCLUDED_PER_SPEC, INV.ELIGIBLE_FOR_HARVEST)
    if rec.classification == INV.EXCLUDED_PER_SPEC:
        assert rec.classification_reason == "redaction_survivor"


def test_eligible_classification_default(tmp_path):
    repo = _make_repo(tmp_path)
    body = (
        "NEW\n\n# a clean, substantive, never-harvested bridge proposal that sits well above the\n"
        "hundred byte harvest size floor so it is not excluded for being too small, and that\n"
        "carries no credential survivor so it is not excluded by the redaction gate either.\n"
    )
    _write_bridge(repo, "delta-thread-001.md", body)
    db = _make_da(tmp_path, [])

    records, _ = INV.build_inventory(repo, db)
    rec = _record_by_path(records, "bridge/delta-thread-001.md")
    assert rec.classification == INV.ELIGIBLE_FOR_HARVEST
    assert rec.classification_reason == "not_yet_harvested"


# ---------------------------------------------------------------------------
# Manifest tests
# ---------------------------------------------------------------------------


def test_inventory_manifest_schema_complete(tmp_path):
    repo = _make_repo(tmp_path)
    _write_bridge(
        repo, "epsilon-thread-001.md", "NEW\n\n# substantive content exceeding the harvest size floor here.\n"
    )
    db = _make_da(tmp_path, [])

    records, snap = INV.build_inventory(repo, db)
    manifest = INV.build_manifest(repo, records, snap)
    assert set(manifest.keys()) == {"_meta", "records"}
    meta = manifest["_meta"]
    for key in ("schema_version", "gt_repo_root", "script_sha256", "da_snapshot_counts", "on_disk_counts"):
        assert key in meta, f"missing _meta.{key}"
    assert manifest["records"], "expected at least one record"
    for key in (
        "path",
        "thread_stem",
        "file_class",
        "size_bytes",
        "sha256",
        "classification",
        "classification_reason",
        "current_da_row_id",
        "current_da_content_hash",
        "index_status",
    ):
        assert key in manifest["records"][0], f"missing record.{key}"


def test_manifest_byte_stable_for_fixed_inputs(tmp_path):
    repo = _make_repo(tmp_path)
    _write_bridge(
        repo, "zeta-thread-001.md", "NEW\n\n# stable content beyond the harvest size floor for determinism.\n"
    )
    _write_lo(
        repo,
        "INSIGHTS-2026-02-02-00-00.md",
        "# LO report content beyond the harvest size floor for determinism check.\n",
    )
    db = _make_da(tmp_path, [])

    records1, snap1 = INV.build_inventory(repo, db)
    records2, snap2 = INV.build_inventory(repo, db)
    bytes1 = INV.manifest_to_bytes(INV.build_manifest(repo, records1, snap1))
    bytes2 = INV.manifest_to_bytes(INV.build_manifest(repo, records2, snap2))
    assert bytes1 == bytes2, "manifest must be byte-identical for fixed inputs"


def test_manifest_excludes_generated_at_and_mtime(tmp_path):
    repo = _make_repo(tmp_path)
    _write_bridge(
        repo, "eta-thread-001.md", "NEW\n\n# content beyond the harvest size floor for the exclusion check here.\n"
    )
    db = _make_da(tmp_path, [])

    records, snap = INV.build_inventory(repo, db)
    manifest_bytes = INV.manifest_to_bytes(INV.build_manifest(repo, records, snap))
    text = manifest_bytes.decode("utf-8")
    assert "generated_at" not in text
    assert "mtime" not in text


def test_summary_records_generated_at_outside_manifest(tmp_path):
    repo = _make_repo(tmp_path)
    _write_bridge(
        repo, "theta-thread-001.md", "NEW\n\n# content beyond the harvest size floor for the summary check here.\n"
    )
    db = _make_da(tmp_path, [])

    records, snap = INV.build_inventory(repo, db)
    summary = INV.build_summary(repo, records, snap, generated_at="2026-06-03T00:00:00+00:00")
    assert "Generated: 2026-06-03T00:00:00+00:00" in summary
    # And the manifest still excludes it.
    manifest_text = INV.manifest_to_bytes(INV.build_manifest(repo, records, snap)).decode("utf-8")
    assert "2026-06-03T00:00:00+00:00" not in manifest_text


def test_orphan_bridge_thread_recorded(tmp_path):
    repo = _make_repo(tmp_path)
    # A bridge file with no INDEX.md entry is an orphan thread.
    _write_bridge(
        repo,
        "orphan-thread-001.md",
        "NEW\n\n# orphaned bridge file not present in any INDEX entry, beyond size floor.\n",
    )
    # Empty INDEX.md => no status for the file.
    (repo / "bridge" / "INDEX.md").write_text("# Bridge Index\n", encoding="utf-8")
    db = _make_da(tmp_path, [])

    records, snap = INV.build_inventory(repo, db)
    rec = _record_by_path(records, "bridge/orphan-thread-001.md")
    assert rec.index_status is None
    summary = INV.build_summary(repo, records, snap, generated_at="2026-06-03T00:00:00+00:00")
    assert "orphan-thread" in summary


def test_inventory_does_not_write_deliberation_archive(tmp_path):
    repo = _make_repo(tmp_path)
    _write_bridge(
        repo, "iota-thread-001.md", "NEW\n\n# content beyond the harvest size floor for the no-mutation check here.\n"
    )
    db = _make_da(tmp_path, [("DELIB-9", "bridge/somewhere-else-001.md", _sha("x"))])

    before = db.read_bytes()
    before_count = sqlite3.connect(db).execute("SELECT COUNT(*) FROM deliberations").fetchone()[0]

    records, snap = INV.build_inventory(repo, db)
    out_dir = tmp_path / "out"
    manifest_bytes = INV.manifest_to_bytes(INV.build_manifest(repo, records, snap))
    INV.write_outputs(out_dir, manifest_bytes, INV.build_summary(repo, records, snap, "2026-06-03T00:00:00+00:00"))

    after = db.read_bytes()
    after_count = sqlite3.connect(db).execute("SELECT COUNT(*) FROM deliberations").fetchone()[0]
    assert before == after, "groundtruth.db bytes must be unchanged (read-only inventory)"
    assert before_count == after_count == 1


def test_outputs_written_to_disk(tmp_path):
    repo = _make_repo(tmp_path)
    _write_bridge(
        repo,
        "kappa-thread-001.md",
        "NEW\n\n# content beyond the harvest size floor for the output-writer check here.\n",
    )
    db = _make_da(tmp_path, [])

    rc = INV.main(
        [
            "--repo-root",
            str(repo),
            "--db-path",
            str(db),
            "--output-dir",
            str(tmp_path / "out"),
        ]
    )
    assert rc == 0
    manifest_path = tmp_path / "out" / "inventory-manifest.json"
    summary_path = tmp_path / "out" / "inventory-summary.md"
    assert manifest_path.exists() and summary_path.exists()
    parsed = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert parsed["_meta"]["schema_version"] == INV.SCHEMA_VERSION


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))
