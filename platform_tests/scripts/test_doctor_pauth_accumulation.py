# (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""WI-7657: the PAUTH accumulation doctor check is absent.

This file previously exercised ``check_project_authorization_hygiene`` and its
private ``_check_project_authorization_hygiene`` wrapper against a fixture
``groundtruth.db`` seeded with authorization rows. Both the check and the
``project_authorizations`` relation it read are gone, so the file now asserts
their absence instead of their behaviour.

Non-vacuity, per the review condition on absence assertions: an absence check
passes trivially if the symbol name is misspelled, so every test here pairs the
absent names with a control symbol that is still present in the same module.
If the import path broke, or the names were mistyped, the control assertion
fails and the test does not pass silently.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path

from groundtruth_kb.db import KnowledgeDB
from groundtruth_kb.project import doctor

#: The two names this module exported for the retired doctor check.
REMOVED_DOCTOR_CHECKS = (
    "_check_project_authorization_hygiene",
    "check_project_authorization_hygiene",
)

#: A check that still exists in the same module. Its presence proves the import
#: resolved and the module under test is the real one, so the absence
#: assertions below cannot pass merely because nothing was imported.
CONTROL_DOCTOR_CHECK = "_check_python"


def test_control_symbol_is_present() -> None:
    """The module imported and still exports a real check.

    This is the non-vacuity guard for every absence assertion in this file.
    """
    assert hasattr(doctor, CONTROL_DOCTOR_CHECK), (
        f"control symbol {CONTROL_DOCTOR_CHECK} is missing from groundtruth_kb.project.doctor; "
        "the absence assertions in this module would be vacuous"
    )


def test_pauth_hygiene_doctor_checks_are_absent() -> None:
    """Neither the private check nor its public wrapper survives."""
    assert hasattr(doctor, CONTROL_DOCTOR_CHECK)
    for name in REMOVED_DOCTOR_CHECKS:
        assert not hasattr(doctor, name), f"{name} should have been removed from groundtruth_kb.project.doctor"


def test_removed_checks_are_not_registered_in_any_doctor_surface() -> None:
    """The names are gone from the module source, not merely unexported."""
    source = Path(doctor.__file__).read_text(encoding="utf-8")
    assert "def _check_python" in source, "control marker missing; the source read did not resolve the real module"
    for name in REMOVED_DOCTOR_CHECKS:
        assert name not in source, f"{name} still appears in {doctor.__file__}"


def test_fresh_database_creates_no_authorization_relation(tmp_path: Path) -> None:
    """A database built through the production API has no authorization store.

    This is the durable half of the removal: the schema no longer creates the
    table, so it cannot return on a later open.
    """
    db_path = tmp_path / "groundtruth.db"
    db = KnowledgeDB(db_path=db_path)
    try:
        db.insert_project("Project Fixture", "test", "fixture", id="PROJECT-FIXTURE")
    finally:
        db.close()

    connection = sqlite3.connect(db_path)
    try:
        names = {row[0] for row in connection.execute("SELECT name FROM sqlite_master")}
    finally:
        connection.close()

    assert "projects" in names, "control relation missing; the fixture database did not build"
    assert not [name for name in names if "project_authorization" in name], (
        "a fresh database created an authorization relation"
    )


def test_knowledge_db_exposes_no_authorization_writers() -> None:
    """The writers that populated the retired store are gone from the API."""
    assert hasattr(KnowledgeDB, "insert_project"), "control method missing; KnowledgeDB did not import correctly"
    for name in (
        "insert_project_authorization",
        "update_project_authorization",
        "get_project_authorization",
        "list_project_authorizations",
    ):
        assert not hasattr(KnowledgeDB, name), f"KnowledgeDB should no longer expose {name}"
