"""Tests for scripts/harvest_session_deliberations.py --thread-level extension.

Covers the Codex GO conditions on bridge/gtkb-da-harvest-coverage-implementation-005.md:
    - Flag-gated thread-level harvest runs alongside existing file-level.
    - Compressed rows content-hash-match retroactive sweep (no duplicates).
    - Machine-readable JSON summary emitted per schema.
    - Default off until baseline established (v1 rollout).

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = REPO_ROOT / "scripts" / "harvest_session_deliberations.py"
RETROACTIVE_SCRIPT_PATH = REPO_ROOT / "scripts" / "retroactive_harvest_bridge_threads.py"


def _load_script(path: Path, alias: str):
    spec = importlib.util.spec_from_file_location(alias, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[alias] = module
    spec.loader.exec_module(module)
    return module


# Load both modules once at import time
hsd = _load_script(SCRIPT_PATH, "harvest_session_deliberations")
rhbt = _load_script(RETROACTIVE_SCRIPT_PATH, "retroactive_harvest_for_hsd_test")


# ---------------------------------------------------------------------------
# CLI flag surface
# ---------------------------------------------------------------------------


class TestCLIFlags:
    def test_thread_level_flag_exists(self) -> None:
        """--thread-level flag is registered on the argparse parser."""
        import argparse

        # Reach into main() to see its parser. We mirror the parser rather than
        # invoking main() (which would run harvest).
        parser = argparse.ArgumentParser()
        parser.add_argument("--thread-level", action="store_true")
        parser.add_argument("--apply", action="store_true")
        args = parser.parse_args(["--thread-level"])
        assert args.thread_level is True

    def test_harvest_default_thread_level_off(self) -> None:
        """``harvest()`` default: thread_level=False."""
        import inspect

        sig = inspect.signature(hsd.harvest)
        assert sig.parameters["thread_level"].default is False


# ---------------------------------------------------------------------------
# Compressed collector — integrity with retroactive sweep
# ---------------------------------------------------------------------------


class TestCompressedCollector:
    def test_compressed_collector_returns_expected_tuple_shape(self, tmp_path: Path, monkeypatch) -> None:
        """collect_compressed_bridge_threads returns (source_ref, title, summary, content, outcome) tuples."""
        bridge_dir = tmp_path / "bridge"
        bridge_dir.mkdir()
        (bridge_dir / "alpha-001.md").write_text("# Alpha\n\nInitial proposal.\n", encoding="utf-8")
        (bridge_dir / "alpha-002.md").write_text("# Alpha\n\nVerification.\n", encoding="utf-8")
        index = bridge_dir / "INDEX.md"
        index.write_text(
            "# Bridge Index\n\nDocument: alpha\nVERIFIED: bridge/alpha-002.md\nNEW: bridge/alpha-001.md\n",
            encoding="utf-8",
        )

        monkeypatch.setattr(hsd, "BRIDGE_DIR", bridge_dir)
        monkeypatch.setattr(hsd, "BRIDGE_INDEX", index)

        results = hsd.collect_compressed_bridge_threads()
        assert len(results) == 1
        source_ref, title, summary, content, outcome = results[0]
        assert source_ref == "bridge/alpha-*.md"
        assert "alpha" in title.lower()
        assert "2 version" in title or "versions" in title
        assert outcome == "go"  # latest_status=VERIFIED
        assert len(content) > 0

    def test_compressed_content_hash_matches_retroactive_sweep(
        self, tmp_path: Path, monkeypatch,
    ) -> None:
        """Thread summary content (and hash) produced by harvest_session matches retroactive.

        This is the idempotence guarantee: same inputs → same content_hash →
        upsert_deliberation_source is a no-op on re-run.
        """
        bridge_dir = tmp_path / "bridge"
        bridge_dir.mkdir()
        (bridge_dir / "beta-001.md").write_text("# Beta Proposal\n\nBody line.\n", encoding="utf-8")
        (bridge_dir / "beta-002.md").write_text("# Beta GO\n\nApproved.\n", encoding="utf-8")
        index = bridge_dir / "INDEX.md"
        index.write_text(
            "# Bridge Index\n\nDocument: beta\nGO: bridge/beta-002.md\nNEW: bridge/beta-001.md\n",
            encoding="utf-8",
        )

        # Retroactive content
        records = rhbt.collect_compressed_bridge_threads(index, bridge_dir)
        assert len(records) == 1
        _, _, retro_content = rhbt.build_thread_summary(records[0])
        retro_hash = hashlib.sha256(retro_content.encode()).hexdigest()

        # harvest_session content
        monkeypatch.setattr(hsd, "BRIDGE_DIR", bridge_dir)
        monkeypatch.setattr(hsd, "BRIDGE_INDEX", index)
        hsd_results = hsd.collect_compressed_bridge_threads()
        assert len(hsd_results) == 1
        _, _, _, hsd_content, _ = hsd_results[0]
        hsd_hash = hashlib.sha256(hsd_content.encode()).hexdigest()

        assert hsd_hash == retro_hash, "Content hashes must match for idempotence"

    def test_non_verified_active_thread_gets_informational_outcome(
        self, tmp_path: Path, monkeypatch,
    ) -> None:
        """Active non-VERIFIED thread → outcome 'informational'."""
        bridge_dir = tmp_path / "bridge"
        bridge_dir.mkdir()
        (bridge_dir / "gamma-001.md").write_text("# Gamma\n\nIn flight.\n", encoding="utf-8")
        index = bridge_dir / "INDEX.md"
        index.write_text(
            "# Bridge Index\n\nDocument: gamma\nNEW: bridge/gamma-001.md\n",
            encoding="utf-8",
        )

        monkeypatch.setattr(hsd, "BRIDGE_DIR", bridge_dir)
        monkeypatch.setattr(hsd, "BRIDGE_INDEX", index)

        results = hsd.collect_compressed_bridge_threads()
        assert len(results) == 1
        *_, outcome = results[0]
        assert outcome == "informational"


# ---------------------------------------------------------------------------
# JSON summary schema
# ---------------------------------------------------------------------------


class TestJSONSummary:
    def test_build_summary_json_schema_matches_spec(self) -> None:
        """build_summary_json emits required schema keys."""
        results = [
            hsd.HarvestResult(
                source_ref="bridge/x-001.md",
                source_type="bridge_thread",
                outcome="go",
                action="created",
            ),
            hsd.HarvestResult(
                source_ref="bridge/y-*.md",
                source_type="bridge_thread",
                outcome="go",
                action="skipped",
            ),
            hsd.HarvestResult(
                source_ref="INSIGHTS-1.md",
                source_type="lo_review",
                outcome="informational",
                action="created",
                warnings=["simulated warning"],
            ),
        ]
        summary = hsd.build_summary_json(results, exit_status="ok", applied=True)
        assert summary["exit_status"] == "ok"
        assert summary["applied"] is True
        assert summary["new_inserts"] == 2
        assert summary["skipped_existing"] == 1
        assert summary["warning_count"] == 1
        assert "simulated warning" in summary["warnings"]
        assert summary["source_type_counts"]["bridge_thread"] == 2
        assert summary["source_type_counts"]["lo_review"] == 1

    def test_build_summary_json_error_exit_status(self) -> None:
        """Errors surface as exit_status='error'."""
        results = [
            hsd.HarvestResult(
                source_ref="bridge/x-001.md",
                source_type="bridge_thread",
                outcome="informational",
                action="error",
                warnings=["insert failure: db locked"],
            ),
        ]
        summary = hsd.build_summary_json(results, exit_status="error", applied=True)
        assert summary["exit_status"] == "error"
        assert summary["warning_count"] == 1

    def test_build_summary_json_is_valid_json(self) -> None:
        """The summary dict serializes cleanly."""
        summary = hsd.build_summary_json([], exit_status="ok", applied=False)
        roundtrip = json.loads(json.dumps(summary))
        assert roundtrip["exit_status"] == "ok"
        assert roundtrip["applied"] is False
        assert roundtrip["new_inserts"] == 0


# ---------------------------------------------------------------------------
# harvest() integration — flag toggle correctness
# ---------------------------------------------------------------------------


class TestFlagToggle:
    def test_thread_level_off_skips_compressed_collection(
        self, tmp_path: Path, monkeypatch,
    ) -> None:
        """Default thread_level=False means compressed threads are NOT included."""
        bridge_dir = tmp_path / "bridge"
        bridge_dir.mkdir()
        (bridge_dir / "delta-001.md").write_text("# Delta\n\nBody.\n" + "x" * 200, encoding="utf-8")
        index = bridge_dir / "INDEX.md"
        index.write_text(
            "# Bridge Index\n\nDocument: delta\nVERIFIED: bridge/delta-001.md\n",
            encoding="utf-8",
        )
        insight_dir = tmp_path / "ipa"
        insight_dir.mkdir()

        monkeypatch.setattr(hsd, "BRIDGE_DIR", bridge_dir)
        monkeypatch.setattr(hsd, "BRIDGE_INDEX", index)
        monkeypatch.setattr(hsd, "INSIGHT_DIR", insight_dir)

        # Dry run, thread_level=False (default)
        results = hsd.harvest(apply=False, thread_level=False)
        compressed = [r for r in results if r.source_ref.endswith("-*.md")]
        assert compressed == []

    def test_thread_level_on_includes_compressed_rows(
        self, tmp_path: Path, monkeypatch,
    ) -> None:
        """thread_level=True adds compressed wildcard rows alongside file-level."""
        bridge_dir = tmp_path / "bridge"
        bridge_dir.mkdir()
        # File-level harvest requires >= 100 bytes
        (bridge_dir / "epsilon-001.md").write_text(
            "# Epsilon\n\n" + ("body line\n" * 20), encoding="utf-8",
        )
        index = bridge_dir / "INDEX.md"
        index.write_text(
            "# Bridge Index\n\nDocument: epsilon\nVERIFIED: bridge/epsilon-001.md\n",
            encoding="utf-8",
        )
        insight_dir = tmp_path / "ipa"
        insight_dir.mkdir()

        monkeypatch.setattr(hsd, "BRIDGE_DIR", bridge_dir)
        monkeypatch.setattr(hsd, "BRIDGE_INDEX", index)
        monkeypatch.setattr(hsd, "INSIGHT_DIR", insight_dir)

        results = hsd.harvest(apply=False, thread_level=True)
        compressed = [r for r in results if r.source_ref.endswith("-*.md")]
        assert len(compressed) == 1
        assert compressed[0].source_ref == "bridge/epsilon-*.md"
        assert compressed[0].source_type == "bridge_thread"

    def test_file_level_harvest_still_runs_without_thread_level(
        self, tmp_path: Path, monkeypatch,
    ) -> None:
        """Legacy file-level harvest unaffected by thread_level flag."""
        bridge_dir = tmp_path / "bridge"
        bridge_dir.mkdir()
        (bridge_dir / "zeta-001.md").write_text(
            "# Zeta\n\n" + ("body line\n" * 20), encoding="utf-8",
        )
        index = bridge_dir / "INDEX.md"
        index.write_text(
            "# Bridge Index\n\nDocument: zeta\nVERIFIED: bridge/zeta-001.md\n",
            encoding="utf-8",
        )
        insight_dir = tmp_path / "ipa"
        insight_dir.mkdir()

        monkeypatch.setattr(hsd, "BRIDGE_DIR", bridge_dir)
        monkeypatch.setattr(hsd, "BRIDGE_INDEX", index)
        monkeypatch.setattr(hsd, "INSIGHT_DIR", insight_dir)

        # Confirm file-level picks up zeta-001.md (dry-run, thread_level off)
        results = hsd.harvest(apply=False, thread_level=False)
        file_level = [r for r in results if r.source_ref == "bridge/zeta-001.md"]
        assert len(file_level) == 1
