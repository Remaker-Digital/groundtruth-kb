REVISED
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 2026-07-06T02-24-38Z-prime-builder-A-5e5b40
author_model: GPT-5.5 Codex
author_model_version: gpt-5.5
author_model_configuration: Codex dispatcher-spawned headless; resolved_role=prime-builder; approval_policy=never; sandbox=workspace-write; reasoning=xhigh
author_metadata_source: dispatcher-runtime-envelope

# Implementation Proposal - Phase 3 gap 09: evidence freshness and archival boundaries (REVISED)

bridge_kind: prime_proposal
Document: gtkb-wi4971-evidence-freshness-boundaries
Version: 003
Date: 2026-07-06 UTC
Responds to: bridge/gtkb-wi4971-evidence-freshness-boundaries-002.md (NO-GO)

Project Authorization: PAUTH-PROJECT-HARNESS-EQUIVALENCE-PHASE-3-WI4971-BATCH-C-20260705
Project: PROJECT-HARNESS-EQUIVALENCE-PHASE-3
Work Item: WI-4971

target_paths: ["config/governance/evidence-freshness-boundaries.toml", "scripts/evidence_freshness_boundary.py", "platform_tests/scripts/test_evidence_freshness_boundary.py", "independent-progress-assessments/CODEX-INSIGHT-DROPBOX/HARNESS-EQUIVALENCE-PHASE-3-EVIDENCE-FRESHNESS-*.md"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Revision Summary

This REVISED clears the Loyal Opposition NO-GO in `bridge/gtkb-wi4971-evidence-freshness-boundaries-002.md` by adding the missing canonical freshness and SoT read-discipline governance, defining the relationship between the proposed evidence-boundary config and the existing platform SoT registry, and adding a spec-derived verification row for state-claim freshness.

It also addresses the non-blocking WI-4966 cross-link by making the boundary explicit: WI-4966 owns query-output compactness and large-SoT default-output measurement; this WI-4971 slice owns evidence-reference freshness, archival-citation-only handling, and full-read justification classification.

## Summary

Define and implement evidence freshness and archival-boundary controls for routine harness-equivalence work. The implementation should distinguish compact/current reads from justified archival/full reads and show how archived transcript references can be cited without loading entire historical state into ordinary sessions.

The work item scope is limited to WI-4971. It does not authorize rewriting startup contracts, changing dispatcher routing, broad CLI compactness rewrites, SoT registry replacement, or bulk archive migration.

## Claim

Prime Builder proposes a bounded implementation slice for `WI-4971` that turns evidence freshness expectations into a small config-backed classifier and report.

## Requirement Sufficiency

Existing requirements are sufficient. `SPEC-INTAKE-46594e`, `DCL-SESSION-STARTUP-TOKEN-BUDGET-001`, `GOV-SESSION-SELF-INITIALIZATION-001`, `GOV-SOURCE-OF-TRUTH-FRESHNESS-001`, `GOV-PLATFORM-SOT-REGISTRY-001`, `DCL-SOT-READ-HOOK-CONTRACT-001`, and the Batch C PAUTH define the expected routine/archival boundary.

## In-Root Placement Evidence

All proposed target paths are inside `E:\GT-KB`: `config/governance/evidence-freshness-boundaries.toml`, `scripts/evidence_freshness_boundary.py`, `platform_tests/scripts/test_evidence_freshness_boundary.py`, and `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/HARNESS-EQUIVALENCE-PHASE-3-EVIDENCE-FRESHNESS-*.md`.

## Specification Links

- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - confirms implementation authority is project-bounded and evidence-backed.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - confirms PAUTH does not bypass bridge proposal review or later GO.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - preserves role-correct bridge status filing.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - requires PAUTH, project, work item, and target path metadata.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - requires concrete governing spec links before implementation review.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - requires implementation reports to map specs to executed verification.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` - governs current-state claims, stale/fresh classification, forbidden summary substitution, declared TTL exceptions, and the historical/audit-trail carve-out.
- `GOV-PLATFORM-SOT-REGISTRY-001` - makes `config/registry/sot-artifacts.toml` the platform-wide SoT artifact inventory; this WI must complement that registry rather than create a competing inventory.
- `DCL-SOT-READ-HOOK-CONTRACT-001` - governs harness-specific read-hook enforcement and the `forbidden_substitutes` discipline consumed from the SoT registry.
- `.claude/rules/sot-read-discipline.md` and `config/registry/sot-artifacts.toml` - narrative and config surfaces that operationalize the SoT read-discipline relationship this WI must preserve.
- `SPEC-INTAKE-46594e` - oversized base-session context and unbounded evidence loading are token-load risks.
- `DCL-SESSION-STARTUP-TOKEN-BUDGET-001` - requires bounded routine session context.
- `GOV-SESSION-SELF-INITIALIZATION-001` - governs what startup/self-initialization should load and cite.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - routes boundary decisions into durable config/evidence artifacts.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - keeps archival exceptions artifact-backed.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - classifies freshness gaps, waivers, supersession, and no-op coverage.

## Prior Deliberations

- `DELIB-202665197` - authorized Harness Equivalence Phase 3 child work; child implementation remains bridge-gated.
- `DELIB-20260705-HIGH-PRIORITY-QUEUE-CONTINUE` - owner-directed Batch C continuation authorization.
- `DELIB-202665119` - compact query and oversized SoT context for large read surfaces.
- `DELIB-202665127` - session/activity envelope sharding taxonomy and global baseline context.
- `bridge/gtkb-wi4966-cli-compactness-sot-size-controls-002.md` - sibling GO for WI-4966; query-output compactness is adjacent but distinct from this WI's evidence-reference freshness and archival justification scope.
- `bridge/gtkb-wi4971-evidence-freshness-archival-boundaries-002.md` - same-WI sibling GO with different target paths; this REVISED remains limited to the config-backed classifier/report paths listed in this proposal and does not claim those sibling target paths.

## Owner Decisions / Input

- `DELIB-20260705-HIGH-PRIORITY-QUEUE-CONTINUE` - owner approved Batch C continuation to governed disposition.
- `PAUTH-PROJECT-HARNESS-EQUIVALENCE-PHASE-3-WI4971-BATCH-C-20260705` - active authorization covering WI-4971.
- No fresh owner decision is required for this REVISED. The NO-GO fixes are additive specification linkage, relationship clarification, and verification-plan tightening.

## Proposed Scope

- Add a small config file describing evidence classes, routine freshness expectations, compact read defaults, archival read justification rules, citation-only patterns, and the relationship to the existing SoT registry/read-hook discipline.
- Add a helper that classifies evidence references as current, stale, archival-citation-only, full-read-justified, or missing.
- Emit a compact markdown report linking session/activity envelope sharding blockers B1-B7 as evidence inputs.
- Add focused tests for config parsing, freshness thresholds, archival/full read classification, citation-only references, state-claim freshness, SoT registry non-duplication, and report output.

## Relationship To Existing SoT Freshness / Read Discipline

`config/governance/evidence-freshness-boundaries.toml` complements, and must not duplicate or supersede, `config/registry/sot-artifacts.toml`. The SoT registry remains the platform-wide inventory of canonical source-of-truth classes, mutation APIs, canonical read paths, and forbidden substitutes under `GOV-PLATFORM-SOT-REGISTRY-001`.

The WI-4971 config is narrower: it classifies evidence references encountered during harness-equivalence review and verification work. It may point at SoT registry records or canonical readers when a reference makes a current-state claim, but it must not become a second inventory of SoT artifacts or a bypass around `forbidden_substitutes`.

The `current` and `stale` classifications defer to `GOV-SOURCE-OF-TRUTH-FRESHNESS-001`: state claims require fresh canonical reads and cannot be satisfied by compact summaries, copied excerpts, or paraphrases unless an explicit declared-TTL exception applies. A compact output may be a valid transport only when it is produced by the canonical reader for the current state being claimed.

The `archival-citation-only` classification aligns with the `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` historical/audit-trail carve-out: append-only history can be cited as history without loading full archived payloads into routine sessions. When a session needs to verify, dispute, or reproduce an archived claim, the `full-read-justified` class must require an explicit reason and stable citation rather than making full archival reads the default.

## Cross-Harness Disposition

The implementation is harness-neutral and exists to keep routine evidence loading comparable across harnesses. Any harness-specific archive gap must be reported as a typed waiver or follow-on work candidate, not papered over by loading full history by default.

This slice does not alter the existing SoT read hook or harness hook registration. If implementation discovers that a harness can satisfy a current-state claim only by reading a registered forbidden substitute, that is a gap to report, not an authorization to bypass the hook.

## Cross-Thread Boundary

WI-4966 and this WI-4971 proposal intentionally interlock without owning the same behavior. WI-4966 measures whether large SoT CLI/query surfaces have compact/current/actionable defaults. WI-4971 defines whether a specific evidence reference is fresh enough for the claim being made, whether it is merely an archival citation, or whether a full archival read is justified.

The same-WI sibling thread `gtkb-wi4971-evidence-freshness-archival-boundaries` has a GO on a broader runtime/test target set. This REVISED does not broaden this selected thread's target paths and does not authorize edits to that sibling's files. If both WI-4971 slices proceed, each implementation report must claim only its own target paths and must cross-reference the other slice where behavior overlaps.

## Specification-Derived Verification Plan

| Spec | Verification |
| --- | --- |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | Confirm implementation report cites the active WI-4971 PAUTH and stays within target paths. |
| `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` | Confirm no protected implementation starts before GO and implementation-start authorization. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Use `gt bridge show gtkb-wi4971-evidence-freshness-boundaries --json --compact` to confirm lifecycle state. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Run bridge applicability preflight and confirm project linkage metadata is present. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Run bridge applicability preflight and confirm `missing_required_specs: []`. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Run targeted tests and include exact command output in the implementation report. |
| `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` | Test that the classifier never treats a compact summary, copied excerpt, or paraphrase as sufficient for a current-state claim unless it is canonical-reader output or an explicit declared-TTL exception; test that archival citation-only references are separated from current-state claims. |
| `GOV-PLATFORM-SOT-REGISTRY-001` | Test/config-review that `evidence-freshness-boundaries.toml` declares itself as evidence-classification policy and does not duplicate or supersede `config/registry/sot-artifacts.toml`. |
| `DCL-SOT-READ-HOOK-CONTRACT-001` | Test/report evidence that current-state classifications route through canonical readers/SoT registry records and do not authorize reading registered `forbidden_substitutes`. |
| `SPEC-INTAKE-46594e` | Test that unbounded full-history reads are not routine defaults. |
| `DCL-SESSION-STARTUP-TOKEN-BUDGET-001` | Test that routine evidence classes resolve to compact/current reads unless explicitly justified. |
| `GOV-SESSION-SELF-INITIALIZATION-001` | Test startup-relevant evidence classes against freshness and citation-only expectations. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Confirm boundary rules are stored as governed config/evidence, not scratch notes. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Confirm archival exceptions carry durable evidence references. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Confirm stale, waiver, superseded, and no-op dispositions are separated. |

## Acceptance Criteria

- Config defines evidence classes, freshness expectations, compact defaults, archival/full read justifications, citation-only patterns, and the relationship to the SoT registry/read-hook discipline.
- The helper classifies sample evidence references without loading full historical state by default.
- The helper treats current-state claims as requiring fresh canonical reads, not compact summaries or paraphrases, unless a declared-TTL exception applies.
- The report links blocker families B1-B7 and names which boundary rule each one exercises.
- Tests cover config parsing, freshness classification, archival read justification, citation-only handling, SoT registry non-duplication, forbidden-substitute non-bypass, and markdown output.
- Implementation report cross-references WI-4966 and the same-WI sibling thread if either one's behavior is used as prior coverage.

## Findings Addressed

### Finding 1 [P1 - NO-GO blocker] - Canonical freshness governance absent from Specification Links

Resolution: Added `GOV-SOURCE-OF-TRUTH-FRESHNESS-001`, `GOV-PLATFORM-SOT-REGISTRY-001`, `DCL-SOT-READ-HOOK-CONTRACT-001`, `.claude/rules/sot-read-discipline.md`, and `config/registry/sot-artifacts.toml` to the governing linkage. Added the relationship subsection stating that the new WI-4971 config complements rather than supersedes the SoT registry, that current/stale classification defers to canonical freshness governance, and that archival-citation-only aligns with the historical/audit-trail carve-out.

Verification-plan change: Added rows for `GOV-SOURCE-OF-TRUTH-FRESHNESS-001`, `GOV-PLATFORM-SOT-REGISTRY-001`, and `DCL-SOT-READ-HOOK-CONTRACT-001`.

### Finding 2 [P3 - advisory, non-blocking] - Cross-link the nearest sibling gap (WI-4966)

Resolution: Added `bridge/gtkb-wi4966-cli-compactness-sot-size-controls-002.md` to Prior Deliberations and added a Cross-Thread Boundary section. The boundary states that WI-4966 owns compact query-output measurement, while WI-4971 owns evidence-reference freshness and archival/full-read justification.

Additional audit-trail cleanup: The same-WI sibling GO thread `gtkb-wi4971-evidence-freshness-archival-boundaries` is now cited explicitly so future implementers do not confuse this selected thread's narrower target paths with that sibling's broader runtime/test target paths.

## Pre-Filing Preflight Evidence

Candidate preflights were run against `.gtkb-state/bridge-revisions/drafts/gtkb-wi4971-evidence-freshness-boundaries-003.md` before live filing through `.codex/skills/bridge/helpers/revise_bridge.py file`.

### Applicability Preflight

- Command: `groundtruth-kb\.venv\Scripts\python.exe scripts\bridge_applicability_preflight.py --bridge-id gtkb-wi4971-evidence-freshness-boundaries --content-file .gtkb-state\bridge-revisions\drafts\gtkb-wi4971-evidence-freshness-boundaries-003.md --json`
- packet_hash: `sha256:598b8618db7eea9f9fda4bb7c1eeaecf01b093e1b4e52c39faa25723e812e36d`
- content_source: `pending_content`
- preflight_passed: `true`
- missing_required_specs: `[]`
- missing_advisory_specs: `[]`
- blocking specs matched: `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`, `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`, `GOV-FILE-BRIDGE-AUTHORITY-001`

### Clause Applicability Preflight

- Command: `groundtruth-kb\.venv\Scripts\python.exe scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-wi4971-evidence-freshness-boundaries --content-file .gtkb-state\bridge-revisions\drafts\gtkb-wi4971-evidence-freshness-boundaries-003.md`
- Clauses evaluated: `5`
- must_apply: `4`
- may_apply: `1`
- Evidence gaps in must_apply clauses: `0`
- Blocking gaps: `0`
- Exit: `0`

## Risks / Rollback

Risk is moderate because freshness boundaries can affect future startup and triage behavior. Mitigation is narrow config-backed classification, explicit SoT registry non-duplication, and no startup contract mutation in this slice.

Rollback is a revert of the config, helper, tests, and generated report. Bridge files and PAUTH records are append-only audit artifacts and must not be deleted.

## Files Expected To Change

- `config/governance/evidence-freshness-boundaries.toml`
- `scripts/evidence_freshness_boundary.py`
- `platform_tests/scripts/test_evidence_freshness_boundary.py`
- `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/HARNESS-EQUIVALENCE-PHASE-3-EVIDENCE-FRESHNESS-*.md`

## Recommended Commit Type

`feat`
