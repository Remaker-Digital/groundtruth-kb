# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Workstation doctor — ``gt project doctor`` implementation (Layer 3)."""

from __future__ import annotations

import ast
import json
import os
import re
import shutil
import subprocess
import sys
from contextlib import suppress
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Literal

from groundtruth_kb import get_templates_dir
from groundtruth_kb.project.managed_registry import (
    FileArtifact,
    GitignorePattern,
    SettingsHookRegistration,
    artifacts_for_doctor,
    find_artifact_by_id,
)
from groundtruth_kb.project.profiles import get_profile

STANDING_BACKLOG_STALE_NO_GO_DAYS = 14
_BRIDGE_LATEST_STATUS_RE = re.compile(
    r"^(NEW|REVISED|GO|NO-GO|VERIFIED|WITHDRAWN|ADVISORY|DEFERRED):\s+(bridge/\S+\.md)\s*$"
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

        data = tomllib.loads(toml_path.read_text(encoding="utf-8"))
    except Exception:
        return "warning"
    doctor_config = data.get("doctor", {}) if isinstance(data, dict) else {}
    severity = str(doctor_config.get("orphan_citations", "")).strip().lower()
    return "fail" if severity == "fail" else "warning"


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


def _check_spec_classifier_canonical_path(target: Path) -> ToolCheck:
    """Verify spec-classifier.py exists at the DCL-mandated canonical path."""
    hook_path = target / ".claude" / "hooks" / "spec-classifier.py"
    return ToolCheck(
        name="spec-classifier hook canonical path",
        required=False,
        found=hook_path.exists(),
        status="pass" if hook_path.exists() else "warning",
        message=(
            f"spec-classifier.py present at {hook_path.relative_to(target)}"
            if hook_path.exists()
            else f"spec-classifier.py missing from canonical path {hook_path.relative_to(target)}"
        ),
    )


def _check_spec_classifier_settings_registered(target: Path) -> ToolCheck:
    """Verify spec-classifier.py is registered in tracked .claude/settings.json.

    Reads tracked settings (NOT settings.local.json) per Codex -004 F1.
    Tracked registration ensures the hook fires for fresh clones and shared
    harness contexts, not only on the current workstation.
    """
    import json as _json

    settings_path = target / ".claude" / "settings.json"
    if not settings_path.exists():
        return ToolCheck(
            name="spec-classifier tracked settings",
            required=False,
            found=False,
            status="warning",
            message=".claude/settings.json missing (tracked project settings)",
        )

    try:
        data = _json.loads(settings_path.read_text(encoding="utf-8"))
    except (OSError, _json.JSONDecodeError) as exc:
        return ToolCheck(
            name="spec-classifier tracked settings",
            required=False,
            found=True,
            status="warning",
            message=f"Malformed tracked settings JSON: {exc}",
        )

    ups = (data.get("hooks") or {}).get("UserPromptSubmit") or []
    for group in ups:
        if not isinstance(group, dict):
            continue
        for h in group.get("hooks", []):
            if isinstance(h, dict) and "spec-classifier.py" in (h.get("command") or ""):
                return ToolCheck(
                    name="spec-classifier tracked settings",
                    required=False,
                    found=True,
                    status="pass",
                    message="spec-classifier.py registered under UserPromptSubmit",
                )

    return ToolCheck(
        name="spec-classifier tracked settings",
        required=False,
        found=True,
        status="warning",
        message="spec-classifier.py NOT registered in tracked .claude/settings.json UserPromptSubmit",
    )


def _check_spec_classifier_codex_parity(target: Path) -> ToolCheck:
    """Verify spec-classifier.py is registered in .codex/hooks.json (forward-compatible parity).

    Per ADR-CODEX-HOOK-PARITY-FALLBACK-001 + Codex -006 F1: parity entry is
    forward-compatible intent (currently disabled on Windows; active when
    Codex hook parity becomes live).
    """
    import json as _json

    codex_path = target / ".codex" / "hooks.json"
    if not codex_path.exists():
        return ToolCheck(
            name="spec-classifier Codex parity",
            required=False,
            found=False,
            status="warning",
            message=".codex/hooks.json missing (Codex parity not configured)",
        )

    try:
        data = _json.loads(codex_path.read_text(encoding="utf-8"))
    except (OSError, _json.JSONDecodeError) as exc:
        return ToolCheck(
            name="spec-classifier Codex parity",
            required=False,
            found=True,
            status="warning",
            message=f"Malformed .codex/hooks.json: {exc}",
        )

    ups = (data.get("hooks") or {}).get("UserPromptSubmit") or []
    for group in ups:
        if not isinstance(group, dict):
            continue
        for h in group.get("hooks", []):
            if isinstance(h, dict) and "spec-classifier.py" in (h.get("command") or ""):
                return ToolCheck(
                    name="spec-classifier Codex parity",
                    required=False,
                    found=True,
                    status="pass",
                    message="spec-classifier.py parity entry present (forward-compatible)",
                )

    return ToolCheck(
        name="spec-classifier Codex parity",
        required=False,
        found=True,
        status="warning",
        message="spec-classifier.py NOT registered in .codex/hooks.json UserPromptSubmit",
    )


def _check_spec_classifier_test_exists(target: Path) -> ToolCheck:
    """Verify the canonical regression test for spec-classifier exists."""
    test_path = target / "groundtruth-kb" / "tests" / "test_spec_classifier_canonical_triggers.py"
    return ToolCheck(
        name="spec-classifier test module",
        required=False,
        found=test_path.exists(),
        status="pass" if test_path.exists() else "warning",
        message=(
            f"Test module present at {test_path.relative_to(target)}"
            if test_path.exists()
            else f"Test module missing at canonical path {test_path.relative_to(target)}"
        ),
    )


# Sub-slice F release-metric doctor invariants per umbrella -003.md:192-204.
# Enforces: GOV-REQUIREMENTS-COLLECTION-HOOK-001 v3 (AUQ-only invariant);
#           GOV-OWNER-DECISION-SURFACING-001;
#           GOV-FILE-BRIDGE-AUTHORITY-001 (Owner Decisions / Input section).
# See bridge/gtkb-gov-auq-enforcement-stack-slice-f-release-metrics-2026-05-04 for approved scope.

# Cutoff for rolling-window metrics: entries asked_at before this date are
# pre-enforcement-era and excluded from coverage calculations. Override via
# env var GTKB_AUQ_METRICS_CUTOFF_DATE (ISO date format).
_AUQ_METRICS_CUTOFF_DATE_DEFAULT = "2026-05-04"


def _parse_pending_decisions_file(path: Path) -> dict[str, list[dict[str, Any]]]:
    """Parse the pending-owner-decisions.md durable file via the canonical hook parser.

    Copies to a tempfile first so the hook's corruption-rename behavior on
    parse failure doesn't touch the live file. Per Sub-slice D pattern.
    """
    import importlib.util
    import shutil
    import sys
    import tempfile

    if not path.exists():
        return {"pending": [], "resolved": [], "history": []}

    hook_path = path.parents[1] / ".claude" / "hooks" / "owner-decision-tracker.py"
    if not hook_path.exists():
        return {"pending": [], "resolved": [], "history": []}

    spec = importlib.util.spec_from_file_location("owner_decision_tracker_doctor", hook_path)
    if not (spec and spec.loader):
        return {"pending": [], "resolved": [], "history": []}
    module = importlib.util.module_from_spec(spec)
    sys.modules["owner_decision_tracker_doctor"] = module
    spec.loader.exec_module(module)

    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False, encoding="utf-8") as tf:
        tmp_path = Path(tf.name)
    try:
        shutil.copy2(path, tmp_path)
        sections = module._read_pending_file(tmp_path)
        # Convert DecisionEntry objects to plain dicts for downstream simplicity.
        return {
            section: [
                {
                    "id": e.id,
                    "asked_at": e.asked_at,
                    "detected_via": getattr(e, "detected_via", ""),
                    "status": e.status,
                    "notes": getattr(e, "notes", ""),
                }
                for e in entries
            ]
            for section, entries in sections.items()
        }
    finally:
        with suppress(OSError):
            tmp_path.unlink(missing_ok=True)
        for sibling in tmp_path.parent.glob(tmp_path.name + ".corrupted-*"):
            with suppress(OSError):
                sibling.unlink()


def _check_untriaged_prose_decisions(target: Path) -> ToolCheck:
    """Count `prose:*` entries in ## Pending; FAIL if > 0.

    Per umbrella Sub-slice F item 1: untriaged prose-decision entries indicate
    surfacing-transparency violations (an owner-decision-ask was detected in
    agent prose but never converted to AskUserQuestion, leaving the candidate
    untriaged). Pre-Sub-slice-A historical entries should already have been
    cleaned via Sub-slice D's `--cleanup` mode; ## Pending should be empty.
    """
    pending_path = target / "memory" / "pending-owner-decisions.md"
    sections = _parse_pending_decisions_file(pending_path)
    pending = sections.get("pending", [])
    prose_entries = [e for e in pending if (e.get("detected_via") or "").startswith("prose:")]

    if not prose_entries:
        return ToolCheck(
            name="Untriaged prose decisions",
            required=False,
            found=True,
            status="pass",
            message=f"## Pending contains 0 prose:* entries (total pending: {len(pending)})",
        )

    sample_ids = [e["id"] for e in prose_entries[:5]]
    suffix = "..." if len(prose_entries) > 5 else ""
    return ToolCheck(
        name="Untriaged prose decisions",
        required=False,
        found=True,
        status="fail",
        message=f"## Pending has {len(prose_entries)} prose:* entries: {sample_ids}{suffix}",
    )


def _check_auq_coverage(target: Path) -> ToolCheck:
    """Percentage of recent owner decisions captured via detected_via=ask_user_question; FAIL if < 100%.

    Rolling window: entries with asked_at >= GTKB_AUQ_METRICS_CUTOFF_DATE
    (default 2026-05-04, the Sub-slice A -014 VERIFIED date which marked
    detector-tightening + AUQ-only enforcement going live). Pre-cutoff
    entries are excluded as historical; their classification reflected the
    pre-tightening detector, not current AUQ-only contract.
    """
    import os
    from datetime import datetime

    cutoff_str = os.environ.get("GTKB_AUQ_METRICS_CUTOFF_DATE", _AUQ_METRICS_CUTOFF_DATE_DEFAULT)
    try:
        cutoff = datetime.fromisoformat(cutoff_str).replace(tzinfo=UTC)
    except ValueError:
        return ToolCheck(
            name="AUQ coverage",
            required=False,
            found=True,
            status="warning",
            message=f"Invalid GTKB_AUQ_METRICS_CUTOFF_DATE: {cutoff_str!r}",
        )

    pending_path = target / "memory" / "pending-owner-decisions.md"
    sections = _parse_pending_decisions_file(pending_path)
    # Exclude ## History — entries explicitly archived there are accepted
    # residuals per the proposal's "document accepted residual via ## History
    # move" pattern. Active compliance is measured over Pending + Resolved only.
    active_entries = []
    for section_name in ("pending", "resolved"):
        active_entries.extend(sections.get(section_name, []))

    in_window = []
    for e in active_entries:
        asked = e.get("asked_at") or ""
        if not asked:
            continue
        try:
            asked_str = asked.replace("Z", "+00:00") if asked.endswith("Z") else asked
            dt = datetime.fromisoformat(asked_str)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=UTC)
        except (ValueError, TypeError):
            continue
        if dt >= cutoff:
            in_window.append(e)

    if not in_window:
        return ToolCheck(
            name="AUQ coverage",
            required=False,
            found=True,
            status="pass",
            message=f"No entries in window (cutoff={cutoff.date().isoformat()})",
        )

    auq = [e for e in in_window if e.get("detected_via") == "ask_user_question"]
    pct = (len(auq) / len(in_window)) * 100.0
    if len(auq) == len(in_window):
        return ToolCheck(
            name="AUQ coverage",
            required=False,
            found=True,
            status="pass",
            message=f"AUQ coverage 100% over {len(in_window)} entries since {cutoff.date().isoformat()}",
        )

    non_auq_ids = [e["id"] for e in in_window if e.get("detected_via") != "ask_user_question"][:5]
    return ToolCheck(
        name="AUQ coverage",
        required=False,
        found=True,
        status="fail",
        message=(
            f"AUQ coverage {pct:.1f}% ({len(auq)}/{len(in_window)}) since {cutoff.date().isoformat()}; "
            f"non-AUQ sample: {non_auq_ids}"
        ),
    )


def _check_uncited_owner_input_bridges(target: Path) -> ToolCheck:
    """Scan VERIFIED bridges; FAIL if any cite owner approval without an Owner Decisions / Input section.

    Reuses bridge-compliance-gate's helper functions (proposal_claims_owner_approval +
    has_concrete_owner_decisions_section) via importlib so the same logic
    that gates Write-time also gates release-time.

    Cutoff: only scans VERIFIED files dated on/after GTKB_AUQ_METRICS_CUTOFF_DATE
    (default 2026-05-04, Sub-slice C -006 VERIFIED date). Pre-cutoff VERIFIED
    bridges predate the Owner Decisions / Input requirement landing in the
    bridge-compliance-gate hook.
    """
    import importlib.util
    import os
    import re as _re
    import sys
    from datetime import datetime

    cutoff_str = os.environ.get("GTKB_AUQ_METRICS_CUTOFF_DATE", _AUQ_METRICS_CUTOFF_DATE_DEFAULT)
    try:
        cutoff = datetime.fromisoformat(cutoff_str).replace(tzinfo=UTC)
    except ValueError:
        return ToolCheck(
            name="Uncited owner-input bridges",
            required=False,
            found=True,
            status="warning",
            message=f"Invalid GTKB_AUQ_METRICS_CUTOFF_DATE: {cutoff_str!r}",
        )

    bridge_dir = target / "bridge"
    index_path = bridge_dir / "INDEX.md"
    if not index_path.exists():
        return ToolCheck(
            name="Uncited owner-input bridges",
            required=False,
            found=False,
            status="warning",
            message="bridge/INDEX.md not found",
        )

    gate_path = target / ".claude" / "hooks" / "bridge-compliance-gate.py"
    if not gate_path.exists():
        return ToolCheck(
            name="Uncited owner-input bridges",
            required=False,
            found=True,
            status="warning",
            message="bridge-compliance-gate.py not found; cannot reuse helpers",
        )
    spec = importlib.util.spec_from_file_location("bridge_gate_doctor", gate_path)
    if not (spec and spec.loader):
        return ToolCheck(
            name="Uncited owner-input bridges",
            required=False,
            found=True,
            status="warning",
            message="bridge-compliance-gate.py could not be loaded",
        )
    module = importlib.util.module_from_spec(spec)
    sys.modules["bridge_gate_doctor"] = module
    spec.loader.exec_module(module)

    # Per bridge protocol: a Document entry is a thread of versioned files,
    # newest at top. The `VERIFIED:` status line points to Codex's verdict
    # file; the actual Prime proposal/report carrying the Owner Decisions
    # obligation is on `NEW:` or `REVISED:` lines in the same entry. The
    # check must inspect the non-verdict files in each VERIFIED thread, not
    # only the verdict file. Per Codex -004 F1.
    threads: list[tuple[str, list[tuple[str, Path]]]] = []
    current_doc: str | None = None
    current_files: list[tuple[str, Path]] = []
    line_re = _re.compile(r"^(NEW|REVISED|GO|NO-GO|VERIFIED|ADVISORY|DEFERRED|WITHDRAWN):\s*(bridge/\S+\.md)\s*$")
    for line in index_path.read_text(encoding="utf-8").splitlines():
        s = line.strip()
        if s.startswith("Document:"):
            if current_doc and current_files:
                threads.append((current_doc, current_files))
            current_doc = s[len("Document:") :].strip()
            current_files = []
            continue
        m = line_re.match(s)
        if m and current_doc:
            current_files.append((m.group(1), target / m.group(2)))
    if current_doc and current_files:
        threads.append((current_doc, current_files))

    # Known historical offenders: bridge files filed before Sub-slice C's
    # bridge-compliance-gate began enforcing the Owner Decisions / Input
    # section requirement. Documented as accepted residuals per the umbrella's
    # "document accepted residual" treatment pattern. New offenders not in
    # this set fail the metric — the allowlist is sealed (no automatic growth).
    known_historical_offenders: set[str] = {
        # Sub-slice B's post-impl REPORT, filed before Sub-slice C VERIFIED
        # introduced the Owner Decisions section gate.
        "gtkb-gov-askuserquestion-enforcement-stack-slice-b-prime-rule-005.md",
        # ISOLATION-018 pending-migration-waiver REPORT, filed S330 prior to
        # the gate landing.
        "gtkb-isolation-018-pending-migration-waiver-005.md",
    }

    bridge_filename_date_re = _re.compile(r"(20\d{2}-\d{2}-\d{2})")
    bridge_content_date_re = _re.compile(r"^\*\*Date:\*\*\s*(20\d{2}-\d{2}-\d{2})(?:\b|[^\d])", _re.MULTILINE)

    def bridge_file_effective_datetime(path: Path, content: str | None) -> datetime | None:
        # Fresh CI checkouts rewrite filesystem mtimes, so prefer the stable
        # date embedded in most bridge filenames or bridge metadata before
        # falling back to mtime.
        filename_match = bridge_filename_date_re.search(path.name)
        if filename_match:
            try:
                return datetime.fromisoformat(filename_match.group(1)).replace(tzinfo=UTC)
            except ValueError:
                pass
        if content is not None:
            content_match = bridge_content_date_re.search(content)
            if content_match:
                try:
                    return datetime.fromisoformat(content_match.group(1)).replace(tzinfo=UTC)
                except ValueError:
                    pass
        try:
            return datetime.fromtimestamp(path.stat().st_mtime, tz=UTC)
        except OSError:
            return None

    offenders: list[str] = []
    for _doc_name, files in threads:
        # Latest status is the first listed file in the thread (insertion is at top).
        if not files or files[0][0] != "VERIFIED":
            continue
        # For VERIFIED threads, inspect every non-verdict file in the thread.
        # Verdict files start with GO/NO-GO/VERIFIED on first non-blank line;
        # mirrors bridge-compliance-gate.py:357 exclusion.
        for _status, vf in files:
            if not vf.exists():
                continue
            if vf.name in known_historical_offenders:
                continue
            try:
                content = vf.read_text(encoding="utf-8")
            except OSError:
                continue
            effective_datetime = bridge_file_effective_datetime(vf, content)
            if effective_datetime is None:
                continue
            if effective_datetime < cutoff:
                continue
            first_line = next((ln for ln in content.splitlines() if ln.strip()), "")
            if first_line.strip().startswith(("GO", "NO-GO", "VERIFIED")):
                continue
            try:
                claims_owner = module._proposal_claims_owner_approval(content)
                has_section = module._has_concrete_owner_decisions_section(content)
            except AttributeError:
                continue
            if claims_owner and not has_section:
                offenders.append(vf.name)

    if not offenders:
        return ToolCheck(
            name="Uncited owner-input bridges",
            required=False,
            found=True,
            status="pass",
            message=(
                f"No VERIFIED bridges since {cutoff.date().isoformat()} "
                f"claim owner approval without an Owner Decisions / Input section"
            ),
        )

    sample = offenders[:5]
    suffix = "..." if len(offenders) > 5 else ""
    return ToolCheck(
        name="Uncited owner-input bridges",
        required=False,
        found=True,
        status="fail",
        message=f"{len(offenders)} VERIFIED bridge(s) missing Owner Decisions section: {sample}{suffix}",
    )


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
            data: object = json.loads(settings_path.read_text(encoding="utf-8"))
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
            gi_text = gitignore.read_text(encoding="utf-8")
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
        data: object = json.loads(settings_path.read_text(encoding="utf-8"))
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


def _check_managed_artifact_drift(target: Path, profile_name: str) -> ToolCheck:
    """Aggregate doctor-required managed-artifact drift for an adopter project."""
    check_name = "Managed artifact drift"
    try:
        artifacts = artifacts_for_doctor(profile_name)
    except Exception as exc:  # pragma: no cover - defensive boundary around registry parser
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
                target_hash = _hash_file(target_path)
                template_hash = _hash_file(template_path)
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
                gitignore_text = gitignore.read_text(encoding="utf-8") if gitignore.is_file() else ""
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


def _check_skill_present(target: Path, profile_name: str) -> ToolCheck:
    """Check that the ``decision-capture`` skill files are present.

    Bridge-profile-only check. Warning-level (not fail) because a missing
    skill degrades workflow quality but does not render the project
    non-functional. Remediation: ``gt project upgrade --apply`` (the
    missing-file repair path is unconditional — works at any scaffold
    version).
    """
    profile = get_profile(profile_name)
    if not profile.includes_bridge:
        return ToolCheck(
            name="skill:decision-capture",
            required=False,
            found=True,
            status="pass",
            message="not applicable to base profile",
        )

    skill_md = target / ".claude" / "skills" / "decision-capture" / "SKILL.md"
    helper_py = target / ".claude" / "skills" / "decision-capture" / "helpers" / "record_decision.py"

    missing: list[str] = []
    if not skill_md.exists():
        missing.append("SKILL.md")
    if not helper_py.exists():
        missing.append("helpers/record_decision.py")

    if missing:
        return ToolCheck(
            name="skill:decision-capture",
            required=False,
            found=False,
            status="warning",
            message=(
                f".claude/skills/decision-capture/ missing: {', '.join(missing)}. "
                f"Run `gt project upgrade --apply` to restore."
            ),
        )

    return ToolCheck(
        name="skill:decision-capture",
        required=False,
        found=True,
        status="pass",
        message="decision-capture skill present",
    )


def _check_bridge_propose_skill_present(target: Path, profile_name: str) -> ToolCheck:
    """Check that the ``bridge-propose`` skill files are present.

    Bridge-profile-only check. Warning-level (not fail) because a
    missing skill degrades workflow quality but does not render the
    project non-functional. Remediation: ``gt project upgrade
    --apply`` (the missing-file repair path is unconditional — works
    at any scaffold version). Parallel in shape to
    :func:`_check_skill_present`.
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

    skill_md = target / ".claude" / "skills" / "bridge-propose" / "SKILL.md"
    helper_py = target / ".claude" / "skills" / "bridge-propose" / "helpers" / "write_bridge.py"

    missing: list[str] = []
    if not skill_md.exists():
        missing.append("SKILL.md")
    if not helper_py.exists():
        missing.append("helpers/write_bridge.py")

    if missing:
        return ToolCheck(
            name="skill:bridge-propose",
            required=False,
            found=False,
            status="warning",
            message=(
                f".claude/skills/bridge-propose/ missing: {', '.join(missing)}. "
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
    :func:`_check_skill_present` and
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

    skill_md = target / ".claude" / "skills" / "spec-intake" / "SKILL.md"
    helper_py = target / ".claude" / "skills" / "spec-intake" / "helpers" / "spec_intake.py"

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
                f".claude/skills/spec-intake/ missing: {', '.join(missing)}. "
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
            required=True,
            found=False,
            status="fail",
            message=".codex/skills missing; Codex skill adapters are not configured",
        )

    failures: list[str] = []
    checked = 0
    for skill_file in sorted(skills_root.glob("*/SKILL.md")):
        checked += 1
        rel_path = skill_file.relative_to(target).as_posix()
        try:
            text = skill_file.read_text(encoding="utf-8")
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
    (Codex GO at ``-006``): when the ``canonical_terms`` table exists in
    the project's MemBase, run parity check (markdown ↔ table) plus
    collision detection over current platform_core rows.

    Behavior:

    - Pass when the table is empty (Phase 1 backing registry hasn't been
      seeded yet — that's fine; the markdown remains the canonical source).
    - Pass when seeded and parity is clean and no collision findings exist.
    - Warning when parity has WARN findings (e.g., markdown term not seeded
      yet, content drift).
    - Fail when parity has ERROR findings (e.g., platform_core row in table
      but no markdown counterpart) or collision detection reports any
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

        terms = _ct.list_terms(conn, include_retired=False)
        if not terms:
            return ToolCheck(
                name="canonical terms registry",
                required=False,
                found=True,
                status="warning",
                message=(
                    "canonical_terms table present but empty while .claude/rules/canonical-terminology.md "
                    "defines platform_core terms — schema/seed drift; run `gt canonical-terms seed --apply`"
                ),
            )

        parity = _ct.parity_check(conn, glossary)
        errors_collisions, warnings_collisions = _ct.find_collisions(terms)

        parity_errors = [p for p in parity if p.severity == "error"]
        parity_warnings = [p for p in parity if p.severity == "warning"]

        if parity_errors or errors_collisions:
            details = []
            for p in parity_errors:
                details.append(f"parity:{p.kind}:{p.id}")
            for c in errors_collisions:
                details.append(f"collision:{c.classification}:{c.key[1]}")
            return ToolCheck(
                name="canonical terms registry",
                required=True,
                found=True,
                status="fail",
                message=(
                    f"canonical_terms registry blocking findings: {len(parity_errors)} parity error(s), "
                    f"{len(errors_collisions)} platform_core redefinition(s) — "
                    f"{'; '.join(details[:10])}"
                ),
            )

        if parity_warnings or warnings_collisions:
            details = []
            for p in parity_warnings:
                details.append(f"parity:{p.kind}:{p.id}")
            for c in warnings_collisions:
                details.append(f"collision:{c.classification}:{c.key[1]}")
            return ToolCheck(
                name="canonical terms registry",
                required=False,
                found=True,
                status="warning",
                message=(
                    f"canonical_terms registry advisory findings: {len(parity_warnings)} parity warn(s), "
                    f"{len(warnings_collisions)} cross-field/cross-scope collision(s) — "
                    f"{'; '.join(details[:10])}"
                ),
            )

        return ToolCheck(
            name="canonical terms registry",
            required=True,
            found=True,
            status="pass",
            message=(f"canonical_terms registry OK — {len(terms)} active terms, parity clean, no collisions"),
        )
    finally:
        conn.close()


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
        message="File bridge inventory, setup prompt, bridge/INDEX.md, and bridge rules present",
    )


# -- Bridge dispatch liveness ------------------------------------------
# Slice 4 (2026-05-09): the smart-poller mechanism was retired in favor of
# the cross-harness event-driven trigger. The dispatch-liveness check below
# is mechanism-agnostic — it reads recipients[role].updated_at from the
# shared dispatch-state.json regardless of which mechanism wrote it. The
# replacement-mechanism check is _check_cross_harness_trigger below.

_BRIDGE_DISPATCH_STATE_PATH = Path(".gtkb-state/bridge-poller/dispatch-state.json")
_BRIDGE_AGENT_TO_RECIPIENT = {"claude": "prime-builder", "codex": "loyal-opposition"}

_BRIDGE_FRESH_SECS = 4 * 60  # < 4 min → OK
_BRIDGE_WARN_SECS = 10 * 60  # 4–10 min → WARN; > 10 min → ALARM
_BRIDGE_DISPATCH_DOC = "docs/tutorials/dual-agent-setup.md"
_BRIDGE_AUTH_DOC = "docs/troubleshooting/auth.md"


def _check_bridge_dispatch_liveness(target: Path, agent: str) -> ToolCheck:
    """Check file bridge dispatch liveness for *agent* (``'claude'`` or ``'codex'``).

    Reads ``recipients[role].updated_at`` from the cross-harness trigger's
    ``dispatch-state.json`` and computes staleness against the freshness
    thresholds. The check is mechanism-agnostic — it surfaces dispatch
    freshness regardless of which mechanism updates the state file.

    - ``< 4 min``  → OK
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
            message=(
                f"{agent} bridge dispatch not started; see {_BRIDGE_DISPATCH_DOC} "
                "for cross-harness event-driven trigger setup"
            ),
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

    if age_secs < _BRIDGE_FRESH_SECS:
        return ToolCheck(
            name=check_name,
            required=False,
            found=True,
            status="pass",
            message=f"{agent} bridge dispatch: OK (last update {age_display}, state: {state_display})",
        )

    if age_secs < _BRIDGE_WARN_SECS:
        return ToolCheck(
            name=check_name,
            required=False,
            found=True,
            status="warning",
            message=(
                f"{agent} bridge dispatch: WARN (last update {age_display}, state: {state_display}) "
                f"— investigate cross-harness event-driven trigger or see {_BRIDGE_DISPATCH_DOC}"
            ),
        )

    return ToolCheck(
        name=check_name,
        required=False,
        found=True,
        status="fail",
        message=(
            f"{agent} bridge dispatch: ALARM (last update {age_display}, state: {state_display}) "
            f"— check {_BRIDGE_AUTH_DOC} and {_BRIDGE_DISPATCH_DOC}"
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


# ── DA harvest coverage ───────────────────────────────────────────────

# Coverage thresholds (hard-coded per implementation GO condition in
# bridge/gtkb-da-harvest-coverage-implementation-005.md).
DA_HARVEST_COVERAGE_WARN_THRESHOLD = 95.0
DA_HARVEST_COVERAGE_ERROR_THRESHOLD = 80.0


def _check_cross_harness_trigger(target: Path) -> ToolCheck:
    """Check cross-harness event-driven trigger surface (Slice 4 replacement).

    Per Slice 3 of bridge/gtkb-bridge-poller-event-driven-replacement-* the
    cross-harness trigger replaces the retired smart-poller. The trigger
    fires from PostToolUse + Stop hooks; this check verifies the trigger
    surface is wired up.

    Subchecks:
      1. ``scripts/cross_harness_bridge_trigger.py`` exists.
      2. ``.claude/settings.json`` registers the trigger in PostToolUse and
         Stop hook arrays (Codex parity in ``.codex/hooks.json`` is
         covered by ``scripts/check_codex_hook_parity.py``; the doctor
         reports the Claude side here).
      3. ``.gtkb-state/bridge-poller/dispatch-state.json`` exists or the
         trigger has not yet fired (steady-state warn, not fail).

    Status mapping:
      - All three subchecks pass → ``pass``
      - Trigger script missing → ``fail``
      - Hook registrations missing → ``fail``
      - Dispatch-state absent or trigger has not yet fired → ``warning``
    """
    check_name = "Cross-harness event-driven trigger"

    trigger_script = target / "scripts" / "cross_harness_bridge_trigger.py"
    if not trigger_script.is_file():
        return ToolCheck(
            name=check_name,
            required=False,
            found=False,
            status="fail",
            message=(
                f"cross-harness event-driven trigger script missing at "
                f"scripts/cross_harness_bridge_trigger.py — see {_BRIDGE_DISPATCH_DOC} "
                f"for installation"
            ),
        )

    settings_path = target / ".claude" / "settings.json"
    if not settings_path.is_file():
        return ToolCheck(
            name=check_name,
            required=False,
            found=True,
            status="fail",
            message=(
                f".claude/settings.json missing — bridge dispatch automation cannot "
                f"fire from PostToolUse + Stop hooks. See {_BRIDGE_DISPATCH_DOC}."
            ),
        )
    try:
        settings_text = settings_path.read_text(encoding="utf-8")
    except OSError as exc:
        return ToolCheck(
            name=check_name,
            required=False,
            found=True,
            status="fail",
            message=f".claude/settings.json unreadable: {exc}",
        )

    trigger_marker = "cross_harness_bridge_trigger.py"
    has_post_tool_use = "PostToolUse" in settings_text and trigger_marker in settings_text
    has_stop = "Stop" in settings_text and trigger_marker in settings_text
    if not (has_post_tool_use and has_stop):
        missing = []
        if not has_post_tool_use:
            missing.append("PostToolUse")
        if not has_stop:
            missing.append("Stop")
        return ToolCheck(
            name=check_name,
            required=False,
            found=True,
            status="fail",
            message=(
                f"cross-harness event-driven trigger not registered in {', '.join(missing)} "
                f"hook(s) in .claude/settings.json — bridge dispatch automation will not fire. "
                f"See {_BRIDGE_DISPATCH_DOC}."
            ),
        )

    state_path = target / _BRIDGE_DISPATCH_STATE_PATH
    if not state_path.exists():
        return ToolCheck(
            name=check_name,
            required=False,
            found=True,
            status="warning",
            message=(
                "cross-harness event-driven trigger registered but dispatch-state.json "
                "absent; trigger has not yet fired (steady state if no actionable bridge "
                "entries since installation)"
            ),
        )

    return ToolCheck(
        name=check_name,
        required=False,
        found=True,
        status="pass",
        message=(
            "cross-harness event-driven trigger active (script present; PostToolUse + Stop "
            "hooks registered; dispatch-state.json present)"
        ),
    )


_HARNESS_EXEC_SCAN_TARGETS = (
    Path("scripts") / "cross_harness_bridge_trigger.py",
    Path("scripts") / "verify_antigravity_dispatch.py",
)
_HARNESS_EXEC_INROOT_TOOLCHAIN = frozenset({"python", "python3"})
_HARNESS_EXEC_SUBPROCESS_METHODS = frozenset({"run", "Popen", "call", "check_output", "check_call"})


def _extract_literal_command(node: ast.Call) -> str | None:
    """Return the literal command name from a subprocess.* or shutil.which() call.

    Detects:
      - ``shutil.which(<literal>)``
      - ``subprocess.{run,Popen,call,check_output,check_call}(<literal>, ...)``
      - ``subprocess.{run,Popen,call,check_output,check_call}([<literal>, ...], ...)``

    Returns ``None`` for parametrized calls (the canonical safe pattern: command
    list built from the harness registry projection at runtime).
    """
    func = node.func
    if not isinstance(func, ast.Attribute) or not isinstance(func.value, ast.Name):
        return None
    if not node.args:
        return None
    module = func.value.id
    method = func.attr
    first = node.args[0]
    if module == "shutil" and method == "which":
        if isinstance(first, ast.Constant) and isinstance(first.value, str):
            return first.value
        return None
    if module == "subprocess" and method in _HARNESS_EXEC_SUBPROCESS_METHODS:
        if isinstance(first, ast.Constant) and isinstance(first.value, str):
            return first.value
        if isinstance(first, ast.List) and first.elts:
            head = first.elts[0]
            if isinstance(head, ast.Constant) and isinstance(head.value, str):
                return head.value
        return None
    return None


def _check_external_harness_exec_boundary(target: Path) -> ToolCheck:
    """Bound cross-harness exec resolution to registry-enumerated harness commands.

    Implements the deterministic bound for the External Harness Executable
    Resolution Exception in ``.claude/rules/project-root-boundary.md`` per
    ``DELIB-S366-ROOT-BOUNDARY-EXTERNAL-HARNESS-EXCEPTION`` and bridge
    ``gtkb-root-boundary-external-harness-exec-exception`` (GO at -006).

    Loads ``harness-state/harness-registry.json``; collects the set of
    ``invocation_surfaces.*.argv[0]`` command names. AST-scans
    ``scripts/cross_harness_bridge_trigger.py`` and
    ``scripts/verify_antigravity_dispatch.py`` for literal ``shutil.which`` /
    ``subprocess.{run,Popen,call,check_output,check_call}`` invocations.
    Classifies each literal command name against the allowed set, the
    in-root Python toolchain, and in-root absolute paths.

    Status:
      - ``pass``: every literal exec resolution targets a registry-enumerated
        harness command, an in-root Python interpreter, or an in-root absolute
        path; or no literal resolutions exist (the canonical pattern: parametrized
        command lists built from the registry projection).
      - ``warning``: the harness registry is missing or empty (exception is
        vacuous), or a scan-target surface is missing.
      - ``fail``: a literal subprocess/shutil.which call routes a non-harness
        command name out-of-root (violates the bound).
    """
    check_name = "External harness exec boundary"

    registry_path = target / "harness-state" / "harness-registry.json"
    if not registry_path.is_file():
        return ToolCheck(
            name=check_name,
            required=False,
            found=False,
            status="warning",
            message=(
                "harness-state/harness-registry.json missing; the External Harness "
                "Executable Resolution Exception cannot be enforced without an "
                "enumerated harness registry"
            ),
        )
    try:
        registry = json.loads(registry_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return ToolCheck(
            name=check_name,
            required=False,
            found=True,
            status="fail",
            message=f"harness-state/harness-registry.json unreadable: {exc}",
        )

    allowed_commands: set[str] = set()
    harnesses = registry.get("harnesses", []) if isinstance(registry, dict) else []
    if isinstance(harnesses, list):
        for h in harnesses:
            if not isinstance(h, dict):
                continue
            surfaces = h.get("invocation_surfaces", {})
            if not isinstance(surfaces, dict):
                continue
            for surface in surfaces.values():
                if not isinstance(surface, dict):
                    continue
                argv = surface.get("argv")
                if isinstance(argv, list) and argv and isinstance(argv[0], str):
                    allowed_commands.add(argv[0])

    if not allowed_commands:
        return ToolCheck(
            name=check_name,
            required=False,
            found=True,
            status="warning",
            message=(
                "harness registry enumerates no invocation_surfaces.*.argv[0] commands; "
                "the External Harness Executable Resolution Exception is vacuous and "
                "cross-harness dispatch has no allowed out-of-root targets"
            ),
        )

    scan_paths = [target / p for p in _HARNESS_EXEC_SCAN_TARGETS]
    missing = [p.relative_to(target).as_posix() for p in scan_paths if not p.is_file()]
    if missing:
        return ToolCheck(
            name=check_name,
            required=False,
            found=True,
            status="warning",
            message=(
                f"cross-harness exec resolution surface(s) missing: {', '.join(missing)}; "
                f"the External Harness Executable Resolution Exception bound cannot be "
                f"fully verified"
            ),
        )

    target_resolved = target.resolve()
    violations: list[str] = []
    for path in scan_paths:
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"))
        except (OSError, SyntaxError) as exc:
            return ToolCheck(
                name=check_name,
                required=False,
                found=True,
                status="fail",
                message=(f"could not parse {path.relative_to(target).as_posix()}: {exc}"),
            )
        rel = path.relative_to(target).as_posix()
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            literal_cmd = _extract_literal_command(node)
            if literal_cmd is None:
                continue
            if literal_cmd in allowed_commands:
                continue
            if literal_cmd in _HARNESS_EXEC_INROOT_TOOLCHAIN:
                continue
            try:
                cmd_path = Path(literal_cmd)
                if cmd_path.is_absolute():
                    cmd_resolved = cmd_path.resolve()
                    if str(cmd_resolved).startswith(str(target_resolved)):
                        continue
            except (OSError, ValueError):
                pass
            violations.append(f"{rel}: literal command {literal_cmd!r} (not a registry-enumerated harness command)")

    if violations:
        return ToolCheck(
            name=check_name,
            required=False,
            found=True,
            status="fail",
            message=(
                "non-harness out-of-root executable resolution detected in cross-harness "
                "surface(s); violates the External Harness Executable Resolution Exception "
                "bound (.claude/rules/project-root-boundary.md): " + "; ".join(violations)
            ),
        )

    return ToolCheck(
        name=check_name,
        required=False,
        found=True,
        status="pass",
        message=(
            f"cross-harness exec resolution bounded to registry-enumerated harness "
            f"commands ({len(allowed_commands)} enumerated: {sorted(allowed_commands)}); "
            f"no literal non-harness commands in scanned surface(s)"
        ),
    )


# Slice 7 of PROJECT-GTKB-INTERACTIVE-SESSION-ROLE-OVERRIDE
# (bridge/gtkb-interactive-session-role-override-slice-7-doctor-marker-checks-001.md,
# Codex GO at -002). The ephemeral session-state role marker is written by the
# UserPromptSubmit init-keyword path (Slice 2) and invalidated at SessionStart
# (Slice 3). These two read-only checks surface marker problems.
#
# The marker path and the session-id env fallback set are DUPLICATED here (with
# a parity test against scripts.session_role_resolution) rather than imported,
# to keep the packaged groundtruth_kb doctor's import surface out of the
# repo-root scripts/ tree (Codex Review Ask 2 confirmed).
_SESSION_ROLE_MARKER_NAME = "active-session-role.json"
_SESSION_ROLE_VALID_ROLES = frozenset({"prime-builder", "loyal-opposition"})
# MUST equal scripts.gtkb_session_id.MARKER_CONTINUITY_ORDER -- the single
# session-id membership authority that scripts.workstream_focus._SESSION_ID_ENV_FALLBACKS
# also delegates to (WI-4270 shared resolver unification). Kept as a verbatim
# copy here (NOT imported) so the packaged groundtruth_kb doctor's import surface
# stays out of the repo-root scripts/ tree (Codex Review Ask 2). Locked by the
# platform_tests/scripts/test_doctor_session_role_marker.py parity tests.
_SESSION_ID_ENV_FALLBACKS = (
    "GTKB_SESSION_ID",
    "CODEX_SESSION_ID",
    "CODEX_THREAD_ID",
    "CLAUDE_SESSION_ID",
    "CLAUDE_CODE_SESSION_ID",
)


def _session_role_marker_path(target: Path) -> Path:
    return target / ".claude" / "session" / _SESSION_ROLE_MARKER_NAME


def _read_session_role_marker(target: Path) -> tuple[dict | None, str | None]:
    """Return (marker_dict, error). error is set on unreadable/malformed/absent.

    (None, None) -> no marker file (a normal, non-warning state).
    (None, "<reason>") -> marker present but unreadable or not a JSON object.
    (dict, None) -> marker parsed.
    """
    marker_path = _session_role_marker_path(target)
    if not marker_path.is_file():
        return None, None
    try:
        body = json.loads(marker_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return None, f"unreadable or malformed JSON: {exc}"
    if not isinstance(body, dict):
        return None, "marker is not a JSON object"
    return body, None


def _session_role_marker_structurally_valid(body: dict) -> bool:
    """True iff a parsed marker satisfies DCL-SESSION-ROLE-RESOLUTION-001
    assertion 6 (non-empty string ``session_id``) AND assertion 7 (``role`` in
    the role set). The alignment check consults this so it defers to the
    validity check for ANY structural invalidity (no double-WARN), including an
    invalid role paired with a present-but-stale session id.
    """
    session_id = body.get("session_id")
    if not (isinstance(session_id, str) and session_id.strip()):
        return False
    return body.get("role") in _SESSION_ROLE_VALID_ROLES


def _resolve_env_session_id() -> str | None:
    """Best-effort current session id from the resolver's env fallback chain."""
    for env_name in _SESSION_ID_ENV_FALLBACKS:
        value = os.environ.get(env_name)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return None


def _check_session_role_marker_validity(target: Path) -> ToolCheck:
    """Structural validity of the ephemeral session-state role marker.

    DCL-SESSION-ROLE-RESOLUTION-001 assertion 6 (non-null session id) and
    assertion 7 (role in {prime-builder, loyal-opposition}). Read-only.
    """
    check_name = "Session-role marker validity"
    body, error = _read_session_role_marker(target)
    if body is None and error is None:
        return ToolCheck(
            name=check_name, required=False, found=False, status="pass", message="no active session-role marker"
        )
    if error is not None:
        return ToolCheck(
            name=check_name, required=False, found=True, status="warning", message=f"session-role marker {error}"
        )
    assert body is not None
    session_id = body.get("session_id")
    if not (isinstance(session_id, str) and session_id.strip()):
        return ToolCheck(
            name=check_name,
            required=False,
            found=True,
            status="warning",
            message="session-role marker missing or empty 'session_id' (DCL-SESSION-ROLE-RESOLUTION-001 assertion 6)",
        )
    role = body.get("role")
    if role not in _SESSION_ROLE_VALID_ROLES:
        return ToolCheck(
            name=check_name,
            required=False,
            found=True,
            status="warning",
            message=f"session-role marker 'role' {role!r} not in {{prime-builder, loyal-opposition}} (assertion 7)",
        )
    return ToolCheck(
        name=check_name, required=False, found=True, status="pass", message=f"valid session-role marker: role={role}"
    )


def _check_session_role_marker_session_id_alignment(target: Path) -> ToolCheck:
    """Best-effort staleness: marker session id vs the current session id.

    The doctor has no UserPromptSubmit payload session id, so 'current' is
    resolved best-effort from the resolver's env fallback set. INFO when no
    session-id env var is available (e.g. a manual CLI run outside a session).
    When the marker is structurally invalid, the validity check owns the
    warning and this check passes (no double-WARN). Read-only.
    """
    check_name = "Session-role marker session alignment"
    body, error = _read_session_role_marker(target)
    if body is None:
        # No marker, or invalid marker (validity check owns that warning).
        detail = "no marker to align" if error is None else "marker invalid (see validity check)"
        return ToolCheck(name=check_name, required=False, found=body is not None, status="pass", message=detail)
    if not _session_role_marker_structurally_valid(body):
        # Any structural invalidity (missing/empty session_id OR invalid role)
        # is owned by the validity check; alignment passes to avoid double-WARN.
        return ToolCheck(
            name=check_name, required=False, found=True, status="pass", message="marker invalid (see validity check)"
        )
    session_id = str(body.get("session_id")).strip()
    current = _resolve_env_session_id()
    if current is None:
        return ToolCheck(
            name=check_name,
            required=False,
            found=True,
            status="info",
            message="alignment indeterminate; no session-id env var set (run inside a session to check staleness)",
        )
    if session_id != current:
        return ToolCheck(
            name=check_name,
            required=False,
            found=True,
            status="warning",
            message=(
                f"stale session-role marker: session_id {session_id!r} != current {current!r}; "
                "SessionStart invalidation (Slice 3) may have failed"
            ),
        )
    return ToolCheck(
        name=check_name,
        required=False,
        found=True,
        status="pass",
        message="marker session id aligns with current session",
    )


def _check_role_set_topology_consistency(target: Path) -> ToolCheck:
    """Check role-set wire form, valid tokens, no duplicates, topology consistency.

    Per IP-6 of bridge/gtkb-single-harness-bridge-dispatcher-001-013.md (Codex
    GO at -014). WI-3342 IP-4 migrated this check from the legacy
    ``harness-state/role-assignments.json`` + ``harness-state/harness-identities.json``
    pair to the DB-backed registry projection
    (``harness-state/harness-registry.json``). Validates:

    - ``harness-state/harness-registry.json`` exists and parses as JSON.
    - Each harness record's ``role`` field is either a list (canonical wire
      form), a string (legacy scalar; READ-accepted), or absent.
    - Every list element is a token in ``{prime-builder, loyal-opposition,
      acting-prime-builder}`` (READ vocabulary; the legacy
      ``acting-prime-builder`` token is READ-accepted per the
      Compatibility/Provenance Classification).
    - No duplicates within a single record's role-set.
    - Identity/role topology consistency: in the projection, each harness
      record carries its ``id`` and ``role`` in a single unified row, so the
      pre-migration cross-check (every role-map ID must also appear in the
      identity map) is intrinsically satisfied — a record with a ``role`` and
      no ``id`` is the only residual drift case, and that is flagged here.
    """
    check_name = "Role-set topology consistency"
    # WI-3342 IP-4: resolve the registry projection path via the package
    # generator module. Function-local import keeps the doctor module's
    # top-level import surface unchanged.
    from groundtruth_kb.harness_projection import harness_registry_path

    registry_path = harness_registry_path(target)

    if not registry_path.is_file():
        return ToolCheck(
            name=check_name,
            required=False,
            found=False,
            status="warning",
            message=(
                "harness-state/harness-registry.json missing; doctor cannot validate "
                "role-set schema until the harness registry projection is generated."
            ),
        )

    try:
        registry_doc = json.loads(registry_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return ToolCheck(
            name=check_name,
            required=False,
            found=True,
            status="fail",
            message=f"harness-state/harness-registry.json unreadable: {exc}",
        )

    valid_read_tokens = frozenset({"prime-builder", "loyal-opposition", "acting-prime-builder"})
    harnesses = registry_doc.get("harnesses", []) if isinstance(registry_doc, dict) else []
    issues: list[str] = []
    legacy_scalar_count = 0
    list_form_count = 0

    if isinstance(harnesses, list):
        for record in harnesses:
            if not isinstance(record, dict):
                issues.append("harness registry record is not a JSON object")
                continue
            harness_id = record.get("id")
            harness_label = harness_id if isinstance(harness_id, str) and harness_id else "<unknown>"
            raw_role = record.get("role")
            if raw_role is None:
                # Missing role is permitted (bootstrap state); doctor flags via
                # the broader self-correction path, not here.
                continue
            if isinstance(raw_role, str):
                legacy_scalar_count += 1
                if raw_role.strip().lower() not in valid_read_tokens:
                    issues.append(
                        f"harness {harness_label!r}: legacy scalar role {raw_role!r} not in valid READ vocabulary"
                    )
            elif isinstance(raw_role, list):
                list_form_count += 1
                seen: set[str] = set()
                for token in raw_role:
                    if not isinstance(token, str):
                        issues.append(f"harness {harness_label!r}: role-set contains non-string token {token!r}")
                        continue
                    canonical = token.strip().lower()
                    if canonical not in valid_read_tokens:
                        issues.append(
                            f"harness {harness_label!r}: role-set contains unknown token "
                            f"{token!r} (valid: {sorted(valid_read_tokens)})"
                        )
                    if canonical in seen:
                        issues.append(f"harness {harness_label!r}: role-set contains duplicate token {token!r}")
                    seen.add(canonical)
            else:
                issues.append(
                    f"harness {harness_label!r}: role field has unsupported type "
                    f"{type(raw_role).__name__} (expected list or string)"
                )
            # Topology consistency: in the unified registry projection, identity
            # (``id``/``harness_name``) and role live in the same row, so the
            # pre-migration "role-map ID also in identity-map" cross-check is
            # intrinsically satisfied. The only residual drift is a row that
            # carries a role but no ``id``.
            if not (isinstance(harness_id, str) and harness_id):
                issues.append("harness registry record carries a role but no 'id' (identity/role topology drift)")
    else:
        issues.append("harness-registry.json 'harnesses' field is not a JSON list")

    if issues:
        return ToolCheck(
            name=check_name,
            required=False,
            found=True,
            status="fail",
            message="role-set topology issues: " + "; ".join(issues),
        )

    summary = (
        f"role-set wire form valid "
        f"({list_form_count} list-form, {legacy_scalar_count} legacy-scalar — "
        f"legacy will upgrade on next WRITE)"
    )
    return ToolCheck(
        name=check_name,
        required=False,
        found=True,
        status="pass",
        message=summary,
    )


def _check_single_harness_dispatcher_when_required(target: Path) -> ToolCheck:
    """When single-harness mode is applicable, verify the dispatcher is registered.

    Per IP-6 of bridge/gtkb-single-harness-bridge-dispatcher-001-013.md
    (Codex GO at -014). The check is applicability-gated:

    - Applicable iff exactly one harness identity has a multi-element role set
      (i.e., the active harness holds both ``prime-builder`` and
      ``loyal-opposition`` per ``ADR-SINGLE-HARNESS-OPERATING-MODE-001``).
    - When applicable: WARN if the Slice 2 dispatcher script + scheduled task
      are not yet installed (Slice 2 is a separate bridge thread; this check is
      forward-compatible).
    - When NOT applicable (the common multi-harness case): PASS with "not
      applicable".
    """
    check_name = "Single-harness dispatcher when required"
    # WI-3342 IP-4: single-harness applicability is determined from the
    # DB-backed registry projection (harness-state/harness-registry.json),
    # migrated from the legacy harness-state/role-assignments.json.
    from groundtruth_kb.harness_projection import harness_registry_path

    registry_path = harness_registry_path(target)

    if not registry_path.is_file():
        return ToolCheck(
            name=check_name,
            required=False,
            found=False,
            status="warning",
            message=(
                "harness-state/harness-registry.json missing; single-harness "
                "dispatcher applicability cannot be determined"
            ),
        )

    try:
        registry_doc = json.loads(registry_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return ToolCheck(
            name=check_name,
            required=False,
            found=True,
            status="fail",
            message=f"harness-state/harness-registry.json unreadable: {exc}",
        )

    multi_role_harnesses: list[str] = []
    harnesses = registry_doc.get("harnesses", []) if isinstance(registry_doc, dict) else []
    if isinstance(harnesses, list):
        for record in harnesses:
            if not isinstance(record, dict):
                continue
            harness_id = record.get("id")
            raw_role = record.get("role")
            if isinstance(raw_role, list):
                canonical = {str(t).strip().lower() for t in raw_role if isinstance(t, str)}
                if len(canonical) >= 2 and "prime-builder" in canonical and "loyal-opposition" in canonical:
                    multi_role_harnesses.append(str(harness_id))

    if not multi_role_harnesses:
        return ToolCheck(
            name=check_name,
            required=False,
            found=True,
            status="pass",
            message=(
                "single-harness dispatcher not applicable "
                "(no harness holds multi-element role set; multi-harness topology)"
            ),
        )

    # Applicable: check dispatcher script AND scheduled-task registration.
    # Per IP-4 of bridge/gtkb-single-harness-bridge-dispatcher-slice-2-005.md
    # (Codex GO at -006) and DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001
    # § Doctor Check: severity is WARN (not FAIL) for any "applicable but
    # not fully healthy" case; PASS only for "applicable + script + task
    # registered + last-run-time fresh". On non-Windows hosts: WARN with
    # platform-extension pointer (Slice 2 ships Windows-only).
    dispatcher_script = target / "scripts" / "single_harness_bridge_dispatcher.py"
    if not dispatcher_script.is_file():
        return ToolCheck(
            name=check_name,
            required=False,
            found=True,
            status="warning",
            message=(
                f"single-harness mode applicable (harness(es) {multi_role_harnesses} hold multi-element "
                f"role sets) but scripts/single_harness_bridge_dispatcher.py is absent. "
                f"Bridge dispatch in single-harness mode operates via manual-trigger fallback "
                f"until the dispatcher script is installed."
            ),
        )

    # Non-Windows host: Slice 2 ships Windows-only.
    if sys.platform != "win32":
        return ToolCheck(
            name=check_name,
            required=False,
            found=True,
            status="warning",
            message=(
                f"single-harness mode applicable (harness(es) {multi_role_harnesses}) and dispatcher "
                f"script present, but the Windows scheduled-task registration check is "
                f"Windows-only. macOS/Linux installers are DECISION DEFERRED to a future Slice "
                f"per DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001 § Platform Bindings."
            ),
        )

    # Windows host: probe Get-ScheduledTask for the canonical task name.
    task_name = "GTKB-SingleHarnessBridgeDispatcher"
    try:
        completed = subprocess.run(
            [
                "powershell.exe",
                "-NoProfile",
                "-Command",
                (
                    f"$t = Get-ScheduledTask -TaskName '{task_name}' "
                    f"-ErrorAction SilentlyContinue; "
                    f"if ($t) {{ "
                    f"$info = Get-ScheduledTaskInfo -TaskName '{task_name}' "
                    f"-ErrorAction SilentlyContinue; "
                    f"$lr = if ($info -and $info.LastRunTime) "
                    f"{{ $info.LastRunTime.ToString('o') }} else {{ '' }}; "
                    f'Write-Output "REGISTERED|$lr" '
                    f"}} else {{ Write-Output 'NOT_REGISTERED' }}"
                ),
            ],
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
    except (subprocess.SubprocessError, OSError, subprocess.TimeoutExpired) as exc:
        return ToolCheck(
            name=check_name,
            required=False,
            found=True,
            status="warning",
            message=(
                f"single-harness mode applicable (harness(es) {multi_role_harnesses}) and dispatcher "
                f"script present, but Get-ScheduledTask probe failed: {exc}. Task registration "
                f"state unknown."
            ),
        )

    output = (completed.stdout or "").strip()
    if output.startswith("NOT_REGISTERED"):
        return ToolCheck(
            name=check_name,
            required=False,
            found=True,
            status="warning",
            message=(
                f"single-harness mode applicable (harness(es) {multi_role_harnesses}) and dispatcher "
                f"script present at scripts/single_harness_bridge_dispatcher.py, but Windows scheduled "
                f"task '{task_name}' is not registered. Run "
                f"scripts/install_single_harness_dispatcher_task.ps1 -ProjectRoot <project-root> "
                f"to register it. Bridge dispatch in single-harness mode operates via manual-trigger "
                f"fallback until the task is registered."
            ),
        )

    if output.startswith("REGISTERED"):
        # Parse last-run time; warn if stale beyond interval + sanity TTL.
        last_run = output.split("|", 1)[1] if "|" in output else ""
        try:
            sanity_ttl = int(os.environ.get("GTKB_ACTIVE_SESSION_SANITY_TTL_SECONDS", "120"))
        except (TypeError, ValueError):
            sanity_ttl = 120
        # Default Slice 2 interval is 5 minutes (300s); stale threshold =
        # interval + sanity_ttl.
        stale_threshold_seconds = 300 + sanity_ttl
        if not last_run:
            return ToolCheck(
                name=check_name,
                required=False,
                found=True,
                status="warning",
                message=(
                    f"single-harness dispatcher task '{task_name}' is registered but has no "
                    f"recorded last-run time yet (newly registered or never fired). "
                    f"Harness(es): {multi_role_harnesses}."
                ),
            )
        try:
            last_run_dt = datetime.fromisoformat(last_run.replace("Z", "+00:00"))
            if last_run_dt.tzinfo is None:
                last_run_dt = last_run_dt.replace(tzinfo=UTC)
            age_seconds = (datetime.now(UTC) - last_run_dt).total_seconds()
        except (ValueError, OSError):
            age_seconds = stale_threshold_seconds + 1

        if age_seconds > stale_threshold_seconds:
            return ToolCheck(
                name=check_name,
                required=False,
                found=True,
                status="warning",
                message=(
                    f"single-harness dispatcher task '{task_name}' is registered but last "
                    f"ran {int(age_seconds)}s ago (threshold {stale_threshold_seconds}s = "
                    f"interval 300s + sanity TTL {sanity_ttl}s). Task may be disabled or "
                    f"failing silently; check Task Scheduler history."
                ),
            )

        return ToolCheck(
            name=check_name,
            required=False,
            found=True,
            status="pass",
            message=(
                f"single-harness dispatcher healthy: task '{task_name}' registered; "
                f"last_run={last_run}; harness(es): {multi_role_harnesses}."
            ),
        )

    # Unrecognized probe output.
    return ToolCheck(
        name=check_name,
        required=False,
        found=True,
        status="warning",
        message=(
            f"single-harness mode applicable but Get-ScheduledTask probe returned unrecognized "
            f"output: {output[:200]!r}. Task registration state unknown."
        ),
    )


def _check_da_harvest_coverage(target: Path) -> ToolCheck:
    """Check DA bridge-thread coverage for active VERIFIED threads.

    Uses the shared helper at ``groundtruth_kb.reporting.harvest_coverage``.
    Status mapping:

    - coverage_pct ``>=`` ``WARN_THRESHOLD`` (95.0)  → pass
    - coverage_pct ``>=`` ``ERROR_THRESHOLD`` (80.0) → warning
    - coverage_pct ``<``  ``ERROR_THRESHOLD``        → fail

    Missing DB or missing INDEX is treated as a skipped (warning) check
    rather than a hard fail — this keeps fresh scaffolds green until the
    consumer project wires its bridge.
    """
    index_path = target / "bridge" / "INDEX.md"
    db_path = target / "groundtruth.db"

    if not index_path.exists() or not db_path.exists():
        return ToolCheck(
            name="DA harvest coverage",
            required=False,
            found=False,
            status="warning",
            message="DA harvest coverage: skipped (bridge/INDEX.md or groundtruth.db missing)",
        )

    try:
        from groundtruth_kb.db import KnowledgeDB
        from groundtruth_kb.reporting.harvest_coverage import (
            compute_active_bridge_thread_coverage,
        )

        db = KnowledgeDB(str(db_path))
        metrics = compute_active_bridge_thread_coverage(index_path, db)
    except Exception as exc:  # intentional-catch: validation tool, error -> fail status
        return ToolCheck(
            name="DA harvest coverage",
            required=False,
            found=True,
            status="fail",
            message=f"DA harvest coverage: error computing metrics: {exc}",
        )

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


def _latest_bridge_status_entries(index_text: str) -> list[dict[str, str]]:
    """Return the top status row for each bridge document in INDEX order."""

    entries: list[dict[str, str]] = []
    current_document: str | None = None
    for raw_line in index_text.splitlines():
        line = raw_line.strip()
        if line.startswith("Document: "):
            current_document = line.removeprefix("Document: ").strip()
            continue
        if current_document is None:
            continue
        match = _BRIDGE_LATEST_STATUS_RE.match(line)
        if not match:
            continue
        entries.append(
            {
                "document": current_document,
                "status": match.group(1),
                "path": match.group(2),
            }
        )
        current_document = None
    return entries


def _bridge_file_date(path: Path) -> datetime | None:
    if not path.is_file():
        return None
    try:
        for line in path.read_text(encoding="utf-8", errors="replace").splitlines()[:80]:
            match = _BRIDGE_DATE_RE.match(line.strip())
            if match:
                return datetime.fromisoformat(match.group(1)).replace(tzinfo=UTC)
    except OSError:
        return None
    return None


def _active_authorized_work_item_ids(db: Any) -> set[str]:
    authorized: set[str] = set()
    for authorization in db.list_project_authorizations(status="active"):
        raw_ids = (
            authorization.get("included_work_item_ids_parsed")
            or authorization.get("_included_work_item_ids_parsed")
            or []
        )
        if not isinstance(raw_ids, list):
            continue
        authorized.update(str(item_id) for item_id in raw_ids if str(item_id).strip())
    return authorized


def check_standing_backlog_health(
    target: Path,
    *,
    stale_no_go_days: int = STANDING_BACKLOG_STALE_NO_GO_DAYS,
    now: datetime | None = None,
) -> dict[str, Any]:
    """Return a machine-readable standing-backlog health payload.

    Findings use the severity taxonomy required by GTKB-GOV-010:
    orphaned-WI=WARN, stale-NO-GO=WARN, missing-evidence=FAIL.
    """

    from groundtruth_kb.db import KnowledgeDB

    target = target.resolve()
    now = now or datetime.now(UTC)
    findings: list[dict[str, Any]] = []

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
                if item_id and item_id not in authorized_work_item_ids:
                    findings.append(
                        {
                            "kind": "orphaned-WI",
                            "severity": "WARN",
                            "work_item_id": item_id,
                            "project_name": item.get("project_name"),
                            "resolution_status": item.get("resolution_status"),
                            "message": (
                                f"Open work item {item_id} is not listed in any active "
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

    index_path = target / "bridge" / "INDEX.md"
    if not index_path.is_file():
        findings.append(
            {
                "kind": "missing-evidence",
                "severity": "FAIL",
                "message": "bridge/INDEX.md is missing; cannot evaluate stale NO-GO bridge entries.",
                "path": "bridge/INDEX.md",
            }
        )
    else:
        try:
            entries = _latest_bridge_status_entries(index_path.read_text(encoding="utf-8"))
            for entry in entries:
                if entry["status"] != "NO-GO":
                    continue
                bridge_file = target / entry["path"]
                decided_at = _bridge_file_date(bridge_file)
                if decided_at is None:
                    findings.append(
                        {
                            "kind": "missing-evidence",
                            "severity": "FAIL",
                            "document": entry["document"],
                            "path": entry["path"],
                            "message": f"Latest NO-GO file {entry['path']} has no parseable Date line.",
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
                    "path": "bridge/INDEX.md",
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
            "stale_no_go_count": sum(1 for finding in findings if finding["kind"] == "stale-NO-GO"),
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
    checks.append(_check_canonical_terminology(target, profile))
    checks.append(_check_canonical_terms_registry(target))

    if p.includes_bridge:
        checks.append(_check_file_bridge_setup(target))
        checks.append(_check_settings_classifiers(target))
        checks.append(_check_active_legacy_root_references(target))
        checks.append(_check_spec_classifier_canonical_path(target))
        checks.append(_check_spec_classifier_settings_registered(target))
        checks.append(_check_spec_classifier_codex_parity(target))
        checks.append(_check_spec_classifier_test_exists(target))
        checks.append(_check_untriaged_prose_decisions(target))
        checks.append(_check_auq_coverage(target))
        checks.append(_check_uncited_owner_input_bridges(target))
        checks.append(_check_scanner_safe_writer_drift(target, profile))
        checks.append(_check_skill_present(target, profile))
        checks.append(_check_bridge_propose_skill_present(target, profile))
        checks.append(_check_spec_intake_skill_present(target, profile))
        checks.append(_check_codex_skill_load_health(target))
        checks.append(_check_managed_artifact_drift(target, profile))
        for registration in artifacts_for_doctor(profile, class_="settings-hook-registration"):
            if isinstance(registration, SettingsHookRegistration):
                checks.append(_check_settings_hook_registration_drift(target, profile, registration))
        checks.append(_check_bridge_dispatch_liveness(target, "claude"))
        checks.append(_check_bridge_dispatch_liveness(target, "codex"))
        checks.append(_check_cross_harness_trigger(target))
        checks.append(_check_external_harness_exec_boundary(target))
        # IP-6 of bridge/gtkb-single-harness-bridge-dispatcher-001-013.md
        # (Codex GO at -014): role-set schema validation + single-harness
        # dispatcher applicability check.
        checks.append(_check_role_set_topology_consistency(target))
        # Slice 7 of PROJECT-GTKB-INTERACTIVE-SESSION-ROLE-OVERRIDE: read-only
        # session-state role marker diagnostics (validity + best-effort staleness).
        checks.append(_check_session_role_marker_validity(target))
        checks.append(_check_session_role_marker_session_id_alignment(target))
        checks.append(_check_single_harness_dispatcher_when_required(target))
        checks.append(_check_da_harvest_coverage(target))
        checks.append(_check_standing_backlog_health(target))
        checks.append(_check_orphan_citations(target))

    # Isolation checks per Phase 9 §4 (GTKB-ISOLATION-017 Slice 1).
    # Local import avoids a circular dependency: doctor_isolation imports
    # ToolCheck from this module.
    from groundtruth_kb.project.doctor_isolation import run_isolation_checks

    _PRODUCT_ROOT = Path(__file__).resolve().parents[3]
    checks.extend(run_isolation_checks(target, profile, product_root=_PRODUCT_ROOT))

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
