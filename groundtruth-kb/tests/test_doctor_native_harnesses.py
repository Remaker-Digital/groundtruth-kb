"""Installation diagnostics use native metadata without assigning harness roles."""

from __future__ import annotations

import sys

import pytest

from groundtruth_kb.authority_client import AuthorityClient, AuthorityClientError
from groundtruth_kb.project.doctor import _check_harness_launchability


@pytest.fixture
def installation(tmp_path, monkeypatch):
    monkeypatch.delenv("GT_AUTHORITY_URL", raising=False)
    (tmp_path / "groundtruth.toml").write_text(
        '[groundtruth]\nauthority_url="http://127.0.0.1:12345"\n', encoding="utf-8"
    )
    sentinel = tmp_path / "groundtruth.db"
    sentinel.write_bytes(b"Never opened by an installation diagnostic")

    def refuse(*args, **kwargs):
        pytest.fail("Installation diagnostics cannot use SQLite, legacy readers or launch an agent")

    monkeypatch.setattr("sqlite3.connect", refuse)
    monkeypatch.setattr("groundtruth_kb.harness_projection.read_roles", refuse)
    monkeypatch.setattr("groundtruth_kb.harness_projection.read_identity", refuse)
    monkeypatch.setattr("subprocess.run", refuse)
    yield tmp_path
    assert sentinel.read_bytes() == b"Never opened by an installation diagnostic"
    assert not (tmp_path / "harness-state").exists()


def record(record_id, argv=None, **extra):
    return {
        "id": record_id,
        "harness_name": record_id,
        "status": "active",
        "invocation_surfaces": {} if argv is None else {"headless": {"argv": argv}},
        **extra,
    }


def test_launchability_reads_every_page_without_role_or_dispatch_aliases(installation, monkeypatch):
    calls = []
    pages = iter(
        [
            {"records": [record("A", [sys.executable])], "next_after": "A"},
            {"records": [record("B", [sys.executable], role=["lo"], can_receive_dispatch=False)], "next_after": None},
        ]
    )

    def request(self, method, path, **kwargs):
        calls.append((method, path, kwargs))
        return next(pages)

    monkeypatch.setattr(AuthorityClient, "request", request)
    result = _check_harness_launchability(installation)
    assert result.status == "pass" and "2 active installation" in result.message
    assert "actual launch is unverified" in result.message
    assert [(method, path) for method, path, _ in calls] == [("GET", "/v1/harnesses")] * 2
    assert [kwargs["query"]["after"] for _, _, kwargs in calls] == [None, "A"]


@pytest.mark.parametrize("failure", ["unavailable", "malformed", "stuck_pagination"])
def test_unavailable_or_incomplete_metadata_never_becomes_pass(installation, monkeypatch, failure):
    def request(*args, **kwargs):
        if failure == "unavailable":
            raise AuthorityClientError("authority_unavailable", "Service unavailable")
        if failure == "malformed":
            return {"records": [None], "next_after": None}
        return {"records": [record("A", [sys.executable])], "next_after": "A"}

    monkeypatch.setattr(AuthorityClient, "request", request)
    result = _check_harness_launchability(installation)
    assert result.status == "warning" and not result.found
    assert "unverified" in result.message


@pytest.mark.parametrize("argv", [[], [None], ["{{PROMPT}}"], ["missing-gtkb-qualification-command"]])
def test_invalid_headless_installation_is_a_failure(installation, monkeypatch, argv):
    monkeypatch.setattr(
        AuthorityClient,
        "request",
        lambda *a, **kw: {
            "records": [record("A", argv)],
            "next_after": None,
        },
    )
    result = _check_harness_launchability(installation)
    assert result.status == "fail" and "unlaunchable" in result.message


def test_desktop_only_metadata_does_not_claim_dispatch_readiness(installation, monkeypatch):
    monkeypatch.setattr(
        AuthorityClient,
        "request",
        lambda *a, **kw: {
            "records": [record("A")],
            "next_after": None,
        },
    )
    result = _check_harness_launchability(installation)
    assert result.status == "info" and "dispatcher readiness is not asserted" in result.message


def test_relative_executable_cannot_fall_back_to_caller_directory(installation, monkeypatch, tmp_path):
    from groundtruth_kb.project.doctor import _normalize_harness_argv_head

    caller = tmp_path / "caller"
    caller.mkdir()
    monkeypatch.chdir(caller)
    requested = []

    def which(command):
        requested.append(command)
        return sys.executable if command == "foreign/python.exe" else None

    monkeypatch.setattr("shutil.which", which)
    result = _normalize_harness_argv_head("foreign/python.exe", installation)
    assert result == str(installation / "foreign/python.exe")
    assert requested == [str(installation / "foreign/python.exe")]
