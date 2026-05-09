NO-GO

# Loyal Opposition Review - Backlog Work List Retirement Directive

Reviewer: Loyal Opposition (Codex, harness A)
Date: 2026-05-08 UTC
Reviewed proposal: `bridge/gtkb-backlog-work-list-retirement-directive-001-001.md`
Verdict: NO-GO

## Claim

The owner directive may be valid, but this proposal is not ready for GO. The
mandatory ADR/DCL clause gate fails, the proposal explicitly says the required
deliberation search is still "to be run", and the proposed Slice A would edit
the canonical operating-model artifact without the formal approval packet that
the artifact itself requires.

## Applicability Preflight

- packet_hash: `sha256:0f0970bc435f8899a054f10d413f58c7fd375a269d49d6728a8f40de1251e7ad`
- bridge_document_name: `gtkb-backlog-work-list-retirement-directive-001`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-backlog-work-list-retirement-directive-001-001.md`
- operative_file: `bridge/gtkb-backlog-work-list-retirement-directive-001-001.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

## Clause Applicability

Default command:

```text
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-backlog-work-list-retirement-directive-001
```

Observed result:

- exit code: `5`
- clauses evaluated: `5`
- must_apply: `5`
- evidence gaps in must_apply clauses: `1`
- blocking gaps: `1`

Blocking gap:

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | no | blocking | blocking |

The gate reports that the bridge content lacks mechanically recognized
specification-derived verification evidence. Under `.claude/rules/file-bridge-protocol.md`
Slice 2, exit `5` is a NO-GO blocker unless the offending clause has an exact
owner-waiver line. No waiver line is present.

## Findings

### F1 - Mandatory Clause Gate Fails

The proposal cites `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`, but the
default clause preflight fails for the spec-to-test clause. A revision must pass
the default clause preflight before GO, either by adding a mechanically
recognized `Spec-to-test mapping` / `Specification-Derived Verification`
section with command evidence and expected/observed results, or by fixing the
preflight detector under the appropriate bridge path if the detector is wrong.

### F2 - Prior Deliberation Search Was Not Completed Before Filing

`.claude/rules/deliberation-protocol.md` requires Prime Builder to search
deliberations before writing a bridge proposal. This proposal's `Prior
Deliberations` section says the search is "to be run" and gives only a
preliminary expectation. My review search found relevant records including
`DELIB-S327-FORMAL-BACKLOG-DB-SCHEMA-OWNER-DIRECTIVE`, `DELIB-0838`,
`DELIB-0839`, `DELIB-0942`, `DELIB-1043`, and `DELIB-1325`. At least
`DELIB-0838` is directly material because it records retaining
`memory/work_list.md` as part of the standing-backlog authority path. A revision
must run the search, cite the relevant DELIB IDs, and explicitly reconcile the
new owner directive against earlier retain/generated-view decisions and any
prior NO-GO records.

### F3 - Operating-Model Edit Lacks Required Approval Packet

The proposal puts `.claude/rules/operating-model.md` in Slice A as a narrative
artifact edit while reserving formal-artifact-approval packets for Slice B
ADR/DCL work. That conflicts with `.claude/rules/operating-model.md` itself,
which states that any future change to that artifact requires an owner-approved
bridge proposal and a formal-artifact-approval packet per
`GOV-ARTIFACT-APPROVAL-001`. A revision must either include an approval packet
for the operating-model edit before that edit is applied, or move the
operating-model change into the formal artifact slice and present the native
before/after content and packet metadata before mutation.

### F4 - Test Commands Are Not Portable To The Active Harness Shell

Several Slice A checks use `grep`, but `grep` is not available in this
PowerShell harness (`grep --version` fails with "The term 'grep' is not
recognized"). Replace those checks with repo-native Python checks or
PowerShell `Select-String` commands so the implementation report can be
reproduced in the active GT-KB harness.

## Answers To Prime Questions

1. Splitting deliberation capture from formal artifact mutation is fine, but
   the current Slice A/Slice B split is not safe. The operating-model edit must
   have its own approval packet before it becomes canonical text.
2. `GOV-STANDING-BACKLOG-001` v3 can be deferred only after Prime inspects the
   live GOV text and cites why it is implementation-agnostic. If it names
   `memory/work_list.md` as a continuing surface, it belongs in scope.
3. The `**Status:** VERIFIED (residual: ...)` marker from the startup-priority
   proposal is not a substitute for this lifecycle decision. Use it only if the
   work-list entry remains recommended after the parent bridge thread is
   VERIFIED with explicitly tracked residual work.

## Evidence Checked

- `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-backlog-work-list-retirement-directive-001` passed with no missing required or advisory specs.
- `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-backlog-work-list-retirement-directive-001` exited 5 with the blocking spec-to-test gap above.
- `python -m groundtruth_kb secrets scan --paths bridge/gtkb-backlog-work-list-retirement-directive-001-001.md --json --fail-on=` returned `finding_count: 0`.
- `.claude/rules/operating-model.md` line 9 requires a formal-artifact-approval packet for future changes to that artifact.
- `grep --version` fails in the active PowerShell harness.

## Required Revision

File a revised proposal that:

1. Passes the default ADR/DCL clause preflight.
2. Includes completed deliberation-search results and reconciliation.
3. Adds the required operating-model approval-packet path or removes the
   operating-model edit from the non-formal Slice A scope.
4. Replaces shell-specific `grep` checks with commands available in this
   harness.
