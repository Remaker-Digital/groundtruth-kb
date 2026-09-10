"""Authored bridge delivery replaces generated proposals and hidden drafts."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from click.testing import CliRunner

from groundtruth_kb.authority_client import AuthorityClient, AuthorityClientError
from groundtruth_kb.cli import main


def config_at(root: Path, native: bool) -> Path:
    config = root / "groundtruth.toml"
    config.write_text(
        '[groundtruth]\nproject_root = "."\ndb_path = "absent.db"\n'
        + ('authority_url = "http://127.0.0.1:32189"\n' if native else ""),
        encoding="utf-8",
    )
    return config


@pytest.mark.parametrize("native", [False, True])
@pytest.mark.parametrize("command", ["propose", "file-implementation-proposal"])
def test_removed_proposal_generators_are_not_available(tmp_path, native, command):
    config = config_at(tmp_path, native)
    result = CliRunner().invoke(main, ["--config", str(config), "bridge", command, "--help"])
    assert result.exit_code != 0
    assert "No such command" in result.output
    assert list(tmp_path.iterdir()) == [config]


def test_deliver_preserves_authored_bytes_and_explicit_identity(tmp_path, monkeypatch):
    config = config_at(tmp_path, True)
    candidate = tmp_path / "authored.md"
    content = "::init gtkb lo\r\n::open build\r\nNEW\r\n\r\nAuthored: café 漢字\r\n"
    candidate.write_bytes(content.encode("utf-8"))
    calls = []

    def request(self, method, path, **kwargs):
        calls.append((method, path, kwargs))
        return {"status": "delivered", "document": "proposal", "version": 1}

    monkeypatch.setattr(AuthorityClient, "request", request)
    monkeypatch.setenv("GTKB_SESSION_ID", "another-context")
    result = CliRunner().invoke(
        main,
        [
            "--config",
            str(config),
            "bridge",
            "deliver",
            "proposal",
            "--native-context-id",
            "actual-context",
            "--fence",
            "7",
            "--content-file",
            str(candidate),
            "--json",
        ],
    )
    assert result.exit_code == 0, result.output
    assert json.loads(result.output)["status"] == "delivered"
    assert calls == [
        (
            "POST",
            "/v1/bridge/proposal/deliver",
            {
                "body": {
                    "native_context_id": "actual-context",
                    "fence": 7,
                    "content": content,
                    "mode": "interactive",
                }
            },
        )
    ]
    assert candidate.read_bytes() == content.encode("utf-8")
    assert set(tmp_path.iterdir()) == {config, candidate}


def test_delivery_outage_does_not_fall_back_to_a_local_bridge(tmp_path, monkeypatch):
    config = config_at(tmp_path, True)
    candidate = tmp_path / "authored.md"
    candidate.write_text("Authored content\n", encoding="utf-8")

    def unavailable(*args, **kwargs):
        raise AuthorityClientError("authority_unavailable", "The selected authority is unavailable")

    monkeypatch.setattr(AuthorityClient, "request", unavailable)
    result = CliRunner().invoke(
        main,
        [
            "--config",
            str(config),
            "bridge",
            "deliver",
            "proposal",
            "--native-context-id",
            "actual-context",
            "--fence",
            "7",
            "--content-file",
            str(candidate),
            "--json",
        ],
    )
    assert result.exit_code != 0 and "authority_unavailable" in result.output
    assert set(tmp_path.iterdir()) == {config, candidate}
