"""The deployment automation writers take their designed warn-and-continue path without the retired SQLite shim (owner ruling D3).

`scripts/_defect_reporter.py::create_defect` (SPEC-1617 defect work items from the deploy pipelines) and
`scripts/test_pipeline.py::_record_phase_result` (PLAN-001 phase results) wrote through the `tools/knowledge-db` shim that the
realignment retired (GOV-SOT-SINGLETON-001; increment c80). Owner ruling D3 (2026-09-16) accepts the degraded path for the
cutover window and records the native port as WI-7860; until the port lands, this module is the executable evidence of the
accepted state: the writers never raise, record nothing anywhere, and say so on their own output channel.
"""

from __future__ import annotations

import importlib
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture
def without_shim(monkeypatch, tmp_path):
    """The retired shim is absent from the tree; `db` is not importable; the working directory is disposable."""
    assert not (ROOT / "tools" / "knowledge-db").exists(), "the SQLite shim is retired (c80)"
    # `from db import KnowledgeDB` raises ImportError regardless of sys.path
    monkeypatch.setitem(sys.modules, "db", None)
    monkeypatch.chdir(tmp_path)
    return tmp_path


def test_create_defect_warns_and_returns_none_without_the_shim(without_shim, capsys):
    reporter = importlib.import_module("scripts._defect_reporter")
    result = reporter.create_defect(
        title="Deploy pipeline failure: Phase 7 (ACR Docker Build)",
        description="Build failed with exit code 1",
        source_spec_id="SPEC-1617",
        component="infrastructure_automation",
        changed_by="deploy-pipeline",
    )
    out = capsys.readouterr()
    assert result is None
    assert "[WARN] Could not create DEFECT work item" in out.out
    assert sorted(p.name for p in without_shim.iterdir()) == [], "the degraded path must record nothing"


def test_record_phase_result_warns_and_continues_without_the_shim(without_shim, capsys):
    pipeline = importlib.import_module("scripts.test_pipeline")
    pipeline._record_phase_result(1, "pass", "Automated execution")  # must not raise
    out = capsys.readouterr()
    assert "KB phase update failed" in out.out + out.err
    assert sorted(p.name for p in without_shim.iterdir()) == [], "the degraded path must record nothing"


def test_the_writers_still_name_the_retired_shim_path_only_as_dead_sys_path_entries():
    """The port (WI-7860) removes these lines; until then they are inert: the directory does not exist."""
    for script in ("scripts/_defect_reporter.py", "scripts/test_pipeline.py"):
        text = (ROOT / script).read_text(encoding="utf-8")
        assert 'sys.path.insert(0, str(PROJECT_ROOT / "tools" / "knowledge-db"))' in text, script
    assert not (ROOT / "tools" / "knowledge-db").exists()
