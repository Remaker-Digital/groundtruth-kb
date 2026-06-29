from __future__ import annotations

import sys
from types import SimpleNamespace

from groundtruth_kb.project.doctor import _check_cursor_dispatch_readiness


def test_doctor_cursor_dispatch_warns_when_agent_unavailable(monkeypatch, tmp_path):
    fake_module = SimpleNamespace(
        evaluate_readiness=lambda project_root: {
            "first_failed_check": "headless Cursor Agent CLI: Cursor Agent CLI not found",
            "ready": False,
        }
    )
    monkeypatch.setitem(sys.modules, "scripts.verify_cursor_dispatch", fake_module)

    result = _check_cursor_dispatch_readiness(tmp_path)

    assert result.status == "warning"
    assert "Cursor headless dispatch unavailable" in result.message
    assert "Cursor Agent CLI not found" in result.message


def test_doctor_cursor_dispatch_passes_when_ready_but_not_selected(monkeypatch, tmp_path):
    fake_module = SimpleNamespace(
        evaluate_readiness=lambda project_root: {
            "dispatchable_now": False,
            "ready": True,
        }
    )
    monkeypatch.setitem(sys.modules, "scripts.verify_cursor_dispatch", fake_module)

    result = _check_cursor_dispatch_readiness(tmp_path)

    assert result.status == "pass"
    assert "ready but not currently selected" in result.message


def test_doctor_cursor_dispatch_passes_when_dispatchable(monkeypatch, tmp_path):
    fake_module = SimpleNamespace(
        evaluate_readiness=lambda project_root: {
            "dispatchable_now": True,
            "ready": True,
        }
    )
    monkeypatch.setitem(sys.modules, "scripts.verify_cursor_dispatch", fake_module)

    result = _check_cursor_dispatch_readiness(tmp_path)

    assert result.status == "pass"
    assert "dispatchable" in result.message
