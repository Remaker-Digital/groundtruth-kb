# POR Step 16.C Stream D — Phantom-Only + Assertion-Only WI Creation

**Status:** NEW (proposal for Codex review)
**Author:** Prime Builder (Opus 4.6)
**Date:** 2026-04-16
**Session:** S297
**Repo:** Agent Red Customer Engagement (groundtruth.db)
**Bridge thread:** por-step16c-stream-d-phantom-wi-creation
**Umbrella:** `bridge/por-step16c-implemented-untested-remediation-002.md` (GO)

## Prior Deliberations

- `DELIB-0711` (S297): SPEC-GTKB-SCOPE owner-approved exception from test-evidence invariant.
- `DELIB-0712` (S297): Methodology review — Phase 1.5 pattern does not generalize.
- `DELIB-0713` (S297): **Owner decisions on 16.C scope** — explicitly rolls 15 δ' specs
  into Stream D instead of treating them as assertion-only verified (per Decision 2).

Relevant bridge precedent:
- `spec-hygiene-untested-verified-008` (VERIFIED): Phase 1.5 β-pattern WI creation
  for 9 non-SPA specs. This Stream D follows the same pattern at larger scale (34 WIs).
- `spec-hygiene-spa-remediation-006` (VERIFIED): SPA bulk remediation using
  `origin=hygiene` WIs with 1:1 source-spec linkage.

## Objective

Create exactly **34 hygiene work items** — one per spec — for all γ' and δ'
specs identified in the 16.B classifier. Each WI records a test-coverage gap
to be remediated later (likely in the backlog, not in this session). The
specs themselves remain at `implemented` status; no status mutations occur in
this stream.

This is the most mechanical of the four Stream 16.C proposals. The pattern is
inherited from `spec-hygiene-untested-verified-008`.

## Scope — Exact Spec ID Sets (per Codex Finding 3)

### γ' (gamma_prime) — 19 specs

Phantom-only evidence (no test_file paths ever, no assertion_runs):

```
SPEC-1707  Campaigns Agent — Marketing Campaign Information MCP Server
SPEC-1708  Bot Agent — External AI Agent Conversation MCP Server
SPEC-1709  Sales Agent — In-line Purchase Completion MCP Server
SPEC-1710  Gateway Agent — Human Escalation Connection MCP Server
SPEC-1711  Schedule Agent — Follow-up Activities and Event Notifications MCP Server
SPEC-1712  3rd-Party MCP Server Integrations — External Service Connections
SPEC-1864  Natural Language Escalation to Peer Agents
SPEC-1865  Agent Marketplace Discovery and Installation
SPEC-1866  Conversation-Level Agent Activation
SPEC-1867  Structured Answer Blocks
SPEC-1868  Transcript Continuity
SPEC-1875  Community Feedback Harvesting Loop
SPEC-1879  Phone Identity Channel: SMS OTP via Azure Communication Services
SPEC-1880  WhatsApp Escalation Channel: Deep-Link to Merchant WhatsApp
SPEC-1881  Tenant Display Name — human-readable tenant identifier for Superadmin
SPEC-1882  Superadmin Contact Requirement — hard provisioning gate
SPEC-2098  Deliberation archive: structured storage and semantic search
SPEC-2099  Pipeline lifecycle metrics: data model and collection
SPEC-2100  Pipeline lifecycle metrics: computed metrics and aggregation
```

### δ' (delta_prime) — 15 specs (per DELIB-0713 Decision 2)

Specs the owner explicitly chose NOT to grant assertion-only verification to:

```
SPEC-1653  Testable Element Dimension Taxonomy
SPEC-1740  Documentation: First-login magic link flow in setup guide
SPEC-1741  Documentation: Intent categories diagram legible in light and dark modes
SPEC-1742  Documentation: Knowledge retrieval technical detail in How It Works
SPEC-1743  Docs site landing page logo must use black text variant in light mode
SPEC-1744  Changelog must include entries for all production-deployed versions
SPEC-1772  Integration Framework — Admin UI Setup & Dashboard
SPEC-1773  Integration Framework — Cosmos DB Schema Extensions
SPEC-1775  Zendesk Integration — Full Helpdesk Adapter
SPEC-1776  Slack Integration — Channel Adapter for AI Bot
SPEC-1777  Google Docs Integration — Knowledge Source Adapter
SPEC-1778  Integration Framework — Internal Event Bus
SPEC-1799  Container Failure Resilience
SPEC-1800  Multi-Replica Agent Routing
SPEC-1872  Conversation Preview with Message Insights
```

**Total: 34 specs, 34 WIs to be created.**

Source of truth: `independent-progress-assessments/spec-hygiene/S297-phase16b-target-inventory.json`,
filtered where `classification.category IN ('gamma_prime', 'delta_prime')`.

## WI Creation Template

Each WI has the following fields:

```python
db.insert_work_item(
    title="Test coverage gap: {spec_title}",
    description=(
        "Per 16.B methodology review (DELIB-0712) and owner decisions "
        "(DELIB-0713), {spec_id} was classified as {category} — "
        "{rationale}. This WI tracks the test-coverage gap to be "
        "remediated per GOV-10 (live interfaces only)."
    ),
    origin="hygiene",
    source_spec_id="{spec_id}",
    priority="P2",   # post-production, non-blocking
    changed_by="prime_builder",
    change_reason="POR Step 16.C Stream D: bulk WI creation for phantom-only and assertion-only-rejected specs",
)
```

Where `{category}` is `γ'` or `δ'`, and `{rationale}` is:
- γ': "phantom-only evidence (no test_file paths, no assertion_runs)"
- δ': "assertion-only verification insufficient for behavioral requirement per DELIB-0713 Decision 2"

## Implementation Plan

1. **Load inventory**: Read `S297-phase16b-target-inventory.json`.
2. **Filter**: Select specs where `classification.category IN ('gamma_prime', 'delta_prime')`.
3. **Verify count**: Assert 34 items (19 γ' + 15 δ'). Fail fast if count differs.
4. **Pre-flight check**: For each spec, verify it exists in KB at `status='implemented'`
   and has no existing WI with `origin='hygiene'` + matching `source_spec_id`. Skip
   any that already have one; report skipped count.
5. **Batch insert**: Create WIs via `db.insert_work_item()` in a single session.
6. **Verify post-condition**: Query KB for WIs with `origin='hygiene'` AND
   `source_spec_id IN (34-id-set)` AND `changed_at >= session_start`. Expect
   34 − skipped_count rows.
7. **DB hash bracket**: Report pre/post SHA-256 of `groundtruth.db`.

## Files Changed

| File | Change Type | Description |
|------|------------|-------------|
| `groundtruth.db` | Write | 34 new work_items rows inserted (one per spec) |
| `independent-progress-assessments/spec-hygiene/scripts/create_stream_d_wis.py` | New | Script performing the batch WI creation (read inventory → insert) |

No source code changes. No test changes. No spec status mutations.

## Risks

- **Low:** WI creation pattern is proven (used in `spec-hygiene-untested-verified-008`
  and `spec-hygiene-spa-remediation-006`).
- **Low:** Spec set is frozen by the 16.B classifier inventory; no ambiguity.
- **Medium:** Some γ'/δ' specs may already have related WIs from prior cleanup
  attempts. Mitigation: step 4 pre-flight detects and skips these; post-impl
  report documents the skip list.

## Exit Criteria

1. 34 − skipped_count WIs inserted with `origin='hygiene'` and 1:1 `source_spec_id` linkage.
2. Post-impl report includes:
   - Full list of created WI IDs with source-spec IDs
   - Any skipped specs with reason (already had matching WI)
   - DB hash pre/post bracket
3. Classifier re-run shows no change to category counts (193/4/15/19/4) — Stream D
   does not mutate spec status, only adds WIs.
4. All 34 specs are covered (either a new WI created or a pre-existing one cited).

## Reconciliation Against Umbrella

Umbrella exit criteria require: "Stream D: 34 hygiene WIs open, 1:1 linkage to source specs."
This proposal meets that requirement modulo skipped duplicates (which still satisfy "WI open for this spec" even if not newly created).

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
