NEW
author_identity: codex-prime-builder
author_harness_id: A
author_session_context_id: 019f09c9-2db0-7b00-a337-40f998b07e56
author_model: GPT-5
author_model_version: Codex desktop
author_model_configuration: Codex desktop; WI-4893 recovery target amendment

# gtkb-wi4893-false-verified-finalization-recovery-test-target-amendment - Add stale hook regression test target

bridge_kind: prime_proposal
Document: gtkb-wi4893-false-verified-finalization-recovery-test-target-amendment
Version: 001
Author: Prime Builder (Codex harness A)
Date: 2026-06-29 UTC

Project Authorization: PAUTH-PROJECT-GTKB-DISPATCHER-RELIABILITY-WI-4893-FALSE-VERIFIED-RECOVERY
Project: PROJECT-GTKB-DISPATCHER-RELIABILITY
Work Item: WI-4893

target_paths: ["platform_tests/hooks/test_bridge_compliance_gate_spec_test_heading.py"]

implementation_scope: test-only stale regression fixture alignment
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

While executing the GO-approved false-VERIFIED recovery, the focused hook tests showed that `platform_tests/hooks/test_bridge_compliance_gate_spec_test_heading.py` still treats a VERIFIED verdict without `## Commit Finalization Evidence` as complete. The live hook now correctly blocks that body under the Mandatory VERIFIED Commit-Finalization Gate, so the test fixture must be updated to include finalization evidence when it asserts a complete VERIFIED verdict is allowed.

This amendment is intentionally narrow. It does not alter hook behavior, source code, dispatcher routing, or the already-GO'd implementation scope. It only authorizes updating the stale existing test fixture so the release test suite aligns with the new finalization requirement.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - protected hook tests require bridge GO and verification before release.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - implementation proposals must cite all relevant governing specifications.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - this proposal carries PAUTH, project, work item, and target_paths metadata.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - VERIFIED test fixtures must include spec-to-test evidence and executed command evidence.
- `.claude/rules/file-bridge-protocol.md` - Mandatory VERIFIED Commit-Finalization Gate requires terminal VERIFIED verdicts to include same-transaction commit evidence.
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` - hook/test behavior must stay aligned with helper finalization semantics.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - stale canonical-looking test artifacts must be corrected rather than documented around.

## Prior Deliberations

- `DELIB-20260628-WI4893-FALSE-VERIFIED-RECOVERY` - owner directive that the false VERIFIED mismatch is a release showstopper and must be corrected/diagnosed before release.
- `bridge/gtkb-wi4893-false-verified-finalization-recovery-001.md` - main recovery proposal.
- `bridge/gtkb-wi4893-false-verified-finalization-recovery-002.md` - GO for the main recovery proposal.

## Owner Decisions / Input

No new owner decision is required. This is a test-only target amendment inside the owner-authorized WI-4893 false-VERIFIED recovery scope.

## Requirement Sufficiency

Existing requirements are sufficient. The main WI-4893 recovery proposal and the Mandatory VERIFIED Commit-Finalization Gate already require this behavior; the only missing piece is target authorization for the stale existing test fixture.

## Implementation Plan

1. Update `platform_tests/hooks/test_bridge_compliance_gate_spec_test_heading.py` so its complete VERIFIED fixture includes a `## Commit Finalization Evidence` section with a same-transaction path set.
2. Keep the existing negative cases intact so missing spec-to-test and missing command evidence still fail.
3. Run `python -m pytest platform_tests/hooks/test_bridge_compliance_gate_spec_test_heading.py platform_tests/hooks/test_bridge_compliance_gate_finalization_evidence.py -q --tb=short` after the related finalization-evidence test file is added under the main recovery GO.

## Spec-Derived Verification Plan

| Specification | Required verification evidence |
| --- | --- |
| Mandatory VERIFIED Commit-Finalization Gate | `python -m pytest platform_tests/hooks/test_bridge_compliance_gate_spec_test_heading.py -q --tb=short` passes with a complete fixture that includes commit-finalization evidence. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Existing negative tests in the same file continue proving missing mapping and command evidence fail. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi4893-false-verified-finalization-recovery-test-target-amendment` reports `missing_required_specs: []`. |

## Risk / Rollback

Risk is limited to test fixture drift. Rollback is reverting the test-only amendment commit after the main recovery is verified, if Loyal Opposition finds the fixture update masks a real hook issue.

## Recommended Commit Type

test: this authorizes a stale regression fixture update only.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
