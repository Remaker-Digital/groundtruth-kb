"""AXIS 2 work-intent visibility tests."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import SimpleNamespace

PROJECT_ROOT = Path(__file__).resolve().parents[2]
HOOK_PATH = PROJECT_ROOT / ".claude" / "hooks" / "bridge-axis-2-surface.py"

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.bridge_work_intent_registry import acquire  # noqa: E402


def _load_module():
    spec = importlib.util.spec_from_file_location("bridge_axis_2_surface_work_intent", HOOK_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _item(document: str):
    return SimpleNamespace(document_name=document, top_status="GO", top_file=f"bridge/{document}-002.md")


def test_split_work_intent_claims_hides_other_session_holder(tmp_path: Path) -> None:
    mod = _load_module()
    mod.PROJECT_ROOT = tmp_path
    acquire("gtkb-held-thread", "session-a", ttl_seconds=300, project_root=tmp_path)

    available, claimed = mod._split_work_intent_claims(
        [_item("gtkb-held-thread"), _item("gtkb-open-thread")],
        "session-b",
    )

    assert [item.document_name for item in available] == ["gtkb-open-thread"]
    assert claimed[0]["item"].document_name == "gtkb-held-thread"
    assert claimed[0]["holder"]["session_id"] == "session-a"


def test_render_surface_includes_claim_footer_and_claimed_annotation() -> None:
    mod = _load_module()

    rendered = mod._render_surface(
        [_item("gtkb-open-thread")],
        mod.ROLE_PRIME,
        [
            {
                "item": _item("gtkb-held-thread"),
                "holder": {"session_id": "session-a", "ttl_expires_at": "2099-01-01T00:00:00Z"},
            }
        ],
    )

    assert "python scripts/bridge_claim_cli.py claim <slug>" in rendered
    assert "ALREADY CLAIMED" in rendered
    assert "gtkb-held-thread" in rendered
    assert "session-a" in rendered


# ---------------------------------------------------------------------------
# WI-4267: CLAUDE_CODE_SESSION_ID env-var resolution
# (bridge/gtkb-claude-code-session-id-env-var-gap thread)
# ---------------------------------------------------------------------------

_AXIS2_TUPLE_ENV_VARS = (
    "GTKB_BRIDGE_POLLER_RUN_ID",
    "CLAUDE_CODE_SESSION_ID",
    "CLAUDE_SESSION_ID",
    "GTKB_INHERITED_SESSION_ID",
    "CODEX_SESSION_ID",
    "CODEX_THREAD_ID",
    "ANTIGRAVITY_SESSION_ID",
    "GTKB_SESSION_ID",
)


def test_axis2_resolve_work_intent_session_id_uses_claude_code_session_id(monkeypatch) -> None:
    """AXIS 2 surface resolver returns CLAUDE_CODE_SESSION_ID when payload
    carries no session_id and CLAUDE_SESSION_ID is unset."""
    mod = _load_module()
    for name in _AXIS2_TUPLE_ENV_VARS:
        monkeypatch.delenv(name, raising=False)
    monkeypatch.setenv("CLAUDE_CODE_SESSION_ID", "claude-code-session-probe")

    assert mod._resolve_work_intent_session_id({}) == "claude-code-session-probe"


def test_axis2_resolve_work_intent_session_id_prefers_dispatch_run_id(monkeypatch) -> None:
    mod = _load_module()
    for name in _AXIS2_TUPLE_ENV_VARS:
        monkeypatch.delenv(name, raising=False)
    monkeypatch.setenv("GTKB_BRIDGE_POLLER_RUN_ID", "dispatch-run")
    monkeypatch.setenv("CODEX_THREAD_ID", "parent-codex-thread")

    assert mod._resolve_work_intent_session_id({"session_id": "from-payload"}) == "dispatch-run"


def test_axis2_live_claude_code_takes_precedence_over_legacy_claude(monkeypatch) -> None:
    """Live CLAUDE_CODE_SESSION_ID wins when both Claude vars are set."""
    mod = _load_module()
    for name in _AXIS2_TUPLE_ENV_VARS:
        monkeypatch.delenv(name, raising=False)
    monkeypatch.setenv("CLAUDE_SESSION_ID", "explicit-session-override")
    monkeypatch.setenv("CLAUDE_CODE_SESSION_ID", "claude-code-session-probe")

    assert mod._resolve_work_intent_session_id({}) == "claude-code-session-probe"


def test_axis2_work_intent_tuple_orders_claude_code_before_claude_session() -> None:
    """Precedence contract: CLAUDE_CODE_SESSION_ID must immediately precede
    CLAUDE_SESSION_ID in the tuple."""
    mod = _load_module()
    tuple_ = mod.WORK_INTENT_SESSION_ENV_VARS
    assert "CLAUDE_CODE_SESSION_ID" in tuple_
    claude_index = tuple_.index("CLAUDE_SESSION_ID")
    claude_code_index = tuple_.index("CLAUDE_CODE_SESSION_ID")
    assert claude_code_index + 1 == claude_index


def test_axis2_live_env_beats_payload_session_id(monkeypatch) -> None:
    """WI-4377: AXIS 2 work-intent filtering uses live env before payload."""
    mod = _load_module()
    for name in _AXIS2_TUPLE_ENV_VARS:
        monkeypatch.delenv(name, raising=False)
    monkeypatch.setenv("CLAUDE_CODE_SESSION_ID", "from-env")

    assert mod._resolve_work_intent_session_id({"session_id": "from-payload"}) == "from-env"


def test_axis2_payload_session_id_remains_fallback(monkeypatch) -> None:
    """Payload session_id is still used when no live env exists."""
    mod = _load_module()
    for name in _AXIS2_TUPLE_ENV_VARS:
        monkeypatch.delenv(name, raising=False)

    assert mod._resolve_work_intent_session_id({"session_id": "from-payload"}) == "from-payload"


# ---------------------------------------------------------------------------
# WI-4270: shared session-id resolver unification
# (bridge/gtkb-session-id-shared-resolver-unification thread)
# ---------------------------------------------------------------------------


def test_axis2_env_vars_equals_canonical_bridge_order() -> None:
    """WI-4270: the surface's WORK_INTENT_SESSION_ENV_VARS is the shared
    canonical BRIDGE_WORK_INTENT_ORDER (membership de-duplicated)."""
    from scripts.gtkb_session_id import BRIDGE_WORK_INTENT_ORDER

    mod = _load_module()
    assert tuple(mod.WORK_INTENT_SESSION_ENV_VARS) == tuple(BRIDGE_WORK_INTENT_ORDER)


def test_axis2_failsoft_fallback_equals_canonical() -> None:
    """WI-4270: with scripts.gtkb_session_id unavailable (partial install), the
    surface's verbatim local fallback still equals the canonical order."""
    from scripts.gtkb_session_id import BRIDGE_WORK_INTENT_ORDER

    saved = sys.modules.get("scripts.gtkb_session_id")
    sys.modules["scripts.gtkb_session_id"] = None  # force ImportError on the submodule
    try:
        spec = importlib.util.spec_from_file_location("bridge_axis_2_surface_failsoft", HOOK_PATH)
        assert spec is not None and spec.loader is not None
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
    finally:
        if saved is None:
            sys.modules.pop("scripts.gtkb_session_id", None)
        else:
            sys.modules["scripts.gtkb_session_id"] = saved
    assert tuple(mod.WORK_INTENT_SESSION_ENV_VARS) == tuple(BRIDGE_WORK_INTENT_ORDER)
