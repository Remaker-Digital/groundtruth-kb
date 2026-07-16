NEW

# Restore active/template non-impairment proposal-gate parity

bridge_kind: prime_proposal
Document: gtkb-wi5166-nonimpairment-proposal-gate-parity
Version: 001
Author: Prime Builder (Codex A)
Date: 2026-07-16T19:08:00Z

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f5f6d-60cd-7040-b73f-c7d23757c4bc
author_model: Codex
author_model_version: GPT-5
author_model_configuration: Codex Desktop, Prime Builder, high reasoning

Project Authorization: PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE
Work Item: WI-5166

target_paths: [".claude/hooks/bridge-compliance-gate.py", "groundtruth-kb/templates/hooks/bridge-compliance-gate.py", "platform_tests/hooks/test_modernization_nonimpairment_proposal_gate.py"]

implementation_scope: governance, protocol, test
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

Restore the structured modernization non-impairment proposal gate in the live
hook without replacing the shared file. The modified canonical template already
contains the heading/constants block, `_nonimpairment_disposition_gap`
validator, and proposal denial path required by
`GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001`; the active
`.claude/hooks/bridge-compliance-gate.py` contains none of those blocks. The
focused current suite therefore reports four active-hook failures and four
template passes. Frozen `AT-AUTHORITY-CARRIERS` reports one failure and two
passes because assertion A1 finds zero occurrences of
`Intuitiveness/Non-Impairment Disposition` in the active hook.

Adopt the pre-existing template/test candidates, sync only the three
non-impairment blocks into the active projection, and extend the focused test
with integration assertions proving the live proposal denial path. Applicable
proposals must contain exactly one fenced JSON disposition with all required,
non-placeholder fields. Missing, malformed, ambiguous, incomplete, or
placeholder evidence must fail closed with an actionable diagnostic. Preserve
all concurrent hook behavior and unrelated template/test hunks.

## Specification Links

- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` — directly requires cross-cutting proposals to carry an intuitiveness/non-impairment disposition and missing hard-invariant evidence to block verification/closure.
- `GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001` — requires this cross-cutting requirement to be mechanically enforced rather than left as prose.
- `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001` — requires every frozen authority carrier, including the non-impairment GOV, to evaluate deterministically from live sources.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` — requires the protected hook/test repair to execute under active project authority.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` — confirms project PAUTH does not replace independent GO, claim/start, or VERIFIED.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — governs the proposal/GO/claim/start/report/VERIFIED lifecycle and exact three-path scope.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — requires every relevant specification to be linked here.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — binds WI-5166 to the active Assurance project PAUTH.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — requires focused denial-path, carrier, and hook-regression evidence before VERIFIED.
- `DCL-PROJECT-DEPENDENCY-ORDERING-001` — requires hunk-only synchronization that preserves concurrent shared-hook/template work.
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` — requires hook-surface proposals to declare behavioral parity or a typed owner waiver for every applicable harness.
- `ADR-CROSS-HARNESS-PARITY-001` — requires equivalent governance behavior across harnesses even where their invocation adapters differ.
- `GOV-STANDING-BACKLOG-001` — keeps WI-5166 visible until exact implementation and acceptance evidence are independently verified.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — requires all live hook, template, test, and evidence paths to remain inside `E:\GT-KB`.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — links the GOV, hook/template projections, tests, work item, and verification evidence.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — keeps the repair lifecycle distinct from the earlier formal GOV recording.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — requires the RC defect and its repair to remain durably traceable.

## Prior Deliberations

- `DELIB-20260710-GTKB-MODERNIZATION-NONIMPAIRMENT-GOV-APPROVAL` — owner approval for the exact non-impairment GOV whose mechanical A1 enforcement is missing from the active hook.
- `DELIB-20260710-GTKB-MODERNIZATION-GATE-1-FORMAL-LANGUAGE-DRAFT` — owner-reviewed formal-language basis for the required structured evidence fields.
- `DELIB-202666274` — authorizes all required modernization blocker repairs at project scope while retaining mechanical-operation restrictions.

## Owner Decisions / Input

The governing GOV was owner-approved in
`DELIB-20260710-GTKB-MODERNIZATION-NONIMPAIRMENT-GOV-APPROVAL`, and
`DELIB-202666274` authorizes required Assurance project repairs. Active
`PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE-20260715-PROJECT-SCOPE`
covers the three target classes. No new owner decision is required. This
proposal does not request staging, commit, push, release, deployment,
dispatcher/TAFE mutation, harness mutation, credential lifecycle, destructive
cleanup, or external-system mutation.

## Requirement Sufficiency

Existing requirements sufficient. The approved non-impairment GOV, frozen
carrier assertions, canonical template implementation, and focused executable
tests completely define the repair. No new or revised requirement is needed.

## Intuitiveness/Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001",
  "canonical_authority": "GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001",
  "primary_route": "governed bridge proposal plus exact implementation-start authority",
  "before_behavior": "the template rejects deficient dispositions but the live hook silently lacks the validator and denial path",
  "after_behavior": "active and template hooks deterministically enforce the same complete structured disposition contract",
  "self_descriptive_naming": "NONIMPAIRMENT constants and _nonimpairment_disposition_gap identify the governed evidence and result",
  "obsolete_guidance_disposition": "no alternate guidance is activated; the template remains the canonical projection source and the active hook matches it",
  "history_preservation": "prior hook and template history remains in Git and the numbered bridge lifecycle remains append-only",
  "baseline": {
    "focused_tests": "4 active failures and 4 template passes",
    "authority_carriers": "1 failure and 2 passes"
  },
  "expected_result": {
    "focused_tests": "all active and template cases pass including denial-path integration",
    "authority_carriers": "all 3 tests pass"
  },
  "rollback": {
    "instructions": "remove only the WI-5166 active-hook hunk and focused-test additions while preserving foreign shared-file hunks",
    "test": "rerun focused and frozen authority-carrier commands"
  },
  "hard_invariants": [
    "missing or unreliable required evidence fails closed",
    "bridge GO, work-intent, implementation-start, and independent verification remain mandatory",
    "active and template hook behavior remains in parity"
  ],
  "fail_closed_conditions": [
    "section absent",
    "not exactly one fenced JSON object",
    "missing required field",
    "empty or placeholder field",
    "active/template behavioral divergence"
  ],
  "essential_context_preservation": "all existing hook checks and concurrent shared-file changes remain intact outside the exact three synchronized blocks"
}
```

## Cross-Harness Disposition

No parity waiver is requested.

| Harness / surface | Disposition |
|---|---|
| Claude Code | The live `.claude/hooks/bridge-compliance-gate.py` directly enforces the structured disposition during proposal writes. |
| Codex | The governed Codex non-bypass proposal writer audits candidate content through the same live gate before writing. |
| Cursor, Antigravity, Ollama, OpenRouter, Alibaba | Their governed bridge CLI/skill proposal paths use the canonical active gate contract; no harness-specific weakening or alternate validator is introduced. |
| Packaged/new GT-KB hosts | `groundtruth-kb/templates/hooks/bridge-compliance-gate.py` carries behaviorally identical constants, validator, and denial path for projection. |

Invocation adapters may differ, but all applicable harness paths must accept the
same complete disposition and reject the same absent, ambiguous, malformed,
incomplete, or placeholder evidence.

## Spec-Derived Verification Plan

| Governing specification | Verification evidence | Expected result |
|---|---|---|
| `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001`; `GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001` | `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/hooks/test_modernization_nonimpairment_proposal_gate.py -q --tb=short` | Active and template helper cases plus live denial-path integration all pass. |
| `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001` | `groundtruth-kb/.venv/Scripts/python.exe scripts/check_artifact_evaluability.py --spec GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001 --json` and frozen `AT-AUTHORITY-CARRIERS` | Carrier aggregate is PASS; all 3 frozen tests pass; A1 finds the live hook evidence. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`; `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`; `GOV-FILE-BRIDGE-AUTHORITY-001` | Mandatory proposal preflights, matching claim/start packet, and independent post-implementation report | Exact three-path authority is present and no project-PAUTH bypass occurs. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`; `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`; `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Applicability/clause preflights and report spec-to-test mapping | No missing required/advisory specs or blocking clause gaps; every linked spec has observed evidence. |
| `DCL-PROJECT-DEPENDENCY-ORDERING-001` | Fresh pre-start SHA-256 inventory and hunk-level active/template diff | Only the three non-impairment blocks and focused integration tests are attributable; all foreign hunks remain unchanged. |
| `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001`; `ADR-CROSS-HARNESS-PARITY-001` | `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_bridge_compliance_gate_disposition.py platform_tests/hooks/test_modernization_nonimpairment_proposal_gate.py -q --tb=short` | Harness-surface disposition gate remains enforced and active/template non-impairment behavior is identical. |
| `GOV-STANDING-BACKLOG-001`; `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`; `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`; `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | WI-5166 history and numbered proposal/report/verdict chain | The repair remains open until exact implementation is independently VERIFIED and finalized. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Mandatory clause preflight and path inventory | `CLAUSE-IN-ROOT` passes and all dependencies resolve under `E:\GT-KB`. |

## Risk / Rollback

The active hook is a shared enforcement surface. A whole-file template copy
could overwrite unrelated active-only or concurrent logic, while a partial
copy that omits the denial call site would make unit tests pass without actual
enforcement. Implementation must rehash all three targets, transplant the exact
constants, validator, and denial-path blocks, and then compare active/template
behavior through the focused parametrized tests. The modified template and
untracked focused test are pre-existing candidates; GO may adopt them only at
their verified pre-start bytes plus attributable test additions. Rollback is
the exact active-hook hunk and focused-test integration additions only.

## Bridge Filing

This proposal is filed under `bridge/` as the next status-bearing numbered
bridge file for `gtkb-wi5166-nonimpairment-proposal-gate-parity`; no prior version is deleted or rewritten
(append-only). Dispatcher/TAFE state plus the numbered file chain are the live
workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

`fix` — restores missing live enforcement for an already approved governance
contract.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
