REVISED
author_identity: prime-builder/codex-automation
author_harness_id: A
author_session_context_id: 019ef4ff-74fc-7a30-8d05-5994ac4fd565
author_model: gpt-5-codex
author_model_version: 2026-06-23
author_model_configuration: Codex desktop automation session after crash resume; approval_policy=never; autonomous Prime Builder

# Revised Implementation Report - Orphan-WI Per-Item Retire/Exclude Service

bridge_kind: implementation_report
Document: gtkb-orphan-wi-backfill-per-wi-retire-exclude-service
Version: 007
Responds-To: bridge/gtkb-orphan-wi-backfill-per-wi-retire-exclude-service-006.md
Supersedes: bridge/gtkb-orphan-wi-backfill-per-wi-retire-exclude-service-005.md

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-NONFASTLANE-BATCH-2026-06-21
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-3464

target_paths: ["groundtruth-kb/src/groundtruth_kb/project/lifecycle.py", "groundtruth-kb/src/groundtruth_kb/cli.py", "platform_tests/scripts/test_projects_cli.py"]

Recommended commit type: feat

## Revision Summary

This bridge-only revision corrects the report linkage defect found in `bridge/gtkb-orphan-wi-backfill-per-wi-retire-exclude-service-006.md`.

No source, test, script, database, or live deferred-action file changed in this revision. The approved implementation remains the existing local commit:

```text
ef45ce5e4 feat: add governed project retire-item command
```

The prior `-005` implementation report was substantively about the same implementation, but it did not carry forward the full mandatory specification surface. Review-time applicability preflight therefore failed on the operative report. This revision carries forward the approved proposal and GO specification links explicitly, preserves the source/test verification evidence, and requests Loyal Opposition re-verification against the corrected implementation report artifact.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - this revised report is filed through the canonical bridge file chain after a latest `NO-GO`; Loyal Opposition must verify against the current status-bearing bridge entry.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - the report preserves the durable artifact graph by linking the approved implementation commit, target paths, owner/project authorization, and spec-derived verification evidence in one self-contained bridge artifact.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this revised report carries forward every relevant governing specification from the approved proposal and GO verdict, correcting the missing-linkage defect in version 005.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the verification table below maps the cited specification obligations to concrete tests and command evidence.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - the report carries Project Authorization, Project, Work Item, and target path linkage.
- `SPEC-AUQ-POLICY-ENGINE-001` - the retire/exclude decisions consumed by this surface require owner-decision provenance and packet-backed execution; the implementation preserves that provenance in `change_reason`.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - the implementation stays in the GT-KB platform package and platform tests; no `applications/` subtree is touched.
- `GOV-STANDING-BACKLOG-001` - WI-3464 is an open tracked standing-backlog item under `PROJECT-GTKB-RELIABILITY-FIXES`.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - the new `gt projects retire-item` CLI is harness-neutral and does not introduce Claude-only or Codex-only behavior.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - the retirement action is artifact-backed by append-only membership state plus a cited approval packet reference, rather than an implicit or unrecorded mutation.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - the implementation records a durable non-active lifecycle transition (`retired`) distinct from the benign `removed` detach state.
- `GOV-ARTIFACT-APPROVAL-001` - `retire_project_work_item()` refuses to execute without a valid in-root owner-approved packet cited in `change_reason`.

## Prior Deliberations

- `DELIB-2509` - owner AUQ selecting per-WI PAUTH plus assign-only scope for the parent orphan-WI backfill driver; retire/exclude execution was deferred to this follow-on slice.
- `DELIB-20265542` - Loyal Opposition NO-GO requiring exact approval-packet binding and narrowed deferred-action scope.
- `DELIB-20261478` and `DELIB-2631` - prior GO context for the orphan-WI membership backfill implementation lineage.
- `DELIB-20265457` - owner decision authorizing the `PROJECT-GTKB-RELIABILITY-FIXES` non-fast-lane proposal batch including WI-3464.
- `DELIB-20265569` - adjacent owner decision about VERIFIED-driven project lifecycle automation.

## Implementation Summary

The approved WI-3464 implementation is present in local commit `ef45ce5e4 feat: add governed project retire-item command`.

Implemented behavior:

- `ProjectLifecycleService.retire_project_work_item()` validates a cited approval packet path from `change_reason`, resolves it in-root, requires a schema-valid owner-approved packet, and binds the packet to the exact project, work item, lifecycle action, and requested non-active status before mutating membership state.
- `gt projects retire-item` exposes the governed service with `project_id`, `work_item_id`, `--status`, `--changed-by`, required packet-bearing `--change-reason`, and `--json`.
- `platform_tests/scripts/test_projects_cli.py` covers valid exact-match execution, mismatched packet rejection, missing/invalid/out-of-root packet refusal, idempotent non-active lifecycle behavior, and owner-decision provenance in `change_reason`.

No canonical live drain of `.gtkb-state/orphan-wi-discovery/<run-id>/deferred_actions.json` was performed. No `groundtruth.db` mutation was performed. No edit to `scripts/resolve_orphan_wi_memberships.py` was performed.

## Scope Evidence

The approved target paths and explicitly out-of-scope drain/data paths remain clean in the handoff context:

```text
git diff --name-only -- groundtruth-kb\src\groundtruth_kb\project\lifecycle.py groundtruth-kb\src\groundtruth_kb\cli.py platform_tests\scripts\test_projects_cli.py scripts\resolve_orphan_wi_memberships.py groundtruth.db
git diff --cached --name-only -- groundtruth-kb\src\groundtruth_kb\project\lifecycle.py groundtruth-kb\src\groundtruth_kb\cli.py platform_tests\scripts\test_projects_cli.py scripts\resolve_orphan_wi_memberships.py groundtruth.db
```

Both commands produced no output when the implementation report was filed. The current bridge-only revision does not alter those paths.

## Specification-Derived Verification

| Spec / obligation | Evidence | Result |
| --- | --- | --- |
| `GOV-ARTIFACT-APPROVAL-001` exact owner-approval binding | `test_retire_item_executes_with_exact_matching_approval_packet`; `test_retire_item_rejects_mismatched_approval_packet`; `test_retire_item_refuses_missing_invalid_or_out_of_root_packet` | PASS |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` append-only non-active lifecycle state | `test_retire_item_idempotent_and_distinct_from_removed` | PASS |
| `SPEC-AUQ-POLICY-ENGINE-001` owner-decision provenance preservation | `test_retire_item_change_reason_carries_owner_decision_reference` | PASS |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` in-root platform placement | implementation commit path set is limited to `groundtruth-kb/src/...` and `platform_tests/...`; no `applications/` path was touched | PASS |
| `GOV-FILE-BRIDGE-AUTHORITY-001` bridge-authorized target surface | latest GO approved the declared target paths; this revision only corrects bridge report evidence after a NO-GO | PASS |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` mandatory spec linkage | this revised report carries all proposal/GO specification links, including the four required specs missing from version 005 | PASS |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` report verification floor | this table maps each cited implementation obligation to concrete tests and command evidence | PASS |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` and `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` durable artifact trail | owner/project authorization, implementation commit, target paths, tests, and bridge revision are linked in this report | PASS |

## Verification Commands

Previously observed implementation checks from the superseded report remain the implementation evidence:

```text
$env:TMP='E:\GT-KB\.tmp'; $env:TEMP='E:\GT-KB\.tmp'; groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests\scripts\test_projects_cli.py -q --tb=short --basetemp .tmp\pytest-wi3464-auto-builder
```

Result: `14 passed, 1 warning in 13.86s`.

```text
groundtruth-kb\.venv\Scripts\python.exe -m ruff check groundtruth-kb\src\groundtruth_kb\project\lifecycle.py groundtruth-kb\src\groundtruth_kb\cli.py platform_tests\scripts\test_projects_cli.py
groundtruth-kb\.venv\Scripts\python.exe -m ruff format --check groundtruth-kb\src\groundtruth_kb\project\lifecycle.py groundtruth-kb\src\groundtruth_kb\cli.py platform_tests\scripts\test_projects_cli.py
```

Result: `All checks passed!`; `3 files already formatted`.

Corrective bridge-report preflights on this revised content:

```text
python scripts\bridge_applicability_preflight.py --content-file .gtkb-state\bridge-revisions\drafts\gtkb-orphan-wi-backfill-per-wi-retire-exclude-service-007.md
```

Observed result:

```text
preflight_passed: true
missing_required_specs: []
missing_advisory_specs: []
```

```text
python scripts\adr_dcl_clause_preflight.py --content-file .gtkb-state\bridge-revisions\drafts\gtkb-orphan-wi-backfill-per-wi-retire-exclude-service-007.md
```

Observed result:

```text
must_apply: 4, may_apply: 1, not_applicable: 0
Evidence gaps in must_apply clauses: 0
Blocking gaps (gate-failing): 0
Exit: 0
```

## Out Of Scope

- No deferred-action drain was executed.
- No data migration or live `groundtruth.db` write was executed.
- No `scripts/resolve_orphan_wi_memberships.py` edit was made.
- No application/adopter subtree was touched.
- No source/test implementation change was made after commit `ef45ce5e4`.

## Verification Request

Loyal Opposition should verify WI-3464 against commit `ef45ce5e4`, this corrected self-contained specification linkage, and the preserved source/test evidence above. The specific NO-GO issue from version 006 should now be rechecked by running the mandatory applicability and clause preflights against this revised report.
