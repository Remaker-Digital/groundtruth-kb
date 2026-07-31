NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f1bfe-9f4b-7bc2-805e-c051192b5a73
author_model: gpt-5-codex
author_model_version: 2026-07-01
author_model_configuration: Codex Desktop interactive Prime Builder session; child proposal filing for session/activity envelope sharding goal

# Child Proposal - Activity-Envelope Manifest And Context-Loader Stack

bridge_kind: prime_proposal
Document: gtkb-envelope-sharding-activity-loader-stack
Version: 001
Date: 2026-07-01 UTC

Project Authorization: PAUTH-PROJECT-GTKB-SESSION-ACTIVITY-ENVELOPE-SHARDING-WI-4948
Project: PROJECT-GTKB-SESSION-ACTIVITY-ENVELOPE-SHARDING
Work Item: WI-4948

target_paths: ["config/agent-control/activity-envelope-sharding.toml", "config/agent-control/activity-disposition-profiles.toml", "groundtruth-kb/src/groundtruth_kb/activity/profiles.py", "groundtruth-kb/src/groundtruth_kb/session/topic_router.py", "scripts/skill_usage_router.py", ".claude/hooks/session-topic-envelope-router.py", ".codex/gtkb-hooks/session_start_dispatch.py", ".cursor/gtkb-hooks/session_start_dispatch.py", "platform_tests/scripts/test_activity_disposition_profiles.py", "platform_tests/scripts/test_session_envelope_runtime.py"]

## Claim

Extend the existing activity profile loader into a manifest-backed context-loader stack that composes activity shards on top of the global session envelope.

## Scope

- Add or extend manifest schema fields for activity shard payloads and global baseline dependencies.
- Render representative ::open activity context from manifest-declared skills, terminology, history_state, and direction only.
- Document hook-primary and agent-fallback behavior for harnesses without native hook support.

## Out Of Scope

- Credential lifecycle, production deployment, and destructive cleanup.
- Unrelated worktree cleanup or broad refactors outside `target_paths`.
- Treating this child proposal as authorization for other child work items.
- Skipping bridge GO, work-intent claim, implementation-start packet, implementation report, or Loyal Opposition verification.

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
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `GOV-STANDING-BACKLOG-001`
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`

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
- `PAUTH-PROJECT-GTKB-SESSION-ACTIVITY-ENVELOPE-SHARDING-WI-4948` - bounded implementation authorization for `WI-4948` only; allowed mutation classes are docs, CLI, tests, skills, and config; forbidden operations are unrelated cleanup, credential lifecycle, and production deployment.

## Cross-Harness Disposition

- Claude: native `.claude` hook/skill surfaces listed in `target_paths` must preserve the canonical behavior for this slice.
- Codex: matching `.codex` adapter/helper surfaces listed in `target_paths` must be updated in lockstep where the slice changes a shared skill or hook behavior.
- Cursor: Cursor fallback hook/skill behavior is either explicitly targeted in this proposal or remains behaviorally unchanged; any newly discovered Cursor delta must be routed to `WI-4950` or a typed waiver before verification.
- Antigravity: generated `.agent` skill-adapter parity is preserved by adapter parity checks when a shared skill source changes; otherwise no Antigravity runtime behavior changes are claimed by this proposal.
- Ollama/OpenRouter/provider lanes: provider harnesses do not own native `.claude`/`.codex` hook files; compact result/session-envelope parity is handled explicitly by `WI-4950`, and this proposal must not imply an unrecorded waiver.

## Requirement Sufficiency

Existing requirements are sufficient for this scoped child implementation. `SPEC-INTAKE-46594e` states the base session envelope must load only core GT-KB terminology and requisite global content, while activity-specific terminology and skills load only for the opened activity envelope. The activity-profile ADR/DCL set defines the manifest classes and hook/fallback placement. This proposal does not introduce a new owner policy; it implements the cited requirement within the child work item boundary.

## Proposed Implementation

- Add or extend manifest schema fields for activity shard payloads and global baseline dependencies.
- Render representative ::open activity context from manifest-declared skills, terminology, history_state, and direction only.
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
| Bridge/project governance | Implementation report must cite this proposal, its GO verdict, the work-intent claim, implementation-start packet, and exact target paths changed. |
| Cross-harness and activity-envelope safety | Tests or report evidence must show unrelated activity shards are not loaded into the base session envelope. |

Planned verification commands:

- `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_activity_disposition_profiles.py platform_tests/scripts/test_session_envelope_runtime.py -q --tb=short`

## Pre-Filing Preflights

Applicability preflight:
- exit_code: 0
- preflight_passed: True
- missing_required_specs: []
- missing_advisory_specs: []
- packet_hash: sha256:8adfeac53fb89f3f68478e422f443f80c2d9e13975718b5d034019aabcccde9e

Clause preflight:
- exit_code: 0
```text
## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-envelope-sharding-activity-loader-stack`
- Operative file: `.gtkb-state\bridge-propose-drafts\session-activity-envelope-sharding\gtkb-envelope-sharding-activity-loader-stack-001.md`
- Clauses evaluated: 5
- must_apply: 3, may_apply: 2, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-NUMBERED-FILE-CHAIN-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | may_apply | â€” | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | may_apply | â€” | blocking | blocking |

_Slice 2 mandatory gate: clauses with `enforcement_mode = "blocking"` and
must_apply applicability fail the gate (exit 5) when evidence is absent and
no `Owner waiver: <clause_id> â€” <DELIB-ID> â€” <reason>` line is cited.
Clauses with `enforcement_mode = "advisory"` are reported but never gate._

```

## Acceptance Criteria

- `WI-4948` is implemented only within the target paths listed above.
- `TEST-11253` has concrete PASS/FAIL evidence in the implementation report.
- Routine focused-agent workflow for this slice avoids loading unrelated activity content into the global session envelope.
- Any discovered out-of-scope blocker is routed to a narrower bridge proposal or work item rather than hidden in this slice.

## Risks / Rollback

Risk: activity sharding could remove safety context from startup. Mitigation: preserve role, bridge, root-boundary, project authorization, and core terminology in the global baseline.

Risk: implementation scope could sprawl across the program. Mitigation: this proposal is one child slice with per-WI PAUTH and explicit target paths.

Rollback: revert this child implementation before filing its implementation report, or file a revised proposal/report in the next numbered bridge version if Loyal Opposition returns NO-GO.

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
