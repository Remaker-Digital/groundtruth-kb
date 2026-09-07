"""Tests for harness-state SoT host-root resolution (WI-6452 / WI-6587).

Bridge: bridge/gtkb-wi6587-harness-state-sot-from-host-root-004.md (GO)
Specs:  GOV-HARNESS-STATE-SOT-CONSOLIDATION-001
        DCL-HARNESS-STATE-SOT-READER-CONTRACT-001

Verifies that `read_roles()` (and the harness-state SoT reader path generally)
resolves the GT-KB host root from an in-root subdirectory CWD instead of
falling back to `Path.cwd()` and inventing a nested `harness-state` under the
subdirectory.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

from groundtruth_kb.harness_projection import read_roles

REPO_ROOT = Path(__file__).resolve().parents[2]


def test_read_roles_resolves_host_root_from_subdirectory_cwd(tmp_path):
    """read_roles() from an in-root subdirectory resolves the host root.

    Builds a fixture checkout with groundtruth.toml and
    harness-state/harness-registry.json at the host root, chdirs into a
    subdirectory, and asserts read_roles() reads the host-root registry, not a
    nested one under the subdirectory.
    """
    # Fixture host root
    host_root = tmp_path / "host"
    host_root.mkdir(parents=True, exist_ok=True)
    (host_root / "groundtruth.toml").write_text("# fixture\n", encoding="utf-8")
    (host_root / "harness-state").mkdir(parents=True, exist_ok=True)
    registry = {
        "schema_version": 1,
        "generated_at": "2026-08-18T00:00:00Z",
        "harnesses": [],
    }
    (host_root / "harness-state" / "harness-registry.json").write_text(json.dumps(registry), encoding="utf-8")
    # A decoy nested registry under the subdirectory must NOT be read
    subdir = host_root / "scratchpad"
    subdir.mkdir(parents=True, exist_ok=True)
    (subdir / "harness-state").mkdir(parents=True, exist_ok=True)
    (subdir / "harness-state" / "harness-registry.json").write_text(
        json.dumps({"schema_version": 99, "decoy": True}), encoding="utf-8"
    )

    old_cwd = Path.cwd()
    old_env = os.environ.get("GTKB_PROJECT_ROOT")
    try:
        os.environ.pop("GTKB_PROJECT_ROOT", None)
        os.chdir(subdir)
        result = read_roles()
        assert result["schema_version"] == 1, "must read host-root registry, not decoy"
        assert "decoy" not in result
    finally:
        os.chdir(old_cwd)
        if old_env is not None:
            os.environ["GTKB_PROJECT_ROOT"] = old_env
        else:
            os.environ.pop("GTKB_PROJECT_ROOT", None)


def test_read_roles_from_repo_subdirectory_resolves_repo_root():
    """In the real checkout, read_roles() from a subdirectory finds the repo registry."""
    old_cwd = Path.cwd()
    old_env = os.environ.get("GTKB_PROJECT_ROOT")
    try:
        os.environ.pop("GTKB_PROJECT_ROOT", None)
        os.chdir(REPO_ROOT / "scratchpad")
        result = read_roles()
        assert isinstance(result, dict)
        assert "harnesses" in result
    finally:
        os.chdir(old_cwd)
        if old_env is not None:
            os.environ["GTKB_PROJECT_ROOT"] = old_env
        else:
            os.environ.pop("GTKB_PROJECT_ROOT", None)
