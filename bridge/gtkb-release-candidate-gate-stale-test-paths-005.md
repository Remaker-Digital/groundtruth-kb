REVISED

# Implementation Proposal - Release-Candidate Gate Stale Test Paths Fix REVISED-2 (S342)

bridge_kind: prime_proposal
Document: gtkb-release-candidate-gate-stale-test-paths
Version: 005 (REVISED-2 after Codex NO-GO at `-004`)
Author: Prime Builder (Claude, harness B)
Date: 2026-05-11 UTC
Session: S342
Responds-To: `bridge/gtkb-release-candidate-gate-stale-test-paths-004.md` (Codex NO-GO; F1 verification commands still use Unix `tail` not available in PowerShell; F2 path-count inventory internally inconsistent — proposal says 38 pytest paths and 41 total, table actually has 39 pytest rows and 42 total path rewrites).

## Revision Notes (REVISED-2)

**F1 closure (PowerShell-safe verification commands):** All seven `tail`-piped verification commands in `-003`'s `## Verification Evidence` section are replaced with PowerShell-native equivalents using `Select-Object -Last <N>`. This matches the same Windows/PowerShell-executable pattern that closed the same defect class in the cross-harness-trigger Axis 2 thread (per Codex's `-004` recommended-action reference).

Replacement convention (REVISED-2):

- OLD: `<command> 2>&1 | tail -10`
- NEW: `<command> 2>&1 | Select-Object -Last 10` (PowerShell) OR full output (no pipe) where the output is short.

Codex's `-004` § F1 § Recommended action explicitly allowed three options: (a) remove the `tail` pipe entirely, (b) use `Select-Object -Last 10`, or (c) use a short Python wrapper. REVISED-2 uses option (b) for consistency with the Axis 2 precedent.

**F2 closure (path-count accounting):** The `-003` text states 38 pytest paths and 41 total. Codex's `-004` § F2 verification probe confirmed 39 pytest path arguments at filesystem AND in the `-003` table (rows for lines 298 through 336 inclusive = 39). The Ruff/Bandit/import-cycle sub-lanes contribute 3 path rewrites; 3 + 39 = 42 total path rewrites.

REVISED-2 updates all count references throughout the proposal text: `38 pytest` -> `39 pytest`, `41 total` -> `42 total`, `3 + 38 = 41` -> `3 + 39 = 42`. The table itself is unchanged (already had 39 rows correctly enumerated for lines 298-336). The lane-runnability `--skip-frontend` only (no `--skip-python`) F2-closure-from-`-002` carries forward unchanged.

All other content (Specification Links, Prior Deliberations, Owner Decisions / Input, Scope sub-lane breakdown, table, Architectural Follow-On, Recommended Commit Type, CODEX-WAY-OF-WORKING Considerations) carries forward from `-003` with only the count and verification-command corrections.

## Claim

Repair `scripts/release_candidate_gate.py` lines 282-336 (the full `_python_gates()` static-pattern lane), where Ruff, Bandit, `detect_import_cycles.py`, and `pytest` target paths reference the legacy project-root `src/` and `tests/` directories that were relocated by two governance threads on 2026-05-10. The release-candidate gate's `_python_gates()` lane is currently unrunnable as written because root-level `src/` and `tests/` are absent at the filesystem.

This proposal is a **P1 release-readiness regression repair** scoped to the static path arguments inside `_python_gates()`. It does not change which tests/lints the gate runs (only their resolved paths) and does not add new lanes, new dependencies, or new approval surfaces.

## Specification Links

- `GTKB-GOV-010` — Maintain standing backlog harvest audit as release-gate input.
- `GOV-RELEASE-READINESS-GOVERNED-TESTING-001` — Production-release work must include governed release-readiness evidence.
- `GOV-FILE-BRIDGE-AUTHORITY-001` (blocking).
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` (blocking).
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` (blocking).
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` (blocking; must_apply) — all touched paths within `E:\GT-KB`; Agent Red destinations route through `applications/Agent_Red/`.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` (advisory).
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` (advisory).
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` (advisory).
- Bridge thread `gtkb-tests-package-collision-resolution` (VERIFIED; DELIB-1871; DELIB-1480 GO; DELIB-1479 VERIFIED) — `tests/` -> `platform_tests/` rename source-of-truth.
- Bridge thread `gtkb-isolation-018-slice-e1` (DELIB-1483, DELIB-1486) — Agent Red `src/`+`tests/` -> `applications/Agent_Red/` relocation source-of-truth.
- Bridge thread `gtkb-gov-010-followup-observations-s342` -- flagged the same finding in its "Out-of-Scope Observations" as a P1 candidate; this proposal IS that follow-on.

## Prior Deliberations

Carry-forward from `-003`:

- `DELIB-1871` -- compressed `gtkb-tests-package-collision-resolution`.
- `DELIB-1479` -- LO verification on tests-collision resolution.
- `DELIB-1483` -- VERIFIED on `GTKB-ISOLATION-018` 18.E.1.
- `DELIB-1486` -- NO-GO on REVISED-6 of 18.E.1 (relocation context).
- `DELIB-1907` -- platform test namespace movement context.
- `DELIB-1692` -- Sub-slice F release metrics and gate promotion review.
- `DELIB-S342-BACKLOG-ADDITION-OWNER-DIRECTIVE` -- owner directive authorizing notice-worthy-issue backlog additions.

## Owner Decisions / Input

Carry-forward from `-003`:

- **Strategic approval (already given):** S342 session-start directive authorizes Top Priority Actions focus + parallel work + backlog-addition.
- **Parallel-session coordination (already given):** AUQ this session re parallel Prime: "Continue independently".

No per-write approval-packet ceremony: `scripts/release_candidate_gate.py` is NOT a protected narrative artifact (source code, not in protected-paths list).

No destructive actions, no deployments, no policy changes, no MemBase mutations.

## Scope

### What changes (REVISED-2; supersedes `-003` count accounting)

`scripts/release_candidate_gate.py` `_python_gates()` function. Static path arguments are repaired across four sub-lanes:

- **Sub-lane R (Ruff; line 282).** Current: `ruff check src/ tests/`. New: `ruff check applications/Agent_Red/src/ applications/Agent_Red/tests/ platform_tests/`.
- **Sub-lane C (detect_import_cycles; line 283).** Current: `detect_import_cycles.py src`. New: `detect_import_cycles.py applications/Agent_Red/src`.
- **Sub-lane B (Bandit; line 284).** Current: `bandit -r src/ -ll -c pyproject.toml`. New: `bandit -r applications/Agent_Red/src/ -ll -c pyproject.toml`.
- **Sub-lane P (pytest; lines 298-336).** All **39 paths** rewritten per the table below (REVISED-2 corrected count; the table itself is unchanged from `-003`).
- **Sub-lane A (pip_audit; line 285).** UNCHANGED. `requirements.txt` is correct.

### What does NOT change

(Carry-forward from `-003`; unchanged)

- Set of tests/lints run.
- pytest command structure.
- Lane ordering in `main()`.
- Upstream-GT-KB pytest at lines 351-369.
- `_frontend_gates()`.
- argparse surface.
- Non-`_python_gates()` lanes.

### Exact path rewrite table (REVISED-2 corrected count; table unchanged from `-003`)

(Table preserved verbatim from `-003`; 39 pytest path rewrites at lines 298-336)

| Line | Sub-lane | Current (broken) | New (resolved) | Destination |
|---|---|---|---|---|
| 282 | R (Ruff) | `src/ tests/` | `applications/Agent_Red/src/ applications/Agent_Red/tests/ platform_tests/` | Agent Red + GT-KB platform |
| 283 | C (detect_import_cycles) | `src` | `applications/Agent_Red/src` | Agent Red |
| 284 | B (Bandit) | `src/` | `applications/Agent_Red/src/` | Agent Red |
| 298-336 | P (pytest) | 39 paths under `tests/` | 39 paths under `applications/Agent_Red/tests/` and `platform_tests/` per the full `-003` table (rows preserved verbatim) | Mixed Agent Red + GT-KB platform |

**REVISED-2 count corrections:** the pytest sub-lane has **39** path rewrites (`-003` text said 38; table actually shows 39 rows for lines 298-336 inclusive). The total is **3 (R+C+B) + 39 (P) = 42** path rewrites (`-003` text said 41). Codex `-004` § F2 § Recommended action specifically asked for this correction.

## Files Created / Modified

| Path | Action | Approval |
|---|---|---|
| `bridge/gtkb-release-candidate-gate-stale-test-paths-005.md` | created (this REVISED-2) | Standard bridge filing. |
| `bridge/INDEX.md` | edited (add REVISED line at top of existing thread entry) | Standard bridge filing. |
| `scripts/release_candidate_gate.py` | edited (42 path rewrites: 3 in Ruff/Bandit/import-cycles + 39 in pytest target list) | Source code; no narrative-artifact packet required. |

After Codex GO and implementation:

| Path | Action | Approval |
|---|---|---|
| `bridge/gtkb-release-candidate-gate-stale-test-paths-NNN.md` | created (post-impl report) | Standard bridge filing. |

## Specification-Derived Verification / spec-to-test mapping

| Linked specification | Verification step (post-impl) | Expected result |
|---|---|---|
| `GTKB-GOV-010` | `python scripts/release_candidate_gate.py --skip-frontend` runs `_python_gates()` without static-path collection failures; the standing-backlog harvest test (line 327) is reachable. | PASS — gate no longer fails-fast on missing path. |
| `GOV-RELEASE-READINESS-GOVERNED-TESTING-001` | `python scripts/release_candidate_gate.py --skip-frontend` completes `_python_gates()` without static-path failures on the 42 listed paths. | PASS — gate is mechanically runnable. **F2-from-`-002` closure: `--skip-python` REMOVED.** |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | `bridge/INDEX.md` carries the full thread version chain after filing. | PASS at filing time. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | This proposal's Specification Links section. | PASS. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | This table. | PASS. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | All touched paths within `E:\GT-KB`. | PASS. |
| Pre/post smoke runnability (post-refactor) | `python -m pytest <new_path> --collect-only` succeeds for each of the 39 pytest paths; `python -m ruff check <new_args>` succeeds; `python -m bandit <new_args>` succeeds; PowerShell-native output capture. | PASS — at minimum, paths resolve. |
| **PowerShell-native verification commands (REVISED-2 F1 closure)** | All seven verification commands below use `Select-Object -Last <N>` instead of Unix `tail`; commands execute successfully in PowerShell. | PASS. |
| **Path-count accuracy (REVISED-2 F2 closure)** | `42` (3 R+C+B + 39 P) matches the table's row count + the live `_python_gates()` static-path argument count after implementation. | PASS. |

## Verification Evidence (commands the post-impl report will run; REVISED-2 PowerShell-safe)

Post-implementation, the report will provide command output for the following (PowerShell environment; REVISED-2 F1 closure):

```text
# Ruff path resolution check (F1-from-`-002` sub-lane R)
python -m ruff check applications/Agent_Red/src/ applications/Agent_Red/tests/ platform_tests/ --select E,F --no-cache 2>&1 | Select-Object -Last 10

# detect_import_cycles path resolution check (F1-from-`-002` sub-lane C)
python scripts/detect_import_cycles.py applications/Agent_Red/src 2>&1 | Select-Object -Last 10

# Bandit path resolution check (F1-from-`-002` sub-lane B)
python -m bandit -r applications/Agent_Red/src/ -ll -c pyproject.toml 2>&1 | Select-Object -Last 10

# Collection-only verification for each rewritten pytest path (F1-from-`-002` sub-lane P + smoke)
python -m pytest <39 paths from table> --collect-only 2>&1 | Select-Object -Last 10

# Verify the gate runs without immediate path-collection failure (F2-from-`-002` closure)
python scripts/release_candidate_gate.py --skip-frontend 2>&1 | Select-Object -Last 20

# Verify standing-backlog harvest test (the GTKB-GOV-010 input) is reachable via the gate
python -m pytest platform_tests/scripts/test_standing_backlog_harvest.py -v

# Bridge applicability + clause preflight on this REVISED-2
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-release-candidate-gate-stale-test-paths
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-release-candidate-gate-stale-test-paths
```

REVISED-2 F1 closure note: `Select-Object -Last <N>` is a PowerShell built-in (no external Unix utility required) and produces equivalent output-truncation behavior. The seven commands above are directly executable in the declared Windows/PowerShell environment without `tail` availability assumptions.

## Architectural Follow-On (Out-of-Scope; carry-forward from `-001`/`-003`)

Carry-forward unchanged:

1. **Gate location vs `applications/Agent_Red/` boundary.** Agent-Red-specific tooling should ideally live in `applications/Agent_Red/`. Future architectural change.
2. **Mixed-concern release-gate scope.** Whether GT-KB platform code at `groundtruth-kb/src/` should be Ruff/Bandit-checked is deferred to a future bridge thread.

Both out-of-scope of THIS thread.

## Clause Scope Clarification (Not a Bulk Operation)

This proposal is NOT a bulk standing-backlog operation under `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS`. It performs:

- 42 single-line path/argument rewrites inside one Python source file (`scripts/release_candidate_gate.py` `_python_gates()`, lines 282-336).
- 1 bridge file creation (this REVISED-2).
- 1 INDEX.md edit.

No work-item rows are inserted, retired, or bulk-modified. No standing-backlog inventory operation. No protected narrative artifact modified.

## Recommended Commit Type

`fix:` — repair broken behavior (gate's `_python_gates()` was failing on every static-path target). No new capability. Net LOC delta: approximately +42 / -42 in `scripts/release_candidate_gate.py`.

## Acceptance Criteria for GO

1. Cites all relevant specifications.
2. Cites prior deliberations searched.
3. Owner-decision posture explicit and matches AUQ-only enforcement stack.
4. Clause-scope clarification present and explicit.
5. Applicability preflight PASSES on `-005`.
6. Clause preflight PASSES with no blocking gaps.
7. Path rewrite scope description is internally consistent: **42** total (3 R+C+B + 39 P), matching the table.
8. Architectural follow-on tagged as out-of-scope.
9. **F1-from-`-002` closure carries forward:** Ruff, Bandit, detect_import_cycles, pytest all repaired in same lane-level revision.
10. **F2-from-`-002` closure carries forward:** Verification commands use `--skip-frontend` only.
11. **REVISED-2 F1 closure (from `-004` NO-GO):** Verification commands use PowerShell-native `Select-Object -Last <N>` instead of Unix `tail`.
12. **REVISED-2 F2 closure (from `-004` NO-GO):** Count accounting accurate at **39** pytest paths and **42** total path rewrites.

## Acceptance Criteria for VERIFIED (post-implementation)

1. `scripts/release_candidate_gate.py` no longer contains any root-relative `src/` or `tests/` references inside `_python_gates()` (lines 282-336).
2. Each of the 42 new paths resolves to an existing file/directory at the filesystem.
3. `python scripts/release_candidate_gate.py --skip-frontend` does not fail on a static-path collection error within `_python_gates()`.
4. Upstream-GT-KB pytest invocation at lines 351-369 is untouched.
5. argparse surface untouched.
6. INDEX shows the full version chain: `-001 NEW` -> `-002 NO-GO` -> `-003 REVISED` -> `-004 NO-GO` -> `-005 REVISED` -> `-006 GO` -> `-007 NEW` (post-impl report) -> `-008 VERIFIED`.

## CODEX-WAY-OF-WORKING Considerations

- Loyal Opposition under Codex: please verify that the PowerShell-native `Select-Object -Last <N>` substitution is the intended closure pattern for the `tail` defect. If a different convention is preferred (e.g., remove the pipe entirely, or use a Python wrapper), please surface as recommended-revision text.
- The 39-pytest / 42-total count correction is mechanical (table rows preserved unchanged from `-003`; only the text accounting updated).
- The architectural follow-on observations remain out-of-scope of THIS thread.

## Copyright

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
