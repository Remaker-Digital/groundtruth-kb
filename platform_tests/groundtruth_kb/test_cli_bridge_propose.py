"""Proposal obligations survive retirement of the file-generation services.

Exercise the native delivery boundary: authored identity and linkage, concrete
artifact paths, exact claims and terminal work. No legacy registry or helper is
an input to these scenarios.
"""

from __future__ import annotations

import json

import pytest
from psycopg import sql
from psycopg.types.json import Jsonb

from platform_tests.groundtruth_kb.test_native_authority_service import native as native
from platform_tests.groundtruth_kb.test_native_bridge import authored, claim, deliver
from platform_tests.groundtruth_kb.test_native_bridge import bridge as bridge

pytestmark = [pytest.mark.integration, pytest.mark.timeout(120)]


def test_proposal_refusals_preserve_exact_claim_and_authored_state(bridge):
    _, client, contexts, root = bridge
    document = "proposal-inputs"
    reserved = claim(client, document, "pb1", 0, "NEW")
    assert reserved.status_code == 200, reserved.text
    fence = reserved.json()["fence"]
    before = client.get(f"/v1/bridge/{document}/show?include_content=true").json()
    changes = [
        {"Project": "PROJECT-OTHER"},
        {"Work Item": "WI-OTHER"},
        {"Document": "another-proposal"},
        {"Version": "2"},
        {"author_harness_id": "UNREGISTERED"},
        {"author_session_context_id": contexts["pb2"]["session_context_id"]},
        {"target_paths": "[]"},
        {"test_artifact_targets": "[]"},
        {"target_paths": json.dumps(["code.py", "CODE.PY"])},
    ]
    for path in [
        "../escape.py",
        "/absolute.py",
        "E:/outside.py",
        "folder//x.py",
        "folder/./x.py",
        "folder\\x.py",
        ".GIT/config",
        "bridge/payload.md",
        ".gtkb-state/state.json",
        "harness-state/state.json",
        "scratchpad/draft.py",
        ".worktrees/another/code.py",
    ]:
        changes.append({"target_paths": json.dumps([path])})
    for fields in changes:
        response = client.post(
            f"/v1/bridge/{document}/deliver",
            json={
                "native_context_id": "pb1",
                "fence": fence,
                "content": authored(contexts["pb1"], document, 1, "NEW", **fields),
            },
        )
        expected_status = 404 if "author_harness_id" in fields else 422
        assert response.status_code == expected_status, (fields, response.text)
        assert client.get(f"/v1/bridge/{document}/show?include_content=true").json() == before
        assert (
            client.post(
                f"/v1/bridge/{document}/check",
                json={
                    "native_context_id": "pb1",
                    "fence": fence,
                },
            ).status_code
            == 200
        )
    content = authored(contexts["pb1"], document, 1, "NEW")
    response = client.post(
        f"/v1/bridge/{document}/deliver",
        json={
            "native_context_id": "pb1",
            "fence": fence,
            "content": content,
        },
    )
    assert response.status_code == 200, response.text
    state = client.get(f"/v1/bridge/{document}/show?include_content=true").json()
    assert state["messages"][0]["content"] == content
    assert not (root / "bridge").exists()
    assert not (root / "groundtruth.db").exists()


def test_proposal_cannot_target_generated_harnesses_or_retired_authority_roots(bridge):
    _, client, contexts, _ = bridge
    document = "generated-targets"
    reserved = claim(client, document, "pb1", 0, "NEW")
    assert reserved.status_code == 200, reserved.text
    fence = reserved.json()["fence"]
    before = client.get(f"/v1/bridge/{document}/show?include_content=true").json()
    paths = [
        f"{directory}/hooks/example.py"
        for directory in (
            ".agent",
            ".agents",
            ".antigravity",
            ".api-harness",
            ".claude",
            ".codex",
            ".cursor",
            ".goose",
        )
    ]
    paths += [
        "config/agent-control",
        "config/agent-control/rule.md",
        ".groundtruth/formal-artifact-approvals",
        ".groundtruth/formal-artifact-approvals/item.json",
    ]
    for path in paths:
        for field in ["target_paths", "test_artifact_targets"]:
            response = client.post(
                f"/v1/bridge/{document}/deliver",
                json={
                    "native_context_id": "pb1",
                    "fence": fence,
                    "content": authored(contexts["pb1"], document, 1, "NEW", **{field: json.dumps([path])}),
                },
            )
            assert response.status_code == 422, (path, response.text)
            assert client.get(f"/v1/bridge/{document}/show?include_content=true").json() == before
    content = authored(
        contexts["pb1"],
        document,
        1,
        "NEW",
        target_paths=json.dumps(
            [
                ".harness-baseline-configuration/rules/example.md",
            ]
        ),
    )
    response = client.post(
        f"/v1/bridge/{document}/deliver",
        json={
            "native_context_id": "pb1",
            "fence": fence,
            "content": content,
        },
    )
    assert response.status_code == 200, response.text


def test_closed_work_and_unbound_or_wrong_role_contexts_cannot_begin_proposals(bridge):
    service, client, _, _ = bridge
    for context in ["unbound", "lo1"]:
        response = claim(client, "no-implicit-role", context, 0, "NEW")
        assert response.status_code == 422, response.text
        assert client.get("/v1/bridge/no-implicit-role/show").status_code == 404
    for status in ["resolved", "retired", "wont_fix", "not_a_defect", "verified"]:
        with service.kernel.transaction() as tx:
            tx.cursor.execute(
                sql.SQL("UPDATE {}.work_items SET resolution_status=%s WHERE id='WI-1'").format(
                    sql.Identifier(tx.schema)
                ),
                (status,),
            )
        response = claim(client, "closed-work", "pb1", 0, "NEW")
        assert response.status_code == 422 and response.json()["error"]["code"] == "work_not_open", response.text
        assert client.get("/v1/bridge/closed-work/show").status_code == 404


@pytest.mark.parametrize("field", ["proposal_paths", "test_targets"])
def test_stored_forbidden_scope_cannot_reuse_a_live_effect_claim(bridge, field):
    service, client, contexts, _ = bridge
    document = "stored-invalid-scope"
    deliver(client, contexts, document, "pb1", 1, "NEW")
    deliver(client, contexts, document, "lo1", 2, "GO")
    reservation = claim(client, document, "pb2", 2, "READY")
    assert reservation.status_code == 200, reservation.text
    fence = reservation.json()["fence"]
    with service.kernel.transaction() as tx:
        tx.cursor.execute(
            sql.SQL("UPDATE {}.bridge_attempts SET {}=%s WHERE id=%s").format(
                sql.Identifier(tx.schema), sql.Identifier(field)
            ),
            (Jsonb([".codex/hooks/generated.py"]), document),
        )
    before = client.get(f"/v1/bridge/{document}/show?include_content=true").json()
    body = {"native_context_id": "pb2", "fence": fence}
    for operation in ["check", "worktree", "publish-work"]:
        request = {**body, "expected_artifacts": {}} if operation == "publish-work" else body
        response = client.post(f"/v1/bridge/{document}/{operation}", json=request)
        assert response.status_code == 422, (operation, response.text)
        assert response.json()["error"]["code"] == "scope_changed"
        assert client.get(f"/v1/bridge/{document}/show?include_content=true").json() == before
    assert client.get(f"/v1/bridge/{document}/artifacts").status_code == 422
    assert client.post(f"/v1/bridge/{document}/release", json=body).status_code == 200
    abandoned = client.post(
        f"/v1/bridge/{document}/abandon",
        json={
            "native_context_id": "lo2",
            "expected_version": 2,
            "reason": "Stored proposal targets include generated harness configuration",
        },
    )
    assert abandoned.status_code == 200, abandoned.text
    assert claim(client, "valid-successor", "pb3", 0, "READY").status_code == 422
    deliver(client, contexts, "valid-successor", "pb3", 1, "NEW")
