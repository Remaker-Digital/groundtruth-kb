"""Tests for SPEC-1843 encrypted field patch guard.

Verifies that TenantScopedRepository.patch() rejects operations on
encrypted fields, forcing callers to use read-modify-write helpers.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import pytest
from unittest.mock import AsyncMock, patch

from src.multi_tenant.repositories.base import (
    EncryptedFieldPatchError,
    TenantScopedRepository,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

class _EncryptedRepo(TenantScopedRepository):
    """Test repo with encryption fields declared."""

    _encryption_fields = frozenset({"messages", "customer_intent", "secret_field"})

    def __init__(self) -> None:
        super().__init__("test_collection")


class _PlainRepo(TenantScopedRepository):
    """Test repo with NO encryption fields."""

    def __init__(self) -> None:
        super().__init__("plain_collection")


@pytest.fixture
def encrypted_repo():
    repo = _EncryptedRepo()
    return repo


@pytest.fixture
def plain_repo():
    return _PlainRepo()


# ---------------------------------------------------------------------------
# Guard: blocks encrypted field patches
# ---------------------------------------------------------------------------

class TestPatchGuardBlocks:
    """Verify that patch() raises EncryptedFieldPatchError for encrypted fields."""

    @pytest.mark.asyncio
    async def test_blocks_set_on_encrypted_field(self, encrypted_repo):
        with pytest.raises(EncryptedFieldPatchError) as exc_info:
            await encrypted_repo.patch(
                "tenant-1", "doc-1",
                [{"op": "set", "path": "/messages", "value": []}],
            )
        assert exc_info.value.field == "messages"
        assert exc_info.value.operation == "set"
        assert "test_collection" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_blocks_add_append_to_encrypted_array(self, encrypted_repo):
        """The /messages/- append pattern must be blocked."""
        with pytest.raises(EncryptedFieldPatchError) as exc_info:
            await encrypted_repo.patch(
                "tenant-1", "doc-1",
                [{"op": "add", "path": "/messages/-", "value": {"role": "ai"}}],
            )
        assert exc_info.value.field == "messages"
        assert exc_info.value.operation == "add"

    @pytest.mark.asyncio
    async def test_blocks_nested_path_into_encrypted_field(self, encrypted_repo):
        """Patching /messages/3/metadata must also be blocked."""
        with pytest.raises(EncryptedFieldPatchError):
            await encrypted_repo.patch(
                "tenant-1", "doc-1",
                [{"op": "set", "path": "/messages/3/metadata", "value": {}}],
            )

    @pytest.mark.asyncio
    async def test_blocks_replace_on_encrypted_field(self, encrypted_repo):
        with pytest.raises(EncryptedFieldPatchError):
            await encrypted_repo.patch(
                "tenant-1", "doc-1",
                [{"op": "replace", "path": "/customer_intent", "value": "new"}],
            )

    @pytest.mark.asyncio
    async def test_blocks_remove_on_encrypted_field(self, encrypted_repo):
        with pytest.raises(EncryptedFieldPatchError):
            await encrypted_repo.patch(
                "tenant-1", "doc-1",
                [{"op": "remove", "path": "/secret_field"}],
            )

    @pytest.mark.asyncio
    async def test_blocks_mixed_ops_if_any_encrypted(self, encrypted_repo):
        """If one op in the list targets an encrypted field, reject all."""
        with pytest.raises(EncryptedFieldPatchError):
            await encrypted_repo.patch(
                "tenant-1", "doc-1",
                [
                    {"op": "set", "path": "/status", "value": "active"},
                    {"op": "add", "path": "/messages/-", "value": {"role": "ai"}},
                ],
            )

    @pytest.mark.asyncio
    async def test_all_encryption_fields_blocked(self, encrypted_repo):
        """Every declared encrypted field must be blocked."""
        for field in encrypted_repo._encryption_fields:
            with pytest.raises(EncryptedFieldPatchError) as exc_info:
                await encrypted_repo.patch(
                    "tenant-1", "doc-1",
                    [{"op": "set", "path": f"/{field}", "value": "x"}],
                )
            assert exc_info.value.field == field


# ---------------------------------------------------------------------------
# Guard: allows non-encrypted field patches
# ---------------------------------------------------------------------------

class TestPatchGuardAllows:
    """Verify that patch() allows operations on non-encrypted fields."""

    @pytest.mark.asyncio
    async def test_allows_non_encrypted_field(self, encrypted_repo):
        """Non-encrypted fields should pass through to Cosmos."""
        mock_container = AsyncMock()
        mock_container.patch_item = AsyncMock(return_value={"id": "doc-1"})
        with patch.object(type(encrypted_repo), '_container', new_callable=lambda: property(lambda self: mock_container)):
            result = await encrypted_repo.patch(
                "tenant-1", "doc-1",
                [{"op": "set", "path": "/status", "value": "active"}],
            )
        assert result == {"id": "doc-1"}
        mock_container.patch_item.assert_called_once()

    @pytest.mark.asyncio
    async def test_allows_metadata_fields(self, encrypted_repo):
        """Timestamp, count, and status fields are safe to patch."""
        mock_container = AsyncMock()
        mock_container.patch_item = AsyncMock(return_value={"id": "doc-1"})
        with patch.object(type(encrypted_repo), '_container', new_callable=lambda: property(lambda self: mock_container)):
            await encrypted_repo.patch(
                "tenant-1", "doc-1",
                [
                    {"op": "set", "path": "/last_activity_at", "value": "2026-01-01"},
                    {"op": "incr", "path": "/message_count", "value": 1},
                    {"op": "set", "path": "/status", "value": "ended"},
                ],
            )
        mock_container.patch_item.assert_called_once()

    @pytest.mark.asyncio
    async def test_plain_repo_no_guard(self, plain_repo):
        """Repos without encryption fields should never trigger the guard."""
        mock_container = AsyncMock()
        mock_container.patch_item = AsyncMock(return_value={"id": "doc-1"})
        with patch.object(type(plain_repo), '_container', new_callable=lambda: property(lambda self: mock_container)):
            await plain_repo.patch(
                "tenant-1", "doc-1",
                [{"op": "set", "path": "/anything", "value": "ok"}],
            )
        mock_container.patch_item.assert_called_once()


# ---------------------------------------------------------------------------
# Guard: edge cases
# ---------------------------------------------------------------------------

class TestPatchGuardEdgeCases:

    @pytest.mark.asyncio
    async def test_empty_path_no_crash(self, encrypted_repo):
        """Empty path should not match any encryption field."""
        mock_container = AsyncMock()
        mock_container.patch_item = AsyncMock(return_value={"id": "doc-1"})
        with patch.object(type(encrypted_repo), '_container', new_callable=lambda: property(lambda self: mock_container)):
            await encrypted_repo.patch(
                "tenant-1", "doc-1",
                [{"op": "set", "path": "", "value": "x"}],
            )

    @pytest.mark.asyncio
    async def test_empty_operations_list(self, encrypted_repo):
        """Empty ops list should pass through."""
        mock_container = AsyncMock()
        mock_container.patch_item = AsyncMock(return_value={"id": "doc-1"})
        with patch.object(type(encrypted_repo), '_container', new_callable=lambda: property(lambda self: mock_container)):
            await encrypted_repo.patch("tenant-1", "doc-1", [])

    @pytest.mark.asyncio
    async def test_exception_includes_collection_name(self, encrypted_repo):
        with pytest.raises(EncryptedFieldPatchError) as exc_info:
            await encrypted_repo.patch(
                "tenant-1", "doc-1",
                [{"op": "set", "path": "/messages", "value": []}],
            )
        assert "test_collection" in str(exc_info.value)
        assert "read-modify-write" in str(exc_info.value)


# ---------------------------------------------------------------------------
# Real repository encryption field declarations
# ---------------------------------------------------------------------------

class TestRealRepositoryGuards:
    """Verify that actual production repositories block their encrypted fields."""

    @pytest.mark.asyncio
    async def test_conversation_repo_blocks_messages(self):
        from src.multi_tenant.repositories.conversation import ConversationRepository
        repo = ConversationRepository()
        with pytest.raises(EncryptedFieldPatchError):
            await repo.patch("t1", "d1", [{"op": "add", "path": "/messages/-", "value": {}}])

    @pytest.mark.asyncio
    async def test_tenant_repo_blocks_customer_email(self):
        from src.multi_tenant.repositories.tenant import TenantRepository
        repo = TenantRepository()
        with pytest.raises(EncryptedFieldPatchError):
            await repo.patch("t1", "d1", [{"op": "set", "path": "/customer_email", "value": "x"}])

    @pytest.mark.asyncio
    async def test_team_repo_blocks_display_name(self):
        from src.multi_tenant.repositories.team import TeamMemberRepository
        repo = TeamMemberRepository()
        with pytest.raises(EncryptedFieldPatchError):
            await repo.patch("t1", "d1", [{"op": "set", "path": "/display_name", "value": "x"}])

    @pytest.mark.asyncio
    async def test_customer_repo_blocks_email(self):
        from src.multi_tenant.repositories.customer import CustomerProfileRepository
        repo = CustomerProfileRepository()
        with pytest.raises(EncryptedFieldPatchError):
            await repo.patch("t1", "d1", [{"op": "set", "path": "/email", "value": "x"}])

    @pytest.mark.asyncio
    async def test_knowledge_repo_blocks_content(self):
        from src.multi_tenant.repositories.knowledge import KnowledgeBaseRepository
        repo = KnowledgeBaseRepository()
        with pytest.raises(EncryptedFieldPatchError):
            await repo.patch("t1", "d1", [{"op": "set", "path": "/content", "value": "x"}])

    @pytest.mark.asyncio
    async def test_preferences_repo_blocks_custom_instructions(self):
        from src.multi_tenant.repositories.preferences import PreferencesRepository
        repo = PreferencesRepository()
        with pytest.raises(EncryptedFieldPatchError):
            await repo.patch("t1", "d1", [{"op": "set", "path": "/custom_instructions", "value": "x"}])

    @pytest.mark.asyncio
    async def test_memory_repo_blocks_chunk_text(self):
        from src.multi_tenant.repositories.memory import MemoryVectorRepository
        repo = MemoryVectorRepository()
        with pytest.raises(EncryptedFieldPatchError):
            await repo.patch("t1", "d1", [{"op": "set", "path": "/chunk_text", "value": "x"}])
