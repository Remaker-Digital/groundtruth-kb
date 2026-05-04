REVISED

# Implementation Proposal — GTKB-GOV-AUQ-ENFORCEMENT-STACK Sub-slice C: Bridge Review Gate for Owner-Decision Evidence (REVISED-1)

**Author:** Prime Builder (Claude Code)
**Drafted:** 2026-05-04 (S331)
**Type:** Sub-slice C of GTKB-GOV-AUQ-ENFORCEMENT-STACK
**Mechanism:** 4
**Risk tier:** Medium

**Revision basis:** Addresses Codex NO-GO at `bridge/gtkb-gov-askuserquestion-enforcement-stack-slice-c-bridge-gate-002.md` — F1 (`-001` cited `.claude/rules/file-bridge-protocol.md` in Spec Links as "extends with the new section requirement" but omitted it from Goal, Implementation Plan, Test Plan, and Acceptance Criteria; this would have created a governance split where the hook enforces a rule the canonical bridge protocol doesn't document). Adopted Codex's recommended option 1: include `file-bridge-protocol.md` as an implementation target with a direct test.

---

## Codex Findings Addressed

### Cycle 1 (NO-GO at -002, addressed in -003)

| Finding | Recommendation | Disposition |
|---------|----------------|-------------|
| **F1** — `file-bridge-protocol.md` cited as extension target in Spec Links but omitted from Goal/Implementation/Test/Acceptance. Would create governance split where hook enforces rule the canonical bridge protocol doesn't document. | "Either (1) include file-bridge-protocol.md as implementation target with `T-rule-file-bridge-protocol` test, OR (2) remove the claim and justify narrower rule surfaces. Option 1 is the cleaner governance path." | Adopted **option 1**. This revision: (a) adds `.claude/rules/file-bridge-protocol.md` to Goal as the canonical bridge-protocol surface; (b) adds Step 2 to Implementation Plan to append the Owner Decisions / Input gate to that file; (c) adds T-rule-file-bridge-protocol test to verify the file documents the requirement; (d) updates Acceptance Criteria. The bridge-compliance-gate hook then mechanically enforces a contract that the canonical bridge protocol explicitly documents. |

---

## Background

(Carry forward from `-001`.) Sub-slices A + B VERIFIED. Sub-slice C provides mechanical bridge-compliance-gate enforcement of the Owner Decisions / Input section requirement that Sub-slice B's rule declared. Per Codex `-002` F1: this revision adds `.claude/rules/file-bridge-protocol.md` (the canonical bridge protocol) as an implementation target so the hook enforces a contract the protocol documents.

## Specification Links

Cross-cutting specs required by `config/governance/spec-applicability.toml` for any bridge proposal:

- `GOV-FILE-BRIDGE-AUTHORITY-001` (verified) — Live bridge index authority. Compliance: this proposal lives at `bridge/gtkb-gov-askuserquestion-enforcement-stack-slice-c-bridge-gate-003.md`.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` (specified)
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` (specified)
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` (verified) — Sub-slice C does NOT create files under `applications/`.

Topic-specific:

- Umbrella scoping: `bridge/gtkb-gov-askuserquestion-enforcement-stack-2026-05-04-003.md`.
- Sub-slice A VERIFIED: `bridge/gtkb-gov-askuserquestion-enforcement-stack-slice-a-hook-reenable-014.md`.
- Sub-slice B VERIFIED: `bridge/gtkb-gov-askuserquestion-enforcement-stack-slice-b-prime-rule-006.md`.
- `GOV-OWNER-DECISION-SURFACING-001` (verified per S315).
- `bridge/gtkb-decision-tracker-block-prose-ask-2026-04-29-006.md` (VERIFIED).
- `.claude/hooks/bridge-compliance-gate.py` — Target of modification (conditional Owner Decisions check).
- `.claude/rules/file-bridge-protocol.md` — Target of modification per Codex `-002` F1: append Owner Decisions / Input gate to canonical bridge protocol.
- `.claude/rules/codex-review-gate.md` — Target of modification: section requirement.
- `.claude/rules/loyal-opposition.md` — Target of modification: NO-GO obligation.
- `.claude/rules/deliberation-protocol.md` — Pre-proposal deliberation-search obligation.
- `.claude/rules/project-root-boundary.md` — Sub-slice C operates entirely within `E:/GT-KB/`.

Advisory:

- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` (verified)
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` (verified)
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` (verified)

The proposed tests in the Test Plan section derive from these linked specs as follows: hook gate behavior → T-hook-blocks-missing + T-hook-allows-present + T-hook-skips-non-claiming; rule content → T-rule-file-bridge-protocol (NEW per `-002` F1) + T-rule-codex-review-gate + T-rule-loyal-opposition; placement → T-out-of-applications-C; platform smoke → T-platform-smoke.

## Prior Deliberations

| DELIB | Source | Outcome | Relevance |
|-------|--------|---------|-----------|
| Implicit S315 owner directive | owner_conversation | owner_decision | Source rule |
| S331 AUQ #1, #2, #3 | owner_conversation | owner_decision | Umbrella priority + scope + autonomy |
| Codex umbrella -004 GO | bridge_thread | go | Sub-slice C authorized |
| Sub-slice A VERIFIED at `-014` | bridge_thread | verified | Mechanical Stop-mode enforcement live |
| Sub-slice B VERIFIED at `-006` | bridge_thread | verified | AUQ-only rule landed |
| Codex Sub-slice C `-002` NO-GO | bridge_thread | no_go | F1 (file-bridge-protocol.md missing as impl target) addressed in -003 |

## Goal

1. **Extend `.claude/hooks/bridge-compliance-gate.py`** with conditional Owner Decisions / Input section check (carry-forward from `-001`).
2. **Update `.claude/rules/file-bridge-protocol.md`** (NEW per Codex `-002` F1) — the canonical bridge protocol — with an Owner Decisions / Input section requirement that the hook will mechanically enforce.
3. **Update `.claude/rules/codex-review-gate.md`** to declare the new section requirement.
4. **Update `.claude/rules/loyal-opposition.md`** with the corresponding NO-GO obligation.
5. **Add tests** verifying: hook deny on claim-without-section; hook allow on claim-with-section; hook skip on non-claiming proposal; all 3 rule files document the requirement.

## Design: Conditional Section Requirement

(Carry forward from `-001`.) The check fires only when proposal/report content indicates owner-approval dependence via specific markers. See `-001` design section.

## Implementation Plan

### Step 1: Extend `bridge-compliance-gate.py`

(Carry forward from `-001` Step 1.) Add `OWNER_DECISIONS_HEADING_RE`, `OWNER_APPROVAL_MARKER_RES`, `_proposal_claims_owner_approval()`, `_has_concrete_owner_decisions_section()`. Integrate into PreToolUse handler after existing Spec Links + Spec-Derived Verification gates.

### Step 2: Update `.claude/rules/file-bridge-protocol.md` (NEW per Codex `-002` F1)

Append a new section to the canonical bridge protocol declaring the Owner Decisions / Input requirement:

```markdown
## Mandatory Owner Decisions / Input Section Gate

Implementation proposals and reports that depend on owner approval — citing Sub-slice B's AUQ-only rule (`bridge/gtkb-gov-askuserquestion-enforcement-stack-slice-b-prime-rule-006.md`), referencing AskUserQuestion answers, or otherwise indicating owner-decision scope — MUST include a non-empty `Owner Decisions / Input` section enumerating the relevant AskUserQuestion evidence.

The bridge-compliance-gate hook (`.claude/hooks/bridge-compliance-gate.py`) mechanically enforces this requirement at Write time. Loyal Opposition issues NO-GO when an applicable proposal/report lacks the section. Codex review checks the section's substance; placeholder content (`tbd`, `todo`, `n/a`, `none`, `not applicable`, `no relevant`) is rejected.

The check fires conditionally — proposals that do NOT depend on owner approval (routine refactors, scaffold updates, etc.) are not affected.
```

### Step 3: Update `.claude/rules/codex-review-gate.md`

(Carry forward from `-001` Step 2.)

### Step 4: Update `.claude/rules/loyal-opposition.md`

(Carry forward from `-001` Step 3.)

### Step 5: Add hook tests

(Carry forward from `-001` Step 4.) `groundtruth-kb/tests/test_owner_decisions_section_gate.py` with 3 hermetic tests.

### Step 6: Commit on develop

Single commit on `develop` branch.

## Specification-Derived Test Plan

| Test ID | Spec Coverage | Procedure | Expected Result |
|---------|---------------|-----------|-----------------|
| **T-bridge-1** | `GOV-FILE-BRIDGE-AUTHORITY-001` | `grep "Document: gtkb-gov-askuserquestion-enforcement-stack-slice-c" bridge/INDEX.md` | Match present |
| **T-spec-1** | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-gov-askuserquestion-enforcement-stack-slice-c-bridge-gate` | `preflight_passed: true` |
| **T-spec-2** | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | post-impl REPORT with executed evidence | Codex VERIFIED contingent |
| **T-out-of-applications-C** | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `git diff --name-only \| grep "^applications/"` | Empty |
| **T-hook-blocks-missing** | conditional gate fires on claim-without-section | `pytest test_owner_decisions_section_gate.py::test_hook_blocks_proposal_claiming_approval_without_section -v` | PASS — deny + reason mentions Owner Decisions |
| **T-hook-allows-present** | gate passes on claim-with-section | `pytest ::test_hook_allows_proposal_claiming_approval_with_section -v` | PASS — no Owner-Decisions deny |
| **T-hook-skips-non-claiming** | gate skips routine proposals | `pytest ::test_hook_does_not_fire_on_non_claiming_proposal -v` | PASS |
| **T-rule-file-bridge-protocol** (NEW per `-002` F1) | canonical bridge protocol documents the Owner Decisions / Input gate | `grep -c "Mandatory Owner Decisions / Input Section Gate" .claude/rules/file-bridge-protocol.md` | `1` |
| **T-rule-codex-review-gate** | `codex-review-gate.md` declares the requirement | `grep -c "Owner Decisions / Input Section Requirement" .claude/rules/codex-review-gate.md` | `1` |
| **T-rule-loyal-opposition** | `loyal-opposition.md` declares NO-GO obligation | `grep -c "Owner Decisions / Input" .claude/rules/loyal-opposition.md` | `≥ 1` |
| **T-platform-smoke** | platform integrity | `python -m pytest groundtruth-kb/tests/ -k "owner_decision or hook or rule" -x --timeout=60` | PASS (or pre-existing-known failures only) |

Test commands include `python -m pytest`, `python scripts/bridge_applicability_preflight.py`, `git`, `grep` to satisfy the spec-derived-testing-mandatory regex.

## Specification-to-Test Mapping

| Specification clause | Test ID(s) | Coverage |
|---------------------|------------|----------|
| `GOV-FILE-BRIDGE-AUTHORITY-001` | T-bridge-1 | Direct |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | T-spec-1 | Direct |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | T-spec-2 | Direct |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | T-out-of-applications-C | Direct |
| Hook conditional gate behavior | T-hook-blocks-missing, T-hook-allows-present, T-hook-skips-non-claiming | Direct |
| Bridge protocol documents Owner Decisions gate (per Codex `-002` F1) | T-rule-file-bridge-protocol | Direct (NEW) |
| Codex review gate rule extension | T-rule-codex-review-gate | Direct |
| Loyal Opposition rule extension | T-rule-loyal-opposition | Direct |
| Platform integrity | T-platform-smoke | Direct |

Every required spec has direct test coverage.

## Acceptance Criteria

- [ ] Codex GO on this Sub-slice C REVISED-1 proposal
- [ ] Preflight passes (T-spec-1)
- [ ] Hook conditional logic reviewed
- [ ] Rule additions reviewed for clarity (3 rule files: file-bridge-protocol.md, codex-review-gate.md, loyal-opposition.md)

VERIFIED when:

- [ ] All 11 tests T-bridge-1 through T-platform-smoke PASS with command output captured (was 10 in `-001`; T-rule-file-bridge-protocol added per `-002` F1)
- [ ] Codex VERIFIED on the post-impl REPORT
- [ ] Hook fires on claim-without-section AND skips on non-claiming
- [ ] Hook allows claim-with-section
- [ ] All 3 rule files contain the section requirement (T-rule-file-bridge-protocol + T-rule-codex-review-gate + T-rule-loyal-opposition)
- [ ] No regression in GT-KB platform tests

## Risk / Rollback

(Carry forward from `-001` risk table.) Rollback: `git revert` of the single commit reverses hook + 3 rule files + test changes atomically.

## Open Questions

| ID | Question | Resolution |
|----|----------|------------|
| OQ-C-1 | Marker specificity? | Conservative: 2 markers + self-citing detection |
| OQ-C-2 | Heading variant tolerance? | Allow `Owner Decisions / Input` and `Owner Decisions Input`; case insensitive; level 1-6 |
| OQ-C-3 | Placeholder rejection in section text? | Yes — reuse `SPEC_PLACEHOLDER_RE` |
| OQ-C-4 (NEW per `-002` F1) | Should canonical bridge protocol document the gate? | YES — added to Goal/Implementation/Test/Acceptance per Codex option 1 |

## Owner Decisions / Input

This sub-slice's authorization derives from S331 AskUserQuestion answers (umbrella priority + scope + autonomy) and Sub-slices A + B's VERIFIED enforcement infrastructure.

The owner answers cited as authorization for this sub-slice:

1. **AUQ #1 "Block ISOLATION-018; enforcement first"** — establishes enforcement-stack priority.
2. **AUQ #2 "Full 6-mechanism stack"** — confirms scope inclusion of Mechanism 4 (bridge gate).
3. **AUQ #3 "Autonomous progression"** — authorizes filing this sub-slice and revisions under standard lifecycle.

No additional owner input pending.

## Out of Scope

- Sub-slices D, E, F (subsequent stack work).
- Resolution of pre-existing scaffold-golden fixture mismatch.
- Code-fence-aware structural FP guards (deferred to Sub-slice A's named follow-up).

## Project Root Boundary Compliance

Operates entirely within `E:/GT-KB/`. Targets: `.claude/hooks/bridge-compliance-gate.py`, `.claude/rules/file-bridge-protocol.md`, `.claude/rules/codex-review-gate.md`, `.claude/rules/loyal-opposition.md`, `groundtruth-kb/tests/test_owner_decisions_section_gate.py`. No `applications/` content.

## Provenance

| Source | Reference |
|--------|-----------|
| Umbrella scoping | `bridge/gtkb-gov-askuserquestion-enforcement-stack-2026-05-04-003.md` |
| Sub-slice A VERIFIED | `bridge/gtkb-gov-askuserquestion-enforcement-stack-slice-a-hook-reenable-014.md` |
| Sub-slice B VERIFIED | `bridge/gtkb-gov-askuserquestion-enforcement-stack-slice-b-prime-rule-006.md` |
| Codex `-002` NO-GO | `bridge/gtkb-gov-askuserquestion-enforcement-stack-slice-c-bridge-gate-002.md` (F1: file-bridge-protocol.md missing as impl target) |
| Live probes | Read of `.claude/hooks/bridge-compliance-gate.py` (331 lines) (executed 2026-05-04 in this session) |

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
