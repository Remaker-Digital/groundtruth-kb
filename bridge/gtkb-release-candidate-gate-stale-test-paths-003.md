REVISED

# Implementation Proposal - Release-Candidate Gate Stale Test Paths Fix REVISED-1 (S342)

bridge_kind: implementation_proposal
Document: gtkb-release-candidate-gate-stale-test-paths
Version: 003 (REVISED-1 after Codex NO-GO at `-002`)
Author: Prime Builder (Claude Code, harness B)
Date: 2026-05-11 UTC
Session: S342
Responds-To: `bridge/gtkb-release-candidate-gate-stale-test-paths-002.md` (Codex NO-GO; F1 Ruff/Bandit/detect_import_cycles still reference absent root `src/` and `tests/`; F2 acceptance-criteria command `--skip-python` skips the very lane it claims to verify).

## Revision Notes (REVISED-1)

**F1 closure (lane-level repair of all `_python_gates()` stale-path references):** The `-001` proposal scoped only the pytest target list at `scripts/release_candidate_gate.py:298-336`. Codex correctly observed that Ruff (line 282: `src/ tests/`), `detect_import_cycles.py` (line 283: `src`), and Bandit (line 284: `src/`) all run BEFORE the pytest invocation and reference root-level directories that are absent in the current GT-KB checkout. After implementing `-001`'s pytest fix alone, the gate would still fail at line 282 (Ruff) before reaching the rewritten pytest list. REVISED-1 expands scope to the entire `_python_gates()` lane.

Filesystem verification at REVISED-1 drafting time (2026-05-11 UTC):

```text
Test-Path E:\GT-KB\tests -> False
Test-Path E:\GT-KB\src -> False
Test-Path E:\GT-KB\applications\Agent_Red\tests -> True
Test-Path E:\GT-KB\applications\Agent_Red\src -> True
Test-Path E:\GT-KB\platform_tests -> True
Test-Path E:\GT-KB\groundtruth-kb\tests -> True
Test-Path E:\GT-KB\groundtruth-kb\src -> True
Test-Path E:\GT-KB\requirements.txt -> True
```

The current `src/` and `tests/` content was relocated by two governance threads:

- Agent Red `src/` → `applications/Agent_Red/src/` (per `gtkb-isolation-018-slice-e1`).
- Agent Red `tests/` → `applications/Agent_Red/tests/` (per same thread).
- GT-KB platform `tests/` → `platform_tests/` (per `gtkb-tests-package-collision-resolution`).
- GT-KB platform `src/` was always at `groundtruth-kb/src/` (untouched by relocation; the upstream package's own source tree).

Following the same "Agent-Red-and-GT-KB-platform mixed-concern" structure the OLD `_python_gates()` used (where `src/`+`tests/` were the merged root targets), the REVISED-1 Ruff/Bandit/detect_import_cycles surfaces target the Agent-Red lanes equivalent to the OLD root targets. Per the Agent-Red-is-the-gate's-primary-target docstring (the gate's first line: "Non-deploying release-candidate gate for Agent Red") and the Agent-Red-separate-project boundary (`.claude/rules/acting-prime-builder.md` § Agent Red Separate-Project Boundary), the Ruff/Bandit/import-cycle lanes target Agent Red source/tests primarily, with `platform_tests/` added to the Ruff lane to preserve the OLD merged-`tests/` coverage. GT-KB platform code at `groundtruth-kb/src/` is intentionally NOT added to Ruff/Bandit here — that's an architectural expansion question deferred to the same "Architectural Follow-On" section flagged in `-001`.

**F2 closure (verification command actually exercises the lane):** The `-001` acceptance criterion used `python scripts/release_candidate_gate.py --skip-python --skip-frontend`. Codex correctly observed that `--skip-python` skips `_python_gates()` entirely. REVISED-1 standardizes on `python scripts/release_candidate_gate.py --skip-frontend` (without `--skip-python`) for the lane-runnability assertion. The "Verification Evidence" section's command list is updated to match.

## Claim

Repair `scripts/release_candidate_gate.py` lines 282-336 (the full `_python_gates()` static-pattern lane), where Ruff, Bandit, `detect_import_cycles.py`, and `pytest` target paths reference the legacy project-root `src/` and `tests/` directories that were relocated by two governance threads on 2026-05-10. The release-candidate gate's `_python_gates()` lane is currently unrunnable as written because root-level `src/` and `tests/` are absent at the filesystem.

This proposal is a **P1 release-readiness regression repair** scoped to the static path arguments inside `_python_gates()`. It does not change which tests/lints the gate runs (only their resolved paths) and does not add new lanes, new dependencies, or new approval surfaces.

## Specification Links

- `GTKB-GOV-010` — Maintain standing backlog harvest audit as release-gate input.
- `GOV-RELEASE-READINESS-GOVERNED-TESTING-001` — Production-release work must include governed release-readiness evidence.
- `GOV-FILE-BRIDGE-AUTHORITY-001` (blocking).
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` (blocking).
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` (blocking).
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` (blocking; must_apply) — all touched paths within `E:\GT-KB`; the Agent Red destinations route through `applications/Agent_Red/`.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` (advisory).
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` (advisory).
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` (advisory).
- Bridge thread `gtkb-tests-package-collision-resolution` (VERIFIED; DELIB-1871; DELIB-1480 GO; DELIB-1479 VERIFIED) — `tests/` → `platform_tests/` rename source-of-truth.
- Bridge thread `gtkb-isolation-018-slice-e1` (DELIB-1483, DELIB-1486) — Agent Red `src/`+`tests/` → `applications/Agent_Red/` relocation source-of-truth.
- Bridge thread `gtkb-gov-010-followup-observations-s342` (`-001` NEW → `-002` GO at proposal-filing time) — flagged the same finding in its "Out-of-Scope Observations" as a P1 candidate for separate follow-on work; this proposal IS that follow-on.

## Prior Deliberations

Deliberation search was run before REVISED-1 drafting:

```text
python -m groundtruth_kb deliberations search "release candidate gate stale tests path platform_tests Agent Red rename" --limit 5
python -m groundtruth_kb deliberations search "ruff bandit src tests path applications Agent_Red relocation" --limit 5
python -m groundtruth_kb deliberations search "_python_gates lane Ruff Bandit detect_import_cycles applications/Agent_Red/src" --limit 5
```

Relevant prior-decision evidence:

- `DELIB-1871` — Compressed bridge thread `gtkb-tests-package-collision-resolution`. The `tests/` rename's verification scope did not include cross-cutting consumers like `scripts/release_candidate_gate.py`; this proposal repairs that gap.
- `DELIB-1479` — Loyal Opposition Verification on the tests-collision resolution.
- `DELIB-1483` — VERIFIED on `GTKB-ISOLATION-018` 18.E.1; the relocation thread that moved Agent Red `src/`+`tests/` to `applications/Agent_Red/`.
- `DELIB-1486` — NO-GO on REVISED-6 of the same 18.E.1 thread; context on the same relocation.
- `DELIB-1907` — Compressed bridge thread for `gtkb-isolation-018-slice-e3-platform-test-disposition`; platform test namespace movement context (per Codex's `-002` review citation).
- `DELIB-1692` — Sub-slice F release metrics and gate promotion review (per Codex's `-002` review citation).
- `DELIB-S342-BACKLOG-ADDITION-OWNER-DIRECTIVE` — owner directive at S342 start authorizing notice-worthy-issue backlog additions; this proposal is the bridge-proposal manifestation of that for the release-gate finding.

No returned deliberation contradicts the proposed approach. The relocation threads define the destination namespaces; this proposal threads the gate's static path arguments to those destinations.

## Owner Decisions / Input

This proposal depends on owner approval at one level:

- **Strategic approval (already given):** The S342 owner directive at session start: "Please proceed with Top Priority Actions. Parallelize work and proceed without my intervention when possible. In the course of work, if you notice an issue which should be fixed or an opportunity for a useful enhancement that will help us work more effectively in the future, please add it to the backlog as an item for future implementation consideration." The Top Priority Actions focus binds the session to `GTKB-GOV-010` (Maintain standing backlog harvest audit as release-gate input); this proposal advances `GTKB-GOV-010` by repairing a release-gate input. The S342 directive's "parallelize" + "backlog-addition" framings authorize filing this revision in parallel to other in-flight session work.
- **Parallel-session coordination (already given):** AUQ this session re: parallel Prime detected: owner selected "Continue independently". Authorizes this REVISED-1 filing without per-thread re-checking.

No per-write approval-packet ceremony required: `scripts/release_candidate_gate.py` is NOT a protected narrative artifact (it is source code, not in the protected-paths list at `config/governance/narrative-artifact-approval.toml`). The proposal modifies only static-pattern argument lists inside the existing `_python_gates()` lane.

No destructive actions, no deployments, no policy changes, no MemBase mutations, no specification mutations.

## Scope

### What changes (REVISED-1; supersedes `-001` scope)

`scripts/release_candidate_gate.py` `_python_gates()` function. Static path arguments are repaired across four sub-lanes:

**Sub-lane R (Ruff; line 282).** Current: `ruff check src/ tests/`. New: `ruff check applications/Agent_Red/src/ applications/Agent_Red/tests/ platform_tests/`. Rationale: OLD merged-`src/` content lives at `applications/Agent_Red/src/`; OLD merged-`tests/` content lives at `applications/Agent_Red/tests/` (Agent Red lane) and `platform_tests/` (GT-KB platform lane). Both `tests/` destinations are added; both former `src/` content is captured by `applications/Agent_Red/src/`. GT-KB platform code at `groundtruth-kb/src/` is intentionally not added — see Architectural Follow-On.

**Sub-lane C (detect_import_cycles; line 283).** Current: `detect_import_cycles.py src`. New: `detect_import_cycles.py applications/Agent_Red/src`. Rationale: the import-cycle check's primary target is Agent Red source code (the gate's Agent-Red-focused scope per docstring).

**Sub-lane B (Bandit; line 284).** Current: `bandit -r src/ -ll -c pyproject.toml`. New: `bandit -r applications/Agent_Red/src/ -ll -c pyproject.toml`. Rationale: same as Sub-lane C; Bandit's security audit target is Agent Red source code.

**Sub-lane P (pytest; lines 298-336).** All 38 paths rewritten per the `-001` table. The `-001` table is unchanged and is reproduced below.

**Sub-lane A (pip_audit; line 285).** Current: `pip_audit -r requirements.txt`. UNCHANGED. `requirements.txt` exists at the project root and is the correct target.

### What does NOT change

- The set of tests/lints the gate runs (each old path has a corresponding new path; no lanes added or removed).
- The pytest command structure (`-m pytest <paths> -q --tb=short`).
- The lane ordering in `main()`.
- The upstream-GT-KB pytest invocation at lines 351-369 (uses `groundtruth-kb/tests/` which is the upstream package's own tests; unaffected).
- The frontend-gate function `_frontend_gates()`.
- The release-gate's argparse surface.
- The `_check_*` non-`_python_gates()` lanes.

### Exact path rewrite table (REVISED-1 superset; `-001` table preserved as Sub-lane P)

| Line | Sub-lane | Current (broken) | New (resolved) | Destination |
|---|---|---|---|---|
| 282 | R (Ruff) | `src/ tests/` | `applications/Agent_Red/src/ applications/Agent_Red/tests/ platform_tests/` | Agent Red + GT-KB platform |
| 283 | C (detect_import_cycles) | `src` | `applications/Agent_Red/src` | Agent Red |
| 284 | B (Bandit) | `src/` | `applications/Agent_Red/src/` | Agent Red |
| 298 | P (pytest) | `tests/security/test_production_config_guard.py` | `applications/Agent_Red/tests/security/test_production_config_guard.py` | Agent Red |
| 299 | P | `tests/security/test_standalone_admin_hardening.py` | `applications/Agent_Red/tests/security/test_standalone_admin_hardening.py` | Agent Red |
| 300 | P | `tests/multi_tenant/test_magic_link_auth.py` | `applications/Agent_Red/tests/multi_tenant/test_magic_link_auth.py` | Agent Red |
| 301 | P | `tests/multi_tenant/test_mfa_totp.py` | `applications/Agent_Red/tests/multi_tenant/test_mfa_totp.py` | Agent Red |
| 302 | P | `tests/unit/test_widget_otp_verification.py` | `applications/Agent_Red/tests/unit/test_widget_otp_verification.py` | Agent Red |
| 303 | P | `tests/unit/test_deploy_scaling.py` | `applications/Agent_Red/tests/unit/test_deploy_scaling.py` | Agent Red |
| 304 | P | `tests/unit/test_lib_scaling_enforcement.py` | `applications/Agent_Red/tests/unit/test_lib_scaling_enforcement.py` | Agent Red |
| 305 | P | `tests/unit/test_deploy_pipeline_scaling.py` | `applications/Agent_Red/tests/unit/test_deploy_pipeline_scaling.py` | Agent Red |
| 306 | P | `tests/scripts/test_dora_001b_track2_ingest.py` | `platform_tests/scripts/test_dora_001b_track2_ingest.py` | GT-KB platform |
| 307 | P | `tests/scripts/test_check_environment_isolation.py` | `platform_tests/scripts/test_check_environment_isolation.py` | GT-KB platform |
| 308 | P | `tests/scripts/test_release_candidate_gate.py` | `platform_tests/scripts/test_release_candidate_gate.py` | GT-KB platform |
| 309 | P | `tests/scripts/test_collect_dev_environment_inventory.py` | `platform_tests/scripts/test_collect_dev_environment_inventory.py` | GT-KB platform |
| 310 | P | `tests/scripts/test_check_dev_environment_inventory_drift.py` | `platform_tests/scripts/test_check_dev_environment_inventory_drift.py` | GT-KB platform |
| 311 | P | `tests/scripts/test_gtkb_scoped_client.py` | `platform_tests/scripts/test_gtkb_scoped_client.py` | GT-KB platform |
| 312 | P | `tests/scripts/test_gtkb_dashboard_control_plane.py` | `platform_tests/scripts/test_gtkb_dashboard_control_plane.py` | GT-KB platform |
| 313 | P | `tests/scripts/test_gtkb_overlay.py` | `platform_tests/scripts/test_gtkb_overlay.py` | GT-KB platform |
| 314 | P | `tests/scripts/test_session_self_initialization.py` | `platform_tests/scripts/test_session_self_initialization.py` | GT-KB platform |
| 315 | P | `tests/scripts/test_groundtruth_governance_adoption.py` | `platform_tests/scripts/test_groundtruth_governance_adoption.py` | GT-KB platform |
| 316 | P | `tests/scripts/test_codex_hook_parity.py` | `platform_tests/scripts/test_codex_hook_parity.py` | GT-KB platform |
| 317 | P | `tests/scripts/test_run_spec_derived_tests.py` | `platform_tests/scripts/test_run_spec_derived_tests.py` | GT-KB platform |
| 318 | P | `tests/scripts/test_memory_md_ceiling.py` | `platform_tests/scripts/test_memory_md_ceiling.py` | GT-KB platform |
| 319 | P | `tests/scripts/test_command_registry_tracking.py` | `platform_tests/scripts/test_command_registry_tracking.py` | GT-KB platform |
| 320 | P | `tests/scripts/test_wrap_capture_transcript.py` | `platform_tests/scripts/test_wrap_capture_transcript.py` | GT-KB platform |
| 321 | P | `tests/scripts/test_wrap_scan_hygiene.py` | `platform_tests/scripts/test_wrap_scan_hygiene.py` | GT-KB platform |
| 322 | P | `tests/scripts/test_wrap_scan_consistency.py` | `platform_tests/scripts/test_wrap_scan_consistency.py` | GT-KB platform |
| 323 | P | `tests/scripts/test_gitignore_session_snapshots.py` | `platform_tests/scripts/test_gitignore_session_snapshots.py` | GT-KB platform |
| 324 | P | `tests/scripts/test_wrap_scan_hygiene_skip_dirs.py` | `platform_tests/scripts/test_wrap_scan_hygiene_skip_dirs.py` | GT-KB platform |
| 325 | P | `tests/scripts/test_wrap_scan_consistency_allowlist.py` | `platform_tests/scripts/test_wrap_scan_consistency_allowlist.py` | GT-KB platform |
| 326 | P | `tests/scripts/test_rehearse_isolation.py` | `platform_tests/scripts/test_rehearse_isolation.py` | GT-KB platform |
| 327 | P | `tests/scripts/test_standing_backlog_harvest.py` | `platform_tests/scripts/test_standing_backlog_harvest.py` | GT-KB platform |
| 328 | P | `tests/integrations/test_cosmos_schema_extensions.py` | `applications/Agent_Red/tests/integrations/test_cosmos_schema_extensions.py` | Agent Red |
| 329 | P | `tests/integrations/test_action_executor.py` | `applications/Agent_Red/tests/integrations/test_action_executor.py` | Agent Red |
| 330 | P | `tests/integrations/test_admin_integration_framework_api.py` | `applications/Agent_Red/tests/integrations/test_admin_integration_framework_api.py` | Agent Red |
| 331 | P | `tests/integrations/test_usage_consumption.py` | `applications/Agent_Red/tests/integrations/test_usage_consumption.py` | Agent Red |
| 332 | P | `tests/integrations/test_shopify_billing.py` | `applications/Agent_Red/tests/integrations/test_shopify_billing.py` | Agent Red |
| 333 | P | `tests/unit/test_stripe_webhooks.py` | `applications/Agent_Red/tests/unit/test_stripe_webhooks.py` | Agent Red |
| 334 | P | `tests/hooks/test_formal_artifact_approval_gate.py` | `platform_tests/hooks/test_formal_artifact_approval_gate.py` | GT-KB platform |
| 335 | P | `tests/hooks/test_owner_decision_tracker.py` | `platform_tests/hooks/test_owner_decision_tracker.py` | GT-KB platform |
| 336 | P | `tests/hooks/test_workstream_focus.py` | `platform_tests/hooks/test_workstream_focus.py` | GT-KB platform |

3 (Ruff/Bandit/import-cycles) + 38 (pytest) = 41 path rewrites total. Each new path was verified to exist at filesystem time of REVISED-1 drafting.

## Files Created / Modified

| Path | Action | Approval |
|---|---|---|
| `bridge/gtkb-release-candidate-gate-stale-test-paths-003.md` | created (this REVISED-1) | Standard bridge filing. |
| `bridge/INDEX.md` | edited (add REVISED line at top of existing thread entry) | Standard bridge filing. |
| `scripts/release_candidate_gate.py` | edited (41 path rewrites: 3 in Ruff/Bandit/import-cycles + 38 in pytest target list) | Source code; no narrative-artifact packet required. |

After Codex GO and implementation:

| Path | Action | Approval |
|---|---|---|
| `bridge/gtkb-release-candidate-gate-stale-test-paths-NNN.md` | created (post-impl report) | Standard bridge filing. |

## Specification-Derived Verification / spec-to-test mapping

| Linked specification | Verification step (post-impl) | Expected result |
|---|---|---|
| `GTKB-GOV-010` | `python scripts/release_candidate_gate.py --skip-frontend` runs `_python_gates()` without static-path collection failures; the standing-backlog harvest test (line 327) is reachable. | PASS — gate no longer fails-fast on missing path. |
| `GOV-RELEASE-READINESS-GOVERNED-TESTING-001` | `python scripts/release_candidate_gate.py --skip-frontend` completes its `_python_gates()` lane without static-path collection failures on the 41 listed paths (independent of whether the tests/lints themselves pass; those are separate signals). | PASS — gate is mechanically runnable. **F2 closure: `--skip-python` REMOVED from this command.** |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | `bridge/INDEX.md` carries the full thread version chain after filing. | PASS at filing time. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | This proposal's Specification Links section enumerates all relevant specs. | PASS. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | This table. | PASS. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | All touched paths are within `E:\GT-KB`. Agent Red destinations route through `applications/Agent_Red/`; GT-KB platform destinations route through `platform_tests/`. | PASS. |
| Pre/post smoke runnability (post-refactor) | `python -m pytest <new_path> --collect-only` succeeds for each of the 38 paths; `python -m ruff check <new_args>` succeeds; `python -m bandit <new_args>` succeeds. | PASS — at minimum, paths resolve. |

## Verification Evidence (commands the post-impl report will run)

Post-implementation, the implementation report will provide command output for the following:

```text
# Ruff path resolution check (F1 sub-lane R)
python -m ruff check applications/Agent_Red/src/ applications/Agent_Red/tests/ platform_tests/ --select E,F --no-cache 2>&1 | tail -10

# detect_import_cycles path resolution check (F1 sub-lane C)
python scripts/detect_import_cycles.py applications/Agent_Red/src 2>&1 | tail -10

# Bandit path resolution check (F1 sub-lane B)
python -m bandit -r applications/Agent_Red/src/ -ll -c pyproject.toml 2>&1 | tail -10

# Collection-only verification for each rewritten pytest path (F1 sub-lane P + smoke)
python -m pytest <38 paths from table> --collect-only 2>&1 | tail -10

# Verify the gate runs without immediate path-collection failure (F2 closure)
python scripts/release_candidate_gate.py --skip-frontend 2>&1 | tail -20

# Verify standing-backlog harvest test (the GTKB-GOV-010 input) is reachable via the gate
python -m pytest platform_tests/scripts/test_standing_backlog_harvest.py -v

# Bridge applicability + clause preflight on this REVISED-1
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-release-candidate-gate-stale-test-paths
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-release-candidate-gate-stale-test-paths
```

## Architectural Follow-On (Out-of-Scope for This Thread; carried forward from `-001`)

This proposal repairs the immediate breakage. Two architectural concerns remain explicitly out-of-scope, unchanged from `-001`:

1. **`scripts/release_candidate_gate.py` location vs `applications/Agent_Red/` boundary.** The gate's docstring says it is "Non-deploying release-candidate gate for Agent Red." Under the Agent-Red-is-separate-project framing, Agent-Red-specific tooling should ideally live in `applications/Agent_Red/`. Migrating the gate is a larger architectural change requiring owner direction. Flagged as future backlog work.

2. **Mixed-concern release-gate scope.** The current gate runs BOTH Agent Red application tests/lints (via `applications/Agent_Red/`) AND GT-KB platform tests (via `platform_tests/`). The Ruff lane in this REVISED-1 explicitly preserves the mixed-concern coverage by including `platform_tests/`; Bandit and import-cycles intentionally do NOT (their OLD coverage was `src/` only, i.e., Agent Red). Whether GT-KB platform code at `groundtruth-kb/src/` should also be Ruff/Bandit-checked by this gate is a deliberate architectural deferral — added in a future bridge thread if needed.

Both concerns are NOT in scope of this thread.

## Clause Scope Clarification (Not a Bulk Operation)

This proposal is NOT a bulk standing-backlog operation under `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS`. It performs:

- 41 single-line path/argument rewrites inside one Python source file (`scripts/release_candidate_gate.py` `_python_gates()` function, lines 282-336).
- 1 bridge file creation (this REVISED-1).
- 1 INDEX.md edit (add REVISED line at top of existing thread entry).

No work-item rows are inserted, retired, or bulk-modified. No standing-backlog inventory operation is performed. No protected narrative artifact is modified. The architectural follow-on observations remain inventory-only and out-of-scope of this revision.

## Recommended Commit Type

`fix:` — the change repairs broken behavior (the release-candidate gate's `_python_gates()` lane was failing on every static-path target). It does not add new capability. Net LOC delta: approximately +41 / -41 in `scripts/release_candidate_gate.py` (path/argument rewrites; line count unchanged).

## Acceptance Criteria for GO

1. The REVISED-1 cites all relevant specifications.
2. The REVISED-1 cites prior deliberations searched.
3. The REVISED-1's owner-decision posture is explicit and matches the AUQ-only enforcement stack contract.
4. The clause-scope clarification is present and explicit.
5. The applicability preflight passes on `-003` with `preflight_passed: true` and `missing_required_specs: []`.
6. The clause preflight passes with no blocking gaps (exit 0).
7. The path rewrite table is exhaustive (41 entries) and each new path is documented as existing at the filesystem.
8. The architectural follow-on concerns are clearly tagged as out-of-scope.
9. **F1 closure:** Ruff, Bandit, detect_import_cycles, AND pytest static-path arguments are all repaired in the same lane-level revision.
10. **F2 closure:** Verification commands use `--skip-frontend` only (no `--skip-python`).

## Acceptance Criteria for VERIFIED (post-implementation)

1. `scripts/release_candidate_gate.py` no longer contains any root-relative `src/` or `tests/` references inside `_python_gates()` (lines 282-336).
2. Each of the 41 new paths resolves to an existing file/directory at the filesystem.
3. `python scripts/release_candidate_gate.py --skip-frontend` does not fail on a static-path collection error within `_python_gates()`. (Other failures unrelated to path collection — e.g., test/lint failures on pre-existing baseline state — are out-of-scope of this thread's verification.)
4. The upstream-GT-KB pytest invocation at lines 351-369 is untouched.
5. The release-gate's argparse surface is untouched.
6. INDEX shows the full version chain: `-001 NEW` → `-002 NO-GO` → `-003 REVISED` → `-004 GO` → `-005 NEW` (post-impl report) → `-006 VERIFIED`.

## CODEX-WAY-OF-WORKING Considerations

- Loyal Opposition under Codex: please verify the 3 new non-pytest sub-lane destinations: `applications/Agent_Red/src/` (Bandit + import-cycles + Ruff), `applications/Agent_Red/tests/` (Ruff), and `platform_tests/` (Ruff). Each must exist at the filesystem at review time.
- The Ruff-targets-`platform_tests/` decision is the load-bearing architectural call in this REVISED-1. If Codex assesses that Ruff should target ONLY Agent-Red (matching Bandit + import-cycles), please surface that as recommended-revision text. If Codex assesses Ruff should ADDITIONALLY target `groundtruth-kb/src/` (which I deliberately deferred to architectural follow-on), please surface that too.
- F2 closure: `--skip-python` removed from all verification commands. The lane-runnability assertion now uses `--skip-frontend` only. Please confirm this is the intended pattern.
- The architectural follow-on observations (gate relocation, mixed-concern split, GT-KB-source linting expansion) remain out-of-scope of THIS thread. Surface any disagreement as recommended-revision text rather than hidden NO-GO.

---

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
