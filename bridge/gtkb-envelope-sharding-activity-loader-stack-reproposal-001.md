NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f1bfe-9f4b-7bc2-805e-c051192b5a73
author_model: gpt-5-codex
author_model_version: 2026-07-01
author_model_configuration: Codex Desktop interactive Prime Builder session; replacement WI-4948 bridge proposal after implementation-start provenance gate refusal

# Replacement Child Proposal - Activity-Envelope Manifest And Context-Loader Stack

bridge_kind: prime_proposal
Document: gtkb-envelope-sharding-activity-loader-stack-reproposal
Version: 001
Date: 2026-07-01 UTC

Project Authorization: PAUTH-PROJECT-GTKB-SESSION-ACTIVITY-ENVELOPE-SHARDING-WI-4948
Project: PROJECT-GTKB-SESSION-ACTIVITY-ENVELOPE-SHARDING
Work Item: WI-4948

target_paths: ["config/agent-control/activity-envelope-sharding.toml", "config/agent-control/activity-disposition-profiles.toml", "groundtruth-kb/src/groundtruth_kb/activity/profiles.py", "groundtruth-kb/src/groundtruth_kb/session/topic_router.py", "scripts/skill_usage_router.py", ".claude/hooks/session-topic-envelope-router.py", ".codex/gtkb-hooks/session_start_dispatch.py", ".cursor/gtkb-hooks/session_start_dispatch.py", "platform_tests/scripts/test_activity_disposition_profiles.py", "platform_tests/scripts/test_session_envelope_runtime.py"]

## Claim

Replace the unusable WI-4948 GO thread with a fresh reviewable proposal for the same activity-envelope manifest/context-loader implementation. The original thread `gtkb-envelope-sharding-activity-loader-stack` reached `GO` at `bridge/gtkb-envelope-sharding-activity-loader-stack-002.md`, but the implementation-start gate refuses that GO because the verdict lacks structured `author_session_context_id` metadata. This replacement proposal preserves the original implementation scope and asks Loyal Opposition for a fresh independent GO/NO-GO verdict with machine-readable author provenance.

## Scope

- Add or extend manifest schema fields for activity shard payloads and global baseline dependencies.
- Render representative `::open <activity>` context from manifest-declared skills, terminology, history_state, and directive overlays only.
- Document hook-primary and agent-fallback behavior for harnesses without native hook support.
- Supersede only the unusable GO handoff for `gtkb-envelope-sharding-activity-loader-stack`; do not edit that historical bridge verdict.

## Out Of Scope

- Credential lifecycle, production deployment, destructive cleanup, or unrelated worktree cleanup.
- Broad refactors outside the declared `target_paths`.
- Treating this replacement proposal as authorization for any child work item other than `WI-4948`.
- Bypassing bridge GO, work-intent claim, implementation-start packet, implementation report, or Loyal Opposition verification.

## In-Root Placement Evidence

All declared target paths are under `E:/GT-KB`. Runtime/cache artifacts created during implementation must remain under `.gtkb-state/` or another in-root governed runtime location.

## Specification Links

- `SPEC-INTAKE-46594e`
- `ADR-ACTIVITY-ENVELOPE-DISPOSITION-001`
- `DCL-ACTIVITY-DISPOSITION-PROFILE-001`
- `DCL-ACTIVITY-ENVELOPE-INTERCEPTION-001`
- `ADR-EXPLICIT-HINT-CONTEXT-MANAGEMENT-001`
- `ADR-CROSS-HARNESS-PARITY-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-DOCUMENT-AUTHOR-PROVENANCE-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`

## Prior Deliberations

- `DELIB-20260701-ENVELOPE-SHARDING-EXECUTE-RETIRE` - owner directive to complete all child work items in this project and retire it after governed verification.
- `DELIB-202665110` - owner authorization for the umbrella program and PAUTH creation.
- `DELIB-20266631` - Loyal Opposition context for activity-envelope context sharding.
- `DELIB-20265892` - disposition-profile ratification.
- `DELIB-20260630-ACTIVITY-ENVELOPE-SHARDING-AUTHORIZATION` - prior envelope refinement authorization.
- `DELIB-20265287` - single-active activity envelope, named disposition profile, and headless eligibility decisions.
- `DELIB-20260621-EXPLICIT-HINT-CONTEXT-LOAD-REFRAME` - context-load profile anatomy and activity vocabulary.

## Owner Decisions / Input

- `DELIB-20260701-ENVELOPE-SHARDING-EXECUTE-RETIRE` - current owner instruction: complete all work items in `PROJECT-GTKB-SESSION-ACTIVITY-ENVELOPE-SHARDING` and retire the project.
- `PAUTH-PROJECT-GTKB-SESSION-ACTIVITY-ENVELOPE-SHARDING-WI-4948` - bounded implementation authorization for `WI-4948` only.

## Gate Failure Being Repaired

The implementation-start preflight for the original `GO` returned:

```json
{"authorized": false, "error": "Self-review GO refused (author_session_context_missing): the GO verdict author session (None) and the proposal author session ('019f1bfe-9f4b-7bc2-805e-c051192b5a73') must be present, distinct, and independent (WI-4829; GOV-DOCUMENT-AUTHOR-PROVENANCE-001)."}
```

This proposal does not ask Loyal Opposition to rubber-stamp the old verdict. It asks for a fresh review of the same scoped implementation proposal so the next verdict carries structured author metadata and can be consumed by the implementation-start gate.

## Cross-Harness Disposition

- Claude: native `.claude` hook/skill surfaces listed in `target_paths` must preserve canonical behavior.
- Codex: matching `.codex` adapter/helper surfaces listed in `target_paths` must be updated in lockstep where the slice changes shared behavior.
- Cursor: Cursor fallback hook behavior is targeted where listed; newly discovered Cursor deltas must route to `WI-4950` or a typed waiver.
- Antigravity/Ollama/OpenRouter/provider lanes: compact result/session-envelope parity remains in `WI-4950`; this proposal must not imply an unrecorded waiver.

## Requirement Sufficiency

Existing requirements are sufficient for this scoped child implementation. `SPEC-INTAKE-46594e` requires base session startup to load only core GT-KB terminology and global content, while activity-specific terminology and skills load only for the opened activity envelope. The activity-profile ADR/DCL set defines manifest payload classes and hook/fallback placement. This replacement proposal changes only the bridge handoff path, not owner policy.

## Proposed Implementation

- Add or extend manifest schema fields for activity shard payloads and global baseline dependencies.
- Render representative `::open <activity>` context from manifest-declared skills, terminology, history_state, and directive overlays only.
- Document hook-primary and agent-fallback behavior for harnesses without native hook support.

Declared implementation target paths:

- `config/agent-control/activity-envelope-sharding.toml`
- `config/agent-control/activity-disposition-profiles.toml`
- `groundtruth-kb/src/groundtruth_kb/activity/profiles.py`
- `groundtruth-kb/src/groundtruth_kb/session/topic_router.py`
- `scripts/skill_usage_router.py`
- `.claude/hooks/session-topic-envelope-router.py`
- `.codex/gtkb-hooks/session_start_dispatch.py`
- `.cursor/gtkb-hooks/session_start_dispatch.py`
- `platform_tests/scripts/test_activity_disposition_profiles.py`
- `platform_tests/scripts/test_session_envelope_runtime.py`

## Specification-Derived Verification Plan

| Requirement / test | Verification |
| --- | --- |
| `TEST-11253` linked to `SPEC-INTAKE-46594e` | PASS when opening a representative activity loads only the manifest-declared activity payload on top of the global envelope and leaves unrelated shards unloaded. |
| Bridge/project governance | Implementation report must cite this replacement proposal, its GO verdict, the work-intent claim, implementation-start packet, and exact target paths changed. |
| Cross-harness and activity-envelope safety | Tests or report evidence must show unrelated activity shards are not loaded into the base session envelope. |

Planned verification commands:

- `python -m pytest platform_tests/scripts/test_activity_disposition_profiles.py platform_tests/scripts/test_session_envelope_runtime.py -q --tb=short`

## Acceptance Criteria

- `WI-4948` is implemented only within the target paths listed above.
- The next GO/NO-GO verdict includes structured `author_session_context_id` metadata and satisfies the implementation-start self-review gate.
- `TEST-11253` has concrete PASS/FAIL evidence in the implementation report.
- Routine focused-agent workflow for this slice avoids loading unrelated activity content into the global session envelope.

## Risks / Rollback

Risk: activity sharding could remove safety context from startup. Mitigation: preserve role, bridge, root-boundary, project authorization, and core terminology in the global baseline.

Risk: the replacement thread could confuse future readers. Mitigation: this proposal explicitly cites the original unusable GO thread and does not edit historical bridge files.

Rollback: abandon this replacement thread before implementation, or file a revised proposal/report in the next numbered bridge version if Loyal Opposition returns NO-GO.

## Files Expected To Change

- `config/agent-control/activity-envelope-sharding.toml`
- `config/agent-control/activity-disposition-profiles.toml`
- `groundtruth-kb/src/groundtruth_kb/activity/profiles.py`
- `groundtruth-kb/src/groundtruth_kb/session/topic_router.py`
- `scripts/skill_usage_router.py`
- `.claude/hooks/session-topic-envelope-router.py`
- `.codex/gtkb-hooks/session_start_dispatch.py`
- `.cursor/gtkb-hooks/session_start_dispatch.py`
- `platform_tests/scripts/test_activity_disposition_profiles.py`
- `platform_tests/scripts/test_session_envelope_runtime.py`

## Recommended Commit Type

`feat`
