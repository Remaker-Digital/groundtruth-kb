NEW
author_identity: Codex
author_harness_id: A
author_session_context_id: 019ebc0a-181f-7791-a64b-482f97486014
author_model: gpt-5
author_model_version: gpt-5
author_model_configuration: Codex Desktop; interactive; Prime Builder via ::init gtkb pb
author_metadata_source: corrected from live Codex session role marker and CODEX_THREAD_ID

# Implementation Report - FAB-18 Backlog Dignity

bridge_kind: implementation_report
Document: gtkb-fab-18-backlog-dignity
Version: 005 (post-implementation report)
Author: Prime Builder (Codex, harness A)
Date: 2026-06-12 UTC
Implements: `bridge/gtkb-fab-18-backlog-dignity-003.md` per GO at `bridge/gtkb-fab-18-backlog-dignity-004.md`.
Recommended commit type: fix:

## Summary

FAB-18 is implemented across its three approved areas:

1. HYG-015 advisory drain: advisory deliberations were harvested before bulk closing old routing WIs, old routing WIs were closed in GOV-15-sized batches, and a 60-day router retention policy now prevents historical advisories from refilling the intake.
2. HYG-065 backlog-health recalibration: doctor warnings now fire for implementation-active uncovered work items, while unapproved/future WIs are counted separately; startup backlog metrics now report implementation-active work instead of future backlog volume.
3. HYG-060 IPA reorganization: root report/evidence files moved to `CODEX-INSIGHT-DROPBOX/`; scratch/render directories moved to `archive/fab-18-ipa-root-reorg/`; a move manifest records every source and destination.

No canonical specification or Deliberation Archive rows were deleted. Report relocation was archive-not-delete / move-not-delete.

## Specification Links

Carried forward from the approved proposal and GO:

- `GOV-STANDING-BACKLOG-001`
- `SPEC-DA-HARVEST-INCLUSION`
- `GOV-15`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `GOV-SESSION-SELF-INITIALIZATION-001`
- `GOV-ARTIFACT-APPROVAL-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`

## Implementation Evidence

### Area 1 - HYG-015 Advisory Drain

- Added `config/governance/advisory-routing-retention.toml` with `[advisory_router.retention].max_advisory_age_days = 60`.
- Updated `scripts/advisory_backlog_router.py` to load the retention policy by default, skip advisory candidates older than the cutoff, report `skipped_expired_count`, and expose `--include-expired` for explicit bypass.
- Ran DA harvest dry run and apply:
  - Dry-run summary: `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/fab-18-da-harvest-dry-run-summary.json`.
  - Formal approval packet: `.groundtruth/formal-artifact-approvals/fab-18-da-harvest-advisory-reports.json`.
  - Apply summary: `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/fab-18-da-harvest-apply-summary.json`.
  - Apply result: `applied=true`, `source_type_counts={lo_review: 775, bridge_thread: 718}`, `new_inserts=2`, `skipped_existing=1491`, `warning_count=74`.
- Closed old advisory-routing WIs after DA harvest:
  - Inventory: `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/fab-18-routing-wi-close-inventory.json`.
  - Dry run: `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/fab-18-routing-wi-close-dry-run.json`.
  - Apply summary: `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/fab-18-routing-wi-close-apply-summary.json`.
  - Dry-run result: `candidate_count=651`, `validated_count=651`, `batch_count=14`, `batch_size_limit=50`, `errors=[]`, `owner_approved=true`.
  - Apply result: `updated_count=651`, `batch_errors=[]`, `post_apply_routing_wi_total=780`, `post_apply_resolved_resolved_count=665`, `post_apply_open_routing_count=115`, `post_apply_recent_open_count=110`, `post_apply_unknown_date_open_count=5`, `old_open_before_cutoff_after_apply=0`.

### Area 2 - HYG-065 Backlog-Health / Startup Metrics

- Updated `groundtruth-kb/src/groundtruth_kb/project/doctor.py`:
  - Added implementation-active classification based on `approval_state`, `resolution_status`, and `stage`.
  - Changed orphaned-WI WARN generation to warn only for implementation-active uncovered WIs.
  - Added `non_implementation_uncovered_count` summary data for future/unapproved uncovered WIs.
- Updated `scripts/session_self_initialization.py`:
  - Added implementation-active backlog classification.
  - Changed `active_item_count` and top-item selection to implementation-active work.
  - Added `visible_non_terminal_item_count` and `non_implementation_future_item_count`.
- Added targeted coverage in `platform_tests/scripts/test_fab18_backlog_dignity.py` and extended existing router/startup tests.

### Area 3 - HYG-060 IPA Reorganization

- Moved 73 root files from `independent-progress-assessments/` to `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/`.
- Moved 11 scratch/render directories from `independent-progress-assessments/` to `archive/fab-18-ipa-root-reorg/`.
- Added provenance manifest: `independent-progress-assessments/fab-18-ipa-reorg-move-manifest.md`.
- Verified the manifest contains 84 move rows and every destination exists while every listed source path is absent.
- Post-move IPA root contains the three retained guide/log files plus this manifest:
  - `KNOWLEDGE-MIKE.md`
  - `KNOWLEDGE-PROJECT.md`
  - `LOYAL-OPPOSITION-LOG.md`
  - `fab-18-ipa-reorg-move-manifest.md`

### Protected Organize Rule Disposition

The GO scope included `.claude/rules/prompt-organize-reports-in-dropbox.md` for an allowlist refresh. Implementation inspection found that this active rule file no longer exists; FAB-05 had already archived it at `independent-progress-assessments/archive/cursor-legacy/prompt-organize-reports-in-dropbox.md`.

FAB-18 therefore did not recreate or edit that retired Cursor-era rule, and no narrative approval packet was generated for the absent active path. Recreating it would have reversed prior archival rather than refreshing a live artifact.

## Spec-Derived Test Plan And Results

| Requirement | Evidence / Command | Result |
|---|---|---|
| HYG-015 / `SPEC-DA-HARVEST-INCLUSION` / `GOV-15`: harvest before bulk close; close old routing WIs through bounded batches | DA apply summary and routing dry-run/apply summaries listed above | PASS |
| HYG-015: router age-out bounds future candidate staging | `python -m pytest platform_tests/scripts/test_advisory_backlog_router.py ...` includes `test_router_retention_policy_skips_expired_advisories` | PASS |
| HYG-065 / `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`: unapproved/future uncovered WIs do not WARN; implementation-active uncovered WIs do WARN | `platform_tests/scripts/test_fab18_backlog_dignity.py` | PASS |
| HYG-065 / `GOV-SESSION-SELF-INITIALIZATION-001`: startup backlog metric reflects implementation-active work | `test_backlog_metrics_counts_only_implementation_active_items` | PASS |
| HYG-060: moved files/directories preserve provenance and are listed in manifest | Manifest sanity check: `manifest_rows=84`, `missing_destinations=0`, `still_at_source=0` | PASS |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`: focused regression and formatting gates pass | pytest, ruff check, ruff format check | PASS |

Commands run:

```powershell
python -m pytest platform_tests/scripts/test_advisory_backlog_router.py platform_tests/scripts/test_fab18_backlog_dignity.py platform_tests/scripts/test_session_self_initialization.py::test_recommender_3_unmapped_work_item_treated_as_active platform_tests/scripts/test_session_self_initialization.py::test_backlog_metrics_counts_only_implementation_active_items -q --tb=short
```

Result: `15 passed in 5.09s`.

```powershell
python -m ruff check scripts/advisory_backlog_router.py scripts/session_self_initialization.py groundtruth-kb/src/groundtruth_kb/project/doctor.py platform_tests/scripts/test_advisory_backlog_router.py platform_tests/scripts/test_fab18_backlog_dignity.py platform_tests/scripts/test_session_self_initialization.py
```

Result: `All checks passed!`.

```powershell
python -m ruff format --check scripts/advisory_backlog_router.py scripts/session_self_initialization.py groundtruth-kb/src/groundtruth_kb/project/doctor.py platform_tests/scripts/test_advisory_backlog_router.py platform_tests/scripts/test_fab18_backlog_dignity.py platform_tests/scripts/test_session_self_initialization.py
```

Result: `6 files already formatted`.

Manifest sanity check result:

```json
{
  "manifest_rows": 84,
  "missing_destinations": 0,
  "still_at_source": 0
}
```

## Files Changed

Focused FAB-18 implementation surfaces:

| Path | Change |
|---|---|
| `config/governance/advisory-routing-retention.toml` | CREATE: 60-day advisory-router retention config |
| `scripts/advisory_backlog_router.py` | UPDATE: retention policy, expired-skip accounting, `--include-expired` |
| `groundtruth-kb/src/groundtruth_kb/project/doctor.py` | UPDATE: implementation-active PAUTH coverage warning calibration |
| `scripts/session_self_initialization.py` | UPDATE: implementation-active backlog metrics |
| `platform_tests/scripts/test_advisory_backlog_router.py` | UPDATE: retention and compact-result assertions |
| `platform_tests/scripts/test_fab18_backlog_dignity.py` | CREATE: doctor backlog-health calibration tests |
| `platform_tests/scripts/test_session_self_initialization.py` | UPDATE: startup metric tests |
| `.groundtruth/formal-artifact-approvals/fab-18-da-harvest-advisory-reports.json` | CREATE: formal packet for DA harvest apply |
| `groundtruth.db` | UPDATE: DA harvest inserts and routing-WI resolution updates |
| `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/fab-18-*.json` | CREATE/MOVE: FAB-18 evidence summaries |
| `independent-progress-assessments/fab-18-ipa-reorg-move-manifest.md` | CREATE: move manifest |
| `archive/fab-18-ipa-root-reorg/` | CREATE: archive destination for moved scratch/render directories |
| `bridge/gtkb-fab-18-backlog-dignity-005.md` | CREATE: this implementation report |
| `bridge/INDEX.md` | UPDATE: `NEW` entry for this implementation report |

Notes for reviewer:

- The checkout had unrelated dirty changes before this FAB-18 work. The report above names the focused FAB-18 surfaces only.
- `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/*` is git-ignored by default. Some moved destinations therefore appear as ignored local files unless staged with `git add -f`; the manifest records the actual local destinations for verification.

## Acceptance Criteria Status

1. Area 1: DA harvest applied; old routing-WI batch dry run validated 651 candidates; apply updated 651 routing WIs; no old-open-before-cutoff candidates remain. PASS.
2. Area 2: doctor warning calibration and startup active-count metrics implemented with targeted tests. PASS.
3. Area 3: IPA root reorg performed by move/archive, manifest written and verified; active organize-rule target was already archived and was not recreated. PASS with documented disposition.
4. Tests and formatting: focused pytest, ruff check, and ruff format check pass. PASS.

## Loyal Opposition Verification Requests

1. Confirm the DA harvest and routing-WI closure evidence satisfies harvest-first and GOV-15 dry-run/batch constraints.
2. Confirm the HYG-065 recalibration matches the PAUTH model: future/unapproved uncovered WIs are summary data, not WARNs; implementation-active uncovered WIs still WARN.
3. Confirm the HYG-060 move manifest preserves provenance and that no moved artifact was deleted.
4. Confirm the protected organize-rule disposition is acceptable given the active target file had already been archived by FAB-05.

## Copyright

Copyright (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
