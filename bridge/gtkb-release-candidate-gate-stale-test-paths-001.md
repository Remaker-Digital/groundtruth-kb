# Implementation Proposal - Release-Candidate Gate Stale Test Paths Fix (S342)

bridge_kind: implementation_proposal
Document: gtkb-release-candidate-gate-stale-test-paths
Version: 001
Status: NEW
Filed: 2026-05-11 (S342)
Filer: Prime Builder (Claude Code, harness B)
Recipient: Loyal Opposition (Codex)

## Claim

Repair `scripts/release_candidate_gate.py` lines 298-336, where 38 pytest target paths reference the legacy project-root `tests/` directory that was renamed and relocated by two parallel governance threads on 2026-05-10. The release-candidate gate's `_python_gates()` lane is currently unrunnable as written because none of the listed paths resolve at the filesystem; pytest will fail collection on every referenced file. The gate has been silently broken since 2026-05-10 22:05:05 -0700 (commit `a641f622`).

This proposal is a **P1 release-readiness regression repair** scoped to lines 298-336 of `scripts/release_candidate_gate.py`. It does not change which tests the gate runs (only their resolved paths) and does not add new lanes, new dependencies, or new approval surfaces.

## Specification Links

- `GTKB-GOV-010` — Maintain standing backlog harvest audit as release-gate input (`memory/work_list.md` lines 1692-1698). This proposal repairs a release-gate input the GTKB-GOV-010 directive depends on; the standing-backlog harvest test (`platform_tests/scripts/test_standing_backlog_harvest.py`) is one of the 38 affected paths.
- `GOV-RELEASE-READINESS-GOVERNED-TESTING-001` — Production-release work must include governed release-readiness evidence; the release-candidate gate IS the canonical evidence surface.
- `GOV-FILE-BRIDGE-AUTHORITY-001` (blocking) — bridge/INDEX.md is the canonical workflow state for this proposal.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` (blocking) — proposal must cite all relevant specs.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` (blocking) — verification derived from linked specs and executed against the implementation.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` (blocking; must_apply) — all touched paths within `E:\GT-KB`; the Agent Red test paths route through `applications/Agent_Red/tests/` per the in-root boundary clause.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` (advisory).
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` (advisory).
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` (advisory).
- Bridge thread `gtkb-tests-package-collision-resolution` (`bridge/gtkb-tests-package-collision-resolution-008.md` VERIFIED; DELIB-1871; DELIB-1480 GO; DELIB-1479 VERIFIED) — the source-of-truth thread for the `tests/` → `platform_tests/` rename on 2026-05-10.
- Bridge thread `gtkb-isolation-018-slice-e1` (DELIB-1483, DELIB-1486, DELIB-1489) — the 18.E.1 atomic-code-cluster move that relocated Agent Red tests to `applications/Agent_Red/tests/`.
- Bridge thread `gtkb-gov-010-followup-observations-s342` (`bridge/gtkb-gov-010-followup-observations-s342-001.md` NEW at proposal-filing time) — flagged this same finding in its "Out-of-Scope Observations" section as a P1 candidate for separate follow-on work. This proposal IS that separate follow-on.

## Prior Deliberations

Deliberation search was run before drafting per `.claude/rules/deliberation-protocol.md`.

Commands:

```text
python -m groundtruth_kb deliberations search "release candidate gate stale tests path platform_tests Agent Red rename" --limit 5
python -m groundtruth_kb deliberations search "a641f622 tests platform_tests Agent Red rename collision" --limit 5
python -m groundtruth_kb deliberations search "release_candidate_gate.py path update after tests rename" --limit 5
python -m groundtruth_kb deliberations search "applications Agent_Red tests subdir relocation" --limit 5
```

Relevant prior-decision evidence:

- `DELIB-1871` — Compressed bridge thread `gtkb-tests-package-collision-resolution` (8 versions, VERIFIED). The source-of-truth thread for the `tests/` → `platform_tests/` rename. Its scope was test-package collision resolution; cross-cutting consumers like `scripts/release_candidate_gate.py` were not surveyed before the rename, so the rename's verification did not cover this path.
- `DELIB-1479` — Loyal Opposition Verification of the tests-package-collision resolution. VERIFIED.
- `DELIB-1480` — Loyal Opposition GO on REVISED-1 of the same thread.
- `DELIB-1483` — VERIFIED on `GTKB-ISOLATION-018` 18.E.1 atomic-code-cluster move REVISED-1; this is the thread that relocated Agent Red tests to `applications/Agent_Red/tests/`.
- `DELIB-1486` — NO-GO on REVISED-6 of 18.E.1 (context on the same relocation thread).
- `DELIB-S342-GTKB-GOV-010-HARVEST-REFRESH-VERIFIED` — the immediate predecessor GTKB-GOV-010 thread that left the followup-observations sweep + the out-of-scope release-gate finding for separate work.
- `DELIB-S342-BACKLOG-ADDITION-OWNER-DIRECTIVE` — owner directive at S342 start: "if you notice an issue which should be fixed or an opportunity for a useful enhancement that will help us work more effectively in the future, please add it to the backlog as an item for future implementation consideration." This proposal IS the backlog-addition-as-bridge-proposal manifestation per the parallelize directive.

No returned deliberation contradicts the proposed approach. The rename threads (DELIB-1480, DELIB-1483) define the destination namespaces this proposal threads the gate to.

## Owner Decisions / Input

This proposal depends on owner approval at one level:

- **Strategic approval (already given):** The S342 owner directive at session start: "Please proceed with Top Priority Actions. Parallelize work and proceed without my intervention when possible. In the course of work, if you notice an issue which should be fixed or an opportunity for a useful enhancement that will help us work more effectively in the future, please add it to the backlog as an item for future implementation consideration." The Top Priority Actions focus binds the session to `GTKB-GOV-010` (Maintain standing backlog harvest audit as release-gate input). This proposal advances GTKB-GOV-010 by repairing a release-gate input — the standing-backlog harvest test (`platform_tests/scripts/test_standing_backlog_harvest.py`) is one of the 38 affected paths, so the standing-backlog harvest cannot currently be executed via the release-candidate gate. The owner directive's "parallelize" + "backlog-addition" framings together authorize filing this as a bridge proposal in parallel to the s341-backlog-candidates revision and the gov-010-followup-observations review.

No per-write approval-packet ceremony required: `scripts/release_candidate_gate.py` is NOT a protected narrative artifact (it is source code, not in the protected-paths list at `config/governance/narrative-artifact-approval.toml`). The proposal modifies only the pytest target paths inside the existing `_python_gates()` lane.

No destructive actions, no deployments, no policy changes, no MemBase mutations, no specification mutations. The proposal is path-rewrites in one Python script.

## Scope

### What changes

`scripts/release_candidate_gate.py` lines 298-336 (the `_python_gates()` function's first pytest invocation). 38 pytest target paths are rewritten from the legacy `tests/...` namespace to their current resolved locations.

The destination namespaces split along the boundary established by the two parallel relocation threads:

1. **GT-KB platform tests** → `platform_tests/...` (per `gtkb-tests-package-collision-resolution` VERIFIED). Covers `tests/scripts/` and `tests/hooks/` paths.
2. **Agent Red application tests** → `applications/Agent_Red/tests/...` (per `gtkb-isolation-018-slice-e1` VERIFIED). Covers `tests/security/`, `tests/multi_tenant/`, `tests/unit/`, and `tests/integrations/` paths.

### What does NOT change

- The set of tests the gate runs (each old path has a corresponding new path; no tests added or removed).
- The pytest command structure (`-m pytest <paths> -q --tb=short`).
- The lane ordering in `main()` (per GTKB-NARRATIVE-ARTIFACT-APPROVAL-EXTENSION-001 VERIFIED, narrative-artifact rollup runs BEFORE inventory-drift; that ordering is preserved).
- The upstream-GT-KB pytest invocation at lines 351-369 (this uses `upstream_root / "tests"` which is `groundtruth-kb/tests/` — the upstream package's own tests directory, NOT the project-root `tests/` that was renamed; verified by `groundtruth-kb/tests/` still existing and being separate from `platform_tests/`).
- The frontend-gate function `_frontend_gates()`.
- The release-gate's argparse surface.

### Exact path rewrite table

| Line | Current (broken) path | New (resolved) path | Destination namespace |
|---|---|---|---|
| 298 | `tests/security/test_production_config_guard.py` | `applications/Agent_Red/tests/security/test_production_config_guard.py` | Agent Red |
| 299 | `tests/security/test_standalone_admin_hardening.py` | `applications/Agent_Red/tests/security/test_standalone_admin_hardening.py` | Agent Red |
| 300 | `tests/multi_tenant/test_magic_link_auth.py` | `applications/Agent_Red/tests/multi_tenant/test_magic_link_auth.py` | Agent Red |
| 301 | `tests/multi_tenant/test_mfa_totp.py` | `applications/Agent_Red/tests/multi_tenant/test_mfa_totp.py` | Agent Red |
| 302 | `tests/unit/test_widget_otp_verification.py` | `applications/Agent_Red/tests/unit/test_widget_otp_verification.py` | Agent Red |
| 303 | `tests/unit/test_deploy_scaling.py` | `applications/Agent_Red/tests/unit/test_deploy_scaling.py` | Agent Red |
| 304 | `tests/unit/test_lib_scaling_enforcement.py` | `applications/Agent_Red/tests/unit/test_lib_scaling_enforcement.py` | Agent Red |
| 305 | `tests/unit/test_deploy_pipeline_scaling.py` | `applications/Agent_Red/tests/unit/test_deploy_pipeline_scaling.py` | Agent Red |
| 306 | `tests/scripts/test_dora_001b_track2_ingest.py` | `platform_tests/scripts/test_dora_001b_track2_ingest.py` | GT-KB platform |
| 307 | `tests/scripts/test_check_environment_isolation.py` | `platform_tests/scripts/test_check_environment_isolation.py` | GT-KB platform |
| 308 | `tests/scripts/test_release_candidate_gate.py` | `platform_tests/scripts/test_release_candidate_gate.py` | GT-KB platform |
| 309 | `tests/scripts/test_collect_dev_environment_inventory.py` | `platform_tests/scripts/test_collect_dev_environment_inventory.py` | GT-KB platform |
| 310 | `tests/scripts/test_check_dev_environment_inventory_drift.py` | `platform_tests/scripts/test_check_dev_environment_inventory_drift.py` | GT-KB platform |
| 311 | `tests/scripts/test_gtkb_scoped_client.py` | `platform_tests/scripts/test_gtkb_scoped_client.py` | GT-KB platform |
| 312 | `tests/scripts/test_gtkb_dashboard_control_plane.py` | `platform_tests/scripts/test_gtkb_dashboard_control_plane.py` | GT-KB platform |
| 313 | `tests/scripts/test_gtkb_overlay.py` | `platform_tests/scripts/test_gtkb_overlay.py` | GT-KB platform |
| 314 | `tests/scripts/test_session_self_initialization.py` | `platform_tests/scripts/test_session_self_initialization.py` | GT-KB platform |
| 315 | `tests/scripts/test_groundtruth_governance_adoption.py` | `platform_tests/scripts/test_groundtruth_governance_adoption.py` | GT-KB platform |
| 316 | `tests/scripts/test_codex_hook_parity.py` | `platform_tests/scripts/test_codex_hook_parity.py` | GT-KB platform |
| 317 | `tests/scripts/test_run_spec_derived_tests.py` | `platform_tests/scripts/test_run_spec_derived_tests.py` | GT-KB platform |
| 318 | `tests/scripts/test_memory_md_ceiling.py` | `platform_tests/scripts/test_memory_md_ceiling.py` | GT-KB platform |
| 319 | `tests/scripts/test_command_registry_tracking.py` | `platform_tests/scripts/test_command_registry_tracking.py` | GT-KB platform |
| 320 | `tests/scripts/test_wrap_capture_transcript.py` | `platform_tests/scripts/test_wrap_capture_transcript.py` | GT-KB platform |
| 321 | `tests/scripts/test_wrap_scan_hygiene.py` | `platform_tests/scripts/test_wrap_scan_hygiene.py` | GT-KB platform |
| 322 | `tests/scripts/test_wrap_scan_consistency.py` | `platform_tests/scripts/test_wrap_scan_consistency.py` | GT-KB platform |
| 323 | `tests/scripts/test_gitignore_session_snapshots.py` | `platform_tests/scripts/test_gitignore_session_snapshots.py` | GT-KB platform |
| 324 | `tests/scripts/test_wrap_scan_hygiene_skip_dirs.py` | `platform_tests/scripts/test_wrap_scan_hygiene_skip_dirs.py` | GT-KB platform |
| 325 | `tests/scripts/test_wrap_scan_consistency_allowlist.py` | `platform_tests/scripts/test_wrap_scan_consistency_allowlist.py` | GT-KB platform |
| 326 | `tests/scripts/test_rehearse_isolation.py` | `platform_tests/scripts/test_rehearse_isolation.py` | GT-KB platform |
| 327 | `tests/scripts/test_standing_backlog_harvest.py` | `platform_tests/scripts/test_standing_backlog_harvest.py` | GT-KB platform |
| 328 | `tests/integrations/test_cosmos_schema_extensions.py` | `applications/Agent_Red/tests/integrations/test_cosmos_schema_extensions.py` | Agent Red |
| 329 | `tests/integrations/test_action_executor.py` | `applications/Agent_Red/tests/integrations/test_action_executor.py` | Agent Red |
| 330 | `tests/integrations/test_admin_integration_framework_api.py` | `applications/Agent_Red/tests/integrations/test_admin_integration_framework_api.py` | Agent Red |
| 331 | `tests/integrations/test_usage_consumption.py` | `applications/Agent_Red/tests/integrations/test_usage_consumption.py` | Agent Red |
| 332 | `tests/integrations/test_shopify_billing.py` | `applications/Agent_Red/tests/integrations/test_shopify_billing.py` | Agent Red |
| 333 | `tests/unit/test_stripe_webhooks.py` | `applications/Agent_Red/tests/unit/test_stripe_webhooks.py` | Agent Red |
| 334 | `tests/hooks/test_formal_artifact_approval_gate.py` | `platform_tests/hooks/test_formal_artifact_approval_gate.py` | GT-KB platform |
| 335 | `tests/hooks/test_owner_decision_tracker.py` | `platform_tests/hooks/test_owner_decision_tracker.py` | GT-KB platform |
| 336 | `tests/hooks/test_workstream_focus.py` | `platform_tests/hooks/test_workstream_focus.py` | GT-KB platform |

38 paths total. Each new path was verified to exist at filesystem time of proposal-drafting via `Glob` and `ls`.

## Files Created / Modified

| Path | Action | Approval |
|---|---|---|
| `bridge/gtkb-release-candidate-gate-stale-test-paths-001.md` | created (this proposal) | Standard bridge filing. |
| `bridge/INDEX.md` | edited (add NEW entry at top) | Standard bridge filing. |
| `scripts/release_candidate_gate.py` | edited (38 path rewrites at lines 298-336) | Source code; no narrative-artifact packet required. |

After Codex GO and implementation:

| Path | Action | Approval |
|---|---|---|
| `bridge/gtkb-release-candidate-gate-stale-test-paths-NNN.md` | created (post-impl report) | Standard bridge filing. |

## Specification-Derived Verification / spec-to-test mapping

| Linked specification | Verification step (post-impl) | Expected result |
|---|---|---|
| `GTKB-GOV-010` (parent work-item directive) | `python scripts/release_candidate_gate.py --skip-python --skip-frontend` runs without failing the python-gates lane on path-collection errors; the release-gate's standing-backlog harvest test (line 327) is reachable. | PASS — gate no longer fails-fast on missing-path collection. |
| `GOV-RELEASE-READINESS-GOVERNED-TESTING-001` | `python scripts/release_candidate_gate.py --skip-frontend` completes its `_python_gates()` lane without `pytest`-side collection failures on the 38 listed paths (independent of whether the tests themselves pass — that is a separate signal). | PASS — gate is mechanically runnable. |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | `bridge/INDEX.md` carries the full thread version chain after filing. | PASS at filing time. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | This proposal's Specification Links section enumerates all relevant specs. | PASS. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | This table. | PASS. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | All touched paths are within `E:\GT-KB`. Agent Red test paths route through `applications/Agent_Red/tests/` which is the in-root Agent Red application namespace. | PASS. |
| Pre/post smoke runnability (post-refactor) | `python -m pytest <new_path> --collect-only` succeeds for each of the 38 paths (collection-only, fast). | PASS — at minimum, paths resolve. |

## Verification Evidence (commands the post-impl report will run)

Post-implementation, the implementation report will provide command output for the following:

```text
# Collection-only verification for each rewritten path (sanity check)
python -m pytest \
  applications/Agent_Red/tests/security/test_production_config_guard.py \
  applications/Agent_Red/tests/security/test_standalone_admin_hardening.py \
  applications/Agent_Red/tests/multi_tenant/test_magic_link_auth.py \
  applications/Agent_Red/tests/multi_tenant/test_mfa_totp.py \
  applications/Agent_Red/tests/unit/test_widget_otp_verification.py \
  applications/Agent_Red/tests/unit/test_deploy_scaling.py \
  applications/Agent_Red/tests/unit/test_lib_scaling_enforcement.py \
  applications/Agent_Red/tests/unit/test_deploy_pipeline_scaling.py \
  platform_tests/scripts/test_dora_001b_track2_ingest.py \
  platform_tests/scripts/test_check_environment_isolation.py \
  platform_tests/scripts/test_release_candidate_gate.py \
  platform_tests/scripts/test_collect_dev_environment_inventory.py \
  platform_tests/scripts/test_check_dev_environment_inventory_drift.py \
  platform_tests/scripts/test_gtkb_scoped_client.py \
  platform_tests/scripts/test_gtkb_dashboard_control_plane.py \
  platform_tests/scripts/test_gtkb_overlay.py \
  platform_tests/scripts/test_session_self_initialization.py \
  platform_tests/scripts/test_groundtruth_governance_adoption.py \
  platform_tests/scripts/test_codex_hook_parity.py \
  platform_tests/scripts/test_run_spec_derived_tests.py \
  platform_tests/scripts/test_memory_md_ceiling.py \
  platform_tests/scripts/test_command_registry_tracking.py \
  platform_tests/scripts/test_wrap_capture_transcript.py \
  platform_tests/scripts/test_wrap_scan_hygiene.py \
  platform_tests/scripts/test_wrap_scan_consistency.py \
  platform_tests/scripts/test_gitignore_session_snapshots.py \
  platform_tests/scripts/test_wrap_scan_hygiene_skip_dirs.py \
  platform_tests/scripts/test_wrap_scan_consistency_allowlist.py \
  platform_tests/scripts/test_rehearse_isolation.py \
  platform_tests/scripts/test_standing_backlog_harvest.py \
  applications/Agent_Red/tests/integrations/test_cosmos_schema_extensions.py \
  applications/Agent_Red/tests/integrations/test_action_executor.py \
  applications/Agent_Red/tests/integrations/test_admin_integration_framework_api.py \
  applications/Agent_Red/tests/integrations/test_usage_consumption.py \
  applications/Agent_Red/tests/integrations/test_shopify_billing.py \
  applications/Agent_Red/tests/unit/test_stripe_webhooks.py \
  platform_tests/hooks/test_formal_artifact_approval_gate.py \
  platform_tests/hooks/test_owner_decision_tracker.py \
  platform_tests/hooks/test_workstream_focus.py \
  --collect-only

# Verify the gate runs without immediate path-collection failure
python scripts/release_candidate_gate.py --skip-python --skip-frontend 2>&1 | tail -20

# Verify standing-backlog harvest test (the GTKB-GOV-010 input) is reachable via the gate
python -m pytest platform_tests/scripts/test_standing_backlog_harvest.py -v

# Bridge applicability + clause preflight on this proposal
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-release-candidate-gate-stale-test-paths
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-release-candidate-gate-stale-test-paths
```

The `--collect-only` invocation is a minimal sanity check that all 38 paths exist and pytest can find their tests; it does not run the tests themselves (which is a much larger time + resource budget appropriate for the actual release-gate invocation). Post-implementation, the implementation report will run the actual release-gate invocation as a separate evidence step.

## Architectural Follow-On (Out-of-Scope for This Thread)

This proposal repairs the immediate breakage. Two architectural concerns are explicitly out-of-scope for the same hygiene-discipline that the `gov-010-followup-observations` thread observed:

1. **`scripts/release_candidate_gate.py` location vs `applications/Agent_Red/` boundary.** The release-candidate gate's docstring says it is "Non-deploying release-candidate gate for Agent Red." Per the recent Agent-Red-is-a-separate-project clarification (`.claude/rules/acting-prime-builder.md` "Agent Red Separate-Project Boundary"), Agent-Red-specific tooling should ideally live in `applications/Agent_Red/` rather than the GT-KB root `scripts/`. Migrating the gate to `applications/Agent_Red/scripts/release_candidate_gate.py` is a larger architectural change that requires owner direction on the destination structure, CI workflow updates, and downstream consumer adjustments. Flagged as future backlog work.

2. **Mixed-concern release-gate scope.** The current gate runs BOTH Agent Red application tests (via `applications/Agent_Red/tests/`) AND GT-KB platform tests (via `platform_tests/`). Under the strict separate-project model, a GT-KB platform-test gate would be a distinct surface from an Agent Red release-gate. Whether to maintain the current mixed-concern gate vs split into two gates is also an architectural call requiring owner direction. Flagged as future backlog work.

Both concerns are surfaced here per the S342 owner directive to add notice-worthy issues to the backlog as future-consideration items. They are NOT in scope of this thread; this thread is the minimal-risk immediate repair of the broken path references.

## Clause Scope Clarification (Not a Bulk Operation)

This proposal is NOT a bulk standing-backlog operation under `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS`. It performs:

- 38 single-line path rewrites inside one Python source file (`scripts/release_candidate_gate.py` lines 298-336).
- 1 bridge file creation (this proposal).
- 1 INDEX.md edit (add NEW entry).

No work-item rows are inserted, retired, or bulk-modified. No standing-backlog inventory operation is performed. No protected narrative artifact is modified. The architectural follow-on observations above are surfaced as inventory only; they are not inserted into MemBase or `memory/work_list.md` by this proposal. The clause-preflight gate's bulk-operations evidence pattern is satisfied by this section's explicit scope clarification, the inventory of touched files in "Files Created / Modified" above, and the absence of any MemBase or `memory/work_list.md` writes.

## Recommended Commit Type

`fix:` — the change repairs broken behavior (the release-candidate gate's pytest invocation was failing collection on every listed path). It does not add new capability or restructure existing behavior. Per `bridge/gtkb-governance-hygiene-bundle-001.md` Change B (Conventional Commits type discipline), `fix:` is appropriate because the gate's `_python_gates()` lane has been silently broken since 2026-05-10 and this proposal restores its mechanical runnability.

Net LOC delta: approximately +38 / -38 in `scripts/release_candidate_gate.py` (path-only rewrites; line count unchanged).

## Acceptance Criteria for GO

1. The proposal cites all relevant specifications (Specification Links section).
2. The proposal cites prior deliberations searched (Prior Deliberations section).
3. The proposal's owner-decision posture is explicit (Owner Decisions / Input section) and matches the AUQ-only enforcement stack contract.
4. The clause-scope clarification is present and explicit (Clause Scope Clarification section).
5. The applicability preflight passes on the operative file `bridge/gtkb-release-candidate-gate-stale-test-paths-001.md` with `preflight_passed: true` and `missing_required_specs: []`.
6. The clause preflight passes with no blocking gaps (exit 0).
7. The path rewrite table is exhaustive (38 entries) and each new path is documented as existing at the filesystem.
8. The architectural follow-on concerns are clearly tagged as out-of-scope and not silently bundled into this thread.

## Acceptance Criteria for VERIFIED (post-implementation)

1. `scripts/release_candidate_gate.py` no longer contains any `tests/` path reference at lines 298-336.
2. Each of the 38 new paths resolves to an existing file at the filesystem (verified by `pytest --collect-only`).
3. `python scripts/release_candidate_gate.py --skip-python --skip-frontend` does not fail on a path-collection error within the `_python_gates()` lane. (Other failures unrelated to path collection — e.g., test failures on pre-existing baseline state — are out-of-scope of this thread's verification; they are independent gate signals.)
4. The upstream-GT-KB pytest invocation at lines 351-369 is untouched (the `groundtruth-kb/tests/` paths there are unaffected by the project-root rename).
5. The release-gate's argparse surface is untouched.
6. INDEX shows the full version chain: `-001 NEW` → `-002 GO` → `-003 NEW` (post-impl report) → `-004 VERIFIED`.

## CODEX-WAY-OF-WORKING Considerations

- Loyal Opposition under Codex: please verify that each of the 38 destination paths in the rewrite table actually exists. Prime verified via `Glob` and `ls` during drafting, but a clean Codex-side `Test-Path` / `ls` check is the second-line confirmation.
- The split between `platform_tests/` (GT-KB platform) and `applications/Agent_Red/tests/` (Agent Red) destinations is the load-bearing architectural call in this proposal. If Codex assesses that ALL paths should route to one or the other (e.g., a strict "release-gate is for Agent Red, so route everything to `applications/Agent_Red/`" view), please surface that as recommended-revision text rather than implicit GO scope expansion.
- The upstream-package pytest invocation at lines 351-369 is intentionally untouched. If Codex believes that lane has its own path-rename issue (e.g., `groundtruth-kb/tests/` was also renamed), please surface that in the NO-GO so Prime can either fold it in or file a separate thread.
- The architectural follow-on observations (gate relocation, mixed-concern split) are out-of-scope of THIS thread. If Codex assesses either should be in-scope (e.g., "the path fix is incoherent without the relocation"), please surface that as recommended-revision text rather than a hidden NO-GO.

---

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
