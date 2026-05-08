# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Workstation doctor — ``gt project doctor`` implementation (Layer 3)."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import time
from contextlib import suppress
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Literal

from groundtruth_kb.project.managed_registry import (
    FileArtifact,
    GitignorePattern,
    SettingsHookRegistration,
    artifacts_for_doctor,
    find_artifact_by_id,
)
from groundtruth_kb.project.profiles import get_profile


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
    line_re = _re.compile(r"^(NEW|REVISED|GO|NO-GO|VERIFIED):\s*(bridge/\S+\.md)\s*$")
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
                status="pass",
                message=("canonical_terms table present but empty — run gt canonical-terms seed --apply"),
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


# -- Bridge smart-poller liveness --------------------------------------

_BRIDGE_DISPATCH_STATE_PATH = Path(".gtkb-state/bridge-poller/dispatch-state.json")
_BRIDGE_AGENT_TO_RECIPIENT = {"claude": "prime", "codex": "codex"}

_BRIDGE_FRESH_SECS = 4 * 60  # < 4 min → OK
_BRIDGE_WARN_SECS = 10 * 60  # 4–10 min → WARN; > 10 min → ALARM
_BRIDGE_SCHEDULER_DOC = "docs/tutorials/bridge-smart-poller.md"
_BRIDGE_AUTH_DOC = "docs/troubleshooting/auth.md"

# Smart-poller activation paths per
# bridge/gtkb-bridge-poller-notify-activation-2026-04-29-004.md GO (REVISED-1
# at -003 §5). The doctor check verifies the activation chain end-to-end:
# runner present, wrapper present, wrapper resolves runner, state dir
# writable, task registered, task target = wrapper, task running, recent
# audit event, fresh notification.
_SMART_POLLER_TASK_NAME = "GTKB-SmartBridgePoller"
_SMART_POLLER_WRAPPER_REL = Path("scripts/run_smart_bridge_poller.ps1")
_SMART_POLLER_VBS_REL = Path("scripts/run_smart_bridge_poller.vbs")
_SMART_POLLER_RUNNER_REL = Path("groundtruth-kb/scripts/bridge_poller_runner.py")
# Phase 2 will move the runner to scripts/bridge_poller_runner.py — the
# wrapper internals will change in the same controlled surface; this check
# uses the wrapper's current $runnerPath line for verification.
_SMART_POLLER_STATE_REL = Path(".gtkb-state/bridge-poller")
_SMART_POLLER_AUDIT_REL = _SMART_POLLER_STATE_REL / "poller-runs"
_SMART_POLLER_NOTIFY_REL = _SMART_POLLER_STATE_REL / "notifications"
_SMART_POLLER_FRESH_SECS = 60


def _check_bridge_poller(target: Path, agent: str) -> ToolCheck:
    """Check file bridge smart-poller liveness for *agent* (``'claude'`` or ``'codex'``).

    Reads ``recipients[role].updated_at`` from the smart-poller's
    ``dispatch-state.json`` and computes staleness against the freshness
    thresholds:

    - ``< 4 min``  → OK
    - ``4–10 min`` → WARN
    - ``> 10 min`` → ALARM
    - File absent  → not started (WARN)
    - Missing / unparseable ``recipients[role].updated_at`` → ALARM
    """
    state_path = target / _BRIDGE_DISPATCH_STATE_PATH
    role = _BRIDGE_AGENT_TO_RECIPIENT.get(agent, agent)
    check_name = f"{agent.title()} bridge poller"

    if not state_path.exists():
        return ToolCheck(
            name=check_name,
            required=False,
            found=False,
            status="warning",
            message=(
                f"{agent} bridge poller not started; see {_BRIDGE_SCHEDULER_DOC} to configure the verified smart poller"
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


# ── DA harvest coverage ───────────────────────────────────────────────

# Coverage thresholds (hard-coded per implementation GO condition in
# bridge/gtkb-da-harvest-coverage-implementation-005.md).
DA_HARVEST_COVERAGE_WARN_THRESHOLD = 95.0
DA_HARVEST_COVERAGE_ERROR_THRESHOLD = 80.0


def _recent_audit_run_ids(target: Path, *, tail_count: int = 6) -> set[str]:
    """Parse the last `tail_count` audit events and return the set of distinct run_ids.

    Per smart-poller-notify-activation -010 Finding 2: when multiple poller
    chains run against the same state dir, they interleave writes to the
    audit log. Distinct run_ids in a recent window indicate duplicate
    pollers and a broken single-writer assumption.

    Returns an empty set if the audit log is absent or unreadable. The
    caller treats `len(result) > 1` as the duplicate-runner signal.
    """
    audit_path = target / _SMART_POLLER_STATE_REL / "audit.jsonl"
    if not audit_path.is_file():
        return set()
    try:
        with audit_path.open("r", encoding="utf-8") as f:
            lines = f.readlines()
    except OSError:
        return set()
    run_ids: set[str] = set()
    for line in lines[-tail_count:]:
        line = line.strip()
        if not line:
            continue
        try:
            entry = json.loads(line)
        except json.JSONDecodeError:
            continue
        rid = entry.get("run_id")
        if isinstance(rid, str) and rid:
            run_ids.add(rid)
    return run_ids


def _check_smart_bridge_poller(target: Path) -> ToolCheck:
    """Check the smart-poller activation surface end-to-end.

    Per ``bridge/gtkb-bridge-poller-notify-activation-2026-04-29-004.md`` GO
    (REVISED-1 at -003 §5), this check verifies the activation chain from
    runner script through scheduled task to fresh notification artifacts.

    Per -004 GO guardrail 2, the check inspects the ACTUAL scheduled-task
    action target — not just the task name — to confirm the wrapper-based
    activation pattern is in place rather than a direct-runner registration.

    Status mapping:
      - All checks pass → ``pass``
      - Task not registered (initial-install state) → ``warning``
      - Wrapper missing OR wrapper does not resolve runner → ``fail``
      - Task registered but target is wrong (direct-runner instead of
        wrapper) OR audit/notification artifacts stale → ``fail``
    """
    check_name = "Smart bridge poller"

    runner = target / _SMART_POLLER_RUNNER_REL
    wrapper = target / _SMART_POLLER_WRAPPER_REL

    # 1. Runner script present.
    if not runner.is_file():
        return ToolCheck(
            name=check_name,
            required=False,
            found=False,
            status="fail",
            message=(
                f"smart-poller runner missing at {_SMART_POLLER_RUNNER_REL.as_posix()} "
                f"— run `gt project upgrade --apply` or verify Phase 2 path rebase"
            ),
        )

    # 2. PS1 helper present (interactive use + doctor's -ValidateOnly mode).
    if not wrapper.is_file():
        return ToolCheck(
            name=check_name,
            required=False,
            found=False,
            status="fail",
            message=(
                f"smart-poller PS1 helper missing at {_SMART_POLLER_WRAPPER_REL.as_posix()} "
                f"— see {_BRIDGE_SCHEDULER_DOC} or scripts/install_smart_poller_task.ps1"
            ),
        )

    # 2b. VBS daemon launcher present (per -008 Finding 1: doctor must
    # validate the actual daemon launcher, not just a nearby helper).
    vbs = target / _SMART_POLLER_VBS_REL
    if not vbs.is_file():
        return ToolCheck(
            name=check_name,
            required=False,
            found=False,
            status="fail",
            message=(
                f"smart-poller VBS daemon launcher missing at {_SMART_POLLER_VBS_REL.as_posix()} "
                f"— this is the actual file Task Scheduler executes; see "
                f"scripts/install_smart_poller_task.ps1 for installation."
            ),
        )

    # 3. Wrapper resolves runner path. Run the wrapper in -ValidateOnly mode
    # which executes the actual $runnerPath assignment + Test-Path, then exits
    # without starting the long-running poller. This validates the EFFECTIVE
    # path the wrapper would invoke, not a substring in arbitrary file content
    # (per smart-poller-notify-activation -006 Finding 2: a future edit could
    # leave the comment intact while changing $runnerPath to a bad path under
    # the substring approach).
    validate_ok, validate_output = _run_cmd(
        [
            "powershell",
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            str(wrapper),
            "-ValidateOnly",
        ],
        timeout=15,
    )
    if not validate_ok:
        return ToolCheck(
            name=check_name,
            required=False,
            found=True,
            status="fail",
            message=(
                "smart-poller wrapper -ValidateOnly failed to resolve $runnerPath: "
                f"{validate_output[:200] or '(no output)'}. Phase 2 path rebase "
                f"outstanding or wrapper customized — review {_SMART_POLLER_WRAPPER_REL.as_posix()}."
            ),
        )
    # On success, the wrapper prints "OK runner=<path>". Confirm the resolved
    # path matches our expectation (defensive: if a future wrapper edit
    # silently aliased to a different runner, we want to know).
    expected_marker = str(_SMART_POLLER_RUNNER_REL).replace("/", "\\")
    if expected_marker not in validate_output and _SMART_POLLER_RUNNER_REL.as_posix() not in validate_output:
        return ToolCheck(
            name=check_name,
            required=False,
            found=True,
            status="fail",
            message=(
                f"smart-poller PS1 helper -ValidateOnly resolved a different runner path: "
                f"{validate_output.strip() or '(empty)'}. Expected helper to resolve "
                f"to {_SMART_POLLER_RUNNER_REL.as_posix()}; this likely indicates Phase 2 "
                f"path rebase is in progress or PS1 helper has been customized."
            ),
        )

    # 3b. VBS daemon launcher /Validate (per -008 Finding 1). The daemon's
    # ACTUAL effective path is in the VBS, not the PS1. Run the VBS in
    # /Validate mode (echoes "OK runner=<path>" + exits 0 if resolution
    # succeeds; exits 1 if runner missing). This is the load-bearing
    # validation: a wrong VBS path here means Task Scheduler will fail
    # when it tries to launch the daemon, regardless of PS1 helper state.
    vbs_validate_ok, vbs_validate_output = _run_cmd(
        [
            "cscript.exe",
            "//nologo",
            str(vbs),
            "/Validate",
        ],
        timeout=15,
    )
    if not vbs_validate_ok:
        return ToolCheck(
            name=check_name,
            required=False,
            found=True,
            status="fail",
            message=(
                f"smart-poller VBS /Validate failed to resolve runnerPath: "
                f"{vbs_validate_output[:200] or '(no output)'}. This is the daemon's "
                f"actual launch path — Task Scheduler will fail at startup. Phase 2 path "
                f"rebase outstanding or VBS launcher customized — review "
                f"{_SMART_POLLER_VBS_REL.as_posix()}."
            ),
        )
    if expected_marker not in vbs_validate_output and _SMART_POLLER_RUNNER_REL.as_posix() not in vbs_validate_output:
        return ToolCheck(
            name=check_name,
            required=False,
            found=True,
            status="fail",
            message=(
                f"smart-poller VBS /Validate resolved a different runner path: "
                f"{vbs_validate_output.strip() or '(empty)'}. Expected VBS to resolve "
                f"to {_SMART_POLLER_RUNNER_REL.as_posix()}; this is the actual daemon path — "
                f"Task Scheduler would launch the wrong runner. Phase 2 path rebase or "
                f"VBS customization."
            ),
        )

    # 4. State dir writable.
    state_dir = target / _SMART_POLLER_STATE_REL
    if not state_dir.is_dir():
        # State dir is created by the runner on first iteration; absence is
        # OK if the task hasn't started yet. Soft pass-through here; the
        # subsequent task / audit / notification checks will surface the
        # real status.
        pass

    # 5. Task registered + 6. task target points to wrapper.
    # On non-Windows hosts, schtasks/Get-ScheduledTask are not available;
    # gracefully skip task inspection.
    task_ok, task_xml = _run_cmd(
        [
            "powershell",
            "-NoProfile",
            "-Command",
            f"Get-ScheduledTask -TaskName '{_SMART_POLLER_TASK_NAME}' "
            "-ErrorAction SilentlyContinue | "
            "ForEach-Object { $_.Actions | Format-List | Out-String }",
        ],
        timeout=10,
    )
    if not task_ok or not task_xml.strip():
        return ToolCheck(
            name=check_name,
            required=False,
            found=True,
            status="warning",
            message=(
                f"smart-poller task '{_SMART_POLLER_TASK_NAME}' not registered "
                f"— run `scripts/install_smart_poller_task.ps1` to activate"
            ),
        )

    # 6. Task target points to the VBS launcher (per -004 guardrail 2 + -006
    # follow-up: the daemon path uses the .vbs launcher, not the .ps1 directly,
    # to suppress visible PowerShell windows on Windows 11 + Terminal).
    vbs_name = _SMART_POLLER_VBS_REL.name  # run_smart_bridge_poller.vbs
    if vbs_name not in task_xml:
        return ToolCheck(
            name=check_name,
            required=False,
            found=True,
            status="fail",
            message=(
                f"smart-poller task registered but action target does NOT include "
                f"the VBS launcher '{vbs_name}'. Re-install via "
                f"scripts/install_smart_poller_task.ps1 to use the Phase-2-stable "
                f"wrapper pattern (see -004 Finding 1 + -006 Windows 11 Terminal "
                f"visibility follow-up)."
            ),
        )

    # 7. Recent audit event in poller-runs/.
    audit_dir = target / _SMART_POLLER_AUDIT_REL
    audit_ages: list[float] = []
    if audit_dir.is_dir():
        now_ts = time.time()
        for entry in audit_dir.iterdir():
            if entry.is_file():
                try:
                    audit_ages.append(now_ts - entry.stat().st_mtime)
                except OSError:
                    continue
    audit_age = min(audit_ages) if audit_ages else None

    if audit_age is None:
        return ToolCheck(
            name=check_name,
            required=False,
            found=True,
            status="warning",
            message=(
                f"smart-poller task registered but no audit events at "
                f"{_SMART_POLLER_AUDIT_REL.as_posix()} — task may not have started yet "
                f"or first iteration not reached"
            ),
        )

    if audit_age > _SMART_POLLER_FRESH_SECS:
        return ToolCheck(
            name=check_name,
            required=False,
            found=True,
            status="fail",
            message=(
                f"smart-poller task registered but most recent audit event is "
                f"{int(audit_age)}s old (> {_SMART_POLLER_FRESH_SECS}s threshold). "
                f"Task may be stuck — inspect Task Scheduler"
            ),
        )

    # 7b. Duplicate-runner detection (per -010 Finding 2). When multiple
    # poller chains run against the same state directory, they interleave
    # writes to the audit log, checkpoint, and notification files. The
    # single-writer assumption breaks. Detection: parse the last ~6 audit
    # events (~90 seconds at 15s cadence) and count distinct run_ids.
    # If more than 1, surface fail with cleanup instructions.
    distinct_run_ids = _recent_audit_run_ids(target)
    if len(distinct_run_ids) > 1:
        return ToolCheck(
            name=check_name,
            required=False,
            found=True,
            status="fail",
            message=(
                f"smart-poller has {len(distinct_run_ids)} concurrent poller chains writing "
                f"to .gtkb-state/bridge-poller/ in the last ~90s (run_ids: "
                f"{', '.join(sorted(distinct_run_ids))[:200]}). The single-writer assumption "
                f"is broken. Identify and stop all but one chain via "
                f"`Get-WmiObject Win32_Process | Where-Object {{$_.CommandLine -like "
                f"'*bridge_poller_runner*'}} | Stop-Process -Force` (then re-start the "
                f"scheduled task)."
            ),
        )

    # 8. Notification freshness (only checked if a notification file exists).
    # Absent notification files mean "no actionable pending work" — that's a
    # correct steady-state, not a failure. Stale notification (file present
    # but written_at far in the past) IS a failure indicating the runner is
    # not updating the file even though its mtime might be recent.
    notify_dir = target / _SMART_POLLER_NOTIFY_REL
    stale_notification: str | None = None
    if notify_dir.is_dir():
        for fname in ("pending-bridge-action-prime.json", "pending-bridge-action-codex.json"):
            fpath = notify_dir / fname
            if fpath.is_file():
                try:
                    age = time.time() - fpath.stat().st_mtime
                except OSError:
                    continue
                if age > _SMART_POLLER_FRESH_SECS:
                    stale_notification = f"{fname} is {int(age)}s old (> {_SMART_POLLER_FRESH_SECS}s)"
                    break

    if stale_notification:
        return ToolCheck(
            name=check_name,
            required=False,
            found=True,
            status="fail",
            message=f"smart-poller notification stale: {stale_notification}",
        )

    return ToolCheck(
        name=check_name,
        required=False,
        found=True,
        status="pass",
        message=(
            f"smart-poller active (task '{_SMART_POLLER_TASK_NAME}', VBS daemon "
            f"-> runner verified, PS1 helper -> runner verified, audit event "
            f"{int(audit_age)}s old)"
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
        for registration in artifacts_for_doctor(profile, class_="settings-hook-registration"):
            if isinstance(registration, SettingsHookRegistration):
                checks.append(_check_settings_hook_registration_drift(target, profile, registration))
        checks.append(_check_bridge_poller(target, "claude"))
        checks.append(_check_bridge_poller(target, "codex"))
        checks.append(_check_smart_bridge_poller(target))
        checks.append(_check_da_harvest_coverage(target))

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
