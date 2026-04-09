# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""SPEC-1844: Line Coverage Enforcement and Per-Module Tracking.

Parses coverage.py JSON reports, computes per-module line/branch
coverage, identifies bottom modules, tracks deltas across sessions,
and detects per-module regressions.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


def parse_coverage_json(coverage_data: dict[str, Any]) -> list[dict[str, Any]]:
    """Parse a coverage.py JSON report into per-module summaries.

    Args:
        coverage_data: Parsed JSON from coverage.py's JSON reporter
            (``coverage json`` output).

    Returns:
        List of dicts, each with:
            - module: file path (e.g. "src/multi_tenant/auth.py")
            - line_coverage: percentage of statements covered
            - branch_coverage: percentage of branches covered (0.0 if no branches)
            - covered_lines: int
            - num_statements: int
            - covered_branches: int
            - num_branches: int
    """
    files = coverage_data.get("files", {})
    modules: list[dict[str, Any]] = []

    for filepath, file_data in files.items():
        summary = file_data.get("summary", {})

        num_statements = summary.get("num_statements", 0)
        covered_lines = summary.get("covered_lines", 0)
        line_pct = summary.get("percent_covered", 0.0)

        num_branches = summary.get("num_branches", 0)
        covered_branches = summary.get("covered_branches", 0)
        branch_pct = (covered_branches / num_branches * 100) if num_branches > 0 else 0.0

        modules.append({
            "module": filepath,
            "line_coverage": line_pct,
            "branch_coverage": round(branch_pct, 1),
            "covered_lines": covered_lines,
            "num_statements": num_statements,
            "covered_branches": covered_branches,
            "num_branches": num_branches,
        })

    return modules


def get_bottom_modules(
    modules: list[dict[str, Any]],
    n: int = 5,
    key: str = "line_coverage",
) -> list[dict[str, Any]]:
    """Return the N modules with the lowest coverage.

    Args:
        modules: Output of parse_coverage_json().
        n: Number of bottom modules to return.
        key: Coverage metric to sort by (default: line_coverage).

    Returns:
        Sorted list (lowest first) of the bottom N modules.
    """
    sorted_modules = sorted(modules, key=lambda m: m.get(key, 0))
    return sorted_modules[:n]


def compute_coverage_delta(
    previous: dict[str, Any],
    current: dict[str, Any],
) -> float:
    """Compute the global line coverage delta between two snapshots.

    Args:
        previous: Dict with "global_line_coverage" float.
        current: Dict with "global_line_coverage" float.

    Returns:
        Delta as a float (positive = improvement, negative = regression).
    """
    prev = previous.get("global_line_coverage", 0.0)
    curr = current.get("global_line_coverage", 0.0)
    return round(curr - prev, 2)


def check_module_regression(
    previous_modules: list[dict[str, Any]],
    current_modules: list[dict[str, Any]],
    threshold: float = 2.0,
) -> list[dict[str, Any]]:
    """Detect modules whose coverage dropped more than threshold.

    Args:
        previous_modules: Per-module coverage from the previous session.
        current_modules: Per-module coverage from the current session.
        threshold: Maximum allowed drop in percentage points.

    Returns:
        List of dicts with "module", "previous", "current", and "drop"
        for each module that regressed beyond the threshold.
    """
    prev_map = {m["module"]: m["line_coverage"] for m in previous_modules}
    regressions: list[dict[str, Any]] = []

    for mod in current_modules:
        module_name = mod["module"]
        current_cov = mod["line_coverage"]
        previous_cov = prev_map.get(module_name)

        if previous_cov is None:
            continue  # New module, no baseline to compare

        drop = round(previous_cov - current_cov, 2)
        if drop > threshold:
            regressions.append({
                "module": module_name,
                "previous": previous_cov,
                "current": current_cov,
                "drop": drop,
            })

    return sorted(regressions, key=lambda r: r["drop"], reverse=True)


def load_module_targets(
    path: str | Path | None = None,
) -> dict[str, Any]:
    """Load per-module coverage targets from JSON config (WI-1487).

    Args:
        path: Path to module_coverage_targets.json. Defaults to the
              bundled config in src/quality_metrics/.

    Returns:
        Parsed targets config dict.
    """
    if path is None:
        path = Path(__file__).parent / "module_coverage_targets.json"
    p = Path(path)
    if not p.exists():
        logger.warning("Module coverage targets not found: %s", p)
        return {"targets": {}, "global": {"target_pct": 80, "current_gate_pct": 75}}
    return json.loads(p.read_text(encoding="utf-8"))


def check_module_targets(
    modules: list[dict[str, Any]],
    targets: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    """Check modules against per-tier coverage targets (WI-1487).

    Args:
        modules: Output of parse_coverage_json().
        targets: Loaded module targets config. If None, loads from default.

    Returns:
        List of dicts with "module", "coverage", "tier", "target",
        "below_target" for each module that's below its tier target.
    """
    if targets is None:
        targets = load_module_targets()

    tier_configs = targets.get("targets", {})
    violations: list[dict[str, Any]] = []

    for mod in modules:
        module_path = mod["module"]
        tier_name, tier_target = _classify_module_tier(module_path, tier_configs)

        if mod["line_coverage"] < tier_target:
            violations.append({
                "module": module_path,
                "coverage": mod["line_coverage"],
                "tier": tier_name,
                "target": tier_target,
                "below_target": round(tier_target - mod["line_coverage"], 1),
            })

    return sorted(violations, key=lambda v: v["below_target"], reverse=True)


def _classify_module_tier(
    module_path: str,
    tier_configs: dict[str, Any],
) -> tuple[str, float]:
    """Classify a module into a coverage tier and return (tier_name, target_pct)."""
    for tier_name in ["critical", "high", "medium", "low"]:
        tier = tier_configs.get(tier_name, {})
        for prefix in tier.get("modules", []):
            if module_path.startswith(prefix) or module_path.startswith(prefix.replace("/", "\\")):
                return tier_name, tier.get("target_pct", 70)

    # Default: medium tier target
    return "unclassified", tier_configs.get("medium", {}).get("target_pct", 70)


def format_coverage_display(
    modules: list[dict[str, Any]],
    previous_modules: list[dict[str, Any]] | None = None,
    n: int = 5,
) -> str:
    """Format bottom N modules for session-start display (WI-1488).

    Returns a formatted string with module names, coverage %, and delta arrows.
    """
    bottom = get_bottom_modules(modules, n=n)
    prev_map = {m["module"]: m["line_coverage"] for m in (previous_modules or [])}

    lines = [f"Bottom {n} modules by line coverage:"]
    for mod in bottom:
        module_name = mod["module"]
        pct = mod["line_coverage"]
        prev = prev_map.get(module_name)

        if prev is not None:
            delta = pct - prev
            if delta > 0.5:
                arrow = "^"
            elif delta < -0.5:
                arrow = "v"
            else:
                arrow = "="
            lines.append(f"  {module_name}: {pct:.1f}% ({arrow} {delta:+.1f}%)")
        else:
            lines.append(f"  {module_name}: {pct:.1f}% (new)")

    return "\n".join(lines)


def load_coverage_json(path: str | Path = "coverage.json") -> dict[str, Any]:
    """Load a coverage.py JSON report from disk.

    Args:
        path: Path to the coverage JSON file.

    Returns:
        Parsed JSON data.

    Raises:
        FileNotFoundError: If the coverage file doesn't exist.
    """
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Coverage report not found: {p}")
    return json.loads(p.read_text(encoding="utf-8"))
