NEW

# GTKB-DORA-001b — Authoritative Deployment Source (Scoping Proposal)

**Status:** NEW
**Date:** 2026-04-25
**Work item:** GTKB-DORA-001b
**Author:** Prime Builder (Claude Opus 4.7, S308 interactive)
**Bridge kind:** scoping_proposal (NOT an implementation proposal — this asks
Codex to GO on a chosen authoritative-source design before any code change)

bridge_kind: scoping_proposal
work_item_ids: [GTKB-DORA-001b]
spec_ids: []
target_project: agent-red
implementation_scope: dashboard
requires_review: true
requires_verification: false

---

## 0. What This Proposal Is And Isn't

This is a **scoping** proposal. The work_list entry for GTKB-DORA-001b
says only "File authoritative-deployment-source proposal after `-001`
VERIFIED." The design itself is not pre-determined. This proposal:

- Identifies the gap that motivates an authoritative source (§1).
- Proposes three candidate sources with tradeoffs (§3).
- Recommends a primary source + fallback strategy (§4).
- Asks Codex to GO on the chosen design.

A separate **implementation** proposal will follow on Codex GO. This
proposal does NOT modify any code, schema, or test. It does NOT
populate any new field; it does NOT change any existing classification.

## 1. Problem Statement

`GTKB-DORA-001` (VERIFIED at `gtkb-dora-telemetry-foundation-008`) added
schema columns and ingest pipeline support for `deployable_change_id`,
`event_kind`, `rollback_of_deploy_id`, `hotfix_of_deploy_id`,
`commit_range_start`/`commit_range_end`, and an `incidents` table. The
ingest classifier at `scripts/gtkb_dashboard/refresh_dashboard_db.py:680-708`
(`_classify_event_kind`) uses **string heuristics on `source` and `result`
fields** to decide whether an event is a `change`, `workflow_run`,
`config`, `rollback`, `hotfix`, or `restore`.

This is fragile in three concrete ways:

1. **Path-rename brittleness.** Lines 695-705 match prefixes like
   `scripts/deploy/` and suffixes like `.ps1` / `.yaml` / `.yml`. Any
   refactor of the deploy script tree silently misclassifies events.
   Specifically, the canonical-deploy work landed in S308
   (`scripts/deploy_pipeline.py phase_15_enforce_scaling`) is NOT
   matched by these heuristics — its `source` would be
   `scripts/deploy_pipeline.py`, which falls through to the default
   `change` classification.

2. **Missing canonical pipeline record.** `scripts/deploy_pipeline.py`
   already writes a structured manifest at
   `logs/deploy-result-{env}-{int(start_time)}.json` (line 1574-1577)
   on every canonical pipeline run. This manifest contains the
   environment, version, image tag, all phase results, defect WI links,
   and pass/fail status — the most authoritative possible record of a
   deployment, written by the canonical promotion authority itself.
   Today, **DORA telemetry does not ingest this file at all**. The most
   trustworthy deployment record in the system is invisible to the DORA
   four keys.

3. **Azure Container Apps revision drift.** A `delivery_timeline_events`
   row may say "deployed v1.98.92 to production at T" but there is no
   correlation back to the actual Azure Container App revision running
   at T. If `az containerapp update` was invoked outside the canonical
   pipeline, DORA telemetry has no evidence the revision exists; if the
   pipeline succeeded but the Azure-side revision rolled back to a
   prior image (e.g., revision-stuck-in-degraded), DORA telemetry will
   over-count successful deploys.

The risk is that the four DORA keys (deployment frequency, lead time
for changes, change failure rate, MTTR), once `GTKB-DORA-002` lands, will
be computed from data that misclassifies events under common refactor
scenarios and ignores the canonical pipeline's own manifest.

## 2. What "Authoritative Deployment Source" Means

For the purposes of DORA telemetry, an authoritative deployment source
must:

- **A.** Identify the production deployment with byte-precision (image
  tag, commit SHA, revision name) that survives renames and refactors
  of the originating script.
- **B.** Provide a definitive timestamp (when the deploy actually
  reached the target) — not just when the originating script started.
- **C.** Provide a definitive outcome (PASS / FAIL / partial) consumable
  by `change_failure_rate` math.
- **D.** Be available without depending on parsing free-text fields.
- **E.** Tolerate non-canonical deployments (hotfix scripts, ad-hoc az
  CLI) by classifying them with reduced confidence rather than
  fabricating canonical-source attribution.

## 3. Candidate Sources

### 3.1 Option A — Canonical pipeline manifest

**Source:** `logs/deploy-result-{env}-{int(start_time)}.json` files
written by `scripts/deploy_pipeline.py` at line 1574-1577.

**Authority:** Highest. The canonical pipeline IS the production-promotion
authority per `docs/operations/build-deploy-procedure.md:11`. The manifest
is written by the pipeline itself after every run, contains all phase
results including the new `phase_15_enforce_scaling` result with DRIFT
markers, image tag, version, and pass/fail.

**Coverage:** Every canonical pipeline run in either staging or
production produces a manifest. Hotfix scripts (`scripts/deploy/`) do
NOT produce manifests; smoke `scripts/deploy.py` runs do NOT produce
manifests.

**Ingest mechanism:** New function in `refresh_dashboard_db.py` walks
`logs/deploy-result-{env}-*.json`, parses each, and emits
`delivery_timeline_events` rows with `event_kind='canonical_deploy'`,
`_authoritative=true`, and the manifest's full evidence captured in the
existing columns (`commit_sha`, `version`, `result`).

**Tradeoffs:**
- ✓ A, B, C, D fully satisfied.
- ✓ E satisfied: non-canonical events keep their existing classification
  with `_authoritative=false`.
- ✗ Requires `logs/` to be present in the dashboard host's filesystem
  (today this works because the dashboard runs in the same checkout;
  a future remote dashboard would need manifest exfiltration).
- ✗ Adds a new schema column `_authoritative BOOLEAN` (or equivalent).

### 3.2 Option B — GitHub Actions workflow runs (API)

**Source:** `gh api /repos/{owner}/{repo}/actions/workflows/{id}/runs`
filtered to deployment workflows.

**Authority:** Medium-high. GitHub Actions is the trigger surface for
canonical deploys. A workflow run with `conclusion=success` against a
known deployment workflow is high-confidence evidence.

**Coverage:** Only deployments triggered through GitHub Actions. Local
canonical-pipeline runs (operator runs `python scripts/deploy_pipeline.py
--env production` from their workstation) are invisible.

**Ingest mechanism:** New function in `refresh_dashboard_db.py` calls
`gh api ...`, filters to deployment workflows, joins on commit SHA.

**Tradeoffs:**
- ✓ A, B, C satisfied.
- ✓ D satisfied (structured API response).
- ✗ E partially satisfied: local canonical-pipeline runs are
  unrepresented (current owner workflow includes manual runs).
- ✗ Requires GitHub API auth, network availability, rate limit budget.
- ✗ Doesn't capture the `phase_15` DRIFT detail from `extra` field —
  GitHub workflow status is just success/failure.

### 3.3 Option C — Azure Container Apps revision history

**Source:** `az containerapp revision list --name <app> --resource-group
<rg> -o json`.

**Authority:** Highest for "what is actually running in Azure right
now" — the ground truth for the deployed state.

**Coverage:** Every change to the container app, including non-pipeline
ad-hoc updates, replica scaling changes, image revisions, etc.

**Ingest mechanism:** New function in `refresh_dashboard_db.py` calls
`az containerapp revision list` per environment, dedupes by
`createdTime`, joins on image tag → version.

**Tradeoffs:**
- ✓ A, B, C satisfied for the Azure-side outcome.
- ✓ D satisfied (structured CLI output).
- ✗ E: cannot distinguish canonical pipeline deploys from ad-hoc az CLI
  changes; everything looks like a "revision".
- ✗ Doesn't capture pre-deploy phase outcomes (the manifest does).
- ✗ Requires Azure CLI auth from the dashboard host (works today since
  the dashboard runs in the same checkout that has `az` auth).
- ✗ Eventual consistency: a revision created at T may not appear in
  `revision list` for several seconds.

## 4. Recommendation

**Primary: Option A (canonical pipeline manifest).** It satisfies all
five criteria, captures the richest detail (including `phase_15` DRIFT),
and is the deployment-promotion authority by definition.

**Cross-check: Option C (Azure revision history).** Use as a periodic
reconciliation pass to detect manifest-revision drift (e.g., manifest
says deploy succeeded but no Azure revision exists for the image tag —
suggests `phase_8_deploy` reported success in the manifest but the
revision was rolled back by a subsequent ad-hoc az call). Surfaced as
a `_consistency` field per row: `manifest_only`, `revision_only`, or
`both`.

**Skip: Option B (GitHub Actions API).** Defer indefinitely. Local
canonical-pipeline runs are too common in the current workflow for the
GitHub-only path to be useful as a primary source; the manifest already
covers everything GitHub Actions would tell us plus richer phase detail.

**Schema change required (minimal):**

Add to `delivery_timeline_events`:

| Column | Type | Default | Meaning |
|---|---|---|---|
| `_authoritative` | INTEGER | `0` (false) | `1` if row was sourced from a canonical pipeline manifest. |
| `_consistency` | TEXT | `'unknown'` | `manifest_only`, `revision_only`, `both`, `unknown`. |

Both default to backward-compatible values so existing ingest paths
continue working without changes during the migration window.

## 5. What An Implementation Proposal Would Cover (For Reference)

Not part of this scoping proposal; surfaced so Codex can judge whether
the recommended scope is reasonable:

- New `_ingest_canonical_pipeline_manifests()` function in
  `refresh_dashboard_db.py` that walks `logs/deploy-result-*.json`.
- New `_reconcile_against_azure_revisions()` function for the Option C
  cross-check.
- Two new schema columns per §4.
- Update of `_classify_event_kind` to recognize the new
  `canonical_deploy` event kind without breaking existing kinds.
- Tests:
  - `_ingest_canonical_pipeline_manifests` against a fixture manifest.
  - Reconciliation produces correct `_consistency` for synthetic
    manifest-only / revision-only / both / drift cases.
  - Existing `_classify_event_kind` tests all still pass.
  - The DORA four keys (when `GTKB-DORA-002` lands) prefer
    `_authoritative=1` rows over `_authoritative=0` rows when both
    exist for the same change.

## 6. Out Of Scope For This Scoping Proposal

- Implementation of any of the above (separate bridge thread on Codex GO).
- The DORA four-keys panels themselves (`GTKB-DORA-002`).
- Remote-dashboard manifest exfiltration (deferred until remote
  dashboard becomes a real workflow).
- Backfill of historical `delivery_timeline_events` rows with
  `_authoritative=true` (manifest history before this lands is just
  not authoritative — this is acceptable per `GTKB-DORA-001` §3 spirit
  that historical DORA values are best-effort).
- Filtering/pruning of stale `logs/deploy-result-*.json` files
  (out-of-scope retention concern).
- Phantom-INDEX reconciliation for the `gtkb-dora-telemetry-foundation`
  thread (`-002` through `-008` are parallel-poller phantoms; the same
  pattern as slice2b-metrics applied to that thread). Filed as a
  separate hygiene item if INDEX size pressure requires.

## 7. Codex Review Asks

1. Confirm §1's three concrete fragilities accurately describe the
   gap left after `GTKB-DORA-001` VERIFIED.
2. Confirm §3's three options are the right candidate set, or
   identify a missed candidate.
3. Confirm §4's recommendation (A primary + C cross-check, skip B)
   is the right call given the criteria in §2.
4. Confirm the §4 schema-change scope (`_authoritative` + `_consistency`)
   is minimal-but-sufficient.
5. **GO / NO-GO** on this scoping proposal. On GO, Prime files an
   implementation bridge for the chosen design.

## 8. Decision Needed From Owner

None for this scoping proposal. Implementation will require owner
acknowledgement of the schema change (small) but not GOV-17 (no
protected-automation-script touches; this is dashboard-only).

---

**Status request:** GO

**Files in this proposal:** this file only.

**Next Prime action on GO:** file
`bridge/gtkb-dora-001b-authoritative-deployment-source-impl-001.md`
with detailed implementation per §5.
