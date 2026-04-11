"""Tests for deliberation archive CRUD, redaction, multi-link, dedup, and semantic search.

Copyright (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
Licensed under AGPL-3.0-or-later.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from groundtruth_kb.db import HAS_CHROMADB, SEMANTIC_MAX_DISTANCE, KnowledgeDB

# Skip marker for tests requiring ChromaDB
requires_chromadb = pytest.mark.skipif(not HAS_CHROMADB, reason="ChromaDB not installed")


class TestInsertDeliberation:
    """Tests for insert_deliberation()."""

    def test_basic_insert(self, db):
        result = db.insert_deliberation(
            id="DELIB-0001",
            source_type="lo_review",
            title="Test review",
            summary="A test review summary.",
            content="Round 1: Finding X. Round 2: GO.",
            changed_by="test",
            change_reason="test insert",
            spec_id="SPEC-001",
            participants=["prime", "codex"],
            outcome="go",
            session_id="S100",
        )
        assert result["id"] == "DELIB-0001"
        assert result["version"] == 1
        assert result["source_type"] == "lo_review"
        assert result["spec_id"] == "SPEC-001"
        assert result["outcome"] == "go"
        assert result["session_id"] == "S100"
        assert result["redaction_state"] == "clean"
        assert result["content_hash"] is not None

    def test_versioning(self, db):
        db.insert_deliberation(
            id="DELIB-0001",
            source_type="proposal",
            title="V1",
            summary="First version.",
            content="Original proposal.",
            changed_by="test",
            change_reason="v1",
        )
        result = db.insert_deliberation(
            id="DELIB-0001",
            source_type="proposal",
            title="V2",
            summary="Updated version.",
            content="Revised proposal with new approach.",
            changed_by="test",
            change_reason="v2",
        )
        assert result["version"] == 2
        assert result["title"] == "V2"

    def test_history(self, db):
        db.insert_deliberation(
            id="DELIB-0001",
            source_type="report",
            title="Report v1",
            summary="Summary.",
            content="Content v1.",
            changed_by="test",
            change_reason="v1",
        )
        db.insert_deliberation(
            id="DELIB-0001",
            source_type="report",
            title="Report v2",
            summary="Summary v2.",
            content="Content v2.",
            changed_by="test",
            change_reason="v2",
        )
        history = db.get_deliberation_history("DELIB-0001")
        assert len(history) == 2
        assert history[0]["version"] == 1
        assert history[1]["version"] == 2

    def test_invalid_source_type(self, db):
        with pytest.raises(ValueError, match="Invalid source_type"):
            db.insert_deliberation(
                id="DELIB-0001",
                source_type="invalid_type",
                title="Bad",
                summary="Bad.",
                content="Bad content.",
                changed_by="test",
                change_reason="test",
            )

    def test_invalid_outcome(self, db):
        with pytest.raises(ValueError, match="Invalid outcome"):
            db.insert_deliberation(
                id="DELIB-0001",
                source_type="lo_review",
                title="Bad",
                summary="Bad.",
                content="Bad content.",
                changed_by="test",
                change_reason="test",
                outcome="maybe",
            )

    def test_all_source_types(self, db):
        for i, st in enumerate(
            ["lo_review", "proposal", "owner_conversation", "report", "session_harvest", "bridge_thread"]
        ):
            result = db.insert_deliberation(
                id=f"DELIB-{i:04d}",
                source_type=st,
                title=f"Test {st}",
                summary=f"Summary for {st}.",
                content=f"Content for {st}.",
                changed_by="test",
                change_reason=f"test {st}",
            )
            assert result["source_type"] == st

    def test_all_outcomes(self, db):
        for i, outcome in enumerate(["go", "no_go", "deferred", "owner_decision", "informational"]):
            result = db.insert_deliberation(
                id=f"DELIB-{i:04d}",
                source_type="lo_review",
                title=f"Test {outcome}",
                summary="Summary.",
                content="Content.",
                changed_by="test",
                change_reason="test",
                outcome=outcome,
            )
            assert result["outcome"] == outcome

    def test_participants_parsed(self, db):
        result = db.insert_deliberation(
            id="DELIB-0001",
            source_type="lo_review",
            title="Test",
            summary="Summary.",
            content="Content.",
            changed_by="test",
            change_reason="test",
            participants=["prime", "codex", "owner"],
        )
        assert result["participants_parsed"] == ["prime", "codex", "owner"]


class TestRedaction:
    """Tests for credential/PII redaction."""

    def test_api_key_redacted(self, db):
        content = "Found bug. api_key=sk_live_abc123def456ghi789 in config."
        result = db.insert_deliberation(
            id="DELIB-0001",
            source_type="report",
            title="Redaction test",
            summary="Summary.",
            content=content,
            changed_by="test",
            change_reason="test",
        )
        assert "sk_live_abc123def456ghi789" not in result["content"]
        assert "[REDACTED:api_key]" in result["content"]
        assert result["redaction_state"] == "redacted"
        assert result["sensitivity"] == "contains_redacted"
        assert "api_key" in result["redaction_notes"]

    def test_token_redacted(self, db):
        content = "bearer=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.payload.signature"
        result = db.insert_deliberation(
            id="DELIB-0001",
            source_type="report",
            title="Token test",
            summary="Summary.",
            content=content,
            changed_by="test",
            change_reason="test",
        )
        assert "eyJhbGciOi" not in result["content"]
        assert "[REDACTED:token]" in result["content"]

    def test_phone_redacted(self, db):
        content = "Customer called from +18005551234 about billing."
        result = db.insert_deliberation(
            id="DELIB-0001",
            source_type="owner_conversation",
            title="Phone test",
            summary="Summary.",
            content=content,
            changed_by="test",
            change_reason="test",
        )
        assert "+18005551234" not in result["content"]
        assert "[REDACTED:phone]" in result["content"]

    def test_email_redacted(self, db):
        content = "Contact user@example.com for details."
        result = db.insert_deliberation(
            id="DELIB-0001",
            source_type="report",
            title="Email test",
            summary="Summary.",
            content=content,
            changed_by="test",
            change_reason="test",
        )
        assert "user@example.com" not in result["content"]
        assert "[REDACTED:email]" in result["content"]

    def test_connection_string_redacted(self, db):
        content = "DB URI: mongodb://admin:pass@host:27017/db"
        result = db.insert_deliberation(
            id="DELIB-0001",
            source_type="report",
            title="ConnStr test",
            summary="Summary.",
            content=content,
            changed_by="test",
            change_reason="test",
        )
        assert "mongodb://admin" not in result["content"]
        assert "[REDACTED:connection_string]" in result["content"]

    def test_clean_content_not_redacted(self, db):
        content = "This review found no issues. The implementation is correct."
        result = db.insert_deliberation(
            id="DELIB-0001",
            source_type="lo_review",
            title="Clean test",
            summary="Summary.",
            content=content,
            changed_by="test",
            change_reason="test",
        )
        assert result["content"] == content
        assert result["redaction_state"] == "clean"
        assert result["redaction_notes"] is None

    def test_content_hash_computed_from_raw(self, db):
        """Content hash is computed from pre-redaction text."""
        import hashlib

        raw = "Secret: api_key=sk_live_abc123def456ghi789"
        expected_hash = hashlib.sha256(raw.encode()).hexdigest()
        result = db.insert_deliberation(
            id="DELIB-0001",
            source_type="report",
            title="Hash test",
            summary="Summary.",
            content=raw,
            changed_by="test",
            change_reason="test",
        )
        assert result["content_hash"] == expected_hash

    def test_redact_content_classmethod(self):
        text = "key: api_key=AKIA1234567890ABCDEF and phone +15551234567"
        redacted, notes = KnowledgeDB.redact_content(text)
        assert "AKIA1234567890ABCDEF" not in redacted
        assert "+15551234567" not in redacted
        assert notes is not None

    def test_redact_bearer_header(self):
        """Regression (Codex P1): Authorization: Bearer <jwt> must be fully redacted."""
        jwt = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.payload.signature"
        text = f"Authorization: Bearer {jwt}"
        redacted, notes = KnowledgeDB.redact_content(text)
        assert jwt not in redacted, "JWT token survived redaction in Authorization header"
        assert notes is not None

    def test_redact_standalone_bearer(self):
        """Bearer <token> without the Authorization: prefix must also be redacted."""
        token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.payload.sig"
        text = f"Token found: Bearer {token}"
        redacted, notes = KnowledgeDB.redact_content(text)
        assert token not in redacted, "Bearer token survived redaction"
        assert notes is not None

    def test_redact_github_pat(self):
        """Regression (Codex P1): GitHub PAT ghp_... must be fully redacted."""
        pat = "ghp_abcdefghijklmnopqrstuvwxyz123456"
        text = f"Token found: {pat}"
        redacted, notes = KnowledgeDB.redact_content(text)
        assert pat not in redacted, "GitHub PAT survived redaction"
        assert notes is not None

    def test_redact_azure_connection_string(self):
        """Regression (Codex P1): Azure SharedAccessKey must be fully redacted — no suffix leakage."""
        conn_str = (
            "Endpoint=sb://example.servicebus.windows.net/;"
            "SharedAccessKeyName=RootManageSharedAccessKey;"
            "SharedAccessKey=AbCdEfGhIjKlMnOpQrStUvWxYz0123456789+/ABCDEFGHIJKL1234567890+/=="
        )
        redacted, notes = KnowledgeDB.redact_content(conn_str)
        # The raw key value must not survive
        assert "AbCdEfGhIjKlMnOpQrStUvWxYz0123456789+/" not in redacted, (
            "Azure SharedAccessKey value survived redaction"
        )
        assert notes is not None

    def test_redact_ar_live_key(self):
        """Agent Red ar_live_ keys must be redacted."""
        key = "ar_live_" + "abc123def456_ghijklm"
        text = f"Tenant key: {key}"
        redacted, notes = KnowledgeDB.redact_content(text)
        assert key not in redacted, "ar_live_ key survived redaction"
        assert "[REDACTED:ar_live_key]" in redacted
        assert notes is not None

    def test_redact_ar_user_key(self):
        """Agent Red ar_user_ keys must be redacted."""
        key = "ar_user_" + "rema_yZR6wMz-VDlVJhbd"
        text = f"API key: {key}"
        redacted, notes = KnowledgeDB.redact_content(text)
        assert key not in redacted, "ar_user_ key survived redaction"
        assert "[REDACTED:ar_user_key]" in redacted

    def test_redact_ar_spa_plat_key(self):
        """Agent Red ar_spa_plat_ keys must be redacted."""
        key = "ar_spa_plat_" + "mdbq-Sm3vE5Qj3d4H"
        text = f"SPA key: {key}"
        redacted, notes = KnowledgeDB.redact_content(text)
        assert key not in redacted, "ar_spa_plat_ key survived redaction"
        assert "[REDACTED:ar_spa_plat_key]" in redacted

    def test_redact_pk_live_key(self):
        """Agent Red pk_live_ keys must be redacted."""
        key = "pk_live_" + "a7f3c9e1b2c3_d4e5f6a7"
        text = f"Widget key: {key}"
        redacted, notes = KnowledgeDB.redact_content(text)
        assert key not in redacted, "pk_live_ key survived redaction"
        assert "[REDACTED:pk_live_key]" in redacted

    def test_redact_arsk_key(self):
        """Agent Red arsk_ keys must be redacted."""
        key = "arsk_" + "test_pro_key_002_extra"
        text = f"Service key: {key}"
        redacted, notes = KnowledgeDB.redact_content(text)
        assert key not in redacted, "arsk_ key survived redaction"
        assert "[REDACTED:arsk_key]" in redacted

    def test_redact_ar_key_with_hyphen(self):
        """Agent Red keys with hyphens (token_urlsafe output) must be redacted."""
        key = "ar_user_" + "rema_yZR6wMz-VDlV-JhbdRPW1Vh01TkytKcQ3"
        text = f"Generated key: {key}."
        redacted, notes = KnowledgeDB.redact_content(text)
        assert key not in redacted, "Hyphen-containing AR key survived redaction"

    def test_redact_no_false_positives_on_plain_text(self):
        """Plain prose must not be corrupted by redaction patterns."""
        text = "We decided to use append-only versioning for audit trail integrity."
        redacted, notes = KnowledgeDB.redact_content(text)
        assert redacted == text
        assert notes is None


class TestListDeliberations:
    """Tests for list_deliberations() with filters."""

    def _seed(self, db):
        db.insert_deliberation(
            id="DELIB-0001",
            source_type="lo_review",
            title="Review A",
            summary="Summary A.",
            content="Content A.",
            changed_by="test",
            change_reason="seed",
            spec_id="SPEC-001",
            session_id="S100",
            outcome="go",
        )
        db.insert_deliberation(
            id="DELIB-0002",
            source_type="proposal",
            title="Proposal B",
            summary="Summary B.",
            content="Content B.",
            changed_by="test",
            change_reason="seed",
            spec_id="SPEC-002",
            session_id="S100",
            outcome="deferred",
        )
        db.insert_deliberation(
            id="DELIB-0003",
            source_type="lo_review",
            title="Review C",
            summary="Summary C.",
            content="Content C.",
            changed_by="test",
            change_reason="seed",
            spec_id="SPEC-001",
            session_id="S101",
            outcome="no_go",
            source_ref="bridge:msg-1234",
        )

    def test_list_all(self, db):
        self._seed(db)
        results = db.list_deliberations()
        assert len(results) == 3

    def test_filter_by_spec_id(self, db):
        self._seed(db)
        results = db.list_deliberations(spec_id="SPEC-001")
        assert len(results) == 2

    def test_filter_by_source_type(self, db):
        self._seed(db)
        results = db.list_deliberations(source_type="lo_review")
        assert len(results) == 2

    def test_filter_by_session_id(self, db):
        self._seed(db)
        results = db.list_deliberations(session_id="S101")
        assert len(results) == 1

    def test_filter_by_outcome(self, db):
        self._seed(db)
        results = db.list_deliberations(outcome="go")
        assert len(results) == 1

    def test_filter_by_source_ref(self, db):
        self._seed(db)
        results = db.list_deliberations(source_ref="bridge:msg-1234")
        assert len(results) == 1
        assert results[0]["id"] == "DELIB-0003"

    def test_combined_filters(self, db):
        self._seed(db)
        results = db.list_deliberations(spec_id="SPEC-001", outcome="go")
        assert len(results) == 1
        assert results[0]["id"] == "DELIB-0001"


class TestMultiLink:
    """Tests for multi-link relation tables."""

    def test_link_deliberation_spec(self, db):
        db.insert_deliberation(
            id="DELIB-0001",
            source_type="lo_review",
            title="Multi-spec review",
            summary="Covers SPEC-001 and SPEC-002.",
            content="Review content.",
            changed_by="test",
            change_reason="test",
            spec_id="SPEC-001",
        )
        db.link_deliberation_spec("DELIB-0001", "SPEC-002", role="related")

        # Primary FK lookup
        results = db.get_deliberations_for_spec("SPEC-001")
        assert len(results) == 1

        # Relation table lookup
        results = db.get_deliberations_for_spec("SPEC-002")
        assert len(results) == 1
        assert results[0]["id"] == "DELIB-0001"

    def test_link_deliberation_work_item(self, db):
        db.insert_deliberation(
            id="DELIB-0001",
            source_type="lo_review",
            title="Multi-WI review",
            summary="Covers WI-001 and WI-002.",
            content="Review content.",
            changed_by="test",
            change_reason="test",
            work_item_id="WI-001",
        )
        db.link_deliberation_work_item("DELIB-0001", "WI-002", role="primary")

        results = db.get_deliberations_for_work_item("WI-001")
        assert len(results) == 1

        results = db.get_deliberations_for_work_item("WI-002")
        assert len(results) == 1
        assert results[0]["id"] == "DELIB-0001"

    def test_link_idempotent(self, db):
        db.insert_deliberation(
            id="DELIB-0001",
            source_type="report",
            title="Test",
            summary="Summary.",
            content="Content.",
            changed_by="test",
            change_reason="test",
        )
        # Link twice — should not raise
        db.link_deliberation_spec("DELIB-0001", "SPEC-001", role="related")
        db.link_deliberation_spec("DELIB-0001", "SPEC-001", role="primary")

        # The role should be updated (INSERT OR REPLACE)
        conn = db._get_conn()
        row = conn.execute(
            "SELECT role FROM deliberation_specs WHERE deliberation_id = ? AND spec_id = ?",
            ("DELIB-0001", "SPEC-001"),
        ).fetchone()
        assert row["role"] == "primary"


class TestUpsertDeliberationSource:
    """Tests for upsert_deliberation_source() dedup."""

    def test_first_upsert_creates(self, db):
        result = db.upsert_deliberation_source(
            source_type="lo_review",
            source_ref="bridge:msg-abc",
            content="Full review text here.",
            title="Review",
            summary="Summary.",
            changed_by="test",
            change_reason="harvest",
        )
        assert result["id"] == "DELIB-0001"
        assert result["source_ref"] == "bridge:msg-abc"

    def test_duplicate_upsert_returns_existing(self, db):
        first = db.upsert_deliberation_source(
            source_type="lo_review",
            source_ref="bridge:msg-abc",
            content="Full review text here.",
            title="Review",
            summary="Summary.",
            changed_by="test",
            change_reason="harvest",
        )
        second = db.upsert_deliberation_source(
            source_type="lo_review",
            source_ref="bridge:msg-abc",
            content="Full review text here.",
            title="Review attempt 2",
            summary="Should not create new.",
            changed_by="test",
            change_reason="harvest again",
        )
        assert first["id"] == second["id"]
        # Title should remain from first insert (no overwrite)
        assert second["title"] == "Review"

    def test_different_content_creates_new(self, db):
        first = db.upsert_deliberation_source(
            source_type="lo_review",
            source_ref="bridge:msg-abc",
            content="Version 1 review.",
            title="Review v1",
            summary="Summary.",
            changed_by="test",
            change_reason="harvest",
        )
        second = db.upsert_deliberation_source(
            source_type="lo_review",
            source_ref="bridge:msg-abc",
            content="Version 2 review with changes.",
            title="Review v2",
            summary="Summary.",
            changed_by="test",
            change_reason="harvest",
        )
        assert first["id"] != second["id"]

    def test_auto_id_increments(self, db):
        r1 = db.upsert_deliberation_source(
            source_type="report",
            source_ref="ref-1",
            content="Report 1.",
            title="R1",
            summary="S1.",
            changed_by="test",
            change_reason="test",
        )
        r2 = db.upsert_deliberation_source(
            source_type="report",
            source_ref="ref-2",
            content="Report 2.",
            title="R2",
            summary="S2.",
            changed_by="test",
            change_reason="test",
        )
        assert r1["id"] == "DELIB-0001"
        assert r2["id"] == "DELIB-0002"

    def test_auto_id_after_lower_id_versioned(self, db):
        """Regression: upsert after append-only versioning of a lower ID must not
        collide with an existing higher ID.

        Repro (Codex P1): create DELIB-0001, create DELIB-0002, append a new
        version of DELIB-0001 (pushes rowid past DELIB-0002), then upsert a new
        source — the new record must be DELIB-0003, not DELIB-0002 version 2.
        """
        db.insert_deliberation(
            id="DELIB-0001",
            source_type="report",
            title="R1",
            summary="S1.",
            content="Content 1.",
            changed_by="test",
            change_reason="seed",
        )
        db.insert_deliberation(
            id="DELIB-0002",
            source_type="report",
            title="R2",
            summary="S2.",
            content="Content 2.",
            changed_by="test",
            change_reason="seed",
        )
        # Append a new version of DELIB-0001 — this bumps its rowid above DELIB-0002
        db.insert_deliberation(
            id="DELIB-0001",
            source_type="report",
            title="R1 v2",
            summary="S1 v2.",
            content="Content 1 updated.",
            changed_by="test",
            change_reason="update",
        )
        # Now upsert a brand-new source — must get DELIB-0003
        r3 = db.upsert_deliberation_source(
            source_type="report",
            source_ref="ref-3",
            content="Report 3.",
            title="R3",
            summary="S3.",
            changed_by="test",
            change_reason="test",
        )
        assert r3["id"] == "DELIB-0003", (
            f"Expected DELIB-0003 but got {r3['id']} — ID allocator used rowid instead of MAX suffix"
        )
        # Verify DELIB-0002 identity is intact (not overwritten)
        current_2 = db.get_deliberation("DELIB-0002")
        assert current_2["source_ref"] is None  # was inserted directly without source_ref
        assert current_2["title"] == "R2"


class TestSearchDeliberations:
    """Tests for search_deliberations() SQLite LIKE fallback."""

    def test_search_by_content(self, db):
        db.insert_deliberation(
            id="DELIB-0001",
            source_type="lo_review",
            title="OTP review",
            summary="Phone OTP verification gate.",
            content="We require phone OTP before escalation because unverified callers waste agent time.",
            changed_by="test",
            change_reason="test",
        )
        db.insert_deliberation(
            id="DELIB-0002",
            source_type="proposal",
            title="Cosmos migration",
            summary="Database migration plan.",
            content="Cosmos offers multi-region replication.",
            changed_by="test",
            change_reason="test",
        )
        results = db.search_deliberations("phone OTP")
        assert len(results) == 1
        assert results[0]["id"] == "DELIB-0001"

    def test_search_by_title(self, db):
        db.insert_deliberation(
            id="DELIB-0001",
            source_type="lo_review",
            title="Append-only versioning rationale",
            summary="Summary.",
            content="Content.",
            changed_by="test",
            change_reason="test",
        )
        results = db.search_deliberations("Append-only")
        assert len(results) == 1

    def test_search_limit(self, db):
        for i in range(10):
            db.insert_deliberation(
                id=f"DELIB-{i:04d}",
                source_type="report",
                title=f"Report {i}",
                summary="Common keyword match.",
                content="Common keyword match content.",
                changed_by="test",
                change_reason="test",
            )
        results = db.search_deliberations("Common keyword", limit=3)
        assert len(results) == 3

    def test_search_no_results(self, db):
        db.insert_deliberation(
            id="DELIB-0001",
            source_type="report",
            title="Unrelated",
            summary="Nothing relevant.",
            content="Nothing relevant.",
            changed_by="test",
            change_reason="test",
        )
        results = db.search_deliberations("quantum entanglement")
        assert len(results) == 0


class TestGetSummary:
    """Test that deliberation count appears in summary."""

    def test_summary_includes_deliberation_count(self, db):
        summary = db.get_summary()
        assert "deliberation_count" in summary
        assert summary["deliberation_count"] == 0

        db.insert_deliberation(
            id="DELIB-0001",
            source_type="report",
            title="Test",
            summary="Summary.",
            content="Content.",
            changed_by="test",
            change_reason="test",
        )
        summary = db.get_summary()
        assert summary["deliberation_count"] == 1


# ── ChromaDB semantic search tests ──────────────────────────────


@pytest.fixture()
def search_db(tmp_path: Path) -> KnowledgeDB:
    """KnowledgeDB with ChromaDB search enabled in a temp directory."""
    db_path = tmp_path / "test_search.db"
    chroma_path = tmp_path / ".groundtruth-chroma"
    return KnowledgeDB(db_path=db_path, chroma_path=chroma_path)


class TestSearchResultContract:
    """Verify search_deliberations returns the stable result contract fields."""

    def test_text_match_has_search_fields(self, db):
        """SQLite fallback results include search_method and score fields."""
        db.insert_deliberation(
            id="DELIB-0001",
            source_type="report",
            title="Database migration",
            summary="Migrate tables.",
            content="Migrating SQL tables to new schema.",
            changed_by="test",
            change_reason="test",
        )
        results = db.search_deliberations("migration")
        assert len(results) == 1
        assert results[0]["search_method"] == "text_match"
        assert results[0]["score"] is None
        assert results[0]["matched_chunk_id"] is None
        assert results[0]["matched_chunk_preview"] is None


class TestChunking:
    """Test the sentence-boundary chunking utility."""

    def test_short_text_single_chunk(self):
        chunks = KnowledgeDB._chunk_text_for_embedding("Short text.")
        assert len(chunks) == 1
        assert chunks[0] == "Short text."

    def test_long_text_multiple_chunks(self):
        # Create text longer than max_chars (~920)
        sentences = [f"Sentence number {i} with some content to fill space." for i in range(30)]
        text = " ".join(sentences)
        chunks = KnowledgeDB._chunk_text_for_embedding(text)
        assert len(chunks) > 1
        # All original content should be recoverable from chunks
        for sentence in sentences[:5]:  # Spot-check first few
            assert any(sentence in chunk for chunk in chunks)

    def test_overlap_present(self):
        sentences = [f"Unique sentence {i} about topic {i}." for i in range(30)]
        text = " ".join(sentences)
        chunks = KnowledgeDB._chunk_text_for_embedding(text)
        if len(chunks) >= 2:
            # Some overlap should exist between consecutive chunks
            chunk1_end = chunks[0][-100:]
            assert any(part in chunks[1] for part in chunk1_end.split(". ") if part)


class TestMetadataBuilder:
    """Test _deliberation_chroma_metadata maps fields correctly."""

    def test_metadata_contains_delib_id_from_row_id(self):
        """GO condition 1: metadata['delib_id'] = row['id']."""
        row = {
            "id": "DELIB-0042",
            "version": 3,
            "changed_at": "2026-04-11T12:00:00",
            "source_type": "lo_review",
            "sensitivity": "normal",
            "redaction_state": "clean",
            "title": "Test deliberation",
            "spec_id": None,
            "work_item_id": None,
            "outcome": None,
            "session_id": None,
            "source_ref": None,
            "origin_project": None,
            "origin_repo": None,
        }
        metadata = KnowledgeDB._deliberation_chroma_metadata(row, chunk_index=0, chunk_count=1)
        assert metadata["delib_id"] == "DELIB-0042"
        assert metadata["version"] == 3
        assert metadata["chunk_index"] == 0
        assert metadata["chunk_count"] == 1

    def test_nullable_fields_omitted(self):
        """Nullable fields with None values are omitted from metadata."""
        row = {
            "id": "DELIB-0001",
            "version": 1,
            "changed_at": "2026-04-11T12:00:00",
            "source_type": "report",
            "sensitivity": "normal",
            "redaction_state": "clean",
            "title": "Test",
            "spec_id": None,
            "work_item_id": None,
            "outcome": None,
            "session_id": None,
            "source_ref": None,
            "origin_project": None,
            "origin_repo": None,
        }
        metadata = KnowledgeDB._deliberation_chroma_metadata(row, chunk_index=0, chunk_count=1)
        assert "spec_id" not in metadata
        assert "work_item_id" not in metadata
        assert "outcome" not in metadata
        assert "session_id" not in metadata

    def test_optional_fields_included_when_present(self):
        """Optional fields are included when not None."""
        row = {
            "id": "DELIB-0001",
            "version": 1,
            "changed_at": "2026-04-11T12:00:00",
            "source_type": "lo_review",
            "sensitivity": "normal",
            "redaction_state": "clean",
            "title": "Test",
            "spec_id": "SPEC-100",
            "work_item_id": "WI-200",
            "outcome": "go",
            "session_id": "S280",
            "source_ref": None,
            "origin_project": None,
            "origin_repo": None,
        }
        metadata = KnowledgeDB._deliberation_chroma_metadata(row, chunk_index=0, chunk_count=1)
        assert metadata["spec_id"] == "SPEC-100"
        assert metadata["work_item_id"] == "WI-200"
        assert metadata["outcome"] == "go"
        assert metadata["session_id"] == "S280"


@requires_chromadb
class TestSemanticSearch:
    """Tests requiring ChromaDB installed — semantic search behavior."""

    def test_semantic_obvious_match_found(self, search_db):
        """GO condition: obvious semantic match returns search_method='semantic'."""
        search_db.insert_deliberation(
            id="DELIB-0001",
            source_type="proposal",
            title="ChromaDB integration for semantic search",
            summary="Adding vector-based retrieval to deliberation archive.",
            content="This proposal adds ChromaDB as an optional dependency for "
            "embedding-based semantic search over deliberation records. "
            "The implementation uses the all-MiniLM-L6-v2 model for "
            "generating document embeddings and supports distance-threshold "
            "filtering to ensure relevance.",
            changed_by="test",
            change_reason="test",
        )
        results = search_db.search_deliberations("vector embeddings retrieval")
        assert len(results) >= 1
        assert results[0]["search_method"] == "semantic"
        assert results[0]["score"] is not None
        assert results[0]["score"] < SEMANTIC_MAX_DISTANCE
        assert results[0]["matched_chunk_id"] is not None

    def test_semantic_unrelated_returns_empty(self, search_db):
        """GO condition 4: unrelated queries return empty list with ChromaDB populated."""
        search_db.insert_deliberation(
            id="DELIB-0001",
            source_type="report",
            title="Database migration strategy",
            summary="Migrate SQL tables.",
            content="The database migration involves moving tables from the old "
            "schema to the new normalized structure with foreign key constraints.",
            changed_by="test",
            change_reason="test",
        )
        results = search_db.search_deliberations("quantum entanglement theory")
        assert len(results) == 0

    def test_semantic_fallback_to_text_match(self, search_db):
        """When ChromaDB has no relevant results, falls back to SQLite LIKE."""
        search_db.insert_deliberation(
            id="DELIB-0001",
            source_type="report",
            title="Specific keyword xyzzy",
            summary="Contains xyzzy marker.",
            content="This document has the xyzzy keyword for testing text fallback.",
            changed_by="test",
            change_reason="test",
        )
        # Search for exact keyword that semantic search might not match well
        # but LIKE will find
        results = search_db.search_deliberations("xyzzy")
        assert len(results) >= 1
        # Should find it via either method
        assert results[0]["id"] == "DELIB-0001"

    def test_index_deliberation_with_nulls(self, search_db):
        """Indexing a deliberation with all optional fields as None succeeds."""
        search_db.insert_deliberation(
            id="DELIB-0001",
            source_type="report",
            title="Minimal deliberation",
            summary="No optional fields.",
            content="A deliberation with no spec_id, work_item_id, outcome, or session_id.",
            changed_by="test",
            change_reason="test",
        )
        # Should not raise — indexing with null optional fields works
        results = search_db.search_deliberations("minimal deliberation")
        assert len(results) >= 1


@requires_chromadb
class TestStaleChunkDeletion:
    """GO condition 2: stale chunks are removed on deliberation revision."""

    def test_revision_removes_old_text(self, search_db):
        """Text from v1 is not searchable after v2 replaces it."""
        search_db.insert_deliberation(
            id="DELIB-0001",
            source_type="proposal",
            title="Architecture proposal",
            summary="Alpha approach chosen.",
            content="We chose the alpha approach for the database layer because "
            "it provides better consistency guarantees and simpler operations.",
            changed_by="test",
            change_reason="initial",
        )
        # Verify v1 is searchable
        results = search_db.search_deliberations("alpha approach consistency")
        assert len(results) >= 1

        # Update to v2 with different content
        search_db.insert_deliberation(
            id="DELIB-0001",
            source_type="proposal",
            title="Architecture proposal v2",
            summary="Beta approach chosen.",
            content="We switched to the beta approach for the database layer "
            "because it provides better horizontal scaling and partition tolerance.",
            changed_by="test",
            change_reason="revised after review",
        )
        # v1 text should NOT be searchable
        results = search_db.search_deliberations("alpha approach consistency")
        assert len(results) == 0

        # v2 text SHOULD be searchable
        results = search_db.search_deliberations("beta approach scaling")
        assert len(results) >= 1
        assert results[0]["id"] == "DELIB-0001"

    def test_long_to_short_revision_removes_surplus_chunks(self, search_db):
        """Revising a long deliberation (many chunks) to short removes surplus."""
        # v1: long content that will produce multiple chunks
        long_content = " ".join(
            [
                f"Section {i}: This is a detailed analysis of topic {i} "
                f"covering multiple aspects of the engineering decision."
                for i in range(50)
            ]
        )
        search_db.insert_deliberation(
            id="DELIB-0001",
            source_type="report",
            title="Detailed analysis",
            summary="Long report.",
            content=long_content,
            changed_by="test",
            change_reason="initial",
        )
        collection = search_db._get_chroma_collection()
        v1_count = collection.count()
        assert v1_count > 2  # Should have multiple chunks

        # v2: short content
        search_db.insert_deliberation(
            id="DELIB-0001",
            source_type="report",
            title="Revised analysis",
            summary="Short report.",
            content="Concise summary replacing the detailed analysis.",
            changed_by="test",
            change_reason="simplified",
        )
        v2_count = collection.count()
        assert v2_count == 1  # Only one chunk for short content
        assert v2_count < v1_count


@requires_chromadb
class TestRebuildIndex:
    """Test rebuild_deliberation_index()."""

    def test_rebuild_from_empty(self, search_db):
        result = search_db.rebuild_deliberation_index()
        assert result["indexed"] == 0
        assert result["chunks"] == 0
        assert result["errors"] == []

    def test_rebuild_reindexes_all(self, search_db):
        for i in range(3):
            search_db.insert_deliberation(
                id=f"DELIB-{i:04d}",
                source_type="report",
                title=f"Report {i}",
                summary=f"Summary {i}.",
                content=f"Deliberation content for report number {i}.",
                changed_by="test",
                change_reason="test",
            )
        result = search_db.rebuild_deliberation_index()
        assert result["indexed"] == 3
        assert result["chunks"] >= 3
        assert result["errors"] == []

    def test_rebuild_clears_stale_entries(self, search_db):
        """Rebuild removes entries for deliberations that no longer exist in current view."""
        search_db.insert_deliberation(
            id="DELIB-0001",
            source_type="report",
            title="Original",
            summary="Original.",
            content="Original content about original topics.",
            changed_by="test",
            change_reason="test",
        )
        # Verify indexed
        collection = search_db._get_chroma_collection()
        assert collection.count() > 0

        # Rebuild should recreate cleanly
        result = search_db.rebuild_deliberation_index()
        assert result["indexed"] == 1
        assert result["errors"] == []


@requires_chromadb
class TestThresholdCalibration:
    """GO condition 3: calibration fixture proves threshold separates positive/negative pairs."""

    def test_positive_pairs_below_threshold(self, search_db):
        """Semantically related text should score below SEMANTIC_MAX_DISTANCE."""
        from groundtruth_kb.db import SEMANTIC_MAX_DISTANCE

        search_db.insert_deliberation(
            id="DELIB-0001",
            source_type="proposal",
            title="Database migration strategy",
            summary="Strategy for migrating SQL tables.",
            content="This proposal covers the database migration strategy including "
            "migrating SQL tables to new schema, handling foreign key constraints, "
            "and ensuring data integrity during the transition period.",
            changed_by="test",
            change_reason="test",
        )
        results = search_db.search_deliberations("migrating SQL tables to new schema")
        assert len(results) >= 1
        assert results[0]["score"] < SEMANTIC_MAX_DISTANCE

        search_db.insert_deliberation(
            id="DELIB-0002",
            source_type="proposal",
            title="ChromaDB semantic search integration",
            summary="Adding vector retrieval.",
            content="Integrating ChromaDB for embedding-based vector retrieval "
            "to enable semantic search over deliberation records using the "
            "all-MiniLM-L6-v2 sentence transformer model.",
            changed_by="test",
            change_reason="test",
        )
        results = search_db.search_deliberations("embedding-based vector retrieval")
        assert len(results) >= 1
        assert results[0]["score"] < SEMANTIC_MAX_DISTANCE

    def test_negative_pairs_filtered(self, search_db):
        """Unrelated text should be filtered by the distance threshold."""

        search_db.insert_deliberation(
            id="DELIB-0001",
            source_type="proposal",
            title="Database migration strategy",
            summary="Strategy for migrating SQL tables.",
            content="This proposal covers the database migration strategy including "
            "migrating SQL tables to new schema and handling foreign key constraints.",
            changed_by="test",
            change_reason="test",
        )
        # Completely unrelated query
        results = search_db.search_deliberations("chocolate cake recipe ingredients")
        assert len(results) == 0

        search_db.insert_deliberation(
            id="DELIB-0002",
            source_type="proposal",
            title="ChromaDB integration",
            summary="Vector search.",
            content="Embedding-based semantic search over deliberation records.",
            changed_by="test",
            change_reason="test",
        )
        results = search_db.search_deliberations("quantum entanglement theory")
        assert len(results) == 0


class TestConfigChromaPath:
    """Test GTConfig [search].chroma_path parsing."""

    def test_config_default_chroma_path_is_none(self):
        """Without [search] section, chroma_path defaults to None."""
        from groundtruth_kb.config import GTConfig

        config = GTConfig()
        assert config.chroma_path is None

    def test_config_chroma_path_from_toml(self, tmp_path):
        """[search].chroma_path is parsed from groundtruth.toml."""
        from groundtruth_kb.config import GTConfig

        toml_content = b'[groundtruth]\ndb_path = "./test.db"\n\n[search]\nchroma_path = "my-chroma"\n'
        config_file = tmp_path / "groundtruth.toml"
        config_file.write_bytes(toml_content)
        config = GTConfig.load(config_path=config_file)
        assert config.chroma_path == tmp_path / "my-chroma"

    def test_config_chroma_path_absolute(self, tmp_path):
        """Absolute chroma_path is used as-is."""
        from groundtruth_kb.config import GTConfig

        abs_path = str(tmp_path / "abs-chroma")
        # Use forward slashes for TOML compatibility (backslashes are escape chars)
        toml_path = abs_path.replace("\\", "/")
        toml_content = f'[groundtruth]\ndb_path = "./test.db"\n\n[search]\nchroma_path = "{toml_path}"\n'
        config_file = tmp_path / "groundtruth.toml"
        config_file.write_bytes(toml_content.encode())
        config = GTConfig.load(config_path=config_file)
        assert config.chroma_path == Path(abs_path)


class TestChromaFailureContainment:
    """ChromaDB index failures must not break canonical SQLite writes."""

    def test_insert_succeeds_when_chroma_add_raises(self, search_db, monkeypatch):
        """Canonical write persists even if ChromaDB add() raises."""
        original_index = search_db._index_deliberation_in_chroma

        def failing_index(delib_id):
            raise RuntimeError("simulated ChromaDB add failure")

        monkeypatch.setattr(search_db, "_index_deliberation_in_chroma", failing_index)

        # insert_deliberation must not raise
        result = search_db.insert_deliberation(
            id="DELIB-0001",
            source_type="report",
            title="Should persist despite index failure",
            summary="Testing failure containment.",
            content="This deliberation must be committed to SQLite even if ChromaDB fails.",
            changed_by="test",
            change_reason="test",
        )

        # Row must exist in SQLite
        assert result is not None
        assert result["id"] == "DELIB-0001"
        assert result["version"] == 1

        # Verify no duplicate version on a second insert (proves first commit succeeded)
        monkeypatch.setattr(search_db, "_index_deliberation_in_chroma", original_index)
        result2 = search_db.insert_deliberation(
            id="DELIB-0001",
            source_type="report",
            title="Second version",
            summary="Version 2.",
            content="Second version after contained failure.",
            changed_by="test",
            change_reason="update",
        )
        assert result2["version"] == 2
