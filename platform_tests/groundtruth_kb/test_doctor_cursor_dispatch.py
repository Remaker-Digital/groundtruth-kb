from __future__ import annotations

import sys
from types import SimpleNamespace

import pytest
from groundtruth_kb.project.doctor import _check_cursor_dispatch_readiness


def _report(**overrides):
    return {
        "probe_passed": True,
        "probe_scope": "launch_prerequisites_and_authentication",
        "authority_source": "native_harness_record",
        "harness_qualification": "unqualified",
        **overrides,
    }


def test_doctor_cursor_probe_warns_when_agent_unavailable(monkeypatch, tmp_path):
    fake_module = SimpleNamespace(
        evaluate_readiness=lambda project_root: _report(
            probe_passed=False,
            first_failed_check="headless Cursor Agent CLI: Cursor Agent CLI not found",
        )
    )
    monkeypatch.setitem(sys.modules, "groundtruth_kb.cursor_readiness", fake_module)

    result = _check_cursor_dispatch_readiness(tmp_path)

    assert result.status == "warning"
    assert "Cursor Agent CLI not found" in result.message


def test_doctor_cursor_probe_passes_only_bounded_checks(monkeypatch, tmp_path):
    selected_roots = []

    def evaluate_readiness(*, project_root):
        selected_roots.append(project_root)
        return _report()

    monkeypatch.setitem(
        sys.modules, "groundtruth_kb.cursor_readiness", SimpleNamespace(evaluate_readiness=evaluate_readiness)
    )

    result = _check_cursor_dispatch_readiness(tmp_path)

    assert selected_roots == [tmp_path]
    assert result.name == "Cursor launch prerequisites"
    assert result.status == "pass"
    assert "launch prerequisites and authentication passed" in result.message
    assert "harness qualification is unverified" in result.message
    assert "dispatchable" not in result.message


@pytest.mark.parametrize(
    "report",
    [
        {"ready": True, "dispatchable_now": True},
        _report(probe_passed="true"),
        _report(probe_passed=1),
        _report(authority_source="file_projection"),
        _report(harness_qualification="qualified"),
        _report(probe_scope="launch_prerequisites_authentication_and_bounded_prompt"),
        None,
    ],
)
def test_doctor_cursor_probe_rejects_unsupported_reports(monkeypatch, tmp_path, report):
    fake_module = SimpleNamespace(evaluate_readiness=lambda project_root: report)
    monkeypatch.setitem(sys.modules, "groundtruth_kb.cursor_readiness", fake_module)

    result = _check_cursor_dispatch_readiness(tmp_path)

    assert result.status == "warning"
    assert "unsupported report" in result.message
    assert "harness qualification is unverified" in result.message


def test_doctor_cursor_probe_does_not_echo_private_exception(monkeypatch, tmp_path):
    def evaluate_readiness(*, project_root):
        raise RuntimeError("private prompt and authentication response")

    monkeypatch.setitem(
        sys.modules, "groundtruth_kb.cursor_readiness", SimpleNamespace(evaluate_readiness=evaluate_readiness)
    )

    result = _check_cursor_dispatch_readiness(tmp_path)

    assert result.status == "warning"
    assert "RuntimeError" in result.message
    assert "private prompt" not in result.message
