NEW
author_identity: Antigravity Prime Builder
author_harness_id: C
author_session_context_id: 42143a1a-3026-440a-badd-fbb57094f014
author_model: Gemini 2.5 Flash
author_model_version: gemini-2.5-flash
author_model_configuration: Antigravity default reasoning, interactive Prime Builder session

Project Authorization: PAUTH-PROJECT-GTKB-INTERACTIVE-SESSION-ROLE-OVERRIDE-001
Project: PROJECT-GTKB-INTERACTIVE-SESSION-ROLE-OVERRIDE
Work Item: WI-4663
target_paths: ["scripts/session_role_resolution.py", "platform_tests/hooks/test_session_role_resolution.py"]

# Defect-Fix Proposal - Make durable session-envelope role authoritative across contiguous/resumed sessions (supersede S371 resume->durable-harness-role fallback)

bridge_kind: prime_proposal
Document: gtkb-interactive-session-role-override-slice-11-envelope-durability
Version: 001
Date: 2026-06-20 UTC

## Claim

Slice 11 of the interactive-session-role-override project resolves the compaction/resume fallback defect (WI-4663) by making the active session-envelope's `role_resolved` authoritative when the marker is absent or stale. Instead of falling back to the durable harness registry role, the resolver checks if the per-harness `session-envelope.json` status is `"open"` and has a valid `role_resolved`. If so, it returns that envelope role. This ensures role continuity across contiguous compacted sessions in the same interactive context, satisfying the owner directive in DELIB-20265225.

## Defect / Reproduction

Under compaction/resume, the ephemeral session-role marker `active-session-role.json` is either absent or stale (session ID mismatch). In the previous implementation, the resolver fell back directly to the durable harness registry role (resolved via `_durable_role` from `harness-registry.json`). When a session is running under an interactive role override (e.g. Loyal Opposition) but its durable harness registry role is Prime Builder, compaction/resume causes the session role to revert to Prime Builder, refusing to accept or file Loyal Opposition verdicts.

Reproduction scenario:
1. Initialize an interactive session under Loyal Opposition: `::init gtkb lo`. The session envelope is open with `role_resolved = "loyal-opposition"`.
2. Trigger compaction/resume. The marker `active-session-role.json` is missing or stale.
3. Query the active session role. The resolver falls back to the registry role (`"prime-builder"`), violating transcript-role durability.

## In-Root Placement Evidence

All target paths (`scripts/session_role_resolution.py`, `platform_tests/hooks/test_session_role_resolution.py`) are inside the workspace root `E:\GT-KB`.

## Specification Links

- `DCL-SESSION-ROLE-RESOLUTION-001` v3 - constraint that interactive resume reads envelope role and removes durable registry fallback.
- `ADR-INTERACTIVE-SESSION-ROLE-OVERRIDE-001` v2 - decision that transcript-defined role survives compaction.
- `GOV-SESSION-ROLE-AUTHORITY-001` v2 - governance rule for split authority and transcript durability.
- `DCL-SESSION-ENVELOPE-DURABILITY-001` v1 - schema for per-harness envelope.json.
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001`
- `GOV-STANDING-BACKLOG-001`
- `GOV-ARTIFACT-APPROVAL-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` (advisory)
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` (advisory)
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` (advisory)

## Prior Deliberations

- `DELIB-20265225` - Owner directive: transcript defines the session envelope and the interactive role survives compaction/resume.
- `DELIB-2507` - S371 Interactive Session Role Override Owner Directive.
- `DELIB-20265224` - Capture role-persistence reconciliation requirement.

## Owner Decisions / Input

- `DELIB-20265225` - Owner directive that transcript defines the envelope and interactive role survives compaction/resume.

## Proposed Scope

We will modify `scripts/session_role_resolution.py` to:
1. Load the active per-harness `session-envelope.json` file.
2. If the envelope is present, has status `"open"`, and has a valid `role_resolved`, return it as the resolved fallback role.
3. If not, fallback to the durable harness registry role using `_durable_role`.

We will modify `platform_tests/hooks/test_session_role_resolution.py` to:
1. Add test cases that simulate compaction/resume by checking that when the marker is absent or stale, but the session envelope is open, the resolver returns the envelope's resolved role instead of the registry fallback.

## Specification-Derived Verification Plan

### Automated Tests
- Run `groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests/hooks/test_session_role_resolution.py` to verify resolver correctness.

## Acceptance Criteria

- The resolver returns the active session envelope's `role_resolved` when the marker is absent or stale, and returns the registry role only when no open envelope is found.
- All unit tests pass.

## Risks / Rollback

- Risk: Minimal, as this is localized to the interactive session role resolution logic and does not impact headless dispatch routing.
- Rollback: Revert modifications to `scripts/session_role_resolution.py` and `platform_tests/hooks/test_session_role_resolution.py`.

## Files Expected To Change

- `scripts/session_role_resolution.py`
- `platform_tests/hooks/test_session_role_resolution.py`

## Recommended Commit Type

`fix`
