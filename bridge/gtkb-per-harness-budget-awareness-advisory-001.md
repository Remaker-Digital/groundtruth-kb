ADVISORY
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f5f66-9582-7f03-a3f1-3c75e6bd9d0a
author_model: GPT-5
author_model_version: 5
author_model_configuration: Codex desktop interactive session; owner-declared ::init gtkb pb; owner-directed ADVISORY bridge filing

bridge_kind: governance_advisory
Document: gtkb-per-harness-budget-awareness-advisory
Version: 001
Author: Owner-directed advisory prepared by Prime Builder (Codex, harness A)
Date: 2026-07-15 UTC
Mode: advisory report
Severity: high
Priority: high

# Per-Harness Budget Awareness Advisory

## Source

This non-dispatchable ADVISORY bridge artifact carries the owner-directed advisory deliberation and research completed on 2026-07-15. Its sources are the governed owner decisions, governing architecture/specification records, current-system checks, and external provider/industry references cited below.

Owner decisions captured during the advisory intake:

- `DELIB-20260715-HARNESS-BUDGET-LEDGER-SOURCE-OF-TRUTH`: GT-KB owns a normalized budget ledger; provider APIs reconcile but are not sole authority.
- `DELIB-20260715-BUDGET-POOLS-SEPARATE-FROM-HARNESSES`: budget pools are first-class records separate from harness IDs.
- `DELIB-20260715-BUDGET-AWARE-DISPATCH-TIERED-POLICY`: dispatch uses normal/warning/critical/exhausted/unknown tiered behavior.
- `DELIB-20260715-BUDGET-PROVIDER-ADAPTER-CREDENTIAL-BOUNDARY`: read-only provider adapters are optional and credential-minimal.

Earlier related deliberations: `DELIB-202665451`, `DELIB-202665456`, and `DELIB-BRIDGE-DISPATCH-OVERHAUL-D12-20260612`.

Known governing/implementation surfaces include `config/dispatcher/rules.toml`, `SPEC-SHIM-HARNESS-DISPATCH-TELEMETRY-001`, and `SPEC-TAFE-R6`.

External reference anchors used in the advisory research include the FinOps Framework, FinOps Unit Economics guidance, OpenTelemetry semantic conventions, OpenAI usage/project/credit/Codex usage docs, Anthropic Admin and rate-limit docs, OpenRouter credits/key-limit docs, Google Cloud Billing budgets and API caps, and Alibaba Cloud BSS/QueryBill/Model Studio/Quota Center docs.

## Claim

GT-KB can implement budget-aware harness dispatch, but the budget source of truth should not be per harness alone. It should be a normalized GT-KB budget-pool ledger where harnesses consume one or more provider/account/model pools. Provider APIs should reconcile that ledger where available, while manual owner-supplied plan terms and dispatch telemetry remain sufficient for operation when provider APIs are unavailable or incomplete.

The best design is ledger-first, pool-based, provider-adapter assisted, and dispatch-policy aware.

Need: GT-KB uses multiple harnesses and providers with different commercial agreements: monthly, weekly, hourly, mixed included capacity, and per-use/overflow pricing. Some budgets drain quickly; others are larger and slower. Dispatch should preserve quality while minimizing cost and avoiding unexpected failures from budget exhaustion.

## Owner Decision Needed

No owner decision is needed to file this ADVISORY. Implementation is not authorized by this artifact. Downstream Prime Builder disposition should choose whether to route the advisory into backlog/spec/project authorization and then file normal implementation proposals with Loyal Opposition GO before touching protected dispatcher, telemetry, config, CLI, dashboard, provider-adapter, credential-boundary, or harness-state surfaces.

## Recommended Prime Action

1. Route this ADVISORY through the governed advisory-disposition path.
2. Reconcile existing budget/cost-aware dispatch work before creating new backlog items.
3. If adopted, create or attach canonical specification/backlog/project records for budget-pool ledger, dispatch telemetry debiting, provider reconciliation, tiered dispatch policy, and budget CLI/status/dashboard surfaces.
4. File separate implementation proposals for protected edits, especially dispatcher config/selection, telemetry schema, provider adapters, credential handling, CLI, tests, and dashboards.
5. Keep this ADVISORY non-dispatchable; it is not a work packet, GO verdict, implementation report, or authorization to mutate protected paths.

## Classification Slot

Owner-directed governance advisory for Prime Builder disposition. Classification recommendation: `adopt` as a future governed program, with implementation deferred until normal project authorization, bridge proposal, Loyal Opposition GO, and implementation-start gates are satisfied.

## Existing Work And Constraints

- `config/dispatcher/rules.toml` already has a budget section, but `[budget] enabled = false`, budget caps are zeroed, and per-harness estimated dispatch cost is currently `0.0`.
- Existing config support includes model/pricing association and `gt bridge dispatch config set-model`.
- Existing tests mention cost-aware selection and budget config parsing/reporting, but the current implementation is not a complete budget ledger.
- `SPEC-SHIM-HARNESS-DISPATCH-TELEMETRY-001` already requires privacy-bounded telemetry with budget fields: turn budget, turns used, usage, cost, and unknown-not-zero treatment.
- `SPEC-TAFE-R6` calls for stage-attempt telemetry that can include model/provider, dispatch decision, timing, tokens/cost where available, outcome, and failure class.

External standards support a ledger plus reconciliation model. The FinOps Framework's Inform phase emphasizes cost, usage, efficiency data, allocation, reporting, forecasting, and budgeting. Its Unit Economics guidance ties strategic decisions and optimization to normalized unit costs. OpenTelemetry semantic conventions support consistent metric names, units, and attributes for budget telemetry.

## Provider Feasibility

| Provider / surface | What appears possible | Constraint |
| --- | --- | --- |
| OpenAI API Platform | Usage dashboard and Usage API support custom usage analysis; project budgets exist as soft thresholds. | Project budgets do not hard-stop API use. Scale Tier/project spend can show zero while org-level bundle cost applies. ChatGPT/Codex included allowance and credits appear partly surfaced through product settings rather than a documented public budget API. |
| Codex / ChatGPT agentic usage | Official docs indicate Codex usage varies by model/instances/automations/fast mode and usage limits can be monitored in Codex settings. Credits can apply after included usage for supported agentic features. | Treat as manual/UI or connector-assisted unless a stable API is available. Do not assume programmatic budget availability. |
| Anthropic / Claude | Admin API exposes Usage and Cost API, Claude Code Analytics API, and Rate Limits API. Docs distinguish spend limits from rate limits. | Requires organization/admin credentials and permission scoping. Rate limits are not the same as monthly spend budgets. |
| OpenRouter | `GET /credits` returns total credits purchased and used with a management key. `GET /key` can check key limits or remaining credits. | Needs management key for global credit view; API-key-level limits may not equal plan/account budget. |
| Google Cloud / Vertex / Gemini | Cloud Billing budgets can send notifications and programmatic controls; API quotas/caps can limit usage per service, day, minute, or user. | Budgets are billing controls and quota enforcement has latency; service quotas are not complete project-wide spend controls. |
| Alibaba Cloud / Model Studio | BSS OpenAPI/BOA can query bills and account billing state; QueryBill returns billing-cycle settlement data. Model Studio bills map API Key ID and workspace ID. Quota Center supports rate-limit visibility and alerts. | Settlement bills may lag real-time dispatch; available credit and quota data require RAM permissions and provider-specific reconciliation. |

## What Is Possible

GT-KB can model budget awareness as a multi-source accounting system:

1. Owner-supplied plan terms seed canonical pools.
2. Dispatch telemetry debits estimated or observed usage against pools.
3. Provider adapters reconcile actual usage/cost/credit/quota where available.
4. Freshness/confidence scores distinguish known, stale, and unknown states.
5. Dispatch policy uses the pool state as a quality/cost tie-breaker and blocker only under explicit thresholds.

This can work even when no provider exposes a real-time budget API because the local ledger can still forecast depletion and warn/route conservatively. Provider data improves accuracy; it should not be required for basic operation.

## Best Implementation Approaches

### 1. Normalized budget-pool ledger

Add first-class `budget_pool` records separate from harness IDs. A pool should model provider/account/project/workspace, model family or group, billing plan, refresh windows, included allowance, remaining allowance, overflow policy, overflow unit price, marginal in-allowance cost, strictness policy, thresholds, last reconciled time, and confidence. Harness records then map to one or more pools with usage weights and routing eligibility.

### 2. Dispatch telemetry debit pipeline

Every dispatcher-launched run should emit a privacy-bounded budget event with dispatch/correlation id, harness id and role, provider/model/pool id, timestamps, tokens/turns/tool calls where available, observed or estimated cost, confidence, budget debit, outcome, and failure class. It must not include prompt/message/tool-argument content. Unknown usage must be recorded as unknown, not zero.

### 3. Provider reconciliation adapters

Build small read-only adapters per provider: OpenAI API usage/cost where available; Codex/ChatGPT manual or connector-assisted usage import until a stable public API exists; Anthropic Admin Usage and Cost API, Claude Code Analytics API, and Rate Limits API; OpenRouter `/credits` and `/key`; Google Cloud Billing budgets/notifications and quota/cap views; Alibaba BSS/QueryBill, billing account credit, Model Studio bills, and Quota Center. Each adapter should report freshness, provider timestamp/window, amount used/remaining, rate/quota dimensions, permissions required, confidence, and reconciliation delta.

### 4. Tiered dispatch policy

Apply owner-selected pool states:

- Normal: route by quality/cost.
- Warning: prefer other pools but allow use when quality/need is high.
- Critical: require explicit override or no suitable alternative.
- Exhausted prepaid with overflow: route only if overflow is allowed.
- Exhausted without overflow: block.
- Unknown or stale: degrade confidence and prefer known-good pools; fail closed only for strict pools.

Budget policy should remain below hard role/independence/safety gates.

### 5. Forecasting, alerting, and serviceability

Add safe and operator budget views such as:

```text
gt bridge dispatch budget status --worker-safe
gt bridge dispatch budget status --operator
gt bridge dispatch budget forecast
gt bridge dispatch budget reconcile --provider <name>
```

Worker-safe views should expose only routing implication. Operator views can show pool ids, provider deltas, windows, thresholds, and adapter health. Forecasting should include drain pace by window, burn-down to refresh, projected exhaustion, allowance waste risk, marginal overflow cost, and per-work-item or per-stage unit economics where available.

## Recommended Sequence

1. Define `budget_pool` schema and harness-to-pool mapping.
2. Extend dispatch telemetry to debit local pools with observed/estimated/unknown cost states.
3. Implement safe and operator budget CLI views.
4. Add tiered dispatch policy using warning/critical/exhausted/stale states.
5. Add provider adapters incrementally, starting with APIs exposing clear data: OpenRouter credits/key, Anthropic Admin usage/cost, OpenAI API usage/cost where applicable, then Google/Alibaba billing/quota surfaces.
6. Add forecasting, alerts, reconciliation delta checks, and simulation tests.

## Non-Approval Statement

This ADVISORY is a non-dispatchable bridge artifact. It is not implementation approval, not a GO verdict, not a project authorization, not an implementation-start packet, and not permission to modify protected dispatcher, telemetry, configuration, provider, credential, CLI, dashboard, harness, source, or test surfaces. Any downstream implementation must proceed through normal GT-KB project authorization, bridge proposal, Loyal Opposition GO, work-intent, implementation-start, and verification gates.
