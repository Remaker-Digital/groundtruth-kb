"""Minimal conftest for scripts tests.

Shields these tests from the project's heavy root conftest by providing a
minimal no-op set of fixtures. No FastAPI, no Cosmos mocks, no tenant wiring.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import json
import os
import sys
import tempfile
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


@pytest.fixture(autouse=True, scope="function")
def mock_harness_registry_for_tests(request) -> None:
    """Mock the harness-registry.json to ensure suspended harnesses are active in tests."""
    module_name = request.module.__name__
    # Skip this mock override for tests that explicitly test harness registry/role/dispatch logic
    if any(
        x in module_name
        for x in [
            "test_check_harness_parity",
            "test_claude_session_start_dispatcher",
            "test_codex_session_start_dispatcher",
            "test_role_set_schema",
            "test_harness_roles",
            "test_harness_projection_reader",
            "test_harness_identity",
            "test_kb_attribution",
            "test_session_self_initialization",
            "test_session_envelope_runtime",
            "test_session_handoff_service",
            "test_single_harness_bridge_automation",
            "test_single_harness_bridge_dispatcher",
            "test_single_harness_doctor_check_upgrade",
            "test_fab01_dispatch_substrate_revival",
            "test_single_harness_governance_artifacts",
            "test_strict_drop_misdirected_headless_dispatch",
            "test_verify_antigravity_dispatch",
            "test_cross_harness_bridge_trigger",
            "test_cross_harness_trigger_suppression",
            "test_cross_harness_trigger_durable_keyed_regression",
            "test_lo_file_safety_gate_role_resolution",
            "test_governing_specs_preserved",
            "test_ollama_dispatch",
            "test_ollama_role_promotion",
            "test_session_self_initialization_canonical_consistency",
            "test_harness_registry_reader_migration",
            "test_bridge_dispatch_per_document_lease",
            "test_gtkb_dispatcher_daemon",
            "test_gtkb_dispatcher_heartbeat",
        ]
    ):
        yield
        return

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_registry = Path(tmpdir) / "harness-registry.json"

        # Load the real harness-registry.json
        real_registry_path = REPO_ROOT / "harness-state" / "harness-registry.json"
        if real_registry_path.exists():
            try:
                data = json.loads(real_registry_path.read_text(encoding="utf-8"))
                # Make all harnesses active for tests so suspended states don't break them
                for h in data.get("harnesses", []):
                    h["status"] = "active"

                # Write to the temp registry
                tmp_registry.write_text(json.dumps(data, indent=2), encoding="utf-8")
            except Exception:
                pass

        # Set the environment variable
        old_val = os.environ.get("GTKB_HARNESS_REGISTRY_PATH")
        os.environ["GTKB_HARNESS_REGISTRY_PATH"] = str(tmp_registry)
        try:
            yield
        finally:
            if old_val is not None:
                os.environ["GTKB_HARNESS_REGISTRY_PATH"] = old_val
            else:
                os.environ.pop("GTKB_HARNESS_REGISTRY_PATH", None)
