"""Wave 2 lane 10 (Stage B leaf): production-effects map.

Per ``bridge/gtkb-isolation-016-phase8-wave2-slice9-005.md`` (REVISED-2)
and ``-006`` (Codex GO with constraint: apply secret-adjacent treatment
to every ``scripts/deploy/_prod_env_vars*.txt`` file, not just the exact
``_prod_env_vars.txt`` filename).

Inventories production-affecting filesystem surfaces and assigns each
one of four dispositions (MOVE / KEEP / DO_NOT_MOVE /
OWNER_DECISION_REQUIRED) plus a ``deploy_safety`` tag (deploy-blocking /
deploy-safe-after-review / deploy-not-applicable) per Phase 8 plan
§"production-effects-map.md must list every code path or config value
that assumes the legacy mixed root".

**Critical safety property:** never reads content of secret-material
files (§2.1). For these surfaces only ``path``, ``exists``, and
``size_bytes`` are recorded; the ``content_read`` field is ``False``
for every secret-adjacent row by construction.

Outputs:
  - ``production-effects-map.md`` (Phase 8 plan §2 named artifact)
  - ``production_effects.json`` (machine-readable companion)
  - ``result.json`` (standard sub-script result envelope)
"""

from __future__ import annotations

import json
import re
import time
from pathlib import Path
from typing import Any

from rehearse._common import LEGACY_ROOT
from rehearse._split_helper import emit_result

# ---- Disposition + deploy_safety vocabulary ---------------------------

_DISPOSITION_MOVE = "MOVE"
_DISPOSITION_KEEP = "KEEP"
_DISPOSITION_DO_NOT_MOVE = "DO_NOT_MOVE"
_DISPOSITION_OWNER_DECISION = "OWNER_DECISION_REQUIRED"

_DEPLOY_SAFETY_BLOCKING = "deploy-blocking"
_DEPLOY_SAFETY_AFTER_REVIEW = "deploy-safe-after-review"
_DEPLOY_SAFETY_NA = "deploy-not-applicable"


# ---- §2.1 Secret material surfaces (presence-only; NEVER content-read) -

# Each entry: (relpath_or_glob, signal, is_glob)
# Per Codex GO -006 implementation constraint: includes the glob
# `scripts/deploy/_prod_env_vars*.txt` to cover every match such as
# `_prod_env_vars.txt` AND `_prod_env_vars_clean.txt`.
_SECRET_MATERIAL_SURFACES: tuple[tuple[str, str, bool], ...] = (
    (".env.local", "secret_material_per_phase8_plan_section_4", False),
    (".env", "secret_material_per_phase8_plan_section_4", False),
    ("secrets", "secret_material_per_phase8_plan_section_4", False),
    ("groundtruth-artifacts/secrets", "secret_material_per_phase8_plan_section_4", False),
    ("scripts/deploy/_prod_env_vars*.txt", "production_env_vars_secret_adjacent_per_codex_s9_004", True),
    ("infrastructure/terraform/*.tfvars", "terraform_variable_potentially_sensitive", True),
)

# ---- §2.2-§2.17 Non-secret surfaces (probed entries) ------------------
#
# Each entry: (relpath_or_glob, default_disposition, signal,
#              deploy_safety, content_scannable, is_glob, category)
# content_scannable: whether content can be safely read (False for
# secret-adjacent; True for source files in git).
# is_glob: True if relpath should be globbed (multiple matches).

_NON_SECRET_SURFACES: tuple[tuple[str, str, str, str, bool, bool, str], ...] = (
    # §2.2 Templates
    (
        ".env.example",
        _DISPOSITION_MOVE,
        "adopter_environment_template",
        _DEPLOY_SAFETY_AFTER_REVIEW,
        True,
        False,
        "template",
    ),
    (
        ".env.integration.example",
        _DISPOSITION_MOVE,
        "adopter_environment_template",
        _DEPLOY_SAFETY_AFTER_REVIEW,
        True,
        False,
        "template",
    ),
    # §2.3 Container orchestration
    (
        "docker-compose.yml",
        _DISPOSITION_MOVE,
        "adopter_container_orchestration",
        _DEPLOY_SAFETY_BLOCKING,
        True,
        False,
        "container_orchestration",
    ),
    # §2.4 Shopify deployment
    (
        ".shopify/deploy-bundle",
        _DISPOSITION_MOVE,
        "adopter_shopify_deployment_artifact",
        _DEPLOY_SAFETY_BLOCKING,
        False,
        False,
        "shopify_deploy",
    ),
    (
        ".shopify/deploy-bundle.br",
        _DISPOSITION_MOVE,
        "adopter_shopify_deployment_artifact_compressed",
        _DEPLOY_SAFETY_BLOCKING,
        False,
        False,
        "shopify_deploy",
    ),
    # §2.5 Deploy logs (owner-decision per spec)
    (
        "logs/deploy-*.log",
        _DISPOSITION_OWNER_DECISION,
        "adopter_deployment_history",
        _DEPLOY_SAFETY_AFTER_REVIEW,
        False,
        True,
        "deploy_log",
    ),
    # §2.7 POR snapshots
    (
        ".groundtruth/por-16d-phase1-snapshot.json",
        _DISPOSITION_MOVE,
        "adopter_production_operations_record",
        _DEPLOY_SAFETY_AFTER_REVIEW,
        False,
        False,
        "por_snapshot",
    ),
    (
        ".groundtruth/por-16d-phase2-classification.json",
        _DISPOSITION_MOVE,
        "adopter_production_operations_record",
        _DEPLOY_SAFETY_AFTER_REVIEW,
        False,
        False,
        "por_snapshot",
    ),
    (
        ".groundtruth/por-16d-phase2-snapshot.json",
        _DISPOSITION_MOVE,
        "adopter_production_operations_record",
        _DEPLOY_SAFETY_AFTER_REVIEW,
        False,
        False,
        "por_snapshot",
    ),
    # §2.8 Per-session evidence
    (
        ".groundtruth/wrap-scan",
        _DISPOSITION_OWNER_DECISION,
        "mixed_scope_session_evidence",
        _DEPLOY_SAFETY_NA,
        False,
        False,
        "session_evidence",
    ),
    (
        ".groundtruth/session",
        _DISPOSITION_OWNER_DECISION,
        "per_session_state_not_per_scope",
        _DEPLOY_SAFETY_NA,
        False,
        False,
        "session_evidence",
    ),
    # §2.9 Config files
    (
        "groundtruth.toml",
        _DISPOSITION_KEEP,
        "framework_config_per_classify_tree",
        _DEPLOY_SAFETY_NA,
        False,
        False,
        "framework_config",
    ),
    (
        "tools/knowledge-db/groundtruth.toml",
        _DISPOSITION_KEEP,
        "framework_config_per_classify_tree",
        _DEPLOY_SAFETY_NA,
        False,
        False,
        "framework_config",
    ),
    # §2.10 Authoritative DB (immovable per Phase 8 §4)
    (
        "groundtruth.db",
        _DISPOSITION_DO_NOT_MOVE,
        "phase_8_plan_section_4_explicit_immovable",
        _DEPLOY_SAFETY_BLOCKING,
        False,
        False,
        "authoritative_db",
    ),
    (
        "groundtruth.db-shm",
        _DISPOSITION_DO_NOT_MOVE,
        "sqlite_wal_companion",
        _DEPLOY_SAFETY_BLOCKING,
        False,
        False,
        "authoritative_db",
    ),
    (
        "groundtruth.db-wal",
        _DISPOSITION_DO_NOT_MOVE,
        "sqlite_wal_companion",
        _DEPLOY_SAFETY_BLOCKING,
        False,
        False,
        "authoritative_db",
    ),
    # §2.11 Framework root directive files
    (
        "CLAUDE.md",
        _DISPOSITION_KEEP,
        "framework_root_directive_file",
        _DEPLOY_SAFETY_NA,
        False,
        False,
        "framework_directive",
    ),
    (
        "CLAUDE-ARCHITECTURE.md",
        _DISPOSITION_KEEP,
        "framework_root_directive_file",
        _DEPLOY_SAFETY_NA,
        False,
        False,
        "framework_directive",
    ),
    (
        "CLAUDE-REFERENCE.md",
        _DISPOSITION_KEEP,
        "framework_root_directive_file",
        _DEPLOY_SAFETY_NA,
        False,
        False,
        "framework_directive",
    ),
    (
        "CLAUDE_ARCHIVE.md",
        _DISPOSITION_KEEP,
        "framework_root_directive_file",
        _DEPLOY_SAFETY_NA,
        False,
        False,
        "framework_directive",
    ),
    (
        "AGENTS.md",
        _DISPOSITION_KEEP,
        "framework_root_directive_file",
        _DEPLOY_SAFETY_NA,
        False,
        False,
        "framework_directive",
    ),
    (
        ".claude/rules/*.md",
        _DISPOSITION_KEEP,
        "framework_rule_file",
        _DEPLOY_SAFETY_NA,
        False,
        True,
        "framework_directive",
    ),
    # §2.13 Docker
    (
        "Dockerfile",
        _DISPOSITION_MOVE,
        "adopter_container_definition",
        _DEPLOY_SAFETY_BLOCKING,
        True,
        False,
        "container_definition",
    ),
    (
        "Dockerfile.ui",
        _DISPOSITION_MOVE,
        "adopter_container_definition_ui_variant",
        _DEPLOY_SAFETY_BLOCKING,
        True,
        False,
        "container_definition",
    ),
    (
        "Dockerfile.test",
        _DISPOSITION_MOVE,
        "adopter_container_definition_test_variant",
        _DEPLOY_SAFETY_AFTER_REVIEW,
        True,
        False,
        "container_definition",
    ),
    (
        ".dockerignore",
        _DISPOSITION_MOVE,
        "adopter_container_build_context_filter",
        _DEPLOY_SAFETY_BLOCKING,
        True,
        False,
        "container_definition",
    ),
    # §2.14 Shopify (in addition to §2.4)
    (
        ".shopifyignore",
        _DISPOSITION_MOVE,
        "adopter_shopify_deploy_filter",
        _DEPLOY_SAFETY_BLOCKING,
        True,
        False,
        "shopify_config",
    ),
    (
        "shopify.app.toml",
        _DISPOSITION_MOVE,
        "adopter_shopify_app_config",
        _DEPLOY_SAFETY_BLOCKING,
        True,
        False,
        "shopify_config",
    ),
    # §2.15 Deploy scripts (NOT _prod_env_vars*.txt — those are §2.1 secret-adjacent)
    (
        "scripts/deploy.py",
        _DISPOSITION_MOVE,
        "adopter_deploy_orchestrator",
        _DEPLOY_SAFETY_BLOCKING,
        True,
        False,
        "deploy_script",
    ),
    (
        "scripts/deploy_agent_containers.py",
        _DISPOSITION_MOVE,
        "adopter_deploy_containers",
        _DEPLOY_SAFETY_BLOCKING,
        True,
        False,
        "deploy_script",
    ),
    (
        "scripts/deploy_config.py",
        _DISPOSITION_MOVE,
        "adopter_deploy_config_loader",
        _DEPLOY_SAFETY_BLOCKING,
        True,
        False,
        "deploy_script",
    ),
    (
        "scripts/deploy_orchestrator.py",
        _DISPOSITION_MOVE,
        "adopter_deploy_orchestrator_v2",
        _DEPLOY_SAFETY_BLOCKING,
        True,
        False,
        "deploy_script",
    ),
    (
        "scripts/deploy_pipeline.py",
        _DISPOSITION_MOVE,
        "adopter_deploy_pipeline",
        _DEPLOY_SAFETY_BLOCKING,
        True,
        False,
        "deploy_script",
    ),
    (
        "scripts/deploy_ui.py",
        _DISPOSITION_MOVE,
        "adopter_deploy_ui",
        _DEPLOY_SAFETY_BLOCKING,
        True,
        False,
        "deploy_script",
    ),
    (
        "scripts/deploy/*.ps1",
        _DISPOSITION_MOVE,
        "adopter_deploy_powershell_scripts",
        _DEPLOY_SAFETY_BLOCKING,
        True,
        True,
        "deploy_script",
    ),
    (
        "scripts/deploy/*.md",
        _DISPOSITION_MOVE,
        "adopter_deploy_documentation",
        _DEPLOY_SAFETY_AFTER_REVIEW,
        True,
        True,
        "deploy_doc",
    ),
    (
        "scripts/deploy/api-gateway-restore.yaml",
        _DISPOSITION_MOVE,
        "adopter_deploy_restore_manifest",
        _DEPLOY_SAFETY_BLOCKING,
        True,
        False,
        "deploy_script",
    ),
    # §2.16 Terraform/infrastructure (tfvars are §2.1 secret-adjacent)
    (
        "infrastructure/terraform/*.tf",
        _DISPOSITION_MOVE,
        "adopter_terraform_definitions",
        _DEPLOY_SAFETY_BLOCKING,
        True,
        True,
        "terraform",
    ),
    (
        "infrastructure/terraform/.terraform.lock.hcl",
        _DISPOSITION_MOVE,
        "terraform_provider_lock",
        _DEPLOY_SAFETY_AFTER_REVIEW,
        True,
        False,
        "terraform",
    ),
    (
        "infrastructure/terraform/terraform.tfstate*",
        _DISPOSITION_DO_NOT_MOVE,
        "terraform_state_immovable_per_phase8_section_4",
        _DEPLOY_SAFETY_BLOCKING,
        False,
        True,
        "terraform_state",
    ),
)

# ---- Hardcoded-path scan markers (§2.15 + §2.17) ----------------------

_HARDCODED_PATH_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"E:[/\\]GT-KB[/\\]?", re.IGNORECASE),
    re.compile(r"/home/runner/work/GT-KB/?", re.IGNORECASE),
    re.compile(r"\bLEGACY_ROOT\b"),
)

# ---- Content-scan markers ---------------------------------------------

_FRAMEWORK_CONTENT_MARKERS: tuple[str, ...] = (
    "groundtruth_kb",
    "groundtruth-kb",
)


# ---- Helpers ----------------------------------------------------------


def _glob_matches(project_root: Path, pattern: str) -> list[Path]:
    """Return paths matching the relative glob pattern under project_root."""
    try:
        return sorted(project_root.glob(pattern))
    except (OSError, ValueError):
        return []


def _safe_size_bytes(path: Path) -> int:
    """Stat + return size; return 0 on error."""
    try:
        return path.stat().st_size if path.exists() else 0
    except OSError:
        return 0


def _scan_hardcoded_paths(content: str) -> list[dict[str, Any]]:
    """Find legacy-root hardcoded paths in content. Returns list of
    {line, matched_string, context}.
    """
    findings: list[dict[str, Any]] = []
    lines = content.splitlines()
    for lineno, line in enumerate(lines, start=1):
        for pattern in _HARDCODED_PATH_PATTERNS:
            for match in pattern.finditer(line):
                findings.append(
                    {
                        "line": lineno,
                        "matched_string": match.group(0),
                        "context": line.strip()[:200],
                    }
                )
    return findings


def _override_for_framework_reference(
    content: str,
    default_disposition: str,
    default_signal: str,
) -> tuple[str, str]:
    """If content references groundtruth_kb, redirect to OWNER_DECISION_REQUIRED.

    Per proposal §2.13: Docker/non-secret config files with framework
    package references are flagged for owner decision rather than
    auto-classified as adopter (the default for these surfaces).
    """
    blob = content.lower()
    if any(m in blob for m in _FRAMEWORK_CONTENT_MARKERS):
        return (
            _DISPOSITION_OWNER_DECISION,
            f"{default_signal}_with_framework_reference_owner_decision",
        )
    return (default_disposition, default_signal)


# ---- Per-category probes ----------------------------------------------


def _probe_secret_material(project_root: Path) -> list[dict[str, Any]]:
    """§2.1: secret-material surfaces. Presence/size only; never content-read.

    Per Codex GO -006 implementation constraint 1: applies to every glob
    match (not just literal filenames). E.g., scripts/deploy/_prod_env_vars*.txt
    covers _prod_env_vars.txt + _prod_env_vars_clean.txt + any future variants.
    """
    rows: list[dict[str, Any]] = []
    for relpath_or_glob, signal, is_glob in _SECRET_MATERIAL_SURFACES:
        if is_glob:
            matched = _glob_matches(project_root, relpath_or_glob)
            if not matched:
                # Record probe as absent.
                rows.append(
                    {
                        "path": relpath_or_glob,
                        "exists": False,
                        "size_bytes": 0,
                        "disposition": _DISPOSITION_DO_NOT_MOVE,
                        "signal": signal,
                        "deploy_safety": _DEPLOY_SAFETY_BLOCKING,
                        "content_read": False,
                        "category": "secret_material",
                        "match_kind": "glob_no_matches",
                    }
                )
            for path in matched:
                rel = str(path.relative_to(project_root)).replace("\\", "/")
                rows.append(
                    {
                        "path": rel,
                        "exists": True,
                        "size_bytes": _safe_size_bytes(path),
                        "disposition": _DISPOSITION_DO_NOT_MOVE,
                        "signal": signal,
                        "deploy_safety": _DEPLOY_SAFETY_BLOCKING,
                        "content_read": False,
                        "category": "secret_material",
                        "match_kind": "glob_match",
                    }
                )
        else:
            path = project_root / relpath_or_glob
            exists = path.exists()
            rows.append(
                {
                    "path": relpath_or_glob,
                    "exists": exists,
                    "size_bytes": _safe_size_bytes(path),
                    "disposition": _DISPOSITION_DO_NOT_MOVE,
                    "signal": signal,
                    "deploy_safety": _DEPLOY_SAFETY_BLOCKING,
                    "content_read": False,
                    "category": "secret_material",
                    "match_kind": "literal",
                }
            )
    return rows


def _probe_non_secret_surfaces(project_root: Path) -> list[dict[str, Any]]:
    """§2.2-§2.17 (excluding §2.1 secret material + §2.6 approval packets +
    §2.12 ACS carrier).

    Content-readable surfaces may be content-scanned for framework refs
    (override to OWNER_DECISION_REQUIRED) and for hardcoded-path findings.
    """
    rows: list[dict[str, Any]] = []
    for entry in _NON_SECRET_SURFACES:
        relpath, default_disp, default_signal, deploy_safety, content_scannable, is_glob, category = entry
        matched_paths = _glob_matches(project_root, relpath) if is_glob else [project_root / relpath]
        if is_glob and not matched_paths:
            rows.append(
                {
                    "path": relpath,
                    "exists": False,
                    "size_bytes": 0,
                    "disposition": default_disp,
                    "signal": default_signal,
                    "deploy_safety": deploy_safety,
                    "content_read": False,
                    "category": category,
                    "match_kind": "glob_no_matches",
                }
            )
            continue
        for path in matched_paths:
            rel = (
                (
                    str(path.relative_to(project_root)).replace("\\", "/")
                    if path.is_relative_to(project_root)
                    else relpath
                )
                if is_glob
                else relpath
            )
            exists = path.exists() and path.is_file()
            disposition = default_disp
            signal = default_signal
            content: str | None = None
            content_read = False
            hardcoded_findings: list[dict[str, Any]] = []
            if exists and content_scannable:
                try:
                    content = path.read_text(encoding="utf-8", errors="replace")
                    content_read = True
                except OSError:
                    content = None
                    content_read = False
            if content is not None:
                disposition, signal = _override_for_framework_reference(content, default_disp, default_signal)
                # Hardcoded-path scan (only for content-readable + scannable surfaces).
                hardcoded_findings = _scan_hardcoded_paths(content)
            row: dict[str, Any] = {
                "path": rel,
                "exists": exists,
                "size_bytes": _safe_size_bytes(path) if exists else 0,
                "disposition": disposition,
                "signal": signal,
                "deploy_safety": deploy_safety,
                "content_read": content_read,
                "category": category,
                "match_kind": "glob_match" if is_glob else "literal",
            }
            if hardcoded_findings:
                row["hardcoded_path_references"] = hardcoded_findings
            rows.append(row)
    return rows


def _probe_approval_packets(project_root: Path) -> list[dict[str, Any]]:
    """§2.6: classify each approval packet by approved-record ID prefixes.

    Reads packet structure (top-level keys + approved_records IDs) — never
    credential or token fields. Per Slice 5 lesson: classify by content
    signals, not just filename.
    """
    rows: list[dict[str, Any]] = []
    approvals_dir = project_root / ".groundtruth" / "formal-artifact-approvals"
    if not approvals_dir.exists() or not approvals_dir.is_dir():
        return rows
    for packet_path in sorted(approvals_dir.glob("*.json")):
        rel = str(packet_path.relative_to(project_root)).replace("\\", "/")
        size_bytes = _safe_size_bytes(packet_path)
        try:
            data = json.loads(packet_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            rows.append(
                {
                    "path": rel,
                    "exists": True,
                    "size_bytes": size_bytes,
                    "disposition": _DISPOSITION_OWNER_DECISION,
                    "signal": "approval_packet_unreadable",
                    "deploy_safety": _DEPLOY_SAFETY_AFTER_REVIEW,
                    "content_read": False,
                    "category": "approval_packet",
                    "match_kind": "literal",
                }
            )
            continue
        # Classify by approved_records ID prefixes (read structure only;
        # NEVER read individual approval body fields).
        approved_records = data.get("approved_records", []) if isinstance(data, dict) else []
        ids = [rec.get("id", "") for rec in approved_records if isinstance(rec, dict)]
        gtkb_count = sum(1 for i in ids if i.startswith("GTKB-"))
        ar_count = sum(1 for i in ids if i.startswith("AR-"))
        if gtkb_count > 0 and ar_count > 0:
            disposition = _DISPOSITION_OWNER_DECISION
            signal = "mixed_scope_approval_packet"
        elif ar_count > 0:
            disposition = _DISPOSITION_MOVE
            signal = "adopter_approval_packet"
        elif gtkb_count > 0:
            disposition = _DISPOSITION_KEEP
            signal = "framework_approval_packet"
        else:
            disposition = _DISPOSITION_OWNER_DECISION
            signal = "neutral_approval_packet_owner_decision"
        rows.append(
            {
                "path": rel,
                "exists": True,
                "size_bytes": size_bytes,
                "disposition": disposition,
                "signal": signal,
                "deploy_safety": _DEPLOY_SAFETY_AFTER_REVIEW,
                "content_read": True,
                "category": "approval_packet",
                "match_kind": "literal",
                "approved_record_id_prefix_counts": {
                    "GTKB": gtkb_count,
                    "AR": ar_count,
                    "other": len(ids) - gtkb_count - ar_count,
                },
            }
        )
    return rows


def _probe_github_actions_hardcoded_paths(project_root: Path) -> list[dict[str, Any]]:
    """§2.17: scan .github/workflows/*.yml for hardcoded legacy-root references.

    Complements Slice 7's CI inventory: Slice 7 classifies workflow files;
    Slice 9 catalogs production-effect implications inside their bodies.
    """
    rows: list[dict[str, Any]] = []
    workflows_dir = project_root / ".github" / "workflows"
    if not workflows_dir.exists():
        return rows
    for yml_path in sorted(workflows_dir.glob("*.yml")):
        rel = f".github/workflows/{yml_path.name}"
        try:
            content = yml_path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        findings = _scan_hardcoded_paths(content)
        if findings:
            rows.append(
                {
                    "path": rel,
                    "exists": True,
                    "size_bytes": _safe_size_bytes(yml_path),
                    "disposition": _DISPOSITION_OWNER_DECISION,
                    "signal": "github_actions_hardcoded_path_owner_decision",
                    "deploy_safety": _DEPLOY_SAFETY_AFTER_REVIEW,
                    "content_read": True,
                    "category": "github_actions_workflow_with_hardcoded_paths",
                    "match_kind": "literal",
                    "hardcoded_path_references": findings,
                }
            )
    return rows


# ---- Emitters ---------------------------------------------------------


def _emit_json(rows: list[dict[str, Any]], warnings: list[str], output_path: Path) -> None:
    """Emit production_effects.json companion."""
    summary = {
        "total_surfaces": len(rows),
        "move_count": sum(1 for r in rows if r["disposition"] == _DISPOSITION_MOVE),
        "keep_count": sum(1 for r in rows if r["disposition"] == _DISPOSITION_KEEP),
        "do_not_move_count": sum(1 for r in rows if r["disposition"] == _DISPOSITION_DO_NOT_MOVE),
        "owner_decision_required_count": sum(1 for r in rows if r["disposition"] == _DISPOSITION_OWNER_DECISION),
        "deploy_blocking_count": sum(1 for r in rows if r["deploy_safety"] == _DEPLOY_SAFETY_BLOCKING),
        "secret_material_count": sum(1 for r in rows if r["category"] == "secret_material"),
        "secret_material_with_content_read": sum(
            1 for r in rows if r["category"] == "secret_material" and r.get("content_read")
        ),
    }
    payload = {
        "schema_version": 1,
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "summary": summary,
        "surfaces": rows,
        "warnings": warnings,
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _emit_preview_markdown(rows: list[dict[str, Any]], output_path: Path) -> None:
    """Emit production-effects-map.md grouped by disposition + deploy_safety."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    timestamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    do_not_move = [r for r in rows if r["disposition"] == _DISPOSITION_DO_NOT_MOVE]
    keep = [r for r in rows if r["disposition"] == _DISPOSITION_KEEP]
    move = [r for r in rows if r["disposition"] == _DISPOSITION_MOVE]
    decide = [r for r in rows if r["disposition"] == _DISPOSITION_OWNER_DECISION]
    deploy_blocking = [r for r in rows if r["deploy_safety"] == _DEPLOY_SAFETY_BLOCKING]
    deploy_after_review = [r for r in rows if r["deploy_safety"] == _DEPLOY_SAFETY_AFTER_REVIEW]
    lines: list[str] = [
        "# Production Effects Map\n",
        "\n",
        f"Generated: {timestamp}\n",
        "Source: GTKB-ISOLATION-016 Phase 8 rehearsal `_production_effects.py` (Slice 9).\n",
        "\n",
        "## Summary\n",
        "\n",
        f"- Total surfaces probed: {len(rows)}\n",
        f"- MOVE: {len(move)}\n",
        f"- KEEP: {len(keep)}\n",
        f"- DO_NOT_MOVE: {len(do_not_move)}\n",
        f"- OWNER_DECISION_REQUIRED: {len(decide)}\n",
        f"- deploy-blocking: {len(deploy_blocking)}\n",
        f"- deploy-safe-after-review: {len(deploy_after_review)}\n",
        "\n",
        "## DO_NOT_MOVE (Phase 8 plan §4 explicit immovables + secret-adjacent)\n",
        "\n",
    ]
    for r in do_not_move:
        present = " present" if r["exists"] else " absent"
        lines.append(f"- `{r['path']}`{present} — signal: `{r['signal']}` — content_read: `{r['content_read']}`\n")
    if not do_not_move:
        lines.append("- (none)\n")

    lines.extend(["\n", "## MOVE (relocate to applications/Agent_Red/<path>)\n", "\n"])
    for r in move:
        target = f"applications/Agent_Red/{r['path']}"
        lines.append(f"- `{r['path']}` → `{target}` — signal: `{r['signal']}`\n")
    if not move:
        lines.append("- (none)\n")

    lines.extend(["\n", "## KEEP (stays at GT-KB root post-cutover)\n", "\n"])
    for r in keep:
        lines.append(f"- `{r['path']}` — signal: `{r['signal']}`\n")
    if not keep:
        lines.append("- (none)\n")

    lines.extend(["\n", "## OWNER_DECISION_REQUIRED\n", "\n"])
    for r in decide:
        lines.append(f"- `{r['path']}` — signal: `{r['signal']}`\n")
    if not decide:
        lines.append("- (none)\n")

    lines.extend(["\n", "## Deploy-Blocking Surfaces (require pre-cutover verification)\n", "\n"])
    for r in deploy_blocking:
        lines.append(f"- `{r['path']}` — disposition: `{r['disposition']}`; signal: `{r['signal']}`\n")
    if not deploy_blocking:
        lines.append("- (none)\n")

    output_path.write_text("".join(lines), encoding="utf-8")


# ---- Entry point ------------------------------------------------------


def run(
    manifest: dict[str, Any],
    output_dir: Path,
    *,
    dry_run: bool = False,
    project_root: Path | None = None,
) -> dict[str, Any]:
    """Wave 2 Stage B leaf lane. Per common contract Wave 2 -003 §4.1.

    ``project_root`` overrides ``LEGACY_ROOT`` for fixture trees.
    """
    if dry_run:
        return {
            "status": "skipped",
            "output_files": [],
            "metrics": {"reason": "dry_run"},
            "warnings": [],
        }

    root = project_root if project_root is not None else LEGACY_ROOT
    lane_dir = output_dir / "production_effects"
    lane_dir.mkdir(parents=True, exist_ok=True)

    warnings: list[str] = []
    output_files: list[Path] = []

    try:
        rows: list[dict[str, Any]] = []
        rows.extend(_probe_secret_material(root))
        rows.extend(_probe_non_secret_surfaces(root))
        rows.extend(_probe_approval_packets(root))
        rows.extend(_probe_github_actions_hardcoded_paths(root))
    except OSError as exc:
        return emit_result(
            lane_dir,
            {
                "status": "error",
                "output_files": [str(p) for p in output_files],
                "metrics": {},
                "warnings": [f"probe_failed: {exc}"],
            },
        )

    json_path = lane_dir / "production_effects.json"
    preview_path = lane_dir / "production-effects-map.md"
    _emit_json(rows, warnings, json_path)
    output_files.append(json_path)
    _emit_preview_markdown(rows, preview_path)
    output_files.append(preview_path)

    metrics = {
        "total_surfaces": len(rows),
        "move_count": sum(1 for r in rows if r["disposition"] == _DISPOSITION_MOVE),
        "keep_count": sum(1 for r in rows if r["disposition"] == _DISPOSITION_KEEP),
        "do_not_move_count": sum(1 for r in rows if r["disposition"] == _DISPOSITION_DO_NOT_MOVE),
        "owner_decision_required_count": sum(1 for r in rows if r["disposition"] == _DISPOSITION_OWNER_DECISION),
        "secret_material_count": sum(1 for r in rows if r["category"] == "secret_material"),
        "secret_material_with_content_read": sum(
            1 for r in rows if r["category"] == "secret_material" and r.get("content_read")
        ),
    }

    return emit_result(
        lane_dir,
        {
            "status": "ok",
            "output_files": [str(p) for p in output_files],
            "metrics": metrics,
            "warnings": warnings,
        },
    )
