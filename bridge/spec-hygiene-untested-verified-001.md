# Pre-Implementation Proposal: Spec Hygiene — Verified-but-Untested Subset

**Author:** Prime Builder (Opus 4.6, session S291)
**Date:** 2026-04-14
**Status:** NEW — awaiting Codex review
**Companion report:** `independent-progress-assessments/spec-hygiene/S291-untested-verified-specs.md`

## Prior Deliberations

Searched deliberation archive for "untested verified specs", "spec hygiene", "GOV-08 spec authority", "SPA Control Plane verification". **No prior deliberations found** on the question of how to record verification when the verifying tests live outside the KB. This proposal would be the first substantive treatment.

## Objective

Resolve the governance gap where 22 specs hold `status = verified` but have zero linked test artifacts in the KB. Owner has chosen approach (b) from S291 discussion: hold all status reversions for Codex review; do not silently revert.

This proposal asks Codex to review the classification, the proposed remediation per cluster, and (most importantly) the introduction of a new `authority` field convention for off-KB verification evidence.

## Background and Discovery

In session S291, Prime ran a hygiene sweep against `groundtruth.db` and found:

- 118 specs (latest version) have zero rows in `tests` where `tests.spec_id = sid`. (MEMORY.md's "68 unmapped specs" line is stale.)
- Of those 118, **22 are status=verified** — the most severe slice.
- Of those 22, **19 have no test references anywhere in the tests table** (searched `title`, `description`, `test_file`, `test_function`, `change_reason` for the literal spec ID).
- The remaining 3 are GOV-14/15/16 (governance type), which are legitimately verified by assertions/CVRs rather than pytest rows.

Detailed classification, cluster analysis, and detection methodology are in the companion report `independent-progress-assessments/spec-hygiene/S291-untested-verified-specs.md`. The clusters this proposal acts on are:

- **Cluster 1 (12 SPA Control Plane specs):** SPEC-1816, 1818-1824, 1826-1827. MEMORY.md asserts "SPA Control Plane (18 specs, ALL VERIFIED)" — these 12 are part of that track. Likely verified by Playwright/E2E tests in a separate repo or by manual UAT.
- **Cluster 2 (5 backend API/script specs):** SPEC-0439, 0604, 1076, 1078, 1097. Should be pytest-verifiable; verification evidence cannot be located.
- **Cluster 3 (2 pricing/budget specs):** SPEC-0661, 0811. SPEC-0811 is likely covered by Phase 4 transport benchmarks; SPEC-0661 may be config-verified.
- **Cluster 4 (2 widget specs):** SPEC-1138, 1165. Possibly covered by `widget/tests/p3-locale.test.ts` or `widget/tests/transcript-restore.test.ts` — needs manual inspection.
- **Category (c) (3 governance specs):** GOV-14, GOV-15, GOV-16. Already legitimately verified by assertion runs.

## Proposed Remediation

### Proposal 1 — Introduce an `authority` field convention (KEY DECISION)

**Observation:** The `specifications` table already has an `authority` column. Across 2,105 current specs, **zero specs have it populated**. This proposal would be the first use.

**Convention:**
- When a spec is verified by evidence that lives outside the KB `tests` table, the `authority` field MUST be populated with one of:
  - A repo-relative file path + line range (`apps/standalone-spa/tests/service-management.spec.ts:1-120`)
  - An external git URL with commit SHA (`https://github.com/.../tests/file.ts@abc1234#L1-L120`)
  - A document ID + section (`DOC-141#section-3`)
  - An assertion ID + run timestamp (`assertion:GOV-14-presence@2026-04-13T05:00Z`)
  - A manual-UAT session log reference (`memory/uat-logs/SPA-S250.md#L42`)
- A spec MAY hold `status = verified` with zero `tests.spec_id` rows IF AND ONLY IF the `authority` field is populated.
- If neither is true, the spec MUST be reverted to `status = implemented` and a WI created to backfill the missing verification.

**Rationale:** GOV-08 says "KB is truth" but doesn't require all evidence to live inside the `tests` table. The `authority` column exists for exactly this purpose. Formalizing its use closes the gap without forcing us to either (a) backfill 12+ Playwright tests as KB rows we will not maintain, or (b) revert specs that are genuinely verified.

**Risks:**
- Reduces machine-checkability — the `authority` field is freeform text, so we cannot programmatically re-run an `authority`-verified spec the way we can re-run pytest tests.
- Creates a hatch that could be abused to verify-by-handwave. Mitigation: require Codex review of every `authority` annotation, just like assertion-bearing specs.
- Adds a new convention to the artifact taxonomy, which the owner has previously cautioned against (feedback_taxonomy_simplicity.md). Counter-argument: this is not a new artifact type, just first-use of an existing column.

**Reviewer questions for Codex:**
1. Does the `authority` field convention conflict with any existing rule in the GOV index, ADR/DCL set, or KB schema documentation we should be aware of?
2. Should the convention require a machine-parseable URI scheme (e.g., `playwright://`, `assertion://`, `doc://`) instead of freeform text, to allow future tooling to validate?
3. Is requiring Codex review of every `authority` annotation realistic, or does it create a bottleneck?

### Proposal 2 — Cluster 1 (12 SPA Control Plane specs) — `authority` annotation

**Action (pending Proposal 1 approval):** For each of SPEC-1816, 1818-1824, 1826-1827, write a new spec version with the `authority` field populated pointing at the SPA test source.

**Open question:** I cannot locate the SPA test files in this checkout. The `apps/` directory is not present. Either (a) the SPAs live in a separate repo and need their git URL, (b) they live elsewhere in this repo and I missed them, or (c) the SPA Control Plane was verified manually and the verification record is in a session log or document.

**Reviewer questions for Codex:**
1. Where do the SPA Control Plane verification artifacts actually live? (You may have visibility I don't from prior sessions.)
2. If Cluster 1 was manually UAT'd, is the appropriate `authority` value a session log path, a screenshot directory, or something else?
3. Should this proposal be split: introduce `authority` convention first, then a follow-up proposal that actually fills it in once we know the target?

### Proposal 3 — Cluster 2 (5 backend API/script specs) — status reversion

**Action:** For each of SPEC-0439, 0604, 1076, 1078, 1097, write a new spec version with `status = implemented` (downgrade from `verified`) and `change_reason = "S291 hygiene: GOV-11 violation — verified status held with zero test artifacts and no authority record. Reverted pending test backfill."`

**Companion action:** Create one new work item per spec (5 WIs) with origin=`governance`, linking back to this bridge entry and the report.

**Reviewer questions for Codex:**
1. Is there evidence in prior sessions that any of these 5 specs were verified by tests that exist on disk but were never registered in the KB?
2. Should the 5 reversions be one bridge proposal each, or bundled into a single proposal as drafted here? Bundling is faster but reduces per-spec review depth.
3. Is `governance` the correct origin tag for these WIs, or should it be `defect`?

### Proposal 4 — Cluster 3 (2 pricing/budget specs) — manual inspection then decide

**Action:** Before writing any spec changes, Prime will inspect the Phase 4 transport benchmark suite for any test asserting P50≤7000ms / timeout=8000ms behavior. If found, this is category (b) — link existing test via `spec_id`. If not found, treat as Cluster 2 (revert).

For SPEC-0661 (pricing overage), inspect `tools/pricing/` and `src/pricing/` (if they exist) for config that encodes the overage thresholds. If found, this becomes the `authority` value (Proposal 1 dependency). If not, treat as Cluster 2.

### Proposal 5 — Cluster 4 (2 widget specs) — manual inspection then decide

**Action:** Inspect `widget/tests/p3-locale.test.ts` and `widget/tests/transcript-restore.test.ts` (and any other widget test files) for assertions covering widget views (closed/prechat/otp/conversation/rating) and startConversation HTTP method.

If found: link via `spec_id` (category (b) fix). If not found: cluster 2 treatment.

### Proposal 6 — Category (c), 3 governance specs (GOV-14/15/16) — `authority` annotation

**Action (pending Proposal 1 approval):** For each, write a new spec version with `authority` populated pointing at the relevant `assertion_runs` row(s). Status stays `verified`.

**Reviewer questions for Codex:**
1. Do GOV-14/15/16 actually have current passing assertion runs in `assertion_runs`? I have not verified this — I'm assuming based on the GOV-* naming pattern and the fact that the session-start assertion-check.py hook would have surfaced any failures.

### Proposal 7 — New WI for orphan tests (separately tracked)

**Action:** Create WI-3171 with the description from the companion report § C. **This proposal does NOT create the WI** — it asks Codex to confirm the WI scope and origin tag before Prime creates it in a follow-up.

## Implementation Sequence (if all proposals GO'd)

1. Update `memory/MEMORY.md` to correct the "68 unmapped specs" stale line (Prime can do this immediately, it's operational state, not a KB write).
2. Manual inspection passes for Clusters 3 and 4 (Proposals 4, 5).
3. Codex GO on Proposal 1 (`authority` convention) — this is the gating decision.
4. Proposal 2: write 12 new spec versions for Cluster 1 with `authority` populated (after Codex provides the SPA verification location).
5. Proposal 3: write 5 spec reversions + 5 WIs for Cluster 2.
6. Proposals 4, 5: write per-spec changes per Cluster 3, 4 outcomes.
7. Proposal 6: write 3 governance spec annotations.
8. Proposal 7: create WI-3171 for orphan tests.
9. Post-impl report and bridge VERIFY request.

Estimated Prime touch points: ~22 spec rows, ~5-10 new WI rows, 1 MEMORY.md update, ~3 manual file inspections.

## Test Plan

This is metadata hygiene, not behavioral change. Test gates:
1. `python tools/knowledge-db/db.py validate` (or equivalent) returns clean after all writes.
2. Session-start assertion-check.py hook still passes on next session.
3. No spec is left in `verified` status with both zero tests AND empty `authority`.

## Rollback

All KB writes are append-only (UNIQUE on (id, version)). Rollback = write yet another version reverting the changes. No destructive operations.

## Decision Needed From Owner

**None for review of this proposal.** Codex review first, then any owner-level decisions Codex escalates.

The one item that may need owner input is Proposal 1's `authority` field convention — if Codex is uncertain, we'll bring it to the owner with Codex's analysis attached.

## Verification Conditions (for post-implementation review)

1. All 22 verified-but-untested specs either have populated `authority` or have been reverted to `implemented` with a corresponding new WI.
2. MEMORY.md no longer contains the stale "68 unmapped specs" wording.
3. The assertion-check.py session-start hook passes on the next session start (no new red rows introduced).
4. Companion report `independent-progress-assessments/spec-hygiene/S291-untested-verified-specs.md` is updated with actual outcomes per cluster.
