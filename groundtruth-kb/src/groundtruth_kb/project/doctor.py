# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Workstation doctor — ``gt project doctor`` implementation (Layer 3)."""

from __future__ import annotations

import json
import os
import re
import shutil
import sqlite3
import subprocess
import sys
from collections.abc import Callable
from contextlib import suppress
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Literal, ParamSpec, TypeVar

from groundtruth_kb import get_templates_dir
from groundtruth_kb.authority_client import AuthorityClient, AuthorityClientError
from groundtruth_kb.project.managed_registry import (
    FileArtifact,
    GitignorePattern,
    SettingsHookRegistration,
    artifacts_for_doctor,
    find_artifact_by_id,
)
from groundtruth_kb.project.profiles import get_profile

STANDING_BACKLOG_STALE_NO_GO_DAYS = 14
IMPLEMENTATION_ACTIVE_RESOLUTION_STATUSES = frozenset({"in_progress"})
IMPLEMENTATION_ACTIVE_STAGES = frozenset({"implementing"})
_BRIDGE_VERSION_FILE_RE = re.compile(r"^(.+)-(\d{3,})\.md$")
_BRIDGE_FILE_STATUS_RE = re.compile(
    r"^[#>*\-\s`]*(NEW|REVISED|GO|NO-GO|VERIFIED|WITHDRAWN|ADVISORY|DEFERRED|ACCEPTED|BLOCKED)\b",
    re.IGNORECASE,
)
_BRIDGE_DATE_RE = re.compile(r"^Date:\s*(\d{4}-\d{2}-\d{2})(?:\s+UTC)?\s*$", re.IGNORECASE)
_LEGACY_ROOT_MARKERS = (
    "E:\\Claude-Playground",
    "E:\\\\Claude-Playground",
    "E:/Claude-Playground",
    "//e/Claude-Playground",
    "//E/Claude-Playground",
)
_ACTIVE_LEGACY_ROOT_SURFACES = (
    Path(".claude") / "settings.local.json",
    Path(".claude") / "settings.json",
    Path(".codex") / "hooks.json",
)
_TAFE_SCHEMA_REQUIRED_COLUMNS: dict[str, set[str]] = {
    "flow_definitions": {
        "id",
        "version",
        "flow_type",
        "title",
        "status",
        "lifecycle_status",
        "stage_sequence",
        "required_roles_by_stage",
        "auq_gate_positions",
        "never_self_review_stages",
        "deterministic_carve_outs",
        "workspace_isolation",
        "source_spec_ids",
        "changed_by",
        "changed_at",
        "change_reason",
    },
    "flow_instances": {
        "id",
        "version",
        "flow_definition_id",
        "flow_definition_version",
        "flow_type",
        "subject_type",
        "subject_id",
        "status",
        "current_stage_instance_id",
        "metadata",
        "changed_by",
        "changed_at",
        "change_reason",
    },
    "stage_instances": {
        "id",
        "version",
        "flow_instance_id",
        "stage_id",
        "stage_index",
        "required_role",
        "status",
        "claim_status",
        "claimed_by_harness_id",
        "claimed_by_session_id",
        "metadata",
        "changed_by",
        "changed_at",
        "change_reason",
    },
    "flow_events": {
        "id",
        "flow_instance_id",
        "stage_instance_id",
        "event_type",
        "event_at",
        "event_payload",
        "changed_by",
        "changed_at",
        "change_reason",
    },
    "flow_artifacts": {
        "id",
        "flow_instance_id",
        "stage_instance_id",
        "artifact_type",
        "artifact_ref",
        "relationship",
        "status",
        "metadata",
        "changed_by",
        "changed_at",
        "change_reason",
    },
}


def _coerce_string_list(value: Any) -> list[str]:
    if isinstance(value, str):
        return [value] if value else []
    if isinstance(value, list):
        return [item for item in value if isinstance(item, str) and item]
    return []


def _ollama_windows_autostart_finding() -> str | None:
    if not sys.platform.startswith("win"):
        return None

    powershell = (
        shutil.which("powershell.exe") or shutil.which("powershell") or shutil.which("pwsh.exe") or shutil.which("pwsh")
    )
    if not powershell:
        return "PowerShell unavailable for Ollama autostart probe"

    ps_script = r"""
$ErrorActionPreference = 'SilentlyContinue'
$tasks = @(Get-ScheduledTask | Where-Object {
    $_.TaskName -match 'Ollama' -or $_.TaskPath -match 'Ollama'
} | Select-Object -ExpandProperty TaskName)
$services = @(Get-Service | Where-Object {
    $_.Name -match 'Ollama' -or $_.DisplayName -match 'Ollama'
} | Select-Object -ExpandProperty Name)
[pscustomobject]@{
    scheduled_tasks = $tasks
    services = $services
} | ConvertTo-Json -Compress
"""
    run_kwargs: dict[str, Any] = {
        "stdin": subprocess.DEVNULL,
        "capture_output": True,
        "text": True,
        "timeout": 5,
        "check": False,
    }
    if os.name == "nt":
        run_kwargs["creationflags"] = getattr(subprocess, "CREATE_NO_WINDOW", 0)

    try:
        result = subprocess.run(
            [
                powershell,
                "-NoLogo",
                "-NoProfile",
                "-NonInteractive",
                "-ExecutionPolicy",
                "Bypass",
                "-Command",
                ps_script,
            ],
            **run_kwargs,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return f"Ollama autostart probe failed: {exc}"

    if result.returncode != 0:
        detail = (result.stderr or result.stdout or "").strip()
        return f"Ollama autostart probe exited {result.returncode}: {detail}"

    try:
        payload = json.loads((result.stdout or "{}").strip() or "{}")
    except json.JSONDecodeError as exc:
        return f"Ollama autostart probe returned non-JSON output: {exc}"

    scheduled_tasks = _coerce_string_list(payload.get("scheduled_tasks"))
    services = _coerce_string_list(payload.get("services"))
    if scheduled_tasks or services:
        return None
    return "Ollama autostart not detected; no matching Windows scheduled task or service"


_ACTIVE_LEGACY_ROOT_GLOBS = (
    "AGENTS.md",
    ".claude/rules/*.md",
    ".claude/hooks/*.py",
    ".codex/hooks.json",
    "config/**/*",
    "scripts/**/*.py",
    "groundtruth-kb/src/**/*.py",
    "groundtruth-kb/templates/**/*",
    "groundtruth-kb/tests/fixtures/**/*",
)
_LEGACY_ROOT_EXCLUDED_PARTS = frozenset(
    {
        "__pycache__",
        ".pytest_cache",
        "_drift-backup-2026-04-23-S304",
        "archive",
        "pre-flight-results",
        "session-tmp",
        "worktrees",
    }
)
_LEGACY_ROOT_PATTERN_SCRIPT_NAMES = frozenset(
    {
        "doctor.py",
        "migrate_root_to_gtkb.py",
        "wrap_scan_hygiene.py",
    }
)
_LEGACY_ROOT_ALLOWED_CONTEXT_RE = re.compile(
    r"archive[- ]only|not a live|must not be (?:used|treated)|forbidden_aliases|retired|migration|migrate|"
    r"legacy[-_]root|hygiene|pattern|_LEGACY_ROOT_|No active control-surface",
    re.IGNORECASE,
)


@dataclass
class ToolCheck:
    """Result of checking a single tool or project file."""

    name: str
    required: bool
    found: bool
    version: str | None = None
    min_version: str | None = None
    status: Literal["pass", "fail", "warning", "info"] = "pass"
    message: str = ""
    auto_installable: bool = False


@dataclass
class DoctorReport:
    """Aggregate readiness report from all checks."""

    checks: list[ToolCheck] = field(default_factory=list)
    profile: str = "local-only"
    overall: Literal["pass", "fail", "warning"] = "pass"

    def __post_init__(self) -> None:
        self._compute_overall()

    def _compute_overall(self) -> None:
        if any(c.status == "fail" and c.required for c in self.checks):
            self.overall = "fail"
        elif any(c.status == "warning" for c in self.checks):
            self.overall = "warning"
        else:
            self.overall = "pass"


# ── Tool detection ────────────────────────────────────────────────────


def _run_cmd(cmd: list[str], *, timeout: int = 10) -> tuple[bool, str]:
    """Run a command and return (success, stdout)."""
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return r.returncode == 0, r.stdout.strip()
    except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
        return False, ""


def _parse_version(output: str) -> str | None:
    """Extract a version-like string from command output."""
    import re

    m = re.search(r"(\d+\.\d+[\.\d]*)", output)
    return m.group(1) if m else None


def _version_ge(actual: str, minimum: str) -> bool:
    """Check if actual version >= minimum version."""

    def to_tuple(v: str) -> tuple[int, ...]:
        return tuple(int(x) for x in v.split(".") if x.isdigit())

    try:
        return to_tuple(actual) >= to_tuple(minimum)
    except (ValueError, TypeError):
        return False


def _check_python() -> ToolCheck:
    v = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    ok = sys.version_info >= (3, 11)
    return ToolCheck(
        name="Python",
        required=True,
        found=True,
        version=v,
        min_version="3.11",
        status="pass" if ok else "fail",
        message=f"Python {v}" if ok else f"Python {v} — requires 3.11+",
    )


def _check_tool(
    name: str,
    cmd: list[str],
    *,
    required: bool = True,
    min_version: str | None = None,
    auto_installable: bool = False,
    install_hint: str = "",
) -> ToolCheck:
    """Generic tool checker."""
    path = shutil.which(cmd[0])
    if not path:
        return ToolCheck(
            name=name,
            required=required,
            found=False,
            min_version=min_version,
            status="fail" if required else "warning",
            message=f"{name} not found" + (f". Install: {install_hint}" if install_hint else ""),
            auto_installable=auto_installable,
        )

    ok, output = _run_cmd(cmd)
    version = _parse_version(output) if ok else None

    status: Literal["pass", "fail", "warning"] = "pass"
    message = f"{name} {version}" if version else f"{name} found"

    if min_version and version and not _version_ge(version, min_version):
        status = "fail" if required else "warning"
        message = f"{name} {version} — requires {min_version}+"

    return ToolCheck(
        name=name,
        required=required,
        found=True,
        version=version,
        min_version=min_version,
        status=status,
        message=message,
        auto_installable=auto_installable,
    )


def _check_git() -> ToolCheck:
    return _check_tool("Git", ["git", "--version"], install_hint="https://git-scm.com/downloads")


def _check_docker() -> ToolCheck:
    return _check_tool(
        "Docker",
        ["docker", "--version"],
        required=False,
        install_hint="https://docs.docker.com/get-docker/",
    )


def _check_node() -> ToolCheck:
    return _check_tool(
        "Node.js",
        ["node", "--version"],
        required=False,
        min_version="20",
        install_hint="https://nodejs.org/",
    )


def _check_azure_cli() -> ToolCheck:
    return _check_tool(
        "Azure CLI",
        ["az", "--version"],
        required=False,
        install_hint="https://aka.ms/installazurecli",
    )


def _check_terraform() -> ToolCheck:
    return _check_tool(
        "Terraform",
        ["terraform", "--version"],
        required=False,
        install_hint="https://developer.hashicorp.com/terraform/install",
    )


def _check_claude_code() -> ToolCheck:
    """Check Claude Code CLI availability (not auth validation)."""
    return _check_tool(
        "Claude Code (availability)",
        ["claude", "--version"],
        required=False,
        install_hint="npm install -g @anthropic-ai/claude-code",
        auto_installable=True,
    )


def _check_codex() -> ToolCheck:
    """Check Codex CLI availability."""
    return _check_tool(
        "Codex CLI",
        ["codex", "--version"],
        required=False,
        install_hint="See Codex documentation for installation",
    )


def _check_ruff(target: Path) -> ToolCheck:
    # Resolve ruff in target path venv-first (WI-4434 / HYG-011)
    venv_py = None
    for rel in ("groundtruth-kb/.venv/Scripts/python.exe", "groundtruth-kb/.venv/bin/python"):
        candidate = target / rel
        if candidate.is_file():
            venv_py = candidate
            break

    candidates = []
    if venv_py:
        candidates.append(([str(venv_py), "-m", "ruff"], "venv"))
    candidates.append(([sys.executable, "-m", "ruff"], "sys"))
    path_ruff = shutil.which("ruff")
    if path_ruff:
        candidates.append(([path_ruff], "path"))

    resolved_cmd = None
    resolved_type = None
    for cmd, cmd_type in candidates:
        try:
            ok, output = _run_cmd(cmd + ["--version"])
            if ok:
                resolved_cmd = cmd
                resolved_type = cmd_type
                break
        except (OSError, Exception):
            continue

    name = "ruff"
    if resolved_cmd is None:
        has_venv = venv_py is not None
        return ToolCheck(
            name=name,
            required=False,
            found=False,
            status="fail" if has_venv else "warning",
            message="ruff not found in groundtruth-kb/.venv. Install: pip install ruff"
            if has_venv
            else "ruff not found. Install: pip install ruff",
            auto_installable=True,
        )

    # Resolve version
    ok, output = _run_cmd(resolved_cmd + ["--version"])
    version = _parse_version(output) if ok else None

    status: Literal["pass", "fail", "warning", "info"] = "pass"
    message = f"ruff {version}" if version else "ruff found"
    if resolved_type == "venv":
        message += " (resolved from groundtruth-kb/.venv)"
    return ToolCheck(
        name=name,
        required=False,
        found=True,
        version=version,
        status=status,
        message=message,
        auto_installable=True,
    )


def _check_gh_cli() -> ToolCheck:
    check = _check_tool(
        "GitHub CLI",
        ["gh", "--version"],
        required=False,
        install_hint="https://cli.github.com/",
    )
    if check.found:
        # Also check auth status
        ok, output = _run_cmd(["gh", "auth", "status"])
        if not ok:
            check.status = "warning"
            check.message += " (not authenticated — run `gh auth login`)"
    return check


# ── Project-level checks ─────────────────────────────────────────────


def _check_groundtruth_toml(target: Path) -> ToolCheck:
    toml_path = target / "groundtruth.toml"
    if not toml_path.exists():
        return ToolCheck(
            name="groundtruth.toml",
            required=True,
            found=False,
            status="fail",
            message="groundtruth.toml not found — run `gt project init` first",
        )
    try:
        import tomllib

        with open(toml_path, "rb") as f:
            tomllib.load(f)
        return ToolCheck(
            name="groundtruth.toml",
            required=True,
            found=True,
            status="pass",
            message="Valid configuration file",
        )
    except Exception as e:  # intentional-catch: validation tool, error -> fail status
        return ToolCheck(
            name="groundtruth.toml",
            required=True,
            found=True,
            status="fail",
            message=f"Parse error: {e}",
        )


def _check_db_schema(target: Path) -> ToolCheck:
    db_path = target / "groundtruth.db"
    if not db_path.exists():
        return ToolCheck(
            name="Knowledge DB",
            required=True,
            found=False,
            status="fail",
            message="groundtruth.db not found",
        )
    try:
        import sqlite3

        conn = sqlite3.connect(str(db_path))
        tables = [r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
        conn.close()
        expected = {"specifications", "tests", "work_items"}
        if expected.issubset(set(tables)):
            return ToolCheck(
                name="Knowledge DB",
                required=True,
                found=True,
                status="pass",
                message=f"Schema OK ({len(tables)} tables)",
            )
        missing = expected - set(tables)
        return ToolCheck(
            name="Knowledge DB",
            required=True,
            found=True,
            status="fail",
            message=f"Missing tables: {missing}",
        )
    except Exception as e:  # intentional-catch: validation tool, error -> fail status
        return ToolCheck(
            name="Knowledge DB",
            required=True,
            found=True,
            status="fail",
            message=f"DB error: {e}",
        )


def _check_application_scope_alignment(target: Path) -> ToolCheck:
    """Validate explicit application_scope/path alignment for specs and tests."""
    name = "Application scope alignment"
    db_path = target / "groundtruth.db"
    if not db_path.exists():
        return ToolCheck(name=name, required=True, found=False, status="fail", message="groundtruth.db not found")
    try:
        from groundtruth_kb.project.application_scope import classify_application_scope, scope_path_violations

        conn = sqlite3.connect(str(db_path))
        conn.row_factory = sqlite3.Row
        try:
            spec_cols = {row[1] for row in conn.execute("PRAGMA table_info(specifications)").fetchall()}
            test_cols = {row[1] for row in conn.execute("PRAGMA table_info(tests)").fetchall()}
            missing = []
            if "application_scope" not in spec_cols:
                missing.append("specifications.application_scope")
            if "application_scope" not in test_cols:
                missing.append("tests.application_scope")
            if missing:
                return ToolCheck(
                    name=name,
                    required=True,
                    found=True,
                    status="fail",
                    message=f"Missing application_scope column(s): {', '.join(missing)}",
                )

            violations: list[str] = []
            ambiguous: list[str] = []
            spec_rows = conn.execute(
                "SELECT id, title, source_paths, application_scope FROM current_specifications ORDER BY id"
            ).fetchall()
            test_rows = conn.execute(
                "SELECT id, title, test_file, application_scope FROM current_tests ORDER BY id"
            ).fetchall()
            for row in spec_rows:
                paths: list[str] = []
                if row["source_paths"]:
                    try:
                        raw_paths = json.loads(row["source_paths"])
                    except json.JSONDecodeError:
                        raw_paths = []
                    if isinstance(raw_paths, list):
                        paths = [path for path in raw_paths if isinstance(path, str)]
                for violation in scope_path_violations(row["application_scope"], paths):
                    violations.append(f"spec {row['id']}: {violation}")
                classification = classify_application_scope(row["id"], row["title"], paths)
                if classification.ambiguous and row["application_scope"] is None:
                    ambiguous.append(f"spec {row['id']}: {', '.join(classification.reasons)}")
            for row in test_rows:
                paths = [row["test_file"]] if row["test_file"] else []
                for violation in scope_path_violations(row["application_scope"], paths):
                    violations.append(f"test {row['id']}: {violation}")
                classification = classify_application_scope(row["id"], row["title"], paths)
                if classification.ambiguous and row["application_scope"] is None:
                    ambiguous.append(f"test {row['id']}: {', '.join(classification.reasons)}")
        finally:
            conn.close()

        if violations:
            sample = "; ".join(violations[:5])
            return ToolCheck(
                name=name,
                required=True,
                found=True,
                status="fail",
                message=f"{len(violations)} application-scope alignment violation(s): {sample}",
            )
        if ambiguous:
            sample = "; ".join(ambiguous[:5])
            return ToolCheck(
                name=name,
                required=False,
                found=True,
                status="warning",
                message=f"{len(ambiguous)} ambiguous application-scope candidate(s): {sample}",
            )
        return ToolCheck(
            name=name,
            required=True,
            found=True,
            status="pass",
            message="Application-scope alignment OK",
        )
    except Exception as exc:  # intentional-catch: validation tool, error -> fail status
        return ToolCheck(
            name=name,
            required=True,
            found=True,
            status="fail",
            message=f"Application-scope alignment check failed: {exc}",
        )


def _check_core_spec_intake(
    target: Path, *, project_id: str | None = None, client: AuthorityClient | None = None
) -> ToolCheck:
    """Report current canonical intake; configuration and context flags are not answers."""
    from groundtruth_kb.config import GTConfig, GTConfigError
    from groundtruth_kb.project.core_spec_intake import intake_enabled, next_question

    name = "Core spec intake"
    try:
        if not intake_enabled(target):
            return ToolCheck(name=name, required=False, found=True, status="info", message="Opted out")
        if not project_id:
            return ToolCheck(
                name=name,
                required=False,
                found=False,
                status="warning",
                message="Select the canonical project ID to inspect its core specifications",
            )
        if client is None:
            config = GTConfig.load(config_path=target / "groundtruth.toml", discover=False)
            if not config.authority_url:
                raise ValueError("Configure the native authority before checking intake")
            client = AuthorityClient(config.authority_url)
        question = next_question(client, project_id)
        if question is None:
            return ToolCheck(
                name=name, required=False, found=True, status="pass", message=f"{project_id}: core specs complete"
            )
        return ToolCheck(
            name=name,
            required=False,
            found=True,
            status="warning",
            message=f"{project_id}: next missing slot '{question['label']}' ({question['name']})",
        )
    except (AuthorityClientError, GTConfigError, OSError, ValueError) as error:
        return ToolCheck(
            name=name,
            required=False,
            found=False,
            status="fail",
            message=f"{getattr(error, 'code', 'invalid_intake')}: {error}",
        )


NATIVE_DOCTOR_SCHEMA_VERSION = "1"


def _check_native_application_registry(host: Path, repository_ref: str) -> ToolCheck:
    """isolation:application-registry — the selected application is a catalog entry with a consistent marker.

    Catalog-backed identities only: any number of registered applications is
    ordinary, and no occupancy limit is inferred.
    """
    from groundtruth_kb.isolation.registry_check import ApplicationRegistryError, load_application_catalog
    from groundtruth_kb.isolation.validation import check_slot_markers

    name = "isolation:application-registry"
    application = repository_ref.partition(":")[2]
    try:
        catalog = load_application_catalog(host)
    except (ApplicationRegistryError, OSError, ValueError) as error:
        return ToolCheck(name=name, required=True, found=False, status="fail", message=f"Application catalog: {error}")
    if application not in catalog:
        return ToolCheck(
            name=name,
            required=True,
            found=False,
            status="fail",
            message=f"{application} is not registered in the host catalog; register it before qualification",
        )
    markers = check_slot_markers(host, application)
    if markers["malformed"] or markers["mismatched"]:
        issue = (markers["malformed"] or markers["mismatched"])[0]
        return ToolCheck(
            name=name,
            required=True,
            found=True,
            status="fail",
            message=f"Inconsistent application marker {issue['path']}: "
            + str(issue.get("error") or f"names {issue.get('found_name')} instead of {application}"),
        )
    if not markers["app_toml_present"]:
        return ToolCheck(
            name=name, required=True, found=False, status="fail", message="The application marker is missing"
        )
    return ToolCheck(
        name=name,
        required=True,
        found=True,
        status="pass",
        message=f"{application} is registered with a consistent marker ({len(catalog)} registered applications)",
    )


def inspect_native_application(client: AuthorityClient, project_id: str, host: Path) -> dict[str, Any]:
    """Inspect retained application duties without running retired diagnostics.

    The result is the schema-v1 machine-readable envelope: every check carries
    its ``required`` flag and the ``overall`` verdict follows the report rules
    (a required failure fails; a warning warns). ``status`` mirrors ``overall``
    for existing consumers. No local store is opened and nothing is written.
    """
    from dataclasses import asdict
    from urllib.parse import quote

    from groundtruth_kb.config import GTConfig, GTConfigError
    from groundtruth_kb.isolation.registry_check import (
        ApplicationRegistryError,
        application_slot_path,
        resolve_project_repository,
    )
    from groundtruth_kb.project.scaffold import _git

    project = client.request("GET", "/v1/projects/" + quote(project_id, safe=""))["project"]
    if project["kind"] != "project" or not str(project.get("repository_ref") or "").startswith("application:"):
        raise ValueError("Select an execution project with an application repository")
    registry = _check_native_application_registry(host, project["repository_ref"])
    try:
        target = resolve_project_repository(host, project["repository_ref"])
    except ApplicationRegistryError as error:
        # A catalog or marker inconsistency is reported as the failing registry check; other refusals stand.
        if registry.status != "fail":
            raise ValueError(str(error)) from error
        target = application_slot_path(host, project["repository_ref"].partition(":")[2])
    checks: list[ToolCheck] = []
    profile = "unknown"
    try:
        config = GTConfig.load(config_path=target / "groundtruth.toml", discover=False)
        matches = config.project_root == target and config.authority_url == client.url
        checks.append(
            ToolCheck(
                name="Native authority configuration",
                required=True,
                found=True,
                status="pass" if matches else "fail",
                message="Matches the selected application and authority"
                if matches
                else "Reconcile the selected configuration",
            )
        )
        declared_text, _unreadable = _read_text_for_check(target / "groundtruth.toml", "groundtruth.toml")
        if declared_text is not None:
            with suppress(ValueError):
                import tomllib

                declared = tomllib.loads(declared_text)
                profile = str(declared.get("project", {}).get("profile") or profile)
    except (GTConfigError, OSError, ValueError) as error:
        checks.append(
            ToolCheck(
                name="Native authority configuration", required=True, found=False, status="fail", message=str(error)
            )
        )
    checks.append(registry)
    hook = target / ".githooks/reference-transaction"
    canonical = host / ".githooks/reference-transaction"
    hook_matches = (
        hook.is_file()
        and canonical.is_file()
        and hook.resolve() == hook
        and hook.read_bytes() == canonical.read_bytes()
        and _git(target, "config", "--get", "core.hooksPath", required=False) in {".githooks", "./.githooks"}
    )
    checks.append(
        ToolCheck(
            name="Native commit hook",
            required=True,
            found=hook.is_file(),
            status="pass" if hook_matches else "fail",
            message="Installed hook matches; behavioral commit qualification is separate"
            if hook_matches
            else "Install the current native commit hook",
        )
    )
    from groundtruth_kb.project.scaffold import application_files, leaked_platform_paths

    leaked = leaked_platform_paths(application_files(target))
    checks.append(
        ToolCheck(
            name="Platform leakage",
            required=True,
            found=not leaked,
            status="fail" if leaked else "pass",
            message="Platform state or a local authority store is inside the application: " + ", ".join(leaked)
            if leaked
            else "No platform state or local authority store inside the application",
        )
    )
    from groundtruth_kb.project.doctor_isolation import _check_isolation_chroma_regeneratable

    checks.append(_check_isolation_chroma_regeneratable(target))
    rules_dir = _projected_terminology_rules_dir(target)
    if rules_dir is not None:
        checks.append(_check_canonical_terminology(target, profile, rules_dir))
    else:
        checks.append(
            ToolCheck(
                name="canonical terminology",
                required=False,
                found=False,
                status="info",
                message="No projected terminology guidance (no harness selected); definitions come from the native CLI",
            )
        )
    # The intake finding stays last: consumers read the current question from the final check.
    checks.append(_check_core_spec_intake(target, project_id=project_id, client=client))
    report = DoctorReport(checks=checks, profile=profile)
    return {
        "schema_version": NATIVE_DOCTOR_SCHEMA_VERSION,
        "project_id": project_id,
        "repository_ref": project["repository_ref"],
        "target": str(target),
        "profile": report.profile,
        "overall": report.overall,
        "status": report.overall,
        "checks": [asdict(check) for check in report.checks],
        "canonical_writes": 0,
    }


def format_native_doctor_report(result: dict[str, Any]) -> str:
    """Human-readable form of the native application doctor envelope."""
    icons = {"pass": "[OK]", "fail": "[FAIL]", "warning": "[WARN]", "info": "[INFO]"}
    lines = [
        "",
        f"  GroundTruth Application Doctor — {result['project_id']} ({result['repository_ref']})",
        f"  Profile: {result['profile']}  Target: {result['target']}",
        "  " + "=" * 50,
        "",
    ]
    for check in result["checks"]:
        lines.append(f"  {icons[check['status']]:>6}  {check['name']}: {check['message']}")
    lines.append("")
    lines.append(f"  Overall: {icons[result['overall']]} {result['overall'].upper()}")
    failed = [check for check in result["checks"] if check["status"] == "fail" and check["required"]]
    if failed:
        lines.append("")
        lines.append("  Required checks failing:")
        lines.extend(f"    - {check['name']}: {check['message']}" for check in failed)
    lines.append("")
    return "\n".join(lines)


def _connect_readonly_sqlite(db_path: Path) -> sqlite3.Connection:
    return sqlite3.connect(f"{db_path.resolve().as_uri()}?mode=ro", uri=True)


def _decode_tafe_json(value: Any, *, field: str, flow_id: str, findings: list[str]) -> Any:
    try:
        return json.loads(value or "null")
    except (TypeError, json.JSONDecodeError) as exc:
        findings.append(f"{flow_id} {field} invalid JSON: {exc}")
        return None


def _orphan_citation_audit_script(target: Path) -> Path:
    target_script = target / "scripts" / "orphan_citation_audit.py"
    if target_script.exists():
        return target_script
    return Path(__file__).resolve().parents[4] / "scripts" / "orphan_citation_audit.py"


def _orphan_citation_severity(target: Path) -> Literal["warning", "fail"]:
    env_value = os.environ.get("GTKB_ORPHAN_CITATION_SEVERITY", "").strip().lower()
    if env_value in {"warning", "fail"}:
        return env_value  # type: ignore[return-value]

    toml_path = target / "groundtruth.toml"
    if not toml_path.exists():
        return "warning"
    try:
        import tomllib

        data = tomllib.loads(_require_utf8_text(toml_path))
    except Exception:  # intentional-catch: quality gate waiver
        return "warning"
    doctor_config = data.get("doctor", {}) if isinstance(data, dict) else {}
    severity = str(doctor_config.get("orphan_citations", "")).strip().lower()
    return "fail" if severity == "fail" else "warning"


def _provider_routing(target: Path, provider: str) -> tuple[ToolCheck, tuple[str, ...]]:
    """Inspect only this provider's generated routing; this grants no role or effect authority."""
    import tomllib

    from groundtruth_kb.session.worktree import SessionWorktreeError, _artifact_path

    name = f"{provider} routing configuration"
    root = target / ".api-harness" / provider
    try:
        path = _artifact_path(target, Path(".api-harness") / provider / "routing.toml")
    except SessionWorktreeError:
        return ToolCheck(
            name=name,
            required=False,
            found=False,
            status="fail",
            message="Provider configuration path is redirected; configuration was not read",
        ), ()
    if not root.exists():
        return ToolCheck(
            name=name, required=False, found=False, status="info", message=f"{provider} is not projected here"
        ), ()
    if not path.is_file():
        return ToolCheck(
            name=name,
            required=False,
            found=False,
            status="warning",
            message=f"{path.relative_to(target).as_posix()} is missing",
        ), ()
    try:
        data = tomllib.loads(_require_utf8_text(path))
    except (OSError, tomllib.TOMLDecodeError) as exc:
        return ToolCheck(
            name=name, required=False, found=True, status="fail", message=f"Provider routing is unreadable: {exc}"
        ), ()
    models = data.get("models")
    routing = data.get("routing")
    findings = []
    model_ids = []
    if data.get("schema_version") != 1:
        findings.append("schema_version must be 1")
    if not isinstance(models, dict) or not models:
        findings.append("no model rows")
        models = {}
    for key, row in models.items():
        if not isinstance(row, dict) or row.get("provider") != provider:
            findings.append(f"model {key} does not belong to this provider projection")
            continue
        model_id = row.get("model_id")
        if not isinstance(model_id, str) or not model_id.strip():
            findings.append(f"model {key} has no model_id")
        else:
            model_ids.append(model_id)
        tools = row.get("allowed_tools")
        if row.get("tool_calling_supported") is not True:
            findings.append(f"model {key} does not declare tool calling")
        if (
            not isinstance(tools, list)
            or not tools
            or any(tool not in ("Read", "Write", "Edit", "Grep", "Glob", "Bash") for tool in tools)
        ):
            findings.append(f"model {key} has an invalid tool subset")
    selected = routing.get(provider) if isinstance(routing, dict) else None
    if (
        not isinstance(selected, dict)
        or not isinstance(selected.get("default_model"), str)
        or selected["default_model"] not in models
    ):
        findings.append("default_model does not resolve to a provider model")
    elif isinstance(routing, dict) and set(routing) != {provider}:
        findings.append("routing contains another provider's configuration")
    if findings:
        return ToolCheck(name=name, required=False, found=True, status="fail", message="; ".join(findings)), ()
    return ToolCheck(
        name=name,
        required=False,
        found=True,
        status="pass",
        message=f"{provider} routing references resolve; runtime and host qualification are separate",
    ), tuple(model_ids)


def _check_provider_routing(target: Path, provider: str) -> ToolCheck:
    return _provider_routing(target, provider)[0]


def _check_ollama_harness(target: Path) -> ToolCheck:
    """Check the provider's own routing and the configured local Ollama host, without role mirrors."""
    import urllib.error
    import urllib.request
    from urllib.parse import urlsplit

    from groundtruth_kb.authority_client import AuthorityClientError
    from groundtruth_kb.config import GTConfigError

    check, model_ids = _provider_routing(target, "ollama")
    if check.status != "pass":
        return check
    name = "Ollama host readiness"
    try:
        installations = [row for row in _native_harness_installations(target) if row.get("harness_name") == "ollama"]
    except (AuthorityClientError, GTConfigError) as exc:
        return ToolCheck(
            name=name,
            required=False,
            found=False,
            status="warning",
            message=f"Current installation metadata unavailable; host readiness unverified: {exc}",
        )
    if len(installations) != 1:
        return ToolCheck(
            name=name,
            required=False,
            found=bool(installations),
            status="warning",
            message="One active Ollama installation is required to identify the host to inspect",
        )
    surfaces = installations[0].get("invocation_surfaces")
    headless = surfaces.get("headless") if isinstance(surfaces, dict) else None
    argv = headless.get("argv") if isinstance(headless, dict) else None
    if not isinstance(argv, list) or not argv or not all(isinstance(arg, str) for arg in argv):
        return ToolCheck(
            name=name, required=False, found=True, status="fail", message="Ollama installation argv is malformed"
        )
    endpoints = []
    for index, arg in enumerate(argv):
        if arg == "--endpoint":
            endpoints.append(argv[index + 1] if index + 1 < len(argv) else "")
        elif arg.startswith("--endpoint="):
            endpoints.append(arg.partition("=")[2])
    endpoint = endpoints[0] if endpoints else "http://localhost:11434"
    try:
        parsed = urlsplit(endpoint)
        valid_endpoint = (
            parsed.scheme in {"http", "https"}
            and parsed.hostname
            and not parsed.username
            and not parsed.password
            and not parsed.query
            and not parsed.fragment
            and parsed.path in {"", "/"}
        )
        _ = parsed.port
    except ValueError:
        valid_endpoint = False
    if len(endpoints) > 1 or not valid_endpoint:
        return ToolCheck(
            name=name,
            required=False,
            found=True,
            status="fail",
            message="Ollama endpoint metadata is invalid; values are not echoed",
        )
    if parsed.hostname not in {"localhost", "127.0.0.1", "::1"}:
        return ToolCheck(
            name=name,
            required=False,
            found=True,
            status="warning",
            message="Remote Ollama availability requires host qualification; no local probe was substituted",
        )
    if os.environ.get("GTKB_DOCTOR_OLLAMA_SKIP_PROBE"):
        return ToolCheck(
            name=name,
            required=False,
            found=True,
            status="warning",
            message="Local model probe was skipped; host readiness is unverified",
        )
    findings = []
    try:
        with urllib.request.urlopen(endpoint.rstrip("/") + "/api/tags", timeout=2.0) as response:
            body = json.loads(response.read().decode("utf-8"))
        models = body.get("models") if isinstance(body, dict) else None
        if not isinstance(models, list) or any(
            not isinstance(row, dict) or not isinstance(row.get("name"), str) for row in models
        ):
            findings.append("Ollama model inventory is malformed")
        else:
            advertised = [row["name"] for row in models]
            for model_id in model_ids:
                if not any(model_id == value or value.startswith(model_id + ":") for value in advertised):
                    findings.append(f"Configured model {model_id!r} is not advertised")
    except (urllib.error.URLError, TimeoutError, OSError, UnicodeError, json.JSONDecodeError):
        findings.append("Local Ollama model inventory is unavailable or unreadable")
    if os.environ.get("GTKB_DOCTOR_OLLAMA_SKIP_HOST_READINESS"):
        findings.append("Host autostart inspection was skipped")
    else:
        autostart = _ollama_windows_autostart_finding()
        if autostart:
            findings.append(autostart)
    return ToolCheck(
        name=name,
        required=False,
        found=True,
        status="warning" if findings else "pass",
        message="; ".join(findings)
        if findings
        else "Local model availability and host setup inspected; actual agent execution is unverified",
    )


def _check_cursor_dispatch_readiness(target: Path) -> ToolCheck:
    """Report Cursor launch prerequisites and authentication, not qualification."""

    check_name = "Cursor launch prerequisites"
    try:
        from groundtruth_kb.cursor_readiness import evaluate_readiness  # noqa: PLC0415
    except Exception as exc:  # noqa: BLE001  # intentional-catch: doctor must surface import drift
        return ToolCheck(
            name=check_name,
            required=False,
            found=False,
            status="warning",
            message=f"Packaged Cursor readiness probe unavailable: {type(exc).__name__}",
        )

    try:
        result = evaluate_readiness(project_root=target)
    except Exception as exc:  # noqa: BLE001  # intentional-catch: launch probe is diagnostic
        return ToolCheck(
            name=check_name,
            required=False,
            found=True,
            status="warning",
            message=f"Cursor launch prerequisite probe failed: {type(exc).__name__}",
        )

    valid_report = (
        isinstance(result, dict)
        and type(result.get("probe_passed")) is bool
        and result.get("probe_scope") == "launch_prerequisites_and_authentication"
        and result.get("authority_source") == "native_harness_record"
        and result.get("harness_qualification") == "unqualified"
    )
    if not valid_report:
        return ToolCheck(
            name=check_name,
            required=False,
            found=True,
            status="warning",
            message="Cursor launch probe returned an unsupported report; harness qualification is unverified",
        )

    if result["probe_passed"] is True:
        return ToolCheck(
            name=check_name,
            required=False,
            found=True,
            status="pass",
            message="Cursor launch prerequisites and authentication passed; harness qualification is unverified",
        )

    detail = str(result.get("first_failed_check") or "launch prerequisite or authentication check failed")
    return ToolCheck(
        name=check_name,
        required=False,
        found=True,
        status="warning",
        message=f"Cursor launch prerequisite or authentication check failed: {detail}",
    )


def _check_orphan_citations(target: Path) -> ToolCheck:
    script_path = _orphan_citation_audit_script(target)
    if not script_path.exists():
        return ToolCheck(
            name="Orphan citations",
            required=False,
            found=False,
            status="warning",
            message="orphan_citation_audit.py not found; citation-anchor audit unavailable",
        )

    cmd = [
        sys.executable,
        str(script_path),
        "--root",
        str(target),
        "--db",
        str(target / "groundtruth.db"),
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30, check=False)
        payload = json.loads(result.stdout or "{}")
    except (json.JSONDecodeError, OSError, subprocess.TimeoutExpired) as exc:
        return ToolCheck(
            name="Orphan citations",
            required=False,
            found=True,
            status="warning",
            message=f"orphan citation audit did not return usable JSON: {exc}",
        )

    orphan_count = len(payload.get("orphans") or [])
    scanned_files = payload.get("scanned_files", 0)
    if result.returncode not in {0, 1}:
        return ToolCheck(
            name="Orphan citations",
            required=False,
            found=True,
            status="warning",
            message=f"orphan citation audit failed with exit {result.returncode}",
        )
    if orphan_count:
        severity = _orphan_citation_severity(target)
        return ToolCheck(
            name="Orphan citations",
            required=False,
            found=True,
            status=severity,
            message=f"{orphan_count} orphan citation(s) found across {scanned_files} scanned file(s)",
        )
    return ToolCheck(
        name="Orphan citations",
        required=False,
        found=True,
        status="pass",
        message=f"No orphan citations found across {scanned_files} scanned file(s)",
    )


def _check_skill_health(target: Path) -> ToolCheck:
    """WI-4431 / FAB-19: Skill-health static checker (Layer 3 doctor check).

    Runs check_skill_health.py in JSON/warn-only mode and reports the count
    of skill-health findings. Surfaced at WARN severity (advisory).
    """
    script_path = target / "scripts" / "check_skill_health.py"
    if not script_path.exists():
        return ToolCheck(
            name="Skill health",
            required=False,
            found=False,
            status="warning",
            message="check_skill_health.py not found; skill-health checker unavailable",
        )

    cmd = [
        sys.executable,
        str(script_path),
        "--project-root",
        str(target),
        "--json",
        "--warn-only",
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30, check=False)
        payload = json.loads(result.stdout or "{}")
    except (json.JSONDecodeError, OSError, subprocess.TimeoutExpired) as exc:
        return ToolCheck(
            name="Skill health",
            required=False,
            found=True,
            status="warning",
            message=f"skill-health checker did not return usable JSON: {exc}",
        )

    finding_count = payload.get("finding_count", 0)
    skills_scanned = payload.get("skills_scanned", 0)

    if result.returncode != 0:
        return ToolCheck(
            name="Skill health",
            required=False,
            found=True,
            status="warning",
            message=f"skill-health checker failed with exit {result.returncode}",
        )

    if finding_count:
        return ToolCheck(
            name="Skill health",
            required=False,
            found=True,
            status="warning",
            message=f"{finding_count} skill health finding(s) found across {skills_scanned} scanned skill(s)",
        )

    return ToolCheck(
        name="Skill health",
        required=False,
        found=True,
        status="pass",
        message=f"No skill health findings found across {skills_scanned} scanned skill(s)",
    )


def _check_hooks(target: Path, profile_name: str) -> ToolCheck:
    hooks_dir = target / ".claude" / "hooks"
    if not hooks_dir.exists():
        return ToolCheck(
            name="Hooks",
            required=True,
            found=False,
            status="fail",
            message=".claude/hooks/ directory not found",
        )
    # Required-hook set is sourced from the managed-artifact registry
    # (``doctor_required_profiles`` axis). Empty set for unknown profiles
    # falls back to no required hooks rather than crashing.
    required_hooks = {
        Path(artifact.target_path).name
        for artifact in artifacts_for_doctor(profile_name, class_="hook")
        if isinstance(artifact, FileArtifact)
    }

    present = {f.name for f in hooks_dir.glob("*.py")}
    missing = required_hooks - present
    if missing:
        return ToolCheck(
            name="Hooks",
            required=True,
            found=True,
            status="warning",
            message=f"Missing hooks: {', '.join(sorted(missing))}",
        )
    return ToolCheck(
        name="Hooks",
        required=True,
        found=True,
        status="pass",
        message=f"{len(present)} hook(s) present",
    )


def _check_rules(target: Path, profile_name: str) -> ToolCheck:
    rules_dir = target / ".claude" / "rules"
    if not rules_dir.exists():
        return ToolCheck(
            name="Rules",
            required=True,
            found=False,
            status="fail",
            message=".claude/rules/ directory not found",
        )
    present = {f.name for f in rules_dir.glob("*.md")}
    if not present:
        return ToolCheck(
            name="Rules",
            required=True,
            found=True,
            status="warning",
            message="No rule files found",
        )
    return ToolCheck(
        name="Rules",
        required=True,
        found=True,
        status="pass",
        message=f"{len(present)} rule(s) present",
    )


def _check_active_legacy_root_references(target: Path) -> ToolCheck:
    """Hard-fail active surfaces that still treat the retired archive root as live authority."""
    findings: list[str] = []
    for relative_path in _iter_active_legacy_root_surfaces(target):
        path = target / relative_path
        if not path.is_file():
            continue
        try:
            lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
        except OSError as exc:
            return ToolCheck(
                name="Active legacy-root references",
                required=True,
                found=True,
                status="fail",
                message=f"Could not read active control surface {relative_path.as_posix()}: {exc}",
            )
        for line_index, line in enumerate(lines):
            if any(marker in line for marker in _LEGACY_ROOT_MARKERS) and not _legacy_root_reference_is_allowed(
                relative_path, lines, line_index
            ):
                line_number = line_index + 1
                findings.append(f"{relative_path.as_posix()}:{line_number}")
    if findings:
        return ToolCheck(
            name="Active legacy-root references",
            required=True,
            found=True,
            status="fail",
            message=(
                "Active control surface references retired E:\\Claude-Playground archive root: "
                + ", ".join(findings[:8])
                + (f", ... (+{len(findings) - 8} more)" if len(findings) > 8 else "")
            ),
        )
    return ToolCheck(
        name="Active legacy-root references",
        required=True,
        found=True,
        status="pass",
        message="No active control-surface references to E:\\Claude-Playground",
    )


def _iter_active_legacy_root_surfaces(target: Path) -> list[Path]:
    """Return active files whose legacy-root references should be inspected."""
    paths: set[Path] = set(_ACTIVE_LEGACY_ROOT_SURFACES)
    for pattern in _ACTIVE_LEGACY_ROOT_GLOBS:
        for path in target.glob(pattern):
            if not path.is_file():
                continue
            try:
                relative_path = path.relative_to(target)
            except ValueError:
                continue
            if any(part in _LEGACY_ROOT_EXCLUDED_PARTS for part in relative_path.parts):
                continue
            paths.add(relative_path)
    return sorted(paths, key=lambda item: item.as_posix())


def _legacy_root_reference_is_allowed(relative_path: Path, lines: list[str], line_index: int) -> bool:
    """Classify archive/migration/hygiene mentions as non-live references."""
    if relative_path.name in _LEGACY_ROOT_PATTERN_SCRIPT_NAMES:
        return True
    start = max(0, line_index - 2)
    end = min(len(lines), line_index + 3)
    context = "\n".join(lines[start:end])
    return bool(_LEGACY_ROOT_ALLOWED_CONTEXT_RE.search(context))


# Sub-slice E doctor invariants per amended DCL-REQUIREMENTS-COLLECTION-HOOK-CONTRACT-001 v2.
# Enforces: GOV-REQUIREMENTS-COLLECTION-HOOK-001 v2; DCL DOCTOR INVARIANTS section.
# See bridge/gtkb-gov-auq-enforcement-stack-slice-e-requirements-collector-2026-05-04 for approved scope.


def _check_registered_hooks_tracked(target: Path) -> ToolCheck:
    """WI-4457: WARN when a registered governance hook script is untracked in git.

    For every hook script path referenced in tracked ``.claude/settings.json``
    event arrays (PreToolUse / PostToolUse / UserPromptSubmit / SessionStart /
    Stop), assert the file is tracked in git (``git ls-files --error-unmatch``).
    Sibling check: untracked ``.py`` files under ``.claude/hooks/`` (which the
    ``!.claude/hooks/*.py`` ``.gitignore`` negation already opts into git).

    Fail-soft ``warning`` (never ``fail``) so a deliberately-untracked local hook
    never blocks ``doctor``; the advisory is visible at session start before any
    tool call can hit the WI-4449 session-block class (registered + on-disk +
    untracked governance hook). No prior doctor check confirmed git-tracking of
    registered hook scripts; that absence is the surface this check closes.
    """
    import json as _json
    import re as _re

    name = "registered hooks git-tracked"
    settings_path = target / ".claude" / "settings.json"
    if not settings_path.exists():
        return ToolCheck(
            name=name,
            required=False,
            found=False,
            status="info",
            message=".claude/settings.json missing; no registered hooks to verify",
        )

    try:
        data = _json.loads(_require_utf8_text(settings_path))
    except (OSError, _json.JSONDecodeError) as exc:
        return ToolCheck(
            name=name,
            required=False,
            found=True,
            status="warning",
            message=f"Malformed .claude/settings.json: {exc}",
        )

    events = ("PreToolUse", "PostToolUse", "UserPromptSubmit", "SessionStart", "Stop")
    hooks = data.get("hooks") or {}
    referenced: set[str] = set()
    for event in events:
        for group in hooks.get(event) or []:
            if not isinstance(group, dict):
                continue
            for h in group.get("hooks", []):
                if not isinstance(h, dict):
                    continue
                command = h.get("command") or ""
                for match in _re.finditer(r"\.claude[\\/]hooks[\\/][A-Za-z0-9_.\-]+\.py", command):
                    referenced.add(match.group(0).replace("\\", "/"))

    untracked_registered: list[str] = []
    for rel in sorted(referenced):
        script = target / rel
        if not script.exists():
            # Registered-but-missing-on-disk is a distinct defect class; out of
            # scope for this tracking check (which only flags present-but-untracked).
            continue
        ok, _out = _run_cmd(["git", "-C", str(target), "ls-files", "--error-unmatch", rel])
        if not ok:
            untracked_registered.append(rel)

    untracked_siblings: list[str] = []
    if (target / ".claude" / "hooks").is_dir():
        ok, out = _run_cmd(["git", "-C", str(target), "ls-files", "--others", "--exclude-standard", ".claude/hooks"])
        if ok and out:
            for line in out.splitlines():
                candidate = line.strip().replace("\\", "/")
                if candidate.endswith(".py"):
                    untracked_siblings.append(candidate)

    if untracked_registered or untracked_siblings:
        parts: list[str] = []
        if untracked_registered:
            parts.append("registered-but-untracked: " + ", ".join(untracked_registered))
        if untracked_siblings:
            parts.append("untracked .claude/hooks/*.py: " + ", ".join(sorted(set(untracked_siblings))))
        return ToolCheck(
            name=name,
            required=False,
            found=True,
            status="warning",
            message="; ".join(parts) + " — run `git add` (registered governance hooks must be committed)",
        )

    return ToolCheck(
        name=name,
        required=False,
        found=True,
        status="pass",
        message="all registered hook scripts are git-tracked",
    )


def _check_skill_rename_reference_sweep(target: Path) -> ToolCheck:
    """WI-5668: WARN while any pre-rename bare skill-directory references remain.

    The GTKB-SKILL-RENAME-REFERENCE-SWEEP program renamed the ``.claude/skills/``
    directories to a ``gtkb-`` prefix (``DELIB-202667105`` / ``DELIB-202667106``).
    This deterministic completion gate (``GOV-DETERMINISTIC-SERVICES-PRINCIPLE-001``)
    counts remaining tracked references to the bare pre-rename skill dirs and WARNs
    until the count reaches zero, so the sweep's "done" is objective rather than a
    session judgment call.

    Self-maintaining: the bare-name set is derived from the current ``gtkb-`` skill
    dirs (for each ``gtkb-<name>`` dir, ``<name>`` is a stale bare name), so no
    hardcoded list is needed and the check adapts to future renames.

    ``required=False`` — a surfaced warning, never a hard release-block — while the
    multi-slice sweep is in flight. Append-only / historical / runtime trees that
    intentionally retain bare references are excluded.
    """
    name = "skill-rename reference sweep"
    skills_dir = target / ".claude" / "skills"
    if not skills_dir.is_dir():
        return ToolCheck(
            name=name,
            required=False,
            found=False,
            status="info",
            message="no .claude/skills/ directory; nothing to verify",
        )

    prefix = "gtkb-"
    bare_names = sorted(
        d.name[len(prefix) :]
        for d in skills_dir.iterdir()
        if d.is_dir() and d.name.startswith(prefix) and len(d.name) > len(prefix)
    )
    if not bare_names:
        return ToolCheck(
            name=name,
            required=False,
            found=True,
            status="info",
            message="no gtkb- skill dirs found; no bare pre-rename names to sweep",
        )

    alt = "|".join(re.escape(b) for b in bare_names)
    grep_pattern = rf'skills/({alt})/|"skills"[ ]*/[ ]*"({alt})"'
    try:
        completed = subprocess.run(
            ["git", "-C", str(target), "grep", "-n", "-E", grep_pattern],
            capture_output=True,
            text=False,
            timeout=30,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
        return ToolCheck(
            name=name,
            required=False,
            found=True,
            status="info",
            message="git grep unavailable; skill-rename reference scan skipped",
        )
    # git grep exit codes: 0 = matches found, 1 = no matches (a PASS), >1 = error.
    if completed.returncode > 1:
        return ToolCheck(
            name=name,
            required=False,
            found=True,
            status="info",
            message="git grep error; skill-rename reference scan skipped",
        )

    excluded = ("bridge/", "RETIRED-", "BARRED-", "archive/", "archive-", ".gtkb-state/")
    hits: list[str] = []
    if completed.returncode == 0:
        stdout_text = (
            completed.stdout.decode("utf-8", errors="replace") if isinstance(completed.stdout, bytes) else None
        )
        if not stdout_text:
            return ToolCheck(
                name=name,
                required=False,
                found=True,
                status="warning",
                message="skill-rename sweep scan unavailable: git grep output could not be decoded",
            )
        for line in stdout_text.splitlines():
            path_part, sep, rest = line.replace("\\", "/").partition(":")
            if not sep:
                continue
            if any(path_part.startswith(p) for p in excluded):
                continue
            lineno_part = rest.partition(":")[0]
            hits.append(f"{path_part}:{lineno_part}")

    count = len(hits)
    if count:
        sample = ", ".join(hits[:8])
        more = f" (+{count - 8} more)" if count > 8 else ""
        return ToolCheck(
            name=name,
            required=False,
            found=True,
            status="warning",
            message=(
                f"{count} pre-rename bare skill-dir reference(s) remain; "
                f"GTKB-SKILL-RENAME-REFERENCE-SWEEP incomplete: {sample}{more}"
            ),
        )

    return ToolCheck(
        name=name,
        required=False,
        found=True,
        status="pass",
        message="0 pre-rename bare skill-dir references remain; sweep complete",
    )


def _check_harness_projection_conformance(target: Path) -> ToolCheck:
    """Compare declared targets with the baseline and their exact engine plans."""
    import importlib.util

    name = "Harness projection conformance"
    script = target / "scripts/check_harness_parity.py"
    if not script.is_file() or script.resolve() != script:
        return ToolCheck(
            name=name,
            required=True,
            found=False,
            status="fail",
            message="Canonical projection checker is missing or redirected",
        )
    try:
        spec = importlib.util.spec_from_file_location("_gtkb_doctor_projection_check", script)
        if spec is None or spec.loader is None:
            raise ImportError("Cannot load canonical projection checker")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        report = module.check_harness_parity(target, harness="all")
        failed = [name for name, result in report["harnesses"].items() if result["status"] != "pass"]
        message = (
            "Installed outputs match the canonical baseline and projector"
            if report["status"] == "pass"
            else f"Projection correction required: {', '.join(failed) or report['issues']}"
        )
        return ToolCheck(
            name=name,
            required=True,
            found=True,
            status=report["status"],
            message=message + "; actual hook invocation remains separate qualification",
        )
    except Exception as exc:  # intentional-catch: present checker failure as a diagnostic
        return ToolCheck(
            name=name, required=True, found=True, status="fail", message=f"Projection check unavailable: {exc}"
        )


# FAB-08 (HYG-053): stale clean-adopter test-sandbox auto-prune.


def _required_bridge_rule_filenames(profile_name: str) -> tuple[str, ...]:
    """Return the basename set of rules whose doctor_required_profiles
    includes *profile_name*.

    Sourced from the managed-artifact registry rather than a hardcoded
    tuple. Preserves the current bridge-profile set
    (``file-bridge-protocol.md``, ``bridge-essential.md``,
    ``deliberation-protocol.md``) while letting the registry add or remove
    rules without code changes.
    """
    return tuple(
        Path(artifact.target_path).name
        for artifact in artifacts_for_doctor(profile_name, class_="rule")
        if isinstance(artifact, FileArtifact)
    )


def _check_scanner_safe_writer_drift(target: Path, profile_name: str) -> ToolCheck:
    """Check scanner-safe-writer hook registration and log-ignore drift.

    Applies only to bridge-enabled profiles. Reports:

    - ``pass`` (``required=False``): base profile — the hook isn't scaffolded
      there, so there's no drift to surface.
    - ``fail``: bridge profile and the hook file itself is missing.
    - ``warning``: the hook file is present but drift exists — the
      PreToolUse registration in ``.claude/settings.json`` is missing OR the
      ``.claude/hooks/*.log`` pattern is missing from ``.gitignore``. Both
      are remediable via ``gt project upgrade --apply``.
    - ``pass``: the hook file is present, the PreToolUse registration is
      present, and the gitignore pattern is present.

    Defensive against malformed ``settings.json`` shape: treats non-dict
    roots, non-dict ``hooks``, non-list ``PreToolUse``, and non-dict entries
    as "registration missing" rather than crashing the doctor check.
    """
    profile = get_profile(profile_name)
    if not profile.includes_bridge:
        return ToolCheck(
            name="scanner-safe-writer",
            required=False,
            found=True,
            status="pass",
            message="not applicable to base profile",
        )

    # Composite-check inputs are resolved from the managed-artifact
    # registry by canonical IDs. This is the C1 Condition 2 contract —
    # three stable IDs that must exist and be unique.
    hook_record = find_artifact_by_id("hook.scanner-safe-writer")
    settings_record = find_artifact_by_id("settings.hook.scanner-safe-writer.pretooluse")
    gitignore_record = find_artifact_by_id("gitignore.hook-logs")
    assert isinstance(hook_record, FileArtifact)
    assert isinstance(settings_record, SettingsHookRegistration)
    assert isinstance(gitignore_record, GitignorePattern)

    hook_file = target / hook_record.target_path
    if not hook_file.exists():
        return ToolCheck(
            name="scanner-safe-writer",
            required=True,
            found=False,
            status="fail",
            message=f"{hook_record.target_path.split('/')[-1]} missing — run `gt project upgrade --apply`",
        )

    settings_path = target / settings_record.target_settings_path
    registered = False
    if settings_path.exists():
        try:
            data: object = json.loads(_require_utf8_text(settings_path))
        except (OSError, json.JSONDecodeError):
            registered = False
        else:
            if isinstance(data, dict):
                raw_hooks = data.get("hooks")
                hooks_dict = raw_hooks if isinstance(raw_hooks, dict) else {}
                raw_pretooluse = hooks_dict.get(settings_record.event)
                pretooluse = raw_pretooluse if isinstance(raw_pretooluse, list) else []
                for entry in pretooluse:
                    if not isinstance(entry, dict):
                        continue
                    entry_hooks = entry.get("hooks", [])
                    if not isinstance(entry_hooks, list):
                        continue
                    for h in entry_hooks:
                        if not isinstance(h, dict):
                            continue
                        cmd = h.get("command", "")
                        if isinstance(cmd, str) and settings_record.hook_filename in cmd:
                            registered = True
                            break
                    if registered:
                        break

    gitignore = target / ".gitignore"
    log_ignored = False
    if gitignore.exists():
        try:
            gi_text = _require_utf8_text(gitignore)
            log_ignored = gitignore_record.pattern in gi_text
        except OSError:
            log_ignored = False

    if not registered or not log_ignored:
        missing: list[str] = []
        if not registered:
            missing.append("settings.json PreToolUse registration")
        if not log_ignored:
            missing.append(".gitignore exclusion of .claude/hooks/*.log")
        return ToolCheck(
            name="scanner-safe-writer",
            required=True,
            found=True,
            status="warning",
            message=(f"hook present but missing: {', '.join(missing)}. Run `gt project upgrade --apply`."),
        )

    return ToolCheck(
        name="scanner-safe-writer",
        required=True,
        found=True,
        status="pass",
        message="hook registered; log ignored",
    )


def _check_safety_gate_registration(target: Path) -> ToolCheck:
    """Check that destructive-gate.py and credential-scan.py are registered
    in tracked .claude/settings.json PreToolUse.

    Returns PASS when both are registered, WARNING when one or both are
    missing from PreToolUse.
    """
    settings_path = target / ".claude" / "settings.json"
    gates = ["destructive-gate.py", "credential-scan.py"]
    missing = [g for g in gates if not _is_command_registered_in_event(settings_path, "PreToolUse", g)]
    if missing:
        return ToolCheck(
            name="safety-gate-registration",
            required=True,
            found=True,
            status="warning",
            message=f"safety gate(s) missing from settings.json PreToolUse: {', '.join(missing)}",
        )
    return ToolCheck(
        name="safety-gate-registration",
        required=True,
        found=True,
        status="pass",
        message="destructive-gate.py and credential-scan.py registered in PreToolUse",
    )


def _derive_paired_hook_id(registration_id: str, event_lowercase: str) -> str:
    """Derive the paired ``hook.<short>`` FileArtifact id from a registration id.

    Registration ids follow the convention
    ``settings.hook.<short>.<event-lowercase>``; the paired hook record is
    ``hook.<short>``. Stripping the ``settings.`` prefix and the
    ``.<event-lowercase>`` suffix yields the paired id.
    """
    stripped = registration_id.removeprefix("settings.")
    suffix = "." + event_lowercase
    if stripped.endswith(suffix):
        stripped = stripped[: -len(suffix)]
    return stripped


def _is_command_registered_in_event(settings_path: Path, event: str, hook_filename: str) -> bool:
    """Return ``True`` iff ``settings.json`` has an entry under
    ``hooks[event]`` whose command references ``hook_filename``.

    Defensive against malformed shapes (non-dict root, non-dict ``hooks``,
    non-list event list, non-dict entries) — all treated as "not
    registered" rather than crashing the doctor check.
    """
    if not settings_path.exists():
        return False
    try:
        data: object = json.loads(_require_utf8_text(settings_path))
    except (OSError, json.JSONDecodeError):
        return False
    if not isinstance(data, dict):
        return False
    raw_hooks = data.get("hooks")
    hooks_dict = raw_hooks if isinstance(raw_hooks, dict) else {}
    raw_event_list = hooks_dict.get(event)
    event_list = raw_event_list if isinstance(raw_event_list, list) else []
    for entry in event_list:
        if not isinstance(entry, dict):
            continue
        entry_hooks = entry.get("hooks", [])
        if not isinstance(entry_hooks, list):
            continue
        for h in entry_hooks:
            if not isinstance(h, dict):
                continue
            cmd = h.get("command", "")
            if isinstance(cmd, str) and hook_filename in cmd:
                return True
    return False


def _ownership_drift_status(
    artifact: FileArtifact | SettingsHookRegistration | GitignorePattern,
) -> Literal["fail", "warning"]:
    if artifact.ownership is None:
        return "warning"
    if artifact.ownership.adopter_divergence_policy == "warn":
        return "warning"
    return "fail"


def _hash_file(path: Path) -> str:
    import hashlib

    return hashlib.sha256(path.read_bytes()).hexdigest()


def _hash_file_normalized(path: Path) -> str:
    """Hash file content with CRLF→LF normalization for EOL-insensitive comparison."""
    import hashlib

    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def _check_managed_artifact_drift(target: Path, profile_name: str) -> ToolCheck:
    """Aggregate doctor-required managed-artifact drift for an adopter project."""
    check_name = "Managed artifact drift"
    try:
        artifacts = artifacts_for_doctor(profile_name)
    # pragma: no cover - defensive boundary around registry parser
    except Exception as exc:  # intentional-catch: quality gate waiver
        return ToolCheck(
            name=check_name,
            required=True,
            found=False,
            status="fail",
            message=f"managed artifact registry unavailable: {exc}",
        )

    if not artifacts:
        return ToolCheck(
            name=check_name,
            required=False,
            found=True,
            status="info",
            message=f"no doctor-required managed artifacts for profile {profile_name}",
        )

    counts = {
        "current": 0,
        "missing": 0,
        "drifted": 0,
        "registration-missing": 0,
        "gitignore-missing": 0,
        "template-missing": 0,
    }
    failures: list[str] = []
    warnings: list[str] = []
    templates_dir = get_templates_dir()

    def record(kind: str, artifact_id: str, status: Literal["fail", "warning"], detail: str) -> None:
        counts[kind] += 1
        entry = f"{artifact_id}: {detail}"
        if status == "fail":
            failures.append(entry)
        else:
            warnings.append(entry)

    for artifact in artifacts:
        if isinstance(artifact, FileArtifact):
            target_path = target / artifact.target_path
            if not target_path.is_file():
                record("missing", artifact.id, "fail", f"{artifact.target_path} missing")
                continue
            template_path = templates_dir / artifact.template_path
            if not template_path.is_file():
                record("template-missing", artifact.id, "fail", f"template {artifact.template_path} missing")
                continue
            try:
                target_hash = _hash_file_normalized(target_path)
                template_hash = _hash_file_normalized(template_path)
            except OSError as exc:
                record("drifted", artifact.id, "fail", f"could not compare {artifact.target_path}: {exc}")
                continue
            if target_hash != template_hash:
                record(
                    "drifted",
                    artifact.id,
                    _ownership_drift_status(artifact),
                    f"{artifact.target_path} differs from template {artifact.template_path}",
                )
                continue
            counts["current"] += 1
            continue

        if isinstance(artifact, SettingsHookRegistration):
            if _is_command_registered_in_event(
                target / artifact.target_settings_path,
                artifact.event,
                artifact.hook_filename,
            ):
                counts["current"] += 1
            else:
                record(
                    "registration-missing",
                    artifact.id,
                    _ownership_drift_status(artifact),
                    f"{artifact.hook_filename} missing from {artifact.target_settings_path} {artifact.event}",
                )
            continue

        if isinstance(artifact, GitignorePattern):
            gitignore = target / ".gitignore"
            try:
                gitignore_text = _require_utf8_text(gitignore) if gitignore.is_file() else ""
            except OSError as exc:
                record("gitignore-missing", artifact.id, "fail", f"could not read .gitignore: {exc}")
                continue
            if artifact.pattern in gitignore_text:
                counts["current"] += 1
            else:
                record(
                    "gitignore-missing",
                    artifact.id,
                    _ownership_drift_status(artifact),
                    f"pattern {artifact.pattern!r} missing from .gitignore",
                )

    status: Literal["pass", "fail", "warning", "info"] = "pass"
    if failures:
        status = "fail"
    elif warnings:
        status = "warning"

    count_text = ", ".join(f"{key}={value}" for key, value in counts.items() if value)
    if not count_text:
        count_text = "no managed artifacts checked"
    details = [*failures[:3], *warnings[: max(0, 3 - len(failures[:3]))]]
    suffix = ""
    remaining = len(failures) + len(warnings) - len(details)
    if remaining > 0:
        suffix = f"; +{remaining} more"
    detail_text = f": {'; '.join(details)}{suffix}" if details else ""

    return ToolCheck(
        name=check_name,
        required=True,
        found=True,
        status=status,
        message=f"{count_text}{detail_text}",
    )


def _check_sot_registry_completeness(target: Path) -> ToolCheck:
    """Validate the platform SoT artifact registry (GOV-PLATFORM-SOT-REGISTRY-001).

    Read the canonical declaration and check its current identity locators and
    load-bearing membership through the five inventory observers. A failed
    observer makes inventory incomplete; historical revision audits and
    packaged copies do not determine whether current state is valid.

    Authority, identity, and membership defects fail closed. A missing registry
    remains an informational skip for adopters that have not enabled the
    platform registry.
    """
    check_name = "SoT registry completeness"
    registry_path = target / "config" / "registry" / "sot-artifacts.toml"

    if not registry_path.is_file():
        return ToolCheck(
            name=check_name,
            required=False,
            found=False,
            status="info",
            message="config/registry/sot-artifacts.toml not present (skip — platform registry only)",
        )

    try:
        from groundtruth_kb.project.registry_control_plane import inspect_registry, load_registry_snapshot
    except Exception as exc:  # pragma: no cover - defensive import boundary  # intentional-catch: quality gate waiver
        return ToolCheck(
            name=check_name,
            required=True,
            found=True,
            status="fail",
            message=f"registry control plane unavailable: {exc}",
        )

    try:
        snapshot = load_registry_snapshot(project_root=target)
        toml_records = list(snapshot.records)
        authority_report = inspect_registry(project_root=target, include_census=True)
    except Exception as exc:  # intentional-catch: authority failures are ERROR severity
        return ToolCheck(
            name=check_name,
            required=True,
            found=True,
            status="fail",
            message=f"coherent registry snapshot failed to load: {exc}",
        )

    failures: list[str] = []

    if not authority_report.get("coherent"):
        failures.append(f"registry generation is not coherent: {authority_report.get('error')}")
    else:
        identity = authority_report["identity_state"]
        if not identity["current"]:
            defects = {
                "missing locators": identity.get("missing", []),
                "object-kind mismatches": identity.get("object_kind_mismatches", []),
                "archived objects still present": identity.get("archived_present", []),
                "invalid paths": identity.get("invalid_paths", []),
            }
            failures.append(
                "registry identity failed: "
                + ", ".join(f"{len(rows)} {kind}" for kind, rows in defects.items())
                + "; "
                + "; ".join(
                    f"{kind}: {row.get('id', '?')} ({row.get('path', '?')})"
                    for kind, rows in defects.items()
                    for row in rows
                )
            )
        membership = authority_report["membership_reconciliation"]
        for failure in membership.get("observer_failures", []):
            failures.append(f"{failure['observer_class']} inventory failed: " + "; ".join(failure["diagnostics"]))
        if not membership["membership_complete"]:
            counts = membership["counts"]
            failures.append(
                "registry membership incomplete: "
                f"{counts['unregistered_load_bearing']} load-bearing gaps, "
                f"{counts['invalid_unknown']} invalid unknowns"
            )

    if failures:
        return ToolCheck(
            name=check_name,
            required=True,
            found=True,
            status="fail",
            message=f"{len(toml_records)} SoT records — " + "; ".join(failures),
        )

    return ToolCheck(
        name=check_name,
        required=False,
        found=True,
        status="pass",
        message=f"{len(toml_records)} SoT records registered; identity and membership complete",
    )


def _check_sot_duplicate_guard(target: Path) -> ToolCheck:
    """Run the duplicate-SoT drift-prevention guard from the verified audit engine."""
    check_name = "SoT duplicate guard"

    try:
        from groundtruth_kb.project.sot_audit import run_duplicate_sot_audit
    except Exception as exc:  # pragma: no cover  # intentional-catch: defensive import boundary
        return ToolCheck(
            name=check_name,
            required=True,
            found=False,
            status="fail",
            message=f"duplicate-SoT audit engine unavailable: {exc}",
        )

    try:
        report = run_duplicate_sot_audit(target)
    except Exception as exc:  # intentional-catch: baseline unavailable or structurally invalid
        return ToolCheck(
            name=check_name,
            required=True,
            found=False,
            status="fail",
            message=f"duplicate-SoT audit baseline unavailable: {exc}",
        )

    if not report.coverage_complete:
        return ToolCheck(
            name=check_name,
            required=True,
            found=True,
            status="fail",
            message=(
                "duplicate-SoT audit baseline incomplete: "
                f"registry_count={report.registry_count}, "
                f"persistent_file_count={report.persistent_file_count}, "
                f"registered_file_count={report.registered_file_count}"
            ),
        )

    violations = [candidate for candidate in report.candidates if candidate.classification == "duplicate_sot_violation"]
    if violations:
        first = "; ".join(
            f"{candidate.candidate_id} paths={','.join(candidate.paths)} "
            f"fields={','.join(candidate.duplicated_fields) or 'n/a'}"
            for candidate in violations[:3]
        )
        suffix = "" if len(violations) <= 3 else f"; +{len(violations) - 3} more"
        return ToolCheck(
            name=check_name,
            required=True,
            found=True,
            status="fail",
            message=f"{len(violations)} persistent duplicate-SoT violation(s): {first}{suffix}",
        )

    return ToolCheck(
        name=check_name,
        required=True,
        found=True,
        status="pass",
        message=f"coverage complete; {len(report.candidates)} candidate(s); no duplicate-SoT violations",
    )


def _check_settings_hook_registration_drift(
    target: Path, profile_name: str, registration: SettingsHookRegistration
) -> ToolCheck:
    """Check drift for a single settings-hook-registration record.

    Generalization of the scanner-safe-writer composite check pattern to any
    ``SettingsHookRegistration`` returned from
    ``artifacts_for_doctor(profile, class_="settings-hook-registration")``.
    Reports:

    - ``pass`` (``required=False``): non-bridge profile.
    - ``fail``: paired hook file (``hook.<short>`` FileArtifact) missing.
    - ``warning``: hook file present but
      ``.claude/settings.json`` registration for ``registration.event`` is
      missing.
    - ``pass``: hook file present and registered under the expected event.
    """
    check_name = f"settings:{registration.id}"
    profile = get_profile(profile_name)
    if not profile.includes_bridge:
        return ToolCheck(
            name=check_name,
            required=False,
            found=True,
            status="pass",
            message="not applicable to base profile",
        )

    paired_id = _derive_paired_hook_id(registration.id, registration.event.lower())
    hook_record = find_artifact_by_id(paired_id)
    assert isinstance(hook_record, FileArtifact)

    hook_file = target / hook_record.target_path
    if not hook_file.exists():
        return ToolCheck(
            name=check_name,
            required=True,
            found=False,
            status="fail",
            message=f"{hook_record.target_path.split('/')[-1]} missing — run `gt project upgrade --apply`",
        )

    if _is_command_registered_in_event(
        target / registration.target_settings_path,
        registration.event,
        registration.hook_filename,
    ):
        return ToolCheck(
            name=check_name,
            required=True,
            found=True,
            status="pass",
            message=f"{registration.hook_filename} registered in {registration.event}",
        )

    return ToolCheck(
        name=check_name,
        required=True,
        found=True,
        status="warning",
        message=(
            f"{registration.hook_filename} present but {registration.event} "
            f"registration missing in settings.json. Run `gt project upgrade --apply`."
        ),
    )


def _check_bridge_propose_skill_present(target: Path, profile_name: str) -> ToolCheck:
    """Check that the ``bridge-propose`` skill files are present.

    Bridge-profile-only check. Warning-level (not fail) because a
    missing skill degrades workflow quality but does not render the
    project non-functional. Remediation: ``gt project upgrade
    --apply`` (the missing-file repair path is unconditional — works
    at any scaffold version).
    """
    profile = get_profile(profile_name)
    if not profile.includes_bridge:
        return ToolCheck(
            name="skill:bridge-propose",
            required=False,
            found=True,
            status="pass",
            message="not applicable to base profile",
        )

    skill_md = target / ".claude" / "skills" / "gtkb-bridge-propose" / "SKILL.md"

    missing: list[str] = []
    if not skill_md.exists():
        missing.append("SKILL.md")

    if missing:
        return ToolCheck(
            name="skill:bridge-propose",
            required=False,
            found=False,
            status="warning",
            message=(
                f".claude/skills/gtkb-bridge-propose/ missing: {', '.join(missing)}. "
                f"Run `gt project upgrade --apply` to restore."
            ),
        )

    return ToolCheck(
        name="skill:bridge-propose",
        required=False,
        found=True,
        status="pass",
        message="bridge-propose skill present",
    )


def _check_spec_intake_skill_present(target: Path, profile_name: str) -> ToolCheck:
    """Check that the ``spec-intake`` skill files are present.

    Bridge-profile-only check. Warning-level (not fail) because a
    missing skill degrades workflow quality but does not render the
    project non-functional. Remediation: ``gt project upgrade
    --apply`` (the missing-file repair path is unconditional — works
    at any scaffold version). Parallel in shape to
    :func:`_check_bridge_propose_skill_present`.
    """
    profile = get_profile(profile_name)
    if not profile.includes_bridge:
        return ToolCheck(
            name="skill:spec-intake",
            required=False,
            found=True,
            status="pass",
            message="not applicable to base profile",
        )

    skill_md = target / ".claude" / "skills" / "gtkb-spec-intake" / "SKILL.md"
    helper_py = target / ".claude" / "skills" / "gtkb-spec-intake" / "helpers" / "spec_intake.py"

    missing: list[str] = []
    if not skill_md.exists():
        missing.append("SKILL.md")
    if not helper_py.exists():
        missing.append("helpers/spec_intake.py")

    if missing:
        return ToolCheck(
            name="skill:spec-intake",
            required=False,
            found=False,
            status="warning",
            message=(
                f".claude/skills/gtkb-spec-intake/ missing: {', '.join(missing)}. "
                f"Run `gt project upgrade --apply` to restore."
            ),
        )

    return ToolCheck(
        name="skill:spec-intake",
        required=False,
        found=True,
        status="pass",
        message="spec-intake skill present",
    )


_SKILL_FRONTMATTER_KEY_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_-]*$")


def _skill_frontmatter_error(text: str, path: str) -> str | None:
    lines = text.splitlines()
    if not lines or lines[0].lstrip("\ufeff").strip() != "---":
        return f"{path}: missing opening YAML frontmatter delimiter"

    closing_index: int | None = None
    for index, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            closing_index = index
            break
    if closing_index is None:
        return f"{path}: missing closing YAML frontmatter delimiter"

    fields: dict[str, str] = {}
    for offset, line in enumerate(lines[1:closing_index], start=2):
        if line.startswith((" ", "\t")):
            continue
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if stripped.startswith("- "):
            continue
        if ":" not in stripped:
            return f"{path}:{offset}: malformed frontmatter line"
        key, value = stripped.split(":", 1)
        key = key.strip()
        if not _SKILL_FRONTMATTER_KEY_RE.match(key):
            return f"{path}:{offset}: invalid frontmatter key {key!r}"
        fields[key] = value.strip().strip("\"'")

    for required in ("name", "description"):
        if not fields.get(required):
            return f"{path}: missing non-empty {required!r} frontmatter field"
    return None


def _check_codex_skill_load_health(target: Path) -> ToolCheck:
    """Validate generated Codex skill adapters expose loadable frontmatter."""
    skills_root = target / ".codex" / "skills"
    if not skills_root.is_dir():
        return ToolCheck(
            name="Codex skill load health",
            required=False,
            found=False,
            status="warning",
            message=".codex/skills missing; Codex skill adapters are not configured",
        )

    failures: list[str] = []
    checked = 0
    for skill_file in sorted(skills_root.glob("*/SKILL.md")):
        checked += 1
        rel_path = skill_file.relative_to(target).as_posix()
        try:
            text = _require_utf8_text(skill_file)
        except OSError as exc:
            failures.append(f"{rel_path}: unreadable: {exc}")
            continue
        error = _skill_frontmatter_error(text, rel_path)
        if error is not None:
            failures.append(error)

    if failures:
        preview = "; ".join(failures[:3])
        suffix = f"; +{len(failures) - 3} more" if len(failures) > 3 else ""
        return ToolCheck(
            name="Codex skill load health",
            required=True,
            found=True,
            status="fail",
            message=f"Codex skill adapter load check failed for {len(failures)} of {checked}: {preview}{suffix}",
        )

    return ToolCheck(
        name="Codex skill load health",
        required=True,
        found=True,
        status="pass",
        message=f"Codex skill adapter load check passed ({checked} adapters)",
    )


def _load_canonical_terminology_config(target: Path, rules_dir: str = ".claude/rules") -> dict[str, object] | None:
    """Load the projected ``canonical-terminology.toml`` or return ``None`` if absent/malformed.

    ``None`` means the projection is missing or unreadable; the caller reports
    that as a required failure and points at ``gt project upgrade --apply``.
    """
    import tomllib

    toml_path = target / rules_dir / "canonical-terminology.toml"
    if not toml_path.exists():
        return None

    try:
        with open(toml_path, "rb") as f:
            data = tomllib.load(f)
    except (OSError, tomllib.TOMLDecodeError):
        return None

    return data


def _resolve_profile_config(
    config: dict[str, object],
    profile_name: str,
) -> dict[str, object] | None:
    """Resolve a profile's terminology config, handling ``extends`` inheritance.

    Returns the effective config dict (``missing_severity``, optionally
    ``memory_md_location`` and ``primer_path``). Returns ``None`` when the
    profile is not configured in the TOML.
    """
    profiles = config.get("config")
    if not isinstance(profiles, dict):
        return None
    profiles_map = profiles.get("profiles")
    if not isinstance(profiles_map, dict):
        return None
    profile_cfg = profiles_map.get(profile_name)
    if not isinstance(profile_cfg, dict):
        return None

    # Handle ``extends = "other-profile"``
    extends = profile_cfg.get("extends")
    base: dict[str, object] = {}
    if isinstance(extends, str):
        parent = _resolve_profile_config(config, extends)
        if parent is not None:
            base = dict(parent)

    # Merge: profile overrides inherit.
    effective = dict(base)
    for key, value in profile_cfg.items():
        if key == "extends":
            continue
        effective[key] = value
    return effective


RETRIEVAL_ROUTE_MARKERS: tuple[str, ...] = ("gt terms", "gt authority resolve")
RETIRED_TERMINOLOGY_CONTRACT_KEYS: tuple[str, ...] = (
    "required_files",
    "required_startup_terms",
    "required_primer_terms",
)


PROJECTED_RULES_DIRS: tuple[str, ...] = (
    ".claude/rules",
    ".codex/rules",
    ".cursor/rules",
    ".goose/rules",
    ".agent/rules",
)


def _projected_terminology_rules_dir(target: Path) -> str | None:
    """The first projected rules directory carrying terminology guidance, if any harness is selected."""
    candidates = list(PROJECTED_RULES_DIRS) + sorted(
        p.relative_to(target).as_posix() for p in target.glob(".api-harness/*/rules") if p.is_dir()
    )
    for rules_dir in candidates:
        guidance = (target / rules_dir / "canonical-terminology.toml", target / rules_dir / "canonical-terminology.md")
        if any(path.exists() for path in guidance):
            return rules_dir
    return None


def _check_canonical_terminology(target: Path, profile_name: str, rules_dir: str = ".claude/rules") -> ToolCheck:
    """Check the projected terminology guidance (GOV-GLOSSARY-AS-DA-READ-SURFACE-001).

    Canonical definitions are current records read through the native CLI; the
    projected primer only teaches that retrieval route. The check fails when the
    projected configuration or primer is missing or malformed, when the
    selected profile is not configured, or when the primer does not name the
    retrieval commands; it warns when the configuration still carries the
    retired prompt-file term contract (required files, startup terms, primer
    terms), which an upgrade re-projects. No file is a term census.
    """
    name = "canonical terminology"
    config = _load_canonical_terminology_config(target, rules_dir)
    if config is None:
        return ToolCheck(
            name=name,
            required=True,
            found=False,
            status="fail",
            message=(
                f"{rules_dir}/canonical-terminology.toml missing or malformed — "
                "run `gt project upgrade --apply` to restore."
            ),
        )
    profile_cfg = _resolve_profile_config(config, profile_name)
    if profile_cfg is None:
        return ToolCheck(
            name=name,
            required=True,
            found=True,
            status="fail",
            message=f"profile {profile_name!r} not configured in canonical-terminology.toml",
        )
    stale = [key for key in RETIRED_TERMINOLOGY_CONTRACT_KEYS if key in profile_cfg]
    section = config.get("config")
    defaults = section.get("defaults", {}) if isinstance(section, dict) else {}
    configured = profile_cfg.get("primer_path") or defaults.get("primer_path")
    primer_rel = str(configured or f"{rules_dir}/canonical-terminology.md").replace("{{HARNESS_RULES_DIR}}", rules_dir)
    primer_text, unreadable = _read_text_for_check(target / primer_rel, primer_rel)
    if primer_text is None:
        return ToolCheck(
            name=name,
            required=True,
            found=False,
            status="fail",
            message=f"{primer_rel} missing or unreadable ({unreadable}) — run `gt project upgrade --apply` to restore.",
        )
    absent = [marker for marker in RETRIEVAL_ROUTE_MARKERS if marker not in primer_text]
    if absent:
        return ToolCheck(
            name=name,
            required=True,
            found=True,
            status="fail",
            message=f"{primer_rel} does not teach the native retrieval route: missing {', '.join(absent)}",
        )
    if stale:
        # Guidance present and correct, projection behind the baseline: drift, not absence.
        return ToolCheck(
            name=name,
            required=True,
            found=True,
            status="warning",
            message=(
                "canonical-terminology.toml still declares the retired prompt-file term contract "
                f"({', '.join(stale)}); run `gt project upgrade --apply` to re-project it"
            ),
        )
    return ToolCheck(
        name=name,
        required=True,
        found=True,
        status="pass",
        message=(
            f"Projected terminology guidance present; {primer_rel} teaches `gt terms` / `gt authority resolve` "
            f"(profile: {profile_name}); definitions are current canonical records, not file content"
        ),
    )


def _check_canonical_terms_registry(target: Path) -> ToolCheck:
    """Phase 1 backing-registry check for the Canonical Terminology System.

    Per ``bridge/gtkb-canonical-terminology-system-context-model-001-005.md``
    (Codex GO at ``-006``) plus FAB-15: when the ``canonical_terms`` table
    exists in the project's MemBase, run deterministic generator-freshness
    check (markdown -> table dry-run) plus collision detection over current
    platform_core rows.

    Behavior:

    - Pass when the table is empty (Phase 1 backing registry hasn't been
      seeded yet — that's fine; the markdown remains the canonical source).
    - Pass when seeded, the generator dry-run is all-unchanged, and no
      collision findings exist.
    - Warning when the generator dry-run has pending insert/update/retire
      operations.
    - Fail only when collision detection reports a
      ``platform_core_redefinition``.

    The table-not-present case is also a pass: this check never blocks if
    the schema upgrade hasn't been applied yet. Run ``gt project upgrade
    --apply`` to install the table.
    """
    glossary = target / ".claude" / "rules" / "canonical-terminology.md"
    if not glossary.exists():
        return ToolCheck(
            name="canonical terms registry",
            required=False,
            found=False,
            status="pass",
            message="canonical-terminology.md not present; backing registry check skipped",
        )

    db_path = target / "groundtruth.db"
    if not db_path.exists():
        return ToolCheck(
            name="canonical terms registry",
            required=False,
            found=False,
            status="pass",
            message="groundtruth.db not present; backing registry check skipped",
        )

    try:
        import sqlite3 as _sqlite3

        from groundtruth_kb import canonical_terms as _ct
    except ImportError as exc:
        return ToolCheck(
            name="canonical terms registry",
            required=False,
            found=False,
            status="warning",
            message=f"canonical_terms module unavailable: {exc}",
        )

    conn = _sqlite3.connect(str(db_path))
    try:
        # Ensure the schema migration is applied; if not, treat as pass-skip.
        cur = conn.execute("SELECT name FROM sqlite_master WHERE type = 'table' AND name = 'canonical_terms'")
        if cur.fetchone() is None:
            return ToolCheck(
                name="canonical terms registry",
                required=False,
                found=False,
                status="pass",
                message=("canonical_terms table not yet provisioned — run gt project upgrade --apply"),
            )

        plan = _ct.seed_from_markdown(conn, glossary, dry_run=True)
        pending_ops = [op for op in plan.operations if op.op != "unchanged"]
        pending_summary: dict[str, int] = {}
        for op in pending_ops:
            pending_summary[op.op] = pending_summary.get(op.op, 0) + 1

        terms = _ct.list_terms(conn, include_retired=False)
        errors_collisions, warnings_collisions = _ct.find_collisions(terms)

        if errors_collisions:
            details = []
            for c in errors_collisions:
                details.append(f"collision:{c.classification}:{c.key[1]}")
            return ToolCheck(
                name="canonical terms registry",
                required=True,
                found=True,
                status="fail",
                message=(
                    "canonical_terms registry blocking findings: "
                    f"{len(errors_collisions)} platform_core redefinition(s) — "
                    f"{'; '.join(details[:10])}"
                ),
            )

        if pending_ops or warnings_collisions:
            details = []
            for op in pending_ops:
                details.append(f"freshness:{op.op}:{op.id}")
            for c in warnings_collisions:
                details.append(f"collision:{c.classification}:{c.key[1]}")
            summary_bits = ", ".join(f"{key}={value}" for key, value in sorted(pending_summary.items()))
            return ToolCheck(
                name="canonical terms registry",
                required=False,
                found=True,
                status="warning",
                message=(
                    "canonical_terms registry generator freshness findings: "
                    f"{len(pending_ops)} pending sync operation(s)"
                    f"{f' ({summary_bits})' if summary_bits else ''}, "
                    f"{len(warnings_collisions)} cross-field/cross-scope collision(s) — "
                    f"{'; '.join(details[:10])}"
                ),
            )

        return ToolCheck(
            name="canonical terms registry",
            required=True,
            found=True,
            status="pass",
            message=(f"canonical_terms registry OK — {len(terms)} active terms, generator fresh, no collisions"),
        )
    finally:
        conn.close()


# -- Bridge dispatch liveness ------------------------------------------
# Bridge dispatch liveness reads recipients[role].updated_at from the shared
# dispatch-state.json written by the dispatcher daemon.


# ── Auto-install ──────────────────────────────────────────────────────


def _auto_install_pip(package: str) -> bool:
    """Install a pip package. Returns True on success."""
    try:
        r = subprocess.run(
            [sys.executable, "-m", "pip", "install", package],
            capture_output=True,
            text=True,
            timeout=120,
        )
        return r.returncode == 0
    except (subprocess.TimeoutExpired, OSError):
        return False


def _auto_install_npm(package: str) -> bool:
    """Install an npm global package. Returns True on success."""
    npm = shutil.which("npm")
    if not npm:
        return False
    try:
        r = subprocess.run(
            [npm, "install", "-g", package],
            capture_output=True,
            text=True,
            timeout=120,
        )
        return r.returncode == 0
    except (subprocess.TimeoutExpired, OSError):
        return False


_AUTO_INSTALL_MAP = {
    "ruff": ("pip", "ruff"),
    "Claude Code": ("npm", "@anthropic-ai/claude-code"),
}


def _try_auto_install(check: ToolCheck) -> ToolCheck:
    """Attempt to auto-install a failed tool check."""
    if check.status == "pass" or not check.auto_installable:
        return check

    entry = _AUTO_INSTALL_MAP.get(check.name)
    if not entry:
        return check

    method, package = entry
    if method == "pip":
        ok = _auto_install_pip(package)
    elif method == "npm":
        ok = _auto_install_npm(package)
    else:
        return check

    if ok:
        return ToolCheck(
            name=check.name,
            required=check.required,
            found=True,
            status="pass",
            message=f"{check.name} installed successfully via {method}",
            auto_installable=True,
        )
    check.message += f" (auto-install via {method} failed)"
    return check


# ── DA harvest coverage ───────────────────────────────────────────────

# Coverage thresholds (hard-coded per implementation GO condition in
# bridge/gtkb-da-harvest-coverage-implementation-005.md).
DA_HARVEST_COVERAGE_WARN_THRESHOLD = 95.0
DA_HARVEST_COVERAGE_ERROR_THRESHOLD = 80.0


def _check_deliberation_search_backend(target: Path) -> ToolCheck:
    """Fail loudly when mandatory deliberation semantic search is degraded."""
    check_name = "Deliberation search backend"
    db_path = target / "groundtruth.db"
    if not db_path.is_file():
        return ToolCheck(
            name=check_name,
            required=True,
            found=False,
            status="fail",
            message="Deliberation search backend unavailable: groundtruth.db not found",
        )

    try:
        from groundtruth_kb.db import KnowledgeDB

        db = KnowledgeDB(db_path)
        try:
            status = db.deliberation_search_backend_status()
        finally:
            db.close()
    except Exception as exc:  # noqa: BLE001  # intentional-catch: doctor checks must report, not crash
        return ToolCheck(
            name=check_name,
            required=True,
            found=False,
            status="fail",
            message=f"Deliberation search backend probe failed: {exc}",
        )

    current_count = int(status.get("current_deliberation_count") or 0)
    indexed_count = int(status.get("indexed_deliberation_count") or 0)
    chunk_count = int(status.get("indexed_chunk_count") or 0)
    chroma_path = str(status.get("canonical_chroma_path") or "<unknown>")
    if status.get("healthy"):
        return ToolCheck(
            name=check_name,
            required=True,
            found=True,
            status="pass",
            message=(
                "Deliberation search backend healthy: ChromaDB importable; "
                f"indexed {indexed_count}/{current_count} current deliberations "
                f"({chunk_count} chunks) at {chroma_path}"
            ),
        )

    reason = str(status.get("degradation_reason") or "unknown_degradation")
    found = bool(status.get("chromadb_importable")) and bool(status.get("index_path_exists"))
    return ToolCheck(
        name=check_name,
        required=True,
        found=found,
        status="fail",
        message=(
            f"Deliberation search backend degraded ({reason}): "
            f"indexed {indexed_count}/{current_count} current deliberations "
            f"({chunk_count} chunks) at {chroma_path}; run `gt deliberations rebuild-index`"
        ),
    )


def _normalize_harness_argv_head(head: str, project_root: Path) -> str:
    """Resolve installation argv without launching a harness or using the caller's CWD."""
    if not head:
        return head
    normalized = os.path.normpath(head.replace("{{PROJECT_ROOT}}", str(project_root)))
    candidate = normalized
    if (os.sep in normalized or (os.altsep and os.altsep in normalized)) and not os.path.isabs(normalized):
        candidate = os.path.normpath(str(project_root / normalized))
    resolved = shutil.which(candidate)
    if resolved:
        return resolved
    return candidate


def _native_harness_installations(target: Path) -> list[dict[str, Any]]:
    """Read current installation metadata without a file or SQLite fallback."""
    from groundtruth_kb.authority_client import AuthorityClient, AuthorityClientError
    from groundtruth_kb.config import GTConfig

    harnesses: list[dict[str, Any]] = []
    config = GTConfig.load(config_path=target / "groundtruth.toml")
    if not config.authority_url:
        raise AuthorityClientError("authority_not_configured", "No authority_url is configured")
    client = AuthorityClient(config.authority_url)
    after = None
    while True:
        result = client.request("GET", "/v1/harnesses", query={"status": "active", "limit": 1000, "after": after})
        records = result.get("records") if isinstance(result, dict) else None
        next_after = result.get("next_after") if isinstance(result, dict) else None
        if not isinstance(records, list) or any(not isinstance(record, dict) for record in records):
            raise AuthorityClientError("invalid_response", "Harness installation records are malformed")
        if next_after is not None and (
            not isinstance(next_after, str) or not next_after or (after and next_after <= after)
        ):
            raise AuthorityClientError("invalid_response", "Harness installation pagination did not advance")
        harnesses.extend(records)
        if next_after is None:
            break
        after = next_after
    return harnesses


def _check_harness_launchability(target: Path) -> ToolCheck:
    """Inspect current installation argv via the native service; never infer session roles."""
    from groundtruth_kb.authority_client import AuthorityClientError
    from groundtruth_kb.config import GTConfigError

    check_name = "Harness installation launchability"
    try:
        harnesses = _native_harness_installations(target)
    except (AuthorityClientError, GTConfigError) as exc:
        return ToolCheck(
            name=check_name,
            required=False,
            found=False,
            status="warning",
            message=f"Current installation metadata unavailable; launchability is unverified: {exc}",
        )

    checked: list[tuple[str, str, str, bool]] = []
    for rec in harnesses:
        if not isinstance(rec, dict):
            continue
        status = rec.get("status")
        if not (isinstance(status, str) and status.strip().lower() == "active"):
            continue
        surfaces = rec.get("invocation_surfaces")
        headless = surfaces.get("headless") if isinstance(surfaces, dict) else None
        if headless is None:
            continue
        argv = headless.get("argv") if isinstance(headless, dict) else None
        name = str(rec.get("harness_name") or rec.get("id") or "?")
        if not isinstance(argv, list) or not argv or not all(isinstance(arg, str) and arg for arg in argv):
            checked.append((name, "<invalid argv>", "<invalid argv>", False))
            continue
        head = argv[0]
        if head == "{{PROMPT}}":
            checked.append((name, head, head, False))
            continue
        resolved = _normalize_harness_argv_head(head, target)
        launchable = bool(shutil.which(resolved))
        checked.append((name, head, resolved, launchable))

    if not checked:
        return ToolCheck(
            name=check_name,
            required=False,
            found=True,
            status="info",
            message="No active headless installation to check; dispatcher readiness is not asserted",
        )

    failures = [c for c in checked if not c[3]]
    if failures:
        detail = "; ".join(
            f"{name} argv head {head!r} unlaunchable (resolved {resolved!r})" for name, head, resolved, _ in failures
        )
        return ToolCheck(
            name=check_name,
            required=False,
            found=True,
            status="fail",
            message=(f"{len(failures)}/{len(checked)} active installation(s) have an unlaunchable argv head: {detail}"),
        )
    names = ", ".join(c[0] for c in checked)
    return ToolCheck(
        name=check_name,
        required=False,
        found=True,
        status="pass",
        message=f"Executables resolve for {len(checked)} active installation(s) ({names}); actual launch is unverified",
    )


# The boundary is declared by the projected rule; the neutral AGENTS.md is a pointer, not a boundary surface.
_HARNESS_SCRATCHPAD_BOUNDARY_DOCS = (Path(".claude") / "rules" / "project-root-boundary.md",)
_HARNESS_SCRATCHPAD_REQUIRED_TERMS = (
    "harness-local scratchpads",
    "non-authoritative",
    "per-harness planning/brain files",
    "automation memory",
    "harness auto-memory",
    "`memory.md` hierarchy",
    "formal gt-kb artifacts",
    "implementation reports",
    "verification verdicts",
    "tests",
    "doctor checks",
    "bridge evidence",
    "governed decisions",
    "release evidence",
    "dependency closure",
    "promoted into governed in-root artifacts",
)
_HARNESS_SCRATCHPAD_POSITIVE_AUTHORITY_RE = re.compile(
    r"\b(?:MEMORY\.md|auto-memory|scratchpads?|scratch/notepad|brain files?|"
    r"Antigravity planning|Codex automation memory|Claude Code auto-memory|"
    r"harness-local scratchpads?)\b.{0,120}\b(?:is|are|as|becomes?|counts as|"
    r"serves as|source for|evidence for)\b.{0,120}\b(?:authoritative|canonical|"
    r"source of truth|live dependency|formal artifact|implementation report|"
    r"verification verdict|test evidence|doctor check|bridge evidence|"
    r"governed decision|release evidence|dependency closure)\b",
    re.IGNORECASE,
)
_HARNESS_SCRATCHPAD_NEGATION_RE = re.compile(
    r"\b(?:non-authoritative|not authoritative|not canonical|cannot|must not|"
    r"do not|does not|is not|are not|forbids?|outside the scope)\b",
    re.IGNORECASE,
)
_CANONICAL_AUTHORITY_CONFIG_GLOBS = (
    "config/**/*.toml",
    "config/**/*.json",
    "config/**/*.yaml",
    "config/**/*.yml",
)
_CANONICAL_AUTHORITY_LABEL_RE = re.compile(
    r"\b(?:authoritative(?:[_ -]?source)?|authority|canonical(?:[_ -]?source)?|"
    r"source[_ -]?of[_ -]?truth)\b",
    re.IGNORECASE,
)
_CANONICAL_AUTHORITY_MEMORY_PATH_RE = re.compile(r"\bmemory[\\/][^\"'`\s,\]}]+", re.IGNORECASE)
_CANONICAL_AUTHORITY_NON_AUTHORITY_RE = re.compile(
    r"\b(?:non[_ -]?authoritative|not authoritative|not canonical|not the source of truth|"
    r"truth comes from|canonical .* lives in|governed in-root artifacts|"
    r"human-readable companion)\b",
    re.IGNORECASE,
)
_CANONICAL_AUTHORITY_SKILL_FRONTMATTER_KEY_RE = re.compile(
    r"^\s*(?:name|description|allowed-tools|allowed_tools|tools|type)\s*:",
    re.IGNORECASE,
)
_CANONICAL_AUTHORITY_FEEDBACK_TYPE_RE = re.compile(r"^\s*type\s*:\s*feedback\s*$", re.IGNORECASE | re.MULTILINE)
_CANONICAL_AUTHORITY_RULE_HEADING_RE = re.compile(
    r"^\s*#{1,3}\s+(?:rule|rules|instructions?|operating rule|how to apply)\b",
    re.IGNORECASE,
)
_CANONICAL_AUTHORITY_IMPERATIVE_RE = re.compile(
    r"\b(?:MUST|NEVER|ALWAYS|REQUIRED|FORBIDDEN|Do not|Never|Always|Before|When)\b"
)
_CANONICAL_AUTHORITY_SOURCE_LINE_RE = re.compile(
    r"^\s*(?:[-*]\s*)?(?:\*\*)?(?:Source|Sources|Authority)\s*:\s*(?:\*\*)?\s*(.*)$",
    re.IGNORECASE,
)
_CANONICAL_AUTHORITY_DELIB_RE = re.compile(r"\bDELIB-[A-Z0-9][A-Z0-9_-]*\b", re.IGNORECASE)
_CANONICAL_AUTHORITY_CARRIER_RE = re.compile(
    r"\b(?:ADR|DCL|GOV|SPEC)-[A-Z0-9][A-Z0-9_-]*\b|"
    r"\bMEMBASE-[A-Z0-9][A-Z0-9_.-]*\b|"
    r"\bgroundtruth\.db\b|\bbridge[\\/][^\s`'\"]+",
    re.IGNORECASE,
)


class DoctorCheckReadError(Exception):
    """Raised when a doctor check cannot read a file as strict UTF-8.

    ``_require_utf8_text`` converts helper findings into this exception so
    expression-shaped call sites can stay one line. ToolCheck-returning
    functions catch it and emit a named FAIL instead of aborting ``run_doctor``.
    """

    def __init__(self, finding: str) -> None:
        super().__init__(finding)
        self.finding = finding


def _read_text_for_check(path: Path, rel_text: str) -> tuple[str | None, str | None]:
    """Read ``path`` as strict UTF-8, turning any failure into a named finding.

    Returns ``(text, None)`` on success and ``(None, finding)`` on failure, so a
    caller appends the finding and continues instead of aborting the run.

    Strict decoding is deliberate (WI-6681). ``DELIB-202667656`` (WI-5688)
    rejected lossy ``errors="replace"`` decoding in doctor checks: silent
    character replacement masks unreadable input and can turn a broken health
    surface into a false ``PASS``. An undecodable file must therefore become an
    explicit, named failure -- never a silent skip, and never a pass.

    ``UnicodeDecodeError`` subclasses ``ValueError``, not ``OSError``. Call
    sites that guarded only ``OSError`` therefore let a decode error escape and
    abort the whole ``gt project doctor`` run; that is the WI-6681 defect.
    """

    try:
        return path.read_text(encoding="utf-8"), None
    except UnicodeDecodeError as exc:
        return None, (f"{rel_text} is not valid UTF-8 (byte 0x{exc.object[exc.start]:02x} at offset {exc.start})")
    except (OSError, ValueError) as exc:
        return None, f"{rel_text} unreadable: {exc}"


def _require_utf8_text(path: Path, rel_text: str | None = None) -> str:
    """Strict UTF-8 read for remaining doctor sites that used unguarded ``read_text``.

    Success returns the decoded text. Failure raises ``DoctorCheckReadError``
    carrying the helper's named finding so the check can FAIL instead of aborting.
    """

    rel = rel_text if rel_text is not None else path.as_posix()
    text, error = _read_text_for_check(path, rel)
    if error is not None:
        raise DoctorCheckReadError(error)
    if text is None:
        raise DoctorCheckReadError(f"{rel} unreadable")
    return text


def _toolcheck_from_utf8_error(fn_name: str, exc: DoctorCheckReadError) -> ToolCheck:
    """Convert a UTF-8 read finding into a named doctor FAIL."""

    return ToolCheck(
        name=fn_name.removeprefix("_check_").replace("_", " "),
        required=True,
        found=True,
        status="fail",
        message=exc.finding,
    )


_CheckParams = ParamSpec("_CheckParams")
_CheckResult = TypeVar("_CheckResult")


def _utf8_named_fail(
    fn: Callable[_CheckParams, _CheckResult],
) -> Callable[_CheckParams, _CheckResult | ToolCheck]:
    """Wrap a ToolCheck producer so undecodable files become FAIL, not abort."""

    def wrapped(*args: _CheckParams.args, **kwargs: _CheckParams.kwargs) -> _CheckResult | ToolCheck:
        try:
            return fn(*args, **kwargs)
        except DoctorCheckReadError as exc:
            return _toolcheck_from_utf8_error(fn.__name__, exc)

    wrapped.__name__ = fn.__name__
    wrapped.__doc__ = fn.__doc__
    return wrapped


def _check_harness_local_scratchpad_boundary(target: Path) -> ToolCheck:
    """Verify harness-local scratchpads cannot become GT-KB authority.

    Implements WI-4681 / ``DELIB-20260619-HARNESS-SCRATCHPAD-NON-AUTHORITY``.
    The check is deliberately narrow: it validates the projected boundary rule
    and fails if that surface regresses to granting positive
    authority to Antigravity planning/brain files, Codex automation memory,
    Claude Code auto-memory, or the ``MEMORY.md`` hierarchy.
    """
    check_name = "Harness-local scratchpad non-authority boundary"
    findings: list[str] = []

    for rel in _HARNESS_SCRATCHPAD_BOUNDARY_DOCS:
        path = target / rel
        rel_text = rel.as_posix()
        if not path.is_file():
            findings.append(f"{rel_text} missing")
            continue
        text, read_error = _read_text_for_check(path, rel_text)
        if read_error is not None:
            findings.append(read_error)
            continue
        if text is None:
            findings.append(f"{rel_text} unreadable")
            continue

        lowered = text.lower()
        missing_terms = [term for term in _HARNESS_SCRATCHPAD_REQUIRED_TERMS if term not in lowered]
        if missing_terms:
            findings.append(f"{rel_text} missing required term(s): {', '.join(missing_terms)}")

        for line_number, line in enumerate(text.splitlines(), start=1):
            if not _HARNESS_SCRATCHPAD_POSITIVE_AUTHORITY_RE.search(line):
                continue
            if _HARNESS_SCRATCHPAD_NEGATION_RE.search(line):
                continue
            excerpt = line.strip()
            if len(excerpt) > 160:
                excerpt = excerpt[:157] + "..."
            findings.append(f"{rel_text}:{line_number} grants scratchpad authority: {excerpt}")

    if findings:
        head = findings[0]
        extra = f" (+{len(findings) - 1} more)" if len(findings) > 1 else ""
        return ToolCheck(
            name=check_name,
            required=False,
            found=True,
            status="fail",
            message=f"{len(findings)} boundary finding(s); first: {head}{extra}",
        )

    docs = ", ".join(path.as_posix() for path in _HARNESS_SCRATCHPAD_BOUNDARY_DOCS)
    return ToolCheck(
        name=check_name,
        required=False,
        found=True,
        status="pass",
        message=f"scratchpad non-authority boundary declared and non-regressed in {docs}",
    )


def _check_canonical_authority_drift(target: Path) -> ToolCheck:
    """Flag recurrence of memory/DELIB-only canonical-authority drift patterns."""
    check_name = "Canonical authority drift guard"
    findings: list[str] = []

    findings.extend(_canonical_authority_config_findings(target))
    findings.extend(_canonical_authority_memory_findings(target))
    findings.extend(_canonical_authority_rule_source_findings(target))

    if findings:
        head = findings[0]
        extra = f" (+{len(findings) - 1} more)" if len(findings) > 1 else ""
        return ToolCheck(
            name=check_name,
            required=True,
            found=True,
            status="fail",
            message=f"{len(findings)} canonical-authority drift finding(s); first: {head}{extra}",
        )

    return ToolCheck(
        name=check_name,
        required=True,
        found=True,
        status="pass",
        message=(
            "No active config memory-authority labels, memory rule-shaped files, or DELIB-sole rule sources found"
        ),
    )


def _canonical_authority_config_findings(target: Path) -> list[str]:
    findings: list[str] = []
    paths: set[Path] = set()
    for pattern in _CANONICAL_AUTHORITY_CONFIG_GLOBS:
        paths.update(path for path in target.glob(pattern) if path.is_file())

    for path in sorted(paths, key=lambda item: item.as_posix()):
        try:
            lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
        except OSError as exc:
            findings.append(f"{_rel_to_target(path, target)} unreadable: {exc}")
            continue
        for index, line in enumerate(lines):
            if not _CANONICAL_AUTHORITY_MEMORY_PATH_RE.search(line):
                continue
            if not _CANONICAL_AUTHORITY_LABEL_RE.search(line):
                continue
            context = "\n".join(lines[max(0, index - 2) : min(len(lines), index + 5)])
            if _CANONICAL_AUTHORITY_NON_AUTHORITY_RE.search(context):
                continue
            findings.append(f"{_rel_to_target(path, target)}:{index + 1} labels memory path as authority")
    return findings


def _canonical_authority_memory_findings(target: Path) -> list[str]:
    memory_dir = target / "memory"
    if not memory_dir.is_dir():
        return []

    findings: list[str] = []
    for path in sorted(memory_dir.glob("*.md"), key=lambda item: item.as_posix()):
        if path.name in {"MEMORY.md", "CLAUDE_ARCHIVE.md", "pending-owner-decisions.md"}:
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError as exc:
            findings.append(f"{_rel_to_target(path, target)} unreadable: {exc}")
            continue
        if _memory_markdown_declares_non_authority(text):
            continue
        if _memory_markdown_has_skill_frontmatter(text):
            findings.append(f"{_rel_to_target(path, target)} has skill-style frontmatter")
            continue
        if _memory_markdown_is_rule_shaped(text):
            findings.append(f"{_rel_to_target(path, target)} has imperative rule-shaped content")
    return findings


def _memory_markdown_declares_non_authority(text: str) -> bool:
    head = "\n".join(text.splitlines()[:40])
    return bool(
        _CANONICAL_AUTHORITY_NON_AUTHORITY_RE.search(head) or _CANONICAL_AUTHORITY_FEEDBACK_TYPE_RE.search(head)
    )


def _memory_markdown_has_skill_frontmatter(text: str) -> bool:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return False
    keys: set[str] = set()
    for line in lines[1:25]:
        if line.strip() == "---":
            break
        if not _CANONICAL_AUTHORITY_SKILL_FRONTMATTER_KEY_RE.match(line):
            continue
        key = line.split(":", 1)[0].strip().lower().replace("_", "-")
        keys.add(key)
    return "name" in keys and "description" in keys


def _memory_markdown_is_rule_shaped(text: str) -> bool:
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if not _CANONICAL_AUTHORITY_RULE_HEADING_RE.match(line):
            continue
        context = "\n".join(lines[index + 1 : min(len(lines), index + 8)])
        if _CANONICAL_AUTHORITY_IMPERATIVE_RE.search(context):
            return True
    return False


def _canonical_authority_rule_source_findings(target: Path) -> list[str]:
    rules_dir = target / ".claude" / "rules"
    if not rules_dir.is_dir():
        return []

    findings: list[str] = []
    for path in sorted(rules_dir.glob("*.md"), key=lambda item: item.as_posix()):
        try:
            lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
        except OSError as exc:
            findings.append(f"{_rel_to_target(path, target)} unreadable: {exc}")
            continue
        for line_number, block in _iter_rule_source_blocks(lines):
            if not _CANONICAL_AUTHORITY_DELIB_RE.search(block):
                continue
            if _CANONICAL_AUTHORITY_CARRIER_RE.search(block):
                continue
            if _source_block_is_delib_only(block):
                findings.append(f"{_rel_to_target(path, target)}:{line_number} cites DELIB as sole rule authority")
    return findings


def _iter_rule_source_blocks(lines: list[str]) -> list[tuple[int, str]]:
    blocks: list[tuple[int, str]] = []
    for index, line in enumerate(lines):
        match = _CANONICAL_AUTHORITY_SOURCE_LINE_RE.match(line)
        if not match:
            continue
        collected = [match.group(1)]
        for continuation in lines[index + 1 : min(len(lines), index + 5)]:
            stripped = continuation.strip()
            if not stripped:
                break
            if stripped.startswith("#"):
                break
            if _CANONICAL_AUTHORITY_SOURCE_LINE_RE.match(continuation):
                break
            collected.append(stripped)
        blocks.append((index + 1, " ".join(collected)))
    return blocks


def _source_block_is_delib_only(block: str) -> bool:
    without_delibs = _CANONICAL_AUTHORITY_DELIB_RE.sub("", block)
    remaining = re.sub(r"[`'\";:,().\s\-/]+", "", without_delibs)
    return not remaining


def _rel_to_target(path: Path, target: Path) -> str:
    try:
        return path.relative_to(target).as_posix()
    except ValueError:
        return path.as_posix()


def _check_session_wrap_had_orient(target: Path) -> ToolCheck:
    """Validate that the prior session ended with a well-formed ORIENT block.

    gtkb-session-start-orientation-gate: mechanical enforcement that session-start
    orientation discipline was not skipped under context pressure. WARN when
    transcript access is unavailable; INFO on first-ever sessions; FAIL when a
    prior transcript exists but lacks ORIENT evidence.
    """
    from groundtruth_kb.project.session_start_orientation import check_session_wrap_had_orient

    check_name = "Prior-session ORIENT block"
    status, message = check_session_wrap_had_orient(target)
    return ToolCheck(
        name=check_name,
        required=False,
        found=status in {"pass", "warning", "fail"},
        status=status,
        message=message,
    )


_ROLE_AUTHORITY_FORBIDDEN_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"\bdurable\s+map\s+wins\b", re.IGNORECASE),
    re.compile(
        r"\bdurable\s+(?:operating-?role|role)\s+record\s+assigns\s+(?:prime\s+builder|loyal\s+opposition)",
        re.IGNORECASE,
    ),
    re.compile(
        r"\bresolved\s+durable\s+role\s+record\s+assigns\s+(?:prime\s+builder|loyal\s+opposition)",
        re.IGNORECASE,
    ),
    re.compile(
        r"\bcanonical\s+role\s+registry\b.*\bsingle\s+source-of-truth\s+operating-role\s+record\b",
        re.IGNORECASE,
    ),
    re.compile(
        r"\bdurable\s+role\b.*\b(?:permissions|restrictions|hook behavior|file authority)\b",
        re.IGNORECASE,
    ),
    re.compile(
        r"\bdispatcher/default\s+role\b.*\b(?:permissions|restrictions|hook behavior|file authority)\b",
        re.IGNORECASE,
    ),
    re.compile(r"\brole\s+authority:\s+resolve\b.*\bharness-state/harness-registry\.json\b", re.IGNORECASE),
)


def _check_da_harvest_coverage(target: Path) -> ToolCheck:
    """Check DA bridge-thread coverage for active VERIFIED threads.

    Uses the shared helper at ``groundtruth_kb.reporting.harvest_coverage``.
    Status mapping:

    - coverage_pct ``>=`` ``WARN_THRESHOLD`` (95.0)  → pass
    - coverage_pct ``>=`` ``ERROR_THRESHOLD`` (80.0) → warning
    - coverage_pct ``<``  ``ERROR_THRESHOLD``        → fail

    Missing DB or missing bridge directory is treated as a skipped warning
    rather than a hard fail — this keeps fresh scaffolds green until the
    consumer project wires its bridge.
    """
    bridge_dir = target / "bridge"
    db_path = target / "groundtruth.db"

    if not bridge_dir.exists() or not db_path.exists():
        return ToolCheck(
            name="DA harvest coverage",
            required=False,
            found=False,
            status="warning",
            message="DA harvest coverage: skipped (bridge directory or groundtruth.db missing)",
        )

    db = None
    try:
        from groundtruth_kb.db import KnowledgeDB
        from groundtruth_kb.reporting.harvest_coverage import (
            compute_active_bridge_thread_coverage,
        )

        db = KnowledgeDB(str(db_path))
        metrics = compute_active_bridge_thread_coverage(bridge_dir, db)
    except Exception as exc:  # intentional-catch: validation tool, error -> fail status
        return ToolCheck(
            name="DA harvest coverage",
            required=False,
            found=True,
            status="fail",
            message=f"DA harvest coverage: error computing metrics: {exc}",
        )
    finally:
        if db is not None:
            db.close()

    pct = float(metrics["coverage_pct"])  # type: ignore[arg-type]
    num = metrics["numerator_threads"]
    denom = metrics["denominator_threads"]
    uncovered_list = metrics["uncovered_thread_names"]
    assert isinstance(uncovered_list, list)  # noqa: S101 - internal invariant
    uncovered_preview = ", ".join(uncovered_list[:3])
    if len(uncovered_list) > 3:
        uncovered_preview += f", … (+{len(uncovered_list) - 3} more)"

    if pct >= DA_HARVEST_COVERAGE_WARN_THRESHOLD:
        return ToolCheck(
            name="DA harvest coverage",
            required=False,
            found=True,
            status="pass",
            message=f"DA harvest coverage: {pct:.2f}% ({num}/{denom} active VERIFIED threads covered)",
        )

    if pct >= DA_HARVEST_COVERAGE_ERROR_THRESHOLD:
        return ToolCheck(
            name="DA harvest coverage",
            required=False,
            found=True,
            status="warning",
            message=(
                f"DA harvest coverage: {pct:.2f}% ({num}/{denom}) below WARN threshold "
                f"{DA_HARVEST_COVERAGE_WARN_THRESHOLD}% — uncovered: {uncovered_preview}"
            ),
        )

    return ToolCheck(
        name="DA harvest coverage",
        required=False,
        found=True,
        status="fail",
        message=(
            f"DA harvest coverage: {pct:.2f}% ({num}/{denom}) below ERROR threshold "
            f"{DA_HARVEST_COVERAGE_ERROR_THRESHOLD}% — uncovered: {uncovered_preview}"
        ),
    )


# ── Main entry point ──────────────────────────────────────────────────


def _read_bridge_file_status(path: Path) -> str | None:
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        match = _BRIDGE_FILE_STATUS_RE.match(stripped)
        return match.group(1).upper() if match else None
    return None


def _status_from_bridge_file(path: Path) -> str | None:
    try:
        return _read_bridge_file_status(path)
    except OSError:
        return None


def _latest_bridge_status_entries(target: Path) -> list[dict[str, str]]:
    """Return the latest status row for each numbered bridge thread."""

    bridge_dir = target / "bridge"
    grouped: dict[str, list[tuple[int, str, str]]] = {}
    for path in bridge_dir.glob("*.md"):
        match = _BRIDGE_VERSION_FILE_RE.match(path.name)
        if match is None:
            continue
        status = _read_bridge_file_status(path)
        if status is None:
            continue
        grouped.setdefault(match.group(1), []).append((int(match.group(2)), status, f"bridge/{path.name}"))

    entries: list[dict[str, str]] = []
    for document, versions in sorted(grouped.items()):
        latest_version, status, rel_path = max(versions, key=lambda item: item[0])
        entries.append(
            {
                "document": document,
                "status": status,
                "path": rel_path,
                "version": str(latest_version),
            }
        )
    return entries


def _bridge_file_date(path: Path) -> datetime | None:
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines()[:80]:
        match = _BRIDGE_DATE_RE.match(line.strip())
        if match:
            try:
                return datetime.fromisoformat(match.group(1)).replace(tzinfo=UTC)
            except ValueError:
                continue
    return None


def _active_authorized_work_item_ids(db: Any) -> set[str]:
    """Work items whose project is authorized.

    WI-7657: previously read an authorization row's included_work_item_ids
    list. Authorization is now a field on the project row, and work-item scope
    is project membership, so the same set comes from joining active
    memberships to projects whose authorization is 'authorized'.
    """
    rows = db._get_conn().execute(
        """SELECT DISTINCT m.work_item_id
           FROM current_project_work_item_memberships m
           JOIN current_projects p ON p.id = m.project_id
           WHERE m.status = 'active' AND p.authorization = 'authorized'"""
    )
    return {str(row[0]) for row in rows if str(row[0]).strip()}


def _is_implementation_active_work_item(item: dict[str, Any]) -> bool:
    resolution_status = str(item.get("resolution_status") or "").strip()
    stage = str(item.get("stage") or "").strip()
    return resolution_status in IMPLEMENTATION_ACTIVE_RESOLUTION_STATUSES or stage in IMPLEMENTATION_ACTIVE_STAGES


def check_standing_backlog_health(
    target: Path,
    *,
    stale_no_go_days: int = STANDING_BACKLOG_STALE_NO_GO_DAYS,
    now: datetime | None = None,
) -> dict[str, Any]:
    """Return a machine-readable standing-backlog health payload.

    Findings use the severity taxonomy required by GTKB-GOV-010, calibrated by
    GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001:
    implementation-active orphaned-WI=WARN, stale-NO-GO=WARN,
    missing-verdict-date=WARN, missing-evidence=FAIL. Unapproved/future WIs do
    not require PAUTH coverage.
    """

    from groundtruth_kb.db import KnowledgeDB

    target = target.resolve()
    now = now or datetime.now(UTC)
    findings: list[dict[str, Any]] = []
    non_implementation_uncovered_count = 0

    db_path = target / "groundtruth.db"
    if not db_path.is_file():
        findings.append(
            {
                "kind": "missing-evidence",
                "severity": "FAIL",
                "message": "groundtruth.db is missing; cannot evaluate open work-item authorization coverage.",
                "path": "groundtruth.db",
            }
        )
    else:
        db = KnowledgeDB(db_path)
        try:
            authorized_work_item_ids = _active_authorized_work_item_ids(db)
            for item in db.get_open_work_items():
                item_id = str(item.get("id") or "")
                if not item_id or item_id in authorized_work_item_ids:
                    continue
                if not _is_implementation_active_work_item(item):
                    non_implementation_uncovered_count += 1
                    continue
                findings.append(
                    {
                        "kind": "orphaned-WI",
                        "severity": "WARN",
                        "work_item_id": item_id,
                        "project_name": item.get("project_name"),
                        "resolution_status": item.get("resolution_status"),
                        "message": (
                            f"Implementation-active work item {item_id} is not listed in any active "
                            "project authorization's included_work_item_ids."
                        ),
                    }
                )
        except Exception as exc:  # intentional-catch: doctor payload, error -> FAIL finding
            findings.append(
                {
                    "kind": "missing-evidence",
                    "severity": "FAIL",
                    "message": f"Could not evaluate work-item authorization coverage: {exc}",
                    "path": "groundtruth.db",
                }
            )
        finally:
            db.close()

    bridge_dir = target / "bridge"
    if not bridge_dir.is_dir():
        findings.append(
            {
                "kind": "missing-evidence",
                "severity": "FAIL",
                "message": "bridge directory is missing; cannot evaluate stale NO-GO bridge entries.",
                "path": "bridge/",
            }
        )
    else:
        try:
            entries = _latest_bridge_status_entries(target)
            for entry in entries:
                if entry["status"] != "NO-GO":
                    continue
                bridge_file = target / entry["path"]
                decided_at = _bridge_file_date(bridge_file)
                if decided_at is None:
                    findings.append(
                        {
                            "kind": "missing-verdict-date",
                            "severity": "WARN",
                            "document": entry["document"],
                            "path": entry["path"],
                            "message": (
                                f"Latest NO-GO file {entry['path']} has no parseable explicit Date line; "
                                "add governed verdict metadata before including it in stale-age calculation."
                            ),
                        }
                    )
                    continue
                age_days = (now - decided_at).days
                if age_days > stale_no_go_days:
                    findings.append(
                        {
                            "kind": "stale-NO-GO",
                            "severity": "WARN",
                            "document": entry["document"],
                            "path": entry["path"],
                            "age_days": age_days,
                            "threshold_days": stale_no_go_days,
                            "message": (
                                f"Bridge document {entry['document']} is latest NO-GO for "
                                f"{age_days} days, exceeding threshold {stale_no_go_days}."
                            ),
                        }
                    )
        except Exception as exc:  # intentional-catch: doctor payload, error -> FAIL finding
            findings.append(
                {
                    "kind": "missing-evidence",
                    "severity": "FAIL",
                    "message": f"Could not evaluate bridge stale NO-GO state: {exc}",
                    "path": "bridge/",
                }
            )

    fail_count = sum(1 for finding in findings if finding["severity"] == "FAIL")
    warn_count = sum(1 for finding in findings if finding["severity"] == "WARN")
    status = "fail" if fail_count else "warning" if warn_count else "pass"
    return {
        "schema_version": 1,
        "check": "standing_backlog_health",
        "status": status,
        "threshold_days": stale_no_go_days,
        "summary": {
            "finding_count": len(findings),
            "fail_count": fail_count,
            "warn_count": warn_count,
            "orphaned_wi_count": sum(1 for finding in findings if finding["kind"] == "orphaned-WI"),
            "non_implementation_uncovered_count": non_implementation_uncovered_count,
            "stale_no_go_count": sum(1 for finding in findings if finding["kind"] == "stale-NO-GO"),
            "missing_verdict_date_count": sum(1 for finding in findings if finding["kind"] == "missing-verdict-date"),
            "missing_evidence_count": sum(1 for finding in findings if finding["kind"] == "missing-evidence"),
        },
        "findings": findings,
    }


def _check_standing_backlog_health(target: Path) -> ToolCheck:
    payload = check_standing_backlog_health(target)
    summary = payload["summary"]
    if payload["status"] == "pass":
        message = "Standing backlog health: no findings"
    else:
        message = (
            "Standing backlog health: "
            f"{summary['fail_count']} fail, {summary['warn_count']} warn "
            f"({summary['finding_count']} findings)"
        )
    return ToolCheck(
        name="Standing backlog health",
        required=True,
        found=True,
        status="fail" if payload["status"] == "fail" else "warning" if payload["status"] == "warning" else "pass",
        message=message,
    )


def _check_obsolete_reference_purge(target: Path) -> ToolCheck:
    """Warn when an in-window retirement-class artifact lacks a paired purge WI.

    Phase 1 (WARN) operationalization of DCL-OBSOLETE-REFERENCE-PURGE-PAIRING-001
    (WI-4795). Returns ``warning`` -- never ``fail`` -- per the GO conditions on
    bridge thread ``gtkb-obsolete-reference-purge-deterministic-check`` (-002);
    fail-soft to ``warning`` when the check is unavailable.
    """
    check_name = "Obsolete-reference purge pairing"
    scripts_dir = target / "scripts"
    inserted = False
    if scripts_dir.is_dir() and str(scripts_dir) not in sys.path:
        sys.path.insert(0, str(scripts_dir))
        inserted = True
    try:
        try:
            from check_obsolete_reference_purge import (  # type: ignore
                unpaired_retirement_class_artifacts,
            )
        except Exception as exc:  # pragma: no cover  # intentional-catch: defensive doctor surface
            return ToolCheck(
                name=check_name,
                required=False,
                found=False,
                status="warning",
                message=f"Obsolete-reference purge pairing: check unavailable: {exc}",
            )
        try:
            unpaired = unpaired_retirement_class_artifacts(target)
        except Exception as exc:  # noqa: BLE001 - diagnostic doctor check  # intentional-catch: autogenerated check fix
            return ToolCheck(
                name=check_name,
                required=False,
                found=False,
                status="warning",
                message=f"Obsolete-reference purge pairing: inspection failed: {exc}",
            )
    finally:
        if inserted:
            with suppress(ValueError):
                sys.path.remove(str(scripts_dir))

    if not unpaired:
        return ToolCheck(
            name=check_name,
            required=False,
            found=True,
            status="pass",
            message="Obsolete-reference purge pairing: no unpaired retirements in window",
        )
    examples = ", ".join(str(finding.get("artifact_id")) for finding in unpaired[:5])
    suffix = "" if len(unpaired) <= 5 else f", +{len(unpaired) - 5} more"
    return ToolCheck(
        name=check_name,
        required=False,
        found=True,
        status="warning",
        message=(
            f"Obsolete-reference purge pairing: {len(unpaired)} unpaired "
            f"retirement-class artifact(s) ({examples}{suffix})"
        ),
    )


def _check_registered_application_roots(target: Path) -> ToolCheck:
    """Report catalog, marker and artifact checks for every application slot."""
    from groundtruth_kb.isolation.doctor_verdicts import evaluate_isolation_state

    name = "Registered application boundaries"
    result = evaluate_isolation_state(target)
    failures = result["verdicts"]
    if failures:
        return ToolCheck(
            name=name,
            required=True,
            found=True,
            status="fail",
            message="Application registry checks failed: " + "; ".join(row["details"] for row in failures[:3]),
        )
    count = len(result["slots_status"])
    return ToolCheck(
        name=name,
        required=bool(count),
        found=bool(count),
        status="pass",
        message=f"Registry checks passed for {count} applications; native lifecycle qualification is separate"
        if count
        else "No application slots configured; no application qualification performed",
    )


def _guard_doctor_utf8_checks() -> None:
    """Wrap ToolCheck producers so remaining UTF-8 findings cannot abort doctor."""

    for name, obj in list(globals().items()):
        if not name.startswith("_check_") or not callable(obj):
            continue
        globals()[name] = _utf8_named_fail(obj)


_guard_doctor_utf8_checks()


def run_doctor(
    target: Path,
    profile: str,
    *,
    auto_install: bool = False,
) -> DoctorReport:
    """Run all readiness checks for the given profile."""
    p = get_profile(profile)
    checks: list[ToolCheck] = []

    # System tools
    checks.append(_check_python())
    checks.append(_check_git())
    checks.append(_check_ruff(target))
    checks.append(_check_gh_cli())

    if p.includes_bridge:
        checks.append(_check_claude_code())
        checks.append(_check_codex())

    if p.includes_docker:
        checks.append(_check_docker())
        checks.append(_check_node())

    if p.includes_cloud:
        checks.append(_check_azure_cli())
        checks.append(_check_terraform())

    # Project-level checks
    checks.append(_check_groundtruth_toml(target))
    checks.append(_check_db_schema(target))
    checks.append(_check_application_scope_alignment(target))
    checks.append(_check_core_spec_intake(target))
    checks.append(_check_hooks(target, profile))
    checks.append(_check_rules(target, profile))
    checks.append(_check_canonical_terminology(target, profile))
    checks.append(_check_canonical_terms_registry(target))

    # Dynamic checks via registry (ADR-REGISTRY-DISCOVERY-001)
    from groundtruth_kb.project.checks import get_registered_checks

    for check_func in get_registered_checks().values():
        checks.append(check_func(target))

    if p.includes_bridge:
        checks.append(_check_active_legacy_root_references(target))
        checks.append(_check_registered_hooks_tracked(target))
        checks.append(_check_skill_rename_reference_sweep(target))
        checks.append(_check_scanner_safe_writer_drift(target, profile))
        checks.append(_check_safety_gate_registration(target))
        checks.append(_check_bridge_propose_skill_present(target, profile))
        checks.append(_check_spec_intake_skill_present(target, profile))
        checks.append(_check_codex_skill_load_health(target))
        checks.append(_check_managed_artifact_drift(target, profile))
        checks.append(_check_sot_registry_completeness(target))
        checks.append(_check_sot_duplicate_guard(target))
        for registration in artifacts_for_doctor(profile, class_="settings-hook-registration"):
            if isinstance(registration, SettingsHookRegistration):
                checks.append(_check_settings_hook_registration_drift(target, profile, registration))
        # Slice 3 of PROJECT-GTKB-CROSS-HARNESS-PARITY: discovery-diff over actual
        # harness hook surfaces (DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001 assertion
        # PARITY-DIFF-WIRED). WARN-only at Slice 3 per Q6; FAIL ramp + CI gate land
        # in Slice 6 after a coverage audit.
        checks.append(_check_harness_projection_conformance(target))
        checks.append(_check_deliberation_search_backend(target))
        # WI-4795: Phase-1 WARN surface for DCL-OBSOLETE-REFERENCE-PURGE-PAIRING-001
        # (deterministic obsolete-reference-purge pairing check).
        checks.append(_check_obsolete_reference_purge(target))
        # FAB-01 / HYG-001: exercise launchability of each active dispatch
        # target's argv head so a WinError-2-class launch regression surfaces
        # in the doctor rather than as a silent exit-127 in dispatch logs.
        checks.append(_check_harness_launchability(target))
        checks.append(_check_harness_local_scratchpad_boundary(target))
        checks.append(_check_canonical_authority_drift(target))
        checks.append(_check_session_wrap_had_orient(target))
        checks.append(_check_da_harvest_coverage(target))
        checks.append(_check_standing_backlog_health(target))
        checks.append(_check_orphan_citations(target))
        checks.append(_check_ollama_harness(target))
        checks.append(_check_provider_routing(target, "alibaba-cloud-studio"))
        checks.append(_check_provider_routing(target, "openrouter"))
        # WI-4778: Cursor headless dispatch readiness stays diagnostic until
        # the external Cursor Agent CLI is present and activation is deliberate.
        checks.append(_check_cursor_dispatch_readiness(target))
        # WI-4431 / FAB-19: Skill health check (WARN/advisory only)
        checks.append(_check_skill_health(target))

    # Isolation checks per Phase 9 §4 (GTKB-ISOLATION-017 Slice 1).
    # Local import avoids a circular dependency: doctor_isolation imports
    # ToolCheck from this module.
    from groundtruth_kb.project.doctor_isolation import run_isolation_checks

    _PRODUCT_ROOT = Path(__file__).resolve().parents[3]
    checks.extend(run_isolation_checks(target, profile, product_root=_PRODUCT_ROOT))
    checks.append(_check_registered_application_roots(target))

    # Auto-install pass
    if auto_install:
        checks = [_try_auto_install(c) for c in checks]

    report = DoctorReport(checks=checks, profile=profile)
    report._compute_overall()
    return report


def format_doctor_report(report: DoctorReport) -> str:
    """Format doctor report for terminal output."""
    lines = [
        "",
        f"  GroundTruth Project Doctor — Profile: {report.profile}",
        "  " + "=" * 50,
        "",
    ]

    status_icons = {"pass": "[OK]", "fail": "[FAIL]", "warning": "[WARN]", "info": "[INFO]"}

    for check in report.checks:
        icon = status_icons[check.status]
        lines.append(f"  {icon:>6}  {check.message}")

    lines.append("")
    overall_icon = status_icons[report.overall]
    lines.append(f"  Overall: {overall_icon} {report.overall.upper()}")

    if report.overall == "fail":
        failed = [c for c in report.checks if c.status == "fail" and c.required]
        if failed:
            lines.append("")
            lines.append("  Required tools missing:")
            for c in failed:
                lines.append(f"    - {c.name}: {c.message}")

    lines.append("")
    return "\n".join(lines)


def format_doctor_report_json(report: DoctorReport) -> dict[str, Any]:
    """Machine-readable JSON shape for dashboard ingestion.

    Per Phase 9 §4 line 226-228 (GTKB-ISOLATION-017 Slice 1): doctor output
    is machine-readable JSON plus a human-readable summary; both feed the
    adopter's dashboard per Phase 5. Schema is versioned for forward-compat.
    """
    return {
        "schema_version": "1",
        "profile": report.profile,
        "overall": report.overall,
        "checks": [
            {
                "name": c.name,
                "required": c.required,
                "found": c.found,
                "version": c.version,
                "min_version": c.min_version,
                "status": c.status,
                "message": c.message,
            }
            for c in report.checks
        ],
    }
