"""Regression tests for CamelCaseModel base class and API DTO serialization.

Verifies that all API response/request DTOs correctly inherit camelCase
alias generation from the shared base class (R8 refactoring, session 31).

Run:
    python -m pytest tests/multi_tenant/test_api_models.py -v

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""


from src.multi_tenant.api_models import CamelCaseModel


# ---------------------------------------------------------------------------
# R8-01: CamelCaseModel base class produces camelCase aliases
# ---------------------------------------------------------------------------


class TestCamelCaseModel:
    """Verify CamelCaseModel base class behavior."""

    def test_r8_01_camel_case_alias_generation(self):
        """Fields with snake_case names serialize to camelCase."""

        class SampleDTO(CamelCaseModel):
            user_name: str = "test"
            is_active: bool = True
            total_count: int = 42

        dto = SampleDTO()
        data = dto.model_dump(by_alias=True)
        assert "userName" in data
        assert "isActive" in data
        assert "totalCount" in data
        assert "user_name" not in data

    def test_r8_02_populate_by_name_works(self):
        """Model can be constructed using Python field names (not just aliases)."""

        class SampleDTO(CamelCaseModel):
            first_name: str
            last_name: str

        # Construct using snake_case (Python field names)
        dto = SampleDTO(first_name="Alice", last_name="Smith")
        assert dto.first_name == "Alice"
        assert dto.last_name == "Smith"

    def test_r8_03_populate_by_alias_works(self):
        """Model can be constructed using camelCase aliases (from JSON input)."""

        class SampleDTO(CamelCaseModel):
            first_name: str
            last_name: str

        # Construct using camelCase (as from JSON deserialization)
        dto = SampleDTO(firstName="Bob", lastName="Jones")
        assert dto.first_name == "Bob"
        assert dto.last_name == "Jones"

    def test_r8_04_json_output_uses_camel_case(self):
        """model_dump(mode='json', by_alias=True) produces camelCase keys."""

        class SampleDTO(CamelCaseModel):
            billing_period: str = "2026-02"
            overage_cost: float = 0.0

        dto = SampleDTO()
        json_data = dto.model_dump(mode="json", by_alias=True)
        assert "billingPeriod" in json_data
        assert "overageCost" in json_data

    def test_r8_05_inheritance_preserves_config(self):
        """Subclasses of CamelCaseModel inherit the alias configuration."""

        class ParentDTO(CamelCaseModel):
            parent_field: str = "parent"

        class ChildDTO(ParentDTO):
            child_field: str = "child"

        dto = ChildDTO()
        data = dto.model_dump(by_alias=True)
        assert "parentField" in data
        assert "childField" in data


# ---------------------------------------------------------------------------
# R8-06 through R8-13: Spot-check actual API DTOs from each refactored file
# ---------------------------------------------------------------------------


class TestRefactoredDTOs:
    """Spot-check that actual API DTOs from each module produce camelCase."""

    def test_r8_06_analytics_dto(self):
        """admin_analytics_api.py DTOs use camelCase."""
        from src.multi_tenant.admin_analytics_api import StatusBreakdown

        dto = StatusBreakdown(status="active", count=5)
        data = dto.model_dump(by_alias=True)
        assert data == {"status": "active", "count": 5}
        assert isinstance(dto, CamelCaseModel)

    def test_r8_07_apikey_dto(self):
        """admin_apikey_api.py DTOs use camelCase."""
        from src.multi_tenant.admin_apikey_api import ApiKeyMetadataResponse

        dto = ApiKeyMetadataResponse(has_key=True, key_prefix="ar_live_test_")
        data = dto.model_dump(by_alias=True)
        assert "hasKey" in data
        assert "keyPrefix" in data
        assert isinstance(dto, CamelCaseModel)

    def test_r8_08_conversation_dto(self):
        """admin_conversation_api.py DTOs use camelCase."""
        from src.multi_tenant.admin_conversation_api import (
            AdminConversationSummary,
        )

        dto = AdminConversationSummary(
            conversation_id="conv-001",
            is_billable=True,
            message_count=5,
        )
        data = dto.model_dump(by_alias=True)
        assert "conversationId" in data
        assert "isBillable" in data
        assert "messageCount" in data
        assert isinstance(dto, CamelCaseModel)

    def test_r8_09_knowledge_dto(self):
        """admin_knowledge_api.py DTOs use camelCase."""
        from src.multi_tenant.admin_knowledge_api import KnowledgeEntryResponse

        dto = KnowledgeEntryResponse(
            id="kb-001",
            tenant_id="t-001",
            entry_type="faq",
            title="Test",
            content="Body",
            created_at="2026-01-01T00:00:00Z",
            updated_at="2026-01-01T00:00:00Z",
        )
        data = dto.model_dump(by_alias=True)
        assert "tenantId" in data
        assert "entryType" in data
        assert "createdAt" in data
        assert isinstance(dto, CamelCaseModel)

    def test_r8_10_quick_action_dto(self):
        """admin_quick_action_api.py DTOs use camelCase."""
        from src.multi_tenant.admin_quick_action_api import QuickActionResponse

        dto = QuickActionResponse(
            id="qa-001",
            label="Test Action",
            prompt_template="Hello {name}",
            created_at="2026-01-01T00:00:00Z",
            updated_at="2026-01-01T00:00:00Z",
        )
        data = dto.model_dump(by_alias=True)
        assert "promptTemplate" in data
        assert "createdAt" in data
        assert isinstance(dto, CamelCaseModel)

    def test_r8_11_team_dto(self):
        """admin_team_api.py DTOs use camelCase."""
        from src.multi_tenant.admin_team_api import TeamMemberResponse

        dto = TeamMemberResponse(
            id="m-001",
            tenant_id="t-001",
            display_name="Alice",
            email="alice@example.com",
            role="ADMIN",
            is_active=True,
            created_at="2026-01-01T00:00:00Z",
            updated_at="2026-01-01T00:00:00Z",
        )
        data = dto.model_dump(by_alias=True)
        assert "displayName" in data
        assert "isActive" in data
        assert "createdAt" in data
        assert isinstance(dto, CamelCaseModel)

    def test_r8_12_superadmin_dto(self):
        """superadmin_api.py DTOs use camelCase."""
        from src.multi_tenant.superadmin_api import TenantSummaryItem

        dto = TenantSummaryItem(
            tenant_id="t-001",
            status="active",
            tier="professional",
            billing_channel="stripe",
        )
        data = dto.model_dump(by_alias=True)
        assert "tenantId" in data
        assert "billingChannel" in data
        assert isinstance(dto, CamelCaseModel)

    def test_r8_13_usage_dashboard_dto(self):
        """usage_dashboard_api.py DTOs use camelCase."""
        from src.multi_tenant.usage_dashboard_api import UsageDashboardResponse

        dto = UsageDashboardResponse(
            tenant_id="t-001",
            billing_period="2026-02",
            total_conversations=100,
            included_allowance=50,
            remaining_included=10,
            pack_balance=0,
            overage_conversations=40,
            overage_reported=40,
            usage_percent=200.0,
            estimated_overage_cost=8.0,
        )
        data = dto.model_dump(by_alias=True)
        assert "tenantId" in data
        assert "billingPeriod" in data
        assert "totalConversations" in data
        assert "overageConversations" in data
        assert isinstance(dto, CamelCaseModel)
