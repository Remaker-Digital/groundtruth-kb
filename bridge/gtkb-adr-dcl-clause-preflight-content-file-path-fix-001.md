NEW

# Implementation Proposal — adr_dcl_clause_preflight.py: Normalize Relative --content-file Argument (WI-3325)

bridge_kind: prime_proposal
Document: gtkb-adr-dcl-clause-preflight-content-file-path-fix
Version: 001
Author: Prime Builder (Claude, harness B)
Date: 2026-05-16 UTC
Session: S357

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-3325

target_paths: ["scripts/adr_dcl_clause_preflight.py", "platform_tests/scripts/test_adr_dcl_clause_preflight.py"]

This NEW proposal fixes a hard crash in `scripts/adr_dcl_clause_preflight.py` when its
documented `--content-file` option is given a path relative to the project root. The fix
is routed through the reliability fast-lane (`GOV-RELIABILITY-FAST-LANE-001`) under the
standing `PROJECT-GTKB-RELIABILITY-FIXES` authorization.

## Claim

When `--content-file` receives a project-root-relative path (for example
`bridge/<name>-NNN.md`, the natural form when running the preflight from the project
root), `adr_dcl_clause_preflight.py` raises
`ValueError: '<rel path>' is not in the subpath of 'E:\GT-KB'` instead of producing a
clause report. Normalizing the `--content-file` argument to an absolute path immediately
after argument parsing — before any `Path.relative_to(PROJECT_ROOT)` call — removes the
crash. Absolute `--content-file` arguments (the current workaround) are returned
unchanged, so existing callers and existing tests are unaffected.

## Defect Evidence

- `scripts/adr_dcl_clause_preflight.py:265-269` (`render_markdown`): builds `operative_str`
  with `str(operative_file.relative_to(PROJECT_ROOT))` guarded by
  `_is_under(operative_file, PROJECT_ROOT)`.
- `_is_under` (`scripts/adr_dcl_clause_preflight.py:337-342`) calls `path.resolve()` before
  `relative_to`, so a relative `operative_file` resolves (CWD-relative) under
  `PROJECT_ROOT` and the guard returns `True`.
- Line 266 then calls `relative_to(PROJECT_ROOT)` on the un-resolved relative path.
  `Path.relative_to` is purely lexical; a relative path is never "under" an absolute one,
  so it raises `ValueError`. The guard and the guarded call disagree about path form.
- `--content-file` reaches `render_markdown` un-normalized: `main()` sets
  `operative_file = args.content_file` directly (`scripts/adr_dcl_clause_preflight.py:378-382`),
  and `args.content_file` is an `argparse type=Path` value
  (`scripts/adr_dcl_clause_preflight.py:355-359`), which preserves a relative argument as-is.
- The sibling tool `scripts/bridge_applicability_preflight.py` does not crash because its
  `_display_path` helper (`scripts/bridge_applicability_preflight.py:314-319`) calls
  `path.resolve()` before `relative_to` and wraps it in `try/except ValueError`. The two
  preflight tools diverged in path-handling discipline.

Reproduction (from `E:\GT-KB`):
`groundtruth-kb/.venv/Scripts/python.exe scripts/adr_dcl_clause_preflight.py --bridge-id <id> --content-file bridge/<file>-NNN.md`.
Passing an absolute path is the current workaround.

## In-Root Placement Evidence

Both target paths are in-root under `E:\GT-KB`: `scripts/adr_dcl_clause_preflight.py` and
`platform_tests/scripts/test_adr_dcl_clause_preflight.py`. This bridge file is at
`E:\GT-KB\bridge\gtkb-adr-dcl-clause-preflight-content-file-path-fix-001.md`. No
application file and no out-of-root path is touched. `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
in-root boundary satisfied.

## Specification Links

- `GOV-RELIABILITY-FAST-LANE-001` — governs the reliability fast-lane this fix is routed through; defect-origin, no new behavior, small single-concern change.
- `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION` — owner-decision record establishing the fast-lane (PROJECT-GTKB-RELIABILITY-FIXES plus standing authorization plus the GOV spec).
- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge protocol; this proposal follows the NEW/GO/implement/report/VERIFIED workflow with `bridge/INDEX.md` as canonical state.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — this proposal cites every governing specification concretely in this section.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — the Specification-Derived Verification Plan maps the fixed behavior to executable tests.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — all target paths and this bridge file are in-root under `E:\GT-KB`.
- `GOV-STANDING-BACKLOG-001` — WI-3325 is the tracked backlog work item; see Clause Scope Clarification.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — the fix is delivered as a durable script change plus regression tests, not an undocumented patch.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — touching `adr_dcl_clause_preflight.py` triggers matching test artifacts; this proposal adds them.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — the work is governed through the bridge artifact chain and the linked work item.

## Prior Deliberations

- `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION` (outcome `owner_decision`, S351) — established the reliability fast-lane under which this fix is routed; for an eligible defect fix no per-fix deliberation or formal-artifact-approval packet is required.
- A Deliberation Archive search (`deliberations search "adr_dcl_clause_preflight relative content-file path crash preflight CLI reliability fix"`) returned no prior decision on this defect. WI-3325 is a newly-reported defect; no prior approach was proposed or rejected.

## Owner Decisions / Input

- 2026-05-16, owner input: the owner reported the `adr_dcl_clause_preflight.py` relative-`--content-file` crash (WI-3325), prescribed the fix — normalize the `--content-file` argument to an absolute path before any `relative_to(PROJECT_ROOT)` call, and add a test covering a relative `--content-file` argument — and directed it be routed through the standing `PROJECT-GTKB-RELIABILITY-FIXES` reliability fast-lane and the bridge protocol.
- Standing pre-approval: `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` (owner decision `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION`) covers WI-3325 by active project membership. Per `GOV-RELIABILITY-FAST-LANE-001`, no per-fix deliberation, per-fix project authorization, or formal-artifact-approval packet is required; the bridge proposal, Loyal Opposition review, and all safety gates remain in force.
- No blocking owner decision is pending. This proposal needs only a Loyal Opposition GO.

## Requirement Sufficiency

Existing requirements sufficient. WI-3325 ("Fix adr_dcl_clause_preflight.py crash on
relative --content-file path") is the operative requirement: the documented
`--content-file` option must accept a project-root-relative path without crashing. No new
or revised specification is required.

## Reliability Fast-Lane Eligibility

Per `GOV-RELIABILITY-FAST-LANE-001`:

- Origin is `defect` — a hard crash on a documented CLI option.
- No new public API/CLI/behavior beyond removing the defect — `--content-file` already
  exists; relative-path support is the documented-intended behavior the crash denies.
- No new or revised requirement or specification.
- Small and single-concern: 2 files (1 script, 1 test file), roughly 15 net source lines
  plus roughly 45 test lines — well under the fast-lane ceiling of about 3 files / 150
  net lines.

## Clause Scope Clarification (Not a Bulk Operation)

Not a bulk operation. One work item (WI-3325) is targeted; it is an existing member of
`PROJECT-GTKB-RELIABILITY-FIXES` under the standing reliability fast-lane authorization.
No backlog bulk mutation, no multi-item promotion or retirement, no multi-item inventory
sweep. The reliability fast-lane (`GOV-RELIABILITY-FAST-LANE-001`) waives the per-fix
formal-artifact-approval packet for an eligible defect fix; this proposal creates no
GOV/ADR/DCL/SPEC artifact and no Deliberation Archive record.

## Bridge INDEX Update Evidence

NEW filed at `E:\GT-KB\bridge\gtkb-adr-dcl-clause-preflight-content-file-path-fix-001.md`;
a new top entry is prepended to canonical `E:\GT-KB\bridge\INDEX.md`. `bridge/INDEX.md`
remains the canonical bridge workflow state.

## Proposed Scope

### IP-1: Normalize the --content-file argument in scripts/adr_dcl_clause_preflight.py

Add a module-level helper alongside the existing `_is_under` path helper:

```
def _resolve_content_file(raw: Path) -> Path:
    """Normalize a --content-file argument to an absolute path.

    argparse keeps a relative argument relative; render_markdown's
    Path.relative_to(PROJECT_ROOT) is purely lexical and raises ValueError on
    a relative path. The documented invocation runs from the project root
    with a project-root-relative bridge/... path, so resolve a relative
    argument against PROJECT_ROOT first and fall back to the current working
    directory when no project-root candidate exists.
    """
    if raw.is_absolute():
        return raw
    root_candidate = PROJECT_ROOT / raw
    if root_candidate.exists():
        return root_candidate.resolve()
    return (Path.cwd() / raw).resolve()
```

In `main()`, immediately after `args = parser.parse_args(argv)`:

```
    if args.content_file is not None:
        args.content_file = _resolve_content_file(args.content_file)
```

Effect: `operative_file` is always absolute when sourced from `--content-file`, so
`render_markdown`'s `_is_under` guard and its `relative_to(PROJECT_ROOT)` call agree on
path form. Absolute arguments are returned unchanged — the existing absolute-path
behavior and the existing `--content-file` tests are unaffected. No change to
`render_markdown`, `find_operative_file`, exit-code semantics, or report content.

### IP-2: Regression and unit tests in platform_tests/scripts/test_adr_dcl_clause_preflight.py

Add two tests to the existing test file:

1. `test_content_file_relative_path_does_not_crash` — integration regression. Monkeypatches
   `preflight.PROJECT_ROOT` to `tmp_path`, changes the working directory into `tmp_path`,
   writes a candidate bridge-content file there, and invokes `main()` with a
   project-root-relative `--content-file` argument. Asserts the call returns an integer
   exit code (no `ValueError`) and writes a clause report naming the operative file. This
   test fails on the pre-fix code with `ValueError` and passes after IP-1.
2. `test_resolve_content_file_normalizes_relative_argument` — unit test of
   `_resolve_content_file`. Asserts: a relative argument that exists under `PROJECT_ROOT`
   resolves to the absolute project-root path; a relative argument with no project-root
   candidate resolves to an absolute current-working-directory path; an absolute argument
   is returned unchanged.

## Specification-Derived Verification Plan

Spec-to-test mapping (per `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`):

| Requirement (WI-3325 / specs) | Behavior verified | Test |
|---|---|---|
| Relative `--content-file` must not crash (WI-3325) | `main()` with a project-root-relative `--content-file` returns an exit code and writes a report; no `ValueError` | `test_content_file_relative_path_does_not_crash` |
| Argument normalized to absolute before `relative_to` | `_resolve_content_file` returns an absolute path for a project-root-relative input | `test_resolve_content_file_normalizes_relative_argument` |
| CWD fallback when no project-root candidate exists | `_resolve_content_file` returns an absolute path for a non-root-relative input | `test_resolve_content_file_normalizes_relative_argument` |
| Absolute argument unchanged (no regression) | `_resolve_content_file` returns an absolute input unchanged | `test_resolve_content_file_normalizes_relative_argument` |
| Existing absolute-`--content-file` behavior preserved | `--content-file` mode still matches indexed mode and still fails closed | existing `test_content_file_mode_matches_indexed_mode_for_equivalent_content` and `test_content_file_mode_reports_blocking_gap_before_index_entry` (regression) |

Verification commands:

- `python -m pytest platform_tests/scripts/test_adr_dcl_clause_preflight.py -q --tb=short`
- `python -m ruff check scripts/adr_dcl_clause_preflight.py platform_tests/scripts/test_adr_dcl_clause_preflight.py`

## Acceptance Criteria

- IP-1 landed; a relative `--content-file` argument produces a clause report instead of
  `ValueError`.
- IP-2 landed; both new tests PASS and the full `test_adr_dcl_clause_preflight.py` suite
  (15 tests after this change) PASSES.
- `ruff check` is clean on both target files.
- Mandatory applicability and clause preflights PASS for this bridge id.

## Risks / Rollback

- Risk: a relative path resolvable under both `PROJECT_ROOT` and the current working
  directory resolves to the `PROJECT_ROOT` copy. This matches the documented invocation
  (run from the project root); the CWD branch is a fallback only. Low risk.
- Risk: behavior change for relative paths — previously they crashed, now they resolve.
  That is the defect being removed, not a regression. Absolute-path callers are returned
  unchanged.
- Rollback: revert the single `_resolve_content_file` helper and the one-line call in
  `main()`, and revert the two added tests. One source file and one test file; fully
  reversible.

## Observations (Not in Scope)

Surfaced for the reviewer's record; not part of the WI-3325 fix scope:

- The underlying root cause is the resolve-mismatch in `render_markdown`
  (`scripts/adr_dcl_clause_preflight.py:265-269`): the `_is_under` guard resolves the path
  but the `relative_to(PROJECT_ROOT)` call at line 266 does not. Normalizing
  `--content-file` (this fix) makes `operative_file` absolute for the `--content-file`
  source path, which removes the mismatch for the reported reproduction.
- A relative `--bridge-dir` argument is a separate, currently-undocumented path that could
  still feed a relative `operative_file` into `render_markdown` via `find_operative_file`'s
  `glob`. `--bridge-dir` defaults to an absolute path and no documented workflow passes it
  relative. The owner scoped this WI-3325 fast-lane fix to `--content-file`; closing the
  `--bridge-dir` path — or hardening line 266 to
  `operative_file.resolve().relative_to(PROJECT_ROOT)` — would be a separate change. It is
  flagged here so the reviewer can request folding it in if preferred.

## Recommended Commit Type

`fix:` — a defect repair. `--content-file` already exists and relative-path support is the
documented-intended behavior; the change removes a crash and adds no new capability
surface.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
