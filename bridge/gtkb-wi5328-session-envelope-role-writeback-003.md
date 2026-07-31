REVISED
author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: A-2026-07-16T12-17-36Z
author_model: OpenAI Codex
author_model_version: GPT-5
author_model_configuration: Codex Desktop interactive Prime Builder; governed bridge revision

# Revised Implementation Proposal - WI-5328 Session Envelope Role Writeback

bridge_kind: prime_proposal
Document: gtkb-wi5328-session-envelope-role-writeback
Version: 003
Responds to: bridge/gtkb-wi5328-session-envelope-role-writeback-002.md
Date: 2026-07-16 UTC

Project Authorization: PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-RUNTIME-INTERFACES-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-PLATFORM-MODERNIZATION-RUNTIME-INTERFACES
Work Item: WI-5328
target_paths: ["groundtruth-kb/src/groundtruth_kb/session/envelope.py", "scripts/session_self_initialization.py", ".claude/hooks/workstream-focus.py", "platform_tests/scripts/test_session_self_initialization.py"]

implementation_scope: source, test, configuration
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
Recommended commit type: fix

## Revision Claim

This revision corrects the project-linkage defect identified by version 002.
WI-5328 is now a member of and its bridge thread is linked to the active,
owner-chartered Runtime Interfaces project. The project-scope PAUTH has no
per-work-item inclusion restriction and explicitly covers session/activity
contracts, role bootstrap, recovery, diagnostics, source, test, configuration,
metadata, and governed bridge work.

The substantive defect, four target paths, and two-part fix remain unchanged.
The stale statement about WI-5314 is corrected: that adjacent thread is latest
`NO-GO` at version 006, not GO. The helper-suggested prior-deliberation
placeholder from version 001 is removed and the cross-cutting artifact specs
reported as advisory omissions by version 002 are added.

## Requirement Sufficiency

Existing requirements are sufficient. The active Runtime Interfaces project
and PAUTH are grounded in `DELIB-202666274`; no new project, target, requirement,
or owner decision is created by this revision.

## Findings Addressed

### F1 (P0, blocking) - Missing mandatory project-linkage metadata

Response: corrected.

- Project membership: `gt projects add-item` linked WI-5328 to
  `PROJECT-GTKB-PLATFORM-MODERNIZATION-RUNTIME-INTERFACES`.
- Bridge linkage: `gt projects link-bridge` linked this exact thread.
- Project authorization:
  `PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-RUNTIME-INTERFACES-20260715-PROJECT-SCOPE`,
  active version 2, no per-work-item restriction.
- Mandatory `Project Authorization:`, `Project:`, and `Work Item:` lines now
  appear in the machine-readable header.

### Minor staleness - WI-5314 status

Response: corrected. WI-5314 remains adjacent and must be coordinated, but its
live latest status is `NO-GO` at
`bridge/gtkb-wi5314-nonspawn-session-envelope-suppression-006.md`.

## Proposed Scope

1. Trace the existing `UserPromptSubmit` init-keyword path and persist a valid
   `::init gtkb pb|lo` match into the current session envelope before any
   downstream role-authority consumer runs.
2. Update the current-session envelope fields consistently: `role`,
   `role_resolved`, `role_asserted`, `init_keyword`, interactive role source,
   and worker-role provenance. Do not modify dispatcher/default role metadata.
3. Add a fail-loud consistency check for an envelope that claims transcript
   role resolution while retaining `session_resolver_fallback` provenance.
4. Add focused tests proving explicit PB and LO directives override the durable
   fallback only for the current interactive session and remain isolated from
   concurrent or stale session markers.

Out of scope: dispatcher selection/configuration, role registry mutation,
credentials, deployment, release, Git finalization, unrelated WI-5314 work,
and broad session-envelope redesign.

## Cross-Harness Disposition

The canonical session-envelope role semantics are harness-independent. This
slice repairs the currently missing Claude `UserPromptSubmit` writeback call
without creating a Claude-specific role rule.

| Harness / surface | Disposition |
| --- | --- |
| Claude Code | `.claude/hooks/workstream-focus.py` may call the canonical envelope update after matching an explicit init keyword. No role semantics are defined in the hook. |
| Codex | Existing transcript-defined role persistence remains unchanged; canonical envelope tests must prove the shared updater accepts the same PB/LO values. No Codex hook mutation is proposed. |
| Cursor and Antigravity | No target mutation. They continue consuming canonical session-envelope semantics through their existing adapters. |
| Ollama, OpenRouter, and other headless workers | No target mutation. Their dispatched role remains authoritative from the worker envelope; interactive writeback does not override dispatched role absent an owner directive. |

Any implementation discovery that requires another harness adapter mutation
must stop and return for a revised, explicit parity scope rather than expanding
this candidate in place.

## Specification Links

- `GOV-SESSION-ROLE-AUTHORITY-001`
- `DCL-SESSION-ROLE-RESOLUTION-001`
- `ADR-INTERACTIVE-SESSION-ROLE-OVERRIDE-001`
- `ADR-ROLE-AUTHORITY-INTERACTIVE-PERSISTENCE-001`
- `DCL-INTERACTIVE-SESSION-ROLE-PERSISTENCE-001`
- `ADR-ACTIVITY-ENVELOPE-DISPOSITION-001`
- `DCL-ACTIVITY-ENVELOPE-INTERCEPTION-001`
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001`
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001`
- `ADR-CROSS-HARNESS-PARITY-001`
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-PROJECT-DEPENDENCY-ORDERING-001`
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`

## Prior Deliberations

- `DELIB-202666274` - owner authorization underlying the active project-scope
  Runtime Interfaces PAUTH while preserving GO, claim, start, verification,
  and mechanical-operation gates.
- `DELIB-20260710-GTKB-RUNTIME-CHARTER-SESSION-ROLE-ENVELOPE` - project charter
  and session-role-envelope direction.
- `bridge/gtkb-wi5252-session-envelope-cli-provenance-006.md` - VERIFIED
  related CLI provenance work; does not cover init-keyword writeback.
- `bridge/gtkb-wi5314-nonspawn-session-envelope-suppression-006.md` - adjacent
  nonterminal `NO-GO`; coordinate without adopting its work.
- `bridge/gtkb-session-envelope-durability-001-007.md` - withdrawn related
  durability proposal, not live implementation authority.

## Owner Decisions / Input

- The active PAUTH cites `DELIB-202666274` and imposes no per-work-item
  restriction.
- Version 001 records owner-observed impact and the explicit session-role
  principle. No new owner decision is inferred by this metadata correction.
- Safety condition carried forward: after any future GO, implementation should
  pause for fresh explicit owner confirmation before modifying this
  self-referential role-resolution mechanism.

## Specification-Derived Verification Plan

| Specifications | Verification evidence required |
| --- | --- |
| Session-role authority and interactive persistence specs | Focused tests open PB and LO session envelopes from explicit init keywords and assert all role/provenance fields agree. |
| Envelope interception and freshness specs | Tests prove writeback occurs for the current session before downstream claim/attribution consumers and does not consume stale markers. |
| Dependency ordering / WI-5314 | Target-hunk review proves no WI-5314 nonspawn-suppression behavior is adopted or overwritten. |
| Project/bridge governance specs | Active project membership, PAUTH, independent GO, matching claim, start packet, report, and independent verification remain mandatory. |
| Nonimpairment | Durable dispatcher fallback remains unchanged when no explicit transcript role exists; dispatcher registry is not mutated. |

Expected implementation verification commands after GO:

```text
python -m pytest platform_tests/scripts/test_session_self_initialization.py -q --tb=short --timeout=300
python -m pytest platform_tests/scripts/test_session_envelope.py platform_tests/scripts/test_session_role_resolver.py -q --tb=short --timeout=300
python -m ruff check groundtruth-kb/src/groundtruth_kb/session/envelope.py scripts/session_self_initialization.py .claude/hooks/workstream-focus.py platform_tests/scripts/test_session_self_initialization.py
python -m ruff format --check groundtruth-kb/src/groundtruth_kb/session/envelope.py scripts/session_self_initialization.py .claude/hooks/workstream-focus.py platform_tests/scripts/test_session_self_initialization.py
git diff --check -- groundtruth-kb/src/groundtruth_kb/session/envelope.py scripts/session_self_initialization.py .claude/hooks/workstream-focus.py platform_tests/scripts/test_session_self_initialization.py
```

## Pre-Filing Preflight Subsection

Applicability preflight:

- command: `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5328-session-envelope-role-writeback --content-file .gtkb-state/bridge-revisions/drafts/gtkb-wi5328-session-envelope-role-writeback-003.md --json`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []
- blocking_errors: []

Clause preflight:

- command: `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi5328-session-envelope-role-writeback --content-file .gtkb-state/bridge-revisions/drafts/gtkb-wi5328-session-envelope-role-writeback-003.md`
- clauses evaluated: 5
- must_apply: 3
- may_apply: 2
- evidence gaps in must_apply clauses: 0
- blocking gaps: 0
- exit code: 0

## Risk And Rollback

Risk is moderate because role provenance controls claims, attribution, file
safety, and handoff routing. Controls are current-session isolation, explicit
field-consistency assertions, preservation of no-init fallback behavior, and
focused cross-session regressions.

Rollback is removal of only the approved writeback and consistency-check hunks,
returning to the conservative durable fallback. Bridge evidence remains
append-only. Rollback, Git, release, and deployment require their own authority.
