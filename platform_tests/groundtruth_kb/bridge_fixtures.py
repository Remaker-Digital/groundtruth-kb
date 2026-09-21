"""Shared fixtures and helpers of the native bridge qualification (c102, Q-3, owner ruling D23).

Moved verbatim from ``test_native_bridge.py`` (the ``bridge`` fixture, ``authored``, ``claim``,
``deliver``) and ``test_native_project_dependencies.py`` (``ready_checkout``) so that no test
module imports another test module. Not collected; defines no test.
"""

from __future__ import annotations

import json
import subprocess
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from groundtruth_kb.authority_api import create_authority_app
from groundtruth_kb.bridge.native import NativeBridgeService
from groundtruth_kb.bridge.vocabulary import LOYAL_OPPOSITION_ACTIONABLE_STATUSES, PRIME_ACTIONABLE_STATUSES
from groundtruth_kb.postgres_kernel import TABLE_SPECS

from platform_tests.groundtruth_kb.native_fixtures import put, seed, work_fields


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


def ready_checkout(bridge):
    _, client, contexts, root = bridge
    deliver(client, contexts, "effect-chain", "pb1", 1, "NEW")
    deliver(client, contexts, "effect-chain", "lo1", 2, "GO")
    reserved = claim(client, "effect-chain", "pb2", 2, "READY").json()
    fence = {"native_context_id": "pb2", "fence": reserved["fence"]}
    opened = client.post("/v1/bridge/effect-chain/worktree", json=fence).json()
    (Path(opened["path"]) / "code.py").write_text("result = 42\n", encoding="utf-8")
    return client, root, {**fence, "expected_artifacts": opened["artifact_preimages"]}
