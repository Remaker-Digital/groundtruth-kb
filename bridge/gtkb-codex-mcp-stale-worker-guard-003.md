NEW

# GT-KB Bridge Implementation Report - gtkb-codex-mcp-stale-worker-guard - 003

bridge_kind: implementation_report
Document: gtkb-codex-mcp-stale-worker-guard
Version: 003 (NEW; post-implementation report)
Author: Prime Builder (Codex)
Date: 2026-06-23T20:24:00Z

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019ef3a8-fefa-7382-a13c-c93e5ee51026
author_model: Codex GPT-5
author_model_version: not exposed by current harness
author_model_configuration: Codex desktop, approval_policy=never, GT-KB Prime Builder

Responds to GO: bridge/gtkb-codex-mcp-stale-worker-guard-002.md
Approved proposal: bridge/gtkb-codex-mcp-stale-worker-guard-001.md
Project Authorization: PAUTH-PROJECT-GTKB-CODEX-MCP-WORKER-LIFECYCLE-HYGIENE-001
Project: PROJECT-GTKB-CODEX-MCP-WORKER-LIFECYCLE-HYGIENE
Work Item: WI-4776
Recommended commit type: fix

## Implementation Claim

Implemented a conservative Codex MCP worker lifecycle guard for WI-4776. The guard inspects local process state, classifies only known MCP worker command-line families (Playwright/browser and Context7-style Node workers), treats workers with a running parent process as attached/live, treats detached workers as stale only when the parent is absent or the parent PID was reused, and exposes cleanup only through an explicit `--cleanup --dry-run` or `--cleanup --yes` mode.

Codex startup now invokes a report-only wrapper. The wrapper uses `--quiet-when-clean`, so normal attached/live MCP workers do not add startup noise and no startup path can terminate processes.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - Implementation began only after the `GO` verdict and implementation authorization packet for this bridge thread.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - This report carries forward the approved proposal's linked specifications and maps verification evidence to them.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - The report preserves project authorization, project, and work item metadata.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - Verification includes spec-derived tests plus live read-only and dry-run diagnostics.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - Changes are limited to GT-KB/Codex development-environment surfaces; no `applications/` files are modified for this implementation.
- `GOV-STANDING-BACKLOG-001` - WI-4776 remains the durable work item authority for this hygiene slice.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - The crash diagnosis was converted into governed implementation evidence through the bridge.

## Owner Decisions / Input

- `DELIB-20265796` authorized the hygiene project, WI-4776, linked test, and implementation proposal for stale Codex MCP worker prevention.
- No new owner decision was required during implementation. Live cleanup was not executed.

## Prior Deliberations

- `DELIB-20265796` - Owner authorized the Codex MCP stale-worker hygiene project and bounded implementation path.
- `bridge/gtkb-codex-mcp-stale-worker-guard-001.md` - Approved proposal.
- `bridge/gtkb-codex-mcp-stale-worker-guard-002.md` - Loyal Opposition `GO` verdict.

## Specification-Derived Verification Plan

| Spec / governing surface | Executed verification evidence |
| --- | --- |
| `GOV-STANDING-BACKLOG-001` / `WI-4776` / `TEST-11236` | `groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests/scripts/test_codex_mcp_worker_guard.py -q --no-header` passed: 7 tests prove known detached Playwright/Context7 workers are classified, live/attached workers are excluded from cleanup, unrelated `node.exe` is ignored, dry-run does not terminate, live cleanup targets only stale workers, and cleanup requires explicit `--dry-run` or `--yes`. |
| Codex startup hook integration | `groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests/scripts/test_check_codex_hook_parity.py -q --no-header` passed: 2 tests prove SessionStart registers the guard wrapper and the wrapper is report-only. |
| Existing Codex hook parity | `python -m pytest platform_tests/scripts/test_codex_hook_parity.py -q --tb=short` passed: 13 tests; `python scripts/check_codex_hook_parity.py` passed. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | `groundtruth-kb\.venv\Scripts\python.exe scripts/bridge_applicability_preflight.py --bridge-id gtkb-codex-mcp-stale-worker-guard` passed with no missing required specs. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `groundtruth-kb\.venv\Scripts\gt.exe backlog show WI-4776 --json` confirmed WI-4776 is open under `PROJECT-GTKB-CODEX-MCP-WORKER-LIFECYCLE-HYGIENE`; `groundtruth-kb\.venv\Scripts\gt.exe projects show PROJECT-GTKB-CODEX-MCP-WORKER-LIFECYCLE-HYGIENE --json` confirmed the active project and authorization scope. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `python scripts/codex_mcp_worker_guard.py --report --json` returned a read-only live diagnostic with `known_mcp_worker_count=6`, `live_workers=6`, `stale_workers=0`, and `suspect_workers=0`. `python scripts/codex_mcp_worker_guard.py --cleanup --dry-run --json` returned `cleanup.requested=true`, `dry_run=true`, `planned=[]`, `terminated=[]`, and `failed=[]`. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `git status --short --untracked-files=all -- .codex/hooks.json scripts/codex_mcp_worker_guard.py .codex/gtkb-hooks/codex-mcp-worker-guard.cmd platform_tests/scripts/test_codex_mcp_worker_guard.py platform_tests/scripts/test_check_codex_hook_parity.py` showed only the five approved target paths for this WI. |

## Commands Run

- `python scripts/implementation_authorization.py validate --target scripts/codex_mcp_worker_guard.py --target .codex/gtkb-hooks/codex-mcp-worker-guard.cmd --target .codex/hooks.json --target platform_tests/scripts/test_codex_mcp_worker_guard.py --target platform_tests/scripts/test_check_codex_hook_parity.py`
- `python -m pytest platform_tests/scripts/test_codex_mcp_worker_guard.py -q --tb=short`
- `python -m pytest platform_tests/scripts/test_check_codex_hook_parity.py -q --tb=short`
- `python -m pytest platform_tests/scripts/test_codex_hook_parity.py -q --tb=short`
- `python scripts/check_codex_hook_parity.py`
- `python -m ruff check scripts/codex_mcp_worker_guard.py platform_tests/scripts/test_codex_mcp_worker_guard.py platform_tests/scripts/test_check_codex_hook_parity.py`
- `python -m ruff format --check scripts/codex_mcp_worker_guard.py platform_tests/scripts/test_codex_mcp_worker_guard.py platform_tests/scripts/test_check_codex_hook_parity.py`
- `groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests/scripts/test_codex_mcp_worker_guard.py -q --no-header`
- `groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests/scripts/test_check_codex_hook_parity.py -q --no-header`
- `groundtruth-kb\.venv\Scripts\gt.exe backlog show WI-4776 --json`
- `groundtruth-kb\.venv\Scripts\gt.exe projects show PROJECT-GTKB-CODEX-MCP-WORKER-LIFECYCLE-HYGIENE --json`
- `groundtruth-kb\.venv\Scripts\python.exe scripts/bridge_applicability_preflight.py --bridge-id gtkb-codex-mcp-stale-worker-guard`
- `cmd /d /s /c E:\GT-KB\.codex\gtkb-hooks\codex-mcp-worker-guard.cmd`
- `python scripts/codex_mcp_worker_guard.py --report --json`
- `python scripts/codex_mcp_worker_guard.py --cleanup --dry-run --json`
- `git diff --check -- .codex/hooks.json scripts/codex_mcp_worker_guard.py .codex/gtkb-hooks/codex-mcp-worker-guard.cmd platform_tests/scripts/test_codex_mcp_worker_guard.py platform_tests/scripts/test_check_codex_hook_parity.py`

## Observed Results

- Implementation authorization validation returned `authorized: true` for all five target paths.
- Focused worker-guard tests passed twice: first with system Python (`6 passed`, then `7 passed` after attached-worker tuning), then with the project venv (`7 passed, 1 warning`). The venv warning is the existing pytest config warning for `asyncio_mode`.
- Focused hook-registration tests passed with system Python and project venv (`2 passed`; venv emitted the same existing pytest config warning).
- Existing Codex hook parity tests passed (`13 passed`), and the parity CLI printed `Codex hook parity: PASS`.
- Ruff check and format checks passed after mechanical import/format fixes.
- The startup wrapper command exited `0` and emitted no stdout in the current attached-worker state.
- Live read-only diagnostic found six known MCP workers, all attached/live, with zero stale and zero suspect workers.
- Cleanup dry-run planned zero terminations and did not terminate any process.

## Files Changed

- `scripts/codex_mcp_worker_guard.py` - New report/cleanup CLI with pure classifier, live process collection, JSON/text output, dry-run cleanup planning, and explicit live cleanup confirmation.
- `.codex/gtkb-hooks/codex-mcp-worker-guard.cmd` - New report-only Codex startup wrapper.
- `.codex/hooks.json` - Registers the wrapper as a `SessionStart` report-only hook.
- `platform_tests/scripts/test_codex_mcp_worker_guard.py` - New spec-derived classifier and cleanup safety tests.
- `platform_tests/scripts/test_check_codex_hook_parity.py` - New focused hook-registration parity tests for the MCP guard.

## Recommended Commit Type

- Recommended commit type: `fix`
- Justification: This mitigates the Codex stability failure mode documented in WI-4776 by adding a guarded detector/reporting path and explicit cleanup controls.

## Risk And Rollback

Residual risk is intentionally bounded to false-positive reporting, not process termination, during startup. Startup uses report-only mode and no cleanup flags. Live cleanup requires `--cleanup --yes`, while dry-run planning requires `--cleanup --dry-run`. The classifier only recognizes known MCP command families and only treats detached workers as cleanup-eligible.

Rollback is a single commit revert of the five target paths listed above. No data migration, credential change, application runtime change, or production deployment was performed.

## Loyal Opposition Asks

1. Verify that the classifier excludes live/attached MCP workers and unrelated Node processes while preserving explicit stale cleanup behavior.
2. Verify that Codex startup integration is report-only and cannot terminate processes.
3. Return `VERIFIED` if the implementation and evidence satisfy WI-4776; otherwise return `NO-GO` with findings.
