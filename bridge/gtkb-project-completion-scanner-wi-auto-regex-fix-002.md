GO

# Loyal Opposition Review - Project Completion Scanner WI-AUTO Regex Fix

bridge_kind: loyal_opposition_review
Document: gtkb-project-completion-scanner-wi-auto-regex-fix
Version: 002
Reviewer: Codex Loyal Opposition (harness A)
Date: 2026-05-16 UTC
Reviewed proposal: `bridge/gtkb-project-completion-scanner-wi-auto-regex-fix-001.md`
Verdict: GO

## Claim

The `-001` proposal is approved for implementation.

The defect is real: both project-completion scanner regex copies currently
accept numeric `WI-\d+`, `GTKB-*`, and `WORKLIST-*` work-item IDs, but not the
`WI-AUTO-*` IDs produced by spec intake. The proposed implementation is narrow,
in-root, covered by an active reliability fast-lane authorization, and includes
spec-derived regression tests for both the package lifecycle path and the
standalone scanner path.

## Prior Deliberations

Deliberation searches were run for:

- `project-completion _WORK_ITEM_LINE_RE WI-AUTO`
- `WI-3335`
- `WI-AUTO completion scanner`

No direct prior deliberation record was found for this exact project-completion
scanner defect. The proposal's cited bridge context is consistent with the live
queue: `gtkb-bridge-compliance-gate-wi-auto-regex-fix` is a sibling hook-surface
thread and currently has latest `GO`, with no file overlap.

## Findings

No blocking findings.

Positive evidence:

- `groundtruth-kb/src/groundtruth_kb/project/lifecycle.py` currently defines
  `_WORK_ITEM_LINE_RE` as
  `(WI-\d+|GTKB-[A-Z0-9-]+|WORKLIST-[A-Z0-9-]+)`, and
  `ProjectLifecycleService._verified_work_items()` uses that regex when reading
  VERIFIED bridge thread metadata.
- `scripts/project_verified_completion_scanner.py` carries the same
  `_WORK_ITEM_LINE_RE` and uses it in `verified_work_items()`.
- `groundtruth-kb/src/groundtruth_kb/intake.py` generates spec-intake work-item
  IDs with `_stable_work_item_id_for_spec()` as `WI-AUTO-{slug}`, where `slug`
  is uppercase alphanumeric/hyphen text.
- `WI-3335` exists in `current_work_items`, is `open/backlogged`, belongs to
  `PROJECT-GTKB-RELIABILITY-FIXES`, and describes this exact defect.
- `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` is active, covers
  `PROJECT-GTKB-RELIABILITY-FIXES` by project membership, and allows `source`
  and `test_addition` mutations.
- All target paths are inside `E:\GT-KB`, and the proposal does not touch
  application files or the sibling bridge-compliance-gate hook files.

Residual risk accepted for this slice:

- The proposal keeps two mirrored regex definitions rather than introducing a
  shared helper. That is acceptable here because the existing lifecycle module
  documents the deliberate mirror, and the proposal requires a drift check to
  confirm the two regex definitions remain byte-identical after the edit.

## Applicability Preflight

- packet_hash: `sha256:084c14e6ef150ba71977a4d8e8e97f025789c4d6493ae189de45a01f068ed889`
- bridge_document_name: `gtkb-project-completion-scanner-wi-auto-regex-fix`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-project-completion-scanner-wi-auto-regex-fix-001.md`
- operative_file: `bridge/gtkb-project-completion-scanner-wi-auto-regex-fix-001.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:traceability, content:deliberation |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | path:groundtruth-kb/src/groundtruth_kb/project/**, content:applications/ |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |

## Clause Applicability

- Bridge id: `gtkb-project-completion-scanner-wi-auto-regex-fix`
- Operative file: `bridge\gtkb-project-completion-scanner-wi-auto-regex-fix-001.md`
- Clauses evaluated: 5
- must_apply: 5, may_apply: 0, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: mandatory (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | must_apply | yes | blocking | blocking |

## Verification Performed

- Read live `bridge/INDEX.md`; selected thread remained latest `NEW`.
- Read the full bridge thread with:
  `$env:PYTHONIOENCODING='utf-8'; python .claude/skills/bridge/helpers/show_thread_bridge.py gtkb-project-completion-scanner-wi-auto-regex-fix --format json --preview-lines 2000`.
- Ran `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-project-completion-scanner-wi-auto-regex-fix`.
- Ran `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-project-completion-scanner-wi-auto-regex-fix`.
- Read the current regex and scanner call sites in
  `groundtruth-kb/src/groundtruth_kb/project/lifecycle.py` and
  `scripts/project_verified_completion_scanner.py`.
- Read the spec-intake `WI-AUTO-*` generator in
  `groundtruth-kb/src/groundtruth_kb/intake.py`.
- Queried `current_work_items` for `WI-3335`.
- Queried `current_project_authorizations` for
  `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING`.
- Queried deliberations for the proposal's stated defect terms.

## Required Next Step

Prime Builder may implement within the target paths listed in
`bridge/gtkb-project-completion-scanner-wi-auto-regex-fix-001.md`, then file
the post-implementation report as the next version with `NEW` status.

Required verification in the implementation report:

- `python -m pytest groundtruth-kb/tests/test_project_artifacts.py platform_tests/scripts/test_project_verified_completion_scanner.py -q`
- `python -m ruff check groundtruth-kb/src/groundtruth_kb/project/lifecycle.py scripts/project_verified_completion_scanner.py groundtruth-kb/tests/test_project_artifacts.py platform_tests/scripts/test_project_verified_completion_scanner.py`
- A drift check confirming the two `_WORK_ITEM_LINE_RE` definitions remain
  byte-identical after the edit.

Decision needed from owner: None.

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
