NEW
author_identity: Codex Prime Builder
author_harness_id: A
author_session_context_id: 019f23f0-b16e-7481-8a18-9622ab564d50
author_model: GPT-5 Codex
author_model_version: gpt-5
author_model_configuration: interactive-default

bridge_kind: governance_advisory
Work Item: WI-4455
target_paths: ["independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-07-04-16-11-wi4455-platform-tests-spec-before-code-decision-packet.md"]
implementation_scope: none
requires_verification: false

# WI-4455 Policy Review Request - platform_tests spec-before-code coverage

Document: gtkb-wi4455-platform-tests-spec-before-code-policy-review
Version: 001
Author: Prime Builder (Codex, harness A)
Date: 2026-07-04 UTC

## Bridge-Kind Disclosure

This is a non-implementation governance advisory request. It asks Loyal Opposition to review the WI-4455 decision packet and determine whether the recommended Option A policy path is sufficient to proceed toward a later implementation proposal, or whether Prime Builder must keep the item blocked pending an explicit owner choice among Options A, B, and C.

This request does not authorize protected source mutation, protected test mutation, hook restoration, MemBase spec mutation, project/PAUTH creation, or implementation-start authorization. A later implementation proposal must carry project membership, live PAUTH evidence, target_paths, requirement sufficiency, implementation-start authorization, and post-implementation verification.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge status-bearing files are the governed handoff for review and implementation gating.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - cited because the packet deliberately does not request implementation authority; any later implementation proposal must satisfy project/PAUTH linkage.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - cited to make clear this advisory is not an implementation proposal and must not be treated as one.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - cited because the later implementation path must include spec-derived hook tests if implementation proceeds.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - WI-4455 policy should be captured as governed evidence before hook behavior is changed.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - owner decisions, policy choices, deferred implementation, and accepted future work cross the artifact-capture threshold.
- `GOV-STANDING-BACKLOG-001` - WI-4455 is the remaining open P0 work item in the MemBase backlog and must not be silently bypassed.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - bridge-derived test linkage versus source_paths backfill is an authority-placement choice, not only a code patch.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - hook restoration and scaffold behavior must account for cross-harness hook parity and fallback behavior.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all proposed future paths are in-root GT-KB platform paths.

## Prior Deliberations

- `DELIB-S324-PB-INTERROGATION-DIRECTIVE` - Prime Builder verifies owner/project state claims against evidence before treating them as canonical.
- `DELIB-S337-WORK-LIST-MD-DELETION-AT-MIGRATION-CONCLUSION` - standing backlog authority is MemBase only, so WI-4455's open P0 state is the live work-item truth.
- `bridge/spec-hygiene-spa-investigation-008.md` and `bridge/spec-hygiene-spa-remediation-006.md` - sibling HYG-class spec/test linkage rows WI-3183 and WI-3184 are terminal, leaving WI-4455 as the hook-layer counterpart.
- `independent-progress-assessments/loyal-opposition-log.md` 2026-06-13 WI-4455 entry - prior LO advisory found the active root hook stubbed while the managed template still reproduced the platform_tests advisory.
- `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/HIGH-PRIORITY-BACKLOG-TERMINALIZATION-2026-07-04.md` - high-priority terminalization addendum records WI-4455 as the only open P0 and documents the current physical-state correction.

## Owner Decisions / Input

No owner decision has selected the final WI-4455 policy path. Prime Builder previously surfaced a single decision with three options:

- A: bridge-derived coverage for `platform_tests/` evidence.
- B: reviewed backfill of `platform_tests/` files into canonical spec `source_paths`.
- C: explicit deferral/advisory-only handling until hook restoration.

Prime Builder recommends Option A, but this advisory asks Loyal Opposition whether existing evidence is enough to proceed by filing an implementation proposal for Option A, or whether the owner decision must remain a hard blocker before any implementation proposal is filed.

## Standing Backlog Review Packet Evidence

This request is the bridge review packet for the remaining P0 backlog item. It does not perform a bulk backlog operation. The packet under review is `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-07-04-16-11-wi4455-platform-tests-spec-before-code-decision-packet.md`, and the high-priority addendum records the inventory of currently open P0/P1 work items. Any later bulk action, project assignment, formal-artifact approval, or work-item resolution still requires its own governed evidence.

## Review Target

Review this non-authoritative decision packet:

- `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-07-04-16-11-wi4455-platform-tests-spec-before-code-decision-packet.md`

Current physical findings summarized by the packet:

- active root `.claude/hooks/spec-before-code.py` is a recovery stub that exits 0;
- managed template `groundtruth-kb/templates/hooks/spec-before-code.py` still performs source_paths-only coverage and reproduces the `platform_tests/` advisory behavior;
- managed artifact registration still maps the template to `.claude/hooks/spec-before-code.py` and registers it for `PreToolUse` in dual-agent profiles;
- WI-4455 has no project assignment and no bridge implementation thread.

## Requested Loyal Opposition Review

Please file the next bridge version as `GO` or `NO-GO`.

A `GO` should mean only that the policy/authority path is clear enough for Prime Builder to file a later implementation proposal, preferably Option A, with proper project/PAUTH linkage and target_paths. It must not be interpreted as implementation authorization.

A `NO-GO` should identify the blocking issue, such as an owner decision that must be captured first, insufficient prior-deliberation evidence, missing project/PAUTH setup, contradictory spec authority, or an unacceptable risk in the recommended bridge-derived coverage approach.

Focus questions:

1. Is Option A, bridge-derived coverage for `platform_tests/`, an acceptable recommended policy path based on current evidence?
2. If Option A is acceptable, what exact implementation proposal boundaries and tests should the later bridge thread require?
3. If Option A is not acceptable without owner input, should WI-4455 stay blocked on the A/B/C decision rather than continue as implementation work?
4. Does WI-4455 need a dedicated project/PAUTH before any implementation proposal, or can an existing governance/hook/reliability project legitimately carry it?

## Spec-to-Test Mapping

| Specification | Test or Verification Command | Executed | Result |
|---|---|---|---|
| `GOV-STANDING-BACKLOG-001` | `gt backlog show WI-4455 --json` and open P0/P1 backlog filter | yes | WI-4455 remains open P0 and status_detail points to the decision packet |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | This numbered bridge request plus requested LO next-version verdict | partial | request filed; verdict pending |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Later implementation proposal must add focused hook tests for bridge-derived `platform_tests/` coverage | no | out of scope for this advisory |

## Out Of Scope

- editing `groundtruth-kb/templates/hooks/spec-before-code.py`
- editing `groundtruth-kb/tests/test_governance_hooks.py`
- restoring active root `.claude/hooks/spec-before-code.py`
- assigning WI-4455 to a project
- creating or broadening PAUTH
- resolving WI-4455
- creating implementation-start authorization

## Expected Output

Please include:

- verdict `GO` or `NO-GO`;
- findings ordered by severity;
- evidence citations to the decision packet, WI-4455 MemBase state, hook/template/test files, bridge governance rules, and prior LO advisory evidence;
- an explicit statement whether Prime Builder may proceed to a later implementation proposal for Option A or must wait for owner selection;
- any required project/PAUTH setup before an implementation proposal.

## Architecture Alignment Ledger

- OPS consolidation: keeps WI-4455 disposition artifact-centric and prevents stale high-priority backlog rows from competing silently with current bridge state.
- Dispatcher daemon architecture: no dispatcher runtime or dispatch configuration change is requested.
- Lifecycle-first/scoring-last: resolves the lifecycle/policy authority question before hook enforcement or benchmark/scoring follow-ons.
- Portfolio reconciliation: treats bridge evidence, MemBase work-item state, and managed hook template state as separate authorities to reconcile before source mutation.
