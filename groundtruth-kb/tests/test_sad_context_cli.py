"""CLI facade composition remains an explicit read, with no fallback or file write."""

from __future__ import annotations

import io
import json

import pytest
from click.testing import CliRunner

from groundtruth_kb import cli_authority as cli


@pytest.mark.parametrize("json_output", [False, True])
def test_cli_composes_for_successor_and_returns_the_requested_output(monkeypatch, json_output):
    captured = []
    monkeypatch.setenv("GTKB_SESSION_ROLE", "pb")
    monkeypatch.setattr(
        cli,
        "_call",
        lambda ctx, method, path, **kwargs: (
            captured.append((method, path, kwargs))
            or {"message_context": {"text": "Quoted current successor context\n"}}
        ),
    )
    result = CliRunner().invoke(
        cli.context_group,
        [
            "work-item",
            "WI-1",
            "--recipient-role",
            "lo",
            "--activity",
            "test",
            "--critical-section",
            "2.4",
            "--critical-spec",
            "SPEC-A",
            "--critical-spec",
            "SPEC-B",
            *(["--json"] if json_output else []),
        ],
    )
    assert result.exit_code == 0
    if json_output:
        assert json.loads(result.output) == {"message_context": {"text": "Quoted current successor context\n"}}
    else:
        assert result.output == "Quoted current successor context\n"
    assert captured == [
        (
            "GET",
            "/v1/work-items/WI-1/context",
            {
                "query": {
                    "recipient_role": "lo",
                    "activity": "test",
                    "critical_sections": "2.4",
                    "critical_specs": "SPEC-A,SPEC-B",
                }
            },
        )
    ]


@pytest.mark.parametrize(
    "options",
    [
        ["--recipient-role", "pb"],
        ["--activity", "build"],
        ["--critical-spec", "SPEC-A"],
        ["--recipient-role", "pb", "--activity", "build", "--critical-spec", "SPEC-A,SPEC-B"],
    ],
)
def test_cli_requires_complete_literal_inputs_before_any_canonical_read(monkeypatch, options):
    def forbidden(*args, **kwargs):
        pytest.fail("Incomplete input contacted the authority")

    monkeypatch.setattr(cli, "_call", forbidden)
    result = CliRunner().invoke(cli.context_group, ["work-item", "WI-1", *options])
    assert result.exit_code != 0 and ("requires both" in result.output or "literal ID" in result.output)


def test_cli_ordinary_no_option_read_keeps_existing_call_shape(monkeypatch):
    captured = []
    client = cli.AuthorityClient("http://127.0.0.1:8765")

    def open_response(request, *, timeout):
        assert timeout > 0
        captured.append((request.get_method(), request.full_url, request.data))
        return io.BytesIO(b'{"work_item":{"id":"WI-1","description":"current"}}')

    monkeypatch.setattr(cli, "_client", lambda ctx: client)
    monkeypatch.setattr(client._opener, "open", open_response)
    result = CliRunner().invoke(cli.context_group, ["work-item", "WI-1", "--json"])
    assert result.exit_code == 0
    assert captured == [("GET", "http://127.0.0.1:8765/v1/work-items/WI-1/context", None)]
    assert json.loads(result.output) == {"work_item": {"id": "WI-1", "description": "current"}}


@pytest.mark.parametrize("output_options", [[], ["--json"]])
@pytest.mark.parametrize("composed", [None, {"text": ""}, "malformed"])
def test_cli_missing_composer_response_is_refused_without_ordinary_context_fallback(
    monkeypatch, output_options, composed
):
    response = {"work_item": {"id": "WI-1"}}
    if composed is not None:
        response["message_context"] = composed
    monkeypatch.setattr(cli, "_call", lambda *args, **kwargs: response)
    result = CliRunner().invoke(
        cli.context_group, ["work-item", "WI-1", "--recipient-role", "lo", "--activity", "test", *output_options]
    )
    assert result.exit_code != 0 and "no composed context" in result.output
