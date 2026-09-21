"""Native coherence candidates: retained checks, real CLI/HTTP and snapshot isolation."""

from __future__ import annotations

import hashlib
import json
import os
import socket
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager
from copy import deepcopy
from dataclasses import replace
from pathlib import Path
from threading import Event, Thread

import groundtruth_kb
import pytest
import uvicorn
from click.testing import CliRunner
from groundtruth_kb.authority_api import create_authority_app
from groundtruth_kb.authority_client import AuthorityClient
from groundtruth_kb.cli import main
from groundtruth_kb.coherence import (
    CoherenceRuleError,
    emit_json,
    emit_markdown,
    load_rules,
    make_result,
    run_all,
)
from groundtruth_kb.postgres_kernel import TABLE_SPECS, PostgresTransaction

from platform_tests.groundtruth_kb.native_fixtures import history_count, put
from platform_tests.groundtruth_kb.native_fixtures import native as native


def _hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _write_rules(root: Path) -> Path:
    rules = root / "config" / "governance" / "spec-coherence-rules.toml"
    rules.parent.mkdir(parents=True)
    rules.write_text(
        r"""
[[rules]]
id = "surface-overlap-opposite-polarity"
class = "surface_overlap"
description = "surface overlap"
surface_tags = ["cached_startup_snapshot_authority"]
classification = "contradiction_candidate"
remediation_hint = "clarify authority"

[[rules.polarity_pairs]]
positive = "\\blive\\s+(?:project\\s+)?sources\\b"
negative = "\\bcached\\s+startup\\s+snapshots\\b|\\bcached\\s+summaries\\b"

[[rules]]
id = "authority-hierarchy-invariant"
class = "hierarchy_violation"
description = "hierarchy"
parent_types = ["governance"]
child_types = ["design_constraint"]
polarity_pairs = [
  { positive = "\\bmust\\s+use\\b", negative = "\\bmust\\s+not\\s+use\\b" },
]
classification = "hierarchy_violation_candidate"
remediation_hint = "revise child"

[[rules]]
id = "status-drift"
class = "status_drift"
description = "drift"
classification = "verification_staleness"
remediation_hint = "reverify child"
""".strip()
        + "\n",
        encoding="utf-8",
    )
    return rules


def _write_project(tmp_path: Path) -> tuple[Path, Path, Path]:
    root = tmp_path / "project"
    root.mkdir()
    config = root / "groundtruth.toml"
    config.write_text('[groundtruth]\nauthority_url = "http://127.0.0.1:9"\nproject_root = "."\n', encoding="utf-8")
    rules = _write_rules(root)
    return root, config, rules


def _spec_rows() -> list[dict]:
    return [
        {
            "id": "DCL-SESSION-STARTUP-TOKEN-BUDGET-001",
            "version": 1,
            "title": "Token budget cache",
            "description": "Startup may rely on cached startup snapshots for summaries.",
            "tags": ["cached_startup_snapshot_authority"],
            "status": "active",
            "type": "design_constraint",
            "authority": "",
            "constraints": {},
            "affected_by": [],
            "implementation_verified_at": None,
            "changed_at": "2026-01-01T00:00:00Z",
            "parent": "GOV-SESSION-SELF-INITIALIZATION-001",
        },
        {
            "id": "GOV-SESSION-SELF-INITIALIZATION-001",
            "version": 1,
            "title": "Startup freshness",
            "description": "Startup must use live project sources and must not use cached summaries as authority.",
            "tags": ["cached_startup_snapshot_authority"],
            "status": "active",
            "type": "governance",
            "authority": "",
            "constraints": {},
            "affected_by": [],
            "implementation_verified_at": None,
            "changed_at": "2026-02-01T00:00:00Z",
            "parent": None,
        },
        {
            "id": "GOV-PARENT-001",
            "version": 1,
            "title": "Parent",
            "description": "The platform must not use archived roots.",
            "tags": [],
            "status": "active",
            "type": "governance",
            "authority": "",
            "constraints": {},
            "affected_by": [],
            "implementation_verified_at": None,
            "changed_at": "2026-03-01T00:00:00Z",
            "parent": None,
        },
        {
            "id": "DCL-CHILD-001",
            "version": 1,
            "title": "Child",
            "description": "The child must use archived roots.",
            "tags": [],
            "status": "active",
            "type": "design_constraint",
            "authority": "",
            "constraints": {},
            "affected_by": [],
            "implementation_verified_at": "2026-02-01T00:00:00Z",
            "changed_at": "2026-02-01T00:00:00Z",
            "parent": "GOV-PARENT-001",
        },
    ]


def test_load_rules_valid_and_filter(tmp_path: Path) -> None:
    root, _config, rules_path = _write_project(tmp_path)
    _ = root
    rules = load_rules(rules_path)
    assert [rule.id for rule in rules] == [
        "surface-overlap-opposite-polarity",
        "authority-hierarchy-invariant",
        "status-drift",
    ]
    assert [rule.id for rule in load_rules(rules_path, name="status-drift")] == ["status-drift"]


def test_load_rules_malformed_registry_raises(tmp_path: Path) -> None:
    bad = tmp_path / "bad.toml"
    bad.write_text("[[rules]]\nclass = 'surface_overlap'\n", encoding="utf-8")
    with pytest.raises(CoherenceRuleError, match="missing 'id'"):
        load_rules(bad)


def test_run_all_detects_surface_hierarchy_and_status_drift(tmp_path: Path) -> None:
    root, _config, rules_path = _write_project(tmp_path)
    specs = _spec_rows()
    findings = run_all(specs, load_rules(rules_path))
    by_rule = {finding.rule_id for finding in findings}
    assert "surface-overlap-opposite-polarity" in by_rule
    assert "authority-hierarchy-invariant" in by_rule
    assert "status-drift" in by_rule
    surface = next(f for f in findings if f.rule_id == "surface-overlap-opposite-polarity")
    assert {
        surface.spec_a,
        surface.spec_b,
    } == {"DCL-SESSION-STARTUP-TOKEN-BUDGET-001", "GOV-SESSION-SELF-INITIALIZATION-001"}


def test_emit_json_and_markdown_schema(tmp_path: Path) -> None:
    root, _config, rules_path = _write_project(tmp_path)
    rules = load_rules(rules_path)
    specs = _spec_rows()
    result = make_result(
        authority_url="http://127.0.0.1:9",
        rule_set_path=rules_path,
        specs=specs,
        rules=rules,
        findings=run_all(specs, rules),
    )
    out_json = tmp_path / "findings.json"
    out_md = tmp_path / "summary.md"

    emit_json(result, out_json)
    emit_markdown(result, out_md)

    payload = json.loads(out_json.read_text(encoding="utf-8"))
    assert payload["schema_version"] == 2
    assert payload["assessment"] == "review_candidates_only"
    assert payload["source_consistency"] == "single_read_transaction"
    assert payload["spec_versions"] == {r["id"]: r["version"] for r in specs}
    assert "db_path" not in payload
    assert payload["finding_count"] == len(payload["findings"])
    assert {"rule_id", "spec_a", "spec_b", "surface", "evidence_excerpts", "classification", "remediation_hint"} <= set(
        payload["findings"][0]
    )
    markdown = out_md.read_text(encoding="utf-8")
    assert "## surface_overlap" in markdown
    assert "## hierarchy_violation" in markdown
    assert "## status_drift" in markdown


def _mock_snapshot(monkeypatch, rows=None):
    calls = []
    records = sorted(_spec_rows() if rows is None else rows, key=lambda row: row["id"])

    def request(self, method, path, **kwargs):
        calls.append((method, path, kwargs))
        assert method == "GET" and path == "/v1/specifications/snapshot" and not kwargs
        return {"records": deepcopy(records), "consistency": "single_read_transaction"}

    monkeypatch.setattr(AuthorityClient, "request", request)
    return calls


def test_cli_runs_writes_outputs_and_fail_on_findings(tmp_path, monkeypatch):
    _, config, _ = _write_project(tmp_path)
    calls = _mock_snapshot(monkeypatch)
    out = tmp_path / "out"
    runner = CliRunner()
    result = runner.invoke(main, ["--config", str(config), "validate", "spec-coherence", "--output", str(out)])
    assert result.exit_code == 0, result.output
    assert (out / "findings.json").exists() and (out / "summary.md").exists()
    assert "spec coherence:" in result.output and "review candidates" in result.output
    assert "No verification or completeness claim" in result.output
    assert json.loads((out / "findings.json").read_text())["finding_count"] > 0
    result_fail = runner.invoke(
        main,
        [
            "--config",
            str(config),
            "validate",
            "spec-coherence",
            "--output",
            str(tmp_path / "out2"),
            "--fail-on-findings",
        ],
    )
    assert result_fail.exit_code == 5
    assert len(calls) == 2


def test_cli_json_only_and_read_only_db(tmp_path, monkeypatch):
    # The obligation remains read-only authority access, not SQLite compatibility.
    root, config, _ = _write_project(tmp_path)
    local = root / "groundtruth.db"
    local.write_bytes(b"Unrelated legacy bytes must never be read or changed")
    before = _hash(local)
    calls = _mock_snapshot(monkeypatch)
    out = tmp_path / "json-only"
    result = CliRunner().invoke(
        main, ["--config", str(config), "validate", "spec-coherence", "--output", str(out), "--format", "json"]
    )
    assert result.exit_code == 0, result.output
    assert (out / "findings.json").exists() and not (out / "summary.md").exists()
    assert _hash(local) == before and len(calls) == 1


@pytest.mark.parametrize(
    "invalid",
    [
        {},
        {"rules": []},
    ],
)
def test_empty_rule_configuration_is_not_a_clean_assessment(tmp_path, invalid):
    path = tmp_path / "rules.toml"
    path.write_text("rules = []" if invalid else "")
    with pytest.raises(CoherenceRuleError):
        load_rules(path)


@pytest.mark.parametrize("change", ["class", "duplicate", "tags", "regex"])
def test_invalid_rule_is_rejected_before_authority_access(tmp_path, monkeypatch, change):
    _, config, path = _write_project(tmp_path)
    text = path.read_text()
    if change == "class":
        text = text.replace('class = "surface_overlap"', 'class = "unsupported"')
    elif change == "duplicate":
        text = text.replace('id = "status-drift"', 'id = "authority-hierarchy-invariant"')
    elif change == "tags":
        text = text.replace('surface_tags = ["cached_startup_snapshot_authority"]', 'surface_tags = "wrong shape"')
    else:
        text = text.replace("positive = ", 'positive = "[" # ', 1)
    path.write_text(text)
    calls = _mock_snapshot(monkeypatch)
    out = tmp_path / "failed"
    result = CliRunner().invoke(main, ["--config", str(config), "validate", "spec-coherence", "--output", str(out)])
    assert result.exit_code != 0 and not out.exists() and not calls


def test_surface_candidate_requires_an_actual_shared_named_surface(tmp_path):
    _, _, path = _write_project(tmp_path)
    rule = replace(load_rules(path)[0], surface_tags=("surface-a", "surface-b"))
    a, b = _spec_rows()[:2]
    a.update(title="A", description="Must use live sources", tags=["surface-a"])
    b.update(title="B", description="Use cached startup snapshots", tags=["surface-b"])
    assert run_all([a, b], [rule]) == []
    b["tags"].append("surface-a")
    findings = run_all([a, b], [rule])
    assert len(findings) == 1 and findings[0].surface == "surface-a"


@pytest.mark.parametrize("dependencies", [["GOV-PARENT-001"], '["GOV-PARENT-001"]'])
def test_dependency_is_not_a_parent_hierarchy(tmp_path, dependencies):
    _, _, path = _write_project(tmp_path)
    parent, child = _spec_rows()[2:]
    child.update(parent=None, affected_by=dependencies)
    assert run_all([parent, child], load_rules(path)[1:]) == []
    child["parent"] = parent["id"]
    assert {f.rule_id for f in run_all([parent, child], load_rules(path)[1:])} == {
        "authority-hierarchy-invariant",
        "status-drift",
    }


@pytest.mark.parametrize("broken", ["missing", "wrong_container", "duplicate", "order", "version", "inactive"])
def test_bad_native_snapshot_never_falls_back_or_writes_reports(tmp_path, monkeypatch, broken):
    root, config, _ = _write_project(tmp_path)
    rows = sorted(_spec_rows(), key=lambda row: row["id"])
    payload = {"records": rows, "consistency": "single_read_transaction"}
    if broken == "missing":
        payload.pop("consistency")
    elif broken == "wrong_container":
        payload["records"] = {}
    elif broken == "duplicate":
        rows.append(rows[-1])
    elif broken == "order":
        rows.reverse()
    elif broken == "version":
        rows[0]["version"] = True
    else:
        rows[0]["status"] = "retired"
    local = root / "groundtruth.db"
    local.write_bytes(b"never a fallback")
    before = _hash(local)
    calls = []

    def request(self, method, path, **kwargs):
        calls.append((method, path))
        return payload

    monkeypatch.setattr(AuthorityClient, "request", request)
    out = tmp_path / "bad"
    result = CliRunner().invoke(main, ["--config", str(config), "validate", "spec-coherence", "--output", str(out)])
    assert result.exit_code != 0 and "snapshot" in result.output
    assert calls == [("GET", "/v1/specifications/snapshot")]
    assert not out.exists() and _hash(local) == before


def test_cli_filter_markdown_empty_corpus_and_explicit_output(tmp_path, monkeypatch):
    _, config, _ = _write_project(tmp_path)
    calls = _mock_snapshot(monkeypatch, [])
    prefix = ["--config", str(config), "validate", "spec-coherence"]
    assert CliRunner().invoke(main, prefix).exit_code == 2
    assert (
        CliRunner().invoke(main, prefix + ["--db-path", "obsolete", "--output", str(tmp_path / "bad")]).exit_code == 2
    )
    assert not calls
    out = tmp_path / "markdown"
    result = CliRunner().invoke(
        main, prefix + ["--output", str(out), "--format", "md", "--rule-set", "status-drift", "--fail-on-findings"]
    )
    assert result.exit_code == 0, result.output
    assert not (out / "findings.json").exists()
    report = (out / "summary.md").read_text()
    assert "Rules loaded: 1" in report and "Specs scanned: 0" in report and "review candidates only" in report
    assert len(calls) == 1


def _seed_native(service, rows):
    with service.kernel.transaction() as tx:
        for source in rows:
            record = {column: None for column in TABLE_SPECS["specifications"].columns}
            record.update(source, changed_by="qualification", change_reason="Native coherence fixture")
            tx.mutate(
                table="specifications",
                identity={"id": record["id"]},
                expected_version=0,
                new_state=record,
                actor="qualification",
                reason="Native coherence fixture",
            )


@contextmanager
def _serve(service):
    listener = socket.socket()
    listener.bind(("127.0.0.1", 0))
    listener.listen()
    url = f"http://127.0.0.1:{listener.getsockname()[1]}"
    server = uvicorn.Server(uvicorn.Config(create_authority_app(service), log_level="error", lifespan="off"))
    thread = Thread(target=lambda: server.run(sockets=[listener]), daemon=True)
    thread.start()
    try:
        deadline = time.monotonic() + 10
        while not server.started:
            assert thread.is_alive() and time.monotonic() < deadline, "Disposable HTTP service did not start"
            time.sleep(0.02)
        yield url
    finally:
        server.should_exit = True
        thread.join(timeout=10)
        listener.close()
        assert not thread.is_alive(), "Disposable HTTP service did not stop"


@pytest.mark.integration
def test_real_cli_http_native_snapshot_is_read_only_and_unavailable_is_not_success(native, tmp_path):
    service, client, _, _ = native
    _seed_native(service, _spec_rows())
    retired = {**_spec_rows()[0], "id": "SPEC-RETIRED", "status": "retired"}
    _seed_native(service, [retired])
    before = client.get("/v1/specifications").content
    history = history_count(service)
    root, config, _ = _write_project(tmp_path)
    local = root / "groundtruth.db"
    local.write_bytes(b"not a valid database, never accessed")
    local_before = _hash(local)
    env = dict(
        os.environ,
        PYTHONPATH=str(Path(groundtruth_kb.__file__).resolve().parent.parent),
        PYTHONDONTWRITEBYTECODE="1",
        PYTHONIOENCODING="utf-8",
    )
    for key in list(env):
        if key.startswith(("PG", "GT_POSTGRES_", "GIT_")) or key in {
            "GT_AUTHORITY_URL",
            "GT_PROJECT_ROOT",
            "GTKB_PROJECT_ROOT",
            "GT_DB_PATH",
        }:
            env.pop(key, None)

    def cli(out):
        code = (
            "import pathlib,groundtruth_kb; assert pathlib.Path(groundtruth_kb.__file__).resolve()==pathlib.Path("
            + repr(str(Path(groundtruth_kb.__file__).resolve()))
            + "); from groundtruth_kb.cli import main; main()"
        )
        return subprocess.run(
            [
                sys.executable,
                "-P",
                "-c",
                code,
                "--config",
                str(config),
                "validate",
                "spec-coherence",
                "--output",
                str(out),
                "--fail-on-findings",
            ],
            cwd=root,
            env=env,
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=30,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        )

    with _serve(service) as url:
        config.write_text('[groundtruth]\nproject_root = "."\nauthority_url = ' + json.dumps(url) + "\n")
        report_dir = tmp_path / "actual"
        result = cli(report_dir)
        assert result.returncode == 5, result.stderr + result.stdout
        report = json.loads((report_dir / "findings.json").read_text())
        assert report["specs_scanned"] == 4 and report["authority_url"] == url
        assert report["spec_versions"] == {r["id"]: 1 for r in _spec_rows()}
        assert {f["rule_id"] for f in report["findings"]} == {
            "surface-overlap-opposite-polarity",
            "authority-hierarchy-invariant",
            "status-drift",
        }
        assert "review candidates only" in (report_dir / "summary.md").read_text()
        assert client.get("/v1/specifications/snapshot?limit=1").status_code == 422
    failed = tmp_path / "offline"
    unavailable = cli(failed)
    assert unavailable.returncode != 0 and "unavailable" in unavailable.stderr
    assert not failed.exists() and _hash(local) == local_before
    assert client.get("/v1/specifications").content == before and history_count(service) == history


@pytest.mark.integration
@pytest.mark.timeout(120)
def test_native_snapshot_keeps_one_transaction_across_pages_and_concurrent_amendment(native, monkeypatch):
    service, client, _, _ = native
    basis = {**_spec_rows()[0], "parent": None}
    rows = [{**basis, "id": f"SPEC-PAGE-{i:04d}"} for i in range(1000)] + [{**basis, "id": "ZZ-LAST"}]
    _seed_native(service, rows)
    history = history_count(service)
    entered, release = Event(), Event()
    original = PostgresTransaction.list

    def listing(self, table, **kwargs):
        result = original(self, table, **kwargs)
        if (
            table == "specifications"
            and kwargs.get("filters") == {"status": "active"}
            and kwargs.get("after") is None
            and not entered.is_set()
        ):
            assert len(result) == 1000
            entered.set()
            assert release.wait(20), "Concurrent amendment did not release the snapshot"
        return result

    monkeypatch.setattr(PostgresTransaction, "list", listing)
    with ThreadPoolExecutor(max_workers=1) as pool:
        pending = pool.submit(client.get, "/v1/specifications/snapshot")
        try:
            assert entered.wait(20)
            changed = put(client, "specifications", "ZZ-LAST", {"status": "retired"}, expected_version=1)
            assert changed.status_code == 200, changed.text
        finally:
            release.set()
        snapshot = pending.result(timeout=20)
    assert snapshot.status_code == 200, snapshot.text
    records = snapshot.json()["records"]
    assert len(records) == 1001 and records[-1]["id"] == "ZZ-LAST"
    assert records[-1]["status"] == "active" and records[-1]["version"] == 1
    fresh = client.get("/v1/specifications/snapshot").json()["records"]
    assert len(fresh) == 1000 and "ZZ-LAST" not in {r["id"] for r in fresh}
    assert history_count(service) == history + 1
