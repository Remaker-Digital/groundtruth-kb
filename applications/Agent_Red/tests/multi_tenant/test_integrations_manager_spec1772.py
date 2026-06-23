"""SPEC-1772 Integrations Manager Admin UI source coverage.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC.
All rights reserved.
"""

from pathlib import Path

import pytest

pytestmark = pytest.mark.local_env

ROOT = Path(__file__).resolve().parents[2]
ADMIN_SHARED = ROOT / "admin" / "shared"
INTEGRATIONS_MANAGER = ADMIN_SHARED / "IntegrationsManager.tsx"
MCP_CONFIG_PANEL = ADMIN_SHARED / "McpConfigPanel.tsx"
TYPES = ADMIN_SHARED / "types" / "index.ts"


def _source(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _assert_terms(source: str, terms: list[str]) -> None:
    for term in terms:
        assert term in source


def test_integration_cards_expose_status_sync_and_count_fields() -> None:
    source = _source(INTEGRATIONS_MANAGER)

    _assert_terms(
        source,
        [
            "STATUS_LABELS",
            "lastSyncAt",
            "lastSyncStatus",
            "Sync error",
            "ticketCount",
            "articleCount",
            "contactCount",
        ],
    )


def test_oauth_and_api_key_setup_surfaces_are_present() -> None:
    manager = _source(INTEGRATIONS_MANAGER)
    mcp_panel = _source(MCP_CONFIG_PANEL)

    _assert_terms(
        manager,
        [
            "OAuth setup required",
            "click Activate to begin authorization",
            "McpConfigPanel",
        ],
    )
    _assert_terms(
        mcp_panel,
        [
            "API key",
            "Save Key",
            "Test Connection",
        ],
    )


def test_sync_dashboard_includes_sync_now_history_counts_and_errors() -> None:
    source = _source(INTEGRATIONS_MANAGER)
    types = _source(TYPES)

    _assert_terms(
        source,
        [
            "Sync Now",
            "/api/admin/integrations/${integration.type}/sync",
            "Sync History",
            "itemsSynced",
            "Error details",
            "No sync-history events recorded yet.",
        ],
    )
    _assert_terms(types, ["syncHistory?: SyncEvent[]", "errorMessage?: string"])


def test_action_configuration_exposes_hitl_policy_toggles() -> None:
    source = _source(INTEGRATIONS_MANAGER)
    types = _source(TYPES)

    _assert_terms(
        source,
        [
            "Configure HITL",
            "actionConfig",
            "Action type:",
            "HITL policy:",
            'type="checkbox"',
        ],
    )
    _assert_terms(types, ["actionConfig?: ActionConfigItem[]", "hitlPolicy"])


def test_knowledge_integrations_expose_folder_and_page_source_selection() -> None:
    source = _source(INTEGRATIONS_MANAGER)

    _assert_terms(
        source,
        [
            "Knowledge Source Selection",
            "Folder browser",
            "Page browser",
            "Browse Sources",
            "category === 'knowledge'",
            "type === 'google_docs'",
        ],
    )


def test_connection_logs_include_timestamp_severity_message_and_details() -> None:
    source = _source(INTEGRATIONS_MANAGER)
    types = _source(TYPES)

    _assert_terms(
        source,
        [
            "Connection logs for this integration.",
            "/api/admin/integrations/{integration.type}/events",
            "connectionLogs",
            "Severity:",
            "entry.timestamp",
            "entry.message",
            "entry.details",
            "Error details",
        ],
    )
    _assert_terms(
        types,
        [
            "connectionLogs?: ConnectionLogEntry[]",
            "timestamp: string",
            "level: 'info' | 'warning' | 'error'",
            "message: string",
            "details?: string",
        ],
    )


def test_detail_panel_combines_config_sync_actions_and_logs_tabs() -> None:
    source = _source(INTEGRATIONS_MANAGER)

    _assert_terms(
        source,
        [
            "type DetailTab = 'config' | 'sync' | 'actions' | 'logs'",
            "IntegrationDetailPanel",
            "View Details",
            "Hide Details",
            "Category:",
            "Capabilities:",
        ],
    )
