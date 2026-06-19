NEW

bridge_kind: prime_proposal
Document: gtkb-role-authority-interactive-persistence
Version: 001 (NEW)
Author: Prime Builder (Claude Code, harness B)
Date: 2026-06-18 UTC
Implements: WI-4668
Project Authorization: PAUTH-WI-4668-ROLE-AUTHORITY-INTERACTIVE-PERSISTENCE-ADR-DCL
Project: PROJECT-GTKB-ROLE-STATUS-ORTHOGONALITY-DISPATCH
Work Item: WI-4668
target_paths: ["specifications:ADR-ROLE-AUTHORITY-INTERACTIVE-PERSISTENCE-001", "specifications:DCL-INTERACTIVE-SESSION-ROLE-PERSISTENCE-001", "specifications:SPEC-INTAKE-a3cdef", ".claude/rules/operating-role.md"]
Recommended commit type: feat:
author_identity: prime-builder/claude/B
author_harness_id: B
author_session_context_id: 806e5944-602e-41ac-b030-cdd18fd50242
author_model: claude-opus-4-7
author_model_version: Claude Opus 4.7
author_model_configuration: Claude Code interactive Prime Builder session; explanatory output style; 1M context

# Formalize Role-Authority Interactive Transcript Persistence as ADR + DCL Pair

## Claim

Per owner directive `DELIB-20265226` (S447, 2026-06-18), formalize four operative invariants governing role authority as a new ADR + DCL pair under the GroundTruth-KB per-artifact approval ceremony:

1. **Dispatcher (SoT)** — the dispatcher regards the registry-recorded role for each harness as authoritative for dispatch routing.
2. **AI agent (hint)** — an AI agent regards the registry-recorded role only as a hint/default used to disambiguate intent when no explicit user direction is present in the transcript.
3. **Transcript = interactive session envelope** — a role established by explicit owner direction in the transcript is durable for the life of the interactive session.
4. **Survives boundaries** — a role established by explicit owner direction in an interactive transcript survives compaction/resume events and contiguous SessionStart-like boundaries within the same interactive context; it changes only when the owner explicitly changes it.

Invariants 1 and 2 sharpen the existing `DCL-ROLE-RESOLUTION-DECLARED-AUTHORITY-001` from `DELIB-ROLE-AUTHORITY-DECLARED-NOT-DETECTED-20260613` (S436, 2026-06-13). Invariants 3 and 4 are NEW material: the existing DCL handled envelope-hint authority at session start; this proposal adds *mid-session direction durability across compaction/resume/SessionStart-like boundaries*.

The proposal also retires the orphan stub `SPEC-INTAKE-a3cdef` (created by the spec-classifier auto-confirm path with description=NULL; superseded by the forthcoming DCL) and adds a one-line pointer in `.claude/rules/operating-role.md` to the new ADR/DCL.

## Specification Links

- `GOV-SESSION-ROLE-AUTHORITY-001` — the governing GOV establishing the durable vs session-stated authority split. This proposal extends the framing with the persistence-across-boundaries dimension. The new ADR/DCL operate within this GOV's split-authority model.
- `DCL-ROLE-RESOLUTION-DECLARED-AUTHORITY-001` — the existing DCL from the S436 directive. The new DCL `DCL-INTERACTIVE-SESSION-ROLE-PERSISTENCE-001` is a peer (not a successor) — it covers the persistence dimension while the existing DCL continues to govern session-start envelope resolution.
- `ADR-INTERACTIVE-SESSION-ROLE-OVERRIDE-001` — the existing ADR for the `::init gtkb (pb|lo)` override path. The new ADR `ADR-ROLE-AUTHORITY-INTERACTIVE-PERSISTENCE-001` extends it: explicit owner direction in chat (not requiring the init keyword) is also a session-stated role override, and that override persists across boundaries.
- `GOV-SPEC-CAPTURE-TRANSPARENCY-001` — required surfacing of every capture event with full text. Satisfied this session by Prime Builder surfacing INTAKE-702b8ea6's raw_text inline before the owner AUQ disposition.
- `GOV-ARTIFACT-APPROVAL-001` — formal artifact (ADR, DCL) mutations require per-artifact approval packets. This proposal authorizes the bridge protocol step; per-artifact packets will be minted at insert time.
- `GOV-09 Owner Input Classification Rule` — owner input describing what the system must do classifies as specification language; capture cycle (record → identify gaps → backlog → prioritize) is satisfied by INTAKE-702b8ea6 → DELIB-20265226 → WI-4668 → this proposal.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — proposal filed through the governed bridge protocol path with append-only versioning.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — this proposal cites every relevant governing specification.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — the verification plan derives its tests from the linked specifications and will be executed against the implementation before VERIFIED.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — all artifact mutations occur within MemBase at `E:\GT-KB\groundtruth.db`; narrative-artifact target path is in-root.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` (advisory) — owner decision, intake, DELIB, WI, PAUTH, bridge proposal, post-impl report, and new ADR/DCL artifacts are preserved as durable linked records.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` (advisory) — the requirement is converted into governed artifacts rather than transient chat interpretation.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` (advisory) — WI-4668 remains open through bridge lifecycle (NEW → GO → ceremony → report → VERIFIED).

## Authorization

This proposal uses active project authorization `PAUTH-WI-4668-ROLE-AUTHORITY-INTERACTIVE-PERSISTENCE-ADR-DCL` (anchoring `DELIB-20265226`). Allowed mutation classes: `formal_artifact_mutation`, `spec_retirement`, `narrative_artifact_mutation`. Forbidden operations: `harness_registry_mutation`, `configuration_change`, `deployment`, `source_code_mutation`. Included work item: `WI-4668`. Included specs: `GOV-SESSION-ROLE-AUTHORITY-001`, `DCL-ROLE-RESOLUTION-DECLARED-AUTHORITY-001`, `GOV-ARTIFACT-APPROVAL-001`.

Per-artifact formal-artifact-approval packets will be minted for ADR-ROLE-AUTHORITY-INTERACTIVE-PERSISTENCE-001, DCL-INTERACTIVE-SESSION-ROLE-PERSISTENCE-001, and the SPEC-INTAKE-a3cdef retirement at insert time per GOV-ARTIFACT-APPROVAL-001. The narrative-artifact edit to `.claude/rules/operating-role.md` will use the narrative-artifact-approval packet path per the narrative-artifact-approval-gate hook.

## Prior Deliberations

- `DELIB-20265226` (this session, 2026-06-18) — the anchoring owner decision. Owner directive verbatim plus AUQ disposition Q1 ("Reject stub; draft formal ADR + DCL pair (Recommended)") and Q2 ("Yes, file both as backlog candidates (Recommended)" — three hygiene WIs filed: WI-4665, WI-4666, WI-4667). Outcome `owner_decision`.
- `INTAKE-702b8ea6` (this session, 2026-06-18) — the rejected intake whose rich raw_text is the substance the ADR/DCL formalize. Outcome `deferred` → `rejected`.
- `DELIB-ROLE-AUTHORITY-DECLARED-NOT-DETECTED-20260613` (S436, 2026-06-13) — the prior similar owner directive establishing the declared-not-detected principle and dispatcher/session-resolution split. Chose the same "Draft ADR + DCL, approve via ceremony" path; produced `DCL-ROLE-RESOLUTION-DECLARED-AUTHORITY-001` (existing). Today's directive extends that path with invariants 3 and 4.
- `DELIB-S378-ROLE-STATUS-ORTHOGONALITY-DISPATCH` — owner decision establishing role/status/dispatchability three-axis orthogonality. Today's proposal operates on the role-resolution axis only.
- `DELIB-20263438` — corrected bridge-dispatch architecture (role↔dispatchability orthogonal). Invariant 1 (dispatcher SoT) reinforces this decision.
- `DELIB-20265223` (earlier this session) — owner directive enabling B headless dispatch. Operates on the dispatchability axis; this proposal operates on the role-resolution axis. Both independently true.

## Owner Decisions / Input

- `DELIB-20265226` (owner decision, 2026-06-18, S447 session) authorizes this proposal. Owner AUQ verbatim:
  - Q1 (spec disposition): *"Reject stub; draft formal ADR + DCL pair (Recommended)"*
  - Q2 (hook defects): *"Yes, file both as backlog candidates (Recommended)"*
- AUQ evidence recorded in DELIB-20265226 with `auq_id: S447-OWNER-DIRECTIVE-2026-06-18-ROLE-AUTHORITY-INTERACTIVE-PERSISTENCE`.
- No additional owner decision required before Codex LO review. If Codex prefers an alternative formalization (e.g., amending `DCL-ROLE-RESOLUTION-DECLARED-AUTHORITY-001` to v2 instead of a new peer DCL), that would be a NO-GO with a scope-narrowing recommendation.
- Per-artifact owner approval packets for the ADR and DCL inserts will be minted at insert time per GOV-ARTIFACT-APPROVAL-001 (not pre-emptively here); their content will mirror the artifact bodies presented in Loyal Opposition GO and the post-implementation report.

## Requirement Sufficiency

Existing requirements sufficient. `GOV-SESSION-ROLE-AUTHORITY-001`, `DCL-ROLE-RESOLUTION-DECLARED-AUTHORITY-001`, and `ADR-INTERACTIVE-SESSION-ROLE-OVERRIDE-001` establish the framing within which this refinement operates. The new ADR/DCL pair add the persistence dimension; no new GOV is required.

## Scope

### IP-1: Draft and insert ADR-ROLE-AUTHORITY-INTERACTIVE-PERSISTENCE-001

Insert a new MemBase specification row with `type=architecture_decision`, `id=ADR-ROLE-AUTHORITY-INTERACTIVE-PERSISTENCE-001`, `status=specified`, `section=session-role-resolution`. Body covers:

- The four operative invariants verbatim with citations to today's owner directive (verbatim raw_text from DELIB-20265226).
- Relationship to prior ADRs (`ADR-INTERACTIVE-SESSION-ROLE-OVERRIDE-001`, `ADR-SINGLE-HARNESS-OPERATING-MODE-001`) — peer-not-successor, refining the override-without-init-keyword case and the cross-boundary durability case.
- Rejected alternatives (verbatim from DELIB-20265226 + Codex LO review additions if any):
  - Confirm SPEC-INTAKE-a3cdef and backfill description (rejected — non-mechanical for cross-cutting agent behavior).
  - Capture as DELIB only, defer formalization (rejected — leaves the requirement non-mechanical).
  - Amend `DCL-ROLE-RESOLUTION-DECLARED-AUTHORITY-001` to v2 instead of a new peer DCL (provisionally rejected; Codex review may revise).
- Consequences: agents must check the transcript-defined role before defaulting to the registry hint; dispatcher behavior unchanged; doctor checks remain advisory.

### IP-2: Draft and insert DCL-INTERACTIVE-SESSION-ROLE-PERSISTENCE-001

Insert a new MemBase specification row with `type=design_constraint`, `id=DCL-INTERACTIVE-SESSION-ROLE-PERSISTENCE-001`, `status=specified`, `section=session-role-resolution`. Body covers machine-checkable constraints derived from the four invariants:

- **CLAUSE-DISPATCHER-SOT-FOR-DISPATCH**: cross-harness dispatch routing reads the registry as SoT; rejection of dispatch on registry-disagreement grounds is forbidden (warn-not-override).
- **CLAUSE-AGENT-HINT-NOT-LOCK**: agent behavior is not constrained by the registry role when explicit user direction is present in the transcript; explicit direction in chat is sufficient to override the registry hint (no init keyword required).
- **CLAUSE-TRANSCRIPT-IS-ENVELOPE**: the transcript is the authoritative envelope for interactive session role.
- **CLAUSE-PERSISTENCE-ACROSS-BOUNDARIES**: explicit-direction role survives compaction/resume + contiguous SessionStart-like boundaries within one interactive context; changes only on explicit owner direction.

Assertions field includes (heuristic; refinable in Codex review):

- `grep_absent`: any rule, hook, or script that re-defaults agent behavior to registry role on SessionStart without checking transcript-defined role.
- `grep`: `.claude/rules/operating-role.md` cites this DCL.
- `grep`: `AGENTS.md` cites this DCL.

### IP-3: Retire SPEC-INTAKE-a3cdef

Update SPEC-INTAKE-a3cdef row to `status=retired`, `retired_at=<insert time>`, `change_reason="Superseded by DCL-INTERACTIVE-SESSION-ROLE-PERSISTENCE-001 per DELIB-20265226 owner AUQ disposition; auto-confirm stub had empty description (the description-NULL defect is tracked at WI-4665)."`.

### IP-4: Add narrative pointer to `.claude/rules/operating-role.md`

Append a single bullet under the existing § "Interactive Session Role Override" section pointing to the new ADR and DCL:

```
- See `ADR-ROLE-AUTHORITY-INTERACTIVE-PERSISTENCE-001` and
  `DCL-INTERACTIVE-SESSION-ROLE-PERSISTENCE-001` for the persistence rules
  governing how an explicit-direction role established in the interactive
  transcript survives compaction/resume and SessionStart-like boundaries.
```

Other narrative-artifact files (`AGENTS.md`, `.claude/rules/operating-model.md`) are intentionally out of scope here to keep the proposal small; subsequent hygiene updates can reference the new ADR/DCL.

## Out Of Scope

- No change to dispatcher rules.toml or harness registry.
- No change to `cross_harness_bridge_trigger.py`, `single_harness_bridge_dispatcher.py`, or any dispatch substrate code (the dispatcher behavior is already aligned with invariant 1 per `DELIB-20263438`).
- No new hook or mechanical enforcement layer for invariants 3 and 4 (the ADR records the decision; the DCL records the machine-checkable shape; a follow-on bridge can land the enforcement when ready).
- No update to `AGENTS.md`, `CLAUDE.md`, or other narrative artifacts beyond the single bullet in `.claude/rules/operating-role.md`.
- No source/test mutation; no production deployment; no external action.

## Pre-Filing Checks

Draft checks to run before filing:

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-role-authority-interactive-persistence --content-file .gtkb-state/bridge-propose-drafts/gtkb-role-authority-interactive-persistence-001.md --json
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-role-authority-interactive-persistence --content-file .gtkb-state/bridge-propose-drafts/gtkb-role-authority-interactive-persistence-001.md
python scripts/proposal_target_paths_coverage_preflight.py --content-file .gtkb-state/bridge-propose-drafts/gtkb-role-authority-interactive-persistence-001.md --json --strict
```

Observed draft results will be recorded inline; revisions before Write if any preflight fails.

## Specification-To-Test Mapping

| Specification | Verification |
| --- | --- |
| `GOV-SESSION-ROLE-AUTHORITY-001` | Post-impl report shows new ADR/DCL preserve the split-authority framing; existing dispatcher tests continue to pass unchanged. |
| `DCL-ROLE-RESOLUTION-DECLARED-AUTHORITY-001` | Post-impl report demonstrates the new DCL is a peer (not a successor) — both DCLs remain at `status=specified`. |
| `ADR-INTERACTIVE-SESSION-ROLE-OVERRIDE-001` | Post-impl report cites the new ADR's relationship-to-prior-ADRs section confirming non-overlap with this existing ADR. |
| `GOV-SPEC-CAPTURE-TRANSPARENCY-001` | Per-artifact approval packets at insert time include the full ADR/DCL body, presented_to_user=True, transcript_captured=True. |
| `GOV-ARTIFACT-APPROVAL-001` | Per-artifact approval packets at `.groundtruth/formal-artifact-approvals/2026-06-18-ADR-ROLE-AUTHORITY-INTERACTIVE-PERSISTENCE-001.json` and `2026-06-18-DCL-INTERACTIVE-SESSION-ROLE-PERSISTENCE-001.json` exist, with content hash matching MemBase row. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Bridge thread is append-only; post-impl report carries forward Specification Links. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Applicability preflight `preflight_passed: true`, `missing_required_specs: []`. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Post-impl report carries spec-to-test mapping with executed commands. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Clause preflight confirms all target paths in-root. |

Implementation verification will run:

```text
python -m groundtruth_kb spec record --id ADR-ROLE-AUTHORITY-INTERACTIVE-PERSISTENCE-001 ...   # per the formal ceremony
python -m groundtruth_kb spec record --id DCL-INTERACTIVE-SESSION-ROLE-PERSISTENCE-001 ...
python -m groundtruth_kb kb-promote --spec-id SPEC-INTAKE-a3cdef --target retired ...
python -m groundtruth_kb deliberations search "interactive transcript role persistence" --limit 3
python -m groundtruth_kb assert --family role-resolution
```

## Acceptance Criteria

- [ ] Loyal Opposition returns GO on this proposal.
- [ ] `ADR-ROLE-AUTHORITY-INTERACTIVE-PERSISTENCE-001` inserted at `status=specified` with per-artifact approval packet evidence.
- [ ] `DCL-INTERACTIVE-SESSION-ROLE-PERSISTENCE-001` inserted at `status=specified` with per-artifact approval packet evidence and 4 machine-checkable clauses covering the four invariants.
- [ ] `SPEC-INTAKE-a3cdef` retired with `retired_at` populated and change_reason citing the new DCL + DELIB-20265226.
- [ ] `.claude/rules/operating-role.md` carries the one-line pointer to the new ADR/DCL under § "Interactive Session Role Override".
- [ ] Existing `DCL-ROLE-RESOLUTION-DECLARED-AUTHORITY-001`, `ADR-INTERACTIVE-SESSION-ROLE-OVERRIDE-001`, and `GOV-SESSION-ROLE-AUTHORITY-001` remain unchanged at their current versions.
- [ ] Loyal Opposition returns VERIFIED on the post-implementation report before WI-4668 is resolved.

## Risk And Rollback

**Risk** (low):
- Adding a peer DCL alongside the existing one introduces a small risk of overlap or confusion. Mitigation: the new DCL's body explicitly states the scope split (existing DCL = session-start envelope; new DCL = persistence across boundaries); the ADR records the rationale.
- The narrative-artifact pointer in `.claude/rules/operating-role.md` is a small addition; risk of unrelated content drift is bounded by the single-bullet scope and narrative-artifact-approval-gate enforcement.

**Rollback**:
- ADR/DCL: append a retirement version with `retired_at` and change_reason; MemBase append-only preserves history.
- SPEC-INTAKE-a3cdef retirement: append a `status=specified` revival version if needed (though the stub has no substance to revive).
- Narrative pointer: single-line revert via narrative-artifact-approval-gate path.

## Loyal Opposition Asks

1. Confirm that the new ADR + new DCL pair (peer to existing) is the right pattern, vs amending `DCL-ROLE-RESOLUTION-DECLARED-AUTHORITY-001` to v2 with the new persistence clauses. The proposal's preferred path is the peer pair (matching the S436 pattern); Codex may NO-GO with a scope-narrowing recommendation if v2-amend is preferred.
2. Confirm that machine-checkable assertions in the DCL (grep_absent / grep) are sufficient at proposal stage, or whether a hook implementation (e.g., a startup hook that re-reads transcript-defined role from a persisted marker before SessionStart) should be in-scope.
3. Confirm that `.claude/rules/operating-role.md` is the right narrative pointer target, or whether `AGENTS.md` and/or `.claude/rules/operating-model.md` should also receive pointers in this proposal vs a follow-on hygiene.
4. Confirm that retiring `SPEC-INTAKE-a3cdef` in this proposal (rather than via a separate hygiene thread tied to WI-4665/4666/4667) is acceptable scope packaging.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
