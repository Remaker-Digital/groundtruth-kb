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

SCHEMA_VERSION = 2
COLLECTOR_VERSION = "gtkb-dev-environment-inventory-v2"
DEFAULT_MAX_AGE_HOURS = 336
PUBLIC_JSON_RELATIVE_PATH = Path(".groundtruth/inventory/dev-environment-inventory.json")
PUBLIC_MARKDOWN_RELATIVE_PATH = Path(".groundtruth/inventory/dev-environment-inventory.md")
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
# Required qualification coverage is independent of installation lifecycle.
# ADR-CROSS-HARNESS-PARITY-001 also requires discovery beyond these primaries.
PRIMARY_HARNESSES = ("claude", "codex", "goose")
CONTEXT_ROLES = ("prime-builder", "loyal-opposition")

CAPABILITY_DIMENSIONS = (
    "startup_support",
    "canonical_terminology_load",
    "native_context_binding",
    "native_bridge_delivery",
    "canonical_mutation_validation",
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
AZURE_CONNECTION_STRING_MARKER = "DefaultEndpoints" + "Protocol="
SENSITIVE_VALUE_RE = re.compile(
    r"(sk-[A-Za-z0-9_-]{10,}|gh[pousr]_[A-Za-z0-9_]{10,}|xox[baprs]-[A-Za-z0-9-]{10,}|"
    r"AKIA[0-9A-Z]{16}|-----BEGIN [A-Z ]*PRIVATE KEY-----|" + re.escape(AZURE_CONNECTION_STRING_MARKER) + r")",
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
    # Path-safe fallback (DELIB-2522 / Codex NO-GO -004 P1-002 fix): if the
    # unstructured first line contains an absolute local path the public
    # validator would later reject, return the sentinel rather than leaking
    # it through the public ``version`` field. This addresses tools whose
    # failure stderr embeds path-shaped diagnostic text (e.g., ``gh`` when
    # its config file is unreadable: ``open C:\Users\...``).
    if ABSOLUTE_PATH_RE.search(first_line):
        return fallback
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
            "evidence": display_command,
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
            "evidence": display_command,
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


class InventoryError(RuntimeError):
    """A content-free inventory refusal; no stale source is substituted."""


def _native_harness_records(project_root: Path) -> list[dict[str, Any]]:
    from groundtruth_kb.authority_client import AuthorityClient, AuthorityClientError
    from groundtruth_kb.config import GTConfig, GTConfigError

    try:
        config = GTConfig.load(config_path=project_root.resolve() / "groundtruth.toml", discover=False)
    except FileNotFoundError as error:
        raise InventoryError("native_authority_not_configured") from error
    except (OSError, GTConfigError, ValueError) as error:
        raise InventoryError("native_authority_configuration_invalid") from error
    if not config.authority_url:
        raise InventoryError("native_authority_not_configured")
    client = AuthorityClient(config.authority_url)
    records = []
    seen = set()
    after = None
    while True:
        try:
            page = client.request("GET", "/v1/harnesses", query={"after": after, "limit": 1000})
        except AuthorityClientError as error:
            raise InventoryError("native_harness_authority_unavailable") from error
        if not isinstance(page, dict) or not isinstance(page.get("records"), list) or "next_after" not in page:
            raise InventoryError("invalid_native_harness_response")
        for record in page["records"]:
            if (
                not isinstance(record, dict)
                or any(
                    not isinstance(record.get(key), str) or not record[key].strip()
                    for key in ("id", "harness_name", "harness_type", "status")
                )
                or not isinstance(record.get("version"), int)
                or isinstance(record["version"], bool)
            ):
                raise InventoryError("invalid_native_harness_response")
            if record["id"] in seen:
                raise InventoryError("duplicate_native_harness_identity")
            seen.add(record["id"])
            records.append(record)
        following = page["next_after"]
        if following is None:
            break
        if not page["records"] or following != page["records"][-1]["id"] or following == after:
            raise InventoryError("invalid_native_harness_pagination")
        after = following
    return records


def _harness_inventory(project_root: Path) -> dict[str, Any]:
    # Installation declarations never assert runtime capability or a role.
    # Do not read private harness configuration, invocation argv or environment.
    records = _native_harness_records(project_root)
    return {
        "identity_source": {
            "source": "native_authority/harnesses",
            "status": "observed",
            "coverage": "canonical_installation_records",
        },
        "installations": [
            {key: record[key] for key in ("id", "harness_name", "harness_type", "status", "version")}
            for record in sorted(records, key=lambda row: row["id"])
        ],
        "qualification": "unqualified",
        "discovery_limit": "Canonical installations only; unregistered surfaces and actual host behavior require independent qualification.",
    }


def _repo_surfaces(project_root: Path) -> dict[str, Any]:
    baseline = ".harness-baseline-configuration"
    workflows = sorted(
        set(
            _directory_entries(project_root, ".github/workflows", "*.yml")
            + _directory_entries(project_root, ".github/workflows", "*.yaml")
        )
    )

    def entries(relative: str, pattern: str) -> dict[str, Any]:
        items = _directory_entries(project_root, relative, pattern)
        return {
            "count": len(items),
            "items": items,
            "classification": "public_safe",
            "coverage": "authored_file_presence_only",
        }

    return {
        "rules": entries(baseline + "/rules", "*.md"),
        "skills": entries(".agents/skills", "*/SKILL.md"),
        "hooks": entries(baseline + "/hooks", "*.py"),
        "commands": entries(baseline + "/commands", "*.md"),
        "git_hooks": {"pre_commit": _file_state(project_root, ".githooks/pre-commit"), "classification": "public_safe"},
        "github_workflows": {"count": len(workflows), "items": workflows, "classification": "public_safe"},
        "mcp_config": _file_state(project_root, ".mcp.json", classification="local_only"),
    }


def _runtime_capabilities() -> dict[str, Any]:
    return {
        "repo_local_collector_limit": {
            "status": "unavailable",
            "classification": "unmeasured",
            "evidence": "This collector does not observe actual harness tool, plugin, hook or MCP invocation.",
            "recommended_source": "Controlled qualification on each actual host.",
        }
    }


def _matrix_targets(harnesses: dict[str, Any]) -> list[dict[str, Any]]:
    installations = harnesses.get("installations", [])
    targets = [{"harness_id": row["id"], "harness": row["harness_name"]} for row in installations]
    names = {row["harness_name"] for row in installations}
    targets.extend({"harness_id": None, "harness": name} for name in PRIMARY_HARNESSES if name not in names)
    return sorted(targets, key=lambda row: (row["harness"], row["harness_id"] or ""))


def _compatibility_matrix(harnesses: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        {
            **target,
            "role": role,
            "role_scope": "qualification_scenario_only",
            "qualification": "unqualified",
            "capabilities": {
                dimension: {"status": "unavailable", "evidence": "actual_host_behavior_not_measured"}
                for dimension in CAPABILITY_DIMENSIONS
            },
        }
        for target in _matrix_targets(harnesses)
        for role in CONTEXT_ROLES
    ]


def collect_inventory(project_root: Path, *, generated_at: str | None = None) -> tuple[dict[str, Any], dict[str, Any]]:
    project_root = project_root.resolve()
    generated = generated_at or _now_iso()
    harnesses = _harness_inventory(project_root)
    redaction_public, redaction_private = _redaction_summary()
    toolchain_public, toolchain_private = _toolchain_inventory()
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
        "role_by_harness_compatibility": _compatibility_matrix(harnesses),
        "redaction": redaction_public,
        "verification": {
            "latest_command": ("python scripts/collect_dev_environment_inventory.py"),
            "release_gate_check": "python scripts/release_candidate_gate.py --skip-python --skip-frontend",
            "status": "generated",
            "behavioral_qualification": "unqualified",
            "scope": "inventory_structure_freshness_and_privacy_only",
        },
    }
    private = {
        **public,
        "project_root": str(project_root),
        "toolchain": toolchain_private,
        "local_only": {
            **redaction_private,
            "mcp_config_present": (project_root / ".mcp.json").is_file(),
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
    for section in PUBLIC_REQUIRED_SECTIONS:
        expected = list if section == "role_by_harness_compatibility" else dict
        if section in payload and not isinstance(payload[section], expected):
            errors.append(f"{section} must be a {expected.__name__}")
    if errors:
        return errors
    age = inventory_age_hours(payload, now=now)
    if age is None:
        errors.append("generated_at is missing or invalid")
    elif max_age_hours is not None and age > max_age_hours:
        errors.append(f"inventory is stale: {age:.1f}h > {max_age_hours}h")
    if (payload.get("redaction") or {}).get("status") != "pass":
        errors.append("redaction.status must be pass")

    harnesses = payload.get("harnesses")
    installations = harnesses.get("installations") if isinstance(harnesses, dict) else None
    valid_installations = isinstance(installations, list) and all(
        isinstance(row, dict)
        and isinstance(row.get("id"), str)
        and bool(row["id"])
        and isinstance(row.get("harness_name"), str)
        and bool(row["harness_name"])
        and not (set(row) - {"id", "harness_name", "harness_type", "status", "version"})
        for row in installations
    )
    if not valid_installations:
        errors.append("harnesses.installations must contain current role-neutral metadata")
    elif len({row["id"] for row in installations}) != len(installations):
        errors.append("duplicate harness installation identity")
    if isinstance(harnesses, dict) and ("role_assignments" in harnesses or "role_assignment_source" in harnesses):
        errors.append("harness role assignments are forbidden")
    matrix = payload.get("role_by_harness_compatibility")
    if not isinstance(matrix, list):
        errors.append("role_by_harness_compatibility must be a list")
    elif valid_installations:
        expected = {
            (row["harness_id"], row["harness"], role) for row in _matrix_targets(harnesses) for role in CONTEXT_ROLES
        }
        seen = set()
        for row in matrix:
            if not isinstance(row, dict):
                errors.append("invalid qualification row")
                continue
            if (
                row.get("harness_id") is not None
                and not isinstance(row["harness_id"], str)
                or not isinstance(row.get("harness"), str)
                or not isinstance(row.get("role"), str)
            ):
                errors.append("invalid qualification target identity")
                continue
            key = (row.get("harness_id"), row.get("harness"), row.get("role"))
            if key in seen:
                errors.append("duplicate qualification row")
            seen.add(key)
            if "assignment" in row or row.get("role_scope") != "qualification_scenario_only":
                errors.append("qualification roles must not assign a harness role")
            if row.get("qualification") != "unqualified":
                errors.append("inventory cannot assert actual-host qualification")
            capabilities = row.get("capabilities")
            if not isinstance(capabilities, dict) or set(capabilities) != set(CAPABILITY_DIMENSIONS):
                errors.append("missing or invalid capability dimensions")
            elif any(
                not isinstance(cap, dict) or cap.get("status") != "unavailable" or not cap.get("evidence")
                for cap in capabilities.values()
            ):
                errors.append("inventory capabilities require unavailable status until actual-host measurement")
        if seen != expected:
            errors.append("qualification coverage must include every installation and required primary harness")
    if (payload.get("verification") or {}).get("behavioral_qualification") != "unqualified":
        errors.append("inventory structure does not establish behavioral qualification")

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
        f"| {row.get('harness')} | {row.get('harness_id') or 'not registered'} | {row.get('role')} | {row.get('qualification')} |"
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
            f"- Harness identity source: {harnesses.get('identity_source', {}).get('source')}",
            "- Roles below identify qualification scenarios, never harness assignments.",
            f"- Skills: {surfaces.get('skills', {}).get('count')}",
            f"- Authored baseline hooks: {surfaces.get('hooks', {}).get('count')}",
            f"- GitHub workflows: {surfaces.get('github_workflows', {}).get('count')}",
            f"- MCP config: {surfaces.get('mcp_config', {}).get('classification')} presence only",
            "",
            "## Required role scenarios by harness",
            "",
            "| Harness | Installation | Scenario role | Qualification |",
            "|---|---|---|---|",
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
    local_json: Path | None = None,
    generated_at: str | None = None,
) -> dict[str, Any]:
    targets = [public_json, public_markdown] + ([local_json] if local_json is not None else [])
    forbidden = {
        ".gtkb-state",
        "harness-state",
        ".agent",
        ".antigravity",
        ".api-harness",
        ".claude",
        ".codex",
        ".cursor",
        ".goose",
        ".harness-baseline-configuration",
    }
    resolved = [target.resolve() for target in targets]
    if len(set(resolved)) != len(resolved) or any(
        forbidden.intersection(part.lower() for part in target.parts) for target in resolved
    ):
        raise InventoryError("invalid_inventory_output_path")
    public, private = collect_inventory(project_root, generated_at=generated_at)
    errors = validate_public_inventory_payload(public, project_root=project_root, max_age_hours=None)
    if errors:
        raise SystemExit("Public inventory validation failed before write: " + "; ".join(errors))
    public_json.parent.mkdir(parents=True, exist_ok=True)
    public_markdown.parent.mkdir(parents=True, exist_ok=True)
    public_json.write_text(json.dumps(public, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    public_markdown.write_text(render_markdown(public), encoding="utf-8")
    if local_json is not None:
        local_json.parent.mkdir(parents=True, exist_ok=True)
        local_json.write_text(json.dumps(private, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return {"public": public, "private": private}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Collect GT-KB development environment inventory.")
    parser.add_argument("--project-root", type=Path, default=Path(__file__).resolve().parent.parent)
    parser.add_argument("--public-json", type=Path, default=PUBLIC_JSON_RELATIVE_PATH)
    parser.add_argument("--public-markdown", type=Path, default=PUBLIC_MARKDOWN_RELATIVE_PATH)
    parser.add_argument(
        "--local-json", type=Path, help="Optional explicit destination for redacted local details; omitted by default."
    )
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
    local_json = (
        (args.local_json if args.local_json.is_absolute() else project_root / args.local_json)
        if args.local_json
        else None
    )

    if args.check_only:
        if not public_json.is_file():
            print(f"FAIL development environment inventory missing: {_relative(public_json, project_root)}")
            return 1
        payload = _read_json(public_json)
        errors = validate_public_inventory_payload(payload, project_root=project_root, max_age_hours=args.max_age_hours)
        if errors:
            print("FAIL development environment inventory invalid: " + "; ".join(errors))
            return 1
        print(
            f"PASS inventory structure/freshness/privacy only: {_relative(public_json, project_root)}; behavioral qualification remains unqualified"
        )
        return 0

    try:
        result = write_inventory(
            project_root,
            public_json=public_json,
            public_markdown=public_markdown,
            local_json=local_json,
            generated_at=args.generated_at,
        )
    except InventoryError as error:
        print(f"FAIL development environment inventory: {error}")
        return 1
    print(f"Wrote public JSON: {_relative(public_json, project_root)}")
    print(f"Wrote public Markdown: {_relative(public_markdown, project_root)}")
    if local_json is not None:
        print(f"Wrote local JSON: {_relative(local_json, project_root)}")
    print(f"Redaction status: {result['public']['redaction']['status']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
