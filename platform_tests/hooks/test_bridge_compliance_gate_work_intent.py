"""Bridge-compliance gate tests for work-intent claim enforcement."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import ModuleType

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
LIVE_HOOK = PROJECT_ROOT / ".claude" / "hooks" / "bridge-compliance-gate.py"
TEMPLATE_HOOK = PROJECT_ROOT / "groundtruth-kb" / "templates" / "hooks" / "bridge-compliance-gate.py"

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.bridge_work_intent_registry import acquire  # noqa: E402


def _load_gate(path: Path, name: str) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(params=((LIVE_HOOK, "live"), (TEMPLATE_HOOK, "template")))
def gate(request: pytest.FixtureRequest) -> ModuleType:
    path, name = request.param
    return _load_gate(path, f"bridge_compliance_gate_work_intent_{name}")


def _seed_project(tmp_path: Path) -> None:
    (tmp_path / "groundtruth.toml").write_text('[project]\nname = "test"\nroot = "."\n', encoding="utf-8")
    (tmp_path / "bridge").mkdir(parents=True, exist_ok=True)


def test_no_claim_blocks_versioned_bridge_write(gate: ModuleType, tmp_path: Path) -> None:
    _seed_project(tmp_path)

    reason = gate._bridge_work_intent_deny_reason(
        cwd_path=tmp_path,
        file_path=str(tmp_path / "bridge" / "gtkb-demo-thread-001.md"),
        payload={"session_id": "session-a"},
    )

    assert reason is not None
    assert "no prior claim" in reason
    assert "gtkb-demo-thread" in reason


def test_other_session_claim_blocks_write(gate: ModuleType, tmp_path: Path) -> None:
    _seed_project(tmp_path)
    acquire("gtkb-demo-thread", "session-a", ttl_seconds=300, project_root=tmp_path)

    reason = gate._bridge_work_intent_deny_reason(
        cwd_path=tmp_path,
        file_path=str(tmp_path / "bridge" / "gtkb-demo-thread-001.md"),
        payload={"session_id": "session-b"},
    )

    assert reason is not None
    assert "claimed by session-a" in reason


def test_matching_session_claim_allows_write(gate: ModuleType, tmp_path: Path) -> None:
    _seed_project(tmp_path)
    acquire("gtkb-demo-thread", "session-a", ttl_seconds=300, project_root=tmp_path)

    reason = gate._bridge_work_intent_deny_reason(
        cwd_path=tmp_path,
        file_path=str(tmp_path / "bridge" / "gtkb-demo-thread-001.md"),
        payload={"session_id": "session-a"},
    )

    assert reason is None


# ---------------------------------------------------------------------------
# WI-4267: CLAUDE_CODE_SESSION_ID env-var resolution
# (bridge/gtkb-claude-code-session-id-env-var-gap thread)
# ---------------------------------------------------------------------------

_WORK_INTENT_TUPLE_ENV_VARS = (
    "CLAUDE_SESSION_ID",
    "CLAUDE_CODE_SESSION_ID",
    "GTKB_INHERITED_SESSION_ID",
    "CODEX_SESSION_ID",
    "CODEX_THREAD_ID",
    "ANTIGRAVITY_SESSION_ID",
    "GTKB_SESSION_ID",
)


def _clear_session_env(monkeypatch: pytest.MonkeyPatch) -> None:
    for name in _WORK_INTENT_TUPLE_ENV_VARS:
        monkeypatch.delenv(name, raising=False)


def test_resolve_work_intent_session_id_uses_claude_code_session_id(
    gate: ModuleType, monkeypatch: pytest.MonkeyPatch
) -> None:
    """When only CLAUDE_CODE_SESSION_ID is set (the Claude Code harness's
    actual session-id env var), the resolver returns it."""
    _clear_session_env(monkeypatch)
    monkeypatch.setenv("CLAUDE_CODE_SESSION_ID", "claude-code-session-probe")

    assert gate._resolve_work_intent_session_id({}) == "claude-code-session-probe"


def test_resolve_work_intent_session_id_claude_session_id_takes_precedence(
    gate: ModuleType, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Explicit CLAUDE_SESSION_ID overrides CLAUDE_CODE_SESSION_ID. This
    preserves the documented operator workaround for forcing a particular
    session-id value."""
    _clear_session_env(monkeypatch)
    monkeypatch.setenv("CLAUDE_SESSION_ID", "explicit-session-override")
    monkeypatch.setenv("CLAUDE_CODE_SESSION_ID", "claude-code-session-probe")

    assert gate._resolve_work_intent_session_id({}) == "explicit-session-override"


def test_work_intent_tuple_orders_claude_code_after_claude_session(gate: ModuleType) -> None:
    """The tuple ordering is the precedence contract; CLAUDE_CODE_SESSION_ID
    must come immediately after CLAUDE_SESSION_ID so the precedence above is
    a static property of the tuple, not a runtime accident."""
    tuple_ = gate.WORK_INTENT_SESSION_ENV_VARS
    assert "CLAUDE_CODE_SESSION_ID" in tuple_
    claude_index = tuple_.index("CLAUDE_SESSION_ID")
    claude_code_index = tuple_.index("CLAUDE_CODE_SESSION_ID")
    assert claude_code_index == claude_index + 1, "CLAUDE_CODE_SESSION_ID must immediately follow CLAUDE_SESSION_ID"


def test_non_versioned_bridge_file_skips_claim_gate(gate: ModuleType, tmp_path: Path) -> None:
    _seed_project(tmp_path)

    reason = gate._bridge_work_intent_deny_reason(
        cwd_path=tmp_path,
        file_path=str(tmp_path / "bridge" / "INDEX.md"),
        payload={"session_id": "session-a"},
    )

    assert reason is None
