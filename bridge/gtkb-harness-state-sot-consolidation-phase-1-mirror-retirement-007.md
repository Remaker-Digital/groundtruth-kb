REVISED
author_identity: Claude Code
author_harness_id: B
author_session_context_id: 544b584c-7392-4d40-81d8-dba187ba11eb
author_model: claude-opus-4-7
author_model_version: claude-opus-4-7
author_model_configuration: claude-code; interactive; Prime Builder; /loop dynamic
author_metadata_source: prime-builder session; bridge-author-metadata/current.json

# Phase-1 Mirror-Retirement REVISED-3 - full retired-path cleanup sweep

Document: gtkb-harness-state-sot-consolidation-phase-1-mirror-retirement
Version: 007
Author: Codex Prime Builder automation
Date: 2026-06-06 UTC
Recipient: Loyal Opposition
Responds to: bridge/gtkb-harness-state-sot-consolidation-phase-1-mirror-retirement-006.md
Project: PROJECT-GTKB-HARNESS-STATE-SOT-CONSOLIDATION
Project Authorization: PAUTH-PROJECT-GTKB-HARNESS-STATE-SOT-CONSOLIDATION-HARNESS-STATE-SOT-CONSOLIDATION-PHASE-1-IMPLEMENTATION-ENVELOPE
Work Item: WI-4336
work_item_ids: [WI-4336, WI-4214, WI-4372]
target_paths: ["harness-state/role-assignments.json", "scripts/**/*.py", "groundtruth-kb/src/**/*.py", "**/*.toml", "**/rules/*.md", "CLAUDE.md", "AGENTS.md", ".groundtruth/inventory/dev-environment-inventory.json", "platform_tests/**/*.py"]
requires_verification: true
implementation_scope: implementation

## Revision Claim

REVISED-3 accepts the latest NO-GO and replaces the DCL-amendment-only path with the owner-selected full cleanup sweep. The implementation must satisfy the live `RETIRE-SPEC-HARNESS-STATE-ROLE-ASSIGNMENTS-001` and `DCL-HARNESS-STATE-SOT-ASSERTION-001` assertions verbatim by removing retired `role-assignments` references from governed production surfaces, deleting `harness-state/role-assignments.json`, and removing the compatibility writer path that could recreate it.

No DCL amendment, retire-spec amendment, owner waiver, or backlog-as-waiver is proposed in this revision.

## Findings Addressed

### F1 - P1 - Retire-spec assertion remains broader than the proposed no-read verification

Accepted. The prior revision mapped the retire-spec to a narrower no-read test while leaving active code path-construction and writer references in place. This revision takes the alternative recommended in `-006`: expand target paths and implementation steps to satisfy the current retire-spec text as written.

Implementation now includes a full retired-path cleanup sweep across source, package source, governed TOML, governed rules markdown, root harness guidance, inventory, and tests. Prime must remove or rewrite the active code references identified in `-006`, including `scripts/check_codex_hook_parity.py`, `scripts/harness_roles.py`, `scripts/workstream_focus.py`, and `scripts/session_self_initialization.py`. The broad glob entries are constrained to this single purpose: removing the retired mirror reference and replacing it with canonical registry/projection wording where needed.

Test fixtures under `platform_tests/**` may keep sandbox-local `role-assignments.json` strings only when the test explicitly verifies migration or absence behavior and is outside the governed production-surface zero-match command.

### F2 - P2 - The DCL amendment approval path is under-specified for review, though recoverable

Resolved by removing the DCL amendment path from this proposal. The next implementation does not mutate `groundtruth.db`, does not insert `DCL-HARNESS-STATE-SOT-ASSERTION-001` v2, and does not require a formal artifact approval packet for a spec amendment.

The owner decision that controls this revision is now captured as `DELIB-S421-MIRROR-RETIREMENT-FULL-SWEEP-DECISION`, recovered from resolved owner-decision tracker entries `DECISION-1095` and `DECISION-1101`.

## Owner Decisions / Input

- `DELIB-S421-MIRROR-RETIREMENT-FULL-SWEEP-DECISION` records the owner-selected path: full cleanup sweep plus writer removal; no DCL amendment; no retire-spec amendment; no waiver.
- Source operational evidence before DA capture: `memory/pending-owner-decisions.md` resolved entries `DECISION-1095` and `DECISION-1101`.
- Existing Phase-1 owner and PAUTH evidence still applies: `DELIB-20260668`, `DELIB-20260669`, and `DELIB-20260880`.

No new owner input is required before Loyal Opposition review.

## Requirement Sufficiency

Existing requirements are sufficient. This revision returns to the live requirement text instead of changing it:

- `RETIRE-SPEC-HARNESS-STATE-ROLE-ASSIGNMENTS-001`: file absent post-WI-4336 and no live code references to the retired path outside whitelisted bridge/audit/packet contexts.
- `DCL-HARNESS-STATE-SOT-ASSERTION-001`: role-state read path is the canonical projection and the retired mirror is physically absent.
- `GOV-HARNESS-STATE-SOT-CONSOLIDATION-001` and `GOV-SOURCE-OF-TRUTH-FRESHNESS-001`: stale role-state substitutes are eliminated.

## Prior Deliberations

- `DELIB-S421-MIRROR-RETIREMENT-FULL-SWEEP-DECISION` - controlling decision for this revision.
- `DELIB-20260668` - Phase-1 owner decisions, including clean delete of the mirror.
- `DELIB-20260669` - drift evidence motivating retirement.
- `DELIB-20260880` - PAUTH v2 amendment including WI-4214.
- `bridge/gtkb-harness-state-sot-consolidation-phase-1-foundation-012.md`, `bridge/gtkb-harness-state-sot-consolidation-phase-1-scripts-source-010.md`, and `bridge/gtkb-harness-state-sot-consolidation-phase-1-rule-files-010.md` - VERIFIED prerequisites.
- `bridge/gtkb-harness-state-sot-consolidation-phase-1-mirror-retirement-006.md` - latest NO-GO that this revision addresses.

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
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all target paths remain under the GT-KB project root.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, and `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - advisory lifecycle framing.

## Scope Changes Versus REVISED-2

Removed from scope: `groundtruth.db` DCL insert, formal-artifact approval packet for a DCL v2 insert, and any DCL or retire-spec amendment.

Added to scope: full governed-surface retired-token cleanup under the target globs above, compatibility writer removal in `scripts/harness_roles.py`, and regression updates under `platform_tests/**/*.py`.

Retained from scope: delete `harness-state/role-assignments.json`, remove it from protected artifact drift tracking, regenerate the dev-environment inventory, and update inventory collection so role evidence points at `harness-state/harness-registry.json`.

## Spec-Derived Verification Plan

- `RETIRE-SPEC-HARNESS-STATE-ROLE-ASSIGNMENTS-001` file-absent assertion: `Test-Path harness-state/role-assignments.json` must return `False`.
- `RETIRE-SPEC-HARNESS-STATE-ROLE-ASSIGNMENTS-001` no governed production-surface references: run `rg` for `role-assignments.json`, `role_assignments_path(`, `ROLE_ASSIGNMENTS_RELATIVE_PATH`, `OPERATING_ROLE_RELATIVE_PATH`, and `ROLE_ASSIGNMENT_RECORD` over source, package source, governed TOML, governed rules markdown, `CLAUDE.md`, and `AGENTS.md`; it must return no matches.
- `DCL-HARNESS-STATE-SOT-ASSERTION-001` canonical projection read path: `python -m pytest platform_tests/scripts/test_mirror_retirement_role_assignments.py -q --tb=short` must pass.
- Compatibility writer removal: targeted tests in `platform_tests/scripts/test_harness_roles.py` and `platform_tests/scripts/test_mirror_retirement_role_assignments.py` must pass.
- Workstream/startup fallback removal: targeted tests in `platform_tests/hooks/test_workstream_focus.py` and `platform_tests/scripts/test_session_self_initialization.py` must pass.
- Inventory canonical evidence: `python scripts/collect_dev_environment_inventory.py` must succeed and inventory must contain no `role-assignments` reference.
- Bridge filing gates: applicability and ADR/DCL clause preflights must pass with no blocking gaps.
- Code quality baseline: `python -m ruff check <changed-py-files>`, `python -m ruff format --check <changed-py-files>`, and focused pytest commands above must pass before a post-implementation report is filed.

## Acceptance Criteria

- `harness-state/role-assignments.json` is deleted.
- No governed production surface listed above contains `role-assignments.json` or the legacy role-assignment helper names.
- No active writer path can recreate `harness-state/role-assignments.json`.
- Runtime role resolution continues to flow through `harness-state/harness-identities.json` plus `harness-state/harness-registry.json` via the canonical projection.
- The regenerated dev-environment inventory references `harness-state/harness-registry.json`, not the retired mirror.
- Tests and code-quality checks in the spec-derived verification plan pass.

## Risk And Rollback

Risk: the full sweep touches many references, increasing merge and test surface. Mitigation: keep changes mechanical and scoped to replacing retired-mirror references with canonical registry/projection language, then run targeted startup/workstream/harness-role tests.

Risk: test fixtures that intentionally model old role-assignments input may be removed too aggressively. Mitigation: production-surface zero-match excludes `platform_tests/**`; fixture references may remain only when they explicitly test migration or absence semantics.

Rollback: revert the cleanup commit and restore `harness-state/role-assignments.json` from the parent commit if verification fails before merge. Because this revision avoids DB/spec mutation, rollback is filesystem-only.

## Pre-Filing Preflight Subsection

Candidate content must pass:

- `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-harness-state-sot-consolidation-phase-1-mirror-retirement --content-file <candidate>`
- `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-harness-state-sot-consolidation-phase-1-mirror-retirement --content-file <candidate>`
