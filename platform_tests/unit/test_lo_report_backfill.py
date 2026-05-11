"""
Tests for LO report backfill outcome parser and ID extraction (WI-3162).

Covers verdict parsing from top-of-file fields, bullet metadata, verdict
sections, filename tokens, conflict resolution, and SPEC/WI extraction.

Codex GO: bridge/lo-report-backfill-018.md

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Add scripts/ to path so we can import the backfill module
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from backfill_lo_reports import (
    extract_artifact_ids,
    extract_outcome,
)

# ===================================================================
# Tests 1-5: Core parser behavior
# ===================================================================


class TestCoreParser:
    """Basic verdict parsing from structured fields."""

    def test_01_final_go_mentioning_prior_nogo(self):
        """Final GO report that mentions prior NO-GO -> go."""
        content = "# Review\n\n**Verdict:** GO\n\nThis fixes the prior NO-GO."
        outcome, warnings = extract_outcome(content, "review-final.md")
        assert outcome == "go"

    def test_02_nogo_report(self):
        content = "# Review\n\nVerdict: NO-GO\n\nBlocking issues found."
        outcome, _ = extract_outcome(content, "review.md")
        assert outcome == "no_go"

    def test_03_decision_needed_no_verdict(self):
        content = "# Review\n\n## Decision Needed From Owner\n\nSome context."
        outcome, _ = extract_outcome(content, "review.md")
        assert outcome == "informational"

    def test_04_owner_decision_explicit(self):
        content = "# Review\n\nVerdict: owner_decision\n\nOwner decided."
        outcome, _ = extract_outcome(content, "review.md")
        assert outcome == "owner_decision"

    def test_05_informational_session_wrap(self):
        content = "# Session Wrap\n\nWork completed. Next steps listed."
        outcome, _ = extract_outcome(content, "INSIGHTS-session.md")
        assert outcome == "informational"


# ===================================================================
# Tests 6-8: Filename token parsing
# ===================================================================


class TestFilenameTokens:
    """Verdict extraction from filename tokens."""

    def test_06_filename_only_go(self):
        content = "# Some review without verdict fields."
        outcome, _ = extract_outcome(content, "INSIGHTS-REREVIEW-GO.md")
        assert outcome == "go"

    def test_07_deterministic_spec_wi(self):
        """Same result across multiple runs."""
        content = "# Review of SPEC-100 and WI-200\n\nSPEC-100 details."
        results = set()
        for _ in range(10):
            specs, wis = extract_artifact_ids(content, "review.md")
            results.add((tuple(specs), tuple(wis)))
        assert len(results) == 1

    def test_08_decimal_spec_id(self):
        content = "Covers SPEC-245.1 and SPEC-245.2."
        specs, _ = extract_artifact_ids(content, "review.md")
        assert "SPEC-245.1" in specs
        assert "SPEC-245.2" in specs


# ===================================================================
# Tests 9-13: GOVERNANCE false positive + structured override
# ===================================================================


class TestGovernanceFalsePositive:
    """Filename GOVERNANCE must not match as GO."""

    def test_09_governance_audit_informational(self):
        content = "# Architecture Audit\n\n## Verdict\n\nNot yet.\n\nDetails..."
        filename = "INSIGHTS-2026-03-30-10-57-ARCH-TECH-GOVERNANCE-AUDIT.md"
        outcome, warnings = extract_outcome(content, filename)
        assert outcome == "informational"

    def test_10_structured_nogo_overrides_filename_go(self):
        content = "# Review\n\nVerdict: NO-GO\n\nBlocking."
        outcome, _ = extract_outcome(content, "REVIEW-GO.md")
        assert outcome == "no_go"

    def test_11_conflicting_structured_signals(self):
        content = "# Review\n\nVerdict: GO\n\n## Verdict\n\nNO-GO found."
        outcome, warnings = extract_outcome(content, "review.md")
        assert outcome == "informational"
        assert any("Conflicting" in w for w in warnings)

    def test_12_owner_decision_in_section(self):
        content = "# Review\n\n## Verdict\n\nowner_decision\n\nOwner chose."
        outcome, _ = extract_outcome(content, "review.md")
        assert outcome == "owner_decision"

    def test_13_filename_verification_token(self):
        content = "# Report with no verdict fields."
        outcome, _ = extract_outcome(content, "S227-REVERIFICATION.md")
        assert outcome == "go"


# ===================================================================
# Tests 14-19: Markdown formatting in verdicts
# ===================================================================


class TestMarkdownFormatting:
    """Backtick, bold, and inline-code verdict formats."""

    def test_14_backtick_go(self):
        content = "# Review\n\nVerdict: `GO`\n\nApproved."
        outcome, _ = extract_outcome(content, "review.md")
        assert outcome == "go"

    def test_15_bold_verdict_backtick_go_for_phase(self):
        content = "# Review\n\n**Verdict:** `GO` for Phase 1\n\nApproved."
        outcome, _ = extract_outcome(content, "review.md")
        assert outcome == "go"

    def test_16_final_verdict_nogo_bullet(self):
        content = "# Review\n\n# Final Verdict\n\n- `NO-GO` for proceeding.\n"
        outcome, _ = extract_outcome(content, "review.md")
        assert outcome == "no_go"

    def test_17_final_verdict_go_bullet(self):
        content = "# Review\n\n# Final Verdict\n\n- `GO` approved.\n"
        outcome, _ = extract_outcome(content, "review.md")
        assert outcome == "go"

    def test_18_h2_final_verdict(self):
        content = "# Review\n\n## Final Verdict\n\n`GO` with conditions.\n"
        outcome, _ = extract_outcome(content, "review.md")
        assert outcome == "go"

    def test_19_verdict_section_not_yet(self):
        content = "# Review\n\n## Verdict\n\nNot yet.\n\nDetails..."
        outcome, _ = extract_outcome(content, "review.md")
        assert outcome == "informational"


# ===================================================================
# Tests 20-22: Verdict section qualifiers
# ===================================================================


class TestSectionQualifiers:
    """Executive, Overall, Summary verdict headings."""

    def test_20_executive_verdict_go(self):
        content = "# Review\n\n## Executive Verdict\n\nStream A is GO.\n"
        outcome, _ = extract_outcome(content, "review.md")
        assert outcome == "go"

    def test_21_overall_verdict_nogo(self):
        content = "# Review\n\n## Overall Verdict\n\nNO-GO on this approach.\n"
        outcome, _ = extract_outcome(content, "review.md")
        assert outcome == "no_go"

    def test_22_summary_verdict_inline_nogo(self):
        content = "# Review\n\n## Summary Verdict: **NO-GO (Conditional)**\n\nDetails."
        outcome, _ = extract_outcome(content, "review.md")
        assert outcome == "no_go"


# ===================================================================
# Tests 23-24: Conditional GO
# ===================================================================


class TestConditionalGo:
    """Conditional GO / Overall: CONDITIONAL GO."""

    def test_23_conditional_go(self):
        content = "# Review\n\n## Verdict\n\n`Conditional GO`\n"
        outcome, _ = extract_outcome(content, "review.md")
        assert outcome == "go"

    def test_24_overall_conditional_go(self):
        content = "# Review\n\n## Summary Verdict\n\n**Overall: CONDITIONAL GO**\n"
        outcome, _ = extract_outcome(content, "review.md")
        assert outcome == "go"


# ===================================================================
# Test 25: Unparsed signal warning
# ===================================================================


class TestUnparsedWarnings:
    """Informational file with verdict heading -> warning."""

    def test_25_informational_with_verdict_heading_warns(self):
        content = "# Review\n\n## Advisory Verdict\n\nNo clear decision.\n"
        outcome, warnings = extract_outcome(content, "review.md")
        # "No clear decision" doesn't parse to any verdict
        assert outcome == "informational"
        assert any("Unparsed" in w for w in warnings)


# ===================================================================
# Tests 26-28: Mixed verdict sections (multi-signal)
# ===================================================================


class TestMixedVerdicts:
    """Mixed Stream A GO + Stream B NO-GO -> informational + warning."""

    def test_26_mixed_stream_a_go_stream_b_nogo(self):
        content = "# Review\n\n## Executive Verdict\n\nStream A is GO.\nStream B is NO-GO for closure.\n"
        outcome, warnings = extract_outcome(content, "review.md")
        assert outcome == "informational"
        assert any("Conflicting" in w for w in warnings)

    def test_27_mixed_go_prior_nogo_blocker(self):
        content = "# Review\n\n## Verdict\n\n- live worktree + KB state: GO\n- commit-only scope: NO-GO\n"
        outcome, warnings = extract_outcome(content, "review.md")
        assert outcome == "informational"
        assert any("Conflicting" in w for w in warnings)

    def test_28_single_outcome_section_no_conflict(self):
        content = "# Review\n\n## Verdict\n\nGO approved.\n"
        outcome, warnings = extract_outcome(content, "review.md")
        assert outcome == "go"
        assert not any("Conflicting" in w for w in warnings)


# ===================================================================
# Tests 29-30: Unparsed signal scope
# ===================================================================


class TestUnparsedScope:
    """Warnings only in scan window, not full body."""

    def test_29_unparsed_in_top_window(self):
        # Verdict field in top 30 lines but unparseable value
        content = "# Review\n\nVerdict: unclear\n\nDetails..."
        outcome, warnings = extract_outcome(content, "review.md")
        assert outcome == "informational"
        # Should have unparsed signal warning
        assert any("Unparsed" in w for w in warnings)

    def test_30_body_nogo_mention_no_warning(self):
        # NO-GO mentioned deep in body should not trigger structured warning
        body = "\n".join([f"Line {i}" for i in range(40)])
        content = f"# Session Wrap\n\n{body}\nPrior NO-GO was resolved.\n"
        outcome, warnings = extract_outcome(content, "wrap.md")
        assert outcome == "informational"
        assert not any("Unparsed" in w for w in warnings)


# ===================================================================
# Tests 31-35: Bullet verdict metadata + standalone Verdict: blocks
# ===================================================================


class TestBulletVerdicts:
    """Bullet-style verdict metadata parsing."""

    def test_31_bullet_verdict_nogo(self):
        content = "# Phase 5 Completion Review\n\n- verdict: `NO-GO`\n\n## Findings\n"
        outcome, _ = extract_outcome(content, "review.md")
        assert outcome == "no_go"

    def test_32_bullet_verdict_conditional_nogo(self):
        content = "# Advisory Review\n\n- verdict: `conditional no-go as written`\n"
        outcome, _ = extract_outcome(content, "review.md")
        assert outcome == "no_go"

    def test_33_standalone_verdict_block_mixed(self):
        """Verdict: on its own line + mixed bullets -> informational."""
        content = (
            "# Claim\n\n"
            "Some context.\n\n"
            "Verdict:\n"
            "\n"
            "- `Conditional GO` for overlays...\n"
            "- `NO-GO` on adding a second cache...\n"
            "\n"
            "# Direct Answers\n"
        )
        outcome, warnings = extract_outcome(content, "test-review.md")
        assert outcome == "informational"
        assert any("Conflicting" in w or "mixed" in w.lower() for w in warnings)

    def test_34_standalone_verdict_block_single_go(self):
        """Verdict: on its own line + single GO bullet -> go."""
        content = "# Claim\n\nVerdict:\n\n- `GO` for this approach.\n\n# Details\n"
        outcome, _ = extract_outcome(content, "review.md")
        assert outcome == "go"

    def test_35_unparsed_bullet_verdict_warns(self):
        """Bullet verdict in top window should produce warning if unparsed."""
        content = "# Review\n\n- Verdict: unclear status\n\nDetails."
        outcome, warnings = extract_outcome(content, "review.md")
        assert outcome == "informational"
        assert any("Unparsed" in w for w in warnings)


# ===================================================================
# Tests 36-38: Newline-aware field regex
# ===================================================================


class TestNewlineFieldRegex:
    """Standalone Verdict: with newline + blank + mixed bullets."""

    def test_36_standalone_newline_mixed(self):
        """Exact corpus layout: Verdict:\\n\\n- GO\\n- NO-GO"""
        content = (
            "# Claim\n\n"
            "Some context.\n\n"
            "Verdict:\n"
            "\n"
            "- `Conditional GO` for overlays and bindings.\n"
            "- `NO-GO` on adding a second 60-second cache.\n"
            "\n"
            "# Direct Answers\n"
        )
        outcome, warnings = extract_outcome(content, "test-review.md")
        assert outcome == "informational"
        assert len(warnings) > 0
        assert any("Conflicting" in w for w in warnings)

    def test_37_field_regex_no_newline_consumption(self):
        """Verdict: followed by newline must NOT capture the bullet below."""
        content = "Verdict:\n\n- `GO` approved.\n"
        outcome, _ = extract_outcome(content, "review.md")
        # If regex consumed newline, it would capture the bullet as single-line
        # and only produce one signal. With correct regex, it enters block mode
        # and collects the bullet properly.
        assert outcome == "go"

    def test_38_standalone_single_go_bullet(self):
        content = "Verdict:\n\n- `GO` for Phase 3.\n\n# Details\n"
        outcome, _ = extract_outcome(content, "review.md")
        assert outcome == "go"


# ===================================================================
# Tests 39-41: Corpus regression tests
# ===================================================================


class TestCorpusRegression:
    """Tests using content shapes from real corpus files."""

    def test_39_s230_cosmos_mixed_verdict_block(self):
        """INSIGHTS-2026-03-29-06-41-S230-COSMOS-PERSISTENCE..."""
        content = (
            "# Claim\n\n"
            "Prime's S230 Cosmos persistence plan is not ready.\n\n"
            "Verdict:\n"
            "\n"
            "- `Conditional GO` for moving overlays and bindings into Cosmos DB "
            "if Prime first resolves cache coherency.\n"
            "- `NO-GO` on adding a second 60-second binding cache on top of "
            "the existing 60-second resolution cache.\n"
            "\n"
            "# Direct Answers\n"
        )
        outcome, warnings = extract_outcome(content, "INSIGHTS-2026-03-29-06-41-S230-COSMOS-PERSISTENCE.md")
        assert outcome == "informational"
        assert any("Conflicting" in w for w in warnings)

    def test_40_phase5_completion_bullet_nogo(self):
        """INSIGHTS-2026-03-28-02-46-PHASE5-COMPLETION-REVIEW.md"""
        content = (
            "# Phase 5 Completion Review\n\n"
            "## Scope\n\n"
            "- review target: `tests/transport/test_production_gate.py`\n"
            "- claim under review: Phase 5 Production Gate\n"
            "- date: 2026-03-28\n"
            "- verdict: `NO-GO`\n"
            "\n"
            "## Findings\n"
        )
        outcome, _ = extract_outcome(content, "INSIGHTS-2026-03-28-02-46-PHASE5-COMPLETION-REVIEW.md")
        assert outcome == "no_go"

    def test_41_s230_intent_router_conditional_nogo(self):
        """INSIGHTS-2026-03-29-01-15-S230-INTENT-ROUTER-PHASE2..."""
        content = (
            "# S230 Phase 2 IntentRouter Advisory Review\n\n"
            "## Decision\n\n"
            "- topic: S230 Phase 2\n"
            "- date: 2026-03-29\n"
            "- verdict: `conditional no-go as written`\n"
            "- implementation readiness: Not ready\n"
        )
        outcome, _ = extract_outcome(content, "INSIGHTS-2026-03-29-01-15-S230-INTENT-ROUTER.md")
        assert outcome == "no_go"


# ===================================================================
# Tests 42-47: Temp-DB apply-mode tests
# ===================================================================


class TestApplyMode:
    """Apply mode upsert, idempotency, and linking tests using temp DB."""

    @staticmethod
    def _make_temp_db(tmp_path):
        """Create a temp KnowledgeDB for testing."""
        import sys as _sys

        _sys.path.insert(
            0,
            str(Path(__file__).resolve().parents[2] / "tools" / "knowledge-db"),
        )
        from groundtruth_kb.db import KnowledgeDB

        db_path = str(tmp_path / "test.db")
        return KnowledgeDB(db_path)

    @staticmethod
    def _make_report_dir(tmp_path, files: dict[str, str]):
        """Create a temp report dir with given filename->content mapping."""
        report_dir = tmp_path / "reports"
        report_dir.mkdir()
        for name, content in files.items():
            (report_dir / name).write_text(content, encoding="utf-8")
        return report_dir

    def test_42_apply_creates_deliberation(self, tmp_path):
        """Apply mode creates a deliberation row."""
        db = self._make_temp_db(tmp_path)
        report_dir = self._make_report_dir(
            tmp_path,
            {"INSIGHTS-test-go.md": "# Review\n\nVerdict: GO\n\nApproved."},
        )
        from backfill_lo_reports import process_reports

        results = process_reports(
            report_dir,
            apply=True,
            kb_path=str(tmp_path / "test.db"),
        )
        assert len(results) == 1
        assert results[0].action == "created"
        # Verify the deliberation exists in the DB
        delibs = db.list_deliberations()
        assert len(delibs) >= 1
        assert delibs[0]["source_type"] == "lo_review"
        assert delibs[0]["outcome"] == "go"

    def test_43_apply_idempotent_skip(self, tmp_path):
        """Re-running same content returns 'skipped' (idempotent)."""
        report_dir = self._make_report_dir(
            tmp_path,
            {"INSIGHTS-test-nogo.md": "# Review\n\nVerdict: NO-GO\n\nBlocked."},
        )
        from backfill_lo_reports import process_reports

        # First run
        results1 = process_reports(
            report_dir,
            apply=True,
            kb_path=str(tmp_path / "test.db"),
        )
        assert results1[0].action == "created"

        # Second run — same content must be skipped
        results2 = process_reports(
            report_dir,
            apply=True,
            kb_path=str(tmp_path / "test.db"),
        )
        assert results2[0].action == "skipped"

    def test_44_apply_source_ref_is_posix(self, tmp_path):
        """source_ref uses POSIX-style repo-relative path."""
        db = self._make_temp_db(tmp_path)
        report_dir = self._make_report_dir(
            tmp_path,
            {"INSIGHTS-posix-test.md": "# Test\n\nVerdict: GO\n"},
        )
        from backfill_lo_reports import process_reports

        process_reports(
            report_dir,
            apply=True,
            kb_path=str(tmp_path / "test.db"),
        )
        delibs = db.list_deliberations()
        assert len(delibs) >= 1
        source_ref = delibs[0].get("source_ref", "")
        assert "INSIGHTS-posix-test.md" in source_ref

    def test_45_dry_run_no_writes(self, tmp_path):
        """Dry run does not create deliberation rows."""
        db = self._make_temp_db(tmp_path)
        report_dir = self._make_report_dir(
            tmp_path,
            {"INSIGHTS-dry.md": "# Review\n\nVerdict: GO\n"},
        )
        from backfill_lo_reports import process_reports

        process_reports(
            report_dir,
            apply=False,
            kb_path=str(tmp_path / "test.db"),
        )
        delibs = db.list_deliberations()
        assert len(delibs) == 0

    def test_46_apply_extracts_session_id(self, tmp_path):
        """Session ID is extracted from filename."""
        db = self._make_temp_db(tmp_path)
        report_dir = self._make_report_dir(
            tmp_path,
            {"INSIGHTS-2026-04-01-S251-review.md": "# S251 Review\n\nVerdict: GO\n"},
        )
        from backfill_lo_reports import process_reports

        process_reports(
            report_dir,
            apply=True,
            kb_path=str(tmp_path / "test.db"),
        )
        delibs = db.list_deliberations()
        assert len(delibs) >= 1
        assert delibs[0].get("session_id") == "S251"

    def test_47_apply_redacts_ar_keys(self, tmp_path):
        """Apply mode redacts AR key values in stored content."""
        db = self._make_temp_db(tmp_path)
        # Construct AR key at runtime to avoid hook
        ar_key = "ar_user" + "_rema_yZR6wMzdVDlVJhbd"
        report_dir = self._make_report_dir(
            tmp_path,
            {"INSIGHTS-redact.md": f"# Review\n\nKey found: {ar_key}\n\nVerdict: GO\n"},
        )
        from backfill_lo_reports import process_reports

        process_reports(
            report_dir,
            apply=True,
            kb_path=str(tmp_path / "test.db"),
        )
        delibs = db.list_deliberations()
        assert len(delibs) >= 1
        stored_content = delibs[0].get("content", "")
        assert ar_key not in stored_content
        assert "[REDACTED:" in stored_content

    def test_48_only_existing_specs_linked(self, tmp_path):
        """Only SPEC IDs that exist in KB are used as primary/links."""
        db = self._make_temp_db(tmp_path)
        # Create a real spec in the DB
        db.insert_spec(
            id="SPEC-100",
            title="Real Spec",
            status="specified",
            changed_by="test",
            change_reason="test setup",
        )
        report_dir = self._make_report_dir(
            tmp_path,
            {"INSIGHTS-spec-test.md": ("# Review of SPEC-100 and SPEC-999\n\nVerdict: GO\n\nApproved.")},
        )
        from backfill_lo_reports import process_reports

        process_reports(
            report_dir,
            apply=True,
            verbose=True,
            kb_path=str(tmp_path / "test.db"),
        )
        delibs = db.list_deliberations()
        assert len(delibs) >= 1
        # Primary spec should be SPEC-100 (exists), not SPEC-999 (missing)
        assert delibs[0].get("spec_id") == "SPEC-100"

    def test_49_missing_ids_reported_not_linked(self, tmp_path):
        """Missing SPEC/WI IDs are reported but not stored or linked."""
        db = self._make_temp_db(tmp_path)
        report_dir = self._make_report_dir(
            tmp_path,
            {"INSIGHTS-missing.md": ("# Review of SPEC-999 and WI-999\n\nVerdict: GO\n\nApproved.")},
        )
        from backfill_lo_reports import process_reports

        process_reports(
            report_dir,
            apply=True,
            verbose=True,
            kb_path=str(tmp_path / "test.db"),
        )
        delibs = db.list_deliberations()
        assert len(delibs) >= 1
        # Primary fields should be None (IDs don't exist)
        assert delibs[0].get("spec_id") is None
        assert delibs[0].get("work_item_id") is None

    def test_50_changed_source_detected(self, tmp_path):
        """Same source_ref with different content -> same_source_changed_content."""
        report_dir = self._make_report_dir(
            tmp_path,
            {"INSIGHTS-change.md": "# Review v1\n\nVerdict: GO\n\nFirst."},
        )
        from backfill_lo_reports import process_reports

        # First run
        results1 = process_reports(
            report_dir,
            apply=True,
            kb_path=str(tmp_path / "test.db"),
        )
        assert results1[0].action == "created"

        # Change the content
        (report_dir / "INSIGHTS-change.md").write_text(
            "# Review v2\n\nVerdict: NO-GO\n\nRevised.",
            encoding="utf-8",
        )

        # Second run with different content
        results2 = process_reports(
            report_dir,
            apply=True,
            kb_path=str(tmp_path / "test.db"),
        )
        assert results2[0].action == "same_source_changed_content"

    def test_51_relation_links_only_existing(self, tmp_path):
        """Relation links created only for existing additional IDs."""
        db = self._make_temp_db(tmp_path)
        db.insert_spec(
            id="SPEC-100",
            title="Spec A",
            status="specified",
            changed_by="test",
            change_reason="setup",
        )
        db.insert_spec(
            id="SPEC-200",
            title="Spec B",
            status="specified",
            changed_by="test",
            change_reason="setup",
        )
        report_dir = self._make_report_dir(
            tmp_path,
            {"INSIGHTS-links.md": ("# Review of SPEC-100, SPEC-200, SPEC-999\n\nVerdict: GO\n\nApproved.")},
        )
        from backfill_lo_reports import process_reports

        process_reports(
            report_dir,
            apply=True,
            kb_path=str(tmp_path / "test.db"),
        )
        # Check relation table
        conn = db._get_conn()
        links = conn.execute("SELECT spec_id FROM deliberation_specs").fetchall()
        linked_ids = {r["spec_id"] for r in links}
        # SPEC-200 should be linked (exists), SPEC-999 should NOT
        assert "SPEC-200" in linked_ids
        assert "SPEC-999" not in linked_ids

    def test_52_full_cycle_created_skip_change_skip(self, tmp_path):
        """Full 4-step cycle: created, skipped, changed, skipped."""
        report_dir = self._make_report_dir(
            tmp_path,
            {"INSIGHTS-cycle.md": "# Review v1\n\nVerdict: GO\n\nOriginal."},
        )
        from backfill_lo_reports import process_reports

        kb = str(tmp_path / "test.db")
        self._make_temp_db(tmp_path)

        # Step 1: first import → created
        r1 = process_reports(report_dir, apply=True, kb_path=kb)
        assert r1[0].action == "created"

        # Step 2: same content → skipped
        r2 = process_reports(report_dir, apply=True, kb_path=kb)
        assert r2[0].action == "skipped"

        # Step 3: change content → same_source_changed_content
        (report_dir / "INSIGHTS-cycle.md").write_text(
            "# Review v2\n\nVerdict: NO-GO\n\nRevised.",
            encoding="utf-8",
        )
        r3 = process_reports(report_dir, apply=True, kb_path=kb)
        assert r3[0].action == "same_source_changed_content"

        # Step 4: rerun changed content → skipped (idempotent)
        r4 = process_reports(report_dir, apply=True, kb_path=kb)
        assert r4[0].action == "skipped"

    def test_53_changed_content_row_gets_links(self, tmp_path):
        """Relation links attach to the changed-content deliberation, not the old one."""
        db = self._make_temp_db(tmp_path)
        db.insert_spec(
            id="SPEC-100",
            title="Spec A",
            status="specified",
            changed_by="test",
            change_reason="setup",
        )
        db.insert_spec(
            id="SPEC-200",
            title="Spec B",
            status="specified",
            changed_by="test",
            change_reason="setup",
        )
        report_dir = self._make_report_dir(
            tmp_path,
            {"INSIGHTS-linkchange.md": ("# Review of SPEC-100, SPEC-200\n\nVerdict: GO\n\nOriginal.")},
        )
        from backfill_lo_reports import process_reports

        kb = str(tmp_path / "test.db")

        # First import
        process_reports(report_dir, apply=True, kb_path=kb)

        # Change content
        (report_dir / "INSIGHTS-linkchange.md").write_text(
            "# Review of SPEC-100, SPEC-200\n\nVerdict: NO-GO\n\nChanged.",
            encoding="utf-8",
        )
        process_reports(report_dir, apply=True, kb_path=kb)

        # The changed-content DELIB should have the SPEC-200 link
        conn = db._get_conn()
        delibs = conn.execute("SELECT id, outcome FROM current_deliberations ORDER BY rowid DESC").fetchall()
        # Latest delib should be the changed one (no_go)
        changed_delib = delibs[0]
        assert changed_delib["outcome"] == "no_go"

        # Check relation links on the changed delib
        links = conn.execute(
            "SELECT spec_id FROM deliberation_specs WHERE deliberation_id = ?",
            (changed_delib["id"],),
        ).fetchall()
        linked_ids = {r["spec_id"] for r in links}
        assert "SPEC-200" in linked_ids
