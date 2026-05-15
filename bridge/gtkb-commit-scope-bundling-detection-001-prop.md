NEW

# Implementation Proposal - Pre-Commit Commit-Scope-Bundling Detection (GTKB-COMMIT-SCOPE-BUNDLING-DETECTION-001)

bridge_kind: implementation_proposal
Document: gtkb-commit-scope-bundling-detection-001-prop
Version: 001
Author: Prime Builder (Claude, harness B)
Date: 2026-05-14 UTC
Session: S350

Project Authorization: PAUTH-PROJECT-GTKB-GOVERNANCE-HARDENING-GOVERNANCE-HARDENING-BATCH
Project: PROJECT-GTKB-GOVERNANCE-HARDENING
Work Item: GTKB-COMMIT-SCOPE-BUNDLING-DETECTION-001

target_paths: [".git/hooks/pre-commit", "scripts/commit_scope_bundling_check.py", "tests/scripts/test_commit_scope_bundling_check.py"]

This NEW proposal adds a pre-commit predicate that detects cross-scope bundling via mismatched approval packets. Observed at S344 (commit 5611dc44 bundled DELIB-S344 scope work with unrelated content without separate approval packets).

## Claim

A pre-commit script scans the staged file set, identifies files that imply distinct authorization scopes (e.g., spec mutations vs. hook changes vs. proposal authoring), checks for an approval-packet referenced in the commit message OR an active implementation-authorization packet covering ALL staged paths, and refuses commit if scopes diverge.

## In-Root Placement Evidence

All target paths in-root. `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` satisfied.

## Specification Links

- `GOV-ARTIFACT-APPROVAL-001` - approval-packet scope enforcement.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - protected behavior.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge protocol.
- `SPEC-AUQ-POLICY-ENGINE-001` - policy engine surface.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - in-root only.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - spec linkage.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - spec-to-test mapping.
- `GOV-STANDING-BACKLOG-001` - WI tracked.
- `DELIB-S350-BATCH4-FOUR-PROJECT-AUTHORIZATIONS` - owner-decision evidence.

## Prior Deliberations

- `DELIB-S350-BATCH4-FOUR-PROJECT-AUTHORIZATIONS` - batch-4 authorization.

## Owner Decisions / Input

- 2026-05-14 UTC, S350+: owner approved GTKB-GOVERNANCE-HARDENING including this WI.

## Requirement Sufficiency

Existing requirements sufficient.

## Clause Scope Clarification (Not a Bulk Operation)

Not a bulk operation. One WI; member of PROJECT-GTKB-GOVERNANCE-HARDENING per `formal-artifact-approval` packet `.groundtruth/formal-artifact-approvals/2026-05-14-batch4-four-project-authorizations.json`. Review-packet inventory: IP-1 (check script) + IP-2 (hook) + IP-3 (tests) single thread.

## Bridge INDEX Update Evidence

NEW filed; new top entry prepended.

## Proposed Scope

### IP-1: commit_scope_bundling_check.py

CLI: `python scripts/commit_scope_bundling_check.py --staged-files <list>`.

Logic:
1. For each staged path, classify by scope using PATH_TOKEN_RE-like prefix matching: `bridge/`, `.groundtruth/formal-artifact-approvals/`, `scripts/`, `.claude/hooks/`, `groundtruth-kb/src/`, etc.
2. Compute set of unique scope classes.
3. If multiple scopes:
   - Check commit message for a `Bundle-scope-acknowledged: <reason>` line.
   - Check `.gtkb-state/implementation-authorizations/current.json` for a packet covering all changed paths.
   - If neither, exit non-zero with a per-scope diagnostic.

### IP-2: Pre-commit hook integration

Register at `.git/hooks/pre-commit` (chmod +x). Calls the script with `git diff --cached --name-only`. Owner can `git commit --no-verify` to bypass when intentional.

### IP-3: Tests

Test fixtures simulate various staged-file scenarios.

## Specification-Derived Verification Plan

| Behavior | Test |
|---|---|
| Single-scope commit allowed | `test_single_scope_commit_allowed` |
| Multi-scope commit blocked without acknowledgement | `test_multi_scope_blocked_without_ack` |
| Multi-scope commit allowed with Bundle-scope-acknowledged line | `test_multi_scope_allowed_with_ack` |
| Multi-scope commit allowed with covering auth packet | `test_multi_scope_allowed_with_packet` |
| Diagnostic enumerates scope per file | `test_diagnostic_enumerates_per_file` |
| --no-verify bypass works | `test_bypass_with_no_verify` |

Run: `python -m pytest tests/scripts/test_commit_scope_bundling_check.py -v`.

## Acceptance Criteria

- IP-1, IP-2, IP-3 landed; 6 tests PASS.
- Both preflights PASS.

## Risks / Rollback

- Risk: legitimate refactors that touch multiple scopes need acknowledgement annotation; friction concern. Mitigation: `Bundle-scope-acknowledged:` line is a documented escape valve.
- Risk: scope classification too coarse or too fine. Mitigation: post-impl evaluation against last 10 commits.
- Rollback: remove hook installation; script stays available.

## Recommended Commit Type

`feat` - new pre-commit governance. ~80 LOC.
