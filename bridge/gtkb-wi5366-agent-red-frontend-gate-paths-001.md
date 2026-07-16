NEW

# Implementation Proposal - Point RC frontend gates at canonical Agent Red packages

bridge_kind: prime_proposal
Document: gtkb-wi5366-agent-red-frontend-gate-paths
Version: 001
Author: Prime Builder (Codex A)
Date: 2026-07-16 UTC

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f5f6d-60cd-7040-b73f-c7d23757c4bc
author_model: GPT-5 Codex
author_model_version: GPT-5
author_model_configuration: Codex Desktop interactive; role=prime-builder; approval_policy=never; sandbox=danger-full-access

Project Authorization: PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE
Work Item: WI-5366

target_paths: ["scripts/release_candidate_gate.py", "platform_tests/scripts/test_release_candidate_gate.py"]

implementation_scope: source,test
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

Repair the release-candidate frontend lane so every npm invocation targets the
four existing Agent Red packages under the canonical application root. Replace
the brittle `project.startswith("admin")` classification with one explicit
widget path and an explicit three-entry admin path list. Preserve the single
root-level environment-sync command, lifecycle-script suppression for all admin
builds, and fail-closed behavior when npm, PowerShell, package dependencies, or
a frontend test/build fails.

Both target files contain unrelated pre-start WI-5165 changes. Implementation,
review, reporting, and any later finalization must be hunk-scoped to WI-5366;
whole-file staging or ownership is prohibited.

## Specification Links

- `GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001` - the frozen frontend release activity must execute against the packages that actually exist.
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` - the repair must not skip frontend verification, weaken failures, or duplicate application packages at the repository root.
- `GOV-RELEASE-READINESS-GOVERNED-TESTING-001` - release readiness requires the real widget test/build and all three admin builds to execute successfully.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - Agent Red application packages live below the canonical application root.
- `GOV-AGENT-RED-NESTED-IN-APPLICATIONS-001` - GT-KB must address the adopter through its nested applications placement rather than legacy root directories.
- `DCL-PROJECT-DEPENDENCY-ORDERING-001` - WI-5366 must preserve the independently owned pre-start WI-5165 hunks in both shared files.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - the defect, proposal, tests, implementation report, and verification remain linked as one durable repair chain.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - the hygiene finding remains open until implementation and independent verification complete.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - the discovered RC defect is preserved as WI-5366 rather than handled as untracked incidental work.
- `GOV-STANDING-BACKLOG-001` - WI-5366 is the durable backlog owner for the frontend-path blocker.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - protected source and test changes require independent GO, matching claim/start authority, reporting, and independent VERIFIED.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - the exact source and test targets are bound to the governing requirements.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - verification must execute the exact command-routing assertions and focused regression module.

## Prior Deliberations

- `DELIB-202666274` - authorizes the modernization program at project scope while retaining independent GO, claim/start, VERIFIED, and exact Git boundaries.

## Owner Decisions / Input

No new owner decision is required. The active Assurance project PAUTH covers
source and test repair for the frozen release-candidate contract. This proposal
does not authorize dispatcher/TAFE/harness mutation, direct harness contact,
manual routing, database mutation, Git staging/commit/push, deployment,
release, credentials, or cleanup.

## Requirement Sufficiency

Existing requirements are sufficient. The failure is a stale path projection,
not a missing product requirement: all four package manifests are present under
the canonical Agent Red application root, while the gate still addresses the
retired repository-root paths.

## Proposed Scope

1. Define the Agent Red application root once using platform-neutral path joins.
2. Define one widget package path and three explicit admin package paths below that root.
3. Run the widget test and widget build against the canonical widget package.
4. Run the existing environment-sync PowerShell script exactly once from the GT-KB root.
5. Build each canonical admin package with `npm_config_ignore_scripts=true` so package lifecycle hooks cannot repeat the sync or mutate environment files.
6. Remove string-prefix classification of widget versus admin packages.
7. Strengthen the focused test to assert the exact ordered npm/PowerShell command sequence and the admin-only environment override.
8. Preserve the existing missing-npm failure test and add no skip, fallback, synthetic package, dependency installation, or root-package recreation.
9. Record pre-implementation hashes and produce a WI-5366-only patch. Preserve every unrelated current worktree byte.

## Intuitiveness/Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "WI-5366 authoritative-worktree diagnosis under DELIB-202666274",
  "canonical_authority": "GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001",
  "primary_route": "python -m pytest platform_tests/scripts/test_release_candidate_gate.py -q --tb=short",
  "before_behavior": "The RC frontend lane invokes npm below nonexistent repository-root widget and admin package paths, so it cannot exercise the four canonical Agent Red packages.",
  "after_behavior": "The lane runs the widget test and build plus all three admin builds against explicit package roots below applications/Agent_Red while preserving one environment sync and fail-closed command handling.",
  "self_descriptive_naming": "Separate agent_red_root, widget_project, and admin_projects values make package ownership and command routing literal instead of inferring role from a legacy string prefix.",
  "obsolete_guidance_disposition": "Legacy repository-root widget/admin path assumptions are removed only from the RC function and its focused assertions; no compatibility fallback or duplicate root package is created.",
  "history_preservation": "WI-5165 and all other pre-start hunks in both shared files remain byte-identical outside the WI-5366 patch and retain independent ownership.",
  "baseline": {
    "canonical_widget_packages": 1,
    "canonical_admin_packages": 3,
    "legacy_gate_prefixes": 4,
    "commands_reaching_canonical_packages": 0
  },
  "expected_result": {
    "canonical_widget_test_commands": 1,
    "canonical_widget_build_commands": 1,
    "canonical_admin_build_commands": 3,
    "environment_sync_commands": 1,
    "legacy_gate_prefixes": 0
  },
  "rollback": "Revert only the WI-5366 source and test hunks through a separately governed transaction; preserve WI-5165, concurrent bytes, package trees, database state, and bridge history.",
  "hard_invariants": [
    "no frontend activity is skipped or converted to advisory behavior",
    "no package or dependency is created, installed, copied, or relocated",
    "admin lifecycle scripts remain suppressed during all three admin builds",
    "environment sync executes exactly once",
    "no unrelated shared-file hunk is changed or finalized"
  ],
  "fail_closed_conditions": [
    "npm or PowerShell is unavailable",
    "a canonical package dependency is missing",
    "the widget test or any frontend build fails",
    "the exact ordered command-routing assertion fails",
    "the proposed patch overlaps an unrelated pre-start hunk"
  ],
  "essential_context_preservation": "The canonical Agent Red placement, four package identities, complete command sequence, lifecycle suppression, and shared-file ownership boundary remain explicit in proposal and test evidence."
}
```

## Specification-Derived Verification Plan

| Requirement | Verification | Expected result |
|---|---|---|
| Canonical package routing | Run the focused release-gate test module and inspect the captured command sequence | Widget test/build and all three admin builds use paths below `applications/Agent_Red`; no root `widget` or `admin` prefix remains. |
| Ordered complete frontend lane | Assert the complete six-command sequence in the focused unit test | Exactly two widget commands, one sync command, and three admin build commands execute in order. |
| Admin lifecycle suppression | Inspect captured environments for the three admin build commands | Every admin build has `npm_config_ignore_scripts=true`; widget commands and sync are not misclassified. |
| Fail closed | Execute the existing missing-npm test and injected `_run` failure fixtures | Missing tooling or any command failure remains a gate failure; no skip or fallback is introduced. |
| Real package existence | Verify each targeted package directory contains a package manifest in the authoritative worktree | All four command prefixes resolve to real package roots. |
| Regression | `python -m pytest platform_tests/scripts/test_release_candidate_gate.py -q --tb=short` | Focused module passes without modifying application files or installing dependencies. |
| Hunk isolation | Compare pre-start hashes, `git diff --check`, and the WI-5366 patch against both target files | Only the frontend function and its focused command-routing test change; all WI-5165 and concurrent hunks remain byte-identical. |

## Acceptance Criteria

1. Every frontend command addresses a real package below the canonical Agent Red application root.
2. The widget test and build both execute; all three admin builds execute.
3. Environment sync executes once and admin lifecycle scripts remain disabled.
4. Missing tools, dependencies, or command failures remain blocking failures.
5. No duplicate root package, fallback path, dependency install, or skip is added.
6. The focused release-gate tests pass and prove exact ordered command routing.
7. WI-5165 and all concurrent bytes in the shared files are unchanged outside the approved WI-5366 hunks.
8. Independent Loyal Opposition review returns VERIFIED before completion is claimed.

## Risk / Rollback

The main risk is accidentally classifying canonical admin paths by their old
root prefix, which would skip all admin builds. Explicit separate lists and an
exact command-sequence assertion remove that ambiguity. A second risk is
absorbing unrelated dirty hunks from the shared files; pre-start hashes and
hunk-only evidence control it.

Rollback reverts only the WI-5366 frontend-routing and focused-test hunks through
a separately governed transaction. It must preserve WI-5165, all other
concurrent work, the canonical package tree, database state, and bridge history.

## Bridge Filing

File this as the next append-only numbered proposal for
`gtkb-wi5366-agent-red-frontend-gate-paths`. Deterministic TAFE/bridge routing is
external to this session; no manual routing or direct harness contact occurs.

## Recommended Commit Type

`fix` - corrects release-candidate execution paths without changing release scope.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
