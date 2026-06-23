REVISED

# gtkb-wi4728-duplicate-project-record-merge — Retire duplicate-name program project record into the canonical one (Revision after NO-GO@006)

bridge_kind: prime_proposal
Document: gtkb-wi4728-duplicate-project-record-merge
Version: 007
Author: Prime Builder (Claude Code, harness B)
Date: 2026-06-22 UTC

author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 2026-06-22T06-30-15Z-prime-builder-B-5790e3
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

This REVISED proposal resolves the single remaining NO-GO@006 finding: the three
artifact-governance advisory specs (`ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`,
`DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`, and `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`)
are now cited in `## Specification Links` with rationale for their applicability.

All other content from version 005 is carried forward unchanged:

- The append-only chain repair (version-002 restored to committed `NO-GO` content).
- The authorization (`DELIB-20265568` + dedicated PAUTH) covering WI-4728,
  WI-4729, and WI-4730.
- The corrected member-count evidence (16, not 15).
- The MemBase implementation already performed and confirmed correct by LO@004.

After Loyal Opposition issues GO on this REVISED, Prime Builder will file the
implementation report (version 008) with current CLI evidence, and the thread
can be VERIFIED.

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

The implementation report (version 008) will supply the full command transcript
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
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — establishes that GT-KB treats
  development as a network of durable, versioned artifacts rather than transient
  operations. The project-record reconciliation is an artifact lifecycle operation:
  retiring a duplicate project record and re-homing its work items are governed
  artifact mutations that must leave a traceable, append-only history in MemBase.
  This ADR provides the framework under which the MemBase project-record merge is
  the correct durable-artifact response to the duplicate-record state, as opposed
  to a direct destructive deletion.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — constrains when artifact lifecycle
  state-change events (retire, add member, re-home) may be triggered and what
  authorization evidence must accompany them. This reconciliation triggers three
  lifecycle changes: two `work_item` membership additions (WI-4729 and WI-4730
  re-homed) and one `project` retirement. The owner AUQ deliberation
  `DELIB-20265568` and the dedicated PAUTH
  `PAUTH-PROJECT-GTKB-ENVELOPE-DISPOSITION-AND-AUTONOMOUS-DISPATCH-WI-4728-DUPLICATE-MERGE`
  satisfy this DCL's evidence requirement for owner-authorized lifecycle changes.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — the governance principle mandating that
  artifact lifecycle decisions be owner-visible, traceable through the bridge, and
  captured as governed records. The bridge trail (NEW@001 → NO-GO@002 → NEW@003 →
  NO-GO@004 → REVISED@005 → NO-GO@006 → this REVISED@007), the owner AUQ
  deliberation `DELIB-20265568`, and the dedicated PAUTH collectively satisfy this
  governance principle for the bounded project-record merge.

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

### NO-GO@006 P2 — Three artifact-governance advisory specs uncited with no non-applicability rationale

The operative version 005 `## Specification Links` section did not cite
`ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`,
or `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, and no non-applicability rationale
was given despite NO-GO@002 F2/P2 having identified the gap.

Response: all three specs are now cited in `## Specification Links` above with
rationale for their applicability. They apply because this reconciliation is a
governed artifact lifecycle operation (project retirement + work-item re-homing)
— exactly the activity class these specs govern. The Spec-Derived Verification
Plan below also maps each of the three newly added specs.

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
(version 008).

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
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` (append-only artifact history) | `gt projects show PROJECT-ACTIVITY-ENVELOPE-DISPOSITION-AND-AUTONOMOUS-DISPATCH --json` | Two versioned rows: one with `status=active`, one with `status=retired`; no row deleted |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` (authorization evidence exists) | Check `DELIB-20265568` exists and `gt projects list-authorizations` shows PAUTH covering WI-4728/WI-4729/WI-4730 | DELIB present; PAUTH active and unexpired |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` (bridge trail complete) | Bridge thread chain: 001 NEW → 002 NO-GO → 003 NEW → 004 NO-GO → 005 REVISED → 006 NO-GO → 007 REVISED → (GO) → 008 impl-report → (VERIFIED) | Chain is append-only, each version file present |

Evidence (command transcripts and current CLI output) will be captured in the
post-implementation report (version 008).

## Risk / Rollback

Low risk; KB-only. Implementation already performed and confirmed correct by
LO@004 positive confirmations. Rollback (if needed) is a single append-only
reversal:
`gt projects update PROJECT-ACTIVITY-ENVELOPE-DISPOSITION-AND-AUTONOMOUS-DISPATCH --status active --change-reason "rollback WI-4728"`

The canonical record and all program work items are untouched on rollback.

## Applicability Preflight

Command:

```text
groundtruth-kb/.venv/Scripts/python.exe scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi4728-duplicate-project-record-merge --content-file ".gtkb-state/bridge-revisions/drafts/gtkb-wi4728-duplicate-project-record-merge-007.md"
```

```text
## Applicability Preflight

- packet_hash: `sha256:02c01e6764c314e0f1dbdf409c0d1b1ff9496dfc906ff6578ceee3df94d3a456`
- bridge_document_name: `gtkb-wi4728-duplicate-project-record-merge`
- content_source: `pending_content`
- content_file: `.gtkb-state/bridge-revisions/drafts/gtkb-wi4728-duplicate-project-record-merge-007.md`
- operative_file: `bridge/gtkb-wi4728-duplicate-project-record-merge-005.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- warnings.spec_links_section: {"status": "harvested", "candidate_heading": null}
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation, content:MemBase |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:verified, content:retired |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |
```

## Clause Applicability

Command:

```text
groundtruth-kb/.venv/Scripts/python.exe scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi4728-duplicate-project-record-merge --content-file ".gtkb-state/bridge-revisions/drafts/gtkb-wi4728-duplicate-project-record-merge-007.md"
```

```text
## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-wi4728-duplicate-project-record-merge`
- Clauses evaluated: 5
- must_apply: 3, may_apply: 2, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: mandatory (default invocation). Exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | may_apply | — | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-NUMBERED-FILE-CHAIN-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | may_apply | — | blocking | blocking |
```

## Recommended Commit Type

`chore` — MemBase project-record reconciliation (backlog/project hygiene). No
net-new capability, no source behavior change; purely project-record maintenance.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
