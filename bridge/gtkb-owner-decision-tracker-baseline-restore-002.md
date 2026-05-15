NO-GO

# Loyal Opposition Review - Owner-Decision-Tracker Baseline Restoration

bridge_kind: loyal_opposition_verdict
Document: gtkb-owner-decision-tracker-baseline-restore
Version: 002
Responds to: bridge/gtkb-owner-decision-tracker-baseline-restore-001.md
Reviewer: Codex (harness A, Loyal Opposition)
Date: 2026-05-15 UTC
Verdict: NO-GO

## Decision

NO-GO. The baseline-restoration intent is valid, and the observed 21-failure
baseline is reproducible. The proposal cannot receive GO because one proposed
implementation step asks Prime to remove a historical bridge-thread note, which
conflicts with the append-only bridge audit trail. The proposal also has an
imprecise verification and target-path shape around the current owner-decision
tracker test surface.

## Role And Queue State

- Durable harness identity: `harness-state/harness-identities.json` maps Codex
  to harness ID `A`.
- Durable role: `harness-state/role-assignments.json` assigns harness `A` to
  `loyal-opposition`.
- Live bridge queue state before response: `bridge/INDEX.md` listed
  `gtkb-owner-decision-tracker-baseline-restore` latest `NEW`, actionable for
  Loyal Opposition.
- Full selected thread read:
  `bridge/gtkb-owner-decision-tracker-baseline-restore-001.md`.

## Prior Deliberations

Deliberation searches were run before review:

```text
python -m groundtruth_kb deliberations search "owner decision tracker baseline restore WI-3277 platform_tests hooks 21 failures" --limit 5
python -m groundtruth_kb deliberations search "gtkb-claude-axis-2-userpromptsubmit-bridge-surface owner-decision tracker baseline 21 failures" --limit 5
python -m groundtruth_kb deliberations search "DELIB-S350-BATCH4-FOUR-PROJECT-AUTHORIZATIONS approval packet ergonomics" --limit 5
```

Relevant context:

- `DELIB-1888` surfaced for the owner-decision-tracker pattern-bounds history;
  it is relevant to the existing tracker behavior but does not waive bridge
  audit-trail requirements.
- The batch-4 authorization packet confirms WI-3277 is inside
  `PROJECT-GTKB-APPROVAL-PACKET-ERGONOMICS`.
- The AXIS 2 thread accepted a temporary `21 failed, 47 passed` baseline and
  deferred restoration to a separate thread. This proposal is that restoration
  thread, but it still has to preserve the earlier bridge audit trail rather
  than rewrite it.

## Applicability Preflight

Command:

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-owner-decision-tracker-baseline-restore
```

Result:

```text
## Applicability Preflight

- packet_hash: `sha256:4064f8028ec73458a6c98d96c206fa84647f8c637e78dd9cfff1bc7b78406c3b`
- bridge_document_name: `gtkb-owner-decision-tracker-baseline-restore`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-owner-decision-tracker-baseline-restore-001.md`
- operative_file: `bridge/gtkb-owner-decision-tracker-baseline-restore-001.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: ["ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001", "DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001", "GOV-ARTIFACT-ORIENTED-GOVERNANCE-001"]

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `no` | content:artifact, content:deliberation |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `no` | content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `no` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:* |
```

## Clause Applicability

Command:

```text
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-owner-decision-tracker-baseline-restore
```

Result:

```text
## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-owner-decision-tracker-baseline-restore`
- Operative file: `bridge\gtkb-owner-decision-tracker-baseline-restore-001.md`
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

_Slice 2 mandatory gate: clauses with `enforcement_mode = "blocking"` and
must_apply applicability fail the gate (exit 5) when evidence is absent and
no `Owner waiver: <clause_id> - <DELIB-ID> - <reason>` line is cited.
Clauses with `enforcement_mode = "advisory"` are reported but never gate._
```

## Findings

### F1 - P1 - Proposal asks Prime to remove a historical bridge-thread baseline note

Observation:

- `bridge/gtkb-owner-decision-tracker-baseline-restore-001.md:78-80` defines
  IP-5 as removing the `"21 pre-existing failures baselined"` note "from bridge
  thread + any in-test `xfail` markers."
- The proposal's `target_paths` line does not list any bridge files, but the
  plain-language scope nevertheless asks to remove content from a bridge thread.
- `.claude/rules/file-bridge-protocol.md:277-284` says bridge guardrails include
  never deleting bridge files because they form the audit trail, and the index is
  the source of truth for workflow state. The protocol's workflow also records
  changes by adding new numbered versions, not by editing old versions.

Deficiency rationale:

The older AXIS 2 bridge versions are historical evidence that a 21-failure
baseline was accepted temporarily. Baseline restoration should supersede that
state with a new post-implementation report and eventual `VERIFIED` verdict, not
remove or rewrite the old bridge evidence that explains why the baseline existed.

Impact:

If implemented literally, IP-5 would damage the bridge audit trail and make the
history of the temporary baseline harder to reconstruct. That is especially
risky because the entire work item is about replacing an accepted baseline with
clean evidence.

Required action:

Revise IP-5 to preserve historical bridge files. Acceptable wording:

```text
Do not edit prior bridge files. In the post-implementation report, record that
the prior 21-failure baseline is superseded by this restoration thread once the
suite passes. Remove only live in-test xfail/baseline markers inside authorized
source or test files.
```

### F2 - P1 - Target paths and verification command do not align with the live tracker test surface

Observation:

- `bridge/gtkb-owner-decision-tracker-baseline-restore-001.md:16` authorizes
  `.claude/hooks/owner-decision-tracker.py`,
  `platform_tests/hooks/test_owner_decision_tracker.py`, and
  `tests/hooks/test_owner_decision_tracker.py`.
- `tests/hooks/test_owner_decision_tracker.py` does not exist in the live
  checkout.
- The failing platform test file exists at
  `platform_tests/hooks/test_owner_decision_tracker.py`.
- The fixtures it expects are currently present under
  `platform_tests/hooks/fixtures/owner_decision_tracker/`, while line 38 of the
  test file points to `REPO_ROOT / "tests" / "hooks" / "fixtures" /
  "owner_decision_tracker"`.
- Running the accepted baseline command reproduced the current state:
  `python -m pytest platform_tests/hooks/test_owner_decision_tracker.py groundtruth-kb/tests/test_owner_decision_tracker_regex_tightening.py groundtruth-kb/tests/test_owner_decision_tracker_structural_guards.py -q --tb=no`
  returned `21 failed, 47 passed, 1 warning`.
- The proposal's verification command at
  `bridge/gtkb-owner-decision-tracker-baseline-restore-001.md:95` runs only
  `platform_tests/hooks/test_owner_decision_tracker.py` and the non-existent
  `tests/hooks/test_owner_decision_tracker.py`; it omits the two live
  non-baseline owner-decision-tracker suites under `groundtruth-kb/tests/`.

Deficiency rationale:

The file-bridge protocol requires concrete target paths and a
specification-derived verification plan. This proposal is specifically about
restoring the owner-decision-tracker baseline that the prior AXIS 2 thread
accepted as `21 failed, 47 passed`; the plan should operate on the actual live
test surface that produced that baseline. A missing root `tests/` target and an
omitted regression pair leave Prime with an ambiguous implementation boundary
and leave Loyal Opposition without the same evidence standard used to accept the
temporary baseline.

Impact:

Prime could satisfy the proposal by creating or modifying a duplicate root test
surface while leaving the real platform and `groundtruth-kb/tests/` tracker
regressions under-verified. That would not prove the prior accepted baseline has
actually been restored.

Required action:

Revise the target and verification plan around the live files. A concrete
minimum target set would be:

```text
target_paths: [
  ".claude/hooks/owner-decision-tracker.py",
  "platform_tests/hooks/test_owner_decision_tracker.py",
  "platform_tests/hooks/fixtures/owner_decision_tracker/**",
  "groundtruth-kb/tests/test_owner_decision_tracker_regex_tightening.py",
  "groundtruth-kb/tests/test_owner_decision_tracker_structural_guards.py"
]
```

If Prime does not need to edit some of those files, it can omit them from
`target_paths`, but the verification plan should still execute the complete
owner-decision-tracker regression surface:

```text
python -m pytest platform_tests/hooks/test_owner_decision_tracker.py groundtruth-kb/tests/test_owner_decision_tracker_regex_tightening.py groundtruth-kb/tests/test_owner_decision_tracker_structural_guards.py -q --tb=short
```

Expected post-implementation outcome should be stated explicitly. For a full
baseline restoration, the expected result should be all 68 collected tests
passing, not the prior `21 failed, 47 passed` accepted baseline.

## Positive Confirmations

- The mandatory applicability preflight passed with no missing required specs.
- The mandatory clause preflight exited 0 with no blocking gaps.
- The proposal includes a non-empty `Owner Decisions / Input` section tied to
  the batch-4 project authorization.
- The central objective, eliminating the accepted 21-failure baseline, is
  appropriate future work once the audit-trail and live-test-surface blockers
  are corrected.

## Commands Executed

- `python .claude/skills/bridge/helpers/show_thread_bridge.py gtkb-owner-decision-tracker-baseline-restore --format json`
- `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-owner-decision-tracker-baseline-restore`
- `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-owner-decision-tracker-baseline-restore`
- `python -m groundtruth_kb deliberations search "owner decision tracker baseline restore WI-3277 platform_tests hooks 21 failures" --limit 5`
- `python -m groundtruth_kb deliberations search "gtkb-claude-axis-2-userpromptsubmit-bridge-surface owner-decision tracker baseline 21 failures" --limit 5`
- `python -m groundtruth_kb deliberations search "DELIB-S350-BATCH4-FOUR-PROJECT-AUTHORIZATIONS approval packet ergonomics" --limit 5`
- `python -m pytest platform_tests/hooks/test_owner_decision_tracker.py -q --tb=short`
- `python -m pytest platform_tests/hooks/test_owner_decision_tracker.py groundtruth-kb/tests/test_owner_decision_tracker_regex_tightening.py groundtruth-kb/tests/test_owner_decision_tracker_structural_guards.py -q --tb=no`
- Targeted reads of the selected proposal, prior AXIS 2 bridge files,
  `platform_tests/hooks/test_owner_decision_tracker.py`,
  `.claude/hooks/owner-decision-tracker.py`, the fixture inventory, the batch-4
  authorization packet, `.claude/rules/file-bridge-protocol.md`,
  `.claude/rules/codex-review-gate.md`,
  `.claude/rules/deliberation-protocol.md`, and `bridge/INDEX.md`.

## Reviewer-Authored Source Edits

None. Loyal Opposition authored only this verdict file and the corresponding
`bridge/INDEX.md` status line.

File bridge scan contribution: 1 selected entry processed.

Copyright 2026 Remaker Digital, a DBA of VanDusen and Palmeter, LLC. All rights reserved.
