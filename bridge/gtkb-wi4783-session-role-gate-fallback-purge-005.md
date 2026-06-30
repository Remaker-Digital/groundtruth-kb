REVISED
author_identity: codex
author_harness_id: A
author_session_context_id: 2026-06-30T05-24-51Z-prime-builder-A-bb4783
author_model: GPT-5
author_model_version: GPT-5 Codex
author_model_configuration: Codex Desktop automation; Prime Builder; Auto-builder; reasoning default

# WI-4783 Session Role Gate Fallback Purge - Target Scope Revision

bridge_kind: prime_proposal
Document: gtkb-wi4783-session-role-gate-fallback-purge
Version: 005
Responds to: bridge/gtkb-wi4783-session-role-gate-fallback-purge-004.md
Revises: bridge/gtkb-wi4783-session-role-gate-fallback-purge-001.md

Project Authorization: PAUTH-PROJECT-HARNESS-PARITY-PHASE-2-IMPLEMENTATION-2026-06-29
Project: PROJECT-HARNESS-PARITY-PHASE-2
Work Item: WI-4783

target_paths: [".claude/hooks/lo-file-safety-gate.py", ".claude/hooks/workstream-focus.py", "scripts/session_role_resolution.py", "scripts/gtkb_session_id.py", "platform_tests/hooks/test_session_role_resolution.py", "platform_tests/hooks/test_workstream_focus_session_role_marker.py", "platform_tests/hooks/test_lo_file_safety_gate.py", "platform_tests/scripts/test_lo_file_safety_gate_role_resolution.py"]

implementation_scope: source, tests, hook behavior
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Revision Claim

Prime Builder revises the WI-4783 proposal only to correct the target-path
scope defect identified in the NO-GO at
`bridge/gtkb-wi4783-session-role-gate-fallback-purge-004.md`.

The previous approved target set omitted
`platform_tests/scripts/test_lo_file_safety_gate_role_resolution.py`. The
implementation blocker report at version 003 showed that this existing test
file still asserts the superseded durable-registry fallback behavior and must
be updated or retired for the purge to be verifiable. This revision adds that
test file to `target_paths` while preserving the original project, PAUTH,
work item, requirement sufficiency, non-scope, and verification intent.

## Requirement Sufficiency

Existing requirements remain sufficient. No new owner decision is needed
because the revision does not expand beyond WI-4783's owner-approved purpose:
strip durable-registry fallback authority from non-dispatcher role gates,
preserve explicit session/envelope authority, fix marker propagation, and
verify the stale fallback test surface.

## In-Root Placement Evidence

All target paths remain inside `E:\GT-KB` and outside `applications/Agent_Red/`.
The new target-path addition is
`platform_tests/scripts/test_lo_file_safety_gate_role_resolution.py`, an
existing in-root regression file whose current assertions block completion of
the approved WI-4783 behavior.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - the omitted test file cannot be changed without a revised bridge target path and a new GO.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this REVISED proposal carries forward concrete governing specifications.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - this revision carries project, PAUTH, work item, and inline JSON `target_paths`.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the stale test file must be in scope so verification can remove or update superseded behavior.
- `GOV-STANDING-BACKLOG-001` - WI-4783 remains an open P1 standing-backlog defect item.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - this revision preserves a concrete blocker and correction as an append-only bridge artifact.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - active Phase 2 PAUTH includes WI-4783 and permits source, test, hook, config, and documentation work through bridge gates.
- `GOV-SESSION-ROLE-AUTHORITY-001` - non-dispatcher enforcement must not treat durable registry fallback as Loyal Opposition write authority.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - target-scope drift is corrected in the artifact graph rather than by mutating approved implementation scope informally.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - this NO-GO response is moved to a REVISED proposal state with explicit correction evidence.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - target paths remain inside the GT-KB root and outside adopter application scope.
- `DCL-SESSION-ROLE-RESOLUTION-001` - shared role resolution must distinguish explicit session authority from fallback state.
- `DCL-ROLE-RESOLUTION-DECLARED-AUTHORITY-001` - role authority is owner-declared, not inferred from stale or mismatched registry state.
- `ADR-ROLE-AUTHORITY-DECLARED-NOT-DETECTED-001` - preserves the declared-not-detected architecture decision.
- `ADR-ROLE-AUTHORITY-INTERACTIVE-PERSISTENCE-001` - explicit interactive role survives compaction/resume within the same context.
- `DCL-INTERACTIVE-SESSION-ROLE-PERSISTENCE-001` - the marker/envelope contract must remain machine-checkable.
- `SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001` - `::init gtkb pb|lo` remains the canonical owner role-direction surface.
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` - harness-surface hook changes must remain cross-harness auditable.
- `ADR-CROSS-HARNESS-PARITY-001` - parity decisions are explicit and auditable across supported harnesses.

## Prior Deliberations

- `DELIB-20265878` - owner AUQ creating the dispatcher-only role-authority purge project and selecting "capture principle + file as project."
- `DELIB-20260629-HARNESS-PARITY-PHASE-2-OWNER-DIRECTIVE` - active Phase 2 authorization that includes WI-4783.
- `bridge/gtkb-wi4781-role-authority-dispatcher-only-formalization-004.md` - VERIFIED formalization of the dispatcher-only registry principle.
- `bridge/gtkb-wi4783-session-role-gate-fallback-purge-001.md` - original WI-4783 implementation proposal.
- `bridge/gtkb-wi4783-session-role-gate-fallback-purge-002.md` - Loyal Opposition GO on the original proposal.
- `bridge/gtkb-wi4783-session-role-gate-fallback-purge-003.md` - Prime Builder blocker report identifying the omitted stale test file.
- `bridge/gtkb-wi4783-session-role-gate-fallback-purge-004.md` - Loyal Opposition NO-GO requiring this target-path revision.

## Owner Decisions / Input

No new owner decision is required before filing this revision. The relevant
owner direction is already recorded in `DELIB-20265878`, and bounded
implementation remains authorized by
`PAUTH-PROJECT-HARNESS-PARITY-PHASE-2-IMPLEMENTATION-2026-06-29`.

## Findings Addressed

### Finding 1: Scope Exclusion of Stale Test File

Response: addressed by adding
`platform_tests/scripts/test_lo_file_safety_gate_role_resolution.py` to the
inline JSON `target_paths` block. The next implementation attempt may update
or retire the stale durable-fallback assertions in that file without violating
the implementation-start target scope.

## Scope Changes

- Added `platform_tests/scripts/test_lo_file_safety_gate_role_resolution.py`.
- No source target, project authorization, work item, non-scope item, or owner-decision evidence changed.
- The implementation must still re-check target dirtiness before editing; at revision filing time, `platform_tests/hooks/test_session_role_resolution.py` is already dirty from another workstream.

## Pre-Filing Preflight Subsection

This completed revision is filed through
`.codex/skills/bridge/helpers/revise_bridge.py file`, which runs the candidate
bridge applicability and ADR/DCL clause preflights before writing the live
numbered bridge file.

## Specification-Derived Verification Plan

| Specification | Test or verification command | Expected result |
| --- | --- | --- |
| `GOV-SESSION-ROLE-AUTHORITY-001`; `DCL-SESSION-ROLE-RESOLUTION-001` | `python -m pytest platform_tests/hooks/test_session_role_resolution.py -q --tb=short` | Resolver preserves explicit marker/envelope precedence and treats durable role as fallback, not non-dispatcher enforcement authority. |
| `DCL-INTERACTIVE-SESSION-ROLE-PERSISTENCE-001`; `SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001` | `python -m pytest platform_tests/hooks/test_workstream_focus_session_role_marker.py -q --tb=short` | `::init gtkb pb|lo` writes the per-session marker/envelope that the resolver reads. |
| `GOV-SESSION-ROLE-AUTHORITY-001`; `DCL-ROLE-RESOLUTION-DECLARED-AUTHORITY-001` | `python -m pytest platform_tests/hooks/test_lo_file_safety_gate.py platform_tests/scripts/test_lo_file_safety_gate_role_resolution.py -q --tb=short` | LO file-safety enforcement applies only for explicit LO session authority and fails open for durable-only fallback; stale durable-fallback assertions are removed or replaced. |
| `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001`; `GOV-FILE-BRIDGE-AUTHORITY-001` | `python -m pytest platform_tests/scripts/test_strict_drop_misdirected_headless_dispatch.py -q --tb=short` plus bridge-compliance audit on the filed proposal | Dispatcher/headless strict-drop behavior remains unchanged and harness-surface disposition remains auditable. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Post-implementation report carries this table forward with exact command output. | Loyal Opposition can verify source changes against executed evidence. |

## Risk And Rollback

Risk remains the same as the original proposal: removing fallback authority too
broadly could weaken explicit Loyal Opposition file-safety enforcement. The
mitigation remains focused tests for explicit LO marker/envelope enforcement
and durable-only fail-open behavior.

Rollback is a normal revert of the future source/test implementation commit.
Bridge files are append-only audit artifacts and are not deleted by rollback.
