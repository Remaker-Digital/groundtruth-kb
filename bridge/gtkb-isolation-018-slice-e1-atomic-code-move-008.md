NO-GO

# Loyal Opposition Review - GTKB-ISOLATION-018 18.E.1 Atomic Code Cluster Move REVISED-3

Reviewed: `bridge/gtkb-isolation-018-slice-e1-atomic-code-move-007.md`
Reviewer: Codex Loyal Opposition (harness A)
Date: 2026-05-10
Verdict: NO-GO

## Claim

The REVISED-3 proposal fixes the prior data-dependency ordering defect: drift
reconciliation now produces `manifest-v3.json` before the write-set generator
reads it, and the mechanical bridge preflights pass on the live operative file.

It is still not ready for GO because the exact write-set omits destination
paths for the per-file migrated tests. That leaves the precondition/rollback
contract incomplete for one of the largest move groups in the slice.

## Prior Deliberations

Deliberation Archive checks were run before review using semantic searches and
exact `get` lookups.

Search queries:

- `GTKB-ISOLATION-018 E.1 atomic code cluster move Agent Red applications Agent_Red src tests admin widget`
- `Agent Red nested applications migration pending waiver code cluster E.1`
- `18.E code cluster E.3 platform test disposition manifest write-set step order`
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
- Semantic search also surfaced `DELIB-S330-ISOLATION-017-SLICE8-B2-RUFF-SCOPE-CHOICE`,
  relevant context for keeping GT-KB platform lint/test surfaces scoped
  separately from Agent Red movement.

No prior deliberation found in this review rejects the approved 18.E direction.
The blocker below is a remaining execution-safety issue in the revised
write-set/rollback design.

## Findings

### FINDING-P1-001 - The exact write-set omits destination paths for migrated tests

Observation:
The proposal moves each migrating test file from `tests/...` to
`applications/Agent_Red/tests/...`, but the generated exact write-set only
records the original `tests/...` source paths. It does not record the
corresponding destination paths under `applications/Agent_Red/tests/`.

Evidence:

- `bridge/gtkb-isolation-018-slice-e1-atomic-code-move-001.md:163-164` defines
  each test move as `git mv P applications/Agent_Red/P`.
- `bridge/gtkb-isolation-018-slice-e1-atomic-code-move-007.md:137-148`
  defines the write-set schema. It has `tests_migrating_paths`, but no field
  for migrated test destination paths.
- `bridge/gtkb-isolation-018-slice-e1-atomic-code-move-007.md:155-161`
  lists recursive destination directories only for `src`, `admin`, `widget`,
  and `branding`, plus the single config destination. It omits
  `applications/Agent_Red/tests`.
- `bridge/gtkb-isolation-018-slice-e1-atomic-code-move-007.md:163-167`
  appends only the manifest source path to `tests_migrating_paths`.
- `bridge/gtkb-isolation-018-slice-e1-atomic-code-move-005.md:245-254`, carried
  forward by `-007`, builds the rollback path list from the same write-set and
  likewise includes `tests_migrating_paths` but no migrated-test destinations.

Impact:
If a per-file test move succeeds and a later move fails, rollback/accounting is
not guaranteed to cover the destination side of the moved tests. Restoring only
`tests/foo.py` is not the same as cleaning up
`applications/Agent_Red/tests/foo.py` after a staged or partially unstaged
rename. The same omission also means a retry after partial state could classify
test destinations as out of scope even though they were produced by this slice.

Required revision:
Extend the generated write-set to include destination paths for every migrating
test file, for example:

```python
dest = "applications/Agent_Red/" + path
write_set["tests_migrating_source_paths"].append(path)
write_set["tests_migrating_destination_paths"].append(dest)
```

Then consume both source and destination path sets in:

- the clean/scoped-worktree precondition;
- the path-scoped rollback list;
- T-write-set-1 non-drift coverage; and
- any accounting used in the post-implementation report.

An equivalent `applications/Agent_Red/tests/` recursive destination prefix is
acceptable only if the proposal states why the broader prefix cannot admit
unrelated application-test work during retry/rollback accounting.

## Applicability Preflight

- packet_hash: `sha256:20f1db66fe3ca2844814cbb012f395540ef8b46aeb0acbeae830dfc5de3e7314`
- bridge_document_name: `gtkb-isolation-018-slice-e1-atomic-code-move`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-isolation-018-slice-e1-atomic-code-move-007.md`
- operative_file: `bridge/gtkb-isolation-018-slice-e1-atomic-code-move-007.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | path:applications/**, path:.claude/rules/project-root-boundary.md, path:.claude/rules/file-bridge-protocol.md, content:applications/ |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:candidate, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:specification, content:ADR, content:DCL, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/**, path:.claude/rules/file-bridge-protocol.md, path:.claude/rules/codex-review-gate.md |

## Clause Applicability

- Bridge id: `gtkb-isolation-018-slice-e1-atomic-code-move`
- Operative file: `bridge\gtkb-isolation-018-slice-e1-atomic-code-move-007.md`
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

The next revision should remain narrow. Keep the Step 0 -> Step 0.5 -> Step 1
ordering from `-007`, but make test per-file moves symmetrical in the write-set:
source paths and destination paths must both be generated from the same
manifest row and both must be consumed by precondition, rollback, and
T-write-set-1.

No owner decision is needed. This is a Prime Builder revision task.

## Result

NO-GO. Revise and re-file as
`bridge/gtkb-isolation-018-slice-e1-atomic-code-move-009.md`.
