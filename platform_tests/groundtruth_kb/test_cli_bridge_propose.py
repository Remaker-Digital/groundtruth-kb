"""Proposal obligations survive retirement of the file-generation services.

Exercise the native delivery boundary: authored identity and linkage, concrete
artifact paths, exact claims and terminal work. No legacy registry or helper is
an input to these scenarios.
"""

from __future__ import annotations

import json
import os
import re
import socket
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path
from string import Template

import pytest
from groundtruth_kb.bridge.native import parse_authored_message
from groundtruth_kb.bridge.taxonomy import BRIDGE_KIND_BY_STATUS, BridgeKind
from groundtruth_kb.bridge.vocabulary import CANONICAL_STATUSES
from groundtruth_kb.postgres_kernel import PostgresKernelError
from psycopg import sql
from psycopg.types.json import Jsonb

from platform_tests.groundtruth_kb.bridge_fixtures import authored, claim, deliver
from platform_tests.groundtruth_kb.bridge_fixtures import bridge as bridge
from platform_tests.groundtruth_kb.native_fixtures import _serve_authority
from platform_tests.groundtruth_kb.native_fixtures import native as native

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


# An independent statement of the contract, not a list derived from the parser.
EXPECTED_KINDS = {
    "NEW": "implementation_proposal",
    "REVISED": "implementation_proposal",
    "GO": "lo_verdict",
    "NO-GO": "lo_verdict",
    "NOT-READY": "lo_verdict",
    "VERIFIED": "lo_verdict",
    "SUPERSEDED": "lo_verdict",
    "READY": "implementation_report",
    "ADVISORY": "governance_advisory",
    "VERDICT-REJECTED": "governance_review",
    "BLOCKED": "operational_state_change",
    "WITHDRAWN": "operational_state_change",
}


def test_native_kind_contract_covers_exactly_the_current_vocabulary():
    assert set(EXPECTED_KINDS) == set(CANONICAL_STATUSES)
    assert {kind.value for kind in BridgeKind} == set(EXPECTED_KINDS.values())
    assert {status: kind.value for status, kind in BRIDGE_KIND_BY_STATUS.items()} == EXPECTED_KINDS


@pytest.mark.parametrize("status", list(EXPECTED_KINDS))
@pytest.mark.parametrize(
    "kind", sorted(set(EXPECTED_KINDS.values())) + ["index_reconciliation", "prime_proposal", "unknown"]
)
def test_native_parser_status_kind_matrix(status, kind):
    content = authored({"session_context_id": "qualification-context"}, "kind-matrix", 1, status, bridge_kind=kind)
    if kind == EXPECTED_KINDS[status]:
        parsed = parse_authored_message(content)
        assert parsed["status"] == status
        assert parsed["metadata"]["bridge_kind"] == kind
    else:
        with pytest.raises(PostgresKernelError) as refused:
            parse_authored_message(content)
        assert refused.value.code == "invalid_bridge_header"
        assert refused.value.details == {"status": status, "expected_bridge_kind": EXPECTED_KINDS[status]}


@pytest.mark.parametrize("status", ["BLOCKED", "WITHDRAWN", "VERDICT-REJECTED"])
def test_native_kind_mismatch_preserves_claim_and_exact_state(bridge, status):
    service, client, contexts, _ = bridge
    document = "kind-refusal"
    context, head = "pb1", 0
    extra, options = {}, {}
    if status == "BLOCKED":
        # The fixture owns a disposable PostgreSQL schema, never production state.
        with service.kernel.transaction() as tx:
            tx.cursor.execute(
                sql.SQL("UPDATE {}.projects SET {}='not authorized' WHERE id='PROJECT-1'").format(
                    sql.Identifier(tx.schema), sql.Identifier("authorization")
                )
            )
        extra = {"observed_authorization": "not authorized", "authorization_read_at": datetime.now(UTC).isoformat()}
        options = {"mode": "headless"}
    else:
        deliver(client, contexts, document, "pb1", 1, "NEW")
        context, head = "pb2", 1
        if status == "VERDICT-REJECTED":
            deliver(client, contexts, document, "lo1", 2, "GO")
            head = 2
    reservation = claim(client, document, context, head, status)
    assert reservation.status_code == 200, reservation.text
    fence = {"native_context_id": context, "fence": reservation.json()["fence"]}
    before = client.get(f"/v1/bridge/{document}/show?include_content=true").json()
    for kind in sorted(set(EXPECTED_KINDS.values()) - {EXPECTED_KINDS[status]}) + ["index_reconciliation"]:
        response = client.post(
            f"/v1/bridge/{document}/deliver",
            json={
                **fence,
                **options,
                "content": authored(contexts[context], document, head + 1, status, bridge_kind=kind, **extra),
            },
        )
        assert response.status_code == 422, response.text
        assert response.json()["error"]["code"] == "invalid_bridge_header"
        assert response.json()["error"]["details"]["expected_bridge_kind"] == EXPECTED_KINDS[status]
        assert client.get(f"/v1/bridge/{document}/show?include_content=true").json() == before
        assert client.post(f"/v1/bridge/{document}/check", json=fence).status_code == 200
    content = authored(contexts[context], document, head + 1, status, bridge_kind=EXPECTED_KINDS[status], **extra)
    accepted = client.post(f"/v1/bridge/{document}/deliver", json={**fence, **options, "content": content})
    assert accepted.status_code == 200, accepted.text
    after = client.get(f"/v1/bridge/{document}/show?include_content=true").json()
    if status == "WITHDRAWN":
        assert "messages" not in after  # Terminal purge omits payload from readback.
    else:
        assert after["messages"][-1]["content"] == content
    assert client.post(f"/v1/bridge/{document}/check", json=fence).status_code == 422


@pytest.mark.parametrize("status", ["NEW", "REVISED"])
def test_documented_proposal_header_delivers_through_actual_cli(bridge, tmp_path, status):
    _, client, contexts, _ = bridge
    document = "documented-proposal"
    head = 0
    if status == "REVISED":
        deliver(client, contexts, document, "pb1", 1, "NEW")
        deliver(client, contexts, document, "lo1", 2, "NO-GO")
        head = 2
    root = Path(__file__).resolve().parents[2]
    # D15: the one skills source; the baseline directory holds rules and hooks only.
    skill = (root / ".agents/skills/gtkb-propose/SKILL.md").read_text(encoding="utf-8")
    example = re.search(r"## Authored header example\n.*?```text\n(.*?)```", skill, re.S)
    assert example is not None
    with socket.socket() as socket_probe:
        socket_probe.bind(("127.0.0.1", 0))
        port = socket_probe.getsockname()[1]
    process, service_env = _serve_authority(tmp_path, port)
    try:
        config = tmp_path / "client.toml"
        config.write_text(
            '[groundtruth]\nproject_root="."\nauthority_url="http://127.0.0.1:'
            + str(port)
            + '"\ndb_path="unavailable-client.db"\n',
            encoding="utf-8",
        )
        env = {key: value for key, value in service_env.items() if not key.startswith(("PG", "GT_POSTGRES_"))}
        env.pop("GT_AUTHORITY_URL", None)

        def cli(*arguments):
            completed = subprocess.run(
                [sys.executable, "-P", "-m", "groundtruth_kb", "--config", str(config), *arguments, "--json"],
                cwd=tmp_path,
                env=env,
                capture_output=True,
                encoding="utf-8",
                timeout=30,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
            )
            assert completed.returncode == 0, completed.stderr
            return json.loads(completed.stdout)

        current = cli("context", "work-item", "WI-1")
        binding = cli("session", "show", "--native-context-id", "pb1")
        assert binding["session_context_id"] == contexts["pb1"]["session_context_id"]
        reserved = cli(
            "bridge",
            "claim",
            document,
            "--work-item-id",
            current["work_item"]["id"],
            "--native-context-id",
            "pb1",
            "--expected-version",
            str(head),
            "--status",
            status,
            "--request-id",
            "documented-" + status.lower(),
        )
        content = Template(example.group(1)).substitute(
            status=status,
            document=document,
            next_version=head + 1,
            date=datetime.now(UTC).date().isoformat(),
            author_identity="qualified-agent",
            harness_id="HARNESS-1",
            bound_session_id=binding["session_context_id"],
            model="qualification-model",
            project_id=current["project"]["id"],
            work_item_id=current["work_item"]["id"],
            work_item_version=current["work_item"]["version"],
            target_paths_json=json.dumps(["code.py"]),
            test_targets_json=json.dumps(["tests/test_effect.py"]),
            spec_versions_json=json.dumps({row["id"]: row["version"] for row in current["specifications"]}),
            complete_body="Implement the specified effect in code.py and verify it with tests/test_effect.py.\nUnicode: cafÃ© æ¼¢å­—.\n",
        )
        draft = tmp_path / "scratchpad" / binding["session_context_id"] / "proposal.md"
        draft.parent.mkdir(parents=True)
        draft.write_text(content, encoding="utf-8", newline="")
        cli(
            "bridge",
            "deliver",
            document,
            "--native-context-id",
            "pb1",
            "--fence",
            str(reserved["fence"]),
            "--content-file",
            str(draft),
        )
        shown = cli("bridge", "show", document, "--content")
        assert shown["messages"][-1]["content"] == content
        assert not (tmp_path / "unavailable-client.db").exists()
        assert not (tmp_path / "bridge").exists()
    finally:
        process.terminate()
        process.wait(timeout=15)
