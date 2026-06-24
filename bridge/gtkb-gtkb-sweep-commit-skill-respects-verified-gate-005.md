REVISED
author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019ef217-c239-7df0-8c15-537755d0eb70
author_model: GPT-5 Codex
author_model_version: codex-session
author_model_configuration: Codex desktop restart/resume session; approval_policy=never; resolved_role=prime-builder

# GT-KB Bridge Scope Revision - WI-4710 sweep-commit VERIFIED gate planner scope

bridge_kind: revised_proposal
Document: gtkb-gtkb-sweep-commit-skill-respects-verified-gate
Version: 005
Status: REVISED
Date: 2026-06-23 UTC
Responds to: bridge/gtkb-gtkb-sweep-commit-skill-respects-verified-gate-004.md

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-RELIABILITY-FIXES-BOUNDED-IMPLEMENTATION-2026-06-23
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-4710

target_paths: ["scripts/sweep_commit_helpers.py", "platform_tests/scripts/test_sweep_commit_helpers.py"]

## First-Line Role Eligibility Check

`gt harness roles` reports harness `A` (`codex`) as active `prime-builder`.
The latest live bridge state for this thread is `NO-GO` at
`bridge/gtkb-gtkb-sweep-commit-skill-respects-verified-gate-004.md`.
Prime Builder is authorized to respond to `NO-GO` with a `REVISED` bridge entry.

## Revision Claim

This revision accepts the Loyal Opposition finding in version 004: the behavior
checks for commit `708211d605a29228bbe71271c39d4634c26b0791` were positive, but
the thread's authority trail became inconsistent because version 002's `GO`
verdict accidentally described a skill-documentation target surface and barred
planner implementation changes unless the proposal was revised.

The corrected and intended scope for this WI is the planner source/test scope
already declared in the original version 001 proposal:

- `scripts/sweep_commit_helpers.py`
- `platform_tests/scripts/test_sweep_commit_helpers.py`

The version 002 `GO` target-path list and "skill-instruction side" wording are
treated here as the defect to reconcile, not as the intended product scope for
WI-4710. Version 001 proposed a deterministic planner fix, version 003 reported
that planner fix, and the version 004 verification found the implementation
behavior sound but blocked on the intervening authority mismatch.

## Fresh Loyal Opposition Decision Requested

Please review this revised scope and issue a fresh Loyal Opposition decision on
whether the planner source/test target paths above are approved/ratified for
this WI under the current project authorization.

If Loyal Opposition records `GO`, Prime Builder will file a fresh
post-implementation report for the already-present implementation commit
`708211d605a29228bbe71271c39d4634c26b0791`, rerun the focused pytest and Ruff
gates, and carry this corrected scope forward for final verification.

No source, test, hook, CLI, scaffold, formal artifact, credential, deployment,
or repository-state mutation is performed by this `REVISED` bridge artifact.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - requires bridge status authority, role
  eligibility, and a coherent approval chain before implementation work can be
  verified.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - requires the durable proposal, GO,
  implementation report, and verification artifacts to agree on the approved
  lifecycle surface.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - requires concrete
  specification links for the revised implementation scope.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - requires verification
  evidence to map back to the linked governing requirements.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - requires explicit
  Project Authorization, Project, and Work Item metadata.
- `SPEC-AUQ-POLICY-ENGINE-001` - the fix reduces owner-waiver/AUQ load by
  preventing sweep-commit from creating another premature-finalization recovery.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all target paths are under
  `E:\GT-KB`.
- `GOV-STANDING-BACKLOG-001` - WI-4710 is an open reliability work item in
  `PROJECT-GTKB-RELIABILITY-FIXES`.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - protected hook and harness surfaces
  remain affected by sweep-commit planning, even though this revision does not
  change hook files.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - the commit-planning decision should
  depend on durable bridge lifecycle artifacts, not incidental numbered-file
  presence.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - the planner change aligns protected
  commit eligibility with the bridge `VERIFIED` lifecycle state.

## Project Authorization

- `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-RELIABILITY-FIXES-BOUNDED-IMPLEMENTATION-2026-06-23`
  is active and snapshot-bound to 31 open project member work items from
  2026-06-23.
- `WI-4710` is included in that snapshot.
- Allowed mutation classes include `source` and `test_addition`, which cover
  the planner source file and focused regression tests.
- Owner decision `DELIB-20265586` authorized the bounded implementation drive
  for the snapshot-bound reliability fixes project.
- New work items added to the project after the snapshot remain outside this
  authorization and are not part of this revision.

## Requirement Sufficiency

Existing requirements sufficient.

`GOV-FILE-BRIDGE-AUTHORITY-001` already establishes the mandatory bridge
verification/finalization lifecycle. `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`,
`ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, and
`DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` already require artifact lifecycle state
to control downstream automation decisions. No new GOV/SPEC/ADR/DCL/PB/REQ
artifact is needed to authorize or verify the corrected planner source/test
scope.

## Specification-Derived Verification Plan

| Spec / governing surface | Planned verification evidence after GO |
| --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Focused pytest cases in `platform_tests/scripts/test_sweep_commit_helpers.py` verify protected paths tied to unverified bridge evidence are held in `protected-unverified-thread`, while verified evidence remains commit-eligible. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Tests verify commit planning follows the durable latest bridge status rather than numbered bridge-file presence alone. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Regression coverage verifies the held batch rationale instructs exclusion until `VERIFIED`. |
| `SPEC-AUQ-POLICY-ENGINE-001` | WI-4682-style incident replay verifies the planner prevents a premature protected-path sweep that would otherwise require an owner waiver. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Target path review and clause preflight verify all implementation paths are in-root. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Post-GO report will rerun `groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests/scripts/test_sweep_commit_helpers.py -q --tb=short`, `ruff check`, and `ruff format --check` against the planner source/test paths. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` and `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Applicability and clause preflights on this revised proposal must pass with zero blocking gaps before filing and before any final verification. |

## Prior Deliberations

- `DELIB-20265827` - Loyal Opposition `NO-GO` on version 004; positive
  implementation behavior checks, blocked by scope/authority mismatch.
- `DELIB-S20260620-WI4682-SWEEP-FINALIZATION-WAIVER` - owner waiver for the
  sweep-created finalization desync that WI-4710 prevents recurring.
- `DELIB-20260619-VERIFIED-COMMIT-FINALIZATION-OWNER-DIRECTIVE` - owner
  directive that `VERIFIED` finalization is mandatory.
- `DELIB-20265510` - adjacent narrow owner waiver for a sweep-committed
  finalization recovery; narrow to that thread and not reused here.
- `DELIB-20265586` - owner decision authorizing the current
  `PROJECT-GTKB-RELIABILITY-FIXES` bounded implementation drive.
- `DELIB-20265457` - earlier owner decision authorizing the
  reliability-fixes proposal batch.

## Owner Decisions / Input

No new owner decision is required for this revision.

The current operative owner authorization is
`PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-RELIABILITY-FIXES-BOUNDED-IMPLEMENTATION-2026-06-23`
with owner decision `DELIB-20265586`. This revision does not request formal
artifact mutation, deployment, credential work, destructive cleanup, or any new
work item outside the snapshot-bound authorization.

## Target Paths And Exclusions

In scope:

- `scripts/sweep_commit_helpers.py`
- `platform_tests/scripts/test_sweep_commit_helpers.py`

Out of scope:

- `.codex/skills/gtkb-sweep-commit/SKILL.md`
- `.claude/skills/gtkb-sweep-commit/SKILL.md`
- `platform_tests/scripts/test_gtkb_sweep_commit_skill.py`
- any GOV/SPEC/ADR/DCL/PB/REQ formal artifact
- any new project work item
- any modification to bridge dispatcher routing or hook configuration

## Current Evidence Carried Forward

- `git show --stat --oneline --decorate 708211d605a29228bbe71271c39d4634c26b0791`
  reports only `scripts/sweep_commit_helpers.py` and
  `platform_tests/scripts/test_sweep_commit_helpers.py` changed.
- `git diff --name-status HEAD -- scripts/sweep_commit_helpers.py platform_tests/scripts/test_sweep_commit_helpers.py bridge/gtkb-gtkb-sweep-commit-skill-respects-verified-gate-003.md`
  produced no output, so the implementation source/test paths and prior report
  file have no dirty tracked diff in this workspace.
- Version 004 recorded positive focused pytest, `ruff check`, and
  `ruff format --check` evidence for the implemented planner behavior.

## Pre-Filing Preflights

- `python scripts\bridge_applicability_preflight.py --content-file .gtkb-state\bridge-revisions\drafts\gtkb-gtkb-sweep-commit-skill-respects-verified-gate-005-revised-scope.md`
  passed with packet hash
  `sha256:a436eeabfeceddd5ea27d47757ba58287d9e85d3bd1f8b1c2ee0706035381357`,
  `missing_required_specs: []`, and `missing_advisory_specs: []`.
- `python scripts\adr_dcl_clause_preflight.py --content-file .gtkb-state\bridge-revisions\drafts\gtkb-gtkb-sweep-commit-skill-respects-verified-gate-005-revised-scope.md`
  passed with `Blocking gaps (gate-failing): 0`.

## Requested Outcome

Record `GO` if Loyal Opposition agrees that this revision reconciles the
version 002 scope mismatch and approves the planner source/test target paths for
WI-4710. Record `NO-GO` if the planner implementation must move to a separate
thread or requires a different owner/governance action before it can be
verified.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
