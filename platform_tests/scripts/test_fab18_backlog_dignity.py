"""FAB-18 regression coverage for backlog dignity metric calibration over native pages.

Owner ruling D31 (2026-09-19): ``check_standing_backlog_health`` reads ``GET /v1/projects`` and
``GET /v1/work-items``, native ``GET /v1/bridge/state-report`` facts and one
``GET /v1/work-items/<id>`` detail per implementation-active item;
open work that is not implementation-active is only counted (``non_implementation_open_count``,
membership not read). The pages are served from dicts by monkeypatching ``AuthorityClient.request``;
``approval_state`` is not a native field - the fake records may carry it, the check ignores it - and
a sentinel ``groundtruth.db`` keeps its bytes while ``sqlite3.connect`` is refused.
No file-bridge directory is created or required.
"""

from __future__ import annotations

from pathlib import Path
from urllib.parse import unquote

import pytest
from groundtruth_kb.authority_client import AuthorityClient, AuthorityClientError
from groundtruth_kb.project.doctor import check_standing_backlog_health

AUTHORITY_URL = "http://127.0.0.1:12345"
SENTINEL = b"Never opened by the standing-backlog check"


@pytest.fixture
def configured_authority(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    """A project configured against a fake authority whose sentinel ``groundtruth.db`` is never opened."""
    monkeypatch.delenv("GT_AUTHORITY_URL", raising=False)
    (tmp_path / "groundtruth.toml").write_text(f'[groundtruth]\nauthority_url="{AUTHORITY_URL}"\n', encoding="utf-8")
    sentinel = tmp_path / "groundtruth.db"
    sentinel.write_bytes(SENTINEL)

    def refuse(*args, **kwargs):
        pytest.fail("The standing-backlog check cannot open SQLite")

    monkeypatch.setattr("sqlite3.connect", refuse)
    yield tmp_path
    assert sentinel.read_bytes() == SENTINEL
    assert not (tmp_path / "bridge").exists()


def _open_work_item(
    item_id: str,
    *,
    approval_state: str = "unapproved",
    resolution_status: str = "open",
    stage: str = "backlogged",
) -> dict:
    return {
        "id": item_id,
        "title": f"Work item {item_id}",
        "origin": "hygiene",
        "component": "backlog",
        "resolution_status": resolution_status,
        "stage": stage,
        "approval_state": approval_state,
    }


def serve(
    monkeypatch: pytest.MonkeyPatch,
    *,
    projects: list[dict] | None = None,
    work_items: list[dict] | None = None,
    memberships: dict[str, str | None] | None = None,
    calls: list | None = None,
) -> None:
    """Serve native collection pages, bridge facts and listed work-item details; refuse other reads."""
    projects = list(projects or [])
    work_items = list(work_items or [])
    memberships = dict(memberships or {})
    rows = {row["id"]: row for row in work_items}

    def request(self, method, path, *, body=None, query=None):
        if calls is not None:
            calls.append((method, path, query))
        assert method == "GET" and body is None, "a doctor check only reads"
        if path == "/v1/bridge/state-report":
            return {"attempts": []}
        if path == "/v1/projects":
            return {"records": [dict(row) for row in projects], "next_after": None}
        if path == "/v1/work-items":
            return {"records": [dict(row) for row in work_items], "next_after": None}
        if path.startswith("/v1/work-items/"):
            item_id = unquote(path.removeprefix("/v1/work-items/"))
            if item_id not in rows or item_id not in memberships:
                raise AuthorityClientError("not_found", f"Unexpected detail read {path}")
            project_id = memberships[item_id]
            member = (
                None if project_id is None else {"id": f"PWM-{item_id}", "project_id": project_id, "status": "active"}
            )
            return {"work_item": rows[item_id], "membership": member, "memberships": [] if member is None else [member]}
        raise AuthorityClientError("invalid_path", f"Unexpected request {method} {path}")

    monkeypatch.setattr(AuthorityClient, "request", request)


def test_unapproved_future_wi_without_pauth_is_not_doctor_warn(
    configured_authority: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    calls: list = []
    serve(monkeypatch, work_items=[_open_work_item("WI-FUTURE", approval_state="unapproved")], calls=calls)

    payload = check_standing_backlog_health(configured_authority)

    assert any(method == "GET" and path == "/v1/bridge/state-report" for method, path, _ in calls)

    assert payload["status"] == "pass"
    assert payload["summary"]["orphaned_wi_count"] == 0
    assert payload["summary"]["non_implementation_open_count"] == 1
    assert payload["findings"] == []
    assert not any(path.startswith("/v1/work-items/") for _, path, _ in calls)


def test_legacy_implementation_authorized_wi_without_pauth_is_not_doctor_warn(
    configured_authority: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    calls: list = []
    serve(
        monkeypatch,
        work_items=[_open_work_item("WI-ACTIVE", approval_state="implementation_authorized")],
        calls=calls,
    )

    payload = check_standing_backlog_health(configured_authority)

    assert any(method == "GET" and path == "/v1/bridge/state-report" for method, path, _ in calls)

    assert payload["status"] == "pass"
    assert payload["summary"]["orphaned_wi_count"] == 0
    assert payload["summary"]["non_implementation_open_count"] == 1
    assert payload["findings"] == []
    assert not any(path.startswith("/v1/work-items/") for _, path, _ in calls)


def test_implementing_stage_wi_without_pauth_still_warns(
    configured_authority: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    calls: list = []
    serve(
        monkeypatch,
        projects=[
            {
                "id": "PROJECT-X",
                "name": "Project X",
                "kind": "project",
                "status": "active",
                "authorization": "not authorized",
            }
        ],
        work_items=[_open_work_item("WI-ACTIVE", stage="implementing")],
        memberships={"WI-ACTIVE": "PROJECT-X"},
        calls=calls,
    )

    payload = check_standing_backlog_health(configured_authority)

    assert any(method == "GET" and path == "/v1/bridge/state-report" for method, path, _ in calls)

    assert payload["status"] == "warning"
    assert payload["summary"]["orphaned_wi_count"] == 1
    assert payload["summary"]["non_implementation_open_count"] == 0
    assert payload["findings"][0]["work_item_id"] == "WI-ACTIVE"
    assert payload["findings"][0]["project_id"] == "PROJECT-X"
    assert "approval_state" not in payload["findings"][0]
