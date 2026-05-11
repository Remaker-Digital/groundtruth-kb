from __future__ import annotations

import json
import subprocess
from pathlib import Path

from click.testing import CliRunner
from groundtruth_kb.cli import _SECRET_SCAN_FINDINGS_EXIT, main


def _stripe_test_secret() -> str:
    return "sk" + "_test" + "_" + "A" * 24


def test_gt_secrets_scan_paths_redacts_stdout(tmp_path: Path) -> None:
    secret = _stripe_test_secret()
    target = tmp_path / "candidate.txt"
    target.write_text(f"token={secret}\n", encoding="utf-8")

    result = CliRunner().invoke(
        main,
        ["secrets", "scan", "--paths", str(target), "--redacted", "--fail-on", "verified-provider"],
    )

    assert result.exit_code == _SECRET_SCAN_FINDINGS_EXIT
    assert "stripe_test_secret_key" in result.output
    assert "sha256:" in result.output
    assert secret not in result.output


def test_gt_secrets_scan_json_and_report_are_redacted(tmp_path: Path) -> None:
    secret = _stripe_test_secret()
    target = tmp_path / "candidate.txt"
    report = tmp_path / "report.json"
    target.write_text(f"token={secret}\n", encoding="utf-8")

    result = CliRunner().invoke(
        main,
        [
            "secrets",
            "scan",
            "--paths",
            str(target),
            "--json",
            "--report-json",
            str(report),
            "--fail-on",
            "",
        ],
    )

    assert result.exit_code == 0
    stdout_payload = json.loads(result.output)
    report_text = report.read_text(encoding="utf-8")
    assert stdout_payload["finding_count"] == 1
    assert secret not in result.output
    assert secret not in report_text
    assert "sha256:" in report_text


def test_gt_secrets_scan_help_lists_slice_one_and_deferred_modes() -> None:
    result = CliRunner().invoke(main, ["secrets", "scan", "--help"])

    assert result.exit_code == 0
    assert "--staged" in result.output
    assert "--paths" in result.output
    assert "--range" in result.output
    assert "--all-refs" in result.output


def test_gt_secrets_scan_all_refs_emits_redacted_local_history_inventory(tmp_path: Path) -> None:
    secret = _stripe_test_secret()
    runner = CliRunner()

    with runner.isolated_filesystem(temp_dir=tmp_path):
        cwd = Path.cwd()
        subprocess.run(["git", "init"], cwd=cwd, check=True, capture_output=True, text=True)
        subprocess.run(["git", "config", "user.email", "tester@example.invalid"], cwd=cwd, check=True)
        subprocess.run(["git", "config", "user.name", "GTKB Test"], cwd=cwd, check=True)
        target = cwd / "history.txt"
        target.write_text(f"token={secret}\n", encoding="utf-8")
        subprocess.run(["git", "add", "history.txt"], cwd=cwd, check=True)
        subprocess.run(["git", "commit", "-m", "history"], cwd=cwd, check=True, capture_output=True, text=True)

        result = runner.invoke(main, ["secrets", "scan", "--all-refs", "--json", "--fail-on", ""])

    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert payload["mode"] == "all-refs"
    assert payload["finding_count"] == 1
    assert secret not in result.output
    assert "sha256:" in result.output
