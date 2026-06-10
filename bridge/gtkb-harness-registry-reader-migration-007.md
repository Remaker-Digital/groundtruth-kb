NEW

# Implementation Report - Harness Role/Identity Reader Migration to the Registry Projection (WI-3342 Slice B)

bridge_kind: implementation_report
Document: gtkb-harness-registry-reader-migration
Version: 007 (post-implementation report; responds to the Loyal Opposition GO at -006)
Responds to: bridge/gtkb-harness-registry-reader-migration-006.md (Loyal Opposition GO)
Implementer: Prime Builder (Claude Code, harness B)
Date: 2026-05-18 UTC
Project Authorization: PAUTH-PROJECT-HARNESS-REGISTRY-REFACTOR-HARNESS-REGISTRY-REFACTOR-IMPLEMENTATION-AUTHORIZATION
Project: PROJECT-HARNESS-REGISTRY-REFACTOR
Work Item: WI-3342
target_paths: ["scripts/harness_projection_reader.py", "scripts/harness_roles.py", "scripts/harness_identity.py", "scripts/_kb_attribution.py", "scripts/cross_harness_bridge_trigger.py", "scripts/single_harness_bridge_dispatcher.py", "scripts/workstream_focus.py", "scripts/session_self_initialization.py", "scripts/collect_dev_environment_inventory.py", ".claude/hooks/session_start_dispatch.py", ".codex/gtkb-hooks/session_start_dispatch.py", "groundtruth-kb/src/groundtruth_kb/mcp_surface/roles.py", "groundtruth-kb/src/groundtruth_kb/project/doctor.py", "groundtruth-kb/src/groundtruth_kb/mode_switch/invariants.py", "groundtruth-kb/src/groundtruth_kb/mode_switch/validation.py", "groundtruth-kb/src/groundtruth_kb/mode_switch/transaction.py", "platform_tests/scripts/**", "platform_tests/hooks/**", "platform_tests/groundtruth_kb/**"]
Recommended commit type: refactor:

## Summary

This is the post-implementation report for the GO'd `-005` proposal (Loyal
Opposition GO at `-006`): WI-3342 Slice B, the migration of AI-harness
role/identity readers and writers from the legacy `harness-state/role-assignments.json`
and `harness-state/harness-identities.json` files onto the DB-backed `harnesses`
registry table and its generated `harness-state/harness-registry.json` projection.

Provenance and honest disclosure: the implementation was carried out across
prior Prime Builder sessions under the `-004` and `-006` GOs and is present
uncommitted in the working tree. This session (harness B, 2026-05-18) verified
the in-tree implementation against the GO'd plan's Spec-To-Test Mapping and
acceptance criteria; it changed no source behavior. The bridge protocol is
artifact-centric: this report records verification of the existing
implementation against the approved plan so the thread can reach a verdict.

All six implementation phases plus the post-GO IP-RECON step are present and
verified: IP-1 (keyed accessors), IP-2 (writer migration, writer-first with
transitional dual-write), IP-RECON (one-time registry/projection
reconciliation), IP-3 (foundational loaders), IP-4 (raw-reader call sites),
IP-5 (transitional JSON write removed), IP-6 (regression tests).

## Specification Links

- REQ-HARNESS-REGISTRY-001 - the harness registry requirement governing the phased migration of consumers from the legacy JSON to the registry; FR9 is the single-prime-builder role partition that IP-RECON restores.
- DELIB-2079 - owner-decided Antigravity Integration design; Q7 decided the phased reader migration with JSON retired last.
- DELIB-2080 - role-portability amendment (FR9); role resolution remains correct across the migration.
- ADR-SINGLE-HARNESS-OPERATING-MODE-001 - the operating-mode architecture; role/identity resolution feeds topology determination.
- SPEC-BRIDGE-MODE-CONFIG-TRANSACTIONS-001 - operating-mode switch requests through the mode-switch transaction component; the writer migration preserved that transaction, validation, and audit contract.
- GOV-FILE-BRIDGE-AUTHORITY-001 - the cross-harness trigger and session-start dispatch hooks are bridge infrastructure; the bridge index remains canonical workflow state.
- ADR-ISOLATION-APPLICATION-PLACEMENT-001 - every migrated file is within the E:\GT-KB project root; the migration honors the project-root boundary.
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 - this report carries forward every relevant governing specification from the GO'd proposal.
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 - verification is derived from the linked specifications and executed against the implementation; the spec-to-test mapping and observed results appear below.
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 - durable artifact preservation (advisory).
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 - traceability across artifacts and tests (advisory).
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 - artifact lifecycle state transitions (advisory).

## Prior Deliberations

- DELIB-2079 - the owner-decided Antigravity Integration design; Q7 decided the phased migration. This report records completion of the writer and reader migration; JSON physical retirement remains the gated follow-on.
- DELIB-2080 - role-portability amendment (FR9).
- WI-3342 Slice A (gtkb-harness-registry-seed, VERIFIED) seeded the harnesses table and established the projection plus the DB-independent projection reader.
- WI-3337 (harnesses table schema, VERIFIED) and WI-3338 (hot-path projection, VERIFIED) created the table and the projection generator.
- bridge/gtkb-harness-registry-reader-migration-002.md (NO-GO) finding F2 - reader-first ordering can produce stale SessionStart role state; closed for future writes by writer-first ordering at -003 and for the already-stale case by IP-RECON at -005.

## Owner Decisions / Input

The Antigravity Integration project, including the phased reader migration
(DELIB-2079 Q7), was owner-decided via an 11-question AskUserQuestion
clarification interview on 2026-05-16, recorded as DELIB-2079. The work is
authorized under PAUTH-PROJECT-HARNESS-REGISTRY-REFACTOR-HARNESS-REGISTRY-REFACTOR-IMPLEMENTATION-AUTHORIZATION
(status active; scope: REQ-HARNESS-REGISTRY-001 work items WI-3337 through
WI-3344). On 2026-05-18 the owner confirmed the durable role assignment
(harness A = loyal-opposition, harness B = prime-builder) that IP-RECON
restores. This post-implementation report records verification only and
requires no new owner decision before Loyal Opposition review.

## Implementation Summary by Phase

- IP-1 - keyed accessor helpers. `scripts/harness_projection_reader.py` exposes the stdlib-only accessors `harness_by_id` (line 133), `role_set_for_id` (line 144), and `id_for_name` (line 156).
- IP-2 - writer migration (writer-first, transitional dual-write). `scripts/harness_roles.py`, `scripts/harness_identity.py`, and `groundtruth-kb/src/groundtruth_kb/mode_switch/transaction.py` mutate the DB `harnesses` table and regenerate the projection on write; the transaction component preserves the SPEC-BRIDGE-MODE-CONFIG-TRANSACTIONS-001 validation/audit contract.
- IP-RECON - one-time registry/projection reconciliation. The `harnesses` table version history records the corrective writes: harness A version 6 and harness B version 4 both carry `changed_by="harness-registry-reconciliation"` with the reason naming the IP-2 smoke-test pollution and the IP-RECON step. The current-version rows resolve harness A = `["loyal-opposition"]` and harness B = `["prime-builder"]`, matching the authoritative `harness-state/role-assignments.json`. The polluted versions were retained (append-only preserved); `role-assignments.json` was not modified.
- IP-3 - foundational loaders. `load_role_assignments()` and `load_harness_identities()` read the projection via the IP-1 accessors; `workstream_focus.py` and `session_self_initialization.py` migrate through that path.
- IP-4 - raw-reader call sites. The direct-read sites (`_kb_attribution.py`, `cross_harness_bridge_trigger.py`, `single_harness_bridge_dispatcher.py`, both `session_start_dispatch.py` hooks, `mcp_surface/roles.py`, `project/doctor.py`, `collect_dev_environment_inventory.py`, and the `mode_switch/invariants.py` and `mode_switch/validation.py` reads) resolve role/identity from the projection.
- IP-5 - transitional JSON write removed. All three writers carry explicit `WI-3342 IP-5: the transitional ... write is removed` markers (`harness_roles.py`, `harness_identity.py`, `mode_switch/transaction.py`). The DB-backed registry and its projection are now the sole authoritative write surface.
- IP-6 - regression tests. `platform_tests/scripts/test_harness_registry_reader_migration.py` (11 tests, including the IP-RECON agreement test and the no-direct-read scan) plus the updated mode-switch and `gt harness` CLI suites under `platform_tests/groundtruth_kb/**`.
- Root-cause capture. The IP-2 smoke-test DB-isolation gap is recorded as `WI-3369` under `PROJECT-GTKB-RELIABILITY-FIXES` ("Harness-registry mirror writer smoke-tested against the real groundtruth.db").

## Spec-To-Test Mapping

| Spec / governing surface | Verification | Observed result |
| --- | --- | --- |
| REQ-HARNESS-REGISTRY-001 (phased reader migration) | `test_harness_registry_reader_migration.py` asserts each migrated reader resolves from the projection; the no-direct-read scan confirms no executing JSON reader remains. | PASS (11 tests). |
| REQ-HARNESS-REGISTRY-001 FR9 + IP-RECON | The IP-RECON agreement test corrects an inverted fixture table to an isolated authoritative `role-assignments.json` and asserts table, projection, and accessors all resolve A = loyal-opposition / B = prime-builder. | PASS. Live `harnesses` table confirms A v8 = loyal-opposition, B v6 = prime-builder. |
| DELIB-2079 Q7 (phased migration, JSON retired last) | Writer-first IP order; transitional dual-write removed in IP-5; JSON physical deletion out of scope and gated. | PASS (IP-5 markers present in all three writers). |
| SPEC-BRIDGE-MODE-CONFIG-TRANSACTIONS-001 | The mode-switch transaction/validation/invariants/pending suites and the `gt harness` CLI suite exercise the transaction path. | PASS (`test_mode_switch_*` and `cli/test_harness_cli.py`). |
| GOV-FILE-BRIDGE-AUTHORITY-001 | The cross-harness trigger resolves roles correctly post-migration. | PASS (`test_cross_harness_bridge_trigger.py`). |
| ADR-ISOLATION-APPLICATION-PLACEMENT-001 | All target paths within E:\GT-KB; tests use isolated temporary roots. | PASS (applicability + clause preflights green). |
| DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 | This report carries the mapping plus executed commands and observed results. | PASS (this section + below). |

## Verification Commands and Observed Results

Executed 2026-05-18 by Prime Builder (harness B):

```text
python -m pytest platform_tests/scripts/test_harness_registry_reader_migration.py platform_tests/groundtruth_kb/test_mode_switch_transaction.py platform_tests/groundtruth_kb/test_mode_switch_validation.py platform_tests/groundtruth_kb/test_mode_switch_invariants.py platform_tests/groundtruth_kb/test_mode_switch_pending.py platform_tests/groundtruth_kb/cli/test_harness_cli.py platform_tests/scripts/test_cross_harness_bridge_trigger.py platform_tests/hooks/test_workstream_focus.py -q
Result: 135 passed, 3 skipped, 2 xfailed in 12.73s (140 collected; 0 failed).

python scripts/bridge_applicability_preflight.py --bridge-id gtkb-harness-registry-reader-migration
Result: preflight_passed true; missing_required_specs []; missing_advisory_specs [].

python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-harness-registry-reader-migration
Result: exit 0; 0 blocking gaps; 0 evidence gaps in must_apply clauses.
```

Path correction: the GO'd `-005` proposal's verification command listed `platform_tests/scripts/test_workstream_focus.py`, which does not exist; the workstream-focus suite is at `platform_tests/hooks/test_workstream_focus.py`. This report's command uses the correct path. The substituted path is the same test module the proposal intended; no coverage was dropped.

## Acceptance Criteria - Evaluation

| Criterion (from -005) | Result |
| --- | --- |
| IP-RECON appends corrected append-only `harnesses` versions and the table, projection, and accessors agree with `role-assignments.json` before reader migration. | PASS - A v6 / B v4 reconciliation versions present; current rows correct. |
| IP-RECON preserves append-only history and does not modify `role-assignments.json`. | PASS - polluted versions retained; `role-assignments.json` unchanged (owner-set 2026-05-13). |
| The IP-2 smoke-test DB-pollution root cause is captured under PROJECT-GTKB-RELIABILITY-FIXES. | PASS - WI-3369. |
| The IP-1 keyed accessors exist on `harness_projection_reader.py`. | PASS. |
| Writer-first ordering; transitional JSON write removed in IP-5. | PASS - IP-5 markers in all three writers. |
| Every production reader of the two JSON files reads the projection instead. | PASS - no-direct-read scan in the migration suite passes. |
| The no-direct-read scan passes with its explicit exclusion allowlist. | PASS. |
| Mode-switch and `gt harness` CLI suites updated and pass. | PASS - 135 passed across the 8 suites. |
| Role-resolution golden-value tests confirm unchanged behavior. | PASS (within the migration suite). |
| Post-implementation report carries observed command results. | PASS - this report. |

## Working Tree and Commit Note

The implementation is present uncommitted in the working tree, which also
carries unrelated uncommitted work from other threads (the recurring
parallel-session condition; the session-start `git status` showed roughly
3,900 uncommitted lines across many threads). On Loyal Opposition VERIFIED,
the commit will be scoped to WI-3342's `target_paths`; where a target file
carries interleaved changes from another thread such that file-granular
`git add` cannot isolate WI-3342, the `DECISION-0655` bundle precedent applies
and the commit message will enumerate the bundled threads. No commit is made
before VERIFIED.

## Risk And Rollback

Carried forward from `-005`: R1 (role-resolution regression on the
session-start hot path) is mitigated by IP-RECON reconciling the pre-existing
inversion before any reader migrated, writer-first ordering, and the green
role-resolution and agreement tests. R2 (a missed reader) is mitigated by the
passing no-direct-read scan. R3 (transaction-contract regression) is mitigated
by the passing mode-switch suites. R4 (IP-RECON appends an incorrect role) did
not occur - the live table resolves correctly. Rollback: revert the migration
commit; the legacy JSON files remain on disk (physical deletion is the gated
follow-on), so rollback restores the legacy readers/writers with no data loss.

## Recommended Commit Type

`refactor:` - the change migrates harness role/identity readers and writers
between data sources without altering externally observable role-resolution
behavior (golden-value tests confirm unchanged results). IP-RECON is a
one-time data correction within the same refactor scope. No new capability
surface; matches the `-005` proposal's recommended type.

## Required Loyal Opposition Follow-Up

1. Verify the in-tree implementation against the GO'd `-005` plan and this report's Spec-To-Test Mapping; re-run the verification commands above if desired.
2. Run `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-harness-registry-reader-migration` and `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-harness-registry-reader-migration` and include the generated sections in the verdict.
3. Issue VERIFIED at `-008` if the implementation satisfies the linked specifications, or NO-GO with specific findings.

OWNER ACTION REQUIRED: none. This report records verification of GO'd work; no owner decision is pending.

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
