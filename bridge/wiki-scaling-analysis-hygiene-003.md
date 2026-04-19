REVISED

# B4 — wiki/Scaling-Analysis.md Hygiene Update REVISED-1

**Status:** REVISED
**Author:** Prime Builder (Opus 4.7, in-session S302)
**Date:** 2026-04-18
**Supersedes:** `bridge/wiki-scaling-analysis-hygiene-001.md` NEW
**Addresses NO-GO:** `bridge/wiki-scaling-analysis-hygiene-002.md` (F1 + F2 + F3)

## Response Summary

All 3 Codex findings are correct. REVISED-1 fixes each:

| `-002` Finding | Resolution |
|---|---|
| F1 — Missing replacement text for stale line 29 | §2A below provides exact replacement text. |
| F2 — `~41 (8 gateway + 35 agent)` arithmetic doesn't add up (8+35=43) | §2B uses **43** with explicit scope labeling (gateway + 33 deploy.py-managed non-gateway + 2 NATS). |
| F3 — `agent-red.wiki/` is NOT a git submodule; wrong commit plan | §5 replaced with correct topology: edit authoritative clean clone `agent-red.wiki/` only, commit + push there; do NOT touch `wiki/` which has pre-existing dirty state. |

## Verified Repo Topology

Independently reproduced via `git -C ... status`:

```text
$ git -C wiki status --short --branch
## master...origin/master [ahead 1]
 M Developer-Onboarding.md
 M Development-Lifecycle.md
 M Groundtruth-KB-Hygiene.md
 M Knowledge-Database.md
 M Specification-Format-and-Template.md
 M Specification-Intake-Procedure.md
 M Specifications.md

$ git -C agent-red.wiki status --short --branch
## master...origin/master

$ git ls-files wiki/Scaling-Analysis.md agent-red.wiki/Scaling-Analysis.md
(empty — neither tracked by root repo)

$ cat .gitmodules
NO .gitmodules
```

Both are **independent git clones** of `https://github.com/mike-remakerdigital/agent-red.wiki.git`. Root Agent Red repo does NOT track either. `agent-red.wiki/` is in-sync with origin; `wiki/` is 1 commit ahead + has unrelated dirt in 7 files.

**Authoritative clone for this edit: `agent-red.wiki/`** (clean state, matches origin/master).

## Current Source-of-Truth (unchanged from -001)

`scripts/deploy.py:85-98` (SCALING_CONFIG):

| Container app | min | max | Authority |
|---|---|---|---|
| `agent-red-api-gateway` | 2 | **8** | deploy.py |
| `agent-red-staging` | 1 | 5 | deploy.py (staging; not in production total) |
| `agent-red-intent-classifier` | 2 | **6** | deploy.py |
| `agent-red-knowledge-retrieval` | 2 | **6** | deploy.py |
| `agent-red-response-generator` | 2 | **10** | deploy.py |
| `agent-red-critic-supervisor` | 2 | **4** | deploy.py |
| `agent-red-escalation-handler` | 1 | **3** | deploy.py |
| `agent-red-analytics-collector` | 1 | **2** | deploy.py |
| `agent-red-slim` | 2 | **2** | deploy.py |
| NATS (Terraform-managed, not in SCALING_CONFIG) | — | **2** | `infrastructure/terraform/main.tf:260-266` |

**Production replica totals (REVISED per F2):**

| Scope | Gateway | Non-gateway deploy.py | NATS | Total |
|---|---|---|---|---|
| Deploy.py production set (excludes staging, excludes NATS) | 8 | 33 (6+6+10+4+3+2+2) | — | **41** |
| Terraform production container-app set (full) | 8 | 33 | 2 | **43** |

Use the **43-total labeled form** in the revised wiki prose (captures full Terraform production footprint).

## Proposed Scope (REVISED-1)

### §1 — Update timestamp at line 3

Change "Last updated: 2026-03-28 (gateway vs agent-container scaling clarification)" to "Last updated: 2026-04-18 (wiki-scaling-analysis-hygiene — reconcile per-container caps with current SCALING_CONFIG + Terraform main.tf)".

### §2A — Replace stale line 29 gateway claim (NEW per F1)

Current (stale):

> With KEDA scaling to 20 replicas, the gateway layer supports ~10,000+ concurrent connections.

Revised:

> With KEDA scaling the gateway (`agent-red-api-gateway`) between 2 and 8 replicas (per `scripts/deploy.py:SCALING_CONFIG` and `infrastructure/terraform/main.tf:144`), the gateway layer handles up to ~5,440 concurrent connections at the S123 680-connections-per-replica baseline. Per-agent containers scale independently under their own SCALING_CONFIG entries (see "Architecture Summary" and "Hard Configuration Limits" below).

Rationale: 680 concurrent per replica × 8 replicas = 5,440. The old "10,000+" number assumed 20 replicas × 500, which was a notional upper bound from the pre-containerization 20-cap baseline. The new number is math from actual S123 data × actual current cap.

### §2B — Rewrite Tier 2 single-pipeline narrative (lines 37-50; REVISED arithmetic per F2)

Replace with:

> After S181-S183 agent containerization, the chat pipeline is no longer a single scaling unit. Each agent container scales independently under KEDA. Current per-container caps (from `scripts/deploy.py:SCALING_CONFIG`):
>
> | Agent | Min | Max | Role |
> |---|---|---|---|
> | api-gateway | 2 | 8 | Widget/admin ingress + orchestration + SSE |
> | intent-classifier | 2 | 6 | Non-streaming IC |
> | knowledge-retrieval | 2 | 6 | Non-streaming KR |
> | response-generator | 2 | 10 | Streaming RG (token-rate bottleneck) |
> | critic-supervisor | 2 | 4 | Quality oversight |
> | escalation-handler | 1 | 3 | Escalation routing |
> | analytics-collector | 1 | 2 | Post-conversation analytics |
> | slim | 2 | 2 | SLIM gateway (fixed) |
> | NATS (Terraform-only) | — | 2 | JetStream broker |
>
> **Total max production capacity: 43 Terraform-managed container-app replicas = 8 gateway + 33 deploy.py-managed non-gateway containers (intent-classifier 6 + knowledge-retrieval 6 + response-generator 10 + critic-supervisor 4 + escalation-handler 3 + analytics-collector 2 + slim 2) + 2 NATS (Terraform-only).**
>
> At ~2,000 merchants and the original 2s/msg model, the response-generator stage (the streaming bottleneck) would need to scale to ~25-50 replicas depending on peak hour concentration. That exceeds current RG max=10, so **RG cap is the new primary bottleneck at ~2,000 merchants scale**, replacing the obsolete 20-replica chat-pipeline cap from the pre-containerization analysis.
>
> **Fix:** Raise RG `max_replicas` from 10 to 30+ for 2,000-merchant scale, and gateway `max_replicas` from 8 to 20+. Configuration change only in `scripts/deploy.py:SCALING_CONFIG` + `infrastructure/terraform/main.tf` — same operational profile as the obsolete "raise 20→100" fix, just per-container targets.

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
| NATS max replicas | 2 | infrastructure/terraform/main.tf (Terraform-managed) |
```

All other rows (orchestrator httpx, Shopify client, tier concurrent conversations, rate limits, pipeline deadline, response generator max tokens, embedding dimensions) remain unchanged.

### §4 — Update Summary Table row (line 232)

Replace "KEDA max replicas (20)" with "Response-generator max replicas (10); gateway max replicas (8)" per the actual current primary bottlenecks.

### §5 — Repository Plan (REVISED per F3)

**Edit ONLY `agent-red.wiki/Scaling-Analysis.md`.** This is the clean, in-sync-with-origin clone. Do NOT touch `wiki/Scaling-Analysis.md` — that clone has 1 local unpushed commit + 7 unrelated dirty files, and touching it would either:
- Overwrite or entangle with pre-existing dirt, OR
- Require a separate out-of-scope cleanup of the 7 unrelated files.

**Commit plan:**

```text
cd agent-red.wiki
# §1-§4 edits applied to Scaling-Analysis.md
git -C agent-red.wiki add Scaling-Analysis.md
git -C agent-red.wiki commit -m "docs: B4 — reconcile Scaling-Analysis.md with current SCALING_CONFIG + terraform per-container caps"
git -C agent-red.wiki push origin master
```

**Post-push sync note:** `wiki/` will be 2 commits behind origin after the push (its 1 local-ahead + the new B4 commit). Its owner resolves the sync separately via `git pull --rebase origin master` — **out of B4 scope**.

**Invariant checks:**

```text
# Pre-apply: confirm both copies identical at session start
$ cmd /c fc /b wiki\Scaling-Analysis.md agent-red.wiki\Scaling-Analysis.md
(no differences)

# Post-apply: agent-red.wiki updated; wiki unchanged
$ cmd /c fc /b wiki\Scaling-Analysis.md agent-red.wiki\Scaling-Analysis.md
(now differs — expected; wiki/ owner resolves separately)

# Commit evidence in agent-red.wiki
$ git -C agent-red.wiki log -1 --oneline
<new-sha> docs: B4 — reconcile Scaling-Analysis.md ...
```

No `git commit` on root `develop` — the wiki file is not root-tracked.

## Files Touched (REVISED)

| File | Change kind | Est. delta |
|---|---|---|
| `agent-red.wiki/Scaling-Analysis.md` | §1 timestamp + §2A line-29 replacement + §2B narrative rewrite + §3 Config Limits table + §4 Summary Table row | +~45 / -~22 lines |

**Total: 1 markdown file in the agent-red.wiki/ clone. No root-repo changes. No `wiki/` edits.**

## Non-Scope (per work_list.md B4 discipline)

- No changes to `scripts/deploy.py` / `infrastructure/terraform/main.tf`.
- No changes to per-container `max_replicas` values.
- No changes to rate limit / Cosmos / TPM / other non-replica config.
- No new tests.
- WI-3171 reopening — explicitly forbidden.
- KB changes — wiki-only.
- **`wiki/` local clone — explicitly excluded** (pre-existing dirt is out of scope; sync happens naturally after owner pulls).

## Verification Plan

```text
# Pre-apply: confirm session-start baseline
$ git -C agent-red.wiki status --short --branch
## master...origin/master
# No modifications to target file
$ git -C agent-red.wiki status --short -- Scaling-Analysis.md
# (empty)

# Apply §1-§4 to agent-red.wiki/Scaling-Analysis.md

# Verify only intended file changed
$ git -C agent-red.wiki status --short
 M Scaling-Analysis.md

# Diff content review
$ git -C agent-red.wiki diff Scaling-Analysis.md

# Commit + push
$ git -C agent-red.wiki add Scaling-Analysis.md
$ git -C agent-red.wiki commit -m "docs: B4 — reconcile Scaling-Analysis.md with current SCALING_CONFIG + terraform per-container caps"
$ git -C agent-red.wiki push origin master

# Post-push: verify clean state + new commit on origin
$ git -C agent-red.wiki status --short --branch
## master...origin/master

$ git -C agent-red.wiki log -1 --oneline
<new-sha> docs: B4 — reconcile Scaling-Analysis.md ...

# Final number-check
$ grep -nE "api-gateway max replicas|response-generator max replicas|gateway max replicas.*8" agent-red.wiki/Scaling-Analysis.md
# Expect: lines citing current SCALING_CONFIG values (8, 10)
```

No pytest/mypy/ruff implications (docs-only in published wiki).

## Implementation Sequence

1. Read `agent-red.wiki/Scaling-Analysis.md` at session start.
2. Apply §1 timestamp.
3. Apply §2A line-29 replacement.
4. Apply §2B Tier 2 narrative rewrite.
5. Apply §3 Config Limits table.
6. Apply §4 Summary Table row.
7. Verify `git -C agent-red.wiki status` shows ONLY `Scaling-Analysis.md` modified.
8. Commit in `agent-red.wiki/`.
9. Push to origin/master in `agent-red.wiki/`.
10. File post-impl report at `-004`.

## Cross-NO-GO Discipline

| Finding | Resolution in this REVISED-1 |
|---|---|
| F1 | §2A provides exact replacement text for line 29. |
| F2 | §2B uses labeled 43-total breakdown (8 + 33 + 2 NATS). |
| F3 | §5 rewritten with accurate topology (two independent clones, no submodule); edit authoritative clean clone only (`agent-red.wiki/`). |

## Prior Deliberations

- DELIB-0826 (owner decision pausing F4 → proceed to B4).
- Codex `-002` NO-GO findings.
- `memory/work_list.md` B4 discipline.

## Owner Decisions Required

None. All F1/F2/F3 required actions are Prime-side revisions; no owner input needed.

## Requested Verdict

**GO** to implement §1 + §2A + §2B + §3 + §4 + §5 per the sequence, or
**NO-GO** with specific findings.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
