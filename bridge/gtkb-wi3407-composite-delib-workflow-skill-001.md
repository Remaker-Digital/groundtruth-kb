NEW

# WI-3407 - Composite DELIB Workflow for Decision Capture Skill

bridge_kind: prime_proposal
Document: gtkb-wi3407-composite-delib-workflow-skill
Version: 001
Author: Prime Builder (Codex)
Date: 2026-07-06T01:52:00Z

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f337a-009a-7f51-8dce-b6c3f1d91b1c
author_model: GPT-5 Codex
author_model_version: gpt-5
author_model_configuration: interactive Prime Builder session; reasoning=xhigh; approval_policy=never

Project Authorization: PAUTH-GTKB-V1-RELEASE-STRATEGY-001-V1-RELEASE-STRATEGY-001-BOUNDED-IMPLEMENTATION-2026-06-23
Project: GTKB-V1-RELEASE-STRATEGY-001
Work Item: WI-3407

target_paths: [".claude/skills/decision-capture/SKILL.md", ".claude/skills/decision-capture/helpers/record_decision.py", ".codex/skills/decision-capture/SKILL.md", ".codex/skills/decision-capture/helpers/record_decision.py", "platform_tests/skills/test_decision_capture_skill.py", "platform_tests/scripts/test_generate_codex_skill_adapters.py", "platform_tests/scripts/test_groundtruth_governance_adoption.py"]

implementation_scope: skill_and_tests
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

WI-3407 turns the S363 composite owner-decision capture pattern into explicit
decision-capture skill guidance and helper coverage. The existing
`gtkb-decision-capture` skill records one owner decision as one Deliberation
Archive record; WI-3407 adds the higher-level workflow for the cases where
several AskUserQuestion answers form one coherent composite DELIB.

The implementation should teach the skill when to consolidate related AUQ
answers versus split them, define the composite content shape used by DELIB-2234
and DELIB-2238, and add tests so future agents preserve the Decisions table,
Composed Implications, Linked Artifacts, First Concrete Actions, source-ref
naming, AUQ-id naming, and collision/fixed-metadata guarantees. This does not
authorize any actual owner-decision record insertion during implementation, any
Deliberation Archive schema change, or any formal artifact mutation beyond the
skill/test files named in `target_paths`.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - protected skill/helper/test changes require bridge review, GO, implementation-start, implementation report, and verification.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - the v1 release-strategy project PAUTH includes WI-3407 and bounds the implementation.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - the PAUTH permits filing this proposal but does not bypass bridge GO or implementation-start.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - this proposal carries machine-readable PAUTH, project, and work item metadata.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal cites governing specification surfaces and maps them to verification.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the implementation report must prove the composite workflow through focused tests.
- `SPEC-2098` - the Deliberation Archive protocol governs search, citation, and durable owner-decision capture behavior.
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` and `ADR-CROSS-HARNESS-PARITY-001` - skill changes touching `.claude/skills/**` and `.codex/skills/**` require an explicit cross-harness parity disposition.
- `GOV-STANDING-BACKLOG-001` - WI-3407 remains the MemBase backlog authority for this work.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, and `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - owner decisions that cross from chat into durable project behavior should be preserved as governed artifacts with lifecycle clarity.

## Prior Deliberations

- `DELIB-2234` - S363 v1.0 release strategy decision set; exemplar for eight AUQ answers composed into one structured DELIB.
- `DELIB-2238` - S363 session-envelope convention decision; exemplar for a smaller confirmation AUQ captured into the same durable decision format.
- `DELIB-20265586` - owner-directed v1 release-strategy project authorization covering WI-3407.
- `DELIB-20260705-HIGH-PRIORITY-QUEUE-CONTINUE` - deferred WI-3407 until the WI-4482 / explicit-hint blocker completed; WI-4482 is now retired after VERIFIED evidence.
- `bridge/gtkb-skill-decision-capture-*.md` - prior baseline decision-capture skill implementation history; this proposal extends it rather than replacing the existing single-decision helper.

## Owner Decisions / Input

Owner approval is already recorded by `DELIB-20265586` and active project
authorization
`PAUTH-GTKB-V1-RELEASE-STRATEGY-001-V1-RELEASE-STRATEGY-001-BOUNDED-IMPLEMENTATION-2026-06-23`.
The original owner agreement that the S363 composite DELIB workflow should
become a skill is preserved in the WI-3407 backlog row with exemplars
`DELIB-2234` and `DELIB-2238`.

No fresh owner decision is required to file this proposal because the only
recorded blocker, WI-4482 / the explicit-hint program, is terminal:
WI-4482 is retired with verification evidence at
`bridge/gtkb-wi4482-formal-artifact-approval-004.md`.

## Requirement Sufficiency

Existing requirements sufficient. WI-3407 describes the source exemplars,
the consolidation/splitting decision to encode, the required content shape,
source-ref and AUQ-id naming, and the relationship to the existing
decision-capture skill. The active PAUTH supplies owner implementation
authorization for the bounded skill/test update.

## Cross-Harness Disposition

Claude Code: behavioral parity required. The canonical skill source lives at
`.claude/skills/decision-capture/SKILL.md`; implementation must update this
surface first and keep any helper changes compatible with the existing
`.claude/skills/decision-capture/helpers/record_decision.py` contract.

Codex: behavioral parity required. The Codex adapter under
`.codex/skills/decision-capture/` must be regenerated from the canonical Claude
skill source, and `scripts/generate_codex_skill_adapters.py --check` plus the
Codex skill-load smoke test must pass before an implementation report is filed.

Other registered harnesses: no direct harness-specific file mutation is
proposed in this slice. Their behavior remains covered by the shared canonical
skill text and future adapter-generation work where those harnesses expose skill
adapter surfaces. No waiver is requested.

## Spec-Derived Verification Plan

| Requirement | Verification |
|---|---|
| Composite owner decisions preserve DA protocol and prior-decision citations | Add or extend `platform_tests/skills/test_decision_capture_skill.py` to assert the skill documents when to consolidate versus split AUQ answers and requires prior deliberation/artifact links for composite records. |
| The helper preserves fixed Deliberation Archive metadata and collision behavior | Add helper-level tests around `record_decision.py` or new pure composer helpers proving fixed `source_type`, `outcome`, `changed_by`, `change_reason`, and collision failure remain intact. |
| The composite workflow encodes S363 structure | Tests assert the skill or helper output names the Decisions table, Composed Implications, Linked Artifacts, First Concrete Actions, source-ref naming, and AUQ-id naming. |
| Existing single-decision behavior remains available | Tests assert the current one-decision path remains documented and does not require composite fields when the owner decision is atomic. |
| Cross-harness skill parity is preserved | Run the Codex skill adapter generation check and skill-load smoke tests after editing the canonical Claude skill. |
| GroundTruth governance adoption still includes decision-capture files | Run the existing governance adoption test covering `.claude/skills/decision-capture/SKILL.md` and helper presence. |

```text
python -m pytest platform_tests/skills/test_decision_capture_skill.py -q --tb=short
python -m pytest platform_tests/scripts/test_generate_codex_skill_adapters.py platform_tests/scripts/test_codex_skill_load_smoke.py platform_tests/scripts/test_groundtruth_governance_adoption.py -q --tb=short
python scripts/generate_codex_skill_adapters.py --check
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi3407-composite-delib-workflow-skill --json
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi3407-composite-delib-workflow-skill
```

## Risk / Rollback

Risk is overfitting the skill to one historical S363 example or making every
owner decision feel like a heavyweight composite record. Keep the implementation
as guidance plus pure helper structure, preserve the atomic `record_decision`
path, and avoid any Deliberation Archive schema or live record mutation.
Rollback is a normal single-commit revert of the skill/helper/test changes and
regenerated adapter files.

## Bridge Filing

This proposal is filed under `bridge/` as the next status-bearing numbered
bridge file for `gtkb-wi3407-composite-delib-workflow-skill`; no prior version is deleted or rewritten
(append-only). Dispatcher/TAFE state plus the numbered file chain are the live
workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

feat - adds a new composite-decision workflow capability to the existing
decision-capture skill while preserving the baseline single-decision path.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
