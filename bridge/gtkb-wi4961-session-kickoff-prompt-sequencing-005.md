NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 2026-07-06T05-07-59Z-prime-builder-A-9179bf
author_model: GPT-5.5
author_model_version: gpt-5.5
author_model_configuration: Codex dispatcher-spawned headless; resolved_role=prime-builder; sandbox=workspace-write; approval_policy=never

# WI-4961 - Session Kickoff Prompt Sequencing Implementation Report

bridge_kind: implementation_report
Document: gtkb-wi4961-session-kickoff-prompt-sequencing
Version: 005
Responds to GO: bridge/gtkb-wi4961-session-kickoff-prompt-sequencing-004.md
Approved proposal: bridge/gtkb-wi4961-session-kickoff-prompt-sequencing-003.md
Date: 2026-07-06
Author: Prime Builder (Codex harness A)
Recommended commit type: fix:

Project Authorization: PAUTH-PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-WI4961-BATCH-B-20260705
Project: PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION
Work Item: WI-4961

## Implementation Claim

WI-4961 is implemented for the approved prompt-emitting and prompt-describing
surfaces. Current GT-KB session kickoff guidance now models three separate
messages instead of bundling the role keyword, activity keyword, and task or
handoff body:

```text
::init gtkb <role>
```

```text
::open <activity>
```

```text
<task or handoff body>
```

The implementation updates the platform root guidance, Codex restart guidance,
scaffold template, committed scaffold fixture guidance, and deterministic
handoff prompt service. Regression tests now pin the separated-message shape for
static guidance, generated scaffold output, and generated handoff prompts.

`scripts/session_self_initialization.py` and
`groundtruth-kb/src/groundtruth_kb/cli_session_handoff.py` were audited during
implementation and did not require changes for this defect. `memory/MEMORY.md`
contains historical notes, but the audit did not find a current live kickoff
instruction there requiring mutation for WI-4961.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `GOV-STANDING-BACKLOG-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001`
- `DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001`
- `DCL-SESSION-ROLE-RESOLUTION-001`
- `GOV-SESSION-ROLE-AUTHORITY-001`
- `DCL-INTERACTIVE-SESSION-ROLE-PERSISTENCE-001`
- `SPEC-HANDOFF-PROMPT-DETERMINISTIC-SERVICE-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `GOV-SOT-SINGLETON-001`

## Owner Decisions / Input

No new owner decision is required. The implementation proceeds from
`DELIB-20260705-HIGH-PRIORITY-QUEUE-CONTINUE`, the approved Batch B PAUTH, and
the Loyal Opposition GO verdict in
`bridge/gtkb-wi4961-session-kickoff-prompt-sequencing-004.md`.

The auto-dispatched Prime Builder worker context cannot ask the owner for live
input. No owner decision blocked this implementation.

## Prior Deliberations

- `DELIB-20260705-HIGH-PRIORITY-QUEUE-CONTINUE` - owner-approved Batch B continuation and PAUTH for WI-4961.
- `bridge/gtkb-wi4961-session-kickoff-prompt-sequencing-002.md` - Loyal Opposition NO-GO requiring template and fixture scope expansion.
- `bridge/gtkb-wi4961-session-kickoff-prompt-sequencing-003.md` - revised approved proposal and spec-derived verification plan.
- `bridge/gtkb-wi4961-session-kickoff-prompt-sequencing-004.md` - Loyal Opposition GO authorizing implementation.

## Specification-Derived Verification Plan

| Spec / governing surface | Executed verification evidence |
| --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001`, `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`, `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`, `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Resolved Codex role with `groundtruth-kb/.venv/Scripts/gt.exe harness roles`; confirmed latest bridge status `GO`; created implementation-start packet with `scripts/implementation_authorization.py begin --bridge-id gtkb-wi4961-session-kickoff-prompt-sequencing`; packet hash `sha256:cd4cddef319e8d714bca3c6f3edf15aa9b5e8ecc7c2a75821766dd84578d3abe`; confirmed live `go_implementation` claim for session `2026-07-06T05-07-59Z-prime-builder-A-9179bf`. |
| `SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001`, `DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001` | Focused tests assert `::init gtkb pb` and `::open ...` are independent `text` fenced messages and the body is not appended to either keyword. |
| `DCL-SESSION-ROLE-RESOLUTION-001`, `GOV-SESSION-ROLE-AUTHORITY-001`, `DCL-INTERACTIVE-SESSION-ROLE-PERSISTENCE-001` | Handoff service now derives `::init gtkb pb` or `::init gtkb lo` from the resolved role without mutating durable registry state; static guidance tells users to send role evidence as the first message and activity as the second. |
| `SPEC-HANDOFF-PROMPT-DETERMINISTIC-SERVICE-001` | `platform_tests/scripts/test_session_handoff_service.py::test_handoff_prompt_separates_init_open_and_body_messages` passed and pins deterministic handoff output fences. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | No lifecycle-independent application repository or `applications/Agent_Red/` artifact was mutated; scaffold template and fixture changes stay within the approved GT-KB platform/test paths. |
| `GOV-SOT-SINGLETON-001`, `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Root `CLAUDE.md`, Codex bootstrap guidance, scaffold template, scaffold fixtures, generated scaffold test, and handoff service now describe one compatible init/open/body sequence. |
| `GOV-STANDING-BACKLOG-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Backlog resolution command was run in `--dry-run --json` mode only; output showed `resolution_status: resolved`, `stage: resolved`, `updated: false`. Final mutation remains deferred until Loyal Opposition verification/closure. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | This report includes command evidence, observed failures, affected files, and the mapping above for Loyal Opposition verification. |

## Commands Run

```text
groundtruth-kb/.venv/Scripts/gt.exe harness roles
groundtruth-kb/.venv/Scripts/python.exe .codex/skills/bridge/helpers/scan_bridge.py --role prime-builder --compact --format json
groundtruth-kb/.venv/Scripts/gt.exe bridge dispatch status --json
groundtruth-kb/.venv/Scripts/gt.exe bridge show gtkb-wi4961-session-kickoff-prompt-sequencing --json
groundtruth-kb/.venv/Scripts/python.exe scripts/implementation_authorization.py begin --bridge-id gtkb-wi4961-session-kickoff-prompt-sequencing
groundtruth-kb/.venv/Scripts/python.exe scripts/bridge_claim_cli.py status gtkb-wi4961-session-kickoff-prompt-sequencing
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_session_handoff_service.py::test_handoff_prompt_separates_init_open_and_body_messages groundtruth-kb/tests/test_session_kickoff_prompt_templates.py groundtruth-kb/tests/test_scaffold_isolation.py::test_tp_integ_1_scaffold_emits_phase9_section1_enumeration -q --tb=short --basetemp .gtkb-state/pytest-tmp/wi4961-focused
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_session_handoff.py platform_tests/scripts/test_session_handoff_service.py platform_tests/scripts/test_session_self_initialization.py platform_tests/scripts/test_session_self_initialization_disclosure_shape.py platform_tests/scripts/test_session_startup_index.py platform_tests/scripts/test_canonical_init_keyword_syntax.py platform_tests/scripts/test_canonical_init_keyword_assertions.py -q --tb=short --basetemp .gtkb-state/pytest-tmp/wi4961-platform
groundtruth-kb/.venv/Scripts/python.exe -m pytest groundtruth-kb/tests/test_cli.py groundtruth-kb/tests/test_scaffold_isolation.py groundtruth-kb/tests/adopter/test_golden_fixture_diff_per_version.py groundtruth-kb/tests/test_session_kickoff_prompt_templates.py -q --tb=short --basetemp .gtkb-state/pytest-tmp/wi4961-scaffold
groundtruth-kb/.venv/Scripts/ruff.exe check groundtruth-kb/src/groundtruth_kb/session/handoff.py platform_tests/scripts/test_session_handoff_service.py groundtruth-kb/tests/test_scaffold_isolation.py groundtruth-kb/tests/test_session_kickoff_prompt_templates.py
groundtruth-kb/.venv/Scripts/ruff.exe format --check groundtruth-kb/src/groundtruth_kb/session/handoff.py platform_tests/scripts/test_session_handoff_service.py groundtruth-kb/tests/test_scaffold_isolation.py groundtruth-kb/tests/test_session_kickoff_prompt_templates.py
groundtruth-kb/.venv/Scripts/ruff.exe check groundtruth-kb/src/groundtruth_kb/session/handoff.py groundtruth-kb/src/groundtruth_kb/cli_session_handoff.py scripts/session_self_initialization.py platform_tests/scripts/test_session_handoff.py platform_tests/scripts/test_session_handoff_service.py platform_tests/scripts/test_session_self_initialization.py platform_tests/scripts/test_session_self_initialization_disclosure_shape.py platform_tests/scripts/test_session_startup_index.py groundtruth-kb/tests/test_cli.py groundtruth-kb/tests/test_scaffold_isolation.py groundtruth-kb/tests/adopter/test_golden_fixture_diff_per_version.py groundtruth-kb/tests/test_session_kickoff_prompt_templates.py
groundtruth-kb/.venv/Scripts/ruff.exe format --check groundtruth-kb/src/groundtruth_kb/session/handoff.py groundtruth-kb/src/groundtruth_kb/cli_session_handoff.py scripts/session_self_initialization.py platform_tests/scripts/test_session_handoff.py platform_tests/scripts/test_session_handoff_service.py platform_tests/scripts/test_session_self_initialization.py platform_tests/scripts/test_session_self_initialization_disclosure_shape.py platform_tests/scripts/test_session_startup_index.py groundtruth-kb/tests/test_cli.py groundtruth-kb/tests/test_scaffold_isolation.py groundtruth-kb/tests/adopter/test_golden_fixture_diff_per_version.py groundtruth-kb/tests/test_session_kickoff_prompt_templates.py
rg -n "Continue work on|Next: \[describe task\]|::init gtkb (pb|lo)|::open (project|build|test)|Read this handoff prompt" CLAUDE.md .claude/rules/codex-session-bootstrap.md groundtruth-kb/templates/CLAUDE.md groundtruth-kb/tests/fixtures/scaffold_golden/dual-agent/CLAUDE.md groundtruth-kb/tests/fixtures/scaffold_golden/local-only/CLAUDE.md groundtruth-kb/src/groundtruth_kb/session/handoff.py platform_tests/scripts/test_session_handoff_service.py groundtruth-kb/tests/test_scaffold_isolation.py groundtruth-kb/tests/test_session_kickoff_prompt_templates.py scripts/session_self_initialization.py memory/MEMORY.md
groundtruth-kb/.venv/Scripts/gt.exe backlog resolve WI-4961 --status-detail "Resolved by bridge VERIFIED: prompt emitters, scaffold templates, root guidance, memory guidance, and startup/handoff helpers now model separate ::init, ::open, and task/handoff messages; tests guard against bundled keyword+payload and keyword-free kickoff prompts." --related-bridge-threads '["bridge/gtkb-wi4961-session-kickoff-prompt-sequencing-003.md"]' --owner-approved --change-reason "WI-4961 bridge-verified prompt sequencing cleanup" --dry-run --json
```

## Observed Results

- Focused WI-4961 regression batch: `7 passed, 2 warnings`.
- Platform session-startup batch: `229 passed, 2 failed, 3 warnings`.
- Scaffold/template batch: `59 passed, 1 skipped, 3 failed, 2 warnings`.
- Ruff check on changed Python files: `All checks passed!`
- Ruff format check on changed Python files: `4 files already formatted`.
- Broader targeted ruff check: `All checks passed!`
- Broader targeted ruff format check: `12 files already formatted`.
- String audit found corrected live guidance in edited surfaces. Historical `memory/MEMORY.md` notes appeared in the search output but were not current live kickoff instructions.
- Backlog dry-run returned `updated: false` and showed the intended resolved fields without mutating MemBase.

## Known Unrelated Test Failures

The two broader pytest batches exposed existing drift outside the WI-4961 prompt
sequencing change:

- `platform_tests/scripts/test_session_self_initialization.py::test_startup_model_contains_role_governance_and_kpi_inventory` expected `integrations["accessibility_axe"]["status"] == "ready"` but observed `"partial"`.
- `platform_tests/scripts/test_session_self_initialization.py::test_dashboard_and_report_are_written_with_time_series_kpi` expected dashboard title `"Agent Red GT-KB Dashboard"` but observed `"GT-KB Operations Dashboard"`.
- `groundtruth-kb/tests/test_scaffold_isolation.py::test_tp14_local_only_matches_golden_fixture` reported scaffold extras including `.claude\rules\session-start-orientation.md` and `.groundtruth\formal-artifact-approvals\.gitkeep`.
- `groundtruth-kb/tests/test_scaffold_isolation.py::test_tp15_dual_agent_matches_golden_fixture` reported unrelated extra generated rule/skill/formal-approval files.
- `groundtruth-kb/tests/adopter/test_golden_fixture_diff_per_version.py::test_clean_adopter_byte_matches_golden_fixture` reported broader fixture drift including a missing `.claude/hooks/scheduler.py`, extra files, and byte-different files.

The focused WI-4961 regression tests pass, and the failing assertions are not
caused by the new prompt sequencing changes.

## Files Changed

WI-4961 implementation touched these paths:

- `CLAUDE.md`
- `.claude/rules/codex-session-bootstrap.md`
- `groundtruth-kb/templates/CLAUDE.md`
- `groundtruth-kb/tests/fixtures/scaffold_golden/dual-agent/CLAUDE.md`
- `groundtruth-kb/tests/fixtures/scaffold_golden/local-only/CLAUDE.md`
- `groundtruth-kb/src/groundtruth_kb/session/handoff.py`
- `platform_tests/scripts/test_session_handoff_service.py`
- `groundtruth-kb/tests/test_scaffold_isolation.py`
- `groundtruth-kb/tests/test_session_kickoff_prompt_templates.py`

The implementation-report helper plan observed a much larger dirty worktree
because this shared checkout already had unrelated pending changes before
WI-4961. This report is scoped to the paths above.

## Recommended Commit Type

- Recommended commit type: `fix:`
- Rationale: this repairs malformed session-kickoff prompt behavior and adds
  regression coverage for the corrected prompt sequence.

## Acceptance Criteria Status

- [x] Root `CLAUDE.md` no longer presents a keyword-free GT-KB kickoff body as
  the first session message; it shows `::init`, `::open`, and task body as
  separate messages.
- [x] Codex quick-restart guidance separates `::init gtkb pb`, `::open project`,
  and the restart body.
- [x] Scaffold template and committed scaffold fixtures emit the same separated
  startup sequence.
- [x] Deterministic handoff prompt service emits role keyword, activity keyword,
  and handoff body as separate fenced messages.
- [x] Focused tests cover static guidance, generated scaffold output, and
  generated handoff output.
- [x] Backlog resolution was dry-run only; terminal mutation remains pending
  Loyal Opposition verification.

## Risk And Rollback

Residual risk is limited to broader scaffold fixture drift already visible in
the existing test suite. The WI-4961-specific prompt sequence is covered by
focused passing tests.

Rollback is a conventional git revert of the WI-4961 paths listed above. Bridge
files remain append-only and must not be rewritten during rollback.

## Loyal Opposition Asks

1. Verify that the implementation satisfies the `-003` proposal and `-004` GO
   verdict.
2. Confirm the focused WI-4961 tests provide sufficient spec-derived evidence
   despite unrelated existing broader test drift.
3. Return `VERIFIED` if satisfied, or `NO-GO` with concrete findings.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
