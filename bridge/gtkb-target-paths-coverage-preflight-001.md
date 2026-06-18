NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 8cd56f34-2ccb-41c3-86e3-e099620f487d
author_model: claude-opus-4-8
author_model_version: 4.8
author_model_configuration: 1m

# Proposal/review-time preflight: detect verification & generator output paths missing from target_paths

Project Authorization: PAUTH-PROJECT-GTKB-MAY29-HYGIENE-ALL-UNIMPLEMENTED-AUTHORIZATION
Project: PROJECT-GTKB-MAY29-HYGIENE
Work Item: WI-4599

target_paths: ["scripts/proposal_target_paths_coverage_preflight.py", "platform_tests/scripts/test_proposal_target_paths_coverage_preflight.py"]

## Summary

WI-4599 (P2, improvement, component `bridge-automation`). The implementation-
start gate already treats `target_paths` as a strict explicit allowlist, and
`scripts/impl_start_target_paths_preflight.py` (WI-3380, VERIFIED at
`bridge/gtkb-impl-start-target-paths-preflight-009.md`) checks *candidate* edited
paths against that allowlist. What is missing is a *forward-looking*,
proposal/review-time check: nothing flags when a proposal's own verification
commands and generator commands imply output paths that the proposal forgot to
declare in `target_paths`. That under-scoping is only discovered later, at
implementation-start, as avoidable NO-GO / begin-gate churn (the concrete case
the WI cites: a no-index skill-template proposal under-scoped its companion
verification/support files).

This proposal adds a deterministic, read-only, advisory preflight that runs
*before GO* and reports implied output paths missing from `target_paths`. It
keeps the implementation-start gate strict and unchanged; it only catches the
omission earlier.

## Problem

`target_paths` is an allowlist that the begin gate enforces strictly. But a
proposal author can write a verification plan that runs, e.g.,
`pytest platform_tests/scripts/test_new.py` or a generator command
`python scripts/generate_codex_skill_adapters.py --check --update-registry`,
while listing only the primary source file in `target_paths`. The implied
companion paths (the new test file; the generated `.codex/skills/**`,
`.codex/skills/MANIFEST.json`, `config/agent-control/harness-capability-registry.toml`)
are then outside the allowlist, so the begin gate blocks the very writes the
proposal intended. There is no review-time signal that the allowlist is
*incomplete* relative to the proposal's own commands.

## Proposed fix (new sibling preflight; reuses verified root-boundary-safe helpers)

Add `scripts/proposal_target_paths_coverage_preflight.py` — a read-only,
deterministic, advisory preflight. It does NOT modify the strict begin gate or
the existing `impl_start_target_paths_preflight.py`.

Behavior:

1. Resolve the operative proposal content: `--bridge-id <slug>` resolves the
   latest NEW/REVISED proposal file via the same `bridge_entry` resolver used by
   the sibling preflights, or `--content-file <path>` for pre-filing self-check.
2. `extract_target_paths(content)` (reused from `implementation_authorization`).
3. Derive *implied* output paths from the proposal text:
   - **Verification test paths**: scan for `pytest`/`-m pytest` invocations and
     collect referenced `*.py` test paths (edit subjects that should be listed).
   - **Generator outputs**: a deterministic, documented, extensible constant
     `GENERATOR_OUTPUT_MAP` mapping a known generator script stem to its declared
     output globs. Seeded per the WI with
     `scripts/generate_codex_skill_adapters.py` →
     `[".codex/skills/**", ".codex/skills/MANIFEST.json", "config/agent-control/harness-capability-registry.toml"]`.
     When a mapped generator command appears in the proposal, its output globs
     become implied edit targets.
4. **Root-boundary-safe normalization (the WI-3380 / -007 NO-GO lesson).** Each
   implied path is normalized via `normalize_relative_path()` (reused). A path
   that escapes the project root raises `AuthorizationError("Path escapes project
   root")`; this preflight CATCHES that and reports it as an explicit
   `out_of_root` finding. It MUST NOT coerce an escaped path back in-root and
   treat it as covered — that was the exact blocking defect that NO-GO'd
   `gtkb-impl-start-target-paths-preflight-007`.
5. **Coverage check**: an implied in-root path is "covered" iff
   `path_authorized(implied, target_paths)` is True (reused glob semantics,
   including the `/**` recursive shortcut — byte-for-byte parity with the begin
   gate). Report `uncovered_verification_paths`, `uncovered_generator_paths`, and
   `out_of_root` separately.
6. **Advisory output**: emit a `## Target-Paths Coverage` markdown section and a
   `--json` form. Default exit `0` (advisory "warn" per the WI). A `--strict`
   opt-in exits non-zero when any uncovered path is found, for future gating;
   the default invocation never gates. Loyal Opposition cites the section in
   review.

## Specification Links

- `GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001` — two-layer
  defense in depth (write-time + review-time); this adds a review-time layer
  complementing the strict begin-gate write-time enforcement.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — proposals must cite
  all relevant governing specifications.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge-mediated implementation/verification
  must honor the file-bridge authority model.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — spec-derived verification.
- `.claude/rules/file-bridge-protocol.md` § Mandatory Implementation-Start
  Authorization Metadata — defines the `target_paths` allowlist this preflight
  checks for completeness.
- `.claude/rules/codex-review-gate.md` — the preflight is cited at review time.
- `.claude/rules/project-root-boundary.md` — root-boundary-safe normalization is
  mandatory; escaped paths are flagged, never coerced in-root.
- (advisory) `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`,
  `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`,
  `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`.

## Prior Deliberations

- `DELIB-20260687` and `DELIB-20261261` (both NO-GO) — Loyal Opposition verdicts
  on `gtkb-impl-start-target-paths-preflight` (WI-3380). The -007 NO-GO root
  cause was a root-boundary defect: the preflight accepted an explicit path that
  escaped the project root and normalized it back into an approved in-root target
  path. This proposal explicitly encodes that lesson (step 4: escaped paths are
  reported as `out_of_root`, never coerced) and reuses the now-VERIFIED
  `normalize_relative_path()` / `path_authorized()` helpers rather than
  re-implementing path handling.
- `gtkb-impl-start-target-paths-preflight` reached VERIFIED at
  `bridge/gtkb-impl-start-target-paths-preflight-009.md` (WI-3380). That is the
  *backward-looking* check (candidate edits vs allowlist). WI-4599 is the
  *forward-looking* complement (proposal commands → implied paths vs allowlist),
  a new sibling script that does not modify the verified one.
- Deliberation search (`gt deliberations search "target_paths coverage preflight
  generator outputs verification missing"`) surfaced the two NO-GO records above
  as the only on-topic prior decisions; the remaining matches (DELIB-20264466,
  DELIB-20261432, DELIB-2584) concern unrelated bridge verdicts.


### Helper-suggested candidates

<!-- Pre-populated by helper; review and prune. -->
- DA: `DELIB-20261789` — seed=search; bridge_thread; Bridge thread: gtkb-impl-start-target-paths-preflight (9 versions, VERIFIED)
- DA: `DELIB-1668` — seed=search; bridge_thread; Loyal Opposition Verification - GTKB-CI-COVERAGE-FOR-PLATFORM-001 Post-NO-GO Fix
- DA: `DELIB-20263439` — seed=search; bridge_thread; Bridge INDEX startup comment compaction snapshot 2026-06-15T20:23:02Z
- DA: `DELIB-20264617` — seed=search; bridge_thread; Loyal Opposition Review - Prime Worker Permission Profile Slice 1
- DA: `DELIB-1981` — seed=search; bridge_thread; Bridge thread: gtkb-platform-spec-coverage-architecture-2026-04-29 (6 versions, 

## Requirement Sufficiency

Existing requirements are sufficient. WI-4599 itself prescribes the behavior
(compare verification and generator commands against `target_paths` before GO;
warn; keep the implementation-start gate strict), and
`GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001` establishes the
two-layer review-time + write-time enforcement model this preflight slots into.
No new or revised requirement is needed before implementation.

## Spec-Derived Verification Plan

Spec-to-test mapping — each linked clause maps to a test in
`platform_tests/scripts/test_proposal_target_paths_coverage_preflight.py`:

- `GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001` (review-time
  detection of incomplete scope): `test_flags_pytest_path_missing_from_target_paths`
  asserts a proposal whose verification runs `pytest platform_tests/scripts/test_x.py`
  with `target_paths` omitting that test reports it under
  `uncovered_verification_paths`.
- Generator-output detection (WI example):
  `test_flags_generator_outputs_missing_from_target_paths` asserts a proposal
  citing `generate_codex_skill_adapters.py --check --update-registry` with
  `target_paths` omitting the mapped outputs reports
  `.codex/skills/**`, `.codex/skills/MANIFEST.json`, and
  `config/agent-control/harness-capability-registry.toml` under
  `uncovered_generator_paths`.
- Coverage via glob (no false positive):
  `test_generator_output_covered_by_recursive_glob` asserts that
  `target_paths` containing `.codex/skills/**` covers an implied
  `.codex/skills/bridge/SKILL.md` (reuses `path_authorized` `/**` semantics) and
  is NOT reported.
- `DCL`/root-boundary lesson (the -007 NO-GO):
  `test_escaped_path_reported_out_of_root_not_coerced` asserts an implied path
  that escapes the project root (e.g., `../evil.py`) is reported under
  `out_of_root` and is NEVER normalized in-root or treated as covered.
- Advisory exit semantics:
  `test_default_exit_is_advisory_zero_even_with_uncovered` (exit 0 by default)
  and `test_strict_flag_exits_nonzero_on_uncovered` (`--strict` exits non-zero).
- Clean proposal:
  `test_fully_scoped_proposal_reports_no_gaps` asserts a proposal whose implied
  paths are all in `target_paths` reports empty lists and exit 0.

Commands (resolved against the GT-KB venv interpreter, which carries `ruff`):

    .venv/Scripts/python.exe -m pytest platform_tests/scripts/test_proposal_target_paths_coverage_preflight.py -q
    .venv/Scripts/python.exe -m ruff check scripts/proposal_target_paths_coverage_preflight.py platform_tests/scripts/test_proposal_target_paths_coverage_preflight.py
    .venv/Scripts/python.exe -m ruff format --check scripts/proposal_target_paths_coverage_preflight.py platform_tests/scripts/test_proposal_target_paths_coverage_preflight.py

Expected: all tests pass; `ruff check` and `ruff format --check` clean on both
changed files.

## Acceptance Criteria

1. A new read-only preflight reports verification-implied test paths and
   generator-implied output paths that are missing from `target_paths`, before
   GO.
2. Escaped (out-of-root) implied paths are reported as `out_of_root` and never
   coerced in-root or treated as covered (the WI-3380 / -007 NO-GO lesson).
3. Glob coverage (`/**`) matches the begin-gate semantics byte-for-byte (reuses
   `path_authorized`).
4. The check is advisory by default (exit 0); `--strict` is opt-in.
5. The existing `impl_start_target_paths_preflight.py` and the strict begin gate
   are unchanged.
6. `ruff check` and `ruff format --check` clean on both changed files.

## Risk and Rollback

- Risk: LOW. New, read-only, advisory script plus its test; default exit 0 so it
  cannot block any existing flow. It imports verified helpers
  (`extract_target_paths`, `path_authorized`, `normalize_relative_path`) rather
  than re-implementing path logic, inheriting the root-boundary fix.
- Blast radius: two new files. No change to `implementation_authorization.py`,
  `impl_start_target_paths_preflight.py`, the begin gate, or any hook
  registration.
- Rollback: delete the two new files; no state, schema, or behavior change
  remains.

## Owner Decisions / Input

None required. Implementation authority derives from the active,
owner-decision-backed project authorization
`PAUTH-PROJECT-GTKB-MAY29-HYGIENE-ALL-UNIMPLEMENTED-AUTHORIZATION` (owner
decision `DELIB-PROJECT-MAY29-HYGIENE-AUTHORIZE-ALL-20260617`). WI-4599 is an
unimplemented work item in PROJECT-GTKB-MAY29-HYGIENE, and the WI text prescribes
the behavior. No AskUserQuestion decision is needed.

## Recommended Commit Type

`feat:` — adds a new review-time preflight capability (a net-new script + test).
