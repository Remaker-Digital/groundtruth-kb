REVISED

bridge_kind: prime_proposal
Document: gtkb-fab-08-slot-leak-fix
Version: 005
Author: prime-builder (Claude Opus 4.8, harness B) — interactive owner session
Date: 2026-06-11
Responds-To: bridge/gtkb-fab-08-slot-leak-fix-004.md

Project: PROJECT-FABLE-INVESTIGATION
Work Item: WI-4420
Project Authorization: PAUTH-FAB08-20260610

author_identity: prime-builder
author_harness_id: B
author_session_context_id: 9660f4cb-1b84-410e-a024-febdabe7c541
author_model: claude-opus-4-8
author_model_version: 4.8
author_model_configuration: interactive owner session, ::init gtkb pb

target_paths: ["groundtruth-kb/tests/adopter/conftest.py", "groundtruth-kb/tests/test_scaffold_isolation.py", "groundtruth-kb/tests/test_cli.py", "groundtruth-kb/src/groundtruth_kb/project/doctor.py", "applications/_test_*/**", "platform_tests/scripts/**"]

No KB mutation: the purge is a file deletion of leaked test skeletons; the doctor auto-prune + the runtime-floor fix are code. No `groundtruth.db` mutation.

---

# FAB-08 — Slot-Leak Fix — Revised Post-Implementation Report

WI-4420 (FAB-08) of PROJECT-FABLE-INVESTIGATION. Revises the post-implementation report
`bridge/gtkb-fab-08-slot-leak-fix-003.md` to clear the single P1 verification finding in
`bridge/gtkb-fab-08-slot-leak-fix-004.md` (NO-GO). Implementation remains under the GO at `-002`;
impl-start authorization packet for this revision:
`sha256:3b5c4c94d0c4e2761f0115c9fda58a9239edadaf5440814be5917711e22026a5` (resumable post-GO NO-GO; the
GO at `-002` still authorizes the revision within the original `target_paths`).

## Revision Scope

REVISED-005 addresses the lone P1 finding in `-004`:

- **P1 (implementation broke the advertised Python 3.11 runtime):** the `_force_rmtree` /
  `_force_remove_tree` helpers called `shutil.rmtree(path, onexc=_on_rm_error)`. `onexc` is a Python
  3.12+ keyword; on the package's declared `requires-python = ">=3.11"` floor it raises
  `TypeError: rmtree() got an unexpected keyword argument 'onexc'`, so the recurrence-prevention path
  would fail on a supported interpreter. The verifier (and this session) run Python 3.14, which is why
  the original suite was green despite the latent break.

**Fix (Codex's preferred least-disruptive path — a version-adaptive wrapper, no runtime-floor change):**
all four helpers now dispatch on `sys.version_info`:

```python
if sys.version_info >= (3, 12):
    shutil.rmtree(path, onexc=_on_rm_error)            # exc is the exception instance
else:
    shutil.rmtree(path, onerror=lambda func, p, exc_info: _on_rm_error(func, p, exc_info[1]))
```

The `onerror` callback (the correct, non-deprecated parameter on 3.11) receives a `(type, value, tb)`
tuple; the lambda adapts it to the existing `(func, path, exc)` handler so behavior is identical across
runtimes. `import sys` was added to the three test files that lacked it (`conftest.py`, `test_cli.py`,
`test_scaffold_isolation.py`, placed per ruff isort); `doctor.py` already imported `sys`. The package
runtime floor is unchanged at `>=3.11`.

A signature-compat regression was added so this cannot silently recur:

- two behavioral tests monkeypatch `sys.version_info` + a recording `shutil.rmtree` stub and assert the
  importable production helper `doctor._force_remove_tree` dispatches to `onerror` on a simulated 3.11
  floor and to `onexc` on 3.12 — these would FAIL against the pre-fix unconditional-`onexc` code
  regardless of the interpreter running them;
- one parametrized **source-scan** test reads all four helper files and asserts each carries both the
  `onexc=` branch and the `onerror=` fallback under a `sys.version_info` guard (interpreter-independent,
  so it catches the >=3.11 regression even on the verifier's 3.12+).

No other change from `-003`: the robust read-only-`.git` removal behavior, the doctor auto-prune, the
one-time purge result, and the GO constraints are unchanged.

## Specification Links

Specs carried forward from the `-001` proposal:

- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge lifecycle; this report is the next version with a `REVISED` INDEX entry.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — specs carried forward from `-001`.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — spec-to-test mapping + executed commands + results below.
- `GOV-STANDING-BACKLOG-001` — WI-4420 governed backlog authority.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — the purge removed only leaked `applications/_test_*` skeletons
  (in-root, test-fixture defect); no real application relocated; the only real slot (`Agent_Red`) preserved.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` / `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` /
  `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — durable-artifact lifecycle for the doctor check + test changes.

## Prior Deliberations

- `bridge/gtkb-fab-08-slot-leak-fix-001.md` (proposal) + `-002` (GO with Implementation Constraints).
- `bridge/gtkb-fab-08-slot-leak-fix-003.md` (post-impl report) + `-004` (verification NO-GO — the P1 fixed here).
- `DELIB-FAB08-REMEDIATION-20260610` — owner decision: fix + purge + doctor auto-clean; HYG-022 deferred.

## Owner Decisions / Input

Per `DELIB-FAB08-REMEDIATION-20260610` (AskUserQuestion, 2026-06-10): HYG-053 = `_force_rmtree` helper +
one-time purge + doctor WARN/auto-prune for stale `_test_*` >24h; HYG-022 (Agent_Red `application.toml`
backfill) deferred to a separate Agent-Red-scoped bridge. The `-004` NO-GO is an implementation-revision
issue (Owner Action Required: None per the verdict); no new owner decision was required to fix it.

## Backlog Visibility

`GOV-STANDING-BACKLOG-001`: this change performs **no bulk backlog/MemBase operation** — it writes nothing
to `work_items` or `groundtruth.db`. The one-time purge (unchanged from `-003`) produced an explicit
inventory of what was removed (234 `applications/_test_*` slots found → 234 purged → 0 remaining;
non-`_test_*` dirs preserved: `Agent_Red`). The deletions are of gitignored, regenerable test artifacts,
not canonical backlog state.

## Isolation Placement Compliance

`ADR-ISOLATION-APPLICATION-PLACEMENT-001`: all changes are in-root under `E:\GT-KB\` — the test files under
`groundtruth-kb/tests/`, the doctor source under `groundtruth-kb/src/groundtruth_kb/project/`, the tests
under `platform_tests/scripts/`, and this report under `E:\GT-KB\bridge\`. The runtime-floor fix touches
only the existing in-root helper bodies; it relocates nothing, creates no out-of-root artifact, and the
one-time purge (already executed in `-003`) preserved the only real slot (`Agent_Red`).

## What Changed Since -003

1. **`_force_rmtree` / `_force_remove_tree` made py3.11-compatible** in all four files
   (`conftest.py`, `test_cli.py`, `test_scaffold_isolation.py`, `doctor.py`): version-adaptive
   `onexc` (3.12+) / `onerror` (3.11) dispatch; `import sys` added where missing.
2. **Signature-compat regression added** to `platform_tests/scripts/test_fab08_slot_leak_fix.py`:
   `test_force_remove_tree_uses_onerror_on_py311_floor`, `test_force_remove_tree_uses_onexc_on_py312_plus`,
   and the parametrized `test_rmtree_helpers_are_runtime_floor_compatible` (4 files).

Everything else (the robust remover behavior, the doctor auto-prune, the purge, the GO constraints) is
unchanged from the verified-by-inspection `-003` content.

## Spec-Derived Verification Plan

| Spec / requirement | Derived test | Result |
|---|---|---|
| P1 runtime-floor fix — helper uses `onerror` (not `onexc`) on the declared >=3.11 floor | `test_force_remove_tree_uses_onerror_on_py311_floor` (monkeypatch `sys.version_info`/`shutil.rmtree`) | PASS |
| runtime — helper uses `onexc` on 3.12+ | `test_force_remove_tree_uses_onexc_on_py312_plus` | PASS |
| structural floor guard — every helper file carries `onexc`+`onerror` under a `version_info` guard | `test_rmtree_helpers_are_runtime_floor_compatible` (4 params: doctor.py, conftest.py, test_cli.py, test_scaffold_isolation.py) | PASS (4/4) |
| HYG-053 root cause — robust read-only `.git` removal without silent failure | `test_force_remove_tree_clears_readonly` | PASS |
| GO constraint — cleanup fails LOUDLY (no `ignore_errors` swallow) | `test_force_remove_tree_fails_loudly_on_missing` | PASS |
| doctor auto-prune — stale `_test_*` >24h pruned + WARN; fresh/non-`_test_*`/real apps preserved | `test_check_stale_test_slots_prunes_old_keeps_fresh` + clean-state tests | PASS |
| application-slot contract — no `_test_*` remains; only real slots remain | live doctor check `_check_stale_test_slots(E:\GT-KB)` | PASS (`no stale _test_* slots (>24h)`) |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `ruff check` + `ruff format --check` on all changed `.py` | PASS (clean) |

## Commands Run + Observed Results

All commands run with the platform interpreter `groundtruth-kb/.venv/Scripts/python.exe`. Because the
root `pyproject.toml` is Agent Red's (HYG-024/FAB-12), the platform package is exercised with
`PYTHONPATH=E:\GT-KB\groundtruth-kb\src` (the documented platform invocation), not via the broken root
pytest config.

- `python -m pytest platform_tests/scripts/test_fab08_slot_leak_fix.py -q` → **11 passed in 0.32s**
  (5 original + 6 new runtime-floor regression tests).
- `python -m ruff check <5 changed files>` → **All checks passed!**
- `python -m ruff format --check <5 changed files>` → **5 files already formatted** (exit 0).
- `python -m pytest groundtruth-kb/tests/test_scaffold_isolation.py -q` → **19 passed, 2 failed**. The 2
  failures (`test_tp14_local_only_matches_golden_fixture`, `test_tp15_dual_agent_matches_golden_fixture`)
  are the **pre-existing HYG-023 golden-fixture byte mismatch** in scaffold output
  `.claude/hooks/bridge-compliance-gate.py` (FAB-22 scope) — identical to the `-003` run, NOT this change.
  The 19 passing tests include the ones exercising `_force_rmtree` at the changed sites, confirming the
  version-adaptive dispatch did not regress the cleanup path.
- `_check_stale_test_slots(Path('E:/GT-KB'))` (live) → `status='pass'`, `message='no stale _test_* slots (>24h)'`.

## Acceptance Criteria Check

1. ✅ P1 cleared: all four helpers are py3.11-compatible (version-adaptive `onexc`/`onerror`); the package
   floor stays `>=3.11`; a signature-compat regression prevents recurrence.
2. ✅ `_force_rmtree`/`_force_remove_tree` still perform robust read-only `.git` removal and fail loudly.
3. ✅ Doctor auto-prune unchanged; live check reports no stale slots; `Agent_Red` preserved.
4. ✅ FAB-08 suite 11/11; affected scaffold suite 19 pass + 2 pre-existing HYG-023 fails; ruff-clean.

## Constraints Honored (from the GO)

- HYG-022 kept OUT (no Agent_Red `application.toml` change).
- Deleted only `applications/_test_*`; `Agent_Red` preserved.
- `_force_rmtree`/`_force_remove_tree` fail loudly (no `ignore_errors`).
- All edits stayed within the GO'd `target_paths` (the impl-start packet gates Write/Edit to them).

## Out-of-Scope Follow-Ons (unchanged from -003; not done — would exceed GO'd target_paths)

- `groundtruth-kb/tests/test_core_spec_intake.py` and
  `groundtruth-kb/tests/adopter/test_golden_fixture_diff_per_version.py` carry the same
  `shutil.rmtree(..., ignore_errors=True)` sandbox-cleanup pattern but are NOT in FAB-08's `target_paths`.
- Consolidating the 4×-duplicated helper into one shared test-util (now also carrying the version-adaptive
  dispatch) is a follow-on requiring expanded `target_paths`.
- The 2 `test_scaffold_isolation.py` golden-fixture failures are HYG-023 (FAB-22 scope), not FAB-08.

## Bridge Protocol Compliance

Filed at `bridge/gtkb-fab-08-slot-leak-fix-005.md` with a matching `REVISED` line inserted at the top of
the FAB-08 entry in `bridge/INDEX.md` (above the `-004` NO-GO); append-only — no prior version deleted or
rewritten. `GOV-FILE-BRIDGE-AUTHORITY-001` (INDEX.md is canonical) is honored; Loyal Opposition reviews
this revised report and responds with `VERIFIED` or `NO-GO`.

## Recommended Commit Type

`fix:` — corrects the Windows `rmtree` slot-leak defect AND the py3.11 runtime-floor break (with a small
`feat:`-class doctor auto-prune + the runtime-floor regression tests).

## Commit Status

Changes are implemented and verified but NOT committed (commit pending owner direction + Codex `VERIFIED`,
per commit discipline). On `VERIFIED`, the changed files can be committed with the `fix:` type above and
WI-4420 resolved.
