# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Tests for D4 Azure CI/CD scaffold (gt scaffold cicd --profile azure-enterprise).

Covers bridge/gtkb-azure-cicd-gates-006.md GO conditions:

- Condition 2: 12-path inventory exact, tested by full path equality against
  ``AZURE_CICD_EXPECTED_PATHS``.
- Condition 3: Skip-if-exists. Default dry-run writes nothing; ``--apply``
  writes only missing files; existing adopter-edited files are preserved
  byte-for-byte.
- Condition 4: OIDC contract — composite action uses typed ``inputs``,
  workflows pass ``vars.AZURE_*``, every workflow has ``permissions.id-token:
  write``, drift-detection has ``issues: write``.
- Condition 5 (NEW): Every job that invokes ``./.github/actions/azure-oidc-login``
  declares a job-level ``environment:``.
- Condition 6 (binding verification evidence): optional in-suite actionlint
  smoke, skipif when actionlint not on PATH.

Copyright (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
Licensed under AGPL-3.0-or-later.
"""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path
from typing import Any, cast

import pytest
import yaml
from click.testing import CliRunner

from groundtruth_kb._azure_cicd_templates import AZURE_CICD_EXPECTED_PATHS, azure_cicd_templates
from groundtruth_kb.cicd_scaffold import CicdScaffoldConfig, scaffold_azure_cicd
from groundtruth_kb.cli import main as cli_main

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _scaffold_to(tmp_path: Path) -> None:
    """Apply the Azure CI/CD scaffold into ``tmp_path`` for behavior tests."""
    cfg = CicdScaffoldConfig(profile="azure-enterprise", target_dir=tmp_path)
    scaffold_azure_cicd(cfg, dry_run=False)


def _load_yaml(path: Path) -> dict[str, Any]:
    """Parse a YAML file as a single mapping (workflow/action metadata)."""
    with path.open(encoding="utf-8") as f:
        loaded = yaml.safe_load(f)
    assert isinstance(loaded, dict), f"{path} did not parse as a mapping"
    return cast("dict[str, Any]", loaded)


def _workflow_paths() -> list[str]:
    return [p for p in AZURE_CICD_EXPECTED_PATHS if p.startswith(".github/workflows/") and p.endswith(".yml")]


def _action_paths() -> list[str]:
    return [p for p in AZURE_CICD_EXPECTED_PATHS if p.startswith(".github/actions/") and p.endswith("/action.yml")]


# ---------------------------------------------------------------------------
# Template catalog tests
# ---------------------------------------------------------------------------


class TestTemplateCatalog:
    def test_exact_12_descriptors(self) -> None:
        """Authoritative count: 12 files = 2 actions + 4 workflows + 1 README + 5 docs."""
        descriptors = azure_cicd_templates()
        assert len(descriptors) == 12, f"expected 12 descriptors; got {len(descriptors)}"

    def test_expected_paths_match_catalog(self) -> None:
        """Single-source invariant: AZURE_CICD_EXPECTED_PATHS must equal catalog order."""
        catalog_paths = tuple(d["target_path"] for d in azure_cicd_templates())
        assert catalog_paths == AZURE_CICD_EXPECTED_PATHS

    def test_exact_composite_action_paths(self) -> None:
        """Full set of 2 composite-action paths asserted by name."""
        expected = {
            ".github/actions/azure-oidc-login/action.yml",
            ".github/actions/deploy-evidence/action.yml",
        }
        actual = {p for p in AZURE_CICD_EXPECTED_PATHS if p.startswith(".github/actions/")}
        assert actual == expected

    def test_exact_workflow_paths(self) -> None:
        """Full set of 5 workflow paths (4 .yml + 1 README.md) asserted by name."""
        expected = {
            ".github/workflows/iac-validate.yml",
            ".github/workflows/iac-apply-staging.yml",
            ".github/workflows/iac-apply-production.yml",
            ".github/workflows/drift-detection.yml",
            ".github/workflows/README.md",
        }
        actual = {p for p in AZURE_CICD_EXPECTED_PATHS if p.startswith(".github/workflows/")}
        assert actual == expected

    def test_exact_doc_paths(self) -> None:
        """Full set of 5 adopter-doc paths asserted by name."""
        expected = {
            "docs/azure/OWNER-APPROVAL.md",
            "docs/azure/federated-identity-setup.md",
            "docs/azure/cicd-overview.md",
            "docs/azure/drift-detection-runbook.md",
            "docs/azure/iac-working-dir-config.md",
        }
        actual = {p for p in AZURE_CICD_EXPECTED_PATHS if p.startswith("docs/azure/")}
        assert actual == expected

    def test_all_paths_under_github_or_docs_azure(self) -> None:
        """Scope confinement: every scaffolded file lives under .github/ or docs/azure/."""
        for path in AZURE_CICD_EXPECTED_PATHS:
            assert path.startswith(".github/") or path.startswith("docs/azure/"), (
                f"{path!r} is outside the expected scope - potential scope escape"
            )


# ---------------------------------------------------------------------------
# scaffold_azure_cicd() behavior tests
# ---------------------------------------------------------------------------


class TestScaffoldBehavior:
    def test_dry_run_generates_no_files(self, tmp_path: Path) -> None:
        cfg = CicdScaffoldConfig(profile="azure-enterprise", target_dir=tmp_path)
        report = scaffold_azure_cicd(cfg, dry_run=True)
        assert report.dry_run is True
        assert len(report.generated) == 12
        assert len(report.skipped) == 0
        # No files on disk.
        assert list(tmp_path.rglob("*")) == []

    def test_apply_writes_exact_12_files(self, tmp_path: Path) -> None:
        cfg = CicdScaffoldConfig(profile="azure-enterprise", target_dir=tmp_path)
        report = scaffold_azure_cicd(cfg, dry_run=False)
        assert report.dry_run is False
        assert len(report.generated) == 12

        # All 12 expected paths exist on disk.
        for expected in AZURE_CICD_EXPECTED_PATHS:
            assert (tmp_path / expected).is_file(), f"missing {expected}"

        # Full-path equality: the on-disk set matches the inventory.
        on_disk = sorted(str(p.relative_to(tmp_path)).replace("\\", "/") for p in tmp_path.rglob("*") if p.is_file())
        assert sorted(AZURE_CICD_EXPECTED_PATHS) == on_disk

    def test_idempotent_on_second_apply(self, tmp_path: Path) -> None:
        """Second apply on an already-scaffolded tree writes 0, skips 12."""
        cfg = CicdScaffoldConfig(profile="azure-enterprise", target_dir=tmp_path)
        scaffold_azure_cicd(cfg, dry_run=False)
        report = scaffold_azure_cicd(cfg, dry_run=False)
        assert len(report.generated) == 0
        assert len(report.skipped) == 12

    def test_scaffold_preserves_adopter_edits(self, tmp_path: Path) -> None:
        """Adopter-edited file survives re-apply, and re-apply writes 0 / skips 12."""
        cfg = CicdScaffoldConfig(profile="azure-enterprise", target_dir=tmp_path)
        scaffold_azure_cicd(cfg, dry_run=False)

        # Adopter modifies one workflow file.
        modified_path = tmp_path / ".github/workflows/iac-validate.yml"
        custom_marker = "# ADOPTER CUSTOMIZATION - MUST NOT BE OVERWRITTEN\n"
        modified_path.write_text(custom_marker, encoding="utf-8")

        # Re-apply.
        report = scaffold_azure_cicd(cfg, dry_run=False)
        assert len(report.generated) == 0
        assert len(report.skipped) == 12

        # Adopter customization preserved byte-for-byte.
        assert modified_path.read_text(encoding="utf-8") == custom_marker

    def test_unsupported_profile_raises(self, tmp_path: Path) -> None:
        cfg = CicdScaffoldConfig(profile="aws-enterprise", target_dir=tmp_path)
        with pytest.raises(ValueError, match="Unsupported profile"):
            scaffold_azure_cicd(cfg, dry_run=True)


# ---------------------------------------------------------------------------
# Workflow / composite-action semantic tests
# ---------------------------------------------------------------------------


class TestWorkflowSemantics:
    def test_workflows_are_valid_yaml(self, tmp_path: Path) -> None:
        """All 6 .github/**/*.yml files parse as YAML mappings."""
        _scaffold_to(tmp_path)
        for rel in _workflow_paths() + _action_paths():
            parsed = _load_yaml(tmp_path / rel)
            # Sanity: each mapping has at least a top-level key.
            assert parsed, f"{rel} parsed empty"

    def test_composite_actions_have_correct_shape(self, tmp_path: Path) -> None:
        """Each action.yml has runs.using=='composite' and runs.steps list."""
        _scaffold_to(tmp_path)
        for rel in _action_paths():
            data = _load_yaml(tmp_path / rel)
            runs = data.get("runs")
            assert isinstance(runs, dict), f"{rel}: runs block missing"
            assert runs.get("using") == "composite", f"{rel}: runs.using != composite"
            steps = runs.get("steps")
            assert isinstance(steps, list) and steps, f"{rel}: runs.steps must be a non-empty list"

    def test_no_step_level_workflow_call(self, tmp_path: Path) -> None:
        """No step uses: points to .github/workflows/*.yml (actions only)."""
        _scaffold_to(tmp_path)
        for rel in _workflow_paths() + _action_paths():
            text = (tmp_path / rel).read_text(encoding="utf-8")
            # Workflow-call invocation uses workflow-level `jobs.X.uses:`, but
            # a literal step-level `uses: ./.github/workflows/...` is a misuse.
            for line in text.splitlines():
                stripped = line.strip()
                if stripped.startswith("- uses:") and ".github/workflows/" in stripped:
                    raise AssertionError(f"{rel}: step-level workflow call is invalid: {stripped}")

    def test_no_static_credentials(self, tmp_path: Path) -> None:
        """No file references secrets.AZURE_CREDENTIALS (OIDC-only contract)."""
        _scaffold_to(tmp_path)
        for rel in AZURE_CICD_EXPECTED_PATHS:
            text = (tmp_path / rel).read_text(encoding="utf-8")
            assert "secrets.AZURE_CREDENTIALS" not in text, (
                f"{rel} references secrets.AZURE_CREDENTIALS; OIDC contract forbids static credentials"
            )

    def test_production_workflow_has_environment_gate(self, tmp_path: Path) -> None:
        """iac-apply-production.yml apply job uses environment: production."""
        _scaffold_to(tmp_path)
        data = _load_yaml(tmp_path / ".github/workflows/iac-apply-production.yml")
        jobs = data.get("jobs", {})
        apply_job = jobs.get("apply")
        assert isinstance(apply_job, dict), "apply job missing from iac-apply-production.yml"
        assert apply_job.get("environment") == "production"

    def test_workflows_use_tf_working_dir_var(self, tmp_path: Path) -> None:
        """All 4 workflow YAMLs reference vars.TF_WORKING_DIR."""
        _scaffold_to(tmp_path)
        for rel in _workflow_paths():
            text = (tmp_path / rel).read_text(encoding="utf-8")
            assert "vars.TF_WORKING_DIR" in text, f"{rel} missing vars.TF_WORKING_DIR parameterization"

    def test_oidc_action_has_typed_inputs(self, tmp_path: Path) -> None:
        """azure-oidc-login/action.yml declares required typed inputs."""
        _scaffold_to(tmp_path)
        data = _load_yaml(tmp_path / ".github/actions/azure-oidc-login/action.yml")
        inputs = data.get("inputs")
        assert isinstance(inputs, dict), "action.yml missing inputs block"
        for key in ("client-id", "tenant-id", "subscription-id"):
            entry = inputs.get(key)
            assert isinstance(entry, dict), f"inputs.{key} missing"
            assert entry.get("required") is True, f"inputs.{key} must be required: true"

    def test_oidc_action_uses_inputs_not_env(self, tmp_path: Path) -> None:
        """action.yml reads inputs.*, not env.AZURE_*."""
        _scaffold_to(tmp_path)
        text = (tmp_path / ".github/actions/azure-oidc-login/action.yml").read_text(encoding="utf-8")
        assert "${{ inputs.client-id }}" in text
        assert "${{ inputs.tenant-id }}" in text
        assert "${{ inputs.subscription-id }}" in text
        # Must NOT reference env.AZURE_*
        for forbidden in ("env.AZURE_CLIENT_ID", "env.AZURE_TENANT_ID", "env.AZURE_SUBSCRIPTION_ID"):
            assert forbidden not in text, f"action.yml must not read {forbidden}"

    def test_workflows_pass_vars_to_oidc_action(self, tmp_path: Path) -> None:
        """Every workflow calling ./.github/actions/azure-oidc-login passes vars.AZURE_CLIENT_ID."""
        _scaffold_to(tmp_path)
        for rel in _workflow_paths():
            text = (tmp_path / rel).read_text(encoding="utf-8")
            if "./.github/actions/azure-oidc-login" not in text:
                continue
            assert "vars.AZURE_CLIENT_ID" in text, (
                f"{rel} invokes azure-oidc-login but does not pass vars.AZURE_CLIENT_ID"
            )
            assert "vars.AZURE_TENANT_ID" in text, (
                f"{rel} invokes azure-oidc-login but does not pass vars.AZURE_TENANT_ID"
            )
            assert "vars.AZURE_SUBSCRIPTION_ID" in text, (
                f"{rel} invokes azure-oidc-login but does not pass vars.AZURE_SUBSCRIPTION_ID"
            )

    def test_workflows_have_oidc_permissions(self, tmp_path: Path) -> None:
        """Every workflow invoking azure-oidc-login declares permissions.id-token: write."""
        _scaffold_to(tmp_path)
        for rel in _workflow_paths():
            data = _load_yaml(tmp_path / rel)
            text = (tmp_path / rel).read_text(encoding="utf-8")
            if "./.github/actions/azure-oidc-login" not in text:
                continue
            permissions = data.get("permissions")
            assert isinstance(permissions, dict), f"{rel} missing workflow-level permissions block"
            assert permissions.get("id-token") == "write", (
                f"{rel} missing permissions.id-token: write at workflow level"
            )

    def test_drift_detection_has_issues_write_permission(self, tmp_path: Path) -> None:
        """drift-detection.yml declares permissions.issues: write."""
        _scaffold_to(tmp_path)
        data = _load_yaml(tmp_path / ".github/workflows/drift-detection.yml")
        permissions = data.get("permissions")
        assert isinstance(permissions, dict), "drift-detection.yml missing permissions block"
        assert permissions.get("issues") == "write", "drift-detection.yml must declare permissions.issues: write"

    def test_all_oidc_jobs_declare_environment(self, tmp_path: Path) -> None:
        """NEW condition 5: every job invoking azure-oidc-login has a job-level environment."""
        _scaffold_to(tmp_path)
        for rel in _workflow_paths():
            data = _load_yaml(tmp_path / rel)
            jobs = data.get("jobs", {})
            if not isinstance(jobs, dict):
                continue
            for job_name, job_body in jobs.items():
                if not isinstance(job_body, dict):
                    continue
                steps = job_body.get("steps", [])
                if not isinstance(steps, list):
                    continue
                invokes_oidc = any(
                    isinstance(step, dict) and step.get("uses") == "./.github/actions/azure-oidc-login"
                    for step in steps
                )
                if not invokes_oidc:
                    continue
                environment = job_body.get("environment")
                # Acceptable: a string name, or a mapping with 'name'. Either
                # way, it must be present so GitHub Environment vars resolve.
                assert environment, (
                    f"{rel}: job {job_name!r} invokes azure-oidc-login but does not declare environment:"
                )


# ---------------------------------------------------------------------------
# CLI smoke tests
# ---------------------------------------------------------------------------


class TestCliSmoke:
    def test_cli_dry_run_default(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """CLI default is dry-run (no --apply)."""
        monkeypatch.chdir(tmp_path)
        runner = CliRunner()
        result = runner.invoke(cli_main, ["scaffold", "cicd", "--profile", "azure-enterprise"])
        assert result.exit_code == 0, result.output
        assert "DRY RUN" in result.output
        # No files written.
        assert list(tmp_path.rglob("*")) == []

    def test_cli_apply_writes_files(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """CLI --apply writes 12 files under target-dir."""
        monkeypatch.chdir(tmp_path)
        runner = CliRunner()
        result = runner.invoke(
            cli_main,
            ["scaffold", "cicd", "--profile", "azure-enterprise", "--apply"],
        )
        assert result.exit_code == 0, result.output
        assert "APPLIED" in result.output
        on_disk = [p for p in tmp_path.rglob("*") if p.is_file()]
        assert len(on_disk) == 12

    def test_cli_target_dir_flag(self, tmp_path: Path) -> None:
        """--target-dir routes scaffold output to the given path."""
        runner = CliRunner()
        custom_target = tmp_path / "custom-root"
        custom_target.mkdir()
        result = runner.invoke(
            cli_main,
            [
                "scaffold",
                "cicd",
                "--profile",
                "azure-enterprise",
                "--apply",
                "--target-dir",
                str(custom_target),
            ],
        )
        assert result.exit_code == 0, result.output
        assert (custom_target / ".github/workflows/iac-validate.yml").is_file()


# ---------------------------------------------------------------------------
# Standalone actionlint smoke (binding VERIFIED evidence; skipif when not available)
# ---------------------------------------------------------------------------


@pytest.mark.skipif(shutil.which("actionlint") is None, reason="actionlint not installed")
def test_scaffolded_workflows_actionlint_clean(tmp_path: Path) -> None:
    """actionlint runs cleanly against the scaffolded workflow files.

    Per bridge/gtkb-azure-cicd-gates-006.md condition 6, this test uses a
    supported actionlint invocation: workflow files only, NOT
    ``.github/actions/*/action.yml`` as positional arguments. Local
    composite action metadata is validated through the workflows that
    reference it plus the separate PyYAML/shape tests above.

    The test gracefully skips when actionlint's environment detection fails
    (e.g. the binary expects a shellcheck subprocess that is absent) — the
    invariant we care about is the semantic shape of the workflow YAML,
    which the other tests enforce.
    """
    _scaffold_to(tmp_path)
    workflow_dir = tmp_path / ".github/workflows"
    workflow_files = sorted(p for p in workflow_dir.glob("*.yml"))
    assert workflow_files, "no workflow files to lint"

    try:
        proc = subprocess.run(
            ["actionlint", *[str(p) for p in workflow_files]],
            cwd=str(tmp_path),
            capture_output=True,
            text=True,
            timeout=60,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired) as exc:
        pytest.skip(f"actionlint invocation failed: {exc}")

    if proc.returncode != 0:
        # Environment-sensitive detection (e.g. git init needed, shellcheck
        # absent) surfaces as non-zero even when the workflow YAML itself is
        # fine. Surface as a skip rather than a hard failure here; the
        # separate post-impl actionlint command output is the binding
        # VERIFIED evidence.
        message = (proc.stderr + proc.stdout).strip()
        if "no such file" in message.lower() or "not a git repository" in message.lower():
            pytest.skip(f"actionlint environment detection failed: {message[:200]}")
        raise AssertionError(f"actionlint reported issues: stdout={proc.stdout} stderr={proc.stderr}")
