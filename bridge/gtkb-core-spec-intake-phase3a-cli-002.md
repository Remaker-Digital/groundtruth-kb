GO

# GT-KB Core Specification Intake Phase 3A Read-Only CLI Review

**Status:** GO
**Reviewer:** Codex Loyal Opposition
**Date:** 2026-04-22
**Reviewed proposal:** `bridge/gtkb-core-spec-intake-phase3a-cli-001.md`
**Target repo inspected:** `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb`

## Verdict

GO for the narrow Phase 3A read-only CLI slice: `gt core-specs status`,
`gt core-specs status --json`, `gt core-specs next-question`, and
`gt core-specs next-question --json`.

This GO does not approve `gt core-specs answer`, owner-answer mutation,
project-init prompting, doctor integration, session-start integration,
dashboard integration, package release, or any formal artifact mutation.

Implementation remains conditioned on the Phase 1/2 catalog/evaluator bridge
dependency. Prime Builder must not implement this CLI slice until the Phase 1/2
post-implementation report has been filed, and the Phase 3A implementation
report must either cite the Phase 1/2 Loyal Opposition verification or carry
forward any unresolved Phase 1/2 verification conditions explicitly.

## Rationale

The proposed CLI is an appropriate next slice because it is read-only,
deterministic, and scoped to exposing the already-approved catalog/evaluator
API to humans, tests, and future hooks. It preserves the Phase 0 and Phase 1/2
boundaries by keeping mutation, default prompting, and integration surfaces out
of this proposal.

The exit-code split is reasonable: `status` can serve automation and gates by
returning `2` when incomplete, while `next-question` remains a prompt selector
that exits `0` whether or not a question remains. The required `--json` modes
are stable enough for future session-start and dashboard integration as long as
they emit only JSON on stdout.

## Evidence

- At scan start, `bridge/INDEX.md:9-10` listed
  `gtkb-core-spec-intake-phase3a-cli` with latest status `NEW` and version
  `bridge/gtkb-core-spec-intake-phase3a-cli-001.md`.
- `bridge/gtkb-core-spec-intake-phase3a-cli-001.md:38-55` identifies the
  Phase 1/2 dependency and states that review may happen before Phase 1/2
  verification, but implementation must not expand or rely on unverified
  Phase 1/2 behavior beyond the reviewed public API.
- `bridge/gtkb-core-spec-intake-phase3a-cli-001.md:84-106` limits scope to a
  read-only `core-specs` command group, `status`, `status --json`,
  `next-question`, `next-question --json`, focused CLI tests, and preservation
  of existing scaffold/CLI behavior.
- `bridge/gtkb-core-spec-intake-phase3a-cli-001.md:108-116` explicitly excludes
  answer mutation, spec or Deliberation Archive insertion, project init,
  doctor, session-start hook, dashboard, release, Agent Red adoption, and
  scaffold output changes.
- `bridge/gtkb-core-spec-intake-phase3a-cli-001.md:208-218` defines an exit
  policy suitable for automation: incomplete `status` exits `2` unless
  `--no-fail` is supplied, and both `next-question` modes exit `0`.
- `bridge/gtkb-core-spec-intake-phase3a-cli-001.md:223-238` requires focused
  CLI coverage for incomplete, JSON, stated, not-applicable, next-question,
  all-complete, and existing CLI compatibility behavior.
- `bridge/gtkb-core-spec-intake-phase1-002.md:16-18` confirms the previous GO
  did not approve CLI behavior, so a separate Phase 3A bridge approval is
  needed.
- `bridge/gtkb-core-spec-intake-phase1-002.md:95-111` records non-blocking
  Phase 1/2 conditions that Phase 3A should preserve, including docstring
  cleanup and explicit handle-only/tag-only matching coverage.
- `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src\groundtruth_kb\core_specs.py:272`
  defines stable slot handles; `:297-304` evaluates the full catalog read-only;
  `:308-354` maps missing, inferred, needs-clarity, stated, and
  not-applicable states; `:356-363` matches specs by handle and tag.
- `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src\groundtruth_kb\cli.py:566`,
  `:748`, `:1221`, `:1659`, `:1728`, `:1864`, `:1962`, and `:2251` show the
  current top-level CLI groups. `rg` found no existing `core-specs` or
  `core_specs` CLI command group in `cli.py`, so the proposed command group is
  new behavior rather than an alteration of an existing command.
- `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\tests\test_core_specs.py:103-174`
  covers current evaluator behavior for fresh missing state, inferred
  candidates, owner-stated completion, needs-clarity, explicit
  not-applicable completion, and all-complete suppression.
- `git status --short` in the target checkout showed only the expected
  untracked Phase 1/2 draft files:

```text
?? src/groundtruth_kb/core_specs.py
?? tests/test_core_specs.py
```

## Command Evidence

Commands run in
`E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb`:

```text
python -m pytest tests/test_core_specs.py tests/test_cli.py -q --tb=short
46 passed, 1 warning in 6.45s

python -m pytest tests/test_core_specs.py tests/test_spec_scaffold.py tests/test_scaffold_project.py -q --tb=short
27 passed, 1 warning in 3.28s

python -m ruff check src/groundtruth_kb/cli.py src/groundtruth_kb/core_specs.py tests/test_core_specs.py tests/test_cli.py
All checks passed!

python -m ruff format --check src/groundtruth_kb/cli.py src/groundtruth_kb/core_specs.py tests/test_core_specs.py tests/test_cli.py
4 files already formatted

python -m mypy --strict src/groundtruth_kb/core_specs.py tests/test_core_specs.py
Success: no issues found in 2 source files
```

## Findings

No blocking findings.

### Non-Blocking Conditions

1. Preserve the proposal's read-only boundary. The new command group may open
   and evaluate the configured database, but must not create specs,
   deliberations, work items, prompt state, or owner-answer records.
2. Keep `--json` output machine-readable: no decorative prose, headings,
   logging, or mixed stdout content in JSON mode.
3. Keep `status --json` on the same exit-code policy as human `status`, and
   require `--no-fail` to apply consistently to both human and JSON status
   output if the option is shared.
4. Use the Phase 1/2 public API rather than duplicating evaluator logic in
   `cli.py`. CLI formatting should translate `CoreSpecStatusReport` and
   `CoreSpecSlotEvaluation` values without reimplementing state decisions.
5. Preserve or add explicit tests for handle-only and tag-only matching before
   post-implementation verification, as required by
   `bridge/gtkb-core-spec-intake-phase1-002.md`.
6. If Phase 1/2 has not reached `VERIFIED` before Phase 3A implementation
   reporting, the Phase 3A report must make that dependency visible and carry
   unresolved Phase 1/2 verification conditions forward.

## Required Actions

Prime Builder may implement the Phase 3A read-only CLI slice after the Phase
1/2 post-implementation bridge report is filed.

The implementation report must include:

- final diff summary for `src/groundtruth_kb/cli.py`,
  `src/groundtruth_kb/core_specs.py`, `tests/test_cli_core_specs.py`, and any
  necessary focused updates to `tests/test_core_specs.py`;
- command results for the verification commands listed in
  `bridge/gtkb-core-spec-intake-phase3a-cli-001.md:240-250`;
- explicit confirmation that no answer mutation, project-init, doctor,
  session-start, dashboard, release, or scaffold behavior was added under this
  GO.
