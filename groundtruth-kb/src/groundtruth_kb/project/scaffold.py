"""Create application files using a canonical project and the selected host baseline.

One initializer serves interactive and desktop use: the explicitly selected
execution project, its registered application slot and the host's neutral
baseline/projectors determine every output. Providers and harness names select
configuration profiles only; they never assign an agent role.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import sys
import tomllib
from collections.abc import Set as AbstractSet
from dataclasses import dataclass, field
from pathlib import Path, PurePosixPath
from typing import Any
from urllib.parse import quote

from groundtruth_kb import __version__, get_templates_dir
from groundtruth_kb.authority_client import AuthorityClient, AuthorityClientError
from groundtruth_kb.isolation.registry_check import application_slot_path, load_application_catalog
from groundtruth_kb.isolation.validation import check_slot_markers
from groundtruth_kb.project.core_spec_intake import intake_status
from groundtruth_kb.project.profiles import ProjectProfile, get_profile
from groundtruth_kb.project.spec_scaffold import (
    NativeScaffoldReport,
    planned_specifications,
    scaffold_config,
    scaffold_specs,
)

CLOUD_PROVIDERS: tuple[str, ...] = ("none", "azure", "aws", "gcp")
TERRAFORM_STUBS: tuple[str, ...] = ("main.tf", "variables.tf", "outputs.tf")


@dataclass(frozen=True)
class ScaffoldOptions:
    """Explicit application selection; providers never determine agent roles."""

    project_name: str
    profile: str
    owner: str
    target_dir: Path
    gt_kb_root: Path
    project_id: str
    authority_url: str
    harnesses: tuple[str, ...] = ()
    copyright_notice: str = ""
    cloud_provider: str = "none"
    init_git: bool = True
    include_ci: bool = True
    seed_example: bool = False
    python_version: str = "3.11"
    integrations: bool = False
    opt_out_core_spec_intake: bool = False
    spec_scaffold: str | None = None


@dataclass(frozen=True)
class ScaffoldPlan:
    """An ephemeral preview, revalidated before creating any application file."""

    options: ScaffoldOptions
    project: dict[str, Any]
    files: dict[str, bytes]
    inputs: dict[Path, str]
    initial_question: dict[str, Any] | None
    generated_paths: tuple[str, ...] = ()
    specifications: tuple[dict[str, Any], ...] = ()


@dataclass(frozen=True)
class ScaffoldResult:
    """What initialization created, read back after the effects."""

    target: Path
    project: dict[str, Any]
    paths: tuple[str, ...]
    generated_paths: tuple[str, ...]
    initial_question: dict[str, Any] | None
    intake: dict[str, Any]
    specifications: NativeScaffoldReport | None
    canonical_writes: int = 0
    commits: int = 0
    warnings: tuple[str, ...] = field(default_factory=tuple)
    specification_error: dict[str, Any] | None = None


def package_name_slug(project_name: str) -> str:
    """Lowercase kebab-case slug usable as a package, image or distribution name."""
    return re.sub(r"[^a-z0-9]+", "-", project_name.lower()).strip("-")


def ci_tier(profile: ProjectProfile) -> str:
    """Select the CI template tier: minimal, standard or full."""
    if profile.includes_ci and profile.includes_bridge:
        return "full"
    if profile.includes_bridge:
        return "standard"
    return "minimal"


def enumerate_scaffold_outputs(profile_name: str, *, cloud_provider: str = "none") -> list[str]:
    """Minimum application-owned files, independent of optional harness projections."""
    profile = get_profile(profile_name)
    if cloud_provider not in CLOUD_PROVIDERS:
        raise ValueError("Select one of: " + ", ".join(CLOUD_PROVIDERS))
    names = {
        "groundtruth.toml",
        "README.md",
        ".gitignore",
        "pyproject.toml",
        ".githooks/reference-transaction",
        ISOLATION_REGISTRY,
    }
    if profile.includes_docker:
        names.update(
            {
                "Dockerfile",
                "docker-compose.yml",
                ".env.example",
                "src/__init__.py",
                "requirements.txt",
                "tests/__init__.py",
                "tests/test_smoke.py",
            }
        )
    if cloud_provider != "none":
        if not profile.includes_cloud:
            raise ValueError("Cloud infrastructure stubs require a profile that includes cloud deployment")
        names.update(f"infrastructure/terraform/{name}" for name in TERRAFORM_STUBS)
    return sorted(names)


ISOLATION_REGISTRY = ".gtkb-app-isolation.json"
RUNTIME_TOP_LEVEL_ENTRIES: tuple[tuple[str, str, str, str], ...] = (
    (".git", "DIR", "runtime_data", "Independent Git repository metadata of the application"),
    (".venv", "DIR", "runtime_data", "Local virtual environment; never a project artifact"),
    ("__pycache__", "DIR", "bounded_temporary_output", "Interpreter bytecode cache"),
    (".pytest_cache", "DIR", "bounded_temporary_output", "Test runner cache"),
    (".ruff_cache", "DIR", "bounded_temporary_output", "Linter cache"),
    (".env.local", "FILE", "runtime_data", "Local environment values; never committed"),
    (".groundtruth-chroma", "DIR", "generated_output", "Derived search cache rebuilt from the configured authority"),
)


def isolation_registry_bytes(application: str, files: dict[str, bytes], generated: list[str]) -> bytes:
    """Deterministic artifact-boundary registry for every top-level entry the initializer creates or expects."""
    generated_roots = {name.split("/")[0] for name in generated}
    entries: dict[str, dict[str, str]] = {}
    for name in files:
        top = name.split("/")[0]
        if top == ISOLATION_REGISTRY:
            continue
        artifact_type = "DIR" if "/" in name else "FILE"
        if top in generated_roots:
            entries[top] = {
                "name": top,
                "type": artifact_type,
                "classification": "generated_output",
                "purpose": "Harness configuration projected from the host baseline; regenerated by gt project upgrade",
            }
        else:
            entries.setdefault(
                top,
                {
                    "name": top,
                    "type": artifact_type,
                    "classification": "authoritative_input",
                    "purpose": "Application-owned file created by gt project init",
                },
            )
    entries["application.toml"] = {
        "name": "application.toml",
        "type": "FILE",
        "classification": "authoritative_input",
        "purpose": "Application registration marker matching the host catalog entry",
    }
    entries[ISOLATION_REGISTRY] = {
        "name": ISOLATION_REGISTRY,
        "type": "FILE",
        "classification": "authoritative_input",
        "purpose": "Artifact-boundary registry of every top-level application entry",
    }
    for name, artifact_type, classification, purpose in RUNTIME_TOP_LEVEL_ENTRIES:
        entries.setdefault(
            name, {"name": name, "type": artifact_type, "classification": classification, "purpose": purpose}
        )
    payload = {
        "schema_version": "2.0",
        "application": application,
        "isolation_contract_adr": "ADR-APPLICATION-ISOLATION-CONTRACT-001",
        "minimization_principle_dcl": "DCL-APP-ROOT-MINIMIZATION-001",
        "top_level_artifacts": [entries[name] for name in sorted(entries, key=str.casefold)],
    }
    return (json.dumps(payload, indent=2, ensure_ascii=False) + "\n").encode("utf-8")


INTERNAL_PLATFORM_LEAK_PREFIXES: tuple[str, ...] = (
    ".gtkb-state/",
    ".claude/worktrees/",
    "groundtruth-kb/",
    "harness-state/",
    "independent-progress-assessments/",
    ".worktrees/",
)
LOCAL_AUTHORITY_NAMES: tuple[str, ...] = ("groundtruth.db", "groundtruth.db-wal", "groundtruth.db-shm")


@dataclass(frozen=True)
class ScaffoldPackagingValidation:
    """Minimum-file and platform-leakage validation for an initialized application."""

    target: Path
    profile_name: str
    cloud_provider: str
    expected_paths: tuple[str, ...]
    observed_paths: tuple[str, ...]
    missing_paths: tuple[str, ...]
    leaked_paths: tuple[str, ...]
    unexpected_paths: tuple[str, ...]

    @property
    def passed(self) -> bool:
        return not self.missing_paths and not self.leaked_paths

    def summary(self) -> str:
        if self.passed:
            return (
                f"PASS scaffold packaging validation for {self.profile_name}: "
                f"{len(self.expected_paths)} expected paths present; no internal-platform leakage"
            )
        parts: list[str] = []
        if self.missing_paths:
            parts.append(f"missing={list(self.missing_paths)}")
        if self.leaked_paths:
            parts.append(f"leaked={list(self.leaked_paths)}")
        return f"FAIL scaffold packaging validation for {self.profile_name}: " + "; ".join(parts)


def application_files(target: Path) -> set[str]:
    """Application-relative file paths, excluding Git metadata."""
    return {
        path.relative_to(target).as_posix()
        for path in target.rglob("*")
        if path.is_file() and ".git" not in path.relative_to(target).parts
    }


def leaked_platform_paths(paths: AbstractSet[str], *, expected: AbstractSet[str] = frozenset()) -> list[str]:
    """Paths that only the platform host or a local authority store should own."""
    leaked = []
    for relative in sorted(paths):
        if relative in expected:
            continue
        platform_owned = any(relative.startswith(prefix) for prefix in INTERNAL_PLATFORM_LEAK_PREFIXES)
        if platform_owned or PurePosixPath(relative).name in LOCAL_AUTHORITY_NAMES:
            leaked.append(relative)
    return leaked


def validate_scaffold_minimum_and_no_leakage(
    target: Path, profile_name: str, *, cloud_provider: str = "none"
) -> ScaffoldPackagingValidation:
    """Validate minimum outputs and the absence of platform state or a local authority store."""
    expected = set(enumerate_scaffold_outputs(profile_name, cloud_provider=cloud_provider))
    observed = application_files(target)
    return ScaffoldPackagingValidation(
        target=target,
        profile_name=profile_name,
        cloud_provider=cloud_provider,
        expected_paths=tuple(sorted(expected)),
        observed_paths=tuple(sorted(observed)),
        missing_paths=tuple(sorted(path for path in expected if path not in observed)),
        leaked_paths=tuple(leaked_platform_paths(observed, expected=expected)),
        unexpected_paths=tuple(sorted(path for path in observed if path not in expected)),
    )


REDIRECTING_GIT_VARIABLES: frozenset[str] = frozenset(
    {
        "GIT_DIR",
        "GIT_WORK_TREE",
        "GIT_COMMON_DIR",
        "GIT_INDEX_FILE",
        "GIT_NAMESPACE",
        "GIT_OBJECT_DIRECTORY",
        "GIT_ALTERNATE_OBJECT_DIRECTORIES",
        "GIT_REPLACE_REF_BASE",
    }
)


def inherited_git_overrides() -> list[str]:
    """Environment variables that would redirect repository, index or configuration identity.

    Editor, pager and similar variables do not change which repository an
    operation observes; only the same set the native commit callback refuses
    is refused here.
    """
    return sorted(
        name
        for name in os.environ
        if name in REDIRECTING_GIT_VARIABLES or (name.startswith("GIT_CONFIG_") and name != "GIT_CONFIG_NOSYSTEM")
    )


def _git(root: Path, *args: str, required: bool = True) -> str:
    result = subprocess.run(
        ["git", "--no-optional-locks", "-C", str(root), *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=30,
        creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
    )
    if required and result.returncode:
        raise ValueError(result.stderr.strip() or "Git did not complete")
    return result.stdout.strip() if result.returncode == 0 else ""


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _selected_project(options: ScaffoldOptions) -> dict[str, Any]:
    host = options.gt_kb_root.absolute()
    if host.resolve(strict=True) != host or not host.is_dir():
        raise ValueError("Select an existing, unredirected platform host")
    if inherited_git_overrides():
        raise ValueError("Remove inherited Git repository/index/config overrides before application initialization")
    if Path(_git(host, "rev-parse", "--show-toplevel")).resolve() != host:
        raise ValueError("The selected host must be a Git repository root")
    project = AuthorityClient(options.authority_url).request(
        "GET", "/v1/projects/" + quote(options.project_id, safe="")
    )["project"]
    ref = project.get("repository_ref")
    if project.get("kind") != "project" or not isinstance(ref, str) or not ref.startswith("application:"):
        raise ValueError("Select an execution project with an explicit application repository")
    app = ref.removeprefix("application:")
    target = application_slot_path(host, app)
    if options.target_dir.absolute() != target or target.resolve() != target:
        raise ValueError(
            "Target must be the selected project's exact registered application root under the host's applications/"
        )
    if app not in load_application_catalog(host):
        raise ValueError("Register the application before initializing its files")
    checks = check_slot_markers(host, app)
    if not checks["consistent"] or not checks["app_toml_present"]:
        raise ValueError("The application marker must agree with its catalog entry")
    return dict(project)


def _empty_target(options: ScaffoldOptions) -> None:
    target = options.target_dir
    if (target / "groundtruth.toml").exists():
        raise ValueError("Existing application configuration: inspect gt project upgrade")
    unexpected = sorted(p.name for p in target.iterdir() if p.name not in {"application.toml", ".git"})
    if unexpected:
        raise ValueError("Target directory is not empty: " + ", ".join(unexpected))
    metadata = target / ".git"
    if metadata.exists():
        if not metadata.is_dir() or metadata.resolve() != metadata:
            raise ValueError("Application initialization requires its independent Git repository")
        if Path(_git(target, "rev-parse", "--show-toplevel")).resolve() != target:
            raise ValueError("Application repository resolves to another root")
        if _git(target, "rev-parse", "--verify", "HEAD", required=False):
            raise ValueError("Application repository has history; use its upgrade workflow")
        if _git(target, "ls-files", "--stage"):
            raise ValueError("Preserve the application's existing staged work before initialization")
        configured = _git(target, "config", "--get", "core.hooksPath", required=False)
        if configured not in {"", ".githooks", "./.githooks"}:
            raise ValueError("Preserve the application's custom hooks configuration before initialization")
    elif not options.init_git:
        raise ValueError("Initialize an independent application repository or permit Git initialization")


def _template(name: str, replacements: dict[str, str], inputs: dict[Path, str]) -> bytes:
    source = get_templates_dir() / name
    inputs[source] = _sha(source)
    text = source.read_text(encoding="utf-8")
    for key, value in replacements.items():
        text = text.replace("{{" + key + "}}", value)
    if re.search(r"\{\{[A-Z_]+\}\}", text):
        raise ValueError("Unresolved application template input: " + name)
    return text.encode("utf-8")


def _terraform_stub(name: str, cloud_provider: str, title: str) -> bytes:
    provider_block = {
        "azure": 'provider "azurerm" {\n  features {}\n}\n',
        "aws": 'provider "aws" {\n  region = var.region\n}\n',
        "gcp": 'provider "google" {\n  project = var.project_id\n  region  = var.region\n}\n',
    }[cloud_provider]
    if name == "main.tf":
        return (
            f"# {title} — infrastructure stub; replace with the reviewed deployment plan\n\n{provider_block}".encode()
        )
    if name == "variables.tf":
        variables = ['variable "environment" {\n  type    = string\n  default = "staging"\n}\n']
        if cloud_provider in {"aws", "gcp"}:
            variables.append('variable "region" {\n  type = string\n}\n')
        if cloud_provider == "gcp":
            variables.append('variable "project_id" {\n  type = string\n}\n')
        return ("# Infrastructure variables\n\n" + "\n".join(variables)).encode()
    return b"# Infrastructure outputs\n"


def _hook_bytes(host: Path, inputs: dict[Path, str]) -> bytes:
    hook = host / ".githooks/reference-transaction"
    if not hook.is_file() or hook.resolve() != hook or b"groundtruth_kb.project.native_commit" not in hook.read_bytes():
        raise ValueError("The host's native reference-transaction hook is missing or redirected")
    inputs[hook] = _sha(hook)
    return hook.read_bytes()


def render_projection(host: Path, harness: str, application: str) -> dict[str, Any]:
    """Render one harness projection for the application as a read-only preview."""
    projector = host / "scripts/harness_projection/project_harness.py"
    if not projector.is_file() or projector.resolve() != projector:
        raise ValueError("The selected host's supported harness projector is unavailable")
    result = subprocess.run(
        [sys.executable, "-P", str(projector), "--harness", harness, "--application", application, "--render-json"],
        cwd=host,
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=120,
        env={**os.environ, "PYTHONIOENCODING": "utf-8", "PYTHONDONTWRITEBYTECODE": "1"},
        creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
    )
    if result.returncode:
        raise ValueError("Application projection refused: " + (result.stderr or result.stdout).strip())
    rendered = json.loads(result.stdout)
    if not isinstance(rendered, dict) or {"writes", "removes", "gaps", "inputs"} - set(rendered):
        raise ValueError("Application projection returned an incomplete preview")
    return rendered


def plan_scaffold(options: ScaffoldOptions) -> ScaffoldPlan:
    """Validate the full initial file set and return its preview without effects."""
    profile = get_profile(options.profile)
    if not options.owner.strip() or re.fullmatch(r"3\.[0-9]+", options.python_version) is None:
        raise ValueError("A nonempty owner and a Python 3 minor version are required")
    if options.cloud_provider not in CLOUD_PROVIDERS:
        raise ValueError("Select one of: " + ", ".join(CLOUD_PROVIDERS))
    if options.cloud_provider != "none" and not profile.includes_cloud:
        raise ValueError("Cloud infrastructure stubs require a profile that includes cloud deployment")
    if options.spec_scaffold is not None:
        scaffold_config(options.spec_scaffold)
    project = _selected_project(options)
    _empty_target(options)
    host, target = options.gt_kb_root, options.target_dir
    inputs = {
        host / "applications/registry.toml": _sha(host / "applications/registry.toml"),
        target / "application.toml": _sha(target / "application.toml"),
    }
    client = AuthorityClient(options.authority_url)
    state = None if options.opt_out_core_spec_intake else intake_status(client, options.project_id)
    question = next((row for row in state["slots"] if not row["complete"]), None) if state else None
    title = str(project["name"])
    notice = options.copyright_notice or f"Copyright {options.owner}. All rights reserved."
    slug = package_name_slug(target.name)

    def encoded(value: str) -> str:
        return json.dumps(value, ensure_ascii=False)

    config = (
        "# Native GT-KB client configuration; canonical project facts are read from the service.\n"
        f'[groundtruth]\nproject_root = "."\nauthority_url = {encoded(options.authority_url)}\n'
        f"app_title = {encoded(title)}\nlegal_footer = {encoded(notice)}\n\n"
        f"[project]\nproject_name = {encoded(title)}\nowner = {encoded(options.owner)}\n"
        f"profile = {encoded(profile.name)}\ncloud_provider = {encoded(options.cloud_provider)}\n"
        f"scaffold_version = {encoded(__version__)}\n\n"
        f"[core_spec_intake]\nenabled = {str(not options.opt_out_core_spec_intake).lower()}\n"
    )
    tomllib.loads(config)
    files = {
        "groundtruth.toml": config.encode(),
        "README.md": (
            f"# {title}\n\n{notice}\n\n"
            "Specifications and work state use the configured GT-KB authority.\n\n"
            "Read the next question: `gt --config groundtruth.toml core-specs next-question "
            f"--project-id {options.project_id}`.\n"
            "Apply an explicit answer with `core-specs answer`; "
            "supply the current expected version, actor and reason.\n"
            "Each agent context receives its role explicitly. The selected harness does not determine that role.\n"
        ).encode(),
        ".gitignore": (
            b"__pycache__/\n*.pyc\n.pytest_cache/\n.ruff_cache/\n.venv/\n.env.local\n.groundtruth-chroma/\n"
        ),
        "pyproject.toml": (
            f'[project]\nname = "{slug}"\nversion = "0.1.0"\nrequires-python = ">={options.python_version}"\n'
        ).encode(),
        ".githooks/reference-transaction": _hook_bytes(host, inputs),
    }
    replacements = {
        "PROJECT_NAME": title,
        "PACKAGE_NAME": slug.replace("-", "_"),
        "OWNER": options.owner,
        "PYTHON_VERSION": options.python_version,
        "COPYRIGHT_NOTICE": notice,
    }
    if options.include_ci:
        tier = ci_tier(profile)
        sources = sorted((get_templates_dir() / "ci" / tier).glob("*.yml"))
        if not sources:
            raise ValueError("The selected CI profile has no templates")
        for source in sources:
            files[".github/workflows/" + source.name] = _template(f"ci/{tier}/{source.name}", replacements, inputs)
    if profile.includes_docker:
        for template_name, destination in (
            ("Dockerfile", "Dockerfile"),
            ("docker-compose.yml", "docker-compose.yml"),
            ("env.example", ".env.example"),
        ):
            files[destination] = _template("project/" + template_name, replacements, inputs)
        files["src/__init__.py"] = f"# {title} application package\n".encode()
        files["requirements.txt"] = b"# Declare the application's runtime dependencies here.\n"
        files["tests/__init__.py"] = b""
        files["tests/test_smoke.py"] = (
            b"# Generated by gt project init; replace with the application's own tests.\n\n\n"
            b"def test_smoke() -> None:\n"
            b'    """Initial smoke test so a fresh scaffold passes its CI test step."""\n'
            b"    assert True\n"
        )
    if options.cloud_provider != "none":
        for name in TERRAFORM_STUBS:
            files[f"infrastructure/terraform/{name}"] = _terraform_stub(name, options.cloud_provider, title)
    if options.seed_example:
        files["src/tasks.py"] = (
            b'"""Example application function; replace it with the required product behavior."""\n\n\n'
            b"def create_task(title: str) -> dict[str, str]:\n"
            b'    return {"title": title, "status": "open"}\n\n\n'
            b"def list_tasks() -> list[dict[str, str]]:\n    return []\n"
        )
        files["tests/test_tasks.py"] = (
            b"from src.tasks import create_task, list_tasks\n\n\n"
            b"def test_new_task_preserves_title_and_starts_open() -> None:\n"
            b'    assert create_task("Example") == {"title": "Example", "status": "open"}\n\n\n'
            b"def test_fresh_listing_is_empty() -> None:\n    assert list_tasks() == []\n"
        )
        files.setdefault("src/__init__.py", b"")
        files.setdefault("tests/__init__.py", b"")
    if options.integrations:
        files[".github/dependabot.yml"] = _template("ci/integrations/dependabot.yml", replacements, inputs)
        files[".coderabbitai.yaml"] = _template("ci/integrations/.coderabbitai.yaml", replacements, inputs)
    generated = []
    for harness in dict.fromkeys(options.harnesses):
        rendered = render_projection(host, harness, target.name)
        if rendered["gaps"] or any((target / name).exists() for name in rendered["removes"]):
            raise ValueError("Initial application projection has gaps or requests removal")
        for name, text in rendered["writes"].items():
            body = text.encode("utf-8")
            if name in files and files[name] != body:
                raise ValueError("Scaffold outputs disagree: " + name)
            files[name] = body
            generated.append(name)
        for name, identity in rendered["inputs"].items():
            inputs[host / name] = identity
    generated_roots = sorted({name.split("/")[0] + "/" for name in generated})
    if generated_roots:
        files[".gitignore"] += ("\n# Derived harness configuration\n" + "\n".join(generated_roots) + "\n").encode()
    files[ISOLATION_REGISTRY] = isolation_registry_bytes(project["repository_ref"].partition(":")[2], files, generated)
    if not set(enumerate_scaffold_outputs(options.profile, cloud_provider=options.cloud_provider)).issubset(files):
        raise ValueError("The application preview is missing required profile files")
    for name in files:
        relative = PurePosixPath(name)
        if relative.is_absolute() or ".." in relative.parts or ":" in name or "\\" in name:
            raise ValueError("Invalid scaffold output path: " + name)
        if (target / name).resolve() != target / name:
            raise ValueError("Redirected scaffold output: " + name)
    specifications: tuple[dict[str, Any], ...] = ()
    if options.spec_scaffold is not None:
        specifications = tuple(planned_specifications(project, scaffold_config(options.spec_scaffold)))
    return ScaffoldPlan(options, project, files, inputs, question, tuple(sorted(set(generated))), specifications)


def scaffold_project(options: ScaffoldOptions) -> Path:
    """Create the validated initial files, with no implicit commit."""
    return initialize_application(options).target


def apply_scaffold(plan: ScaffoldPlan) -> Path:
    """Create the planned files; canonical starter specifications are written by initialize_application."""
    options = plan.options
    target = options.target_dir
    if _selected_project(options) != plan.project or any(
        _sha(path) != identity for path, identity in plan.inputs.items()
    ):
        raise ValueError("Scaffold inputs changed; inspect a new preview before applying")
    _empty_target(options)
    created: dict[Path, bytes] = {}
    directories: set[Path] = set()
    try:
        for name, body in sorted(plan.files.items()):
            path = target / name
            parent = path.parent
            while parent != target:
                if not parent.exists():
                    directories.add(parent)
                parent = parent.parent
            path.parent.mkdir(parents=True, exist_ok=True)
            with path.open("xb") as stream:
                created[path] = body
                stream.write(body)
        if not (target / ".git").exists():
            _git(target, "init", "--quiet", "--initial-branch=main")
        _git(target, "config", "core.hooksPath", ".githooks")
        if _git(target, "config", "--get", "core.hooksPath") != ".githooks":
            raise ValueError("Application Git hook configuration did not read back")
        if any(path.read_bytes() != body for path, body in created.items()):
            raise ValueError("Application files changed before initialization readback")
    except Exception:
        for path, body in created.items():
            if path.resolve() == path and path.is_file() and path.read_bytes() == body:
                path.unlink()
        for path in sorted(directories, key=lambda value: len(value.parts), reverse=True):
            if path.resolve() == path and path.is_dir() and not any(path.iterdir()):
                path.rmdir()
        raise
    return target


def initialize_application(options: ScaffoldOptions, *, plan: ScaffoldPlan | None = None) -> ScaffoldResult:
    """Create the files, apply any requested starter specifications, then read current intake.

    The initial question is read after every effect so an answer written while
    files were being created is not repeated. If that later read fails, the
    already-created files are still reported truthfully with the read failure.
    """
    plan = plan_scaffold(options) if plan is None else plan
    target = apply_scaffold(plan)
    client = AuthorityClient(options.authority_url)
    report = None
    warnings: list[str] = []
    specification_error: dict[str, Any] | None = None
    if options.spec_scaffold is not None:
        try:
            report = scaffold_specs(
                client,
                options.project_id,
                scaffold_config(options.spec_scaffold),
                dry_run=False,
                actor=options.owner,
                reason=f"Starter specifications for {options.project_id} ({options.spec_scaffold} profile)",
            )
        except (AuthorityClientError, ValueError, OSError) as error:
            # Files exist; the starter set is incomplete. Report both truthfully.
            specification_error = {"code": getattr(error, "code", "invalid_scaffold"), "message": str(error)}
            warnings.append("Starter specifications were not completely written; run gt scaffold specs --apply")
    question = None
    intake: dict[str, Any]
    if options.opt_out_core_spec_intake:
        intake = {"status": "disabled"}
    else:
        try:
            state = intake_status(client, options.project_id)
            question = next((row for row in state["slots"] if not row["complete"]), None)
            intake = {
                "status": "complete" if state["complete"] else "incomplete",
                "completed_slots": state["completed_slots"],
                "total_slots": state["total_slots"],
            }
        except (AuthorityClientError, ValueError, OSError) as error:
            intake = {
                "status": "unavailable",
                "error": {"code": getattr(error, "code", "invalid_intake"), "message": str(error)},
            }
    if intake["status"] == "unavailable":
        warnings.append("The intake read after initialization failed; run core-specs next-question")
    return ScaffoldResult(
        target=target,
        project=plan.project,
        paths=tuple(sorted(plan.files)),
        generated_paths=plan.generated_paths,
        initial_question=question,
        intake=intake,
        specifications=report,
        canonical_writes=report.canonical_writes if report else 0,
        warnings=tuple(warnings),
        specification_error=specification_error,
    )


def scaffold_summary(target: Path, profile: str) -> str:
    return f"Application scaffolded at {target}; profile {get_profile(profile).display_name}. No commit created."
