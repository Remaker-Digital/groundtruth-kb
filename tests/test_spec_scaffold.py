# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Tests for F6: Specification Scaffold Generator.

Organized per Phase 4 revised v4 proposal scope (10 tests total):

Phase A (4): minimal config, full config, pre-existing handle skip, dry-run default
Phase B (2): authority='inferred', owner promotion via update_spec
F3 Quality Validation (3): quality_summary, low_quality_warnings, NO_ASSERTIONS fix
Integration (1): scaffold_project with ScaffoldOptions.spec_scaffold

Copyright (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
Licensed under AGPL-3.0-or-later.
"""

from __future__ import annotations

import pytest

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
# Phase A — Core scaffold generator semantics
# ---------------------------------------------------------------------------


class TestF6PhaseA:
    """Phase A: minimal/full profile, pre-existing skip, dry-run default."""

    # ------------------------------------------------------------------
    # 1. Minimal config — dry run returns governance + infra only
    # ------------------------------------------------------------------
    def test_minimal_config_generates_governance_and_infra(self, db):
        """Minimal profile (default) generates governance + infrastructure
        specs but NOT ai_components or compliance."""
        config = SpecScaffoldConfig(profile="minimal")
        report = scaffold_specs(db, config, dry_run=True)

        assert isinstance(report, ScaffoldReport)
        assert report.dry_run is True

        sections = {spec["section"] for spec in report.generated}
        assert "governance" in sections
        assert "infrastructure" in sections
        assert "ai_components" not in sections
        assert "compliance" not in sections

    # ------------------------------------------------------------------
    # 2. Full config — dry run returns all phases
    # ------------------------------------------------------------------
    def test_full_config_generates_all_phases(self, db):
        """Full profile generates governance + infra + ai_components + compliance."""
        config = SpecScaffoldConfig(profile="full")
        report = scaffold_specs(db, config, dry_run=True)

        sections = {spec["section"] for spec in report.generated}
        assert "governance" in sections
        assert "infrastructure" in sections
        assert "ai_components" in sections
        assert "compliance" in sections

    # ------------------------------------------------------------------
    # 3. Pre-existing handle is skipped, others generated
    # ------------------------------------------------------------------
    def test_preexisting_handle_is_skipped(self, db):
        """A spec with a handle that already exists in the KB is skipped
        (not overwritten), while other handles are generated normally."""
        # Seed a pre-existing spec with the handle that governance template #1 uses.
        db.insert_spec(
            id="PRE-EXISTING-01",
            title="Pre-existing test discipline rule",
            status="implemented",
            handle="test-discipline",
            changed_by="owner",
            change_reason="seeded before scaffold run",
        )

        config = SpecScaffoldConfig(profile="minimal")
        report = scaffold_specs(db, config, dry_run=False)

        skipped_handles = {s["handle"] for s in report.skipped}
        assert "test-discipline" in skipped_handles

        generated_handles = {s.get("handle") for s in report.generated}
        assert "test-discipline" not in generated_handles
        # Other minimal handles should still be generated:
        assert "readme-exists" in generated_handles
        assert "ci-config" in generated_handles

    # ------------------------------------------------------------------
    # 4. Dry-run default writes nothing
    # ------------------------------------------------------------------
    def test_dry_run_is_default_and_writes_nothing(self, db):
        """scaffold_specs(db, config) with no dry_run kwarg defaults to
        dry_run=True and must not persist anything to the database."""
        config = SpecScaffoldConfig(profile="minimal")
        report = scaffold_specs(db, config)  # no dry_run kwarg

        assert report.dry_run is True
        assert len(report.generated) > 0

        # Nothing should be in the DB.
        assert db.list_specs() == []


# ---------------------------------------------------------------------------
# Phase B — Authority lifecycle (inferred → stated promotion)
# ---------------------------------------------------------------------------


class TestF6PhaseB:
    """Phase B: generated specs use authority='inferred' until owner promotes."""

    # ------------------------------------------------------------------
    # 5. Generated specs have authority='inferred'
    # ------------------------------------------------------------------
    def test_generated_specs_have_authority_inferred(self, db):
        """Apply mode: every spec inserted by scaffold_specs must have
        authority='inferred' so owners can distinguish generated specs
        from authoritative (stated) ones."""
        config = SpecScaffoldConfig(profile="full")
        report = scaffold_specs(db, config, dry_run=False)

        assert not report.dry_run
        assert len(report.generated) > 0

        for spec_entry in report.generated:
            stored = db.get_spec(spec_entry["id"])
            assert stored is not None
            assert stored["authority"] == "inferred", (
                f"Spec {spec_entry['id']} has authority {stored['authority']!r} but expected 'inferred'"
            )

    # ------------------------------------------------------------------
    # 6. Owner promotion to 'stated' via update_spec creates new version
    # ------------------------------------------------------------------
    def test_owner_promotion_to_stated_creates_new_version(self, db):
        """After scaffold, an owner can promote an inferred spec to stated
        by calling db.update_spec(authority='stated'). The update must
        create a new version while preserving lineage."""
        config = SpecScaffoldConfig(profile="minimal")
        report = scaffold_specs(db, config, dry_run=False)

        target = report.generated[0]["id"]
        original = db.get_spec(target)
        assert original["authority"] == "inferred"
        assert original["version"] == 1

        db.update_spec(
            id=target,
            changed_by="owner",
            change_reason="promote scaffold spec to stated after review",
            authority="stated",
        )

        promoted = db.get_spec(target)
        assert promoted["authority"] == "stated"
        assert promoted["version"] == 2  # new version created


# ---------------------------------------------------------------------------
# F3 Quality Validation — dry-run quality scoring, summary, warnings
# ---------------------------------------------------------------------------


class TestF6QualityValidation:
    """F3 integration: quality scoring during scaffold runs."""

    # ------------------------------------------------------------------
    # 7. quality_summary populated on apply
    # ------------------------------------------------------------------
    def test_quality_summary_populated_on_apply(self, db):
        """After a non-dry-run scaffold, ScaffoldReport.quality_summary
        must contain tier counts that sum to the number of generated
        specs."""
        config = SpecScaffoldConfig(profile="full")
        report = scaffold_specs(db, config, dry_run=False)

        assert isinstance(report.quality_summary, dict)
        total_in_summary = sum(report.quality_summary.values())
        assert total_in_summary == len(report.generated)
        # At least one tier should be populated.
        assert total_in_summary > 0

    # ------------------------------------------------------------------
    # 8. low_quality_warnings populated for bronze/needs-work tiers
    # ------------------------------------------------------------------
    def test_low_quality_warnings_structure(self, db):
        """low_quality_warnings is a list of {id, tier, score} dicts and
        only contains specs at bronze or needs-work tier."""
        config = SpecScaffoldConfig(profile="full")
        report = scaffold_specs(db, config, dry_run=True)

        assert isinstance(report.low_quality_warnings, list)
        for warning in report.low_quality_warnings:
            assert "id" in warning
            assert "tier" in warning
            assert warning["tier"] in ("bronze", "needs-work")

    # ------------------------------------------------------------------
    # 9. Dry-run quality scoring does NOT fire NO_ASSERTIONS false-positive
    # ------------------------------------------------------------------
    def test_dry_run_quality_scores_executable_assertions(self, db):
        """Regression test for NO-GO -004 Finding 3: dry-run synthetic specs
        must populate `_assertions_parsed` before calling
        `score_spec_quality()` so executable assertions are recognized.

        With the fix, at least one generated spec has machine-executable
        assertions (grep/glob/file_exists/etc.) and its quality result
        must NOT contain the NO_ASSERTIONS flag."""
        config = SpecScaffoldConfig(profile="minimal")
        report = scaffold_specs(db, config, dry_run=True)

        # Find a generated spec that has executable assertions in the template.
        specs_with_executable_assertions = [
            s
            for s in report.generated
            if s.get("assertions")
            and any(
                isinstance(a, dict)
                and a.get("type")
                in {
                    "grep",
                    "glob",
                    "grep_absent",
                    "file_exists",
                    "count",
                    "json_path",
                    "all_of",
                    "any_of",
                }
                for a in s["assertions"]
            )
        ]
        assert len(specs_with_executable_assertions) > 0, (
            "Scaffold should generate at least one spec with executable assertions to exercise this code path"
        )

        for spec in specs_with_executable_assertions:
            quality = spec.get("quality", {})
            flags = quality.get("flags", [])
            assert "NO_ASSERTIONS" not in flags, (
                f"Spec {spec['id']} has executable assertions but dry-run "
                f"quality scoring flagged NO_ASSERTIONS — synthetic dict did "
                f"not populate _assertions_parsed correctly. flags={flags}"
            )
            assert "NO_EXECUTABLE_ASSERTIONS" not in flags
            assert quality.get("tier") is not None


# ---------------------------------------------------------------------------
# Integration — scaffold_project wiring
# ---------------------------------------------------------------------------


class TestF6Integration:
    """F6 integrates into the existing scaffold_project() entry point."""

    # ------------------------------------------------------------------
    # 10. scaffold_project(ScaffoldOptions(spec_scaffold=...)) populates KB
    # ------------------------------------------------------------------
    def test_scaffold_project_with_spec_scaffold_populates_kb(self, tmp_path):
        """When ScaffoldOptions carries a non-None spec_scaffold config,
        scaffold_project() populates the newly-created KB with generated
        specs at authority='inferred' (post-_seed_database). Default
        gt project init behavior (spec_scaffold=None) is unchanged."""
        from groundtruth_kb.project.scaffold import ScaffoldOptions, scaffold_project

        target = tmp_path / "new_project"
        options = ScaffoldOptions(
            project_name="test-scaffold",
            profile="local-only",
            owner="Test Owner",
            target_dir=target,
            init_git=False,
            include_ci=False,
            seed_example=False,
            spec_scaffold=SpecScaffoldConfig(profile="minimal"),
        )

        created = scaffold_project(options)
        assert created == target.resolve()

        # Open the new project's KB and confirm scaffold specs landed.
        new_db = KnowledgeDB(db_path=created / "groundtruth.db")
        try:
            scaffold_handles = {"test-discipline", "readme-exists", "ci-config", "no-aws-keys"}
            all_handles = {spec.get("handle") for spec in new_db.list_specs() if spec.get("handle")}
            # At least the minimal scaffold handles should be present.
            assert scaffold_handles.issubset(all_handles), f"Expected {scaffold_handles} ⊆ {all_handles}"

            # And they should all be authority='inferred'.
            for handle in scaffold_handles:
                specs = new_db.list_specs(handle=handle)
                assert len(specs) == 1
                assert specs[0]["authority"] == "inferred"
        finally:
            new_db.close()
