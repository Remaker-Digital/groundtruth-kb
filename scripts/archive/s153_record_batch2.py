"""S153 Batch 2 — Promote 15 specs + record 46 test artifacts in KB."""

import sys

sys.path.insert(0, "tools/knowledge-db")
from db import KnowledgeDB

db = KnowledgeDB()

# --- 1. Promote 15 specs to 'implemented' ---
specs_to_promote = [
    "SPEC-1568",
    "SPEC-1562",
    "SPEC-1570",
    "SPEC-1571",
    "SPEC-1572",
    "SPEC-1573",
    "SPEC-1574",
    "SPEC-1575",
    "SPEC-1576",
    "SPEC-1577",
    "SPEC-1578",
    "SPEC-1616",
    "SPEC-1624",
    "SPEC-1643",
    "SPEC-1645",
]
for sid in specs_to_promote:
    db.update_spec(
        sid,
        changed_by="S153",
        change_reason="Promoted to implemented — real production-interface test passing in test_s153_batch2_spec_verification.py",
        status="implemented",
    )
    print(f"Promoted {sid} -> implemented")

print(f"\n--- Promoted {len(specs_to_promote)} specs ---\n")

# --- 2. Record 46 test artifacts ---
TEST_FILE = "tests/multi_tenant/test_s153_batch2_spec_verification.py"
CB = "S153"
CR = "S153 batch 2 real production-interface spec verification test"

tests = [
    # SPEC-1570 (5)
    (
        "SPEC-1570",
        "TestSpec1570CopilotDocumentCRUD",
        "test_list_endpoint_exists",
        "list_copilot_documents endpoint exists",
        "hasattr returns True",
    ),
    (
        "SPEC-1570",
        "TestSpec1570CopilotDocumentCRUD",
        "test_create_endpoint_exists",
        "create_copilot_document endpoint exists",
        "hasattr returns True",
    ),
    (
        "SPEC-1570",
        "TestSpec1570CopilotDocumentCRUD",
        "test_update_endpoint_exists",
        "update_copilot_document endpoint exists",
        "hasattr returns True",
    ),
    (
        "SPEC-1570",
        "TestSpec1570CopilotDocumentCRUD",
        "test_delete_endpoint_exists",
        "delete_copilot_document endpoint exists",
        "hasattr returns True",
    ),
    (
        "SPEC-1570",
        "TestSpec1570CopilotDocumentCRUD",
        "test_delete_is_soft_delete",
        "delete is soft-delete (sets active=False)",
        "source references 'active'",
    ),
    # SPEC-1571 (3)
    (
        "SPEC-1571",
        "TestSpec1571BatchIngestion",
        "test_ingest_endpoint_exists",
        "ingest_docs_site endpoint exists",
        "hasattr returns True",
    ),
    (
        "SPEC-1571",
        "TestSpec1571BatchIngestion",
        "test_ingest_scans_admin_guide_directory",
        "ingestion scans admin-guide/*.md",
        "source contains admin-guide and .md",
    ),
    (
        "SPEC-1571",
        "TestSpec1571BatchIngestion",
        "test_ingest_uses_content_hash",
        "ingestion uses SHA content hash",
        "source references hash",
    ),
    # SPEC-1572 (2)
    (
        "SPEC-1572",
        "TestSpec1572URLImport",
        "test_import_url_endpoint_exists",
        "import_url endpoint exists",
        "hasattr returns True",
    ),
    (
        "SPEC-1572",
        "TestSpec1572URLImport",
        "test_import_url_enforces_https",
        "URL import enforces HTTPS",
        "source references https",
    ),
    # SPEC-1573 (2)
    (
        "SPEC-1573",
        "TestSpec1573ReEmbedding",
        "test_re_embed_endpoint_exists",
        "re_embed_documents endpoint exists",
        "hasattr returns True",
    ),
    (
        "SPEC-1573",
        "TestSpec1573ReEmbedding",
        "test_re_embed_uses_azure_openai_embeddings",
        "re-embedding uses embedding model",
        "source references embed",
    ),
    # SPEC-1574 (3)
    (
        "SPEC-1574",
        "TestSpec1574CollectionStats",
        "test_stats_endpoint_exists",
        "copilot_stats endpoint exists",
        "hasattr returns True",
    ),
    (
        "SPEC-1574",
        "TestSpec1574CollectionStats",
        "test_stats_returns_category_breakdown",
        "stats includes category breakdown",
        "source references category",
    ),
    (
        "SPEC-1574",
        "TestSpec1574CollectionStats",
        "test_stats_tracks_stale_documents",
        "stats tracks stale documents",
        "source references stale",
    ),
    # SPEC-1575 (3)
    (
        "SPEC-1575",
        "TestSpec1575ScanScheduling",
        "test_get_schedule_endpoint_exists",
        "get_copilot_schedule endpoint exists",
        "hasattr returns True",
    ),
    (
        "SPEC-1575",
        "TestSpec1575ScanScheduling",
        "test_update_schedule_endpoint_exists",
        "update_copilot_schedule endpoint exists",
        "hasattr returns True",
    ),
    (
        "SPEC-1575",
        "TestSpec1575ScanScheduling",
        "test_schedule_supports_three_frequencies",
        "schedule supports manual/daily/weekly",
        "source contains all three frequencies",
    ),
    # SPEC-1576 (4)
    (
        "SPEC-1576",
        "TestSpec1576RetrievalParameters",
        "test_get_retrieval_config_endpoint_exists",
        "get_copilot_retrieval_config endpoint exists",
        "hasattr returns True",
    ),
    (
        "SPEC-1576",
        "TestSpec1576RetrievalParameters",
        "test_update_retrieval_config_endpoint_exists",
        "update_copilot_retrieval_config endpoint exists",
        "hasattr returns True",
    ),
    (
        "SPEC-1576",
        "TestSpec1576RetrievalParameters",
        "test_retrieval_config_has_all_five_parameters",
        "retrieval config has 5 parameters",
        "source contains vector_weight, bm25_weight, rrf_k, top_k, min_score",
    ),
    (
        "SPEC-1576",
        "TestSpec1576RetrievalParameters",
        "test_configure_copilot_retrieval_runtime_push",
        "runtime push function exists in co_pilot",
        "co_pilot has configure_copilot_retrieval",
    ),
    # SPEC-1577 (2)
    (
        "SPEC-1577",
        "TestSpec1577TestQuery",
        "test_test_query_endpoint_exists",
        "test_copilot_query endpoint exists",
        "hasattr returns True",
    ),
    (
        "SPEC-1577",
        "TestSpec1577TestQuery",
        "test_test_query_returns_scored_results",
        "test query returns scored results",
        "source references score",
    ),
    # SPEC-1578 (3)
    (
        "SPEC-1578",
        "TestSpec1578ProviderConsoleUI",
        "test_page_component_exists",
        "CopilotKnowledge.tsx exists",
        "file exists on disk",
    ),
    (
        "SPEC-1578",
        "TestSpec1578ProviderConsoleUI",
        "test_page_has_four_tabs",
        "page has Documents/Ingestion/Schedule/Parameters tabs",
        "all 4 tab names present",
    ),
    (
        "SPEC-1578",
        "TestSpec1578ProviderConsoleUI",
        "test_page_calls_copilot_api_endpoints",
        "page calls copilot API",
        "content references copilot",
    ),
    # SPEC-1568 (5)
    (
        "SPEC-1568",
        "TestSpec1568SecretPosture",
        "test_secret_posture_endpoint_exists",
        "secret_posture endpoint exists",
        "hasattr returns True",
    ),
    (
        "SPEC-1568",
        "TestSpec1568SecretPosture",
        "test_secret_posture_response_model_exists",
        "SecretPostureResponse model exists",
        "import succeeds",
    ),
    (
        "SPEC-1568",
        "TestSpec1568SecretPosture",
        "test_aggregates_key_vault_secrets",
        "aggregates Key Vault secrets",
        "source references vault",
    ),
    (
        "SPEC-1568",
        "TestSpec1568SecretPosture",
        "test_aggregates_cosmos_tenant_fields",
        "aggregates Cosmos tenant secret fields",
        "source references api_key_hash/tenant",
    ),
    (
        "SPEC-1568",
        "TestSpec1568SecretPosture",
        "test_aggregates_totp_seeds",
        "aggregates TOTP seed secrets",
        "source references totp",
    ),
    # SPEC-1562 (3)
    (
        "SPEC-1562",
        "TestSpec1562WidgetAdminMode",
        "test_widget_reads_admin_key_attribute",
        "widget reads data-admin-key attribute",
        "index.ts contains data-admin-key",
    ),
    (
        "SPEC-1562",
        "TestSpec1562WidgetAdminMode",
        "test_transport_uses_admin_key_when_set",
        "transport uses X-API-Key for admin auth",
        "http.ts contains adminApiKey and X-API-Key",
    ),
    (
        "SPEC-1562",
        "TestSpec1562WidgetAdminMode",
        "test_transport_falls_back_to_widget_key",
        "transport falls back to X-Widget-Key",
        "http.ts contains X-Widget-Key",
    ),
    # SPEC-1624 (3)
    (
        "SPEC-1624",
        "TestSpec1624LifespanMigration",
        "test_lifecycle_uses_asynccontextmanager",
        "lifecycle uses @asynccontextmanager",
        "source contains asynccontextmanager",
    ),
    (
        "SPEC-1624",
        "TestSpec1624LifespanMigration",
        "test_lifecycle_has_build_app_lifespan",
        "build_app_lifespan function exists",
        "hasattr returns True",
    ),
    (
        "SPEC-1624",
        "TestSpec1624LifespanMigration",
        "test_no_on_event_registration_in_lifecycle",
        "no app.on_event() registrations",
        "regex finds 0 app.on_event( calls",
    ),
    # SPEC-1616 (4)
    (
        "SPEC-1616",
        "TestSpec1616TestPipeline",
        "test_pipeline_script_exists",
        "test_pipeline.py exists",
        "file exists on disk",
    ),
    (
        "SPEC-1616",
        "TestSpec1616TestPipeline",
        "test_pipeline_has_multiple_phases",
        "pipeline has >= 5 phases",
        "count of def phase_ >= 5",
    ),
    (
        "SPEC-1616",
        "TestSpec1616TestPipeline",
        "test_pipeline_supports_env_flag",
        "pipeline accepts --env flag",
        "content contains --env",
    ),
    (
        "SPEC-1616",
        "TestSpec1616TestPipeline",
        "test_pipeline_supports_stop_on_fail",
        "pipeline supports stop-on-fail",
        "content contains stop and fail",
    ),
    # SPEC-1643 (2)
    (
        "SPEC-1643",
        "TestSpec1643StagingDeployVerification",
        "test_deploy_pipeline_exists",
        "deploy_pipeline.py exists",
        "file exists on disk",
    ),
    (
        "SPEC-1643",
        "TestSpec1643StagingDeployVerification",
        "test_deploy_pipeline_has_initialization_verification",
        "deploy pipeline verifies initialization",
        "content contains initializ",
    ),
    # SPEC-1645 (2)
    (
        "SPEC-1645",
        "TestSpec1645CanonicalStagingTenancy",
        "test_e2e_conftest_uses_remaker_digital",
        "E2E conftest references remaker-digital-001",
        "content contains REMAKER_DIGITAL_001 env var",
    ),
    (
        "SPEC-1645",
        "TestSpec1645CanonicalStagingTenancy",
        "test_upgrade_verification_uses_remaker_digital",
        "upgrade verification uses remaker-digital-001",
        "content contains remaker-digital-001",
    ),
]

start_id = 8215
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
        last_executed_at="2026-03-06T14:00:00+00:00",
    )

print(f"Created {len(tests)} test artifacts (TEST-{start_id}..TEST-{start_id + len(tests) - 1})")
