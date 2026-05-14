# Implementation Proposal - Assertion Signal/Noise Triage (Self-Diagnostic Leak Closure Slice 3)

bridge_kind: implementation_proposal
Document: gtkb-self-diagnostic-leak-closure-slice-3-assertion-triage
Version: 001
Author: Prime Builder (Claude, harness B)
Date: 2026-05-13 UTC
Session: S349
Work Item: new MemBase work item to be created from this proposal's IP-1 SPEC creation; current proposal scope is Slice 3 of the GTKB-SELF-DIAGNOSTIC-LEAK-CLOSURE umbrella
target_paths: ["scripts/assertion_categorize.py", "scripts/assertion_retirement_workflow.py", "platform_tests/scripts/test_assertion_categorize.py", "platform_tests/scripts/test_assertion_retirement_workflow.py", ".claude/hooks/assertion-check.py", "groundtruth.db", ".claude/skills/assertion-triage/SKILL.md", ".codex/skills/assertion-triage/SKILL.md", "config/agent-control/harness-capability-registry.toml", ".codex/skills/MANIFEST.json"]

## Claim

Implement assertion signal/noise categorization that converts the 1,463 currently-failing GT-KB assertions from undifferentiated noise into four owner-actionable categories: genuine_drift, chronic_noise, flaky, healthy. The slice closes LEAK 3 from S349 self-diagnostic investigation, where the wrap-up handoff has been classifying "224/1687 PASS, 1463 FAIL" as "the known broad historical failure profile" - meaning drift detection has been functionally disabled by accumulation.

Categorization is the precondition for owner triage. Today the owner cannot meaningfully act on 1,463 failing assertions because they are an undifferentiated pile. After categorization, expected owner-actionable subsets are: a small handful of genuine_drift entries warranting immediate investigation, a categorized chronic_noise list with retirement-or-accept owner decisions, and a flaky list flagged for repair. The undifferentiated background-noise number shrinks to a defined small set.

This slice does not change which assertions exist, does not modify the assertion-check hook to gate writes on categorization, and does not auto-retire any assertion. Categorization is read-only inference; retirement requires explicit owner AskUserQuestion approval per the AUQ-only enforcement stack.

## Why Now

S349 self-diagnostic investigation cited LEAK 3 with quantitative evidence from `memory/MEMORY.md`: "Broad assertion check still reports 224/1687 PASS and 1463 FAIL, matching the known broad historical failure profile rather than this slice." 86.7% assertion failure rate normalized as background. Per GOV-18 (Assertion Quality: meaningfulness over coverage, no rubber-stamp assertions), this state is exactly the failure mode the principle was designed to prevent.

Today's broad assertion-check output is one undifferentiated number per session wrap. The owner has no way to distinguish a newly-failing assertion (which deserves investigation) from a chronically-failing one (which deserves retirement or explicit accept). Without categorization, every wrap-up either acknowledges the number and moves on (current behavior) or burns owner attention on 1,463 entries (impractical).

The slice is sequenced after Slices 1 and 2 of the GTKB-SELF-DIAGNOSTIC-LEAK-CLOSURE umbrella but per the S349 parallelization directive, files in parallel with them rather than waiting for VERIFIED.

## Specification Links

- GOV-FILE-BRIDGE-AUTHORITY-001 - live `bridge/INDEX.md` remains the authoritative bridge queue; this proposal files governed work before implementation.
- ADR-ISOLATION-APPLICATION-PLACEMENT-001 - all target paths are inside `E:/GT-KB`.
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 - this proposal cites relevant existing governing specs and names new specs to be created at IP-1 before code semantics depend on them.
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 - verification requires tests derived from linked specs.
- GOV-18 ASSERTION-QUALITY - meaningfulness over coverage; the categorization operationalizes this principle.
- GOV-03 TEST-CLARITY - every test must produce unambiguous PASS/FAIL; chronic-noise category surfaces tests that have lost clarity.
- GOV-15 TEST-FIX-GATE - no fixing failed tests without owner approval; categorization is read-only inference, not fixing.
- GOV-ARTIFACT-APPROVAL-001 - SPECs proposed at IP-1 follow the standard formal-artifact-approval-packet workflow.
- GOV-STANDING-BACKLOG-001 - retirement candidates flow to the standing backlog as candidate WIs for owner decision.
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 - categorization output is a durable artifact, not transient session state.
- DCL-CONCEPT-ON-CONTACT-001 - "assertion category", "genuine_drift", "chronic_noise" are new load-bearing concepts; glossary entries added at IP-1.
- DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE - categorization is repetitive plumbing; belongs in services not sessions.

Advisory / cross-cutting:

- `.claude/rules/operating-model.md` §1 - "GT-KB is strongly biased toward durable artifacts, traceability, modular implementation, versioned interfaces, automated checks, and release evidence." Assertion categorization is automated check.
- INSIGHTS-2026-05-10-13-26-GTKB-SELF-MEASUREMENT-SYSTEM - the LO advisory that recommends assertion regression rate as a Quality and Evidence metric (Section "Measurement Portfolio" subsection 3).

## Prior Deliberations

- S349 self-diagnostic investigation (this conversation, 2026-05-13 UTC) - Mike asked Prime to probe agent behavior for leaks/gaps/waste; investigation produced quantitative evidence of LEAK 3 (86.7% assertion failure rate normalized); Mike authorized "File both, sequenced" via AskUserQuestion; Mike then authorized "parallelize this work to the maximum extent possible".
- INSIGHTS-2026-05-10-13-26-GTKB-SELF-MEASUREMENT-SYSTEM (Codex Loyal Opposition advisory, 2026-05-10) - identified assertion regression rate as a Quality and Evidence portfolio metric; this slice operationalizes that recommendation for the existing 1,463-failing pile.
- DELIB-S341-SELF-IMPROVEMENT-STANDING-DIRECTIVE - improvement opportunities flow to MemBase backlog; categorization output produces candidate retirement WIs.
- DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE - repetitive plumbing belongs in services.
- Prior MEMORY.md handoff entries (S347, S348) - both cite "224/1687 PASS and 1463 FAIL, matching the known broad historical failure profile" verbatim, evidencing the normalized-noise pattern.

## Owner Decisions / Input

- 2026-05-13 UTC, S349: owner asked Prime Builder to investigate GT-KB behavior for leaks/gaps/waste; investigation produced quantitative findings on assertion failure normalization.
- 2026-05-13 UTC, S349: owner authorized "File both, sequenced" via AskUserQuestion covering Slice 1 advisory-router + Slice 2 benchmark suite + Slice 3 assertion S/N triage.
- 2026-05-13 UTC, S349: owner authorized "parallelize this work to the maximum extent possible" lifting sequencing constraint.

The AUQ in S349 plus the parallelization directive together constitute owner authorization for this slice. Retirement of any specific chronic-noise assertion still requires a fresh AskUserQuestion at the retirement-workflow step; this slice's authorization covers categorization only.

## Requirement Sufficiency

Existing requirements sufficient.

GOV-18 (assertion quality) and GOV-15 (test fix gate) together authorize categorization work. Categorization is inference over existing `assertion_runs` history; it creates no new product behavior. Two new SPECs are created at IP-1 to formalize the categorization contract and the retirement workflow. Retirement of specific assertions requires owner AUQ per GOV-15 and the AUQ-only enforcement stack; that approval is gathered at execution time, not at this proposal.

## Current Implementation Baseline

- `groundtruth.db` has an `assertion_runs` table recording historical assertion execution with timestamps and pass/fail status.
- `.claude/hooks/assertion-check.py` runs assertions at session start and reports counts.
- Session-wrap procedures (`.claude/skills/kb-session-wrap/SKILL.md`) include assertion reporting as a checklist item.
- No current code computes per-assertion history or categorizes by drift/noise/flaky/healthy.
- No retirement workflow exists; retirement of an assertion currently requires direct MemBase spec modification with owner approval, but the surfacing path is undefined.

## Proposed New Specs

IP-1 creates these MemBase records:

1. SPEC-ASSERTION-CATEGORIZATION-001 - categorization contract:
   - Input: `assertion_runs` history for a single assertion (timestamps + pass/fail).
   - Output: exactly one of `genuine_drift`, `chronic_noise`, `flaky`, `healthy` plus a confidence score and rationale.
   - Predicates:
     - `genuine_drift`: latest run is FAIL, prior 5+ runs were PASS, transition is within configurable window (default 7 days).
     - `chronic_noise`: latest 50+ consecutive runs are all FAIL (default 50, configurable).
     - `flaky`: latest 10 runs include both PASS and FAIL with at least one transition.
     - `healthy`: stable PASS, or stable FAIL for a `specified`-status spec where FAIL is expected.
   - Determinism: same input must produce same category and rationale.
   - Read-only: never modifies the assertion or the spec it belongs to.

2. SPEC-ASSERTION-RETIREMENT-WORKFLOW-001 - retirement workflow:
   - Trigger: `chronic_noise` categorization produces a candidate retirement entry.
   - Surface: candidate retirement entries written to `.gtkb-state/assertion-triage/candidates/<assertion_id>.json` with rationale and historical evidence.
   - Owner decision: each retirement candidate is presented via AskUserQuestion with options retire-with-rationale / accept-as-expected-fail / keep-and-repair.
   - Effect of retire: `db.update_specification()` with `status='retired'` and `change_reason` citing the retirement workflow and AUQ answer.
   - No batch auto-retirement: each chronic-noise assertion requires its own AUQ.

## Proposed Scope

### IP-1: Create SPECs with formal-artifact-approval packets

1. For each of the 2 SPECs above, create `.groundtruth/formal-artifact-approvals/2026-05-13-<SPEC-ID>.json` with required fields.
2. Insert SPECs via `db.insert_specification()`, citing packet path in `change_reason` and S349 AUQ as `presented_to_user` evidence.

### IP-2: Implement categorization script

1. Create `scripts/assertion_categorize.py`:
   - CLI: `python scripts/assertion_categorize.py [--since YYYY-MM-DD] [--output-dir <path>] [--dry-run]`
   - Queries `assertion_runs` history for each currently-failing assertion.
   - Applies the four-category decision logic from SPEC-ASSERTION-CATEGORIZATION-001.
   - Writes per-assertion category JSON to `.gtkb-state/assertion-triage/categories/<assertion_id>.json`.
   - Emits summary markdown listing counts per category and the highest-priority entries.

### IP-3: Implement retirement workflow

1. Create `scripts/assertion_retirement_workflow.py`:
   - CLI: `python scripts/assertion_retirement_workflow.py [--review-candidates|--apply-decision <assertion_id> <retire|accept|keep>]`
   - `--review-candidates` lists current chronic_noise candidates with rationale.
   - `--apply-decision` requires a valid AUQ packet path and applies the owner decision to MemBase.
   - Validates AUQ packet via existing `scripts/validate_formal_artifact_packet.py`.

### IP-4: Wire into session-wrap reporting (advisory only)

1. Update `.claude/hooks/assertion-check.py` to report per-category counts in addition to the existing pass/fail total.
2. Format: "Assertions: PASS=224 FAIL=1463 (categorized: genuine_drift=N, chronic_noise=N, flaky=N, healthy=N, uncategorized=N)" with the breakdown computed from the latest categorization run.
3. The hook does NOT block any operation on categorization output; this is advisory display only.

### IP-5: Add assertion-triage skill

1. Create `.claude/skills/assertion-triage/SKILL.md` describing how Prime should run categorization and surface retirement candidates.
2. Add capability registry entry; run `scripts/generate_codex_skill_adapters.py --update-registry`.
3. Verify parity with `python scripts/check_harness_parity.py --all --markdown`.

## Tests

`platform_tests/scripts/test_assertion_categorize.py`:

1. `test_genuine_drift_detected` - fixture: 7 PASS runs then 1 FAIL run within 7 days; expects `genuine_drift`.
2. `test_chronic_noise_detected` - fixture: 51 consecutive FAIL runs; expects `chronic_noise`.
3. `test_flaky_detected` - fixture: 10 alternating PASS/FAIL runs; expects `flaky`.
4. `test_healthy_stable_pass` - fixture: 30 consecutive PASS runs; expects `healthy`.
5. `test_healthy_specified_status_expected_fail` - fixture: 30 consecutive FAIL runs for a `status='specified'` spec; expects `healthy` (expected fail for specified-not-implemented).
6. `test_categorization_deterministic` - same input twice produces same output.
7. `test_categorization_handles_insufficient_history` - assertion with <5 runs returns `healthy` with uncategorized=true.
8. `test_categorization_writes_output` - per-assertion JSON written to expected path.

`platform_tests/scripts/test_assertion_retirement_workflow.py`:

1. `test_review_candidates_lists_chronic_noise` - fixture: 3 chronic_noise + 2 healthy; lists only the 3.
2. `test_apply_decision_requires_valid_auq_packet` - missing packet path raises error; invalid packet raises error.
3. `test_apply_decision_retire_updates_spec` - valid packet + retire decision updates spec status to retired.
4. `test_apply_decision_accept_records_acceptance` - accept decision writes acceptance record; spec status unchanged.
5. `test_apply_decision_keep_marks_for_repair` - keep decision flags for repair without retirement.

## Verification Plan

Post-impl report at version -003 (or higher) must include:

1. All 13 tests PASS.
2. Categorization run against live `assertion_runs` history.
3. Live result: counts in each category from the 1,463 currently-failing assertions; expected pattern is most are chronic_noise, a few are flaky, very few are genuine_drift.
4. Sample candidate retirement entries: 3 chronic_noise candidates with their rationale and historical evidence.
5. Updated assertion-check hook output format demonstrated.
6. Specification linkage check.
7. `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-self-diagnostic-leak-closure-slice-3-assertion-triage` returns preflight_passed=true.
8. `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-self-diagnostic-leak-closure-slice-3-assertion-triage` returns no blocking gaps.

## Risks and Rollback

Risks:

- Categorization heuristics are simple thresholds (5, 50, 10). Edge cases may produce surprising categories. Mitigation: each category carries a confidence score and rationale; uncategorized fallback for ambiguous cases.
- Owner AUQ overhead: if hundreds of chronic_noise candidates appear, presenting each via separate AUQ is impractical. Mitigation: the retirement workflow supports batch-acceptance via a single AUQ that lists multiple candidates; deterministic-services principle applies.
- Misidentified `genuine_drift`: a flaky assertion mid-cycle could appear as drift. Mitigation: drift category requires 5+ prior PASS runs, which flaky assertions usually don't have.

Rollback:

- Retire SPECs created at IP-1.
- Delete categorization scripts and skill.
- Revert assertion-check hook update.
- No data mutation in canonical state; `.gtkb-state/assertion-triage/` outputs are non-authoritative.

## Sequenced Follow-Ons

Per S349 parallelization directive, Slice 3 no longer waits for Slices 1 or 2 VERIFIED. Filing in parallel.

Independent follow-ons after Slice 3 VERIFIED:

- Slice 3a: Run categorization against live assertion_runs and surface the categorized lists to owner for triage AUQ.
- Slice 3b: Implement batch-AUQ pattern for retiring chronic_noise lists.
- Slice 3c: Doctor check that flags ungated genuine_drift entries as P0 (after baseline data confirms genuine_drift is a small set).

## Recommended Commit Type

`feat:` - new functionality (two scripts, hook update, skill, capability registry entry, two SPECs).

## Bridge-Compliance Self-Check

This proposal includes:

- non-empty `## Specification Links` section with cited governing specs (10 blocking + 2 advisory).
- non-empty `## Prior Deliberations` section with cited DELIB-IDs and INSIGHTS files.
- non-empty `## Owner Decisions / Input` section enumerating S349 AUQ + parallelization directive.
- `target_paths` metadata in header block (10 paths, all in-root).
- `## Requirement Sufficiency` subsection with explicit state.
- `## Recommended Commit Type` per governance hygiene bundle.
