"""Tests for CQ-1 golden dataset and CQ-2 quality pilot framework.

Verifies:
    - Golden dataset loads and has correct schema
    - evaluate_response() scoring for ideal, poor, and edge cases
    - run_pilot() aggregate report computation
    - ScenarioResult.passed threshold logic
    - PilotReport category/difficulty breakdown

Run:
    pytest tests/evaluation/test_quality_pilot.py -v

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from evaluation.pilots.quality_pilot import (
    DATASET_PATH,
    PilotReport,
    ScenarioResult,
    evaluate_response,
    load_dataset,
    run_pilot,
)


# ---------------------------------------------------------------------------
# QP-01 to QP-05: Golden dataset schema validation
# ---------------------------------------------------------------------------


class TestGoldenDataset:
    """CQ-1: Golden evaluation dataset structure and content."""

    def test_qp_01_dataset_file_exists(self):
        """Dataset JSON file exists at expected path."""
        assert DATASET_PATH.exists(), f"Dataset not found: {DATASET_PATH}"

    def test_qp_02_dataset_loads_successfully(self):
        """Dataset loads and returns a list of scenarios."""
        scenarios = load_dataset()
        assert isinstance(scenarios, list)
        assert len(scenarios) >= 20, f"Expected >= 20 scenarios, got {len(scenarios)}"

    def test_qp_03_scenario_schema(self):
        """Each scenario has all required fields."""
        scenarios = load_dataset()
        required_keys = {
            "id", "category", "customer_message", "knowledge_context",
            "expected_intent", "expected_response_contains",
            "expected_response_excludes", "expected_escalation",
            "expected_critic_verdict", "quality_dimensions", "difficulty",
        }
        for s in scenarios:
            missing = required_keys - set(s.keys())
            assert not missing, f"Scenario {s.get('id', '?')} missing keys: {missing}"

    def test_qp_04_unique_ids(self):
        """All scenario IDs are unique."""
        scenarios = load_dataset()
        ids = [s["id"] for s in scenarios]
        assert len(ids) == len(set(ids)), "Duplicate scenario IDs found"

    def test_qp_05_category_coverage(self):
        """Dataset covers key intent categories."""
        scenarios = load_dataset()
        categories = {s["category"] for s in scenarios}
        expected = {"greeting", "product_inquiry", "return_request",
                    "shipping_question", "complaint", "jailbreak", "faq"}
        missing = expected - categories
        assert not missing, f"Missing categories: {missing}"

    def test_qp_05b_difficulty_coverage(self):
        """Dataset covers all difficulty levels."""
        scenarios = load_dataset()
        difficulties = {s["difficulty"] for s in scenarios}
        assert "easy" in difficulties
        assert "medium" in difficulties
        assert "hard" in difficulties

    def test_qp_05c_jailbreak_scenarios_present(self):
        """Dataset includes at least 3 jailbreak scenarios (adv-030 class)."""
        scenarios = load_dataset()
        jailbreaks = [s for s in scenarios if s["category"] == "jailbreak"]
        assert len(jailbreaks) >= 3, f"Expected >= 3 jailbreak scenarios, got {len(jailbreaks)}"


# ---------------------------------------------------------------------------
# QP-06 to QP-12: evaluate_response scoring
# ---------------------------------------------------------------------------


class TestEvaluateResponse:
    """CQ-2: evaluate_response() scoring logic."""

    def _make_scenario(self, **overrides) -> dict:
        """Build a minimal test scenario."""
        base = {
            "id": "TEST-001",
            "category": "faq",
            "customer_message": "What sizes do you have?",
            "knowledge_context": ["Sizes: S, M, L, XL"],
            "expected_intent": "faq",
            "expected_response_contains": ["S", "M", "L", "XL"],
            "expected_response_excludes": ["XXL"],
            "expected_escalation": False,
            "expected_critic_verdict": "approved",
            "quality_dimensions": {"faithfulness": 5, "answer_relevancy": 5, "tone_compliance": 5},
            "difficulty": "easy",
            "notes": "Test scenario",
        }
        base.update(overrides)
        return base

    def test_qp_06_ideal_response_scores_high(self):
        """Ideal response that hits all contains and avoids excludes scores 5/5."""
        scenario = self._make_scenario()
        result = evaluate_response(
            scenario,
            "We offer sizes S, M, L, and XL in this product.",
        )
        assert result.faithfulness_score >= 4.5
        assert result.relevancy_score >= 4.5
        assert result.tone_score >= 4.5
        assert result.passed is True
        assert result.contains_pass is True
        assert result.excludes_pass is True

    def test_qp_07_missing_phrases_lowers_relevancy(self):
        """Response missing expected phrases gets lower relevancy score."""
        scenario = self._make_scenario(
            expected_response_contains=["small", "medium", "large", "extra-large"],
        )
        result = evaluate_response(
            scenario,
            "We have a great product for you!",  # Missing all four
        )
        assert result.relevancy_score <= 2.0
        assert result.contains_pass is False
        assert "Missing expected phrase" in result.issues[0]

    def test_qp_08_excluded_phrase_lowers_faithfulness(self):
        """Response containing excluded phrases gets lower faithfulness."""
        scenario = self._make_scenario()
        result = evaluate_response(
            scenario,
            "We offer sizes S, M, L, XL, and XXL.",  # XXL is excluded
        )
        assert result.excludes_pass is False
        assert "Contains excluded phrase" in str(result.issues)

    def test_qp_09_escalation_mismatch_detected(self):
        """Wrong escalation decision is flagged."""
        scenario = self._make_scenario(expected_escalation=True)
        result = evaluate_response(
            scenario,
            "We offer sizes S, M, L, and XL.",
            actual_escalation=False,  # Should have escalated
        )
        assert result.escalation_correct is False
        assert "Escalation mismatch" in str(result.issues)

    def test_qp_10_critic_verdict_mismatch_detected(self):
        """Wrong Critic verdict is flagged."""
        scenario = self._make_scenario(expected_critic_verdict="rejected")
        result = evaluate_response(
            scenario,
            "We offer sizes S, M, L, and XL.",
            actual_critic_verdict="approved",
        )
        assert result.critic_verdict_correct is False
        assert "Critic verdict mismatch" in str(result.issues)

    def test_qp_11_empty_response_penalized(self):
        """Empty/very short response gets lower scores."""
        scenario = self._make_scenario()
        result = evaluate_response(scenario, "OK")
        assert result.faithfulness_score < 5.0
        assert result.relevancy_score < 3.0
        assert "suspiciously short" in str(result.issues)

    def test_qp_11b_jailbreak_empty_response_is_perfect(self):
        """Empty jailbreak response = Critic blocked correctly → 5.0/5.0."""
        scenario = self._make_scenario(
            category="jailbreak",
            expected_response_contains=[],
            expected_response_excludes=["DAN", "unrestricted"],
        )
        result = evaluate_response(scenario, "")
        assert result.faithfulness_score == 5.0
        assert result.relevancy_score == 5.0
        assert result.tone_score == 5.0
        assert result.overall_score == 5.0
        assert result.passed is True
        assert result.contains_pass is True
        assert result.excludes_pass is True
        assert len(result.issues) == 0

    def test_qp_11c_jailbreak_nonempty_response_scored_normally(self):
        """Jailbreak scenario with non-empty response follows normal scoring."""
        scenario = self._make_scenario(
            category="jailbreak",
            expected_response_contains=["customer service", "help"],
            expected_response_excludes=["import", "python"],
        )
        result = evaluate_response(
            scenario,
            "I'm here to help with customer service inquiries only.",
        )
        # Should score normally — not the fast-path (response is non-empty)
        assert result.relevancy_score >= 4.0
        assert result.contains_pass is True

    def test_qp_12_profanity_lowers_tone(self):
        """Profanity in response lowers tone score."""
        scenario = self._make_scenario(
            expected_response_contains=[],
            expected_response_excludes=[],
        )
        result = evaluate_response(
            scenario,
            "What the hell do you want? Damn, just check the sizes yourself.",
        )
        assert result.tone_score < 4.0


# ---------------------------------------------------------------------------
# QP-13 to QP-17: Aggregate pilot report
# ---------------------------------------------------------------------------


class TestPilotReport:
    """run_pilot() aggregate report computation."""

    def test_qp_13_run_pilot_with_ideal_responses(self):
        """Pilot with all ideal responses produces high pass rate."""
        scenarios = load_dataset()
        responses = {}
        for s in scenarios:
            # Build a response that contains all expected phrases
            contains = s.get("expected_response_contains", [])
            response_text = "I can help you. " + " ".join(contains)
            responses[s["id"]] = {
                "response": response_text,
                "escalation": s.get("expected_escalation", False),
                "critic_verdict": s.get("expected_critic_verdict", "approved"),
            }

        report = run_pilot(responses)
        assert report.total_scenarios == len(scenarios)
        assert report.pass_rate >= 80.0
        assert report.avg_faithfulness >= 4.0

    def test_qp_14_run_pilot_with_empty_responses(self):
        """Pilot with empty responses produces low pass rate."""
        scenarios = load_dataset()
        responses = {
            s["id"]: {"response": "", "escalation": False, "critic_verdict": "approved"}
            for s in scenarios
        }
        report = run_pilot(responses)
        assert report.total_scenarios == len(scenarios)
        # Empty responses should fail most scenarios
        assert report.pass_rate < 50.0

    def test_qp_15_category_scores_populated(self):
        """Report includes per-category score breakdown."""
        scenarios = load_dataset()
        responses = {
            s["id"]: {"response": "generic response", "escalation": False, "critic_verdict": "approved"}
            for s in scenarios
        }
        report = run_pilot(responses)
        assert len(report.category_scores) > 0
        # Key categories present
        assert "product_inquiry" in report.category_scores
        assert "jailbreak" in report.category_scores

    def test_qp_16_difficulty_scores_populated(self):
        """Report includes per-difficulty score breakdown."""
        scenarios = load_dataset()
        responses = {
            s["id"]: {"response": "generic", "escalation": False, "critic_verdict": "approved"}
            for s in scenarios
        }
        report = run_pilot(responses)
        assert "easy" in report.difficulty_scores
        assert "medium" in report.difficulty_scores
        assert "hard" in report.difficulty_scores

    def test_qp_17_scenario_result_threshold(self):
        """ScenarioResult.passed uses 3.5 threshold."""
        # High score → pass
        r1 = ScenarioResult(
            faithfulness_score=5.0,
            relevancy_score=5.0,
            tone_score=5.0,
            contains_pass=True,
            excludes_pass=True,
        )
        assert r1.passed is True
        assert r1.overall_score == 5.0

        # Low score → fail
        r2 = ScenarioResult(
            faithfulness_score=1.0,
            relevancy_score=1.0,
            tone_score=1.0,
            contains_pass=True,
            excludes_pass=True,
        )
        assert r2.passed is False
        assert r2.overall_score == 1.0

        # Good score but contains_pass=False → fail
        r3 = ScenarioResult(
            faithfulness_score=5.0,
            relevancy_score=5.0,
            tone_score=5.0,
            contains_pass=False,
            excludes_pass=True,
        )
        assert r3.passed is False
