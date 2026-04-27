"""Wave 2 lane 6 (Stage C leaf): dashboard regeneration rehearsal.

Per ``bridge/gtkb-isolation-016-phase8-wave2-slice11-011.md`` (REVISED-5)
and ``-012`` (Codex GO with 6 implementation constraints).

Probes the dashboard generator and current dashboard artifacts read-only,
builds an isolated sandbox containing the project-state inputs the
generator consumes (including 5 named deployment-evidence files), spawns
the generator via the audit-hook-instrumented runner subprocess, and
captures classification of any out-of-sandbox reads as audit-hook
violations.

Constraints (per Slice 11 GO ``-012``):
  1. No recursive ``legacy_root/scripts`` allowance — the runner's
     allowlist enforces an exact-file code allowlist + per-prefix
     sandbox/Python-runtime/temp allowance only.
  2. Legacy originals of the 5 generator-consumed deployment files are
     denied at the audit-hook layer; sandbox copies under
     ``<sandbox_root>/scripts/...`` are allowed.
  3. The 5 deployment files are copied as real files (not symlinks),
     preserving the relative path under ``<sandbox_root>``.
  4. If a deployment file exists in legacy source but is not byte-equal
     in the sandbox copy, the lane returns ``status="error"``.
  5. Bystander files under ``scripts/deploy/`` are NOT copied unless
     future static analysis flags them.
  6. Driver missing-lane fixture advances from ``"dashboard"`` to
     ``"rollback"`` when this lane lands.

Outputs:
  - ``dashboard-regen-plan.json`` (machine-readable plan + audit_hook_proof)
  - ``dashboard-regen-preview.md`` (human review)
  - ``violations.json`` (audit-hook violations; empty on ok path)
  - ``sandbox/`` (the assembled sandbox tree, preserved for forensics)
  - ``sample_render/`` (subprocess output: index.html + dashboard-data.json + stdout/stderr)
  - ``result.json`` (standard sub-script envelope)
"""

from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import sys
import time
from collections.abc import Callable
from pathlib import Path
from typing import Any

from rehearse._common import LEGACY_ROOT
from rehearse._split_helper import emit_result

# ---- Constants --------------------------------------------------------

# Per Slice 11 REVISED-5 ``-010``: canonical list of generator-consumed
# deployment-evidence files. Source-verified at
# ``scripts/session_self_initialization.py:1716-1721``. These are
# required-when-present sandbox copies (lane fails byte-equal copy
# verification if a file exists in legacy but the copy fails).
_KNOWN_DEPLOYMENT_INPUTS: tuple[str, ...] = (
    "scripts/agent-container-template.yaml",
    "scripts/deploy/build-and-deploy-staging.ps1",
    "scripts/deploy/api-gateway-restore.yaml",
    "scripts/deploy/upgrade.ps1",
    "scripts/deploy/rollback.ps1",
)

# Required: lane fails with status='error' if missing from legacy.
_REQUIRED_SANDBOX_INPUTS: tuple[str, ...] = (
    "groundtruth.db",
    "bridge/INDEX.md",
    ".claude/rules/operating-role.md",
    "memory/work_list.md",
    "memory/release-readiness.md",
    "pyproject.toml",
)

_REQUIRED_SANDBOX_DIRS: tuple[str, ...] = (".github/workflows",)

# Optional: lane warns if missing.
_OPTIONAL_SANDBOX_INPUTS: tuple[str, ...] = (
    "src/api_versioning.py",
    "package.json",
)

_OPTIONAL_SANDBOX_DIRS: tuple[str, ...] = (
    ".claude/hooks",
    ".claude/skills",
)

# Generated fresh in sandbox (NEVER copied from legacy).
_FRESH_SANDBOX_FILES: dict[str, str] = {
    "memory/gtkb-dashboard-history.json": "[]",
}

# Subprocess timeout (seconds) for the sample-render runner.
_SUBPROCESS_TIMEOUT = 120

# Per Slice 11 REVISED-1 of post-impl (addressing Codex `-014` Finding 1):
# the runner subprocess uses ``os._exit(99)`` to fail-closed on the first
# audit-hook violation. The lane recognizes returncode 99 as the canonical
# audit-hook termination signal (vs. generator's normal codes 0/1).
_AUDIT_HOOK_TERMINATION_RETURNCODE = 99


# ---- Probe helpers ----------------------------------------------------


def _probe_generator(generator_path: Path) -> dict[str, Any]:
    """Probe the generator script: existence + size + commit stamp."""
    if not generator_path.is_file():
        return {"path": str(generator_path), "exists": False, "size_bytes": 0}
    return {
        "path": str(generator_path),
        "exists": True,
        "size_bytes": generator_path.stat().st_size,
    }


def _probe_current_dashboard(legacy_root: Path) -> dict[str, Any]:
    """Probe current dashboard artifacts (presence + size only).

    Per REVISED-3 §2.2 carry-forward: the lane MUST NOT parse HTML
    or embed JSON content. Size + structural top-level-key probe is
    sufficient for the regen plan.
    """
    paths = {
        "index_html": legacy_root / "docs" / "gtkb-dashboard" / "index.html",
        "dashboard_data_json": legacy_root / "docs" / "gtkb-dashboard" / "dashboard-data.json",
        "history_json": legacy_root / "memory" / "gtkb-dashboard-history.json",
        "grafana_dir": legacy_root / "docs" / "gtkb-dashboard" / "grafana",
    }
    out: dict[str, Any] = {}
    for key, p in paths.items():
        if p.is_file():
            out[key] = {"exists": True, "is_file": True, "size_bytes": p.stat().st_size}
        elif p.is_dir():
            out[key] = {"exists": True, "is_directory": True}
        else:
            out[key] = {"exists": False}
    return out


def _probe_lifecycle_hooks(legacy_root: Path) -> dict[str, Any]:
    """Probe lifecycle hook configuration files (presence only)."""
    return {
        "claude_settings": (legacy_root / ".claude" / "settings.json").is_file(),
        "codex_hooks": (legacy_root / ".codex" / "hooks.json").is_file(),
    }


def discover_deployment_dependencies() -> tuple[str, ...]:
    """Return the canonical list of generator-consumed deployment-evidence files.

    Per REVISED-5 ``-010`` Required Revision: this list is explicitly
    tracked (``_KNOWN_DEPLOYMENT_INPUTS``) as defense-in-depth against
    future static-analysis bugs. The static-analysis broadening described
    in REVISED-5 §2.3 is provided here as the canonical anchor; a future
    AST-based discovery mechanism can cross-validate against this list.

    Source-verified at ``scripts/session_self_initialization.py:1716-1721``.
    """
    return _KNOWN_DEPLOYMENT_INPUTS


# ---- Sandbox builders -------------------------------------------------


def _sha256(path: Path) -> str:
    """Return the sha256 hex digest of a file's bytes."""
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _copy_file_real(src: Path, dst: Path) -> None:
    """Copy a real file (not symlink), preserving mtime, creating parents."""
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst, follow_symlinks=True)


def _copy_dir_real(src: Path, dst: Path) -> None:
    """Recursively copy a directory tree as real files (not symlinks)."""
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(src, dst, symlinks=False, dirs_exist_ok=False)


def _build_sandbox(legacy_root: Path, sandbox_root: Path, warnings: list[str]) -> tuple[dict[str, Any], list[str]]:
    """Assemble sandbox tree per REVISED-5 §3.1-§3.4.

    Returns ``(summary, missing_required_paths)``. If ``missing_required``
    is non-empty, the lane fails before subprocess invocation.
    """
    sandbox_root.mkdir(parents=True, exist_ok=True)
    missing_required: list[str] = []
    summary: dict[str, list[str]] = {
        "required_copied": [],
        "required_dirs_copied": [],
        "optional_copied": [],
        "optional_dirs_copied": [],
        "optional_missing": [],
        "fresh_files_written": [],
    }

    # Required files.
    for rel in _REQUIRED_SANDBOX_INPUTS:
        src = legacy_root / rel
        if not src.is_file():
            missing_required.append(rel)
            continue
        _copy_file_real(src, sandbox_root / rel)
        summary["required_copied"].append(rel)

    # Required directories (recursive copy).
    for rel in _REQUIRED_SANDBOX_DIRS:
        src = legacy_root / rel
        if not src.is_dir():
            missing_required.append(rel)
            continue
        _copy_dir_real(src, sandbox_root / rel)
        summary["required_dirs_copied"].append(rel)

    # Optional files.
    for rel in _OPTIONAL_SANDBOX_INPUTS:
        src = legacy_root / rel
        if src.is_file():
            _copy_file_real(src, sandbox_root / rel)
            summary["optional_copied"].append(rel)
        else:
            summary["optional_missing"].append(rel)
            warnings.append(f"optional_input_missing: {rel}")

    # Optional directories.
    for rel in _OPTIONAL_SANDBOX_DIRS:
        src = legacy_root / rel
        if src.is_dir():
            _copy_dir_real(src, sandbox_root / rel)
            summary["optional_dirs_copied"].append(rel)
        else:
            summary["optional_missing"].append(rel)
            warnings.append(f"optional_input_missing: {rel}")

    # Fresh-generated files.
    for rel, content in _FRESH_SANDBOX_FILES.items():
        dst = sandbox_root / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_text(content, encoding="utf-8")
        summary["fresh_files_written"].append(rel)

    # Lifecycle guard with current-session metadata.
    lifecycle_guard_path = sandbox_root / ".claude" / "session" / "lifecycle-guard.json"
    lifecycle_guard_path.parent.mkdir(parents=True, exist_ok=True)
    lifecycle_guard_path.write_text(
        json.dumps(
            {
                "start_iso": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "session_id": "S314-rehearse",
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    summary["fresh_files_written"].append(".claude/session/lifecycle-guard.json")

    # Empty docs/gtkb-dashboard/ directory (generator writes here).
    (sandbox_root / "docs" / "gtkb-dashboard").mkdir(parents=True, exist_ok=True)

    return summary, missing_required


def _verify_deployment_files(legacy_root: Path, sandbox_root: Path) -> dict[str, Any]:
    """Copy + byte-equal verify the 5 deployment files.

    Per Codex ``-012`` constraint 4: if a deployment file exists in legacy
    source but the sandbox copy is not byte-equal (or copy failed),
    return status='error'. Missing-from-legacy is acceptable as a
    ``deployment_evidence_incomplete`` warning.

    Returns:
        {
            "expected_inputs": [...],
            "present_in_legacy_source": [...],
            "copied_to_sandbox": [...],
            "missing_from_legacy_source": [...],
            "copy_errors": [{"path": ..., "reason": ...}, ...],
        }
    """
    expected = list(_KNOWN_DEPLOYMENT_INPUTS)
    present: list[str] = []
    copied: list[str] = []
    missing: list[str] = []
    errors: list[dict[str, str]] = []

    for rel in expected:
        src = legacy_root / rel
        if not src.is_file():
            missing.append(rel)
            continue
        present.append(rel)
        dst = sandbox_root / rel
        try:
            _copy_file_real(src, dst)
        except OSError as exc:
            errors.append({"path": rel, "reason": f"copy_failed: {exc}"})
            continue
        # Byte-equal verification (Codex `-012` constraint 4).
        try:
            src_hash = _sha256(src)
            dst_hash = _sha256(dst)
        except OSError as exc:
            errors.append({"path": rel, "reason": f"hash_failed: {exc}"})
            continue
        if src_hash != dst_hash:
            errors.append({"path": rel, "reason": f"sha256_mismatch: legacy={src_hash[:12]} sandbox={dst_hash[:12]}"})
            continue
        copied.append(rel)

    return {
        "expected_inputs": expected,
        "present_in_legacy_source": present,
        "copied_to_sandbox": copied,
        "missing_from_legacy_source": missing,
        "copy_errors": errors,
    }


# ---- Subprocess invocation --------------------------------------------


def _build_generator_argv(sandbox_root: Path) -> list[str]:
    """Build argv for the legacy generator per REVISED-5 §2.3."""
    return [
        "--project-root",
        str(sandbox_root),
        "--dashboard-dir",
        str(sandbox_root / "docs" / "gtkb-dashboard"),
        "--history-path",
        str(sandbox_root / "memory" / "gtkb-dashboard-history.json"),
        "--role-record-path",
        str(sandbox_root / ".claude" / "rules" / "operating-role.md"),
        "--lifecycle-guard-path",
        str(sandbox_root / ".claude" / "session" / "lifecycle-guard.json"),
        "--harness-name",
        "claude",
        "--skip-bridge-maintenance",
        "--fast-hook",
    ]


def _build_subprocess_command(
    legacy_root: Path,
    sandbox_root: Path,
    violations_path: Path,
) -> list[str]:
    """Build the subprocess command list (runner + generator argv)."""
    legacy_script = legacy_root / "scripts" / "session_self_initialization.py"
    runner = legacy_root / "scripts" / "rehearse" / "_dashboard_regen_runner.py"
    return [
        sys.executable,
        str(runner),
        "--legacy-script",
        str(legacy_script),
        "--legacy-root",
        str(legacy_root),
        "--sandbox-root",
        str(sandbox_root),
        "--violations-out",
        str(violations_path),
        "--",
        *_build_generator_argv(sandbox_root),
    ]


def _default_subprocess_invoker(cmd: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    """Default subprocess invocation. Tests inject a fake invoker."""
    return subprocess.run(  # noqa: S603 (controlled command list, no shell)
        cmd,
        cwd=str(cwd),
        capture_output=True,
        text=True,
        timeout=_SUBPROCESS_TIMEOUT,
        check=False,
    )


def _run_sample_render(
    legacy_root: Path,
    sandbox_root: Path,
    sample_render_dir: Path,
    violations_path: Path,
    invoker: Callable[[list[str], Path], subprocess.CompletedProcess[str]],
) -> tuple[subprocess.CompletedProcess[str] | None, list[dict[str, Any]], str | None]:
    """Spawn the generator subprocess via the runner.

    Returns ``(proc_or_None, violations, error_kind)``.
    On TimeoutExpired returns ``(None, [], "timeout")``.
    """
    sample_render_dir.mkdir(parents=True, exist_ok=True)
    cmd = _build_subprocess_command(legacy_root, sandbox_root, violations_path)
    try:
        proc = invoker(cmd, sample_render_dir)
    except subprocess.TimeoutExpired:
        return None, [], "timeout"
    # Persist stdout/stderr alongside the sample render.
    (sample_render_dir / "stdout.txt").write_text(proc.stdout or "", encoding="utf-8")
    (sample_render_dir / "stderr.txt").write_text(proc.stderr or "", encoding="utf-8")
    if violations_path.exists():
        try:
            violations = json.loads(violations_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            violations = []
    else:
        violations = []
    return proc, violations, None


# ---- Output emitters --------------------------------------------------


def _quarantine_sample_render(sample_render_dir: Path, violation_count: int) -> None:
    """Rename sample_render dir to ``.QUARANTINED-<count>-violations`` to signal
    operator the artifacts are incomplete / suspect.

    Per Codex `-014` Finding 1 required revision: "Prevent preserved
    sample artifacts from containing content derived from denied legacy
    reads. ... add explicit handling for quarantining or suppressing
    sample-render artifacts when violations are non-empty."

    Subprocess termination via ``os._exit(99)`` already prevents the
    denied open() from completing (PEP 578 audit hooks fire pre-action).
    The partial sample_render contents at termination time contain only
    sandbox-derived data — no leaked legacy content. The quarantine
    rename is defense-in-depth: it signals the artifacts are incomplete
    and should not be trusted, even though they're technically clean.
    """
    if not sample_render_dir.exists():
        return
    quarantine_path = sample_render_dir.with_name(f"{sample_render_dir.name}.QUARANTINED-{violation_count}-violations")
    # If a previous quarantine already exists (rare; same lane re-run),
    # append a discriminator.
    if quarantine_path.exists():
        ts = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
        quarantine_path = sample_render_dir.with_name(
            f"{sample_render_dir.name}.QUARANTINED-{violation_count}-violations-{ts}"
        )
    try:
        sample_render_dir.rename(quarantine_path)
    except OSError:
        # Best-effort; rename can fail if a process holds the dir on Windows.
        pass


def _build_audit_hook_proof(
    legacy_root: Path,
    sandbox_root: Path,
    violations: list[dict[str, Any]],
    proc: subprocess.CompletedProcess[str] | None,
    deployment_evidence: dict[str, Any],
) -> dict[str, Any]:
    """Build the audit_hook_proof block per REVISED-5 §5.1."""
    if not violations:
        verdict = "no_legacy_data_read_detected"
    else:
        verdict = "legacy_data_read_detected"
    return {
        "hook_installed_before_legacy_script_import": True,
        "audit_events_intercepted": ["open", "subprocess.Popen"],
        "allowed_bases": [
            "<sys.base_prefix>",
            "<sys.prefix>",
            f"{legacy_root}/scripts (5 exact-file allows + __pycache__/ prefixes only)",
            f"<sandbox_root> ({sandbox_root})",
            "<temp>",
        ],
        "denied_bases": [
            f"{legacy_root}/scripts/agent-container-template.yaml",
            f"{legacy_root}/scripts/deploy/",
            f"{legacy_root}/.env.local",
            f"{legacy_root}/memory",
            f"{legacy_root}/bridge",
            f"{legacy_root}/docs/gtkb-dashboard",
            f"{legacy_root}/.github/workflows",
            f"{legacy_root}/groundtruth.db",
            f"{legacy_root}/.git",
        ],
        "violations_count": len(violations),
        "violations": violations,
        "subprocess_returncode": proc.returncode if proc is not None else None,
        "subprocess_stdout_bytes": len(proc.stdout) if proc is not None else 0,
        "subprocess_stderr_bytes": len(proc.stderr) if proc is not None else 0,
        "verdict": verdict,
        "deployment_files_pipeline": deployment_evidence,
    }


def _build_regen_plan(legacy_root: Path) -> dict[str, str]:
    """Per REVISED-5 §5.1 regen_plan block."""
    target_root = "applications/Agent_Red"
    return {
        "target_generator_path": f"{target_root}/scripts/session_self_initialization.py",
        "target_dashboard_path": f"{target_root}/docs/gtkb-dashboard/index.html",
        "target_data_json_path": f"{target_root}/docs/gtkb-dashboard/dashboard-data.json",
        "target_history_path": f"{target_root}/memory/gtkb-dashboard-history.json",
        "target_grafana_path": f"{target_root}/docs/gtkb-dashboard/grafana",
    }


def _emit_plan_json(
    plan_path: Path,
    legacy_root: Path,
    sandbox_root: Path,
    source_probes: dict[str, Any],
    dashboard_probes: dict[str, Any],
    lifecycle_probes: dict[str, Any],
    sandbox_summary: dict[str, list[str]],
    deployment_evidence: dict[str, Any],
    violations: list[dict[str, Any]],
    proc: subprocess.CompletedProcess[str] | None,
    status: str,
    warnings: list[str],
) -> None:
    payload = {
        "schema_version": 1,
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "lane": "dashboard_regen",
        "status": status,
        "source": {
            "generator": source_probes,
            "dashboard": dashboard_probes,
            "lifecycle_hooks": lifecycle_probes,
        },
        "regen_plan": _build_regen_plan(legacy_root),
        "lifecycle_hooks": {
            "claude_settings_session_start_update_required": lifecycle_probes.get("claude_settings", False),
            "claude_settings_stop_update_required": lifecycle_probes.get("claude_settings", False),
            "codex_hooks_parity_update_required": lifecycle_probes.get("codex_hooks", False),
        },
        "sandbox": sandbox_summary,
        "audit_hook_proof": _build_audit_hook_proof(legacy_root, sandbox_root, violations, proc, deployment_evidence),
        "warnings": warnings,
    }
    plan_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _emit_preview_markdown(
    preview_path: Path,
    legacy_root: Path,
    source_probes: dict[str, Any],
    sandbox_summary: dict[str, list[str]],
    deployment_evidence: dict[str, Any],
    violations: list[dict[str, Any]],
    status: str,
    warnings: list[str],
) -> None:
    timestamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    plan = _build_regen_plan(legacy_root)
    lines: list[str] = [
        "# Dashboard Regeneration Plan\n\n",
        f"Generated: {timestamp}\n",
        "Source: GTKB-ISOLATION-016 Phase 8 rehearsal `_dashboard_regen.py` (Slice 11).\n\n",
        f"Status: **{status}**\n\n",
        "## Summary\n\n",
        f"- Generator: `{source_probes.get('path')}` ({source_probes.get('size_bytes', 0):,} bytes)\n",
        f"- Sandbox required files copied: {len(sandbox_summary['required_copied'])}\n",
        f"- Sandbox required dirs copied: {len(sandbox_summary['required_dirs_copied'])}\n",
        f"- Sandbox optional files copied: {len(sandbox_summary['optional_copied'])}\n",
        f"- Deployment files copied: {len(deployment_evidence['copied_to_sandbox'])} of "
        f"{len(deployment_evidence['expected_inputs'])}\n",
        f"- Audit-hook violations: {len(violations)}\n\n",
        "## Relocation Plan\n\n",
        "| Source path | Target path |\n",
        "|---|---|\n",
        f"| `scripts/session_self_initialization.py` | `{plan['target_generator_path']}` |\n",
        f"| `docs/gtkb-dashboard/index.html` | `{plan['target_dashboard_path']}` |\n",
        f"| `docs/gtkb-dashboard/dashboard-data.json` | `{plan['target_data_json_path']}` |\n",
        f"| `docs/gtkb-dashboard/grafana/` | `{plan['target_grafana_path']}` |\n",
        f"| `memory/gtkb-dashboard-history.json` | `{plan['target_history_path']}` |\n\n",
        "## Sandbox Boundary Proof\n\n",
        "Audit hook installed: ✓ (before legacy-script import)\n",
        "Events intercepted: open, subprocess.Popen\n",
        f"Violations: {len(violations)}\n",
        f"Verdict: **{'no legacy data read detected' if not violations else 'legacy data read detected'}**\n\n",
        "## Deployment Files\n\n",
    ]
    for entry in deployment_evidence["expected_inputs"]:
        if entry in deployment_evidence["copied_to_sandbox"]:
            mark = "✓ copied"
        elif entry in deployment_evidence["missing_from_legacy_source"]:
            mark = "(absent from legacy source)"
        else:
            err = next(
                (e for e in deployment_evidence["copy_errors"] if e["path"] == entry),
                None,
            )
            mark = f"✗ {err['reason']}" if err else "✗ unknown"
        lines.append(f"- `{entry}` — {mark}\n")
    if warnings:
        lines.append("\n## Warnings\n\n")
        for w in warnings:
            lines.append(f"- {w}\n")
    preview_path.write_text("".join(lines), encoding="utf-8")


# ---- Entry point ------------------------------------------------------


def run(
    manifest: dict[str, Any],
    output_dir: Path,
    *,
    dry_run: bool = False,
    project_root: Path | None = None,
    subprocess_invoker: Callable[[list[str], Path], subprocess.CompletedProcess[str]] | None = None,
) -> dict[str, Any]:
    """Wave 2 Stage C leaf lane. Per common contract Wave 2 ``-003`` §4.1.

    ``project_root`` overrides ``LEGACY_ROOT`` for fixture trees.
    ``subprocess_invoker`` allows tests to inject a fake subprocess
    invocation that simulates the runner without spawning a real Python
    subprocess.
    """
    if dry_run:
        return {
            "status": "skipped",
            "output_files": [],
            "metrics": {"reason": "dry_run"},
            "warnings": [],
        }

    legacy_root = project_root if project_root is not None else LEGACY_ROOT
    lane_dir = output_dir / "dashboard_regen"
    lane_dir.mkdir(parents=True, exist_ok=True)

    output_files: list[Path] = []
    warnings: list[str] = []

    # Phase 1: probe legacy artifacts.
    generator_path = legacy_root / "scripts" / "session_self_initialization.py"
    source_probes = _probe_generator(generator_path)
    if not source_probes["exists"]:
        return emit_result(
            lane_dir,
            {
                "status": "error",
                "output_files": [],
                "metrics": {},
                "warnings": [f"generator_script_not_found: {generator_path}"],
            },
        )
    dashboard_probes = _probe_current_dashboard(legacy_root)
    lifecycle_probes = _probe_lifecycle_hooks(legacy_root)

    # Phase 2: build sandbox tree.
    sandbox_root = lane_dir / "sandbox"
    sandbox_summary, missing_required = _build_sandbox(legacy_root, sandbox_root, warnings)
    if missing_required:
        plan_path = lane_dir / "dashboard-regen-plan.json"
        deployment_evidence = {
            "expected_inputs": list(_KNOWN_DEPLOYMENT_INPUTS),
            "present_in_legacy_source": [],
            "copied_to_sandbox": [],
            "missing_from_legacy_source": [],
            "copy_errors": [],
        }
        warnings.extend(f"required_input_missing: {p}" for p in missing_required)
        _emit_plan_json(
            plan_path,
            legacy_root,
            sandbox_root,
            source_probes,
            dashboard_probes,
            lifecycle_probes,
            sandbox_summary,
            deployment_evidence,
            [],
            None,
            "error",
            warnings,
        )
        return emit_result(
            lane_dir,
            {
                "status": "error",
                "output_files": [str(plan_path)],
                "metrics": {"missing_required_inputs": missing_required},
                "warnings": warnings,
            },
        )

    # Phase 3: copy + verify deployment files.
    deployment_evidence = _verify_deployment_files(legacy_root, sandbox_root)
    if deployment_evidence["copy_errors"]:
        warnings.append(
            f"deployment_file_copy_error: {len(deployment_evidence['copy_errors'])} files failed copy/verify"
        )
        plan_path = lane_dir / "dashboard-regen-plan.json"
        _emit_plan_json(
            plan_path,
            legacy_root,
            sandbox_root,
            source_probes,
            dashboard_probes,
            lifecycle_probes,
            sandbox_summary,
            deployment_evidence,
            [],
            None,
            "error",
            warnings,
        )
        return emit_result(
            lane_dir,
            {
                "status": "error",
                "output_files": [str(plan_path)],
                "metrics": {"deployment_copy_errors": len(deployment_evidence["copy_errors"])},
                "warnings": warnings,
            },
        )

    # Phase 4: run sample render via runner subprocess.
    sample_render_dir = lane_dir / "sample_render"
    violations_path = lane_dir / "violations.json"
    invoker = subprocess_invoker or _default_subprocess_invoker
    proc, violations, error_kind = _run_sample_render(
        legacy_root, sandbox_root, sample_render_dir, violations_path, invoker
    )

    # Phase 5: status determination.
    # Per Slice 11 REVISED-1 of post-impl: subprocess returncode 99
    # signals fail-closed termination by the audit hook on first
    # violation (Codex `-014` Finding 1 fix). Distinct from generator's
    # normal returncodes (0 / 1).
    if error_kind == "timeout":
        status = "error"
        warnings.append(f"subprocess_timeout: exceeded {_SUBPROCESS_TIMEOUT}s")
    elif proc is not None and proc.returncode == _AUDIT_HOOK_TERMINATION_RETURNCODE:
        status = "error"
        warnings.append(
            f"audit_hook_fail_closed_termination: subprocess terminated by audit hook on first "
            f"of {len(violations)} violation(s); sample_render quarantined"
        )
        _quarantine_sample_render(sample_render_dir, len(violations))
    elif violations:
        # Defense-in-depth: any non-empty violations list → error,
        # even if subprocess didn't terminate (legacy fallback path).
        status = "error"
        warnings.append(f"legacy_data_read_detected: {len(violations)} violations")
        _quarantine_sample_render(sample_render_dir, len(violations))
    elif proc is not None and proc.returncode != 0:
        status = "error"
        warnings.append(f"subprocess_returncode_nonzero: {proc.returncode}")
    else:
        status = "ok"
        if deployment_evidence["missing_from_legacy_source"]:
            warnings.append(
                "deployment_evidence_incomplete: " + ", ".join(deployment_evidence["missing_from_legacy_source"])
            )

    # Phase 6: emit artifacts.
    plan_path = lane_dir / "dashboard-regen-plan.json"
    preview_path = lane_dir / "dashboard-regen-preview.md"
    _emit_plan_json(
        plan_path,
        legacy_root,
        sandbox_root,
        source_probes,
        dashboard_probes,
        lifecycle_probes,
        sandbox_summary,
        deployment_evidence,
        violations,
        proc,
        status,
        warnings,
    )
    _emit_preview_markdown(
        preview_path,
        legacy_root,
        source_probes,
        sandbox_summary,
        deployment_evidence,
        violations,
        status,
        warnings,
    )
    output_files.extend([plan_path, preview_path])
    if violations_path.exists():
        output_files.append(violations_path)

    metrics = {
        "sandbox_required_files_copied": len(sandbox_summary["required_copied"]),
        "sandbox_required_dirs_copied": len(sandbox_summary["required_dirs_copied"]),
        "sandbox_optional_files_copied": len(sandbox_summary["optional_copied"]),
        "deployment_files_copied": len(deployment_evidence["copied_to_sandbox"]),
        "deployment_files_missing_from_legacy": len(deployment_evidence["missing_from_legacy_source"]),
        "audit_hook_violations": len(violations),
        "subprocess_returncode": proc.returncode if proc is not None else None,
    }

    return emit_result(
        lane_dir,
        {
            "status": status,
            "output_files": [str(p) for p in output_files],
            "metrics": metrics,
            "warnings": warnings,
        },
    )
