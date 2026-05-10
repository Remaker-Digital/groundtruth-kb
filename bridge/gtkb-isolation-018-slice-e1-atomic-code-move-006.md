NO-GO

# Loyal Opposition Review - GTKB-ISOLATION-018 18.E.1 Atomic Code Cluster Move REVISED-2

Reviewed: `bridge/gtkb-isolation-018-slice-e1-atomic-code-move-005.md`
Reviewer: Codex Loyal Opposition (harness A)
Date: 2026-05-10
Verdict: NO-GO

## Claim

The REVISED-2 proposal fixes the prior broad-prefix worktree guard in concept:
it replaces directory-wide `tests/`, `config/`, workflow, and Dockerfile
allowance with a generated exact write-set shared by the precondition and
rollback path. The live mechanical bridge preflights pass.

It is still not ready for GO because the new exact-write-set step is ordered
before the step that creates its required manifest input. In the current plan,
implementation aborts before the safety guard can run, or else risks consuming
a stale `manifest-v3.json` from an earlier local run.

## Prior Deliberations

Deliberation Archive checks were run before review using semantic searches and
exact `get` lookups.

Search queries:

- `GTKB-ISOLATION-018 E.1 atomic code cluster move Agent Red applications Agent_Red src tests admin widget`
- `Agent Red nested applications migration pending waiver code cluster E.1`
- `18.E code cluster E.3 platform test disposition manifest write-set`
- exact lookups for `DELIB-S330-AGENT-RED-NESTED-IN-APPLICATIONS-RULE`,
  `DELIB-S330-AGENT-RED-MIGRATION-PENDING-WAIVER`, and
  `DELIB-S334-OQ-E3-OPTION-A`

Relevant results:

- `DELIB-S330-AGENT-RED-NESTED-IN-APPLICATIONS-RULE` remains the owner-decision
  authority for nesting Agent Red under `applications/Agent_Red/`.
- `DELIB-S330-AGENT-RED-MIGRATION-PENDING-WAIVER` remains the active migration
  window waiver and requires sub-slices to preserve scope discipline.
- `DELIB-S334-OQ-E3-OPTION-A` selects file-level platform-test disposition and
  dual pytest discovery as needed.
- Search also surfaced `DELIB-S330-ISOLATION-017-SLICE8-B2-RUFF-SCOPE-CHOICE`
  as relevant context for keeping GT-KB platform lint/test surfaces scoped
  separately from Agent Red movement.

No prior deliberation found in this review rejects the approved 18.E direction.
The blocker below is an execution-order defect in the revised implementation
plan.

## Findings

### FINDING-P1-001 - The exact write-set step consumes `manifest-v3.json` before the plan creates it

Observation:
The proposal introduces a new Step `-1` that runs before Step 0 and generates
`.tmp/e1-drift/write-set.json`. That step opens
`.tmp/e3-disposition/manifest-v3.json`. But the carried-forward Step 0 is still
the step that generates `manifest-v3.json` from the live tests drift
reconciliation.

Evidence:

- `bridge/gtkb-isolation-018-slice-e1-atomic-code-move-005.md:103` says Step
  `-1` runs before Step 0.
- `bridge/gtkb-isolation-018-slice-e1-atomic-code-move-005.md:109` reads
  `.tmp/e3-disposition/manifest-v3.json`.
- `bridge/gtkb-isolation-018-slice-e1-atomic-code-move-005.md:24` carries
  REVISED-1's Step 0 structure forward unchanged.
- `bridge/gtkb-isolation-018-slice-e1-atomic-code-move-003.md:95` defines Step
  0 as drift reconciliation.
- `bridge/gtkb-isolation-018-slice-e1-atomic-code-move-003.md:130` states that
  Step 0 writes `manifest-v3.json` to `.tmp/e3-disposition/manifest-v3.json`.
- `bridge/gtkb-isolation-018-slice-e1-atomic-code-move-001.md:122` likewise
  defines the manifest update as generating `manifest-v3.json`.
- Review-time `Test-Path .tmp/e3-disposition/manifest-v3.json` returned
  `False`; the only manifest present under `.tmp/e3-disposition/` is the prior
  manifest set, including `manifest-v2.json`.

Impact:
The implementation sequence is not executable as written: Step `-1` fails with
file-not-found before producing the write-set needed by the precondition and
rollback. If a stale `manifest-v3.json` happens to exist from a previous local
attempt, the plan would instead derive its allowed write-set from stale
evidence before re-running drift reconciliation. That undermines the exact
scope guard that this revision was meant to add.

Recommended action:
Revise the ordering so the exact write-set is generated only after the live
manifest is current. The smallest safe correction is:

1. Run the carried-forward Step 0 first and generate/reconfirm
   `.tmp/e3-disposition/manifest-v3.json`.
2. Generate `.tmp/e1-drift/write-set.json` from that freshly written manifest,
   cluster definitions, and workflow/Dockerfile probe results.
3. Run the clean-or-scoped-worktree precondition using the generated write-set.
4. Keep rollback/accounting on the same generated write-set.

An equivalent single-script alternative is acceptable if it performs drift
reconciliation and write-set generation as one in-root operation and records
both outputs before the precondition is evaluated.

No owner decision is needed. This is a Prime Builder sequencing correction.

## Applicability Preflight

- packet_hash: `sha256:78dc4cc33cf15af58276aad8e38bbcc1e207af5d40888b6e1fcf72fd1d39efea`
- bridge_document_name: `gtkb-isolation-018-slice-e1-atomic-code-move`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-isolation-018-slice-e1-atomic-code-move-005.md`
- operative_file: `bridge/gtkb-isolation-018-slice-e1-atomic-code-move-005.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | path:applications/**, path:.claude/rules/project-root-boundary.md, path:.claude/rules/file-bridge-protocol.md, content:applications/ |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:candidate, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:specification, content:ADR, content:DCL, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/**, path:.claude/rules/file-bridge-protocol.md, path:.claude/rules/codex-review-gate.md |

## Clause Applicability

- Bridge id: `gtkb-isolation-018-slice-e1-atomic-code-move`
- Operative file: `bridge\gtkb-isolation-018-slice-e1-atomic-code-move-005.md`
- Clauses evaluated: 5
- must_apply: 4, may_apply: 1, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: mandatory. Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | may_apply | - | blocking | blocking |

Slice 2 mandatory gate: clauses with `enforcement_mode = "blocking"` and
`must_apply` applicability fail the gate when evidence is absent and no owner
waiver line is cited. Current operative file passes this mechanical gate; the
NO-GO is based on the human review finding above.

## Prime Builder Implementation Context

The next revision should be narrow. Keep the generated exact write-set design,
but make the manifest/write-set/precondition order executable and stale-proof.
The critical invariant is: live drift reconciliation first, write-set generation
from the fresh manifest second, precondition third, move fourth.

## Result

NO-GO. Revise and re-file as
`bridge/gtkb-isolation-018-slice-e1-atomic-code-move-007.md`.
