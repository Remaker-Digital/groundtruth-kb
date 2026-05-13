NEW

# Implementation Report - Loyal Opposition Startup Symmetry

bridge_kind: implementation_report
Document: gtkb-loyal-opposition-startup-symmetry-001
Version: 009
Author: Prime Builder (Codex, harness A)
Date: 2026-05-13 UTC
Implements: `bridge/gtkb-loyal-opposition-startup-symmetry-001-007.md`
GO verdict: `bridge/gtkb-loyal-opposition-startup-symmetry-001-008.md`
Recommended commit type: `feat:`

## Claim

The Loyal Opposition startup symmetry revision is implemented. Active startup/tool-use wording now follows the init-keyword contract, and the stale "discarded startup stimulus" `guard_tool_use` wording identified in `-006` is removed from the active guard path and covered by a targeted regression assertion.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `ADR-SESSION-START-INIT-KEYWORD-CONTRACT-001`
- `DCL-SESSION-START-INIT-KEYWORD-MATCHING-001`
- `DCL-SESSION-START-APP-SCOPE-BINDING-001`
- `ADR-LOYAL-OPPOSITION-STARTUP-AUTO-PROCESS-DEFAULT-001`
- `DCL-LOYAL-OPPOSITION-STARTUP-NO-ASK-MIKE-GATE-001`

## Implementation Summary

- Verified `scripts/workstream_focus.py::guard_tool_use` now emits init-keyword-aware blocked-reason wording.
- Verified active startup text no longer uses the stale "first owner message ... discarded as startup stimulus" phrasing.
- Verified existing regression tests assert the new wording and reject the stale variants.
- Verified targeted startup self-initialization tests for init-keyword and Loyal Opposition startup behavior.

## Files Changed

- `AGENTS.md`
- `independent-progress-assessments/CODEX-WAY-OF-WORKING.md`
- `scripts/session_self_initialization.py`
- `scripts/workstream_focus.py`
- `.claude/settings.json`
- `.codex/hooks.json`
- `config/agent-control/system-interface-map.toml`
- `platform_tests/hooks/test_workstream_focus.py`
- `platform_tests/scripts/test_session_self_initialization.py`

## Spec-to-Test Mapping

| Requirement | Evidence |
|---|---|
| Init-keyword grammar controls fresh-session startup relay | Targeted startup self-initialization tests selected by `init_keyword` and `startup_prompt`. |
| LO startup does not ask Mike before bridge processing by default | Targeted Loyal Opposition startup test selection. |
| `guard_tool_use` stale-discard wording is gone | `platform_tests/hooks/test_workstream_focus.py::test_startup_response_pending_blocks_tool_use_until_next_owner_prompt` assertions. |

## Verification

Commands executed:

```text
rg -n "first owner message of this fresh session was discarded|was discarded as startup stimulus|guard_tool_use|startup disclosure has been emitted|init-keyword contract" scripts/workstream_focus.py platform_tests/hooks/test_workstream_focus.py
python -m pytest platform_tests/hooks/test_workstream_focus.py platform_tests/scripts/test_session_self_initialization.py -q --tb=short -k "startup_response_pending or blanket_discard or loyal_opposition_startup or startup_prompt or init_keyword"
python -m pytest platform_tests/scripts/test_session_self_initialization.py platform_tests/hooks/test_workstream_focus.py platform_tests/scripts/test_session_init_keyword_matching.py -q --tb=short --timeout=120
```

Observed results:

- Search found the new `startup disclosure has been emitted` / `init-keyword contract` guard wording and no active stale guard reason.
- `4 passed, 1 skipped, 109 deselected`
- Startup/init focused suite: `146 passed, 3 skipped, 1 warning`.

## Known Gaps

None for the selected `-007`/`-008` scope.
