"""
Flow tests: Caller-level encrypted field patch safety.

Verifies that callers identified in the S218 Codex NO-GO report
no longer trigger EncryptedFieldPatchError at runtime.

Each test simulates the caller's update flow and verifies:
  1. No EncryptedFieldPatchError is raised
  2. Encrypted fields are updated correctly (read-modify-write)
  3. Non-encrypted fields are patched normally

S218 Codex findings:
  - admin_team_api.py:752 — display_name patch
  - admin_knowledge_api.py:998,1000 — title/content patch
  - activation_service.py:1158-1160 — custom_instructions/return_policy/shipping_info

GOV-19: Outside-in testing.
SPEC-1843: Zero-knowledge architecture.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

from unittest.mock import patch, AsyncMock, MagicMock

import pytest

from tests.conftest import STARTER_TENANT_ID, MockCosmosManager, MockContainerProxy
from src.multi_tenant.repositories.base import EncryptedFieldPatchError

from tests.flows.test_flow_encryption_roundtrip import (
    _mock_encryption_service,
    _mock_cosmos_for_repo,
)


# ---------------------------------------------------------------------------
# Flow: Team member update (admin_team_api caller)
# ---------------------------------------------------------------------------

class TestFlowTeamMemberUpdate:
    """Team member display_name update must use read-modify-write, not patch."""

    @pytest.mark.asyncio
    async def test_update_display_name_no_patch_error(self):
        """Updating display_name via update_encrypted_fields doesn't raise."""
        from src.multi_tenant.repositories.team import TeamMemberRepository
        from pydantic import BaseModel

        class FakeTeamDoc(BaseModel):
            id: str
            tenant_id: str
            email: str
            display_name: str
            role: str
            partition_key: str

        repo = TeamMemberRepository()

        with _mock_encryption_service(), _mock_cosmos_for_repo(repo) as container:
            # Seed member
            await repo.create(
                tenant_id=STARTER_TENANT_ID,
                document=FakeTeamDoc(
                    id="member-update-001",
                    tenant_id=STARTER_TENANT_ID,
                    email="alice@example.com",
                    display_name="Alice Smith",
                    role="agent",
                    partition_key=STARTER_TENANT_ID,
                ),
            )

            # MockContainerProxy needs replace_item for update_encrypted_fields
            container.replace_item = _make_replace_item(container)

            # Update display_name via safe path (not patch)
            result = await repo.update_encrypted_fields(
                tenant_id=STARTER_TENANT_ID,
                document_id="member-update-001",
                field_updates={"display_name": "Alice Jones"},
            )

            assert result["display_name"] == "Alice Jones"
            assert result["email"] == "alice@example.com"  # unchanged

    @pytest.mark.asyncio
    async def test_patch_role_still_works(self):
        """Non-encrypted field (role) can still be patched directly."""
        from src.multi_tenant.repositories.team import TeamMemberRepository
        from pydantic import BaseModel

        class FakeTeamDoc(BaseModel):
            id: str
            tenant_id: str
            email: str
            display_name: str
            role: str
            partition_key: str

        repo = TeamMemberRepository()

        with _mock_encryption_service(), _mock_cosmos_for_repo(repo) as container:
            await repo.create(
                tenant_id=STARTER_TENANT_ID,
                document=FakeTeamDoc(
                    id="member-role-001",
                    tenant_id=STARTER_TENANT_ID,
                    email="bob@example.com",
                    display_name="Bob",
                    role="agent",
                    partition_key=STARTER_TENANT_ID,
                ),
            )

            # Patching role (non-encrypted) should work fine
            result = await repo.patch(
                tenant_id=STARTER_TENANT_ID,
                document_id="member-role-001",
                operations=[{"op": "set", "path": "/role", "value": "escalation_agent"}],
            )
            assert result["role"] == "escalation_agent"


# ---------------------------------------------------------------------------
# Flow: Knowledge entry update (admin_knowledge_api caller)
# ---------------------------------------------------------------------------

class TestFlowKnowledgeEntryUpdate:
    """Knowledge title/content update must use read-modify-write."""

    @pytest.mark.asyncio
    async def test_update_title_content_no_patch_error(self):
        """Updating title+content via update_encrypted_fields doesn't raise."""
        from src.multi_tenant.repositories.knowledge import KnowledgeBaseRepository
        from pydantic import BaseModel

        class FakeKBDoc(BaseModel):
            id: str
            tenant_id: str
            title: str
            content: str
            entry_type: str
            partition_key: str

        repo = KnowledgeBaseRepository()

        with _mock_encryption_service(), _mock_cosmos_for_repo(repo) as container:
            await repo.create(
                tenant_id=STARTER_TENANT_ID,
                document=FakeKBDoc(
                    id="kb-update-001",
                    tenant_id=STARTER_TENANT_ID,
                    title="Old Title",
                    content="Old content about returns.",
                    entry_type="policy",
                    partition_key=STARTER_TENANT_ID,
                ),
            )

            container.replace_item = _make_replace_item(container)

            result = await repo.update_encrypted_fields(
                tenant_id=STARTER_TENANT_ID,
                document_id="kb-update-001",
                field_updates={
                    "title": "Updated Return Policy",
                    "content": "New content: 60-day returns on all items.",
                },
            )

            assert result["title"] == "Updated Return Policy"
            assert result["content"] == "New content: 60-day returns on all items."
            assert result["entry_type"] == "policy"  # unchanged

    @pytest.mark.asyncio
    async def test_patch_entry_type_still_works(self):
        """Non-encrypted field (entry_type) can still be patched directly."""
        from src.multi_tenant.repositories.knowledge import KnowledgeBaseRepository
        from pydantic import BaseModel

        class FakeKBDoc(BaseModel):
            id: str
            tenant_id: str
            title: str
            content: str
            entry_type: str
            partition_key: str

        repo = KnowledgeBaseRepository()

        with _mock_encryption_service(), _mock_cosmos_for_repo(repo) as container:
            await repo.create(
                tenant_id=STARTER_TENANT_ID,
                document=FakeKBDoc(
                    id="kb-type-001",
                    tenant_id=STARTER_TENANT_ID,
                    title="Test",
                    content="Test content",
                    entry_type="faq",
                    partition_key=STARTER_TENANT_ID,
                ),
            )

            result = await repo.patch(
                tenant_id=STARTER_TENANT_ID,
                document_id="kb-type-001",
                operations=[{"op": "set", "path": "/entry_type", "value": "policy"}],
            )
            assert result["entry_type"] == "policy"


# ---------------------------------------------------------------------------
# Flow: Activation reset (activation_service caller)
# ---------------------------------------------------------------------------

class TestFlowActivationReset:
    """Preferences reset must use read-modify-write for encrypted fields."""

    @pytest.mark.asyncio
    async def test_reset_encrypted_prefs_no_patch_error(self):
        """Resetting custom_instructions/return_policy/shipping_info via update_encrypted_fields."""
        from src.multi_tenant.repositories.preferences import PreferencesRepository
        from pydantic import BaseModel

        class FakePrefsDoc(BaseModel):
            id: str
            tenant_id: str
            custom_instructions: str
            return_policy: str
            shipping_info: str
            brand_name: str
            partition_key: str

        repo = PreferencesRepository()

        with _mock_encryption_service(), _mock_cosmos_for_repo(repo) as container:
            await repo.create(
                tenant_id=STARTER_TENANT_ID,
                document=FakePrefsDoc(
                    id="prefs-reset-001",
                    tenant_id=STARTER_TENANT_ID,
                    custom_instructions="Be very friendly and helpful",
                    return_policy="30 days full refund",
                    shipping_info="Free shipping over $50",
                    brand_name="Alice's Store",
                    partition_key=STARTER_TENANT_ID,
                ),
            )

            container.replace_item = _make_replace_item(container)

            # Reset encrypted fields to empty (matching activation_service reset)
            result = await repo.update_encrypted_fields(
                tenant_id=STARTER_TENANT_ID,
                document_id="prefs-reset-001",
                field_updates={
                    "custom_instructions": "",
                    "return_policy": "",
                    "shipping_info": "",
                },
            )

            assert result["custom_instructions"] == ""
            assert result["return_policy"] == ""
            assert result["shipping_info"] == ""
            assert result["brand_name"] == "Alice's Store"  # unchanged

    @pytest.mark.asyncio
    async def test_patch_non_encrypted_prefs_still_works(self):
        """Non-encrypted pref fields (brand_name) can still be patched."""
        from src.multi_tenant.repositories.preferences import PreferencesRepository
        from pydantic import BaseModel

        class FakePrefsDoc(BaseModel):
            id: str
            tenant_id: str
            brand_name: str
            partition_key: str

        repo = PreferencesRepository()

        with _mock_encryption_service(), _mock_cosmos_for_repo(repo) as container:
            await repo.create(
                tenant_id=STARTER_TENANT_ID,
                document=FakePrefsDoc(
                    id="prefs-patch-001",
                    tenant_id=STARTER_TENANT_ID,
                    brand_name="Old Brand",
                    partition_key=STARTER_TENANT_ID,
                ),
            )

            result = await repo.patch(
                tenant_id=STARTER_TENANT_ID,
                document_id="prefs-patch-001",
                operations=[{"op": "set", "path": "/brand_name", "value": "New Brand"}],
            )
            assert result["brand_name"] == "New Brand"


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def _make_replace_item(container: MockContainerProxy):
    """Create an async replace_item method for MockContainerProxy."""
    async def replace_item(item: str, body: dict, **kwargs) -> dict:
        container.items = [
            doc for doc in container.items
            if doc.get("id") != item
        ]
        container.items.append(body)
        return body
    return replace_item
