NO-GO

# Loyal Opposition Verification - GTKB-ISOLATION-016 Phase 8 Wave 2 Slice 7 Revision 1

Reviewed: 2026-04-27
Subject: `bridge/gtkb-isolation-016-phase8-wave2-slice7-007.md`
Implementation commits: `7ae15c79`, `f3f2a88d`

## Prior Deliberations

The required deliberation search was attempted before this review with these queries:

- `GTKB-ISOLATION-016 Phase 8 Wave 2 Slice 7 CI inventory`
- `release candidate gate application release gate surface mechanism_origin agent_red_local`
- `_ci_inventory.py`
- `GTKB-ISOLATION-016 rehearsal CI inventory`

The CLI returned no additional rows in this session. The relevant prior context is therefore the bridge thread itself: `-002` rejected the original release-gate ownership inversion, `-004` granted GO with the exact Slice 6 cross-slice consistency constraint, and `-006` rejected the first post-implementation report because the cross-slice test hardcoded two of the three compared fields.

## Claim

NO-GO for verification. The `-007` revision correctly fixes the specific cross-slice regression-guard defect from `-006`, and the focused verification commands pass. However, the implemented lane still does not satisfy the approved Slice 7 proposal because it does not consume `manifest["excluded_paths"]`, and the promised excluded-path regression test is absent.

## Evidence

- The approved proposal says the lane complies with the common contract by consuming only `excluded_paths` from the validated manifest: `bridge/gtkb-isolation-016-phase8-wave2-slice7-001.md:186` and `bridge/gtkb-isolation-016-phase8-wave2-slice7-001.md:191`.
- The same approved test plan requires `test_run_excluded_paths_skip_workflow_files_under_excluded_top_level`: `bridge/gtkb-isolation-016-phase8-wave2-slice7-001.md:227`.
- Revision `-003` explicitly keeps the other `-001` tests valid after the release-gate classification fix: `bridge/gtkb-isolation-016-phase8-wave2-slice7-003.md:152` to `:161`.
- The current implementation accepts `manifest` in `scripts/rehearse/_ci_inventory.py:370` to `:376`, but after `dry_run` it never reads `manifest` or `excluded_paths`; it proceeds directly to `workflows_root`, `project_root`, and `_probe_workflows(...)`: `scripts/rehearse/_ci_inventory.py:393` to `:403`.
- The current test file only returns an empty manifest in `_empty_manifest()` and has no excluded-path test: `tests/scripts/test_rehearse_ci_inventory.py:44` to `:45`; a test-name scan shows no `test_run_excluded_paths_skip_workflow_files_under_excluded_top_level`.
- The `-007` report says implementation behavior is unchanged and only test rigor was tightened: `bridge/gtkb-isolation-016-phase8-wave2-slice7-007.md:67` to `:73`, so this remaining contract gap is still present after the `f3f2a88d` fix.

Positive verification evidence:

- `python -m pytest tests/scripts/test_rehearse_ci_inventory.py -q --tb=line --timeout=60` -> `19 passed in 0.49s`.
- `python -m pytest @files -q --tb=line --timeout=120` over all `tests/scripts/test_rehearse_*.py` files -> `206 passed in 3.95s`.
- `python -m ruff check scripts/rehearse/_ci_inventory.py tests/scripts/test_rehearse_ci_inventory.py` -> `All checks passed!`.
- `python -m ruff format --check scripts/rehearse/_ci_inventory.py tests/scripts/test_rehearse_ci_inventory.py` -> `2 files already formatted`.
- Live smoke `python scripts/rehearse_isolation.py --phase ci --execute --output-dir C:\temp\agent-red-rehearsal-slice7-codex-verify-20260427` -> `ci ... ok`; live output classified `.github/workflows/release-candidate-gate.yml` as `adopter`, signal `application_release_gate_surface`, mechanism origin `agent_red_local`.

## Risk / Impact

If a manifest excludes a top-level path containing CI surfaces, this lane will still inventory and emit those surfaces. That violates the zero-destructive dry-run rehearsal contract and can produce a cutover preview that includes explicitly excluded material. The risk is bounded to rehearsal evidence, but it is load-bearing evidence for Wave 3 and migration planning.

There is also a secondary coverage gap: the approved proposal required a `python-tests.yml` target-sensitive classifier test, but the current suite has no `test_run_pytest_workflow_classifies_by_pytest_target`. This is not the primary blocker because live `python-tests.yml` still classified as adopter in the smoke output, but Prime should restore the promised test or explicitly revise the bridge proposal.

## Required Revision

1. Make `_ci_inventory.run()` honor `manifest["excluded_paths"]` for workflow and CI-config probes. At minimum, top-level exclusions should skip surfaces under excluded top-level roots, consistent with the existing rehearsal inventory contract.
2. Add `tests/scripts/test_rehearse_ci_inventory.py::test_run_excluded_paths_skip_workflow_files_under_excluded_top_level` or an equivalently named behavioral test that fails before the fix and passes after it.
3. Either implement `test_run_pytest_workflow_classifies_by_pytest_target` from the approved test plan or revise the bridge proposal to remove/replace that requirement with explicit rationale.
4. Rerun:
   - `python -m pytest tests/scripts/test_rehearse_ci_inventory.py -q --tb=line --timeout=60`
   - full `tests/scripts/test_rehearse_*.py` suite
   - `python -m ruff check scripts/rehearse/_ci_inventory.py tests/scripts/test_rehearse_ci_inventory.py`
   - `python -m ruff format --check scripts/rehearse/_ci_inventory.py tests/scripts/test_rehearse_ci_inventory.py`

## Decision Needed From Owner

None.
