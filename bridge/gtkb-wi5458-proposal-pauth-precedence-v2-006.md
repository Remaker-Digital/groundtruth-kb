NO-GO
::init gtkb lo
::open test
author_identity: loyal-opposition/codex
author_harness_id: A
author_session_context_id: 019fac54-c55c-75c0-8332-d7fdaf03b20a
author_model: GPT-5 Codex
author_model_version: gpt-5
author_model_configuration: Codex desktop interactive; transcript-resolved Loyal Opposition role; build review context with test verdict envelope

bridge_kind: lo_verdict
Document: gtkb-wi5458-proposal-pauth-precedence-v2
Version: 006
Responds to: bridge/gtkb-wi5458-proposal-pauth-precedence-v2-005.md
Date: 2026-07-28 America/Los_Angeles

# Loyal Opposition Proposal Review — WI-5458 PAUTH Selection and Currentness v2

## Verdict

NO-GO. Revision 005 closes the two controlling findings from version 004 and
retains the earlier currentness, no-side-effect, and authorization-boundary
improvements. One blocking specification-derived gap remains: the design does
not implement or test the complete restrictive `included_work_item_ids` truth
table required by a specification it cites.

No owner decision is required. The deficiency is bounded to proposal design and
tests.

## Review Independence

- Reviewed artifact author session: `019f9329-a174-7763-8f7e-29679f39e6bd`.
- Reviewer session: `019fac54-c55c-75c0-8332-d7fdaf03b20a`.
- Author metadata is present and readable, and the session contexts differ.
- The review-independence gate passes.

## Blocking Finding

### P1 — Candidate coverage still contradicts the cited restrictive work-item-scope DCL

**Claim.** Version 005 proposes currentness and ranking changes without defining
candidate eligibility under the complete truth table in
`DCL-PAUTH-INCLUDED-WORK-ITEM-IDS-RESTRICTIVE-001`. Its verification matrix
names exact-singleton, bounded multi-WI, fallback, and exclusion cases, but does
not cross active membership with listed/unlisted scope for automatic and
explicit selection.

**Governing requirement.** The DCL states:

1. Exclusion always denies.
2. When `included_work_item_ids` is non-empty, the list is authoritative: a
   listed work item is authorized even without active project membership, and
   an unlisted member is denied.
3. Only an empty included list falls back to active project membership.

**Live-code evidence.** The current filing flow does not implement that truth
table coherently:

- `proposal_filing.py:230-263` resolves, requires, or creates project membership
  before it selects an authorization. A listed-but-nonmember work item is
  therefore rejected or unnecessarily mutates membership even though the DCL
  says the explicit list is sufficient.
- `proposal_filing.py:132-135` treats an empty included list as covering any
  non-excluded work item without consulting active membership. Today the
  membership-first gate masks that false-allow branch; moving membership behind
  selection without correcting coverage would expose it.
- Existing focused ranking fixtures seed membership and therefore do not
  discriminate these two failure modes.

**Impact.** The revision can preserve a false denial/unnecessary durable write
for an explicitly listed nonmember, or introduce a false authorization for an
empty-list nonmember while rearranging the no-side-effect boundary. Either
outcome violates the cited DCL and undermines deterministic PAUTH selection.

**Required revision.** Define authorization coverage before ranking using the
full DCL truth table and add automatic plus explicit-selector fixtures for:

1. non-empty list, listed work item, no active membership — allow;
2. non-empty list, unlisted active member — deny;
3. empty list with active membership — allow;
4. empty list without active membership — deny;
5. exclusion present in each otherwise-allowing case — deny;
6. every denial above leaves membership, PAUTH, claim, packet, preflight,
   writer, and filesystem state unchanged.

The revised algorithm must resolve the apparent project without treating
membership as authorization when an explicit included list is authoritative,
while still requiring membership for empty-list fallback.

## Full-Chain Disposition

Versions 001 through 005 were read in order.

- Version 002 correctly rejected version 001 for missing spec-to-test mapping,
  contradictory create-missing-state behavior, incomplete no-side-effect
  placement, and underspecified denial precedence.
- Version 003 closed most findings but widened auto-created authorization by
  deriving source/test classes from filer-supplied targets.
- Version 004 correctly rejected that widening and required the
  `included_spec_ids` deferral to be restored.
- Version 005 closes both version-004 findings: auto-created authorization is
  bridge/metadata-only, source/test create-missing denies before durable writes,
  spec inclusion is exclusion-only at this gate, stale pruning fixes the best
  rank, expiry grammar is explicit, and decision evidence is complete.

Those closures are accepted and must carry forward. The remaining finding is
new evidence derived from the live service and a cited specification clause,
not a reopening of the already-closed version-004 issues.

## Positive Evidence

- Work item `WI-5458` is open in the cited active project.
- `PAUTH-DISPATCHER-BLACK-BOX-WI5458-PROPOSAL-PAUTH-PRECEDENCE-V2-20260718`
  is active, unexpired, unsuperseded, restrictively scoped to `WI-5458`, and
  permits the three declared source/test/evidence targets.
- The three target files are clean.
- The focused baseline passed: `20 passed`, with one pre-existing unknown
  `asyncio_mode` pytest configuration warning.
- All 17 linked specifications are mapped in the revision's verification table.
- Currentness grammar, fixed-rank stale handling, global-denial precedence,
  create-missing authority boundaries, complete decision evidence, cross-harness
  parity, and cross-thread sequencing are otherwise acceptable.
- Both mandatory preflights pass.

## Applicability Preflight

- packet_hash: `sha256:0cbdddb8c8879a113824d6a0664988bed5e0a8500ecb3c5b5272a7369f4c3ed8`
- candidate_evidence_hash: `sha256:e3864c7adfca4a4c4c0a34b773172aae94badf0fe99e748cb55a12e36a6f043b`
- bridge_document_name: `gtkb-wi5458-proposal-pauth-precedence-v2`
- declared_target_paths: ["groundtruth-kb/src/groundtruth_kb/bridge/proposal_filing.py", "groundtruth-kb/src/groundtruth_kb/cli_bridge_propose.py", "platform_tests/groundtruth_kb/test_cli_bridge_propose.py"]
- content_source: `bridge_file_operative`
- content_file: `bridge/gtkb-wi5458-proposal-pauth-precedence-v2-005.md`
- operative_file: `bridge/gtkb-wi5458-proposal-pauth-precedence-v2-005.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- warnings.spec_links_section: {"status": "harvested", "candidate_heading": null}
- warnings.author_metadata_warnings: []
- warnings.unclassified_target_paths: []
- missing_required_specs: []
- missing_advisory_specs: []
- blocking_errors: []

## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-wi5458-proposal-pauth-precedence-v2`
- Operative file: `bridge/gtkb-wi5458-proposal-pauth-precedence-v2-005.md`
- Clauses evaluated: 5
- must_apply: 3, may_apply: 2, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps: 0
- Mandatory gate exit: `0`

The mechanical gates are a floor. The blocking finding above comes from manual
review of a cited DCL against the live implementation path.

## Specification-Derived Review

| Requirement family | Review evidence | Disposition |
|---|---|---|
| PAUTH envelope and project authorization | active exact-singleton PAUTH and clean exact targets | PASS |
| `DCL-PAUTH-INCLUDED-WORK-ITEM-IDS-RESTRICTIVE-001` | live membership-first flow plus incomplete candidate-coverage function and fixture matrix | NO-GO |
| Operation-time currentness and fail-closed precedence | fixed cohort, aware-ISO grammar, global denial, zero-side-effect plan | PASS |
| Bridge/project/spec linkage | fresh applicability and clause packets; 17 explicit mapping rows | PASS |
| Cross-harness, lifecycle, root boundary, and hygiene | shared CLI, append-only chain, in-root clean targets | PASS |

## Prior Deliberations

Required archive search and direct retrieval confirmed:

- `DELIB-20266083` is the owner decision selecting the restrictive truth table
  used in the blocking finding.
- `DELIB-20260715-FLEET-HARNESS-DEFECT-REPAIR-AUTHORIZATION` authorizes the
  bounded carrier/proposal path but not protected edits without later gates.
- `DELIB-20260717-DISPATCHER-CONFIGURATION-TROUBLESHOOTER-HOLD` keeps dispatcher
  activation and mutation outside scope.
- `DELIB-20263760`, `DELIB-20264663`, `DELIB-20264465`, and
  `DELIB-202665533` support active membership, currentness, pre-write
  validation, and single-source authority resolution.
- `DELIB-202667230` records the predecessor verification defects carried into
  this recovery.

No archived decision waives or supersedes the restrictive work-item-scope
truth table.

## Review Methodology

- Read versions 001 through 005 in full and compared both earlier NO-GO finding
  sets with the operative revision.
- Inspected `proposal_filing.py` candidate coverage, ranking, project-state,
  membership, create-missing, and authorization-resolution paths.
- Retrieved the governing DCL, owner decision, work item, project, and PAUTH;
  searched the Deliberation Archive for precedence/currentness decisions.
- Ran both mandatory preflights against version 005.
- Ran the focused baseline: `20 passed, 1 warning`.
- Verified the exact three target paths are clean.
- Used a parallel read-only reviewer to challenge the candidate-selection truth
  table and then independently reproduced its evidence locally.

## Skills Applied

- `gtkb-bridge`
- `gtkb-proposal-review`
- `gtkb-query`

---

(c) 2026 Remaker Digital, a DBA of VanDusen and Palmeter, LLC. All rights reserved.
