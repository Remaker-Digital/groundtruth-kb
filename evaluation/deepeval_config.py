"""CQ-4: DeepEval Integration Scaffold.

Provides the configuration and adapter layer for integrating DeepEval
into the Agent Red evaluation framework. DeepEval enables LLM-based
evaluation metrics (faithfulness, answer relevancy, hallucination
detection) that go beyond the Phase 0 string-matching heuristics.

Prerequisites:
    pip install deepeval

This scaffold provides:
    - Configuration for DeepEval metrics (which model, thresholds)
    - Adapter to convert golden dataset scenarios to DeepEval test cases
    - Runner that executes DeepEval evaluation and returns results

Usage:
    from evaluation.deepeval_config import (
        create_deepeval_test_cases,
        run_deepeval_evaluation,
        DEEPEVAL_AVAILABLE,
    )

    if DEEPEVAL_AVAILABLE:
        cases = create_deepeval_test_cases(scenarios, responses)
        results = run_deepeval_evaluation(cases)

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)

# DeepEval availability check — graceful degradation if not installed
DEEPEVAL_AVAILABLE = False
try:
    from deepeval import evaluate as deepeval_evaluate
    from deepeval.metrics import (
        AnswerRelevancyMetric,
        FaithfulnessMetric,
        HallucinationMetric,
    )
    from deepeval.test_case import LLMTestCase

    DEEPEVAL_AVAILABLE = True
    logger.info("DeepEval is available — LLM-based evaluation enabled")
except ImportError:
    logger.info("DeepEval not installed — using Phase 0 heuristic evaluation")


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

# DeepEval model for judge evaluation
EVAL_MODEL = "gpt-4o-mini"

# Metric thresholds (minimum acceptable scores)
FAITHFULNESS_THRESHOLD = 0.7
RELEVANCY_THRESHOLD = 0.7
HALLUCINATION_THRESHOLD = 0.5  # Lower = fewer hallucinations


# ---------------------------------------------------------------------------
# Adapter: Golden dataset → DeepEval test cases
# ---------------------------------------------------------------------------


def create_deepeval_test_cases(
    scenarios: list[dict[str, Any]],
    responses: dict[str, dict[str, Any]],
) -> list[Any]:
    """Convert golden dataset scenarios + actual responses to DeepEval LLMTestCases.

    Args:
        scenarios: Golden dataset scenario dicts.
        responses: Map of scenario_id → {"response": str, ...}.

    Returns:
        List of LLMTestCase objects (or empty list if DeepEval unavailable).
    """
    if not DEEPEVAL_AVAILABLE:
        logger.warning("DeepEval not available — returning empty test cases")
        return []

    test_cases = []
    for scenario in scenarios:
        sid = scenario["id"]
        resp_data = responses.get(sid, {})
        actual_response = resp_data.get("response", "")

        if not actual_response:
            continue

        # Build retrieval context from knowledge_context
        retrieval_context = scenario.get("knowledge_context", [])
        if isinstance(retrieval_context, list):
            retrieval_context = [str(c) for c in retrieval_context]

        test_case = LLMTestCase(
            input=scenario["customer_message"],
            actual_output=actual_response,
            expected_output=None,  # We use contains/excludes instead
            retrieval_context=retrieval_context,
        )
        test_cases.append(test_case)

    return test_cases


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------


def create_metrics() -> list[Any]:
    """Create DeepEval metric instances.

    Returns:
        List of metric objects (or empty list if DeepEval unavailable).
    """
    if not DEEPEVAL_AVAILABLE:
        return []

    return [
        FaithfulnessMetric(
            threshold=FAITHFULNESS_THRESHOLD,
            model=EVAL_MODEL,
        ),
        AnswerRelevancyMetric(
            threshold=RELEVANCY_THRESHOLD,
            model=EVAL_MODEL,
        ),
        HallucinationMetric(
            threshold=HALLUCINATION_THRESHOLD,
            model=EVAL_MODEL,
        ),
    ]


def run_deepeval_evaluation(
    test_cases: list[Any],
    metrics: list[Any] | None = None,
) -> dict[str, Any]:
    """Run DeepEval evaluation on test cases.

    Args:
        test_cases: List of LLMTestCase objects.
        metrics: Optional list of metrics (defaults to create_metrics()).

    Returns:
        Results dict with per-case scores and aggregate summary.
    """
    if not DEEPEVAL_AVAILABLE:
        return {
            "status": "unavailable",
            "message": "DeepEval not installed. Run: pip install deepeval",
            "results": [],
        }

    if not test_cases:
        return {
            "status": "empty",
            "message": "No test cases provided",
            "results": [],
        }

    if metrics is None:
        metrics = create_metrics()

    try:
        evaluation_results = deepeval_evaluate(
            test_cases=test_cases,
            metrics=metrics,
        )

        return {
            "status": "completed",
            "total_cases": len(test_cases),
            "metrics_used": [type(m).__name__ for m in metrics],
            "results": evaluation_results,
        }

    except Exception as exc:
        logger.exception("DeepEval evaluation failed: %s", exc)
        return {
            "status": "error",
            "message": str(exc),
            "results": [],
        }
