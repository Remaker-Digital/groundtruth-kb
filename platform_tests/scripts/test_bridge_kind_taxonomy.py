# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
import tempfile
from pathlib import Path

from groundtruth_kb.bridge.taxonomy import BridgeKind

from scripts.lint_bridge_proposals import lint_file_content
from scripts.migrate_bridge_kind_taxonomy import map_bridge_kind


def test_bridge_kind_enum_values():
    assert BridgeKind.PRIME_PROPOSAL == "prime_proposal"
    assert BridgeKind.LO_VERDICT == "lo_verdict"
    assert BridgeKind.IMPLEMENTATION_REPORT == "implementation_report"
    assert BridgeKind.GOVERNANCE_ADVISORY == "governance_advisory"
    assert BridgeKind.INDEX_RECONCILIATION == "index_reconciliation"
    assert BridgeKind.OPERATIONAL_STATE_CHANGE == "operational_state_change"


def test_lint_file_content_valid():
    content = """NEW
bridge_kind: prime_proposal
Document: foo
Version: 001
"""
    assert lint_file_content(content) is None


def test_lint_file_content_invalid():
    content = """NEW
bridge_kind: invalid_kind_value
Document: foo
Version: 001
"""
    err = lint_file_content(content)
    assert err is not None
    assert "Invalid bridge_kind" in err


def test_lint_file_content_missing():
    # If bridge_kind is missing, it should pass (fail-open for legacy)
    content = """NEW
Document: foo
Version: 001
"""
    assert lint_file_content(content) is None


def test_map_bridge_kind():
    # LO Verdict mapping
    assert map_bridge_kind("loyal_opposition_verdict", "GO") == "lo_verdict"
    assert map_bridge_kind("verification_verdict", "VERIFIED") == "lo_verdict"
    assert map_bridge_kind("review_verdict", "GO") == "lo_verdict"
    assert map_bridge_kind("review", "GO") == "lo_verdict"

    # Prime Proposal mapping
    assert map_bridge_kind("implementation_proposal", "NEW") == "prime_proposal"
    assert map_bridge_kind("proposal", "NEW") == "prime_proposal"
    assert map_bridge_kind("scoping_proposal", "NEW") == "prime_proposal"

    # Prime Report mapping
    assert map_bridge_kind("implementation_report", "NEW") == "implementation_report"
    assert map_bridge_kind("post_implementation_report", "NEW") == "implementation_report"

    # Governance & Advisory mapping
    assert map_bridge_kind("governance_review", "NEW") == "governance_advisory"
    assert map_bridge_kind("loyal_opposition_advisory", "NEW") == "governance_advisory"

    # Heuristic fallback
    assert map_bridge_kind("some_custom_verdict", "GO") == "lo_verdict"
    assert map_bridge_kind("custom_proposal", "NEW") == "prime_proposal"
    assert map_bridge_kind("unknown_kind", "GO") == "lo_verdict"
    assert map_bridge_kind("unknown_kind", "NEW") == "prime_proposal"


def test_migration_and_rollback():
    # Setup temporary directory for test migration
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        bridge_dir = tmp_path / "bridge"
        bridge_dir.mkdir()
        backup_dir = tmp_path / ".gtkb-state" / "bridge-backup-taxonomy-migration"

        # Create a mock proposal file with legacy bridge_kind
        proposal_file = bridge_dir / "gtkb-test-proposal-001.md"
        proposal_content = """NEW
bridge_kind: implementation_proposal
Document: gtkb-test-proposal
Version: 001
"""
        proposal_file.write_text(proposal_content, encoding="utf-8")

        # Create another mock verdict file with legacy bridge_kind
        verdict_file = bridge_dir / "gtkb-test-proposal-002.md"
        verdict_content = """GO
bridge_kind: loyal_opposition_verdict
Document: gtkb-test-proposal
Version: 002
"""
        verdict_file.write_text(verdict_content, encoding="utf-8")

        # Patch/mock the paths in migrate_bridge_kind_taxonomy module
        import scripts.migrate_bridge_kind_taxonomy as migrator

        orig_bridge_dir = migrator.BRIDGE_DIR
        orig_backup_dir = migrator.BACKUP_DIR
        orig_project_root = migrator.PROJECT_ROOT

        migrator.BRIDGE_DIR = bridge_dir
        migrator.BACKUP_DIR = backup_dir
        migrator.PROJECT_ROOT = tmp_path

        try:
            # Run migration main
            exit_code = migrator.main([])
            assert exit_code == 0

            # Check backup directory created and matches
            assert backup_dir.is_dir()
            assert (backup_dir / proposal_file.name).is_file()
            assert (backup_dir / verdict_file.name).is_file()

            # Check migrated contents
            new_prop_content = proposal_file.read_text(encoding="utf-8")
            assert "bridge_kind: prime_proposal" in new_prop_content

            new_verd_content = verdict_file.read_text(encoding="utf-8")
            assert "bridge_kind: lo_verdict" in new_verd_content

            # Run rollback
            exit_code_rollback = migrator.main(["--rollback"])
            assert exit_code_rollback == 0

            # Verify original content is restored
            assert proposal_file.read_text(encoding="utf-8") == proposal_content
            assert verdict_file.read_text(encoding="utf-8") == verdict_content

        finally:
            migrator.BRIDGE_DIR = orig_bridge_dir
            migrator.BACKUP_DIR = orig_backup_dir
            migrator.PROJECT_ROOT = orig_project_root
