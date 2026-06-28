"""Doctor coverage for application_scope/path alignment."""

from __future__ import annotations

from pathlib import Path

from groundtruth_kb.db import KnowledgeDB
from groundtruth_kb.project.doctor import _check_application_scope_alignment


def test_application_scope_doctor_passes_aligned_rows(tmp_path: Path) -> None:
    db = KnowledgeDB(tmp_path / "groundtruth.db")
    db.insert_spec(
        id="SPEC-APP-ALIGNED",
        title="Aligned app spec",
        status="specified",
        changed_by="test",
        change_reason="seed",
        source_paths=["applications/Agent_Red/app/main.py"],
        application_scope="agent_red_application",
    )
    db.insert_test(
        id="TEST-PLATFORM-ALIGNED",
        title="Aligned platform test",
        spec_id="SPEC-APP-ALIGNED",
        test_type="unit",
        test_file="platform_tests/scripts/test_platform.py",
        expected_outcome="passes",
        changed_by="test",
        change_reason="seed",
        application_scope="gtkb_platform",
    )
    db.close()

    check = _check_application_scope_alignment(tmp_path)

    assert check.status == "pass"
    assert "Application-scope alignment OK" in check.message


def test_application_scope_doctor_fails_explicit_scope_path_mismatch(tmp_path: Path) -> None:
    db = KnowledgeDB(tmp_path / "groundtruth.db")
    db.insert_test(
        id="TEST-MISSCOPED",
        title="Mis-scoped platform test",
        spec_id="SPEC-MISSCOPED",
        test_type="unit",
        test_file="applications/Agent_Red/tests/test_widget.py",
        expected_outcome="passes",
        changed_by="test",
        change_reason="seed",
        application_scope="gtkb_platform",
    )
    db.close()

    check = _check_application_scope_alignment(tmp_path)

    assert check.status == "fail"
    assert "gtkb_platform path points at applications/Agent_Red/" in check.message


def test_application_scope_doctor_warns_on_ambiguous_unscoped_candidates(tmp_path: Path) -> None:
    db = KnowledgeDB(tmp_path / "groundtruth.db")
    db.insert_spec(
        id="SPEC-AMBIGUOUS",
        title="Agent Red generic evidence",
        status="specified",
        changed_by="test",
        change_reason="seed",
        source_paths=["tests/test_agent_red_widget.py"],
    )
    db.close()

    check = _check_application_scope_alignment(tmp_path)

    assert check.status == "warning"
    assert "ambiguous application-scope candidate" in check.message
