NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: codex-prime-20260623-wi22c078
author_model: GPT-5 Codex
author_model_version: gpt-5-codex
author_model_configuration: Codex desktop Prime Builder session; PowerShell; approval_policy_never

# WI-22C078 Attested Role Eligibility Test Guard

bridge_kind: prime_proposal
Document: gtkb-wi22c078-attested-role-eligibility-test-guard
Version: 001
Author: Prime Builder (Codex, harness A)
Date: 2026-06-23 UTC

Project Authorization: PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-BRIDGE-PROTOCOL-RELIABILITY-BOUNDED-IMPLEMENTATION-2026-06-23
Project: PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY
Work Item: WI-AUTO-SPEC-INTAKE-22C078

target_paths: ["platform_tests/scripts/test_dcl_role_resolution_authority_001.py"]

implementation_scope: test_addition
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

This proposal completes the currently implementable source/test slice of
`WI-AUTO-SPEC-INTAKE-22C078` by repairing the DCL role-resolution guard so it
continues to enforce the owner-selected attested-session-role model without
false-positive failures on unrelated application-state terminology.

The live source behavior already authorizes a dispatch keyword whose role mode
does not appear in the receiving harness's durable role set, while emitting
structured audit evidence. The focused behavior test
`platform_tests/scripts/test_strict_drop_misdirected_headless_dispatch.py`
passes and proves that both Claude and Codex receiver paths return
`DISPATCH_AUTHORIZED` with a `dispatch_role_mismatch_authorized` audit record.
The remaining defect is in
`platform_tests/scripts/test_dcl_role_resolution_authority_001.py`: its R5
registry-status guard scans for the bare substring `suspended`, so current
`scripts/cross_harness_bridge_trigger.py` terminology
`work_subject_application_suspended` trips the guard even though it is not a
harness registry status and does not invalidate bridge review eligibility on a
durable-role mismatch.

The proposed implementation tightens that test guard to detect actual registry
status or role-mismatch invalidation patterns while preserving the DCL's R5
intent: no gate may reject, drop, defer, or invalidate a bridge verdict,
dispatch, or work product solely because of a harness registry status or a
registry-vs-declared role disagreement.

This proposal does not modify `.claude/rules/operating-role.md`, GOV/SPEC/ADR,
DCL, PB, or REQ artifacts. Any narrative-rule correction for the historical
`STRICT_DROP` wording remains outside this PAUTH and requires its own
formal/narrative artifact approval path.

## Specification Links

- `SPEC-INTAKE-22c078` - Owner-stated requirement: bridge review eligibility is
  harness-agnostic; durable role is a fallback/routing source, not a review or
  verdict-validity gate.
- `DCL-ROLE-RESOLUTION-DECLARED-AUTHORITY-001` - Provides the R1-R5 role
  resolution assertions, including R5's rule that no gate invalidates work on a
  registry mismatch alone.
- `DCL-SESSION-ROLE-RESOLUTION-001` - Governs deterministic session role
  resolution and the durable-vs-session-stated role split.
- `GOV-SESSION-ROLE-AUTHORITY-001` - Governs durable registry authority for
  dispatch routing versus session-stated role authority for in-session surfaces.
- `ADR-INTERACTIVE-SESSION-ROLE-OVERRIDE-001` - Records the architectural split
  between interactive session role authority and durable harness role
  assignment.
- `ADR-ROLE-AUTHORITY-DECLARED-NOT-DETECTED-001` - Records the owner-declared
  role authority stance and the warn/audit-not-override model.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - Requires bridge state to flow through the
  versioned bridge file chain and governed dispatcher/TAFE state.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - Requires concrete
  specification linkage for implementation proposals.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - Requires the project
  authorization, project, and work item metadata present above.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - Requires the
  post-implementation report to carry forward spec-derived tests and executed
  evidence.
- `GOV-STANDING-BACKLOG-001` - Keeps `WI-AUTO-SPEC-INTAKE-22C078` as the
  durable work authority and prohibits silent backlog/status mutation.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - Governs the bounded project
  authorization cited above.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - Advises preserving the traceability
  chain between owner decision, requirement, work item, bridge proposal, test
  guard, and implementation report.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - Advises explicit lifecycle handling
  for deferred, verified, and retired artifacts; relevant because this proposal
  converts a deferred WI into an implementable source/test slice.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - Advises durable capture of owner
  decisions and implementation evidence; satisfied by the cited deliberations
  and this bridge thread.

## Prior Deliberations

- `INTAKE-b4928376` - Confirmed `SPEC-INTAKE-22c078` from the owner statement
  that bridge review eligibility is harness-agnostic and durable role must not
  gate review/verdict validity.
- `DELIB-20263189` - Owner authorization for the P1 dispatch-reliability spec
  batch including `WI-AUTO-SPEC-INTAKE-22C078`; preserved as background scope
  evidence.
- `DELIB-20260623-WI22C078-ATTESTED-SESSION-ROLE-REVIEW-ELIGIBILITY` - Owner
  decision in this session: proceed on the assumption that an owner/dispatcher-
  attested session role may satisfy bridge review eligibility even when the
  harness's durable role does not match the review duty.
- `DELIB-20265586` - Owner approval for the snapshot-bound
  `PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY` PAUTH used by this proposal.
- `bridge/gtkb-interactive-session-role-override-slice-10-regression-tests-005.md`
  through `-010.md` - Prior source/test work that already established the
  dispatch keyword mismatch row as `DISPATCH_AUTHORIZED` with audit evidence.

## Owner Decisions / Input

- `DELIB-20265586` authorizes bounded implementation for the snapshot-bound
  eight-member open set in `PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY`, including
  `WI-AUTO-SPEC-INTAKE-22C078`, with allowed mutation classes `source`,
  `test_addition`, `hook_upgrade`, `cli_extension`, and `scaffold_update`.
- `DELIB-20260623-WI22C078-ATTESTED-SESSION-ROLE-REVIEW-ELIGIBILITY` records
  the owner's specific tradeoff decision for this WI: proceed on the attested
  session-role assumption rather than keeping receiver-side durable-role
  membership as a review-eligibility blocker.

## Requirement Sufficiency

Existing requirements sufficient. `SPEC-INTAKE-22c078`,
`DCL-ROLE-RESOLUTION-DECLARED-AUTHORITY-001`,
`DCL-SESSION-ROLE-RESOLUTION-001`, `GOV-SESSION-ROLE-AUTHORITY-001`,
`ADR-INTERACTIVE-SESSION-ROLE-OVERRIDE-001`, and
`ADR-ROLE-AUTHORITY-DECLARED-NOT-DETECTED-001` already define the behavior and
the owner decision in
`DELIB-20260623-WI22C078-ATTESTED-SESSION-ROLE-REVIEW-ELIGIBILITY` resolves the
only outstanding policy tradeoff for this source/test slice.

New or revised formal requirements are not needed before repairing the test
guard. Formal or narrative artifact mutation remains out of scope.

## Spec-Derived Verification Plan

| Linked specification | Test / verification command | Expected evidence |
| --- | --- | --- |
| `SPEC-INTAKE-22c078`; `DCL-SESSION-ROLE-RESOLUTION-001`; `GOV-SESSION-ROLE-AUTHORITY-001` | `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_strict_drop_misdirected_headless_dispatch.py -q --tb=short` | Both dispatch receivers authorize durable-role-mismatched canonical dispatch keywords with audit evidence. |
| `DCL-ROLE-RESOLUTION-DECLARED-AUTHORITY-001`; `ADR-ROLE-AUTHORITY-DECLARED-NOT-DETECTED-001` | `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_dcl_role_resolution_authority_001.py -q --tb=short` | R1-R5 executable assertions pass; R5 remains a guard against actual registry-status/role-mismatch invalidation and no longer false-positives on `work_subject_application_suspended`. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `groundtruth-kb/.venv/Scripts/python.exe -m ruff check platform_tests/scripts/test_dcl_role_resolution_authority_001.py` and `groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check platform_tests/scripts/test_dcl_role_resolution_authority_001.py` | The touched Python test file passes lint and format checks. |

## Risk / Rollback

Risk is low and localized to one regression-test file. The main risk is
over-relaxing the R5 guard so it stops catching actual registry-status
invalidation. The implementation must therefore add a positive fixture or
pattern check showing actual registry-status invalidation text still fails the
guard, while allowing unrelated application-state identifiers.

Rollback is a single-file revert of
`platform_tests/scripts/test_dcl_role_resolution_authority_001.py`.

## Bridge Filing

This proposal is filed as
`bridge/gtkb-wi22c078-attested-role-eligibility-test-guard-001.md` through the
governed bridge writer. No prior bridge version for this slug is deleted or
rewritten. Dispatcher/TAFE state plus the numbered bridge file chain remain the
live workflow state.

## Recommended Commit Type

`test:` - the implementation is expected to modify only a regression-test guard
while preserving existing source behavior.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
