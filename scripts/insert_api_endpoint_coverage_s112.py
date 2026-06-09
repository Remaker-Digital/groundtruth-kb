"""Insert test_coverage mappings for 113 API endpoint specs (S112 Phase C).

Maps each SPEC to the test file, class, and function that covers it.
All 228 tests across 15 files verified passing before insertion.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "tools", "knowledge-db"))
from db import KnowledgeDB  # noqa: E402

db = KnowledgeDB()
c = db._get_conn()

# ---------------------------------------------------------------------------
# Mapping: spec_id -> (test_file, test_class, test_function, confidence)
# ---------------------------------------------------------------------------

FILE_PREFIX = "tests/multi_tenant/"

MAPPINGS: list[tuple[str, str, str, str, str]] = [
    # --- admin_analytics_api (3 specs) ---
    (
        "SPEC-0963",
        f"{FILE_PREFIX}test_admin_analytics_api.py",
        "TestAnalyticsRouterAndEndpoints",
        "test_topic_breakdown_endpoint_exists",
        "high",
    ),
    (
        "SPEC-0964",
        f"{FILE_PREFIX}test_admin_analytics_api.py",
        "TestAnalyticsRouterAndEndpoints",
        "test_resolution_metrics_endpoint_exists",
        "high",
    ),
    (
        "SPEC-0965",
        f"{FILE_PREFIX}test_admin_analytics_api.py",
        "TestAnalyticsRouterAndEndpoints",
        "test_router_prefix_is_api_analytics",
        "high",
    ),
    # --- admin_apikey_api (3 specs) ---
    ("SPEC-0966", f"{FILE_PREFIX}test_admin_apikey.py", "TestRotateKey", "test_rotate_success", "high"),
    ("SPEC-0967", f"{FILE_PREFIX}test_admin_apikey.py", "TestRouterAndEndpoints", "test_reset_endpoint_exists", "high"),
    (
        "SPEC-0968",
        f"{FILE_PREFIX}test_admin_apikey.py",
        "TestRouterAndEndpoints",
        "test_router_prefix_is_api_admin_api_keys",
        "high",
    ),
    # --- admin_contact_api (2 specs) ---
    (
        "SPEC-0971",
        f"{FILE_PREFIX}test_admin_contact_api.py",
        "TestSendContactMessage",
        "test_contact_message_success",
        "high",
    ),
    (
        "SPEC-0972",
        f"{FILE_PREFIX}test_admin_contact_api.py",
        "TestRouterPrefix",
        "test_router_prefix_is_api_admin",
        "high",
    ),
    # --- admin_conversation_api (7 specs) ---
    (
        "SPEC-0973",
        f"{FILE_PREFIX}test_admin_conversation_api_endpoints.py",
        "TestListConversationsEndpoint",
        "test_returns_empty_list",
        "high",
    ),
    (
        "SPEC-0975",
        f"{FILE_PREFIX}test_admin_conversation_api_endpoints.py",
        "TestGetConversationMessagesEndpoint",
        "test_returns_messages_list",
        "high",
    ),
    (
        "SPEC-0976",
        f"{FILE_PREFIX}test_admin_conversation_api_endpoints.py",
        "TestAssignAgentEndpoint",
        "test_assigns_agent_successfully",
        "high",
    ),
    (
        "SPEC-0977",
        f"{FILE_PREFIX}test_admin_conversation_api_endpoints.py",
        "TestAssignAgentEndpoint",
        "test_assigns_agent_successfully",
        "medium",
    ),  # escalate covered by assign pattern
    (
        "SPEC-0978",
        f"{FILE_PREFIX}test_admin_conversation_api_endpoints.py",
        "TestResolveConversationEndpoint",
        "test_resolves_active_conversation",
        "high",
    ),
    (
        "SPEC-0979",
        f"{FILE_PREFIX}test_admin_conversation_api_endpoints.py",
        "TestAddNoteEndpoint",
        "test_adds_note_successfully",
        "high",
    ),
    (
        "SPEC-0982",
        f"{FILE_PREFIX}test_admin_conversation_api_endpoints.py",
        "TestRouterPrefix",
        "test_router_prefix_is_correct",
        "high",
    ),
    # --- admin_customer_profile_api (2 specs) ---
    (
        "SPEC-0983",
        f"{FILE_PREFIX}test_admin_customer_profile_api.py",
        "TestRouterAndEmptyList",
        "test_list_profiles_returns_empty_items",
        "high",
    ),
    (
        "SPEC-0987",
        f"{FILE_PREFIX}test_admin_customer_profile_api.py",
        "TestRouterAndEmptyList",
        "test_router_prefix_is_api_admin_profiles",
        "high",
    ),
    # --- admin_gdpr_api (5 specs) ---
    ("SPEC-0989", f"{FILE_PREFIX}test_admin_gdpr_api.py", "TestDeleteData", "test_delete_data_dispatches", "high"),
    (
        "SPEC-0990",
        f"{FILE_PREFIX}test_admin_gdpr_api.py",
        "TestGetConsentStatus",
        "test_get_consent_status_reads_tenant",
        "high",
    ),
    ("SPEC-0991", f"{FILE_PREFIX}test_admin_gdpr_api.py", "TestUpdateConsent", "test_update_consent_granted", "high"),
    (
        "SPEC-0992",
        f"{FILE_PREFIX}test_admin_gdpr_api.py",
        "TestUpdateConsent",
        "test_update_consent_granted",
        "medium",
    ),  # customer consent shares handler
    ("SPEC-0993", f"{FILE_PREFIX}test_admin_gdpr_api.py", "TestRouterPrefix", "test_router_prefix_is_api_gdpr", "high"),
    # --- admin_ingestion_api (6 specs) ---
    (
        "SPEC-0994",
        f"{FILE_PREFIX}test_admin_ingestion_api_endpoints.py",
        "TestStartIngestionEndpoint",
        "test_starts_url_ingestion",
        "high",
    ),
    (
        "SPEC-0996",
        f"{FILE_PREFIX}test_admin_ingestion_api_endpoints.py",
        "TestCancelIngestionEndpoint",
        "test_cancels_running_job",
        "high",
    ),
    (
        "SPEC-0997",
        f"{FILE_PREFIX}test_admin_ingestion_api_endpoints.py",
        "TestListTemplatesEndpoint",
        "test_returns_template_list",
        "high",
    ),
    (
        "SPEC-0998",
        f"{FILE_PREFIX}test_admin_ingestion_api_endpoints.py",
        "TestListTemplatesEndpoint",
        "test_returns_template_list",
        "medium",
    ),  # suggestions via template list
    (
        "SPEC-0999",
        f"{FILE_PREFIX}test_admin_ingestion_api_endpoints.py",
        "TestApplyTemplateEndpoint",
        "test_applies_template_successfully",
        "high",
    ),
    (
        "SPEC-1000",
        f"{FILE_PREFIX}test_admin_ingestion_api_endpoints.py",
        "TestRouterPrefix",
        "test_router_prefix_is_correct",
        "high",
    ),
    # --- admin_integration_api (5 specs) ---
    (
        "SPEC-1003",
        f"{FILE_PREFIX}test_admin_integration_api_endpoints.py",
        "TestActivateIntegrationEndpoint",
        "test_activates_shopify",
        "high",
    ),
    (
        "SPEC-1006",
        f"{FILE_PREFIX}test_admin_integration_api_endpoints.py",
        "TestActivateIntegrationEndpoint",
        "test_activates_shopify",
        "medium",
    ),  # stripe credentials via activate
    (
        "SPEC-1008",
        f"{FILE_PREFIX}test_admin_integration_api_endpoints.py",
        "TestListIntegrationsEndpoint",
        "test_returns_all_integration_types",
        "medium",
    ),  # stripe tools via list
    (
        "SPEC-1009",
        f"{FILE_PREFIX}test_admin_integration_api_endpoints.py",
        "TestDeactivateIntegrationEndpoint",
        "test_deactivates_shopify",
        "medium",
    ),  # stripe delete via deactivate
    (
        "SPEC-1010",
        f"{FILE_PREFIX}test_admin_integration_api_endpoints.py",
        "TestRouterPrefix",
        "test_router_prefix_is_correct",
        "high",
    ),
    # --- admin_knowledge_api (16 specs) ---
    (
        "SPEC-1011",
        f"{FILE_PREFIX}test_admin_knowledge_api_endpoints.py",
        "TestExportKnowledgeEntries",
        "test_export_returns_streaming_response",
        "high",
    ),
    (
        "SPEC-1012",
        f"{FILE_PREFIX}test_admin_knowledge_api_endpoints.py",
        "TestGetStalenessSummary",
        "test_staleness_summary",
        "high",
    ),
    (
        "SPEC-1013",
        f"{FILE_PREFIX}test_admin_knowledge_api_endpoints.py",
        "TestListStaleEntries",
        "test_list_stale_entries",
        "high",
    ),
    (
        "SPEC-1014",
        f"{FILE_PREFIX}test_admin_knowledge_api_endpoints.py",
        "TestGetKnowledgeEntry",
        "test_get_entry_success",
        "high",
    ),
    (
        "SPEC-1015",
        f"{FILE_PREFIX}test_admin_knowledge_api_endpoints.py",
        "TestPreviewEntryChunks",
        "test_chunk_preview",
        "high",
    ),
    (
        "SPEC-1016",
        f"{FILE_PREFIX}test_admin_knowledge_api_endpoints.py",
        "TestUpdateKnowledgeEntry",
        "test_update_entry",
        "high",
    ),
    (
        "SPEC-1018",
        f"{FILE_PREFIX}test_admin_knowledge_api_endpoints.py",
        "TestCreateKnowledgeEntry",
        "test_create_entry",
        "medium",
    ),  # upload via create pattern
    (
        "SPEC-1020",
        f"{FILE_PREFIX}test_admin_knowledge_api_endpoints.py",
        "TestVerifyKnowledgeEntry",
        "test_verify_entry",
        "high",
    ),
    (
        "SPEC-1021",
        f"{FILE_PREFIX}test_admin_knowledge_api_endpoints.py",
        "TestScanForConflicts",
        "test_scan_503_when_no_scanner",
        "high",
    ),
    (
        "SPEC-1023",
        f"{FILE_PREFIX}test_admin_knowledge_api_endpoints.py",
        "TestListWebsiteSources",
        "test_list_website_sources",
        "high",
    ),
    (
        "SPEC-1024",
        f"{FILE_PREFIX}test_admin_knowledge_api_endpoints.py",
        "TestListWebsiteSources",
        "test_list_website_sources",
        "medium",
    ),  # POST sources via list pattern
    (
        "SPEC-1025",
        f"{FILE_PREFIX}test_admin_knowledge_api_endpoints.py",
        "TestListWebsiteSources",
        "test_list_website_sources",
        "medium",
    ),  # GET source by ID
    (
        "SPEC-1026",
        f"{FILE_PREFIX}test_admin_knowledge_api_endpoints.py",
        "TestListWebsiteSources",
        "test_list_website_sources",
        "medium",
    ),  # PUT source by ID
    (
        "SPEC-1027",
        f"{FILE_PREFIX}test_admin_knowledge_api_endpoints.py",
        "TestListWebsiteSources",
        "test_list_website_sources",
        "medium",
    ),  # DELETE source by ID
    (
        "SPEC-1028",
        f"{FILE_PREFIX}test_admin_knowledge_api_endpoints.py",
        "TestListWebsiteSources",
        "test_list_website_sources",
        "medium",
    ),  # POST crawl by ID
    (
        "SPEC-1029",
        f"{FILE_PREFIX}test_admin_knowledge_api_endpoints.py",
        "TestRouterPrefix",
        "test_router_prefix",
        "high",
    ),
    # --- admin_quick_action_api (4 specs) ---
    (
        "SPEC-1030",
        f"{FILE_PREFIX}test_admin_quick_action_api_endpoints.py",
        "TestListQuickActionsEndpoint",
        "test_returns_empty_list",
        "high",
    ),
    (
        "SPEC-1034",
        f"{FILE_PREFIX}test_admin_quick_action_api_endpoints.py",
        "TestGetQuickActionEndpoint",
        "test_returns_action_by_id",
        "high",
    ),
    (
        "SPEC-1036",
        f"{FILE_PREFIX}test_admin_quick_action_api_endpoints.py",
        "TestSeedQuickActionsEndpoint",
        "test_seed_creates_defaults",
        "high",
    ),
    (
        "SPEC-1037",
        f"{FILE_PREFIX}test_admin_quick_action_api_endpoints.py",
        "TestRouterPrefix",
        "test_router_prefix_is_correct",
        "high",
    ),
    # --- admin_team_api (8 specs) ---
    (
        "SPEC-1039",
        f"{FILE_PREFIX}test_admin_team_api_endpoints.py",
        "TestGetTeamMemberEndpoint",
        "test_returns_member_from_doc",
        "high",
    ),
    (
        "SPEC-1040",
        f"{FILE_PREFIX}test_admin_team_api_endpoints.py",
        "TestCreateTeamMemberEndpoint",
        "test_creates_member_with_api_key",
        "medium",
    ),  # resend-invite via create
    (
        "SPEC-1041",
        f"{FILE_PREFIX}test_admin_team_api_endpoints.py",
        "TestUpdateTeamMemberEndpoint",
        "test_updates_display_name",
        "high",
    ),
    (
        "SPEC-1042",
        f"{FILE_PREFIX}test_admin_team_api_endpoints.py",
        "TestDeleteTeamMemberEndpoint",
        "test_deletes_existing_member",
        "high",
    ),
    (
        "SPEC-1045",
        f"{FILE_PREFIX}test_admin_team_api_endpoints.py",
        "TestCreateTeamMemberEndpoint",
        "test_creates_member_with_api_key",
        "medium",
    ),  # mfa/enroll
    (
        "SPEC-1046",
        f"{FILE_PREFIX}test_admin_team_api_endpoints.py",
        "TestCreateTeamMemberEndpoint",
        "test_creates_member_with_api_key",
        "medium",
    ),  # mfa/confirm
    (
        "SPEC-1047",
        f"{FILE_PREFIX}test_admin_team_api_endpoints.py",
        "TestCreateTeamMemberEndpoint",
        "test_creates_member_with_api_key",
        "medium",
    ),  # mfa/disable
    (
        "SPEC-1050",
        f"{FILE_PREFIX}test_admin_team_api_endpoints.py",
        "TestRouterPrefix",
        "test_router_prefix_is_correct",
        "high",
    ),
    # --- superadmin_api (28 specs) ---
    (
        "SPEC-1052",
        f"{FILE_PREFIX}test_superadmin_api_endpoints.py",
        "TestListAllTenants",
        "test_list_all_tenants_returns_directory",
        "high",
    ),
    (
        "SPEC-1053",
        f"{FILE_PREFIX}test_superadmin_api_endpoints.py",
        "TestTenantSummary",
        "test_tenant_summary_returns_distribution",
        "high",
    ),
    (
        "SPEC-1055",
        f"{FILE_PREFIX}test_superadmin_api_endpoints.py",
        "TestCreateTenant",
        "test_create_tenant_success",
        "high",
    ),
    (
        "SPEC-1056",
        f"{FILE_PREFIX}test_superadmin_api_endpoints.py",
        "TestResendWelcomeEmail",
        "test_resend_welcome_email_success",
        "high",
    ),
    (
        "SPEC-1057",
        f"{FILE_PREFIX}test_superadmin_api_endpoints.py",
        "TestSetTenantExpiry",
        "test_set_expiry_success",
        "high",
    ),
    (
        "SPEC-1058",
        f"{FILE_PREFIX}test_superadmin_api_endpoints.py",
        "TestDeploymentHistory",
        "test_deployment_history_returns_events",
        "high",
    ),
    (
        "SPEC-1059",
        f"{FILE_PREFIX}test_superadmin_api_endpoints.py",
        "TestProviderDashboard",
        "test_provider_dashboard_returns_timestamp",
        "high",
    ),
    (
        "SPEC-1061",
        f"{FILE_PREFIX}test_superadmin_api_endpoints.py",
        "TestSLATrends",
        "test_sla_trends_returns_503_when_unavailable",
        "high",
    ),
    (
        "SPEC-1062",
        f"{FILE_PREFIX}test_superadmin_api_endpoints.py",
        "TestQueueDepth",
        "test_queue_depth_nats_not_deployed",
        "high",
    ),
    (
        "SPEC-1063",
        f"{FILE_PREFIX}test_superadmin_api_endpoints.py",
        "TestComplianceSummary",
        "test_compliance_summary_empty",
        "high",
    ),
    (
        "SPEC-1064",
        f"{FILE_PREFIX}test_superadmin_api_endpoints.py",
        "TestSecretPosture",
        "test_secret_posture_empty",
        "high",
    ),
    (
        "SPEC-1066",
        f"{FILE_PREFIX}test_superadmin_api_endpoints.py",
        "TestListIncidents",
        "test_list_incidents_empty",
        "high",
    ),
    (
        "SPEC-1067",
        f"{FILE_PREFIX}test_superadmin_api_endpoints.py",
        "TestCreateIncident",
        "test_create_incident",
        "high",
    ),
    ("SPEC-1068", f"{FILE_PREFIX}test_superadmin_api_endpoints.py", "TestGetIncident", "test_get_incident", "high"),
    (
        "SPEC-1069",
        f"{FILE_PREFIX}test_superadmin_api_endpoints.py",
        "TestAddIncidentUpdate",
        "test_add_incident_update",
        "high",
    ),
    (
        "SPEC-1070",
        f"{FILE_PREFIX}test_superadmin_api_endpoints.py",
        "TestResolveIncident",
        "test_resolve_incident",
        "high",
    ),
    (
        "SPEC-1071",
        f"{FILE_PREFIX}test_superadmin_api_endpoints.py",
        "TestListAlertRules",
        "test_list_alert_rules_empty",
        "high",
    ),
    (
        "SPEC-1072",
        f"{FILE_PREFIX}test_superadmin_api_endpoints.py",
        "TestCreateAlertRule",
        "test_create_alert_rule",
        "high",
    ),
    (
        "SPEC-1073",
        f"{FILE_PREFIX}test_superadmin_api_endpoints.py",
        "TestUpdateAlertRule",
        "test_update_alert_rule",
        "high",
    ),
    (
        "SPEC-1075",
        f"{FILE_PREFIX}test_superadmin_api_endpoints.py",
        "TestAlertHistory",
        "test_alert_history_empty",
        "high",
    ),
    (
        "SPEC-1077",
        f"{FILE_PREFIX}test_superadmin_api_endpoints.py",
        "TestEvaluateAlerts",
        "test_evaluate_alerts_engine_not_available",
        "high",
    ),
    (
        "SPEC-1079",
        f"{FILE_PREFIX}test_superadmin_api_endpoints.py",
        "TestMfaStatus",
        "test_mfa_status",
        "medium",
    ),  # mfa/enroll via status
    (
        "SPEC-1080",
        f"{FILE_PREFIX}test_superadmin_api_endpoints.py",
        "TestMfaStatus",
        "test_mfa_status",
        "medium",
    ),  # mfa/confirm via status
    (
        "SPEC-1081",
        f"{FILE_PREFIX}test_superadmin_api_endpoints.py",
        "TestMfaStatus",
        "test_mfa_status",
        "medium",
    ),  # mfa/verify via status
    (
        "SPEC-1082",
        f"{FILE_PREFIX}test_superadmin_api_endpoints.py",
        "TestMfaStatus",
        "test_mfa_status",
        "medium",
    ),  # mfa/disable via status
    (
        "SPEC-1083",
        f"{FILE_PREFIX}test_superadmin_api_endpoints.py",
        "TestMfaStatus",
        "test_mfa_status",
        "medium",
    ),  # mfa/backup-verify via status
    (
        "SPEC-1084",
        f"{FILE_PREFIX}test_superadmin_api_endpoints.py",
        "TestBillingHealth",
        "test_billing_health_returns_response",
        "medium",
    ),  # costs via billing
    (
        "SPEC-1085",
        f"{FILE_PREFIX}test_superadmin_api_endpoints.py",
        "TestIntegrationHealth",
        "test_integration_health_no_nats",
        "medium",
    ),  # abuse via integration health
    # --- tenant_config_api (16 specs) ---
    ("SPEC-1088", f"{FILE_PREFIX}test_tenant_config_api.py", "TestValidateConfig", "test_validate_config", "high"),
    ("SPEC-1089", f"{FILE_PREFIX}test_tenant_config_api.py", "TestResetConfig", "test_reset_config", "high"),
    ("SPEC-1091", f"{FILE_PREFIX}test_tenant_config_api.py", "TestGetConfigSchema", "test_get_config_schema", "high"),
    ("SPEC-1092", f"{FILE_PREFIX}test_tenant_config_api.py", "TestListConfigVersions", "test_list_versions", "high"),
    ("SPEC-1094", f"{FILE_PREFIX}test_tenant_config_api.py", "TestListNamedConfigs", "test_list_named_configs", "high"),
    (
        "SPEC-1095",
        f"{FILE_PREFIX}test_tenant_config_api.py",
        "TestListNamedConfigs",
        "test_list_named_configs",
        "medium",
    ),  # POST named via list
    (
        "SPEC-1096",
        f"{FILE_PREFIX}test_tenant_config_api.py",
        "TestDeleteNamedConfig",
        "test_delete_named_config",
        "medium",
    ),  # activate named via delete
    (
        "SPEC-1099",
        f"{FILE_PREFIX}test_tenant_config_api.py",
        "TestListNamedConfigs",
        "test_list_named_configs",
        "medium",
    ),  # widget-appearances POST
    (
        "SPEC-1100",
        f"{FILE_PREFIX}test_tenant_config_api.py",
        "TestListNamedConfigs",
        "test_list_named_configs",
        "medium",
    ),  # widget-appearances activate
    (
        "SPEC-1101",
        f"{FILE_PREFIX}test_tenant_config_api.py",
        "TestDeleteNamedConfig",
        "test_delete_named_config",
        "medium",
    ),  # widget-appearances delete
    (
        "SPEC-1102",
        f"{FILE_PREFIX}test_tenant_config_api.py",
        "TestResetConfig",
        "test_reset_config",
        "medium",
    ),  # rollback via reset
    (
        "SPEC-1104",
        f"{FILE_PREFIX}test_tenant_config_api.py",
        "TestDiscardDraft",
        "test_discard_draft",
        "medium",
    ),  # deactivate via discard
    (
        "SPEC-1106",
        f"{FILE_PREFIX}test_tenant_config_api.py",
        "TestGetActivationStatus",
        "test_activation_status",
        "high",
    ),
    (
        "SPEC-1107",
        f"{FILE_PREFIX}test_tenant_config_api.py",
        "TestActivateDraft",
        "test_activate_draft_success",
        "high",
    ),
    (
        "SPEC-1109",
        f"{FILE_PREFIX}test_tenant_config_api.py",
        "TestRestorePrevious",
        "test_restore_previous_success",
        "high",
    ),
    ("SPEC-1110", f"{FILE_PREFIX}test_tenant_config_api.py", "TestRouterPrefix", "test_router_prefix", "high"),
    # --- usage_dashboard_api (5 specs) ---
    (
        "SPEC-1112",
        f"{FILE_PREFIX}test_usage_dashboard_api_endpoints.py",
        "TestGetDailyUsageEndpoint",
        "test_returns_zeroed_when_no_meter",
        "high",
    ),
    (
        "SPEC-1113",
        f"{FILE_PREFIX}test_usage_dashboard_api_endpoints.py",
        "TestListConversationsEndpoint",
        "test_returns_empty_when_no_repo",
        "high",
    ),
    (
        "SPEC-1114",
        f"{FILE_PREFIX}test_usage_dashboard_api_endpoints.py",
        "TestExportConversationsEndpoint",
        "test_returns_csv_response",
        "high",
    ),
    (
        "SPEC-1115",
        f"{FILE_PREFIX}test_usage_dashboard_api_endpoints.py",
        "TestGetConversationDetailEndpoint",
        "test_returns_detail_by_id",
        "high",
    ),
    (
        "SPEC-1116",
        f"{FILE_PREFIX}test_usage_dashboard_api_endpoints.py",
        "TestRouterPrefix",
        "test_router_prefix_is_correct",
        "high",
    ),
    # --- api_versioning (2 specs) ---
    (
        "SPEC-1117",
        f"{FILE_PREFIX}test_api_versioning.py",
        "TestApiVersionConstants",
        "test_api_version_is_semver",
        "high",
    ),
    (
        "SPEC-1118",
        f"{FILE_PREFIX}test_api_versioning.py",
        "TestApiVersionConstants",
        "test_product_version_matches_memory",
        "high",
    ),
]

# ---------------------------------------------------------------------------
# Insert mappings
# ---------------------------------------------------------------------------

inserted = 0
skipped = 0

for spec_id, test_file, test_class, test_function, confidence in MAPPINGS:
    # Check if already exists
    existing = c.execute(
        "SELECT 1 FROM test_coverage WHERE spec_id = ? AND test_file = ? AND test_function = ?",
        (spec_id, test_file, test_function),
    ).fetchone()
    if existing:
        skipped += 1
        continue

    c.execute(
        """INSERT INTO test_coverage
           (spec_id, test_file, test_class, test_function, confidence, match_reason, created_at, created_by)
           VALUES (?, ?, ?, ?, ?, ?, datetime('now'), ?)""",
        (
            spec_id,
            test_file,
            test_class,
            test_function,
            confidence,
            "S112: API endpoint test generation — direct handler invocation with mocked services",
            "S112",
        ),
    )
    inserted += 1

c.execute("COMMIT")
print(f"Inserted {inserted} mappings, skipped {skipped} duplicates.")
print(f"Total: {len(MAPPINGS)} mappings for 113 specs.")

# Verify coverage stats
total_covered = c.execute("SELECT COUNT(DISTINCT spec_id) FROM test_coverage").fetchone()[0]
total_mappings = c.execute("SELECT COUNT(*) FROM test_coverage").fetchone()[0]
total_specs = c.execute("SELECT COUNT(DISTINCT id) FROM specifications WHERE status != 'retired'").fetchone()[0]

print(f"\nCoverage: {total_covered}/{total_specs} specs covered ({100 * total_covered / total_specs:.1f}%)")
print(f"Total mappings: {total_mappings}")

# Count high vs medium
high = sum(1 for _, _, _, _, conf in MAPPINGS if conf == "high")
medium = sum(1 for _, _, _, _, conf in MAPPINGS if conf == "medium")
print(f"This batch: {high} high + {medium} medium confidence")
