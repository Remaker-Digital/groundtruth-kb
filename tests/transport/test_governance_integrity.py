"""Phase 3 — Governance integrity tests.

Proves KB governance gates reject invalid operations by executing real
DB operations against a test KB instance. No source inspection — all
tests perform actual insert/update calls and verify rejection or success.

Recovery plan reference: INSIGHTS-2026-03-27-01-00.md Phase 3, Category 5.
Governing decisions: DCL-003.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import os
import shutil
import sys
import tempfile
from pathlib import Path

import pytest

# Ensure tools/knowledge-db is importable
_PROJECT_ROOT = Path(__file__).resolve().parents[2]
_TOOLS_DIR = str(_PROJECT_ROOT / "tools" / "knowledge-db")
if _TOOLS_DIR not in sys.path:
    sys.path.insert(0, _TOOLS_DIR)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def test_db():
    """Create a temporary copy of the KB for governance gate testing.

    Yields a KnowledgeDB instance backed by a temp file. Cleaned up after test.
    """
    import db as kb_db

    src_db = _PROJECT_ROOT / "tools" / "knowledge-db" / "knowledge.db"
    tmp_dir = tempfile.mkdtemp(prefix="governance_test_")
    tmp_db = Path(tmp_dir) / "test_knowledge.db"
    shutil.copy2(src_db, tmp_db)

    instance = kb_db.KnowledgeDB(str(tmp_db))
    yield instance

    # Cleanup
    shutil.rmtree(tmp_dir, ignore_errors=True)


@pytest.fixture
def transport_gated_spec_id():
    """Return one of the transport-gated spec IDs for testing."""
    import db as kb_db
    return next(iter(kb_db._TRANSPORT_GATED_SPECS))


@pytest.fixture
def non_transport_spec_id():
    """Return a spec ID that is NOT transport-gated."""
    return "SPEC-0001"  # Likely a non-transport spec


# ---------------------------------------------------------------------------
# 1. KB rejects pass without test file
# ---------------------------------------------------------------------------


class TestGovernanceGateRejectNoFile:
    """KB must reject test='pass' for transport specs without test_file."""

    def test_rejects_pass_without_test_file(self, test_db, transport_gated_spec_id):
        """insert_test with pass and no test_file must raise TransportEvidenceGateError."""
        import db as kb_db

        with pytest.raises(kb_db.TransportEvidenceGateError):
            test_db.insert_test(
                id="TEST-GOVTEST-001",
                title="Governance gate test — no file",
                spec_id=transport_gated_spec_id,
                test_type="behavioral",
                expected_outcome="pass",
                changed_by="S226-governance-test",
                change_reason="Phase 3 governance gate verification",
                last_result="pass",
                # test_file intentionally omitted
            )


# ---------------------------------------------------------------------------
# 2. KB rejects pass with fake test file
# ---------------------------------------------------------------------------


class TestGovernanceGateRejectFakeFile:
    """KB must reject test='pass' for transport specs with non-existent file."""

    def test_rejects_pass_with_nonexistent_file(self, test_db, transport_gated_spec_id):
        """insert_test with pass and a fake file path must raise TransportEvidenceGateError."""
        import db as kb_db

        with pytest.raises(kb_db.TransportEvidenceGateError):
            test_db.insert_test(
                id="TEST-GOVTEST-002",
                title="Governance gate test — fake file",
                spec_id=transport_gated_spec_id,
                test_type="behavioral",
                expected_outcome="pass",
                changed_by="S226-governance-test",
                change_reason="Phase 3 governance gate verification",
                last_result="pass",
                test_file="tests/transport/NONEXISTENT_FILE_12345.py",
            )


# ---------------------------------------------------------------------------
# 3. KB rejects spec promotion without evidence
# ---------------------------------------------------------------------------


class TestGovernanceGateRejectPromotion:
    """KB must reject promoting transport spec to 'verified' without evidence."""

    def test_rejects_verified_without_passing_tests(self, test_db, transport_gated_spec_id):
        """update_spec to 'verified' must fail if no linked tests pass.

        The transport governance gate checks all linked tests before allowing
        a transport spec to reach 'verified' status.
        """
        import db as kb_db

        with pytest.raises(kb_db.TransportEvidenceGateError):
            test_db.update_spec(
                id=transport_gated_spec_id,
                changed_by="S226-governance-test",
                change_reason="Phase 3 governance gate verification — should be rejected",
                status="verified",
            )


# ---------------------------------------------------------------------------
# 4. KB allows pass with real test file
# ---------------------------------------------------------------------------


class TestGovernanceGateAllowsReal:
    """KB must allow test='pass' when a real test file is provided."""

    def test_allows_pass_with_real_file(self, test_db, transport_gated_spec_id):
        """insert_test with pass and a real file that exists on disk must succeed."""
        # _resolve_test_file resolves relative to DB_PATH.parent.parent (tools/)
        # so we need a path relative to tools/, not repo root
        real_file = "../tests/transport/test_governance_integrity.py"
        import db as kb_db
        resolved = kb_db._resolve_test_file(real_file)
        assert resolved is not None and resolved.is_file(), (
            f"Test file {real_file} must resolve to an existing file (got {resolved})"
        )

        # Should NOT raise
        test_db.insert_test(
            id="TEST-GOVTEST-004",
            title="Governance gate test — real file",
            spec_id=transport_gated_spec_id,
            test_type="behavioral",
            expected_outcome="pass",
            changed_by="S226-governance-test",
            change_reason="Phase 3 governance gate verification — should succeed",
            last_result="pass",
            test_file=real_file,
        )


# ---------------------------------------------------------------------------
# 5. Non-transport spec not gated
# ---------------------------------------------------------------------------


class TestGovernanceGateNotGated:
    """Non-transport specs must not be subject to the governance gate."""

    def test_non_transport_spec_allows_pass_without_file(self, test_db, non_transport_spec_id):
        """insert_test with pass for a non-transport spec should succeed even without file."""
        # Should NOT raise — gate does not apply to non-transport specs
        test_db.insert_test(
            id="TEST-GOVTEST-005",
            title="Non-transport spec — ungated",
            spec_id=non_transport_spec_id,
            test_type="behavioral",
            expected_outcome="pass",
            changed_by="S226-governance-test",
            change_reason="Phase 3 governance gate verification — non-transport",
            last_result="pass",
            # No test_file — should be fine for non-transport spec
        )
