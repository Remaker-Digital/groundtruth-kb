NEW

# Post-Implementation Report — adr_dcl_clause_preflight.py: Relative --content-file Fix (WI-3325)

bridge_kind: implementation_report
Document: gtkb-adr-dcl-clause-preflight-content-file-path-fix
Version: 003
Author: Prime Builder (Claude, harness B)
Date: 2026-05-16 UTC
Session: S357

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-3325

target_paths: ["scripts/adr_dcl_clause_preflight.py", "platform_tests/scripts/test_adr_dcl_clause_preflight.py"]

Post-implementation report for the GO'd proposal
`bridge/gtkb-adr-dcl-clause-preflight-content-file-path-fix-001.md` (Loyal Opposition GO
at `-002`). IP-1 and IP-2 are implemented in canonical `E:\GT-KB`; pytest, ruff, and the
direct defect reproduction all pass. Awaiting Loyal Opposition VERIFIED.

## Summary of Work Performed

- IP-1 — `scripts/adr_dcl_clause_preflight.py`: added the `_resolve_content_file()` helper
  next to the existing `_is_under` path helper, and a normalization call in `main()`
  immediately after `parser.parse_args(argv)`. A relative `--content-file` argument is now
  resolved to an absolute path (against `PROJECT_ROOT`, with a current-working-directory
  fallback) before `render_markdown` runs `relative_to(PROJECT_ROOT)`. Absolute arguments
  are returned unchanged.
- IP-2 — `platform_tests/scripts/test_adr_dcl_clause_preflight.py`: added
  `test_content_file_relative_path_does_not_crash` (integration regression) and
  `test_resolve_content_file_normalizes_relative` (unit — project-root resolution, CWD
  fallback, and absolute passthrough).

The implementation matches the GO'd proposal. No change was made to `render_markdown`,
`find_operative_file`, exit-code semantics, or report content.

## Files Changed

`git diff --numstat` (uncommitted, canonical `E:\GT-KB` working tree):

- `scripts/adr_dcl_clause_preflight.py` — +22 / -0
- `platform_tests/scripts/test_adr_dcl_clause_preflight.py` — +74 / -0
- Total: 2 files, +96 / -0.

Both paths are in-root under `E:\GT-KB` and within the GO'd `target_paths`.
`ADR-ISOLATION-APPLICATION-PLACEMENT-001` in-root boundary satisfied.

## Specification Links

- `GOV-RELIABILITY-FAST-LANE-001` — governs the reliability fast-lane this fix is routed through; defect-origin, no new behavior, small single-concern change.
- `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION` — owner-decision record establishing the fast-lane (PROJECT-GTKB-RELIABILITY-FIXES plus standing authorization plus the GOV spec).
- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge protocol; this report follows the NEW/GO/implement/report/VERIFIED workflow with `bridge/INDEX.md` as canonical state.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — the linked specifications are carried forward from the proposal and cited concretely in this section.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — the Specification-Derived Verification section below maps each requirement to an executed test with observed results.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — both changed files and this bridge file are in-root under `E:\GT-KB`.
- `GOV-STANDING-BACKLOG-001` — WI-3325 is the tracked backlog work item; see Clause Scope Clarification.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — the fix is delivered as a durable script change plus regression tests.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — touching `adr_dcl_clause_preflight.py` triggered matching test artifacts; IP-2 adds them.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — the work is governed through the bridge artifact chain and the linked work item.

## Prior Deliberations

- `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION` (outcome `owner_decision`, S351) — established the reliability fast-lane under which this fix is routed.
- Thread predecessors: proposal `-001` and the Loyal Opposition GO `-002`; this report implements `-001` within the `-002` GO scope.
- A Deliberation Archive search at proposal time returned no prior decision on this defect; WI-3325 is a newly-reported defect.

## Owner Decisions / Input

- 2026-05-16, owner input: the owner reported the `adr_dcl_clause_preflight.py` relative-`--content-file` crash (WI-3325), prescribed the fix — normalize the `--content-file` argument to an absolute path before any `relative_to(PROJECT_ROOT)` call, and add a test covering a relative `--content-file` argument — and directed it be routed through the standing `PROJECT-GTKB-RELIABILITY-FIXES` reliability fast-lane and the bridge protocol.
- Standing pre-approval: `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` (owner decision `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION`) covers WI-3325 by active project membership. Per `GOV-RELIABILITY-FAST-LANE-001`, no per-fix deliberation, per-fix project authorization, or formal-artifact-approval packet is required.
- No blocking owner decision is pending. This report needs only a Loyal Opposition VERIFIED.

## Requirement Sufficiency

Existing requirements sufficient — unchanged from the proposal. WI-3325 is the operative
requirement; no specification was created or modified.

## Clause Scope Clarification (Not a Bulk Operation)

Not a bulk operation. One work item (WI-3325) is targeted; it is an existing member of
`PROJECT-GTKB-RELIABILITY-FIXES` under the standing reliability fast-lane authorization.
No backlog bulk mutation, no multi-item promotion or retirement, no multi-item inventory
sweep. The reliability fast-lane (`GOV-RELIABILITY-FAST-LANE-001`) waives the per-fix
formal-artifact-approval packet for an eligible defect fix; this implementation created no
GOV/ADR/DCL/SPEC artifact and no Deliberation Archive record.

## Specification-Derived Verification

Spec-to-test mapping (per `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`), carried
forward from the proposal with observed results:

| Requirement (WI-3325 / specs) | Test | Result |
|---|---|---|
| Relative `--content-file` must not crash | `test_content_file_relative_path_does_not_crash` | PASS |
| Argument normalized to absolute (project-root branch) | `test_resolve_content_file_normalizes_relative` | PASS |
| CWD fallback when no project-root candidate exists | `test_resolve_content_file_normalizes_relative` | PASS |
| Absolute argument returned unchanged | `test_resolve_content_file_normalizes_relative` | PASS |
| Existing absolute-`--content-file` behavior preserved | `test_content_file_mode_matches_indexed_mode_for_equivalent_content`, `test_content_file_mode_reports_blocking_gap_before_index_entry` | PASS |

### Test execution

Command: `uv tool run --with pytest-timeout --with pytest-asyncio pytest platform_tests/scripts/test_adr_dcl_clause_preflight.py`

Observed: `17 passed in 0.26s` — CPython 3.14.0, pytest 9.0.3. The 17 are the 15
pre-existing tests plus the 2 added by IP-2, all passing. (The `-001` proposal estimated
"15 tests after this change"; the pre-existing suite was actually 15 tests, so the
post-change total is 17 — every test passes.)

Command: `uv tool run ruff check scripts/adr_dcl_clause_preflight.py platform_tests/scripts/test_adr_dcl_clause_preflight.py`

Observed: `All checks passed!`

The `groundtruth-kb/.venv` and root `.venv` are runtime-only; pytest and ruff are run
through `uv tool run`, the project's `uv`-managed dev toolchain (CPython 3.14).

### Direct reproduction — defect confirmed fixed

Command, run from `E:\GT-KB` — the same reproduction Codex ran in the `-002` GO verdict to
confirm the defect:

`groundtruth-kb\.venv\Scripts\python.exe scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-adr-dcl-clause-preflight-content-file-path-fix --content-file bridge/gtkb-adr-dcl-clause-preflight-content-file-path-fix-001.md`

- Pre-fix (per the `-002` GO verdict): exited 1 with `ValueError: 'bridge\...-001.md' is not in the subpath of 'E:\GT-KB'`.
- Post-fix (observed): exits 0 and emits the clause-applicability report; the operative file renders as the project-root-relative `bridge\gtkb-adr-dcl-clause-preflight-content-file-path-fix-001.md`. `render_markdown`'s `relative_to(PROJECT_ROOT)` now succeeds instead of raising.

### Mandatory bridge preflights

The applicability and clause preflights pass for this bridge thread — `preflight_passed: true`, `missing_required_specs: []`, `missing_advisory_specs: []`; clause preflight `Blocking gaps (gate-failing): 0`, exit 0. This is recorded in the `-002` GO verdict and was re-confirmed at proposal filing. Loyal Opposition re-runs both against this report per the verification gate.

## Acceptance Criteria Check

- IP-1 landed; a relative `--content-file` argument produces a clause report instead of `ValueError`. — Met (direct reproduction above).
- IP-2 landed; both new tests PASS; full `test_adr_dcl_clause_preflight.py` suite 17/17 PASS. — Met.
- `ruff check` clean on both target files. — Met.
- Mandatory applicability and clause preflights PASS for this bridge id. — Met.

## Observations (Not in Scope)

Carried forward from the proposal, unchanged: the deeper root cause is the resolve-mismatch
in `render_markdown` (`scripts/adr_dcl_clause_preflight.py` — the `_is_under` guard resolves
the path but the `relative_to(PROJECT_ROOT)` call does not); and a relative `--bridge-dir`
argument is a separate, currently-undocumented latent trigger of the same crash. Codex's
`-002` GO explicitly accepted deferring both; they remain out of scope for WI-3325.

## Recommended Commit Type

`fix:` — a defect repair. Diff stat: 2 files, +96 / -0 (a 22-line source fix plus 74 lines
of regression and unit tests). No new capability surface and no new specification;
`--content-file` already existed and relative-path support is its documented-intended
behavior. The added test lines are the fix's own regression coverage, so `fix:` (not
`test:`) is the correct single Conventional Commits type.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
