from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
GTKB_SRC = REPO_ROOT / "groundtruth-kb" / "src"
if str(GTKB_SRC) not in sys.path:
    sys.path.insert(0, str(GTKB_SRC))

from groundtruth_kb.bridge.versioned_files import (  # noqa: E402
    candidate_is_archived,
    load_acknowledged_archived_slugs,
    scan_expected_documents,
)


def _write_bridge_file(project_root: Path, filename: str, text: str) -> None:
    bridge_dir = project_root / "bridge"
    bridge_dir.mkdir(parents=True, exist_ok=True)
    (bridge_dir / filename).write_text(text, encoding="utf-8")


def _is_archived(project_root: Path, slug: str) -> bool:
    return candidate_is_archived(
        slug,
        scan_expected_documents(project_root),
        load_acknowledged_archived_slugs(project_root),
        project_root,
    )


def test_malformed_lead_in_with_later_terminal_status_is_not_archived(tmp_path: Path) -> None:
    _write_bridge_file(
        tmp_path,
        "stranded-go-001.md",
        "## Implementation Report\n\nVERIFIED\n\nThis later token is not the status line.\n",
    )

    assert _is_archived(tmp_path, "stranded-go") is False


def test_canonical_nonterminal_status_remains_live_even_with_later_terminal_text(tmp_path: Path) -> None:
    _write_bridge_file(
        tmp_path,
        "live-go-001.md",
        "GO\n\n## Prior status\n\nVERIFIED was discussed in historical context.\n",
    )

    assert _is_archived(tmp_path, "live-go") is False


def test_terminal_first_line_status_is_archived(tmp_path: Path) -> None:
    _write_bridge_file(tmp_path, "finished-001.md", "VERIFIED\n\nImplementation accepted.\n")

    assert _is_archived(tmp_path, "finished") is True


def test_owner_acknowledged_malformed_candidate_is_archived(tmp_path: Path) -> None:
    config_dir = tmp_path / "config" / "governance"
    config_dir.mkdir(parents=True)
    (config_dir / "tafe-acknowledged-archived-bridges.toml").write_text(
        """
[[acknowledged]]
slug = "acknowledged-malformed"
""".lstrip(),
        encoding="utf-8",
    )
    _write_bridge_file(
        tmp_path,
        "acknowledged-malformed-001.md",
        "Implementation report without status\n\nVERIFIED\n",
    )

    assert _is_archived(tmp_path, "acknowledged-malformed") is True


def test_terminal_implementation_sibling_archives_source_thread(tmp_path: Path) -> None:
    _write_bridge_file(tmp_path, "source-thread-001.md", "GO\n\nApproved work remains live.\n")
    _write_bridge_file(
        tmp_path,
        "source-thread-implementation-001.md",
        "VERIFIED\n\nImplementation sibling closed this thread.\n",
    )

    assert _is_archived(tmp_path, "source-thread") is True
