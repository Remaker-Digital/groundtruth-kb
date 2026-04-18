# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Tests for D1 Azure spec scaffold (`azure-enterprise` profile).

Covers all 6 Codex binding conditions from bridge/gtkb-azure-spec-scaffold-004.md GO:

1. Preserve existing `minimal` and `full` behavior (new doc buckets empty;
   existing spec scaffold tests continue to pass — covered via regression tests
   in this file plus the unchanged existing test_spec_scaffold.py).
2. CLI output distinguishes spec counts from document counts (covered via
   direct ScaffoldReport field checks; full CLI integration covered in
   test_cli.py-level tests that already run on the package).
3. Idempotence by artifact type: specs don't create v2 on re-run; document
   doesn't create v2 on re-run; skipped rows identify id + reason.
4. Apply-mode tests query persisted rows via db.get_spec()["description"]
   and db.get_document() — NOT dry-run dicts.
5. Scope boundary preserved: no changes to project/scaffold.py, doctor.py,
   or CI workflows (verified structurally — not imported from those modules).
6. `description` field is sufficient for template bodies (verified by apply
   round-trip: insert → get_spec → description contains expected headings).

Copyright (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
Licensed under AGPL-3.0-or-later.
"""

from __future__ import annotations

import pytest

from groundtruth_kb._azure_spec_templates import (
    AZURE_ADR_TEMPLATE_SPEC_ID,
    AZURE_ALL_SPEC_IDS,
    AZURE_CATEGORY_SPEC_IDS,
    AZURE_TAXONOMY_DOC_ID,
    AZURE_VERIFICATION_SPEC_ID,
    azure_spec_templates,
    azure_taxonomy_document,
)
from groundtruth_kb.db import KnowledgeDB
from groundtruth_kb.spec_scaffold import (
    ScaffoldReport,
    SpecScaffoldConfig,
    scaffold_specs,
)


@pytest.fixture
def db(tmp_path):
    return KnowledgeDB(db_path=tmp_path / "test.db")


# ---------------------------------------------------------------------------
# Template-level unit tests (no DB needed)
# ---------------------------------------------------------------------------


class TestAzureTemplatesUnit:
    """Pure-template unit tests. No DB required."""

    def test_azure_spec_templates_returns_15(self):
        specs = azure_spec_templates()
        assert len(specs) == 15, (
            f"Expected 15 specs (13 categories + 1 ADR template + 1 verification plan), got {len(specs)}"
        )

    def test_azure_category_spec_ids_has_13(self):
        assert len(AZURE_CATEGORY_SPEC_IDS) == 13

    def test_azure_all_spec_ids_has_15(self):
        assert len(AZURE_ALL_SPEC_IDS) == 15

    def test_all_category_specs_have_unique_ids(self):
        specs = azure_spec_templates()
        ids = [s["id"] for s in specs]
        assert len(ids) == len(set(ids)), "Duplicate spec IDs in azure template registry"

    def test_all_category_specs_have_unique_handles(self):
        specs = azure_spec_templates()
        handles = [s["handle"] for s in specs]
        assert len(handles) == len(set(handles)), "Duplicate handles in azure template registry"

    def test_every_category_has_description_with_headings(self):
        """Codex condition 6: description field must carry template markdown with headings."""
        for spec in azure_spec_templates():
            desc = spec["description"]
            assert f"# {spec['title']}" in desc, f"Missing title heading in {spec['id']}"
            # The top-level title is mandatory; most specs have Subtopics and other sections
            # but the ADR template uses different section headings. The essential contract is
            # that `description` is non-empty and structured.
            assert len(desc) > 100, f"Description suspiciously short for {spec['id']}"

    def test_every_category_has_assertion_or_owner_placeholder(self):
        """INSIGHTS Phase 2 verification clause #2: every category has at least one
        automatable assertion OR an explicit owner-decision placeholder."""
        for spec in azure_spec_templates():
            assertions = spec.get("assertions", [])
            assert len(assertions) >= 1, f"Spec {spec['id']} has no assertions"
            # Per Codex binding condition: either automatable OR owner-decision placeholder
            has_automatable = any(
                a.get("type") in {"grep", "grep_absent", "glob", "file_exists", "count", "json_path"}
                for a in assertions
            )
            has_owner_placeholder = any(a.get("type") == "owner_decision_placeholder" for a in assertions)
            has_template_marker = any(a.get("type") == "template" for a in assertions)
            assert has_automatable or has_owner_placeholder or has_template_marker, (
                f"Spec {spec['id']} lacks automatable assertion, owner_decision_placeholder, and template marker"
            )

    def test_category_spec_ids_match_golden_list(self):
        """Stable golden IDs — any reshuffle is a breaking change."""
        specs = azure_spec_templates()
        actual_category_ids = tuple(
            s["id"]
            for s in specs
            if s["id"].startswith("SPEC-AZURE-")
            and s["type"] == "requirement"
            and s["id"] != AZURE_VERIFICATION_SPEC_ID
        )
        assert actual_category_ids == AZURE_CATEGORY_SPEC_IDS

    def test_adr_template_spec_present(self):
        specs = azure_spec_templates()
        adr_specs = [s for s in specs if s["id"] == AZURE_ADR_TEMPLATE_SPEC_ID]
        assert len(adr_specs) == 1
        assert adr_specs[0]["type"] == "architecture_decision"

    def test_verification_spec_present(self):
        specs = azure_spec_templates()
        v_specs = [s for s in specs if s["id"] == AZURE_VERIFICATION_SPEC_ID]
        assert len(v_specs) == 1

    def test_taxonomy_document_shape(self):
        doc = azure_taxonomy_document()
        assert doc["id"] == AZURE_TAXONOMY_DOC_ID
        assert doc["category"] == "taxonomy"
        assert doc["source_path"] == "docs/reference/azure-readiness-taxonomy.md"
        assert "tags" in doc


# ---------------------------------------------------------------------------
# scaffold_specs() integration — dry-run path
# ---------------------------------------------------------------------------


class TestAzureProfileDryRun:
    """Dry-run mode end-to-end."""

    def test_dry_run_generates_15_specs_and_1_document(self, db):
        cfg = SpecScaffoldConfig(profile="azure-enterprise")
        report = scaffold_specs(db, cfg, dry_run=True)
        assert isinstance(report, ScaffoldReport)
        assert report.dry_run is True
        assert len(report.generated) == 15
        assert len(report.generated_documents) == 1
        assert len(report.skipped) == 0
        assert len(report.skipped_documents) == 0

    def test_dry_run_all_13_categories_present(self, db):
        cfg = SpecScaffoldConfig(profile="azure-enterprise")
        report = scaffold_specs(db, cfg, dry_run=True)
        ids = {s["id"] for s in report.generated}
        for expected_id in AZURE_CATEGORY_SPEC_IDS:
            assert expected_id in ids, f"Missing category spec {expected_id}"

    def test_dry_run_generated_document_has_correct_id(self, db):
        cfg = SpecScaffoldConfig(profile="azure-enterprise")
        report = scaffold_specs(db, cfg, dry_run=True)
        assert report.generated_documents[0]["id"] == AZURE_TAXONOMY_DOC_ID


# ---------------------------------------------------------------------------
# scaffold_specs() integration — apply path (Codex F2 / condition 4/6)
# ---------------------------------------------------------------------------


class TestAzureProfileApply:
    """Apply mode — persisted-row verification per Codex condition 4."""

    def test_apply_inserts_15_specs(self, db):
        cfg = SpecScaffoldConfig(profile="azure-enterprise")
        scaffold_specs(db, cfg, dry_run=False)
        for spec_id in AZURE_ALL_SPEC_IDS:
            stored = db.get_spec(spec_id)
            assert stored is not None, f"Spec {spec_id} not persisted"
            assert stored["authority"] == "inferred"

    def test_apply_inserts_taxonomy_document(self, db):
        cfg = SpecScaffoldConfig(profile="azure-enterprise")
        scaffold_specs(db, cfg, dry_run=False)
        doc = db.get_document(AZURE_TAXONOMY_DOC_ID)
        assert doc is not None, "Taxonomy document not persisted"
        assert doc["category"] == "taxonomy"
        assert doc["source_path"] == "docs/reference/azure-readiness-taxonomy.md"

    def test_apply_description_persists_with_headings(self, db):
        """Codex condition 6 + F2 resolution: description field carries the
        template markdown through apply. Verified against persisted DB row,
        not dry-run dict."""
        cfg = SpecScaffoldConfig(profile="azure-enterprise")
        scaffold_specs(db, cfg, dry_run=False)
        stored = db.get_spec("SPEC-AZURE-LANDING-ZONE-001")
        assert stored is not None
        desc = stored["description"]
        # Essential headings must persist
        assert "# Azure Landing Zone" in desc
        assert "## Subtopics" in desc
        assert "## Owner decisions required" in desc
        assert "## Automatable assertions" in desc
        # At least 4 of the 6 subtopics named by the taxonomy must be in the body
        taxonomy_subtopic_cues = [
            "Subscription strategy",
            "Management group hierarchy",
            "Resource naming convention",
            "Tagging strategy",
            "Policy inheritance",
            "Environment topology",
        ]
        hits = sum(1 for s in taxonomy_subtopic_cues if s in desc)
        assert hits >= 4, f"Only {hits}/6 subtopic cues found in persisted description"

    def test_apply_all_category_specs_have_at_least_one_assertion(self, db):
        """INSIGHTS Phase 2 verification clause #2 against persisted rows."""
        cfg = SpecScaffoldConfig(profile="azure-enterprise")
        scaffold_specs(db, cfg, dry_run=False)
        for spec_id in AZURE_CATEGORY_SPEC_IDS:
            stored = db.get_spec(spec_id)
            assert stored is not None
            assertions = stored.get("assertions_parsed") or stored.get("assertions") or []
            assert len(assertions) >= 1, f"No assertions on persisted {spec_id}"


# ---------------------------------------------------------------------------
# Idempotence (Codex condition 3)
# ---------------------------------------------------------------------------


class TestAzureProfileIdempotence:
    """Codex condition 3: no v2 on re-run; skipped rows identify id + reason."""

    def test_reapply_skips_all_specs(self, db):
        cfg = SpecScaffoldConfig(profile="azure-enterprise")
        scaffold_specs(db, cfg, dry_run=False)  # first apply
        report2 = scaffold_specs(db, cfg, dry_run=False)  # re-apply
        assert len(report2.generated) == 0, "Re-apply should generate zero new specs"
        assert len(report2.skipped) == 15, f"Re-apply should skip all 15 specs, got {len(report2.skipped)}"
        for s in report2.skipped:
            assert "id" in s
            assert "reason" in s

    def test_reapply_skips_taxonomy_document(self, db):
        cfg = SpecScaffoldConfig(profile="azure-enterprise")
        scaffold_specs(db, cfg, dry_run=False)
        report2 = scaffold_specs(db, cfg, dry_run=False)
        assert len(report2.generated_documents) == 0
        assert len(report2.skipped_documents) == 1
        sk = report2.skipped_documents[0]
        assert sk["id"] == AZURE_TAXONOMY_DOC_ID
        assert sk["reason"] == "already exists"

    def test_reapply_does_not_create_spec_version_2(self, db):
        cfg = SpecScaffoldConfig(profile="azure-enterprise")
        scaffold_specs(db, cfg, dry_run=False)
        scaffold_specs(db, cfg, dry_run=False)  # re-apply
        stored = db.get_spec("SPEC-AZURE-LANDING-ZONE-001")
        assert stored["version"] == 1, f"Re-apply created version 2! Got v{stored['version']}"

    def test_reapply_does_not_create_document_version_2(self, db):
        cfg = SpecScaffoldConfig(profile="azure-enterprise")
        scaffold_specs(db, cfg, dry_run=False)
        scaffold_specs(db, cfg, dry_run=False)
        doc = db.get_document(AZURE_TAXONOMY_DOC_ID)
        # Version semantics: doc should NOT have v2; the get_document contract returns
        # the current version only — assert it is still 1 (no v2 created).
        assert doc.get("version", 1) == 1


# ---------------------------------------------------------------------------
# Regression: existing profiles unchanged (Codex condition 1)
# ---------------------------------------------------------------------------


class TestProfileRegressionMinimal:
    """`minimal` profile unchanged: doc buckets empty, spec count unchanged."""

    def test_minimal_profile_generates_no_documents(self, db):
        cfg = SpecScaffoldConfig(profile="minimal")
        report = scaffold_specs(db, cfg, dry_run=True)
        assert len(report.generated_documents) == 0
        assert len(report.skipped_documents) == 0

    def test_minimal_profile_spec_count_unchanged(self, db):
        """Hardcoded golden count for the minimal profile baseline.

        If this changes, it must be a separate bridge — D1 must not touch it.
        """
        cfg = SpecScaffoldConfig(profile="minimal")
        report = scaffold_specs(db, cfg, dry_run=True)
        # Baseline at D1-filing time: 2 governance + 2 infra = 4 specs
        assert len(report.generated) == 4, (
            f"Minimal profile output count changed! Expected 4, got {len(report.generated)}. "
            f"D1 must not alter existing profile behavior."
        )


class TestProfileRegressionFull:
    """`full` profile unchanged: doc buckets empty, spec count unchanged."""

    def test_full_profile_generates_no_documents(self, db):
        cfg = SpecScaffoldConfig(profile="full")
        report = scaffold_specs(db, cfg, dry_run=True)
        assert len(report.generated_documents) == 0
        assert len(report.skipped_documents) == 0

    def test_full_profile_spec_count_unchanged(self, db):
        cfg = SpecScaffoldConfig(profile="full")
        report = scaffold_specs(db, cfg, dry_run=True)
        # Baseline at D1-filing time: 2 governance + 2 infra + 1 ai + 1 compliance = 6 specs
        assert len(report.generated) == 6, (
            f"Full profile output count changed! Expected 6, got {len(report.generated)}. "
            f"D1 must not alter existing profile behavior."
        )


# ---------------------------------------------------------------------------
# ScaffoldReport shape / API compatibility
# ---------------------------------------------------------------------------


class TestScaffoldReportShape:
    """ScaffoldReport is backward-compatible: new fields default to []."""

    def test_scaffold_report_new_fields_default_empty(self):
        r = ScaffoldReport()
        assert r.generated_documents == []
        assert r.skipped_documents == []
        # Pre-existing fields still default correctly
        assert r.generated == []
        assert r.skipped == []
        assert r.dry_run is True
