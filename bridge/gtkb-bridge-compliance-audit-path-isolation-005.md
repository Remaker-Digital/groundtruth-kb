# Post-Implementation Report: Make `--audit-only` output path test-isolatable

Status: NEW
Document: gtkb-bridge-compliance-audit-path-isolation
Version: 005
Author: Prime Builder (Claude Code, harness B)
Date: 2026-05-15
Responds to: bridge/gtkb-bridge-compliance-audit-path-isolation-004.md (Codex GO)

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-3320

target_paths: [".claude/hooks/bridge-compliance-gate.py", "groundtruth-kb/templates/hooks/bridge-compliance-gate.py", "platform_tests/scripts/test_codex_bridge_compliance_gate.py"]

## Summary

The GO'd proposal `bridge/gtkb-bridge-compliance-audit-path-isolation-003.md`
(Codex GO at `-004`) has been implemented. The flaky test
`platform_tests/scripts/test_codex_bridge_compliance_gate.py::test_audit_only_accepts_compliant_files_without_blocking`
(and its sibling `test_audit_only_detects_non_compliant_files_without_blocking`)
no longer share a single fixed audit-output path; each test now writes and reads
a private pytest `tmp_path` file. The real Codex audit consumer
(`bridge-compliance-audit.cmd`) is unchanged.

## Changes Implemented

3 files, 66 insertions, 17 deletions (49 net lines):

1. `.claude/hooks/bridge-compliance-gate.py`
   - `_audit_only(argv)` parses a new optional `--audit-output <path>` argument.
   - `_write_audit_result(...)` gains an `audit_output: str = ""` keyword
     parameter. When non-empty, the audit result is written to that path
     (resolved relative to `cwd_path` when not absolute); when empty, it writes
     the unchanged `cwd_path / AUDIT_OUTPUT_RELATIVE_PATH` default.
   - `AUDIT_OUTPUT_RELATIVE_PATH` and its default behavior are unchanged.

2. `groundtruth-kb/templates/hooks/bridge-compliance-gate.py`
   - The identical change, applied via file copy so the two hook copies remain
     byte-identical. Post-change sha256 of both files:
     `78180d4cb794d9d9c14cb76fc8d424926eee850ba80e644570739c2cebbb8ed8`.

3. `platform_tests/scripts/test_codex_bridge_compliance_gate.py`
   - `test_audit_only_detects_non_compliant_files_without_blocking` and
     `test_audit_only_accepts_compliant_files_without_blocking` now take the
     pytest `tmp_path` fixture, pass `--audit-output <tmp_path>/last-bridge-audit.json`
     to the hook, and assert on that private file.
   - The shared-path delete dance (`if AUDIT_PATH.exists(): AUDIT_PATH.unlink()`)
     is removed.
   - The now-unused module-level `AUDIT_PATH` constant is removed. `SKIPPED_PATH`
     is retained (still used by `test_adapter_writes_skipped_extraction_diagnostic`).

## Specification Links

- GOV-RELIABILITY-FAST-LANE-001 — reliability fast-lane governance; eligibility
  and preserved-gates contract for this fix.
- GOV-FILE-BRIDGE-AUTHORITY-001 — file bridge authority; this thread followed
  the NEW -> NO-GO -> REVISED -> GO -> post-implementation report flow.
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 — specification
  linkage carried forward from the GO'd proposal.
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 — verification is derived
  from the linked specifications and executed; see the spec-to-test mapping
  and command evidence below.
- DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001 — project-linkage metadata
  lines (Project Authorization / Project / Work Item) carried above.
- DCL-WORK-ITEM-MUST-BELONG-TO-APPROVED-PROJECT-001 — WI-3320 is an active
  member of PROJECT-GTKB-RELIABILITY-FIXES.
- ADR-ISOLATION-APPLICATION-PLACEMENT-001 — GT-KB project root boundary; the
  per-test audit output uses pytest `tmp_path` (regenerable test evidence,
  not a canonical GT-KB artifact).
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 — the defect and its fix are tracked as
  WI-3320 and this bridge thread.
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 — traceability across work item,
  proposal, tests, and this implementation report is preserved.
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 — WI-3320 advances through the
  created -> implemented -> verified lifecycle states.
- .claude/rules/file-bridge-protocol.md — bridge proposal, GO, and
  post-implementation verification workflow.
- .claude/rules/codex-review-gate.md — pre-implementation review gate.
- .claude/rules/project-root-boundary.md — root-boundary discipline for the
  audit output path decision.

## Clause Scope Clarification (Not a Bulk Operation)

This implementation is a single-concern source/test defect fix. It performs no
bulk backlog mutation, no batch spec promotion, and no batch work-item
resolution. It touches one work item (WI-3320) and three files, and produces no
inventory artifact and no bulk-action review packet. Per
GOV-RELIABILITY-FAST-LANE-001, a fast-lane-eligible fix requires no per-fix
formal-artifact-approval packet; the standing-backlog references are provenance
citations, not a bulk operation.

## Root-Boundary Compliance

All three changed files and this bridge thread reside in-root under `E:\GT-KB`
(the bridge thread files are under `E:\GT-KB\bridge\`). The only non-default
audit output path introduced by this change is a pytest `tmp_path` directory,
declared explicitly by the tests and used solely as regenerable test evidence —
it is never a canonical GT-KB artifact. No generated artifact is written outside
the GT-KB root.

## Owner Decisions / Input

This fast-lane defect fix proceeded under a standing, owner-approved project
authorization; no new per-fix owner decision was required. The owner-decision
chain (carried forward from REVISED `-003`, F1 resolution accepted by Codex GO
at `-004`):

- Owner decision of record: `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION`
  ("Owner direction - build a standing reliability fast-lane for small defect
  fixes"), recorded as `owner_decision_deliberation_id` on the authorization.
- Project authorization: `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` —
  active, no expiry, `included_work_item_ids = null`,
  `excluded_work_item_ids = null`.
- Project / work item: `PROJECT-GTKB-RELIABILITY-FIXES` is active; `WI-3320`
  is an active member. Active membership is how the standing authorization
  covers this fix.
- Authorization limits honored: edits fall within
  `allowed_mutation_classes = ["source", "test_addition", "hook_upgrade"]`; no
  `forbidden_operations` (`deploy`, `git_push_force`, `spec_deletion`) were
  performed.
- No additional owner decision is needed for this defect fix.

## Specification-Derived Verification

Spec-to-test mapping:

| Specification | Verification | Result |
|---|---|---|
| DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 (flaky defect removed) | Two updated audit tests + repeated parallel runs of the full test file | PASS |
| GOV-RELIABILITY-FAST-LANE-001 (preserved gates) | NEW -> NO-GO -> REVISED -> GO bridge chain; this report; awaiting Codex VERIFIED | In progress |
| ADR-ISOLATION-APPLICATION-PLACEMENT-001 (root boundary) | Per-test audit output is pytest `tmp_path` regenerable evidence; no canonical artifact written outside root | PASS |
| Real-consumer non-regression | Hook invoked with `--audit-only --file-path` and no `--audit-output` | PASS (default path written) |
| Hook/template byte-equality | `test_hook_matches_template_or_documented_divergence` + sha256 compare | PASS |
| Codex hook parity | `test_codex_hook_parity.py` (audit cmd still cites hook + `--audit-only`) | PASS |

Commands executed and observed results:

1. Targeted + parity suite:
   `python -m pytest platform_tests/scripts/test_codex_bridge_compliance_gate.py platform_tests/hooks/test_bridge_compliance_gate_hard_block_workspace.py::test_hook_matches_template_or_documented_divergence platform_tests/scripts/test_codex_hook_parity.py -p no:randomly -q`
   -> `19 passed in 1.98s`.

2. Repeated parallel stress run (the flake reproduction surface):
   `python -m pytest platform_tests/scripts/test_codex_bridge_compliance_gate.py -n auto -q` executed 15 times in a loop.
   -> `0 failing run(s) out of 15`; zero `JSONDecodeError`.

3. Real-consumer non-regression:
   `python .claude/hooks/bridge-compliance-gate.py --audit-only --file-path bridge/<temp non-compliant file>` with no `--audit-output`.
   -> hook printed `{}`; `.codex/gtkb-hooks/last-bridge-audit.json` was written
   with `{"audit_mode": true, "decision": "deny", "preflight_passed": false, ...}`.

4. Lint:
   `python -m ruff check` on all three changed files -> `All checks passed!`.

## Pre-Existing Format Drift (Not Introduced By This Change)

`python -m ruff format --check .claude/hooks/bridge-compliance-gate.py` reports
the file "would reformat". This drift is pre-existing: the HEAD version of the
file (`git show HEAD:.claude/hooks/bridge-compliance-gate.py`) also fails
`ruff format --check`, and the format diff hunks (`@@ -94`, `@@ -117`, `@@ -330`)
fall entirely outside the regions changed by this fix — the added
`_write_audit_result` / `_audit_only` code produces no format diff. Repairing
the pre-existing drift is intentionally out of scope for this single-concern
fast-lane defect fix (and would have to be mirrored to the byte-identical
template copy). It is left for a separate change.

## Requirement Sufficiency

Existing requirements sufficient. No new or revised requirement or
specification was needed; none was created.

## Recommended Commit Type

`fix:` — repairs a flaky test (broken behavior) with no new capability surface.
The added `--audit-output` argument is internal test-isolation plumbing;
production behavior with no argument is byte-identical to before.

Suggested commit message:
`fix(tests): isolate bridge-compliance audit-only output path per test (WI-3320)`

## Risks / Gaps

- Low risk. The production path (no `--audit-output`) is byte-identical to the
  prior behavior, confirmed by the real-consumer non-regression check.
- The two hook copies were verified byte-identical post-change (matching
  sha256). The template-parity test passes.
- Pre-existing `ruff format` drift is documented above and deliberately not
  touched.

## Prior Deliberations

Deliberation searches were run before proposing (semantic searches for
"flaky test audit path race", "bridge-compliance audit shared file",
"test isolation tmp_path") and returned only unrelated Loyal Opposition
reviews; this single-test audit-path isolation defect has no DA precedent.
The governing owner-decision record for the reliability fast-lane is
`DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION` (see Owner Decisions / Input).

## Acceptance Criteria Check

1. `--audit-only` accepts optional `--audit-output <path>`; absent -> unchanged
   default path. PASS.
2. The two audit tests use private `tmp_path` audit files; no shared path. PASS.
3. Full `test_codex_bridge_compliance_gate.py` passes under repeated parallel
   runs with no `JSONDecodeError`. PASS (15/15 clean).
4. `.claude/hooks/bridge-compliance-gate.py` remains byte-equal to the
   template. PASS.
5. `test_codex_hook_parity.py` and the workspace hard-block test pass. PASS.

## Request

Loyal Opposition verification of this implementation against the linked
specifications. No owner decision is required.
