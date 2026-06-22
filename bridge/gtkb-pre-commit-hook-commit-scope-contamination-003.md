NEW

# GT-KB Bridge Implementation Report - gtkb-pre-commit-hook-commit-scope-contamination - 003

bridge_kind: implementation_report
Document: gtkb-pre-commit-hook-commit-scope-contamination
Version: 003 (NEW; post-implementation report)
Responds to GO: bridge/gtkb-pre-commit-hook-commit-scope-contamination-002.md
Approved proposal: bridge/gtkb-pre-commit-hook-commit-scope-contamination-001.md
Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-3497
Recommended commit type: fix:
Implementation commit: 056334caf

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019eefa3-75b3-7951-a6b7-939a7c794b30
author_model: GPT-5 Codex
author_model_version: gpt-5-codex
author_model_configuration: Codex automation Auto-builder; approval_policy=never; workspace=E:/GT-KB

## Implementation Claim

Implemented WI-3497 within the approved GO target paths only. The assertion ratchet still updates `scripts/guardrails/assertion-baseline.json` on disk when staged tests increase assertion counts, and it still blocks assertion decreases, but it no longer runs `git add` from inside the pre-commit check. The commit-facing message now tells the committer to stage the baseline deliberately if it belongs in the commit.

Added `platform_tests/scripts/test_check_assertion_ratchet.py`, which exercises the ratchet against isolated temporary git repositories so the live GT-KB index is never touched. The tests prove an increased assertion count does not add the baseline to the staged set, unrelated staged files remain staged and unchanged, assertion decreases still return exit 1, and the regenerated baseline remains unstaged.

The implementation was committed locally as `056334caf` (`fix: stop assertion ratchet auto-staging`). The repository had substantial unrelated dirty worktree and pre-existing staged bridge/report files during this run; those were explicitly excluded from the staged set before the implementation commit. Only the two approved target paths were included in the implementation commit.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge `VERIFIED` is a commit-finalization outcome whose committed scope must equal the declared verified path set; removing the ratchet's implicit `git add` preserves scoped commit composition.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - commits remain deliberate durable artifacts rather than being silently expanded by a pre-commit side effect.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this report carries forward the governing specification links from the approved proposal.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - verification uses tests derived from the approved proposal's spec-to-test mapping plus ruff quality gates.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - this report carries the project authorization, project, and work item linkage.
- `SPEC-AUQ-POLICY-ENGINE-001` - no owner-decision or AUQ behavior was added or changed.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all changed files are in-root GT-KB platform files under `scripts/` and `platform_tests/`; no adopter/application path was touched.
- `GOV-STANDING-BACKLOG-001` - WI-3497 is the standing-backlog work item advanced by this report.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - the ratchet is a git pre-commit guardrail and remains harness-neutral.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - the baseline lifecycle remains artifact-backed and explicit; staging is no longer hidden inside the check.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - baseline regeneration remains a visible lifecycle action the committer stages deliberately.

## Owner Decisions / Input

- `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` (backed by `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION`) authorized this small, single-concern reliability fix through the bridge protocol.
- `DELIB-20265457` authorized authoring NEW proposals for open PROJECT-GTKB-RELIABILITY-FIXES work items; WI-3497 is in that authorized batch.
- No new owner decision, waiver, credential action, or production deployment approval was needed during implementation.

## Prior Deliberations

- `bridge/gtkb-pre-commit-hook-commit-scope-contamination-001.md` - approved implementation proposal and spec-derived verification plan.
- `bridge/gtkb-pre-commit-hook-commit-scope-contamination-002.md` - Loyal Opposition GO verdict authorizing implementation.
- `DELIB-2394` - prior commit-scope bundling detection review context.
- `DELIB-20264744` - prior ruff/pre-file gate context establishing checks should not silently stage unrelated artifacts.
- `DELIB-20261599` - artifact helper precedent: staging should be explicit and scoped.

## Specification-Derived Verification Plan

| Spec / governing surface | Executed verification evidence |
| --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` scoped commit composition | `test_ratchet_does_not_stage_baseline_on_increase` and `test_ratchet_leaves_unrelated_staged_set_unchanged` passed. The staged set remains exactly the pre-check set after the ratchet runs. Before commit, `git diff --cached --name-only` contained only `platform_tests/scripts/test_check_assertion_ratchet.py` and `scripts/guardrails/check_assertion_ratchet.py`. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` deliberate artifact state | `test_ratchet_increase_returns_zero_and_baseline_unstaged` passed, proving baseline regeneration remains visible as an unstaged artifact instead of being silently committed. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` linked implementation scope | This report carries forward all proposal-linked specs, and `scripts/impl_start_target_paths_preflight.py --bridge-id gtkb-pre-commit-hook-commit-scope-contamination --candidate-paths scripts/guardrails/check_assertion_ratchet.py platform_tests/scripts/test_check_assertion_ratchet.py --json` returned `verdict: in_scope`. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` executed derived tests | `python -m pytest platform_tests/scripts/test_check_assertion_ratchet.py -q --tb=short` passed with 4 tests. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` project/work linkage | The implementation-start packet resolved PAUTH `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING`, project `PROJECT-GTKB-RELIABILITY-FIXES`, and work item `WI-3497`. |
| `SPEC-AUQ-POLICY-ENGINE-001` no AUQ surface change | Changed files were limited to the guardrail script and its tests; no owner-decision tracker, AUQ policy, or pending-decision surface was touched. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` in-root path boundary | Target-path preflight returned both candidate paths in scope and no out-of-scope paths. No `applications/` path was modified. |
| `GOV-STANDING-BACKLOG-001` standing-backlog visibility | Live MemBase query showed WI-3497 open and in PROJECT-GTKB-RELIABILITY-FIXES before implementation. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` harness-neutral hook behavior | The ratchet remains a git pre-commit script, independent of Claude/Codex runtime. Temp-repo subprocess tests exercise plain git behavior. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` explicit artifact lifecycle | The new tests prove baseline changes are left unstaged for deliberate operator action. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` baseline regeneration trigger | `test_ratchet_increase_returns_zero_and_baseline_unstaged` passed, proving an assertion increase returns 0 while leaving the regenerated baseline as a visible unstaged lifecycle artifact. |

## Commands Run

- `python scripts/impl_start_target_paths_preflight.py --bridge-id gtkb-pre-commit-hook-commit-scope-contamination --candidate-paths scripts/guardrails/check_assertion_ratchet.py platform_tests/scripts/test_check_assertion_ratchet.py --json`
- `python -m pytest platform_tests/scripts/test_check_assertion_ratchet.py -q --tb=short`
- `python -m ruff check scripts/guardrails/check_assertion_ratchet.py platform_tests/scripts/test_check_assertion_ratchet.py`
- `python -m ruff format --check scripts/guardrails/check_assertion_ratchet.py platform_tests/scripts/test_check_assertion_ratchet.py`
- `git diff --cached --name-only`
- `git commit -m "fix: stop assertion ratchet auto-staging"`

## Observed Results

- Target-path preflight: `verdict: in_scope`; 2 candidate paths in scope; 0 out-of-scope; 0 unused targets.
- Pytest: 4 passed in the post-commit run.
- Ruff check: `All checks passed!`
- Ruff format check: `2 files already formatted`
- Staged set immediately before implementation commit: `platform_tests/scripts/test_check_assertion_ratchet.py` and `scripts/guardrails/check_assertion_ratchet.py` only.
- Commit hooks during `git commit`: secret scan found 0 potential secrets; inventory drift PASS; narrative-artifact evidence PASS; ruff format PASS for 2 staged Python files; protected-commit authorization PASS.
- Local implementation commit: `056334caf` (`fix: stop assertion ratchet auto-staging`).

## Files Changed

- `scripts/guardrails/check_assertion_ratchet.py`
- `platform_tests/scripts/test_check_assertion_ratchet.py`

## Recommended Commit Type

`fix:` - the change removes a scoped-commit contamination defect without adding a public user-facing capability.

## Acceptance Criteria Status

- [x] `check_assertion_ratchet.py` no longer invokes `git add` in the assertion-increase branch.
- [x] Assertion decreases still return exit 1.
- [x] Assertion increases still return exit 0 and update the baseline on disk.
- [x] The regenerated baseline is left unstaged, with an informational message telling the committer to stage it deliberately if desired.
- [x] The four derived tests pass.
- [x] Ruff check and ruff format check are clean on both changed files.

## Risk And Rollback

Residual risk is low. Developers who expected the baseline to be auto-staged must now stage it deliberately, which is the intended scoped-commit behavior. Rollback is limited to reverting commit `056334caf`, which restores the prior auto-stage behavior and removes the temp-repo regression tests.

Bridge audit files remain append-only. The current repository still contains unrelated dirty/untracked work from other sessions; those files were not staged or committed by this implementation.

## Loyal Opposition Asks

1. Verify commit `056334caf` against the approved proposal and linked specifications.
2. Confirm that the implementation report's command evidence satisfies the spec-derived verification gate.
3. Return VERIFIED if satisfied; otherwise return NO-GO with concrete findings.
