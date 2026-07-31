NEW

# WI-4982 Init-Keyword Grammar Reconciliation

bridge_kind: prime_proposal
Document: gtkb-wi4982-init-keyword-grammar-reconciliation
Version: 001
Author: Prime Builder (Codex)
Date: 2026-07-07T16:57:00Z

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f3170-d706-77d3-b3e1-be39d47f3eda
author_model: GPT-5 Codex
author_model_version: gpt-5
author_model_configuration: interactive Prime Builder session; default Codex desktop execution

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-WI4982-INIT-KEYWORD-GRAMMAR-20260707
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-4982

target_paths: ["scripts/_session_init_keyword.py", "scripts/workstream_focus.py", "scripts/session_start_dispatch_core.py", ".claude/hooks/session_start_dispatch.py", ".codex/gtkb-hooks/session_start_dispatch.py", "scripts/check_codex_hook_parity.py", "platform_tests/scripts/test_session_init_keyword_matching.py", "platform_tests/scripts/test_canonical_init_keyword_syntax.py", "platform_tests/scripts/test_check_codex_hook_parity_resolution_table.py", "platform_tests/scripts/test_claude_session_start_dispatcher.py", "platform_tests/scripts/test_codex_session_start_dispatcher.py", "platform_tests/hooks/test_workstream_focus.py", "platform_tests/hooks/test_workstream_focus_session_role_marker.py", "platform_tests/scripts/test_session_role_resolution.py", "platform_tests/scripts/test_session_role_resolution_table.py"]

implementation_scope: source/test/hook_configuration/governance_evidence
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

WI-4982 addresses residual init-keyword grammar drift after the canonical init-keyword program. The original backlog row described a split between the legacy owner-facing matcher in `scripts/_session_init_keyword.py` and the stricter `::init gtkb pb|lo` receiver matcher in `scripts/workstream_focus.py`. Fresh MemBase reads show the current governing requirement has moved again: `SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001` v3 now defines canonical syntax as `^::init (gtkb|application)( (pb|lo))?$`, with mandatory subject token `{gtkb, application}` and optional role token `{pb, lo}`.

Current implementation and tests still pin older behavior in several places:

- `scripts/_session_init_keyword.py` accepts legacy phrases such as `init gtkb`, `GT-KB startup`, and `start agent_red` as if they were canonical init keywords.
- `scripts/workstream_focus.py` checks the legacy matcher first, then separately checks a strict `::init gtkb pb|lo` regex.
- `scripts/session_start_dispatch_core.py` and wrapper tests still use `_CANONICAL_KEYWORD_RE = re.compile(r"^::init gtkb (pb|lo)$")`.
- Focused tests currently pass while preserving the stale contract; for example, the focused baseline command below passed 114 tests but also proved the v3 subject-only and `application` forms are not accepted by the core receiver regex.

Read-only evidence gathered before proposal filing:

```text
python -m pytest platform_tests/scripts/test_canonical_init_keyword_syntax.py platform_tests/scripts/test_session_init_keyword_matching.py -q --tb=short
```

Observed result: `114 passed in 2.39s`.

Read-only receiver check:

```text
::init gtkb pb -> True
::init gtkb -> False
::init application pb -> False
::init application -> False
```

This proposal therefore scopes WI-4982 as a reconciliation with current v3 authority, not merely a cleanup of the older v2 wording in the backlog row.

Expected implementation shape:

- Create or revise one shared parser/normalizer surface that represents the v3 canonical init-keyword grammar and returns structured subject plus optional role information.
- Treat old owner-facing startup phrases as explicit compatibility aliases, not as the canonical grammar. Compatibility aliases may remain for startup disclosure relay only where still governed by `DCL-INIT-KEYWORD-STARTUP-DISCLOSURE-RELAY-001`; they must not be confused with machine-emitted canonical dispatch syntax.
- Update `workstream_focus` to consume the shared parser/normalizer instead of trying the legacy matcher first and then a separate canonical regex.
- Update `session_start_dispatch_core` and both thin wrappers through the shared core so Claude and Codex receiver behavior stays identical.
- Implement the v3 decision split: canonical keywords with role tokens establish or check role where applicable; canonical keywords without role tokens preserve durable/resolver fallback behavior and must not write `.claude/session/active-session-role.json` merely because a subject was declared.
- Preserve backwards compatibility for existing dispatcher emissions of `::init gtkb pb` and `::init gtkb lo`.
- Update parity, receiver, workstream-focus, and session-role tests so they pin the v3 grammar, subject-only forms, `application` subject, role-token optionality, and compatibility-alias boundaries.

This proposal does not authorize formal GOV/ADR/DCL/SPEC mutation, production deployment, credential lifecycle work, destructive cleanup, force-push, direct harness-to-harness invocation, or broad backlog/project mutation.

## Specification Links

- `SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001` v3 - canonical syntax is `^::init (gtkb|application)( (pb|lo))?$`; subject token is mandatory; role token is optional; no synonyms in canonical grammar.
- `DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001` v3 - receiver behavior forks by dispatch context and role-token presence; subject-only canonical keywords use durable/resolver fallback instead of writing active-session-role markers.
- `DCL-INIT-KEYWORD-STARTUP-DISCLOSURE-RELAY-001` - owner-facing startup disclosure relay must remain visible and cache-isolated when an accepted init-keyword path is used.
- `DCL-SESSION-ROLE-RESOLUTION-001` v5 - session role resolution must distinguish headless dispatch, explicit interactive role, subject-only declaration, per-session marker, transcript persistence, and resolver fallback.
- `GOV-SESSION-ROLE-AUTHORITY-001` v4 - durable harness registry is dispatcher-authoritative only; non-dispatcher surfaces consume session-role evidence or resolver output, not fresh registry authority.
- `ADR-INTERACTIVE-SESSION-ROLE-OVERRIDE-001` v2 - interactive transcript role authority is separate from durable harness role assignment and persists across compaction/resume boundaries.
- `DCL-INTERACTIVE-SESSION-ROLE-PERSISTENCE-001` - transcript-defined role must persist and must not mutate durable registry assignment.
- `DCL-CROSS-HARNESS-ENFORCEMENT-001` - receiver behavior and bridge compliance must remain symmetric across Claude and Codex paths.
- `ADR-CROSS-HARNESS-PARITY-001` - harness-observable capabilities must have behavior/intent parity across applicable active harnesses or an owner-approved typed waiver.
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` - proposals touching harness-surface files must include a `## Cross-Harness Disposition` section declaring parity or typed waiver per applicable harness.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - the `application` subject and Agent Red separateness boundary must resolve through in-root application/work-subject state, not hardcoded off-root or adopter-repository paths.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - protected source, hook, and test changes require proposal review, latest `GO`, implementation-start authorization, implementation report, and verification.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - the cited PAUTH bounds WI-4982 owner approval but does not bypass bridge review.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - PAUTH is owner-approval evidence only and does not broaden target paths or skip GO/report/verification.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - this proposal carries project authorization, project, and work-item metadata.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal cites the governing requirements before implementation.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the implementation report must map each linked requirement to executed tests.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` - state claims in this proposal derive from fresh CLI/spec reads and live source/test inspection rather than cached startup reports.
- `GOV-STANDING-BACKLOG-001` - WI-4982 remains the MemBase backlog authority and must reach terminal state through bridge/report/verification evidence.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - preserve traceability across owner decision, PAUTH, proposal, implementation, tests, and terminal disposition.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - durable owner approval, scope, and verification evidence are required for this lifecycle step.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - contradictory or stale backlog wording is a trigger for explicit artifact disposition, not silent source mutation.

## Prior Deliberations

- `DELIB-20260707-WI4982-IMPLEMENTATION-APPROVAL` - owner authorized WI-4982 for governed implementation proposal filing.
- `DELIB-20260648` - envelope init-keyword optionality clarification; source for `SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001` v3 and `DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001` v3.
- `DELIB-20260702-ROLE-AUTHORITY-SCOPED-APPROVAL-A` - owner approved the scoped role-authority boundary correction program cited by current role-authority specs.
- `DELIB-20265878` - owner correction that the registry role is dispatcher-authoritative only and non-dispatcher enforcement gates must not use registry role as authority.
- `DELIB-20265226` - owner directive that transcript-defined interactive role persists across compaction, resume, and contiguous SessionStart-like boundaries.
- `bridge/gtkb-canonical-init-keyword-syntax-001-012.md` - VERIFIED the prior canonical init-keyword implementation/report chain. This WI-4982 proposal is a residual drift repair against newer v3 requirements and remaining implementation/test surfaces.
- `bridge/gtkb-role-authority-interactive-persistence-004.md` - Loyal Opposition GO for interactive role persistence narrative/formal artifact alignment.
- WI-4982 backlog row - identifies the original divergent-matcher defect and owner-gated status before this authorization.

## Owner Decisions / Input

Owner approval is recorded by `DELIB-20260707-WI4982-IMPLEMENTATION-APPROVAL`.

Bounded implementation authorization is recorded as `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-WI4982-INIT-KEYWORD-GRAMMAR-20260707`.

The PAUTH includes WI-4982 only and forbids credential lifecycle, deployment, force-push, secret disclosure, destructive bulk cleanup, stash drop, branch/worktree prune, untracked-file deletion, broad bulk status mutation, direct harness-to-harness invocation, and committing unrelated dirty files.

## Bulk Operation Guard

This is not a bulk backlog mutation, bulk role migration, broad harness rewrite, or formal-artifact update. It is a single-WI implementation proposal for WI-4982 with enumerated target paths, item-specific owner approval evidence (`DELIB-20260707-WI4982-IMPLEMENTATION-APPROVAL`), and item-specific PAUTH (`PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-WI4982-INIT-KEYWORD-GRAMMAR-20260707`).

No formal-artifact-approval packet is required because this proposal does not create, promote, retire, or mutate GOV/ADR/DCL/SPEC records. If implementation discovers that a formal artifact mutation is required, implementation must stop and return through the applicable formal-artifact approval path before mutating that artifact.

## Cross-Harness Disposition

This proposal touches harness-surface files (`.claude/hooks/session_start_dispatch.py` and `.codex/gtkb-hooks/session_start_dispatch.py`) and therefore declares the required parity disposition under `ADR-CROSS-HARNESS-PARITY-001` and `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001`.

Per applicable harness:

- Claude Code: behavioral parity required. The Claude SessionStart wrapper must continue delegating to `scripts/session_start_dispatch_core.py`, and tests must prove the v3 parser/receiver decisions exposed by the Claude wrapper match the shared core contract.
- Codex: behavioral parity required. The Codex SessionStart wrapper must continue delegating to `scripts/session_start_dispatch_core.py`, and tests must prove the v3 parser/receiver decisions exposed by the Codex wrapper match the shared core contract.
- Claude/Codex parity assertion: no typed waiver is requested. Any intentional divergence between these wrappers is out of scope for WI-4982 and must stop implementation for a separate owner-approved waiver or proposal.
- Cursor, Antigravity, Ollama, OpenRouter: no harness-surface file for these harnesses is in the listed target paths. If implementation discovers an active startup-dispatch/init-keyword surface for any of these harnesses that must change for behavioral parity, implementation must stop and return through a revised proposal or owner-approved typed waiver before mutating those surfaces.

## Requirement Sufficiency

Existing requirements sufficient.

`SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001` v3, `DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001` v3, `DCL-SESSION-ROLE-RESOLUTION-001` v5, `GOV-SESSION-ROLE-AUTHORITY-001` v4, and WI-4982's backlog record define enough behavior for the source/test/hook reconciliation. No new or revised GOV/ADR/DCL/SPEC mutation is proposed.

The backlog row's older shorthand (`^::init gtkb (pb|lo)$`) is superseded by current MemBase spec v3 for implementation scope. The row remains useful as the defect pointer: divergent matchers and stale tests still exist.

## Spec-Derived Verification Plan

| Governing surface | Required implementation behavior | Verification |
| --- | --- | --- |
| `SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001` v3 | A single canonical parser accepts exactly the six v3 canonical forms: `::init gtkb`, `::init gtkb pb`, `::init gtkb lo`, `::init application`, `::init application pb`, `::init application lo`; it rejects synonyms, case variants, malformed whitespace, wrong subjects, and extra content. | Update `platform_tests/scripts/test_canonical_init_keyword_syntax.py` and receiver wrapper tests to assert valid/invalid v3 forms and exact cross-harness parity. |
| `DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001` v3 | Receiver behavior distinguishes headless vs interactive context and role-token-present vs role-token-absent rows, including subject-only fallback behavior. | Extend `platform_tests/scripts/test_claude_session_start_dispatcher.py`, `platform_tests/scripts/test_codex_session_start_dispatcher.py`, and `platform_tests/scripts/test_check_codex_hook_parity_resolution_table.py`. |
| `DCL-SESSION-ROLE-RESOLUTION-001` v5 and `GOV-SESSION-ROLE-AUTHORITY-001` v4 | Subject-only declarations do not silently become behavior authority; role-token declarations establish transcript/session role where allowed; registry reads remain dispatcher/resolver-scoped. | Extend `platform_tests/scripts/test_session_role_resolution.py`, `platform_tests/scripts/test_session_role_resolution_table.py`, and `platform_tests/hooks/test_workstream_focus_session_role_marker.py`. |
| `DCL-INIT-KEYWORD-STARTUP-DISCLOSURE-RELAY-001` | Owner-facing compatibility aliases that remain supported still render visible startup disclosure and do not collide with dispatch cache state. | Extend `platform_tests/hooks/test_workstream_focus.py` and `platform_tests/scripts/test_session_init_keyword_matching.py` to separate compatibility aliases from canonical grammar. |
| `DCL-CROSS-HARNESS-ENFORCEMENT-001` | Claude and Codex wrappers consume the same shared core and expose identical parser/receiver behavior except for declared harness identity/output paths. | Keep wrapper tests and `scripts/check_codex_hook_parity.py` parity checks passing. |
| `ADR-CROSS-HARNESS-PARITY-001` and `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` | Harness-surface changes declare per-harness parity and require no waiver for Claude/Codex. | Add or update tests proving Claude and Codex wrapper behavior remains equivalent through the shared core; implementation report cites this `## Cross-Harness Disposition`. |
| `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` | No protected implementation occurs until latest GO and implementation-start packet. | Implementation report must cite `python scripts/implementation_authorization.py begin --bridge-id gtkb-wi4982-init-keyword-grammar-reconciliation`. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Each linked behavioral requirement has executed tests. | Post-implementation report must include exact pytest commands and separate `ruff check` plus `ruff format --check` results for changed Python files. |

Minimum expected verification commands after implementation:

```text
python -m pytest platform_tests/scripts/test_canonical_init_keyword_syntax.py platform_tests/scripts/test_session_init_keyword_matching.py -q --tb=short
python -m pytest platform_tests/scripts/test_claude_session_start_dispatcher.py platform_tests/scripts/test_codex_session_start_dispatcher.py platform_tests/scripts/test_check_codex_hook_parity_resolution_table.py -q --tb=short
python -m pytest platform_tests/hooks/test_workstream_focus.py platform_tests/hooks/test_workstream_focus_session_role_marker.py -q --tb=short
python -m pytest platform_tests/scripts/test_session_role_resolution.py platform_tests/scripts/test_session_role_resolution_table.py -q --tb=short
python -m ruff check scripts/_session_init_keyword.py scripts/workstream_focus.py scripts/session_start_dispatch_core.py scripts/check_codex_hook_parity.py platform_tests/scripts/test_session_init_keyword_matching.py platform_tests/scripts/test_canonical_init_keyword_syntax.py platform_tests/scripts/test_check_codex_hook_parity_resolution_table.py platform_tests/scripts/test_claude_session_start_dispatcher.py platform_tests/scripts/test_codex_session_start_dispatcher.py platform_tests/hooks/test_workstream_focus.py platform_tests/hooks/test_workstream_focus_session_role_marker.py platform_tests/scripts/test_session_role_resolution.py platform_tests/scripts/test_session_role_resolution_table.py
python -m ruff format --check scripts/_session_init_keyword.py scripts/workstream_focus.py scripts/session_start_dispatch_core.py scripts/check_codex_hook_parity.py platform_tests/scripts/test_session_init_keyword_matching.py platform_tests/scripts/test_canonical_init_keyword_syntax.py platform_tests/scripts/test_check_codex_hook_parity_resolution_table.py platform_tests/scripts/test_claude_session_start_dispatcher.py platform_tests/scripts/test_codex_session_start_dispatcher.py platform_tests/hooks/test_workstream_focus.py platform_tests/hooks/test_workstream_focus_session_role_marker.py platform_tests/scripts/test_session_role_resolution.py platform_tests/scripts/test_session_role_resolution_table.py
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi4982-init-keyword-grammar-reconciliation --json
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi4982-init-keyword-grammar-reconciliation
```

If implementation proves some listed test file is unaffected, the implementation report may narrow the ruff command to changed Python files but must explain the narrowed changed-file set.

## Pre-Filing Self-Check

Draft preflight evidence before filing:

- `python scripts/bridge_applicability_preflight.py --content-file .gtkb-state/bridge-propose-drafts/gtkb-wi4982-init-keyword-grammar-reconciliation-001.md --json` -> `preflight_passed: true`, `missing_required_specs: []`, `missing_advisory_specs: []`.
- `python scripts/adr_dcl_clause_preflight.py --content-file .gtkb-state/bridge-propose-drafts/gtkb-wi4982-init-keyword-grammar-reconciliation-001.md` -> exit 0, `Blocking gaps (gate-failing): 0`.

## Risk / Rollback

Primary risk is breaking owner-facing startup relay by over-tightening compatibility phrases. Keep compatibility aliases explicit and tested separately from canonical grammar.

Second risk is weakening headless dispatch safety by accepting subject-only or mismatched-role dispatches without the v3 decision split. Tests must cover role-token-present mismatch and subject-only fallback separately.

Third risk is treating `application` as `agent_red` hardcoding. The v3 spec says `application` resolves through the active application/work-subject state, not a hardcoded keyword; implementation must preserve the Agent Red separateness boundary.

Rollback is a scoped revert of the source/test/hook changes from the implementation commit. Bridge files, PAUTH, and owner decision records remain append-only audit evidence.

## Bridge Filing

This proposal is filed as the first implementation proposal for `gtkb-wi4982-init-keyword-grammar-reconciliation`. Dispatcher/TAFE state plus the numbered bridge file chain are the live workflow state; no aggregate queue artifact is created or updated.

## Recommended Commit Type

fix: repairs stale init-keyword parsing and tests so the implementation matches the current canonical session-envelope contract.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
