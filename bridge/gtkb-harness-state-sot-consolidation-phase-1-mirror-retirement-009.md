REVISED
author_identity: Codex Prime Builder automation
author_harness_id: A
author_session_context_id: keep-working-2026-06-06
author_model: GPT-5 Codex
author_model_version: gpt-5-codex
author_model_configuration: Codex desktop automation, owner-requested Prime Builder mode
author_metadata_source: automation prompt plus live bridge revision helper

# Phase-1 Mirror-Retirement REVISED-4 - protected narrative packet plan and deliberation conflict disposition

Document: gtkb-harness-state-sot-consolidation-phase-1-mirror-retirement
Version: 009
Author: Codex Prime Builder automation
Date: 2026-06-06 UTC
Recipient: Loyal Opposition
Responds to: bridge/gtkb-harness-state-sot-consolidation-phase-1-mirror-retirement-008.md
Project: PROJECT-GTKB-HARNESS-STATE-SOT-CONSOLIDATION
Project Authorization: PAUTH-PROJECT-GTKB-HARNESS-STATE-SOT-CONSOLIDATION-HARNESS-STATE-SOT-CONSOLIDATION-PHASE-1-IMPLEMENTATION-ENVELOPE
Work Item: WI-4336
work_item_ids: [WI-4336, WI-4214, WI-4372]
target_paths: ["harness-state/role-assignments.json", "scripts/**/*.py", "groundtruth-kb/src/**/*.py", "**/*.toml", "**/rules/*.md", "CLAUDE.md", "AGENTS.md", ".groundtruth/inventory/dev-environment-inventory.json", ".groundtruth/formal-artifact-approvals/*.json", "platform_tests/**/*.py"]
requires_verification: true
implementation_scope: implementation

## Revision Claim

REVISED-4 keeps the full retired-path cleanup sweep from REVISED-3 and fixes the two NO-GO findings in `bridge/gtkb-harness-state-sot-consolidation-phase-1-mirror-retirement-008.md`:

1. Protected narrative targets now have an explicit approval-packet plan, concrete packet command, staged-evidence verification step, and governing specification links.
2. The older amend-path deliberation is cited and explicitly superseded by the later full-sweep decision for this bridge thread.

No DCL amendment, retire-spec amendment, owner waiver, or backlog-as-waiver is proposed in this revision.

## Findings Addressed

### F1 - P1 - Protected narrative edits lack the mandatory approval-packet plan

Accepted. REVISED-3 expanded the target set to include protected narrative authority files through `**/rules/*.md`, `CLAUDE.md`, and `AGENTS.md`, but it did not include the separate narrative-artifact approval lane required by the active registry and pre-commit evidence checker.

This revision adds:

- `GOV-ARTIFACT-APPROVAL-001` and `DCL-ARTIFACT-APPROVAL-HOOK-001` to `## Specification Links`.
- `.groundtruth/formal-artifact-approvals/*.json` to `target_paths` for the approval packets that may be generated during implementation.
- A dedicated `## Protected Narrative Approval Packet Plan` section below.
- Verification commands that run `python scripts/check_narrative_artifact_evidence.py --paths <protected narrative paths>` after the narrative targets and packet files are staged.

Implementation rule: if the actual cleanup changes zero protected narrative files, no narrative packet is required. If it changes one or more protected narrative files, Prime must create one matching packet per changed protected narrative target before filing the post-implementation report.

### F2 - P2 - The proposal should explicitly supersede the conflicting amend-path deliberation

Accepted. The Deliberation Archive contains two records for the mirror-retirement resolution path:

- `DELIB-MIRROR-RETIREMENT-AMEND-PATH-2026-06-05` records the older amend-both-specs path.
- `DELIB-S421-MIRROR-RETIREMENT-FULL-SWEEP-DECISION` records the later full cleanup sweep and writer-removal path.

For this bridge thread, `DELIB-S421-MIRROR-RETIREMENT-FULL-SWEEP-DECISION` supersedes `DELIB-MIRROR-RETIREMENT-AMEND-PATH-2026-06-05`. The supersession reason is the S421 recovered owner decision content: `DECISION-1101` clarified that the DCL-amendment-only REVISED@-005 was contradictory to `DECISION-1095`, and the next revision must follow the full-sweep decision. Therefore the implementation path remains full cleanup, writer removal, no DCL amendment, no retire-spec amendment, and no waiver.

## Owner Decisions / Input

- `DELIB-S421-MIRROR-RETIREMENT-FULL-SWEEP-DECISION` records the controlling owner-selected path: full cleanup sweep plus writer removal; no DCL amendment; no retire-spec amendment; no waiver.
- `DELIB-MIRROR-RETIREMENT-AMEND-PATH-2026-06-05` is explicitly superseded for this bridge thread by `DELIB-S421-MIRROR-RETIREMENT-FULL-SWEEP-DECISION` for the reason above.
- Existing Phase-1 owner and PAUTH evidence still applies: `DELIB-20260668`, `DELIB-20260669`, and `DELIB-20260880`.

No new owner input is required before Loyal Opposition review. Implementation-time narrative packets must quote the existing full-sweep owner decision as the explicit change request evidence for the specific protected narrative target being changed.

## Requirement Sufficiency

Existing requirements are sufficient. This revision does not change the operative retire-spec or DCL assertions; it only adds the missing approval-packet execution plan required for protected narrative files and resolves the DA conflict disposition.

The implementation remains governed by:

- `RETIRE-SPEC-HARNESS-STATE-ROLE-ASSIGNMENTS-001`: file absent post-WI-4336 and no live code references to the retired path outside whitelisted bridge/audit/packet contexts.
- `DCL-HARNESS-STATE-SOT-ASSERTION-001`: role-state read path is the canonical projection and the retired mirror is physically absent.
- `GOV-HARNESS-STATE-SOT-CONSOLIDATION-001` and `GOV-SOURCE-OF-TRUTH-FRESHNESS-001`: stale role-state substitutes are eliminated.
- `GOV-ARTIFACT-APPROVAL-001` and `DCL-ARTIFACT-APPROVAL-HOOK-001`: protected narrative mutations carry approval-packet evidence and staged-content hash validation.

## Prior Deliberations

- `DELIB-S421-MIRROR-RETIREMENT-FULL-SWEEP-DECISION` - controlling decision for this revision and implementation path.
- `DELIB-MIRROR-RETIREMENT-AMEND-PATH-2026-06-05` - older conflicting amend-path decision; superseded by `DELIB-S421-MIRROR-RETIREMENT-FULL-SWEEP-DECISION` for this bridge thread because the later recovered owner decision states the next revision must follow the full-sweep path instead of the DCL-amendment-only path.
- `DELIB-20260668` - Phase-1 owner decisions, including clean delete of the mirror.
- `DELIB-20260669` - drift evidence motivating retirement.
- `DELIB-20260880` - PAUTH v2 amendment including WI-4214.
- `bridge/gtkb-harness-state-sot-consolidation-phase-1-foundation-012.md`, `bridge/gtkb-harness-state-sot-consolidation-phase-1-scripts-source-010.md`, and `bridge/gtkb-harness-state-sot-consolidation-phase-1-rule-files-010.md` - VERIFIED prerequisites.
- `bridge/gtkb-harness-state-sot-consolidation-phase-1-mirror-retirement-008.md` - latest NO-GO that this revision addresses.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - versioned bridge revision filed through `bridge/INDEX.md`.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - concrete governing specs are linked here.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the verification plan maps requirements to executable checks.
- `RETIRE-SPEC-HARNESS-STATE-ROLE-ASSIGNMENTS-001` - operative deletion authorization.
- `DCL-HARNESS-STATE-SOT-ASSERTION-001` - role-state SoT assertions.
- `GOV-HARNESS-STATE-SOT-CONSOLIDATION-001` - SoT consolidation contract.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` - stale substitute removal.
- `GOV-HARNESS-ROLE-PORTABILITY-001` - role registry remains canonical and portable; no role-set value changes.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - active PAUTH covers the bounded implementation.
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` - work remains inside the Phase-1 authorization envelope.
- `GOV-ARTIFACT-APPROVAL-001` - protected narrative authority files require approval-packet evidence.
- `DCL-ARTIFACT-APPROVAL-HOOK-001` - narrative-artifact gate and universal staged-content evidence checker must pass.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all target paths remain under the GT-KB project root.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, and `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - advisory lifecycle framing.

## Scope Changes Versus REVISED-3

Retained from REVISED-3:

- Full governed-surface retired-token cleanup across source, package source, governed TOML, governed rules markdown, root harness guidance, inventory, and tests.
- Compatibility writer removal in `scripts/harness_roles.py`.
- Deletion of `harness-state/role-assignments.json`.
- Regeneration of `.groundtruth/inventory/dev-environment-inventory.json`.
- No DCL amendment, no retire-spec amendment, and no waiver.

Added in REVISED-4:

- `.groundtruth/formal-artifact-approvals/*.json` as an implementation target for narrative approval packets.
- Narrative-artifact approval packet generation and verification steps for protected narrative files actually changed.
- Explicit DA conflict disposition: `DELIB-S421-MIRROR-RETIREMENT-FULL-SWEEP-DECISION` supersedes `DELIB-MIRROR-RETIREMENT-AMEND-PATH-2026-06-05` for this bridge thread.

## Protected Narrative Approval Packet Plan

During implementation, Prime must classify actual changed files against `config/governance/narrative-artifact-approval.toml`.

Protected narrative targets include:

- `.claude/rules/*.md`
- `AGENTS.md`
- `CLAUDE.md`

For each changed protected narrative target, Prime must generate one packet under `.groundtruth/formal-artifact-approvals/` before filing the post-implementation report. The packet must use:

- `artifact_type`: `narrative_artifact`
- `action`: `update` unless the implementation creates or deletes the target
- `target_path`: the project-root-relative path being changed
- `source_ref`: `gtkb-harness-state-sot-consolidation-phase-1-mirror-retirement`
- `full_content`: the complete proposed target content
- `full_content_sha256`: sha256 of the complete proposed target content
- `approval_mode`: `approve`
- `presented_to_user`: `true`
- `transcript_captured`: `true`
- `explicit_change_request`: quote the owner full-sweep decision from `DELIB-S421-MIRROR-RETIREMENT-FULL-SWEEP-DECISION`, especially the instruction to remove all retired-path references across `.claude/rules/`, `CLAUDE.md`, and `AGENTS.md`.
- `changed_by`: the implementing harness identity
- `change_reason`: cite this bridge thread and the protected narrative target cleanup.

Executable packet path:

```text
groundtruth-kb\.venv\Scripts\python.exe -m groundtruth_kb generate-approval-packet --kind narrative --target <protected-target> --artifact-id <stable-artifact-id> --action update --source-ref gtkb-harness-state-sot-consolidation-phase-1-mirror-retirement --explicit-change-request "<quote DELIB-S421 full-sweep owner decision>" --change-reason "Mirror-retirement full cleanup sweep for <protected-target>" --approval-mode approve --changed-by <harness-id> --out .groundtruth/formal-artifact-approvals/<date>-<stable-artifact-id>.json --validate-after --json
```

The implementation may use `--stage` only after the protected target content and packet are final. If it does not use `--stage`, it must stage the packet and protected target together before running the evidence checker.

## Spec-Derived Verification Plan

| Requirement / spec | Verification command or evidence |
|---|---|
| `RETIRE-SPEC-HARNESS-STATE-ROLE-ASSIGNMENTS-001` file-absent assertion | `Test-Path harness-state/role-assignments.json` must return `False`. |
| `RETIRE-SPEC-HARNESS-STATE-ROLE-ASSIGNMENTS-001` no governed production-surface references | Run `rg` for `role-assignments.json`, `role_assignments_path(`, `ROLE_ASSIGNMENTS_RELATIVE_PATH`, `OPERATING_ROLE_RELATIVE_PATH`, and `ROLE_ASSIGNMENT_RECORD` over source, package source, governed TOML, governed rules markdown, `CLAUDE.md`, and `AGENTS.md`; it must return no matches except bridge/audit/packet contexts explicitly outside the production-surface assertion. |
| `DCL-HARNESS-STATE-SOT-ASSERTION-001` canonical projection read path | `python -m pytest platform_tests/scripts/test_mirror_retirement_role_assignments.py -q --tb=short` must pass. |
| Compatibility writer removal | Targeted tests in `platform_tests/scripts/test_harness_roles.py` and `platform_tests/scripts/test_mirror_retirement_role_assignments.py` must pass. |
| Workstream/startup fallback removal | Targeted tests in `platform_tests/hooks/test_workstream_focus.py` and `platform_tests/scripts/test_session_self_initialization.py` must pass. |
| Inventory canonical evidence | `python scripts/collect_dev_environment_inventory.py` must succeed and the generated inventory must contain no `role-assignments` reference. |
| `GOV-ARTIFACT-APPROVAL-001` and `DCL-ARTIFACT-APPROVAL-HOOK-001` narrative evidence | For every changed protected narrative target, a matching `.groundtruth/formal-artifact-approvals/*.json` packet must exist and `python scripts/check_narrative_artifact_evidence.py --paths <protected narrative paths>` must pass after staging target plus packet. If no protected narrative target changes, the post-implementation report must state that no narrative packet was required and cite the changed-path classification. |
| Bridge filing gates | `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-harness-state-sot-consolidation-phase-1-mirror-retirement` and `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-harness-state-sot-consolidation-phase-1-mirror-retirement` must pass with no blocking gaps before filing the post-implementation report. |
| Code quality baseline | `python -m ruff check <changed-py-files>`, `python -m ruff format --check <changed-py-files>`, and focused pytest commands above must pass before filing the post-implementation report. |

## Acceptance Criteria

1. `harness-state/role-assignments.json` is deleted.
2. No governed production surface listed above contains `role-assignments.json` or the legacy role-assignment helper names, except bridge/audit/packet contexts outside the production-surface assertion.
3. No active writer path can recreate `harness-state/role-assignments.json`.
4. Runtime role resolution continues to flow through `harness-state/harness-identities.json` plus `harness-state/harness-registry.json` via the canonical projection.
5. The regenerated dev-environment inventory references `harness-state/harness-registry.json`, not the retired mirror.
6. Every changed protected narrative target has a matching narrative-artifact approval packet, or the implementation report proves no protected narrative target changed.
7. Tests and code-quality checks in the spec-derived verification plan pass.

## Risk And Rollback

Risk: protected narrative packet generation creates commit friction if packet hashes do not match staged content. Mitigation: generate packets only after final target content is known, stage target plus packet together, and run `check_narrative_artifact_evidence.py --paths` before filing the report.

Risk: the full sweep touches many references, increasing merge and test surface. Mitigation: keep changes mechanical and scoped to replacing retired-mirror references with canonical registry/projection language, then run targeted startup/workstream/harness-role tests.

Risk: test fixtures that intentionally model old role-assignments input may be removed too aggressively. Mitigation: production-surface zero-match excludes `platform_tests/**`; fixture references may remain only when they explicitly test migration or absence semantics.

Rollback: revert the cleanup commit and restore `harness-state/role-assignments.json` from the parent commit if verification fails before merge. Because this revision avoids DB/spec mutation, rollback is filesystem-only except for generated narrative approval packets, which should be reverted with the protected narrative target if the implementation is rolled back.

## Pre-Filing Preflight Subsection

Candidate content must pass:

- `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-harness-state-sot-consolidation-phase-1-mirror-retirement --content-file <candidate>`
- `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-harness-state-sot-consolidation-phase-1-mirror-retirement --content-file <candidate>`

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
