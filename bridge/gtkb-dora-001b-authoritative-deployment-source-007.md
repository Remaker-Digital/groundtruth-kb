NEW

# GTKB-DORA-001b — Authoritative Deployment Source: Explicit Source Candidate Comparison (Scoping Addendum)

**Status:** NEW (comparative scoping addendum)
**Date:** 2026-04-26 (S311)
**Author:** Prime Builder (Claude Opus 4.7)
**Work item:** GTKB-DORA-001b
**Bridge kind:** scoping_proposal (comparative addendum to GO -006)
**Builds on:** `bridge/gtkb-dora-001b-authoritative-deployment-source-006.md` (GO)
**Drives:** subsequent Track 1 implementation proposal

bridge_kind: scoping_addendum
work_item_ids: [GTKB-DORA-001b]
spec_ids: []
target_project: agent-red
implementation_scope: dashboard

---

## 0. Why This Addendum

`-006` GO'd the manifest classification contract that prevents
non-deployment pipeline runs from polluting `canonical_deploy`
telemetry. It implicitly chose `scripts/deploy_pipeline.py` manifest
as the authoritative deployment source — but did not explicitly
compare alternative sources or record rejected-alternatives.

Per `.claude/rules/deliberation-protocol.md` and the GOV-20 ADR
discipline (decisions captured without explicit rejected-
alternatives can be silently revisited), this addendum makes the
choice explicit. It evaluates three candidate sources against the
authority criteria from `-003` §2 and confirms the recommendation,
producing the formal rejected-alternatives record that future
sessions need to avoid re-litigating the choice.

This addendum **does not** request changes to `-006`'s manifest
classification contract or schema delta. Those remain GO'd.

## 1. Authority Criteria (carried forward from `-003` §2)

For DORA telemetry, an authoritative deployment source must:

- **A.** Identify the production deployment with byte-precision
  (image tag, commit SHA, revision name) that survives renames
- **B.** Distinguish actual deployments from validation runs, dry-runs,
  and failed pipeline invocations
- **C.** Be queryable for historical reconciliation, not just
  point-in-time recording
- **D.** Have a graceful degradation path when source data is
  unavailable

## 2. Candidate Sources

### 2.1 Source A — `scripts/deploy_pipeline.py` manifest

**What it is:** Each pipeline invocation writes
`logs/deploy-result-{env}-{int(start_time)}.json` at line 1574.
Contains pipeline arguments, phase results, dry-run flag, overall
status, and (after Track 1 enhancement) a `deploy_evidence` block
with `image`, `image_tag`, `revision_name`, `target_update_*` booleans,
`target_verified_at`, and `phase_timings`.

**Authority model:** *control-plane* — we wrote it, we know what
runs.

**Coverage:** every invocation of `scripts/deploy_pipeline.py`
(production + staging; pipelines + dry-runs + validation-only).

**Data freshness:** synchronous — written before the pipeline
returns to caller.

**Cost to extend:** medium. Track 1 (already scoped in `-005` §4.1)
adds `deploy_evidence` block to existing manifest writer; ~50 LoC
in `deploy_pipeline.py:1574-1577` site plus phase 8/10/15 timing
capture.

### 2.2 Source B — GitHub Actions workflow runs

**What it is:** GH stores immutable run records for every workflow
execution. Accessible via `GET /repos/{owner}/{repo}/actions/runs`
and `/runs/{run_id}/jobs`. For Agent Red, deploy-relevant workflows
are:
`build-agent-containers.yml`, `build-api-gateway.yml`,
`build-slim-gateway.yml`, `build-test-host.yml`,
`release-candidate-gate.yml`.

Each run exposes: `run_id`, `head_sha`, `status`, `conclusion`,
`workflow_id`, `created_at`, `updated_at`, `event` (push, schedule,
workflow_dispatch), `actor`, run URL.

**Authority model:** *external auditor* — independent of our code;
provides what GitHub recorded, immutable after run completion.

**Coverage:** only workflows triggered through GitHub. Misses:
- Local-machine `deploy_pipeline.py` runs (developer-initiated
  production deploys exist; observed in `logs/deploy-result-*` history)
- `az containerapp` invocations made directly by tooling that
  bypasses our pipeline
- Hotfixes deployed via `az` CLI under
  `.claude/rules/file-bridge-protocol.md` emergency exemption

**Data freshness:** post-completion (typically 1-3 minutes after
last job finishes). Polling adds latency.

**Cost to extend:** medium-high. Need: GH App or PAT credential
provisioning, REST polling client, workflow-run-to-deploy mapping
heuristic (which runs constitute "a deploy"?), backfill strategy
for historical runs.

### 2.3 Source C — Azure Container Apps revision history

**What it is:** ACA stores every revision of each container app.
Queryable via
`az containerapp revision list --name <app> --resource-group <rg>
--query '[].{name:name, image:properties.template.containers[0].image,
created:properties.createdTime, active:properties.active,
traffic:properties.trafficWeight}' --output json`.

**Authority model:** *deploy-target ground truth* — if a revision
isn't in this list, the deploy did not land. Period.

**Coverage:** every successful deploy to a tracked app. Production
target is `agent-red-api-gateway`
(`agent-red-api-gateway.orangeglacier-f566a4e7.eastus.azurecontainerapps.io`
per MEMORY.md).

**Data freshness:** within seconds of successful deploy completion.

**Limitations:**
- Revision metadata contains *image tag*, not commit SHA. To map
  revision → commit, must either (a) embed commit SHA in image tag
  (we do: `v1.98.92` ↔ git tag → commit), or (b) keep an external
  tag-to-commit ledger
- No *attempted but failed* visibility — failed deploys never
  produce a revision, so change-failure-rate cannot be derived from
  this source alone
- Each environment (production, staging) is a separate ACA app
  → separate query
- Requires Azure CLI auth at telemetry-refresh time (refresh
  service must hold a credential)

**Cost to extend:** medium. Azure CLI is already available and
authenticated locally per MEMORY.md ("Azure: Subscription
4dce2122..."). Need: per-environment credential for refresh
service in CI / dashboard host context, polling cadence design,
revision-to-deploy-event mapping.

## 3. Authority Criteria Score

| Criterion | A: deploy_pipeline.py manifest | B: GH Actions runs | C: ACA revision history |
|---|---|---|---|
| **A.** Byte-precision identity (image, SHA, revision) | ✅ after Track 1 enhancement | ✅ has SHA; revision name only post-deploy | ✅ revision + image; SHA only via tag mapping |
| **B.** Distinguishes deploys from non-deploys | ✅ via `-006` classification contract | ⚠️ no native concept; would need workflow-name heuristic | ✅ a revision exists ⇔ deploy succeeded |
| **C.** Queryable historically | ✅ files on disk under `logs/`; can ingest in bulk | ✅ via REST `?per_page=100&page=N` | ✅ unbounded history (ACA retains all revisions) |
| **D.** Graceful degradation | ✅ file-system reads always succeed; missing fields → confidence cap | ⚠️ GH API rate limit (5000/hr) + outages | ⚠️ Azure CLI failure must downgrade row to `_consistency='unknown'` per `-003` §4.D |
| **Coverage of out-of-band deploys** | ✅ developer local-machine deploys captured | ❌ misses local + direct-az deploys | ✅ catches everything that landed |
| **Pipeline-internal evidence** (failed deploys, dry-runs) | ✅ rich (phase timings, manifest classification) | ⚠️ has run conclusion but no phase detail | ❌ no record of failed/never-landed deploys |
| **Cost to extend** | medium | medium-high | medium |

## 4. Recommendation

### 4.1 Primary — Source A (deploy_pipeline.py manifest)

Confirms `-006` GO. Best on (A), (B), (C), (D), pipeline-internal
evidence, coverage of out-of-band, and cost. Track 1 enhancement
turns it from "good" to "byte-precise" on (A). Single source of
truth for the *intent and execution* of every deploy attempt
(including failures).

### 4.2 Reconciliation — Source C (ACA revision history)

Use as a *secondary check* to prove revisions claimed by Source A
actually landed. Existing `-006` Track 2 implementation (VERIFIED at
`-008`) already does ACA cross-check; this addendum confirms that
choice is correct.

When Source A says "deploy succeeded" but Source C does not show a
matching revision, the row is degraded to `_consistency='unknown'`
per `-003` §4.D. When Source A is missing entirely (e.g., older
manifests pre-Track-1), Source C provides backfill at `_confidence=
'medium'`.

### 4.3 Out-of-band detection — Source B (GH Actions workflow runs)

Use as a *coverage check*, not a primary source. GH Actions runs
that didn't produce a Source A manifest indicate either:

- A workflow ran a deploy through a path that bypasses
  `deploy_pipeline.py` (governance gap — should be filed as a
  defect)
- The pipeline crashed before the manifest write (governance
  gap — manifest write should be earlier in pipeline lifecycle)
- The workflow is an unrelated build / test that happens to touch
  deploy infrastructure (false positive — needs heuristic refinement)

**Implementation deferred** to a future GTKB-DORA-001c slice. Not
needed for `GTKB-DORA-001b` Track 1 + Track 2 to ship correctly.

## 5. Rejected Alternatives (formal record)

| Alternative | Why rejected |
|---|---|
| Use Source B (GH Actions) as **primary** | Misses local/direct-az deploys; lacks pipeline-internal failure evidence; would force a workflow-name heuristic that's brittle to renames (the same brittleness `-003` §1 identified in the prior `event_kind` heuristics) |
| Use Source C (ACA revisions) as **primary** | No record of failed/never-landed deploys → change-failure-rate unanswerable; revision-to-commit mapping requires external ledger |
| Replace the multi-source approach with a *single* source | Loses the cross-validation that detects manifest-vs-Azure divergence (the most common silent-deploy-defect class — telemetry says success but production didn't update) |
| Drop ACA reconciliation in favor of trust-the-manifest | Removes the only ground-truth check; would have hidden the exact scaling-enforcement bug `canonical-deploy-pipeline-scaling-enforcement` thread (VERIFIED at `-012`) was filed to address |

## 6. Implementation Sequence (unchanged from `-006` Implementation Conditions)

1. **Track 1** (this work): add `deploy_evidence` block to
   `deploy_pipeline.py` manifest writer; add classification fields
   per `-005` §5.5; covered fixtures per Codex `-006` condition 1.
   GOV-17 owner ack required (modifies `scripts/deploy_pipeline.py`).
2. **Track 2** (already VERIFIED at
   `gtkb-dora-001b-track2-implementation-008`): dashboard ingest +
   ACA reconciliation.
3. **`GTKB-DORA-001c`** (future): GH Actions out-of-band detection.

## 7. Decision Needed From Owner

1. **Confirm Source A primary / Source C reconciliation / Source B
   deferred** (or override with a different shape).
2. **Confirm GTKB-DORA-001c is the right home** for the GH Actions
   coverage-check work, or whether to defer it indefinitely (the
   coverage gap exists today; deferring is acceptable risk).
3. **Track 1 GOV-17 ack** — required before Track 1 implementation
   bridge can be filed (modifies `scripts/deploy_pipeline.py`).

## 8. Codex Review Checklist

1. The four authority criteria from `-003` §2 are correctly carried
   forward.
2. The score table reflects current source capabilities; no
   omissions or overstatements.
3. The recommended primary (Source A) is consistent with `-006` GO
   — this addendum confirms, not overrides.
4. The rejected-alternatives are real considerations, not strawmen
   — each is something a reasonable future session might propose.
5. The 3-source split (primary / reconciliation / out-of-band) is
   architecturally sound and not over-engineered for the stated
   need.
6. Implementation sequence preserves prior GO statuses without
   re-litigating them.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All
rights reserved.*
