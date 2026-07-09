# (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""WI-5107: bridge-filing helper subprocess calls must run headless (no console window).

Each interactive bridge-filing subprocess (`gtkb_bridge_writer` git-check +
compliance-audit; the bridge helper preflight/git runners) must spread the
canonical `no_window_subprocess_kwargs()` into its `subprocess.run(...)` call so
Windows does not flash a console window. These tests are OS-independent: they
monkeypatch `no_window_subprocess_kwargs` to a sentinel and assert the sentinel
kwarg reaches `subprocess.run`.
"""

from __future__ import annotations

import importlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
for _p in (
    str(ROOT),
    str(ROOT / "groundtruth-kb" / "src"),
    str(ROOT / ".claude" / "skills" / "bridge" / "helpers"),
):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import scripts.gtkb_bridge_writer as writer  # noqa: E402

_SENTINEL_FLAGS = 0x08000000  # CREATE_NO_WINDOW


class _FakeCompleted:
    def __init__(self, stdout: object = "", returncode: int = 0) -> None:
        self.stdout = stdout
        self.stderr = ""
        self.returncode = returncode


def test_git_committed_check_spreads_no_window(monkeypatch, tmp_path):
    captured: dict = {}
    monkeypatch.setattr(writer, "no_window_subprocess_kwargs", lambda: {"creationflags": _SENTINEL_FLAGS})

    def fake_run(*_args, **kwargs):
        captured.update(kwargs)
        return _FakeCompleted(stdout=b"")

    monkeypatch.setattr(writer.subprocess, "run", fake_run)
    writer._bridge_file_committed_in_git(tmp_path / "bridge" / "x-001.md", tmp_path)
    assert captured.get("creationflags") == _SENTINEL_FLAGS


def test_compliance_audit_spreads_no_window(monkeypatch, tmp_path):
    import json as _json

    captured: dict = {}
    monkeypatch.setattr(writer, "no_window_subprocess_kwargs", lambda: {"creationflags": _SENTINEL_FLAGS})

    def fake_run(cmd, **kwargs):
        captured.update(kwargs)
        # The audit writes its verdict JSON to the --audit-output path; emulate a pass.
        out_path = Path(cmd[cmd.index("--audit-output") + 1])
        out_path.write_text(_json.dumps({"decision": "pass"}), encoding="utf-8")
        return _FakeCompleted(stdout="", returncode=0)

    monkeypatch.setattr(writer.subprocess, "run", fake_run)
    # A gate path must exist for _bridge_compliance_gate_path resolution; point at any file.
    gate = tmp_path / "gate.py"
    gate.write_text("# stub gate\n", encoding="utf-8")
    monkeypatch.setattr(writer, "_bridge_compliance_gate_path", lambda project_root: gate)
    writer.run_bridge_compliance_audit(
        file_path=tmp_path / "bridge" / "x-001.md", content="NEW\n", project_root=tmp_path
    )
    assert captured.get("creationflags") == _SENTINEL_FLAGS


def test_revise_preflight_runner_spreads_no_window(monkeypatch, tmp_path):
    revise = importlib.import_module("revise_bridge")
    captured: dict = {}
    monkeypatch.setattr(revise, "no_window_subprocess_kwargs", lambda: {"creationflags": _SENTINEL_FLAGS})

    def fake_run(*_args, **kwargs):
        captured.update(kwargs)
        return _FakeCompleted(stdout="", returncode=0)

    monkeypatch.setattr(revise.subprocess, "run", fake_run)
    revise._run_preflight_command(["echo", "ok"], cwd=tmp_path)
    assert captured.get("creationflags") == _SENTINEL_FLAGS


def test_impl_report_git_lines_spreads_no_window(monkeypatch, tmp_path):
    sys.path.insert(0, str(ROOT / ".claude" / "skills" / "bridge" / "helpers"))
    impl_report = importlib.import_module("impl_report_bridge")
    captured: dict = {}
    monkeypatch.setattr(impl_report, "no_window_subprocess_kwargs", lambda: {"creationflags": _SENTINEL_FLAGS})

    def fake_run(*_args, **kwargs):
        captured.update(kwargs)
        return _FakeCompleted(stdout="", returncode=0)

    monkeypatch.setattr(impl_report.subprocess, "run", fake_run)
    impl_report._git_lines(["status"], cwd=tmp_path)
    assert captured.get("creationflags") == _SENTINEL_FLAGS
