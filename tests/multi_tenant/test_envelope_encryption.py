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

    def test_memory_repo_declares_fields(self):
        from src.multi_tenant.repositories.memory import MemoryVectorRepository
        fields = getattr(MemoryVectorRepository, "_encryption_fields", None)
        assert fields is not None, "MemoryVectorRepository must declare _encryption_fields"


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
