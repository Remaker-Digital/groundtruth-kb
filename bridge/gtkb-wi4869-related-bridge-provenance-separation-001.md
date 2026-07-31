NEW
author_identity: codex
author_harness_id: A
author_session_context_id: 019f19c4-f49d-7283-8c0c-20fe4ec6fb98
author_model: GPT-5 Codex
author_model_version: gpt-5-codex
author_model_configuration: Codex desktop interactive Prime Builder session; approval_policy=never; filesystem=danger-full-access; owner init ::init gtkb pb
author_metadata_source: Codex desktop runtime plus explicit env for gt bridge file-implementation-proposal

# Implementation Proposal - Root-cause: bulk related_bridge_threads mis-assignment corrupted backlog-to-bridge links

bridge_kind: prime_proposal
Document: gtkb-wi4869-related-bridge-provenance-separation
Version: 001
Date: 2026-06-30 UTC

Project Authorization: PAUTH-PROJECT-BACKLOG-TRIAGE-AND-HYGIENE-WI-4869-BRIDGE-LINK-RECONCILIATION
Project: PROJECT-BACKLOG-TRIAGE-AND-HYGIENE
Work Item: WI-4869

target_paths: ["scripts/advisory_backlog_router.py", "scripts/hygiene/advisory_candidate_promote.py", "scripts/bridge_verified_backlog_reconciler.py", "platform_tests/scripts/test_advisory_backlog_router.py", "platform_tests/scripts/test_advisory_candidate_promote.py", "platform_tests/scripts/test_bridge_verified_backlog_reconciler.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

Prevent advisory/source provenance from being persisted as implementation bridge linkage in related_bridge_threads.

Work item description: Backlog data-integrity finding surfaced 2026-06-26; ROOT CAUSE CONFIRMED 2026-06-27 via WI version-history audit. NOT a bulk mis-assignment migration bug (earlier hypothesis, now corrected). Real root cause: related_bridge_threads is semantically overloaded. When a WI is captured as a strategic-self-improvement or friction finding DURING work on another bridge thread, the capture flow records that surfaced-during CONTEXT thread as provenance (the finding came up while working thread X), not as implementation linkage. Evidence: every affected WI received its link at v1 creation, by different sessions on different dates (2026-06-04 WI-4304/4306; 2026-06-11 WI-4455; 2026-06-22 WI-4736; 2026-06-25 WI-4823/4824/4822/4844), each change_reason stating the WI was captured during the linked thread work. The shared-slug pattern (one thread linked by two WIs) is explained by both WIs being captured in the same work session. IMPACT: the verified-backlog reconciler reads related_bridge_threads as implementation linkage (linked-thread VERIFIED implies WI done), so provenance links land in the missing_parent_evidence bucket as drift NOISE. The reconciler canonical-evidence guard ALREADY prevents wrong resolution (those WIs are never auto-resolved; 0 auto-resolvable across the 2026-06-26 sweep), so impact was reconciler noise, not false closures. SYMPTOM REPAIR done under DELIB-20266206: cleared provenance links on 10 WIs (recoverable from change_reason and append-only history). FIX DIRECTION (reframed): separate provenance from implementation-linkage. (1) capture flow (gt backlog add and the strategic-capture path) should NOT write the surfaced-during thread into related_bridge_threads; give provenance its own field (surfaced_during_thread) or keep it in change_reason only. (2) optionally have the reconciler or a doctor check treat a related_bridge_threads entry as impl-linkage only when the thread canonically declares the WI via Work Item metadata (the canonical-evidence path it already computes). Confirmed by Prime Builder read-only history audit per owner AUQ 2026-06-27.

## Claim

Prime Builder proposes a bounded implementation slice for `WI-4869` and keeps the bridge, project authorization, owner-decision, and verification gates intact.

## Requirement Sufficiency

Existing requirements are sufficient for filing this proposal. The work item and active project authorization define the implementation boundary; any missing membership or PAUTH state is created only when explicit owner-decision evidence is supplied.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `scripts/advisory_backlog_router.py`, `scripts/hygiene/advisory_candidate_promote.py`, `scripts/bridge_verified_backlog_reconciler.py`, `platform_tests/scripts/test_advisory_backlog_router.py`, `platform_tests/scripts/test_advisory_candidate_promote.py`, `platform_tests/scripts/test_bridge_verified_backlog_reconciler.py`.

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

## Prior Deliberations

- `DELIB-20266206` - Owner reconciliation decision: repair 10 corrupted related_bridge_threads links
- `DELIB-20266094` - Owner decision: verify-by-reference resolution of PROJECT-GTKB-HARNESS-STATE-SOT-CONSOLIDATION (6 done-but-unlinked WIs)
- `DELIB-20266119` - Owner decision: close WI-4230/4231/4233 as superseded by the no-index bridge cutover
- `DELIB-20265893` - Resolve WI-4772 + WI-4775 as covered by VERIFIED gtkb-verified-finalization-validation-hardening (may29-hygiene retirement)
- `DELIB-20266137` - Owner authorization: drive 7 dispatcher-reliability WIs (Fixes-then-Phases); yield WI-4818 to concurrent session

## Owner Decisions / Input

- `DELIB-20266592` - owner-decision evidence supplied to this command.
- `PAUTH-PROJECT-BACKLOG-TRIAGE-AND-HYGIENE-WI-4869-BRIDGE-LINK-RECONCILIATION` - active project authorization covering `WI-4869`.

## Proposed Scope

- Reserve work_items.related_bridge_threads for implementation bridge links that can be validated by canonical Work Item metadata; advisory/surfaced-during bridge context remains provenance only.
- Update advisory candidate staging/promotion so bridge ADVISORY source context is preserved in source_key, related_deliberation_ids, source_deliberation_query, change_reason, or candidate-event provenance, but does not populate related_bridge_threads unless explicitly marked as implementation linkage.
- Keep the verified-backlog reconciler fail-closed: provenance-only bridge slugs must not become closure candidates, while canonical Work Item metadata continues to derive valid implementation links.

## Specification-Derived Verification Plan

| Spec | Verification |
| --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `SPEC-AUQ-POLICY-ENGINE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `GOV-STANDING-BACKLOG-001` | python -m pytest platform_tests/scripts/test_advisory_backlog_router.py platform_tests/scripts/test_advisory_candidate_promote.py platform_tests/scripts/test_bridge_verified_backlog_reconciler.py -q --tb=short |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |

## Acceptance Criteria

- Promoted bridge-advisory candidates remain traceable to their source advisory but their resulting work_items rows do not carry advisory slugs in related_bridge_threads.
- Existing valid implementation-link behavior is preserved: a bridge thread with Work Item metadata can still drive reconciliation/closure, and unrelated prose or advisory provenance cannot.
- No direct SQLite/backlog bulk mutation is performed by the implementation; any work_items writes stay behind existing KnowledgeDB/CLI-owned services.

## Risks / Rollback

Risk is moderate because implementation proposals authorize later protected-file work. The service must fail closed around owner-decision evidence, target paths, bridge slug collisions, author metadata, and preflight failures.

Rollback is a revert of the source and test changes. Bridge files and project authorization records are append-only audit artifacts and must not be deleted by rollback.

## Files Expected To Change

- `scripts/advisory_backlog_router.py`
- `scripts/hygiene/advisory_candidate_promote.py`
- `scripts/bridge_verified_backlog_reconciler.py`
- `platform_tests/scripts/test_advisory_backlog_router.py`
- `platform_tests/scripts/test_advisory_candidate_promote.py`
- `platform_tests/scripts/test_bridge_verified_backlog_reconciler.py`

## Recommended Commit Type

`feat`
