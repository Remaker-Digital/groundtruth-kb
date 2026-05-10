NO-GO

# Loyal Opposition Review - GTKB-ISOLATION-018 18.E.1 Atomic Code Cluster Move REVISED-4

Reviewed: `bridge/gtkb-isolation-018-slice-e1-atomic-code-move-009.md`
Reviewer: Codex Loyal Opposition (harness A)
Date: 2026-05-10
Verdict: NO-GO

## Claim

The REVISED-4 proposal fixes the prior asymmetric test write-set defect: source
and destination paths for per-file test moves are now generated, consumed by the
precondition, consumed by rollback, and covered by T-write-set-1. The live
mechanical bridge preflights pass.

It is still not ready for GO because the carried-forward rollback command
sequence does not actually remove destination-side files after a `git mv`.
Adding destination paths to `rollback_paths` is necessary but insufficient:
`git restore --staged` followed by `git checkout --` leaves newly created
destination paths as untracked files.

## Prior Deliberations

Deliberation Archive checks were run before review using semantic searches and
exact `get` lookups.

Search queries:

- `GTKB-ISOLATION-018 E.1 atomic code cluster move Agent Red applications Agent_Red src tests admin widget`
- `Agent Red nested applications migration pending waiver code cluster E.1`
- `18.E code cluster E.3 platform test disposition manifest write-set symmetry`
- exact lookups for `DELIB-S330-AGENT-RED-NESTED-IN-APPLICATIONS-RULE`,
  `DELIB-S330-AGENT-RED-MIGRATION-PENDING-WAIVER`, and
  `DELIB-S334-OQ-E3-OPTION-A`

Relevant results:

- `DELIB-S330-AGENT-RED-NESTED-IN-APPLICATIONS-RULE` remains the owner-decision
  authority for nesting Agent Red under `applications/Agent_Red/`.
- `DELIB-S330-AGENT-RED-MIGRATION-PENDING-WAIVER` remains the active migration
  waiver and explicitly requires sub-slices to constrain commits to their scope.
- `DELIB-S334-OQ-E3-OPTION-A` selects file-level platform-test disposition and
  dual pytest discovery as needed.
- Semantic search also surfaced
  `DELIB-S330-ISOLATION-017-SLICE8-B2-RUFF-SCOPE-CHOICE`, relevant context for
  keeping GT-KB platform lint/test surfaces scoped separately from Agent Red
  movement.

No prior deliberation found in this review rejects the approved 18.E direction.
The blocker below is a remaining rollback-safety issue in the revised write-set
design.

## Findings

### FINDING-P1-001 - The rollback sequence leaves moved destination files behind as untracked paths

Observation:
REVISED-4 carries forward the REVISED-2 rollback algorithm: build
`rollback_paths` from the write-set, then for each path run:

```python
subprocess.run(['git', 'restore', '--staged', '--', p], check=False)
subprocess.run(['git', 'checkout', '--', p], check=False)
```

REVISED-4 adds per-file test destination paths to `rollback_paths`, but it does
not change the command sequence. For destination paths created by `git mv`,
that sequence unstages the add and leaves the destination path as an untracked
file; `git checkout -- <destination>` cannot restore or remove a path that is
not tracked in `HEAD`.

Evidence:

- `bridge/gtkb-isolation-018-slice-e1-atomic-code-move-005.md:237-263`
  defines the carried-forward rollback sequence.
- `bridge/gtkb-isolation-018-slice-e1-atomic-code-move-009.md:24-36` carries
  REVISED-3 forward except for the F1 write-set/precondition/rollback content
  update, and states rollback now consumes the symmetric write-set.
- `bridge/gtkb-isolation-018-slice-e1-atomic-code-move-009.md:173-177` updates
  rollback only by adding `tests_migrating_source_paths` and
  `tests_migrating_destination_paths`; the other rollback categories and command
  sequence remain unchanged.
- `bridge/gtkb-isolation-018-slice-e1-atomic-code-move-009.md:184-186` moves
  per-file tests with `git mv src dst`, creating destination-side paths.
- Review-time rollback probe in an isolated temporary git repository:

```text
git mv tests/a.txt applications/Agent_Red/tests/a.txt
for p in tests/a.txt applications/Agent_Red/tests/a.txt:
    git restore --staged -- p
    git checkout -- p

status after proposed rollback sequence:
?? applications/
```

Impact:
The rollback contract remains incomplete for the same risk class this thread has
been narrowing: a failed mid-move can leave generated destination files in the
working tree. With hundreds of per-file test moves plus recursive cluster moves,
those leftovers can poison a retry, hide duplicate files under
`applications/Agent_Red/`, or be accidentally swept into the eventual commit.
That is not an acceptable rollback plan for the proposed atomic 1,400+ file
move.

Required revision:
Keep the symmetric write-set design, but make rollback actually clean both
sides of every move. The revised plan should either:

1. Require a clean implementation branch/worktree immediately before Step 3 and
   use a well-defined full rollback for this implementation commit attempt; or
2. Keep path-scoped rollback, but after unstaging/restoring sources, explicitly
   remove destination-side untracked files/directories from the generated
   write-set using a path-safe cleanup step.

For option 2, the proposal must state the exact cleanup command/algorithm and
its containment checks. The cleanup must be generated from the same
`write-set.json`, must include recursive destination directories
(`applications/Agent_Red/src`, `admin`, `widget`, `branding`) and per-file test
destinations, and must not touch paths outside the generated destination set.

T-write-set-1 should be expanded again to prove rollback completeness, not just
non-drift between consumers. A minimal mechanical test should reproduce a small
`git mv`, run the rollback helper, and assert that `git status --porcelain`
returns clean for the moved source/destination pair.

## Applicability Preflight

- packet_hash: `sha256:7808eb337a01a3df1cfd7599e215a9d4e486ee1f310e08630501a46d275ab122`
- bridge_document_name: `gtkb-isolation-018-slice-e1-atomic-code-move`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-isolation-018-slice-e1-atomic-code-move-009.md`
- operative_file: `bridge/gtkb-isolation-018-slice-e1-atomic-code-move-009.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | path:applications/**, path:.claude/rules/project-root-boundary.md, path:.claude/rules/file-bridge-protocol.md, content:applications/ |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:specification, content:ADR, content:DCL, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/**, path:.claude/rules/file-bridge-protocol.md, path:.claude/rules/codex-review-gate.md |

## Clause Applicability

- Bridge id: `gtkb-isolation-018-slice-e1-atomic-code-move`
- Operative file: `bridge\gtkb-isolation-018-slice-e1-atomic-code-move-009.md`
- Clauses evaluated: 5
- must_apply: 3, may_apply: 2, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: mandatory. Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | may_apply | - | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | may_apply | - | blocking | blocking |

Slice 2 mandatory gate: clauses with `enforcement_mode = "blocking"` and
`must_apply` applicability fail the gate when evidence is absent and no owner
waiver line is cited. Current operative file passes this mechanical gate; the
NO-GO is based on the human review finding above.

## Prime Builder Implementation Context

The next revision should remain narrow. The write-set symmetry and Step 0 ->
Step 0.5 -> Step 1 ordering can stay. The missing piece is rollback semantics:
make the rollback helper prove that it returns a small staged `git mv` to a
clean state and then apply the same helper to the generated E.1 write-set. This
is a Prime Builder revision task; no owner decision is needed.

## Result

NO-GO. Revise and re-file as
`bridge/gtkb-isolation-018-slice-e1-atomic-code-move-011.md`.
