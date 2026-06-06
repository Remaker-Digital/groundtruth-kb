"""Focused tests for bridge-propose helper work-intent integration."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import ModuleType
from typing import Any

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
HELPER_PATH = REPO_ROOT / ".claude" / "skills" / "bridge-propose" / "helpers" / "write_bridge.py"
SCRIPTS_DIR = REPO_ROOT / "scripts"
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import bridge_work_intent_registry as registry  # noqa: E402


def _load_helper() -> ModuleType:
    module_name = "platform_test_bridge_propose_helper_work_intent"
    cached = sys.modules.get(module_name)
    if cached is not None:
        return cached
    spec = importlib.util.spec_from_file_location(module_name, HELPER_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def _write_fresh_index(bridge_dir: Path) -> None:
    bridge_dir.mkdir(parents=True, exist_ok=True)
    (bridge_dir / "INDEX.md").write_text("# Bridge Index\n\n<!-- entries -->\n\n", encoding="utf-8")


def _proposal_body(text: str = "Clean bridge body.") -> str:
    return "\n".join(
        [
            "# Test Bridge Proposal",
            "",
            "## Summary",
            "",
            text,
            "",
            "## Specification Links",
            "",
            "- `GOV-FILE-BRIDGE-AUTHORITY-001`",
            "",
            "## Prior Deliberations",
            "",
            "_No prior deliberations: focused helper test._",
            "",
        ]
    )


def test_resolve_work_intent_session_id_precedence() -> None:
    helper = _load_helper()

    env = {
        "GTKB_BRIDGE_POLLER_RUN_ID": "dispatch-session",
        "CLAUDE_SESSION_ID": " claude-session ",
        "CLAUDE_CODE_SESSION_ID": "claude-code-session",
        "GTKB_INHERITED_SESSION_ID": "inherited-session",
        "CODEX_SESSION_ID": "codex-session",
        "CODEX_THREAD_ID": "codex-thread",
        "ANTIGRAVITY_SESSION_ID": "antigravity-session",
        "GTKB_SESSION_ID": "gtkb-session",
    }
    assert helper.resolve_work_intent_session_id(env) == "dispatch-session"

    env.pop("GTKB_BRIDGE_POLLER_RUN_ID")
    assert helper.resolve_work_intent_session_id(env) == "claude-code-session"

    env.pop("CLAUDE_CODE_SESSION_ID")
    assert helper.resolve_work_intent_session_id(env) == "claude-session"

    env.pop("CLAUDE_SESSION_ID")
    assert helper.resolve_work_intent_session_id(env) == "inherited-session"

    env.pop("GTKB_INHERITED_SESSION_ID")
    assert helper.resolve_work_intent_session_id(env) == "codex-session"

    env.pop("CODEX_SESSION_ID")
    assert helper.resolve_work_intent_session_id(env) == "codex-thread"

    env.pop("CODEX_THREAD_ID")
    assert helper.resolve_work_intent_session_id(env) == "antigravity-session"

    env.pop("ANTIGRAVITY_SESSION_ID")
    assert helper.resolve_work_intent_session_id(env) == "gtkb-session"

    with pytest.raises(helper.BridgeWorkIntentError, match="session id required"):
        helper.resolve_work_intent_session_id({})


def test_propose_bridge_acquires_with_ttl_300_and_releases_after_success(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    helper = _load_helper()
    bridge_dir = tmp_path / "bridge"
    _write_fresh_index(bridge_dir)

    class _RecordingRegistry:
        def __init__(self) -> None:
            self.events: list[tuple[Any, ...]] = []

        def current_holder(self, thread_slug: str, *, project_root: Path) -> None:
            self.events.append(("current_holder", thread_slug, project_root))
            return None

        def acquire(self, thread_slug: str, session_id: str, ttl_seconds: int, *, project_root: Path) -> bool:
            self.events.append(("acquire", thread_slug, session_id, ttl_seconds, project_root))
            return True

        def release(self, thread_slug: str, session_id: str, *, project_root: Path) -> None:
            self.events.append(("release", thread_slug, session_id, project_root))

    fake_registry = _RecordingRegistry()
    monkeypatch.setenv("CLAUDE_SESSION_ID", "session-a")
    monkeypatch.setattr(helper, "_load_work_intent_registry", lambda project_root: fake_registry)

    result = helper.propose_bridge(
        "ttl-topic",
        _proposal_body(),
        bridge_dir=bridge_dir,
        pre_populate_prior_deliberations=False,
    )

    assert result.exists()
    assert fake_registry.events == [
        ("current_holder", "ttl-topic", tmp_path.resolve()),
        ("acquire", "ttl-topic", "session-a", 300, tmp_path.resolve()),
        ("release", "ttl-topic", "session-a", tmp_path.resolve()),
    ]


def test_propose_bridge_blocks_when_thread_held_by_other_session(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    helper = _load_helper()
    bridge_dir = tmp_path / "bridge"
    _write_fresh_index(bridge_dir)
    original_index = (bridge_dir / "INDEX.md").read_text(encoding="utf-8")

    assert registry.acquire("held-topic", "session-a", ttl_seconds=300, project_root=tmp_path)
    monkeypatch.setenv("CLAUDE_SESSION_ID", "session-b")

    with pytest.raises(helper.BridgeWorkIntentError) as excinfo:
        helper.propose_bridge(
            "held-topic",
            _proposal_body("This write must be blocked."),
            bridge_dir=bridge_dir,
            pre_populate_prior_deliberations=False,
        )

    message = str(excinfo.value)
    assert "held-topic" in message
    assert "session-a" in message
    assert not (bridge_dir / "held-topic-001.md").exists()
    assert (bridge_dir / "INDEX.md").read_text(encoding="utf-8") == original_index
    assert registry.current_holder("held-topic", project_root=tmp_path)["session_id"] == "session-a"


def test_propose_bridge_does_not_release_when_index_update_fails(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    helper = _load_helper()
    bridge_dir = tmp_path / "bridge"
    _write_fresh_index(bridge_dir)
    monkeypatch.setenv("CLAUDE_SESSION_ID", "session-c")

    def _always_conflicts(index_path: Path, new_entry: str, *, topic_slug: str) -> None:  # noqa: ARG001
        raise helper.BridgeIndexConflictError("simulated INDEX conflict")

    monkeypatch.setattr(helper, "_update_bridge_index", _always_conflicts)

    with pytest.raises(helper.BridgeIndexConflictError, match="2 total attempts"):
        helper.propose_bridge(
            "conflict-topic",
            _proposal_body("File write succeeds, INDEX update fails."),
            bridge_dir=bridge_dir,
            pre_populate_prior_deliberations=False,
        )

    assert (bridge_dir / "conflict-topic-001.md").exists()
    holder = registry.current_holder("conflict-topic", project_root=tmp_path)
    assert holder is not None
    assert holder["session_id"] == "session-c"


# ---------------------------------------------------------------------------
# WI-4270: shared session-id resolver unification
# (bridge/gtkb-session-id-shared-resolver-unification thread)
# ---------------------------------------------------------------------------


def test_helper_env_vars_equals_canonical_bridge_order() -> None:
    """WI-4270: the helper's WORK_INTENT_SESSION_ENV_VARS is the shared
    canonical BRIDGE_WORK_INTENT_ORDER (membership de-duplicated)."""
    from scripts.gtkb_session_id import BRIDGE_WORK_INTENT_ORDER

    helper = _load_helper()
    assert tuple(helper.WORK_INTENT_SESSION_ENV_VARS) == tuple(BRIDGE_WORK_INTENT_ORDER)


def test_helper_failsoft_fallback_equals_canonical() -> None:
    """WI-4270: with scripts.gtkb_session_id unavailable (partial install), the
    helper's verbatim local fallback still equals the canonical order."""
    import importlib.util

    from scripts.gtkb_session_id import BRIDGE_WORK_INTENT_ORDER

    saved = sys.modules.get("scripts.gtkb_session_id")
    sys.modules["scripts.gtkb_session_id"] = None  # force ImportError on the submodule
    try:
        spec = importlib.util.spec_from_file_location("bridge_propose_helper_failsoft", HELPER_PATH)
        assert spec is not None and spec.loader is not None
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
    finally:
        if saved is None:
            sys.modules.pop("scripts.gtkb_session_id", None)
        else:
            sys.modules["scripts.gtkb_session_id"] = saved
    assert tuple(mod.WORK_INTENT_SESSION_ENV_VARS) == tuple(BRIDGE_WORK_INTENT_ORDER)
