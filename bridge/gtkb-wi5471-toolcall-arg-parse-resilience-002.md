GO
::init gtkb pb
::open test
author_identity: loyal-opposition/claude
author_harness_id: B
author_session_context_id: f15698f1-d8a9-4c63-8905-a3aaa30fa609
author_model: claude-sonnet-5
author_model_version: claude-sonnet-5
author_model_configuration: Claude Code sub-agent performing Loyal Opposition bulk bridge processing; independent fresh-context review session, no shared context with the proposal author session

# Loyal Opposition GO Verdict - WI-5471 Tool-call argument parse resilience in dispatch worker shims

bridge_kind: lo_verdict
Document: gtkb-wi5471-toolcall-arg-parse-resilience
Version: 002
Responds to: bridge/gtkb-wi5471-toolcall-arg-parse-resilience-001.md
Date: 2026-07-17 UTC

## Verdict

GO. The claimed defect is real and independently confirmed by reading the exact code paths in both target shims. The fix direction (route the malformed-JSON parse failure through the existing recoverable tool-error pattern) is sound, minimal, and consistent with a pattern already implemented for `dispatch_tool_call` errors in both shims. Both mandatory preflights pass with zero blocking gaps. The project authorization and work item are independently verified as active/open and correctly scoped, and the fast-lane eligibility criteria are all met.

## Review Independence

- Reviewer session: `f15698f1-d8a9-4c63-8905-a3aaa30fa609` (this sub-agent invocation, fresh context, no prior turns on this thread).
- Proposal author session: `d067ca16-171b-4b2e-89f5-642340e605a6` (per `bridge/gtkb-wi5471-toolcall-arg-parse-resilience-001.md` line 6, `author_identity: prime-builder/codex`).
- Identifiers are present and distinct; review independence passes.

## Applicability Preflight

Command: `groundtruth-kb/.venv/Scripts/python.exe scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5471-toolcall-arg-parse-resilience`

- packet_hash: `sha256:012fe9c6d829c770b0e1126234afb2390e9f1e65d223e7e4ccd32e0185d1eef9`
- operative_file: `bridge/gtkb-wi5471-toolcall-arg-parse-resilience-001.md`
- preflight_passed: `true`
- missing_required_specs: `[]`
- missing_advisory_specs: `[]`
- blocking_errors: `[]`
- exit code: `0`

All six evaluated specs (`ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`, `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`, `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`, `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `GOV-FILE-BRIDGE-AUTHORITY-001`) were cited.

## Clause Applicability

Command: `groundtruth-kb/.venv/Scripts/python.exe scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi5471-toolcall-arg-parse-resilience`

- Clauses evaluated: 5 (`must_apply: 4`, `may_apply: 1`, `not_applicable: 0`)
- Evidence gaps in must_apply clauses: `0`
- Blocking gaps (gate-failing): `0`
- Mode: mandatory. Exit code: `0` (pass; exit 5 would indicate a blocking gap).

## Deliberation Archive Check

Ran `KnowledgeDB.search_deliberations()` with queries `"malformed JSON tool call arguments"`, `"GOV-RELIABILITY-FAST-LANE-001 eligibility"`, and `"JSONDecodeError tool_call arguments"`. All three returned only generic/unrelated hits (backlog JSON validation reviews, cross-harness trigger fixes, unrelated verification verdicts) with no semantic match on this specific defect. No prior deliberation exists on this exact tool-call-argument-parse failure mode; WI-5471 was created same-day (`changed_at: 2026-07-17T18:09:24+00:00`) from a fresh owner AUQ, consistent with no prior coverage. Stated per `.claude/rules/deliberation-protocol.md`: no relevant prior deliberations found for this topic.

## Independent Technical Verification

The proposal's problem statement was verified by reading the actual source, not trusting the prose:

- `scripts/cloud_harness_base.py` lines 2210-2232, function `_tool_call_parts`: when `function.get("arguments")` is a string, it is parsed with `json.loads(raw_arguments or "{}")` inside a bare `try/except json.JSONDecodeError`, and on failure raises `CloudHarnessError("tool_call arguments string must be JSON")` (line 2228).
- The call site is `scripts/cloud_harness_base.py` line 2567, inside `run_tool_loop`'s per-tool-call dispatch loop: `tool_name, arguments, call_id = _tool_call_parts(call, index)`. This call is made BEFORE the `try/except CloudHarnessError as tool_err: result = f"ERROR: {tool_err}"` block that wraps only `dispatch_tool_call` (lines 2589-2603). A `CloudHarnessError` raised inside `_tool_call_parts` is therefore not caught locally; it propagates out of both the per-call loop and the per-turn `for _turn in range(max_turns)` loop, is caught once by the outer `except CloudHarnessError as exc:` at line 2654 only to classify `stop_reason` and then `raise` again, unwinding `run_tool_loop` entirely. This confirms the claimed defect: a malformed-JSON tool-call argument aborts the whole worker with no retry.
- `scripts/ollama_harness.py` carries an identical `_tool_call_parts` function (lines 1141-1161, using `OllamaHarnessError`) and an identical call-site defect at line 1360, again outside the local `try/except OllamaHarnessError` (lines 1369-1383) that wraps only `dispatch_tool_call`. The inline comment at lines 1380-1382 ("Guard denial or other tool error: return error as tool result instead of crashing the loop") documents the existing recoverable-tool-error pattern the proposal intends to extend to the parse-failure case; that pattern does not currently cover `_tool_call_parts` failures in either shim.
- The "existing repeated-signature backstop" the proposal relies on to bound any retry loop is real: `MAX_REPEATED_TOOL_SIGNATURE_TURNS = 4` (line 114) and the check at lines 2550-2557 (`cloud_harness_base.py`) / lines 1349-1356 (`ollama_harness.py`) raises after more than 4 turns with an identical `tool_calls` signature. If a smaller model resends the identical malformed call repeatedly, the backstop still trips; this is consistent with the proposal's acceptance criteria and introduces no new unbounded-loop risk.

Conclusion: the defect claim is accurate and precisely characterized in both shims, and the proposed remediation (extend the try/except that already wraps `dispatch_tool_call` to also cover the `_tool_call_parts` call, converting the parse failure into a `"ERROR: ..."` tool-result keyed to the call id) is the correct, minimal fix consistent with the pattern already used for every other tool-dispatch failure in both shims.

## Project Authorization / Work Item / Fast-Lane Eligibility Verification

Independently queried MemBase (not the proposal's prose) via `KnowledgeDB`:

- `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING`: `status: active`, `project_id: PROJECT-GTKB-RELIABILITY-FIXES`, `allowed_mutation_classes: ["source", "test_addition", "hook_upgrade"]`, `forbidden_operations: ["deploy", "git_push_force", "spec_deletion"]`. The proposal's mutation (source edits + one new test file) is within `allowed_mutation_classes` and touches none of `forbidden_operations`.
- `WI-5471`: exists, `resolution_status: open`, `stage: backlogged`, `priority: P1`, `origin: defect`, `project_name: PROJECT-GTKB-RELIABILITY-FIXES` (matches the PAUTH's `project_id`, satisfying "active project membership" coverage since `included_work_item_ids` is null). `source_owner_directive: "Owner AUQ 2026-07-17: fix robustness first before relying on cloud dispatch workers"` is a real, dated owner-decision trail behind this WI.
- `PROJECT-GTKB-RELIABILITY-FIXES`: `status: active`.
- `GOV-RELIABILITY-FAST-LANE-001` eligibility (all four required):
  1. Origin is `defect` (never `new`) - PASS.
  2. No new public API/CLI surface/behavior beyond removing the defect - PASS (internal tool-dispatch error-handling change only).
  3. No new or revised requirement/specification needed - PASS (proposal's own Requirement Sufficiency section agrees; nothing in this review contradicts it).
  4. Small, single-concern, guide of ~3 source files / ~150 net lines - PASS. `target_paths` lists exactly 2 non-test source files (`cloud_harness_base.py`, `ollama_harness.py`) plus 1 net-new test file; the fix is a narrow try/except widening applied identically at one call site per shim.

All four criteria independently confirmed met; the fast-lane classification is legitimate and `GOV-RELIABILITY-FAST-LANE-001`'s NO-GO trigger ("any fast-lane proposal whose work item fails an eligibility criterion") does not apply.

## Root Boundary / Target Path Verification

- `target_paths`: `scripts/cloud_harness_base.py`, `scripts/ollama_harness.py`, `platform_tests/scripts/test_shim_toolcall_arg_resilience.py` - all three resolve under `E:\GT-KB` (repo root); no out-of-root dependency.
- `git status --short -- scripts/cloud_harness_base.py scripts/ollama_harness.py platform_tests/scripts/test_shim_toolcall_arg_resilience.py` returned no output (clean; the two source files are tracked and unmodified, the test file does not yet exist), confirming a clean implementation baseline consistent with `git ls-files` showing both source paths tracked.

## Backlog Conflict Check

Queried open work items for `cloud_harness_base` / `ollama_harness` / tool-call-related text. Two adjacent, non-conflicting items found in the same project:

- `WI-5191` (backlogged) - native-hook PreToolUse empty-stdout handling in `cloud_harness_base.py`; a different function/region (native-hook output contract), not `_tool_call_parts`.
- `WI-5495` (backlogged) - publisher-only-recovery `tool_choice` forcing on the OpenAI-compatible dialect in `cloud_harness_base.py`; a different region of `run_tool_loop` (the `publisher_only_recovery` branch, lines 2386-2548), not the `_tool_call_parts` call site at line 2567.

Neither is `GO`'d or in-flight (both remain `backlogged`; live bridge `state-report` shows no other actionable thread referencing either file). No duplication or interference; noted for the record rather than as a blocker, since both touch the same file but different, non-overlapping concerns.

## Non-Blocking Observations

1. The proposal creates one new shared test module (`test_shim_toolcall_arg_resilience.py`) covering both shims rather than extending the two existing per-shim modules (`test_cloud_harness_base.py`, `test_ollama_harness.py`, neither of which currently tests `_tool_call_parts`). This is disclosed in the proposal's verification-plan row for `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` ("pytest the new test module covering both shims") and is a reasonable choice given the defect and fix are byte-identical in shape across both shims. Not a defect; flagged only so the post-implementation verifier expects this file layout.
2. The implementation should decide, and the post-implementation report should state, whether the try/except widening covers only the JSON-decode failure (`"tool_call arguments string must be JSON"`) or all of `_tool_call_parts`'s raise points (missing function name, non-dict arguments). The proposal's Acceptance Criteria is precisely scoped to "arguments string is not valid JSON," so either choice is compliant; the verifier should confirm test coverage matches whichever scope was actually implemented.

## Specification Links (carried forward)

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `SPEC-AUQ-POLICY-ENGINE-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `GOV-STANDING-BACKLOG-001`
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `GOV-RELIABILITY-FAST-LANE-001`

## Prior Deliberations

- No prior deliberations found for this specific tool-call-argument-parse defect (see Deliberation Archive Check above). WI-5471 originates from a same-day owner AUQ, not a re-litigated prior decision.

## Commands Executed

- `groundtruth-kb/.venv/Scripts/gt.exe bridge show gtkb-wi5471-toolcall-arg-parse-resilience --json --compact`
- `groundtruth-kb/.venv/Scripts/python.exe scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5471-toolcall-arg-parse-resilience` (exit 0)
- `groundtruth-kb/.venv/Scripts/python.exe scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi5471-toolcall-arg-parse-resilience` (exit 0)
- Read `scripts/cloud_harness_base.py` in full (2680 lines) and `scripts/ollama_harness.py` (relevant sections around lines 1141-1410).
- `git status --short -- scripts/cloud_harness_base.py scripts/ollama_harness.py platform_tests/scripts/test_shim_toolcall_arg_resilience.py`
- `git ls-files -- scripts/cloud_harness_base.py scripts/ollama_harness.py`
- `KnowledgeDB.get_project_authorization('PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING')`
- `KnowledgeDB.get_work_item('WI-5471')`
- `KnowledgeDB.get_project('PROJECT-GTKB-RELIABILITY-FIXES')`
- `KnowledgeDB.get_spec('GOV-RELIABILITY-FAST-LANE-001')`
- `KnowledgeDB.list_work_items(resolution_status='open')` filtered for target-file/topic overlap
- `KnowledgeDB.search_deliberations(...)` x3 (see Deliberation Archive Check)
- `groundtruth-kb/.venv/Scripts/gt.exe bridge state-report --json` (checked for other actionable threads touching the same files)

## Recommended Next Step

Prime Builder proceeds with implementation per the approved scope: run `python scripts/implementation_authorization.py begin --bridge-id gtkb-wi5471-toolcall-arg-parse-resilience` to open the implementation-start packet, implement the try/except widening at both call sites plus the new test module, run `ruff check` and `ruff format --check` on the changed Python files, then file the post-implementation report carrying forward this thread's linked specifications and a spec-to-test mapping.

## Owner Action Required

None. This is a fast-lane-eligible fix already covered by the standing project authorization; no additional owner approval is required before implementation per `GOV-RELIABILITY-FAST-LANE-001`.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

