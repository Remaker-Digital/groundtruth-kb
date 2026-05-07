NEW

# GTKB-ADR-DCL-CLAUSE-TEST-ENFORCEMENT — Slice 1: Clause Registry Skeleton + Five High-Risk Fixtures

Filed by: Prime Builder (Claude / harness B)
Date: 2026-05-07 (S334)
Bridge kind: implementation proposal (NEW)
Source advisory: `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/ADR-DCL-CLAUSE-TEST-ENFORCEMENT-ADVISORY-2026-05-06.md` (Codex Loyal Opposition; tier-2 owner-elevated)
Related backlog identifier: `GTKB-ADR-DCL-CLAUSE-TEST-ENFORCEMENT-001`
Requested bridge disposition: `GO`

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` (always blocking)
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` (always blocking)
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` (always blocking)
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` (blocking)
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` (advisory)
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` (advisory)
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` (advisory)
- `.claude/rules/file-bridge-protocol.md` (Mandatory Applicability Preflight Gate)
- `.claude/rules/codex-review-gate.md`
- `.claude/rules/project-root-boundary.md`
- `.claude/rules/operating-model.md` §4 (Alignment Tests)

## Source Advisory Summary

The Codex Loyal Opposition advisory dated 2026-05-06 claims that ADR/DCL
records risk becoming decorative references unless each enforceable clause
is treated as a test that must pass before `GO` (proposal review) and before
`VERIFIED` (post-implementation review). The advisory recommends building a
clause registry, an applicability discovery surface, mandatory clause-test
matrices in both review verdicts, and ratcheted adoption starting from
highest-risk records.

The advisory does NOT propose a specific schema or specific enforcement
ordering. Slice 1 (this proposal) sets the framework with deterministic
discovery and the five highest-risk ADR/DCL fixtures, runs in advisory
mode (mechanical floor that surfaces gaps without blocking), and defers
mandatory blocking enforcement to Slice 2.

## Slice Plan (this proposal covers Slice 1 only)

| Slice | Scope | Status |
|---|---|---|
| 1 | Clause registry schema + 5 high-risk fixtures + companion preflight CLI + advisory-mode reporting + tests | THIS PROPOSAL |
| 2 | Promote registry-derived clause coverage to mandatory `GO`/`VERIFIED` gate (block when blocking clauses lack evidence) | Future bridge thread, after Slice 1 VERIFIED |
| 3 | Clause-test matrix integration into Loyal Opposition verdict templates + Prime Builder proposal templates | Future, owner-decision dependent (semantic search vs deterministic) |
| 4 | Ratchet adoption: backfill remaining ADR/DCL records | Future, opportunistic during normal bridge work |
| 5 | Optional semantic-search/LLM-assist for candidate discovery | Future, owner-decision dependent |

## Slice 1 Scope

### Change 1 — Clause registry schema + file

New file: `config/governance/adr-dcl-clauses.toml`. Schema:

```toml
[[clauses]]
clause_id = "ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT"
spec_id = "ADR-ISOLATION-APPLICATION-PLACEMENT-001"
description = "All active GT-KB files must remain within E:\\GT-KB."
applies_when_path = ["**/*"]
applies_when_doc_name = []
applies_when_content = ['(?i)\\b(?:in-root|out-of-root|project root|root boundary)\\b']
evidence_required = "implementation_report:must declare in-root output paths for all generated artifacts; bridge file must reside under bridge/"
failure_condition = "implementation_report references an output path outside E:\\GT-KB"
severity = "blocking"
waiver_policy = "explicit_owner_waiver_required_in_bridge"
enforcement_mode = "advisory_only_in_slice_1"
```

The five fixtures encoded in Slice 1 (highest-risk ADR/DCL records per the
advisory's prioritization):

1. `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — in-root boundary clause.
2. `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge as canonical workflow state.
3. `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — concrete
   spec-link section on every implementation proposal.
4. `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — spec-to-test mapping
   + executed evidence on every VERIFIED report.
5. `GOV-STANDING-BACKLOG-001` — backlog as cross-session work authority
   (the bulk-operation visibility clause that the codex-backlog-cleanup
   incident exposed).

### Change 2 — Companion preflight CLI

New file: `scripts/adr_dcl_clause_preflight.py`. CLI surface:

```text
python scripts/adr_dcl_clause_preflight.py --bridge-id <document-name>
```

For the bridge thread's operative file, computes:

- `must_apply` clauses (deterministic triggers fired);
- `may_apply` clauses (partial trigger match);
- `not_applicable` clauses;
- For each `must_apply` clause: whether the operative bridge file shows
  evidence satisfying that clause's `evidence_required` (heuristic
  text-match for Slice 1; promotes to structural check in Slice 2).

Output: markdown section identical in shape to the existing
`bridge_applicability_preflight.py` output (a "Clause Applicability"
section listing each clause + applicability status + evidence-found
status).

Slice 1 always exits 0 regardless of findings (advisory mode); the report
is informational. Slice 2 promotes the exit code to a hard-block when
blocking clauses lack evidence.

### Change 3 — Tests

New file: `tests/scripts/test_adr_dcl_clause_preflight.py`. Six tests:

1. **Schema parse test:** the TOML loads, all 5 fixtures parse with
   required fields populated.
2. **Applicability discovery — true positive:** for a synthetic bridge
   file whose content fires the in-root boundary triggers, the preflight
   reports `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` as
   `must_apply`.
3. **Applicability discovery — true negative:** for a synthetic bridge
   file with no boundary keywords or paths, the preflight reports the
   clause as `not_applicable`.
4. **Evidence-detection — true positive:** for a synthetic bridge file
   that includes an implementation report with in-root output paths, the
   preflight reports the clause's `evidence_found = true`.
5. **Evidence-detection — true negative (gap detection):** for a
   synthetic bridge file that references an out-of-root path, the
   preflight reports the clause's `evidence_found = false` AND
   `gap_summary` describes the violation.
6. **Advisory-mode exit code:** the CLI returns exit code 0 even when
   blocking clauses lack evidence (Slice-1 advisory mode); the report
   text contains the gap summary so it remains visible to reviewers.

### Change 4 — Documentation note

New section in `.claude/rules/file-bridge-protocol.md` titled
`Clause-Test Preflight (Advisory; Slice 1)` describing the new
preflight as an additional tool reviewers may consult, with explicit
note that it is NOT yet a blocking gate. The note also records that
Slice 2 will promote it to blocking after owner approval.

## Specification-Derived Verification

| Linked specification | Test |
|---|---|
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Schema fixture for it (Change 1 fixture 2) |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Schema fixture (Change 1 fixture 3) |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Schema fixture (Change 1 fixture 4) |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Schema fixture (Change 1 fixture 1) + Tests 2 + 4 + 5 |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | The whole proposal's framing (clause-as-artifact) |
| Read-only discipline (Slice 1) | CLI does not mutate KB; advisory output only |
| Slice-1 boundary | Test 6 asserts advisory-mode exit code |

## Acceptance Criteria

1. `config/governance/adr-dcl-clauses.toml` exists with 5 fixtures parseable.
2. `scripts/adr_dcl_clause_preflight.py` exists, runs in advisory mode, exits 0
   on the existing `bridge/INDEX.md` operative files.
3. All 6 tests in `tests/scripts/test_adr_dcl_clause_preflight.py` pass.
4. `.claude/rules/file-bridge-protocol.md` carries the advisory-mode note.
5. `python scripts/check_harness_parity.py --all --markdown` continues to
   report `PASS`.
6. `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-adr-dcl-clause-test-enforcement` reports `preflight_passed: true`.
7. No KB write performed during Slice 1.

## Risk And Rollback

- Risk: Heuristic evidence-detection produces false positives/negatives in
  Slice 1 — addressed by advisory-mode (output is informational; no GO/VERIFIED
  is blocked on Slice 1 results); Slice 2 promotes only after the heuristic is
  tightened with feedback from Slice 1 runs.
- Risk: Schema lock-in — addressed by keeping the schema minimal in Slice 1
  and reserving extension for Slices 2-3 with separate proposals.
- Risk: Owner-decision deferral on semantic-search/LLM-assist (Slice 5) and
  on canonical schema mutation (e.g., adding clause fields directly to the
  `specifications` table vs companion TOML registry) is preserved as
  explicit out-of-scope; the proposal does NOT pre-decide either.
- Rollback: delete `config/governance/adr-dcl-clauses.toml`,
  `scripts/adr_dcl_clause_preflight.py`,
  `tests/scripts/test_adr_dcl_clause_preflight.py`, and the
  `.claude/rules/file-bridge-protocol.md` advisory note. All isolated.

## Open Owner Decisions Required Before Slice 3 / Slice 5

These are NOT requested in this Slice-1 proposal; they are surfaced here so
the deferral is explicit and so a future bridge thread does not silently
make the choice without owner sign-off.

1. **Semantic-search vs deterministic-only candidate discovery (Slice 5):**
   Should clause-applicability discovery later use semantic search /
   embeddings / LLM assistance, or remain deterministic-only via TOML
   triggers + content regex?
2. **Companion clause registry vs canonical schema mutation (Slice 3):**
   Should ADR/DCL clauses live in a companion TOML registry (Slice 1's
   approach) indefinitely, or migrate into the `specifications` table
   itself as new structured fields once the framework stabilizes?

These will be surfaced via `AskUserQuestion` in the Slice 3 / Slice 5
proposals when the time comes.

## Owner Decisions / Input

- Owner directive 2026-05-06 (per source advisory): captured in the
  CODEX-INSIGHT-DROPBOX advisory; owner directed Loyal Opposition to file
  the advisory and Prime Builder to file a normal bridge proposal with the
  advisory as input. This proposal is the result.
- Owner AUQ-committed plan at S334 (this turn) included this filing as
  item 3 of 4 (tier-2 owner-elevated); the AUQ-committed plan authorizes
  filing this NEW proposal for Codex review.
- The two open owner decisions for Slices 3 and 5 (above) are NOT
  requested in this proposal; Slice 1's deterministic+advisory scope
  does not depend on them.

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
