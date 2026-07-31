# Per-Harness Budget Awareness Advisory

Date: 2026-07-15

Skills applied: grill-me-for-clarification, alternatives-investigation, advisory-proposal, loyal-opposition-report

Advisory status: ADVISORY ONLY - this report is not implementation approval and does not authorize protected source/configuration changes. Any implementation should proceed through the governed bridge/work-item path.

## Claim

GT-KB can implement budget-aware harness dispatch, but the budget source of truth should not be "per harness" alone. It should be a normalized GT-KB budget-pool ledger where harnesses consume one or more provider/account/model pools. Provider APIs should reconcile that ledger where available, while manual owner-supplied plan terms and dispatch telemetry remain sufficient for operation when provider APIs are unavailable or incomplete.

The best design is ledger-first, pool-based, provider-adapter assisted, and dispatch-policy aware.

## Need

GT-KB uses multiple harnesses and providers with different commercial agreements: monthly, weekly, hourly, mixed included capacity, and per-use/overflow pricing. Some budgets drain quickly; others are larger and slower. Dispatch should preserve quality while minimizing cost and avoiding unexpected failures from budget exhaustion.

The system therefore needs:

- normalized budget pools with refresh cadence and allowance terms;
- dispatch-time debits from telemetry;
- warning/critical/exhausted thresholds;
- provider reconciliation where possible;
- a routing policy that treats low, stale, unknown, and overflow states explicitly.

## Owner Decisions Captured

The following decisions were captured in the Deliberation Archive during this advisory intake:

- `DELIB-20260715-HARNESS-BUDGET-LEDGER-SOURCE-OF-TRUTH`: GT-KB owns a normalized budget ledger; provider APIs reconcile but are not sole authority.
- `DELIB-20260715-BUDGET-POOLS-SEPARATE-FROM-HARNESSES`: budget pools are first-class records separate from harness IDs.
- `DELIB-20260715-BUDGET-AWARE-DISPATCH-TIERED-POLICY`: dispatch uses normal/warning/critical/exhausted/unknown tiered behavior.
- `DELIB-20260715-BUDGET-PROVIDER-ADAPTER-CREDENTIAL-BOUNDARY`: read-only provider adapters are optional and credential-minimal.

Earlier related deliberations remain relevant:

- `DELIB-202665451`: cost model should be plan-aware and pace-aware, with weekly drain terms and allowance economics.
- `DELIB-202665456`: enforce cost-aware dispatch now using owner-supplied values; automated cost determination comes later.
- `DELIB-BRIDGE-DISPATCH-OVERHAUL-D12-20260612`: per-harness cost tier and budget cap belong in dispatch telemetry and tie-breaks, not above quality/independence gates.

## Known Constraints And Existing Work

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

### 1. Normalized Budget-Pool Ledger

Recommended as the foundation.

Add first-class `budget_pool` records separate from harness IDs. A pool should model:

- provider/account/project/workspace;
- model family or model group;
- billing plan name;
- refresh windows: monthly, weekly, hourly, daily, mixed;
- included allowance;
- remaining allowance;
- overflow allowed;
- overflow unit price;
- marginal in-allowance cost;
- strictness policy;
- warning/critical thresholds;
- last reconciled time and confidence.

Harness records then map to one or more pools with usage weights and routing eligibility. This avoids falsely treating a harness as the budget owner when several harnesses share an account, model plan, or credit bucket.

Why this is best: it matches the commercial reality and the owner's decision. It also supports future harness changes without rewriting the accounting model.

Risks/tradeoffs: requires data modeling and migration from today's per-harness budget placeholders.

### 2. Dispatch Telemetry Debit Pipeline

Recommended as the operational core.

Every dispatcher-launched run should emit a privacy-bounded budget event:

- dispatch id / correlation id;
- harness id and role;
- provider/model/pool id;
- start/end timestamps;
- tokens, turns, tool calls where available;
- observed provider cost if available;
- estimated cost otherwise;
- confidence: observed, estimated, manual, unknown;
- budget debit amount;
- outcome and failure class;
- no prompt/message/tool argument content.

The ledger should debit on completion and optionally reserve on dispatch start for strict pools. Unknown usage must be recorded as unknown, not zero.

Why this is best: it uses existing shim telemetry requirements and gives GT-KB a provider-independent local truth.

Risks/tradeoffs: estimates must be calibrated, and failed/partial jobs need clear debit semantics.

### 3. Provider Reconciliation Adapters

Recommended as optional accuracy enhancers.

Build small read-only adapters per provider:

- OpenAI API: usage/cost retrieval where available; account for soft project budgets and Scale Tier/org-level cost behavior.
- Codex/ChatGPT: manual or connector-assisted usage import until a stable public API exists.
- Anthropic: Admin Usage and Cost API, Claude Code Analytics API, Rate Limits API.
- OpenRouter: `/credits` and `/key` limit/credit endpoints.
- Google Cloud: Billing budgets/notifications plus API quota/cap views where applicable.
- Alibaba: BSS OpenAPI/QueryBill, billing account credit, Model Studio bill keys/workspaces, Quota Center.

Each adapter should report:

- freshness;
- provider timestamp/window;
- amount used/remaining;
- rate/quota dimensions;
- permissions required;
- confidence;
- reconciliation delta against local ledger.

Why this is best: provider data varies widely. Adapter modularity prevents one weak provider surface from weakening the whole budget system.

Risks/tradeoffs: credentials and permissions must remain owner-managed and minimal. Some provider data lags or is only soft-limit/billing-notification data, not real-time hard budget.

### 4. Tiered Dispatch Policy

Recommended for routing behavior.

Dispatch should apply the owner-selected pool states:

- Normal: route by quality/cost.
- Warning: prefer other pools but allow use when quality/need is high.
- Critical: require explicit override or no suitable alternative.
- Exhausted prepaid with overflow: route only if overflow is allowed.
- Exhausted without overflow: block.
- Unknown or stale: degrade confidence and prefer known-good pools; fail closed only for strict pools.

Budget policy should remain below hard role/independence/safety gates. It should influence selection and prevent predictable budget failures, but it should not allow role-ineligible dispatch or self-selection.

Why this is best: it turns budget data into predictable operational behavior without overfitting to one provider.

Risks/tradeoffs: strict pools can reduce availability when telemetry is stale. This is acceptable only when the owner marks the pool strict.

### 5. Forecasting, Alerting, And Serviceability

Recommended as the serviceability layer.

Add dashboard/CLI summaries:

```text
gt bridge dispatch budget status --worker-safe
gt bridge dispatch budget status --operator
gt bridge dispatch budget forecast
gt bridge dispatch budget reconcile --provider <name>
```

Worker-safe views should expose only the routing implication: normal, warning, critical, exhausted, unknown/stale, and safe next action. Operator views can show pool ids, provider deltas, windows, thresholds, and adapter health.

Forecasting should include:

- drain pace by window;
- burn-down to refresh;
- projected exhaustion time;
- allowance waste risk near refresh;
- marginal cost after included allowance;
- per-work-item or per-stage unit economics where available.

Why this is best: budget awareness is only useful if operators can see approaching exhaustion before jobs fail.

Risks/tradeoffs: forecasting can create false precision. Confidence and freshness must be visible.

## Recommended Sequence

1. Define `budget_pool` schema and harness-to-pool mapping.
2. Extend dispatch telemetry to debit local pools with observed/estimated/unknown cost states.
3. Implement safe and operator budget CLI views.
4. Add tiered dispatch policy using warning/critical/exhausted/stale states.
5. Add provider adapters incrementally, starting with the APIs that expose the clearest data: OpenRouter credits/key, Anthropic Admin usage/cost, OpenAI API usage/cost where applicable, then Google/Alibaba billing/quota surfaces.
6. Add forecasting, alerts, reconciliation delta checks, and simulation tests.

## Decision Needed

No further owner decision is needed for this advisory. Implementation requires a separate governed proposal/work item. The advisory recommendation is to implement budget pools and local ledger debiting first, then add provider adapters and dispatch routing policy as separate slices.

## Sources

- FinOps Framework Phases: https://www.finops.org/framework/phases/
- FinOps Unit Economics: https://www.finops.org/wg/introduction-cloud-unit-economics/
- OpenTelemetry Semantic Conventions: https://opentelemetry.io/docs/concepts/semantic-conventions/
- OpenTelemetry Metrics Semantic Conventions: https://opentelemetry.io/docs/specs/semconv/general/metrics/
- OpenAI API Usage Dashboard: https://help.openai.com/en/articles/10478918-api-usage-dashboard
- OpenAI Projects and Budgets: https://help.openai.com/en/articles/9186755-managing-your-work-in-the-api-platform-with-projects
- OpenAI credits for ChatGPT/Codex: https://help.openai.com/en/articles/12642688-using-credits-for-flexible-usage-in-chatgpt-freegopluspro-sora
- Codex rate card: https://help.openai.com/en/articles/20001106-codex-rate-card
- Anthropic Admin API: https://platform.claude.com/docs/en/manage-claude/admin-api
- Anthropic rate limits: https://platform.claude.com/docs/en/api/rate-limits
- OpenRouter credits API: https://openrouter.ai/docs/api/api-reference/credits/get-remaining-credits
- OpenRouter key limits API: https://openrouter.ai/docs/api/reference/limits
- Google Cloud Billing budgets: https://docs.cloud.google.com/billing/docs/how-to/budgets
- Google Cloud API usage caps: https://docs.cloud.google.com/apis/docs/capping-api-usage
- Alibaba Cloud BSS OpenAPI: https://www.alibabacloud.com/help/en/user-center/developer-reference/what-is-boa-1
- Alibaba Cloud QueryBill: https://www.alibabacloud.com/help/en/user-center/developer-reference/api-bssopenapi-2017-12-14-querybill
- Alibaba Cloud billing account overview: https://www.alibabacloud.com/help/en/user-center/fund-account-overview
- Alibaba Cloud Model Studio bill query and cost management: https://www.alibabacloud.com/help/en/model-studio/bill-query-and-cost-management
- Alibaba Cloud Quota Center: https://www.alibabacloud.com/help/en/quota-center/
- Alibaba Cloud throttling and quota management: https://www.alibabacloud.com/help/en/openapi/throttling-and-quota-management

