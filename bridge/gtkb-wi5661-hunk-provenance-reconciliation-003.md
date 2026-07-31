REVISED
::init gtkb pb
::open build
author_identity: codex
author_harness_id: A
author_session_context_id: A-2026-07-24T16-22-28Z
author_model: gpt-5
author_model_version: gpt-5
author_model_configuration: reasoning_effort=default;thread_source=codex-desktop
author_metadata_source: x-codex-turn-metadata

# Hunk Provenance Reconciliation for WI-5661 Live-Break Recovery

bridge_kind: prime_proposal
Document: gtkb-wi5661-hunk-provenance-reconciliation
Version: 003
Responds to: bridge/gtkb-wi5661-hunk-provenance-reconciliation-002.md
Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-WI5661-SKILL-RENAME-LIVE-BREAK-20260724
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-5661
target_paths: ["groundtruth-kb/docs/reports/wi5661-hunk-provenance-evidence.md"]
implementation_scope: governance_evidence_only
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Revision Claim

This revision is an observation-only prerequisite for the WI-5661 recovery. If approved, it authorizes only one additive, durable evidence report at `groundtruth-kb/docs/reports/wi5661-hunk-provenance-evidence.md`. It does not authorize modification, staging, attribution, rollback, reformatting, or commit of any source, hook, configuration, or test path observed by the report.

The report will identify each observed path, current diff fingerprint/hunk count, current claim state, known owner or bridge disposition, and the precise clean-baseline or owner-attribution predicate that must be met before a separate WI-5661 source proposal can request GO.

## Requirement Sufficiency

Existing requirements sufficient. The recorded owner directive, WI-5661 description, active project authorization, and NO-GO findings fully bound this evidence-only prerequisite. A separate source proposal is required before any live-break implementation.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - preserves the numbered bridge chain and blocks source implementation without a separate GO.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - records foreign-hunk ownership and disposition as a durable artifact instead of tacitly absorbing it.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - binds this revised proposal to its governing constraints and exact target.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - requires read-only evidence commands and independent report review before any terminal conclusion.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - supplies project, authorization, work item, and exact target metadata.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - retains a traceable evidence artifact for recovery ownership.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - makes the prerequisite state explicit and non-terminal.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - keeps the evidence report in the GT-KB root, outside an adopter application.

## Prior Deliberations

_No additional Deliberation Archive record is relied on. The prior bridge chain and the owner directive recorded on WI-5661 are the relevant durable scope evidence for this narrow reconciliation._

## Owner Decisions / Input

- Owner directive recorded in `WI-5661.source_owner_directive`: “2026-07-24 owner AUQ: fix WI-5651 live breaks first as a fast-lane slice, then a project for the rest.”
- `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-WI5661-SKILL-RENAME-LIVE-BREAK-20260724` bounds this prerequisite to WI-5661; it does not authorize the observed source files.

## Findings Addressed

### P1 - Observation-only claim conflicted with source implementation authority

Response: `target_paths` contains only the new additive evidence report. `implementation_scope` is `governance_evidence_only`. All source/test/configuration paths are listed below solely as read-only observed evidence.

### P1 - Live-break inventory was both overbroad and incomplete

Response: the evidence report must enumerate the complete observed live-break inventory, including `scripts/verify_antigravity_dispatch.py`, without making any observed path an implementation target. A later source proposal must be independently complete and separately reviewed.

## Read-Only Observed Evidence

The following paths are evidence only and are expressly excluded from `target_paths` and Files Expected To Change:

- `bridge/gtkb-wi5661-skill-rename-live-breaks-003.md`
- `bridge/gtkb-wi5661-skill-rename-live-breaks-004.md`
- `.claude/hooks/bridge-axis-2-surface.py`
- `config/hooks/gtkb-bridge-axis-2-surface.py`
- `scripts/gtkb_bridge_writer.py`
- `scripts/harness_parity_phase2.py`
- `scripts/per_thread_finalization_repair.py`
- `scripts/verify_antigravity_dispatch.py`
- `platform_tests/scripts/test_gtkb_bridge_writer.py`

## Pre-Filing Preflight Subsection

- `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5661-hunk-provenance-reconciliation --content-file .gtkb-state/bridge-revisions/drafts/gtkb-wi5661-hunk-provenance-reconciliation-003.md --json` must pass with no missing required specification.
- `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi5661-hunk-provenance-reconciliation --content-file .gtkb-state/bridge-revisions/drafts/gtkb-wi5661-hunk-provenance-reconciliation-003.md` must exit 0 with no blocking gap.

## Specification-Derived Verification Plan

| Spec / governing surface | Read-only verification | Expected result |
| --- | --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `gt bridge show gtkb-wi5661-hunk-provenance-reconciliation --json`; `python scripts/bridge_claim_cli.py status gtkb-wi5661-terminal-verdict-recovery` | Reconciliation target remains evidence-only; recovery thread and claim states are recorded without mutation. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Applicability preflight against this content file | No missing required specification and only the additive report declared. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `git diff --numstat -- <each observed path>` and `git diff --check -- <each observed path>` | Exact observed hunk/byte evidence is captured; no source path is written. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` and `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Inspect report content and commit scope | One durable report names ownership/disposition and no foreign source path is staged. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | LO review of the implementation report | NO-GO/VERIFIED is based on the evidence artifact only; it does not constitute source recovery approval. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `git diff --name-only -- groundtruth-kb/docs/reports/wi5661-hunk-provenance-evidence.md` | Additive report stays in-root and outside `applications/`. |

## Acceptance Criteria

- The only written and staged implementation artifact is `groundtruth-kb/docs/reports/wi5661-hunk-provenance-evidence.md`.
- The report records the nine read-only observed paths, their hunk/fingerprint state, bridge/claim ownership facts, and a separate-GO prerequisite for any source recovery.
- No observed source/test/configuration path is modified, staged, committed, attributed, or placed in rollback scope.
- The report is independently reviewed before it is treated as evidence for a future WI-5661 source proposal.

## Risks And Rollback

Risk: an evidence report could be mistaken for source-recovery authority. The report will state that a future source change requires a separate proposal, exact target set, fresh GO, authorization packet, and commit-finalization evidence.

Rollback: revert only the additive evidence report if its recorded facts are incorrect. The observed source/test/configuration paths are not this proposal's changes and are never rollback targets.

## Files Expected To Change

- `groundtruth-kb/docs/reports/wi5661-hunk-provenance-evidence.md`

## Recommended Commit Type

`docs`
