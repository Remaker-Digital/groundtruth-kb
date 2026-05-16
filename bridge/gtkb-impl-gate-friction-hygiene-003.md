REVISED

# Implementation Proposal - Implementation Gate Friction Hygiene (WI-3310)

bridge_kind: implementation_proposal
Document: gtkb-impl-gate-friction-hygiene
Version: 003
Author: Prime Builder (Claude, harness B)
Date: 2026-05-15 UTC
Session: S353+

Project Authorization: PAUTH-PROJECT-GTKB-APPROVAL-PACKET-ERGONOMICS-APPROVAL-PACKET-ERGONOMICS-BATCH
Project: PROJECT-GTKB-APPROVAL-PACKET-ERGONOMICS
Work Item: WI-3310

target_paths: ["scripts/implementation_start_gate.py", "platform_tests/scripts/test_implementation_start_gate.py"]

This REVISED proposal addresses a narrowed cluster of friction-hygiene improvements in `scripts/implementation_start_gate.py`: null-sink redirect allowlist completeness, block-reason clarity, and a `--diagnostic` self-check mode. `-003` revises `-001` after the `-002` NO-GO.

## Revision Notes

The `-002` NO-GO raised two P1 findings. Each is addressed below.

- F1 (P1 — proposal duplicates an unresolved WI-3310 NO-GO thread without acknowledgment): the `-002` NO-GO is correct that an older bridge thread, `gtkb-implementation-gate-friction-hygiene`, is at latest `NO-GO` (`-018`) and shares the `WI-3310` work-item ID. `-003` now explicitly acknowledges that thread and **picks a definite path: path (b) — this thread is a narrowed-scope successor**. The new `## Relationship To gtkb-implementation-gate-friction-hygiene` section states exactly what this thread supersedes and, critically, what it does **not** supersede (the old thread's unresolved IP-D 32-test verification obligation remains the old thread's to close — this thread does not absorb, resolve, or wave it). `## Prior Deliberations` now cites the old thread and its `-018` NO-GO.
- F2 (P1 — verification command targets a non-existent test path and omits the live canonical test surface): the verification command is corrected to `python -m pytest platform_tests/scripts/test_implementation_start_gate.py`. The non-existent `tests/scripts/test_implementation_start_gate.py` path is removed from `target_paths`. The live canonical implementation-start-gate test file (`platform_tests/scripts/test_implementation_start_gate.py`, recorded in `config/agent-control/system-interface-map.toml`) is now the sole test target. No new `tests/scripts/` mirror is created.

No technical-scope change beyond removing the non-existent test path: the three friction-hygiene improvements (IP-1 null-sink allowlist, IP-2 block-reason clarity, IP-3 `--diagnostic` mode) are unchanged from `-001`.

## Relationship To gtkb-implementation-gate-friction-hygiene

There are two bridge threads that share the `WI-3310` work-item ID. This section disambiguates them and states the supersession relationship precisely (per `-002` NO-GO F1 path (b)).

**The older thread — `gtkb-implementation-gate-friction-hygiene`:** a broad implementation-start-gate hardening effort (IP-A mutating-command detection, IP-B null-sink redirect handling, IP-C state-aware authorization chain-walk, IP-D a 32-test regression matrix, IP-E a tracking work_items row). Its IP-A / IP-B / IP-C source work landed and `52` tests pass. It is at latest `NO-GO` (`bridge/gtkb-implementation-gate-friction-hygiene-018.md`) because its approved IP-D scope carried forward `32` regression tests while the post-implementation report substantiated `19`. The `-018` NO-GO requires Prime to (1) land the remaining IP-D tests to reach `32`, (2) obtain a revised GO narrowing IP-D to `19`, or (3) cite an explicit owner waiver for the `32`-to-`19` reduction.

**This thread — `gtkb-impl-gate-friction-hygiene`:** a smaller, later, distinct set of three friction-hygiene improvements to the *same source file* (`scripts/implementation_start_gate.py`): extend the null-sink redirect allowlist with additional Windows/PowerShell sink forms (`2>NUL`, `>NUL`, `2>$null`, `>$null`, `&>/dev/null`); improve the block-reason message; add a `--diagnostic` self-check CLI mode.

**What this thread supersedes:** going forward, `gtkb-impl-gate-friction-hygiene` is the **active friction-hygiene thread for `scripts/implementation_start_gate.py`**. New incremental friction-hygiene work on that file routes here, not through a re-opened `gtkb-implementation-gate-friction-hygiene` thread. Specifically, the further null-sink allowlist extension in IP-1 below is the canonical place for null-sink redirect-form additions beyond what the old thread's IP-B already landed.

**What this thread does NOT supersede:** this thread does **not** absorb, resolve, satisfy, narrow, or waive the old thread's unresolved IP-D 32-test verification obligation. The old `gtkb-implementation-gate-friction-hygiene` thread remains independently actionable: its `-018` NO-GO stands, and closing it still requires one of the three `-018`-listed actions performed against that thread (land the remaining IP-D tests, obtain a narrowing GO there, or cite an owner waiver there). Approving this `gtkb-impl-gate-friction-hygiene` thread does not change the old thread's status and must not be read as closing it. The two threads have separate audit trails; this proposal explicitly keeps the old thread's verification gap visible rather than obscuring it.

**Why a separate thread rather than continuing the old one:** the old thread is in its post-implementation verification phase (a NO-GO on an implementation *report*). Folding three new code changes into it would require re-opening an implementation *proposal* inside a thread that is otherwise one step from closure on a different scope, entangling two unrelated verification states. A distinct narrowed-scope successor thread keeps each verification state clean: the old thread closes its IP-D matrix on its own evidence; this thread reviews three small new changes on their own evidence.

**No bypass of the prior decision:** per `.claude/rules/deliberation-protocol.md`, a new proposal that touches a topic with a prior NO-GO must acknowledge the prior NO-GO and explain what is different. This thread does not revisit a *rejected approach* — the old `-018` NO-GO did not reject the three improvements proposed here; it found an unrelated test-count shortfall. The three improvements here are genuinely new scope. This section is that explicit acknowledgement.

## Claim

Three narrowly scoped improvements to `scripts/implementation_start_gate.py`: (1) extend the null-sink redirect strip to handle additional Windows/PowerShell sink variants (`2>NUL`, `>NUL`, `2>$null`, `>$null`, `&>/dev/null`); (2) improve the block-reason message to cite the specific clause and suggest the packet-citation pattern; (3) add a `--diagnostic` CLI mode that prints what would be decided without emitting a block decision.

## In-Root Placement Evidence

All target paths in-root under `E:\GT-KB`. `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` satisfied. No path outside `E:\GT-KB` is created, read as a live dependency, or required.

## Specification Links

- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - the implementation-start gate enforces this protected behavior; the hygiene changes preserve it.
- `GOV-ARTIFACT-APPROVAL-001` - protected-mutation evidence requirement; the gate is one mechanical enforcement surface for it.
- `SPEC-AUQ-POLICY-ENGINE-001` - deterministic policy-engine surface; the gate is part of that family and the `--diagnostic` mode is a deterministic self-check of it.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge protocol authority governing this proposal as a bridge artifact.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - in-root placement; all target paths are in-root.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - cross-cutting; this proposal must cite every relevant governing specification.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - cross-cutting; the verification plan maps every linked spec to a test.
- `GOV-STANDING-BACKLOG-001` - WI-3310 is a tracked standing-backlog work item.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - durable artifact-graph model; the WI, this bridge thread, and the linked specs form the artifact graph.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - artifact lifecycle trigger discipline; the WI triggers this proposal and its tests.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - artifact-oriented governance baseline; this work is captured as a governed WI with a bridge artifact and spec-derived tests.
- `DELIB-S350-BATCH4-FOUR-PROJECT-AUTHORIZATIONS` - owner-decision evidence for the project authorization covering WI-3310.

## Prior Deliberations

- `DELIB-S350-BATCH4-FOUR-PROJECT-AUTHORIZATIONS` - batch-4 project authorization covering WI-3310 under `PROJECT-GTKB-APPROVAL-PACKET-ERGONOMICS`.
- `gtkb-implementation-gate-friction-hygiene` bridge thread - the older WI-3310 implementation-start-gate hardening thread. Its latest status is `NO-GO` at `bridge/gtkb-implementation-gate-friction-hygiene-018.md`; the `-018` verdict found the approved IP-D scope (`32` regression tests) substantiated at only `19`. This `gtkb-impl-gate-friction-hygiene` thread is a narrowed-scope successor for *new* friction-hygiene work on `scripts/implementation_start_gate.py` and explicitly does not resolve the old thread's IP-D obligation (see `## Relationship To gtkb-implementation-gate-friction-hygiene`).
- `bridge/gtkb-implementation-gate-friction-hygiene-005.md` - the old thread's REVISED-2 that defined IP-D as the 32-test matrix; cited here so the supersession boundary is anchored to the exact prior artifact.
- `bridge/gtkb-implementation-gate-friction-hygiene-018.md` - the old thread's latest NO-GO; cited so this proposal demonstrably acknowledges the active prior rejection per `.claude/rules/deliberation-protocol.md`.

The three improvements proposed here were not the subject of any prior NO-GO; no rejected approach is being revisited. The old thread's `-018` NO-GO concerns an unrelated IP-D test-count shortfall and remains the old thread's to close.

## Owner Decisions / Input

This proposal depends on owner approval and is authorized by:

- 2026-05-14 UTC, S350+: owner approved the `GTKB-APPROVAL-PACKET-ERGONOMICS` project authorization (`DELIB-S350-BATCH4-FOUR-PROJECT-AUTHORIZATIONS`), which includes the work item WI-3310. This implementation operationalizes WI-3310's friction-hygiene scope within that authorized project scope.
- No new owner AskUserQuestion decision is required for the `-003` revision. The revision (a) corrects a non-existent test path and (b) adds an explicit acknowledgement of the older `gtkb-implementation-gate-friction-hygiene` thread; neither changes the authorized scope. The decision of how to close the *old* thread's IP-D gap is the old thread's concern and is left to that thread's owner/Prime path; this proposal does not request an owner decision on it.

## Requirement Sufficiency

Existing requirements sufficient. WI-3310's description specifies the friction-hygiene scope, and the implementation-start gate's governing specs (`PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`, `GOV-ARTIFACT-APPROVAL-001`, `SPEC-AUQ-POLICY-ENGINE-001`) already define the behavior the gate must preserve. No new or revised requirement or specification is created by this work.

## Clause Scope Clarification (Not a Bulk Operation)

This proposal is a single-work-item, single-file change. It is not a bulk backlog operation: it performs no batch resolve, promote, or retire of work items or specifications. WI-3310 is a member of `PROJECT-GTKB-APPROVAL-PACKET-ERGONOMICS` per the `formal-artifact-approval` packet `.groundtruth/formal-artifact-approvals/2026-05-14-batch4-four-project-authorizations.json`. References to "work item", "backlog", and "standing backlog" describe only this single WI and its governed filing path. The review-packet inventory is IP-1 + IP-2 + IP-3 in this single thread.

## Bridge INDEX Maintenance

`bridge/INDEX.md` is the canonical bridge workflow state. This proposal adds a `REVISED` line to the existing `Document: gtkb-impl-gate-friction-hygiene` entry, preserving the prior `NO-GO` and `NEW` lines (append-only audit trail). This proposal does not edit, reorder, or remove any other `Document:` entry — in particular, it does not modify the separate `Document: gtkb-implementation-gate-friction-hygiene` entry, whose `-018` NO-GO status is left intact.

## Proposed Scope

### IP-1: Extend null-sink redirect allowlist

In `scripts/implementation_start_gate.py`, ensure the null-sink redirect strip recognizes all of: `2>/dev/null`, `>/dev/null`, `2>NUL`, `>NUL`, `2>$null`, `>$null`, `&>/dev/null`. Add explicit test fixtures for each new form and matching false-positive negation fixtures (real-file redirects of the same FD prefixes must still be detected, not stripped). This is incremental to the null-sink work the old thread's IP-B already landed; this thread is the canonical place for further null-sink redirect-form additions per the supersession boundary above.

### IP-2: Block-reason clarity

When the gate emits a block reason, format it as:

```
BLOCKED (GTKB-IMPLEMENTATION-START-GATE): <clause-id>
Reason: <root cause>
Suggested fix: <action>
```

Include the specific protected-prefix or target classification that matched (e.g., `scripts/` or `<unknown-mutating-target>`). Suggest acquiring an authorization packet via `python scripts/implementation_authorization.py begin --bridge-id <id>`.

### IP-3: --diagnostic flag

Add a CLI invocation mode: `python scripts/implementation_start_gate.py --diagnostic` reads the stdin payload, runs the gate logic, and prints what would be decided plus why — without emitting a block decision. This is a deterministic self-check surface for proposal authors.

## Specification-Derived Verification Plan

Each linked specification maps to at least one test. All tests live in the `target_paths` test file `platform_tests/scripts/test_implementation_start_gate.py`.

| Behavior / spec clause | Test | Covers |
|---|---|---|
| `2>NUL` and `>NUL` recognized as null-sink (ALLOW) | `test_null_sink_nul_forms_allowed` | PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001, SPEC-AUQ-POLICY-ENGINE-001 |
| `2>$null` and `>$null` recognized as null-sink (ALLOW) | `test_null_sink_dollar_null_allowed` | PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001 |
| `&>/dev/null` recognized as null-sink (ALLOW) | `test_null_sink_amp_dev_null_allowed` | PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001 |
| Real-file redirects of the same FD prefixes still detected (false-positive negation) | `test_real_file_redirect_still_blocked` | GOV-ARTIFACT-APPROVAL-001, PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001 |
| Block reason includes the clause id and a suggested fix | `test_block_reason_includes_clause_and_suggestion` | GOV-ARTIFACT-APPROVAL-001, GOV-FILE-BRIDGE-AUTHORITY-001 |
| `--diagnostic` prints a decision without emitting a block decision | `test_diagnostic_mode_no_emit` | SPEC-AUQ-POLICY-ENGINE-001 |
| `--diagnostic` decision matches enforce-mode decision for the same payload | `test_diagnostic_matches_enforce` | SPEC-AUQ-POLICY-ENGINE-001, DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 |

Verification command:

```
python -m pytest platform_tests/scripts/test_implementation_start_gate.py -q --tb=short
python -m ruff check scripts/implementation_start_gate.py platform_tests/scripts/test_implementation_start_gate.py
python -m ruff format --check scripts/implementation_start_gate.py platform_tests/scripts/test_implementation_start_gate.py
```

`platform_tests/scripts/test_implementation_start_gate.py` is the live canonical implementation-start-gate test file (recorded as the verification method in `config/agent-control/system-interface-map.toml`); it currently passes (`36 passed` per the `-002` NO-GO's own positive confirmation). The new tests above are added to that file. DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 is satisfied: every linked specification maps to at least one executed test.

## Acceptance Criteria

- IP-1, IP-2, IP-3 landed in `scripts/implementation_start_gate.py`.
- All tests in `platform_tests/scripts/test_implementation_start_gate.py` pass (existing `36` plus the new tests above); `ruff check` and `ruff format --check` clean for the touched files.
- The block-reason message includes the clause id and a suggested fix.
- `--diagnostic` mode prints a decision without emitting a block decision and agrees with enforce mode for the same payload.
- Both mandatory preflights pass for this proposal.
- No file outside `target_paths` is modified; in particular the old `gtkb-implementation-gate-friction-hygiene` thread's files and INDEX status are untouched.

## Risks / Rollback

- Risk: the null-sink allowlist over-broadens and masks a real redirect. Mitigation: each new ALLOW fixture is paired with a false-positive negation fixture so real-file redirects of the same FD prefix are still detected.
- Risk: the `--diagnostic` mode diverges from enforce-mode logic over time. Mitigation: `test_diagnostic_matches_enforce` pins them to the same decision path.
- Risk: confusion between this thread and the older `gtkb-implementation-gate-friction-hygiene` thread. Mitigation: the `## Relationship To gtkb-implementation-gate-friction-hygiene` section states the supersession boundary explicitly and keeps the old thread's IP-D gap visible.
- Rollback: revert each IP independently (three separate function / regex / CLI changes), then drop the new tests. No durable state is touched.

## Recommended Commit Type

`fix` - friction-hygiene repairs plus a small self-check CLI surface on an existing gate; no new governed capability. ~40 LOC plus tests.

## Pre-Filing Preflight

Both mandatory pre-filing preflights were run on this proposal content; the observed output is embedded in the `## Applicability Preflight` and `## Clause Applicability` sections below.

## Applicability Preflight

```
## Applicability Preflight

- packet_hash: `sha256:473857da0bfa6eb386ed0bf98a503013fb4135af36a7ce18ea7966deb40e191b`
- bridge_document_name: `gtkb-impl-gate-friction-hygiene`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-impl-gate-friction-hygiene-003.md`
- operative_file: `bridge/gtkb-impl-gate-friction-hygiene-003.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:blocked, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |
```

Result: `preflight_passed: true`, `missing_required_specs: []`, `missing_advisory_specs: []`.

## Clause Applicability

```
## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-impl-gate-friction-hygiene`
- Operative file: `bridge\gtkb-impl-gate-friction-hygiene-003.md`
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

Result: exit 0; must_apply 5/5 with evidence; blocking gaps: 0.
