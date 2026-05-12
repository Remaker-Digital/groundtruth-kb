NEW

# Implementation Report — Canonical Init-Keyword Syntax IP-4 + IP-8 (Post-Implementation)

bridge_kind: implementation_report
Document: gtkb-canonical-init-keyword-syntax-001
Version: 009
Author: Prime Builder (Claude, harness B)
Date: 2026-05-12 UTC
Authorizing Verdict: `bridge/gtkb-canonical-init-keyword-syntax-001-008.md` (GO).
Implements: `bridge/gtkb-canonical-init-keyword-syntax-001-007.md` REVISED-3 (carries forward `-005` REVISED-2 plan).

## Claim

IP-4 (StartupDecision enum + receiver-side keyword recognition with strict-ignore-on-mismatch + audit-log) and IP-8 (six test surfaces covering syntax parser, DCL assertions, governing-specs preservation, Claude-side and Codex-side receiver enum-path coverage) are implemented and passing.

IP-1, IP-2, IP-3a/b/c, and IP-7 were closed in prior commits (S343 status: MemBase rows v1, trigger DispatchTarget + consumer migration + state-key migration, glossary entry at canonical-terminology.md line 1061). This implementation report closes the remaining IP-4 and IP-8 work and additionally records one IP-4 companion change to the trigger (env-var emission so SessionStart can recognize the keyword without parsing the prompt).

Both Claude and Codex SessionStart hooks now implement byte-mirror IP-4 logic: regex `^::init gtkb (pb|lo)$`, two-step durable-role resolution (`harness-state/harness-identities.json` → `harness-state/role-assignments.json`), five-decision `StartupDecision` enum, and strict-ignore-on-mismatch with audit-log to `.gtkb-state/bridge-poller/dispatch-failures.jsonl`.

## Owner Decisions / Input

This implementation depends on prior owner approvals already cited in the authorizing -005/-007 proposals (the GO at -008 ratified them). No new owner-decision asks were required for IP-4/IP-8 implementation. The relevant prior AskUserQuestion evidence carried forward:

1. AUQ 2026-05-09 "file thread now" — owner answer "File now (Recommended)". Authorized the entire bridge thread.
2. AUQ 2026-05-09 "authority semantic" — owner answer "Consistent assertion (Recommended)". Implemented as DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001 receiver clause.
3. AUQ 2026-05-09 "strict-ignore refinement" — owner directive that the receiver hook must check durable role and ignore mismatched notifications. Implemented as the STRICT_DROP enum path.
4. AUQ 2026-05-09 "review-then-revise sequencing" — owner answer "Let Codex review -001 first (Recommended)".
5. AUQ 2026-05-09 "revise canonical-syntax -005" — owner answer "Revise canonical-syntax to -005 (Recommended)". Authorized the REVISED-2 plan that this report implements.
6. AUQ 2026-05-09 standing parity directive — "everything we do needs to be paralleled by Claude Code, for both Loyal Opposition and Prime Builder roles as applicable". Implemented as byte-mirror Codex hook + cross-harness enforcement tests.

Per the Acting-Prime KB-Write Approval-Packet pathway, no MemBase mutations were performed in this slice; IP-1 (SPEC) and IP-2 (DCL) MemBase inserts happened in prior commits with separate per-artifact approval packets (S343 status notes IP-1 at rowid 8475 and IP-2 v1).

## Prior Deliberations

- `bridge/gtkb-canonical-init-keyword-syntax-001-008.md` (GO) — authorizing verdict for this implementation.
- `bridge/gtkb-canonical-init-keyword-syntax-001-007.md` (REVISED-3) — implementation plan carried forward.
- `bridge/gtkb-canonical-init-keyword-syntax-001-005.md` (REVISED-2) — IP-4 enum specification authored here.
- `bridge/gtkb-canonical-init-keyword-syntax-001-004.md` (NO-GO) — F1/F2/F3 closed by -005.
- `bridge/gtkb-canonical-init-keyword-syntax-001-002.md` (NO-GO) — F1/F2/F3 of -001 closed by -003.
- `bridge/gtkb-bridge-poller-event-driven-replacement-slice-4-smart-poller-retirement-001` — established cross-harness event-driven trigger as canonical bridge automation; this thread's IP-4 receiver-side check operates inside that substrate.
- `bridge/gtkb-loyal-opposition-startup-symmetry-001-008.md` (GO) — established the LO startup symmetry contract that IP-4 receiver enforcement honors.
- `bridge/gtkb-single-harness-bridge-dispatcher-001-014.md` (GO) — parallel thread targeting single-harness operation in both directions (Claude OR Codex); IP-4's receiver-side check is symmetric, supporting future single-harness dispatch.
- Auto-memory `feedback_init_keyword_as_role_symmetric_activator.md` — owner principle that the init keyword unifies LO/Prime parity and auto-process default.
- Auto-memory `feedback_bridge_compliance_gate_strict_heading.md` — this report uses plain `## Specification Links` heading with flat citations to satisfy the bridge-compliance-gate hook's strict-parse semantic.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — `bridge/INDEX.md` remains canonical workflow state; this report is filed as `NEW` at the top of the thread's INDEX entry.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — implementation is governed via durable artifacts (proposal, post-impl report, tests, MemBase rows from prior commits).
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — the IP-4 implementation is delivered as artifact-anchored work (regex pinned in source, tests pinned per spec, audit log structured).
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — implementation lands behind the bridge VERIFIED lifecycle trigger; no live operation until Codex VERIFIED.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — this section enumerates all specs the implementation honors.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — the Spec-to-Test Mapping section below maps every cited spec to executed tests.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — all touched files under `E:\GT-KB`; no out-of-root paths introduced.
- `GOV-ARTIFACT-APPROVAL-001` v3 — no new SPEC/DCL/GOV/PB/ADR MemBase rows created in this slice; existing IP-1 and IP-2 rows from prior commits retain their per-artifact approval packets.
- `SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001` v1 — regex `^::init gtkb (pb|lo)$` implemented in both SessionStart hooks AND the trigger's emission (`scripts/cross_harness_bridge_trigger.py:357`, `.claude/hooks/session_start_dispatch.py`, `.codex/gtkb-hooks/session_start_dispatch.py`). Test surface 1 pins the regex literally.
- `DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001` v1 — emitter clause (two-step authority chain) implemented in trigger `_resolve_dispatch_target`; receiver clause (set-membership check + strict-ignore-on-mismatch + audit log) implemented in both hooks via `_bridge_dispatch_keyword_check` + `_audit_log_misdirected_dispatch`.
- `GOV-HARNESS-ROLE-PORTABILITY-001` v1 — preserved: T-CIK-role-portability proves swapping which harness holds which role swaps the dispatch target.
- `GOV-GTKB-MULTI-HARNESS-ROLE-CONFIG-001` v1 — preserved: T-CIK-multi-harness-config exercises both role-assignment configurations.
- `DCL-CROSS-HARNESS-ENFORCEMENT-001` v1 — preserved: T-CIK-cross-harness-enforcement proves strict-ignore applies symmetrically to Claude and Codex hooks.
- `ADR-SMART-POLLER-OWNER-OUT-OF-LOOP-001` v2 — preserved: T-CIK-actionable-only-spawn proves keyword is emitted only inside `_dispatch_prompt`.
- `DCL-SMART-POLLER-AUTO-TRIGGER-001` v2 — preserved: T-CIK-no-idle-emission proves empty INDEX produces no spawn and no keyword.
- `DCL-SPAWNED-HARNESS-ROLE-DEFER-DURABLE-RECORD-001` v2 — preserved: T-CIK-defer-to-durable proves the receiver consults its OWN durable role (not the prompt body).
- `PB-INCIDENT-S321-DAEMON-DISPATCH-DISABLED-001` v2 — preserved: T-CIK-audit-log-on-misdirect proves STRICT_DROP writes a JSONL audit record with structured fields making silent-drops investigable.
- `DCL-CONCEPT-ON-CONTACT-001` — satisfied by the IP-7 glossary entry already in place at `.claude/rules/canonical-terminology.md:1061` (load-bearing concept added on first contact).
- `.claude/rules/operating-role.md` — single source of truth for durable role is `harness-state/role-assignments.json`; the IP-4 receiver reads identity from `harness-state/harness-identities.json` and role from that file. No harness-local override (`harness-state/<harness>/operating-role.md`) used.

## Pre-Filing Preflight Evidence

Per `.claude/rules/file-bridge-protocol.md` Mandatory Pre-Filing Preflight Subsection. Both preflights run against this filed report with the INDEX entry resolving the operative file:

- Applicability preflight: `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-canonical-init-keyword-syntax-001`
  - `preflight_passed: true`
  - `missing_required_specs: []`
  - `missing_advisory_specs: []`
  - `packet_hash: sha256:e6421b8c04d9885f69a5403373202d403b0cbcf00debc0977cef0ef92ae3a6f6`
- Clause preflight: `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-canonical-init-keyword-syntax-001`
  - Clauses evaluated: 5 (4 must_apply with evidence; 1 may_apply benign).
  - Blocking gaps: 0.

## Spec-to-Test Mapping

| Spec | Test | Path | Status |
|---|---|---|---|
| SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001 (valid forms) | test_valid_forms_accepted_claude, test_valid_forms_accepted_codex | platform_tests/scripts/test_canonical_init_keyword_syntax.py | PASS |
| SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001 (invalid forms; closed vocab; strict parse) | test_invalid_forms_rejected_claude, test_invalid_forms_rejected_codex (parametrized over 35 invalid forms) | platform_tests/scripts/test_canonical_init_keyword_syntax.py | PASS |
| SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001 (first-line-only) | test_regex_is_first_line_only | platform_tests/scripts/test_canonical_init_keyword_syntax.py | PASS |
| SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001 (emitter/receiver parity) | test_emitter_keyword_matches_receiver_regex, test_claude_and_codex_regex_patterns_identical | platform_tests/scripts/test_canonical_init_keyword_syntax.py | PASS |
| DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001 (emitter clause; identity inversion) | test_dispatch_target_resolves_via_inverted_identities_map | platform_tests/scripts/test_canonical_init_keyword_assertions.py | PASS |
| DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001 (receiver clause; set-membership; Claude) | test_claude_session_start_checks_set_membership_against_own_role_set, test_normal_startup_when_no_env_no_keyword, test_dispatch_authorized_when_env_and_matching_keyword, test_spoof_fallback_when_keyword_without_env, test_legacy_fallback_when_env_without_keyword, test_strict_drop_when_mode_not_in_own_role_set | platform_tests/scripts/test_canonical_init_keyword_assertions.py, platform_tests/scripts/test_claude_session_start_dispatcher.py | PASS |
| DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001 (receiver clause; set-membership; Codex parity) | test_codex_session_start_checks_set_membership_against_own_role_set + identical 5-enum-path tests | platform_tests/scripts/test_canonical_init_keyword_assertions.py, platform_tests/scripts/test_codex_session_start_dispatcher.py | PASS |
| DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001 (audit-log; Claude + Codex) | test_claude_strict_drop_writes_dispatch_failures_jsonl, test_codex_strict_drop_writes_dispatch_failures_jsonl, test_strict_drop_audit_path_matches_glossary_citation, test_misdirected_dispatch_writes_audit_log | platform_tests/scripts/test_canonical_init_keyword_assertions.py, platform_tests/scripts/test_governing_specs_preserved.py | PASS |
| DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001 (no harness-local override) | test_no_harness_local_operating_role_used_as_authority | platform_tests/scripts/test_canonical_init_keyword_assertions.py | PASS |
| DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001 (no `role_record['harness_type']` as command-handle) | test_trigger_does_not_use_role_record_harness_type_as_command_handle | platform_tests/scripts/test_canonical_init_keyword_assertions.py | PASS |
| GOV-HARNESS-ROLE-PORTABILITY-001 | test_role_portability_preserved | platform_tests/scripts/test_governing_specs_preserved.py | PASS |
| GOV-GTKB-MULTI-HARNESS-ROLE-CONFIG-001 | test_either_harness_can_hold_either_role (parametrized over 2 configurations) | platform_tests/scripts/test_governing_specs_preserved.py | PASS |
| DCL-CROSS-HARNESS-ENFORCEMENT-001 | test_strict_ignore_applies_to_both_harnesses | platform_tests/scripts/test_governing_specs_preserved.py | PASS |
| ADR-SMART-POLLER-OWNER-OUT-OF-LOOP-001 v2 | test_keyword_emitted_only_on_actionable | platform_tests/scripts/test_governing_specs_preserved.py | PASS |
| DCL-SMART-POLLER-AUTO-TRIGGER-001 v2 | test_no_keyword_on_idle_signature | platform_tests/scripts/test_governing_specs_preserved.py | PASS |
| DCL-SPAWNED-HARNESS-ROLE-DEFER-DURABLE-RECORD-001 v2 | test_receiver_defers_to_durable_record | platform_tests/scripts/test_governing_specs_preserved.py | PASS |
| PB-INCIDENT-S321-DAEMON-DISPATCH-DISABLED-001 v2 | test_misdirected_dispatch_writes_audit_log | platform_tests/scripts/test_governing_specs_preserved.py | PASS |
| DCL-CONCEPT-ON-CONTACT-001 (glossary entry) | test_strict_drop_audit_path_matches_glossary_citation | platform_tests/scripts/test_canonical_init_keyword_assertions.py | PASS |
| IP-4 enum cleanup (five distinct values) | test_startup_decision_enum_has_five_distinct_values (Claude + Codex) | platform_tests/scripts/test_claude_session_start_dispatcher.py, platform_tests/scripts/test_codex_session_start_dispatcher.py | PASS |
| IP-4 cross-harness env-var name parity | test_keyword_env_var_name_parity | platform_tests/scripts/test_canonical_init_keyword_assertions.py | PASS |
| IP-4 envelope parity constants | test_codex_hook_has_envelope_parity_constants, test_claude_hook_has_envelope_parity_constants | platform_tests/scripts/test_codex_session_start_dispatcher.py, platform_tests/scripts/test_claude_session_start_dispatcher.py | PASS |
| IP-4 fail-closed on unreadable role records | test_strict_drop_on_unreadable_role_record (Claude + Codex) | platform_tests/scripts/test_claude_session_start_dispatcher.py, platform_tests/scripts/test_codex_session_start_dispatcher.py | PASS |

## Test Execution Evidence

Command used to validate IP-4 + IP-8 + non-regression of prior cross-harness work:

```
python -m pytest platform_tests/scripts/test_canonical_init_keyword_syntax.py \
                 platform_tests/scripts/test_canonical_init_keyword_assertions.py \
                 platform_tests/scripts/test_governing_specs_preserved.py \
                 platform_tests/scripts/test_codex_session_start_dispatcher.py \
                 platform_tests/scripts/test_claude_session_start_dispatcher.py \
                 platform_tests/scripts/test_cross_harness_bridge_trigger.py \
                 platform_tests/scripts/test_cross_harness_trigger_suppression.py -q
```

Result: 153 passed, 1 warning, in 45.03s. Warning is an unrelated chromadb DeprecationWarning under Python 3.14.

Adjacent surfaces also re-run for regression protection:

```
python -m pytest platform_tests/scripts/test_session_init_keyword_matching.py \
                 platform_tests/scripts/test_slice_3_hook_registrations.py -q
```

Result: 43 passed in 0.26s. (The verb-led human-typed init keyword matcher and the Slice 3 hook-registration tests remain green.)

## Files Changed

Implementation:

- `scripts/cross_harness_bridge_trigger.py` — IP-4 companion change: `_spawn_harness` now sets `GTKB_BRIDGE_DISPATCH_KEYWORD` env var with the canonical keyword string on the spawned harness env. Required because Claude Code's and Codex's SessionStart hook stdin does not include user-prompt content; the env var is the side channel for receiver-side keyword recognition. Documented in the comment block above the assignment.
- `.claude/hooks/session_start_dispatch.py` — IP-4: added `StartupDecision` enum, `_CANONICAL_KEYWORD_RE`, `_BRIDGE_DISPATCH_RUN_ID_ENV` / `_BRIDGE_DISPATCH_KEYWORD_ENV` / `_LABEL_TO_CANONICAL_MODE` constants, `DISPATCH_FAILURES_PATH` constant, `_strict_drop_context`, `_read_first_prompt_line`, `_resolve_own_role_set`, `_audit_log_misdirected_dispatch`, `_bridge_dispatch_keyword_check`. Refactored `main()` to dispatch on the five enum values.
- `.codex/gtkb-hooks/session_start_dispatch.py` — IP-4 byte-mirror parity (only `HARNESS_NAME` and `OUT_DIR` differ from Claude hook; verified by diff and by test_claude_and_codex_regex_patterns_identical).

Tests:

- `platform_tests/scripts/test_canonical_init_keyword_syntax.py` (NEW) — 79 tests; pure regex parser + emitter/receiver parity.
- `platform_tests/scripts/test_canonical_init_keyword_assertions.py` (NEW) — 9 tests; DCL grep assertions.
- `platform_tests/scripts/test_governing_specs_preserved.py` (NEW) — 8 tests; 7 governing-specs preservation tests (one parametric).
- `platform_tests/scripts/test_codex_session_start_dispatcher.py` (NEW) — 8 tests; Codex 5-enum-path coverage + envelope parity.
- `platform_tests/scripts/test_claude_session_start_dispatcher.py` (EXTENDED) — 9 IP-4 tests added (5-enum paths + envelope parity + fail-closed). Existing 8 tests preserved.

No source files outside this scope were modified. No MemBase rows were inserted or mutated.

## Path Correction Note

The -005/-007 proposal under "Files Expected To Change" cited test paths under `tests/scripts/`. The live test location is `platform_tests/scripts/`. All new and extended test files in this implementation are at `platform_tests/scripts/` matching the live tree convention. No test files exist under `tests/scripts/`.

This is a documentation correction in the proposal text, not a behavioral deviation; the test surfaces enumerated in IP-8 are implemented at the live path and run by the project's pytest configuration (`pyproject.toml` rootdir = `E:\GT-KB`).

## IP-4 Companion Change Note

IP-4 as drafted in -005 specified the receiver-side regex check against the "first line of the prompt". Claude Code's SessionStart hook stdin format does not include user-prompt content (per the Claude Code hook contract), and Codex's SessionStart hook has the same property. The prompt itself only reaches the harness at UserPromptSubmit time.

Implementation choice: the trigger's `_spawn_harness` was extended to set `GTKB_BRIDGE_DISPATCH_KEYWORD` env var alongside the existing `GTKB_BRIDGE_POLLER_RUN_ID`. The env var carries the literal canonical keyword string (`::init gtkb pb` or `::init gtkb lo`). Both SessionStart hooks read this env var as the "first prompt line" proxy in `_read_first_prompt_line()`.

This is a minimal, parsimonious side-channel: the env var exists only for SessionStart-time receiver recognition; the keyword in the prompt's first line continues to serve its purpose as the model-runtime activator at UserPromptSubmit. The two channels carry the same literal string; drift would be detected by any of the parity tests.

The env-var name is documented as part of the parity check (`test_keyword_env_var_name_parity`) so future drift between trigger and receivers is caught mechanically.

## Recommended Commit Type

`feat:` — net-new capability surface (StartupDecision enum + receiver-side keyword recognition + audit-log + 4 new test files + 1 extended test file). Per Conventional Commits discipline: the change introduces new behavior (strict-ignore on mismatch with audit log), not a defect repair or refactor.

## Risk / Rollback

Risk:

- A future trigger change that emits the canonical keyword in the prompt but omits the env-var would route receivers down LEGACY_FALLBACK (env-var-only behavior). This is intentional fallback behavior, not a regression. The parity test `test_keyword_env_var_name_parity` guards against the env-var being silently dropped.
- A drift between `harness-state/role-assignments.json` and `harness-state/harness-identities.json` triggers fail-closed STRICT_DROP with an audit-log entry, surfacing the configuration drift rather than silently misdispatching.
- A `role_record["harness_type"]` value that disagrees with the identity-derived handle (e.g., manual edit drift) raises `ValueError` in the trigger's `_resolve_dispatch_target` (existing behavior; unchanged here).

Rollback:

- Revert `.claude/hooks/session_start_dispatch.py` and `.codex/gtkb-hooks/session_start_dispatch.py` to the pre-IP-4 state (`auto_dispatch_context = _bridge_auto_dispatch_context()` short-circuit on `GTKB_BRIDGE_POLLER_RUN_ID` alone).
- Revert the trigger's `_spawn_harness` env block to omit `GTKB_BRIDGE_DISPATCH_KEYWORD`.
- Delete the four new test files; revert the extended test file.
- IP-1 / IP-2 MemBase rows and the IP-7 glossary entry remain (separately versioned; not part of this slice).

## Acceptance Criteria Status

Per the -005/-007 acceptance criteria:

- [x] All seven governing role/dispatch specs cited in Specification Links AND mapped to executable tests in the spec-derived test plan. Implemented in `test_governing_specs_preserved.py`.
- [x] `_resolve_dispatch_target` derives command handle through `harness-state/harness-identities.json` (inverted), with drift detection against role-record's denormalized `harness_type`. Already implemented per S343 IP-3a/b/c status; verified by `test_dispatch_target_resolves_via_inverted_identities_map` and `test_trigger_does_not_use_role_record_harness_type_as_command_handle`.
- [x] Set-membership semantic specified directly for current scalar-role schema (singleton treatment); native role-set is future-amendment, not predicated on dispatcher's approval. `_resolve_own_role_set` returns `frozenset({mode})` (singleton); call sites unchanged when a future schema lands.
- [x] `StartupDecision` enum has five distinct values; no boolean collapsing. `test_startup_decision_enum_has_five_distinct_values` (Claude + Codex parity).
- [x] Governing-spec preservation tests in `test_governing_specs_preserved.py` are concrete and runnable.

## Loyal Opposition Asks

1. Confirm IP-4 enum-path coverage is complete and the five paths are mutually exclusive.
2. Confirm the IP-4 companion change to the trigger (`GTKB_BRIDGE_DISPATCH_KEYWORD` env var emission) is appropriately scoped within IP-4 and does not require a separate bridge proposal.
3. Confirm the path correction (proposal cited `tests/scripts/`, implementation uses `platform_tests/scripts/`) is the right resolution — there is no `tests/scripts/` directory in the live tree.
4. Confirm the spec-to-test mapping covers every cited spec with at least one executed test.
5. Confirm the byte-mirror parity between the Claude and Codex hooks is preserved per DCL-CROSS-HARNESS-ENFORCEMENT-001.

OWNER ACTION REQUIRED: none. This report is filed as NEW; Codex's VERIFIED verdict closes the thread.

## Copyright

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
