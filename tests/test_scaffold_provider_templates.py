# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Tests for provider schema + parameterized templates + role validation (WI-MVP-3)."""

from __future__ import annotations

from pathlib import Path

import pytest
from click.testing import CliRunner

from groundtruth_kb.cli import main as cli
from groundtruth_kb.project.scaffold import ScaffoldOptions, scaffold_project
from groundtruth_kb.providers.schema import CLAUDE_CODE, CODEX, AgentProvider, get_provider, list_providers


# ---------------------------------------------------------------------------
# Provider schema unit tests
# ---------------------------------------------------------------------------


def test_claude_code_provider_has_prime_role() -> None:
    """CLAUDE_CODE provider has bridge_role='prime'."""
    assert CLAUDE_CODE.bridge_role == "prime"


def test_codex_provider_has_loyal_opposition_role() -> None:
    """CODEX provider has bridge_role='loyal-opposition'."""
    assert CODEX.bridge_role == "loyal-opposition"


def test_get_provider_returns_correct_provider() -> None:
    """get_provider() returns the matching provider."""
    assert get_provider("claude-code") is CLAUDE_CODE
    assert get_provider("codex") is CODEX


def test_get_provider_raises_for_unknown_id() -> None:
    """get_provider() raises ValueError for an unknown provider ID."""
    with pytest.raises(ValueError, match="Unknown provider"):
        get_provider("custom-unknown-provider")


def test_list_providers_returns_all() -> None:
    """list_providers() returns at least both built-in providers."""
    providers = list_providers()
    ids = {p.provider_id for p in providers}
    assert "claude-code" in ids
    assert "codex" in ids


# ---------------------------------------------------------------------------
# Template rendering with provider placeholders
# ---------------------------------------------------------------------------


def test_agents_md_contains_lo_display_name(tmp_path: Path) -> None:
    """AGENTS.md has LO provider display name substituted correctly."""
    options = ScaffoldOptions(
        project_name="Prov Test",
        profile="dual-agent",
        owner="Owner",
        target_dir=tmp_path / "project",
        seed_example=False,
        include_ci=False,
    )
    scaffold_project(options)
    content = (tmp_path / "project" / "AGENTS.md").read_text(encoding="utf-8")
    assert CODEX.display_name in content


def test_agents_md_contains_prime_display_name(tmp_path: Path) -> None:
    """AGENTS.md has Prime provider display name substituted correctly."""
    options = ScaffoldOptions(
        project_name="Prov Test",
        profile="dual-agent",
        owner="Owner",
        target_dir=tmp_path / "project",
        seed_example=False,
        include_ci=False,
    )
    scaffold_project(options)
    content = (tmp_path / "project" / "AGENTS.md").read_text(encoding="utf-8")
    assert CLAUDE_CODE.display_name in content


def test_agents_md_no_unresolved_provider_placeholders(tmp_path: Path) -> None:
    """AGENTS.md has no unresolved {{LO_PROVIDER_*}} or {{PRIME_PROVIDER_*}} placeholders."""
    options = ScaffoldOptions(
        project_name="Prov Test",
        profile="dual-agent",
        owner="Owner",
        target_dir=tmp_path / "project",
        seed_example=False,
        include_ci=False,
    )
    scaffold_project(options)
    content = (tmp_path / "project" / "AGENTS.md").read_text(encoding="utf-8")
    assert "{{LO_PROVIDER_" not in content
    assert "{{PRIME_PROVIDER_" not in content


# ---------------------------------------------------------------------------
# CLI role validation tests
# ---------------------------------------------------------------------------


def test_cli_unknown_prime_provider_raises_usage_error(tmp_path: Path) -> None:
    """--prime-provider with unknown ID produces a UsageError."""
    runner = CliRunner()
    result = runner.invoke(
        cli,
        [
            "project",
            "init",
            "TestProject",
            "--profile",
            "dual-agent",
            "--prime-provider",
            "custom-nonexistent",
            "--dir",
            str(tmp_path / "out"),
            "--no-seed-example",
            "--no-include-ci",
        ],
    )
    assert result.exit_code != 0
    assert "Unknown provider" in result.output or "Error" in result.output


def test_cli_prime_provider_with_lo_role_raises_usage_error(tmp_path: Path) -> None:
    """--prime-provider codex raises UsageError because codex has role loyal-opposition."""
    runner = CliRunner()
    result = runner.invoke(
        cli,
        [
            "project",
            "init",
            "TestProject",
            "--profile",
            "dual-agent",
            "--prime-provider",
            "codex",
            "--dir",
            str(tmp_path / "out"),
            "--no-seed-example",
            "--no-include-ci",
        ],
    )
    assert result.exit_code != 0
    assert "loyal-opposition" in result.output or "bridge_role" in result.output or "Error" in result.output


def test_cli_lo_provider_with_prime_role_raises_usage_error(tmp_path: Path) -> None:
    """--lo-provider claude-code raises UsageError because claude-code has role prime."""
    runner = CliRunner()
    result = runner.invoke(
        cli,
        [
            "project",
            "init",
            "TestProject",
            "--profile",
            "dual-agent",
            "--lo-provider",
            "claude-code",
            "--dir",
            str(tmp_path / "out"),
            "--no-seed-example",
            "--no-include-ci",
        ],
    )
    assert result.exit_code != 0
    assert "prime" in result.output or "bridge_role" in result.output or "Error" in result.output


def test_cli_default_providers_succeed(tmp_path: Path) -> None:
    """Default providers (claude-code + codex) produce a successful scaffold."""
    runner = CliRunner()
    result = runner.invoke(
        cli,
        [
            "project",
            "init",
            "TestProject",
            "--profile",
            "dual-agent",
            "--dir",
            str(tmp_path / "out"),
            "--no-seed-example",
            "--no-include-ci",
        ],
    )
    assert result.exit_code == 0
    assert (tmp_path / "out" / "AGENTS.md").exists()
