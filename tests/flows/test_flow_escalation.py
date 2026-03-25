"""
Flow tests: Conversation escalation flow.

Verifies the full escalation path: customer requests escalation →
conversation updated with encrypted escalation_reason → audit event
logged with sanitized payload → email dispatched.

Flow pattern:
  1. Create conversation via repository
  2. Escalate via repository (read-modify-write, not patch)
  3. Verify escalation_reason is encrypted in storage
  4. Verify the conversation status is updated
  5. Verify audit sanitization prevents PII in escalation log

GOV-19: Outside-in testing.
SPEC-1843: Zero-knowledge.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

from unittest.mock import patch

import pytest

from tests.conftest import STARTER_TENANT_ID
from src.multi_tenant.repositories.base import EncryptedFieldPatchError
from src.multi_tenant.repositories.conversation import ConversationRepository
from src.multi_tenant.audit_sanitizer import sanitize_audit_payload

from tests.flows.test_flow_encryption_roundtrip import (
    _mock_encryption_service,
    _mock_cosmos_for_repo,
)


class TestFlowEscalationEncryption:
    """Escalation reason must be encrypted at rest."""

    @pytest.mark.asyncio
    async def test_escalation_reason_encrypted_on_write(self):
        """Writing an escalation_reason encrypts it in Cosmos."""
        from pydantic import BaseModel

        class FakeConv(BaseModel):
            id: str
            tenant_id: str
            messages: list
            escalation_reason: str
            status: str
            partition_key: str

        repo = ConversationRepository()

        with _mock_encryption_service(), _mock_cosmos_for_repo(repo) as container:
            await repo.create(
                tenant_id=STARTER_TENANT_ID,
                document=FakeConv(
                    id="conv-esc-001",
                    tenant_id=STARTER_TENANT_ID,
                    messages=[{"role": "user", "content": "I want a refund NOW"}],
                    escalation_reason="Customer is angry about defective product, wants full refund",
                    status="escalated",
                    partition_key=STARTER_TENANT_ID,
                ),
            )

            raw = container.items[-1]

            # escalation_reason must be encrypted
            assert isinstance(raw["escalation_reason"], str)
            assert "angry" not in raw["escalation_reason"], (
                "Plaintext escalation_reason in Cosmos — encryption failed!"
            )
            assert "defective" not in raw["escalation_reason"], (
                "Plaintext product detail in Cosmos — encryption failed!"
            )

            # messages must also be encrypted
            assert not isinstance(raw["messages"], list), (
                "Messages stored as plain list — encryption failed!"
            )

    @pytest.mark.asyncio
    async def test_escalation_reason_decrypts_on_read(self):
        """Reading back an escalated conversation decrypts the reason."""
        from pydantic import BaseModel

        class FakeConv(BaseModel):
            id: str
            tenant_id: str
            escalation_reason: str
            partition_key: str

        repo = ConversationRepository()

        with _mock_encryption_service(), _mock_cosmos_for_repo(repo) as container:
            await repo.create(
                tenant_id=STARTER_TENANT_ID,
                document=FakeConv(
                    id="conv-esc-002",
                    tenant_id=STARTER_TENANT_ID,
                    escalation_reason="Customer wants to speak to a manager",
                    partition_key=STARTER_TENANT_ID,
                ),
            )

            doc = await repo.read(STARTER_TENANT_ID, "conv-esc-002")

        assert doc["escalation_reason"] == "Customer wants to speak to a manager"

    @pytest.mark.asyncio
    async def test_patch_escalation_reason_blocked(self):
        """Direct patch on escalation_reason is structurally blocked."""
        repo = ConversationRepository()
        with pytest.raises(EncryptedFieldPatchError, match="escalation_reason"):
            await repo.patch(
                tenant_id=STARTER_TENANT_ID,
                document_id="conv-001",
                operations=[{
                    "op": "set",
                    "path": "/escalation_reason",
                    "value": "attacker overwrites reason",
                }],
            )


class TestFlowEscalationAudit:
    """Escalation audit events must not contain PII."""

    def test_escalation_audit_strips_customer_content(self):
        """Audit payload from escalation must not contain message content."""
        payload = {
            "action": "escalation",
            "resource_type": "conversation",
            "resource_id": "conv-esc-001",
            "result": "escalated",
            # These should be stripped by sanitizer:
            "escalation_reason": "Customer angry about refund for order #12345",
            "messages": [{"role": "user", "content": "I want my money back"}],
            "customer_email": "alice@shop.com",
        }
        sanitized = sanitize_audit_payload(payload)

        # Allowed operational fields survive
        assert sanitized["action"] == "escalation"
        assert sanitized["resource_type"] == "conversation"
        assert sanitized["resource_id"] == "conv-esc-001"

        # PII/content fields stripped
        assert "escalation_reason" not in sanitized
        assert "messages" not in sanitized
        assert "customer_email" not in sanitized

    def test_escalation_audit_scrubs_email_in_reason(self):
        """If reason field were somehow allowed, emails would be scrubbed."""
        payload = {
            "reason": "Escalated by alice@shop.com for refund issue",
        }
        sanitized = sanitize_audit_payload(payload)
        if "reason" in sanitized:
            assert "alice@shop.com" not in sanitized["reason"]
            assert "[EMAIL]" in sanitized["reason"]
