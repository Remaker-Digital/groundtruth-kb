# GT-KB v1.0 Release Plan — Target Scope Inventory

This document lists all active projects and individual open work items that comprise the scope for the **GT-KB v1.0 Release Plan** under the **Option B (Hybrid Variant - Spec-Driven Progressive Refactor)** strategy.

## Active v1.0 Target Projects

| Project ID | Name | Status | Purpose |
|:---|:---|:---|:---|
| `GTKB-V1-RELEASE-STRATEGY-001` | GT-KB v1.0 Release Strategy | active | Organize all v1.0 implementation prerequisite and slice work under one governed scope, per DELIB-2234 (Hybrid Variant + Release-Gate + 3-tier + In-tree-then-separate spec corpus + Promotion governance + Quality-driven pacing) and DELIB-2238 (session-envelope convention, scaffold-fork-tier). |
| `PROJECT-AGENT-RED-RELEASE-READINESS` | AGENT-RED-RELEASE-READINESS | active |  |
| `PROJECT-GTKB-DISPATCH-ENVELOPES` | GTKB-DISPATCH-ENVELOPES | retired | Centralized singleton dispatch service plus a first-class envelope abstraction (recurring/one-shot ops, work, review, and audit envelopes) routed to a chosen harness or role, schedule- or event-driven, activity-gated per the S308 lesson. |
| `PROJECT-GTKB-ENVELOPE-OPEN-CLOSE-ACTION-REFINEMENT` | Envelope Open and Close action refinement | active | Refine the GT-KB session envelope open (startup disclosure) and close (wrap-up) behaviors plus work envelope dispositions per owner directive S366 2026-05-29 |
| `PROJECT-GTKB-ISOLATION` | GTKB-ISOLATION | active |  |
| `PROJECT-GTKB-ISOLATION-016` | GTKB-ISOLATION-016 | retired |  |
| `PROJECT-GTKB-ISOLATION-017-SLICE-2-5` | GTKB-ISOLATION-017-SLICE-2.5 | active |  |
| `PROJECT-GTKB-ISOLATION-017-SLICE-2-5-REGISTRY-RATIONALE-SCHEMA-EXTENSION` | (registry rationale schema extension) | active |  |
| `PROJECT-GTKB-ISOLATION-017-SLICE-5-5` | GTKB-ISOLATION-017-SLICE-5.5 | active |  |
| `PROJECT-GTKB-ISOLATION-017-SLICE-5-5-OVERLAY-REFRESH-DISPOSABILITY-CHROMA-REGEN-API` | (overlay refresh + disposability + chroma-regen API) | active |  |
| `PROJECT-GTKB-ISOLATION-AGENT-RED-CUTOVER` | Agent Red cutover | active |  |
| `PROJECT-GTKB-ISOLATION-CLOSEOUT` | GTKB-ISOLATION-CLOSEOUT | active | Final closeout of the GT-KB isolation program (Phase 7 + adopter packaging + program backstop). |
| `PROJECT-GTKB-ISOLATION-PHASE-7-SLICE-2` | Phase 7 Slice 2 | active |  |
| `PROJECT-GTKB-ISOLATION-PHASE-9-PRODUCTIZATION` | Phase 9 productization | active |  |
| `PROJECT-GTKB-ISOLATION-PROGRAM-CLOSEOUT` | Program closeout | active |  |
| `PROJECT-GTKB-RELIABILITY-FIXES` | GTKB-RELIABILITY-FIXES | active | Standing home for small, incidentally-discovered defect and reliability fixes that do not descend from a planned workstream. |
| `PROJECT-GTKB-SECRETS-PURGE-AND-COMMIT-ENFORCEMENT` | GTKB-SECRETS-PURGE-AND-COMMIT-ENFORCEMENT | active |  |
| `PROJECT-GTKB-V1-RELEASE-STRATEGY-001` | GTKB-V1-RELEASE-STRATEGY-001 | active |  |
| `PROJECT-GTKB-WINDOWS-GOVERNANCE-PREFLIGHT-SURFACE` | GTKB-WINDOWS-GOVERNANCE-PREFLIGHT-SURFACE | active | Provide Windows-native governance preflight surfaces so Codex and Git can run hook-equivalent commit and push checks without Bash/WSL-only manual equivalents. |

## Outstanding Work Items

| Work Item ID | Title | Priority | Project Mapping |
|:---|:---|:---|:---|
| `GTKB-AUTO-PUSH-INVESTIGATION-001` | Investigate background auto-push of local commits to origin/develop | P2 | (none) |
| `GTKB-COMMIT-SCOPE-BUNDLING-DETECTION-001` | Pre-commit predicate to detect cross-scope bundling via mismatched approval packets | P2 | (none) |
| `WI-3395` | ChromaDB semantic-history backfill design for v1.0 identifier-reset cut (Finding 3 from V1 Release Strategy LO review) | P3 | (none) |
| `WI-3441` | Route LO advisory: INSIGHTS-2026-05-29-07-12-delib-2500-envelope-convention-advisory.md | low | (none) |
| `WI-3467` | Remove 'Work State' and 'Recommended Session Focus' sections from session envelope opening disclosure | P3 | (none) |
| `WI-3623` | Route LO advisory: INSIGHTS-2026-03-28-S227-COMMIT-463F989C-REVIEW.md | low | (none) |
| `WI-3624` | Route LO advisory: INSIGHTS-2026-03-28-S227-COMMIT-837B7B9F-REVIEW.md | low | (none) |
| `WI-3625` | Route LO advisory: INSIGHTS-2026-03-28-S227-COMMIT-933DA39A-REVERIFICATION.md | low | (none) |
| `WI-3626` | Route LO advisory: INSIGHTS-2026-03-28-S227-COMMIT-C4377D1E-REVERIFICATION.md | low | (none) |
| `WI-3627` | Route LO advisory: INSIGHTS-2026-03-28-S227-COMMIT-C4377D1E-REVERIFY.md | low | (none) |
| `WI-3628` | Route LO advisory: INSIGHTS-2026-03-28-S227-COMMIT-E8808F0B-REVIEW.md | low | (none) |
| `WI-3819` | Route LO advisory: INSIGHTS-2026-04-01-10-44-34-S251-FINAL-VERIFICATION-LAST-3-COMMITS-NOGO.md | low | (none) |
| `WI-4100` | Route LO advisory: INSIGHTS-2026-04-08-21-56-28-SPEC1879-HARDENING-COMMIT-BFB27252-REVIEW.md | low | (none) |
| `WI-4291` | Envelope: amend init-keyword family for ::init <subject> <role> | P2 | (none) |
| `WI-4292` | Envelope: draft SPEC-CANONICAL-WRAP-KEYWORD-SYNTAX-001 (::wrap) | P2 | (none) |
| `WI-4293` | Envelope: draft DCL-SESSION-ENVELOPE-DURABILITY-001 (.claude/session/envelope.json) | P2 | (none) |
| `WI-4294` | Envelope: draft SPEC-SESSION-WRAP-PROCEDURE-DETERMINISTIC-TRIGGER-001 + lean-mandatory tiering | P2 | (none) |
| `WI-4295` | Envelope: draft work-envelope router spec/DCL (::open/::close) | P2 | (none) |
| `WI-4296` | Envelope: draft dispatch-envelope element spec/DCL (schedule/event-driven routing) | P2 | (none) |
| `WI-4297` | Envelope: draft project-completion dispatch-envelope type spec | P2 | (none) |
| `WI-4298` | Envelope: open/close disclosure UI (minimal-open + structured-close) | P2 | (none) |
| `WI-4299` | Envelope: extract handoff-prompt generator as a deterministic service | P3 | (none) |
| `WI-4300` | Envelope: glossary entries + GOV-SESSION-LIFECYCLE amendment | P3 | (none) |
| `WI-4301` | Envelope: implementation (markers + state + triggers + router + dispatch) | P2 | (none) |
| `WI-4302` | Envelope: meta-model ADR (3-part anatomy + dispatch-session-topic containment) | P2 | (none) |
| `GTKB-ISOLATION-015` | Complete full Phase 7 work-subject/root enforcement (Slice 1 VERIFIED; Slice 2 remaining) |  | GTKB-ISOLATION |
| `GTKB-ISOLATION-017` | Implement downstream adopter packaging and clean-adopter validation |  | GTKB-ISOLATION |
| `GTKB-ISOLATION-018` | Execute Agent Red child-directory cutover |  | GTKB-ISOLATION |
| `GTKB-ISOLATION-019` | Close the isolation program with final verification and backlog cleanup |  | GTKB-ISOLATION |
| `GTKB-ISOLATION-017-SLICE-2.5` | GTKB-ISOLATION-017-SLICE-2.5 (registry rationale schema extension) |  | GTKB-ISOLATION-017-SLICE-2.5 |
| `WI-3497` | Pre-commit hook auto-stages files outside the verified staged set (commit-scope contamination) | P2 | GTKB-RELIABILITY-FIXES |
| `WI-3498` | S373/S378 ruff cleanup: pre-run ruff format/check before commit-ready and clear current groundtruth-kb drift | P2 | GTKB-RELIABILITY-FIXES |
| `WI-3400` | Capture Antigravity 2026-05-27 V1-RELEASE-STRATEGY-REVIEW advisory disposition (peer-solution-advisory-loop) | P2 | GTKB-V1-RELEASE-STRATEGY-001 |
| `WI-3401` | Scope §10.1 mechanical-enforcement gate bridge proposal (Hybrid Variant prereq) | P1 | GTKB-V1-RELEASE-STRATEGY-001 |
| `WI-3402` | Scope §10.2 spec-corpus distillation bridge proposal (in-tree specs/ initially) | P1 | GTKB-V1-RELEASE-STRATEGY-001 |
| `WI-3403` | Scope Docker isolation-validator test (release-gate validator, promoted from Antigravity Finding 1) | P1 | GTKB-V1-RELEASE-STRATEGY-001 |
| `WI-3405` | Revise gtkb-agent-red-reference-adopter-framing-restoration to -003 REVISED (ADR-ISOLATION-APPLICATION-PLACEMENT-001 citation) | P2 | GTKB-V1-RELEASE-STRATEGY-001 |
| `WI-3407` | Create decision-capture composite DELIB workflow skill (per owner agreement) | P2 | GTKB-V1-RELEASE-STRATEGY-001 |
| `WI-4303` | Promote standing major-release content goal to GOV + release-gate DCL | P2 | GTKB-V1-RELEASE-STRATEGY-001 |
| `WI-3392` | Commit regenerated dev-environment inventory artifacts (2026-05-27 hygiene) | P3 | PROJECT-GTKB-RELIABILITY-FIXES |
| `WI-3428` | Commit regenerated dev-environment inventory artifacts (2026-05-28 hygiene) | P3 | PROJECT-GTKB-RELIABILITY-FIXES |
| `WI-4255` | Windows governance preflight evidence model | P2 | PROJECT-GTKB-WINDOWS-GOVERNANCE-PREFLIGHT-SURFACE |
| `WI-4256` | Windows commit governance preflight command and wrapper | P2 | PROJECT-GTKB-WINDOWS-GOVERNANCE-PREFLIGHT-SURFACE |
| `WI-4257` | Windows push governance preflight command and wrapper | P2 | PROJECT-GTKB-WINDOWS-GOVERNANCE-PREFLIGHT-SURFACE |
| `WI-4258` | Read-only push readiness diagnostic | P2 | PROJECT-GTKB-WINDOWS-GOVERNANCE-PREFLIGHT-SURFACE |

---
*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*