NEW

bridge_kind: prime_proposal
Document: gtkb-fab-08-slot-leak-fix
Version: 003
Author: prime-builder (Claude Opus 4.8, harness B) — interactive owner session
Date: 2026-06-11
Responds-To: bridge/gtkb-fab-08-slot-leak-fix-002.md

Project: PROJECT-FABLE-INVESTIGATION
Work Item: WI-4420
Project Authorization: PAUTH-FAB08-20260610

author_identity: prime-builder
author_harness_id: B
author_session_context_id: e45ccf07-99f6-4ad6-b572-570a76a264a2
author_model: claude-opus-4-8
author_model_version: 4.8
author_model_configuration: interactive owner session, ::init gtkb pb

target_paths: ["groundtruth-kb/tests/adopter/conftest.py", "groundtruth-kb/tests/test_scaffold_isolation.py", "groundtruth-kb/tests/test_cli.py", "groundtruth-kb/src/groundtruth_kb/project/doctor.py", "applications/_test_*/**", "platform_tests/scripts/**"]

No KB mutation: the purge is a file deletion of leaked test skeletons; the doctor auto-prune is code. No `groundtruth.db` mutation.

---

# FAB-08 — Slot-Leak Fix — Post-Implementation Report

WI-4420 (FAB-08) of PROJECT-FABLE-INVESTIGATION. Implements the GO'd proposal
`bridge/gtkb-fab-08-slot-leak-fix-001.md` (GO at `-002`) within the scoped `target_paths` and the GO's
Implementation Constraints. Implementation-start authorization packet:
`sha256:f11f2ea8d26a907e419327ffbbe0a8a8f3dfaf560c5d21c60b75eb39347e494a` (from the live GO at `-002`).

## Specification Links

Specs carried forward from the `-001` proposal:

- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge lifecycle; this report is the next version with a `NEW` INDEX entry.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — specs carried forward from `-001`.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — spec-to-test mapping + executed commands + results below.
- `GOV-STANDING-BACKLOG-001` — WI-4420 governed backlog authority.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — the purge removed only leaked `applications/_test_*` skeletons
  (in-root, test-fixture defect); no real application relocated; the only real slot (`Agent_Red`) preserved.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` / `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` /
  `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — durable-artifact lifecycle for the doctor check + test changes.

## Prior Deliberations

- `bridge/gtkb-fab-08-slot-leak-fix-001.md` (proposal) + `-002` (GO with Implementation Constraints).
- `DELIB-FAB08-REMEDIATION-20260610` — owner decision: fix + purge + doctor auto-clean; HYG-022 deferred.

## Owner Decisions / Input

Per `DELIB-FAB08-REMEDIATION-20260610` (AskUserQuestion, 2026-06-10): HYG-053 = `_force_rmtree` onexc helper +
one-time purge + doctor WARN/auto-prune for stale `_test_*` >24h; HYG-022 (Agent_Red `application.toml`
backfill) deferred to a separate Agent-Red-scoped bridge. No new owner decision was required to implement.

## Backlog Visibility

`GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS`: this change performs **no bulk backlog/MemBase
operation** — it writes nothing to `work_items` or `groundtruth.db`. The one-time purge of leaked test
skeletons produced an explicit inventory of what was removed (234 `applications/_test_*` slots found → 234
purged → 0 remaining; non-`_test_*` dirs preserved: `Agent_Red`), recorded under Commands Run for review. The
deletions are of gitignored, regenerable test artifacts, not canonical backlog state.

## Isolation Placement Compliance

`ADR-ISOLATION-APPLICATION-PLACEMENT-001`: all changes are in-root under `E:\GT-KB\` — the test files under
`groundtruth-kb/tests/`, the doctor source under `groundtruth-kb/src/groundtruth_kb/project/`, the new test
under `platform_tests/scripts/`, and this report under `E:\GT-KB\bridge\`. The one-time purge deleted only
leaked `applications/_test_*` skeletons (a test-fixture defect) directly under in-root `applications/`; it
relocated no real application and preserved the only real slot (`Agent_Red`).

## What Was Implemented

1. **`_force_rmtree` robust removal helper** — added to the 3 GO'd in-scope test files
   (`tests/adopter/conftest.py`, `tests/test_scaffold_isolation.py`, `tests/test_cli.py`). It clears the
   Windows read-only bit on `.git` object files via the py3.12+ `shutil.rmtree(onexc=...)` handler and retries;
   unlike `ignore_errors=True` it propagates a real failure (the GO's "fail loudly" constraint).
2. **Replaced the silent cleanup at all in-scope sites** — `conftest.py:92`;
   `test_scaffold_isolation.py` × 5 (the two `sandbox_path` sites, the two golden post-test `sandbox` sites,
   and the golden pre-scaffold `shutil.rmtree(sandbox)` at the former line 464); `test_cli.py:401`.
3. **Doctor auto-prune** — added `_check_stale_test_slots(target)` + a module-level `_force_remove_tree` to
   `doctor.py`, registered as a project-level check. It detects `applications/_test_*` slots older than 24h,
   prunes them with the robust remover, and emits a WARN listing what was removed; it touches ONLY
   `_test_*`-named dirs directly under `applications/` (defense-in-depth: never a real application subtree).
4. **One-time purge** — removed the live leaked `_test_*` skeletons (see count below).
5. **Spec-derived tests** — `platform_tests/scripts/test_fab08_slot_leak_fix.py` (5 tests).
6. **Incidental in-file lint fix** — `doctor.py` carried one pre-existing `SIM105` (`try/except ValueError/pass`
   at the dispatch-state staleness parse, unrelated to FAB-08); since `doctor.py` is an in-scope changed file
   and the changed-file gate requires `ruff check` clean, it was converted to `contextlib.suppress(ValueError)`
   (the `suppress` import already existed). Behavior-preserving; disclosed here per GOV-06.

## Spec-Derived Verification Plan

| Spec / requirement | Derived test | Result |
|---|---|---|
| HYG-053 root cause — `_force_rmtree`/`_force_remove_tree` removes a read-only `.git` tree without silent failure | `test_force_remove_tree_clears_readonly` | PASS |
| GO constraint — cleanup fails LOUDLY (no `ignore_errors` swallow) | `test_force_remove_tree_fails_loudly_on_missing` (raises `OSError`) | PASS |
| doctor auto-prune — stale `_test_*` >24h pruned + WARN; fresh + non-`_test_*` + real apps preserved | `test_check_stale_test_slots_prunes_old_keeps_fresh` | PASS |
| doctor auto-prune — clean state | `test_check_stale_test_slots_pass_when_clean` / `_pass_when_no_applications_dir` | PASS |
| application-slot contract — no `_test_*` remains after a fixture run; only real slots remain | live purge + `test_scaffold_isolation.py` in-situ run | PASS (0 remain; `Agent_Red` preserved) |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `ruff check` + `ruff format --check` on all changed `.py` | PASS (clean) |

## Commands Run + Observed Results

- `python -m pytest platform_tests/scripts/test_fab08_slot_leak_fix.py -q` → **5 passed in 0.28s**.
- `python -m ruff check <5 changed files>` → **All checks passed!** (after the incidental SIM105 fix +
  import-sort on the new test).
- `python -m ruff format --check <5 changed files>` → **5 files already formatted** (exit 0).
- `python -m pytest groundtruth-kb/tests/test_scaffold_isolation.py -q` → **19 passed, 2 failed**. The 2
  failures (`test_tp14_local_only_matches_golden_fixture`, `test_tp15_dual_agent_matches_golden_fixture`) are a
  **pre-existing template drift** — a byte mismatch in scaffold output `.claude/hooks/bridge-compliance-gate.py`
  vs the committed golden fixture. This is exactly **HYG-023** (templates are the stale side), owned by FAB-22;
  it is in scaffold output, NOT the cleanup path, so it is independent of this FAB-08 change. The 19 passing
  tests include the ones that exercise `_force_rmtree` at the changed sites.
- One-time purge (venv python, robust remover scoped to `applications/_test_*`): **FOUND 234** →
  **PURGED 234** → **REMAINING `_test_*`: 0**; non-`_test_*` dirs preserved: **`['Agent_Red']`**. Recorded per
  the GO constraint that the live count is no longer exactly the investigation's 229 (Codex review counted 234).

## Acceptance Criteria Check

1. ✅ All live `applications/_test_*` skeletons removed (234 purged; 0 remain); `applications/` holds only the
   real `Agent_Red` slot.
2. ✅ `_force_rmtree` implemented + used at all in-scope fixture sites; read-only `.git` cleanup works
   (validated by `test_force_remove_tree_clears_readonly` + the 19-passing in-situ run).
3. ✅ Doctor auto-prunes stale `_test_*` >24h with a WARN (`_check_stale_test_slots`); the occupancy input is
   now 0 slots so the HYG-053 P0/~230-P1 spam no longer has slots to report (full `gt project doctor` run is
   the verifier's final confirmation).
4. ✅ Tests pass (FAB-08 suite 5/5; affected suite 19 pass + 2 pre-existing HYG-023 failures); ruff-clean.

## Constraints Honored (from the GO)

- HYG-022 kept OUT (no Agent_Red `application.toml` change).
- Deleted only `applications/_test_*`; `Agent_Red` and the non-`_test_*` dir preserved (verified post-purge).
- `_force_rmtree` fails loudly (no `ignore_errors`); validated by the loud-on-missing test.
- Actual purged count (234) recorded.

## Out-of-Scope Follow-Ons (not done — would exceed GO'd target_paths)

- `groundtruth-kb/tests/test_core_spec_intake.py` (lines ~159/188) and
  `groundtruth-kb/tests/adopter/test_golden_fixture_diff_per_version.py` (~84/89) carry the same
  `shutil.rmtree(..., ignore_errors=True)` sandbox-cleanup pattern but are NOT in FAB-08's `target_paths`;
  routing them through a shared helper is a follow-on.
- Consolidating the (currently self-contained, 3×-duplicated) `_force_rmtree` into one shared test-util module
  requires expanding `target_paths`; deferred.
- The 2 `test_scaffold_isolation.py` golden-fixture failures are HYG-023 (FAB-22 scope), not FAB-08.

## Bridge Protocol Compliance

Filed at `bridge/gtkb-fab-08-slot-leak-fix-003.md` with a matching `NEW` entry inserted at the top of the
FAB-08 entry in `bridge/INDEX.md` (above the prior `-002` GO and `-001` NEW versions); append-only — no prior
version was deleted or rewritten. `GOV-FILE-BRIDGE-AUTHORITY-001` (INDEX.md is canonical) is honored; Loyal
Opposition reviews this report and responds with `VERIFIED` or `NO-GO`.

## Recommended Commit Type

`fix:` — corrects the Windows `rmtree` slot-leak defect (with a small `feat:`-class doctor auto-prune + an
incidental `style:`/`refactor:`-class pre-existing `SIM105` cleanup in the touched `doctor.py`).

## Commit Status

Changes are implemented and verified but NOT committed (commit pending owner direction per commit discipline).
On `VERIFIED`, the changed files can be committed with the `fix:` type above.
