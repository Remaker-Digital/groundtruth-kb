"""Tests for deliberation archive CRUD, redaction, multi-link, and dedup.

Copyright (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
Licensed under AGPL-3.0-or-later.
"""

from __future__ import annotations

import pytest

from groundtruth_kb.db import KnowledgeDB


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
                summary=f"Summary.",
                content=f"Content.",
                changed_by="test",
                change_reason=f"test",
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
            id="DELIB-0001", source_type="report", title="R1", summary="S1.",
            content="Content 1.", changed_by="test", change_reason="seed",
        )
        db.insert_deliberation(
            id="DELIB-0002", source_type="report", title="R2", summary="S2.",
            content="Content 2.", changed_by="test", change_reason="seed",
        )
        # Append a new version of DELIB-0001 — this bumps its rowid above DELIB-0002
        db.insert_deliberation(
            id="DELIB-0001", source_type="report", title="R1 v2", summary="S1 v2.",
            content="Content 1 updated.", changed_by="test", change_reason="update",
        )
        # Now upsert a brand-new source — must get DELIB-0003
        r3 = db.upsert_deliberation_source(
            source_type="report", source_ref="ref-3", content="Report 3.",
            title="R3", summary="S3.", changed_by="test", change_reason="test",
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
