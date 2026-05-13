NEW

# Implementation Report - SessionStart Formalization

bridge_kind: implementation_report
Document: gtkb-session-start-formalization-001
Version: 007
Author: Prime Builder (Codex, harness A)
Date: 2026-05-13 UTC
Implements: `bridge/gtkb-session-start-formalization-001-005.md`
GO verdict: `bridge/gtkb-session-start-formalization-001-006.md`
Recommended commit type: `feat:`

## Claim

SessionStart formalization is implemented for the approved revised scope. Startup disclosure relay is gated by the canonical init-keyword matcher, non-matching first prompts pass through as ordinary task input, app-scope init phrases write schema-valid workstream subjects, and bridge auto-dispatch context remains protected from unconditional startup relay.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `GOV-ARTIFACT-APPROVAL-001`
- `GOV-CHAT-DERIVED-SPEC-APPROVAL-001`
- `ADR-SESSION-START-INIT-KEYWORD-CONTRACT-001`
- `DCL-SESSION-START-INIT-KEYWORD-MATCHING-001`
- `DCL-SESSION-START-APP-SCOPE-BINDING-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `.claude/rules/file-bridge-protocol.md`
- `.claude/rules/codex-review-gate.md`

## Prior Deliberations

- `DELIB-1536` - prior Loyal Opposition NO-GO for this SessionStart formalization thread.
- `DELIB-1515` - canonical init-keyword syntax review context.
- `DELIB-1079` - SessionStart acceptance-check context.
- `DELIB-1076` - earlier startup and session-focus implementation context.
- `DELIB-1529`, `DELIB-1530`, and `DELIB-1531` - related startup-symmetry review context.
- `bridge/gtkb-session-start-formalization-001-002.md`, `-004.md`, and `-006.md` - prior bridge review chain constraining the implementation.

## Owner Decisions / Input

This implementation follows the owner directive carried in the proposal chain: formalize session start around explicit owner init phrases such as `init session`, `initialize session`, and `start gtkb session`, including app-scope phrases such as `init gtkb` and `init agent_red`.

## Implementation Summary

- Added/shared the init-keyword matcher in `scripts/_session_init_keyword.py` and wired startup prompt handling through that canonical grammar.
- Updated `scripts/workstream_focus.py` so init matches relay cached startup disclosure context, non-matches clear the gate without startup injection, and app-scoped matches write `current_subject = "gtkb_infrastructure"` or `current_subject = "application"`.
- Preserved `_bridge_auto_dispatch_context` for dispatch prompts while removing unconditional first-message startup-relay wording from active startup surfaces.
- Updated `scripts/session_self_initialization.py` and `AGENTS.md` to describe init-keyword routing rather than blanket first-message discard.
- Added and aligned regression coverage for positive init phrases, bare-verb negatives, dispatch prompt negatives, app-scope binding, startup payload wording, and guard-tool-use wording.

## Files Changed

- `AGENTS.md`
- `scripts/_session_init_keyword.py`
- `scripts/workstream_focus.py`
- `scripts/session_self_initialization.py`
- `platform_tests/scripts/test_session_init_keyword_matching.py`
- `platform_tests/hooks/test_workstream_focus.py`
- `platform_tests/scripts/test_session_self_initialization.py`

## Spec-to-Test Mapping

| Proposal Test | Evidence |
|---|---|
| `test_match_start_gtkb_session` | `platform_tests/scripts/test_session_init_keyword_matching.py` positive grammar cases. |
| `test_bare_verbs_do_not_match` | `platform_tests/scripts/test_session_init_keyword_matching.py` negative bare-verb cases. |
| `test_dispatch_prompt_does_not_match` | `platform_tests/scripts/test_session_init_keyword_matching.py` dispatch-prompt negative case. |
| `test_gate_non_match_returns_no_context` | `platform_tests/hooks/test_workstream_focus.py` non-init first-prompt pass-through coverage. |
| `test_gate_match_relays_disclosure` | `platform_tests/hooks/test_workstream_focus.py` init-keyword relay coverage. |
| `test_gate_app_scope_sets_internal_subject_application` | `platform_tests/hooks/test_workstream_focus.py` app-scope binding to `application`. |
| `test_gate_gtkb_scope_sets_internal_subject` | `platform_tests/hooks/test_workstream_focus.py` GT-KB binding to `gtkb_infrastructure`. |
| `test_sessionstart_plus_dispatch_prompt_without_marker_processes_bridge_task` | `platform_tests/scripts/test_session_self_initialization.py` dispatch-safety regression. |
| `test_startup_payload_has_no_blanket_discard_rule` | `platform_tests/scripts/test_session_self_initialization.py` startup-context wording regression. |

## Verification

Commands executed:

```text
rg -n "first owner message in a fresh session is a session-start stimulus only|first owner message of this fresh session was discarded|was discarded as startup stimulus|ask Mike whether to begin processing bridge reviews|ask Mike whether to begin processing reviews and verifications" AGENTS.md scripts/workstream_focus.py scripts/session_self_initialization.py
python -m pytest platform_tests/scripts/test_session_self_initialization.py platform_tests/hooks/test_workstream_focus.py platform_tests/scripts/test_session_init_keyword_matching.py -q --tb=short --timeout=120
python -m ruff check scripts/implementation_authorization.py scripts/implementation_start_gate.py scripts/workstream_focus.py scripts/session_self_initialization.py platform_tests/scripts/test_implementation_start_gate.py platform_tests/scripts/test_hook_registration_parity.py platform_tests/scripts/test_session_self_initialization.py platform_tests/hooks/test_workstream_focus.py groundtruth-kb/src/groundtruth_kb/cli.py groundtruth-kb/tests/test_project_artifacts.py .claude/hooks/implementation-start-gate.py
python -m ruff format --check scripts/implementation_authorization.py scripts/implementation_start_gate.py scripts/workstream_focus.py scripts/session_self_initialization.py platform_tests/scripts/test_implementation_start_gate.py platform_tests/scripts/test_hook_registration_parity.py platform_tests/scripts/test_session_self_initialization.py platform_tests/hooks/test_workstream_focus.py groundtruth-kb/src/groundtruth_kb/cli.py groundtruth-kb/tests/test_project_artifacts.py .claude/hooks/implementation-start-gate.py
```

Observed results:

- Stale startup wording search returned no matches.
- Startup/init focused suite: `146 passed, 3 skipped, 1 warning`.
- Targeted ruff check: `All checks passed!`
- Targeted ruff format check: `11 files already formatted`.

## Known Gaps

No known functional gap in the selected SessionStart formalization scope. The startup-focused pytest suite requires an increased per-test timeout because an existing dashboard time-series KPI test takes longer than the default 30-second pytest-timeout limit in this dirty worktree.
