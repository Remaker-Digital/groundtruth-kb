"""Standing delete authorization classifier — WI-6743 (Route B).

Acceptance contract for the bounded relaxation in
``.harness-baseline-configuration/rules/prime-builder.md`` section
"Standing Delete Authorization - DERIVED and CACHED Only", owner-approved via
``DELIB-20260825183500``.

The classifier is deliberately conservative: it grants standing delete only on
positive proof, and fails closed to ``owner_gated`` everywhere else. These tests
cover the positive paths, the negative paths that must NOT qualify, and the
fail-closed default.
"""

from __future__ import annotations

from datetime import UTC, datetime

import pytest
from groundtruth_kb.hygiene.reclaim import (
    _STANDING_DELETE_AUTHORIZED,
    classify_standing_delete,
    standing_delete_audit_record,
)

DIGEST = "a" * 64
OTHER_DIGEST = "b" * 64


# --- positive paths -------------------------------------------------------


def test_derived_requires_generator_and_demonstrated_regeneration() -> None:
    result = classify_standing_delete(
        rel_path="build/out.js",
        observed_digest=DIGEST,
        generator="npm run build",
        regenerated_digest=DIGEST,
        evidence_source="governed_regeneration_verifier",
    )
    assert result["disposition"] == "derived"
    assert result["standing_delete_authorized"] is True
    assert result["evidence"]["generator"] == "npm run build"


def test_cached_requires_named_sot_and_digest_correspondence() -> None:
    result = classify_standing_delete(
        rel_path=".cache/spec.json",
        observed_digest=DIGEST,
        source_of_truth="groundtruth.db",
        sot_digest=DIGEST,
        evidence_source="governed_sot_verifier",
    )
    assert result["disposition"] == "cached"
    assert result["standing_delete_authorized"] is True
    assert result["evidence"]["source_of_truth"] == "groundtruth.db"


# --- negative paths: named but unproven must NOT qualify ------------------


def test_named_generator_without_regeneration_does_not_qualify() -> None:
    """Absence of a demonstrated regeneration is not evidence of derivation."""
    result = classify_standing_delete(
        rel_path="build/out.js",
        observed_digest=DIGEST,
        generator="npm run build",
        registry_matches=["SOT-BUILD"],
    )
    assert result["disposition"] == "owner_gated"
    assert result["standing_delete_authorized"] is False


def test_generator_whose_regeneration_diverges_does_not_qualify() -> None:
    result = classify_standing_delete(
        rel_path="build/out.js",
        observed_digest=DIGEST,
        generator="npm run build",
        regenerated_digest=OTHER_DIGEST,
        registry_matches=["SOT-BUILD"],
    )
    assert result["disposition"] == "owner_gated"
    assert result["standing_delete_authorized"] is False


def test_named_sot_whose_digest_diverges_does_not_qualify() -> None:
    result = classify_standing_delete(
        rel_path=".cache/spec.json",
        observed_digest=DIGEST,
        source_of_truth="groundtruth.db",
        sot_digest=OTHER_DIGEST,
        registry_matches=["SOT-SPEC"],
    )
    assert result["disposition"] == "owner_gated"
    assert result["standing_delete_authorized"] is False


def test_sot_named_without_digest_does_not_qualify() -> None:
    result = classify_standing_delete(
        rel_path=".cache/spec.json",
        observed_digest=DIGEST,
        source_of_truth="groundtruth.db",
        registry_matches=["SOT-SPEC"],
    )
    assert result["disposition"] == "owner_gated"


# --- unregistered routes to quarantine, never direct delete ---------------


def test_unregistered_routes_to_quarantine_and_is_never_authorized() -> None:
    result = classify_standing_delete(rel_path="stray/file.txt", observed_digest=DIGEST)
    assert result["disposition"] == "unregistered"
    assert result["standing_delete_authorized"] is False
    assert "quarantine" in result["reason"]


@pytest.mark.parametrize("registry_matches", [None, []])
def test_registry_absence_alone_never_authorizes_delete(registry_matches: list[str] | None) -> None:
    result = classify_standing_delete(
        rel_path="stray/file.txt",
        observed_digest=DIGEST,
        registry_matches=registry_matches,
    )
    assert result["standing_delete_authorized"] is False


# --- precedence -----------------------------------------------------------


def test_proven_regeneration_outranks_registry_absence() -> None:
    """Registry-absent AND demonstrably regenerable classifies as derived.

    Positive proof that the bytes reproduce is strictly stronger evidence than
    registry absence, so it decides. Registry absence alone never upgrades a
    disposition -- that direction is covered above.
    """
    result = classify_standing_delete(
        rel_path="__pycache__/mod.pyc",
        observed_digest=DIGEST,
        generator="python -m compileall",
        regenerated_digest=DIGEST,
        registry_matches=[],
        evidence_source="governed_regeneration_verifier",
    )
    assert result["disposition"] == "derived"


# --- fail-closed default --------------------------------------------------


def test_no_evidence_at_all_is_not_authorized() -> None:
    result = classify_standing_delete(rel_path="mystery")
    assert result["standing_delete_authorized"] is False


def test_registered_object_with_no_class_evidence_is_owner_gated() -> None:
    """Uncertainty is not a licence: the default is owner-gated."""
    result = classify_standing_delete(
        rel_path="src/module.py",
        observed_digest=DIGEST,
        registry_matches=["SOT-SRC"],
    )
    assert result["disposition"] == "owner_gated"
    assert result["standing_delete_authorized"] is False


def test_only_derived_and_cached_are_ever_authorized() -> None:
    """The authorized set is bounded and must not grow without a fresh owner decision."""
    assert frozenset({"derived", "cached"}) == _STANDING_DELETE_AUTHORIZED


def test_code_and_tests_cannot_satisfy_the_evidence_conditions() -> None:
    """The rule states it does not authorize removing code or tests.

    Source files have no generator that reproduces them and no SoT they mirror,
    so they cannot reach an authorized disposition through this classifier.
    """
    for path in ("src/module.py", "platform_tests/scripts/test_thing.py"):
        result = classify_standing_delete(rel_path=path, observed_digest=DIGEST, registry_matches=["SOT-SRC"])
        assert result["standing_delete_authorized"] is False


# --- mandatory post-hoc audit record --------------------------------------


def test_audit_record_names_object_and_evidence() -> None:
    disposition = classify_standing_delete(
        rel_path="build/out.js",
        observed_digest=DIGEST,
        generator="npm run build",
        regenerated_digest=DIGEST,
        evidence_source="governed_regeneration_verifier",
    )
    record = standing_delete_audit_record(
        disposition,
        action="delete",
        actor="prime-builder/claude/B",
        performed_at=datetime(2026, 8, 25, 22, 0, tzinfo=UTC),
    )
    assert record["record_kind"] == "standing_delete_action"
    assert record["path"] == "build/out.js"
    assert record["disposition"] == "derived"
    assert record["evidence"]["generator"] == "npm run build"
    assert record["action"] == "delete"
    assert record["actor"] == "prime-builder/claude/B"
    assert record["authority"] == "DELIB-20260825183500"
    assert record["performed_at"].startswith("2026-08-25T22:00")


def test_audit_record_preserves_evidence_for_refused_actions() -> None:
    """A refusal is auditable too: the record carries why the class was not established."""
    disposition = classify_standing_delete(rel_path="mystery", registry_matches=["SOT-X"])
    record = standing_delete_audit_record(
        disposition,
        action="refused",
        actor="prime-builder/claude/B",
        performed_at=datetime(2026, 8, 25, 22, 0, tzinfo=UTC),
    )
    assert record["standing_delete_authorized"] is False
    assert record["disposition"] == "owner_gated"
    assert record["reason"]


# --- WI-6743 F1: protected classes are denied on path, before evidence -----
#
# Verdict `-008` proved the prior classifier authorized deletion of protected
# source and tests whenever the caller supplied matching digests, because it
# compared caller-asserted strings for equality and never inspected `rel_path`.
# Every case below supplies MATCHING digests -- the strongest evidence a caller
# can assert -- and must still be refused.


@pytest.mark.parametrize(
    ("rel_path", "denied_class"),
    [
        ("src/module.py", "protected_source_or_test_tree"),
        ("platform_tests/scripts/test_x.py", "protected_path_prefix"),
        ("groundtruth-kb/src/groundtruth_kb/db.py", "protected_path_prefix"),
        ("scripts/gtkb_bridge_writer.py", "protected_path_prefix"),
        ("bridge/gtkb-thing-001.md", "protected_path_prefix"),
        ("config/dispatcher/rules.toml", "protected_path_prefix"),
        (".claude/hooks/some-hook.py", "protected_path_prefix"),
        (".claude/rules/some-rule.md", "protected_path_prefix"),
        (
            ".harness-baseline-configuration/rules/prime-builder.md",
            "protected_source_or_test_tree",
        ),
        ("CLAUDE.md", "protected_exact_artifact"),
        ("AGENTS.md", "protected_exact_artifact"),
        ("env.local", "protected_exact_artifact"),
        ("anywhere/SPEC-1234-thing.md", "protected_specification_or_governance"),
        ("anywhere/GOV-01-thing.md", "protected_specification_or_governance"),
        ("anywhere/ADR-0001-thing.md", "protected_specification_or_governance"),
        ("anywhere/DCL-THING-001.md", "protected_specification_or_governance"),
        ("anywhere/test_orphan.py", "protected_code_or_config"),
        ("toplevel.py", "protected_code_or_config"),
        ("deploy.sh", "protected_code_or_config"),
        ("pyproject.toml", "protected_code_or_config"),
    ],
)
def test_denied_class_is_refused_despite_matching_regeneration_digests(rel_path: str, denied_class: str) -> None:
    """A protected object with a PERFECT derived proof must stay unauthorized."""
    result = classify_standing_delete(
        rel_path=rel_path,
        observed_digest=DIGEST,
        generator="arbitrary",
        regenerated_digest=DIGEST,
        evidence_source="governed_regeneration_verifier",
    )
    assert result["standing_delete_authorized"] is False
    assert result["disposition"] == "owner_gated"
    assert result["evidence"]["protected_class"] == denied_class


@pytest.mark.parametrize(
    "rel_path",
    [
        "src/module.py",
        "platform_tests/scripts/test_x.py",
        "groundtruth-kb/src/groundtruth_kb/db.py",
        ".harness-baseline-configuration/hooks/manifest.toml",
        "CLAUDE.md",
    ],
)
def test_denied_class_is_refused_despite_matching_sot_digests(rel_path: str) -> None:
    """The same objects with a PERFECT cached proof must also stay unauthorized."""
    result = classify_standing_delete(
        rel_path=rel_path,
        observed_digest=DIGEST,
        source_of_truth="arbitrary",
        sot_digest=DIGEST,
        evidence_source="governed_sot_verifier",
    )
    assert result["standing_delete_authorized"] is False
    assert result["disposition"] == "owner_gated"


def test_dot_prefixed_protected_paths_are_not_stripped_into_unprotected_ones() -> None:
    """Regression: ``lstrip("./")`` strips any leading "." and defeats dot-paths.

    Written because the first implementation of this path guard used
    ``lstrip("./")``, which turned ``.claude/hooks/x.py`` into
    ``claude/hooks/x.py`` and silently unprotected every dot-prefixed tree.
    """
    for rel_path in (
        ".claude/hooks/x.py",
        ".claude/rules/x.md",
        ".harness-baseline-configuration/rules/prime-builder.md",
        ".github/workflows/ci.yml",
    ):
        result = classify_standing_delete(
            rel_path=rel_path,
            observed_digest=DIGEST,
            source_of_truth="arbitrary",
            sot_digest=DIGEST,
            evidence_source="governed_sot_verifier",
        )
        assert result["standing_delete_authorized"] is False, rel_path


# --- WI-6743 F1: evidence must come from a governed verifier ---------------


@pytest.mark.parametrize("evidence_source", [None, "", "arbitrary", "self", "caller"])
def test_untrusted_evidence_source_never_authorizes(evidence_source: str | None) -> None:
    """Caller-asserted evidence is an input, not proof."""
    result = classify_standing_delete(
        rel_path="build/out.txt",
        observed_digest=DIGEST,
        generator="npm run build",
        regenerated_digest=DIGEST,
        evidence_source=evidence_source,
    )
    assert result["standing_delete_authorized"] is False
    assert result["disposition"] == "owner_gated"


def test_trusted_evidence_source_on_unprotected_object_still_authorizes() -> None:
    """The guards must not disable the feature they protect.

    Without this, a maximally strict classifier would pass every negative test
    while authorizing nothing, which is not what the owner approved.
    """
    derived = classify_standing_delete(
        rel_path="build/out.txt",
        observed_digest=DIGEST,
        generator="npm run build",
        regenerated_digest=DIGEST,
        evidence_source="governed_regeneration_verifier",
    )
    cached = classify_standing_delete(
        rel_path=".cache/blob.bin",
        observed_digest=DIGEST,
        source_of_truth="groundtruth.db",
        sot_digest=DIGEST,
        evidence_source="governed_sot_verifier",
    )
    assert derived["disposition"] == "derived"
    assert derived["standing_delete_authorized"] is True
    assert cached["disposition"] == "cached"
    assert cached["standing_delete_authorized"] is True
