"""FAB-10 regression tests for bridge/INDEX.md well-formedness checks."""

from __future__ import annotations

import importlib.util
from pathlib import Path
from types import ModuleType

REPO_ROOT = Path(__file__).resolve().parents[2]
LIVE_HOOK = REPO_ROOT / ".claude" / "hooks" / "bridge-compliance-gate.py"


def _load_gate() -> ModuleType:
    spec = importlib.util.spec_from_file_location("bridge_compliance_gate_fab10_index", LIVE_HOOK)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_index_gate_rejects_literal_escaped_newline() -> None:
    gate = _load_gate()
    content = "Document: fixture\\nNEW: bridge/fixture-001.md\n"

    reason = gate._deny_reason_for_content(
        cwd_path=REPO_ROOT,
        file_path="bridge/INDEX.md",
        content=content,
        run_pending_preflight=False,
    )

    assert reason is not None
    assert "literal escaped newline" in reason


def test_index_gate_allows_parseable_index() -> None:
    gate = _load_gate()
    content = "Document: fixture\nNEW: bridge/fixture-001.md\n"

    reason = gate._deny_reason_for_content(
        cwd_path=REPO_ROOT,
        file_path="bridge/INDEX.md",
        content=content,
        run_pending_preflight=False,
    )

    assert reason is None


def test_doctor_fails_on_malformed_bridge_index(tmp_path: Path) -> None:
    from groundtruth_kb.project.doctor import _check_file_bridge_index_parse

    bridge_dir = tmp_path / "bridge"
    bridge_dir.mkdir()
    (bridge_dir / "INDEX.md").write_text("Document: fixture\\nNEW: bridge/fixture-001.md\n", encoding="utf-8")

    check = _check_file_bridge_index_parse(tmp_path)

    assert check.status == "fail"
    assert "literal escaped newline" in check.message
