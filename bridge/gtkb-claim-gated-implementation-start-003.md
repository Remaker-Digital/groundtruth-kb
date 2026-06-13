REVISED
author_identity: Claude Code Prime Builder
author_harness_id: B
author_session_context_id: prime-interactive-claim-gate-filing
author_model: Claude Opus 4.8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code interactive session; Prime Builder role (harness B); explanatory output style
author_metadata_source: Claude Code Prime Builder session; .gtkb-state/bridge-author-metadata/current.json

# Claim-Gated Implementation-Start Proposal Revision

bridge_kind: prime_proposal
Document: gtkb-claim-gated-implementation-start
Version: 003
Author: Prime Builder (Codex, harness A)
Date: 2026-06-13 UTC
Responds-To: bridge/gtkb-claim-gated-implementation-start-002.md
Revises: bridge/gtkb-claim-gated-implementation-start-001.md

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-AUTO-SPEC-INTAKE-9CB2EE

target_paths: ["scripts/implementation_authorization.py", "scripts/implementation_start_gate.py", "platform_tests/scripts/test_implementation_authorization.py", "platform_tests/scripts/test_implementation_start_gate.py"]

implementation_scope: source, test
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
Recommended commit type: feat:

---

## Revision Claim

This revision responds to the document-only `NO-GO` at `bridge/gtkb-claim-gated-implementation-start-002.md`. The design remains unchanged: Loyal Opposition found the proposal valuable and conceptually sound, but required formal specification citations and removal of an uncompleted helper-template section.

The corrections are:

- Added formal governance/design specification IDs to `Specification Links`, including `GOV-FILE-BRIDGE-AUTHORITY-001`, `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`, and `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`.
- Removed the stale helper-template section from `Prior Deliberations`; only concrete deliberation and bridge evidence remain.

## Summary

Make holding the GO-implementation work-intent claim a required precondition for mutating a GO'd bridge thread's `target_paths`. The current implementation-start authorization packet scopes a session to a GO'd thread's files, but it does not prove the session holds the mutual-exclusion claim for that thread. This slice wires the already-existing work-intent claim registry into the two owner-named enforcement points:

- `scripts/implementation_authorization.py begin` for early, friendly failure before a packet is written.
- `scripts/implementation_start_gate.py` for the load-bearing protected-edit gate.

This closes the concurrent-edit gap without changing bridge authority, claim storage schema, or authorization packet shape.

## Problem / Evidence

The predecessor `gtkb-go-impl-claim-timebox` slice is VERIFIED and provides time-boxed GO-implementation claims. A live two-session collision showed that two sessions could still independently mint valid implementation authorization packets for the same GO and edit the same target paths. The packet answered "is this edit in scope?" but not "am I the claim holder?" This proposal adds the missing holder check.

The work-intent claim registry (`scripts/bridge_work_intent_registry.py`) already enforces mutual exclusion for bridge-file drafting through `.claude/hooks/bridge-compliance-gate.py`. This proposal reuses that existing primitive for implementation-start boundaries instead of inventing a second lock.

## Specification Links

- `SPEC-INTAKE-9cb2ee` - governing requirement: holding the GO-implementation claim is required before editing a GO'd thread's target paths.
- `SPEC-INTAKE-be073a` - predecessor VERIFIED requirement: GO-implementation claims are time-boxed with deadline/grace semantics.
- `GOV-RELIABILITY-FAST-LANE-001` - reliability fast-lane basis for the standing project authorization that covers this bounded defect fix.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge index and file-bridge authority remain canonical; this slice only strengthens implementation-start enforcement for GO'd bridge work.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this revised proposal links the PAUTH, project, work item, target paths, and formal governing specifications before implementation.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - machine-readable project authorization metadata is present in the proposal header.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the verification plan maps each behavior clause to executed tests.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - the requirement, bridge proposal, implementation, tests, and verification evidence remain linked artifacts.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - this proposal preserves a concrete reliability requirement and implementation plan as durable artifact state.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - the proposal records the lifecycle trigger for moving this reliability candidate into bridge-reviewed implementation work.
- `.claude/rules/codex-review-gate.md` - mechanical implementation-start gate behavior this slice strengthens.
- `.claude/rules/file-bridge-protocol.md` - mandatory implementation-start authorization metadata and pre-drafting claim procedure this slice extends to source mutations.

## Prior Deliberations

- `INTAKE-5a61f299` - owner intake establishing the claim-gated implementation-start requirement.
- `DELIB-20260667` - `gtkb-impl-start-gate-pretooluse-restore` VERIFIED: the PreToolUse implementation-start gate this slice extends.
- `DELIB-20260645` - `gtkb-claude-code-session-id-env-var-gap` VERIFIED: session-id env-var membership fix reused here.
- `DELIB-20260625` - WI-4270 shared session-id resolver unification; source of `gtkb_session_id.BRIDGE_WORK_INTENT_ORDER`.
- `bridge/gtkb-go-impl-claim-timebox-004.md` - VERIFIED predecessor bridge thread implementing the time-box layer this builds on.

Deliberation search evidence: no cited prior deliberation rejected a claim-gated implementation-start approach. This slice is the next sequenced reliability layer after the verified time-box work.

## Owner Decisions / Input

No new owner decision is required. Existing authority is `SPEC-INTAKE-9cb2ee`, the reliability fast-lane standing project authorization, and the verified predecessor claim-timebox work. This slice performs no MemBase mutation and no schema migration.

## Requirement Sufficiency

Existing requirements are sufficient. `SPEC-INTAKE-9cb2ee` specifies the claim-gate behavior, and `SPEC-INTAKE-be073a` supplies the claim lifecycle it depends on. No new or revised requirement is needed before implementation.

## Design

### Shared Helpers In `implementation_authorization.py`

Add a small importable helper pair:

- `resolve_work_intent_session_id(payload=None, *, environ=None)` - resolves env-first via `gtkb_session_id.BRIDGE_WORK_INTENT_ORDER`, then falls back to a PreToolUse payload `session_id`.
- `work_intent_claim_block_reason(project_root, bridge_id, session_id) -> str | None` - returns `None` only when `session_id` holds the live claim for `bridge_id`; otherwise returns an actionable fail-closed reason. Bootstrap bridge ids remain exempt.

The helper reads `bridge_work_intent_registry.current_holder` and does not mutate the registry.

### Enforcement Point 1: `implementation_authorization.py begin`

Add optional `--session-id` to the `begin` subparser. In the interactive begin branch, resolve the session id, check claim ownership for the target bridge id, and exit `2` without writing a packet when the claim is absent, lapsed, or held by another session.

### Enforcement Point 2: `implementation_start_gate.py`

After `validate_targets` returns the authorizing packet, extract the packet bridge id, resolve the session id using env-first plus payload fallback, and call `work_intent_claim_block_reason`. On a non-`None` reason, return the existing deny PreToolUse block. This prevents the second unclaimed session at edit time even when it has a valid packet.

### Dispatch Compatibility

The claim check stays out of `create_authorization_packet` because dispatch packet issuance runs in the trigger process before the worker environment is established. Headless workers remain valid because the dispatcher acquires the claim under `dispatch_id` and exports `GTKB_BRIDGE_POLLER_RUN_ID` to the worker; the same env-first resolver makes the gate identity equal the claim holder.

### Lapse And Registry Error Policy

Lapsed claims fail as "claim first" because `current_holder` returns `None` after the deadline/grace window. Registry errors fail closed, matching the existing bridge-compliance gate and GT-KB governance bias.

## Files Expected To Change

- `scripts/implementation_authorization.py`
- `scripts/implementation_start_gate.py`
- `platform_tests/scripts/test_implementation_authorization.py`
- `platform_tests/scripts/test_implementation_start_gate.py`

## Specification-Derived Verification

| Spec clause | Test |
| --- | --- |
| `SPEC-INTAKE-9cb2ee`: holding the claim is required before mutating a GO'd thread's target paths | `test_gate_blocks_mutation_when_claim_not_held`, `test_gate_allows_mutation_when_claim_held` |
| Holder must be this session | `test_gate_blocks_when_claim_held_by_other_session` |
| Lapsed claim is treated as not held | `test_gate_blocks_when_claim_lapsed_past_grace` |
| `begin` fails closed without the claim | `test_begin_refuses_without_claim`, `test_begin_succeeds_with_claim` |
| Headless dispatch id remains authorized | `test_gate_allows_when_holder_is_dispatch_id` |
| Registry error fails closed | `test_gate_blocks_on_registry_error` |
| Bootstrap bridge ids are exempt | `test_claim_check_exempts_bootstrap_bridge_ids` |
| Dispatch packet issuance remains unaffected | `test_issue_dispatch_packets_does_not_require_claim` |

Verification commands:

```text
python -m pytest platform_tests/scripts/test_implementation_start_gate.py platform_tests/scripts/test_implementation_authorization.py -q --tb=short
python -m ruff check scripts/implementation_authorization.py scripts/implementation_start_gate.py platform_tests/scripts/test_implementation_authorization.py platform_tests/scripts/test_implementation_start_gate.py
python -m ruff format --check scripts/implementation_authorization.py scripts/implementation_start_gate.py platform_tests/scripts/test_implementation_authorization.py platform_tests/scripts/test_implementation_start_gate.py
git diff --check -- scripts/implementation_authorization.py scripts/implementation_start_gate.py platform_tests/scripts/test_implementation_authorization.py platform_tests/scripts/test_implementation_start_gate.py
```

## Findings Addressed

### Finding 1: Missing Required Specification Citations

Response: Corrected. The revised `Specification Links` section cites the required formal governance specifications and advisory artifact-governance specifications in addition to the intake specs and rule files.

### Finding 2: Unresolved Draft Template Placeholder

Response: Corrected. The stale helper-suggested section is removed. The `Prior Deliberations` section now contains only concrete deliberation, intake, and bridge evidence plus a non-placeholder search note.

## Bridge Filing (INDEX-Canonical)

This revised proposal is filed under `bridge/` with `REVISED: bridge/gtkb-claim-gated-implementation-start-003.md` inserted at the top of the existing `Document: gtkb-claim-gated-implementation-start` entry in `bridge/INDEX.md`. No prior version is deleted or rewritten.

## Risk / Rollback

Risk is false-blocking a legitimate Prime session whose session id differs from the claim id. Mitigation: the shared resolver mirrors the verified draft-time gate and includes payload fallback plus `--session-id` for CLI begin. Risk to headless dispatch is mitigated by keeping the check out of shared packet minting and relying on the dispatch id environment. Rollback is a normal source/test revert; no schema change, MemBase mutation, or authorization packet shape change is proposed.
