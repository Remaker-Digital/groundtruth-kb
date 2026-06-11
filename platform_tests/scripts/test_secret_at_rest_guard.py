"""Tests for the FAB-02 secret-at-rest regression guard (WI-4414; HYG-019/020).

Exercises the guard's PASS/FAIL branches against a tmp fixture tree and asserts
value-safety (no file contents leak into the result). Derived from
DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001.
"""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

_GUARD_PATH = Path(__file__).resolve().parents[2] / "scripts" / "hygiene" / "secret_at_rest_guard.py"


def _load_guard():
    spec = importlib.util.spec_from_file_location("secret_at_rest_guard", _GUARD_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


guard = _load_guard()

_CLEAN_DRIVEIGNORE = (
    "\n".join(
        [
            "# comment line is ignored",
            "groundtruth.db",
            ".env.local",
            ".env*",
            "!*.example",
            "*.tfstate",
            "*.tfstate.*",
            "*.tfvars",
            "infrastructure/terraform/.terraform/",
            "infrastructure/terraform/backend.hcl",
        ]
    )
    + "\n"
)


def _build_clean_tree(root: Path) -> Path:
    """Create a clean fixture tree that should pass every invariant."""
    (root / ".driveignore").write_text(_CLEAN_DRIVEIGNORE, encoding="utf-8")
    tf = root / "infrastructure" / "terraform"
    tf.mkdir(parents=True)
    (tf / "backend.tf").write_text('terraform {\n  backend "azurerm" {}\n}\n', encoding="utf-8")
    (tf / "backend.hcl.example").write_text('resource_group_name = "x"\n', encoding="utf-8")
    (tf / "STATE-MIGRATION-RUNBOOK.md").write_text("# runbook\n", encoding="utf-8")
    # Live state with NO backups; the guard must not read its contents.
    (tf / "terraform.tfstate").write_text('{"version": 4}\n', encoding="utf-8")
    return tf


def test_clean_tree_passes(tmp_path: Path) -> None:
    _build_clean_tree(tmp_path)
    result = guard.evaluate(tmp_path)
    assert result["ok"] is True, result["failures"]
    assert result["failures"] == []


def test_result_is_json_serializable(tmp_path: Path) -> None:
    _build_clean_tree(tmp_path)
    result = guard.evaluate(tmp_path)
    json.dumps(result)  # must not raise


def test_missing_driveignore_fails(tmp_path: Path) -> None:
    _build_clean_tree(tmp_path)
    (tmp_path / ".driveignore").unlink()
    result = guard.evaluate(tmp_path)
    assert result["ok"] is False
    assert "driveignore_present" in result["failures"]


def test_missing_env_local_exclusion_fails(tmp_path: Path) -> None:
    _build_clean_tree(tmp_path)
    # Re-write .driveignore without any .env exclusion (HYG-020 regressed).
    (tmp_path / ".driveignore").write_text(
        "\n".join(["*.tfstate", "*.tfstate.*", "*.tfvars", "x/.terraform/"]) + "\n",
        encoding="utf-8",
    )
    result = guard.evaluate(tmp_path)
    assert result["ok"] is False
    assert "env_local_excluded" in result["failures"]


def test_missing_tfstate_exclusion_fails(tmp_path: Path) -> None:
    _build_clean_tree(tmp_path)
    (tmp_path / ".driveignore").write_text(
        "\n".join([".env.local", "*.tfvars", "x/.terraform/"]) + "\n",
        encoding="utf-8",
    )
    result = guard.evaluate(tmp_path)
    assert result["ok"] is False
    assert "tfstate_excluded" in result["failures"]


def test_missing_backend_hcl_exclusion_fails(tmp_path: Path) -> None:
    """FAB-02 -004 NO-GO regression: the real backend.hcl must be Drive-excluded.

    The docs (backend.hcl.example, STATE-MIGRATION-RUNBOOK.md) claim the
    owner-filled backend config is never Drive-synced; the guard now asserts the
    .driveignore exclusion that makes that claim mechanically true.
    """
    _build_clean_tree(tmp_path)
    # Re-write .driveignore keeping every other exclusion but dropping the
    # backend.hcl exclusion (the -004 verification gap).
    (tmp_path / ".driveignore").write_text(
        "\n".join(
            [
                ".env.local",
                ".env*",
                "!*.example",
                "*.tfstate",
                "*.tfstate.*",
                "*.tfvars",
                "infrastructure/terraform/.terraform/",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    result = guard.evaluate(tmp_path)
    assert result["ok"] is False
    assert "backend_hcl_excluded" in result["failures"]


def test_stale_tfstate_backup_fails(tmp_path: Path) -> None:
    tf = _build_clean_tree(tmp_path)
    (tf / "terraform.tfstate.backup").write_text('{"stale": true}\n', encoding="utf-8")
    result = guard.evaluate(tmp_path)
    assert result["ok"] is False
    assert "no_stale_tfstate_backups" in result["failures"]


def test_missing_backend_block_fails(tmp_path: Path) -> None:
    tf = _build_clean_tree(tmp_path)
    # backend.tf without the azurerm block (scaffolding regressed).
    (tf / "backend.tf").write_text("# no backend block here\n", encoding="utf-8")
    result = guard.evaluate(tmp_path)
    assert result["ok"] is False
    assert "azurerm_backend_block_present" in result["failures"]


def test_missing_runbook_fails(tmp_path: Path) -> None:
    tf = _build_clean_tree(tmp_path)
    (tf / "STATE-MIGRATION-RUNBOOK.md").unlink()
    result = guard.evaluate(tmp_path)
    assert result["ok"] is False
    assert "migration_runbook_present" in result["failures"]


def test_guard_is_value_safe(tmp_path: Path) -> None:
    """The guard must never surface secret-bearing file contents in its result."""
    tf = _build_clean_tree(tmp_path)
    sentinel = "TOTALLY-SECRET-VALUE-DO-NOT-LEAK"
    # Plant a fake secret inside state + .env.local; the guard never reads them.
    (tf / "terraform.tfstate").write_text(json.dumps({"admin_password": sentinel}) + "\n", encoding="utf-8")
    (tmp_path / ".env.local").write_text(f"API_KEY={sentinel}\n", encoding="utf-8")
    result = guard.evaluate(tmp_path)
    assert sentinel not in json.dumps(result)
