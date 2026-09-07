"""Inactive-authorization denial must be navigable (WI-7300).

The denial is correct - an inactive authorization confers no authority - but it
was a dead end: it named the dead identifier and stopped. An agent could not tell
whether it had mis-cited a live record or was working inside a project with no
active authorization at all, and those need opposite responses.

These assertions are behavioral against the real resolver, per SPEC-1662: they
exercise `validate_project_authorization_row` and
`_live_project_authorization_refusal_hint` rather than grepping for message text.

Specification coverage:
  DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001 - the denial surface changed
  GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001 - the decision is unchanged; only the diagnostic
  SPEC-1662 - behavioral assertions against the real resolver and the real corpus
"""

from __future__ import annotations

import importlib.util
import sqlite3
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = REPO_ROOT / "scripts" / "implementation_authorization.py"


def _load_module():
    spec = importlib.util.spec_from_file_location("gtkb_implementation_authorization", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def auth():
    return _load_module()


def _row(**fields) -> sqlite3.Row:
    """Build a real sqlite3.Row so the resolver sees production row semantics."""
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    cols = ", ".join(f'"{k}"' for k in fields)
    marks = ", ".join("?" for _ in fields)
    conn.execute(f"CREATE TABLE r ({', '.join(f'{k} TEXT' for k in fields)})")
    conn.execute(f"INSERT INTO r ({cols}) VALUES ({marks})", tuple(fields.values()))
    row = conn.execute("SELECT * FROM r").fetchone()
    conn.close()
    return row


def _project_with_active_count(count: int) -> str | None:
    """Find a real project whose current active-authorization count is `count`."""
    conn = sqlite3.connect(REPO_ROOT / "groundtruth.db")
    try:
        rows = conn.execute(
            """SELECT project_id, SUM(status = 'active') AS live
               FROM current_project_authorizations
               GROUP BY project_id"""
        ).fetchall()
    finally:
        conn.close()
    for project_id, live in rows:
        if live == count and project_id:
            return str(project_id)
    return None


def test_denial_names_the_cited_status_and_version(auth):
    """Branch 1: the cited record's own status and version appear in the denial."""
    project_id = _project_with_active_count(1)
    if project_id is None:
        pytest.skip("no project with exactly one active authorization in the live corpus")
    row = _row(id="PAUTH-DOES-NOT-EXIST", project_id=project_id, status="revoked", version="50")
    with pytest.raises(auth.AuthorizationError) as excinfo:
        auth.validate_project_authorization_row(REPO_ROOT, row)
    message = str(excinfo.value)
    assert "PAUTH-DOES-NOT-EXIST" in message, "the denial no longer names the cited identifier"
    assert "v50" in message, (
        "the denial omits the cited version; a citation pinned to a stale version reads as "
        "correct until the version is shown"
    )
    assert "revoked" in message, (
        "the denial omits the cited status; 'not active' does not distinguish revoked from "
        "superseded, and those have different remedies"
    )


def test_denial_names_the_live_successor_with_its_version(auth):
    """Branch 2: a sole live authorization is named, WITH its version."""
    project_id = _project_with_active_count(1)
    if project_id is None:
        pytest.skip("no project with exactly one active authorization in the live corpus")
    hint = auth._live_project_authorization_refusal_hint(REPO_ROOT, project_id)
    assert project_id in hint
    assert " v" in hint, (
        "the successor is named without a version; naming the id alone was the pre-WI-7300 "
        "behaviour and is what let a stale-version citation look correct"
    )


def test_project_with_no_active_authorization_says_so_explicitly(auth):
    """Branch 3: the case that previously produced an empty hint.

    This is the branch that mattered most. A project holding no active
    authorization produced the same bare denial as a mis-citation, so an agent
    could not tell 'fix the citation' from 'stop and seek an owner decision'.
    """
    project_id = _project_with_active_count(0)
    if project_id is None:
        pytest.skip("no project without an active authorization in the live corpus")
    hint = auth._live_project_authorization_refusal_hint(REPO_ROOT, project_id)
    assert hint.strip(), "a project with no active authorization still yields an empty hint"
    assert "NO active authorization" in hint
    assert "owner decision" in hint, "the diagnostic does not tell the agent that this is not a citation error"


def test_hint_matches_a_direct_canonical_query(auth):
    """Corpus-derived: the diagnostic cannot drift from the record it describes."""
    project_id = _project_with_active_count(1)
    if project_id is None:
        pytest.skip("no project with exactly one active authorization in the live corpus")
    conn = sqlite3.connect(REPO_ROOT / "groundtruth.db")
    try:
        identifier, version = conn.execute(
            """SELECT id, version FROM current_project_authorizations
               WHERE project_id = ? AND status = 'active'""",
            (project_id,),
        ).fetchone()
    finally:
        conn.close()
    hint = auth._live_project_authorization_refusal_hint(REPO_ROOT, project_id)
    assert identifier in hint, "the diagnostic names an authorization the canonical query does not"
    assert f"v{version}" in hint, "the diagnostic reports a version the canonical query does not"


def test_the_decision_itself_is_unchanged(auth):
    """The diagnostic is additive: an inactive authorization is still refused."""
    project_id = _project_with_active_count(1) or _project_with_active_count(0)
    if project_id is None:
        pytest.skip("no project available in the live corpus")
    for status in ("revoked", "superseded", "inactive", "completed"):
        row = _row(id="PAUTH-X", project_id=project_id, status=status, version="1")
        with pytest.raises(auth.AuthorizationError):
            auth.validate_project_authorization_row(REPO_ROOT, row)
