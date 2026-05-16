REVISED

# Implementation Proposal - POR Step 16.D Orphan Test Rationalization (WORKLIST-POR-STEPS-16-D-16-E-SPEC-HYGIENE-REMEDIATION-16-A-B-C-COMPLETE)

bridge_kind: implementation_proposal
Document: gtkb-por-step-16-d-orphan-test-rationalization
Version: 003
Author: Prime Builder (Claude, harness B)
Date: 2026-05-15 UTC
Session: S353+

Project Authorization: PAUTH-PROJECT-GTKB-SECURITY-PRIVACY-SECURITY-PRIVACY-BATCH-SPECS-LIGHT-INITIAL
Project: PROJECT-GTKB-SECURITY-PRIVACY
Work Item: WORKLIST-POR-STEPS-16-D-16-E-SPEC-HYGIENE-REMEDIATION-16-A-B-C-COMPLETE

target_paths: ["scripts/orphan_test_rationalization.py", "scripts/por_step_16_exit_verification.py", "platform_tests/scripts/test_orphan_test_rationalization.py"]

This REVISED proposal advances POR Steps 16.D-16.E spec hygiene remediation. Per the WI
description, 16.A/B/C are VERIFIED at `por-step16c-implemented-untested-remediation-004`.
Remaining: **16.D** orphan test rationalization and **16.E** exit verification (untested-spec
count <= 6 + orphan-test count <= 100).

## Revision Notes

This `-003` REVISED version addresses every finding in the `-002` NO-GO:

- **F1 (P1) — omits controlling prior POR 16.D evidence and repeats the stale orphan baseline.**
  Addressed. The `## Prior Deliberations` section now cites `DELIB-0822` (POR 16.D Phase 1
  completion + baseline correction), `DELIB-0823` (POR 16.D Phase 2 completion), and `DELIB-0845`
  / `DELIB-1275` (the `por-step16d-orphan-triage-phase2` bridge thread and its VERIFIED history).
  The stale ~10,440 figure has been **removed everywhere** in this proposal and replaced with the
  live verified Phase 2 baseline. The new `## POR 16.D Verified Baseline` section states the
  corrected numbers, verified by direct read of the existing Phase 2 tooling
  (`tools/knowledge-db/triage_orphan_tests_phase2.py` lines 32-35:
  `EXPECTED_TOTAL_ORPHANS = 2322` post-Phase-1, `EXPECTED_POST_APPLY_ORPHANS = 2189`
  post-Phase-2; `tools/knowledge-db/verify_post_16d_phase1.py` line 195: empty-spec count 2,322
  post-Phase-1). The new `## Relationship to Existing 16.D Tooling` section states explicitly that
  the new `orphan_test_rationalization.py` script **reuses** (does not supersede or replace) the
  Phase 2 classification artifacts: it consumes `.groundtruth/por-16d-phase2-classification.json`
  as its input baseline and operates only on the 2,189-test post-Phase-2 empty-spec residue.
- **F2 (P1) — proposed test target outside the current root pytest lane.** Addressed. The test
  file moved from `tests/scripts/test_orphan_test_rationalization.py` to
  `platform_tests/scripts/test_orphan_test_rationalization.py`. `target_paths`, the verification
  plan, and acceptance criteria all use the `platform_tests/scripts/` path, inside the configured
  `testpaths` (`pyproject.toml` `testpaths = ["platform_tests", "applications/Agent_Red/tests"]`).

## Claim

Two-part advance, scoped to the verified post-Phase-2 orphan residue:

1. **Orphan-test rationalization tooling** — `scripts/orphan_test_rationalization.py` consumes the
   existing Phase 2 classification artifact `.groundtruth/por-16d-phase2-classification.json` as
   its input baseline (the 2,189-test post-Phase-2 empty-spec residue, classified into Class
   B/C/D by the verified Phase 2 work) and refines the disposition of each remaining orphan into
   adopt / migrate / retire / review using heuristics (test name -> likely spec mapping, content
   -> likely target). It emits a per-test inventory file. It does NOT recompute the Phase 1/2
   baseline and does NOT re-classify Class A orphans (those were already auto-linked in Phase 2).
2. **Exit-verification script** — `scripts/por_step_16_exit_verification.py` asserts the 16.E
   thresholds (untested specs <= 6, orphan tests <= 100) against live MemBase state.

Full disposition execution (the 2,189-test residue is bulk-scale) follows in separate execution
batches gated by owner approval; this proposal produces the rationalization tooling and the
exit-verification gate only.

## In-Root Placement Evidence

All target paths in-root under `E:\GT-KB`. `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT`
satisfied.

## POR 16.D Verified Baseline

The orphan-test baseline is NOT ~10,440. That figure was the stale pre-Phase-1 estimate and was
corrected by verified Phase 1 and Phase 2 work. The current verified baseline:

- **Post-Phase-1:** 2,322 empty-spec orphan tests (total latest-version tests = 11,142). Source:
  `tools/knowledge-db/verify_post_16d_phase1.py` invariant I3 (line 195-201:
  `counts["empty_spec_id"] == 2322`) and `triage_orphan_tests_phase2.py` line 32
  (`EXPECTED_TOTAL_ORPHANS = 2322`). Recorded in `DELIB-0822`.
- **Post-Phase-2:** 2,189 empty-spec orphan tests (133 Class A orphans were auto-linked in
  Phase 2; 2,322 - 133 = 2,189). Source: `triage_orphan_tests_phase2.py` line 35
  (`EXPECTED_POST_APPLY_ORPHANS = EXPECTED_TOTAL_ORPHANS - EXPECTED_CLASS_A # 2189`). Recorded in
  `DELIB-0823`.

The implementation will re-confirm the live count at run time via a read-only MemBase query and
record the observed value in the inventory `_meta` block; if the live count diverges from 2,189,
the script records the divergence rather than assuming the stale figure.

## Relationship to Existing 16.D Tooling

The new `scripts/orphan_test_rationalization.py` **reuses, does not supersede or replace**, the
verified Phase 2 artifacts:

- `tools/knowledge-db/triage_orphan_tests_phase2.py` — the verified Phase 2 script that produced
  the Class A auto-link + B/C/D classification. The new script does NOT re-run Phase 2 logic; it
  treats Phase 2's output as a fixed, verified input.
- `.groundtruth/por-16d-phase2-classification.json` — the verified Phase 2 classification report.
  The new script **consumes this file as its input baseline**: it reads the Class B/C/D orphan
  set from this artifact and refines each residual orphan's disposition (adopt/migrate/retire/
  review). If the file is absent, the script fails closed with an actionable diagnostic naming
  the Phase 2 prerequisite rather than recomputing from scratch.
- `.groundtruth/por-16d-phase2-snapshot.json` — the Phase 2 pre-apply snapshot; read-only
  reference for the rationalization script's audit trail.

This relationship is explicit so the new tooling cannot redo Phase 2 work against a stale mental
model. The new tool's scope is strictly the post-Phase-2 residue refinement plus the 16.E exit
gate; Phase 1 and Phase 2 remain VERIFIED and untouched.

## Specification Links

- `GOV-18` - assertion quality standard (SPEC-1662); orphan tests undermine assertion-quality coverage.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - cross-cutting constraint requiring the post-implementation VERIFIED step to rest on executed spec-derived tests; the spec-to-test plan below maps every linked spec to a test.
- `GOV-RELEASE-READINESS-GOVERNED-TESTING-001` - release readiness; orphan tests block governed-testing release readiness.
- `GOV-ARTIFACT-APPROVAL-001` - bulk-mutation governance; per-batch test-status mutations carry per-batch approval packets.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge protocol authority governing this proposal as a bridge artifact.
- `SPEC-AUQ-POLICY-ENGINE-001` - CLI surface (the two new root scripts).
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - in-root only; all paths under `E:\GT-KB`.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - cross-cutting constraint requiring this proposal to cite every relevant governing specification.
- `GOV-STANDING-BACKLOG-001` - the POR 16.D-16.E WI is tracked in the standing backlog.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - artifact-oriented governance baseline; this hygiene work is captured as governed artifacts (WI, bridge thread, inventory, spec-derived tests).
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - durable artifact-graph model; the WI, bridge thread, the Phase 1/2 artifacts, and linked specs form the artifact graph.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - artifact lifecycle trigger discipline; the WI triggers this implementation proposal and its tests.
- `.claude/rules/file-bridge-protocol.md` - bridge file naming, INDEX semantics, Specification Links and Owner Decisions / Input section requirements, Pre-Filing Preflight Subsection.
- `.claude/rules/codex-review-gate.md` - Counterpart Review Gate; this proposal seeks Codex GO before implementation.
- `.claude/rules/project-root-boundary.md` - all `target_paths` resolve inside `E:\GT-KB`.

## Prior Deliberations

- `DELIB-S350-BATCH5-EIGHT-PROJECT-AUTHORIZATIONS` - batch-5 owner authorization; the owner-decision evidence for the active project authorization cited by this proposal.
- `DELIB-0822` - records POR Step 16.D Phase 1 completion and the baseline correction: the stale ~10,440 figure was corrected to a 2,322-test unified empty-spec orphan pool. This proposal's baseline is derived from this record.
- `DELIB-0823` - records POR Step 16.D Phase 2 completion: 133 Class A orphans auto-linked and the remaining pool classified B/C/D, leaving 2,189 empty-spec orphans. This proposal consumes the Phase 2 classification output as its input baseline.
- `DELIB-0845` - records the `por-step16d-orphan-triage-phase2` bridge thread.
- `DELIB-1275` - records the `por-step16d-orphan-triage-phase2` bridge thread VERIFIED status/history.
- `bridge/por-step16c-implemented-untested-remediation-004` - POR 16.A/B/C VERIFIED; the predecessor sub-phase.

No prior deliberation waives the requirement to carry forward the POR 16.D Phase 1/2 verified
baseline into a new 16.D rationalization proposal; the `-002` NO-GO requires it and this REVISED
version satisfies it.

## Owner Decisions / Input

This proposal depends on owner approval. The authorizing AskUserQuestion evidence:

- 2026-05-15 UTC, S350+: owner approved the GTKB-SECURITY-PRIVACY project authorization (captured via AskUserQuestion, recorded as DELIB-S350-BATCH5-EIGHT-PROJECT-AUTHORIZATIONS) including the POR 16.D-16.E work item. The authorization `PAUTH-PROJECT-GTKB-SECURITY-PRIVACY-SECURITY-PRIVACY-BATCH-SPECS-LIGHT-INITIAL` is active and includes `WORKLIST-POR-STEPS-16-D-16-E-SPEC-HYGIENE-REMEDIATION-16-A-B-C-COMPLETE` (confirmed via live `projects authorizations` query before filing).
- Per-proposal Codex GO is required before implementation; this REVISED proposal seeks that GO.
- Actual per-test disposition application against MemBase is Phase-deferred to separate per-batch bridge proposals, each with its own explicit owner approval and its own Codex GO. This proposal produces only the rationalization tooling and the exit-verification gate; it mutates no test rows.

## Requirement Sufficiency

Existing requirements sufficient. The WI description specifies the 16.D/16.E scope and the 16.E
numerical exit thresholds (untested specs <= 6, orphan tests <= 100). The Phase 1/2 verified
artifacts supply the corrected baseline. No new or revised requirement or specification is
created by this work; the rationalization tooling and exit-verification gate implement the
existing WI scope. If a per-batch disposition reveals classification ambiguity not covered by the
existing exclusion specs, that batch's proposal will surface the gap as a candidate SPEC update
through the governed approval path.

## Files Expected To Change

- `scripts/orphan_test_rationalization.py` - new rationalization tooling: consumes `.groundtruth/por-16d-phase2-classification.json`, refines each residual orphan into adopt/migrate/retire/review, emits a per-test inventory JSONL. Read-only against MemBase.
- `scripts/por_step_16_exit_verification.py` - new exit-verification gate: queries MemBase for untested-spec count and orphan-test count, compares against 16.E thresholds, exits 0 on PASS.
- `platform_tests/scripts/test_orphan_test_rationalization.py` - new spec-derived test module (the seven tests in the verification plan below).

## Clause Scope Clarification (Bulk Operation w/ Inventory + Approval Packet)

This proposal builds tooling that processes a bulk-scale orphan residue (2,189 tests post-Phase-2)
but the proposal itself performs **no bulk mutation**: it creates two scripts and one test file
and mutates no MemBase rows. Per `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS`, the
bulk-operation evidence the clause expects:

- **Inventory** — the rationalization tooling produces a per-test `inventory` file
  (`.gtkb-state/orphan-test-rationalization/<date>.jsonl`) with classification + suggested
  disposition for each of the 2,189 residual orphans. This is the visibility artifact required by
  the clause.
- **Review packet** — this bridge document is the review packet for the tooling. The owner
  reviews the inventory output before any actual per-test disposition execution batch.
- **Phase-deferred decision** — actual disposition application is Phase-deferred to separate
  per-batch bridge proposals, each with explicit owner approval.
- **formal-artifact-approval** — applies to MemBase test-status mutations in the deferred
  execution batches; each batch carries its own `formal-artifact-approval` packet.

WI membership: per the `formal-artifact-approval` packet
`.groundtruth/formal-artifact-approvals/2026-05-14-batch5-eight-project-authorizations.json`, the
WI is a member of `PROJECT-GTKB-SECURITY-PRIVACY` (the security/privacy lens scopes POR spec
hygiene work in the batch-5 authorization). Cited evidence patterns: `inventory`,
`formal-artifact-approval`.

## Bridge INDEX Maintenance

This proposal keeps `bridge/INDEX.md` as the canonical bridge workflow-state record. The REVISED
version is filed by inserting `REVISED: bridge/gtkb-por-step-16-d-orphan-test-rationalization-003.md`
at the top of the existing `Document: gtkb-por-step-16-d-orphan-test-rationalization` entry's
version list, above the `-002` NO-GO line. No prior bridge versions are deleted or rewritten.

## Proposed Scope

### IP-1: scripts/orphan_test_rationalization.py

1. Read `.groundtruth/por-16d-phase2-classification.json` (the verified Phase 2 classification
   output). Fail closed with an actionable diagnostic if the file is absent.
2. Re-confirm the live empty-spec orphan count via a read-only MemBase query; record the observed
   value in the inventory `_meta` block alongside the expected post-Phase-2 baseline (2,189).
3. For each residual (Class B/C/D) orphan from the Phase 2 classification, apply refinement
   heuristics:
   - **adopt**: test name matches a known spec (name-similarity scoring) -> suggest spec_id binding.
   - **migrate**: test references a deprecated spec -> suggest replacement.
   - **retire**: test references nothing meaningful + no recent runs -> suggest retirement.
   - **review**: ambiguous -> owner review needed.
4. Emit `.gtkb-state/orphan-test-rationalization/<date>.jsonl` with one classification per test.

CLI: `python scripts/orphan_test_rationalization.py [--out <path>]`. Read-only against
`groundtruth.db`.

### IP-2: scripts/por_step_16_exit_verification.py

- Query MemBase: count untested specs (specs with `status='implemented'` or `'verified'` but no
  linked tests).
- Query MemBase: count orphan tests (tests without `spec_id`).
- Compare against 16.E thresholds: untested <= 6, orphans <= 100.
- Exit 0 if PASS; non-zero with diagnostic if FAIL.

### IP-3: Tests

`platform_tests/scripts/test_orphan_test_rationalization.py` verifies the classification
heuristic output and the exit-verification thresholds with fixture data, plus the Phase 2
input-baseline consumption behavior.

## Specification-Derived Verification Plan

Each linked specification maps to at least one test. Tests live in the `target_paths` test file
`platform_tests/scripts/test_orphan_test_rationalization.py`.

| Behavior | Test | Covers spec |
|---|---|---|
| Classifier "adopt" pattern works | `test_classifier_adopt_pattern` | `GOV-18`, `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` |
| Classifier "retire" pattern works | `test_classifier_retire_pattern` | `GOV-18` |
| Classifier "review" pattern works | `test_classifier_ambiguous_review` | `GOV-18` |
| Inventory JSONL schema incl. `_meta` observed/expected baseline | `test_inventory_jsonl_schema` | `GOV-STANDING-BACKLOG-001` (inventory visibility) |
| Phase 2 classification consumed as input baseline; fail-closed if absent | `test_consumes_phase2_classification_baseline` | `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` |
| Read-only (no MemBase writes) | `test_rationalization_no_db_writes` | `GOV-ARTIFACT-APPROVAL-001` (no unapproved mutation) |
| Exit-verify applies 16.E thresholds; FAIL diagnostic clear | `test_exit_verify_thresholds` | `GOV-RELEASE-READINESS-GOVERNED-TESTING-001`, `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` |

Run: `python -m pytest platform_tests/scripts/test_orphan_test_rationalization.py -v`.

Verification commands:

```
python -m pytest platform_tests/scripts/test_orphan_test_rationalization.py -v --tb=short
python -m ruff check .
python -m ruff format --check .
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-por-step-16-d-orphan-test-rationalization
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-por-step-16-d-orphan-test-rationalization
```

## Acceptance Criteria

- IP-1, IP-2, IP-3 landed; the 7 tests in `platform_tests/scripts/test_orphan_test_rationalization.py` PASS.
- `ruff check` and `ruff format --check` are clean.
- `orphan_test_rationalization.py` consumes `.groundtruth/por-16d-phase2-classification.json` as its input baseline and fails closed if absent.
- The inventory JSONL `_meta` block records the live observed orphan count and the expected post-Phase-2 baseline (2,189).
- Inventory JSONL produced for current state.
- Both preflights PASS (`preflight_passed: true`, clause preflight exit 0).
- Per-test disposition execution is Phase-deferred (separate bridge per batch); no MemBase test rows are mutated by this proposal.

## Risks / Rollback

- Risk: the new tool redoes Phase 2 work against a stale mental model. Mitigation: the tool consumes Phase 2's verified classification artifact as a fixed input and fails closed if absent; it never recomputes the Phase 1/2 baseline.
- Risk: classifier heuristics get many cases wrong on the 2,189-test residue. Mitigation: per-test disposition is owner-gated in deferred batches; the tooling is informational only.
- Risk: project-membership semantic (this WI under SECURITY-PRIVACY) may look unusual. Mitigation: the SECURITY-PRIVACY project authorization is specs-light initial; the POR spec hygiene scope fits the batch-5 authorization, confirmed via live query.
- Rollback: remove `scripts/orphan_test_rationalization.py`, `scripts/por_step_16_exit_verification.py`, and `platform_tests/scripts/test_orphan_test_rationalization.py`. No MemBase rows are mutated by this proposal.

## Recommended Commit Type

`feat` - new audit + verification infrastructure (rationalization tooling + exit-verification gate). Net-new capability surface (~150 LOC + tests).

## Applicability Preflight

Command: `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-por-step-16-d-orphan-test-rationalization`

```text
## Applicability Preflight

- packet_hash: `sha256:11815e3434fa6d46befcd36682959d997ef71117e03f8355faffdcd3cf428707`
- bridge_document_name: `gtkb-por-step-16-d-orphan-test-rationalization`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-por-step-16-d-orphan-test-rationalization-003.md`
- operative_file: `bridge/gtkb-por-step-16-d-orphan-test-rationalization-003.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation, content:MemBase |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | path:applications/**, path:.claude/rules/project-root-boundary.md, path:.claude/rules/file-bridge-protocol.md, content:applications/ |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:candidate, content:deferred, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal, content:bridge proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/**, path:.claude/rules/file-bridge-protocol.md, path:.claude/rules/codex-review-gate.md |
```

Result: `preflight_passed: true`, `missing_required_specs: []`, `missing_advisory_specs: []`.

## Clause Applicability

Command: `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-por-step-16-d-orphan-test-rationalization`

```text
## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-por-step-16-d-orphan-test-rationalization`
- Operative file: `bridge\gtkb-por-step-16-d-orphan-test-rationalization-003.md`
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
```

Result: exit 0; 5/5 `must_apply` clauses with evidence found; 0 blocking gaps.
