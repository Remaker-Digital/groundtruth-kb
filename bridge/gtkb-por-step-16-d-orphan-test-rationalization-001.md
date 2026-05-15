NEW

# Implementation Proposal - POR Step 16.D Orphan Test Rationalization (WORKLIST-POR-STEPS-16-D-16-E-SPEC-HYGIENE-REMEDIATION-16-A-B-C-COMPLETE)

bridge_kind: implementation_proposal
Document: gtkb-por-step-16-d-orphan-test-rationalization
Version: 001
Author: Prime Builder (Claude, harness B)
Date: 2026-05-15 UTC
Session: S350

Project Authorization: PAUTH-PROJECT-GTKB-SECURITY-PRIVACY-SECURITY-PRIVACY-BATCH-SPECS-LIGHT-INITIAL
Project: PROJECT-GTKB-SECURITY-PRIVACY
Work Item: WORKLIST-POR-STEPS-16-D-16-E-SPEC-HYGIENE-REMEDIATION-16-A-B-C-COMPLETE

target_paths: ["scripts/orphan_test_rationalization.py", "scripts/por_step_16_exit_verification.py", "tests/scripts/test_orphan_test_rationalization.py"]

This NEW proposal advances POR Steps 16.D-16.E spec hygiene remediation. Per WI description, 16.A/B/C are VERIFIED at `por-step16c-implemented-untested-remediation-004`. Remaining: **16.D** orphan test rationalization (~10,440 tests, largest sub-phase) + **16.E** exit verification (untested-spec count ≤ 6 + orphan-test count ≤ 100).

## Claim

Two-part advance: (1) orphan-test rationalization tooling — classify each orphan test into adopt/retire/migrate dispositions based on heuristics (test name → likely spec mapping, content → likely target); (2) exit-verification script that asserts the 16.E thresholds. Full disposition execution (10,440 tests is bulk-scale) follows in separate execution batches gated by owner approval.

## In-Root Placement Evidence

All target paths in-root. `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` satisfied.

## Specification Links

- `GOV-18` - assertion quality.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - test-to-spec mapping.
- `GOV-RELEASE-READINESS-GOVERNED-TESTING-001` - release readiness; orphan tests block readiness.
- `GOV-ARTIFACT-APPROVAL-001` - bulk-mutation governance applies.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge protocol.
- `SPEC-AUQ-POLICY-ENGINE-001` - policy engine.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - in-root only.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - spec linkage.
- `GOV-STANDING-BACKLOG-001` - WI tracked.
- `DELIB-S350-BATCH5-EIGHT-PROJECT-AUTHORIZATIONS` - owner-decision evidence.

## Prior Deliberations

- `DELIB-S350-BATCH5-EIGHT-PROJECT-AUTHORIZATIONS` - batch-5 authorization.
- `bridge/por-step16c-implemented-untested-remediation-004` - 16.A/B/C VERIFIED.

## Owner Decisions / Input

- 2026-05-15 UTC, S350+: owner approved GTKB-SECURITY-PRIVACY authorization including this WI.

## Requirement Sufficiency

Existing requirements sufficient. WI description specifies 16.D/16.E scope + 16.E numerical exit thresholds.

## Clause Scope Clarification (Bulk Operation w/ Inventory + Approval Packet)

This IS a bulk operation by scale (10,440 tests). Per `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS`, bulk evidence required:
- **Inventory**: 16.D rationalization tooling produces a per-test inventory file (`orphan_test_rationalization_<date>.jsonl`) with classification + suggested disposition for each.
- **Review packet**: this proposal IS the review packet. Owner reviews the inventory output before any actual execution batch.
- **Phase-deferred decision**: actual disposition application is Phase-deferred (separate per-batch bridges, each with explicit owner approval).
- **formal-artifact-approval**: applies to MemBase test-status mutations; covered per-batch.

Per `formal-artifact-approval` packet `.groundtruth/formal-artifact-approvals/2026-05-14-batch5-eight-project-authorizations.json`, WI is a member of PROJECT-GTKB-SECURITY-PRIVACY (note: WI is filed under PROJECT-GTKB-SECURITY-PRIVACY in the batch-5 authorization; the project authority covers POR spec hygiene work that the security/privacy lens scopes).

## Bridge INDEX Update Evidence

NEW filed; new top entry prepended.

## Proposed Scope

### IP-1: orphan_test_rationalization.py

`scripts/orphan_test_rationalization.py`:
1. Query MemBase for tests with no `spec_id` linkage (orphans).
2. For each, apply classification heuristics:
   - **adopt**: test name matches a known spec (per name-similarity scoring) → suggest spec_id binding.
   - **migrate**: test references a deprecated spec → suggest replacement.
   - **retire**: test references nothing meaningful + no recent runs → suggest retirement.
   - **review**: ambiguous → owner review needed.
3. Emit `.gtkb-state/orphan-test-rationalization/<date>.jsonl` with one classification per test.

CLI: `python scripts/orphan_test_rationalization.py [--out <path>]`. Read-only.

### IP-2: por_step_16_exit_verification.py

`scripts/por_step_16_exit_verification.py`:
- Query MemBase: count untested specs (specs with `status='implemented'` or `'verified'` but no linked tests).
- Query: count orphan tests (tests without `spec_id`).
- Compare against 16.E thresholds: untested ≤ 6, orphans ≤ 100.
- Exit 0 if PASS; non-zero with diagnostic if FAIL.

### IP-3: Tests

Tests verify classification heuristic output + exit-verification thresholds with fixture data.

## Specification-Derived Verification Plan

| Behavior | Test |
|---|---|
| Classifier "adopt" pattern works | `test_classifier_adopt_pattern` |
| Classifier "retire" pattern works | `test_classifier_retire_pattern` |
| Classifier "review" pattern works | `test_classifier_ambiguous_review` |
| Inventory JSONL schema | `test_inventory_jsonl_schema` |
| Read-only (no DB writes) | `test_rationalization_no_db_writes` |
| Exit-verify thresholds correctly | `test_exit_verify_thresholds` |
| Exit-verify FAIL diagnostic clear | `test_exit_verify_failure_diagnostic` |

Run: `python -m pytest tests/scripts/test_orphan_test_rationalization.py -v`.

## Acceptance Criteria

- IP-1, IP-2, IP-3 landed; 7 tests PASS.
- Inventory JSONL produced for current S350 state.
- Both preflights PASS.
- Per-test execution is Phase-deferred (separate bridge per batch).

## Risks / Rollback

- Risk: classifier heuristics get many cases wrong on 10,440 tests. Mitigation: per-test review is owner-gated; tooling is informational only.
- Risk: project-membership semantic (this WI under SECURITY-PRIVACY) may look unusual. Mitigation: SECURITY-PRIVACY project authorization is specs-light initial; this WI fits the POR spec hygiene scope.
- Rollback: remove scripts.

## Recommended Commit Type

`feat` - new audit + verification infrastructure. ~150 LOC + tests.
