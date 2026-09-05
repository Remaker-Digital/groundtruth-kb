"""Bridge status resolution is independent of artifact-head line order (WI-7672).

``file-bridge-protocol.md`` section "Complete authored heads are order-independent
at the writer" (WI-6538) states that a head carrying a canonical status token, one
``::init gtkb`` line and one ``::open`` line within the first three non-blank lines
is COMPLETE and correct in **any** order.

``proposal_filing`` previously resolved status by taking the first non-blank line,
so a head in the order-independent form reported ``'::init gtkb pb'`` as its status
and a live ``GO`` was invisible. WI-6541 had already repaired this exact defect in
``bridge/read_commands.py`` and did not reach this reader.

The repair reuses ``bridge.versioned_files.status_from_bridge_file``, the canonical
reader already used by ``read_commands``, ``versioned_files`` and
``git_lifecycle.service``.

Authority: ``GOV-FILE-BRIDGE-AUTHORITY-001``;
``DCL-BRIDGE-ENVELOPE-LINE-AUTHORING-PLACEMENT-001``;
``ADR-BRIDGE-ARTIFACT-HEAD-ENVELOPE-001``; ``GOV-SOT-SINGLETON-001``.
Bridge thread ``gtkb-wi7672-bridge-status-reader-head-order``.
"""

from __future__ import annotations

import inspect
from pathlib import Path

import pytest
from groundtruth_kb.bridge import proposal_filing
from groundtruth_kb.bridge.versioned_files import status_from_bridge_file

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


def test_proposal_filing_holds_no_independent_status_read() -> None:
    """GOV-SOT-SINGLETON-001: one canonical implementation, not two.

    The defect was a private first-non-blank-line expression. Assert the module
    delegates to the canonical reader instead of re-deriving status itself.
    """
    source = inspect.getsource(proposal_filing)
    assert "status_from_bridge_file" in source, "module no longer delegates to the canonical reader"
    assert 'if line.strip()), ""' not in source, (
        "a first-non-blank-line status expression is present again; bridge status must be "
        "read via status_from_bridge_file so head order does not change the answer"
    )


def test_canonical_reader_agrees_with_proposal_filing_on_a_real_thread() -> None:
    """End-to-end: the reader and the consumer report the same status.

    Uses the live repository rather than a fixture so the assertion covers the
    actual call path that refused a GO'd PostgreSQL thread.
    """
    repo_root = Path(__file__).resolve().parents[2]
    slug = "gtkb-wi7672-bridge-status-reader-head-order"
    latest = sorted((repo_root / "bridge").glob(f"{slug}-[0-9]*.md"))
    if not latest:
        pytest.skip(f"no numbered files for {slug} in this checkout")
    direct = status_from_bridge_file(latest[-1])
    via_consumer = proposal_filing._bridge_invalidation_inputs(repo_root, slug)["latest_bridge_status"]
    assert via_consumer == direct, f"consumer {via_consumer!r} disagrees with canonical reader {direct!r}"
