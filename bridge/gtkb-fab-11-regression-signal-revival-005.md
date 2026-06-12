NEW
author_identity: Codex Prime Builder
author_harness_id: A
author_session_context_id: 019ebc0a-181f-7791-a64b-482f97486014
author_model: GPT-5 Codex coding agent
author_model_version: GPT-5 family; exact runtime build not exposed in session context
author_model_configuration: Codex desktop session; Prime Builder override; approval_policy=never
author_metadata_source: Codex Prime Builder session; .gtkb-state/bridge-author-metadata/current.json

# GT-KB Bridge Implementation Report - gtkb-fab-11-regression-signal-revival - 005

bridge_kind: implementation_report
Document: gtkb-fab-11-regression-signal-revival
Version: 005 (NEW; post-implementation report)
Responds to GO: bridge/gtkb-fab-11-regression-signal-revival-004.md
Approved proposal: bridge/gtkb-fab-11-regression-signal-revival-003.md
Recommended commit type: feat:

## Implementation Claim

FAB-11 is implemented inside the approved target paths. The implementation revives regression signal quality by:

1. Repairing the stale Agent Red assertion corpus: 210 critical/verified specs were re-versioned to point at `applications/Agent_Red/*`; 1,162 non-critical Agent-Red-era specs were retired as app-scoped history with machine assertions cleared.
2. Preserving a deterministic remediation tool at `scripts/fab11_assertion_corpus_remediation.py`; the post-apply planner reports zero remaining stale Agent Red `File not found` candidates.
3. Amending `GOV-12` and `GOV-13` with formal approval packets so repository-native pytest files/execution output can be treated as governed verification evidence while historical MemBase `tests` rows remain provenance only.
4. Migrating `kpi_spec_test_mapping` and the M16/M17/M18 helpers in `groundtruth-kb/src/groundtruth_kb/db.py` so stale or `historical_agent_red` test rows no longer count as live evidence.
5. Adding governed `pipeline_events` retention config and tooling, pruning old `assertion_run` telemetry, retaining an in-root pre-VACUUM DB snapshot, and recording post-retention evidence.
6. Clarifying `CLAUDE.md` to say the Claude SessionStart assertion hook is registered in the Claude hook surface; `.codex/hooks.json` was not modified because it is outside this FAB-11 authorization packet's `target_paths`.

## Specification Links

- `SPEC-1662` / GOV-18 - assertion quality: stale false-positive assertions are no longer counted as active regression failures.
- `GOV-08` - MemBase/root `groundtruth.db` remains the source of truth; DB mutations used `KnowledgeDB` append-only APIs except the explicit approved view migration and operational telemetry pruning.
- `GOV-12` / `GOV-13` - amended by formal packets to recognize pytest evidence and scope historical tests-table rows.
- `GOV-15` - bulk stale-path assertion disposition ran under the approved FAB-11 GOV-15 authorization packet, not ad hoc test fixing.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - rewritten critical paths target `applications/Agent_Red/*`.
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` - remediation, evidence scoping, and retention are deterministic scripts.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - this report is filed through the live bridge.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - links carried forward from the approved proposal and mapped here.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - verification below is derived from the linked requirements.
- `GOV-STANDING-BACKLOG-001` - work is scoped to WI-4423 / PROJECT-FABLE-INVESTIGATION under `PAUTH-FAB11-20260610`.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` / `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - governance changes were preserved as scripts, config, packets, and bridge evidence.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - concrete artifact changes triggered durable script/config/spec-packet/bridge-report preservation.

## Owner Decisions / Input

No new owner decision is required by this implementation report. Implementation used existing owner authorization:

- `PAUTH-FAB11-20260610`
- `DELIB-FAB11-REMEDIATION-20260610B`
- GO verdict: `bridge/gtkb-fab-11-regression-signal-revival-004.md`

## Prior Deliberations

- `bridge/gtkb-fab-11-regression-signal-revival-003.md` - approved implementation proposal.
- `bridge/gtkb-fab-11-regression-signal-revival-004.md` - Loyal Opposition GO verdict.

## Specification-Derived Verification Plan

| Spec / governing surface | Executed verification evidence |
| --- | --- |
| `SPEC-1662` / GOV-18 | `python scripts\fab11_assertion_corpus_remediation.py --format json` before apply reported 1,372 candidates, 210 rewrites, 1,162 retirements, zero unresolved; post-apply and post-sweep reruns reported zero candidates. |
| `GOV-08` | Live DB probes showed `historical_agent_red_tests=8168`, `old_pass_fail_tests=0`, live KPI row `total=988`, `mapped=420`, `unmapped=568`, `42.51012145748988%`. |
| `GOV-12` / `GOV-13` | `python scripts\fab11_pytest_evidence_contract.py --apply --format json` amended 2 specs, wrote 2 formal packets, scoped 8,168 historical tests, and migrated the KPI view. Packet validation returned true for both GOV packets. |
| `GOV-15` | `python scripts\implementation_authorization.py begin --bridge-id gtkb-fab-11-regression-signal-revival` was activated before live DB/script mutations. The apply output recorded 210 rewrites and 1,162 retirements under the FAB-11 bridge id. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Assertion remediation rewrites only current assertion file targets that still equal stale prefixes, converting them to `applications/Agent_Red/<old-path>`; test coverage verifies `json_path.path` expressions are not rewritten as file paths. |
| `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` | Added deterministic scripts for assertion corpus remediation, pytest evidence contract migration, and retention pruning; `python -m py_compile` passed for all three scripts. |
| Retention requirement | Dry-run found 3,321,409 old `assertion_run` rows; apply deleted 3,321,409, VACUUM ran, DB shrank from 1,500,364,800 bytes to 182,763,520 bytes immediately after apply, and post dry-run reported zero prune candidates. |
| Hook registration / narrative accuracy | `.claude/settings.json` already registers `python .claude/hooks/assertion-check.py`; `CLAUDE.md` now accurately scopes this as the Claude SessionStart hook. Narrative approval packet `2026-06-12-fab11-claude-md-sessionstart-hook.json` validates against final content. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Targeted pytest/ruff/py_compile commands below passed; live assertion sweep recorded fresh post-repair evidence: 2,319 total specs, 533 with assertions, 388 passed, 145 failed, 1,786 skipped. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | This report will be filed as `bridge/gtkb-fab-11-regression-signal-revival-005.md`; the bridge helper inserts the matching `NEW` row at the top of the `bridge/INDEX.md` document entry without deleting or rewriting prior bridge versions. |

## Commands Run

- `python -m pytest platform_tests\scripts\test_fab11_regression_signal_revival.py -q --tb=short --basetemp=.gtkb-state\pytest-tmp-fab11` - 4 passed.
- `python -m py_compile scripts\fab11_assertion_corpus_remediation.py scripts\fab11_pytest_evidence_contract.py scripts\fab11_pipeline_events_retention.py` - passed.
- `python -m ruff check scripts\fab11_assertion_corpus_remediation.py scripts\fab11_pytest_evidence_contract.py scripts\fab11_pipeline_events_retention.py platform_tests\scripts\test_fab11_regression_signal_revival.py groundtruth-kb\src\groundtruth_kb\db.py` - all checks passed.
- `python -m ruff format --check scripts\fab11_assertion_corpus_remediation.py scripts\fab11_pytest_evidence_contract.py scripts\fab11_pipeline_events_retention.py platform_tests\scripts\test_fab11_regression_signal_revival.py groundtruth-kb\src\groundtruth_kb\db.py` - 5 files already formatted.
- `python scripts\fab11_assertion_corpus_remediation.py --format json` - pre-apply 1,372 candidates; post-apply/post-sweep zero candidates.
- `python scripts\fab11_assertion_corpus_remediation.py --apply --format json` - applied 210 rewrites and 1,162 retirements.
- `python scripts\fab11_assertion_corpus_remediation.py --run-assertions --format json` - fresh assertion sweep recorded 388 passed, 145 failed, 1,786 skipped.
- `python scripts\fab11_pytest_evidence_contract.py --format json` - pre-apply 8,168 historical tests planned; post-apply zero planned.
- `python scripts\fab11_pytest_evidence_contract.py --apply --format json` - amended 2 specs, scoped 8,168 historical tests, migrated view.
- `python scripts\fab11_pipeline_events_retention.py --format json` - pre-apply 3,321,409 prune candidates; post-apply zero prune candidates.
- `python scripts\fab11_pipeline_events_retention.py --apply --format json` - deleted 3,321,409 rows and VACUUMed.
- `python scripts\assertion_categorize.py --dry-run --format json` - completed; counts: chronic_noise 1390, healthy 1176, uncategorized 48, flaky/genuine_drift 0.

## Observed Results

- Assertion corpus remediation:
  - Rewritten: 210
  - Retired/app-scoped history: 1,162
  - Skipped: 0
  - Unresolved critical paths: 0
  - Post-remediation FAB-11 stale-path planner candidates: 0
- Pytest evidence contract:
  - `GOV-12` and `GOV-13` updated with approval packets:
    - `.groundtruth/formal-artifact-approvals/2026-06-12-fab11-gov-12-pytest-evidence.json`
    - `.groundtruth/formal-artifact-approvals/2026-06-12-fab11-gov-13-pytest-evidence.json`
  - Historical Agent Red tests table rows: 8,168
  - Remaining old pre-May `pass`/`fail` rows: 0
  - Live KPI after migration: 988 active specs, 420 mapped, 568 unmapped, 42.51012145748988%.
- Retention:
  - Deleted `assertion_run` telemetry rows: 3,321,409
  - Remaining `assertion_run` telemetry rows after follow-up verification activity: 169,514
  - `groundtruth.db` size after follow-up checks: 185,851,904 bytes
  - Retained pre-VACUUM snapshot: `groundtruth.db.pre-backfill-fab11-vacuum-20260612T201233Z.bak` (1,500,364,800 bytes)
- Residual assertion status:
  - Fresh full assertion sweep still has 145 failing specs. Those are outside this FAB-11 stale Agent Red path class; the FAB-11 planner remains zero.

## Files Changed

- `groundtruth.db`
- `groundtruth.db.pre-backfill-fab11-vacuum-20260612T201233Z.bak`
- `.groundtruth/formal-artifact-approvals/2026-06-12-fab11-gov-12-pytest-evidence.json`
- `.groundtruth/formal-artifact-approvals/2026-06-12-fab11-gov-13-pytest-evidence.json`
- `.groundtruth/formal-artifact-approvals/2026-06-12-fab11-claude-md-sessionstart-hook.json`
- `scripts/fab11_assertion_corpus_remediation.py`
- `scripts/fab11_pytest_evidence_contract.py`
- `scripts/fab11_pipeline_events_retention.py`
- `config/governance/pipeline-events-retention.toml`
- `groundtruth-kb/src/groundtruth_kb/db.py`
- `CLAUDE.md`
- `platform_tests/scripts/test_fab11_regression_signal_revival.py`

## Acceptance Criteria Status

- [x] HYG-029 hybrid stale-path assertion repair implemented.
- [x] Critical/verified assertions rewritten to `applications/Agent_Red/*` where the moved path exists.
- [x] Non-critical Agent-Red-era requirement assertions retired/app-scoped.
- [x] `scripts/assertion_categorize.py --dry-run --format json` rerun after remediation.
- [x] HYG-044 Claude SessionStart hook state verified in `.claude/settings.json`.
- [x] `CLAUDE.md` wording corrected to actual Claude hook surface; Codex hook parity deferred because `.codex/hooks.json` is outside target paths.
- [x] HYG-030 GOV-12/GOV-13 amended with formal approval packets.
- [x] Historical MemBase test rows scoped to Agent Red history.
- [x] KPI view and M16/M17/M18 helpers exclude stale/historical Agent Red rows from live evidence.
- [x] HYG-014 retention TOML and retention script added.
- [x] Root DB snapshot created before VACUUM and retained in-root.
- [x] Old `assertion_run` pipeline telemetry pruned and VACUUMed.
- [x] Targeted regression tests added and passed.

## Risk And Rollback

Risk is moderate because `groundtruth.db` was intentionally mutated at scale. Rollback path is the retained in-root pre-VACUUM snapshot `groundtruth.db.pre-backfill-fab11-vacuum-20260612T201233Z.bak` plus append-only DB version history for spec/test rows. For code/config rollback, revert the FAB-11 scripts, test, `db.py` KPI changes, `CLAUDE.md` wording, and retention TOML. Bridge files remain append-only.

Residual known limitation: Codex hook parity was not changed because `.codex/hooks.json` is not included in FAB-11 `target_paths`. A follow-up bridge should handle Codex SessionStart assertion parity if desired.

## Loyal Opposition Asks

1. Verify that the stale Agent Red path false-positive class is eliminated by the planner-zero evidence and fresh assertion sweep.
2. Verify that GOV-12/GOV-13 packeted amendments and historical test scoping satisfy the pytest-as-evidence contract.
3. Verify retention pruning/snapshot/VACUUM evidence and confirm the retained in-root DB snapshot is acceptable.
