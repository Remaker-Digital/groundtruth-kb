NEW
::init gtkb pb
::open build

# GT-KB Bridge Implementation Report - gtkb-wi5671-startup-relay-fail-open - 009

bridge_kind: implementation_report
Document: gtkb-wi5671-startup-relay-fail-open
Version: 009 (NEW; post-implementation report)
Responds to: bridge/gtkb-wi5671-startup-relay-fail-open-008.md
Approved proposal: bridge/gtkb-wi5671-startup-relay-fail-open-001.md
Project Authorization: PAUTH-PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-DISPATCHER-BLACK-BOX-HARDENING-SESSION-STARTUP-LATENCY-WI-5671-SLICE-B-STARTUP-RELAY-FAIL-OPEN-DETACHED-BACKGROUND-REFRESH
Project: PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-DISPATCHER-BLACK-BOX-HARDENING-SESSION-STARTUP-LATENCY
Work Item: WI-5671
Recommended commit type: fix:
kb_mutation_in_scope: false

**No KB mutation.** This implementation report performs no MemBase write and does not modify groundtruth.db.

author_identity: prime-builder/goose
author_harness_id: G
author_session_context_id: 235a0cb7-2d12-4241-9951-a54c73c301f8
author_model: DeepSeek V4 Flash 0731
author_model_version: deepseek-v4-flash-0731
author_model_configuration: goose-desktop-interactive;role=prime-builder;::init gtkb pb;build activity
author_metadata_source: session envelope (worker_role_provenance)

## Implementation Claim

WI-5671 Slice B implements the startup-relay fail-open fix in
scripts/workstream_focus.py: a stale-but-valid cache now fails OPEN (relays the
cached disclosure with an explicit staleness banner) instead of failing closed,
and the refresh is dispatched as a DETACHED background process so the current
prompt is never blocked by the 5s-capped synchronous render (which
deterministically abandoned on large reports).

- Edit A (fail-open): in _startup_gate_response, the consistent_except_freshness
  branch now builds a staleness banner (naming generated_at + the freshness TTL,
  directing the reader to fresh canonical reads) and returns the relayed
  disclosure with the banner, returning (response, True) instead of the
  GTKB STARTUP RELAY FAILURE diagnostic. Fail-closed is preserved for a missing
  cache (pointer None) and for a genuine content/identity mismatch.
- Edit B (detached refresh): in _startup_relay_pointer, the stale/recoverable-
  drift path now calls _dispatch_detached_startup_relay_refresh (a new helper
  that launches a detached, headless subprocess running the bounded refresh via
  scripts/windows_subprocess.hidden_process_popen_kwargs) instead of the
  synchronous _refresh_startup_relay_cache_bounded join.
- Tests: added 2 focused tests (fail-open relays no FAILURE with staleness
  banner; stale path does not invoke the synchronous render) and updated 5
  existing behavior-encoding tests to the new fail-open/detached semantics.

## Specification Links

- GOV-SESSION-SELF-INITIALIZATION-001
- DCL-INIT-KEYWORD-STARTUP-DISCLOSURE-RELAY-001
- GOV-SOURCE-OF-TRUTH-FRESHNESS-001
- ADR-CODEX-HOOK-PARITY-FALLBACK-001
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001
- DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001
- GOV-FILE-BRIDGE-AUTHORITY-001
- ADR-ISOLATION-APPLICATION-PLACEMENT-001

## Owner Decisions / Input

No new owner decision required. The bounded PAUTH
PAUTH-PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-DISPATCHER-BLACK-BOX-HARDENING-SESSION-STARTUP-LATENCY-WI-5671-SLICE-B-STARTUP-RELAY-FAIL-OPEN-DETACHED-BACKGROUND-REFRESH
was verified active; the active GO (v008), matching claim, and
implementation-start packet were in place before any protected mutation.

## Prior Deliberations

- bridge/gtkb-wi5671-startup-relay-fail-open-001.md - approved implementation proposal.
- bridge/gtkb-wi5671-startup-relay-fail-open-008.md - Loyal Opposition GO verdict authorizing implementation.

## Specification-Derived Verification Plan

| Spec / governing surface | Executed verification evidence |
| --- | --- |
| GOV-SESSION-SELF-INITIALIZATION-001 + DCL-INIT-KEYWORD-STARTUP-DISCLOSURE-RELAY-001 | test_startup_gate_fails_open_on_stale_but_valid_cache: stale-but-valid relays disclosure, no GTKB STARTUP RELAY FAILURE, staleness banner present. |
| DCL-INIT-KEYWORD-STARTUP-DISCLOSURE-RELAY-001 (fail-closed preserved) | Existing tests (test_startup_gate_fails_visibly_on_inconsistent_cache, test_genuine_identity_mismatch_message_unchanged, test_startup_gate_no_self_heal_on_non_recoverable_inconsistency) assert FAILURE still emitted for missing/mismatched/inconsistent caches. |
| GOV-SOURCE-OF-TRUTH-FRESHNESS-001 | Fail-open body contains explicit staleness banner naming generated_at + TTL + fresh-reads direction. |
| relay-reliability (no synchronous block) | test_startup_gate_stale_path_does_not_invoke_synchronous_refresh: synchronous render not invoked; detached dispatch used. |
| ADR-CODEX-HOOK-PARITY-FALLBACK-001 | scripts/check_codex_hook_parity.py -> Codex hook parity: PASS. |
| DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 | pytest platform_tests/hooks/test_workstream_focus.py -> 84 passed, 3 skipped. |
| Python quality | ruff check and ruff format --check on the two changed files -> clean. |

## Commands Run

- python -m pytest platform_tests/hooks/test_workstream_focus.py -q --no-header
- python -m pytest platform_tests/hooks/test_workstream_focus.py -q --tb=short
- python scripts/check_codex_hook_parity.py
- python -m ruff check scripts/workstream_focus.py platform_tests/hooks/test_workstream_focus.py
- python -m ruff format --check scripts/workstream_focus.py platform_tests/hooks/test_workstream_focus.py

## Observed Results

- Pytest: 84 passed, 3 skipped, 1 warning (includes 2 new + 5 updated tests).
- Codex hook parity: PASS.
- Ruff check: All checks passed; ruff format applied and re-checked clean.

## Files Changed

- scripts/workstream_focus.py (fail-open in _startup_gate_response; detached refresh + _dispatch_detached_startup_relay_refresh helper)
- platform_tests/hooks/test_workstream_focus.py (2 new + 5 updated tests)

Excluded out-of-scope dirty paths: 673.

## Recommended Commit Type

- Recommended commit type: fix: (startup-relay fail-open + detached background refresh).

## Acceptance Criteria Status

- Fail-open on mere staleness with a staleness banner (generated_at + TTL + fresh-read direction) - MET.
- Detached background refresh; current prompt not blocked by the joined synchronous render - MET.
- Fail-closed preserved for missing cache and genuine content/identity mismatch - MET (existing tests green).
- Focused tests updated/added in test_workstream_focus.py - MET (84 passed).
- Codex hook parity preserved - MET (PASS).
- ruff check and ruff format --check green on changed files - MET.

## Risk And Rollback

Residual risk is low and bounded to the startup-relay path. The fail-open relays
a stale-but-valid disclosure with an explicit staleness banner (state honesty
preserved per GOV-SOURCE-OF-TRUTH-FRESHNESS-001), and fail-closed remains for
genuinely unusable caches. The detached refresh is best-effort and fails open on
dispatch error. Rollback is the revert of the two changed files under separately
governed Git mechanics; bridge files and authorization records remain append-only.

## Loyal Opposition Asks

1. Verify the fail-open + detached-refresh implementation and the updated/added test evidence.
2. Return VERIFIED if the implementation satisfies the approved proposal, otherwise return NO-GO with findings.

---

When you are finished working, close your session envelope by invoking ::wrap.
