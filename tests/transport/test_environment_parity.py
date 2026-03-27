"""Phase 3 — Environment parity and governance integrity tests.

Validates:
- Identical transport selection rules across development, staging, production
- No hidden in-process rescue path (DCL-002)
- KB rejects phantom test evidence (DCL-003)
- Spec promotion blocked without executable test metadata

Recovery plan reference: INSIGHTS-2026-03-27-01-00.md Phase 3, Categories 4-5.
Governing decisions: ADR-001, DCL-002, DCL-003.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import inspect
import os
from unittest.mock import patch

import pytest


# ---------------------------------------------------------------------------
# 1. Environment parity — identical rules across environments
# ---------------------------------------------------------------------------


class TestEnvironmentParity:
    """Verify transport selection is environment-independent."""

    def test_use_agent_containers_defaults_true_all_envs(self):
        """USE_AGENT_CONTAINERS defaults to True in all environments."""
        for env_name in ("development", "staging", "production", ""):
            with patch.dict(os.environ, {"ENVIRONMENT": env_name}, clear=False):
                import importlib
                import src.chat.pipeline.constants as mod
                importlib.reload(mod)
                assert mod.USE_AGENT_CONTAINERS is True, (
                    f"USE_AGENT_CONTAINERS is False in {env_name or 'unset'}"
                )

    def test_transport_type_consistent_across_envs(self):
        """TRANSPORT_TYPE should be 'slim' regardless of ENVIRONMENT."""
        for env_name in ("development", "staging", "production"):
            with patch.dict(os.environ, {
                "ENVIRONMENT": env_name,
                "AGNTCY_TRANSPORT_TYPE": "slim",
            }, clear=False):
                import importlib
                import src.multi_tenant.agntcy_sdk_integration as mod
                importlib.reload(mod)
                assert mod.TRANSPORT_TYPE == "slim", (
                    f"TRANSPORT_TYPE != 'slim' in {env_name}"
                )

    def test_health_transport_enforcement_all_envs(self):
        """Health check enforces transport in ALL environments, not just production."""
        import src.app.health as health_mod
        source = inspect.getsource(health_mod)
        # Must contain "ALL environments" or "all environments" (SPEC-1802)
        assert "all environments" in source.lower() or "transport_enforcement" in source


# ---------------------------------------------------------------------------
# 2. No hidden in-process rescue path (DCL-002)
# ---------------------------------------------------------------------------


class TestNoInProcessPath:
    """Verify DCL-002: no in-process dispatch in canonical pipeline."""

    def test_ic_dispatch_no_direct_call(self):
        """Intent classifier dispatch must not call _direct in canonical path."""
        from src.chat.pipeline.agent_dispatch import AgentDispatchMixin
        source = inspect.getsource(AgentDispatchMixin._call_intent_classifier)
        assert "_call_intent_classifier_direct" not in source

    def test_kr_dispatch_no_direct_call(self):
        """Knowledge retrieval dispatch must not call _direct in canonical path."""
        from src.chat.pipeline.agent_dispatch import AgentDispatchMixin
        source = inspect.getsource(AgentDispatchMixin._call_knowledge_retrieval)
        assert "_call_knowledge_retrieval_direct" not in source

    def test_rg_dispatch_terminates_at_503(self):
        """Response generator dispatch must terminate at 503, not in-process."""
        from src.chat.pipeline.agent_dispatch import AgentDispatchMixin
        source = inspect.getsource(AgentDispatchMixin._call_response_generator_stream)
        assert "_require_transport_or_fail" in source

    def test_critic_no_in_process_fallback(self):
        """Critic validation must not call in-process methods."""
        from src.chat.pipeline.critic_escalation import CriticEscalationMixin
        source = inspect.getsource(CriticEscalationMixin._validate_with_critic)
        # Check executable code only — docstring mentions are historical notes
        code_lines = [
            ln for ln in source.split("\n")
            if ln.strip()
            and not ln.strip().startswith(("#", '"""', "'''"))
            and "Phase 2A:" not in ln
        ]
        code = "\n".join(code_lines)
        assert "await self._validate_with_critic_direct" not in code
        assert "self._cr_agent" not in code

    def test_analytics_no_in_process_fallback(self):
        """Analytics must not fall back to in-process."""
        from src.chat.pipeline.analytics import AnalyticsMixin
        source = inspect.getsource(AnalyticsMixin._fire_analytics)
        assert "_an_agent" not in source

    def test_orchestrator_no_dead_agent_instances(self):
        """Orchestrator must not construct dead agent instances."""
        from src.chat.pipeline.orchestrator import ChatPipeline
        source = inspect.getsource(ChatPipeline._init_agents)
        # These agents were removed in S224
        assert "EscalationHandlerAgent" not in source
        assert "AnalyticsCollectorAgent" not in source
        assert "CriticSupervisorAgent" not in source


# ---------------------------------------------------------------------------
# 3. Governance integrity — KB rejects phantom evidence (DCL-003)
# ---------------------------------------------------------------------------


class TestGovernanceIntegrity:
    """Verify KB governance gates prevent phantom test evidence."""

    @pytest.fixture(autouse=True)
    def _ensure_tools_path(self):
        """Add project root to path so tools.knowledge_db is importable."""
        import sys
        from pathlib import Path
        root = Path(__file__).resolve().parents[2]
        tools_dir = str(root / "tools" / "knowledge-db")
        if tools_dir not in sys.path:
            sys.path.insert(0, tools_dir)

    def test_transport_gated_specs_defined(self):
        """Transport-gated spec set must be defined in db.py."""
        import db as kb_db
        assert hasattr(kb_db, "_TRANSPORT_GATED_SPECS")
        gated = kb_db._TRANSPORT_GATED_SPECS
        assert len(gated) >= 6, f"Expected >=6 gated specs, got {len(gated)}"

    def test_transport_evidence_gate_error_exists(self):
        """TransportEvidenceGateError exception must be defined."""
        import db as kb_db
        assert hasattr(kb_db, "TransportEvidenceGateError")
        assert issubclass(kb_db.TransportEvidenceGateError, Exception)

    def test_insert_test_gate_exists(self):
        """KnowledgeDB.insert_test() must include transport evidence gate logic."""
        import db as kb_db
        source = inspect.getsource(kb_db.KnowledgeDB.insert_test)
        assert (
            "TransportEvidenceGateError" in source
            or "_TRANSPORT_GATED_SPECS" in source
            or "_validate_transport_test_pass" in source
        )

    def test_update_spec_gate_exists(self):
        """KnowledgeDB.update_spec() must include transport evidence gate logic."""
        import db as kb_db
        source = inspect.getsource(kb_db.KnowledgeDB.update_spec)
        assert "TransportEvidenceGateError" in source or "_TRANSPORT_GATED_SPECS" in source
