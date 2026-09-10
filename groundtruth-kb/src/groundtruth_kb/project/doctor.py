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
from typing import Any, Literal

from groundtruth_kb import get_templates_dir
from groundtruth_kb.bridge.role_state import (
    BRIDGE_AGENT_TO_RECIPIENT as _BRIDGE_AGENT_TO_RECIPIENT,
)
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
_TAFE_SCHEMA_REQUIRED_VIEWS = {
    "current_flow_definitions",
    "current_flow_instances",
    "current_stage_instances",
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
_LEGACY_ROOT_PATTERN_FILE_NAMES = frozenset({"hygiene-sweep-patterns.toml"})
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


def _check_core_spec_intake(target: Path) -> ToolCheck:
    """Doctor-style health surface for core-spec intake (SPEC-CORE-INTAKE-001).

    Read-only: reports the next missing core application specification slot for an
    enrolled adopter project, or pass when complete / not enrolled / opted out.
    """
    name = "Core spec intake"
    db_path = target / "groundtruth.db"
    if not db_path.exists():
        return ToolCheck(name=name, required=False, found=False, status="info", message="No groundtruth.db")
    try:
        from groundtruth_kb.db import KnowledgeDB
        from groundtruth_kb.project.core_spec_intake import (
            find_enrolled_project_id,
            intake_enabled,
            next_question,
        )

        if not intake_enabled(target):
            return ToolCheck(name=name, required=False, found=True, status="info", message="Opted out")
        db = KnowledgeDB(db_path)
        try:
            project_id = find_enrolled_project_id(db)
            if project_id is None:
                return ToolCheck(
                    name=name, required=False, found=True, status="pass", message="No enrolled intake project"
                )
            nxt = next_question(db, project_id)
        finally:
            db.close()
        if nxt is None:
            return ToolCheck(
                name=name, required=False, found=True, status="pass", message=f"{project_id}: core specs complete"
            )
        return ToolCheck(
            name=name,
            required=False,
            found=True,
            status="warning",
            message=f"{project_id}: next missing slot '{nxt['label']}' ({nxt['name']})",
        )
    except Exception as e:  # intentional-catch: validation tool, error -> info status
        return ToolCheck(name=name, required=False, found=True, status="info", message=f"Check error: {e}")


def _connect_readonly_sqlite(db_path: Path) -> sqlite3.Connection:
    return sqlite3.connect(f"{db_path.resolve().as_uri()}?mode=ro", uri=True)


def _check_tafe_schema(target: Path) -> ToolCheck:
    db_path = target / "groundtruth.db"
    if not db_path.exists():
        return ToolCheck(
            name="TAFE schema health",
            required=False,
            found=False,
            status="warning",
            message="TAFE schema health: groundtruth.db not found",
        )
    try:
        conn = _connect_readonly_sqlite(db_path)
        try:
            table_rows = conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
            view_rows = conn.execute("SELECT name FROM sqlite_master WHERE type='view'").fetchall()
            tables = {row[0] for row in table_rows}
            views = {row[0] for row in view_rows}
            findings: list[str] = []
            missing_tables = sorted(set(_TAFE_SCHEMA_REQUIRED_COLUMNS) - tables)
            if missing_tables:
                findings.append(f"missing tables: {', '.join(missing_tables)}")
            for table_name, required_columns in _TAFE_SCHEMA_REQUIRED_COLUMNS.items():
                if table_name not in tables:
                    continue
                columns = {row[1] for row in conn.execute(f"PRAGMA table_info({table_name})").fetchall()}
                missing_columns = sorted(required_columns - columns)
                if missing_columns:
                    findings.append(f"{table_name} missing columns: {', '.join(missing_columns)}")
            missing_views = sorted(_TAFE_SCHEMA_REQUIRED_VIEWS - views)
            if missing_views:
                findings.append(f"missing views: {', '.join(missing_views)}")
        finally:
            conn.close()
    except Exception as exc:  # intentional-catch: diagnostic doctor check, error -> warning
        return ToolCheck(
            name="TAFE schema health",
            required=False,
            found=True,
            status="warning",
            message=f"TAFE schema health: DB inspection failed: {exc}",
        )

    if findings:
        return ToolCheck(
            name="TAFE schema health",
            required=False,
            found=True,
            status="warning",
            message="TAFE schema health: " + "; ".join(findings),
        )
    return ToolCheck(
        name="TAFE schema health",
        required=False,
        found=True,
        status="pass",
        message=(
            "TAFE schema health: tables/views present "
            f"({len(_TAFE_SCHEMA_REQUIRED_COLUMNS)} tables, {len(_TAFE_SCHEMA_REQUIRED_VIEWS)} views)"
        ),
    )


def _decode_tafe_json(value: Any, *, field: str, flow_id: str, findings: list[str]) -> Any:
    try:
        return json.loads(value or "null")
    except (TypeError, json.JSONDecodeError) as exc:
        findings.append(f"{flow_id} {field} invalid JSON: {exc}")
        return None


def _check_tafe_flow_definitions(target: Path) -> ToolCheck:
    db_path = target / "groundtruth.db"
    if not db_path.exists():
        return ToolCheck(
            name="TAFE flow definitions health",
            required=False,
            found=False,
            status="warning",
            message="TAFE flow definitions health: groundtruth.db not found",
        )
    try:
        from groundtruth_kb.typed_artifact_flow import canonical_reviewed_task_flow_definitions  # noqa: PLC0415

        canonical = {seed["id"]: seed for seed in canonical_reviewed_task_flow_definitions()}
        conn = _connect_readonly_sqlite(db_path)
        conn.row_factory = sqlite3.Row
        try:
            row_count = conn.execute(
                "SELECT COUNT(*) FROM sqlite_master WHERE type='view' AND name='current_flow_definitions'"
            ).fetchone()[0]
            if not row_count:
                return ToolCheck(
                    name="TAFE flow definitions health",
                    required=False,
                    found=True,
                    status="warning",
                    message="TAFE flow definitions health: current_flow_definitions view missing",
                )
            rows = {
                row["id"]: row
                for row in conn.execute(
                    "SELECT * FROM current_flow_definitions WHERE COALESCE(lifecycle_status, status) = 'active'"
                ).fetchall()
            }
        finally:
            conn.close()
    except Exception as exc:  # intentional-catch: diagnostic doctor check, error -> warning
        return ToolCheck(
            name="TAFE flow definitions health",
            required=False,
            found=True,
            status="warning",
            message=f"TAFE flow definitions health: DB inspection failed: {exc}",
        )

    findings: list[str] = []
    missing = sorted(set(canonical) - set(rows))
    if missing:
        findings.append(f"missing active canonical definitions: {', '.join(missing)}")
    for flow_id, seed in canonical.items():
        row = rows.get(flow_id)
        if row is None:
            continue
        stage_sequence = _decode_tafe_json(
            row["stage_sequence"], field="stage_sequence", flow_id=flow_id, findings=findings
        )
        required_roles = _decode_tafe_json(
            row["required_roles_by_stage"],
            field="required_roles_by_stage",
            flow_id=flow_id,
            findings=findings,
        )
        if row["flow_type"] != seed["flow_type"]:
            findings.append(f"{flow_id} flow_type drift: {row['flow_type']} != {seed['flow_type']}")
        if stage_sequence != seed["stage_sequence"]:
            findings.append(f"{flow_id} stage_sequence drift")
        if isinstance(stage_sequence, list) and len(stage_sequence) != len(set(stage_sequence)):
            findings.append(f"{flow_id} stage_sequence contains duplicate stages")
        if isinstance(required_roles, dict) and isinstance(stage_sequence, list):
            missing_roles = [stage for stage in stage_sequence if stage not in required_roles]
            extra_roles = sorted(set(required_roles) - set(stage_sequence))
            if missing_roles:
                findings.append(f"{flow_id} missing required roles: {', '.join(missing_roles)}")
            if extra_roles:
                findings.append(f"{flow_id} has roles for unknown stages: {', '.join(extra_roles)}")
        if required_roles != seed["required_roles_by_stage"]:
            findings.append(f"{flow_id} required_roles_by_stage drift")

    if findings:
        return ToolCheck(
            name="TAFE flow definitions health",
            required=False,
            found=True,
            status="warning",
            message="TAFE flow definitions health: " + "; ".join(findings),
        )
    return ToolCheck(
        name="TAFE flow definitions health",
        required=False,
        found=True,
        status="pass",
        message=f"TAFE flow definitions health: {len(canonical)} canonical definitions active and well-formed",
    )


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
    elif set(routing) != {provider}:
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
    """WI-4778: surface Cursor headless dispatch readiness without activating it."""

    check_name = "Cursor dispatch readiness"
    try:
        from scripts.verify_cursor_dispatch import evaluate_readiness  # noqa: PLC0415
    except Exception as exc:  # noqa: BLE001 - doctor must surface import drift
        return ToolCheck(
            name=check_name,
            required=False,
            found=False,
            status="warning",
            message=f"scripts/verify_cursor_dispatch.py unavailable: {exc}",
        )

    try:
        result = evaluate_readiness(project_root=target)
    except Exception as exc:  # noqa: BLE001 - readiness probe is diagnostic
        return ToolCheck(
            name=check_name,
            required=False,
            found=True,
            status="warning",
            message=f"Cursor dispatch readiness probe failed: {exc}",
        )

    if result.get("ready"):
        dispatchable = "dispatchable" if result.get("dispatchable_now") else "ready but not currently selected"
        return ToolCheck(
            name=check_name,
            required=False,
            found=True,
            status="pass",
            message=f"Cursor headless Agent CLI readiness clean ({dispatchable})",
        )

    detail = str(result.get("first_failed_check") or "readiness check failed")
    return ToolCheck(
        name=check_name,
        required=False,
        found=True,
        status="warning",
        message=f"Cursor headless dispatch unavailable: {detail}",
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
    if relative_path.name in _LEGACY_ROOT_PATTERN_FILE_NAMES:
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


def _check_raw_written_close_intent_no_action(target: Path) -> ToolCheck:
    """WI-5811 (detection slice): WARN when an untracked NO-ACTION bridge file
    reads as a close/disposal rather than a verdict correction.

    The write-time bridge-compliance gate cannot intercept a hook-less harness
    that writes ``bridge/*.md`` via a raw filesystem write. That is the exact
    2026-07-31 Goose "auto-disposition" vector: 322 close-intent NO-ACTION files,
    none written through a gated path (see
    ``bridge/cleanup-evidence/goose-cursor-autonomous-loop-incident-20260731/``).
    Write-time enforcement (``_no_action_close_intent_deny`` / the WI-5850
    preflight-assertion-integrity guard) closes the Write-tool and governed-writer
    paths; this read-time check closes the residual raw-write path by making such
    artifacts DISCOVERABLE for quarantine even though no gate could block them.

    Reuses the gate's validated close-intent detector via dynamic import (single
    source of truth, no drift; N1 ∪ N2, measured 0/269 false-positive against the
    lawful corpus). Scans only untracked bridge files — committed files are the
    append-only audit trail and are out of scope for this working-tree detector.
    Fail-soft ``warning`` (never ``fail``): a surfaced discoverability signal, not
    a release block, since the artifact is already on disk and unblockable.
    """
    name = "raw-written close-intent NO-ACTION"
    if not (target / "bridge").is_dir():
        return ToolCheck(
            name=name,
            required=False,
            found=False,
            status="info",
            message="no bridge/ directory; nothing to verify",
        )
    gate_path = target / ".claude" / "hooks" / "bridge-compliance-gate.py"
    if not gate_path.is_file():
        return ToolCheck(
            name=name,
            required=False,
            found=False,
            status="info",
            message="bridge-compliance-gate.py absent; close-intent scan skipped",
        )
    try:
        import importlib.util

        spec = importlib.util.spec_from_file_location("_gtkb_bcg_doctor_close_intent", gate_path)
        gate = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(gate)
        detect = gate._no_action_close_intent_deny
    except Exception:  # noqa: BLE001 - detector unavailable must not crash doctor
        return ToolCheck(
            name=name,
            required=False,
            found=True,
            status="info",
            message="close-intent detector unavailable; scan skipped",
        )

    ok, out = _run_cmd(["git", "-C", str(target), "ls-files", "--others", "--exclude-standard", "bridge"])
    if not ok:
        return ToolCheck(
            name=name,
            required=False,
            found=True,
            status="info",
            message="git ls-files unavailable; close-intent scan skipped",
        )

    hits: list[str] = []
    for line in out.splitlines():
        rel = line.strip().replace("\\", "/")
        if not rel.endswith(".md"):
            continue
        # Scope to the LIVE top-level chain only: `bridge/<file>.md`. This mirrors
        # the actionability parsers (status_driver / bridge_thread_files /
        # versioned_files all use non-recursive glob("*.md")), and it excludes the
        # `bridge/cleanup-evidence/**` quarantine subtree — files relocated there
        # are already correctly dispositioned and must not re-alarm.
        if rel.count("/") != 1:
            continue
        try:
            content = _require_utf8_text(target / rel)
        except OSError:
            continue
        try:
            if detect(str(target / rel), content) is not None:
                hits.append(rel)
        except Exception:  # noqa: BLE001 - one bad file must not abort the scan
            continue

    if hits:
        return ToolCheck(
            name=name,
            required=False,
            found=True,
            status="warning",
            message=(
                "untracked NO-ACTION bridge files read as close/disposal rather than a "
                "verdict correction (raw-write vector bypassed all write-time gates; "
                "DCL-NO-ACTION-STATUS-SEMANTICS-001) — inspect and quarantine to "
                "bridge/cleanup-evidence/: " + ", ".join(sorted(hits))
            ),
        )
    return ToolCheck(
        name=name,
        required=False,
        found=True,
        status="pass",
        message="no untracked close-intent NO-ACTION bridge files detected",
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
            failures.append(
                f"registry identity failed: {len(identity['missing'])} missing locators, "
                f"{len(identity['object_kind_mismatches'])} object-kind mismatches"
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


def _check_sot_read_discipline(target: Path) -> ToolCheck:
    """Validate the SoT read-discipline hook coverage (DCL-SOT-READ-HOOK-CONTRACT-001).

    4-layer assertion:

    1. Canonical hook file presence (.claude/hooks/sot-read-discipline.py).
    2. Codex adapter presence (.codex/gtkb-hooks/sot-read-discipline-bash-adapter.py).
    3. Claude effective coverage: .claude/settings.json PreToolUse contains an entry
       whose matcher string includes Read AND Grep AND Glob, AND whose command
       resolves to the canonical hook.
    4. Codex effective coverage: .codex/hooks.json PreToolUse contains an entry
       with matcher "Bash" AND whose command resolves to the adapter. Anti-false-green:
       if Codex registration uses Read/Grep/Glob matcher (an unsupported tool-event
       surface per ADR-CODEX-HOOK-PARITY-FALLBACK-001 v2), the check fails with
       explicit guidance.
    5. Registry referential integrity: every forbidden_substitutes entry references
       a real storage_path in the registry projection.

    Severity is WARN-only during Slice 2A per the bridge proposal; promotion to FAIL
    is a Slice 2B candidate after coverage audit.
    """
    check_name = "SoT read-discipline hook coverage"
    canonical_hook = target / ".claude" / "hooks" / "sot-read-discipline.py"
    codex_adapter = target / ".codex" / "gtkb-hooks" / "sot-read-discipline-bash-adapter.py"
    claude_settings = target / ".claude" / "settings.json"
    codex_hooks = target / ".codex" / "hooks.json"

    warnings: list[str] = []

    # Layer 1: canonical hook
    if not canonical_hook.is_file():
        warnings.append(f"canonical hook missing: {canonical_hook.relative_to(target).as_posix()}")

    # Layer 2: Codex adapter
    if not codex_adapter.is_file():
        warnings.append(f"Codex adapter missing: {codex_adapter.relative_to(target).as_posix()}")

    # Layer 3: Claude registration
    if claude_settings.is_file():
        try:
            claude_data = json.loads(_require_utf8_text(claude_settings))
        except (OSError, json.JSONDecodeError) as exc:
            warnings.append(f"Claude settings.json unreadable: {exc}")
            claude_data = {}
        claude_pre = claude_data.get("hooks", {}).get("PreToolUse", []) if isinstance(claude_data, dict) else []
        claude_hit = False
        for entry in claude_pre if isinstance(claude_pre, list) else []:
            if not isinstance(entry, dict):
                continue
            matcher = str(entry.get("matcher", ""))
            if not all(tok in matcher for tok in ("Read", "Grep", "Glob")):
                continue
            for hook_entry in entry.get("hooks", []) if isinstance(entry.get("hooks"), list) else []:
                cmd = str(hook_entry.get("command", "") if isinstance(hook_entry, dict) else "")
                if "sot-read-discipline.py" in cmd:
                    claude_hit = True
                    break
            if claude_hit:
                break
        if not claude_hit:
            warnings.append(
                "Claude registration missing or matcher does not include Read+Grep+Glob "
                "(per DCL-SOT-READ-HOOK-CONTRACT-001 v1)"
            )
    else:
        warnings.append(".claude/settings.json absent — cannot verify Claude registration")

    # Layer 4: Codex registration (anti-false-green)
    if codex_hooks.is_file():
        try:
            codex_data = json.loads(_require_utf8_text(codex_hooks))
        except (OSError, json.JSONDecodeError) as exc:
            warnings.append(f".codex/hooks.json unreadable: {exc}")
            codex_data = {}
        _hooks = codex_data.get("hooks", {}) if isinstance(codex_data, dict) else {}
        codex_pre = _hooks.get("PreToolUse", []) if isinstance(_hooks, dict) else []
        codex_bash_hit = False
        codex_false_green = False
        for entry in codex_pre if isinstance(codex_pre, list) else []:
            if not isinstance(entry, dict):
                continue
            matcher = str(entry.get("matcher", ""))
            for hook_entry in entry.get("hooks", []) if isinstance(entry.get("hooks"), list) else []:
                cmd = str(hook_entry.get("command", "") if isinstance(hook_entry, dict) else "")
                if "sot-read-discipline" not in cmd:
                    continue
                if matcher == "Bash":
                    codex_bash_hit = True
                elif any(tok in matcher for tok in ("Read", "Grep", "Glob")):
                    codex_false_green = True
        if codex_false_green:
            warnings.append(
                "Codex registration uses Read/Grep/Glob matcher — these are NOT live Codex "
                "tool-events (per ADR-CODEX-HOOK-PARITY-FALLBACK-001 v2). Use matcher 'Bash' "
                "pointing at .codex/gtkb-hooks/sot-read-discipline-bash-adapter.py instead."
            )
        elif not codex_bash_hit:
            warnings.append(
                "Codex registration missing or matcher is not 'Bash' (per DCL-SOT-READ-HOOK-CONTRACT-001 v1)"
            )
    else:
        warnings.append(".codex/hooks.json absent — cannot verify Codex registration")

    # Layer 5: Registry referential integrity from one coherent generation.
    try:
        from groundtruth_kb.project.registry_control_plane import load_registry_snapshot

        rows = load_registry_snapshot(project_root=target).records
        known_paths = {row.storage_path for row in rows if row.storage_path}
        for row in rows:
            for substitute in row.forbidden_substitutes:
                if substitute and not any(known.endswith(substitute) or substitute in known for known in known_paths):
                    warnings.append(
                        f"forbidden_substitutes on {row.id!r} references {substitute!r} "
                        "which does not match any known SoT storage_path"
                    )
                    break
    except Exception as exc:  # intentional-catch: authority failure must be visible
        warnings.append(f"coherent registry authority unavailable: {exc}")

    if warnings:
        return ToolCheck(
            name=check_name,
            required=False,
            found=True,
            status="warning",
            message="; ".join(warnings[:5]) + (" (+more)" if len(warnings) > 5 else ""),
        )

    return ToolCheck(
        name=check_name,
        required=False,
        found=True,
        status="pass",
        message=(
            "canonical hook + Codex adapter present; Claude+Codex registrations effective; "
            "registry referential integrity OK"
        ),
    )


def _check_sot_duplicate_guard(target: Path) -> ToolCheck:
    """Run the duplicate-SoT drift-prevention guard from the verified audit engine."""
    check_name = "SoT duplicate guard"

    try:
        from groundtruth_kb.project.sot_audit import run_duplicate_sot_audit
    except Exception as exc:  # pragma: no cover - defensive import boundary
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


def _load_canonical_terminology_config(target: Path) -> dict[str, object] | None:
    """Load ``.claude/rules/canonical-terminology.toml`` or return ``None`` if absent/malformed.

    Returns the parsed TOML as a dict. ``None`` indicates the config is
    missing — the caller should treat this as an ERROR (config is required
    by the scaffold for every profile per SPEC-TERMINOLOGY-CONFIG-TOML).

    The canonical-terminology config is a managed ``rule`` artifact in the
    registry (``rule.canonical-terminology-config``), but its presence and
    validity are enforced by this composite check, not by generic
    ``_check_rules()`` Markdown enumeration.
    """
    import tomllib

    toml_path = target / ".claude" / "rules" / "canonical-terminology.toml"
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

    Returns the effective config dict with ``required_startup_terms``,
    ``required_files``, ``missing_severity``, and (optionally)
    ``memory_md_location`` keys. Returns ``None`` when the profile is not
    configured in the TOML.
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


def _check_canonical_terminology(target: Path, profile_name: str) -> ToolCheck:
    """Check canonical-terminology surface per SPEC-TERMINOLOGY-DOCTOR-CHECK.

    Reads the profile-aware matrix from ``.claude/rules/canonical-terminology.toml``.
    ERROR when required startup terms are missing from the profile's required
    files; WARN when minor drift is detected. Runs for every profile, with the
    required-term set selected by profile per SPEC-TERMINOLOGY-PROFILE-MATRIX.

    The two canonical-terminology files are managed ``rule`` artifacts in
    ``templates/managed-artifacts.toml`` (``rule.canonical-terminology`` and
    ``rule.canonical-terminology-config``). Lifecycle (scaffold/upgrade) is
    registry-driven; presence/validity is enforced by this composite check
    rather than by generic ``_check_rules()`` Markdown enumeration.

    Skipped (pass with 'not applicable') if the harness-memory override is in
    effect and the requested file is MEMORY.md — projects whose harness holds
    MEMORY.md outside the project repo opt in by setting
    ``memory_md_location = "harness"`` in their profile block.
    """
    config = _load_canonical_terminology_config(target)
    if config is None:
        return ToolCheck(
            name="canonical terminology",
            required=True,
            found=False,
            status="fail",
            message=(
                ".claude/rules/canonical-terminology.toml missing or malformed — "
                "run `gt project upgrade --apply` to restore."
            ),
        )

    profile_cfg = _resolve_profile_config(config, profile_name)
    if profile_cfg is None:
        # Unknown profile in config — don't fail; warn.
        return ToolCheck(
            name="canonical terminology",
            required=False,
            found=True,
            status="warning",
            message=f"profile {profile_name!r} not configured in canonical-terminology.toml",
        )

    raw_terms = profile_cfg.get("required_startup_terms", [])
    required_terms: list[str] = [t for t in raw_terms if isinstance(t, str)] if isinstance(raw_terms, list) else []
    raw_files = profile_cfg.get("required_files", [])
    required_files: list[str] = [f for f in raw_files if isinstance(f, str)] if isinstance(raw_files, list) else []
    missing_severity_raw = profile_cfg.get("missing_severity", "ERROR")
    missing_severity = str(missing_severity_raw).upper() if missing_severity_raw else "ERROR"
    memory_md_location = profile_cfg.get("memory_md_location", "project")

    # Verify the canonical-terminology glossary file exists.
    glossary_md = target / ".claude" / "rules" / "canonical-terminology.md"
    if not glossary_md.exists():
        return ToolCheck(
            name="canonical terminology",
            required=True,
            found=False,
            status="fail",
            message=(".claude/rules/canonical-terminology.md missing — run `gt project upgrade --apply` to restore."),
        )

    # CONTRACT 1 (preserved): required_startup_terms must appear in every required_files entry.
    # Track startup-file misses SEPARATELY from primer-file misses per Codex
    # `gtkb-gov-term-primer-startup-2026-05-02-008.md` F1 — each contract emits at its own severity.
    startup_missing: list[str] = []
    for rel in required_files:
        # harness-memory profile: MEMORY.md is out-of-repo; skip content check for it.
        if rel == "MEMORY.md" and memory_md_location == "harness":
            continue

        abs_path = target / rel
        if not abs_path.exists():
            startup_missing.append(f"{rel}: file missing")
            continue
        try:
            text = abs_path.read_text(encoding="utf-8", errors="replace")
        except OSError as exc:
            startup_missing.append(f"{rel}: unreadable ({exc})")
            continue

        for term in required_terms:
            if term not in text:
                startup_missing.append(f"{rel}: missing term {term!r}")

    # CONTRACT 2 (Slice 1 of GTKB-GOV-TERM-PRIMER-STARTUP, S327):
    # required_primer_terms must appear in the primer file (not in required_files).
    # Per Codex `-004.md` F1 option 1 + `-008.md` F1: independent severity contract.
    primer_missing: list[str] = []
    raw_primer_terms = profile_cfg.get("required_primer_terms", [])
    required_primer_terms: list[str] = (
        [t for t in raw_primer_terms if isinstance(t, str)] if isinstance(raw_primer_terms, list) else []
    )
    primer_missing_severity_raw = profile_cfg.get("primer_missing_severity", missing_severity_raw)
    primer_missing_severity = str(primer_missing_severity_raw).upper() if primer_missing_severity_raw else "ERROR"
    if required_primer_terms:
        defaults_section: dict[str, Any] = {}
        try:
            cfg_section = config.get("config") if isinstance(config, dict) else None
            if isinstance(cfg_section, dict):
                ds = cfg_section.get("defaults")
                if isinstance(ds, dict):
                    defaults_section = ds
        except AttributeError:
            defaults_section = {}
        primer_path_str = (
            profile_cfg.get("primer_path")
            or defaults_section.get("primer_path")
            or ".claude/rules/canonical-terminology.md"
        )
        primer_abs = target / str(primer_path_str)
        if not primer_abs.exists():
            primer_missing.append(f"{primer_path_str}: primer file missing")
        else:
            try:
                primer_text = primer_abs.read_text(encoding="utf-8", errors="replace")
                for term in required_primer_terms:
                    if term not in primer_text:
                        primer_missing.append(f"{primer_path_str}: missing primer term {term!r}")
            except OSError as exc:
                primer_missing.append(f"{primer_path_str}: unreadable ({exc})")

    # Per Codex `-008.md` F1: apply each contract's severity independently;
    # combine results with fail > warning > pass precedence.
    def _severity_to_status(sev: str) -> Literal["pass", "fail", "warning"]:
        if sev == "ERROR":
            return "fail"
        if sev == "WARN":
            return "warning"
        return "warning"

    statuses: list[Literal["pass", "fail", "warning"]] = []
    if startup_missing:
        statuses.append(_severity_to_status(missing_severity))
    if primer_missing:
        statuses.append(_severity_to_status(primer_missing_severity))

    if statuses:
        # fail > warning > pass precedence.
        if "fail" in statuses:
            combined: Literal["pass", "fail", "warning"] = "fail"
        elif "warning" in statuses:
            combined = "warning"
        else:
            combined = "warning"
        missing_report = startup_missing + primer_missing
        return ToolCheck(
            name="canonical terminology",
            required=True,
            found=True,
            status=combined,
            message=(
                f"Missing canonical terms in profile {profile_name!r} "
                f"required files: {'; '.join(missing_report[:6])}" + ("; ..." if len(missing_report) > 6 else "")
            ),
        )

    return ToolCheck(
        name="canonical terminology",
        required=True,
        found=True,
        status="pass",
        message=(
            f"Canonical-terminology surface OK — {len(required_terms)} required terms "
            f"present in {len(required_files)} required files (profile: {profile_name})"
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


def _check_file_bridge_setup(target: Path) -> ToolCheck:
    """Check file bridge configuration for dual-agent projects."""
    bridge_dir = target / "bridge"
    if not bridge_dir.is_dir():
        return ToolCheck(
            name="File Bridge Config",
            required=True,
            found=False,
            status="warning",
            message=(
                "Bridge directory not found; create bridge/ and file numbered "
                "bridge documents through dispatcher-backed flows."
            ),
        )

    rules_dir = target / ".claude" / "rules"
    # ``_check_file_bridge_setup`` is gated on ``p.includes_bridge`` at its
    # sole call site in :func:`run_doctor`, so sourcing the required-rule
    # set from the bridge-profile registry entries preserves prior behavior.
    required_rules = _required_bridge_rule_filenames("dual-agent")
    missing_rules = [r for r in required_rules if not (rules_dir / r).exists()]
    if missing_rules:
        return ToolCheck(
            name="File Bridge Config",
            required=True,
            found=True,
            status="warning",
            message=f"Missing bridge rule file(s) in .claude/rules/: {', '.join(missing_rules)}",
        )

    return ToolCheck(
        name="File Bridge Config",
        required=True,
        found=True,
        status="pass",
        message="File bridge directory and bridge rules present",
    )


def _check_file_bridge_state_parse(target: Path) -> ToolCheck:
    bridge_dir = target / "bridge"
    if not bridge_dir.exists():
        return ToolCheck(
            name="File Bridge State",
            required=True,
            found=False,
            status="fail",
            message="bridge directory not found; cannot parse bridge workflow state",
        )

    try:
        from groundtruth_kb.bridge.status_driver import collect_bridge_status

        snapshot = collect_bridge_status(target)
    except Exception as exc:  # intentional-catch: doctor health check
        return ToolCheck(
            name="File Bridge State",
            required=True,
            found=True,
            status="fail",
            message=f"Versioned bridge state unreadable: {exc}",
        )

    if snapshot.queue.parse_error_count:
        first_error = snapshot.queue.parse_errors[0] if snapshot.queue.parse_errors else {}
        return ToolCheck(
            name="File Bridge State",
            required=True,
            found=True,
            status="fail",
            message=f"Versioned bridge state malformed: {first_error}",
        )

    return ToolCheck(
        name="File Bridge State",
        required=True,
        found=True,
        status="pass",
        message=(
            f"Versioned bridge state parseable ({snapshot.queue.threads} "
            f"thread{'s' if snapshot.queue.threads != 1 else ''})"
        ),
    )


# -- Bridge dispatch liveness ------------------------------------------
# Bridge dispatch liveness reads recipients[role].updated_at from the shared
# dispatch-state.json written by the dispatcher daemon.

_BRIDGE_DISPATCH_STATE_PATH = Path(".gtkb-state/bridge-poller/dispatch-state.json")

_BRIDGE_FRESH_SECS = 4 * 60  # < 4 min → OK
_BRIDGE_WARN_SECS = 10 * 60  # 4–10 min → WARN; > 10 min → ALARM
_BRIDGE_DISPATCH_DOC = "docs/tutorials/dual-agent-setup.md"
_BRIDGE_AUTH_DOC = "docs/troubleshooting/auth.md"


def _check_bridge_dispatch_liveness(target: Path, agent: str) -> ToolCheck:
    """Check file bridge dispatch liveness for *agent* (``'claude'`` or ``'codex'``).

    Reads ``recipients[role].updated_at`` from ``dispatch-state.json`` and
    computes staleness against the freshness thresholds.

    - ``< 4 min`` or empty queue with fresh state heartbeat → OK
    - ``4–10 min`` → WARN
    - ``> 10 min`` → ALARM
    - File absent  → not started (WARN)
    - Missing / unparseable ``recipients[role].updated_at`` → ALARM
    """
    state_path = target / _BRIDGE_DISPATCH_STATE_PATH
    role = _BRIDGE_AGENT_TO_RECIPIENT.get(agent, agent)
    check_name = f"{agent.title()} bridge dispatch"

    if not state_path.exists():
        return ToolCheck(
            name=check_name,
            required=False,
            found=False,
            status="warning",
            message=(f"{agent} bridge dispatch not started; see {_BRIDGE_DISPATCH_DOC} for dispatcher daemon setup"),
        )

    try:
        raw = state_path.read_bytes().decode("utf-8-sig")
        data: object = json.loads(raw)
    except (OSError, json.JSONDecodeError, UnicodeDecodeError) as exc:
        return ToolCheck(
            name=check_name,
            required=False,
            found=True,
            status="fail",
            message=f"{agent} bridge dispatch-state file unreadable: {exc}",
        )

    if not isinstance(data, dict):
        return ToolCheck(
            name=check_name,
            required=False,
            found=True,
            status="fail",
            message=f"{agent} bridge dispatch-state file is not a JSON object",
        )

    recipients = data.get("recipients")
    if not isinstance(recipients, dict):
        return ToolCheck(
            name=check_name,
            required=False,
            found=True,
            status="fail",
            message=(f"{agent} bridge dispatch-state missing 'recipients' map — ALARM. See {_BRIDGE_AUTH_DOC}"),
        )

    recipient_state = recipients.get(role)
    if recipient_state is None:
        matching = [k for k in recipients if k.startswith(f"{role}:") and isinstance(recipients[k], dict)]
        if matching:
            matching.sort(key=lambda k: str(recipients[k].get("updated_at") or ""), reverse=True)
            recipient_state = recipients[matching[0]]

    if not isinstance(recipient_state, dict):
        return ToolCheck(
            name=check_name,
            required=False,
            found=True,
            status="fail",
            message=(
                f"{agent} bridge dispatch-state missing 'recipients.{role}' entry — ALARM. See {_BRIDGE_AUTH_DOC}"
            ),
        )

    updated_at_raw = recipient_state.get("updated_at")
    last_result = recipient_state.get("last_result", "unknown")
    pending_count = recipient_state.get("pending_count", 0)
    state_display = f"{last_result}, pending: {pending_count}"

    if not isinstance(updated_at_raw, str) or not updated_at_raw.strip():
        return ToolCheck(
            name=check_name,
            required=False,
            found=True,
            status="fail",
            message=(
                f"{agent} bridge dispatch-state missing recipients.{role}.updated_at — ALARM. See {_BRIDGE_AUTH_DOC}"
            ),
        )

    try:
        updated_at = datetime.fromisoformat(updated_at_raw.replace("Z", "+00:00"))
    except ValueError:
        return ToolCheck(
            name=check_name,
            required=False,
            found=True,
            status="fail",
            message=(
                f"{agent} bridge dispatch-state has unparseable updated_at "
                f"{updated_at_raw!r} — ALARM. See {_BRIDGE_AUTH_DOC}"
            ),
        )

    now = datetime.now(tz=UTC)
    age_secs = (now - updated_at).total_seconds()
    age_min = int(age_secs // 60)
    age_sec_part = int(age_secs % 60)
    age_display = f"{age_min}m {age_sec_part}s ago"

    # Compute top-level staleness (DCL-DISPATCH-STATE-STALENESS-THRESHOLD-001)
    top_updated_at_raw = data.get("updated_at")
    top_updated_at = None
    if isinstance(top_updated_at_raw, str) and top_updated_at_raw.strip():
        with suppress(ValueError):
            top_updated_at = datetime.fromisoformat(top_updated_at_raw.replace("Z", "+00:00"))
    if top_updated_at is None:
        try:
            mtime = state_path.stat().st_mtime
            top_updated_at = datetime.fromtimestamp(mtime, tz=UTC)
        except OSError:
            pass

    is_top_stale = False
    top_age_display = ""
    if top_updated_at is not None:
        top_age_secs = (now - top_updated_at).total_seconds()
        if top_age_secs > 3600:
            is_top_stale = True
            top_age_min = int(top_age_secs // 60)
            top_age_sec_part = int(top_age_secs % 60)
            top_age_display = f"{top_age_min}m {top_age_sec_part}s ago"

    top_state_is_fresh = top_updated_at is not None and not is_top_stale
    is_empty_queue = pending_count == 0

    if age_secs < _BRIDGE_FRESH_SECS:
        status: Literal["pass", "fail", "warning", "info"] = "pass"
        message = f"{agent} bridge dispatch: OK (last update {age_display}, state: {state_display})"
    elif is_empty_queue and top_state_is_fresh:
        status = "pass"
        message = (
            f"{agent} bridge dispatch: OK (empty queue idle; recipient last update {age_display}, "
            f"state: {state_display})"
        )
    elif age_secs < _BRIDGE_WARN_SECS:
        status = "warning"
        message = (
            f"{agent} bridge dispatch: WARN (last update {age_display}, state: {state_display}) "
            f"— investigate dispatcher daemon liveness or see {_BRIDGE_DISPATCH_DOC}"
        )
    else:
        status = "fail"
        message = (
            f"{agent} bridge dispatch: ALARM (last update {age_display}, state: {state_display}) "
            f"— check {_BRIDGE_AUTH_DOC} and {_BRIDGE_DISPATCH_DOC}"
        )

    if is_top_stale:
        if status == "pass":
            status = "warning"
        message += f" (stale dispatch-state.json: last updated {top_age_display} ago)"

    return ToolCheck(
        name=check_name,
        required=False,
        found=True,
        status=status,
        message=message,
    )


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


def _check_dispatcher_daemon_substrate_readiness(target: Path) -> ToolCheck:
    """Correlate bridge substrate with dispatcher-daemon liveness (WI-4848 slice 3c)."""
    check_name = "Dispatcher daemon substrate readiness"
    from groundtruth_kb.mode_switch.validation import (
        DISPATCHER_DAEMON_HEARTBEAT_MAX_AGE_SECONDS,
        DISPATCHER_DAEMON_SUBSTRATE,
    )

    sub_path = target / "harness-state" / "bridge-substrate.json"
    substrate = DISPATCHER_DAEMON_SUBSTRATE
    if sub_path.is_file():
        try:
            sub_doc = json.loads(_require_utf8_text(sub_path))
            if isinstance(sub_doc, dict):
                raw = sub_doc.get("substrate")
                if isinstance(raw, str) and raw.strip():
                    substrate = raw.strip()
        except (OSError, json.JSONDecodeError):
            return ToolCheck(
                name=check_name,
                required=False,
                found=True,
                status="warning",
                message="harness-state/bridge-substrate.json is unreadable; substrate correlation skipped",
            )

    daemon_script = target / "scripts" / "gtkb_dispatcher_daemon.py"
    if not daemon_script.is_file():
        return ToolCheck(
            name=check_name,
            required=False,
            found=False,
            status="warning",
            message="scripts/gtkb_dispatcher_daemon.py missing; daemon substrate check skipped",
        )

    import importlib.util

    spec = importlib.util.spec_from_file_location(
        "gtkb_dispatcher_daemon_doctor",
        daemon_script,
    )
    if spec is None or spec.loader is None:
        return ToolCheck(
            name=check_name,
            required=False,
            found=True,
            status="warning",
            message="could not load gtkb_dispatcher_daemon.py for substrate correlation",
        )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    daemon_status = module.collect_daemon_status(target)
    running = bool(daemon_status.get("running"))
    heartbeat_age = daemon_status.get("heartbeat_age_seconds")
    stale = not running or heartbeat_age is None or float(heartbeat_age) > DISPATCHER_DAEMON_HEARTBEAT_MAX_AGE_SECONDS

    if substrate == DISPATCHER_DAEMON_SUBSTRATE:
        if stale:
            detail = (
                f"active substrate is {DISPATCHER_DAEMON_SUBSTRATE!r} but daemon is not healthy "
                f"(running={running}, heartbeat_age_seconds={heartbeat_age})"
            )
            return ToolCheck(
                name=check_name,
                required=False,
                found=True,
                status="warning",
                message=(
                    detail + f"; threshold={DISPATCHER_DAEMON_HEARTBEAT_MAX_AGE_SECONDS}s. "
                    "See .claude/rules/dispatcher-daemon-substrate-rollback-runbook.md"
                ),
            )
        return ToolCheck(
            name=check_name,
            required=False,
            found=True,
            status="pass",
            message=(f"active substrate is {DISPATCHER_DAEMON_SUBSTRATE!r} and daemon heartbeat is fresh"),
        )

    if running and heartbeat_age is not None and float(heartbeat_age) <= DISPATCHER_DAEMON_HEARTBEAT_MAX_AGE_SECONDS:
        return ToolCheck(
            name=check_name,
            required=False,
            found=True,
            status="pass",
            message=(
                f"substrate is {substrate!r} (daemon running with fresh heartbeat; advisory-only — go-live not active)"
            ),
        )

    return ToolCheck(
        name=check_name,
        required=False,
        found=True,
        status="pass",
        message=f"substrate is {substrate!r}; daemon substrate go-live path is not selected",
    )


def _check_dispatcher_daemon_supervisor_task(
    target: Path,
    load_complex_health: Callable[[], dict[str, Any]] | None = None,
) -> ToolCheck:
    """Warn when dispatcher_daemon substrate lacks a healthy Windows supervisor (WI-4937)."""
    check_name = "Dispatcher daemon supervisor task"
    skip = _dispatcher_daemon_task_skip_check(target, check_name=check_name, component_label="supervisor")
    if skip is not None:
        return skip

    status = _dispatcher_complex_component_status(
        load_complex_health or _dispatcher_complex_health_reader(target), "supervisor"
    )
    if status.get("healthy"):
        return ToolCheck(
            name=check_name,
            required=False,
            found=True,
            status="pass",
            message="GTKB-DispatcherDaemon supervisor is registered, enabled, and headless",
        )
    findings = status.get("findings") or []
    detail = "; ".join(str(item) for item in findings) or "supervisor unhealthy"
    return ToolCheck(
        name=check_name,
        required=False,
        found=bool(status.get("registered")),
        status="warning",
        message=(f"{detail}. Install/enable with: gt bridge dispatch daemon supervisor install"),
    )


def _check_dispatcher_daemon_watchdog_task(
    target: Path,
    load_complex_health: Callable[[], dict[str, Any]] | None = None,
) -> ToolCheck:
    """Warn when dispatcher_daemon substrate lacks a healthy Windows storm watchdog (WI-5023)."""
    check_name = "Dispatcher daemon watchdog task"
    skip = _dispatcher_daemon_task_skip_check(target, check_name=check_name, component_label="watchdog")
    if skip is not None:
        return skip

    status = _dispatcher_complex_component_status(
        load_complex_health or _dispatcher_complex_health_reader(target), "watchdog"
    )
    if status.get("healthy"):
        return ToolCheck(
            name=check_name,
            required=False,
            found=True,
            status="pass",
            message="GTKB-HarnessStormWatchdog is registered, enabled, hidden, and uses pythonw.exe",
        )
    findings = status.get("findings") or []
    detail = "; ".join(str(item) for item in findings) or "watchdog unhealthy"
    return ToolCheck(
        name=check_name,
        required=False,
        found=bool(status.get("registered")),
        status="warning",
        message=(f"{detail}. Install/enable with: gt bridge dispatch daemon watchdog install"),
    )


def _check_service_sot_watchdog(
    target: Path,
    load_task_status: Callable[[Path], dict[str, Any]] | None = None,
) -> ToolCheck:
    """Warn when the platform service/SoT watchdog task is absent or stale."""
    check_name = "Service/SoT watchdog task"
    registry_path = target / "config" / "registry" / "sot-artifacts.toml"
    if not registry_path.is_file():
        return ToolCheck(
            name=check_name,
            required=False,
            found=True,
            status="pass",
            message="Service/SoT watchdog skipped outside a platform SoT-registry workspace",
        )
    if os.name != "nt":
        return ToolCheck(
            name=check_name,
            required=False,
            found=True,
            status="pass",
            message="Service/SoT watchdog task check is Windows-only; skipped on this host",
        )

    try:
        if load_task_status is None:
            from groundtruth_kb.watchdog.service_sot import collect_task_status

            status = collect_task_status(target)
        else:
            status = load_task_status(target)
    except Exception as exc:  # noqa: BLE001 - doctor checks fail soft
        return ToolCheck(
            name=check_name,
            required=False,
            found=False,
            status="warning",
            message=f"Service/SoT watchdog status unavailable: {exc}",
        )

    if status.get("healthy"):
        return ToolCheck(
            name=check_name,
            required=False,
            found=True,
            status="pass",
            message="GTKB-ServiceSoTWatchdog is registered, enabled, hidden, fresh, and detection-only",
        )
    findings = status.get("findings") or []
    detail = "; ".join(str(item) for item in findings) or "service/SoT watchdog unhealthy"
    return ToolCheck(
        name=check_name,
        required=False,
        found=bool(status.get("registered")),
        status="warning",
        message=(f"{detail}. Install/enable with: gt watchdog service-sot install"),
    )


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
    except Exception as exc:  # noqa: BLE001 - doctor checks must report, not crash
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


def _dispatcher_daemon_task_skip_check(target: Path, *, check_name: str, component_label: str) -> ToolCheck | None:
    """Return a completed skip/warning check when the component probe is not applicable."""
    from groundtruth_kb.mode_switch.validation import DISPATCHER_DAEMON_SUBSTRATE

    if os.name != "nt":
        return ToolCheck(
            name=check_name,
            required=False,
            found=True,
            status="pass",
            message=f"{component_label} task check is Windows-only; skipped on this host",
        )

    sub_path = target / "harness-state" / "bridge-substrate.json"
    substrate = DISPATCHER_DAEMON_SUBSTRATE
    if sub_path.is_file():
        try:
            sub_doc = json.loads(_require_utf8_text(sub_path))
            if isinstance(sub_doc, dict):
                raw = sub_doc.get("substrate")
                if isinstance(raw, str) and raw.strip():
                    substrate = raw.strip()
        except (OSError, json.JSONDecodeError):
            return ToolCheck(
                name=check_name,
                required=False,
                found=True,
                status="warning",
                message=f"harness-state/bridge-substrate.json is unreadable; {component_label} check skipped",
            )

    if substrate != DISPATCHER_DAEMON_SUBSTRATE:
        return ToolCheck(
            name=check_name,
            required=False,
            found=True,
            status="pass",
            message=f"substrate is {substrate!r}; {component_label} task not required",
        )

    return None


def _collect_dispatcher_complex_health(target: Path) -> dict[str, Any]:
    from groundtruth_kb.dispatcher_complex import collect_complex_health

    try:
        return collect_complex_health(target)
    except Exception as exc:  # intentional-catch: doctor probes fail soft
        return {
            "components": {
                "daemon": {
                    "status": {
                        "healthy": False,
                        "registered": False,
                        "findings": [f"dispatcher complex health unavailable: {exc}"],
                    }
                },
                "supervisor": {
                    "status": {
                        "healthy": False,
                        "registered": False,
                        "findings": [f"dispatcher complex health unavailable: {exc}"],
                    }
                },
                "watchdog": {
                    "status": {
                        "healthy": False,
                        "registered": False,
                        "findings": [f"dispatcher complex health unavailable: {exc}"],
                    }
                },
            }
        }


def _dispatcher_complex_health_reader(target: Path) -> Callable[[], dict[str, Any]]:
    health: dict[str, Any] | None = None

    def read() -> dict[str, Any]:
        nonlocal health
        if health is None:
            health = _collect_dispatcher_complex_health(target)
        return health

    return read


def _dispatcher_complex_component_status(
    load_complex_health: Callable[[], dict[str, Any]],
    component_name: str,
) -> dict[str, Any]:
    health = load_complex_health()
    components = health.get("components")
    if not isinstance(components, dict):
        return {
            "healthy": False,
            "registered": False,
            "findings": ["dispatcher complex health payload has no components"],
        }
    component = components.get(component_name)
    if not isinstance(component, dict):
        return {
            "healthy": False,
            "registered": False,
            "findings": [f"dispatcher complex health payload has no {component_name} component"],
        }
    status = component.get("status")
    if isinstance(status, dict):
        return status
    finding = component.get("finding") or component.get("error") or f"{component_name} status unavailable"
    return {
        "healthy": False,
        "registered": False,
        "findings": [str(finding)],
    }


def _retired_bridge_worker_markers() -> tuple[str, ...]:
    return (
        "cross_" + "harness_" + "bridge_" + "trigger.py",
        "bridge-" + "dispatch-" + "trigger.cmd",
        "single_" + "harness_" + "bridge_" + "automation.py",
        "single_" + "harness_" + "bridge_" + "dispatcher.py",
    )


def _collect_hook_commands(value: object) -> list[str]:
    commands: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            if key == "command" and isinstance(child, str):
                commands.append(child)
            else:
                commands.extend(_collect_hook_commands(child))
    elif isinstance(value, list):
        for child in value:
            commands.extend(_collect_hook_commands(child))
    return commands


def _check_dispatcher_only_bridge_automation(target: Path) -> ToolCheck:
    """Check that automated bridge dispatch is daemon-only."""
    check_name = "Dispatcher-only bridge automation"

    daemon_script = target / "scripts" / "gtkb_dispatcher_daemon.py"
    if not daemon_script.is_file():
        return ToolCheck(
            name=check_name,
            required=False,
            found=False,
            status="fail",
            message=f"scripts/gtkb_dispatcher_daemon.py missing; see {_BRIDGE_DISPATCH_DOC} for daemon setup",
        )

    markers = _retired_bridge_worker_markers()
    script_findings = [
        marker for marker in markers if marker.endswith(".py") and (target / "scripts" / marker).exists()
    ]
    hook_findings: list[str] = []
    for hook_path in (target / ".claude" / "settings.json", target / ".codex" / "hooks.json"):
        if not hook_path.exists():
            continue
        try:
            payload = json.loads(_require_utf8_text(hook_path))
        except (OSError, json.JSONDecodeError) as exc:
            return ToolCheck(
                name=check_name,
                required=False,
                found=True,
                status="fail",
                message=f"{hook_path.relative_to(target).as_posix()} unreadable: {exc}",
            )
        for command in _collect_hook_commands(payload):
            if any(marker in command for marker in markers):
                hook_findings.append(f"{hook_path.relative_to(target).as_posix()}: {command[:160]}")

    if script_findings or hook_findings:
        head = (script_findings + hook_findings)[0]
        finding_count = len(script_findings) + len(hook_findings)
        extra = "" if finding_count == 1 else f" (+{finding_count - 1} more)"
        return ToolCheck(
            name=check_name,
            required=False,
            found=True,
            status="fail",
            message=f"retired bridge worker surface present: {head}{extra}",
        )

    state_path = target / _BRIDGE_DISPATCH_STATE_PATH
    if not state_path.exists():
        return ToolCheck(
            name=check_name,
            required=False,
            found=True,
            status="warning",
            message=(
                "dispatcher daemon script present and retired hook workers absent; dispatch-state.json not written yet"
            ),
        )

    return ToolCheck(
        name=check_name,
        required=False,
        found=True,
        status="pass",
        message="dispatcher daemon is the only automated bridge substrate and dispatch-state.json is present",
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


_HARNESS_SCRATCHPAD_BOUNDARY_DOCS = (
    Path("AGENTS.md"),
    Path(".claude") / "rules" / "project-root-boundary.md",
)
_HARNESS_SCRATCHPAD_REQUIRED_TERMS = (
    "harness-local scratchpads",
    "non-authoritative",
    "antigravity planning/brain files",
    "codex automation memory",
    "claude code auto-memory",
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


def _utf8_named_fail(fn):  # type: ignore[no-untyped-def]
    """Wrap a ToolCheck producer so undecodable files become FAIL, not abort."""

    def wrapped(*args, **kwargs):  # type: ignore[no-untyped-def]
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
    The check is deliberately narrow: it validates the two operator-facing
    boundary surfaces and fails if those surfaces regress to granting positive
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


def _check_lapsed_go_implementation_claims(target: Path) -> ToolCheck:
    """Warn when GO-latest implementation claims are lapsed past grace."""
    check_name = "Lapsed GO implementation claims"
    scripts_dir = target / "scripts"
    inserted = False
    if scripts_dir.is_dir() and str(scripts_dir) not in sys.path:
        sys.path.insert(0, str(scripts_dir))
        inserted = True
    try:
        try:
            from bridge_work_intent_registry import lapsed_go_implementation_claims  # type: ignore
        except (
            Exception
        ) as exc:  # pragma: no cover - defensive doctor surface  # intentional-catch: autogenerated check fix
            return ToolCheck(
                name=check_name,
                required=False,
                found=False,
                status="warning",
                message=f"Lapsed GO implementation claims: registry unavailable: {exc}",
            )
        try:
            claims = lapsed_go_implementation_claims(project_root=target)
        except Exception as exc:  # noqa: BLE001 - diagnostic doctor check  # intentional-catch: autogenerated check fix
            return ToolCheck(
                name=check_name,
                required=False,
                found=False,
                status="warning",
                message=f"Lapsed GO implementation claims: inspection failed: {exc}",
            )
    finally:
        if inserted:
            with suppress(ValueError):
                sys.path.remove(str(scripts_dir))

    if not claims:
        return ToolCheck(
            name=check_name,
            required=False,
            found=True,
            status="pass",
            message="Lapsed GO implementation claims: none",
        )
    examples = ", ".join(str(claim.get("thread_slug")) for claim in claims[:5])
    suffix = "" if len(claims) <= 5 else f", +{len(claims) - 5} more"
    return ToolCheck(
        name=check_name,
        required=False,
        found=True,
        status="warning",
        message=f"Lapsed GO implementation claims: {len(claims)} lapsed ({examples}{suffix})",
    )


def _work_tree_stray_age_hours(report: dict[str, Any]) -> list[float]:
    ages: list[float] = []
    for key in ("workspace_findings", "stash_findings", "worktree_findings"):
        for finding in report.get(key, []):
            if not isinstance(finding, dict) or finding.get("classification") != "stale":
                continue
            try:
                ages.append(float(finding.get("age_hours", 0)))
            except (TypeError, ValueError):
                continue
    return ages


def _format_work_tree_stray_ages(ages: list[float]) -> str:
    if not ages:
        return "age_hours=none"
    average = sum(ages) / len(ages)
    return f"age_hours=min={min(ages):.1f} avg={average:.1f} max={max(ages):.1f}"


def _format_auto_resolve_summary(report: dict[str, Any]) -> str:
    summary = report.get("auto_resolve_summary")
    if not isinstance(summary, dict):
        plan = report.get("auto_resolve_plan")
        if not isinstance(plan, dict):
            return ""
        counts = plan.get("counts", {})
        if not isinstance(counts, dict):
            return ""
        summary = {
            "dirty_paths": counts.get("dirty_paths", 0),
            "actuator_actions": counts.get("actuator_actions", {}),
        }
    actions = summary.get("actuator_actions", {})
    action_text = "none"
    if isinstance(actions, dict) and actions:
        action_text = ",".join(f"{key}={value}" for key, value in sorted(actions.items()) if value)
    return f"; auto_resolve=dirty_paths={summary.get('dirty_paths', 0)} actions={action_text}"


def _check_work_tree_strays(target: Path) -> ToolCheck:
    """Read-only WI-4356 doctor visibility for stale work-tree strays."""
    check_name = "work-tree strays"
    try:
        from groundtruth_kb.hygiene.strays import run_strays, stale_count  # noqa: PLC0415
    except Exception as exc:  # intentional-catch: doctor check must fail soft
        return ToolCheck(
            name=check_name,
            required=False,
            found=False,
            status="warning",
            message=f"Work-tree strays: scan unavailable: {exc}",
        )

    try:
        report = run_strays(target)
    except Exception as exc:  # intentional-catch: git-state collection must fail soft
        return ToolCheck(
            name=check_name,
            required=False,
            found=False,
            status="warning",
            message=f"Work-tree strays: scan unavailable: {exc}",
        )

    counts = report.get("counts", {})
    workspace = int(counts.get("workspace_stale", 0))
    stash = int(counts.get("stash_stale", 0))
    worktree = int(counts.get("worktree_stale", 0))
    stale = stale_count(report)
    if stale == 0:
        return ToolCheck(
            name=check_name,
            required=False,
            found=True,
            status="pass",
            message="Work-tree strays: no stale workspace, stash, or worktree findings",
        )

    ages = _format_work_tree_stray_ages(_work_tree_stray_age_hours(report))
    auto_resolve = _format_auto_resolve_summary(report)
    return ToolCheck(
        name=check_name,
        required=False,
        found=True,
        status="warning",
        message=(
            f"Work-tree strays: {stale} stale "
            f"(workspace={workspace}, stash={stash}, worktree={worktree}; {ages}{auto_resolve}); "
            "run `gt hygiene strays` for read-only details"
        ),
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
        except (
            Exception
        ) as exc:  # pragma: no cover - defensive doctor surface  # intentional-catch: autogenerated check fix
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


_DB_SNAPSHOT_OUTPUT_ALLOWLIST = re.compile(
    r"^[A-Za-z]:[/\\]Users[/\\][^/\\]+[/\\]AppData[/\\]Local[/\\]gtkb-snapshots[/\\]",
)


def _check_db_snapshot_freshness(target: Path) -> ToolCheck:
    """Check that a recent db snapshot exists (daily cadence expected)."""
    check_name = "DB snapshot freshness"
    try:
        from groundtruth_kb.config import GTConfig  # noqa: PLC0415
        from groundtruth_kb.db_snapshot import default_output_dir  # noqa: PLC0415

        cfg = GTConfig.load(config_path=target / "groundtruth.toml")
        out_dir = cfg.backup.snapshot_output_dir or default_output_dir(cfg)
    except Exception as exc:  # intentional-catch: autogenerated check fix
        return ToolCheck(
            name=check_name,
            required=False,
            found=False,
            status="warning",
            message=f"Cannot resolve snapshot output directory: {exc}",
        )
    out_path = Path(out_dir)
    if not out_path.is_dir():
        return ToolCheck(
            name=check_name,
            required=False,
            found=False,
            status="warning",
            message=f"Snapshot directory does not exist yet: {out_path}",
        )
    snapshots = sorted(out_path.glob("groundtruth-*.db"), key=lambda p: p.stat().st_mtime, reverse=True)
    if not snapshots:
        return ToolCheck(
            name=check_name,
            required=False,
            found=False,
            status="warning",
            message=f"No snapshot files found in {out_path}",
        )
    newest = snapshots[0]
    age_hours = (datetime.now(tz=UTC) - datetime.fromtimestamp(newest.stat().st_mtime, tz=UTC)).total_seconds() / 3600
    if age_hours > 48:
        return ToolCheck(
            name=check_name,
            required=False,
            found=True,
            status="warning",
            message=f"Newest snapshot is {age_hours:.0f}h old (>{48}h): {newest.name}",
        )
    return ToolCheck(
        name=check_name,
        required=False,
        found=True,
        status="pass",
        message=f"Newest snapshot {newest.name} is {age_hours:.0f}h old",
    )


def _check_db_snapshot_output_allowlist(target: Path) -> ToolCheck:
    """Enforce the DB-Snapshot Output Exception allowlist bound."""
    check_name = "DB snapshot output allowlist"
    try:
        from groundtruth_kb.config import GTConfig  # noqa: PLC0415
        from groundtruth_kb.db_snapshot import default_output_dir  # noqa: PLC0415

        cfg = GTConfig.load(config_path=target / "groundtruth.toml")
        out_dir = str(cfg.backup.snapshot_output_dir or default_output_dir(cfg))
    except Exception as exc:  # intentional-catch: autogenerated check fix
        return ToolCheck(
            name=check_name,
            required=True,
            found=False,
            status="warning",
            message=f"Cannot resolve snapshot output directory: {exc}",
        )
    if _DB_SNAPSHOT_OUTPUT_ALLOWLIST.match(out_dir):
        return ToolCheck(
            name=check_name,
            required=True,
            found=True,
            status="pass",
            message=f"Snapshot output {out_dir} matches allowlist",
        )
    return ToolCheck(
        name=check_name,
        required=True,
        found=True,
        status="fail",
        message=(
            f"Snapshot output {out_dir} does NOT match the DB-Snapshot Output "
            f"Exception allowlist in project-root-boundary.md"
        ),
    )


def _check_agent_red_app_root_minimization(target: Path) -> ToolCheck:
    """Run the Agent Red app-root minimization validator."""
    check_name = "Agent Red app-root minimization"
    app_root = target / "applications" / "Agent_Red"
    if not app_root.exists() and not (target / "applications").exists():
        return ToolCheck(
            name=check_name,
            required=True,
            found=False,
            status="pass",
            message="Agent Red app-root minimization skipped outside the GT-KB platform workspace",
        )

    try:
        from groundtruth_kb.isolation.app_root_minimization import validate_app_root_minimization  # noqa: PLC0415

        result = validate_app_root_minimization(app_root, project_root=target, tracked_only=True)
    except Exception as exc:  # intentional-catch: diagnostic doctor check should report, not crash
        return ToolCheck(
            name=check_name,
            required=True,
            found=app_root.exists(),
            status="fail",
            message=f"Agent Red app-root minimization validator failed to run: {exc}",
        )

    if result.ok:
        return ToolCheck(
            name=check_name,
            required=True,
            found=True,
            status="pass",
            message=f"Agent Red app-root minimization clean ({len(result.actual_entries)} top-level artifacts)",
        )

    return ToolCheck(
        name=check_name,
        required=True,
        found=app_root.exists(),
        status="fail",
        message=f"Agent Red app-root minimization failed: {result.first_error_message()}",
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
        checks.append(_check_file_bridge_setup(target))
        checks.append(_check_file_bridge_state_parse(target))
        checks.append(_check_active_legacy_root_references(target))
        checks.append(_check_registered_hooks_tracked(target))
        checks.append(_check_raw_written_close_intent_no_action(target))
        checks.append(_check_skill_rename_reference_sweep(target))
        checks.append(_check_scanner_safe_writer_drift(target, profile))
        checks.append(_check_safety_gate_registration(target))
        checks.append(_check_bridge_propose_skill_present(target, profile))
        checks.append(_check_spec_intake_skill_present(target, profile))
        checks.append(_check_codex_skill_load_health(target))
        checks.append(_check_managed_artifact_drift(target, profile))
        checks.append(_check_sot_registry_completeness(target))
        checks.append(_check_sot_read_discipline(target))
        checks.append(_check_sot_duplicate_guard(target))
        for registration in artifacts_for_doctor(profile, class_="settings-hook-registration"):
            if isinstance(registration, SettingsHookRegistration):
                checks.append(_check_settings_hook_registration_drift(target, profile, registration))
        checks.append(_check_bridge_dispatch_liveness(target, "claude"))
        checks.append(_check_bridge_dispatch_liveness(target, "codex"))
        checks.append(_check_dispatcher_only_bridge_automation(target))
        # Slice 3 of PROJECT-GTKB-CROSS-HARNESS-PARITY: discovery-diff over actual
        # harness hook surfaces (DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001 assertion
        # PARITY-DIFF-WIRED). WARN-only at Slice 3 per Q6; FAIL ramp + CI gate land
        # in Slice 6 after a coverage audit.
        checks.append(_check_harness_projection_conformance(target))
        checks.append(_check_dispatcher_daemon_substrate_readiness(target))
        dispatcher_complex_health = _dispatcher_complex_health_reader(target)
        checks.append(_check_dispatcher_daemon_supervisor_task(target, dispatcher_complex_health))
        checks.append(_check_dispatcher_daemon_watchdog_task(target, dispatcher_complex_health))
        checks.append(_check_service_sot_watchdog(target))
        checks.append(_check_deliberation_search_backend(target))
        checks.append(_check_lapsed_go_implementation_claims(target))
        checks.append(_check_work_tree_strays(target))
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
        checks.append(_check_tafe_schema(target))
        checks.append(_check_tafe_flow_definitions(target))
        checks.append(_check_ollama_harness(target))
        checks.append(_check_provider_routing(target, "alibaba-cloud-studio"))
        checks.append(_check_provider_routing(target, "openrouter"))
        # WI-4778: Cursor headless dispatch readiness stays diagnostic until
        # the external Cursor Agent CLI is present and activation is deliberate.
        checks.append(_check_cursor_dispatch_readiness(target))
        # WI-4431 / FAB-19: Skill health check (WARN/advisory only)
        checks.append(_check_skill_health(target))
        # FAB-03: DB snapshot checks
        checks.append(_check_db_snapshot_freshness(target))
        checks.append(_check_db_snapshot_output_allowlist(target))

    # Isolation checks per Phase 9 §4 (GTKB-ISOLATION-017 Slice 1).
    # Local import avoids a circular dependency: doctor_isolation imports
    # ToolCheck from this module.
    from groundtruth_kb.project.doctor_isolation import run_isolation_checks

    _PRODUCT_ROOT = Path(__file__).resolve().parents[3]
    checks.extend(run_isolation_checks(target, profile, product_root=_PRODUCT_ROOT))
    checks.append(_check_agent_red_app_root_minimization(target))

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
