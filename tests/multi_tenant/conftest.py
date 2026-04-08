"""Shared fixtures and helpers for multi_tenant mutation tests.

Provides:
    - MutationTestBase mixin with common auth/validation assertions
    - Service wiring fixtures for superadmin, knowledge, team, etc.
    - CRUD lifecycle helpers

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from src.multi_tenant.superadmin_api._monolith import (
    configure_copilot_knowledge_service,
    configure_superadmin_services,
)
from src.multi_tenant.admin_knowledge_api import configure_admin_knowledge_services
from src.multi_tenant.admin_apikey_api import configure_apikey_services
from src.multi_tenant.admin_team_api import configure_admin_team_services
from src.multi_tenant.admin_conversation_api import configure_admin_conversation_services
from src.multi_tenant.admin_quick_action_api import configure_admin_quick_action_services
from src.multi_tenant.memory_dashboard import configure_memory_dashboard


# ---------------------------------------------------------------------------
# MutationTestBase — shared assertion helpers
# ---------------------------------------------------------------------------


class MutationTestBase:
    """Mixin providing common mutation endpoint assertions.

    Subclass this alongside unittest.TestCase or use as a mixin with
    pytest test classes. All methods accept an http method name (string)
    and a URL, plus optional json body.
    """

    @staticmethod
    def assert_requires_auth(raw_client, method: str, url: str, **kwargs):
        """Verify endpoint returns 401 without authentication."""
        resp = getattr(raw_client, method)(url, **kwargs)
        assert resp.status_code == 401, (
            f"Expected 401 for unauthenticated {method.upper()} {url}, "
            f"got {resp.status_code}"
        )

    @staticmethod
    def assert_rejects_widget_key(widget_client, method: str, url: str, **kwargs):
        """Verify admin endpoint rejects widget key auth.

        Widget keys are only valid for /api/chat/* and /api/config.
        Admin endpoints should return 401 (path not allowed for widget keys).
        """
        resp = getattr(widget_client, method)(url, **kwargs)
        assert resp.status_code in (401, 403), (
            f"Expected 401/403 for widget key on {method.upper()} {url}, "
            f"got {resp.status_code}"
        )

    @staticmethod
    def assert_spa_isolation(tenant_client, method: str, url: str, **kwargs):
        """Verify superadmin endpoint returns 403 for tenant keys."""
        resp = getattr(tenant_client, method)(url, **kwargs)
        assert resp.status_code == 403, (
            f"Expected 403 for tenant key on superadmin {method.upper()} {url}, "
            f"got {resp.status_code}"
        )

    @staticmethod
    def assert_validation_error(client, method: str, url: str, **kwargs):
        """Verify malformed input returns 422."""
        resp = getattr(client, method)(url, **kwargs)
        assert resp.status_code == 422, (
            f"Expected 422 for invalid input on {method.upper()} {url}, "
            f"got {resp.status_code}"
        )


# ---------------------------------------------------------------------------
# Mock repository factory helpers
# ---------------------------------------------------------------------------


def make_mock_repo(**overrides) -> AsyncMock:
    """Create a mock repository with common async methods."""
    repo = AsyncMock()
    repo.get = AsyncMock(return_value=None)
    repo.create = AsyncMock(return_value={"id": "mock-id"})
    repo.update = AsyncMock(return_value={"id": "mock-id"})
    repo.delete = AsyncMock(return_value=None)
    repo.list = AsyncMock(return_value=[])
    repo.query = AsyncMock(return_value=[])
    for key, value in overrides.items():
        setattr(repo, key, value)
    return repo


# ---------------------------------------------------------------------------
# Superadmin service fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def superadmin_repos():
    """Pre-configured mock repos for all superadmin domain modules.

    Wires configure_superadmin_services() with mock repos and yields
    a dict of all mocks for test assertions.
    """
    repos = {
        "tenant_repo": make_mock_repo(),
        "audit_repo": make_mock_repo(),
        "conv_repo": make_mock_repo(),
        "usage_repo": make_mock_repo(),
        "prefs_repo": make_mock_repo(),
        "nats_mgr": MagicMock(),
        "secret_service": MagicMock(),
        "incident_repo": make_mock_repo(),
        "alert_rule_repo": make_mock_repo(),
        "alert_history_repo": make_mock_repo(),
        "platform_admin_repo": make_mock_repo(),
    }
    configure_superadmin_services(**repos)
    yield repos
    # Cleanup — reset all module-level refs to None
    configure_superadmin_services(
        tenant_repo=None,
        audit_repo=None,
    )


@pytest.fixture
def copilot_repos():
    """Mock repo for Co-Pilot knowledge management."""
    repo = make_mock_repo()
    configure_copilot_knowledge_service(admin_doc_repo=repo)
    yield {"admin_doc_repo": repo}
    configure_copilot_knowledge_service(admin_doc_repo=None)


# ---------------------------------------------------------------------------
# Tenant admin service fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def knowledge_repos():
    """Mock repos for admin knowledge API."""
    repo = make_mock_repo()
    vectorizer = AsyncMock()
    staleness = AsyncMock()
    scanner = AsyncMock()
    configure_admin_knowledge_services(
        knowledge_repo=repo,
        knowledge_vectorizer=vectorizer,
        staleness_service=staleness,
        conflict_scanner=scanner,
    )
    yield {
        "knowledge_repo": repo,
        "knowledge_vectorizer": vectorizer,
        "staleness_service": staleness,
        "conflict_scanner": scanner,
    }
    configure_admin_knowledge_services(knowledge_repo=None)


@pytest.fixture
def apikey_repos():
    """Mock repos for admin API key endpoints."""
    tenant_repo = make_mock_repo()
    audit_repo = make_mock_repo()
    configure_apikey_services(tenant_repo=tenant_repo, audit_repo=audit_repo)
    yield {"tenant_repo": tenant_repo, "audit_repo": audit_repo}
    configure_apikey_services(tenant_repo=None)


@pytest.fixture
def team_repos():
    """Mock repos for admin team API."""
    team_repo = make_mock_repo()
    audit_repo = make_mock_repo()
    conv_repo = make_mock_repo()
    configure_admin_team_services(
        team_repo=team_repo,
        audit_repo=audit_repo,
        conv_repo=conv_repo,
    )
    yield {
        "team_repo": team_repo,
        "audit_repo": audit_repo,
        "conv_repo": conv_repo,
    }
    configure_admin_team_services(team_repo=None)


@pytest.fixture
def conversation_repos():
    """Mock repos for admin conversation API."""
    conv_repo = make_mock_repo()
    configure_admin_conversation_services(conversation_repo=conv_repo)
    yield {"conversation_repo": conv_repo}
    configure_admin_conversation_services(conversation_repo=None)


@pytest.fixture
def quick_action_repos():
    """Mock repos for admin quick action API."""
    prefs_repo = make_mock_repo()
    configure_admin_quick_action_services(prefs_repo=prefs_repo)
    yield {"prefs_repo": prefs_repo}
    configure_admin_quick_action_services(prefs_repo=None)


@pytest.fixture
def memory_repos():
    """Mock repos for memory dashboard API."""
    memory_repo = make_mock_repo()
    configure_memory_dashboard(memory_repo=memory_repo)
    yield {"memory_repo": memory_repo}
    configure_memory_dashboard(memory_repo=None)
