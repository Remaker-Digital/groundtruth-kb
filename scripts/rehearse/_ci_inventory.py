"""Wave 2 lane 3 (Stage B leaf): CI surface inventory + cutover preview.

Per ``bridge/gtkb-isolation-016-phase8-wave2-slice7-003.md`` (REVISED-1)
and ``-004`` (Codex GO).

Inventories ``.github/workflows/*.yml`` plus a fixed roster of root-level
CI configuration files. Each surface is classified ``framework`` /
``adopter`` / ``unclassified`` by filename rule (highest priority) +
content-scan fallback. Per GO ``-004``: ``release-candidate-gate.yml``
inherits Slice 6's adopter classification verbatim, including the
``mechanism_origin = "agent_red_local"`` value (cross-slice consistency).

Outputs:
  - ``ci-command-inventory.csv`` (Phase 8 plan §2 named artifact)
  - ``ci-rewrite-preview.md`` (Phase 8 plan §2 named artifact)
  - ``ci_inventory.json`` (machine-readable companion)
  - ``result.json`` (standard sub-script result envelope)
"""

from __future__ import annotations

import csv
import io
import json
import re
import time
from pathlib import Path
from typing import Any

from rehearse._common import LEGACY_ROOT
from rehearse._split_helper import emit_result

# ---- Source set --------------------------------------------------------

# Filename rules in declaration order; first match wins.
# Format: (regex_or_literal, classification, signal, mechanism_origin)
# release-candidate-gate.yml mirrors Slice 6's _RELEASE_GATE_SURFACES
# entry exactly (per Codex GO -004 cross-slice consistency constraint).
_FILENAME_RULES: tuple[tuple[re.Pattern[str], str, str, str | None], ...] = (
    (
        re.compile(r"^release-candidate-gate\.yml$"),
        "adopter",
        "application_release_gate_surface",
        "agent_red_local",
    ),
    (
        re.compile(r"^(build|deploy)-(agent|api-gateway|slim-gateway|test-host).*\.yml$"),
        "adopter",
        "application_build_or_deploy_workflow",
        None,
    ),
    (
        re.compile(r"^(accessibility|chromatic|visual-regression)\.yml$"),
        "adopter",
        "application_ui_gate_workflow",
        None,
    ),
    (
        re.compile(r"^(deploy-docs|docs-quality)\.yml$"),
        "adopter",
        "application_docs_workflow",
        None,
    ),
    (
        re.compile(r"^dependabot\.yml$"),
        "adopter",
        "application_dependabot_config",
        None,
    ),
)

# CI configuration files at known root-relative locations.
_CI_CONFIG_PROBES: tuple[tuple[str, str, str], ...] = (
    # (relative_path, classification, signal)
    ("sonar-project.properties", "adopter", "agent_red_sonar_config"),
    (".coderabbit.yaml", "adopter", "adopter_coderabbit_config"),
    (".coderabbit.yml", "adopter", "adopter_coderabbit_config"),
    (".pre-commit-config.yaml", "adopter", "adopter_precommit_config"),
    ("pytest.ini", "adopter", "adopter_pytest_config"),
    ("pyproject.toml", "adopter", "adopter_pyproject_config_presence_only"),
    (".github/dependabot.yml", "adopter", "application_dependabot_config"),
)

# Content-scan markers (case-insensitive substring match).
_FRAMEWORK_CONTENT_MARKERS: tuple[str, ...] = (
    "groundtruth_kb",
    "groundtruth-kb",
)
_ADOPTER_CONTENT_MARKERS: tuple[str, ...] = (
    "src/",
    "admin-spa/",
    "transport-tests/",
    "mike-remakerdigital_agent-red",
)
# Workflows known to be mixed-scope (force unclassified for owner decision).
_MIXED_SCOPE_WORKFLOWS: frozenset[str] = frozenset({"lint.yml"})


# ---- Classifiers -------------------------------------------------------


def _apply_filename_rules(
    filename: str,
) -> tuple[str | None, str | None, str | None]:
    """Return (classification, signal, mechanism_origin) or (None, None, None) if no rule matches."""
    for pattern, classification, signal, mechanism_origin in _FILENAME_RULES:
        if pattern.match(filename):
            return (classification, signal, mechanism_origin)
    return (None, None, None)


def _content_scan(content: str) -> tuple[str | None, str | None]:
    """Return (classification, signal) by content markers, or (None, None) if no signal."""
    blob = content.lower()
    has_framework = any(m in blob for m in _FRAMEWORK_CONTENT_MARKERS)
    has_adopter = any(m in blob for m in _ADOPTER_CONTENT_MARKERS)
    if has_framework and has_adopter:
        return ("unclassified", "mixed_scope_owner_decision_required")
    if has_framework:
        return ("framework", "groundtruth_kb_reference")
    if has_adopter:
        return ("adopter", "agent_red_source_reference")
    return (None, None)


def _extract_pytest_targets(content_lower: str) -> list[str]:
    """Extract pytest target subpaths from a workflow file's content.

    Handles two patterns observed in live + synthetic workflows:
      - Literal command: ``pytest tests/<subpath>`` (or ``python -m pytest tests/...``)
      - GitHub Actions output forwarding (live python-tests.yml pattern at
        S313): ``test_args=tests/<subpath> [tests/<subpath2> ...]`` written
        to ``$GITHUB_OUTPUT``, then consumed via
        ``python -m pytest ${{ steps.paths.outputs.test_args }}``.

    Returns a list of subpaths after ``tests/``. Empty list means no
    pytest target was found in either pattern.
    """
    targets: list[str] = []
    # Pattern A: literal `pytest tests/<subpath>` (covers `pytest`,
    # `python -m pytest`, etc.)
    targets.extend(re.findall(r"pytest\s+tests/(\S*)", content_lower))
    # Pattern B: GHA `test_args=tests/<subpath> [tests/<subpath2> ...]`
    # The right-hand side may contain multiple space-separated tokens.
    # Stop the assignment value at quote, newline, or `>>` (redirection).
    for assignment in re.findall(r"test_args=([^\"'\n>]*)", content_lower):
        for token in assignment.split():
            if token.startswith("tests/"):
                targets.append(token[len("tests/") :])
    return targets


def _classify_python_tests_workflow(content: str) -> tuple[str, str, str | None]:
    """Classify python-tests.yml by its pytest target paths.

    Per proposal -001 §3 specific call:
      - pytest tests/groundtruth_kb/  → framework
      - pytest tests/<other> → adopter
      - both → unclassified (mixed_scope_pytest_owner_decision_required)

    Per Codex S313 -010 NO-GO: covers both literal ``pytest tests/...``
    invocations AND the GHA ``test_args=tests/...`` output-forwarding
    pattern used in the live workflow.
    """
    targets = _extract_pytest_targets(content.lower())
    framework_targets = [t for t in targets if t.startswith("groundtruth_kb")]
    adopter_targets = [t for t in targets if not t.startswith("groundtruth_kb")]
    if framework_targets and adopter_targets:
        return ("unclassified", "mixed_scope_pytest_owner_decision_required", None)
    if framework_targets:
        return ("framework", "framework_pytest_workflow", None)
    if adopter_targets:
        return ("adopter", "agent_red_pytest_workflow", None)
    return ("unclassified", "no_classification_signal", None)


def _classify_workflow(
    filename: str,
    content: str,
) -> tuple[str, str, str | None]:
    """Classify a workflow file. Returns (classification, signal, mechanism_origin)."""
    if filename in _MIXED_SCOPE_WORKFLOWS:
        return ("unclassified", "mixed_scope_linter_owner_decision_required", None)
    if filename == "python-tests.yml":
        return _classify_python_tests_workflow(content)
    classification, signal, mechanism_origin = _apply_filename_rules(filename)
    if classification is not None:
        return (classification, signal or "filename_rule", mechanism_origin)
    # Filename rule did not match; fall back to content scan.
    cs_classification, cs_signal = _content_scan(content)
    if cs_classification is not None:
        return (cs_classification, cs_signal or "content_scan", None)
    return ("unclassified", "no_classification_signal", None)


def _classify_ci_config(
    relative_path: str,
    default_classification: str,
    default_signal: str,
    content: str | None,
) -> tuple[str, str]:
    """Classify a CI config file. Content scan can override the default."""
    if content is None:
        return (default_classification, default_signal)
    cs_classification, cs_signal = _content_scan(content)
    if cs_classification == "framework":
        # Framework-scoped CI config flagged for owner decision rather than
        # auto-reclassification. The default (adopter) is the safer base
        # for root config files; framework reference is non-obvious.
        return ("unclassified", "ci_config_with_framework_reference")
    return (default_classification, default_signal)


# ---- Cross-reference helper -------------------------------------------


def _load_path_rewrite_classification(output_dir: Path) -> dict[str, str]:
    """Load Slice 4's per-path ownership map, if present in same output dir."""
    classification_path = output_dir / "path_rewrite" / "classification.json"
    if not classification_path.exists():
        return {}
    try:
        data = json.loads(classification_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    rows = data.get("rows", []) if isinstance(data, dict) else []
    return {row["path"]: row.get("ownership", "") for row in rows if isinstance(row, dict) and "path" in row}


# ---- Probes ------------------------------------------------------------


def _is_path_excluded_by_manifest(
    relative_path: str,
    excluded_top: frozenset[str],
    excluded_full: frozenset[str],
) -> bool:
    """Return True when the relative path is covered by manifest excluded_paths.

    Per proposal -001 §6.6 (common contract): lane consumes manifest's
    excluded_paths to skip surfaces under excluded top-level roots.

    Two match modes:
      - Top-level dir match: relative_path's first segment is in
        excluded_top (e.g., '.github' excludes '.github/workflows/x.yml').
      - Full-path match: relative_path is exactly in excluded_full
        (e.g., 'sonar-project.properties' explicitly excluded).
    """
    if relative_path in excluded_full:
        return True
    top = relative_path.split("/", 1)[0]
    return top in excluded_top


def _probe_workflows(
    ci_root: Path,
    classify_tree_lookup: dict[str, str],
    excluded_top: frozenset[str] = frozenset(),
    excluded_full: frozenset[str] = frozenset(),
) -> list[dict[str, Any]]:
    """Walk .github/workflows/*.yml; classify each.

    Workflows under excluded top-level dirs (e.g., manifest excludes
    '.github') are skipped entirely per the common contract.
    """
    rows: list[dict[str, Any]] = []
    if not ci_root.exists() or not ci_root.is_dir():
        return rows
    for yml_path in sorted(ci_root.glob("*.yml")):
        rel = f".github/workflows/{yml_path.name}"
        if _is_path_excluded_by_manifest(rel, excluded_top, excluded_full):
            continue
        try:
            size_bytes = yml_path.stat().st_size
            content = yml_path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            rows.append(
                {
                    "path": rel,
                    "type": "workflow",
                    "classification": "unclassified",
                    "classification_signal": "read_failure",
                    "mechanism_origin": None,
                    "size_bytes": 0,
                    "exists": False,
                    "gt_classify_tree_ownership": classify_tree_lookup.get(rel, ""),
                }
            )
            continue
        classification, signal, mechanism_origin = _classify_workflow(yml_path.name, content)
        rows.append(
            {
                "path": rel,
                "type": "workflow",
                "classification": classification,
                "classification_signal": signal,
                "mechanism_origin": mechanism_origin,
                "size_bytes": size_bytes,
                "exists": True,
                "gt_classify_tree_ownership": classify_tree_lookup.get(rel, ""),
            }
        )
    return rows


def _probe_ci_configs(
    project_root: Path,
    classify_tree_lookup: dict[str, str],
    excluded_top: frozenset[str] = frozenset(),
    excluded_full: frozenset[str] = frozenset(),
) -> list[dict[str, Any]]:
    """Probe known root-relative CI config paths.

    Configs whose path is manifest-excluded (top-level dir match or full
    path match) are skipped entirely.
    """
    rows: list[dict[str, Any]] = []
    for relative_path, default_classification, default_signal in _CI_CONFIG_PROBES:
        if _is_path_excluded_by_manifest(relative_path, excluded_top, excluded_full):
            continue
        full = project_root / relative_path
        exists = full.exists() and full.is_file()
        size_bytes = 0
        content: str | None = None
        if exists:
            try:
                size_bytes = full.stat().st_size
                # Skip body parse for pyproject.toml (presence-only per -001 §2.2).
                if relative_path != "pyproject.toml":
                    content = full.read_text(encoding="utf-8", errors="replace")
            except OSError:
                exists = False
        if not exists:
            classification = "unclassified"
            signal = "absent_probed"
        else:
            classification, signal = _classify_ci_config(relative_path, default_classification, default_signal, content)
        rows.append(
            {
                "path": relative_path,
                "type": "ci_config",
                "classification": classification,
                "classification_signal": signal,
                "mechanism_origin": None,
                "size_bytes": size_bytes,
                "exists": exists,
                "gt_classify_tree_ownership": classify_tree_lookup.get(relative_path, ""),
            }
        )
    return rows


# ---- Emitters ----------------------------------------------------------


_CSV_COLUMNS: tuple[str, ...] = (
    "path",
    "type",
    "classification",
    "classification_signal",
    "mechanism_origin",
    "size_bytes",
    "exists",
    "gt_classify_tree_ownership",
)


def _emit_csv(rows: list[dict[str, Any]], output_path: Path) -> None:
    """Emit ci-command-inventory.csv with a stable column order."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=list(_CSV_COLUMNS))
    writer.writeheader()
    for row in rows:
        writer.writerow({col: row.get(col, "") if row.get(col) is not None else "" for col in _CSV_COLUMNS})
    output_path.write_text(buffer.getvalue(), encoding="utf-8")


def _emit_preview_markdown(
    workflows: list[dict[str, Any]],
    ci_configs: list[dict[str, Any]],
    output_path: Path,
) -> None:
    """Emit ci-rewrite-preview.md with three disposition sections."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    all_rows = list(workflows) + list(ci_configs)
    move_rows = [r for r in all_rows if r["classification"] == "adopter" and r["exists"]]
    keep_rows = [r for r in all_rows if r["classification"] == "framework" and r["exists"]]
    decide_rows = [r for r in all_rows if r["classification"] == "unclassified"]

    timestamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    lines: list[str] = [
        "# CI Surface Cutover Preview\n",
        "\n",
        f"Generated: {timestamp}\n",
        "Source: GTKB-ISOLATION-016 Phase 8 rehearsal `_ci_inventory.py` (Slice 7).\n",
        "\n",
        "## Summary\n",
        "\n",
        f"- Workflow files: {len(workflows)} ({len(move_rows)} adopter / {len(keep_rows)} framework / {sum(1 for r in workflows if r['classification'] == 'unclassified')} unclassified)\n",
        f"- CI config files probed: {len(ci_configs)} ({sum(1 for r in ci_configs if r['exists'])} present / {sum(1 for r in ci_configs if not r['exists'])} absent)\n",
        f"- Owner decisions required: {len(decide_rows)} rows\n",
        "\n",
        "## Move to `applications/Agent_Red/<path>` (adopter)\n",
        "\n",
    ]
    for row in move_rows:
        target = f"applications/Agent_Red/{row['path']}"
        mech = f"; mechanism_origin: `{row['mechanism_origin']}`" if row.get("mechanism_origin") else ""
        lines.append(f"- `{row['path']}` → `{target}` — signal: `{row['classification_signal']}`{mech}\n")
    if not move_rows:
        lines.append("- (none)\n")

    lines.extend(["\n", "## Keep at GT-KB root (framework)\n", "\n"])
    for row in keep_rows:
        lines.append(f"- `{row['path']}` — signal: `{row['classification_signal']}`\n")
    if not keep_rows:
        lines.append("- (none)\n")

    lines.extend(["\n", "## Owner decision required (unclassified)\n", "\n"])
    for row in decide_rows:
        present = " (present)" if row["exists"] else " (absent — probe-only)"
        lines.append(f"- `{row['path']}`{present} — signal: `{row['classification_signal']}`\n")
    if not decide_rows:
        lines.append("- (none)\n")

    output_path.write_text("".join(lines), encoding="utf-8")


def _emit_json(
    workflows: list[dict[str, Any]],
    ci_configs: list[dict[str, Any]],
    warnings: list[str],
    output_path: Path,
) -> None:
    """Emit ci_inventory.json companion with per-row schema."""
    all_rows = list(workflows) + list(ci_configs)
    payload = {
        "schema_version": 1,
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "summary": {
            "workflow_count": len(workflows),
            "ci_config_count": len(ci_configs),
            "framework_count": sum(1 for r in all_rows if r["classification"] == "framework"),
            "adopter_count": sum(1 for r in all_rows if r["classification"] == "adopter"),
            "unclassified_count": sum(1 for r in all_rows if r["classification"] == "unclassified"),
            "absent_probed_count": sum(1 for r in ci_configs if not r["exists"]),
            "owner_decisions_required": sum(1 for r in all_rows if r["classification"] == "unclassified"),
        },
        "workflows": workflows,
        "ci_configs": ci_configs,
        "warnings": warnings,
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


# ---- Entry point -------------------------------------------------------


def run(
    manifest: dict[str, Any],
    output_dir: Path,
    *,
    dry_run: bool = False,
    ci_root: Path | None = None,
    ci_configs_root: Path | None = None,
) -> dict[str, Any]:
    """Wave 2 Stage B leaf lane. Per common contract Wave 2 -003 §4.1.

    ``ci_root`` overrides ``LEGACY_ROOT/.github/workflows`` for fixture trees.
    ``ci_configs_root`` overrides ``LEGACY_ROOT`` for the root-level CI
    configuration probes.
    """
    if dry_run:
        return {
            "status": "skipped",
            "output_files": [],
            "metrics": {"reason": "dry_run"},
            "warnings": [],
        }

    workflows_root = ci_root if ci_root is not None else (LEGACY_ROOT / ".github" / "workflows")
    project_root = ci_configs_root if ci_configs_root is not None else LEGACY_ROOT

    classify_tree_lookup = _load_path_rewrite_classification(output_dir)
    warnings: list[str] = []
    output_files: list[Path] = []

    # Per common contract -001 §6.6: consume manifest['excluded_paths'].
    excluded = set(manifest.get("excluded_paths", []))
    excluded_full = frozenset(excluded)
    excluded_top = frozenset(e.rstrip("/").split("/")[0] for e in excluded if e)

    lane_dir = output_dir / "ci_inventory"
    lane_dir.mkdir(parents=True, exist_ok=True)
    try:
        workflows = _probe_workflows(workflows_root, classify_tree_lookup, excluded_top, excluded_full)
        ci_configs = _probe_ci_configs(project_root, classify_tree_lookup, excluded_top, excluded_full)
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

    csv_path = lane_dir / "ci-command-inventory.csv"
    preview_path = lane_dir / "ci-rewrite-preview.md"
    json_path = lane_dir / "ci_inventory.json"

    _emit_csv(workflows + ci_configs, csv_path)
    output_files.append(csv_path)
    _emit_preview_markdown(workflows, ci_configs, preview_path)
    output_files.append(preview_path)
    _emit_json(workflows, ci_configs, warnings, json_path)
    output_files.append(json_path)

    all_rows = list(workflows) + list(ci_configs)
    metrics = {
        "workflow_count": len(workflows),
        "ci_config_count": len(ci_configs),
        "framework_count": sum(1 for r in all_rows if r["classification"] == "framework"),
        "adopter_count": sum(1 for r in all_rows if r["classification"] == "adopter"),
        "unclassified_count": sum(1 for r in all_rows if r["classification"] == "unclassified"),
        "cross_reference_loaded": bool(classify_tree_lookup),
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
