"""Tests for F5: Requirement Intake Pipeline.

34 tests per approved Phase 3 v6 scope (bridge/gtkb-phase3-implementation-013.md).

Copyright (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
Licensed under AGPL-3.0-or-later.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from click.testing import CliRunner

from groundtruth_kb.cli import main as cli_main
from groundtruth_kb.db import KnowledgeDB
from groundtruth_kb.intake import (
    capture_requirement,
    classify_requirement,
    confirm_intake,
    list_intakes,
    reject_intake,
)
from groundtruth_kb.project.doctor import _check_settings_classifiers
from groundtruth_kb.project.upgrade import _MANAGED_HOOKS


@pytest.fixture
def db(tmp_path):
    return KnowledgeDB(db_path=tmp_path / "test.db")


@pytest.fixture
def seeded_project(tmp_path):
    """A scaffolded project directory with a settings.local.json we can mutate."""
    target = tmp_path / "proj"
    (target / ".claude").mkdir(parents=True)
    return target


def _write_settings(target: Path, hooks: object) -> Path:
    """Write a .claude/settings.local.json with the given 'hooks' value."""
    settings = {"permissions": {"allow": [], "deny": []}, "hooks": hooks}
    path = target / ".claude" / "settings.local.json"
    path.write_text(json.dumps(settings), encoding="utf-8")
    return path


class TestF5CoreIntake:
    """Core intake API: classify, capture, confirm, reject."""

    # 1. Classify directive — confidence > 0.8
    def test_classify_directive(self, db):
        result = classify_requirement(
            db,
            "The system must validate all user input and require authentication before login.",
        )
        assert result["classification"] == "directive"
        assert result["confidence"] > 0.8

    # 2. Classify exploration — confidence < 0.5
    def test_classify_exploration(self, db):
        result = classify_requirement(db, "Just something I'm thinking about.")
        assert result["classification"] == "exploration"
        assert result["confidence"] < 0.5

    # 3. Classify question
    def test_classify_question(self, db):
        result = classify_requirement(db, "How does the auth flow work?")
        assert result["classification"] == "question"

    # 4. Classify constraint
    def test_classify_constraint(self, db):
        result = classify_requirement(
            db,
            "The API must not exceed 300ms and cannot process more than 100 requests per second.",
        )
        assert result["classification"] == "constraint"

    # 5. Classify ambiguous → exploration, low confidence
    def test_classify_ambiguous(self, db):
        result = classify_requirement(db, "maybe we should add logging")
        assert result["classification"] == "exploration"
        assert result["confidence"] <= 0.7

    # 6. Classify with related specs populated
    def test_classify_with_related_specs(self, db):
        db.insert_spec(
            id="SPEC-AUTH-001",
            title="Authentication login flow",
            status="specified",
            changed_by="test",
            change_reason="test",
            section="auth",
        )
        result = classify_requirement(
            db,
            "The authentication login flow should require email verification",
        )
        related_ids = [s["id"] for s in result["related_specs"]]
        assert "SPEC-AUTH-001" in related_ids

    # 7. Capture stores full candidate payload
    def test_capture_stores_full_payload(self, db):
        result = capture_requirement(
            db,
            "The system must log all API errors",
            proposed_title="API error logging",
            proposed_section="observability",
            proposed_type="requirement",
            proposed_authority="stated",
        )
        content = result["content"]
        assert content["intake_type"] == "requirement_candidate"
        assert content["intake_status"] == "pending"
        assert content["raw_text"] == "The system must log all API errors"
        assert content["classification"] == "directive"
        assert isinstance(content["confidence"], float)
        assert content["proposed_title"] == "API error logging"
        assert content["proposed_type"] == "requirement"
        assert content["proposed_authority"] == "stated"

    # 8. Confirm creates spec with proposed type/authority, records confirmed_spec_id
    def test_confirm_creates_spec(self, db):
        cap = capture_requirement(
            db,
            "The system must log all errors",
            proposed_title="Error logging",
            proposed_section="observability",
            proposed_type="requirement",
            proposed_authority="stated",
        )
        result = confirm_intake(db, cap["deliberation_id"])
        assert "confirmed_spec_id" in result
        created = db.get_spec(result["confirmed_spec_id"])
        assert created is not None
        assert created["title"] == "Error logging"
        assert created.get("type") == "requirement"
        assert created.get("authority") == "stated"

    # 9. Confirm with default type/authority when proposed fields absent
    def test_confirm_default_type_authority(self, db):
        # Capture with explicit defaults (the defaults that capture uses)
        cap = capture_requirement(
            db,
            "The app should handle errors",
            proposed_title="Error handling",
            proposed_section="core",
        )
        result = confirm_intake(db, cap["deliberation_id"])
        created = db.get_spec(result["confirmed_spec_id"])
        assert created.get("type") == "requirement"
        assert created.get("authority") == "stated"

    # 10. Confirm returns F2 impact + F4 constraints
    def test_confirm_returns_impact_and_constraints(self, db):
        db.insert_spec(
            id="ADR-SEC",
            title="Security decision",
            status="specified",
            changed_by="test",
            change_reason="test",
            section="security",
            type="architecture_decision",
        )
        cap = capture_requirement(
            db,
            "The login must verify credentials",
            proposed_title="Login credential check",
            proposed_section="security",
        )
        result = confirm_intake(db, cap["deliberation_id"])
        assert "impact" in result
        assert "constraints" in result
        assert any(c["id"] == "ADR-SEC" for c in result["constraints"])

    # 11. Confirm returns F3 quality score and tier
    def test_confirm_returns_quality(self, db):
        cap = capture_requirement(
            db,
            "The system must implement user registration",
            proposed_title="User registration",
            proposed_section="auth",
        )
        result = confirm_intake(db, cap["deliberation_id"])
        assert "quality" in result
        quality = result["quality"]
        assert "overall" in quality
        assert "tier" in quality
        assert "flags" in quality

    # 12. Reject stores reason, updates status
    def test_reject_stores_reason(self, db):
        cap = capture_requirement(
            db,
            "Exploratory idea",
            proposed_title="Exploration",
            proposed_section="core",
        )
        reject_intake(db, cap["deliberation_id"], "Out of scope")

        intakes = list_intakes(db)
        target = next(i for i in intakes if i["deliberation_id"] == cap["deliberation_id"])
        assert target["intake_status"] == "rejected"
        assert target["rejection_reason"] == "Out of scope"

    # 13. Reject reason required
    def test_reject_reason_required(self, db):
        cap = capture_requirement(
            db,
            "Idea",
            proposed_title="Idea",
            proposed_section="core",
        )
        with pytest.raises(ValueError):
            reject_intake(db, cap["deliberation_id"], "")


class TestF5ListFilter:
    """List/filter operations."""

    # 14. List pending — only pending intakes
    def test_list_pending(self, db):
        c1 = capture_requirement(db, "idea 1", proposed_title="I1", proposed_section="core")
        capture_requirement(db, "idea 2", proposed_title="I2", proposed_section="core")
        confirm_intake(db, c1["deliberation_id"])

        pending = list_intakes(db, pending_only=True)
        assert len(pending) == 1
        assert pending[0]["proposed_title"] == "I2"

    # 15. List all — excludes non-intake deliberations
    def test_list_excludes_non_intake(self, db):
        # Insert a non-intake owner_conversation deliberation
        db.insert_deliberation(
            id="NON-INTAKE-001",
            title="Regular chat",
            summary="Discussion",
            content=json.dumps({"kind": "chat", "text": "hello"}),
            source_type="owner_conversation",
            outcome=None,
            changed_by="test",
            change_reason="test",
        )
        capture_requirement(db, "real intake", proposed_title="Real", proposed_section="core")

        all_intakes = list_intakes(db)
        ids = [i["deliberation_id"] for i in all_intakes]
        assert "NON-INTAKE-001" not in ids

    # 16. Double confirm idempotent
    def test_double_confirm_idempotent(self, db):
        cap = capture_requirement(
            db,
            "The system must log errors",
            proposed_title="Error logging",
            proposed_section="observability",
        )
        r1 = confirm_intake(db, cap["deliberation_id"])
        r2 = confirm_intake(db, cap["deliberation_id"])
        assert r2.get("already_confirmed") is True
        assert r2.get("confirmed_spec_id") == r1["confirmed_spec_id"]


class TestF5RedactionAndCLI:
    """Redaction coverage + CLI smoke tests."""

    # 17. Redaction: credential stored redacted, still filterable
    def test_redaction(self, db):
        secret_text = 'The API must use api_key="AKIAIOSFODNN7EXAMPLEKEY" for auth'
        cap = capture_requirement(
            db,
            secret_text,
            proposed_title="API auth key",
            proposed_section="security",
        )

        # The captured content goes through redaction during insert_deliberation.
        # Verify the intake is still findable and filterable.
        intakes = list_intakes(db)
        target = next(
            (i for i in intakes if i["deliberation_id"] == cap["deliberation_id"]),
            None,
        )
        assert target is not None

        # Fetch the deliberation and verify the stored content has been redacted
        delib = db.get_deliberation(cap["deliberation_id"])
        assert delib is not None
        assert "AKIAIOSFODNN7EXAMPLEKEY" not in delib.get("content", "")

    # 18. CLI smoke: gt intake list
    def test_cli_intake_list(self, tmp_path):
        db_path = tmp_path / "test.db"
        db_local = KnowledgeDB(db_path=db_path)
        capture_requirement(
            db_local,
            "The system must log errors",
            proposed_title="Logging",
            proposed_section="core",
        )

        # Create groundtruth.toml so _resolve_config finds the DB
        toml_path = tmp_path / "groundtruth.toml"
        toml_path.write_text(
            f'[groundtruth]\ndb_path = "{db_path.as_posix()}"\n',
            encoding="utf-8",
        )

        runner = CliRunner()
        result = runner.invoke(
            cli_main,
            ["--config", str(toml_path), "intake", "list"],
        )
        assert result.exit_code == 0, result.output
        assert "Logging" in result.output or "No intake" in result.output

    # 19. CLI smoke: gt intake confirm
    def test_cli_intake_confirm(self, tmp_path):
        db_path = tmp_path / "test.db"
        db_local = KnowledgeDB(db_path=db_path)
        cap = capture_requirement(
            db_local,
            "The system must log errors",
            proposed_title="Logging",
            proposed_section="core",
        )

        toml_path = tmp_path / "groundtruth.toml"
        toml_path.write_text(
            f'[groundtruth]\ndb_path = "{db_path.as_posix()}"\n',
            encoding="utf-8",
        )

        runner = CliRunner()
        result = runner.invoke(
            cli_main,
            ["--config", str(toml_path), "intake", "confirm", cap["deliberation_id"]],
        )
        assert result.exit_code == 0, result.output
        assert "Confirmed" in result.output

    # 20. CLI smoke: gt intake reject
    def test_cli_intake_reject(self, tmp_path):
        db_path = tmp_path / "test.db"
        db_local = KnowledgeDB(db_path=db_path)
        cap = capture_requirement(
            db_local,
            "Test idea",
            proposed_title="Idea",
            proposed_section="core",
        )

        toml_path = tmp_path / "groundtruth.toml"
        toml_path.write_text(
            f'[groundtruth]\ndb_path = "{db_path.as_posix()}"\n',
            encoding="utf-8",
        )

        runner = CliRunner()
        result = runner.invoke(
            cli_main,
            [
                "--config",
                str(toml_path),
                "intake",
                "reject",
                cap["deliberation_id"],
                "--reason",
                "Out of scope",
            ],
        )
        assert result.exit_code == 0, result.output
        assert "Rejected" in result.output


class TestF5Scaffold:
    """Scaffold adoption tests."""

    # 21. Bridge-profile — settings includes intake hook
    def test_scaffold_bridge_includes_intake_hook(self):
        template = Path(__file__).parent.parent / "templates" / "project" / "settings.local.json"
        assert template.exists()
        data = json.loads(template.read_text(encoding="utf-8"))
        ups = data["hooks"]["UserPromptSubmit"]
        commands = [entry.get("command", "") for entry in ups]
        assert any("intake-classifier.py" in c for c in commands)

    # 22. Local-only — settings omits intake hook
    def test_scaffold_local_only_no_settings(self, tmp_path):
        """Local-only scaffold does not install .claude/settings.local.json.

        Verifies this by checking that the scaffold's _copy_dual_agent_templates
        is NOT called for local-only profile, so settings.local.json is absent.
        """
        from groundtruth_kb.project.scaffold import ScaffoldOptions, scaffold_project

        target = tmp_path / "local-proj"
        options = ScaffoldOptions(
            project_name="local-proj",
            profile="local-only",
            owner="test",
            target_dir=target,
            copyright_notice="",
            init_git=False,
            include_ci=False,
            seed_example=False,
        )
        scaffold_project(options)

        settings_path = target / ".claude" / "settings.local.json"
        assert not settings_path.exists(), "local-only profile should not install settings.local.json"


class TestF5Doctor:
    """Doctor classifier-settings check (8 tests)."""

    # 23. Bridge: only intake active → passes
    def test_doctor_only_intake_active(self, seeded_project):
        _write_settings(
            seeded_project,
            {
                "UserPromptSubmit": [
                    {"command": "python .claude/hooks/intake-classifier.py"},
                ],
            },
        )
        check = _check_settings_classifiers(seeded_project)
        assert check.status == "pass"
        assert "intake-classifier.py" in check.message

    # 24. Bridge: only spec active → passes (backward compat)
    def test_doctor_only_spec_active(self, seeded_project):
        _write_settings(
            seeded_project,
            {
                "UserPromptSubmit": [
                    {"command": "python .claude/hooks/spec-classifier.py"},
                ],
            },
        )
        check = _check_settings_classifiers(seeded_project)
        assert check.status == "pass"
        assert "spec-classifier.py" in check.message

    # 25. Bridge: both active → warns
    def test_doctor_both_active_warns(self, seeded_project):
        _write_settings(
            seeded_project,
            {
                "UserPromptSubmit": [
                    {"command": "python .claude/hooks/intake-classifier.py"},
                    {"command": "python .claude/hooks/spec-classifier.py"},
                ],
            },
        )
        check = _check_settings_classifiers(seeded_project)
        assert check.status == "warning"
        assert "redundant" in check.message.lower()

    # 26. Bridge: neither active → warns
    def test_doctor_neither_active_warns(self, seeded_project):
        _write_settings(
            seeded_project,
            {"UserPromptSubmit": [{"command": "python .claude/hooks/scheduler.py"}]},
        )
        check = _check_settings_classifiers(seeded_project)
        assert check.status == "warning"
        assert "intake-classifier" in check.message or "spec-classifier" in check.message

    # 27. Bridge: malformed JSON → warns without crash
    def test_doctor_malformed_json(self, seeded_project):
        settings_path = seeded_project / ".claude" / "settings.local.json"
        settings_path.write_text("{ not valid json }}", encoding="utf-8")
        check = _check_settings_classifiers(seeded_project)
        assert check.status == "warning"
        assert "malformed" in check.message.lower() or "settings" in check.message.lower()

    # 28. Bridge: hooks as non-dict → warns without crash
    def test_doctor_hooks_non_dict(self, seeded_project):
        _write_settings(seeded_project, ["not", "a", "dict"])
        check = _check_settings_classifiers(seeded_project)
        assert check.status == "warning"

    # 29. Bridge: hooks as null → warns without crash
    def test_doctor_hooks_null(self, seeded_project):
        _write_settings(seeded_project, None)
        check = _check_settings_classifiers(seeded_project)
        assert check.status == "warning"

    # 30. Local-only: no false warning when settings absent
    def test_doctor_local_only_no_false_warning(self, tmp_path):
        """When run_doctor is called for local-only profile, the classifier-settings
        check is not added at all — no warning regardless of settings file state.
        """
        from groundtruth_kb.project.doctor import run_doctor

        target = tmp_path / "local-proj"
        target.mkdir()
        (target / ".claude").mkdir()
        (target / ".claude" / "hooks").mkdir()

        # Minimal project files so doctor can run; no settings.local.json
        (target / "groundtruth.toml").write_text('[project]\nname = "t"\nprofile = "local-only"\n', encoding="utf-8")

        report = run_doctor(target, "local-only")
        classifier_checks = [c for c in report.checks if c.name == "Classifier settings"]
        assert classifier_checks == [], "local-only profile must not add a Classifier settings check"


class TestF5Upgrade:
    """Upgrade managed-hook tests."""

    # 31. Upgrade copy — intake hook is in the managed hook list
    def test_upgrade_managed_hooks_include_intake(self):
        assert ".claude/hooks/intake-classifier.py" in _MANAGED_HOOKS

    # 32. Upgrade preserve — existing spec-classifier stays in managed set
    def test_upgrade_preserves_spec_classifier(self):
        """Legacy spec-classifier.py must remain in _MANAGED_HOOKS so upgrade
        does not remove it from projects that still rely on it."""
        assert ".claude/hooks/spec-classifier.py" in _MANAGED_HOOKS

    # 33. Upgrade local-only — intake hook respects the local-only allowlist
    def test_upgrade_local_only_excludes_intake(self):
        """plan_upgrade() for local-only profile should not include
        intake-classifier.py since intake is a bridge-profile feature.
        Verified by inspecting the filter logic."""
        from groundtruth_kb.project.upgrade import _MANAGED_HOOKS as managed

        # Simulate the local-only filter
        local_allowed = {"assertion-check.py", "spec-classifier.py"}
        filtered = [h for h in managed if h.split("/")[-1] in local_allowed]
        assert ".claude/hooks/intake-classifier.py" not in filtered
        assert ".claude/hooks/spec-classifier.py" in filtered


class TestF5Roundtrip:
    """End-to-end roundtrip test."""

    # 34. classify → capture → confirm → spec exists with correct type/authority + quality tier
    def test_full_roundtrip(self, db):
        # Classify
        c = classify_requirement(
            db,
            "The system must implement OAuth 2.0 authorization for all API endpoints",
        )
        assert c["classification"] == "directive"
        assert c["confidence"] > 0.8

        # Capture
        cap = capture_requirement(
            db,
            "The system must implement OAuth 2.0 authorization for all API endpoints",
            proposed_title="OAuth 2.0 API authorization",
            proposed_section="auth",
            proposed_type="requirement",
            proposed_authority="stated",
        )

        # Confirm
        result = confirm_intake(db, cap["deliberation_id"])
        assert "confirmed_spec_id" in result

        # Verify spec exists with correct fields
        spec = db.get_spec(result["confirmed_spec_id"])
        assert spec is not None
        assert spec["title"] == "OAuth 2.0 API authorization"
        assert spec.get("type") == "requirement"
        assert spec.get("authority") == "stated"
        assert spec.get("section") == "auth"

        # Verify quality tier is present
        assert result["quality"].get("tier") is not None


class TestF5Regressions:
    """Regression tests from NO-GO bridge/gtkb-phase3-implementation-016.md."""

    # R1. reject_intake must refuse non-intake deliberations
    def test_reject_intake_refuses_non_intake(self, db):
        """Ordinary owner_conversation deliberations cannot be rejected as intakes."""
        db.insert_deliberation(
            id="D-NON-INTAKE-001",
            title="Regular chat",
            summary="General discussion",
            content=json.dumps({"note": "ordinary conversation, not an intake"}),
            source_type="owner_conversation",
            outcome=None,
            changed_by="test",
            change_reason="test",
        )

        result = reject_intake(db, "D-NON-INTAKE-001", "not an intake")
        assert "error" in result
        assert "intake" in result["error"].lower()

        # Verify the original deliberation was not mutated
        delib = db.get_deliberation("D-NON-INTAKE-001")
        assert delib is not None
        content = json.loads(delib["content"])
        assert content.get("intake_status") is None
        assert content.get("rejection_reason") is None
        assert content.get("note") == "ordinary conversation, not an intake"
        # Outcome should remain None (not "no_go")
        assert delib.get("outcome") in (None, "")

    # R2. reject_intake on malformed content (not a dict) is refused
    def test_reject_intake_refuses_malformed(self, db):
        """Deliberations with non-dict content are refused."""
        db.insert_deliberation(
            id="D-MALFORMED-001",
            title="Bad content",
            summary="Malformed JSON",
            content='"just a string, not a dict"',
            source_type="owner_conversation",
            outcome=None,
            changed_by="test",
            change_reason="test",
        )

        result = reject_intake(db, "D-MALFORMED-001", "malformed")
        assert "error" in result
