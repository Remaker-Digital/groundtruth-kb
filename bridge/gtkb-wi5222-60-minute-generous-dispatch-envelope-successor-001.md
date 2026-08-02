NEW

# WI-5222 - 60-minute generous dispatch envelope successor

bridge_kind: prime_proposal
Document: gtkb-wi5222-60-minute-generous-dispatch-envelope-successor
Version: 001
Date: 2026-07-13 UTC

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f5474-93a6-7f70-8e54-d6d8b0a31bb4
author_model: gpt-5.5
author_model_version: 5.5
author_model_configuration: Codex desktop interactive Prime Builder; fresh post-WI-5220 successor

Project Authorization: PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-WI5222-60M-GENEROUS-ALLOWANCE-20260713
Project: PROJECT-GTKB-GOOSE-HARNESS-ADOPTION
Work Item: WI-5222
Test: TEST-11376
target_paths: [".api-harness/routing.toml", "scripts/dispatcher_runtime.py", "platform_tests/scripts/test_cloud_harness_base.py", "platform_tests/scripts/test_alibaba_cloud_studio_harness.py", "platform_tests/scripts/test_ollama_harness.py", "platform_tests/scripts/test_openrouter_harness.py", "platform_tests/scripts/test_dispatcher_runtime.py", "platform_tests/scripts/test_gtkb_dispatcher_daemon.py", "platform_tests/scripts/test_lo_harness_turn_budget.py"]

## Claim

Adopt the owner-calibrated 60-minute model window as the new generous
dispatcher allowance. This fresh successor replaces the withdrawn first
attempt only after WI-5220 was independently VERIFIED and committed as
`89198140`, so its exact patch can be constructed against a stable fixture
baseline without importing unrelated dirty-worktree changes.

## Requirement Sufficiency

Existing requirements sufficient. The owner decision fixes the numerical
policy values, and the cited dispatch-envelope, centralized-dispatch,
cross-harness-parity, authorization, and worktree-hygiene requirements govern
the implementation and verification method.

## In-Root Placement Evidence

All implementation, tests, hunk patches, detached review roots, bridge
artifacts, and commit evidence remain under `E:/GT-KB`. No external project,
archive, harness scratchpad, runtime JSON, or lease file is an implementation
dependency.

## Specification Links

- `DCL-DISPATCH-ENVELOPE-RULES-001` - governs operation, session, turn, worker, and lease timing relationships.
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` - governs dispatcher worker lifetime and reconciliation behavior.
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` - requires the same policy across D, F, and H and common A/B/C/D/F/H workers.
- `GOV-HARNESS-ONBOARDING-CONTRACT-001` - requires truthful routing values for active provider harnesses.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - requires proposal, independent verdict, report, verification, and focused commit.
- `GOV-WORK-TREE-HYGIENE-001` - requires exact hunk isolation in the heavily dirty shared worktree.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - requires a live PAUTH, claim, and implementation-start packet.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - prohibits implementation before GO and packet issuance.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - requires concrete governing links.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - requires PAUTH, project, WI, TEST, and target paths.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - requires executed spec-derived verification before VERIFIED.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - preserves the owner calibration and failed predecessor as durable evidence.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - links decision, work item, test, bridge chain, source, and commit.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - the withdrawn first attempt requires a fresh successor lifecycle.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - keeps every artifact inside the mandatory project root.

## Prior Deliberations

- `DELIB-20260713-DISPATCH-60-MINUTE-GENEROUS-ALLOWANCE` - controlling owner decision: 60-minute model window, superseding the prior 8-hour value.
- `DELIB-20260711-WI5200-5202-HARNESS-REPAIR-AUTHORIZATION` - earlier generous-envelope and provider-recovery authorization.
- `DELIB-202666178` - prior Loyal Opposition review of the broad generous harness repair.
- `bridge/gtkb-wi5222-60-minute-generous-dispatch-envelope-004.md` - first-attempt NO-GO caused by uncommitted fixture dependency and exact-patch hygiene failures.
- `bridge/gtkb-wi5222-60-minute-generous-dispatch-envelope-005.md` - WITHDRAWN disposition requiring this fresh post-WI-5220 successor.
- `bridge/gtkb-wi5220-dispatcher-test-fixture-parity-006.md` - OpenRouter F VERIFIED verdict establishing the committed fixture baseline.

## Owner Decisions / Input

- `DELIB-20260713-DISPATCH-60-MINUTE-GENEROUS-ALLOWANCE` selects a 60-minute model window because only two successful historical runs exceeded 60 minutes.
- Preserve D/F/H per-operation timeouts at 900 seconds and turn budgets at 600.
- Preserve a 600-second session-to-worker wrap-up margin and a 300-second worker-to-lease/reset margin.
- This proposal uses the already approved PAUTH named above; no new owner decision is required.

## Proposed Scope

1. Set D, F, and H `session_timeout_seconds` from 28,800 to 3,600 while preserving `timeout_seconds = 900` and `max_turns = 600`.
2. Set the default A/B/C/D/F/H dispatcher worker lifetime from 29,400 to 4,200 seconds, preserving the 600-second D session-to-worker margin.
3. Preserve lease and reset derivation at worker lifetime plus 300 seconds, producing 4,500-second thresholds.
4. Update timer-policy comments, including the stale owner-authorized 8-hour comment, so prose and executable values agree.
5. Update only the corresponding assertions in the seven approved test modules across the nine approved target paths.
6. Build the implementation as exact hunk patches against post-WI-5220 `HEAD 89198140`, excluding every unrelated owner/session hunk.

Out of scope: model IDs, endpoints, credentials, routes, roles, eligibility,
ranking, provider retry behavior, verdict publication recovery, Antigravity
prompt transport, cleanup logic, circuit-breaker behavior, direct runtime-state
edits, and lease-file edits.

## Specification-Derived Verification Plan

| Specification / contract | Verification | Expected result |
| --- | --- | --- |
| `DCL-DISPATCH-ENVELOPE-RULES-001` | Provider routing tests | D/F/H resolve exactly to `900 / 3600 / 600` |
| `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` | Runtime and daemon lifetime tests | A/B/C/D/F/H default worker lifetime is 4,200 seconds |
| D session-to-worker margin | Direct routed-lifetime assertion | `3600 + 600 = 4200` |
| Lease/reset margin | Runtime lease and stale-run assertions | both thresholds are 4,500 seconds |
| Truthful telemetry | Existing configured lifetime/source assertions | emitted values and sources remain truthful |
| `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` | Seven approved test modules together | all pass against exact successor patch |
| `GOV-WORK-TREE-HYGIENE-001` | Detached reconstruction, patch check, name-status, whitespace gate | only nine approved paths and WI-5222-owned lines |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Pytest plus Ruff check/format | all pass before VERIFIED |

Focused test command:

`python -m pytest platform_tests/scripts/test_cloud_harness_base.py platform_tests/scripts/test_alibaba_cloud_studio_harness.py platform_tests/scripts/test_ollama_harness.py platform_tests/scripts/test_openrouter_harness.py platform_tests/scripts/test_dispatcher_runtime.py platform_tests/scripts/test_gtkb_dispatcher_daemon.py platform_tests/scripts/test_lo_harness_turn_budget.py -q --tb=short`

## Acceptance Criteria

- WI-5220 commit `89198140` is the exact implementation baseline.
- D/F/H resolve exactly to 900-second operations, 3,600-second sessions, and 600 turns.
- A/B/C/D/F/H default workers resolve to 4,200 seconds.
- A direct test proves D's configured 3,600-second session plus 600-second margin equals the 4,200-second routed lifetime.
- Lease TTL and reset straggler age resolve to 4,500 seconds.
- Timeout telemetry continues to report configured lifetime and source truthfully.
- The stale 8-hour source comment is removed or corrected.
- The exact staged patch contains only the nine approved paths and WI-5222-owned lines.
- All seven approved test modules, Ruff checks, formatting checks, and staged whitespace checks pass in a detached reconstruction.
- A genuine independent D, F, or H dispatcher-produced verdict closes the implementation report.

## Hunk-Scoped Finalization

Because approved paths contain unrelated dirty owner/session work, whole-file
staging is prohibited. The implementation report must name binary-safe hunk
patches, hashes, detached base, exact reconstructed blobs, and test results.
VERIFIED finalization must use the committed WI-5112 disposable-index helper
with `--hunk-patch` inputs and include only this bridge chain plus the reviewed
hunks.

## Risks / Rollback

The primary risk is timing-policy drift that prematurely stops healthy provider
runs or leaves leases longer than intended. Exact value assertions and margin
tests bound that risk. A focused revert of the eventual successor commit
restores the prior 8-hour policy without disturbing unrelated work; the
withdrawn predecessor and this successor remain append-only evidence.

## Files Expected To Change

- `.api-harness/routing.toml`
- `scripts/dispatcher_runtime.py`
- `platform_tests/scripts/test_cloud_harness_base.py`
- `platform_tests/scripts/test_alibaba_cloud_studio_harness.py`
- `platform_tests/scripts/test_ollama_harness.py`
- `platform_tests/scripts/test_openrouter_harness.py`
- `platform_tests/scripts/test_dispatcher_runtime.py`
- `platform_tests/scripts/test_gtkb_dispatcher_daemon.py`
- `platform_tests/scripts/test_lo_harness_turn_budget.py`

## Recommended Commit Type

`fix:`

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
