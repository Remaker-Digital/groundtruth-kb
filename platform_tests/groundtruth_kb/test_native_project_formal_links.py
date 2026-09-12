"""Current project formal roots through native transactions, CLI and Bridge."""

from __future__ import annotations

import json
from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime
from threading import Barrier, Event

import pytest
from groundtruth_kb.bridge import native as native_bridge
from groundtruth_kb.native_authority import ProjectFormalLinkMutation
from groundtruth_kb.postgres_kernel import TABLE_SPECS, PostgresKernelError, PostgresTransaction

from platform_tests.groundtruth_kb.test_native_authority_service import history_count, put, seed, work_fields
from platform_tests.groundtruth_kb.test_native_authority_service import native as native
from platform_tests.groundtruth_kb.test_native_bridge import bridge as bridge
from platform_tests.groundtruth_kb.test_native_bridge import claim, deliver
from platform_tests.groundtruth_kb.test_native_project_dependencies import ready_checkout
from platform_tests.groundtruth_kb.test_project_association_consistency import membership_cli as membership_cli

pytestmark = [pytest.mark.integration, pytest.mark.timeout(120)]


def fields(**extra):
    return {"project_id": "PROJECT-1", "artifact_ref": "SPEC-1", **extra}


def change(client, record_id="LINK-1", *, version=0, **values):
    return put(client, "project-formal-links", record_id, values, expected_version=version)


def test_formal_link_lifecycle_reads_current_roots_and_preserves_project_authorization(native):
    service, client, _, _ = native
    seed(client)
    assert put(client, "work-items", "WI-1", work_fields(), project_id="PROJECT-1").status_code == 200
    project = client.get("/v1/projects/PROJECT-1").json()["project"]
    before = history_count(service)
    linked = change(client, **fields())
    assert linked.status_code == 200, linked.text
    row = linked.json()
    assert row["version"] == 1 and row["artifact_type"] == "spec" and row["relationship"] == "governed_by"
    assert client.get("/v1/project-formal-links/LINK-1").json() == row
    assert client.get("/v1/projects/PROJECT-1").json()["artifact_links"] == [row]
    assert client.get("/v1/project-formal-links", params={"project_id": "PROJECT-1"}).json()["records"] == [row]
    assert client.get("/v1/project-formal-links", params={"project_id": "PROGRAM-1"}).json()["records"] == []
    assert history_count(service) == before + 1
    stale = change(client, version=0, status="retired")
    assert stale.status_code == 409 and stale.json()["error"]["code"] == "cas_conflict"
    assert history_count(service) == before + 1
    for version, status in [(1, "retired"), (2, "active")]:
        result = change(client, version=version, status=status)
        assert result.status_code == 200, result.text
        assert result.json()["version"] == version + 1
        context = client.get("/v1/work-items/WI-1/context").json()
        # SPEC-1 is also a work/test source, so content alone cannot prove roots.
        assert {s["id"] for s in context["specifications"]} == {"SPEC-1"}
        with service.kernel.transaction(read_only=True) as tx:
            from groundtruth_kb.native_authority import _work_formal_roots

            roots = _work_formal_roots(tx, context["work_item"], "PROJECT-1")
        assert roots["project"] == ({"LINK-1": "SPEC-1"} if status == "active" else {})
        assert client.get("/v1/projects/PROJECT-1").json()["project"] == project
    assert history_count(service) == before + 3


@pytest.mark.parametrize(
    "values,code",
    [
        ({}, "formal_link_endpoint_required"),
        ({"project_id": None, "artifact_ref": "SPEC-1"}, "formal_link_endpoint_required"),
        (fields(project_id="MISSING"), "not_found"),
        (fields(project_id="PROGRAM-1"), "program_cannot_contain_work"),
        (fields(artifact_ref="MISSING"), "not_found"),
        (fields(artifact_ref="SPEC-RETIRED"), "inactive_formal_source"),
        (fields(status="retired"), "invalid_formal_link_transition"),
        (fields(status=None), "invalid_formal_link_transition"),
        (fields(artifact_type="git_commit"), "invalid_request"),
        (fields(relationship="activation"), "invalid_request"),
        (fields(authorization="authorized"), "invalid_request"),
    ],
)
def test_invalid_formal_links_refuse_without_row_or_history(native, values, code):
    service, client, _, _ = native
    seed(client)
    assert put(client, "specifications", "SPEC-RETIRED", {"title": "Old rule", "status": "retired"}).status_code == 200
    before = history_count(service)
    result = change(client, **values)
    response = result.json()
    assert result.status_code in {404, 422} and response.get("error", response)["code"] == code, result.text
    if code == "invalid_request":
        rejected = set(values) - {"project_id", "artifact_ref", "status", "notes"}
        assert {item["location"][-1] for item in response["fields"]} == rejected
        assert all(item["type"] == "extra_forbidden" for item in response["fields"])
    assert client.get("/v1/project-formal-links/LINK-1").status_code == 404
    assert history_count(service) == before


@pytest.mark.parametrize("values", [{"project_id": "PROJECT-2"}, {"artifact_ref": "SPEC-2"}])
def test_formal_link_cannot_be_silently_retargeted(native, values):
    service, client, _, _ = native
    seed(client)
    original = change(client, **fields()).json()
    before = history_count(service)
    result = change(client, version=1, **values)
    assert result.status_code == 422 and result.json()["error"]["code"] == "formal_link_identity_frozen"
    assert client.get("/v1/project-formal-links/LINK-1").json() == original
    assert history_count(service) == before


@pytest.mark.parametrize("other_type", ["git_commit", "bridge_thread", "completion_guard"])
def test_formal_link_writer_cannot_rewrite_other_artifact_or_completion_evidence(native, other_type):
    service, client, _, _ = native
    seed(client)
    row = {column: None for column in TABLE_SPECS["project_artifact_links"].columns}
    row.update(
        id="FOREIGN",
        version=1,
        project_id="PROJECT-1",
        artifact_type=other_type,
        artifact_ref="foreign-value",
        relationship="activation",
        status="active",
        changed_at=datetime.now(UTC).isoformat(),
        changed_by="qualification",
        change_reason="Foreign evidence fixture",
    )
    service.kernel.mutate_current(
        table="project_artifact_links",
        identity={"id": "FOREIGN"},
        expected_version=0,
        new_state=row,
        actor="qualification",
        reason="Foreign evidence fixture",
    )
    before = history_count(service)
    result = change(client, "FOREIGN", version=1, **fields())
    assert result.status_code == 422 and result.json()["error"]["code"] == "invalid_formal_link"
    assert client.get("/v1/project-formal-links/FOREIGN").status_code == 404
    assert client.get("/v1/project-formal-links").json()["records"] == []
    with service.kernel.transaction(read_only=True) as tx:
        preserved = tx.get("project_artifact_links", {"id": "FOREIGN"})
    assert preserved["artifact_ref"] == "foreign-value" and preserved["artifact_type"] == other_type
    assert preserved["version"] == 1 and history_count(service) == before


def test_duplicate_and_concurrent_links_produce_one_current_relationship(native):
    service, client, _, _ = native
    seed(client)
    barrier = Barrier(2)
    before = history_count(service)

    def create(record_id):
        barrier.wait(timeout=10)
        try:
            return service.amend_project_formal_link(
                record_id,
                ProjectFormalLinkMutation(
                    expected_version=0,
                    actor="qualification",
                    reason="Concurrent formal linkage",
                    fields=fields(),
                ),
            )
        except PostgresKernelError as error:
            return error.code

    with ThreadPoolExecutor(max_workers=2) as pool:
        outcomes = list(pool.map(create, ["LINK-A", "LINK-B"]))
    assert sum(isinstance(result, dict) for result in outcomes) == 1, outcomes
    assert next(result for result in outcomes if isinstance(result, str)) in {
        "duplicate_formal_link",
        "retryable_conflict",
    }
    assert len(client.get("/v1/project-formal-links").json()["records"]) == 1
    assert history_count(service) == before + 1
    result = change(client, "LINK-THIRD", **fields())
    assert result.status_code == 422 and result.json()["error"]["code"] == "duplicate_formal_link"
    assert history_count(service) == before + 1


def test_link_write_failure_rolls_back_the_row_and_history(native, monkeypatch):
    service, client, _, _ = native
    seed(client)
    before = history_count(service)
    mutate = PostgresTransaction.mutate
    observed = []

    def fail_after_write(tx, **request):
        result = mutate(tx, **request)
        if request["table"] == "project_artifact_links":
            assert tx.get("project_artifact_links", {"id": "LINK-1"}) is not None
            tx.cursor.execute("SELECT count(*) AS n FROM record_history")
            assert tx.cursor.fetchone()["n"] == before + 1
            observed.append(True)
            raise PostgresKernelError("fixture_link_interruption", "Interrupt after the canonical link write")
        return result

    monkeypatch.setattr(PostgresTransaction, "mutate", fail_after_write)
    result = change(client, **fields())
    assert result.status_code == 422 and result.json()["error"]["code"] == "fixture_link_interruption"
    assert observed == [True] and history_count(service) == before
    assert client.get("/v1/project-formal-links/LINK-1").status_code == 404


def test_formal_link_writer_cannot_cross_a_publication_effect(bridge, monkeypatch):
    service, _, _, _ = bridge
    client, root, body = ready_checkout(bridge)
    entered, release, writer_started = Event(), Event(), Event()
    publish = native_bridge.publish_context_work

    def paused(*args, **kwargs):
        entered.set()
        assert release.wait(timeout=10)
        return publish(*args, **kwargs)

    def writer():
        writer_started.set()
        return service.amend_project_formal_link(
            "LINK-LATE",
            ProjectFormalLinkMutation(
                expected_version=0,
                actor="qualification",
                reason="Current project formal root",
                fields=fields(),
            ),
        )

    with monkeypatch.context() as patch:
        patch.setattr(native_bridge, "publish_context_work", paused)
        with ThreadPoolExecutor(max_workers=2) as pool:
            published = pool.submit(client.post, "/v1/bridge/effect-chain/publish-work", json=body)
            assert entered.wait(timeout=10)
            amended = pool.submit(writer)
            try:
                assert writer_started.wait(timeout=10)
                with pytest.raises(TimeoutError):
                    amended.result(timeout=0.2)
            finally:
                release.set()
            result = published.result(timeout=15)
            assert result.status_code == 200, result.text
            assert amended.result(timeout=15)["id"] == "LINK-LATE"
    assert (root / "code.py").read_text() == "result = 42\n"
    before = (root / "code.py").read_bytes()
    result = client.post("/v1/bridge/effect-chain/publish-work", json=body)
    assert result.status_code == 422 and result.json()["error"]["code"] == "scope_changed"
    assert (root / "code.py").read_bytes() == before


@pytest.mark.parametrize("status", ["verified", "retired", "cancelled"])
def test_closed_project_formal_links_are_immutable(native, status):
    service, client, _, _ = native
    seed(client)
    original = change(client, **fields()).json()
    with service.kernel.transaction() as tx:
        project = tx.get("projects", {"id": "PROJECT-1"})
        tx.mutate(
            table="projects",
            identity={"id": "PROJECT-1"},
            expected_version=project["version"],
            new_state={**project, "status": status},
            actor="qualification",
            reason="Closed state fixture",
        )
    before = history_count(service)
    result = change(client, version=1, status="retired")
    assert result.status_code == 422 and result.json()["error"]["code"] == "project_closed"
    assert client.get("/v1/project-formal-links/LINK-1").json() == original
    assert history_count(service) == before


@pytest.mark.parametrize("stage", ["GO", "VERIFIED"])
def test_removed_overlapping_formal_root_refuses_prior_effect_and_requires_fresh_attempt(bridge, stage):
    _, client, contexts, root = bridge
    assert change(client, **fields()).status_code == 200
    deliver(client, contexts, "old-intent", "pb1", 1, "NEW")
    deliver(client, contexts, "old-intent", "lo1", 2, "GO")
    version = 2
    if stage == "VERIFIED":
        deliver(client, contexts, "old-intent", "pb2", 3, "READY")
        artifacts = client.get("/v1/bridge/old-intent/artifacts").json()
        deliver(client, contexts, "old-intent", "lo2", 4, "VERIFIED", verified_artifacts=json.dumps(artifacts))
        version = 4
    before = client.get("/v1/work-items/WI-1").json()
    original = {name: (root / name).read_bytes() for name in ("code.py", "tests/test_effect.py", "foreign_tracked.txt")}
    assert change(client, version=1, status="retired").status_code == 200
    if stage == "GO":
        refused = claim(client, "old-intent", "pb2", version, "READY")
    else:
        project = client.get("/v1/projects/PROJECT-1").json()["project"]
        refused = client.post(
            "/v1/projects/PROJECT-1/prepare-commit",
            json={
                "native_context_id": "lo3",
                "expected_version": project["version"],
            },
        )
    assert refused.status_code == 422 and refused.json()["error"]["code"] == "scope_changed", refused.text
    reconciled = client.post(
        "/v1/bridge/old-intent/abandon",
        json={
            "native_context_id": "lo3",
            "expected_version": version,
            "reason": "The canonical formal root changed",
        },
    )
    assert reconciled.status_code == 200, reconciled.text
    current = client.get("/v1/work-items/WI-1").json()
    assert current["work_item"]["id"] == "WI-1" and current["membership"] == before["membership"]
    assert current["work_item"]["resolution_status"] == "open"
    assert {name: (root / name).read_bytes() for name in original} == original
    deliver(client, contexts, "fresh-intent", "pb3", 1, "NEW", work_item_version=current["work_item"]["version"])
    assert claim(client, "fresh-intent", "pb2", 1, "READY").status_code == 422
    deliver(client, contexts, "fresh-intent", "lo3", 2, "GO")
    attempt = client.get("/v1/bridge/fresh-intent/show").json()["attempt"]
    assert attempt["formal_roots"] == {"work": ["SPEC-1"], "test": {"TEST-1": "SPEC-1"}, "project": {}}


def test_real_cli_formal_link_record_readback_retirement_and_unavailable_refusal(membership_cli, tmp_path):
    service, client, cli, stop = membership_cli
    document = tmp_path / "fields.json"

    def record(version, values):
        document.write_text(json.dumps(values), encoding="utf-8")
        return cli(
            "projects",
            "formal-links",
            "record",
            "--id",
            "LINK-CLI",
            "--fields-file",
            str(document),
            "--expected-version",
            str(version),
            "--actor",
            "qualification",
            "--change-reason",
            "Current roots",
            "--json",
        )

    created = record(0, fields())
    assert created.returncode == 0, created.stderr
    row = json.loads(created.stdout)
    assert client.get("/v1/project-formal-links/LINK-CLI").json() == row
    listed = cli("projects", "formal-links", "list", "--project-id", "PROJECT-1", "--json")
    assert listed.returncode == 0 and json.loads(listed.stdout) == [row]
    text = cli("projects", "formal-links", "list", "--project-id", "PROJECT-1")
    assert text.returncode == 0 and "PROJECT-1 -> SPEC-1 [active]" in text.stdout
    assert record(1, {"status": "retired"}).returncode == 0
    before = client.get("/v1/project-formal-links/LINK-CLI").json()
    history = history_count(service)
    stop()
    unavailable = record(2, {"status": "active"})
    assert unavailable.returncode != 0 and "authority_unavailable" in unavailable.stdout + unavailable.stderr
    assert client.get("/v1/project-formal-links/LINK-CLI").json() == before
    assert history_count(service) == history
