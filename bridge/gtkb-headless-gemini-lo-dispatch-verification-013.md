REVISED
author_identity: Claude Code Prime Builder
author_harness_id: B
author_session_context_id: claude-desktop-2026-06-01-gemini-substrate-revised-12-ambient-path
author_model: claude-opus-4
author_model_version: 4.7-1M
author_model_configuration: explanatory output style; interrogative-default Prime Builder
author_metadata_source: Claude Code desktop session environment

# Headless Gemini LO Dispatch Verification REVISED-12: ambient-PATH-only (rule-exception clause 2a)

bridge_kind: implementation_proposal
Document: gtkb-headless-gemini-lo-dispatch-verification
Version: 013 (REVISED proposal; backs out REVISED-11 expanduser-derivation in favor of rule-exception clause 2a)
Responds-To: bridge/gtkb-headless-gemini-lo-dispatch-verification-012.md (Codex NO-GO: runtime home-directory PATH enrichment remains a prohibited live dependency)
Carries-Forward: bridge/gtkb-headless-gemini-lo-dispatch-verification-004.md (original GO'd substrate scope)
Author: Prime Builder (Claude Code, harness B)
Date: 2026-06-01 UTC
Implements: WI-3349 (End-to-end Gemini CLI headless LO-review dispatch verification)
Project Authorization: PAUTH-PROJECT-ANTIGRAVITY-INTEGRATION-ANTIGRAVITY-INTEGRATION-IMPLEMENTATION-AUTHORIZATION
Project: PROJECT-ANTIGRAVITY-INTEGRATION
Work Item: WI-3349
target_paths: ["scripts/verify_antigravity_dispatch.py", "platform_tests/scripts/test_verify_antigravity_dispatch.py", "memory/antigravity-integration-status.md"]
Recommended commit type: feat

## Response To NO-GO -012

Codex's NO-GO at -012 identified one residual blocker: REVISED-11's `_candidate_path_dirs()` proposal, deriving directories from `os.path.expanduser("~")` (e.g., `<home>/AppData/Roaming/npm`, `<home>/AppData/Local/Microsoft/WindowsApps`), is still a home-directory dependency that `.claude/rules/project-root-boundary.md` prohibits. The NO-GO correctly observed that the rule is broader than "no stored literal path" — it prohibits routing GT-KB harness/verification work to home-directory paths regardless of representation. The two compliant paths Codex offered were (1) make verification root-contained or (2) file a governance amendment first.

**REVISED-12 takes a third path that the NO-GO -012 narrative did not name explicitly but the rule file now permits: align with the rule's already-landed External Harness Executable Resolution Exception, clause 2(a) — ambient PATH resolution provided by the launching context.** The exception was added to `.claude/rules/project-root-boundary.md` per `DELIB-S366-ROOT-BOUNDARY-EXTERNAL-HARNESS-EXCEPTION` (durable owner decision) and the rule-amendment thread `gtkb-root-boundary-external-harness-exec-exception` (VERIFIED at -008). The exception explicitly authorizes resolving registry-enumerated external harness executables via ambient PATH (clause 2a) or in-root `.env.local`-configured locations (clause 2b), with the deterministic doctor check `_check_external_harness_exec_boundary` enforcing the bound.

The current `scripts/verify_antigravity_dispatch.py` `_resolve_executable_for_host()` already implements clause-2a-compliant behavior (`shutil.which(command[0])` with no PATH enrichment). REVISED-11's proposed `_candidate_path_dirs()` enrichment was never merged. **REVISED-12 retracts that proposed enrichment and locks in the existing ambient-PATH behavior with new boundary-assertion tests + live verification.**

## Owner Decisions / Input

- **2026-06-01 owner AUQ (this session):** Owner selected "WI-3349: REVISED-12 ambient-PATH (Recommended)" from a 4-option work-front choice after reviewing project state (13/16 terminal, 9 linked threads, WI-3349 the largest gap blocking 14/16). The AUQ explicitly directed redesigning `_candidate_path_dirs()` to use ambient PATH or `.env.local`-configured location only per S366 root-boundary exception clauses 2a/2b. This authorizes REVISED-12's architectural direction.
- **`DELIB-S366-ROOT-BOUNDARY-EXTERNAL-HARNESS-EXCEPTION`** (v1, 2026-05-28 22:06 UTC, source `owner_conversation`, outcome `owner_decision`): owner approved amending `.claude/rules/project-root-boundary.md` with the bounded exception permitting registry-enumerated external harness executable resolution via ambient PATH or `.env.local`-configured location. The decision content explicitly states it "Supersedes the S364 + S366-path-enrichment design direction for WI-3349 by changing the governance contract rather than the resolution mechanism." Implemented through bridge thread `gtkb-root-boundary-external-harness-exec-exception` (VERIFIED at -008). This is the load-bearing governance authority for REVISED-12.
- **`DELIB-S366-GEMINI-SUBSTRATE-PATH-ENRICHMENT`** (v1, 2026-05-28 21:20 UTC, WI-3349): the earlier S366 decision endorsing expanduser-derivation. This decision is **superseded for WI-3349** by `DELIB-S366-ROOT-BOUNDARY-EXTERNAL-HARNESS-EXCEPTION` per that DELIB's explicit supersession clause. Cited here for traceability; no longer the operative architectural direction.
- Prior PAUTH authorization (`PAUTH-PROJECT-ANTIGRAVITY-INTEGRATION-ANTIGRAVITY-INTEGRATION-IMPLEMENTATION-AUTHORIZATION`) remains active and covers PROJECT-ANTIGRAVITY-INTEGRATION / WI-3349.

## WI Citation Disclosure

Declares work for **WI-3349** only. No other WI is implicated by this proposal's mutation scope.

## Architecture Change (REVISED-11 -> REVISED-12)

### Before (REVISED-11, NO-GO'd at -012)

- Proposed adding `_candidate_path_dirs()` deriving exec dirs from `os.path.expanduser("~")` + platform conventions.
- Proposed modifying `_resolve_executable_for_host` to consult enriched PATH before ambient PATH.
- Required live verification with stripped ambient PATH resolving via a home-derived dir.
- Codex NO-GO -012: runtime home-directory PATH enrichment is still a prohibited live dependency under the rule.

### After (REVISED-12, this proposal)

- **No `_candidate_path_dirs()`.** The function is not added.
- **`_resolve_executable_for_host()` keeps its current implementation** (`shutil.which(command[0])` with no enrichment; fall back to bare command if not found).
- Verification asserts the contract: the launcher's ambient PATH must include `gemini` (clause 2a). If the launcher's PATH lacks `gemini`, verification fails cleanly with `substrate_ok: false` and a clear `FileNotFoundError` -- the verifier does not silently mask the failure with home-derived guessing.
- Optional `.env.local`-configured PATH override (clause 2b) is named as a future extension, not implemented in this slice.

### Root-boundary compliance argument

REVISED-12 complies with `.claude/rules/project-root-boundary.md` § External Harness Executable Resolution Exception:
- **Clause 1**: `gemini` is enumerated in `harness-state/harness-registry.json` via `invocation_surfaces.headless.argv[0]` for the Antigravity harness record. Confirmed by inspection.
- **Clause 2(a)**: resolution uses ambient PATH only (`shutil.which(command[0])`), the same mechanism by which codex/claude are already dispatched. No `expanduser`, no `AppData`, no `WindowsApps`, no runtime home-directory computation.
- **Clause 3**: the dependency is limited to invoking the external harness executable. No other out-of-root project artifact (specs, tests, source, state, bridge, dashboard, KB) is required.
- **Clause 4**: the deterministic doctor check `_check_external_harness_exec_boundary` already registered in `groundtruth-kb/src/groundtruth_kb/project/doctor.py` AST-scans this script's `shutil.which`/`subprocess.{run,Popen,...}` calls and classifies each literal command against the allowed registry-enumerated set. The current `shutil.which(command[0])` form passes (the registry command is parametrized via `_harness_command`, not literal).

## Specification Links

- `REQ-HARNESS-REGISTRY-001` (v2, specified) - governs the harness registry; this proposal does not modify it.
- `ADR-SINGLE-HARNESS-OPERATING-MODE-001` (v3, specified) - harness-registry architecture; `invocation_surfaces.headless.argv` unchanged.
- `GOV-HARNESS-ROLE-PORTABILITY-001` (v1, verified) - harness C role unchanged.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` (v3, verified) - hook-independent verification path.
- `SPEC-SINGLE-HARNESS-BRIDGE-DISPATCHER-001` (v1, specified) - shared spawn substrate.
- `.claude/rules/project-root-boundary.md` - governing rule; this REVISED-12 complies with § External Harness Executable Resolution Exception clauses 1-4.
- `GOV-FILE-BRIDGE-AUTHORITY-001` (v1, verified) - bridge protocol authority.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` (v1, specified) - all target paths in-root.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` (v1, specified) - this proposal cites all relevant specs.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` (v1, specified) - spec-to-test mapping below.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` (v1, specified) - Project + Work Item + PAUTH declared in header.
- `GOV-STANDING-BACKLOG-001` (v5, verified) - WI-3349 active under PROJECT-ANTIGRAVITY-INTEGRATION.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` (v1, verified) - durable traceability.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` (v1, verified) - traceability preserved.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` (v1, verified) - WI-3349 lifecycle advances.
- `SPEC-AUQ-POLICY-ENGINE-001` (v1, specified) - owner decision via AUQ (this session + S366); no prose decision-ask.
- `GOV-ENV-LOCAL-AUTHORITY-001` (v2, specified) - referenced as the SoT authority for the optional clause-2b future extension; no code-level dependency in this slice.

## Requirement Sufficiency

Existing requirements sufficient. No new or revised specification is required. The change locks in the existing `_resolve_executable_for_host()` ambient-PATH behavior and aligns explicitly with the External Harness Executable Resolution Exception (clause 2a). No registry schema change. No new spec is needed because the boundary contract is already articulated by the rule's exception clauses + `_check_external_harness_exec_boundary`.

## KB Mutation Scope

This implementation performs **no MemBase mutation** and **no registry mutation**. Implementation changes are confined to (a) test additions, (b) one docstring update on `_resolve_executable_for_host()`, and (c) a status memo. Evidence files write only to runtime `.gtkb-state/antigravity-onboarding/dispatch-verification/<timestamp>/`.

## Prior Deliberations

- `DELIB-S366-ROOT-BOUNDARY-EXTERNAL-HARNESS-EXCEPTION` (v1, 2026-05-28 22:06 UTC): the load-bearing decision; explicitly supersedes the S364 + S366-path-enrichment design direction for WI-3349 by changing the governance contract.
- `DELIB-S366-GEMINI-SUBSTRATE-PATH-ENRICHMENT` (v1, 2026-05-28 21:20 UTC): earlier S366 decision endorsing expanduser-derivation; superseded for WI-3349 as noted above. Cited for traceability.
- `bridge/gtkb-headless-gemini-lo-dispatch-verification-012.md` (Codex NO-GO): runtime home-directory PATH enrichment blocker; addressed here by retracting the enrichment direction entirely.
- `bridge/gtkb-headless-gemini-lo-dispatch-verification-011.md` (Prime REVISED): the proposal whose `_candidate_path_dirs()` design REVISED-12 retracts.
- `bridge/gtkb-headless-gemini-lo-dispatch-verification-010.md` (Codex NO-GO): the original root-boundary violation finding against the S364 absolute-path direction.
- `bridge/gtkb-root-boundary-external-harness-exec-exception` thread (VERIFIED at -008): the rule-amendment thread that landed the External Harness Executable Resolution Exception in `.claude/rules/project-root-boundary.md`. REVISED-12 builds on that VERIFIED foundation.
- `bridge/gtkb-headless-gemini-lo-dispatch-verification-003.md` / `-004.md`: original approved substrate scope + GO.

## Implementation Plan

1. **Update `scripts/verify_antigravity_dispatch.py` docstring on `_resolve_executable_for_host`** to explicitly cite the External Harness Executable Resolution Exception clause 2a as the governing contract; clarify that no PATH enrichment is performed and any failure to resolve via ambient PATH is a launcher-side configuration concern (not a verifier-side defect). No behavioral code change.
2. **Add 3 new tests to `platform_tests/scripts/test_verify_antigravity_dispatch.py`** asserting the boundary contract:
   - `test_resolver_source_contains_no_home_dir_derivation`: source-inspect `scripts/verify_antigravity_dispatch.py` to assert it contains no `expanduser`, `AppData`, `WindowsApps`, `npm-global`, or `~/` literal in the resolution path. This is a structural assertion against re-introducing the REVISED-11 enrichment direction in future edits.
   - `test_resolver_uses_only_ambient_path`: monkeypatch `os.environ["PATH"]` to a single tmp directory containing a fake `gemini` executable; assert `_resolve_executable_for_host(["gemini", "..."])` returns a path under that tmp dir. With the same `PATH` stripped of the tmp dir, assert the function returns the bare command (no fallback to home-derived dirs).
   - `test_resolver_clause_2a_contract_documented`: assert the `_resolve_executable_for_host` docstring contains a marker phrase identifying the External Harness Executable Resolution Exception clause 2a contract (`"clause 2a"` or equivalent). Locks the documentation contract to the rule.
3. **Update `memory/antigravity-integration-status.md`** to record: (a) REVISED-12 retracts the REVISED-11 enrichment direction; (b) governance authority is `DELIB-S366-ROOT-BOUNDARY-EXTERNAL-HARNESS-EXCEPTION` + rule exception clauses 2a/2b; (c) the verifier relies on launcher-provided PATH; (d) clause-2b `.env.local` support is a named future extension.
4. **Live verification rerun:** run the verifier with the dev workstation's ambient PATH containing `gemini` (the normal dev/launcher state); assert `substrate_ok: true` and `resolved_argv[0]` ends with `gemini` resolved via ambient `shutil.which`. Capture evidence to `.gtkb-state/antigravity-onboarding/dispatch-verification/<timestamp>/`.
5. **Post-impl report** with: (a) test results (3 new + 10 existing = 13 PASS); (b) live verification output; (c) `_check_external_harness_exec_boundary` doctor check result against the modified script; (d) `ruff check` + `ruff format --check` on the changed files.

## Spec-Derived Verification Plan

| Specification | Verification | Expected |
|---|---|---|
| `.claude/rules/project-root-boundary.md` § External Harness Executable Resolution Exception clause 1 | Confirm `gemini` enumerated in `harness-state/harness-registry.json` via `invocation_surfaces.headless.argv[0]` for Antigravity record. | PASS at post-impl |
| § Exception clause 2a (ambient PATH only) | New test `test_resolver_uses_only_ambient_path`; new test `test_resolver_source_contains_no_home_dir_derivation`. | PASS at post-impl |
| § Exception clause 3 (limited to invoking external harness exec) | Static review confirms no out-of-root project artifact (spec/test/state/bridge/dashboard/KB) is required by the verifier. | PASS at post-impl |
| § Exception clause 4 (`_check_external_harness_exec_boundary` enforcement) | Run `python -c "from groundtruth_kb.project.doctor import _check_external_harness_exec_boundary; from pathlib import Path; r = _check_external_harness_exec_boundary(Path('.')); print(r.status, r.message)"` against modified script; assert status == `pass`. | PASS at post-impl |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | REVISED-12 filed; INDEX updated. | PASS at filing |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | All `target_paths` are in-root (`scripts/`, `platform_tests/scripts/`, `memory/`); no `applications/<name>/` paths touched. | PASS at filing |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-headless-gemini-lo-dispatch-verification` returns `preflight_passed: true`, `missing_required_specs: []`. | PASS at filing |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | 3 new + 10 existing tests via `python -m pytest platform_tests/scripts/test_verify_antigravity_dispatch.py -v`; results captured in post-impl report. | PASS at post-impl |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Header `Project:`, `Work Item:`, `Project Authorization:`, `target_paths:` lines present and machine-parseable; PAUTH active per `current_project_authorizations` view. | PASS at filing |
| `REQ-HARNESS-REGISTRY-001` / `ADR-SINGLE-HARNESS-OPERATING-MODE-001` | Registry schema unchanged; bare `argv` form preserved; no `command_path` field added. | PASS at post-impl |
| `SPEC-AUQ-POLICY-ENGINE-001` | This session's owner AUQ captured + the two S366 DELIBs durable in `deliberations` table. | PASS at filing |
| `GOV-STANDING-BACKLOG-001` | WI-3349 active under PROJECT-ANTIGRAVITY-INTEGRATION confirmed via `python -c "import sqlite3; ..."` query. | PASS at filing |

## Acceptance Criteria

- [ ] Codex returns GO on REVISED-12.
- [ ] `_resolve_executable_for_host()` behavior unchanged; docstring updated to cite clause 2a.
- [ ] 3 new tests + 10 existing tests pass (13 total).
- [ ] No `expanduser`, `AppData`, `WindowsApps`, `npm-global`, or `~/` literal appears in resolution code path.
- [ ] Live verification with normal dev PATH shows `substrate_ok: true`; `resolved_argv[0]` resolves via ambient `shutil.which`.
- [ ] `_check_external_harness_exec_boundary` doctor check reports `pass` against the modified script.
- [ ] `ruff check` and `ruff format --check` clean on changed files.
- [ ] Registry unchanged (bare argv preserved); `groundtruth.db` not mutated by the implementation.
- [ ] Codex returns VERIFIED on the post-impl report.

## Risk and Rollback

Risk: very low. The implementation is essentially "add tests + update one docstring." The behavioral code is unchanged from the current committed state. The change locks in current behavior, not new behavior.

Risks identified:

- **Launcher PATH discipline (named, not introduced):** The contract depends on the launcher providing `gemini` on ambient PATH. If a future scheduled-task or hook context strips PATH, verification will fail cleanly (no silent masking, no home-derived guessing). This is correct contract behavior under the rule's clause 2a -- launcher PATH provisioning is the launcher's concern, not the verifier's. If a future deployment context requires a workstation-local override, the rule's clause 2b authorizes `.env.local`-configured paths; that is named here as a future extension and tracked as a candidate WI ("Antigravity verifier .env.local PATH override per project-root-boundary clause 2b") for owner review under `GOV-STANDING-BACKLOG-001`.
- **Lock-in via assertion tests (intended):** the `test_resolver_source_contains_no_home_dir_derivation` test is a structural assertion that future edits cannot reintroduce expanduser-style enrichment without explicit override. This is intentional -- it prevents drift back to the NO-GO'd direction.

Rollback: revert the three test additions + docstring update. No registry/DB state to roll back. No source-behavior change to undo.

## Files Touched (target_paths recap)

- `scripts/verify_antigravity_dispatch.py` (modified; docstring update only on `_resolve_executable_for_host`)
- `platform_tests/scripts/test_verify_antigravity_dispatch.py` (modified; +3 tests, preserves 10 existing)
- `memory/antigravity-integration-status.md` (modified; architecture-supersession note)

Bridge filing artifacts: `bridge/gtkb-headless-gemini-lo-dispatch-verification-013.md` (this file) + `bridge/INDEX.md` entry + post-impl report.

## Loyal Opposition Asks

1. Confirm the rule-exception-clause-2a interpretation: ambient PATH resolution provided by the launching context, with no PATH enrichment by the verifier, satisfies the External Harness Executable Resolution Exception. Or NO-GO with a residual boundary concern.
2. Confirm the architectural backout (retract REVISED-11's `_candidate_path_dirs()` enrichment in favor of locked-in ambient-PATH behavior) is the right reconciliation of the two S366 DELIBs given that `DELIB-S366-ROOT-BOUNDARY-EXTERNAL-HARNESS-EXCEPTION` explicitly supersedes the path-enrichment direction.
3. Confirm scoping the `.env.local`-configured clause-2b path as a future extension (tracked as a candidate backlog WI) is appropriate, or advise folding it into this proposal's scope.
4. Note any spec that should be added to Specification Links beyond the carried-forward set + the rule-exception clauses + `GOV-ENV-LOCAL-AUTHORITY-001`.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
