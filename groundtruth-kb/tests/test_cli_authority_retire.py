"""Request shapes of the D32 retirement verbs against a captured authority client (no service, no database).

``gt backlog retire`` and ``gt projects retire`` post exactly {expected_version, actor, reason} to
POST /v1/work-items/<id>/retire and POST /v1/projects/<id>/retire; every option is required (Click exit 2
without a request), --json echoes the response and text output prints the row with its retired status.
"""

from __future__ import annotations

import json
import os

import pytest
from click.testing import CliRunner

from groundtruth_kb.authority_client import AuthorityClient, AuthorityClientError
from groundtruth_kb.cli import main
from groundtruth_kb.postgres_kernel import canonical_json_bytes

MEMBERSHIP = {"id": "PWM-1", "version": 1, "project_id": "PROJECT-1", "work_item_id": "WI-1", "status": "active"}
WORK_ITEM = {
    "work_item": {
        "id": "WI-1",
        "version": 2,
        "title": "Spine",
        "resolution_status": "retired",
        "stage": "backlogged",
        "changed_by": "a",
        "change_reason": "r",
    },
    "membership": MEMBERSHIP,
    "memberships": [MEMBERSHIP],
}
PROJECT = {
    "id": "P",
    "version": 3,
    "name": "Name",
    "kind": "project",
    "status": "retired",
    "authorization": "authorized",
    "changed_by": "a",
    "change_reason": "r",
}
# group -> (record id, expected version, path, response, text label, text status line)
VERBS = {
    "backlog": ("WI-1", 1, "/v1/work-items/WI-1/retire", WORK_ITEM, "WI-1 v2: Spine", 'resolution_status: "retired"'),
    "projects": ("P", 2, "/v1/projects/P/retire", PROJECT, "P v3: Name", 'status: "retired"'),
}


@pytest.fixture
def captured(tmp_path, monkeypatch):
    monkeypatch.delenv("GT_AUTHORITY_URL", raising=False)
    config = tmp_path / "groundtruth.toml"
    config.write_text('[groundtruth]\nauthority_url="http://127.0.0.1:12345"\nproject_root="."\n', encoding="utf-8")
    sentinel = tmp_path / "groundtruth.db"
    sentinel.write_bytes(b"SQLite is not a fallback")
    calls = []

    def request(self, method, path, **kwargs):
        calls.append((method, path, kwargs))
        return WORK_ITEM if path.startswith("/v1/work-items/") else PROJECT

    monkeypatch.setattr(AuthorityClient, "request", request)
    yield config, calls
    assert sentinel.read_bytes() == b"SQLite is not a fallback"


def invoke(config, *args):
    return CliRunner().invoke(main, ["--config", str(config), *args])


def retire(config, group, *extra, record_id="WI-1", version="1"):
    options = ("--id", record_id, "--reason", "r", "--expected-version", version, "--actor", "a")
    return invoke(config, group, "retire", *options, *extra)


@pytest.mark.parametrize("group", ["backlog", "projects"])
def test_retire_posts_the_version_reason_and_actor_and_echoes_the_row(captured, group):
    config, calls = captured
    record_id, version, path, row, label, status_line = VERBS[group]
    result = retire(config, group, "--json", record_id=record_id, version=str(version))
    assert result.exit_code == 0, result.output
    expected = json.dumps(row, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n"
    assert canonical_json_bytes(row) == expected.encode("utf-8")
    # Click writes text: Windows translates the serializer's LF to one native CRLF.
    assert result.stdout_bytes == expected.replace("\n", os.linesep).encode("utf-8")
    assert result.stdout.count("\n") == 1 and result.stderr_bytes == b""
    assert calls == [("POST", path, {"body": {"expected_version": version, "actor": "a", "reason": "r"}})]
    text = retire(config, group, record_id=record_id, version=str(version))
    assert text.exit_code == 0, text.output
    assert text.stderr == ""
    assert label in text.output and status_line in text.output
    assert len(calls) == 2 and calls[1] == calls[0]


@pytest.mark.parametrize("group", ["backlog", "projects"])
@pytest.mark.parametrize(
    "arguments",
    [
        ("--reason", "r", "--expected-version", "1", "--actor", "a"),
        ("--id", "WI-1", "--expected-version", "1", "--actor", "a"),
        ("--id", "WI-1", "--reason", "r", "--actor", "a"),
        ("--id", "WI-1", "--reason", "r", "--expected-version", "1"),
        ("--id", "WI-1", "--reason", "r", "--expected-version", "0", "--actor", "a"),
        ("--id", "WI-1", "--reason", "r", "--expected-version", "x", "--actor", "a"),
    ],
)
def test_retire_usage_errors_exit_2_without_a_request(captured, group, arguments):
    config, calls = captured
    result = invoke(config, group, "retire", *arguments)
    assert result.exit_code == 2, result.output
    assert result.stdout == "" and result.stderr.startswith("Usage:")
    assert "\nError: " in result.stderr and result.stderr.endswith("\n")
    assert not calls


@pytest.mark.parametrize(
    "group,code,message,details",
    [
        ("backlog", "dependants_open", "Refused by the authority", {"id": "WI-1", "dependant_work_item_ids": ["WI-2"]}),
        ("backlog", "work_item_frozen", "Refused by the authority", {"id": "WI-1", "resolution_status": "verified"}),
        (
            "projects",
            "members_open",
            "Refused by the authority",
            {"id": "WI-1", "work_item_ids": ["WI-9"], "project_ids": []},
        ),
        ("projects", "cas_conflict", "Refused by the authority", {"id": "WI-1", "expected": 1, "actual": 2}),
        # The API's top-level validation fields are not domain details. The client exposes code/message only.
        ("backlog", "invalid_request", "Request does not match the domain contract", None),
        ("projects", "invalid_request", "Request does not match the domain contract", None),
    ],
)
def test_retire_refusals_surface_the_code_and_details_with_exit_1(captured, monkeypatch, group, code, message, details):
    config, calls = captured

    def refused(self, method, path, **kwargs):
        calls.append((method, path, kwargs))
        raise AuthorityClientError(code, message, details=details)

    monkeypatch.setattr(AuthorityClient, "request", refused)
    result = retire(config, group, "--json")
    assert result.exit_code == 1, result.output
    assert result.stdout == ""
    expected = f"Error: {code}: {message}\n"
    if details is not None:
        expected += json.dumps(details, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n"
    assert result.stderr == expected
    assert len(calls) == 1 and calls[0][0] == "POST" and calls[0][1].endswith("/WI-1/retire")


@pytest.mark.parametrize("group", ["backlog", "projects"])
def test_retire_against_an_unavailable_authority_exits_1_without_fallback(captured, monkeypatch, group):
    config, _ = captured

    def unavailable(*args, **kwargs):
        raise AuthorityClientError("authority_unavailable", "Unavailable fixture authority")

    monkeypatch.setattr(AuthorityClient, "request", unavailable)
    result = retire(config, group, "--json")
    assert result.exit_code == 1 and result.stdout == ""
    assert result.stderr == "Error: authority_unavailable: Unavailable fixture authority\n"


@pytest.mark.parametrize("group", ["backlog", "projects"])
def test_retire_is_listed_and_documents_its_required_options(captured, group):
    config, calls = captured
    listing = invoke(config, group, "--help")
    assert listing.exit_code == 0 and "retire" in listing.output
    usage = invoke(config, group, "retire", "--help")
    assert usage.exit_code == 0, usage.output
    assert all(option in usage.output for option in ("--id", "--reason", "--expected-version", "--actor", "--json"))
    assert not calls
