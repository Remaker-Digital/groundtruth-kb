REVISED

bridge_kind: implementation_report
Document: gtkb-fab-11-regression-signal-revival
Version: 007
Responds-To: bridge/gtkb-fab-11-regression-signal-revival-006.md
Author: prime-builder (Claude Opus 4.8, harness B) — interactive owner session
Date: 2026-06-12

Project: PROJECT-FABLE-INVESTIGATION
Work Item: WI-4423
Project Authorization: PAUTH-FAB11-20260610

author_identity: prime-builder
author_harness_id: B
author_session_context_id: 0f59a219-caee-4943-be84-23ec6ada1d07
author_model: claude-opus-4-8
author_model_version: 4.8
author_model_configuration: interactive owner session, ::init gtkb pb, 1m context

target_paths: ["groundtruth.db", "scripts/fab11_assertion_corpus_remediation.py", "scripts/fab11_pytest_evidence_contract.py", "scripts/fab11_pipeline_events_retention.py", "config/governance/pipeline-events-retention.toml", "groundtruth-kb/src/groundtruth_kb/db.py", "CLAUDE.md", "platform_tests/scripts/test_fab11_regression_signal_revival.py", ".groundtruth/formal-artifact-approvals/2026-06-12-fab11-*.json"]

KB mutation: groundtruth.db IS in target_paths. MemBase mutations performed by the original implementation (assertion corpus remediation, GOV-12/GOV-13 amendments, KPI view migration, pipeline_events retention pruning).

---

# FAB-11 — Regression Signal Revival — REVISED Post-Implementation Report (v007)

Implements the GO'd proposal `bridge/gtkb-fab-11-regression-signal-revival-003.md` (GO at `-004`). This REVISED report carries forward the substantive implementation evidence from `-005` (authored by Codex Prime Builder, harness A) and addresses the single finding in the NO-GO at `-006`.

## Revision Scope

Addresses the P1 finding from `bridge/gtkb-fab-11-regression-signal-revival-006.md` (NO-GO):

**P1 — Required approval packets are ignored and untracked:** The three FAB-11 approval packets existed on disk but were ignored by `.gitignore:551` (the `.groundtruth/` blanket pattern) and were not tracked by git. This repeats the same durability class previously blocked in FAB-07 and FAB-14.

**Resolution:** All three packets have been force-added to git staging:

```
git add -f .groundtruth/formal-artifact-approvals/2026-06-12-fab11-gov-12-pytest-evidence.json
git add -f .groundtruth/formal-artifact-approvals/2026-06-12-fab11-gov-13-pytest-evidence.json
git add -f .groundtruth/formal-artifact-approvals/2026-06-12-fab11-claude-md-sessionstart-hook.json
```

Staged-state verification:

```
git status --short -- .groundtruth/formal-artifact-approvals/2026-06-12-fab11*
A  .groundtruth/formal-artifact-approvals/2026-06-12-fab11-claude-md-sessionstart-hook.json
A  .groundtruth/formal-artifact-approvals/2026-06-12-fab11-gov-12-pytest-evidence.json
A  .groundtruth/formal-artifact-approvals/2026-06-12-fab11-gov-13-pytest-evidence.json
```

All three packets now show status `A` (staged new file), confirming they are durable in the commit candidate. No source code, test, or implementation changes were required for this revision.

## Bridge Protocol Compliance

This report is filed at `bridge/gtkb-fab-11-regression-signal-revival-007.md` with a matching `REVISED:` line inserted at the top of the `gtkb-fab-11-regression-signal-revival` document entry in `bridge/INDEX.md`. All prior versions (`-001` through `-006`) remain on disk per bridge append-only protocol.

## Implementation Claim (carried forward from -005)

FAB-11 is implemented inside the approved target paths. The implementation revives regression signal quality by:

1. Repairing the stale Agent Red assertion corpus: 210 critical/verified specs were re-versioned to point at `applications/Agent_Red/*`; 1,162 non-critical Agent-Red-era specs were retired as app-scoped history with machine assertions cleared.
2. Preserving a deterministic remediation tool at `scripts/fab11_assertion_corpus_remediation.py`; the post-apply planner reports zero remaining stale Agent Red `File not found` candidates.
3. Amending `GOV-12` and `GOV-13` with formal approval packets so repository-native pytest files/execution output can be treated as governed verification evidence while historical MemBase `tests` rows remain provenance only.
4. Migrating `kpi_spec_test_mapping` and the M16/M17/M18 helpers in `groundtruth-kb/src/groundtruth_kb/db.py` so stale or `historical_agent_red` test rows no longer count as live evidence.
5. Adding governed `pipeline_events` retention config and tooling, pruning old `assertion_run` telemetry, retaining an in-root pre-VACUUM DB snapshot, and recording post-retention evidence.
6. Clarifying `CLAUDE.md` to say the Claude SessionStart assertion hook is registered in the Claude hook surface; `.codex/hooks.json` was not modified because it is outside this FAB-11 authorization packet's `target_paths`.

## Specification Links

- `SPEC-1662` / GOV-18 — assertion quality: stale false-positive assertions are no longer counted as active regression failures.
- `GOV-08` — MemBase/root `groundtruth.db` remains the source of truth; DB mutations used `KnowledgeDB` append-only APIs except the explicit approved view migration and operational telemetry pruning.
- `GOV-12` / `GOV-13` — amended by formal packets to recognize pytest evidence and scope historical tests-table rows.
- `GOV-15` — bulk stale-path assertion disposition ran under the approved FAB-11 GOV-15 authorization packet, not ad hoc test fixing.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — rewritten critical paths target `applications/Agent_Red/*`.
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` — remediation, evidence scoping, and retention are deterministic scripts.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — this report is filed through the live bridge at `bridge/gtkb-fab-11-regression-signal-revival-007.md` with a matching entry in `bridge/INDEX.md`.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — links carried forward from the approved proposal and mapped here.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — verification below is derived from the linked requirements.
- `GOV-STANDING-BACKLOG-001` — work is scoped to WI-4423 / PROJECT-FABLE-INVESTIGATION under `PAUTH-FAB11-20260610`.
- `GOV-ARTIFACT-APPROVAL-001` — all three formal approval packets are force-added to git staging (see Revision Scope).
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` / `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — governance changes preserved as scripts, config, packets, and bridge evidence.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — concrete artifact changes triggered durable script/config/spec-packet/bridge-report preservation.

## Owner Decisions / Input

No new owner decision is required by this implementation report. Implementation used existing owner authorization:

- `PAUTH-FAB11-20260610`
- `DELIB-FAB11-REMEDIATION-20260610B`
- GO verdict: `bridge/gtkb-fab-11-regression-signal-revival-004.md`

The owner's 2026-06-12 standing auto-approve-inline authorization governs the approval-packet force-add.

## Prior Deliberations

- `bridge/gtkb-fab-11-regression-signal-revival-003.md` — approved implementation proposal.
- `bridge/gtkb-fab-11-regression-signal-revival-004.md` — Loyal Opposition GO verdict.
- `bridge/gtkb-fab-11-regression-signal-revival-005.md` — original implementation report (Codex Prime Builder, harness A).
- `bridge/gtkb-fab-11-regression-signal-revival-006.md` — Loyal Opposition NO-GO (single P1: approval packets gitignored).

## Specification-Derived Verification Plan

| Spec / governing surface | Executed verification evidence |
| --- | --- |
| `SPEC-1662` / GOV-18 | `python scripts/fab11_assertion_corpus_remediation.py --format json` post-apply: candidates=0, rewrite_planned=0, retire_planned=0, unresolved=0 |
| `GOV-08` | Live DB probes showed `historical_agent_red_tests=8168`, `old_pass_fail_tests=0`, live KPI total=988, mapped=420, unmapped=568, 42.51% |
| `GOV-12` / `GOV-13` | `python scripts/fab11_pytest_evidence_contract.py --format json` post-apply: historical_tests_planned=0; packets validated |
| `GOV-15` | Implementation authorization activated before live DB/script mutations |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Assertion remediation rewrites target `applications/Agent_Red/*`; test verifies json_path.path expressions are not rewritten as file paths |
| `DELIB-S312` | Added deterministic scripts; `python -m py_compile` passed for all three |
| Retention | `python scripts/fab11_pipeline_events_retention.py --format json` post-apply: prune_candidates=0 |
| Hook registration | `.claude/settings.json` registers `python .claude/hooks/assertion-check.py`; CLAUDE.md corrected |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Targeted pytest/ruff/py_compile commands below passed |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Filed at `bridge/gtkb-fab-11-regression-signal-revival-007.md` with INDEX update |
| `GOV-ARTIFACT-APPROVAL-001` (revision) | Three packets force-added: `git status --short` shows `A` (staged) for all three |

## Commands Run (carried forward from -005, revalidated by -006 LO)

```
python -m pytest platform_tests/scripts/test_fab11_regression_signal_revival.py -q --tb=short --basetemp=.gtkb-state/pytest-tmp-fab11-lo
  -> 4 passed in 1.47s

python -m py_compile scripts/fab11_assertion_corpus_remediation.py scripts/fab11_pytest_evidence_contract.py scripts/fab11_pipeline_events_retention.py
  -> passed

python -m ruff check scripts/fab11_assertion_corpus_remediation.py scripts/fab11_pytest_evidence_contract.py scripts/fab11_pipeline_events_retention.py platform_tests/scripts/test_fab11_regression_signal_revival.py groundtruth-kb/src/groundtruth_kb/db.py
  -> All checks passed!

python -m ruff format --check scripts/fab11_assertion_corpus_remediation.py scripts/fab11_pytest_evidence_contract.py scripts/fab11_pipeline_events_retention.py platform_tests/scripts/test_fab11_regression_signal_revival.py groundtruth-kb/src/groundtruth_kb/db.py
  -> 5 files already formatted

python scripts/fab11_assertion_corpus_remediation.py --format json
  -> candidates=0, rewrite_planned=0, retire_planned=0, unresolved=0

python scripts/fab11_pytest_evidence_contract.py --format json
  -> historical_tests_planned=0, KPI total=988, mapped=420, unmapped=568, 42.51%

python scripts/fab11_pipeline_events_retention.py --format json
  -> prune_candidates=0, event_type_total=173360, total=185636, db_bytes=188088320

python scripts/check_narrative_artifact_evidence.py --paths CLAUDE.md --json
  -> status: pass

git status --short -- .groundtruth/formal-artifact-approvals/2026-06-12-fab11*
  -> A  .groundtruth/formal-artifact-approvals/2026-06-12-fab11-claude-md-sessionstart-hook.json
     A  .groundtruth/formal-artifact-approvals/2026-06-12-fab11-gov-12-pytest-evidence.json
     A  .groundtruth/formal-artifact-approvals/2026-06-12-fab11-gov-13-pytest-evidence.json
```

## Observed Results (carried forward from -005)

- Assertion corpus remediation: 210 rewritten, 1,162 retired, 0 unresolved; post-remediation planner: 0 candidates.
- Pytest evidence contract: GOV-12 and GOV-13 amended; 8,168 historical test rows scoped; KPI: 988 total, 420 mapped.
- Retention: 3,321,409 old assertion_run rows deleted; VACUUM applied; retained snapshot at `groundtruth.db.pre-backfill-fab11-vacuum-20260612T201233Z.bak` (1,500,364,800 bytes).
- Residual: 145 failing specs remain but are outside the FAB-11 stale Agent Red path class.

## Files Changed

- `groundtruth.db` — assertion corpus remediation, GOV-12/GOV-13 amendments, KPI view migration, retention pruning
- `groundtruth.db.pre-backfill-fab11-vacuum-20260612T201233Z.bak` — pre-VACUUM snapshot
- `.groundtruth/formal-artifact-approvals/2026-06-12-fab11-gov-12-pytest-evidence.json` — GOV-12 approval packet (**force-added to git**)
- `.groundtruth/formal-artifact-approvals/2026-06-12-fab11-gov-13-pytest-evidence.json` — GOV-13 approval packet (**force-added to git**)
- `.groundtruth/formal-artifact-approvals/2026-06-12-fab11-claude-md-sessionstart-hook.json` — CLAUDE.md narrative approval packet (**force-added to git**)
- `scripts/fab11_assertion_corpus_remediation.py` — deterministic remediation planner/applier
- `scripts/fab11_pytest_evidence_contract.py` — pytest evidence contract migration
- `scripts/fab11_pipeline_events_retention.py` — pipeline events retention pruner
- `config/governance/pipeline-events-retention.toml` — retention config
- `groundtruth-kb/src/groundtruth_kb/db.py` — KPI view migration, M16/M17/M18 helpers
- `CLAUDE.md` — SessionStart hook registration narrative correction
- `platform_tests/scripts/test_fab11_regression_signal_revival.py` — spec-derived tests (4)

## Acceptance Criteria Status

- [x] HYG-029 hybrid stale-path assertion repair implemented.
- [x] Critical/verified assertions rewritten to `applications/Agent_Red/*`.
- [x] Non-critical Agent-Red-era requirement assertions retired/app-scoped.
- [x] HYG-044 Claude SessionStart hook state verified.
- [x] CLAUDE.md wording corrected to actual Claude hook surface.
- [x] HYG-030 GOV-12/GOV-13 amended with formal approval packets.
- [x] Historical MemBase test rows scoped to Agent Red history.
- [x] KPI view and M16/M17/M18 helpers exclude stale/historical rows.
- [x] HYG-014 retention TOML and retention script added.
- [x] Root DB snapshot created before VACUUM and retained in-root.
- [x] Old assertion_run pipeline telemetry pruned and VACUUMed.
- [x] Targeted regression tests added and passed.
- [x] (v007) All three approval packets force-added to git staging — durable in commit candidate.

## Recommended Commit Type

`feat:` — net-new deterministic scripts (assertion corpus remediation, pytest evidence contract, pipeline events retention), GOV-12/GOV-13 amendments, KPI view migration, and retention infrastructure.

## Requirement Sufficiency

Existing requirements sufficient. All acceptance criteria from the GO at `-004` are covered by the tests and formal approval packets. The revision addresses only the approval-packet durability finding from the NO-GO at `-006`; no new requirements were needed.

## Risk And Rollback

Risk is moderate because `groundtruth.db` was mutated at scale. Rollback path: the retained in-root pre-VACUUM snapshot plus append-only DB version history for spec/test rows. For code/config rollback, revert the FAB-11 scripts, test, db.py KPI changes, CLAUDE.md wording, and retention TOML. Bridge files remain append-only.
