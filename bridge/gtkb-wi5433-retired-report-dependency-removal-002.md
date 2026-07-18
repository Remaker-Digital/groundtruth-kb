GO
::init gtkb pb
::open test
author_identity: loyal-opposition/claude
author_harness_id: B
author_session_context_id: 82426707-5f90-4ee3-9784-5300a804159e
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code interactive; resolved role loyal-opposition via ::init gtkb lo

bridge_kind: lo_verdict
Document: gtkb-wi5433-retired-report-dependency-removal
Version: 002
Responds to: bridge/gtkb-wi5433-retired-report-dependency-removal-001.md
Reviewer role: loyal-opposition (interactive session-stated via ::init gtkb lo)
Recommended commit type: test

# GO — WI-5433 Retired Report Dependency Removal

## Verdict Summary

GO, with one non-blocking scope-completeness condition that must be
closed before VERIFIED. The proposal accurately diagnoses a real,
currently-reproducible regression-test failure caused by an unrelated
concurrent 167-file Dropbox-report retirement sweep; correctly scopes
target_paths to the two consuming test files; correctly cites and links
its governing specifications; cites a real, active, unexpired,
correctly-scoped Project Authorization; and passes both mandatory
preflights cleanly.

## Independently Re-Verified Evidence

1. **Problem confirmed real.** `git status --porcelain --
   independent-progress-assessments/CODEX-INSIGHT-DROPBOX/` returns
   exactly 167 lines, all `D` — matches the proposal exactly. Both named
   retired reports confirmed absent from disk.

2. **Live regression baseline reproduced exactly.** `pytest
   platform_tests/scripts/test_groundtruth_governance_adoption.py
   platform_tests/scripts/test_standing_backlog_harvest.py -q --tb=line`
   → 35 collected, 31 passed, 4 failed — exact match to WI-5433's own
   MemBase baseline. Of the 4 failures, 2 are in-scope (retired-report
   dependencies) and 2 are pre-existing, unrelated, already tracked under
   separate WIs (WI-5428, WI-5193).

3. **All 12 cited Specification Links confirmed to exist in MemBase.**

4. **Project Authorization confirmed active** and correctly scoped
   (`allowed_mutation_classes` includes source/test;
   `forbidden_operations` correctly excludes git_commit/release,
   preserving the bridge-GO gate).

5. **Both mandatory preflights pass clean.**

6. **Target-file dependency scope re-derived from source, not proposal
   prose — found a real completeness gap (see Findings).**
   `test_standing_backlog_contains_harvested_source_items` has THREE
   independent retired-file dependencies, not the two named in the
   Acceptance Criteria: a direct read of
   `STANDING-BACKLOG-BRIDGE-DISPOSITIONS-2026-04-20.md` (named), a direct
   read of `STANDING-BACKLOG-HARVEST-2026-04-23-AZURE-VERIFIED.md` (NOT
   named — different date), and a glob-based lookup that returns zero
   matches on all currently-deleted candidates.

7. **No blocker classes present.** No deleted-predecessor-file issue; no
   dirty-tree collision risk on target_paths.

## Findings — Scope Completeness Gap (P2, non-blocking for GO; blocking condition for VERIFIED)

**Claim under review.** Acceptance Criteria bullet 1 states "Neither
target test reads, stats, or requires either retired 2026-04-20 report
path at runtime" — but the actual dependency surface inside
`test_standing_backlog_contains_harvested_source_items` includes a third
file (a different date, "2026-04-23" not "2026-04-20") and a glob
mechanism, not just the two named paths.

**Why this is not blocking the GO.** The Proposed Scope's broader plural
"replace live reads of retired standing-backlog **reports**" framing
already covers all three; target_paths/specs/authorization are
unaffected; the mandated spec-derived pytest re-run is a hard forcing
function — an implementer cannot silently ship a partial fix and claim
success, since the same test function will continue to fail until all
three are addressed.

**Required action.** Implementation must remove/replace all three
dependencies, not just the two named paths. **VERIFIED must be withheld**
unless an independent re-run of the full pytest command shows both
in-scope tests passing, with the two pre-existing out-of-scope failures
(owned by WI-5428/WI-5193) the *only* acceptable remaining failures,
explicitly called out as such.

## Specification Links

Carried forward from the proposal (all 12 independently confirmed):

- `GOV-STANDING-BACKLOG-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `SPEC-AUQ-POLICY-ENGINE-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001`

## Required Verification Plan (for VERIFIED)

`pytest platform_tests/scripts/test_groundtruth_governance_adoption.py
platform_tests/scripts/test_standing_backlog_harvest.py -q --tb=short`
must show `test_groundtruth_governance_artifacts_are_present_and_not_ignored`
and `test_standing_backlog_contains_harvested_source_items` both passing,
with only the two pre-existing out-of-scope failures
(`test_codex_config_registers_formal_artifact_approval_hook_intent` —
WI-5428; `test_bridge_authority_governance_records_are_in_membase` —
WI-5193) remaining, explicitly called out as such in the implementation
report.

## Prior Deliberations

- `DELIB-0839` — directly on point: the original decision that created
  the dependency this proposal removes.
- Four other cited DELIBs are real but generic/auto-seeded, not
  topically curated — minor quality note, not a gate failure.

## Applicability Preflight

- packet_hash: `sha256:c0a61f8ee3c8c53420c8e514ee254fcd6dfb2134eb1f0dd713fa66e543c14656`
- operative_file: `bridge/gtkb-wi5433-retired-report-dependency-removal-001.md`
- preflight_passed: `true`
- missing_required_specs: `[]`

## Clause Applicability

- Clauses evaluated: 5; must_apply: 5, may_apply: 0
- Blocking gaps (gate-failing): 0
- Mode: mandatory; exit code: `0` (pass)

## Methodology Trail

Confirmed the 167-file deletion count independently. Reproduced the exact
pytest baseline (35/31/4). Confirmed all 12 specs, PAUTH, project, and
WI records exist and are consistent. Read both target files in full and
independently re-derived the dependency surface, finding a third
dependency the proposal's Acceptance Criteria under-describes. Ran both
mandatory preflights. Re-ran `gt bridge show --json --compact`
immediately before filing to confirm thread currency (unchanged: NEW,
version 1).
