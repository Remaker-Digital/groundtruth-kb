ADVISORY
author_identity: loyal-opposition/claude
author_harness_id: B
author_session_context_id: 077da0d1-f51e-43b0-ace9-13eb98da71ab
author_model: claude-opus-5
author_model_version: claude-opus-5
author_model_configuration: Claude Code scheduled task (loyal-opposition-worker); resolved role loyal-opposition via worker session document

# LO Advisory - Project Authorizations Are Never Retired, So 155 Work Items Carry Two Or More Simultaneously Active Authorizations And The Implementing Agent Chooses Which One Governs

bridge_kind: governance_advisory
Document: gtkb-lo-project-authorization-accumulation-and-conflict-advisory
Version: 001
Author: Loyal Opposition (Claude, harness B)
Date: 2026-07-28 UTC

Project: PROJECT-GTKB-HOUSEKEEPING-HARDENING
Work Item: WI-5657

---

## Source

Read-only observation during a scheduled Loyal Opposition queue run, branch
`research`, 2026-07-28 UTC, while reviewing bridge thread
`gtkb-wi5657-terminal-finalization-recovery-v2` version 005.

Trigger: that proposal's acceptance criterion 2 asserts "**The** active PAUTH
resolves to WI-5657 only". Verifying the definite article surfaced a systemic
condition well outside the thread's scope. The thread itself is unaffected and
received `GO`; this advisory does not reopen it.

## Classification Slot

`adopt` - the condition is mechanically confirmed, the harm maps onto an existing
governance specification, and the first step is a non-gating, fully reversible
detection change.

## Claim

Project authorizations are created but effectively never completed or revoked.
576 are currently `status='active'`. 155 work items are covered by two or more
simultaneously active authorizations. In at least one confirmed case the two
active authorizations for the same work item carry **contradictory
forbidden-operation sets**, and nothing in the resolution path detects or
resolves the contradiction: the authorization that governs is whichever one the
proposal author cited by ID.

This converts a control the owner grants - this bounded scope, these mutation
classes, these forbidden operations - into a menu the implementing agent selects
from.

## Evidence

### E1 - Two active authorizations govern WI-5657, with opposed operation sets

```
id: PAUTH-PROJECT-GTKB-HOUSEKEEPING-HARDENING-WI-5657-PROTECTED-COMMIT-CHECKER-
    SUPERSEDED-PREDECESSOR-VERIFIED-FIX
status: active
owner_decision_deliberation_id: DELIB-202667182
allowed_mutation_classes: ["source", "test"]
forbidden_operations: [..., "git_commit", ...]
included_work_item_ids: ["WI-5657"]
expires_at: None

id: PAUTH-PROJECT-GTKB-HOUSEKEEPING-HARDENING-WI5657-TERMINAL-RECOVERY-20260728
status: active
owner_decision_deliberation_id: DELIB-202667519
allowed_mutation_classes: ["bridge", "governance_evidence", "metadata"]
forbidden_operations: [...]            # git_commit NOT present
included_work_item_ids: ["WI-5657"]
expires_at: None
```

One forbids `git_commit`; the other permits it. Both are active. Neither sets
`expires_at`.

### E2 - The first authorization's work is delivered and committed

`git diff-tree --no-commit-id --name-only -r 7b838d9e7606a8b1f8be75ade78881f63beda170`
returns exactly `scripts/check_protected_commit_authorization.py` and
`platform_tests/scripts/test_check_protected_commit_authorization.py` - the whole
`["source","test"]` scope of the predecessor authorization. That authorization has
nothing left to authorize, and remains `active` indefinitely.

### E3 - Resolution is by cited ID only; no conflict check exists

`scripts/implementation_authorization.py:1066` resolves the governing
authorization with:

```sql
SELECT * FROM current_project_authorizations WHERE id = ?
```

using the single ID from the proposal's `Project Authorization:` header. The
validator (`:1275-1335`) then checks that authorization in isolation - active,
unexpired, project match, work item in `included_work_item_ids`, spec exclusions,
operation evaluation. No code path enumerates the *other* active authorizations
covering the same work item, so a stricter concurrent authorization is never
consulted.

The only function that enumerates authorizations by work item is
`_suggest_pauth_for_work_item` (`:1827-1853`), and it is advisory: it feeds error
messages, is capped at `LIMIT 10`, and returns a plain list with no uniqueness or
conflict assertion.

### E4 - The doctor checks under-coverage only

`_active_authorized_work_item_ids`
(`groundtruth-kb/src/groundtruth_kb/project/doctor.py:6633-6644`) **unions** the
work items of all active authorizations to answer "is this open WI authorized?".
`check_standing_backlog_health` (`:6653`) reports orphaned - that is, uncovered -
work items. There is no finding kind for a work item covered by multiple active
authorizations, for an active authorization whose work items are all resolved, or
for conflicting `forbidden_operations` across concurrent authorizations. The
check is structurally incapable of seeing this condition.

### E5 - Retirement commands exist and are unused

`gt projects complete-authorization` and `gt projects revoke-authorization` are
both implemented and documented in `gt projects --help`. With 576 active and 155
work items multiply-covered, neither is part of routine terminal verification.
The mechanism is present; nothing requires or prompts its use.

### E6 - Scale

```
active PAUTH count: 576
work items covered by >1 active PAUTH: 155
maximum concurrent authorizations on one work item: 4 (GTKB-CORE-001)
```

## Deficiency Rationale

Three harms, in increasing severity.

**Audit ambiguity (P3).** A verifier asked to confirm "the governing
authorization permits this operation" cannot answer from the work item alone. Any
proposal that says "the active PAUTH" is underspecified whenever more than one is
active, which is now true for 155 work items. This is not hypothetical: it is
what made acceptance criterion 2 of the reviewed thread imprecise.

**Erosion of bounded scope (P2).** An owner authorization exists to bound what an
agent may do for a work item. When a completed authorization stays active
forever, its grants stay live forever. Any later proposal on the same work item
may cite the older authorization and inherit mutation classes the owner granted
for different, already-finished work. In the WI-5657 case, the stale
authorization still grants `source` and `test` for work delivered in July.

**Authority selection by the authorized party (P2).** Because resolution keys on
the cited ID and no conflict check runs, the implementing agent chooses which of
several live authorizations governs its own work. In the confirmed case the two
sets are disjoint rather than nested, so this is not yet
pick-the-most-permissive - but nothing in the design prevents the nested case,
and with 4-way coverage already present it is a matter of time. This is precisely
the class of defect `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` exists to
prevent.

Note the compounding factor: none of the 576 sets `expires_at`, so the population
is monotonically increasing. Every authorization ever granted is still granted.

## Recommended Prime Action

Ordered by risk and reversibility; all additive.

1. **Doctor check - detect the condition (lowest risk, do first).** Add a
   `check_project_authorization_hygiene` finding set:
   - WARN: work item covered by more than one active authorization.
   - FAIL: work item covered by more than one active authorization whose
     `forbidden_operations` sets differ - a contradiction, not merely a
     duplication.
   - WARN: active authorization whose `included_work_item_ids` are all resolved -
     a completion candidate.

   This surfaces the population without changing any gate and gives the eventual
   cleanup a measurable target.
2. **Terminal-verification completion prompt.** At terminal `VERIFIED`, prompt or
   require `gt projects complete-authorization` for the cited authorization when
   its work items are resolved. This closes the source of new accumulation before
   attempting to drain the existing 576.
3. **Conflict resolution at `begin`.** When the cited authorization is one of
   several active authorizations covering the work item, either (a) fail closed
   and require the owner to complete or revoke the others, or (b) evaluate
   requested operations against the **intersection** of all active
   authorizations' permissions.
4. **Backfill.** Bulk `complete-authorization` for authorizations whose work
   items are all resolved.

**Option rationale.** (1) before (3) is deliberate and not merely cautious.
Option 3(a) is the conceptually correct fix - an owner authorization should be
unambiguous - but applied today it would immediately block work on 155 work
items, including live threads, with no prepared remediation path. Option 3(b)
preserves forward motion but silently changes what an authorization *means*
(from "this grant" to "this grant, intersected with every other live grant"),
which is an owner decision rather than an implementation detail. Detection first
converts an invisible condition into a measured one and lets the owner choose
between them against real numbers. Recommendation 4 should not precede 2, or the
population will simply refill.

## Required Prime Builder Owner-Grilling Gate

### Implementation implied

Yes. (1) mutates `groundtruth-kb/src/groundtruth_kb/project/doctor.py` plus a
test; (2) the verification/finalization helper path; (3)
`scripts/implementation_authorization.py`; (4) bulk MemBase authorization
completion.

### Grill-the-owner questions

Prime Builder must obtain durable AskUserQuestion-recorded answers to:

1. **First-slice scope.** Detection only (recommendation 1), or detection plus the
   terminal-verification completion prompt (1 + 2)? Detection only is the
   smaller, fully reversible step.
2. **Severity calibration.** Should "work item covered by more than one active
   authorization with differing `forbidden_operations`" be FAIL or WARN? FAIL
   turns the doctor red immediately against a known-large population; WARN risks
   being ignored. This is an owner tolerance decision, not a technical one.
3. **Conflict semantics.** If (3) is pursued, is the rule fail-closed or
   intersection-of-permissions? This changes what an owner authorization *means*
   and must not be chosen by an agent.
4. **Backfill authority.** Is bulk `complete-authorization` of the roughly 500
   stale-active authorizations in scope? If so, per-item owner review or a batch
   decision? Note the GOV-15 fix-approval gate and the 50-item batch maximum
   enforced by the `gtkb-batch` surface.
5. **Expiry policy.** Should new authorizations carry a default `expires_at`?
   None of the 576 has one. This would prevent recurrence but changes the
   authorization contract for all future work.

### Required durable owner decisions

- First-slice scope (detection only vs. detection plus completion prompt).
- Doctor severity for the conflicting-authorization finding.
- Whether conflict resolution at `begin` is in scope, and if so which semantics.
- Whether backfill is authorized, and under what batch discipline.

## Specification Links

- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `GOV-PROJECT-REQUIRES-LINKED-SPECIFICATIONS-001`
- `GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001`
- `GOV-STANDING-BACKLOG-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`

## Prior Deliberations

- `DELIB-202667182` - owner authorization for the original WI-5657 checker fix;
  the source of the stale active authorization documented at E1/E2.
- `DELIB-202667519` - owner authorization for the WI-5657 terminal recovery; the
  second, concurrently active authorization on the same work item.
- `DELIB-202667520` - owner disposition continuing the v2 recovery chain; the
  review that surfaced this observation.
- `DELIB-202667318` - prior Loyal Opposition NO-GO on WI-5602 concerning a
  governance-gate cleanup that cited a stale authorization reference; the closest
  existing precedent that authorization citation hygiene is a reviewable
  property.

## Prime Builder Implementation Context

| Element | Detail |
| --- | --- |
| Objective | Make concurrent and stale project authorizations detectable, then decide with the owner how to constrain them. |
| Preconditions | Owner-grilling gate answers recorded via AskUserQuestion. No existing authorization covers this work. |
| Evidence paths | `scripts/implementation_authorization.py:1066`, `:1275-1335`, `:1827-1853`; `groundtruth-kb/src/groundtruth_kb/project/doctor.py:6633-6690`; MemBase `current_project_authorizations`. |
| File touchpoints | `groundtruth-kb/src/groundtruth_kb/project/doctor.py` plus a test for slice 1. Later slices touch the finalization helper and `scripts/implementation_authorization.py`. |
| Implementation sequence | (1) Add the three findings to a new doctor check. (2) Add a test fixture with two conflicting active authorizations on one work item and assert FAIL. (3) Report the live population as evidence in the implementation report. |
| Verification steps | Run the new check against the live database and confirm it reports 155 multiply-covered work items and flags the WI-5657 pair as conflicting. Confirm no existing doctor check changes verdict. |
| Rollback notes | Detection-only slice is additive and non-gating; revert is a single check removal. Do not begin backfill in the same slice. |
| Open decisions | All five grilling questions above. |

## Owner Decision Needed

None from this advisory. It records a condition and proposes future work.

## Commands Executed

```powershell
gt projects --help
git diff-tree --no-commit-id --name-only -r 7b838d9e7606a8b1f8be75ade78881f63beda170
```

Read-only MemBase access via `sqlite3` over `groundtruth.db`:
`SELECT id,version,status,project_id,authorization_name,
owner_decision_deliberation_id,allowed_mutation_classes,forbidden_operations,
included_work_item_ids,expires_at FROM current_project_authorizations
WHERE included_work_item_ids LIKE '%5657%' OR id LIKE '%5657%'`; and
`SELECT id,status,included_work_item_ids,allowed_mutation_classes
FROM current_project_authorizations WHERE status='active'` with in-process
aggregation of the multiply-covered counts.

Read-only source inspection: `scripts/implementation_authorization.py`
(lines 1060-1090, 1275-1335, 1820-1860);
`groundtruth-kb/src/groundtruth_kb/project/doctor.py` (lines 6612-6690).

No repository file was modified by this observation other than the creation of
this advisory artifact through the governed bridge writer.

## Skills applied

- gtkb-bridge
- gtkb-advisory-proposal
- gtkb-lo-opportunity-radar

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
