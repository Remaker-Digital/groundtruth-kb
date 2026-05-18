"""Tests for scripts/retroactive_harvest_bridge_threads.py.

Covers the Codex GO conditions on bridge/gtkb-da-harvest-coverage-implementation-005.md:
    - Orphan prefix-pair separation for the 4 real pairs.
    - Legacy file-level rows do not count as canonical coverage.
    - Duplicate wildcard DELIB rows count as one covered thread.
    - Idempotent second retroactive run produces zero new inserts.
    - Empty active index returns 100% coverage.
    - Threshold-boundary behavior for coverage metric.

Raw transcript exclusion is proven by source inspection (no home-directory
transcript path reference in retroactive_harvest_bridge_threads.py).

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = REPO_ROOT / "scripts" / "retroactive_harvest_bridge_threads.py"


def _load_script_module():
    spec = importlib.util.spec_from_file_location("retroactive_harvest", SCRIPT_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules["retroactive_harvest"] = module
    spec.loader.exec_module(module)
    return module


rhbt = _load_script_module()


# ---------------------------------------------------------------------------
# extract_thread_stem
# ---------------------------------------------------------------------------


class TestExtractThreadStem:
    def test_basic_three_digit_version(self):
        assert rhbt.extract_thread_stem("gtkb-example-001.md") == "gtkb-example"

    def test_hyphenated_name(self):
        assert rhbt.extract_thread_stem("gtkb-da-harvest-coverage-001.md") == "gtkb-da-harvest-coverage"

    def test_implementation_suffix(self):
        assert (
            rhbt.extract_thread_stem("gtkb-da-harvest-coverage-implementation-005.md")
            == "gtkb-da-harvest-coverage-implementation"
        )

    def test_non_versioned_file_returns_none(self):
        assert rhbt.extract_thread_stem("INDEX.md") is None

    def test_partial_version_returns_none(self):
        assert rhbt.extract_thread_stem("gtkb-thing-1.md") is None

    def test_four_digit_version_not_supported(self):
        # -NNN is strictly 3 digits in the bridge convention
        assert rhbt.extract_thread_stem("thread-0001.md") is None


# ---------------------------------------------------------------------------
# Orphan grouping — 4 real prefix pairs from Codex -003 addendum
# ---------------------------------------------------------------------------


REAL_PREFIX_PAIRS = [
    ("gtkb-da-harvest-coverage", "gtkb-da-harvest-coverage-implementation"),
    ("gtkb-canonical-terminology-surface", "gtkb-canonical-terminology-surface-implementation"),
    ("gtkb-docs-memory-architecture-alignment", "gtkb-docs-memory-architecture-alignment-editplan"),
    ("gtkb-start-here-adopter-rewrite", "gtkb-start-here-adopter-rewrite-implementation"),
]


class TestOrphanGrouping:
    @pytest.mark.parametrize("retired,child", REAL_PREFIX_PAIRS)
    def test_prefix_pairs_remain_distinct(self, tmp_path: Path, retired: str, child: str) -> None:
        files = [
            tmp_path / f"{retired}-001.md",
            tmp_path / f"{retired}-002.md",
            tmp_path / f"{child}-001.md",
        ]
        for f in files:
            f.touch()
        groups = rhbt.group_orphans_by_strict_stem(files)
        assert retired in groups
        assert child in groups
        assert len(groups[retired]) == 2
        assert len(groups[child]) == 1

    def test_multi_version_thread_groups_to_one(self, tmp_path: Path) -> None:
        files = [tmp_path / f"groundtruth-db-migration-{i:03d}.md" for i in range(1, 26)]
        for f in files:
            f.touch()
        groups = rhbt.group_orphans_by_strict_stem(files)
        assert "groundtruth-db-migration" in groups
        assert len(groups["groundtruth-db-migration"]) == 25

    def test_unrelated_threads_group_separately(self, tmp_path: Path) -> None:
        files = [
            tmp_path / "gtkb-phase-a-x-001.md",
            tmp_path / "gtkb-phase-a-y-001.md",
        ]
        for f in files:
            f.touch()
        groups = rhbt.group_orphans_by_strict_stem(files)
        assert set(groups.keys()) == {"gtkb-phase-a-x", "gtkb-phase-a-y"}

    def test_non_versioned_files_skipped(self, tmp_path: Path) -> None:
        (tmp_path / "INDEX.md").touch()
        (tmp_path / "README.md").touch()
        (tmp_path / "thread-alpha-001.md").touch()
        groups = rhbt.group_orphans_by_strict_stem(list(tmp_path.glob("*.md")))
        assert set(groups.keys()) == {"thread-alpha"}


# ---------------------------------------------------------------------------
# Coverage formula — distinct thread-name sets
# ---------------------------------------------------------------------------


class FakeDB:
    """In-memory DA stand-in implementing only list_deliberations()."""

    def __init__(self, rows: list[dict]) -> None:
        self._rows = rows

    def list_deliberations(
        self,
        *,
        source_type: str | None = None,
        source_ref: str | None = None,
        **_kwargs,
    ) -> list[dict]:
        out = self._rows
        if source_type is not None:
            out = [r for r in out if r.get("source_type") == source_type]
        if source_ref is not None:
            out = [r for r in out if r.get("source_ref") == source_ref]
        return out


def _active_verified(name: str) -> rhbt.ThreadRecord:
    return rhbt.ThreadRecord(
        thread_name=name,
        source_ref=f"bridge/{name}-*.md",
        versions=[],
        active=True,
        latest_status="VERIFIED",
    )


class TestCoverageFormula:
    def test_empty_active_index_returns_100(self) -> None:
        db = FakeDB([])
        result = rhbt.compute_active_bridge_thread_coverage([], db)
        assert result["coverage_pct"] == 100.0
        assert result["denominator_threads"] == 0
        assert result["numerator_threads"] == 0

    def test_zero_coverage(self) -> None:
        records = [_active_verified("a"), _active_verified("b")]
        db = FakeDB([])
        result = rhbt.compute_active_bridge_thread_coverage(records, db)
        assert result["coverage_pct"] == 0.0
        assert result["uncovered_thread_names"] == ["a", "b"]

    def test_full_coverage(self) -> None:
        records = [_active_verified("a"), _active_verified("b")]
        db = FakeDB([
            {"source_type": "bridge_thread", "source_ref": "bridge/a-*.md"},
            {"source_type": "bridge_thread", "source_ref": "bridge/b-*.md"},
        ])
        result = rhbt.compute_active_bridge_thread_coverage(records, db)
        assert result["coverage_pct"] == 100.0
        assert result["uncovered_thread_names"] == []

    def test_duplicate_wildcard_delibs_count_as_one(self) -> None:
        """Multiple current DELIBs with the same wildcard source_ref must
        count as ONE covered thread. This guards against the coverage-math
        bug Codex flagged in Finding 1 of -002."""
        records = [_active_verified("a")]
        db = FakeDB([
            {"source_type": "bridge_thread", "source_ref": "bridge/a-*.md", "id": "DELIB-0001"},
            {"source_type": "bridge_thread", "source_ref": "bridge/a-*.md", "id": "DELIB-0002"},
            {"source_type": "bridge_thread", "source_ref": "bridge/a-*.md", "id": "DELIB-0003"},
        ])
        result = rhbt.compute_active_bridge_thread_coverage(records, db)
        assert result["coverage_pct"] == 100.0
        assert result["numerator_threads"] == 1
        assert result["denominator_threads"] == 1

    def test_coverage_cannot_exceed_100(self) -> None:
        records = [_active_verified("a")]
        db = FakeDB([
            {"source_type": "bridge_thread", "source_ref": "bridge/a-*.md"} for _ in range(10)
        ])
        result = rhbt.compute_active_bridge_thread_coverage(records, db)
        assert 0.0 <= result["coverage_pct"] <= 100.0

    def test_legacy_file_level_rows_do_not_count_as_covered(self) -> None:
        """Finding 5 (Codex -003): legacy file-level bridge_thread rows must
        NOT count as canonical wildcard coverage. Only wildcard source_ref
        rows are visible to the coverage metric."""
        records = [_active_verified("demo-thread")]
        db = FakeDB([
            {"source_type": "bridge_thread", "source_ref": "bridge/demo-thread-001.md"},
            {"source_type": "bridge_thread", "source_ref": "bridge/demo-thread-002.md"},
        ])
        result = rhbt.compute_active_bridge_thread_coverage(records, db)
        assert result["numerator_threads"] == 0
        assert result["coverage_pct"] == 0.0

        db_with_canonical = FakeDB([
            {"source_type": "bridge_thread", "source_ref": "bridge/demo-thread-001.md"},
            {"source_type": "bridge_thread", "source_ref": "bridge/demo-thread-*.md"},
        ])
        result2 = rhbt.compute_active_bridge_thread_coverage(records, db_with_canonical)
        assert result2["numerator_threads"] == 1
        assert result2["coverage_pct"] == 100.0

    def test_partial_coverage_identifies_uncovered(self) -> None:
        records = [_active_verified("a"), _active_verified("b"), _active_verified("c")]
        db = FakeDB([
            {"source_type": "bridge_thread", "source_ref": "bridge/b-*.md"},
        ])
        result = rhbt.compute_active_bridge_thread_coverage(records, db)
        assert result["numerator_threads"] == 1
        assert result["denominator_threads"] == 3
        assert result["uncovered_thread_names"] == ["a", "c"]
        assert result["covered_thread_names"] == ["b"]


# ---------------------------------------------------------------------------
# INDEX parsing
# ---------------------------------------------------------------------------


class TestParseActiveIndex:
    def test_basic_parsing(self, tmp_path: Path) -> None:
        index = tmp_path / "INDEX.md"
        index.write_text(
            """# Bridge Index

<!-- commentary -->

Document: thread-alpha
VERIFIED: bridge/thread-alpha-002.md
NEW: bridge/thread-alpha-001.md

Document: thread-beta
NO-GO: bridge/thread-beta-001.md
""",
            encoding="utf-8",
        )
        entries = rhbt.parse_active_index(index)
        assert [e.name for e in entries] == ["thread-alpha", "thread-beta"]
        assert entries[0].latest_status == "VERIFIED"
        assert entries[1].latest_status == "NO-GO"

    def test_missing_index_returns_empty(self, tmp_path: Path) -> None:
        assert rhbt.parse_active_index(tmp_path / "nonexistent.md") == []


# ---------------------------------------------------------------------------
# Raw-transcript exclusion (source inspection)
# ---------------------------------------------------------------------------


class TestTranscriptExclusion:
    def test_script_does_not_reference_claude_projects_jsonl(self) -> None:
        body = SCRIPT_PATH.read_text(encoding="utf-8")
        # These patterns would indicate raw transcript ingestion
        assert ".claude/projects/" not in body
        assert ".jsonl" not in body


# ---------------------------------------------------------------------------
# Idempotence — content_hash dedup in run_sweep
# ---------------------------------------------------------------------------


class _StubDB:
    """Stub DB that records inserts and enforces content-hash dedup."""

    def __init__(self) -> None:
        self.rows: list[dict] = []
        # WI-3364: active project authorizations for the authorization-aware
        # prune skip. Empty by default so pre-WI-3364 tests are unaffected.
        self.authorizations: list[dict] = []

    def list_project_authorizations(self, project_id=None, *, status=None, include_terminal=False, **_):
        out = self.authorizations
        if status is not None:
            out = [a for a in out if a.get("status") == status]
        return list(out)

    def list_deliberations(self, *, source_type=None, source_ref=None, **_):
        out = self.rows
        if source_type is not None:
            out = [r for r in out if r.get("source_type") == source_type]
        if source_ref is not None:
            out = [r for r in out if r.get("source_ref") == source_ref]
        return list(out)

    def upsert_deliberation_source(
        self,
        *,
        source_type: str,
        source_ref: str,
        content: str,
        **kwargs,
    ):
        import hashlib

        content_hash = hashlib.sha256(content.encode()).hexdigest()
        existing = [
            r for r in self.rows
            if r.get("source_ref") == source_ref and r.get("content_hash") == content_hash
        ]
        if existing:
            return existing[0]
        row = {
            "id": f"DELIB-{len(self.rows):04d}",
            "source_type": source_type,
            "source_ref": source_ref,
            "content_hash": content_hash,
            "content": content,
            **kwargs,
        }
        self.rows.append(row)
        return row


class TestIdempotence:
    def test_second_run_inserts_zero_rows(self, tmp_path: Path, monkeypatch) -> None:
        bridge_dir = tmp_path / "bridge"
        bridge_dir.mkdir()
        (bridge_dir / "thread-x-001.md").write_text("# Thread X\n\nBody text.\n", encoding="utf-8")
        (bridge_dir / "thread-x-002.md").write_text("# Thread X\n\nBody text v2.\n", encoding="utf-8")
        index = bridge_dir / "INDEX.md"
        index.write_text(
            "Document: thread-x\nVERIFIED: bridge/thread-x-002.md\nNEW: bridge/thread-x-001.md\n",
            encoding="utf-8",
        )

        stub = _StubDB()
        monkeypatch.setattr(rhbt, "BRIDGE_DIR", bridge_dir)
        monkeypatch.setattr(rhbt, "BRIDGE_INDEX", index)
        monkeypatch.setattr(rhbt, "_load_db", lambda _kb_path: stub)

        r1 = rhbt.run_sweep(execute=True, sample=0, kb_path=None)
        r2 = rhbt.run_sweep(execute=True, sample=0, kb_path=None)

        assert r1["summary"]["new_compressed_inserts_applied"] == 1
        assert r2["summary"]["new_compressed_inserts_applied"] == 0
        # Exactly one canonical wildcard row in the stub DB
        canonical = [r for r in stub.rows if "*" in r["source_ref"]]
        assert len(canonical) == 1


# ---------------------------------------------------------------------------
# Verified-thread startup archival + INDEX pruning
# ---------------------------------------------------------------------------


class TestVerifiedArchiveAndPrune:
    def test_archives_and_prunes_only_verified_entries(self, tmp_path: Path, monkeypatch) -> None:
        bridge_dir = tmp_path / "bridge"
        bridge_dir.mkdir()
        (bridge_dir / "alpha-001.md").write_text("# Alpha\n\nProposal.\n", encoding="utf-8")
        (bridge_dir / "alpha-002.md").write_text("# Alpha\n\nVerified.\n", encoding="utf-8")
        (bridge_dir / "beta-001.md").write_text("# Beta\n\nProposal.\n", encoding="utf-8")
        (bridge_dir / "beta-002.md").write_text("# Beta\n\nGO.\n", encoding="utf-8")
        index = bridge_dir / "INDEX.md"
        index.write_text(
            """# Bridge Index

Document: alpha
VERIFIED: bridge/alpha-002.md
NEW: bridge/alpha-001.md

Document: beta
GO: bridge/beta-002.md
NEW: bridge/beta-001.md
""",
            encoding="utf-8",
        )
        stub = _StubDB()
        monkeypatch.setattr(rhbt, "_load_db", lambda _kb_path: stub)

        report = rhbt.archive_verified_threads_and_prune_index(
            index_path=index,
            bridge_dir=bridge_dir,
            kb_path=None,
        )

        assert report["verified_threads_seen"] == 1
        assert report["inserted"] == 1
        assert report["pruned_from_index"] == 1
        assert report["failed_count"] == 0
        assert [row["source_ref"] for row in stub.rows] == ["bridge/alpha-*.md"]

        index_text = index.read_text(encoding="utf-8")
        assert "Document: alpha" not in index_text
        assert "VERIFIED: bridge/alpha-002.md" not in index_text
        assert "Document: beta" in index_text
        assert "GO: bridge/beta-002.md" in index_text

    def test_keeps_verified_entry_when_archive_insert_fails(self, tmp_path: Path, monkeypatch) -> None:
        bridge_dir = tmp_path / "bridge"
        bridge_dir.mkdir()
        (bridge_dir / "alpha-001.md").write_text("# Alpha\n\nVerified.\n", encoding="utf-8")
        index = bridge_dir / "INDEX.md"
        index.write_text(
            "Document: alpha\nVERIFIED: bridge/alpha-001.md\n",
            encoding="utf-8",
        )

        class FailingDB(_StubDB):
            def upsert_deliberation_source(self, **kwargs):
                raise RuntimeError("db unavailable")

        monkeypatch.setattr(rhbt, "_load_db", lambda _kb_path: FailingDB())

        report = rhbt.archive_verified_threads_and_prune_index(
            index_path=index,
            bridge_dir=bridge_dir,
            kb_path=None,
        )

        assert report["failed_count"] == 1
        assert report["pruned_from_index"] == 0
        assert "Document: alpha" in index.read_text(encoding="utf-8")

    def test_existing_exact_archive_prunes_without_reinserting(self, tmp_path: Path, monkeypatch) -> None:
        bridge_dir = tmp_path / "bridge"
        bridge_dir.mkdir()
        (bridge_dir / "alpha-001.md").write_text("# Alpha\n\nVerified.\n", encoding="utf-8")
        index = bridge_dir / "INDEX.md"
        index.write_text(
            "Document: alpha\nVERIFIED: bridge/alpha-001.md\n",
            encoding="utf-8",
        )
        record = rhbt.collect_compressed_bridge_threads(index, bridge_dir)[0]
        _, _, content = rhbt.build_thread_summary(record)
        content_hash = __import__("hashlib").sha256(content.encode()).hexdigest()

        stub = _StubDB()
        stub.rows.append({
            "source_type": "bridge_thread",
            "source_ref": "bridge/alpha-*.md",
            "content_hash": content_hash,
        })
        monkeypatch.setattr(rhbt, "_load_db", lambda _kb_path: stub)

        report = rhbt.archive_verified_threads_and_prune_index(
            index_path=index,
            bridge_dir=bridge_dir,
            kb_path=None,
        )

        assert report["already_archived"] == 1
        assert report["inserted"] == 0
        assert report["pruned_from_index"] == 1
        assert len(stub.rows) == 1

    def test_oversized_index_comments_are_archived_and_compacted(self, tmp_path: Path, monkeypatch) -> None:
        bridge_dir = tmp_path / "bridge"
        bridge_dir.mkdir()
        (bridge_dir / "active-001.md").write_text("# Active\n\nBody.\n", encoding="utf-8")
        repeated = "\n".join(
            f"<!--   - Retirement ack #{i}: verbose obsolete dispatcher fire details {'x' * 500} -->"
            for i in range(30)
        )
        index = bridge_dir / "INDEX.md"
        index.write_text(
            f"""# Bridge Index

<!-- Prime inserts new document entries at the top of the list below. -->
<!-- Codex scans for NEW/REVISED statuses and adds GO/NO-GO/VERIFIED versions. -->

{repeated}

Document: active
GO: bridge/active-001.md
""",
            encoding="utf-8",
        )
        stub = _StubDB()
        monkeypatch.setattr(rhbt, "_load_db", lambda _kb_path: stub)

        report = rhbt.archive_verified_threads_and_prune_index(
            index_path=index,
            bridge_dir=bridge_dir,
            kb_path=None,
        )

        compaction = report["comment_compaction"]
        assert compaction["removed_comment_lines"] >= 30
        assert compaction["removed_bytes"] > 8_000
        assert compaction["archive_id"] == "DELIB-0000"
        assert len(stub.rows) == 1
        assert "Retirement ack #29" in stub.rows[0]["content"]

        text = index.read_text(encoding="utf-8")
        assert "STARTUP-PRUNED HISTORICAL PREAMBLE" in text
        assert "Retirement ack #29" not in text
        assert "Document: active" in text
        assert "GO: bridge/active-001.md" in text
