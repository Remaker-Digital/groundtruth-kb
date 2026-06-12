NEW

bridge_kind: governance_advisory
Document: gtkb-tafe-spec-promotion
Version: 001
Responds-To: bridge/gtkb-typed-artifact-flow-engine-advisory-004.md

author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 3bc0229b-441d-46ca-ade0-e5bf06608e2a
author_model: claude-fable-5
author_model_version: 5
author_model_configuration: default

target_paths: ["groundtruth.db"]

# TAFE Candidate Specification Promotion Proposal

## Proposal Claim

Prime Builder proposes promoting the eight TAFE candidate specifications from
`candidate` to `specified` status, content unchanged. The constrained GO at
`bridge/gtkb-typed-artifact-flow-engine-advisory-004.md` explicitly excluded
formal spec promotion from its authorization and required it to pass the
normal bridge gates independently — this proposal is that independent gate
passage.

This artifact is filed under `bridge/` with a `NEW` entry inserted at the
top of its `bridge/INDEX.md` document entry; no prior bridge version is
deleted or rewritten, and live `bridge/INDEX.md` remains the canonical
workflow state throughout (GOV-FILE-BRIDGE-AUTHORITY-001).

This filing performs no mutation. On `GO`, Prime Builder creates one
formal-artifact approval packet per specification (citing the owner-decision
deliberation below), promotes each spec via a new MemBase version with
`status='specified'` and description byte-identical to the approved
candidate text, and files a post-implementation report with read-back
evidence for verification.

## Bridge Kind Classification

`bridge_kind: governance_advisory` — this is a governance/lifecycle proposal
for formal artifact promotion, not a source-code implementation proposal. The
only target surface is MemBase (`groundtruth.db`) specification rows. It
creates no source, test, config, hook, release, deployment, dispatcher, or
bridge-rule change. Precedent: `bridge/gtkb-tafe-backlog-reconciliation-001.md`
used the same classification for a bounded MemBase-only mutation plan and
received GO at `-002`.

## Specification Links

- `SPEC-TYPED-ARTIFACT-FLOW-ENGINE-UMBRELLA` (promotion target)
- `SPEC-TAFE-R1` (promotion target)
- `SPEC-TAFE-R2` (promotion target)
- `SPEC-TAFE-R3` (promotion target)
- `SPEC-TAFE-R4` (promotion target)
- `SPEC-TAFE-R5` (promotion target)
- `SPEC-TAFE-R6` (promotion target)
- `SPEC-TAFE-R7` (promotion target)
- `GOV-ARTIFACT-APPROVAL-001` (per-artifact approval packets required)
- `GOV-SPEC-CAPTURE-TRANSPARENCY-001` (full-text owner presentation — satisfied, see Owner Decisions / Input)
- `GOV-SPEC-CREATION-STANDING-AUTHORIZATION-001` (spec capture authority)
- `GOV-STANDING-BACKLOG-001` (backlog/work-item linkage discipline)
- `GOV-FILE-BRIDGE-AUTHORITY-001` (bridge protocol authority)
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` (spec linkage)
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` (verification mapping below)
- `DCL-BRIDGE-KIND-TAXONOMY-ENUM-001` (kind classification)
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` (candidate → specified lifecycle transition)
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` (artifact-oriented interpretation)
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` (artifact-oriented development)

## Owner Decisions / Input

- `DELIB-TAFE-SPEC-PROMOTION-APPROVAL-20260612` (AskUserQuestion, 2026-06-12
  ~21:45Z): the full text of all eight candidate specifications was presented
  to the owner in conversation; the owner selected "Approve all 8" over
  "Approve with edits" and "Defer promotion". The deliberation records the
  approved spec IDs, the agreed promotion path (this bridge proposal → GO →
  per-artifact packets → promotion), and the agreement that assertions and
  linked tests are added at Phase 0 work-item approval per GOV-12/GOV-13
  rather than during promotion.
- `DELIB-BRIDGE-DISPATCH-OVERHAUL-D3-20260612`: owner decision establishing
  the spec capture structure (one umbrella + one child per R1–R7) that these
  eight candidates implement.

## Prior Deliberations

- `bridge/gtkb-typed-artifact-flow-engine-advisory-003.md` (corrected
  advisory) and `-004.md` (constrained GO: "Future implementation proposals
  must still pass the normal bridge, spec-linkage, owner-authorization, and
  VERIFIED cutover gates"; formal spec promotion explicitly not authorized by
  that GO).
- `bridge/gtkb-tafe-backlog-reconciliation-001.md`/`-002.md`/`-003.md`: the
  reconciliation precondition ("before any implementation work begins") has
  been executed; post-implementation report at `-003` is awaiting LO
  verification. Spec promotion is a lifecycle action, not implementation
  work, and does not depend on that verification outcome.
- `DELIB-BRIDGE-DISPATCH-OVERHAUL-SPEC-CAPTURE-STRUCTURE-20260612` (umbrella
  plus child candidate specs).
- `DELIB-TAFE-BACKLOG-RECONCILIATION-PAUTH-20260612` (bounded reconciliation
  PAUTH; that PAUTH explicitly forbids `formal_spec_promotion`, which is why
  this separate proposal exists).

## Requirement Sufficiency

Existing requirements sufficient. The eight candidate specifications already
exist in MemBase with owner-approved content
(`DELIB-TAFE-SPEC-PROMOTION-APPROVAL-20260612`); this proposal changes only
their lifecycle status from `candidate` to `specified` and creates no new
requirement content. No source/config/test implementation is requested.

## Proposed Execution Plan (on GO)

1. For each of the eight specs, generate a formal-artifact approval packet at
   `.groundtruth/formal-artifact-approvals/2026-06-12-<spec-id>.json` citing
   `DELIB-TAFE-SPEC-PROMOTION-APPROVAL-20260612`, with `full_content` and
   `full_content_sha256` matching the promoted row.
2. Promote each spec via `KnowledgeDB` append-only versioning: new version
   with `status='specified'`, description byte-identical to the candidate v1
   description, `change_reason` citing this bridge thread and the owner
   deliberation.
3. Read back all eight latest rows and assert: version incremented,
   `status='specified'`, description equality with candidate v1.
4. File the post-implementation report as
   `bridge/gtkb-tafe-spec-promotion-00N.md` with dry-run/apply/read-back
   evidence for exactly eight spec rows.

## Specification-Derived Verification Plan

| Requirement | Verification |
|---|---|
| `GOV-ARTIFACT-APPROVAL-001` (packet per formal mutation) | Eight packet files exist; each `full_content_sha256` matches the promoted row content; packet paths listed in post-impl report |
| `GOV-SPEC-CAPTURE-TRANSPARENCY-001` (owner-visible full text) | DELIB records full-text presentation + AUQ selection; cited in each packet |
| Content-unchanged invariant | Read-back description equality check (candidate v1 vs specified v2) for all eight IDs |
| Append-only versioning (`GOV-08`/MemBase discipline) | v1 candidate rows remain; promotion adds new versions only |
| Bounded scope | Exactly eight spec IDs mutated; no work-item, project, or deliberation mutation in the apply step |

## Out of Scope

- No assertions or testability fields added during promotion (deferred to
  Phase 0 WI approval per GOV-12/GOV-13, recorded in the owner deliberation).
- No work-item approval_state changes, no Phase 0 PAUTH, no implementation
  proposal for WI-4487 — those are separate follow-on gates.
- No TAFE implementation-flow pilot, no bridge-rule cutover, no generated-view
  authority change.

## Recommended Commit Type

`chore:` — MemBase lifecycle bookkeeping (spec status promotion); no source,
test, or configuration change.

## Review Request

Requesting Loyal Opposition review of:

1. Whether the owner-approval evidence (full-text presentation + AUQ +
   deliberation) satisfies the formal promotion gate for all eight specs.
2. Whether the content-unchanged + append-only execution plan is sound.
3. Whether deferring assertions/tests to Phase 0 WI approval is acceptable
   sequencing under GOV-12/GOV-13.
