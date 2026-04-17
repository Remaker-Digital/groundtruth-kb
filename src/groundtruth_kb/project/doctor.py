# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Workstation doctor — ``gt project doctor`` implementation (Layer 3)."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import UTC, datetime
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


_REQUIRED_BRIDGE_RULES = (
    "file-bridge-protocol.md",
    "bridge-essential.md",
    "deliberation-protocol.md",
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

    hook_file = target / ".claude" / "hooks" / "scanner-safe-writer.py"
    if not hook_file.exists():
        return ToolCheck(
            name="scanner-safe-writer",
            required=True,
            found=False,
            status="fail",
            message="scanner-safe-writer.py missing — run `gt project upgrade --apply`",
        )

    settings_path = target / ".claude" / "settings.json"
    registered = False
    if settings_path.exists():
        try:
            data: object = json.loads(settings_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            registered = False
        else:
            if isinstance(data, dict):
                raw_hooks = data.get("hooks")
                hooks_dict = raw_hooks if isinstance(raw_hooks, dict) else {}
                raw_pretooluse = hooks_dict.get("PreToolUse")
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
                        if isinstance(cmd, str) and "scanner-safe-writer.py" in cmd:
                            registered = True
                            break
                    if registered:
                        break

    gitignore = target / ".gitignore"
    log_ignored = False
    if gitignore.exists():
        try:
            gi_text = gitignore.read_text(encoding="utf-8")
            log_ignored = ".claude/hooks/*.log" in gi_text
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


def _check_file_bridge_setup(target: Path) -> ToolCheck:
    """Check file bridge configuration for dual-agent projects.

    Returns WARN when:
    - BRIDGE-INVENTORY.md or bridge-os-poller-setup-prompt.md are missing
    - bridge/INDEX.md is absent
    - Any of the 3 required bridge rule files are absent from .claude/rules/

    Returns pass only when bridge/INDEX.md exists AND all 3 required rule
    files are present.
    """
    inventory = target / "BRIDGE-INVENTORY.md"
    setup_prompt = target / "bridge-os-poller-setup-prompt.md"
    index = target / "bridge" / "INDEX.md"

    missing_setup = [path.name for path in (inventory, setup_prompt) if not path.exists()]
    if missing_setup:
        return ToolCheck(
            name="File Bridge Config",
            required=True,
            found=False,
            status="warning",
            message=f"Missing file bridge setup artifact(s): {', '.join(missing_setup)}",
        )

    if not index.exists():
        return ToolCheck(
            name="File Bridge Config",
            required=True,
            found=True,
            status="warning",
            message="bridge/INDEX.md not found — create it to enable the bridge workflow",
        )

    rules_dir = target / ".claude" / "rules"
    missing_rules = [r for r in _REQUIRED_BRIDGE_RULES if not (rules_dir / r).exists()]
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
        message="File bridge inventory, setup prompt, bridge/INDEX.md, and bridge rules present",
    )


# ── Bridge poller liveness ────────────────────────────────────────────

_BRIDGE_STATUS_PATHS = {
    "claude": Path("independent-progress-assessments/bridge-automation/logs/claude-scan-status.json"),
    "codex": Path("independent-progress-assessments/bridge-automation/logs/codex-scan-status.json"),
}

_BRIDGE_FRESH_SECS = 4 * 60  # < 4 min → OK
_BRIDGE_WARN_SECS = 10 * 60  # 4–10 min → WARN; > 10 min → ALARM
_BRIDGE_SCHEDULER_DOC = "docs/tutorials/bridge-os-scheduler.md"
_BRIDGE_AUTH_DOC = "docs/troubleshooting/auth.md"


def _check_bridge_poller(target: Path, agent: str) -> ToolCheck:
    """Check file bridge poller liveness for *agent* (``'claude'`` or ``'codex'``).

    Reads the JSON status file written by the OS-scheduler poller and
    computes staleness against the freshness thresholds:

    - ``< 4 min``  → OK
    - ``4–10 min`` → WARN
    - ``> 10 min`` → ALARM
    - File absent  → not started (WARN)
    - Missing / unparseable ``updatedAtUtc`` → ALARM
    """
    status_path = target / _BRIDGE_STATUS_PATHS[agent]
    check_name = f"{agent.title()} bridge poller"

    if not status_path.exists():
        return ToolCheck(
            name=check_name,
            required=False,
            found=False,
            status="warning",
            message=(
                f"{agent} bridge poller not started — see {_BRIDGE_SCHEDULER_DOC} to configure OS-scheduler pollers"
            ),
        )

    try:
        raw = status_path.read_text(encoding="utf-8")
        data: object = json.loads(raw)
    except (OSError, json.JSONDecodeError) as exc:
        return ToolCheck(
            name=check_name,
            required=False,
            found=True,
            status="fail",
            message=f"{agent} bridge status file unreadable: {exc}",
        )

    if not isinstance(data, dict):
        return ToolCheck(
            name=check_name,
            required=False,
            found=True,
            status="fail",
            message=f"{agent} bridge status file is not a JSON object",
        )

    updated_at_raw = data.get("updatedAtUtc")
    state_raw = data.get("state", "")
    state_display = str(state_raw) if state_raw else "unknown"

    if not isinstance(updated_at_raw, str) or not updated_at_raw.strip():
        return ToolCheck(
            name=check_name,
            required=False,
            found=True,
            status="fail",
            message=(f"{agent} bridge status file missing updatedAtUtc — ALARM. See {_BRIDGE_AUTH_DOC}"),
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
                f"{agent} bridge status file has unparseable updatedAtUtc "
                f"{updated_at_raw!r} — ALARM. See {_BRIDGE_AUTH_DOC}"
            ),
        )

    now = datetime.now(tz=UTC)
    age_secs = (now - updated_at).total_seconds()
    age_min = int(age_secs // 60)
    age_sec_part = int(age_secs % 60)
    age_display = f"{age_min}m {age_sec_part}s ago"

    if age_secs < _BRIDGE_FRESH_SECS:
        return ToolCheck(
            name=check_name,
            required=False,
            found=True,
            status="pass",
            message=f"{agent} bridge poller: OK (last scan {age_display}, state: {state_display})",
        )

    if age_secs < _BRIDGE_WARN_SECS:
        return ToolCheck(
            name=check_name,
            required=False,
            found=True,
            status="warning",
            message=(
                f"{agent} bridge poller: WARN (last scan {age_display}, state: {state_display}) "
                f"— investigate poller or see {_BRIDGE_SCHEDULER_DOC}"
            ),
        )

    return ToolCheck(
        name=check_name,
        required=False,
        found=True,
        status="fail",
        message=(
            f"{agent} bridge poller: ALARM (last scan {age_display}, state: {state_display}) "
            f"— check {_BRIDGE_AUTH_DOC} and {_BRIDGE_SCHEDULER_DOC}"
        ),
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
    checks.append(_check_hooks(target, profile))
    checks.append(_check_rules(target, profile))

    if p.includes_bridge:
        checks.append(_check_file_bridge_setup(target))
        checks.append(_check_settings_classifiers(target))
        checks.append(_check_scanner_safe_writer_drift(target, profile))
        checks.append(_check_bridge_poller(target, "claude"))
        checks.append(_check_bridge_poller(target, "codex"))

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
