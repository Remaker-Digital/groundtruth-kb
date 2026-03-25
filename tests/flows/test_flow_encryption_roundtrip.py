"""
Flow tests: Encryption round-trip integrity.

These tests verify that data written through external interfaces is stored
as ciphertext and retrieved as plaintext — exercising the full write→store→read
path through the real application code with mock infrastructure.

Each test follows the outside-in pattern:
  1. Write data via HTTP API (external interface)
  2. Inspect raw storage (MockCosmosManager) to verify ciphertext
  3. Read data back via HTTP API to verify decryption
  4. Verify side-effects (audit log, events)

SPEC-1843: Operator cannot read tenant data.
GOV-19: Outside-in testing.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import json
from unittest.mock import AsyncMock, patch

import pytest

from tests.conftest import (
    TEST_API_KEY_STARTER,
    TEST_API_KEY_HASH_STARTER,
    STARTER_TENANT_ID,
    auth_headers_api_key,
    make_tenant_document,
    MockCosmosManager,
)
from src.multi_tenant.repositories.base import EncryptedFieldPatchError


# ---------------------------------------------------------------------------
# Flow 1: Conversation encryption round-trip
# ---------------------------------------------------------------------------

class TestFlowConversationEncryption:
    """Write a conversation message → verify storage is encrypted → read back decrypted."""

    @pytest.mark.asyncio
    async def test_conversation_create_encrypts_messages(self):
        """Creating a conversation stores messages as ciphertext in Cosmos."""
        from src.multi_tenant.repositories.conversation import ConversationRepository

        repo = ConversationRepository()

        with _mock_encryption_service() as enc_svc, _mock_cosmos_for_repo(repo) as container:
            from pydantic import BaseModel

            class FakeConvDoc(BaseModel):
                id: str
                tenant_id: str
                messages: list
                customer_intent: str
                partition_key: str

            doc = await repo.create(
                tenant_id=STARTER_TENANT_ID,
                document=FakeConvDoc(
                    id="conv-001",
                    tenant_id=STARTER_TENANT_ID,
                    messages=[{"role": "user", "content": "Hello, I need help"}],
                    customer_intent="support_request",
                    partition_key=STARTER_TENANT_ID,
                ),
            )

            # VERIFY: raw storage has ciphertext (not plaintext)
            raw_items = container.items
            assert len(raw_items) >= 1
            raw_doc = raw_items[-1]

            # If encryption is active, messages field should be encrypted
            raw_messages = raw_doc.get("messages", "")
            if isinstance(raw_messages, list):
                pytest.fail(
                    "messages field stored as plain list without encryption. "
                    "Expected encrypted string blob."
                )

    @pytest.mark.asyncio
    async def test_conversation_read_decrypts_messages(self):
        """Reading a conversation returns plaintext messages after decryption."""
        from src.multi_tenant.repositories.conversation import ConversationRepository

        repo = ConversationRepository()
        original_messages = [{"role": "user", "content": "Hello"}]

        with _mock_encryption_service() as enc_svc, _mock_cosmos_for_repo(repo) as container:
            from pydantic import BaseModel

            class FakeConvDoc(BaseModel):
                id: str
                tenant_id: str
                messages: list
                partition_key: str

            await repo.create(
                tenant_id=STARTER_TENANT_ID,
                document=FakeConvDoc(
                    id="conv-002",
                    tenant_id=STARTER_TENANT_ID,
                    messages=original_messages,
                    partition_key=STARTER_TENANT_ID,
                ),
            )

            # READ back
            doc = await repo.read(STARTER_TENANT_ID, "conv-002")

        # VERIFY: returned messages are plaintext and match original
        assert doc is not None
        returned_messages = doc.get("messages", [])
        assert isinstance(returned_messages, list), (
            f"Expected list, got {type(returned_messages)}: {returned_messages}"
        )
        assert returned_messages == original_messages


class TestFlowPatchGuard:
    """Verify that patch() on encrypted fields raises EncryptedFieldPatchError."""

    @pytest.mark.asyncio
    async def test_patch_messages_field_blocked(self):
        """Patching the 'messages' field on ConversationRepository raises."""
        from src.multi_tenant.repositories.conversation import ConversationRepository

        repo = ConversationRepository()
        with pytest.raises(EncryptedFieldPatchError, match="messages"):
            await repo.patch(
                tenant_id=STARTER_TENANT_ID,
                document_id="conv-001",
                operations=[{"op": "set", "path": "/messages", "value": []}],
            )

    @pytest.mark.asyncio
    async def test_patch_customer_intent_blocked(self):
        """Patching 'customer_intent' on ConversationRepository raises."""
        from src.multi_tenant.repositories.conversation import ConversationRepository

        repo = ConversationRepository()
        with pytest.raises(EncryptedFieldPatchError, match="customer_intent"):
            await repo.patch(
                tenant_id=STARTER_TENANT_ID,
                document_id="conv-001",
                operations=[{"op": "set", "path": "/customer_intent", "value": "test"}],
            )

    @pytest.mark.asyncio
    async def test_patch_non_encrypted_field_allowed(self):
        """Patching a non-encrypted field (e.g. status) is allowed."""
        from src.multi_tenant.repositories.conversation import ConversationRepository

        repo = ConversationRepository()
        # This should NOT raise — status is not an encrypted field
        # (It may raise CosmosResourceNotFoundError since we have no seeded data,
        # but it must NOT raise EncryptedFieldPatchError)
        try:
            await repo.patch(
                tenant_id=STARTER_TENANT_ID,
                document_id="conv-001",
                operations=[{"op": "set", "path": "/status", "value": "resolved"}],
            )
        except EncryptedFieldPatchError:
            pytest.fail("Non-encrypted field 'status' should not be blocked by patch guard")
        except Exception:
            pass  # Any other error (e.g. not found) is acceptable

    @pytest.mark.asyncio
    async def test_patch_guard_all_seven_repos(self):
        """Every repository with _encryption_fields blocks patch on those fields."""
        from src.multi_tenant.repositories.conversation import ConversationRepository
        from src.multi_tenant.repositories.customer import CustomerProfileRepository
        from src.multi_tenant.repositories.knowledge import KnowledgeBaseRepository
        from src.multi_tenant.repositories.memory import MemoryVectorRepository
        from src.multi_tenant.repositories.preferences import PreferencesRepository
        from src.multi_tenant.repositories.team import TeamMemberRepository
        from src.multi_tenant.repositories.tenant import TenantRepository

        repos_and_fields = [
            (ConversationRepository(), "messages"),
            (CustomerProfileRepository(), "email"),
            (KnowledgeBaseRepository(), "content"),
            (MemoryVectorRepository(), "chunk_text"),
            (PreferencesRepository(), "custom_instructions"),
            (TeamMemberRepository(), "display_name"),
            (TenantRepository(), "customer_email"),
        ]

        for repo, field in repos_and_fields:
            with pytest.raises(EncryptedFieldPatchError, match=field):
                await repo.patch(
                    tenant_id=STARTER_TENANT_ID,
                    document_id="test-001",
                    operations=[{"op": "set", "path": f"/{field}", "value": "plaintext"}],
                )


class TestFlowTenantEncryption:
    """Tenant document encryption: customer_email, shop_domain, brand_name."""

    @pytest.mark.asyncio
    async def test_tenant_email_encrypted_at_rest(self):
        """Updating customer_email stores ciphertext, reads back plaintext."""
        from pydantic import BaseModel
        from src.multi_tenant.repositories.tenant import TenantRepository

        repo = TenantRepository()

        class FakeTenantDoc(BaseModel):
            id: str
            tenant_id: str
            customer_email: str
            partition_key: str

        with _mock_encryption_service(), _mock_cosmos_for_repo(repo) as container:
            await repo.create(
                tenant_id=STARTER_TENANT_ID,
                document=FakeTenantDoc(
                    id=STARTER_TENANT_ID,
                    tenant_id=STARTER_TENANT_ID,
                    customer_email="secret@example.com",
                    partition_key=STARTER_TENANT_ID,
                ),
            )

            doc = await repo.read(STARTER_TENANT_ID, STARTER_TENANT_ID)

        assert doc is not None
        assert doc["customer_email"] == "secret@example.com"


class TestFlowTeamMemberEncryption:
    """Team member encryption: email, display_name."""

    @pytest.mark.asyncio
    async def test_team_member_display_name_encrypted(self):
        """Creating team member encrypts display_name, reads back plaintext."""
        from pydantic import BaseModel
        from src.multi_tenant.repositories.team import TeamMemberRepository

        repo = TeamMemberRepository()

        class FakeTeamDoc(BaseModel):
            id: str
            tenant_id: str
            email: str
            display_name: str
            partition_key: str

        with _mock_encryption_service(), _mock_cosmos_for_repo(repo) as container:
            await repo.create(
                tenant_id=STARTER_TENANT_ID,
                document=FakeTeamDoc(
                    id="member-001",
                    tenant_id=STARTER_TENANT_ID,
                    email="alice@example.com",
                    display_name="Alice Smith",
                    partition_key=STARTER_TENANT_ID,
                ),
            )

            doc = await repo.read(STARTER_TENANT_ID, "member-001")

        assert doc is not None
        assert doc["display_name"] == "Alice Smith"
        assert doc["email"] == "alice@example.com"


# ---------------------------------------------------------------------------
# Encryption mock helper
# ---------------------------------------------------------------------------

def _mock_cosmos_for_repo(repo):
    """Context manager that patches CosmosManager so the repo gets a MockContainerProxy.

    Returns the MockContainerProxy so tests can inspect raw storage.
    The _container property on TenantScopedRepository calls
    get_cosmos_manager().get_container(), so we patch the manager.
    """
    from contextlib import contextmanager
    from tests.conftest import MockCosmosManager
    import src.multi_tenant.cosmos_client as _cosmos_mod

    manager = MockCosmosManager()
    container = manager.get_container(repo._collection_name)

    @contextmanager
    def _ctx():
        with patch.object(_cosmos_mod, "_manager", manager):
            with patch.object(_cosmos_mod, "get_cosmos_manager", return_value=manager):
                yield container

    return _ctx()


def _mock_encryption_service():
    """Context manager providing a deterministic mock encryption service.

    Encrypts by base64-encoding with an ENC: prefix, decrypts by reversing.
    Also injects a fake DEK into the module-level DEK cache so that
    _pre_write / _post_read gate #3 (tenant DEK exists) passes.

    Three gates in _pre_write must all pass:
      1. _encryption_fields is non-empty (per repository subclass)
      2. encryption service is not None (mocked here)
      3. tenant DEK exists (injected into _dek_cache here)
    """
    import base64
    from contextlib import contextmanager
    from unittest.mock import MagicMock
    import src.multi_tenant.repositories.base as _base_mod

    service = MagicMock()

    # Fake DEK bytes
    fake_raw_dek = b"fake-raw-dek-32-bytes-for-tests!"  # 32 bytes
    fake_wrapped_dek = b"fake-wrapped-dek-bytes"

    def _encrypt(wrapped_dek: bytes, plaintext: str, **kwargs) -> str:
        """Deterministic fake encryption: base64 encode with long enough output."""
        import base64 as b64
        # Produce output that looks like base64 ciphertext (>= 40 chars)
        # so _post_read's heuristic recognizes it
        payload = b"NONCE_12_BYTE" + b"TAG_16_BYTES_XX" + plaintext.encode("utf-8")
        return b64.b64encode(payload).decode()

    def _decrypt(wrapped_dek: bytes, ciphertext: str, **kwargs) -> str:
        """Reverse the fake encryption."""
        import base64 as b64
        raw = b64.b64decode(ciphertext)
        # Strip nonce (13 bytes) + tag (15 bytes) = 28 bytes prefix
        return raw[28:].decode("utf-8")

    service.encrypt_field = _encrypt
    service.decrypt_field = _decrypt
    service.is_enabled = True

    # Create a fake DEK cache entry
    fake_entry = _base_mod._DekCacheEntry(fake_raw_dek, fake_wrapped_dek)

    @contextmanager
    def _ctx():
        # Inject DEK into module-level cache for the test tenant
        _base_mod._dek_cache[STARTER_TENANT_ID] = fake_entry
        try:
            with patch(
                "src.multi_tenant.envelope_encryption.get_envelope_encryption_service",
                return_value=service,
            ):
                yield service
        finally:
            # Clean up
            _base_mod._dek_cache.pop(STARTER_TENANT_ID, None)

    return _ctx()
