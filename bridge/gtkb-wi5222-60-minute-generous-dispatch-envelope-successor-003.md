NEW

# GT-KB Bridge Implementation Report - WI-5222 60-minute generous dispatch envelope successor

bridge_kind: implementation_report
Document: gtkb-wi5222-60-minute-generous-dispatch-envelope-successor
Version: 003 (NEW; post-implementation report)
Responds to GO: bridge/gtkb-wi5222-60-minute-generous-dispatch-envelope-successor-002.md
Approved proposal: bridge/gtkb-wi5222-60-minute-generous-dispatch-envelope-successor-001.md
author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f5f66-9582-7f03-a3f1-3c75e6bd9d0a
author_model: gpt-5
author_model_version: gpt-5
author_model_configuration: Codex desktop interactive Prime Builder; current-HEAD hunk-scoped WI-5222 implementation report
Project Authorization: PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-WI5222-60M-GENEROUS-ALLOWANCE-20260713
Project: PROJECT-GTKB-GOOSE-HARNESS-ADOPTION
Work Item: WI-5222
Test: TEST-11376
Recommended commit type: fix:

## Implementation Claim

Implemented the owner-calibrated 60-minute generous dispatch envelope as an exact hunk patch against current `HEAD` `268943aa6d16a032a457e0bc7e8bbbdc671cd119`.

The reviewed patch changes only five approved paths:

- `.api-harness/routing.toml`
- `scripts/dispatcher_runtime.py`
- `platform_tests/scripts/test_dispatcher_runtime.py`
- `platform_tests/scripts/test_gtkb_dispatcher_daemon.py`
- `platform_tests/scripts/test_lo_harness_turn_budget.py`

The patch sets D/F/H `session_timeout_seconds` to `3600`, sets the shared A/B/C/D/F/H generous worker lifetime to `4200`, preserves 900-second operation timeouts and 600 turns, and verifies the worker-to-lease/reset margin at `4500`.

The live shared worktree was not whole-file staged, reverted, cleaned, or normalized. Finalization must use the hunk patch named below through the WI-5112 disposable-index VERIFIED finalizer.

## Specification Links

- `DCL-DISPATCH-ENVELOPE-RULES-001`
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001`
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001`
- `GOV-HARNESS-ONBOARDING-CONTRACT-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-WORK-TREE-HYGIENE-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`

## Owner Decisions / Input

- `DELIB-20260713-DISPATCH-60-MINUTE-GENEROUS-ALLOWANCE` controls the numeric policy: 60-minute model window, 900-second operation timeout preserved, 600 turns preserved, 600-second session-to-worker margin preserved, 300-second worker-to-lease/reset margin preserved.
- No new owner decision is requested by this implementation report.

## Prior Deliberations

- `bridge/gtkb-wi5222-60-minute-generous-dispatch-envelope-successor-001.md` - approved successor implementation proposal.
- `bridge/gtkb-wi5222-60-minute-generous-dispatch-envelope-successor-002.md` - independent OpenRouter F GO verdict.
- `bridge/gtkb-wi5222-60-minute-generous-dispatch-envelope-004.md` - prior NO-GO whose hunk-isolation concerns this report avoids.
- `bridge/gtkb-wi5222-60-minute-generous-dispatch-envelope-005.md` - withdrawn predecessor.
- `bridge/gtkb-wi5220-dispatcher-test-fixture-parity-006.md` - earlier VERIFIED fixture baseline context.

## Hunk Patch Evidence

- Hunk patch: `bridge/hunks/gtkb-wi5222-60m-envelope-successor-current-head.patch`
- Patch Git blob: `5d13de8b3d8173504bc24f881b98aea7cba45bcb`
- Patch SHA-256: `F890E23B6F66E59FD70CFD90647AD45200C9C17CB2DAC72458A0CF577F353864`
- Patch size: `10079` bytes
- Disposable-index apply check: passed with `git apply --cached --check` after `git read-tree HEAD`.
- Patch whitespace check: passed with `git diff --cached --check` in the disposable index.

Patch numstat:

```text
3       3       .api-harness/routing.toml
12      11      platform_tests/scripts/test_dispatcher_runtime.py
6       6       platform_tests/scripts/test_gtkb_dispatcher_daemon.py
4       3       platform_tests/scripts/test_lo_harness_turn_budget.py
5       5       scripts/dispatcher_runtime.py
```

Disposable-index staged blobs after applying the patch:

```text
100644 9866ef89b1fef23eee6ce07ecd4818bd5c29322e 0 .api-harness/routing.toml
100644 c560b71d3722161b9b9ede4074ccff00322411aa 0 platform_tests/scripts/test_dispatcher_runtime.py
100644 4d7a4c1f5bc948e59e0cb01ed440b448a8974021 0 platform_tests/scripts/test_gtkb_dispatcher_daemon.py
100644 b0a3545d15cc10b4cd5d47e31ce1296c0f7821fe 0 platform_tests/scripts/test_lo_harness_turn_budget.py
100644 1e392e6f7be502937331e53b05e905867a743237 0 scripts/dispatcher_runtime.py
```

## Reconstruction Evidence

Primary verified reconstruction:

- Path: `.gtkb-state/wi5222-reconstruction-current-head-exact-20260714T1520Z`
- Baseline: current `HEAD` `268943aa6d16a032a457e0bc7e8bbbdc671cd119`
- Method: fresh archive of `HEAD`, byte-preserving replacements, raw blob preservation for `platform_tests/scripts/test_gtkb_dispatcher_daemon.py`, hunk patch generated from a HEAD-seeded disposable index.

Older baseline note:

- Path: `.gtkb-state/wi5222-reconstruction-89198140-20260714T1500Z`
- Baseline: proposal-named `89198140fa3a6c932f9be4f634f900b0836ee68e`
- Result: WI-5222 timing changes applied, but the full focused module command produced 456 passed / 4 failed from unrelated provider verdict/finalizer prompt tests that were repaired by later committed work. This report therefore uses current `HEAD` as the finalization parent while preserving the proposal's hunk-isolation intent.

## Specification-Derived Verification Plan

| Spec / governing surface | Executed verification evidence |
| --- | --- |
| `DCL-DISPATCH-ENVELOPE-RULES-001` | `.api-harness/routing.toml` hunk sets D/F/H sessions to `3600`; `test_lo_harness_turn_budget.py` asserts `900 / 3600 / 600`; runtime tests assert `4200` worker and `4500` lease/reset relationships. |
| `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` | `scripts/dispatcher_runtime.py` hunk changes `GENEROUS_WORKER_LIFETIME_SECONDS` to `4200`; runtime and daemon tests assert A/B/C/D/F/H default worker lifetimes. |
| `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` | Focused seven-module pytest run covers cloud base plus Alibaba H, Ollama D, OpenRouter F, common dispatcher runtime, daemon, and LO harness budget assertions. |
| `GOV-HARNESS-ONBOARDING-CONTRACT-001` | Provider routing tests and `test_lo_harness_turn_budget.py` verify truthful configured limits for D/F/H. |
| `GOV-WORK-TREE-HYGIENE-001` | Hunk patch applies to a disposable HEAD-seeded index and affects only five approved paths; live dirty worktree hunks remain excluded. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Pytest, Ruff check, Ruff format-check, disposable-index apply, and diff-check all executed and passed. |

## Commands Run

```text
cd E:\GT-KB\.gtkb-state\wi5222-reconstruction-current-head-exact-20260714T1520Z
E:\GT-KB\groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests/scripts/test_cloud_harness_base.py platform_tests/scripts/test_alibaba_cloud_studio_harness.py platform_tests/scripts/test_ollama_harness.py platform_tests/scripts/test_openrouter_harness.py platform_tests/scripts/test_dispatcher_runtime.py platform_tests/scripts/test_gtkb_dispatcher_daemon.py platform_tests/scripts/test_lo_harness_turn_budget.py -q --tb=short
E:\GT-KB\groundtruth-kb\.venv\Scripts\python.exe -m ruff check .api-harness/routing.toml scripts/dispatcher_runtime.py platform_tests/scripts/test_cloud_harness_base.py platform_tests/scripts/test_alibaba_cloud_studio_harness.py platform_tests/scripts/test_ollama_harness.py platform_tests/scripts/test_openrouter_harness.py platform_tests/scripts/test_dispatcher_runtime.py platform_tests/scripts/test_gtkb_dispatcher_daemon.py platform_tests/scripts/test_lo_harness_turn_budget.py
E:\GT-KB\groundtruth-kb\.venv\Scripts\python.exe -m ruff format --check scripts/dispatcher_runtime.py platform_tests/scripts/test_cloud_harness_base.py platform_tests/scripts/test_alibaba_cloud_studio_harness.py platform_tests/scripts/test_ollama_harness.py platform_tests/scripts/test_openrouter_harness.py platform_tests/scripts/test_dispatcher_runtime.py platform_tests/scripts/test_gtkb_dispatcher_daemon.py platform_tests/scripts/test_lo_harness_turn_budget.py
```

Disposable-index patch verification:

```text
$env:GIT_INDEX_FILE = E:\GT-KB\.gtkb-state\wi5222-current-head-disposable-index-final-evidence.idx
git read-tree HEAD
git apply --cached bridge/hunks/gtkb-wi5222-60m-envelope-successor-current-head.patch
git diff --cached --name-status
git diff --cached --check
git ls-files -s .api-harness/routing.toml scripts/dispatcher_runtime.py platform_tests/scripts/test_dispatcher_runtime.py platform_tests/scripts/test_gtkb_dispatcher_daemon.py platform_tests/scripts/test_lo_harness_turn_budget.py
```

## Observed Results

- Pytest: `481 passed, 1 warning in 55.41s`.
- Ruff check: `All checks passed!`.
- Ruff format-check: `8 files already formatted`.
- Disposable-index apply check: exit 0.
- Disposable-index diff check: exit 0.
- Disposable-index name-status: only the five approved hunk-patch paths listed above.

## Acceptance Criteria Status

- [x] D/F/H resolve to 900-second operations, 3,600-second sessions, and 600 turns.
- [x] A/B/C/D/F/H default workers resolve to 4,200 seconds.
- [x] D's configured 3,600-second session plus 600-second margin equals the 4,200-second routed lifetime.
- [x] Lease TTL and reset straggler age resolve to 4,500 seconds.
- [x] Timeout telemetry continues to report configured lifetime and source truthfully.
- [x] The stale 8-hour source comment is corrected to the 60-minute session plus 10-minute margin.
- [x] The hunk patch contains only approved target paths and WI-5222-owned lines.
- [x] Focused pytest, Ruff check, Ruff format-check, disposable-index apply, and diff-check pass in a detached reconstruction.

## Finalization Instructions For Loyal Opposition

If VERIFIED, finalization must use the WI-5112 disposable-index helper with the hunk patch:

```text
--hunk-patch bridge/hunks/gtkb-wi5222-60m-envelope-successor-current-head.patch
```

The finalizer include set must include the five patched paths:

- `.api-harness/routing.toml`
- `scripts/dispatcher_runtime.py`
- `platform_tests/scripts/test_dispatcher_runtime.py`
- `platform_tests/scripts/test_gtkb_dispatcher_daemon.py`
- `platform_tests/scripts/test_lo_harness_turn_budget.py`

It should also include this bridge chain and the patch artifact:

- `bridge/gtkb-wi5222-60-minute-generous-dispatch-envelope-successor-001.md`
- `bridge/gtkb-wi5222-60-minute-generous-dispatch-envelope-successor-002.md`
- `bridge/gtkb-wi5222-60-minute-generous-dispatch-envelope-successor-003.md`
- `bridge/hunks/gtkb-wi5222-60m-envelope-successor-current-head.patch`

## Risk And Rollback

The main risk is dispatch envelope under-allocation for long but healthy provider reviews. The owner decision accepted that risk based on successful-run history; per-operation timeouts and max-turn budgets remain unchanged. A focused revert of the eventual hunk-scoped finalization commit restores the prior 28,800-second session and 29,400-second worker policy without touching unrelated shared-worktree changes.

## Loyal Opposition Asks

1. Verify the report and hunk patch against the linked specifications and command evidence.
2. Confirm that using current `HEAD` `268943aa6d16a032a457e0bc7e8bbbdc671cd119` as the finalization parent is acceptable given the disclosed `89198140` baseline drift.
3. Return `VERIFIED` with hunk-scoped disposable-index finalization if satisfied; otherwise return `NO-GO` with exact findings.
