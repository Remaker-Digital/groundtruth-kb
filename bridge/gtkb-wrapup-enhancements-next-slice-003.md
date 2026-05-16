REVISED

# Implementation Proposal - Wrap-Up Enhancements Next Slice (GTKB-WRAPUP-ENHANCEMENTS)

bridge_kind: implementation_proposal
Document: gtkb-wrapup-enhancements-next-slice
Version: 003
Author: Prime Builder (Claude, harness B)
Date: 2026-05-15 UTC
Session: S353+

Project Authorization: PAUTH-PROJECT-GTKB-SESSION-LIFECYCLE-UX-SESSION-LIFECYCLE-UX-BATCH
Project: PROJECT-GTKB-SESSION-LIFECYCLE-UX
Work Item: GTKB-WRAPUP-ENHANCEMENTS

target_paths: ["scripts/wrap_scan_cross_artifact_drift.py", "platform_tests/scripts/test_wrap_scan_cross_artifact_drift.py"]

This REVISED proposal advances `GTKB-WRAPUP-ENHANCEMENTS` with a new, deeper cross-artifact drift scanner that composes with — and does not replace — the already-VERIFIED W2/S2 reference-integrity consistency scanner.

## Revision Notes

This `-003` revision addresses every finding in the `-002` NO-GO:

- **F1 (P1) — stale `tests/scripts/**` test path.** The verification path is moved off the stale root `tests/scripts/**` tree. The authorized test file is now `platform_tests/scripts/test_wrap_scan_cross_artifact_drift.py`, the live root pytest surface that `pyproject.toml` `testpaths = ["platform_tests", "applications/Agent_Red/tests"]` and the CI workflows discover. The new scanner is root-level wrap-up infrastructure, so no `groundtruth-kb/tests/` package lane is needed.
- **F2 (P1) — proposal reopened the verified W2/S2 consistency scanner.** Reframed per the NO-GO's accepted Path 2: this is NOT a re-implementation of W2/S2. The existing `scripts/wrap_scan_consistency.py` (W2/S2 reference-integrity consistency scanner, VERIFIED via `gtkb-wrapup-enhancements-slice1-014.md`) remains the live wrap consistency surface, unchanged and untouched. This proposal adds a distinct, deeper follow-on scanner with a different concern (semantic cross-artifact *content* drift, not reference-integrity), a stated rationale for why W2/S2 is insufficient for that concern, an explicit composition contract describing how the two scanners' outputs combine, and a deprecation plan. See `## W2/S2 Relationship` below. This proposal does NOT discharge or alter the separate W2 Stage 2 baseline/allowlist obligation defined in `gtkb-wrapup-enhancements-slice1-011.md` and `-012.md`; that remains a separate bridge return path owned by the W2 thread family.
- **F3 (P2) — package/CLI names do not match the existing `wrap_scan_*` surface.** The new scanner is renamed to follow the existing `wrap_scan_*` family convention: `scripts/wrap_scan_cross_artifact_drift.py` (CLI + module in one root script, matching `scripts/wrap_scan_consistency.py` and `scripts/wrap_scan_hygiene.py`). The proposed `groundtruth_kb.wrapup.consistency_check` package module is dropped — the existing scanners are root `scripts/` modules with no `groundtruth_kb` package layer, and matching that convention removes the discoverability/maintenance split F3 identified.
- **Non-blocking note — advisory spec omissions.** The three advisory specs flagged by the `-002` preflight (`ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`, `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`) are now cited in `## Specification Links`.

No owner-decision scope change; the project authorization, project, and work item are unchanged from `-001`.

## Claim

Build a cross-artifact drift scanner — `scripts/wrap_scan_cross_artifact_drift.py` — that compares this-session's bridge proposals, DELIB inserts, work-item mutations, and memory-file changes against canonical MemBase state, flagging semantic *content* contradictions: DELIB content disagreeing with the cited spec's status; bridge proposal `target_paths` mismatching the files actually modified; `memory/*.md` state recording a WI status differently from MemBase; and cross-DELIB references to retired records. This is a deeper, content-level scanner that complements the already-VERIFIED W2/S2 reference-integrity scanner without replacing it.

## W2/S2 Relationship (Rationale, Composition Contract, Deprecation Plan)

**Why the existing W2/S2 scanner is insufficient for this concern.** `scripts/wrap_scan_consistency.py` (W2/S2, VERIFIED) detects *reference-integrity* failures: an INDEX entry citing a missing bridge file, a bridge file orphaned from INDEX, a work-list entry citing a missing bridge file. Its question is "does the cited artifact exist and is it linked?" It does not inspect artifact *content*. The drift class this proposal addresses is different: an artifact that exists and is correctly linked but whose *content disagrees* with another artifact (a DELIB whose claimed spec status contradicts the spec's actual MemBase status; a bridge `target_paths` list that does not match the files git shows were modified; a `memory/*.md` line stating a WI status MemBase does not record). Extending `wrap_scan_consistency.py` with content-comparison lenses would mix two distinct failure taxonomies, two severity models (reference-integrity is structural/blocking-ish; content drift is informational/report-only), and two output schemas in one module — exactly the audit-trail split F2 warned against. A distinct scanner keeps each module's concern, schema, and severity model coherent.

**Composition contract.** The two scanners are siblings in the `wrap_scan_*` family and compose by concatenation, not replacement:
- `wrap_scan_consistency.py` (W2/S2) runs first and reports reference-integrity findings.
- `wrap_scan_cross_artifact_drift.py` (this proposal) runs after and reports content-drift findings.
- Each emits its own independently-parseable markdown + JSON block under its own scanner ID; the wrap-up procedure presents both. Neither scanner reads the other's output; there is no shared state. The owner sees one wrap consistency surface composed of two clearly-labelled sections (reference integrity, content drift).
- This proposal does NOT register the new scanner into the `/kb-session-wrap` skill or the release gate; that wiring, if desired, is a follow-on slice and is explicitly out of scope here. The new scanner is a standalone CLI in this slice.

**Deprecation plan.** No existing artifact is deprecated by this proposal. `wrap_scan_consistency.py` and its tests are unchanged and remain canonical for reference integrity. If a future slice consolidates the `wrap_scan_*` family behind a single dispatcher, that consolidation would be its own bridge proposal with migration tests; this proposal neither performs nor presumes that consolidation.

## In-Root Placement Evidence

All target paths are within `E:\GT-KB`. `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` satisfied. `scripts/wrap_scan_cross_artifact_drift.py` is an in-root platform script; `platform_tests/scripts/**` is the in-root platform test surface.

## Specification Links

- `GOV-SESSION-LIFECYCLE-PROACTIVE-ENGAGEMENT-001` - session lifecycle proactive-engagement requirement; the wrap-up drift scan is part of proactive wrap-up engagement.
- `GOV-SESSION-SELF-INITIALIZATION-001` - companion startup/wrap lifecycle spec.
- `GOV-08` - KB is truth; the drift scanner enforces that canonical MemBase state is the reference when artifacts disagree.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge protocol authority governing this proposal as a bridge artifact.
- `SPEC-AUQ-POLICY-ENGINE-001` - deterministic policy-engine surface adjacent to the wrap-up scanner family.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - in-root placement; all target paths are in-root.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - cross-cutting constraint requiring this proposal to cite every relevant governing specification.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - cross-cutting constraint requiring the post-implementation VERIFIED step to rest on executed spec-derived tests; the Specification-Derived Verification Plan below maps every linked spec to a test.
- `GOV-STANDING-BACKLOG-001` - WI-tracked work; GTKB-WRAPUP-ENHANCEMENTS is the governed work item.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - durable artifact-graph model; the WI, bridge thread, and linked specs form the artifact graph for this work.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - artifact lifecycle trigger discipline; the drift scanner inspects artifacts at lifecycle boundaries (session wrap).
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - artifact-oriented governance baseline; this work is captured as governed artifacts (WI + bridge thread + spec-derived tests).
- `DELIB-S350-BATCH5-EIGHT-PROJECT-AUTHORIZATIONS` - owner-decision evidence for the project authorization.

## Prior Deliberations

- `DELIB-S350-BATCH5-EIGHT-PROJECT-AUTHORIZATIONS` - batch-5 owner authorization including PROJECT-GTKB-SESSION-LIFECYCLE-UX and work item GTKB-WRAPUP-ENHANCEMENTS.
- `DELIB-0939` - prior Slice 1 NO-GO on wrap-up scanner containment and warning/error semantics; informs the report-only severity model adopted here.
- `DELIB-0937` - prior post-implementation NO-GO showing W2 live-scan operational issues; informs keeping the new scanner distinct from W2.
- `DELIB-1114` - compressed bridge-thread record for `gtkb-wrapup-enhancements-slice1` (Slice 1 closed at VERIFIED).
- `DELIB-2062` - compressed bridge-thread record for `gtkb-wrapup-enhancements-slice1`.

No prior deliberation rejected a distinct content-drift scanner alongside the W2/S2 reference-integrity scanner; the `-002` NO-GO explicitly offered this as accepted Path 2.

## Owner Decisions / Input

- 2026-05-14 UTC, S350+: owner approved the PROJECT-GTKB-SESSION-LIFECYCLE-UX authorization batch (`DELIB-S350-BATCH5-EIGHT-PROJECT-AUTHORIZATIONS`), including this work item GTKB-WRAPUP-ENHANCEMENTS. The authorization `PAUTH-PROJECT-GTKB-SESSION-LIFECYCLE-UX-SESSION-LIFECYCLE-UX-BATCH` is active and covers this WI through project membership; the `-002` review independently confirmed this.

## Requirement Sufficiency

Existing requirements sufficient. `GOV-SESSION-LIFECYCLE-PROACTIVE-ENGAGEMENT-001` already requires proactive wrap-up engagement that draws owner attention to cross-dimension issues, and `GOV-08` establishes MemBase as the reference of truth when artifacts disagree. The GTKB-WRAPUP-ENHANCEMENTS work item description specifies the scanner suite. No new or revised requirement or specification is created by this work.

## Clause Scope Clarification (Not a Bulk Operation)

This proposal is not a bulk backlog operation. It performs no batch resolve, promote, or retire of work items or specifications. It implements a single work item (GTKB-WRAPUP-ENHANCEMENTS), a single new scanner. References to "work item", "backlog", and "standing backlog" describe that single governed work item and its membership in PROJECT-GTKB-SESSION-LIFECYCLE-UX per the formal-artifact-approval packet `.groundtruth/formal-artifact-approvals/2026-05-14-batch5-eight-project-authorizations.json`. The review-packet inventory is a single thread: IP-1 (scanner) + IP-2 (tests). The inventory of touched files is the two `target_paths` entries above; no formal artifact is created. The scanner itself is report-only and never mutates any work item or specification.

## Bridge INDEX Maintenance

This proposal keeps `bridge/INDEX.md` as the canonical bridge workflow state. The `-003` REVISED line is appended under the existing `Document: gtkb-wrapup-enhancements-next-slice` block above the prior `NO-GO` and `NEW` lines; the prior versions are preserved unchanged (append-only audit trail).

## Proposed Scope

### IP-1: Cross-artifact drift scanner (`scripts/wrap_scan_cross_artifact_drift.py`)

A single root `scripts/` module + CLI in the `wrap_scan_*` family convention. Four content-drift check lenses:

1. **Spec-DELIB content drift**: for DELIBs inserted this session that reference a spec ID, check that the DELIB's claimed spec status matches the spec's actual current MemBase status.
2. **Bridge `target_paths` vs actual changes**: for bridge proposals filed this session, check that `target_paths` covers the files git status/diff shows were actually edited.
3. **WI status MemBase vs memory**: for WIs touched this session, check that `memory/*.md` references match the WI's MemBase status.
4. **Cross-DELIB references**: for DELIBs that cite other DELIBs, check the referenced DELIBs exist and are not retired.

CLI surface: reads session-id from env or `--session-id` arg; emits a markdown report plus a JSON block under a distinct scanner ID. All findings are severity `informational` / report-only (per the F2-distinct-scanner severity model and the `DELIB-0939` containment lesson).

### IP-2: Tests (`platform_tests/scripts/test_wrap_scan_cross_artifact_drift.py`)

Tests verify each lens with fixture data, plus the output schema and report-only severity.

## Specification-Derived Verification Plan

Each linked specification maps to at least one test. Tests are added only within the `target_paths` test file.

| Behavior / Spec clause | Test | Covers |
|---|---|---|
| Spec-DELIB content drift: aligned status passes | `test_spec_delib_aligned` | GOV-08, GOV-SESSION-LIFECYCLE-PROACTIVE-ENGAGEMENT-001 |
| Spec-DELIB content drift: status disagreement flagged | `test_spec_delib_drift_flagged` | GOV-08 |
| Bridge `target_paths` vs actual-diff gap detected | `test_target_paths_vs_actual_diff` | GOV-FILE-BRIDGE-AUTHORITY-001, GOV-08 |
| WI status MemBase vs memory mismatch flagged | `test_wi_status_mismatch_flagged` | GOV-08, DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 |
| Cross-DELIB broken/retired reference detected | `test_broken_delib_reference_flagged` | GOV-08, ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 |
| Output schema stable and all findings are report-only severity | `test_output_schema_and_report_only_severity` | DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001, GOV-SESSION-LIFECYCLE-PROACTIVE-ENGAGEMENT-001 |

Verification commands:

```
python -m pytest platform_tests/scripts/test_wrap_scan_cross_artifact_drift.py -q --tb=short
python -m pytest platform_tests/scripts/test_wrap_scan_consistency.py -q --tb=short
python -m ruff check .
python -m ruff format --check .
```

The second pytest command re-runs the existing W2/S2 scanner tests to confirm this proposal does not regress the verified W2/S2 surface (a no-touch composition guard).

## Acceptance Criteria

- IP-1 and IP-2 landed; all six listed tests PASS.
- The new scanner is a root `scripts/wrap_scan_cross_artifact_drift.py` module in the `wrap_scan_*` family convention (F3 resolved).
- The authorized test path is under `platform_tests/**` (F1 resolved).
- `scripts/wrap_scan_consistency.py` and `platform_tests/scripts/test_wrap_scan_consistency*.py` are unchanged, and the W2/S2 tests still PASS (F2 resolved — distinct, composing scanner; no reopening of W2/S2).
- All findings emitted by the new scanner are report-only severity.
- `ruff check` and `ruff format --check` are clean.
- Both preflights PASS.
- The separate W2 Stage 2 baseline/allowlist obligation (`gtkb-wrapup-enhancements-slice1-011.md` / `-012.md`) is acknowledged as out of scope and remains owned by the W2 thread family.

## Risks / Rollback

- Risk: heuristics for `memory/*.md` vs MemBase comparison may over-flag intentional divergence. Mitigation: all findings are `informational` / report-only; the scanner never mutates or blocks.
- Risk: a parallel "consistency" surface confuses the owner. Mitigation: the new scanner is named `wrap_scan_cross_artifact_drift` (not "consistency"), labelled as content-drift, and explicitly composes with — does not replace — W2/S2 per the Composition Contract above.
- Rollback: delete `scripts/wrap_scan_cross_artifact_drift.py` and its test file; no other artifact is touched, so there is no behavior change elsewhere.

## Files Expected To Change

- `scripts/wrap_scan_cross_artifact_drift.py` — new root cross-artifact content-drift scanner module + CLI (IP-1).
- `platform_tests/scripts/test_wrap_scan_cross_artifact_drift.py` — new spec-derived tests for the four drift lenses, output schema, and report-only severity (IP-2).

## Recommended Commit Type

`feat` - net-new wrap-up scanner module + tests. ~120 LOC of source + tests.

## Pre-Filing Preflight

Both mandatory pre-filing preflights were run on this `-003` content after filing the INDEX entry; outputs are embedded in `## Applicability Preflight` and `## Clause Applicability` below.

## Applicability Preflight

- packet_hash: `sha256:be0daf3bce2571c113ff9a449d668ed85c5c26adb3117a7de262ad2e5ba3a70c`
- bridge_document_name: `gtkb-wrapup-enhancements-next-slice`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-wrapup-enhancements-next-slice-003.md`
- operative_file: `bridge/gtkb-wrapup-enhancements-next-slice-003.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation, content:MemBase |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | path:applications/**, content:applications/ |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:verified, content:retired |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal, content:bridge proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |

## Clause Applicability

- Bridge id: `gtkb-wrapup-enhancements-next-slice`
- Operative file: `bridge\gtkb-wrapup-enhancements-next-slice-003.md`
- Clauses evaluated: 5
- must_apply: 5, may_apply: 0, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: mandatory (default invocation). Exit 5 = blocking gap; exit 0 = pass. Result: exit 0.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | must_apply | yes | blocking | blocking |

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
