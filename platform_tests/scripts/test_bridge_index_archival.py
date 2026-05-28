# (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Regression tests for WI-3364: event-driven bridge/INDEX.md archival trim.

Covers the GO'd scope of bridge/gtkb-bridge-index-archival-trim-007.md:

- IP-1: the ``exclude_threads`` guard on ``archive_verified_threads_and_prune_index``.
- IP-2: the authorization-aware skip (resolves the -004 F1 blocker) — covers
  active vs completed authorizations and archived vs unarchived protected
  threads, and ties the assertion to live ``verified_work_items()``.
- IP-3: GT-KB origin metadata on archive rows (resolves the -004 F2 blocker).
- IP-4: stale-snapshot conflict detection in ``_write_pruned_index`` and
  ``_compact_index_comments`` (resolves the -006 F1 blocker).
- IP-5: the ``maybe_archive_and_prune_index`` event-driven entry point.
- IP-6: the four bridge-write helper hookups (source inspection).
"""

from __future__ import annotations

import hashlib
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPTS_DIR = REPO_ROOT / "scripts"
GT_SRC = REPO_ROOT / "groundtruth-kb" / "src"
for _path in (str(SCRIPTS_DIR), str(GT_SRC)):
    if _path not in sys.path:
        sys.path.insert(0, _path)

import bridge_index_archival as bia  # noqa: E402
import retroactive_harvest_bridge_threads as rhbt  # noqa: E402

# ---------------------------------------------------------------------------
# Stub DB
# ---------------------------------------------------------------------------


class StubDB:
    """In-memory Deliberation Archive + project-authorization stand-in."""

    def __init__(self) -> None:
        self.rows: list[dict] = []
        self.authorizations: list[dict] = []

    def list_deliberations(self, *, source_type=None, source_ref=None, **_):
        out = list(self.rows)
        if source_type is not None:
            out = [r for r in out if r.get("source_type") == source_type]
        if source_ref is not None:
            out = [r for r in out if r.get("source_ref") == source_ref]
        return out

    def upsert_deliberation_source(self, *, source_type, source_ref, content, **kwargs):
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

    def list_project_authorizations(self, project_id=None, *, status=None, include_terminal=False, **_):
        out = list(self.authorizations)
        if status is not None:
            out = [a for a in out if a.get("status") == status]
        return out


# ---------------------------------------------------------------------------
# Fixture helpers
# ---------------------------------------------------------------------------


def _make_bridge(tmp_path: Path) -> Path:
    bridge_dir = tmp_path / "bridge"
    bridge_dir.mkdir()
    return bridge_dir


def _verified_thread(bridge_dir: Path, slug: str, *, work_item: str | None = None) -> str:
    """Write a single-version VERIFIED bridge thread; return its INDEX block."""
    wi_line = f"Work Item: {work_item}\n" if work_item else ""
    (bridge_dir / f"{slug}-001.md").write_text(
        f"VERIFIED\n\n# {slug}\n\n{wi_line}\nVerified body for {slug}.\n",
        encoding="utf-8",
    )
    return f"Document: {slug}\nVERIFIED: bridge/{slug}-001.md\n"


def _write_index(bridge_dir: Path, *blocks: str) -> Path:
    index = bridge_dir / "INDEX.md"
    index.write_text("# Bridge Index\n\n" + "\n".join(blocks) + "\n", encoding="utf-8")
    return index


class _RacingIndexPath:
    """Path-like wrapper that injects a concurrent bridge/INDEX.md write right
    before the Nth ``read_text`` call — simulating another harness inserting a
    status line between the archival writer's snapshot read and its pre-write
    re-read.
    """

    def __init__(self, real: Path, *, mutate_before_read: int, concurrent_text: str) -> None:
        self._real = real
        self._reads = 0
        self._mutate_before_read = mutate_before_read
        self._concurrent_text = concurrent_text

    def exists(self) -> bool:
        return self._real.exists()

    def is_file(self) -> bool:
        return self._real.is_file()

    def read_text(self, encoding: str = "utf-8", **kwargs):
        self._reads += 1
        if self._reads == self._mutate_before_read:
            self._real.write_text(self._concurrent_text, encoding=encoding)
        return self._real.read_text(encoding=encoding, **kwargs)

    def write_text(self, content, encoding: str = "utf-8", **kwargs):
        return self._real.write_text(content, encoding=encoding, **kwargs)


# ---------------------------------------------------------------------------
# IP-1: exclude_threads guard
# ---------------------------------------------------------------------------


class TestExcludeThreads:
    def test_excluded_thread_is_not_pruned(self, tmp_path: Path, monkeypatch) -> None:
        bridge_dir = _make_bridge(tmp_path)
        index = _write_index(
            bridge_dir,
            _verified_thread(bridge_dir, "alpha"),
            _verified_thread(bridge_dir, "beta"),
        )
        monkeypatch.setattr(rhbt, "_load_db", lambda _kb: StubDB())

        report = rhbt.archive_verified_threads_and_prune_index(
            index_path=index,
            bridge_dir=bridge_dir,
            kb_path=None,
            exclude_threads=frozenset({"alpha"}),
        )

        assert report["excluded_current_thread"] == ["alpha"]
        text = index.read_text(encoding="utf-8")
        assert "Document: alpha" in text          # excluded -> retained
        assert "Document: beta" not in text       # eligible -> pruned

    def test_default_excludes_nothing(self, tmp_path: Path, monkeypatch) -> None:
        bridge_dir = _make_bridge(tmp_path)
        index = _write_index(
            bridge_dir,
            _verified_thread(bridge_dir, "alpha"),
            _verified_thread(bridge_dir, "beta"),
        )
        monkeypatch.setattr(rhbt, "_load_db", lambda _kb: StubDB())

        report = rhbt.archive_verified_threads_and_prune_index(
            index_path=index, bridge_dir=bridge_dir, kb_path=None,
        )

        assert report["excluded_current_thread"] == []
        text = index.read_text(encoding="utf-8")
        assert "Document: alpha" not in text
        assert "Document: beta" not in text


# ---------------------------------------------------------------------------
# IP-2: authorization-aware skip (the -004 F1 blocker)
# ---------------------------------------------------------------------------


class TestAuthorizationAwareSkip:
    def _run(self, tmp_path, monkeypatch, *, authorizations, archived_protected=False):
        bridge_dir = _make_bridge(tmp_path)
        # gamma carries WI-9999 (the protected work item); delta is unrelated.
        index = _write_index(
            bridge_dir,
            _verified_thread(bridge_dir, "gamma", work_item="WI-9999"),
            _verified_thread(bridge_dir, "delta", work_item="WI-1"),
        )
        stub = StubDB()
        stub.authorizations = authorizations
        if archived_protected:
            records = rhbt.collect_compressed_bridge_threads(index, bridge_dir)
            gamma_rec = next(r for r in records if r.thread_name == "gamma")
            _, _, content = rhbt.build_thread_summary(gamma_rec)
            stub.rows.append({
                "source_type": "bridge_thread",
                "source_ref": gamma_rec.source_ref,
                "content_hash": hashlib.sha256(content.encode()).hexdigest(),
            })
        monkeypatch.setattr(rhbt, "_load_db", lambda _kb: stub)
        report = rhbt.archive_verified_threads_and_prune_index(
            index_path=index, bridge_dir=bridge_dir, kb_path=None,
        )
        return index, report

    def test_active_authorization_thread_is_skipped(self, tmp_path, monkeypatch) -> None:
        index, report = self._run(
            tmp_path, monkeypatch,
            authorizations=[{"status": "active", "included_work_item_ids_parsed": ["WI-9999"]}],
        )
        assert report["protected_authorization_skipped"] == ["gamma"]
        text = index.read_text(encoding="utf-8")
        assert "Document: gamma" in text       # protected -> retained
        assert "Document: delta" not in text   # unrelated -> pruned
        # Tie the guard to the live completion scanner: WI-9999 must still be
        # discoverable from live bridge/INDEX.md after the prune.
        import project_verified_completion_scanner as pvcs
        assert "WI-9999" in pvcs.verified_work_items(tmp_path)

    def test_already_archived_protected_thread_is_skipped(self, tmp_path, monkeypatch) -> None:
        index, report = self._run(
            tmp_path, monkeypatch,
            authorizations=[{"status": "active", "included_work_item_ids_parsed": ["WI-9999"]}],
            archived_protected=True,
        )
        assert report["protected_authorization_skipped"] == ["gamma"]
        assert "Document: gamma" in index.read_text(encoding="utf-8")

    def test_completed_authorization_does_not_protect(self, tmp_path, monkeypatch) -> None:
        index, report = self._run(
            tmp_path, monkeypatch,
            authorizations=[{"status": "completed", "included_work_item_ids_parsed": ["WI-9999"]}],
        )
        # status != active -> not protected -> gamma becomes prunable again.
        assert report["protected_authorization_skipped"] == []
        assert "Document: gamma" not in index.read_text(encoding="utf-8")

    def test_no_authorizations_prunes_all(self, tmp_path, monkeypatch) -> None:
        index, report = self._run(tmp_path, monkeypatch, authorizations=[])
        assert report["protected_authorization_skipped"] == []
        text = index.read_text(encoding="utf-8")
        assert "Document: gamma" not in text
        assert "Document: delta" not in text


# ---------------------------------------------------------------------------
# IP-3: GT-KB origin metadata (the -004 F2 blocker)
# ---------------------------------------------------------------------------


class TestArchiveOriginMetadata:
    def test_archive_row_uses_groundtruth_kb_origin(self, tmp_path, monkeypatch) -> None:
        bridge_dir = _make_bridge(tmp_path)
        index = _write_index(bridge_dir, _verified_thread(bridge_dir, "epsilon"))
        stub = StubDB()
        monkeypatch.setattr(rhbt, "_load_db", lambda _kb: stub)

        rhbt.archive_verified_threads_and_prune_index(
            index_path=index, bridge_dir=bridge_dir, kb_path=None,
        )

        assert len(stub.rows) == 1
        row = stub.rows[0]
        assert row["origin_project"] == "groundtruth-kb"
        assert row["origin_repo"] == "Remaker-Digital/groundtruth-kb"
        assert row["origin_project"] != "agent-red"


# ---------------------------------------------------------------------------
# IP-4: stale-snapshot conflict detection (the -006 F1 blocker)
# ---------------------------------------------------------------------------


class TestConflictSafeWriters:
    def test_write_pruned_index_skips_on_concurrent_change(self, tmp_path) -> None:
        bridge_dir = _make_bridge(tmp_path)
        original = "# Bridge Index\n\nDocument: alpha\nVERIFIED: bridge/alpha-001.md\n"
        real_index = bridge_dir / "INDEX.md"
        real_index.write_text(original, encoding="utf-8")
        concurrent = original + "\nDocument: beta\nNEW: bridge/beta-001.md\n"
        racing = _RacingIndexPath(real_index, mutate_before_read=2, concurrent_text=concurrent)

        removed, skipped = rhbt._write_pruned_index(racing, {"alpha"})

        assert skipped is True
        assert removed == 0
        # The concurrent NEW line survived; the prune did not clobber it.
        text = real_index.read_text(encoding="utf-8")
        assert "Document: beta" in text
        assert "Document: alpha" in text

    def test_write_pruned_index_writes_when_no_conflict(self, tmp_path) -> None:
        bridge_dir = _make_bridge(tmp_path)
        index = bridge_dir / "INDEX.md"
        index.write_text(
            "# Bridge Index\n\nDocument: alpha\nVERIFIED: bridge/alpha-001.md\n",
            encoding="utf-8",
        )
        removed, skipped = rhbt._write_pruned_index(index, {"alpha"})
        assert skipped is False
        assert removed == 1
        assert "Document: alpha" not in index.read_text(encoding="utf-8")

    def test_compact_index_comments_skips_on_concurrent_change(self, tmp_path) -> None:
        bridge_dir = _make_bridge(tmp_path)
        bloat = "\n".join(
            f"<!--   obsolete dispatcher detail #{i} {'x' * 400} -->" for i in range(30)
        )
        original = (
            "# Bridge Index\n\n"
            "<!-- Prime inserts new document entries at the top of the list below. -->\n"
            f"{bloat}\n\n"
            "Document: active\nGO: bridge/active-001.md\n"
        )
        real_index = bridge_dir / "INDEX.md"
        real_index.write_text(original, encoding="utf-8")
        concurrent = original + "\nDocument: beta\nNEW: bridge/beta-001.md\n"
        racing = _RacingIndexPath(real_index, mutate_before_read=2, concurrent_text=concurrent)

        result = rhbt._compact_index_comments(racing, StubDB())

        assert result["skipped_concurrent_index_change"] is True
        text = real_index.read_text(encoding="utf-8")
        assert "Document: beta" in text                       # concurrent line survived
        assert "obsolete dispatcher detail #29" in text       # compaction did not land

    def test_report_surfaces_concurrent_skip(self, tmp_path, monkeypatch) -> None:
        bridge_dir = _make_bridge(tmp_path)
        index = _write_index(bridge_dir, _verified_thread(bridge_dir, "alpha"))
        monkeypatch.setattr(rhbt, "_load_db", lambda _kb: StubDB())
        monkeypatch.setattr(rhbt, "_write_pruned_index", lambda *_a, **_k: (0, True))

        report = rhbt.archive_verified_threads_and_prune_index(
            index_path=index, bridge_dir=bridge_dir, kb_path=None,
        )
        assert report["concurrent_index_change_skipped"] is True


# ---------------------------------------------------------------------------
# IP-5: maybe_archive_and_prune_index entry point
# ---------------------------------------------------------------------------


class TestMaybeArchiveAndPruneIndex:
    def test_no_index_returns_no_op(self, tmp_path) -> None:
        result = bia.maybe_archive_and_prune_index(tmp_path, current_thread="x")
        assert result["triggered"] is False
        assert result["reason"] == "no_index"

    def test_below_threshold_is_no_op_without_pipeline(self, tmp_path, monkeypatch) -> None:
        bridge_dir = _make_bridge(tmp_path)
        _write_index(bridge_dir, _verified_thread(bridge_dir, "alpha"))

        def _boom(*_a, **_k):
            raise AssertionError("pipeline must not be invoked below threshold")

        monkeypatch.setattr(rhbt, "archive_verified_threads_and_prune_index", _boom)

        result = bia.maybe_archive_and_prune_index(tmp_path, current_thread="x", threshold=10_000)
        assert result["triggered"] is False
        assert result["reason"] == "below_threshold"

    def test_above_threshold_invokes_pipeline_excluding_current_thread(self, tmp_path, monkeypatch) -> None:
        bridge_dir = _make_bridge(tmp_path)
        _write_index(bridge_dir, _verified_thread(bridge_dir, "alpha"))
        captured: dict = {}

        def _recorder(*, index_path, bridge_dir, kb_path, exclude_threads):
            captured["exclude_threads"] = exclude_threads
            return {"ok": True}

        monkeypatch.setattr(rhbt, "archive_verified_threads_and_prune_index", _recorder)

        result = bia.maybe_archive_and_prune_index(tmp_path, current_thread="myslug", threshold=1)
        assert result["triggered"] is True
        assert result["report"] == {"ok": True}
        assert captured["exclude_threads"] == frozenset({"myslug"})


# ---------------------------------------------------------------------------
# Archive idempotence
# ---------------------------------------------------------------------------


class TestIdempotence:
    def test_second_pass_creates_no_duplicate_archive_row(self, tmp_path, monkeypatch) -> None:
        bridge_dir = _make_bridge(tmp_path)
        index = _write_index(bridge_dir, _verified_thread(bridge_dir, "zeta"))
        stub = StubDB()
        monkeypatch.setattr(rhbt, "_load_db", lambda _kb: stub)

        rhbt.archive_verified_threads_and_prune_index(
            index_path=index, bridge_dir=bridge_dir, kb_path=None,
        )
        assert len(stub.rows) == 1

        # zeta is pruned from INDEX after pass 1; re-list it to simulate a
        # still-listed, already-archived thread and confirm no duplicate row.
        index.write_text(
            "# Bridge Index\n\n" + _verified_thread(bridge_dir, "zeta") + "\n",
            encoding="utf-8",
        )
        report = rhbt.archive_verified_threads_and_prune_index(
            index_path=index, bridge_dir=bridge_dir, kb_path=None,
        )
        assert report["already_archived"] == 1
        assert len(stub.rows) == 1   # idempotent: no duplicate archive row


# ---------------------------------------------------------------------------
# IP-6: the four bridge-write helper hookups (source inspection)
# ---------------------------------------------------------------------------


class TestHelperHookups:
    HELPERS = [
        REPO_ROOT / ".claude" / "skills" / "bridge-propose" / "helpers" / "write_bridge.py",
        REPO_ROOT / ".claude" / "skills" / "bridge" / "helpers" / "revise_bridge.py",
        REPO_ROOT / ".claude" / "skills" / "bridge" / "helpers" / "impl_report_bridge.py",
        REPO_ROOT / "scripts" / "gtkb_bridge_writer.py",
    ]

    @pytest.mark.parametrize("helper", HELPERS, ids=lambda p: p.name)
    def test_helper_invokes_archival_entry_point(self, helper: Path) -> None:
        body = helper.read_text(encoding="utf-8")
        assert "maybe_archive_and_prune_index" in body, (
            f"{helper.name} does not invoke the WI-3364 archival entry point"
        )
        assert "current_thread=" in body
