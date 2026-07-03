"""Regression tests for bridge review-independence artifact resolution."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
HELPER_PATH = REPO_ROOT / "scripts" / "bridge_review_independence.py"


def _load_helper():
    spec = importlib.util.spec_from_file_location("bridge_review_independence_test", HELPER_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules["bridge_review_independence_test"] = module
    spec.loader.exec_module(module)
    return module


def test_versioned_bridge_files_excludes_prefix_superset_slug(tmp_path: Path) -> None:
    helper = _load_helper()
    bridge = tmp_path / "bridge"
    bridge.mkdir()
    for name in (
        "gtkb-finalization-tooling-batch-001.md",
        "gtkb-finalization-tooling-batch-002.md",
        "gtkb-finalization-tooling-batch-exact-target-amendment-003.md",
        "gtkb-finalization-tooling-batch-004-draft.md",
    ):
        (bridge / name).write_text("NEW\n", encoding="utf-8")

    paths = helper._versioned_bridge_files("gtkb-finalization-tooling-batch", tmp_path)

    assert [path.name for path in paths] == [
        "gtkb-finalization-tooling-batch-001.md",
        "gtkb-finalization-tooling-batch-002.md",
    ]


def test_reviewed_artifact_reference_accepts_trailing_descriptor(tmp_path: Path) -> None:
    helper = _load_helper()
    bridge = tmp_path / "bridge"
    bridge.mkdir()
    reviewed = bridge / "gtkb-thread-003.md"
    reviewed.write_text("NEW\nauthor_session_context_id: prime-session\n", encoding="utf-8")
    verdict = """VERIFIED
author_session_context_id: lo-session

Responds to: bridge/gtkb-thread-003.md (NEW implementation report)
"""

    assert helper.reviewed_artifact_path(verdict, "gtkb-thread", tmp_path) == reviewed.resolve()
