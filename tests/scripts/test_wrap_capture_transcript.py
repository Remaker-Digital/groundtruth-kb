"""Tests for scripts/wrap_capture_transcript.py (W0 manifest-only).

Per bridge/gtkb-wrapup-enhancements-slice1-005.md (REVISED-2, GO at -006).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
import wrap_capture_transcript as w0  # noqa: E402


def test_build_manifest_returns_required_fields(tmp_path: Path) -> None:
    """Manifest must contain only the allowed fields (no transcript content)."""
    manifest = w0.build_manifest("S310", tmp_path)
    expected_keys = {
        "manifest_schema_version",
        "session_id",
        "captured_at",
        "git_head",
        "git_branch",
        "uncommitted_paths",
        "untracked_paths",
    }
    assert set(manifest.keys()) == expected_keys, (
        f"Manifest fields must be exactly {expected_keys}; got {set(manifest.keys())}. "
        "Slice 1 is manifest-only — no transcript content is permitted."
    )
    assert manifest["session_id"] == "S310"
    assert manifest["manifest_schema_version"] == w0.MANIFEST_SCHEMA_VERSION


def test_write_manifest_creates_file_atomically(tmp_path: Path) -> None:
    """Manifest file must exist after write_manifest, and be valid JSON."""
    snapshot_root = tmp_path / "snapshots"
    project_root = Path(__file__).resolve().parents[2]
    manifest_path = w0.write_manifest("S999-test", snapshot_root, project_root)
    assert manifest_path.exists()
    assert manifest_path.parent.name == "S999-test"
    parsed = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert parsed["session_id"] == "S999-test"


def test_main_exit_zero_on_success(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Main should exit 0 when manifest writes cleanly."""
    snapshot_root = tmp_path / "snapshots"
    rc = w0.main(["--session-id", "S999-test-main", "--snapshot-root", str(snapshot_root)])
    assert rc == 0
    assert (snapshot_root / "S999-test-main" / "manifest.json").exists()


def test_manifest_contains_no_transcript_content_field(tmp_path: Path) -> None:
    """Defense-in-depth: assert no 'transcript' or 'transcript_content' field exists."""
    manifest = w0.build_manifest("S310", tmp_path)
    forbidden = {"transcript", "transcript_content", "transcript_jsonl", "transcript_path"}
    assert not (set(manifest.keys()) & forbidden), (
        "Slice 1 must not capture transcript content. Future WRAPUP-Slice-2A "
        "will ship transcript handling with redaction + retention + ignore policy."
    )
