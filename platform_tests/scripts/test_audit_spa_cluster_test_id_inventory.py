# (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Focused tests for the S350 SPA cluster test-ID inventory canonical-output helper (WI-5590)."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "scripts" / "audit_spa_cluster_test_id_inventory.py"


def _load_module():
    spec = importlib.util.spec_from_file_location("audit_spa_cluster_test_id_inventory", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules["audit_spa_cluster_test_id_inventory"] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def mod():
    return _load_module()


def test_no_implicit_file_output_default(mod):
    """WI-5590: DEFAULT_OUTPUT_PATH must not exist; the helper emits stdout only."""
    assert not hasattr(mod, "DEFAULT_OUTPUT_PATH"), "DEFAULT_OUTPUT_PATH must be removed"


def test_generate_inventory_returns_content_without_writing(mod, tmp_path):
    """generate_inventory() returns the rendered content and creates no file."""
    # Run against the real DB; assert it returns a non-empty string and creates no side file.
    content = mod.generate_inventory(db_path=REPO_ROOT / "groundtruth.db")
    assert isinstance(content, str)
    assert content.strip(), "inventory must return non-empty content"
    # No output file should be created in the dropbox or anywhere by the pure function.
    assert "## Closure Statement" in content


def test_main_emits_content_to_stdout_without_argument(mod, capsys):
    """main() with no args writes the inventory to stdout and returns 0."""
    rc = mod.main([])
    captured = capsys.readouterr()
    assert rc == 0
    assert captured.out.strip(), "main() must emit inventory to stdout"


def test_main_rejects_unknown_arguments(mod, capsys):
    """main() rejects arguments (no --out / output-path option remains)."""
    rc = mod.main(["--out", "x.md"])
    captured = capsys.readouterr()
    assert rc == 2
    assert "usage" in captured.err
