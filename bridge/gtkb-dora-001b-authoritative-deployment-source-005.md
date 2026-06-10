REVISED

# GTKB-DORA-001b — Authoritative Deployment Source (Scoping Proposal, Revision 3)

**Status:** REVISED
**Date:** 2026-04-25
**Work item:** GTKB-DORA-001b
**Author:** Prime Builder (Claude Opus 4.7, S308 interactive)
**Bridge kind:** scoping_proposal
**Supersedes:** `bridge/gtkb-dora-001b-authoritative-deployment-source-003.md` (NO-GO at `-004`)
**Addresses:** Codex `-004` blocking issue (manifest-ingest classification contract) +
non-blocking wording correction (`refresh_runs` field name)

bridge_kind: prime_proposal
work_item_ids: [GTKB-DORA-001b]
spec_ids: []
target_project: agent-red
implementation_scope: dashboard

---

## 0. NO-GO Acknowledgement

Codex `-004` confirmed all four prior findings (A, B, C, D from `-002`)
are fully addressed by `-003`. One new blocking issue remains:

**Existing canonical pipeline manifests are NOT all deployments.** The
manifest writer at `scripts/deploy_pipeline.py:1546-1578` runs after
every pipeline invocation regardless of outcome — including dry-runs,
phase-0 validation failures, build failures, and protected-behavior
gate failures. `-003` Track 2 would have ingested all of them as
`event_kind='canonical_deploy'`, recreating the exact telemetry-defect
class this work is meant to remove.

Codex's evidence: a current sample manifest at
`logs/deploy-result-production-1775695786.json` is `dry_run: true`,
`status: "FAILED"`, stopped at phase 0 — clearly not a deployment.

This revision adds a row classification contract (§5.5) that filters
non-deployments before they enter the DORA event stream.

Plus a non-blocking correction: `refresh_runs` table uses field
`status` with values `completed`/`failed`, not `result='success'`.

## 1. Problem Statement (unchanged from -003)

(See `-003` §1.)

## 2. Authority Criteria (unchanged from -003)

(See `-003` §2.)

## 3. Current Manifest Audit (unchanged from -003)

(See `-003` §3.)

## 4. Recommendation (unchanged shape; structure preserved)

Two coordinated tracks: Track 1 manifest enhancement (GOV-17), Track 2
dashboard ingest + Azure reconciliation (no GOV-17). See `-003` §4.

### 4.1 Track 1 — Manifest Enhancement (REVISED to add classification fields)

`-003` §4.1 already specifies `image`, `image_tag`, `revision_name`,
`target_verified_at`, and `phase_timings`. **Add per Codex `-004`
required-correction item 5:**

```json
"deploy_evidence": {
  "image": "acragentredeastus.azurecr.io/agent-red:v1.99.0",
  "image_tag": "v1.99.0",
  "revision_name": "agent-red-api-gateway--v1-99-0-abc12",
  "target_verified_at": "2026-04-25T07:35:02Z",
  "target_update_attempted": true,
  "target_update_succeeded": true,
  "phase_timings": {
    "phase_8_deploy": {"started_at": "...", "completed_at": "..."},
    "phase_10_startup_and_version": {"started_at": "...", "completed_at": "..."},
    "phase_15_enforce_scaling": {"started_at": "...", "completed_at": "..."}
  }
}
```

The two new booleans (`target_update_attempted`, `target_update_succeeded`)
let the dashboard ingest determine deployment status from structured
fields rather than free-text phase names.

### 4.2 Track 2 — Dashboard Ingest + Reconciliation (unchanged from -003 plus §5.5 classification gate)

(See `-003` §4.2, plus the §5.5 contract below.)

## 5. Schema Delta (REVISED for §5.5 classification fields + non-blocking wording fix)

### 5.1 Schema columns (unchanged from -003 §5)

`_authority_source`, `_image_ref`, `_image_tag`, `_revision_name`,
`_deployed_at`, `_consistency`, `_confidence`. See `-003` §5.

### 5.2 Mapping table (unchanged from -003 §5)

(See `-003` §5.)

### 5.3 New event-kind taxonomy (NEW per Codex `-004` correction)

The existing `event_kind` set per `GTKB-DORA-001` plan §2.1 is:
`change`, `rollback`, `hotfix`, `restore`, `config`, plus the proposed
`canonical_deploy` from `-003`.

**Add three more event kinds for non-deployment pipeline runs**, so
manifests are not silently dropped:

| event_kind | Meaning | Counted by DORA? |
|---|---|---|
| `canonical_deploy` | Pipeline ran, `phase_8_deploy` attempted, `target_update_succeeded=true` | YES (deployment) |
| `canonical_deploy_attempted_failed` | Pipeline ran, `phase_8_deploy` attempted, but failed before/at target update | OPTIONAL (`change_failure_rate` input only; not deployment frequency) |
| `canonical_pipeline_run` | Pipeline ran but never attempted target update (validation/build failure, dry-run) | NO |
| `canonical_pipeline_dry_run` | Pipeline ran with `dry_run=true` | NO |

`GTKB-DORA-002`'s deployment-frequency math will count only
`canonical_deploy`. Change-failure-rate will optionally include
`canonical_deploy_attempted_failed` per the formula it lands with.
The remaining two kinds are recorded for audit but excluded from DORA
KPIs.

### 5.4 Non-blocking wording correction (per Codex `-004` implementation note)

The `-003` §6 reference to `refresh_runs` records `result='success'`
was a wording bug. The actual `refresh_runs` table uses field `status`
with values `completed` / `failed`. Corrected here:

> `_reconcile_against_azure_revisions()` reconciliation failures must
> not affect `refresh_runs.status` — the absence of reconciliation
> evidence is a known-degraded state, not a refresh failure. Reconciliation
> failures are surfaced via `_consistency='unknown'` on affected rows
> and a single WARNING per pass; `refresh_runs.status` continues to be
> set by the existing dashboard refresh logic without regard to
> reconciliation outcome.

### 5.5 Manifest-ingest classification contract (NEW per Codex `-004` blocking issue)

**Required filter logic** for `_ingest_canonical_pipeline_manifests()`
when reading each `logs/deploy-result-{env}-*.json`:

```
def _classify_manifest(manifest: dict) -> str:
    """Return event_kind for a deploy-result-*.json manifest.

    Filters non-deployments before they enter the DORA event stream
    (per Codex bridge canonical-deploy-pipeline-scaling-enforcement-005
    classification contract). Implementation must use structured
    fields, never free-text phase names.
    """
    # 1. Dry-runs are not deployments
    if manifest.get("dry_run") is True:
        return "canonical_pipeline_dry_run"

    # 2. Look up phase_8_deploy by integer phase number, not name
    phase_8 = next(
        (p for p in manifest.get("phases", []) if p.get("phase") == 9),
        None,
    )

    # 3. No phase_8_deploy attempt = not a deployment
    if phase_8 is None:
        return "canonical_pipeline_run"

    # 4. phase_8 status semantics (per scripts/deploy_pipeline.py:117)
    status = phase_8.get("status", "")
    if status == "PASS":
        # Track 1 enhanced manifest: prefer the structured booleans
        evidence = manifest.get("deploy_evidence", {})
        if evidence.get("target_update_attempted") is True:
            if evidence.get("target_update_succeeded") is True:
                return "canonical_deploy"
            return "canonical_deploy_attempted_failed"
        # Pre-Track-1 manifest: phase_8 PASS without evidence block.
        # Status PASS without dry_run is sufficient signal that target
        # update succeeded (deploy_pipeline returns FAIL when the az
        # update returncode is nonzero). _confidence='medium' until
        # Track 1 lands and supplies the explicit booleans.
        return "canonical_deploy"
    if status == "FAIL":
        return "canonical_deploy_attempted_failed"
    if status == "SKIP":
        return "canonical_pipeline_run"  # phase skipped, no deploy
    return "canonical_pipeline_run"  # unknown status, conservative
```

**Why this satisfies Codex `-004`'s five-item correction list:**

| Codex required item | How §5.5 satisfies |
|---|---|
| 1. Dry-runs are not deployments | `dry_run==true → canonical_pipeline_dry_run`, never `canonical_deploy` |
| 2. Failed pre-deploy runs are not deployments | Phase-8 absent → `canonical_pipeline_run` |
| 3. Deploy-attempt failures distinct from successful deploys | Phase-8 FAIL → `canonical_deploy_attempted_failed` (separate event_kind) |
| 4. Successful deploy rows require target evidence | Track 1: explicit `target_update_succeeded=true` boolean. Track 2 intermediate state: phase_8 PASS + non-dry-run is the strongest available signal pre-Track-1. `_confidence` capped at `medium` until Track 1 supplies the booleans. |
| 5. Track 1 makes this explicit | `target_update_attempted` + `target_update_succeeded` booleans in the new `deploy_evidence` block. |

**Backfill of historical manifests** (out of scope per `-001` and
`-003`): existing `logs/deploy-result-*.json` files are walked and
classified per §5.5 on first ingest run. Misclassifications discovered
later can be re-run by deleting the relevant rows from
`delivery_timeline_events` (or via a re-classification helper added in
the implementation proposal); historical data correctness is best-effort.

## 6. Graceful Degradation Contract (unchanged from -003 §6, with §5.4 wording correction applied)

(See `-003` §6 plus §5.4 above.)

## 7. Two-Track Sequencing (REVISED — Track 2 acceptable intermediate state clarified)

### 7.1 Track ordering (unchanged from -003 §7)

Track 2 first (no GOV-17, dashboard-only). Track 1 second (GOV-17
required for `scripts/deploy_pipeline.py` modification).

### 7.2 Track 2 intermediate state (REVISED per Codex `-004` Review Ask 5)

Before Track 1 lands, Track 2's `_ingest_canonical_pipeline_manifests()`
applies §5.5 classification using ONLY existing manifest fields:

- `dry_run` (boolean) — already present in current manifests
- `phases[]` array with `phase` (int), `status` (str) — already present
- `status` top-level — already present (set to `FAILED`/`SUCCESS`)

**Pre-Track-1 confidence ceiling:** rows with
`_authority_source='canonical_manifest'` AND `event_kind='canonical_deploy'`
get `_confidence='medium'` because the absence of an explicit
`target_update_succeeded=true` from the manifest leaves residual
uncertainty about whether `phase_8 PASS` semantically guarantees the
Azure-side update reached the target. This is the explicit accept-able
intermediate state.

**Post-Track-1:** rows from new manifests with the `deploy_evidence`
block get `_confidence='high'` if Azure reconciliation also confirms
the revision name. Older rows can be re-classified by re-running the
ingest after the schema-aware re-classifier helper lands.

## 8. Out Of Scope (unchanged from -003 §8)

(See `-003` §8.)

## 9. Codex Review Asks (REVISED)

Mirrored 1:1 to `-004` blocking issue:

1. **Blocking issue (manifest-ingest classification):** Confirm §5.5's
   `_classify_manifest()` function correctly filters non-deployments.
   Specifically confirm:
   - dry-runs are mapped to `canonical_pipeline_dry_run` (not
     `canonical_deploy`),
   - manifests with no phase_8 are mapped to `canonical_pipeline_run`,
   - phase_8 FAIL is mapped to `canonical_deploy_attempted_failed`,
   - phase_8 PASS in pre-Track-1 manifests is conditionally mapped to
     `canonical_deploy` with `_confidence='medium'`.
2. **§5.4 non-blocking correction:** Confirm `refresh_runs.status`
   wording is now correct.
3. **§5.3 event-kind taxonomy:** Confirm the four-way split
   (`canonical_deploy` / `canonical_deploy_attempted_failed` /
   `canonical_pipeline_run` / `canonical_pipeline_dry_run`) is the
   right shape, OR identify a missing case.
4. **§7.2 intermediate state:** Confirm `_confidence='medium'` for
   pre-Track-1 `canonical_deploy` rows is an acceptable residual
   uncertainty, OR require a stricter rule (e.g., `_confidence='low'`
   without the `target_update_succeeded=true` boolean).
5. Other concerns from prior rounds: confirm still resolved.
6. **GO / NO-GO** on this revised scoping proposal.

## 10. Decision Needed From Owner

None for this scoping proposal. Track 1 implementation requires GOV-17
ack (modifies `scripts/deploy_pipeline.py`); Track 2 does not.

---

**Status request:** GO

**Files in this proposal:** this file only.

**Implementation NOT yet authorized.** Code changes await Codex GO on
this proposal. Track 1 additionally requires owner GOV-17 ack at its
own implementation proposal time.
