NO-GO

bridge_kind: review_verdict
Document: gtkb-hygiene-sweep-presence-patterns-slice-1
Version: 002
Author: Loyal Opposition (Codex, harness A)
Date: 2026-06-03 UTC
Reviewer: Loyal Opposition
Responds to: bridge/gtkb-hygiene-sweep-presence-patterns-slice-1-001.md

# Loyal Opposition Review - Hygiene Sweep Presence Patterns

## Verdict

NO-GO.

The proposal's implementation shape is technically plausible: adding a
back-compatible `match_mode` field to the hygiene sweep pattern loader and
emitting one finding per matched file for `presence` patterns fits the current
`groundtruth-kb/src/groundtruth_kb/hygiene/sweep.py` engine. The PAUTH also
covers source, test, and config changes for WI-4249.

It is not ready for implementation because the live applicability preflight
still reports missing advisory specifications, and the proposal does not
reconcile WI-4249's declared dependency on unresolved WI-3469 even though the
proposal includes pytest basetemp detection in scope.

## Applicability Preflight

Command:

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-hygiene-sweep-presence-patterns-slice-1
```

Observed result:

```text
- packet_hash: `sha256:feeb4c290c0c021433495731e68f353271ad40dda25f095a6c0be556f0785f99`
- bridge_document_name: `gtkb-hygiene-sweep-presence-patterns-slice-1`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-hygiene-sweep-presence-patterns-slice-1-001.md`
- operative_file: `bridge/gtkb-hygiene-sweep-presence-patterns-slice-1-001.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- missing_required_specs: []
- missing_advisory_specs: ["ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001", "DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001"]
```

## Clause Applicability

Command:

```text
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-hygiene-sweep-presence-patterns-slice-1
```

Observed result:

```text
- Bridge id: `gtkb-hygiene-sweep-presence-patterns-slice-1`
- Operative file: `bridge\gtkb-hygiene-sweep-presence-patterns-slice-1-001.md`
- Clauses evaluated: 5
- must_apply: 4, may_apply: 1, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: mandatory
```

## Prior Deliberations

Deliberation search command:

```text
groundtruth-kb\.venv\Scripts\gt.exe deliberations search "WI-4249 hygiene sweep presence patterns runtime residue pytest basetemp snapshots" --limit 8
```

Relevant results included:

- `DELIB-2679` - verified `gt hygiene sweep` CLI baseline.
- `DELIB-2675` and `DELIB-2673` - `gtkb-hygiene-sweep` skill NO-GO and VERIFIED context.
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` - deterministic services principle cited by the proposal.

## Positive Confirmations

- `PAUTH-PROJECT-GTKB-DETERMINISTIC-SERVICES-001-HYGIENE-CLUSTER` is active
  and includes WI-4249, with allowed mutation categories `source`,
  `test_addition`, and `config_change`.
- WI-3420 and WI-3421, two of WI-4249's declared dependencies, are resolved
  and cite the verified hygiene sweep CLI/skill bridge threads.
- The proposal keeps MemBase out of `target_paths` and limits this slice to
  report-only detection, which is consistent with the stated WI-4259
  remediation boundary.
- The current `Pattern` dataclass and `scan_file` flow have a clear, narrow
  place to add a back-compatible presence mode.

## Findings

### F1 - P2 - Applicability preflight still reports missing advisory specifications

Observation:

- The proposal's `Specification Links` section starts at
  `bridge/gtkb-hygiene-sweep-presence-patterns-slice-1-001.md:86`.
- The live applicability preflight reports
  `missing_advisory_specs: ["ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001", "DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001"]`.
- `.claude/rules/file-bridge-protocol.md` defines the expected preflight result
  as `preflight_passed: true`, `missing_required_specs: []`, and
  `missing_advisory_specs: []`; non-empty missing spec lists are self-detected
  proposal defects.

Deficiency rationale:

This is a governed artifact/config change proposal touching the hygiene sweep
registry. Missing the artifact-oriented ADR and lifecycle trigger DCL weakens
the proposal's required trace from observed recurring drift, to backlog item,
to artifact mutation, to future remediation flow.

Impact:

Prime Builder would start from a proposal that has already self-identified
incomplete advisory linkage. That increases the chance of a later review or
verification rejection for a defect that is cheap to correct before
implementation.

Recommended remediation:

Add `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` and
`DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` to the proposal's specification links,
then rerun the applicability preflight until both `missing_*_specs` lists are
empty.

### F2 - P1 - The proposal does not reconcile unresolved dependency WI-3469

Observation:

- The live backlog row for WI-4249 declares
  `depends_on_work_items: ["WI-3420", "WI-3421", "WI-3469"]`.
- WI-3469 is still `resolution_status: open`, `stage: backlogged`, and
  describes reclaiming `.pytest-tmp/` from ACL contamination by
  parallel-session Python processes.
- The proposal scopes pytest basetemp ACL contamination detection at
  `bridge/gtkb-hygiene-sweep-presence-patterns-slice-1-001.md:27`,
  `:34`, and `:59`, but it does not mention WI-3469 or explain why WI-4249 can
  proceed before that dependency is resolved.

Deficiency rationale:

The owner asked Loyal Opposition to check future-work dependencies before
choosing or clearing a task. Here, the governing backlog metadata says WI-4249
depends on WI-3469. A proposal may be able to justify detection before
remediation, but that justification must be explicit because WI-3469 is not a
generic sibling; it is the same pytest basetemp ACL contamination class that
this proposal plans to detect.

Impact:

Prime Builder could implement pytest basetemp detection while the declared
underlying dependency remains unresolved or incorrectly modeled. That creates
ordering ambiguity for follow-on verification: a later session may be unable to
tell whether WI-4249 was supposed to wait for WI-3469, unblock WI-3469, or
replace part of WI-3469.

Recommended remediation:

Revise the proposal to do one of the following:

1. Complete or otherwise resolve WI-3469 first, then refile WI-4249.
2. Correct the WI-4249 dependency metadata if WI-3469 is not truly a
   prerequisite.
3. Explicitly justify why detection can precede the unresolved WI-3469
   remediation/workflow item, with owner or PAUTH evidence and a clear
   verification boundary.

## Decision

NO-GO. Revise the proposal to clear the missing advisory-spec preflight defects
and reconcile the unresolved WI-3469 dependency before implementation begins.

## Commands Executed

```text
python .claude/skills/bridge/helpers/show_thread_bridge.py gtkb-hygiene-sweep-presence-patterns-slice-1 --format json --preview-lines 260
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-hygiene-sweep-presence-patterns-slice-1
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-hygiene-sweep-presence-patterns-slice-1
groundtruth-kb\.venv\Scripts\gt.exe deliberations search "WI-4249 hygiene sweep presence patterns runtime residue pytest basetemp snapshots" --limit 8
groundtruth-kb\.venv\Scripts\gt.exe backlog show WI-4249 --json
groundtruth-kb\.venv\Scripts\gt.exe backlog show WI-3420 --json
groundtruth-kb\.venv\Scripts\gt.exe backlog show WI-3421 --json
groundtruth-kb\.venv\Scripts\gt.exe backlog show WI-3469 --json
groundtruth-kb\.venv\Scripts\gt.exe projects authorizations PROJECT-GTKB-DETERMINISTIC-SERVICES-001 --json
rg -n "Pattern|match_mode|content_patterns|def scan_file|def run_sweep" groundtruth-kb/src/groundtruth_kb/hygiene/sweep.py
Select-String -Path bridge\gtkb-hygiene-sweep-presence-patterns-slice-1-001.md -Pattern "Specification Links|pytest basetemp|WI-3469|target_paths|Acceptance Criteria"
```

## Owner Action Required

None.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
