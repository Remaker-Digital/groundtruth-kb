"""Native terminology diagnostics; file-glossary freshness has no authority."""

from __future__ import annotations

import pytest
from groundtruth_kb.authority import compact_status
from groundtruth_kb.authority_client import AuthorityClient
from groundtruth_kb.project.doctor import _check_canonical_terms_registry


def term(name, *, level="platform_core", scope="platform", **fields):
    return {
        "id": name,
        "canonical_term": name,
        "authority_level": level,
        "scope": scope,
        "lifecycle_status": "active",
        "accepted_synonyms": [],
        "discouraged_synonyms": [],
        "forbidden_uses": [],
        **fields,
    }


def serve(monkeypatch, terms, *, health=None):
    monkeypatch.setenv("GT_AUTHORITY_URL", "http://127.0.0.1:12345")
    status = {**compact_status(records=terms), "source_issues": []} if health is None else health

    def request(self, method, path, *, body=None, query=None):
        assert method == "GET" and body is None
        if path == "/v1/authority/status":
            return status
        assert path == "/v1/terms"
        return {"records": terms, "next_after": None}

    monkeypatch.setattr(AuthorityClient, "request", request)


@pytest.mark.parametrize("glossary_present", [False, True])
def test_native_terms_ignore_missing_or_conflicting_glossary(tmp_path, monkeypatch, glossary_present):
    serve(monkeypatch, [term("MEMBASE")])
    glossary = tmp_path / ".claude/rules/canonical-terminology.md"
    if glossary_present:
        glossary.parent.mkdir(parents=True)
        glossary.write_text("# Wrong local definition\n", encoding="utf-8")
    sentinel = tmp_path / "groundtruth.db"
    sentinel.write_bytes(b"inert")

    def refuse(*args, **kwargs):
        pytest.fail("Native term diagnostics must not open SQLite")

    monkeypatch.setattr("sqlite3.connect", refuse)
    result = _check_canonical_terms_registry(tmp_path)
    assert result.status == "pass", result.message
    assert result.found is True
    assert sentinel.read_bytes() == b"inert"
    if glossary_present:
        assert glossary.read_text(encoding="utf-8") == "# Wrong local definition\n"
    else:
        assert not glossary.exists()


def test_platform_core_redefinition_fails(tmp_path, monkeypatch):
    serve(
        monkeypatch,
        [
            term("CORE", canonical_term="Shared"),
            term("EXT", level="adopter_extension", scope="application:Example", canonical_term="Shared"),
        ],
    )
    result = _check_canonical_terms_registry(tmp_path)
    assert result.status == "fail"
    assert "platform_core_redefinition" in result.message


def test_cross_field_reuse_warns(tmp_path, monkeypatch):
    serve(monkeypatch, [term("FIRST", accepted_synonyms=["overlap"]), term("SECOND", discouraged_synonyms=["overlap"])])
    result = _check_canonical_terms_registry(tmp_path)
    assert result.status == "warning"
    assert "cross_field_text_reuse" in result.message


def test_native_source_issue_and_ambiguity_fail(tmp_path, monkeypatch):
    health = {
        "status": "fail",
        "active_records": 2,
        "ambiguities": [{"ids": ["A", "B"]}],
        "validation_issues": [],
        "source_issues": [{"id": "A", "status": "retired"}],
    }
    serve(monkeypatch, [term("A"), term("B")], health=health)
    result = _check_canonical_terms_registry(tmp_path)
    assert result.status == "fail"
    assert "source_issues=1" in result.message
    assert "ambiguities=1" in result.message


@pytest.mark.parametrize("health", [{}, {"status": "pass"}])
def test_malformed_terminology_status_fails(tmp_path, monkeypatch, health):
    serve(monkeypatch, [term("A")], health=health)
    result = _check_canonical_terms_registry(tmp_path)
    assert result.status == "fail"
    assert "malformed" in result.message


def test_no_authority_is_unverified_warning(tmp_path, monkeypatch):
    monkeypatch.delenv("GT_AUTHORITY_URL", raising=False)
    result = _check_canonical_terms_registry(tmp_path)
    assert result.status == "warning"
    assert result.found is False
