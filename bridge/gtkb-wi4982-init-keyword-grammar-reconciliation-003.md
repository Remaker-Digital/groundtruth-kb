NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f3170-d706-77d3-b3e1-be39d47f3eda
author_model: GPT-5 Codex
author_model_version: gpt-5
author_model_configuration: Codex desktop interactive Prime Builder session; approval_policy=never; filesystem unrestricted; network enabled

# GT-KB Bridge Implementation Report - gtkb-wi4982-init-keyword-grammar-reconciliation - 003

bridge_kind: implementation_report
Document: gtkb-wi4982-init-keyword-grammar-reconciliation
Version: 003 (NEW; post-implementation report)
Responds to GO: bridge/gtkb-wi4982-init-keyword-grammar-reconciliation-002.md
Approved proposal: bridge/gtkb-wi4982-init-keyword-grammar-reconciliation-001.md
Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-WI4982-INIT-KEYWORD-GRAMMAR-20260707
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-4982
Recommended commit type: feat:

## Implementation Claim

WI-4982 is implemented. The strict canonical init-keyword grammar is now the v3 grammar:

`^::init (?P<subject>gtkb|application)(?: (?P<role_mode>pb|lo))?$`

The implementation separates strict machine/init parsing from owner-facing compatibility aliases:

- `scripts/_session_init_keyword.py` now exposes `CANONICAL_INIT_KEYWORD_REGEX` plus `match_canonical_init_keyword()` for exact canonical parsing, while preserving the broader compatibility alias matcher for owner-facing startup relay.
- `scripts/session_start_dispatch_core.py` and the Claude/Codex hook wrappers now consume the shared canonical parser. Role-token keywords still perform role-set checks; subject-only canonical keywords are accepted in dispatch context through resolver fallback and do not force a role marker.
- `scripts/workstream_focus.py` checks strict canonical keywords before compatibility aliases, treats `::init application` as application work-subject selection without hardcoding Agent Red, and only derives a session-role marker from canonical keywords that carry an explicit `pb` or `lo` role token.
- `scripts/check_codex_hook_parity.py` now checks for the shared canonical-regex import instead of an obsolete local literal.

No durable harness registry role assignment, application repository, production deployment, credential lifecycle, or dispatcher topology activation was changed.

## Specification Links

- `SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001` v3 - canonical syntax is `^::init (gtkb|application)( (pb|lo))?$`; subject token is mandatory; role token is optional; no synonyms in canonical grammar.
- `DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001` v3 - receiver behavior forks by dispatch context and role-token presence; subject-only canonical keywords use durable/resolver fallback instead of writing active-session-role markers.
- `DCL-INIT-KEYWORD-STARTUP-DISCLOSURE-RELAY-001` - owner-facing startup disclosure relay remains visible and cache-isolated when an accepted init-keyword path is used.
- `DCL-SESSION-ROLE-RESOLUTION-001` v5 - session role resolution distinguishes headless dispatch, explicit interactive role, subject-only declaration, per-session marker, transcript persistence, and resolver fallback.
- `GOV-SESSION-ROLE-AUTHORITY-001` v4 - durable harness registry remains dispatcher-authoritative only; non-dispatcher surfaces consume session-role evidence or resolver output.
- `ADR-INTERACTIVE-SESSION-ROLE-OVERRIDE-001` v2 and `DCL-INTERACTIVE-SESSION-ROLE-PERSISTENCE-001` - transcript-defined role authority remains separate from durable harness assignment.
- `DCL-CROSS-HARNESS-ENFORCEMENT-001`, `ADR-CROSS-HARNESS-PARITY-001`, and `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` - Claude/Codex dispatch behavior and parity checks are updated together.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - canonical `application` subject resolves to in-root work-subject state without hardcoding Agent Red.
- `GOV-FILE-BRIDGE-AUTHORITY-001`, `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`, and `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - implementation proceeded under GO plus PAUTH and still requires report/verification.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`, `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`, and `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - proposal/report lifecycle and verification mapping are preserved.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001`, `GOV-STANDING-BACKLOG-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, and `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - evidence is from live source/tests/preflights and the bridge lifecycle remains the terminal-state authority.

## Owner Decisions / Input

No new owner decision was required for WI-4982. Implementation used the owner authorization already captured in `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-WI4982-INIT-KEYWORD-GRAMMAR-20260707` and the Loyal Opposition GO at `bridge/gtkb-wi4982-init-keyword-grammar-reconciliation-002.md`.

## Prior Deliberations

- `bridge/gtkb-wi4982-init-keyword-grammar-reconciliation-001.md` - approved implementation proposal carried forward.
- `bridge/gtkb-wi4982-init-keyword-grammar-reconciliation-002.md` - Loyal Opposition GO verdict authorizing implementation.

## Specification-Derived Verification Plan

| Spec / governing surface | Executed verification evidence |
| --- | --- |
| `SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001` | `python -m pytest platform_tests/scripts/test_canonical_init_keyword_syntax.py platform_tests/scripts/test_session_init_keyword_matching.py -q --tb=short` -> 141 passed. |
| `DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001` | Canonical parser tests cover the six accepted v3 forms and malformed/synonym rejection; dispatch tests cover role-token and subject-only dispatch behavior. |
| `DCL-INIT-KEYWORD-STARTUP-DISCLOSURE-RELAY-001` | `python -m pytest platform_tests/hooks/test_workstream_focus.py platform_tests/hooks/test_workstream_focus_session_role_marker.py -q --tb=short` -> 107 passed, 3 skipped. |
| `DCL-SESSION-ROLE-RESOLUTION-001`, `GOV-SESSION-ROLE-AUTHORITY-001`, `ADR-INTERACTIVE-SESSION-ROLE-OVERRIDE-001`, `DCL-INTERACTIVE-SESSION-ROLE-PERSISTENCE-001` | `python -m pytest platform_tests/scripts/test_session_role_resolution.py platform_tests/scripts/test_session_role_resolution_table.py -q --tb=short` -> 34 passed; role-marker workstream tests prove subject-only keywords do not write session role markers. |
| Cross-harness parity/enforcement specs | `python -m pytest platform_tests/scripts/test_claude_session_start_dispatcher.py platform_tests/scripts/test_codex_session_start_dispatcher.py platform_tests/scripts/test_check_codex_hook_parity_resolution_table.py platform_tests/scripts/test_codex_hook_parity_resolution_table_drift.py -q --tb=short` -> 75 passed before formatting; focused post-format dispatcher rerun -> 40 passed. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Workstream-focus test coverage proves `::init application` selects generic application focus with `application_id is None`; legacy Agent Red alias remains separate. |
| Bridge/project authorization and spec-linkage specs | `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi4982-init-keyword-grammar-reconciliation --json` -> `preflight_passed: true`, no missing required specs. |
| ADR/DCL clause gate | `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi4982-init-keyword-grammar-reconciliation` -> 0 blocking gaps. |
| Source style/format | `python -m ruff check ...` -> all checks passed; `python -m ruff format --check ...` -> 14 files already formatted. |

## Commands Run

- `python -m pytest platform_tests/scripts/test_canonical_init_keyword_syntax.py platform_tests/scripts/test_session_init_keyword_matching.py -q --tb=short`
- `python -m pytest platform_tests/hooks/test_workstream_focus.py platform_tests/hooks/test_workstream_focus_session_role_marker.py -q --tb=short`
- `python -m pytest platform_tests/scripts/test_session_role_resolution.py platform_tests/scripts/test_session_role_resolution_table.py -q --tb=short`
- `python -m pytest platform_tests/scripts/test_claude_session_start_dispatcher.py platform_tests/scripts/test_codex_session_start_dispatcher.py platform_tests/scripts/test_check_codex_hook_parity_resolution_table.py platform_tests/scripts/test_codex_hook_parity_resolution_table_drift.py -q --tb=short`
- `python -m pytest platform_tests/scripts/test_claude_session_start_dispatcher.py platform_tests/scripts/test_codex_session_start_dispatcher.py -q --tb=short`
- `python -m ruff check scripts/_session_init_keyword.py scripts/workstream_focus.py scripts/session_start_dispatch_core.py scripts/check_codex_hook_parity.py platform_tests/scripts/test_session_init_keyword_matching.py platform_tests/scripts/test_canonical_init_keyword_syntax.py platform_tests/scripts/test_check_codex_hook_parity_resolution_table.py platform_tests/scripts/test_claude_session_start_dispatcher.py platform_tests/scripts/test_codex_session_start_dispatcher.py platform_tests/hooks/test_workstream_focus.py platform_tests/hooks/test_workstream_focus_session_role_marker.py platform_tests/scripts/test_session_role_resolution.py platform_tests/scripts/test_session_role_resolution_table.py platform_tests/scripts/test_codex_hook_parity_resolution_table_drift.py`
- `python -m ruff format --check scripts/_session_init_keyword.py scripts/workstream_focus.py scripts/session_start_dispatch_core.py scripts/check_codex_hook_parity.py platform_tests/scripts/test_session_init_keyword_matching.py platform_tests/scripts/test_canonical_init_keyword_syntax.py platform_tests/scripts/test_check_codex_hook_parity_resolution_table.py platform_tests/scripts/test_claude_session_start_dispatcher.py platform_tests/scripts/test_codex_session_start_dispatcher.py platform_tests/hooks/test_workstream_focus.py platform_tests/hooks/test_workstream_focus_session_role_marker.py platform_tests/scripts/test_session_role_resolution.py platform_tests/scripts/test_session_role_resolution_table.py platform_tests/scripts/test_codex_hook_parity_resolution_table_drift.py`
- `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi4982-init-keyword-grammar-reconciliation --json`
- `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi4982-init-keyword-grammar-reconciliation`

## Observed Results

- Canonical init-keyword tests: 141 passed.
- Workstream focus / session marker tests: 107 passed, 3 skipped.
- Session role resolution tests: 34 passed.
- Combined dispatcher/parity tests: 75 passed.
- Post-format dispatcher focused rerun: 40 passed.
- Ruff check: all checks passed.
- Ruff format check: 14 files already formatted.
- Bridge applicability preflight: passed, no missing required specs.
- ADR/DCL clause preflight: passed, 0 blocking gaps.

## Files Changed

- `scripts/_session_init_keyword.py`
- `scripts/session_start_dispatch_core.py`
- `scripts/workstream_focus.py`
- `scripts/check_codex_hook_parity.py`
- `platform_tests/scripts/test_session_init_keyword_matching.py`
- `platform_tests/scripts/test_canonical_init_keyword_syntax.py`
- `platform_tests/scripts/test_check_codex_hook_parity_resolution_table.py`
- `platform_tests/scripts/test_codex_hook_parity_resolution_table_drift.py`
- `platform_tests/scripts/test_claude_session_start_dispatcher.py`
- `platform_tests/scripts/test_codex_session_start_dispatcher.py`
- `platform_tests/hooks/test_workstream_focus.py`
- `platform_tests/hooks/test_workstream_focus_session_role_marker.py`

## Acceptance Criteria Status

- [x] Canonical grammar reconciled to v3 and shared from one parser surface.
- [x] Subject-only canonical `::init gtkb` / `::init application` forms accepted where specified.
- [x] Subject-only canonical forms do not write active session-role markers.
- [x] `application` subject selects generic application focus without hardcoding Agent Red.
- [x] Claude and Codex dispatch hook behavior remains parity-checked through shared core.
- [x] Compatibility aliases remain owner-facing only and are not accepted by the strict canonical parser.
- [x] Implementation stayed within GO/PAUTH scope and did not mutate durable role assignment, production deployment, credentials, or dispatcher topology.

## Risk And Rollback

Residual risk is concentrated in startup/hook behavior, where small parser differences can be owner-visible at session start or dispatch receipt. The focused tests cover strict canonical parsing, compatibility alias preservation, subject-only fallback, session-role marker suppression, work-subject selection, Claude/Codex dispatch parity, and the parity drift detector.

Rollback is a focused revert of the changed WI-4982 source/test files listed above plus this report if Loyal Opposition has not yet verified it. That restores the previous role-token-only `::init gtkb (pb|lo)` canonical dispatch behavior and the prior compatibility alias handling.

## Loyal Opposition Asks

1. Verify the implementation against the linked specifications and executed command evidence.
2. Pay particular attention to the subject-only dispatch fallback and the generic `application` work-subject behavior.
3. Return VERIFIED if the report and implementation satisfy the approved proposal, otherwise return NO-GO with findings.
