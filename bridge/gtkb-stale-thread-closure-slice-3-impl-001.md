NEW
author_identity: Claude Code Prime Builder
author_harness_id: B
author_session_context_id: 1fdfef13-fddf-431a-b209-94b9301ef3b9
author_model: Opus 4.7 (1M context)
author_model_version: claude-opus-4-7[1m]
author_model_configuration: Claude Code CLI default reasoning

# Stale Bridge Thread Closure - gtkb-claude-md-scope-clarification-slice-3-implementation

bridge_kind: governance_review
target_paths: ["groundtruth.db", "bridge/gtkb-claude-md-scope-clarification-slice-3-implementation-011.md", "bridge/INDEX.md"]

Document: gtkb-stale-thread-closure-slice-3-impl
Version: 001 (NEW)
Date: 2026-05-31 UTC

## Summary

Close one stale bridge thread by procedurally terminating it via WITHDRAWN status, and resolve the orphaned MemBase work item it nominally tracks. The underlying Slice 3 implementation work was settled out-of-protocol in S378 via commit `f91dbebb` (owner-confirmed working-tree settlement; the original authoring bridge thread is "archived and unrecoverable" per the commit body). The thread `gtkb-claude-md-scope-clarification-slice-3-implementation` currently sits at `NO-GO @-010` and never received a closure or VERIFIED, so it persists on Prime's actionable bridge surface as a false-positive. `WI-3438` is `open` despite the underlying work being committed.

This proposal applies the established precedent pattern from `gtkb-completed-bridge-wi-hygiene-2026-05-13` (VERIFIED at `-008`, archived as `DELIB-2115`) and uses the protocol's native `WITHDRAWN` terminal status to remove the thread from the actionable surface without claiming a verification the bridge protocol never performed.

**bridge_kind: governance_review** is used (rather than `prime_builder_proposal` per the precedent) because the cited PAUTH for the underlying project is `completed` and the cited project is `retired`; the standard implementation-proposal project-linkage metadata gate hard-blocks the file write under that condition. The `governance_review` classification is the appropriate non-implementation-proposal classification per the `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001/CLAUSE-PROJECT-METADATA-PRESENT` gate's escape valves; the operation IS a review and correction of governance state (the disagreement between MemBase `work_items.resolution_status` and the committed reality, plus the actionable-surface-false-positive on the stuck NO-GO thread).

Scope is deliberately bounded to a single thread + a single WI for this session. A larger inventory exists (49 open WIs in retired projects per the catalog described in Inventory below) but is out of scope for this proposal; the doubled-prefix subclass of that population has separate tooling (`gt projects reconcile-doubled-prefix`) and the single-prefix subclass deserves a separate batch proposal that the owner can scope deliberately.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - live bridge index authority. This proposal adds a `NEW` line for this document at the top of `bridge/INDEX.md`. Post-GO it will add a `WITHDRAWN` line for `gtkb-claude-md-scope-clarification-slice-3-implementation-011.md` at the top of that existing document's entry. No prior versions are deleted or rewritten; append-only chains preserved.
- `GOV-08` - KB is truth. `WI-3438`'s `resolution_status` field currently disagrees with reality (the work is committed at `f91dbebb`). This proposal updates MemBase to reflect ground truth.
- `GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001` (v4) - VERIFIED-Driven Project Completion and Retirement Are Automatic. The v3 trigger fired twice on `PROJECT-GTKB-CLAUDE-MD-SCOPE-CORRECTION` (auto-retired at v2 + v4 of the project record), leaving `WI-3438` orphaned because the trigger does not propagate to child WI lifecycle fields. Closing the orphan completes the cycle the trigger left open.
- `GOV-STANDING-BACKLOG-001` - standing backlog as durable cross-session work authority. This proposal performs a single-WI state transition; owner-AUQ evidence in the Owner Decisions / Input section satisfies `CLAUSE-VISIBILITY-BULK-OPS` (operative even for single-row transitions, per precedent).
- `GOV-15` - test fix approval gate. Out of scope: `WI-3438` has `origin=new` (not `defect`/`regression`), so the GOV-15 gate does not fire. Confirmed by live query at draft time.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this Specification Links section enumerates linkage. The Spec-Derived Verification Plan section below provides the spec-to-test mapping. The `CLAUSE-PROJECT-METADATA-PRESENT` gate's escape valve to `bridge_kind: governance_review` is invoked per the Summary section above.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the Spec-Derived Verification Plan below lists executable verifications and the post-impl report will include spec-to-test mapping with executed evidence.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - durable artifact graph preserved. The WITHDRAWN entry preserves the audit trail (the NO-GO at -010 and the prior version chain remain on disk); WI-3438's state change is append-only versioned per MemBase semantics.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - artifact lifecycle transitions. `WI-3438` transitions open -> resolved; the bridge thread transitions NO-GO -> WITHDRAWN; both transitions follow established terminal-state semantics.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` (advisory) - artifact-oriented baseline preserved.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - in-root placement. All in-scope file paths reside under the GT-KB root `E:\GT-KB\` (in-root): the bridge proposal file itself lives at `E:\GT-KB\bridge\gtkb-stale-thread-closure-slice-3-impl-001.md`; the planned WITHDRAWN file lives at `E:\GT-KB\bridge\gtkb-claude-md-scope-clarification-slice-3-implementation-011.md`; the MemBase file is `E:\GT-KB\groundtruth.db`; and `bridge/INDEX.md` is `E:\GT-KB\bridge\INDEX.md`. No application-side placement is implicated by this proposal (the bridge thread being closed concerned Agent Red application files, but this proposal does not itself touch any `applications/` path).
- `ADR-0001` (Three-Tier Memory Architecture) - structural reference. Architecture concept referenced across the project; not formalized as a MemBase row (pre-existing project-wide gap unrelated to this proposal; queued as separate hygiene task in this session).

## Prior Deliberations

- `DELIB-2115` - `gtkb-completed-bridge-wi-hygiene-2026-05-13` (VERIFIED at `-008`). The most directly applicable precedent: a 6-WI batch closure of stale work items whose bridge threads were terminal. This proposal applies the same template (bridge_kind escape, target_paths, AUQ evidence pattern) at single-WI scope, adapted to use `governance_review` bridge_kind because the gate landscape has tightened since the precedent.
- `DELIB-0573` - Bridge Closure-Starvation Root Cause. Documents the broader class of bridge-closure friction.
- `DELIB-1155` - `bridge-spawn-revalidation` (10 versions, ORPHAN). Establishes that ORPHAN classification is a recognized terminal state for threads not in active INDEX.
- `DELIB-1916` - `gtkb-codex-backlog-cleanup-retroactive-review` (VERIFIED). Precedent that retroactive backlog cleanup of work items not closed when underlying work completed is a legitimate bridge-mediated operation.
- `DELIB-1918` - `gtkb-governance-hygiene-bundle` (VERIFIED). Multi-item governance hygiene bundle precedent.
- `DELIB-1973` - `gtkb-phantom-index-cleanup-2026-04-30` (VERIFIED). Parallel hygiene work (bridge-side phantom cleanup); same family of "state diverged from reality" problem.
- `DELIB-S346-SPEC-CREATION-SCOPED-BATCH-AUTHORIZATION` - scoped batch authorization pattern via AskUserQuestion.

## Owner Decisions / Input

This proposal proceeds under explicit owner approval collected via `AskUserQuestion` in this session (S379, 2026-05-31):

- **AUQ 1** (priority list pick): "Which project should I start on first?" Answer: "Tier 2 #7 - CLAUDE.md scope correction (1 WI)". This selected WI-3438 as the work focus for this session.
- **AUQ 2** (corrected scope): "Given the corrected scope (recovery from NO-GO @-010 on an already-implemented slice; needs REVISED post-impl report -011), what's your call?" Answer: "Proceed - author REVISED -011". This authorized the work; the subsequent hard-block by the bridge-compliance gate (citing stale PAUTH state) revealed the work was already done, prompting AUQ 3.
- **AUQ 3** (close-out path): "Given Slice 3 is already shipped (f91dbebb) and the bridge thread is stale, what's the right close-out?" Answer: "Investigate a clean-closure pattern for stale bridge threads". This authorized the design-and-propose path that this proposal implements.
- **AUQ 4** (closure scope): "What scope should the closure proposal cover?" Answer: "Just WI-3438 + close the slice-3-implementation thread". This bounded the proposal to single-thread + single-WI scope.

All four AUQ answers were collected via the `AskUserQuestion` tool (`detected_via: ask_user_question`); no prose decision-asks involved. This evidence satisfies the AUQ-only enforcement contract per `.claude/rules/prime-builder-role.md` "AskUserQuestion as the Only Valid Owner-Decision Channel" and the bridge-compliance-gate requirement for substantive Owner Decisions / Input section content.

## Requirement Sufficiency

Existing requirements sufficient. No new specification, ADR, DCL, GOV, or PB creation needed. This proposal performs a state-correction operation against MemBase + a procedural bridge-thread termination using the protocol's native `WITHDRAWN` status. All controlling specifications are pre-existing.

## Inventory (Bulk-Ops Visibility)

Live evidence captured 2026-05-31 from `groundtruth.db` (read-only query) and `bridge/` filesystem:

| WI | Origin | Component | Priority | Bridge Thread | Latest INDEX Status | Settlement Evidence |
|---|---|---|---|---|---|---|
| WI-3438 | new | governance | P1 | gtkb-claude-md-scope-clarification-slice-3-implementation | NO-GO @-010 (2026-05-29) | commit `f91dbebb` (2026-05-31, S378); owner-confirmed working-tree settlement per commit body |

Out-of-scope context (informational; not addressed by this proposal): live query at draft time identified 49 open WIs whose cited project is currently retired, across approximately 12 distinct retired projects. Approximately half are under doubled-prefix `PROJECT-PROJECT-*` projects with separate tooling (`gt projects reconcile-doubled-prefix`). The remaining single-prefix stale WIs are candidates for a future batch closure proposal owner-scoped separately.

## Implementation Plan

After Codex GO on this proposal:

1. Run `python scripts/implementation_authorization.py begin --bridge-id gtkb-stale-thread-closure-slice-3-impl` to create the implementation-start packet (per `.claude/rules/codex-review-gate.md`).
2. Update `WI-3438` row in MemBase via governed CLI (no raw `db.insert_*` per `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` discipline). Specifically: `python -m groundtruth_kb backlog update WI-3438 --resolution-status resolved --stage resolved --change-reason "Slice 3 implementation settled out-of-protocol per commit f91dbebb (S378 working-tree settlement); original authoring bridge thread archived and unrecoverable per owner statement in commit body. Bridge thread procedurally withdrawn at -011 per gtkb-stale-thread-closure-slice-3-impl GO."`. If the `gt backlog update` CLI surface lacks one of these flags, fall back to the smallest governed equivalent (e.g., `gt backlog resolve WI-3438 ...`) and document the exact CLI used in the post-impl report.
3. Write `bridge/gtkb-claude-md-scope-clarification-slice-3-implementation-011.md` with the following header and body:
   - First line: `WITHDRAWN`
   - Required `author_*` audit metadata lines per the owner emergency audit directive 2026-05-19 (preserved from this proposal's own header pattern)
   - `bridge_kind: closure`
   - NO `Project Authorization` / `Project` / `Work Item` header metadata lines (the cited PAUTH-V2 is completed; per `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001/CLAUSE-PROJECT-AUTH-LIVE-CHECK` the gate refuses citations of non-active PAUTH; the WITHDRAWN entry is a procedural close-out and does not require PAUTH citation per the `bridge_kind: closure` terminal classification per `notify.py` lines 86-95). If the gate fires on the WITHDRAWN write, fall back to `bridge_kind: governance_review` on the WITHDRAWN entry as well and document the substitution.
   - Body cites: `f91dbebb` commit, S378 owner statement, the NO-GO `-010` findings (F1 and F2 as historical record of why the thread did not reach VERIFIED), this proposal as the authorizing thread, and `DELIB-2115` as the precedent template.
4. Update `bridge/INDEX.md`: insert `WITHDRAWN: bridge/gtkb-claude-md-scope-clarification-slice-3-implementation-011.md` at the top of the existing `gtkb-claude-md-scope-clarification-slice-3-implementation` document entry; no other lines in that entry modified.
5. Run the Spec-Derived Verification Plan commands (below) and collect evidence.
6. File the post-implementation report for Codex VERIFIED review.

## Spec-Derived Verification Plan

Per `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`, all spec-derived verification commands the implementation report will execute. All commands below are repo-venv Python or rg or `gt` CLI surfaces (Windows / PowerShell-valid):

| # | Verification | Spec Coverage | Command | Expected |
|---|---|---|---|---|
| V1 | WI-3438 resolution_status terminal | GOV-08 | `python -c "import sqlite3; c=sqlite3.connect('E:/GT-KB/groundtruth.db'); r=c.execute('SELECT resolution_status, stage FROM work_items WHERE id=\"WI-3438\" AND version=(SELECT MAX(version) FROM work_items WHERE id=\"WI-3438\")').fetchone(); print(r)"` | resolution_status = `'resolved'` (or other terminal value); stage = `'resolved'` (or other terminal value) |
| V2 | WI-3438 change_reason cites f91dbebb | GOV-08 + ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 | `python -c "import sqlite3; c=sqlite3.connect('E:/GT-KB/groundtruth.db'); r=c.execute('SELECT change_reason FROM work_items WHERE id=\"WI-3438\" AND version=(SELECT MAX(version) FROM work_items WHERE id=\"WI-3438\")').fetchone(); print(r[0])"` | output contains `f91dbebb` |
| V3 | -011 file written | GOV-FILE-BRIDGE-AUTHORITY-001 | `python -c "from pathlib import Path; print(Path('bridge/gtkb-claude-md-scope-clarification-slice-3-implementation-011.md').exists())"` | `True` |
| V4 | -011 status is WITHDRAWN | GOV-FILE-BRIDGE-AUTHORITY-001 | `python -c "print(open('bridge/gtkb-claude-md-scope-clarification-slice-3-implementation-011.md').readline().strip())"` | `WITHDRAWN` |
| V5 | -011 bridge_kind is closure or governance_review | GOV-FILE-BRIDGE-AUTHORITY-001 + notify.py terminal classification | `rg "^bridge_kind:\s*(closure|governance_review)" bridge/gtkb-claude-md-scope-clarification-slice-3-implementation-011.md` | match found (exit 0); preferred match is `closure`; `governance_review` accepted only if the gate forces substitution and the substitution is documented in the post-impl report |
| V6 | INDEX updated with WITHDRAWN line at top of slice-3-impl entry | GOV-FILE-BRIDGE-AUTHORITY-001 | `python -c "import re; t=open('bridge/INDEX.md').read(); m=re.search(r'Document: gtkb-claude-md-scope-clarification-slice-3-implementation\n([A-Z\\-]+): bridge/gtkb-claude-md-scope-clarification-slice-3-implementation-(\\d+)\\.md', t); print(m.group(1), m.group(2))"` | `WITHDRAWN 011` |
| V7 | Actionable surface no longer flags slice-3-impl thread for Prime | GOV-FILE-BRIDGE-AUTHORITY-001 + notify.py terminal-kind filtering | `python -c "from groundtruth_kb.bridge.detector import parse_index; from groundtruth_kb.bridge.notify import compute_actionable_pending; from pathlib import Path; t=open('bridge/INDEX.md').read(); pr=Path('E:/GT-KB'); p=parse_index(t, project_root=pr); ap,ac=compute_actionable_pending(p, project_root=pr); print([i.document_name for i in ap if 'slice-3-implementation' in i.document_name])"` | empty list `[]` |

## Risk / Rollback

- **Risk: governed CLI does not expose the exact flag combination assumed in step 2.** Mitigation: the post-impl report documents the exact CLI surface used (probe pre-mutation via `python -m groundtruth_kb backlog update --help`); if the canonical surface differs, use the closest governed equivalent without falling back to raw db calls. Worst case: a small REVISED if Codex flags the substitution.
- **Risk: bridge-compliance gate blocks the WITHDRAWN file write.** Mitigation: omit Project Authorization / Project / Work Item header lines per the precedent pattern; use `bridge_kind: closure` first, fall back to `governance_review` and document the substitution if needed. Probe before assuming - if the gate blocks, the failure mode is loud and recoverable.
- **Risk: notify.py terminal-kind classifier does not extract `bridge_kind` from the WITHDRAWN file as expected.** Mitigation: the WITHDRAWN status itself is non-actionable per `notify.py` lines 76 and 327 (`VERIFIED / ADVISORY / DEFERRED / WITHDRAWN top status -> excluded`) independent of bridge_kind classification. V7 verifies the practical outcome regardless of classification path.
- **Rollback if NO-GO**: no MemBase mutations performed pre-GO; no files written pre-GO. If NO-GO arrives post-implementation: revert WI-3438 via append-only new version restoring open state; rename `-011` to `-011-WITHDRAWN-ATTEMPTED.md` and add a REVISED-1 on this thread describing the corrected approach.

## Owner Action Required

None for this NEW. Awaiting Codex GO at `-002` (or NO-GO with findings).

After Codex GO:
1. Prime Builder runs the Implementation Plan steps 1-4.
2. Prime Builder runs the Spec-Derived Verification Plan and collects evidence.
3. Prime Builder files post-implementation report at `-003` (or appropriate version) for Codex VERIFIED review.

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
