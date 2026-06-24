"""Focused tests for the WI-4587 Bridge CLI benchmark wrapper."""

from __future__ import annotations

import json
import sys
from pathlib import Path

from click.testing import CliRunner

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "groundtruth-kb" / "src"))

from groundtruth_kb.cli import main  # noqa: E402

from scripts.benchmarks import cli as benchmark_cli  # noqa: E402


def _invoke(*args: str):
    return CliRunner().invoke(main, ["bridge", "benchmark", *args])


def test_bridge_benchmark_help_lists_cli_surface():
    result = _invoke("--help")

    assert result.exit_code == 0
    assert "run" in result.output
    assert "report" in result.output
    assert "compare" in result.output
    assert "manifest" in result.output


def test_bridge_benchmark_run_delegates_to_benchmark_module(monkeypatch):
    captured: list[str] = []

    def fake_main(argv: list[str]) -> int:
        captured.extend(argv)
        print("delegated-run")
        return 0

    monkeypatch.setattr(benchmark_cli, "main", fake_main)

    result = _invoke(
        "run",
        "--benchmark",
        "assertion_signal_noise",
        "--window-start",
        "2026-01-01T00:00:00+00:00",
        "--window-end",
        "2026-01-02T00:00:00+00:00",
    )

    assert result.exit_code == 0
    assert captured == [
        "run",
        "--benchmark",
        "assertion_signal_noise",
        "--window-start",
        "2026-01-01T00:00:00+00:00",
        "--window-end",
        "2026-01-02T00:00:00+00:00",
    ]
    assert "delegated-run" in result.output


def test_bridge_benchmark_report_and_compare_delegate(monkeypatch):
    calls: list[list[str]] = []

    def fake_main(argv: list[str]) -> int:
        calls.append(list(argv))
        return 0

    monkeypatch.setattr(benchmark_cli, "main", fake_main)

    report = _invoke("report", "--run-id", "RUN-A")
    compare = _invoke("compare", "--baseline", "RUN-A", "--candidate", "RUN-B")

    assert report.exit_code == 0
    assert compare.exit_code == 0
    assert calls == [
        ["report", "--run-id", "RUN-A"],
        ["compare", "--baseline", "RUN-A", "--candidate", "RUN-B"],
    ]


def test_bridge_benchmark_manifest_json_is_valid_and_read_only(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    result = _invoke("manifest", "--json")

    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert payload["valid"] is True
    assert payload["validation_errors"] == []
    assert payload["summary"]["modes"] == 2
    assert payload["summary"]["dispatcher_bridge_cli_requirements"] >= 1
    assert not (tmp_path / ".gtkb-state").exists()
    assert not (tmp_path / "groundtruth.db").exists()


def test_bridge_benchmark_missing_required_argument_fails_safely():
    result = _invoke("report")

    assert result.exit_code != 0
    assert "Missing option" in result.output
    assert "Traceback" not in result.output


def test_benchmark_module_manifest_command_preserves_direct_entrypoint(capsys):
    exit_code = benchmark_cli.main(["manifest", "--json"])

    assert exit_code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["valid"] is True
