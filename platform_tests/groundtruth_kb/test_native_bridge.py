"""Native bridge state-machine qualification with fresh independent contexts."""

from __future__ import annotations

import json
import subprocess
from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime
from pathlib import Path
from threading import Barrier
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from groundtruth_kb.authority_api import create_authority_app
from groundtruth_kb.bridge.native import BindSession, NativeBridgeService
from groundtruth_kb.bridge.vocabulary import LOYAL_OPPOSITION_ACTIONABLE_STATUSES, PRIME_ACTIONABLE_STATUSES
from groundtruth_kb.postgres_kernel import TABLE_SPECS
from psycopg import sql

from platform_tests.groundtruth_kb.test_native_authority_service import native as native
from platform_tests.groundtruth_kb.test_native_authority_service import put, seed, work_fields

pytestmark = [pytest.mark.integration, pytest.mark.timeout(120)]


@pytest.fixture
def bridge(native, tmp_path):
    service, _, _, _ = native
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True, capture_output=True)
    (tmp_path / "tests").mkdir()
    (tmp_path / "code.py").write_text("value = 1\n", encoding="utf-8")
    (tmp_path / "second.py").write_text("second = 1\n", encoding="utf-8")
    (tmp_path / "foreign_tracked.txt").write_text("Original unrelated content\n", encoding="utf-8")
    (tmp_path / ".gitignore").write_text(".worktrees/\n", encoding="utf-8")
    (tmp_path / "tests/test_effect.py").write_text("def test_effect(): assert 1 == 1\n", encoding="utf-8")
    for arguments in (
        ["config", "user.name", "Qualification"],
        ["config", "user.email", "qualification@example.invalid"],
        ["add", "--", "code.py", "second.py", "tests/test_effect.py", ".gitignore", "foreign_tracked.txt"],
        ["commit", "-qm", "Isolated qualification preimage"],
    ):
        subprocess.run(["git", "-C", str(tmp_path), *arguments], check=True, capture_output=True)
    row = {column: None for column in TABLE_SPECS["harnesses"].columns}
    row.update(
        id="HARNESS-1",
        version=1,
        harness_name="qualification",
        harness_type="test",
        status="registered",
        changed_at=datetime.now(UTC).isoformat(),
        changed_by="qualification",
        change_reason="Isolated harness",
    )
    service.kernel.mutate_current(
        table="harnesses",
        identity={"id": row["id"]},
        expected_version=0,
        new_state=row,
        actor="qualification",
        reason="Test setup",
    )
    with TestClient(create_authority_app(service, project_root=tmp_path)) as client:
        seed(client)
        assert put(client, "work-items", "WI-1", work_fields(), project_id="PROJECT-1").status_code == 200
        contexts = {}
        for name in ("pb1", "lo1", "pb2", "lo2", "pb3", "lo3"):
            result = client.post(
                "/v1/sessions/bind", json={"native_context_id": name, "init_command": f"::init gtkb {name[:2]}"}
            )
            assert result.status_code == 200, result.text
            contexts[name] = result.json()
        work_root = NativeBridgeService(service.kernel, tmp_path).work_root("PROJECT-1")
        yield service, client, contexts, work_root


def authored(context, document, version, status, **extra):
    receiver = (
        "pb"
        if status in PRIME_ACTIONABLE_STATUSES
        else "lo"
        if status in LOYAL_OPPOSITION_ACTIONABLE_STATUSES
        else None
    )
    lines = [f"::init gtkb {receiver}", "::open build", status] if receiver else [status]
    kind = (
        "implementation_proposal"
        if status in {"NEW", "REVISED"}
        else "implementation_report"
        if status == "READY"
        else "lo_verdict"
    )
    fields = {
        "bridge_kind": kind,
        "Document": document,
        "Version": str(version),
        "Date": datetime.now(UTC).date().isoformat(),
        "author_identity": "qualified-agent",
        "author_harness_id": "HARNESS-1",
        "author_session_context_id": context["session_context_id"],
        "author_model": "qualification-model",
        "Project": "PROJECT-1",
        "Work Item": "WI-1",
    }
    if status == "ADVISORY":
        fields["bridge_kind"] = "governance_advisory"
    elif status in {"WITHDRAWN", "BLOCKED"}:
        fields["bridge_kind"] = "operational_state_change"
    elif status == "VERDICT-REJECTED":
        fields["bridge_kind"] = "governance_review"
    if receiver:
        fields["recipient_role"] = {"pb": "prime-builder", "lo": "loyal-opposition"}[receiver]
    if status in {"NEW", "REVISED"}:
        fields.update(
            target_paths=json.dumps(["code.py"]),
            test_artifact_targets=json.dumps(["tests/test_effect.py"]),
            spec_ids=json.dumps(["SPEC-1"]),
        )
    fields.update(extra)
    return "\r\n".join(
        [*lines, *(f"{key}: {value}" for key, value in fields.items()), "", "Authored content: café 漢字.", ""]
    )


def claim(client, document, context, version, status, *, work_item_id="WI-1", request_id=None):
    return client.post(
        f"/v1/bridge/{document}/claim",
        json={
            "native_context_id": context,
            "work_item_id": work_item_id,
            "expected_version": version,
            "intended_status": status,
            "request_id": request_id or str(uuid4()),
        },
    )


def deliver(client, contexts, document, context, version, status, *, work_item_id="WI-1", **extra):
    reserved = claim(client, document, context, version - 1, status, work_item_id=work_item_id)
    assert reserved.status_code == 200, reserved.text
    content = authored(contexts[context], document, version, status, **{"Work Item": work_item_id, **extra})
    request = {"native_context_id": context, "fence": reserved.json()["fence"], "content": content}
    result = client.post(f"/v1/bridge/{document}/deliver", json=request)
    assert result.status_code == 200, result.text
    return result, request


def test_binding_is_immutable_exact_and_retry_idempotent(bridge):
    service, client, contexts, root = bridge
    request = {"native_context_id": "pb1", "init_command": "::init gtkb pb\n::init gtkb pb"}
    again = client.post("/v1/sessions/bind", json=request)
    assert again.status_code == 200 and again.json() == contexts["pb1"]
    for marker in ("::init gtkb lo", "::init gtkb pb\n::init gtkb lo", " ::init gtkb pb", "::init gtkb"):
        result = client.post("/v1/sessions/bind", json={**request, "init_command": marker})
        assert result.status_code == 422
    native_service = NativeBridgeService(service.kernel, root)
    with ThreadPoolExecutor(max_workers=2) as workers:
        bound = list(
            workers.map(
                lambda _: native_service.bind(
                    BindSession(native_context_id="concurrent", init_command="::init gtkb lo")
                ),
                range(2),
            )
        )
    assert bound[0] == bound[1]
    # Ending a worker process does not delete its immutable role binding or
    # allow that same native context to reinitialize as its own reviewer.
    assert client.post("/v1/sessions/retire", json={"native_context_id": "pb1"}).status_code in {404, 405}
    assert client.get("/v1/sessions/binding", params={"native_context_id": "pb1"}).json() == contexts["pb1"]
    assert (
        client.post(
            "/v1/sessions/bind", json={"native_context_id": "pb1", "init_command": "::init gtkb lo"}
        ).status_code
        == 422
    )


def test_fresh_context_chain_preserves_bytes_consumes_claims_and_verifies(bridge):
    service, client, contexts, root = bridge
    result, new_request = deliver(client, contexts, "chain", "pb1", 1, "NEW")
    retry = client.post("/v1/bridge/chain/deliver", json=new_request)
    assert retry.status_code == 200 and retry.json()["status"] == "already_delivered"
    queue = client.get("/v1/bridge/queue", params={"role": "lo"}).json()
    assert [row["id"] for row in queue["eligible"]] == ["chain"]
    reserved = claim(client, "chain", "lo1", 1, "GO").json()
    assert reserved["predecessor"]["content"] == new_request["content"]
    go = {
        "native_context_id": "lo1",
        "fence": reserved["fence"],
        "content": authored(contexts["lo1"], "chain", 2, "GO"),
    }
    assert client.post("/v1/bridge/chain/deliver", json=go).status_code == 200
    ready_claim = claim(client, "chain", "pb2", 2, "READY").json()
    fence = {"native_context_id": "pb2", "fence": ready_claim["fence"]}
    assert client.post("/v1/bridge/chain/check", json=fence).json()["target_paths"] == [
        "code.py",
        "tests/test_effect.py",
    ]
    (root / "code.py").write_text("value = 2\n", encoding="utf-8")
    ready = {**fence, "content": authored(contexts["pb2"], "chain", 3, "READY")}
    assert client.post("/v1/bridge/chain/deliver", json=ready).status_code == 200
    assert client.post("/v1/bridge/chain/check", json=fence).status_code == 422
    artifacts = client.get("/v1/bridge/chain/artifacts").json()
    verified, _ = deliver(client, contexts, "chain", "lo2", 4, "VERIFIED", verified_artifacts=json.dumps(artifacts))
    assert verified.json()["project_ready_for_commit"] is True
    assert client.get("/v1/work-items/WI-1").json()["work_item"]["resolution_status"] == "verified"
    assert client.get("/v1/projects/PROJECT-1").json()["project"]["status"] == "active"
    assert client.get("/v1/bridge/queue", params={"role": "lo"}).json()["eligible"] == []
    with service.kernel.transaction(read_only=True) as tx:
        tx.cursor.execute(sql.SQL("SELECT count(*) AS n FROM {}.work_intent_claims").format(sql.Identifier(tx.schema)))
        assert tx.cursor.fetchone()["n"] == 0
        tx.cursor.execute(
            sql.SQL(
                "SELECT count(*) AS n FROM {}.record_history WHERE record_type LIKE 'bridge%' "
                "OR record_type='work_intent_claims'"
            ).format(sql.Identifier(tx.schema))
        )
        assert tx.cursor.fetchone()["n"] == 0


def test_scoped_publication_preserves_local_work_and_supports_a_fresh_successor(bridge):
    service, client, contexts, root = bridge
    deliver(client, contexts, "chain", "pb1", 1, "NEW")
    deliver(client, contexts, "chain", "lo1", 2, "GO")
    reserved = claim(client, "chain", "pb2", 2, "READY").json()
    fence = {"native_context_id": "pb2", "fence": reserved["fence"]}
    opened = client.post("/v1/bridge/chain/worktree", json=fence).json()
    own = Path(opened["path"])
    (own / "code.py").write_text("value = 2\n", encoding="utf-8")
    (own / "foreign_tracked.txt").write_text("Private unrelated work\n", encoding="utf-8")
    refused = client.post("/v1/bridge/chain/worktree", json=fence)
    assert refused.json()["error"]["code"] == "checkout_has_local_work"
    assert (own / "code.py").read_text() == "value = 2\n"
    body = {**fence, "expected_artifacts": opened["artifact_preimages"]}
    published = client.post("/v1/bridge/chain/publish-work", json=body)
    assert published.status_code == 200, published.text
    assert client.post("/v1/bridge/chain/publish-work", json=body).json() == published.json()
    assert (root / "foreign_tracked.txt").read_text() == "Original unrelated content\n"
    (root / "tests/test_effect.py").write_text("def test_effect(): assert 2 == 2\n", encoding="utf-8")
    refused = client.post("/v1/bridge/chain/publish-work", json=body)
    assert refused.json()["error"]["code"] == "artifact_preimage_changed"
    (own / "code.py").write_text("Unpublished prior-context edit\n", encoding="utf-8")
    with service.kernel.transaction() as tx:
        tx.cursor.execute(
            sql.SQL(
                "UPDATE {}.work_intent_claims SET expires_at=clock_timestamp()-interval '1 second' WHERE attempt_id='chain'"
            ).format(sql.Identifier(tx.schema))
        )
    assert client.post("/v1/bridge/chain/publish-work", json=body).json()["error"]["code"] == "stale_artifact_fence"
    successor = claim(client, "chain", "pb3", 2, "READY").json()
    loaded = client.post(
        "/v1/bridge/chain/worktree", json={"native_context_id": "pb3", "fence": successor["fence"]}
    ).json()
    fresh = Path(loaded["path"])
    assert fresh != own
    assert (fresh / "code.py").read_text() == "value = 2\n"
    assert (fresh / "tests/test_effect.py").read_text() == "def test_effect(): assert 2 == 2\n"
    assert (fresh / "foreign_tracked.txt").read_text() == "Original unrelated content\n"
    assert (own / "code.py").read_text() == "Unpublished prior-context edit\n"


@pytest.mark.parametrize("next_status", ["GO", "READY", "VERIFIED"])
@pytest.mark.parametrize("changed_scope", ["work", "formal", "parent"])
@pytest.mark.parametrize("claim_before_change", [False, True])
def test_claim_operations_reject_changed_scope_without_consuming_the_reservation(
    bridge, next_status, changed_scope, claim_before_change
):
    service, client, contexts, root = bridge
    chain = [("pb1", "NEW"), ("lo1", "GO"), ("pb2", "READY"), ("lo2", "VERIFIED")]
    for version, (context, status) in enumerate(chain, 1):
        if status == next_status:
            break
        deliver(client, contexts, "chain", context, version, status)
    head_version = version - 1
    request_id = str(uuid4())
    reserved = None
    if claim_before_change:
        granted = claim(client, "chain", context, head_version, next_status, request_id=request_id)
        assert granted.status_code == 200, granted.text
        reserved = granted.json()

    if changed_scope == "work":
        changed = put(client, "work-items", "WI-1", {"description": "A different required effect"}, expected_version=1)
    elif changed_scope == "formal":
        changed = put(client, "specifications", "SPEC-1", {"description": "Changed formal intent"}, expected_version=1)
    else:
        assert put(client, "projects", "PROJECT-2", {"name": "Different complete outcome"}).status_code == 200
        membership = client.get("/v1/work-items/WI-1").json()["membership"]
        changed = client.post(
            "/v1/work-items/WI-1/move",
            json={
                "expected_version": membership["version"],
                "source_project_id": "PROJECT-1",
                "destination_project_id": "PROJECT-2",
                "actor": "qualification",
                "reason": "Current parent changes during an unfinished attempt",
            },
        )
    assert changed.status_code == 200, changed.text
    with service.kernel.transaction(read_only=True) as tx:
        tx.cursor.execute(
            sql.SQL("SELECT * FROM {}.bridge_attempts WHERE id='chain'").format(sql.Identifier(tx.schema))
        )
        attempt_before = dict(tx.cursor.fetchone())
        tx.cursor.execute(sql.SQL("SELECT * FROM {}.work_intent_claims").format(sql.Identifier(tx.schema)))
        claims_before = list(tx.cursor.fetchall())

    responses = {
        "claim": claim(client, "chain", context, head_version, next_status, request_id=request_id),
    }
    checkouts_before = set(root.parent.parent.glob("SENV-*"))
    if reserved:
        fence = {"native_context_id": context, "fence": reserved["fence"]}
        responses.update(
            {operation: client.post(f"/v1/bridge/chain/{operation}", json=fence) for operation in ("check", "worktree")}
        )
        responses["deliver"] = client.post(
            "/v1/bridge/chain/deliver",
            json={**fence, "content": authored(contexts[context], "chain", version, next_status)},
        )
    assert {
        name: (result.status_code, result.json().get("error", {}).get("code")) for name, result in responses.items()
    } == {name: (422, "scope_changed") for name in responses}
    assert set(root.parent.parent.glob("SENV-*")) == checkouts_before
    with service.kernel.transaction(read_only=True) as tx:
        tx.cursor.execute(
            sql.SQL("SELECT * FROM {}.bridge_attempts WHERE id='chain'").format(sql.Identifier(tx.schema))
        )
        assert dict(tx.cursor.fetchone()) == attempt_before
        tx.cursor.execute(sql.SQL("SELECT * FROM {}.work_intent_claims").format(sql.Identifier(tx.schema)))
        assert list(tx.cursor.fetchall()) == claims_before
    if reserved:
        released = client.post("/v1/bridge/chain/release", json=fence)
        assert released.status_code == 200 and released.json()["status"] == "released"
        assert claim(client, "chain", context, head_version, next_status).json()["error"]["code"] == "scope_changed"


def test_changed_scope_can_be_rejected_and_revised_without_reusing_the_old_proposal(bridge):
    _, client, contexts, _ = bridge
    deliver(client, contexts, "chain", "pb1", 1, "NEW")
    changed = put(client, "work-items", "WI-1", {"description": "Corrected required effect"}, expected_version=1)
    assert changed.status_code == 200, changed.text
    deliver(client, contexts, "chain", "lo1", 2, "NO-GO")
    deliver(client, contexts, "chain", "pb2", 3, "REVISED")
    deliver(client, contexts, "chain", "lo2", 4, "GO")
    assert claim(client, "chain", "pb3", 4, "READY").status_code == 200


def test_claim_expiry_and_different_successor_contention_are_not_thread_ownership(bridge):
    service, client, contexts, _ = bridge
    deliver(client, contexts, "chain", "pb1", 1, "NEW")
    first = claim(client, "chain", "lo1", 1, "GO", request_id="same-request")
    assert first.status_code == 200
    repeated = claim(client, "chain", "lo1", 1, "GO", request_id="same-request")
    assert repeated.json() == first.json()
    for author, status in (("lo1", "GO"), ("lo2", "NO-GO"), ("lo2", "SUPERSEDED")):
        assert claim(client, "chain", author, 1, status).status_code == 422
    with service.kernel.transaction() as tx:
        tx.cursor.execute(
            sql.SQL(
                "UPDATE {}.work_intent_claims SET expires_at=clock_timestamp()-interval '1 second' "
                "WHERE attempt_id='chain'"
            ).format(sql.Identifier(tx.schema))
        )
    second = claim(client, "chain", "lo2", 1, "NO-GO")
    assert second.status_code == 200
    assert second.json()["fence"] > first.json()["fence"]
    stale = {"native_context_id": "lo1", "fence": first.json()["fence"]}
    assert client.post("/v1/bridge/chain/release", json=stale).status_code == 422
    assert (
        client.post(
            "/v1/bridge/chain/deliver", json={**stale, "content": authored(contexts["lo1"], "chain", 2, "GO")}
        ).status_code
        == 422
    )
    fence = {"native_context_id": "lo2", "fence": second.json()["fence"]}
    assert (
        client.post(
            "/v1/bridge/chain/deliver", json={**fence, "content": authored(contexts["lo2"], "chain", 2, "NO-GO")}
        ).status_code
        == 200
    )
    assert claim(client, "chain", "pb2", 2, "READY").status_code == 422
    deliver(client, contexts, "chain", "pb2", 3, "REVISED")


def test_header_and_role_errors_have_no_delivery_effect(bridge):
    _, client, contexts, _ = bridge
    reserved = claim(client, "chain", "pb1", 0, "NEW").json()
    original = authored(contexts["pb1"], "chain", 1, "NEW")
    for content in (
        original.replace("::init gtkb lo", "::init gtkb pb"),
        original.replace("recipient_role: loyal-opposition", "recipient_role: prime-builder"),
        original.replace("Version: 1", "Version: 1\r\nversion: 1"),
        original.replace("Version: 1", "Version: 1\r\nNEW"),
        original.replace("bridge_kind: implementation_proposal", "bridge_kind: prime_proposal"),
        original.replace('["code.py"]', '["bridge/payload.md"]'),
        original.replace('["code.py"]', '[".GIT/config"]'),
        original.replace("NEW\r\n", "NO-ACTION\r\n", 1),
        original.replace(
            "author_session_context_id: " + contexts["pb1"]["session_context_id"],
            "author_session_context_id: " + contexts["pb2"]["session_context_id"],
        ),
    ):
        result = client.post(
            "/v1/bridge/chain/deliver",
            json={"native_context_id": "pb1", "fence": reserved["fence"], "content": content},
        )
        assert result.status_code == 422, result.text
        assert client.get("/v1/bridge/chain/show").json()["attempt"]["head_version"] == 0
    assert claim(client, "chain", "pb1", 0, "GO").status_code == 422
    result = client.post(
        "/v1/bridge/chain/deliver", json={"native_context_id": "pb1", "fence": reserved["fence"], "content": original}
    )
    assert result.status_code == 200
    collision = client.post(
        "/v1/bridge/chain/deliver",
        json={"native_context_id": "pb1", "fence": reserved["fence"], "content": original + "altered"},
    )
    assert collision.status_code == 422


def test_proposal_rechecks_executable_evidence_after_claim(bridge):
    _, client, contexts, _ = bridge
    reserved = claim(client, "chain", "pb1", 0, "NEW").json()
    request = {
        "native_context_id": "pb1",
        "fence": reserved["fence"],
        "content": authored(contexts["pb1"], "chain", 1, "NEW"),
    }
    assert put(client, "test-plans", "PLAN-1", {"status": "retired"}, expected_version=1).status_code == 200
    rejected = client.post("/v1/bridge/chain/deliver", json=request)
    assert rejected.status_code == 422 and rejected.json()["error"]["code"] == "test_phase_required"
    state = client.get("/v1/bridge/chain/show", params={"include_content": True}).json()
    assert state["attempt"]["head_version"] == 0 and state["messages"] == []
    assert put(client, "test-plans", "PLAN-1", {"status": "active"}, expected_version=2).status_code == 200
    assert client.post("/v1/bridge/chain/deliver", json=request).status_code == 200


def test_authorization_checked_at_new_delivery_but_does_not_cancel_chain(bridge):
    service, client, contexts, _ = bridge
    reserved = claim(client, "chain", "pb1", 0, "NEW").json()

    def authorize(value):
        with service.kernel.transaction() as tx:
            tx.cursor.execute(
                sql.SQL('UPDATE {}.projects SET "authorization"=%s WHERE id=%s').format(sql.Identifier(tx.schema)),
                (value, "PROJECT-1"),
            )

    authorize("not authorized")
    result = client.post(
        "/v1/bridge/chain/deliver",
        json={
            "native_context_id": "pb1",
            "fence": reserved["fence"],
            "content": authored(contexts["pb1"], "chain", 1, "NEW"),
        },
    )
    assert result.status_code == 422 and result.json()["error"]["code"] == "project_not_authorized"
    authorize("authorized")
    assert (
        client.post(
            "/v1/bridge/chain/deliver",
            json={
                "native_context_id": "pb1",
                "fence": reserved["fence"],
                "content": authored(contexts["pb1"], "chain", 1, "NEW"),
            },
        ).status_code
        == 200
    )
    authorize("not authorized")
    assert len(client.get("/v1/bridge/queue", params={"role": "lo"}).json()["eligible"]) == 1
    deliver(client, contexts, "chain", "lo1", 2, "GO")
    deliver(client, contexts, "chain", "pb2", 3, "READY")


def test_report_rejection_verdict_rejection_and_withdrawal(bridge):
    _, client, contexts, _ = bridge
    deliver(client, contexts, "chain", "pb1", 1, "NEW")
    deliver(client, contexts, "chain", "lo1", 2, "GO")
    assert claim(client, "chain", "pb1", 2, "WITHDRAWN").status_code == 422
    deliver(client, contexts, "chain", "pb2", 3, "READY")
    assert claim(client, "chain", "lo2", 3, "NO-GO").status_code == 422
    deliver(client, contexts, "chain", "lo2", 4, "NOT-READY")
    deliver(client, contexts, "chain", "pb3", 5, "VERDICT-REJECTED")
    deliver(client, contexts, "chain", "lo3", 6, "NOT-READY")
    deliver(client, contexts, "chain", "pb2", 7, "READY")


def test_withdrawal_and_broken_chain_recovery_purge_payload_without_fabricating_history(bridge):
    service, client, contexts, _ = bridge
    deliver(client, contexts, "withdrawn", "pb1", 1, "NEW")
    deliver(client, contexts, "withdrawn", "pb2", 2, "WITHDRAWN")
    state = client.get("/v1/bridge/withdrawn/show", params={"include_content": True}).json()
    assert state["attempt"]["disposition"] == "withdrawn" and "messages" not in state
    deliver(client, contexts, "broken", "pb2", 1, "NEW")
    with service.kernel.transaction() as tx:
        tx.cursor.execute(
            sql.SQL("DELETE FROM {}.bridge_items WHERE attempt_id='broken'").format(sql.Identifier(tx.schema))
        )
    result = client.post(
        "/v1/bridge/broken/abandon",
        json={"native_context_id": "lo1", "expected_version": 1, "reason": "Canonical current message is missing"},
    )
    assert result.status_code == 200
    assert result.json()["disposition"] == "abandoned"
    deliver(client, contexts, "replacement", "pb3", 1, "NEW")
    with service.kernel.transaction(read_only=True) as tx:
        tx.cursor.execute(sql.SQL("SELECT DISTINCT attempt_id FROM {}.bridge_items").format(sql.Identifier(tx.schema)))
        assert [row["attempt_id"] for row in tx.cursor.fetchall()] == ["replacement"]


def test_verified_refuses_changed_bytes_and_preserves_unverified_work(bridge):
    _, client, contexts, root = bridge
    deliver(client, contexts, "chain", "pb1", 1, "NEW")
    deliver(client, contexts, "chain", "lo1", 2, "GO")
    deliver(client, contexts, "chain", "pb2", 3, "READY")
    reviewed = client.get("/v1/bridge/chain/artifacts").json()
    (root / "code.py").write_text("value = 3\n", encoding="utf-8")
    reserved = claim(client, "chain", "lo2", 3, "VERIFIED").json()
    result = client.post(
        "/v1/bridge/chain/deliver",
        json={
            "native_context_id": "lo2",
            "fence": reserved["fence"],
            "content": authored(contexts["lo2"], "chain", 4, "VERIFIED", verified_artifacts=json.dumps(reviewed)),
        },
    )
    assert result.status_code == 422 and result.json()["error"]["code"] == "reviewed_bytes_changed"
    assert client.get("/v1/work-items/WI-1").json()["work_item"]["resolution_status"] == "open"


def test_headless_blocked_superseded_and_unscoped_advisory(bridge):
    service, client, contexts, _ = bridge
    with service.kernel.transaction() as tx:
        tx.cursor.execute(
            sql.SQL("UPDATE {}.projects SET \"authorization\"='not authorized' WHERE id='PROJECT-1'").format(
                sql.Identifier(tx.schema)
            )
        )
    blocked = claim(client, "blocked", "pb1", 0, "BLOCKED")
    assert blocked.status_code == 200
    body = {
        "native_context_id": "pb1",
        "fence": blocked.json()["fence"],
        "content": authored(
            contexts["pb1"],
            "blocked",
            1,
            "BLOCKED",
            observed_authorization="not authorized",
            authorization_read_at=datetime.now(UTC).isoformat(),
        ),
    }
    assert client.post("/v1/bridge/blocked/deliver", json=body).status_code == 422
    assert client.post("/v1/bridge/blocked/deliver", json={**body, "mode": "headless"}).status_code == 200
    assert client.get("/v1/bridge/queue", params={"role": "lo"}).json()["eligible"] == []
    with service.kernel.transaction() as tx:
        tx.cursor.execute(
            sql.SQL("UPDATE {}.projects SET \"authorization\"='authorized' WHERE id='PROJECT-1'").format(
                sql.Identifier(tx.schema)
            )
        )
    deliver(client, contexts, "blocked", "pb2", 2, "NEW")
    assert put(client, "specifications", "SPEC-1", {"status": "retired"}, expected_version=1).status_code == 200
    deliver(
        client, contexts, "blocked", "lo1", 3, "SUPERSEDED", supersession_source="SPEC-1", residual_work_item="none"
    )
    closed = client.get("/v1/bridge/blocked/show", params={"include_content": True}).json()
    assert closed["attempt"]["disposition"] == "superseded" and "messages" not in closed
    for version, context in ((1, "pb3"), (2, "lo2")):
        reserved = claim(client, "advisory", context, version - 1, "ADVISORY", work_item_id=None)
        assert reserved.status_code == 200, reserved.text
        content = authored(contexts[context], "advisory", version, "ADVISORY")
        content = content.replace("Project: PROJECT-1\r\n", "").replace("Work Item: WI-1\r\n", "")
        result = client.post(
            "/v1/bridge/advisory/deliver",
            json={"native_context_id": context, "fence": reserved.json()["fence"], "content": content},
        )
        assert result.status_code == 200, result.text
    assert client.get("/v1/bridge/advisory/show").json()["attempt"]["work_item_id"] is None


def test_overlapping_effect_claims_and_source_change_require_fresh_work(bridge):
    _, client, contexts, _ = bridge
    assert put(client, "work-items", "WI-2", work_fields(), project_id="PROJECT-1").status_code == 200
    for document, work in (("first", "WI-1"), ("second", "WI-2")):
        deliver(client, contexts, document, "pb1", 1, "NEW", work_item_id=work)
        deliver(client, contexts, document, "lo1", 2, "GO", work_item_id=work)
    first = claim(client, "first", "pb2", 2, "READY").json()
    conflict = claim(client, "second", "pb2", 2, "READY", work_item_id="WI-2")
    assert conflict.status_code == 422 and conflict.json()["error"]["code"] == "artifact_effect_conflict"
    release = {"native_context_id": "pb2", "fence": first["fence"]}
    assert client.post("/v1/bridge/first/release", json=release).status_code == 200
    assert (
        put(
            client, "specifications", "SPEC-1", {"description": "Owner changes the intended result"}, expected_version=1
        ).status_code
        == 200
    )
    stale = claim(client, "first", "pb3", 2, "READY")
    assert stale.status_code == 422 and stale.json()["error"]["code"] == "scope_changed"
    abandoned = client.post(
        "/v1/bridge/first/abandon",
        json={"native_context_id": "lo2", "expected_version": 2, "reason": "Formal scope changed after GO"},
    )
    assert abandoned.status_code == 200
    assert claim(client, "replacement", "pb3", 0, "READY").status_code == 422
    deliver(client, contexts, "replacement", "pb3", 1, "NEW")


@pytest.mark.parametrize("scope", ["shared_test", "test_is_source", "source_is_test", "independent"])
def test_effect_claim_arbitration_includes_test_artifacts(bridge, scope):
    service, client, contexts, _ = bridge
    second_test = "tests/test_second.py"
    assert (
        put(
            client,
            "tests",
            "TEST-2",
            {
                "title": "Second effect test",
                "spec_id": "SPEC-1",
                "test_type": "integration",
                "test_file": second_test,
                "expected_outcome": "Second effect observed",
            },
        ).status_code
        == 200
    )
    assert (
        put(client, "test-phases", "PHASE-1", {"test_ids": ["TEST-1", "TEST-2"]}, expected_version=1).status_code == 200
    )
    assert (
        put(client, "work-items", "WI-2", work_fields(source_test_id="TEST-2"), project_id="PROJECT-1").status_code
        == 200
    )
    targets = ["second.py"]
    tests = [second_test]
    if scope == "shared_test":
        tests.append("tests/test_effect.py")
    elif scope == "test_is_source":
        targets.append("tests/test_effect.py")
    elif scope == "source_is_test":
        tests.append("CODE.PY")
    deliver(client, contexts, "first", "pb1", 1, "NEW")
    deliver(client, contexts, "first", "lo1", 2, "GO")
    deliver(
        client,
        contexts,
        "second",
        "pb3",
        1,
        "NEW",
        work_item_id="WI-2",
        target_paths=json.dumps(targets),
        test_artifact_targets=json.dumps(tests),
    )
    deliver(client, contexts, "second", "lo3", 2, "GO", work_item_id="WI-2")
    first = claim(client, "first", "pb2", 2, "READY")
    assert first.status_code == 200, first.text
    second = claim(client, "second", "pb3", 2, "READY", work_item_id="WI-2")
    if scope == "independent":
        assert second.status_code == 200, second.text
    else:
        assert second.status_code == 422, second.text
        assert second.json()["error"]["code"] == "artifact_effect_conflict"
        with service.kernel.transaction(read_only=True) as tx:
            tx.cursor.execute(
                sql.SQL("SELECT count(*) AS n FROM {}.work_intent_claims WHERE attempt_id='second'").format(
                    sql.Identifier(tx.schema)
                )
            )
            assert tx.cursor.fetchone()["n"] == 0
        assert (
            client.post(
                "/v1/bridge/first/release", json={"native_context_id": "pb2", "fence": first.json()["fence"]}
            ).status_code
            == 200
        )
        second = claim(client, "second", "pb3", 2, "READY", work_item_id="WI-2")
        assert second.status_code == 200, second.text
    checked = client.post("/v1/bridge/second/check", json={"native_context_id": "pb3", "fence": second.json()["fence"]})
    assert checked.status_code == 200, checked.text
    assert checked.json()["target_paths"] == sorted(set(targets + tests))


def test_simultaneous_test_artifact_claims_leave_one_live_reservation(bridge, monkeypatch):
    service, client, contexts, _ = bridge
    assert put(client, "work-items", "WI-2", work_fields(), project_id="PROJECT-1").status_code == 200
    for document, work, path in (("first", "WI-1", "code.py"), ("second", "WI-2", "second.py")):
        deliver(client, contexts, document, "pb1", 1, "NEW", work_item_id=work, target_paths=json.dumps([path]))
        deliver(client, contexts, document, "lo1", 2, "GO", work_item_id=work)
    barrier = Barrier(2, timeout=15)
    original_scope = NativeBridgeService._scope

    def simultaneous_scope(tx, attempt, **kwargs):
        original_scope(tx, attempt, **kwargs)
        barrier.wait()

    with monkeypatch.context() as racing:
        racing.setattr(NativeBridgeService, "_scope", staticmethod(simultaneous_scope))
        with ThreadPoolExecutor(max_workers=2) as workers:
            futures = [
                workers.submit(claim, client, document, context, 2, "READY", work_item_id=work)
                for document, context, work in (("first", "pb2", "WI-1"), ("second", "pb3", "WI-2"))
            ]
            responses = [future.result() for future in futures]
    assert sum(response.status_code == 200 for response in responses) == 1
    failure = next(response for response in responses if response.status_code != 200)
    assert (failure.status_code, failure.json()["error"]["code"]) in {
        (422, "artifact_effect_conflict"),
        (409, "retryable_conflict"),
    }
    with service.kernel.transaction(read_only=True) as tx:
        tx.cursor.execute(sql.SQL("SELECT attempt_id FROM {}.work_intent_claims").format(sql.Identifier(tx.schema)))
        assert len(tx.cursor.fetchall()) == 1
    loser = responses.index(failure)
    document, context, work = [("first", "pb2", "WI-1"), ("second", "pb3", "WI-2")][loser]
    retry = claim(client, document, context, 2, "READY", work_item_id=work)
    assert retry.status_code == 422 and retry.json()["error"]["code"] == "artifact_effect_conflict"
