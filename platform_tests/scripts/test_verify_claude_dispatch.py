from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = REPO_ROOT / "scripts" / "verify_claude_dispatch.py"


def _load_module():
    if str(REPO_ROOT) not in sys.path:
        sys.path.insert(0, str(REPO_ROOT))
    spec = importlib.util.spec_from_file_location("verify_claude_dispatch", SCRIPT_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _write_registry(root: Path, record: dict) -> None:
    state = root / "harness-state"
    state.mkdir()
    (state / "harness-registry.json").write_text(json.dumps({"schema_version": 1, "harnesses": [record]}))


def _claude_record(**overrides):
    record = {
        "can_receive_dispatch": False,
        "harness_name": "claude",
        "harness_type": "claude",
        "id": "B",
        "invocation_surfaces": {"headless": {"argv": ["claude", "-p", "{{PROMPT}}"]}},
        "status": "suspended",
    }
    record.update(overrides)
    return record


def test_evaluate_readiness_reports_static_ok_without_claiming_dispatchable_for_suspended(tmp_path: Path) -> None:
    module = _load_module()
    _write_registry(tmp_path, _claude_record())

    result = module.evaluate_readiness(project_root=tmp_path, executable_resolver=lambda _name: "claude.exe")

    assert result["static_ok"] is True
    assert result["dispatchable"] is False
    assert result["status"] == "suspended"


def test_evaluate_readiness_can_report_dispatchable_when_registry_allows_it(tmp_path: Path) -> None:
    module = _load_module()
    _write_registry(tmp_path, _claude_record(status="active", can_receive_dispatch=True))

    result = module.evaluate_readiness(project_root=tmp_path, executable_resolver=lambda _name: "claude.exe")

    assert result["static_ok"] is True
    assert result["dispatchable"] is True


def test_evaluate_readiness_errors_for_wrong_harness_type(tmp_path: Path) -> None:
    module = _load_module()
    _write_registry(tmp_path, _claude_record(harness_type="codex"))

    with pytest.raises(module.VerificationError, match="is not claude"):
        module.evaluate_readiness(project_root=tmp_path, executable_resolver=lambda _name: "claude.exe")
