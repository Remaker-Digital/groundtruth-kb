"""Native bridge state-machine qualification with fresh independent contexts."""

from __future__ import annotations

import json
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime
from itertools import permutations
from pathlib import Path
from threading import Barrier
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from groundtruth_kb.authority_api import create_authority_app
from groundtruth_kb.bridge.native import BindSession, NativeBridgeService, parse_authored_message
from groundtruth_kb.bridge.vocabulary import LOYAL_OPPOSITION_ACTIONABLE_STATUSES, PRIME_ACTIONABLE_STATUSES
from groundtruth_kb.postgres_kernel import TABLE_SPECS, PostgresKernelError
from psycopg import sql

from platform_tests.groundtruth_kb.test_native_authority_service import link_project_formal, put, seed, work_fields
from platform_tests.groundtruth_kb.test_native_authority_service import native as native

pytestmark = [pytest.mark.integration, pytest.mark.timeout(120)]


@pytest.fixture
def bridge(native, tmp_path, request):
    service, _, _, _ = native
    # An indirect parameter selects the host location (a nested path with a space exercises quoting in Git,
    # hooks and worktrees); consumers without one keep the temporary directory itself.
    tmp_path = tmp_path / request.param if getattr(request, "param", None) else tmp_path
    tmp_path.mkdir(parents=True, exist_ok=True)
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
            assert result.json()["status"] == "init_requested"
            contexts[name] = result.json()["binding"]
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
            work_item_version=1,
            target_paths=json.dumps(["code.py"]),
            test_artifact_targets=json.dumps(["tests/test_effect.py"]),
            spec_versions=json.dumps({"SPEC-1": 1}),
        )
    fields.update(extra)
    return "\r\n".join(
        [
            *lines,
            *(f"{key}: {value}" for key, value in fields.items()),
            "",
            "Authored content: cafÃƒÂ© Ã¦Â¼Â¢Ã¥Â­â€”.",
            "",
        ]
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


def test_native_delivery_readback_requires_the_exact_context_and_slot(bridge):
    _service, client, contexts, _root = bridge
    document = "delivery-readback"

    def read(version, context="lo1", name=document):
        return client.get(f"/v1/bridge/{name}/delivery", params={"version": version, "native_context_id": context})

    assert read(1).json()["error"]["code"] == "bridge_delivery_incomplete"
    assert read(1, "unbound").json()["error"]["code"] == "no_session_binding"
    deliver(client, contexts, document, "pb1", 1, "NEW")
    reservation = claim(client, document, "lo1", 1, "GO").json()
    fence = {"native_context_id": "lo1", "fence": reservation["fence"]}
    before = client.get(f"/v1/bridge/{document}/show?include_content=true").json()
    assert read(2).json()["error"]["code"] == "bridge_delivery_incomplete"
    assert client.post(f"/v1/bridge/{document}/check", json=fence).status_code == 200
    assert client.post(f"/v1/bridge/{document}/release", json=fence).status_code == 200
    assert read(2).json()["error"]["code"] == "bridge_delivery_incomplete"
    assert client.get(f"/v1/bridge/{document}/show?include_content=true").json() == before

    deliver(client, contexts, document, "lo1", 2, "GO")
    expected = {
        "status": "delivered",
        "document": document,
        "version": 2,
        "bridge_status": "GO",
        "native_context_id": "lo1",
        "author_session_context_id": contexts["lo1"]["session_context_id"],
    }
    assert read(2).json() == expected
    for version, context, name in [
        (1, "lo1", document),
        (2, "lo2", document),
        (3, "lo1", document),
        (2, "lo1", "other"),
    ]:
        assert read(version, context, name).json()["error"]["code"] == "bridge_delivery_incomplete"
    deliver(client, contexts, document, "pb2", 3, "READY")
    assert read(2).json() == expected


def test_native_effect_check_uses_live_claim_checkout_and_current_scope(bridge):
    service, client, contexts, work_root = bridge
    root = work_root.parents[2]
    document = "effect-check"
    deliver(client, contexts, document, "pb1", 1, "NEW")
    deliver(client, contexts, document, "lo1", 2, "GO")
    reserved = claim(client, document, "pb2", 2, "READY").json()
    fence = {"native_context_id": "pb2", "fence": reserved["fence"]}
    opened = client.post(f"/v1/bridge/{document}/worktree", json=fence)
    assert opened.status_code == 200, opened.text
    checkout = Path(opened.json()["path"])

    def check(paths, *, context="pb2", cwd=checkout):
        return client.post(
            "/v1/bridge/check-effects",
            json={"native_context_id": context, "cwd": str(cwd), "paths": paths},
        )

    before = client.get(f"/v1/bridge/{document}/show", params={"include_content": True}).json()
    accepted = check(["code.py", "tests/test_effect.py"])
    assert accepted.status_code == 200, accepted.text
    assert accepted.json()["document"] == document
    assert accepted.json()["fence"] == reserved["fence"]
    assert accepted.json()["scope"] == "implementation"
    assert check(["test_effect.py"], cwd=checkout / "tests").status_code == 200
    for paths, cwd, context in (
        (["second.py"], checkout, "pb2"),
        (["code.py"], root, "pb2"),
        ([str(checkout / "code.py")], checkout, "lo1"),
        ([".git"], checkout, "pb2"),
        (["bridge/message-001.md"], root, "pb2"),
        (["code.py", "second.py"], checkout, "pb2"),
        (["tests"], checkout, "pb2"),
    ):
        refused = check(paths, cwd=cwd, context=context)
        assert refused.status_code == 422, refused.text
    assert client.get(f"/v1/bridge/{document}/show", params={"include_content": True}).json() == before
    assert client.post(f"/v1/bridge/{document}/check", json=fence).status_code == 200

    with service.kernel.transaction() as tx:
        tx.cursor.execute(
            sql.SQL(
                "UPDATE {}.work_intent_claims SET expires_at=clock_timestamp()-interval '1 second' WHERE attempt_id=%s"
            ).format(sql.Identifier(tx.schema)),
            (document,),
        )
    assert check(["code.py"]).json()["error"]["code"] == "implementation_claim_required"
    successor = claim(client, document, "pb3", 2, "READY").json()
    successor_fence = {"native_context_id": "pb3", "fence": successor["fence"]}
    successor_checkout = Path(client.post(f"/v1/bridge/{document}/worktree", json=successor_fence).json()["path"])
    assert check(["code.py"], context="pb3", cwd=successor_checkout).status_code == 200
    assert check(["code.py"]).status_code == 422

    # A service mutation changes the observed formal input without altering the
    # reservation. The next actual tool check must reject the stale proposal.
    assert (
        put(
            client,
            "specifications",
            "SPEC-1",
            {"title": "Required effect", "description": "Changed governing intent", "status": "active"},
            expected_version=1,
        ).status_code
        == 200
    )
    refused = check(["code.py"], context="pb3", cwd=successor_checkout)
    assert refused.status_code == 422, refused.text
    assert refused.json()["error"]["code"] == "scope_changed"


def test_native_effect_check_confines_scratch_to_exact_bound_context(bridge):
    _service, client, contexts, work_root = bridge
    root = work_root.parents[2]
    own = root / "scratchpad" / contexts["pb1"]["session_context_id"]
    other = root / "scratchpad" / contexts["lo1"]["session_context_id"]
    request = {"native_context_id": "pb1", "cwd": str(root), "paths": [str(own / "draft.md")]}
    accepted = client.post("/v1/bridge/check-effects", json=request)
    assert accepted.status_code == 200, accepted.text
    assert accepted.json()["scope"] == "scratch"
    assert not own.exists()
    for path in (other / "draft.md", root / "code.py", own / ".." / "escape.md"):
        refused = client.post("/v1/bridge/check-effects", json={**request, "paths": [str(path)]})
        assert refused.status_code == 422, refused.text
    assert client.post("/v1/bridge/check-effects", json={**request, "native_context_id": "unbound"}).status_code == 422
    assert client.post("/v1/bridge/check-effects", json={**request, "paths": []}).status_code == 422


def test_native_effect_check_refuses_unregistered_checkout_and_redirected_targets(bridge):
    _service, client, contexts, work_root = bridge
    root = work_root.parents[2]
    document = "effect-containment"
    deliver(client, contexts, document, "pb1", 1, "NEW")
    deliver(client, contexts, document, "lo1", 2, "GO")
    reserved = claim(client, document, "pb2", 2, "READY").json()
    fence = {"native_context_id": "pb2", "fence": reserved["fence"]}
    checkout = root / ".worktrees" / contexts["pb2"]["session_context_id"]
    request = {"native_context_id": "pb2", "cwd": str(root), "paths": [str(checkout / "code.py")]}
    refused = client.post("/v1/bridge/check-effects", json=request)
    assert refused.json()["error"]["code"] == "checkout_not_registered"
    opened = client.post(f"/v1/bridge/{document}/worktree", json=fence)
    assert opened.status_code == 200, opened.text
    assert client.post("/v1/bridge/check-effects", json=request).status_code == 200
    tests = checkout / "tests"
    preserved = checkout / "preserved-tests"
    tests.rename(preserved)
    import os

    if os.name == "nt":
        subprocess.run(["cmd", "/c", "mklink", "/J", str(tests), str(preserved)], check=True, capture_output=True)
    else:
        tests.symlink_to(preserved, target_is_directory=True)
    original = (preserved / "test_effect.py").read_bytes()
    refused = client.post("/v1/bridge/check-effects", json={**request, "paths": [str(tests / "test_effect.py")]})
    assert refused.json()["error"]["code"] == "effect_path_redirected"
    assert (preserved / "test_effect.py").read_bytes() == original
    assert client.post(f"/v1/bridge/{document}/check", json=fence).status_code == 200


def test_native_effect_gate_refuses_unavailable_authority_without_sqlite(tmp_path):
    import os
    import socket
    import sys

    sentinel = tmp_path / "must-not-open.db"
    sentinel.write_bytes(b"No SQLite fallback is permitted.")
    env = {key: value for key, value in os.environ.items() if not key.startswith(("PG", "GT_POSTGRES_"))}
    env.update(
        GTKB_NATIVE_CONTEXT_ID="current-native-context",
        GTKB_PROJECT_ROOT=str(tmp_path),
        GT_PROJECT_ROOT=str(tmp_path),
        GT_DB_PATH=str(sentinel),
        PYTHONIOENCODING="utf-8",
    )
    payload = {
        "session_id": "current-native-context",
        "cwd": str(tmp_path),
        "project_root": str(tmp_path),
        "tool_name": "Write",
        "tool_input": {"path": "code.py", "content": "must not be written"},
    }
    with socket.socket() as unavailable:
        unavailable.bind(("127.0.0.1", 0))
        env["GT_AUTHORITY_URL"] = f"http://127.0.0.1:{unavailable.getsockname()[1]}"
        result = subprocess.run(
            [sys.executable, str(Path(__file__).resolve().parents[2] / "scripts/implementation_start_gate.py")],
            input=json.dumps(payload),
            cwd=tmp_path,
            env=env,
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=20,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        )
    assert result.returncode == 0, result.stderr
    refusal = json.loads(result.stdout)["hookSpecificOutput"]
    assert refusal["hookEventName"] == "PreToolUse"
    assert refusal["permissionDecision"] == "deny"
    assert "authority_unavailable" in refusal["permissionDecisionReason"]
    assert sentinel.read_bytes() == b"No SQLite fallback is permitted."
    assert not (tmp_path / "code.py").exists()


def test_native_binding_rejects_role_aliases_and_ambiguous_init_without_mutation(bridge):
    _service, client, contexts, _root = bridge
    invalid = (
        "::init gtkb admin",
        "::init gtkb prime-builder",
        "::init gtkb loyal-opposition",
        "::init gtkb PB",
        "::init gtkb LO",
        "::init gtkb",
        "::init codex pb",
        "init gtkb pb",
        " ::init gtkb pb",
        "::init gtkb pb ",
        "::init\tgtkb pb",
        "::init  gtkb pb",
        "::init gtkb pb --force",
        "::init gtkb pb\n::init gtkb lo",
    )
    for index, marker in enumerate(invalid):
        native_id = f"invalid-init-{index}"
        result = client.post("/v1/sessions/bind", json={"native_context_id": native_id, "init_command": marker})
        assert result.status_code == 422, (marker, result.text)
        expected = "session_init_conflict" if "\n" in marker else "invalid_init_marker"
        assert result.json()["error"]["code"] == expected
        read = client.get("/v1/sessions/binding", params={"native_context_id": native_id})
        assert read.json()["error"]["code"] == "no_session_binding"
    for native_id, existing in contexts.items():
        assert client.get("/v1/sessions/binding", params={"native_context_id": native_id}).json() == existing


@pytest.mark.parametrize(
    "prompt,code,markers,invalid_lines",
    [
        ("An ordinary owner request.\nContinue.", "no_init_marker", [], []),
        ("Owner text.\r\n::INIT gtkb PB\r\nContinue.", "invalid_init_marker", [], [2]),
        ("::init gtkb pb # private-owner-content", "invalid_init_marker", [], [1]),
        ("::init gtkb pb ${private-owner-content}", "invalid_init_marker", [], [1]),
        ("\ufeff::init gtkb pb", "invalid_init_marker", [], [1]),
        (
            "private-owner-content\r\n::init gtkb pb\r\n::init gtkb lo",
            "session_init_conflict",
            ["::init gtkb lo", "::init gtkb pb"],
            [],
        ),
        (
            "::init application pb\n::init gtkb pb",
            "session_init_conflict",
            ["::init application pb", "::init gtkb pb"],
            [],
        ),
    ],
)
def test_init_refusals_report_marker_evidence_and_recovery_without_effects(
    bridge, prompt, code, markers, invalid_lines
):
    service, client, contexts, root = bridge

    def snapshot():
        with service.kernel.transaction(read_only=True) as tx:
            tx.cursor.execute(
                sql.SQL("SELECT * FROM {}.session_init_bindings ORDER BY native_context_id").format(
                    sql.Identifier(tx.schema)
                )
            )
            bindings = tx.cursor.fetchall()
        report = client.get("/v1/bridge/state-report").json()
        report.pop("observed_at")
        return bindings, report

    before = snapshot()
    files = {p.relative_to(root): p.read_bytes() for p in root.rglob("*") if p.is_file()}
    # Reject on both a fresh identity and an already-bound context. Failure
    # cannot create a binding, alter one, or acquire bridge work.
    for native_id in ("unbound-init-refusal", "pb1"):
        result = client.post("/v1/sessions/bind", json={"native_context_id": native_id, "init_command": prompt})
        assert result.status_code == 422
        error = result.json()["error"]
        assert error["code"] == code
        assert error["details"]["observed_markers"] == markers
        assert error["details"]["invalid_marker_line_numbers"] == invalid_lines
        assert "gt session" in error["details"]["recovery_route"]
        assert "private-owner-content" not in result.text
        assert snapshot() == before
    assert {p.relative_to(root): p.read_bytes() for p in root.rglob("*") if p.is_file()} == files
    assert client.get("/v1/sessions/binding", params={"native_context_id": "pb1"}).json() == contexts["pb1"]


def test_existing_binding_conflicts_report_the_observed_marker_and_remain_immutable(bridge):
    _service, client, contexts, _root = bridge
    for marker in ("::init gtkb lo", "::init application pb", "::init application lo"):
        result = client.post("/v1/sessions/bind", json={"native_context_id": "pb1", "init_command": marker})
        assert result.status_code == 422
        error = result.json()["error"]
        assert error["code"] == "session_init_conflict"
        assert error["details"]["observed_markers"] == [marker]
        assert error["details"]["invalid_marker_line_numbers"] == []
        assert "gt session show" in error["details"]["recovery_route"]
        assert client.get("/v1/sessions/binding", params={"native_context_id": "pb1"}).json() == contexts["pb1"]


@pytest.mark.parametrize("identity", [{}, {"native_context_id": ""}, {"native_context_id": None}])
def test_native_binding_requires_actual_context_identity_without_creating_state(bridge, identity):
    service, client, contexts, root = bridge
    with service.kernel.transaction(read_only=True) as tx:
        tx.cursor.execute(
            sql.SQL("SELECT * FROM {}.session_init_bindings ORDER BY native_context_id").format(
                sql.Identifier(tx.schema)
            )
        )
        before = tx.cursor.fetchall()
    result = client.post("/v1/sessions/bind", json={**identity, "init_command": "::init gtkb lo"})
    assert result.status_code == 422
    assert result.json()["code"] == "invalid_request"
    assert any(field["location"] == ["body", "native_context_id"] for field in result.json()["fields"])
    with service.kernel.transaction(read_only=True) as tx:
        tx.cursor.execute(
            sql.SQL("SELECT * FROM {}.session_init_bindings ORDER BY native_context_id").format(
                sql.Identifier(tx.schema)
            )
        )
        assert tx.cursor.fetchall() == before
    for native_id, binding in contexts.items():
        assert client.get("/v1/sessions/binding", params={"native_context_id": native_id}).json() == binding
    assert not (root / "groundtruth.db").exists()


def test_init_success_results_identify_creation_and_retry_without_persisting_status(native):
    service, client, *_ = native
    for subject, role in (("gtkb", "pb"), ("gtkb", "lo"), ("application", "pb"), ("application", "lo")):
        native_id = f"result-contract-{subject}-{role}"
        marker = f"::init {subject} {role}"
        request = {"native_context_id": native_id, "init_command": f"Owner input.\r\n{marker}\r\n{marker}"}
        first = client.post("/v1/sessions/bind", json=request)
        assert first.status_code == 200
        result = first.json()
        assert set(result) == {"status", "binding"}
        assert result["status"] == "init_requested"
        binding = result["binding"]
        assert set(binding) == {
            "native_context_id",
            "session_context_id",
            "subject",
            "role",
            "created_at",
            "minimum_idempotency_identity",
        }
        assert binding["native_context_id"] == native_id and binding["subject"] == subject
        assert binding["role"] == {"pb": "prime-builder", "lo": "loyal-opposition"}[role]
        repeated = client.post("/v1/sessions/bind", json={**request, "init_command": marker})
        assert repeated.status_code == 200
        assert repeated.json() == {"status": "already_initialized_idempotent", "binding": binding}
        assert client.get("/v1/sessions/binding", params={"native_context_id": native_id}).json() == binding
        with service.kernel.transaction(read_only=True) as tx:
            tx.cursor.execute(
                sql.SQL("SELECT * FROM {}.session_init_bindings WHERE native_context_id=%s").format(
                    sql.Identifier(tx.schema)
                ),
                (native_id,),
            )
            assert set(tx.cursor.fetchone()) == set(binding)
            tx.cursor.execute(
                sql.SQL("SELECT count(*) AS count FROM {}.record_history").format(sql.Identifier(tx.schema))
            )
            assert tx.cursor.fetchone()["count"] == 0


def test_concurrent_init_results_have_one_creation_and_identical_immutable_bindings(native, tmp_path):
    service, _client, *_ = native
    bridge_service = NativeBridgeService(service.kernel, tmp_path)
    barrier = Barrier(4)

    def bind():
        barrier.wait(timeout=10)
        return bridge_service.bind(BindSession(native_context_id="concurrent-result", init_command="::init gtkb lo"))

    with ThreadPoolExecutor(max_workers=4) as workers:
        results = list(workers.map(lambda _: bind(), range(4)))
    assert [r["status"] for r in results].count("init_requested") == 1
    assert [r["status"] for r in results].count("already_initialized_idempotent") == 3
    assert all(r["binding"] == results[0]["binding"] for r in results)
    assert bridge_service.session("concurrent-result") == results[0]["binding"]
    assert not list(tmp_path.iterdir())


def test_binding_is_immutable_exact_and_retry_idempotent(bridge):
    service, client, contexts, root = bridge
    request = {"native_context_id": "pb1", "init_command": "::init gtkb pb\n::init gtkb pb"}
    again = client.post("/v1/sessions/bind", json=request)
    assert again.status_code == 200
    assert again.json() == {"status": "already_initialized_idempotent", "binding": contexts["pb1"]}
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
    assert {result["status"] for result in bound} == {"init_requested", "already_initialized_idempotent"}
    assert bound[0]["binding"] == bound[1]["binding"]
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
@pytest.mark.parametrize(
    "changed_scope",
    [
        "work",
        "formal",
        "parent",
        "project_formal",
        "test_formal",
        "project_formal_removed",
        "project_formal_overlap_removed",
        "test_formal_cited",
    ],
)
@pytest.mark.parametrize("claim_before_change", [False, True])
def test_claim_operations_reject_changed_scope_without_consuming_the_reservation(
    bridge, next_status, changed_scope, claim_before_change
):
    service, client, contexts, root = bridge
    source_versions = {"SPEC-1": 1}
    if changed_scope in {"project_formal_removed", "test_formal_cited"}:
        added = put(client, "specifications", "SPEC-ADDED", {"title": "Cited requirement", "status": "active"})
        assert added.status_code == 200, added.text
        source_versions["SPEC-ADDED"] = 1
        if changed_scope == "project_formal_removed":
            link_project_formal(service, "SPEC-ADDED")
    elif changed_scope == "project_formal_overlap_removed":
        link_project_formal(service, "SPEC-1")
    chain = [("pb1", "NEW"), ("lo1", "GO"), ("pb2", "READY"), ("lo2", "VERIFIED")]
    for version, (context, status) in enumerate(chain, 1):
        if status == next_status:
            break
        extra = {"spec_versions": json.dumps(source_versions)} if status == "NEW" else {}
        deliver(client, contexts, "chain", context, version, status, **extra)
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
    elif changed_scope in {"project_formal_removed", "project_formal_overlap_removed"}:
        spec_id = "SPEC-ADDED" if changed_scope == "project_formal_removed" else "SPEC-1"
        with service.kernel.transaction(read_only=True) as tx:
            link = tx.get("project_artifact_links", {"id": f"LINK-{spec_id}"})
        link.update(version=2, status="retired", changed_at=datetime.now(UTC).isoformat())
        service.kernel.mutate_current(
            table="project_artifact_links",
            identity={"id": link["id"]},
            expected_version=1,
            new_state=link,
            actor="qualification",
            reason="Remove the canonical formal relationship",
        )
        changed = client.get("/v1/work-items/WI-1/context")
        assert {row["id"] for row in changed.json()["specifications"]} == {"SPEC-1"}
    elif changed_scope == "test_formal_cited":
        changed = put(client, "tests", "TEST-1", {"spec_id": "SPEC-ADDED"}, expected_version=1)
    elif changed_scope in {"project_formal", "test_formal"}:
        changed = put(
            client, "specifications", "SPEC-ADDED", {"title": "Additional current requirement", "status": "active"}
        )
        assert changed.status_code == 200, changed.text
        if changed_scope == "project_formal":
            link_project_formal(service, "SPEC-ADDED")
        else:
            changed = put(client, "tests", "TEST-1", {"spec_id": "SPEC-ADDED"}, expected_version=1)
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
    if next_status == "GO" and changed_scope in {
        "project_formal_removed",
        "project_formal_overlap_removed",
        "test_formal_cited",
    }:
        deliver(client, contexts, "chain", "lo3", 2, "NO-GO")
        current = client.get("/v1/work-items/WI-1/context").json()
        deliver(
            client,
            contexts,
            "chain",
            "pb3",
            3,
            "REVISED",
            spec_versions=json.dumps({row["id"]: row["version"] for row in current["specifications"]}),
        )
        deliver(client, contexts, "chain", "lo2", 4, "GO")
        assert claim(client, "chain", "pb2", 4, "READY").status_code == 200


def test_changed_scope_can_be_rejected_and_revised_without_reusing_the_old_proposal(bridge):
    _, client, contexts, _ = bridge
    deliver(client, contexts, "chain", "pb1", 1, "NEW")
    changed = put(client, "work-items", "WI-1", {"description": "Corrected required effect"}, expected_version=1)
    assert changed.status_code == 200, changed.text
    deliver(client, contexts, "chain", "lo1", 2, "NO-GO")
    deliver(client, contexts, "chain", "pb2", 3, "REVISED", work_item_version=2)
    deliver(client, contexts, "chain", "lo2", 4, "GO")
    assert claim(client, "chain", "pb3", 4, "READY").status_code == 200


def test_proposal_requires_transitive_formals_before_delivery_and_rechecks_them(bridge):
    service, client, contexts, _ = bridge
    assert (
        put(client, "specifications", "GOV-1", {"title": "Required constraint", "status": "active"}).status_code == 200
    )
    assert put(client, "specifications", "SPEC-1", {"affected_by": ["GOV-1"]}, expected_version=1).status_code == 200
    reserved = claim(client, "chain", "pb1", 0, "NEW").json()
    fence = {"native_context_id": "pb1", "fence": reserved["fence"]}
    missing = client.post(
        "/v1/bridge/chain/deliver",
        json={**fence, "content": authored(contexts["pb1"], "chain", 1, "NEW")},
    )
    assert missing.status_code == 422, missing.text
    assert missing.json()["error"]["code"] == "incomplete_formal_scope"
    assert missing.json()["error"]["details"]["ids"] == ["GOV-1"]
    assert client.post("/v1/bridge/chain/check", json=fence).status_code == 200
    accepted = client.post(
        "/v1/bridge/chain/deliver",
        json={
            **fence,
            "content": authored(
                contexts["pb1"], "chain", 1, "NEW", spec_versions=json.dumps({"GOV-1": 1, "SPEC-1": 2})
            ),
        },
    )
    assert accepted.status_code == 200, accepted.text
    assert (
        put(client, "specifications", "GOV-1", {"description": "Changed constraint"}, expected_version=1).status_code
        == 200
    )
    refused = claim(client, "chain", "lo1", 1, "GO")
    assert refused.status_code == 422 and refused.json()["error"]["code"] == "scope_changed"
    deliver(client, contexts, "chain", "lo1", 2, "NO-GO")
    fresh = client.get("/v1/work-items/WI-1/context").json()
    assert next(row for row in fresh["specifications"] if row["id"] == "GOV-1")["version"] == 2
    deliver(
        client,
        contexts,
        "chain",
        "pb2",
        3,
        "REVISED",
        spec_versions=json.dumps({row["id"]: row["version"] for row in fresh["specifications"]}),
    )
    deliver(client, contexts, "chain", "lo2", 4, "GO")
    assert claim(client, "chain", "pb3", 4, "READY").status_code == 200


@pytest.mark.parametrize("status", ["NEW", "REVISED"])
@pytest.mark.parametrize("changed_source", ["formal", "work"])
def test_proposal_cannot_silently_bind_newer_inputs_than_its_author_read(bridge, status, changed_source):
    service, client, contexts, _ = bridge
    head, author = 0, "pb1"
    if status == "REVISED":
        deliver(client, contexts, "chain", "pb1", 1, "NEW")
        deliver(client, contexts, "chain", "lo1", 2, "NO-GO")
        head, author = 2, "pb2"
    observed = client.get("/v1/work-items/WI-1/context").json()
    source_versions = {row["id"]: row["version"] for row in observed["specifications"]}
    reserved = claim(client, "chain", author, head, status).json()
    fence = {"native_context_id": author, "fence": reserved["fence"]}
    delayed = authored(
        contexts[author],
        "chain",
        head + 1,
        status,
        spec_versions=json.dumps(source_versions),
        work_item_version=observed["work_item"]["version"],
    )
    domain, identifier = ("specifications", "SPEC-1") if changed_source == "formal" else ("work-items", "WI-1")
    assert (
        put(
            client,
            domain,
            identifier,
            {"description": "A materially different requirement"},
            expected_version=1,
        ).status_code
        == 200
    )
    refused = client.post("/v1/bridge/chain/deliver", json={**fence, "content": delayed})
    assert refused.status_code == 422, refused.text
    assert refused.json()["error"]["code"] == "scope_changed"
    assert refused.json()["error"]["details"]["id"] == identifier
    assert client.post("/v1/bridge/chain/check", json=fence).status_code == 200
    with service.kernel.transaction(read_only=True) as tx:
        tx.cursor.execute(
            sql.SQL("SELECT head_version FROM {}.bridge_attempts WHERE id='chain'").format(sql.Identifier(tx.schema))
        )
        assert tx.cursor.fetchone()["head_version"] == head
    fresh = client.get("/v1/work-items/WI-1/context").json()
    corrected = authored(
        contexts[author],
        "chain",
        head + 1,
        status,
        spec_versions=json.dumps({row["id"]: row["version"] for row in fresh["specifications"]}),
        work_item_version=fresh["work_item"]["version"],
    )
    accepted = client.post("/v1/bridge/chain/deliver", json={**fence, "content": corrected})
    assert accepted.status_code == 200, accepted.text


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


@pytest.mark.parametrize("order", list(permutations(range(3))))
def test_every_dispatchable_head_order_delivers_exact_authored_chain(bridge, order):
    _, client, contexts, root = bridge
    document = "head-order"
    previous = None
    for version, (context, status) in enumerate((("pb1", "NEW"), ("lo1", "GO"), ("pb2", "READY")), 1):
        reserved = claim(client, document, context, version - 1, status)
        assert reserved.status_code == 200, reserved.text
        if previous is not None:
            assert reserved.json()["predecessor"]["content"] == previous
        if status == "READY":
            (root / "code.py").write_bytes(b"value = 2\n")
        lines = authored(contexts[context], document, version, status).splitlines()
        content = "\r\n".join([*(lines[i] for i in order), *lines[3:]]) + "\r\n"
        request = {"native_context_id": context, "fence": reserved.json()["fence"], "content": content}
        result = client.post(f"/v1/bridge/{document}/deliver", json=request)
        assert result.status_code == 200, result.text
        retry = client.post(f"/v1/bridge/{document}/deliver", json=request)
        assert retry.status_code == 200 and retry.json()["status"] == "already_delivered"
        previous = content
    reviewer = claim(client, document, "lo2", 3, "VERIFIED")
    assert reviewer.status_code == 200, reviewer.text
    assert reviewer.json()["predecessor"]["content"] == previous
    artifacts = client.get(f"/v1/bridge/{document}/artifacts").json()
    verified = authored(contexts["lo2"], document, 4, "VERIFIED", verified_artifacts=json.dumps(artifacts))
    assert "::init" not in verified and "::open" not in verified
    result = client.post(
        f"/v1/bridge/{document}/deliver",
        json={"native_context_id": "lo2", "fence": reviewer.json()["fence"], "content": verified},
    )
    assert result.status_code == 200, result.text
    assert result.json()["project_ready_for_commit"] is True


@pytest.mark.parametrize(
    "defect", ["status", "version", "context", "recipient", "missing_model", "duplicate_model", "placeholder_model"]
)
def test_verdict_delivery_rejects_changed_authorship_without_rewriting_or_consuming_claim(bridge, defect):
    _, client, contexts, _ = bridge
    document = "authored-verdict"
    deliver(client, contexts, document, "pb1", 1, "NEW")
    reservation = claim(client, document, "lo1", 1, "GO").json()
    original = authored(
        contexts["lo1"],
        document,
        2,
        "GO",
        author_model="agent-selected-model",
        author_model_version="agent-observed-version",
        author_model_configuration="agent-authored-configuration",
    )
    invalid = {
        "status": original.replace("GO\r\n", "NO-GO\r\n", 1),
        "version": original.replace("Version: 2", "Version: 3"),
        "context": original.replace(contexts["lo1"]["session_context_id"], contexts["lo2"]["session_context_id"]),
        "recipient": original.replace("::init gtkb pb", "::init gtkb lo"),
        "missing_model": original.replace("author_model: agent-selected-model\r\n", ""),
        "placeholder_model": original.replace("author_model: agent-selected-model", "author_model: unknown"),
        "duplicate_model": original.replace(
            "author_model: agent-selected-model",
            "author_model: agent-selected-model\r\nauthor_model: substituted-model",
        ),
    }[defect]
    request = {"native_context_id": "lo1", "fence": reservation["fence"], "content": invalid}
    response = client.post(f"/v1/bridge/{document}/deliver", json=request)
    assert response.status_code == 422, response.text
    if defect == "placeholder_model":
        assert "author_model" in response.json()["error"]["message"]
    state = client.get(f"/v1/bridge/{document}/show", params={"include_content": True}).json()
    assert state["attempt"]["head_version"] == 1
    assert len(state["messages"]) == 1
    assert (
        client.post(
            f"/v1/bridge/{document}/check", json={"native_context_id": "lo1", "fence": reservation["fence"]}
        ).status_code
        == 200
    )
    response = client.post(f"/v1/bridge/{document}/deliver", json={**request, "content": original})
    assert response.status_code == 200, response.text
    state = client.get(f"/v1/bridge/{document}/show", params={"include_content": True}).json()
    assert state["messages"][-1]["content"] == original
    assert (
        client.post(
            f"/v1/bridge/{document}/check", json={"native_context_id": "lo1", "fence": reservation["fence"]}
        ).status_code
        == 422
    )


@pytest.mark.parametrize("status", ["NEW", "REVISED"])
@pytest.mark.parametrize("defect", ["project", "work_item", "both", "bold"])
def test_proposals_require_plain_canonical_linkage_without_consuming_claim(bridge, status, defect):
    _, client, contexts, _ = bridge
    document = "proposal-linkage"
    version = 1
    if status == "REVISED":
        deliver(client, contexts, document, "pb1", 1, "NEW")
        deliver(client, contexts, document, "lo1", 2, "NO-GO")
        version = 3
    reserved = claim(client, document, "pb1", version - 1, status).json()
    fence = {"native_context_id": "pb1", "fence": reserved["fence"]}
    original = authored(contexts["pb1"], document, version, status)
    invalid = original
    if defect in {"project", "both"}:
        invalid = invalid.replace("Project: PROJECT-1\r\n", "")
    if defect in {"work_item", "both"}:
        invalid = invalid.replace("Work Item: WI-1\r\n", "")
    if defect == "bold":
        invalid = invalid.replace("Project:", "**Project:**").replace("Work Item:", "**Work Item:**")
    before = client.get(f"/v1/bridge/{document}/show?include_content=true").json()
    response = client.post(f"/v1/bridge/{document}/deliver", json={**fence, "content": invalid})
    assert response.status_code == 422, response.text
    error = response.json()["error"]
    assert error["code"] == "invalid_bridge_header"
    expected = {"project", "work_item"} if defect in {"both", "bold"} else {defect}
    assert expected <= set(error["details"]["fields"])
    assert "Project: <canonical project ID>" in error["message"]
    assert "Work Item: <canonical work-item ID>" in error["message"]
    assert "PAUTH" not in response.text and "Authorization:" not in response.text
    assert client.get(f"/v1/bridge/{document}/show?include_content=true").json() == before
    assert client.post(f"/v1/bridge/{document}/check", json=fence).status_code == 200
    accepted = client.post(f"/v1/bridge/{document}/deliver", json={**fence, "content": original})
    assert accepted.status_code == 200, accepted.text
    assert client.get(f"/v1/bridge/{document}/show?include_content=true").json()["messages"][-1]["content"] == original


@pytest.mark.parametrize("field", ["author_identity", "author_harness_id", "author_session_context_id", "author_model"])
def test_advisory_requires_complete_author_provenance_without_proposal_linkage(bridge, field):
    _, client, contexts, _ = bridge
    document = "advisory-provenance"
    reserved = claim(client, document, "pb1", 0, "ADVISORY", work_item_id=None).json()
    fence = {"native_context_id": "pb1", "fence": reserved["fence"]}
    original = authored(contexts["pb1"], document, 1, "ADVISORY")
    original = original.replace("Project: PROJECT-1\r\n", "").replace("Work Item: WI-1\r\n", "")
    invalid = "\r\n".join(line for line in original.split("\r\n") if not line.startswith(field + ":"))
    response = client.post(f"/v1/bridge/{document}/deliver", json={**fence, "content": invalid})
    assert response.status_code == 422, response.text
    assert response.json()["error"]["details"]["fields"] == [field]
    assert client.get(f"/v1/bridge/{document}/show?include_content=true").json()["messages"] == []
    assert client.post(f"/v1/bridge/{document}/check", json=fence).status_code == 200
    accepted = client.post(f"/v1/bridge/{document}/deliver", json={**fence, "content": original})
    assert accepted.status_code == 200, accepted.text
    state = client.get(f"/v1/bridge/{document}/show?include_content=true").json()
    assert state["attempt"]["work_item_id"] is None
    assert state["messages"][0]["content"] == original


@pytest.mark.parametrize("status", ["GO", "NO-GO", "VERIFIED", "WITHDRAWN"])
def test_successor_uses_exact_claim_linkage_without_reauthoring_proposal_fields(bridge, status):
    _, client, contexts, _ = bridge
    document = "claimed-linkage"
    deliver(client, contexts, document, "pb1", 1, "NEW")
    version, context = 2, "lo1"
    extra = {}
    if status == "VERIFIED":
        deliver(client, contexts, document, "lo1", 2, "GO")
        deliver(client, contexts, document, "pb2", 3, "READY")
        version, context = 4, "lo2"
        extra["verified_artifacts"] = json.dumps(client.get(f"/v1/bridge/{document}/artifacts").json())
    elif status == "WITHDRAWN":
        context = "pb2"
    reserved = claim(client, document, context, version - 1, status)
    assert reserved.status_code == 200, reserved.text
    fence = {"native_context_id": context, "fence": reserved.json()["fence"]}
    content = authored(contexts[context], document, version, status, **extra)
    content = content.replace("Project: PROJECT-1\r\n", "").replace("Work Item: WI-1\r\n", "")
    response = client.post(f"/v1/bridge/{document}/deliver", json={**fence, "content": content})
    assert response.status_code == 200, response.text
    state = client.get(f"/v1/bridge/{document}/show?include_content=true").json()
    assert state["attempt"]["work_item_id"] == "WI-1"
    assert state["attempt"]["project_id"] == "PROJECT-1"
    assert state["attempt"]["head_status"] == status
    if status == "WITHDRAWN":
        assert state["attempt"]["disposition"] == "withdrawn"
    else:
        assert state["messages"][-1]["content"] == content
    assert client.post(f"/v1/bridge/{document}/check", json=fence).status_code == 422


@pytest.mark.parametrize("status", ["NEW", "GO"])
@pytest.mark.parametrize("field,value", [("Project", "PROJECT-OTHER"), ("Work Item", "WI-OTHER")])
def test_authored_linkage_cannot_redirect_the_claimed_work(bridge, status, field, value):
    _, client, contexts, _ = bridge
    document = "foreign-linkage"
    version, context = 1, "pb1"
    if status == "GO":
        deliver(client, contexts, document, "pb1", 1, "NEW")
        version, context = 2, "lo1"
    reserved = claim(client, document, context, version - 1, status).json()
    fence = {"native_context_id": context, "fence": reserved["fence"]}
    before = client.get(f"/v1/bridge/{document}/show?include_content=true").json()
    invalid = authored(contexts[context], document, version, status, **{field: value})
    response = client.post(f"/v1/bridge/{document}/deliver", json={**fence, "content": invalid})
    assert response.status_code == 422 and response.json()["error"]["code"] == "invalid_bridge_header"
    assert client.get(f"/v1/bridge/{document}/show?include_content=true").json() == before
    assert client.post(f"/v1/bridge/{document}/check", json=fence).status_code == 200
    original = authored(contexts[context], document, version, status)
    assert client.post(f"/v1/bridge/{document}/deliver", json={**fence, "content": original}).status_code == 200


@pytest.mark.parametrize(
    "work_item_id",
    ["WI-9999", "WI-AUTO-SPEC-BRIDGE-MODE-CONFIG-TRANSACTIONS-001", "GTKB-SOME-THING-001", "WORKLIST-A-B-C"],
)
def test_canonical_work_item_identifiers_preserve_membership_and_exact_authored_bytes(bridge, work_item_id):
    _, client, contexts, _ = bridge
    assert put(client, "work-items", work_item_id, work_fields(), project_id="PROJECT-1").status_code == 200
    document = "canonical-identifier"
    original = authored(contexts["pb1"], document, 1, "NEW", **{"Work Item": work_item_id})
    assert parse_authored_message(original)["metadata"]["work_item"] == work_item_id
    reserved = claim(client, document, "pb1", 0, "NEW", work_item_id=work_item_id)
    assert reserved.status_code == 200, reserved.text
    response = client.post(
        f"/v1/bridge/{document}/deliver",
        json={"native_context_id": "pb1", "fence": reserved.json()["fence"], "content": original},
    )
    assert response.status_code == 200, response.text
    state = client.get(f"/v1/bridge/{document}/show?include_content=true").json()
    assert state["attempt"]["work_item_id"] == work_item_id
    assert state["attempt"]["project_id"] == "PROJECT-1"
    assert state["messages"][0]["content"] == original


@pytest.mark.parametrize("work_item_id", ["WI-1", "WI-AUTO-SPEC-BRIDGE-MODE-CONFIG-TRANSACTIONS-001"])
@pytest.mark.parametrize("membership_state", ["missing", "inactive"])
@pytest.mark.parametrize("boundary", ["claim", "delivery"])
def test_proposal_rejects_missing_current_parent_for_every_identifier(bridge, work_item_id, membership_state, boundary):
    service, client, contexts, _ = bridge
    if work_item_id != "WI-1":
        assert put(client, "work-items", work_item_id, work_fields(), project_id="PROJECT-1").status_code == 200
    document = "missing-parent"
    reserved = None
    if boundary == "delivery":
        reserved = claim(client, document, "pb1", 0, "NEW", work_item_id=work_item_id).json()
    before = client.get(f"/v1/bridge/{document}/show?include_content=true").json()
    content = authored(contexts["pb1"], document, 1, "NEW", **{"Work Item": work_item_id})
    # Simulate damaged current relationship state, including loss after claim.
    # The supported writer never manufactures an unparented work item.
    with service.kernel.transaction() as tx:
        tx.cursor.execute(
            sql.SQL("SELECT * FROM {}.project_work_item_memberships WHERE work_item_id=%s").format(
                sql.Identifier(tx.schema)
            ),
            (work_item_id,),
        )
        membership = dict(tx.cursor.fetchone())
        mutation = (
            "DELETE FROM {}.project_work_item_memberships WHERE work_item_id=%s"
            if membership_state == "missing"
            else "UPDATE {}.project_work_item_memberships SET status='inactive' WHERE work_item_id=%s"
        )
        tx.cursor.execute(sql.SQL(mutation).format(sql.Identifier(tx.schema)), (work_item_id,))
    if boundary == "claim":
        response = claim(client, document, "pb1", 0, "NEW", work_item_id=work_item_id)
    else:
        response = client.post(
            f"/v1/bridge/{document}/deliver",
            json={"native_context_id": "pb1", "fence": reserved["fence"], "content": content},
        )
    assert response.status_code == 422, response.text
    assert response.json()["error"]["code"] == "invalid_membership"
    assert response.json()["error"]["details"]["work_item_id"] == work_item_id
    assert client.get(f"/v1/bridge/{document}/show?include_content=true").json() == before
    with service.kernel.transaction() as tx:
        if membership_state == "missing":
            tx.cursor.execute(
                sql.SQL("INSERT INTO {}.project_work_item_memberships ({}) VALUES ({})").format(
                    sql.Identifier(tx.schema),
                    sql.SQL(",").join(map(sql.Identifier, membership)),
                    sql.SQL(",").join(sql.Placeholder() for _ in membership),
                ),
                tuple(membership.values()),
            )
        else:
            tx.cursor.execute(
                sql.SQL("UPDATE {}.project_work_item_memberships SET status='active' WHERE work_item_id=%s").format(
                    sql.Identifier(tx.schema)
                ),
                (work_item_id,),
            )
    if reserved is None:
        response = claim(client, document, "pb1", 0, "NEW", work_item_id=work_item_id)
        assert response.status_code == 200, response.text
        reserved = response.json()
    accepted = client.post(
        f"/v1/bridge/{document}/deliver",
        json={"native_context_id": "pb1", "fence": reserved["fence"], "content": content},
    )
    assert accepted.status_code == 200, accepted.text


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
    assert state["attempt"]["formal_roots"] is None
    assert state["attempt"]["terminal_author_session_context_id"] == contexts["pb2"]["session_context_id"]
    proof = client.get("/v1/bridge/withdrawn/delivery", params={"version": 2, "native_context_id": "pb2"})
    assert proof.status_code == 200 and proof.json()["bridge_status"] == "WITHDRAWN"
    for version, context in [(2, "pb1"), (1, "pb1")]:
        missing = client.get("/v1/bridge/withdrawn/delivery", params={"version": version, "native_context_id": context})
        assert missing.json()["error"]["code"] == "bridge_delivery_incomplete"
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
    current = client.get("/v1/work-items/WI-1/context").json()
    deliver(
        client,
        contexts,
        "replacement",
        "pb3",
        1,
        "NEW",
        spec_versions=json.dumps({row["id"]: row["version"] for row in current["specifications"]}),
    )
    with service.kernel.transaction(read_only=True) as tx:
        tx.cursor.execute(sql.SQL("SELECT DISTINCT attempt_id FROM {}.bridge_items").format(sql.Identifier(tx.schema)))
        assert [row["attempt_id"] for row in tx.cursor.fetchall()] == ["replacement"]


@pytest.mark.parametrize(
    "versions",
    [
        "{}",
        "[]",
        '{"SPEC-1": true}',
        '{"SPEC-1": 0}',
        '{"SPEC-1": "1"}',
        '{"SPEC-1": 1.0}',
        '{"SPEC-1": 1, "SPEC-1": 2}',
    ],
)
def test_proposal_requires_unambiguous_observed_integer_source_versions(versions):
    content = authored({"session_context_id": "context"}, "chain", 1, "NEW", spec_versions=versions)
    with pytest.raises(PostgresKernelError) as error:
        parse_authored_message(content)
    assert error.value.code == "invalid_bridge_header"


def test_ids_without_observed_versions_cannot_supply_proposal_scope():
    content = authored({"session_context_id": "context"}, "chain", 1, "NEW")
    content = content.replace('spec_versions: {"SPEC-1": 1}', 'spec_ids: ["SPEC-1"]')
    with pytest.raises(PostgresKernelError) as error:
        parse_authored_message(content)
    assert error.value.code == "invalid_bridge_header"


@pytest.mark.parametrize("version", ["", "0", "-1", "true", "1.0", "2147483647"])
def test_proposal_requires_an_observed_work_item_version(version):
    content = authored({"session_context_id": "context"}, "chain", 1, "NEW", work_item_version=version)
    with pytest.raises(PostgresKernelError) as error:
        parse_authored_message(content)
    assert error.value.code == "invalid_bridge_header"


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
    current = client.get("/v1/work-items/WI-1/context").json()
    deliver(
        client,
        contexts,
        "replacement",
        "pb3",
        1,
        "NEW",
        spec_versions=json.dumps({row["id"]: row["version"] for row in current["specifications"]}),
    )


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
    original_claim = NativeBridgeService.claim

    def simultaneous_claim(self, document, request):
        barrier.wait()
        return original_claim(self, document, request)

    with monkeypatch.context() as racing:
        racing.setattr(NativeBridgeService, "claim", simultaneous_claim)
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


def test_state_report_uses_canonical_queues_and_does_not_change_claims(bridge):
    service, client, contexts, root = bridge
    deliver(client, contexts, "report-chain", "pb1", 1, "NEW")
    before = client.get("/v1/bridge/report-chain/show", params={"include_content": True}).json()
    result = client.get("/v1/bridge/state-report")
    assert result.status_code == 200, result.text
    report = result.json()
    assert report["attempt_counts"] == {"active": 1}
    assert report["active_status_mix"] == [{"status": "NEW", "count": 1}]
    assert report["active_claim_count"] == 0
    assert [row["id"] for row in report["queues"]["lo"]["eligible"]] == ["report-chain"]
    assert not report["queues"]["pb"]["eligible"]
    assert not {"harnesses", "registry_publication"} & report.keys()
    assert client.get("/v1/bridge/report-chain/show", params={"include_content": True}).json() == before
    held = claim(client, "report-chain", "lo1", 1, "GO")
    assert held.status_code == 200, held.text
    claimed = client.get("/v1/bridge/state-report").json()
    assert claimed["active_claim_count"] == 1
    assert not claimed["queues"]["lo"]["eligible"]
    fence = {"native_context_id": "lo1", "fence": held.json()["fence"]}
    assert client.post("/v1/bridge/report-chain/check", json=fence).status_code == 200
    assert client.post("/v1/bridge/report-chain/release", json=fence).status_code == 200
    released = client.get("/v1/bridge/state-report").json()
    assert datetime.fromisoformat(released.pop("observed_at")) >= datetime.fromisoformat(report.pop("observed_at"))
    assert released == report


def test_state_report_counts_and_queues_share_one_snapshot(bridge, monkeypatch):
    service, client, contexts, root = bridge
    deliver(client, contexts, "report-chain", "pb1", 1, "NEW")
    original = NativeBridgeService._queue
    changed = False

    def change_after_first_queue(self, tx, role):
        nonlocal changed
        result = original(self, tx, role)
        if not changed:
            changed = True
            with ThreadPoolExecutor(max_workers=1) as worker:
                worker.submit(deliver, client, contexts, "report-chain", "lo1", 2, "GO").result(timeout=20)
        return result

    monkeypatch.setattr(NativeBridgeService, "_queue", change_after_first_queue)
    result = client.get("/v1/bridge/state-report")
    assert result.status_code == 200, result.text
    report = result.json()
    assert report["active_status_mix"] == [{"status": "NEW", "count": 1}]
    assert report["attempts"][0]["head_status"] == "NEW"
    assert report["attempts"][0]["head_version"] == 1
    assert not report["queues"]["pb"]["eligible"]
    assert [row["id"] for row in report["queues"]["lo"]["eligible"]] == ["report-chain"]
    current = client.get("/v1/bridge/state-report").json()
    assert current["active_status_mix"] == [{"status": "GO", "count": 1}]
    assert current["attempts"][0]["head_status"] == "GO"
    assert current["attempts"][0]["head_version"] == 2
    assert [row["id"] for row in current["queues"]["pb"]["eligible"]] == ["report-chain"]
    assert not current["queues"]["lo"]["eligible"]


@pytest.mark.parametrize("status", ["NEW", "GO", "ADVISORY"])
def test_bridge_credentials_are_refused_without_consuming_a_claim(bridge, status):
    _, client, contexts, root = bridge
    document = "credential-refusal"
    context, version = "pb1", 1
    if status == "GO":
        deliver(client, contexts, document, "pb1", 1, "NEW")
        context, version = "lo1", 2
    work_item_id = None if status == "ADVISORY" else "WI-1"
    reservation = claim(client, document, context, version - 1, status, work_item_id=work_item_id)
    assert reservation.status_code == 200, reservation.text
    fence = reservation.json()["fence"]
    before = client.get(f"/v1/bridge/{document}/show?include_content=true").json()
    clean = authored(contexts[context], document, version, status)
    credential = "AKIA" + "A" * 16
    request = {"native_context_id": context, "fence": fence, "content": clean + credential}
    refused = client.post(f"/v1/bridge/{document}/deliver", json=request)
    assert refused.status_code == 422, refused.text
    assert refused.json()["error"]["code"] == "bridge_credential_detected"
    assert credential not in refused.text
    assert client.get(f"/v1/bridge/{document}/show?include_content=true").json() == before
    assert (
        client.post(
            f"/v1/bridge/{document}/check",
            json={
                "native_context_id": context,
                "fence": fence,
            },
        ).status_code
        == 200
    )
    request["content"] = clean
    accepted = client.post(f"/v1/bridge/{document}/deliver", json=request)
    assert accepted.status_code == 200, accepted.text
    replay = client.post(f"/v1/bridge/{document}/deliver", json=request)
    assert replay.status_code == 200 and replay.json()["status"] == "already_delivered"
    assert not (root / "bridge").exists()


@pytest.mark.parametrize("foreign_path", [None, "code.py", "tests/test_effect.py", "changed_intent", "abandoned"])
def test_killed_publication_resumes_exact_mixture_or_refuses_all_foreign_changes(bridge, foreign_path):
    _service, client, contexts, root = bridge
    project_root = root.parents[2]
    document = "killed-publication"
    deliver(client, contexts, document, "pb1", 1, "NEW")
    deliver(client, contexts, document, "lo1", 2, "GO")
    reserved = claim(client, document, "pb2", 2, "READY").json()
    fence = {"native_context_id": "pb2", "fence": reserved["fence"]}
    opened = client.post(f"/v1/bridge/{document}/worktree", json=fence)
    assert opened.status_code == 200, opened.text
    checkout = Path(opened.json()["path"])
    (checkout / "code.py").write_text("value = 2\n", encoding="utf-8")
    (checkout / "tests/test_effect.py").write_text("assert 2 == 2\n", encoding="utf-8")
    original_test = (root / "tests/test_effect.py").read_bytes()
    unrelated = root / "foreign_tracked.txt"
    unrelated.write_bytes(b"Preserve unrelated work\r\n")
    foreign_index = subprocess.check_output(["git", "-C", str(root), "ls-files", "--stage", "--", unrelated.name])
    payload = {**fence, "expected_artifacts": opened.json()["artifact_preimages"]}
    checkpoint = project_root / "publication-interrupted"
    child = r"""
import json,os,sys,time
from pathlib import Path
from groundtruth_kb.bridge.native import NativeBridgeService, PublishWorkRequest
from groundtruth_kb.config import PostgreSQLConfig
from groundtruth_kb.postgres_kernel import PostgresKernel
replace = os.replace
target = Path(sys.argv[3]).resolve()
def pause_after_first(source, destination):
    replace(source, destination)
    if Path(destination).resolve() == target:
        Path(sys.argv[4]).write_text("first path replaced", encoding="utf-8")
        while True:
            time.sleep(1)
os.replace = pause_after_first
service = NativeBridgeService(PostgresKernel(PostgreSQLConfig(service=os.environ["GTKB_TEST_POSTGRES_SERVICE"])), Path(sys.argv[1]))
service.publish_work("killed-publication", PublishWorkRequest(**json.loads(sys.argv[2])))
"""
    process = subprocess.Popen(
        [sys.executable, "-c", child, str(project_root), json.dumps(payload), str(root / "code.py"), str(checkpoint)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
    )
    try:
        deadline = time.monotonic() + 25
        while not checkpoint.exists() and process.poll() is None and time.monotonic() < deadline:
            time.sleep(0.05)
        assert checkpoint.exists(), "Child never reached the first completed replacement"
    finally:
        if process.poll() is None:
            process.kill()
        stdout, stderr = process.communicate(timeout=10)
    assert process.returncode != 0, (stdout, stderr)
    assert (root / "code.py").read_bytes() == (checkout / "code.py").read_bytes()
    assert (root / "tests/test_effect.py").read_bytes() == original_test
    expected_error = None
    if foreign_path in {"changed_intent", "abandoned"}:
        assert (
            put(
                client,
                "specifications",
                "SPEC-1",
                {"description": "Materially changed intent after interrupted publication"},
                expected_version=1,
            ).status_code
            == 200
        )
        expected_error = "scope_changed"
        if foreign_path == "abandoned":
            assert client.post(f"/v1/bridge/{document}/release", json=fence).status_code == 200
            abandoned = client.post(
                f"/v1/bridge/{document}/abandon",
                json={"native_context_id": "lo2", "expected_version": 2, "reason": "Material intent changed"},
            )
            assert abandoned.status_code == 200, abandoned.text
            expected_error = "stale_bridge_head"
    elif foreign_path:
        (root / foreign_path).write_bytes(b"Foreign mutation must survive\n")
        expected_error = "artifact_preimage_changed"
    before = {name: (root / name).read_bytes() for name in ["code.py", "tests/test_effect.py", unrelated.name]}
    if foreign_path not in {"changed_intent", "abandoned"}:
        assert client.post(f"/v1/bridge/{document}/check", json=fence).status_code == 200
    state = client.get(f"/v1/bridge/{document}/show?include_content=true").json()
    result = client.post(f"/v1/bridge/{document}/publish-work", json=payload)
    if expected_error:
        assert result.status_code == 422
        assert result.json()["error"]["code"] == expected_error
        assert {name: (root / name).read_bytes() for name in before} == before
        assert client.get(f"/v1/bridge/{document}/show?include_content=true").json() == state
    else:
        assert result.status_code == 200, result.text
        for name in ["code.py", "tests/test_effect.py"]:
            assert (root / name).read_bytes() == (checkout / name).read_bytes()
        assert client.post(f"/v1/bridge/{document}/publish-work", json=payload).json() == result.json()
    assert unrelated.read_bytes() == before[unrelated.name]
    assert (
        subprocess.check_output(["git", "-C", str(root), "ls-files", "--stage", "--", unrelated.name]) == foreign_index
    )


@pytest.mark.parametrize("stage", ["GO", "READY", "VERIFIED"])
@pytest.mark.parametrize("roots", [None, {"work": ["FABRICATED"], "test": {}, "project": {}}])
def test_unproven_formal_roots_require_explicit_restart_without_inherited_authority(bridge, stage, roots):
    service, client, contexts, root = bridge
    deliver(client, contexts, "old-attempt", "pb1", 1, "NEW")
    deliver(client, contexts, "old-attempt", "lo1", 2, "GO")
    version = 2
    if stage in {"READY", "VERIFIED"}:
        deliver(client, contexts, "old-attempt", "pb2", 3, "READY")
        version = 3
    if stage == "VERIFIED":
        artifacts = client.get("/v1/bridge/old-attempt/artifacts").json()
        deliver(client, contexts, "old-attempt", "lo2", 4, "VERIFIED", verified_artifacts=json.dumps(artifacts))
        version = 4
    original = (root / "code.py").read_bytes()
    membership = client.get("/v1/work-items/WI-1").json()["membership"]
    with service.kernel.transaction() as tx:
        from psycopg.types.json import Jsonb

        tx.cursor.execute(
            sql.SQL("UPDATE {}.bridge_attempts SET formal_roots=%s WHERE id='old-attempt'").format(
                sql.Identifier(tx.schema)
            ),
            (Jsonb(roots) if roots is not None else None,),
        )
    intended = "READY" if stage == "GO" else "VERIFIED"
    refusal = claim(client, "old-attempt", "pb3" if intended == "READY" else "lo3", version, intended)
    assert refusal.json()["error"]["code"] == "scope_changed"
    before = client.get("/v1/bridge/old-attempt/show?include_content=true").json()
    restarted = client.post(
        "/v1/bridge/old-attempt/abandon",
        json={
            "native_context_id": "lo3",
            "expected_version": version,
            "reason": "Original formal roots cannot be proved; restart from current canonical scope",
        },
    )
    assert restarted.status_code == 200, restarted.text
    closed = client.get("/v1/bridge/old-attempt/show?include_content=true").json()
    assert closed["attempt"]["disposition"] == "abandoned" and "messages" not in closed
    assert closed["attempt"]["head_status"] == before["attempt"]["head_status"]
    assert closed["attempt"]["go_context_id"] is None and closed["attempt"]["verified_artifacts"] is None
    assert claim(client, "replacement", "pb3", 0, "READY").status_code == 422
    current = client.get("/v1/work-items/WI-1/context").json()
    assert current["membership"] == membership
    assert current["work_item"]["resolution_status"] == "open"
    deliver(client, contexts, "replacement", "pb3", 1, "NEW", work_item_version=current["work_item"]["version"])
    attempt = client.get("/v1/bridge/replacement/show").json()["attempt"]
    assert attempt["formal_roots"] == {"work": ["SPEC-1"], "test": {"TEST-1": "SPEC-1"}, "project": {}}
    assert attempt["go_context_id"] is None
    assert (root / "code.py").read_bytes() == original


def test_material_formal_change_after_verified_restarts_same_uncommitted_work(bridge):
    _, client, contexts, root = bridge
    deliver(client, contexts, "reviewed", "pb1", 1, "NEW")
    deliver(client, contexts, "reviewed", "lo1", 2, "GO")
    deliver(client, contexts, "reviewed", "pb2", 3, "READY")
    artifacts = client.get("/v1/bridge/reviewed/artifacts").json()
    deliver(client, contexts, "reviewed", "lo2", 4, "VERIFIED", verified_artifacts=json.dumps(artifacts))
    request = {"native_context_id": "lo3", "expected_version": 4, "reason": "Reconcile formal intent"}
    assert client.post("/v1/bridge/reviewed/abandon", json=request).json()["error"]["code"] == "attempt_still_valid"
    original = (root / "code.py").read_bytes()
    (root / "code.py").write_bytes(original + b"# ordinary byte change\n")
    assert client.post("/v1/bridge/reviewed/abandon", json=request).json()["error"]["code"] == "attempt_still_valid"
    before = client.get("/v1/work-items/WI-1").json()
    changed = put(
        client,
        "specifications",
        "SPEC-1",
        {"description": "New required result after independent verification"},
        expected_version=1,
    )
    assert changed.status_code == 200, changed.text
    assert client.post("/v1/bridge/reviewed/abandon", json=request).status_code == 200
    current = client.get("/v1/work-items/WI-1/context").json()
    assert current["work_item"]["id"] == "WI-1" and current["membership"] == before["membership"]
    assert current["work_item"]["resolution_status"] == "open"
    assert (root / "code.py").read_bytes() == original + b"# ordinary byte change\n"
    deliver(
        client,
        contexts,
        "new-intent",
        "pb3",
        1,
        "NEW",
        work_item_version=current["work_item"]["version"],
        spec_versions=json.dumps({"SPEC-1": 2}),
    )
    assert claim(client, "new-intent", "pb2", 1, "READY").status_code == 422
    deliver(client, contexts, "new-intent", "lo3", 2, "GO")
    for name in ["pb4", "lo4"]:
        contexts[name] = client.post(
            "/v1/sessions/bind", json={"native_context_id": name, "init_command": f"::init gtkb {name[:2]}"}
        ).json()["binding"]
    deliver(client, contexts, "new-intent", "pb4", 3, "READY")
    fresh = client.get("/v1/bridge/new-intent/artifacts").json()
    deliver(client, contexts, "new-intent", "lo4", 4, "VERIFIED", verified_artifacts=json.dumps(fresh))
    assert client.get("/v1/work-items/WI-1").json()["work_item"]["resolution_status"] == "verified"


@pytest.mark.parametrize("context", ["pb1", "lo1"])
def test_advisory_recommendation_neither_dispatches_nor_reserves_work(bridge, context):
    _, client, contexts, _ = bridge
    before = {
        resource: client.get(f"/v1/{resource}/{identifier}").json()
        for resource, identifier in (("work-items", "WI-1"), ("projects", "PROJECT-1"), ("harnesses", "HARNESS-1"))
    }
    document = "informational-advisory"
    reserved = claim(client, document, context, 0, "ADVISORY", work_item_id=None)
    assert reserved.status_code == 200, reserved.text
    content = authored(contexts[context], document, 1, "ADVISORY")
    content = content.replace("Project: PROJECT-1\r\n", "").replace("Work Item: WI-1\r\n", "")
    content += "\r\n## Claim\r\nAdopt this change and launch another harness.\r\n"
    content += "## Owner Decision Needed\r\nNone within the assigned investigation.\r\n"
    assert "Classification Slot" not in content and "Grilling" not in content
    response = client.post(
        f"/v1/bridge/{document}/deliver",
        json={"native_context_id": context, "fence": reserved.json()["fence"], "content": content},
    )
    assert response.status_code == 200, response.text
    attempt = client.get(f"/v1/bridge/{document}/show").json()["attempt"]
    assert attempt["work_item_id"] is None and attempt["project_id"] is None
    for role in ("pb", "lo"):
        queue = client.get("/v1/bridge/queue", params={"role": role}).json()
        assert queue["eligible"] == [] and queue["blocked"] == []
    for resource, identifier in (("work-items", "WI-1"), ("projects", "PROJECT-1"), ("harnesses", "HARNESS-1")):
        assert client.get(f"/v1/{resource}/{identifier}").json() == before[resource]


def test_advisory_follow_up_uses_fresh_chain_and_new_time_authorization(bridge):
    _, client, contexts, _ = bridge
    document = "advisory-follow-up"
    for version, context in ((1, "lo1"), (2, "pb2")):
        deliver(client, contexts, document, context, version, "ADVISORY", work_item_id=None)
    before = client.get(f"/v1/bridge/{document}/show", params={"include_content": True}).json()
    refused = claim(client, document, "pb1", 2, "NEW")
    assert refused.status_code != 200
    assert client.get(f"/v1/bridge/{document}/show", params={"include_content": True}).json() == before
    project = client.get("/v1/projects/PROJECT-1").json()["project"]
    assert (
        client.put(
            "/v1/projects/PROJECT-1/authorization",
            json={
                "authorization": "not authorized",
                "expected_version": project["version"],
                "actor": "qualification",
                "reason": "Owner-selected work ordering",
            },
        ).status_code
        == 200
    )
    refused = claim(client, "separate-implementation", "pb1", 0, "NEW")
    assert refused.status_code != 200
    assert refused.json()["error"]["code"] == "project_not_authorized"
    project = client.get("/v1/projects/PROJECT-1").json()["project"]
    assert (
        client.put(
            "/v1/projects/PROJECT-1/authorization",
            json={
                "authorization": "authorized",
                "expected_version": project["version"],
                "actor": "qualification",
                "reason": "Owner-selected work ordering",
            },
        ).status_code
        == 200
    )
    deliver(client, contexts, "separate-implementation", "pb1", 1, "NEW")
    assert client.get(f"/v1/bridge/{document}/show", params={"include_content": True}).json() == before
    queued = client.get("/v1/bridge/queue", params={"role": "lo"}).json()
    assert [row["id"] for row in queued["eligible"]] == ["separate-implementation"]
