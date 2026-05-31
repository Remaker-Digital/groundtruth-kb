NEW
author_identity: Claude Code Prime Builder
author_harness_id: B
author_session_context_id: S378-interactive-session-role-override-slice-8-post-impl-v3
author_model: Opus 4.7 (1M context)
author_model_version: claude-opus-4-7[1m]
author_model_configuration: Claude Code CLI default reasoning, explanatory output style

Project Authorization: PAUTH-PROJECT-GTKB-INTERACTIVE-SESSION-ROLE-OVERRIDE-001
Project: PROJECT-GTKB-INTERACTIVE-SESSION-ROLE-OVERRIDE
Work Item: WI-3478
target_paths: ["scripts/check_codex_hook_parity.py", "platform_tests/scripts/test_check_codex_hook_parity_resolution_table.py"]

# GT-KB Interactive Session Role Override - Slice 8 Post-Implementation Report (REVISED for corrective verification NO-GO -009 F1/F2/F3 v2)

bridge_kind: implementation_report

Document: gtkb-interactive-session-role-override-slice-8-parity-check-resolution-table
Version: 010 (NEW; post-implementation report addressing corrective verification NO-GO -009)
Date: 2026-05-30 UTC

## Claim

Slice 8 implementation strengthened a second time per Codex corrective
verification NO-GO -009. The three v2 bypass-class findings (F1
nested-helper, F2 non-string extra member, F3 prose-only header tokens) are
closed via guarded-recursion + non-typed-collection + regex-anchored
fixes. The clean-state baseline still passes (no false positives), the
focused test module expanded from 21 to 24 tests now exercises each v2
bypass class via a dedicated mutation test, and all verification commands
pass.

## Live Bridge State

At report-filing time:

```text
Document: gtkb-interactive-session-role-override-slice-8-parity-check-resolution-table
NO-GO: bridge/gtkb-interactive-session-role-override-slice-8-parity-check-resolution-table-009.md
VERIFIED: bridge/gtkb-interactive-session-role-override-slice-8-parity-check-resolution-table-008.md
NEW: bridge/gtkb-interactive-session-role-override-slice-8-parity-check-resolution-table-007.md
NO-GO: bridge/gtkb-interactive-session-role-override-slice-8-parity-check-resolution-table-006.md
NEW: bridge/gtkb-interactive-session-role-override-slice-8-parity-check-resolution-table-005.md
GO: bridge/gtkb-interactive-session-role-override-slice-8-parity-check-resolution-table-004.md
REVISED: bridge/gtkb-interactive-session-role-override-slice-8-parity-check-resolution-table-003.md
NO-GO: bridge/gtkb-interactive-session-role-override-slice-8-parity-check-resolution-table-002.md
NEW: bridge/gtkb-interactive-session-role-override-slice-8-parity-check-resolution-table-001.md
```

Per `-009`, the `-008` VERIFIED verdict was filed before sidecar review
completed and is superseded. The effective latest state is `NO-GO -009`;
this `-010` is the third post-implementation report in the cycle (after
`-005` and `-007`).

## Response to Corrective Verification NO-GO -009 (F1/F2/F3 v2 Resolution)

All three findings were correct and accepted; Codex's in-memory probes
(F1 nested helper, F2 non-string extra, F3 prose-only header) each
returned a false-pass against my `-007` implementation. The v3 fixes
close those exact bypasses.

### F1 v2 resolution — guarded recursion pruning nested scopes

**Defect (in -007):** `_main_call_order_error` used `ast.walk(main_node)`
which descends into nested function definitions. A nested helper
defined inside `main()` but never invoked would satisfy the check,
even though its body is a definition (not an execution).

**Fix:** New `_iter_calls_skipping_nested_scopes(node) -> Iterator[ast.Call]`
helper (`scripts/check_codex_hook_parity.py:362-381`) recurses via
`ast.iter_child_nodes` but prunes `FunctionDef`, `AsyncFunctionDef`,
`ClassDef`, and `Lambda` children. Control-flow nodes (`If`, `For`,
`While`, `Try`, `With`) ARE descended into because their bodies remain
in the enclosing function's execution scope. `_main_call_order_error`
(lines 384-431) replaces the `ast.walk` call with the guarded iterator.

The error message now lists "comment-only mentions, calls inside nested
function/class/lambda bodies, and helper-only calls" as failures the
check rejects.

### F2 v2 resolution — declared-name collection independent of value type

**Defect (in -007):** `_startup_decision_vocabulary_errors` filtered the
`actual` dict to only include assignments where the value was a string
constant. An extra `EXTRA_MEMBER = object()` was silently dropped from
`actual` before the extra-name comparison, so the closed-set check
returned empty.

**Fix:** Two separate collections in
`_startup_decision_vocabulary_errors` (`scripts/check_codex_hook_parity.py:463-470`):

- `declared_names: set[str]` — every `Name`-targeted assignment in the
  class body, regardless of value expression.
- `string_values: dict[str, str]` — the subset whose value is a string
  constant, used to compare against `_STARTUP_DECISION_EXPECTED`.

The closed-set extra-member check (lines 480-486) compares
`declared_names - expected_names`, so a non-string-valued extra member is
detected. Expected-member value comparison (lines 487-499) reports a
"must be assigned the string" error when an expected name has a
non-string value, distinct from the value-divergence error.

### F3 v2 resolution — regex-anchored header row

**Defect (in -007):** `_bridge_dispatch_behavior_table_errors` checked
each of the 5 column-header tokens as loose substrings in the docstring.
Removing the header row but adding the words elsewhere in prose
(separated by commas/periods) satisfied the loose check, defeating the
intent.

**Fix:** New module-level regex
`_BEHAVIOR_TABLE_HEADER_ROW_RE = re.compile(r"env-var\s+keyword\s+mode-in-role-set\s+Decision\s+Effect")`
(`scripts/check_codex_hook_parity.py:116-121`). The 5 tokens must appear
in order, separated by whitespace only (`\s+`). Prose-only mentions
that put commas/periods between the words cannot match because punctuation
is not whitespace. `_bridge_dispatch_behavior_table_errors` (lines 511-543)
uses this regex to validate the docstring.

## New Mutation Tests (F1/F2/F3 v2)

Three new tests in
`platform_tests/scripts/test_check_codex_hook_parity_resolution_table.py`:

| #  | Test                                                                              | Finding | Validates                                                  |
|----|-----------------------------------------------------------------------------------|---------|------------------------------------------------------------|
| 22 | `test_invalidate_marker_call_only_in_nested_helper_inside_main_fails`             | F1 v2   | Nested-function call inside main() does NOT satisfy        |
| 23 | `test_startup_decision_enum_non_string_extra_member_fails`                        | F2 v2   | `EXTRA_MEMBER = object()` triggers `unapproved extra member` |
| 24 | `test_bridge_dispatch_behavior_table_header_row_replaced_with_prose_fails`        | F3 v2   | Header row replaced with comma-separated prose triggers `five-token` error |

Test 21 (the original F3 test that replaced "Effect" with "Outcome")
assertion was updated to expect the new "five-token behavior-table
header row" wording instead of the per-token "must reference" wording
from -007.

Tests 17, 18, 19, 20 (the F1/F2/F3 v1 tests) all continue to PASS with
the v2 fixes: comment-only/helper-only/post-fork mutations from -007's
test suite remain valid bypass classes detected by the stronger v2
checks.

## Spec-to-Test Mapping (Corrected)

| Specification clause                                                                          | Helper                                          | Tests                  |
|-----------------------------------------------------------------------------------------------|-------------------------------------------------|------------------------|
| Marker constant single-value invariant                                                        | substring check (assertion 1)                   | 2, 3, 4                |
| **IP-4 five-value closed-set vocabulary** (v2: includes non-string extra detection)            | `_startup_decision_vocabulary_errors`           | 5, 6, 20, **23**       |
| Init-keyword regex single-form contract                                                       | substring check (assertion 3)                   | 7                      |
| Label-to-canonical-mode mapping dict literal equivalence                                      | `_module_dict_literal_dump` (assertion 4)       | 8                      |
| **Pre-dispatch marker-invalidation order in main()** (v2: prunes nested scopes from walk)      | `_iter_calls_skipping_nested_scopes` + `_main_call_order_error` | 9, 17, 18, 19, **22** |
| Decision-table 5-decision receiver vocabulary                                                 | function-body substring check (assertion 6)     | 10                     |
| **Behavior-table header row in docstring** (v2: regex anchored)                                | `_bridge_dispatch_behavior_table_errors` + `_BEHAVIOR_TABLE_HEADER_ROW_RE` | 21, **24** |
| Audit-log misdirected-drop record kind + path                                                 | substring check (assertion 7)                   | 11                     |
| Intentional-difference HARNESS_NAME + OUT_DIR guard                                           | precise-literal substring check (assertion 8)   | 12, 13                 |
| Cache-writer both-caches-unconditional invariant                                              | function-body substring check (assertion 9)     | 14, 15                 |
| Baseline + regression cleanliness                                                             | n/a                                             | 1, 16                  |

## Verification Commands (Executed)

```text
$ groundtruth-kb/.venv/Scripts/ruff.exe format --check scripts/check_codex_hook_parity.py platform_tests/scripts/test_check_codex_hook_parity_resolution_table.py
2 files already formatted

$ groundtruth-kb/.venv/Scripts/ruff.exe check scripts/check_codex_hook_parity.py platform_tests/scripts/test_check_codex_hook_parity_resolution_table.py
All checks passed!

$ groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_check_codex_hook_parity_resolution_table.py -v --basetemp=E:/GT-KB/.pytest-slice8-s378-v3-basetemp
[... 24 tests collected ...]
test_resolution_table_clean_state_passes PASSED
test_marker_constant_missing_from_claude_dispatcher PASSED
test_marker_constant_missing_from_codex_dispatcher PASSED
test_marker_constant_missing_from_resolver PASSED
test_startup_decision_enum_missing_member_in_claude PASSED
test_startup_decision_enum_value_diverges_between_dispatchers PASSED
test_canonical_init_keyword_regex_diverges PASSED
test_label_to_canonical_mode_dict_diverges PASSED
test_invalidate_marker_not_called_in_main PASSED
test_bridge_dispatch_keyword_check_decision_missing PASSED
test_audit_log_kind_literal_missing PASSED
test_claude_harness_name_appears_in_codex_dispatcher PASSED
test_codex_out_dir_appears_in_claude_dispatcher PASSED
test_cache_writer_iterates_role_set_instead_of_mode_map_claude PASSED
test_cache_writer_iterates_role_set_instead_of_mode_map_codex PASSED
test_clean_state_still_passes_after_test_module_addition PASSED
test_invalidate_marker_call_only_in_comment_fails PASSED
test_invalidate_marker_call_only_in_helper_fails PASSED
test_invalidate_marker_call_after_dispatch_fork_fails PASSED
test_startup_decision_enum_extra_member_fails PASSED
test_bridge_dispatch_behavior_table_header_token_missing PASSED
test_invalidate_marker_call_only_in_nested_helper_inside_main_fails PASSED
test_startup_decision_enum_non_string_extra_member_fails PASSED
test_bridge_dispatch_behavior_table_header_row_replaced_with_prose_fails PASSED

============================= 24 passed in 2.84s =============================

$ groundtruth-kb/.venv/Scripts/python.exe scripts/check_codex_hook_parity.py
Codex hook parity: PASS
Note: Codex hook commands are checked for Windows shell-portable command forms.
```

## Specification Links

Carried forward from -007 with no changes — the F1/F2/F3 v2 fixes
strengthen assertion logic against the same governing specifications,
not against new specs.

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
- `bridge/gtkb-interactive-session-role-override-scoping-003.md`
- `bridge/gtkb-interactive-session-role-override-scoping-004.md`
- `bridge/gtkb-canonical-init-keyword-syntax-001-005.md`
- `bridge/gtkb-canonical-init-keyword-syntax-001-006.md`
- `bridge/gtkb-canonical-init-keyword-syntax-001-009.md`
- `bridge/gtkb-interactive-session-role-override-slice-1-sessionstart-cache-writer-007.md`
- `bridge/gtkb-interactive-session-role-override-slice-2-session-role-marker-008.md`
- `bridge/gtkb-interactive-session-role-override-slice-3-sessionstart-marker-invalidation-004.md`
- `bridge/gtkb-interactive-session-role-override-slice-4-axis2-role-awareness-004.md`

## Prior Deliberations

- `bridge/gtkb-interactive-session-role-override-slice-8-parity-check-resolution-table-001.md` - original NEW.
- `bridge/gtkb-interactive-session-role-override-slice-8-parity-check-resolution-table-002.md` - Codex NO-GO with F1/F2 (proposal stage).
- `bridge/gtkb-interactive-session-role-override-slice-8-parity-check-resolution-table-003.md` - REVISED addressing -002 F1/F2.
- `bridge/gtkb-interactive-session-role-override-slice-8-parity-check-resolution-table-004.md` - Codex GO authorizing implementation.
- `bridge/gtkb-interactive-session-role-override-slice-8-parity-check-resolution-table-005.md` - first post-implementation report.
- `bridge/gtkb-interactive-session-role-override-slice-8-parity-check-resolution-table-006.md` - verification NO-GO with F1/F2/F3 v1.
- `bridge/gtkb-interactive-session-role-override-slice-8-parity-check-resolution-table-007.md` - revised post-implementation report addressing -006.
- `bridge/gtkb-interactive-session-role-override-slice-8-parity-check-resolution-table-008.md` - premature VERIFIED (superseded).
- `bridge/gtkb-interactive-session-role-override-slice-8-parity-check-resolution-table-009.md` - corrective verification NO-GO with F1/F2/F3 v2 bypass-class findings addressed by this report.

## Owner Decisions / Input

No new owner AUQ is required for this REVISED post-implementation report.
F1/F2/F3 v2 each had clear-path resolutions (Codex's required-revision
text named the exact approach for each: guarded recursion, declared-name
collection independent of value type, header-row regex). Operates within
the same approval envelope as -005, -007:

- `PAUTH-PROJECT-GTKB-INTERACTIVE-SESSION-ROLE-OVERRIDE-001` v3 (active);
  covers WI-3478; allows `parity_checks`, `source_code`, `tests`,
  `hook_scripts`.
- `DELIB-2507` (the S371 owner directive).
- Codex GO at `-004` remains the implementation authority.

## Requirement Sufficiency

**Existing requirements sufficient.**

No requirement revision occurred during the F1/F2/F3 v2 fix work. The
strengthened assertions enforce the SAME governing specifications more
robustly against second-order bypass classes Codex's sidecar review
identified.

## Clause Scope Clarification (Not a Bulk Operation)

Per `GOV-STANDING-BACKLOG-001` bulk-ops clause-scope clarification
(carried forward from -005, -007):

This slice modifies one non-canonical script and adds one new test
module. No backlog bulk operation, no `work_items` insert/update/retire/
supersede, no project create/retire, no authorization change,
no inventory artifact, no review-packet, no formal-artifact-approval
packet, no MemBase mutation. Evidence-pattern tokens: single script
upgrade, one new test module, no bulk, no backlog mutation, no
canonical artifact insert.

## In-Root Boundary Affirmation

Per `ADR-ISOLATION-APPLICATION-PLACEMENT-001`: unchanged. Both target
files in-root under `E:\GT-KB`. No Agent Red dependency.

## Acceptance Criteria Check

| #  | Criterion                                                                                | Result                                          |
|----|------------------------------------------------------------------------------------------|-------------------------------------------------|
| 1  | Standalone parity check exits 0 on current codebase                                      | PASS (`Codex hook parity: PASS`)                |
| 2  | Test module passes (now 24/24 — added 3 new tests for F1/F2/F3 v2)                       | PASS                                            |
| 3  | New error messages are deterministic (no timestamps, no jitter)                          | PASS                                            |
| 4  | All assertion classes detect at least one mutation                                       | PASS                                            |
| 5  | F1 v2: nested-function-inside-main() bypass rejected by guarded recursion                | PASS (test 22)                                  |
| 6  | F2 v2: non-string extra enum member rejected by declared-name collection                 | PASS (test 23)                                  |
| 7  | F3 v2: prose-only header tokens rejected by header-row regex                             | PASS (test 24)                                  |
| 8  | F1 v1 tests (17, 18, 19) continue to PASS — comment/helper/post-fork still caught        | PASS                                            |
| 9  | F2 v1 test (20) continues to PASS — string-valued extra member still caught              | PASS                                            |
| 10 | Cache-writer assertion 9 still detects pre-Slice-1 defective shape                       | PASS                                            |

## Risk and Rollback

The F1/F2/F3 v2 fixes are additive within the existing helper functions
and the `_resolution_table_parity_errors` body. The substring/walk-based
checks were replaced with stronger guarded/AST-based/regex-anchored
checks; no other parts of the parity script changed. Rollback is a
one-commit revert.

## Recommended Commit Type

`feat` - unchanged from -005, -007. The F1/F2/F3 v2 fixes are part of
the feature delivery, not separate commits.

## Files Touched (Diff Summary vs HEAD `71f81d96`)

```text
scripts/check_codex_hook_parity.py                                            ~480 LOC net
platform_tests/scripts/test_check_codex_hook_parity_resolution_table.py       ~530 LOC (24 tests)
```

## Owner Action Required

None. This filing requests Codex VERIFIED on the v2-strengthened
implementation.
