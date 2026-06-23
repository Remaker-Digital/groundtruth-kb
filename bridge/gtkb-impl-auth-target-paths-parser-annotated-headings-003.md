REVISED
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019ef047-d4a9-7993-8217-7bb8a6745c97
author_model: GPT-5 Codex
author_model_version: gpt-5-codex
author_model_configuration: Codex automation auto-builder; owner-declared Prime Builder; approval_policy=never; workspace=E:\GT-KB
author_metadata_source: explicit automation metadata

# Revised Proposal - impl-auth target_paths parser annotated heading handling

bridge_kind: prime_proposal
Document: gtkb-impl-auth-target-paths-parser-annotated-headings
Version: 003 (REVISED)
Date: 2026-06-22 UTC
Responds to: bridge/gtkb-impl-auth-target-paths-parser-annotated-headings-002.md

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-3499

target_paths: ["scripts/implementation_authorization.py", "platform_tests/scripts/test_implementation_authorization.py"]

## Revision Claim

This revision preserves the WI-3499 defect-fix goal but corrects the algorithm and verification plan rejected in `bridge/gtkb-impl-auth-target-paths-parser-annotated-headings-002.md`. The implementation-start authorization parser should accept a valid annotated `## target_paths (...)` proposal section while never reading bullets from nested `###` subsections as authorized paths. The revised approach adds a target-paths-specific section reader that matches the canonical `target_paths` heading with a bounded annotation suffix and returns text only until the next markdown heading at any level.

The change remains source-and-test only. It does not alter bridge lifecycle state, work-intent claims, project authorization, owner-decision routing, or `section_body()` exact-match semantics for the other parser consumers.

## In-Root Placement Evidence

All live files and generated artifacts for this proposal remain under `E:\GT-KB`. The implementation targets are `E:\GT-KB\scripts\implementation_authorization.py` and `E:\GT-KB\platform_tests\scripts\test_implementation_authorization.py`. The versioned bridge revision will be filed as `E:\GT-KB\bridge\gtkb-impl-auth-target-paths-parser-annotated-headings-003.md`.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - implementation-start authorization must derive from the live latest `GO` bridge proposal and its concrete target paths; this fix keeps a valid proposal artifact parseable by `implementation_authorization.py begin`.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - target paths remain artifact-backed proposal data, not an out-of-band workaround added after review.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this revised proposal cites the governing specifications constraining the implementation.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the verification plan maps each linked requirement to an executed regression test.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - project authorization, project, and work item metadata are present in machine-readable header lines.
- `SPEC-AUQ-POLICY-ENGINE-001` - boundary citation: this is a parser-only implementation authorization fix and does not add or change owner-decision policy behavior.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all target paths remain in-root GT-KB platform paths; no adopter/application boundary is crossed.
- `GOV-STANDING-BACKLOG-001` - WI-3499 is an open MemBase work item in `PROJECT-GTKB-RELIABILITY-FIXES`.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - the implementation authorization helper is harness-neutral; no Claude/Codex hook parity surface is altered.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - authorization continues to be derived from durable bridge artifact content.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - the touched parser behavior receives explicit regression coverage at the lifecycle boundary where a GO'd proposal becomes an implementation-start packet.

## Prior Deliberations

- `DELIB-20265457` - owner AUQ authorizing the PROJECT-GTKB-RELIABILITY-FIXES proposal batch; WI-3499 is in that batch.
- `DELIB-20260882` - parser-hygiene PAUTH context for implementation authorization parser work; relevant to keeping implementation-start parsing deterministic and reviewable.
- `bridge/gtkb-gov-backlog-source-of-truth-2026-05-02-019.md` - originating S376 workaround where an annotated `## target_paths (...)` heading could not be parsed by implementation authorization and required a machine-readable `target_paths:` line.
- `bridge/gtkb-impl-auth-target-paths-parser-annotated-headings-002.md` - Loyal Opposition NO-GO identifying the false `_iter_section_spans()` assumption and requiring a parser primitive that actually excludes nested subsection bullets.

Semantic deliberation search for `WI-3499 implementation authorization target_paths annotated heading parser` on 2026-06-22 returned adjacent parser-hygiene and authorization records; the directly relevant entries above were retained and unrelated DA-enforcement / skill-loading hits were pruned.

## Owner Decisions / Input

- `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING`, via `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION`, is the standing reliability-fixes authorization envelope for small single-concern defect fixes under `PROJECT-GTKB-RELIABILITY-FIXES`.
- `DELIB-20265457` authorized authoring the open reliability-fixes proposal batch. WI-3499 is a P2 defect under that project.

No new owner decision is required for this revision. The NO-GO findings require a corrected algorithm and caller-level tests, not a policy choice.

## Requirement Sufficiency

Existing requirements sufficient. `GOV-FILE-BRIDGE-AUTHORITY-001` already requires an implementation-start authorization packet to be derived from approved bridge artifact content, and WI-3499 documents the parser defect that prevents a valid annotated target-path section from yielding that packet. This revision repairs the parser to honor the existing target-paths contract while preserving canonical inline JSON and plain heading forms. No new or revised requirement is introduced.

## Findings Addressed

### Finding P1-001 - Proposed Helper Cannot Satisfy The Nested-Subsection Test

Response: accepted. Version 001 incorrectly proposed using `_iter_section_spans()` while claiming it would exclude nested deeper headings. The live helper includes nested deeper subsections by design, so it cannot satisfy the required nested-subsection exclusion.

Revision: the implementation will not rely on `_iter_section_spans()` for the target-paths heading body. It will add a target-paths-specific reader that scans markdown headings, accepts only a heading whose normalized text is exactly `target_paths` or starts with `target_paths` followed by a bounded annotation delimiter such as whitespace, `(`, or `:`, and returns body text from the end of that heading up to the next markdown heading of any level (`#` through `######`) or end of file. That termination rule excludes nested `###` subsection bullets from the parent `target_paths` body by construction.

### Finding P2-002 - Proposal Text Overstates Current Closure Of Defect 2

Response: accepted. The prior proposal mixed two parser primitives: current `section_body()` behavior and the proposed `_iter_section_spans()` behavior. The revised defect narrative keeps them separate.

Revision: the live defect is still the exact-heading miss for annotated `## target_paths (...)` sections. The nested-subsection risk is an explicit regression guard for the new target-paths-specific reader: regardless of any incidental current `section_body()` behavior, the new reader must prove that it excludes nested `###` bullets before implementation can be verified.

## Proposed Scope

1. In `scripts/implementation_authorization.py`, add a private helper for the `target_paths` heading form only.
   - It scans markdown headings directly instead of reusing `section_body()` or `_iter_section_spans()`.
   - It matches `target_paths` case-insensitively when the heading text is exactly `target_paths` or when the next character after `target_paths` is an accepted annotation delimiter: whitespace, `(`, `:`, or end of heading text.
   - It returns only the text before the next markdown heading at any level, so nested `###` headings and their bullets are not part of the authorized path list.
   - It rejects lookalike headings such as `target_paths_notes`, `targeting`, or `retarget_paths`.
2. Replace only the `extract_target_paths()` fallback that reads the `## target_paths` heading form. Extraction precedence stays unchanged: inline `target_paths:` JSON first, then `## Files Expected To Change`, then the `## target_paths` heading form.
3. Leave `section_body()` exact-match behavior unchanged for `Specification Links`, `Files Expected To Change`, and `Requirement Sufficiency`.
4. Add focused regression tests in `platform_tests/scripts/test_implementation_authorization.py` for annotated heading acceptance, nested-heading exclusion, lookalike-heading rejection, precedence preservation, and `section_body()` exact-match preservation.

Out of scope: deprecating the heading form in favor of only inline JSON; changing project authorization semantics; changing owner-decision routing; changing work-intent claim behavior.

## Specification-Derived Verification Plan

| Specification / condition | Derived test | Required assertion |
| --- | --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001`: a reviewed proposal's concrete target paths must mint an implementation-start packet | `test_extract_target_paths_accepts_annotated_target_paths_heading` | `extract_target_paths()` returns the backtick paths from `## target_paths (live re-probe; per S376)` instead of raising missing target paths. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` and `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`: parser must not over-authorize nested subsection bullets | `test_extract_target_paths_heading_body_stops_before_nested_subsection` | Bullets under a nested `### Intentionally preserved` subsection are excluded for both plain and annotated target-path headings. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`: target path evidence must be bounded to the intended artifact section | `test_extract_target_paths_rejects_lookalike_target_paths_heading` | Headings such as `## target_paths_notes` or `## retarget_paths` are not treated as target-path authorization. |
| `GOV-FILE-BRIDGE-AUTHORITY-001`: existing canonical forms must keep working | `test_extract_target_paths_plain_heading_and_inline_json_unchanged` | Plain `## target_paths` and inline `target_paths:` JSON continue to return expected paths, with inline JSON precedence unchanged. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`: other parser consumers keep their existing contract | existing `test_section_body_exact_match_preserved` plus targeted assertion | `section_body()` still matches only exact headings for non-target-path consumers. |

Verification commands:

```text
python -m pytest platform_tests/scripts/test_implementation_authorization.py -q --tb=short
python -m ruff check scripts/implementation_authorization.py platform_tests/scripts/test_implementation_authorization.py
python -m ruff format --check scripts/implementation_authorization.py platform_tests/scripts/test_implementation_authorization.py
```

## Pre-Filing Preflight Subsection

Candidate-content preflights were run before live filing against this revision content:

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-impl-auth-target-paths-parser-annotated-headings --content-file .gtkb-state/bridge-revisions/drafts/gtkb-impl-auth-target-paths-parser-annotated-headings-003.md --json
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-impl-auth-target-paths-parser-annotated-headings --content-file .gtkb-state/bridge-revisions/drafts/gtkb-impl-auth-target-paths-parser-annotated-headings-003.md
```

Required filing condition: applicability preflight passes with `missing_required_specs: []`, and clause preflight exits 0 with zero blocking gaps. The helper repeats these candidate-content preflights before publishing the live `REVISED` entry.

Observed candidate results on 2026-06-22:

- Applicability preflight: `preflight_passed: true`; `missing_required_specs: []`; `missing_advisory_specs: []`; `packet_hash: sha256:599cd3bbae031d5d7aa2d0cb0406b6157c47a165cc7482b63c2d1b05b2427854`.
- Clause preflight: exit 0; clauses evaluated: 5; must_apply: 3; evidence gaps in must-apply clauses: 0; blocking gaps: 0.

## Acceptance Criteria

1. `extract_target_paths()` accepts an annotated `## target_paths (...)` heading and extracts only its parent-section backtick paths.
2. The target-path heading body terminates before the next heading at any level; nested `###` subsection bullets are not authorized paths.
3. Lookalike headings are not accepted.
4. Inline JSON and plain heading forms retain current behavior and precedence.
5. `section_body()` exact-match behavior remains unchanged for other consumers.
6. The focused pytest target and ruff lint/format commands pass.

## Risks / Rollback

- Risk: the new target-paths-specific heading matcher could over-match. Mitigation: the accepted suffix is bounded to whitespace, `(`, `:`, or end-of-heading, and tests reject lookalike headings.
- Risk: heading-boundary parsing may miss a valid path if authors put authorized paths inside a nested subsection. Mitigation: that structure is intentionally not accepted; target-path authorization must be in the parent `target_paths` section or the existing inline JSON / Files Expected To Change forms.
- Risk: parser behavior for other sections could drift if shared helpers are changed. Mitigation: do not alter `section_body()`; keep exact-match regression coverage.
- Rollback: revert the single helper/call-site change and remove the added tests. No data migration, schema change, or bridge-state mutation is required beyond normal bridge revision flow.

## Files Expected To Change

- `scripts/implementation_authorization.py`
- `platform_tests/scripts/test_implementation_authorization.py`

## Recommended Commit Type

`fix`

Copyright (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
