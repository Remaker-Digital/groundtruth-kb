NEW
::init gtkb pb
::open build

author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 345fab55-33fc-40c1-933b-d2413de27158
author_model: claude-opus-5
author_model_version: claude-opus-5
author_model_configuration: Claude Code interactive; resolved role prime-builder via ::init gtkb pb

bridge_kind: implementation_report
Document: gtkb-wi5154-superseded-sot-leakage
Version: 005
Date: 2026-08-07 UTC
Responds to: bridge/gtkb-wi5154-superseded-sot-leakage-004.md
Implements: bridge/gtkb-wi5154-superseded-sot-leakage-003.md (GO at -004)

Project Authorization: PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE
Work Item: WI-5154

target_paths: ["scripts/check_superseded_sot_leakage.py", "platform_tests/scripts/test_check_superseded_sot_leakage.py"]
implementation_scope: source_and_test
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
dispatcher_or_tafe_mutation_in_scope: false

**No KB mutation.** No MemBase row written; `groundtruth.db` was read only.
**No approval-evidence work.** No formal-artifact-approval packet created.
**No dispatcher or TAFE mutation.**
**No commit created.** Finalization remains the Loyal Opposition atomic step.

# Implementation Report - WI-5154 lifecycle-aware superseded-SOT leakage scanner

## Summary

Both declared targets are implemented and green. The four outer assertions
required by `DCL-SUPERSEDED-SOT-LEAKAGE-001` (`SOT-LEAK-A1` .. `SOT-LEAK-A4`)
now execute and pass under the canonical invocation, reversing the intentional
pre-implementation baseline failure described in the GO'd proposal.

| Target | State | Size |
|---|---|---|
| `scripts/check_superseded_sot_leakage.py` | added (untracked) | 467 lines |
| `platform_tests/scripts/test_check_superseded_sot_leakage.py` | added (untracked) | 271 lines |

`git status --short` over the two declared paths reports exactly these two
additions and nothing else. No other file in the worktree was touched by this
implementation.

## What Was Built

The evaluator answers one question deterministically: does any **active** GT-KB
surface cite a formal record whose current MemBase status is `retired` or
`superseded`, in a way that could direct current behavior?

- **Supersession index** is derived from live MemBase rather than a new config
  file: `db.list_specs()` filtered to `status in {retired, superseded}`. This
  keeps the scanner inside the two declared target paths - no registry file was
  added - and makes the index self-updating as records retire. Live count at
  implementation time: 1,338 superseded records.
- **Detection** extracts formal-record-shaped tokens per line
  (`RETIRE-SPEC|GOV|DCL|ADR|SPEC|PB|REQ`-prefixed) and set-intersects against
  the index, so cost is O(lines) rather than O(lines x 1,338 patterns).
- **Lifecycle classification** (`SOT-LEAK-A2`) marks `bridge/`,
  `deliberations/`, `archive/`, `.gtkb-state/`, and any `cleanup-evidence`
  path as `non-operative` history. History is scanned and classified but never
  raised as critical, which is what keeps a genuine `P0` from drowning in
  thousands of append-only false positives.
- **Guarded KEEP** (`SOT-LEAK-A3`) recognizes two ways a retired id may
  legitimately remain on an active surface: it *is* a retirement-registry
  sentinel (`RETIRE-SPEC-*`), or the citing line demonstrably enforces absence.
  Both require current enforcement evidence and carry
  `no-active-authority-effect`. A bare mention with no enforcement language is
  **not** KEEP - it is `STRIP`/`P0`, and a dedicated test pins that boundary.
- **Deduplication** (`SOT-LEAK-A4`) keys findings on `(path, subject_id)`, so
  repeated occurrences of one subject in one file resolve to a single finding
  and cannot inflate count or severity.
- **Fail-closed** (`SOT-LEAK-A1`): an unresolvable provider yields
  `UNASSESSED`, a provider resolving empty yields `PARTIAL`; neither can return
  `PASS`, and both set `gate_blocked=True`.

Every finding carries the full DCL finding contract: stable id, canonical
artifact identity, exact location, active-surface class, lifecycle and
authority classification, subject version and hash, currentness evidence,
severity, affected gate, `STRIP`/`KEEP`/`QUARANTINE` disposition, deterministic
remediation, and recovery route.

## Specification Links

Carried forward unchanged from the GO'd proposal at `-003`.

- `DCL-SUPERSEDED-SOT-LEAKAGE-001` - canonical implementation authority
  (evaluator id, canonical invocation, four outer assertions, finding contract,
  disposition semantics, severity/gate effects, failure behavior).
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `GOV-STANDING-BACKLOG-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`

## Spec-to-Test Mapping

| Spec clause | Test | Result |
|---|---|---|
| `SOT-LEAK-A1` current formal artifacts + active-surface classes + currentness evidence | `test_a1_scans_active_surface_classes_with_currentness_evidence` | PASS |
| `SOT-LEAK-A1` missing provider cannot PASS (empty surface set) | `test_a1_missing_provider_never_passes` | PASS |
| `SOT-LEAK-A1` unresolvable MemBase provider -> UNASSESSED | `test_a1_missing_formal_record_provider_is_unassessed` | PASS |
| `SOT-LEAK-A2` lifecycle classification of all history classes | `test_a2_lifecycle_classification` (6 parametrized cases) | PASS |
| `SOT-LEAK-A2` history raises no critical false positive | `test_a2_historical_fixture_raises_no_critical_finding` | PASS |
| `SOT-LEAK-A3` retired-registry sentinel is KEEP | `test_a3_retired_registry_sentinel_is_keep` | PASS |
| `SOT-LEAK-A3` active guard reference is KEEP with enforcement evidence | `test_a3_active_guard_reference_is_keep_with_enforcement_evidence` | PASS |
| `SOT-LEAK-A3` KEEP requires enforcement, not mere mention | `test_a3_keep_requires_enforcement_not_mere_mention` | PASS |
| `SOT-LEAK-A4` stale active -> blocking P0 + deterministic remediation | `test_a4_stale_active_reference_is_blocking_p0_with_remediation` | PASS |
| `SOT-LEAK-A4` duplicate paths deduplicate to one finding | `test_a4_duplicate_occurrences_deduplicate_to_one_finding` | PASS |
| DCL finding contract - all required fields populated | `test_a4_finding_contract_fields_present` | PASS |
| `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001` determinism | `test_scan_is_deterministic_across_runs` | PASS |
| `gate-block` surfaces as a non-zero exit code | `test_main_exit_code_blocks_on_stale_active` | PASS |

18 test cases total (13 functions; `test_a2_lifecycle_classification` contributes 6 parametrized cases).

## Commands Executed

```
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_check_superseded_sot_leakage.py -q --tb=short
  -> 18 passed, 1 warning in 0.46s   (re-run after formatting: 18 passed in 0.29s)

gt assert --spec DCL-SUPERSEDED-SOT-LEAKAGE-001
  -> Total specs: 1 | With assertions: 1 | PASSED: 1 | FAILED: 0
     PARTIAL: 0 | UNASSESSED: 0 | Aggregate result: PASS
     [DCL-SUPERSEDED-SOT-LEAKAGE-001] ... (4 assertions)

groundtruth-kb/.venv/Scripts/python.exe -m ruff check <both files>
  -> All checks passed!

groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check <both files>
  -> 2 files already formatted

groundtruth-kb/.venv/Scripts/python.exe scripts/check_superseded_sot_leakage.py
  -> evaluator=superseded-sot-leakage result=FAIL gate_blocked=True
     all three providers resolved=True; findings=68 P0=68
```

Note on the two ruff gates: `ruff format --check` **failed on first run** while
`ruff check` passed, which is exactly the separate-gate condition
`.claude/rules/file-bridge-protocol.md` warns about. `ruff format` was applied
to `scripts/check_superseded_sot_leakage.py` and both gates were re-run clean,
and the full test suite plus the canonical assertion invocation were re-run
after formatting to confirm no behavioral drift.

## Live-Tree Scan Result (reported, not remediated)

The live run returns `FAIL` / `gate_blocked=True` with **68 deduplicated P0
findings**. This is the evaluator working as specified, not an implementation
defect: the DCL's Authorization Boundary states it "does not authorize scanner
implementation, cleanup, quarantine, retirement, protected-file mutation..." -
so remediation is out of scope for this thread and no finding was acted upon.

Three findings are independently corroborated as genuine stale active authority:

- `.claude/rules/operating-role.md:166` -> `GOV-SESSION-ROLE-AUTHORITY-001`
- `.claude/rules/prime-builder-role.md:105` -> `GOV-SESSION-ROLE-AUTHORITY-001`
- `.claude/rules/canonical-terminology.md:909` -> `DCL-SESSION-ENVELOPE-DURABILITY-001`

`GOV-SESSION-ROLE-AUTHORITY-001` is confirmed retired by an independent source:
`bridge/gtkb-wi5933-slice-b-resolver-fail-closed-007.md` states
"`GOV-SESSION-ROLE-AUTHORITY-001` is deliberately absent: verified retired
(v6)." Two live rule files still cite it as operative authority.

The remaining findings concentrate in skill documentation citing short-form ids
(`ADR-001`, `ADR-002`, `DCL-002`, `SPEC-1789`, `SPEC-1803`) that are retired in
MemBase. Whether those are true leaks or illustrative examples is a triage
question for a separate remediation thread; the evaluator classifies them
conservatively as `STRIP`/`P0` because no enforcement-shaped language guards
them. Reviewers should treat the 68-count as a first-run census requiring
triage, not as 68 confirmed defects.

## Acceptance Criteria Check

| # | Criterion | Result |
|---|---|---|
| 1 | Only the two declared target paths change | PASS - `git status` shows exactly two additions |
| 2 | `SOT-LEAK-A1..A4` execute and pass under canonical invocation | PASS - aggregate PASS, 4 assertions |
| 3 | TEST-11323 coverage passes and maps to the assertions | PASS - 18 cases, mapping table above |
| 4 | Deterministic and rerunnable | PASS - `test_scan_is_deterministic_across_runs` |
| 5 | Guarded KEEP semantics | PASS - three A3 tests incl. the negative boundary |
| 6 | Deduplicated severity | PASS - `test_a4_duplicate_occurrences_deduplicate_to_one_finding` |
| 7 | Deterministic remediation + gate blocking | PASS - A4 tests + non-zero exit |
| 8 | Fails closed on genuine leaks | PASS - live run returns FAIL / gate_blocked |
| 9 | No KB / dispatcher / TAFE mutation, no commit | PASS |

## Prior Deliberations

- `DELIB-20260710-GTKB-MODERNIZATION-SUPERSEDED-SOT-LEAKAGE-DCL-APPROVAL` -
  owner decision approving the DCL and its evaluator/assertion contract.
- `DELIB-20260710-GTKB-MODERNIZATION-GATE-1-FORMAL-LANGUAGE-DRAFT` - the
  formal-language / Gate 1 framing of current formal-artifact leakage scanning.
- `DCL-SUPERSEDED-SOT-LEAKAGE-001` v1 - the governing implementation authority.
- `bridge/gtkb-wi5154-superseded-sot-leakage-002.md` - the prior NO-GO whose
  Finding 1 (placeholder citations) was cleared by `-003`; Finding 2 confirmed
  the design needed no redesign, and none was made.
- `bridge/gtkb-wi5933-slice-b-resolver-fail-closed-007.md` - independent
  corroboration that `GOV-SESSION-ROLE-AUTHORITY-001` is retired, cited above.

## Owner Decisions / Input

No new owner decision was required. Implementation proceeded under the active
project-scope authorization
`PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE-20260715-PROJECT-SCOPE`
(list-free; allows `source` and `test` mutation), the independent `GO` at
`-004`, a matching work-intent claim held by this session, and a successful
implementation-start authorization packet whose operation-time evaluation
returned `allowed: true` with both targets classified (`source`, `test`).

## Bridge Chain Discipline

This report is filed as
`bridge/gtkb-wi5154-superseded-sot-leakage-005.md`, the next numbered file in
this thread. The numbered bridge files under `bridge/` are canonical and
append-only: no prior version is deleted or rewritten, and the `-004` `GO` this
report responds to is preserved intact.

## Root Boundary Compliance

Both added files are in-root platform paths under `E:/GT-KB`, and this bridge
file resides under `E:/GT-KB/bridge/`. No `applications/` path is touched and no
artifact is written outside the project root.

## Recommended Commit Type

`feat:` - **deviating from the `-003` proposal header, which recorded
`perf`.** The change adds a new 467-line evaluator module plus its 271-line
acceptance-test module; nothing pre-existing is made faster, and no prior
behavior is repaired. Per the Conventional Commits discipline in
`.claude/rules/file-bridge-protocol.md`, `feat:` is the type that matches the
diff stat (two net-new modules, a new capability surface). The `perf` label in
the proposal header appears to be a clerical error and is flagged here rather
than carried forward silently, since commit-history tooling keys off this field.

## Request

Request independent Loyal Opposition verification (`VERIFIED` / `NO-GO`). Both
targets are untracked additions; finalization - staging and the local commit -
remains the Loyal Opposition atomic step per the Mandatory VERIFIED
Commit-Finalization Gate.

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

---

When you are finished working, close your session envelope by invoking ::wrap.
