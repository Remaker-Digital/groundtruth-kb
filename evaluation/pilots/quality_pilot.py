"""CQ-2: Phase 0 Quality Pilot — Faithfulness & Answer Relevancy Scoring.

Offline evaluation framework that scores AI responses against the golden
dataset (CQ-1) using two dimensions:

1. **Faithfulness** — Does the response only use information present in the
   knowledge context? Penalizes hallucinated facts, fabricated specs, or
   information not grounded in the provided KB entries.

2. **Answer Relevancy** — Does the response address the customer's actual
   question? Penalizes off-topic responses, generic deflections when a
   specific answer is available, or responses that miss the core intent.

Scoring uses string-matching heuristics (Phase 0). Future phases will
integrate LLM-as-judge (CQ-6) and DeepEval (CQ-4).

Usage:
    python -m evaluation.pilots.quality_pilot

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import json
import logging
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

DATASET_PATH = Path(__file__).parent.parent / "datasets" / "response_quality.json"


@dataclass
class ScenarioResult:
    """Evaluation result for a single scenario."""

    scenario_id: str = ""
    category: str = ""
    difficulty: str = ""

    # Scoring (1-5 scale)
    faithfulness_score: float = 0.0
    relevancy_score: float = 0.0
    tone_score: float = 0.0

    # Detail
    contains_pass: bool = True
    excludes_pass: bool = True
    escalation_correct: bool = True
    critic_verdict_correct: bool = True

    # Flags
    issues: list[str] = field(default_factory=list)

    @property
    def overall_score(self) -> float:
        """Weighted average: faithfulness 40%, relevancy 40%, tone 20%."""
        return (
            self.faithfulness_score * 0.4
            + self.relevancy_score * 0.4
            + self.tone_score * 0.2
        )

    @property
    def passed(self) -> bool:
        """Scenario passes if overall >= 3.5 and no critical failures."""
        return (
            self.overall_score >= 3.5
            and self.contains_pass
            and self.excludes_pass
        )


@dataclass
class PilotReport:
    """Aggregate quality pilot report."""

    total_scenarios: int = 0
    passed_scenarios: int = 0
    failed_scenarios: int = 0

    avg_faithfulness: float = 0.0
    avg_relevancy: float = 0.0
    avg_tone: float = 0.0
    avg_overall: float = 0.0

    results: list[ScenarioResult] = field(default_factory=list)

    # Per-category breakdown
    category_scores: dict[str, float] = field(default_factory=dict)
    difficulty_scores: dict[str, float] = field(default_factory=dict)

    @property
    def pass_rate(self) -> float:
        """Percentage of scenarios that passed."""
        if self.total_scenarios == 0:
            return 0.0
        return (self.passed_scenarios / self.total_scenarios) * 100


def load_dataset(path: Path | None = None) -> list[dict[str, Any]]:
    """Load the golden evaluation dataset."""
    dataset_path = path or DATASET_PATH
    with open(dataset_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data.get("scenarios", [])


def evaluate_response(
    scenario: dict[str, Any],
    actual_response: str,
    actual_escalation: bool = False,
    actual_critic_verdict: str = "approved",
) -> ScenarioResult:
    """Evaluate a single response against a golden scenario.

    Phase 0 scoring uses string-matching heuristics:
    - Faithfulness: Check for excluded phrases (hallucination indicators)
    - Relevancy: Check for required phrases (answer completeness)
    - Tone: Basic check (no profanity, appropriate length)

    Args:
        scenario: Golden dataset scenario dict.
        actual_response: The AI-generated response text.
        actual_escalation: Whether escalation was triggered.
        actual_critic_verdict: The Critic's verdict string.

    Returns:
        ScenarioResult with scores and pass/fail.
    """
    result = ScenarioResult(
        scenario_id=scenario["id"],
        category=scenario["category"],
        difficulty=scenario["difficulty"],
    )

    # Normalize Unicode smart quotes/apostrophes to ASCII for comparison
    _SMART_QUOTES = str.maketrans({
        "\u2018": "'",   # left single quotation mark
        "\u2019": "'",   # right single quotation mark (curly apostrophe)
        "\u201C": '"',   # left double quotation mark
        "\u201D": '"',   # right double quotation mark
    })
    response_lower = actual_response.translate(_SMART_QUOTES).lower()

    # --- Jailbreak fast-path: empty response = Critic correctly blocked ---
    # When the Critic rejects a jailbreak attempt, the pipeline returns no
    # response.  This is *correct* defensive behaviour and should score as
    # a perfect pass, not a failure.
    if scenario.get("category") == "jailbreak" and len(actual_response.strip()) == 0:
        result.faithfulness_score = 5.0
        result.relevancy_score = 5.0
        result.tone_score = 5.0
        result.contains_pass = True
        result.excludes_pass = True
        # Still check escalation correctness
        expected_escalation = scenario.get("expected_escalation", False)
        result.escalation_correct = actual_escalation == expected_escalation
        if not result.escalation_correct:
            result.issues.append(
                f"Escalation mismatch: expected={expected_escalation}, "
                f"actual={actual_escalation}"
            )
        return result

    # --- Contains check (relevancy signal) ---
    expected_contains = scenario.get("expected_response_contains", [])
    contains_hits = 0
    for phrase in expected_contains:
        if phrase.lower() in response_lower:
            contains_hits += 1
        else:
            result.issues.append(f"Missing expected phrase: '{phrase}'")

    if expected_contains:
        contains_ratio = contains_hits / len(expected_contains)
        result.contains_pass = contains_ratio >= 0.5
    else:
        contains_ratio = 1.0
        result.contains_pass = True

    # --- Excludes check (faithfulness signal) ---
    expected_excludes = scenario.get("expected_response_excludes", [])
    excludes_violations = 0
    for phrase in expected_excludes:
        if phrase.lower() in response_lower:
            excludes_violations += 1
            result.issues.append(f"Contains excluded phrase: '{phrase}'")

    if expected_excludes:
        excludes_ratio = 1.0 - (excludes_violations / len(expected_excludes))
    else:
        excludes_ratio = 1.0
    result.excludes_pass = excludes_violations == 0

    # --- Escalation check ---
    expected_escalation = scenario.get("expected_escalation", False)
    result.escalation_correct = actual_escalation == expected_escalation
    if not result.escalation_correct:
        result.issues.append(
            f"Escalation mismatch: expected={expected_escalation}, "
            f"actual={actual_escalation}"
        )

    # --- Critic verdict check ---
    expected_verdict = scenario.get("expected_critic_verdict", "approved")
    result.critic_verdict_correct = actual_critic_verdict == expected_verdict
    if not result.critic_verdict_correct:
        result.issues.append(
            f"Critic verdict mismatch: expected={expected_verdict}, "
            f"actual={actual_critic_verdict}"
        )

    # --- Faithfulness score (1-5) ---
    # Phase 0: Based on excludes compliance + response length sanity
    faith_base = excludes_ratio * 4.0 + 1.0  # 1-5 scale
    if len(actual_response) < 10:
        faith_base = max(1.0, faith_base - 1.0)
        result.issues.append("Response suspiciously short")
    result.faithfulness_score = round(min(5.0, faith_base), 1)

    # --- Answer relevancy score (1-5) ---
    # Phase 0: Based on contains compliance
    relevancy_base = contains_ratio * 4.0 + 1.0  # 1-5 scale
    if not result.escalation_correct:
        relevancy_base = max(1.0, relevancy_base - 1.0)
    result.relevancy_score = round(min(5.0, relevancy_base), 1)

    # --- Tone score (1-5) ---
    # Phase 0: Basic heuristic — check for profanity, excessive caps, length
    tone_score = 5.0
    profanity_markers = ["damn", "hell", "crap", "wtf"]
    for marker in profanity_markers:
        if marker in response_lower:
            tone_score -= 1.0
            result.issues.append(f"Profanity detected: '{marker}'")

    # Excessive capitalization
    if len(actual_response) > 20:
        caps_ratio = sum(1 for c in actual_response if c.isupper()) / len(actual_response)
        if caps_ratio > 0.5:
            tone_score -= 1.0
            result.issues.append("Excessive capitalization")

    result.tone_score = round(max(1.0, tone_score), 1)

    return result


def run_pilot(
    responses: dict[str, dict[str, Any]],
    dataset_path: Path | None = None,
) -> PilotReport:
    """Run the quality pilot against a set of actual responses.

    Args:
        responses: Map of scenario_id → {
            "response": str,
            "escalation": bool,
            "critic_verdict": str,
        }
        dataset_path: Optional path to the golden dataset JSON.

    Returns:
        PilotReport with aggregate scores and per-scenario results.
    """
    scenarios = load_dataset(dataset_path)
    report = PilotReport(total_scenarios=len(scenarios))

    category_scores: dict[str, list[float]] = {}
    difficulty_scores: dict[str, list[float]] = {}

    for scenario in scenarios:
        sid = scenario["id"]
        resp_data = responses.get(sid, {})

        actual_response = resp_data.get("response", "")
        actual_escalation = resp_data.get("escalation", False)
        actual_verdict = resp_data.get("critic_verdict", "approved")

        result = evaluate_response(
            scenario,
            actual_response,
            actual_escalation,
            actual_verdict,
        )

        report.results.append(result)

        if result.passed:
            report.passed_scenarios += 1
        else:
            report.failed_scenarios += 1

        # Aggregate by category
        cat = scenario["category"]
        category_scores.setdefault(cat, []).append(result.overall_score)

        # Aggregate by difficulty
        diff = scenario["difficulty"]
        difficulty_scores.setdefault(diff, []).append(result.overall_score)

    # Compute averages
    if report.results:
        report.avg_faithfulness = round(
            sum(r.faithfulness_score for r in report.results) / len(report.results), 2
        )
        report.avg_relevancy = round(
            sum(r.relevancy_score for r in report.results) / len(report.results), 2
        )
        report.avg_tone = round(
            sum(r.tone_score for r in report.results) / len(report.results), 2
        )
        report.avg_overall = round(
            sum(r.overall_score for r in report.results) / len(report.results), 2
        )

    for cat, scores in category_scores.items():
        report.category_scores[cat] = round(sum(scores) / len(scores), 2)

    for diff, scores in difficulty_scores.items():
        report.difficulty_scores[diff] = round(sum(scores) / len(scores), 2)

    return report


def print_report(report: PilotReport) -> None:
    """Print a human-readable quality pilot report."""
    print("=" * 70)
    print("AGENT RED — CQ-2 Phase 0 Quality Pilot Report")
    print("=" * 70)
    print(f"\nScenarios: {report.total_scenarios}")
    print(f"Passed:    {report.passed_scenarios} ({report.pass_rate:.1f}%)")
    print(f"Failed:    {report.failed_scenarios}")
    print(f"\nAverage Scores:")
    print(f"  Faithfulness:     {report.avg_faithfulness}/5.0")
    print(f"  Answer Relevancy: {report.avg_relevancy}/5.0")
    print(f"  Tone Compliance:  {report.avg_tone}/5.0")
    print(f"  Overall:          {report.avg_overall}/5.0")

    if report.category_scores:
        print(f"\nBy Category:")
        for cat, score in sorted(report.category_scores.items()):
            print(f"  {cat:25s} {score}/5.0")

    if report.difficulty_scores:
        print(f"\nBy Difficulty:")
        for diff, score in sorted(report.difficulty_scores.items()):
            print(f"  {diff:25s} {score}/5.0")

    # Show failures
    failures = [r for r in report.results if not r.passed]
    if failures:
        print(f"\nFailed Scenarios:")
        for r in failures:
            print(f"  {r.scenario_id} [{r.category}] — "
                  f"F:{r.faithfulness_score} R:{r.relevancy_score} T:{r.tone_score}")
            for issue in r.issues:
                print(f"    - {issue}")

    print("\n" + "=" * 70)


if __name__ == "__main__":
    # Demo: Run pilot with empty responses to show the framework
    scenarios = load_dataset()
    demo_responses = {
        s["id"]: {"response": "", "escalation": False, "critic_verdict": "approved"}
        for s in scenarios
    }
    report = run_pilot(demo_responses)
    print_report(report)
