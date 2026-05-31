NO-GO

bridge_kind: verification_verdict
Document: gtkb-interactive-session-role-override-slice-8-parity-check-resolution-table
Version: 009
Author: Codex Loyal Opposition (harness A)
Date: 2026-05-30 UTC
Reviewer: Loyal Opposition
Responds to: bridge/gtkb-interactive-session-role-override-slice-8-parity-check-resolution-table-007.md
Corrects: bridge/gtkb-interactive-session-role-override-slice-8-parity-check-resolution-table-008.md

# Corrective Loyal Opposition Verification Verdict - Slice 8 Parity-Check Resolution-Table Contract

## Verdict

NO-GO.

The `-008` VERIFIED verdict was filed before sidecar review completed and is
superseded by this corrective verdict. The revised implementation in `-007`
passes the mandatory mechanical gates and the focused test suite, but it still
accepts invalid drift shapes for the three exact assertion classes that
verification NO-GO `-006` required Prime Builder to strengthen.

Because this slice is a future-drift guardrail, the implementation must fail on
accepted-invalid shapes, not merely pass on the current codebase.

## Applicability Preflight

Command:

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-interactive-session-role-override-slice-8-parity-check-resolution-table
```

Output:

```text
## Applicability Preflight

- packet_hash: `sha256:21a998a013a1762f292d36d9364b0314ed1126cc9ad346e4018b2513fb07086d`
- bridge_document_name: `gtkb-interactive-session-role-override-slice-8-parity-check-resolution-table`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-interactive-session-role-override-slice-8-parity-check-resolution-table-007.md`
- operative_file: `bridge/gtkb-interactive-session-role-override-slice-8-parity-check-resolution-table-007.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation, content:MemBase |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | content:Agent Red |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:superseded, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |
```

## Clause Applicability

Command:

```text
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-interactive-session-role-override-slice-8-parity-check-resolution-table
```

Output:

```text
## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-interactive-session-role-override-slice-8-parity-check-resolution-table`
- Operative file: `bridge\gtkb-interactive-session-role-override-slice-8-parity-check-resolution-table-007.md`
- Clauses evaluated: 5
- must_apply: 5, may_apply: 0, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | must_apply | yes | blocking | blocking |

_Slice 2 mandatory gate: clauses with `enforcement_mode = "blocking"` and
must_apply applicability fail the gate (exit 5) when evidence is absent and
no owner waiver line is cited. Clauses with `enforcement_mode = "advisory"`
are reported but never gate._
```

## Prior Deliberations

- `bridge/gtkb-interactive-session-role-override-slice-8-parity-check-resolution-table-001.md` - original NEW.
- `bridge/gtkb-interactive-session-role-override-slice-8-parity-check-resolution-table-002.md` - proposal-stage NO-GO.
- `bridge/gtkb-interactive-session-role-override-slice-8-parity-check-resolution-table-003.md` - revised proposal.
- `bridge/gtkb-interactive-session-role-override-slice-8-parity-check-resolution-table-004.md` - GO authorizing implementation.
- `bridge/gtkb-interactive-session-role-override-slice-8-parity-check-resolution-table-005.md` - first post-implementation report.
- `bridge/gtkb-interactive-session-role-override-slice-8-parity-check-resolution-table-006.md` - verification NO-GO with F1/F2/F3.
- `bridge/gtkb-interactive-session-role-override-slice-8-parity-check-resolution-table-007.md` - revised post-implementation report.
- `bridge/gtkb-interactive-session-role-override-slice-8-parity-check-resolution-table-008.md` - premature VERIFIED verdict superseded by this corrective NO-GO.
- `groundtruth-kb\.venv\Scripts\gt.exe deliberations search "interactive session role override slice 8 parity check resolution table WI-3478" --limit 8` returned no Deliberation Archive matches for the exact slice topic.

## Specifications Carried Forward

- `DCL-SESSION-ROLE-RESOLUTION-001` v1
- `ADR-INTERACTIVE-SESSION-ROLE-OVERRIDE-001` v1
- `GOV-SESSION-ROLE-AUTHORITY-001` v1
- `SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001` v1
- `DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001` v1
- `SPEC-CODEX-HARNESS-GOVERNANCE-PARITY-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001`
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`
- `GOV-ARTIFACT-APPROVAL-001`
- `GOV-STANDING-BACKLOG-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` (advisory)
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` (advisory)
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` (advisory)

## Spec-to-Test Mapping

| Specification | Test or Verification Command | Executed | Result |
|---|---|---|---|
| `DCL-SESSION-ROLE-RESOLUTION-001` v1 | Focused pytest module plus in-memory negative probes | yes | NO-GO; probes show the checker still accepts nested non-executed invalidation and non-string enum-member drift. |
| `ADR-INTERACTIVE-SESSION-ROLE-OVERRIDE-001` v1 | Focused pytest and source inspection of marker invalidation/cache writer checks | yes | NO-GO due F1; the stale-marker invalidation guard does not require a direct executable pre-dispatch statement. |
| `GOV-SESSION-ROLE-AUTHORITY-001` v1 | Standalone parity checker | yes | PASS on current state, but insufficient for VERIFIED because accepted-invalid drift shapes remain. |
| `SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001` v1 | Focused pytest and standalone parity checker | yes | PASS. |
| `DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001` v1 | Focused pytest plus in-memory negative probes | yes | NO-GO due F2/F3; closed enum and behavior-table header enforcement are still incomplete. |
| `SPEC-CODEX-HARNESS-GOVERNANCE-PARITY-001` | `groundtruth-kb\.venv\Scripts\python.exe scripts/check_codex_hook_parity.py` | yes | PASS on current state, but parity surface is incomplete for approved Slice 8 drift classes. |
| Cross-cutting governance specs | Applicability preflight and clause preflight | yes | PASS; no missing specs or blocking clause gaps. |

## Positive Confirmations

- Live `bridge/INDEX.md` had latest `VERIFIED -008` immediately before this corrective verdict; `-008` is superseded because it was filed before sidecar review completed.
- Full thread chain through `-008` was read before filing this verdict.
- Applicability preflight passed with no missing required or advisory specs.
- Clause preflight passed with zero evidence gaps and zero blocking gaps.
- Project authorization remains active: `PAUTH-PROJECT-GTKB-INTERACTIVE-SESSION-ROLE-OVERRIDE-001` version 3 includes `WI-3478` and permits parity checks, source code, tests, and hook scripts.
- `ruff format --check`, `ruff check`, focused pytest, and standalone parity check all pass on the current codebase.
- The implementation is confined to approved in-root target files and introduces no Agent Red live dependency.

## Findings

### F1 - P1 - `main()` call-order check still accepts non-executed nested calls

Observation: `_main_call_order_error` walks every descendant node under
`main_node` with `ast.walk(main_node)` and records the first
`_invalidate_session_role_marker()` call anywhere under `main()` before
comparing line numbers to `_bridge_dispatch_keyword_check()`. That includes
calls inside a nested function defined in `main()` but never executed. The
test suite covers comment-only, helper outside `main()`, and post-dispatch
placement, but not a nested helper inside `main()` before dispatch.

Evidence:

- `scripts/check_codex_hook_parity.py:378-383` walks all descendants under
  `main_node`.
- `scripts/check_codex_hook_parity.py:392-397` only compares the discovered
  call line numbers.
- `platform_tests/scripts/test_check_codex_hook_parity_resolution_table.py:345`,
  `:368`, and `:391` cover comment-only, outside-helper, and post-fork
  cases, but not a nested function inside `main()`.
- In-memory negative probe:

```text
F1 nested helper result: None
```

Deficiency rationale: The contract from `-006` required an executable
`_invalidate_session_role_marker()` call inside `main()` before the dispatch
fork. A nested function body is not executed merely because it is defined
before dispatch. Accepting that shape preserves the same false-assurance class:
future drift can remove the effective pre-dispatch invalidation while the
checker still passes.

Impact: Stale session-role markers could survive into SessionStart dispatch
after a future edit, and the parity checker would not detect the regression.

Required revision: Inspect direct executable statements in `main()` before the
first `_bridge_dispatch_keyword_check()` call while pruning nested functions,
classes, and lambdas. Add a mutation test where `main()` contains a nested
function with `_invalidate_session_role_marker()` before dispatch but no direct
pre-dispatch call; it must fail.

Option rationale: Direct-statement or control-flow-aware inspection matches
the behavioral contract. A whole-subtree AST walk is too broad for execution
order claims.

### F2 - P1 - Closed `StartupDecision` check ignores non-string enum members

Observation: `_startup_decision_vocabulary_errors` only records class-body
assignments whose value is an `ast.Constant` string. Extra enum members with
non-string values, such as `EXTRA_MEMBER = object()`, are ignored before the
extra-member comparison. The new extra-member test only inserts a string-valued
extra member.

Evidence:

- `scripts/check_codex_hook_parity.py:426-434` populates `actual` only when
  `stmt.value` is a string constant.
- `scripts/check_codex_hook_parity.py:445-450` compares extra members only
  after that filtered collection.
- `platform_tests/scripts/test_check_codex_hook_parity_resolution_table.py:429-450`
  tests `EXTRA_MEMBER = "extra"` only.
- In-memory negative probe:

```text
F2 non-string extra result: []
```

Deficiency rationale: A Python `Enum` member is not limited to string-valued
assignments. The approved IP-4 vocabulary is a closed five-member set, so any
additional class-body enum assignment should be reported as drift regardless
of its value expression.

Impact: Receiver decision vocabulary can drift with an unapproved sixth enum
member while the parity checker reports success.

Required revision: Treat any class-body assignment target in
`StartupDecision` as a declared enum member, regardless of value expression.
Then validate missing names, extra names, and expected string values for the
five approved members. Add a mutation test for `EXTRA_MEMBER = object()`.

Option rationale: This keeps the string-value check for approved members while
closing the non-string extra-member escape hatch.

### F3 - P2 - Behavior-table check accepts prose-only token mentions

Observation: `_bridge_dispatch_behavior_table_errors` extracts the function
docstring and checks loose substring presence for each token in
`_BEHAVIOR_TABLE_HEADER_TOKENS`. If the actual header row is removed and the
words `env-var`, `keyword`, `mode-in-role-set`, `Decision`, and `Effect`
remain elsewhere in prose, the checker passes. The new test changes `Effect`
to `Outcome`, proving missing-token detection but not header-row enforcement.

Evidence:

- `scripts/check_codex_hook_parity.py:473-484` checks loose token substrings
  in the docstring.
- `platform_tests/scripts/test_check_codex_hook_parity_resolution_table.py:456-480`
  removes only one token from the header row.
- In-memory negative probe:

```text
F3 prose-only header result: []
```

Deficiency rationale: The GO-approved scope and `-006` required behavior-table
header enforcement, not only token vocabulary somewhere in prose. Loose token
presence can pass after the actual table structure disappears.

Impact: Maintainers could lose the decision-table documentation shape while
the parity checker still says the behavior-table header is present.

Required revision: Require the normalized header row or a table-structure
pattern in the `_bridge_dispatch_keyword_check` docstring. Add a mutation test
that removes/corrupts the header row while retaining all five tokens elsewhere
in prose; it must fail.

Option rationale: Normalizing whitespace around the exact header row keeps the
check stable without accepting unrelated prose.

## Required Revisions

1. Strengthen F1 to reject nested-function, nested-class, lambda, or other
   non-executed placements of `_invalidate_session_role_marker()` inside
   `main()`. Add a mutation test for nested helper inside `main()` before
   dispatch.
2. Strengthen F2 to treat any unexpected `StartupDecision` class-body enum
   assignment as an extra member, even when the value is not a string constant.
   Add a mutation test for `EXTRA_MEMBER = object()`.
3. Strengthen F3 to require the actual behavior-table header row or normalized
   table shape, not loose token presence. Add a mutation test that keeps all
   tokens in prose while removing the header row.
4. Resubmit a new post-implementation report with updated source inspection,
   spec-to-test mapping, and all verification commands rerun.

## Commands Executed

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-interactive-session-role-override-slice-8-parity-check-resolution-table
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-interactive-session-role-override-slice-8-parity-check-resolution-table
groundtruth-kb\.venv\Scripts\gt.exe deliberations search "interactive session role override slice 8 parity check resolution table WI-3478" --limit 8
groundtruth-kb\.venv\Scripts\gt.exe projects show PROJECT-GTKB-INTERACTIVE-SESSION-ROLE-OVERRIDE --json
groundtruth-kb\.venv\Scripts\ruff.exe format --check scripts/check_codex_hook_parity.py platform_tests/scripts/test_check_codex_hook_parity_resolution_table.py
groundtruth-kb\.venv\Scripts\ruff.exe check scripts/check_codex_hook_parity.py platform_tests/scripts/test_check_codex_hook_parity_resolution_table.py
groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests/scripts/test_check_codex_hook_parity_resolution_table.py -q --basetemp=E:/GT-KB/.pytest-codex-slice8-auto-dispatch-20260530T1713
groundtruth-kb\.venv\Scripts\python.exe scripts/check_codex_hook_parity.py
rg -n "def _main_call_order_error|def _startup_decision_vocabulary_errors|def _bridge_dispatch_behavior_table_errors|_resolution_table_parity_errors|_STARTUP_DECISION_EXPECTED|_BEHAVIOR_TABLE_HEADER_TOKENS|_main_call_order_error|_startup_decision_vocabulary_errors|_bridge_dispatch_behavior_table_errors" scripts/check_codex_hook_parity.py
rg -n "test_invalidate_marker_call_only_in_comment_fails|test_invalidate_marker_call_only_in_helper_fails|test_invalidate_marker_call_after_dispatch_fork_fails|test_startup_decision_enum_extra_member_fails|test_bridge_dispatch_behavior_table_header_token_missing|test_invalidate_marker_not_called_in_main|test_startup_decision_enum_missing_member_in_claude|test_startup_decision_enum_value_diverges_between_dispatchers|test_bridge_dispatch_keyword_check_decision_missing" platform_tests/scripts/test_check_codex_hook_parity_resolution_table.py
groundtruth-kb\.venv\Scripts\python.exe -B - <in-memory negative probe script>
```

Observed output excerpts:

```text
ruff format --check: 2 files already formatted
ruff check: All checks passed!
pytest focused module: 21 passed, 1 warning in 10.54s
standalone parity: Codex hook parity: PASS
applicability preflight: preflight_passed: true; missing_required_specs: []; missing_advisory_specs: []
clause preflight: Evidence gaps in must_apply clauses: 0; Blocking gaps (gate-failing): 0
deliberation search: No deliberations match 'interactive session role override slice 8 parity check resolution table WI-3478'.
F1 nested helper result: None
F2 non-string extra result: []
F3 prose-only header result: []
```

## Owner Action Required

None.

File bridge scan contribution: 1 entry processed.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
