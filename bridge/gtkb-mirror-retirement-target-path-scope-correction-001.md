NEW

author_identity: Codex Prime Builder automation
author_harness_id: A
author_session_context_id: keep-working-automation-2026-06-06T05-20Z
author_model: GPT-5 Codex
author_model_version: gpt-5-codex
author_model_configuration: Codex automation Keep Working PB; workspace E:\GT-KB

# Mirror-Retirement Target-Path Scope Correction

bridge_kind: implementation_proposal
Document: gtkb-mirror-retirement-target-path-scope-correction
Version: 001
Author: Prime Builder (Codex automation)
Date: 2026-06-06 UTC
Recipient: Loyal Opposition
Parent thread: bridge/gtkb-harness-state-sot-consolidation-phase-1-mirror-retirement-012.md (GO)
Project Authorization: PAUTH-PROJECT-GTKB-HARNESS-STATE-SOT-CONSOLIDATION-HARNESS-STATE-SOT-CONSOLIDATION-PHASE-1-IMPLEMENTATION-ENVELOPE
Project: PROJECT-GTKB-HARNESS-STATE-SOT-CONSOLIDATION
Work Item: WI-4336
work_item_ids: [WI-4336, WI-4214]
requires_verification: true
implementation_scope: scoping_correction
target_paths: ["harness-state/role-assignments.json", "scripts/*.py", "scripts/**/*.py", "groundtruth-kb/src/**/*.py", "config/governance/protected-artifact-inventory-drift.toml", "config/registry/sot-artifacts.toml", "config/agent-control/SESSION-STARTUP-INDEX.md", "config/agent-control/SESSION-STARTUP-CONTROL-MAP.md", "config/agent-control/system-interface-map.toml", ".claude/rules/operating-role.md", ".claude/rules/sot-read-discipline.md", "AGENTS.md", "CLAUDE.md", ".groundtruth/inventory/dev-environment-inventory.json", ".groundtruth/formal-artifact-approvals/*.json", "platform_tests/scripts/test_mirror_retirement_role_assignments.py"]

## Claim

`gtkb-harness-state-sot-consolidation-phase-1-mirror-retirement-012.md` is implementation-approved, but the implementation packet generated from `-011` cannot authorize the live files that still need cleanup. This child proposal asks Loyal Opposition to approve a target-path scope correction only. It does not change the mirror-retirement requirements, does not complete implementation, and does not expand the work into `WI-4372`.

## Evidence For The Scope Gap

The live parent thread latest status is `GO` at `bridge/gtkb-harness-state-sot-consolidation-phase-1-mirror-retirement-012.md`. The authorization packet generated for that GO contains the `target_paths` from `-011`:

```text
["harness-state/role-assignments.json", "scripts/**/*.py", "groundtruth-kb/src/**/*.py", "**/*.toml", "**/rules/*.md", "CLAUDE.md", "AGENTS.md", ".groundtruth/inventory/dev-environment-inventory.json", ".groundtruth/formal-artifact-approvals/*.json", "platform_tests/**/*.py"]
```

During implementation-start validation, the gate rejected protected edits because those globs did not cover the concrete live targets:

```text
Target path outside implementation authorization scope: scripts/harness_roles.py, scripts/collect_dev_environment_inventory.py, config/agent-control/SESSION-STARTUP-INDEX.md, config/agent-control/SESSION-STARTUP-CONTROL-MAP.md
```

Live grep evidence confirms the specific surfaces that drive this scope correction:

```text
scripts/harness_roles.py
scripts/collect_dev_environment_inventory.py
config/agent-control/SESSION-STARTUP-INDEX.md
config/agent-control/SESSION-STARTUP-CONTROL-MAP.md
config/agent-control/system-interface-map.toml
config/governance/protected-artifact-inventory-drift.toml
config/registry/sot-artifacts.toml
.claude/rules/operating-role.md
.claude/rules/sot-read-discipline.md
groundtruth-kb/src/groundtruth_kb/mcp_surface/roles.py
groundtruth-kb/src/groundtruth_kb/mode_switch/invariants.py
groundtruth-kb/src/groundtruth_kb/mode_switch/transaction.py
groundtruth-kb/src/groundtruth_kb/mode_switch/validation.py
groundtruth-kb/src/groundtruth_kb/project/doctor.py
```

The problem is not absence of project authorization. `gt projects show PROJECT-GTKB-HARNESS-STATE-SOT-CONSOLIDATION --json` shows PAUTH v2 is active, includes `WI-4336` and `WI-4214`, and allows `source_file`, `test_file`, `config_file`, `protected_narrative_file`, `membase_spec_insert`, and `file_deletion`. The blocker is the approved bridge target-path envelope used by the implementation-start gate.

## Proposed Correction

Approve this child as a scope-correction dependency for the parent mirror-retirement implementation. After GO, Prime Builder may run implementation authorization against this thread and complete the parent objective inside the corrected target paths listed above.

This child preserves the parent implementation semantics:

- Delete `harness-state/role-assignments.json`.
- Remove active retired-path readers, writers, constants, config references, and inventory evidence required for the deletion.
- Regenerate `.groundtruth/inventory/dev-environment-inventory.json` when evidence changes.
- Add/update `platform_tests/scripts/test_mirror_retirement_role_assignments.py`.
- Generate formal approval packets and run `scripts/check_narrative_artifact_evidence.py` only if protected narrative targets actually change.

This child does not authorize:

- Implementation, completion, or mutation of `WI-4372`.
- Broad doctor predicate refinement beyond what is required to avoid claiming false mirror-retirement completion.
- Role-state value changes.
- New harness registration or capability changes.
- Pushes.

## Dependency And Future-Work Check

`WI-4336` has precedence because it is the open, approved clean-delete work item for the legacy mirror and is the final child of Harness State SoT Phase 1. `WI-4214` remains included by PAUTH v2 as cross-project retirement support. `WI-4372` is a dependent follow-on: it refines `_check_harness_state_sot_consistency` and migrates remaining L2/direct-reader noise after mirror-retirement boundaries are clean. This proposal intentionally keeps `WI-4372` future work.

The earlier parent proposal `-011` tried to express the same broad cleanup with globs. This child exists only because the implementation-start validator requires parseable concrete target paths for the actual top-level scripts and startup-control config documents.

## Code Quality Baseline

| Rule ID | Applies? | Compliance plan | Verification | Waiver / N/A reason |
|---|---|---|---|---|
| CQ-SECRETS-001 | Yes | Proposal and implementation should contain only path/spec evidence, no credentials or environment values. | Bridge credential scan and diff review. | |
| CQ-PATHS-001 | Yes | Keep all target paths root-relative and under `E:/GT-KB`; implementation report must list actual changed paths. | Bridge preflights and changed-path review. | |
| CQ-COMPLEXITY-001 | Yes | Limit implementation to mirror-retirement cleanup, not doctor redesign or broader reader migration. | Focused tests and code review. | |
| CQ-CONSTANTS-001 | Yes | Remove retired-path constants and avoid substitute magic path literals outside canonical registry references. | Targeted grep for retired path tokens. | |
| CQ-SECURITY-001 | Yes | Preserve implementation authorization, bridge review, protected-narrative, and credential-scan gates. | Authorization packet plus bridge audit. | |
| CQ-DOCS-001 | Yes | If protected narrative files change, keep wording scoped to SoT cleanup and attach approval-packet evidence. | Narrative evidence checker when applicable. | |
| CQ-TESTS-001 | Yes | Use the focused mirror-retirement platform test plus relevant grep checks. | `python -m pytest platform_tests/scripts/test_mirror_retirement_role_assignments.py -q --tb=short`. | |
| CQ-LOGGING-001 | N/A | No runtime logging behavior is proposed. | Changed-path review. | No logging surface is in scope. |
| CQ-VERIFICATION-001 | Yes | Run focused pytest, ruff, bridge applicability, and ADR/DCL clause preflights before report filing. | Command evidence in post-implementation report. | |

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`: file this child through `bridge/INDEX.md` as a new versioned bridge document and leave the parent thread append-only.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`: this section cites the concrete governing specs for the scope correction.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`: verification plan maps requirements to exact checks before any post-implementation report.
- `RETIRE-SPEC-HARNESS-STATE-ROLE-ASSIGNMENTS-001`: preserve the clean-delete objective and file-absent/no-live-read assertions.
- `DCL-HARNESS-STATE-SOT-ASSERTION-001`: corrected target paths let the implementation satisfy retired-path assertions instead of leaving known active references.
- `GOV-HARNESS-STATE-SOT-CONSOLIDATION-001`: keep the role registry as the canonical role SoT and remove stale mirror surfaces.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001`: remove stale substitute evidence from live control/config/source surfaces.
- `GOV-HARNESS-ROLE-PORTABILITY-001`: do not alter role values; change read/reference surfaces only.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`: use active PAUTH v2 and stay inside included `WI-4336` plus `WI-4214`.
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001`: correct the executable target-path envelope without expanding the approved project work.
- `DCL-WORK-ITEM-MUST-BELONG-TO-APPROVED-PROJECT-001`: exclude unapproved `WI-4372` implementation and keep all work-item claims PAUTH-covered.
- `GOV-ARTIFACT-APPROVAL-001`: require approval packets for protected narrative targets if changed.
- `DCL-ARTIFACT-APPROVAL-HOOK-001`: require narrative evidence checker evidence for changed protected narrative files.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`: all target paths are inside `E:/GT-KB`.
- `.claude/rules/project-root-boundary.md`: no live dependency or write outside the GT-KB root.
- `GOV-STANDING-BACKLOG-001`: preserve WI precedence and record the dependency boundary rather than hiding it in implementation.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`: treat the blocked implementation envelope as a governed bridge artifact requiring review.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`: capture the scope correction as a durable artifact instead of an ad-hoc bypass.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`: handle a lifecycle trigger caused by a retired artifact deletion path.

## Requirement Sufficiency

Existing requirements are sufficient. The parent GO, PAUTH v2, and owner decision history already authorize mirror retirement. This child requests only a corrected target-path envelope so Prime Builder can implement the already-approved objective through the implementation-start gate.

No new owner decision is required. No owner waiver is requested.

## Prior Deliberations

- `DELIB-S421-MIRROR-RETIREMENT-FULL-SWEEP-DECISION`: controlling decision for full cleanup sweep, writer removal, no DCL amendment, no retire-spec amendment, and no waiver.
- `DELIB-20260668`: Phase-1 owner decisions, including clean deletion of the mirror.
- `DELIB-20260669`: stale mirror drift evidence.
- `DELIB-20260880`: PAUTH v2 adding `WI-4214`.
- `bridge/gtkb-harness-state-sot-consolidation-phase-1-mirror-retirement-011.md`: latest approved parent proposal with under-parsed target globs.
- `bridge/gtkb-harness-state-sot-consolidation-phase-1-mirror-retirement-012.md`: GO verdict authorizing implementation but requiring actual changed-path evidence.
- `bridge/gtkb-impl-start-target-paths-preflight-009.md`: relevant precedent that target-path parseability is a governed implementation-start concern.

## Owner Decisions / Input

No new owner input is required.

The controlling decisions are already archived:

- `DELIB-S421-MIRROR-RETIREMENT-FULL-SWEEP-DECISION`.
- `DELIB-20260668`.
- `DELIB-20260880`.

This proposal does not request a waiver and does not alter the owner-approved mirror-retirement outcome.

## Spec-Derived Verification Plan

- Corrected executable target scope: run `python scripts/implementation_authorization.py begin --bridge-id gtkb-mirror-retirement-target-path-scope-correction`; acceptance is that an authorization packet opens and includes the corrected target paths.
- File deletion: run `Test-Path harness-state/role-assignments.json`; acceptance is `False` after implementation.
- Retired live references removed: run targeted `rg` checks on changed live surfaces plus the focused test; acceptance is no active retired-path reader/writer/config evidence remains except explicitly retained historical evidence.
- Retire-spec assertions: run `python -m pytest platform_tests/scripts/test_mirror_retirement_role_assignments.py -q --tb=short`; acceptance is pass.
- Source hygiene: run `ruff check` and `ruff format --check` on changed Python targets; acceptance is pass.
- Project boundary and work-item boundary: inspect post-implementation changed-path list and grep for `WI-4372` completion claims; acceptance is all changed paths approved and no `WI-4372` mutation/completion claim.
- Protected narrative evidence: when protected narrative files change, run `python scripts/check_narrative_artifact_evidence.py --paths <changed protected narrative paths> --json`; acceptance is pass, or report states no protected narrative files changed.
- Bridge gates: run bridge applicability and ADR/DCL clause preflights on the implementation report before filing; acceptance is pass.

## Acceptance Criteria

- Loyal Opposition approves the corrected target-path envelope or identifies any path that should be narrowed or moved to a separate child.
- Implementation-start authorization can be opened against this child without the target-path denial seen in the parent thread.
- Parent mirror-retirement implementation remains bounded to `WI-4336` and `WI-4214`.
- `WI-4372` remains open follow-on work unless separately authorized.

## Risk And Rollback

Risk: the corrected `scripts/*.py` target is broad enough to include follow-on `WI-4372` surfaces. Mitigation: this proposal explicitly forbids `WI-4372` implementation and requires exact changed-path evidence in the post-implementation report.

Risk: protected narrative files might be needed to remove active stale instructions. Mitigation: the target paths include known protected narrative surfaces and require approval packets plus evidence checking if they change.

Risk: inventory regeneration may surface unrelated drift. Mitigation: implementation must stage/report only mirror-retirement target changes and document any unrelated drift as residual risk, not bundle it.

Rollback: this child only authorizes a future implementation. Before implementation, rollback is deleting/withdrawing this proposal if LO rejects it. After implementation, normal file-level revert applies to source/config/test/doc/inventory edits and deleted mirror restoration if LO returns NO-GO on the post-implementation report.

## Pre-Filing Preflight Subsection

The candidate file was created without an INDEX entry first, so it was not actionable when these checks ran.

Commands:

```text
python scripts\bridge_applicability_preflight.py --bridge-id gtkb-mirror-retirement-target-path-scope-correction --content-file bridge\gtkb-mirror-retirement-target-path-scope-correction-001.md --json
python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-mirror-retirement-target-path-scope-correction --content-file bridge\gtkb-mirror-retirement-target-path-scope-correction-001.md
python scripts\check_code_quality_baseline_parity.py bridge\gtkb-mirror-retirement-target-path-scope-correction-001.md
```

Observed results:

- Applicability preflight exit 0; `preflight_passed: true`.
- Applicability missing required specs: `[]`.
- Applicability missing advisory specs: `[]`.
- Applicability warnings: missing parent directories for wildcard planning globs `groundtruth-kb/src/**/*.py` and `scripts/**/*.py`; non-blocking.
- ADR/DCL clause preflight exit 0; blocking gaps 0.
- Code Quality Baseline parity clean.
