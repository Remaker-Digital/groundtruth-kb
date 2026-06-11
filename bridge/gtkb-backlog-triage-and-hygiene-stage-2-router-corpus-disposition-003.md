REVISED

bridge_kind: prime_proposal
Document: gtkb-backlog-triage-and-hygiene-stage-2-router-corpus-disposition
Version: 003
Author: prime-builder (Claude Opus 4.7, harness B) — interactive owner session
Date: 2026-06-11
Responds-To: bridge/gtkb-backlog-triage-and-hygiene-stage-2-router-corpus-disposition-002.md

Project: PROJECT-GTKB-BACKLOG-TRIAGE-AND-HYGIENE-001
Work Item: WI-4456
Project Authorization: PAUTH-PROJECT-GTKB-BACKLOG-TRIAGE-AND-HYGIENE-001-BACKLOG-TRIAGE-AND-HYGIENE-BOUNDED-IMPLEMENTATION-AUTHORIZATION

author_identity: prime-builder
author_harness_id: B
author_session_context_id: 0c0caa91-3f63-41d1-b4c6-960f9b137180
author_model: claude-opus-4-7
author_model_version: 4.7
author_model_configuration: interactive owner session, ::init gtkb pb

target_paths: ["scripts/hygiene/router_corpus_dispose.py", "platform_tests/scripts/test_router_corpus_dispose.py"]

No KB mutation at GO time: this proposal authorizes adding a deterministic disposition tool plus tests. The mutation path runs AFTER bridge GO AND a separate per-batch owner AskUserQuestion approval, with an explicit approved-id batch file and a deterministic batch hash. `groundtruth.db` is intentionally NOT in target_paths.

---

# Stage 2 — Advisory-Router Corpus Disposition (REVISED-1 addressing -002 NO-GO)

Stage 2 of `PROJECT-GTKB-BACKLOG-TRIAGE-AND-HYGIENE-001` (WI-4456). Chartered by owner decision `DELIB-20261667`. This REVISED-1 addresses all four findings in Codex's `-002` NO-GO; the underlying direction (signal-classify + bulk-dispose under owner per-batch AUQ) is unchanged, but the executable contract is tightened so the approved cohort is owner-specified exactly and so the bulk-mutation primitive preserves work-item metadata.

## Revision Scope

Addresses all four findings in `-002` NO-GO:

- **FINDING-P1-001 (refined batches not representable)**: The original `--apply --batch-size N` interface could not encode the exact id set Mike approved if Mike used REFINE/exclude. Under the bounded PAUTH's `work_item_retirement_without_stage_batch_auq` prohibition, that's a direct D2 violation. **Fix:** replace `--batch-size N` with `--batch-file <approved-batch.json>` containing the explicit approved id list plus the batch hash. The tool computes its own hash over `(sorted ids, manifest run_id, auq_id)` and refuses on mismatch, unknown id, or stale manifest. The deterministic-services principle (`DELIB-S312`) is preserved: the *hashing* and *refusal* logic are mechanical; only the approved-id list is human-supplied.
- **FINDING-P1-002 (insert_work_item blanks fields)**: The original proposal said the tool would invoke `db.insert_work_item(...resolution_status="wont_fix"...)`, but that API requires every work-item field and does NOT carry forward existing fields. For a 749-item bulk operation this is a high-blast-radius corruption risk. **Fix:** the tool uses `db.update_work_item(id, changed_by, change_reason, *, owner_approved=True, resolution_status="wont_fix")` which reads the current row and preserves every unchanged field (title, description, origin, component, priority, project_name, subproject_name, related_*, source_*, approval_state, acceptance_summary, regression_visibility — all preserved). Tests assert each field's pre-state equals its post-state for every disposed item.
- **FINDING-P2-003 (stale manifest selection)**: The "newest item file by mtime" rule could select a directory containing only the companion file but no `run.json` (the idempotency-key carrier). **Fix:** the manifest-selection algorithm now requires the newest run directory that contains BOTH `run.json` AND `backlog_triage_items.json` AND whose `run.json["run_id"] == backlog_triage_items.json["run_id"]`. The idempotency_key is derived from `run.json`. Tests assert that a partial-state directory (companion file present, `run.json` absent) is skipped.
- **FINDING-P2-004 (AUQ evidence missing from manifest)**: The proposal said the batch AUQ would surface title, changed_at, and source_spec_id, but the manifest companion file contains only the per-item signal vector — not those owner-facing evidence fields. **Fix:** the dry-run JOIN reads `current_work_items` (read-only) for every candidate id and surfaces `title`, `changed_at`, `source_spec_id`, `priority`, `origin`, and `component` alongside the signal vector. The batch packet schema documents these enrichment fields. Tests assert that the dry-run output contains them and that a missing-in-DB id is reported as a defect (fail-closed).

The read-only / no-KB-mutation boundaries, the safety-belt design, and the spec linkage are preserved.

## Summary

Fresh Stage 0 manifest (run `20260611-145313`, post-hardening) shows:

- **`total_open`: 1044**; **`router_generated`: 753**; **`retire_candidate_unapproved_noise`: 749**; **`keep_signal`: 202**; **`review`: 93**.

Per D4 (signal-classify + bulk-dispose) and D2 (staged batch-approval), Stage 2 disposes only items the Stage 0 classifier labeled `retire_candidate_unapproved_noise` AND only via owner-AUQ-supplied id batches. The disposition primitive is `update_work_item(..., resolution_status="wont_fix", owner_approved=True)` so every existing field on every disposed item is preserved.

Under the kb-batch 50-item maximum, the 749-item cohort resolves over **~15 owner batches**, each owner-supplied as `<approved-batch.json>` with an explicit id list + batch hash. Each batch executes only after its own owner AskUserQuestion.

## Specification Links

- `GOV-STANDING-BACKLOG-001` (linked in PAUTH).
- `SPEC-AUTO-BACKLOG-FOR-IMPLEMENTATION-BEARING-SPECS-001` (linked in PAUTH).
- `SPEC-1662` (GOV-18, Assertion/measurement quality) — Stage 0 hardening that makes Stage 2 safe is grounded in this spec.
- `GOV-08` — KB is the single source of truth; Stage 2 mutates only via the canonical `db.update_work_item` API.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` — the freshness principle; the disposition tool refuses to operate on stale manifests AND requires the approved-id list to match the current dry-run derivation.
- `ADR-STANDING-BACKLOG-DB-AUTHORITY-001` / `DCL-STANDING-BACKLOG-DB-SCHEMA-001` — schema authority; append-only versioning; preserved-fields requirement (FINDING-P1-002).
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — all Stage 2 changes are in-root.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` / `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` / `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — durable-artifact discipline.
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` — repetitive AI plumbing is a defect; the disposition tool IS the service.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — filed under `bridge/` with REVISED INDEX entry; append-only.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — all relevant specs cited.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — verification derived below.

## Prior Deliberations

- `DELIB-20261667` — owner decision chartering this project (D4 + D2).
- `bridge/gtkb-backlog-triage-and-hygiene-stage-2-router-corpus-disposition-002.md` (NO-GO) — Codex's four findings this REVISED-1 directly addresses.
- `bridge/gtkb-backlog-triage-and-hygiene-stage-0-analyzer-011.md` (VERIFIED) — Stage 0 analyzer + its rubber-stamp hardening; load-bearing precedent.
- `bridge/gtkb-backlog-triage-and-hygiene-stage-1-structural-repair-003.md` (REVISED-1) and `-004` (GO) — Stage 1's strict-apply-order pattern that Stage 2's tool reuses.
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` — Stage 2 IS the service.

## Owner Decisions / Input

Collected via `AskUserQuestion` during the `/grill-me-for-clarification` interview on 2026-06-11, persisted to `DELIB-20261667`:

1. **D1** — platform-only disposition; Agent Red items deferred to Stage 5.
2. **D2** — staged batch-approval; this REVISED-1 makes that exact through `--batch-file` + hash.
3. **D3** — priority-preserving; Stage 2 mutates only `resolution_status`, priorities preserved by `update_work_item` field-carry-forward.
4. **D4** — signal-classify + bulk-dispose; this stage IS the dispose surface.
5. **D5** — stop-the-leak; Stage 2's source-attribution surface feeds Stage 3.
6. **Continuation approval — `Yes` / `Resume`** (2026-06-11). Owner authorized continuation; Stage 1 reached VERIFIED clearance via Codex GO @ `-004`.

The per-batch owner decisions Stage 2 implementation will collect via separate AskUserQuestion calls (NOT authorized by this proposal's GO):

- **Stage 2 batch AUQ shape (per FINDING-P2-004 enrichment)** — for each batch (≤ 50 items): present an enriched candidate table with `id`, `title`, `changed_at`, `source_spec_id`, `priority`, `origin`, `component`, plus the manifest's `run_id` + `idempotency_key`; ask Mike to APPROVE / REFINE (specify exact id subset) / REJECT. The accepted set becomes the `<approved-batch.json>` file with a deterministic batch hash, citing the AUQ id.

## Requirement Sufficiency

**Existing requirements sufficient.** The disposition contract is fixed by `DELIB-20261667` D4. The governing specs already constrain backlog-authority, measurement-quality, source-of-truth-freshness, schema-authority, and the field-preservation requirement. No new requirement is needed.

## Backlog Visibility

`GOV-STANDING-BACKLOG-001` bulk-ops clause (`CLAUSE-VISIBILITY-BULK-OPS`): the `--apply` execution path performs bulk-class operations on `current_work_items`. The visibility evidence required by the clause is satisfied by THREE distinct artifacts produced per batch:

1. **Inventory artifact**: the `--prepare-batch` output (`approved-batch.json`) is itself the inventory — a deterministic enumeration of every id that will be disposed, plus the manifest run_id, idempotency_key, batch_hash, and (via the enrichment join) title/changed_at/source_spec_id per id. This inventory is the canonical record of what was operated on.
2. **Review packet**: the dry-run JSON + markdown summary served to Mike inside the per-batch AskUserQuestion IS the review packet — it surfaces label/scope/origin counts, the first 10 sample titles, and the full per-id enrichment table the owner uses to APPROVE / REFINE / REJECT.
3. **Owner-approval evidence**: the AUQ id captured into `approved-batch.json.auq_id` plus the durable `change_reason` on every disposed item's new version embeds the AUQ id, manifest run_id, and batch_hash — append-only audit trail.

Per D2 of `DELIB-20261667`, each batch (≤ 50 items) requires its own per-batch owner AskUserQuestion at execution time, with the explicit approved id list embedded in `<approved-batch.json>`. The bounded PAUTH (v4) explicitly forbids `work_item_retirement_without_stage_batch_auq`; the batch-hash refusal ensures the tool cannot execute an unhand-approved cohort even by accident. No DECISION DEFERRED state applies — every disposition is owner-approved or refused.

## Scope and Boundaries

In scope: (1) new `scripts/hygiene/router_corpus_dispose.py` deterministic disposition tool with read-only dry-run + opt-in `--apply` mode; (2) pytest at `platform_tests/scripts/test_router_corpus_dispose.py`. Out of scope: any direct mutation of `groundtruth.db` at Write time; the 202 `keep_signal` items; the 93 `review` items (deferred to Stage 4); the 47 Agent-Red-scope items (Stage 5); Stage 3 stop-the-leak; Stage 4 re-ranking; Stage 6 closeout; deploy/push.

## Proposed Implementation

**`scripts/hygiene/router_corpus_dispose.py` (new).** Three operative modes:

### Default (dry-run, read-only)

1. Locate the newest **complete** benchmark run directory under `.gtkb-state/benchmarks/` (FINDING-P2-003 fix): the newest directory that contains BOTH `run.json` AND `backlog_triage_items.json` AND whose `run.json["run_id"] == backlog_triage_items.json["run_id"]`. Skip directories missing either file or with mismatched run_ids.
2. Load `run.json` for the `idempotency_key` and `source_commit`; load `backlog_triage_items.json` for the per-item signal vectors.
3. Filter to the disposition cohort: items where `label == "retire_candidate_unapproved_noise"` AND `scope == "platform"`.
4. Read `current_work_items` (read-only SQLite URI) and JOIN against the cohort to enrich each item with `title`, `changed_at`, `source_spec_id`, `priority`, `origin`, `component` (FINDING-P2-004 fix). Items present in the manifest but missing from the DB are reported as defects.
5. Emit deterministic JSON to stdout: `{run_id, idempotency_key, source_commit, candidates: [{id, title, changed_at, source_spec_id, priority, origin, component, label, scope, router_generated, approval_state}, ...]}`. Print a markdown summary listing counts by label/scope/origin + the first 10 sample titles.

### `--prepare-batch <out.json>` (read-only batch packet generation)

1. Run the dry-run logic and select the first N candidates (where N is owner-configurable via `--max-batch-size`, default 50, hard-capped at 50 per the kb-batch convention).
2. Emit `out.json`: `{auq_id: null, manifest_run_id, idempotency_key, ids: [WI-...], batch_hash: sha256(sorted_ids + manifest_run_id + "")}`. Owner fills `auq_id` after AskUserQuestion approval; the tool re-computes `batch_hash` at apply time with the filled-in AUQ id.

### `--apply --batch-file <approved-batch.json>`

Required fields in the batch file:
- `auq_id` (string, owner-supplied after AskUserQuestion approval)
- `manifest_run_id` (string)
- `ids` (list of WI-* strings, the exact owner-approved cohort)
- `batch_hash` (string, deterministic over `sorted(ids) + manifest_run_id + auq_id`)

Pre-mutation safety belts (all FAIL-CLOSED):
1. `--confirm-manifest <run_id>` matches `batch_file.manifest_run_id` AND matches the newest complete run on disk → otherwise refuse with "stale manifest" (FINDING-P2-003 fix).
2. Re-compute `batch_hash` from the file's fields → refuse on mismatch (FINDING-P1-001 fix).
3. Each id in `ids` MUST be present in the manifest's `retire_candidate_unapproved_noise` platform cohort → refuse on any id not in cohort.
4. Each id MUST exist in `current_work_items` AND have its current `resolution_status` in (`null`, `""`, `"open"`) → refuse on any non-open id (idempotency).
5. Batch size ≤ 50 → refuse otherwise.

Mutation primitive (FINDING-P1-002 fix):
- For each id, call `db.update_work_item(id, changed_by=<resolved>, change_reason=f"Stage 2 router-corpus disposition; batch approved by {auq_id}; manifest {manifest_run_id}; per DELIB-20261667 D4.", owner_approved=True, resolution_status="wont_fix")`.
- `update_work_item` reads the current row and preserves every unchanged field; only `resolution_status` changes.

Idempotency: if any id has already become non-open between the dry-run and the apply, the safety belt #4 fires and the tool refuses, with a clear remediation message ("re-prepare the batch from a fresh dry-run").

**`platform_tests/scripts/test_router_corpus_dispose.py` (new).** Tests covering:

- **Manifest selection (FINDING-P2-003)**: partial-state directory (companion only, no `run.json`) is skipped; run-id mismatch between `run.json` and `backlog_triage_items.json` is rejected.
- **Enrichment (FINDING-P2-004)**: dry-run output contains `title`, `changed_at`, `source_spec_id`; a manifest id missing from `current_work_items` is reported as a defect.
- **Refined batches (FINDING-P1-001)**: a `<batch-file.json>` with a subset (REFINE) executes only that subset; a batch hash mismatch is refused; a stale manifest is refused; an unknown id (not in cohort) is refused.
- **Field preservation (FINDING-P1-002)**: pre/post snapshot of every preserved field (title, description, origin, component, priority, project_name, subproject_name, related_spec_ids_at_creation, related_bridge_threads, related_deliberation_ids, source_spec_id, source_owner_directive, source_deliberation_query, acceptance_summary, regression_visibility, approval_state) — asserts each field's pre-state equals its post-state, ONLY `resolution_status` changes.
- **Batch-size limit**: 0 ≤ size ≤ 50; 51+ refuses.
- **Idempotency / repeat-apply**: an id already non-open is refused with a remediation message.
- **Read-only default**: AST scan + row-count guard + read-only DB URI.
- **Determinism**: two dry-runs over identical input produce byte-identical JSON.
- **APPROVE / REFINE / REJECT semantics**:
  - APPROVE all: batch-file with full cohort → all disposed.
  - REFINE (exclude): batch-file with subset → only subset disposed; excluded items remain open.
  - REJECT: tool not invoked → no mutation (test confirms a no-op).
- **Scope filter**: Agent-Red-scope items are excluded from the cohort.
- **No regression**: existing benchmarks remain importable.

## Isolation Placement Compliance

`ADR-ISOLATION-APPLICATION-PLACEMENT-001`: all Stage 2 changes are in-root under `E:\GT-KB\`.

## Spec-Derived Verification Plan

| Spec / requirement | Derived test |
|---|---|
| `GOV-STANDING-BACKLOG-001` + `SPEC-1662` (deterministic disposition) | test: a synthetic manifest + DB produces identical dry-run output across two runs; the apply path is fully reproducible from a `<batch-file.json>` |
| `GOV-08` + `ADR-STANDING-BACKLOG-DB-AUTHORITY-001` (canonical mutation via the governed API only; field preservation) | test: AST scan confirms `update_work_item` is the only mutation primitive; pre/post field snapshot asserts every preserved field is unchanged for every disposed item |
| `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` (no stale-manifest execution) | test: `--apply` refuses on stale manifest; refuses on incomplete manifest dir (no `run.json`); the change_reason embeds the manifest run_id |
| D2 (per-batch owner AUQ; refined batches representable) | test: `--apply` without `--batch-file` refuses; `--batch-file` with mismatching batch_hash refuses; unknown id in batch refuses; APPROVE/REFINE/REJECT semantics each tested |
| D4 (signal-classify + bulk-dispose; conservative-on-retire-candidacy) | test: items NOT in `retire_candidate_unapproved_noise` cohort are refused even if they appear in the batch file |
| FINDING-P1-002 specifically | test: 16-field pre/post equality snapshot per disposed item |
| FINDING-P2-003 specifically | test: a fixture with only a companion file (no `run.json`) is rejected; mismatched run_ids between the two files refuse |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `python -m pytest platform_tests/scripts/test_router_corpus_dispose.py -q`; `ruff check` AND `ruff format --check` on every changed Python file |

## Acceptance Criteria

1. `scripts/hygiene/router_corpus_dispose.py` exists, runs read-only by default, locates the newest **complete** manifest deterministically, joins against `current_work_items` for enrichment fields, and emits JSON + markdown summary citing `run_id` + `idempotency_key`.
2. `--prepare-batch <out.json>` emits a batch packet with `auq_id=null`, `manifest_run_id`, `idempotency_key`, `ids`, and the precomputed `batch_hash`.
3. `--apply --batch-file <approved-batch.json>` requires `auq_id` populated; validates `batch_hash`; refuses on stale manifest, batch-hash mismatch, unknown id, non-open id, or size > 50.
4. The mutation primitive is `update_work_item(...)` with `owner_approved=True` and `resolution_status="wont_fix"`; field-preservation snapshot tests pass.
5. Default-mode AST scan + row-count guard + read-only DB URI all pass.
6. APPROVE / REFINE / REJECT semantics are each covered by tests.
7. All new tests pass; `ruff check` and `ruff format --check` clean on every changed Python file.

## Bridge Protocol Compliance

Filed at `bridge/gtkb-backlog-triage-and-hygiene-stage-2-router-corpus-disposition-003.md` with a matching `REVISED` entry directly below the Document header at the top of `bridge/INDEX.md`; append-only. `GOV-FILE-BRIDGE-AUTHORITY-001` is honored. The implementation-start packet will be minted from the GO against PAUTH v4 under `source_addition` / `test_addition` mutation classes. The `--apply` executions execute only AFTER bridge GO AND a fresh dry-run AND their per-batch owner AskUserQuestion approval AND a deterministic batch-hash match.

## Risk and Rollback

- **Risk — owner approves a batch but discovers later that one id should have been excluded:** the change_reason on every disposed item embeds the AUQ id + manifest run_id + batch_hash, so the audit trail surfaces exactly which batch caused the disposition. **Per-item rollback:** `update_work_item(id, ..., resolution_status="open", change_reason="Stage 2 disposition rollback per <reason>")` — append-only, no destructive operation.
- **Risk — manifest selection picks a directory that is complete but has stale counts vs the current DB:** the FINDING-P2-004 enrichment join refuses if any approved id is missing from `current_work_items`; for stale-but-present ids, the batch hash already pinned the exact id set. **Rollback:** re-run dry-run; re-prepare batch; re-AUQ.
- **Risk — `update_work_item` field preservation breaks for some field type:** the 16-field pre/post snapshot test catches any field that is not preserved. If `update_work_item` semantics ever change, the test fires immediately. **Rollback:** revert the affected disposed items via the per-item rollback above.
- **Risk — batch hash collision (sha256 has none in practice; mentioned for completeness):** sha256 collision space is computationally infeasible at this corpus size.

## Recommended Implementation Routing

**Claude/Codex (deterministic source + test).** Stage 2 is greenfield source + tests under an existing PAUTH with no protected-narrative surface. The intellectual care is in: (a) the **manifest-complete-run selection** algorithm (FINDING-P2-003); (b) the **field-preservation snapshot test** (FINDING-P1-002); (c) the **batch-hash refusal** logic (FINDING-P1-001); (d) the **enrichment join** (FINDING-P2-004). All four findings have orthogonal safety belts that make their respective failure modes structurally hard rather than policy-prevented.

## Recommended Commit Type

`feat:` — net-new disposition tool + test suite. The 15 batches of `--apply` execution that occur separately are not part of the commit Stage 2 produces.
