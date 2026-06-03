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
    "CLAUDE_SESSION_ID",
    "CLAUDE_CODE_SESSION_ID",
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


def test_axis2_claude_session_id_takes_precedence_over_claude_code(monkeypatch) -> None:
    """Explicit CLAUDE_SESSION_ID still wins when both are set."""
    mod = _load_module()
    for name in _AXIS2_TUPLE_ENV_VARS:
        monkeypatch.delenv(name, raising=False)
    monkeypatch.setenv("CLAUDE_SESSION_ID", "explicit-session-override")
    monkeypatch.setenv("CLAUDE_CODE_SESSION_ID", "claude-code-session-probe")

    assert mod._resolve_work_intent_session_id({}) == "explicit-session-override"


def test_axis2_work_intent_tuple_orders_claude_code_after_claude_session() -> None:
    """Precedence contract: CLAUDE_CODE_SESSION_ID must immediately follow
    CLAUDE_SESSION_ID in the tuple."""
    mod = _load_module()
    tuple_ = mod.WORK_INTENT_SESSION_ENV_VARS
    assert "CLAUDE_CODE_SESSION_ID" in tuple_
    claude_index = tuple_.index("CLAUDE_SESSION_ID")
    claude_code_index = tuple_.index("CLAUDE_CODE_SESSION_ID")
    assert claude_code_index == claude_index + 1
