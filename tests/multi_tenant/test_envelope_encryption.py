# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Tests for Pillar 1: Envelope Encryption Service (SPEC-1843).

WI-1624: EnvelopeEncryptionService — encrypt/decrypt with AES-256-GCM
WI-1625: Master KEK provisioning (Terraform, not tested here)
WI-1626: Repository hooks (_pre_write/_post_read)
WI-1627: _encryption_fields declarations
WI-1628: DEK provisioning during tenant creation
WI-1631: Lifecycle wiring
"""
import inspect
import os

import pytest


# ---------------------------------------------------------------------------
# WI-1624: EnvelopeEncryptionService
# ---------------------------------------------------------------------------

class TestEnvelopeEncryptionService:
    """Core encryption service: encrypt/decrypt with AES-256-GCM."""

    def _make_service(self):
        """Create a dev-mode service with in-memory KEK."""
        from src.multi_tenant.envelope_encryption import EnvelopeEncryptionService
        return EnvelopeEncryptionService(dev_mode=True)

    def test_service_instantiates_in_dev_mode(self):
        svc = self._make_service()
        assert svc is not None

    def test_create_tenant_dek(self):
        svc = self._make_service()
        wrapped_dek = svc.create_tenant_dek_sync("t-test-001")
        assert isinstance(wrapped_dek, bytes)
        assert len(wrapped_dek) > 0

    def test_encrypt_decrypt_roundtrip(self):
        svc = self._make_service()
        wrapped_dek = svc.create_tenant_dek_sync("t-test-001")
        plaintext = "Hello, this is sensitive tenant data."
        tenant_id = "t-test-001"
        doc_id = "doc-001"

        ciphertext = svc.encrypt_field(
            wrapped_dek, plaintext, tenant_id=tenant_id, doc_id=doc_id,
        )
        assert ciphertext != plaintext
        assert isinstance(ciphertext, str)  # base64-encoded

        decrypted = svc.decrypt_field(
            wrapped_dek, ciphertext, tenant_id=tenant_id, doc_id=doc_id,
        )
        assert decrypted == plaintext

    def test_different_tenants_produce_different_ciphertexts(self):
        svc = self._make_service()
        dek_a = svc.create_tenant_dek_sync("t-a")
        dek_b = svc.create_tenant_dek_sync("t-b")
        plaintext = "Same data, different tenants"

        ct_a = svc.encrypt_field(dek_a, plaintext, tenant_id="t-a", doc_id="d1")
        ct_b = svc.encrypt_field(dek_b, plaintext, tenant_id="t-b", doc_id="d1")
        assert ct_a != ct_b, "Different DEKs must produce different ciphertexts"

    def test_aad_mismatch_raises(self):
        """Decryption with wrong tenant_id/doc_id (AAD) must fail."""
        svc = self._make_service()
        wrapped_dek = svc.create_tenant_dek_sync("t-test-001")
        plaintext = "Sensitive data"

        ciphertext = svc.encrypt_field(
            wrapped_dek, plaintext, tenant_id="t-test-001", doc_id="doc-001",
        )
        # Try decrypting with wrong tenant_id
        with pytest.raises(Exception):
            svc.decrypt_field(
                wrapped_dek, ciphertext, tenant_id="t-WRONG", doc_id="doc-001",
            )

    def test_encrypt_none_returns_none(self):
        svc = self._make_service()
        wrapped_dek = svc.create_tenant_dek_sync("t-test-001")
        result = svc.encrypt_field(wrapped_dek, None, tenant_id="t-001", doc_id="d1")
        assert result is None

    def test_decrypt_none_returns_none(self):
        svc = self._make_service()
        wrapped_dek = svc.create_tenant_dek_sync("t-test-001")
        result = svc.decrypt_field(wrapped_dek, None, tenant_id="t-001", doc_id="d1")
        assert result is None

    def test_encrypt_empty_string(self):
        svc = self._make_service()
        wrapped_dek = svc.create_tenant_dek_sync("t-test-001")
        ct = svc.encrypt_field(wrapped_dek, "", tenant_id="t-001", doc_id="d1")
        pt = svc.decrypt_field(wrapped_dek, ct, tenant_id="t-001", doc_id="d1")
        assert pt == ""


# ---------------------------------------------------------------------------
# WI-1626: Repository hooks
# ---------------------------------------------------------------------------

class TestRepositoryEncryptionHooks:
    """TenantScopedRepository must have _pre_write/_post_read hooks."""

    def test_base_repo_has_pre_write_hook(self):
        from src.multi_tenant.repositories.base import TenantScopedRepository
        assert hasattr(TenantScopedRepository, '_pre_write'), \
            "TenantScopedRepository must have _pre_write method"

    def test_base_repo_has_post_read_hook(self):
        from src.multi_tenant.repositories.base import TenantScopedRepository
        assert hasattr(TenantScopedRepository, '_post_read'), \
            "TenantScopedRepository must have _post_read method"

    def test_base_repo_has_encryption_fields_attribute(self):
        from src.multi_tenant.repositories.base import TenantScopedRepository
        assert hasattr(TenantScopedRepository, '_encryption_fields'), \
            "TenantScopedRepository must have _encryption_fields class attribute"


# ---------------------------------------------------------------------------
# WI-1627: Encryption field declarations
# ---------------------------------------------------------------------------

class TestEncryptionFieldDeclarations:
    """Repository subclasses must declare _encryption_fields."""

    def test_conversation_repo_declares_fields(self):
        from src.multi_tenant.repositories.conversation import ConversationRepository
        fields = getattr(ConversationRepository, "_encryption_fields", None)
        assert fields is not None, "ConversationRepository must declare _encryption_fields"
        assert "messages" in fields

    def test_knowledge_repo_declares_fields(self):
        from src.multi_tenant.repositories.knowledge import KnowledgeBaseRepository
        fields = getattr(KnowledgeBaseRepository, "_encryption_fields", None)
        assert fields is not None, "KnowledgeBaseRepository must declare _encryption_fields"
        assert "content" in fields

    def test_customer_repo_declares_fields(self):
        from src.multi_tenant.repositories.customer import CustomerProfileRepository
        fields = getattr(CustomerProfileRepository, "_encryption_fields", None)
        assert fields is not None, "CustomerProfileRepository must declare _encryption_fields"
        assert "email" in fields

    def test_memory_repo_declares_chunk_text(self):
        from src.multi_tenant.repositories.memory import MemoryVectorRepository
        fields = getattr(MemoryVectorRepository, "_encryption_fields", None)
        assert fields is not None, "MemoryVectorRepository must declare _encryption_fields"
        assert "chunk_text" in fields, "MemoryVectorRepository must encrypt chunk_text (the actual stored field)"

    def test_tenant_repo_declares_fields(self):
        from src.multi_tenant.repositories.tenant import TenantRepository
        fields = getattr(TenantRepository, "_encryption_fields", None)
        assert fields is not None, "TenantRepository must declare _encryption_fields"
        assert "customer_email" in fields

    def test_team_repo_declares_fields(self):
        from src.multi_tenant.repositories.team import TeamMemberRepository
        fields = getattr(TeamMemberRepository, "_encryption_fields", None)
        assert fields is not None, "TeamMemberRepository must declare _encryption_fields"
        assert "email" in fields

    def test_preferences_repo_declares_fields(self):
        from src.multi_tenant.repositories.preferences import PreferencesRepository
        fields = getattr(PreferencesRepository, "_encryption_fields", None)
        assert fields is not None, "PreferencesRepository must declare _encryption_fields"
        assert "custom_instructions" in fields


# ---------------------------------------------------------------------------
# WI-1631: Lifecycle wiring
# ---------------------------------------------------------------------------

class TestLifecycleWiring:
    """Encryption service must be wired in lifecycle.py."""

    def test_lifecycle_references_encryption_service(self):
        from src.app import lifecycle
        source = inspect.getsource(lifecycle)
        assert "envelope_encryption" in source.lower() or "EnvelopeEncryptionService" in source, \
            "lifecycle.py must reference envelope encryption service"


# ---------------------------------------------------------------------------
# Roundtrip tests: _pre_write/_post_read with actual field types
# ---------------------------------------------------------------------------

class TestPreWritePostReadRoundtrip:
    """Prove that _pre_write encrypts and _post_read decrypts for all field types."""

    def _setup(self):
        """Set up dev-mode encryption service and return it."""
        from src.multi_tenant.envelope_encryption import (
            EnvelopeEncryptionService,
            set_envelope_encryption_service,
        )
        svc = EnvelopeEncryptionService(dev_mode=True)
        set_envelope_encryption_service(svc)
        wrapped_dek = svc.create_tenant_dek_sync("t-roundtrip")
        return svc, wrapped_dek

    @pytest.mark.asyncio
    async def test_string_field_roundtrip(self):
        """String fields encrypt to base64 and decrypt back to original."""
        self._setup()
        from src.multi_tenant.repositories.base import TenantScopedRepository, _dek_cache, _DekCacheEntry
        from src.multi_tenant.envelope_encryption import get_envelope_encryption_service

        svc = get_envelope_encryption_service()
        wrapped_dek = svc.create_tenant_dek_sync("t-roundtrip")

        # Pre-populate DEK cache (normally done by _get_tenant_dek)
        import time
        _dek_cache["t-roundtrip"] = _DekCacheEntry(
            raw_dek=svc._unwrap_key(wrapped_dek, "t-roundtrip"),
            wrapped_dek=wrapped_dek,
        )

        class TestRepo(TenantScopedRepository):
            _encryption_fields = frozenset({"secret_field"})
            def __init__(self):
                pass  # Skip Cosmos init

        repo = TestRepo()
        doc = {"id": "doc-1", "tenant_id": "t-roundtrip", "secret_field": "hello world"}

        encrypted = await repo._pre_write(dict(doc), "t-roundtrip")
        assert encrypted["secret_field"] != "hello world", "Field should be encrypted"
        assert isinstance(encrypted["secret_field"], str), "Encrypted value should be base64 string"

        decrypted = await repo._post_read(encrypted, "t-roundtrip")
        assert decrypted["secret_field"] == "hello world", "Should decrypt back to original"

    @pytest.mark.asyncio
    async def test_list_field_roundtrip(self):
        """List fields (like messages) serialize to json:, encrypt, and roundtrip."""
        self._setup()
        from src.multi_tenant.repositories.base import TenantScopedRepository, _dek_cache, _DekCacheEntry
        from src.multi_tenant.envelope_encryption import get_envelope_encryption_service

        svc = get_envelope_encryption_service()
        wrapped_dek = svc.create_tenant_dek_sync("t-roundtrip-list")
        import time
        _dek_cache["t-roundtrip-list"] = _DekCacheEntry(
            raw_dek=svc._unwrap_key(wrapped_dek, "t-roundtrip-list"),
            wrapped_dek=wrapped_dek,
        )

        class TestRepo(TenantScopedRepository):
            _encryption_fields = frozenset({"messages"})
            def __init__(self):
                pass

        repo = TestRepo()
        messages = [
            {"role": "user", "content": "What is your return policy?"},
            {"role": "assistant", "content": "We offer 30-day returns."},
        ]
        doc = {"id": "conv-1", "tenant_id": "t-roundtrip-list", "messages": messages}

        encrypted = await repo._pre_write(dict(doc), "t-roundtrip-list")
        # After encryption, messages should be a base64 string (not a list)
        assert isinstance(encrypted["messages"], str), "Encrypted messages should be a string"
        assert encrypted["messages"] != str(messages), "Should not be plaintext"

        decrypted = await repo._post_read(encrypted, "t-roundtrip-list")
        # After decryption, messages should be a list again
        assert isinstance(decrypted["messages"], list), "Decrypted messages should be a list"
        assert len(decrypted["messages"]) == 2
        assert decrypted["messages"][0]["content"] == "What is your return policy?"
        assert decrypted["messages"][1]["content"] == "We offer 30-day returns."

    @pytest.mark.asyncio
    async def test_dict_field_roundtrip(self):
        """Dict fields serialize to json:, encrypt, and roundtrip."""
        self._setup()
        from src.multi_tenant.repositories.base import TenantScopedRepository, _dek_cache, _DekCacheEntry
        from src.multi_tenant.envelope_encryption import get_envelope_encryption_service

        svc = get_envelope_encryption_service()
        wrapped_dek = svc.create_tenant_dek_sync("t-roundtrip-dict")
        import time
        _dek_cache["t-roundtrip-dict"] = _DekCacheEntry(
            raw_dek=svc._unwrap_key(wrapped_dek, "t-roundtrip-dict"),
            wrapped_dek=wrapped_dek,
        )

        class TestRepo(TenantScopedRepository):
            _encryption_fields = frozenset({"preferences"})
            def __init__(self):
                pass

        repo = TestRepo()
        prefs = {"theme": "dark", "notifications": True, "webhook_url": "https://example.com/hook"}
        doc = {"id": "cust-1", "tenant_id": "t-roundtrip-dict", "preferences": prefs}

        encrypted = await repo._pre_write(dict(doc), "t-roundtrip-dict")
        assert isinstance(encrypted["preferences"], str), "Encrypted dict should be a string"

        decrypted = await repo._post_read(encrypted, "t-roundtrip-dict")
        assert isinstance(decrypted["preferences"], dict), "Decrypted should be a dict"
        assert decrypted["preferences"]["theme"] == "dark"
        assert decrypted["preferences"]["webhook_url"] == "https://example.com/hook"

    @pytest.mark.asyncio
    async def test_plaintext_passthrough(self):
        """Pre-migration plaintext data passes through _post_read unchanged."""
        self._setup()
        from src.multi_tenant.repositories.base import TenantScopedRepository, _dek_cache, _DekCacheEntry
        from src.multi_tenant.envelope_encryption import get_envelope_encryption_service

        svc = get_envelope_encryption_service()
        wrapped_dek = svc.create_tenant_dek_sync("t-passthrough")
        _dek_cache["t-passthrough"] = _DekCacheEntry(
            raw_dek=svc._unwrap_key(wrapped_dek, "t-passthrough"),
            wrapped_dek=wrapped_dek,
        )

        class TestRepo(TenantScopedRepository):
            _encryption_fields = frozenset({"messages", "name"})
            def __init__(self):
                pass

        repo = TestRepo()
        # Simulate pre-migration document with plaintext list and string
        doc = {
            "id": "doc-old", "tenant_id": "t-passthrough",
            "messages": [{"role": "user", "content": "hi"}],
            "name": "short",
        }

        # _post_read should NOT crash on plaintext data
        result = await repo._post_read(dict(doc), "t-passthrough")
        assert result["messages"] == [{"role": "user", "content": "hi"}], "Lists pass through"
        assert result["name"] == "short", "Short strings pass through"
