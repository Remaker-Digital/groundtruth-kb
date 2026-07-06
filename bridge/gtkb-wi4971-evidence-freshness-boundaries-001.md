NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f3170-d706-77d3-b3e1-be39d47f3eda
author_model: GPT-5 Codex
author_model_version: gpt-5
author_model_configuration: interactive Prime Builder session; default Codex desktop execution
author_metadata_source: codex-explicit-runtime-envelope

# Implementation Proposal - Phase 3 gap 09: evidence freshness and archival boundaries

bridge_kind: prime_proposal
Document: gtkb-wi4971-evidence-freshness-boundaries
Version: 001
Date: 2026-07-06 UTC

Project Authorization: PAUTH-PROJECT-HARNESS-EQUIVALENCE-PHASE-3-WI4971-BATCH-C-20260705
Project: PROJECT-HARNESS-EQUIVALENCE-PHASE-3
Work Item: WI-4971

target_paths: ["config/governance/evidence-freshness-boundaries.toml", "scripts/evidence_freshness_boundary.py", "platform_tests/scripts/test_evidence_freshness_boundary.py", "independent-progress-assessments/CODEX-INSIGHT-DROPBOX/HARNESS-EQUIVALENCE-PHASE-3-EVIDENCE-FRESHNESS-*.md"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

Define and implement evidence freshness and archival-boundary controls for routine harness-equivalence work. The implementation should distinguish compact/current reads from justified archival/full reads and show how archived transcript references can be cited without loading entire historical state into ordinary sessions.

The work item scope is limited to WI-4971. It does not authorize rewriting startup contracts, changing dispatcher routing, or bulk archive migration.

## Claim

Prime Builder proposes a bounded implementation slice for `WI-4971` that turns evidence freshness expectations into a small config-backed classifier and report.

## Requirement Sufficiency

Existing requirements are sufficient. `SPEC-INTAKE-46594e`, `DCL-SESSION-STARTUP-TOKEN-BUDGET-001`, `GOV-SESSION-SELF-INITIALIZATION-001`, and the Batch C PAUTH define the expected routine/archival boundary.

## In-Root Placement Evidence

All proposed target paths are inside `E:\GT-KB`: `config/governance/evidence-freshness-boundaries.toml`, `scripts/evidence_freshness_boundary.py`, `platform_tests/scripts/test_evidence_freshness_boundary.py`, and `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/HARNESS-EQUIVALENCE-PHASE-3-EVIDENCE-FRESHNESS-*.md`.

## Specification Links

- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - confirms implementation authority is project-bounded and evidence-backed.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - confirms PAUTH does not bypass bridge proposal review or later GO.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - preserves role-correct bridge status filing.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - requires PAUTH, project, work item, and target path metadata.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - requires concrete governing spec links before implementation review.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - requires implementation reports to map specs to executed verification.
- `SPEC-INTAKE-46594e` - oversized base-session context and unbounded evidence loading are token-load risks.
- `DCL-SESSION-STARTUP-TOKEN-BUDGET-001` - requires bounded routine session context.
- `GOV-SESSION-SELF-INITIALIZATION-001` - governs what startup/self-initialization should load and cite.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - routes boundary decisions into durable config/evidence artifacts.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - keeps archival exceptions artifact-backed.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - classifies freshness gaps, waivers, supersession, and no-op coverage.

## Prior Deliberations

- `DELIB-202665197` - authorized Harness Equivalence Phase 3 child work.
- `DELIB-20260705-HIGH-PRIORITY-QUEUE-CONTINUE` - owner-directed Batch C continuation authorization.
- `DELIB-202665119` - compact query and oversized SoT context.
- `DELIB-202665127` - session/activity envelope sharding taxonomy and global baseline context.
- `DELIB-20260701-ENVELOPE-SHARDING-EXECUTE-RETIRE` - B1-B7 blocker context and envelope-sharding closure.

## Owner Decisions / Input

- `DELIB-20260705-HIGH-PRIORITY-QUEUE-CONTINUE` - owner approved Batch C continuation.
- `PAUTH-PROJECT-HARNESS-EQUIVALENCE-PHASE-3-WI4971-BATCH-C-20260705` - active authorization covering WI-4971.

## Proposed Scope

- Add a small config file describing evidence classes, routine freshness expectations, compact read defaults, archival read justification rules, and citation-only patterns.
- Add a helper that classifies evidence references as current, stale, archival-citation-only, full-read-justified, or missing.
- Emit a compact markdown report linking session/activity envelope sharding blockers B1-B7 as evidence inputs.
- Add focused tests for config parsing, freshness thresholds, archival/full read classification, citation-only references, and report output.

## Cross-Harness Disposition

The implementation is harness-neutral and exists to keep routine evidence loading comparable across harnesses. Any harness-specific archive gap must be reported as a typed waiver or follow-on work candidate, not papered over by loading full history by default.

## Specification-Derived Verification Plan

| Spec | Verification |
| --- | --- |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | Confirm implementation report cites the active WI-4971 PAUTH and stays within target paths. |
| `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` | Confirm no protected implementation starts before GO. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Use `gt bridge show gtkb-wi4971-evidence-freshness-boundaries --json --compact` to confirm lifecycle state. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Run bridge applicability preflight and confirm project linkage metadata is present. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Run bridge applicability preflight and confirm `missing_required_specs: []`. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Run targeted tests and include exact command output in the implementation report. |
| `SPEC-INTAKE-46594e` | Test that unbounded full-history reads are not routine defaults. |
| `DCL-SESSION-STARTUP-TOKEN-BUDGET-001` | Test that routine evidence classes resolve to compact/current reads unless explicitly justified. |
| `GOV-SESSION-SELF-INITIALIZATION-001` | Test startup-relevant evidence classes against freshness and citation-only expectations. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Confirm boundary rules are stored as governed config/evidence, not scratch notes. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Confirm archival exceptions carry durable evidence references. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Confirm stale, waiver, superseded, and no-op dispositions are separated. |

## Acceptance Criteria

- Config defines evidence classes, freshness expectations, compact defaults, archival/full read justifications, and citation-only patterns.
- The helper classifies sample evidence references without loading full historical state by default.
- The report links blocker families B1-B7 and names which boundary rule each one exercises.
- Tests cover config parsing, freshness classification, archival read justification, citation-only handling, and markdown output.

## Risks / Rollback

Risk is moderate because freshness boundaries can affect future startup and triage behavior. Mitigation is narrow config-backed classification and no startup contract mutation in this slice.

Rollback is a revert of the config, helper, tests, and generated report. Bridge files and PAUTH records are append-only audit artifacts and must not be deleted.

## Files Expected To Change

- `config/governance/evidence-freshness-boundaries.toml`
- `scripts/evidence_freshness_boundary.py`
- `platform_tests/scripts/test_evidence_freshness_boundary.py`
- `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/HARNESS-EQUIVALENCE-PHASE-3-EVIDENCE-FRESHNESS-*.md`

## Recommended Commit Type

`feat`
