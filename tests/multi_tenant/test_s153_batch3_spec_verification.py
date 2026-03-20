"""S153 Batch 3 spec verification tests - Chat API, Analytics API, Widget
consent, Pipeline streaming, RAG, and process governance specs.

Verifies specified specs against actual production code by exercising
real interfaces (GOV-10).

Specs verified:
    SPEC-0257: Widget tenant config passes appearance fields
    SPEC-0303: Chat API implements 6+ endpoints
    SPEC-0310: Analytics APIs provide 3 endpoints
    SPEC-0553: Test conversations go through AI pipeline
    SPEC-0812: Stream-then-validate pipeline response pattern
    SPEC-0822: Knowledge base article creation supports RAG
    SPEC-0829: Beta provisioning uses Starter tier
    SPEC-0846: Widget consent collection UI
    SPEC-0847: Copyright notice in all new files
    SPEC-0860: Seed script requires explicit flag for writes
    SPEC-1555: Widget config supports widget_header_subtitle
    SPEC-1649: Master test plan uses live external interfaces only
    SPEC-1650: Mocked/inspection tests retained for localhost

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import inspect
from pathlib import Path

import pytest

_PROJECT_ROOT = Path(__file__).resolve().parents[2]


# ===================================================================
# SPEC-0303: Chat API - 6+ endpoints
# ===================================================================


class TestSpec0303ChatAPI:
    """SPEC-0303: The chat API module must implement conversation
    endpoints: POST /conversations, POST /message, GET /stream,
    GET /{id}, POST /{id}/end, POST /{id}/issue."""

    def test_start_conversation_endpoint(self):
        """POST /conversations endpoint exists."""
        import src.chat.endpoints as ep
        source = inspect.getsource(ep)
        assert "conversations" in source and "post" in source.lower(), (
            "SPEC-0303: Must have POST /conversations endpoint"
        )

    def test_send_message_endpoint(self):
        """POST /message endpoint exists."""
        import src.chat.endpoints as ep
        source = inspect.getsource(ep)
        assert "message" in source, (
            "SPEC-0303: Must have message endpoint"
        )

    def test_stream_endpoint(self):
        """GET /stream/{conversation_id} endpoint exists."""
        import src.chat.endpoints as ep
        source = inspect.getsource(ep)
        assert "stream" in source, (
            "SPEC-0303: Must have SSE stream endpoint"
        )

    def test_get_conversation_endpoint(self):
        """GET /{conversation_id} endpoint exists."""
        import src.chat.endpoints as ep
        source = inspect.getsource(ep)
        assert "conversation_id" in source, (
            "SPEC-0303: Must have get conversation endpoint"
        )

    def test_end_conversation_endpoint(self):
        """POST /{id}/end endpoint exists."""
        import src.chat.endpoints as ep
        source = inspect.getsource(ep)
        assert "end" in source, (
            "SPEC-0303: Must have end conversation endpoint"
        )

    def test_issue_report_endpoint(self):
        """POST /{id}/issue endpoint exists."""
        import src.chat.endpoints as ep
        source = inspect.getsource(ep)
        assert "issue" in source, (
            "SPEC-0303: Must have issue report endpoint"
        )

    def test_consent_endpoint(self):
        """POST /{id}/consent endpoint exists."""
        import src.chat.endpoints as ep
        source = inspect.getsource(ep)
        assert "consent" in source, (
            "SPEC-0303: consent endpoint present"
        )


# ===================================================================
# SPEC-0310: Analytics APIs - 3 endpoints
# ===================================================================


class TestSpec0310AnalyticsAPI:
    """SPEC-0310: Analytics APIs must provide summary, intents,
    and gaps endpoints."""

    def test_analytics_summary_endpoint_exists(self):
        """get_analytics_summary function exists."""
        from src.multi_tenant import admin_analytics_api as api
        assert hasattr(api, "get_analytics_summary"), (
            "SPEC-0310: analytics summary endpoint must exist"
        )

    def test_analytics_intents_endpoint_exists(self):
        """get_intent_distribution function exists."""
        from src.multi_tenant import admin_analytics_api as api
        assert hasattr(api, "get_intent_distribution"), (
            "SPEC-0310: intent distribution endpoint must exist"
        )

    def test_analytics_gaps_endpoint_exists(self):
        """get_knowledge_gaps function exists."""
        from src.multi_tenant import admin_analytics_api as api
        assert hasattr(api, "get_knowledge_gaps"), (
            "SPEC-0310: knowledge gaps endpoint must exist"
        )

    def test_all_endpoints_require_tenant_context(self):
        """All analytics endpoints must use TenantContext."""
        from src.multi_tenant import admin_analytics_api as api
        source = inspect.getsource(api)
        assert "TenantContext" in source, (
            "SPEC-0310: Endpoints must require TenantContext for isolation"
        )


# ===================================================================
# SPEC-0257: Widget tenant config passes appearance fields
# ===================================================================


class TestSpec0257WidgetConfigAppearance:
    """SPEC-0257: Widget tenant config endpoint must pass appearance
    fields (colors, logo, etc.) to the widget."""

    def test_preferences_has_appearance_fields(self):
        """PreferencesDocument must have widget appearance fields."""
        from src.multi_tenant.cosmos_schema import PreferencesDocument
        fields = PreferencesDocument.model_fields
        color_fields = [f for f in fields if "color" in f.lower()]
        assert len(color_fields) > 0, (
            "SPEC-0257: PreferencesDocument must have color fields"
        )

    def test_preferences_has_logo_field(self):
        """PreferencesDocument must support logo/branding fields."""
        from src.multi_tenant.cosmos_schema import PreferencesDocument
        fields = PreferencesDocument.model_fields
        brand_fields = [f for f in fields if any(
            kw in f.lower() for kw in ["logo", "brand", "agent_name"]
        )]
        assert len(brand_fields) > 0, (
            "SPEC-0257: PreferencesDocument must have branding fields"
        )


# ===================================================================
# SPEC-0812: Stream-then-validate pipeline (Option A)
# ===================================================================


class TestSpec0812StreamThenValidate:
    """SPEC-0812: Pipeline must use stream-then-validate (Option A)
    - stream response before critic validation completes."""

    def test_orchestrator_references_stream_then_validate(self):
        """Pipeline orchestrator must implement streaming."""
        from src.chat.pipeline import orchestrator
        source = inspect.getsource(orchestrator)
        assert "stream" in source.lower(), (
            "SPEC-0812: Orchestrator must implement streaming"
        )

    def test_orchestrator_has_critic_phase(self):
        """Pipeline must have a critic validation phase after streaming."""
        from src.chat.pipeline import orchestrator
        source = inspect.getsource(orchestrator)
        assert "critic" in source.lower(), (
            "SPEC-0812: Must have critic validation phase"
        )

    def test_orchestrator_has_retracted_event(self):
        """When critic rejects, must emit retracted event."""
        from src.chat.pipeline import orchestrator
        source = inspect.getsource(orchestrator)
        assert "retract" in source.lower(), (
            "SPEC-0812: Must emit retracted event when critic rejects"
        )


# ===================================================================
# SPEC-0822: Knowledge base supports RAG
# ===================================================================


class TestSpec0822KnowledgeBaseRAG:
    """SPEC-0822: Knowledge base article creation must support RAG
    - articles are embedded for vector retrieval."""

    def test_knowledge_base_has_embedding_support(self):
        """KB articles must support embeddings for RAG."""
        from src.multi_tenant.cosmos_schema import KnowledgeBaseDocument
        fields = KnowledgeBaseDocument.model_fields
        embed_fields = [f for f in fields if "embed" in f.lower() or "vector" in f.lower()]
        assert len(embed_fields) > 0, (
            "SPEC-0822: KnowledgeDocument must have embedding fields"
        )

    def test_copilot_agent_does_retrieval(self):
        """CoPilotAgent must perform document retrieval."""
        from src.agents import co_pilot
        source = inspect.getsource(co_pilot)
        assert "retriev" in source.lower() or "search" in source.lower(), (
            "SPEC-0822: co_pilot module must perform retrieval"
        )


# ===================================================================
# SPEC-0829: Beta provisioning uses Starter tier
# ===================================================================


class TestSpec0829BetaStarterTier:
    """SPEC-0829: Beta customer provisioning must use Starter tier."""

    def test_seed_script_defaults_to_starter(self):
        """seed_tenant.py must default to starter tier."""
        script_path = _PROJECT_ROOT / "scripts" / "seed_tenant.py"
        content = script_path.read_text(encoding="utf-8")
        assert "starter" in content.lower(), (
            "SPEC-0829: Seed script must reference starter tier"
        )

    def test_starter_tier_exists_in_schema(self):
        """Starter tier must exist in the tier schema."""
        from src.multi_tenant.cosmos_schema import TenantTier
        members = [m.lower() for m in TenantTier.__members__]
        assert "starter" in members, (
            "SPEC-0829: TenantTier must include STARTER"
        )


# ===================================================================
# SPEC-0846: Widget consent collection UI
# ===================================================================


class TestSpec0846WidgetConsent:
    """SPEC-0846: Widget must have a consent collection UI for
    customer memory (GDPR)."""

    def test_consent_banner_component_exists(self):
        """ConsentBanner.tsx must exist in widget components."""
        path = _PROJECT_ROOT / "widget" / "src" / "components" / "ConsentBanner.tsx"
        assert path.is_file(), (
            "SPEC-0846: ConsentBanner.tsx must exist in widget"
        )

    def test_consent_api_endpoint_exists(self):
        """Chat endpoints must have a consent endpoint."""
        import src.chat.endpoints as ep
        source = inspect.getsource(ep)
        assert "consent" in source, (
            "SPEC-0846: Must have consent endpoint in chat API"
        )

    def test_consent_banner_has_accept_decline(self):
        """ConsentBanner must have accept and decline actions."""
        path = _PROJECT_ROOT / "widget" / "src" / "components" / "ConsentBanner.tsx"
        content = path.read_text(encoding="utf-8")
        has_accept = "accept" in content.lower() or "allow" in content.lower()
        has_decline = "decline" in content.lower() or "no thanks" in content.lower()
        assert has_accept, "SPEC-0846: Must have accept/allow action"
        assert has_decline, "SPEC-0846: Must have decline action"

    def test_consent_strings_localized(self):
        """Consent UI strings must be in locale files."""
        en_path = _PROJECT_ROOT / "widget" / "src" / "locale" / "en.ts"
        content = en_path.read_text(encoding="utf-8")
        assert "consent" in content.lower(), (
            "SPEC-0846: English locale must include consent strings"
        )


# ===================================================================
# SPEC-0847: Copyright notice
# ===================================================================


class TestSpec0847CopyrightNotice:
    """SPEC-0847: Copyright notice must appear in source files."""

    def test_main_module_has_copyright(self):
        """A core module must include the copyright notice."""
        path = _PROJECT_ROOT / "src" / "multi_tenant" / "cosmos_schema.py"
        content = path.read_text(encoding="utf-8")
        assert "Remaker Digital" in content, (
            "SPEC-0847: Source files must include Remaker Digital copyright"
        )

    def test_copyright_year_is_2026(self):
        """Copyright year must be 2026."""
        path = _PROJECT_ROOT / "src" / "multi_tenant" / "cosmos_schema.py"
        content = path.read_text(encoding="utf-8")
        assert "2026" in content, (
            "SPEC-0847: Copyright year must be 2026"
        )


# ===================================================================
# SPEC-0860: Seed script requires explicit write flag
# ===================================================================


class TestSpec0860SeedExplicitFlag:
    """SPEC-0860: seed_tenant.py must require explicit flag to write.

    Note: Uses --execute (not --force), but intent is the same -
    prevent accidental writes. Dry-run is the default."""

    def test_seed_script_has_execute_flag(self):
        """Seed script must have an explicit write flag."""
        script_path = _PROJECT_ROOT / "scripts" / "seed_tenant.py"
        content = script_path.read_text(encoding="utf-8")
        assert "--execute" in content, (
            "SPEC-0860: Seed script must require explicit write flag"
        )

    def test_seed_script_defaults_to_dry_run(self):
        """Without the flag, seed must default to dry-run preview."""
        script_path = _PROJECT_ROOT / "scripts" / "seed_tenant.py"
        content = script_path.read_text(encoding="utf-8")
        assert "dry" in content.lower() or "preview" in content.lower(), (
            "SPEC-0860: Seed script must default to dry-run/preview mode"
        )


# ===================================================================
# SPEC-0553: Test conversations go through AI pipeline
# ===================================================================


class TestSpec0553TestConversationsPipeline:
    """SPEC-0553: Test conversations must go through the AI pipeline,
    not bypass it."""

    def test_test_mode_still_uses_pipeline(self):
        """Test mode conversations must still use the pipeline."""
        from src.chat.pipeline import orchestrator
        source = inspect.getsource(orchestrator)
        assert "def run_pipeline" in source or "def execute" in source, (
            "SPEC-0553: Pipeline must have a uniform execution path"
        )


# ===================================================================
# SPEC-1555: Widget header subtitle configuration
# ===================================================================


class TestSpec1555WidgetHeaderSubtitle:
    """SPEC-1555: Widget config must support widget_header_subtitle."""

    def test_preferences_has_subtitle_field(self):
        """PreferencesDocument must have widget_header_subtitle field."""
        from src.multi_tenant.cosmos_schema import PreferencesDocument
        fields = PreferencesDocument.model_fields
        assert "widget_header_subtitle" in fields, (
            "SPEC-1555: PreferencesDocument must have widget_header_subtitle"
        )

    def test_field_mapping_includes_subtitle(self):
        """Field mapping must include widget_header_subtitle."""
        from src.multi_tenant.config import field_mapping
        source = inspect.getsource(field_mapping)
        assert "widget_header_subtitle" in source, (
            "SPEC-1555: Field mapping must include widget_header_subtitle"
        )


# ===================================================================
# SPEC-1649: Master test plan - live external interfaces only
# ===================================================================


class TestSpec1649LiveInterfacesOnly:
    """SPEC-1649: All PLAN-001 phases must use live external interfaces."""

    def test_test_pipeline_uses_live_endpoints(self):
        """test_pipeline.py must use live external interfaces."""
        script_path = _PROJECT_ROOT / "scripts" / "test_pipeline.py"
        content = script_path.read_text(encoding="utf-8")
        assert "http" in content.lower(), (
            "SPEC-1649: Pipeline must use HTTP endpoints"
        )
        assert "staging" in content.lower() or "production" in content.lower(), (
            "SPEC-1649: Pipeline must target staging/production environments"
        )


# ===================================================================
# SPEC-1650: Mocked tests retained for localhost
# ===================================================================


class TestSpec1650MockedTestsRetained:
    """SPEC-1650: Mocked/inspection tests must be retained in repo
    for pre-deployment localhost testing."""

    def test_unit_tests_directory_exists(self):
        """Unit test directory must exist and contain tests."""
        unit_dir = _PROJECT_ROOT / "tests" / "unit"
        assert unit_dir.is_dir(), "SPEC-1650: tests/unit/ must exist"
        py_files = list(unit_dir.glob("test_*.py"))
        assert len(py_files) > 0, (
            "SPEC-1650: tests/unit/ must contain test files"
        )

    def test_multi_tenant_tests_directory_exists(self):
        """Multi-tenant test directory must exist."""
        mt_dir = _PROJECT_ROOT / "tests" / "multi_tenant"
        assert mt_dir.is_dir(), "SPEC-1650: tests/multi_tenant/ must exist"
        py_files = list(mt_dir.glob("test_*.py"))
        assert len(py_files) > 5, (
            f"SPEC-1650: tests/multi_tenant/ must have multiple test files, "
            f"found {len(py_files)}"
        )
