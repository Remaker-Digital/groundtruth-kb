"""Native publication fencing and lost-acknowledgement recovery.

The retired raw-file compensation receipts have no current API. Surviving
obligations are exact next-artifact fencing, preservation of unrelated work,
refusal of changed predecessors and idempotent delivery through the authority.
"""

from __future__ import annotations

import pytest
from psycopg import sql

from platform_tests.groundtruth_kb.test_native_authority_service import native as native
from platform_tests.groundtruth_kb.test_native_authority_service import put, work_fields
from platform_tests.groundtruth_kb.test_native_bridge import authored, claim, deliver
from platform_tests.groundtruth_kb.test_native_bridge import bridge as bridge

pytestmark = [pytest.mark.integration, pytest.mark.timeout(120)]


def _state(client, document):
    response = client.get(f"/v1/bridge/{document}/show", params={"include_content": True})
    assert response.status_code == 200, response.text
    return response.json()


def _go_claim(client, contexts):
    deliver(client, contexts, "target", "pb1", 1, "NEW")
    reserved = claim(client, "target", "lo1", 1, "GO")
    assert reserved.status_code == 200, reserved.text
    request = {
        "native_context_id": "lo1",
        "fence": reserved.json()["fence"],
        "content": authored(contexts["lo1"], "target", 2, "GO"),
    }
    return request


def test_unrelated_thread_append_does_not_invalidate_exact_delivery(bridge):
    _, client, contexts, _ = bridge
    request = _go_claim(client, contexts)
    assert put(client, "work-items", "WI-2", work_fields(), project_id="PROJECT-1").status_code == 200
    deliver(client, contexts, "unrelated", "pb2", 1, "NEW", work_item_id="WI-2")
    foreign = _state(client, "unrelated")
    response = client.post("/v1/bridge/target/deliver", json=request)
    assert response.status_code == 200, response.text
    assert _state(client, "unrelated") == foreign
    assert _state(client, "target")["messages"][-1]["content"] == request["content"]


def test_lost_acknowledgement_retry_preserves_successor_and_its_claim(bridge):
    _, client, contexts, _ = bridge
    _, original = deliver(client, contexts, "target", "pb1", 1, "NEW")
    deliver(client, contexts, "target", "lo1", 2, "GO")
    reserved = claim(client, "target", "pb2", 2, "READY")
    assert reserved.status_code == 200, reserved.text
    fence = {"native_context_id": "pb2", "fence": reserved.json()["fence"]}
    before = _state(client, "target")
    response = client.post("/v1/bridge/target/deliver", json=original)
    assert response.status_code == 200 and response.json()["status"] == "already_delivered"
    assert _state(client, "target") == before
    assert client.post("/v1/bridge/target/check", json=fence).status_code == 200


@pytest.mark.parametrize("changed", ["content", "fence"])
def test_retry_mismatch_cannot_replace_the_delivered_artifact(bridge, changed):
    _, client, contexts, _ = bridge
    _, request = deliver(client, contexts, "target", "pb1", 1, "NEW")
    before = _state(client, "target")
    request = dict(request)
    request[changed] += "Changed body." if changed == "content" else 1
    response = client.post("/v1/bridge/target/deliver", json=request)
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "bridge_version_collision"
    assert _state(client, "target") == before


def test_changed_predecessor_refuses_without_consuming_claim_or_rewriting_content(bridge):
    service, client, contexts, _ = bridge
    request = _go_claim(client, contexts)
    with service.kernel.transaction() as tx:
        tx.cursor.execute(
            sql.SQL("UPDATE {}.bridge_items SET content=content || 'changed' WHERE attempt_id='target'").format(
                sql.Identifier(tx.schema)
            )
        )
    before = _state(client, "target")
    response = client.post("/v1/bridge/target/deliver", json=request)
    assert response.status_code == 422 and response.json()["error"]["code"] == "stale_bridge_head"
    assert _state(client, "target") == before
    with service.kernel.transaction(read_only=True) as tx:
        tx.cursor.execute(
            sql.SQL("SELECT fence FROM {}.work_intent_claims WHERE attempt_id='target'").format(
                sql.Identifier(tx.schema)
            )
        )
        assert tx.cursor.fetchone()["fence"] == request["fence"]


def test_expired_claim_cannot_consume_replacement_contexts_artifact_slot(bridge):
    service, client, contexts, _ = bridge
    request = _go_claim(client, contexts)
    with service.kernel.transaction() as tx:
        tx.cursor.execute(
            sql.SQL(
                "UPDATE {}.work_intent_claims SET expires_at=clock_timestamp()-interval '1 second' WHERE attempt_id='target'"
            ).format(sql.Identifier(tx.schema))
        )
    successor = claim(client, "target", "lo2", 1, "GO")
    assert successor.status_code == 200, successor.text
    before = _state(client, "target")
    response = client.post("/v1/bridge/target/deliver", json=request)
    assert response.status_code == 422 and response.json()["error"]["code"] == "stale_artifact_fence"
    assert _state(client, "target") == before
    assert (
        client.post(
            "/v1/bridge/target/check", json={"native_context_id": "lo2", "fence": successor.json()["fence"]}
        ).status_code
        == 200
    )
