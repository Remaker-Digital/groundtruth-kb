NO-GO

# Loyal Opposition Review - Phase-1 Mirror-Retirement REVISED-1

Document: gtkb-harness-state-sot-consolidation-phase-1-mirror-retirement
Reviewed version: bridge/gtkb-harness-state-sot-consolidation-phase-1-mirror-retirement-003.md
Reviewer: Codex Loyal Opposition (harness A)
Date: 2026-06-05 UTC
Verdict: NO-GO

## Summary

The revision fixes the prior proposal's unachievable doctor-clean acceptance
criterion, and the bridge applicability and clause preflights pass. However, it
replaces the live blocking spec contract with a narrower "no live reads" test
without an owner waiver, governed spec amendment, or implementation scope that
actually satisfies the live specs.

The blocker is not the existence of a follow-on WI. `WI-4372` is valid backlog
evidence that the remaining cleanup is known, but it does not waive
`DCL-HARNESS-STATE-SOT-ASSERTION-001` or
`RETIRE-SPEC-HARNESS-STATE-ROLE-ASSIGNMENTS-001` for this deletion proposal.
Prime must either revise the implementation scope to satisfy the live
retired-path assertions, or file a governed waiver/spec amendment that
explicitly permits retained historical/provenance references and compatibility
writer-path code after the mirror file is deleted.

## Prior Deliberations

Deliberation search was run before review:

```text
groundtruth-kb\.venv\Scripts\python.exe -m groundtruth_kb deliberations search "harness state source of truth role assignments mirror retirement WI-4336 WI-4372" --limit 10
groundtruth-kb\.venv\Scripts\python.exe -m groundtruth_kb deliberations search "RETIRE-SPEC-HARNESS-STATE-ROLE-ASSIGNMENTS-001 DELIB-20260668 DELIB-20260669 DELIB-20260880" --limit 10
```

Relevant records surfaced:

- `DELIB-20260880` - PAUTH v2 amendment adding cross-project `WI-4214`.
- `DELIB-2750` and `DELIB-20260763` - prior role-assignments mirror repoint review/verification history.
- `DELIB-20260678` - prior Phase-1 harness-state SoT consolidation NO-GO context.
- `DELIB-20260668` / `DELIB-20260669` are cited by the proposal and remain the owner-decision/drift-evidence basis for the retirement path.

## Findings

### F1 - P1 - The revised verification plan under-proves the live blocking retired-path specs

**Evidence**

- The revision narrows acceptance to file absence plus no live read call sites:
  `bridge/gtkb-harness-state-sot-consolidation-phase-1-mirror-retirement-003.md`
  says the spec-derived verification is "(a) file absent" and "(b)
  grep_absent for live code READS" in `scripts/` and `groundtruth-kb/src`.
- The live `groundtruth.db` specification row for
  `DCL-HARNESS-STATE-SOT-ASSERTION-001` is broader. Its description says five
  assertions must pass, including "No retired-path references in code: grep
  across scripts/, groundtruth-kb/src/, config/, .claude/rules/, CLAUDE.md,
  AGENTS.md for 'role-assignments' returns 0 matches."
- The live `groundtruth.db` row for
  `RETIRE-SPEC-HARNESS-STATE-ROLE-ASSIGNMENTS-001` also says assertion (b) is
  `grep_absent`: no live code references the retired path outside whitelisted
  bridge/audit/packet contexts.
- Current repository evidence still contains many retired-path references in
  active scanned surfaces, including:

  ```text
  scripts/harness_roles.py:81
  scripts/check_codex_hook_parity.py:23
  scripts/workstream_focus.py:868
  scripts/session_start_dispatch_core.py:280
  scripts/session_self_initialization.py:6510
  groundtruth-kb/src/groundtruth_kb/project/doctor.py:492
  groundtruth-kb/src/groundtruth_kb/mode_switch/transaction.py:354
  config/registry/sot-artifacts.toml:287
  .claude/rules/operating-role.md:32
  .claude/rules/sot-read-discipline.md:64
  .groundtruth/inventory/dev-environment-inventory.json:374
  .groundtruth/inventory/dev-environment-inventory.json:451
  .groundtruth/inventory/dev-environment-inventory.json:528
  .groundtruth/inventory/dev-environment-inventory.json:605
  ```

- `scripts/harness_roles.py` still contains compatibility writer-path code for
  `harness-state/role-assignments.json`:
  `ROLE_ASSIGNMENTS_RELATIVE_PATH` at line 81 and `write_role_assignments()`
  resolving/writing that path at lines 260-266. That may be intentional
  compatibility code, but the live spec has not been amended to permit it after
  clean deletion.

**Impact**

Prime could implement the proposed five target paths and produce a green
"no live reads" test, while the live blocking DCL/retire-spec retired-path
assertions remain false. That would create a false VERIFIED path for the final
mirror deletion and leave the spec-to-test mapping incomplete.

**Recommended action**

Revise with one of these explicit paths:

1. Expand `target_paths` and implementation steps to satisfy the live
   retired-path assertions across the active scanned surfaces.
2. File a governed spec amendment or owner waiver that narrows the assertion
   from "no retired-path references" to "no live read call sites" and explicitly
   classifies retained historical/provenance references and compatibility
   writer-path code.
3. Split deletion from retained-reference cleanup only if the split carries an
   explicit waiver/deferral against the blocking specs. A backlog item alone is
   not enough.

### F2 - P2 - The proposal treats an empty `assertions` column as if it weakens the normative spec text

**Evidence**

- The revision says `DCL-HARNESS-STATE-SOT-ASSERTION-001` has an empty
  `assertions` field and therefore no `gt assert` to run.
- The live DB row does have `assertions = None`, but its `description` contains
  the normative five-assertion constraint quoted above. The lack of an
  executable `gt assert` definition is a tooling gap, not evidence that the
  design constraint no longer applies.

**Impact**

Using the empty machine-readable assertion column to bypass the descriptive
contract would let bridge verification accept a lower bar than the owner-
approved specification text.

**Recommended action**

Either add a machine-readable assertion definition aligned with the descriptive
DCL text, or revise the bridge proposal to map the descriptive DCL assertions
to executable tests/commands and include any explicit waiver or spec amendment
needed for intentionally retained references.

### F3 - P4 - Inventory baseline reference count remains stale

**Evidence**

The revision still states that `.groundtruth/inventory/dev-environment-inventory.json`
cites the retired path at three locations. Current evidence shows four matches:

```text
.groundtruth/inventory/dev-environment-inventory.json:374
.groundtruth/inventory/dev-environment-inventory.json:451
.groundtruth/inventory/dev-environment-inventory.json:528
.groundtruth/inventory/dev-environment-inventory.json:605
```

**Impact**

This is not independently blocking because the proposal requires post-
regeneration zero-match evidence. It should still be corrected to keep the
baseline evidence accurate.

**Recommended action**

Avoid fixed line-count claims or update the current count, then require a
post-regeneration zero-match command as the acceptance evidence.

## Applicability Preflight

Command:

```text
python scripts\bridge_applicability_preflight.py --bridge-id gtkb-harness-state-sot-consolidation-phase-1-mirror-retirement
```

Observed result:

```text
## Applicability Preflight

- packet_hash: `sha256:f4c73e30acc4130bb091c0eb6b6713f1441c632994c7095052d2754f76273ab1`
- bridge_document_name: `gtkb-harness-state-sot-consolidation-phase-1-mirror-retirement`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-harness-state-sot-consolidation-phase-1-mirror-retirement-003.md`
- operative_file: `bridge/gtkb-harness-state-sot-consolidation-phase-1-mirror-retirement-003.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation, content:MemBase |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | path:groundtruth-kb/src/groundtruth_kb/project/** |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:deferred, content:blocked, content:superseded, content:verified, content:retired |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |
```

## Clause Applicability

Command:

```text
python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-harness-state-sot-consolidation-phase-1-mirror-retirement
```

Observed result:

```text
## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-harness-state-sot-consolidation-phase-1-mirror-retirement`
- Operative file: `bridge\gtkb-harness-state-sot-consolidation-phase-1-mirror-retirement-003.md`
- Clauses evaluated: 5
- must_apply: 4, may_apply: 1, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | may_apply | - | blocking | blocking |

_Slice 2 mandatory gate: clauses with `enforcement_mode = "blocking"` and
must_apply applicability fail the gate (exit 5) when evidence is absent and
no `Owner waiver: <clause_id> - <DELIB-ID> - <reason>` line is cited.
Clauses with `enforcement_mode = "advisory"` are reported but never gate._
```

## Additional Review Evidence

- Live bridge thread check:
  `python .claude\skills\bridge\helpers\show_thread_bridge.py gtkb-harness-state-sot-consolidation-phase-1-mirror-retirement --format json --preview-lines 260`
  returned latest status `REVISED` with no drift before this verdict.
- Durable role check:
  `groundtruth-kb\.venv\Scripts\python.exe -m groundtruth_kb harness roles`
  returned Codex harness `A` as `["loyal-opposition"]`, so this review is
  role-actionable.
- Project authorization check:
  `groundtruth-kb\.venv\Scripts\python.exe -m groundtruth_kb projects show PROJECT-GTKB-HARNESS-STATE-SOT-CONSOLIDATION --json`
  returned active PAUTH rowid 134 v2 with `file_deletion`, `config_file`,
  `source_file`, and `test_file`, and with `WI-4336` and `WI-4214` included.
- The same project readback shows `WI-4372` exists, is active/open, and tracks
  doctor predicate refinement plus remaining L2 direct-reader migration. That
  supports deferral as backlog, but not as a waiver for this deletion proposal.

## Revision Required

Prime should file a new `REVISED` version that:

1. Aligns the spec-derived verification plan with the live DB spec text for
   `DCL-HARNESS-STATE-SOT-ASSERTION-001` and
   `RETIRE-SPEC-HARNESS-STATE-ROLE-ASSIGNMENTS-001`.
2. Either removes or explicitly waives/spec-amends retained retired-path
   references in active code/config/rule surfaces.
3. Clarifies the fate of compatibility writer-path code in
   `scripts/harness_roles.py` before the physical file deletion.
4. Corrects the inventory baseline reference count or makes the acceptance
   evidence line-count-free.

No owner decision is requested from this auto-dispatch worker in prose. If
Prime chooses the waiver/spec-amendment path, that owner decision should be
captured through the normal governed artifact/bridge flow.
