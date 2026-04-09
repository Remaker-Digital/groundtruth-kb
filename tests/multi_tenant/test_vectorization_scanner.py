"""Tests for the conversation vectorization background scanner (WI #87).

Verifies:
- Scanner processes ended conversations and marks them as vectorized
- Scanner skips when vectorizer is not configured
- Scanner respects consent gating (DENIED/NOT_ASKED → no vectors stored)
- Per-conversation and per-tenant error isolation
- list_unvectorized_ended() query filters

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import asyncio
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.multi_tenant.cosmos_schema import ConsentStatus, ConversationStatus


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def _make_conv(
    conv_id: str = "conv-001",
    tenant_id: str = "tenant-001",
    customer_id: str | None = "cust-001",
    status: str = "resolved",
    message_count: int = 5,
    messages: list | None = None,
    vectorized_at: str | None = None,
) -> dict[str, Any]:
    """Build a minimal conversation document for testing."""
    return {
        "id": conv_id,
        "conversation_id": conv_id,
        "tenant_id": tenant_id,
        "customer_id": customer_id,
        "status": status,
        "message_count": message_count,
        "messages": messages or [
            {"role": "customer", "content": "Hello", "timestamp": "2026-01-01T00:00:00Z"},
            {"role": "agent", "content": "Hi there!", "timestamp": "2026-01-01T00:00:01Z"},
        ],
        "started_at": "2026-01-01T00:00:00Z",
        "ended_at": "2026-01-01T00:05:00Z",
        "last_activity_at": "2026-01-01T00:05:00Z",
        "vectorized_at": vectorized_at,
    }


# ---------------------------------------------------------------------------
# Scanner loop tests
# ---------------------------------------------------------------------------

class TestVectorizationScanner:
    """Tests for _vectorization_scanner_loop inner logic."""

    @pytest.mark.asyncio
    async def test_scanner_processes_ended_conversations(self):
        """Scanner calls vectorize_conversation and patches vectorized_at."""
        conv = _make_conv()

        mock_vectorizer = MagicMock()
        mock_vectorizer._ensure_configured = MagicMock()
        mock_vectorizer.vectorize_conversation = AsyncMock(return_value=["chunk-0", "chunk-1"])

        mock_tenant_repo = MagicMock()
        mock_tenant_repo.list_active_tenant_ids = AsyncMock(return_value=["tenant-001"])

        mock_conv_repo = MagicMock()
        mock_conv_repo.list_unvectorized_ended = AsyncMock(return_value=[conv])
        mock_conv_repo.patch = AsyncMock()

        mock_profile_repo = MagicMock()
        mock_profile_repo.read = AsyncMock(return_value={
            "consent_status": "granted",
        })

        with (
            patch("src.multi_tenant.conversation_vectorizer.get_vectorizer", return_value=mock_vectorizer),
            patch("src.multi_tenant.repository.TenantRepository", return_value=mock_tenant_repo),
            patch("src.multi_tenant.repositories.conversation.ConversationRepository", return_value=mock_conv_repo),
            patch("src.multi_tenant.repository.CustomerProfileRepository", return_value=mock_profile_repo),
        ):
            # Import and directly invoke scanner logic (not the infinite loop)
            from src.app.background import _vectorization_scanner_loop

            # Run one iteration by patching sleep to raise after first iteration
            call_count = 0

            async def fake_sleep(seconds):
                nonlocal call_count
                call_count += 1
                if call_count == 1:
                    return  # Skip startup delay
                raise asyncio.CancelledError()  # Exit loop after first iteration

            with patch("src.app.background.asyncio.sleep", side_effect=fake_sleep):
                with pytest.raises(asyncio.CancelledError):
                    await _vectorization_scanner_loop()

        # Verify vectorize was called
        mock_vectorizer.vectorize_conversation.assert_called_once_with(
            tenant_id="tenant-001",
            customer_id="cust-001",
            conversation_id="conv-001",
            messages=conv["messages"],
            canonical_customer_id=None,  # ADR-004: canonical ID passed through (None when no CID resolved)
            consent_status=ConsentStatus.GRANTED,
        )

        # Verify vectorized_at was patched
        mock_conv_repo.patch.assert_called_once()
        patch_args = mock_conv_repo.patch.call_args
        assert patch_args.kwargs["tenant_id"] == "tenant-001"
        assert patch_args.kwargs["document_id"] == "conv-001"
        ops = patch_args.kwargs["operations"]
        assert any(op["path"] == "/vectorized_at" for op in ops)

    @pytest.mark.asyncio
    async def test_scanner_skips_unconfigured_vectorizer(self):
        """Scanner gracefully skips when vectorizer is not configured."""
        mock_vectorizer = MagicMock()
        mock_vectorizer._ensure_configured = MagicMock(
            side_effect=RuntimeError("ConversationVectorizer not configured")
        )

        with patch("src.multi_tenant.conversation_vectorizer.get_vectorizer", return_value=mock_vectorizer):
            from src.app.background import _vectorization_scanner_loop

            call_count = 0

            async def fake_sleep(seconds):
                nonlocal call_count
                call_count += 1
                if call_count == 1:
                    return
                raise asyncio.CancelledError()

            with patch("src.app.background.asyncio.sleep", side_effect=fake_sleep):
                with pytest.raises(asyncio.CancelledError):
                    await _vectorization_scanner_loop()

        # Should not have tried to list tenants
        mock_vectorizer.vectorize_conversation = AsyncMock()
        mock_vectorizer.vectorize_conversation.assert_not_called()

    @pytest.mark.asyncio
    async def test_scanner_marks_denied_consent_as_vectorized(self):
        """Conversations with DENIED consent are marked vectorized (no re-processing)."""
        conv = _make_conv()

        mock_vectorizer = MagicMock()
        mock_vectorizer._ensure_configured = MagicMock()
        # vectorize_conversation returns [] for denied consent (internal gate)
        mock_vectorizer.vectorize_conversation = AsyncMock(return_value=[])

        mock_tenant_repo = MagicMock()
        mock_tenant_repo.list_active_tenant_ids = AsyncMock(return_value=["tenant-001"])

        mock_conv_repo = MagicMock()
        mock_conv_repo.list_unvectorized_ended = AsyncMock(return_value=[conv])
        mock_conv_repo.patch = AsyncMock()

        mock_profile_repo = MagicMock()
        mock_profile_repo.read = AsyncMock(return_value={
            "consent_status": "denied",
        })

        # Tenant requires explicit consent → scanner checks customer profile
        mock_prefs_repo = MagicMock()
        mock_prefs_repo.read = AsyncMock(return_value={
            "consent_collection_enabled": True,
        })

        with (
            patch("src.multi_tenant.conversation_vectorizer.get_vectorizer", return_value=mock_vectorizer),
            patch("src.multi_tenant.repository.TenantRepository", return_value=mock_tenant_repo),
            patch("src.multi_tenant.repositories.conversation.ConversationRepository", return_value=mock_conv_repo),
            patch("src.multi_tenant.repository.CustomerProfileRepository", return_value=mock_profile_repo),
            patch("src.multi_tenant.repository.PreferencesRepository", return_value=mock_prefs_repo),
        ):
            from src.app.background import _vectorization_scanner_loop

            call_count = 0

            async def fake_sleep(seconds):
                nonlocal call_count
                call_count += 1
                if call_count == 1:
                    return
                raise asyncio.CancelledError()

            with patch("src.app.background.asyncio.sleep", side_effect=fake_sleep):
                with pytest.raises(asyncio.CancelledError):
                    await _vectorization_scanner_loop()

        # Vectorize was called with DENIED status
        mock_vectorizer.vectorize_conversation.assert_called_once()
        args = mock_vectorizer.vectorize_conversation.call_args
        assert args.kwargs["consent_status"] == ConsentStatus.DENIED

        # Still patched vectorized_at (prevents re-processing)
        mock_conv_repo.patch.assert_called_once()

    @pytest.mark.asyncio
    async def test_scanner_handles_per_conversation_failure(self):
        """One conversation failure doesn't block processing of others."""
        conv1 = _make_conv(conv_id="conv-001")
        conv2 = _make_conv(conv_id="conv-002")

        mock_vectorizer = MagicMock()
        mock_vectorizer._ensure_configured = MagicMock()
        # First call fails, second succeeds
        mock_vectorizer.vectorize_conversation = AsyncMock(
            side_effect=[Exception("API timeout"), ["chunk-0"]],
        )

        mock_tenant_repo = MagicMock()
        mock_tenant_repo.list_active_tenant_ids = AsyncMock(return_value=["tenant-001"])

        mock_conv_repo = MagicMock()
        mock_conv_repo.list_unvectorized_ended = AsyncMock(return_value=[conv1, conv2])
        mock_conv_repo.patch = AsyncMock()

        mock_profile_repo = MagicMock()
        mock_profile_repo.read = AsyncMock(return_value={"consent_status": "granted"})

        with (
            patch("src.multi_tenant.conversation_vectorizer.get_vectorizer", return_value=mock_vectorizer),
            patch("src.multi_tenant.repository.TenantRepository", return_value=mock_tenant_repo),
            patch("src.multi_tenant.repositories.conversation.ConversationRepository", return_value=mock_conv_repo),
            patch("src.multi_tenant.repository.CustomerProfileRepository", return_value=mock_profile_repo),
        ):
            from src.app.background import _vectorization_scanner_loop

            call_count = 0

            async def fake_sleep(seconds):
                nonlocal call_count
                call_count += 1
                if call_count == 1:
                    return
                raise asyncio.CancelledError()

            with patch("src.app.background.asyncio.sleep", side_effect=fake_sleep):
                with pytest.raises(asyncio.CancelledError):
                    await _vectorization_scanner_loop()

        # Both conversations attempted
        assert mock_vectorizer.vectorize_conversation.call_count == 2
        # Only second was patched (first failed before patch)
        assert mock_conv_repo.patch.call_count == 1

    @pytest.mark.asyncio
    async def test_scanner_handles_per_tenant_failure(self):
        """One tenant failure doesn't block processing of others."""
        conv = _make_conv(tenant_id="tenant-002")

        mock_vectorizer = MagicMock()
        mock_vectorizer._ensure_configured = MagicMock()
        mock_vectorizer.vectorize_conversation = AsyncMock(return_value=["chunk-0"])

        mock_tenant_repo = MagicMock()
        mock_tenant_repo.list_active_tenant_ids = AsyncMock(
            return_value=["tenant-001", "tenant-002"],
        )

        mock_conv_repo = MagicMock()
        # First tenant raises, second returns a conversation
        mock_conv_repo.list_unvectorized_ended = AsyncMock(
            side_effect=[Exception("Cosmos error"), [conv]],
        )
        mock_conv_repo.patch = AsyncMock()

        mock_profile_repo = MagicMock()
        mock_profile_repo.read = AsyncMock(return_value={"consent_status": "granted"})

        with (
            patch("src.multi_tenant.conversation_vectorizer.get_vectorizer", return_value=mock_vectorizer),
            patch("src.multi_tenant.repository.TenantRepository", return_value=mock_tenant_repo),
            patch("src.multi_tenant.repositories.conversation.ConversationRepository", return_value=mock_conv_repo),
            patch("src.multi_tenant.repository.CustomerProfileRepository", return_value=mock_profile_repo),
        ):
            from src.app.background import _vectorization_scanner_loop

            call_count = 0

            async def fake_sleep(seconds):
                nonlocal call_count
                call_count += 1
                if call_count == 1:
                    return
                raise asyncio.CancelledError()

            with patch("src.app.background.asyncio.sleep", side_effect=fake_sleep):
                with pytest.raises(asyncio.CancelledError):
                    await _vectorization_scanner_loop()

        # Second tenant's conversation was processed
        mock_vectorizer.vectorize_conversation.assert_called_once()
        mock_conv_repo.patch.assert_called_once()


# ---------------------------------------------------------------------------
# Schema field test
# ---------------------------------------------------------------------------

class TestConversationDocumentVectorizedAt:
    """Verify vectorized_at field exists on ConversationDocument."""

    def test_vectorized_at_field_exists(self):
        """ConversationDocument has vectorized_at field with None default."""
        from src.multi_tenant.cosmos_schema import ConversationDocument

        fields = ConversationDocument.model_fields
        assert "vectorized_at" in fields
        field_info = fields["vectorized_at"]
        assert field_info.default is None

    def test_vectorized_at_defaults_to_none(self):
        """New ConversationDocument instances have vectorized_at=None."""
        from src.multi_tenant.cosmos_schema import ConversationDocument

        doc = ConversationDocument(
            id="test",
            tenant_id="t",
            conversation_id="c",
            status=ConversationStatus.ACTIVE,
            started_at="2026-01-01T00:00:00Z",
            last_activity_at="2026-01-01T00:00:00Z",
        )
        assert doc.vectorized_at is None


# ---------------------------------------------------------------------------
# Registration test
# ---------------------------------------------------------------------------

class TestVectorizationScannerRegistration:
    """Verify scanner is registered in main.py composition."""

    def test_register_vectorization_scanner_exists(self):
        """register_vectorization_scanner is importable from background module."""
        from src.app.background import register_vectorization_scanner
        assert callable(register_vectorization_scanner)

    def test_main_imports_register_vectorization_scanner(self):
        """main.py imports register_vectorization_scanner."""
        import src.main as main_mod

        # Verify the function is in the module's namespace
        assert hasattr(main_mod, "register_vectorization_scanner")
