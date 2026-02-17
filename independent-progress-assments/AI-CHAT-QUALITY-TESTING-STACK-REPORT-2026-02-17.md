# AI Chat Quality Testing Stack Report

Date: 2026-02-17  
Project: Agent Red Customer Engagement  
Scope: Recommended production-grade AI chat quality testing framework and methodology for Azure-hosted, multi-tenant e-commerce support SaaS

## Executive Summary

For Agent Red, the best approach is a **hybrid evaluation stack**:

1. `azure-ai-evaluation` as the Azure-native backbone
2. OpenAI Evals methodology for regression discipline and judge-based evaluation patterns
3. Promptfoo for CI gate enforcement and red-team automation
4. RAGAS + TruLens for retrieval/groundedness diagnostics
5. LangSmith for dataset/evaluator operations and human annotation loops
6. Giskard for structured robustness and security testing

No single framework is sufficient for your failure surface (multi-tenant + RAG + streaming + external integrations + escalation workflows).

## Context-Specific Requirements for Agent Red

Agent Red quality testing must cover:

- Tenant isolation correctness
- RAG groundedness and retrieval quality
- Escalation precision/recall and routing correctness
- E-commerce domain correctness (policies, orders, returns, shipping context)
- Integration resilience (Shopify/Stripe/webhook-driven behavior)
- Safety and compliance outputs (PII handling, harmful output prevention)
- Cost-quality balance under load

## Recommended Framework Stack

## 1) Primary Backbone: Azure AI Evaluation SDK

- Use for: baseline quality and safety evaluation in Azure-aligned workflow
- Why: native fit for Azure OpenAI deployments and enterprise governance posture
- Role in stack: canonical evaluator runner and reporting anchor

Reference: https://pypi.org/project/azure-ai-evaluation/

## 2) Regression Discipline: OpenAI Evals Methodology

- Use for: versioned eval datasets, grader prompts, deterministic + model-judge combined scoring
- Why: strong pattern library for continuous model/prompt/tool regression testing
- Role in stack: release-candidate comparison and fail/pass policy inputs

References:
- https://platform.openai.com/docs/guides/evaluation-best-practices
- https://cookbook.openai.com/examples/evaluation/getting_started_with_openai_evals

## 3) CI/CD Gatekeeper: Promptfoo

- Use for: automated eval runs in CI on PRs and release branches
- Why: practical for test matrix execution and policy-based gate thresholds
- Role in stack: hard release gate and regression signal in pull requests

References:
- https://www.promptfoo.dev/docs/integrations/ci-cd/
- https://github.com/promptfoo/promptfoo

## 4) RAG Quality Layer: RAGAS + TruLens

- Use for: retrieval relevance, context quality, groundedness/faithfulness-style scoring, trace diagnostics
- Why: RAG-specific failure modes are often hidden by overall answer quality metrics
- Role in stack: dedicated RAG health signal and root-cause diagnostics

References:
- https://docs.ragas.io/en/latest/references/evaluate/
- https://www.trulens.org/docs/

## 5) EvalOps + Human Review: LangSmith

- Use for: annotation queues, evaluator management, dataset versioning, feedback loops
- Why: production quality requires human-in-the-loop adjudication for ambiguous cases
- Role in stack: continuous quality operations and reviewer workflow

Reference: https://docs.langchain.com/langsmith/evaluation-quickstart

## 6) Security/Robustness Layer: Giskard

- Use for: structured vulnerability tests (prompt injection, jailbreak, unsafe outputs, brittle behavior)
- Why: AI support bots are externally reachable and abuse-prone
- Role in stack: pre-release and periodic adversarial test battery

Reference: https://docs.giskard.ai/

## Suggested Architecture (Practical)

1. Data sources
- Golden test sets (curated synthetic + historical anonymized conversations)
- Tenant-segmented slices (Starter/Pro/Enterprise behavior profiles)
- Incident-derived regression cases (every P1/P2 defect becomes an eval)

2. Evaluation modes
- Offline batch evals (pre-merge, pre-release)
- Online sampled evals (post-release production monitoring)
- Shadow/canary evals for model or prompt changes

3. Scoring layers
- Deterministic checks (format, required fields, policy constraints)
- LLM-as-judge checks (helpfulness, relevance, clarity)
- RAG-specific checks (retrieval/context grounding)
- Safety checks (policy violations, PII leakage patterns)

4. Quality gate engine
- CI job computes scorecard deltas vs previous baseline
- Release blocked when threshold breaches occur
- Exceptions require explicit approval with incident ticket reference

## Required Core Metrics

## Release-Blocking Metrics

- `Intent classification accuracy` (overall + by top intent families)
- `Escalation precision/recall` (especially false negative risk)
- `Grounded answer rate` for RAG-backed responses
- `Hallucination/unsupported claim rate`
- `Policy/safety violation rate`
- `Tenant isolation failure rate` (must be effectively zero)
- `P95 response latency` and timeout/error rates

## Critical Post-Launch Metrics

- `Retrieval hit quality` (context relevance, top-k utility)
- `Conversation resolution quality` (successful/no-reopen proxy)
- `Fallback frequency` and fallback quality
- `Webhook/dependency fault impact` on response quality
- `Cost per successful conversation` by tenant tier and model

## Example Initial Gate Thresholds (Starting Point)

Use these as initial defaults, then tighten after 2-4 weeks of stable data:

- Intent accuracy: `>= 93%`
- Escalation precision: `>= 98%`
- Escalation recall: `>= 95%`
- Grounded answer rate (RAG-eligible prompts): `>= 92%`
- Hallucination rate: `<= 3%`
- Safety violation rate: `<= 0.5%`
- Tenant isolation violations: `0 tolerated`
- P95 end-to-end response latency: `<= 3.5s` (non-streaming equivalent benchmark)

## Note

Thresholds should be tuned by tier and conversation class (simple FAQ vs policy-sensitive vs order/escalation workflows).

## Evaluation Dataset Strategy

1. Build four dataset classes
- `Core commerce`: orders, shipping, returns, refunds, product questions
- `Policy-sensitive`: legal/compliance constraints, uncertain claims
- `Escalation-critical`: upset users, high-risk intents, manual handoff cases
- `Adversarial`: injection attempts, jailbreak patterns, data exfiltration prompts

2. Dataset governance
- Every severe production defect adds at least one permanent regression case
- Version datasets with semantic tags (`dataset-v2026.02.x`)
- Keep tenant-segmented slices to detect skew and unequal quality

3. Labeling
- Use clear rubrics with pass/fail criteria and tie-break rules
- Require double-review on safety and escalation edge cases

## Release Policy (Recommended)

1. PR-level checks
- Run reduced smoke eval suite on every PR touching chat/retrieval/escalation logic
- Block merge on material regression beyond tolerance window

2. Pre-release checks
- Run full offline suite (core + RAG + security + escalation)
- Compare against previous production baseline
- Require sign-off from engineering + operations owner

3. Post-release checks
- Canary sample live traffic for online eval
- Auto-rollback criteria for severe regression patterns

4. Weekly quality review
- Track trends, failure clusters, and root causes
- Convert top failure clusters into new fixed regression cases

## Mapping to Agent Red Components

- `src/chat/pipeline.py`: end-to-end response and orchestration quality evals
- `src/agents/*.py`: per-agent unit evals + contract tests
- `src/multi_tenant/*`: tenant isolation, policy enforcement, metering correctness checks
- `admin APIs`: escalation workflow correctness and operational auditability
- `integration modules`: Shopify/Stripe failure-path quality tests

## Comparison to SaaS Best Practice

Mature AI SaaS providers typically do the following:

- Treat evals as release gates, not occasional experiments
- Combine automated and human evaluation
- Maintain persistent adversarial/security test suites
- Tie model/prompt changes to explicit scorecard deltas
- Convert production incidents into permanent regressions

This recommendation aligns with that pattern and avoids the common anti-pattern of “single benchmark + manual spot checks.”

## Implementation Roadmap (Phased)

## Phase 1 (2-3 weeks): Foundation

- Stand up baseline offline eval runner
- Define initial golden dataset and rubrics
- Add CI smoke gates for major chat-path changes

## Phase 2 (2-4 weeks): Hard Gates + RAG Depth

- Integrate Promptfoo CI matrix
- Add RAGAS/TruLens diagnostics and dashboards
- Enforce pre-release full-suite gate

## Phase 3 (3-5 weeks): EvalOps + Security Maturity

- Add human annotation workflow (LangSmith)
- Add Giskard red-team cadence
- Implement post-release canary eval and rollback triggers

## Phase 4 (ongoing): Optimization

- Tune thresholds by tenant tier and intent class
- Add cost-quality optimization loops per model route
- Expand adversarial dataset from real incident patterns

## Risks If Not Implemented

- Quality regressions reaching production unnoticed
- Escalation failures (missed high-risk conversations)
- Hallucination/compliance exposure in merchant-facing support
- Uncontrolled LLM cost drift without quality gain
- Slower incident triage due to missing eval telemetry

## Final Recommendation

Adopt the hybrid stack and gate policy above, with Azure AI Evaluation as the anchor and Promptfoo as CI enforcement.  
Treat evaluation as a product reliability discipline (like testing + observability), not a one-time model benchmark.

---

## References

- Azure AI Evaluation SDK: https://pypi.org/project/azure-ai-evaluation/  
- OpenAI evaluation best practices: https://platform.openai.com/docs/guides/evaluation-best-practices  
- OpenAI Evals cookbook example: https://cookbook.openai.com/examples/evaluation/getting_started_with_openai_evals  
- Promptfoo CI/CD integration: https://www.promptfoo.dev/docs/integrations/ci-cd/  
- Promptfoo repository: https://github.com/promptfoo/promptfoo  
- RAGAS evaluate reference: https://docs.ragas.io/en/latest/references/evaluate/  
- TruLens docs: https://www.trulens.org/docs/  
- LangSmith evaluation quickstart: https://docs.langchain.com/langsmith/evaluation-quickstart  
- Giskard docs: https://docs.giskard.ai/

---

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
