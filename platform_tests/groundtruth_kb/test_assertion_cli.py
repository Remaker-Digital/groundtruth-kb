"""Ordinary assertion observations use the selected authority without writes."""

from __future__ import annotations

import json
import sqlite3

import pytest
from click.testing import CliRunner
from groundtruth_kb import assertions
from groundtruth_kb.authority_client import AuthorityClient, AuthorityClientError
from groundtruth_kb.cli import main
from groundtruth_kb.db import KnowledgeDB
from psycopg import sql

from platform_tests.groundtruth_kb.test_native_authority_service import native as native
from platform_tests.groundtruth_kb.test_native_authority_service import put

pytestmark = [pytest.mark.integration, pytest.mark.timeout(120)]


@pytest.fixture(params=["sqlite", "native"])
def assertion_source(request, monkeypatch, tmp_path):
    for name in ("GT_DB_PATH", "GT_PROJECT_ROOT", "GT_AUTHORITY_URL"):
        monkeypatch.delenv(name, raising=False)
    (tmp_path / "effect.py").write_text("value = 1\n", encoding="utf-8")
    database = tmp_path / "selected.db"
    config = tmp_path / "groundtruth.toml"
    settings = '[groundtruth]\ndb_path = "selected.db"\nproject_root = "."\n'
    calls = []
    if request.param == "sqlite":
        with sqlite3.connect(database) as connection:
            connection.execute(
                "CREATE TABLE specifications (id TEXT, version INTEGER, title TEXT, status TEXT, "
                "assertions TEXT, constraints TEXT, priority TEXT)"
            )
            connection.execute(
                "CREATE VIEW current_specifications AS SELECT s.* FROM specifications s "
                "JOIN (SELECT id,MAX(version) version FROM specifications GROUP BY id) h USING (id,version)"
            )

        def record(ident, fields, version=0):
            with sqlite3.connect(database) as connection:
                connection.execute(
                    "INSERT INTO specifications VALUES (?,?,?,?,?,?,?)",
                    (
                        ident,
                        version + 1,
                        fields["title"],
                        fields.get("status", "active"),
                        json.dumps(fields.get("assertions")),
                        json.dumps(fields.get("constraints")),
                        "P1",
                    ),
                )

        def snapshot():
            with sqlite3.connect(database) as connection:
                return (
                    list(connection.iterdump()),
                    connection.execute("PRAGMA user_version").fetchone(),
                    database.read_bytes(),
                )

    else:
        service, client, _, _ = request.getfixturevalue("native")
        settings += 'authority_url = "http://127.0.0.1:8765"\n'

        def transport(_self, method, path, *, body=None, query=None):
            calls.append((method, path))
            result = client.request(
                method, path, json=body, params={k: v for k, v in (query or {}).items() if v is not None}
            )
            if result.status_code >= 400:
                error = result.json()["error"]
                raise AuthorityClientError(error["code"], error["message"], details=error.get("details"))
            return result.json()

        monkeypatch.setattr(AuthorityClient, "request", transport)

        def record(ident, fields, version=0):
            response = put(client, "specifications", ident, fields, expected_version=version)
            assert response.status_code == 200, response.text

        def snapshot():
            with service.kernel.transaction(read_only=True) as tx:
                tx.cursor.execute(
                    "SELECT tablename FROM pg_tables WHERE schemaname=%s ORDER BY tablename", (tx.schema,)
                )
                tables = [r["tablename"] for r in tx.cursor.fetchall()]
                counts = {}
                for name in tables:
                    tx.cursor.execute(
                        sql.SQL("SELECT COUNT(*) AS n FROM {}.{}").format(
                            sql.Identifier(tx.schema), sql.Identifier(name)
                        )
                    )
                    counts[name] = tx.cursor.fetchone()["n"]
                return counts, tx.list("specifications", limit=1000), database.exists()

    config.write_text(settings, encoding="utf-8")
    return config, record, snapshot, calls


@pytest.mark.parametrize("behavior_required", [False, True])
def test_cli_observes_current_definitions_without_recording_or_schema_bootstrap(assertion_source, behavior_required):
    config, record, snapshot, calls = assertion_source
    fields = {
        "title": "Current effect",
        "status": "active",
        "assertions": [{"type": "file_exists", "file": "effect.py"}],
    }
    if behavior_required:
        fields["constraints"] = {"behavioral_validation_required": True}
    record("SPEC-1", fields)
    record(
        "SPEC-OLD",
        {
            "title": "Inert old requirement",
            "status": "retired",
            "assertions": [{"type": "file_exists", "file": "missing.py"}],
        },
    )
    before = snapshot()
    result = CliRunner().invoke(main, ["--config", str(config), "assert", "--json"])
    assert result.exit_code == (1 if behavior_required else 0), result.output
    report = json.loads(result.output)
    assert report["aggregate_result"] == ("PARTIAL" if behavior_required else "PASS")
    assert report["total_specs"] == 1
    assert report["details"][0]["spec_version"] == 1
    assert snapshot() == before
    assert all(method == "GET" for method, _ in calls)
    retired = CliRunner().invoke(main, ["--config", str(config), "assert", "--spec", "SPEC-OLD", "--json"])
    assert retired.exit_code == 1
    assert json.loads(retired.output)["aggregate_result"] == "NOT_APPLICABLE"
    assert snapshot() == before


def test_changed_canonical_definition_invalidates_an_earlier_passing_observation(assertion_source, monkeypatch):
    config, record, _, _ = assertion_source
    record(
        "SPEC-1",
        {"title": "Original effect", "status": "active", "assertions": [{"type": "file_exists", "file": "effect.py"}]},
    )
    original = assertions._RUNNERS["file_exists"]

    def change_while_checking(definition, context):
        record(
            "SPEC-1",
            {
                "title": "Changed requirement",
                "status": "active",
                "assertions": [{"type": "file_exists", "file": "missing.py"}],
            },
            version=1,
        )
        return original(definition, context)

    monkeypatch.setitem(assertions._RUNNERS, "file_exists", change_while_checking)
    result = CliRunner().invoke(main, ["--config", str(config), "assert", "--spec", "SPEC-1", "--json"])
    assert result.exit_code == 1, result.output
    report = json.loads(result.output)
    assert report["aggregate_result"] == "UNASSESSED"
    detail = report["details"][0]
    assert detail["spec_version"] == 1 and not detail["overall_passed"]
    assert detail["results"][-1]["type"] == "source_changed"


def test_read_only_database_refuses_writes_and_does_not_create_a_missing_source(tmp_path):
    path = tmp_path / "source.db"
    with sqlite3.connect(path) as connection:
        connection.execute("CREATE TABLE retained (value TEXT)")
    before = path.read_bytes()
    db = KnowledgeDB(path, read_only=True)
    try:
        assert db._get_conn().execute("PRAGMA user_version").fetchone()[0] == 0
        with pytest.raises(sqlite3.OperationalError, match="readonly"):
            db._get_conn().execute("INSERT INTO retained VALUES ('unwanted')")
    finally:
        db.close()
    assert path.read_bytes() == before
    missing = tmp_path / "absent.db"
    db = KnowledgeDB(missing, read_only=True)
    try:
        with pytest.raises(sqlite3.OperationalError):
            db.get_spec("SPEC-1")
    finally:
        db.close()
    assert not missing.exists()


def test_unavailable_native_authority_does_not_fall_back_to_sqlite(assertion_source, monkeypatch):
    config, record, snapshot, _ = assertion_source
    if "authority_url" not in config.read_text(encoding="utf-8"):
        pytest.skip("This refusal concerns the native authority selection")
    record("SPEC-1", {"title": "Effect", "status": "active"})
    before = snapshot()

    def unavailable(*args, **kwargs):
        raise AuthorityClientError("authority_unavailable", "Service unavailable")

    monkeypatch.setattr(AuthorityClient, "request", unavailable)
    result = CliRunner().invoke(main, ["--config", str(config), "assert", "--spec", "SPEC-1", "--json"])
    assert result.exit_code == 1 and "authority_unavailable" in result.output
    assert snapshot() == before
