"""Spec-derived tests for Agent Red env SoT migration helpers.

Authority: bridge/gtkb-wi3430-3431-env-sot-migration-cli-slice-002.md.
Source work items: WI-3430 and WI-3431.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from groundtruth_kb.env_sot import EnvSotError, build_plan, migrate, render_migration_result, render_plan

SECRET_VALUE = "keep-this-value-private"


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def test_plan_classifies_root_keys_without_rendering_values(tmp_path: Path) -> None:
    _write(
        tmp_path / ".env.local",
        f"GTKB_MODE=platform\nAGENT_RED_TOKEN={SECRET_VALUE}\nSHOPIFY_SHOP=example\nOPENAI_API_KEY=ambiguous\n",
    )

    plan = build_plan(tmp_path)
    rendered = render_plan(plan)

    assert plan.platform_key_count == 1
    assert plan.root_app_key_count == 2
    assert plan.ambiguous_root_keys == ("OPENAI_API_KEY",)
    assert SECRET_VALUE not in rendered
    assert "ambiguous=1" in rendered


def test_check_plan_fails_when_admin_env_is_independent_sot(tmp_path: Path) -> None:
    _write(tmp_path / "applications" / "Agent_Red" / ".env.local", f"AGENT_RED_TOKEN={SECRET_VALUE}\n")
    _write(tmp_path / "applications" / "Agent_Red" / "admin" / "shopify" / ".env.local", "SHOPIFY_SHOP=example\n")

    plan = build_plan(tmp_path)

    assert not plan.ok_for_apply
    assert plan.independent_admin_sot_count == 1
    assert "admin/shopify/.env.local" in "\n".join(plan.diagnostics)


def test_apply_migration_moves_app_keys_and_generates_admin_views(tmp_path: Path) -> None:
    _write(tmp_path / ".env.local", f"GTKB_MODE=platform\nAGENT_RED_TOKEN={SECRET_VALUE}\n")

    result = migrate(tmp_path, apply=True)

    assert result.applied is True
    assert result.moved_key_count == 1
    assert result.generated_view_count == 3
    assert "AGENT_RED_TOKEN" not in (tmp_path / ".env.local").read_text(encoding="utf-8")
    app_env = tmp_path / "applications" / "Agent_Red" / ".env.local"
    assert f"AGENT_RED_TOKEN={SECRET_VALUE}" in app_env.read_text(encoding="utf-8")
    shopify_view = tmp_path / "applications" / "Agent_Red" / "admin" / "shopify" / ".env.local"
    assert f"AGENT_RED_TOKEN={SECRET_VALUE}" in shopify_view.read_text(encoding="utf-8")
    assert SECRET_VALUE not in render_migration_result(result)


def test_apply_migration_fails_closed_on_ambiguous_root_keys(tmp_path: Path) -> None:
    _write(tmp_path / ".env.local", f"OPENAI_API_KEY={SECRET_VALUE}\n")

    with pytest.raises(EnvSotError):
        migrate(tmp_path, apply=True)


def test_dry_run_does_not_mutate_files_or_render_values(tmp_path: Path) -> None:
    root_env = tmp_path / ".env.local"
    _write(root_env, f"AGENT_RED_TOKEN={SECRET_VALUE}\n")

    result = migrate(tmp_path, apply=False)

    assert result.applied is False
    assert root_env.read_text(encoding="utf-8") == f"AGENT_RED_TOKEN={SECRET_VALUE}\n"
    assert SECRET_VALUE not in render_migration_result(result)
