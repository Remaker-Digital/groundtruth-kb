NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: codex-auto-builder-20260628T161357
author_model: gpt-5-codex
author_model_version: gpt-5-codex-2026-06-28
author_model_configuration: Codex desktop automation; role=Prime Builder; reasoning_effort=default
author_metadata_source: auto-builder-env

# Implementation Proposal - Define and implement recurring work-tree hygiene + stash-stray-cleanup mechanism

bridge_kind: prime_proposal
Document: gtkb-work-tree-hygiene-slice-b-strays-cli
Version: 001
Date: 2026-06-28 UTC

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-AUTHORIZE-WI-4356-IMPLEMENTATION
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-4356

target_paths: ["groundtruth-kb/src/groundtruth_kb/cli.py", "groundtruth-kb/src/groundtruth_kb/hygiene/strays.py", "platform_tests/scripts/test_hygiene_strays_cli.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

Slice B implements the read-only gt hygiene strays triage CLI for WI-4356, consuming the verified stray detector and producing deterministic dry-run recommendations.

Work item description: Owner directive 2026-06-04 S-loop: 'agents wont return after 12h; need recurring work-tree hygiene + stray-cleanup mechanism'. Scope: stale-detection criteria, triage rules, CLI surface + doctor check + optional scheduled enforcement. DELIB precedent: today drop'd 9 stashes (3d to 2wk old) after confirming zero recoverable unique content.

## Claim

Prime Builder proposes a bounded implementation slice for `WI-4356` and keeps the bridge, project authorization, owner-decision, and verification gates intact.

## Requirement Sufficiency

Existing requirements are sufficient for filing this proposal. The work item and active project authorization define the implementation boundary; any missing membership or PAUTH state is created only when explicit owner-decision evidence is supplied.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `groundtruth-kb/src/groundtruth_kb/cli.py`, `groundtruth-kb/src/groundtruth_kb/hygiene/strays.py`, `platform_tests/scripts/test_hygiene_strays_cli.py`.

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
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` - auto-linked governing or work-item specification.

## Prior Deliberations

- `DELIB-20266072` - Loyal Opposition Review - WI-4720 Narrative Staged EOL Parity
- `DELIB-20266310` - GO - gtkb-mass-release-candidate-blocker-repair - GT-KB Mass Release Candidate Blocker Repair
- `DELIB-20266120` - Owner decision: resolve WI-3502 and WI-3503 as substantially-addressed (SoT-freshness final closure)
- `DELIB-20266333` - Separation Check
- `DELIB-20265989` - Verdict

## Owner Decisions / Input

- `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-AUTHORIZE-WI-4356-IMPLEMENTATION` - active project authorization covering `WI-4356`.

## Proposed Scope

- Add a dry-run gt hygiene strays CLI that collects live workspace, stash, and worktree state and feeds the verified stray detector.
- Emit deterministic human and JSON reports with recommended actions only; do not delete, stash, drop, commit, or mutate formal artifacts in this slice.
- Keep implementation scoped to the existing hygiene CLI surface and detector adapter/tests.

## Specification-Derived Verification Plan

| Spec | Verification |
| --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Run targeted pytest and ruff checks and cite exact commands in the implementation report. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `SPEC-AUQ-POLICY-ENGINE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `GOV-STANDING-BACKLOG-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` | Invoke the CLI in tests with freshly supplied git/stash/worktree fixtures and assert no cached summaries or prior reports are used. |

## Acceptance Criteria

- gt hygiene strays runs read-only from live git/worktree/stash state and returns deterministic JSON suitable for bridge evidence.
- Default behavior is dry-run-only and cannot execute destructive or formal-artifact mutations.
- CLI tests cover clean state, stale workspace/stash/worktree findings, and no-active-session false-positive mitigation.

## Risks / Rollback

Risk is moderate because implementation proposals authorize later protected-file work. The service must fail closed around owner-decision evidence, target paths, bridge slug collisions, author metadata, and preflight failures.

Rollback is a revert of the source and test changes. Bridge files and project authorization records are append-only audit artifacts and must not be deleted by rollback.

## Files Expected To Change

- `groundtruth-kb/src/groundtruth_kb/cli.py`
- `groundtruth-kb/src/groundtruth_kb/hygiene/strays.py`
- `platform_tests/scripts/test_hygiene_strays_cli.py`

## Recommended Commit Type

`feat`
