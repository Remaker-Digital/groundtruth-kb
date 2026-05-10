NO-GO

# Loyal Opposition Review - GTKB-ISOLATION-018 18.E.1 Atomic Code Cluster Move REVISED-5

Reviewed: `bridge/gtkb-isolation-018-slice-e1-atomic-code-move-011.md`
Reviewer: Codex Loyal Opposition (harness A)
Date: 2026-05-10
Verdict: NO-GO

## Claim

REVISED-5 fixes the prior rollback-completeness issue for the normal in-scope
`git mv` path shape: the new four-phase rollback resets the index, restores
source-side paths, and explicitly removes destination-side untracked artifacts.
The live mechanical bridge preflights pass.

It is still not ready for GO because the rollback helper's stated containment
invariant is not true for destination files. The proposed Phase 3 cleanup
unlinks files and symlinks before applying the `applications/Agent_Red/`
containment check; the check is applied only to directories. That contradicts
the proposed T-write-set-1 mutation-test claim and leaves the safety helper able
to delete an out-of-scope destination file if the generated write-set is wrong,
stale, or corrupted.

## Prior Deliberations

Deliberation Archive checks were run before review using semantic search and
exact `get` lookups.

Search query:

- `GTKB-ISOLATION-018 E.1 atomic code cluster move Agent Red applications Agent_Red rollback write-set`

Relevant results and exact checks:

- `DELIB-S330-AGENT-RED-NESTED-IN-APPLICATIONS-RULE` remains the owner-decision
  authority for nesting Agent Red under `applications/Agent_Red/`.
- `DELIB-S330-AGENT-RED-MIGRATION-PENDING-WAIVER` remains the active
  migration-window waiver and requires sub-slices to constrain commits to their
  scope.
- `DELIB-S334-OQ-E3-OPTION-A` remains relevant for the file-level platform-test
  disposition and dual pytest discovery.
- Semantic search also surfaced older isolation-contract/rehearsal records
  (`DELIB-0878`, `DELIB-1119`, `DELIB-1327`, `DELIB-1328`, `DELIB-1329`), but
  no prior deliberation found in this review rejects the approved 18.E.1
  direction.

The blocker below is a remaining rollback-helper containment defect, not an
objection to the atomic code-cluster move itself.

## Findings

### FINDING-P1-001 - Phase 3 cleanup deletes destination files before the containment check

Observation:
REVISED-5 claims the rollback cleanup operates only on generated destination
paths under `applications/Agent_Red/`, and that T-write-set-1 proves Phase 3's
containment assert fires when a synthetic write-set names a destination outside
that tree. The proposed algorithm does not satisfy that claim for files or
symlinks. In Phase 3, `path.unlink()` runs before any containment assertion;
the assertion exists only in the directory branch.

Evidence:

- `bridge/gtkb-isolation-018-slice-e1-atomic-code-move-011.md:158` starts
  Phase 3 destination-side cleanup.
- `bridge/gtkb-isolation-018-slice-e1-atomic-code-move-011.md:160-162` builds
  `destinations_to_clean` from recursive destination directories, destination
  files, and migrated-test destination files.
- `bridge/gtkb-isolation-018-slice-e1-atomic-code-move-011.md:164-167`
  immediately unlinks destination files and symlinks.
- `bridge/gtkb-isolation-018-slice-e1-atomic-code-move-011.md:168-172` applies
  the `applications/Agent_Red/` containment assertion only for directories.
- `bridge/gtkb-isolation-018-slice-e1-atomic-code-move-011.md:213` says
  T-write-set-1 mutation tests confirm "Phase 3's containment assert fires when
  the synthetic write-set names a destination outside `applications/Agent_Red/`."
  That statement is false for an outside destination file.
- Review-time in-root scratch probe, applying only the proposed Phase 3 branch
  ordering to a self-created file `outside.txt`, produced:

```text
exists_after=False
events=unlinked-file-before-containment-check
```

Impact:
The rollback helper is the safety mechanism for a 1,400+ file move. If its
write-set is stale, corrupted, incorrectly generated, or accidentally includes
an out-of-scope destination file, the helper can delete that file before any
containment guard runs. That breaks the scope-discipline invariant from
`DELIB-S330-AGENT-RED-MIGRATION-PENDING-WAIVER` and weakens the rollback safety
that REVISED-5 was meant to establish.

Required revision:
Revise the rollback helper so every destination path is validated before any
destructive action, regardless of file type. The smallest safe correction is:

1. Normalize and validate each destination path before the file/dir branch.
2. Reject absolute paths, parent traversal, and any destination that is not
   under `applications/Agent_Red/`.
3. Only after validation, run `unlink()` for files/symlinks or `rmtree()` for
   directories.
4. Expand T-write-set-1 to prove both outside-file and outside-directory
   destinations fail before deletion, and that in-scope file/dir destinations
   still clean correctly.

No owner decision is needed. This is a Prime Builder revision task.

## Applicability Preflight

- packet_hash: `sha256:e2f8d07c519cb7ddf1c9cafbf73157c8691e0681d6a8704f6ab9e12965918fa2`
- bridge_document_name: `gtkb-isolation-018-slice-e1-atomic-code-move`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-isolation-018-slice-e1-atomic-code-move-011.md`
- operative_file: `bridge/gtkb-isolation-018-slice-e1-atomic-code-move-011.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | path:applications/**, path:.claude/rules/project-root-boundary.md, path:.claude/rules/file-bridge-protocol.md, content:applications/ |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal, content:bridge proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:specification, content:ADR, content:DCL, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/**, path:.claude/rules/file-bridge-protocol.md, path:.claude/rules/codex-review-gate.md |

## Clause Applicability

- Bridge id: `gtkb-isolation-018-slice-e1-atomic-code-move`
- Operative file: `bridge\gtkb-isolation-018-slice-e1-atomic-code-move-011.md`
- Clauses evaluated: 5
- must_apply: 3, may_apply: 2, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | may_apply | — | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | may_apply | — | blocking | blocking |

_Slice 2 mandatory gate: clauses with `enforcement_mode = "blocking"` and
must_apply applicability fail the gate (exit 5) when evidence is absent and
no `Owner waiver: <clause_id> — <DELIB-ID> — <reason>` line is cited.
Clauses with `enforcement_mode = "advisory"` are reported but never gate._

## Prime Builder Implementation Context

The next revision should remain narrow. Keep the four-phase rollback structure,
but move destination containment validation ahead of `unlink()` and `rmtree()`
for every path. Then update the rollback-completeness test so it explicitly
covers outside destination files as well as outside destination directories.

Expected touchpoints for the revision are only the bridge proposal text and,
after GO, the planned implementation helper/test:

- `scripts/rollback_e1_write_set.py`
- `tests/governance/test_isolation_018_e1_rollback_completeness.py`

The revised proposal should also state whether validation uses lexical
repository-relative paths or resolved paths. If resolved paths are used, the
comparison should be against the resolved `applications/Agent_Red/` root so a
path such as `applications/Agent_Red/../outside.txt` cannot pass.

## Result

NO-GO. Revise and re-file as
`bridge/gtkb-isolation-018-slice-e1-atomic-code-move-013.md`.
