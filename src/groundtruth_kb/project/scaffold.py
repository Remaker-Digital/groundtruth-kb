# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Project scaffold engine — ``gt project init`` implementation."""

from __future__ import annotations

import shutil
from dataclasses import dataclass
from pathlib import Path

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
from groundtruth_kb.project.manifest import ProjectManifest, write_manifest
from groundtruth_kb.project.profiles import get_profile


@dataclass(frozen=True)
class ScaffoldOptions:
    """Options for ``gt project init``."""

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


def scaffold_project(options: ScaffoldOptions) -> Path:
    """Create a complete project scaffold based on the selected profile."""
    profile = get_profile(options.profile)
    target = options.target_dir.resolve()
    _validate_target(target)
    target.mkdir(parents=True, exist_ok=True)

    copyright_notice = options.copyright_notice or _default_copyright(options.owner)

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
        _copy_dual_agent_templates(target)

    # ── Webapp templates ──────────────────────────────────────────────
    if profile.includes_docker:
        _copy_webapp_templates(target, cloud_provider=options.cloud_provider)

    # ── CI workflows ──────────────────────────────────────────────────
    include_ci = options.include_ci or profile.includes_ci
    if include_ci:
        _copy_ci_templates(target)

    # ── Render all placeholders ───────────────────────────────────────
    _render_all_templates(
        target=target,
        project_name=options.project_name,
        owner=options.owner,
        copyright_notice=copyright_notice,
        profile=profile,
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

    # ── Git init ──────────────────────────────────────────────────────
    if options.init_git:
        _initialize_git_repo(target)

    return target


# ── Template copy helpers ─────────────────────────────────────────────


def _copy_base_templates(target: Path) -> None:
    """Copy base templates for all profiles: CLAUDE.md, MEMORY.md, hooks, rules."""
    templates = get_templates_dir()

    for name in ("CLAUDE.md", "MEMORY.md"):
        shutil.copy2(templates / name, target / name)

    hooks_target = target / ".claude" / "hooks"
    hooks_target.mkdir(parents=True, exist_ok=True)
    for src in (templates / "hooks").glob("*.py"):
        shutil.copy2(src, hooks_target / src.name)

    rules_target = target / ".claude" / "rules"
    rules_target.mkdir(parents=True, exist_ok=True)
    for src in (templates / "rules").glob("*.md"):
        # Base profile only gets prime-builder rule
        if src.name == "prime-builder.md":
            shutil.copy2(src, rules_target / src.name)

    # Generate base pyproject sections
    _write_pyproject_sections(target)


def _copy_dual_agent_templates(target: Path) -> None:
    """Copy dual-agent templates: AGENTS.md, bridge rules, Codex bootstrap."""
    templates = get_templates_dir()

    # BRIDGE-INVENTORY.md
    bi = templates / "BRIDGE-INVENTORY.md"
    if bi.exists():
        shutil.copy2(bi, target / "BRIDGE-INVENTORY.md")

    # AGENTS.md
    agents_template = templates / "project" / "AGENTS.md"
    if agents_template.exists():
        shutil.copy2(agents_template, target / "AGENTS.md")
    else:
        _write_default_agents_md(target)

    # All rules (bridge-specific)
    rules_target = target / ".claude" / "rules"
    rules_target.mkdir(parents=True, exist_ok=True)
    for src in (templates / "rules").glob("*.md"):
        shutil.copy2(src, rules_target / src.name)

    # Additional hooks (destructive-gate, credential-scan, scheduler)
    hooks_target = target / ".claude" / "hooks"
    for src in (templates / "hooks").glob("*.py"):
        if not (hooks_target / src.name).exists():
            shutil.copy2(src, hooks_target / src.name)

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

    # .gitignore additions for bridge
    gi = target / ".gitignore"
    content = gi.read_text(encoding="utf-8") if gi.exists() else ""
    additions = "\n# Bridge database\nbridge.db\nprime_bridge.db\n"
    if "bridge.db" not in content:
        gi.write_text(content + additions, encoding="utf-8")


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


def _copy_ci_templates(target: Path) -> None:
    """Copy CI/CD workflow templates."""
    templates = get_templates_dir()
    workflows = target / ".github" / "workflows"
    workflows.mkdir(parents=True, exist_ok=True)
    for src in (templates / "ci").glob("*.yml"):
        shutil.copy2(src, workflows / src.name)


# ── Rendering ─────────────────────────────────────────────────────────


def _render_all_templates(
    *,
    target: Path,
    project_name: str,
    owner: str,
    copyright_notice: str,
    profile,
) -> None:
    """Replace all {{PLACEHOLDER}} values in rendered files."""
    replacements = {
        "{{PROJECT_NAME}}": project_name,
        "{{PROJECT_TYPE}}": f"{profile.display_name} project",
        "{{OWNER}}": owner,
        "{{COPYRIGHT}}": copyright_notice,
        "{{VERSION}}": "0.1.0",
        "{{PROFILE}}": profile.name,
        "{{ENVIRONMENT_DESCRIPTION}}": "Local workstation bootstrap",
        "{{TEST_STATUS}}": "Not run yet",
        "{{BRIDGE_INVENTORY_PATH_OR_NA}}": (
            "BRIDGE-INVENTORY.md" if profile.includes_bridge else "N/A"
        ),
        "{{AUTOMATION_SUMMARY_OR_NA}}": (
            "Bridge resident worker + poller configured"
            if profile.includes_bridge
            else "None configured yet"
        ),
        "{{OPS_HEALTH_NOTES}}": "Bootstrap complete. Update after the first working session.",
        "{{AGENT_OR_PROCESS_1}}": (
            "prime-builder" if profile.includes_bridge else "builder-agent"
        ),
        "{{RESPONSIBILITY}}": "Implementation, specs, and project bootstrap",
        "{{REVIEWER}}": (
            "codex (Loyal Opposition)" if profile.includes_bridge else "owner"
        ),
        "{{NOTES}}": "Replace with your actual collaboration topology.",
        "{{PATH_TO_ENTRYPOINT}}": (
            "gt bridge serve (MCP)" if profile.includes_bridge else "TBD"
        ),
        "{{WHAT_IT_DOES}}": (
            "Synchronous dialog bridge between Prime and Codex"
            if profile.includes_bridge
            else "Document your bridge or automation entrypoint here."
        ),
        "{{HOW_IT_RUNS}}": (
            "SessionStart hook launches resident worker"
            if profile.includes_bridge
            else "Manual start or scheduled run"
        ),
        "{{OTHER_PATH}}": "TBD",
        "{{KIND}}": "TBD",
        "{{PURPOSE}}": "Replace with the actual purpose for this control surface.",
        "{{WHEN_TO_UPDATE}}": "Whenever the runtime or coordination rules change.",
        "{{AUTOMATION_NAME}}": "bridge-resident-worker",
        "{{SCHEDULE}}": "Session start (hook-driven)",
        "{{EXECUTOR}}": "groundtruth_kb.bridge.worker",
        "{{SOURCE}}": ".claude/hooks/",
        "{{FAILURE_SIGNAL}}": "Bridge health check failure",
        "{{ASYNC_OR_TRANSACTIONAL_DESCRIPTION}}": (
            "Asynchronous message passing with synchronous dialog semantics. "
            "Not all messages require replies."
        ),
        "{{WHEN_MESSAGES_REQUIRE_REPLIES}}": (
            "Substantive messages with expected_response field require replies."
        ),
        "{{WHEN_TO_RETRY}}": "Non-blocking persistent retry, 3 attempts max, 5-minute interval.",
        "{{STARTUP_OR_LIVENESS_CHECK}}": (
            "Session-start handshake: send 'Report your current operating state' and wait for reply."
        ),
        "{{WHEN_RESTARTS_ARE_ALLOWED_OR_AVOIDED}}": (
            "Restart only for code deployment, bad session state, or instruction reload."
        ),
        "{{ENV_CONFIG_IDS_OR_NOTES}}": "Add KB IDs or notes here.",
        "{{PROCEDURE_IDS_OR_NOTES}}": "Add KB IDs or notes here.",
        "{{DOCUMENT_IDS_OR_NOTES}}": "Add KB IDs or notes here.",
        "{{DATE}}": "TBD",
        "{{FOLLOW_UPS}}": "TBD",
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
1. Run bridge sweep: check for pending messages
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

# GroundTruth bridge (dual-agent mode)
PRIME_BRIDGE_DB=~/.claude/prime-bridge/bridge.db

# Azure OpenAI (if using AI features)
# AZURE_OPENAI_ENDPOINT=
# AZURE_OPENAI_API_KEY=
"""
    (target / ".env.example").write_text(content, encoding="utf-8")


def _write_default_terraform(infra: Path, cloud_provider: str) -> None:
    provider_block = {
        "azure": 'provider "azurerm" {\n  features {}\n}',
        "aws": 'provider "aws" {\n  region = var.region\n}',
        "gcp": 'provider "google" {\n  project = var.project_id\n  region  = var.region\n}',
    }.get(cloud_provider, "# Configure your cloud provider here")

    (infra / "main.tf").write_text(
        f'# {{{{PROJECT_NAME}}}} — Infrastructure\n\n{provider_block}\n',
        encoding="utf-8",
    )
    (infra / "variables.tf").write_text(
        '# Infrastructure variables\n\nvariable "environment" {\n'
        '  type    = string\n  default = "staging"\n}\n',
        encoding="utf-8",
    )
    (infra / "outputs.tf").write_text(
        "# Infrastructure outputs\n", encoding="utf-8"
    )


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
        lines.extend([
            "  - AGENTS.md (Loyal Opposition contract)",
            "  - BRIDGE-INVENTORY.md",
            "  - Bridge rules and hooks",
            "  - independent-progress-assessments/ (Codex reports)",
        ])
    if p.includes_docker:
        lines.extend([
            "  - Dockerfile + docker-compose.yml",
            "  - .env.example",
        ])
    if p.includes_cloud:
        lines.append("  - infrastructure/terraform/ stubs")
    lines.extend([
        "",
        "Next steps:",
        f"  1. cd {target}",
        "  2. Review CLAUDE.md and replace any TBD values",
        "  3. Run `gt project doctor` to verify workstation readiness",
        "  4. Run `gt summary` to inspect the knowledge database",
    ])
    if p.includes_bridge:
        lines.append("  5. Start a session — the bridge handshake will run automatically")
    return "\n".join(lines)
