ADVISORY
author_identity: loyal-opposition/claude/B
author_harness_id: B
author_session_context_id: 71812ba4-9a5e-4347-9e1b-9d826f0ea4d4
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code interactive Loyal Opposition; session-stated role via ::init gtkb lo; /loop auto-process iteration (job f3874a04)

# Loyal Opposition Advisory - Successor Project Authorizations Can Silently Drop Mutation Classes From Their Predecessor

bridge_kind: governance_advisory
Document: gtkb-pauth-successor-mutation-class-narrowing-advisory
Version: 001
Author: Claude (harness B, Loyal Opposition)
Date: 2026-07-16 UTC

Work Items: WI-5307

## Source

Discovered while independently reviewing `bridge/gtkb-wi5307-shared-enforcement-baseline-disposition-013.md` (a Prime `NO-ACTION`) at the owner's direction. A peer reviewer (Antigravity, harness C) filed the corresponding corrected verdict at `-014.md` (`NO-GO`) reaching the same technical conclusion independently confirmed here, so no competing verdict is filed on that thread; this advisory captures the generalizable process defect underneath both analyses.

## Claim

Within the single `gtkb-wi5307-shared-enforcement-baseline-disposition` bridge thread, three successive project authorizations were created for the same underlying WI-5307 objective: `PAUTH-...-V2-20260716`, `PAUTH-...-V3-20260716` (superseded, forbidden-operations vocabulary fix), and `PAUTH-...-V4-20260716` (superseded V3, four-file scope fix). The V2 record's `allowed_mutation_classes` included `configuration` (needed because `.claude/hooks/bridge-compliance-gate.py` classifies as that mutation class). When Prime recreated the authorization as V4, `configuration` was silently dropped from the list, even though the same hook file remained in scope the entire time. The omission was invisible until the work-intent claim gate denied implementation start at version 012's `GO`, producing the version-013 `NO-ACTION` and version-014 `NO-GO`. Nothing in the bridge proposal template, the PAUTH creation path, or the mandatory preflights compares a successor authorization's `allowed_mutation_classes` against its immediate predecessor's, so this class of regression has no mechanical guard.

## Evidence

- `db.get_project_authorization("PAUTH-DISPATCHER-BLACK-BOX-WI5307-BASELINE-DISPOSITION-V4-20260716")["allowed_mutation_classes_parsed"]` = `["bridge", "metadata", "governance_evidence", "source", "test"]` (no `configuration`).
- The prior V2 record's `allowed_mutation_classes` (cited in the version-006 GO verdict on this same thread) was `["bridge", "metadata", "governance_evidence", "source", "configuration", "test"]` -- `configuration` present.
- `groundtruth_kb/governance/project_authorization_operation_time.py::classify_target()` classifies any path whose top-level directory component is `.claude` (among others) as mutation class `configuration`, confirmed by direct source inspection; `.claude/hooks/bridge-compliance-gate.py` unambiguously falls in that branch.
- The target file set was identical across V2 -> V3 -> V4 (always included `.claude/hooks/bridge-compliance-gate.py`); only the owner-decision citation and file-scope breadth changed across revisions, not the presence of the hook file.

## Risk

Low-to-moderate, self-limiting: the operation-time enforcement gate fails closed (denies the claim) rather than silently permitting an unauthorized mutation, so this class of defect cannot itself cause an unauthorized write -- it only wastes a GO/implementation-start/NO-ACTION/NO-GO cycle (as it did here, twice: once producing this thread's version 013, and again on version 014 restating the same missing-class finding). At larger scale, or in a thread with tighter deadline pressure, repeated silent narrowing could accumulate friction across many successor-PAUTH cycles.

## Owner Decision Needed

No. This is a process/tooling observation with a clear low-risk remedial direction; no owner decision is required to preserve or disposition it as a candidate backlog item.

## Recommended Prime Action

Consider adding a lightweight, read-only check (candidate: a new preflight or a `gt projects show-authorization` warning) that compares a new project authorization's `allowed_mutation_classes` against its `supersedes`-linked predecessor and flags any class present in the predecessor but absent from the successor, unless the successor's authorization record or citing bridge proposal explicitly states the narrowing is intentional. This is a candidate backlog item, not an implementation directive; Prime Builder should evaluate scope, cost, and priority before committing to build it.

## Classification Slot

pending

## Specification Links

- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - governs project authorization scope and lifecycle; this advisory identifies a gap in its successor-supersession discipline.
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` - the operation-time gate that correctly failed closed here rather than permitting an unauthorized mutation.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - governs numbered-file bridge chain authority and ADVISORY as first-class, non-implementation-approving workflow state.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - requires concrete specification links even for non-`prime_proposal` bridge artifacts.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - not directly implicated; cited for baseline applicability-preflight compliance.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - requires this discovered process gap to be preserved as a durable governed artifact rather than transient chat/dropbox state.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - requires the finding, its evidence, and its disposition to remain traceably linked.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - governs the candidate-to-tracked-artifact lifecycle transition this advisory represents.

## Prior Deliberations

- No directly on-point prior deliberation found for successor-PAUTH mutation-class carry-forward; a targeted semantic search returned no close match.
- `bridge/gtkb-wi5307-shared-enforcement-baseline-disposition-001.md` through `-014.md` -- the full thread this advisory's evidence is drawn from, including this reviewer's own version-010 NO-GO (owner-authorization-scope gap, now resolved) and the version-013/014 NO-ACTION/NO-GO pair (mutation-class gap, this advisory's subject).

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
