"""SPEC-1842/WI-1498: Mutation score tracking and oracle gap detection.

Parses mutmut results, computes mutation scores, and identifies modules
where high code coverage masks weak test assertions (the "oracle gap").
See arXiv:2309.02395 and GOV-18.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""
from __future__ import annotations

import re
from typing import Any


def parse_mutmut_results(mutmut_output: str) -> dict[str, int]:
    """Parse mutmut results text into structured counts.

    Accepts the output of `mutmut results` or the summary line from
    `mutmut run`, e.g.:
      "282 mutants were generated. Of those, 200 were killed, 70 survived,
       and 12 timed out."

    Returns:
        Dict with keys: killed, survived, timeout, total.
    """
    killed = 0
    survived = 0
    timeout = 0

    # Match summary line format
    killed_match = re.search(r"(\d+)\s+(?:were\s+)?killed", mutmut_output, re.IGNORECASE)
    survived_match = re.search(r"(\d+)\s+survived", mutmut_output, re.IGNORECASE)
    timeout_match = re.search(r"(\d+)\s+timed?\s*out", mutmut_output, re.IGNORECASE)

    if killed_match:
        killed = int(killed_match.group(1))
    if survived_match:
        survived = int(survived_match.group(1))
    if timeout_match:
        timeout = int(timeout_match.group(1))

    return {
        "killed": killed,
        "survived": survived,
        "timeout": timeout,
        "total": killed + survived + timeout,
    }


def compute_mutation_score(killed: int, survived: int, timeout: int = 0) -> float:
    """Mutation score = killed / (killed + survived).

    Timeout mutants are excluded from the denominator (they are inconclusive).

    Returns 0.0-1.0. Returns 0.0 if no mutants were generated.
    """
    total = killed + survived
    if total == 0:
        return 0.0
    return round(killed / total, 4)


def identify_oracle_gap_modules(
    coverage_data: dict[str, float],
    mutation_data: dict[str, float],
    coverage_threshold: float = 0.80,
    mutation_threshold: float = 0.50,
) -> list[dict[str, Any]]:
    """Identify modules with high coverage but low mutation score.

    These are the "oracle gap" modules — tests that execute code but don't
    assert meaningful outcomes. See arXiv:2309.02395 and GOV-18.

    Args:
        coverage_data: Dict mapping module path → branch coverage (0.0-1.0).
        mutation_data: Dict mapping module path → mutation score (0.0-1.0).
        coverage_threshold: Minimum branch coverage to consider (default 80%).
        mutation_threshold: Maximum mutation score to flag (default 50%).

    Returns:
        List of dicts with module, branch_coverage, mutation_score, oracle_gap,
        sorted by oracle_gap descending (worst first).
    """
    gap_modules = []
    for module, branch_cov in coverage_data.items():
        mutation_score = mutation_data.get(module, 0.0)
        if branch_cov >= coverage_threshold and mutation_score < mutation_threshold:
            gap_modules.append({
                "module": module,
                "branch_coverage": round(branch_cov, 4),
                "mutation_score": round(mutation_score, 4),
                "oracle_gap": round(branch_cov - mutation_score, 4),
            })
    return sorted(gap_modules, key=lambda x: x["oracle_gap"], reverse=True)


def format_mutation_summary(results: dict[str, int], score: float) -> str:
    """Format mutation results for display in quality dashboard.

    Returns a human-readable summary string.
    """
    return (
        f"Mutation score: {score:.1%} "
        f"({results['killed']} killed, {results['survived']} survived, "
        f"{results['timeout']} timed out of {results['total']} mutants)"
    )
