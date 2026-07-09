NEW

# gtkb-wi4897-release-gate-parity-hard-gate-alignment - Align release gate with verified parity hard gate

bridge_kind: prime_proposal
Document: gtkb-wi4897-release-gate-parity-hard-gate-alignment
Version: 001
Author: Codex Prime Builder
Date: 2026-06-28 UTC

author_identity: Codex Prime Builder
author_harness_id: A
author_session_context_id: 019f09c9-2db0-7b00-a337-40f998b07e56
author_model: GPT-5
author_model_version: GPT-5 Codex
author_model_configuration: Codex desktop; formal-release release-gate audit

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-4897

target_paths: ["scripts/release_candidate_gate.py", "platform_tests/scripts/test_release_candidate_gate.py"]

implementation_scope: source,test_update
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

Repair the release-candidate gate so it uses the verified cross-harness parity hard gate from WI-4892 Slice 6 instead of the retired legacy all-harness parity matrix.

The formal release audit found that `scripts/release_candidate_gate.py --skip-pip-audit --skip-frontend` still executes `scripts/check_harness_parity.py --all --markdown` and fails with `MISSING: 99` even though `scripts/parity_discovery_diff.py` is the verified CI/release hard gate and currently exits 0 with no unwaived asymmetries. This stale gate-command wiring blocks release readiness without representing an actionable parity defect in the current canonical hard gate.

The implementation is intentionally narrow: update the release-candidate configuration to use the parity discovery-diff script, update the release-gate unit tests to assert the canonical command, and verify the fast release gate advances past the parity phase. It does not edit harness registries, waivers, skill adapters, README, wiki, or dashboard code.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - protected source and test edits require a bridge GO and implementation-start authorization before mutation.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal links the governing specs and maps them to verification evidence.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - this proposal carries PAUTH, project, work item, and inline JSON target paths.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the implementation report and Loyal Opposition verdict must map linked specs to executed evidence.
- `GOV-STANDING-BACKLOG-001` - `WI-4897` is the durable backlog authority for this release-blocking defect.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - implementation is bounded by the active reliability-fixes project authorization.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - the release-blocking audit finding is promoted into a work item, bridge thread, implementation report, and verdict instead of remaining scratch knowledge.
- `ADR-CROSS-HARNESS-PARITY-001` - cross-harness behavior must be governed by the canonical parity invariant, not stale local release-gate wiring.
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` - release and CI parity enforcement must use the governed parity disposition mechanism and hard gate.

## Prior Deliberations

- `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION` - authorizes small reliability fixes in `PROJECT-GTKB-RELIABILITY-FIXES` through the standing PAUTH used here.
- `DELIB-S20260626-PARITY-IMPL-AUTHORIZATION` - authorized the cross-harness parity implementation program whose Slice 6 output this fix aligns with.
- `DELIB-20266285` - records the owner-approved batch-waiver posture for the parity program completed by Slice 6.
- `bridge/gtkb-cross-harness-parity-slice-6-coverage-audit-flip-004.md` - VERIFIED the Slice 6 coverage-audit flip, including `scripts/parity_discovery_diff.py` as the canonical hard gate.
- Formal release directive from the owner on 2026-06-27 - release-ready verified work should be separated from WIP/scratch, with outstanding nearly-complete release blockers driven to completion before main release.

## Owner Decisions / Input

No new owner decision is required for this proposal.

`WI-4897` is open/backlogged in `PROJECT-GTKB-RELIABILITY-FIXES`, depends on verified `WI-4892`, and is covered by active `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING`. The PAUTH is active, references owner decision `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION`, allows source and test-addition mutation classes, and forbids deploy, force-push, and spec deletion operations, none of which are in scope.

## Requirement Sufficiency

Existing requirements are sufficient.

The verified parity program already established `scripts/parity_discovery_diff.py` as the hard release/CI gate for unwaived parity asymmetries. This proposal does not reopen parity semantics; it aligns the local release-candidate gate with the verified Slice 6 release contract and current GitHub Actions workflow.

## Proposed Implementation

1. In `scripts/release_candidate_gate.py`, update the hard parity command configuration to use the discovery-diff script.
2. Update `platform_tests/scripts/test_release_candidate_gate.py` so the release-gate command-order tests assert the discovery-diff hard gate and do not preserve the stale legacy matrix expectation.
3. Keep `scripts/check_harness_parity.py` untouched. It can remain as an advisory/diagnostic tool; it should not be the release-candidate hard gate for the formal release.
4. File a post-implementation report with before/after command evidence and the exact release-gate result.

## Cross-Harness Disposition

No harness-surface adapter, hook, registry, or waiver is changed.

This is a release-gate wiring correction. It aligns the local release-candidate gate with the already-verified cross-harness parity hard gate and the current CI workflow. The release gate will continue to fail on unwaived discovery-diff asymmetries; it will no longer fail solely because the legacy registry matrix reports advisory/baseline coverage gaps that Slice 6 deliberately replaced as the hard gate.

## Spec-Derived Verification Plan

- `GOV-FILE-BRIDGE-AUTHORITY-001`: run implementation-start before editing and cite the resulting packet in the implementation report.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`: run `scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi4897-release-gate-parity-hard-gate-alignment` and expect `preflight_passed: true` with no missing required specs.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`: run `scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi4897-release-gate-parity-hard-gate-alignment` and expect zero blocking gaps.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`: execute the targeted unit and parity tests, then include the command outputs in the implementation report for independent verification.
- `GOV-STANDING-BACKLOG-001` and `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`: cite MemBase evidence that `WI-4897` is open in `PROJECT-GTKB-RELIABILITY-FIXES` and covered by active `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING`.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`: preserve the release audit finding as `WI-4897`, this bridge proposal, and a post-implementation report rather than as scratch-only context.
- `ADR-CROSS-HARNESS-PARITY-001` and `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001`: run `groundtruth-kb/.venv/Scripts/python.exe scripts/parity_discovery_diff.py` and expect PASS with zero unwaived asymmetries.

Concrete verification commands after implementation:

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_release_candidate_gate.py -q --tb=short
groundtruth-kb/.venv/Scripts/python.exe -m ruff check scripts/release_candidate_gate.py platform_tests/scripts/test_release_candidate_gate.py
groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check scripts/release_candidate_gate.py platform_tests/scripts/test_release_candidate_gate.py
groundtruth-kb/.venv/Scripts/python.exe scripts/release_candidate_gate.py --skip-pip-audit --skip-frontend
```

## Risk / Rollback

Risk is low and localized. The main risk is accidentally removing useful advisory visibility from the release gate, so the implementation should only change the hard parity command used by the release gate and should leave the legacy parity script available for advisory investigation.

Rollback is a single commit revert of the release-gate/test update. If the updated release gate exposes a later unrelated failure, that later failure should be handled as its own release-readiness finding rather than folded into this parity-command fix.

## Bridge Filing

This proposal is filed under `bridge/` as the first status-bearing numbered bridge file for `gtkb-wi4897-release-gate-parity-hard-gate-alignment`; no prior version is deleted or rewritten. Dispatcher/TAFE state plus the numbered file chain are the live workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

fix: align release-candidate parity gate with verified discovery-diff hard gate
