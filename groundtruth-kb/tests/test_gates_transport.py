"""Tests for the Transport Evidence Governance Gate plugin."""

from __future__ import annotations

from pathlib import Path

import pytest

from groundtruth_kb.gates import GateRegistry, GovernanceGateError
from groundtruth_kb.gates_transport import TransportEvidenceGate, TransportEvidenceGateError

GATED_SPEC = "SPEC-1524"
NON_GATED_SPEC = "SPEC-9999"
GATED_IDS = {"SPEC-1524", "SPEC-1525"}


class TestTransportEvidenceGateTestPass:
    """Tests for pre_test_pass enforcement."""

    def test_blocks_pass_without_test_file(self, tmp_path: Path):
        gate = TransportEvidenceGate(spec_ids=GATED_IDS, project_root=tmp_path)
        with pytest.raises(TransportEvidenceGateError, match="test_file is required"):
            gate.pre_test_pass("TEST-001", GATED_SPEC, None, {})

    def test_blocks_pass_with_nonexistent_test_file(self, tmp_path: Path):
        gate = TransportEvidenceGate(spec_ids=GATED_IDS, project_root=tmp_path)
        with pytest.raises(TransportEvidenceGateError, match="does not exist on disk"):
            gate.pre_test_pass("TEST-001", GATED_SPEC, "tests/missing.py", {})

    def test_allows_pass_with_real_test_file(self, tmp_path: Path):
        test_file = tmp_path / "tests" / "test_transport.py"
        test_file.parent.mkdir(parents=True)
        test_file.write_text("def test_pass(): pass")
        gate = TransportEvidenceGate(spec_ids=GATED_IDS, project_root=tmp_path)
        # Should not raise
        gate.pre_test_pass("TEST-001", GATED_SPEC, "tests/test_transport.py", {})

    def test_allows_pass_for_non_gated_spec(self, tmp_path: Path):
        gate = TransportEvidenceGate(spec_ids=GATED_IDS, project_root=tmp_path)
        # Non-gated spec should always pass regardless of test_file
        gate.pre_test_pass("TEST-001", NON_GATED_SPEC, None, {})

    def test_allows_non_pass_result_for_gated_spec(self, tmp_path: Path):
        """pre_test_pass is only called for 'pass' results — other results bypass."""
        gate = TransportEvidenceGate(spec_ids=GATED_IDS, project_root=tmp_path)
        # Direct call still checks, but the DB only calls it for 'pass'
        gate.pre_test_pass("TEST-001", NON_GATED_SPEC, None, {})


class TestTransportEvidenceGateSpecPromotion:
    """Tests for pre_promote enforcement (spec → verified)."""

    def test_blocks_verified_without_linked_tests(self, tmp_path: Path):
        gate = TransportEvidenceGate(spec_ids=GATED_IDS, project_root=tmp_path)
        with pytest.raises(TransportEvidenceGateError, match="no linked tests found"):
            gate.pre_promote(GATED_SPEC, "implemented", "verified", {"linked_tests": []})

    def test_blocks_verified_with_missing_test_file(self, tmp_path: Path):
        gate = TransportEvidenceGate(spec_ids=GATED_IDS, project_root=tmp_path)
        linked = [{"id": "TEST-001", "test_file": None, "last_result": "pass"}]
        with pytest.raises(TransportEvidenceGateError, match="no test_file"):
            gate.pre_promote(GATED_SPEC, "implemented", "verified", {"linked_tests": linked})

    def test_blocks_verified_with_nonexistent_test_file(self, tmp_path: Path):
        gate = TransportEvidenceGate(spec_ids=GATED_IDS, project_root=tmp_path)
        linked = [{"id": "TEST-001", "test_file": "tests/missing.py", "last_result": "pass"}]
        with pytest.raises(TransportEvidenceGateError, match="does not exist on disk"):
            gate.pre_promote(GATED_SPEC, "implemented", "verified", {"linked_tests": linked})

    def test_blocks_verified_with_failing_test(self, tmp_path: Path):
        test_file = tmp_path / "tests" / "test_transport.py"
        test_file.parent.mkdir(parents=True)
        test_file.write_text("def test_fail(): pass")
        gate = TransportEvidenceGate(spec_ids=GATED_IDS, project_root=tmp_path)
        linked = [{"id": "TEST-001", "test_file": "tests/test_transport.py", "last_result": "fail"}]
        with pytest.raises(TransportEvidenceGateError, match="not 'pass'"):
            gate.pre_promote(GATED_SPEC, "implemented", "verified", {"linked_tests": linked})

    def test_allows_verified_with_full_evidence(self, tmp_path: Path):
        test_file = tmp_path / "tests" / "test_transport.py"
        test_file.parent.mkdir(parents=True)
        test_file.write_text("def test_pass(): pass")
        gate = TransportEvidenceGate(spec_ids=GATED_IDS, project_root=tmp_path)
        linked = [{"id": "TEST-001", "test_file": "tests/test_transport.py", "last_result": "pass"}]
        # Should not raise
        gate.pre_promote(GATED_SPEC, "implemented", "verified", {"linked_tests": linked})

    def test_allows_non_verified_promotion(self, tmp_path: Path):
        gate = TransportEvidenceGate(spec_ids=GATED_IDS, project_root=tmp_path)
        # Promoting to 'implemented' doesn't trigger transport gate
        gate.pre_promote(GATED_SPEC, "specified", "implemented", {})

    def test_allows_verified_for_non_gated_spec(self, tmp_path: Path):
        gate = TransportEvidenceGate(spec_ids=GATED_IDS, project_root=tmp_path)
        # Non-gated specs can be verified without evidence
        gate.pre_promote(NON_GATED_SPEC, "implemented", "verified", {})

    def test_blocks_verified_multiple_tests_one_failing(self, tmp_path: Path):
        f1 = tmp_path / "tests" / "test_a.py"
        f2 = tmp_path / "tests" / "test_b.py"
        f1.parent.mkdir(parents=True, exist_ok=True)
        f1.write_text("pass")
        f2.write_text("pass")
        gate = TransportEvidenceGate(spec_ids=GATED_IDS, project_root=tmp_path)
        linked = [
            {"id": "TEST-001", "test_file": "tests/test_a.py", "last_result": "pass"},
            {"id": "TEST-002", "test_file": "tests/test_b.py", "last_result": "fail"},
        ]
        with pytest.raises(TransportEvidenceGateError, match="TEST-002"):
            gate.pre_promote(GATED_SPEC, "implemented", "verified", {"linked_tests": linked})


class TestTransportEvidenceGateConfig:
    """Tests for from_config construction."""

    def test_from_config_with_spec_ids(self, tmp_path: Path):
        config = {"spec_ids": ["SPEC-1524", "SPEC-1525"], "project_root": str(tmp_path)}
        gate = TransportEvidenceGate.from_config(config)
        assert gate._spec_ids == frozenset({"SPEC-1524", "SPEC-1525"})
        assert gate._project_root == tmp_path

    def test_from_config_empty(self):
        gate = TransportEvidenceGate.from_config({})
        assert gate._spec_ids == frozenset()
        assert gate._project_root == Path(".")

    def test_from_config_no_project_root(self):
        gate = TransportEvidenceGate.from_config({"spec_ids": ["SPEC-1"]})
        assert gate._spec_ids == frozenset({"SPEC-1"})

    def test_default_constructor_empty(self):
        gate = TransportEvidenceGate()
        assert gate._spec_ids == frozenset()
        assert gate.name() == "Transport Evidence Gate"


class TestTransportGateRegistryIntegration:
    """Tests for transport gate integrated with GateRegistry."""

    def test_registry_from_config_with_gate_config(self, tmp_path: Path):
        """Test that GateRegistry.from_config passes config to TransportEvidenceGate."""
        registry = GateRegistry.from_config(
            gate_paths=["groundtruth_kb.gates_transport:TransportEvidenceGate"],
            include_builtins=False,
            gate_config={
                "TransportEvidenceGate": {
                    "spec_ids": ["SPEC-1524"],
                    "project_root": str(tmp_path),
                }
            },
        )
        assert len(registry._gates) == 1
        gate = registry._gates[0]
        assert isinstance(gate, TransportEvidenceGate)
        assert gate._spec_ids == frozenset({"SPEC-1524"})

    def test_registry_runs_transport_gate_on_test_pass(self, tmp_path: Path):
        gate = TransportEvidenceGate(spec_ids={"SPEC-1524"}, project_root=tmp_path)
        registry = GateRegistry()
        registry.register(gate)
        # Should block — no test file
        with pytest.raises(GovernanceGateError, match="test_file is required"):
            registry.run_pre_test_pass("TEST-001", "SPEC-1524", None, {})

    def test_registry_runs_transport_gate_on_promote(self, tmp_path: Path):
        gate = TransportEvidenceGate(spec_ids={"SPEC-1524"}, project_root=tmp_path)
        registry = GateRegistry()
        registry.register(gate)
        # Should block — no linked tests
        with pytest.raises(GovernanceGateError, match="no linked tests"):
            registry.run_pre_promote("SPEC-1524", "implemented", "verified", {"linked_tests": []})


class TestTransportGateDBIntegration:
    """Tests for transport gate integrated with KnowledgeDB."""

    def test_db_blocks_test_pass_via_gate(self, tmp_path: Path):
        from groundtruth_kb.db import KnowledgeDB
        from groundtruth_kb.gates import GateRegistry

        gate = TransportEvidenceGate(spec_ids={"SPEC-1524"}, project_root=tmp_path)
        registry = GateRegistry(_gates=[gate])
        db = KnowledgeDB(db_path=tmp_path / "test.db", gate_registry=registry)

        # Insert spec first
        db.insert_spec("SPEC-1524", "Transport test", "specified", "test", "test")

        # Should block — gated spec, no test_file
        with pytest.raises(GovernanceGateError, match="test_file is required"):
            db.insert_test(
                "TEST-001",
                "Transport test",
                "SPEC-1524",
                "e2e",
                "pass expected",
                "test",
                "test",
                last_result="pass",
            )

    def test_db_allows_test_pass_with_evidence(self, tmp_path: Path):
        from groundtruth_kb.db import KnowledgeDB
        from groundtruth_kb.gates import GateRegistry

        test_file = tmp_path / "tests" / "test_transport.py"
        test_file.parent.mkdir(parents=True)
        test_file.write_text("def test_pass(): pass")

        gate = TransportEvidenceGate(spec_ids={"SPEC-1524"}, project_root=tmp_path)
        registry = GateRegistry(_gates=[gate])
        db = KnowledgeDB(db_path=tmp_path / "test.db", gate_registry=registry)

        db.insert_spec("SPEC-1524", "Transport test", "specified", "test", "test")
        # Should succeed — real test file
        result = db.insert_test(
            "TEST-001",
            "Transport test",
            "SPEC-1524",
            "e2e",
            "pass expected",
            "test",
            "test",
            test_file="tests/test_transport.py",
            last_result="pass",
        )
        assert result["last_result"] == "pass"

    def test_db_allows_non_pass_for_gated_spec(self, tmp_path: Path):
        from groundtruth_kb.db import KnowledgeDB
        from groundtruth_kb.gates import GateRegistry

        gate = TransportEvidenceGate(spec_ids={"SPEC-1524"}, project_root=tmp_path)
        registry = GateRegistry(_gates=[gate])
        db = KnowledgeDB(db_path=tmp_path / "test.db", gate_registry=registry)

        db.insert_spec("SPEC-1524", "Transport test", "specified", "test", "test")
        # Non-pass results should not trigger gate
        result = db.insert_test(
            "TEST-001",
            "Transport test",
            "SPEC-1524",
            "e2e",
            "pass expected",
            "test",
            "test",
            last_result="fail",
        )
        assert result["last_result"] == "fail"

    def test_db_blocks_spec_verified_via_gate(self, tmp_path: Path):
        from groundtruth_kb.db import KnowledgeDB
        from groundtruth_kb.gates import GateRegistry

        gate = TransportEvidenceGate(spec_ids={"SPEC-1524"}, project_root=tmp_path)
        registry = GateRegistry(_gates=[gate])
        db = KnowledgeDB(db_path=tmp_path / "test.db", gate_registry=registry)

        db.insert_spec("SPEC-1524", "Transport test", "specified", "test", "initial")
        # Should block verified — no linked tests
        with pytest.raises(GovernanceGateError, match="no linked tests"):
            db.update_spec("SPEC-1524", "test", "promote", status="verified")

    def test_db_allows_spec_verified_with_evidence(self, tmp_path: Path):
        from groundtruth_kb.db import KnowledgeDB
        from groundtruth_kb.gates import GateRegistry

        test_file = tmp_path / "tests" / "test_transport.py"
        test_file.parent.mkdir(parents=True)
        test_file.write_text("def test_pass(): pass")

        gate = TransportEvidenceGate(spec_ids={"SPEC-1524"}, project_root=tmp_path)
        registry = GateRegistry(_gates=[gate])
        db = KnowledgeDB(db_path=tmp_path / "test.db", gate_registry=registry)

        db.insert_spec("SPEC-1524", "Transport test", "implemented", "test", "initial")
        db.insert_test(
            "TEST-001",
            "Transport test",
            "SPEC-1524",
            "e2e",
            "pass expected",
            "test",
            "test",
            test_file="tests/test_transport.py",
            last_result="pass",
        )
        # Should succeed — all evidence present
        result = db.update_spec("SPEC-1524", "test", "promote", status="verified")
        assert result["status"] == "verified"
