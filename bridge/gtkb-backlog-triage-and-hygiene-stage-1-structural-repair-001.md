NEW

bridge_kind: prime_proposal
Document: gtkb-backlog-triage-and-hygiene-stage-1-structural-repair
Version: 001
Author: prime-builder (Claude Opus 4.7, harness B) — interactive owner session
Date: 2026-06-11

Project: PROJECT-GTKB-BACKLOG-TRIAGE-AND-HYGIENE-001
Work Item: WI-4454
Project Authorization: PAUTH-PROJECT-GTKB-BACKLOG-TRIAGE-AND-HYGIENE-001-BACKLOG-TRIAGE-AND-HYGIENE-BOUNDED-IMPLEMENTATION-AUTHORIZATION

author_identity: prime-builder
author_harness_id: B
author_session_context_id: 0c0caa91-3f63-41d1-b4c6-960f9b137180
author_model: claude-opus-4-7
author_model_version: 4.7
author_model_configuration: interactive owner session, ::init gtkb pb

target_paths: ["scripts/hygiene/prefix_split_detector.py", "platform_tests/scripts/test_prefix_split_detector.py"]

No KB mutation at GO time: this proposal authorizes adding a read-only detector script and its test. The two execution paths that DO mutate the canonical store — `gt projects reconcile-doubled-prefix --apply` and `python scripts/hygiene/prefix_split_detector.py --apply ...` — run AFTER bridge GO AND a separate per-batch owner AskUserQuestion per the bounded authorization PAUTH (v3; `forbid project_retirement_without_stage_batch_auq`, `forbid work_item_reorder_without_stage_batch_auq`). `groundtruth.db` is intentionally NOT in target_paths; the mutations are owner-gated at execution time, not at file-Write time.

---

# Stage 1 — Structural Defect Repair (read-only detector + owner-gated execution paths)

Stage 1 of `PROJECT-GTKB-BACKLOG-TRIAGE-AND-HYGIENE-001` (WI-4454). Chartered by owner decision `DELIB-20261667`. Stage 0 reached VERIFIED at `bridge/gtkb-backlog-triage-and-hygiene-stage-0-analyzer-006.md` and the resulting `backlog_triage` benchmark manifest is the empirical basis for this proposal's numbers.

## Summary

Read-only probes of the live `groundtruth.db` against the existing `gt projects reconcile-doubled-prefix` CLI (commit `281fa28f` fixed the originating cause; the CLI cleans up the historical phantoms) reveal that **Stage 1 is materially smaller than the project charter implied**:

- **Doubled-prefix cleanup**: 9 of 10 phantom `PROJECT-PROJECT-*` projects are already fully reconciled; **exactly one phantom (`PROJECT-PROJECT-GTKB-RELIABILITY-FIXES`) still has 71 active memberships to supersede**. Cleanup = one `--apply` invocation of the existing CLI.
- **Prefix-split projects** (e.g. `X` and `PROJECT-X` both active for the same canonical stem): **exactly one active-BOTH pair** — `GTKB-V1-RELEASE-STRATEGY-001` (8 active memberships) vs `PROJECT-GTKB-V1-RELEASE-STRATEGY-001` (10 active memberships). Canonical is the `PROJECT-` prefixed form (matches every other GT-KB project id). Cleanup = an analogous one-shot `--apply` against a new reusable detector script.
- **`project_name` field vs membership-table divergence**: Stage 0 reports 111 inconsistent items. This surface is already owned by `WI-3500` (reporting-side correction) + `WI-3501` (formalizing the source-of-truth-freshness principle as `GOV` + `DCL`). **Stage 1 defers to those.**

The total live state mutation Stage 1 would authorize (after owner per-batch AUQ at execution time): 71 phantom memberships superseded, 1 phantom project retired, 8 memberships re-linked from the non-canonical prefix-split id to the canonical, 1 non-canonical project retired. **No new state is created.**

## Specification Links

- `GOV-STANDING-BACKLOG-001` — standing-backlog governance authority; Stage 1 reconciles structural defects under it (linked in PAUTH).
- `SPEC-AUTO-BACKLOG-FOR-IMPLEMENTATION-BEARING-SPECS-001` — auto-backlog substrate Stage 1 operates over (linked in PAUTH).
- `GOV-08` — KB is the single source of truth; Stage 1 mutates only the canonical tables it governs and only through governed paths (existing CLI + new detector with explicit `--apply` flag).
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` — the freshness principle; the new detector reads canonical tables directly (no cached snapshots), aligning with WI-3501's chartered direction.
- `ADR-STANDING-BACKLOG-DB-AUTHORITY-001` / `DCL-STANDING-BACKLOG-DB-SCHEMA-001` — the schema authority being repaired (phantom rows + duplicate canonical ids violate the implied uniqueness of project canonical form).
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — all Stage 1 changes are in-root; see Isolation Placement Compliance below.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` / `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` / `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — the durable-artifact discipline; the detector is itself a tracked durable surface (S347 owner-directive bias).
- `GOV-FILE-BRIDGE-AUTHORITY-001` — filed under `bridge/` with a matching `NEW` INDEX entry; append-only.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — all relevant specs cited here.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — verification derived below.

## Prior Deliberations

- `DELIB-20261667` — owner decision chartering this project (5 decisions + 7-stage shape, including D2 staged batch-approval and D3 priority-preserving ranking). This Stage 1 implements that decision's Stage 1 with the live-data tightening above.
- `WI-3355` — the originating doubled-prefix defect (`insert_work_item` `project_name` backfill doubled an already-`PROJECT-`-prefixed id). The originating cause was fixed in commit `281fa28f`; this Stage 1 closes out the historical phantoms (included in PAUTH v1+).
- `WI-3500` — startup-rollup uses legacy `work_items.project_name` column rather than the canonical membership table (the 111-item divergence Stage 1 explicitly defers to).
- `WI-3501` — formalize the source-of-truth-freshness principle as governance (GOV + DCL); Stage 1 defers to this for the field-vs-membership divergence remediation.
- `DELIB-S327-FORMAL-BACKLOG-DB-SCHEMA-OWNER-DIRECTIVE` — owner directive on the backlog DB schema; informs the canonical-form choice (PROJECT-prefixed id).
- `DELIB-S339-LO-STARTUP-PROJECT-STATE-REPORT` — Loyal Opposition's startup project-state report that surfaced the doubled-prefix and prefix-split classes.
- `DELIB-S357-WI-3353-PAUTH-COMPLETION` — prior session's correction that linked `WI-3353` to its real project after the doubled-prefix defect mis-filed it; demonstrates the operational remediation pattern.
- `DELIB-2505` / `DELIB-2506` / `DELIB-20261050` — substantial DA records on the WI-3355 reconciliation work; the existing CLI's behavior contract is grounded here.
- `bridge/gtkb-backlog-triage-and-hygiene-stage-0-analyzer-006.md` (VERIFIED) — the manifest source for the 1,031-open count and the 111 `project_name_inconsistent` count cited above; the detector's dedup-to-latest-version pattern is reused.

## Owner Decisions / Input

Collected via `AskUserQuestion` during the `/grill-me-for-clarification` interview on 2026-06-11, persisted to `DELIB-20261667`:

1. **D1 — Triage scope = GT-KB platform + a separate labeled Agent Red stage.** Stage 1's reconciliation operates on platform projects; the one prefix-split case (`GTKB-V1-RELEASE-STRATEGY-001`) is a platform project. No AR-scope action here.
2. **D2 — Retirement model = staged batch-approval.** Stage 1's `--apply` execution paths are explicitly NOT authorized by this bridge GO. Each execution path requires its own per-batch owner AskUserQuestion at impl time, citing the live dry-run output as evidence.
3. **D3 — Ranking axis = composite, priority-preserving.** Stage 1 does not reorder items; it only fixes project membership/identity. Item priorities are untouched.
4. **D4 — Advisory-router corpus = signal-classify + bulk-dispose.** Stage 1 does not dispose of router items; that is Stage 2's scope.
5. **D5 — Include stop-the-leak stage.** The new detector script also serves as the regression scaffold the Stage 3 stop-the-leak surface can extend.
6. **Continuation approval — "Yes" (2026-06-11).** Owner approved continuation after the Stage 0 thread reached VERIFIED at `-006` and was self-corrected on the suite-run companion-file issue.

The TWO execution-time owner decisions Stage 1 implementation will collect via separate AskUserQuestion calls (NOT authorized by this proposal's GO):

- **Stage 1.A AUQ** — approve `gt projects reconcile-doubled-prefix --apply` based on the dry-run output (1 phantom to retire, 71 memberships to supersede, zero canonical links to create — the canonicals all exist).
- **Stage 1.B AUQ** — approve the prefix-split merge of `GTKB-V1-RELEASE-STRATEGY-001` into `PROJECT-GTKB-V1-RELEASE-STRATEGY-001` (8 memberships re-linked, 1 non-canonical project retired).

## Requirement Sufficiency

**Existing requirements sufficient.** The doubled-prefix reconciliation contract is already specified by the existing `gt projects reconcile-doubled-prefix` CLI's behavior (per the prior verified work referenced in `WI-3355`, `DELIB-2505`, `DELIB-2506`). The prefix-split case is a structurally simpler analogue (no membership supersedes needed beyond the re-link; one project retire). `GOV-STANDING-BACKLOG-001`, `GOV-08`, `GOV-SOURCE-OF-TRUTH-FRESHNESS-001`, `ADR-STANDING-BACKLOG-DB-AUTHORITY-001`, and `DCL-STANDING-BACKLOG-DB-SCHEMA-001` already constrain the data-authority and freshness surfaces. No new requirement is needed.

## Backlog Visibility

`GOV-STANDING-BACKLOG-001` bulk-ops clause: the `--apply` execution paths perform bulk-class operations on `current_projects` + `current_project_work_item_memberships`. Per D2 of `DELIB-20261667`, each operation requires its own per-batch owner AskUserQuestion at execution time, citing the live dry-run output. The bounded PAUTH (v3) explicitly forbids `project_retirement_without_stage_batch_auq` and `work_item_reorder_without_stage_batch_auq`. This proposal authorizes ONLY the addition of a read-only detector script and its test; the execution paths are owner-gated separately.

## Scope and Boundaries

In scope: (1) a new `scripts/hygiene/prefix_split_detector.py` read-only detector with an opt-in `--apply` path for the specific merge case; (2) a pytest at `platform_tests/scripts/test_prefix_split_detector.py`. Out of scope and explicitly excluded: any direct mutation of `groundtruth.db` at Write time; the `project_name`-vs-membership divergence (deferred to `WI-3500` and `WI-3501`); Stage 2's router-corpus disposition; Stage 3's stop-the-leak; Stage 4's re-ranking; Stage 5's Agent Red lane; Stage 6's closeout; deploy/push. The existing-CLI invocation and the new-CLI invocation with `--apply` happen AFTER this proposal's GO and AFTER their separate owner batch AUQ.

## Proposed Implementation

**`scripts/hygiene/prefix_split_detector.py` (new).** A read-only detector module patterned on the existing `gt projects reconcile-doubled-prefix` CLI. Behavior:

1. Open `groundtruth.db` with a read-only SQLite URI (`file:...?mode=ro`).
2. Read `current_projects` and group project ids by canonical stem (strip a leading `PROJECT-` prefix if present). Identify stems with more than one id whose statuses are both `active`.
3. For each active-BOTH split, build a per-pair plan:
   - `canonical_id` = the `PROJECT-`-prefixed variant (matches every other GT-KB project id).
   - `non_canonical_id` = the bare-stem variant.
   - `memberships_to_relink` = list of `(work_item_id, current_membership_id)` from `current_project_work_item_memberships` where `project_id = non_canonical_id` AND status is active.
   - `non_canonical_project_to_retire` = the non-canonical project record.
4. Default mode (no `--apply`) emits the plan as JSON to stdout (idempotent, deterministic — sorted by canonical id, sorted by work_item_id within each pair). Identical to the existing reconcile CLI's contract.
5. `--apply` flag — explicitly opt-in — performs the membership re-link and the non-canonical project retire **for a single owner-specified pair only** (the CLI takes `--canonical PROJECT-X --merge-from X`). The script will REFUSE to operate if either id is not in the dry-run's active-BOTH set. This is the safety belt: even with `--apply`, an owner cannot accidentally retire an unrelated project.

**`platform_tests/scripts/test_prefix_split_detector.py` (new).** Tests covering: detection of active-BOTH splits on a synthetic fixture; correct canonical-form selection (PROJECT-prefixed wins); no-mutation guarantee (AST + read-only connection + row-count-unchanged); determinism (two runs produce identical output); `--apply` refuses to operate on an id pair that is not an active-BOTH split; a regression assert that registering the module does not break anything else.

**No changes to `groundtruth-kb/src/groundtruth_kb/*`.** The new detector lives under `scripts/hygiene/` so it stays out of the installed CLI surface until a follow-on stage (or Stage 6's regression guard) explicitly promotes it to `gt projects reconcile-prefix-split`. That promotion is intentionally a separate decision so this stage stays scoped.

## Isolation Placement Compliance

`ADR-ISOLATION-APPLICATION-PLACEMENT-001`: all Stage 1 changes are in-root under `E:\GT-KB\` — the detector under `scripts/hygiene/`, the test under `platform_tests/scripts/`, and this bridge file under `E:\GT-KB\bridge\`. The stage relocates no application file, touches no `applications/` subtree, and writes no out-of-root artifact.

## Spec-Derived Verification Plan

| Spec / requirement | Derived test |
|---|---|
| `GOV-STANDING-BACKLOG-001` + `ADR-STANDING-BACKLOG-DB-AUTHORITY-001` (canonical project id uniqueness) | test: on a synthetic fixture with active-BOTH split pairs, the detector identifies each pair exactly once, selects the `PROJECT-`-prefixed variant as canonical, and emits the membership-relink + project-retire plan |
| `GOV-08` (read-only; no canonical mutation at Write time) | test: AST scan of `prefix_split_detector.py` asserts no `commit`/`UPDATE`/`DELETE`/`INSERT` write paths in the default (no `--apply`) code path; the DB connection is opened read-only; a no-mutation row-count check confirms `current_projects` and `current_project_work_item_memberships` are unchanged after a default-mode run |
| `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` (canonical reads, no cached snapshots) | test: the detector reads `current_projects` and `current_project_work_item_memberships` directly (no intermediate snapshot file); a fixture mutation between two consecutive runs produces different output (freshness) |
| D2 (per-batch owner AUQ before `--apply`) | test: `--apply` invoked without `--canonical` + `--merge-from` exits non-zero with an "owner must specify the pair" error; `--apply --canonical X --merge-from Y` refuses if (X, Y) is not in the dry-run's active-BOTH set |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `python -m pytest platform_tests/scripts/test_prefix_split_detector.py -q`; `ruff check` AND `ruff format --check` on every changed Python file |

## Acceptance Criteria

1. `scripts/hygiene/prefix_split_detector.py` exists, runs read-only by default, and emits a deterministic JSON plan for every active-BOTH prefix-split pair.
2. `--apply --canonical X --merge-from Y` is the only path that mutates the DB, refuses to operate on any pair not present in the current dry-run, and is idempotent on rerun (re-linking already-canonical members is a no-op).
3. The no-mutation AST scan, the read-only connection check, and the row-count-unchanged guard all pass.
4. Classification + plan emission is deterministic across two runs on identical input.
5. All new tests pass; `ruff check` and `ruff format --check` are clean on every changed Python file.

## Bridge Protocol Compliance

Filed at `bridge/gtkb-backlog-triage-and-hygiene-stage-1-structural-repair-001.md` with a matching `NEW` entry directly below the Document header at the top of `bridge/INDEX.md`; append-only. `GOV-FILE-BRIDGE-AUTHORITY-001` is honored; nothing implements until Loyal Opposition records `GO`. At implementation time the implementation-start packet will be minted from the GO against the bounded authorization PAUTH (v3) under the `source_addition` / `test_addition` mutation classes. The two execution paths that mutate canonical tables (`gt projects reconcile-doubled-prefix --apply` and `prefix_split_detector.py --apply`) execute only AFTER their separate per-batch owner AskUserQuestion approvals — not at file Write time.

## Risk and Rollback

- **Risk — detector mislabels a legitimate two-id-but-different-purpose pair as a prefix-split:** mitigated by the canonical-stem definition (strict leading `PROJECT-` strip; nothing else). If a future project legitimately needs both forms (none today), the detector's `--apply` refusal-on-mismatch guard prevents accidental retire; owner can also refuse the Stage 1.B AUQ. **Rollback:** delete the detector module + test (additive, no state touched at Write time).
- **Risk — the existing `gt projects reconcile-doubled-prefix --apply` removes too much:** the dry-run is purpose-built for owner pre-approval and reports exactly what will change (1 phantom retire, 71 memberships supersede, 0 canonical link creates). Append-only versioning means the supersedes are reversible by inserting a successor membership row. **Rollback:** insert a successor membership row restoring the prior link (the supersede chain is auditable).
- **Risk — the `GTKB-V1-RELEASE-STRATEGY-001` merge re-links an item that has historical reason to be in the non-canonical project:** the dry-run lists every (work_item, project) pair before any mutation; owner can refuse the Stage 1.B AUQ if they spot something wrong. **Rollback:** for any specific item, re-link to the non-canonical project via `gt projects add-item` (append-only, no destructive deletion).
- **Risk — adding a parallel detector pattern to the existing `reconcile-doubled-prefix` confuses the surface:** mitigated by placing the new detector under `scripts/hygiene/` rather than the installed `gt projects` CLI. A follow-on stage may promote it to `gt projects reconcile-prefix-split` if the pattern proves load-bearing; that promotion is intentionally a separate decision.

## Recommended Implementation Routing

**Claude/Codex (deterministic source + test).** Stage 1 is greenfield read-only source plus a pytest under an existing PAUTH with no protected-narrative or KB-mutation surface at Write time — cleanly draftable. The intellectual care is in the safety belt: refusing `--apply` on any pair not present in the live dry-run (so future drift doesn't silently mis-apply a stale plan). The two `--apply` executions happen AFTER bridge GO AND their separate owner batch AUQ; that pacing is what makes Stage 1 reversible and proportionate.

## Recommended Commit Type

`feat:` — net-new detector script + test suite (a new measurement + safe-merge capability), with no behavior change to existing surfaces. The `--apply` executions that occur separately are not part of the commit Stage 1 produces.
