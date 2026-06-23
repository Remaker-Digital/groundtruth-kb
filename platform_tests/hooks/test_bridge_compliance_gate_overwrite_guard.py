"""Tests for the bridge-compliance-gate overwrite guard (WI-4740).

The bridge append-only invariant requires that existing numbered bridge files
cannot be overwritten in place.  The guard fires in _deny_reason_for_content()
before the body-status-token check and triggers on both Write (full content)
and Edit (empty content) tool paths when the target versioned bridge file
already exists on disk.

Guard location in hook:
    bridge-compliance-gate.py lines 1407-1417
    Condition: _is_bridge_markdown_file(file_path) and _versioned_bridge_file_exists_on_disk(file_path)
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
ACTIVE_HOOK = REPO_ROOT / ".claude" / "hooks" / "bridge-compliance-gate.py"


def _load_gate():
    """Import the hyphenated hook module by path."""
    spec = importlib.util.spec_from_file_location("bridge_compliance_gate", ACTIVE_HOOK)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_gate = _load_gate()


def _bridge_dir(tmp_path: Path) -> Path:
    """Create and return a tmp bridge directory."""
    d = tmp_path / "bridge"
    d.mkdir(exist_ok=True)
    return d


# ---------------------------------------------------------------------------
# _versioned_bridge_file_exists_on_disk unit behavior
# ---------------------------------------------------------------------------


def test_detects_existing_versioned_bridge_file(tmp_path: Path) -> None:
    """Helper returns True when the versioned bridge file exists on disk."""
    path = _bridge_dir(tmp_path) / "gtkb-demo-001.md"
    path.write_text("GO\n", encoding="utf-8")

    assert _gate._versioned_bridge_file_exists_on_disk(str(path)) is True


def test_absent_versioned_bridge_file_returns_false(tmp_path: Path) -> None:
    """Helper returns False when the versioned bridge file is absent from disk."""
    path = _bridge_dir(tmp_path) / "gtkb-demo-999.md"

    assert _gate._versioned_bridge_file_exists_on_disk(str(path)) is False


def test_index_file_is_not_treated_as_versioned_file(tmp_path: Path) -> None:
    """bridge/INDEX.md is not a versioned bridge file and should not trigger the guard."""
    path = _bridge_dir(tmp_path) / "INDEX.md"
    path.write_text("Document: sample\nNEW: bridge/sample-001.md\n", encoding="utf-8")

    # INDEX.md has no version number suffix, so _is_bridge_markdown_file may exclude it
    # or _versioned_bridge_file_exists_on_disk may return False for it.
    # Either way, the overwrite guard must not block writes to INDEX.md.
    reason = _gate._deny_reason_for_content(
        cwd_path=tmp_path,
        file_path=str(path),
        content="Document: sample\nNEW: bridge/sample-001.md\nGO: bridge/sample-002.md\n",
    )

    assert reason is None or "Bridge append-only boundary violation" not in reason


# ---------------------------------------------------------------------------
# _deny_reason_for_content overwrite guard integration
# ---------------------------------------------------------------------------


def test_write_blocked_when_versioned_file_exists_on_disk(tmp_path: Path) -> None:
    """Writing to an existing versioned bridge file is denied with the append-only error."""
    path = _bridge_dir(tmp_path) / "gtkb-demo-001.md"
    path.write_text("GO\n\n# Existing verdict\n", encoding="utf-8")

    reason = _gate._deny_reason_for_content(
        cwd_path=tmp_path,
        file_path=str(path),
        content="REVISED\n\n# Attempt to overwrite\n",
    )

    assert reason is not None
    assert "Bridge append-only boundary violation" in reason
    assert path.name in reason


def test_overwrite_guard_fires_with_empty_content_edit_path(tmp_path: Path) -> None:
    """Overwrite guard fires even with empty content — the Edit tool passes empty string."""
    path = _bridge_dir(tmp_path) / "gtkb-demo-001.md"
    path.write_text("NEW\n\n# Proposal\n", encoding="utf-8")

    reason = _gate._deny_reason_for_content(
        cwd_path=tmp_path,
        file_path=str(path),
        content="",
    )

    assert reason is not None
    assert "Bridge append-only boundary violation" in reason


def test_fresh_versioned_file_not_blocked_by_overwrite_guard(tmp_path: Path) -> None:
    """Writing a new versioned bridge file (not on disk) is not blocked by the overwrite guard."""
    path = _bridge_dir(tmp_path) / "gtkb-fresh-003.md"
    # File does not exist on disk

    reason = _gate._deny_reason_for_content(
        cwd_path=tmp_path,
        file_path=str(path),
        content="NEW\n\n# Fresh proposal\n",
    )

    assert reason is None or "Bridge append-only boundary violation" not in reason


def test_overwrite_guard_message_includes_next_version_guidance(tmp_path: Path) -> None:
    """Denial message directs caller to write the next numbered version."""
    path = _bridge_dir(tmp_path) / "gtkb-demo-001.md"
    path.write_text("GO\n", encoding="utf-8")

    reason = _gate._deny_reason_for_content(
        cwd_path=tmp_path,
        file_path=str(path),
        content="NEW\n",
    )

    assert reason is not None
    assert "next version" in reason or "NNN" in reason


def test_overwrite_guard_cites_wi4740(tmp_path: Path) -> None:
    """Denial message cites WI-4740 so it is traceable to the originating defect."""
    path = _bridge_dir(tmp_path) / "gtkb-demo-001.md"
    path.write_text("GO\n", encoding="utf-8")

    reason = _gate._deny_reason_for_content(
        cwd_path=tmp_path,
        file_path=str(path),
        content="NEW\n",
    )

    assert reason is not None
    assert "WI-4740" in reason
