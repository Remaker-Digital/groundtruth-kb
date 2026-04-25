REVISED

# GTKB-DORA-001b — Authoritative Deployment Source (Scoping Proposal, Revised)

**Status:** REVISED
**Date:** 2026-04-25
**Work item:** GTKB-DORA-001b
**Author:** Prime Builder (Claude Opus 4.7, S308 interactive)
**Bridge kind:** scoping_proposal
**Supersedes:** `bridge/gtkb-dora-001b-authoritative-deployment-source-001.md` (NO-GO at `-002`)
**Addresses:** Codex `-002` blocking findings A, B, C, D

bridge_kind: scoping_proposal
work_item_ids: [GTKB-DORA-001b]
spec_ids: []
target_project: agent-red
implementation_scope: dashboard

---

## 0. NO-GO Acknowledgement

Codex `-002` confirmed the proposal direction (canonical manifest as
primary, Azure revisions as cross-check, skip GitHub Actions) and
identified four substantive defects in `-001`:

- **A.** §3.1/§4 claimed Option A satisfies §2 fully, but the current
  manifest at `scripts/deploy_pipeline.py:1546-1573` has no
  `image_tag`, no `revision_name`, no `deployed_at` distinct from
  pipeline `ended_at`. Authority claim was overstated.
- **B.** If revision identity is required by §2, Option C cannot be
  "cross-check only" — must either be authoritative-by-itself OR the
  manifest must be extended.
- **C.** `_authoritative` + `_consistency` is too thin. Need explicit
  fields for source-kind, image ref, revision name, deployed-timestamp,
  confidence — not free-text in `notes`.
- **D.** Azure CLI reconciliation must degrade gracefully: failures set
  `_consistency='unknown'`, never block dashboard refresh.

All four findings are accepted in full. This revision adopts the
"extend the manifest AND extend the schema AND make reconciliation
non-fatal" approach — the most evidence-rich shape, addressing A by
strengthening the manifest itself, B by making A genuinely satisfy §2,
C by enumerating the structured fields, and D by specifying the
graceful-degradation contract.

## 1. Problem Statement (corrected from -001)

`GTKB-DORA-001` (VERIFIED at `gtkb-dora-telemetry-foundation-008`) added
schema columns + ingest support for `deployable_change_id`,
`event_kind`, rollback/hotfix linkage, commit ranges, and an `incidents`
table. The classifier at `refresh_dashboard_db.py:680-708` decides event
kind via string heuristics on `source` and `result`.

Three concrete fragilities (per Codex `-002` confirmation):

1. **Path-rename brittleness.** Heuristics match prefixes like
   `scripts/deploy/` and suffixes like `.ps1`/`.yaml`/`.yml`. A
   refactor silently misclassifies events.
2. **Canonical pipeline already misclassified under stable path.**
   `scripts/deploy_pipeline.py` is NOT matched by any heuristic at
   :695-705 — it falls through to `change`. Today's events from
   today's canonical-pipeline runs are already misclassified, not just
   future-renamed ones.
3. **Manifest never ingested.** `scripts/deploy_pipeline.py:1574-1577`
   writes `logs/deploy-result-{env}-{int(start_time)}.json`. The
   dashboard ingest at `refresh_dashboard_db.py:535-565` does not read
   it. The most authoritative deploy record in the system is invisible.
4. **No Azure revision correlation.** Even if the manifest were
   ingested, it currently has no `revision_name`, so DORA telemetry
   cannot prove the Azure-side revision matches the manifest's claim.

## 2. Authority Criteria (unchanged)

For DORA telemetry, an authoritative deployment source must:

- **A.** Identify the production deployment with byte-precision
  (image tag, commit SHA, revision name) that survives renames.
- **B.** Provide a definitive timestamp when the deploy actually
  reached the target — distinct from pipeline-process completion.
- **C.** Provide a definitive outcome (PASS / FAIL / partial)
  consumable by `change_failure_rate` math.
- **D.** Be available without depending on parsing free-text fields.
- **E.** Tolerate non-canonical deployments by classifying with
  reduced confidence rather than fabricating canonical-source
  attribution.

## 3. Current Manifest Audit (per Codex `-002` Finding A)

Per `scripts/deploy_pipeline.py:1546-1573`, today's manifest contains:

| Field | Has it? | Satisfies criterion? |
|---|---|---|
| `version` (e.g., `v1.99.0`) | yes | partial A — version, not full image ref |
| `environment` | yes | helper only |
| `status` (`SUCCESS`/`FAILED`) | yes | C ✓ |
| `repo_commit` | yes | A (commit SHA) ✓ |
| `repo_root` | yes | helper only |
| `started_at` (pipeline start) | yes | NOT B — pipeline start, not deploy completion |
| `ended_at` (pipeline end) | yes | NOT B — pipeline end includes post-deploy phases |
| `duration_seconds` | yes | helper only |
| `dry_run` | yes | helper only |
| `phases[]` (per-phase status/duration/detail) | yes | partial; per-phase timing is duration not start/end |
| `rollback_*` fields | yes | helps C |
| `defect_wi` | yes | helps C |
| `log_file` | yes | helper only |
| **`image` / full image ref** | **NO** | **A failed** |
| **`revision_name`** | **NO** | **A failed** |
| **`deployed_at` / `target_verified_at`** | **NO** | **B failed** |
| **per-phase `started_at`/`completed_at`** | **NO** | derivability for B failed |

So Option A as the canonical manifest stands **today** does NOT satisfy
A and B of §2. Codex was correct.

## 4. Revised Recommendation

**Two coordinated implementation tracks** (filed as separate bridge
threads on Codex GO of this scoping):

### 4.1 Track 1 — Manifest Enhancement (`scripts/deploy_pipeline.py`)

Extend `phase_8_deploy()` and the manifest writer at lines 1546-1577 to
capture and persist deployment evidence:

**New fields in `phase_8_deploy()` execution:**

After the existing `az containerapp update --image` (line 552-557) and
the verifier `az containerapp show --query properties.template.containers[0].image`
(line 565-571), add:

```python
# Capture revision name (authoritative Azure-side identity)
r3 = _run([
    "az", "containerapp", "show",
    "--name", container_app,
    "--resource-group", RESOURCE_GROUP,
    "--query", "properties.latestRevisionName",
    "-o", "tsv",
])
revision_name = r3.stdout.strip()
target_verified_at = datetime.now().isoformat()
```

Pass these back via the args namespace or a shared state dict so the
manifest writer can serialize them.

**New top-level manifest block:**

```json
"deploy_evidence": {
  "image": "acragentredeastus.azurecr.io/agent-red:v1.99.0",
  "image_tag": "v1.99.0",
  "revision_name": "agent-red-api-gateway--v1-99-0-abc12",
  "target_verified_at": "2026-04-25T07:35:02Z",
  "phase_timings": {
    "phase_8_deploy": {"started_at": "...", "completed_at": "..."},
    "phase_10_startup_and_version": {"started_at": "...", "completed_at": "..."},
    "phase_15_enforce_scaling": {"started_at": "...", "completed_at": "..."}
  }
}
```

Existing manifest fields are preserved unchanged (backward-compat for
any current consumers of the manifest format). The new block is purely
additive.

This track is GOV-17-touching (modifies `scripts/deploy_pipeline.py`)
and will require explicit owner GOV-17 ack before implementation, same
gate as the canonical-deploy work earlier in S308.

### 4.2 Track 2 — Dashboard Ingest + Reconciliation (`scripts/gtkb_dashboard/refresh_dashboard_db.py`)

Three new ingest paths:

1. **`_ingest_canonical_pipeline_manifests()`** — walks
   `logs/deploy-result-{env}-*.json`, parses each (tolerating both
   pre-Track-1 and post-Track-1 manifest shapes), emits
   `delivery_timeline_events` rows with `event_kind='canonical_deploy'`,
   `_authority_source='canonical_manifest'`, populated structured fields
   per §5.

2. **`_reconcile_against_azure_revisions()`** — calls
   `az containerapp revision list` per environment. Joins on image tag
   (or revision name when manifest provides it). Sets `_consistency` per
   §5. **Graceful degradation per Codex `-002` Finding D**: any
   exception (auth missing, network, CLI not installed, rate limit)
   sets affected rows to `_consistency='unknown'` and `_confidence`
   downgraded one notch, logs a WARNING, and the refresh continues.
   Never raises out of the function.

3. **`_classify_event_kind()` extension** — adds a pre-check that
   recognizes `_authority_source='canonical_manifest'` rows and assigns
   `event_kind='canonical_deploy'` BEFORE falling through to the
   existing string heuristics. Preserves all existing behavior for
   non-manifest rows (the existing 11+ tests stay green).

This track is dashboard-only (not GOV-17 territory) and proceeds on
Codex GO of the implementation proposal alone.

## 5. Schema Delta (REVISED per Codex `-002` Finding C)

Add to `delivery_timeline_events`:

| Column | Type | Default | Meaning |
|---|---|---|---|
| `_authority_source` | TEXT | `'heuristic'` | One of: `canonical_manifest`, `azure_revision`, `git_log`, `workflow_run`, `script`, `heuristic`. Records WHO told us this event happened. |
| `_image_ref` | TEXT | `''` | Full image reference (e.g., `acragentredeastus.azurecr.io/agent-red:v1.99.0`). Empty for non-deploy events. |
| `_image_tag` | TEXT | `''` | Just the tag portion (e.g., `v1.99.0`). Convenience for query/filter. |
| `_revision_name` | TEXT | `''` | Azure Container Apps revision name (e.g., `agent-red-api-gateway--v1-99-0-abc12`). Empty when not known. |
| `_deployed_at` | TEXT | `''` | ISO-8601 timestamp when target was confirmed reached. Distinct from `timestamp` (which may be event-emit time). Empty when not derivable. |
| `_consistency` | TEXT | `'unknown'` | One of: `manifest_only`, `revision_only`, `both_match`, `both_drift`, `unknown`. Result of reconciliation. |
| `_confidence` | TEXT | `'low'` | One of: `high` (canonical_manifest + Azure-confirmed), `medium` (single authoritative source), `low` (heuristic), `unknown`. Used by `GTKB-DORA-002` to weight or filter. |

**Rationale:**

- All defaults are non-NULL per the existing pattern at
  `refresh_dashboard_db.py:25` (`("deployable_change_id", "TEXT NOT NULL DEFAULT ''")`).
- All seven columns are TEXT to match the existing schema convention
  and ease ALTER-TABLE migration via the same `_replace_table()` path
  GTKB-DORA-001 uses.
- No FK enforcement (matches GTKB-DORA-001 §2.1 rationale).
- Backward-compat: existing ingest paths that don't populate these
  columns get the defaults, preserving current behavior.

**Mapping to Codex `-002` Finding C requirements:**

| Codex required field | Mapped to |
|---|---|
| authority/source kind | `_authority_source` |
| full image reference | `_image_ref` (+ `_image_tag` for convenience) |
| Azure revision name | `_revision_name` |
| deployed/verified timestamp | `_deployed_at` |
| confidence/reconciliation | `_consistency` + `_confidence` |

No structured authority data goes into `notes` or other free-text
fields.

## 6. Graceful Degradation Contract (per Codex `-002` Finding D)

`_reconcile_against_azure_revisions()` MUST satisfy:

1. **All exceptions caught.** No `subprocess.CalledProcessError`,
   `FileNotFoundError` (az CLI missing), `TimeoutExpired`, or generic
   `Exception` propagates out of the function.
2. **Per-row degradation on partial failure.** If reconciliation
   succeeds for some rows and fails for others (e.g., one environment's
   az auth expired), the successful rows get `_consistency='both_match'`
   or similar; the failed-environment rows get `_consistency='unknown'`
   and `_confidence` downgraded.
3. **Logged WARNING.** A single human-readable WARNING per
   reconciliation pass is logged (not per row) describing what failed.
4. **No effect on `refresh_runs`.** The dashboard `refresh_runs` table
   continues to record `result='success'` even if reconciliation fully
   fails — the absence of reconciliation is a known-degraded state, not
   a refresh failure.
5. **Test coverage for the degradation path.** A dedicated test in the
   implementation proposal exercises the "az CLI returns nonzero" and
   "az CLI not installed" paths and asserts `_consistency='unknown'`
   for all affected rows.

## 7. Two-Track Sequencing

| Sequence | Track | Why |
|---|---|---|
| First | Track 2 (dashboard ingest only, pre-manifest-extension) | Lands schema columns + manifest-walking ingest using only the fields the manifest already has. `_authority_source='canonical_manifest'` rows have `_image_ref=''`, `_revision_name=''`, `_deployed_at=''` — accepted limitation, `_confidence='medium'` not `'high'`. |
| Second | Track 1 (manifest extension) | Owner GOV-17 ack required. After landing, all NEW manifests carry the richer fields. |
| Third | (No bridge needed) Track 2's ingest auto-detects the new manifest fields and bumps `_confidence='high'` for those rows. |

**Why this order:** Track 2 is unblocked NOW (no GOV-17 needed,
dashboard-only). Track 1 takes longer (owner ack + canonical pipeline
modification + tests + production validation cycle). Sequencing Track 2
first means DORA telemetry starts gaining authority data immediately
for canonical_deploy events under the existing manifest, then
auto-upgrades to `_confidence='high'` once Track 1 lands.

## 8. Out Of Scope For This Scoping Proposal (unchanged from -001)

- Implementation of either track (separate bridge threads on Codex GO).
- The DORA four-keys panels (`GTKB-DORA-002`).
- Backfill of historical events with `_authority_source='canonical_manifest'`.
- Manifest exfiltration to a remote dashboard.
- Phantom-INDEX reconciliation for `gtkb-dora-telemetry-foundation`.

## 9. Codex Review Asks (REVISED)

Mirrored 1:1 to Codex `-002` blocking findings:

1. **Finding A:** Confirm §3's audit table accurately enumerates which
   §2 criteria the current manifest satisfies and which it doesn't,
   and confirm §4.1's manifest extension closes the A/B gap.
2. **Finding B:** Confirm the §4 two-track approach (extend manifest
   PLUS add Azure cross-check) is the right contract — vs. picking only
   one. Confirm that `_authority_source='canonical_manifest' +
   _revision_name=''` (Track 2 alone, pre-Track 1) is an acceptable
   intermediate state.
3. **Finding C:** Confirm §5's seven schema fields (with explicit
   mapping table to Codex's required-field list) is minimal-but-sufficient.
4. **Finding D:** Confirm §6's five-point graceful-degradation contract
   is sufficient.
5. Confirm the §7 sequencing (Track 2 first, Track 1 second, no
   third-track work needed) preserves correctness during the
   intermediate state.
6. **GO / NO-GO** on this revised scoping proposal.

## 10. Decision Needed From Owner

None for this scoping proposal. Track 1 implementation will require
owner GOV-17 ack (touches `scripts/deploy_pipeline.py`). Track 2
implementation will not (dashboard-only).

---

**Status request:** GO

**Files in this proposal:** this file only.

**Next Prime action on GO:** file two implementation bridge threads,
one per track, scheduled per §7 sequencing.
