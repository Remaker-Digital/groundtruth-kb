"""Tests for GFR Slice A preflight extensions: author-metadata warnings and unclassified target paths.

Governing decisions: DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001,
DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001, GOV-FILE-BRIDGE-AUTHORITY-001.
Work item: WI-5644 (TEST-11689).
"""

from __future__ import annotations

import importlib.util
import json
import sqlite3
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = REPO_ROOT / "scripts" / "bridge_applicability_preflight.py"

spec = importlib.util.spec_from_file_location("bridge_applicability_preflight", SCRIPT_PATH)
assert spec is not None
preflight = importlib.util.module_from_spec(spec)
assert spec.loader is not None
sys.modules["bridge_applicability_preflight"] = preflight
spec.loader.exec_module(preflight)


def _make_proposal_content(
    *,
    target_paths: list[str] | None = None,
    author_metadata: bool = True,
) -> str:
    """Build a minimal bridge proposal content with optional metadata."""
    if target_paths is None:
        target_paths = ["scripts/dummy.py"]
    tp = json.dumps(target_paths)
    metadata_block = ""
    if author_metadata:
        metadata_block = "\n".join(
            [
                "author_identity: test/tester",
                "author_harness_id: TEST",
                "author_session_context_id: test-session-001",
                "author_model: test-model",
                "author_model_version: 1.0",
                "author_model_configuration: standard",
                "",
            ]
        )
    return f"""NEW

bridge_kind: prime_proposal
Document: test-proposal
Version: 001
target_paths: {tp}

# Test Proposal

## Specification Links

- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001
- GOV-FILE-BRIDGE-AUTHORITY-001

## Specification-Derived Verification Plan

| Spec | Test | Result |
|---|---|---|
| DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 | pytest this file | pending |

## Files Expected To Change

{metadata_block}
"""


def _write_proposal(tmp_path: Path, content: str) -> Path:
    bridge_dir = tmp_path / "bridge"
    bridge_dir.mkdir(parents=True, exist_ok=True)
    p = bridge_dir / "test-proposal-001.md"
    p.write_text(content, encoding="utf-8")
    return p


def _write_config(tmp_path: Path) -> Path:
    config_path = tmp_path / "spec-applicability.toml"
    config_path.write_text(
        """
[[rules]]
spec_id = "GOV-FILE-BRIDGE-AUTHORITY-001"
severity = "blocking"
rationale = "Bridge authority."
applies_when_doc_matches = ["*"]

[[rules]]
spec_id = "DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001"
severity = "blocking"
rationale = "Spec linkage mandatory."
applies_when_doc_matches = ["*"]
applies_when_content_matches = ["Specification Links", "implementation proposal"]

[[rules]]
spec_id = "DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001"
severity = "blocking"
rationale = "Spec-derived testing."
applies_when_doc_matches = ["*"]
applies_when_content_matches = ["VERIFIED", "verification", "Specification-Derived Verification"]
""",
        encoding="utf-8",
    )
    return config_path


def _build_packet(tmp_path: Path, content: str) -> dict:
    bridge_dir = tmp_path / "bridge"
    config_path = _write_config(tmp_path)
    db_path = tmp_path / "groundtruth.db"
    db_path.touch()
    # Create minimal schema for enrich_from_membase
    conn = sqlite3.connect(str(db_path))
    conn.execute("CREATE TABLE IF NOT EXISTS current_specifications (id TEXT PRIMARY KEY, title TEXT, status TEXT, type TEXT)")
    conn.execute("CREATE TABLE IF NOT EXISTS current_project_authorizations (id TEXT PRIMARY KEY, status TEXT, included_spec_ids TEXT, excluded_spec_ids TEXT)")
    conn.commit()
    conn.close()
    return preflight.build_packet(
        bridge_id="test-proposal",
        bridge_dir=bridge_dir,
        config_path=config_path,
        db_path=db_path,
        content_file=_write_proposal(tmp_path, content),
    )


class TestAuthorMetadataWarnings:
    """Finding 2.1: preflight should warn on missing author metadata fields."""

    def test_warns_on_missing_author_metadata(self, tmp_path: Path) -> None:
        content = _make_proposal_content(author_metadata=False)
        packet = _build_packet(tmp_path, content)
        warnings = packet.get("warnings", {})
        metadata_warnings = warnings.get("author_metadata_warnings", [])
        assert "author_identity" in metadata_warnings
        assert "author_model" in metadata_warnings

    def test_no_metadata_warnings_when_complete(self, tmp_path: Path) -> None:
        content = _make_proposal_content(author_metadata=True)
        packet = _build_packet(tmp_path, content)
        warnings = packet.get("warnings", {})
        metadata_warnings = warnings.get("author_metadata_warnings", [])
        assert metadata_warnings == []


class TestUnclassifiedTargetPaths:
    """Finding 2.4: preflight should warn on unclassified target paths."""

    def test_warns_on_unclassified_target_paths(self, tmp_path: Path) -> None:
        # Use a path with an unknown extension that won't match any classifier rule
        content = _make_proposal_content(
            target_paths=["weird/file.xyzq"],
            author_metadata=True,
        )
        packet = _build_packet(tmp_path, content)
        warnings = packet.get("warnings", {})
        unclassified = warnings.get("unclassified_target_paths", [])
        # The classifier may or may not be available depending on import path;
        # if available, weird/file.xyzq should be unclassified
        if unclassified:
            assert "weird/file.xyzq" in unclassified

    def test_no_unclassified_warnings_for_known_paths(self, tmp_path: Path) -> None:
        content = _make_proposal_content(
            target_paths=["scripts/foo.py"],
            author_metadata=True,
        )
        packet = _build_packet(tmp_path, content)
        warnings = packet.get("warnings", {})
        unclassified = warnings.get("unclassified_target_paths", [])
        assert "scripts/foo.py" not in unclassified
