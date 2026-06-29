from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = REPO_ROOT / "scripts" / "verify_codex_dispatch.py"


def _load_module():
    if str(REPO_ROOT) not in sys.path:
        sys.path.insert(0, str(REPO_ROOT))
    spec = importlib.util.spec_from_file_location("verify_codex_dispatch", SCRIPT_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _write_registry(root: Path, record: dict) -> None:
    state = root / "harness-state"
    state.mkdir()
    (state / "harness-registry.json").write_text(json.dumps({"schema_version": 1, "harnesses": [record]}))


def _codex_record(**overrides):
    record = {
        "can_receive_dispatch": True,
        "harness_name": "codex",
        "harness_type": "codex",
        "id": "A",
        "invocation_surfaces": {"headless": {"argv": ["codex", "exec", "{{PROMPT}}"]}},
        "status": "active",
    }
    record.update(overrides)
    return record


def test_evaluate_readiness_reports_dispatchable_when_static_requirements_pass(tmp_path: Path) -> None:
    module = _load_module()
    _write_registry(tmp_path, _codex_record())

    result = module.evaluate_readiness(project_root=tmp_path, executable_resolver=lambda _name: "codex.exe")

    assert result["static_ok"] is True
    assert result["dispatchable"] is True
    assert result["resolved_executable"] == "codex.exe"


def test_evaluate_readiness_fails_when_executable_required_and_missing(tmp_path: Path) -> None:
    module = _load_module()
    _write_registry(tmp_path, _codex_record())

    result = module.evaluate_readiness(project_root=tmp_path, executable_resolver=lambda _name: None)

    assert result["static_ok"] is False
    assert result["dispatchable"] is False
    assert result["executable_ok"] is False


def test_evaluate_readiness_errors_for_wrong_harness_type(tmp_path: Path) -> None:
    module = _load_module()
    _write_registry(tmp_path, _codex_record(harness_type="claude"))

    with pytest.raises(module.VerificationError, match="is not codex"):
        module.evaluate_readiness(project_root=tmp_path, executable_resolver=lambda _name: "codex.exe")
