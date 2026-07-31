REVISED

# Implementation Proposal - Restore bounded Codex startup-relay cache refresh - 003

bridge_kind: prime_proposal
Document: gtkb-wi5128-startup-relay-cache-refresh
Version: 003 (REVISED)
Responds to: bridge/gtkb-wi5128-startup-relay-cache-refresh-002.md
Date: 2026-07-10 UTC

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f4929-9343-7480-a8a0-055a97ab4b8a
author_model: GPT-5
author_model_version: GPT-5
author_model_configuration: Codex desktop interactive; resolved role prime-builder via ::init gtkb pb

Project Authorization: PAUTH-PROJECT-GTKB-CANONICAL-AUTHORITY-DRIFT-REMEDIATION-STARTUP-RELAY-REPAIR
Project: PROJECT-GTKB-CANONICAL-AUTHORITY-DRIFT-REMEDIATION
Work Item: WI-5128

target_paths: ["scripts/workstream_focus.py", "scripts/session_start_dispatch_core.py", "platform_tests/hooks/test_workstream_focus.py", "platform_tests/hooks/test_session_start_dispatch_role_cache.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
Recommended commit type: feat:

## Summary

Repair bounded Codex startup-relay cache refresh without weakening the init-keyword relay guard.

Work item description: repair the interactive startup relay so a stale but integrity-valid role-scoped cache is refreshed within the hook budget or yields a focused, diagnosable result. Preserve cache integrity and freshness validation.

## Revision Claim

This REVISED proposal addresses `bridge/gtkb-wi5128-startup-relay-cache-refresh-002.md` F1 and F2. The verification plan now maps every retained specification to a concrete test or gate, and the specification links now include relevance rationales instead of scaffold boilerplate. `SPEC-AUQ-POLICY-ENGINE-001` is pruned because this startup-relay cache refresh does not change AUQ policy evaluation.

## Requirement Sufficiency

Existing requirements are sufficient for this proposal. The active work item and project authorization define the implementation boundary; no KB mutation is in scope.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `scripts/workstream_focus.py`, `scripts/session_start_dispatch_core.py`, `platform_tests/hooks/test_workstream_focus.py`, and `platform_tests/hooks/test_session_start_dispatch_role_cache.py`.

## Specification Links

- `SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001` - the relay must preserve role-scoped startup disclosure for canonical `::init gtkb pb` / `::init gtkb lo` handling after cache refresh.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - Codex hook fallback behavior must remain parity-safe when the startup relay cache is stale, invalid, or refresh-bounded.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - the proposal and later implementation report must remain governed bridge artifacts with correct status transitions.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal must cite the relevant governing specifications with concrete rationales.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - VERIFIED requires tests derived from the linked startup-relay and hook-parity specs.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - the proposal must carry PAUTH, project, WI, and target-path metadata.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all changes are GT-KB platform hook/source files, not adopter application files.
- `GOV-STANDING-BACKLOG-001` - WI-5128 is a standing reliability/remediation work item and should remain linked to its backlog item.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - the proposal preserves the defect, revision rationale, owner evidence, and future verification obligations as durable artifacts.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - implementation and verification evidence will remain connected through bridge files, tests, and work-item metadata.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - this revision records the NO-GO to REVISED lifecycle transition and the concrete conditions for a later GO/VERIFIED path.

## Prior Deliberations

- `DELIB-202665935` - owner-decision evidence for the startup-relay repair and PAUTH.
- `DELIB-20264942` - Loyal Opposition verification of a prior startup-relay truncation fix; establishes the expected concrete verification bar.
- `DELIB-20264941` - companion Loyal Opposition verification of startup-relay truncation fix refile.
- `bridge/gtkb-wi5126-deterministic-services-carrier-recovery-003.md` - precedent for correcting boilerplate verification rows into concrete spec-derived commitments.

## Owner Decisions / Input

- `DELIB-202665935` - owner-decision evidence supplied to authorize this repair.
- `PAUTH-PROJECT-GTKB-CANONICAL-AUTHORITY-DRIFT-REMEDIATION-STARTUP-RELAY-REPAIR` - active project authorization covering `WI-5128`.

No new owner input is required by this revision.

## Proposed Scope

- Repair the bounded refresh path for a stale but integrity-valid role-scoped startup relay cache.
- Preserve hash, byte-length, harness, role, disclosure-shape, and freshness validation.
- Preserve fail-closed behavior for invalid cache data.
- Ensure refresh failures produce focused, diagnosable output instead of silent stale-cache acceptance.
- Add focused regression coverage for the Codex interactive Prime Builder init path and the shared session-start role-cache path.

## Findings Addressed

### F1 [P1] Specification-Derived Verification Plan is boilerplate for 11 of 12 rows

Response: Accepted. The verification plan below maps each retained specification to concrete target-file tests and gates. It no longer defers real test design to the implementation report.

### F2 [P3] Specification links include scaffold boilerplate and at least one likely-irrelevant spec

Response: Accepted. `SPEC-AUQ-POLICY-ENGINE-001` is pruned. Retained links now include relevance rationales tied to startup-relay cache refresh, hook parity, project/bridge governance, and artifact lifecycle.

## Specification-Derived Verification Plan

| Spec | Verification commitment |
| --- | --- |
| `SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001` | Add/extend `platform_tests/hooks/test_workstream_focus.py` to assert a Codex Prime Builder `::init gtkb pb` startup path refreshes a stale but integrity-valid role-scoped cache and still emits the Prime Builder startup disclosure. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | Add/extend `platform_tests/hooks/test_session_start_dispatch_role_cache.py` to assert session-start cache refresh behavior is parity-safe and does not weaken the hook fallback contract. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Run candidate and live bridge preflights for the REVISED proposal and the later implementation report; confirm no alternate bridge queue or status token is introduced. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Candidate preflight must pass with no missing required specs; retained spec links must have concrete relevance rationales. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Run `pytest platform_tests/hooks/test_workstream_focus.py platform_tests/hooks/test_session_start_dispatch_role_cache.py -q --tb=short --basetemp .harness-tmp/<name>` after implementation; tests must cover stale-valid refresh, invalid-data fail-closed, and bounded-timeout diagnostic behavior. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Candidate/live preflights must confirm PAUTH, project, WI, and target paths remain present and in-root. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Confirm all source/test changes stay within the four in-root platform target paths and do not touch `applications/` or adopter repositories. |
| `GOV-STANDING-BACKLOG-001` | Implementation report must preserve `Work Item: WI-5128` and the active project authorization link. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Implementation report must cite this revision, the NO-GO finding, and owner decision evidence so the artifact graph remains durable. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Implementation report must connect changed source, tests, bridge revision, and verification command evidence. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | The implementation report must state whether the lifecycle result is ready for VERIFIED or still blocked by a concrete condition; no silent stale-cache acceptance is allowed. |

## Acceptance Criteria

- An interactive Codex Prime Builder init can recover a stale integrity-valid relay cache inside the bounded refresh contract.
- Invalid hash, byte-length, harness, role, disclosure-shape, or freshness data remains fail-closed.
- A refresh that cannot complete within the hook budget returns focused diagnostic evidence rather than silently accepting stale cache data.
- The two targeted hook test files cover the stale-valid, invalid, and bounded-timeout cases.
- Candidate/live bridge preflights pass with no missing required specifications.

## Risks / Rollback

Risk is moderate because this changes startup hook behavior. The implementation must fail closed around cache integrity, role/harness identity, disclosure shape, and time budget. Rollback is a revert of the four target files; bridge files remain append-only audit artifacts.

## Files Expected To Change

- `scripts/workstream_focus.py`
- `scripts/session_start_dispatch_core.py`
- `platform_tests/hooks/test_workstream_focus.py`
- `platform_tests/hooks/test_session_start_dispatch_role_cache.py`
