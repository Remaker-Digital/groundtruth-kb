"""Native metadata audit observations, pagination, read-only access and CLI."""

from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
from contextlib import contextmanager
from copy import deepcopy
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread
from urllib.parse import parse_qs, urlparse

import groundtruth_kb
import pytest
from groundtruth_kb.authority_client import AuthorityClient

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "groundtruth-kb/scripts/audit_adr_dcl_metadata.py"
FROZEN = "2026-05-01T00:00:00+00:00"


def _load_module():
    spec = importlib.util.spec_from_file_location("audit_adr_dcl_metadata", SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def records():
    def row(identifier, kind, tags=None, sources=None, assertions=None, status="active"):
        return {
            "id": identifier,
            "version": 1,
            "type": kind,
            "status": status,
            "tags": tags,
            "source_paths": sources,
            "assertions": assertions,
        }

    return [
        row(
            "ADR-001",
            "architecture_decision",
            ["shared", "design-constraint", "topic-foo"],
            ["src/a.py"],
            [{"type": "file_exists", "file": "src/a.py"}],
        ),
        row("ADR-002", "architecture_decision", ["shared", "topic-bar"], [], []),
        row("ADR-003", "architecture_decision", [], None, [], status="superseded"),
        row(
            "DCL-001",
            "design_constraint",
            ["mechanical-enforcement", "topic-foo"],
            ["src/b.py"],
            [{"type": "file_exists", "file": "src/b.py"}],
        ),
        row(
            "DCL-002",
            "design_constraint",
            ["shared", "design-constraint"],
            [],
            [{"type": "file_exists", "file": "src/c.py"}],
        ),
        row("DCL-003", "design_constraint"),
    ]


@contextmanager
def authority(pages):
    requests = []

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            parsed = urlparse(self.path)
            query = parse_qs(parsed.query)
            requests.append((self.command, parsed.path, query))
            cursor = query.get("after", [None])[0]
            value = pages[cursor]
            status = 503 if isinstance(value, Exception) else 200
            payload = (
                {"error": {"code": "fixture_unavailable", "message": "Second page unavailable"}}
                if status != 200
                else value
            )
            body = json.dumps(payload).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def do_PUT(self):
            requests.append((self.command, self.path, {}))
            self.send_error(405)

        do_POST = do_PUT
        do_DELETE = do_PUT

        def log_message(self, *args):
            pass

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{server.server_port}", requests
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)
        assert not thread.is_alive()


def test_idempotency_byte_identical_with_frozen_timestamp(records):
    module = _load_module()
    a = module.build_report(records, "http://127.0.0.1:8765", FROZEN)
    b = module.build_report(records, "http://127.0.0.1:8765", FROZEN)
    assert module.render_json(a) == module.render_json(b)
    assert module.render_markdown(a) == module.render_markdown(b)


def test_population_computation(records):
    report = _load_module().build_report(records, "http://127.0.0.1:8765", FROZEN)
    assert report["totals"] == {
        "architecture_decision": {"total": 3, "with_tags": 2, "with_source_paths": 1, "with_assertions": 1},
        "design_constraint": {"total": 3, "with_tags": 2, "with_source_paths": 1, "with_assertions": 2},
    }
    assert report["status_counts"] == {"active": 5, "superseded": 1}


def test_missing_source_paths_list_correct(records):
    report = _load_module().build_report(records, "http://127.0.0.1:8765", FROZEN)
    assert [r["id"] for r in report["missing_source_paths"]] == ["ADR-002", "ADR-003", "DCL-002", "DCL-003"]
    assert report["records_needing_backfill_count"] == 4


def test_histogram_counts_records_without_inferring_tag_categories(records):
    records[0]["tags"].extend(["shared", "", None])
    report = _load_module().build_report(records, "http://127.0.0.1:8765", FROZEN)
    assert report["tags_histogram"] == [
        {"tag": "shared", "count": 3},
        {"tag": "design-constraint", "count": 2},
        {"tag": "topic-foo", "count": 2},
        {"tag": "mechanical-enforcement", "count": 1},
        {"tag": "topic-bar", "count": 1},
    ]
    assert "concern_tags_normalization_recommendation" not in report


def test_json_snapshot_deterministic_and_valid(records):
    module = _load_module()
    report = json.loads(module.render_json(module.build_report(records, "http://127.0.0.1:8765", FROZEN)))
    assert report["schema_version"] == 2 and report["generated_at"] == FROZEN
    assert report["authority_url"] == "http://127.0.0.1:8765"
    assert "do not establish" in report["evidence_limit"]
    assert "db_path" not in report


def test_markdown_snapshot_contains_required_sections(records):
    module = _load_module()
    text = module.render_markdown(module.build_report(records, "http://127.0.0.1:8765", FROZEN))
    for expected in (
        "# ADR/DCL Metadata Audit Report",
        "## Totals",
        "## Records needing backfill",
        "## Tags histogram",
        "Generated: " + FROZEN,
        "superseded: 1",
        "do not establish",
    ):
        assert expected in text
    assert "**Decision:**" not in text


def test_native_pagination_uses_only_get_and_selects_architecture_records(records):
    pages = {
        None: {"records": records[:3], "next_after": "ADR-003"},
        "ADR-003": {"records": [*records[3:], {"id": "SPEC-001", "type": "requirement"}], "next_after": None},
    }
    before = deepcopy(pages)
    with authority(pages) as (url, requests):
        got = _load_module()._query_records(AuthorityClient(url))
    assert got == records
    assert pages == before
    assert requests == [
        ("GET", "/v1/specifications", {"limit": ["1000"]}),
        ("GET", "/v1/specifications", {"limit": ["1000"], "after": ["ADR-003"]}),
    ]


@pytest.mark.parametrize("problem", ["duplicate", "repeated_cursor", "missing_records"])
def test_invalid_page_refused_without_partial_report(records, problem):
    second = (
        {"records": records[:1], "next_after": None}
        if problem == "duplicate"
        else {"records": records[1:2], "next_after": "page-two"}
        if problem == "repeated_cursor"
        else {"next_after": None}
    )
    with (
        authority({None: {"records": records[:1], "next_after": "page-two"}, "page-two": second}) as (url, requests),
        pytest.raises(ValueError),
    ):
        _load_module()._query_records(AuthorityClient(url))
    assert len(requests) == 2


def _config(tmp_path, url=None):
    config = tmp_path / "groundtruth.toml"
    config.write_text(
        '[groundtruth]\nproject_root="."\ndb_path="must-not-open.db"\n' + (f'authority_url="{url}"\n' if url else ""),
        encoding="utf-8",
    )
    return config


def test_output_flag_writes_file_through_native_cli_without_database_access(tmp_path, records):
    sentinel = tmp_path / "must-not-open.db"
    sentinel.write_bytes(b"Opening this as SQLite would be a test failure")
    before = (sentinel.read_bytes(), sentinel.stat().st_mtime_ns)
    output = tmp_path / "report.json"
    with authority({None: {"records": records, "next_after": None}}) as (url, requests):
        config = _config(tmp_path, url)
        env = dict(
            os.environ,
            PYTHONIOENCODING="utf-8",
            PYTHONDONTWRITEBYTECODE="1",
            PYTHONPATH=str(Path(groundtruth_kb.__file__).resolve().parent.parent),
        )
        for key in list(env):
            if key == "GT_AUTHORITY_URL" or key.startswith(("PG", "GT_POSTGRES_")):
                env.pop(key, None)
        result = subprocess.run(
            [
                sys.executable,
                "-P",
                str(SCRIPT),
                "--config",
                str(config),
                "--output",
                str(output),
                "--frozen-timestamp",
                FROZEN,
            ],
            cwd=tmp_path,
            env=env,
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=20,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        )
    assert result.returncode == 0, result.stderr
    assert len(requests) == 1 and requests[0][0] == "GET"
    assert json.loads(output.read_text(encoding="utf-8"))["totals"]["architecture_decision"]["total"] == 3
    assert (sentinel.read_bytes(), sentinel.stat().st_mtime_ns) == before


def test_missing_native_configuration_refuses_without_creating_database(tmp_path, monkeypatch, capsys):
    monkeypatch.delenv("GT_AUTHORITY_URL", raising=False)
    assert _load_module().main(["--config", str(_config(tmp_path))]) == 2
    assert "No authority_url is configured" in capsys.readouterr().err
    assert not (tmp_path / "must-not-open.db").exists()


def test_second_page_outage_preserves_existing_report(tmp_path, records, monkeypatch, capsys):
    monkeypatch.delenv("GT_AUTHORITY_URL", raising=False)
    output = tmp_path / "report.json"
    output.write_bytes(b"previous completed observation")
    with authority({None: {"records": records[:1], "next_after": "next"}, "next": RuntimeError("outage")}) as (
        url,
        requests,
    ):
        assert _load_module().main(["--config", str(_config(tmp_path, url)), "--output", str(output)]) == 2
    assert "Second page unavailable" in capsys.readouterr().err
    assert output.read_bytes() == b"previous completed observation"
    assert len(requests) == 2
