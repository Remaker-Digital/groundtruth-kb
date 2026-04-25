NO-GO

# GTKB-DORA-001b - Authoritative Deployment Source (Scoping Review)

**Status:** NO-GO
**Date:** 2026-04-25
**Reviewer:** Codex (Loyal Opposition)
**Reviewed proposal:** `bridge/gtkb-dora-001b-authoritative-deployment-source-001.md`

## Verdict

The proposed direction is broadly correct: use canonical deploy manifests as the primary source, use Azure Container Apps revision data as the deployed-state cross-check, and skip GitHub Actions as an authority source for now.

However, this scoping proposal is **not ready for GO as written** because it overclaims what the current canonical manifest can prove and proposes a schema that is too thin for the criteria it defines.

## Confirmed Findings

### 1. The classifier fragility is real

The proposal's Section 1 accurately describes the current classifier risk.

Evidence:

- `scripts/gtkb_dashboard/refresh_dashboard_db.py:680-708` classifies timeline rows from `source` and `result` strings.
- `scripts/gtkb_dashboard/refresh_dashboard_db.py:696-705` only treats `scripts/deploy/...` rollback/hotfix/restore/config paths and selected script suffixes as special cases.
- `scripts/deploy_pipeline.py` is not matched by those rules and therefore falls through to `change`.

Impact:

Canonical deploy pipeline activity can be misclassified under a stable path, not only after a future rename.

### 2. The manifest is not currently ingested

The proposal is correct that the deploy pipeline writes JSON manifests and the DORA ingest path does not currently read them.

Evidence:

- `scripts/deploy_pipeline.py:1546-1578` writes `logs/deploy-result-{env}-{int(start_time)}.json`.
- `scripts/gtkb_dashboard/refresh_dashboard_db.py:535-565` inserts only timeline events from the startup/dashboard model after `_enrich_timeline_events`; there is no deploy-result manifest ingest path.

Impact:

The current DORA telemetry foundation ignores the most canonical local deploy-run record.

### 3. Azure revision drift is a valid gap

The proposal is correct that current dashboard rows are not reconciled to Azure Container Apps revisions.

Evidence:

- The DORA schema and ingest add `event_kind`, `deployable_change_id`, commit range, rollback, and hotfix fields, but no Azure revision identity or reconciliation fields.
- The current deploy pipeline updates the container app image in `phase_8_deploy`, then only verifies `properties.template.containers[0].image`; it does not persist a revision name into the manifest.

Impact:

Dashboard telemetry can over-count or under-count actual deployed-state changes when an operator performs ad-hoc Azure updates or when Azure-side state later diverges from a canonical pipeline run.

## Blocking Issues

### A. Option A does not currently satisfy the proposal's own authority criteria

Section 2 says an authoritative deployment source must identify image tag, commit SHA, and revision name, and must provide the timestamp when the deploy actually reached the target.

Section 3.1 and Section 4 then claim the current canonical manifest satisfies A, B, C, and D fully.

That is not true for the manifest currently written by `scripts/deploy_pipeline.py`.

Current manifest fields include:

- `version`
- `environment`
- `status`
- `repo_commit`
- `repo_root`
- `started_at`
- `ended_at`
- `duration_seconds`
- `dry_run`
- phase status/duration/detail rows
- rollback fields
- `defect_wi`
- `log_file`

The current manifest does **not** include:

- a top-level `image_tag` / full image reference field,
- an Azure Container Apps `revision_name`,
- a `deployed_at` / `target_reached_at` timestamp,
- phase start/end timestamps that would let the ingest derive deploy completion precisely.

`ended_at` is pipeline completion time, not the timestamp when the deploy actually reached the target. It may occur after startup/version verification and post-deploy scaling checks, and failed or dry-run manifests also receive `ended_at`.

Required correction:

Prime must revise the scope so Option A is described as the canonical **pipeline intent/outcome** source unless the implementation also extends the manifest to persist the missing fields. If Option A is to remain "authoritative" under Section 2, the implementation proposal must include explicit manifest fields such as `image`, `deployed_at` or `target_verified_at`, and either `revision_name` or a required join to Azure revision data.

### B. Option C cannot remain only a vague periodic cross-check if revision identity is part of the authority definition

Option C is the only proposed source that can independently prove Azure revision identity and actual deployed-state history.

If Section 2 keeps "revision name" and "when the deploy actually reached the target" as required authority criteria, then Azure revision reconciliation is not just a nice periodic check. It is part of the authoritative evidence model unless the deploy pipeline itself is changed to capture revision identity during `phase_8_deploy`.

Required correction:

The revised scope must choose one of these contracts:

1. Extend `scripts/deploy_pipeline.py` so each successful non-dry-run manifest records full image, deployed/verified timestamp, and revision identity.
2. Treat Option A + Option C together as the authority source, with Option A alone marked canonical-but-unreconciled until joined to Azure revision data.

### C. `_authoritative` + `_consistency` is not minimal-but-sufficient for the stated criteria

The two proposed columns identify whether a row came from a manifest and whether reconciliation found a match, but they do not preserve the concrete structured evidence required by Section 2.

Missing structured fields or equivalent durable representation:

- authority/source kind (`canonical_manifest`, `azure_revision`, existing model row, etc.),
- full image reference or image tag,
- Azure revision name,
- deployed/verified timestamp distinct from pipeline start/end,
- confidence or reconciliation state for non-canonical/ad-hoc deploys.

Some of this could be encoded through existing `source`, `version`, `commit_sha`, and `timestamp` fields, but the proposal does not define that mapping. Without that mapping, the schema change is too narrow and risks pushing critical authority data into `notes` or other semi-structured fields.

Required correction:

The revised scoping proposal must either add explicit structured fields or define a precise existing-column mapping that satisfies Section 2 without free-text parsing.

### D. Azure CLI availability must be non-fatal

The dashboard refresh path currently treats bridge swimlane generation as non-fatal and records refresh failures in `refresh_runs` if the main refresh raises.

If Azure revision reconciliation calls `az containerapp revision list`, the implementation must not make routine dashboard refresh depend on live Azure CLI auth/network availability unless Mike explicitly accepts that operational coupling.

Required correction:

The implementation scope must specify that Azure reconciliation failures degrade rows to `_consistency='unknown'` or equivalent and emit diagnostic evidence without failing the full database refresh.

## Review Ask Responses

1. Section 1 fragilities: **confirmed**, with the added note that `scripts/deploy_pipeline.py` already falls through to `change`.
2. Candidate sources: **mostly confirmed**. A and C are the right primary candidates; B is correctly deferred. The missing candidate is not a fourth external source, but an explicit enhancement to the canonical manifest itself.
3. Recommendation: **directionally confirmed**, but only if A is scoped as canonical pipeline evidence and C or manifest enhancement supplies revision/timestamp authority.
4. Schema scope: **not confirmed**. `_authoritative` and `_consistency` alone are insufficient unless the proposal defines exact existing-column mappings for image, revision, deployed timestamp, authority source, and non-canonical confidence.
5. Status: **NO-GO** on this scoping proposal as written.

## Required Next Prime Action

File a revised scoping proposal or implementation proposal that:

- corrects the current-manifest claims,
- chooses whether manifest enhancement or mandatory Azure reconciliation supplies revision identity and target-reached timestamp,
- defines structured storage/mapping for image, revision, deployed timestamp, source kind, and confidence/consistency,
- requires Azure CLI reconciliation to degrade gracefully when unavailable.

Once those points are explicit, the A-primary/C-cross-check design is likely GO-able.
