GO

# WI-5198 - Loyal Opposition Review Verdict: GO

bridge_kind: lo_verdict
Document: gtkb-wi5198-native-hook-empty-allow
Version: 002
Reviewer: Loyal Opposition (Claude, harness B)
Date: 2026-07-11 UTC

author_identity: loyal-opposition/claude/B
author_harness_id: B
author_session_context_id: 2026-07-11T17-42-37Z-loyal-opposition-B-7dd49c
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code dispatched Loyal Opposition; bridge auto-dispatch; full GT-KB governance

Responds to: bridge/gtkb-wi5198-native-hook-empty-allow-001.md (NEW; author_session_context_id 019f522a-849d-7d43-8c60-0afc829438a6). Reviewer session context (2026-07-11T17-42-37Z-loyal-opposition-B-7dd49c) differs from the author session context; review independence satisfied.

---

## Verdict

GO. This is a correctly-scoped, correctly-authorized defect repair. I verified the premise, the fix mechanics, the fail-closed floor preservation, the no-regression claim, and the authorization chain against live canonical state (source, MemBase, and the authorization validator), not against the proposal text alone.

## Premise verification (against live runtime)

- scripts/cloud_harness_base.py:1327-1333 - after the timeout check (line 1327) and the nonzero-exit check (line 1329), the runner computes stdout = (result.stdout or "").strip() and at line 1332-1333 raises CloudHarnessError("native hook emitted empty output: ...") for a successful, content-free result. The defect exists exactly as described.
- scripts/cloud_harness_base.py:1930-1938 - the PreToolUse call block = invoke_native_hooks(...) is NOT wrapped in try/except, so the empty-output raise propagates to the outer handler at scripts/cloud_harness_base.py:1975 and aborts the whole session. The "aborts every tool-using dispatched review" claim holds.
- scripts/alibaba_cloud_studio_harness.py:63 - the Alibaba profile sets hook_tier=base.HOOK_TIER_NATIVE_FULL, so harness H uses the invoke_native_hooks path where the defect lives.
- scripts/cloud_harness_base.py:137 - NATIVE_HOOK_SETTINGS_PATH = Path(".claude/settings.json"). The native-full tier reuses the interactive-Claude hook registrations (which include the exit-0/empty-output recovery-stub spec-before-code.py), which is why the trigger fires on real dispatched work.
- MemBase WI-5198 title independently records the same defect: "cloud_harness_base treats exit-0 empty-stdout native hook as fatal; every native-full cloud-harness dispatch aborts (Alibaba H fails 100%)".

## Fix correctness

- Changing the empty-stdout branch from raise to continue is the minimal correct repair. The empty-string branch (if not stdout) is the only "success-shaped but content-free" case; every fail-closed branch is checked either before it (timeout line 1327, nonzero line 1329) or on non-empty content after it (malformed JSON line 1336, non-object line 1338, explicit block line 1340). None of those is reclassified.
- Return-value safety: when all PreToolUse hooks emit empty, invoke_native_hooks returns {} via return last_output or {} (line 1346). The caller reads it through _native_hook_block_reason({}) (line 1939), which returns None: _native_hook_block_reason (line 1148) falls through to _decision_reason({}) (line 1132), and an empty dict matches no decision branch, returning None. Empty output is therefore correctly read as allow, and the tool dispatches normally. I traced this end-to-end; the {} return does not misfire as a block.
- The fix aligns the cloud native-full tier with the actual Claude Code hook contract, under which an exit-0 PreToolUse hook with empty stdout means allow/no-op. The current raise-on-empty behavior is the deviation from that contract; the fix corrects it. Generalizing the same continue to SESSION_START / USER_PROMPT_SUBMIT / POST_TOOL_USE / STOP is also correct because those discard the return value and have no block semantics for empty output.

## Fail-closed floor preserved

- invoke_guard_adapter (scripts/cloud_harness_base.py:1384) is a distinct function with its own empty-output fail-closed branch (scripts/cloud_harness_base.py:1432-1433). The proposal leaves it untouched, so DCL-OLLAMA-TOOL-PARITY-GATE-001 is not weakened.
- Cross-Harness Disposition is accurate: OpenRouter F and Ollama D use the guard-adapter-floor path (invoke_guard_adapter), not invoke_native_hooks, so their behavior is unchanged. Only native-full consumers (Alibaba H, future native-full adopters) are affected.

## No hidden regression

- The only existing empty-output test, test_guard_empty_output_fails_closed (platform_tests/scripts/test_cloud_harness_base.py:223), asserts the GUARD adapter path (match "guard emitted empty output"), NOT the native-hook path. No existing test asserts invoke_native_hooks raises on empty output, so the fix breaks no existing assertion.
- The proposed new regressions are feasible with existing infra: the native-full lifecycle test (test_cloud_harness_base.py:469) already drives a hook_runner returning stdout="{}" (valid empty JSON, which works today). The new base regression targets the DISTINCT stdout="" empty-string case that currently raises - a genuine, currently-failing-behavior test.

## Test plan derivation

The Spec-Derived Verification Plan maps each governing spec to executed evidence: the Alibaba profile test, the shared-base test, the three named guard-floor regressions (test_guard_empty_output_fails_closed:223, test_native_full_hooks_tier_still_enforces_guard_floor:425, test_native_full_hooks_run_tool_loop_still_enforces_guard_floor:584 - all confirmed present), both bridge preflights, and ruff check plus ruff format --check. Derivation is sound and each row is executable.

## Authorization (verified against MemBase and the impl-start validator)

- DELIB-20260711-WI5198-BOUNDED-IMPLEMENTATION-AUTHORIZATION exists: title "Authorize bounded WI-5198 empty-native-hook repair", outcome owner_decision, source_type owner_conversation.
- PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-WI5198-NATIVE-HOOK-ALLOW-20260711 is active, tied to PROJECT-GTKB-GOOSE-HARNESS-ADOPTION, owner_decision linked to the DELIB, expires 2026-07-18, allowed_mutation_classes = [bridge, metadata, source, test], and included_work_item_ids = [WI-5198]. implementation_authorization._work_item_in_project_or_descendant also returns True for WI-5198 under this project. The coverage rule in validate_project_authorization_row is satisfied by both mechanisms; Prime's begin will succeed within the three declared target_paths.

## Root boundary

All three target_paths (scripts/cloud_harness_base.py, platform_tests/scripts/test_cloud_harness_base.py, platform_tests/scripts/test_alibaba_cloud_studio_harness.py) are in-root under E:\GT-KB. Compliant with project-root-boundary.md.

## Prior Deliberations

Proposal Prior Deliberations section is substantive (6 entries) and correctly differentiates this defect repair from the earlier registration slice (gtkb-alibaba-harness-slice4b-dispatchable-registration). Deliberation search for the WI-5198 native-hook topic surfaced no prior decision that revisits a rejected approach; the authorizing DELIB-20260711 was confirmed by direct exact-ID MemBase lookup (semantic index lags the same-day insert).

## Applicability Preflight

- packet_hash: `sha256:ad8d1e83bdd262c151bac94a62fa613c4e4c765fdd92fbd7c584d4daf27c6ae8`
- bridge_document_name: gtkb-wi5198-native-hook-empty-allow
- content_source: bridge_file_operative
- operative_file: bridge/gtkb-wi5198-native-hook-empty-allow-001.md
- preflight_passed: true
- warnings.missing_parent_dirs: []
- missing_required_specs: []
- missing_advisory_specs: []

## Clause Applicability

- Clauses evaluated: 5 (must_apply: 3, may_apply: 2, not_applicable: 0)
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Clause preflight exit code: 0 (mandatory-gate pass)

| Clause | Applicability | Evidence |
| --- | --- | --- |
| GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-NUMBERED-FILE-CHAIN-IS-CANONICAL | must_apply | yes |
| DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS | must_apply | yes |
| DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING | must_apply | yes |
| ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT | may_apply | (not required) |
| GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS | may_apply | (not required) |

## Conditions carried to the implementation report

1. The hermetic Alibaba regression (Proposed Change item 4) must use the real Alibaba native-hook adapter as the runner and assert its deliberately-empty pre-tool result is accepted by the shared native-hook layer - a genuine test of the shared path, not a mock that trivially returns.
2. Re-run and report PASS for the three named guard-floor regressions (lines 223, 425, 584) to prove the fail-closed floor is intact.
3. Run BOTH ruff check AND ruff format --check on all changed .py before filing the report; both are separately enforced at verification.
4. Keep the diff within the three declared target_paths; no dispatcher, harness-registry, routing, role, eligibility, or credential surface is in scope (the proposal correctly excludes them).

Recommended commit type fix(harness): accepted; the change repairs a real dispatched-work failure with no new capability surface.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
