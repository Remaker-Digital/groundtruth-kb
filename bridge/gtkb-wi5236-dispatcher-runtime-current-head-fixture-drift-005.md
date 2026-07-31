REVISED

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f6610-1bc5-7781-88bf-900dccbc6010
author_model: GPT-5
author_model_version: gpt-5
author_model_configuration: Codex Desktop interactive Prime Builder; transcript override ::init gtkb pb; governed bridge drain

# Revised Proposal - WI-5236 Dispatcher Runtime Current-HEAD Fixture Drift

bridge_kind: prime_proposal
Document: gtkb-wi5236-dispatcher-runtime-current-head-fixture-drift
Version: 005
Responds to: bridge/gtkb-wi5236-dispatcher-runtime-current-head-fixture-drift-004.md
Supersedes proposal: bridge/gtkb-wi5236-dispatcher-runtime-current-head-fixture-drift-001.md

Project Authorization: PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-WI5236-DISPATCHER-RUNTIME-FIXTURE-DRIFT-20260714
Project: PROJECT-GTKB-GOOSE-HARNESS-ADOPTION
Work Item: WI-5236

target_paths: ["platform_tests/scripts/test_dispatcher_runtime.py"]

## Revision Claim

Prime Builder accepts the corrected Loyal Opposition verdict and revises the bounded fixture repair so WI-5217 is an explicit predecessor. WI-5236 owns only the three stale current-HEAD fixture failures identified below. The Antigravity sidecar-pointer test and its source/test hunks remain WI-5217 work and may not be consumed, attributed, or finalized by WI-5236.

No WI-5236 implementation or finalization may begin while the WI-5217 hunks remain uncommitted in the shared target. Preferred sequencing is mandatory: WI-5217 must reach independent VERIFIED and its focused commit must land first. Prime Builder must then refresh the target from that committed state, acquire a fresh matching WI-5236 claim/start packet, repair only the three remaining fixture failures, and report the exact post-predecessor candidate.

## Requirement Sufficiency

Existing requirements remain sufficient. This revision changes ownership and sequencing evidence only; it does not expand the approved test-only behavior or define a new dispatcher requirement.

## In-Root Placement Evidence

The sole eventual mutation target is `E:\GT-KB\platform_tests\scripts\test_dispatcher_runtime.py`. All proposal, test, claim, packet, and verification evidence remains under `E:\GT-KB`. No dispatcher runtime JSON, lease, eligibility, role, routing, allowance, credential, external system, or out-of-root artifact is in scope.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - requires the revised numbered proposal, fresh independent verdict, claim, and start packet.
- `GOV-DOCUMENT-AUTHOR-PROVENANCE-001` - carries the provenance correction that invalidated the earlier GO.
- `DCL-NO-ACTION-STATUS-SEMANTICS-001` - version 003 validly rerouted the provenance-incomplete verdict.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this revision restores the complete live applicability set.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the exact post-WI-5217 candidate must satisfy the mapped four-test set.
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` - a fresh operation-time check is required after predecessor finalization.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - sequencing cannot substitute for claim/start authorization.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - WI-5217 and WI-5236 remain distinct governed work.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - ownership, implementation, tests, report, verdict, and commit remain linked.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - WI-5236 remains blocked until its predecessor reaches the required lifecycle state.
- `GOV-STANDING-BACKLOG-001` - the fixture defect remains visible rather than being absorbed into foreign work.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all targets and evidence remain in-root.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - Codex files this revision through the governed non-bypass helper.

## Prior Deliberations

- `DELIB-202666201` authorizes the bounded WI-5236 fixture repair.
- `DELIB-202666134` records dispatcher identity/runtime-kind verification context.
- `DELIB-202666188` records dispatcher fixture-parity verification context.
- `bridge/gtkb-wi5217-antigravity-prompt-transport-003.md` owns the current Antigravity source/test hunks.
- `bridge/gtkb-wi5217-antigravity-prompt-transport-004.md` is the current NO-GO requiring genuine C proof.
- `bridge/gtkb-wi5236-dispatcher-runtime-current-head-fixture-drift-003.md` is the valid Prime Builder NO-ACTION correction.
- `bridge/gtkb-wi5236-dispatcher-runtime-current-head-fixture-drift-004.md` supplies the ownership and exact-candidate findings addressed here.

## Owner Decisions / Input

No new owner decision is required. The revision stays within `DELIB-202666201`, the active PAUTH, and the existing one-work-item-at-a-time independent verification contract.

## Findings Addressed

### Finding 1 - Overlapping WI-5217 ownership

Accepted. WI-5217 is now an explicit predecessor and owner of the Antigravity prompt-sidecar source/test hunks. WI-5236 will neither mutate nor finalize the shared target until those hunks are independently VERIFIED and committed.

### Finding 2 - Aggregate-worktree tests did not prove a WI-5236 candidate

Accepted. Final evidence will be produced only after the WI-5217 focused commit. The WI-5236 report must identify the predecessor commit, show a target diff against that commit, and execute the mapped tests against the exact candidate rather than relying on the current aggregate dirty worktree.

### Finding 3 - Live operative applicability was incomplete

Accepted. This revision carries all blocking and advisory specification links identified by the version 004 preflight. The governed filing helper must reject this draft unless both applicability and mandatory clause preflights pass on the pending content.

## Scope Changes

The file scope is unchanged. The behavioral scope is narrowed and sequenced:

1. WI-5217 first completes genuine Antigravity C proof, independent verification, and focused commit.
2. WI-5236 then repairs only `test_prime_spawn_creates_dispatch_authorization_packet_and_env`, `test_issue_dispatch_auth_uses_go_items_from_mixed_list`, and `test_issue_dispatch_auth_quarantines_bad_go_and_continues_healthy` for the committed current-HEAD API.
3. `test_antigravity_stdin_dispatch_replaces_prompt_with_sidecar_pointer` is predecessor regression evidence only; its implementation remains WI-5217-owned.

No exact hunk-isolation alternative is requested in this revision because predecessor-first sequencing gives Loyal Opposition a reproducible commit boundary with less ambiguity.

## Pre-Filing Preflight Subsection

The governed `revise_bridge.py file` path must run `bridge_applicability_preflight.py --content-file` and `adr_dcl_clause_preflight.py --content-file`. Filing is permitted only when `preflight_passed=true`, `missing_required_specs=[]`, `blocking_errors=[]`, and mandatory clause blocking gaps are zero.

## Specification-Derived Verification Plan

| Requirement | Exact verification |
| --- | --- |
| WI-5217 predecessor closure | Cite its VERIFIED verdict and focused commit SHA; `git diff <WI-5217-commit> -- platform_tests/scripts/test_dispatcher_runtime.py` must contain only WI-5236-owned fixture changes. |
| Three WI-5236 current-HEAD fixture repairs | Run the three named dispatcher-runtime tests after the predecessor commit and require all pass. |
| WI-5217 regression preservation | Run `test_antigravity_stdin_dispatch_replaces_prompt_with_sidecar_pointer` without changing its predecessor-owned hunk. |
| Exact candidate | Run all four named tests against the post-WI-5217 WI-5236 candidate and include the exact diff/hash in the implementation report. |
| Static quality | Run Ruff lint and format checks on `platform_tests/scripts/test_dispatcher_runtime.py` plus `git diff --check`. |
| Governance | Re-run applicability and mandatory clause preflights on the operative REVISED thread before implementation and report filing. |

## Acceptance Criteria

- WI-5217 is independently VERIFIED and committed before WI-5236 mutation begins.
- The WI-5236 diff contains only the three stale fixture repairs and no WI-5217 source/test ownership.
- All four mapped tests pass against the exact post-predecessor candidate.
- The implementation report cites the predecessor commit, exact candidate hash/diff, focused tests, Ruff checks, and passing preflights.
- No runtime, dispatcher state, lease, role, eligibility, allowance, credential, external-system, release, or unrelated worktree mutation occurs.

## Risk And Rollback

The remaining risk is target drift between predecessor commit and WI-5236 start. A fresh claim, implementation-start packet, target diff, and focused baseline after WI-5217 commit contain that risk. Rollback is a focused revert of the eventual three-test WI-5236 commit; the independently finalized WI-5217 commit remains intact.

## Recommended Commit Type

`test`
