NO-GO

# Loyal Opposition Review - Proposal-Standards WI-ID Collision Gate

Reviewer: Loyal Opposition (Codex, harness A)
Date: 2026-05-14 UTC
Reviewed proposal: `bridge/gtkb-proposal-standards-wi-id-collision-gate-001.md`
Verdict: NO-GO

## Claim

The work direction is valid, but this proposal cannot receive GO as written.

The mandatory applicability and clause preflights pass with no missing required
specifications and no blocking clause gaps. The proposal nevertheless does not
implement the Slice 3 required outcome as a pre-review hook, and its verification
command targets a nonexistent root `tests/` surface while omitting the listed
`platform_tests/` path.

## Prior Deliberations

Deliberation search was run before review:

```text
$env:PYTHONPATH='E:/GT-KB/groundtruth-kb/src'; python -m groundtruth_kb deliberations search "GTKB-GOV-PROPOSAL-STANDARDS WI ID collision bridge proposal" --limit 8 --json
```

Relevant results:

- `DELIB-0990`, `DELIB-0991`, and `DELIB-0993` - prior Loyal Opposition reviews
  for `gtkb-gov-proposal-standards-slice1`; relevant parent-thread context for
  keeping proposal-standards behavior concrete and mechanically enforceable.
- Current sibling thread evidence:
  `bridge/gtkb-proposal-standards-test-claim-rerun-verifier-002.md` identifies
  the same class of scope-alignment and test-surface problems in Slice 2.

No retrieved deliberation waives the bridge requirement that implementation
proposals map the operative work item to concrete, executable verification.

## Findings

### FINDING-P1-001 - The required pre-review hook is not in implementation scope

Observation:

- The governing work item says Slice 3's required outcome is a "pre-review hook"
  that cross-references `GTKB-ISOLATION-NNN`, `GTKB-DASHBOARD-NNN`, and
  `GTKB-GOV-NNN` mentions against the standing backlog and flags ID collisions
  before review (`memory/work_list.md:1377` through `:1385`).
- The proposal repeats the pre-review hook claim at
  `bridge/gtkb-proposal-standards-wi-id-collision-gate-001.md:18`.
- The authorized `target_paths` list includes only a standalone script and test
  files, not a hook, hook registration, bridge-compliance integration, or
  proposal-standards hook integration
  (`bridge/gtkb-proposal-standards-wi-id-collision-gate-001.md:16`).
- The proposed implementation is a manually invoked CLI with default exit 0 and
  nonzero behavior only under `--strict`
  (`bridge/gtkb-proposal-standards-wi-id-collision-gate-001.md:22`,
  `:61` through `:69`).
- The acceptance criteria require only "collision-check landed" and seven tests
  passing; they do not require a pre-review hook path to execute on proposal
  filing or edit (`bridge/gtkb-proposal-standards-wi-id-collision-gate-001.md:89`
  through `:92`).

Deficiency rationale:

The work item is not asking merely for an optional diagnostic. It is part of the
proposal-standards enforcement family whose stated purpose is to catch proposal
defects mechanically before high-velocity bridge review. A detached CLI can be
useful, but if no hook path invokes it, normal proposal filing can still bypass
the collision check completely.

Impact:

Prime Builder could implement and pass this proposal while the original failure
mode remains open: a bridge proposal can still route work to an already-assigned
ID without any pre-review gate firing.

Recommended action:

Revise the proposal in one of two concrete ways:

1. Implement the pre-review hook integration in this slice, including the hook or
   proposal-standards integration path, target paths, trigger point, bypass or
   advisory behavior, and tests proving the hook runs on proposal write/edit; or
2. Narrow this proposal to a standalone diagnostic CLI, explicitly defer hook
   integration to a named follow-on slice, and update the work-item/acceptance
   language so Slice 3 is not claimed complete until the hook path lands.

### FINDING-P1-002 - The verification command targets a nonexistent root test tree

Observation:

- The proposal authorizes both
  `tests/scripts/test_bridge_proposal_wi_id_collision_check.py` and
  `platform_tests/scripts/test_bridge_proposal_wi_id_collision_check.py`
  (`bridge/gtkb-proposal-standards-wi-id-collision-gate-001.md:16`).
- The live checkout has no root `tests/` directory, while
  `platform_tests/scripts/` exists.
- The only proposed run command executes the nonexistent root test path and does
  not execute the authorized `platform_tests/scripts/...` path
  (`bridge/gtkb-proposal-standards-wi-id-collision-gate-001.md:87`).

Deficiency rationale:

The bridge verification gate requires executable tests derived from the linked
specifications. A command that points at a missing test tree cannot be the
post-implementation verification command, and listing a second test path without
running it leaves the authorized platform-test surface unmapped.

Impact:

Post-implementation verification would either fail immediately because the
stated command cannot collect tests, or it would require Prime Builder to invent
an unstated test location after GO. Both outcomes weaken the audit trail.

Recommended action:

Revise `target_paths` and the verification plan to match the actual test surface.
Use `platform_tests/scripts/test_bridge_proposal_wi_id_collision_check.py` unless
the revision explicitly justifies creating a new root `tests/` tree. The run
command must execute every in-scope test file or explain why a listed target is
not part of verification.

## Applicability Preflight

- packet_hash: `sha256:70d24388df8804862ba899494ba2fc201a92b783e279032141a8f607a80957e1`
- bridge_document_name: `gtkb-proposal-standards-wi-id-collision-gate`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-proposal-standards-wi-id-collision-gate-001.md`
- operative_file: `bridge/gtkb-proposal-standards-wi-id-collision-gate-001.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: ["ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001", "DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001", "GOV-ARTIFACT-ORIENTED-GOVERNANCE-001"]

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `no` | content:artifact, content:deliberation, content:MemBase |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `no` | content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal, content:bridge proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `no` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |

## Clause Applicability

- Bridge id: `gtkb-proposal-standards-wi-id-collision-gate`
- Operative file: `bridge\gtkb-proposal-standards-wi-id-collision-gate-001.md`
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

Slice 2 mandatory gate note: clauses with `enforcement_mode = "blocking"` and
must_apply applicability fail the gate when evidence is absent and no explicit
owner-waiver line is cited. No blocking gaps were reported here.

## Verification Performed

- Read live `bridge/INDEX.md`; selected thread remained latest `NEW`.
- Read full thread with `python .claude/skills/bridge/helpers/show_thread_bridge.py gtkb-proposal-standards-wi-id-collision-gate --format json`.
- Ran `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-proposal-standards-wi-id-collision-gate`.
- Ran `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-proposal-standards-wi-id-collision-gate`.
- Ran Deliberation Archive search listed above.
- Read `memory/work_list.md` Slice 3 required outcome.
- Checked live path state: root `tests/` is absent; `platform_tests/scripts/` is present.

## Required Revision

File `bridge/gtkb-proposal-standards-wi-id-collision-gate-003.md` as `REVISED`
after aligning the implementation scope with a real pre-review hook path or
narrowing the claim to a standalone diagnostic CLI. The revision must also fix
the test target paths and run command so the post-implementation report can be
verified without inventing new scope.

No owner decision is required from Loyal Opposition at this stage.

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
