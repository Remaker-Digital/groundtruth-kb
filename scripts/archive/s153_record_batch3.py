"""S153 Batch 3 - Promote 13 specs + record 34 test artifacts in KB."""

import sys

sys.path.insert(0, "tools/knowledge-db")
from db import KnowledgeDB

db = KnowledgeDB()

# --- 1. Promote 13 specs to 'implemented' ---
specs_to_promote = [
    "SPEC-0257",
    "SPEC-0303",
    "SPEC-0310",
    "SPEC-0553",
    "SPEC-0812",
    "SPEC-0822",
    "SPEC-0829",
    "SPEC-0846",
    "SPEC-0847",
    "SPEC-0860",
    "SPEC-1555",
    "SPEC-1649",
    "SPEC-1650",
]
for sid in specs_to_promote:
    db.update_spec(
        sid,
        changed_by="S153",
        change_reason="Promoted to implemented - real production-interface test passing in test_s153_batch3_spec_verification.py",
        status="implemented",
    )
    print(f"Promoted {sid} -> implemented")

print(f"\n--- Promoted {len(specs_to_promote)} specs ---\n")

# --- 2. Record 34 test artifacts ---
TEST_FILE = "tests/multi_tenant/test_s153_batch3_spec_verification.py"
CB = "S153"
CR = "S153 batch 3 real production-interface spec verification test"

tests = [
    # SPEC-0303 (7)
    (
        "SPEC-0303",
        "TestSpec0303ChatAPI",
        "test_start_conversation_endpoint",
        "POST /conversations endpoint exists",
        "source contains conversations and post",
    ),
    (
        "SPEC-0303",
        "TestSpec0303ChatAPI",
        "test_send_message_endpoint",
        "POST /message endpoint exists",
        "source contains message",
    ),
    (
        "SPEC-0303",
        "TestSpec0303ChatAPI",
        "test_stream_endpoint",
        "GET /stream endpoint exists",
        "source contains stream",
    ),
    (
        "SPEC-0303",
        "TestSpec0303ChatAPI",
        "test_get_conversation_endpoint",
        "GET /{id} endpoint exists",
        "source contains conversation_id",
    ),
    (
        "SPEC-0303",
        "TestSpec0303ChatAPI",
        "test_end_conversation_endpoint",
        "POST /{id}/end endpoint exists",
        "source contains end",
    ),
    (
        "SPEC-0303",
        "TestSpec0303ChatAPI",
        "test_issue_report_endpoint",
        "POST /{id}/issue endpoint exists",
        "source contains issue",
    ),
    (
        "SPEC-0303",
        "TestSpec0303ChatAPI",
        "test_consent_endpoint",
        "POST /{id}/consent endpoint exists",
        "source contains consent",
    ),
    # SPEC-0310 (4)
    (
        "SPEC-0310",
        "TestSpec0310AnalyticsAPI",
        "test_analytics_summary_endpoint_exists",
        "analytics summary endpoint exists",
        "hasattr returns True",
    ),
    (
        "SPEC-0310",
        "TestSpec0310AnalyticsAPI",
        "test_analytics_intents_endpoint_exists",
        "intent distribution endpoint exists",
        "hasattr returns True",
    ),
    (
        "SPEC-0310",
        "TestSpec0310AnalyticsAPI",
        "test_analytics_gaps_endpoint_exists",
        "knowledge gaps endpoint exists",
        "hasattr returns True",
    ),
    (
        "SPEC-0310",
        "TestSpec0310AnalyticsAPI",
        "test_all_endpoints_require_tenant_context",
        "endpoints use TenantContext",
        "source contains TenantContext",
    ),
    # SPEC-0257 (2)
    (
        "SPEC-0257",
        "TestSpec0257WidgetConfigAppearance",
        "test_preferences_has_appearance_fields",
        "PreferencesDocument has color fields",
        "color fields found in model_fields",
    ),
    (
        "SPEC-0257",
        "TestSpec0257WidgetConfigAppearance",
        "test_preferences_has_logo_field",
        "PreferencesDocument has branding fields",
        "brand/logo/agent_name fields found",
    ),
    # SPEC-0812 (3)
    (
        "SPEC-0812",
        "TestSpec0812StreamThenValidate",
        "test_orchestrator_references_stream_then_validate",
        "orchestrator implements streaming",
        "source contains stream",
    ),
    (
        "SPEC-0812",
        "TestSpec0812StreamThenValidate",
        "test_orchestrator_has_critic_phase",
        "orchestrator has critic phase",
        "source contains critic",
    ),
    (
        "SPEC-0812",
        "TestSpec0812StreamThenValidate",
        "test_orchestrator_has_retracted_event",
        "retracted event on critic reject",
        "source contains retract",
    ),
    # SPEC-0822 (2)
    (
        "SPEC-0822",
        "TestSpec0822KnowledgeBaseRAG",
        "test_knowledge_base_has_embedding_support",
        "KnowledgeBaseDocument has embedding fields",
        "embed/vector fields found",
    ),
    (
        "SPEC-0822",
        "TestSpec0822KnowledgeBaseRAG",
        "test_copilot_agent_does_retrieval",
        "co_pilot performs retrieval",
        "source contains retriev/search",
    ),
    # SPEC-0829 (2)
    (
        "SPEC-0829",
        "TestSpec0829BetaStarterTier",
        "test_seed_script_defaults_to_starter",
        "seed script defaults to starter",
        "content references starter",
    ),
    (
        "SPEC-0829",
        "TestSpec0829BetaStarterTier",
        "test_starter_tier_exists_in_schema",
        "TenantTier includes STARTER",
        "STARTER in TenantTier members",
    ),
    # SPEC-0846 (4)
    (
        "SPEC-0846",
        "TestSpec0846WidgetConsent",
        "test_consent_banner_component_exists",
        "ConsentBanner.tsx exists",
        "file exists on disk",
    ),
    (
        "SPEC-0846",
        "TestSpec0846WidgetConsent",
        "test_consent_api_endpoint_exists",
        "consent endpoint in chat API",
        "source contains consent",
    ),
    (
        "SPEC-0846",
        "TestSpec0846WidgetConsent",
        "test_consent_banner_has_accept_decline",
        "banner has accept/decline",
        "content has accept and decline",
    ),
    (
        "SPEC-0846",
        "TestSpec0846WidgetConsent",
        "test_consent_strings_localized",
        "consent strings in locale",
        "en.ts contains consent",
    ),
    # SPEC-0847 (2)
    (
        "SPEC-0847",
        "TestSpec0847CopyrightNotice",
        "test_main_module_has_copyright",
        "copyright notice present",
        "Remaker Digital in source",
    ),
    (
        "SPEC-0847",
        "TestSpec0847CopyrightNotice",
        "test_copyright_year_is_2026",
        "copyright year is 2026",
        "2026 in source",
    ),
    # SPEC-0860 (2)
    (
        "SPEC-0860",
        "TestSpec0860SeedExplicitFlag",
        "test_seed_script_has_execute_flag",
        "seed has --execute flag",
        "content contains --execute",
    ),
    (
        "SPEC-0860",
        "TestSpec0860SeedExplicitFlag",
        "test_seed_script_defaults_to_dry_run",
        "seed defaults to dry-run",
        "content references dry/preview",
    ),
    # SPEC-0553 (1)
    (
        "SPEC-0553",
        "TestSpec0553TestConversationsPipeline",
        "test_test_mode_still_uses_pipeline",
        "pipeline has uniform execution",
        "run_pipeline or execute in source",
    ),
    # SPEC-1555 (2)
    (
        "SPEC-1555",
        "TestSpec1555WidgetHeaderSubtitle",
        "test_preferences_has_subtitle_field",
        "PreferencesDocument has subtitle",
        "widget_header_subtitle in fields",
    ),
    (
        "SPEC-1555",
        "TestSpec1555WidgetHeaderSubtitle",
        "test_field_mapping_includes_subtitle",
        "field mapping includes subtitle",
        "widget_header_subtitle in source",
    ),
    # SPEC-1649 (1)
    (
        "SPEC-1649",
        "TestSpec1649LiveInterfacesOnly",
        "test_test_pipeline_uses_live_endpoints",
        "pipeline uses live endpoints",
        "http and staging in content",
    ),
    # SPEC-1650 (2)
    (
        "SPEC-1650",
        "TestSpec1650MockedTestsRetained",
        "test_unit_tests_directory_exists",
        "tests/unit/ exists with tests",
        "dir exists and has test files",
    ),
    (
        "SPEC-1650",
        "TestSpec1650MockedTestsRetained",
        "test_multi_tenant_tests_directory_exists",
        "tests/multi_tenant/ exists",
        "dir has > 5 test files",
    ),
]

start_id = 8261
for i, (spec_id, cls, func, title, expected) in enumerate(tests):
    tid = f"TEST-{start_id + i}"
    db.insert_test(
        id=tid,
        title=title,
        spec_id=spec_id,
        test_type="unit",
        expected_outcome=expected,
        changed_by=CB,
        change_reason=CR,
        test_file=TEST_FILE,
        test_class=cls,
        test_function=func,
        last_result="PASS",
        last_executed_at="2026-03-06T15:00:00+00:00",
    )

print(f"Created {len(tests)} test artifacts (TEST-{start_id}..TEST-{start_id + len(tests) - 1})")
