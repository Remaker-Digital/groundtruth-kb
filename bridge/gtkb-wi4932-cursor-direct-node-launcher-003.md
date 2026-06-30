NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f178b-68fb-78c1-b631-7cdfa39877e5
author_model: GPT-5 Codex
author_model_version: gpt-5-codex
author_model_configuration: Codex Desktop automation; reasoning=default
author_metadata_source: runtime_env

# GT-KB Bridge Implementation Report - gtkb-wi4932-cursor-direct-node-launcher - 003

bridge_kind: implementation_report
Document: gtkb-wi4932-cursor-direct-node-launcher
Version: 003 (NEW; post-implementation report)
Responds to GO: bridge/gtkb-wi4932-cursor-direct-node-launcher-002.md
Approved proposal: bridge/gtkb-wi4932-cursor-direct-node-launcher-001.md
Project Authorization: PAUTH-PROJECT-GTKB-DISPATCHER-RELIABILITY-WI-4932-CURSOR-NO-WINDOW-LAUNCHER
Project: PROJECT-GTKB-DISPATCHER-RELIABILITY
Work Item: WI-4932
Recommended commit type: feat

target_paths: ["scripts/cursor_harness.py", "platform_tests/scripts/test_cursor_harness.py"]

## Implementation Claim

Implemented the bounded Cursor dispatcher no-window launcher repair. `scripts/cursor_harness.py` now discovers versioned `%LOCALAPPDATA%/cursor-agent/versions/<version>/node.exe` plus `index.js` entries and prefers that direct argv before Windows `.cmd`/`.ps1` wrapper fallback paths. Explicit `CURSOR_AGENT_BIN` remains highest precedence, non-wrapper standalone PATH entries remain accepted, shell-wrapper PATH entries are deferred behind the direct node/index entrypoint, and wrapper fallback remains available when no direct entrypoint exists.

## Implementation-Start / Work-Intent Evidence

- Initial protected edit packet: `sha256:531d231aeb3a9cb4c648549152fe967f21ca2083fce1e1aaa816ab1b17469f09`.
- Final formatting/normalization packet: `sha256:d9bb4dc3ce8e8e2199cb1b99de6e5a69a9c91cf49e550b37a3ce898990e1c650`.
- Final live work-intent claim: row `25295`, session `019f178b-68fb-78c1-b631-7cdfa39877e5`, bridge `gtkb-wi4932-cursor-direct-node-launcher`.

## Specification Links

- `DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `SPEC-AUQ-POLICY-ENGINE-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `GOV-STANDING-BACKLOG-001`
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001`
- `ADR-DISPATCHER-ARCHITECTURE-001`

## Owner Decisions / Input

- `DELIB-20266506` - owner decision authorizing WI-4932 Cursor dispatcher no-window launcher repair.
- `PAUTH-PROJECT-GTKB-DISPATCHER-RELIABILITY-WI-4932-CURSOR-NO-WINDOW-LAUNCHER` - active project authorization covering this implementation scope.
- No new owner decision was required during implementation.

## Prior Deliberations

- `bridge/gtkb-wi4932-cursor-direct-node-launcher-001.md` - approved implementation proposal carried forward.
- `bridge/gtkb-wi4932-cursor-direct-node-launcher-002.md` - Loyal Opposition GO verdict authorizing implementation.

## Specification-Derived Verification Plan

| Spec / governing surface | Executed verification evidence |
| --- | --- |
| `DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001` | `python -m pytest platform_tests/scripts/test_cursor_harness.py -q --tb=short` passed 25 tests, including direct node/index preference, wrapper fallback, explicit override, and no-window creationflags coverage. |
| `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` | Same Cursor harness test module covers daemon-equivalent command construction and verifies direct argv avoids shell-wrapper command paths when available. |
| `ADR-DISPATCHER-ARCHITECTURE-001` | `python -m ruff check ...` passed; `python -m ruff format --check ...` passed; no topology, config, credential, deployment, or retired-trigger paths changed. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | All edited files are in-root GT-KB platform files: `scripts/cursor_harness.py` and `platform_tests/scripts/test_cursor_harness.py`. No adopter application files changed for this slice. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` / `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Protected edits were made only after live GO, active PAUTH, implementation-start packet, and live work-intent claim were established. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | This report lists exact tests and observed results for the linked implementation behavior before requesting Loyal Opposition verification. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` / `GOV-STANDING-BACKLOG-001` / `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` / `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Implementation remained within the approved bridge artifact lifecycle: proposal -> GO -> implementation -> report. |
| `SPEC-AUQ-POLICY-ENGINE-001` / `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | No AUQ-policy, hook topology, or fallback behavior changes were introduced by this slice. |

## Commands Run

- `python -m pytest platform_tests/scripts/test_cursor_harness.py -q --tb=short`
- `python -m pytest platform_tests/scripts/test_cursor_harness.py platform_tests/scripts/test_bridge_dispatch_config.py::test_wi4933_recent_openrouter_429_is_backpressure_warning platform_tests/scripts/test_bridge_dispatch_config.py::test_wi4933_spawn_rate_limited_launch_reason_warns_as_backpressure platform_tests/scripts/test_bridge_dispatch_config.py::test_wi4933_spawn_rate_limited_last_result_warns_with_live_worker platform_tests/scripts/test_openrouter_harness.py -q --tb=short`
- `python -m ruff check scripts/cursor_harness.py platform_tests/scripts/test_cursor_harness.py groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py scripts/openrouter_harness.py platform_tests/scripts/test_bridge_dispatch_config.py platform_tests/scripts/test_openrouter_harness.py`
- `python -m ruff format --check scripts/cursor_harness.py platform_tests/scripts/test_cursor_harness.py groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py scripts/openrouter_harness.py platform_tests/scripts/test_bridge_dispatch_config.py platform_tests/scripts/test_openrouter_harness.py`
- `git diff --check -- scripts/cursor_harness.py platform_tests/scripts/test_cursor_harness.py groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py scripts/openrouter_harness.py platform_tests/scripts/test_bridge_dispatch_config.py platform_tests/scripts/test_openrouter_harness.py`

## Observed Results

- Cursor focused test module: `25 passed`.
- Combined focused regression set: `51 passed`.
- Ruff check: `All checks passed!`
- Ruff format check: `6 files already formatted`.
- Git whitespace check: exit 0; only Git autocrlf warnings were printed for the touched files.

## Files Changed

- `scripts/cursor_harness.py`
- `platform_tests/scripts/test_cursor_harness.py`

## Acceptance Criteria Status

- Dispatcher-spawned Cursor harness commands do not use `cmd.exe` or PowerShell wrapper paths when a versioned `node.exe` plus `index.js` entrypoint exists.
- Explicit `CURSOR_AGENT_BIN` override behavior remains preserved.
- Non-wrapper standalone PATH agent behavior remains preserved.
- Shell-wrapper fallback remains covered when no direct entrypoint exists.
- No dispatcher topology, credential, production deployment, external GT-KB artifact, or retired trigger fallback changes were made.

## Risk And Rollback

Residual risk is limited to Windows Cursor Agent install layout variation. The implementation fails open to the prior wrapper fallback when no direct versioned entrypoint exists. Rollback is a revert of `scripts/cursor_harness.py` and `platform_tests/scripts/test_cursor_harness.py`; bridge audit files remain append-only.

## Loyal Opposition Asks

1. Verify the implementation against the linked specifications and executed command evidence.
2. Return VERIFIED if the report and implementation satisfy the approved proposal, otherwise return NO-GO with findings.
