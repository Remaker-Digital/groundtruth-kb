NEW

bridge_kind: prime_proposal
Document: gtkb-backlog-triage-and-hygiene-stage-2-router-corpus-disposition
Version: 001
Author: prime-builder (Claude Opus 4.7, harness B) — interactive owner session
Date: 2026-06-11

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

No KB mutation at GO time: this proposal authorizes adding a deterministic disposition tool plus tests. The mutation path — `python scripts/hygiene/router_corpus_dispose.py --apply --auq-id AUQ-NNN --batch-size N` — runs AFTER bridge GO AND a separate per-batch owner AskUserQuestion per the bounded authorization PAUTH (v4; `forbid work_item_retirement_without_stage_batch_auq`). `groundtruth.db` is intentionally NOT in target_paths; mutations are owner-gated at execution time, not at file-Write time.

---

# Stage 2 — Advisory-Router Corpus Disposition (deterministic bulk-retire tool + per-batch owner AUQ execution)

Stage 2 of `PROJECT-GTKB-BACKLOG-TRIAGE-AND-HYGIENE-001` (WI-4456). Chartered by owner decision `DELIB-20261667`. Stage 0 reached VERIFIED at `bridge/gtkb-backlog-triage-and-hygiene-stage-0-analyzer-006.md`; the hardened classifier's fresh manifest (run `20260611-145313`) is the empirical basis for this proposal.

## Summary

The freshly-rerun Stage 0 manifest (post-hardening that excludes the rubber-stamp `source_spec_id='GOV-STANDING-BACKLOG-001'` signal) reveals the real disposition surface:

- **`total_open`: 1044** (up from 1031 this morning — drift continues, reinforcing the Stage 3 stop-the-leak rationale).
- **`retire_candidate_unapproved_noise`: 749** items — router-generated, `approval_state` in (`unapproved`, `unset`), and not signal-bearing under the hardened classifier. These are the Stage 2 disposition candidates.
- **`keep_signal`: 202** items — bridge-/spec-/owner-linked. **Stage 2 will not touch these.**
- **`review`: 93** items — non-router items the classifier left to owner case-by-case review. **Stage 2 will not touch these** (the per-item disposition flow belongs in Stage 4's re-rank or a future skill).
- **`router_generated`: 753**; of those, 4 are bridge-linked (signal-bearing → kept). The remaining 749 form the disposition cohort.

Per the kb-batch governance convention (50-item maximum, mandatory dry-run, GOV-15 gate), the 749 candidates resolve over **15 owner batches**. Each batch is owner-AUQ-gated at execution time; Stage 2's bridge GO authorizes the **tool**, not the executions.

The hardened classifier itself is the safety case: the boilerplate `source_spec_id` rubber-stamp defeat case is tested by `test_boilerplate_source_spec_id_is_not_a_signal` (landed in Stage 0). Without that test, this Stage 2 would risk false-positive retires.

## Specification Links

- `GOV-STANDING-BACKLOG-001` — standing-backlog governance authority; Stage 2 disposes items under it (linked in PAUTH).
- `SPEC-AUTO-BACKLOG-FOR-IMPLEMENTATION-BEARING-SPECS-001` — auto-backlog substrate whose corpus Stage 2 disposes of (linked in PAUTH).
- `SPEC-1662` (GOV-18, Assertion/measurement quality) — the prohibition on rubber-stamp signals; the Stage 0 hardening that makes Stage 2 safe is grounded in this spec.
- `GOV-08` — KB is the single source of truth; Stage 2 mutates only via the canonical `db.insert_work_item` API (append-only versioning) and only with explicit owner-AUQ-cited `change_reason`.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` — the freshness principle; the disposition tool refuses to operate on any WI not present in the LATEST manifest (no stale-plan execution).
- `ADR-STANDING-BACKLOG-DB-AUTHORITY-001` / `DCL-STANDING-BACKLOG-DB-SCHEMA-001` — the schema authority Stage 2 writes through (append-only versions; resolution_status terminal values).
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — all Stage 2 changes are in-root; see Isolation Placement Compliance below.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` / `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` / `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — the durable-artifact discipline; the disposition tool is itself a tracked durable surface (S347 owner-directive bias).
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` — repetitive AI plumbing (here: manually retiring 749 router items) is a defect to engineer into a deterministic service; this stage IS that service.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — filed under `bridge/` with a matching `NEW` INDEX entry; append-only.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — all relevant specs cited here.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — verification derived below.

## Prior Deliberations

- `DELIB-20261667` — owner decision chartering this project (D4 = signal-classify + bulk-dispose; D2 = staged batch-approval). This Stage 2 implements that decision's Stage 2 with the live-data tightening from the fresh manifest.
- `bridge/gtkb-backlog-triage-and-hygiene-stage-0-analyzer-006.md` (VERIFIED) — the Stage 0 analyzer + its hardening pass that makes Stage 2 safe. The boilerplate-`source_spec_id` defeat case is the load-bearing precedent.
- `bridge/gtkb-backlog-triage-and-hygiene-stage-1-structural-repair-001.md` (NEW; awaits Codex) — Stage 1's prefix-split detector reuses the same safety-belt design (refuse `--apply` on any pair not in the live dry-run); Stage 2's manifest-presence guard is the analogue here.
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` — recurring AI plumbing is a defect; Stage 2 absorbs the per-item retire ceremony into one tool.
- `SPEC-1662` (GOV-18) — the rubber-stamp prohibition; the Stage 0 hardening test asserts the classifier honors it.
- `DELIB-S327-FORMAL-BACKLOG-DB-SCHEMA-OWNER-DIRECTIVE` — owner directive on backlog DB schema; informs the disposition's terminal-status choice (`wont_fix` per the existing corpus convention, which has 61 wont_fix items already).
- `WI-4222` — earlier LO advisory observing that bulk-retire of lifecycle-cleanup candidates needed "a dry-run inventory or follow-on bridge packet before multi-project lifecycle changes"; Stage 2's design honors that requirement (dry-run + per-batch AUQ).

## Owner Decisions / Input

Collected via `AskUserQuestion` during the `/grill-me-for-clarification` interview on 2026-06-11, persisted to `DELIB-20261667`:

1. **D1 — Triage scope = GT-KB platform + a separate labeled Agent Red stage.** The disposition tool partitions candidates by `scope` (the manifest already does this) and processes the platform partition only. Agent Red items in `retire_candidate_unapproved_noise` are deferred to Stage 5's AR lane.
2. **D2 — Retirement model = staged batch-approval.** Stage 2's `--apply` execution path is explicitly NOT authorized by this bridge GO. Each batch (≤ 50 items) requires its own per-batch owner AskUserQuestion at impl time, citing the live manifest excerpt as evidence.
3. **D3 — Ranking axis = composite, priority-preserving.** Stage 2 does not reorder items; it only resolves the conservative retire candidates to `wont_fix`. Item priorities on surviving items are untouched.
4. **D4 — Advisory-router corpus = signal-classify + bulk-dispose.** Stage 2 IS the bulk-dispose surface. The classifier (Stage 0) supplied the labels; this stage acts on `retire_candidate_unapproved_noise` only.
5. **D5 — Include stop-the-leak stage.** Stage 2's manifest-presence safety belt also produces source-attribution counts (router vs human) Stage 3 will consume to quantify the leak.
6. **Continuation approval — "draft Stage 2 next" (2026-06-11T14:50Z).** Owner approved continuation after the Stage 1 proposal `-001` cleared both preflights on the first try.

The per-batch owner decisions Stage 2 implementation will collect via separate AskUserQuestion calls (NOT authorized by this proposal's GO):

- **Stage 2 batch-AUQ template** — for each batch of ≤ 50 items: present the WI ids + titles + `changed_at` + `source_spec_id` (the rubber-stamp, surfaced informationally to prove they're router boilerplate); ask owner to APPROVE / REFINE (exclude specific ids) / REJECT batch; capture the AUQ id and pass it to `--auq-id` so the change_reason traces back to the owner decision.

## Requirement Sufficiency

**Existing requirements sufficient.** The disposition contract is fixed by `DELIB-20261667` D4 (signal-classify + bulk-dispose) operating on the Stage 0 classifier's output. The governing specs (`GOV-STANDING-BACKLOG-001`, `SPEC-1662`/GOV-18, `GOV-08`, `GOV-SOURCE-OF-TRUTH-FRESHNESS-001`, `ADR-STANDING-BACKLOG-DB-AUTHORITY-001`, `DCL-STANDING-BACKLOG-DB-SCHEMA-001`) already constrain the backlog-authority, measurement-quality, source-of-truth-freshness, and schema-authority surfaces. The kb-batch skill's 50-item maximum + mandatory dry-run + GOV-15 gate convention is the operational pattern Stage 2 mirrors. No new requirement is needed.

## Backlog Visibility

`GOV-STANDING-BACKLOG-001` bulk-ops clause: the `--apply` execution path performs bulk-class operations on `current_work_items`. Per D2 of `DELIB-20261667`, each batch (≤ 50 items) requires its own per-batch owner AskUserQuestion at execution time, citing the live manifest excerpt as evidence. The bounded PAUTH (v4) explicitly forbids `work_item_retirement_without_stage_batch_auq`. This proposal authorizes ONLY the addition of the disposition tool and its test; the execution batches are owner-gated separately. The 749-item cohort resolves over **~15 owner batches**, each independently approvable or refinable.

## Scope and Boundaries

In scope: (1) a new `scripts/hygiene/router_corpus_dispose.py` deterministic disposition tool with mandatory dry-run and opt-in `--apply` mode; (2) a pytest at `platform_tests/scripts/test_router_corpus_dispose.py`. Out of scope and explicitly excluded: any direct mutation of `groundtruth.db` at Write time; the 202 `keep_signal` items (preserved); the 93 `review` items (deferred to Stage 4's re-rank or a future per-item review skill); the 47 Agent-Red-scope items (deferred to Stage 5's AR lane); Stage 3's stop-the-leak; Stage 4's re-ranking; Stage 6's closeout; deploy/push. The `--apply` execution batches happen AFTER this proposal's GO and AFTER their separate per-batch owner AUQ.

## Proposed Implementation

**`scripts/hygiene/router_corpus_dispose.py` (new).** A deterministic disposition tool that:

1. Locates the latest `.gtkb-state/benchmarks/<run_id>/backlog_triage_items.json` (newest by mtime).
2. Loads the per-item signal vectors and partitions them by `label` and `scope`. Builds the disposition candidate list = items with `label == "retire_candidate_unapproved_noise"` AND `scope == "platform"`, sorted by WI id.
3. Default mode (no `--apply`): emits the candidate list as JSON to stdout plus a markdown summary of `(count by label, count by scope, sample 10 candidate titles)`. Includes the source manifest's `run_id` and `idempotency_key` so reviewers can verify which manifest the proposed disposition derives from.
4. `--apply` mode requires three flags: `--auq-id AUQ-NNN` (proves owner approved this specific batch), `--batch-size N` (1 ≤ N ≤ 50; refuses larger), `--confirm-manifest <run_id>` (refuses if the latest manifest's run_id is not the cited one — this is the stale-plan safety belt).
5. With those flags, takes the first N un-disposed candidates in sorted order and invokes `db.insert_work_item` for each: new version, `resolution_status="wont_fix"`, `change_reason=f"Stage 2 router-corpus disposition; batch approved by {auq_id}; manifest {run_id}; per DELIB-20261667 D4."`. Idempotent: if an item is already `wont_fix` (or any non-open resolution_status), it is skipped, not re-versioned.
6. Refuses to operate on any WI not present in the latest manifest's `retire_candidate_unapproved_noise` list. This is the structural guard: even with `--apply`, an owner cannot accidentally retire an item the classifier did not flag.

**`platform_tests/scripts/test_router_corpus_dispose.py` (new).** Tests:

- Default mode is read-only: AST scan + no-mutation row-count guard + read-only fixture.
- Stale-plan safety belt: `--apply --confirm-manifest old-run-id` refuses if a newer manifest exists.
- Batch-size enforcement: `--batch-size 0` and `--batch-size 51` both refuse.
- AUQ-id requirement: `--apply` without `--auq-id` refuses.
- Manifest-presence guard: `--apply` refuses to dispose a WI id not in the manifest's `retire_candidate_unapproved_noise` list (even if the id exists in MemBase).
- Idempotency: a second `--apply` over an already-disposed batch is a no-op (zero new versions written).
- Determinism: dry-run output for identical input is byte-identical across runs.
- Scope filter: Agent-Red-scope items are excluded from the candidate list.
- Mutation primitive: a `--apply` run inserts the expected new version with the correct `resolution_status`, `change_reason`, and `changed_by` attribution on a synthetic fixture DB.

## Isolation Placement Compliance

`ADR-ISOLATION-APPLICATION-PLACEMENT-001`: all Stage 2 changes are in-root under `E:\GT-KB\` — the disposition tool under `scripts/hygiene/`, the test under `platform_tests/scripts/`, the manifest read from `.gtkb-state/benchmarks/<run_id>/`, and this bridge file under `E:\GT-KB\bridge\`. The stage relocates no application file, touches no `applications/` subtree, and writes no out-of-root artifact.

## Spec-Derived Verification Plan

| Spec / requirement | Derived test |
|---|---|
| `GOV-STANDING-BACKLOG-001` + `SPEC-1662` (deterministic, meaningful disposition) | test: on a synthetic fixture, dry-run emits the exact retire-candidate list deterministically; the `--apply` mutation writes new versions only for items the classifier conservatively flagged; running dry-run twice produces byte-identical output |
| `GOV-08` (canonical mutation via the governed API only) | test: AST scan confirms the tool writes only via `db.insert_work_item` (no raw `UPDATE`/`DELETE`/`INSERT INTO work_items` paths); default mode opens the manifest only and never touches the DB |
| `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` (no stale-plan execution) | test: `--apply --confirm-manifest <older-run-id>` refuses when a newer manifest is on disk; the change_reason embeds the run_id so audit trails surface the source manifest |
| D2 (staged batch-approval; per-batch owner AUQ) | test: `--apply` without `--auq-id` refuses; `--batch-size > 50` refuses; the change_reason on each new version embeds the AUQ id |
| D4 (signal-classify + bulk-dispose; conservative-on-retire-candidacy) | test: the tool refuses to retire any WI not in the manifest's `retire_candidate_unapproved_noise` list, even if the WI is router-generated and unapproved at the time of execution (drift safety) |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `python -m pytest platform_tests/scripts/test_router_corpus_dispose.py -q`; `ruff check` AND `ruff format --check` on every changed Python file |

## Acceptance Criteria

1. `scripts/hygiene/router_corpus_dispose.py` exists, runs read-only by default, locates the latest manifest deterministically, and emits a JSON candidate list + markdown summary that cites the source manifest's `run_id` and `idempotency_key`.
2. `--apply` requires `--auq-id`, `--batch-size 1..50`, and `--confirm-manifest <run_id>` matching the latest manifest; missing or mismatched flags refuse with a clear error.
3. The manifest-presence safety belt blocks any WI not in the latest manifest's `retire_candidate_unapproved_noise` list.
4. Disposition is idempotent: a second `--apply` over an already-resolved batch writes zero new versions.
5. The no-mutation AST scan and the row-count-unchanged guard pass for the default mode.
6. All new tests pass; `ruff check` and `ruff format --check` are clean on every changed Python file.

## Bridge Protocol Compliance

Filed at `bridge/gtkb-backlog-triage-and-hygiene-stage-2-router-corpus-disposition-001.md` with a matching `NEW` entry directly below the Document header at the top of `bridge/INDEX.md`; append-only. `GOV-FILE-BRIDGE-AUTHORITY-001` is honored; nothing implements until Loyal Opposition records `GO`. At implementation time the implementation-start packet will be minted from the GO against the bounded authorization PAUTH (v4) under the `source_addition` / `test_addition` mutation classes. The `--apply` executions (each batch ≤ 50, gated by separate owner AUQ) happen AFTER bridge GO AND AFTER VERIFIED post-impl — not at file Write time.

## Risk and Rollback

- **Risk — classifier false-positive (an item flagged as `retire_candidate_unapproved_noise` is actually signal-bearing):** mitigated by (a) the Stage 0 hardening test (`test_boilerplate_source_spec_id_is_not_a_signal`) that asserts the rubber-stamp source_spec_id is not counted; (b) the conservative criterion (router + `unapproved`/`unset` + no bridge/spec/owner link); (c) per-batch owner AUQ where the owner can REFINE the batch (exclude specific ids); (d) append-only versioning — every retirement is reversible by inserting a successor open-status version. **Rollback per item:** `db.insert_work_item(<id>, resolution_status="open", change_reason="Reverting Stage 2 retire; classifier mis-fired on this id.")` — adds one new version, no destructive operation.
- **Risk — stale manifest leads to retiring items that have since gained signal:** the `--confirm-manifest <run_id>` flag refuses when the cited manifest is not the newest; the safety belt fires before any DB mutation. **Rollback:** re-run the Stage 0 benchmark to get a fresh manifest, then retry the batch.
- **Risk — partial batch execution leaves the DB in an inconsistent state:** the tool processes items one at a time and is idempotent; a re-run picks up from the first un-disposed item. No partial transactional boundary is needed because each item's new version is independent. **Rollback:** see the per-item rollback above for any specific item the owner disagrees with.
- **Risk — owner approves a batch but discovers later it included items they meant to keep:** every change_reason embeds the AUQ id + manifest run_id, so the audit trail surfaces the exact batch; selective per-item rollback restores any specific id. **Rollback:** see per-item rollback above.

## Recommended Implementation Routing

**Claude/Codex (deterministic source + test).** Stage 2 is greenfield source + tests under an existing PAUTH with no protected-narrative surface. The intellectual care is in the THREE safety belts: (1) `--confirm-manifest <run_id>` against the latest on disk; (2) manifest-presence guard on every candidate id; (3) batch-size ≤ 50 enforcement. These three together make false-positive retires structurally hard, not just policy-prevented. The 15 batches of execution happen AFTER bridge GO + post-impl VERIFIED + per-batch owner AUQ — that pacing is what makes Stage 2 reversible at scale.

## Recommended Commit Type

`feat:` — net-new disposition tool + test suite (a new operational capability), with no behavior change to existing surfaces. The 15 batches of `--apply` execution that occur separately are not part of the commit Stage 2 produces.
