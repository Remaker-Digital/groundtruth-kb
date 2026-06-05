NEW
author_identity: Codex Prime Builder
author_harness_id: A
author_session_context_id: 019e95cd-bdc9-7da2-9b1d-c4cbb31e21d1
author_model: GPT-5 Codex
author_model_version: gpt-5
author_model_configuration: Codex desktop; interactive; Prime Builder; danger-full-access; approval-policy never
author_metadata_source: Codex explicit metadata in bridge implementation report

Project Authorization: PAUTH-PROJECT-GTKB-STARTUP-REFRACTOR-001-COMPACT-AUTO-DISPATCH-STARTUP-IMPLEMENTATION-AUTHORIZATION
Implementation Authorization Packet: sha256:d3af5cc358580c334cb587adaf7d4b0da3e6a1e14b9d347e40a06215dd521119
Project: PROJECT-GTKB-STARTUP-REFRACTOR-001
Work Item: WI-4361
Recommended commit type: feat

target_paths: ["scripts/session_self_initialization.py","scripts/session_start_dispatch_core.py","platform_tests/scripts/test_session_self_initialization.py","platform_tests/hooks/test_session_start_dispatch_role_cache.py","platform_tests/scripts/test_claude_session_start_dispatcher.py","platform_tests/scripts/test_codex_session_start_dispatcher.py",".gtkb-state/startup-payload-profiles/**"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

# Startup Payload Profiler + Compact SessionStart Context - Post-Implementation Report

bridge_kind: implementation_report
Document: gtkb-startup-payload-profiler-compact-context
Version: 003
Author: Prime Builder (Codex, harness A)
Date: 2026-06-05 UTC
Reviewed proposal: `bridge/gtkb-startup-payload-profiler-compact-context-001.md`
GO verdict: `bridge/gtkb-startup-payload-profiler-compact-context-002.md`

## Claim

The `WI-4361` implementation is complete for the approved compact SessionStart payload slice.

Default SessionStart `hookSpecificOutput.additionalContext` is now a compact routing and startup-instruction summary, while the complete owner-visible startup disclosure is emitted separately in `hookSpecificOutput.startupDisclosure` for init-keyword relay cache writing. The startup service also emits deterministic payload-profile metadata and writes the latest generated profile under `.gtkb-state/startup-payload-profiles/`.

This report does not claim `WI-4360` closure. The profile instrumentation added here supports the paired profiler direction, but `WI-4360` remains a separate backlog item unless later authorization and acceptance evidence close it.

## Specification Links

- `GOV-SESSION-SELF-INITIALIZATION-001` - startup payloads still come from the live startup model and freshness contract; the service now emits compact context plus a separate disclosure.
- `DCL-SESSION-STARTUP-TOKEN-BUDGET-001` - compact context removes the embedded full disclosure from default model-facing SessionStart context and adds byte/line/character/rough-token profile metadata.
- `DCL-INIT-KEYWORD-STARTUP-DISCLOSURE-RELAY-001` - dispatcher relay-cache writing now prefers `startupDisclosure` and keeps legacy embedded-marker extraction as fallback.
- `SPEC-CODEX-STARTUP-INPUT-GATE-TRIGGER-001` - the final hook envelope still emits standard `hookSpecificOutput.hookEventName == SessionStart` and compact `additionalContext`.
- `DCL-SESSION-ROLE-RESOLUTION-001` - role-scoped startup disclosure caches continue to be generated independent of durable role-set shape.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - implementation started after the live bridge thread received GO and after the implementation authorization packet was minted.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - this report maps each cited behavior to executed test or lint evidence.

## Implementation Summary

- Added `STARTUP_PAYLOAD_PROFILE_CONTRACT_VERSION` and `.gtkb-state/startup-payload-profiles/last-<harness>.json` runtime profile handling in `scripts/session_self_initialization.py`.
- Changed `_startup_service_context(...)` so it no longer embeds `## User-Visible Startup Message` or the full report in `additionalContext`; it now emits compact routing facts, token-reduction status, top-priority summaries, artifact paths, relay-cache paths, and harness-only startup instructions.
- Added `hookSpecificOutput.startupDisclosure` containing the complete rendered startup report.
- Added `hookSpecificOutput.startupPayloadProfile` with UTF-8 bytes, line count, character count, rough token estimate, and SHA-256 for both `additionalContext` and `startupDisclosure`.
- Updated `scripts/session_start_dispatch_core.py` so normal SessionStart cache writing uses `startupDisclosure` when available, with fallback to the legacy marker-split behavior.
- Updated focused startup-service and dispatcher tests for compact context, separate disclosure, profile metrics/file evidence, and both Codex/Claude relay-cache behavior.

## Files Changed

- `scripts/session_self_initialization.py`
- `scripts/session_start_dispatch_core.py`
- `platform_tests/scripts/test_session_self_initialization.py`
- `platform_tests/scripts/test_claude_session_start_dispatcher.py`
- `platform_tests/scripts/test_codex_session_start_dispatcher.py`
- Generated runtime evidence observed under `.gtkb-state/startup-payload-profiles/last-claude.json` and `.gtkb-state/startup-payload-profiles/last-codex.json`.

`platform_tests/hooks/test_session_start_dispatch_role_cache.py` remained behaviorally covered by verification but did not require a source edit.

## Specification-Derived Verification

| Spec / claim | Verification | Result |
| --- | --- | --- |
| `GOV-SESSION-SELF-INITIALIZATION-001` fresh startup generation and valid service payload | Targeted startup-service tests covering service context and emitted payload | PASS |
| `DCL-SESSION-STARTUP-TOKEN-BUDGET-001` compact default context and profile metrics | `test_emit_startup_service_payload_returns_full_codex_session_start_contract` asserts compact context, separate disclosure, profile hashes/byte counts, and written profile file | PASS |
| `DCL-INIT-KEYWORD-STARTUP-DISCLOSURE-RELAY-001` complete disclosure relay cache | Added Codex and Claude dispatcher tests proving caches use `startupDisclosure` while final hook output stays compact | PASS |
| `SPEC-CODEX-STARTUP-INPUT-GATE-TRIGGER-001` hook envelope shape | Dispatcher tests assert emitted `additionalContext` remains the final SessionStart context | PASS |
| `DCL-SESSION-ROLE-RESOLUTION-001` role cache generation | Existing role-cache parity suite passed unchanged | PASS |
| Code quality / formatting | Ruff check and format check on touched source/tests | PASS |

## Commands Executed

```powershell
.\groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests/hooks/test_session_start_dispatch_role_cache.py -q --tb=short
```

Result: 15 passed in 0.37s.

```powershell
.\groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests/scripts/test_codex_session_start_dispatcher.py -q --tb=short
```

Result: 12 passed in 0.44s.

```powershell
.\groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests/scripts/test_session_self_initialization.py::test_startup_report_treats_first_owner_message_as_session_start_stimulus platform_tests/scripts/test_session_self_initialization.py::test_startup_report_surfaces_session_overlay_status_as_non_authoritative platform_tests/scripts/test_session_self_initialization.py::test_loyal_opposition_role_profile_reports_active_bridge platform_tests/scripts/test_session_self_initialization.py::test_emit_startup_service_payload_returns_full_codex_session_start_contract platform_tests/scripts/test_claude_session_start_dispatcher.py::test_normal_startup_relay_cache_uses_startup_disclosure_field platform_tests/scripts/test_codex_session_start_dispatcher.py::test_normal_startup_relay_cache_uses_startup_disclosure_field -q --tb=short
```

Result: 6 passed in 64.26s.

```powershell
.\groundtruth-kb\.venv\Scripts\python.exe -m ruff check scripts/session_self_initialization.py scripts/session_start_dispatch_core.py platform_tests/scripts/test_session_self_initialization.py platform_tests/scripts/test_claude_session_start_dispatcher.py platform_tests/scripts/test_codex_session_start_dispatcher.py
```

Result: All checks passed.

```powershell
.\groundtruth-kb\.venv\Scripts\python.exe -m ruff format --check scripts/session_self_initialization.py scripts/session_start_dispatch_core.py platform_tests/scripts/test_session_self_initialization.py platform_tests/scripts/test_claude_session_start_dispatcher.py platform_tests/scripts/test_codex_session_start_dispatcher.py
```

Result: 5 files already formatted.

## Attempted Broader Verification

```powershell
.\groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests/scripts/test_session_self_initialization.py platform_tests/hooks/test_session_start_dispatch_role_cache.py platform_tests/scripts/test_claude_session_start_dispatcher.py platform_tests/scripts/test_codex_session_start_dispatcher.py -q --tb=short
```

Result: timed out after 124 seconds during the broader combined run.

Follow-up split runs showed:

- `platform_tests/scripts/test_session_self_initialization.py -q --tb=short` timed out in an existing startup-model subprocess call to `git branch --show-current` during an early, unrelated full-file test.
- `platform_tests/scripts/test_claude_session_start_dispatcher.py -q --tb=short` timed out in the file's existing live dispatcher startup probe.
- The directly impacted tests listed above passed after stale child processes from the timed-out broad runs were cleared.

## Acceptance Criteria Status

- Default SessionStart `additionalContext` is compact and no longer embeds `## User-Visible Startup Message`: met.
- `hookSpecificOutput.startupDisclosure` carries the complete owner-visible startup disclosure: met.
- Dispatcher cache writing uses `startupDisclosure` when present and preserves legacy fallback: met.
- Payload profile metadata is deterministic and written under `.gtkb-state/startup-payload-profiles/`: met.
- Focused startup-service and dispatcher tests pass: met.

## Risks / Follow-Up

- The broader full-file startup tests include live subprocess paths that timed out independently of the changed assertions. The narrow tests exercise the modified behavior, and the successful Codex dispatcher and role-cache full-file runs give additional coverage.
- `WI-4360` should remain open until a later implementation explicitly defines and verifies the profiler acceptance criteria beyond this slice's runtime profile object.

## Owner Action Required

None.
