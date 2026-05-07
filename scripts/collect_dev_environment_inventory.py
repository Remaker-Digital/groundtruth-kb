#!/usr/bin/env python3
"""Collect the GT-KB development environment inventory.

The collector intentionally separates a release-safe public inventory from a
local/private inventory. Public output uses relative evidence pointers and
redacted summaries only; local output may name local-only keys and discovery
failures, but it still never writes raw credential values.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import re
import shutil
import subprocess
import sys
import tomllib
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

SCHEMA_VERSION = 1
COLLECTOR_VERSION = "gtkb-dev-environment-inventory-v1"
DEFAULT_MAX_AGE_HOURS = 336
PUBLIC_JSON_RELATIVE_PATH = Path(".groundtruth/inventory/dev-environment-inventory.json")
PUBLIC_MARKDOWN_RELATIVE_PATH = Path(".groundtruth/inventory/dev-environment-inventory.md")
LOCAL_JSON_RELATIVE_PATH = Path(".gtkb-state/dev-environment-inventory/local.json")
PUBLIC_REQUIRED_SECTIONS = (
    "project",
    "collector",
    "host",
    "shell",
    "toolchain",
    "harnesses",
    "repo_configured_surfaces",
    "runtime_provided_capabilities",
    "role_by_harness_compatibility",
    "redaction",
    "verification",
)
MATRIX_ROWS = (
    ("claude", "prime-builder"),
    ("codex", "prime-builder"),
    ("claude", "loyal-opposition"),
    ("codex", "loyal-opposition"),
)
CAPABILITY_DIMENSIONS = (
    "startup_support",
    "canonical_terminology_load",
    "role_record_resolution",
    "file_bridge_read_write",
    "formal_artifact_mutation_gates",
    "hook_support",
    "skill_support",
    "command_support",
    "subagent_team_support",
    "mcp_support",
    "browser_automation",
    "github_pr_ci_access",
    "shell_runtime_behavior",
    "permission_approval_model",
    "credential_safety_gates",
    "release_package_command_support",
)
SENSITIVE_KEY_RE = re.compile(
    r"(token|secret|password|passwd|credential|api[_-]?key|private[_-]?key|client[_-]?secret|connection[_-]?string|"
    r"access[_-]?key|refresh[_-]?token|bearer)",
    re.IGNORECASE,
)
SENSITIVE_VALUE_RE = re.compile(
    r"(sk-[A-Za-z0-9_-]{10,}|gh[pousr]_[A-Za-z0-9_]{10,}|xox[baprs]-[A-Za-z0-9-]{10,}|"
    r"AKIA[0-9A-Z]{16}|-----BEGIN [A-Z ]*PRIVATE KEY-----|DefaultEndpointsProtocol=)",
    re.IGNORECASE,
)
ABSOLUTE_PATH_RE = re.compile(r"([A-Za-z]:\\|/Users/|/home/|/root/)")


def _now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _parse_iso8601(value: Any) -> datetime | None:
    text = str(value or "").strip()
    if not text:
        return None
    normalized = text[:-1] + "+00:00" if text.endswith("Z") else text
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError:
        return None
    return parsed.astimezone(UTC) if parsed.tzinfo else parsed.replace(tzinfo=UTC)


def _relative(path: Path, project_root: Path) -> str:
    try:
        return path.resolve().relative_to(project_root.resolve()).as_posix()
    except ValueError:
        return "redacted-outside-project-root"


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


def _read_json(path: Path) -> dict[str, Any]:
    try:
        loaded = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return loaded if isinstance(loaded, dict) else {}


def _read_toml(path: Path) -> dict[str, Any]:
    try:
        with path.open("rb") as handle:
            loaded = tomllib.load(handle)
    except (OSError, tomllib.TOMLDecodeError):
        return {}
    return loaded if isinstance(loaded, dict) else {}


def _file_sha256(path: Path) -> str | None:
    try:
        digest = hashlib.sha256()
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(65536), b""):
                digest.update(chunk)
    except OSError:
        return None
    return f"sha256:{digest.hexdigest()}"


def _file_state(project_root: Path, relative_path: str, *, classification: str = "public_safe") -> dict[str, Any]:
    path = project_root / relative_path
    return {
        "path": relative_path.replace("\\", "/"),
        "present": path.is_file(),
        "classification": classification,
        "evidence": relative_path.replace("\\", "/"),
    }


def _directory_entries(project_root: Path, relative_path: str, pattern: str) -> list[str]:
    root = project_root / relative_path
    if not root.is_dir():
        return []
    return sorted(_relative(path, project_root) for path in root.glob(pattern) if path.is_file())


def _extract_version(output: str, fallback: str = "unknown") -> str:
    first_line = next((line.strip() for line in output.splitlines() if line.strip()), "")
    if not first_line:
        return fallback
    version_match = re.search(r"(\d+(?:\.\d+)+(?:[A-Za-z0-9.+_-]*)?)", first_line)
    if version_match:
        return version_match.group(1)
    return first_line[:80]


def _run_tool_version(
    command: list[str], display_command: str, *, timeout: int = 8
) -> tuple[dict[str, Any], dict[str, Any]]:
    executable = command[0]
    resolved = executable if Path(executable).is_absolute() else shutil.which(executable)
    if not resolved:
        public = {
            "command": display_command,
            "status": "unsupported",
            "version": "unknown",
            "classification": "unsupported",
            "evidence": f"{display_command} not found on PATH",
        }
        return public, {**public, "resolved_executable": None, "returncode": None, "raw_output": ""}

    actual_command = [resolved, *command[1:]]
    try:
        result = subprocess.run(
            actual_command,
            cwd=None,
            text=True,
            capture_output=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        public = {
            "command": display_command,
            "status": "unknown",
            "version": "unknown",
            "classification": "unknown",
            "evidence": f"{display_command} could not be executed",
        }
        return public, {**public, "resolved_executable": resolved, "returncode": None, "raw_output": str(exc)}

    output = "\n".join(part for part in [result.stdout, result.stderr] if part).strip()
    status = "verified" if result.returncode == 0 else "unknown"
    public = {
        "command": display_command,
        "status": status,
        "version": _extract_version(output),
        "classification": status,
        "evidence": display_command,
    }
    private = {
        **public,
        "resolved_executable": resolved,
        "returncode": result.returncode,
        "raw_output": _redact_text(output),
    }
    return public, private


def _python_module_version(module: str) -> tuple[dict[str, Any], dict[str, Any]]:
    return _run_tool_version([sys.executable, "-m", module, "--version"], f"python -m {module} --version")


def _redact_text(value: str) -> str:
    return SENSITIVE_VALUE_RE.sub("<redacted>", value)


def _redaction_summary() -> tuple[dict[str, Any], dict[str, Any]]:
    private_matches = []
    categories: set[str] = set()
    for key, value in sorted(os.environ.items()):
        key_sensitive = bool(SENSITIVE_KEY_RE.search(key))
        value_sensitive = bool(SENSITIVE_VALUE_RE.search(value or ""))
        if not key_sensitive and not value_sensitive:
            continue
        category = "key_name" if key_sensitive else "value_pattern"
        categories.add(category)
        private_matches.append(
            {
                "key": key,
                "classification": "redacted",
                "reason": category,
                "value_present": bool(value),
                "value_length": len(value or ""),
                "value": "<redacted>",
            }
        )
    public = {
        "status": "pass",
        "public_output_policy": "public inventory contains only counts/classes for sensitive local values",
        "sensitive_environment_entry_count": len(private_matches),
        "sensitive_environment_categories": sorted(categories),
        "public_exclusions": [
            "raw credential values",
            "credential-like environment variable names",
            "absolute local paths",
            "machine-specific MCP config contents",
            "local command output with path detail",
        ],
    }
    return public, {"sensitive_environment_entries": private_matches}


def _project_identity(project_root: Path) -> dict[str, Any]:
    groundtruth_toml = _read_toml(project_root / "groundtruth.toml")
    package_init = project_root / "groundtruth-kb" / "src" / "groundtruth_kb" / "__init__.py"
    version_match = re.search(r'__version__\s*=\s*["\']([^"\']+)["\']', _read_text(package_init))
    project = groundtruth_toml.get("project", {}) if isinstance(groundtruth_toml.get("project"), dict) else {}
    return {
        "name": "GroundTruth-KB host workspace",
        "configured_project_name": str(project.get("project_name") or "unknown"),
        "profile": str(project.get("profile") or "unknown"),
        "scaffold_version": str(project.get("scaffold_version") or "unknown"),
        "groundtruth_kb_package_version": version_match.group(1) if version_match else "unknown",
        "root_boundary": ".",
        "classification": "public_safe",
    }


def _host_inventory() -> dict[str, Any]:
    return {
        "os_family": platform.system() or "unknown",
        "os_release": platform.release() or "unknown",
        "os_version": platform.version() or "unknown",
        "architecture": platform.machine() or "unknown",
        "python_platform": platform.platform(aliased=True, terse=True) or "unknown",
        "hostname": "redacted",
        "classification": "public_safe",
    }


def _shell_inventory() -> dict[str, Any]:
    shell_name = "unknown"
    if os.environ.get("PSMODULEPATH"):
        shell_name = "PowerShell-compatible"
    elif os.environ.get("SHELL"):
        shell_name = Path(os.environ["SHELL"]).name
    elif os.environ.get("COMSPEC"):
        shell_name = Path(os.environ["COMSPEC"]).name
    return {
        "current_shell_family": shell_name,
        "terminal": "redacted",
        "path_detail": "local_only",
        "classification": "public_safe",
    }


def _toolchain_inventory() -> tuple[dict[str, Any], dict[str, Any]]:
    public_tools: dict[str, Any] = {
        "python": {
            "command": "python --version",
            "status": "verified",
            "version": platform.python_version(),
            "classification": "verified",
            "evidence": "running interpreter",
        }
    }
    private_tools: dict[str, Any] = {
        "python": {
            **public_tools["python"],
            "resolved_executable": sys.executable,
            "raw_output": sys.version,
        }
    }
    module_commands = {"pip": "pip", "pytest": "pytest", "ruff": "ruff"}
    external_commands = {
        "node": ["node", "--version"],
        "npm": ["npm", "--version"],
        "git": ["git", "--version"],
        "gh": ["gh", "--version"],
        "playwright": ["playwright", "--version"],
    }
    for name, module in module_commands.items():
        public, private = _python_module_version(module)
        public_tools[name] = public
        private_tools[name] = private
    for name, command in external_commands.items():
        public, private = _run_tool_version(command, " ".join(command))
        public_tools[name] = public
        private_tools[name] = private
    return dict(sorted(public_tools.items())), dict(sorted(private_tools.items()))


def _harness_inventory(project_root: Path) -> dict[str, Any]:
    identities = _read_json(project_root / "harness-state" / "harness-identities.json")
    assignments = _read_json(project_root / "harness-state" / "role-assignments.json")
    codex_config = _read_toml(project_root / ".codex" / "config.toml")
    codex_hooks = _read_json(project_root / ".codex" / "hooks.json")
    claude_settings = _read_json(project_root / ".claude" / "settings.json")
    return {
        "identity_source": _file_state(project_root, "harness-state/harness-identities.json"),
        "role_assignment_source": _file_state(project_root, "harness-state/role-assignments.json"),
        "identities": {
            name: {"id": details.get("id"), "status": "verified" if details.get("id") else "unknown"}
            for name, details in sorted((identities.get("harnesses") or {}).items())
            if isinstance(details, dict)
        },
        "role_assignments": {
            harness_id: {
                "harness_type": details.get("harness_type"),
                "role": details.get("role"),
                "status": "verified" if details.get("role") else "unknown",
            }
            for harness_id, details in sorted((assignments.get("harnesses") or {}).items())
            if isinstance(details, dict)
        },
        "codex": {
            "config": _file_state(project_root, ".codex/config.toml"),
            "hooks": _file_state(project_root, ".codex/hooks.json"),
            "hooks_enabled": bool((codex_config.get("features") or {}).get("codex_hooks")),
            "session_start_configured": "SessionStart" in (codex_hooks.get("hooks") or {}),
        },
        "claude": {
            "settings": _file_state(project_root, ".claude/settings.json"),
            "session_start_configured": "SessionStart" in (claude_settings.get("hooks") or {}),
        },
    }


def _repo_surfaces(project_root: Path) -> dict[str, Any]:
    command_registry = _read_json(project_root / ".claude" / "commands" / "registry.json")
    command_entries = command_registry.get("commands") if isinstance(command_registry.get("commands"), dict) else {}
    workflows = _directory_entries(project_root, ".github/workflows", "*.yml") + _directory_entries(
        project_root, ".github/workflows", "*.yaml"
    )
    skills = sorted(Path(path).parent.name for path in _directory_entries(project_root, ".claude/skills", "*/SKILL.md"))
    hooks = _directory_entries(project_root, ".claude/hooks", "*.py")
    codex_hooks = _directory_entries(project_root, ".codex/gtkb-hooks", "*.py") + _directory_entries(
        project_root, ".codex/gtkb-hooks", "*.cmd"
    )
    return {
        "rules": {
            "count": len(_directory_entries(project_root, ".claude/rules", "*.md")),
            "items": _directory_entries(project_root, ".claude/rules", "*.md"),
            "classification": "public_safe",
        },
        "skills": {"count": len(skills), "items": skills, "classification": "public_safe"},
        "claude_hooks": {"count": len(hooks), "items": hooks, "classification": "public_safe"},
        "codex_hooks": {"count": len(codex_hooks), "items": codex_hooks, "classification": "public_safe"},
        "commands": {
            "count": len(command_entries),
            "items": sorted(command_entries),
            "registry": ".claude/commands/registry.json",
            "classification": "public_safe",
        },
        "git_hooks": {
            "pre_commit": _file_state(project_root, ".githooks/pre-commit"),
            "classification": "public_safe",
        },
        "github_workflows": {"count": len(workflows), "items": workflows, "classification": "public_safe"},
        "mcp_config": _file_state(project_root, ".mcp.json", classification="local_only"),
    }


def _runtime_capabilities() -> dict[str, Any]:
    return {
        "repo_local_collector_limit": {
            "status": "unsupported",
            "classification": "unsupported",
            "evidence": "active Codex/Claude plugin and MCP runtime lists are not exposed to this repo-local script",
            "recommended_source": "startup payload or harness-provided tool metadata when available",
        }
    }


def _capability(status: str, evidence: str) -> dict[str, str]:
    return {"status": status, "evidence": evidence}


def _compatibility_matrix(
    project_root: Path, harnesses: dict[str, Any], surfaces: dict[str, Any]
) -> list[dict[str, Any]]:
    bridge_present = (project_root / "bridge" / "INDEX.md").is_file()
    canonical_terms = (project_root / ".claude" / "rules" / "canonical-terminology.md").is_file()
    formal_gate = (project_root / ".claude" / "hooks" / "formal-artifact-approval-gate.py").is_file()
    credential_gate = (project_root / ".claude" / "hooks" / "credential-scan.py").is_file()
    pre_commit = (project_root / ".githooks" / "pre-commit").is_file()
    release_gate = (project_root / "scripts" / "release_candidate_gate.py").is_file()
    command_registry = (project_root / ".claude" / "commands" / "registry.json").is_file()
    skills_present = bool(surfaces.get("skills", {}).get("count"))
    workflows_present = bool(surfaces.get("github_workflows", {}).get("count"))
    mcp_present = (project_root / ".mcp.json").is_file()
    matrix = []
    for harness, role in MATRIX_ROWS:
        startup_configured = bool(harnesses.get(harness, {}).get("session_start_configured"))
        hook_configured = bool(
            harnesses.get(harness, {}).get("hooks", {}).get("present")
            or harnesses.get(harness, {}).get("settings", {}).get("present")
        )
        matrix.append(
            {
                "harness": harness,
                "role": role,
                "assignment": _assignment_status_for(harness, role, harnesses),
                "capabilities": {
                    "startup_support": _capability(
                        "configured" if startup_configured else "unknown",
                        f"{'.codex/hooks.json' if harness == 'codex' else '.claude/settings.json'} SessionStart",
                    ),
                    "canonical_terminology_load": _capability(
                        "configured" if canonical_terms else "unknown", ".claude/rules/canonical-terminology.md"
                    ),
                    "role_record_resolution": _capability(
                        "verified" if harnesses.get("role_assignment_source", {}).get("present") else "unknown",
                        "harness-state/role-assignments.json",
                    ),
                    "file_bridge_read_write": _capability(
                        "verified" if bridge_present else "unknown", "bridge/INDEX.md"
                    ),
                    "formal_artifact_mutation_gates": _capability(
                        "configured" if formal_gate else "unknown",
                        ".claude/hooks/formal-artifact-approval-gate.py",
                    ),
                    "hook_support": _capability(
                        "configured" if hook_configured else "unknown",
                        ".codex/hooks.json" if harness == "codex" else ".claude/settings.json",
                    ),
                    "skill_support": _capability(
                        "configured" if skills_present else "unknown", ".claude/skills/*/SKILL.md"
                    ),
                    "command_support": _capability(
                        "configured" if command_registry else "unknown", ".claude/commands/registry.json"
                    ),
                    "subagent_team_support": _capability(
                        "runtime_provided" if harness == "codex" else "unknown",
                        "harness runtime; not repo-configured",
                    ),
                    "mcp_support": _capability(
                        "configured" if mcp_present else "unknown",
                        ".mcp.json presence only; contents are local_only",
                    ),
                    "browser_automation": _capability(
                        "runtime_provided" if harness == "codex" else "unknown",
                        "harness runtime; not repo-configured",
                    ),
                    "github_pr_ci_access": _capability(
                        "configured" if workflows_present else "unknown", ".github/workflows/"
                    ),
                    "shell_runtime_behavior": _capability("verified", "collector executed in current shell"),
                    "permission_approval_model": _capability("configured", "AGENTS.md and harness role assignment"),
                    "credential_safety_gates": _capability(
                        "configured" if credential_gate and pre_commit else "unknown",
                        ".claude/hooks/credential-scan.py and .githooks/pre-commit",
                    ),
                    "release_package_command_support": _capability(
                        "configured" if release_gate else "unknown", "scripts/release_candidate_gate.py"
                    ),
                },
            }
        )
    return matrix


def _assignment_status_for(harness: str, role: str, harnesses: dict[str, Any]) -> dict[str, str]:
    identities = harnesses.get("identities") or {}
    assignments = harnesses.get("role_assignments") or {}
    harness_id = (identities.get(harness) or {}).get("id")
    assigned_role = (assignments.get(str(harness_id)) or {}).get("role")
    return {
        "harness_id": str(harness_id or "unknown"),
        "current_role": str(assigned_role or "unknown"),
        "matrix_role": role,
        "status": "verified" if assigned_role == role else "configured",
        "evidence": "harness-state/harness-identities.json + harness-state/role-assignments.json",
    }


def collect_inventory(project_root: Path, *, generated_at: str | None = None) -> tuple[dict[str, Any], dict[str, Any]]:
    project_root = project_root.resolve()
    generated = generated_at or _now_iso()
    redaction_public, redaction_private = _redaction_summary()
    toolchain_public, toolchain_private = _toolchain_inventory()
    harnesses = _harness_inventory(project_root)
    surfaces = _repo_surfaces(project_root)
    public = {
        "schema_version": SCHEMA_VERSION,
        "generated_at": generated,
        "project": _project_identity(project_root),
        "collector": {
            "name": "GT-KB development environment inventory collector",
            "version": COLLECTOR_VERSION,
            "script": "scripts/collect_dev_environment_inventory.py",
            "script_hash": _file_sha256(project_root / "scripts" / "collect_dev_environment_inventory.py"),
        },
        "host": _host_inventory(),
        "shell": _shell_inventory(),
        "toolchain": toolchain_public,
        "harnesses": harnesses,
        "repo_configured_surfaces": surfaces,
        "runtime_provided_capabilities": _runtime_capabilities(),
        "role_by_harness_compatibility": _compatibility_matrix(project_root, harnesses, surfaces),
        "redaction": redaction_public,
        "verification": {
            "latest_command": (
                "python scripts/collect_dev_environment_inventory.py "
                "--public-json docs/release/dev-environment-inventory.json "
                "--public-markdown docs/release/dev-environment-inventory.md "
                "--local-json .gtkb-state/dev-environment-inventory/local.json"
            ),
            "release_gate_check": "python scripts/release_candidate_gate.py --skip-python --skip-frontend",
            "status": "generated",
        },
    }
    private = {
        **public,
        "project_root": str(project_root),
        "toolchain": toolchain_private,
        "local_only": {
            **redaction_private,
            "mcp_config_present": (project_root / ".mcp.json").is_file(),
            "codex_hook_runtime_files": sorted(
                _relative(path, project_root)
                for path in (project_root / ".codex" / "gtkb-hooks").glob("last-*.json")
                if path.is_file()
            ),
        },
    }
    return public, private


def inventory_age_hours(payload: dict[str, Any], *, now: datetime | None = None) -> float | None:
    generated = _parse_iso8601(payload.get("generated_at"))
    if generated is None:
        return None
    current = now or datetime.now(UTC)
    return max(0.0, (current - generated).total_seconds() / 3600)


def validate_public_inventory_payload(
    payload: dict[str, Any],
    *,
    project_root: Path | None = None,
    max_age_hours: int | None = DEFAULT_MAX_AGE_HOURS,
    now: datetime | None = None,
) -> list[str]:
    errors: list[str] = []
    if payload.get("schema_version") != SCHEMA_VERSION:
        errors.append(f"schema_version must be {SCHEMA_VERSION}")
    missing_sections = [section for section in PUBLIC_REQUIRED_SECTIONS if section not in payload]
    if missing_sections:
        errors.append(f"missing required sections: {', '.join(missing_sections)}")
    age = inventory_age_hours(payload, now=now)
    if age is None:
        errors.append("generated_at is missing or invalid")
    elif max_age_hours is not None and age > max_age_hours:
        errors.append(f"inventory is stale: {age:.1f}h > {max_age_hours}h")
    if (payload.get("redaction") or {}).get("status") != "pass":
        errors.append("redaction.status must be pass")

    matrix = payload.get("role_by_harness_compatibility")
    if not isinstance(matrix, list):
        errors.append("role_by_harness_compatibility must be a list")
    else:
        seen_rows = {(row.get("harness"), row.get("role")) for row in matrix if isinstance(row, dict)}
        missing_rows = [f"{harness}/{role}" for harness, role in MATRIX_ROWS if (harness, role) not in seen_rows]
        if missing_rows:
            errors.append(f"missing compatibility rows: {', '.join(missing_rows)}")
        for row in matrix:
            if not isinstance(row, dict):
                continue
            capabilities = row.get("capabilities")
            if not isinstance(capabilities, dict):
                errors.append(f"{row.get('harness')}/{row.get('role')} missing capabilities")
                continue
            missing_capabilities = [name for name in CAPABILITY_DIMENSIONS if name not in capabilities]
            if missing_capabilities:
                errors.append(
                    f"{row.get('harness')}/{row.get('role')} missing capabilities: {', '.join(missing_capabilities)}"
                )

    rendered = json.dumps(payload, sort_keys=True)
    if SENSITIVE_VALUE_RE.search(rendered):
        errors.append("public inventory contains credential-shaped value")
    if ABSOLUTE_PATH_RE.search(rendered):
        errors.append("public inventory contains an absolute local path")
    if project_root is not None and str(project_root.resolve()) in rendered:
        errors.append("public inventory contains the project root absolute path")
    return errors


def render_markdown(payload: dict[str, Any]) -> str:
    project = payload.get("project") or {}
    collector = payload.get("collector") or {}
    redaction = payload.get("redaction") or {}
    toolchain = payload.get("toolchain") or {}
    harnesses = payload.get("harnesses") or {}
    surfaces = payload.get("repo_configured_surfaces") or {}
    matrix = payload.get("role_by_harness_compatibility") or []
    tool_rows = "\n".join(
        f"| `{name}` | {entry.get('status')} | `{entry.get('version')}` | `{entry.get('command')}` |"
        for name, entry in sorted(toolchain.items())
        if isinstance(entry, dict)
    )
    matrix_rows = "\n".join(
        f"| {row.get('harness')} | {row.get('role')} | {row.get('assignment', {}).get('status')} | "
        f"{sum(1 for cap in (row.get('capabilities') or {}).values() if cap.get('status') in {'verified', 'configured', 'runtime_provided'})} |"
        for row in matrix
        if isinstance(row, dict)
    )
    return "\n".join(
        [
            "# GT-KB Development Environment Inventory",
            "",
            f"Generated: {payload.get('generated_at')}",
            f"Collector: {collector.get('version')} ({collector.get('script_hash')})",
            "",
            "## Project",
            "",
            f"- Name: {project.get('name')}",
            f"- Configured project name: {project.get('configured_project_name')}",
            f"- GT-KB package version: {project.get('groundtruth_kb_package_version')}",
            f"- Scaffold version: {project.get('scaffold_version')}",
            "",
            "## Redaction",
            "",
            f"- Status: {redaction.get('status')}",
            f"- Sensitive local environment entries detected: {redaction.get('sensitive_environment_entry_count')}",
            "- Public output excludes raw credential values, local-only key names, and absolute local paths.",
            "",
            "## Toolchain",
            "",
            "| Tool | Status | Version | Evidence |",
            "|---|---|---|---|",
            tool_rows or "| none | unknown | unknown | unavailable |",
            "",
            "## Harness And Repo Surfaces",
            "",
            f"- Harness identity source present: {harnesses.get('identity_source', {}).get('present')}",
            f"- Role assignment source present: {harnesses.get('role_assignment_source', {}).get('present')}",
            f"- Skills: {surfaces.get('skills', {}).get('count')}",
            f"- Claude hooks: {surfaces.get('claude_hooks', {}).get('count')}",
            f"- Codex hooks: {surfaces.get('codex_hooks', {}).get('count')}",
            f"- GitHub workflows: {surfaces.get('github_workflows', {}).get('count')}",
            f"- MCP config: {surfaces.get('mcp_config', {}).get('classification')} presence only",
            "",
            "## Role By Harness Compatibility",
            "",
            "| Harness | Role | Assignment Status | Configured/Verified Capabilities |",
            "|---|---|---|---:|",
            matrix_rows or "| none | none | unknown | 0 |",
            "",
            "## Verification",
            "",
            f"- Latest command: `{(payload.get('verification') or {}).get('latest_command')}`",
            f"- Release gate check: `{(payload.get('verification') or {}).get('release_gate_check')}`",
            "",
        ]
    )


def write_inventory(
    project_root: Path,
    *,
    public_json: Path,
    public_markdown: Path,
    local_json: Path,
    generated_at: str | None = None,
) -> dict[str, Any]:
    public, private = collect_inventory(project_root, generated_at=generated_at)
    errors = validate_public_inventory_payload(public, project_root=project_root, max_age_hours=None)
    if errors:
        raise SystemExit("Public inventory validation failed before write: " + "; ".join(errors))
    public_json.parent.mkdir(parents=True, exist_ok=True)
    public_markdown.parent.mkdir(parents=True, exist_ok=True)
    local_json.parent.mkdir(parents=True, exist_ok=True)
    public_json.write_text(json.dumps(public, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    public_markdown.write_text(render_markdown(public), encoding="utf-8")
    local_json.write_text(json.dumps(private, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return {"public": public, "private": private}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Collect GT-KB development environment inventory.")
    parser.add_argument("--project-root", type=Path, default=Path(__file__).resolve().parent.parent)
    parser.add_argument("--public-json", type=Path, default=PUBLIC_JSON_RELATIVE_PATH)
    parser.add_argument("--public-markdown", type=Path, default=PUBLIC_MARKDOWN_RELATIVE_PATH)
    parser.add_argument("--local-json", type=Path, default=LOCAL_JSON_RELATIVE_PATH)
    parser.add_argument("--generated-at", default=None, help="Override generated_at for deterministic tests.")
    parser.add_argument(
        "--check-only", action="store_true", help="Validate the public inventory without writing files."
    )
    parser.add_argument("--max-age-hours", type=int, default=DEFAULT_MAX_AGE_HOURS)
    args = parser.parse_args(argv)

    project_root = args.project_root.resolve()
    public_json = args.public_json if args.public_json.is_absolute() else project_root / args.public_json
    public_markdown = (
        args.public_markdown if args.public_markdown.is_absolute() else project_root / args.public_markdown
    )
    local_json = args.local_json if args.local_json.is_absolute() else project_root / args.local_json

    if args.check_only:
        if not public_json.is_file():
            print(f"FAIL development environment inventory missing: {_relative(public_json, project_root)}")
            return 1
        payload = _read_json(public_json)
        errors = validate_public_inventory_payload(payload, project_root=project_root, max_age_hours=args.max_age_hours)
        if errors:
            print("FAIL development environment inventory invalid: " + "; ".join(errors))
            return 1
        print(f"PASS development environment inventory: {_relative(public_json, project_root)}")
        return 0

    result = write_inventory(
        project_root,
        public_json=public_json,
        public_markdown=public_markdown,
        local_json=local_json,
        generated_at=args.generated_at,
    )
    print(f"Wrote public JSON: {_relative(public_json, project_root)}")
    print(f"Wrote public Markdown: {_relative(public_markdown, project_root)}")
    print(f"Wrote local JSON: {_relative(local_json, project_root)}")
    print(f"Redaction status: {result['public']['redaction']['status']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
