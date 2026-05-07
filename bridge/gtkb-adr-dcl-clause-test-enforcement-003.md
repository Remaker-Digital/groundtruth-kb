NEW

# GTKB-ADR-DCL-CLAUSE-TEST-ENFORCEMENT — Slice 1 Implementation Report

Filed by: Prime Builder (Claude / harness B)
Date: 2026-05-07 (S334)
Bridge kind: implementation report (post-implementation, NEW for VERIFIED review)
Implements: `bridge/gtkb-adr-dcl-clause-test-enforcement-001.md` (NEW) under `GO` at `-002`
Requested bridge disposition: `VERIFIED`

## Specification Links

(Carried forward from `-001`.)

- `GOV-FILE-BRIDGE-AUTHORITY-001` (always blocking)
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` (always blocking)
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` (always blocking)
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` (blocking)
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` (advisory)
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` (advisory)
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` (advisory)
- `.claude/rules/file-bridge-protocol.md` (Mandatory Applicability Preflight Gate + new "Clause-Test Preflight (Advisory; Slice 1)" section)
- `.claude/rules/codex-review-gate.md`
- `.claude/rules/project-root-boundary.md`
- `.claude/rules/operating-model.md` §4 (Alignment Tests)

## Implemented Changes

### Change 1 — Clause registry file

`config/governance/adr-dcl-clauses.toml` (NEW). 5 fixtures, all
`enforcement_mode = "advisory_only_in_slice_1"`:

| # | clause_id | spec_id | severity |
|---|---|---|---|
| 1 | `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | blocking |
| 2 | `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | blocking |
| 3 | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | blocking |
| 4 | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | blocking |
| 5 | `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | blocking |

Each clause carries: `applies_when_path` (glob), `applies_when_doc_name`
(regex), `applies_when_content` (regex), `evidence_required` (text),
`evidence_pattern` (regex), `failure_condition` (text), optional
`failure_pattern` (regex), `severity`, `waiver_policy`, `enforcement_mode`.

### Change 2 — Companion preflight CLI

`scripts/adr_dcl_clause_preflight.py` (NEW, ~250 lines).

- CLI: `python scripts/adr_dcl_clause_preflight.py --bridge-id <id> [--out <path>]`.
- Loads clauses from `config/governance/adr-dcl-clauses.toml`; falls back gracefully
  when not present (still exits 0 per Slice-1 contract).
- Resolves the operative bridge file by parsing `bridge/INDEX.md` (mirrors the
  resolution logic of `bridge_applicability_preflight.py`).
- For each clause: applicability discovery via path-glob + doc-name regex +
  content regex; for `must_apply` clauses, evidence detection via
  `evidence_pattern` (with optional `failure_pattern` refutation).
- Emits a markdown "Clause Applicability" section: counts table, per-clause
  verdict table, and an "Evidence Gaps" subsection for must_apply clauses
  without satisfying evidence.
- **Always exits 0** in Slice 1 (advisory contract).
- Read-only against MemBase (no KB API calls; only TOML + filesystem).

### Change 3 — Tests

`tests/scripts/test_adr_dcl_clause_preflight.py` (NEW, 6 tests, ~150 lines).

| # | Test | Maps to GO condition |
|---|---|---|
| 1 | `test_schema_parses_with_five_fixtures` | Codex GO condition: 5 fixtures parse cleanly |
| 2 | `test_applicability_discovery_true_positive` | Spec verification: trigger detection |
| 3 | `test_applicability_discovery_true_negative` | Spec verification: false-positive guard |
| 4 | `test_evidence_detection_true_positive` | Spec verification: evidence detection |
| 5 | `test_evidence_detection_true_negative_with_gap_summary` | Spec verification: gap reporting |
| 6 | `test_cli_advisory_mode_always_exits_zero` | Codex GO condition: Slice-1 advisory contract |

### Change 4 — Documentation note

Added section "Clause-Test Preflight (Advisory; Slice 1)" to
`.claude/rules/file-bridge-protocol.md` (between "Mandatory Applicability
Preflight Gate" and "File Naming"). Explicitly:

- Describes the new preflight as "NOT a blocking gate."
- States "always exits 0 — even when blocking-severity clauses lack
  satisfying evidence."
- Names Slice 2 as the future bridge thread that will promote selected
  clauses to a hard gate.
- Cites `bridge/gtkb-adr-dcl-clause-test-enforcement-001.md` (GO at -002)
  as the source.

This satisfies Codex GO condition 4 ("the new file-bridge-protocol.md note
does not represent the clause preflight as a blocking gate yet").

## Specification-Derived Verification

| Linked specification | Test / Evidence | Result |
|---|---|---|
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Clause #2 fixture (`CLAUSE-INDEX-IS-CANONICAL`) + `test_schema_parses_with_five_fixtures` | PASS |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Clause #3 fixture (`CLAUSE-CONCRETE-LINKS`) + Test 1 | PASS |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Clause #4 fixture (`CLAUSE-SPEC-TO-TEST-MAPPING`) + Test 1 + this matrix | PASS |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Clause #1 fixture (`CLAUSE-IN-ROOT`) + Tests 2 + 4 + 5 | PASS |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Slice 1 framing (clauses-as-artifacts, registered in TOML, evaluated mechanically) | PASS (advisory) |
| Read-only discipline (Slice 1) | CLI uses TOML + filesystem only, no `groundtruth_kb` import, no KB API call | PASS |
| Slice-1 advisory boundary | Test 6 asserts `rc == 0` even with evidence gap | PASS |
| Codex GO condition: TOML parses cleanly | Test 1 | PASS |
| Codex GO condition: rule-doc note is non-blocking | Doc edit in `file-bridge-protocol.md` Section "Clause-Test Preflight (Advisory; Slice 1)" — explicit "NOT a blocking gate" + "always exits 0" | PASS |
| Codex GO condition: harness parity preserved | `python scripts/check_harness_parity.py --all --markdown` | PASS (Counts: PASS: 50) |
| Codex GO condition: no KB write or schema mutation | Static analysis: no `db.insert_*`/`db.update_*`/`db.delete_*` calls in Slice 1 source | PASS |

## Commands Executed

```
python -m pytest tests/scripts/test_adr_dcl_clause_preflight.py -v
# -> 6 passed in 0.25s

python scripts/check_harness_parity.py --all --markdown
# -> Overall status: PASS; Counts: PASS: 50

python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-codex-backlog-cleanup-retroactive-review
# -> Exit 0; report shows 5 must_apply clauses, 0 evidence gaps
#    (the recently-VERIFIED Phase-1 report cites all 5 spec families)

python scripts/bridge_applicability_preflight.py --bridge-id gtkb-adr-dcl-clause-test-enforcement
# -> preflight_passed: true; missing_required_specs: []; missing_advisory_specs: []
```

## Acceptance Criteria — Status

| # | Criterion | Status |
|---|---|---|
| 1 | `config/governance/adr-dcl-clauses.toml` exists with 5 fixtures parseable | PASS (Test 1 verifies parse + spec-id set) |
| 2 | `scripts/adr_dcl_clause_preflight.py` exists, runs in advisory mode, exits 0 on existing operative file | PASS (smoke run on `gtkb-codex-backlog-cleanup-retroactive-review` exits 0) |
| 3 | All 6 tests in `tests/scripts/test_adr_dcl_clause_preflight.py` pass | PASS (6 of 6) |
| 4 | `.claude/rules/file-bridge-protocol.md` carries the advisory-mode note | PASS (Section "Clause-Test Preflight (Advisory; Slice 1)" added) |
| 5 | `python scripts/check_harness_parity.py --all --markdown` continues to report `PASS` | PASS (PASS: 50) |
| 6 | `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-adr-dcl-clause-test-enforcement` reports `preflight_passed: true` | PASS |
| 7 | No KB write performed during Slice 1 | PASS (no `groundtruth_kb` import, no DB API calls in source) |

## Out of Scope (Slice 1 boundaries enforced)

Per the proposal at `-001` and Codex GO at `-002`, the following are
explicitly NOT included in Slice 1:

- Slice 2: promote registry-derived clause coverage to mandatory `GO`/`VERIFIED` gate.
- Slice 3: clause-test matrix integration into LO verdict + PB proposal templates.
- Slice 4: ratchet adoption (backfill remaining ADR/DCL records).
- Slice 5: optional semantic-search/LLM-assist for candidate discovery.
- Mutation of canonical `specifications` table schema (companion TOML
  registry only in Slice 1).

The two open owner decisions (semantic vs deterministic discovery for
Slice 5; companion registry vs canonical schema for Slice 3) remain
deferred to those future bridge threads.

## Files Changed

```
config/governance/adr-dcl-clauses.toml                       (new, 5 fixtures, ~80 lines)
scripts/adr_dcl_clause_preflight.py                          (new, ~250 lines)
tests/scripts/test_adr_dcl_clause_preflight.py               (new, 6 tests, ~150 lines)
.claude/rules/file-bridge-protocol.md                        (modified, +18 lines: new section)
bridge/gtkb-adr-dcl-clause-test-enforcement-003.md           (this report)
```

## Recommended Commit Type

`feat:` — adds a new clause registry, a new preflight CLI, a new test
module, and a new advisory section in the file-bridge protocol rule.
Net-new capability surface (clause-test preflight pipeline), not a
maintenance-only change.

## Risk And Rollback

- Risk realized? None during Slice 1. The CLI is advisory-only and cannot
  block any GO/VERIFIED decision.
- Risk forward: a future Slice 2 promotion to blocking-mode requires the
  clause patterns to be tightened first (false-positive avoidance).
  Slice-1 feedback runs against real bridges in upcoming sessions will
  drive that tightening.
- Rollback: delete the 4 new files (TOML, script, test, this report) and
  revert the file-bridge-protocol.md note. All isolated.

## Owner Decisions / Input

- Owner directive 2026-05-06 (per source advisory) authorized filing of
  the bridge proposal at `-001`.
- Codex GO at `-002` authorized Slice-1 implementation under the listed
  GO conditions; all conditions met above.
- Owner AUQ-committed plan at S334 (Option C this session) authorized
  proceeding to file this implementation report for Codex VERIFIED review.
- The two open owner decisions for Slices 3 and 5 remain explicitly
  deferred (not requested in this report).

## Pre-Filing Preflight Subsection

1. Triggered specs in `config/governance/spec-applicability.toml` — all cited.
2. KB-search — `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`,
   `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, and
   `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` cited as advisory governance.
3. Bridge-governance specs — cited.
4. Preflight to be run after INDEX update.
5. `packet_hash` recorded after preflight.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
