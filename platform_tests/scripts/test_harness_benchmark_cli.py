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


def test_benchmark_module_manifest_command_preserves_direct_entrypoint(capsys):
    exit_code = benchmark_cli.main(["manifest", "--json"])

    assert exit_code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["valid"] is True


def test_benchmark_module_cadence_report_writes_json_and_markdown(tmp_path, capsys):
    payload_path = tmp_path / "evidence.json"
    payload_path.write_text(
        json.dumps(
            {
                "run_id": "RUN-WRITE",
                "evidence_records": [],
            }
        ),
        encoding="utf-8",
    )

    exit_code = benchmark_cli.main(
        [
            "cadence-report",
            "--input-json",
            str(payload_path),
            "--project-root",
            str(tmp_path),
            "--output-run-id",
            "RUN-WRITE-OUT",
        ]
    )

    assert exit_code == 0
    paths = json.loads(capsys.readouterr().out)
    assert paths["run_id"] == "RUN-WRITE-OUT"
    # Canon s17: benchmark output is session-scoped scratch, never `.gtkb-state`.
    from scripts.gtkb_session_id import session_scratch_dirname

    out_root = tmp_path / "scratchpad" / session_scratch_dirname() / "benchmarks" / "RUN-WRITE-OUT"
    assert (out_root / "harness-quality-cadence-report.json").is_file()
    assert (out_root / "harness-quality-cadence-report.md").is_file()
    assert not (tmp_path / ".gtkb-state").exists()
