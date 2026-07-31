NEW
::init gtkb lo
::open build

# Implementation Proposal — GFR Slice C Follow-up: Fix Broken CLI Flags + Missing Tests

bridge_kind: prime_proposal
Document: gtkb-gfr-slice-c-followup-fix-broken-flags
Version: 001
Date: 2026-07-21 UTC
author_identity: prime-builder/goose
author_harness_id: G
author_session_context_id: G-2026-07-21T08-15-00Z
author_model: GLM-5.2
author_model_version: GLM-5.2-2026
author_model_configuration: standard

Project Authorization: PAUTH-GFR-SLICE-C-FOLLOWUP-20260721
Project: PROJECT-GTKB-GOVERNANCE-FRICTION-REDUCTION
Work Item: WI-5647

target_paths: ["groundtruth-kb/src/groundtruth_kb/cli.py", "groundtruth-kb/src/groundtruth_kb/cli_backlog_add_work_item.py", "platform_tests/scripts/test_cli_projects_authorizations_covers_path.py", "platform_tests/scripts/test_cli_backlog_add_work_item_project_flag.py"]

Implementation proposal for GFR Slice C follow-up: fix two broken CLI flags and add the two missing test files.

## Claim

Slice C (WI-5645) was VERIFIED by the LO with a non-blocking note that two of three proposed test files were missing. Subsequent investigation by the PB revealed that the two features themselves are **not functional** — not merely untested:

1. **`--covers-path` (Finding 4.2): RUNTIME CRASH.** The `@click.option("--covers-path", ...)` decorator is present at line 6403 of `cli.py`, but the function signature `def projects_authorizations(ctx, project_id, include_terminal, json_output)` at line 6408 does **not** accept a `covers_path` parameter. Click passes the option as a keyword argument, which Python rejects with `TypeError: projects_authorizations() got an unexpected keyword argument 'covers_path'`. The command exits non-zero with no output.

2. **`--project` (Finding 2.6): SILENT NO-OP.** The `--project` option is accepted by `backlog_add_work_item` (line 4462) and passed to `AddWorkItemRequest.project_id` (line 4521). However, `add_work_item_with_test()` in `cli_backlog_add_work_item.py` (lines 277-363) **never reads `request.project_id`** — no `project_work_item_memberships` row is ever created. The WI is created successfully but the atomic project linkage promised by the proposal does not happen.

This proposal fixes both defects and adds the two missing test files that verify the fixes work correctly.

## Evidence

### `--covers-path` crash

```
$ python -c "from click.testing import CliRunner; from groundtruth_kb.cli import projects_cmd; r=CliRunner(); res=r.invoke(projects_cmd, ['authorizations', 'PROJECT-GTKB-GOVERNANCE-FRICTION-REDUCTION', '--covers-path', 'scripts/bridge_applicability_preflight.py']); print('exit:', res.exit_code); print('exc:', res.exception)"

exit: 1
exc: projects_authorizations() got an unexpected keyword argument 'covers_path'
```

Root cause: `cli.py:6408` — `def projects_authorizations(ctx, project_id, include_terminal, json_output)` missing `covers_path: str | None` parameter.

### `--project` no-op

```
$ python -m groundtruth_kb.cli backlog add-work-item ... --project PROJECT-GTKB-GOVERNANCE-FRICTION-REDUCTION
Created WI-5647 + TEST-11692 -> phase PHASE-001

$ python -c "from groundtruth_kb.db import KnowledgeDB; db=KnowledgeDB(db_path='groundtruth.db'); rows=db._get_conn().execute('SELECT project_id, work_item_id FROM project_work_item_memberships WHERE work_item_id = ?', ('WI-5647',)).fetchall(); print(rows)"
[]
```

Root cause: `cli_backlog_add_work_item.py:277-363` — `add_work_item_with_test()` never reads `request.project_id` after the WI+test+phase commit.

### LO Advisory

`bridge/gtkb-gfr-slice-c-missing-tests-001.md` — LO verified both files are MISSING. The advisory recommended creating the two test files. The investigation above revealed the scope is larger than the advisory anticipated: the features are broken, not just untested.

## Requirement Sufficiency

Existing requirements are sufficient. The fixes implement the features as originally proposed in `bridge/gtkb-gfr-slice-c-cli-affordances-001.md` — no new specifications or requirement changes are needed.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`:
- `groundtruth-kb/src/groundtruth_kb/cli.py` ✅
- `groundtruth-kb/src/groundtruth_kb/cli_backlog_add_work_item.py` ✅
- `platform_tests/scripts/test_cli_projects_authorizations_covers_path.py` ✅ (new test file)
- `platform_tests/scripts/test_cli_backlog_add_work_item_project_flag.py` ✅ (new test file)

## Specification Links

- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — this proposal cites all relevant governing specifications.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — defines who may author which status tokens.
- `GOV-12` — work-item test-spec requirement (relevant to `--project` flag atomicity).
- `GOV-13` — test-plan-phase assignment (relevant to test creation).
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — verification requires spec-to-test mapping; TEST-11692 covers the fixed CLI flags.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — this proposal includes the three mandatory header lines.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — all target paths are within the GT-KB root boundary.
- `GOV-STANDING-BACKLOG-001` — follow-up work item WI-5647 created under formal-artifact-approval DELIB-202667078.

## Prior Deliberations

- `DELIB-202667078` — Owner approval: Governance Friction Reduction program.
- `bridge/gtkb-gfr-slice-c-cli-affordances-001.md` — Original Slice C proposal (accepted, implemented, VERIFIED).
- `bridge/gtkb-gfr-slice-c-cli-affordances-004.md` — LO VERIFIED with non-blocking note about missing test files.
- `bridge/gtkb-gfr-slice-c-missing-tests-001.md` — LO advisory recommending follow-up WI for missing tests.

### Helper-suggested candidates

_No prior deliberations beyond those listed above._

## Owner Decisions / Input

- `DELIB-202667078` (AUQ GFR-PAUTH-001) — Owner answer: "1 - Yes, proceed". This approved the GFR program including follow-up work items.
- `PAUTH-GFR-SLICE-C-FOLLOWUP-20260721` — Active project authorization covering WI-5647.

## Cross-Harness Disposition

This proposal touches only `groundtruth-kb/src/` and `platform_tests/` files — no harness-surface files. No adapter regeneration is required.

| Harness | Surface | Parity Status | Disposition |
|---|---|---|---|
| All harnesses | `groundtruth-kb/src/` (platform code) | N/A — platform code | Changes are to platform CLI, not harness-surface files. |

**No typed waiver required.** No downstream adapter regeneration needed.

## Proposed Scope

### Fix 1 — `--covers-path` function signature + filtering logic

**File:** `groundtruth-kb/src/groundtruth_kb/cli.py`

The `projects_authorizations` function signature at line 6408 must accept `covers_path: str | None`. When `covers_path` is set:

1. Classify the path using `classify_target` from `groundtruth_kb.governance.project_authorization_operation_time`
2. For each PAUTH in the list, parse `allowed_mutation_classes` (already parsed by `_row_to_dict` into `allowed_mutation_classes_parsed`)
3. Filter to PAUTHs where the path's mutation class is in the PAUTH's allowed classes
4. If no PAUTHs match, print: `"No active project authorization covers path: <path>"`
5. This works with both `--json` and default output

### Fix 2 — `--project` project linkage in `add_work_item_with_test`

**File:** `groundtruth-kb/src/groundtruth_kb/cli_backlog_add_work_item.py`

After the WI+test+phase commit succeeds (line 344), if `request.project_id` is set:
1. Use `db.link_project_work_item(project_id, work_item_id, changed_by, change_reason, ...)` — the same function called by `gt projects add-item`
2. This insert is outside the WI+test+phase transaction (which has already committed). If the linkage fails, the WI still exists (fail-open for WI, fail-loud for linkage — per the original proposal's design).
3. Return the project linkage result in the response dict.

### Test 1 — `test_cli_projects_authorizations_covers_path.py`

**File:** `platform_tests/scripts/test_cli_projects_authorizations_covers_path.py` (new)

Tests:
1. `--covers-path` filters to PAUTHs whose `allowed_mutation_classes` cover the path's mutation class (e.g., `scripts/foo.py` → `source`, matches PAUTH with `["source", "test"]`)
2. Returns empty result with clear message when no PAUTH covers the path (e.g., `bridge/foo-001.md` → `bridge`, no match when PAUTH only has `["source", "test"]`)
3. Works with `--json` output

### Test 2 — `test_cli_backlog_add_work_item_project_flag.py`

**File:** `platform_tests/scripts/test_cli_backlog_add_work_item_project_flag.py` (new)

Tests:
1. `--project` flag creates a `project_work_item_memberships` row linking the new WI to the specified project
2. Without `--project`, no project membership is created (backward compat)
3. Error handling when project id is invalid (WI still created, error reported)

## Intuitiveness / Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "Bug fixes for broken CLI flags + missing test files",
  "provenance": "LO advisory gtkb-gfr-slice-c-missing-tests-001; owner decision DELIB-202667078",
  "canonical_authority": "cli.py; cli_backlog_add_work_item.py",
  "primary_route": "fix: add missing function parameter, add missing project linkage write, add test files",
  "before_behavior": "--covers-path crashes; --project is a silent no-op",
  "after_behavior": "--covers-path filters correctly; --project creates project_members row",
  "self_descriptive_naming": "unchanged from original Slice C proposal",
  "obsolete_guidance_disposition": "no existing guidance is superseded",
  "history_preservation": "no existing artifacts are deleted or rewritten",
  "baseline": "existing tests + ruff check + ruff format --check",
  "expected_result": "all tests pass, ruff clean, CLI flags work correctly",
  "rollback": "revert the commit; no data migration or state change",
  "hard_invariants": "GOV-12/GOV-13 chain intact; PAUTH grant is not automated; existing commands unchanged",
  "fail_closed_conditions": "--covers-path is read-only; --project fails loud on linkage error but WI persists",
  "essential_context_preservation": "all changes are durable code artifacts (CLI, tests)"
}
```

## Specification-Derived Verification Plan

| Specification | Test or Verification Command | Executed | Result |
|---|---|---|---|
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Visual inspection of spec links | yes | (pending) |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `python -m pytest platform_tests/scripts/test_cli_projects_authorizations_covers_path.py platform_tests/scripts/test_cli_backlog_add_work_item_project_flag.py -q --tb=short` | (pending) | (pending) |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Verify proposal author identity | yes | (pending) |
| `GOV-12` | Verify TEST-11692 exists and is linked to WI-5647 | yes | (pending) |
| `GOV-13` | Verify TEST-11692 is assigned to PHASE-001 | yes | (pending) |

## Acceptance Criteria

1. `gt projects authorizations <PROJECT_ID> --covers-path <path>` filters to PAUTHs covering the path's mutation class without crashing.
2. `gt projects authorizations <PROJECT_ID> --covers-path <path> --json` emits valid JSON of filtered results.
3. When no PAUTH covers the path, a clear message is printed: "No active project authorization covers path: <path>".
4. `gt backlog add-work-item --project <PROJECT_ID> ...` creates a `project_work_item_memberships` row linking the new WI.
5. `gt backlog add-work-item` without `--project` is backward-compatible (no membership created).
6. New test files pass.
7. All existing tests pass.
8. `ruff check` and `ruff format --check` pass on modified files.
9. No existing governance gate is weakened or removed.

## Risks / Rollback

- **Risk: `--covers-path` classifier mismatch** — the `classify_target` function may classify a path differently than expected. Mitigation: use the same `classify_target` function used by the implementation authorization system.
- **Risk: `--project` linkage after commit** — the project linkage happens after the WI+test+phase commit. If the linkage fails, the WI exists without a project link. Mitigation: report the error clearly; the WI is still usable, and `gt projects add-item` can be run manually.
- **Rollback:** Revert the commit. No data migration. All changes are additive CLI fixes and tests.

## Files Expected To Change

- `groundtruth-kb/src/groundtruth_kb/cli.py` — add `covers_path` parameter to `projects_authorizations`, add filtering logic
- `groundtruth-kb/src/groundtruth_kb/cli_backlog_add_work_item.py` — add `project_members` insert after WI+test+phase commit
- `platform_tests/scripts/test_cli_projects_authorizations_covers_path.py` — new test file
- `platform_tests/scripts/test_cli_backlog_add_work_item_project_flag.py` — new test file

## Recommended Commit Type

`fix`

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
