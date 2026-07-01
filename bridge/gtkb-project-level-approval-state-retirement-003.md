REVISED
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 2026-06-30T20-14-29Z-prime-builder-A-c0de5a
author_model: GPT-5
author_model_version: GPT-5 Codex desktop runtime, 2026-06-30
author_model_configuration: Codex desktop heartbeat session; sandbox=danger-full-access; approval_policy=never; role=Prime Builder

# Implementation Proposal - Retire individual work-item approval-state authority

bridge_kind: prime_proposal
Document: gtkb-project-level-approval-state-retirement
Version: 003
Responds to: bridge/gtkb-project-level-approval-state-retirement-002.md
Date: 2026-06-30 UTC

Project Authorization: PAUTH-PROJECT-GTKB-OBSOLETE-REFERENCE-PURGE-PROJECT-LEVEL-APPROVAL-STATE-RETIREMENT-2026-06-30
Project: PROJECT-GTKB-OBSOLETE-REFERENCE-PURGE
Work Item: WI-4936

target_paths: ["groundtruth.db", ".claude/rules/backlog-approval-state.md", ".claude/rules/codex-standing-priorities.md", ".claude/skills/kb-batch/SKILL.md", ".codex/skills/kb-batch/SKILL.md", "AGENTS.md", "CLAUDE.md", "scripts/session_self_initialization.py", "scripts/backfill_approval_state.py", "scripts/backlog_approval_gate.py", "scripts/benchmarks/backlog_triage.py", "scripts/hygiene/advisory_candidate_promote.py", "scripts/hygiene/router_corpus_dispose.py", "groundtruth-kb/src/groundtruth_kb/backlog.py", "groundtruth-kb/src/groundtruth_kb/backlog/approval_state.py", "groundtruth-kb/src/groundtruth_kb/backlog/__init__.py", "groundtruth-kb/src/groundtruth_kb/cli_backlog_update.py", "groundtruth-kb/src/groundtruth_kb/project/doctor.py", "platform_tests/cli/test_backlog_update_title_desc.py", "platform_tests/governance/__init__.py", "platform_tests/scripts/test_advisory_candidate_promote.py", "platform_tests/scripts/test_backlog_triage_benchmark.py", "platform_tests/scripts/test_fab18_backlog_dignity.py", "platform_tests/scripts/test_router_corpus_dispose.py", "platform_tests/scripts/test_session_self_initialization.py", "platform_tests/scripts/test_session_self_initialization_disclosure_shape.py", "platform_tests/scripts/test_project_authorization.py", "platform_tests/scripts/test_implementation_authorization.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

Remove current load-bearing reliance on individual work-item approval states so project-level authorization is the only approval scope while preserving bridge GO and implementation-start gates.

Work item description: Remove live/load-bearing GT-KB reliance on individual work-item approval state and WI-specific approval semantics. Project authorization is the approval unit: an approved parent project authorizes its active member work items, while bridge GO, implementation-start packet, target-path scope, spec-derived verification, implementation report, and Loyal Opposition verification remain mandatory. Retire or neutralize directives, skills, instructions, helpers, startup surfaces, doctor/triage logic, and tests that treat work_items.approval_state or per-WI approval as implementation authority. Preserve historical bridge and audit records as non-authoritative history. Related authority: DELIB-20260630-PROJECT-LEVEL-WI-APPROVAL-RETIREMENT; DELIB-S347-PROJECT-SCOPED-IMPLEMENTATION-AUTHORIZATION; GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001; SPEC-PROJECT-FIT-AUTO-ATTACHMENT-001; bridge/gtkb-project-scoped-implementation-authorization-010.md; supersedes current-authority use of bridge/gtkb-backlog-approval-state-taxonomy-slice-1-011.md.

## Claim

Prime Builder proposes a bounded implementation slice for `WI-4936` and keeps the bridge, project authorization, owner-decision, and verification gates intact.

## Revision Claim

This REVISED entry makes no implementation-scope, target-path, requirement, acceptance, or verification-plan change from `bridge/gtkb-project-level-approval-state-retirement-001.md`.

The prior `GO` at `bridge/gtkb-project-level-approval-state-retirement-002.md` is non-operative for implementation-start authorization because `scripts/implementation_authorization.py begin --bridge-id gtkb-project-level-approval-state-retirement` refused it with `author_session_context_missing`: the GO verdict lacks machine-readable `author_session_context_id` metadata. Prime Builder did not modify implementation files. This revision reopens Loyal Opposition review so an independent Loyal Opposition session can issue a metadata-complete verdict.

## Requirement Sufficiency

Existing requirements are sufficient for filing this proposal. The work item and active project authorization define the implementation boundary; any missing membership or PAUTH state is created only when explicit owner-decision evidence is supplied.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `groundtruth.db`, `.claude/rules/backlog-approval-state.md`, `.claude/rules/codex-standing-priorities.md`, `.claude/skills/kb-batch/SKILL.md`, `.codex/skills/kb-batch/SKILL.md`, `AGENTS.md`, `CLAUDE.md`, `scripts/session_self_initialization.py`, `scripts/backfill_approval_state.py`, `scripts/backlog_approval_gate.py`, `scripts/benchmarks/backlog_triage.py`, `scripts/hygiene/advisory_candidate_promote.py`, `scripts/hygiene/router_corpus_dispose.py`, `groundtruth-kb/src/groundtruth_kb/backlog.py`, `groundtruth-kb/src/groundtruth_kb/backlog/approval_state.py`, `groundtruth-kb/src/groundtruth_kb/backlog/__init__.py`, `groundtruth-kb/src/groundtruth_kb/cli_backlog_update.py`, `groundtruth-kb/src/groundtruth_kb/project/doctor.py`, `platform_tests/cli/test_backlog_update_title_desc.py`, `platform_tests/governance/__init__.py`, `platform_tests/scripts/test_advisory_candidate_promote.py`, `platform_tests/scripts/test_backlog_triage_benchmark.py`, `platform_tests/scripts/test_fab18_backlog_dignity.py`, `platform_tests/scripts/test_router_corpus_dispose.py`, `platform_tests/scripts/test_session_self_initialization.py`, `platform_tests/scripts/test_session_self_initialization_disclosure_shape.py`, `platform_tests/scripts/test_project_authorization.py`, `platform_tests/scripts/test_implementation_authorization.py`.

## Specification Links

- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - governs bounded project implementation authority.
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
- `SPEC-PROJECT-FIT-AUTO-ATTACHMENT-001` - auto-linked governing or work-item specification.
- `ADR-OBSOLETE-REFERENCE-PURGE-OBLIGATION-001` - auto-linked governing or work-item specification.
- `DCL-OBSOLETE-REFERENCE-PURGE-PAIRING-001` - auto-linked governing or work-item specification.
- `SPEC-ENVELOPE-DISCLOSURE-UI-001` - auto-linked governing or work-item specification.

## Prior Deliberations

- `DELIB-20260630-PROJECT-LEVEL-WI-APPROVAL-RETIREMENT` - Project-level approval supersedes individual work-item approval state
- `DELIB-20266267` - Bounded implementation authorization: governance/bridge reliability hardening (WI-4457, WI-4458, WI-4871)
- `DELIB-20266085` - Owner decision: PROJECT-GTKB-ADOPTER-EXPERIENCE retirement disposition (resolve 5 VERIFIED + implement WI-3352)
- `DELIB-20266596` - Approve PROJECT-GTKB-SKILL-ACTIVATION-ENFORCEMENT continuation and skill scaffold WIs
- `DELIB-20265963` - WI-4750 implementation report â€” auto-retire verify-helper parity regression

## Owner Decisions / Input

- `DELIB-20260630-PROJECT-LEVEL-WI-APPROVAL-RETIREMENT` - owner-decision evidence supplied to this command.
- `PAUTH-PROJECT-GTKB-OBSOLETE-REFERENCE-PURGE-PROJECT-LEVEL-APPROVAL-STATE-RETIREMENT-2026-06-30` - active project authorization covering `WI-4936`.

## Proposed Scope

- Update current directives/rules/skills/startup/doctor/backlog helpers so project authorization is approval source and work-item approval_state is not implementation authority.
- Remove or deprecate legacy approval_state helper scripts/modules/tests, preserving historical audit evidence and compatibility shims that do not drive authority.
- Update or supersede conflicting formal/spec language, especially SPEC-ENVELOPE-DISCLOSURE-UI-001 top-priority approval_state filtering, through governed formal-artifact evidence before relying on changed behavior.
- Use deterministic inventory scans plus focused tests to prove no current load-bearing artifact treats individual work items as separately approved.

## Specification-Derived Verification Plan

| Spec | Verification |
| --- | --- |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | Focused tests cover PAUTH with empty included_work_item_ids authorizing active project-member work items without consulting approval_state. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `SPEC-AUQ-POLICY-ENGINE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `GOV-STANDING-BACKLOG-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `SPEC-PROJECT-FIT-AUTO-ATTACHMENT-001` | Project membership/attachment tests prove active project fit is the work-item scope source. |
| `ADR-OBSOLETE-REFERENCE-PURGE-OBLIGATION-001` | Inventory scan and rg evidence show obsolete approval-state authority removed from load-bearing directives, skills, helpers, and tests or explicitly quarantined as historical. |
| `DCL-OBSOLETE-REFERENCE-PURGE-PAIRING-001` | A deterministic obsolete-reference purge check/ledger captures any remaining approval_state references and classifies them KEEP historical/compatibility or STRIP. |
| `SPEC-ENVELOPE-DISCLOSURE-UI-001` | Startup disclosure tests are updated so Top-3 no longer requires approval_state=implementation_authorized. |

## Cross-Harness Disposition

- Universal applicability: project-level-only approval semantics apply to all active GT-KB harnesses and must not diverge by vendor or role surface.
- Claude and Codex skill-doc target paths are both in scope (`.claude/skills/kb-batch/SKILL.md`, `.codex/skills/kb-batch/SKILL.md`); implementation must update them equivalently or remove obsolete approval wording from both. No typed waiver is requested.
- Cursor, Antigravity, Ollama, and OpenRouter have no directly targeted skill-doc files in this proposal, but any load-bearing instruction/helper surface discovered there during the deterministic scan must either be added through a bridge revision before mutation or classified as historical/non-authoritative evidence. No silent harness-specific exception is allowed.
- Verification must include focused parity/string evidence showing retained current surfaces cite project authorization rather than individual work-item approval state as implementation authority.

## Acceptance Criteria
- Active project-level PAUTH with empty included_work_item_ids plus active project membership is sufficient approval evidence for project member work items; no load-bearing surface blocks on work_items.approval_state.
- Startup Top-3/project priority selection no longer filters on approval_state and instead uses project authorization/membership plus non-terminal status.
- Old WI-3271 approval-state taxonomy is clearly historical/superseded outside append-only bridge/audit history.
- Bridge GO, implementation-start packet, target_paths, spec-derived tests, implementation report, and LO verification remain mandatory.

## Risks / Rollback

Risk is moderate because implementation proposals authorize later protected-file work. The service must fail closed around owner-decision evidence, target paths, bridge slug collisions, author metadata, and preflight failures.

Rollback is a revert of the source and test changes. Bridge files and project authorization records are append-only audit artifacts and must not be deleted by rollback.

## Files Expected To Change

- `groundtruth.db`
- `.claude/rules/backlog-approval-state.md`
- `.claude/rules/codex-standing-priorities.md`
- `.claude/skills/kb-batch/SKILL.md`
- `.codex/skills/kb-batch/SKILL.md`
- `AGENTS.md`
- `CLAUDE.md`
- `scripts/session_self_initialization.py`
- `scripts/backfill_approval_state.py`
- `scripts/backlog_approval_gate.py`
- `scripts/benchmarks/backlog_triage.py`
- `scripts/hygiene/advisory_candidate_promote.py`
- `scripts/hygiene/router_corpus_dispose.py`
- `groundtruth-kb/src/groundtruth_kb/backlog.py`
- `groundtruth-kb/src/groundtruth_kb/backlog/approval_state.py`
- `groundtruth-kb/src/groundtruth_kb/backlog/__init__.py`
- `groundtruth-kb/src/groundtruth_kb/cli_backlog_update.py`
- `groundtruth-kb/src/groundtruth_kb/project/doctor.py`
- `platform_tests/cli/test_backlog_update_title_desc.py`
- `platform_tests/governance/__init__.py`
- `platform_tests/scripts/test_advisory_candidate_promote.py`
- `platform_tests/scripts/test_backlog_triage_benchmark.py`
- `platform_tests/scripts/test_fab18_backlog_dignity.py`
- `platform_tests/scripts/test_router_corpus_dispose.py`
- `platform_tests/scripts/test_session_self_initialization.py`
- `platform_tests/scripts/test_session_self_initialization_disclosure_shape.py`
- `platform_tests/scripts/test_project_authorization.py`
- `platform_tests/scripts/test_implementation_authorization.py`

## Recommended Commit Type

`feat`
