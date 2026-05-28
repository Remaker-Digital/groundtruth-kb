"""Tests for the codex-backlog-cleanup inventory + review-packet generators.

Bridge governance: ``bridge/gtkb-codex-backlog-cleanup-retroactive-review-003.md``
(GO at ``-004``). Phase-1 scope is read-only inventory plus a review packet; no
KB mutation is permitted, no operating-model edit is permitted, and the Path
A/Path B owner decision is explicitly deferred.

Linked specifications under verification:
- ``GOV-STANDING-BACKLOG-001`` — inventory file exists; lists all 119 WI changes.
- ``PB-STANDING-BACKLOG-CONTINUITY-001`` — review packet makes the bulk
  operation visible.
- ``ADR-ISOLATION-APPLICATION-PLACEMENT-001`` — all artifacts are under
  ``E:\\GT-KB``; the static path test asserts in-root output.
- Read-only discipline — DB file mtime + sha256 unchanged across both runs.
- Phase-1 scope — review packet contains the
  ``DECISION DEFERRED TO PHASE 2`` marker.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import hashlib
import importlib.util
import sqlite3
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
DB_PATH = REPO_ROOT / "groundtruth.db"
INVENTORY_SCRIPT = REPO_ROOT / "scripts" / "generate_codex_backlog_cleanup_inventory.py"
REVIEW_SCRIPT = REPO_ROOT / "scripts" / "generate_codex_backlog_cleanup_review_packet.py"
DEFAULT_DROPBOX = REPO_ROOT / "independent-progress-assessments" / "CODEX-INSIGHT-DROPBOX"
EXPECTED_ROW_COUNT = 119


def _load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def inventory_module():
    return _load_module(INVENTORY_SCRIPT, "generate_codex_backlog_cleanup_inventory")


@pytest.fixture(scope="module")
def review_module():
    return _load_module(REVIEW_SCRIPT, "generate_codex_backlog_cleanup_review_packet")


@pytest.fixture(scope="module")
def db_available():
    if not DB_PATH.exists():
        pytest.skip(f"groundtruth.db not present at {DB_PATH}; skipping integration test.")
    return DB_PATH


def _file_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _distinct_wi_ids(db_path: Path) -> set[str]:
    conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    try:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT DISTINCT id FROM work_items
            WHERE changed_by = 'codex-backlog-cleanup'
              AND changed_at >= '2026-05-06T18:06:00Z'
              AND changed_at <  '2026-05-06T18:10:00Z'
            """
        )
        return {row[0] for row in cur.fetchall()}
    finally:
        conn.close()


def test_inventory_in_root_output_path(inventory_module):
    """ADR-ISOLATION-APPLICATION-PLACEMENT-001: output path is under E:\\GT-KB."""
    out = inventory_module.DEFAULT_OUTPUT_PATH.resolve()
    assert out.is_relative_to(REPO_ROOT.resolve()), f"out path escapes project root: {out}"


def test_inventory_generator_produces_expected_row_count(inventory_module, db_available, tmp_path):
    """GOV-STANDING-BACKLOG-001 / row-count check: emit exactly 119 data rows."""
    out = tmp_path / "inventory.md"
    rc = inventory_module.main(["--db", str(db_available), "--out", str(out)])
    assert rc == 0
    assert out.exists()
    text = out.read_text(encoding="utf-8")
    data_lines = [
        line
        for line in text.splitlines()
        if line.startswith("| ")
        and not line.startswith("| # ")
        and not line.startswith("| ---")
        and not line.startswith("|---")
        and "WI ID" not in line
    ]
    assert len(data_lines) == EXPECTED_ROW_COUNT, f"expected {EXPECTED_ROW_COUNT} data rows; got {len(data_lines)}"


def test_inventory_covers_all_distinct_wi_ids(inventory_module, db_available, tmp_path):
    """Inventory generator covers every distinct WI id in the changed_by window."""
    out = tmp_path / "inventory.md"
    rc = inventory_module.main(["--db", str(db_available), "--out", str(out)])
    assert rc == 0
    text = out.read_text(encoding="utf-8")
    expected_ids = _distinct_wi_ids(db_available)
    assert len(expected_ids) == EXPECTED_ROW_COUNT
    for wi_id in expected_ids:
        assert f"`{wi_id}`" in text, f"missing WI id in inventory output: {wi_id}"


def test_review_packet_aggregates_transition_types(inventory_module, review_module, db_available, tmp_path):
    """Review packet aggregates by transition type without errors."""
    inv = tmp_path / "inventory.md"
    pkt = tmp_path / "packet.md"
    assert inventory_module.main(["--db", str(db_available), "--out", str(inv)]) == 0
    rc = review_module.main(["--db", str(db_available), "--inventory", str(inv), "--out", str(pkt)])
    assert rc == 0
    text = pkt.read_text(encoding="utf-8")
    assert "Counts By Transition Type" in text
    assert "->" in text, "transition arrow missing — aggregation likely empty"
    rows = [line for line in text.splitlines() if line.startswith("| `") and "->" in line]
    assert rows, "no transition rows rendered"


def test_review_packet_contains_phase_2_deferred_marker(inventory_module, review_module, db_available, tmp_path):
    """Phase-1 scope marker: review packet must contain DECISION DEFERRED TO PHASE 2."""
    inv = tmp_path / "inventory.md"
    pkt = tmp_path / "packet.md"
    assert inventory_module.main(["--db", str(db_available), "--out", str(inv)]) == 0
    assert review_module.main(["--db", str(db_available), "--inventory", str(inv), "--out", str(pkt)]) == 0
    assert review_module.DEFERRED_MARKER in pkt.read_text(encoding="utf-8")


def test_no_kb_write_during_generation(inventory_module, review_module, db_available, tmp_path):
    """Read-only discipline: DB file mtime + sha256 unchanged across both runs."""
    pre_mtime = db_available.stat().st_mtime_ns
    pre_hash = _file_sha256(db_available)
    inv = tmp_path / "inventory.md"
    pkt = tmp_path / "packet.md"
    assert inventory_module.main(["--db", str(db_available), "--out", str(inv)]) == 0
    assert review_module.main(["--db", str(db_available), "--inventory", str(inv), "--out", str(pkt)]) == 0
    post_mtime = db_available.stat().st_mtime_ns
    post_hash = _file_sha256(db_available)
    assert pre_mtime == post_mtime, "DB mtime changed — read-only contract violated"
    assert pre_hash == post_hash, "DB sha256 changed — read-only contract violated"
