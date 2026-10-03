"""Existing-writer correction of imported resolution and irregular parent membership.

These tests prepare historical rows only in the disposable native fixture. They
exercise one final lawful postimage, rather than provisional completion labels.
"""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from groundtruth_kb import native_authority
from groundtruth_kb.authority_api import create_authority_app
from groundtruth_kb.isolation.registry_check import ApplicationRegistryError
from groundtruth_kb.postgres_kernel import TABLE_SPECS, PostgresKernelError, PostgresTransaction
from psycopg import sql

from platform_tests.groundtruth_kb.bridge_fixtures import authorize_project
from platform_tests.groundtruth_kb.native_fixtures import history_count, put, seed, work_fields
from platform_tests.groundtruth_kb.native_fixtures import native as native

pytestmark = pytest.mark.integration

COMMIT = "a" * 40
CHANGE_METADATA = {"version", "changed_at", "changed_by", "change_reason"}


def _raw_change(tx, table, record_id, **fields):
    current = tx.get(table, {"id": record_id}, lock=True)
    state = dict(current) if current else {column: None for column in TABLE_SPECS[table].columns}
    state.update(
        id=record_id,
        changed_at=datetime.now(UTC).isoformat(),
        changed_by="qualification",
        change_reason="Imported historical fixture",
        **fields,
    )
    return tx.mutate(
        table=table,
        identity={"id": record_id},
        expected_version=current["version"] if current else 0,
        new_state=state,
        actor="qualification",
        reason="Imported historical fixture",
    )["record"]


def _historical(native, resolution, *, parents=1, evidence="Historical completion not established"):
    service, client, _, _ = native
    seed(client)
    assert put(client, "projects", "PROJECT-2", {"name": "Explicit execution destination"}).status_code == 200
    assert put(client, "work-items", "WI-1", work_fields(), project_id="PROJECT-1").status_code == 200
    with service.kernel.transaction() as tx:
        _raw_change(
            tx,
            "work_items",
            "WI-1",
            resolution_status=resolution,
            stage="historical-stage",
            completion_evidence=evidence,
            status_detail="Preserve the historical observation",
        )
        original = tx.list("project_work_item_memberships", filters={"work_item_id": "WI-1"})[0]
        if parents == 0:
            _raw_change(tx, "project_work_item_memberships", original["id"], status="removed")
        elif parents == 2:
            _raw_change(
                tx,
                "project_work_item_memberships",
                "PWM-HISTORICAL-2",
                project_id="PROJECT-2",
                work_item_id="WI-1",
                status="active",
                membership_order=20,
                source="historical_fixture",
            )
    authorize_project(client, "PROJECT-1")
    authorize_project(client, "PROJECT-2")
    return service, client


def _snapshot(service):
    with service.kernel.transaction(read_only=True) as tx:
        tx.cursor.execute(sql.SQL("SELECT * FROM {}.bridge_attempts ORDER BY id").format(sql.Identifier(tx.schema)))
        attempts = tx.cursor.fetchall()
        return {
            "work": tx.get("work_items", {"id": "WI-1"}),
            "memberships": tx.list("project_work_item_memberships", filters={"work_item_id": "WI-1"}),
            "projects": [tx.get("projects", {"id": key}) for key in ("PROJECT-1", "PROJECT-2")],
            "history": history_count(service),
            "links": tx.list("project_artifact_links"),
            "attempts": attempts,
        }


def _correct(
    client,
    resolution,
    *,
    project_id=None,
    expected_version=None,
    reason="Exercise native domain behavior",
    **fields,
):
    work = client.get("/v1/work-items/WI-1").json()["work_item"]
    return client.put(
        "/v1/work-items/WI-1",
        json={
            "expected_version": work["version"] if expected_version is None else expected_version,
            "actor": "qualification",
            "reason": reason,
            "fields": {"resolution_status": resolution, **fields},
            **({"project_id": project_id} if project_id else {}),
        },
    )


def _preserved_work(before, after, *, completion_changed=False):
    excluded = CHANGE_METADATA | {"resolution_status"} | ({"completion_evidence"} if completion_changed else set())
    assert {key: value for key, value in after.items() if key not in excluded} == {
        key: value for key, value in before.items() if key not in excluded
    }
    assert after["version"] == before["version"] + 1


def _refused_unchanged(service, result, before, code):
    assert result.status_code in {409, 422}, result.text
    assert result.json()["error"]["code"] == code, result.text
    assert _snapshot(service) == before


def _git_reads(
    monkeypatch,
    *,
    host=None,
    resolved=COMMIT,
    paths=b"code.py\0",
    parents=b"b" * 40,
    current=True,
    skills_declaration=None,
):
    """Author bounded physical Git read responses; no commits or product imports execute in this review."""
    host = Path.cwd().resolve() if host is None else host.resolve()
    repository = host / "registered-historical-repository"
    calls = []

    def resolve(observed_host, reference):
        assert observed_host == host and reference == "platform"
        return repository

    def read(root, *arguments):
        assert root == repository
        calls.append(arguments)
        if arguments[:1] == ("rev-parse",):
            assert arguments == ("rev-parse", "--verify", "--end-of-options", COMMIT + "^{commit}")
            return (resolved + "\n").encode("ascii")
        if arguments[:1] == ("merge-base",):
            assert arguments == ("merge-base", "--is-ancestor", COMMIT, "HEAD")
            if not current:
                raise PostgresKernelError("historical_git_not_current", "The commit survives only as an orphan object")
            return b""
        if arguments[:1] == ("ls-tree",):
            assert arguments == ("ls-tree", "-z", COMMIT, "--", "scripts/harness_projection/profiles.toml")
            return (
                b"100644 blob " + b"d" * 40 + b"\tscripts/harness_projection/profiles.toml\0"
                if skills_declaration is not None
                else b""
            )
        if arguments == ("show", COMMIT + ":scripts/harness_projection/profiles.toml"):
            assert skills_declaration is not None
            return skills_declaration
        if arguments[:1] == ("show",):
            assert arguments == ("show", "-s", "--format=%P", COMMIT)
            return parents + b"\n"
        assert arguments[:5] == ("diff-tree", "--no-commit-id", "-r", "--name-only", "-z")
        assert arguments[-1] == COMMIT
        return paths

    monkeypatch.setattr(native_authority, "resolve_project_repository", resolve)
    monkeypatch.setattr(native_authority, "_historical_git", read)
    return calls


@pytest.mark.parametrize("legacy", ["wont_fix", "not_a_defect", "deferred", "drop"])
def test_status_only_retirement_normalization_preserves_relationships_and_authorization(native, legacy):
    service, client = _historical(native, legacy, parents=2)
    before = _snapshot(service)
    result = _correct(client, "retired")
    assert result.status_code == 200, result.text
    after = _snapshot(service)
    assert after["work"]["resolution_status"] == "retired"
    _preserved_work(before["work"], after["work"])
    assert after["memberships"] == before["memberships"]
    assert after["projects"] == before["projects"]
    assert after["history"] == before["history"] + 1
    assert _correct(client, "retired").status_code == 200
    assert _snapshot(service) == after


@pytest.mark.parametrize(
    "legacy", ["not yet implemented", "not_yet_implemented", "verified", "implemented", "resolved"]
)
def test_one_inspected_open_postimage_preserves_a_valid_parent_and_existing_evidence(native, legacy):
    service, client = _historical(native, legacy)
    before = _snapshot(service)
    result = _correct(client, "open")
    assert result.status_code == 200, result.text
    after = _snapshot(service)
    assert after["work"]["resolution_status"] == "open"
    _preserved_work(before["work"], after["work"])
    assert after["memberships"] == before["memberships"]
    assert after["projects"] == before["projects"]
    assert after["history"] == before["history"] + 1
    with service.kernel.transaction(read_only=True) as tx:
        correction = tx.history("work_items", {"id": "WI-1"})[-1]
    assert correction["new_state"]["resolution_status"] == "open"
    assert correction["prior_version"] == before["work"]["version"]


@pytest.mark.parametrize("parents", [0, 2])
def test_irregular_parent_repair_requires_an_explicit_destination_and_deauthorizes_only_changed_sets(native, parents):
    service, client = _historical(native, "verified", parents=parents)
    before = _snapshot(service)
    _refused_unchanged(service, _correct(client, "open"), before, "project_required")
    result = _correct(client, "open", project_id="PROJECT-1")
    assert result.status_code == 200, result.text
    after = _snapshot(service)
    assert result.json()["membership"]["project_id"] == "PROJECT-1"
    assert [row["project_id"] for row in after["memberships"] if row["status"] == "active"] == ["PROJECT-1"]
    _preserved_work(before["work"], after["work"])
    if parents == 0:
        assert after["memberships"][0]["id"] == before["memberships"][0]["id"]
        assert after["memberships"][0]["version"] == before["memberships"][0]["version"] + 1
        assert after["projects"][0]["authorization"] == "not authorized"
        assert after["projects"][1] == before["projects"][1]
    else:
        prior_retained = next(row for row in before["memberships"] if row["project_id"] == "PROJECT-1")
        retained = next(row for row in after["memberships"] if row["project_id"] == "PROJECT-1")
        assert retained == prior_retained
        assert after["projects"][0] == before["projects"][0]
        assert after["projects"][1]["authorization"] == "not authorized"
    assert after["history"] == before["history"] + 3


def test_a_closed_sole_parent_is_not_an_execution_destination(native):
    service, client = _historical(native, "verified")
    with service.kernel.transaction() as tx:
        _raw_change(tx, "projects", "PROJECT-1", status="retired")
    before = _snapshot(service)
    _refused_unchanged(service, _correct(client, "open"), before, "project_required")
    _refused_unchanged(service, _correct(client, "open", project_id="PROJECT-1"), before, "project_closed")
    result = _correct(client, "open", project_id="PROJECT-2")
    assert result.status_code == 200, result.text
    after = _snapshot(service)
    assert result.json()["membership"]["project_id"] == "PROJECT-2"
    assert all(project["authorization"] == "not authorized" for project in after["projects"])
    assert after["projects"][0]["status"] == "retired"
    _preserved_work(before["work"], after["work"])


def test_a_valid_single_parent_move_stays_on_the_existing_move_route(native):
    service, client = _historical(native, "verified")
    before = _snapshot(service)
    _refused_unchanged(service, _correct(client, "open", project_id="PROJECT-2"), before, "membership_move_required")


def test_ordinary_completion_and_mixed_correction_fields_are_refused(native):
    service, client = _historical(native, "open")
    before = _snapshot(service)
    _refused_unchanged(service, _correct(client, "verified"), before, "work_item_frozen")
    _refused_unchanged(service, _correct(client, "retired"), before, "work_item_frozen")
    _refused_unchanged(service, _correct(client, "open", title="Mixed amendment"), before, "invalid_request")
    result = put(client, "work-items", "WI-NEW", work_fields(resolution_status="verified"), project_id="PROJECT-1")
    _refused_unchanged(service, result, before, "work_item_frozen")
    assert client.get("/v1/work-items/WI-NEW").status_code == 404
    invalid = _correct(client, "implemented")
    assert invalid.status_code == 422
    assert _snapshot(service) == before


def _attempt(service, *, disposition="active", commit=None):
    with service.kernel.transaction() as tx:
        tx.cursor.execute(
            sql.SQL(
                "INSERT INTO {}.bridge_attempts (id,work_item_id,project_id,head_status,disposition,terminal_commit) "
                "VALUES (%s,%s,%s,%s,%s,%s)"
            ).format(sql.Identifier(tx.schema)),
            ("ATTEMPT-HISTORICAL", "WI-1", "PROJECT-1", "VERIFIED", disposition, commit),
        )


def test_an_active_review_attempt_blocks_resolution_reconciliation(native):
    service, client = _historical(native, "verified", parents=2)
    _attempt(service)
    before = _snapshot(service)
    _refused_unchanged(service, _correct(client, "open", project_id="PROJECT-1"), before, "attempt_active")


@pytest.mark.parametrize("legacy", ["verified", "implemented", "resolved"])
def test_canonical_committed_attempts_cannot_be_reopened(native, legacy):
    service, client = _historical(native, legacy)
    _attempt(service, disposition="committed", commit=COMMIT)
    before = _snapshot(service)
    _refused_unchanged(service, _correct(client, "open"), before, "work_item_frozen")


@pytest.mark.parametrize("legacy", ["implemented", "resolved"])
@pytest.mark.parametrize("canonical", [False, True])
def test_legacy_completion_uses_real_git_reads_without_inventing_modern_terminal_facts(
    native, legacy, canonical, monkeypatch
):
    service, client = _historical(native, legacy, evidence="git:" + COMMIT)
    if canonical:
        _attempt(service, disposition="committed", commit=COMMIT)
    before = _snapshot(service)
    calls = _git_reads(monkeypatch)
    result = _correct(client, "verified")
    assert result.status_code == 200, result.text
    after = _snapshot(service)
    assert after["work"]["resolution_status"] == "verified"
    _preserved_work(before["work"], after["work"])
    assert after["memberships"] == before["memberships"]
    assert after["projects"] == before["projects"]
    assert after["history"] == before["history"] + 1
    assert after["links"] == before["links"] and after["attempts"] == before["attempts"]
    assert len(calls) == 4
    assert calls[1] == ("merge-base", "--is-ancestor", COMMIT, "HEAD")


@pytest.mark.parametrize(
    "evidence", ["git:" + COMMIT, COMMIT, COMMIT[:9], "Committed as " + COMMIT, "Earlier git:" + COMMIT]
)
def test_historical_git_shaped_evidence_requires_inspection_without_presuming_no_commit(native, evidence):
    service, client = _historical(native, "resolved", evidence=evidence)
    before = _snapshot(service)
    _refused_unchanged(service, _correct(client, "open"), before, "git_reconciliation_required")


def test_project_activation_commit_evidence_also_protects_terminality(native):
    service, client = _historical(native, "verified")
    with service.kernel.transaction() as tx:
        _raw_change(
            tx,
            "project_artifact_links",
            "LINK-COMMITTED",
            project_id="PROJECT-1",
            artifact_type="git_commit",
            artifact_ref=COMMIT,
            relationship="activation",
            status="active",
        )
    before = _snapshot(service)
    _refused_unchanged(service, _correct(client, "open"), before, "work_item_frozen")


def test_stale_resolution_cas_and_replayed_preimage_change_nothing(native):
    service, client = _historical(native, "verified", parents=2)
    before = _snapshot(service)
    _refused_unchanged(
        service,
        _correct(client, "open", project_id="PROJECT-1", expected_version=before["work"]["version"] - 1),
        before,
        "cas_conflict",
    )
    assert _correct(client, "open", project_id="PROJECT-1").status_code == 200
    after = _snapshot(service)
    _refused_unchanged(
        service,
        _correct(client, "open", project_id="PROJECT-1", expected_version=before["work"]["version"]),
        after,
        "cas_conflict",
    )
    assert _correct(client, "open", project_id="PROJECT-1").status_code == 200
    assert _snapshot(service) == after


def test_parent_repair_deauthorization_and_history_roll_back_together(native, monkeypatch):
    service, client = _historical(native, "verified", parents=2)
    before = _snapshot(service)
    mutate = PostgresTransaction.mutate
    observed = []

    def fail_after_deauthorization(tx, **request):
        result = mutate(tx, **request)
        if request["table"] == "projects":
            observed.append(
                (
                    tx.get("project_work_item_memberships", {"id": "PWM-HISTORICAL-2"})["status"],
                    result["record"]["authorization"],
                )
            )
            raise PostgresKernelError("injected_failure", "Abort after membership and authorization history writes")
        return result

    with monkeypatch.context() as patch:
        patch.setattr(PostgresTransaction, "mutate", fail_after_deauthorization)
        result = _correct(client, "open", project_id="PROJECT-1")
    _refused_unchanged(service, result, before, "injected_failure")
    assert observed == [("removed", "not authorized")]


@pytest.mark.parametrize("legacy", ["implemented", "resolved", "verified"])
def test_inspected_evidence_repair_records_scope_reason_and_only_changes_existing_work_columns(
    native, monkeypatch, legacy
):
    service, client = _historical(native, legacy)
    before = _snapshot(service)
    _git_reads(monkeypatch)
    reason = (
        "Inspected the delivered code.py slice against this work's intent; a Git citation alone does not prove scope"
    )
    result = _correct(client, "verified", completion_evidence="git:" + COMMIT, reason=reason)
    assert result.status_code == 200, result.text
    after = _snapshot(service)
    assert after["work"]["resolution_status"] == "verified"
    assert after["work"]["completion_evidence"] == "git:" + COMMIT
    assert after["work"]["change_reason"] == reason and after["work"]["changed_by"] == "qualification"
    _preserved_work(before["work"], after["work"], completion_changed=True)
    assert after["memberships"] == before["memberships"] and after["projects"] == before["projects"]
    assert after["links"] == before["links"] and after["attempts"] == before["attempts"]
    assert after["history"] == before["history"] + 1
    assert _correct(client, "verified", completion_evidence="git:" + COMMIT, reason=reason).status_code == 200
    assert _snapshot(service) == after


def test_historical_reads_use_the_api_configured_host_not_an_inferred_repository(native, monkeypatch, tmp_path):
    service, _ = _historical(native, "resolved")
    host = tmp_path / "selected-authority-host"
    calls = _git_reads(monkeypatch, host=host)
    with TestClient(create_authority_app(service, project_root=host)) as client:
        result = _correct(client, "verified", completion_evidence="git:" + COMMIT)
    assert result.status_code == 200, result.text
    assert len(calls) == 4


@pytest.mark.parametrize("parents", [0, 2])
def test_historical_commit_never_guesses_missing_or_multiple_project_membership(native, parents):
    service, client = _historical(native, "resolved", parents=parents)
    before = _snapshot(service)
    _refused_unchanged(
        service, _correct(client, "verified", completion_evidence="git:" + COMMIT), before, "invalid_membership"
    )


def test_historical_commit_requires_a_current_explicit_repository(native):
    service, client = _historical(native, "resolved")
    with service.kernel.transaction() as tx:
        _raw_change(tx, "projects", "PROJECT-1", repository_ref=None)
    before = _snapshot(service)
    _refused_unchanged(
        service,
        _correct(client, "verified", completion_evidence="git:" + COMMIT),
        before,
        "project_repository_required",
    )


def test_historical_commit_refuses_an_unresolvable_registered_repository(native, monkeypatch):
    service, client = _historical(native, "resolved")

    def unavailable(*args):
        raise ApplicationRegistryError("The registered repository is unavailable")

    monkeypatch.setattr(native_authority, "resolve_project_repository", unavailable)
    before = _snapshot(service)
    _refused_unchanged(
        service, _correct(client, "verified", completion_evidence="git:" + COMMIT), before, "invalid_repository_ref"
    )


@pytest.mark.parametrize(
    "paths", [b"", b"bridge/old-verdict.md\0", b"memory/receipt.md\0", b".codex/rules/projection.md\0"]
)
def test_historical_completion_requires_a_substantive_product_change(native, monkeypatch, paths):
    service, client = _historical(native, "resolved")
    before = _snapshot(service)
    _git_reads(monkeypatch, paths=paths)
    _refused_unchanged(
        service,
        _correct(client, "verified", completion_evidence="git:" + COMMIT),
        before,
        "historical_product_change_required",
    )


@pytest.mark.parametrize("parents", [b"", b"b" * 40 + b" " + b"c" * 40])
def test_historical_root_and_merge_reads_have_an_explicit_comparison(native, monkeypatch, parents):
    service, client = _historical(native, "resolved")
    calls = _git_reads(monkeypatch, parents=parents)
    result = _correct(client, "verified", completion_evidence="git:" + COMMIT)
    assert result.status_code == 200, result.text
    assert calls[-1][-2:] == (("--root", COMMIT) if not parents else ("b" * 40, COMMIT))


def test_historical_completion_refuses_a_different_resolved_object(native, monkeypatch):
    service, client = _historical(native, "resolved")
    before = _snapshot(service)
    _git_reads(monkeypatch, resolved="b" * 40)
    _refused_unchanged(
        service, _correct(client, "verified", completion_evidence="git:" + COMMIT), before, "historical_commit_mismatch"
    )


def test_historical_completion_refuses_an_absent_object_in_the_selected_repository(native, monkeypatch):
    service, client = _historical(native, "resolved")
    _git_reads(monkeypatch)

    def absent(*args):
        raise PostgresKernelError("historical_git_unavailable", "The commit is absent from this selected repository")

    monkeypatch.setattr(native_authority, "_historical_git", absent)
    before = _snapshot(service)
    _refused_unchanged(
        service, _correct(client, "verified", completion_evidence="git:" + COMMIT), before, "historical_git_unavailable"
    )


def test_historical_orphan_object_cannot_establish_completion_after_replacement(native, monkeypatch):
    service, client = _historical(native, "resolved")
    before = _snapshot(service)
    calls = _git_reads(monkeypatch, current=False)
    _refused_unchanged(
        service, _correct(client, "verified", completion_evidence="git:" + COMMIT), before, "historical_git_not_current"
    )
    assert calls == [
        ("rev-parse", "--verify", "--end-of-options", COMMIT + "^{commit}"),
        ("merge-base", "--is-ancestor", COMMIT, "HEAD"),
    ]


@pytest.mark.parametrize(
    ("returncode", "error_code"), [(1, "historical_git_not_current"), (128, "historical_git_unavailable")]
)
def test_historical_ancestry_read_distinguishes_noncurrent_from_unavailable(
    monkeypatch, tmp_path, returncode, error_code
):
    def read(command, **options):
        assert command[-4:] == ["merge-base", "--is-ancestor", COMMIT, "HEAD"]
        return native_authority.subprocess.CompletedProcess(command, returncode, stdout=b"", stderr=b"fixture")

    monkeypatch.setattr(native_authority.subprocess, "run", read)
    with pytest.raises(PostgresKernelError) as failure:
        native_authority._historical_git(tmp_path, "merge-base", "--is-ancestor", COMMIT, "HEAD")
    assert failure.value.code == error_code


def test_historical_evidence_cannot_replace_conflicting_canonical_terminal_commit(native):
    service, client = _historical(native, "resolved")
    _attempt(service, disposition="committed", commit="b" * 40)
    before = _snapshot(service)
    _refused_unchanged(
        service, _correct(client, "verified", completion_evidence="git:" + COMMIT), before, "terminal_commit_mismatch"
    )


@pytest.mark.parametrize("evidence", [None, COMMIT, "git:" + COMMIT[:9], "git:HEAD", "git:" + COMMIT.upper()])
def test_historical_completion_accepts_only_exact_full_git_evidence(native, evidence):
    service, client = _historical(native, "resolved")
    before = _snapshot(service)
    _refused_unchanged(
        service, _correct(client, "verified", completion_evidence=evidence), before, "invalid_completion_evidence"
    )


def test_historical_evidence_cannot_be_smuggled_into_ordinary_work_or_other_field_amendments(native):
    service, client = _historical(native, "resolved")
    before = _snapshot(service)
    _refused_unchanged(
        service,
        _correct(client, "verified", completion_evidence="git:" + COMMIT, title="Changed scope"),
        before,
        "invalid_request",
    )
    _refused_unchanged(
        service, _correct(client, "open", completion_evidence="git:" + COMMIT), before, "invalid_completion_evidence"
    )
    assert _correct(client, "open").status_code == 200
    opened = _snapshot(service)
    _refused_unchanged(
        service,
        _correct(client, "verified", completion_evidence="git:" + COMMIT),
        opened,
        "invalid_completion_evidence",
    )
    new = put(client, "work-items", "WI-NEW", work_fields(completion_evidence="git:" + COMMIT), project_id="PROJECT-1")
    assert new.status_code == 422 and new.json()["error"]["code"] == "invalid_completion_evidence"


def test_historical_evidence_write_and_history_roll_back_together(native, monkeypatch):
    service, client = _historical(native, "resolved")
    before = _snapshot(service)
    _git_reads(monkeypatch)
    mutate = PostgresTransaction.mutate

    def fail_after_work(tx, **request):
        result = mutate(tx, **request)
        if request["table"] == "work_items":
            raise PostgresKernelError(
                "injected_failure", "Abort after historical evidence and its history were written"
            )
        return result

    monkeypatch.setattr(PostgresTransaction, "mutate", fail_after_work)
    _refused_unchanged(
        service, _correct(client, "verified", completion_evidence="git:" + COMMIT), before, "injected_failure"
    )


@pytest.mark.parametrize(
    ("legacy", "parents", "rejected"),
    [
        ("verified", 1, "git:" + COMMIT),
        ("implemented", 1, COMMIT),
        ("resolved", 1, "Committed as " + COMMIT[:9]),
        ("resolved", 0, "git:" + COMMIT),
        ("verified", 2, COMMIT[:9]),
    ],
)
def test_inspected_false_completion_clear_preserves_scope_history_and_repairs_only_needed_membership(
    native, legacy, parents, rejected
):
    service, client = _historical(native, legacy, parents=parents, evidence=rejected)
    before = _snapshot(service)
    history_before = client.get("/v1/work-items/WI-1/history").json()["history"]
    reason = (
        "Inspected the assigned three-gate scope: the cited partial test change did not deliver the required "
        "source behaviors. Clear that false completion assertion; retain the Git citation in native history."
    )
    if parents != 1:
        _refused_unchanged(
            service, _correct(client, "open", completion_evidence="", reason=reason), before, "project_required"
        )
    result = _correct(
        client, "open", project_id="PROJECT-1" if parents != 1 else None, completion_evidence="", reason=reason
    )
    assert result.status_code == 200, result.text
    after = _snapshot(service)
    assert after["work"]["resolution_status"] == "open"
    assert after["work"]["completion_evidence"] == ""
    assert after["work"]["change_reason"] == reason
    _preserved_work(before["work"], after["work"], completion_changed=True)
    assert after["links"] == before["links"] and after["attempts"] == before["attempts"]
    assert result.json()["membership"]["project_id"] == "PROJECT-1"
    if parents == 1:
        assert after["memberships"] == before["memberships"] and after["projects"] == before["projects"]
        assert after["history"] == before["history"] + 1
    else:
        assert [row["project_id"] for row in after["memberships"] if row["status"] == "active"] == ["PROJECT-1"]
        changed_project = "PROJECT-1" if parents == 0 else "PROJECT-2"
        for old, new in zip(before["projects"], after["projects"], strict=True):
            if old["id"] == changed_project:
                assert new["authorization"] == "not authorized" and new["version"] == old["version"] + 1
            else:
                assert new == old
        assert after["history"] == before["history"] + 3
    history_after = client.get("/v1/work-items/WI-1/history").json()["history"]
    assert history_after[:-1] == history_before
    assert history_after[-2]["state"]["completion_evidence"] == rejected
    assert history_after[-1]["reason"] == reason and history_after[-1]["actor"] == "qualification"
    assert history_after[-1]["state"]["completion_evidence"] == ""


@pytest.mark.parametrize(
    ("condition", "code"),
    [
        ("active", "attempt_active"),
        ("committed", "work_item_frozen"),
        ("terminal_commit", "work_item_frozen"),
        ("activation", "work_item_frozen"),
        ("stale", "cas_conflict"),
    ],
)
def test_explicit_false_completion_clear_cannot_bypass_attempt_terminal_or_cas_guards(native, condition, code):
    service, client = _historical(native, "verified", parents=2, evidence="git:" + COMMIT)
    if condition == "active":
        _attempt(service)
    elif condition == "committed":
        _attempt(service, disposition="committed", commit=COMMIT)
    elif condition == "terminal_commit":
        _attempt(service, disposition="abandoned", commit=COMMIT)
    elif condition == "activation":
        with service.kernel.transaction() as tx:
            _raw_change(
                tx,
                "project_artifact_links",
                "LINK-COMMITTED",
                project_id="PROJECT-1",
                artifact_type="git_commit",
                artifact_ref=COMMIT,
                relationship="activation",
                status="active",
            )
    before = _snapshot(service)
    result = _correct(
        client,
        "open",
        project_id="PROJECT-1",
        completion_evidence="",
        expected_version=before["work"]["version"] - 1 if condition == "stale" else None,
        reason="Inspected scope does not override a live attempt or genuine canonical terminal facts",
    )
    _refused_unchanged(service, result, before, code)


@pytest.mark.parametrize("replacement", [None, "replacement note", " ", "git:" + COMMIT])
def test_false_completion_return_rejects_nonempty_or_null_replacement_evidence(native, replacement):
    service, client = _historical(native, "resolved", evidence="git:" + COMMIT)
    before = _snapshot(service)
    _refused_unchanged(
        service, _correct(client, "open", completion_evidence=replacement), before, "invalid_completion_evidence"
    )


@pytest.mark.parametrize(("current", "target"), [("open", "open"), ("retired", "open"), ("wont_fix", "retired")])
def test_explicit_evidence_clear_is_confined_to_false_historical_completion(native, current, target):
    service, client = _historical(native, current)
    before = _snapshot(service)
    _refused_unchanged(service, _correct(client, target, completion_evidence=""), before, "invalid_completion_evidence")


@pytest.mark.parametrize("evidence", [None, "", "Unfinished delivery note"])
def test_open_return_without_an_evidence_field_preserves_empty_or_unrelated_text(native, evidence):
    service, client = _historical(native, "resolved", evidence=evidence)
    before = _snapshot(service)
    result = _correct(client, "open", reason="Inspected unfinished scope; no evidence rewrite was requested")
    assert result.status_code == 200, result.text
    after = _snapshot(service)
    _preserved_work(before["work"], after["work"])
    assert after["work"]["completion_evidence"] == evidence
    assert after["memberships"] == before["memberships"] and after["projects"] == before["projects"]


def test_explicit_evidence_clear_parent_repair_and_history_roll_back_together(native, monkeypatch):
    service, client = _historical(native, "resolved", parents=2, evidence="git:" + COMMIT)
    before = _snapshot(service)
    mutate = PostgresTransaction.mutate

    def fail_after_work(tx, **request):
        result = mutate(tx, **request)
        if request["table"] == "work_items":
            assert result["record"]["completion_evidence"] == ""
            raise PostgresKernelError("injected_failure", "Abort after evidence clear and atomic membership correction")
        return result

    monkeypatch.setattr(PostgresTransaction, "mutate", fail_after_work)
    result = _correct(
        client,
        "open",
        project_id="PROJECT-1",
        completion_evidence="",
        reason="Inspected incomplete scope and selected the lawful execution destination",
    )
    _refused_unchanged(service, result, before, "injected_failure")


@pytest.mark.parametrize("declaration", [None, b'[baseline]\nskills_root = ".harness-baseline-configuration/skills"\n'])
def test_generated_agents_skill_commit_cannot_be_historical_product_evidence(native, monkeypatch, declaration):
    service, client = _historical(native, "resolved")
    before = _snapshot(service)
    calls = _git_reads(monkeypatch, paths=b".agents/skills/gtkb-bridge/SKILL.md\0", skills_declaration=declaration)
    _refused_unchanged(
        service,
        _correct(client, "verified", completion_evidence="git:" + COMMIT),
        before,
        "historical_product_change_required",
    )
    assert ("ls-tree", "-z", COMMIT, "--", "scripts/harness_projection/profiles.toml") in calls


def test_real_former_authored_skill_commit_preserves_historical_completion(native, monkeypatch):
    service, client = _historical(native, "resolved")
    _git_reads(
        monkeypatch,
        paths=b".agents/skills/gtkb-bridge/SKILL.md\0",
        skills_declaration=b'[baseline]\nskills_root = ".agents/skills"\n',
    )
    result = _correct(client, "verified", completion_evidence="git:" + COMMIT)
    assert result.status_code == 200, result.text
    assert _snapshot(service)["work"]["completion_evidence"] == "git:" + COMMIT


def test_baseline_skill_commit_needs_no_legacy_declaration_or_alias(native, monkeypatch):
    service, client = _historical(native, "resolved")
    calls = _git_reads(monkeypatch, paths=b".harness-baseline-configuration/skills/gtkb-bridge/SKILL.md\0")
    result = _correct(client, "verified", completion_evidence="git:" + COMMIT)
    assert result.status_code == 200, result.text
    assert not any(call[0] == "ls-tree" for call in calls)
