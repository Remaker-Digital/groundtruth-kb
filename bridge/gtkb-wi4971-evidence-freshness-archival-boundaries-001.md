NEW

# WI-4971 - Evidence Freshness and Archival Boundaries

bridge_kind: prime_proposal
Document: gtkb-wi4971-evidence-freshness-archival-boundaries
Version: 001
Author: Prime Builder (Codex)
Date: 2026-07-06T01:50:00Z

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f337a-009a-7f51-8dce-b6c3f1d91b1c
author_model: GPT-5.5 Codex
author_model_version: gpt-5.5
author_model_configuration: interactive Prime Builder session; reasoning=xhigh; approval_policy=never

Project Authorization: PAUTH-PROJECT-HARNESS-EQUIVALENCE-PHASE-3-WI4971-BATCH-C-20260705
Project: PROJECT-HARNESS-EQUIVALENCE-PHASE-3
Work Item: WI-4971

target_paths: ["groundtruth-kb/src/groundtruth_kb/cli_session_handoff.py", "groundtruth-kb/src/groundtruth_kb/reconciliation.py", "groundtruth-kb/src/groundtruth_kb/harness_projection.py", "scripts/bridge_citation_freshness_preflight.py", "platform_tests/scripts/test_bridge_citation_freshness_preflight.py", "platform_tests/scripts/test_wrap_capture_transcript.py", "platform_tests/scripts/test_wrap_scan_consistency.py", "platform_tests/scripts/test_harvest_session_thread_level.py", "platform_tests/scripts/test_session_envelope_runtime.py", "platform_tests/scripts/test_versioned_files_archival_invariant.py", "platform_tests/scripts/test_deliberation_search_stale_segment.py", "platform_tests/scripts/test_session_handoff.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

WI-4971 implements Phase 3 gap 09: define when agents should read compact summaries, when archival/full output is justified, and how to cite archived transcripts without loading entire historical state into routine sessions. The implementation should link current session/activity envelope sharding blockers B1-B7 as evidence and make freshness boundaries machine-checkable.

The work should add or tighten freshness metadata, archival/full-output opt-in rules, and citation checks around transcripts, session envelopes, bridge history, deliberation search segments, and wrap/handoff evidence. Routine sessions should consume compact current-state references by default; verification or dispute resolution can still explicitly request full archived evidence with stable citations.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`, `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`, and `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - bridge/PAUTH lifecycle applies.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`, `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`, and `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - proposal and verification linkage are mandatory.
- `SPEC-INTAKE-46594e`, `DCL-SESSION-STARTUP-TOKEN-BUDGET-001`, and `GOV-SESSION-SELF-INITIALIZATION-001` - compact/fresh evidence defaults protect startup and routine context use.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`, `GOV-STANDING-BACKLOG-001`, `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, and `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - preserve root-bound artifact traceability.

## Prior Deliberations

- `DELIB-20260705-HIGH-PRIORITY-QUEUE-CONTINUE` - owner approved Batch C continuation.
- `DELIB-202665197` and `bridge/harness-equivalence-phase-3-umbrella-002.md` - Phase 3 child-gap authority.
- Session/activity envelope sharding blockers B1-B7 - evidence set this WI must link without reloading full historical state by default.
- `TEST-11271` - manual test linkage for WI-4971 under `SPEC-INTAKE-46594e`.

## Owner Decisions / Input

Owner approval is already recorded by the active PAUTH. No fresh owner decision is required.

## Requirement Sufficiency

Existing requirements are sufficient: compact-by-default current evidence, explicit archive/full evidence opt-in, stable transcript citation, and freshness checks are all in scope.

## Spec-Derived Verification Plan

| Requirement | Verification |
|---|---|
| Compact current evidence is default | Add tests that wrap/handoff/session-envelope reads return compact references unless full/archive mode is requested. |
| Full archived evidence is explicit and citeable | Extend archival invariant and deliberation-search tests for stable archived transcript/segment citations. |
| Freshness boundaries are machine-checkable | Extend bridge citation freshness preflight tests for stale, current, archived, and justified-full cases. |
| Startup token budget is protected | Add regression evidence that startup/self-initialization paths do not load full historical transcript state. |

Minimum expected verification commands:

```text
python -m pytest platform_tests/scripts/test_bridge_citation_freshness_preflight.py platform_tests/scripts/test_wrap_capture_transcript.py platform_tests/scripts/test_wrap_scan_consistency.py -q --tb=short
python -m pytest platform_tests/scripts/test_harvest_session_thread_level.py platform_tests/scripts/test_session_envelope_runtime.py platform_tests/scripts/test_versioned_files_archival_invariant.py platform_tests/scripts/test_deliberation_search_stale_segment.py platform_tests/scripts/test_session_handoff.py -q --tb=short
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi4971-evidence-freshness-archival-boundaries --json
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi4971-evidence-freshness-archival-boundaries
```

## Risk / Rollback

Risk is either stale summary evidence or excessive archive loading. Keep freshness explicit, preserve full drill-down, and rollback if wrap/session/citation tests regress.

## Bridge Filing

This proposal is filed as the first numbered bridge file for `gtkb-wi4971-evidence-freshness-archival-boundaries`.

## Recommended Commit Type

feat - add freshness and archival-boundary controls.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
