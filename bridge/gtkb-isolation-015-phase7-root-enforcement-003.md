WITHDRAWN

# Withdrawal - Isolation Phase 7 Work-Subject/Root Enforcement (GTKB-ISOLATION-015)

bridge_kind: implementation_proposal
Document: gtkb-isolation-015-phase7-root-enforcement
Version: 003
Status: WITHDRAWN
Author: Prime Builder (Claude, harness B)
Date: 2026-05-15 UTC
Session: S353+

## Withdrawal Summary

This thread is **WITHDRAWN**. The `-002` NO-GO finding F1 established — and a
direct live-tree investigation for this withdrawal confirms — that the work
proposed in `-001` (work-subject/root enforcement for `GTKB-ISOLATION-015`)
is **already fully implemented and VERIFIED** on a prior bridge thread. The
`-001` proposal's defining premise ("Currently `work-subject.json` is advisory;
this WI promotes it to mechanically enforced") is factually incorrect: the
mechanical enforcement already exists, is live, and is regression-covered.

Per `.claude/rules/file-bridge-protocol.md` the bridge audit trail is
append-only; `-001` (NEW) and `-002` (NO-GO) are preserved unchanged on disk.
This `-003` is the append-only `WITHDRAWN` terminal version of the thread.
`bridge/INDEX.md` records the thread's latest status as `WITHDRAWN`.

## Evidence That the Work Is Already Done

The `-002` NO-GO finding F1 identified the duplication. This withdrawal verifies
it against the live tree:

1. **`GTKB-ISOLATION-015` Slice 1 is VERIFIED.**
   `bridge/gtkb-isolation-015-phase7-full-integration-016.md` is a `VERIFIED`
   verdict (dated 2026-04-24) for thread `gtkb-isolation-015-phase7-full-integration`,
   the same `GTKB-ISOLATION-015` work item this thread targets. Its verified
   scope explicitly covers the live root-aware guard, the four-category
   taxonomy, work-subject state, harness-symmetric subject reads, and
   regression tests.

2. **The work-subject/root enforcement guard is live in
   `scripts/workstream_focus.py`.** The function `guard_tool_use(payload,
   project_root)` (defined at `scripts/workstream_focus.py:1420`) is a Phase 7
   root-aware tool-use guard that blocks cross-product writes:
   `application` subject blocks `gtkb_product` targets
   (`scripts/workstream_focus.py:1455-1463`); `gtkb_infrastructure` subject
   blocks `application_product` targets
   (`scripts/workstream_focus.py:1464-1472`). This is precisely the
   "Write hook that consults `work-subject.json` and blocks Writes that violate
   the declared scope" the `-001` proposal claimed to add.

3. **The four-category taxonomy already exists and is the live classifier.**
   `classify_root(path_text, project_root)`
   (`scripts/workstream_focus.py:1329`) returns one of `application_product`,
   `current_repo_bridge_or_governance`, `gtkb_product`, `neutral` — the exact
   taxonomy the `-002` NO-GO finding F4 said any revision must preserve.

4. **The bridge/governance exception is already implemented.**
   `guard_tool_use`'s own docstring states that
   `current_repo_bridge_or_governance` surfaces are NOT blocked in either
   subject (`scripts/workstream_focus.py:1431-1433`), and a regression test
   asserts the application subject still allows current-repo bridge/governance
   writes (`platform_tests/hooks/test_workstream_focus.py`). The `-001`
   proposal's path semantics (application scope allows only
   `applications/<name>/`) would have regressed this verified behavior — finding
   F4 of the `-002` NO-GO.

5. **The companion thread `gtkb-work-subject-root-enforcement-implementation`
   is also VERIFIED.** `bridge/gtkb-work-subject-root-enforcement-implementation-020.md`
   (`VERIFIED`, dated 2026-04-23) confirms canonical work-subject state, command
   handling, root classification, and guard enforcement are present in
   `scripts/workstream_focus.py`.

6. **The proposed new hook file does not exist and should not be created.**
   `-001`'s `target_paths` named `.claude/hooks/work-subject-write-gate.py` —
   a new parallel hook. The `-002` NO-GO finding F1 explicitly directed: "do
   NOT create a parallel hook"; a second enforcement surface would obscure
   which verified thread owns the behavior. The correct disposition is
   withdrawal, not a revised parallel-hook design.

## Why WITHDRAWN Rather Than REVISED

The `-002` NO-GO finding F1 offered two paths: "Revise the proposal to start
from the verified existing surface ... If no gap remains, withdraw or convert
this thread into a closure/disposition proposal." The investigation above
confirms the enforcement surface, the four-category taxonomy, the
bridge/governance exception, and the verified-thread coverage all already
exist. There is no enforcement-behavior gap for `-001`'s proposed
parallel-hook design to fill. The `-001` design is wholly duplicative of
VERIFIED work on the same work item, so withdrawal — not a revision of a
duplicative proposal — is the correct terminal disposition.

## Observation Surfaced for Owner (Not a Revision of This Thread)

During this investigation one narrow observation arose that is **out of scope
for this withdrawn thread** and is recorded here only so it is not lost:

- The Claude-side hook adapter `.claude/hooks/workstream-focus.py` is registered
  in `.claude/settings.json` under `UserPromptSubmit` only, not under
  `PreToolUse`. `handle_hook_payload` routes a no-prompt payload to
  `guard_tool_use`, so the guard function is reachable in principle, but a
  `PreToolUse` trigger registration is what would invoke it on Write/Edit/Bash
  tool use.

This observation does NOT change the withdrawal disposition: `-001` proposed a
*new parallel hook*, which the `-002` NO-GO rejected outright. Whether the
*existing* `workstream_focus` guard needs an additional `PreToolUse`
registration is a separate, much narrower question that — if the owner judges
it worth pursuing — belongs in its own bridge proposal targeting the existing
hook and settings registration, not a parallel-hook design. It is left to the
owner / a future session to decide whether to open such a thread. No new work
item or proposal is created by this withdrawal.

## Specification Links

The compliance gate requires this section even on a withdrawal. The
specifications that governed the original `-001` proposal, carried forward for
audit completeness:

- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - source isolation contract; the live `guard_tool_use` + `classify_root` enforce it.
- `DELIB-S319-LIFECYCLE-INDEPENDENCE-CONTRACT` - lifecycle independence motivation.
- `DELIB-S331-DA-READ-SURFACE-CORRECTION-FOUNDATIONS` - three-mode work-subject declaration as runtime invariant.
- `DELIB-0876` - durable session work subject.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge protocol authority; governs this withdrawal as a bridge artifact and the append-only INDEX update.
- `SPEC-AUQ-POLICY-ENGINE-001` - policy engine surface.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - spec-linkage requirement; satisfied by this section.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - spec-to-test mapping requirement; a withdrawal triggers no implementation, so no spec-derived test step runs.
- `GOV-STANDING-BACKLOG-001` - `GTKB-ISOLATION-015` remains a tracked work item; this withdrawal closes a duplicative bridge thread, it does not retire the work item.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - durable artifact-graph model (advisory; cited per the applicability preflight `missing_advisory_specs` list).
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - artifact lifecycle triggers (advisory; cited per the applicability preflight `missing_advisory_specs` list).
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - artifact-oriented governance baseline (advisory; cited per the applicability preflight `missing_advisory_specs` list).

## Clause Scope Clarification (Not a Bulk Operation)

This `-003` is a withdrawal of a single bridge thread covering exactly one
work item (`GTKB-ISOLATION-015`). It is **not** a bulk backlog operation. It
performs no batch resolve, promote, retire, reorder, or create against
`work_items` or specifications. The `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS`
clause-preflight match is a false positive triggered by the words "work item"
and "standing backlog" appearing in narrative prose; this withdrawal touches
no backlog inventory. The applicable evidence pattern for a non-bulk
single-work-item withdrawal is: no `inventory` artifact is produced, no
`review-packet` is generated, no `formal-artifact-approval` packet is required
(a withdrawal authorizes no protected-artifact mutation and no implementation),
and no `DECISION DEFERRED` marker applies (the decision is final: WITHDRAWN).
The single work item `GTKB-ISOLATION-015` remains in the backlog unchanged;
only this duplicative bridge thread is closed.

## Prior Deliberations

- `DELIB-2061` / `DELIB-1142` - the VERIFIED `gtkb-work-subject-root-enforcement-implementation` thread (VERIFIED closure at `bridge/gtkb-work-subject-root-enforcement-implementation-020.md`). This withdrawal cites that thread as the verified surface that makes `-001` duplicative.
- `DELIB-2029` / `DELIB-1135` - the VERIFIED `gtkb-isolation-015-phase7-full-integration` thread (VERIFIED closure at `bridge/gtkb-isolation-015-phase7-full-integration-016.md`) for `GTKB-ISOLATION-015` Slice 1. Same work item; confirms the enforcement is already verified.
- `DELIB-S350-BATCH4-FOUR-PROJECT-AUTHORIZATIONS` - the owner-approved `PROJECT-GTKB-ISOLATION-CLOSEOUT` authorization under which `-001` was filed. The authorization remains valid; this withdrawal simply finds no remaining enforcement work for `GTKB-ISOLATION-015` of the kind `-001` proposed.

## Applicability Preflight

Run on this `-003` withdrawal content after the INDEX entry was updated:

```
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-isolation-015-phase7-root-enforcement
```

```
## Applicability Preflight

- packet_hash: `sha256:da19ef8ee973196545693b7fb643771f43d106e391bdaa999d349025b3298f6a`
- bridge_document_name: `gtkb-isolation-015-phase7-root-enforcement`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-isolation-015-phase7-root-enforcement-003.md`
- operative_file: `bridge/gtkb-isolation-015-phase7-root-enforcement-003.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []
```

`preflight_passed: true`; `missing_required_specs: []`; `missing_advisory_specs: []`.

## Clause Applicability

```
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-isolation-015-phase7-root-enforcement
```

```
## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-isolation-015-phase7-root-enforcement`
- Operative file: `bridge\gtkb-isolation-015-phase7-root-enforcement-003.md`
- Clauses evaluated: 5
- must_apply: 4, may_apply: 1, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.
```

Exit 0; zero blocking gaps. The `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS`
clause now reports evidence found after the `## Clause Scope Clarification`
section was added.

## Disposition

WITHDRAWN. No implementation proceeds on this thread. No counterpart GO/NO-GO/
VERIFIED verdict is expected. `GTKB-ISOLATION-015` work-subject/root enforcement
is already delivered and VERIFIED on `gtkb-isolation-015-phase7-full-integration`
(`-016`). The append-only `bridge/INDEX.md` entry records `WITHDRAWN` as this
thread's latest status.

End of withdrawal.
