NEW

# Implementation Proposal - ADR/DCL Clause-Test Enforcement Slice 2 (Promote Blocking Clauses) (GTKB-ADR-DCL-CLAUSE-TEST-ENFORCEMENT-001)

bridge_kind: prime_proposal
Document: gtkb-adr-dcl-clause-test-enforcement-slice-2
Version: 001
Author: Prime Builder (Claude, harness B)
Date: 2026-05-14 UTC
Session: S350

Project Authorization: PAUTH-PROJECT-GTKB-SPEC-TEST-QUALITY-SPEC-TEST-QUALITY-BATCH
Project: PROJECT-GTKB-SPEC-TEST-QUALITY
Work Item: GTKB-ADR-DCL-CLAUSE-TEST-ENFORCEMENT-001

target_paths: ["config/governance/adr-dcl-clauses.toml", "scripts/adr_dcl_clause_preflight.py", "tests/scripts/test_adr_dcl_clause_preflight.py"]

This NEW proposal advances `GTKB-ADR-DCL-CLAUSE-TEST-ENFORCEMENT-001` from Slice 1 (advisory) to Slice 2 (mandatory) for the first batch of stable, well-evidenced ADR/DCL clauses. Slice 1 landed advisory-mode clause preflight; Slice 2 promotes a small number of high-confidence clauses to blocking enforcement.

## Claim

Per `bridge/gtkb-adr-dcl-clause-test-enforcement-001.md` Slice 1 GO at -002, Slice 2's job is to promote selected blocking-severity clauses to `enforcement_mode = "blocking"` (currently they have `enforcement_mode = "advisory"`). This requires evidence that the clause's detection regex is stable + the must_apply trigger is accurate.

## In-Root Placement Evidence

All target paths in-root. `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` satisfied.

## Specification Links

- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - clause this promotion strengthens.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - clause this promotion strengthens.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge protocol.
- `GOV-STANDING-BACKLOG-001` - WI tracked.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - in-root only.
- `DELIB-S350-BATCH5-EIGHT-PROJECT-AUTHORIZATIONS` - owner-decision evidence.

## Prior Deliberations

- `DELIB-S350-BATCH5-EIGHT-PROJECT-AUTHORIZATIONS` - batch-5 authorization.
- `bridge/gtkb-adr-dcl-clause-test-enforcement-001` Slice 1 - parent (advisory pilot).

## Owner Decisions / Input

- 2026-05-14 UTC, S350+: owner approved GTKB-SPEC-TEST-QUALITY authorization including this WI.

## Requirement Sufficiency

Existing requirements sufficient. Slice 1 GO is the operative parent contract; Slice 2 follows its "Open Follow-On" Section §2 directive.

## Clause Scope Clarification (Not a Bulk Operation)

Not a bulk operation. One WI promoting a small enumerated clause set; member of PROJECT-GTKB-SPEC-TEST-QUALITY per `formal-artifact-approval` packet `.groundtruth/formal-artifact-approvals/2026-05-14-batch5-eight-project-authorizations.json`. Review-packet inventory: IP-1 (clause TOML promotions) + IP-2 (regression tests) + IP-3 (rollback contingency) single thread.

## Bridge INDEX Update Evidence

NEW filed; new top entry prepended.

## Proposed Scope

### IP-1: Promote selected clauses to enforcement_mode="blocking"

In `config/governance/adr-dcl-clauses.toml`, promote these high-confidence clauses (Slice 1 has months of advisory evidence on each):

1. `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` - currently advisory; trigger pattern stable; mark blocking.
2. `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` - currently advisory; mark blocking.
3. `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` - currently advisory; mark blocking.

(Already blocking for proposals that match: these already block via the applicability preflight. This proposal aligns the clause-preflight enforcement_mode to match the operational reality. Affects exit-code behavior in `--strict` mode.)

### IP-2: Tests

Tests verify each newly-blocking clause: positive cases (clause satisfied -> exit 0) + negative cases (clause unsatisfied + no waiver -> exit 5).

### IP-3: Rollback contingency

If any promotion causes a wave of false-positive blocks on legitimate proposals, the TOML edit is single-line per clause; revert is fast. Owner can also waive via the established owner-waiver pattern.

## Specification-Derived Verification Plan

| Clause | Test |
|---|---|
| CLAUSE-CONCRETE-LINKS promoted | `test_concrete_links_blocking_when_evidence_missing` |
| CLAUSE-INDEX-IS-CANONICAL promoted | `test_index_canonical_blocking_when_violated` |
| CLAUSE-IN-ROOT promoted | `test_in_root_blocking_when_path_outside` |
| Positive evidence still passes | `test_promoted_clauses_pass_with_evidence` |
| Owner-waiver bypass works | `test_promoted_clauses_owner_waiver_bypasses` |
| Other clauses still advisory | `test_unpromoted_clauses_remain_advisory` |

Run: `python -m pytest tests/scripts/test_adr_dcl_clause_preflight.py -v`.

## Acceptance Criteria

- IP-1 TOML promotions landed.
- IP-2 tests PASS (6 tests).
- IP-3 rollback procedure documented in this thread's post-impl report.
- Both preflights PASS.

## Risks / Rollback

- Risk: legitimate proposals may have legacy phrasing that doesn't match the detection regex; sudden block on a clause that was previously advisory. Mitigation: owner-waiver line is established escape hatch + Slice 1's months of advisory evidence shows current proposals pass.
- Rollback: per-clause TOML edit revert.

## Recommended Commit Type

`feat` - enforcement promotion. ~10 LOC TOML + tests.
