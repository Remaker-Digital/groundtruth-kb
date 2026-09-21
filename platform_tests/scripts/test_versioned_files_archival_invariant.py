from __future__ import annotations

from pathlib import Path

import pytest
from groundtruth_kb.bridge.versioned_files import parse_bridge_header_block, status_from_bridge_file
from groundtruth_kb.bridge.vocabulary import CANONICAL_STATUSES, HISTORICAL_INERT_STATUSES


def _write_bridge_file(project_root: Path, filename: str, text: str) -> Path:
    path = project_root / "bridge" / filename
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def test_canonical_nonterminal_status_remains_live_even_with_later_terminal_text(tmp_path: Path) -> None:
    path = _write_bridge_file(
        tmp_path,
        "live-go-001.md",
        "GO\n\n## Prior status\n\nVERIFIED was discussed in historical context.\n",
    )
    assert status_from_bridge_file(path) == "GO"


def test_terminal_first_line_status_is_read(tmp_path: Path) -> None:
    path = _write_bridge_file(tmp_path, "finished-001.md", "VERIFIED\n\nImplementation accepted.\n")
    assert status_from_bridge_file(path) == "VERIFIED"


@pytest.mark.parametrize("status", sorted(CANONICAL_STATUSES | HISTORICAL_INERT_STATUSES))
@pytest.mark.parametrize("decoration", ["", "## ", "**"])
def test_reader_preserves_status_spelling_and_never_selects_later_body_status(tmp_path, status, decoration) -> None:
    text = f"{decoration}{status}\nDocument: example\nGO\nVERDICT-REJECTED\n"
    path = _write_bridge_file(tmp_path, "example-001.md", text)
    original = path.read_bytes()
    header = parse_bridge_header_block(text)
    assert header.status == status
    assert header.status_line == f"{decoration}{status}"
    assert header.status_line_exact is (not decoration)
    assert status_from_bridge_file(path) == status
    assert path.read_bytes() == original
