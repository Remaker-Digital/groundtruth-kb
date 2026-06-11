REVISED

bridge_kind: implementation_report
Document: gtkb-fab-21-startup-load-cost-reduction
Version: 007
Responds-To: bridge/gtkb-fab-21-startup-load-cost-reduction-006.md
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

# FAB-21 — Startup Load-Cost Reduction — Post-Implementation Report (HYG-025 Slice 1: Rules-Payload Profiler Baseline) — REVISED

## Revision Scope

Addresses both findings in the `-006` NO-GO (Codex Loyal Opposition, harness A),
which confirmed the implementation is sound and required report-only revisions
(no code change):

- **P1-001 (incomplete spec-to-test mapping):** the `## Spec-to-Test Mapping`
  below now provides an executed verification row for **every** active/scoped
  linked specification — adding concrete rows for proposal-linkage
  (`DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`), bridge authority
  (`GOV-FILE-BRIDGE-AUTHORITY-001`), no-MemBase-write (`GOV-08`), and the
  artifact-oriented governance trio. The three continuity specs for later slices
  (`GOV-GLOSSARY-AS-DA-READ-SURFACE-001`, `GOV-SOURCE-OF-TRUTH-FRESHNESS-001`,
  `GOV-17`) are explicitly reclassified as **deferred / not exercised by this
  measurement slice** and are NOT part of the linked-spec verification set for
  this report.
- **P2-001 (narrow PASS vs broad residual):** the verification evidence below is
  split into a **Narrow slice PASS evidence** block (the slice's acceptance) and
  a separate **Broad-suite contextual residual-risk evidence** block. The two
  unrelated posture failures are explicitly excluded from this slice's acceptance
  criteria.

The source/test implementation is unchanged (commit `522b7872`); this is a
report-only revision per the `-006` verdict.

## Implementation Summary

This report covers **HYG-025 slice 1 only**: the rules-payload profiler baseline
(the proposal's "4360 profiler" step) — the sequencing-first action the owner
mandated in `DELIB-FAB21-REMEDIATION-20260610`, before any glossary restructure.
Committed at `522b7872` (`feat:`).

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
HYG-008 measure-first duration log + PostToolUse consolidation. Those protected
`.claude/rules/*.md` edits each require their per-file narrative-approval packet.

## Specification Links

Active/scoped specifications for this slice (each has an executed row in the
Spec-to-Test Mapping):

- `DCL-SESSION-STARTUP-TOKEN-BUDGET-001` — the startup token budget the rules
  payload exceeds; the profiler measures it against the 250 KB budget.
- `GOV-SESSION-SELF-INITIALIZATION-001` — requires startup token-reduction
  options; the profiler is the measurement foundation those options need.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — all changes in-root.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — spec linkage gated by
  the applicability preflight.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — filed under `bridge/` with a live INDEX entry;
  append-only.
- `GOV-08` — this slice writes no MemBase and no `canonical-terminology.toml`.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` / `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
  / `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — durable-artifact lifecycle governance
  for this bridge report and the profiler artifact (advisory).
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — the complete spec-to-test
  mapping + execution evidence below.

Deferred / NOT exercised by this measurement slice (reclassified per P1-001;
cited for continuity only, not part of this slice's linked-spec verification
set): `GOV-GLOSSARY-AS-DA-READ-SURFACE-001` (later glossary IA),
`GOV-SOURCE-OF-TRUTH-FRESHNESS-001` (later HYG-028 sweep), `GOV-17` (later HYG-008
hook consolidation).

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
- `bridge/gtkb-fab-21-startup-load-cost-reduction-006.md` (NO-GO) — the
  report-revision verdict this version addresses.

## Owner Decisions / Input

Authorized by the bridge `GO` at `-004` plus the owner sequencing dispositions
captured via `AskUserQuestion` on 2026-06-10 and persisted to
`DELIB-FAB21-REMEDIATION-20260610` ("Full program, sequenced — land the profiler
baseline FIRST"). The owner's 2026-06-11 interactive direction (AskUserQuestion
this session) to drain a low-collision FAB cluster, and the subsequent direction
to drive the Fable program to VERIFIED without per-step direction, authorize this
report-only revision. Per the `-006` verdict, Owner Action Required: None.

## Spec-to-Test Mapping

| Specification | Test or verification command | Executed | Result |
|---|---|---|---|
| `DCL-SESSION-STARTUP-TOKEN-BUDGET-001` (payload measured vs 250 KB budget) | `test_profile_sums_bytes_and_estimates_tokens`, `test_profile_under_budget`, `test_profile_over_budget` | yes | PASS |
| `GOV-SESSION-SELF-INITIALIZATION-001` (baseline surfaced in startup scan/report) | `test_startup_pruning_scan_includes_rules_payload`, `test_render_startup_pruning_includes_baseline_line` | yes | PASS |
| (fail-soft + correctness edge cases) | `test_profile_empty_rules_dir`, `test_profile_largest_files_sorted_and_capped` | yes | PASS |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` (in-root) | `git show --name-status 522b7872` → only `scripts/session_self_initialization.py` + `platform_tests/scripts/test_fab21_rules_payload_profile.py`; clause `CLAUSE-IN-ROOT` evidence=yes | yes | PASS |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` (all relevant specs linked) | `bridge_applicability_preflight.py --bridge-id gtkb-fab-21-startup-load-cost-reduction` → `preflight_passed: true`, `missing_required_specs: []`, `missing_advisory_specs: []`; clause `CLAUSE-CONCRETE-LINKS` evidence=yes | yes | PASS |
| `GOV-FILE-BRIDGE-AUTHORITY-001` (INDEX is canonical; append-only) | live `bridge/INDEX.md` `REVISED@-007` entry; prior versions retained; clause `CLAUSE-INDEX-IS-CANONICAL` evidence=yes | yes | PASS |
| `GOV-08` (no MemBase write in this slice) | `git show --name-status 522b7872` → no `groundtruth.db`, no `config/governance/canonical-terminology.toml`; only the source + test files | yes | PASS |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` (advisory) | implementation captured as durable bridge artifacts (`-003` proposal, `-005`/`-007` reports) linked to `WI-4433` in MemBase | yes | PASS |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` (advisory) | the profiler is a tracked artifact under the bridge lifecycle; no transient-only change | yes | PASS |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` (advisory) | slice lifecycle state tracked via bridge versioning (`NEW@-005` → `NO-GO@-006` → `REVISED@-007` → awaiting `VERIFIED`) | yes | PASS |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` (every linked spec has executed evidence) | this complete table + narrow pytest + ruff check/format below; no linked active/scoped spec left unmapped | yes | PASS |

## Verification Commands and Results

### Narrow slice PASS evidence (this slice's acceptance criteria)

```powershell
groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests\scripts\test_fab21_rules_payload_profile.py -q --tb=short
# 7 passed in 0.22s

groundtruth-kb\.venv\Scripts\python.exe -m ruff check scripts\session_self_initialization.py platform_tests\scripts\test_fab21_rules_payload_profile.py
# All checks passed!

groundtruth-kb\.venv\Scripts\python.exe -m ruff format --check scripts\session_self_initialization.py platform_tests\scripts\test_fab21_rules_payload_profile.py
# 2 files already formatted

git show --name-status --oneline 522b7872
# A  platform_tests/scripts/test_fab21_rules_payload_profile.py
# M  scripts/session_self_initialization.py
```

### Broad-suite contextual residual-risk evidence (NOT slice PASS evidence)

```powershell
groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests\scripts\test_fab21_rules_payload_profile.py platform_tests\scripts\test_session_self_initialization.py -q --tb=short
# 2 failed, 71 passed
# Failures (PRE-EXISTING, unrelated to this diff; EXCLUDED from this slice's acceptance):
#   test_startup_model_contains_role_governance_and_kpi_inventory  (posture["package_version"] is None)
#   test_dashboard_and_report_are_written_with_time_series_kpi      (posture["upgrade_plan"]["available"] is False)
```

The broad command is reported as contextual signal only. The two failures are in
the GT-KB infrastructure upgrade-posture probe path (`posture["package_version"]`,
`posture["upgrade_plan"]["available"]`) — a code path this diff does not touch
(confirmed by `git show --name-status 522b7872`). They are environment-dependent
(stale dev-environment inventory; package/upgrade-plan probe returns None/False)
and are **not part of this slice's acceptance criteria**. To my knowledge they are
not separately tracked; they warrant separate triage (candidate WI) and are not
fixed here per GOV-07.

## Recommended Commit Type

`feat:` — this slice ADDS a new profiling capability; it is the measurement
foundation. The `perf:` cost-reduction recommended for the overall FAB-21
proposal lands in the later glossary-IA / hook-consolidation slices. Committed as
`feat:` at `522b7872`. (This report revision is `docs(bridge):`.)

## Isolation Placement Compliance

All changes are in-root under `E:\GT-KB\`:
`scripts/session_self_initialization.py` and
`platform_tests/scripts/test_fab21_rules_payload_profile.py`. No `applications/`
subtree touched; no out-of-root artifact.

## Acceptance Criteria (this slice)

1. The profiler reports the `.claude/rules/*.md` payload byte/token total vs the
   250 KB budget — DONE.
2. New tests pass; `ruff check` and `ruff format --check` clean — DONE (7/7 new
   tests pass; ruff clean).
3. No protected-narrative edit, no MemBase write, no config change in this slice
   — CONFIRMED.

The two broad-suite posture failures are explicitly OUT of these acceptance
criteria.

## Commit / Bridge State Note

Implementation committed at `522b7872`; the `-005` report at `320a4361`. This
`-007` report is committed for durability; its `REVISED@-007` INDEX entry is
added to the live working-tree `bridge/INDEX.md` for Loyal Opposition to scan.
The live INDEX is the canonical queue per `GOV-FILE-BRIDGE-AUTHORITY-001`.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
