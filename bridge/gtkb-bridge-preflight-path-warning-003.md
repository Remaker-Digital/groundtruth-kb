REVISED

# Implementation Proposal - Bridge Preflight: Missing Parent Directory Warning (WI-3272)

bridge_kind: implementation_proposal
Document: gtkb-bridge-preflight-path-warning
Version: 003
Author: Prime Builder (Claude, harness B)
Date: 2026-05-15 UTC
Session: S353+

Project Authorization: PAUTH-PROJECT-GTKB-BRIDGE-TOOLING-ENHANCEMENTS-BRIDGE-TOOLING-ENHANCEMENTS-PARALLEL-BATCH
Project: PROJECT-GTKB-BRIDGE-TOOLING-ENHANCEMENTS
Work Item: WI-3272

target_paths: ["scripts/bridge_applicability_preflight.py", "platform_tests/scripts/test_bridge_applicability_preflight.py"]

This REVISED proposal extends `scripts/bridge_applicability_preflight.py` with a warning when a bridge proposal cites `Files Changed` / `Files Expected To Change` or `target_paths` paths whose parent directory does not exist. Observed defect during S341 (bridge `gtkb-peer-solution-workflow-contract-adr` REVISED-3): a test path was cited that pointed to a non-existent directory, surfaced only at implementation time.

## Revision Notes

This `-003` revision addresses all three findings in the `-002` NO-GO verdict:

- **F1 (P2 — verification command targets a non-existent test path):**
  Resolved. The nonexistent top-level path
  `tests/scripts/test_bridge_applicability_preflight.py` is removed from
  `target_paths` (live checkout inspection confirms `E:\GT-KB\tests` and
  `E:\GT-KB\tests\scripts` do not exist). `target_paths` and the verification
  command now reference only the existing file
  `platform_tests/scripts/test_bridge_applicability_preflight.py`. No new
  top-level `tests` root is created by this work.
- **F2 (P2 — warning source underspecified against the current parser):**
  Resolved. IP-1 below now defines a SEPARATE, narrow cited-path collection
  step for the new warning — a new function `collect_cited_implementation_paths()`
  that parses ONLY (a) explicit `target_paths:` metadata lines and (b) a
  dedicated `## Files Changed` / `## Files Expected To Change` section/table
  parser. The existing `extract_target_paths()` function and its broad
  document-wide `PATH_TOKEN_RE` scan (`scripts/bridge_applicability_preflight.py:41`,
  `:164`) are left UNCHANGED and continue to feed applicability matching only.
  The missing-parent warning is computed from `collect_cited_implementation_paths()`,
  not from `extract_target_paths()`, so incidental path-like tokens in prose,
  prior-deliberation citations, bridge-file citations, or approval-packet
  paths cannot enter `warnings.missing_parent_dirs`. A new test
  (`test_preflight_warning_ignores_incidental_prose_paths`) proves incidental
  prose paths do not appear in the warning list.
- **F3 (P3 — applicability preflight reports missing advisory specs):**
  Resolved. The three advisory specs `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`,
  `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`, and `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
  are now cited in `## Specification Links` below with relevance notes.

## Claim

Add a non-blocking advisory warning to the preflight output listing cited paths whose parent directory does not exist relative to the project root. The warning is computed from a precise cited-path collection (explicit `target_paths` metadata + a dedicated `Files Changed` section parser) — NOT from the broad document-wide path-token scan. Existing pass/fail semantics preserved; the warning surfaces in the `Applicability Preflight` section text and as a stderr line for tooling.

## In-Root Placement Evidence

All target paths in-root under `E:\GT-KB`. Bridge file at `E:\GT-KB\bridge\gtkb-bridge-preflight-path-warning-003.md`. `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` satisfied.

## Specification Links

- `SPEC-AUQ-POLICY-ENGINE-001` - preflight is part of the policy engine surface.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - preflight enforces this; this enhancement is a quality-of-output improvement.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge protocol.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - in-root only.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - spec-to-test mapping below.
- `GOV-STANDING-BACKLOG-001` - WI-3272 tracked.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - durable artifact-graph model; the preflight warning improves the artifact-graph trustworthiness by surfacing misplaced cited paths early.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - artifact lifecycle trigger discipline; WI-3272 triggers this implementation proposal and its spec-derived tests.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - artifact-oriented governance baseline; the warning enhancement is captured as governed work with a bridge artifact and spec-derived tests.
- `DELIB-S350-BATCH2-THREE-PROJECT-AUTHORIZATIONS` - owner-decision evidence.

## Prior Deliberations

- `DELIB-S350-BATCH2-THREE-PROJECT-AUTHORIZATIONS` - batch-2 authorization 2026-05-14; records the owner authorization for `PAUTH-PROJECT-GTKB-BRIDGE-TOOLING-ENHANCEMENTS` including WI-3272.

The Codex `-002` deliberation search confirmed no prior deliberation
contradicts adding a missing-parent-directory warning.

## Owner Decisions / Input

- 2026-05-14 UTC, S350+: owner AUQ "Authorize all 3 groups (7 WIs added)" — explicit authorization for this NEW under `PAUTH-PROJECT-GTKB-BRIDGE-TOOLING-ENHANCEMENTS`.

## Requirement Sufficiency

Existing requirements sufficient. The WI-3272 description is the operative
spec for the missing-parent-directory warning; `SPEC-AUQ-POLICY-ENGINE-001`
governs the preflight surface. No new or revised requirement or specification
is created by this work.

## Clause Scope Clarification (Not a Bulk Operation)

Not a bulk operation. One WI (WI-3272) targeted; member of PROJECT-GTKB-BRIDGE-TOOLING-ENHANCEMENTS per `formal-artifact-approval` packet `.groundtruth/formal-artifact-approvals/2026-05-14-batch2-three-project-authorizations.json`. It performs no batch resolve/promote/retire across the backlog. Review-packet inventory: IP-1 (preflight warning) + IP-2 (tests) scoped to one thread. The applicable evidence pattern is a single-WI tooling-enhancement proposal with formal-artifact-approval discipline preserved unchanged.

## Bridge INDEX Update Evidence

`-003` REVISED line prepended above the `-002` NO-GO line under the `Document: gtkb-bridge-preflight-path-warning` block; prior `-001`/`-002` versions preserved unchanged per the append-only bridge audit trail.

## Files Expected To Change

- `scripts/bridge_applicability_preflight.py` — new `collect_cited_implementation_paths()` function + missing-parent-directory warning computation and rendering.
- `platform_tests/scripts/test_bridge_applicability_preflight.py` — spec-derived tests for the new warning.

## Proposed Scope

### IP-1: Add parent-directory check to preflight (precise cited-path source per F2)

In `scripts/bridge_applicability_preflight.py`:

1. **New narrow collector — `collect_cited_implementation_paths(content)`:**
   add a new function, separate from the existing `extract_target_paths()`,
   that collects cited implementation paths from ONLY two sources:
   - explicit `target_paths:` / `target_path:` metadata lines (reuse the
     existing `TARGET_PATH_RE` parse logic — JSON list or comma/space split);
   - a dedicated section parser for a `## Files Changed` or
     `## Files Expected To Change` heading: collect path-like tokens that
     appear inside that section's bullet/table rows only, until the next
     `#`-prefixed heading.

   This collector does NOT scan the whole document and does NOT use
   `PATH_TOKEN_RE` against arbitrary prose.

2. **Existing `extract_target_paths()` is unchanged.** Its broad
   document-wide `PATH_TOKEN_RE` scan continues to feed applicability
   matching only. The new warning never reads from it.

3. **Missing-parent computation:** for each path from
   `collect_cited_implementation_paths()`, compute the parent directory
   relative to project root. If the parent directory does not exist AND the
   path itself does not exist as a target, add the path to a
   `warnings.missing_parent_dirs` list.

4. **Rendering:** emit `warnings.missing_parent_dirs` in the output JSON and
   render a `- warnings.missing_parent_dirs: [...]` line in the
   `Applicability Preflight` markdown section beneath `preflight_passed`.
   Also emit a stderr line for tooling consumers.

5. **Non-blocking:** the warning does NOT change the exit code;
   `preflight_passed` semantics are unchanged.

### IP-2: Tests

Tests are added to `platform_tests/scripts/test_bridge_applicability_preflight.py`
(the existing file confirmed present; no new test root is created):

- cited `target_paths` entry with an existing parent → no warning;
- cited `target_paths` entry with a missing parent → warning emitted;
- mixed valid + invalid cited paths → only the invalid path in the warning list;
- cited path that itself exists → no warning;
- a `## Files Changed` / `## Files Expected To Change` section path with a
  missing parent → warning emitted;
- **F2 false-positive guard:** incidental path-like tokens that appear ONLY in
  prose / prior-deliberation citations / bridge-file citations (NOT in
  `target_paths` and NOT in a `Files Changed` section) → MUST NOT appear in
  `warnings.missing_parent_dirs`;
- existing output schema preserved.

## Specification-Derived Verification Plan

| Linked specification / behavior | Test |
|---|---|
| `SPEC-AUQ-POLICY-ENGINE-001` — cited path with existing parent yields no warning | `test_preflight_no_warning_when_parent_exists` |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — cited path with missing parent yields a warning | `test_preflight_warns_when_parent_missing` |
| `SPEC-AUQ-POLICY-ENGINE-001` — mixed valid + invalid: only invalid warned | `test_preflight_warns_only_invalid_paths` |
| `SPEC-AUQ-POLICY-ENGINE-001` — existing path itself yields no warning | `test_preflight_no_warning_when_path_exists` |
| `GOV-FILE-BRIDGE-AUTHORITY-001` — a `Files Changed` section path with missing parent yields a warning | `test_preflight_warns_for_files_changed_section_path` |
| `GOV-FILE-BRIDGE-AUTHORITY-001` / `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — incidental prose paths are NOT warned (F2 guard) | `test_preflight_warning_ignores_incidental_prose_paths` |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — existing output schema preserved | `test_preflight_output_passes_existing_schema_test` |

Corrected verification command (replaces the `-001` nonexistent `tests/...` path):

```
python -m pytest platform_tests/scripts/test_bridge_applicability_preflight.py -q --tb=short
python -m ruff check .
```

## Acceptance Criteria

- IP-1 landed: `collect_cited_implementation_paths()` added; `extract_target_paths()` left unchanged; `warnings.missing_parent_dirs` rendered.
- IP-2: all listed tests pass, including `test_preflight_warning_ignores_incidental_prose_paths` proving incidental prose paths are not warned.
- `preflight_passed` exit-code semantics unchanged for existing inputs.
- Both preflights PASS on the `-003` operative file.

## Risks / Rollback

- Risk: false-positive when paths exist only in a worktree branch not yet merged. Mitigation: the check evaluates the live filesystem under the project root; warnings are non-blocking and advisory only, so a worktree-only path produces an advisory note, never a gate failure.
- Risk (addressed by F2): warning noise from incidental prose paths. Mitigation: the warning reads only from the narrow `collect_cited_implementation_paths()` collector, and `test_preflight_warning_ignores_incidental_prose_paths` regression-guards it.
- Rollback: revert the `collect_cited_implementation_paths()` function and the warning computation/rendering; `extract_target_paths()` is untouched so applicability matching is unaffected.

## Recommended Commit Type

`feat` - non-blocking preflight warning enhancement plus tests. Net-new capability surface.

## Pre-Filing Preflight

Both mandatory pre-filing preflights were run on this `-003` operative file
after filing the INDEX entry. Outputs are embedded in the `## Applicability
Preflight` and `## Clause Applicability` sections below.

## Applicability Preflight

```text
- packet_hash: `sha256:fea404c3e49abcd0ea8d7e5cf731339c8ae7e7274adbd88ce370975585956ca9`
- bridge_document_name: `gtkb-bridge-preflight-path-warning`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-bridge-preflight-path-warning-003.md`
- operative_file: `bridge/gtkb-bridge-preflight-path-warning-003.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 | advisory | yes | content:artifact, content:deliberation |
| DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 | advisory | yes | content:verified |
| DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 | blocking | yes | doc:*, content:Specification Links, content:implementation proposal, content:bridge proposal |
| DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 | blocking | yes | doc:*, content:VERIFIED, content:verification, content:spec-to-test, content:Specification-Derived Verification |
| GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 | advisory | yes | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| GOV-FILE-BRIDGE-AUTHORITY-001 | blocking | yes | doc:* |
```

## Clause Applicability

```text
- Bridge id: `gtkb-bridge-preflight-path-warning`
- Operative file: `bridge\gtkb-bridge-preflight-path-warning-003.md`
- Clauses evaluated: 5
- must_apply: 5, may_apply: 0, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: mandatory (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT | ADR-ISOLATION-APPLICATION-PLACEMENT-001 | must_apply | yes | blocking | blocking |
| GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL | GOV-FILE-BRIDGE-AUTHORITY-001 | must_apply | yes | blocking | blocking |
| DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS | DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 | must_apply | yes | blocking | blocking |
| DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING | DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 | must_apply | yes | blocking | blocking |
| GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS | GOV-STANDING-BACKLOG-001 | must_apply | yes | blocking | blocking |

Exit 0 = pass.
```

## Copyright

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
