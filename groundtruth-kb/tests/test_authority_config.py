"""The native client selects one explicit local service without credential URLs."""

import pytest
from click.testing import CliRunner

from groundtruth_kb.cli import main
from groundtruth_kb.config import GTConfig, GTConfigError, validate_authority_url


@pytest.mark.parametrize(
    "url",
    [
        "http://127.0.0.1:8765",
        "http://127.0.0.1:8765/",
    ],
)
def test_loopback_endpoint_normalizes(url):
    assert validate_authority_url(url) == "http://127.0.0.1:8765"


@pytest.mark.parametrize(
    "url",
    [
        "",
        "http://127.0.0.1",
        "http://127.0.0.1:0",
        "http://127.0.0.1:65536",
        "http://workstation:8765",
        "http://127.0.0.1:8765/other",
        "https://127.0.0.1:8765",
        "http://owner:secret@127.0.0.1:8765",
        "http://127.0.0.1:8765?token=secret",
        "http://127.0.0.1:8765#ignored",
    ],
)
def test_unknown_transports_and_embedded_credentials_are_not_silently_accepted(url):
    with pytest.raises(GTConfigError) as error:
        validate_authority_url(url)
    assert "secret" not in str(error.value)


def test_native_help_and_unavailable_commands_do_not_open_sqlite(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("GT_AUTHORITY_URL", raising=False)
    config_path = tmp_path / "groundtruth.toml"
    config_path.write_text(
        '[groundtruth]\nauthority_url="http://127.0.0.1:8765"\ndb_path="absent.db"\n', encoding="utf-8"
    )
    assert GTConfig.load(config_path=config_path).authority_url == "http://127.0.0.1:8765"
    help_result = CliRunner().invoke(main, ["--config", str(config_path), "--help"])
    assert help_result.exit_code == 0, help_result.output
    assert "service" in help_result.output
    assert "generate-approval-packet" not in help_result.output
    rejected = CliRunner().invoke(main, ["--config", str(config_path), "db", "postgres", "status"])
    assert rejected.exit_code == 1
    assert "fallback is disabled" in rejected.output
    assert not (tmp_path / "absent.db").exists()
