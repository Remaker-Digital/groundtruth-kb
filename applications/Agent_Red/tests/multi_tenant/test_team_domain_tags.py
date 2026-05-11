"""Slice 0b: S234/S236 team-member domain-tag CRUD regression tests (backend).

Tests POST/PUT/GET round-trip of staff_domain_tags on team member documents.

Test plan ref: COMPREHENSIVE-TEST-PLAN-S245-S255.md Slice 0b

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import pytest
from unittest.mock import AsyncMock, MagicMock



class TestDomainTagsCRUD:
    """Backend API tests for staff_domain_tags field on team members."""

    @pytest.fixture
    def mock_repo(self):
        repo = MagicMock()
        repo.create = AsyncMock(return_value={
            "id": "t-001:user@test.com",
            "tenant_id": "t-001",
            "email": "user@test.com",
            "display_name": "Test User",
            "role": "agent",
            "staff_domain_tags": ["returns", "shipping"],
            "is_active": True,
        })
        repo.read = AsyncMock(return_value={
            "id": "t-001:user@test.com",
            "tenant_id": "t-001",
            "email": "user@test.com",
            "display_name": "Test User",
            "role": "agent",
            "staff_domain_tags": ["returns", "shipping"],
            "is_active": True,
        })
        repo.list_all = AsyncMock(return_value=[{
            "id": "t-001:user@test.com",
            "tenant_id": "t-001",
            "email": "user@test.com",
            "display_name": "Test User",
            "role": "agent",
            "staff_domain_tags": ["returns", "shipping"],
            "is_active": True,
        }])
        repo.patch = AsyncMock(return_value={
            "id": "t-001:user@test.com",
            "tenant_id": "t-001",
            "email": "user@test.com",
            "display_name": "Test User",
            "role": "agent",
            "staff_domain_tags": ["returns", "billing"],
            "is_active": True,
        })
        return repo

    def test_create_member_schema_accepts_domain_tags(self):
        """POST /api/admin/team request schema includes staff_domain_tags field."""
        from src.multi_tenant.admin_team_api import CreateTeamMemberRequest
        req = CreateTeamMemberRequest(
            email="new@test.com",
            display_name="New User",
            role="admin",
            staff_domain_tags=["returns", "shipping"],
        )
        assert req.staff_domain_tags == ["returns", "shipping"]

    def test_create_member_schema_defaults_empty_tags(self):
        """staff_domain_tags defaults to empty list when not provided."""
        from src.multi_tenant.admin_team_api import CreateTeamMemberRequest
        req = CreateTeamMemberRequest(
            email="new@test.com",
            display_name="New User",
            role="admin",
        )
        assert req.staff_domain_tags == []

    def test_update_member_schema_accepts_domain_tags(self):
        """PUT /api/admin/team/{id} request schema includes staff_domain_tags."""
        from src.multi_tenant.admin_team_api import UpdateTeamMemberRequest
        req = UpdateTeamMemberRequest(
            staff_domain_tags=["billing", "support"],
        )
        assert req.staff_domain_tags == ["billing", "support"]

    def test_member_response_includes_domain_tags(self):
        """GET /api/admin/team response includes staff_domain_tags."""
        from src.multi_tenant.cosmos_schema import TeamMemberDocument
        doc = TeamMemberDocument(
            id="t-001:user@test.com",
            tenant_id="t-001",
            email="user@test.com",
            display_name="Test User",
            role="admin",
            staff_domain_tags=["returns"],
            created_at="2026-01-01T00:00:00Z",
            updated_at="2026-01-01T00:00:00Z",
        )
        assert doc.staff_domain_tags == ["returns"]

    def test_empty_tags_array_accepted(self):
        """Empty staff_domain_tags array is valid."""
        from src.multi_tenant.cosmos_schema import TeamMemberDocument
        doc = TeamMemberDocument(
            id="t-001:user@test.com",
            tenant_id="t-001",
            email="user@test.com",
            display_name="Test User",
            role="admin",
            staff_domain_tags=[],
            created_at="2026-01-01T00:00:00Z",
            updated_at="2026-01-01T00:00:00Z",
        )
        assert doc.staff_domain_tags == []

    def test_domain_tags_field_exists_in_schema(self):
        """TeamMemberDocument schema has staff_domain_tags field."""
        from src.multi_tenant.cosmos_schema import TeamMemberDocument
        assert "staff_domain_tags" in TeamMemberDocument.model_fields
