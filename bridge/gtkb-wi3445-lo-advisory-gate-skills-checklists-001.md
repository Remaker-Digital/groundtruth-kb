NEW
author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f3170-d706-77d3-b3e1-be39d47f3eda
author_model: GPT-5 Codex coding agent
author_model_version: GPT-5 family; exact runtime build not exposed in session context
author_model_configuration: Codex desktop session; Prime Builder override; approval_policy=never

# WI-3445 LO Advisory Gate Skills And Checklists

bridge_kind: prime_proposal
Document: gtkb-wi3445-lo-advisory-gate-skills-checklists
Version: 001
Author: Prime Builder (Codex, harness A)
Date: 2026-07-05 UTC

Project Authorization: PAUTH-PROJECT-LO-ADVISORY-OWNER-GRILLING-GATE-001-LO-ADVISORY-OWNER-GRILLING-GATE-IMPLEMENTATION
Project Authorization: PAUTH-PROJECT-LO-ADVISORY-OWNER-GRILLING-GATE-001-LO-ADVISORY-OWNER-GRILLING-GATE-001-BOUNDED-IMPLEMENTATION-2026-06-23
Project: PROJECT-LO-ADVISORY-OWNER-GRILLING-GATE-001
Work Item: WI-3445

target_paths: [".claude/rules/codex-review-operating-contract.md", ".claude/rules/codex-review-checklists.md", "groundtruth-kb/templates/project/codex-bootstrap/codex-review-operating-contract.md", ".claude/skills/codex-report/SKILL.md", ".claude/skills/lo-opportunity-radar/SKILL.md", ".claude/skills/loyal-opposition-hygiene-assessment/SKILL.md", ".codex/skills/codex-report/SKILL.md", ".codex/skills/lo-opportunity-radar/SKILL.md", ".codex/skills/loyal-opposition-hygiene-assessment/SKILL.md", "platform_tests/skills/test_lo_advisory_owner_grilling_gate.py"]

implementation_scope: rule_docs/skill_docs/generated_adapters/tests
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

WI-3445 is Slice 2 of the LO Advisory Owner-Grilling Gate project. Slice 1 established the rule-level gate and Slice 3 established lint enforcement. The remaining open work is to update the Loyal Opposition review contract, checklist, and advisory-emitting skills so advisory authors naturally produce the owner-grilling section before any adopt/adapt advisory can become an implementation proposal.

This proposal adds `Advisory Report` as a fifth required output mode, adds an advisory checklist, updates the three canonical LO-advisory-emitting skills, regenerates the Codex skill adapters from canonical Claude skill sources, and adds a focused regression test that locks the new mode/checklist/skill guidance in place.

## Specification Links

- `GOV-LO-ADVISORY-OWNER-GRILLING-GATE-001` - advisories classified `adopt` or `adapt` must include a Prime Builder owner-grilling gate before derived implementation proposals exist.
- `DCL-LO-ADVISORY-OWNER-GRILLING-GATE-001` - the skill/checklist wording must expose the gate shape that the lint can later detect.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - this proposal and LO verdict use the status-bearing numbered bridge chain.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - this proposal carries project, PAUTH, and WI metadata.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - all governing specs relevant to the implementation are cited.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - verification must include tests derived from the linked GOV/DCL requirements.
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` and `ADR-CROSS-HARNESS-PARITY-001` - canonical skill source edits must propagate to Codex adapters; no one-harness-only guidance drift is allowed.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` and `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - the active PAUTH authorizes the bounded work but does not bypass LO review or implementation-start authorization.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, and `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - advisory findings that imply future work must become durable artifacts with explicit lifecycle state.

## Prior Deliberations

- `INTAKE-e226b05a` - original owner requirement intake for the owner-grilling gate.
- `DELIB-S364-LO-ADVISORY-GRILLING-GATE-PROJECT-AUTH` - owner project authorization for the three-slice implementation.
- `DELIB-20265586` - snapshot-bound mass authorization that includes the currently open WI-3445 row.
- `bridge/gtkb-lo-advisory-owner-grilling-gate-009.md` - VERIFIED Slice 1 rule amendment.
- `bridge/gtkb-lo-advisory-owner-grilling-gate-slice3-lint-004.md` - VERIFIED Slice 3 lint work; this proposal fills the remaining Slice 2 authoring-surface gap.

## Owner Decisions / Input

No additional owner decision is required before LO review. Owner decisions already authorize:

- Rule home, gate scope, and skill targets from S364 AUQs.
- `PAUTH-PROJECT-LO-ADVISORY-OWNER-GRILLING-GATE-001-LO-ADVISORY-OWNER-GRILLING-GATE-IMPLEMENTATION`.
- Snapshot-bound WI-3445 continuation via `DELIB-20265586`.

## Requirement Sufficiency

Existing requirements are sufficient. WI-3445 explicitly names the contract/checklist/skill updates, and the GOV/DCL pair defines the required advisory gate behavior. No new specification is needed.

## Cross-Harness Disposition

No typed waiver is requested.

- Claude Code: canonical skill sources under `.claude/skills/` are direct targets and must receive the new advisory authoring guidance.
- Codex: `.codex/skills/**` files are generated adapters. Implementation must regenerate or directly synchronize the adapters from the canonical Claude skill sources while preserving adapter metadata.
- Cursor, Antigravity, Ollama, and OpenRouter: no direct skill file is targeted in this slice. Their parity obligation is that shared guidance remains anchored in the canonical review contract/checklist and any generated adapters continue to reflect canonical sources when those harnesses consume them.

Parity verification: tests must prove the canonical skill sources and Codex adapters include the owner-grilling gate guidance, and that generated adapter headers remain intact.

## Proposed Implementation

1. Update `.claude/rules/codex-review-operating-contract.md` so substantial Loyal Opposition work has five output modes, adding `Advisory Report` with adopt/adapt/reject/defer/monitor disposition language and owner-grilling-gate obligations.
2. Mirror the output-mode addition into `groundtruth-kb/templates/project/codex-bootstrap/codex-review-operating-contract.md` so new adopters inherit the current contract.
3. Update `.claude/rules/codex-review-checklists.md` with an `Advisory Report Checklist` that requires classification, owner-grilling gate presence for adopt/adapt, durable owner-decision routing, and next-artifact disposition.
4. Update canonical skill sources:
   - `.claude/skills/codex-report/SKILL.md`
   - `.claude/skills/lo-opportunity-radar/SKILL.md`
   - `.claude/skills/loyal-opposition-hygiene-assessment/SKILL.md`
5. Regenerate or directly sync generated Codex adapters so `.codex/skills/**/SKILL.md` reflects the canonical skill sources and retains adapter headers.
6. Add focused tests in `platform_tests/skills/test_lo_advisory_owner_grilling_gate.py` checking the fifth output mode, checklist, canonical skill guidance, and generated adapter parity.

## Spec-Derived Verification Plan

| Governing surface | Required behavior | Verification |
| --- | --- | --- |
| `GOV-LO-ADVISORY-OWNER-GRILLING-GATE-001` | Advisory authoring guidance requires a gate for adopt/adapt findings. | Test asserts contract, checklist, and skills include adopt/adapt owner-grilling gate language. |
| `DCL-LO-ADVISORY-OWNER-GRILLING-GATE-001` | Authoring surfaces expose machine-detectable section names and checklist obligations. | Test asserts the canonical `Required Prime Builder Owner-Grilling Gate` phrase appears in the checklist or skills and is not merely in an archived bridge file. |
| `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` | Codex adapters stay aligned with canonical Claude skill sources. | Test asserts generated adapters retain source headers and include the new advisory guidance. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | LO can verify with executed, spec-derived tests. | Implementation report includes pytest plus ruff check/format evidence. |

Minimum verification after GO:

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/skills/test_lo_advisory_owner_grilling_gate.py -q --tb=short
groundtruth-kb/.venv/Scripts/python.exe -m ruff check .claude/rules/codex-review-operating-contract.md .claude/rules/codex-review-checklists.md .claude/skills/codex-report/SKILL.md .claude/skills/lo-opportunity-radar/SKILL.md .claude/skills/loyal-opposition-hygiene-assessment/SKILL.md platform_tests/skills/test_lo_advisory_owner_grilling_gate.py
groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check platform_tests/skills/test_lo_advisory_owner_grilling_gate.py
```

If ruff does not accept markdown inputs in this repository, run ruff on Python targets and report markdown inspection/test coverage separately.

## Acceptance Criteria

- The review operating contract lists `Advisory Report` as a fifth output mode.
- The review checklist includes an advisory checklist covering classification and owner-grilling gate obligations.
- The three canonical LO-advisory-emitting skills guide authors to include the gate for adopt/adapt advisories.
- Generated Codex adapters are updated from canonical sources or explicitly synced without losing adapter metadata.
- Tests prove the new mode/checklist/skill guidance is present.
- No credential changes, release deployment, hook promotion, broad status mutation, or source behavior changes are in scope.

## Risk / Rollback

Risk is low. The work changes authoring guidance and tests, not runtime gate behavior. Rollback is a straightforward revert of documentation/skill/test changes. Main risk is adapter drift; mitigation is test coverage that compares canonical and generated surfaces.

## Bridge Filing

This proposal is filed under `bridge/` as the first version of `gtkb-wi3445-lo-advisory-gate-skills-checklists`. It does not rewrite the already VERIFIED Slice 1 or Slice 3 bridge chains.

## Recommended Commit Type

`docs:` because the implementation changes review/skill authoring guidance, with tests to prevent drift.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
