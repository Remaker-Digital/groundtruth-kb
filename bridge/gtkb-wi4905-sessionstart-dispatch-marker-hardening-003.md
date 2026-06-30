NEW
author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f09c9-2db0-7b00-a337-40f998b07e56
author_model: GPT-5 Codex
author_model_version: 2026-06
author_model_configuration: Codex Desktop Prime Builder interactive restart; hooks manually disabled in UI for diagnosis; approval_policy=never; cwd=E:\GT-KB

# GT-KB Bridge Implementation Report - gtkb-wi4905-sessionstart-dispatch-marker-hardening - 003

bridge_kind: implementation_report
Document: gtkb-wi4905-sessionstart-dispatch-marker-hardening
Version: 003 (NEW; post-implementation report)
Responds to GO: bridge/gtkb-wi4905-sessionstart-dispatch-marker-hardening-002.md
Approved proposal: bridge/gtkb-wi4905-sessionstart-dispatch-marker-hardening-001.md
Recommended commit type: fix:

## Implementation Claim

Implemented the approved SessionStart dispatch-marker hardening. `LEGACY_FALLBACK` remains a distinct diagnostic decision when `GTKB_BRIDGE_POLLER_RUN_ID` is present without `GTKB_BRIDGE_DISPATCH_KEYWORD`, but it no longer emits the bridge auto-dispatch SessionStart context. Only `DISPATCH_AUTHORIZED` now enters the bridge auto-dispatch context path, which requires the canonical keyword side channel as well as the run id.

Updated Codex and Claude SessionStart regression tests so run-id-only inheritance falls through to normal startup, true bridge auto-dispatch uses both markers, and the Codex hook-parity test no longer writes live `.codex/gtkb-hooks/last-session-start.json` state while exercising dispatch mode.

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
- `DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001` - canonical init keyword receiver semantics.
- `DCL-CROSS-HARNESS-ENFORCEMENT-001` - symmetric cross-harness enforcement.
- `DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001` - dispatcher-only desktop task model.

## Owner Decisions / Input

No new owner decision is required by this implementation report. This work is under `PAUTH-PROJECT-HARNESS-PARITY-PHASE-2-IMPLEMENTATION-2026-06-29` and the GO verdict at `bridge/gtkb-wi4905-sessionstart-dispatch-marker-hardening-002.md`.

## Prior Deliberations

- `bridge/gtkb-wi4905-sessionstart-dispatch-marker-hardening-001.md` - approved implementation proposal.
- `bridge/gtkb-wi4905-sessionstart-dispatch-marker-hardening-002.md` - Loyal Opposition GO verdict.

## Specification-Derived Verification Plan

| Spec / governing surface | Executed verification evidence |
| --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001`; `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`; `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Used `python scripts\bridge_claim_cli.py claim gtkb-wi4905-sessionstart-dispatch-marker-hardening` and `python scripts\implementation_authorization.py begin --bridge-id gtkb-wi4905-sessionstart-dispatch-marker-hardening`; both succeeded before file mutation. |
| `DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001`; `DCL-CROSS-HARNESS-ENFORCEMENT-001`; `DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001` | Added direct Codex and Claude tests proving run-id-only marker inheritance falls through to normal startup and true auto-dispatch uses the canonical keyword side channel. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001`; `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Updated the hook-parity dispatch-mode test to use a temp `OUT_DIR`, preventing live hook diagnostic pollution while preserving schema/dispatch coverage. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Ran focused regression tests, lint, format-check, and compile checks listed below. |

## Commands Run

- `python -m py_compile scripts\session_start_dispatch_core.py` - passed.
- `python -m ruff format scripts\session_start_dispatch_core.py platform_tests\scripts\test_codex_session_start_dispatcher.py platform_tests\scripts\test_claude_session_start_dispatcher.py platform_tests\scripts\test_codex_hook_parity.py` - `4 files left unchanged`.
- `python -m ruff check scripts\session_start_dispatch_core.py platform_tests\scripts\test_codex_session_start_dispatcher.py platform_tests\scripts\test_claude_session_start_dispatcher.py platform_tests\scripts\test_codex_hook_parity.py` - `All checks passed!`.
- `python -m ruff format --check scripts\session_start_dispatch_core.py platform_tests\scripts\test_codex_session_start_dispatcher.py platform_tests\scripts\test_claude_session_start_dispatcher.py platform_tests\scripts\test_codex_hook_parity.py` - `4 files already formatted`.
- `python -m pytest platform_tests\scripts\test_codex_session_start_dispatcher.py::test_legacy_env_without_keyword_falls_through_to_normal_startup platform_tests\scripts\test_claude_session_start_dispatcher.py::test_legacy_env_without_keyword_falls_through_to_normal_startup platform_tests\scripts\test_claude_session_start_dispatcher.py::test_bridge_auto_dispatch_context_bypasses_interactive_startup platform_tests\scripts\test_codex_session_start_dispatcher.py::test_startup_relay_cache_not_written_by_bridge_dispatch_path platform_tests\scripts\test_claude_session_start_dispatcher.py::test_startup_relay_cache_not_written_by_bridge_dispatch_path platform_tests\scripts\test_codex_hook_parity.py::test_codex_session_start_dispatcher_bridge_auto_dispatch_mode -q --tb=short` - `6 passed in 0.52s`.
- Broader diagnostic run: `python -m pytest platform_tests\scripts\test_codex_session_start_dispatcher.py platform_tests\scripts\test_claude_session_start_dispatcher.py platform_tests\scripts\test_codex_hook_parity.py -q --tb=short` - `50 passed`, `1 failed` on `platform_tests/scripts/test_claude_session_start_dispatcher.py::test_session_start_timeout_alignment` because Claude SessionStart timeout is `60s` and Codex SessionStart timeout is `180s`.

## Observed Results

- Run-id-only `GTKB_BRIDGE_POLLER_RUN_ID` no longer produces `# GroundTruth-KB Bridge Auto-Dispatch Session` in either Codex or Claude SessionStart tests.
- True dispatch mode with `GTKB_BRIDGE_POLLER_RUN_ID` plus `GTKB_BRIDGE_DISPATCH_KEYWORD` still emits bridge auto-dispatch context.
- The Codex hook-parity dispatch-mode test now writes diagnostics to a temp directory instead of the live Codex hook directory.
- During diagnosis, an old Antigravity autonomous LO scheduler launched `powershell.exe` child commands (`pytest`, `.claude/hooks/session_start_dispatch.py`, `wrap_scan_hygiene.py`, and `wrap_scan_consistency.py`) from `language_server.exe`. Those children and the current Antigravity process tree were terminated as emergency containment. This is a separate release-health finding: Antigravity autonomous scheduling must not be used as a dispatcher fallback, and any Antigravity dispatch path must launch through a no-window controlled boundary.

## Files Changed

- `scripts/session_start_dispatch_core.py`
- `platform_tests/scripts/test_codex_session_start_dispatcher.py`
- `platform_tests/scripts/test_claude_session_start_dispatcher.py`
- `platform_tests/scripts/test_codex_hook_parity.py`

## Residual Risk / Follow-Up

- `platform_tests/scripts/test_claude_session_start_dispatcher.py::test_session_start_timeout_alignment` currently fails because `.claude/settings.json` has SessionStart timeout `60s` while `.codex/hooks.json` has `180s`. This predates this patch and should be handled as the next bridge-governed release-health correction.
- Antigravity's current GUI-side autonomous scheduler spawned visible `powershell.exe` windows during this investigation. That validates the owner's showstopper: no harness integration can be release-healthy until Antigravity scheduled/autonomous work is disabled or routed through a no-window dispatcher-owned launcher.
