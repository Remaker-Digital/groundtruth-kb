NEW
author_identity: Codex Prime Builder
author_harness_id: A
author_session_context_id: 019f23f0-b16e-7481-8a18-9622ab564d50
author_model: GPT-5 Codex
author_model_version: gpt-5
author_model_configuration: interactive-default

bridge_kind: prime_proposal
Document: gtkb-wi4455-platform-tests-bridge-derived-spec-before-code
Version: 001
Date: 2026-07-04 UTC

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-4455

target_paths: ["groundtruth-kb/templates/hooks/spec-before-code.py", "groundtruth-kb/tests/test_governance_hooks.py"]
implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

# Implementation Proposal - WI-4455 bridge-derived platform_tests spec-before-code coverage

## Summary

Implement WI-4455 Option A by teaching the managed `spec-before-code` template hook to recognize bridge-derived Spec-to-Test Mapping evidence for `platform_tests/` files, while preserving existing `source_paths` behavior and keeping the active root recovery stub out of scope.

## Claim

Prime Builder proposes a bounded Reliability Fixes implementation slice for `WI-4455`. The slice corrects the managed template policy gap documented in the WI-4455 decision packet and approved as the preferred path by Loyal Opposition GO at `bridge/gtkb-wi4455-platform-tests-spec-before-code-policy-review-002.md`.

This proposal does not restore or edit active root `.claude/hooks/spec-before-code.py`; that recovery-stub restoration remains out of scope unless a later WI-4449/hook-restoration thread authorizes it.

## Requirement Sufficiency

Existing requirements are sufficient for this implementation proposal.

Evidence:

- `WI-4455` describes the concrete hook-layer defect: `platform_tests/` files can be spec-linked through bridge Spec-to-Test Mapping rather than per-file `source_paths`.
- `bridge/gtkb-wi4455-platform-tests-spec-before-code-policy-review-002.md` gives policy GO for Option A and states no additional owner input blocks filing an implementation proposal.
- `PROJECT-GTKB-RELIABILITY-FIXES` active membership now includes `WI-4455`.
- `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` is active and covers eligible active project members for `source`, `test_addition`, and `hook_upgrade` work through the normal bridge GO and verification gates.

## In-Root Placement Evidence

All target paths are inside the GT-KB project root:

- `groundtruth-kb/templates/hooks/spec-before-code.py`
- `groundtruth-kb/tests/test_governance_hooks.py`

The active root hook `.claude/hooks/spec-before-code.py` is intentionally out of scope.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - the proposal and later implementation report must remain in the numbered bridge chain, and bridge evidence is the authority surface this slice consumes.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - this proposal carries Project Authorization, Project, Work Item, and target_paths metadata.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - implementation is valid only because this proposal cites the governing specs and maps tests to them.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the implementation report must execute tests derived from these linked requirements before LO can verify.
- `GOV-STANDING-BACKLOG-001` - WI-4455 is the current open P0 work item and is advanced through governed backlog/project/bridge evidence rather than silently bypassed.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - the fix preserves bridge artifacts and MemBase roles as durable evidence surfaces instead of duplicating authority in ad hoc lists.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - Option A places platform test linkage in existing bridge evidence rather than creating a second source_paths mirror.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - the policy GO, implementation proposal, implementation report, and verification are lifecycle artifacts with explicit states.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - hook behavior must preserve the stdin/stdout contract used by cross-harness PreToolUse runners.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all implementation paths are GT-KB platform paths, not external or adopter-repository paths.
- `SPEC-AUQ-POLICY-ENGINE-001` - this proposal does not collect new owner input; it relies on the LO policy GO and existing project PAUTH rather than creating a prose decision path.

## Prior Deliberations

- `DELIB-S324-PB-INTERROGATION-DIRECTIVE` - Prime Builder verifies current GT-KB state before treating owner/project claims as implementation authority.
- `DELIB-S337-WORK-LIST-MD-DELETION-AT-MIGRATION-CONCLUSION` - MemBase is the standing backlog authority; WI-4455's open P0 state is therefore load-bearing.
- `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION` - owner direction behind the Reliability Fixes standing authorization used by this proposal.
- `bridge/spec-hygiene-spa-investigation-008.md` and `bridge/spec-hygiene-spa-remediation-006.md` - sibling HYG-class spec/test linkage rows WI-3183 and WI-3184 are terminal, leaving WI-4455 as the hook-layer counterpart.
- `independent-progress-assessments/loyal-opposition-log.md` 2026-06-13 WI-4455 entry - prior LO advisory found the active root hook stubbed while the managed template reproduced the `platform_tests/` advisory.
- `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-07-04-16-11-wi4455-platform-tests-spec-before-code-decision-packet.md` - current decision packet recommending Option A after live physical re-check.
- `bridge/gtkb-wi4455-platform-tests-spec-before-code-policy-review-002.md` - LO GO confirming Option A is acceptable and no additional owner input blocks this implementation proposal.

## Owner Decisions / Input

- `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` / `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION` - active standing authorization for eligible Reliability Fixes members.
- `bridge/gtkb-wi4455-platform-tests-spec-before-code-policy-review-002.md` - LO policy GO for Option A and for proceeding to this implementation proposal.

No new owner decision is requested by this proposal. If Loyal Opposition finds that WI-4455 is not eligible for Reliability Fixes standing authorization, the correct verdict is `NO-GO` with required project/PAUTH setup.

## Standing Backlog Review Packet Evidence

This proposal follows the current high-priority inventory and review packet chain rather than performing a bulk backlog operation. Evidence:

- `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/HIGH-PRIORITY-BACKLOG-TERMINALIZATION-2026-07-04.md` addendum inventories the current open P0/P1 set and identifies WI-4455 as the only P0.
- `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-07-04-16-11-wi4455-platform-tests-spec-before-code-decision-packet.md` is the WI-4455 review packet.
- `bridge/gtkb-wi4455-platform-tests-spec-before-code-policy-review-002.md` is the LO policy review outcome.

## Proposed Scope

1. Preserve the existing `source_paths` lookup behavior for all source files.
2. Add a narrowly scoped bridge-derived coverage path for `platform_tests/` Python files.
3. Treat a platform test path as covered only when bridge evidence explicitly references that test path through `target_paths`, Spec-to-Test Mapping, or equivalent status-bearing bridge content.
4. Require the bridge evidence to come from the in-root numbered bridge file chain and acceptable governed lifecycle evidence; do not read retired aggregate queue artifacts as authority.
5. Add focused tests in `groundtruth-kb/tests/test_governance_hooks.py` for valid mapped and invalid unmapped `platform_tests/` paths.
6. Keep active root `.claude/hooks/spec-before-code.py`, dispatcher runtime/config, MemBase schema, and formal specs out of scope.

## Spec-to-Test Mapping

| Spec | Verification |
| --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Focused hook tests create numbered bridge fixtures and prove the hook recognizes only explicit bridge evidence. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Implementation report carries this proposal's PAUTH/project/WI/target_paths metadata forward. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi4455-platform-tests-bridge-derived-spec-before-code --json` after filing must pass. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `python -m pytest groundtruth-kb/tests/test_governance_hooks.py -q --tb=short` covers mapped/unmapped bridge-derived behavior plus existing source_paths cases. |
| `GOV-STANDING-BACKLOG-001` | Implementation report cites the WI-4455 row and policy-review GO, and does not resolve the work item until LO verification. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | Tests invoke the hook through its stdin/stdout JSON contract, matching cross-harness PreToolUse behavior. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Tests and implementation remain under the in-root platform paths listed in target_paths. |

## Acceptance Criteria

- A `platform_tests/.../test_*.py` path with explicit bridge Spec-to-Test Mapping or target-path evidence no longer emits the false `No specification found covering ...` advisory.
- An unrelated `platform_tests/.../test_*.py` path without `source_paths` or bridge-derived evidence still emits the advisory.
- Existing no-source_paths, matching-source_paths, non-matching-source_paths, non-source-file, and migrated-DB tests continue to pass.
- No active root hook restoration, dispatcher/config mutation, MemBase schema mutation, or formal artifact insertion occurs in this slice.

## Risks / Rollback

Risk: overly broad bridge parsing could turn stale or unrelated bridge files into false coverage. Mitigation: tests must prove explicit path matching and leave unmapped files advisory-producing.

Risk: parsing the bridge file chain could become expensive. Mitigation: keep the lookup scoped to `platform_tests/` source files and simple textual/structured evidence in numbered bridge files.

Rollback: revert the changes to `groundtruth-kb/templates/hooks/spec-before-code.py` and `groundtruth-kb/tests/test_governance_hooks.py`. Bridge files and project membership records remain append-only audit evidence.

## Architecture Alignment Ledger

- OPS consolidation: resolves the remaining P0 hook-policy gap through explicit lifecycle evidence rather than silent backlog drift.
- Dispatcher daemon architecture: consumes numbered bridge evidence only; no dispatcher daemon or routing change is proposed.
- Lifecycle-first/scoring-last: establishes coverage/authority before any hook enforcement or scoring/ranking concern.
- Portfolio reconciliation: aligns the P0 work item, decision packet, policy GO, project membership, PAUTH, implementation proposal, and later verification as separate governed records.

## Files Expected To Change

- `groundtruth-kb/templates/hooks/spec-before-code.py`
- `groundtruth-kb/tests/test_governance_hooks.py`

## Recommended Commit Type

`fix`
