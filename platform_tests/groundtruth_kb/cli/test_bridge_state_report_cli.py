"""The ordinary bridge report reads canonical state without harness disclosure."""

from __future__ import annotations

import json
from pathlib import Path

from click.testing import CliRunner
from groundtruth_kb.authority_client import AuthorityClient, AuthorityClientError
from groundtruth_kb.cli import main


def _config(root: Path, *, native: bool = True) -> Path:
    path = root / "groundtruth.toml"
    path.write_text(
        '[groundtruth]\nproject_root = "."\ndb_path = "absent.db"\n'
        + ('authority_url = "http://127.0.0.1:32189"\n' if native else ""),
        encoding="utf-8",
    )
    return path


def _report():
    return {
        "attempt_counts": {"active": 2, "committed": 1},
        "unfiled_attempt_count": 0,
        "active_status_mix": [{"status": "NEW", "count": 1}, {"status": "GO", "count": 1}],
        "active_claim_count": 0,
        "queues": {
            "pb": {"role": "pb", "eligible": [{"id": "implementation", "head_status": "GO"}], "blocked": []},
            "lo": {"role": "lo", "eligible": [{"id": "review", "head_status": "NEW"}], "blocked": []},
        },
    }


def test_state_report_json_uses_selected_authority_without_local_storage(tmp_path: Path, monkeypatch) -> None:
    config = _config(tmp_path)
    calls = []

    def request(self, method, path, **kwargs):
        calls.append((method, path, kwargs))
        return _report()

    monkeypatch.setattr(AuthorityClient, "request", request)
    result = CliRunner().invoke(main, ["--config", str(config), "bridge", "state-report", "--json"])
    assert result.exit_code == 0, result.output
    assert json.loads(result.output) == _report()
    assert calls == [("GET", "/v1/bridge/state-report", {})]
    assert list(tmp_path.iterdir()) == [config]


def test_state_report_markdown_contains_work_without_harness_or_registry_permissions(
    tmp_path: Path, monkeypatch
) -> None:
    config = _config(tmp_path)
    monkeypatch.setattr(AuthorityClient, "request", lambda *args, **kwargs: _report())
    result = CliRunner().invoke(main, ["--config", str(config), "bridge", "state-report", "--markdown"])
    assert result.exit_code == 0, result.output
    assert "implementation" in result.output and "review" in result.output
    assert "NEW" in result.output and "GO" in result.output
    assert "HARNESS" not in result.output.upper()
    assert "REGISTRY PUBLICATION" not in result.output
    assert "NO_ACTION" not in result.output
    assert list(tmp_path.iterdir()) == [config]


def test_state_report_requires_native_authority_without_creating_a_database(tmp_path: Path) -> None:
    config = _config(tmp_path, native=False)
    result = CliRunner().invoke(main, ["--config", str(config), "bridge", "state-report", "--json"])
    assert result.exit_code != 0
    assert "authority_url" in result.output
    assert list(tmp_path.iterdir()) == [config]


def test_state_report_reports_authority_failure_without_local_fallback(tmp_path: Path, monkeypatch) -> None:
    config = _config(tmp_path)

    def unavailable(*args, **kwargs):
        raise AuthorityClientError("authority_unavailable", "Selected authority is unavailable")

    monkeypatch.setattr(AuthorityClient, "request", unavailable)
    result = CliRunner().invoke(main, ["--config", str(config), "bridge", "state-report", "--json"])
    assert result.exit_code != 0 and "authority_unavailable" in result.output
    assert list(tmp_path.iterdir()) == [config]
