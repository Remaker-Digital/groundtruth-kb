NEW
author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f09c9-2db0-7b00-a337-40f998b07e56
author_model: GPT-5 Codex
author_model_version: 2026-06
author_model_configuration: Codex Desktop Prime Builder interactive session; hooks restored with no-window containment; approval_policy=never; cwd=E:\GT-KB

# GT-KB Bridge Implementation Report - gtkb-wi4905-codex-hook-release-parity-restore - 003

bridge_kind: implementation_report
Document: gtkb-wi4905-codex-hook-release-parity-restore
Version: 003 (NEW; post-implementation report)
Responds to GO: bridge/gtkb-wi4905-codex-hook-release-parity-restore-002.md
Approved proposal: bridge/gtkb-wi4905-codex-hook-release-parity-restore-001.md
Recommended commit type: feat:

## Implementation Claim

Restored Codex hook parity for the release gate using hidden, bounded Windows launchers and without reviving retired bridge-trigger automation.

The Codex hook registry is no longer empty. It now registers the expected SessionStart, UserPromptSubmit, PreToolUse, PostToolUse, and Stop lifecycle hooks through `pythonw.exe` plus the hardened no-window helpers. The helper paths are extensionless shims (`.codex/gtkb-hooks/run_py_no_window` and `.codex/gtkb-hooks/run_cmd_no_window`) delegating to the existing wrapper implementations so parity discovery can see the real hook surfaces instead of counting the wrapper `.py` stems as capabilities.

The restored registry explicitly excludes `cross_harness_bridge_trigger.py`, `single_harness_bridge_automation.py`, `single_harness_bridge_dispatcher.py`, `bridge-dispatch-trigger`, `dispatcher-daemon.cmd`, and `gtkb_dispatcher_daemon.py`. Dispatcher operation remains daemon-owned. Manual user assignment remains the only fallback path when daemon dispatch is unhealthy.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - role-correct bridge authority and numbered-file filing.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - artifact-oriented change control.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - proposal-to-spec linkage.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - spec-derived verification evidence.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - project/work-item/target metadata.
- `SPEC-AUQ-POLICY-ENGINE-001` - owner authorization policy.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - platform/adopter boundary.
- `GOV-STANDING-BACKLOG-001` - standing backlog governance.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - Codex hook parity fallback.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - artifact-oriented development.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - artifact lifecycle triggers.
- `DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001` - dispatcher desktop-task containment.
- `DCL-CROSS-HARNESS-ENFORCEMENT-001` - cross-harness enforcement.
- `GOV-RELEASE-READINESS-GOVERNED-TESTING-001` - release-readiness governed testing.
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` - cross-harness parity enforcement.
- `ADR-CROSS-HARNESS-PARITY-001` - harness parity architecture.

## Owner Decisions / Input

No new owner decision is required by this implementation report. This work is under `PAUTH-PROJECT-HARNESS-PARITY-PHASE-2-IMPLEMENTATION-2026-06-29` and the GO verdict at `bridge/gtkb-wi4905-codex-hook-release-parity-restore-002.md`.

## Prior Deliberations

- `bridge/gtkb-wi4905-codex-hook-release-parity-restore-001.md` - approved implementation proposal.
- `bridge/gtkb-wi4905-codex-hook-release-parity-restore-002.md` - Loyal Opposition GO verdict.

## Specification-Derived Verification Plan

| Spec / governing surface | Executed verification evidence |
| --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001`; `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`; `SPEC-AUQ-POLICY-ENGINE-001` | `python scripts\implementation_authorization.py begin --bridge-id gtkb-wi4905-codex-hook-release-parity-restore` succeeded before protected edits; report filed as next numbered bridge document. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001`; `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001`; `ADR-CROSS-HARNESS-PARITY-001` | `python scripts\parity_discovery_diff.py --json` returned PASS / no findings after restoring Codex hooks. |
| `DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001`; `DCL-CROSS-HARNESS-ENFORCEMENT-001` | Focused hook tests assert `pythonw.exe` launchers, extensionless wrapper use, and absence of retired dispatcher-trigger paths. |
| `GOV-RELEASE-READINESS-GOVERNED-TESTING-001`; `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Focused pytest, ruff check, ruff format-check, hook parity checker, JSON validation, and `gt project doctor --json` were run. Doctor exits 0 / overall warning and no longer reports cross-harness parity discovery-diff or dispatcher config CLI-only guard failures for the Codex hook registry. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001`; `GOV-STANDING-BACKLOG-001`; `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`; `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Changes remain in platform governance/hook/test surfaces under `E:\GT-KB`; no adopter application files were modified by this slice. |

## Commands Run

- `python -m pytest platform_tests\scripts\test_parity_discovery_diff.py platform_tests\scripts\test_codex_hook_runtime_containment.py platform_tests\scripts\test_hook_registration_parity.py platform_tests\scripts\test_codex_hook_parity.py platform_tests\scripts\test_cross_harness_protocol_parity.py platform_tests\scripts\test_fab09_safety_gate_registration.py platform_tests\hooks\test_auto_finalize_verified_verdicts.py -q --tb=short`
- `python -m ruff check scripts\parity_discovery_diff.py platform_tests\scripts\test_parity_discovery_diff.py platform_tests\scripts\test_codex_hook_runtime_containment.py platform_tests\scripts\test_codex_hook_parity.py platform_tests\scripts\test_cross_harness_protocol_parity.py platform_tests\scripts\test_hook_registration_parity.py`
- `python -m ruff format --check scripts\parity_discovery_diff.py platform_tests\scripts\test_parity_discovery_diff.py platform_tests\scripts\test_codex_hook_runtime_containment.py platform_tests\scripts\test_codex_hook_parity.py platform_tests\scripts\test_cross_harness_protocol_parity.py platform_tests\scripts\test_hook_registration_parity.py`
- `python scripts\parity_discovery_diff.py --json`
- `python scripts\check_codex_hook_parity.py --project-root E:\GT-KB`
- `python -m json.tool .codex\hooks.json > $null`
- `gt project doctor --json`

## Observed Results

- Focused pytest bundle: `72 passed`.
- Ruff check: `All checks passed`.
- Ruff format-check: `6 files already formatted`.
- `python scripts\parity_discovery_diff.py --json`: PASS with empty findings.
- `python scripts\check_codex_hook_parity.py --project-root E:\GT-KB`: PASS.
- `.codex/hooks.json` JSON validation: passed.
- `gt project doctor --json`: exit code 0, overall `warning`; hook registration, cross-harness parity discovery-diff, dispatcher daemon substrate readiness, dispatcher config CLI-only guard, harness dispatch launchability, and Cursor dispatch readiness checks pass. Remaining warnings/failures are pre-existing or separately scoped release-health items, including GitHub CLI authentication, artifact drift, untracked VERIFIED verdicts, harness-state consistency, Ollama consistency, skill health, and one non-required prior-session ORIENT warning.

## Files Changed

- `.codex/config.toml`
- `.codex/hooks.json`
- `.codex/gtkb-hooks/run_cmd_no_window`
- `.codex/gtkb-hooks/run_py_no_window`
- `platform_tests/scripts/test_codex_hook_runtime_containment.py`
- `platform_tests/scripts/test_codex_hook_parity.py`
- `platform_tests/scripts/test_cross_harness_protocol_parity.py`

## Acceptance Criteria Status

- PASS: Codex hooks are registered again and include the expected release-governance lifecycle surfaces.
- PASS: Every registered Codex hook command starts with `pythonw.exe`.
- PASS: Registered Codex hook commands use extensionless no-window helper shims and do not expose helper `.py` stems to parity discovery.
- PASS: Retired trigger paths are absent from the Codex hook registry.
- PASS: Parity discovery and Codex hook parity checks pass after restoration.
- PASS: `gt project doctor --json` no longer reports the Codex hook parity/config failures this slice targeted.

## Residual Release Blocker Outside This Slice

During verification, the dispatcher still showed live runtime defects even while static launchability checks passed:

- Ollama/D reviewer dispatch accepted work and then hung with empty stdout/stderr until reaped.
- OpenRouter/F manual dispatch timed out before reaching a Bash tool call.
- Cursor/E manual dispatch timed out waiting for Cursor Agent.
- Antigravity/C manual `agy --print` did successfully produce GO verdicts.

These are not regressions from the Codex hook restoration, but they remain release blockers for full dispatcher readiness and should be handled by a follow-on dispatcher runtime hardening proposal.

## Risk And Rollback

Risk is moderate because Codex hooks are active again. The containment risk is bounded by `pythonw.exe`, finite-stdin no-window wrappers, short per-hook timeouts, and explicit tests banning retired dispatcher-trigger paths.

Rollback is to disable `.codex/config.toml` hooks and restore `.codex/hooks.json` to an empty registry. Bridge files are append-only and should not be deleted.

## Loyal Opposition Asks

1. Verify that Codex hook parity has been restored without reintroducing visible console spawning or retired bridge-trigger automation.
2. Return VERIFIED if the report and implementation satisfy the approved proposal; otherwise return NO-GO with concrete findings.
