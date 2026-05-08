"""Tests for canonical_terms collision detection (unified text-surface key model).

Per `bridge/gtkb-canonical-terminology-system-context-model-001-005.md`
Specification-Derived Test Plan: T-collision-1, T-collision-2, T-collision-3,
T-collision-4, T-collision-5.

The unified text-surface key model: all lexical surfaces (canonical_term,
accepted_synonyms, discouraged_synonyms, forbidden_uses) share the
``("text", normalized_value)`` namespace so cross-field text reuse is
detected. Field-of-origin metadata is preserved for the classifier.

Copyright (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC.
All rights reserved.
"""

from __future__ import annotations

from groundtruth_kb import canonical_terms


def _term(
    *,
    id: str,
    canonical_term: str = "",
    authority_level: str = "platform_core",
    scope: str = "platform",
    accepted_synonyms: list[str] | None = None,
    discouraged_synonyms: list[str] | None = None,
    forbidden_uses: list[str] | None = None,
) -> dict:
    return {
        "id": id,
        "canonical_term": canonical_term or id,
        "definition": "test definition",
        "authority_level": authority_level,
        "scope": scope,
        "accepted_synonyms": accepted_synonyms or [],
        "discouraged_synonyms": discouraged_synonyms or [],
        "forbidden_uses": forbidden_uses or [],
        "lifecycle_status": "active",
    }


# ---------------------------------------------------------------------------
# T-collision-1: id collision across authority levels = ERROR
# ---------------------------------------------------------------------------


def test_id_collision_across_authority_levels_errors() -> None:
    """T-collision-1: same id at platform_core and adopter_extension is ERROR."""
    terms = [
        _term(id="MEMBASE", authority_level="platform_core", scope="platform"),
        _term(
            id="MEMBASE",
            canonical_term="My Custom MemBase",
            authority_level="adopter_extension",
            scope="adopter:agent_red",
        ),
    ]
    errors, warnings = canonical_terms.find_collisions(terms)
    assert len(errors) >= 1
    assert any(e.classification == "platform_core_redefinition" for e in errors)
    # Both id-key and text-key (canonical_term overlap) may surface;
    # whichever fires, the classification must be platform_core_redefinition
    # because authority levels mix platform_core with non-platform_core.


# ---------------------------------------------------------------------------
# T-collision-2: display-term collision across authority levels = ERROR
# ---------------------------------------------------------------------------


def test_display_term_collision_across_authority_levels_errors() -> None:
    """T-collision-2: different ids, same canonical_term (case-insensitive),
    levels include platform_core and adopter_extension. ERROR.
    """
    terms = [
        _term(
            id="WRAP_UP_TRIGGER",
            canonical_term="Wrap Up",
            authority_level="platform_core",
            scope="platform",
        ),
        _term(
            id="CUSTOMER_ENGAGEMENT_CLOSE",
            canonical_term="wrap up",  # case-insensitive match to platform_core
            authority_level="adopter_extension",
            scope="adopter:agent_red",
        ),
    ]
    errors, warnings = canonical_terms.find_collisions(terms)
    assert len(errors) >= 1
    finding = next(e for e in errors if e.classification == "platform_core_redefinition")
    assert finding.key == ("text", "wrap up")


# ---------------------------------------------------------------------------
# T-collision-3: cross-field text reuse — accepted vs discouraged = WARN
# ---------------------------------------------------------------------------


def test_cross_field_text_reuse_accepted_vs_discouraged_warns() -> None:
    """T-collision-3: same-scope terms, A.accepted_synonyms = ["wrap up"],
    B.discouraged_synonyms = ["wrap up"]. WARN.
    """
    scope = "adopter:agent_red"
    terms = [
        _term(
            id="A",
            canonical_term="A",
            authority_level="adopter_extension",
            scope=scope,
            accepted_synonyms=["wrap up"],
        ),
        _term(
            id="B",
            canonical_term="B",
            authority_level="adopter_extension",
            scope=scope,
            discouraged_synonyms=["wrap up"],
        ),
    ]
    errors, warnings = canonical_terms.find_collisions(terms)
    assert errors == []
    assert any(w.classification == "cross_field_text_reuse" and w.key == ("text", "wrap up") for w in warnings)
    finding = next(w for w in warnings if w.classification == "cross_field_text_reuse" and w.key == ("text", "wrap up"))
    # Origin metadata must label which field each side originated from.
    field_kinds = {field for (_, pairs) in finding.origin_pairs for (field, _) in pairs}
    assert "accepted_synonym" in field_kinds
    assert "discouraged_synonym" in field_kinds


# ---------------------------------------------------------------------------
# T-collision-4: cross-field text reuse — accepted vs forbidden = WARN
# ---------------------------------------------------------------------------


def test_cross_field_text_reuse_accepted_vs_forbidden_warns() -> None:
    """T-collision-4: same-scope terms, A.accepted_synonyms = ["customer signal"],
    B.forbidden_uses = ["customer signal"]. WARN.
    """
    scope = "adopter:agent_red"
    terms = [
        _term(
            id="A",
            canonical_term="A",
            authority_level="adopter_extension",
            scope=scope,
            accepted_synonyms=["customer signal"],
        ),
        _term(
            id="B",
            canonical_term="B",
            authority_level="adopter_extension",
            scope=scope,
            forbidden_uses=["customer signal"],
        ),
    ]
    errors, warnings = canonical_terms.find_collisions(terms)
    assert errors == []
    finding = next(
        w for w in warnings if w.classification == "cross_field_text_reuse" and w.key == ("text", "customer signal")
    )
    field_kinds = {field for (_, pairs) in finding.origin_pairs for (field, _) in pairs}
    assert "accepted_synonym" in field_kinds
    assert "forbidden_use" in field_kinds


# ---------------------------------------------------------------------------
# T-collision-5: cross-authority text reuse — synonym overlap = ERROR
# ---------------------------------------------------------------------------


def test_cross_authority_synonym_overlap_errors() -> None:
    """T-collision-5: A platform_core accepted_synonyms = ["wrap up"];
    B adopter_extension accepted_synonyms = ["wrap up"]. ERROR
    (platform_core_redefinition).
    """
    terms = [
        _term(
            id="WRAP_UP_TRIGGER",
            canonical_term="WRAP UP TRIGGER",
            authority_level="platform_core",
            scope="platform",
            accepted_synonyms=["wrap up", "prepare for a new session"],
        ),
        _term(
            id="ADOPTER_TERM",
            canonical_term="ADOPTER TERM",
            authority_level="adopter_extension",
            scope="adopter:agent_red",
            accepted_synonyms=["wrap up"],
        ),
    ]
    errors, warnings = canonical_terms.find_collisions(terms)
    assert any(e.classification == "platform_core_redefinition" and e.key == ("text", "wrap up") for e in errors)


# ---------------------------------------------------------------------------
# Negative cases: no collision when there shouldn't be one
# ---------------------------------------------------------------------------


def test_no_collision_when_terms_are_distinct() -> None:
    """Distinct ids, distinct lexical surfaces, distinct scopes: no collision."""
    terms = [
        _term(id="A", canonical_term="Alpha"),
        _term(id="B", canonical_term="Beta"),
    ]
    errors, warnings = canonical_terms.find_collisions(terms)
    assert errors == []
    assert warnings == []


def test_same_field_same_scope_synonym_overlap_in_one_authority_level() -> None:
    """Two adopter_extension terms in the same scope sharing a synonym in
    the same field: classified as cross_scope_overlap or cross_field_text_reuse
    (we only assert it's a WARN, not how it's classified — both are
    legitimate for the field-overlap-vs-scope-overlap distinction).
    """
    scope = "adopter:agent_red"
    terms = [
        _term(
            id="A",
            canonical_term="A",
            authority_level="adopter_extension",
            scope=scope,
            accepted_synonyms=["shared phrase"],
        ),
        _term(
            id="B",
            canonical_term="B",
            authority_level="adopter_extension",
            scope=scope,
            accepted_synonyms=["shared phrase"],
        ),
    ]
    errors, warnings = canonical_terms.find_collisions(terms)
    # Same-field same-scope same-level reuse is not flagged as cross_field_text_reuse
    # (only one field of origin); not flagged as cross_scope_overlap (only one scope);
    # not flagged as platform_core_redefinition. So warnings should be empty.
    # This is a deliberate non-finding: same-scope same-field text reuse is a
    # legitimate "two terms share an accepted synonym" pattern that the system
    # neither blocks nor warns about. Phase 2/3 may revisit.
    assert errors == []
    assert warnings == []


def test_case_insensitive_text_normalization() -> None:
    """Texts that differ only by case still collide."""
    terms = [
        _term(
            id="A",
            canonical_term="Wrap Up",
            authority_level="platform_core",
            scope="platform",
        ),
        _term(
            id="B",
            canonical_term="WRAP UP",
            authority_level="adopter_extension",
            scope="adopter:agent_red",
        ),
    ]
    errors, warnings = canonical_terms.find_collisions(terms)
    assert any(e.classification == "platform_core_redefinition" for e in errors)


def test_whitespace_normalization() -> None:
    """Texts that differ only by leading/trailing whitespace collide."""
    terms = [
        _term(
            id="A",
            canonical_term="MemBase",
            authority_level="platform_core",
            scope="platform",
        ),
        _term(
            id="B",
            canonical_term="  MemBase  ",
            authority_level="adopter_extension",
            scope="adopter:agent_red",
        ),
    ]
    errors, warnings = canonical_terms.find_collisions(terms)
    assert any(e.classification == "platform_core_redefinition" for e in errors)


def test_empty_field_lists_do_not_collide() -> None:
    """Empty accepted_synonyms/discouraged_synonyms/forbidden_uses do not
    produce spurious collisions."""
    terms = [
        _term(id="A", canonical_term="Alpha"),
        _term(id="B", canonical_term="Beta"),
    ]
    errors, warnings = canonical_terms.find_collisions(terms)
    assert errors == []
    assert warnings == []
