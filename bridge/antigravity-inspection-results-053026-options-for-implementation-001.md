ADVISORY
author_identity: Codex Loyal Opposition
author_harness_id: A
author_session_context_id: S053026-antigravity-advisory-consolidation
author_model: GPT-5 Codex
author_model_version: gpt-5-codex
author_model_configuration: Codex desktop default reasoning, advisory triage and bridge verification

bridge_kind: governance_advisory
Document: antigravity-inspection-results-053026-options-for-implementation
Version: 001
Author: Loyal Opposition (Codex, harness A)
Date: 2026-05-30 UTC

# ANTIGRAVITY INSPECTION RESULTS - 053026 - OPTIONS FOR IMPLEMENTATION

## Source

Owner request on 2026-05-30: review open advisory proposals, incorporate valid contents into existing known work items where appropriate, and consolidate remaining verified and appropriate work into a fresh advisory proposal.

Source materials reviewed:

- `bridge/gtkb-antigravity-implements-link-ambiguity-advisory-001.md`
- `bridge/gtkb-antigravity-insight-stale-owner-action-advisory-001.md`
- `bridge/gtkb-lo-hourly-quality-scout-advisory-004.md` as the latest hourly scout advisory thread version
- `bridge/gtkb-owner-role-switch-codex-loyal-opposition-001.md`
- `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-05-30-05-04.md`
- Live `bridge/INDEX.md`
- Live MemBase `current_work_items`
- Live verification commands listed in the Evidence Commands section

## Claim

Four live ADVISORY bridge threads were reviewed against the current bridge index, MemBase `current_work_items`, and live verification commands. Valid contents were incorporated into existing known work items where an appropriate owner existed. Remaining verified and appropriate work is consolidated here as advisory implementation options for Prime Builder disposition.

This advisory is non-dispatchable. It does not grant implementation authority by itself. Prime Builder should convert chosen options through normal bridge proposals, AUQs, or project-authorized work as applicable.

## Owner Decision Needed

None for this advisory disposition.

Future implementation may require owner decisions only where the normal governance path requires them, especially the one-at-a-time AUQs for implements-link ambiguity in `WI-3471` and any decision to create a new work item for assertion path scoping, public API type drift, or dashboard test environment repair.

## Recommended Prime Action

1. Treat this advisory as a disposition packet, not an implementation approval.
2. Continue existing known work items that were updated in MemBase.
3. Convert only the selected remaining options into normal bridge proposals, project-authorized work, or one-at-a-time AUQs.
4. Do not spawn duplicate work for exclusions called out below.

## Classification Slot

- Classification: advisory-disposition and implementation-options consolidation.
- Dispatchability: Axis-2 non-dispatchable ADVISORY.
- Primary owners: Prime Builder for future conversion proposals; owner only for future AUQs or explicit scope choices.
- Related work items: `WI-3471`, `WI-3473`, `WI-3308`, `WI-3268`, `WI-3502`, `WI-3459`, `WI-3498`, `WI-3478`, `WI-3479`, `WI-3480`, `WI-3457`, `WI-3483`, `WI-3484`, `WI-3504`, `WI-3305`.

## Source Advisories Reviewed

| Source | Existing routed WI | Disposition |
|---|---:|---|
| `bridge/gtkb-antigravity-implements-link-ambiguity-advisory-001.md` | `WI-3504` | Triaged; valid AUQ guidance incorporated into `WI-3471`; stale single-project claim superseded by live report. |
| `bridge/gtkb-antigravity-insight-stale-owner-action-advisory-001.md` | `WI-3484` | Triaged; stale formatter warning closed by `WI-3473`; live ambiguity concern incorporated into `WI-3471`. |
| `bridge/gtkb-lo-hourly-quality-scout-advisory-004.md` | `WI-3457` | Triaged; contents incorporated into `WI-3308`, `WI-3268`, `WI-3502`, `WI-3459`, and `WI-3498`. |
| `bridge/gtkb-owner-role-switch-codex-loyal-opposition-001.md` | `WI-3305` | Audit evidence only; no implementation proposal or owner action remains. |
| `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-05-30-05-04.md` | `WI-3483` | Triaged as source advisory evidence; relevant parts incorporated or excluded as stale. |

## Work Items Updated

| Work item | Update made |
|---|---|
| `WI-3471` | Updated title, priority, description, status detail, and bridge links for current implements-link ambiguity Phase 3. Live report now shows `CLEAN=10`, `AMBIGUOUS=6`, `UNADDRESSED=11`, not the stale one-project or five-project counts. |
| `WI-3473` | Resolved as completed by `bridge/gtkb-ruff-format-pre-file-gate-010.md` VERIFIED; stale owner-action warning should not create duplicate work. |
| `WI-3308` | Expanded with LO file-safety false-positive repair requirement for read-only commands whose text contains comparison-like tokens. |
| `WI-3268` | Expanded with bridge proposal/report lint patterns for bare `pytest` and Unix-only command forms in Windows GT-KB verification reports. |
| `WI-3502` | Expanded with source-of-truth freshness and dashboard/startup underreporting evidence. |
| `WI-3459` | Expanded with live harness registry drift: two undeclared Claude skills in parity check output. |
| `WI-3498` | Updated title, priority, and description with current `groundtruth-kb` ruff drift evidence. |
| `WI-3478` | Resolved after `bridge/gtkb-interactive-session-role-override-slice-8-parity-check-resolution-table-017.md` VERIFIED. |
| `WI-3479` | Updated status detail: latest live bridge state is NO-GO at `bridge/gtkb-interactive-session-role-override-slice-9-rule-claude-agents-updates-006.md`. |
| `WI-3480` | Updated status detail: latest live bridge state is GO at `bridge/gtkb-interactive-session-role-override-slice-10-regression-tests-006.md`. |
| `WI-3457`, `WI-3483`, `WI-3484`, `WI-3504`, `WI-3305` | Resolved as advisory-routing/disposition work after incorporation or explicit exclusion. |

## Verified Implementation Options

### Option 1 - Implements-link ambiguity Phase 3 (`WI-3471`)

Current live evidence from `python scripts/backfill_implements_links.py --report` supersedes prior advisory counts:

```text
CLEAN=10  AMBIGUOUS=6  UNADDRESSED=11  total=27
```

Ambiguous projects/items now requiring one-at-a-time owner AUQs:

- `PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY`: `WI-AUTO-SPEC-BRIDGE-MODE-CONFIG-TRANSACTIONS-001`
- `PROJECT-GTKB-DETERMINISTIC-SERVICES-001`: `WI-3261`, `WI-3262`, `WI-3263`
- `PROJECT-GTKB-GOVERNANCE-HARDENING`: `GTKB-GOV-CODE-QUALITY-BASELINE`, `WI-3308`
- `PROJECT-GTKB-INTERACTIVE-SESSION-ROLE-OVERRIDE`: `WI-3474`
- `PROJECT-GTKB-LO-ADVISORY-INTAKE`: `WI-3303`
- `PROJECT-GTKB-RELIABILITY-FIXES`: `WI-3398`, `WI-3423`

Recommended conversion: Prime Builder proposal for Phase 3 AUQ-by-AUQ resolution. Do not use the stale bundled owner-decision table as authority.

### Option 2 - LO file-safety false-positive repair (`WI-3308`)

The hourly scout advisory and this review both reproduced the class: read-only shell probes can be blocked when the command text contains comparison-like tokens even when no file mutation is intended. The implementation target should preserve LO write protection while making read-only probes quote-aware and target-aware.

Recommended conversion: focused governance-hardening proposal for the LO file-safety hook, with tests proving that true writes remain blocked while read-only `rg`, `Select-String`, `Get-Content`, `git status`, and `git diff --name-only` patterns pass.

### Option 3 - Bridge command-pattern lint (`WI-3268`)

Slice 9 and Slice 10 review churn showed recurring proposal/report command defects: bare `pytest` instead of the repo interpreter and Unix-only `grep | head` command forms in a Windows GT-KB workspace. These are predictable enough for a pre-filing lint.

Recommended conversion: extend the existing proposal-pattern lint surface to catch non-workspace-valid verification commands before filing.

### Option 4 - Source-of-truth counter freshness (`WI-3502`)

The advisory evidence remains appropriate: startup/dashboard/cached surfaces can underreport live bridge or MemBase state unless counters cite their read source and compare against live authorities. Related known work includes `WI-3500`, `WI-3489`, and `WI-3503`.

Recommended conversion: audit and repair cached/snapshot surfaces with source-explicit counters and live bridge/MemBase comparison checks.

### Option 5 - Harness capability registry drift (`WI-3459`)

Live `python scripts/check_harness_parity.py --all --markdown` returned WARN with two undeclared skills:

```text
.claude/skills/gtkb-hygiene-sweep/SKILL.md
.claude/skills/loyal-opposition-hygiene-assessment/SKILL.md
```

Recommended conversion: update `config/agent-control/harness-capability-registry.toml` through the governed skill/registry adapter path.

### Option 6 - Current ruff cleanup (`WI-3498`)

Live `groundtruth-kb` checks found current cleanup work remains:

```text
ruff check .: 3 issues
ruff format --check .: 44 files would be reformatted
```

Recommended conversion: focused cleanup or commit-handoff prep that runs both lint and format gates before declaring commit-ready. This is distinct from `WI-3473`, which is already verified as the pre-file ruff-format gate.

### Option 7 - Assertion path scoping architecture debt (new conversion candidate)

Read-only assertion-run sampling found substantial failing assertion history and examples whose paths no longer exist, such as `src/multi_tenant/auth.py` tied to multiple specs. This supports a future assertion-triage or assertion-runner scoping task, but no existing exact work item owner was confirmed during this advisory pass.

Recommended conversion: either attach to the assertion-triage project after owner confirmation or create a new scoped WI for stale assertion path handling.

### Option 8 - Public API type-check drift (new conversion candidate)

Targeted public API tests produced 34 passes and 1 failing strict mypy test. Observed errors:

```text
src/groundtruth_kb/config.py:229: Argument 1 to Path has incompatible type object
src/groundtruth_kb/cli.py:558: Module groundtruth_kb.backlog has no attribute migrate_work_list_items
src/groundtruth_kb/cli.py:558: Module groundtruth_kb.backlog has no attribute parse_work_list_file
```

Recommended conversion: focused public API type-surface repair. The broader 27-failure advisory claim was not reproduced in this pass and should not be copied as fact without a fresh full run.

### Option 9 - Dashboard test environment or timeout issue (new conversion candidate)

The targeted dashboard subject-selector test did not reach the reported timeout behavior. Current first failure is an import error:

```text
ModuleNotFoundError: No module named 'yaml'
```

Recommended conversion: first reproduce under the intended environment, then decide whether the real work is dependency wiring, timeout handling, or both.

### Option 10 - Interactive role override continuation (`WI-3479`, `WI-3480`)

Live bridge state after this advisory pass:

- Slice 8 (`WI-3478`) is VERIFIED at `-017` and the WI was resolved.
- Slice 9 (`WI-3479`) is latest NO-GO at `-006`; Prime Builder revision needed.
- Slice 10 (`WI-3480`) is latest GO at `-006`; implementation/report cycle remains.

Recommended conversion: Prime Builder should continue the live Slice 9 and Slice 10 bridge threads directly rather than spawning duplicate advisory work.

## Exclusions

- The stale formatter owner-action warning is excluded because `WI-3473` is resolved by `gtkb-ruff-format-pre-file-gate-010.md` VERIFIED.
- The stale claim that only one ambiguous implements-link project remains is excluded because live `backfill_implements_links.py --report` reports six ambiguous projects.
- The bundled owner-decision table pattern is excluded; owner AUQs must be one decision at a time.
- The owner-role-switch advisory is retained as audit history only and should not produce implementation work by itself.

## Evidence Commands

```text
python scripts/backfill_implements_links.py --report
python scripts/check_harness_parity.py --all --markdown
groundtruth-kb/.venv/Scripts/ruff.exe check .
groundtruth-kb/.venv/Scripts/ruff.exe format --check .
groundtruth-kb/.venv/Scripts/python.exe -m pytest tests/test_managed_registry.py tests/test_scaffold_skills.py tests/test_public_api_type_checks.py -q --tb=short
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_dashboard_subject_selector.py -q --tb=short
python scripts/advisory_backlog_router.py equivalent dry-run via import, source=bridge
```

## Copyright

Copyright 2026 Remaker Digital, a DBA of VanDusen and Palmeter, LLC. All rights reserved.
