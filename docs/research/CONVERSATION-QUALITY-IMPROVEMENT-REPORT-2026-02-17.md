# Conversation Quality Improvement Report — Agent Red AI Chat Service

**Document Type:** Research Report  
**Created:** 2026-02-17  
**Revised:** 2026-02-17 (v2 — added baselines, tool justification, implementation risks, human-in-the-loop details, failure mode taxonomy, dataset strategy, success criteria)  
**Purpose:** Help decide how to improve the conversation quality of the Agent Red AI chat service. Covers tests, tools, best practices, and guidance specific to AI chat customer experience (sales, service, support).

---

## Executive Summary

Agent Red already has strong foundations: a six-agent pipeline (intent, knowledge, response, escalation, analytics, critic), response explainability, and analytics APIs. **Gaps identified:**

1. **Response quality evaluation** — The AGNTCY response-generation evaluation dataset is empty; no systematic quality scoring.
2. **RAG-specific metrics** — Faithfulness, answer relevancy, and retrieval quality are not instrumented.
3. **CX-specific benchmarking** — No benchmark aligned with customer-service dialogue quality (e.g., OlaBench-style).
4. **LLM-as-judge** — Not used for quality; research advises validation and multi-dimensional assessment.
5. **Sales/commerce metrics** — Conversion influence, GMV, and recommendation accuracy are not tracked.

This report synthesizes industry best practices, evaluation tools, and actionable recommendations to close these gaps.

---

## 1. Current Agent Red Quality Infrastructure

### 1.1 Pipeline & Agents

| Stage | Agent | Purpose | Quality Signals |
|-------|-------|---------|-----------------|
| 1 | Intent Classifier | Classifies customer intent | Accuracy 94% (AGNTCY baseline) |
| 2 | Knowledge Retrieval | Hybrid search (BM25 + vector + MCP) | Relevance scores; no faithfulness metric |
| 3 | Response Generator | Generates branded, contextual responses | No automated quality scoring |
| 4 | Critic/Supervisor | Validates safety, blocks harmful content | 97.1% TP rate (1 jailbreak miss); 0% FP |
| 5 | Escalation Handler | Routes to humans when needed | 100% precision, 97% recall |
| 6 | Analytics Collector | Logs pipeline metrics | Stage latency, success flags |

### 1.2 Instrumented Metrics

**Admin Analytics API** (`/api/analytics/*`):

- Total/billable conversations, avg turns, avg messages
- Resolution rate, escalation rate, escalation count
- Customer satisfaction (if surveyed)
- Critic pass/fail counts
- Intent/topic breakdown
- Knowledge gaps (escalated + error conversations)

**Response Explainability** (`ResponseDecisionTrace`):

- Profile factors used, knowledge sources, memory signals
- Critic verdict, intent, latency, cost
- Stored per-conversation for audit and debugging

### 1.3 Gaps

| Gap | Description |
|-----|-------------|
| Response quality dataset | `evaluation/datasets/response_quality.json` empty — AGNTCY eval skips response generation |
| RAG faithfulness | No automated check that responses are grounded in retrieved context |
| Answer relevancy | No metric for how well responses address the query |
| Hallucination detection | Critic focuses on safety; not fact-checking against KB |
| LLM-as-judge | No GPT-4/Claude scoring of response quality |
| Sales metrics | No GMV influence, conversion lift, or recommendation accuracy |

### 1.4 Current Performance Baselines

These values are instrumented but vary by tenant, volume, and data freshness. Use as rough reference for prioritization.

| Metric | Source | Current State | Notes |
|--------|--------|---------------|-------|
| **Resolution rate** | `GET /api/analytics/summary` | Per-tenant, computed | `(non-escalated + non-error) / total`; no 72h follow-up check |
| **Escalation rate** | Same | Per-tenant | Inverse of containment |
| **Critic pass rate** | Same | Per-tenant | `critic_passed / (critic_passed + critic_failed)` |
| **Customer satisfaction** | Same | Often 0 | Requires post-conversation survey; low uptake without widget instrumentation |
| **Avg response time** | Same | Seconds | From `aggregate_metrics`; depends on pipeline latency instrumentation |
| **Latency (platform)** | `sla_monitoring.py` | P50 < 1,500ms, P95 < 2,000ms, P99 < 5,000ms | SLA targets; actual from `SlaMonitor.record_latency()` |
| **Cost per conversation** | `cost_model.py` | ~\$0.0073 AI cost | GPT-4o response gen ≈ 94.5%; add ~\$0.01–0.02 for LLM-as-judge per eval |
| **Intent accuracy** | AGNTCY eval | 94% | 47/50 test cases |
| **Escalation precision/recall** | AGNTCY eval | 100% / 97% | Baseline |
| **Critic TP/FP** | AGNTCY eval | 97.1% TP, 0% FP | One jailbreak miss (adv-030) |

**Implication:** Resolution rate and escalation rate are the most reliable current signals. CSAT and satisfaction-related metrics require survey instrumentation. Latency and cost are well understood; adding LLM-as-judge at scale (~\$0.01–0.02 per conversation) is material and should be sampled rather than run on 100% of traffic.

---

## 2. Industry Best Practices

### 2.1 Support & Service CX

**Primary metrics (beyond CSAT):**

| Metric | Definition | Benchmark | Source |
|--------|-------------|-----------|--------|
| **First-Contact Resolution (FCR)** | % resolved without escalation or follow-up in 72h | 30% improvement potential with AI eval | Pedowitz, Zendesk |
| **Containment Rate** | % fully automated (no human) | 60–80% industry | Nineten |
| **Intent Recognition Accuracy** | Correct identification of customer need | Critical for routing | Industry |
| **Escalation Appropriateness** | Right automation vs. right handoff | "Right automation" goal | Loris AI |
| **Conversation Quality** | Clarity, tone, empathy, brand alignment | AI can reduce analysis time 85% | Pedowitz |

**Critical insight:** CSAT alone is insufficient — low survey response (<15%), post-facto, and can mask problems like frequent unnecessary escalations. Modern evaluation requires **conversation quality, compliance, tone, empathy, and brand alignment** across 100% of conversations rather than manual sampling.

### 2.2 Sales & Conversational Commerce

| Metric | Definition | Typical Result |
|--------|-------------|----------------|
| **GMV Influenced** | Revenue attributed to chat interactions | Arc'teryx: 75% conversion lift (4%→7%) on high-intent product Qs |
| **Conversion Rate** | Chat-influenced purchases | Up to 22% boost; mobile up to 387% |
| **AOV** | Average order value from chat-assisted buyers | Higher when AI recommends effectively |
| **Containment + Accuracy** | Resolution without escalation, with correct answers | Quality > volume; accuracy matters |

**Key principle:** Measure **revenue influence**, not just volume. AI should both deflect volume and drive confident purchases.

### 2.3 Multi-Dimensional Evaluation

**OlaBench (2025)** — customer service benchmark:

- **Dimensions:** Dialogue quality, policy compliance, tool calling, critical business risk, hallucination, latency
- **Emphasis:** Subjective service quality and realistic failure modes, not just task completion
- **Finding:** State-of-the-art LLMs still fall short; specialized models (OlaMind 78.72) outperform general (GPT-5.2 70.58); real-world deployment improved resolution +23.67%, reduced transfer -6.6%

**Takeaway:** Decompose evaluation across complementary dimensions rather than a single score.

### 2.4 LLM-as-Judge Caveats

- **Rating indeterminacy:** When criteria admit multiple valid interpretations, forced-choice validation can select suboptimal judges (up to 31% worse)
- **Multi-label ratings:** Prefer "response set" ratings over forced-choice to account for ambiguity
- **Human verification:** Include explicit human review to validate benchmark correctness and real-world relevance
- **System-level ranking:** Evaluate judges on system-level rankings, not just instance-level; instance-based eval can miss biases

---

## 3. Evaluation Frameworks & Tools

### 3.1 DeepEval (confident-ai/deepeval)

**Overview:** Open-source LLM evaluation framework, pytest-like, 13.7k GitHub stars.

**RAG metrics:**

- Answer Relevancy
- Faithfulness
- Contextual Recall
- Contextual Precision
- Contextual Relevancy
- RAGAS integration

**Conversational metrics:**

- Knowledge Retention
- Conversation Completeness
- Conversation Relevancy
- Role Adherence

**Other:**

- G-Eval (custom criteria)
- Hallucination, Toxicity, Bias
- Task Completion, Tool Correctness
- Red-teaming (40+ safety vulnerabilities)

**Integration:** CI/CD, LlamaIndex, Hugging Face. Supports Azure OpenAI. Can run locally or with Confident AI cloud.

**Example (customer support chatbot):**

```python
from deepeval import assert_test
from deepeval.metrics import GEval
from deepeval.test_case import LLMTestCase, LLMTestCaseParams

correctness_metric = GEval(
    name="Correctness",
    criteria="Determine if the 'actual output' is correct based on the 'expected output'.",
    evaluation_params=[LLMTestCaseParams.ACTUAL_OUTPUT, LLMTestCaseParams.EXPECTED_OUTPUT],
    threshold=0.5
)
test_case = LLMTestCase(
    input="What if these shoes don't fit?",
    actual_output="You have 30 days to get a full refund at no extra cost.",
    expected_output="We offer a 30-day full refund at no extra costs.",
    retrieval_context=["All customers are eligible for a 30 day full refund..."]
)
assert_test(test_case, [correctness_metric])
```

### 3.2 RAGAS (Retrieval Augmented Generation Assessment)

**Overview:** Reference-free RAG evaluation (no ground truth required).

**Metrics:**

| Metric | What It Measures |
|--------|------------------|
| **Faithfulness** | Response grounded in retrieved context; no hallucination |
| **Answer Relevancy** | Response addresses the query; useful and on-topic |
| **Context Precision** | Retrieved docs that are relevant to the query |
| **Context Recall** | Retrieved docs cover the needed information |

**Use case:** Diagnose retrieval vs. generation failures. DeepEval includes RAGAS metrics.

### 3.3 RAGChecker

**Overview:** Fine-grained RAG diagnostic framework (arXiv 2408.08067).

- Separate metrics for retrieval and generation
- Meta-evaluation: better correlation with human judgment than alternatives
- Open-sourced

### 3.4 Microsoft Azure AI / OpenAI Evals

**Approach:**

- 200+ ground-truth question-answer pairs
- Record model responses with context
- GPT-4 rates answers on 1–5 scales for multiple metrics
- Synthetic data generation
- Azure AI Generative SDK provides automated eval functions

### 3.5 Hallucination Detection (Research)

| System | Approach |
|--------|----------|
| **HaluCheck** | Atomic fact decomposition, retrieve docs, NLI-style hallucination likelihood |
| **Halu-J** | Critique-based judge, 7B params, multi-evidence handling |
| **KnowHalu** | Step-wise reasoning + multi-form knowledge check; distinguishes fabrication vs. off-target (correct but irrelevant) |

---

## 4. Testing Approaches

### 4.1 Unit Tests (Per-Turn)

- **Input:** Single customer message + context (profile, KB, history)
- **Output:** AI response
- **Metrics:** Faithfulness, relevancy, correctness vs. expected
- **Tools:** DeepEval, RAGAS, custom G-Eval

### 4.2 Integration Tests (Full Pipeline)

- **Input:** Multi-turn conversation or scenario
- **Output:** Full conversation transcript
- **Metrics:** Resolution, escalation, knowledge retention, role adherence
- **Tools:** DeepEval conversational metrics, custom scripts

### 4.3 Regression / Golden Dataset

- **Input:** Curated 50–200 question-answer pairs with expected outputs
- **Run:** On every release or PR
- **Pass criteria:** Thresholds per metric (e.g., faithfulness >0.8, relevancy >0.7)
- **Source:** Real conversations (anonymized), support tickets, FAQ coverage

### 4.4 Human-in-the-Loop

- **Sampling:** 5–10% of conversations for human review
- **Criteria:** Clarity, empathy, brand alignment, correctness, escalation appropriateness
- **Use:** Calibrate LLM judges; surface edge cases; training data for fine-tuning

### 4.5 Red Teaming / Adversarial

- **Focus:** Prompt injection, jailbreak, PII extraction, harmful instructions
- **Current:** AGNTCY Critic addresses this; 97.1% TP (1 jailbreak miss)
- **Tool:** DeepEval red-teaming (40+ vulnerabilities)

---

## 5. Metrics Taxonomy for Agent Red

### 5.1 Existing (Keep)

| Metric | Source | Purpose |
|--------|--------|---------|
| Intent accuracy | AGNTCY eval | Classification quality |
| Escalation precision/recall | AGNTCY eval | Handoff correctness |
| Critic pass/fail | Analytics API | Safety gate |
| Resolution rate, escalation rate | Analytics API | Business outcome |
| Knowledge gaps | Analytics API | KB improvement signals |

### 5.2 Add: RAG Quality

| Metric | Definition | Threshold (suggested) | Tool |
|--------|-------------|------------------------|------|
| **Faithfulness** | Response grounded in retrieved context | >0.8 | DeepEval, RAGAS |
| **Answer Relevancy** | Response addresses query | >0.7 | DeepEval, RAGAS |
| **Contextual Precision** | Retrieved docs relevant | >0.7 | RAGAS |
| **Contextual Recall** | Retrieved docs sufficient | >0.8 | RAGAS |

### 5.3 Add: Response Quality (LLM-as-Judge)

| Metric | Definition | Criteria |
|--------|-------------|----------|
| **Correctness** | Factually correct vs. KB/source | G-Eval with KB as ground truth |
| **Helpfulness** | Addresses customer need | G-Eval: "Does this help resolve the query?" |
| **Tone alignment** | Matches brand voice | G-Eval vs. tenant config |
| **Empathy** | Acknowledges customer concern | G-Eval (support-focused) |

### 5.4 Add: CX-Specific (Support)

| Metric | Definition | Measurement |
|--------|-------------|-------------|
| **FCR proxy** | Resolved without escalation + no quick follow-up | Conversation status + 72h window |
| **Containment rate** | % not escalated | Existing escalation_rate inverse |
| **Repeat explanation rate** | Customer re-states prior info | Semantic similarity (PERSISTENT-CUSTOMER-MEMORY-METRICS) |

### 5.5 Add: Commerce (Sales)

| Metric | Definition | Measurement |
|--------|-------------|-------------|
| **Chat-influenced conversion** | Purchase within session or attributed | GA4/attribution, Stripe |
| **Product recommendation acceptance** | Click-through on suggested products | Widget events, analytics |
| **Cart recovery rate** | Abandoned cart reopened after chat | E-commerce integration |

---

## 6. Specific Guidance by Use Case

### 6.1 Customer Support (Primary)

**Quality dimensions:**

1. **Correctness** — Answers aligned with policies, KB, product info
2. **Completeness** — Addresses all parts of multi-part questions
3. **Clarity** — Easy to understand, no jargon (unless customer uses it)
4. **Empathy** — Acknowledges frustration, apologizes when appropriate
5. **Escalation appropriateness** — Hands off when needed; does not over-escalate
6. **Brand alignment** — Tone matches tenant config

**Tests:**

- Policy questions (returns, shipping, privacy) — correctness vs. KB
- Complex multi-part queries — completeness
- Angry/frustrated customer tone — empathy + escalation
- Edge cases from knowledge gaps — flag for KB update

### 6.2 Customer Service (General)

**Quality dimensions:**

1. **Proactivity** — Offers next steps, related info
2. **Consistency** — Same answer for same question across sessions
3. **Personalization** — Uses customer name, prior history when relevant
4. **Memory** — References prior conversations (Layer 2–3)

**Tests:**

- Returning customer — greeting, history reference
- Preference learning — verbosity, channel preference
- Cross-session continuity — "Any update on my return?"

### 6.3 Sales / Conversational Commerce

**Quality dimensions:**

1. **Product accuracy** — Correct prices, availability, specs
2. **Recommendation relevance** — Suggestions match query and context
3. **Conversion support** — Reduces friction, answers buying objections
4. **Upsell appropriateness** — Relevant add-ons without being pushy

**Tests:**

- Product Q&A — faithfulness to catalog
- "What do you recommend?" — relevancy, personalization
- Cart abandonment follow-up — effectiveness (if implemented)

---

## 7. Recommendations & Action Plan

**Pilot first:** Start with Phase 0 (Section 14.4): faithfulness + relevancy on 100 conversations using existing `ResponseDecisionTrace` data — zero new instrumentation. Then expand.

### 7.1 Immediate (0–2 weeks)

| # | Action | Owner | Effort | Success Criteria |
|---|--------|-------|--------|------------------|
| 1 | **Phase 0 pilot:** Run Faithfulness + Answer Relevancy on 100 conversations via ResponseDecisionTrace export | Dev | S | Metrics computed; top 3 failure modes identified |
| 2 | Populate response quality dataset | Dev | M | 20+ cases |
| 3 | Add DeepEval or RAGAS to `requirements.txt`; create `tests/conversation_quality/` | Dev | S | CI-ready |
| 4 | Implement 20–30 golden test cases (FAQ, policy, product) | Dev/Content | M | Core cases pass |
| 5 | Fix Critic jailbreak miss (adv-030) per AGNTCY report | Dev | S | Critic TP = 100% |

### 7.2 Short-Term (1–2 months)

| # | Action | Owner | Effort | Success Criteria |
|---|--------|-------|--------|------------------|
| 6 | Integrate DeepEval into CI (`deepeval test run` on PR) | Dev | M | <5% flakiness |
| 7 | Add LLM-as-judge for Correctness and Helpfulness (G-Eval) | Dev | M | Sampled, not 100% |
| 8 | Implement FCR proxy metric (resolved + no 72h follow-up) | Dev | M | In analytics API |
| 9 | Human review pilot: 50 conversations, rubric, correlation study | Ops/QA | M | Correlation >0.6 on 2+ metrics |
| 10 | Document evaluation runbook in `docs/operations/` | Dev | S | Alert thresholds defined |

### 7.3 Medium-Term (2–4 months)

| # | Action | Owner | Effort | Success Criteria |
|---|--------|-------|--------|------------------|
| 11 | Commerce metrics: session-level attribution, GA4 integration | Dev | L | Dashboard widget |
| 12 | OlaBench-style multi-dimensional eval | Dev | L | 6 dimensions measured |
| 13 | Dataset maintenance process (versioning, changelog) | Dev | M | Quarterly review |
| 14 | Knowledge gap → auto-suggest KB articles workflow | Product | M | Actionable suggestions |

### 7.4 Ongoing

| # | Action | Measurement |
|---|--------|-------------|
| 15 | Weekly eval on 5% production sample | Trend visible |
| 16 | Monthly regression on golden dataset | All core pass |
| 17 | Quarterly human calibration of LLM judges | Rubric updated |
| 18 | Quality panel in admin dashboard | Metrics surfaced |

---

## 8. Tool Selection Summary & Justification

### 8.1 Summary

| Tool | Use Case | Recommendation |
|------|----------|----------------|
| **DeepEval** | RAG + conversational metrics, CI integration, custom G-Eval | **Adopt** — comprehensive, pytest-like, active community |
| **RAGAS** | RAG faithfulness, relevancy, retrieval | Use via DeepEval or standalone |
| **Azure AI / OpenAI Evals** | If already on Azure ecosystem | Consider for synthetic data + eval |
| **Custom scripts** | Pipeline integration, ResponseDecisionTrace analysis | Build on top of Agent Red explainability |
| **Human review** | Calibration, edge cases | **Required** — complement to automation |

### 8.2 DeepEval vs. Alternatives

| Criterion | DeepEval | RAGAS (standalone) | LangSmith / Langfuse | Azure AI Studio Evals |
|-----------|----------|--------------------|----------------------|------------------------|
| **RAG metrics** | Yes (incl. RAGAS) | Yes (core) | Via custom evals | Custom + synthetic |
| **Conversational** | Knowledge retention, completeness, role adherence | No | Custom | Custom |
| **CI/CD** | pytest-native, `deepeval test run` | Script-based | Dashboard-centric | Azure pipeline |
| **Cost** | Open-source; optional cloud for reports | Open-source | Per-seat + usage | Azure subscription |
| **Maintenance** | Active (13.7k stars), Confident AI backing | Maintained | Vendor | Microsoft |
| **Azure OpenAI** | Supported (model config) | Manual integration | Via LangChain | Native |
| **Learning curve** | Low (pytest familiarity) | Low | Medium | Medium |

**Why DeepEval:** Single framework for RAG + conversational + custom G-Eval; pytest integration fits existing 2,646-unit-test CI; runs locally without cloud lock-in; can use Azure OpenAI for judge models. RAGAS alone is sufficient for retrieval/generation quality but does not cover conversational metrics. LangSmith/Langfuse excel at observability, not batch evaluation.

### 8.3 LLM-as-Judge Cost at Scale

| Scenario | Conversations/mo | Cost/judge call | Monthly cost |
|----------|------------------|------------------|--------------|
| 100% eval | 10,000 | ~\$0.015 (GPT-4o-mini) | ~\$150 |
| 10% sample | 10,000 | ~\$0.015 × 1,000 | ~\$15 |
| Golden dataset only | 50 runs/release | ~\$0.015 × 50 | ~\$0.75/run |
| Weekly sample 100 | 400/mo | ~\$0.015 × 400 | ~\$6 |

**Recommendation:** Do not run LLM-as-judge on 100% of production traffic. Use (a) golden dataset for CI regression, (b) 5–10% sampled production conversations for monitoring, (c) optional batch eval on demand. RAG metrics (faithfulness, relevancy) that use local models or cheaper APIs have lower marginal cost.

---

## 9. Implementation Risks & Mitigations

### 9.1 Automated Metrics vs. Human Judgment

**Risk:** Automated metrics (e.g., faithfulness, G-Eval correctness) disagree with human reviewers, leading to false confidence or wasted effort.

**Mitigation:**

- Run a **human correlation study** before scaling: score 50–100 conversations with both automated metrics and 2–3 human reviewers; compute Pearson/Spearman correlation. Target >0.6 for primary metrics.
- If correlation is low, refine criteria (G-Eval prompts) or choose different metrics; do not deploy automation as the sole quality gate.
- Document known failure modes where automation diverges (e.g., idiomatic vs. literal correctness).

### 9.2 Rating Indeterminacy (LLM-as-Judge)

**Risk:** Criteria admit multiple valid interpretations; forced-choice elicitation selects suboptimal judges (research: up to 31% worse).

**Mitigation:**

- Use **multi-label or graded ratings** where possible (e.g., "partially correct" vs. binary).
- Define criteria narrowly: "Response must cite at least one KB article; no unsupported product claims" vs. "Response is helpful."
- Validate judge prompts on a held-out set with known human labels before production use.
- Avoid over-reliance on a single judge; consider ensemble or human adjudication for borderline cases.

### 9.3 Alert Thresholds & Fatigue

**Risk:** Over-alerting on metric regressions leads to ignored alerts.

**Mitigation:**

- **Tiered thresholds:** Critical (page): e.g., faithfulness <0.5 on >20% of sampled conversations; Warning: trend down 2+ weeks; Info: weekly digest.
- **Baseline comparison:** Alert on delta from rolling 7-day baseline, not absolute values.
- **Actionable alerts:** Each alert links to a runbook (e.g., "Check KB coverage for topic X").
- **Cooldown:** No duplicate alert for same condition within 24–72 hours.
- Start conservative; tune thresholds after 2–4 weeks of observation.

---

## 10. Human-in-the-Loop: Sampling & Process

### 10.1 Sampling Strategy

| Strategy | Selection | Use Case |
|----------|------------|----------|
| **Random** | 5–10% of all conversations | General quality monitoring, calibration |
| **Stratified** | Proportional by status (active, escalated, error), intent, tenant | Representative coverage |
| **Edge-case** | Escalated, Critic failed, knowledge gaps, low intent confidence | Failure mode discovery |
| **Targeted** | New tenants, post-KB-update, post-config-change | Validation of changes |

**Recommendation:** Combine random (e.g., 5%) for baseline with edge-case oversampling (all escalated + sample of gaps) for actionable insight.

### 10.2 Reviewer Roles & Training

| Role | Responsibility | Training |
|------|-----------------|----------|
| **QA / Support lead** | Primary reviewer; applies rubric; flags for escalation | 2–4 hr rubric training; calibration session with 10 examples |
| **Product / Dev** | Spot-checks; interprets metrics; owns remediation | Overview + rubric; ad-hoc |
| **Merchant (optional)** | Brand/tone validation for their tenant | Self-serve; simple 1–5 scale |

**Rubric:** 5–7 dimensions (correctness, completeness, clarity, empathy, escalation appropriateness, brand alignment). Each dimension: 1–3 scale (fail / partial / pass) with clear definitions. Include 2–3 example conversations per dimension for calibration.

### 10.3 Feedback Loop to Model Improvement

1. **Triage:** Reviewer tags failure type (wrong KB, tone, missing escalation, hallucination, etc.).
2. **Aggregation:** Weekly report of failure-mode distribution.
3. **Prioritization:** Top 2–3 failure modes → backlog items (KB update, prompt change, escalation rule).
4. **Golden dataset:** Add 2–5 high-value failures to regression suite with expected behavior.
5. **Re-eval:** After fix, run golden + sample to confirm improvement.

---

## 11. Commerce Metrics: Attribution & Instrumentation

### 11.1 Attribution Challenges

**Multi-touch attribution** for chat-influenced conversion is notoriously hard:

- Customer may browse, chat, leave, return via paid ad, then purchase.
- Last-touch credit undervalues chat; first-touch overvalues acquisition channels.
- GA4 supports model comparison (last-touch, linear, time decay) but requires proper event setup.

**Pragmatic approach:**

- **Session-level:** Purchase within same browser session (e.g., 30 min) after chat → attribute to chat. Simple, undercounts delayed conversions.
- **UTM / campaign:** Tag chat-originated traffic; use GA4 segments. Requires widget to set UTM on outbound links.
- **A/B test:** Compare conversion rate for chat-enabled vs. chat-disabled storefronts (or time windows). More rigorous; requires experimentation capability.

### 11.2 Instrumentation in Existing Pipeline

| Metric | Where to instrument | Data source |
|--------|---------------------|-------------|
| **Chat-influenced conversion** | Widget / GA4 integration | `schema/fields.yaml` documents GA4 event (start, resolution, escalation, CSAT); add `conversion` event with order_id if available |
| **Product recommendation CTR** | Response generator / widget | Emit event when customer clicks product link from AI response; requires widget modification to track link clicks |
| **Cart recovery** | E-commerce integration | Requires Shopify Cart API or webhook; outside current pipeline |

**Recommendation:** Start with session-level attribution (chat → purchase within session) and GA4 segments. Defer full attribution modeling to a later phase.

---

## 12. Failure Mode Taxonomy & Unknown Unknowns

### 12.1 Observed Failure Modes (from Knowledge Gaps & Escalations)

| Failure Mode | Description | Detection | Priority |
|--------------|-------------|-----------|----------|
| **KB gap** | No relevant KB article; AI guesses or deflects | Escalated/gap conversations; `knowledge_results_count = 0` | High — add KB content |
| **Wrong retrieval** | Retrieved article irrelevant or outdated | Faithfulness / relevancy metrics; human review | High |
| **Hallucination** | AI invents facts (prices, policies) | Faithfulness vs. KB; human review | Critical |
| **Off-topic** | Correct but irrelevant (e.g., shipping answer to returns question) | Relevancy; intent misclassification | Medium |
| **Tone mismatch** | Too formal, too casual, or off-brand | Human review; G-Eval tone | Medium |
| **Over-escalation** | Escalated when AI could have resolved | Escalation rules; human review | Medium |
| **Under-escalation** | Not escalated when human was needed | Escalation handler config; post-resolution complaints | High |
| **Prompt injection / jailbreak** | Safety bypass | Critic (97.1% TP); red-teaming | Ongoing |

### 12.2 Unknown Unknowns

**Challenge:** Novel failure modes not in the taxonomy (e.g., new attack vector, edge-case intent, UX confusion).

**Strategies:**

1. **Periodic taxonomy review:** Quarterly, review random sample + edge cases; add new failure modes.
2. **Open-ended feedback:** Optional free-text "What could we improve?" in post-conversation survey.
3. **Diverse sampling:** Ensure review covers various intents, tenants, and time periods.
4. **Red-team exercises:** Quarterly adversarial testing with novel prompts.
5. **Monitor anomaly:** Alert when a previously unseen pattern appears (e.g., new intent cluster, sudden spike in "other" category).

---

## 13. Evaluation Dataset Strategy

### 13.1 Maintenance & Versioning

| Practice | Description |
|----------|-------------|
| **Version dataset** | Store `evaluation/datasets/response_quality_v{N}.json`; tag releases with dataset version |
| **Changelog** | Document additions, removals, and edits in `evaluation/CHANGELOG.md` |
| **Ownership** | Assign owner (Dev or QA) for dataset curation; review quarterly |
| **Deprecation** | Mark obsolete cases as `deprecated` rather than delete; retain for regression history |

### 13.2 Dataset Contents

- **Core (20–30):** FAQ, returns, shipping, privacy — must pass on every release.
- **Tiered (20–30):** Product-specific, edge cases — inform but don't block.
- **Regression (10+):** Historical failures — prevent recurrence.
- **Adversarial (10+):** Prompt injection, jailbreak, PII — Critic-focused.

### 13.3 Synthetic Data

- **Use:** Generate edge cases (e.g., "Customer asks about refund for gift" when policy is ambiguous).
- **Tools:** Azure AI Generative SDK, GPT-4 with few-shot, or templates.
- **Caution:** Synthetic data can drift from real distribution; validate with human review before adding to golden set.
- **Best practice:** Seed with 2–3 real examples; generate variations; manually filter 20–30% for quality.

---

## 14. Clarifications: Critic, Pipeline Scope, Integration

### 14.1 Critic vs. LLM-as-Judge

| Aspect | Critic (existing) | LLM-as-Judge (proposed) |
|--------|-------------------|--------------------------|
| **Purpose** | Safety gate — block harmful, inject, jailbreak, PII | Quality scoring — correctness, helpfulness, tone |
| **When** | Per response, real-time, blocking | Offline or sampled, non-blocking |
| **Failure** | Response withheld; escalation or fallback | Metric recorded; used for dashboards and alerts |
| **Overlap** | Both can flag "wrong" content | Critic = safety; Judge = quality. Complementary. |
| **Replacement?** | No — keep Critic for real-time guardrail | Judge augments for retrospective analysis |

**Summary:** Critic remains the in-line safety gate. LLM-as-judge is for evaluation, monitoring, and improvement — not for blocking.

### 14.2 Full Pipeline vs. Individual Agents

| Eval Type | Scope | Use Case |
|-----------|-------|----------|
| **End-to-end** | Full 6-agent pipeline, production-like | Regression, business metrics (resolution, escalation) |
| **Per-agent** | Intent, KR, RG, Critic in isolation | Debugging, optimization, component swap |
| **RAG-only** | KR + RG with mocked IC/context | Faithfulness, relevancy, retrieval quality |

**Recommendation:** Golden dataset runs **end-to-end** for regression. Add **per-agent** evals when debugging or comparing model/prompt variants. Use **RAG-only** for fast iteration on retrieval and generation.

### 14.3 ResponseDecisionTrace Integration

**Low-instrumentation cost:** `ResponseDecisionTrace` already captures:

- `knowledge_sources` (entry_id, title, relevance_score), `knowledge_query`
- `critic` verdict, `stage_attributions`, `total_latency_ms`, `total_cost_estimate`
- Conversation context (customer message, response)

**Use for eval:** Export traces from Cosmos; for faithfulness, re-fetch KB content by `entry_id` (or use stored chunk text if pipeline adds it to trace). Feed into DeepEval `LLMTestCase` with `input`, `actual_output`, and `retrieval_context`. No pipeline modification required for batch eval beyond optional trace enrichment. Optional: add `quality_score` field to trace if running inline sampled eval.

### 14.4 Pilot Approach

**Phase 0 (2 weeks):** Run faithfulness + answer relevancy on 100 conversations using ResponseDecisionTrace data. No new instrumentation. Goals: (a) establish baseline, (b) validate tooling, (c) identify top 3 failure modes. Success = metrics computed, report generated, 3+ actionable findings.

**Phase 1 (4 weeks):** Add 25 golden test cases; integrate into CI. Success = CI runs on PR, <5% flakiness, no regression on core cases.

**Phase 2 (6 weeks):** Human review pilot (50 conversations, 1 reviewer, rubric). Success = correlation study complete, rubric validated, feedback loop documented.

---

## 15. Success Criteria by Phase

| Phase | Success Criteria | Measurement |
|-------|------------------|-------------|
| **Immediate (0–2 wk)** | Response dataset populated; Faithfulness + Relevancy baseline | 20+ cases in dataset; metrics on 100 convos; report |
| **Immediate** | Critic adv-030 fixed | AGNTCY eval: Critic TP = 100% |
| **Short-term (1–2 mo)** | CI integration | `deepeval test run` passes on PR; <5% flakiness |
| **Short-term** | FCR proxy implemented | Metric in analytics API; documented |
| **Short-term** | Human review process live | 5% sampling; rubric; 1 correlation study |
| **Medium-term (2–4 mo)** | LLM-as-judge validated | Human correlation >0.6 on 2+ metrics |
| **Medium-term** | Commerce metrics (session attribution) | GA4 event + segment; dashboard widget |
| **Ongoing** | No regression on golden set | Monthly run; all core cases pass |
| **Ongoing** | Alert fatigue avoided | <2 critical alerts/week; 100% acknowledged |

---

## 16. References

### Internal

- `docs/architecture/PERSISTENT-CUSTOMER-MEMORY-METRICS.md` — Metrics framework, test cases, A/B methodology
- `docs/AGNTCY-BASELINE-VERIFICATION-REPORT.md` — Intent, escalation, Critic baselines
- `src/multi_tenant/response_explainability.py` — Decision trace schema
- `src/multi_tenant/admin_analytics_api.py` — Current analytics endpoints
- `src/multi_tenant/cost_model.py` — Per-conversation AI cost (~$0.0073)
- `src/multi_tenant/sla_monitoring.py` — Latency targets (P50/P95/P99)

### External

- DeepEval: https://github.com/confident-ai/deepeval
- RAGAS: https://github.com/explodinggradients/ragas
- OlaBench: arXiv 2510.22143 — Benchmarking Real-World Customer Service Dialogue
- Pedowitz Group — Evaluate Chatbot & Conversational AI Performance for Better CX
- Zendesk QA — AI Agent evaluation
- Loris AI — AI Agent Evaluation Guide 2025
- JudgeBench, JuStRank — LLM-as-judge validation (arXiv 2410.12784, 2412.09569)

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
