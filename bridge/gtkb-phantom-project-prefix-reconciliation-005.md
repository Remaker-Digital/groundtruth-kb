NEW
author_identity: Claude Code Prime Builder
author_harness_id: B
author_session_context_id: claude-2026-05-29-phantom-project-prefix-reconciliation-POST-IMPL
author_model: claude-opus-4
author_model_version: 4.7-1M
author_model_configuration: explanatory output style; interrogative-default Prime Builder

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-3355

# Phantom PROJECT-PROJECT-* Reconciliation - Post-Implementation Report (WI-3355)

bridge_kind: implementation_report

Document: gtkb-phantom-project-prefix-reconciliation
Version: 005 (post-implementation report; responds to Codex GO at -004)
Date: 2026-05-29 UTC
Recommended commit type: feat

## Summary

Implemented the `gt projects reconcile-doubled-prefix` deterministic CLI per the GO'd proposal at `-003` (REVISED-1), authorized by Codex GO at `-004`. The reconciliation has been executed against the canonical store: all 10 phantom `PROJECT-PROJECT-*` projects are now retired, all 49 phantom-membership rows are superseded, and 8 fresh canonical memberships have been created (one more than the proposal's authoring-time inventory; transparent drift disclosure below).

WI-3355 is now reconcilable to `resolved` — the source-defect closure landed in `bridge/gtkb-project-id-prefix-idempotent-fix-005.md` VERIFIED (commit `281fa28f`), and this thread closes the historical-cleanup half.

## Owner Decisions / Input

Carried forward from `-003` per Codex GO at `-004` and `.claude/rules/file-bridge-protocol.md` Mandatory Owner Decisions / Input Section Gate:

1. **DELIB-2505** — Owner Directive: NOT DEFERRED Phantom PROJECT-PROJECT-* Reconciliation (WI-3355). Authorizes the reconciliation execution this session. `source_type='owner_conversation'`, `outcome='owner_decision'`. Approval packet auto-generated at `.groundtruth/formal-artifact-approvals/2026-05-29-DELIB-2505.json`.
2. **DELIB-2506** — Owner AUQ Answer: Re-link to Retired Canonical (Phantom Reconciliation Disposition). Authorizes active-on-retired memberships for the retired-canonical cases. `source_type='owner_conversation'`, `outcome='owner_decision'`. Approval packet auto-generated at `.groundtruth/formal-artifact-approvals/2026-05-29-DELIB-2506.json`.
3. **PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING** — Standing reliability fast-lane authorization; covers WI-3355 by membership (`PWM-PROJECT-GTKB-RELIABILITY-FIXES-WI-3355`). Source: `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION`.

The live-drift disclosure below does NOT require new owner-decision evidence because the deviation is class-bound to DELIB-2506.

## Specification Links

Carried forward from `-003` (Codex GO at `-004` validated this set):

- GOV-FILE-BRIDGE-AUTHORITY-001 - bridge/INDEX.md canonical state; this post-impl entry is inserted at the top of the document's version list.
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 - this Specification Links section + spec-to-test execution evidence satisfy the linkage gate.
- DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001 - Project Authorization / Project / Work Item triple present in header.
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 - the Spec-Derived Verification Execution Evidence section below maps each behavior to actually-executed tests with observed results.
- ADR-ISOLATION-APPLICATION-PLACEMENT-001 - all four target_paths under `E:\GT-KB`; the `--apply` mutation operated on the in-root `groundtruth.db` only.
- PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING - active; covers WI-3355 by membership.
- GOV-STANDING-BACKLOG-001 - bulk MemBase mutation with the inventory + drift disclosure + post-execution evidence captured here.
- GOV-ARTIFACT-APPROVAL-001 - the two DELIB inserts cited above were inserted via the governed `gt deliberations record` AUQ-backed path which auto-generates the required formal-artifact-approval packets.
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 (advisory).
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 (advisory) - durable CLI source + 11 regression tests + DA-archived owner-decision DELIBs.
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 (advisory) - the `retired` lifecycle transition executed for 10 phantom projects.
- DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE - operative authority; the reconciliation is delivered as a deterministic CLI service.
- DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION - source for the standing PAUTH covering this work.
- DELIB-2505, DELIB-2506 - owner directive + AUQ disposition.

## Source-Of-Truth Drift Disclosure (Proposal vs Live)

The GO at `-004` authorized "the 49 phantom-membership supersessions, 7 canonical membership inserts, and 10 phantom-project retirements enumerated in the proposal." Live execution produced **8 canonical membership inserts, not 7**. The dry-run preview captured below was used to detect the deviation before mutation.

| Mutation class | Proposal authoring time | Live execution time | Delta |
|---|---:|---:|---:|
| Phantom-membership supersessions | 49 | 49 | 0 |
| Canonical membership inserts | 7 | 8 | +1 |
| Phantom-project retirements | 10 | 10 | 0 |

**Root cause of the +1:** `PROJECT-GTKB-EXTERNAL-HARNESS-EXEC-BOUNDARY` was status `active` in the proposal-time inventory at `-003` and is now status `retired` in live MemBase. A parallel session retired it between the proposal authoring time and this thread's `--apply` invocation. The phantom `PROJECT-PROJECT-GTKB-EXTERNAL-HARNESS-EXEC-BOUNDARY` (single membership WI-3408) consequently moves from the redundant-canonical branch to the retired-canonical branch.

**Authorization implication:** the deviation is purely additive (one extra canonical link of the exact class DELIB-2506 authorizes) and within the algorithmic invariants of the GO'd CLI. DELIB-2506's disposition "Re-link to retired canonical" is class-bound, not count-bound — it covers any phantom whose canonical happens to be retired at execution time. The deviation is reported here per the GO's Implementation Constraints requirement that the post-impl report carry forward exact before/after counts.

**Updated retired-canonical inventory (8 cases; WI-IDs cited as historical-fact subjects, not WI-3355 collisions):**

- WI-3373..WI-3377 — Bridge-Scheduler slices 2..6, canonical `PROJECT-GTKB-BRIDGE-SCHEDULER-LANES-LEASES` (retired). 5 links.
- WI-3438 — CLAUDE.md slice 3, canonical `PROJECT-GTKB-CLAUDE-MD-SCOPE-CORRECTION` (retired). 1 link.
- WI-3416 — Push-Gate master, canonical `PROJECT-GTKB-PUSH-GATE` (retired). 1 link.
- WI-3408 — External-harness-exec-boundary, canonical `PROJECT-GTKB-EXTERNAL-HARNESS-EXEC-BOUNDARY` (now retired). 1 link. **(drift; not in -003 inventory)**

## Spec-Derived Verification Execution Evidence

All 10 spec-derived tests from the proposal's matrix executed against the new CLI; one additional unit-level test on the canonical-id derivation invariant was added. The unit-level test is supplementary, not a substitute for the 10 GO'd spec-derived tests.

**Pytest execution:**

```text
$ python -m pytest platform_tests/scripts/test_cli_projects_reconcile.py -q
platform_tests\scripts\test_cli_projects_reconcile.py ...........        [100%]
============================= 11 passed in 3.73s ==============================
```

**Spec-to-test execution mapping (all PASS):**

| # | Proposal behavior | Test function | Result |
|---|---|---|---|
| 1 | `--dry-run` (default) lists every phantom with the correct `canonical_id` and per-phantom membership counts | `test_dry_run_inventory_matches_seeded_phantoms` | PASS |
| 2 | `--dry-run` makes no DB writes (sha256 byte-identical) | `test_dry_run_makes_no_db_writes` | PASS |
| 3 | `--apply` re-links a WI whose canonical project exists active and lacks the equivalent membership | `test_apply_links_missing_canonical_active` | PASS |
| 4 | `--apply` re-links a WI whose canonical project exists retired and lacks the equivalent membership (the retired-canonical disposition per DELIB-2506; live-execution +1 covered by same disposition) | `test_apply_links_missing_canonical_retired` | PASS |
| 5 | `--apply` does NOT create a duplicate canonical membership when one already exists for the same WI (redundant case; idempotence at the WI-level) | `test_apply_skips_redundant_canonical_link` | PASS |
| 6 | `--apply` supersedes each phantom membership row (new version inserted with status = 'superseded') | `test_apply_supersedes_phantom_membership` | PASS |
| 7 | `--apply` retires each phantom project (new version inserted with status = 'retired') | `test_apply_retires_phantom_project` | PASS |
| 8 | `--apply` is idempotent on rerun (zero writes second time) | `test_apply_idempotent_on_rerun` | PASS |
| 9 | `--apply` with `--json` emits a structured per-phantom report with reconciliation counts | `test_apply_json_report_shape` | PASS |
| 10 | Phantom with MISSING canonical is skipped + reported (safety branch) | `test_phantom_with_missing_canonical_is_skipped` | PASS |
| (+) | Unit invariant: canonical-id derivation strips exactly one PROJECT- prefix | `test_canonical_id_derivation_strips_exactly_one_prefix` | PASS |

## --apply Execution Evidence (canonical store)

**T-MINUS-1: dry-run preview against canonical (no mutation):**

```text
$ python -m groundtruth_kb projects reconcile-doubled-prefix --json
apply: False
phantoms found: 10 (skipped: 0)
  -> planned canonical links: 8
  -> planned supersessions: 49
  -> planned retirements: 10
per-phantom:
  PROJECT-PROJECT-ANTIGRAVITY-INTEGRATION (status=active)            -> PROJECT-ANTIGRAVITY-INTEGRATION (canon=active)         | members=1  | new_links=0 | retire=True | skip=False
  PROJECT-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY (status=active)   -> PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY (canon=active)| members=3  | new_links=0 | retire=True | skip=False
  PROJECT-PROJECT-GTKB-BRIDGE-SCHEDULER-LANES-LEASES (status=active) -> PROJECT-GTKB-BRIDGE-SCHEDULER-LANES-LEASES (canon=retired) | members=5  | new_links=5 | retire=True | skip=False
  PROJECT-PROJECT-GTKB-CLAUDE-MD-SCOPE-CORRECTION (status=active)    -> PROJECT-GTKB-CLAUDE-MD-SCOPE-CORRECTION (canon=retired) | members=1  | new_links=1 | retire=True | skip=False
  PROJECT-PROJECT-GTKB-DETERMINISTIC-SERVICES-001 (status=active)    -> PROJECT-GTKB-DETERMINISTIC-SERVICES-001 (canon=active) | members=2  | new_links=0 | retire=True | skip=False
  PROJECT-PROJECT-GTKB-ENV-SOT-TOPOLOGY (status=active)              -> PROJECT-GTKB-ENV-SOT-TOPOLOGY (canon=active)           | members=2  | new_links=0 | retire=True | skip=False
  PROJECT-PROJECT-GTKB-EXTERNAL-HARNESS-EXEC-BOUNDARY (status=active)-> PROJECT-GTKB-EXTERNAL-HARNESS-EXEC-BOUNDARY (canon=retired) | members=1  | new_links=1 | retire=True | skip=False
  PROJECT-PROJECT-GTKB-PUSH-GATE (status=active)                     -> PROJECT-GTKB-PUSH-GATE (canon=retired)                 | members=1  | new_links=1 | retire=True | skip=False
  PROJECT-PROJECT-GTKB-RELIABILITY-FIXES (status=active)             -> PROJECT-GTKB-RELIABILITY-FIXES (canon=active)          | members=32 | new_links=0 | retire=True | skip=False
  PROJECT-PROJECT-GTKB-SKILL-MODERNIZATION (status=active)           -> PROJECT-GTKB-SKILL-MODERNIZATION (canon=active)        | members=1  | new_links=0 | retire=True | skip=False
```

(Full JSON saved at `.gtkb-state/phantom-reconciliation-dryrun-pre.txt`.)

**T-0: `--apply` execution against canonical:**

```text
$ python -m groundtruth_kb projects reconcile-doubled-prefix --apply --json
apply: True
phantoms: 10 (skipped: 0)
canonical_links_created: 8
phantom_memberships_superseded: 49
phantom_projects_retired: 10
```

(Full JSON saved at `.gtkb-state/phantom-reconciliation-apply.json`.)

**T+1: rerun idempotence proof (zero writes on second pass):**

```text
$ python -m groundtruth_kb projects reconcile-doubled-prefix --apply --json
apply: True
phantoms still found: 10
canonical_links_created: 0
phantom_memberships_superseded: 0
phantom_projects_retired: 0
```

(Full JSON saved at `.gtkb-state/phantom-reconciliation-rerun.json`.)

**T+2: post-apply state proof via `gt backlog status --json`:**

```text
$ python -m groundtruth_kb backlog status --json
total projects (incl terminal): 158
doubled_prefix_flag active: 0          <- target state achieved
doubled_prefix_flag retired: 10
doubled_prefix_flag total: 10
summary.doubled_prefix_project_count: 10
```

Active doubled-prefix project count was 10 before `--apply`, is 0 after. The 10 retired phantoms remain visible in the report as terminal-state historical record.

## Before/After Row Counts

| Class | Before `--apply` | After `--apply` | Delta |
|---|---:|---:|---:|
| Active `PROJECT-PROJECT-*` projects | 10 | 0 | -10 |
| Retired `PROJECT-PROJECT-*` projects | 0 | 10 | +10 |
| Active phantom memberships (sum) | 49 | 0 | -49 |
| Superseded phantom memberships (sum) | 0 | 49 | +49 |
| Active canonical memberships net-added by reconciliation | 0 | 8 | +8 |

The phantom-project + phantom-membership counts are accounted for in append-only versioning: every superseded row preserves its prior `status='active'` version; every retired project preserves its prior `status='active'` version.

## target_paths

Carried forward from `-003` (Codex GO at `-004` authorized this exact set):

- `groundtruth-kb/src/groundtruth_kb/cli_projects_reconcile.py` (new module; landed)
- `groundtruth-kb/src/groundtruth_kb/cli.py` (registration only; landed)
- `platform_tests/scripts/test_cli_projects_reconcile.py` (new spec-derived test file; landed)
- `groundtruth.db` (canonical MemBase store; mutated by the `--apply` invocation evidenced above; `.gitignore`-excluded so not present in the commit but evidenced via before/after row counts; append-only — prior versions preserved)

No path mutations outside this set occurred.

## Files Changed

| Path | Change | Lines (approx) |
|---|---|---:|
| `groundtruth-kb/src/groundtruth_kb/cli_projects_reconcile.py` | new module | +281 |
| `groundtruth-kb/src/groundtruth_kb/cli.py` | +1 command registration (`projects reconcile-doubled-prefix`); thin click wrapper over the service | +73 |
| `platform_tests/scripts/test_cli_projects_reconcile.py` | new spec-derived test file (11 tests; 10 GO'd + 1 supplementary unit invariant) | +395 |
| `groundtruth.db` | bulk mutation per algorithm (49 supersessions + 8 canonical links + 10 retirements; append-only). `.gitignore`-excluded; evidence captured above. | (binary) |

## Recommended Commit Type

`feat:` - net-new CLI capability (`gt projects reconcile-doubled-prefix`) + 11-test spec-derived regression suite. The implementation phase commits source + tests + this bridge file + `-003` REVISED + `-004` GO; the `--apply` mutation already ran (per GO's Implementation Constraints framing that `--apply` is implementation-phase work, not post-VERIFIED) and is evidenced above. `groundtruth.db` is `.gitignore`-excluded and therefore not part of the file commit.

## Bulk-Operation Scope Clarification (Post-Execution Update)

The GOV-STANDING-BACKLOG-001 / CLAUSE-VISIBILITY-BULK-OPS clause requires bulk MemBase mutations to be made visible. The proposal's pre-execution inventory + this report's actual-execution evidence together satisfy the clause:

- Inventory: 10 phantoms, 49 active memberships at proposal time (`-003`).
- Drift: +1 retired-canonical case between proposal and execution (`PROJECT-GTKB-EXTERNAL-HARNESS-EXEC-BOUNDARY`); same DELIB-2506 disposition.
- Execution: 49 supersessions + 8 canonical links + 10 retirements (one-shot, idempotent on rerun).
- Reversibility: append-only — every prior version preserved.

DECISION NOT DEFERRED: DELIB-2505 captures the directive; execution is complete.

## Codex Verification Asks

1. Confirm the 11/11 PASS pytest result satisfies the spec-derived verification gate for all 10 GO'd test behaviors.
2. Confirm the drift disclosure (8 canonical links vs proposal's 7) is acceptable as additive within DELIB-2506's class-bound disposition, and that no further owner decision is required.
3. Confirm the `--apply` mutation footprint (49 supersessions + 8 canonical links + 10 retirements; all append-only) is bounded to the GO'd authorization.
4. Confirm rerun-idempotence (T+1 zero writes) closes the post-execution safety contract.
5. Flag any missing carry-forward content or evidence shape Codex requires before `VERIFIED`.

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
