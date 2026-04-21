NEW

# B4 — wiki/Scaling-Analysis.md Hygiene Update

**Status:** NEW
**Author:** Prime Builder (Opus 4.7, in-session S302)
**Date:** 2026-04-18
**Backlog Slot:** B4 per owner work-through
**Prior:** `memory/work_list.md` B4 discipline: "stay scoped as documentation-hygiene around `wiki/Scaling-Analysis.md`; must NOT reopen WI-3171 implementation scope unless new evidence shows a live scaling mismatch."

## Scope

Reconcile stale scaling numbers in `wiki/Scaling-Analysis.md` against
current `scripts/deploy.py:SCALING_CONFIG` and `infrastructure/terraform/main.tf`
reality. Documentation-only changes; no code or terraform modifications.

## Observed Stale Numbers

### Current source-of-truth (code)

From `scripts/deploy.py:85-98` (SCALING_CONFIG):

| Container app | min | max | Notes |
|---|---|---|---|
| `agent-red-api-gateway` | 2 | **8** | Gateway (production) |
| `agent-red-staging` | 1 | 5 | Staging gateway |
| `agent-red-intent-classifier` | 2 | **6** | IC |
| `agent-red-knowledge-retrieval` | 2 | **6** | KR |
| `agent-red-response-generator` | 2 | **10** | RG |
| `agent-red-critic-supervisor` | 2 | **4** | Critic |
| `agent-red-escalation-handler` | 1 | **3** | Escalation |
| `agent-red-analytics-collector` | 1 | **2** | Analytics |
| `agent-red-slim` | 2 | **2** | SLIM (fixed) |

`infrastructure/terraform/main.tf:144`: gateway `max_replicas = 8` (matches deploy.py).

### Drift points in `wiki/Scaling-Analysis.md`

| Line | Current stale text | Reason stale |
|---|---|---|
| 3 | "Last updated: 2026-03-28 (gateway vs agent-container scaling clarification)" | Update timestamp on this edit |
| 29 | "With KEDA scaling to 20 replicas, the gateway layer supports ~10,000+ concurrent connections" | Gateway actually capped at 8, not 20 |
| 39 | "The chat pipeline is capped at 20 max replicas" | Post-containerization, there is no single "chat pipeline cap"; IC=6, KR=6, RG=10, Critic=4 are individual per-container caps. |
| 44-48 | Table "Required Replicas (at 2s/msg)" projecting 50/125 required for 2K/5K merchants against an obsolete 20-replica single-pipeline model | Math no longer applies — current architecture has per-agent caps summing to ~43 max replicas across the pipeline (2+6+6+10+4+3+2+2 = 35 agent replicas; with gateway 8, total 43). |
| 49 | "Raise `max_replicas` from 20 to 100+" | Reference to obsolete 20-cap |
| 120 | "Chat pipeline max replicas 20" | Should enumerate per-container: IC=6, KR=6, RG=10, Critic=4 |
| 121 | "Knowledge retrieval max replicas 10" | Actual KR cap = 6 |
| 122 | "Analytics processor max replicas 5" | Actual analytics-collector cap = 2 |
| 232 | "KEDA max replicas (20)" | Stale |

## Proposed Changes

### §1 — Update timestamp at line 3

Change "Last updated: 2026-03-28 (gateway vs agent-container scaling clarification)" to "Last updated: 2026-04-18 (wiki-scaling-analysis-hygiene — reconcile per-container caps with current SCALING_CONFIG)".

### §2 — Rewrite "Chat pipeline capped at 20 max replicas" narrative (lines 37-50)

Replace the single-pipeline-cap framing with per-container framing. New narrative:

> After S181-S183 agent containerization, the chat pipeline is no longer a single scaling unit. Each agent container scales independently under KEDA. Current per-container caps (from `scripts/deploy.py:SCALING_CONFIG`):
>
> | Agent | Min | Max | Role |
> |---|---|---|---|
> | api-gateway | 2 | 8 | Widget/admin ingress + orchestration + SSE |
> | intent-classifier | 2 | 6 | Non-streaming IC |
> | knowledge-retrieval | 2 | 6 | Non-streaming KR |
> | response-generator | 2 | 10 | Streaming RG (bottleneck for token rate) |
> | critic-supervisor | 2 | 4 | Quality oversight |
> | escalation-handler | 1 | 3 | Escalation routing |
> | analytics-collector | 1 | 2 | Post-conversation analytics |
> | slim | 2 | 2 | SLIM gateway (fixed) |
>
> **Total max pipeline capacity: ~41 container replicas** (8 gateway + 35 agent replicas).
>
> At ~2,000 merchants and the original 2s/msg model, the math needs the response-generator stage (the streaming bottleneck) to scale to ~25-50 replicas depending on peak hour concentration. That exceeds current RG max=10, so **RG cap is the new primary bottleneck at ~2,000 merchants scale**, replacing the obsolete 20-replica chat-pipeline cap from the pre-containerization analysis.
>
> **Fix:** Raise RG `max_replicas` from 10 to 30+ for 2,000-merchant scale, and gateway `max_replicas` from 8 to 20+. Configuration change only in deploy.py + terraform main.tf — same operational profile as the obsolete "raise 20→100" fix, just per-container targets.

### §3 — Update Hard Configuration Limits table (lines 118-133)

Replace lines 120-122 with per-container breakdown:

```
| api-gateway max replicas | 8 | SCALING_CONFIG (scripts/deploy.py) |
| intent-classifier max replicas | 6 | SCALING_CONFIG |
| knowledge-retrieval max replicas | 6 | SCALING_CONFIG |
| response-generator max replicas | 10 | SCALING_CONFIG |
| critic-supervisor max replicas | 4 | SCALING_CONFIG |
| escalation-handler max replicas | 3 | SCALING_CONFIG |
| analytics-collector max replicas | 2 | SCALING_CONFIG |
| slim max replicas | 2 | SCALING_CONFIG |
```

All other rows (orchestrator httpx, Shopify client, tier concurrent conversations, rate limits, pipeline deadline, response generator max tokens, embedding dimensions) remain unchanged — not in scope.

### §4 — Update Summary Table row (line 232)

Replace "KEDA max replicas (20)" with "Response-generator max replicas (10); gateway max replicas (8)" per the actual current primary bottlenecks.

### §5 — Mirror changes into `agent-red.wiki/Scaling-Analysis.md`

The `agent-red.wiki/` submodule is a git submodule pointing to the same
content published to GitHub wiki. Both copies must stay in sync.

`diff --brief` confirmed they were identical at session start; this
bridge's edits must land in both files verbatim.

## Files Touched

| File | Change kind | Est. delta |
|---|---|---|
| `wiki/Scaling-Analysis.md` | Timestamp + narrative rewrite (lines 37-50) + Config Limits table + Summary Table row | +~40 / -~20 lines |
| `agent-red.wiki/Scaling-Analysis.md` (submodule) | Mirror all changes verbatim | +~40 / -~20 lines |

**Total: 2 markdown files. No code, no tests, no KB.**

## Non-Scope (per work_list.md B4 discipline)

- **No changes to `scripts/deploy.py`**. `SCALING_CONFIG` is source-of-truth; wiki documents it.
- **No changes to `infrastructure/terraform/main.tf`**. Terraform authoritative; wiki documents it.
- **No changes to per-container `max_replicas` values**. Those are in scope of future scaling work (pre-v1.99 cap raises per "Tier 2 config changes" narrative) but NOT this bridge.
- **No changes to rate limit, Cosmos, TPM, or other non-replica config values.**
- **No new test additions.** This is documentation-only.
- **WI-3171 reopening** — explicitly forbidden per B4 discipline. Note: WI-3171 was reused by the deploy.py scaling full-coverage bridge (S289); the original "proposed WI-3171 for orphan tests" framing from POR is stale. B4 does not touch either interpretation.
- **KB changes** — no spec/test/work-item/deliberation mutations. Wiki hygiene only.

## Verification Plan

```text
# Pre-apply: confirm current wiki content matches the session-start snapshot
$ wc -l wiki/Scaling-Analysis.md agent-red.wiki/Scaling-Analysis.md
  246 wiki/Scaling-Analysis.md
  246 agent-red.wiki/Scaling-Analysis.md

# Diff the two copies (should be identical pre-edit)
$ diff --brief wiki/Scaling-Analysis.md agent-red.wiki/Scaling-Analysis.md
(empty output = identical)

# After apply: verify both files updated identically
$ diff --brief wiki/Scaling-Analysis.md agent-red.wiki/Scaling-Analysis.md
(empty output = still identical post-edit)

# Confirm new numbers match SCALING_CONFIG
$ grep -nE "api-gateway max replicas|response-generator max replicas" wiki/Scaling-Analysis.md
# Expect: lines citing SCALING_CONFIG values (8, 10 respectively)

# Compare to live deploy.py
$ grep -nE "max_replicas.: 8|max_replicas.: 10" scripts/deploy.py
# Expect: matches
```

No pytest/mypy/ruff implications (docs-only).

## Implementation Sequence

1. Apply §1 (timestamp) in `wiki/Scaling-Analysis.md`.
2. Apply §2 (narrative rewrite) in `wiki/Scaling-Analysis.md`.
3. Apply §3 (Config Limits table) in `wiki/Scaling-Analysis.md`.
4. Apply §4 (Summary Table row) in `wiki/Scaling-Analysis.md`.
5. Copy full file to `agent-red.wiki/Scaling-Analysis.md` (mirror per §5).
6. Verify `diff --brief` shows identical content.
7. Commit on `develop`: `docs(wiki): B4 — reconcile Scaling-Analysis.md with current SCALING_CONFIG + terraform per-container caps`.
8. File post-impl report.
9. On VERIFIED: push to `origin/develop`.

## Prior Deliberations

- DELIB-0826 (owner decision pausing F4 to proceed to B4).
- `memory/work_list.md` B4 discipline note (2026-04-17 prioritization).

## Owner Decisions Required

None. Defaults pinned:

- **Scope = reconcile numbers only** per B4 discipline (no narrative-voice or structure changes beyond the stale-number rewrite).
- **Both `wiki/` and `agent-red.wiki/` updated** to maintain sync invariant.
- **No spec/KB touch** per B4 discipline.

## Requested Verdict

**GO** to implement §1 + §2 + §3 + §4 + §5, or **NO-GO** with specific findings.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
