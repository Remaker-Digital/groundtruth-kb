"""Native citation resolution without a local store or bridge-file dependency."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest
from groundtruth_kb.authority_client import AuthorityClient

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = REPO_ROOT / "scripts" / "orphan_citation_audit.py"


def _load_audit_module():
    spec = importlib.util.spec_from_file_location("orphan_citation_audit", SCRIPT_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def source(tmp_path, monkeypatch):
    monkeypatch.setenv("GT_AUTHORITY_URL", "http://127.0.0.1:12345")
    src = tmp_path / "src"
    src.mkdir()
    sentinel = tmp_path / "groundtruth.db"
    sentinel.write_bytes(b"inert leftover")

    def refuse(*args, **kwargs):
        pytest.fail("Citation audit must not open SQLite")

    monkeypatch.setattr("sqlite3.connect", refuse)
    yield tmp_path, src
    assert sentinel.read_bytes() == b"inert leftover"


def _serve(monkeypatch, specs=(), *, malformed=False):
    def request(self, method, path, *, body=None, query=None):
        assert method == "GET" and body is None
        assert path in {"/v1/specifications", "/v1/work-items", "/v1/deliberations"}
        if malformed:
            return {"records": [{}], "next_after": None}
        ids = specs if path == "/v1/specifications" else ()
        return {"records": [{"id": value} for value in ids], "next_after": None}

    monkeypatch.setattr(AuthorityClient, "request", request)


def test_audit_detects_orphan_citation(source, monkeypatch):
    root, src = source
    _serve(monkeypatch)
    (src / "sample.py").write_text("# See SPEC-MISSING-001\n", encoding="utf-8")
    result = _load_audit_module().audit_root(root, [src])
    assert result.scanned_files == 1
    assert [(row.anchor, row.kind, row.line) for row in result.orphans] == [("SPEC-MISSING-001", "spec", 1)]


def test_audit_resolves_known_good_spec(source, monkeypatch):
    root, src = source
    _serve(monkeypatch, ["SPEC-OK-001"])
    (src / "sample.md").write_text("See SPEC-OK-001 and bridge/absent-thread-001.md.\n", encoding="utf-8")
    result = _load_audit_module().audit_root(root, [src])
    assert result.orphans == []
    assert result.resolved == {"spec": 1, "deliberation": 0, "work_item": 0}
    assert not (root / "bridge").exists()


def test_audit_json_output_shape_is_stable(source, monkeypatch):
    root, src = source
    _serve(monkeypatch)
    (src / "sample.py").write_text("# SPEC-MISSING-001\n", encoding="utf-8")
    payload = _load_audit_module().audit_root(root, [src]).to_jsonable()
    assert set(payload) == {"root", "authority_url", "scanned_files", "resolved", "orphans"}
    assert set(payload["orphans"][0]) == {"anchor", "kind", "path", "line"}


def test_cli_exit_code_reflects_orphan_presence(source, monkeypatch, capsys):
    root, src = source
    _serve(monkeypatch, ["SPEC-OK-001"])
    sample = src / "sample.py"
    audit = _load_audit_module()
    sample.write_text("# SPEC-MISSING-001\n", encoding="utf-8")
    assert audit.main(["--root", str(root), "--scan-dir", "src"]) == 1
    assert json.loads(capsys.readouterr().out)["orphans"][0]["anchor"] == "SPEC-MISSING-001"
    sample.write_text("# SPEC-OK-001\n", encoding="utf-8")
    assert audit.main(["--root", str(root), "--scan-dir", "src"]) == 0
    assert json.loads(capsys.readouterr().out)["orphans"] == []


def test_doctor_reads_native_ids_and_warns_for_orphans(source, monkeypatch):
    from groundtruth_kb.project.doctor import _check_orphan_citations

    root, src = source
    _serve(monkeypatch)
    _load_audit_module()
    (src / "sample.py").write_text("# SPEC-MISSING-001\n", encoding="utf-8")
    result = _check_orphan_citations(root)
    assert result.status == "warning"
    assert result.found is True
    assert "SPEC-MISSING-001" in result.message


def test_unreadable_native_ids_fail_instead_of_reporting_false_orphans(source, monkeypatch, capsys):
    from groundtruth_kb.project.doctor import _check_orphan_citations

    root, src = source
    _serve(monkeypatch, malformed=True)
    audit = _load_audit_module()
    (src / "sample.py").write_text("# SPEC-OK-001\n", encoding="utf-8")
    assert audit.main(["--root", str(root), "--scan-dir", "src"]) == 2
    assert "malformed" in capsys.readouterr().err
    result = _check_orphan_citations(root)
    assert result.status == "fail"
    assert result.found is False


def test_audit_excludes_scratch_credentials_and_bridge_content(source, monkeypatch):
    root, src = source
    _serve(monkeypatch)
    for name in ("scratchpad", "credentials", "bridge"):
        folder = src / name
        folder.mkdir()
        (folder / "ignored.md").write_text("SPEC-MISSING-001", encoding="utf-8")
    result = _load_audit_module().audit_root(root, [src])
    assert result.scanned_files == 0
    assert result.orphans == []
