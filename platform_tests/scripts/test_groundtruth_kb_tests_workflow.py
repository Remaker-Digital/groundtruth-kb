"""Static checks for the dedicated GroundTruth KB platform test workflow."""

from __future__ import annotations

from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
WORKFLOW_PATH = REPO_ROOT / ".github" / "workflows" / "groundtruth-kb-tests.yml"


def _workflow() -> dict:
    return yaml.safe_load(WORKFLOW_PATH.read_text(encoding="utf-8"))


def _on_block(workflow: dict) -> dict:
    return workflow.get("on") or workflow.get(True)


def test_groundtruth_kb_tests_workflow_triggers_on_platform_paths() -> None:
    workflow = _workflow()
    on_block = _on_block(workflow)

    assert "workflow_dispatch" in on_block
    for event in ("pull_request", "push"):
        paths = on_block[event]["paths"]
        assert "groundtruth-kb/**" in paths
        assert ".agents/skills/**" in paths
        assert ".github/ISSUE_TEMPLATE/**" in paths
        assert ".github/pull_request_template.md" in paths
        assert ".github/workflows/groundtruth-kb-tests.yml" in paths


def test_groundtruth_kb_tests_workflow_runs_the_package_pytest_lane_after_harness_derivation() -> None:
    workflow = _workflow()
    job = workflow["jobs"]["platform-tests"]
    steps = job["steps"]

    install_step = next(step for step in steps if step.get("name") == "Install GroundTruth KB test dependencies")
    derivation_step = next(step for step in steps if step.get("name") == "Canonical harness derivation")
    test_step = next(step for step in steps if step.get("name") == "Run GroundTruth KB platform tests")

    assert job["runs-on"] == "ubuntu-latest"
    assert test_step["working-directory"] == "groundtruth-kb"
    assert '"./groundtruth-kb[dev,search,authority]"' in install_step["run"]
    assert "python scripts/check_harness_parity.py --all --validate" in derivation_step["run"]
    assert steps.index(derivation_step) < steps.index(test_step)
    assert "python -m pytest tests/ -q --tb=short" in test_step["run"]
    assert "--junitxml=.pytest-results/groundtruth-kb-tests.xml" in test_step["run"]


def test_native_lane_provisions_the_disposable_fixture_service() -> None:
    """The real fixture rejects a server whose address/port/database are not local test values."""
    workflow = _workflow()
    job = workflow["jobs"]["platform-tests"]
    env = job["env"]
    assert env["GTKB_RUN_POSTGRES_INTEGRATION"] == "1"
    assert env["GTKB_TEST_POSTGRES_SERVICE"] == "gtkb_ci"
    assert env["PGSERVICEFILE"] == "${{ runner.temp }}/gtkb-pg-service.conf"
    assert env["GTKB_CI_PGDATA"] == "${{ runner.temp }}/gtkb-pgdata"

    steps = job["steps"]
    start = next(step for step in steps if step.get("name") == "Start disposable PostgreSQL for native tests")
    stop = next(step for step in steps if step.get("name") == "Stop the owned disposable PostgreSQL cluster")
    tests = next(step for step in steps if step.get("name") == "Run GroundTruth KB platform tests")
    assert start["shell"] == stop["shell"] == "bash"
    assert not start.get("continue-on-error", False)
    assert stop["if"] == "always()"
    assert steps.index(start) < steps.index(tests) < steps.index(stop)

    # Parse the actual emitted libpq configuration; a service-level options value
    # would override PGOPTIONS and break every fixture's per-test schema isolation.
    import configparser

    config = configparser.ConfigParser()
    config.read_string(start["run"].split("<<'GTKB_SERVICE'\n", 1)[1].split("\nGTKB_SERVICE", 1)[0])
    assert dict(config["gtkb_ci"]) == {
        "host": "127.0.0.1",
        "port": "55434",
        "dbname": "postgres",
        "user": "postgres",
    }
    assert 'test ! -e "$GTKB_CI_PGDATA"' in start["run"]
    assert '-o "-h 127.0.0.1 -p 55434" -w start' in start["run"]
    assert "inet_server_addr() = '127.0.0.1'::inet" in start["run"]
    assert "inet_server_port() = 55434" in start["run"]
    assert "current_database() = 'postgres'" in start["run"]
    assert "--auth-local=trust --auth-host=trust" in start["run"]
    assert '"$GTKB_CI_PGDATA/postmaster.pid"' in stop["run"]
    assert '-D "$GTKB_CI_PGDATA" -m fast -w stop' in stop["run"]
    assert '"/proc/$postgres_pid/exe"' in stop["run"]
    assert '"/proc/$postgres_pid/cmdline"' in stop["run"]
