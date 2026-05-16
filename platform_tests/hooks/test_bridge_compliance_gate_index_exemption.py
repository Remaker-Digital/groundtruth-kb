"""Regression tests for the bridge-compliance-gate bridge/INDEX.md exemption.

The pending-proposal target-path checkpoint in the bridge-compliance-gate
hook's main() must never emit an `ask` for edits to bridge/INDEX.md. The
canonical bridge queue is edited as intrinsic protocol on every proposal
filing, verdict, and status transition - even while a pending NEW/REVISED/NO-GO
proposal legitimately lists bridge/INDEX.md in its target_paths. The checkpoint
must still fire for every non-INDEX target path.

The fix is applied identically to the live hook and the scaffold template, so
the behavioral tests are parametrized over both copies.

Source: bridge/gtkb-bridge-compliance-gate-index-exemption-001.md (Codex GO at
-002); WI-3334 under PROJECT-GTKB-RELIABILITY-FIXES;
GOV-FILE-BRIDGE-AUTHORITY-001 / CLAUSE-INDEX-IS-CANONICAL.
"""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from types import ModuleType

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
LIVE_HOOK = REPO_ROOT / ".claude" / "hooks" / "bridge-compliance-gate.py"
TEMPLATE_HOOK = REPO_ROOT / "groundtruth-kb" / "templates" / "hooks" / "bridge-compliance-gate.py"


def _load_gate(path: Path, module_name: str) -> ModuleType:
    """Import a hyphenated hook file by path under a unique module name."""
    spec = importlib.util.spec_from_file_location(module_name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_HOOKS = {
    "live": _load_gate(LIVE_HOOK, "bridge_compliance_gate_live"),
    "template": _load_gate(TEMPLATE_HOOK, "bridge_compliance_gate_template"),
}


@pytest.fixture(params=sorted(_HOOKS), ids=sorted(_HOOKS))
def gate(request: pytest.FixtureRequest) -> ModuleType:
    """The bridge-compliance-gate hook module, once per copy (live + template)."""
    return _HOOKS[request.param]


def _write_index(tmp_path: Path, entries: str) -> Path:
    """Create a fixture bridge/INDEX.md under tmp_path; return its path."""
    bridge_dir = tmp_path / "bridge"
    bridge_dir.mkdir(parents=True, exist_ok=True)
    index = bridge_dir / "INDEX.md"
    index.write_text(entries, encoding="utf-8")
    return index


def _write_proposal(tmp_path: Path, filename: str, target_paths: list[str]) -> None:
    """Create a fixture bridge proposal file declaring target_paths."""
    bridge_dir = tmp_path / "bridge"
    bridge_dir.mkdir(parents=True, exist_ok=True)
    body = f"NEW\n\n# Fixture proposal\n\ntarget_paths: {json.dumps(target_paths)}\n"
    (bridge_dir / filename).write_text(body, encoding="utf-8")


# --- _is_bridge_index_file --------------------------------------------------


def test_is_bridge_index_file_recognizes_index(gate: ModuleType) -> None:
    assert gate._is_bridge_index_file("bridge/INDEX.md") is True
    assert gate._is_bridge_index_file("E:/GT-KB/bridge/INDEX.md") is True
    assert gate._is_bridge_index_file("E:\\GT-KB\\bridge\\INDEX.md") is True


def test_is_bridge_index_file_rejects_decoys(gate: ModuleType) -> None:
    assert gate._is_bridge_index_file("bridge/gtkb-some-proposal-001.md") is False
    assert gate._is_bridge_index_file("notbridge/INDEX.md") is False
    assert gate._is_bridge_index_file(".claude/hooks/bridge-compliance-gate.py") is False


# --- core regression: bridge/INDEX.md is exempt -----------------------------


@pytest.mark.parametrize("pending_status", ["NEW", "REVISED"])
def test_index_edit_with_pending_proposal_targeting_index_is_exempt(
    gate: ModuleType, tmp_path: Path, pending_status: str
) -> None:
    index = _write_index(
        tmp_path,
        f"Document: sentinel-thread\n{pending_status}: bridge/sentinel-thread-001.md\n",
    )
    _write_proposal(tmp_path, "sentinel-thread-001.md", ["bridge/INDEX.md", "scripts/sentinel.py"])
    # Editing the canonical index while a pending proposal targets it: no ask.
    assert gate._pending_proposal_ask_reason(index, str(index)) is None
    assert gate._pending_proposal_ask_reason(index, "bridge/INDEX.md") is None


# --- the checkpoint still fires for non-INDEX targets -----------------------


def test_non_index_target_still_triggers_ask(gate: ModuleType, tmp_path: Path) -> None:
    index = _write_index(tmp_path, "Document: feature-thread\nNEW: bridge/feature-thread-001.md\n")
    _write_proposal(tmp_path, "feature-thread-001.md", ["scripts/feature.py"])
    reason = gate._pending_proposal_ask_reason(index, "scripts/feature.py")
    assert reason is not None
    assert "pending Codex review" in reason
    assert "feature-thread" in reason


def test_no_go_proposal_non_index_target_triggers_no_go_reason(gate: ModuleType, tmp_path: Path) -> None:
    index = _write_index(
        tmp_path,
        "Document: rejected-thread\nNO-GO: bridge/rejected-thread-002.md\nNEW: bridge/rejected-thread-001.md\n",
    )
    _write_proposal(tmp_path, "rejected-thread-002.md", ["scripts/rejected.py"])
    reason = gate._pending_proposal_ask_reason(index, "scripts/rejected.py")
    assert reason is not None
    assert "NO-GO status" in reason
    assert "rejected-thread" in reason


# --- no false positives -----------------------------------------------------


def test_unmatched_non_index_file_returns_none(gate: ModuleType, tmp_path: Path) -> None:
    index = _write_index(tmp_path, "Document: feature-thread\nNEW: bridge/feature-thread-001.md\n")
    _write_proposal(tmp_path, "feature-thread-001.md", ["scripts/feature.py"])
    assert gate._pending_proposal_ask_reason(index, "scripts/unrelated.py") is None
