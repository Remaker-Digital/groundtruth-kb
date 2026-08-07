REVISED
::init gtkb pb
::open build

# Amend and decontaminate the live bridge authority family (WI-5193)

bridge_kind: prime_proposal
Document: gtkb-wi5193-file-bridge-authority
Version: 003
Author: Prime Builder (Claude, harness B)
Date: 2026-08-06 UTC
Responds to: bridge/gtkb-wi5193-file-bridge-authority-002.md

author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 7c5bf02a-db61-459e-9321-695a31696526
author_model: claude-opus-5
author_model_version: claude-opus-5
author_model_configuration: Claude Code interactive; resolved role prime-builder via ::init gtkb pb

Project Authorization: PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-ARTIFACT-DECONTAMINATION-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-PLATFORM-MODERNIZATION-ARTIFACT-DECONTAMINATION
Work Item: WI-5193

target_paths: ["scripts/check_file_bridge_authority.py", "platform_tests/scripts/test_check_file_bridge_authority.py"]

implementation_scope: source + focused test (deterministic bridge-authority checker)
kb_mutation_in_scope: false

**No KB mutation.** This proposal performs no MemBase write and does not modify
groundtruth.db. Its entire declared scope is the two source/test target paths
above (a deterministic checker and its focused test). The confirmation is stated
explicitly because the publication guard flags bridge-authority prose as
KB-mutation-shaped; groundtruth.db is deliberately NOT added to 	arget_paths,
since adding it would widen scope beyond the citation-only revision -002 asked
for.
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

WI-5193 is a P0, backlogged, open, unimplemented formal-family blocker in the
active project `PROJECT-GTKB-PLATFORM-MODERNIZATION-ARTIFACT-DECONTAMINATION`.
At HEAD `fcb4ebbb`, both declared target paths are ABSENT on disk:

- `scripts/check_file_bridge_authority.py` - the canonical assertion evaluator
  mandated by `GOV-FILE-BRIDGE-AUTHORITY-001` v3.
- `platform_tests/scripts/test_check_file_bridge_authority.py` - the focused
  executable coverage mandated by the same spec.

The two support tests already exist:
`platform_tests/groundtruth_kb/cli/test_bridge_state_report_cli.py` and
`platform_tests/hooks/test_bridge_compliance_gate_index_exemption.py`.

This proposal implements the six declared executable assertions
(`FILE-BRIDGE-AUTH-A1` .. `A6`) of `GOV-FILE-BRIDGE-AUTHORITY-001` v3 as a
deterministic checker plus a focused test, so that the GOV v3 lifecycle may
proceed to promotion once the companion dispositions and formal transition are
also governed. It does NOT itself promote the GOV, retire/supersede the
companion records, run the lifecycle transition, or grant implementation start
authority.

## Required Executable Assertions (from GOV-FILE-BRIDGE-AUTHORITY-001 v3)

| Assertion | Requirement the checker must implement |
|---|---|
| `FILE-BRIDGE-AUTH-A1` | Current document status is derived from numbered status-bearing files through the governed versioned-file reader. |
| `FILE-BRIDGE-AUTH-A2` | Live dispatch, lease, recipient, and runtime coordination is derived from TAFE/dispatcher state and cannot be inferred from a copied report or Markdown aggregate. |
| `FILE-BRIDGE-AUTH-A3` | `bridge/INDEX.md` is absent, cannot be generated or restored, and appears in load-bearing artifacts only as historical evidence or an explicit anti-regression guard. |
| `FILE-BRIDGE-AUTH-A4` | Startup, dashboard, report, and cache projections are mechanically classified as context-only and carry no queue/status authority. |
| `FILE-BRIDGE-AUTH-A5` | Unreadable, conflicting, duplicate, or malformed numbered-file/runtime state fails closed before actionability or mutation. |
| `FILE-BRIDGE-AUTH-A6` | Loyal Opposition repair authority is bridge-scoped, preserves append-only history and reviewer independence, and cannot authorize unrelated work or a same-session terminal review. |

The canonical assertion evaluator is `scripts/check_file_bridge_authority.py`;
the focused executable coverage is
`platform_tests/scripts/test_check_file_bridge_authority.py` together with the
current bridge state-report and compliance-gate tests.

## Claim

Prime Builder proposes a bounded implementation slice for `WI-5193`: a
deterministic checker and focused test covering the six GOV v3 assertions, and
keeps the bridge, project authorization, owner-decision, and verification gates
intact. This proposal is the bridge `prime_proposal` artifact only; it does not
authorize implementation start, a GO, or a claim.

## Requirement Sufficiency

Existing requirements are sufficient for filing this proposal. The six
declared assertions are fully specified in `GOV-FILE-BRIDGE-AUTHORITY-001` v3
(status=specified) and the exact source/test paths are declared there. The
bounded WI-5193 PAUTH is active, so no new or revised requirement is needed to
define the implementation boundary.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`:
`scripts/check_file_bridge_authority.py` and
`platform_tests/scripts/test_check_file_bridge_authority.py`. Both are
declared Source Paths in `GOV-FILE-BRIDGE-AUTHORITY-001` v3.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - defines the six required executable assertions and the canonical evaluator/test source paths this proposal implements.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - requires all relevant governing specifications to be linked here.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - requires the focused test to be executed and mapped to the six assertions before VERIFIED.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - binds WI-5193 to the active Artifact Decontamination project PAUTH.
- `ADR-TAFE-AUTHORITATIVE-BRIDGE-STATE-001` - companion record; governs live TAFE/dispatcher bridge-state authority and must receive a retirement/supersession disposition before GOV v3 promotion.
- `DCL-INDEX-GENERATED-VIEW-001` - companion record; governs the retired `bridge/INDEX.md` generated-view model and must receive a retirement/supersession disposition before GOV v3 promotion.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - preserves the artifact lifecycle and companion-disposition obligations.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - requires governed lifecycle transitions for the GOV and companion records.
- `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001` - requires deterministic, executable evidence for the checker and test.
- `GOV-GTKB-PUBLISHED-STATE-SOT-DEFERENCE-001` - the live read surfaces the checker must enforce over projections.
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` - requires the checker and test to preserve legitimate results and all hard invariants.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - keeps the platform checker and test out of adopter application scope and inside `E:\GT-KB`.
- `GOV-STANDING-BACKLOG-001` - keeps the blocker visible until the GOV is promoted and companions governed.

## Revision Basis

`-002` issued NO-GO on one blocking defect: "Independent review found blocking
unresolved template placeholders in Prior Deliberations."

The defect was a stale bridge-propose helper stub. The section carried four real,
substantive citations AND a trailing `### Helper-suggested candidates` subsection
still holding the helper's unedited placeholder line
`_No prior deliberations: <fill in reason before filing>._`. That is
self-contradictory on its face -- it asserts no prior deliberations exist directly
beneath four that do -- and it is exactly the unresolved-placeholder condition the
Prior Deliberations gate in `.claude/rules/codex-review-gate.md` exists to catch.

Fix 1: the placeholder subsection is removed. The four substantive citations are
retained verbatim and unaltered. This is a citation-only revision.

Fix 2 (guard-driven, non-scope): an explicit \kb_mutation_in_scope: false\ line plus a
no-KB-mutation confirmation are added, because the publication guard flags this
proposal's bridge-authority prose as KB-mutation-shaped while \	arget_paths\ declares
only source and test. This states what \-001\ already implied; it does not widen scope.

No other section of `-001` is changed: no scope, target-path, test-plan,
acceptance-criteria, or specification-link drift. `target_paths`,
`implementation_scope`, and the project/PAUTH/work-item bindings are carried
forward exactly as approved-for-review in `-001`.

## Prior Deliberations

- `DELIB-0880` - originating permanent LO bridge repair authority.
- `DELIB-20266119` - no-index operating-model decision.
- `DELIB-202666274` - authorizes modernization blocker and false-closure repairs at project scope while preserving mechanical-operation gates.
- Independent Gate 1.25 finding: `bridge/gtkb-modernization-gate-1-25-unified-foundation-design-review-001.md`.


## Owner Decisions / Input

The active bounded PAUTH
`PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-ARTIFACT-DECONTAMINATION-WI-5193-BRIDGE-AUTHORITY-20260711`
and the project-scope PAUTH
`PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-ARTIFACT-DECONTAMINATION-20260715-PROJECT-SCOPE`
both authorize this WI-5193 implementation proposal. No new owner decision is
required for proposal filing. This proposal does not itself authorize
implementation start, staging, commit, push, release, deployment,
dispatcher/TAFE mutation, harness mutation, credential lifecycle, destructive
cleanup, or external-system mutation.

## Proposed Scope

- Add `scripts/check_file_bridge_authority.py` as the canonical assertion
  evaluator implementing the six `FILE-BRIDGE-AUTH-A1`..`A6` assertions as a
  deterministic, rerunnable checker (exit/JSON contract consistent with the
  existing governed checker family).
- Add `platform_tests/scripts/test_check_file_bridge_authority.py` as focused
  executable coverage asserting each of the six assertions, including a
  fail-closed case for `A5` and an anti-regression `A3` case for `bridge/INDEX.md`.
- Leave the two support tests unchanged; the new focused test composes with them.

## Specification-Derived Verification Plan

| Spec | Verification |
| --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Run `scripts/check_file_bridge_authority.py` and the focused test; assert each of the six assertions (A1..A6) executes and passes on the current tree. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_check_file_bridge_authority.py -q --tb=short` plus the two support tests; all pass and map to the six assertions. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Bridge applicability preflight and clause preflight pass with no missing required/advisory specs. |
| `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001` | Checker output is deterministic and rerunnable (fixed exit/JSON contract), bound by SHA-256 inventory before report and before finalization. |
| `GOV-GTKB-PUBLISHED-STATE-SOT-DEFERENCE-001` | A4 assertion verifies projections are classified context-only with no queue/status authority. |
| `ADR-TAFE-AUTHORITATIVE-BRIDGE-STATE-001`; `DCL-INDEX-GENERATED-VIEW-001` | A2/A3 assertions enforce live TAFE/dispatcher authority and `bridge/INDEX.md` non-recreation; companion dispositions remain a separate governed follow-on. |
| `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` | All pre-existing state-report and compliance-gate tests continue to pass; no hard invariant is removed or weakened. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Clause preflight passes; all paths resolve under `E:\GT-KB`. |

## Acceptance Criteria

- `scripts/check_file_bridge_authority.py` exists and deterministically
  evaluates all six `FILE-BRIDGE-AUTH-A1`..`A6` assertions, failing closed on
  `A5` and flagging `A3` anti-regression for `bridge/INDEX.md`.
- `platform_tests/scripts/test_check_file_bridge_authority.py` exists and
  passes together with the two support tests, with one test per assertion.
- The GOV v3 is NOT promoted, and the companion records are NOT retired or
  superseded, by this proposal; those remain governed follow-on actions.

## Intuitiveness/Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001",
  "canonical_authority": "config/governance/modernization-release-candidate.json",
  "baseline": {
    "head": "fcb4ebbb",
    "target_paths_absent": [
      "scripts/check_file_bridge_authority.py",
      "platform_tests/scripts/test_check_file_bridge_authority.py"
    ],
    "support_tests_present": [
      "platform_tests/groundtruth_kb/cli/test_bridge_state_report_cli.py",
      "platform_tests/hooks/test_bridge_compliance_gate_index_exemption.py"
    ],
    "companion_records": "ADR-TAFE-AUTHORITATIVE-BRIDGE-STATE-001 v1 and DCL-INDEX-GENERATED-VIEW-001 v1 status=specified, superseded_by=null, retired_at=null"
  },
  "primary_route": "deterministic checker + focused test for the six GOV v3 assertions before lifecycle promotion",
  "before_behavior": "the canonical assertion evaluator and focused test are absent, so GOV-FILE-BRIDGE-AUTHORITY-001 v3 cannot be promoted",
  "after_behavior": "the six assertions are mechanically evaluable and covered; GOV v3 promotion remains gated on governed companion dispositions and the formal lifecycle transition",
  "self_descriptive_naming": "check_file_bridge_authority and test_check_file_bridge_authority name the bridge-authority checker and its focused test directly",
  "obsolete_guidance_disposition": "the retired aggregate model remains governed by the two companion records; this proposal does not silently cure any other load-bearing INDEX.md guidance",
  "history_preservation": "GOV v3, ADR-TAFE-AUTHORITATIVE-BRIDGE-STATE-001, and DCL-INDEX-GENERATED-VIEW-001 histories remain append-only and unmodified by this proposal",
  "expected_result": {
    "checker": "scripts/check_file_bridge_authority.py present and deterministic",
    "test": "platform_tests/scripts/test_check_file_bridge_authority.py present and passing",
    "support_tests": "both existing support tests unchanged and passing"
  },
  "rollback": {
    "instructions": "revert the two newly added files (checker and focused test) under separately authorized Git mechanics; no broad reset or unrelated cleanup",
    "test": "rerun the two support tests and the focused test; confirm the six assertions are again unimplemented"
  },
  "hard_invariants": [
    "no GOV v3 promotion occurs under this proposal",
    "no companion retirement/supersession occurs under this proposal",
    "no unrelated source or test file is modified",
    "all pre-existing state-report and compliance-gate behavior is preserved"
  ],
  "fail_closed_conditions": [
    "any assertion evaluator fails to detect a violation",
    "the focused test does not cover all six assertions",
    "a fourth path enters scope",
    "an active PAUTH, GO, claim, or start authority is absent at implementation time"
  ],
  "essential_context_preservation": "all existing numbered-file bridge authority, TAFE/dispatcher live state, and projection classification behavior are preserved"
}
```

## Risk / Rollback

Risk is moderate because this proposal authorizes later protected-file work
(`scripts/` and `platform_tests/scripts/`). The checker must fail closed on
unreadable/conflicting/duplicate/malformed state (`A5`) and the proposal must
fail closed around active PAUTH, GO, claim, and start authority before any
implementation begins. Rollback is the revert of the two newly added files
under separate Git mechanics; bridge files and project authorization records
are append-only audit artifacts and must not be deleted by rollback.

## Bridge Filing

This proposal is filed under `bridge/` as the next status-bearing numbered
bridge file for `gtkb-wi5193-file-bridge-authority`; no prior version is
deleted or rewritten (append-only). Dispatcher/TAFE state plus the numbered
file chain are the live workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Follow-on Note (required PAUTH / GO / claim / start + companion disposition / lifecycle transition)

Implementation may NOT begin until, in sequence: (1) this proposal receives an
independent Loyal Opposition `GO` verdict; (2) a matching Prime Builder claim
and work-intent are active under the bounded WI-5193 PAUTH; and (3) a matching
implementation-start gate is satisfied. After the checker and focused test are
independently VERIFIED, a separate governed follow-on must: (4) file
retirement/supersession dispositions for `ADR-TAFE-AUTHORITATIVE-BRIDGE-STATE-001`
and `DCL-INDEX-GENERATED-VIEW-001` (both currently status=specified,
superseded_by=null, retired_at=null); and only then (5) run the formal GOV
lifecycle transition to promote `GOV-FILE-BRIDGE-AUTHORITY-001` v3. None of
(1)-(5) is granted by this proposal.

## Recommended Commit Type

`feat` - adds the deterministic bridge-authority checker and its focused test
as the implementation prerequisite for GOV-FILE-BRIDGE-AUTHORITY-001 v3
promotion.

---
(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

---

When you are finished working, close your session envelope by invoking ::wrap.
