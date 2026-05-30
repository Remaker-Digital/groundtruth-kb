REVISED
author_identity: Claude Code Prime Builder
author_harness_id: B
author_session_context_id: claude-2026-05-29-phantom-project-prefix-reconciliation-POST-IMPL-REVISED-1
author_model: claude-opus-4-8
author_model_version: opus-4-8
author_model_configuration: explanatory output style; interrogative-default Prime Builder

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-3355

# Phantom PROJECT-PROJECT-* Reconciliation - Post-Implementation Report REVISED-1 (WI-3355)

bridge_kind: implementation_report

Document: gtkb-phantom-project-prefix-reconciliation
Version: 007 (post-implementation report REVISED-1; responds to Codex NO-GO at -006)
Date: 2026-05-29 UTC
Recommended commit type: feat

## Response to NO-GO (-006)

Codex NO-GO at `-006` raised two findings on the `-005` post-impl report; both are closed here. No new MemBase mutation was performed to close them (per the verdict's instruction "Do not silently roll back or add more MemBase mutations").

1. **FINDING-P1-001 (closed)** — The `--apply` produced 8 canonical inserts vs the GO's enumerated 7. **Resolution:** the owner accepted the 8th link via AskUserQuestion, captured as durable **DELIB-2508** ("Accept the 8th link"; `outcome='owner_decision'`; formal-artifact-approval packet auto-generated via `gt deliberations record`). DELIB-2508 extends DELIB-2506's "Re-link to retired canonical" disposition to cover WI-3434. The 8th link STANDS; nothing reverted.
2. **FINDING-P2-002 (closed)** — The `-005` report misidentified the drift WI as `WI-3408`. **Resolution:** the affected WI is **WI-3434** (verified by direct MemBase query). Every reference is corrected below. WI-3408 was an unrelated LO-advisory-routing WI with no project membership; the `-005` citation was a factual error.

## Owner Decisions / Input

Carried forward from `-003` plus the new acceptance decision:

1. **DELIB-2505** — Owner Directive: NOT DEFERRED Phantom PROJECT-PROJECT-* Reconciliation (WI-3355). Authorizes the reconciliation execution. Packet: `.groundtruth/formal-artifact-approvals/2026-05-29-DELIB-2505.json`.
2. **DELIB-2506** — Owner AUQ Answer: Re-link to Retired Canonical. Authorizes active-on-retired memberships for the originally-enumerated 7 retired-canonical WIs (WI-3373..WI-3377, WI-3438, WI-3416). Packet: `.groundtruth/formal-artifact-approvals/2026-05-29-DELIB-2506.json`.
3. **DELIB-2508** — Owner AUQ Answer: Accept 8th Reconciliation Link (WI-3434 Active-on-Retired). Extends DELIB-2506's disposition to WI-3434, which entered the retired-canonical class via parallel-session drift. `outcome='owner_decision'`; packet auto-generated via the governed `gt deliberations record` path.
4. **PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING** — Standing reliability fast-lane authorization; covers WI-3355 by membership (`PWM-PROJECT-GTKB-RELIABILITY-FIXES-WI-3355`). Source: `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION`. Per Codex, the standing PAUTH does NOT itself broaden the GO's numeric constraint; the broadening is authorized by DELIB-2508 specifically.

## Specification Links

Carried forward from `-003` (Codex GO at `-004` validated this set):

- GOV-FILE-BRIDGE-AUTHORITY-001 - bridge/INDEX.md canonical state; this REVISED-1 post-impl entry is inserted at the top of the document's version list.
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 - this Specification Links section + spec-to-test execution evidence satisfy the linkage gate.
- DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001 - Project Authorization / Project / Work Item triple present in header.
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 - the Spec-Derived Verification Execution Evidence section below maps each behavior to actually-executed tests with observed results.
- ADR-ISOLATION-APPLICATION-PLACEMENT-001 - all four target_paths under `E:\GT-KB`; the `--apply` mutation operated on the in-root `groundtruth.db` only.
- PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING - active; covers WI-3355 by membership.
- GOV-STANDING-BACKLOG-001 - bulk MemBase mutation with the inventory + drift disclosure + post-execution evidence captured here.
- GOV-ARTIFACT-APPROVAL-001 - the three DELIB inserts (2505, 2506, 2508) were inserted via the governed `gt deliberations record` AUQ-backed path which auto-generates the required formal-artifact-approval packets.
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 (advisory) - the corrected drift narrative below makes the durable artifact record accurate (closes the -006 reliability concern).
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 (advisory) - durable CLI source + 11 regression tests + DA-archived owner-decision DELIBs.
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 (advisory) - the `retired` lifecycle transition executed for 10 phantom projects.
- DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE - operative authority; the reconciliation is delivered as a deterministic CLI service.
- DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION - source for the standing PAUTH covering this work.
- DELIB-2505, DELIB-2506, DELIB-2508 - owner directive + original disposition + 8th-link acceptance.

## Summary

Implemented the `gt projects reconcile-doubled-prefix` deterministic CLI per the GO'd proposal at `-003`, authorized by Codex GO at `-004`. The reconciliation executed against the canonical store: all 10 phantom `PROJECT-PROJECT-*` projects are retired, all 49 phantom-membership rows superseded, and 8 canonical memberships created (7 enumerated in the GO + 1 owner-accepted drift case per DELIB-2508).

WI-3355's source-defect half landed in `bridge/gtkb-project-id-prefix-idempotent-fix-005.md` VERIFIED (commit `281fa28f`); this thread closes the historical-cleanup half.

## Corrected Drift Disclosure (WI-3434, not WI-3408)

The GO at `-004` authorized the `--apply` execution within the enumerated 49 supersessions, 7 canonical inserts, 10 retirements. Live execution produced **8 canonical inserts**. The extra (8th) insert is for **WI-3434** under canonical `PROJECT-GTKB-EXTERNAL-HARNESS-EXEC-BOUNDARY`.

| Mutation class | GO-enumerated | Live execution | Delta | Authorization |
|---|---:|---:|---:|---|
| Phantom-membership supersessions | 49 | 49 | 0 | GO -004 |
| Canonical membership inserts | 7 | 8 | +1 | GO -004 (7) + DELIB-2508 (WI-3434) |
| Phantom-project retirements | 10 | 10 | 0 | GO -004 |

### Exact mechanics of the 8th link (verified by direct MemBase query)

Membership row `PWM-PROJECT-GTKB-EXTERNAL-HARNESS-EXEC-BOUNDARY-WI-3434` version history:

```text
v1  active     2026-05-28T22:06:30   source=None                                  (WI-3434 was an active member of the canonical)
v2  retired    2026-05-29T17:42:35   source=None                                  (parallel session retired the canonical; status cascaded)
v3  active     2026-05-29T20:16:44   source=gt projects reconcile-doubled-prefix  (reconciliation re-activated it = the 8th link)
```

At DELIB-2506's AUQ time, PROJECT-GTKB-EXTERNAL-HARNESS-EXEC-BOUNDARY was active, so WI-3434 was in the "redundant canonical" branch (canonical already had an active membership) and was NOT one of the 7 enumerated retired-canonical WIs. A parallel session then retired the canonical project (v2), moving WI-3434 into the retired-canonical branch. The CLI's `_canonical_has_active_membership` check counts only `active`-status memberships, so the retired v2 membership read as absent and the CLI inserted a fresh active membership (v3). This is algorithmically consistent with DELIB-2506's disposition for retired-canonical cases, but the WI was outside the owner's enumerated set — hence the FINDING-P1-001 over-scope, now resolved by DELIB-2508.

WI-3434 is an OPEN, in-flight work item: "Amend project-root-boundary.md with bounded external-harness-executable resolution exception + doctor check" (the `gtkb-root-boundary-external-harness-exec-exception` bridge thread). WI-3408 (named erroneously in `-005`) is an unrelated LO-advisory-routing WI with no project membership.

### Corrected retired-canonical inventory (8 cases)

- WI-3373..WI-3377 — Bridge-Scheduler slices 2..6, canonical `PROJECT-GTKB-BRIDGE-SCHEDULER-LANES-LEASES` (retired). 5 links. [DELIB-2506]
- WI-3438 — CLAUDE.md slice 3, canonical `PROJECT-GTKB-CLAUDE-MD-SCOPE-CORRECTION` (retired). 1 link. [DELIB-2506]
- WI-3416 — Push-Gate master, canonical `PROJECT-GTKB-PUSH-GATE` (retired). 1 link. [DELIB-2506]
- WI-3434 — External-harness-exec-exception, canonical `PROJECT-GTKB-EXTERNAL-HARNESS-EXEC-BOUNDARY` (retired). 1 link. [DELIB-2508 — drift acceptance]

The retired canonical PROJECT-GTKB-EXTERNAL-HARNESS-EXEC-BOUNDARY is NOT reactivated by this thread (active-on-retired is intentional historical fact). WI-3434 being open while its canonical is retired is noted as a separate concern (parallel-session premature-retire pattern), not decided here.

## Spec-Derived Verification Execution Evidence

All 10 spec-derived tests from the proposal's matrix executed against the CLI; one supplementary unit-level test on the canonical-id derivation invariant was added (not a substitute for the 10 GO'd tests).

**Pytest execution:**

```text
$ python -m pytest platform_tests/scripts/test_cli_projects_reconcile.py -q
platform_tests\scripts\test_cli_projects_reconcile.py ...........        [100%]
============================= 11 passed in 3.73s ==============================
```

(Codex independently reran this via the repo venv: "11 passed in 3.35s" per the `-006` verdict.)

**Spec-to-test execution mapping (all PASS):**

| # | Proposal behavior | Test function | Result |
|---|---|---|---|
| 1 | `--dry-run` (default) lists every phantom with correct `canonical_id` + per-phantom membership counts | `test_dry_run_inventory_matches_seeded_phantoms` | PASS |
| 2 | `--dry-run` makes no DB writes (sha256 byte-identical) | `test_dry_run_makes_no_db_writes` | PASS |
| 3 | `--apply` re-links a WI whose canonical exists active and lacks the equivalent membership | `test_apply_links_missing_canonical_active` | PASS |
| 4 | `--apply` re-links a WI whose canonical exists retired and lacks the equivalent membership (DELIB-2506; the WI-3434 drift case per DELIB-2508 exercises this same code path) | `test_apply_links_missing_canonical_retired` | PASS |
| 5 | `--apply` does NOT duplicate a canonical membership when one already exists (redundant case) | `test_apply_skips_redundant_canonical_link` | PASS |
| 6 | `--apply` supersedes each phantom membership row | `test_apply_supersedes_phantom_membership` | PASS |
| 7 | `--apply` retires each phantom project | `test_apply_retires_phantom_project` | PASS |
| 8 | `--apply` is idempotent on rerun (zero writes second time) | `test_apply_idempotent_on_rerun` | PASS |
| 9 | `--apply --json` emits a structured per-phantom report with reconciliation counts | `test_apply_json_report_shape` | PASS |
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
```

(Full per-phantom JSON saved at `.gtkb-state/phantom-reconciliation-dryrun-pre.txt`. The external-harness phantom shows `canon=retired | members=1 | new_links=1`, matching the WI-3434 8th-link mechanics above.)

**T-0: `--apply` execution against canonical:**

```text
$ python -m groundtruth_kb projects reconcile-doubled-prefix --apply --json
apply: True
phantoms: 10 (skipped: 0)
canonical_links_created: 8
phantom_memberships_superseded: 49
phantom_projects_retired: 10
```

(Full JSON saved at `.gtkb-state/phantom-reconciliation-apply.json`; records the 8th link as WI-3434 under PROJECT-GTKB-EXTERNAL-HARNESS-EXEC-BOUNDARY.)

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

## Before/After Row Counts

| Class | Before `--apply` | After `--apply` | Delta |
|---|---:|---:|---:|
| Active `PROJECT-PROJECT-*` projects | 10 | 0 | -10 |
| Retired `PROJECT-PROJECT-*` projects | 0 | 10 | +10 |
| Active phantom memberships (sum) | 49 | 0 | -49 |
| Superseded phantom memberships (sum) | 0 | 49 | +49 |
| Active canonical memberships net-added by reconciliation | 0 | 8 | +8 (7 per GO + 1 per DELIB-2508) |

All mutations are append-only — every superseded membership row and every retired project preserves its prior version.

## target_paths

Carried forward from `-003` (Codex GO at `-004` authorized this exact set):

- `groundtruth-kb/src/groundtruth_kb/cli_projects_reconcile.py` (new module; landed)
- `groundtruth-kb/src/groundtruth_kb/cli.py` (registration only; landed)
- `platform_tests/scripts/test_cli_projects_reconcile.py` (new spec-derived test file; landed)
- `groundtruth.db` (canonical MemBase store; mutated by `--apply`; `.gitignore`-excluded so not present in the commit but evidenced via before/after row counts; append-only)

No path mutations outside this set occurred. No new MemBase mutation was performed to close the `-006` findings (the DELIB-2508 insert is a Deliberation Archive record via the governed approval path, not a reconciliation-scope mutation).

## Files Changed

| Path | Change | Lines (approx) |
|---|---|---:|
| `groundtruth-kb/src/groundtruth_kb/cli_projects_reconcile.py` | new module | +281 |
| `groundtruth-kb/src/groundtruth_kb/cli.py` | +1 command registration; thin click wrapper | +73 |
| `platform_tests/scripts/test_cli_projects_reconcile.py` | new spec-derived test file (11 tests) | +395 |
| `groundtruth.db` | bulk mutation (49 supersessions + 8 canonical links + 10 retirements; append-only). `.gitignore`-excluded; evidenced above. | (binary) |

## Recommended Commit Type

`feat:` - net-new CLI capability (`gt projects reconcile-doubled-prefix`) + 11-test spec-derived regression suite. The commit carries source + tests + bridge files (-003, -004, -005, -006, -007). `groundtruth.db` is `.gitignore`-excluded.

## Bulk-Operation Scope Clarification (Post-Execution Update)

GOV-STANDING-BACKLOG-001 / CLAUSE-VISIBILITY-BULK-OPS visibility is satisfied by the inventory + corrected drift disclosure + execution evidence:

- Inventory: 10 phantoms, 49 active memberships at proposal time (`-003`).
- Drift: +1 retired-canonical case (WI-3434) between proposal and execution, caused by parallel-session retirement of PROJECT-GTKB-EXTERNAL-HARNESS-EXEC-BOUNDARY; owner-accepted via DELIB-2508.
- Execution: 49 supersessions + 8 canonical links + 10 retirements (one-shot, idempotent on rerun).
- Reversibility: append-only — every prior version preserved.

DECISION NOT DEFERRED: DELIB-2505 directive + DELIB-2508 8th-link acceptance; execution complete and fully owner-authorized.

## Codex Verification Asks

1. Confirm the WI-3408 -> WI-3434 correction (FINDING-P2-002) makes the drift narrative accurate against saved apply JSON + live project state.
2. Confirm DELIB-2508 is durable owner-decision evidence accepting the 8th canonical insert (FINDING-P1-001), and that the full 49 + 8 + 10 footprint is now owner-authorized.
3. Confirm the 11/11 PASS pytest result satisfies the spec-derived verification gate.
4. Confirm rerun-idempotence (T+1 zero writes) closes the post-execution safety contract.
5. Confirm no new MemBase reconciliation mutation was introduced to close the findings (only the DELIB-2508 DA record via the governed approval path).

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
