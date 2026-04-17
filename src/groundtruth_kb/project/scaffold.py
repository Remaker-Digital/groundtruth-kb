# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Project scaffold engine — ``gt project init`` implementation."""

from __future__ import annotations

import json
import re
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from groundtruth_kb import get_templates_dir
from groundtruth_kb.bootstrap import (
    _default_copyright,
    _initialize_database,
    _initialize_git_repo,
    _seed_database,
    _validate_target,
    _write_groundtruth_toml,
    _write_project_gitignore,
)
from groundtruth_kb.project.managed_registry import (
    FileArtifact,
    GitignorePattern,
    SettingsHookRegistration,
    artifacts_for_scaffold,
)
from groundtruth_kb.project.manifest import ProjectManifest, write_manifest
from groundtruth_kb.project.profiles import ProjectProfile, get_profile
from groundtruth_kb.providers.schema import CLAUDE_CODE, CODEX, AgentProvider, get_provider
from groundtruth_kb.spec_scaffold import SpecScaffoldConfig, scaffold_specs


@dataclass(frozen=True)
class ScaffoldOptions:
    """Options for ``gt project init``.

    Attributes:
        spec_scaffold: Optional :class:`SpecScaffoldConfig`. When provided,
            the newly-initialised KB is populated with generated starter
            specs at ``authority='inferred'``. When ``None`` (the default),
            ``gt project init`` behavior is unchanged and no specs are
            generated — this preserves every pre-F6 caller.
        prime_provider_id: Provider ID for the Prime Builder agent (default: ``"claude-code"``).
        lo_provider_id: Provider ID for the Loyal Opposition agent (default: ``"codex"``).
    """

    project_name: str
    profile: str
    owner: str
    target_dir: Path
    copyright_notice: str = ""
    cloud_provider: str = "none"
    init_git: bool = False
    include_ci: bool = True
    seed_example: bool = True
    brand_mark: str = "GT"
    brand_color: str = "#2563eb"
    spec_scaffold: SpecScaffoldConfig | None = None
    prime_provider_id: str = "claude-code"
    lo_provider_id: str = "codex"
    python_version: str = "3.11"
    integrations: bool = False


def scaffold_project(options: ScaffoldOptions) -> Path:
    """Create a complete project scaffold based on the selected profile."""
    profile = get_profile(options.profile)
    target = options.target_dir.resolve()
    _validate_target(target)
    target.mkdir(parents=True, exist_ok=True)

    copyright_notice = options.copyright_notice or _default_copyright(options.owner)

    # ── Resolve agent providers ───────────────────────────────────────
    prime_provider = get_provider(options.prime_provider_id)
    lo_provider = get_provider(options.lo_provider_id)

    # ── Layer 1: Core KB (same as bootstrap-desktop) ──────────────────
    _write_groundtruth_toml(
        target=target,
        project_name=options.project_name,
        brand_mark=options.brand_mark,
        brand_color=options.brand_color,
        legal_footer=copyright_notice,
    )
    _initialize_database(target)
    _write_project_gitignore(target)

    # ── Base templates (all profiles) ─────────────────────────────────
    _copy_base_templates(target)

    # ── Dual-agent templates ──────────────────────────────────────────
    if profile.includes_bridge:
        _copy_dual_agent_templates(target, project_name=options.project_name)

    # ── Webapp templates ──────────────────────────────────────────────
    if profile.includes_docker:
        _copy_webapp_templates(target, cloud_provider=options.cloud_provider)

    # ── CI workflows ──────────────────────────────────────────────────
    # User flag always wins; profile selects tier, not whether CI is generated.
    include_ci = options.include_ci
    if include_ci:
        _copy_ci_templates(target, profile=profile, options=options)

    # ── dual-agent-webapp stub files ─────────────────────────────────
    if profile.name == "dual-agent-webapp":
        _write_webapp_stubs(target, options=options)

    # ── src/tasks.py stub for all profiles when seed_example=True ────
    if options.seed_example:
        _write_tasks_stub(target)

    # ── Integration files (--integrations flag) ───────────────────────
    if options.integrations:
        _copy_integration_templates(target, options=options)

    # ── Render all placeholders ───────────────────────────────────────
    _render_all_templates(
        target=target,
        project_name=options.project_name,
        owner=options.owner,
        copyright_notice=copyright_notice,
        profile=profile,
        prime_provider=prime_provider,
        lo_provider=lo_provider,
    )

    # ── Seed governance data ──────────────────────────────────────────
    _seed_database(target, include_example=options.seed_example)

    # ── Write project manifest ────────────────────────────────────────
    manifest = ProjectManifest(
        project_name=options.project_name,
        owner=options.owner,
        profile=options.profile,
        copyright_notice=copyright_notice,
        cloud_provider=options.cloud_provider,
    )
    write_manifest(target / "groundtruth.toml", manifest)

    # ── F6: Optional spec scaffold into the freshly-created KB ───────
    # Runs AFTER _seed_database so the governance seed is already in place;
    # scaffold_specs() skips pre-existing handles, so the seed is preserved.
    # Only runs when options.spec_scaffold is set — default gt project init
    # behavior is unchanged.
    if options.spec_scaffold is not None:
        from groundtruth_kb.db import KnowledgeDB

        db = KnowledgeDB(target / "groundtruth.db")
        try:
            scaffold_specs(db, options.spec_scaffold, dry_run=False)
        finally:
            db.close()

    # ── Git init ──────────────────────────────────────────────────────
    if options.init_git:
        _initialize_git_repo(target)

    return target


# ── Template copy helpers ─────────────────────────────────────────────


def _copy_base_templates(target: Path) -> None:
    """Copy base templates for all profiles: CLAUDE.md, MEMORY.md, hooks, rules.

    Hook and rule copies are driven by the managed-artifact registry
    (:func:`artifacts_for_scaffold` with ``"local-only"``) so that the single
    source of truth controls what the base profile receives.
    """
    templates = get_templates_dir()

    for name in ("CLAUDE.md", "MEMORY.md"):
        shutil.copy2(templates / name, target / name)

    # Hooks — registry-driven (initial_profiles contains "local-only" for all 14 hooks).
    hooks_target = target / ".claude" / "hooks"
    hooks_target.mkdir(parents=True, exist_ok=True)
    for artifact in artifacts_for_scaffold("local-only", class_="hook"):
        assert isinstance(artifact, FileArtifact)
        src = templates / artifact.template_path
        if not src.exists():
            continue
        dst = target / artifact.target_path
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)

    # Rules — registry-driven. Base profile only gets rules whose
    # initial_profiles contains "local-only" (currently only prime-builder).
    rules_target = target / ".claude" / "rules"
    rules_target.mkdir(parents=True, exist_ok=True)
    for artifact in artifacts_for_scaffold("local-only", class_="rule"):
        assert isinstance(artifact, FileArtifact)
        src = templates / artifact.template_path
        if not src.exists():
            continue
        dst = target / artifact.target_path
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)

    # Developer config files (from templates/project/)
    project_templates = templates / "project"
    for name in (".editorconfig", "Makefile", ".pre-commit-config.yaml"):
        src = project_templates / name
        if src.exists():
            shutil.copy2(src, target / name)

    # Generate base pyproject sections
    _write_pyproject_sections(target)


def _generate_bridge_index(project_name: str) -> str:
    """Generate the initial bridge/INDEX.md content.

    Args:
        project_name: Human-readable project name used in the header.

    Returns:
        UTF-8 string content for ``bridge/INDEX.md``.
    """
    return """\
# {{PROJECT_NAME}} — File Bridge Index

<!-- This file is the single coordination artifact for the Prime Builder ↔
     Loyal Opposition file bridge. Both agents read and write this file.
     Newest entries are at the top. -->

## Statuses

| Status | Set by | Meaning |
|--------|--------|---------|
| NEW | Prime | Fresh proposal awaiting review |
| REVISED | Prime | Updated proposal after a NO-GO |
| GO | Codex | Proposal approved for implementation |
| NO-GO | Codex | Proposal requires changes before approval |
| VERIFIED | Codex | Post-implementation verification passed |

## Prime Workflow

1. Write proposal as `bridge/{{name}}-001.md`
2. Insert `NEW: bridge/{{name}}-001.md` at the top of this file
3. On GO: implement; on NO-GO: revise and insert REVISED entry

## Codex Workflow

1. Scan this file for NEW or REVISED entries
2. Review the indicated file, write response as next incremented version
3. Insert GO or NO-GO verdict line at the top of that document entry

<!-- Add new document entries below this line -->
"""


def _copy_dual_agent_templates(target: Path, *, project_name: str = "") -> None:
    """Copy dual-agent templates: AGENTS.md, bridge rules, Codex bootstrap."""
    templates = get_templates_dir()

    # BRIDGE-INVENTORY.md
    bi = templates / "BRIDGE-INVENTORY.md"
    if bi.exists():
        shutil.copy2(bi, target / "BRIDGE-INVENTORY.md")

    # File bridge setup prompt
    bridge_prompt = templates / "bridge-os-poller-setup-prompt.md"
    if bridge_prompt.exists():
        shutil.copy2(bridge_prompt, target / "bridge-os-poller-setup-prompt.md")

    # AGENTS.md
    agents_template = templates / "project" / "AGENTS.md"
    if agents_template.exists():
        shutil.copy2(agents_template, target / "AGENTS.md")
    else:
        _write_default_agents_md(target)

    # All rules (bridge-specific) — registry-driven.
    rules_target = target / ".claude" / "rules"
    rules_target.mkdir(parents=True, exist_ok=True)
    for artifact in artifacts_for_scaffold("dual-agent", class_="rule"):
        assert isinstance(artifact, FileArtifact)
        src = templates / artifact.template_path
        if not src.exists():
            continue
        dst = target / artifact.target_path
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)

    # Additional hooks — registry-driven. Already copied by
    # :func:`_copy_base_templates` (initial_profiles is ALL), so this is a
    # no-op for every hook; retained as a defensive guard against a base
    # scaffold failing to populate ``.claude/hooks/`` before this point.
    for artifact in artifacts_for_scaffold("dual-agent", class_="hook"):
        assert isinstance(artifact, FileArtifact)
        dst = target / artifact.target_path
        if dst.exists():
            continue
        src = templates / artifact.template_path
        if not src.exists():
            continue
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)

    # Codex bootstrap documents
    codex_dir = target / "independent-progress-assessments"
    codex_dir.mkdir(parents=True, exist_ok=True)
    (codex_dir / "CODEX-INSIGHT-DROPBOX").mkdir(exist_ok=True)

    codex_src = templates / "project" / "codex-bootstrap"
    if codex_src.exists():
        for src in codex_src.glob("*.md"):
            shutil.copy2(src, codex_dir / src.name)

    # settings.local.json with bridge hooks
    settings_template = templates / "project" / "settings.local.json"
    if settings_template.exists():
        shutil.copy2(settings_template, target / ".claude" / "settings.local.json")

    # settings.json (tracked) — governance hook registration for all 8 hooks
    _write_settings_json(target / ".claude" / "settings.json")

    # .gitignore additions for file bridge automation runtime state
    gi = target / ".gitignore"
    content = gi.read_text(encoding="utf-8") if gi.exists() else ""
    additions = (
        "\n# File bridge automation runtime state\n"
        "independent-progress-assessments/bridge-automation/logs/\n"
        "independent-progress-assessments/bridge-automation/*.lock\n"
        "independent-progress-assessments/bridge-automation/*.tmp\n"
    )
    if "bridge-automation/logs" not in content:
        gi.write_text(content + additions, encoding="utf-8")
        content = gi.read_text(encoding="utf-8")

    # Registry-driven gitignore-pattern additions (currently: ``.claude/hooks/*.log``).
    for artifact in artifacts_for_scaffold("dual-agent", class_="gitignore-pattern"):
        assert isinstance(artifact, GitignorePattern)
        if artifact.pattern in content:
            continue
        addition = f"\n# {artifact.comment}\n{artifact.pattern}\n"
        gi.write_text(content + addition, encoding="utf-8")
        content = gi.read_text(encoding="utf-8")

    # bridge/INDEX.md — the coordination file for the file bridge workflow
    bridge_dir = target / "bridge"
    bridge_dir.mkdir(parents=True, exist_ok=True)
    (bridge_dir / "INDEX.md").write_text(
        _generate_bridge_index(project_name),
        encoding="utf-8",
    )

    # .claude/skills/ — dual-agent-only Phase A skills (decision-capture).
    _copy_skill_templates(target)


def _copy_skill_templates(target: Path) -> None:
    """Copy dual-agent skill templates into ``.claude/skills/``.

    Driven by the managed-artifact registry: every ``skill``-class record whose
    ``initial_profiles`` contains ``dual-agent`` is copied, preserving subdirectory
    structure (e.g., ``decision-capture/helpers/record_decision.py``). Missing
    template files are silently skipped so a partially-populated template tree
    does not break scaffold.
    """
    templates = get_templates_dir()

    for artifact in artifacts_for_scaffold("dual-agent", class_="skill"):
        assert isinstance(artifact, FileArtifact)
        src = templates / artifact.template_path
        if not src.exists():
            continue
        dst = target / artifact.target_path
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)


def _write_settings_json(settings_path: Path) -> None:
    """Write tracked .claude/settings.json with all governance and feature hooks.

    Registration matrix is driven by the managed-artifact registry — every
    ``settings-hook-registration`` record whose ``initial_profiles`` contains
    ``dual-agent`` is emitted, preserving the per-event ordering given by the
    registry's record sequence. Uses the nested hook event → matcher group →
    handler schema expected by current Claude Code versions. The file is tracked
    in git so all hooks are inherited by every worktree and fresh clone.
    """
    hooks_dir = ".claude/hooks"
    # Preserve registry order; build per-event groups in record order so the
    # output matches the event-to-hook matrix asserted by tests.
    event_order: list[str] = []
    per_event: dict[str, list[dict[str, Any]]] = {}
    for artifact in artifacts_for_scaffold("dual-agent", class_="settings-hook-registration"):
        assert isinstance(artifact, SettingsHookRegistration)
        event = artifact.event
        if event not in per_event:
            per_event[event] = []
            event_order.append(event)
        per_event[event].append(
            {"hooks": [{"type": "command", "command": f"python {hooks_dir}/{artifact.hook_filename}"}]}
        )

    content: dict[str, Any] = {"hooks": {event: per_event[event] for event in event_order}}
    settings_path.parent.mkdir(parents=True, exist_ok=True)
    settings_path.write_text(json.dumps(content, indent=2) + "\n", encoding="utf-8")


def _copy_webapp_templates(target: Path, *, cloud_provider: str) -> None:
    """Copy webapp templates: Dockerfile, docker-compose, terraform, .env.example."""
    templates = get_templates_dir()

    # Dockerfile
    df = templates / "project" / "Dockerfile"
    if df.exists():
        shutil.copy2(df, target / "Dockerfile")
    else:
        _write_default_dockerfile(target)

    # docker-compose.yml
    dc = templates / "project" / "docker-compose.yml"
    if dc.exists():
        shutil.copy2(dc, target / "docker-compose.yml")
    else:
        _write_default_docker_compose(target)

    # .env.example
    env = templates / "project" / "env.example"
    if env.exists():
        shutil.copy2(env, target / ".env.example")
    else:
        _write_default_env_example(target)

    # Terraform stubs
    if cloud_provider != "none":
        infra = target / "infrastructure" / "terraform"
        infra.mkdir(parents=True, exist_ok=True)
        tf_src = templates / "infrastructure" / "terraform"
        if tf_src.exists():
            for src in tf_src.glob("*.tf"):
                shutil.copy2(src, infra / src.name)
        else:
            _write_default_terraform(infra, cloud_provider)


def _package_name_slug(project_name: str) -> str:
    """Convert *project_name* to a slug suitable for use as a Python package/Docker image name.

    Args:
        project_name: Human-readable project name (may contain spaces, caps, etc.)

    Returns:
        Lowercase kebab-case slug with only alphanumeric characters and hyphens.
    """
    return re.sub(r"[^a-z0-9]+", "-", project_name.lower()).strip("-")


def _ci_tier(profile: ProjectProfile) -> str:
    """Select the CI template tier for *profile*.

    Tier selection:
    - ``local-only``: ``includes_ci=False``, ``includes_bridge=False`` → ``minimal``
    - ``dual-agent``: ``includes_ci=False``, ``includes_bridge=True`` → ``standard``
    - ``dual-agent-webapp``: ``includes_ci=True``, ``includes_bridge=True`` → ``full``
    """
    if profile.includes_ci and profile.includes_bridge:
        return "full"
    if profile.includes_bridge:
        return "standard"
    return "minimal"


def _copy_ci_templates(target: Path, *, profile: ProjectProfile, options: ScaffoldOptions) -> None:
    """Copy CI/CD workflow templates for the profile-selected tier.

    Applies ``{{PACKAGE_NAME}}`` and ``{{PYTHON_VERSION}}`` placeholder
    substitution in the copied files.
    """
    templates = get_templates_dir()
    tier = _ci_tier(profile)
    tier_dir = templates / "ci" / tier
    workflows = target / ".github" / "workflows"
    workflows.mkdir(parents=True, exist_ok=True)

    pkg_slug = _package_name_slug(options.project_name)
    py_ver = options.python_version

    for src in tier_dir.glob("*.yml"):
        dest = workflows / src.name
        content = src.read_text(encoding="utf-8")
        content = content.replace("{{PACKAGE_NAME}}", pkg_slug)
        content = content.replace("{{PYTHON_VERSION}}", py_ver)
        dest.write_text(content, encoding="utf-8")


# ── Rendering ─────────────────────────────────────────────────────────


def _render_all_templates(
    *,
    target: Path,
    project_name: str,
    owner: str,
    copyright_notice: str,
    profile: ProjectProfile,
    prime_provider: AgentProvider | None = None,
    lo_provider: AgentProvider | None = None,
) -> None:
    """Replace all {{PLACEHOLDER}} values in rendered files."""
    _prime = prime_provider or CLAUDE_CODE
    _lo = lo_provider or CODEX
    replacements = {
        "{{PROJECT_NAME}}": project_name,
        "{{PROJECT_TYPE}}": f"{profile.display_name} project",
        "{{OWNER}}": owner,
        "{{COPYRIGHT}}": copyright_notice,
        "{{VERSION}}": "0.1.0",
        "{{PROFILE}}": profile.name,
        "{{ENVIRONMENT_DESCRIPTION}}": "Local workstation bootstrap",
        "{{TEST_STATUS}}": "Not run yet",
        "{{BRIDGE_INVENTORY_PATH_OR_NA}}": ("BRIDGE-INVENTORY.md" if profile.includes_bridge else "N/A"),
        "{{AUTOMATION_SUMMARY_OR_NA}}": (
            "File bridge inventory and setup prompt included; configure OS pollers per project"
            if profile.includes_bridge
            else "None configured yet"
        ),
        "{{OPS_HEALTH_NOTES}}": "Bootstrap complete. Update after the first working session.",
        "{{AGENT_OR_PROCESS_1}}": ("prime-builder" if profile.includes_bridge else "builder-agent"),
        "{{RESPONSIBILITY}}": "Implementation, specs, and project bootstrap",
        "{{REVIEWER}}": ("codex (Loyal Opposition)" if profile.includes_bridge else "owner"),
        "{{NOTES}}": "Replace with your actual collaboration topology.",
        "{{PATH_TO_ENTRYPOINT}}": ("bridge/INDEX.md + project-owned OS pollers" if profile.includes_bridge else "TBD"),
        "{{WHAT_IT_DOES}}": (
            "File bridge queue for Prime Builder and Loyal Opposition review handoffs"
            if profile.includes_bridge
            else "Document your bridge or automation entrypoint here."
        ),
        "{{HOW_IT_RUNS}}": (
            "OS scheduler invokes project-owned scanner scripts"
            if profile.includes_bridge
            else "Manual start or scheduled run"
        ),
        "{{OTHER_PATH}}": "TBD",
        "{{KIND}}": "TBD",
        "{{PURPOSE}}": "Replace with the actual purpose for this control surface.",
        "{{WHEN_TO_UPDATE}}": "Whenever the runtime or coordination rules change.",
        "{{AUTOMATION_NAME}}": "file-bridge-os-pollers",
        "{{SCHEDULE}}": "Project-defined OS scheduler interval",
        "{{EXECUTOR}}": "claude -p / codex exec via project-owned scanner scripts",
        "{{SOURCE}}": "bridge-os-poller-setup-prompt.md and BRIDGE-INVENTORY.md",
        "{{FAILURE_SIGNAL}}": "No recent scan logs or stale actionable bridge entries",
        "{{ASYNC_OR_TRANSACTIONAL_DESCRIPTION}}": (
            "File-based latest-status queue in bridge/INDEX.md. Entries are newest-first."
        ),
        "{{WHEN_MESSAGES_REQUIRE_REPLIES}}": (
            "Latest NEW/REVISED entries require Loyal Opposition verdicts; latest GO/NO-GO entries "
            "require Prime responses."
        ),
        "{{WHEN_TO_RETRY}}": "Scheduled re-scan after the next interval; lock files prevent overlapping runs.",
        "{{STARTUP_OR_LIVENESS_CHECK}}": ("Read bridge/INDEX.md, scheduler state, and recent scan logs."),
        "{{WHEN_RESTARTS_ARE_ALLOWED_OR_AVOIDED}}": (
            "No long-running bridge process is required; update scheduled tasks after scanner or prompt changes."
        ),
        "{{ENV_CONFIG_IDS_OR_NOTES}}": "Add KB IDs or notes here.",
        "{{PROCEDURE_IDS_OR_NOTES}}": "Add KB IDs or notes here.",
        "{{DOCUMENT_IDS_OR_NOTES}}": "Add KB IDs or notes here.",
        "{{DATE}}": "TBD",
        "{{FOLLOW_UPS}}": "TBD",
        # Provider-specific placeholders
        "{{PRIME_PROVIDER_DISPLAY_NAME}}": _prime.display_name,
        "{{PRIME_PROVIDER_CLI_COMMAND}}": _prime.cli_command,
        "{{PRIME_PROVIDER_MODEL_LABEL}}": _prime.model_label,
        "{{LO_PROVIDER_DISPLAY_NAME}}": _lo.display_name,
        "{{LO_PROVIDER_CLI_COMMAND}}": _lo.cli_command,
        "{{LO_PROVIDER_MODEL_LABEL}}": _lo.model_label,
    }

    # Find all renderable files
    renderable_extensions = {".md", ".json", ".toml", ".yml", ".yaml", ".env", ".txt"}
    for path in target.rglob("*"):
        if path.is_file() and path.suffix in renderable_extensions:
            try:
                content = path.read_text(encoding="utf-8")
            except (UnicodeDecodeError, PermissionError):
                continue
            if "{{" not in content:
                continue
            for placeholder, value in replacements.items():
                content = content.replace(placeholder, value)
            path.write_text(content, encoding="utf-8")


# ── Fallback generators (when templates don't exist yet) ──────────────


def _write_pyproject_sections(target: Path) -> None:
    """Write a pyproject-sections.toml with standard tooling config."""
    content = """\
# GroundTruth project tooling configuration
# Copy these sections into your project's pyproject.toml.

[tool.pytest.ini_options]
testpaths = ["tests"]
asyncio_mode = "auto"
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = "-v --tb=short --strict-markers --timeout=30"
markers = [
    "unit: fast, isolated unit tests",
    "integration: cross-module integration tests",
    "e2e: end-to-end tests requiring full stack",
    "slow: tests that take >2 seconds",
    "security: adversarial and security-focused tests",
]

[tool.coverage.run]
source = ["src"]
branch = true

[tool.coverage.report]
fail_under = 75
show_missing = true

[tool.ruff]
target-version = "py312"
line-length = 120

[tool.ruff.lint]
select = ["E", "F", "I", "UP", "B", "SIM"]
ignore = ["E501", "B008", "SIM108", "UP007"]
"""
    (target / "pyproject-sections.toml").write_text(content, encoding="utf-8")


def _write_default_agents_md(target: Path) -> None:
    content = """\
# {{PROJECT_NAME}} — Loyal Opposition Operating Contract

## Non-negotiable Rule
YOU MUST NOT delete or modify files which you have not created without explicit
approval from the owner.

## Role
- **Loyal Opposition mission:** inspect, critique, and analyze implementation.
- **Output:** evidence-based reports in `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/`

## Startup Checklist
1. Run file bridge sweep: check bridge/INDEX.md for latest NEW or REVISED entries
2. Read project CLAUDE.md and MEMORY.md
3. Report operating state to Prime Builder

## Report Standard
Each finding must include:
1. Concrete claim
2. Evidence source
3. Severity (P0-P3)
4. Impact
5. Recommended action
"""
    (target / "AGENTS.md").write_text(content, encoding="utf-8")


def _write_default_dockerfile(target: Path) -> None:
    content = """\
# {{PROJECT_NAME}} — Production container
FROM python:3.12-slim-bookworm

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/
COPY groundtruth.toml .

EXPOSE 8000
USER 1000:1000
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
"""
    (target / "Dockerfile").write_text(content, encoding="utf-8")


def _write_default_docker_compose(target: Path) -> None:
    content = """\
# {{PROJECT_NAME}} — Local development stack
services:
  app:
    build: .
    ports:
      - "8000:8000"
    env_file: .env.local
    volumes:
      - ./src:/app/src
"""
    (target / "docker-compose.yml").write_text(content, encoding="utf-8")


def _write_default_env_example(target: Path) -> None:
    content = """\
# {{PROJECT_NAME}} — Environment variables
# Copy to .env.local and fill in values.

ENVIRONMENT=development
LOG_LEVEL=INFO

# GroundTruth file bridge (dual-agent mode)
# Configure project-owned OS pollers from bridge-os-poller-setup-prompt.md.

# Azure OpenAI (if using AI features)
# AZURE_OPENAI_ENDPOINT=
# AZURE_OPENAI_API_KEY=
"""
    (target / ".env.example").write_text(content, encoding="utf-8")


def _write_default_terraform(infra: Path, cloud_provider: str) -> None:
    provider_block = {
        "azure": '# stub\nprovider "azurerm" {\n  features {}\n}',
        "aws": '# stub\nprovider "aws" {\n  region = var.region\n}',
        "gcp": '# stub\nprovider "google" {\n  project = var.project_id\n  region  = var.region\n}',
    }.get(cloud_provider, "# stub\n# Configure your cloud provider here")

    (infra / "main.tf").write_text(
        f"# {{{{PROJECT_NAME}}}} — Infrastructure\n\n{provider_block}\n",
        encoding="utf-8",
    )
    (infra / "variables.tf").write_text(
        '# Infrastructure variables\n\nvariable "environment" {\n  type    = string\n  default = "staging"\n}\n',
        encoding="utf-8",
    )
    (infra / "outputs.tf").write_text("# Infrastructure outputs\n", encoding="utf-8")


def _write_webapp_stubs(target: Path, *, options: ScaffoldOptions) -> None:  # noqa: F821
    """Write stub source files for the dual-agent-webapp profile.

    Always generated (not gated on ``seed_example``):
    - ``src/__init__.py``
    - ``pyproject.toml``
    - ``requirements.txt``
    - ``tests/__init__.py``
    - ``tests/test_smoke.py``
    """
    pkg_slug = _package_name_slug(options.project_name)

    src_dir = target / "src"
    src_dir.mkdir(parents=True, exist_ok=True)
    (src_dir / "__init__.py").write_text(
        "# {{PROJECT_NAME}} application package\n",
        encoding="utf-8",
    )

    # Only write pyproject.toml if the scaffold_project helper hasn't already
    # written one via _write_pyproject_sections (that writes pyproject-sections.toml,
    # not pyproject.toml, so we are safe to write pyproject.toml here).
    pyproject = target / "pyproject.toml"
    if not pyproject.exists():
        pyproject.write_text(
            f'[project]\nname = "{pkg_slug}"\nversion = "0.1.0"\nrequires-python = ">=3.11"\n',
            encoding="utf-8",
        )

    req = target / "requirements.txt"
    if not req.exists():
        req.write_text("# Add your runtime dependencies here\n", encoding="utf-8")

    tests_dir = target / "tests"
    tests_dir.mkdir(parents=True, exist_ok=True)
    tests_init = tests_dir / "__init__.py"
    if not tests_init.exists():
        tests_init.write_text("", encoding="utf-8")

    smoke = tests_dir / "test_smoke.py"
    if not smoke.exists():
        smoke.write_text(
            "# tests/test_smoke.py — generated by gt project init\n"
            "# This smoke test ensures pytest CI passes immediately on a fresh scaffold.\n"
            "# Replace with your own tests.\n"
            "\n"
            "\n"
            "def test_smoke() -> None:\n"
            '    """Initial smoke test. Replace with real assertions."""\n'
            "    assert True\n",
            encoding="utf-8",
        )


def _write_tasks_stub(target: Path) -> None:
    """Write ``src/tasks.py`` implementation stub for seeded-example scaffolds.

    The stub satisfies the seeded SPEC-001 and SPEC-002 grep assertions so CI
    is green from the first push. The assertion patterns are:
    - ``def create_task`` (function exists)
    - ``status.*=.*['"]open['"]`` (create_task sets status to open)
    """
    src_dir = target / "src"
    src_dir.mkdir(parents=True, exist_ok=True)
    stub = src_dir / "tasks.py"
    if stub.exists():
        return
    stub.write_text(
        "# src/tasks.py — seed-example implementation stub\n"
        "# Generated by: gt project init (default --seed-example)\n"
        "#\n"
        "# This stub satisfies the seeded SPEC-001 and SPEC-002 assertions so your CI\n"
        "# is green from first push. Evolve this file or replace it with your real app.\n"
        "# To start without example assertions, use: gt project init --no-seed-example\n"
        "\n"
        "from __future__ import annotations\n"
        "\n"
        "\n"
        "def create_task(\n"
        "    title: str,\n"
        '    description: str = "",\n'
        '    priority: str = "medium",\n'
        ") -> dict:\n"
        '    """Create a task with the given title.\n'
        "\n"
        "    Returns a dict with id, title, description, priority, status='open',\n"
        "    and created_at timestamp.\n"
        '    """\n'
        "    return {\n"
        '        "id": 1,\n'
        '        "title": title,\n'
        '        "description": description,\n'
        '        "priority": priority,\n'
        '        "status": "open",\n'
        '        "created_at": "2026-01-01T00:00:00Z",\n'
        "    }\n"
        "\n"
        "\n"
        "def list_tasks(\n"
        "    status: str | None = None,\n"
        "    priority: str | None = None,\n"
        ") -> list:\n"
        '    """List tasks, optionally filtered by status and/or priority."""\n'
        "    return []\n",
        encoding="utf-8",
    )


def _copy_integration_templates(target: Path, *, options: ScaffoldOptions) -> None:  # noqa: F821
    """Copy optional integration config files (``--integrations`` flag).

    Generates:
    - ``.github/dependabot.yml``
    - ``.coderabbitai.yaml``

    Applies ``{{PROJECT_NAME}}`` substitution in both files.
    """
    templates = get_templates_dir()
    int_dir = templates / "ci" / "integrations"

    pkg_slug = _package_name_slug(options.project_name)

    # dependabot.yml → .github/dependabot.yml
    dep_src = int_dir / "dependabot.yml"
    if dep_src.exists():
        github_dir = target / ".github"
        github_dir.mkdir(parents=True, exist_ok=True)
        content = dep_src.read_text(encoding="utf-8")
        content = content.replace("{{PROJECT_NAME}}", options.project_name)
        content = content.replace("{{PACKAGE_NAME}}", pkg_slug)
        (github_dir / "dependabot.yml").write_text(content, encoding="utf-8")

    # .coderabbitai.yaml → repository root
    cr_src = int_dir / ".coderabbitai.yaml"
    if cr_src.exists():
        content = cr_src.read_text(encoding="utf-8")
        content = content.replace("{{PROJECT_NAME}}", options.project_name)
        content = content.replace("{{PACKAGE_NAME}}", pkg_slug)
        (target / ".coderabbitai.yaml").write_text(content, encoding="utf-8")


def scaffold_summary(target: Path, profile: str) -> str:
    """Human-readable summary of what was created."""
    p = get_profile(profile)
    lines = [
        f"Project scaffolded in {target}",
        f"Profile: {p.display_name} ({p.name})",
        "",
        "Created:",
        "  - groundtruth.toml (with [project] manifest)",
        "  - groundtruth.db",
        "  - CLAUDE.md, MEMORY.md",
        "  - .claude/hooks/ and .claude/rules/",
    ]
    if p.includes_bridge:
        lines.extend(
            [
                "  - AGENTS.md (Loyal Opposition contract)",
                "  - BRIDGE-INVENTORY.md",
                "  - bridge-os-poller-setup-prompt.md",
                "  - Bridge rules and hooks",
                "  - independent-progress-assessments/ (Codex reports)",
            ]
        )
    if p.includes_docker:
        lines.extend(
            [
                "  - Dockerfile + docker-compose.yml",
                "  - .env.example",
            ]
        )
    if p.includes_cloud:
        lines.append("  - infrastructure/terraform/ stubs")
    lines.extend(
        [
            "",
            "Next steps:",
            f"  1. cd {target}",
            "  2. Review CLAUDE.md and replace any TBD values",
            "  3. Run `gt project doctor` to verify workstation readiness",
            "  4. Run `gt summary` to inspect the knowledge database",
        ]
    )
    if p.includes_bridge:
        lines.append("  5. Start a session — the bridge handshake will run automatically")
    return "\n".join(lines)
