"""Real PostgreSQL delivery rollback and complete diagnostic preservation."""

import json
import re

import pytest
from groundtruth_kb.postgres_kernel import PostgresKernelError
from psycopg import Cursor, sql

from platform_tests.groundtruth_kb.test_native_authority_service import native as native
from platform_tests.groundtruth_kb.test_native_bridge import authored, claim, deliver
from platform_tests.groundtruth_kb.test_native_bridge import bridge as bridge

pytestmark = [pytest.mark.integration, pytest.mark.timeout(120)]


def canonical_rows(service):
    """Read every table in this test's isolated schema, including history/claims."""
    with service.kernel.transaction(read_only=True) as tx:
        tx.cursor.execute(
            "SELECT table_name FROM information_schema.tables "
            "WHERE table_schema=%s AND table_type='BASE TABLE' ORDER BY table_name",
            (tx.schema,),
        )
        names = [row["table_name"] for row in tx.cursor.fetchall()]
        result = {}
        for name in names:
            tx.cursor.execute(sql.SQL("SELECT * FROM {}.{}").format(sql.Identifier(tx.schema), sql.Identifier(name)))
            result[name] = sorted(json.dumps(row, sort_keys=True, default=str) for row in tx.cursor.fetchall())
        return result


def file_bytes(root):
    return {str(path.relative_to(root)): path.read_bytes() for path in root.rglob("*") if path.is_file()}


@pytest.mark.parametrize("status", ["NEW", "REVISED", "VERIFIED"])
@pytest.mark.parametrize("failure", ["connection", "validation"])
@pytest.mark.parametrize(
    "table,event",
    [
        ("bridge_items", "INSERT"),
        ("bridge_attempts", "UPDATE"),
        ("work_intent_claims", "DELETE"),
    ],
)
def test_storage_failure_rolls_back_whole_delivery_and_same_claim_retries(
    bridge,
    monkeypatch,
    status,
    table,
    event,
    failure,
):
    service, client, contexts, root = bridge
    document = "transaction-fault"
    extra = {}
    if status in {"REVISED", "VERIFIED"}:
        deliver(client, contexts, document, "pb1", 1, "NEW")
        if status == "VERIFIED":
            deliver(client, contexts, document, "lo1", 2, "GO")
            (root / "code.py").write_text("value = 2\n", encoding="utf-8")
            deliver(client, contexts, document, "pb2", 3, "READY")
            extra["verified_artifacts"] = json.dumps(client.get(f"/v1/bridge/{document}/artifacts").json())
            context, version = "lo2", 4
        else:
            deliver(client, contexts, document, "lo1", 2, "NO-GO")
            context, version = "pb2", 3
    else:
        context, version = "pb1", 1
    reserved = claim(client, document, context, version - 1, status)
    assert reserved.status_code == 200, reserved.text
    request = {
        "native_context_id": context,
        "fence": reserved.json()["fence"],
        "content": authored(contexts[context], document, version, status, **extra),
    }
    before, files_before = canonical_rows(service), file_bytes(root)
    real_execute = Cursor.execute
    triggered = []

    def execute_then_fail(cursor, query, *args, **kwargs):
        statement = query.as_string(cursor.connection) if isinstance(query, sql.Composable) else str(query)
        result = real_execute(cursor, query, *args, **kwargs)
        if statement.startswith(event) and re.search(rf'\."?{table}"?(?:\s|$)', statement):
            triggered.append(statement)
            if failure == "validation":
                raise PostgresKernelError("post_update_validation_failed", "Refuse the incomplete delivery")
            # Terminate this exact test transaction after its real write completed.
            # No schema change or schema-validation bypass is required.
            return real_execute(cursor, "SELECT pg_terminate_backend(pg_backend_pid())")
        return result

    with monkeypatch.context() as injected:
        injected.setattr(Cursor, "execute", execute_then_fail)
        result = client.post(f"/v1/bridge/{document}/deliver", json=request)
    assert len(triggered) == 1
    assert result.status_code == (503 if failure == "connection" else 422), result.text
    assert result.json()["error"]["code"] == (
        "postgres_operation_failed" if failure == "connection" else "post_update_validation_failed"
    )
    assert canonical_rows(service) == before
    assert file_bytes(root) == files_before
    assert (
        client.get(
            f"/v1/bridge/{document}/delivery",
            params={
                "version": version,
                "native_context_id": context,
            },
        ).json()["error"]["code"]
        == "bridge_delivery_incomplete"
    )
    assert (
        client.post(
            f"/v1/bridge/{document}/check",
            json={
                "native_context_id": context,
                "fence": request["fence"],
            },
        ).status_code
        == 200
    )
    assert canonical_rows(service) == before
    delivered = client.post(f"/v1/bridge/{document}/deliver", json=request)
    assert delivered.status_code == 200, delivered.text
    final = canonical_rows(service)
    retry = client.post(f"/v1/bridge/{document}/deliver", json=request)
    assert retry.status_code == 200 and retry.json()["status"] == "already_delivered"
    assert canonical_rows(service) == final
    assert file_bytes(root) == files_before


def test_native_diagnostics_preserve_every_canonical_row_claim_and_file(bridge, tmp_path):
    service, client, contexts, root = bridge
    document = "read-only-diagnostics"
    deliver(client, contexts, document, "pb1", 1, "NEW")
    reserved = claim(client, document, "lo1", 1, "GO")
    assert reserved.status_code == 200
    registry = tmp_path / "config/registry/sot-artifacts.toml"
    registry.parent.mkdir(parents=True, exist_ok=True)
    registry.write_text("# Preserve unrelated canonical declaration bytes.\n", encoding="utf-8")
    before, files_before = canonical_rows(service), file_bytes(tmp_path)
    for _ in range(2):
        for endpoint, params in [
            ("/v1/status", {}),
            ("/v1/registry/path-observations", {}),
            ("/v1/bridge/state-report", {}),
            ("/v1/bridge/queue", {"role": "pb"}),
            ("/v1/bridge/queue", {"role": "lo"}),
            (f"/v1/bridge/{document}/show", {"include_content": "true"}),
            (f"/v1/bridge/{document}/artifacts", {}),
            (f"/v1/bridge/{document}/delivery", {"version": 1, "native_context_id": "pb1"}),
        ]:
            result = client.get(endpoint, params=params)
            assert result.status_code == 200, (endpoint, result.text)
        assert canonical_rows(service) == before
        assert file_bytes(tmp_path) == files_before
