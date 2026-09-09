"""Ordinary task loading must not expose the retired descriptor packet producer."""

from pathlib import Path

from click.testing import CliRunner
from groundtruth_kb.cli import main


def test_retired_packet_route_cannot_return_ready_from_local_descriptors(tmp_path: Path, monkeypatch) -> None:
    config = tmp_path / "groundtruth.toml"
    config.write_text('[groundtruth]\ndb_path = "groundtruth.db"\nproject_root = "."\n', encoding="utf-8")
    monkeypatch.delenv("GT_DB_PATH", raising=False)
    monkeypatch.delenv("GT_PROJECT_ROOT", raising=False)
    monkeypatch.delenv("GTKB_AUTHORITY_URL", raising=False)
    args = ["--config", str(config), "session", "envelope"]

    help_result = CliRunner().invoke(main, [*args, "--help"])
    assert help_result.exit_code == 0, help_result.output
    assert "packet" not in help_result.output
    result = CliRunner().invoke(main, [*args, "packet"])
    assert result.exit_code != 0
    assert "No such command 'packet'" in result.output
    assert not (tmp_path / "groundtruth.db").exists()
