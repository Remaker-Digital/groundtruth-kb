# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Tests for D3 Azure IaC scaffold (gt scaffold iac --profile azure-enterprise).

Covers bridge/gtkb-azure-iac-skeleton-004.md GO conditions:

- Condition 2: 45-file inventory exact, tested by full path.
- Condition 3: Existing files adopter-owned; never overwritten.
- Condition 4: Terraform validation is optional (skipif when terraform not on PATH).
- Condition 5: CLI write behavior explicit (--dry-run default, --apply writes).

Copyright (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
Licensed under AGPL-3.0-or-later.
"""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import pytest
from click.testing import CliRunner

from groundtruth_kb._azure_iac_templates import AZURE_IAC_EXPECTED_PATHS, azure_iac_templates
from groundtruth_kb.cli import main as cli_main
from groundtruth_kb.iac_scaffold import IacScaffoldConfig, scaffold_azure_iac

# ---------------------------------------------------------------------------
# Template catalog tests
# ---------------------------------------------------------------------------


class TestTemplateCatalog:
    def test_exact_45_descriptors(self) -> None:
        """Authoritative count: 45 files = 6 top-level + 13 modules x 3."""
        descriptors = azure_iac_templates()
        assert len(descriptors) == 45, f"expected 45 descriptors; got {len(descriptors)}"

    def test_exact_45_expected_paths(self) -> None:
        """Expected-paths constant must mirror the template catalog length."""
        assert len(AZURE_IAC_EXPECTED_PATHS) == 45

    def test_expected_paths_match_catalog(self) -> None:
        """Single-source invariant: AZURE_IAC_EXPECTED_PATHS must equal catalog order."""
        catalog_paths = tuple(d["target_path"] for d in azure_iac_templates())
        assert catalog_paths == AZURE_IAC_EXPECTED_PATHS

    def test_all_paths_under_iac_azure(self) -> None:
        """Scope confinement: every scaffolded file lives under iac/azure/."""
        for path in AZURE_IAC_EXPECTED_PATHS:
            assert path.startswith("iac/azure/"), f"{path!r} does not start with 'iac/azure/' - scope escape"

    def test_exact_top_level_paths(self) -> None:
        """Assert full set of 6 top-level paths (not just count)."""
        expected_top = {
            "iac/azure/main.tf",
            "iac/azure/variables.tf",
            "iac/azure/outputs.tf",
            "iac/azure/providers.tf",
            "iac/azure/README.md",
            "iac/azure/terraform.tfvars.example",
        }
        actual_top = {p for p in AZURE_IAC_EXPECTED_PATHS if p.count("/") == 2}
        assert actual_top == expected_top

    def test_exact_13_modules(self) -> None:
        """Assert full set of 13 module directories."""
        expected_mods = {
            "landing-zone",
            "identity",
            "tenancy",
            "cost",
            "compliance",
            "networking",
            "cicd",
            "observability",
            "compute",
            "data",
            "secrets",
            "dr",
            "doctor",
        }
        actual_mods = {p.split("/")[3] for p in AZURE_IAC_EXPECTED_PATHS if p.startswith("iac/azure/modules/")}
        assert actual_mods == expected_mods

    def test_each_module_has_three_files(self) -> None:
        """Each module directory has exactly main.tf + variables.tf + outputs.tf."""
        module_files: dict[str, set[str]] = {}
        for p in AZURE_IAC_EXPECTED_PATHS:
            if p.startswith("iac/azure/modules/"):
                parts = p.split("/")
                mod_name, filename = parts[3], parts[4]
                module_files.setdefault(mod_name, set()).add(filename)
        for mod_name, files in module_files.items():
            assert files == {"main.tf", "variables.tf", "outputs.tf"}, f"module {mod_name} has files {files}"


# ---------------------------------------------------------------------------
# scaffold_azure_iac() behavior tests
# ---------------------------------------------------------------------------


class TestScaffoldBehavior:
    def test_dry_run_generates_no_files(self, tmp_path: Path) -> None:
        cfg = IacScaffoldConfig(profile="azure-enterprise", target_dir=tmp_path)
        report = scaffold_azure_iac(cfg, dry_run=True)
        assert report.dry_run is True
        assert len(report.generated) == 45
        assert len(report.skipped) == 0
        # No files on disk.
        assert list(tmp_path.rglob("*")) == []

    def test_apply_writes_exact_45_files(self, tmp_path: Path) -> None:
        cfg = IacScaffoldConfig(profile="azure-enterprise", target_dir=tmp_path)
        report = scaffold_azure_iac(cfg, dry_run=False)
        assert report.dry_run is False
        assert len(report.generated) == 45

        # All 45 expected paths exist on disk.
        for expected in AZURE_IAC_EXPECTED_PATHS:
            assert (tmp_path / expected).is_file(), f"missing {expected}"

        # Count total files to catch extras.
        on_disk = sorted(str(p.relative_to(tmp_path)).replace("\\", "/") for p in tmp_path.rglob("*") if p.is_file())
        assert sorted(AZURE_IAC_EXPECTED_PATHS) == on_disk

    def test_idempotent_on_second_apply(self, tmp_path: Path) -> None:
        """Condition 3: existing files are adopter-owned; never overwritten."""
        cfg = IacScaffoldConfig(profile="azure-enterprise", target_dir=tmp_path)
        scaffold_azure_iac(cfg, dry_run=False)

        # Adopter modifies one file.
        modified_path = tmp_path / "iac/azure/main.tf"
        custom_marker = "# ADOPTER CUSTOMIZATION - MUST NOT BE OVERWRITTEN\n"
        modified_path.write_text(custom_marker, encoding="utf-8")

        # Re-apply.
        report = scaffold_azure_iac(cfg, dry_run=False)
        assert len(report.generated) == 0
        assert len(report.skipped) == 45

        # Adopter customization preserved.
        assert modified_path.read_text(encoding="utf-8") == custom_marker

    def test_unsupported_profile_raises(self, tmp_path: Path) -> None:
        cfg = IacScaffoldConfig(profile="aws-enterprise", target_dir=tmp_path)
        with pytest.raises(ValueError, match="Unsupported profile"):
            scaffold_azure_iac(cfg, dry_run=True)

    def test_scaffolded_files_contain_adopter_todo_markers(self, tmp_path: Path) -> None:
        """Every module main.tf must have a TODO: adopter marker (traceability to ADR)."""
        cfg = IacScaffoldConfig(profile="azure-enterprise", target_dir=tmp_path)
        scaffold_azure_iac(cfg, dry_run=False)

        for expected in AZURE_IAC_EXPECTED_PATHS:
            if "/modules/" in expected and expected.endswith("/main.tf"):
                content = (tmp_path / expected).read_text(encoding="utf-8")
                assert "TODO: adopter" in content, f"{expected} missing adopter TODO"
                assert "adr-azure-" in content, f"{expected} missing ADR reference"


# ---------------------------------------------------------------------------
# CLI smoke tests
# ---------------------------------------------------------------------------


class TestCliSmoke:
    def test_cli_dry_run_default(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """CLI default is dry-run (no --apply)."""
        monkeypatch.chdir(tmp_path)
        runner = CliRunner()
        result = runner.invoke(cli_main, ["scaffold", "iac", "--profile", "azure-enterprise"])
        assert result.exit_code == 0, result.output
        assert "DRY RUN" in result.output
        # No files written.
        assert list(tmp_path.rglob("*")) == []

    def test_cli_apply_writes_files(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """CLI --apply writes files under target-dir."""
        monkeypatch.chdir(tmp_path)
        runner = CliRunner()
        result = runner.invoke(
            cli_main,
            ["scaffold", "iac", "--profile", "azure-enterprise", "--apply"],
        )
        assert result.exit_code == 0, result.output
        assert "APPLIED" in result.output
        # 45 files written.
        on_disk = [p for p in tmp_path.rglob("*") if p.is_file()]
        assert len(on_disk) == 45

    def test_cli_target_dir_flag(self, tmp_path: Path) -> None:
        """CLI --target-dir routes scaffold output to the given path."""
        runner = CliRunner()
        custom_target = tmp_path / "custom-root"
        custom_target.mkdir()
        result = runner.invoke(
            cli_main,
            [
                "scaffold",
                "iac",
                "--profile",
                "azure-enterprise",
                "--apply",
                "--target-dir",
                str(custom_target),
            ],
        )
        assert result.exit_code == 0, result.output
        assert (custom_target / "iac/azure/main.tf").is_file()


# ---------------------------------------------------------------------------
# Terraform validation (optional per GO condition 4)
# ---------------------------------------------------------------------------


@pytest.mark.skipif(shutil.which("terraform") is None, reason="terraform not installed")
def test_scaffolded_tree_terraform_validates(tmp_path: Path) -> None:
    """Condition 4 smoke: scaffolded skeletons parse with terraform validate.

    Skipped when terraform CLI is not on PATH - per GO condition, Terraform
    must not be a hard dependency of the default pytest suite.
    """
    cfg = IacScaffoldConfig(profile="azure-enterprise", target_dir=tmp_path)
    scaffold_azure_iac(cfg, dry_run=False)

    iac_dir = tmp_path / "iac" / "azure"

    # terraform init -backend=false avoids provider-download network hits that
    # would still be required by init without -backend=false.
    init = subprocess.run(
        ["terraform", "init", "-backend=false"],
        cwd=str(iac_dir),
        capture_output=True,
        text=True,
    )
    # Skip the test if init fails (e.g., no network for provider download) -
    # the invariant we care about is that the HCL syntax is valid, which
    # validate covers. Init failures are environment-specific, not skeleton bugs.
    if init.returncode != 0:
        pytest.skip(f"terraform init failed (likely network/provider download): {init.stderr[:200]}")

    validate = subprocess.run(
        ["terraform", "validate"],
        cwd=str(iac_dir),
        capture_output=True,
        text=True,
    )
    assert validate.returncode == 0, f"terraform validate failed: stdout={validate.stdout} stderr={validate.stderr}"
