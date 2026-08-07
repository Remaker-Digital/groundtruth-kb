"""AXIS 2 surface role-awareness tests (Slice 4).

bridge/gtkb-interactive-session-role-override-slice-4-axis2-role-awareness-001.md
(Codex GO at -002).

Asserts that .claude/hooks/bridge-axis-2-surface.py selects the actionable
element matching the resolved session role (element 0 = Prime, element 1 =
Loyal Opposition per compute_actionable_pending's (prime, codex) contract),
renders a role-aware heading, and keys its signature off the resolved-role
items. Per owner S371 Decision 1 (full session override includes the AXIS 2
surface).
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import ModuleType, SimpleNamespace
from typing import Any

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
_PACKAGE_SRC = REPO_ROOT / "groundtruth-kb" / "src"
if str(_PACKAGE_SRC) not in sys.path:
    sys.path.insert(0, str(_PACKAGE_SRC))

_HOOK_PATH = REPO_ROOT / ".claude" / "hooks" / "bridge-axis-2-surface.py"


def _load_hook() -> ModuleType:
    spec = importlib.util.spec_from_file_location("_test_bridge_axis_2_surface", _HOOK_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class _Item(SimpleNamespace):
    def __init__(self, name: str, status: str, top_file: str) -> None:
        super().__init__(
            document_name=name,
            top_status=status,
            top_file=top_file,
            dispatchable=True,
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, (SimpleNamespace, _Item)):
            return False
        return (
            self.document_name == getattr(other, "document_name", None)
            and self.top_status == getattr(other, "top_status", None)
            and self.top_file == getattr(other, "top_file", None)
        )


_PRIME_ITEMS = [_Item("doc-go", "GO", "bridge/doc-go-002.md")]
_CODEX_ITEMS = [
    _Item("doc-new", "NEW", "bridge/doc-new-001.md"),
    _Item("doc-rev", "REVISED", "bridge/doc-rev-003.md"),
]


@pytest.fixture
def hook(monkeypatch: pytest.MonkeyPatch) -> ModuleType:
    """Load the hook and stub the dynamic scan bridge helper.

    The hook imports scan_bridge helper locally inside _compute_actionable_for_role,
    so monkeypatching _load_scan_bridge_helper is picked up at call time.
    """
    module = _load_hook()

    class MockScanner:
        @staticmethod
        def scan(role: str, *args, **kwargs) -> dict[str, Any]:
            if role == module.ROLE_PRIME:
                return {
                    "actionable": [{"document": "doc-go", "latest_status": "GO", "latest_path": "bridge/doc-go-002.md"}]
                }
            elif role == module.ROLE_LO:
                return {
                    "actionable": [
                        {"document": "doc-new", "latest_status": "NEW", "latest_path": "bridge/doc-new-001.md"},
                        {"document": "doc-rev", "latest_status": "REVISED", "latest_path": "bridge/doc-rev-003.md"},
                    ]
                }
            return {"actionable": []}

    monkeypatch.setattr(module, "_load_scan_bridge_helper", lambda: MockScanner)
    return module


def test_axis2_pb_marker_surfaces_prime(hook: ModuleType) -> None:
    signature, items = hook._compute_actionable_for_role(hook.ROLE_PRIME)
    assert items == _PRIME_ITEMS
    assert signature  # non-empty
    rendered = hook._render_surface(items, hook.ROLE_PRIME)
    assert "Newly-Actionable Prime Work" in rendered


def test_axis2_lo_marker_surfaces_lo(hook: ModuleType) -> None:
    signature, items = hook._compute_actionable_for_role(hook.ROLE_LO)
    assert items == _CODEX_ITEMS
    assert signature
    rendered = hook._render_surface(items, hook.ROLE_LO)
    assert "Newly-Actionable Loyal Opposition Work" in rendered


def test_axis2_signature_role_scoped(hook: ModuleType) -> None:
    """PB and LO signatures differ for the same INDEX (different item sets)."""
    sig_pb, _ = hook._compute_actionable_for_role(hook.ROLE_PRIME)
    sig_lo, _ = hook._compute_actionable_for_role(hook.ROLE_LO)
    assert sig_pb != sig_lo


def test_render_heading_defaults_to_prime(hook: ModuleType) -> None:
    """An unknown role profile renders the Prime heading (safe default)."""
    rendered = hook._render_surface(_PRIME_ITEMS, "unknown-role")
    assert "Newly-Actionable Prime Work" in rendered


def test_resolve_failsoft_uses_resolver_role(hook: ModuleType, monkeypatch: pytest.MonkeyPatch) -> None:
    """_resolve_session_role_failsoft returns the resolver's role on success."""
    import scripts.session_role_resolution as srr

    monkeypatch.setattr(srr, "resolve_interactive_session_role", lambda *a, **k: (srr.ROLE_LO, "marker"))
    assert hook._resolve_session_role_failsoft({"session_id": "sess-1"}) == hook.ROLE_LO


def test_resolve_failsoft_suppresses_on_resolver_error(hook: ModuleType, monkeypatch: pytest.MonkeyPatch) -> None:
    """On any resolver exception the hook suppresses (returns None), not Prime.

    WI-5933 Slice B (C4): surfacing a Prime-filtered actionable list to a
    session whose role is unknown is the mislabelling
    ``DCL-SESSION-ROLE-RESOLUTION-001`` v7 forbids; the caller suppresses the
    surface entirely on ``None``. The hook still fails soft (never crashes).
    """
    import scripts.session_role_resolution as srr

    def _boom(*a: object, **k: object) -> tuple[str, str]:
        raise RuntimeError("resolver unavailable")

    monkeypatch.setattr(srr, "resolve_interactive_session_role", _boom)
    assert hook._resolve_session_role_failsoft({"session_id": "sess-1"}) is None


def test_resolve_failsoft_passes_raw_session_id(hook: ModuleType, monkeypatch: pytest.MonkeyPatch) -> None:
    """The RAW payload session_id (not a sanitized form) is passed to the resolver."""
    import scripts.session_role_resolution as srr

    captured: dict[str, object] = {}

    def _capture(project_root: object, *, current_session_id: object = None, harness_name: object = "claude"):
        captured["sid"] = current_session_id
        return (srr.ROLE_PRIME, "durable_marker_absent")

    monkeypatch.setattr(srr, "resolve_interactive_session_role", _capture)
    # A raw id with characters the cache-key sanitizer would strip; the resolver
    # must receive it verbatim so its comparison matches the Slice 2 writer.
    hook._resolve_session_role_failsoft({"session_id": "abc/DEF:123"})
    assert captured["sid"] == "abc/DEF:123"
