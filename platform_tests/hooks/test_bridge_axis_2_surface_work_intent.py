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
