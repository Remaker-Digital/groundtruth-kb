"""Doctor must not treat disposable verdict files as work awaiting a Git commit."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from types import SimpleNamespace

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "groundtruth-kb" / "src"))

from groundtruth_kb.project import checks, doctor, doctor_isolation  # noqa: E402


def test_doctor_does_not_require_bridge_files_in_git(tmp_path, monkeypatch):
    bridge = tmp_path / "bridge"
    bridge.mkdir()
    verdict = bridge / "review-005.md"
    verdict.write_text("VERIFIED\n\nAn independent review may precede project commit.\n", encoding="utf-8")
    scripts = tmp_path / "scripts"
    scripts.mkdir()
    (scripts / "auto_finalize_sweep.py").write_text("# obsolete installation residue\n", encoding="utf-8")

    # Keep the offending diagnostics live in the pre-repair implementation;
    # unrelated machine, provider and project checks are outside this regression.
    retired_checks = {"_check_untracked_terminal_verified_verdicts", "_check_auto_finalize_sweep_liveness"}
    for name, function in list(vars(doctor).items()):
        if name.startswith("_check_") and callable(function) and name not in retired_checks:
            monkeypatch.setattr(doctor, name, lambda *args, **kwargs: doctor.ToolCheck("unrelated", False, True))
    monkeypatch.setattr(checks, "get_registered_checks", lambda: {})
    monkeypatch.setattr(doctor_isolation, "run_isolation_checks", lambda *args, **kwargs: [])
    monkeypatch.setattr(doctor, "_dispatcher_complex_health_reader", lambda target: lambda: {})
    commands = []

    def run_command(command, **kwargs):
        commands.append(command)
        return True, "bridge/review-005.md"

    def run_probe(command, **kwargs):
        commands.append(command)
        return SimpleNamespace(returncode=0, stdout=json.dumps({"terminal_verified_backlog": []}))

    monkeypatch.setattr(doctor, "_run_cmd", run_command)
    monkeypatch.setattr(doctor.subprocess, "run", run_probe)
    before = verdict.read_bytes()

    report = doctor.run_doctor(tmp_path, "dual-agent")

    assert commands == []
    assert report.overall == "pass"
    assert "git add" not in doctor.format_doctor_report(report)
    assert verdict.read_bytes() == before
