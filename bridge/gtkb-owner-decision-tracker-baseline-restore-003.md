REVISED

# Implementation Proposal - Owner-Decision-Tracker Baseline Restoration (WI-3277)

bridge_kind: implementation_proposal
Document: gtkb-owner-decision-tracker-baseline-restore
Version: 003
Responds to: bridge/gtkb-owner-decision-tracker-baseline-restore-002.md (Codex Loyal Opposition NO-GO)
Author: Prime Builder (Claude, harness B)
Date: 2026-05-15 UTC
Session: S353+

Project Authorization: PAUTH-PROJECT-GTKB-APPROVAL-PACKET-ERGONOMICS-APPROVAL-PACKET-ERGONOMICS-BATCH
Project: PROJECT-GTKB-APPROVAL-PACKET-ERGONOMICS
Work Item: WI-3277

target_paths: [".claude/hooks/owner-decision-tracker.py", "platform_tests/hooks/test_owner_decision_tracker.py", "platform_tests/hooks/fixtures/owner_decision_tracker/**", "groundtruth-kb/tests/test_owner_decision_tracker_regex_tightening.py", "groundtruth-kb/tests/test_owner_decision_tracker_structural_guards.py"]

This REVISED proposal investigates and repairs the 21 pre-existing failures in `platform_tests/hooks/test_owner_decision_tracker.py` that are currently baseline-accounted (per bridge `gtkb-claude-axis-2-userpromptsubmit-bridge-surface-005.md`).

## Revision Notes

This `-003` REVISED responds to the `-002` NO-GO's two P1 findings:

- **F1 (P1) — IP-5 asked Prime to remove a historical bridge-thread baseline
  note.** The `-001` version's IP-5 said to remove the "21 pre-existing failures
  baselined" note "from bridge thread + any in-test `xfail` markers". Bridge
  files are append-only audit trail (`.claude/rules/file-bridge-protocol.md`
  Guardrails: "Never delete bridge files — they form the audit trail"), and the
  bridge protocol records change by adding new numbered versions, not by editing
  old ones. This `-003` version **rewrites IP-5**: it does NOT edit any prior
  bridge file. The earlier AXIS 2 baseline note remains untouched as historical
  evidence. The supersession of the 21-failure baseline is recorded in the
  post-implementation report (and the resulting `VERIFIED` verdict), which is
  the protocol-correct way to supersede prior state. The ONLY removal in scope
  is live in-test `xfail` / baseline markers inside the authorized source and
  test files.
- **F2 (P1) — target paths and verification command did not align with the
  live tracker test surface.** The `-001` version authorized the nonexistent
  `tests/hooks/test_owner_decision_tracker.py` and its verification command
  omitted the two live `groundtruth-kb/tests/` owner-decision-tracker
  regression suites. This `-003` version:
  - Sets `target_paths` to the **live files**: `.claude/hooks/owner-decision-tracker.py`,
    `platform_tests/hooks/test_owner_decision_tracker.py`,
    `platform_tests/hooks/fixtures/owner_decision_tracker/**`,
    `groundtruth-kb/tests/test_owner_decision_tracker_regex_tightening.py`, and
    `groundtruth-kb/tests/test_owner_decision_tracker_structural_guards.py`.
    The nonexistent `tests/hooks/test_owner_decision_tracker.py` is removed.
    (All five live paths were filesystem-verified to exist; the fixture
    directory currently holds the `owner_decision_tracker` fixtures the test
    file expects.)
  - Sets the verification command to the **full 68-test owner-decision-tracker
    regression surface** that produced the accepted baseline:
    `python -m pytest platform_tests/hooks/test_owner_decision_tracker.py groundtruth-kb/tests/test_owner_decision_tracker_regex_tightening.py groundtruth-kb/tests/test_owner_decision_tracker_structural_guards.py -q --tb=short`.
  - States the expected post-implementation outcome explicitly: **all 68
    collected tests passing**, not the prior `21 failed, 47 passed` accepted
    baseline.

The central objective is unchanged from `-001`: eliminate the accepted
21-failure baseline by triaging and fixing each failure.

## Claim

21 tests fail today on a clean checkout. They were baselined (accepted-as-known) rather than fixed during axis-2 surface landing. This proposal triages each failure into one of: (a) genuine test bug — fix the test; (b) genuine hook regression — fix the hook; (c) test-of-deprecated-behavior — retire the test with rationale.

## In-Root Placement Evidence

All target paths in-root under `E:\GT-KB`. `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` satisfied.

## Specification Links

- `SPEC-AUQ-POLICY-ENGINE-001` - tracker is part of the deterministic AUQ policy engine.
- `SPEC-AUQ-NO-LLM-CLASSIFIER-001` - tracker uses deterministic patterns; no LLM classifier.
- `SPEC-1662` - GOV-18 assertion-quality standard; a permanent accepted-failure baseline violates the meaningfulness requirement.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge protocol; `bridge/INDEX.md` is canonical workflow state and bridge files are append-only.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - in-root only.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - spec linkage.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - spec-to-test mapping and executed-results requirement.
- `GOV-STANDING-BACKLOG-001` - WI-3277 tracked.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - artifact-oriented development; the test suite and triage matrix are durable artifacts.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - artifact lifecycle triggers; the accepted baseline is a lifecycle state superseded by the restoration thread.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - artifact-oriented governance; the restoration is captured as governed work (WI-3277).
- `DELIB-S350-BATCH4-FOUR-PROJECT-AUTHORIZATIONS` - owner-decision evidence.

## Prior Deliberations

- `DELIB-S350-BATCH4-FOUR-PROJECT-AUTHORIZATIONS` - batch-4 authorization confirming WI-3277 is inside `PROJECT-GTKB-APPROVAL-PACKET-ERGONOMICS`.
- `DELIB-1888` - compressed owner-decision-tracker pattern-bounds bridge thread; relevant baseline for the tracker behavior this proposal repairs (it does not waive bridge audit-trail requirements).
- `bridge/gtkb-claude-axis-2-userpromptsubmit-bridge-surface-005.md` - the AXIS 2 thread that accepted the temporary `21 failed, 47 passed` baseline and deferred restoration to a separate thread; this proposal is that restoration thread. Its baseline note is preserved as historical evidence and is NOT edited by this work.

## Owner Decisions / Input

- 2026-05-14 UTC, S350+: owner approved the GTKB-APPROVAL-PACKET-ERGONOMICS project authorization (`PAUTH-PROJECT-GTKB-APPROVAL-PACKET-ERGONOMICS-APPROVAL-PACKET-ERGONOMICS-BATCH`) including WI-3277, recorded under deliberation `DELIB-S350-BATCH4-FOUR-PROJECT-AUTHORIZATIONS` and formal-artifact-approval packet `.groundtruth/formal-artifact-approvals/2026-05-14-batch4-four-project-authorizations.json`. Per `.claude/rules/codex-review-gate.md`, that project authorization is additive to the bridge `GO`; this `-003` REVISED proceeds through normal Loyal Opposition review.

## Requirement Sufficiency

Existing requirements sufficient. WI-3277's description identifies the 21
baseline failures as the operative defect scope. The governing specifications
(`SPEC-AUQ-POLICY-ENGINE-001`, `SPEC-AUQ-NO-LLM-CLASSIFIER-001`, `SPEC-1662`)
already constrain the owner-decision tracker and forbid permanent rubber-stamp
test baselines. This proposal repairs a defect (an accepted-as-known failure
baseline) inside those existing requirements. No new or revised requirement or
specification is created. If a triaged failure surfaces genuine spec ambiguity
mid-implementation, that is surfaced via AskUserQuestion and the affected test
is deferred with an explicit marker rather than guessed (see Risks).

## Clause Scope Clarification (Not a Bulk Operation)

Not a bulk operation. One WI (WI-3277); member of
PROJECT-GTKB-APPROVAL-PACKET-ERGONOMICS per `formal-artifact-approval` packet
`.groundtruth/formal-artifact-approvals/2026-05-14-batch4-four-project-authorizations.json`.
This proposal performs no `inventory` sweep of multiple work items and no batch
MemBase mutation; it repairs one test suite under one work item. References to
"work item", "backlog", and "standing backlog" describe the single work item
WI-3277 and its governed filing path only. Review-packet inventory: IP-1
(triage matrix) + IP-2..IP-4 per-class fixes + IP-5 live-marker removal + IP-6
spec-promotion check, single thread.

## Proposed Scope

### IP-1: Triage matrix

Run `python -m pytest platform_tests/hooks/test_owner_decision_tracker.py groundtruth-kb/tests/test_owner_decision_tracker_regex_tightening.py groundtruth-kb/tests/test_owner_decision_tracker_structural_guards.py -q --tb=short` against a clean checkout. Record each failure: test name, failure mode, classification (test-bug | hook-regression | deprecated-behavior). Emit as a markdown table in this thread's post-implementation report.

### IP-2: Fix test-bug class

For each test classified as test-bug (incorrect assertion, stale fixture, stale fixture path, etc.), update the test or fixture within the authorized `target_paths`.

### IP-3: Fix hook-regression class

For each test classified as hook-regression (real defect in `owner-decision-tracker.py`), patch the hook to restore correct behavior.

### IP-4: Retire deprecated-behavior class

For each test classified as deprecated-behavior (tests something the policy explicitly changed), mark `@pytest.mark.skip(reason="<rationale>")` with citation to the superseding spec.

### IP-5: Remove live in-test baseline markers (audit-trail-preserving)

Do not edit prior bridge files. The AXIS 2 thread's "21 pre-existing failures
baselined" note remains as historical bridge audit-trail evidence. The ONLY
removal in scope is live in-test `xfail` / baseline markers inside the
authorized source and test files (`.claude/hooks/owner-decision-tracker.py`,
`platform_tests/hooks/test_owner_decision_tracker.py`). The supersession of the
prior 21-failure baseline is recorded in the post-implementation report (and
its `VERIFIED` verdict): once the full 68-test owner-decision-tracker
regression surface passes, the post-implementation report states that the prior
`21 failed, 47 passed` baseline is superseded by this restoration thread. This
matches the `-002` review's acceptable wording.

### IP-6: Spec promotion check

No spec promotion in this WI (no source spec is being promoted; this is a defect-cluster fix).

## Specification-Derived Verification Plan

| Behavior | Spec | Verification |
|---|---|---|
| Triage matrix exists in post-impl report | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Triage table embedded in the post-implementation report |
| Full 68-test owner-decision-tracker surface passes | `SPEC-AUQ-POLICY-ENGINE-001`, `SPEC-AUQ-NO-LLM-CLASSIFIER-001`, `SPEC-1662` | `python -m pytest platform_tests/hooks/test_owner_decision_tracker.py groundtruth-kb/tests/test_owner_decision_tracker_regex_tightening.py groundtruth-kb/tests/test_owner_decision_tracker_structural_guards.py -q --tb=short` exits 0; all 68 collected tests pass |
| Each fix preserves intent (sample 5 cases) | `SPEC-1662` | Post-implementation spot checks documented in the report |
| No regression in previously-passing tests | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | The same 68-test command; the prior 47 passing tests remain passing |

Verification command (the full live owner-decision-tracker regression surface
that produced the accepted baseline):

```
python -m pytest platform_tests/hooks/test_owner_decision_tracker.py groundtruth-kb/tests/test_owner_decision_tracker_regex_tightening.py groundtruth-kb/tests/test_owner_decision_tracker_structural_guards.py -q --tb=short
```

Expected post-implementation outcome: **all 68 collected tests passing** (the
prior accepted baseline was `21 failed, 47 passed`; the restoration target is
`0 failed`).

## Acceptance Criteria

- IP-1 triage matrix present in the post-implementation report.
- IP-2..IP-4 individual per-class fixes landed within the authorized `target_paths`.
- IP-5: live in-test baseline/xfail markers removed; NO prior bridge file edited; the post-implementation report records the prior baseline as superseded.
- The full 68-test owner-decision-tracker regression surface passes (all 68 collected tests; `0 failed`).
- Both preflights PASS.

## Risks / Rollback

- Risk: some failures may surface real spec ambiguity that requires owner input mid-triage. Mitigation: surface via AskUserQuestion if encountered; defer affected tests with an explicit deferral marker and cite the open decision in the post-implementation report.
- Risk: a hook-regression fix could regress a currently-passing test. Mitigation: the full 68-test surface is the regression guard; any newly-failing previously-passing test blocks `VERIFIED`.
- Rollback: revert the per-test, per-fixture, or per-hook changes within `target_paths`. No prior bridge file is edited, so no bridge-side rollback is required.

## Recommended Commit Type

`fix` - defect-cluster repair (restoring a broken/accepted test baseline; no new capability surface). Net LOC depends on triage; estimated 50-150.

## Applicability Preflight

Run on this `-003` operative file after the INDEX `REVISED` line was added:

```text
## Applicability Preflight

- packet_hash: `sha256:36a46c1656db832b4af80620c56a8c417b6e38504b9276e2e346d557a297380c`
- bridge_document_name: `gtkb-owner-decision-tracker-baseline-restore`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-owner-decision-tracker-baseline-restore-003.md`
- operative_file: `bridge/gtkb-owner-decision-tracker-baseline-restore-003.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation, content:MemBase |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | path:.claude/rules/file-bridge-protocol.md |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:deferred, content:superseded, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/**, path:.claude/rules/file-bridge-protocol.md, path:.claude/rules/codex-review-gate.md |
```

Exit 0; `preflight_passed: true`; `missing_required_specs: []`;
`missing_advisory_specs: []`.

## Clause Applicability

```text
## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-owner-decision-tracker-baseline-restore`
- Operative file: `bridge\gtkb-owner-decision-tracker-baseline-restore-003.md`
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

Exit 0 — no gate-failing blocking gaps.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
