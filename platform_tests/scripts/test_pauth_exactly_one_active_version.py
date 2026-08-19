# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""WI-6453: exactly one active project_authorizations row per id after insert."""

from __future__ import annotations

import json
from pathlib import Path

from groundtruth_kb.db import KnowledgeDB


def _seed(db: KnowledgeDB) -> None:
    db.insert_deliberation(
        "DELIB-WI6453-OWNER",
        "owner_conversation",
        "Owner approved isolated PAUTH insert fixture",
        "Owner approved the WI-6453 isolated insert fixture.",
        "{}",
        "test",
        "seed owner decision",
        outcome="owner_decision",
    )
    db.insert_spec(
        "SPEC-WI6453", "WI-6453 fixture spec", "specified", "test", "seed spec"
    )
    db.insert_project(
        "WI-6453 Isolated Auth Project",
        "test",
        "create project",
        id="PROJECT-WI6453",
        status="active",
    )


def _base_rows(db: KnowledgeDB, authorization_id: str) -> list[dict[str, object]]:
    conn = db._get_conn()
    rows = conn.execute(
        """SELECT version, status, superseded_by, forbidden_operations
           FROM project_authorizations
           WHERE id = ?
           ORDER BY version""",
        (authorization_id,),
    ).fetchall()
    return [dict(row) for row in rows]


def test_second_active_insert_supersedes_prior_row_only(tmp_path: Path) -> None:
    db = KnowledgeDB(tmp_path / "groundtruth.db")
    try:
        _seed(db)
        first = db.insert_project_authorization(
            "PROJECT-WI6453",
            "WI-6453 isolated authorization",
            "DELIB-WI6453-OWNER",
            "Implement the authorized project membership.",
            "test",
            "first active insert",
            id="PAUTH-WI6453-ISOLATED",
            status="active",
            included_spec_ids=["SPEC-WI6453"],
            forbidden_operations=["git_commit"],
        )
        assert first is not None
        assert first["version"] == 1
        v1_forbidden = _base_rows(db, "PAUTH-WI6453-ISOLATED")[0][
            "forbidden_operations"
        ]

        second = db.insert_project_authorization(
            "PROJECT-WI6453",
            "WI-6453 isolated authorization",
            "DELIB-WI6453-OWNER",
            "Implement the authorized project membership.",
            "test",
            "second active insert",
            id="PAUTH-WI6453-ISOLATED",
            status="active",
            included_spec_ids=["SPEC-WI6453"],
            forbidden_operations=["git_push"],
        )
        assert second is not None
        assert second["version"] == 2
        assert second["status"] == "active"

        rows = _base_rows(db, "PAUTH-WI6453-ISOLATED")
        assert len(rows) == 2
        active = [row for row in rows if row["status"] == "active"]
        assert len(active) == 1
        assert active[0]["version"] == 2

        prior = rows[0]
        assert prior["version"] == 1
        assert prior["status"] == "superseded"
        assert json.loads(str(prior["superseded_by"])) == ["PAUTH-WI6453-ISOLATED"]
        assert prior["forbidden_operations"] == v1_forbidden
        assert json.loads(str(prior["forbidden_operations"])) == ["git_commit"]

        current = db.get_project_authorization("PAUTH-WI6453-ISOLATED")
        assert current is not None
        assert current["version"] == 2
        assert current["status"] == "active"
    finally:
        db.close()
