REVISED
::init gtkb lo
::open build

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f5f66-9582-7f03-a3f1-3c75e6bd9d0a
author_model: GPT-5
author_model_version: gpt-5
author_model_configuration: Codex Desktop interactive Prime Builder; transcript-defined ::init gtkb pb; governed proposal revision

bridge_kind: prime_proposal
Document: gtkb-wi5425-nonimpairment-test-membership-isolation
Version: 005
Responds to: bridge/gtkb-wi5425-nonimpairment-test-membership-isolation-004.md
Project Authorization: PAUTH-PROJECT-GTKB-TREE-STABILIZATION-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-TREE-STABILIZATION
Work Item: WI-5425
target_paths: ["platform_tests/hooks/test_modernization_nonimpairment_proposal_gate.py"]
implementation_scope: test
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

# Revised Implementation Proposal - Current-Head Envelope Fixture Completion

## First-Line Role Eligibility Check

PASS. Session `019f5f66-9582-7f03-a3f1-3c75e6bd9d0a` is transcript-defined
Prime Builder and holds the exact draft claim for this latest `NO-GO` thread.
`REVISED` is role-correct and grants no implementation authority.

## Revision Claim

Version 004 independently confirmed that the existing WI-5425 one-file
candidate is correctly scoped and that its membership-isolation behavior works.
It withheld `VERIFIED` only because the synthetic proposal fixture predates the
now-VERIFIED artifact-head envelope gate and therefore fails two active-hook
cases before reaching the behavior under test.

This revision preserves the existing reviewed `_wi_project_membership_gap`
isolation and exception-safe restoration hunk, then adds exactly two synthetic
proposal lines immediately after `NEW`:

```text
::init gtkb lo
::open build
```

Those lines make the fixture a valid dispatchable Prime-to-LO implementation
proposal under the current artifact-head contract. No production hook or
template hook changes are requested.

## Current Reproduction

At current HEAD, before this revision receives implementation authority:

```text
python -m pytest platform_tests/hooks/test_modernization_nonimpairment_proposal_gate.py -q --tb=short
```

reports `12 passed, 2 failed`. The two failures are:

- `test_proposal_without_structured_disposition_is_denied[active]`
- `test_proposal_with_structured_disposition_passes[active]`

Both return the artifact-head envelope denial requiring line 2
`::init gtkb lo` and line 3 `::open build`. The template-hook variants and the
new exception-restoration regressions pass. The one authorized target remains
the only dirty path in this scope; production hook targets are clean.

## Requirement Sufficiency

Existing requirements sufficient. Version 004 supplies the independent
root-cause evidence and expressly permits the same-file fixture correction
without a new owner decision. The active Tree Stabilization PAUTH permits test
mutation and preserves the normal bridge, claim, implementation-start,
independent verification, and focused finalization gates.

## Proposed Change

In the local `_proposal()` helper inside
`platform_tests/hooks/test_modernization_nonimpairment_proposal_gate.py`:

1. Preserve `NEW` as the first line.
2. Add `::init gtkb lo` as line 2.
3. Add `::open build` as line 3.
4. Preserve all existing author, project, PAUTH, WI, target, specification,
   requirement-sufficiency, cross-harness, and structured non-impairment
   fixture content.
5. Preserve the existing `_deny()` membership-isolation helper and
   `test_deny_restores_membership_check_when_content_gate_raises` exactly
   unless formatting requires no-semantic-change movement.

No gate ordering, membership enforcement, artifact-head validation,
production source, template source, database, dispatcher, TAFE, harness,
runtime state, or Git state changes are in scope.

## Intuitiveness/Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "WI-5425; TEST-11536; bridge/gtkb-wi5425-nonimpairment-test-membership-isolation-004.md; commit 35dfaf04",
  "canonical_authority": "GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001; ADR-BRIDGE-ARTIFACT-HEAD-ENVELOPE-001; DCL-BRIDGE-ENVELOPE-LINE-AUTHORING-PLACEMENT-001",
  "primary_route": "python -m pytest platform_tests/hooks/test_modernization_nonimpairment_proposal_gate.py -q --tb=short",
  "before_behavior": "The synthetic implementation proposal omits the mandatory artifact-head envelope, so two active-hook cases stop before the isolated non-impairment behavior is evaluated.",
  "after_behavior": "The synthetic proposal carries the current Prime-to-LO build envelope and all fourteen active/template isolation behaviors execute against their intended gate.",
  "self_descriptive_naming": "The fixture uses the literal canonical init keyword and build activity line required for an implementation proposal.",
  "obsolete_guidance_disposition": "The pre-envelope synthetic fixture shape is replaced in the one local helper; no production guidance or historical bridge file is rewritten.",
  "history_preservation": "The prior implementation report, NO-GO evidence, membership-isolation hunk, production gate behavior, and verified envelope commit remain queryable and unchanged.",
  "baseline": {
    "target_file_sha256": "2cdf298965965b5867e1d76cb3cbfae6b5a317de6343013eaca8c44d8993a517",
    "focused_result": "12 passed, 2 failed",
    "production_hook_dirty": false,
    "template_hook_dirty": false
  },
  "expected_result": {
    "focused_result": "14 passed, 0 failed",
    "production_hook_changed": false,
    "template_hook_changed": false,
    "membership_callable_restored": true
  },
  "rollback": {
    "instructions": "Remove only the two synthetic envelope lines if this candidate is rejected before finalization.",
    "verification": "Re-run the focused module and confirm production hook hashes and Git status remain unchanged."
  },
  "hard_invariants": [
    "one authorized test path only",
    "status token remains line 1",
    "init keyword is line 2 and build activity is line 3",
    "production membership enforcement remains unchanged",
    "membership callable is restored after normal and exceptional test paths",
    "no production hook, template hook, dispatcher, TAFE, harness, database, or Git mutation"
  ],
  "fail_closed_conditions": [
    "latest bridge status is not fresh GO",
    "implementation-start packet does not authorize the exact test path",
    "target hash differs before implementation",
    "either production hook becomes dirty",
    "focused module has any failure",
    "membership callable is not restored by identity"
  ],
  "essential_context_preservation": "Preserve the independently confirmed membership-isolation behavior, the verified artifact-head contract, all fourteen focused behaviors, and the one-test-path ownership boundary."
}
```

## Specification Links

- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001`
- `ADR-BRIDGE-ARTIFACT-HEAD-ENVELOPE-001`
- `DCL-BRIDGE-ENVELOPE-LINE-AUTHORING-PLACEMENT-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001`
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001`
- `ADR-CROSS-HARNESS-PARITY-001`
- `GOV-WORK-TREE-HYGIENE-001`
- `GOV-STANDING-BACKLOG-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`

## Prior Deliberations

- `DELIB-20260710-GTKB-MODERNIZATION-NONIMPAIRMENT-GOV-APPROVAL`
  approves the structured non-impairment control.
- `DELIB-202666274` supplies the project-scoped Tree Stabilization authority
  while preserving bridge and exact-operation gates.
- `bridge/gtkb-wi5425-nonimpairment-test-membership-isolation-001.md` and
  `-002.md` are the original proposal and GO for membership isolation.
- `bridge/gtkb-wi5425-nonimpairment-test-membership-isolation-003.md` is the
  prior implementation report whose current-head test claim became stale.
- `bridge/gtkb-wi5425-nonimpairment-test-membership-isolation-004.md` is the
  independent current-head NO-GO and exact correction authority.
- `bridge/gtkb-envelope-protocol-slice-b-bridge-writer-envelope-head-006.md`
  is the terminal verification for the artifact-head gate now reflected in the
  synthetic fixture.

## Owner Decisions / Input

No new owner decision is required. Version 004 explicitly identifies this
same-file correction as the preferred non-waiver path. This proposal requests
no waiver and does not change production behavior.

## Specification-Derived Verification

| Requirement | Verification | Expected result |
| --- | --- | --- |
| Structured non-impairment behavior | Run the complete focused module | `14 passed, 0 failed`. |
| Artifact-head placement | Assert the synthetic proposal's first three lines | `NEW`, `::init gtkb lo`, `::open build` in exact order. |
| Membership isolation | Existing active/template normal-path tests | Live project membership does not preempt the subject gate. |
| Exception restoration | Existing parameterized forced-exception regression | Original membership callable restored by identity for both hook modules. |
| Production non-impairment | Hash and Git-status checks for both hook files | No production/template hook mutation. |
| Exact scope | Git diff/status and `git diff --check` for the one target | Only the authorized test hunk is present. |
| Code quality | Ruff check, Ruff format check, and py_compile | All pass. |

Commands required before the implementation report:

```text
groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests/hooks/test_modernization_nonimpairment_proposal_gate.py -q --tb=short
groundtruth-kb\.venv\Scripts\ruff.exe check platform_tests/hooks/test_modernization_nonimpairment_proposal_gate.py
groundtruth-kb\.venv\Scripts\ruff.exe format --check platform_tests/hooks/test_modernization_nonimpairment_proposal_gate.py
groundtruth-kb\.venv\Scripts\python.exe -m py_compile platform_tests/hooks/test_modernization_nonimpairment_proposal_gate.py
git diff --check -- platform_tests/hooks/test_modernization_nonimpairment_proposal_gate.py
```

## Acceptance Criteria

1. The synthetic proposal carries the exact current artifact-head envelope.
2. All fourteen active/template focused tests pass.
3. Existing membership isolation and exception restoration remain intact.
4. Production and template hook bytes remain unchanged.
5. Only the one approved test path is dirty and eventually finalized.
6. The post-implementation report carries fresh current-head results and
   independent Loyal Opposition verification remains mandatory.

## Pre-Filing Preflight Evidence

The applicability and mandatory ADR/DCL clause preflights are executed against
this exact candidate immediately before filing. Filing is permitted only with
`preflight_passed: true`, no missing required or advisory specifications, no
blocking errors, and zero blocking clause gaps.

## Implementation Boundary

No test mutation may begin from this `REVISED` filing. Prime Builder must first
receive fresh independent `GO`, acquire the exact implementation claim, and
obtain successful implementation-start authorization for the one target path.
No dispatcher configuration change is authorized.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
