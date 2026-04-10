"""
Desktop bootstrap helpers for GroundTruth projects.

Copyright (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC.
All rights reserved. Licensed under AGPL-3.0-or-later.
"""

from __future__ import annotations

import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path

from groundtruth_kb import get_templates_dir
from groundtruth_kb.db import KnowledgeDB
from groundtruth_kb.seed import load_example_seeds, load_governance_seeds

DEFAULT_PROJECT_GITIGNORE = """\
__pycache__/
*.pyc
.pytest_cache/
.ruff_cache/
.venv/
groundtruth.db
"""


@dataclass(frozen=True)
class DesktopBootstrapOptions:
    project_name: str
    owner: str
    project_type: str
    target_dir: Path
    brand_mark: str = "GT"
    brand_color: str = "#2563eb"
    copyright_notice: str = ""
    include_ci: bool = True
    init_git: bool = False
    seed_example: bool = True


def bootstrap_desktop_project(options: DesktopBootstrapOptions) -> Path:
    """Create a ready-to-edit GroundTruth project scaffold."""
    target = options.target_dir.resolve()
    _validate_target(target)

    target.mkdir(parents=True, exist_ok=True)
    copyright_notice = options.copyright_notice or _default_copyright(options.owner)
    _write_groundtruth_toml(
        target=target,
        project_name=options.project_name,
        brand_mark=options.brand_mark,
        brand_color=options.brand_color,
        legal_footer=copyright_notice,
    )
    _initialize_database(target)
    _write_project_gitignore(target)
    _copy_templates(target, include_ci=options.include_ci)
    _render_project_templates(
        target=target,
        project_name=options.project_name,
        project_type=options.project_type,
        owner=options.owner,
        copyright_notice=copyright_notice,
    )
    _seed_database(target, include_example=options.seed_example)
    if options.init_git:
        _initialize_git_repo(target)
    return target


def _validate_target(target: Path) -> None:
    if target.exists() and not target.is_dir():
        raise ValueError(f"Target path is not a directory: {target}")
    if target.exists() and any(target.iterdir()):
        raise ValueError(f"Target directory is not empty: {target}")


def _default_copyright(owner: str) -> str:
    return f"Copyright 2026 {owner}. All rights reserved."


def _write_groundtruth_toml(
    *,
    target: Path,
    project_name: str,
    brand_mark: str,
    brand_color: str,
    legal_footer: str,
) -> None:
    toml_path = target / "groundtruth.toml"
    escaped_project_name = _toml_escape(project_name)
    escaped_brand_mark = _toml_escape(brand_mark)
    escaped_brand_color = _toml_escape(brand_color)
    escaped_footer = _toml_escape(legal_footer)
    toml_content = f"""\
# GroundTruth KB project configuration
# Docs: https://github.com/Remaker-Digital/groundtruth-kb

[groundtruth]
db_path = "./groundtruth.db"
project_root = "."
app_title = "{escaped_project_name}"
brand_mark = "{escaped_brand_mark}"
brand_color = "{escaped_brand_color}"
# logo_url = ""
legal_footer = "{escaped_footer}"

[gates]
# Plug-in governance gates (dotted import paths)
# plugins = ["my_package.gates:MyCustomGate"]
"""
    toml_path.write_text(toml_content, encoding="utf-8")


def _toml_escape(value: str) -> str:
    return value.replace("\\", "\\\\").replace('"', '\\"')


def _initialize_database(target: Path) -> None:
    db = KnowledgeDB(db_path=target / "groundtruth.db")
    db.close()


def _write_project_gitignore(target: Path) -> None:
    gitignore_path = target / ".gitignore"
    if not gitignore_path.exists():
        gitignore_path.write_text(DEFAULT_PROJECT_GITIGNORE, encoding="utf-8")


def _copy_templates(target: Path, *, include_ci: bool) -> None:
    templates_dir = get_templates_dir()
    for template_name in ("CLAUDE.md", "MEMORY.md", "BRIDGE-INVENTORY.md"):
        shutil.copy2(templates_dir / template_name, target / template_name)

    hooks_target = target / ".claude" / "hooks"
    hooks_target.mkdir(parents=True, exist_ok=True)
    for source in (templates_dir / "hooks").glob("*.py"):
        shutil.copy2(source, hooks_target / source.name)

    rules_target = target / ".claude" / "rules"
    rules_target.mkdir(parents=True, exist_ok=True)
    for source in (templates_dir / "rules").glob("*.md"):
        shutil.copy2(source, rules_target / source.name)

    # Developer config files (from templates/project/)
    project_templates = templates_dir / "project"
    for name in (".editorconfig", "Makefile", ".pre-commit-config.yaml"):
        src = project_templates / name
        if src.exists():
            shutil.copy2(src, target / name)

    if include_ci:
        workflows_target = target / ".github" / "workflows"
        workflows_target.mkdir(parents=True, exist_ok=True)
        for source in (templates_dir / "ci").glob("*.yml"):
            shutil.copy2(source, workflows_target / source.name)


def _render_project_templates(
    *,
    target: Path,
    project_name: str,
    project_type: str,
    owner: str,
    copyright_notice: str,
) -> None:
    replacements = {
        "{{PROJECT_NAME}}": project_name,
        "{{PROJECT_TYPE}}": project_type,
        "{{OWNER}}": owner,
        "{{COPYRIGHT}}": copyright_notice,
        "{{VERSION}}": "0.1.0",
        "{{ENVIRONMENT_DESCRIPTION}}": "Local workstation bootstrap",
        "{{TEST_STATUS}}": "Not run yet",
        "{{BRIDGE_INVENTORY_PATH_OR_NA}}": "BRIDGE-INVENTORY.md",
        "{{AUTOMATION_SUMMARY_OR_NA}}": "None configured yet",
        "{{OPS_HEALTH_NOTES}}": "Bootstrap complete. Update after the first working session.",
        "{{AGENT_OR_PROCESS_1}}": "builder-agent",
        "{{RESPONSIBILITY}}": "Implementation, specs, and project bootstrap",
        "{{REVIEWER}}": "review-agent or owner",
        "{{NOTES}}": "Replace with your actual collaboration topology.",
        "{{PATH_TO_ENTRYPOINT}}": "TBD",
        "{{WHAT_IT_DOES}}": "Document your bridge or automation entrypoint here.",
        "{{HOW_IT_RUNS}}": "Manual start or scheduled run",
        "{{OTHER_PATH}}": "TBD",
        "{{KIND}}": "TBD",
        "{{PURPOSE}}": "Replace with the actual purpose for this control surface.",
        "{{WHEN_TO_UPDATE}}": "Whenever the runtime or coordination rules change.",
        "{{AUTOMATION_NAME}}": "example-recurring-task",
        "{{SCHEDULE}}": "Not configured",
        "{{EXECUTOR}}": "TBD",
        "{{SOURCE}}": "TBD",
        "{{FAILURE_SIGNAL}}": "TBD",
        "{{ASYNC_OR_TRANSACTIONAL_DESCRIPTION}}": (
            "Document whether your bridge is async message passing or another model."
        ),
        "{{WHEN_MESSAGES_REQUIRE_REPLIES}}": "Document which message types require replies.",
        "{{WHEN_TO_RETRY}}": "Document retry rules and escalation thresholds.",
        "{{STARTUP_OR_LIVENESS_CHECK}}": "Document the startup handshake or health check procedure.",
        "{{WHEN_RESTARTS_ARE_ALLOWED_OR_AVOIDED}}": "Document when restarts are safe, required, or forbidden.",
        "{{ENV_CONFIG_IDS_OR_NOTES}}": "Add KB IDs or notes here.",
        "{{PROCEDURE_IDS_OR_NOTES}}": "Add KB IDs or notes here.",
        "{{DOCUMENT_IDS_OR_NOTES}}": "Add KB IDs or notes here.",
        "{{DATE}}": "TBD",
        "{{FOLLOW_UPS}}": "TBD",
    }

    for relative_path in (
        Path("CLAUDE.md"),
        Path("MEMORY.md"),
        Path("BRIDGE-INVENTORY.md"),
    ):
        path = target / relative_path
        rendered = path.read_text(encoding="utf-8")
        for placeholder, value in replacements.items():
            rendered = rendered.replace(placeholder, value)
        path.write_text(rendered, encoding="utf-8")


def _seed_database(target: Path, *, include_example: bool) -> None:
    db = KnowledgeDB(db_path=target / "groundtruth.db")
    try:
        load_governance_seeds(db)
        if include_example:
            load_example_seeds(db)
    finally:
        db.close()


def _initialize_git_repo(target: Path) -> None:
    subprocess.run(["git", "init"], cwd=target, check=True, capture_output=True, text=True)
    subprocess.run(["git", "branch", "-m", "main"], cwd=target, check=True, capture_output=True, text=True)


def bootstrap_summary(target: Path, *, include_ci: bool, init_git: bool, seed_example: bool) -> str:
    summary_lines = [
        f"Desktop bootstrap created in {target}",
        "Included:",
        "  - groundtruth.toml",
        "  - groundtruth.db",
        "  - CLAUDE.md, MEMORY.md, BRIDGE-INVENTORY.md",
        "  - .claude/hooks and .claude/rules",
        f"  - CI workflows: {'yes' if include_ci else 'no'}",
        f"  - Git initialized: {'yes' if init_git else 'no'}",
        f"  - Example seed data: {'yes' if seed_example else 'no'}",
        "",
        "Next steps:",
        f"  1. cd {target}",
        "  2. Open CLAUDE.md, MEMORY.md, and BRIDGE-INVENTORY.md and replace the remaining TBD values.",
        "  3. Run `gt --config groundtruth.toml summary`.",
        "  4. Open the project in your editor and start the first session.",
    ]
    return "\n".join(summary_lines)
