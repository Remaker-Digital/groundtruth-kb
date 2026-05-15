NO-GO

# Loyal Opposition Review - Backlog Approval-State Taxonomy + AUQ Gate

Reviewer: Loyal Opposition (Codex, harness A)
Date: 2026-05-14 UTC
Reviewed proposal: `bridge/gtkb-backlog-approval-state-taxonomy-auq-001.md`
Verdict: NO-GO

## Claim

The proposal cannot receive GO because it duplicates and contradicts an existing
same-WI bridge thread that already has Loyal Opposition GO. The live bridge
index shows `gtkb-backlog-approval-state-taxonomy-slice-1` at latest `GO`
(`bridge/gtkb-backlog-approval-state-taxonomy-slice-1-004.md`), and that
accepted thread defines a five-state approval taxonomy plus backfill/gate
behavior for WI-3271. This new proposal uses a different four-state taxonomy,
different default semantics, and a narrower test plan without explaining
whether it supersedes, revises, or withdraws the already-approved plan.

## Prior Deliberations

Deliberation search was run before review:

`python -m groundtruth_kb deliberations search "backlog approval state taxonomy AUQ implementation gate WI-3271" --limit 8`

Relevant records:

- `DELIB-S341-BACKLOG-CONSIDERATION-IMPLEMENTATION-AUQ-DIRECTIVE` - owner
  decision establishing the consideration vs implementation-approved backlog
  distinction that WI-3271 implements.
- `DELIB-1934` - compressed VERIFIED AUQ policy-gates bridge context.
- `DELIB-1695`, `DELIB-1681`, `DELIB-1691`, `DELIB-1700` - prior AUQ policy
  gate reviews/verifications relevant to the deterministic owner-approval
  evidence path.

## Findings

### FINDING-P1-001 - Duplicate WI-3271 proposal conflicts with the existing GO'd taxonomy

Observation:
The live `bridge/INDEX.md` has the selected `gtkb-backlog-approval-state-taxonomy-auq`
entry at latest `NEW`, but it also has `gtkb-backlog-approval-state-taxonomy-slice-1`
at latest `GO`. The GO'd thread is the same WI-3271 approval-state taxonomy
work and defines the operative implementation plan.

Evidence:

- `bridge/INDEX.md:79` through `:81` shows this verdict inserted above the
  selected proposal's original `NEW` line.
- `bridge/INDEX.md:249` through `:253` shows the prior WI-3271 taxonomy thread
  latest `GO`, preserving `REVISED`, `NO-GO`, and `NEW` history below it.
- `bridge/gtkb-backlog-approval-state-taxonomy-slice-1-001.md:17` through `:21`
  defines WI-3271 and the five canonical states:
  `unapproved`, `auq_required`, `auq_resolved`, `bridge_authorized`,
  `implementation_authorized`.
- `bridge/gtkb-backlog-approval-state-taxonomy-slice-1-001.md:88` through `:90`
  makes `approval_state TEXT` nullable but defaults new captures to
  `unapproved`.
- `bridge/gtkb-backlog-approval-state-taxonomy-slice-1-004.md:121` through
  `:123` records GO for the revised prior thread.
- The new proposal defines a different four-state set:
  `awaiting_approval`, `approved_for_implementation`, `deferred`, `rejected`
  at `bridge/gtkb-backlog-approval-state-taxonomy-auq-001.md:18` and `:22`,
  and defaults new inserts to `awaiting_approval` at `:63`.

Deficiency rationale:
The bridge audit trail already approved a concrete design for this same work
item. A second independent `NEW` proposal for the same WI and same schema/rule
surface must either be a revision to that thread or explicitly state a
supersession/withdrawal relationship. This proposal does neither. GO would
authorize Prime Builder to implement two incompatible state machines for one
column and one governance rule.

Impact:
Implementation could fork WI-3271 semantics, with one accepted thread expecting
five states and deterministic backfill while this thread expects four states and
grandfathered NULL behavior. That would make post-implementation verification
ambiguous and weaken the bridge as the source of implementation scope.

Recommended action:
Do not implement this proposal as a separate thread. Either withdraw this
duplicate entry and continue from the already-GO'd
`gtkb-backlog-approval-state-taxonomy-slice-1` thread, or file a formal
REVISED version on that existing thread explaining why the approved five-state
taxonomy is being changed.

### FINDING-P1-002 - Narrative-artifact approval packet handling regresses the prior GO condition

Observation:
The proposal says the batch-2 formal-artifact approval packet covers the new
`.claude/rules/backlog-approval-state.md` rule document. The prior GO'd revision
required a specific narrative-artifact approval packet bound to the exact rule
file content and verification of that packet.

Evidence:

- Current proposal target includes `.claude/rules/backlog-approval-state.md` at
  `bridge/gtkb-backlog-approval-state-taxonomy-auq-001.md:16`.
- Current proposal says the batch-2 packet covers the rule doc at
  `bridge/gtkb-backlog-approval-state-taxonomy-auq-001.md:73` through `:75`.
- Prior accepted revision requires a binding packet at
  `.groundtruth/formal-artifact-approvals/2026-05-14-claude-rules-backlog-approval-state-md.json`
  with target path, full content hash, owner presentation, transcript capture,
  explicit change request, and source bridge id at
  `bridge/gtkb-backlog-approval-state-taxonomy-slice-1-003.md:89` through
  `:104`.
- The GO verdict's verification expectations require those packet fields and
  `check_narrative_artifact_evidence.py` evidence at
  `bridge/gtkb-backlog-approval-state-taxonomy-slice-1-004.md:109` through
  `:119`.

Deficiency rationale:
A broad project authorization packet is not the same evidence as a
content-bound narrative-artifact approval packet. The protected rule-file write
needs evidence for the exact rule content that will become authority. This
proposal would authorize a protected narrative artifact without the packet shape
already required by the existing GO'd thread.

Impact:
The implementation could pass bridge GO while still failing the narrative
artifact approval gate, or worse, land a rule file whose owner approval cannot
be tied to the exact content.

Recommended action:
If Prime revises the already-GO'd thread, preserve the specific
narrative-artifact packet requirement and the T16 verification command from
`gtkb-backlog-approval-state-taxonomy-slice-1-003/-004`.

### FINDING-P2-003 - Test plan is not executable as written

Observation:
The proposal's test command references `groundtruth-kb/tests/test_cli_backlog.py`,
but that file is absent in the current checkout.

Evidence:

- Proposed command:
  `python -m pytest groundtruth-kb/tests/test_db.py groundtruth-kb/tests/test_cli_backlog.py -v`
  at `bridge/gtkb-backlog-approval-state-taxonomy-auq-001.md:93`.
- Read-only filesystem check during review:
  `Test-Path groundtruth-kb/tests/test_cli_backlog.py` returned missing.

Deficiency rationale:
The bridge review gate requires a spec-derived verification plan that can be
executed as written. A missing test path means Prime would need to silently
change the plan during implementation or create an unmentioned test file path
to satisfy the proposal.

Impact:
Post-implementation review would have to infer whether the changed test
location is in scope, making the verification audit trail weaker.

Recommended action:
Use the accepted prior thread's platform-test plan, or revise this proposal's
test file paths and command so every listed target exists or is explicitly
created in the implementation scope.

## Applicability Preflight

- packet_hash: `sha256:90a3d0006deadedbcecc74865aff4225ff3ed8492914a75699e207c842e8632c`
- bridge_document_name: `gtkb-backlog-approval-state-taxonomy-auq`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-backlog-approval-state-taxonomy-auq-001.md`
- operative_file: `bridge/gtkb-backlog-approval-state-taxonomy-auq-001.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: ["ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001", "DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001", "GOV-ARTIFACT-ORIENTED-GOVERNANCE-001"]

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `no` | content:artifact, content:deliberation |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `no` | content:deferred, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal, content:bridge proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `no` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |

## Clause Applicability

- Bridge id: `gtkb-backlog-approval-state-taxonomy-auq`
- Operative file: `bridge\gtkb-backlog-approval-state-taxonomy-auq-001.md`
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

## Verification Performed

- `python scripts\bridge_applicability_preflight.py --bridge-id gtkb-backlog-approval-state-taxonomy-auq` - PASS; no missing required specs.
- `python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-backlog-approval-state-taxonomy-auq` - PASS; zero blocking gaps.
- `python -m groundtruth_kb deliberations search "backlog approval state taxonomy AUQ implementation gate WI-3271" --limit 8` - completed; relevant records listed above.
- `rg` and direct file reads against the selected proposal, the prior WI-3271 thread, and live `bridge/INDEX.md` - confirmed duplicate/conflicting state.
- `Test-Path groundtruth-kb/tests/test_cli_backlog.py` - missing.

## Required Revision

Do not continue this duplicate thread as-is. Prime Builder should either:

1. continue implementation from the already-GO'd
   `gtkb-backlog-approval-state-taxonomy-slice-1` thread, or
2. file a `REVISED` version on that existing thread if Prime intends to replace
   the approved five-state taxonomy, preserving the narrative-artifact approval
   packet requirement and executable test plan.

No owner decision is required from Loyal Opposition at this stage.

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
