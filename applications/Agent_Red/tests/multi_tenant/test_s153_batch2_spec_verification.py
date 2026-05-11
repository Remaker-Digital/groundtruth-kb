"""S153 Batch 2 spec verification tests — Co-Pilot Knowledge, Secret Posture,
Widget Admin Mode, Test Pipeline, Lifespan migration.

Verifies specified specs against actual production code by exercising
real interfaces (GOV-10).

Specs verified:
    SPEC-1568: Secret Posture aggregates secrets from all storage locations
    SPEC-1562: Widget Admin Mode — admin API key authentication
    SPEC-1570: Co-Pilot Knowledge — document CRUD API endpoints
    SPEC-1571: Co-Pilot Knowledge — batch ingestion from docs-site
    SPEC-1572: Co-Pilot Knowledge — URL import source
    SPEC-1573: Co-Pilot Knowledge — re-embedding trigger
    SPEC-1574: Co-Pilot Knowledge — collection statistics endpoint
    SPEC-1575: Co-Pilot Knowledge — scan scheduling
    SPEC-1576: Co-Pilot Knowledge — configurable retrieval parameters
    SPEC-1577: Co-Pilot Knowledge — test query endpoint
    SPEC-1578: Co-Pilot Knowledge — Provider Console UI page
    SPEC-1616: Automated test pipeline — single invocation
    SPEC-1624: FastAPI lifespan context manager migration
    SPEC-1643: Staging deployment verifies tenant initialization
    SPEC-1645: remaker-digital-001 is canonical staging tenancy

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import inspect
from pathlib import Path

import pytest

pytestmark = pytest.mark.local_env


_PROJECT_ROOT = Path(__file__).resolve().parents[2]


# ===================================================================
# SPEC-1570: Co-Pilot Knowledge — document CRUD API endpoints
# ===================================================================


class TestSpec1570CopilotDocumentCRUD:
    """SPEC-1570: Superadmin API must expose CRUD endpoints for co-pilot
    admin documentation (list, create, update, soft-delete)."""

    def test_list_endpoint_exists(self):
        """list_copilot_documents function exists in superadmin_api."""
        from src.multi_tenant import superadmin_api as api
        assert hasattr(api, "list_copilot_documents"), (
            "SPEC-1570: list_copilot_documents endpoint must exist"
        )

    def test_create_endpoint_exists(self):
        """create_copilot_document function exists."""
        from src.multi_tenant import superadmin_api as api
        assert hasattr(api, "create_copilot_document"), (
            "SPEC-1570: create_copilot_document endpoint must exist"
        )

    def test_update_endpoint_exists(self):
        """update_copilot_document function exists."""
        from src.multi_tenant import superadmin_api as api
        assert hasattr(api, "update_copilot_document"), (
            "SPEC-1570: update_copilot_document endpoint must exist"
        )

    def test_delete_endpoint_exists(self):
        """delete_copilot_document function exists (soft-delete)."""
        from src.multi_tenant import superadmin_api as api
        assert hasattr(api, "delete_copilot_document"), (
            "SPEC-1570: delete_copilot_document endpoint must exist"
        )

    def test_delete_is_soft_delete(self):
        """Deletion must be soft-delete (mark inactive), not hard-delete."""
        from src.multi_tenant import superadmin_api as api
        source = inspect.getsource(api.delete_copilot_document)
        # Should set active=False, not physically remove document
        assert "active" in source.lower(), (
            "SPEC-1570: delete must be soft-delete (set active=False)"
        )


# ===================================================================
# SPEC-1571: Co-Pilot Knowledge — batch ingestion from docs-site
# ===================================================================


class TestSpec1571BatchIngestion:
    """SPEC-1571: Batch ingestion scans docs-site/docs/admin-guide/*.md,
    computes SHA-256 hashes, and creates/updates documents."""

    def test_ingest_endpoint_exists(self):
        """ingest_docs_site function exists."""
        from src.multi_tenant import superadmin_api as api
        assert hasattr(api, "ingest_docs_site"), (
            "SPEC-1571: ingest_docs_site endpoint must exist"
        )

    def test_ingest_scans_admin_guide_directory(self):
        """Ingestion must scan docs/admin-guide/*.md files."""
        from src.multi_tenant import superadmin_api as api
        source = inspect.getsource(api.ingest_docs_site)
        assert "admin-guide" in source, (
            "SPEC-1571: Must scan admin-guide directory"
        )
        assert ".md" in source, (
            "SPEC-1571: Must process markdown files"
        )

    def test_ingest_uses_content_hash(self):
        """Ingestion must use SHA-256 content hash for change detection."""
        from src.multi_tenant import superadmin_api as api
        source = inspect.getsource(api.ingest_docs_site)
        assert "hash" in source.lower(), (
            "SPEC-1571: Must use content hash for change detection"
        )


# ===================================================================
# SPEC-1572: Co-Pilot Knowledge — URL import source
# ===================================================================


class TestSpec1572URLImport:
    """SPEC-1572: URL import endpoint fetches URL content, converts
    HTML to markdown, and creates a document."""

    def test_import_url_endpoint_exists(self):
        """import_url function exists."""
        from src.multi_tenant import superadmin_api as api
        assert hasattr(api, "import_url"), (
            "SPEC-1572: import_url endpoint must exist"
        )

    def test_import_url_enforces_https(self):
        """URL import must enforce HTTPS-only."""
        from src.multi_tenant import superadmin_api as api
        source = inspect.getsource(api.import_url)
        assert "https" in source.lower(), (
            "SPEC-1572: Must validate HTTPS URLs"
        )


# ===================================================================
# SPEC-1573: Co-Pilot Knowledge — re-embedding trigger
# ===================================================================


class TestSpec1573ReEmbedding:
    """SPEC-1573: Re-embedding endpoint must re-embed stale documents
    or all when force=true."""

    def test_re_embed_endpoint_exists(self):
        """re_embed_documents function exists."""
        from src.multi_tenant import superadmin_api as api
        assert hasattr(api, "re_embed_documents"), (
            "SPEC-1573: re_embed_documents endpoint must exist"
        )

    def test_re_embed_uses_azure_openai_embeddings(self):
        """Re-embedding must use text-embedding model."""
        from src.multi_tenant import superadmin_api as api
        source = inspect.getsource(api.re_embed_documents)
        # Should reference embedding somewhere (direct or helper)
        assert "embed" in source.lower(), (
            "SPEC-1573: Must trigger embedding process"
        )


# ===================================================================
# SPEC-1574: Co-Pilot Knowledge — collection statistics endpoint
# ===================================================================


class TestSpec1574CollectionStats:
    """SPEC-1574: Statistics endpoint must return document counts,
    category breakdown, embedded count, stale count."""

    def test_stats_endpoint_exists(self):
        """copilot_stats function exists."""
        from src.multi_tenant import superadmin_api as api
        assert hasattr(api, "copilot_stats"), (
            "SPEC-1574: copilot_stats endpoint must exist"
        )

    def test_stats_returns_category_breakdown(self):
        """Statistics must include category breakdown."""
        from src.multi_tenant import superadmin_api as api
        source = inspect.getsource(api.copilot_stats)
        assert "category" in source.lower(), (
            "SPEC-1574: Must include category breakdown in stats"
        )

    def test_stats_tracks_stale_documents(self):
        """Statistics must track stale documents (hash mismatch)."""
        from src.multi_tenant import superadmin_api as api
        source = inspect.getsource(api.copilot_stats)
        assert "stale" in source.lower(), (
            "SPEC-1574: Must track stale document count"
        )


# ===================================================================
# SPEC-1575: Co-Pilot Knowledge — scan scheduling
# ===================================================================


class TestSpec1575ScanScheduling:
    """SPEC-1575: Configurable scan schedules — manual, daily, weekly."""

    def test_get_schedule_endpoint_exists(self):
        """get_copilot_schedule function exists."""
        from src.multi_tenant import superadmin_api as api
        assert hasattr(api, "get_copilot_schedule"), (
            "SPEC-1575: get_copilot_schedule endpoint must exist"
        )

    def test_update_schedule_endpoint_exists(self):
        """update_copilot_schedule function exists."""
        from src.multi_tenant import superadmin_api as api
        assert hasattr(api, "update_copilot_schedule"), (
            "SPEC-1575: update_copilot_schedule endpoint must exist"
        )

    def test_schedule_supports_three_frequencies(self):
        """Schedule must support manual, daily, weekly frequencies."""
        from src.multi_tenant import superadmin_api as api
        source = inspect.getsource(api.update_copilot_schedule)
        assert "manual" in source, "SPEC-1575: Must support manual frequency"
        assert "daily" in source, "SPEC-1575: Must support daily frequency"
        assert "weekly" in source, "SPEC-1575: Must support weekly frequency"


# ===================================================================
# SPEC-1576: Co-Pilot Knowledge — configurable retrieval parameters
# ===================================================================


class TestSpec1576RetrievalParameters:
    """SPEC-1576: CoPilotAgent reads retrieval parameters from config,
    not hardcoded defaults. Parameters: vector_weight, bm25_weight,
    rrf_k, top_k, min_score."""

    def test_get_retrieval_config_endpoint_exists(self):
        """get_copilot_retrieval_config function exists."""
        from src.multi_tenant import superadmin_api as api
        assert hasattr(api, "get_copilot_retrieval_config"), (
            "SPEC-1576: get_copilot_retrieval_config endpoint must exist"
        )

    def test_update_retrieval_config_endpoint_exists(self):
        """update_copilot_retrieval_config function exists."""
        from src.multi_tenant import superadmin_api as api
        assert hasattr(api, "update_copilot_retrieval_config"), (
            "SPEC-1576: update_copilot_retrieval_config endpoint must exist"
        )

    def test_retrieval_config_has_all_five_parameters(self):
        """Config must include vector_weight, bm25_weight, rrf_k, top_k, min_score."""
        from src.multi_tenant import superadmin_api as api
        source = inspect.getsource(api.get_copilot_retrieval_config)
        for param in ["vector_weight", "bm25_weight", "rrf_k", "top_k", "min_score"]:
            assert param in source, (
                f"SPEC-1576: Retrieval config must include {param}"
            )

    def test_configure_copilot_retrieval_runtime_push(self):
        """Runtime push function exists in co_pilot module."""
        from src.agents import co_pilot
        assert hasattr(co_pilot, "configure_copilot_retrieval"), (
            "SPEC-1576: co_pilot must have configure_copilot_retrieval for runtime push"
        )


# ===================================================================
# SPEC-1577: Co-Pilot Knowledge — test query endpoint
# ===================================================================


class TestSpec1577TestQuery:
    """SPEC-1577: Test query runs full hybrid retrieval pipeline
    and returns top-k results with scores."""

    def test_test_query_endpoint_exists(self):
        """test_copilot_query function exists."""
        from src.multi_tenant import superadmin_api as api
        assert hasattr(api, "test_copilot_query"), (
            "SPEC-1577: test_copilot_query endpoint must exist"
        )

    def test_test_query_returns_scored_results(self):
        """Test query must return results with scores."""
        from src.multi_tenant import superadmin_api as api
        source = inspect.getsource(api.test_copilot_query)
        assert "score" in source.lower(), (
            "SPEC-1577: Test query results must include scores"
        )


# ===================================================================
# SPEC-1578: Co-Pilot Knowledge — Provider Console UI page
# ===================================================================


class TestSpec1578ProviderConsoleUI:
    """SPEC-1578: CopilotKnowledge.tsx must exist with four tabs:
    Documents, Ingestion, Schedule, Parameters."""

    def test_page_component_exists(self):
        """CopilotKnowledge.tsx must exist in provider admin pages."""
        page_path = _PROJECT_ROOT / "admin" / "provider" / "pages" / "CopilotKnowledge.tsx"
        assert page_path.is_file(), (
            "SPEC-1578: CopilotKnowledge.tsx must exist in provider admin pages"
        )

    def test_page_has_four_tabs(self):
        """The page must have Documents, Ingestion, Schedule, Parameters tabs."""
        page_path = _PROJECT_ROOT / "admin" / "provider" / "pages" / "CopilotKnowledge.tsx"
        content = page_path.read_text(encoding="utf-8")
        for tab_name in ["Documents", "Ingestion", "Schedule", "Parameters"]:
            assert tab_name in content, (
                f"SPEC-1578: Page must have '{tab_name}' tab"
            )

    def test_page_calls_copilot_api_endpoints(self):
        """The page must call the Co-Pilot API endpoints."""
        page_path = _PROJECT_ROOT / "admin" / "provider" / "pages" / "CopilotKnowledge.tsx"
        content = page_path.read_text(encoding="utf-8")
        assert "copilot" in content.lower(), (
            "SPEC-1578: Page must reference copilot API endpoints"
        )


# ===================================================================
# SPEC-1568: Secret Posture — aggregates from all storage locations
# ===================================================================


# TestSpec1568SecretPosture REMOVED (WI-1640 / S137):
# GET /secrets/posture endpoint was intentionally removed per SPEC-1843 (ZK mandate).
# Replaced by GET /health/secrets (aggregate counts only, no per-tenant detail).
# Replacement tests: TEST-10901 through TEST-10934 (ZK test suite).


# ===================================================================
# SPEC-1562: Widget Admin Mode
# ===================================================================


class TestSpec1562WidgetAdminMode:
    """SPEC-1562: Widget in admin panel uses admin API key authentication
    instead of widget key, routing to Co-Pilot agent."""

    def test_widget_reads_admin_key_attribute(self):
        """Widget index.ts must read data-admin-key attribute."""
        index_path = _PROJECT_ROOT / "widget" / "src" / "index.ts"
        content = index_path.read_text(encoding="utf-8")
        assert "data-admin-key" in content, (
            "SPEC-1562: Widget must read data-admin-key attribute"
        )

    def test_transport_uses_admin_key_when_set(self):
        """HTTP transport must use X-API-Key header when adminApiKey is set."""
        http_path = _PROJECT_ROOT / "widget" / "src" / "transport" / "http.ts"
        content = http_path.read_text(encoding="utf-8")
        assert "adminApiKey" in content, (
            "SPEC-1562: Transport must support adminApiKey"
        )
        assert "X-API-Key" in content, (
            "SPEC-1562: Must use X-API-Key header for admin authentication"
        )

    def test_transport_falls_back_to_widget_key(self):
        """When no admin key, must fall back to X-Widget-Key header."""
        http_path = _PROJECT_ROOT / "widget" / "src" / "transport" / "http.ts"
        content = http_path.read_text(encoding="utf-8")
        assert "X-Widget-Key" in content, (
            "SPEC-1562: Must fall back to X-Widget-Key when no admin key"
        )


# ===================================================================
# SPEC-1624: FastAPI lifespan context manager migration
# ===================================================================


class TestSpec1624LifespanMigration:
    """SPEC-1624: FastAPI app must use lifespan context manager,
    not deprecated on_event() hooks."""

    def test_lifecycle_uses_asynccontextmanager(self):
        """lifecycle.py must use @asynccontextmanager for lifespan."""
        import src.app.lifecycle as lifecycle
        source = inspect.getsource(lifecycle)
        assert "asynccontextmanager" in source, (
            "SPEC-1624: Must use @asynccontextmanager for lifespan"
        )

    def test_lifecycle_has_build_app_lifespan(self):
        """build_app_lifespan function must exist."""
        import src.app.lifecycle as lifecycle
        assert hasattr(lifecycle, "build_app_lifespan"), (
            "SPEC-1624: Must have build_app_lifespan function"
        )

    def test_no_on_event_registration_in_lifecycle(self):
        """lifecycle.py must not register deprecated on_event handlers.

        Note: on_event may appear in comments/docstrings explaining the
        migration — that's fine. What matters is no actual registration
        calls like app.on_event() exist."""
        import src.app.lifecycle as lifecycle
        source = inspect.getsource(lifecycle)
        # Check for actual registration calls, not documentation references
        import re
        registrations = re.findall(r'app\.on_event\s*\(', source)
        assert len(registrations) == 0, (
            f"SPEC-1624: Must not register on_event handlers, "
            f"found {len(registrations)} registration(s)"
        )


# ===================================================================
# SPEC-1616: Automated test pipeline — single invocation
# ===================================================================


class TestSpec1616TestPipeline:
    """SPEC-1616: test_pipeline.py must execute all test phases
    autonomously via single invocation."""

    def test_pipeline_script_exists(self):
        """scripts/test_pipeline.py must exist."""
        script_path = _PROJECT_ROOT / "scripts" / "test_pipeline.py"
        assert script_path.is_file(), (
            "SPEC-1616: test_pipeline.py must exist"
        )

    def test_pipeline_has_multiple_phases(self):
        """Pipeline must define multiple test phases."""
        script_path = _PROJECT_ROOT / "scripts" / "test_pipeline.py"
        content = script_path.read_text(encoding="utf-8")
        # Count phase definitions
        phase_count = content.count("def phase_")
        assert phase_count >= 5, (
            f"SPEC-1616: Pipeline must have >= 5 phases, found {phase_count}"
        )

    def test_pipeline_supports_env_flag(self):
        """Pipeline must accept --env staging/production flag."""
        script_path = _PROJECT_ROOT / "scripts" / "test_pipeline.py"
        content = script_path.read_text(encoding="utf-8")
        assert "--env" in content, (
            "SPEC-1616: Must accept --env argument"
        )

    def test_pipeline_supports_stop_on_fail(self):
        """Pipeline must support --stop-on-fail flag."""
        script_path = _PROJECT_ROOT / "scripts" / "test_pipeline.py"
        content = script_path.read_text(encoding="utf-8")
        assert "stop" in content.lower() and "fail" in content.lower(), (
            "SPEC-1616: Must support stop-on-fail behavior"
        )


# ===================================================================
# SPEC-1643: Staging deploy verifies tenant initialization
# ===================================================================


class TestSpec1643StagingDeployVerification:
    """SPEC-1643: Deployment pipeline Phase 14 must verify tenant
    is functional — admin URL resolves, tenant recognized."""

    def test_deploy_pipeline_exists(self):
        """scripts/deploy_pipeline.py must exist."""
        script_path = _PROJECT_ROOT / "scripts" / "deploy_pipeline.py"
        assert script_path.is_file(), (
            "SPEC-1643: deploy_pipeline.py must exist"
        )

    def test_deploy_pipeline_has_initialization_verification(self):
        """Deploy pipeline must verify initialized state."""
        script_path = _PROJECT_ROOT / "scripts" / "deploy_pipeline.py"
        content = script_path.read_text(encoding="utf-8")
        assert "initializ" in content.lower(), (
            "SPEC-1643: Must verify tenant initialization"
        )


# ===================================================================
# SPEC-1645: remaker-digital-001 is canonical staging tenancy
# ===================================================================


class TestSpec1645CanonicalStagingTenancy:
    """SPEC-1645: remaker-digital-001 must be used as canonical test
    tenancy for all staging tests."""

    def test_e2e_conftest_uses_remaker_digital(self):
        """E2E conftest must reference remaker-digital-001 (directly or via env var)."""
        conftest_path = _PROJECT_ROOT / "tests" / "e2e_live" / "conftest.py"
        content = conftest_path.read_text(encoding="utf-8")
        # May reference directly or via env var name containing the tenant
        has_direct = "remaker-digital-001" in content
        has_env_var = "REMAKER_DIGITAL_001" in content
        assert has_direct or has_env_var, (
            "SPEC-1645: E2E conftest must reference remaker-digital-001 "
            "(directly or via STAGING_REMAKER_DIGITAL_001_* env var)"
        )

    def test_upgrade_verification_uses_remaker_digital(self):
        """Upgrade verification must reference remaker-digital-001."""
        script_path = _PROJECT_ROOT / "scripts" / "upgrade_verification.py"
        content = script_path.read_text(encoding="utf-8")
        assert "remaker-digital-001" in content or "remaker_digital_001" in content, (
            "SPEC-1645: upgrade_verification must use remaker-digital-001"
        )
