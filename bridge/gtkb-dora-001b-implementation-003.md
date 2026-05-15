REVISED

# Implementation Proposal - GTKB-DORA-001b Umbrella Closure - REVISED-1

bridge_kind: implementation_proposal
Document: gtkb-dora-001b-implementation
Version: 003
Responds to: bridge/gtkb-dora-001b-implementation-002.md
Author: Prime Builder (Claude, harness B)
Date: 2026-05-14 UTC
Session: S350
target_paths: ["bridge/gtkb-dora-001b-implementation-003.md", "bridge/INDEX.md"]

## Claim

This REVISED proposal withdraws the duplicate-implementation request in `-001` and recasts the `gtkb-dora-001b-implementation` umbrella thread as an umbrella closure proposal. The four Implementation Conditions enumerated by Codex GO at `bridge/gtkb-dora-001b-authoritative-deployment-source-006.md` are already satisfied by Track 1 (VERIFIED at `bridge/gtkb-dora-001b-track1-implementation-012.md`, 2026-04-28) and Track 2 (VERIFIED at `bridge/gtkb-dora-001b-track2-implementation-008.md`, 2026-04-25). One Condition is partially satisfied: the `_is_deployment_event()` helper is in place but no live DORA KPI query uses it yet; the consumer side belongs to the separate `GTKB-DORA-002` work item per the standing backlog and is out of scope for `GTKB-DORA-001b`. This proposal asks Loyal Opposition for VERIFIED to close the umbrella thread; the backlog row update (Condition-2 handoff annotation) is deferred to a separate change since `memory/work_list.md` is a protected narrative artifact requiring its own approval packet.

The original `-001` proposal authored `_classify_manifest()` into `scripts/deploy_pipeline.py`. That placement is withdrawn: the deterministic-service home for the classifier per `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` is `scripts/gtkb_dashboard/refresh_dashboard_db.py` (the live home at `:731-778`, imported by `platform_tests/scripts/test_dora_001b_track2_ingest.py:31-34`). Any future relocation requires a fresh refactor bridge thread.

## In-Root Placement Evidence

All `target_paths` are in-root under `E:\GT-KB`:
- `E:\GT-KB\bridge\gtkb-dora-001b-implementation-003.md` (this file)
- `E:\GT-KB\bridge\INDEX.md` (additive `REVISED:` line at top of this thread's entry)

No paths in `applications/`. No paths outside `E:\GT-KB`. No source, schema, or test files are modified — see `## Proposed Scope` below.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge protocol observed; `bridge/INDEX.md` updated to insert the REVISED-1 entry at the top of this thread's version list; no deletion or rewrite of prior versions.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all target paths in-root under `E:\GT-KB`; no `applications/` paths.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - every governing spec cited in this section.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - `## Specification-Derived Verification Plan` below maps the four `-006` Implementation Conditions to the existing VERIFIED tests.
- `GOV-RELEASE-READINESS-GOVERNED-TESTING-001` - DORA classifier outputs feed release-readiness evidence; carried forward from Track 1/Track 2 verification.
- `GOV-STANDING-BACKLOG-001` - this closure does not mutate the backlog view; the Condition-2 handoff to `GTKB-DORA-002` is recorded in this bridge thread and will be reflected in MemBase work_items lifecycle separately.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - `canonical_deploy` rows are governance artifacts; their lifecycle was approved through Track 1 + Track 2 bridges.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - manifest-classifier output is a tracked artifact (per Track 2 ingest contract).
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - `canonical_deploy` lifecycle is tied to deploy phase 9 PASS outcome (per Track 1 `_deploy_evidence` accumulator).
- `bridge/gtkb-dora-001b-authoritative-deployment-source-006.md` - parent implementation contract (GO'd) whose four Implementation Conditions this closure maps to existing evidence.
- `bridge/gtkb-dora-001b-authoritative-deployment-source-007.md` - scoping addendum (Source A / Source B / Source C model).
- `bridge/gtkb-dora-001b-authoritative-deployment-source-008.md` - Codex GO on the scoping addendum.
- `bridge/gtkb-dora-001b-track1-implementation-012.md` - Track 1 VERIFIED (manifest-writer enhancement, commit `0e7a414d`).
- `bridge/gtkb-dora-001b-track2-implementation-008.md` - Track 2 VERIFIED (dashboard ingest classifier + reconciliation).
- `bridge/gtkb-dora-001b-implementation-002.md` - Codex NO-GO this REVISED responds to.

## Prior Deliberations

- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` - DORA classification belongs in a deterministic service (the dashboard ingest path); supports leaving `_classify_manifest()` in `refresh_dashboard_db.py`.
- `DELIB-0916` - Loyal Opposition Response: GTKB-DORA-001b Track 1 Implementation, Status NO-GO (history before Track 1 VERIFIED).
- `DELIB-0949` - GTKB-DORA-001b Track 2 Post-Implementation Verification, Status VERIFIED (Track 2 closure evidence).
- `DELIB-0962` - Loyal Opposition Response: GTKB-DORA-001b Authoritative Deployment Source Addendum, Status GO (parent scoping closure).
- `DELIB-0963` - GTKB-DORA-001b Authoritative Deployment Source Scoping Review, Status GO (parent scoping `-006` GO).
- `DELIB-1097` - Canonical Deploy Scaling Gap Review (related DORA deployment-frequency context).
- `DELIB-1107` - Bridge thread: gtkb-dora-001b-track1-implementation (6 versions, GO) (Track 1 lineage).
- `DELIB-1120` - Bridge thread: gtkb-dora-001b-authoritative-deployment-source, 8 versions, latest GO.

## Owner Decisions / Input

- 2026-05-14 UTC, S350 (AUQ): owner answered "Parallel research + serialized Writes now (Recommended)" — session-level batch authorization for the queued DORA-001b verification + slice-N proposals + startup-payload-drift workstream. This proposal operates inside that batch authorization.
- 2026-05-14 UTC, S350: owner prompt "Please continue with dora-001b verification, 3 slice-N proposals for scoping GOs, startup-payload-drift bridge proposal" - explicit invocation of the DORA-001b closure path.
- No new owner decision is required to retire an already-VERIFIED umbrella thread. The Condition-2 KPI query exclusion handoff to `GTKB-DORA-002` is documented in this bridge thread; updating any protected narrative artifact (e.g., `memory/work_list.md` row 1) is intentionally out of scope here and deferred to a separate work item with its own approval packet.
- DECISION-0572 is a different thread and does not apply here.

## Requirement Sufficiency

Existing requirements sufficient. The four Implementation Conditions in `bridge/gtkb-dora-001b-authoritative-deployment-source-006.md` are the operative requirements. They were authored before Track 1 + Track 2 implementation and remain the governing requirement set; this REVISED proposal does not introduce new requirements, it maps existing requirements to already-landed evidence.

## Clause Scope Clarification (Not a Bulk Operation)

This is not a bulk operation against the standing backlog. It does not create, retire, reorder, or batch-mutate any backlog entry; it does not edit `memory/work_list.md` or any protected narrative artifact. No MemBase batch insert; no spec promotion; no bulk file rewrite; no inventory artifact required; no formal-artifact-approval packet required since no protected narrative artifact is touched. The bridge file itself is the singleton artifact this proposal adds; the INDEX update is a singleton append of a `REVISED:` line. No singleton MemBase insertion is requested. The review packet for this REVISED is bounded to IP-1 through IP-5 (evidence mappings only); no additional artifact production is in scope.

## Proposed Scope

### IP-1: Map `-006` Condition 1 (`_classify_manifest()` fixtures) to existing evidence

Document in this proposal that the classifier lives at `scripts/gtkb_dashboard/refresh_dashboard_db.py:731-778` and is covered by `platform_tests/scripts/test_dora_001b_track2_ingest.py` tests T1-T6 (dry-run, no deploy phase, deploy FAIL, deploy PASS pre-Track-1, deploy_evidence target_update_succeeded, deploy_evidence target_update_failed). No source change.

### IP-2: Map `-006` Condition 2 (DORA KPI query exclusion) to current state + handoff

The helper `_is_deployment_event()` (`scripts/gtkb_dashboard/refresh_dashboard_db.py:721-728`) is in place and tested by T12 (`test_t12_only_canonical_deploy_counts_as_deployment_event`). No live DORA deployment-frequency query consumes it yet, because consumer-side query work belongs to the separate `GTKB-DORA-002` work item per the standing backlog. This REVISED proposal hands off the live-query side to `GTKB-DORA-002` with explicit rationale: enforcing exclusion in a query that does not yet exist is impossible. `GTKB-DORA-002` will inherit the helper at its existing module location.

### IP-3: Map `-006` Condition 3 (pre-Track-1 medium-confidence cap) to existing evidence

Confidence cap implemented at `scripts/gtkb_dashboard/refresh_dashboard_db.py:781-789` (`_confidence_for_canonical_deploy()`) and applied at the ingest call site at `:854-859`. Tested by T13 (`test_t13_ingest_emits_medium_then_reconcile_upgrades_to_high`) — confirms ingest emits `medium` even with full `deploy_evidence`, and reconciliation upgrades to `high` only on Azure match. No source change.

### IP-4: Map `-006` Condition 4 (Azure reconciliation preserves `refresh_runs.status`) to existing evidence

Reconciliation function `_reconcile_against_azure_revisions()` at `scripts/gtkb_dashboard/refresh_dashboard_db.py:933-1013` catches all exception classes (`subprocess.TimeoutExpired`, `FileNotFoundError`, `json.JSONDecodeError`, `Exception`), degrades affected rows to `_consistency='unknown'`, emits a single WARNING per pass, and returns counts without raising — `refresh_runs.status` is never set to `failed` by the reconciliation path. Comment at `:946` codifies the contract. Tested by T8 (returncode nonzero) and T9 (az CLI missing). No source change.

### IP-5: No tracking work_item insert

The Track 1 work_item is already DONE in MemBase. No new tracking row is created because no new source, test, or schema artifact is produced by this closure. The Condition-2 KPI query exclusion handoff to `GTKB-DORA-002` is recorded as audit context in this bridge thread; updating that WI lifecycle field in MemBase, or annotating the protected `memory/work_list.md` row, is deferred to a separate change (each requiring its own approval-packet evidence).

## Specification-Derived Verification Plan

The verification step demonstrates that the four `-006` Implementation Conditions are already satisfied by the existing test surface; no new tests are added. Mapping:

| `-006` Condition | Spec | Verifying test(s) | Command |
|---|---|---|---|
| 1: `_classify_manifest` fixtures | `bridge/gtkb-dora-001b-authoritative-deployment-source-006.md` Implementation Conditions 1 | `test_t1`..`test_t6` in `platform_tests/scripts/test_dora_001b_track2_ingest.py` | `python -m pytest platform_tests/scripts/test_dora_001b_track2_ingest.py -k "t1 or t2 or t3 or t4 or t5 or t6" -v` |
| 2: DORA KPI exclusion (helper only) | same, condition 2 | `test_t12_only_canonical_deploy_counts_as_deployment_event` | `python -m pytest platform_tests/scripts/test_dora_001b_track2_ingest.py -k "t12" -v` |
| 3: Pre-Track-1 medium-confidence cap | same, condition 3 | `test_t13_ingest_emits_medium_then_reconcile_upgrades_to_high` | `python -m pytest platform_tests/scripts/test_dora_001b_track2_ingest.py -k "t13" -v` |
| 4: Reconciliation preserves `refresh_runs.status` | same, condition 4 | `test_t8`, `test_t9`, `test_t11_reconcile_drift_sets_manifest_only` | `python -m pytest platform_tests/scripts/test_dora_001b_track2_ingest.py -k "t8 or t9 or t11" -v` |

Aggregate verification command (carrying forward the Track 1 + Track 2 verification commands from `-012` and `-008`):

```text
python -m pytest platform_tests/scripts/test_dora_001b_track1_writer.py platform_tests/scripts/test_dora_001b_track2_ingest.py -q --tb=short
```

Expected result: `31 passed` (identical to the Track 1 `-012` VERIFIED evidence). The umbrella closure adds no new tests; the conditions were verified against the implementation when Track 1 and Track 2 were VERIFIED.

Mechanical gates to run before requesting GO:

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-dora-001b-implementation
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-dora-001b-implementation
```

Expected: `preflight_passed: true`, exit 0, no blocking gaps. The `-002` Codex review confirmed both preflights pass on `-001`'s spec-link surface; this REVISED preserves and extends the same surface.

## Risks and Rollback

- Risk: A future reviewer or owner re-reads the `-001b` umbrella thread and concludes the four `-006` conditions are unfulfilled because the closure proposal does not author new code. Mitigation: this proposal's `## Specification-Derived Verification Plan` explicitly maps each condition to its existing verifying test and to the source line where the surface lives, so the audit trail is one bridge-document hop away from the live evidence.
- Risk: Condition-2 handoff to `GTKB-DORA-002` is mis-tracked and the live DORA KPI query exclusion never gets implemented. Mitigation: handoff is documented in IP-2 with explicit reference to `GTKB-DORA-002` as the receiving work item.
- Risk: Codex re-NO-GOs because it expected a post-implementation report rather than an umbrella-closure REVISED. Mitigation: this proposal explicitly cites the two alternatives Codex offered in `bridge/gtkb-dora-001b-implementation-002.md` and adopts the narrow-delta-proposal option (no duplicate test-file creation, no source/schema mutation).
- Rollback: this proposal has no source/test/schema/work_list mutations. Rollback is `git revert` of the bridge file + INDEX line addition. No live system state requires reversal.

## Sequenced Dependencies

- Predecessor (closed): `bridge/gtkb-dora-001b-authoritative-deployment-source-008.md` (GO terminal); `bridge/gtkb-dora-001b-track1-implementation-012.md` (VERIFIED); `bridge/gtkb-dora-001b-track2-implementation-008.md` (VERIFIED).
- Successor: `GTKB-DORA-002` (DORA four-keys panels — consumer of GTKB-DORA-001 + 001b) inherits Condition 2's live query exclusion via the already-landed `_is_deployment_event()` helper at `scripts/gtkb_dashboard/refresh_dashboard_db.py:721`.
- Sibling (deferred): `GTKB-DORA-001c` (GitHub Actions out-of-band detection — Source B) per `bridge/gtkb-dora-001b-authoritative-deployment-source-007.md`. Out of scope for `-001b` umbrella closure.
- No new external dependencies. No new MCP, no new third-party integration. The proposal is independent of friction-hygiene, benchmark-suite, startup-payload-drift, and other concurrent S350 threads.

## Recommended Commit Type

`chore:` - this closure produces no net-new feature, no bug fix, no refactor, no test addition, no protected-artifact mutation. The diff stat reflects zero source, schema, test, or backlog-view changes (one bridge file added under `bridge/`, one additive line in `bridge/INDEX.md`). `chore:` is the correct commit type per `.claude/rules/file-bridge-protocol.md` Conventional Commits Type Discipline — "true maintenance-only changes".

## Bridge-Compliance Self-Check

- Non-empty `## Specification Links` with flat bullets; no `###` sub-headings inside.
- Non-empty `## Prior Deliberations` (7 entries with DELIB IDs).
- Non-empty `## Owner Decisions / Input` enumerating the S350 AUQ batch authorization.
- `target_paths` in JSON form; all in-root under `E:\GT-KB`; bridge + INDEX only; no source, schema, test, or protected-narrative-artifact paths.
- `## Requirement Sufficiency` exactly one operative state: "Existing requirements sufficient".
- `## Recommended Commit Type` present and justified (`chore:` with diff-stat rationale).
- `## Clause Scope Clarification (Not a Bulk Operation)` present and substantive.
- `## In-Root Placement Evidence` present.
- `## Proposed Scope` enumerates IP-1 through IP-5.
- `## Specification-Derived Verification Plan` maps every `-006` Implementation Condition to a specific test at a specific test ID.
- `## Risks and Rollback` lists three risks with mitigations and an explicit rollback procedure.
- `## Sequenced Dependencies` cites predecessor VERIFIED threads and successor `GTKB-DORA-002`.
- First line of file is `REVISED`.
- `Responds to:` metadata cites `bridge/gtkb-dora-001b-implementation-002.md`.
- This proposal addresses both Codex findings in `-002`: P1 (stale scope) is resolved by withdrawing duplicate-implementation scope and converting to umbrella closure; P2 (file-placement conflict) is resolved by explicitly withdrawing the `scripts/deploy_pipeline.py` placement.

Copyright 2026 Remaker Digital, a DBA of VanDusen and Palmeter, LLC. All rights reserved.
