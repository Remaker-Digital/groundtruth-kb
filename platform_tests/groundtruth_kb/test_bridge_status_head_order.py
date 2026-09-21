"""Current authored heads and grandfathered file reads preserve status order independence."""

from __future__ import annotations

from itertools import permutations
from pathlib import Path

import pytest
from groundtruth_kb.bridge.native import parse_authored_message
from groundtruth_kb.bridge.versioned_files import status_from_bridge_file

from platform_tests.groundtruth_kb.bridge_fixtures import authored

MARKER_INIT = "::init gtkb lo"
MARKER_OPEN = "::open build"
BODY = "\nbridge_kind: implementation_proposal\nDocument: probe\nVersion: 001\n"


def _write(tmp_path: Path, slug: str, head_lines: list[str]) -> Path:
    bridge = tmp_path / "bridge"
    bridge.mkdir(exist_ok=True)
    path = bridge / f"{slug}-001.md"
    path.write_text("\n".join(head_lines) + BODY, encoding="utf-8")
    return path


@pytest.mark.parametrize(
    ("label", "head"),
    [
        ("status-first", ["GO", MARKER_INIT, MARKER_OPEN]),
        ("init-first", [MARKER_INIT, MARKER_OPEN, "GO"]),
        ("open-first", [MARKER_OPEN, MARKER_INIT, "GO"]),
        ("status-middle", [MARKER_INIT, "GO", MARKER_OPEN]),
    ],
)
def test_status_is_order_independent(tmp_path: Path, label: str, head: list[str]) -> None:
    """All four complete-head orderings resolve to the same status."""
    path = _write(tmp_path, f"probe-{label}", head)
    assert status_from_bridge_file(path) == "GO", f"{label} head did not resolve to GO"


@pytest.mark.parametrize("marker", [MARKER_INIT, MARKER_OPEN])
def test_a_marker_is_never_returned_as_a_status(tmp_path: Path, marker: str) -> None:
    """The regression that made a live GO invisible.

    Taking the first non-blank line returned the marker itself as the status.
    """
    path = _write(tmp_path, "probe-marker", [marker, MARKER_OPEN if marker == MARKER_INIT else MARKER_INIT, "GO"])
    resolved = status_from_bridge_file(path)
    assert resolved != marker
    assert not str(resolved).startswith("::"), f"marker leaked as status: {resolved!r}"


def test_line_one_heads_are_unaffected(tmp_path: Path) -> None:
    """Regression floor: the previously-working form still works."""
    for token in ("GO", "NEW", "REVISED", "NO-GO"):
        path = _write(tmp_path, f"probe-line1-{token.lower()}", [token, MARKER_INIT, MARKER_OPEN])
        assert status_from_bridge_file(path) == token


@pytest.mark.parametrize("status", ["NEW", "REVISED", "GO", "NO-GO", "READY", "NOT-READY", "VERDICT-REJECTED"])
def test_native_complete_heads_are_order_independent(status):
    content = authored({"session_context_id": "context-for-header-validation"}, "order-independent", 1, status)
    lines = content.splitlines()
    for head in permutations(lines[:3]):
        reordered = "\r\n".join([*head, *lines[3:]])
        result = parse_authored_message(reordered)
        assert result["status"] == status
        assert result["metadata"]["document"] == "order-independent"
