NEW

# Implementation Proposal - Proposal-Standards Test-Claim Re-Run Verifier (Slice 2)

bridge_kind: prime_proposal
Document: gtkb-proposal-standards-test-claim-rerun-verifier
Version: 001
Author: Prime Builder (Claude, harness B)
Date: 2026-05-14 UTC
Session: S350

Project Authorization: PAUTH-PROJECT-GTKB-GOV-PROPOSAL-STANDARDS-PROPOSAL-STANDARDS-SLICES-2-3
Project: PROJECT-GTKB-GOV-PROPOSAL-STANDARDS
Work Item: GTKB-GOV-PROPOSAL-STANDARDS-SLICE2

target_paths: ["scripts/bridge_proposal_test_claim_verifier.py", "tests/scripts/test_bridge_proposal_test_claim_verifier.py", "platform_tests/scripts/test_bridge_proposal_test_claim_verifier.py"]

This NEW proposal lands GTKB-GOV-PROPOSAL-STANDARDS Slice 2: a verifier that parses `pytest` claims out of bridge proposals' Specification-Derived Verification Plan sections and re-runs them against the working tree to confirm the claimed outcomes match reality.

## Claim

Build a CLI: `python scripts/bridge_proposal_test_claim_verifier.py --bridge-id <id> [--strict]`. Parses test-claim tables/lines from the bridge content, locates referenced test files, runs `pytest --collect-only` (or `--no-header -q`) to verify the tests exist, and emits a per-claim PASS/MISSING report. `--strict` mode also runs the tests and compares observed outcomes to claimed.

## In-Root Placement Evidence

All target paths in-root. `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` satisfied.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge protocol; this verifier supports the review packet.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - proposal must cite specs; verifier supports test-side check.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - proposal must map specs to tests; verifier confirms tests exist.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - in-root only.
- `GOV-STANDING-BACKLOG-001` - GTKB-GOV-PROPOSAL-STANDARDS-SLICE2 tracked.
- `DELIB-S350-BATCH2-THREE-PROJECT-AUTHORIZATIONS` - owner-decision evidence.

## Prior Deliberations

- `DELIB-S350-BATCH2-THREE-PROJECT-AUTHORIZATIONS` - batch-2 authorization.
- `DELIB-S341-PROPOSAL-STANDARDS-S341` (if exists; otherwise the Slice 1 bridge VERIFIED record) - parent program rationale.

## Owner Decisions / Input

- 2026-05-14 UTC, S350+: owner AUQ "Authorize all 3 groups (7 WIs added)".

## Requirement Sufficiency

Existing requirements sufficient. GTKB-GOV-PROPOSAL-STANDARDS-SLICE2 description is the operative spec.

## Clause Scope Clarification (Not a Bulk Operation)

Not a bulk operation. One WI (Slice 2); member of PROJECT-GTKB-GOV-PROPOSAL-STANDARDS per `formal-artifact-approval` packet `.groundtruth/formal-artifact-approvals/2026-05-14-batch2-three-project-authorizations.json`. Review-packet inventory: IP-1 (parser) + IP-2 (tests) single thread.

## Bridge INDEX Update Evidence

NEW filed at `bridge/gtkb-proposal-standards-test-claim-rerun-verifier-001.md`; new top entry prepended.

## Proposed Scope

### IP-1: Test-claim parser + runner

`scripts/bridge_proposal_test_claim_verifier.py`:

1. Read the bridge proposal at `bridge/<bridge-id>-NNN.md` (latest version).
2. Locate the `Specification-Derived Verification Plan` (or `## Test Plan`) section.
3. Extract test-references via regex: lines matching `test_[a-z0-9_]+` and any explicit `pytest` invocation patterns.
4. For each test-name, locate the test in the working tree (heuristic: search `tests/`, `platform_tests/`, `groundtruth-kb/tests/` for files matching `test_*.py` containing a `def test_<name>` symbol).
5. Emit JSON + markdown report: `{claim: <name>, found: bool, file: <path or null>}`.
6. `--strict` mode: also `pytest -k <name>` and compare outcome.

### IP-2: Tests + (no spec promotion - new tool)

Tests cover: claim-extraction with various proposal formats, test-location heuristic, strict-mode outcome comparison.

## Specification-Derived Verification Plan

| Behavior | Test |
|---|---|
| Parse claims from table format | `test_parse_test_claims_from_table` |
| Parse claims from inline mentions | `test_parse_test_claims_from_inline_text` |
| Locate test in single test dir | `test_locate_test_in_tests_dir` |
| Locate test in groundtruth-kb/tests | `test_locate_test_in_gtkb_tests_dir` |
| Missing test reported | `test_missing_test_emits_not_found_status` |
| Strict mode runs pytest | `test_strict_mode_runs_pytest_per_claim` |
| Output JSON schema | `test_output_emits_expected_schema` |

Run: `python -m pytest tests/scripts/test_bridge_proposal_test_claim_verifier.py -v`.

## Acceptance Criteria

- IP-1 verifier landed; 7 tests PASS.
- Both preflights PASS.

## Risks / Rollback

- Risk: tests outside the heuristic dirs aren't found; false MISSING reports. Mitigation: configurable additional roots; document heuristic in --help.
- Rollback: remove script.

## Recommended Commit Type

`feat` - new verifier tool. ~120 LOC.
