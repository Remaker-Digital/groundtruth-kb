"""Tests for the deterministic ``gt bridge propose`` draft CLI."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest
from click.testing import CliRunner

from groundtruth_kb.bridge.proposal_autoload import (
    auto_prior_delibs,
    auto_project_metadata,
    auto_spec_links,
)
from groundtruth_kb.cli import main
from groundtruth_kb.cli_bridge_propose import build_propose_context, render_proposal_draft
from groundtruth_kb.db import KnowledgeDB

WI_ID = "WI-3318"
PROJECT_ID = "PROJECT-GTKB-DETERMINISTIC-SERVICES-TEST"
AUTH_ID = "PAUTH-GT-BRIDGE-PROPOSE-CLI"
DELIB_ID = "DELIB-GT-BRIDGE-PROPOSE-CLI"


def _config_path(project_dir: Path) -> Path:
    return project_dir / "groundtruth.toml"


def _seed_project(project_dir: Path) -> None:
    db = KnowledgeDB(db_path=project_dir / "groundtruth.db")
    try:
        db.insert_spec(
            id="SPEC-CLI-001",
            title="CLI source spec",
            status="specified",
            changed_by="test",
            change_reason="seed spec",
        )
        db.insert_deliberation(
            id=DELIB_ID,
            source_type="owner_conversation",
            title="Owner approved gt bridge propose CLI",
            summary=f"Owner approved deterministic bridge proposal scaffolding for {WI_ID}.",
            content=f"{WI_ID} approved for deterministic bridge proposal scaffolding.",
            changed_by="test",
            change_reason="seed owner decision",
        )
        db.insert_project("Deterministic Services", "test", "seed project", id=PROJECT_ID)
        db.insert_work_item(
            id=WI_ID,
            title="gt bridge propose CLI",
            description="Build deterministic bridge proposal scaffolding.",
            origin="new",
            component="developer_tooling",
            source_spec_id="SPEC-CLI-001",
            resolution_status="open",
            priority="P1",
            changed_by="test",
            change_reason="seed work item",
            related_spec_ids_at_creation='["SPEC-RELATED-001"]',
        )
        db.link_project_work_item(PROJECT_ID, WI_ID, "test", "link work item")
        db.insert_project_authorization(
            PROJECT_ID,
            "gt bridge propose CLI",
            DELIB_ID,
            "Implement deterministic bridge proposal scaffolding.",
            "test",
            "seed authorization",
            id=AUTH_ID,
            included_work_item_ids=[WI_ID],
            included_spec_ids=["SPEC-CLI-001"],
        )
    finally:
        db.close()


def _runner_result(project_dir: Path, *args: str):
    return CliRunner().invoke(main, ["--config", str(_config_path(project_dir)), *args])


def _context(project_dir: Path, kind: str = "implementation") -> dict:
    db = KnowledgeDB(db_path=project_dir / "groundtruth.db")
    try:
        return build_propose_context(
            db,
            project_dir,
            kind=kind,
            wi_id=WI_ID,
            slug="gtkb-test-bridge-propose",
            target_paths=("groundtruth-kb/src/groundtruth_kb/cli.py",),
            add_specs=("SPEC-EXTRA-001",),
        )
    finally:
        db.close()


def test_auto_project_metadata_active_auth(project_dir: Path) -> None:
    _seed_project(project_dir)
    db = KnowledgeDB(db_path=project_dir / "groundtruth.db")
    try:
        metadata = auto_project_metadata(db, WI_ID)
    finally:
        db.close()

    assert metadata["project_authorization_id"] == AUTH_ID
    assert metadata["project_id"] == PROJECT_ID
    assert metadata["work_item_title"] == "gt bridge propose CLI"


def test_auto_spec_links_cross_cutting(project_dir: Path) -> None:
    _seed_project(project_dir)
    db = KnowledgeDB(db_path=project_dir / "groundtruth.db")
    try:
        specs = auto_spec_links(
            db,
            project_dir,
            WI_ID,
            "implementation",
            ("groundtruth-kb/src/groundtruth_kb/cli.py",),
            ("SPEC-EXTRA-001",),
        )
    finally:
        db.close()

    assert "SPEC-CLI-001" in specs
    assert "SPEC-RELATED-001" in specs
    assert "GOV-FILE-BRIDGE-AUTHORITY-001" in specs
    assert "DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001" in specs
    assert "SPEC-EXTRA-001" in specs


def test_implementation_template_renders(project_dir: Path) -> None:
    _seed_project(project_dir)
    rendered = render_proposal_draft("implementation", _context(project_dir))
    assert "# Implementation Proposal - gt bridge propose CLI" in rendered
    assert f"Project Authorization: {AUTH_ID}" in rendered
    assert "## Specification Links" in rendered
    assert "${claim}" in rendered


def test_defect_fix_template_renders(project_dir: Path) -> None:
    _seed_project(project_dir)
    rendered = render_proposal_draft("defect-fix", _context(project_dir, "defect-fix"))
    assert "# Defect-Fix Proposal - gt bridge propose CLI" in rendered
    assert "## Defect / Reproduction" in rendered


def test_scoping_template_renders(project_dir: Path) -> None:
    _seed_project(project_dir)
    rendered = render_proposal_draft("scoping", _context(project_dir, "scoping"))
    assert "# Scoping Proposal - gt bridge propose CLI" in rendered
    assert "## Scope Boundary" in rendered


def test_advisory_disposition_template_renders(project_dir: Path) -> None:
    _seed_project(project_dir)
    rendered = render_proposal_draft("advisory-disposition", _context(project_dir, "advisory-disposition"))
    assert "# Advisory-Disposition Proposal - gt bridge propose CLI" in rendered
    assert "## Advisory Disposition" in rendered


def test_retirement_template_renders(project_dir: Path) -> None:
    _seed_project(project_dir)
    rendered = render_proposal_draft("retirement", _context(project_dir, "retirement"))
    assert "# Retirement Proposal - gt bridge propose CLI" in rendered
    assert "## Retirement Rationale" in rendered


def test_umbrella_template_renders(project_dir: Path) -> None:
    _seed_project(project_dir)
    rendered = render_proposal_draft("umbrella", _context(project_dir, "umbrella"))
    assert "# Umbrella Proposal - gt bridge propose CLI" in rendered
    assert "## Umbrella Inventory" in rendered


def test_template_emits_spec_to_test_skeleton(project_dir: Path) -> None:
    _seed_project(project_dir)
    rendered = render_proposal_draft("implementation", _context(project_dir))
    assert "## Specification-Derived Verification Plan" in rendered
    assert "${verification_plan_table}" in rendered


def test_cli_arg_validation(project_dir: Path) -> None:
    _seed_project(project_dir)
    result = _runner_result(
        project_dir,
        "bridge",
        "propose",
        "--kind",
        "unknown",
        "--wi",
        WI_ID,
        "--slug",
        "gtkb-test",
    )
    assert result.exit_code == 2
    assert "Invalid value for '--kind'" in result.output


def test_missing_wi_clear_error(project_dir: Path) -> None:
    _seed_project(project_dir)
    result = _runner_result(
        project_dir,
        "bridge",
        "propose",
        "--kind",
        "implementation",
        "--wi",
        "WI-MISSING",
        "--slug",
        "gtkb-test",
        "--dry-run",
    )
    assert result.exit_code == 1
    assert "Work item not found: WI-MISSING" in result.output


def test_cli_dry_run_no_write(project_dir: Path) -> None:
    _seed_project(project_dir)
    result = _runner_result(
        project_dir,
        "bridge",
        "propose",
        "--kind",
        "implementation",
        "--wi",
        WI_ID,
        "--slug",
        "gtkb-test-bridge-propose",
        "--target-path",
        "groundtruth-kb/src/groundtruth_kb/cli.py",
        "--dry-run",
    )
    assert result.exit_code == 0, result.output
    assert "# Implementation Proposal - gt bridge propose CLI" in result.output
    assert not (project_dir / ".gtkb-state" / "bridge-propose-drafts").exists()


def test_cli_draft_path_in_root(project_dir: Path) -> None:
    _seed_project(project_dir)
    result = _runner_result(
        project_dir,
        "bridge",
        "propose",
        "--kind",
        "implementation",
        "--wi",
        WI_ID,
        "--slug",
        "gtkb-test-bridge-propose",
        "--target-path",
        "groundtruth-kb/src/groundtruth_kb/cli.py",
    )
    assert result.exit_code == 0, result.output
    draft = project_dir / ".gtkb-state" / "bridge-propose-drafts" / "gtkb-test-bridge-propose-001.md"
    assert draft.is_file()
    assert draft.resolve().is_relative_to(project_dir.resolve())
    assert "NON-DISPATCHABLE" in result.output


def test_cli_refuses_overwrite(project_dir: Path) -> None:
    _seed_project(project_dir)
    draft = project_dir / ".gtkb-state" / "bridge-propose-drafts" / "gtkb-test-bridge-propose-001.md"
    draft.parent.mkdir(parents=True)
    draft.write_text("existing", encoding="utf-8")
    result = _runner_result(
        project_dir,
        "bridge",
        "propose",
        "--kind",
        "implementation",
        "--wi",
        WI_ID,
        "--slug",
        "gtkb-test-bridge-propose",
    )
    assert result.exit_code == 1
    assert "Refusing to overwrite" in result.output
    assert draft.read_text(encoding="utf-8") == "existing"


def test_cli_does_not_touch_bridge_dir(project_dir: Path) -> None:
    _seed_project(project_dir)
    bridge_dir = project_dir / "bridge"
    bridge_dir.mkdir()
    index = bridge_dir / "INDEX.md"
    index.write_text("# Bridge Index\n", encoding="utf-8")
    result = _runner_result(
        project_dir,
        "bridge",
        "propose",
        "--kind",
        "implementation",
        "--wi",
        WI_ID,
        "--slug",
        "gtkb-test-bridge-propose",
        "--target-path",
        "groundtruth-kb/src/groundtruth_kb/cli.py",
    )
    assert result.exit_code == 0, result.output
    assert index.read_text(encoding="utf-8") == "# Bridge Index\n"
    assert not (bridge_dir / "gtkb-test-bridge-propose-001.md").exists()


def test_cli_bridge_propose_no_optional_deps(project_dir: Path) -> None:
    _seed_project(project_dir)
    for source in (
        Path("src/groundtruth_kb/cli_bridge_propose.py"),
        Path("src/groundtruth_kb/bridge/proposal_autoload.py"),
    ):
        text = (Path(__file__).parents[1] / source).read_text(encoding="utf-8")
        assert "import jinja2" not in text
        assert "import chromadb" not in text

    help_result = _runner_result(project_dir, "bridge", "propose", "--help")
    assert help_result.exit_code == 0, help_result.output
    dry_run_result = _runner_result(
        project_dir,
        "bridge",
        "propose",
        "--kind",
        "implementation",
        "--wi",
        WI_ID,
        "--slug",
        "gtkb-test-bridge-propose",
        "--dry-run",
    )
    assert dry_run_result.exit_code == 0, dry_run_result.output


def test_cli_bridge_propose_help_resolves() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "groundtruth_kb", "bridge", "propose", "--help"],
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert "Emit a deterministic, non-dispatchable bridge proposal draft." in result.stdout


def test_auto_prior_delibs_fallback_safe(project_dir: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _seed_project(project_dir)
    db = KnowledgeDB(db_path=project_dir / "groundtruth.db")

    def fail_search(*_args, **_kwargs):
        raise RuntimeError("optional search unavailable")

    monkeypatch.setattr(db, "search_deliberations", fail_search)
    try:
        assert auto_prior_delibs(db, WI_ID, "gtkb-test-bridge-propose") == []
    finally:
        db.close()
