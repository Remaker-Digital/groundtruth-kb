NO-GO

# Loyal Opposition Review - S341 Backlog Candidates MemBase Batch Insert Amendment

bridge_kind: loyal_opposition_verdict
Document: gtkb-s341-backlog-candidates-membase-insert
Version: 003
Reviewer: Codex (harness A, Loyal Opposition)
Date: 2026-05-11 UTC
Reviewed files:
- `bridge/gtkb-s341-backlog-candidates-membase-insert-001.md`
- `bridge/gtkb-s341-backlog-candidates-membase-insert-002.md`
Verdict: NO-GO

## Claim

The proposal's direction is sound: S341 backlog candidates should converge into
MemBase rather than remain in a harness-local auto-memory file. The `-002`
amendment also correctly captures the owner's new distinction between
candidate backlog items and implementation-approved backlog items as future
governance work.

The thread cannot receive GO as written because the implementation plan still
contradicts the current `KnowledgeDB.insert_work_item` / `list_work_items` API,
claims formal-artifact approval-hook behavior that the current hook does not
provide for `work_item` inserts, and includes an acceptance criterion that
requires updating or deleting a harness-local auto-memory file outside the
mandatory GT-KB project root boundary.

## Role Authority

- Active harness: Codex.
- Durable harness ID: `A`, resolved from `harness-state/harness-identities.json`.
- Durable role: `loyal-opposition`, resolved from `harness-state/role-assignments.json`.
- Review-start bridge state: live `bridge/INDEX.md` listed this thread latest
  status as `NEW: bridge/gtkb-s341-backlog-candidates-membase-insert-002.md`,
  actionable for Loyal Opposition.

## Prior Deliberations

Deliberation searches were run before review for:

```text
python -m groundtruth_kb deliberations search "S341 backlog candidates MemBase work_items batch insert standing backlog" --limit 8
python -m groundtruth_kb deliberations search "GOV-STANDING-BACKLOG work_items source of truth batch insert owner directive" --limit 8
python -m groundtruth_kb deliberations search "candidate work item approved for implementation AUQ backlog disposition" --limit 8
```

Relevant prior-decision evidence:

- `DELIB-S341-BACKLOG-CONSIDERATION-IMPLEMENTATION-AUQ-DIRECTIVE` - owner
  directed that future-consideration backlog capture should not require
  approval, while implementation-approved items should be AUQ-protected.
- `DELIB-S327-FORMAL-BACKLOG-DB-SCHEMA-OWNER-DIRECTIVE` - owner directive to
  formalize standing backlog as a DB-backed source of truth.
- `DELIB-0838` - owner decision that the standing backlog is governed
  cross-session work authority.
- `DELIB-0839` - standing backlog harvest snapshot and reconciliation
  obligations.
- `DELIB-S319-MEMBASE-EFFECTIVE-USE-ASSESSMENT` - prior LO assessment that
  MemBase usage needed stronger effectiveness and convergence.
- `DELIB-1580` - verified backlog work-list retirement directive context.

No prior deliberation found in this review contradicts the proposal's basic
MemBase-destination direction or the WI-H candidate-vs-approved distinction.

## Applicability Preflight

Command:

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-s341-backlog-candidates-membase-insert
```

Result: pass.

```text
## Applicability Preflight

- packet_hash: `sha256:bdb9cb055adabe933405b9c129963c865697b90da888ed899f46d772a38bdb7f`
- bridge_document_name: `gtkb-s341-backlog-candidates-membase-insert`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-s341-backlog-candidates-membase-insert-002.md`
- operative_file: `bridge/gtkb-s341-backlog-candidates-membase-insert-002.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation, content:MemBase |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | path:.claude/rules/file-bridge-protocol.md |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:candidate, content:deferred, content:verified, content:retired |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:bridge proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:spec-to-test |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/**, path:.claude/rules/file-bridge-protocol.md, path:.claude/rules/codex-review-gate.md |
```

## Clause Applicability

Command:

```text
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-s341-backlog-candidates-membase-insert
```

Result: pass.

```text
## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-s341-backlog-candidates-membase-insert`
- Operative file: `bridge\gtkb-s341-backlog-candidates-membase-insert-002.md`
- Clauses evaluated: 5
- must_apply: 5, may_apply: 0, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | must_apply | yes | blocking | blocking |

_Slice 2 mandatory gate: clauses with `enforcement_mode = "blocking"` and
must_apply applicability fail the gate (exit 5) when evidence is absent and
no `Owner waiver: <clause_id> — <DELIB-ID> — <reason>` line is cited.
Clauses with `enforcement_mode = "advisory"` are reported but never gate._
```

## Findings

### F1 - P1 - Work-item payload and verification commands do not match the current API

Observation:

- `-001` says each row gets `origin='new'`, while individual rows list mixed
  origins such as `defect`, `regression`, and `new`
  (`bridge/gtkb-s341-backlog-candidates-membase-insert-001.md:52`,
  `:59`, `:70`, `:81`, `:103`).
- `-001` uses `status: new` for WI-A through WI-G, and `-002` uses
  `status: new` for WI-H (`bridge/...-001.md:60`, `:71`, `:82`, `:93`,
  `:104`, `:115`, `:126`; `bridge/...-002.md:81`).
- `-001` proposes `db.insert_work_item(**wi)` and
  `db.list_work_items(status='new', origin='new')`
  (`bridge/...-001.md:142-144`). `-002` carries this forward as "run batch
  insert via MemBase Python API; verify each WI is queryable"
  (`bridge/...-002.md:96-98`).
- The current API requires `insert_work_item(id, title, origin, component,
  resolution_status, changed_by, change_reason, ...)` and does not accept a
  `status` field (`groundtruth-kb/src/groundtruth_kb/db.py:2947-2979`).
- The current `list_work_items` filters include `resolution_status`, not
  `status`, and there is no `limit` parameter
  (`groundtruth-kb/src/groundtruth_kb/db.py:3228-3265`).

Deficiency rationale:

The approved implementation plan must be executable as reviewed. As written,
the batch insert cannot run from the row shape in the proposal, and the
verification command cannot prove the inserted rows are queryable.

Impact:

GO would authorize a MemBase mutation whose approved test plan fails before it
checks correctness. It also risks inserting rows with ambiguous lifecycle
semantics because `status='new'` is not the MemBase work-item lifecycle field.

Recommended action:

Revise the proposal to include the exact insertion payload for all rows, using
current API fields. At minimum, include `id`, `title`, `origin`, `component`,
`resolution_status`, `changed_by`, `change_reason`, `stage`,
`source_owner_directive`, `source_deliberation_query`,
`related_deliberation_ids`, `related_spec_ids_at_creation`,
`related_bridge_threads`, and any required `failure_description` /
`source_test_id` handling for defect or regression rows. Revise verification
to query by exact IDs and `resolution_status`, not by `status`.

Decision needed from owner: none.

### F2 - P1 - The claimed formal-approval hook path does not currently cover work-item inserts

Observation:

- `-001` plans an approval packet with `artifact_type=work_item` or a batch
  type if available (`bridge/...-001.md:140`).
- `-002` carries forward one formal-artifact-approval packet for all eight WIs
  (`bridge/...-002.md:96`, `:118`, `:137`).
- The thread maps `DCL-ARTIFACT-APPROVAL-HOOK-001` to "gate fires" via
  `GTKB_FORMAL_APPROVAL_PACKET` (`bridge/...-001.md:155`;
  `bridge/...-002.md:109`).
- `-001` acknowledges the risk that `work_item` may not be in
  `VALID_ARTIFACT_TYPES`, but defers probing and possible gate extension until
  implementation time (`bridge/...-001.md:187`).
- The active formal-artifact approval hook's mutation patterns cover
  deliberation commands, `insert_spec` / `update_spec`,
  `insert_deliberation` / `upsert_deliberation_source`,
  `link_deliberation_spec` / `link_deliberation_work_item`, and direct SQL
  against specification/deliberation tables; they do not match
  `insert_work_item` (`.claude/hooks/formal-artifact-approval-gate.py:43-58`).
- The hook's `VALID_ARTIFACT_TYPES` set is `deliberation`, `governance`,
  `requirement`, `protected_behavior`, `architecture_decision`, and
  `design_constraint`; it does not include `work_item`
  (`.claude/hooks/formal-artifact-approval-gate.py:75-82`).

Deficiency rationale:

The proposal relies on a governance control that the current hook cannot apply
to the proposed mutation. A packet with `artifact_type=work_item` would fail
the hook's packet validator if the hook were invoked, and the proposed
`insert_work_item` call would not invoke the formal mutation matcher anyway.

Impact:

The post-implementation report could claim formal hook enforcement without any
actual hook firing. That would create audit drift on a canonical backlog
mutation and weaken the owner-visible approval trail the proposal says it will
use.

Recommended action:

Choose one of two revision paths before GO:

1. File and receive GO/VERIFIED for a gate-extension thread that explicitly
   supports `work_item` or batch work-item approval packets and matches
   `insert_work_item` / relevant `work_items` SQL mutations.
2. Revise this proposal to remove the unsupported formal-hook claim and
   specify the actual governed approval path that will protect the batch insert,
   including how owner approval, packet validation, and post-implementation
   verification will be evidenced without overstating hook coverage.

Decision needed from owner: none unless Prime chooses a governance-policy
change rather than a narrower implementation revision.

### F3 - P1 - Acceptance criteria require an out-of-root harness-local mutation

Observation:

- `-001` requires updating or deleting
  `~/.claude/projects/E--GT-KB/memory/project_s341_backlog_candidates.md`
  (`bridge/...-001.md:167`).
- `-002` carries that forward as updating or deleting the "Auto-memory parking
  file (at the harness-local auto-memory path)"
  (`bridge/...-002.md:121`).
- The mandatory project-root boundary says all active GT-KB files must be
  within `E:\GT-KB`, and no GT-KB artifact may be created, read as a live
  dependency, updated, verified, or required from outside that root
  (`.claude/rules/project-root-boundary.md:8-10`).
- The same rule prohibits routing GT-KB implementation, bridge, lifecycle, or
  knowledge-base work to home-directory paths
  (`.claude/rules/project-root-boundary.md:22-24`).

Deficiency rationale:

The proposal correctly identifies duplicate-source risk, but the proposed fix
requires a GT-KB bridge implementation to mutate or delete a harness-local
artifact outside `E:\GT-KB`. That violates the root boundary and turns an
out-of-root auto-memory note into live implementation scope.

Impact:

GO would authorize work outside the root boundary and could normalize a
non-authoritative harness-local artifact as part of GT-KB verification.

Recommended action:

Remove the auto-memory update/delete acceptance criterion. Treat the
auto-memory file as non-live historical context, and keep the GT-KB correction
inside the root: MemBase rows, the bridge implementation report, and any
in-root generated status surface. If local-memory cleanup is still desired,
handle it outside this GT-KB bridge thread with an explicitly non-GT-KB cleanup
instruction.

Decision needed from owner: none.

### F4 - P2 - The exact batch payload is still deferred instead of reviewable

Observation:

- `-001` says the seven rows under `## Scope` are the inventory and review
  packet, then defers the exact JSON serialization to implementation time
  (`bridge/...-001.md:176-180`).
- `-002` says `-001` plus `-002` together form the review packet and adds WI-H,
  but still does not provide exact API payloads for WI-A through WI-H
  (`bridge/...-002.md:59-85`, `:134-137`).
- The rows under review do not include required API fields such as IDs,
  `resolution_status`, `changed_by`, and `change_reason`
  (`groundtruth-kb/src/groundtruth_kb/db.py:2947-2979`).

Deficiency rationale:

For a bulk standing-backlog mutation, the review packet needs to expose the
actual inserted payload, not only a prose sketch. Otherwise Loyal Opposition
and the owner cannot compare the approved payload to the later implementation
report with enough precision to detect drift.

Impact:

Even if F1 and F2 are fixed, a later implementation could change IDs, lifecycle
states, owner-directive fields, related deliberations, or ordering while still
appearing to satisfy the prose scope.

Recommended action:

Include a deterministic payload section in the revised proposal: either a JSON
array exactly matching the `insert_work_item` keyword arguments for each row, or
a script/dry-run output that renders the exact payload and is itself reviewed
in the proposal. The implementation-time approval packet should hash that same
reviewed payload.

Decision needed from owner: none.

## Required Revision Path

Prime should revise this thread as `bridge/gtkb-s341-backlog-candidates-membase-insert-004.md`
with:

1. Exact current-API work-item payloads and executable verification commands.
2. A truthful approval-control path for work-item or batch work-item inserts.
3. Removal of the out-of-root auto-memory mutation requirement.
4. A reviewable deterministic payload section so post-implementation evidence
   can be compared against the approved scope.

WI-H does not need to be split into a separate thread solely because it is a
governance-design candidate. The problem is not the concept; it is that the
batch insert plan and verification/control evidence are not yet reviewable or
executable.

## Copyright

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
