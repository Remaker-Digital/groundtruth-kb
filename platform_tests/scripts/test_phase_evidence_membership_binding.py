"""Phase evidence follows semantic membership through the native authority.

TEST-11861 retains the eight write-side obligations originally scoped by
WI-6126, now on disposable PostgreSQL and current service/HTTP/CLI routes.
SPEC-1605, GOV-13 and DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 apply.

Native requests exclude execution fields. Attempts to copy evidence are
rejected without effects; accepted membership changes clear stored evidence.
Fixtures seed existing evidence through the kernel, as migration can. They
qualify neither an execution-result recorder nor production row reconciliation.
"""

from __future__ import annotations

import json
import os
import socket
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from threading import Barrier

import groundtruth_kb
import pytest
from groundtruth_kb.authority_client import AuthorityClient, AuthorityClientError
from groundtruth_kb.native_authority import TestPhaseMutation as PhaseMutation
from groundtruth_kb.postgres_kernel import PostgresKernelError, PostgresTransaction
from psycopg import sql

from platform_tests.groundtruth_kb.test_native_authority_service import native as native
from platform_tests.groundtruth_kb.test_native_authority_service import put

pytestmark = [pytest.mark.integration, pytest.mark.timeout(120)]
_EXECUTED_AT = "2026-04-04T14:38:03.677803+00:00"
_EVIDENCE = ("last_result", "last_executed_at", "last_executed_on")


def _current(service):
    with service.kernel.transaction(read_only=True) as tx:
        return tx.get("test_plan_phases", {"id": "PHASE-001"})


def _history(service):
    with service.kernel.transaction(read_only=True) as tx:
        tx.cursor.execute(
            sql.SQL(
                "SELECT prior_version,new_version,prior_state,new_state FROM {}.record_history "
                "WHERE record_type='test_plan_phases' AND record_id=%s ORDER BY new_version"
            ).format(sql.Identifier(tx.schema)),
            ('{"id":"PHASE-001"}',),
        )
        return tx.cursor.fetchall()


def _seed(native, test_ids, *, date_only=False, result="PASS"):
    service, client, _, _ = native
    response = put(client, "specifications", "SPEC-1", {"title": "Membership evidence", "status": "active"})
    assert response.status_code == 200, response.text
    for test_id in ("TEST-1", "TEST-2", "TEST-3"):
        response = put(
            client,
            "tests",
            test_id,
            {
                "title": test_id,
                "spec_id": "SPEC-1",
                "test_type": "integration",
                "expected_outcome": "Evidence belongs to the tested membership",
            },
        )
        assert response.status_code == 200, response.text
    response = put(client, "test-plans", "PLAN-001", {"title": "Evidence qualification"})
    assert response.status_code == 200, response.text
    response = put(
        client,
        "test-phases",
        "PHASE-001",
        {
            "plan_id": "PLAN-001",
            "phase_order": 1,
            "title": "Pre-flight Checks",
            "gate_criteria": "all pass",
            "test_ids": test_ids,
        },
    )
    assert response.status_code == 200, response.text
    if result is not None:
        # Existing/migrated evidence is a fixture input, never caller-authored
        # execution evidence accepted by the ordinary phase amendment route.
        with service.kernel.transaction() as tx:
            row = tx.get("test_plan_phases", {"id": "PHASE-001"}, lock=True)
            row.update(
                last_result=result,
                last_executed_at=None if date_only else _EXECUTED_AT,
                last_executed_on="2026-04-04" if date_only else None,
            )
            tx.mutate(
                table="test_plan_phases",
                identity={"id": "PHASE-001"},
                expected_version=row["version"],
                new_state=row,
                actor="qualification",
                reason="Seed existing execution evidence in a disposable schema",
            )
    return _current(service)


def _amend(native, fields, version):
    response = put(native[1], "test-phases", "PHASE-001", fields, expected_version=version)
    assert response.status_code == 200, response.text
    assert response.json() == _current(native[0])
    return response.json()


def _cleared(row):
    assert {key: row[key] for key in _EVIDENCE} == dict.fromkeys(_EVIDENCE)


@pytest.mark.parametrize("date_only", [False, True])
def test_membership_addition_clears_prior_result(native, date_only):
    before = _seed(native, ["TEST-1", "TEST-2"], date_only=date_only)
    row = _amend(native, {"test_ids": ["TEST-1", "TEST-2", "TEST-3"]}, before["version"])
    assert row["test_ids"] == ["TEST-1", "TEST-2", "TEST-3"]
    _cleared(row)


@pytest.mark.parametrize("date_only", [False, True])
def test_membership_removal_clears_prior_result(native, date_only):
    before = _seed(native, ["TEST-1", "TEST-2"], date_only=date_only)
    row = _amend(native, {"test_ids": ["TEST-1"]}, before["version"])
    assert row["test_ids"] == ["TEST-1"]
    _cleared(row)


@pytest.mark.parametrize(
    "supplied",
    [
        {"last_result": "PASS"},
        {"last_executed_at": _EXECUTED_AT},
        {"last_executed_on": "2026-04-04"},
        {"last_result": "PASS", "last_executed_at": _EXECUTED_AT},
    ],
)
def test_explicit_stale_copy_is_cleared_not_trusted(native, supplied):
    """Rejected copies change nothing; the lawful amendment clears old evidence."""
    before = _seed(native, ["TEST-1"])
    history = _history(native[0])
    response = put(
        native[1],
        "test-phases",
        "PHASE-001",
        {"test_ids": ["TEST-1", "TEST-2"], **supplied},
        expected_version=before["version"],
    )
    assert response.status_code == 422, response.text
    assert response.json()["code"] == "invalid_request"
    assert {tuple(item["location"]): item["type"] for item in response.json()["fields"]} == {
        ("body", "fields", field): "extra_forbidden" for field in supplied
    }
    assert _current(native[0]) == before and _history(native[0]) == history
    _cleared(_amend(native, {"test_ids": ["TEST-1", "TEST-2"]}, before["version"]))


def test_update_writer_also_clears_on_membership_change(native):
    """Direct typed service calls obey the same invariant as HTTP amendments."""
    before = _seed(native, ["TEST-1"])
    row = native[0].amend_test_phase(
        "PHASE-001",
        PhaseMutation(
            expected_version=before["version"],
            actor="qualification",
            reason="Change membership",
            fields={"test_ids": ["TEST-1", "TEST-2"]},
        ),
    )
    assert row == _current(native[0])
    _cleared(row)


@pytest.mark.parametrize("fields", [{"title": "Renamed"}, {"test_ids": ["TEST-1", "TEST-2"]}])
@pytest.mark.parametrize("date_only", [False, True])
def test_unchanged_membership_preserves_result(native, fields, date_only):
    before = _seed(native, ["TEST-1", "TEST-2"], date_only=date_only)
    row = _amend(native, fields, before["version"])
    assert {key: row[key] for key in _EVIDENCE} == {key: before[key] for key in _EVIDENCE}


@pytest.mark.parametrize("test_ids", [["TEST-2", "TEST-1"], ["TEST-2", "TEST-1", "TEST-2"]])
def test_idempotent_reordered_membership_preserves_result(native, test_ids):
    before = _seed(native, ["TEST-1", "TEST-2"])
    row = _amend(native, {"test_ids": test_ids}, before["version"])
    assert set(row["test_ids"]) == set(before["test_ids"])
    assert {key: row[key] for key in _EVIDENCE} == {key: before[key] for key in _EVIDENCE}


def test_prior_versions_retain_their_own_evidence(native):
    before = _seed(native, ["TEST-1"])
    history = _history(native[0])
    row = _amend(native, {"test_ids": ["TEST-1", "TEST-2"]}, before["version"])
    after = _history(native[0])
    assert after[:-1] == history
    assert after[-1]["prior_state"] == before and after[-1]["new_state"] == row
    assert after[-1]["new_version"] == before["version"] + 1
    _cleared(after[-1]["new_state"])


def test_injected_failure_rolls_back_membership_and_evidence(native, monkeypatch):
    before = _seed(native, ["TEST-1"])
    history = _history(native[0])
    original = PostgresTransaction.mutate
    written = []

    def fail_after_write(tx, **request):
        result = original(tx, **request)
        if request["table"] == "test_plan_phases":
            written.append(result["record"])
            raise RuntimeError("injected after row and history writes")
        return result

    monkeypatch.setattr(PostgresTransaction, "mutate", fail_after_write)
    with pytest.raises(PostgresKernelError, match="PostgreSQL domain operation failed"):
        native[0].amend_test_phase(
            "PHASE-001",
            PhaseMutation(
                expected_version=before["version"],
                actor="qualification",
                reason="Doomed membership change",
                fields={"test_ids": ["TEST-1", "TEST-2"]},
            ),
        )
    assert len(written) == 1
    assert _current(native[0]) == before and _history(native[0]) == history
    _cleared(written[0])


@pytest.mark.parametrize("test_ids", [[], None])
def test_empty_membership_clears_evidence(native, test_ids):
    before = _seed(native, ["TEST-1"])
    row = _amend(native, {"test_ids": test_ids}, before["version"])
    assert row["test_ids"] == test_ids
    _cleared(row)


@pytest.mark.parametrize("test_ids", [[], None])
def test_absent_evidence_is_not_invented(native, test_ids):
    before = _seed(native, test_ids, result=None)
    _cleared(before)
    _cleared(_amend(native, {"test_ids": ["TEST-1"]}, before["version"]))


@pytest.mark.parametrize("test_ids", [[], None])
def test_empty_membership_representations_are_set_identical(native, test_ids):
    before = _seed(native, test_ids)
    row = _amend(native, {"test_ids": None if test_ids == [] else []}, before["version"])
    assert {key: row[key] for key in _EVIDENCE} == {key: before[key] for key in _EVIDENCE}


def test_stale_membership_amendment_changes_neither_state_nor_history(native):
    before = _seed(native, ["TEST-1"])
    current = _amend(native, {"title": "A newer version"}, before["version"])
    history = _history(native[0])
    response = put(native[1], "test-phases", "PHASE-001", {"test_ids": ["TEST-2"]}, expected_version=before["version"])
    assert response.status_code == 409, response.text
    assert response.json()["error"]["code"] == "cas_conflict"
    assert _current(native[0]) == current and _history(native[0]) == history


def test_missing_test_reference_does_not_clear_evidence(native):
    before = _seed(native, ["TEST-1"])
    history = _history(native[0])
    response = put(
        native[1], "test-phases", "PHASE-001", {"test_ids": ["TEST-MISSING"]}, expected_version=before["version"]
    )
    assert response.status_code == 404, response.text
    assert response.json()["error"]["code"] == "not_found"
    assert _current(native[0]) == before and _history(native[0]) == history


def test_concurrent_membership_amendments_have_one_complete_winner(native):
    before = _seed(native, ["TEST-1"])
    history = _history(native[0])
    barrier = Barrier(2)

    def amend(test_id):
        barrier.wait(timeout=10)
        try:
            return native[0].amend_test_phase(
                "PHASE-001",
                PhaseMutation(
                    expected_version=before["version"],
                    actor="qualification",
                    reason="Competing membership",
                    fields={"test_ids": [test_id]},
                ),
            )
        except PostgresKernelError as error:
            assert error.code in {"cas_conflict", "retryable_conflict"}
            return error.code

    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(amend, ["TEST-2", "TEST-3"]))
    winners = [result for result in results if isinstance(result, dict)]
    assert len(winners) == 1
    row = _current(native[0])
    assert row == winners[0] and row["test_ids"] in [["TEST-2"], ["TEST-3"]]
    assert row["version"] == before["version"] + 1
    assert len(_history(native[0])) == len(history) + 1
    _cleared(row)


def test_ordinary_cli_membership_change_reads_back_cleared_evidence(native, tmp_path):
    before = _seed(native, ["TEST-1"], date_only=True)
    with socket.socket() as listener:
        listener.bind(("127.0.0.1", 0))
        port = listener.getsockname()[1]
    url = f"http://127.0.0.1:{port}"
    server_config = tmp_path / "server.toml"
    server_config.write_text(
        f'[groundtruth]\nproject_root="."\n[postgresql]\nservice="{native[3]}"\n', encoding="utf-8"
    )
    client_config = tmp_path / "client.toml"
    client_config.write_text(f'[groundtruth]\nauthority_url="{url}"\nproject_root="."\n', encoding="utf-8")
    foreign = tmp_path / "foreign"
    foreign.mkdir()
    sentinel = foreign / "groundtruth.db"
    sentinel.write_bytes(b"Must not open this SQLite-looking file")
    base_env = dict(os.environ, PYTHONPATH=str(Path(groundtruth_kb.__file__).resolve().parent.parent))
    for key in ("GT_AUTHORITY_URL", "GT_PROJECT_ROOT", "GTKB_PROJECT_ROOT"):
        base_env.pop(key, None)
    client_env = {key: value for key, value in base_env.items() if not key.startswith(("PG", "GT_POSTGRES_"))}
    client_env["GT_DB_PATH"] = str(sentinel)
    flags = getattr(subprocess, "CREATE_NO_WINDOW", 0)

    def cli(*args):
        return subprocess.run(
            [sys.executable, "-m", "groundtruth_kb", "--config", str(client_config), *args],
            cwd=foreign,
            env=client_env,
            capture_output=True,
            encoding="utf-8",
            timeout=30,
            creationflags=flags,
        )

    with (tmp_path / "service.log").open("wb") as log:
        process = subprocess.Popen(
            [
                sys.executable,
                "-m",
                "groundtruth_kb",
                "--config",
                str(server_config),
                "service",
                "serve",
                "--port",
                str(port),
            ],
            cwd=tmp_path,
            env=base_env,
            stdout=log,
            stderr=log,
            creationflags=flags,
        )
        try:
            deadline = time.monotonic() + 30
            http = AuthorityClient(url, timeout=1)
            while True:
                try:
                    http.request("GET", "/v1/status")
                    break
                except AuthorityClientError:
                    if process.poll() is not None or time.monotonic() >= deadline:
                        pytest.fail("Disposable authority did not start; inspect service.log")
                    time.sleep(0.1)
            fields = tmp_path / "fields.json"
            fields.write_text(json.dumps({"test_ids": ["TEST-1", "TEST-2"]}), encoding="utf-8")
            args = (
                "test-phases",
                "record",
                "--id",
                "PHASE-001",
                "--fields-file",
                str(fields),
                "--expected-version",
                str(before["version"]),
                "--actor",
                "qualification",
                "--change-reason",
                "Amend from a foreign directory",
                "--json",
            )
            written = cli(*args)
            assert written.returncode == 0, written.stderr
            readback = cli("test-phases", "show", "PHASE-001", "--json")
            assert readback.returncode == 0, readback.stderr
            row = json.loads(readback.stdout)
            assert row == json.loads(written.stdout) == _current(native[0])
            assert row["test_ids"] == ["TEST-1", "TEST-2"]
            _cleared(row)
            history = _history(native[0])
            refused = cli(*args)
            assert refused.returncode != 0 and "cas_conflict" in refused.stderr
            assert _current(native[0]) == row and _history(native[0]) == history
        finally:
            process.terminate()
            process.wait(timeout=15)
    assert sentinel.read_bytes() == b"Must not open this SQLite-looking file"
