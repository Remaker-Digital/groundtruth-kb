NEW

# Corrective Implementation Report - SessionStart Formalization

bridge_kind: implementation_report
Document: gtkb-session-start-formalization-001
Version: 011
Author: Prime Builder (Codex, harness A)
Date: 2026-05-13 UTC
Implements: `bridge/gtkb-session-start-formalization-001-009.md`
GO verdict: `bridge/gtkb-session-start-formalization-001-010.md`
Recommended commit type: `fix:`

## Claim

The corrective SessionStart formalization scope approved at `-010` is
implemented. SessionStart now carries cache-only startup disclosure context,
not unconditional first-answer relay directives; the UserPromptSubmit
init-keyword path remains the only startup disclosure relay path; and a
dispatcher/no-marker regression proves a bridge dispatch prompt remains
ordinary task input when it does not match the init grammar.

## Implementation Authorization

Prime Builder ran the required implementation-start gate before source/test
edits:

```text
python scripts/implementation_authorization.py begin --bridge-id gtkb-session-start-formalization-001
```

Observed result: authorization packet created for latest `GO` file
`bridge/gtkb-session-start-formalization-001-010.md`, proposal file
`bridge/gtkb-session-start-formalization-001-009.md`, requirement sufficiency
`sufficient`, target paths
`scripts/session_self_initialization.py`,
`platform_tests/scripts/test_session_self_initialization.py`, and
`platform_tests/hooks/test_workstream_focus.py`.

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
- `.claude/rules/bridge-essential.md`

## Prior Deliberations

- `DELIB-1536` - prior SessionStart formalization NO-GO context.
- `DELIB-1515` - canonical init-keyword syntax review context.
- `DELIB-1079` and `DELIB-1076` - earlier startup acceptance and
  session-focus implementation context.
- `DELIB-1529`, `DELIB-1530`, and `DELIB-1531` - related startup-symmetry
  review context.
- `bridge/gtkb-session-start-formalization-001-008.md` - verification NO-GO
  closed by this corrective report.

## Owner Decisions / Input

No new owner decision was required. This correction stays within the approved
proposal chain and the carried owner directive that startup disclosure is
triggered by explicit init phrases such as `init session`, `initialize
session`, `start gtkb session`, `init gtkb`, and `init agent_red`.

## Files Changed

- `scripts/session_self_initialization.py`
- `platform_tests/scripts/test_session_self_initialization.py`
- `platform_tests/hooks/test_workstream_focus.py`

Baseline accounting: `platform_tests/scripts/test_session_init_keyword_matching.py`
was included in ruff verification as required by the `-010` GO verdict. It is
not part of this corrective target-path edit set.

## Implementation Summary

- Replaced active SessionStart relay instructions with cache-only,
  init-keyword-gated startup disclosure wording.
- Removed the active SessionStart directives that instructed the harness to use
  the startup disclosure as the first durable answer before an init-keyword
  match.
- Updated the startup payload regression so it asserts those unconditional
  relay phrases are absent from SessionStart `additionalContext`.
- Added
  `platform_tests/hooks/test_workstream_focus.py::test_sessionstart_plus_dispatch_prompt_without_marker_processes_bridge_task`,
  which composes an armed startup gate with a multi-line single-harness bridge
  dispatcher prompt and verifies no startup gate response or disclosure context
  is returned.

## Spec-to-Test Mapping

| Requirement | Evidence |
|---|---|
| SessionStart does not carry unconditional first-answer relay instructions | `platform_tests/scripts/test_session_self_initialization.py::test_emit_startup_service_payload_returns_full_codex_session_start_contract` asserts the cache-only wording is present and the unconditional relay/durability phrases are absent. |
| Dispatch prompt without marker remains ordinary task input | `platform_tests/hooks/test_workstream_focus.py::test_sessionstart_plus_dispatch_prompt_without_marker_processes_bridge_task` asserts no startup gate response, no `hookSpecificOutput`, no `additionalContext`, and no-match pass-through guard state. |
| Init grammar and app-scope bindings remain green | `platform_tests/scripts/test_session_init_keyword_matching.py` plus sampled startup-gate tests remained passing. |
| All touched files are lint-clean and formatted | Targeted ruff check and ruff format-check passed over the touched startup/init files plus the required init-keyword matcher verification file. |

## Verification

Commands executed:

```text
rg -n "relay the generated startup message verbatim as the first durable assistant answer|The first durable assistant answer should be the startup disclosure itself|Codex Desktop durability rule|first durable assistant answer|not in transient progress/intermediary output" scripts/session_self_initialization.py platform_tests/scripts/test_session_self_initialization.py
rg -n "test_sessionstart_plus_dispatch_prompt_without_marker_processes_bridge_task|Only an init-keyword match relays startup disclosure|User-visible startup content below was generated programmatically by the startup service and cached" scripts/session_self_initialization.py platform_tests/scripts/test_session_self_initialization.py platform_tests/hooks/test_workstream_focus.py
python -m pytest platform_tests/scripts/test_session_self_initialization.py::test_emit_startup_service_payload_returns_full_codex_session_start_contract platform_tests/hooks/test_workstream_focus.py::test_sessionstart_plus_dispatch_prompt_without_marker_processes_bridge_task platform_tests/scripts/test_session_init_keyword_matching.py platform_tests/hooks/test_workstream_focus.py::test_hook_payload_accepts_claude_prompt_field_for_startup_gate platform_tests/hooks/test_workstream_focus.py::test_startup_gate_no_match_passes_prompt_through -q --tb=short
python -m ruff check scripts/session_self_initialization.py platform_tests/scripts/test_session_self_initialization.py platform_tests/hooks/test_workstream_focus.py platform_tests/scripts/test_session_init_keyword_matching.py
python -m ruff format --check scripts/session_self_initialization.py platform_tests/scripts/test_session_self_initialization.py platform_tests/hooks/test_workstream_focus.py platform_tests/scripts/test_session_init_keyword_matching.py
```

Observed results:

- The stale active relay wording is absent from
  `scripts/session_self_initialization.py`. The only remaining occurrences in
  `platform_tests/scripts/test_session_self_initialization.py` are negative
  assertions requiring absence from generated context.
- The dispatch/no-marker regression exists in
  `platform_tests/hooks/test_workstream_focus.py`.
- Targeted pytest: `39 passed, 1 warning`.
- Ruff check: `All checks passed!`
- Ruff format check: `4 files already formatted`.

## Risk And Rollback

Risk: cache-only SessionStart wording could make startup disclosure depend on a
working UserPromptSubmit init-keyword hook. Mitigation: the init-keyword gate
continues to inject cached startup disclosure, and this corrective verification
keeps the init matcher and startup-gate tests green.

Rollback: revert only the wording and test changes in the three corrective
target files, then file a superseding bridge revision. Do not delete prior
bridge files.
