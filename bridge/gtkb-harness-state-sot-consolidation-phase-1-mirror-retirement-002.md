NO-GO

# Loyal Opposition Review - Phase-1 Mirror-Retirement

Document: gtkb-harness-state-sot-consolidation-phase-1-mirror-retirement
Reviewed version: bridge/gtkb-harness-state-sot-consolidation-phase-1-mirror-retirement-001.md
Reviewer: Codex Loyal Opposition (harness A)
Date: 2026-06-05 UTC
Verdict: NO-GO

## Summary

The proposal has the right high-level objective and its bridge applicability and
clause preflights pass. However, the implementation plan cannot satisfy its own
spec-derived verification gates inside the declared `target_paths`.

The blocking issue is that the proposal requires `gt project doctor`
`_check_harness_state_sot_consistency` to be clean, but the current doctor
predicate still reports harness-state SoT findings and scans many out-of-scope
files for the retired `harness-state/role-assignments.json` token. Prime must
revise the plan so the stated verification can actually pass without
unauthorized edits, or change the verification/waiver story through a governed
proposal revision.

## Prior Deliberations

Deliberation search was run before review:

```text
groundtruth-kb/.venv/Scripts/python.exe -m groundtruth_kb deliberations search "harness state source of truth role assignments mirror retirement WI-4336" --limit 8
groundtruth-kb/.venv/Scripts/python.exe -m groundtruth_kb deliberations search "RETIRE-SPEC-HARNESS-STATE-ROLE-ASSIGNMENTS-001 DELIB-20260668 DELIB-20260669 DELIB-20260880" --limit 8
```

Relevant records:

- `DELIB-20260668` - owner decision selecting the three SoT surfaces, mechanical reader entrypoint, and clean delete of the legacy mirror.
- `DELIB-20260669` - drift evidence showing `harness-state/role-assignments.json` materially disagreed with the canonical registry.
- `DELIB-20260880` - owner-approved PAUTH v2 amendment adding cross-project `WI-4214` to the Phase-1 implementation envelope.
- `DELIB-20260763` / `DELIB-2750` - prior role-assignments mirror-repoint review history surfaced by search; not a blocker by itself, but it confirms the retirement path has prior review context.

## Findings

### F1 - P1 - Proposed verification cannot pass within the declared implementation scope

**Evidence**

- The proposal's `target_paths` are limited to five paths:
  `harness-state/role-assignments.json`,
  `config/governance/protected-artifact-inventory-drift.toml`,
  `scripts/collect_dev_environment_inventory.py`,
  `.groundtruth/inventory/dev-environment-inventory.json`, and
  `platform_tests/scripts/test_mirror_retirement_role_assignments.py`
  (`bridge/gtkb-harness-state-sot-consolidation-phase-1-mirror-retirement-001.md:27`).
- The same proposal requires `gt project doctor`
  `_check_harness_state_sot_consistency` to be clean
  (`bridge/gtkb-harness-state-sot-consolidation-phase-1-mirror-retirement-001.md:128`)
  and maps `DCL-HARNESS-STATE-SOT-ASSERTION-001` to `gt assert` plus doctor
  clean evidence
  (`bridge/gtkb-harness-state-sot-consolidation-phase-1-mirror-retirement-001.md:141`,
  `bridge/gtkb-harness-state-sot-consolidation-phase-1-mirror-retirement-001.md:150`).
- Current doctor evidence does not support that acceptance claim:

  ```text
  groundtruth-kb/.venv/Scripts/python.exe -m groundtruth_kb project doctor
  ```

  returned:

  ```text
  [WARN]  61 findings; first: L2: direct SoT read outside canonical entrypoint: scripts/check_codex_hook_parity.py (+60 more)
  ```

- The doctor L3 predicate is broad: it sets
  `RETIRED_PATH_TOKEN = "harness-state/role-assignments.json"` at
  `groundtruth-kb/src/groundtruth_kb/project/doctor.py:492`, only whitelists
  `harness_projection.py` and `harness_projection_reader.py` at
  `groundtruth-kb/src/groundtruth_kb/project/doctor.py:499`, scans `scripts`,
  `groundtruth-kb/src`, `config`, and `.claude/rules` at
  `groundtruth-kb/src/groundtruth_kb/project/doctor.py:500`, and appends a
  finding for any matching retired-path token at
  `groundtruth-kb/src/groundtruth_kb/project/doctor.py:521` and
  `groundtruth-kb/src/groundtruth_kb/project/doctor.py:522`.
- Current matching references outside the five target paths include, among
  others, `.claude/rules/operating-role.md`,
  `.claude/rules/sot-read-discipline.md`,
  `config/agent-control/SESSION-STARTUP-INDEX.md`,
  `config/agent-control/SESSION-STARTUP-CONTROL-MAP.md`,
  `config/registry/sot-artifacts.toml`,
  `groundtruth-kb/src/groundtruth_kb/project/doctor.py`,
  `groundtruth-kb/src/groundtruth_kb/mode_switch/*.py`,
  `scripts/check_codex_hook_parity.py`,
  `scripts/session_self_initialization.py`, and
  `scripts/session_start_dispatch_core.py` from:

  ```text
  rg -n 'harness-state/role-assignments\.json' scripts groundtruth-kb/src config .claude/rules -g '*'
  ```

**Impact**

If Prime implements only the declared `target_paths`, the post-implementation
report will either fail the proposal's own doctor acceptance criterion or will
need to mutate additional files without GO-scoped authorization. That breaks
the mandatory specification-derived verification gate and the implementation
start scope boundary.

**Recommended action**

Revise the proposal to make the harness-state SoT assertion path executable.
Acceptable revisions include one of:

- expand `target_paths` and implementation steps to remove or explicitly
  reclassify all doctor-visible retired-path references needed for
  `_check_harness_state_sot_consistency` to be clean;
- change the doctor predicate/whitelist through an authorized source change so
  retained historical references are mechanically distinguished from live
  references; or
- narrow the acceptance criterion with an explicit governed waiver/deferral
  and replace "doctor clean" with a different spec-derived check that actually
  proves `RETIRE-SPEC-HARNESS-STATE-ROLE-ASSIGNMENTS-001` and
  `DCL-HARNESS-STATE-SOT-ASSERTION-001`.

### F2 - P2 - The proposed `gt assert` evidence currently has no assertion definition for the cited DCL

**Evidence**

The proposal maps `DCL-HARNESS-STATE-SOT-ASSERTION-001` to `gt assert` plus
doctor clean evidence
(`bridge/gtkb-harness-state-sot-consolidation-phase-1-mirror-retirement-001.md:141`,
`bridge/gtkb-harness-state-sot-consolidation-phase-1-mirror-retirement-001.md:150`).
The repo-local equivalent command currently reports the spec has no assertion
definition:

```text
groundtruth-kb/.venv/Scripts/python.exe -m groundtruth_kb assert --spec DCL-HARNESS-STATE-SOT-ASSERTION-001
```

Observed result:

```text
Total specs:       1
With assertions:   0
PASSED:            0
FAILED:            0
Skipped (no def):  1
```

**Impact**

The proposal relies on an assertion command that would not verify the cited DCL
today. That leaves the verification plan incomplete for a blocking specification
unless another executable assertion is added or the proposal maps the DCL to a
different existing check.

**Recommended action**

Add or identify a real assertion definition for
`DCL-HARNESS-STATE-SOT-ASSERTION-001`, or revise the verification plan so the
DCL is covered by the new platform test and a doctor predicate whose output is
expected to pass.

### F3 - P4 - Inventory reference count in the proposal is stale

**Evidence**

The proposal says `.groundtruth/inventory/dev-environment-inventory.json`
currently cites `role-assignments.json` at three lines
(`bridge/gtkb-harness-state-sot-consolidation-phase-1-mirror-retirement-001.md:62`).
Current file evidence shows four references:

```text
.groundtruth/inventory/dev-environment-inventory.json:374
.groundtruth/inventory/dev-environment-inventory.json:451
.groundtruth/inventory/dev-environment-inventory.json:528
.groundtruth/inventory/dev-environment-inventory.json:605
```

**Impact**

This is not the main blocker because the proposed regeneration step should
remove all references, but the stale count weakens the proposal's factual
baseline.

**Recommended action**

Revise the scope table to state the current count accurately, or avoid fixed
line-count claims and require a post-regeneration `rg` proof of zero matches.

## Applicability Preflight

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-harness-state-sot-consolidation-phase-1-mirror-retirement
```

```text
## Applicability Preflight

- packet_hash: `sha256:d7a985b0e451dfee99a158659a2f003fed6a00c0a1ab1588b3a15bf739039d52`
- bridge_document_name: `gtkb-harness-state-sot-consolidation-phase-1-mirror-retirement`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-harness-state-sot-consolidation-phase-1-mirror-retirement-001.md`
- operative_file: `bridge/gtkb-harness-state-sot-consolidation-phase-1-mirror-retirement-001.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation, content:MemBase |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:deferred, content:superseded, content:verified, content:retired |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |
```

## Clause Applicability

```text
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-harness-state-sot-consolidation-phase-1-mirror-retirement
```

```text
## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-harness-state-sot-consolidation-phase-1-mirror-retirement`
- Operative file: `bridge\gtkb-harness-state-sot-consolidation-phase-1-mirror-retirement-001.md`
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
  `python .claude/skills/bridge/helpers/show_thread_bridge.py gtkb-harness-state-sot-consolidation-phase-1-mirror-retirement --format json`
  returned latest status `NEW` with no drift before this verdict.
- Durable role check:
  `groundtruth-kb/.venv/Scripts/python.exe -m groundtruth_kb harness roles`
  returned Codex harness `A` as `["loyal-opposition"]`, so this review is role-actionable.
- Project authorization check:
  `groundtruth-kb/.venv/Scripts/python.exe -m groundtruth_kb projects authorizations PROJECT-GTKB-HARNESS-STATE-SOT-CONSOLIDATION --json`
  returned active PAUTH rowid 134 v2 with mutation classes including
  `file_deletion`, `config_file`, `source_file`, and `test_file`, and
  included work items including `WI-4336` and `WI-4214`.

## Revision Required

Prime should file `REVISED` with:

1. A target scope that includes every file needed to make the retired-path
   verification pass, or a governed narrowing/waiver that explains why retained
   historical references are acceptable and how doctor/test predicates encode
   that distinction.
2. A concrete executable assertion plan for
   `DCL-HARNESS-STATE-SOT-ASSERTION-001` rather than a skipped `gt assert`
   command.
3. Updated inventory baseline evidence count or a line-count-free zero-match
   proof requirement.

No owner decision is currently required from this auto-dispatch review; this is
a Prime Builder revision blocker.
