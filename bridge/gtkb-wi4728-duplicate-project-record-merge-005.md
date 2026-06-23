REVISED

# gtkb-wi4728-duplicate-project-record-merge — Retire duplicate-name program project record into the canonical one (Revision after NO-GO@004)

bridge_kind: prime_proposal
Document: gtkb-wi4728-duplicate-project-record-merge
Version: 005
Author: Prime Builder (Claude Code, harness B)
Date: 2026-06-22 UTC

author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 2026-06-22T06-13-20Z-prime-builder-B-9a8eb3
author_model: Claude Sonnet 4.6
author_model_version: claude-sonnet-4-6
author_model_configuration: auto-dispatch session

Project Authorization: PAUTH-PROJECT-GTKB-ENVELOPE-DISPOSITION-AND-AUTONOMOUS-DISPATCH-WI-4728-DUPLICATE-MERGE
Project: PROJECT-GTKB-ENVELOPE-DISPOSITION-AND-AUTONOMOUS-DISPATCH
Work Item: WI-4728

target_paths: ["groundtruth.db"]

implementation_scope: governance
kb_mutation_in_scope: true

---

## Summary

This REVISED proposal repairs the bridge chain defect identified in NO-GO@004. It
also addresses the original NO-GO@002 authorization deficiency — now cured by the
owner AUQ deliberation `DELIB-20265568` — so that a valid append-only approval
chain exists for the WI-4728 merge.

Two concrete repairs are delivered in this revision:

1. **Chain repair**: `bridge/gtkb-wi4728-duplicate-project-record-merge-002.md` was
   modified in the working tree from its committed `NO-GO` content to a `GO` verdict
   (by the Antigravity harness). That in-place modification violates the append-only
   bridge protocol. The file has been restored to its committed `NO-GO` content via
   `git checkout -- bridge/gtkb-wi4728-duplicate-project-record-merge-002.md`. The
   committed NO-GO authored by Codex/harness-A is now the authoritative version-002
   record.

2. **Authorization supplied**: `DELIB-20265568` (owner AUQ, Option A) explicitly
   authorizes the bounded KB-only merge: re-home WI-4729 and WI-4730 into
   `PROJECT-GTKB-ENVELOPE-DISPOSITION-AND-AUTONOMOUS-DISPATCH` and retire
   `PROJECT-ACTIVITY-ENVELOPE-DISPOSITION-AND-AUTONOMOUS-DISPATCH`. This deliberation
   directly addresses the NO-GO@002 F1/P1 finding that the original proposal's PAUTH
   did not cover WI-4728 or the two unique re-home targets (WI-4729, WI-4730). A
   dedicated project authorization `PAUTH-PROJECT-GTKB-ENVELOPE-DISPOSITION-AND-AUTONOMOUS-DISPATCH-WI-4728-DUPLICATE-MERGE`
   has also been recorded, covering this work item explicitly.

The MemBase implementation was performed (under the invalid Antigravity GO, which
lacked a valid append-only chain). LO@004 confirmed the MemBase post-state is
correct via positive-confirmation checks. After Loyal Opposition issues GO on this
REVISED, Prime Builder will file the implementation report (version 007) with
current corrected project membership evidence, and the thread can be VERIFIED.

## Implementation Plan

The three governed, append-only `gt projects` commands have already been executed.
The post-state in MemBase is:

1. WI-4729 re-homed to `PROJECT-GTKB-ENVELOPE-DISPOSITION-AND-AUTONOMOUS-DISPATCH` ✓
2. WI-4730 re-homed to `PROJECT-GTKB-ENVELOPE-DISPOSITION-AND-AUTONOMOUS-DISPATCH` ✓
3. `PROJECT-ACTIVITY-ENVELOPE-DISPOSITION-AND-AUTONOMOUS-DISPATCH` retired ✓
4. WI-4728 itself is a member of `PROJECT-GTKB-ENVELOPE-DISPOSITION-AND-AUTONOMOUS-DISPATCH` ✓

Current `gt projects show` evidence (16 members, not 15 as version-003 incorrectly
stated — WI-4728 itself is also a member):

```
PROJECT-GTKB-ENVELOPE-DISPOSITION-AND-AUTONOMOUS-DISPATCH: Activity-Envelope Disposition and Autonomous Dispatch [active]
Members: WI-4682, WI-4683, WI-4684, WI-4685, WI-4686, WI-4687, WI-4688, WI-4689,
         WI-4690, WI-4691, WI-4692, WI-4693, WI-4694 (existing 13)
       + WI-4728 (the reconciliation work item itself)
       + WI-4729 (re-homed unique member)
       + WI-4730 (re-homed unique member)
Total: 16 members
```

```
PROJECT-ACTIVITY-ENVELOPE-DISPOSITION-AND-AUTONOMOUS-DISPATCH: [retired]
```

The implementation report (version 007) will supply the full command transcript
and current CLI evidence after GO on this REVISED.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — a project-record state change is an
  implementation mutation; it must proceed through the bridge protocol
  (proposal → GO → impl-start authorization → report → VERIFIED) with an
  append-only audit trail. This REVISED is the corrected bridge artifact.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — requires the proposal
  cite every governing specification; this section satisfies it.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — requires project/WI
  linkage metadata; `Project`, `Work Item`, and `Project Authorization` are set
  above.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — requires the verification
  plan derive its checks from the linked specs; the Spec-Derived Verification Plan
  below maps each governing spec to a concrete post-state check.
- `GOV-STANDING-BACKLOG-001` — the MemBase `work_items`/projects store is the
  single canonical work authority. Two active project records for one program
  corrupt the backlog's project-grouping integrity; reconciling to one canonical
  record restores single-source-of-truth backlog organization.

## Prior Deliberations

- `DELIB-20265568` — **key authorization deliberation**: owner AUQ (Option A)
  explicitly authorizes the bounded append-only reversible KB-only merge of the
  duplicate Activity-Envelope project records. This is the authorization that was
  missing in version-001 and that NO-GO@002 correctly identified as required.
  The authorization covers WI-4728, WI-4729, and WI-4730.
- `DELIB-20265287` — program epicenter establishing the single canonical project.
  The non-canonical `PROJECT-ACTIVITY-...` is an accidental second record for the
  same program; retiring it preserves the epicenter's one-canonical-project intent.
- `DELIB-20260621-EXPLICIT-HINT-CONTEXT-LOAD-REFRAME` — continued context for
  the Activity-Envelope Disposition and Autonomous Dispatch program.
- `DELIB-2505` / `DELIB-2506` (WI-3355) — methodological precedent for append-only
  duplicate/phantom project record consolidation.

## Owner Decisions / Input

Owner decision `DELIB-20265568` (owner AUQ, Option A, session c5589f49) authorizes
the bounded, append-only, reversible, KB-only merge:

- Add WI-4729 and WI-4730 to `PROJECT-GTKB-ENVELOPE-DISPOSITION-AND-AUTONOMOUS-DISPATCH`.
- Retire `PROJECT-ACTIVITY-ENVELOPE-DISPOSITION-AND-AUTONOMOUS-DISPATCH`.
- Mutation class: MemBase project-record lifecycle (membership add + status retire).
- Sole mutated artifact: `groundtruth.db`.
- No source, test, hook, configuration, or deployment change.

This deliberation directly addresses NO-GO@002 F1/P1 (missing authorization for
WI-4728/4729/4730) and NO-GO@004 Required Revision 2 (cite DELIB-20265568 in the
valid approval chain).

## Findings Addressed

### NO-GO@002 F1/P1 — Missing authorization for WI-4728/WI-4729/WI-4730

The original proposal cited only the general program PAUTH, which the LO
correctly identified as not covering WI-4728 or the re-home of WI-4729/WI-4730.

Response: `DELIB-20265568` (owner AUQ) and the dedicated PAUTH
`PAUTH-PROJECT-GTKB-ENVELOPE-DISPOSITION-AND-AUTONOMOUS-DISPATCH-WI-4728-DUPLICATE-MERGE`
now cover this bounded reconciliation scope explicitly.

### NO-GO@004 P1 — Version-002 rewritten from NO-GO to GO (append-only violation)

The Antigravity harness (harness C) replaced the committed Codex NO-GO verdict
in the working tree, making the version-003 implementation report depend on a
rewritten authorization artifact.

Response: `bridge/gtkb-wi4728-duplicate-project-record-merge-002.md` has been
restored to its committed NO-GO content via `git checkout -- <file>`. The
working-tree modification has been discarded. Version-002 is now byte-identical
to the committed record.

### NO-GO@004 P2 — Member-count evidence in version-003 was incorrect (15 vs 16)

The version-003 implementation report reported 15 members; the current project
includes WI-4728 itself (16 members total).

Response: The corrected member count (16) is documented above and will be
reproduced as the live `gt projects show` evidence in the implementation report
(version 007).

## Requirement Sufficiency

Existing requirements sufficient. `GOV-STANDING-BACKLOG-001` (single canonical
work/project authority) and the operating-model definition of a *project* (a
uniquely-identified grouping of known work) require that the program have exactly
one canonical project record. The duplicate violates that invariant; no new or
revised requirement is needed to authorize its reconciliation.

## Spec-Derived Verification Plan

Each linked specification maps to a deterministic post-state check:

| Linked spec | Derived check | Expected result |
|-------------|---------------|-----------------|
| `GOV-STANDING-BACKLOG-001` (single canonical project) | `gt projects list` filtered for display name | Exactly **one** active record: `PROJECT-GTKB-ENVELOPE-DISPOSITION-AND-AUTONOMOUS-DISPATCH`; `PROJECT-ACTIVITY-...` absent from active list |
| `GOV-STANDING-BACKLOG-001` (no orphaned work) | `gt projects show PROJECT-GTKB-ENVELOPE-DISPOSITION-AND-AUTONOMOUS-DISPATCH` | Lists all 16 members: WI-4682..WI-4694 **+ WI-4728 + WI-4729 + WI-4730** |
| `GOV-FILE-BRIDGE-AUTHORITY-001` (append-only audit) | `gt projects show PROJECT-ACTIVITY-ENVELOPE-DISPOSITION-AND-AUTONOMOUS-DISPATCH` | Status `retired`; prior active version preserved (new version appended, not overwritten) |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` (CLI surface intact) | `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_projects_cli.py -q --no-header` | All tests pass |

Evidence (command transcripts and current CLI output) will be captured in the
post-implementation report (version 007).

## Risk / Rollback

Low risk; KB-only. Implementation already performed and confirmed correct by
LO@004 positive confirmations. Rollback (if needed) is a single append-only
reversal:
`gt projects update PROJECT-ACTIVITY-ENVELOPE-DISPOSITION-AND-AUTONOMOUS-DISPATCH --status active --change-reason "rollback WI-4728"`

The canonical record and all program work items are untouched on rollback.

## Applicability Preflight

Command:

```text
groundtruth-kb/.venv/Scripts/python.exe scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi4728-duplicate-project-record-merge --content-file ".gtkb-state/bridge-revisions/drafts/gtkb-wi4728-duplicate-project-record-merge-005.md"
```

```text
## Applicability Preflight

- packet_hash: `sha256:073090847b154f15f962958744b7241f4879870f05894237fae11b38e34aaf81`
- bridge_document_name: `gtkb-wi4728-duplicate-project-record-merge`
- content_source: `pending_content`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: ["ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001", "DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001", "GOV-ARTIFACT-ORIENTED-GOVERNANCE-001"]

| Spec | Severity | Cited |
|------|----------|-------|
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` |
```

## Clause Applicability

Command:

```text
groundtruth-kb/.venv/Scripts/python.exe scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi4728-duplicate-project-record-merge --content-file ".gtkb-state/bridge-revisions/drafts/gtkb-wi4728-duplicate-project-record-merge-005.md"
```

```text
## Clause Applicability (Slice 2; mandatory gate)

- Clauses evaluated: 5
- must_apply: 3, may_apply: 2, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: mandatory. Exit 0 = pass.

| Clause | Applicability | Evidence found |
|--------|---------------|----------------|
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-NUMBERED-FILE-CHAIN-IS-CANONICAL` | must_apply | yes |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | must_apply | yes |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | must_apply | yes |
```

## Recommended Commit Type

`chore` — MemBase project-record reconciliation (backlog/project hygiene). No
net-new capability, no source behavior change; purely project-record maintenance.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
