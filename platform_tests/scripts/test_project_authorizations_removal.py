# (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""WI-7657: the project_authorizations removal holds and stays held.

This is the regression guard for the removal itself, as distinct from the
per-surface absence assertions in the files that used to exercise it. It
answers three questions a future change could silently re-break:

1. Does the writer surface stay gone from the production API?
2. Does a *freshly opened* database create the relation again? This is the
   question that matters most, because the statement lived in ``SCHEMA_SQL``
   and ``_upgrade_schema`` re-executes that whenever the version stamp or the
   structural sentinels mismatch. A drop alone is not durable; only the
   schema-statement removal makes it so.
3. Does any non-test source still issue SQL against either relation?

Non-vacuity: every absence assertion below is paired with a control that is
still present. An absence check passes trivially if the symbol is misspelled or
an import silently failed, so without the control these tests could all pass
against nothing at all.
"""

from __future__ import annotations

import re
import sqlite3
from pathlib import Path

from groundtruth_kb.db import KnowledgeDB

REPO_ROOT = Path(__file__).resolve().parents[2]

#: The four accessors the retired record exposed on the production API.
REMOVED_WRITERS = (
    "insert_project_authorization",
    "update_project_authorization",
    "get_project_authorization",
    "list_project_authorizations",
)

#: SQL that names either retired relation. Matches the statement forms rather
#: than the bare identifier, so prose and comments do not trip the guard.
SQL_AGAINST_RETIRED_RELATIONS = re.compile(
    r"(?:FROM|INTO|UPDATE|JOIN)\s+(?:current_)?project_authorizations\b",
    re.IGNORECASE,
)

#: Source trees that must not issue SQL against the retired relations.
GUARDED_TREES = ("scripts", "groundtruth-kb/src/groundtruth_kb")

#: Files that still reference the relations and are deliberately not repaired
#: here. Both are authority gates whose PAUTH limb is a subsystem rather than a
#: reader, so removing it is a governance change rather than a repoint, and it
#: is carried separately. This list must only ever shrink; an addition means a
#: new dependency was introduced on a relation that no longer exists.
KNOWN_UNREPAIRED = {
    "scripts/implementation_authorization.py",
}

#: Files that legitimately name the relations while building their OWN
#: throwaway schema in a temporary directory. These are not dependencies on the
#: canonical store: they construct a fixture database, exercise it, and discard
#: it. They are listed separately from KNOWN_UNREPAIRED because they are not
#: work owed -- conflating the two would make a shrinking list look stalled.
#:
#: check_modernization_git_lifecycle.py issues a bare ``CREATE TABLE`` without
#: ``IF NOT EXISTS``, which would recreate the dropped relation if it ever ran
#: against the live database. It does not: its harness is wrapped in
#: ``tempfile.TemporaryDirectory``. That is the property this entry depends on,
#: so a change moving that harness onto the real root must not land silently.
FIXTURE_BUILDERS = {
    "scripts/check_modernization_git_lifecycle.py",
}


def _iter_guarded_sources():
    for tree in GUARDED_TREES:
        root = REPO_ROOT / tree
        if not root.is_dir():
            continue
        for path in root.rglob("*.py"):
            if "__pycache__" in path.parts:
                continue
            yield path


def test_control_api_surface_is_present() -> None:
    """Non-vacuity guard: the production API imported and is the real one."""
    assert hasattr(KnowledgeDB, "insert_project")
    assert hasattr(KnowledgeDB, "get_project")


def test_writers_are_absent_from_the_api() -> None:
    """No accessor for the retired record survives on ``KnowledgeDB``."""
    assert hasattr(KnowledgeDB, "insert_project"), "control method missing"
    for name in REMOVED_WRITERS:
        assert not hasattr(KnowledgeDB, name), f"KnowledgeDB should no longer expose {name}"


def test_fresh_database_creates_no_authorization_objects(tmp_path: Path) -> None:
    """A database built through the production API creates none of the objects.

    Seven objects carried the name before the removal: the table, its view,
    four explicit indexes, and one implicit autoindex. All seven must be
    absent, not merely the table.
    """
    db_path = tmp_path / "groundtruth.db"
    db = KnowledgeDB(db_path=db_path)
    try:
        db.insert_project("Removal Guard", "test", "fixture", id="PROJECT-REMOVAL-GUARD")
    finally:
        db.close()

    connection = sqlite3.connect(db_path)
    try:
        names = {row[0] for row in connection.execute("SELECT name FROM sqlite_master")}
    finally:
        connection.close()

    assert "projects" in names, "control relation missing; the fixture database did not build"
    assert not [name for name in names if "project_authorization" in name]


def test_relation_stays_absent_across_a_second_open(tmp_path: Path) -> None:
    """Reopening runs ``_upgrade_schema``; the relation must not come back.

    This is the durability half. A removal that passes the first check but
    fails this one is the failure mode every prior attempt hit: the drop
    appears to land, then the next connection re-executes ``SCHEMA_SQL`` and
    recreates the table, empty. Empty is worse than populated, because the
    surfaces that read it then deny universally rather than selectively.
    """
    db_path = tmp_path / "groundtruth.db"
    for _ in range(2):
        db = KnowledgeDB(db_path=db_path)
        try:
            specs = db.list_specs()
        finally:
            db.close()

    connection = sqlite3.connect(db_path)
    try:
        names = {row[0] for row in connection.execute("SELECT name FROM sqlite_master")}
    finally:
        connection.close()

    assert isinstance(specs, list), "control read failed; the database did not open"
    assert "projects" in names, "control relation missing after reopen"
    assert not [name for name in names if "project_authorization" in name]


def test_no_unexpected_source_issues_sql_against_the_retired_relations() -> None:
    """No guarded source file gains a new dependency on the retired relations.

    ``KNOWN_UNREPAIRED`` records the two authority gates carried separately.
    The assertion is two-sided on purpose: an unexpected file failing the check
    means a new dependency appeared, and a listed file *passing* means the
    carrier landed and the entry should be deleted.
    """
    offenders = {
        path.relative_to(REPO_ROOT).as_posix()
        for path in _iter_guarded_sources()
        if SQL_AGAINST_RETIRED_RELATIONS.search(path.read_text(encoding="utf-8", errors="ignore"))
    }

    assert any(_iter_guarded_sources()), "control failed; no guarded sources were scanned"

    unexpected = offenders - KNOWN_UNREPAIRED - FIXTURE_BUILDERS
    assert not unexpected, f"new SQL against a retired relation in: {sorted(unexpected)}"

    stale = (KNOWN_UNREPAIRED | FIXTURE_BUILDERS) - offenders
    assert not stale, f"KNOWN_UNREPAIRED lists files that are already clean; delete them: {sorted(stale)}"
