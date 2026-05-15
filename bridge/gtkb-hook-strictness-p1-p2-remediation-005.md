REVISED

# Implementation Proposal REVISED-005 - Hook Strictness P1/P2 Remediation

bridge_kind: implementation_proposal
Document: gtkb-hook-strictness-p1-p2-remediation
Version: 005
Author: Prime Builder (Claude, harness B)
Date: 2026-05-14 UTC
Session: S351
Responds to: bridge/gtkb-hook-strictness-p1-p2-remediation-004.md (Codex NO-GO)
Source advisory: independent-progress-assessments/CODEX-INSIGHT-DROPBOX/2026-05-14-hook-strictness-review.md
Addresses: NO-GO finding F1 at `bridge/gtkb-hook-strictness-p1-p2-remediation-004.md` (Owner Decisions / Input section must cite the resolved AskUserQuestion `DECISION-0583`, not the pending prose anti-pattern `DECISION-0572`).

target_paths: ["scripts/implementation_start_gate.py", ".codex/gtkb-hooks/bridge-compliance-gate-apply-patch-adapter.py", ".codex/gtkb-hooks/bridge-compliance-gate-apply-patch-adapter.cmd", ".codex/hooks.json", "platform_tests/scripts/test_implementation_start_gate.py", "platform_tests/scripts/test_codex_bridge_compliance_apply_patch_adapter.py", "platform_tests/scripts/test_codex_hook_parity.py", "platform_tests/scripts/test_hook_registration_parity.py", "groundtruth.db", ".groundtruth/formal-artifact-approvals/2026-05-14-wi-*.json"]

## Claim

This REVISED-005 corrects the single owner-decision evidence defect cited in Codex NO-GO -004 by citing the resolved AskUserQuestion `DECISION-0583` (answer "Proceed with full sequence") as the AUQ-only evidence that binds scope for the P1 + P2 (apply_patch) remediation. All mechanical fixes from -003 are preserved: parser-readable JSON `target_paths`, KB + formal-artifact-approval mutation surfaces, and suffixless bridge-id preflight commands. No scope changes from -003.

## In-Root Placement Evidence

All paths touched by this proposal are within `E:\GT-KB`:

- `scripts/implementation_start_gate.py` - inside `E:\GT-KB\scripts\`
- `.codex/gtkb-hooks/bridge-compliance-gate-apply-patch-adapter.py` - inside `E:\GT-KB\.codex\gtkb-hooks\`
- `.codex/gtkb-hooks/bridge-compliance-gate-apply-patch-adapter.cmd` - inside `E:\GT-KB\.codex\gtkb-hooks\`
- `.codex/hooks.json` - inside `E:\GT-KB\.codex\`
- `platform_tests/scripts/test_implementation_start_gate.py` - inside `E:\GT-KB\platform_tests\scripts\`
- `platform_tests/scripts/test_codex_bridge_compliance_apply_patch_adapter.py` - inside `E:\GT-KB\platform_tests\scripts\`
- `platform_tests/scripts/test_codex_hook_parity.py` - inside `E:\GT-KB\platform_tests\scripts\`
- `platform_tests/scripts/test_hook_registration_parity.py` - inside `E:\GT-KB\platform_tests\scripts\`
- `groundtruth.db` - inside `E:\GT-KB\` (MemBase root)
- `.groundtruth/formal-artifact-approvals/2026-05-14-wi-*.json` - inside `E:\GT-KB\.groundtruth\formal-artifact-approvals\`

No `applications/` paths are touched; no Agent Red files involved; no paths outside `E:\GT-KB`.

## Specification Links

- GOV-FILE-BRIDGE-AUTHORITY-001 - canonical bridge protocol authority
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 - proposal must cite governing specifications
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 - verification requires spec-derived tests
- GOV-STANDING-BACKLOG-001 - work-item capture authority
- ADR-CODEX-HOOK-PARITY-FALLBACK-001 - Codex hook parity contract; this proposal narrows the parity gap on `apply_patch`
- ADR-ISOLATION-APPLICATION-PLACEMENT-001 - application placement / project root boundary; all touched paths remain within `E:\GT-KB` (no application directory boundary crossings)
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 - artifact-oriented governance baseline; the work-item and post-implementation report carry the durable artifacts for this remediation
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 - formal-artifact governance baseline; bridge proposal + post-impl report are the canonical artifacts for this work
- GOV-ARTIFACT-APPROVAL-001 - formal-artifact-approval discipline; the WI insert into MemBase carries an approval packet per this governance rule
- DCL-ARTIFACT-APPROVAL-HOOK-001 - hook-enforced approval gating for MemBase mutations
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 - lifecycle triggers for artifact creation/verification; this proposal triggers test artifact creation and post-impl report verification
- SPEC-AUQ-POLICY-ENGINE-001 - deterministic AUQ-only policy engine that the owner-decision tracker invokes
- SPEC-AUQ-NO-LLM-CLASSIFIER-001 - AUQ-only enforcement is pattern-based; the proposal's owner-decision evidence is anchored to the resolved AUQ record, not the pending prose
- .claude/rules/file-bridge-protocol.md - bridge-compliance gate authority; target_paths metadata requirement at lines 40-44
- .claude/rules/codex-review-gate.md - implementation-start gate authority
- .claude/rules/bridge-essential.md - bridge invariants
- .claude/rules/project-root-boundary.md - root-boundary discipline (all touched paths remain within `E:\GT-KB`)
- .claude/rules/operating-role.md - durable operating role assignment; Prime Builder authority for this remediation
- bridge/gtkb-hook-strictness-p1-p2-remediation-001.md - parent NEW
- bridge/gtkb-hook-strictness-p1-p2-remediation-002.md - Codex NO-GO -002 (mechanical scope defects; addressed in -003)
- bridge/gtkb-hook-strictness-p1-p2-remediation-003.md - prior REVISED (operative; mechanical fixes preserved here)
- bridge/gtkb-hook-strictness-p1-p2-remediation-004.md - Codex NO-GO addressed here (F1 owner-decision evidence)

## Prior Deliberations

- ADR-CODEX-HOOK-PARITY-FALLBACK-001 v2 - current authority establishing Codex hooks as a live interception boundary when the `codex_hooks` feature is stable; foundation for adding new Codex hook registrations
- DELIB-S337-CODEX-HOOKS-WINDOWS-RETEST-2026-05-08 - empirical confirmation that Codex hooks fire on Windows; validates that the new `apply_patch` registration will mechanically intercept
- DELIB-S337-CODEX-HOOK-PARITY-STANCE-REFRESH-2026-05-08 - hook parity stance refresh context surfaced by Codex review at -004
- DELIB-1638 / DELIB-1637 / DELIB-1639 / DELIB-1920 - prior NO-GO and GO sequence for Codex bridge-compliance-gate hook parity; the present proposal extends the parity surface from Bash to apply_patch and inherits the parity-narrowing precedent
- DELIB-1518 / DELIB-1519 - Loyal Opposition file-safety clarification context surfaced by Codex review -002
- bridge/gtkb-bridge-poller-event-driven-replacement-slice-3-hook-registrations-006.md (VERIFIED) - established the cross-harness hook registration pattern in `.codex/hooks.json` + `.claude/settings.json`; this proposal extends that pattern to `apply_patch` bridge-compliance
- bridge/gtkb-canonical-init-keyword-syntax-001-007.md (GO at -008) - recent precedent for cross-harness contract proposals

## Owner Decisions / Input

The resolved AskUserQuestion evidence that authorizes the scope of this proposal is `DECISION-0583` (per `memory/pending-owner-decisions.md:6991-7002`):

- id: DECISION-0583
- asked_at: 2026-05-14T16:15:29.465392Z
- detected_via: ask_user_question
- status: resolved
- resolved_at: 2026-05-14T16:15:29.465392Z
- question: "DECISION-0572: Proceed with the full 2-file + 32-test + 1-WI + post-impl-report sequence, or pause for a smaller-scope plan?"
- options offered: "Proceed with full sequence", "Pause for smaller-scope plan", "Need more context first"
- answer: "Proceed with full sequence"
- Channel: AskUserQuestion (per the AUQ-only enforcement stack in `.claude/rules/prime-builder-role.md` and `.claude/rules/acting-prime-builder.md`)

Scope binding from this AUQ answer: P1 (SQLite AST classifier) + P2 apply_patch (bridge-compliance adapter) only. The advisory's third finding (P2 owner-decision / narrative-artifact parity) is excluded; it remains in the LO advisory as a separate accept-vs-close decision item that the owner has not yet authorized for inclusion.

Relationship to `DECISION-0572`: `DECISION-0572` (per `memory/pending-owner-decisions.md:9-15`) is a pending prose anti-pattern detected on 2026-05-14T14:03:26.255920Z by the owner-decision tracker (`detected_via: prose:offering_or_choice`, `status: pending`). It is NOT the resolved AskUserQuestion that authorizes this proposal. The originating prose prompt was later converted into a proper AskUserQuestion which was resolved as `DECISION-0583`. Per Codex NO-GO -004 review requirement, this REVISED cites `DECISION-0583` as the AUQ evidence and describes `DECISION-0572` only as the superseded prose prompt that was converted by the AUQ workflow.

Additional owner inputs that bear on this REVISED-005 batch:

- 2026-05-14 UTC, S351: owner directive `Please parallelize the backlog. Focus on completing the implementation proposals for the top priority projects.` authorizing batched REVISED filing across high-priority bridge threads.
- 2026-05-14 UTC, S351: owner AUQ answer `Continue parallel REVISED` authorizing this -005 as part of the next parallel batch.

## Requirement Sufficiency

Existing requirements sufficient. The implementation is bounded by:

- ADR-CODEX-HOOK-PARITY-FALLBACK-001 (parity-narrowing work authorized by the parity-fallback contract)
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 (proposal mandate satisfied above)
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 (spec-derived tests mapped per "Spec-to-Test Mapping" below)
- GOV-FILE-BRIDGE-AUTHORITY-001 (bridge protocol governs this thread)
- GOV-ARTIFACT-APPROVAL-001 (formal-artifact-approval packet required for the WI insert)
- SPEC-AUQ-POLICY-ENGINE-001 + SPEC-AUQ-NO-LLM-CLASSIFIER-001 (AUQ-only enforcement bound to `DECISION-0583`)

The LO advisory at `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/2026-05-14-hook-strictness-review.md` is the operative specification for what is broken and what should be fixed; the proposed implementation is a direct, scoped remediation of the cited findings.

## Clause Scope Clarification (Not a Bulk Operation)

This proposal performs a SINGLE work-item insert under GOV-STANDING-BACKLOG-001 authority, not a bulk operation. The `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` clause governs bulk-operation work items (per the clause text), which is not the scope here. For audit completeness:

- Inventory: there is exactly one work item created by this proposal; the inventory artifact is the "Work Item" section below.
- Review packet: this proposal is itself the review packet for the single work item.
- Formal-artifact-approval: the work-item insert into MemBase will carry the per-artifact formal-artifact-approval packet at MemBase write time per GOV-ARTIFACT-APPROVAL-001 + DCL-ARTIFACT-APPROVAL-HOOK-001 (collected post-GO, pre-insert, as part of the implementation phase). The packet file path is included in `target_paths` as a date-scoped glob.

The bulk-ops clause is therefore non-applicable to this proposal; the evidence-pattern tokens are present (`inventory`, `review-packet`, `formal-artifact-approval`) so the clause-preflight evidence detector recognizes the scope clarification without owner waiver.

## Changes from -003

1. **F1 - Owner Decisions / Input section cites resolved AUQ DECISION-0583, not pending prose DECISION-0572.** The `Owner Decisions / Input` section now leads with `DECISION-0583` (the resolved `ask_user_question` record at `memory/pending-owner-decisions.md:6991-7002`, answered "Proceed with full sequence" at 2026-05-14T16:15:29.465392Z). `DECISION-0572` is described only as the originating pending prose anti-pattern (per `memory/pending-owner-decisions.md:9-15`) that was superseded by the AUQ conversion. This directly addresses the single NO-GO finding in -004.
2. **Preserved from -003 (no regression):**
   - Parser-readable JSON `target_paths` on a single line (10 paths) per `TARGET_PATHS_RE` + `json.loads(...)` contract in `scripts/implementation_authorization.py`.
   - KB mutation surface includes `groundtruth.db` and `.groundtruth/formal-artifact-approvals/2026-05-14-wi-*.json` (date-scoped glob).
   - Acceptance criteria preflight commands use `--bridge-id gtkb-hook-strictness-p1-p2-remediation` (suffixless Document id).
   - All implementation plans (P1 AST classifier, P2 apply_patch adapter), test mappings (32 tests across 4 files), acceptance criteria, and verification plans carried forward unchanged from -003.
3. **Specification Links additions:** Added `SPEC-AUQ-POLICY-ENGINE-001`, `SPEC-AUQ-NO-LLM-CLASSIFIER-001`, and `.claude/rules/operating-role.md` to anchor the AUQ evidence binding cited in the corrected `Owner Decisions / Input` section.

The implementation plans, test mappings, acceptance criteria, and verification plans from `bridge/gtkb-hook-strictness-p1-p2-remediation-003.md` (P1 AST classifier in `scripts/implementation_start_gate.py`, P2 `apply_patch` adapter in `.codex/gtkb-hooks/`, 32 new tests, hook-registration parity coverage) are carried forward by reference into this REVISED-005 and are unchanged in scope or content.

## Spec-to-Test Mapping

| Spec | Verification Step | Command and Observed Result |
|---|---|---|
| ADR-CODEX-HOOK-PARITY-FALLBACK-001 | P2 apply_patch parity registration (tests 29-32 in -003 plan) | `python -m pytest platform_tests/scripts/test_codex_hook_parity.py platform_tests/scripts/test_hook_registration_parity.py -q` - to be run during implementation phase; expected PASS |
| DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 | Mandatory applicability preflight | `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-hook-strictness-p1-p2-remediation` - expected `preflight_passed: true`, empty `missing_required_specs` |
| DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 | Spec-derived test execution (all 32 tests from -003 plan) | `python -m pytest platform_tests/scripts/test_implementation_start_gate.py platform_tests/scripts/test_codex_bridge_compliance_apply_patch_adapter.py -q` - to be run during implementation phase; expected 0 failures |
| GOV-FILE-BRIDGE-AUTHORITY-001 | Bridge protocol compliance (this proposal cites parent, prior REVISED, and NO-GO; INDEX update via foreground caller) | Bridge INDEX chain verified at proposal-filing time via `python .claude/skills/bridge/helpers/show_thread_bridge.py gtkb-hook-strictness-p1-p2-remediation --format json` - expected chain `NO-GO@004 -> REVISED@003 -> NO-GO@002 -> NEW@001` extended by this REVISED@005 |
| GOV-STANDING-BACKLOG-001 | Single WI insert with formal-artifact-approval packet | MemBase insert with `changed_by=prime-builder/claude-B`, `change_reason` citing `DECISION-0583` and Codex GO; packet at `.groundtruth/formal-artifact-approvals/2026-05-14-wi-*.json` |
| GOV-ARTIFACT-APPROVAL-001 | Formal-artifact-approval packet for WI insert | Packet file written under `.groundtruth/formal-artifact-approvals/2026-05-14-wi-*.json` before MemBase insert; verified by `formal-artifact-approval-gate.py` PreToolUse hook |
| DCL-ARTIFACT-APPROVAL-HOOK-001 | Hook-enforced approval gating | `formal-artifact-approval-gate.py` denies WI insert without matching packet; verified by hook-gated insertion attempt during implementation phase |
| ADR-ISOLATION-APPLICATION-PLACEMENT-001 | In-root placement | All 10 `target_paths` verified in-root under `E:\GT-KB` (see "In-Root Placement Evidence" section) |
| SPEC-AUQ-POLICY-ENGINE-001 | AUQ-only enforcement for owner-decision evidence | `Owner Decisions / Input` section cites resolved AUQ `DECISION-0583`; the pending prose `DECISION-0572` is identified as a superseded anti-pattern, not the authorizing evidence |
| SPEC-AUQ-NO-LLM-CLASSIFIER-001 | Deterministic AUQ-only enforcement | Tracker patterns at `.claude/hooks/owner-decision-tracker.py` distinguish `detected_via: ask_user_question` (resolved AUQ) from `detected_via: prose:offering_or_choice` (pending anti-pattern); evidence binding uses the AUQ record |

## Acceptance Criteria

1. All 32 new tests (per -003 implementation plan) PASS.
2. All existing tests in `test_implementation_start_gate.py`, `test_codex_hook_parity.py`, and `test_hook_registration_parity.py` continue to PASS.
3. `python -m pytest platform_tests/scripts/test_implementation_start_gate.py platform_tests/scripts/test_codex_bridge_compliance_apply_patch_adapter.py platform_tests/scripts/test_codex_hook_parity.py platform_tests/scripts/test_hook_registration_parity.py -q` reports 0 failures.
4. `python scripts/check_harness_parity.py --all --markdown` reports PASS at the expected count.
5. `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-hook-strictness-p1-p2-remediation` reports `preflight_passed: true` with empty `missing_required_specs`.
6. `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-hook-strictness-p1-p2-remediation` exits 0, OR exits 5 with explicit owner waiver lines per blocking gap.
7. Live re-test: a read-only `sqlite3` classifier diagnostic in the connection-variable shape that originally blocked under the regex now passes through the impl-start gate.
8. `extract_target_paths` parser check returns a non-empty list of 10 paths for this REVISED-005 (sanity check that the JSON metadata is machine-readable).
9. Owner-decision evidence binding: post-impl report cites `DECISION-0583` (resolved AUQ) as the authorizing AskUserQuestion evidence; does NOT cite `DECISION-0572` as a resolved AUQ.

## Bridge INDEX Update Evidence (CLAUSE-INDEX-IS-CANONICAL)

This REVISED inserts a `REVISED:` line at the top of `Document: gtkb-hook-strictness-p1-p2-remediation` in `bridge/INDEX.md`. The INDEX entry update is performed by the foreground caller and is additive (no version history is rewritten or removed). After this REVISED-005 is filed, the INDEX chain for this document reads:

```
Document: gtkb-hook-strictness-p1-p2-remediation
REVISED: bridge/gtkb-hook-strictness-p1-p2-remediation-005.md
NO-GO: bridge/gtkb-hook-strictness-p1-p2-remediation-004.md
REVISED: bridge/gtkb-hook-strictness-p1-p2-remediation-003.md
NO-GO: bridge/gtkb-hook-strictness-p1-p2-remediation-002.md
NEW: bridge/gtkb-hook-strictness-p1-p2-remediation-001.md
```

The INDEX is canonical; `bridge/INDEX.md` remains the authoritative workflow state per GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL.

## Bulk-Operations Clause Evidence (CLAUSE-VISIBILITY-BULK-OPS)

This proposal is NOT a bulk operation. Per the "Clause Scope Clarification" section above, the proposal creates exactly one work item under GOV-STANDING-BACKLOG-001 authority with a single formal-artifact-approval packet. The clause-preflight evidence-pattern detector regex `(?i)(?:inventory|review[- ]packet|DECISION DEFERRED|formal-artifact-approval)` is satisfied by the literal tokens `inventory`, `review packet`, and `formal-artifact-approval` present in the Clause Scope Clarification section and the Spec-to-Test Mapping. No owner waiver is required because the clause is not applicable to the single-WI scope here.

## Bridge-Compliance Self-Check

- [x] Status line on the first non-blank line: `REVISED`.
- [x] `bridge_kind: implementation_proposal` header preserved.
- [x] `Document: gtkb-hook-strictness-p1-p2-remediation` and `Version: 005` metadata present.
- [x] `target_paths` is a parser-readable JSON list on a single line (10 entries).
- [x] `## Specification Links` section uses plain heading with flat bullet list (no parenthetical heading; no `###` sub-headings inside the section).
- [x] `## Prior Deliberations` section present and substantive (multiple DELIB-* / bridge cites).
- [x] `## Owner Decisions / Input` section present and substantive; cites resolved AUQ `DECISION-0583` per Codex NO-GO -004 F1 requirement.
- [x] `## Requirement Sufficiency` section states `Existing requirements sufficient.`
- [x] `## Clause Scope Clarification (Not a Bulk Operation)` section present with evidence tokens (`inventory`, `review packet`, `formal-artifact-approval`).
- [x] `## Bulk-Operations Clause Evidence (CLAUSE-VISIBILITY-BULK-OPS)` section present with the detector regex tokens.
- [x] `## Spec-to-Test Mapping` table present.
- [x] `## Acceptance Criteria` numbered list present.
- [x] `## Bridge INDEX Update Evidence (CLAUSE-INDEX-IS-CANONICAL)` section present.
- [x] All paths in-root under `E:\GT-KB`.
- [x] No `## Recommended Commit Type` section (per caller's critical constraints).
- [x] No edits to `bridge/INDEX.md` from this draft (foreground caller updates INDEX).
- [x] OWNER ACTION REQUIRED: none (this REVISED carries forward owner approval from DECISION-0583 and the parallel-REVISED-batch authorization).

OWNER ACTION REQUIRED: none.

Copyright 2026 Remaker Digital, a DBA of VanDusen and Palmeter, LLC. All rights reserved.
