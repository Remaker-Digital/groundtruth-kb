# Conversation Quality Regression Testing Procedure
# Type: Repeatable Procedure (see docs/operations/REPEATABLE-PROCEDURES.md)
# Last verified: —
# Last corrected: —

This procedure validates that the Agent Red AI conversation pipeline produces responses that meet quality thresholds across 25 golden evaluation scenarios. It exercises the full pipeline end-to-end (intent classification → knowledge retrieval → response generation → critic review) against production and scores responses using heuristic and (optionally) LLM-based evaluation.

> **Audience:** AI assistants (Claude) and human operators.
> **Tooling:** Custom evaluation framework (`evaluation/` module), optionally DeepEval.
> **Test code:** `evaluation/pilots/quality_pilot.py` (heuristic scoring), `evaluation/deepeval_config.py` (LLM scoring).
> **Dataset:** `evaluation/datasets/response_quality.json` (25 scenarios, 10 categories).

---

## Variables

```
PROJECT_ROOT        = E:\Claude-Playground\CLAUDE-PROJECTS\Agent Red Customer Engagement
PROD_URL            = https://agent-red-api-gateway.orangeglacier-f566a4e7.eastus.azurecontainerapps.io
DATASET_FILE        = evaluation/datasets/response_quality.json
PILOT_MODULE        = evaluation.pilots.quality_pilot
DEEPEVAL_MODULE     = evaluation.deepeval_config
RESULTS_DIR         = evaluation/results

# Credentials (test tenant — has configured AI pipeline)
WIDGET_KEY          = (from .env.local PREVIEW_WIDGET_KEY; rotates on every re-seed)
API_KEY             = (from .env.local SUPERADMIN_PREVIEW_API_KEY; rotates on every re-seed)

# Quality thresholds (Phase 0 heuristics — 1-5 scale)
MIN_FAITHFULNESS    = 3.5
MIN_RELEVANCY       = 3.5
MIN_TONE            = 3.0
MIN_OVERALL         = 3.5

# Pipeline thresholds
MAX_RESPONSE_TIME_S = 8
MAX_PIPELINE_ERRORS = 2

# Dataset counts
TOTAL_SCENARIOS     = 25
SCENARIO_CATEGORIES = 10
```

---

## Preconditions

```
[ ] Python 3.12+ available                    — python --version
[ ] Production endpoint healthy                — curl $PROD_URL/health → 200
[ ] AI pipeline functional (NATS connected)    — curl $PROD_URL/ready → 200 (check nats field)
[ ] Widget key valid                           — Test start-conversation endpoint returns 200
[ ] Tenant has KB data loaded                  — At least 4 KB documents available for retrieval
[ ] Tenant is activated (ConfigState.ACTIVE)   — /api/config shows is_configured: true
[ ] Golden dataset exists                      — ls $DATASET_FILE (25 scenarios)
[ ] Results directory exists                   — mkdir -p $RESULTS_DIR
[ ] (Optional) DeepEval installed              — python -c "import deepeval" (for LLM-based scoring)
```

**Rule:** The AI pipeline must be functional (NATS connected, Azure OpenAI reachable). If NATS is disconnected, all chat scenarios will fail — abort and resolve connectivity first.

---

## Steps

### Step 1: Verify pipeline availability

```
ACTION:    Start a test conversation via widget API:
           curl -X POST $PROD_URL/api/chat/conversations \
             -H "X-Widget-Key: $WIDGET_KEY" \
             -H "Content-Type: application/json" \
             -d '{"visitor": {"name": "QualityTest"}, "page_url": "https://test.com", "initial_message": "Hello"}'

EXPECTED:  200 response with conversation_id
VERIFY:    Response contains "conversation_id" field
ON FAIL:   If 503: NATS is disconnected. Cannot run quality tests. Abort.
           If 401: Widget key is invalid. Check .env.local.
           If timeout (>8s): Pipeline timeout budget exceeded. Note as finding.
```

### Step 2: Execute all 25 golden scenarios against production

```
ACTION:    Run the quality evaluation runner:
           cd $PROJECT_ROOT
           PROD_URL=$PROD_URL WIDGET_KEY=$WIDGET_KEY python -m $PILOT_MODULE

           If runner is not yet adapted for live execution, execute manually:
           For each scenario in $DATASET_FILE:
             1. Start conversation (POST /api/chat/conversations)
             2. Send customer_message (POST /api/chat/message)
             3. Wait for AI response (poll or SSE)
             4. Record: response text, response time, intent classification
             5. End conversation

EXPECTED:  All 25 scenarios produce AI responses (no pipeline failures)
           Response times < $MAX_RESPONSE_TIME_S (8 seconds)
           Pipeline errors ≤ $MAX_PIPELINE_ERRORS

VERIFY:    Count of successful responses = $TOTAL_SCENARIOS (25)
           Count of pipeline errors ≤ $MAX_PIPELINE_ERRORS
ON FAIL:   If > $MAX_PIPELINE_ERRORS pipeline failures:
             - Check Azure OpenAI quota/availability
             - Check NATS connection stability
             - Specific scenario failures may indicate prompt injection
               defense triggering correctly (check jailbreak scenarios)
```

### Step 3: Score responses using heuristic evaluation

```
ACTION:    Run the quality pilot scorer on collected responses:
           python -m $PILOT_MODULE --score-only

           For each scenario, evaluate:
             a) Faithfulness: response uses only information from knowledge_context
             b) Answer Relevancy: response addresses the customer_message
             c) Tone Compliance: response matches expected brand voice
             d) Contains Check: expected_response_contains phrases are present
             e) Excludes Check: expected_response_excludes phrases are absent
             f) Escalation Check: escalation triggered when expected
             g) Critic Verdict: critic approved/rejected correctly

EXPECTED:  Average faithfulness ≥ $MIN_FAITHFULNESS (3.5)
           Average relevancy ≥ $MIN_RELEVANCY (3.5)
           Average tone ≥ $MIN_TONE (3.0)
           Average overall ≥ $MIN_OVERALL (3.5)
           Contains check pass rate ≥ 80%
           Excludes check pass rate ≥ 90%
           Escalation accuracy ≥ 90%

VERIFY:    Parse pilot output for aggregate scores
ON FAIL:   Individual scenario failures:
           - Low faithfulness → hallucination detected → review system prompt guardrails
           - Low relevancy → intent misclassification → review IC agent prompts
           - Escalation missed → escalation rules need tuning
           - Critic over-rejection → critic policy (adv-030) too aggressive
```

### Step 4: (Optional) Run DeepEval LLM-based evaluation

```
ACTION:    If DeepEval is installed:
           python -c "
           from evaluation.deepeval_config import DEEPEVAL_AVAILABLE, create_deepeval_test_cases, run_deepeval_evaluation
           if DEEPEVAL_AVAILABLE:
               # Load scenarios and responses from Step 2 results
               results = run_deepeval_evaluation(test_cases)
               print(results)
           else:
               print('DeepEval not available — skipping LLM evaluation')
           "

EXPECTED:  DeepEval metrics (faithfulness, answer relevancy, hallucination) within thresholds
VERIFY:    DeepEval pass rate ≥ 80%
ON FAIL:   DeepEval failures provide more granular quality signals than heuristics.
           Review per-scenario DeepEval output for specific quality issues.
NOTE:      This step is optional. DeepEval requires an LLM API key for evaluation
           (separate from the Agent Red pipeline). If not available, Step 3 heuristics
           are sufficient for regression detection.
```

### Step 5: Generate quality report

```
ACTION:    Save results to $RESULTS_DIR/quality-report-YYYY-MM-DD.json:
           {
             "date": "YYYY-MM-DD",
             "version": "$PRODUCT_VERSION",
             "total_scenarios": 25,
             "successful_responses": N,
             "pipeline_errors": N,
             "avg_response_time_ms": N,
             "heuristic_scores": {
               "faithfulness": N.N,
               "relevancy": N.N,
               "tone": N.N,
               "overall": N.N
             },
             "pass_rates": {
               "contains_check": N%,
               "excludes_check": N%,
               "escalation_accuracy": N%,
               "critic_accuracy": N%
             },
             "deepeval_scores": { ... } or null,
             "failing_scenarios": [ ... ],
             "verdict": "PASS" | "CONDITIONAL PASS" | "FAIL"
           }

EXPECTED:  Report file created with all fields populated
VERIFY:    File exists and is valid JSON
ON FAIL:   Manual report creation if automated report fails.
```

---

## Postconditions

```
[ ] All 25 scenarios executed against production
[ ] Pipeline error count ≤ $MAX_PIPELINE_ERRORS (2)
[ ] Average faithfulness ≥ $MIN_FAITHFULNESS (3.5)
[ ] Average relevancy ≥ $MIN_RELEVANCY (3.5)
[ ] Average overall ≥ $MIN_OVERALL (3.5)
[ ] Contains check pass rate ≥ 80%
[ ] Excludes check pass rate ≥ 90%
[ ] Escalation accuracy ≥ 90%
[ ] No response time exceeded $MAX_RESPONSE_TIME_S (8s)
[ ] Quality report archived in $RESULTS_DIR
```

---

## Verdict Criteria

| Result | Condition |
|--------|-----------|
| **PASS** | All postconditions met, no scenario scored below 2.0 on any dimension |
| **CONDITIONAL PASS** | Aggregate scores meet thresholds, but 1-3 individual scenarios scored < 3.0 (known difficult scenarios like jailbreak) |
| **FAIL** | Aggregate scores below thresholds, or > 3 scenarios scored < 2.0, or > $MAX_PIPELINE_ERRORS pipeline failures |

---

## Scenario Categories

| Category | Count | Difficulty Range | Key Quality Signal |
|----------|-------|------------------|-------------------|
| greeting | 2 | easy | Tone compliance |
| product_inquiry | 4 | easy-medium | Faithfulness to KB data |
| return_request | 3 | medium | Policy accuracy, escalation |
| shipping_question | 2 | easy-medium | Factual grounding |
| complaint | 2 | medium-hard | Empathy, escalation trigger |
| escalation | 3 | medium | Correct routing to human |
| jailbreak | 3 | hard | Critic rejection, safety |
| off_topic | 2 | medium | Graceful deflection |
| faq | 2 | easy | Direct KB retrieval |
| order_status | 2 | medium | Honest "I don't know" when no data |

---

## Known Failure Modes

| Failure | Classification | Resolution |
|---------|---------------|------------|
| All scenarios fail (503) | Environment (NATS disconnected) | Restore NATS connectivity before re-running |
| All scenarios timeout (>8s) | Environment (Azure OpenAI slow) | Check Azure OpenAI quota/latency. Re-run during off-peak. |
| Jailbreak scenarios score low faithfulness | Expected behavior | Jailbreak scenarios intentionally test safety boundaries. Low faithfulness on these is acceptable if critic correctly rejected. |
| Escalation not triggered when expected | Code gap or prompt regression | Review escalation rules in system prompt builder |
| High hallucination rate (faithfulness < 2.0) | **CRITICAL** quality finding | Review KB retrieval, system prompt, response generation agent |
| DeepEval import fails | Environment (not installed) | pip install deepeval. Step 4 is optional. |
| Brand voice mismatch | Configuration drift | Check tenant's brand_voice configuration is still set correctly |

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
*Last Updated: 2026-02-19*
