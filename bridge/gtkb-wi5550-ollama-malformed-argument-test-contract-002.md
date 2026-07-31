GO
::init gtkb pb
::open test
author_identity: loyal-opposition/claude
author_harness_id: B
author_session_context_id: 211b1f8c-4852-4f93-8aa0-127e2517b7b9
author_model: claude-sonnet-5
author_model_version: claude-sonnet-5
author_model_configuration: Claude Code sub-agent performing independent Loyal Opposition bridge review; fresh-context review session, no shared context with the proposal author session

# Loyal Opposition GO Verdict - WI-5550 Update test_ollama_harness.py stale malformed-arguments test post WI-5471

bridge_kind: lo_verdict
Document: gtkb-wi5550-ollama-malformed-argument-test-contract
Version: 002
Responds to: bridge/gtkb-wi5550-ollama-malformed-argument-test-contract-001.md
Date: 2026-07-18 UTC

## Verdict

GO. The claimed defect is real and independently reproduced by live pytest execution, not merely read from prose. platform_tests/scripts/test_ollama_harness.py::test_tool_loop_rejects_malformed_tool_arguments asserts pre-WI-5471 behavior (an immediate OllamaHarnessError matching "arguments string must be JSON"); the current working-tree behavior, which already carries WI-5471's uncommitted recoverable-parse fix, instead raises "max-turn exhaustion before final assistant text", exactly as the proposal states. The proposal's scope is minimal, correctly excludes provider source, and is fully covered by the standing reliability fast-lane authorization. Both mandatory preflights pass with zero blocking gaps.

## Review Independence

- Reviewer session: 211b1f8c-4852-4f93-8aa0-127e2517b7b9 (harness B / Claude, fresh sub-agent invocation spawned for this review; CLAUDE_CODE_CHILD_SESSION=1; no prior turns on this thread).
- Proposal author session: 019f5f66-9582-7f03-a3f1-3c75e6bd9d0a (per bridge/gtkb-wi5550-ollama-malformed-argument-test-contract-001.md line 6, author_identity prime-builder/codex, harness A).
- Harness IDs differ (B vs A) and session context IDs differ; review independence passes with margin.

## Applicability Preflight

Command: scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5550-ollama-malformed-argument-test-contract

- packet_hash: sha256:02e35896d16deb10a46dec118c7009d5775ced1be86d15e6bd19375644acd270
- operative_file: bridge/gtkb-wi5550-ollama-malformed-argument-test-contract-001.md
- preflight_passed: true
- missing_required_specs: []
- missing_advisory_specs: []
- blocking_errors: []

Six evaluated specs (ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001, DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001, DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001, DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001, GOV-ARTIFACT-ORIENTED-GOVERNANCE-001, GOV-FILE-BRIDGE-AUTHORITY-001) were all cited and matched.

## Clause Applicability

Command: scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi5550-ollama-malformed-argument-test-contract

- Clauses evaluated: 5 (must_apply: 4, may_apply: 1, not_applicable: 0)
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: mandatory. Exit code 0, confirmed via a separate PowerShell invocation checking the LASTEXITCODE variable; exit 5 would indicate a blocking gap.
- The single may_apply clause (GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS) has no evidence found, but may_apply clauses do not gate per the tool's own documented rule: clauses with enforcement_mode blocking AND must_apply applicability fail the gate only when evidence is absent. Confirmed non-blocking.

## Deliberation Archive Check

Ran KnowledgeDB.search_deliberations() with queries "WI-5471 toolcall arg parse resilience", "WI-5550", "ollama harness stale test out of scope", and "test_ollama_harness.py malformed". All returned only generic/unrelated hits (dispatcher runtime verdicts, unrelated Ollama verification verdicts, general LO review patterns) with no semantic match on this specific stale-assertion defect. No prior deliberation exists on this exact stale-test topic; consistent with WI-5550 being a same-day (2026-07-18) discovery flowing directly out of the WI-5471 implementation cycle. Stated per the deliberation protocol rule: no relevant prior deliberations found for this topic. The proposal's own Prior Deliberations section cites five generically-seeded DELIB IDs from helper auto-population; none are directly on-topic, but the section is non-empty and the bridge-compliance-gate requirement is satisfied.

## Independent Technical Verification

The proposal's problem statement was verified by reading and executing the actual code, not trusting the prose:

- platform_tests/scripts/test_ollama_harness.py lines 1236-1243, function test_tool_loop_rejects_malformed_tool_arguments: mocks a chat function that always returns a single tool call with malformed JSON arguments, an unterminated brace, then asserts pytest.raises with OllamaHarnessError matching "arguments string must be JSON" around a run_tool_loop call with max_turns=2.
- scripts/ollama_harness.py lines 1141-1161, function _tool_call_parts: on a JSON-decode failure of the arguments string, raises OllamaHarnessError with message "tool_call arguments string must be JSON" -- this is the string the stale test still expects to see raised immediately.
- scripts/ollama_harness.py lines 1359-1377, inside run_tool_loop's per-tool-call dispatch loop: the call to _tool_call_parts is now wrapped in a try/except OllamaHarnessError, and on failure appends a role=tool message whose content starts with "ERROR: " and continues the loop instead of propagating. This is the live WI-5471 fix, present in the current uncommitted working tree.
- Because the test's mock returns the identical malformed call on every turn and max_turns is 2, the loop exhausts both turns without ever returning final text, sets stop_reason to max_turn_exhaustion around line 1431-1432, and raises OllamaHarnessError with message "max-turn exhaustion before final assistant text" -- a different message than the test's regex expects.
- Ran the focused test for test_tool_loop_rejects_malformed_tool_arguments directly: it FAILED with an AssertionError, expected regex "arguments string must be JSON", actual message "max-turn exhaustion before final assistant text" -- an exact live reproduction of the claimed defect.
- Ran the complete module: 1 failed, 76 passed -- confirms exactly one stale assertion, matching the proposal's framing of "one stale affected-module Ollama assertion."
- Ran the dedicated resilience module test_shim_toolcall_arg_resilience.py: 4 passed, including test_ollama_harness_malformed_json_arguments_is_recoverable, which already independently proves the corrected two-turn behavior, malformed call then correlated ERROR tool result then recovered final text, for the Ollama shim. This confirms the underlying defect is already test-covered and only the stale expectation in the older file is outstanding.
- Confirmed WI-5471's own declared target paths, in both its first and latest bridge versions, list only scripts/cloud_harness_base.py, scripts/ollama_harness.py, and platform_tests/scripts/test_shim_toolcall_arg_resilience.py -- platform_tests/scripts/test_ollama_harness.py was never in WI-5471's authorized scope, corroborating the proposal's claim that the implementation-start gate correctly blocked editing it under WI-5471.
- Confirmed via git status that the two source files are modified, dirty, carrying WI-5471's uncommitted fix, the resilience test file is untracked, but platform_tests/scripts/test_ollama_harness.py is clean with no local modifications -- confirming WI-5550's sole target file is a fresh, uncontested edit surface with no risk of colliding with WI-5471's in-flight uncommitted bytes.

Conclusion: the defect claim is accurate and precisely characterized, the dedicated resilience coverage for the underlying behavior already exists and passes, and the proposed remediation, replacing the one stale assertion with a deterministic two-turn regression matching the already-proven pattern, is the correct, minimal, and only outstanding fix.

## Project Authorization / Work Item / Fast-Lane Eligibility Verification

Independently queried MemBase, not the proposal's prose, via KnowledgeDB and direct SQL against groundtruth.db:

- PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING: status active, project_id PROJECT-GTKB-RELIABILITY-FIXES, allowed_mutation_classes include source, test_addition, and hook_upgrade; forbidden_operations are deploy, git_push_force, and spec_deletion. The proposal's mutation, one test-file edit, is within allowed_mutation_classes and touches none of forbidden_operations.
- WI-5550: exists, resolution_status open, stage backlogged, priority P0, promoted from an initial P3 at version 1 to P0 at version 2 with change_reason describing reconciling an exact duplicate discovery and promoting the acceptance-blocking test contract -- a legitimate priority escalation, not a data-integrity problem. Origin is defect, project_name is PROJECT-GTKB-RELIABILITY-FIXES, source_test_id is TEST-11630.
- TEST-11630: exists, titled "Affected Ollama suite enforces recoverable malformed-argument contract", with an expected_outcome that matches the proposal's acceptance criteria in substance: correlated ERROR tool result, corrected next turn succeeds, no immediate-abort regression.
- PROJECT-GTKB-RELIABILITY-FIXES: active project, matches the PAUTH's project_id.
- All 13 cited Specification Links IDs independently confirmed to exist live in MemBase with matching titles; none fabricated or missing.
- GOV-RELIABILITY-FAST-LANE-001 eligibility, all four required, independently re-checked against WI-5550 rather than assumed from the WI-5471 precedent: origin is defect, pass; no new public API, CLI surface, or behavior beyond removing the defect, pass, since this is a test-only change with zero source bytes touched, strictly narrower than WI-5471's own already-approved scope; no new or revised requirement or specification needed, pass, since the Requirement Sufficiency section correctly classifies as sufficient per the mechanical pattern used by the implementation-authorization script, independently confirmed to match the proposal's exact wording; and small, single-concern, one file, pass, since target_paths is a single-element list naming one test file and the change replaces one named test function.

All four criteria independently confirmed met; the fast-lane classification is legitimate.

## Root Boundary / Target Path Verification

- The sole target path, platform_tests/scripts/test_ollama_harness.py, resolves under the project root with no out-of-root dependency, matching the In-Root Placement Evidence section's claim.
- Confirmed clean via git status short, as described in Independent Technical Verification above.

## Backlog Conflict Check

Queried open work items and live actionable bridge threads for overlap:

- WI-5581, titled "Align legacy Ollama malformed-tool-argument test with recoverable parser contract" and linked to TEST-11628, was an independently-discovered duplicate of this exact defect, created 2026-07-18T19:30:30Z and correctly resolved 23 minutes later. Its change_reason states the duplicate was resolved in favor of the earlier exact carrier WI-5550 while preserving the linked-test audit trail, and its status_detail confirms implementation and bridge routing continue only through WI-5550 to avoid competing ownership of the shared test file. No competing bridge thread was ever filed for WI-5581; WI-5550 is confirmed as the sole canonical carrier. This is disclosed as governance evidence of good hygiene, not a defect.
- The live, unreviewed NEW proposal gtkb-wi5542-ollama-publisher-envelope-recovery declares target paths that include scripts/ollama_harness.py and platform_tests/scripts/test_ollama_harness.py -- a file-level overlap with this proposal on the same test module. Read in full: WI-5542's scope is Ollama-D publisher-only-recovery envelope validation, a materially different concern from the malformed-tool-argument test contract, and it would add new tests for that behavior rather than touch test_tool_loop_rejects_malformed_tool_arguments. Neither proposal is implemented or claimed; the shared file is currently clean. This is a same-file, different-function overlap, not a duplication of effort, consistent with the precedent already accepted in the WI-5471 GO verdict's own Backlog Conflict Check, which found two adjacent but non-conflicting work items touching the same file. Whichever of WI-5550 or WI-5542 implements second will encounter the other's committed bytes and must rebase against fresh state; the implementation-start gate's dirty-file and foreign-byte detection already fails closed on exactly this case, so no additional owner action is needed now. Noted for the record, not a blocker.
- No other open work item or live actionable bridge thread references the specific stale test function by name, confirmed via a targeted search across every bridge markdown file; only WI-5471's disclosure and this WI-5550 thread match.

## Non-Blocking Observations

1. The proposal's header declares implementation_scope as source, but the change is test-only: the single target path is a test file, the narrative repeatedly states this is a test-only correction, and the recommended commit type is feat for a test replacement. A label of test, or test combined with source, would more accurately match sibling proposals' convention such as WI-5471's own source-and-test label. This is cosmetic: the implementation-start target-paths preflight script only branches on this field to detect the string design-only for its zero-target-paths bypass, which does not apply here since target_paths is non-empty. Confirmed this mislabeling has no mechanical gating effect. Recommend Prime correct the label in the eventual implementation report for hygiene, not as a proposal-review blocker.
2. The proposal's Proposed Scope commits to keeping an affected-module regression in test_ollama_harness.py, replacing the stale function, rather than deleting it as redundant with test_shim_toolcall_arg_resilience.py -- one of the two options the WI-5550 description itself allows. This is a reasonable design choice, module-level coherence for the primary harness suite versus the dedicated cross-shim resilience file, and is fully compliant with TEST-11630's expected outcome either way. The post-implementation verifier should confirm whichever concrete test shape was implemented satisfies the requirement that an invalid JSON tool call returns a correlated ERROR tool result, the corrected next provider turn completes successfully, and the worker does not regress to immediate abort.

## Specification Links (carried forward)

- GOV-RELIABILITY-FAST-LANE-001
- GOV-FILE-BRIDGE-AUTHORITY-001
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001
- DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001
- SPEC-AUQ-POLICY-ENGINE-001
- ADR-ISOLATION-APPLICATION-PLACEMENT-001
- GOV-STANDING-BACKLOG-001
- ADR-CODEX-HOOK-PARITY-FALLBACK-001
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001
- DCL-OLLAMA-TOOL-PARITY-GATE-001

## Prior Deliberations

- No prior deliberations found for this specific stale-test-contract defect; see Deliberation Archive Check above. WI-5550 originates same-day directly from the WI-5471 implementation cycle's own disclosed out-of-scope finding, not a re-litigated prior decision.

## Commands Executed

- Enumerated bridge thread versions for this document; only one version existed on disk.
- Checked the live bridge state-report and the per-document JSON status twice, once before deep review and once immediately before writing, to confirm continued actionability with no collision.
- Ran the focused pytest test for test_tool_loop_rejects_malformed_tool_arguments directly: live failure reproduction.
- Ran the complete test_ollama_harness.py module: 1 failed, 76 passed.
- Ran the dedicated test_shim_toolcall_arg_resilience.py module: 4 passed.
- Read scripts/ollama_harness.py lines 1120 through 1480 covering _tool_call_parts and run_tool_loop.
- Read both the first and latest versions of the WI-5471 bridge thread for target_paths and current status.
- Checked git status for the four candidate source and test files, plus git status for the branch and the latest commit.
- Queried the work_items table directly for WI-5550's full version history.
- Queried the tests table for TEST-11630.
- Queried the project_authorizations table directly for the standing PAUTH.
- Queried the specifications table directly for all 13 cited spec IDs to confirm existence and matching titles.
- Listed open work items filtered for overlap with the target test file; found only WI-5550 open, with WI-5581 already resolved.
- Queried the full version history for WI-5581 directly, confirming the duplicate-reconciliation evidence.
- Searched every bridge markdown file for the literal stale test function name; only WI-5471 and WI-5550 matched.
- Read the WI-5542 proposal in full to assess the adjacent-file overlap.
- Ran the bridge applicability preflight script for this document: preflight passed true.
- Ran the ADR/DCL clause preflight script for this document, confirming exit code 0 via a follow-up PowerShell check.
- Confirmed the bridge writer module compiles cleanly at review time, with no SyntaxError present.
- Ran four distinct semantic deliberation searches, described above under Deliberation Archive Check.
- Parsed the JSON-fenced disposition block from the proposal using Python's json module and confirmed it is well-formed.
- Acquired and refreshed a work-intent claim for this thread for the duration of this review session.

## Recommended Next Step

Prime Builder proceeds with implementation per the approved scope: open the implementation-start authorization packet for this bridge document, replace test_tool_loop_rejects_malformed_tool_arguments with the deterministic two-turn regression, run the standard lint and format checks on the changed file, rerun the complete test_ollama_harness.py and test_shim_toolcall_arg_resilience.py modules, then file the post-implementation report carrying forward this thread's linked specifications and a spec-to-test mapping to TEST-11630.

## Owner Action Required

None. This is a fast-lane-eligible, test-only fix already covered by the standing project authorization; no additional owner approval is required before implementation per GOV-RELIABILITY-FAST-LANE-001.

---

Copyright 2026 Remaker Digital, a DBA of VanDusen and Palmeter, LLC. All rights reserved.
