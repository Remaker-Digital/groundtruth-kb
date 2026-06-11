NEW

bridge_kind: implementation_report
Document: gtkb-fab-21-startup-load-cost-reduction
Version: 005
Responds-To: bridge/gtkb-fab-21-startup-load-cost-reduction-004.md
Author: prime-builder (Claude Opus 4.8, harness B) — interactive owner session
Date: 2026-06-11

Project: PROJECT-FABLE-INVESTIGATION
Work Item: WI-4433
Project Authorization: PAUTH-FAB21-20260610

author_identity: prime-builder
author_harness_id: B
author_session_context_id: ad3221a1-e3bc-4d3e-bcec-d3d608598322
author_model: claude-opus-4-8
author_model_version: 4.8
author_model_configuration: interactive owner session, ::init gtkb pb

target_paths: ["scripts/session_self_initialization.py", "platform_tests/scripts/test_fab21_rules_payload_profile.py"]

# FAB-21 — Startup Load-Cost Reduction — Post-Implementation Report (HYG-025 Slice 1: Rules-Payload Profiler Baseline)

## Implementation Summary

This report covers **HYG-025 slice 1 only**: the rules-payload profiler baseline
(the proposal's "4360 profiler" step) — the sequencing-first action the owner
mandated ("Land the 4360 profiler baseline first") in
`DELIB-FAB21-REMEDIATION-20260610`, before any glossary restructure. Committed at
`522b7872` (`feat:`).

The profiler makes the always-loaded `.claude/rules/*.md` payload — the
~336 KB / 34%-over-budget startup cost identified in HYG-025 — a visible, tracked
metric in every startup report.

Implemented in `scripts/session_self_initialization.py`:

- `RULES_PAYLOAD_BYTES_PER_TOKEN` constant (rough token-estimation heuristic; the
  byte total and file count are exact).
- `_rules_payload_profile(project_root)`: globs `.claude/rules/*.md`, sums exact
  bytes (reusing `_file_size_profile`), estimates tokens, computes the overage vs
  `STARTUP_PRUNING_TOTAL_WARN_BYTES` (250 KB), and returns
  file_count / total_bytes / estimated_tokens / over_budget / overage_bytes /
  overage_pct / largest_files.
- `rules_payload` key added to `_startup_pruning_scan`'s return.
- A baseline line rendered in `_render_startup_pruning`.

Test added: `platform_tests/scripts/test_fab21_rules_payload_profile.py` (7 tests).

## Scope (this slice vs remaining FAB-21)

In scope (this report): HYG-025 slice 1 — profiler baseline (source + test only;
no protected-narrative edit, no MemBase write, no config change).

Explicitly NOT in this slice (subsequent reports): the HYG-025 glossary
core/detail IA + dedup + era-file archival; the HYG-028 stale-pointer sweep; the
HYG-008 measure-first duration log + PostToolUse consolidation. The HYG-025/028
protected `.claude/rules/*.md` edits each require their per-file
narrative-approval packet at implementation time; those are owner-gated
subsequent slices.

## Specification Links

Carried forward from the GO'd `-003` proposal; scoped to what this measurement
slice exercises:

- `DCL-SESSION-STARTUP-TOKEN-BUDGET-001` — the startup token budget the rules
  payload exceeds; the profiler measures it against the 250 KB budget.
- `GOV-SESSION-SELF-INITIALIZATION-001` — requires startup token-reduction
  options; the profiler is the measurement foundation those options need.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — all changes in-root (`scripts/`,
  `platform_tests/`).
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — specs cited.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — spec-to-test mapping +
  execution evidence below.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — filed under `bridge/` with a live INDEX
  entry; append-only.
- `GOV-08` — this slice writes no MemBase and no `canonical-terminology.toml`
  change (deferred to later slices).
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` / `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` /
  `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — durable-artifact lifecycle governance for
  this bridge report and the profiler artifact (advisory).
- Deferred to later slices (cited for continuity, not exercised here):
  `GOV-GLOSSARY-AS-DA-READ-SURFACE-001` (glossary IA),
  `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` (HYG-028 sweep),
  `GOV-17` (HYG-008 hook consolidation).

## Prior Deliberations

- `DELIB-FAB21-REMEDIATION-20260610` — the 3 owner AUQ dispositions; this slice
  implements the HYG-025 "profiler baseline first" sequencing decision.
- `DELIB-FABLE-GRILL-20260610-Q1` — project chartering.
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` — recurring fixed token costs are
  a defect to engineer out; the profiler makes the cost visible and trackable.
- `bridge/gtkb-fab-21-startup-load-cost-reduction-003.md` (REVISED) — the GO'd
  proposal this report implements (slice 1).
- `bridge/gtkb-fab-21-startup-load-cost-reduction-004.md` (GO) — Loyal Opposition
  (Antigravity, harness C) approval.

## Owner Decisions / Input

This implementation is authorized by the bridge `GO` at `-004` plus the owner
sequencing dispositions captured via `AskUserQuestion` on 2026-06-10 and
persisted to `DELIB-FAB21-REMEDIATION-20260610`, which fixed HYG-025 as
"Full program, sequenced — land the profiler baseline FIRST." This slice
implements exactly that first step. The owner's 2026-06-11 interactive direction
(AskUserQuestion this session) to drain a low-collision FAB cluster authorized
proceeding with the source-only slice. No new owner decision is required for this
measurement-only slice; the protected-narrative slices that follow each require
their per-file narrative-approval packets.

## Spec-to-Test Mapping

| Specification / requirement | Test(s) | Executed | Result |
|---|---|---|---|
| `DCL-SESSION-STARTUP-TOKEN-BUDGET-001` (payload measured vs 250 KB budget) | `test_profile_sums_bytes_and_estimates_tokens`, `test_profile_under_budget`, `test_profile_over_budget` | yes | PASS |
| `GOV-SESSION-SELF-INITIALIZATION-001` (baseline surfaced in startup scan/report) | `test_startup_pruning_scan_includes_rules_payload`, `test_render_startup_pruning_includes_baseline_line` | yes | PASS |
| Fail-soft + correctness edge cases (empty dir, sorting/cap, non-.md exclusion) | `test_profile_empty_rules_dir`, `test_profile_largest_files_sorted_and_capped` | yes | PASS |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` (in-root) | target_paths inspection (`scripts/`, `platform_tests/`) | yes | PASS |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | full table above + ruff check/format below | yes | PASS |

## Verification Commands and Results

```powershell
groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests\scripts\test_fab21_rules_payload_profile.py platform_tests\scripts\test_session_self_initialization.py -q --tb=short
# test_fab21_rules_payload_profile.py: 7 passed
# overall: 2 failed, 71 passed in 209.20s

groundtruth-kb\.venv\Scripts\python.exe -m ruff check scripts\session_self_initialization.py platform_tests\scripts\test_fab21_rules_payload_profile.py
# All checks passed!

groundtruth-kb\.venv\Scripts\python.exe -m ruff format --check scripts\session_self_initialization.py platform_tests\scripts\test_fab21_rules_payload_profile.py
# 2 files already formatted
```

## Pre-Existing Failure Disclosure

The 2 failing tests are PRE-EXISTING and unrelated to this change:

- `test_startup_model_contains_role_governance_and_kpi_inventory` — `assert posture["package_version"]` → `None`.
- `test_dashboard_and_report_are_written_with_time_series_kpi` — `assert posture["upgrade_plan"]["available"] is True` → `False`.

Both assert against `posture` (the GT-KB infrastructure upgrade-posture probe:
package-version detection and upgrade-plan availability), a code path this change
does not touch. This slice modifies only `_startup_pruning_scan` /
`_render_startup_pruning` (additively) — and the 71 passing tests include the
startup-model tests that exercise the modified `_startup_pruning_scan`; a real
regression would have failed those too. These are environment-dependent failures
(the dev-environment inventory is stale and the package/upgrade-plan probe
returns None/False in this environment). They are out of scope for this slice and
not fixed here per GOV-07 (defects recorded, not fixed mid-implementation); they
warrant separate triage if not already tracked.

## Recommended Commit Type

`feat:` — this slice ADDS a new profiling capability (a function + render line +
test); it is the measurement foundation. The `perf:` cost-reduction recommended
for the overall FAB-21 proposal lands in the later glossary-IA / hook-consolidation
slices, not here. Committed as `feat:` at `522b7872`.

## Isolation Placement Compliance

All changes are in-root under `E:\GT-KB\`:
`scripts/session_self_initialization.py` and
`platform_tests/scripts/test_fab21_rules_payload_profile.py`. No `applications/`
subtree touched; no out-of-root artifact.

## Acceptance Criteria (this slice)

1. The profiler reports the `.claude/rules/*.md` payload byte/token total vs the
   250 KB budget — DONE, surfaced in `_startup_pruning_scan` + `_render_startup_pruning`.
2. New tests pass; `ruff check` and `ruff format --check` clean — DONE (7/7 new
   tests pass; ruff clean on both changed files).
3. No protected-narrative edit, no MemBase write, no config change in this slice
   — CONFIRMED.

## Commit / Bridge State Note

The implementation is committed at `522b7872` with explicit pathspec. This report
file (`-005`) is committed for durability; its INDEX `NEW` entry is added to the
live working-tree `bridge/INDEX.md` for Loyal Opposition to scan, but the INDEX
commit is intentionally deferred to avoid bundling concurrent Codex uncommitted
INDEX entries (a separate harness's in-flight bridge threads). The live INDEX is
the canonical queue per `GOV-FILE-BRIDGE-AUTHORITY-001`.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
