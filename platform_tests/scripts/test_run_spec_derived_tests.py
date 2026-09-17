"""Selected execution observations for DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001.

GOV-SOURCE-OF-TRUTH-FRESHNESS-001: current canonical inputs, no stale pass.
These tests exercise selection and reporting; complete applicability and an
independent review remain separate obligations even when every case passes.
"""

from __future__ import annotations

import copy
import importlib.util
import json
import os
import socket
import subprocess
import sys
import time
from pathlib import Path

import groundtruth_kb
import pytest
from groundtruth_kb.authority_client import AuthorityClient, AuthorityClientError

from platform_tests.groundtruth_kb.test_native_authority_service import native as native_authority_fixture
from platform_tests.groundtruth_kb.test_native_authority_service import put

REPO_ROOT = Path(__file__).resolve().parents[2]
RUNNER_PATH = REPO_ROOT / "scripts/run_spec_derived_tests.py"
pytestmark = pytest.mark.timeout(120)
native = native_authority_fixture


@pytest.fixture
def runner():
    spec = importlib.util.spec_from_file_location("selected_test_runner", RUNNER_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class CurrentAuthority:
    def __init__(self):
        self.specs = {"SPEC-1": {"id": "SPEC-1", "version": 1, "status": "active"}}
        self.tests = []
        self.context = None
        self.calls = []
        self.on_read = None

    def request(self, method, path, *, query=None):
        assert method == "GET"
        self.calls.append((method, path, query))
        if self.on_read:
            self.on_read(path)
        if path.endswith("/context"):
            return copy.deepcopy(self.context)
        if path == "/v1/tests":
            rows = [t for t in self.tests if t["spec_id"] == query["spec_id"]]
            # Deliberately paginate at one record to exercise continuation.
            rows = [t for t in rows if query["after"] is None or t["id"] > query["after"]]
            return {"records": copy.deepcopy(rows[:1]), "next_after": rows[0]["id"] if len(rows) > 1 else None}
        ident = path.rsplit("/", 1)[-1]
        if ident not in self.specs:
            raise AuthorityClientError("not_found", "No current record")
        return copy.deepcopy(self.specs[ident])


def write_test(root, relative="platform_tests/test_probe.py", body=None, docstring="SPEC-1"):
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        f'"""{docstring}"""\n' + (body or "def test_observed():\n    assert 2 + 2 == 4\n"), encoding="utf-8"
    )
    return path


@pytest.fixture
def setup(runner, tmp_path, monkeypatch):
    for key in ("GT_AUTHORITY_URL", "GT_PROJECT_ROOT", "GTKB_PROJECT_ROOT", "GT_DB_PATH"):
        monkeypatch.delenv(key, raising=False)
    config = tmp_path / "groundtruth.toml"
    config.write_text('[groundtruth]\nproject_root="."\nauthority_url="http://127.0.0.1:1"\n', encoding="utf-8")
    authority = CurrentAuthority()
    monkeypatch.setattr(runner, "AuthorityClient", lambda url: authority)
    return runner, tmp_path, config, authority


def observe(setup, capsys, **kwargs):
    runner, _, config, _ = setup
    code = runner.run(config_path=config, spec_ids=["SPEC-1"], json_output=True, **kwargs)
    report = json.loads(capsys.readouterr().out)
    assert report["verification_result"] == "UNASSESSED"
    assert "verified_overall" not in report
    return code, report


@pytest.mark.parametrize("test_root", ["tests", "groundtruth-kb/tests", "platform_tests"])
def test_each_supported_root_runs_real_pytest_without_full_verification(setup, capsys, test_root):
    write_test(setup[1], test_root + "/test_probe.py")
    code, report = observe(setup, capsys)
    assert code == 1 and report["result"] == "PARTIAL"
    assert report["execution_result"] == "PASS" and report["inputs_unchanged"]
    execution = next(iter(report["executions"].values()))
    assert execution["passed"] == 1 and execution["returncode"] == 0


def test_mixed_roots_execute_without_conftest_import_collisions(setup, capsys):
    for test_root in setup[0].TEST_ROOTS:
        write_test(setup[1], test_root + "/test_probe.py")
        (setup[1] / test_root / "conftest.py").write_text("import pytest\n", encoding="utf-8")
    code, report = observe(setup, capsys)
    assert code == 1 and len(report["executions"]) == 3
    assert report["execution_result"] == "PASS"


def test_unknown_requirement_cannot_pass_from_local_docstring(setup, capsys):
    write_test(setup[1])
    setup[3].specs.clear()
    code, report = observe(setup, capsys)
    assert code == 2 and report["problems"] == ["not_found"] and not report["executions"]


@pytest.mark.parametrize("status", ["retired", "superseded", "draft", None])
def test_inactive_requirement_is_visible_failure(setup, capsys, status):
    setup[3].specs["SPEC-1"]["status"] = status
    write_test(setup[1])
    code, report = observe(setup, capsys)
    assert code == 2 and "inactive_requirement" in report["problems"][0]


def test_registry_pagination_and_exact_selector_run_unreferenced_test(setup, capsys):
    write_test(
        setup[1],
        "platform_tests/check.py",
        body="class TestScope:\n    def test_pass(self):\n        assert True\n\ndef test_unselected():\n    assert False\n",
        docstring="No linked requirement",
    )
    setup[3].tests = [
        {
            "id": f"TEST-{n}",
            "version": 1,
            "spec_id": "SPEC-1",
            "test_file": "platform_tests/check.py",
            "test_class": "TestScope",
            "test_function": "test_pass",
            "last_result": "FAIL",
        }
        for n in (1, 2)
    ]
    code, report = observe(setup, capsys)
    assert code == 1 and report["execution_result"] == "PASS"
    assert report["matrix"]["SPEC-1"]["registered_tests"] == ["TEST-1", "TEST-2"]
    assert len(report["executions"]) == 1
    assert any(q and q.get("after") == "TEST-1" for _, _, q in setup[3].calls)


@pytest.mark.parametrize(
    "field,value",
    [
        ("test_file", None),
        ("test_file", "../outside.py"),
        ("test_file", "elsewhere.py"),
        ("test_file", "platform_tests/missing.py"),
        ("test_file", "platform_tests/test_probe.py::test_observed"),
        ("test_class", "--help"),
        ("test_function", "bad()"),
        ("test_function", ""),
    ],
)
def test_invalid_registered_target_cannot_be_waived_by_passing_discovery(setup, capsys, field, value):
    write_test(setup[1])
    row = {"id": "TEST-1", "version": 1, "spec_id": "SPEC-1", "test_file": "platform_tests/test_probe.py"}
    row[field] = value
    setup[3].tests = [row]
    code, report = observe(setup, capsys)
    assert code == 2 and any("TEST-1" in p for p in report["problems"]) and not report["executions"]


def test_function_docstrings_and_longer_identifiers_do_not_supply_coverage(setup, capsys):
    write_test(setup[1], body='def test_pass():\n    """SPEC-1"""\n    assert True\n', docstring="SPEC-10 SPEC-1-EXTRA")
    code, report = observe(setup, capsys)
    assert code == 2 and "SPEC-1: no_derived_tests" in report["problems"]


def test_dry_run_reports_no_execution_or_pass(setup, capsys):
    write_test(setup[1], body="def test_would_fail():\n    assert False\n")
    code, report = observe(setup, capsys, dry_run=True)
    assert code == 1 and report["execution_result"] == "NOT_RUN" and not report["executions"]


@pytest.mark.parametrize(
    "body,reason",
    [
        ("def test_bad():\n    assert False\n", "pytest_nonzero_exit"),
        ("import pytest\ndef test_skip():\n    pytest.skip('unavailable')\n", "incomplete_execution"),
        ("def no_test():\n    pass\n", "pytest_nonzero_exit"),
        ("raise RuntimeError('collection error')\n", "pytest_nonzero_exit"),
    ],
)
def test_real_pytest_incomplete_or_failed_execution_is_nonpassing(setup, capsys, body, reason):
    write_test(setup[1], body=body)
    code, report = observe(setup, capsys)
    assert code == 2 and report["execution_result"] == "FAIL"
    assert next(iter(report["executions"].values()))["reason"] == reason


def test_nonzero_pytest_exit_cannot_be_overridden_by_passing_test(setup, capsys):
    write_test(setup[1])
    (setup[1] / "conftest.py").write_text(
        "def pytest_sessionfinish(session, exitstatus):\n    session.exitstatus = 2\n", encoding="utf-8"
    )
    code, report = observe(setup, capsys)
    execution = next(iter(report["executions"].values()))
    assert code == 2 and execution["passed"] == 1 and execution["returncode"] == 2


def test_actual_pytest_timeout_is_failure(setup, capsys):
    write_test(setup[1], body="import time\ndef test_slow():\n    time.sleep(10)\n")
    code, report = observe(setup, capsys, pytest_timeout_s=1)
    assert code == 2 and next(iter(report["executions"].values()))["reason"] == "pytest_timeout"


@pytest.mark.parametrize("change", ["modify", "add", "delete", "config"])
def test_source_change_during_actual_execution_invalidates_report(setup, capsys, change):
    bodies = {
        "modify": "p=Path(__file__); p.write_text(p.read_text()+'\\n# changed\\n')",
        "add": "Path(__file__).with_name('test_added.py').write_text('def test_new(): pass')",
        "delete": "Path(__file__).unlink()",
        "config": "Path('groundtruth.toml').write_text('[groundtruth]\\n')",
    }
    write_test(setup[1], body="from pathlib import Path\ndef test_change():\n    " + bodies[change] + "\n")
    code, report = observe(setup, capsys)
    assert code == 2 and report["inputs_unchanged"] is False
    assert "selected_inputs_changed" in report["problems"]


@pytest.mark.parametrize("change", ["version", "unavailable", "new_test"])
def test_canonical_change_or_loss_invalidates_passing_execution(setup, capsys, change):
    write_test(setup[1])
    reads = []

    def change_on_second_read(path):
        if path.endswith("/SPEC-1"):
            reads.append(path)
            if len(reads) == 2:
                if change == "unavailable":
                    raise AuthorityClientError("authority_unavailable", "Unavailable")
                if change == "version":
                    setup[3].specs["SPEC-1"]["version"] = 2
                else:
                    setup[3].tests.append({"id": "TEST-2", "version": 1, "spec_id": "SPEC-1"})

    setup[3].on_read = change_on_second_read
    code, report = observe(setup, capsys)
    assert code == 2 and report["result"] == "FAIL"


def test_work_item_selection_uses_current_context_and_preserves_it(setup, capsys):
    write_test(setup[1])
    setup[3].context = {
        "work_item": {"id": "WI-1", "version": 1},
        "specifications": [setup[3].specs["SPEC-1"]],
        "test": None,
    }
    before = copy.deepcopy(setup[3].context)
    code = setup[0].run(config_path=setup[2], work_item="WI-1", json_output=True)
    report = json.loads(capsys.readouterr().out)
    assert code == 1 and report["execution_result"] == "PASS" and setup[3].context == before


@pytest.mark.parametrize("argument", ["--bridge-id", "--advisory", "--strict"])
def test_retired_bridge_and_waiver_modes_are_rejected(runner, argument):
    with pytest.raises(SystemExit) as error:
        runner.main(["--config", "unused.toml", "--spec", "SPEC-1", argument, "old-thread"])
    assert error.value.code == 2


def test_no_authority_has_no_sqlite_or_bridge_fallback(setup, capsys):
    setup[2].write_text('[groundtruth]\nproject_root="."\n', encoding="utf-8")
    sentinel = setup[1] / "groundtruth.db"
    sentinel.write_bytes(b"must remain unopened")
    (setup[1] / "bridge").mkdir()
    bridge = setup[1] / "bridge/probe-001.md"
    bridge.write_text("VERIFIED\nSPEC-1\n", encoding="utf-8")
    code, report = observe(setup, capsys)
    assert code == 2 and report["problems"] == ["native_authority_required"]
    assert sentinel.read_bytes() == b"must remain unopened" and bridge.read_text() == "VERIFIED\nSPEC-1\n"


def test_malformed_source_is_not_silently_omitted(setup, capsys):
    write_test(setup[1], body="def bad syntax\n")
    code, report = observe(setup, capsys)
    assert code == 2 and "invalid_test_source" in report["problems"][0]


def test_native_service_and_separate_cli_report_without_canonical_writes(native, tmp_path):
    service, client, _, service_name = native
    assert (
        put(
            client,
            "specifications",
            "SPEC-1",
            {"title": "Selected behavior", "description": "Keep selected tests bounded", "status": "active"},
        ).status_code
        == 200
    )
    assert (
        put(
            client,
            "tests",
            "TEST-1",
            {
                "title": "Actual selected execution",
                "test_type": "integration",
                "spec_id": "SPEC-1",
                "expected_outcome": "Selected execution is partial",
                "test_file": "platform_tests/test_probe.py",
                "test_function": "test_observed",
            },
        ).status_code
        == 200
    )
    before = {
        domain: client.get(f"/v1/{domain}/{ident}").json()
        for domain, ident in [("specifications", "SPEC-1"), ("tests", "TEST-1")]
    }
    with service.kernel.transaction(read_only=True) as tx:
        history_before = tx.cursor.execute("SELECT count(*) AS count FROM record_history").fetchone()["count"]
    write_test(tmp_path)
    with socket.socket() as listener:
        listener.bind(("127.0.0.1", 0))
        port = listener.getsockname()[1]
    url = f"http://127.0.0.1:{port}"
    server_config = tmp_path / "server.toml"
    server_config.write_text(
        f'[groundtruth]\nproject_root="."\n[postgresql]\nservice="{service_name}"\n', encoding="utf-8"
    )
    config = tmp_path / "client.toml"
    config.write_text(f'[groundtruth]\nproject_root="."\nauthority_url="{url}"\n', encoding="utf-8")
    foreign = tmp_path / "foreign"
    foreign.mkdir()
    sentinel = foreign / "groundtruth.db"
    sentinel.write_bytes(b"unchanged local sentinel")
    env = dict(os.environ, PYTHONPATH=str(Path(groundtruth_kb.__file__).resolve().parent.parent))
    for key in ("GT_AUTHORITY_URL", "GT_PROJECT_ROOT", "GTKB_PROJECT_ROOT"):
        env.pop(key, None)
    flags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
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
            env=env,
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
                        pytest.fail("Disposable service failed to start; inspect service.log")
                    time.sleep(0.1)
            client_env = {k: v for k, v in env.items() if not k.startswith(("PG", "GT_POSTGRES_"))}
            client_env["GT_DB_PATH"] = str(sentinel)
            observed = subprocess.run(
                [sys.executable, str(RUNNER_PATH), "--config", str(config), "--spec", "SPEC-1", "--json"],
                cwd=foreign,
                env=client_env,
                capture_output=True,
                encoding="utf-8",
                timeout=40,
                creationflags=flags,
            )
            assert observed.returncode == 1, observed.stdout + observed.stderr
            report = json.loads(observed.stdout)
            assert report["execution_result"] == "PASS" and report["result"] == "PARTIAL"
            assert report["verification_result"] == "UNASSESSED" and report["inputs_unchanged"]
            for domain, ident in [("specifications", "SPEC-1"), ("tests", "TEST-1")]:
                assert http.request("GET", f"/v1/{domain}/{ident}") == before[domain]
        finally:
            process.terminate()
            process.wait(timeout=15)
    with service.kernel.transaction(read_only=True) as tx:
        assert tx.cursor.execute("SELECT count(*) AS count FROM record_history").fetchone()["count"] == history_before
    assert sentinel.read_bytes() == b"unchanged local sentinel"
