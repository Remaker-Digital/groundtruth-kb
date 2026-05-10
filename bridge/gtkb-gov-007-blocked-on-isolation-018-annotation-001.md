# GTKB-GOV-007 Backlog Annotation — Blocked on GTKB-ISOLATION-018

**Document:** `gtkb-gov-007-blocked-on-isolation-018-annotation`
**Status:** `NEW`
**Date:** 2026-05-10
**Author:** Prime Builder (Claude Code, harness B)
**Bridge kind:** implementation_proposal
**Recommended commit type:** `chore:` (governance hygiene; one annotation update; no new capability)

## Goal

Update the GTKB-GOV-007 entry in `memory/work_list.md` to record that the work item is blocked on GTKB-ISOLATION-018 (the Agent Red git-boundary + relocation program). This prevents future sessions from picking GTKB-GOV-007 as actionable while the underlying NO-GO bridge threads cite implementation paths that would violate `.claude/rules/project-root-boundary.md` Rule 3 if revised in place.

The annotation is metadata only. It does NOT close, retire, or reclassify GTKB-GOV-007. The work item remains alive and becomes actionable again once GTKB-ISOLATION-018 reaches VERIFIED.

## Specification Links

- `DELIB-1537` (S330 owner decision, 2026-05-04) — establishes the project-root-boundary topology that makes GTKB-GOV-007 unactionable against current GT-KB-root paths.
- `GOV-STANDING-BACKLOG-001` — `memory/work_list.md` as the governed cross-session work authority. Annotations preserve actionability information across sessions.
- `PB-STANDING-BACKLOG-CONTINUITY-001` — Prime Builder must maintain the standing backlog continuously; blocking dependencies must be visible.
- `ADR-STANDING-BACKLOG-AS-WORK-AUTHORITY-001` — the standing backlog has formal work-authority status.
- `DCL-STANDING-BACKLOG-SCHEMA-001` — schema constraints on backlog entries.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — applications/<name>/ placement convention; explains why GTKB-GOV-007 paths must move before action.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — every implementation proposal must cite all relevant specifications.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — VERIFIED requires tests derived from linked specifications and executed against the implementation; this proposal includes a spec-to-test mapping.
- `GOV-ARTIFACT-APPROVAL-001` — formal-artifact-approval discipline. `memory/work_list.md` is a protected narrative artifact per `canonical-terminology.md` § "canonical artifact"; the implementation Edit step requires a formal-artifact-approval packet at implementation time.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` (advisory) — artifact-oriented development as the working model.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` (advisory) — backlog entry annotations are lifecycle metadata.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` (advisory) — artifact-oriented governance discipline.
- `.claude/rules/project-root-boundary.md` — the binding rules that make GTKB-GOV-007 unactionable today against GT-KB-root paths.
- `.claude/rules/operating-model.md` §1 — application/platform/hosted-application terminology and the spec-first discipline.
- `.claude/rules/file-bridge-protocol.md` — Mandatory Owner Decisions / Input Section Gate; Mandatory Pre-Filing Preflight Subsection; Mandatory Specification-Derived Verification Gate.
- `.claude/rules/codex-review-gate.md` — Loyal Opposition review obligations.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge/INDEX.md is the canonical bridge workflow state. This proposal was filed via the bridge-propose helper which inserted a NEW entry at the top of bridge/INDEX.md per the protocol; no prior versions of this thread exist; nothing is rewritten or deleted.

## Prior Deliberations

(Helper pre-populates this section from glossary-source seeds and semantic search.)


### Helper-suggested candidates

<!-- Pre-populated by helper; review and prune. -->
- DA: `DELIB-0988` — seed=search; bridge_thread; GTKB-ISOLATION-015 Slice 2 Reconciliation Review
- DA: `DELIB-1424` — seed=search; bridge_thread; Bridge thread: gtkb-isolation-phase1-implementation-2026-04-28 (10 versions, VER
- DA: `DELIB-0987` — seed=search; bridge_thread; VERIFIED: GTKB-ISOLATION-015 Slice 2 work_subject.set reconciliation
- DA: `DELIB-S310-ROLE-DEFINITION-ASSESSMENT` — seed=search; owner_conversation; Prime Builder / Loyal Opposition Role-Definition Assessment (S310)
- DA: `DELIB-1135` — seed=search; bridge_thread; Bridge thread: gtkb-isolation-015-phase7-full-integration (16 versions, VERIFIED

## Owner Decisions / Input

This proposal depends on owner approval per `.claude/rules/file-bridge-protocol.md` § Mandatory Owner Decisions / Input Section Gate:

1. **Lane scope authorization (this session, 2026-05-10).** Owner answered "Full parallel (Recommended)" to AskUserQuestion: "Authorize me to open these lanes in parallel for maximum throughput?" — this proposal is C.1 in that authorization.
2. **Owner directives in this session re-establishing the gating constraint.**
   - "All Agent Red artifacts and data should be relocated to E:\GT-KB\applications\Agent_Red." (in-tree relocation directive)
   - "Agent Red is a separate project and the entire content of the Agent_Red directory should never be pushed to the GT-KB repo, because the Agent_Red directory is a different project: it is the Agent Red project, and it has its own repo." (boundary directive)
3. **Implementation-time owner approval required.** `memory/work_list.md` is a protected narrative artifact. The implementation step requires a formal-artifact-approval packet at `.groundtruth/formal-artifact-approvals/<date>-gtkb-gov-007-annotation.json` with full file content plus body_hash, before the Edit lands. This proposal does NOT include the packet; the Codex GO authorizes the work; the packet is collected at implementation time.

## Implementation Plan

### Single Step

Edit the GTKB-GOV-007 section of `memory/work_list.md`. Add a "Blocked on:" annotation immediately under the existing "Priority:" line, citing GTKB-ISOLATION-018 as the gating dependency, with reference to DELIB-1537 and the lead bridge thread `bridge/gtkb-isolation-018-slice-0-git-boundary-001.md`.

**Proposed annotation text (verbatim, to be inserted as a new paragraph immediately after the existing Priority line):**

```
**Blocked on:** `GTKB-ISOLATION-018` (Agent Red in-tree relocation program). The three child NO-GO threads cite implementation paths at GT-KB root (`src/multi_tenant/middleware.py`, `src/app/health.py`, `src/multi_tenant/default_alert_rules.py`, etc.). Per `DELIB-1537` (S330 owner directive) and `.claude/rules/project-root-boundary.md` Rule 3, those paths must relocate to `applications/Agent_Red/` before revised bridge proposals against them can pass the project-root-boundary preflight. Lead Slice 0 (git boundary) tracked at `bridge/gtkb-isolation-018-slice-0-git-boundary-001.md`. This entry returns to actionable when GTKB-ISOLATION-018 reaches VERIFIED.
```

### Preconditions and Sequence

1. Assemble formal-artifact-approval packet per `GOV-ARTIFACT-APPROVAL-001` referencing the full proposed body of `memory/work_list.md` post-edit, with `body_hash` (SHA-256). Owner-approval evidence is the AUQ "Full parallel (Recommended)" answer in this session.
2. Apply the Edit using the Edit tool against `memory/work_list.md`. The narrative-artifact-approval-gate hook reads the packet at write time.
3. Add and run the regression test described in § Tests Derived From Linked Specifications.
4. Run release-candidate gate.
5. File post-implementation report through the bridge.

### Out of Scope

- Modifying any other entry in `memory/work_list.md`.
- Closing, retiring, or reclassifying GTKB-GOV-007 itself — those are separate decisions awaiting ISOLATION-018 outcome.
- Editing `canonical-terminology.md` — separate proposal C.2.
- Editing the three child bridge threads (`commercial-readiness-spec-1831-startup-wiring`, `commercial-readiness-spec-verification`, `commercial-readiness-spec-1833-ready-propagation`) — they remain at their current PAUSED state until ISOLATION-018 lands.
- Annotating any other GTKB-GOV-* work items — only GTKB-GOV-007 is gated by ISOLATION-018; if other items are similarly blocked, separate proposals.

## Tests Derived From Linked Specifications

| Linked specification | Acceptance check | Test |
|----------------------|------------------|------|
| GOV-STANDING-BACKLOG-001 (work_list.md as authority) | "Blocked on:" annotation present in the GTKB-GOV-007 section | `tests/governance/test_standing_backlog_annotations.py::test_gtkb_gov_007_blocked_on_annotation_present` (NEW file, NEW test) |
| PB-STANDING-BACKLOG-CONTINUITY-001 (continuity) | Block annotation cites both DELIB-1537 and the lead bridge thread | Same test, expanded assertion: line contains both `DELIB-1537` and `bridge/gtkb-isolation-018-slice-0-git-boundary` |
| GOV-FILE-BRIDGE-AUTHORITY-001 (bridge/INDEX.md canonical state) | Annotation references the correct bridge file path verbatim | Same test: `bridge/gtkb-isolation-018-slice-0-git-boundary-001.md` literal substring |
| ADR-ISOLATION-APPLICATION-PLACEMENT-001 (placement convention) | Annotation explains the path-relocation rationale | Same test: `applications/Agent_Red/` substring present |
| DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 (spec-to-test mapping) | This proposal's spec-to-test mapping is honored | This very mapping plus the implementation tests being green |

The new test runs as part of `pytest tests/governance/`. Pass criteria: the annotation matches the proposed text and contains the cited substrings.

## Verification Commands

```text
$ grep -A 4 "^### GTKB-GOV-007" memory/work_list.md | head -10
(shows annotation under the entry)
$ python -m pytest tests/governance/test_standing_backlog_annotations.py -q
.                                                                        [100%]
1 passed
$ python scripts/audit_standing_backlog_sources.py
(audit reports the annotation as a known dependency, not as drift)
$ python scripts/release_candidate_gate.py
(gate passes)
```

## Risks and Rollback

### R1 — Annotation phrasing creates terminology drift

If the annotation introduces phrasing that contradicts `.claude/rules/canonical-terminology.md` or `.claude/rules/operating-model.md` §2, future readers may infer the wrong meaning.

**Mitigation:** Annotation text uses canonical terms (`bridge thread`, `verified`, `applications/Agent_Red/`, `GT-KB root`, `verification`) as defined in `canonical-terminology.md`. Codex review verifies term usage.

**Rollback:** Edit `memory/work_list.md` to remove the annotation. Single-revert commit; recoverable from git reflog.

### R2 — Annotation becomes stale before ISOLATION-018 reaches VERIFIED

If GTKB-ISOLATION-018 takes multiple slices to complete, the annotation may need updates as slice numbers progress (Slice 0, Slice 1, Slice 2, ...).

**Mitigation:** Annotation references the program (GTKB-ISOLATION-018) at the umbrella level and the lead Slice 0 bridge file. Slice numbering updates are normal backlog hygiene under standing-backlog governance; this proposal does not lock the annotation against future updates.

**Rollback:** Same as R1.

### R3 — Formal-artifact-approval packet drift

If the packet's `body_hash` does not match the actual post-edit body, the narrative-artifact-approval-gate hook blocks the Edit, leaving partial state.

**Mitigation:** Packet construction step (1 in the sequence above) computes `body_hash` against the exact post-edit body produced by the Edit operation, by first dry-rendering the proposed edit and hashing.

**Rollback:** Packet creation is idempotent; if the gate blocks, no Edit applied; rebuild packet with correct hash and retry.

## Acceptance Criteria

1. The "Blocked on:" annotation is present immediately under the "Priority:" line of the GTKB-GOV-007 section in `memory/work_list.md`.
2. The annotation cites `DELIB-1537` and `bridge/gtkb-isolation-018-slice-0-git-boundary-001.md` explicitly.
3. The new regression test in `tests/governance/test_standing_backlog_annotations.py` passes.
4. The implementation Edit was preceded by a formal-artifact-approval packet at `.groundtruth/formal-artifact-approvals/<date>-gtkb-gov-007-annotation.json` whose `body_hash` matches the post-edit body.
5. The annotation does not modify any other entry in `memory/work_list.md`.
6. `python scripts/release_candidate_gate.py` passes.

## Pre-Filing Applicability Preflight

Will run after this proposal is filed and INDEX entry is in place; final preflight result and `packet_hash` recorded post-revision in this section.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
