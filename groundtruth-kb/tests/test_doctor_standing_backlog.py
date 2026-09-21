"""D31/N35: current native backlog and content-free bridge observations.

The fixture refuses SQLite and preserves an inert leftover. GET response stubs
exercise malformed and unavailable boundaries; disposable served PostgreSQL
and the real release consumer are covered in test_doctor_native_readers.py.
"""

from __future__ import annotations

from pathlib import Path
from urllib.parse import unquote

import pytest

from groundtruth_kb.authority_client import AuthorityClient, AuthorityClientError
from groundtruth_kb.project.doctor import _check_standing_backlog_health, check_standing_backlog_health

AUTHORITY_URL = "http://127.0.0.1:12345"
SENTINEL = b"Never opened by the standing-backlog check"
TERMINAL_RESOLUTION_STATUSES = ("verified", "resolved", "retired", "wont_fix", "not_a_defect")


@pytest.fixture
def storeless_project(tmp_path, monkeypatch):
    monkeypatch.delenv("GT_AUTHORITY_URL", raising=False)
    sentinel = tmp_path / "groundtruth.db"
    sentinel.write_bytes(SENTINEL)

    def refuse(*args, **kwargs):
        pytest.fail("The standing-backlog check cannot open SQLite")

    monkeypatch.setattr("sqlite3.connect", refuse)
    yield tmp_path
    assert sentinel.read_bytes() == SENTINEL


@pytest.fixture
def configured_authority(storeless_project):
    (storeless_project / "groundtruth.toml").write_text(
        f'[groundtruth]\nauthority_url="{AUTHORITY_URL}"\n', encoding="utf-8"
    )
    return storeless_project


def project(project_id, authorization="authorized"):
    return {"id": project_id, "name": project_id, "kind": "project", "status": "active", "authorization": authorization}


def work_item(item_id, *, resolution_status="open", stage="implementing"):
    return {"id": item_id, "resolution_status": resolution_status, "stage": stage}


def serve(monkeypatch, *, projects=(), work_items=(), memberships=None, calls=None, bridge=None):
    memberships = memberships or {}

    def request(self, method, path, *, body=None, query=None):
        if calls is not None:
            calls.append((method, path, query))
        assert method == "GET" and body is None
        if path == "/v1/projects":
            return {"records": list(projects), "next_after": None}
        if path == "/v1/work-items":
            return {"records": list(work_items), "next_after": None}
        if path == "/v1/bridge/state-report":
            return {"attempts": []} if bridge is None else bridge
        if path.startswith("/v1/work-items/"):
            item_id = unquote(path.removeprefix("/v1/work-items/"))
            assert item_id in memberships, f"Unexpected membership request: {item_id}"
            project_id = memberships[item_id]
            return {"membership": None if project_id is None else {"project_id": project_id}}
        raise AuthorityClientError("invalid_path", f"Unexpected request {path}")

    monkeypatch.setattr(AuthorityClient, "request", request)


@pytest.mark.parametrize(
    ("projects", "membership_project"),
    [
        ([project("PROJECT-X")], "PROJECT-GONE"),
        ([project("PROJECT-X", "not authorized")], "PROJECT-X"),
        ([project("PROJECT-X")], None),
    ],
    ids=["project-absent", "project-not-authorized", "no-active-membership"],
)
def test_doctor_finds_orphaned_wis(configured_authority, monkeypatch, projects, membership_project):
    serve(
        monkeypatch,
        projects=projects,
        work_items=[work_item("WI-ORPHAN")],
        memberships={"WI-ORPHAN": membership_project},
    )
    payload = check_standing_backlog_health(configured_authority)
    assert payload["status"] == "warning"
    assert payload["summary"]["orphaned_wi_count"] == 1
    finding = payload["findings"][0]
    assert finding["kind"] == "orphaned-WI" and finding["severity"] == "WARN"
    assert finding["work_item_id"] == "WI-ORPHAN" and finding["project_id"] == membership_project


def test_clean_native_state_without_bridge_files(configured_authority, monkeypatch):
    calls = []
    serve(
        monkeypatch,
        projects=[project("PROJECT-X")],
        work_items=[work_item("WI-COVERED")],
        memberships={"WI-COVERED": "PROJECT-X"},
        calls=calls,
    )
    payload = check_standing_backlog_health(configured_authority)
    assert payload["status"] == "pass" and payload["findings"] == []
    assert not (configured_authority / "bridge").exists()
    assert [(method, path) for method, path, _ in calls] == [
        ("GET", "/v1/projects"),
        ("GET", "/v1/work-items"),
        ("GET", "/v1/work-items/WI-COVERED"),
        ("GET", "/v1/bridge/state-report"),
    ]
    assert all(query == {"limit": 1000, "after": None} for _, _, query in calls[:2])
    check = _check_standing_backlog_health(configured_authority)
    assert check.required and check.found and check.status == "pass"


def test_stale_unreadable_local_remnants_cannot_change_native_result(configured_authority, monkeypatch):
    serve(monkeypatch)
    before = check_standing_backlog_health(configured_authority)
    bridge = configured_authority / "bridge"
    bridge.mkdir()
    (bridge / "INDEX.md").write_text("NO-GO contradiction", encoding="utf-8")
    (bridge / "obsolete-001.md").write_text("NO-GO\nDate: 1999-01-01\n", encoding="utf-8")
    read_text = Path.read_text

    def refuse_bridge(path, *args, **kwargs):
        if path.parent == bridge:
            pytest.fail("Retired bridge files must not be read")
        return read_text(path, *args, **kwargs)

    monkeypatch.setattr(Path, "read_text", refuse_bridge)
    assert check_standing_backlog_health(configured_authority) == before


@pytest.mark.parametrize(
    ("disposition", "status", "time"),
    [
        ("active", "NO-GO", "1999-01-01T00:00:00+00:00"),
        ("active", "NO-GO", None),
        ("active", None, None),
        ("committed", "VERIFIED", None),
        ("abandoned", "NO-GO", None),
    ],
)
def test_native_attempts_do_not_infer_file_age_or_completion(
    configured_authority, monkeypatch, disposition, status, time
):
    serve(
        monkeypatch,
        bridge={
            "attempts": [
                {"id": "attempt-one", "disposition": disposition, "head_status": status, "head_created_at": time}
            ]
        },
    )
    payload = check_standing_backlog_health(configured_authority)
    assert payload["status"] == "pass" and not payload["findings"]
    assert "threshold_days" not in payload
    assert "stale_no_go_count" not in payload["summary"]
    assert "missing_verdict_date_count" not in payload["summary"]


@pytest.mark.parametrize(
    "bridge",
    [
        {},
        {"attempts": None},
        {"attempts": [{}]},
        {"attempts": [{"id": "bad", "head_status": "NO-ACTION", "disposition": "active"}]},
    ],
)
def test_malformed_native_bridge_report_fails(configured_authority, monkeypatch, bridge):
    serve(monkeypatch, bridge=bridge)
    payload = check_standing_backlog_health(configured_authority)
    assert payload["status"] == "fail"
    assert payload["summary"]["missing_evidence_count"] == 1
    assert "state-report attempts are malformed" in payload["findings"][0]["message"]


def test_terminal_and_unstarted_work_do_not_fetch_membership(configured_authority, monkeypatch):
    calls = []
    serve(
        monkeypatch,
        work_items=[
            *(work_item(f"WI-{status}", resolution_status=status) for status in TERMINAL_RESOLUTION_STATUSES),
            work_item("WI-BACKLOGGED", stage="backlogged"),
            work_item("WI-DEFERRED", resolution_status="deferred", stage="backlogged"),
        ],
        calls=calls,
    )
    payload = check_standing_backlog_health(configured_authority)
    assert payload["status"] == "pass"
    assert payload["summary"]["non_implementation_open_count"] == 2
    assert not any(path.startswith("/v1/work-items/") for _, path, _ in calls)


def test_json_output_schema(configured_authority, monkeypatch):
    serve(monkeypatch)
    payload = check_standing_backlog_health(configured_authority)
    assert payload["schema_version"] == 3 and payload["check"] == "standing_backlog_health"
    assert set(payload["summary"]) == {
        "finding_count",
        "fail_count",
        "warn_count",
        "orphaned_wi_count",
        "non_implementation_open_count",
        "missing_evidence_count",
        "authority_not_configured_count",
    }


@pytest.mark.parametrize("config", ["[groundtruth]\ndb_path='groundtruth.db'\n", None])
def test_no_authority_configured_is_warning_without_bridge(storeless_project, monkeypatch, config):
    if config is not None:
        (storeless_project / "groundtruth.toml").write_text(config, encoding="utf-8")

    def refuse(*args, **kwargs):
        pytest.fail("No authority may be contacted when none is configured")

    monkeypatch.setattr(AuthorityClient, "request", refuse)
    payload = check_standing_backlog_health(storeless_project)
    assert payload["status"] == "warning" and payload["summary"]["fail_count"] == 0
    assert payload["summary"]["authority_not_configured_count"] == 1
    assert not (storeless_project / "bridge").exists()
    check = _check_standing_backlog_health(storeless_project)
    assert not check.found and check.status == "warning"
    assert "No authority_url is configured" in check.message


@pytest.mark.parametrize("failing_path", ["/v1/projects", "/v1/work-items/WI-ACTIVE", "/v1/bridge/state-report"])
def test_unreachable_authority_is_missing_evidence_failure(configured_authority, monkeypatch, failing_path):
    serve(
        monkeypatch,
        projects=[project("PROJECT-X")],
        work_items=[work_item("WI-ACTIVE")],
        memberships={"WI-ACTIVE": "PROJECT-X"},
    )
    request = AuthorityClient.request

    def unavailable(self, method, path, **kwargs):
        if path == failing_path:
            raise AuthorityClientError("authority_unavailable", "Fixture service unavailable")
        return request(self, method, path, **kwargs)

    monkeypatch.setattr(AuthorityClient, "request", unavailable)
    payload = check_standing_backlog_health(configured_authority)
    assert payload["status"] == "fail" and payload["summary"]["missing_evidence_count"] == 1
    assert payload["findings"][0]["path"] == AUTHORITY_URL
    assert "authority_unavailable" in _check_standing_backlog_health(configured_authority).message


@pytest.mark.parametrize(
    "detail",
    [{}, {"membership": {}}, {"membership": []}, {"membership": {"project_id": ""}}, {"membership": {"project_id": 3}}],
)
def test_malformed_successful_membership_response_fails(configured_authority, monkeypatch, detail):
    serve(monkeypatch, projects=[project("PROJECT-X")], work_items=[work_item("WI-ACTIVE")])
    request = AuthorityClient.request

    def malformed(self, method, path, **kwargs):
        if path == "/v1/work-items/WI-ACTIVE":
            return detail
        return request(self, method, path, **kwargs)

    monkeypatch.setattr(AuthorityClient, "request", malformed)
    payload = check_standing_backlog_health(configured_authority)
    assert payload["status"] == "fail" and payload["summary"]["missing_evidence_count"] == 1
    assert payload["summary"]["orphaned_wi_count"] == 0
