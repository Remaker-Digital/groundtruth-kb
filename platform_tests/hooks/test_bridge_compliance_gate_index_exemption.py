"""Regression tests for retired bridge aggregate handling and pending scans.

The post-TAFE bridge model treats bridge/INDEX.md as a retired aggregate file,
not as writable queue authority. The pending-proposal checkpoint now derives
latest status from versioned bridge files directly and caches target-path
decisions under .gtkb-state to avoid scanning the whole bridge directory on
every non-bridge Write/Edit.
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


def _write_bridge_file(tmp_path: Path, filename: str, status: str, target_paths: list[str] | None = None) -> Path:
    """Create a fixture versioned bridge file under tmp_path."""
    bridge_dir = tmp_path / "bridge"
    bridge_dir.mkdir(parents=True, exist_ok=True)
    body = f"{status}\n\n# Fixture proposal\n"
    if target_paths is not None:
        body += f"\ntarget_paths: {json.dumps(target_paths)}\n"
    path = bridge_dir / filename
    path.write_text(body, encoding="utf-8")
    return path


def _cache_path(gate: ModuleType, tmp_path: Path) -> Path:
    return gate._pending_target_cache_path(tmp_path)


# --- retired aggregate handling --------------------------------------------


def test_retired_bridge_aggregate_file_recognizes_index(gate: ModuleType) -> None:
    assert gate._is_retired_bridge_aggregate_file("bridge/INDEX.md") is True
    assert gate._is_retired_bridge_aggregate_file("E:/GT-KB/bridge/INDEX.md") is True
    assert gate._is_retired_bridge_aggregate_file("E:\\GT-KB\\bridge\\INDEX.md") is True


def test_retired_bridge_aggregate_file_rejects_decoys(gate: ModuleType) -> None:
    assert gate._is_retired_bridge_aggregate_file("bridge/gtkb-some-proposal-001.md") is False
    assert gate._is_retired_bridge_aggregate_file("notbridge/INDEX.md") is False
    assert gate._is_retired_bridge_aggregate_file(".claude/hooks/bridge-compliance-gate.py") is False


def test_retired_bridge_aggregate_file_is_denied(gate: ModuleType, tmp_path: Path) -> None:
    reason = gate._deny_reason_for_content(
        cwd_path=tmp_path,
        file_path="bridge/INDEX.md",
        content="Document: legacy\nNEW: bridge/legacy-001.md\n",
    )
    assert reason is not None
    assert "Retired bridge aggregate files" in reason


def test_versioned_bridge_file_gets_normal_proposal_governance_denial(gate: ModuleType, tmp_path: Path) -> None:
    reason = gate._deny_reason_for_content(
        cwd_path=tmp_path,
        file_path="bridge/example-thread-001.md",
        content="NEW\n\n# Example proposal\n",
    )
    assert reason is not None
    assert "Specification Links" in reason
    assert "Retired bridge aggregate files" not in reason


# --- pending target-path checkpoint -----------------------------------------


@pytest.mark.parametrize(
    ("status", "expected_fragment"),
    [
        ("NEW", "pending Codex review"),
        ("REVISED", "pending Codex review"),
    ],
)
def test_pending_proposal_target_triggers_review_ask(
    gate: ModuleType, tmp_path: Path, status: str, expected_fragment: str
) -> None:
    _write_bridge_file(tmp_path, "feature-thread-001.md", status, ["scripts/feature.py"])
    reason = gate._pending_proposal_ask_reason(tmp_path, "scripts/feature.py")
    assert reason is not None
    assert expected_fragment in reason
    assert status in reason
    assert "feature-thread" in reason


def test_no_go_proposal_non_index_target_triggers_no_go_reason(gate: ModuleType, tmp_path: Path) -> None:
    _write_bridge_file(tmp_path, "rejected-thread-001.md", "NEW", ["scripts/rejected.py"])
    _write_bridge_file(tmp_path, "rejected-thread-002.md", "NO-GO")
    reason = gate._pending_proposal_ask_reason(tmp_path, "scripts/rejected.py")
    assert reason is not None
    assert "NO-GO status" in reason
    assert "rejected-thread" in reason


# --- no false positives -----------------------------------------------------


def test_unmatched_non_index_file_returns_none(gate: ModuleType, tmp_path: Path) -> None:
    _write_bridge_file(tmp_path, "feature-thread-001.md", "NEW", ["scripts/feature.py"])
    assert gate._pending_proposal_ask_reason(tmp_path, "scripts/unrelated.py") is None


def test_pending_target_cache_hit_preserves_decisions(
    gate: ModuleType, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _write_bridge_file(tmp_path, "new-thread-001.md", "NEW", ["scripts/new.py"])
    _write_bridge_file(tmp_path, "revised-thread-001.md", "NEW", ["scripts/revised.py"])
    _write_bridge_file(tmp_path, "revised-thread-002.md", "REVISED", ["scripts/revised.py"])
    _write_bridge_file(tmp_path, "rejected-thread-001.md", "NEW", ["scripts/rejected.py"])
    _write_bridge_file(tmp_path, "rejected-thread-002.md", "NO-GO")

    expected = {
        "scripts/new.py": gate._pending_proposal_ask_reason(tmp_path, "scripts/new.py"),
        "scripts/revised.py": gate._pending_proposal_ask_reason(tmp_path, "scripts/revised.py"),
        "scripts/rejected.py": gate._pending_proposal_ask_reason(tmp_path, "scripts/rejected.py"),
        "scripts/unmatched.py": gate._pending_proposal_ask_reason(tmp_path, "scripts/unmatched.py"),
    }
    assert _cache_path(gate, tmp_path).is_file()

    def fail_build(_project_root: Path) -> list[dict[str, object]]:
        raise AssertionError("cache hit should not rescan bridge files")

    monkeypatch.setattr(gate, "_build_pending_proposal_targets", fail_build)
    observed = {path: gate._pending_proposal_ask_reason(tmp_path, path) for path in expected}
    assert observed == expected


def test_pending_target_cache_miss_rebuilds(gate: ModuleType, tmp_path: Path) -> None:
    _write_bridge_file(tmp_path, "feature-thread-001.md", "NEW", ["scripts/feature.py"])
    _cache_path(gate, tmp_path).parent.mkdir(parents=True, exist_ok=True)
    _cache_path(gate, tmp_path).write_text(
        json.dumps(
            {
                "schema_version": gate.PENDING_TARGET_CACHE_SCHEMA_VERSION,
                "bridge_signature": {"file_count": -1, "max_mtime_ns": -1},
                "records": [],
            }
        ),
        encoding="utf-8",
    )

    reason = gate._pending_proposal_ask_reason(tmp_path, "scripts/feature.py")
    assert reason is not None
    assert "pending Codex review" in reason
