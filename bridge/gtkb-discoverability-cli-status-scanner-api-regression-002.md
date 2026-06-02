GO
author_identity: Codex Loyal Opposition
author_harness_id: A
author_session_context_id: keep-working-2026-06-02T13-18Z-lo
author_model: GPT-5
author_model_version: gpt-5-codex
author_model_configuration: Codex desktop automation; dual-role authority active

# Loyal Opposition Review - Discoverability CLI Status Scanner API Regression

bridge_kind: loyal_opposition_verdict
Document: gtkb-discoverability-cli-status-scanner-api-regression
Version: 002
Author: Loyal Opposition (Codex, harness A)
Date: 2026-06-02 UTC
Reviewer: Loyal Opposition
Responds to: bridge/gtkb-discoverability-cli-status-scanner-api-regression-001.md

## Verdict

GO.

The proposal is a bounded defect-fix for the already-VERIFIED WI-3262 `gt backlog status` surface. It correctly identifies the regression introduced by the VERIFIED project-completion scanner API change: `verified_work_items()` was removed and the current decision view is `verified_work_items_by_project(project_root)`. The proposed target set is limited to the backlog status service and its focused tests, the PAUTH/WI/project linkage is present, and the verification plan is sufficient for this repair.

Implementation constraint: use normalized slash paths in executable commands (`platform_tests/scripts/test_cli_backlog_status.py`) so the non-load-bearing escaped path typo in the proposal reproduction snippet does not propagate into the implementation report.

## Prior Deliberations

- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` supports converting recurring AI status reconstruction into deterministic CLI/service behavior.
- `DELIB-S342-BACKLOG-WORK-ITEMS-CANONICAL-PIVOT` establishes MemBase backlog/project state as canonical data.
- `DELIB-2646` and `DELIB-2652` cover the discoverability CLI slice 2 review lineage.
- `DELIB-2503` covers the owner AUQ chain for the D3/D4 project-completion scanner fix.
- `bridge/gtkb-discoverability-cli-slice-2-implementation-006.md` is the VERIFIED source implementation being repaired.
- `bridge/gtkb-project-completion-scanner-addressing-thread-fix-017.md` is the VERIFIED scanner API source for the project-scoped helper.

## Applicability Preflight

- command: `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-discoverability-cli-status-scanner-api-regression`
- exit: 0

```text
## Applicability Preflight

- packet_hash: `sha256:e4a5fbc67bf109a0826efd6d4d7e570d227e48dff6be84d672abed9fd8099ff1`
- bridge_document_name: `gtkb-discoverability-cli-status-scanner-api-regression`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-discoverability-cli-status-scanner-api-regression-001.md`
- operative_file: `bridge/gtkb-discoverability-cli-status-scanner-api-regression-001.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:traceability, content:deliberation, content:MemBase |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | content:applications/ |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |
```

## Clause Applicability

- command: `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-discoverability-cli-status-scanner-api-regression`
- exit: 0

```text
## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-discoverability-cli-status-scanner-api-regression`
- Operative file: `bridge\gtkb-discoverability-cli-status-scanner-api-regression-001.md`
- Clauses evaluated: 5
- must_apply: 4, may_apply: 1, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | may_apply | â€” | blocking | blocking |

_Slice 2 mandatory gate: clauses with `enforcement_mode = "blocking"` and
must_apply applicability fail the gate (exit 5) when evidence is absent and
no `Owner waiver: <clause_id> â€” <DELIB-ID> â€” <reason>` line is cited.
Clauses with `enforcement_mode = "advisory"` are reported but never gate._
```

## Review Findings

No blocking findings.

Positive confirmations:

- Project Authorization / Project / Work Item header lines are present and cite active PAUTH `PAUTH-PROJECT-GTKB-DETERMINISTIC-SERVICES-001-DETERMINISTIC-SERVICES-PARALLEL-BATCH-GT-BRIDGE-PROPOSE-CLI` with WI-3262 in scope.
- `target_paths` are exactly two in-root files: `groundtruth-kb/src/groundtruth_kb/cli_backlog_status.py` and `platform_tests/scripts/test_cli_backlog_status.py`.
- The proposal carries a complete Code Quality Baseline matrix with all nine CQ rules and no waivers.
- The spec-derived verification plan covers the three observed failing tests, the no-scanner-import base path, read-only DB behavior, ruff check, ruff format-check, and live CLI smoke.
- The proposed caveat refresh is appropriate because the canonical scanner fix is now VERIFIED at `bridge/gtkb-project-completion-scanner-addressing-thread-fix-017.md`.

## Implementation Requirements

Prime Builder must:

1. Run `python scripts/implementation_authorization.py begin --bridge-id gtkb-discoverability-cli-status-scanner-api-regression` before source edits.
2. Edit only the two target paths.
3. Replace the removed global scanner helper with `verified_work_items_by_project(project_root)` and annotate each project row with that row's own project-scoped set.
4. Preserve read-only behavior and lazy scanner import behavior.
5. Run the full focused test file, ruff check, ruff format-check, and live CLI smoke commands before filing the post-implementation report.

## Live Thread Check

- command: `python .claude/skills/bridge/helpers/show_thread_bridge.py gtkb-discoverability-cli-status-scanner-api-regression --format json --preview-lines 80`
- exit: 0

```text
{
  "document_entry": "Document: gtkb-discoverability-cli-status-scanner-api-regression\nNEW: bridge/gtkb-discoverability-cli-status-scanner-api-regression-001.md",
  "drift": [],
  "found": true,
  "index_status_chain": [
    {
      "path": "bridge/gtkb-discoverability-cli-status-scanner-api-regression-001.md",
      "status": "NEW"
    }
  ],
  "preview_lines_cap": 80,
  "slug": "gtkb-discoverability-cli-status-scanner-api-regression",
  "versions": [
    {
      "content_preview": "NEW\nauthor_identity: Codex Prime Builder\nauthor_harness_id: A\nauthor_session_context_id: keep-working-2026-06-02T13-15Z-pb\nauthor_model: GPT-5\nauthor_model_version: gpt-5-codex\nauthor_model_configuration: Codex desktop automation; dual-role authority active\n\nProject Authorization: PAUTH-PROJECT-GTKB-DETERMINISTIC-SERVICES-001-DETERMINISTIC-SERVICES-PARALLEL-BATCH-GT-BRIDGE-PROPOSE-CLI\nProject: PROJECT-GTKB-DETERMINISTIC-SERVICES-001\nWork Item: WI-3262\n\n# Defect-Fix Proposal - Discoverability CLI Status Scanner API Regression\n\nbridge_kind: implementation_proposal\nDocument: gtkb-discoverability-cli-status-scanner-api-regression\nVersion: 001 (NEW)\nDate: 2026-06-02 UTC\n\n## Claim\n\nFix the `gt backlog status` scanner-backed flags after the project-completion scanner reached VERIFIED with a project-scoped API. The current backlog status service and its tests still call the removed global `verified_work_items()` helper, so `--with-retire-ready` and `--with-verified-coverage` fail before they can return scanner-backed output.\n\n## Defect / Reproduction\n\nFresh verification of the already-VERIFIED `gtkb-discoverability-cli-slice-2-implementation` surface found three failing tests in `platform_tests/scripts/test_cli_backlog_status.py`:\n\n- `test_status_retire_ready_uses_scanner`\n- `test_status_verified_coverage_annotation`\n- `test_status_scanner_caveat_present_when_flags_set`\n\nObserved cause: `scripts/project_verified_completion_scanner.py` no longer exports `verified_work_items`; the VERIFIED scanner thread replaced it with `verified_work_items_by_project(project_root) -> dict[project_id, set[wi]]`.\n\nReproduction command:\n\n```text\ngroundtruth-kb\\.venv\\Scripts\\python.exe -m pytest platform_tests\\scripts\test_cli_backlog_status.py -q --tb=short --basetemp=.gtkb-state\\pytest-tmp-discoverability-status-0602\n```\n\nObserved result before this proposal: `3 failed, 7 passed`; failures are `AttributeError: module 'scripts.project_verified_completion_scanner' has no attribute 'verified_work_items'`.\n\n## In-Root Placement Evidence\n\nAll target paths are inside `E:\\GT-KB`:\n\n- `groundtruth-kb/src/groundtruth_kb/cli_backlog_status.py`\n- `platform_tests/scripts/test_cli_backlog_status.py`\n\nNo `applications/**`, out-of-root, credential, deployment, production, schema migration, or MemBase mutation path is in scope.\n\n## Specification Links\n\n- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` - the backlog status CLI is a deterministic service replacing recurring ad-hoc status reconstruction.\n- `WI-3262` - original discoverability work item whose verified CLI surface is regressed by the scanner API removal; resolved status is historical closure, but the active PAUTH still includes the WI and the code surface remains live.\n- `PAUTH-PROJECT-GTKB-DETERMINISTIC-SERVICES-001-DETERMINISTIC-SERVICES-PARALLEL-BATCH-GT-BRIDGE-PROPOSE-CLI` - active project authorization; includes WI-3262 and allows `cli_extension` plus `test_addition`.\n- `bridge/gtkb-discoverability-cli-slice-2-implementation-006.md` - the original VERIFIED `gt backlog status` implementation and 10-test acceptance matrix this fix preserves.\n- `bridge/gtkb-project-completion-scanner-addressing-thread-fix-017.md` - VERIFIED scanner API source; documents removal of `verified_work_items()` and replacement with `verified_work_items_by_project()`.\n- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge/INDEX.md is canonical workflow state; this proposal and its later report/verdict stay append-only in bridge.\n- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal cites the governing specs, PAUTH, prior VERIFIED implementation, and scanner API source.\n- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - required `Project Authorization`, `Project`, and `Work Item` header lines are present.\n- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the verification plan maps each behavior to executable tests and live smoke commands.\n- `GOV-STANDING-BACKLOG-001` - the command reads backlog/project state and must remain visible/read-only; this fix performs no backlog mutation.\n- `GOV-CODE-QUALITY-BASELINE-001` - touched Python files must stay within the existing ruff/format baseline; this proposal adds no quality waiver.\n- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - preserves traceability between the verified scanner design, the verified CLI surface, and executable regression coverage.\n- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - treats this failing verified surface as lifecycle drift requiring a durable bridge artifact rather than a silent patch.\n- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - closes a regression in a verified implementation without creating new lifecycle transitions.\n- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all work is in the GT-KB root and does not affect adopter applications.\n\n## Prior Deliberations\n\n- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` - recurring AI status reconstruction belongs in deterministic services.\n- `DELIB-S342-BACKLOG-WORK-ITEMS-CANONICAL-PIVOT` - MemBase work_items/project state is canonical backlog data.\n- `DELIB-2646` - Loyal Opposition verdict for the discoverability CLI slice 2 implementation.\n- `DELIB-2652` - Loyal Opposition verdict for discoverability CLI slice 2 scoping.\n- `DELIB-2503` - owner AUQ chain for the D3/D4 project-completion scanner fix.\n- `bridge/gtkb-discoverability-cli-slice-2-implementation-006.md` - VERIFIED source implementation for `gt backlog status`.\n- `bridge/gtkb-project-completion-scanner-addressing-thread-fix-017.md` - VERIFIED scanner API change that makes the current backlog status code stale.\n\n## Owner Decisions / Input\n",
      "path": "bridge/gtkb-discoverability-cli-status-scanner-api-regression-001.md",
      "verdict_line": "NEW",
      "version": 1
    }
  ]
}
```

File bridge scan contribution: 1 entry processed.
