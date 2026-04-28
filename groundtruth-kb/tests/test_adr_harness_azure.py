# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Tests for D2 Azure ADR verification harness (verify_azure_adrs).

Covers Codex binding conditions F2, F4, F5 from
bridge/gtkb-azure-adr-template-activation-002.md GO:

F2 — Placeholder token `<<ADOPTER-ANSWER-REQUIRED>>` is used correctly;
     replacing it changes harness classification.
F4 — `answered` requires (a) all 9 headings present AND (b) Decision +
     Rationale + Rejected alternatives non-empty + non-placeholder.
     Malformed cases (placeholder removed but section empty/missing)
     remain `unanswered`.
F5 — Exit 0 only when all 13 answered; mixed cases report correct counts.

Copyright (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
Licensed under AGPL-3.0-or-later.
"""

from __future__ import annotations

import pytest

from groundtruth_kb._azure_adr_instance_templates import (
    ADR_MANDATORY_OWNER_ANSWER_HEADINGS,
    ADR_PLACEHOLDER,
    AZURE_ADR_INSTANCE_IDS,
)
from groundtruth_kb.adr_harness import (
    AdrVerificationReport,
    _extract_section,
    _is_answered_section,
    verify_azure_adrs,
)
from groundtruth_kb.adr_scaffold import (
    AdrScaffoldConfig,
    scaffold_adrs,
)
from groundtruth_kb.db import KnowledgeDB


@pytest.fixture
def db(tmp_path):
    return KnowledgeDB(db_path=tmp_path / "test.db")


def _fill_adr_answers(
    db: KnowledgeDB, adr_id: str, *, fill_decision: bool = True, fill_rationale: bool = True, fill_rejected: bool = True
) -> None:
    """Test helper: replace placeholders with actual answer text in the named ADR."""
    stored = db.get_spec(adr_id)
    assert stored is not None, f"{adr_id} must be present before filling"
    new_desc = stored["description"]
    if fill_decision:
        new_desc = new_desc.replace(
            "## Decision\n\n" + ADR_PLACEHOLDER,
            "## Decision\n\nWe chose Container Apps because of managed-platform ergonomics.",
            1,
        )
    if fill_rationale:
        new_desc = new_desc.replace(
            "## Rationale\n\n" + ADR_PLACEHOLDER,
            "## Rationale\n\nContainer Apps provides the scale envelope we need with minimal ops.",
            1,
        )
    if fill_rejected:
        new_desc = new_desc.replace(
            "## Rejected alternatives\n\n" + ADR_PLACEHOLDER,
            "## Rejected alternatives\n\nAKS was rejected due to ops cost; App Service due to limited networking.",
            1,
        )
    db.update_spec(
        id=adr_id,
        description=new_desc,
        changed_by="test_fill_adr_answers",
        change_reason="Simulate adopter-owner answering ADR",
    )


# ---------------------------------------------------------------------------
# Section extraction unit tests
# ---------------------------------------------------------------------------


class TestSectionExtraction:
    def test_extract_section_returns_body(self):
        desc = "# Title\n\n## Decision\n\nWe chose Option A.\n\n## Rationale\n\nBecause reasons.\n"
        assert _extract_section(desc, "Decision") == "We chose Option A."

    def test_extract_section_handles_last_section(self):
        desc = "# Title\n\n## Decision\n\nWe chose Option A."
        assert _extract_section(desc, "Decision") == "We chose Option A."

    def test_extract_section_missing_heading_returns_none(self):
        desc = "# Title\n\n## Decision\n\nWe chose Option A."
        assert _extract_section(desc, "Nonexistent") is None

    def test_extract_section_empty_body_returns_empty_string(self):
        desc = "## Decision\n\n\n## Rationale\n\nBody"
        assert _extract_section(desc, "Decision") == ""

    def test_is_answered_section_placeholder_fails(self):
        assert _is_answered_section(ADR_PLACEHOLDER) is False

    def test_is_answered_section_empty_fails(self):
        assert _is_answered_section("") is False
        assert _is_answered_section("   \n\n  ") is False
        assert _is_answered_section(None) is False

    def test_is_answered_section_substantive_passes(self):
        assert _is_answered_section("We chose Option A for reason X.") is True


# ---------------------------------------------------------------------------
# Harness behavior — empty DB (all missing)
# ---------------------------------------------------------------------------


class TestHarnessEmptyDB:
    def test_empty_db_reports_all_13_missing(self, db):
        report = verify_azure_adrs(db)
        assert isinstance(report, AdrVerificationReport)
        assert report.total == 13
        assert report.missing_count == 13
        assert report.answered_count == 0
        assert report.unanswered_count == 0

    def test_empty_db_all_answered_false(self, db):
        report = verify_azure_adrs(db)
        assert report.all_answered() is False


# ---------------------------------------------------------------------------
# Harness behavior — post-scaffold (all unanswered with placeholders)
# ---------------------------------------------------------------------------


class TestHarnessPostScaffold:
    def test_post_scaffold_all_13_unanswered(self, db):
        scaffold_adrs(db, AdrScaffoldConfig(), dry_run=False)
        report = verify_azure_adrs(db)
        assert report.total == 13
        assert report.missing_count == 0
        assert report.unanswered_count == 13
        assert report.answered_count == 0

    def test_post_scaffold_unanswered_sections_named(self, db):
        """F4: each unanswered entry names exactly the 3 mandatory sections."""
        scaffold_adrs(db, AdrScaffoldConfig(), dry_run=False)
        report = verify_azure_adrs(db)
        for entry in report.entries:
            assert entry.status == "unanswered"
            assert set(entry.unanswered_sections) == set(ADR_MANDATORY_OWNER_ANSWER_HEADINGS)
            # All 9 headings present post-scaffold:
            assert entry.missing_headings == ()


# ---------------------------------------------------------------------------
# Harness behavior — single ADR answered (F2: placeholder removal changes status)
# ---------------------------------------------------------------------------


class TestHarnessSingleAnswered:
    def test_filling_one_adr_changes_its_status_to_answered(self, db):
        scaffold_adrs(db, AdrScaffoldConfig(), dry_run=False)
        _fill_adr_answers(db, "ADR-AZURE-COMPUTE-001")
        report = verify_azure_adrs(db)
        assert report.answered_count == 1
        assert report.unanswered_count == 12
        assert report.missing_count == 0
        # Find the compute entry:
        compute_entry = next(e for e in report.entries if e.adr_id == "ADR-AZURE-COMPUTE-001")
        assert compute_entry.status == "answered"
        assert compute_entry.unanswered_sections == ()

    def test_filling_all_13_makes_all_answered(self, db):
        scaffold_adrs(db, AdrScaffoldConfig(), dry_run=False)
        for adr_id in AZURE_ADR_INSTANCE_IDS:
            _fill_adr_answers(db, adr_id)
        report = verify_azure_adrs(db)
        assert report.answered_count == 13
        assert report.all_answered() is True


# ---------------------------------------------------------------------------
# Harness behavior — F4 malformed cases: placeholder removed but section empty
# ---------------------------------------------------------------------------


class TestHarnessMalformed:
    """F4: placeholder absence alone is NOT sufficient; section must be substantive."""

    def test_empty_decision_section_remains_unanswered(self, db):
        """Adopter deletes placeholder but leaves section empty → still unanswered."""
        scaffold_adrs(db, AdrScaffoldConfig(), dry_run=False)
        stored = db.get_spec("ADR-AZURE-TENANCY-001")
        assert stored is not None
        # Remove the placeholder from Decision but leave nothing in its place:
        desc_with_empty_decision = stored["description"].replace(
            "## Decision\n\n" + ADR_PLACEHOLDER,
            "## Decision\n\n",
            1,
        )
        db.update_spec(
            id="ADR-AZURE-TENANCY-001",
            description=desc_with_empty_decision,
            changed_by="test_malformed",
            change_reason="Simulate malformed Decision section",
        )
        report = verify_azure_adrs(db)
        entry = next(e for e in report.entries if e.adr_id == "ADR-AZURE-TENANCY-001")
        assert entry.status == "unanswered"
        assert "Decision" in entry.unanswered_sections

    def test_missing_heading_remains_unanswered(self, db):
        """Adopter removes a required heading entirely → unanswered with missing_headings flagged."""
        scaffold_adrs(db, AdrScaffoldConfig(), dry_run=False)
        stored = db.get_spec("ADR-AZURE-COST-001")
        assert stored is not None
        # Strip the '## Review trigger' heading and its body:
        desc = stored["description"]
        idx = desc.find("## Review trigger")
        truncated = desc[:idx].rstrip() + "\n"
        db.update_spec(
            id="ADR-AZURE-COST-001",
            description=truncated,
            changed_by="test_malformed",
            change_reason="Simulate missing Review trigger heading",
        )
        # Also fill Decision/Rationale/Rejected so the only failure is the missing heading:
        _fill_adr_answers(db, "ADR-AZURE-COST-001")
        report = verify_azure_adrs(db)
        entry = next(e for e in report.entries if e.adr_id == "ADR-AZURE-COST-001")
        assert entry.status == "unanswered"
        assert "Review trigger" in entry.missing_headings

    def test_partial_fill_remains_unanswered(self, db):
        """Adopter fills Decision + Rationale but leaves Rejected alternatives with placeholder."""
        scaffold_adrs(db, AdrScaffoldConfig(), dry_run=False)
        _fill_adr_answers(db, "ADR-AZURE-DR-001", fill_rejected=False)
        report = verify_azure_adrs(db)
        entry = next(e for e in report.entries if e.adr_id == "ADR-AZURE-DR-001")
        assert entry.status == "unanswered"
        assert "Rejected alternatives" in entry.unanswered_sections
        assert "Decision" not in entry.unanswered_sections
        assert "Rationale" not in entry.unanswered_sections


# ---------------------------------------------------------------------------
# Harness behavior — mixed state (missing + unanswered + answered)
# ---------------------------------------------------------------------------


class TestHarnessMixedState:
    """F5: mixed ADR states produce correct counts."""

    def test_partial_scaffold_produces_mixed_state(self, db):
        """Scaffold 13, delete 3 to simulate missing, fill 5 to simulate answered."""
        scaffold_adrs(db, AdrScaffoldConfig(), dry_run=False)

        # Fill 5 ADRs
        answered_ids = list(AZURE_ADR_INSTANCE_IDS[:5])
        for adr_id in answered_ids:
            _fill_adr_answers(db, adr_id)

        report = verify_azure_adrs(db)
        # 5 answered, 8 unanswered (13 - 5), 0 missing — since we kept all scaffold entries.
        assert report.answered_count == 5
        assert report.unanswered_count == 8
        assert report.missing_count == 0
        assert report.total == 13
        assert report.all_answered() is False
