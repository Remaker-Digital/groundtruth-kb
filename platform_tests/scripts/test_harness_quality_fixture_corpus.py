from __future__ import annotations

import ast
from dataclasses import replace

import pytest

from scripts.benchmarks import fixture_corpus as corpus
from scripts.benchmarks import harness_quality_manifest as manifest


def test_fixture_corpus_is_valid_and_readable() -> None:
    fixtures = corpus.require_valid_fixture_corpus()

    assert corpus.validate_fixture_corpus(fixtures) == []
    assert len(fixtures) >= len(corpus.DETERMINISTIC_ONLY_FAMILY_IDS)
    assert corpus.fixture_corpus_to_dict(fixtures)["fixtures"]


def test_seeded_fixtures_cover_deterministic_only_families() -> None:
    fixtures = corpus.require_valid_fixture_corpus()
    family_ids = {fixture.challenge_family for fixture in fixtures}

    assert set(corpus.DETERMINISTIC_ONLY_FAMILY_IDS) <= family_ids


def test_answer_keys_use_manifest_tokens_and_failure_classes() -> None:
    fixtures = corpus.require_valid_fixture_corpus()
    families = {family.id: family for family in manifest.CHALLENGE_FAMILIES}

    for fixture in fixtures:
        family = families[fixture.challenge_family]
        assert set(fixture.deterministic_evidence) <= set(family.deterministic_evidence)
        assert set(fixture.failure_classes) <= set(manifest.FAILURE_CLASSES)
        assert fixture.author_model_configuration


def test_fixture_roots_are_isolated_and_unpromoted() -> None:
    fixtures = corpus.require_valid_fixture_corpus()
    root = corpus.FIXTURE_ROOT.resolve()

    for fixture in fixtures:
        fixture_root = (corpus.PROJECT_ROOT / fixture.fixture_root).resolve()
        assert fixture_root.is_relative_to(root)
        assert fixture_root.is_dir()
        assert fixture.promotion_status == corpus.PROMOTION_STATUS_UNPROMOTED


def test_seeded_failure_classes_include_root_boundary_and_claim_accuracy() -> None:
    fixtures = corpus.require_valid_fixture_corpus()
    failure_classes = {failure_class for fixture in fixtures for failure_class in fixture.failure_classes}

    assert "root-boundary" in failure_classes
    assert "claim-accuracy" in failure_classes


def test_promotion_requires_explicit_token_and_does_not_write() -> None:
    fixture = corpus.require_valid_fixture_corpus()[0]

    with pytest.raises(ValueError, match="explicit approval token"):
        corpus.mark_fixture_promoted(fixture, approval_token="implicit")

    promoted = corpus.mark_fixture_promoted(fixture, approval_token=corpus.PROMOTION_APPROVAL_TOKEN)

    assert fixture.promotion_status == corpus.PROMOTION_STATUS_UNPROMOTED
    assert promoted.promotion_status == corpus.PROMOTION_STATUS_PROMOTED


def test_validation_rejects_unknown_answer_key_and_missing_family_coverage() -> None:
    fixture = corpus.require_valid_fixture_corpus()[0]
    bad_fixture = replace(
        fixture,
        deterministic_evidence={"not-a-real-token": True},
        challenge_family="implementation_start_safety",
    )

    errors = corpus.validate_fixture_corpus((bad_fixture,))

    assert any("unknown deterministic evidence" in error for error in errors)
    assert any("missing deterministic-only fixture families" in error for error in errors)


def test_validation_rejects_out_of_root_fixture_and_unknown_failure_class() -> None:
    fixture = corpus.require_valid_fixture_corpus()[0]
    bad_fixture = replace(
        fixture,
        fixture_root="bridge",
        failure_classes=("not-a-real-failure-class",),
    )

    errors = corpus.validate_fixture_corpus((bad_fixture,))

    assert any("fixture root escapes isolated corpus root" in error for error in errors)
    assert any("unknown failure classes" in error for error in errors)


def test_fixture_module_imports_no_live_mutating_surface() -> None:
    module_path = corpus.PROJECT_ROOT / "scripts/benchmarks/fixture_corpus.py"
    tree = ast.parse(module_path.read_text(encoding="utf-8"))
    imported_modules: set[str] = set()
    call_names: set[str] = set()

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported_modules.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported_modules.add(node.module)
        elif isinstance(node, ast.Call):
            if isinstance(node.func, ast.Attribute):
                call_names.add(node.func.attr)
            elif isinstance(node.func, ast.Name):
                call_names.add(node.func.id)

    assert all(not module.startswith("groundtruth_kb.") for module in imported_modules)
    assert not {"insert_spec", "resolve_work_item", "write_text", "open"} & call_names
