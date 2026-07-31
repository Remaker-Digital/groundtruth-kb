NEW
author_identity: codex
author_harness_id: A
author_session_context_id: 2026-06-29T21-30-00Z-prime-builder-A-a01b02
author_model: GPT-5
author_model_version: Codex desktop GPT-5 2026-06-29
author_model_configuration: Codex desktop automation auto-builder; approval_policy=never; sandbox=danger-full-access; role=prime-builder
author_metadata_source: Codex automation runtime environment

# Implementation Proposal - bridge-claim acting_role resolves from clobbered shared active-session-role.json under concurrent sessions

bridge_kind: prime_proposal
Document: gtkb-wi4868-work-intent-role-isolation-target-scope-repair
Version: 001
Date: 2026-06-29 UTC

Project Authorization: PAUTH-PROJECT-HARNESS-PARITY-PHASE-2-IMPLEMENTATION-2026-06-29
Project: PROJECT-HARNESS-PARITY-PHASE-2
Work Item: WI-4868

target_paths: ["scripts/bridge_work_intent_registry.py", "scripts/bridge_claim_cli.py", "scripts/gtkb_session_id.py", "platform_tests/scripts/test_bridge_work_intent_registry.py", "platform_tests/scripts/test_bridge_claim_cli.py", "platform_tests/scripts/test_work_intent_role_eligibility.py", "platform_tests/scripts/test_work_intent_auto_extend.py", "platform_tests/scripts/test_go_impl_claim_timebox.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

Supersede the existing WI-4868 GO with a target-scope repair proposal because the requested role-isolation behavior necessarily touches adjacent GO-claim timebox and auto-extend tests omitted from the approved target_paths.

Work item description: scripts/bridge_claim_cli.py claim resolves acting_role from the shared single-file .claude/session/active-session-role.json marker, which concurrent/background sessions continuously overwrite (single shared file, not per-session). S-2026-06-26 repro: an interactive Prime Builder session (harness B, session c579b2a5, durable role prime-builder, transcript init gtkb pb) acquired a claim with acting_role=loyal-opposition because a concurrent LO session (318f66d8) had written the shared marker to loyal-opposition at 23:12Z. This mislabels the claim and blocks/risks filing a prime_proposal with role-confused author attribution. Expected: claim acting_role should derive from the durable registry role (harness B prime-builder via groundtruth_kb.harness_projection.read_roles) and/or per-session marker/envelope authority, not the shared single-file cache. Blocked the cross-harness parity Slice-1 filing (PROJECT-GTKB-CROSS-HARNESS-PARITY, WI-4865). Cross-session shared-state contention adjacent to the parity program. Related: DELIB-S20260626-PARITY-IMPL-AUTHORIZATION.

## Claim

Prime Builder proposes a bounded implementation slice for `WI-4868` and keeps the bridge, project authorization, owner-decision, and verification gates intact.

## Requirement Sufficiency

Existing requirements are sufficient for filing this proposal. The work item and active project authorization define the implementation boundary; any missing membership or PAUTH state is created only when explicit owner-decision evidence is supplied.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `scripts/bridge_work_intent_registry.py`, `scripts/bridge_claim_cli.py`, `scripts/gtkb_session_id.py`, `platform_tests/scripts/test_bridge_work_intent_registry.py`, `platform_tests/scripts/test_bridge_claim_cli.py`, `platform_tests/scripts/test_work_intent_role_eligibility.py`, `platform_tests/scripts/test_work_intent_auto_extend.py`, `platform_tests/scripts/test_go_impl_claim_timebox.py`.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - preserves role-correct bridge authority and numbered-file filing.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - auto-linked governing or work-item specification.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - requires concrete specification links in implementation proposals.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - requires spec-derived verification evidence before VERIFIED.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - requires project authorization, project, work item, and target path metadata.
- `SPEC-AUQ-POLICY-ENGINE-001` - auto-linked governing or work-item specification.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - keeps this platform command out of adopter application scope.
- `GOV-STANDING-BACKLOG-001` - auto-linked governing or work-item specification.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - auto-linked governing or work-item specification.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - auto-linked governing or work-item specification.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - auto-linked governing or work-item specification.
- `GOV-SESSION-ROLE-AUTHORITY-001` - auto-linked governing or work-item specification.
- `DCL-SESSION-ROLE-RESOLUTION-001` - auto-linked governing or work-item specification.
- `DCL-INTERACTIVE-SESSION-ROLE-PERSISTENCE-001` - auto-linked governing or work-item specification.
- `DCL-CROSS-HARNESS-ENFORCEMENT-001` - auto-linked governing or work-item specification.

## Prior Deliberations

- `DELIB-20266031` - Loyal Opposition Review - included_work_item_ids Semantics
- `DELIB-20266032` - Loyal Opposition Review - included_work_item_ids Semantics
- `DELIB-20266033` - Loyal Opposition Review - included_work_item_ids Semantics
- `DELIB-20266034` - Verdict
- `DELIB-20266042` - Loyal Opposition Review - WI-4779 Session-Context Review Independence Startup Rationale

## Owner Decisions / Input

- `PAUTH-PROJECT-HARNESS-PARITY-PHASE-2-IMPLEMENTATION-2026-06-29` - active project authorization covering `WI-4868`.

## Proposed Scope

- Supersede the narrower GO because removing the active-session-role fallback affects adjacent GO-claim timebox and work-intent auto-extend tests outside the prior target_paths.
- Remove shared active-session-role.json fallback from work-intent acting_role and GO-implementation eligibility while preserving dispatch-format session-id registry and matching per-session role markers.
- Update all affected focused tests so absent or mismatched per-session markers ignore the shared legacy marker and raw non-dispatch sessions require scoped per-session Prime evidence.

## Specification-Derived Verification Plan

| Spec | Verification |
| --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | python -m pytest platform_tests/scripts/test_bridge_work_intent_registry.py platform_tests/scripts/test_bridge_claim_cli.py platform_tests/scripts/test_work_intent_role_eligibility.py platform_tests/scripts/test_work_intent_auto_extend.py platform_tests/scripts/test_go_impl_claim_timebox.py -q --tb=short |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `SPEC-AUQ-POLICY-ENGINE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `GOV-STANDING-BACKLOG-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `GOV-SESSION-ROLE-AUTHORITY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-SESSION-ROLE-RESOLUTION-001` | python -m ruff check scripts/bridge_work_intent_registry.py scripts/bridge_claim_cli.py scripts/gtkb_session_id.py platform_tests/scripts/test_bridge_work_intent_registry.py platform_tests/scripts/test_bridge_claim_cli.py platform_tests/scripts/test_work_intent_role_eligibility.py platform_tests/scripts/test_work_intent_auto_extend.py platform_tests/scripts/test_go_impl_claim_timebox.py |
| `DCL-INTERACTIVE-SESSION-ROLE-PERSISTENCE-001` | python -m ruff format --check scripts/bridge_work_intent_registry.py scripts/bridge_claim_cli.py scripts/gtkb_session_id.py platform_tests/scripts/test_bridge_work_intent_registry.py platform_tests/scripts/test_bridge_claim_cli.py platform_tests/scripts/test_work_intent_role_eligibility.py platform_tests/scripts/test_work_intent_auto_extend.py platform_tests/scripts/test_go_impl_claim_timebox.py |
| `DCL-CROSS-HARNESS-ENFORCEMENT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |

## Acceptance Criteria

- No work-intent claim persists acting_role from .claude/session/active-session-role.json when dispatch id and matching per-session marker evidence are absent.
- Focused bridge work-intent, claim CLI, role eligibility, auto-extend, and GO-claim timebox tests pass together.

## Risks / Rollback

Risk is moderate because implementation proposals authorize later protected-file work. The service must fail closed around owner-decision evidence, target paths, bridge slug collisions, author metadata, and preflight failures.

Rollback is a revert of the source and test changes. Bridge files and project authorization records are append-only audit artifacts and must not be deleted by rollback.

## Files Expected To Change

- `scripts/bridge_work_intent_registry.py`
- `scripts/bridge_claim_cli.py`
- `scripts/gtkb_session_id.py`
- `platform_tests/scripts/test_bridge_work_intent_registry.py`
- `platform_tests/scripts/test_bridge_claim_cli.py`
- `platform_tests/scripts/test_work_intent_role_eligibility.py`
- `platform_tests/scripts/test_work_intent_auto_extend.py`
- `platform_tests/scripts/test_go_impl_claim_timebox.py`

## Recommended Commit Type

`feat`
