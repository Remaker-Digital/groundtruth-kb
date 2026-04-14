# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Workstation doctor — ``gt project doctor`` implementation (Layer 3)."""

from __future__ import annotations

import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

from groundtruth_kb.project.profiles import get_profile


@dataclass
class ToolCheck:
    """Result of checking a single tool or project file."""

    name: str
    required: bool
    found: bool
    version: str | None = None
    min_version: str | None = None
    status: Literal["pass", "fail", "warning"] = "pass"
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
    return _check_tool(
        "Claude Code",
        ["claude", "--version"],
        required=False,
        install_hint="npm install -g @anthropic-ai/claude-code",
        auto_installable=True,
    )


def _check_ruff() -> ToolCheck:
    return _check_tool(
        "ruff",
        ["ruff", "--version"],
        required=False,
        install_hint="pip install ruff",
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
    except Exception as e:
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
    except Exception as e:
        return ToolCheck(
            name="Knowledge DB",
            required=True,
            found=True,
            status="fail",
            message=f"DB error: {e}",
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
    required_hooks = {"assertion-check.py", "spec-classifier.py"}
    profile = get_profile(profile_name)
    if profile.includes_bridge:
        required_hooks.update({"destructive-gate.py", "credential-scan.py"})

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


def _check_settings_classifiers(target: Path) -> ToolCheck:
    """F5: Check classifier hook configuration in .claude/settings.local.json.

    Bridge-profile-only. Warns when:
      - settings file is missing
      - settings JSON is malformed
      - ``hooks`` key is not a dict
      - ``UserPromptSubmit`` hooks list is missing, null, or non-list
      - neither ``intake-classifier.py`` nor ``spec-classifier.py`` is active
      - both classifiers are active (redundant)
    """
    import json

    settings_path = target / ".claude" / "settings.local.json"
    if not settings_path.exists():
        return ToolCheck(
            name="Classifier settings",
            required=False,
            found=False,
            status="warning",
            message=".claude/settings.local.json not found; classifiers cannot be activated",
        )

    try:
        raw = settings_path.read_text(encoding="utf-8")
        data = json.loads(raw)
    except (OSError, json.JSONDecodeError) as exc:
        return ToolCheck(
            name="Classifier settings",
            required=False,
            found=True,
            status="warning",
            message=f"Malformed settings JSON: {exc}",
        )

    if not isinstance(data, dict):
        return ToolCheck(
            name="Classifier settings",
            required=False,
            found=True,
            status="warning",
            message="settings.local.json root must be a JSON object",
        )

    hooks = data.get("hooks")
    if hooks is None:
        return ToolCheck(
            name="Classifier settings",
            required=False,
            found=True,
            status="warning",
            message="settings.local.json has no 'hooks' section",
        )
    if not isinstance(hooks, dict):
        return ToolCheck(
            name="Classifier settings",
            required=False,
            found=True,
            status="warning",
            message=f"'hooks' must be a JSON object, got {type(hooks).__name__}",
        )

    ups = hooks.get("UserPromptSubmit")
    if ups is None or not isinstance(ups, list):
        return ToolCheck(
            name="Classifier settings",
            required=False,
            found=True,
            status="warning",
            message="'hooks.UserPromptSubmit' must be a non-null list",
        )

    active_hook_names: set[str] = set()
    for entry in ups:
        if not isinstance(entry, dict):
            continue
        cmd = entry.get("command", "") or ""
        if "intake-classifier.py" in cmd:
            active_hook_names.add("intake-classifier.py")
        if "spec-classifier.py" in cmd:
            active_hook_names.add("spec-classifier.py")

    has_intake = "intake-classifier.py" in active_hook_names
    has_spec = "spec-classifier.py" in active_hook_names

    if has_intake and has_spec:
        return ToolCheck(
            name="Classifier settings",
            required=False,
            found=True,
            status="warning",
            message="Both intake-classifier.py and spec-classifier.py are active (redundant)",
        )
    if not has_intake and not has_spec:
        return ToolCheck(
            name="Classifier settings",
            required=False,
            found=True,
            status="warning",
            message="Neither intake-classifier.py nor spec-classifier.py is active",
        )

    active = "intake-classifier.py" if has_intake else "spec-classifier.py"
    return ToolCheck(
        name="Classifier settings",
        required=False,
        found=True,
        status="pass",
        message=f"{active} is active",
    )


def _check_file_bridge_setup(target: Path) -> ToolCheck:
    """Check file bridge configuration capture for dual-agent projects."""
    inventory = target / "BRIDGE-INVENTORY.md"
    setup_prompt = target / "bridge-os-poller-setup-prompt.md"
    index = target / "bridge" / "INDEX.md"

    missing = [path.name for path in (inventory, setup_prompt) if not path.exists()]
    if missing:
        return ToolCheck(
            name="File Bridge Config",
            required=True,
            found=False,
            status="warning",
            message=f"Missing file bridge setup artifact(s): {', '.join(missing)}",
        )

    if index.exists():
        return ToolCheck(
            name="File Bridge Config",
            required=True,
            found=True,
            status="pass",
            message="File bridge inventory, setup prompt, and bridge/INDEX.md present",
        )

    return ToolCheck(
        name="File Bridge Config",
        required=True,
        found=True,
        status="pass",
        message="File bridge inventory and setup prompt present; create bridge/INDEX.md when enabling pollers",
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


# ── Main entry point ──────────────────────────────────────────────────


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
    checks.append(_check_ruff())
    checks.append(_check_gh_cli())

    if p.includes_bridge:
        checks.append(_check_claude_code())

    if p.includes_docker:
        checks.append(_check_docker())
        checks.append(_check_node())

    if p.includes_cloud:
        checks.append(_check_azure_cli())
        checks.append(_check_terraform())

    # Project-level checks
    checks.append(_check_groundtruth_toml(target))
    checks.append(_check_db_schema(target))
    checks.append(_check_hooks(target, profile))
    checks.append(_check_rules(target, profile))

    if p.includes_bridge:
        checks.append(_check_file_bridge_setup(target))
        checks.append(_check_settings_classifiers(target))

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

    status_icons = {"pass": "[OK]", "fail": "[FAIL]", "warning": "[WARN]"}

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
