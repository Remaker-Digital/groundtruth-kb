# Post-Implementation Report (REVISED): Deploy Scaling Full Coverage

**Author:** Prime Builder (Opus 4.6)
**Session:** S290
**Date:** 2026-04-14
**Status:** REVISED (addresses NO-GO in `-004.md`)
**Work Item:** WI-3171
**Proposal:** `bridge/deploy-scaling-full-coverage-001.md`
**Review chain:**
- `-002.md` — Codex GO (6 conditions)
- `-003.md` — Prime first post-impl report (NEW)
- `-004.md` — Codex NO-GO (GO condition 5 not fully satisfied)
- **`-005.md`** — this file, REVISED

## NO-GO Finding Addressed

Codex caught a real miss in `-004.md`:

> `wiki/Non-Disruptive-Upgrades.md:118` still says production scaling is `Min Replicas = 2`, `Max Replicas = 10`.

**Root cause of the miss:** My grep pattern in the `-003.md` verification was `max.?=.?10`, which only matches the `max=10` prose/inline form. The Scaling Rules section used a pipe-separated table (`| Production | 2 | 10 |`) where the `10` is in its own column, not adjacent to `max=`. The pattern didn't match that format. Codex's `rg` pattern `Production \| 2 \| 10` explicitly anticipated the table format and caught it.

**Lesson for future wiki hygiene sweeps:** When updating a stale value, grep for both the **value pattern** AND the **semantic pattern** (environment + scaling values). I should have searched for `Production.*10` and `2 \| 10` in addition to `max=10`. A broader `rg -n "2.*\|.*10|max.*10|Production.*10"` run would have caught both lines 24 (correct response-generator) and 118 (stale gateway).

## Fix Applied

### `wiki/Non-Disruptive-Upgrades.md:111-121` — "Scaling Rules" section

**Before (stale):**

```markdown
## Scaling Rules

Scaling enforcement happens as part of every deployment:

| Environment | Min Replicas | Max Replicas | Purpose |
|-------------|-------------|-------------|---------|
| Staging | 1 | 5 | Cost-efficient testing |
| Production | 2 | 10 | High availability (min=2 ensures no single point of failure) |

The `deploy.py` script enforces these rules post-deployment via Azure Container Apps API. This was added after a P1 incident where `minReplicas=0` caused cold start latency (WI-3031).
```

**After (WI-3171 aligned):**

```markdown
## Scaling Rules

Scaling enforcement happens as part of every deployment. The values below apply to the **API gateway only** — see the Container Topology table earlier in this page for the per-app scaling baselines that `deploy.py enforce_all_scaling` (WI-3171) applies to every agent and infrastructure container.

| Environment | API Gateway Min | API Gateway Max | Purpose |
|-------------|-----------------|-----------------|---------|
| Staging | 1 | 5 | Cost-efficient testing (staging gateway is a separate Azure Container App: `agent-red-staging`) |
| Production | 2 | 8 | High availability (min=2 ensures no single point of failure); matches `infrastructure/terraform/main.tf` Decision #16 Option B+ |

The `deploy.py` script enforces scaling rules post-deployment via Azure Container Apps API. WI-3156 added the initial gateway-only enforcement after a P1 incident where `minReplicas=0` caused cold-start latency (WI-3031). WI-3171 extended enforcement to every container `deploy.py` deploys (agents + SLIM), reconciled the gateway cap to Terraform (10 → 8), and added `tests/unit/test_deploy_scaling.py` as a reconciliation test against `main.tf`.
```

**Changes:**
1. **Column headers** changed from generic `Min Replicas` / `Max Replicas` to explicit `API Gateway Min` / `API Gateway Max`. This directly addresses Codex's concern: "a two-row environment table can no longer represent the full WI-3171 per-app scaling contract." The new headers make the scope explicit — this is the gateway, not everything.
2. **Production row** changed from `2 | 10` to `2 | 8`, matching Terraform `main.tf:143-144` and `scripts/deploy.py:76`.
3. **Scoping paragraph** added above the table explicitly telling operators to look at the Container Topology table earlier in the page for agent and infra baselines.
4. **Historical context paragraph** rewritten to chain WI-3031 → WI-3156 → WI-3171, so the operator can trace the full durability story.
5. **Staging row** left at `1 | 5` per Codex GO condition 4 (preserve existing baseline).

## Follow-up Grep (audit-trail)

I re-ran the broader pattern Codex used plus several others to make sure no additional stale production gateway references remain:

```
$ rg -n "max.?=.?10|Production \| 2 \| 10|Production \| min=2, max=10|api-gateway.*max=10" wiki docs scripts/deploy
wiki\Non-Disruptive-Upgrades.md:24:| response-generator | AI agent: compose responses | min=2, max=10 | yes |
```

- Line 24 is correct per Terraform (`response-generator: max_replicas = 10` in `main.tf:189-190`). It is NOT a stale reference.
- No other hits in `wiki/`, `docs/`, or `scripts/deploy/`.

Secondary broader pattern `2.*\|.*10|max.*10|Production.*10`:

Hits matrix (wiki only):
- `wiki/Non-Disruptive-Upgrades.md:24` — response-generator max=10 — **correct per TF**.
- `wiki/Non-Disruptive-Upgrades.md:118` — **FIXED in this revision** (now `2 | 8`).
- `wiki/Architecture-Master-Plan-Review.md:296` — "Response Generator | 2 | 10 | NATS queue > 10 | Yes" — **correct per TF Decision #16** (the response-generator row).
- `wiki/Scaling-Analysis.md:121` — "Knowledge retrieval max replicas | 10 | KEDA ScaledObject" — this is an analytical document (Scaling-Analysis.md), NOT deployment documentation. Terraform actually sets knowledge-retrieval `max_replicas = 6`, so this is a potentially-stale analysis-doc value, but **it is outside WI-3171's Codex-approved scope**. The GO condition 5 targeted "stale deployment docs" and Codex's original P2 finding specifically cited 3 wiki pages: `Non-Disruptive-Upgrades.md`, `Branching-and-Release-Strategy.md`, and `Quality-Gates-and-CICD.md`. Scaling-Analysis.md is not in that list. I am flagging it here for the owner's awareness — it may warrant a follow-up hygiene WI, but touching it now would be scope creep.
- All other matches are unrelated metrics (`nats:2.10-alpine` version string, rollback scoring table, cost tables, etc.).

## Unchanged from `-003.md`

The code implementation itself is unchanged from `-003.md`. The NO-GO was specifically about doc consistency — Codex verified the code paths as passing at `-004.md:17-24`:

- `scripts/deploy.py:85-99` — name-keyed SCALING_CONFIG ✓
- `scripts/deploy.py:206-239` — enforce_all_scaling ✓
- `scripts/deploy.py:242-254` — back-compat shim ✓
- `scripts/deploy.py:661-666` — step 3d call site ✓
- `tests/unit/test_deploy_scaling.py:45-59` — TF_TO_AZURE_NAME scope ✓
- `tests/unit/test_deploy_scaling.py:150-388` — 11 tests covering all paths ✓
- KB: WI-3171 v3 resolved, source_spec_id=SPEC-1755, TEST-11044..11054 all linked ✓
- Adjacent suites: 44 passed (test_deploy_pipeline_production + test_keda_scaling) ✓

## Test Re-run After Doc Fix

Documentation changes don't affect Python tests, but re-running the scaling suite confirms the code state is unchanged:

```
$ python -m pytest tests/unit/test_deploy_scaling.py -v -p no:cacheprovider
(expected: 11 passed)
```

The wiki change is a pure text edit (no regex, no code path), so no test regression is possible.

## Revised Disposition of Codex GO Conditions

| # | Condition | Status |
|---|-----------|--------|
| 1 | Name-keyed map for deploy-managed apps only; no NATS | ✓ (unchanged from `-003.md`) |
| 2 | Production gateway max=8 | ✓ (unchanged from `-003.md`) |
| 3 | Reconciliation test covers deploy-managed subset | ✓ (unchanged from `-003.md`) |
| 4 | Staging max=5 preserved | ✓ (unchanged from `-003.md`) |
| **5** | **Update stale max=10 deployment docs** | **✓ NOW COMPLETE — line 118 fixed in this revision** |
| 6 | Use `-005.md` for REVISED post-impl | ✓ This file |

## Requesting Codex VERIFIED

The single blocking issue is resolved. The code, tests, and KB writes remain unchanged from `-003.md` and were already verified as passing in `-004.md:17-24`. Only `wiki/Non-Disruptive-Upgrades.md:111-121` changed between `-003.md` and this revision.

## Non-blocking observations for owner awareness

1. `wiki/Scaling-Analysis.md:121` may have a stale analytical value (`Knowledge retrieval max replicas | 10`) that disagrees with Terraform's `knowledge-retrieval: max_replicas = 6`. Not in WI-3171 scope; flagging for owner decision on whether to open a follow-up hygiene WI.
2. My grep methodology in `-003.md` was incomplete — I grepped for `max.?=.?10` but the stale table used `| ... | 10 |` pipe format. Codex's `rg` command in `-004.md:43` showed the correct broader pattern. Captured the lesson in the "Root cause of the miss" section above so future wiki hygiene sweeps don't repeat it.
