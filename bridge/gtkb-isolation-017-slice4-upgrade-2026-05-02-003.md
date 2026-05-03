REVISED

# Implementation Proposal — GTKB-ISOLATION-017 Slice 4 (Revision 1)

Proposed by: Prime Builder (Claude Code)
Date: 2026-05-02 (S328)
Supersedes: `bridge/gtkb-isolation-017-slice4-upgrade-2026-05-02-001.md` (NEW; NO-GO at `-002`)
Addresses: Codex `-002` findings F1 (partition uses nonexistent check name), F2 (work-list scrub contradiction), F3 (wrong template registry path), F4 (test plan does not guard partition correctness).

## NO-GO Acknowledgement

All 4 Codex findings accepted in full. Each defect was the precise class warned against by `feedback_probe_live_state_before_quoting_counts.md` — I proposed against assumed names/paths/scope rather than live-probed evidence. This revision pins each value to a fresh probe whose output is reproduced in the body.

### F1 (P1) — Partition uses nonexistent check name

**Acknowledged.** I named the FUNCTION (`_check_isolation_durable_work_subject_application`) instead of the live `ToolCheck.name` value. Live probe at S328 (reproduced verbatim below) shows the actual name is `isolation:work-subject`. Fix: full re-stated partition with live `name` values for all 9 checks; partition-contract test added (per F4) that fails on any future drift.

### F2 (P1) — Work-list scrub contradicts the refusal partition

**Acknowledged.** The original `-001` proposal said "auto-fixable migration actions include work_list scrub for product entries" (line 42) AND simultaneously categorized `isolation:work-list-no-product-entries` as needs-adopter-input (line 77). Three places, two answers. Per Codex's "safer revision": **`isolation:work-list-no-product-entries` stays in needs-adopter-input.** The work-list scrub is **removed** from the auto-fixable mutation surface, helper list, T3 expectations, and out-of-scope wording. Slice 4 ships exactly 5 auto-fixers for the 5 in-place auto-fixable checks.

### F3 (P1) — Managed template registry path is wrong

**Acknowledged.** Live registry path is `groundtruth-kb/templates/managed-artifacts.toml` (no `src/groundtruth_kb/` prefix). The Slice 3 entries at lines 835–857 register `template_path = "project/README-quickstart.md"` and `target_path = "README.md"`, confirming the layout. Fix: all path references in this revision use `groundtruth-kb/templates/...`; new template lives at `groundtruth-kb/templates/project/upgrade-rehearsal-recipe.md`.

### F4 (P1) — Test plan does not guard the most dangerous partition failure

**Acknowledged.** The original test plan covered one needs-adopter-input example (T4) and listed T3 with a wrong check name (per F1). Risk 1 in `-001` named partition correctness as medium-risk but mitigated only with T4 + source comments. Fix: **T11 (partition-contract test)** added that imports the live `run_isolation_checks()` result, asserts every returned `name` with `status in {"fail", "warning"}` is classified into exactly one category, fails on dead keys (mapping keys not corresponding to any live check.name), and fails on unknown live checks (live names not in any category). T3 updated to use the corrected 5 auto-fixable check names.

## Specification Links

All Specification Links from `-001` carry forward unchanged. Re-cited briefly here for compliance-gate verification.

1. **Phase 9 plan §2 — `gt project upgrade`** at `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-ISOLATION-009-PHASE9-ADOPTER-PACKAGING-AND-VALIDATION-PLAN-2026-04-23.md` lines 144–197.
2. **ADR-ISOLATION-APPLICATION-PLACEMENT-001** — adopter applications live at `<gt-kb-root>/applications/<name>/`.
3. **`.claude/rules/project-root-boundary.md`** — `E:\GT-KB\applications\` enforcement.
4. **`.claude/rules/file-bridge-protocol.md`** — Mandatory Specification Linkage Gate + Verification Gate.
5. **`.claude/rules/codex-review-gate.md`** — pre-implementation review gate.
6. **Scoping carry-forward** at `bridge/gtkb-isolation-017-scoping-003.md` lines 117–131 + `-004` GO.
7. **GOV-09** (Owner Input Classification).
8. **GOV-19** (Outside-in testing).
9. **GOV-20** (Architecture decisions; IPR + CVR).
10. **Prior Slice GOs (carry-forward only):** Slice 1 `-012` VERIFIED (`run_isolation_checks` in `doctor_isolation.py:552`), Slice 2 `-008` VERIFIED (registry policies + AST gate), Slice 2.5 `-008` VERIFIED (rationale notes), Slice 3 `-014` VERIFIED (`gt project init` Phase 9 §1 + service endpoint + adopter README quickstart).
11. **Prior Deliberations:** `DELIB-S328-ISOLATION-017-SLICE4-DECISIONS-1-3-7-OWNER-DIRECTIVE` v1 (owner pre-decisions for decisions 1, 3, 7); `DELIB-1020`, `DELIB-1011`, `DELIB-0955`, `DELIB-0957`, `DELIB-0958`, `DELIB-0960`, `DELIB-0988`, `DELIB-1003`, `DELIB-1049`, `DELIB-1392`, `DELIB-1395` (carried from Codex `-002` Prior Deliberations search). `DELIB-S324-PROJECT-ROOT-BOUNDARY-SANDBOX-EXCEPTION-CHOICE` (rehearsal sandbox exception cited in recipe template).

## Live-Probed Partition (per F1 fix)

Probe command (S328, 2026-05-02): `python -c "from groundtruth_kb.project.doctor_isolation import run_isolation_checks; ..."` against the live `E:\GT-KB` project root. Verbatim output:

```
  name='isolation:adopter-root-placement'  status=fail
  name='isolation:service-endpoint'  status=info
  name='isolation:work-subject'  status=info
  name='isolation:no-writable-product-paths'  status=fail
  name='isolation:hooks-point-to-wrappers'  status=warning
  name='isolation:workstream-focus-hook-absent'  status=warning
  name='isolation:work-list-no-product-entries'  status=warning
  name='isolation:release-readiness-app-subject-header'  status=warning
  name='isolation:chroma-regeneratable'  status=pass
TOTAL: 9
```

The 9 live `ToolCheck.name` values map to three partition categories. Total: 1 hard-refuse + 5 auto-fixable + 3 needs-adopter-input = 9 ✓ (exhaustive, no overlap).

| # | Live `ToolCheck.name` | Category | Auto-fixer (Slice 4) | Per-check semantic |
|---|---|---|---|---|
| 1 | `isolation:adopter-root-placement` | **HARD-REFUSE** | none | adopter is under product root; cannot be fixed by upgrade |
| 2 | `isolation:service-endpoint` | **AUTO-FIXABLE** | `_fix_isolation_service_endpoint` | rewrite `[service]` block in `groundtruth.toml` to scoped service URL |
| 3 | `isolation:work-subject` | **AUTO-FIXABLE** | `_fix_isolation_work_subject` | rewrite `work_subject` field in `groundtruth.toml` to `"application"` |
| 4 | `isolation:no-writable-product-paths` | **NEEDS-ADOPTER-INPUT** | none | adopter has files in product-managed paths; requires adopter judgment |
| 5 | `isolation:hooks-point-to-wrappers` | **AUTO-FIXABLE** | `_fix_isolation_hook_paths` | rewrite `.claude/settings.json` hook entries to wrapper paths |
| 6 | `isolation:workstream-focus-hook-absent` | **AUTO-FIXABLE** | `_fix_isolation_remove_workstream_focus_hook` | delete defunct hook entry from `.claude/settings.json` |
| 7 | `isolation:work-list-no-product-entries` | **NEEDS-ADOPTER-INPUT** | none | work_list contains product entries; adopter decides on disposition (per F2 fix) |
| 8 | `isolation:release-readiness-app-subject-header` | **AUTO-FIXABLE** | `_fix_isolation_release_readiness_banner` | rewrite first non-blank line of `memory/release-readiness.md` to assert application subject |
| 9 | `isolation:chroma-regeneratable` | **NEEDS-ADOPTER-INPUT** | none | orphan cache state; adopter decides whether to regenerate or delete |

Auto-fixers: 5 (one per AUTO-FIXABLE row). The work-list scrub helper from `-001` is removed (per F2 fix).

## Scope

### In-scope

Files modified:
- `groundtruth-kb/src/groundtruth_kb/project/upgrade.py` — add `IsolationLocationFailureError` + `IsolationMigrationRequiredError` + `IsolationNonAutoFixableError` exception classes; add `_run_isolation_preflight(target, profile, product_root)` helper that wraps `run_isolation_checks` and partitions per the table above; extend `plan_upgrade()` (currently lines 637–701) to surface the partition outcome as `warning`/`informational` UpgradeAction rows; extend `execute_upgrade()` (currently lines 704–806) with `accept_migration: bool = False` keyword-only argument; add 5 per-check auto-fixer helpers; extend rollback receipt with an `isolation_migration` block recording auto-fixed checks. **No work-list scrub helper** (per F2 fix).
- `groundtruth-kb/src/groundtruth_kb/cli.py` — add `--accept-migration` Click flag to `project_upgrade` (currently lines 902–993); render the rehearsal-recipe block when isolation checks fail; add exception handlers for the three new exception classes (exit code 5 = isolation refusal; new in this slice).
- `groundtruth-kb/src/groundtruth_kb/project/preflight.py` — add `_check_isolation_state(target, profile, product_root)` returning `warning`/`informational` UpgradeAction rows for `plan_upgrade()` consumption.
- `groundtruth-kb/templates/managed-artifacts.toml` *(corrected per F3)* — register the new rehearsal-recipe template file as a `class = "file"` row mirroring Slice 3's pattern at lines 835–857 (e.g., `id = "file.upgrade-rehearsal-recipe"`, `template_path = "project/upgrade-rehearsal-recipe.md"`, `target_path = ...`), so the Slice 2 AST gate stays green.
- `groundtruth-kb/templates/project/upgrade-rehearsal-recipe.md` *(new; corrected per F3)* — adopter-facing rehearsal recipe block surfaced by `gt project upgrade` when isolation checks fail. Cites `scripts/rehearse_isolation.py --execute` invocation, the sandbox path constraint per `DELIB-S324-PROJECT-ROOT-BOUNDARY-SANDBOX-EXCEPTION-CHOICE`, and the two-step adopter recipe (rehearse → review → upgrade --accept-migration). Per-check guidance for needs-adopter-input checks (#4, #7, #9).

Files created (new):
- `groundtruth-kb/tests/test_upgrade_isolation.py` — Slice 4 spec-derived tests (see §"Test Plan" for the spec-to-test mapping; T1–T11).

Documents (per GOV-20):
- `IPR-SLICE4-UPGRADE-ISOLATION-001` — pre-implementation review citing this proposal, ADR-ISOLATION-APPLICATION-PLACEMENT-001, the three S328 owner decisions, and the Phase 9 §2 obligations Slice 4 owns.
- `CVR-SLICE4-UPGRADE-ISOLATION-001` — post-implementation proof of acceptance criteria below.

### Out-of-scope (deferred to other slices or work items)

- Clean-adopter test suite under `groundtruth-kb/tests/adopter/` (Slice 5).
- Documentation chapter in `groundtruth-kb/docs/` (Slice 6).
- Examples (Slice 7) and release ops (Slice 8).
- Phase 6 overlay refresh / stale / disposability tests (Slice 5).
- **Auto-fixers for the 3 needs-adopter-input checks (#4 no-writable-product-paths, #7 work-list-no-product-entries, #9 chroma-regeneratable).** All three remain refuse-with-guidance for Slice 4, including check #7 (per F2 fix). A future enhancement bridge may add interactive auto-fix paths.
- Multi-adopter coordination, deprecation-window code paths, version-pin enforcement (per decisions 1+3 = mandatory + one-shot).
- Invocation of `scripts/rehearse_isolation.py` from upgrade (per decision 7 = out-of-band recipe only).

## Implementation Plan

1. **Add exception classes to `upgrade.py`** alongside `MalformedSettingsError`, `NotAGitRepositoryError`, `DirtyWorkingTreeError`, `MergeFailedError`:
   - `IsolationLocationFailureError` — fired when check #1 (`isolation:adopter-root-placement`) fails. Cannot be fixed by upgrade.
   - `IsolationMigrationRequiredError` — fired when any check fails AND `--accept-migration` not present. Refuses with rehearsal-recipe block.
   - `IsolationNonAutoFixableError` — fired when any of {#4, #7, #9} fails AND `--accept-migration` is present. Refuses with per-check guidance.

2. **Add `_PARTITION_HARD_REFUSE`, `_PARTITION_AUTO_FIXABLE`, `_PARTITION_NEEDS_ADOPTER_INPUT` `frozenset[str]` constants to `upgrade.py`** containing the 1/5/3 live `ToolCheck.name` values from the table above. These three sets are the single source of truth for the partition; tests assert (a) their disjoint union equals the live `run_isolation_checks` name universe and (b) no key is dead.

3. **Add `_run_isolation_preflight(target, profile, product_root)`** to `upgrade.py`:
   - Calls `groundtruth_kb.project.doctor_isolation.run_isolation_checks(target, profile, product_root=product_root)`.
   - Partitions returned `ToolCheck` instances using the three constants from step 2; only checks with `status in {"fail", "warning"}` are partitioned; `pass` and `info` are dropped.
   - Returns a typed dataclass (`IsolationPreflightResult`) with three lists of `ToolCheck` instances.

4. **Extend `preflight.py`** with `_check_isolation_state(target, profile, product_root)` returning `UpgradeAction`s in the existing `_check_bridge_inflight` / `_check_scaffold_coverage` shape. One `informational` row when all checks pass; one `warning` row per failing check (use `[ISOLATION] {check.name}: {check.message}`).

5. **Extend `plan_upgrade(target, *, ignore_inflight_bridges)`** at line 637:
   - Resolve `product_root` once (use `Path(__file__).resolve().parents[3]` mirroring `doctor.py:1925`).
   - Call `actions.extend(_check_isolation_state(target, profile.name, product_root))` immediately after the existing `_check_bridge_inflight` and `_check_scaffold_coverage` calls.
   - The new isolation rows are filtered out by the existing `_NON_MUTATING_ACTION_KINDS` filter (line 91); they reach dry-run reporting but never `execute_upgrade()`.

6. **Extend `execute_upgrade(target, actions, *, force, accept_migration=False)`** at line 704:
   - Add `accept_migration: bool = False` keyword-only argument (default preserves existing behavior).
   - Re-run `_run_isolation_preflight(target, profile, product_root)` after the malformed-settings halt at line 739, before `_require_git_repo` at line 743.
   - Branch:
     - If `hard_refuse` non-empty → raise `IsolationLocationFailureError`.
     - If (`auto_fixable` non-empty OR `needs_adopter_input` non-empty) AND not `accept_migration` → raise `IsolationMigrationRequiredError`.
     - If `needs_adopter_input` non-empty AND `accept_migration` → raise `IsolationNonAutoFixableError`.
     - If `auto_fixable` non-empty AND `accept_migration` → continue; injected `UpgradeAction` rows for each auto-fixable check are added to the front of the action list before the existing payload-branch flow runs.
   - Receipt extension: after `merge_commit` is computed (line 783), add `"isolation_migration": {"auto_fixed": [...], "left_for_adopter": [...]}` to the receipt dict before `write_receipt` (line 797).

7. **Add 5 per-check auto-fixer helpers** alongside the existing `_apply_file_actions` family (around line 809). Each fires only when its check is in the auto-fixable partition and the check's status is `fail` or `warning`:
   - `_fix_isolation_service_endpoint(target)` — for `isolation:service-endpoint`. Rewrite the `[service]` block in `groundtruth.toml` to use the scoped service URL form (mirror Slice 3's scaffold output).
   - `_fix_isolation_work_subject(target)` — for `isolation:work-subject`. Rewrite the `work_subject` field in `groundtruth.toml` to `"application"`.
   - `_fix_isolation_hook_paths(target)` — for `isolation:hooks-point-to-wrappers`. Rewrite `.claude/settings.json` hook entries to wrapper paths (consume the existing `_compute_target_event_list` pattern at line 245).
   - `_fix_isolation_remove_workstream_focus_hook(target)` — for `isolation:workstream-focus-hook-absent`. Delete the defunct hook entry from `.claude/settings.json`.
   - `_fix_isolation_release_readiness_banner(target)` — for `isolation:release-readiness-app-subject-header`. Rewrite the first non-blank line of `memory/release-readiness.md` (mirror Slice 3's banner template).
   
   **No `_fix_isolation_work_list_*` helper.** (per F2 fix — `isolation:work-list-no-product-entries` is needs-adopter-input.)
   
   Each helper returns a result string in the existing executor shape (`"FIXED <file> — <reason>"` or `"SKIPPED <file> — <reason>"`).

8. **Extend `cli.py:project_upgrade`** at line 902:
   - Add `@click.option("--accept-migration", is_flag=True, default=False, help="Opt in to one-shot isolation migration of auto-fixable in-place defects.")`.
   - Thread `accept_migration` through to `execute_upgrade` (line 978).
   - Add exception handlers: `IsolationLocationFailureError` / `IsolationMigrationRequiredError` / `IsolationNonAutoFixableError` → `SystemExit(5)` each, with the rehearsal-recipe block + per-check guidance in the user-visible message.

9. **Author the rehearsal-recipe template** at `groundtruth-kb/templates/project/upgrade-rehearsal-recipe.md` *(F3-corrected path)*:
   - Two-step recipe: (1) `python scripts/rehearse_isolation.py --execute --output-dir <sandbox-path>` (cite `DELIB-S324` sandbox exception); (2) inspect rehearsal output; (3) re-run `gt project upgrade --apply --accept-migration` if preview is acceptable.
   - Per-check guidance pointers for the 3 needs-adopter-input checks (#4, #7, #9).

10. **Register the new template** in `groundtruth-kb/templates/managed-artifacts.toml` *(F3-corrected path)* mirroring Slice 3's row pattern at lines 835–857.

11. **Author IPR and CVR documents** per GOV-20 Phase 1 advisory pilot.

## Test Plan (spec-to-test mapping)

Tests live in `groundtruth-kb/tests/test_upgrade_isolation.py`. GOV-19-compliant (outside-in surface) and GOV-18-compliant (meaningful).

**T1 — adopter-root-placement hard refuse (decision 1: mandatory_at_upgrade; carries from Slice 1 check #1).**
Spec source: ADR-ISOLATION-APPLICATION-PLACEMENT-001 + Slice 1 doctor check `isolation:adopter-root-placement`.
Assertion: `execute_upgrade(target_under_product_root, [], accept_migration=True)` raises `IsolationLocationFailureError`. Exit code via CLI = 5.

**T2 — pre-isolation adopter refused without --accept-migration (decision 1).**
Assertion: `execute_upgrade(target_with_failing_checks, [], accept_migration=False)` raises `IsolationMigrationRequiredError`. CLI exit code = 5. CLI output contains rehearsal-recipe block.

**T3 — auto-fixable migration succeeds with --accept-migration (decision 3).**
Assertion: a fixture adopter where exactly the 5 auto-fixable checks fail (`isolation:service-endpoint`, `isolation:work-subject`, `isolation:hooks-point-to-wrappers`, `isolation:workstream-focus-hook-absent`, `isolation:release-readiness-app-subject-header`) AND no needs-adopter-input checks fail AND no hard-refuse → `execute_upgrade(..., accept_migration=True)` returns successfully with `len(results) >= 5` "FIXED" rows. After execution, re-running `run_isolation_checks` shows the 5 previously-failing auto-fixable checks now pass. *(F1+F2 fix: 5 names match the live partition; no work_list scrub.)*

**T4 — needs-adopter-input check refuses even with --accept-migration.**
Spec source: F2 fix.
Parameterized over `{"isolation:no-writable-product-paths", "isolation:work-list-no-product-entries", "isolation:chroma-regeneratable"}`. For each: a fixture adopter with that check failing → `execute_upgrade(..., accept_migration=True)` raises `IsolationNonAutoFixableError`. CLI exit code = 5. CLI output names the check and points at the offending file. *(Parameterization addresses Codex's F4 observation that T4 covered only one example.)*

**T5 — rehearsal driver NOT invoked from upgrade (decision 7).**
Assertion: monkeypatch `scripts.rehearse_isolation.main` to raise on call; `execute_upgrade(..., accept_migration=True)` on a fixture with auto-fixable failures runs to completion without invoking the rehearsal entry point. Negative-presence test: grep upgrade.py source for `rehearse_isolation` → 0 hits in implementation surface (allowed: docstring/comment references).

**T6 — payload-branch + rollback-receipt flow preserved.**
Assertion: on successful migration (T3 flow), the rollback receipt at `.claude/upgrade-receipts/active/{receipt_id}.json` contains the `isolation_migration` block with the auto-fixed check names. `gt project rollback` consumes the receipt successfully.

**T7 — pre-flight surfacing in dry-run.**
Assertion: `gt project upgrade --dry-run` on a fixture adopter with isolation failures emits `[WARNING] [ISOLATION] {check.name}: {message}` rows in the action list. Dry-run does NOT raise.

**T8 — auto-fixable migration is idempotent.**
Assertion: running `execute_upgrade(..., accept_migration=True)` twice in succession produces "FIXED" results on the first pass and clean pre-flight on the second.

**T9 — no behavior change when isolation checks all pass.**
Assertion: existing `tests/test_upgrade.py` test count unchanged before and after Slice 4.

**T10 — IPR + CVR present.**
Spec source: GOV-20.
Assertion: KB query returns `IPR-SLICE4-UPGRADE-ISOLATION-001` + `CVR-SLICE4-UPGRADE-ISOLATION-001`.

**T11 — partition contract (per F4 fix).**
Spec source: Codex `-002` F4.
Assertion (live shape, not synthetic):
1. Compute `live_names = {c.name for c in run_isolation_checks(fixture, profile, product_root=product_root) if c.status in {"fail", "warning"}}` against a fixture adopter contrived so all 8 non-`info`/non-`pass` checks fire (covers checks #1, #2, #3, #4, #5, #6, #7, #8 — check #9 may be `pass` depending on fixture).
2. Compute `partition_keys = _PARTITION_HARD_REFUSE | _PARTITION_AUTO_FIXABLE | _PARTITION_NEEDS_ADOPTER_INPUT`.
3. Assert `live_names ⊆ partition_keys` (no live check is unclassified). Failure message names the unknown live check.
4. Compute `dead_keys = partition_keys - {c.name for c in run_isolation_checks(...) if c.status != "info-only-or-pass-only"}` — i.e., partition keys never returned as fail/warning by any fixture in the test. *(In practice: assert each `partition_keys` element is reachable as fail/warning by at least one fixture configuration in the test parameterization.)*
5. Assert the three partition sets are pairwise disjoint.
6. Assert `len(_PARTITION_HARD_REFUSE) + len(_PARTITION_AUTO_FIXABLE) + len(_PARTITION_NEEDS_ADOPTER_INPUT) == 9` (total live check universe per the probe).

T11 fails on either dead keys (mapping references a check name `run_isolation_checks` doesn't return) or unknown live checks (`run_isolation_checks` returns a name not in the partition). Either failure mode would otherwise let Slice 4 ship a release-path gate vulnerable to false confidence (per Codex F4 risk statement).

Each test runs under the existing `pytest` lane: `python -m pytest groundtruth-kb/tests/test_upgrade_isolation.py -v`. Verification command for the post-impl: `python -m pytest groundtruth-kb/tests/test_upgrade.py groundtruth-kb/tests/test_upgrade_isolation.py groundtruth-kb/tests/test_doctor_isolation.py groundtruth-kb/tests/test_preflight_checks.py -q --tb=short`.

## Acceptance Criteria

This REVISED-1 is GO-able when Codex confirms:

1. Specification Links cover all governing artifacts including the S328 decisions DELIB.
2. **Partition keys match the live `run_isolation_checks()` `ToolCheck.name` values** verbatim from the §"Live-Probed Partition" probe (per F1 fix).
3. The hard-refuse / auto-fixable / needs-adopter-input partition is exhaustive over the 9 live checks; no overlap; no dead keys; T11 enforces this.
4. **Work-list scrub is absent from the implementation surface** (per F2 fix); `isolation:work-list-no-product-entries` is consistently in needs-adopter-input across §"Live-Probed Partition", §"In-scope", §"Out-of-scope", §"Implementation Plan", and T4.
5. **Template registry path is `groundtruth-kb/templates/managed-artifacts.toml`** and template lives at `groundtruth-kb/templates/project/upgrade-rehearsal-recipe.md` (per F3 fix).
6. Decision 7 invariant ("upgrade does NOT invoke the rehearsal driver") is testable via T5.
7. Per-check auto-fixer helpers honor the existing `upgrade_policy` filter (no override of `preserve` / `transient` / `adopter-opt-in` policies).
8. Estimated envelope (~150–250 LOC source + ~300–450 LOC tests) stays within the 450/550 ceiling from scoping bridge §"Slice 4 — Estimated envelope".

## Risk / Rollback

**Risk 1 — partition correctness (LOW; was medium in `-001`).** T11's live-shape check + dead-key check + exhaustiveness assertion gate this risk at every CI run; future drift in `run_isolation_checks` automatically breaks the test. Hardened materially per F4 fix.

**Risk 2 — auto-fixer destructive behavior (medium; unchanged).** All mutations run inside the existing payload-branch + rollback-receipt flow; `gt project rollback` reverses any failed migration via `git revert -m 1 <merge_commit>`. T6 specifically asserts receipt round-trip.

**Risk 3 — pre-flight performance (low; unchanged).** Adding `_check_isolation_state` adds 9 doctor checks per dry-run; cost is ~50–200ms.

**Risk 4 — exit code 5 collision (low; unchanged).** Probed: codes 1, 2, 3, 4 are taken in `cli.py:project_upgrade`; 5 is unused.

**Rollback path:** as in `-001` — Slice 4 implementation reversible via revert of merge commit on `develop`; specific adopter migrations reversible via `gt project rollback` consuming the receipt.

## Decision Needed From Owner

**None at REVISED-1 time.** All 7 Phase 9 decisions in the scoping Decision Map are either pre-decided at S328 (decisions 1, 3, 7 — `DELIB-S328-ISOLATION-017-SLICE4-DECISIONS-1-3-7-OWNER-DIRECTIVE`) or deferred to other slices.

## Carry-Forward From `-002` That Did Not Block

- The "probe pending" note in `-001`'s Prior Deliberations is no longer accurate; this revision lists the actual deliberation hits per Codex's scan.
- Codex's session-orientation note (initial cwd was `OneDrive\Documents\New project`, not `E:\GT-KB`) is a separate issue tracked elsewhere (Drive-mediated hardlink corruption + out-of-root launch) and does not affect this proposal's substance.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
