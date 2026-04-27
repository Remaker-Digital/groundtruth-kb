"""Tests for Wave 2 Slice 9 ``_production_effects.py``.

Per ``bridge/gtkb-isolation-016-phase8-wave2-slice9-005.md`` (REVISED-2)
and ``-006`` (Codex GO with constraint: secret-adjacent treatment for
every ``_prod_env_vars*.txt`` glob match, not just the literal filename).

Fixture-based per the Slice 4-7 pattern. The safety-regression tests
monkeypatch ``Path.read_text`` and ``Path.read_bytes`` to assert the
lane never reads sensitive content.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from rehearse import _production_effects  # noqa: E402

# ---- Fixtures ----------------------------------------------------------


def _build_project_root(tmp_path: Path) -> Path:
    project_root = tmp_path / "project"
    project_root.mkdir()
    return project_root


def _run_lane(
    project_root: Path,
    output_dir: Path,
    manifest: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return _production_effects.run(
        manifest or {"excluded_paths": []},
        output_dir,
        project_root=project_root,
    )


def _read_json(output_dir: Path) -> dict[str, Any]:
    return json.loads((output_dir / "production_effects" / "production_effects.json").read_text(encoding="utf-8"))


# ---- Common contract --------------------------------------------------


def test_run_dry_run_returns_skipped(tmp_path: Path) -> None:
    project_root = _build_project_root(tmp_path)
    result = _production_effects.run(
        {"excluded_paths": []},
        tmp_path / "output",
        dry_run=True,
        project_root=project_root,
    )
    assert result["status"] == "skipped"
    assert result["metrics"] == {"reason": "dry_run"}


# ---- §2.1 Secret material safety (CRITICAL) ---------------------------


def test_run_does_not_read_prod_env_vars_content(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Per Codex GO -006 + REVISED-2: _prod_env_vars*.txt MUST NOT be
    content-read. Monkeypatch read_text/read_bytes to assert no forbidden
    reads occur, while the lane still classifies the file correctly.
    """
    project_root = _build_project_root(tmp_path)
    deploy_dir = project_root / "scripts" / "deploy"
    deploy_dir.mkdir(parents=True)
    (deploy_dir / "_prod_env_vars.txt").write_text("AZURE_KEY=should-never-be-read\n", encoding="utf-8")
    (deploy_dir / "_prod_env_vars_clean.txt").write_text("AZURE_KEY=also-should-never-be-read\n", encoding="utf-8")

    real_read_text = Path.read_text
    real_read_bytes = Path.read_bytes
    forbidden_reads: list[tuple[str, str]] = []

    def _trap_read_text(self: Path, *args: object, **kwargs: object) -> str:  # type: ignore[no-untyped-def]
        if "_prod_env_vars" in self.name:
            forbidden_reads.append(("read_text", str(self)))
            raise AssertionError(f"Lane illegally read content of {self}")
        return real_read_text(self, *args, **kwargs)

    def _trap_read_bytes(self: Path, *args: object, **kwargs: object) -> bytes:  # type: ignore[no-untyped-def]
        if "_prod_env_vars" in self.name:
            forbidden_reads.append(("read_bytes", str(self)))
            raise AssertionError(f"Lane illegally read content of {self}")
        return real_read_bytes(self, *args, **kwargs)

    monkeypatch.setattr(Path, "read_text", _trap_read_text)
    monkeypatch.setattr(Path, "read_bytes", _trap_read_bytes)

    output_dir = tmp_path / "output"
    result = _run_lane(project_root, output_dir)

    assert result["status"] == "ok"
    assert forbidden_reads == [], f"Lane attempted forbidden reads: {forbidden_reads}"

    payload = _read_json(output_dir)
    # BOTH glob matches must be classified secret-adjacent (per GO -006).
    prod_env_rows = [s for s in payload["surfaces"] if "_prod_env_vars" in s["path"]]
    assert len(prod_env_rows) == 2, (
        f"Expected 2 _prod_env_vars*.txt rows; got {len(prod_env_rows)}: {[r['path'] for r in prod_env_rows]}"
    )
    for row in prod_env_rows:
        assert row["disposition"] == "DO_NOT_MOVE"
        assert row["signal"] == "production_env_vars_secret_adjacent_per_codex_s9_004"
        assert row["deploy_safety"] == "deploy-blocking"
        assert row["content_read"] is False


def test_run_does_not_read_env_local_content(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Original §2.1 safety property: .env.local presence-only, never content-read."""
    project_root = _build_project_root(tmp_path)
    (project_root / ".env.local").write_text("SECRET=do-not-read\n", encoding="utf-8")

    real_read_text = Path.read_text
    forbidden_reads: list[str] = []

    def _trap(self: Path, *args: object, **kwargs: object) -> str:  # type: ignore[no-untyped-def]
        if self.name == ".env.local":
            forbidden_reads.append(str(self))
            raise AssertionError(f"Lane read .env.local: {self}")
        return real_read_text(self, *args, **kwargs)

    monkeypatch.setattr(Path, "read_text", _trap)

    output_dir = tmp_path / "output"
    result = _run_lane(project_root, output_dir)
    assert result["status"] == "ok"
    assert forbidden_reads == []
    payload = _read_json(output_dir)
    row = next(s for s in payload["surfaces"] if s["path"] == ".env.local")
    assert row["disposition"] == "DO_NOT_MOVE"
    assert row["content_read"] is False


def test_run_does_not_read_tfvars_content(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """tfvars files are secret-adjacent; presence-only."""
    project_root = _build_project_root(tmp_path)
    tf_dir = project_root / "infrastructure" / "terraform"
    tf_dir.mkdir(parents=True)
    (tf_dir / "production.tfvars").write_text('api_key = "secret"\n', encoding="utf-8")

    real_read_text = Path.read_text
    forbidden: list[str] = []

    def _trap(self: Path, *args: object, **kwargs: object) -> str:  # type: ignore[no-untyped-def]
        if self.name.endswith(".tfvars"):
            forbidden.append(str(self))
            raise AssertionError(f"tfvars read: {self}")
        return real_read_text(self, *args, **kwargs)

    monkeypatch.setattr(Path, "read_text", _trap)
    output_dir = tmp_path / "output"
    result = _run_lane(project_root, output_dir)
    assert result["status"] == "ok"
    assert forbidden == []
    payload = _read_json(output_dir)
    row = next(s for s in payload["surfaces"] if s["path"].endswith(".tfvars"))
    assert row["disposition"] == "DO_NOT_MOVE"
    assert row["signal"] == "terraform_variable_potentially_sensitive"
    assert row["content_read"] is False


# ---- §2.10 Authoritative DB ------------------------------------------


def test_run_classifies_groundtruth_db_as_do_not_move(tmp_path: Path) -> None:
    project_root = _build_project_root(tmp_path)
    (project_root / "groundtruth.db").write_bytes(b"SQLite stub")
    output_dir = tmp_path / "output"
    _run_lane(project_root, output_dir)
    payload = _read_json(output_dir)
    row = next(s for s in payload["surfaces"] if s["path"] == "groundtruth.db")
    assert row["disposition"] == "DO_NOT_MOVE"
    assert row["signal"] == "phase_8_plan_section_4_explicit_immovable"


# ---- §2.11 Framework directive files ---------------------------------


def test_run_classifies_claude_md_as_keep(tmp_path: Path) -> None:
    project_root = _build_project_root(tmp_path)
    (project_root / "CLAUDE.md").write_text("# project rules\n", encoding="utf-8")
    output_dir = tmp_path / "output"
    _run_lane(project_root, output_dir)
    payload = _read_json(output_dir)
    row = next(s for s in payload["surfaces"] if s["path"] == "CLAUDE.md")
    assert row["disposition"] == "KEEP"
    assert row["signal"] == "framework_root_directive_file"


# ---- §2.13 Docker classification + framework override ---------------


def test_run_classifies_dockerfile_as_move_with_deploy_blocking(tmp_path: Path) -> None:
    project_root = _build_project_root(tmp_path)
    (project_root / "Dockerfile").write_text("FROM python:3.14\nCOPY src/ /app/src/\n", encoding="utf-8")
    output_dir = tmp_path / "output"
    _run_lane(project_root, output_dir)
    payload = _read_json(output_dir)
    row = next(s for s in payload["surfaces"] if s["path"] == "Dockerfile")
    assert row["disposition"] == "MOVE"
    assert row["signal"] == "adopter_container_definition"
    assert row["deploy_safety"] == "deploy-blocking"


def test_run_overrides_dockerfile_to_owner_decision_when_framework_reference(tmp_path: Path) -> None:
    project_root = _build_project_root(tmp_path)
    (project_root / "Dockerfile").write_text("FROM python:3.14\nRUN pip install groundtruth_kb\n", encoding="utf-8")
    output_dir = tmp_path / "output"
    _run_lane(project_root, output_dir)
    payload = _read_json(output_dir)
    row = next(s for s in payload["surfaces"] if s["path"] == "Dockerfile")
    assert row["disposition"] == "OWNER_DECISION_REQUIRED"
    assert "framework_reference" in row["signal"]


# ---- §2.14 Shopify ---------------------------------------------------


def test_run_classifies_shopify_app_toml_as_move_with_deploy_blocking(tmp_path: Path) -> None:
    project_root = _build_project_root(tmp_path)
    (project_root / "shopify.app.toml").write_text('name = "agent-red"\n', encoding="utf-8")
    output_dir = tmp_path / "output"
    _run_lane(project_root, output_dir)
    payload = _read_json(output_dir)
    row = next(s for s in payload["surfaces"] if s["path"] == "shopify.app.toml")
    assert row["disposition"] == "MOVE"
    assert row["deploy_safety"] == "deploy-blocking"


# ---- §2.15 Deploy scripts + hardcoded-path scan ----------------------


def test_run_classifies_deploy_script_as_move_with_deploy_blocking(tmp_path: Path) -> None:
    project_root = _build_project_root(tmp_path)
    (project_root / "scripts").mkdir()
    (project_root / "scripts" / "deploy.py").write_text("#!/usr/bin/env python\nprint('deploy')\n", encoding="utf-8")
    output_dir = tmp_path / "output"
    _run_lane(project_root, output_dir)
    payload = _read_json(output_dir)
    row = next(s for s in payload["surfaces"] if s["path"] == "scripts/deploy.py")
    assert row["disposition"] == "MOVE"
    assert row["deploy_safety"] == "deploy-blocking"


def test_run_records_hardcoded_path_references_in_deploy_script(tmp_path: Path) -> None:
    """§2.15: deploy scripts content-scanned for hardcoded legacy-root references."""
    project_root = _build_project_root(tmp_path)
    (project_root / "scripts").mkdir()
    (project_root / "scripts" / "deploy.py").write_text("REPO_ROOT = 'E:/GT-KB/'\n", encoding="utf-8")
    output_dir = tmp_path / "output"
    _run_lane(project_root, output_dir)
    payload = _read_json(output_dir)
    row = next(s for s in payload["surfaces"] if s["path"] == "scripts/deploy.py")
    assert "hardcoded_path_references" in row
    assert len(row["hardcoded_path_references"]) >= 1
    assert "E:/GT-KB" in row["hardcoded_path_references"][0]["matched_string"]


# ---- §2.16 Terraform -------------------------------------------------


def test_run_classifies_terraform_tf_as_move_with_deploy_blocking(tmp_path: Path) -> None:
    project_root = _build_project_root(tmp_path)
    tf_dir = project_root / "infrastructure" / "terraform"
    tf_dir.mkdir(parents=True)
    (tf_dir / "main.tf").write_text('resource "azurerm_resource_group" "main" {}\n', encoding="utf-8")
    output_dir = tmp_path / "output"
    _run_lane(project_root, output_dir)
    payload = _read_json(output_dir)
    row = next(s for s in payload["surfaces"] if s["path"] == "infrastructure/terraform/main.tf")
    assert row["disposition"] == "MOVE"
    assert row["signal"] == "adopter_terraform_definitions"


def test_run_classifies_terraform_tfstate_as_do_not_move(tmp_path: Path) -> None:
    project_root = _build_project_root(tmp_path)
    tf_dir = project_root / "infrastructure" / "terraform"
    tf_dir.mkdir(parents=True)
    (tf_dir / "terraform.tfstate").write_text("{}\n", encoding="utf-8")
    output_dir = tmp_path / "output"
    _run_lane(project_root, output_dir)
    payload = _read_json(output_dir)
    row = next(s for s in payload["surfaces"] if s["path"].endswith("terraform.tfstate"))
    assert row["disposition"] == "DO_NOT_MOVE"
    assert row["signal"] == "terraform_state_immovable_per_phase8_section_4"


# ---- §2.17 GitHub Actions hardcoded-path scan -----------------------


def test_run_records_github_actions_hardcoded_path_references(tmp_path: Path) -> None:
    project_root = _build_project_root(tmp_path)
    workflows = project_root / ".github" / "workflows"
    workflows.mkdir(parents=True)
    (workflows / "build.yml").write_text(
        "jobs:\n  build:\n    steps:\n      - run: cd E:/GT-KB/ && python build.py\n",
        encoding="utf-8",
    )
    output_dir = tmp_path / "output"
    _run_lane(project_root, output_dir)
    payload = _read_json(output_dir)
    row = next(
        (s for s in payload["surfaces"] if s["path"] == ".github/workflows/build.yml"),
        None,
    )
    assert row is not None, "GHA hardcoded-path scan didn't surface the workflow"
    assert row["category"] == "github_actions_workflow_with_hardcoded_paths"
    assert row["hardcoded_path_references"][0]["matched_string"].startswith("E:")


# ---- §2.6 Approval packets -------------------------------------------


def test_run_classifies_approval_packet_by_legacy_records_schema(tmp_path: Path) -> None:
    """Backward-compat: legacy approved_records[] schema still classified."""
    project_root = _build_project_root(tmp_path)
    approvals = project_root / ".groundtruth" / "formal-artifact-approvals"
    approvals.mkdir(parents=True)
    (approvals / "ar-approval.json").write_text(
        json.dumps({"approved_records": [{"id": "AR-001"}]}),
        encoding="utf-8",
    )
    output_dir = tmp_path / "output"
    _run_lane(project_root, output_dir)
    payload = _read_json(output_dir)
    row = next(s for s in payload["surfaces"] if "ar-approval.json" in s["path"])
    assert row["disposition"] == "MOVE"
    assert row["signal"] == "adopter_approval_packet_legacy_records"
    assert row["classification_basis"] == "legacy_schema_approved_records"


def test_run_classifies_mixed_scope_approval_packet_as_owner_decision(tmp_path: Path) -> None:
    project_root = _build_project_root(tmp_path)
    approvals = project_root / ".groundtruth" / "formal-artifact-approvals"
    approvals.mkdir(parents=True)
    (approvals / "mixed.json").write_text(
        json.dumps({"approved_records": [{"id": "AR-001"}, {"id": "GTKB-009"}]}),
        encoding="utf-8",
    )
    output_dir = tmp_path / "output"
    _run_lane(project_root, output_dir)
    payload = _read_json(output_dir)
    row = next(s for s in payload["surfaces"] if "mixed.json" in s["path"])
    assert row["disposition"] == "OWNER_DECISION_REQUIRED"
    assert row["signal"] == "mixed_scope_approval_packet"


# ---- Summary + schema -----------------------------------------------


def test_run_emits_deploy_safety_field_for_every_surface(tmp_path: Path) -> None:
    """Every row has a deploy_safety field per REVISED-1 §2.2 schema."""
    project_root = _build_project_root(tmp_path)
    (project_root / "Dockerfile").write_text("FROM python:3.14\n", encoding="utf-8")
    (project_root / "groundtruth.db").write_bytes(b"stub")
    output_dir = tmp_path / "output"
    _run_lane(project_root, output_dir)
    payload = _read_json(output_dir)
    assert all("deploy_safety" in s for s in payload["surfaces"])


def test_run_summary_records_secret_material_with_content_read_zero(tmp_path: Path) -> None:
    """Schema-level safety evidence: summary.secret_material_with_content_read == 0."""
    project_root = _build_project_root(tmp_path)
    (project_root / ".env.local").write_text("SECRET=do-not-read\n", encoding="utf-8")
    deploy_dir = project_root / "scripts" / "deploy"
    deploy_dir.mkdir(parents=True)
    (deploy_dir / "_prod_env_vars.txt").write_text("X=Y\n", encoding="utf-8")
    output_dir = tmp_path / "output"
    _run_lane(project_root, output_dir)
    payload = _read_json(output_dir)
    assert payload["summary"]["secret_material_count"] >= 2
    assert payload["summary"]["secret_material_with_content_read"] == 0


# ---- Output artifacts -----------------------------------------------


def test_run_writes_production_effects_map_with_four_disposition_sections(tmp_path: Path) -> None:
    project_root = _build_project_root(tmp_path)
    (project_root / "Dockerfile").write_text("FROM python:3.14\n", encoding="utf-8")
    output_dir = tmp_path / "output"
    _run_lane(project_root, output_dir)
    preview = (output_dir / "production_effects" / "production-effects-map.md").read_text(encoding="utf-8")
    assert "## DO_NOT_MOVE" in preview
    assert "## MOVE" in preview
    assert "## KEEP" in preview
    assert "## OWNER_DECISION_REQUIRED" in preview
    assert "## Deploy-Blocking Surfaces" in preview


def test_run_writes_result_json_on_ok_path(tmp_path: Path) -> None:
    project_root = _build_project_root(tmp_path)
    output_dir = tmp_path / "output"
    result = _run_lane(project_root, output_dir)
    assert result["status"] == "ok"
    assert (output_dir / "production_effects" / "result.json").exists()


# ---- Codex -008 Finding 1: directory existence ------------------------


def test_run_reports_directory_surfaces_as_existing(tmp_path: Path) -> None:
    """Per Codex -008 Finding 1: real directory surfaces must surface as
    exists=True with is_directory=True, not exists=False.

    Tests .shopify/deploy-bundle, .groundtruth/wrap-scan, .groundtruth/session.
    """
    project_root = _build_project_root(tmp_path)
    (project_root / ".shopify" / "deploy-bundle").mkdir(parents=True)
    (project_root / ".groundtruth" / "wrap-scan").mkdir(parents=True)
    (project_root / ".groundtruth" / "session").mkdir(parents=True)
    output_dir = tmp_path / "output"
    _run_lane(project_root, output_dir)
    payload = _read_json(output_dir)
    for path_suffix in (".shopify/deploy-bundle", ".groundtruth/wrap-scan", ".groundtruth/session"):
        row = next(s for s in payload["surfaces"] if s["path"] == path_suffix)
        assert row["exists"] is True, f"Directory {path_suffix} reported as absent"
        assert row["is_directory"] is True
        assert row["is_file"] is False
        assert row["content_read"] is False  # directories never content-read


def test_run_reports_file_surfaces_with_is_file_true(tmp_path: Path) -> None:
    """Files distinguishable from directories via is_file/is_directory."""
    project_root = _build_project_root(tmp_path)
    (project_root / "Dockerfile").write_text("FROM python:3.14\n", encoding="utf-8")
    output_dir = tmp_path / "output"
    _run_lane(project_root, output_dir)
    payload = _read_json(output_dir)
    row = next(s for s in payload["surfaces"] if s["path"] == "Dockerfile")
    assert row["exists"] is True
    assert row["is_file"] is True
    assert row["is_directory"] is False


# ---- Codex -008 Finding 2: live approval schema ----------------------


def test_run_classifies_live_schema_gtkb_artifact_id_as_keep(tmp_path: Path) -> None:
    """Live schema: artifact_id starts with GTKB- → KEEP framework."""
    project_root = _build_project_root(tmp_path)
    approvals = project_root / ".groundtruth" / "formal-artifact-approvals"
    approvals.mkdir(parents=True)
    (approvals / "gov-approval.json").write_text(
        json.dumps(
            {
                "artifact_type": "governance",
                "artifact_id": "GTKB-GOV-011-IMPLEMENTATION-VERIFICATION",
                "source_ref": "owner_conversation:2026-04-20-gtkb-gov-011-proceed",
            }
        ),
        encoding="utf-8",
    )
    output_dir = tmp_path / "output"
    _run_lane(project_root, output_dir)
    payload = _read_json(output_dir)
    row = next(s for s in payload["surfaces"] if "gov-approval.json" in s["path"])
    assert row["disposition"] == "KEEP"
    assert row["signal"] == "framework_approval_packet_gtkb_prefix"
    assert row["classification_basis"] == "live_schema_top_level_artifact"
    assert row["artifact_id"] == "GTKB-GOV-011-IMPLEMENTATION-VERIFICATION"
    assert row["artifact_type"] == "governance"


def test_run_classifies_live_schema_governance_artifact_type_as_keep(tmp_path: Path) -> None:
    """Live schema: artifact_type=governance with no GTKB-/AR- prefix → KEEP."""
    project_root = _build_project_root(tmp_path)
    approvals = project_root / ".groundtruth" / "formal-artifact-approvals"
    approvals.mkdir(parents=True)
    (approvals / "gov-batch.json").write_text(
        json.dumps(
            {
                "artifact_type": "governance",
                "artifact_id": "ARTIFACT-ORIENTED-GOVERNANCE-BATCH-2026-04-22",
                "source_ref": "owner_conversation:2026-04-22",
            }
        ),
        encoding="utf-8",
    )
    output_dir = tmp_path / "output"
    _run_lane(project_root, output_dir)
    payload = _read_json(output_dir)
    row = next(s for s in payload["surfaces"] if "gov-batch.json" in s["path"])
    assert row["disposition"] == "KEEP"
    assert row["signal"] == "framework_approval_packet_artifact_type_governance"


def test_run_classifies_live_schema_deliberation_with_framework_source_ref(tmp_path: Path) -> None:
    """Live schema: DELIB-* with framework source_ref → KEEP."""
    project_root = _build_project_root(tmp_path)
    approvals = project_root / ".groundtruth" / "formal-artifact-approvals"
    approvals.mkdir(parents=True)
    (approvals / "delib.json").write_text(
        json.dumps(
            {
                "artifact_type": "deliberation",
                "artifact_id": "DELIB-0836",
                "source_ref": "owner_conversation:2026-04-20-codex-hook-windows-limitation-groundtruth_kb",
            }
        ),
        encoding="utf-8",
    )
    output_dir = tmp_path / "output"
    _run_lane(project_root, output_dir)
    payload = _read_json(output_dir)
    row = next(s for s in payload["surfaces"] if "delib.json" in s["path"])
    assert row["disposition"] == "KEEP"
    assert row["signal"] == "framework_deliberation_approval_packet"


def test_run_classifies_live_schema_deliberation_with_adopter_source_ref(tmp_path: Path) -> None:
    """Live schema: DELIB-* with agent_red source_ref → MOVE."""
    project_root = _build_project_root(tmp_path)
    approvals = project_root / ".groundtruth" / "formal-artifact-approvals"
    approvals.mkdir(parents=True)
    (approvals / "ar-delib.json").write_text(
        json.dumps(
            {
                "artifact_type": "deliberation",
                "artifact_id": "DELIB-0900",
                "source_ref": "owner_conversation:2026-04-20-agent-red-shopify-rollout",
            }
        ),
        encoding="utf-8",
    )
    output_dir = tmp_path / "output"
    _run_lane(project_root, output_dir)
    payload = _read_json(output_dir)
    row = next(s for s in payload["surfaces"] if "ar-delib.json" in s["path"])
    assert row["disposition"] == "MOVE"
    assert row["signal"] == "adopter_deliberation_approval_packet"


def test_run_classifies_live_schema_ambiguous_deliberation_as_owner_decision(tmp_path: Path) -> None:
    """Live schema: DELIB-* with no clear adopter/framework signal → owner decision."""
    project_root = _build_project_root(tmp_path)
    approvals = project_root / ".groundtruth" / "formal-artifact-approvals"
    approvals.mkdir(parents=True)
    (approvals / "ambiguous.json").write_text(
        json.dumps(
            {
                "artifact_type": "deliberation",
                "artifact_id": "DELIB-0500",
                "source_ref": "owner_conversation:2026-04-15-process-improvement",
            }
        ),
        encoding="utf-8",
    )
    output_dir = tmp_path / "output"
    _run_lane(project_root, output_dir)
    payload = _read_json(output_dir)
    row = next(s for s in payload["surfaces"] if "ambiguous.json" in s["path"])
    assert row["disposition"] == "OWNER_DECISION_REQUIRED"
    assert row["signal"] == "deliberation_approval_packet_subject_ambiguous"


def test_run_classifies_live_schema_ar_artifact_id_as_move(tmp_path: Path) -> None:
    """Live schema: artifact_id starts with AR- → MOVE adopter."""
    project_root = _build_project_root(tmp_path)
    approvals = project_root / ".groundtruth" / "formal-artifact-approvals"
    approvals.mkdir(parents=True)
    (approvals / "ar-approval.json").write_text(
        json.dumps(
            {
                "artifact_type": "specification",
                "artifact_id": "AR-DASH-001",
                "source_ref": "owner_conversation:agent-red-dashboard",
            }
        ),
        encoding="utf-8",
    )
    output_dir = tmp_path / "output"
    _run_lane(project_root, output_dir)
    payload = _read_json(output_dir)
    row = next(s for s in payload["surfaces"] if "ar-approval.json" in s["path"])
    assert row["disposition"] == "MOVE"
    assert row["signal"] == "adopter_approval_packet_ar_prefix"
