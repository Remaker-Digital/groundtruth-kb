# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Tests for D2 Azure ADR instance scaffold (`gt scaffold adrs --profile azure-enterprise`).

Covers Codex binding conditions F1, F3, F6, F7 from
bridge/gtkb-azure-adr-template-activation-002.md GO:

F1 — ADR IDs match `ADR-AZURE-{CATEGORY}-001` format, one-to-one with
     `AZURE_CATEGORY_SPEC_IDS` from D1.
F3 — Separate scaffold subcommand; regression on D1 scaffold specs.
F6 — Scope boundary: no IaC, CI, doctor, Azure SDK, Agent Red writes.
F7 — Idempotence + persisted-row tests (dry-run no write; apply inserts 13;
     re-apply skips by handle, no v2; apply-mode assertions via
     `db.get_spec(id)["description"]`).

Harness-specific conditions (F2, F4, F5) are covered in
test_adr_harness_azure.py.

Copyright (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
Licensed under AGPL-3.0-or-later.
"""

from __future__ import annotations

import pytest

from groundtruth_kb._azure_adr_instance_templates import (
    ADR_MANDATORY_OWNER_ANSWER_HEADINGS,
    ADR_PLACEHOLDER,
    ADR_REQUIRED_HEADINGS,
    AZURE_ADR_INSTANCE_IDS,
    azure_adr_instance_templates,
)
from groundtruth_kb._azure_spec_templates import AZURE_CATEGORY_SPEC_IDS
from groundtruth_kb.adr_scaffold import (
    AdrScaffoldConfig,
    AdrScaffoldReport,
    scaffold_adrs,
)
from groundtruth_kb.db import KnowledgeDB
from groundtruth_kb.spec_scaffold import (
    SpecScaffoldConfig,
    scaffold_specs,
)


@pytest.fixture
def db(tmp_path):
    return KnowledgeDB(db_path=tmp_path / "test.db")


# ---------------------------------------------------------------------------
# Template unit tests (F1)
# ---------------------------------------------------------------------------


class TestAdrTemplatesUnit:
    """F1: ID format + pairing + unique IDs/handles."""

    def test_returns_13_adr_skeletons(self):
        adrs = azure_adr_instance_templates()
        assert len(adrs) == 13

    def test_azure_adr_instance_ids_has_13(self):
        assert len(AZURE_ADR_INSTANCE_IDS) == 13

    def test_one_to_one_pairing_with_d1_category_specs(self):
        """F1: ADR IDs pair one-to-one with D1 SPEC-AZURE-{CATEGORY}-001 IDs."""
        assert len(AZURE_ADR_INSTANCE_IDS) == len(AZURE_CATEGORY_SPEC_IDS)
        # Extract the {CATEGORY} slug from each ID in both registries.
        adr_slugs = [adr_id.removeprefix("ADR-AZURE-").removesuffix("-001") for adr_id in AZURE_ADR_INSTANCE_IDS]
        spec_slugs = [spec_id.removeprefix("SPEC-AZURE-").removesuffix("-001") for spec_id in AZURE_CATEGORY_SPEC_IDS]
        assert adr_slugs == spec_slugs

    def test_unique_ids(self):
        adrs = azure_adr_instance_templates()
        ids = [a["id"] for a in adrs]
        assert len(ids) == len(set(ids))

    def test_unique_handles(self):
        adrs = azure_adr_instance_templates()
        handles = [a["handle"] for a in adrs]
        assert len(handles) == len(set(handles))

    def test_all_have_type_architecture_decision(self):
        for adr in azure_adr_instance_templates():
            assert adr["type"] == "architecture_decision"

    def test_every_adr_description_contains_all_9_headings(self):
        """F4 preparation: all 9 taxonomy §5.1 headings must be present."""
        for adr in azure_adr_instance_templates():
            desc = adr["description"]
            for heading in ADR_REQUIRED_HEADINGS:
                assert f"## {heading}" in desc, f"{adr['id']} missing heading '{heading}'"

    def test_every_adr_mandatory_sections_contain_placeholder(self):
        """F4 preparation: Decision + Rationale + Rejected alternatives must start
        with placeholder (adopter replaces these)."""
        for adr in azure_adr_instance_templates():
            desc = adr["description"]
            for heading in ADR_MANDATORY_OWNER_ANSWER_HEADINGS:
                assert f"## {heading}" in desc
            # Placeholder appears at least 3 times (one per mandatory section).
            assert desc.count(ADR_PLACEHOLDER) >= 3, (
                f"{adr['id']} has {desc.count(ADR_PLACEHOLDER)} placeholders, expected ≥3"
            )


# ---------------------------------------------------------------------------
# scaffold_adrs() integration — dry-run (F7)
# ---------------------------------------------------------------------------


class TestAdrScaffoldDryRun:
    def test_dry_run_generates_13(self, db):
        cfg = AdrScaffoldConfig(profile="azure-enterprise")
        report = scaffold_adrs(db, cfg, dry_run=True)
        assert isinstance(report, AdrScaffoldReport)
        assert report.dry_run is True
        assert len(report.generated) == 13
        assert len(report.skipped) == 0

    def test_dry_run_does_not_write_to_db(self, db):
        cfg = AdrScaffoldConfig(profile="azure-enterprise")
        scaffold_adrs(db, cfg, dry_run=True)
        # No ADR should be persisted.
        for adr_id in AZURE_ADR_INSTANCE_IDS:
            assert db.get_spec(adr_id) is None

    def test_dry_run_includes_all_13_expected_ids(self, db):
        cfg = AdrScaffoldConfig(profile="azure-enterprise")
        report = scaffold_adrs(db, cfg, dry_run=True)
        ids = {a["id"] for a in report.generated}
        for expected in AZURE_ADR_INSTANCE_IDS:
            assert expected in ids

    def test_unsupported_profile_raises(self, db):
        cfg = AdrScaffoldConfig(profile="not-a-profile")
        with pytest.raises(ValueError, match="Unsupported profile"):
            scaffold_adrs(db, cfg, dry_run=True)


# ---------------------------------------------------------------------------
# scaffold_adrs() integration — apply + persisted-row verification (F7)
# ---------------------------------------------------------------------------


class TestAdrScaffoldApply:
    def test_apply_inserts_13_specs(self, db):
        cfg = AdrScaffoldConfig(profile="azure-enterprise")
        scaffold_adrs(db, cfg, dry_run=False)
        for adr_id in AZURE_ADR_INSTANCE_IDS:
            stored = db.get_spec(adr_id)
            assert stored is not None, f"{adr_id} not persisted"
            assert stored["authority"] == "inferred"

    def test_apply_persisted_description_contains_all_9_headings(self, db):
        """F7: apply-mode tests query persisted rows via db.get_spec()['description']."""
        cfg = AdrScaffoldConfig(profile="azure-enterprise")
        scaffold_adrs(db, cfg, dry_run=False)
        for adr_id in AZURE_ADR_INSTANCE_IDS:
            stored = db.get_spec(adr_id)
            assert stored is not None
            desc = stored["description"]
            for heading in ADR_REQUIRED_HEADINGS:
                assert f"## {heading}" in desc, f"{adr_id} missing {heading} in persisted description"

    def test_apply_persisted_description_contains_placeholder(self, db):
        cfg = AdrScaffoldConfig(profile="azure-enterprise")
        scaffold_adrs(db, cfg, dry_run=False)
        stored = db.get_spec("ADR-AZURE-LANDING-ZONE-001")
        assert stored is not None
        assert ADR_PLACEHOLDER in stored["description"]

    def test_apply_persisted_type_is_architecture_decision(self, db):
        """ADR- prefix triggers auto-classification; also explicit type=architecture_decision."""
        cfg = AdrScaffoldConfig(profile="azure-enterprise")
        scaffold_adrs(db, cfg, dry_run=False)
        stored = db.get_spec("ADR-AZURE-IDENTITY-001")
        assert stored is not None
        assert stored["type"] == "architecture_decision"


# ---------------------------------------------------------------------------
# Idempotence (F7)
# ---------------------------------------------------------------------------


class TestAdrScaffoldIdempotence:
    def test_reapply_skips_all_13(self, db):
        cfg = AdrScaffoldConfig(profile="azure-enterprise")
        scaffold_adrs(db, cfg, dry_run=False)
        report2 = scaffold_adrs(db, cfg, dry_run=False)
        assert len(report2.generated) == 0
        assert len(report2.skipped) == 13
        for s in report2.skipped:
            assert "id" in s
            assert "handle" in s
            assert "reason" in s

    def test_reapply_does_not_create_version_2(self, db):
        cfg = AdrScaffoldConfig(profile="azure-enterprise")
        scaffold_adrs(db, cfg, dry_run=False)
        scaffold_adrs(db, cfg, dry_run=False)  # re-apply
        stored = db.get_spec("ADR-AZURE-LANDING-ZONE-001")
        assert stored is not None
        assert stored["version"] == 1


# ---------------------------------------------------------------------------
# Regression: D1 scaffold specs unchanged (F3)
# ---------------------------------------------------------------------------


class TestD1RegressionUnchanged:
    """F3: Preserve D1 behavior. D2 scaffold path must not touch D1 output."""

    def test_minimal_spec_scaffold_count_unchanged(self, db):
        cfg = SpecScaffoldConfig(profile="minimal")
        report = scaffold_specs(db, cfg, dry_run=True)
        assert len(report.generated) == 4  # D1 baseline golden count

    def test_full_spec_scaffold_count_unchanged(self, db):
        cfg = SpecScaffoldConfig(profile="full")
        report = scaffold_specs(db, cfg, dry_run=True)
        assert len(report.generated) == 6

    def test_azure_enterprise_spec_scaffold_unchanged(self, db):
        cfg = SpecScaffoldConfig(profile="azure-enterprise")
        report = scaffold_specs(db, cfg, dry_run=True)
        assert len(report.generated) == 15
        assert len(report.generated_documents) == 1
