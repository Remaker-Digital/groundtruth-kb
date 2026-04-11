"""Tests for governance gate system."""

from __future__ import annotations

import pytest

from groundtruth_kb.gates import (
    ADRDCLAssertionGate,
    GateRegistry,
    GovernanceGate,
    GovernanceGateError,
    OwnerApprovalGate,
)


class TestADRDCLAssertionGate:
    """Tests for the built-in ADR/DCL assertion gate."""

    def test_blocks_implemented_adr_without_assertions(self):
        gate = ADRDCLAssertionGate()
        with pytest.raises(GovernanceGateError, match="non-empty assertions"):
            gate.pre_promote(
                "ADR-001",
                "specified",
                "implemented",
                {"type": "architecture_decision", "assertions": ""},
            )

    def test_blocks_implemented_dcl_without_assertions(self):
        gate = ADRDCLAssertionGate()
        with pytest.raises(GovernanceGateError, match="non-empty assertions"):
            gate.pre_promote(
                "DCL-001",
                "specified",
                "implemented",
                {"type": "design_constraint", "assertions": None},
            )

    def test_allows_implemented_adr_with_assertions(self):
        gate = ADRDCLAssertionGate()
        # Should not raise
        gate.pre_promote(
            "ADR-001",
            "specified",
            "implemented",
            {"type": "architecture_decision", "assertions": '[{"check": "exists"}]'},
        )

    def test_allows_non_adr_without_assertions(self):
        gate = ADRDCLAssertionGate()
        # Regular specs don't need assertions for 'implemented'
        gate.pre_promote(
            "SPEC-100",
            "specified",
            "implemented",
            {"type": "requirement", "assertions": ""},
        )

    def test_allows_adr_for_non_implemented_status(self):
        gate = ADRDCLAssertionGate()
        # ADR going to 'specified' doesn't need assertions
        gate.pre_promote(
            "ADR-001",
            "new",
            "specified",
            {"type": "architecture_decision", "assertions": ""},
        )


class TestOwnerApprovalGate:
    """Tests for the built-in owner approval gate."""

    def test_blocks_defect_resolution_without_approval(self):
        gate = OwnerApprovalGate()
        with pytest.raises(GovernanceGateError, match="owner_approved=True"):
            gate.pre_resolve_work_item(
                "WI-100",
                "defect",
                "resolved",
                False,
                {"origin": "defect"},
            )

    def test_blocks_regression_resolution_without_approval(self):
        gate = OwnerApprovalGate()
        with pytest.raises(GovernanceGateError, match="owner_approved=True"):
            gate.pre_resolve_work_item(
                "WI-100",
                "regression",
                "resolved",
                False,
                {"origin": "regression"},
            )

    def test_allows_defect_resolution_with_approval(self):
        gate = OwnerApprovalGate()
        # Should not raise
        gate.pre_resolve_work_item(
            "WI-100",
            "defect",
            "resolved",
            True,
            {"origin": "defect"},
        )

    def test_allows_new_wi_resolution_without_approval(self):
        gate = OwnerApprovalGate()
        # 'new' origin doesn't require owner approval
        gate.pre_resolve_work_item(
            "WI-100",
            "new",
            "resolved",
            False,
            {"origin": "new"},
        )


class TestGateRegistry:
    """Tests for gate registry behavior."""

    def test_from_config_includes_builtins(self):
        registry = GateRegistry.from_config([], include_builtins=True)
        assert len(registry._gates) == 2
        assert isinstance(registry._gates[0], ADRDCLAssertionGate)
        assert isinstance(registry._gates[1], OwnerApprovalGate)

    def test_from_config_no_builtins(self):
        registry = GateRegistry.from_config([], include_builtins=False)
        assert len(registry._gates) == 0

    def test_registry_runs_all_gates(self):
        registry = GateRegistry.from_config([], include_builtins=True)
        # ADR without assertions should fail
        with pytest.raises(GovernanceGateError):
            registry.run_pre_promote(
                "ADR-001",
                "specified",
                "implemented",
                {"type": "architecture_decision", "assertions": ""},
            )

    def test_registry_passes_when_gates_pass(self):
        registry = GateRegistry.from_config([], include_builtins=True)
        # Regular spec should pass all gates
        registry.run_pre_promote(
            "SPEC-100",
            "specified",
            "implemented",
            {"type": "requirement", "assertions": ""},
        )

    def test_custom_gate_registration(self):
        class TestGate(GovernanceGate):
            def name(self):
                return "Test Gate"

            def pre_promote(self, spec_id, current_status, target_status, spec_data):
                if spec_data.get("blocked"):
                    raise GovernanceGateError("Blocked by test gate")

        registry = GateRegistry.from_config([], include_builtins=False)
        registry.register(TestGate())
        # Should pass
        registry.run_pre_promote("SPEC-1", "specified", "implemented", {})
        # Should fail
        with pytest.raises(GovernanceGateError, match="Blocked by test gate"):
            registry.run_pre_promote("SPEC-1", "specified", "implemented", {"blocked": True})

    def test_import_invalid_path(self):
        with pytest.raises(ValueError, match="must be 'module:ClassName'"):
            GateRegistry.from_config(["no_colon_here"])


class TestOwnerApprovalGateDBPath:
    """DB integration test: OwnerApprovalGate through the full KnowledgeDB path.

    Reproduces the P1 bug from Codex strategic assessment (INSIGHTS-2026-04-10-23-20):
    gates.py:126 passed wi_id as origin, bypassing the gate.
    """

    def test_defect_wi_resolution_blocked_without_approval(self, tmp_path):
        """Defect WI resolved via update_work_item without owner_approved must raise."""
        from groundtruth_kb.db import KnowledgeDB

        db_path = tmp_path / "gate_test.db"
        registry = GateRegistry.from_config([], include_builtins=True)
        db = KnowledgeDB(db_path=db_path, gate_registry=registry)

        db.insert_work_item(
            id="WI-GATE-001",
            title="Defect for gate test",
            origin="defect",
            component="test",
            resolution_status="open",
            stage="created",
            changed_by="test",
            change_reason="gate integration test",
        )

        with pytest.raises(GovernanceGateError, match="owner_approved=True"):
            db.update_work_item(
                "WI-GATE-001",
                changed_by="test",
                change_reason="attempt resolve without approval",
                resolution_status="resolved",
                stage="resolved",
                owner_approved=False,
            )

        # WI should still be open
        wi = db.get_work_item("WI-GATE-001")
        assert wi["resolution_status"] == "open"

    def test_defect_wi_resolution_allowed_with_approval(self, tmp_path):
        """Defect WI resolved with owner_approved=True must succeed."""
        from groundtruth_kb.db import KnowledgeDB

        db_path = tmp_path / "gate_test2.db"
        registry = GateRegistry.from_config([], include_builtins=True)
        db = KnowledgeDB(db_path=db_path, gate_registry=registry)

        db.insert_work_item(
            id="WI-GATE-002",
            title="Defect for gate test",
            origin="defect",
            component="test",
            resolution_status="open",
            stage="created",
            changed_by="test",
            change_reason="gate integration test",
        )

        db.update_work_item(
            "WI-GATE-002",
            changed_by="test",
            change_reason="resolve with approval",
            resolution_status="resolved",
            stage="resolved",
            owner_approved=True,
        )

        wi = db.get_work_item("WI-GATE-002")
        assert wi["resolution_status"] == "resolved"

    def test_regression_wi_resolution_blocked_without_approval(self, tmp_path):
        """Regression WI resolved without owner_approved must raise."""
        from groundtruth_kb.db import KnowledgeDB

        db_path = tmp_path / "gate_test3.db"
        registry = GateRegistry.from_config([], include_builtins=True)
        db = KnowledgeDB(db_path=db_path, gate_registry=registry)

        db.insert_work_item(
            id="WI-GATE-003",
            title="Regression for gate test",
            origin="regression",
            component="test",
            resolution_status="open",
            stage="created",
            changed_by="test",
            change_reason="gate integration test",
        )

        with pytest.raises(GovernanceGateError, match="owner_approved=True"):
            db.update_work_item(
                "WI-GATE-003",
                changed_by="test",
                change_reason="attempt resolve without approval",
                resolution_status="resolved",
                stage="resolved",
                owner_approved=False,
            )
