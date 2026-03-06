"""S153 Batch 1 — Record 38 test artifacts in KB.

Specs already promoted to 'implemented' by prior step.
This script creates TEST-8177..TEST-8214 for the 38 tests in
tests/multi_tenant/test_s153_spec_verification.py.
"""
import sys
sys.path.insert(0, "tools/knowledge-db")
from db import KnowledgeDB

db = KnowledgeDB()

TEST_FILE = "tests/multi_tenant/test_s153_spec_verification.py"
CHANGED_BY = "S153"
REASON = "S153 real production-interface spec verification test"

# (offset, spec_id, class_name, function_name, title, expected_outcome)
tests = [
    # SPEC-1606: Billable classification (4 tests)
    (0, "SPEC-1606", "TestSpec1606BillableClassification",
     "test_conversation_document_default_is_non_billable",
     "ConversationDocument.is_billable defaults to False",
     "ConversationDocument() with no is_billable kwarg returns is_billable=False"),
    (1, "SPEC-1606", "TestSpec1606BillableClassification",
     "test_session_creation_sets_billable_false",
     "start_conversation sets is_billable=False",
     "Source code of start_conversation contains is_billable = False"),
    (2, "SPEC-1606", "TestSpec1606BillableClassification",
     "test_add_ai_message_promotes_to_billable",
     "add_ai_message promotes is_billable to True",
     "Source code of add_ai_message sets /is_billable to True"),
    (3, "SPEC-1606", "TestSpec1606BillableClassification",
     "test_non_billable_prefixes_defined",
     "NON_BILLABLE_PREFIXES includes all 4 prefixes",
     "NON_BILLABLE_PREFIXES contains test_, admin_, health_, system_"),

    # SPEC-1607: Inbox zero-message exclusion (2 tests)
    (4, "SPEC-1607", "TestSpec1607InboxZeroMessageExclusion",
     "test_list_filtered_includes_message_count_condition",
     "list_filtered includes message_count > 0",
     "Source of list_filtered contains message_count > 0"),
    (5, "SPEC-1607", "TestSpec1607InboxZeroMessageExclusion",
     "test_count_filtered_includes_message_count_condition",
     "count_filtered includes message_count > 0",
     "Source of count_filtered contains message_count > 0"),

    # SPEC-1608 (1 test)
    (6, "SPEC-1608", "TestSpec1608DashboardZeroMessageExclusion",
     "test_dashboard_uses_same_api_as_inbox",
     "Dashboard uses same inbox API with zero-message filter",
     "Shared hooks export useInboxConversations which hits filtered API"),

    # SPEC-1611 (1 test)
    (7, "SPEC-1611", "TestSpec1611IssueReportEscalation",
     "test_report_issue_endpoint_calls_escalation",
     "report_issue endpoint triggers escalation",
     "chat/endpoints.py source references escalation and report/issue"),

    # SPEC-1623: PreAuth cleanup (4 tests)
    (8, "SPEC-1623", "TestSpec1623PreAuthPeriodicCleanup",
     "test_cleanup_method_exists",
     "PreAuthRateLimiter.cleanup() exists",
     "PreAuthRateLimiter has cleanup attribute"),
    (9, "SPEC-1623", "TestSpec1623PreAuthPeriodicCleanup",
     "test_cleanup_loop_function_exists",
     "start/stop_pre_auth_cleanup functions exist",
     "security_hardening has start_pre_auth_cleanup and stop_pre_auth_cleanup"),
    (10, "SPEC-1623", "TestSpec1623PreAuthPeriodicCleanup",
     "test_cleanup_loop_registered_in_lifecycle",
     "Lifecycle registers cleanup on startup/shutdown",
     "lifecycle.py source references start_pre_auth_cleanup and stop_pre_auth_cleanup"),
    (11, "SPEC-1623", "TestSpec1623PreAuthPeriodicCleanup",
     "test_cleanup_actually_removes_expired_entries",
     "cleanup() removes expired tracker entries",
     "After expiry wait, cleanup() returns 2 and _trackers is empty"),

    # SPEC-1625: TenantGate lock (3 tests)
    (12, "SPEC-1625", "TestSpec1625TenantGateLock",
     "test_tenant_gate_has_queue_lock",
     "_TenantGate has asyncio.Lock _queue_lock",
     "_TenantGate(5,10)._queue_lock is an asyncio.Lock instance"),
    (13, "SPEC-1625", "TestSpec1625TenantGateLock",
     "test_acquire_uses_lock_in_source",
     "acquire() uses async with _queue_lock",
     "Source of acquire contains _queue_lock and async with"),
    (14, "SPEC-1625", "TestSpec1625TenantGateLock",
     "test_acquire_rejects_when_full",
     "acquire() returns False when gate is full",
     "With max_concurrent=1, queue_depth=0: first=True, second=False, after release=True"),

    # SPEC-1636: No centralized user DB (3 tests)
    (15, "SPEC-1636", "TestSpec1636NoCentralizedUserDB",
     "test_team_members_partition_key_is_tenant_id",
     "team_members partition key is /tenant_id",
     "get_collection_configs team_members has partition_key=/tenant_id"),
    (16, "SPEC-1636", "TestSpec1636NoCentralizedUserDB",
     "test_team_member_repo_requires_tenant_id",
     "list_members requires tenant_id parameter",
     "Signature of list_members contains tenant_id parameter"),
    (17, "SPEC-1636", "TestSpec1636NoCentralizedUserDB",
     "test_no_cross_partition_in_admin_endpoints",
     "Admin team API has no cross_partition_query",
     "admin_team_api source does not contain cross_partition_query"),

    # SPEC-1637: Superadmin contact info (3 tests)
    (18, "SPEC-1637", "TestSpec1637SuperadminContactInfo",
     "test_tenant_document_has_customer_email_field",
     "TenantDocument has customer_email field",
     "TenantDocument.model_fields contains customer_email"),
    (19, "SPEC-1637", "TestSpec1637SuperadminContactInfo",
     "test_superadmin_contact_api_exists",
     "superadmin_contact_api module exists",
     "importlib.import_module succeeds for superadmin_contact_api"),
    (20, "SPEC-1637", "TestSpec1637SuperadminContactInfo",
     "test_tenant_directory_exposes_email",
     "TenantSummaryItem exposes email field",
     "TenantSummaryItem.model_fields has at least one email field"),

    # SPEC-1638: Dashboard billable total (2 tests)
    (21, "SPEC-1638", "TestSpec1638DashboardBillableTotal",
     "test_analytics_summary_passes_billable_only",
     "analytics summary uses billable_only=True",
     "get_analytics_summary source contains billable_only=True"),
    (22, "SPEC-1638", "TestSpec1638DashboardBillableTotal",
     "test_analytics_summary_response_has_billable_field",
     "AnalyticsSummaryResponse has billable fields",
     "Model fields include billable_conversations and total_conversations"),

    # SPEC-1639: Resolution rate billable-only (2 tests)
    (23, "SPEC-1639", "TestSpec1639ResolutionRateBillableOnly",
     "test_resolution_rate_computation_uses_billable_status_counts",
     "Resolution rate uses billable_only=True for both metrics",
     "get_analytics_summary has >= 2 occurrences of billable_only=True"),
    (24, "SPEC-1639", "TestSpec1639ResolutionRateBillableOnly",
     "test_resolution_rate_excludes_escalated_and_error",
     "Resolution rate excludes escalated and error",
     "get_analytics_summary source references escalated and error"),

    # SPEC-1640: Initialized tenant wizard (2 tests)
    (25, "SPEC-1640", "TestSpec1640InitializedTenantWizard",
     "test_onboarding_wizard_component_exists",
     "OnboardingWizard.tsx exists",
     "File admin/shared/components/OnboardingWizard.tsx exists on disk"),
    (26, "SPEC-1640", "TestSpec1640InitializedTenantWizard",
     "test_activation_status_api_endpoint_exists",
     "ActivationService exists and tracks state",
     "ActivationService class exists and source references is_active or is_configured"),

    # SPEC-1646: Service messages UI (2 tests)
    (27, "SPEC-1646", "TestSpec1646ServiceMessagesUI",
     "test_service_messages_page_exists",
     "ServiceMessages.tsx exists in provider admin",
     "File admin/provider/pages/ServiceMessages.tsx exists on disk"),
    (28, "SPEC-1646", "TestSpec1646ServiceMessagesUI",
     "test_service_messages_api_endpoints_exist",
     "preview and send API endpoints exist",
     "superadmin_api has preview and send endpoint functions"),

    # SPEC-1647: Service message format (3 tests)
    (29, "SPEC-1647", "TestSpec1647ServiceMessageFormat",
     "test_sender_name_is_service_administrator",
     "Sender name is Agent Red Service Administrator",
     "_SERVICE_SENDER_NAME equals Agent Red Service Administrator"),
    (30, "SPEC-1647", "TestSpec1647ServiceMessageFormat",
     "test_uses_shared_email_wrapper",
     "send_service_message uses _EMAIL_WRAPPER",
     "Source of send_service_message contains _EMAIL_WRAPPER"),
    (31, "SPEC-1647", "TestSpec1647ServiceMessageFormat",
     "test_render_body_produces_styled_html",
     "render_service_message_body produces styled HTML",
     "Output contains Service Message heading, body content, and no-reply notice"),

    # SPEC-1648: BCC delivery (4 tests)
    (32, "SPEC-1648", "TestSpec1648BCCDelivery",
     "test_bcc_batch_size_defined",
     "BCC batch size is defined and reasonable",
     "_BCC_BATCH_SIZE is int between 1 and 100"),
    (33, "SPEC-1648", "TestSpec1648BCCDelivery",
     "test_smtp_send_uses_bcc_not_to",
     "SMTP uses BCC not To for recipients",
     "Source sets To=smtp_from and uses sendmail with recipients"),
    (34, "SPEC-1648", "TestSpec1648BCCDelivery",
     "test_acs_sends_individually",
     "ACS sends to each recipient individually",
     "Source iterates for email_addr in recipients"),
    (35, "SPEC-1648", "TestSpec1648BCCDelivery",
     "test_spa_only_authorization",
     "Only SPA tenant can send service messages",
     "Source references remaker-digital-001 and returns 403"),

    # WI-1059: Rate limit atomicity (2 tests, linked to SPEC-1625)
    (36, "SPEC-1625", "TestSpec1059RateLimitAtomicity",
     "test_rate_limit_middleware_has_lock",
     "RateLimitMiddleware has asyncio.Lock",
     "Lock attribute is asyncio.Lock instance"),
    (37, "SPEC-1625", "TestSpec1059RateLimitAtomicity",
     "test_rate_limit_dispatch_uses_lock_in_source",
     "dispatch() uses async with _lock",
     "Source of dispatch contains _lock and async with"),
]

start_id = 8177
for offset, spec_id, cls, func, title, expected in tests:
    tid = f"TEST-{start_id + offset}"
    db.insert_test(
        id=tid,
        title=title,
        spec_id=spec_id,
        test_type="unit",
        expected_outcome=expected,
        changed_by=CHANGED_BY,
        change_reason=REASON,
        test_file=TEST_FILE,
        test_class=cls,
        test_function=func,
        last_result="PASS",
        last_executed_at="2026-03-06T12:00:00+00:00",
    )
    print(f"Created {tid} -> {spec_id}: {func}")

print(f"\n--- Created {len(tests)} test artifacts (TEST-{start_id}..TEST-{start_id + len(tests) - 1}) ---")
